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
st.info("Explorez les outils et leurs usages pour choisir ceux qui correspondent à votre séance. Les informations sont complétées progressivement.")
st.warning("Ne saisissez pas de données personnelles d'élèves. Cette version n'est pas destinée à stocker des dossiers scolaires.")
catalogue=load_real_tools()
documented=[t for t in catalogue if t.get("source_url")]
a,b,c=st.columns(3)
a.metric("Références du catalogue",len(catalogue))
b.metric("Liens éditeurs",len(documented))
c.metric("Fiches vérifiées",sum(t.get("evidence_status")=="FEATURES_VERIFIED_ON_OFFICIAL_SITE" for t in catalogue))
context=st.text_area("Votre contexte pédagogique",value="Endurance, suivi de course, classe nombreuse, budget limité",max_chars=1000)
if context.strip():
    result=match_real_tools(context)
    st.subheader("Suggestions pour votre contexte")
    st.caption("Suggestions fondées sur les usages renseignés. Vérifiez les fonctionnalités avant de choisir.")
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
st.dataframe([{"Application":t["name"],"Catégorie":t["category"],"Lien éditeur":"Disponible" if t.get("source_url") else "À compléter"} for t in filtered],hide_index=True,use_container_width=True)
st.caption("Utilisez le menu Pages pour ouvrir Performance Lab et l'Espace enseignant.")
