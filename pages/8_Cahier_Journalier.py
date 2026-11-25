"""Cahier journalier : planifier, retrouver et documenter les séances."""
import sys
import uuid
from pathlib import Path
from datetime import date
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.journal import STATUSES, MAX_ENTRIES, workspace_backup, restore_workspace, export_csv
from acpa_msmda.timetable import generate, timetable_warnings
from acpa_msmda.cycle_plan import check_journal, cycle_at, allows_session
from acpa_msmda.i18n import colon, t
from acpa_msmda.curriculum import profiles, validate_projects, export_projects, import_projects
from acpa_msmda.aps_specialties import registry, catalog_category, valid_specialty
from acpa_msmda.ui import JOURNAL, configure_page, page_header, PRIVACY_NOTE

S=st.session_state
configure_page(JOURNAL)
page_header(JOURNAL,PRIVACY_NOTE)
data=ctx.store(S)
entries=data.setdefault("journal_entries",[])
cycles=data.setdefault("journal_cycles",[])
slots=data.setdefault("journal_slots",[])
interruptions=data.setdefault("journal_interruptions",[])
projects=data.setdefault("cycle_projects",[])
st.caption(t("Le journal reste en mémoire de session. Téléchargez une sauvegarde pour le conserver."))
with st.expander(t("Sauvegarder ou restaurer le journal")):
    try:
        raw=workspace_backup(cycles,entries,slots,interruptions,projects)
    except ValueError:
        st.error(t("Fichier de sauvegarde invalide ou incompatible."))
    else:
        st.download_button(t("Sauvegarder mes données"),raw,"journal_acpa.json","application/json")
    uploaded=st.file_uploader(t("Restaurer mes données"),type=["json"],key="journal_upload")
    if uploaded is not None:
        try:
            restored_cycles,restored,restored_slots,restored_breaks,restored_projects=restore_workspace(uploaded.getvalue())
        except ValueError:
            st.error(t("Fichier de sauvegarde invalide ou incompatible."))
        else:
            st.warning(t("La restauration remplacera les cycles, séances, créneaux, interruptions et projets actuels."))
            if st.button(t("Confirmer la restauration"),key="journal_restore"):
                data["journal_cycles"]=restored_cycles
                data["journal_entries"]=restored
                data["journal_slots"]=restored_slots
                data["journal_interruptions"]=restored_breaks
                data["cycle_projects"]=restored_projects
                st.rerun()
st.subheader(t("Programmation annuelle des cycles"))
if cycles:
    st.dataframe([{t("Cycle"):c["number"],t("Début"):c["start"],t("Fin"):c["end"],t("Activité physique ou sportive"):t(c["activities"][0])} for c in cycles],hide_index=True)
with st.expander(t("Ajouter ou modifier un cycle"),expanded=not cycles):
    with st.form("cycle_edit"):
        number=st.number_input(t("Cycle"),min_value=1,max_value=30,step=1)
        start=st.date_input(t("Début"),value=date.today())
        end=st.date_input(t("Fin"),value=date.today())
        choices=[a["label"] for g in registry() for a in g["activities"]]
        choice=st.selectbox(t("APS du cycle"),choices+["Autre APS"],format_func=t)
        custom=st.text_input(t("APS personnalisée (si autre)"),max_chars=100)
        activity=custom.strip() if choice=="Autre APS" else choice
        if st.form_submit_button(t("Enregistrer le cycle")):
            candidate=[c for c in cycles if c["number"]!=number]+[{"number":number,"start":start.isoformat(),"end":end.isoformat(),"activities":[activity]}]
            try:
                checked=check_journal(candidate,entries)
                validate_projects(projects,checked)
                data["journal_cycles"]=checked
            except ValueError:
                st.error(t("Cycle incompatible : vérifiez les dates, les chevauchements et les séances existantes."))
            else:
                st.rerun()
st.subheader(t("Emploi du temps hebdomadaire"))
days=("Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche")
if slots:
    st.dataframe([{t("Code du groupe (non nominatif)"):s["group"],t("Niveau"):t(s["level"]),t("Jour"):t(days[s["weekday"]]),t("Heure"):f'{s["start_minute"]//60:02d}:{s["start_minute"]%60:02d}',t("Durée (min)"):s["duration"]} for s in slots],hide_index=True)
