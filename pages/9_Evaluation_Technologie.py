"""Consult available catalogue assessments without imputing missing ratings."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools
from acpa_msmda.scoring import CODES,LABELS,documented,applicable
from acpa_msmda import session_context as ctx
from acpa_msmda.scenario_engine import safe_cell
import csv
import io
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

st.divider()
st.subheader(t("Évaluer un nouvel outil"))
st.caption(t("Autoévaluation exploratoire sur 18 critères, distincte des évaluations documentées du répertoire."))
with st.form("independent_assessment"):
    name=st.text_input(t("Nom de l'outil"),max_chars=150,key="assessment_name")
    evidence=st.text_area(t("Sources et observations"),max_chars=3000)
    st.caption(t("0 = très insuffisant ; 10 = excellent. Utilisez NR si la preuve manque et SO si le critère ne s’applique pas."))
    assessment={}
    for code in CODES:
        assessment[code]=st.selectbox(code+" · "+t(LABELS[code]),["NR","SO",*range(11)],key="ind_"+code,format_func=str)
    if st.form_submit_button(t("Enregistrer mon évaluation")):
        if not name.strip() or not evidence.strip() or not documented(assessment):
            st.error(t("Indiquez un nom, des sources ou observations et au moins une note."))
        else:
            ctx.put(st.session_state,"independent_assessment",{"name":name.strip(),"evidence":evidence.strip(),"scores":assessment})
result=ctx.get(st.session_state,"independent_assessment")
if result:
    scores=result["scores"]
    known=documented(scores)
    eligible=applicable(scores)
    st.subheader(result["name"])
    st.caption(t("Critères renseignés : {n}/{m}",n=len(known),m=len(eligible)))
    st.write(t("Moyenne descriptive des critères renseignés : {value}/10",value=round(sum(scores[c] for c in known)/len(known),2)))
    st.caption(t("Cette moyenne ne constitue ni une note ACPA/MSMDA validée ni une preuve d’efficacité. Les critères ont ici le même poids."))
    rows=[(c,LABELS[c],scores[c]) for c in CODES]
    st.dataframe([{"Code":c,t("Critère"):t(label),t("Évaluation"):str(value)} for c,label,value in rows],hide_index=True)
    buffer=io.StringIO()
    writer=csv.writer(buffer)
    writer.writerow([t("Nom de l'outil"),safe_cell(result["name"])])
    writer.writerow([t("Sources et observations"),safe_cell(result["evidence"])])
    writer.writerow([t("Autoévaluation exploratoire sur 18 critères, distincte des évaluations documentées du répertoire.")])
    writer.writerow(["Code",t("Critère"),t("Évaluation")])
    for code,label,value in rows:
        writer.writerow([code,t(label),value])
    st.download_button(t("Télécharger mon évaluation"),buffer.getvalue().encode("utf-8-sig"),"evaluation_technologie.csv","text/csv")
