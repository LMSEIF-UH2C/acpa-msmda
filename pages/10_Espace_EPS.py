import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.ui import EPS_SPACE,JOURNAL,PLANNER,FIELD,FORMATIVE,LAB,configure_page,page_header
from acpa_msmda.i18n import t
configure_page(EPS_SPACE)
page_header(EPS_SPACE)
for m in (JOURNAL,PLANNER,FIELD,FORMATIVE,LAB):
    if st.button(t(m.title), key="eps_"+m.key, icon=m.icon, use_container_width=True):
        st.switch_page(m.path)
    st.caption(t(m.summary))
st.caption(t("Les compagnons vidéo et hors ligne restent expérimentaux."))
