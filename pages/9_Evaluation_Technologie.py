"""Consult available catalogue assessments without imputing missing ratings."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools
from acpa_msmda.scoring import CODES,LABELS,PUBLIC_LABELS,documented,applicable
from acpa_msmda.context_engine import analyze_context,detect_language
from acpa_msmda.contracts import ContextRequest
from acpa_msmda.understanding import understand
from acpa_msmda.keywords import label as keyword_label
from acpa_msmda import decision
from acpa_msmda import session_context as ctx
from acpa_msmda.scenario_engine import safe_cell
import csv
import io
from acpa_msmda.i18n import colon, t
from acpa_msmda.ui import TECH_EVAL,configure_page,page_header

configure_page(TECH_EVAL)
page_header(TECH_EVAL)
S=st.session_state
st.caption(t("Décrivez votre situation d’enseignement pour identifier vos besoins et vos priorités."))
if st.button(t("Reprendre le contexte de ma séance"),key="eval_use_session"):
    ctx.put(S,"evaluation_context",ctx.search_query(S))
description=st.text_area(t("Votre situation d’enseignement"),placeholder=t("Ex. endurance, 35 élèves, sans connexion, budget limité"),max_chars=1000,**ctx.bind(S,"evaluation_context",""))
constraints=st.multiselect(t("Vos besoins et contraintes"),decision.REFINEMENTS,format_func=t,placeholder=t("Choisir dans la liste"),**ctx.bind(S,"evaluation_constraints",[]))
query_context=decision.refine(description.strip(),constraints) if description.strip() else ", ".join(t(x) for x in constraints)
if st.button(t("Analyser mon contexte"),key="analyze_context",type="primary",use_container_width=True):
    if not description.strip():
        st.warning(t("Décrivez votre activité ou vos contraintes pour obtenir des suggestions."))
    else:
        ctx.put(S,"analyzed_context",query_context)
analysis_query=ctx.get(S,"analyzed_context")
if analysis_query and analysis_query==query_context:
    analysis=analyze_context(ContextRequest(analysis_query,detect_language(analysis_query)))
    st.subheader(t("Vos besoins et priorités"))
    items=understand(analysis_query)
    for item in items:
        value=keyword_label(item.value) if item.parameter in ("Activité","Fonction") else t(item.value)
        st.write(t(item.parameter)+colon()+value)
    from acpa_msmda.context_engine import CONTEXT_BOOSTS
    boosted={code for flag in analysis.flags for code in CONTEXT_BOOSTS.get(flag,{})}
    if boosted:
        priorities=sorted(boosted,key=lambda c:(-analysis.weights.values[CODES.index(c)],CODES.index(c)))
        for code in priorities:
            st.write("• "+t(PUBLIC_LABELS[code]))
    else:
        st.caption(t("Précisez vos contraintes pour mieux cibler les technologies adaptées."))
    st.caption(t("Ces priorités découlent de votre description. Vérifiez qu’elles correspondent à votre réalité."))
    if st.button(t("Explorer les technologies adaptées"),key="context_to_explore",type="primary",use_container_width=True):
        ctx.put(S,"search_context",analysis_query)
        ctx.put(S,"search_query",analysis_query)
        st.switch_page("pages/4_Technologies_Reelles.py")
elif analysis_query:
    st.caption(t("Votre contexte a changé. Relancez l’analyse."))
st.divider()
st.caption(t("Vous pouvez aussi examiner une technologie que vous utilisez déjà."))
with st.expander(t("Examiner une technologie"),expanded=bool(ctx.get(S,"evaluation_target"))):
    tools=load_real_tools()
    target=ctx.store(st.session_state).pop("evaluation_target",None)
    if target:
        st.session_state["eval_query"]=""
        st.session_state["eval_rated_only"]=False
        st.session_state["eval_selected"]=target
    query=st.text_input(t("Nom de l'outil"),max_chars=100,key="eval_query")
    rated_only=st.checkbox(t("Afficher uniquement les outils évalués"),value=False,key="eval_rated_only")
    matches=[x for x in tools if query.casefold() in x["name"].casefold() and (not rated_only or x.get("criteria_scores"))]
    if not matches:
        st.info(t("Aucune fiche ne correspond à ces filtres."))
    else:
        options={x["id"]:x for x in matches}
        if st.session_state.get("eval_selected") not in options:
            st.session_state["eval_selected"]=next(iter(options))
        selected=st.selectbox(t("Choisir une technologie"),list(options),format_func=lambda k:options[k]["name"],key="eval_selected")
        tool=options[selected]
        st.subheader(tool["name"])
        if tool.get("source_url"):
            st.link_button(t("Site de l'éditeur"),tool["source_url"])
        if tool.get("source_url") and st.button(t("Retenir pour mon scénario"),key="eval_to_studio"):
            ctx.put(st.session_state,"scenario_tool_candidate",tool["id"])
            ctx.put(S,"scenario_context_pending",analysis_query if analysis_query == query_context else "")
            st.switch_page("pages/5_Studio_Pedagogique.py")
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
            st.caption(t("Vérifiez les fonctionnalités dans vos propres conditions de pratique."))
    
with st.expander(t("Évaluer un nouvel outil")):
    st.caption(t("Donnez votre avis sur un outil à partir de vos propres essais."))
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
        from acpa_msmda.teacher_workbooks import MIME, report_xlsx
        st.download_button(t("Télécharger mon évaluation"),report_xlsx(buffer.getvalue().encode("utf-8-sig")),"evaluation_technologie.xlsx",MIME)
