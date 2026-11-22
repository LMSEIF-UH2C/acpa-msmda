"""Identité visuelle et vocabulaire communs à toutes les pages de l'application.

Un seul endroit définit le nom, l'icône, le libellé court et le fichier de chaque module :
la barre d'onglets, les cartes de l'accueil et les en-têtes de page restent ainsi identiques.
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
    short: str = ""


APP_NAME = "ACPA/MSMDA"

HOME = Module("home", "Accueil", ":material/home:", None,
              "Préparer, organiser et enrichir vos séances d'EPS.", "Accueil")
SEARCH = Module("search", "Trouver une technologie", ":material/search:",
                "pages/4_Technologies_Reelles.py",
                "Des outils adaptés à votre activité et à vos contraintes.", "Outils")
STUDIO = Module("studio", "Concevoir une séance", ":material/edit_note:",
                "pages/5_Studio_Pedagogique.py",
                "Phases, activités, supports et critères de réussite.", "Séance")
PLANNER = Module("planner", "Organiser les ateliers", ":material/groups:",
                 "pages/3_Espace_Enseignant.py",
                 "Groupes, rotations et temps de séance.", "Ateliers")
LAB = Module("lab", "Mesurer et analyser", ":material/monitoring:",
             "pages/2_Performance_Lab.py",
             "Saisir des résultats et suivre une progression.", "Mesures")

# Ordre d'affichage dans la barre d'onglets et sur l'accueil.
MODULES = (HOME, SEARCH, STUDIO, PLANNER, LAB)
TASKS = (SEARCH, STUDIO, PLANNER, LAB)

PRIVACY_NOTE = "N'indiquez ni nom ni identifiant d'élève."

# Feuille de style unique. Police système (San Francisco sur iPhone) : aucun chargement réseau,
# rendu natif et fonctionnement hors connexion. Les animations respectent « réduire les animations ».
_CSS = """
<style>
:root{
  --blue:#1552F8; --blue-2:#3D6BFF; --sky:#22B8F0; --violet:#6D4AFF;
  --ink:#142348; --muted:#56647F; --line:#E3E8F6; --card:#FFFFFF; --bg:#F5F7FF;
  --radius:18px; --shadow:0 1px 2px rgba(11,21,51,.05),0 8px 24px rgba(27,68,245,.08);
  --font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
html,body,.stApp,[data-testid="stAppViewContainer"],button,input,textarea,select,
h1,h2,h3,h4,p,li,label,input,textarea,[data-baseweb="select"] div,[data-baseweb="tab"] p{font-family:var(--font)!important}
.stApp{background:
  radial-gradient(1200px 520px at 15% -10%,rgba(61,107,255,.16),transparent 60%),
  radial-gradient(900px 480px at 110% 0%,rgba(34,184,240,.14),transparent 55%),var(--bg)}
[data-testid="stHeader"]{background:transparent;height:0}
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stAppDeployButton"],#MainMenu,footer{display:none!important}
p,li,label{line-height:1.55}
/* Focus clavier toujours visible */
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,[role="tab"]:focus-visible,summary:focus-visible{
  outline:3px solid #83A8FF!important;outline-offset:2px!important}
.block-container,[data-testid="stMainBlockContainer"]{max-width:880px;padding-top:calc(1rem + env(safe-area-inset-top));
  padding-bottom:calc(7rem + env(safe-area-inset-bottom))}
h1,h2,h3{color:var(--ink);letter-spacing:-.02em}
h2{font-size:1.35rem!important;font-weight:700!important}
h3{font-size:1.12rem!important;font-weight:650!important}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)}
[data-testid="stHeadingWithActionElements"] a{display:none}

