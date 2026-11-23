"""ACPA/MSMDA : accueil et navigation par onglets entre les quatre tâches de l'enseignant."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import i18n  # noqa: E402
from acpa_msmda.i18n import t  # noqa: E402
from acpa_msmda.ui import (APP_NAME, HOME, MODULES, PRIVACY_NOTE, TASKS, configure_page,  # noqa: E402
                           language_buttons, page_header, tab_bar)


def choose_language():
    """Premier écran : choix de la langue, dans les trois langues à la fois."""
    page_header(HOME, title=APP_NAME, eyebrow="EPS · collège et lycée", tagline="De l’idée à la séance.")
    st.subheader("Choisissez votre langue · اختر لغتك · Choose your language")
    language_buttons("first", primary=True)


def home():
    configure_page(HOME)
    if i18n.from_session(st.session_state, st.query_params) is None:
        choose_language()
        return
    page_header(HOME, title=APP_NAME, eyebrow="EPS · collège et lycée", tagline="De l’idée à la séance.")
    st.subheader(t("Que voulez-vous faire ?"))
    st.caption(t("Choisissez un parcours pour commencer."))
    for row in (TASKS[:2], TASKS[2:]):
        for column, module in zip(st.columns(2), row):
            with column, st.container(key=f"task_{module.key}"):
                # Deux blocs côte à côte : le pictogramme, puis le texte (titre + description).
                # La carte les aligne au centre : le pictogramme est centré sur tout le texte.
                st.markdown(module.icon)
                with st.container(key=f"tasktext_{module.key}"):
                    st.page_link(module.path, label=t(module.title), use_container_width=True)
                    st.caption(t(module.summary))
    st.caption(t(PRIVACY_NOTE))
    st.caption(t("Langue"))
    language_buttons("switch")


i18n.use(i18n.from_session(st.session_state, st.query_params) or i18n.DEFAULT)
home_page = st.Page(home, title=t(HOME.title), icon=HOME.icon, default=True)
pages = st.navigation([home_page] + [st.Page(m.path, title=t(m.title), icon=m.icon) for m in MODULES if m.path],
                      position="hidden")
current = next((m.key for m in MODULES if t(m.title) == pages.title), HOME.key)
if i18n.from_session(st.session_state, st.query_params) is not None or current != HOME.key:
    tab_bar(current, home_page)
pages.run()
