"""Observation formative anonyme, grille personnalisable."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.formative import DIMENSIONS, LEVELS, summarize_observations, observation_export, snapshot, compare_lessons
from acpa_msmda.i18n import colon, t
from acpa_msmda.pdf import formative_comparison_pdf
from acpa_msmda.formative_backup import make_backup, load_backup
from acpa_msmda.learning_library import load_situations, details
from acpa_msmda.ui import FORMATIVE, configure_page, page_header, PRIVACY_NOTE

S=st.session_state
configure_page(FORMATIVE)
page_header(FORMATIVE, PRIVACY_NOTE)
st.caption(t("Évaluation descriptive : une absence d’observation ne signifie pas un échec."))
data=ctx.store(S)
with st.expander(t("Sauvegarder ou restaurer les évaluations")):
    st.caption(t("Conservez ce fichier dans un emplacement sécurisé. Ne saisissez aucune donnée nominative."))
    current = None
    if data.get("formative_context") is not None:
        current = {"context":data["formative_context"],"criteria":data["formative_criteria"],"records":data["formative_records"]}
    saved_history = data.get("formative_history",{})
    if current is not None or saved_history:
        try:
            backup = make_backup(current,saved_history)
            st.download_button(t("Télécharger la sauvegarde (JSON)"),backup,"evaluations_acpa.json","application/json")
        except ValueError:
            st.error(t("La sauvegarde dépasse les limites autorisées ou contient des données invalides."))
    uploaded = st.file_uploader(t("Restaurer une sauvegarde JSON"),type=["json"],key="formative_backup_upload")
    if uploaded is not None:
        try:
            restored, archived = load_backup(uploaded.getvalue())
        except ValueError:
            st.error(t("Fichier de sauvegarde invalide ou incompatible."))
        else:
            st.write(t("{n} séances archivées dans le fichier",n=len(archived)))
            st.warning(t("La restauration remplacera les évaluations actuellement ouvertes."))
            if st.button(t("Confirmer la restauration"),key="formative_restore"):
                data["formative_history"]=archived
                data["formative_generation"]=data.get("formative_generation",0)+1
                selected=restored or max(archived.values(),key=lambda v:v["context"][4])
                data["formative_context"]=selected["context"]
                data["formative_criteria"]=selected["criteria"]
                data["formative_records"]=selected["records"]
                for key,value in zip(("activity","level","class_size","cycle_number","lesson_number","formative_group"),selected["context"]):
                    ctx.put(S,key,value)
                st.rerun()
ctx.render_context(st,S,fields=("activity","level","class_size","cycle_number","lesson_number"))
group=st.text_input(t("Code du groupe (non nominatif)"),max_chars=30,**ctx.bind(S,"formative_group","")).strip()
history=data.setdefault("formative_history",{})
context=(ctx.get(S,"activity"),ctx.get(S,"level"),ctx.get(S,"class_size"),ctx.get(S,"cycle_number"),ctx.get(S,"lesson_number"),group)
if data.get("formative_context") != context:
    st.warning(t("Toute nouvelle grille remplace les observations précédentes. Exportez-les avant de continuer."))
    if st.button(t("Créer une nouvelle grille")):
        data["formative_generation"]=data.get("formative_generation",0)+1
        data["formative_context"]=context
        existing=history.get(context)
        previous=[v for k,v in history.items() if k[:4]==context[:4] and k[5]==context[5] and k[4]<context[4]]
        from copy import deepcopy
        data["formative_criteria"]=deepcopy(existing["criteria"]) if existing else deepcopy(max(previous,key=lambda v:v["context"][4])["criteria"]) if previous else []
        data["formative_records"]=deepcopy(existing["records"]) if existing else {}
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
        st.write(t(dim)+colon()+label)
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


st.subheader(t("Suivi du cycle"))
st.caption(t("Historique temporaire de cette session. Exportez vos données avant de fermer l’application."))
confirmed=st.checkbox(t("Les codes correspondent aux mêmes élèves et les conditions d’observation sont comparables."),key="formative_match")
if st.button(t("Archiver cette séance"),disabled=not group or context[3]<1 or context[4]<1 or not confirmed):
    history[context]=snapshot(context,criteria,records)
    st.rerun()
compatible=[v for k,v in history.items() if k[:4]==context[:4] and k[5]==context[5] and k[4]<context[4] and v["criteria"]==criteria]
if compatible and confirmed and group and context[3]>0 and context[4]>0:
    choices={v["context"][4]:v for v in compatible}
    prior=st.selectbox(t("Séance de référence"),sorted(choices))
    comparison=compare_lessons(choices[prior],snapshot(context,criteria,records))
    labels={"higher":t("Niveau supérieur"),"same":t("Niveau stable"),"lower":t("Niveau inférieur"),"missing":t("Non comparable")}
    for item in comparison:
        st.write(item["criterion"])
        st.dataframe([{t("Variation observée"):label,t("Élèves"):item[key]} for key,label in labels.items()],hide_index=True)
        st.write(t("Détail par élève"))
        st.dataframe([{t("Code"):code,t("Avant"):t(old),t("Après"):t(new),t("Variation observée"):labels[status]} for code,old,new,status in item["transitions"]],hide_index=True)
    st.download_button(t("Bilan comparatif (PDF)"),formative_comparison_pdf(context,prior,comparison),"bilan_formative.pdf","application/pdf")
