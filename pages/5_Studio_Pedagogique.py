"""Concevoir une séance : phases, activités, supports et export."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.scenario_engine import export_scenario_csv, recommend_phase_tools, validate_scenario  # noqa: E402
from acpa_msmda.scenario_templates import apply_template, load_templates, scenario_checks  # noqa: E402
from acpa_msmda.ui import PRIVACY_NOTE, STUDIO, configure_page  # noqa: E402

PHASE_NAMES = ("Diagnostic", "Mise en activité", "Apprentissage", "Régulation", "Évaluation")
PHASE_MINUTES = (5, 10, 30, 10, 5)
SUPPORTS = ("Vidéo", "Audio", "Quiz", "QR code", "Fiche numérique", "Démonstration", "Capteurs", "Analyse vidéo")
MODALITIES = ("Présentiel", "Hybride", "À distance", "Classe inversée", "Autonomie accompagnée")

S = st.session_state
configure_page(STUDIO)
st.title(STUDIO.title)
st.caption(STUDIO.summary + " " + PRIVACY_NOTE)

templates = load_templates()
left, right = st.columns([3, 1], vertical_alignment="bottom")
with left:
    selected = st.selectbox("Partir d'un modèle", ["Séance vierge"] + [t["title"] for t in templates],
                            key="studio_template")
with right:
    if st.button("Charger le modèle", disabled=selected == "Séance vierge", use_container_width=True):
        apply_template(next(t for t in templates if t["title"] == selected), S)
        st.rerun()

ctx.render_context(st, S, fields=("activity", "level", "class_size", "duration", "connectivity",
                                  "devices", "equipment", "objectives"))
modality = st.selectbox("Modalité", MODALITIES, **ctx.bind(S, "modality", "Présentiel"))
prerequisites = st.text_input("Prérequis", max_chars=300, **ctx.bind(S, "prerequisites", ""))

st.subheader("Déroulement")
st.caption("Adaptez les activités, supports, critères de réussite et durées.")
connectivity = ctx.get(S, "connectivity")
rows = []
for i, (phase, default_minutes) in enumerate(zip(PHASE_NAMES, PHASE_MINUTES)):
    minutes_now = ctx.store(S).get(f"minutes_{i}", default_minutes)
    with st.expander(f"{i + 1}. {phase} · {minutes_now} min", expanded=i == 2):
        col1, col2 = st.columns([3, 1])
        with col1:
            action = st.text_area("Activité, consignes et rôle des élèves", max_chars=600,
                                  **ctx.bind(S, f"action_{i}", ""))
            supports = st.multiselect("Supports", SUPPORTS, **ctx.bind(S, f"supports_{i}", []))
            evaluation = st.text_input("Critères de réussite et retour aux élèves", max_chars=300,
                                       **ctx.bind(S, f"evaluation_{i}", ""))
        with col2:
            minutes = int(st.number_input("Durée (min)", min_value=0, max_value=240,
                                          **ctx.bind(S, f"minutes_{i}", default_minutes)))
        rows.append({"Phase": phase, "Durée (min)": minutes, "Activité / consignes": action,
                     "Supports": ", ".join(supports), "Évaluation / feedback": evaluation})
        suggestions = recommend_phase_tools(phase, connectivity=connectivity, limit=5)
        if suggestions:
            st.markdown("**Outils à explorer pour cette phase**")
            for tool in suggestions:
                label = tool["name"] + " · " + tool["category"]
                if not tool["documented"]:
                    label += " · à confirmer"
                st.markdown(f"- [{label}]({tool['source_url']})")
                if tool["notes"]:
                    st.caption(" ; ".join(tool["notes"]))
        else:
            st.caption("Aucun outil documenté pour cette phase. Un support non numérique peut convenir.")

duration = int(ctx.get(S, "duration"))
st.subheader("Répartition du temps")
total_minutes = sum(r["Durée (min)"] for r in rows)
for row in rows:
    st.write(f"**{row['Phase']}** · {row['Durée (min)']} min")
    st.progress(row["Durée (min)"] / total_minutes if total_minutes else 0.0)
validation = validate_scenario(rows, duration)
if validation["balanced"]:
    st.success(f"Les phases occupent exactement la durée prévue : {duration} min.")
else:
    st.warning(f"Les phases totalisent {validation['used_minutes']} min pour une séance de {duration} min "
               f"(écart : {validation['difference_minutes']:+d} min).")
issues = scenario_checks(rows, ctx.get(S, "objectives") or "")
with st.expander(f"Points à compléter : {len(issues)}"):
    if issues:
        for issue in issues:
            st.write("• " + issue)
    else:
        st.write("Objectifs, activités et critères de réussite sont renseignés.")

metadata = {"APS": ctx.get(S, "activity"), "Niveau": ctx.get(S, "level"), "Modalité": modality,
            "Effectif": ctx.get(S, "class_size"), "Durée (min)": duration,
            "Connexion": ctx.CONNECTIVITY_LABELS[connectivity],
            "Appareils": ctx.get(S, "devices"), "Objectifs": ctx.get(S, "objectives"),
            "Prérequis": prerequisites, "Matériel et contraintes": ctx.get(S, "equipment")}
st.download_button("Exporter le scénario (CSV)", export_scenario_csv(metadata, rows),
                   "scenario_seance_eps.csv", "text/csv")
