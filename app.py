"""ACPA/MSMDA — plateforme EPS : catalogue réel, planification et mesures."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_real_tools

st.set_page_config(page_title="ACPA/MSMDA — Technologies pour l'EPS",page_icon="🏃",layout="wide")
st.title("ACPA / MSMDA")
st.caption("Identifier et intégrer les technologies adaptées au contexte d'enseignement de l'EPS.")
st.info("Le catalogue distingue les fiches documentées des références à vérifier. Aucun score de qualité n'est attribué sans évaluation des critères ACPA/MSMDA.")
st.warning("Ne saisissez pas de données personnelles d'élèves. Cette version n'est pas destinée à stocker des dossiers scolaires.")
catalogue=load_real_tools()
documented=[t for t in catalogue if t["evidence_status"]=="OFFICIAL_SOURCE_FEATURES_ONLY"]
a,b,c=st.columns(3)
a.metric("Références du catalogue",len(catalogue))
b.metric("Fiches avec source",len(documented))
c.metric("Catégories",len({t["category"] for t in catalogue}))
context=st.text_area("Votre contexte pédagogique",value="Endurance, suivi de course, classe nombreuse, budget limité",max_chars=1000)
if context.strip():
    result=match_real_tools(context)
    st.subheader("Correspondances contextuelles documentées")
    st.caption("Présélection par mots-clés, non classement scientifique. Les références en attente de vérification ne sont pas recommandées.")
    if result["matches"]:
        for t in result["matches"]:
            with st.expander(t["name"]+" · "+t["category"]):
                st.write("Correspondances : "+", ".join(t["matched_terms"]))
                for note in t["cautions"]: st.caption(note)
                if t.get("source_url"): st.link_button("Source",t["source_url"])
    else: st.info("Aucune fiche documentée ne correspond aux termes saisis.")
st.subheader("Explorer toutes les technologies")
categories=sorted({t["category"] for t in catalogue})
category=st.selectbox("Catégorie",["Toutes"]+categories)
search=st.text_input("Rechercher une application")
filtered=[t for t in catalogue if (category=="Toutes" or t["category"]==category) and search.casefold() in t["name"].casefold()]
st.dataframe([{"Application":t["name"],"Catégorie":t["category"],"Vérification":"Source renseignée" if t.get("source_url") else "À vérifier"} for t in filtered],hide_index=True,use_container_width=True)
st.caption("Utilisez le menu Pages pour ouvrir Performance Lab et l'Espace enseignant.")
