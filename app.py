"""ACPA/MSMDA — accueil : accès direct aux quatre tâches de l'enseignant."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.ui import APP_NAME, HOME, MODULES, PRIVACY_NOTE, TASKS, configure_page  # noqa: E402


def home():
    configure_page(HOME)
    st.title(APP_NAME)
    st.caption(HOME.summary)
    st.subheader("Que voulez-vous faire ?")
    for row in (TASKS[:2], TASKS[2:]):
        columns = st.columns(2)
        for column, module in zip(columns, row):
            with column:
                if st.button(module.title, icon=module.icon, key=f"go_{module.key}",
                             use_container_width=True):
                    st.switch_page(module.path)
                st.caption(module.summary)
    st.caption(PRIVACY_NOTE)


pages = st.navigation(
    [st.Page(home, title=HOME.title, icon=HOME.icon, default=True)]
    + [st.Page(m.path, title=m.title, icon=m.icon) for m in MODULES if m.path],
    position="sidebar",
)
pages.run()
