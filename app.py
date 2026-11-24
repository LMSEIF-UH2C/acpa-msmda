"""ACPA/MSMDA : accueil et navigation par onglets entre les quatre tâches de l'enseignant."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx
from acpa_msmda import i18n  # noqa: E402
from acpa_msmda.i18n import t  # noqa: E402
from acpa_msmda.ui import (APP_NAME, HOME, MODULES, ALL_MODULES, TECH_EVAL, EPS_SPACE, SEARCH, STUDIO, PRIVACY_NOTE, configure_page,  # noqa: E402
                           language_buttons, page_header, tab_bar)


def choose_language():
    """Premier écran : choix de la langue, dans les trois langues à la fois."""
    page_header(HOME, title=APP_NAME, eyebrow="Technologies numériques · EPS", tagline="De la technologie à l’apprentissage.")
    st.subheader("Choisissez votre langue · اختر لغتك · Choose your language")
    language_buttons("first", primary=True)


def home():
    configure_page(HOME)
    if i18n.from_session(st.session_state, st.query_params) is None:
        choose_language()
        return
    page_header(HOME, title=APP_NAME, eyebrow="Technologies numériques · EPS", tagline="De la technologie à l’apprentissage.")
    st.subheader(t("Que voulez-vous faire ?"))
    st.caption(t("Choisissez un parcours pour commencer."))
    paths = (
        ("evaluate", TECH_EVAL, "Évaluer une technologie", "Consulter les critères et les évaluations documentées."),
        ("find", SEARCH, "Trouver une technologie adaptée", "Des outils adaptés à votre activité et à vos contraintes."),
        ("prepare", STUDIO, "Concevoir un scénario pédagogique", "Phases, activités, supports et critères de réussite."),
    )
    for key, module, label, description in paths:
        with st.container(border=True, key="core_"+key):
            if st.button(t(label), key="guided_"+key, icon=module.icon, use_container_width=True):
                ctx.put(st.session_state, "guided_path", key)
                st.switch_page(module.path)
            st.caption(t(description))
    st.subheader(t("Espace EPS"))
    st.page_link(EPS_SPACE.path,label=t(EPS_SPACE.title),icon=EPS_SPACE.icon)
    st.caption(t(EPS_SPACE.summary))
    st.caption(t(PRIVACY_NOTE))
    st.caption(t("Langue"))
    language_buttons("switch")


i18n.use(i18n.from_session(st.session_state, st.query_params) or i18n.DEFAULT)
home_page = st.Page(home, title=t(HOME.title), icon=HOME.icon, default=True)
pages = st.navigation([home_page] + [st.Page(m.path, title=t(m.title), icon=m.icon) for m in ALL_MODULES if m.path],
                      position="hidden")
current = next((m.key for m in ALL_MODULES if t(m.title) == pages.title), HOME.key)
if i18n.from_session(st.session_state, st.query_params) is not None or current != HOME.key:
    tab_bar(current, home_page)
pages.run()
