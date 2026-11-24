"""Consult available catalogue assessments without imputing missing ratings."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools
from acpa_msmda.scoring import CODES,LABELS
from acpa_msmda.i18n import t
from acpa_msmda.ui import TECH_EVAL,configure_page,page_header

configure_page(TECH_EVAL)
page_header(TECH_EVAL)
st.caption(t("Les évaluations disponibles reposent sur les informations documentées. Elles ne démontrent pas l’efficacité pédagogique."))
tools=load_real_tools()
query=st.text_input(t("Nom de l'outil"),max_chars=100)
rated_only=st.checkbox(t("Afficher uniquement les outils évalués"),value=False)
matches=[x for x in tools if query.casefold() in x["name"].casefold() and (not rated_only or x.get("criteria_scores"))]
if not matches:
    st.info(t("Aucune fiche ne correspond à ces filtres."))
else:
    options={x["id"]:x for x in matches}
    selected=st.selectbox(t("Choisir une technologie"),list(options),format_func=lambda k:options[k]["name"])
    tool=options[selected]
    st.subheader(tool["name"])
    if tool.get("source_url"):
        st.link_button(t("Site de l'éditeur"),tool["source_url"])
    scores=tool.get("criteria_scores")
    if not scores:
        st.info(t("Cette technologie ne dispose pas encore d’une évaluation documentée."))
    else:
        rows=[]
        for code in CODES:
            value=scores.get(code)
            status=t("Non renseigné") if value in (None,"NR") else t("Sans objet") if value=="SO" else str(value)+"/10"
            rows.append({"Code":code,t("Critère"):t(LABELS[code]),t("Évaluation"):status})
        st.dataframe(rows,hide_index=True)
        st.caption(t("NR : information non renseignée. SO : critère sans objet."))
        st.caption(t("Les 18 critères opérationnels ne constituent pas une transcription exhaustive des 97 paramètres."))
