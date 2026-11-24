"""Observation formative anonyme, grille personnalisable."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.formative import DIMENSIONS, LEVELS, summarize_observations, observation_export
from acpa_msmda.i18n import t
from acpa_msmda.learning_library import load_situations, details
from acpa_msmda.ui import FORMATIVE, configure_page, page_header, PRIVACY_NOTE

S=st.session_state
configure_page(FORMATIVE)
page_header(FORMATIVE, PRIVACY_NOTE)
st.caption(t("Évaluation descriptive : une absence d’observation ne signifie pas un échec."))
ctx.render_context(st,S,fields=("activity","level","class_size","cycle_number","lesson_number"))
data=ctx.store(S)
context=(ctx.get(S,"activity"),ctx.get(S,"level"),ctx.get(S,"class_size"),ctx.get(S,"cycle_number"),ctx.get(S,"lesson_number"))
if data.get("formative_context") != context:
    st.warning(t("Toute nouvelle grille remplace les observations précédentes. Exportez-les avant de continuer."))
    if st.button(t("Créer une nouvelle grille")):
        data["formative_generation"]=data.get("formative_generation",0)+1
        data["formative_context"]=context
        data["formative_criteria"]=[]
        data["formative_records"]={}
        st.rerun()
    if data.get("formative_criteria"):
        st.download_button(t("Exporter les observations (CSV)"),observation_export(data["formative_criteria"],{f"E{i:03d}":data["formative_records"].get(f"E{i:03d}",{}) for i in range(1,data["formative_context"][2]+1)}),"observations.csv","text/csv")
    st.stop()
criteria=data["formative_criteria"]
records=data["formative_records"]
with st.expander(t("Construire la grille"),expanded=not criteria):
    available = [s for s in load_situations() if s["activity"] == context[0] and s["level"] == context[1]]
    if available:
        by_id = {s["id"]: s for s in available}
        sid = st.selectbox(t("Critère issu d’une situation pédagogique"), list(by_id), format_func=lambda k:t(by_id[k]["title"]))
        suggested = details(by_id[sid])["success"]
        st.write(suggested)
        if st.button(t("Ajouter le critère proposé"),disabled=len(criteria)>=12 or any(label==suggested for _,_,label in criteria)):
            criteria.append((str(len(criteria)+1),"Motrice",suggested))
            st.rerun()
    dimension=st.selectbox(t("Dimension"),DIMENSIONS,format_func=t)
    criterion=st.text_input(t("Critère observable"),max_chars=200)
    if st.button(t("Ajouter le critère"),disabled=not criterion.strip() or len(criteria)>=12):
        criteria.append((str(len(criteria)+1),dimension,criterion.strip()))
        st.rerun()
    for key, dim, label in criteria:
        st.write(t(dim)+" : "+label)
if not criteria:
    st.stop()
code=st.selectbox(t("Code élève"),[f"E{i:03d}" for i in range(1,context[2]+1)])
with st.form("observation_"+code):
    pending={}
    for key, dim, label in criteria:
        value=records.get(code,{}).get(key,LEVELS[0])
        pending[key]=st.radio(label,LEVELS,index=LEVELS.index(value),format_func=t,key=f"obs_{data['formative_generation']}_{code}_{key}",horizontal=False)
    if st.form_submit_button(t("Enregistrer les observations")):
        records[code]=pending
        st.rerun()
st.subheader(t("Bilan descriptif"))
for key,dim,label in criteria:
    values=[records.get(f"E{i:03d}",{}).get(key,LEVELS[0]) for i in range(1,context[2]+1)]
    result=summarize_observations(values)
    st.write("**"+label+"**")
    st.caption(t("{n} élèves observés sur {total}",n=result["observed"],total=result["total"]))
    st.dataframe([{t("Niveau observé"):t(level),t("Élèves"):count} for level,count in result["counts"].items()],hide_index=True)
all_records={f"E{i:03d}":records.get(f"E{i:03d}",{}) for i in range(1,context[2]+1)}
st.download_button(t("Exporter les observations (CSV)"),observation_export(criteria,all_records),"observations.csv","text/csv")
