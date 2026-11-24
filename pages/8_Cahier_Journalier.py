"""Cahier journalier : planifier, retrouver et documenter les séances."""
import sys
import uuid
from pathlib import Path
from datetime import date
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.journal import STATUSES, MAX_ENTRIES, cycle_backup, restore_cycles, export_csv
from acpa_msmda.cycle_plan import check_journal, cycle_at, allows_session
from acpa_msmda.i18n import t
from acpa_msmda.ui import JOURNAL, configure_page, page_header, PRIVACY_NOTE

S=st.session_state
configure_page(JOURNAL)
page_header(JOURNAL,PRIVACY_NOTE)
data=ctx.store(S)
entries=data.setdefault("journal_entries",[])
cycles=data.setdefault("journal_cycles",[])
st.caption(t("Le journal reste en mémoire de session. Téléchargez une sauvegarde pour le conserver."))
with st.expander(t("Sauvegarder ou restaurer le journal")):
    st.download_button(t("Télécharger la sauvegarde (JSON)"),cycle_backup(cycles,entries),"journal_acpa.json","application/json")
    uploaded=st.file_uploader(t("Restaurer une sauvegarde JSON"),type=["json"],key="journal_upload")
    if uploaded is not None:
        try:
            restored_cycles,restored=restore_cycles(uploaded.getvalue())
        except ValueError:
            st.error(t("Fichier de sauvegarde invalide ou incompatible."))
        else:
            st.warning(t("La restauration remplacera le journal actuel."))
            if st.button(t("Confirmer la restauration"),key="journal_restore"):
                data["journal_cycles"]=restored_cycles
                data["journal_entries"]=restored
                st.rerun()
st.subheader(t("Programmation annuelle des cycles"))
if cycles:
    st.dataframe([{t("Cycle"):c["number"],t("Début"):c["start"],t("Fin"):c["end"],t("Activité physique ou sportive"):t(c["activities"][0])} for c in cycles],hide_index=True)
with st.expander(t("Ajouter ou modifier un cycle"),expanded=not cycles):
    with st.form("cycle_edit"):
        number=st.number_input(t("Cycle"),min_value=1,max_value=30,step=1)
        start=st.date_input(t("Début"),value=date.today())
        end=st.date_input(t("Fin"),value=date.today())
        activity=st.selectbox(t("Activité physique ou sportive"),ctx.APS,format_func=t)
        if st.form_submit_button(t("Enregistrer le cycle")):
            candidate=[c for c in cycles if c["number"]!=number]+[{"number":number,"start":start.isoformat(),"end":end.isoformat(),"activities":[activity]}]
            try:
                data["journal_cycles"]=check_journal(candidate,entries)
            except ValueError:
                st.error(t("Cycle incompatible : vérifiez les dates, les chevauchements et les séances existantes."))
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
        reflection=st.text_area(t("Bilan pédagogique"),value=entry["reflection"],max_chars=1500)
        if st.form_submit_button(t("Enregistrer le bilan")):
            if not allows_session(cycles,actual_date,entry["cycle"],entry["activity"]):
                st.error(t("Aucun cycle compatible à cette date."))
            elif any(e["id"]!=selected and e["group"]==entry["group"] and e["date"]==actual_date.isoformat() for e in entries):
                st.error(t("Une séance existe déjà pour ce groupe à cette date."))
            else:
                entry.update(status=status,reflection=reflection,date=actual_date.isoformat())
                st.rerun()
    if st.button(t("Reprendre le contexte de la séance")):
        for key,value in (("activity",entry["activity"]),("level",entry["level"]),("cycle_number",entry["cycle"]),("lesson_number",entry["lesson"]),("duration",entry["duration"]),("objectives",entry["objectives"])):
            ctx.put(S,key,value)
        st.switch_page("pages/5_Studio_Pedagogique.py")
    if st.checkbox(t("Confirmer la suppression"),key="journal_delete_"+selected):
        if st.button(t("Supprimer")):
            entries.remove(entry)
            st.rerun()
    st.download_button(t("Journal (CSV)"),export_csv(visible),"journal_acpa.csv","text/csv")
