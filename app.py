"""ACPA/MSMDA : accueil et navigation par onglets entre les quatre tâches de l'enseignant."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.ui import APP_NAME, HOME, MODULES, PRIVACY_NOTE, TASKS, configure_page, page_header, tab_bar  # noqa: E402


def home():
    configure_page(HOME)
    page_header(HOME, title=APP_NAME, eyebrow="EPS · collège et lycée")
    st.subheader("Que voulez-vous faire ?")
    for row in (TASKS[:2], TASKS[2:]):
        for column, module in zip(st.columns(2), row):
            with column, st.container(key=f"task_{module.key}"):
                st.page_link(module.path, label=module.title, icon=module.icon, use_container_width=True)
                st.caption(module.summary)
    st.caption(PRIVACY_NOTE)


home_page = st.Page(home, title=HOME.title, icon=HOME.icon, default=True)
pages = st.navigation([home_page] + [st.Page(m.path, title=m.title, icon=m.icon) for m in MODULES if m.path],
                      position="hidden")
current = next((m.key for m in MODULES if m.title == pages.title), HOME.key)
tab_bar(current, home_page)
pages.run()
