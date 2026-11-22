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
    # Une identité visuelle mobile sans écran de connexion fictif.
    with st.container(key="home_hero"):
        st.markdown('<span class="acpa-hero-kicker">ACPA / MSMDA · EPS</span>',
                    unsafe_allow_html=True)
        st.title(APP_NAME)
        st.markdown('<p class="acpa-hero-line">De l’idée à la séance.</p>',
                    unsafe_allow_html=True)
        st.caption(HOME.summary)

    st.subheader("Que voulez-vous faire ?")
    st.caption("Choisissez un parcours pour commencer.")
    # Quatre liens natifs : clavier, lecteur d’écran et navigation Streamlit conservés.
    for module in TASKS:
        with st.container(key=f"task_{module.key}"):
            st.page_link(module.path, label=module.title, icon=module.icon, use_container_width=True)
            st.caption(module.summary)
    st.caption(PRIVACY_NOTE)


pages = st.navigation(
    [st.Page(home, title=HOME.title, icon=HOME.icon, default=True)]
    + [st.Page(m.path, title=m.title, icon=m.icon) for m in MODULES if m.path],
    position="top",
)
pages.run()
