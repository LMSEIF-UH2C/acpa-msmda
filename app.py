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
from acpa_msmda.ui import (APP_NAME, HOME, MODULES, FIELD, FORMATIVE, JOURNAL, PRIVACY_NOTE, configure_page,  # noqa: E402
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
    paths = (
        ("prepare", "Préparer une séance", "Phases, activités, supports et critères de réussite.", ":material/edit_note:", "pages/5_Studio_Pedagogique.py"),
        ("assess", "Évaluer une classe", "Saisir des résultats et suivre une progression.", ":material/monitoring:", "pages/2_Performance_Lab.py"),
        ("find", "Trouver un outil", "Des outils adaptés à votre activité et à vos contraintes.", ":material/search:", "pages/4_Technologies_Reelles.py"),
        ("offline", "Préparer une séance sans connexion", "Préparer des activités réalisables sans Internet sur le terrain.", ":material/wifi_off:", "pages/5_Studio_Pedagogique.py"),
    )
    for start in (0, 2):
        for column, (key, label, description, icon, target) in zip(st.columns(2), paths[start:start+2]):
            with column:
                if st.button(t(label), key="guided_" + key, icon=icon, use_container_width=True):
                    ctx.put(st.session_state, "guided_path", key)
                    if key == "offline":
                        ctx.put(st.session_state, "connectivity", "Aucune")
                    st.switch_page(target)
                st.caption(t(description))
    st.page_link("pages/3_Espace_Enseignant.py", label=t("Organiser les ateliers"), icon=":material/groups:")
    if st.button(t("Mode terrain"), icon=FIELD.icon, use_container_width=True, key="field_entry"):
        st.switch_page(FIELD.path)
    st.page_link(FORMATIVE.path, label=t(FORMATIVE.title), icon=FORMATIVE.icon)
    if st.button(t(JOURNAL.title), icon=JOURNAL.icon, key="journal_entry", use_container_width=True):
        st.switch_page(JOURNAL.path)
    st.caption(t("La préparation sans connexion concerne le terrain ; cette application hébergée nécessite Internet."))
    st.caption(t(PRIVACY_NOTE))
    st.caption(t("Langue"))
    language_buttons("switch")


i18n.use(i18n.from_session(st.session_state, st.query_params) or i18n.DEFAULT)
home_page = st.Page(home, title=t(HOME.title), icon=HOME.icon, default=True)
pages = st.navigation([home_page] + [st.Page(m.path, title=t(m.title), icon=m.icon) for m in (*MODULES, FIELD, FORMATIVE, JOURNAL) if m.path],
                      position="hidden")
current = next((m.key for m in (*MODULES, FIELD, FORMATIVE, JOURNAL) if t(m.title) == pages.title), HOME.key)
if i18n.from_session(st.session_state, st.query_params) is not None or current != HOME.key:
    tab_bar(current, home_page)
pages.run()
