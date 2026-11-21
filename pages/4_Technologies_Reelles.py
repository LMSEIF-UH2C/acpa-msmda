"""Catalogue complet des technologies EPS, avec niveau de vérification visible."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_real_tools
st.set_page_config(page_title="ACPA/MSMDA | Catalogue",page_icon="🔎",layout="wide")
st.title("Catalogue technologique EPS")
st.caption("Découvrez les outils pour préparer, animer et évaluer vos séances EPS.")
catalogue=load_real_tools()
a,b=st.columns(2)
a.metric("Références répertoriées",len(catalogue))
b.metric("Fonctionnalités vérifiées",sum(t.get("evidence_status")=="FEATURES_VERIFIED_ON_OFFICIAL_SITE" for t in catalogue))
category=st.selectbox("Catégorie",["Toutes"]+sorted({t["category"] for t in catalogue}))
search=st.text_input("Nom de l'application")
filtered=[t for t in catalogue if (category=="Toutes" or t["category"]==category) and search.casefold() in t["name"].casefold()]
st.dataframe([{"Application":t["name"],"Catégorie":t["category"],"Lien éditeur":"Disponible" if t.get("source_url") else "À compléter"} for t in filtered],hide_index=True,use_container_width=True)
st.divider()
st.subheader("Présélection contextuelle")
query=st.text_area("Objectif pédagogique et contraintes (sans données personnelles)",value="Endurance, suivi de course, budget limité",max_chars=1000)
if query.strip():
    result=match_real_tools(query)
    st.caption("Suggestions selon les usages renseignés dans le catalogue.")
    for t in result["matches"]:
        with st.expander(t["name"]):
            st.write("Correspondances : "+", ".join(t["matched_terms"]))
            for caution in t["cautions"]:st.caption(caution)
            if t.get("source_url"):st.link_button("Source officielle renseignée",t["source_url"])
    if not result["matches"]:st.info("Aucune fiche documentée correspondante ; explorer les catégories pour découvrir d'autres références.")