with st.expander(t("Ajouter un créneau")):
    with st.form("journal_slot"):
        slot_group=st.text_input(t("Code du groupe (non nominatif)"),max_chars=30)
        slot_level=st.selectbox(t("Niveau"),ctx.LEVELS,format_func=t)
        weekday=st.selectbox(t("Jour"),range(7),format_func=lambda i:t(days[i]))
        hour=st.time_input(t("Heure"))
        duration=st.number_input(t("Durée (min)"),min_value=15,max_value=240,value=60,step=5)
        if st.form_submit_button(t("Enregistrer le créneau")):
            candidate=slots+[{"group":slot_group.strip(),"level":slot_level,"weekday":weekday,"start_minute":hour.hour*60+hour.minute,"duration":duration}]
            try:
                generate([],candidate,[],[])
            except ValueError:
                st.error(t("Créneau invalide ou en conflit."))
            else:
                slots[:]=candidate
                st.rerun()
    if slots:
        remove_slot=st.selectbox(t("Créneau à supprimer"),range(len(slots)),format_func=lambda i:slots[i]["group"]+" · "+t(days[slots[i]["weekday"]]))
        if st.button(t("Supprimer le créneau")):
            slots.pop(remove_slot)
            st.rerun()
with st.expander(t("Interruptions pédagogiques")):
    st.write(interruptions)
    with st.form("journal_break"):
        break_start=st.date_input(t("Début"),key="break_start")
        break_end=st.date_input(t("Fin"),key="break_end")
        if st.form_submit_button(t("Ajouter une interruption")):
            if break_start>break_end or len(interruptions)>=100:
                st.error(t("Période invalide."))
            else:
                interruptions.append([break_start.isoformat(),break_end.isoformat()])
                st.rerun()
    if interruptions:
        remove_break=st.selectbox(t("Interruption à supprimer"),range(len(interruptions)),format_func=lambda i:" – ".join(interruptions[i]))
        if st.button(t("Supprimer l’interruption")):
            interruptions.pop(remove_break)
            st.rerun()
for kind,group in timetable_warnings(slots):
    messages={"afternoon":"Horaire avant 15 h : vérifier la règle EPS.","weekly_count":"Nombre de créneaux différent de deux par semaine.","spacing":"Intervalle inférieur à 48 h entre deux séances."}
    st.warning(group+colon()+t(messages[kind])+" "+t("Avertissement non bloquant."))
st.caption(t("La génération ajoute uniquement les séances manquantes. Elle ne modifie pas les séances existantes."))
if st.button(t("Générer les séances annuelles"),disabled=not cycles or not slots):
    try:
        data["journal_entries"]=generate(cycles,slots,interruptions,entries)
    except ValueError:
        st.error(t("Génération impossible : vérifiez les créneaux et la capacité du journal."))
    else:
        st.rerun()
ctx.render_context(st,S,fields=("level","duration","objectives"))
when=st.date_input(t("Date de la séance"),value=date.today(),key="journal_day")
assigned=cycle_at(cycles,when)
if assigned:
    st.info(t("Cycle {n} : {activity}",n=assigned["number"],activity=t(assigned["activities"][0])))
else:
    st.warning(t("Aucun cycle prévu à cette date."))
with st.form("journal_add"):
    group=st.text_input(t("Code du groupe (non nominatif)"),max_chars=30)
    if st.form_submit_button(t("Planifier la séance"),disabled=len(entries)>=MAX_ENTRIES or assigned is None):
        if not group.strip():
            st.error(t("Renseignez le code du groupe."))
        elif any(e["group"]==group.strip() and e["cycle"]==assigned["number"] and e["date"]==when.isoformat() for e in entries):
            st.error(t("Une séance existe déjà pour ce groupe à cette date."))
        else:
            entries.append({"id":uuid.uuid4().hex,"date":when.isoformat(),"group":group.strip(),"activity":assigned["activities"][0],"level":ctx.get(S,"level"),"cycle":assigned["number"],"lesson":max([e["lesson"] for e in entries if e["group"]==group.strip() and e["cycle"]==assigned["number"]]+[0])+1,"duration":ctx.get(S,"duration"),"objectives":ctx.get(S,"objectives"),"status":STATUSES[0],"reflection":""})
            st.rerun()
