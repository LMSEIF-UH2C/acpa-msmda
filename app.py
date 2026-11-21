"""ACPA/MSMDA — accueil mobile pour les enseignants d'EPS."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_real_tools

st.set_page_config(page_title="ACPA/MSMDA | EPS",page_icon=":material/directions_run:",layout="centered",initial_sidebar_state="collapsed")
def home():
    st.markdown("""
    <style>
    .block-container {padding-top:1.1rem;padding-bottom:3rem;max-width:850px}
    h1 {font-size:clamp(1.8rem,7vw,2.6rem)!important;letter-spacing:-.035em}
    h2 {font-size:1.35rem!important;margin-top:1.2rem!important}
    div[data-testid="stMetric"] {padding:.6rem .4rem;border:1px solid rgba(128,128,128,.22);border-radius:12px;text-align:center}
    div[data-testid="stMetricLabel"] {font-size:.73rem}
    div[data-testid="stMetricValue"] {font-size:1.4rem}
    div[data-testid="stButton"] button {min-height:3rem;border-radius:10px;white-space:normal;text-align:left;justify-content:flex-start;padding-inline:1rem;font-weight:550}
    div[data-testid="stExpander"] {border-radius:12px}
    div[data-testid="stAlert"] {padding:.6rem .75rem}
    @media(max-width:640px){
     .block-container {padding-left:1rem;padding-right:1rem}
     div[data-testid="stMetricValue"] {font-size:1.25rem}
     div[data-testid="stMetricLabel"] {font-size:.65rem}
    }
    </style>
    """,unsafe_allow_html=True)

    catalogue=load_real_tools()
    categories=sorted({t["category"] for t in catalogue})
    st.title("ACPA / MSMDA")
    st.caption("Votre espace pour préparer, organiser et enrichir vos séances d'EPS.")

    st.subheader("Votre espace de travail")
    left,right=st.columns(2)
    with left:
        if st.button("Explorer les technologies",icon=":material/search:",use_container_width=True):
            st.session_state["home_view"]="search"
            st.rerun()
        if st.button("Mesurer et analyser",icon=":material/monitoring:",use_container_width=True):
            st.switch_page("pages/2_Performance_Lab.py")
    with right:
        if st.button("Concevoir une séance",icon=":material/edit_note:",use_container_width=True):
            st.switch_page("pages/5_Studio_Pedagogique.py")
        if st.button("Organiser mes séances",icon=":material/event_note:",use_container_width=True):
            st.switch_page("pages/3_Espace_Enseignant.py")

    st.subheader("Décrivez votre besoin")
    context=st.text_area("Décrivez votre activité, vos objectifs et contraintes",placeholder="Ex. Endurance, 35 élèves, sans connexion, budget limité",max_chars=1000,height=95,key="home_context")
    search_now=st.button("Voir les suggestions",type="primary",use_container_width=True)
    if search_now and not context.strip():
        st.warning("Décrivez votre situation pour obtenir des suggestions.")
    if context.strip() and (search_now or st.session_state.get("home_view")=="search"):
        result=match_real_tools(context)
        st.caption("Suggestions selon les usages renseignés, à confirmer avant utilisation.")
        if not result["matches"]:
            st.info("Aucune correspondance disponible. Explorez les catégories ci-dessous ; une solution sans application peut aussi convenir.")
        for t in result["matches"][:8]:
            with st.expander(t["name"]+" · "+t["category"]):
                st.write("Pourquoi cet outil ? "+", ".join(t["matched_terms"]))
                if t.get("features"):
                    st.write("Fonctions : "+", ".join(t["features"][:4]))
                if t.get("platforms"):
                    st.caption("Plateformes : "+", ".join(t["platforms"]))
                for note in t.get("cautions",[]):st.caption(note)
                if t.get("source_url"):st.link_button("Consulter l'éditeur",t["source_url"])
        if len(result["matches"])>8:st.caption(f"{len(result['matches'])-8} autres correspondances : affinez votre recherche.")

    st.subheader("Répertoire des technologies")
    category=st.selectbox("Famille d'outils",["Toutes"]+categories)
    name=st.text_input("Nom de l'application",placeholder="Rechercher parmi les outils")
    filtered=[t for t in catalogue if (category=="Toutes" or t["category"]==category) and name.casefold() in t["name"].casefold()]
    st.caption("Explorez les fiches et consultez les informations disponibles pour chaque outil.")
    page_size=12
    max_pages=max(1,(len(filtered)+page_size-1)//page_size)
    page=st.number_input("Page",min_value=1,max_value=max_pages,value=1,step=1) if max_pages>1 else 1
    for t in filtered[(page-1)*page_size:page*page_size]:
        with st.expander(t["name"]+" · "+t["category"]):
            status="Fonctionnalités documentées" if t.get("evidence_status")=="FEATURES_VERIFIED_ON_OFFICIAL_SITE" else "Informations à compléter"
            st.caption(status)
            if t.get("features"):st.write("Fonctions : "+", ".join(t["features"]))
            if t.get("platforms"):st.write("Plateformes : "+", ".join(t["platforms"]))
            if t.get("pricing"):st.write("Tarif : "+t["pricing"])
            if t.get("offline"):st.write("Hors ligne : "+t["offline"])
            if t.get("source_url"):st.link_button("Site éditeur",t["source_url"])
            else:st.caption("Lien éditeur en cours de renseignement.")
    with st.expander("Confidentialité et utilisation"):
        st.write("Ne renseignez aucune donnée personnelle d'élève dans cette version. Vérifiez les conditions d'utilisation des applications avant de les utiliser en classe.")


pages = st.navigation([
    st.Page(home, title="Accueil", icon=":material/home:", default=True),
    st.Page("pages/2_Performance_Lab.py", title="Évaluer", icon=":material/monitoring:"),
    st.Page("pages/3_Espace_Enseignant.py", title="Organiser une séance", icon=":material/event_note:"),
    st.Page("pages/4_Technologies_Reelles.py", title="Technologies", icon=":material/search:"),
    st.Page("pages/5_Studio_Pedagogique.py", title="Créer un scénario", icon=":material/edit_note:"),
], position="sidebar")
pages.run()