/* En-tête de page : bandeau lumineux */
.st-key-hero{position:relative;overflow:hidden;border-radius:26px;padding:1.4rem 1.35rem 1.25rem;
  margin:.25rem 0 1.1rem;color:#fff;
  background:radial-gradient(420px 220px at 95% -25%,rgba(34,184,240,.55),transparent 62%),
             radial-gradient(360px 200px at 88% -10%,rgba(255,255,255,.28),transparent 60%),
             linear-gradient(130deg,#0F33D8 0%,var(--blue) 45%,#1A66D6 100%);
  background-size:160% 160%;animation:glow 14s ease-in-out infinite alternate;
  box-shadow:0 14px 34px rgba(27,68,245,.28)}
.st-key-hero h1{color:#fff!important;font-size:clamp(1.55rem,6.4vw,2.2rem)!important;font-weight:750!important;
  line-height:1.15;padding:0!important;margin:0}
.st-key-hero [data-testid="stCaptionContainer"],.st-key-hero [data-testid="stCaptionContainer"] p{
  color:#fff!important;font-size:.98rem}
.st-key-hero .tagline{color:#fff;font-size:clamp(1.05rem,3.6vw,1.25rem);font-weight:560;letter-spacing:-.02em;margin:.15rem 0 .35rem}
.st-key-hero .eyebrow{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;color:rgba(255,255,255,.85);background:rgba(255,255,255,.16);
  border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:.22rem .65rem;margin-bottom:.35rem}
@keyframes glow{from{background-position:0% 40%}to{background-position:100% 60%}}

/* Cartes de l'accueil : toute la carte est cliquable */
div[class*="st-key-task_"]{position:relative;background:var(--card);border:1px solid var(--line);
  border-radius:var(--radius);padding:1rem 1rem .85rem;box-shadow:var(--shadow);
  transition:transform .18s ease,box-shadow .18s ease}
div[class*="st-key-task_"]:hover{transform:translateY(-2px);box-shadow:0 2px 4px rgba(11,21,51,.06),0 16px 34px rgba(27,68,245,.14)}
div[class*="st-key-task_"]:active{transform:scale(.985)}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]{padding:0;background:none!important;gap:.8rem}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]::after{content:"";position:absolute;inset:0;border-radius:var(--radius)}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]>span:last-child{padding-left:.75rem}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] p{font-size:1.06rem;font-weight:680;color:var(--ink)}
div[class*="st-key-task_"] [data-testid="stIconMaterial"]{box-sizing:content-box!important;width:1.4rem!important;height:1.4rem!important;padding:.6rem;flex:0 0 auto;display:inline-flex!important;align-items:center;justify-content:center;line-height:1!important;overflow:visible!important;
  border-radius:14px;color:#fff!important;font-size:1.35rem!important;
  background:linear-gradient(135deg,#0F33D8 0%,var(--blue) 50%,#1A66D6 100%);
  box-shadow:0 6px 14px rgba(27,68,245,.28)}
div[class*="st-key-task_"] [data-testid="stCaptionContainer"]{padding-left:2.95rem;padding-right:1.6rem;margin-top:-.7rem}
div[class*="st-key-task_"] [data-testid="stCaptionContainer"] p{font-size:.92rem;line-height:1.35}
div[class*="st-key-task_"]::after{content:"chevron_right";font-family:"Material Symbols Rounded";position:absolute;
  right:1rem;top:1.25rem;font-size:1.4rem;color:#9AA6C4}

/* Boutons : pilule bleue pour l'action principale, blanche arrondie pour les autres */
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"],
[data-testid="stDownloadButton"] button,[data-testid="stBaseButton-link"],[data-testid="stLinkButton"] a{min-height:3rem;border-radius:999px!important;
  font-weight:620!important;transition:transform .12s ease,box-shadow .18s ease,background .18s ease}
[data-testid="stBaseButton-primary"]{border:0!important;color:#fff!important;
  background:linear-gradient(120deg,#0F33D8 0%,var(--blue) 55%,#2A5EF5 100%)!important;
  box-shadow:0 8px 20px rgba(27,68,245,.30)}
[data-testid="stBaseButton-primary"]:hover{box-shadow:0 10px 26px rgba(27,68,245,.38)}
[data-testid="stBaseButton-secondary"],[data-testid="stDownloadButton"] button,[data-testid="stLinkButton"] a{background:#fff!important;
  color:var(--blue)!important;border:1px solid var(--line)!important;box-shadow:0 2px 8px rgba(11,21,51,.06)}
[data-testid="stBaseButton-secondary"]:hover,[data-testid="stDownloadButton"] button:hover{border-color:var(--blue-2)!important}
[data-testid="stBaseButton-primary"]:active,[data-testid="stBaseButton-secondary"]:active,
[data-testid="stDownloadButton"] button:active{transform:scale(.97)}
button:disabled{opacity:.45}

/* Champs : arrondis, fond clair, anneau bleu au focus ; 16 px pour éviter le zoom automatique d'iOS */
input,textarea,[data-baseweb="select"] div{font-size:16px!important}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div,[data-testid="stDateInputField"]{
  border-radius:14px!important;background:#F4F6FD!important;border:1px solid transparent!important}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{
  border-color:var(--blue-2)!important;box-shadow:0 0 0 4px rgba(61,107,255,.14)}
[data-testid="stWidgetLabel"] p{font-weight:600;color:var(--ink)}

/* Cartes : volets, alertes, tableaux */
[data-testid="stExpander"] details{background:var(--card);border:1px solid var(--line)!important;border-radius:var(--radius);
  box-shadow:var(--shadow);overflow:hidden}
[data-testid="stExpander"] summary{padding:.85rem 1rem;font-weight:620}
[data-testid="stExpander"] summary:hover{color:var(--blue)}
[data-testid="stAlert"]>div{border-radius:16px}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:var(--radius)}

/* Onglets façon contrôle segmenté */
[data-testid="stTabs"] [role="tablist"]{gap:.25rem;background:#E9EEFB;border-radius:999px;padding:.25rem;border:0}
[data-testid="stTabs"] [role="tab"]{border-radius:999px;padding:.45rem 1rem;min-height:2.5rem;border:0}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#fff;box-shadow:0 2px 8px rgba(11,21,51,.10)}
[data-testid="stTabs"] [role="tab"] p{font-weight:620}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"]{display:none}

/* Curseurs et interrupteurs */
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 6px rgba(61,107,255,.18)}

/* Barre d'onglets fixe, façon application iPhone */
.st-key-tabbar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(.6rem + env(safe-area-inset-bottom));
  z-index:999;width:min(560px,calc(100% - 1.2rem));background:rgba(255,255,255,.94);
  -webkit-backdrop-filter:saturate(180%) blur(18px);backdrop-filter:saturate(180%) blur(18px);
  border:1px solid rgba(227,232,246,.9);border-radius:24px;padding:.3rem .35rem;
  box-shadow:0 10px 30px rgba(11,21,51,.14)}
.st-key-tabbar [data-testid="stHorizontalBlock"]{gap:0!important;flex-wrap:nowrap!important}
.st-key-tabbar [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important;width:auto!important}
.st-key-tabbar a[data-testid="stPageLink-NavLink"]{flex-direction:column;justify-content:center;gap:.1rem;
  padding:.35rem .1rem;border-radius:18px;min-height:3rem;background:none!important}
.st-key-tabbar a[data-testid="stPageLink-NavLink"] p{font-size:.7rem;font-weight:600;color:#5E6A88;white-space:nowrap}
.st-key-tabbar [data-testid="stIconMaterial"]{color:#5E6A88!important;font-size:1.35rem!important}
.st-key-tabbar [class*="st-key-tab_active"] a[data-testid="stPageLink-NavLink"]{background:rgba(27,68,245,.10)!important}
.st-key-tabbar [class*="st-key-tab_active"] p,.st-key-tabbar [class*="st-key-tab_active"] [data-testid="stIconMaterial"]{color:var(--blue)!important}
[data-testid="stSidebar"],[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"]{display:none!important}

/* Apparition douce du contenu */
[data-testid="stMainBlockContainer"]>div>div>div{animation:rise .35s ease both}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
@media (max-width:640px){
  .block-container,[data-testid="stMainBlockContainer"]{padding-left:.95rem;padding-right:.95rem}
  .st-key-hero{border-radius:22px;padding:1.2rem 1.1rem 1.05rem}
}
</style>
"""


def configure_page(module: Module) -> None:
    """Titre d'onglet, icône et feuille de style. À appeler en tête de chaque page."""
    import streamlit as st

    st.set_page_config(page_title=f"{module.title} | {APP_NAME}", page_icon=module.icon,
                       layout="centered", initial_sidebar_state="collapsed")
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(module: Module, note: str | None = None, title: str | None = None,
                eyebrow: str = APP_NAME, tagline: str | None = None) -> None:
    """Bandeau d'en-tête lumineux : nom de l'application, titre du module et sa description."""
    import streamlit as st

    with st.container(key="hero"):
        st.markdown(f'<span class="eyebrow">{eyebrow}</span>', unsafe_allow_html=True)
        st.title(title or module.title)
        if tagline:
            st.markdown(f'<p class="tagline">{tagline}</p>', unsafe_allow_html=True)
        st.caption(module.summary + (" " + note if note else ""))


def tab_bar(current: str, home_page=None) -> None:
    """Barre d'onglets fixée en bas de l'écran ; l'onglet de la page affichée est mis en valeur."""
    import streamlit as st

    with st.container(key="tabbar"):
        for column, module in zip(st.columns(len(MODULES)), MODULES):
            target = home_page if module.path is None else module.path
            if target is None:
                continue
            state = "active" if module.key == current else "idle"
            with column, st.container(key=f"tab_{state}_{module.key}"):
                st.page_link(target, label=module.short, icon=module.icon, use_container_width=True)
