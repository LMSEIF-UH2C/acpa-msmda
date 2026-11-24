import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.ui import EPS_SPACE,JOURNAL,PLANNER,FIELD,FORMATIVE,LAB,configure_page,page_header
from acpa_msmda.i18n import t
configure_page(EPS_SPACE)
page_header(EPS_SPACE)
for m in (JOURNAL,PLANNER,FIELD,FORMATIVE,LAB):
    st.page_link(m.path,label=t(m.title),icon=m.icon)
    st.caption(t(m.summary))
st.caption(t("Les compagnons vidéo et hors ligne restent expérimentaux."))
