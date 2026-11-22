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
/* ACPA/MSMDA · Electric Blue. Pure presentation: no application logic changed. */
:root {
  --acpa-ink:#142348;
  --acpa-blue:#1552f8;
  --acpa-blue-dark:#0831ca;
  --acpa-muted:#5b6885;
  --acpa-stroke:#e2e8f6;
  --acpa-surface:#ffffff;
}
html {scroll-behavior:smooth}
.stApp {background:linear-gradient(180deg,#f2f6ff 0,#fbfcff 350px,#fff 780px)}
.block-container {padding-top:1.5rem;padding-bottom:3.5rem;max-width:860px}
h1,h2,h3 {letter-spacing:-.035em;color:var(--acpa-ink)}
h1 {font-size:clamp(1.8rem,5.6vw,2.35rem)!important;font-weight:780!important}
h2,h3 {font-weight:740!important}
p,li,label {line-height:1.55}
div[data-testid="stCaptionContainer"] {color:var(--acpa-muted)}
a {text-underline-offset:.2rem}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible {
  outline:3px solid #83a8ff!important;outline-offset:2px!important
}
/* Hero intentionally limited to home; internal tools stay light and legible. */
div[class*="st-key-home_hero"] {
  background:radial-gradient(ellipse at 82% 8%,#6892ff80 0,transparent 38%),
             radial-gradient(ellipse at 7% 90%,#031d88 0,transparent 58%),
             linear-gradient(140deg,#245eff 0%,#0533ed 55%,#061b9a 100%);
  border:1px solid #5078ff;
  border-radius:28px;
  padding:clamp(1.4rem,5vw,2.35rem);
  box-shadow:0 16px 40px #183c9d2b,inset 0 1px 0 #ffffff50;
  margin:.15rem 0 1.75rem;
}
div[class*="st-key-home_hero"] h1 {
  color:#fff!important;
  font-size:clamp(2.25rem,9vw,3.65rem)!important;
  font-weight:800!important;
  letter-spacing:-.06em
}
div[class*="st-key-home_hero"] div[data-testid="stCaptionContainer"] {
  color:#dce7ff!important;font-size:.9rem
}
.acpa-hero-kicker {
  display:inline-flex;align-items:center;
  color:#f0f4ff;font-size:.73rem;font-weight:750;
  letter-spacing:.13em;text-transform:uppercase;
  border:1px solid #ffffff55;background:#ffffff17;
  border-radius:999px;padding:.4rem .8rem;
}
.acpa-hero-line {
  color:#fff;font-size:clamp(1.05rem,3.6vw,1.25rem);
  font-weight:520;letter-spacing:-.02em;margin:0 0 .55rem
}
/* Mobile-friendly task list: actual native links, never fake buttons. */
div[class*="st-key-task_"] {
  border-bottom:1px solid var(--acpa-stroke);
  padding:.45rem .35rem .65rem;
  transition:background-color .18s ease,padding-left .18s ease;
}
div[class*="st-key-task_"]:hover {background:#eef3ff;padding-left:.65rem}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] {
  min-height:2.8rem;
  padding:.35rem .1rem;border:0!important;
  border-radius:0;background:transparent!important;
}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] p {
  color:var(--acpa-ink);font-size:1.07rem;font-weight:720
}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]:hover p {color:var(--acpa-blue)}
div[class*="st-key-task_"] div[data-testid="stCaptionContainer"] {
  margin-top:-.48rem;padding-left:2rem;font-size:.87rem
}
/* Consistent controls across the four practical modules. */
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button,
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stLinkButton"] a {
  min-height:3rem;border-radius:999px;font-weight:650;
  border-color:#cdd9fa;transition:box-shadow .18s ease,transform .18s ease
}
div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
  box-shadow:0 5px 15px #1552f822;transform:translateY(-1px)
}
button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] {
  background:linear-gradient(105deg,#316dff,#0b39d9)!important;
  color:#fff!important;border-color:#2458ed!important
}
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
  border-radius:14px;border-color:#d5def1
}
div[data-testid="stExpander"] details {
  border:1px solid var(--acpa-stroke);
  border-radius:18px;background:var(--acpa-surface);
  box-shadow:0 3px 16px #173c8d0a;overflow:hidden
}
div[data-testid="stTabs"] button {font-weight:650}
div[data-testid="stAlert"] {border-radius:14px}
div[data-testid="stDataFrame"] {max-width:100%}
hr {border-color:var(--acpa-stroke)}
/* Hide only developer furniture; retain user navigation and app status. */
#MainMenu,footer,[data-testid="stDecoration"] {visibility:hidden;height:0}
@media(max-width:640px) {
  .block-container {padding-left:1rem;padding-right:1rem;padding-top:1.1rem}
  div[class*="st-key-home_hero"] {border-radius:24px;margin-bottom:1.35rem}
  div[class*="st-key-task_"] div[data-testid="stCaptionContainer"] {padding-left:1.85rem}
  div[data-testid="stHorizontalBlock"] {gap:.65rem}
  div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button {
    min-height:3rem
  }
}
@media(prefers-reduced-motion:reduce) {
  *,*::before,*::after {transition:none!important;animation:none!important;scroll-behavior:auto!important}
}
</style>
"""


def configure_page(module: Module) -> None:
    """Titre d'onglet, icône et styles communs. À appeler en tête de chaque page."""
    import streamlit as st

    st.set_page_config(page_title=f"{module.title} | {APP_NAME}", page_icon=module.icon,
                       layout="centered")
    st.markdown(_CSS, unsafe_allow_html=True)