st.subheader(t("Séances enregistrées"))
if entries:
    groups=sorted({e["group"] for e in entries})
    selected_group=st.selectbox(t("Code du groupe (non nominatif)"),[""]+groups,format_func=lambda x:x or t("Tous"),key="journal_filter")
    visible=[e for e in entries if not selected_group or e["group"]==selected_group]
    visible.sort(key=lambda e:(e["date"],e["lesson"]),reverse=True)
    st.dataframe([{t("Date"):e["date"],t("Code du groupe (non nominatif)"):e["group"],t("Activité physique ou sportive"):t(e["activity"]),t("Séance"):e["lesson"],t("Statut de la séance"):t(e["status"])} for e in visible],hide_index=True)
    selected=st.selectbox(t("Séance à consulter"),[e["id"] for e in visible],format_func=lambda k:next(e["date"]+" · "+e["group"]+" · "+t(e["activity"])+" · "+str(e["lesson"]) for e in visible if e["id"]==k))
    entry=next(e for e in visible if e["id"]==selected)
    st.write(entry["objectives"])
    with st.form("journal_edit_"+selected):
        status=st.selectbox(t("Statut de la séance"),STATUSES,index=STATUSES.index(entry["status"]),format_func=t)
        actual_date=st.date_input(t("Date"),value=date.fromisoformat(entry["date"]))
        objectives=st.text_area(t("Objectifs de la séance"),value=entry["objectives"],max_chars=800)
        reflection=st.text_area(t("Bilan pédagogique"),value=entry["reflection"],max_chars=1500)
        if st.form_submit_button(t("Enregistrer le bilan")):
            if not allows_session(cycles,actual_date,entry["cycle"],entry["activity"]):
                st.error(t("Aucun cycle compatible à cette date."))
            elif any(e["id"]!=selected and e["group"]==entry["group"] and e["date"]==actual_date.isoformat() for e in entries):
                st.error(t("Une séance existe déjà pour ce groupe à cette date."))
            else:
                entry.update(status=status,reflection=reflection,objectives=objectives,date=actual_date.isoformat())
                st.rerun()
    if st.button(t("Reprendre le contexte de la séance")):
        for key,value in (("activity",catalog_category(entry["activity"])),("activity_specialty",entry["activity"]),("level",entry["level"]),("cycle_number",entry["cycle"]),("lesson_number",entry["lesson"]),("duration",entry["duration"]),("objectives",entry["objectives"])):
            ctx.put(S,key,value)
        st.switch_page("pages/5_Studio_Pedagogique.py")
    if st.checkbox(t("Confirmer la suppression"),key="journal_delete_"+selected):
        if st.button(t("Supprimer")):
            entries.remove(entry)
            st.rerun()
    st.download_button(t("Journal (CSV)"),export_csv(visible),"journal_acpa.csv","text/csv")


st.subheader(t("Projets de cycle par classe"))
if cycles:
    profile=st.selectbox(t("Référentiel"),profiles(),format_func=lambda p:t(p["label"]),key="cp_profile")
    grades=profile["levels"]
    grade=st.selectbox(t("Niveau scolaire précis"),grades,format_func=lambda g:g["id"],key="cp_grade") if grades else None
    cycle=st.selectbox(t("Cycle"),cycles,format_func=lambda c:str(c["number"])+" · "+t(c["activities"][0]),key="cp_cycle")
    group=st.text_input(t("Code du groupe (non nominatif)"),max_chars=30,key="cp_group")
    existing=next((p for p in projects if p["group"]==group.strip() and p["cycle"]==cycle["number"]),{})
    if grade:
        source=profile["sources"][grade["source"]]
        st.caption(grade["source"]+" · "+t("Source à vérifier"))
        st.markdown("[ "+grade["source"]+" ]("+source["url"]+")")
    with st.form("cycle_project_"+str(cycle["number"])+"_"+group):
        level=grade["category"] if grade else st.selectbox(t("Niveau"),ctx.LEVELS,format_func=t)
        custom_grade=grade["id"] if grade else st.text_input(t("Niveau scolaire précis"),value=existing.get("grade",""))
        values={}
        for key,label in (("module","Module pédagogique"),("institutional","Objectifs institutionnels"),("reference","Référence précise du texte"),("diagnostic","Diagnostic initial"),("target","Objectif terminal du cycle"),("progression","Progression pédagogique"),("assessment","Critères et modalités d’évaluation")):
            values[key]=st.text_area(t(label),value=existing.get(key,""),max_chars=2000)
        if st.form_submit_button(t("Enregistrer le projet de cycle")):
            project={"group":group.strip(),"cycle":cycle["number"],"level":level,"grade":custom_grade,"profile":profile["id"],**values}
            candidate=[p for p in projects if (p["group"],p["cycle"])!=(project["group"],project["cycle"])]+[project]
            try:
                data["cycle_projects"]=validate_projects(candidate,cycles)
            except ValueError:
                st.error(t("Projet invalide : vérifiez le groupe, le niveau et les références."))
            else:
                st.rerun()
    try:
        saved=export_projects(projects,cycles)
    except ValueError:
        st.warning(t("Certains projets ne correspondent plus aux cycles actuels."))
    else:
        st.download_button(t("Sauvegarder les projets de cycle"),saved,"projets_cycles.json","application/json")
    upload=st.file_uploader(t("Restaurer les projets de cycle"),type=["json"],key="cp_upload")
    if upload is not None:
        try:
            imported=import_projects(upload.getvalue(),cycles)
        except ValueError:
            st.error(t("Fichier de sauvegarde invalide ou incompatible."))
        else:
            if st.button(t("Confirmer la restauration"),key="cp_restore"):
                data["cycle_projects"]=imported
                st.rerun()
