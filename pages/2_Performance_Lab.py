"""ACPA/MSMDA Performance Lab — prototype de terrain sans données personnelles."""
from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda.ui import LAB, PRIVACY_NOTE, configure_page  # noqa: E402

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "performance_tests.json"
data = json.loads(REGISTRY.read_text(encoding="utf-8"))
tests = data["tests"]

configure_page(LAB)
st.title(LAB.title)
st.caption(LAB.summary + " " + PRIVACY_NOTE)
domain = st.selectbox("Domaine", ["Tous"] + sorted({t["domain"] for t in tests}))
selected = [t for t in tests if (domain == "Tous" or t["domain"] == domain)]
test_id = st.selectbox("Choisir une épreuve", [t["id"] for t in selected], format_func=lambda i: next(t["name"] for t in selected if t["id"] == i)) if selected else None
if test_id:
    t = next(t for t in selected if t["id"] == test_id)
    st.subheader(t["name"])
    st.write("**Mesure :** " + t["measure"] + " (" + t["unit"] + ")")
    st.caption("Protocole : " + t["protocol_note"])
    with st.form("measurement"):
        value = st.number_input("Résultat mesuré (" + t["unit"] + ")", min_value=None if t.get("signed") else 0.0, value=0.0, step=0.1)
        submitted = st.form_submit_button("Enregistrer la mesure", type="primary")
    if submitted:
        if not math.isfinite(value) or (value <= 0 and not t.get("signed")):
            st.error("Saisissez une valeur valide" + ("." if t.get("signed") else " strictement positive."))
        else:
            record = {"test_id":test_id,"test":t["name"],"value":value,"unit":t["unit"]}
            st.session_state["performance_last_record"] = record
    record = st.session_state.get("performance_last_record")
    if record and record["test_id"] == test_id:
        st.success("Mesure prise en compte. Exportez-la pour la conserver.")
        st.metric("Résultat", f'{record["value"]:g} {record["unit"]}')
        if test_id == "cooper":
            distance = record["value"]
            st.metric("Vitesse moyenne sur 12 min", f"{distance / 200:.2f} km/h")
            st.caption("Cette vitesse moyenne n'est pas une VMA mesurée.")
            if distance > 504.9:
                st.metric("VO₂max estimée (formule de Cooper)", f"{(distance - 504.9) / 44.73:.1f} mL/kg/min")
                st.caption("Estimation indirecte ; ne remplace pas une mesure physiologique.")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(record))
        writer.writeheader()
        writer.writerow(record)
        st.download_button("Exporter la mesure (CSV)", output.getvalue().encode("utf-8-sig"), "acpa_mesure.csv", "text/csv")

st.divider()
st.subheader("Visualiser une progression")
st.caption("Mesures successives d'une même épreuve, dans la même unité. L'application ne les sauvegarde pas : elles disparaissent si vous rechargez ou fermez la page ; exportez-les pour les garder.")
with st.form("progression_chart"):
    chart_test = st.selectbox("Épreuve à représenter", [t["id"] for t in tests], format_func=lambda i: next(t["name"] for t in tests if t["id"] == i))
    raw_values = st.text_area("Mesures successives (une valeur par ligne)", placeholder="1200\\n1300\\n1450", height=115, max_chars=3000)
    direction = st.radio("Interprétation de la mesure", ["Valeur élevée favorable", "Valeur faible favorable", "Sans interprétation"], index=2)
    draw = st.form_submit_button("Générer le graphique", type="primary")
if draw:
    chosen = next(t for t in tests if t["id"] == chart_test)
    lines = [line.strip().replace(",", ".") for line in raw_values.splitlines() if line.strip()]
    try:
        values = [float(line) for line in lines]
        if not 2 <= len(values) <= 60 or any(not math.isfinite(v) or (v < 0 and not chosen.get("signed")) for v in values):
            raise ValueError
    except ValueError:
        st.error("Saisissez entre 2 et 60 valeurs numériques, une par ligne" + ("." if chosen.get("signed") else ", positives ou nulles."))
    else:
        st.session_state["performance_chart"] = {"test_id":chart_test, "values":values, "direction":direction}
chart = st.session_state.get("performance_chart")
if chart:
    chosen = next(t for t in tests if t["id"] == chart["test_id"])
    st.write("**" + chosen["name"] + "** — " + chosen["unit"])
    st.caption("Évolution des mesures successives")
    minimum=min(chart["values"])
    maximum=max(chart["values"])
    for i, value in enumerate(chart["values"], 1):
        st.write(f"**Mesure {i}** — {value:g} {chosen['unit']}")
        st.progress((value - minimum) / (maximum - minimum) if maximum > minimum else 1.0)
    if maximum == minimum:
        st.caption("Toutes les mesures ont la même valeur.")
    first,last=chart["values"][0],chart["values"][-1]
    delta=last-first
    st.metric("Variation entre première et dernière mesure", f"{delta:+g} {chosen['unit']}")
    if chart["direction"]=="Sans interprétation":
        st.caption("Variation descriptive uniquement ; aucune conclusion sur la performance.")
    else:
        favorable=(delta>0) if chart["direction"]=="Valeur élevée favorable" else (delta<0)
        if delta==0:st.info("Valeur inchangée entre les deux mesures.")
        elif favorable:st.success("Évolution favorable selon le sens de mesure choisi.")
        else:st.info("Évolution défavorable selon le sens de mesure choisi.")
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=["Mesure","Valeur","Unité","Épreuve"])
    writer.writeheader()
    for i,v in enumerate(chart["values"],1):
        writer.writerow({"Mesure":i,"Valeur":v,"Unité":chosen["unit"],"Épreuve":chosen["name"]})
    st.download_button("Exporter les données du graphique (CSV)",output.getvalue().encode("utf-8-sig"),"progression_eps.csv","text/csv",key="export_progression")
    st.caption("Le graphique représente des mesures successives saisies manuellement, sans identification d'élèves ni normes de référence.")

with st.expander("Catalogue complet des épreuves"):
    st.dataframe([{"Test":t["name"],"Domaine":t["domain"],"Unité":t["unit"]} for t in tests],hide_index=True,use_container_width=True)
st.caption("Seuls les calculs dont la formule est documentée sont affichés ; aucun barème n'est appliqué.")
