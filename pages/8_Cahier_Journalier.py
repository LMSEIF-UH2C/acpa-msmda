"""Cahier journalier : planifier, retrouver et documenter les séances."""
import sys
import uuid
from pathlib import Path
from datetime import date
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.journal import STATUSES, MAX_ENTRIES, backup, restore, export_csv
from acpa_msmda.i18n import t
from acpa_msmda.ui import JOURNAL, configure_page, page_header, PRIVACY_NOTE

S=st.session_state
configure_page(JOURNAL)
page_header(JOURNAL,PRIVACY_NOTE)
data=ctx.store(S)
entries=data.setdefault("journal_entries",[])
st.caption(t("Le journal reste en mémoire de session. Téléchargez une sauvegarde pour le conserver."))
with st.expander(t("Sauvegarder ou restaurer le journal")):
    st.download_button(t("Télécharger la sauvegarde (JSON)"),backup(entries),"journal_acpa.json","application/json")
    uploaded=st.file_uploader(t("Restaurer une sauvegarde JSON"),type=["json"],key="journal_upload")
    if uploaded is not None:
        try:
            restored=restore(uploaded.getvalue())
        except ValueError:
            st.error(t("Fichier de sauvegarde invalide ou incompatible."))
        else:
            st.warning(t("La restauration remplacera le journal actuel."))
            if st.button(t("Confirmer la restauration"),key="journal_restore"):
                data["journal_entries"]=restored
                st.rerun()
ctx.render_context(st,S,fields=("activity","level","class_size","duration","cycle_number","lesson_number","objectives"))
with st.form("journal_add"):
    when=st.date_input(t("Date"),value=date.today())
    group=st.text_input(t("Code du groupe (non nominatif)"),max_chars=30)
    if st.form_submit_button(t("Planifier la séance"),disabled=len(entries)>=MAX_ENTRIES):
        if not group.strip():
            st.error(t("Renseignez le code du groupe."))
        else:
            entries.append({"id":uuid.uuid4().hex,"date":when.isoformat(),"group":group.strip(),"activity":ctx.get(S,"activity"),"level":ctx.get(S,"level"),"cycle":ctx.get(S,"cycle_number"),"lesson":ctx.get(S,"lesson_number"),"duration":ctx.get(S,"duration"),"objectives":ctx.get(S,"objectives"),"status":STATUSES[0],"reflection":""})
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
