"""Organiser les ateliers : groupes, rotations et temps de séance."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.scenario_engine import safe_cell  # noqa: E402
from acpa_msmda.ui import PLANNER, PRIVACY_NOTE, SEARCH, configure_page, page_header  # noqa: E402

S = st.session_state
configure_page(PLANNER)
page_header(PLANNER, PRIVACY_NOTE)

ctx.render_context(st, S, fields=("activity", "level", "class_size", "duration", "connectivity",
                                  "devices", "space", "equipment", "objectives"))
workshops = st.slider("Nombre d'ateliers", min_value=1, max_value=8, **ctx.bind(S, "workshops", 4))


def build_plan(class_size: int, duration: int, workshops: int) -> dict:
    welcome = max(3, round(duration * .10))
    review = max(4, round(duration * .10))
    cool_down = max(3, round(duration * .10))
    practice = duration - welcome - review - cool_down
    groups = [class_size // workshops + (1 if i < class_size % workshops else 0) for i in range(workshops)]
    return {"groups": groups, "rotation": practice / workshops,
            "phases": [("Accueil et consignes", welcome), ("Ateliers et rotations", practice),
                       ("Retour au calme", cool_down), ("Bilan et traces", review)]}


class_size = int(ctx.get(S, "class_size"))
duration = int(ctx.get(S, "duration"))
if workshops > class_size:
    st.error(f"{workshops} ateliers pour {class_size} élèves : certains groupes seraient vides. "
             "Réduisez le nombre d'ateliers.")
    st.stop()

plan = build_plan(class_size, duration, workshops)
st.subheader("Organisation proposée")
st.dataframe([{"Phase": name, "Durée (min)": minutes} for name, minutes in plan["phases"]],
             hide_index=True, use_container_width=True)
st.write("**Groupes :** " + ", ".join(str(n) for n in plan["groups"]) + " élèves")
st.write(f"**Temps par atelier :** {plan['rotation']:.1f} min, transitions comprises.")

if ctx.get(S, "connectivity") != "Disponible":
    st.info("Connexion limitée sur le lieu de pratique : préférez les chronomètres, les supports "
            "téléchargés à l'avance et les fiches papier.")
if ctx.get(S, "devices") == "Aucun":
    st.info("Sans appareil : consignes imprimées, ateliers autonomes et observation directe.")
if st.button(SEARCH.title + " pour cette séance", icon=SEARCH.icon):
    ctx.put(S, "search_context", ctx.search_query(S))
    ctx.put(S, "search_query", ctx.search_query(S))
    st.switch_page(SEARCH.path)

output = io.StringIO()
writer = csv.writer(output)
writer.writerow(["APS", "Niveau", "Effectif", "Durée", "Objectifs", "Phase", "Minutes"])
for name, minutes in plan["phases"]:
    writer.writerow([ctx.get(S, "activity"), ctx.get(S, "level"), class_size, duration,
                     safe_cell(ctx.get(S, "objectives") or ""), name, minutes])
st.download_button("Exporter l'organisation (CSV)", output.getvalue().encode("utf-8-sig"),
                   file_name="organisation_seance_eps.csv", mime="text/csv")
st.caption("Répartition indicative : environ 10 % du temps pour l'accueil, le retour au calme et le bilan. "
           "À adapter à votre terrain.")
