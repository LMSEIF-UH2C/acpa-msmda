"""ACPA/MSMDA Performance Lab — prototype de terrain sans données personnelles."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import streamlit as st

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "performance_tests.json"
data = json.loads(REGISTRY.read_text(encoding="utf-8"))
tests = data["tests"]

st.set_page_config(page_title="ACPA/MSMDA | Performance Lab", page_icon="⏱️", layout="wide")
st.title("Performance Lab")
st.caption("ACPA/MSMDA 2.0 · Référentiel institutionnel, protocoles de thèse et tests complémentaires")
st.warning("Version pilote. Protocoles à confirmer avant utilisation institutionnelle. N'enregistrez aucun nom, identifiant d'élève ni donnée de santé personnelle.")
source = st.selectbox("Collection", ["Toutes", "Circulaire 2358/25", "Thèse", "Complément"])
domain = st.selectbox("Domaine", ["Tous"] + sorted({t["domain"] for t in tests}))
selected = [t for t in tests if (source == "Toutes" or source in t["source"]) and (domain == "Tous" or t["domain"] == domain)]
st.metric("Tests et mesures disponibles", len(selected))
test_id = st.selectbox("Choisir une épreuve", [t["id"] for t in selected], format_func=lambda i: next(t["name"] for t in selected if t["id"] == i)) if selected else None
if test_id:
    t = next(t for t in selected if t["id"] == test_id)
    st.subheader(t["name"])
    st.write("**Origine :** " + t["source"])
    st.write("**Mesure :** " + t["measure"] + " (" + t["unit"] + ")")
    st.info(t["protocol_note"])
    with st.form("measurement"):
        value = st.number_input("Résultat mesuré (" + t["unit"] + ")", min_value=0.0, value=0.0, step=0.1)
        submitted = st.form_submit_button("Calculer / enregistrer localement", type="primary")
    if submitted:
        if value <= 0:
            st.error("Saisissez une valeur positive.")
        else:
            record = {"test_id":test_id,"test":t["name"],"value":value,"unit":t["unit"],"source":t["source"]}
            st.session_state["performance_last_record"] = record
    record = st.session_state.get("performance_last_record")
    if record and record["test_id"] == test_id:
        st.success("Mesure saisie pour cette session (aucun enregistrement serveur volontaire).")
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
with st.expander("Catalogue complet des épreuves"):
    st.dataframe([{"Test":t["name"],"Domaine":t["domain"],"Source":t["source"],"Unité":t["unit"]} for t in tests],hide_index=True,use_container_width=True)
st.caption("Les formules, normes, interprétations et barèmes non documentés ne sont pas simulés. Les mesures restent dans la session du navigateur jusqu'à fermeture ou réinitialisation.")
