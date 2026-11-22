"""Vocabulaire et présentation communs à toutes les pages de l'application.

Un seul endroit définit le nom, l'icône et le fichier de chaque module : le menu,
les boutons de l'accueil et les titres de page restent ainsi identiques.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Module:
    key: str
    title: str
    icon: str
    path: str | None
    summary: str


APP_NAME = "ACPA/MSMDA"

HOME = Module("home", "Accueil", ":material/home:", None,
              "Préparer, organiser et enrichir vos séances d'EPS.")
SEARCH = Module("search", "Trouver une technologie", ":material/search:",
                "pages/4_Technologies_Reelles.py",
                "Des outils adaptés à votre activité et à vos contraintes.")
STUDIO = Module("studio", "Concevoir une séance", ":material/edit_note:",
                "pages/5_Studio_Pedagogique.py",
                "Phases, activités, supports et critères de réussite.")
PLANNER = Module("planner", "Organiser les ateliers", ":material/groups:",
                 "pages/3_Espace_Enseignant.py",
                 "Groupes, rotations et temps de séance.")
LAB = Module("lab", "Mesurer et analyser", ":material/monitoring:",
             "pages/2_Performance_Lab.py",
             "Saisir des résultats et suivre une progression.")

# Ordre d'affichage dans le menu et sur l'accueil.
MODULES = (HOME, SEARCH, STUDIO, PLANNER, LAB)
TASKS = (SEARCH, STUDIO, PLANNER, LAB)

PRIVACY_NOTE = "N'indiquez ni nom ni identifiant d'élève."

_CSS = """
<style>
.block-container {padding-top:1.2rem;padding-bottom:3rem;max-width:860px}
h1 {font-size:clamp(1.6rem,6vw,2.2rem)!important;letter-spacing:-.02em}
h2, h3 {letter-spacing:-.01em}
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button,
div[data-testid="stFormSubmitButton"] button {min-height:2.75rem;border-radius:8px}
div[data-testid="stExpander"] details {border-radius:8px}
/* Accès de l'accueil : lignes sobres plutôt que grands boutons encadrés */
div[class*="st-key-task_"] {border-bottom:1px solid #E3E8EC;padding:.35rem 0 .5rem}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] {padding:.35rem 0;border-radius:0}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] p {font-size:1.08rem;font-weight:600;color:#1F2933}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]:hover p {color:#2F6F8F}
div[class*="st-key-task_"] div[data-testid="stCaptionContainer"] {margin-top:-.6rem;padding-left:2rem}
/* Éléments propres à l'outil de développement, inutiles pour l'enseignant */
#MainMenu, footer, [data-testid="stDecoration"] {visibility:hidden;height:0}
@media (max-width:640px){
  .block-container {padding-left:.9rem;padding-right:.9rem}
}
</style>
"""


def configure_page(module: Module) -> None:
    """Titre d'onglet, icône et styles communs. À appeler en tête de chaque page."""
    import streamlit as st

    st.set_page_config(page_title=f"{module.title} | {APP_NAME}", page_icon=module.icon,
                       layout="centered")
    st.markdown(_CSS, unsafe_allow_html=True)
