"""Catalogue de produits réels : faits sourcés, aucune note ACPA/MSMDA inventée."""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st

CATALOG = Path(__file__).resolve().parents[1] / "data" / "real_tools_evidence.json"
data = json.loads(CATALOG.read_text(encoding="utf-8"))
if data.get("dataset_type") != "REAL_PRODUCTS_FACTUAL_REGISTER_NOT_SCORED":
    st.error("Catalogue invalide.")
    st.stop()

st.set_page_config(page_title="ACPA/MSMDA | Outils réels", page_icon="🔎", layout="wide")
st.title("ACPA/MSMDA — Catalogue d'outils réels")
st.caption("Inventaire factuel sourcé · dernière revue : " + data["review_date"])
st.warning("Les outils existent, mais leurs 18 critères ACPA/MSMDA n'ont pas été évalués par des experts. Aucun score ni classement scientifique n'est calculé.")
st.info("N'importez aucune vidéo d'élève, donnée personnelle ou document confidentiel dans cette démonstration.")
query = st.text_input("Rechercher un outil ou une fonctionnalité", max_chars=100, placeholder="vidéo, capteurs, observation…")
categories = ["Toutes"] + sorted({tool["category"] for tool in data["tools"]})
category = st.selectbox("Domaine d'utilisation", categories)
tools = [
    t for t in data["tools"]
    if (category == "Toutes" or t["category"] == category)
    and (not query or query.casefold() in json.dumps(t, ensure_ascii=False).casefold())
]
st.metric("Outils documentés", len(tools))
for t in tools:
    with st.container(border=True):
        st.subheader(t["name"])
        st.caption(t["category"] + " · " + t["platform"] + " · " + t["cost"])
        st.write("**Fonctions documentées :** " + " · ".join(t["features"]))
        st.write("**À vérifier sur le terrain :** " + t["note"])
        st.link_button("Consulter la source officielle", t["evidence"])
        st.caption("Statut : caractéristiques publiques documentées ; évaluation multicritère et efficacité en EPS non établies.")
st.divider()
st.subheader("Étape suivante : évaluation des 18 critères")
st.write("Une évaluation ACPA/MSMDA exige un protocole, des évaluateurs, des preuves par critère, une traçabilité et une vérification de la fidélité. Les notes manquantes restent **non évaluées**, jamais remplacées par des valeurs fictives.")
st.download_button("Exporter le registre factuel (JSON)", json.dumps(data, ensure_ascii=False, indent=2), "acpa_outils_reels_non_notes.json", "application/json")
