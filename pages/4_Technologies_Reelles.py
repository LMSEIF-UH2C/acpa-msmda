"""Catalogue d'outils réels et présélection transparente par contexte."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools, match_real_tools

st.set_page_config(page_title="ACPA/MSMDA | Technologies réelles",page_icon="🔎",layout="wide")
st.title("Technologies réelles pour l'EPS")
st.caption("Catalogue initial sourcé, extensible et sans notes fictives.")
st.warning("Présélection descriptive : ce module ne détermine pas encore la meilleure technologie au sens des 18 critères ACPA/MSMDA. Aucun score de produit réel n'a été inventé.")
query=st.text_area("Décrivez votre situation pédagogique (sans données personnelles)",value="Endurance, suivi de course, classe nombreuse, budget limité",max_chars=1000)
try:
    result=match_real_tools(query) if query.strip() else {"matches":[],"context_flags":[]}
    matches=result["matches"]
    st.write(f"**{len(matches)} outil(s) associé(s) à des termes de votre contexte**")
    if result["context_flags"]:
        st.caption("Contraintes détectées : "+", ".join(result["context_flags"]))
    if not matches:
        st.info("Aucune correspondance descriptive. Consultez le catalogue complet ou reformulez les objectifs.")
    for tool in matches:
        with st.expander(tool["name"]+" · "+tool["category"],expanded=len(matches)<=3):
            st.write("**Correspondances :** "+", ".join(tool["matched_terms"]))
            st.write("**Conditions à examiner :** "+tool["requirement"])
            for caution in tool["cautions"]:
                st.caption("• "+caution)
            st.link_button("Consulter la source officielle",tool["source_url"])
    with st.expander("Voir tout le catalogue"):
        st.dataframe([{"Application":t["name"],"Catégorie":t["category"],"Usage":", ".join(t["uses"]),"Statut":"Fonctions documentées, critères non notés"} for t in load_real_tools()],hide_index=True,use_container_width=True)
except (ValueError,KeyError,OSError) as error:
    st.error("Impossible de charger le catalogue : "+str(error))
