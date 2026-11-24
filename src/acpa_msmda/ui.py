"""Identité visuelle et vocabulaire communs à toutes les pages de l'application.

Un seul endroit définit le nom, l'icône, le libellé court et le fichier de chaque module :
la barre d'onglets, les cartes de l'accueil et les en-têtes de page restent ainsi identiques.
"""
from __future__ import annotations

from dataclasses import dataclass
from base64 import b64encode
from functools import lru_cache
from pathlib import Path

from . import i18n
from .i18n import t


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
              "Évaluer, sélectionner et intégrer les technologies numériques en EPS.", "Accueil")
SEARCH = Module("search", "Technothèque", ":material/search:",
                "pages/4_Technologies_Reelles.py",
                "Trouvez les technologies adaptées à votre situation d’enseignement.", "Explorer")
STUDIO = Module("studio", "Scénarisation pédagogique", ":material/edit_note:",
                "pages/5_Studio_Pedagogique.py",
                "Intégrez les technologies dans vos situations d’apprentissage.", "Scénario")
PLANNER = Module("planner", "Organiser les ateliers", ":material/groups:",
                 "pages/3_Espace_Enseignant.py",
                 "Groupes, rotations et temps de séance.", "Ateliers")
LAB = Module("lab", "Mesurer et analyser", ":material/monitoring:",
             "pages/2_Performance_Lab.py",
             "Saisir des résultats et suivre une progression.", "Mesures")

# Ordre d'affichage dans la barre d'onglets et sur l'accueil.
FIELD = Module("field", "Mode terrain", ":material/timer:",
               "pages/6_Mode_Terrain.py", "Chronomètre, scores, compteurs et rotations.", "Terrain")
FORMATIVE = Module("formative", "Évaluation formative", ":material/assignment:",
                   "pages/7_Evaluation_Formative.py", "Observer les acquisitions à partir de critères personnalisés.", "Évaluation")
JOURNAL = Module("journal", "Cahier journalier", ":material/calendar_month:",
                 "pages/8_Cahier_Journalier.py", "Programmation cyclique et suivi des séances.", "Journal")
TECH_EVAL = Module("tech_eval", "Évaluer votre contexte", ":material/fact_check:", "pages/9_Evaluation_Technologie.py", "Analysez votre contexte et identifiez vos besoins numériques.", "Évaluer")
EPS_SPACE = Module("eps_space", "Espace EPS", ":material/apps:", "pages/10_Espace_EPS.py", "Organisez, accompagnez et suivez les apprentissages de vos élèves.", "Espace EPS")
MODULES = (HOME, TECH_EVAL, SEARCH, STUDIO, EPS_SPACE)
ALL_MODULES = (*MODULES, PLANNER, LAB, FIELD, FORMATIVE, JOURNAL)
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
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;opacity:1!important}
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
  color:#fff!important;opacity:1!important;font-size:.98rem}
.st-key-hero .tagline{color:#fff;font-size:clamp(1.05rem,3.6vw,1.25rem);font-weight:560;letter-spacing:-.02em;margin:.15rem 0 .35rem}
.st-key-hero .eyebrow{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;color:rgba(255,255,255,.85);background:rgba(255,255,255,.16);
  border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:.22rem .65rem;margin-bottom:.35rem}
@keyframes glow{from{background-position:0% 40%}to{background-position:100% 60%}}

/* Cartes de l'accueil. Structure : la carte contient deux blocs frères, le pictogramme et le bloc
   texte (titre + description). Disposés en ligne et centrés verticalement, le pictogramme est aligné
   sur l'ensemble du texte, quelle que soit la longueur de la description. Toute la carte est cliquable. */
div[class*="st-key-task_"]{position:relative;z-index:0;display:flex!important;flex-direction:row!important;
  align-items:center;gap:.75rem;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1rem 2.6rem .95rem calc(1rem - 1px);box-shadow:var(--shadow);
  transition:transform .18s ease,box-shadow .18s ease}
div[class*="st-key-task_"]>div:first-child{flex:0 0 auto;width:auto!important;position:static!important}
div[class*="st-key-tasktext_"]{flex:1 1 auto;min-width:0;gap:.2rem!important}
/* Le lien de page reçoit de Streamlit des marges négatives de -6 px en haut et en bas : il dépassait
   du bloc texte, que la carte centrait alors sur une hauteur fausse. */
div[class*="st-key-tasktext_"]>div{margin:0!important}
div[class*="st-key-task_"] *:not(a){position:static}
div[class*="st-key-task_"]:hover{transform:translateY(-2px);box-shadow:0 2px 4px rgba(11,21,51,.06),0 16px 34px rgba(27,68,245,.14)}
div[class*="st-key-task_"]:active{transform:scale(.985)}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]{padding:0;margin:0;background:none!important;min-height:0}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"]::after{content:"";position:absolute;inset:0;z-index:2;border-radius:var(--radius)}
div[class*="st-key-task_"] a[data-testid="stPageLink-NavLink"] p{font-size:1.06rem;font-weight:680;color:var(--ink);margin:0}
/* Streamlit donne aux textes Markdown une marge basse négative (-16 px) qui fausse la hauteur des
   éléments : remise à zéro pour que le centrage porte sur le vrai bloc de texte. */
div[class*="st-key-task_"] [data-testid="stMarkdownContainer"],div[class*="st-key-task_"] [data-testid="stCaptionContainer"]{margin:0!important}
div[class*="st-key-task_"]>div:first-child p{margin:0;line-height:0}
div[class*="st-key-task_"]>div:first-child span[role="img"]{box-sizing:content-box!important;
  width:1.4rem!important;height:1.4rem!important;padding:.6rem;display:inline-flex!important;align-items:center;
  justify-content:center;line-height:1!important;overflow:visible!important;vertical-align:middle;
  border-radius:14px;color:#fff!important;font-size:1.35rem!important;
  background:linear-gradient(135deg,#0F33D8 0%,var(--blue) 50%,#1A66D6 100%);
  box-shadow:0 6px 14px rgba(27,68,245,.28)}
div[class*="st-key-task_"] [data-testid="stCaptionContainer"]{padding:0;margin:0}
div[class*="st-key-task_"] [data-testid="stCaptionContainer"] p{font-size:.92rem;line-height:1.35;margin:0}
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
.st-key-tabbar a[data-testid="stPageLink-NavLink"]{
  display:flex!important;flex-direction:column!important;align-items:center!important;
  justify-content:center!important;gap:.22rem!important;
  padding:.45rem .05rem!important;border-radius:18px;min-height:3.7rem;
  height:100%;background:none!important;text-align:center
}
.st-key-tabbar a[data-testid="stPageLink-NavLink"] > span{
  display:flex!important;flex-direction:column!important;
  align-items:center!important;justify-content:center!important;
  gap:.25rem!important;width:100%!important;
  margin:0!important;padding:0!important;line-height:1!important
}
.st-key-tabbar a[data-testid="stPageLink-NavLink"] p{
  font-size:.7rem!important;line-height:1.15!important;font-weight:600;
  color:#5E6A88;white-space:normal;overflow-wrap:normal;word-break:normal;margin:0!important;text-align:center!important
}
.st-key-tabbar [data-testid="stIconMaterial"]{
  display:inline-flex!important;align-items:center!important;justify-content:center!important;
  color:#5E6A88!important;font-size:1.35rem!important;line-height:1!important;
  width:1.5rem;height:1.5rem;margin:0!important;vertical-align:middle!important
}
.st-key-tabbar [class*="st-key-tab_active"] a[data-testid="stPageLink-NavLink"]{background:rgba(27,68,245,.10)!important}
.st-key-tabbar [class*="st-key-tab_active"] p,.st-key-tabbar [class*="st-key-tab_active"] [data-testid="stIconMaterial"]{color:var(--blue)!important}
[data-testid="stSidebar"],[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"]{display:none!important}

/* Accueil : une seule surface par action, bouton natif et description solidaire. */
div[class*="st-key-core_"],.st-key-home_eps{
  position:relative;isolation:isolate;display:flex!important;flex-direction:column!important;
  align-items:stretch!important;gap:.2rem!important;height:auto!important;min-height:0!important;
  box-sizing:border-box;padding:.65rem .85rem .85rem;
  border:1px solid var(--line);border-radius:18px;background:#fff;box-shadow:var(--shadow);
}
/* Keep captions in normal flow and reset Streamlit negative margins. */
div[class*="st-key-core_"] > div,.st-key-home_eps > div,
div[class*="st-key-core_"] [data-testid="stElementContainer"],.st-key-home_eps [data-testid="stElementContainer"],
div[class*="st-key-core_"] [data-testid="stMarkdownContainer"],.st-key-home_eps [data-testid="stMarkdownContainer"],
div[class*="st-key-core_"] [data-testid="stCaptionContainer"],.st-key-home_eps [data-testid="stCaptionContainer"]{
  margin:0!important;height:auto!important;min-height:0!important;flex-shrink:0!important;box-sizing:border-box;
}
div[class*="st-key-core_"] [data-testid="stCaptionContainer"],
.st-key-home_eps [data-testid="stCaptionContainer"]{padding:0!important;overflow:visible!important}
div[class*="st-key-core_"] button[data-testid="stBaseButton-secondary"]{
  background:transparent!important;border:0!important;box-shadow:none!important;
  color:var(--ink)!important;justify-content:flex-start!important;
  border-radius:0!important;min-height:2.75rem;padding:.15rem .25rem!important;
}
div[class*="st-key-core_"] button::after,.st-key-home_eps a[data-testid="stPageLink-NavLink"]::after{
  content:"";position:absolute;inset:0;z-index:1;border-radius:18px;
}
div[class*="st-key-core_"]:focus-within,.st-key-home_eps:focus-within{
  outline:3px solid var(--blue);outline-offset:2px;
}
div[class*="st-key-core_"] button [data-testid="stIconMaterial"],
.st-key-home_eps [data-testid="stIconMaterial"]{color:var(--blue)!important}
div[class*="st-key-core_"] [data-testid="stCaptionContainer"] p,
.st-key-home_eps [data-testid="stCaptionContainer"] p{
  font-size:.88rem;line-height:1.4;margin:0!important;padding-inline-start:2rem;color:#475569!important;opacity:1!important;white-space:normal;overflow-wrap:anywhere;
}
.st-key-home_eps{box-shadow:none;background:rgba(255,255,255,.6);margin-top:.3rem}
.st-key-home_eps a[data-testid="stPageLink-NavLink"]{min-height:2.75rem;padding:.15rem .25rem}
.st-key-home_languages [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.35rem!important}
.st-key-home_languages [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important;width:auto!important}
.st-key-home_languages button{min-height:2.75rem;padding:.25rem .15rem!important;font-size:.85rem!important}
.st-key-home_languages button p{font-size:.85rem!important}
@media(max-width:640px){
  div[class*="st-key-core_"],.st-key-home_eps{padding:.45rem .75rem .85rem}
  .st-key-home_languages{margin-bottom:1.25rem}
  .block-container,[data-testid="stMainBlockContainer"]{padding-bottom:calc(9rem + env(safe-area-inset-bottom))}
}
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


# Arabe : lecture de droite à gauche. Les nombres, les dates et les saisies chiffrées restent de
# gauche à droite ; la barre d'onglets garde l'ordre des modules, lu de droite à gauche.
_RTL_CSS = """
<style>
[data-testid="stMainBlockContainer"],.st-key-tabbar{direction:rtl}
[data-testid="stMainBlockContainer"] p,[data-testid="stMainBlockContainer"] li,
[data-testid="stMainBlockContainer"] label,[data-testid="stMainBlockContainer"] h1,
[data-testid="stMainBlockContainer"] h2,[data-testid="stMainBlockContainer"] h3,
[data-testid="stMainBlockContainer"] summary,[data-testid="stCaptionContainer"]{text-align:right}
[data-testid="stMainBlockContainer"] button>span:first-child{margin:0 0 0 .5rem!important;flex-shrink:0}
[data-testid="stMainBlockContainer"] button{gap:.4rem}
[data-testid="stMainBlockContainer"] button p{text-align:center!important}
textarea,input[type="text"]{direction:rtl;text-align:right}
input[type="number"],[data-testid="stDateInputField"] input{direction:ltr;text-align:left}
div[class*="st-key-task_"]{padding:1rem calc(1rem - 1px) .95rem 2.6rem}
div[class*="st-key-task_"]::after{content:"chevron_left";right:auto;left:1rem}
[data-testid="stExpander"] summary{flex-direction:row-reverse}
ul,ol{padding-right:1.4rem;padding-left:0}
</style>
"""


@lru_cache(maxsize=2)
def arabic_font_css(mixed: bool = False) -> str:
    """Local OFL fonts; mixed mode applies Amiri only to Arabic Unicode ranges."""
    root = Path(__file__).resolve().parents[2] / "assets" / "fonts"
    faces = []
    unicode_range = "unicode-range:U+0600-06FF,U+0750-077F,U+0870-089F,U+08A0-08FF,U+FB50-FDFF,U+FE70-FEFF;" if mixed else ""
    for weight, name in ((400, "Amiri-Regular.ttf"), (700, "Amiri-Bold.ttf")):
        try:
            encoded = b64encode((root / name).read_bytes()).decode("ascii")
        except OSError:
            continue
        faces.append(f"@font-face{{font-family:Amiri;src:url(data:font/ttf;base64,{encoded}) format('truetype');font-weight:{weight};font-display:swap;{unicode_range}}}")
    if mixed:
        return "<style>" + "".join(faces) + '\n[data-testid="stMainBlockContainer"]{--font:Amiri,-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}\n</style>'
    return "<style>" + "".join(faces) + """
[data-testid="stMainBlockContainer"],.st-key-tabbar{--font:Amiri,"Geeza Pro","Noto Naskh Arabic",Arial,sans-serif}
[data-testid="stMainBlockContainer"] p,[data-testid="stMainBlockContainer"] li,
[data-testid="stMainBlockContainer"] label,[data-testid="stMainBlockContainer"] summary{
 font-size:1.15rem;line-height:1.65;letter-spacing:0}
[data-testid="stMainBlockContainer"] h1,[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3{letter-spacing:0;line-height:1.5}
[data-testid="stMainBlockContainer"] input,[data-testid="stMainBlockContainer"] textarea{font-size:19px!important}
.st-key-hero .eyebrow{font-family:Amiri,Arial,sans-serif;letter-spacing:0;font-size:.95rem}
.st-key-hero .tagline{font-size:1.3rem}
.st-key-hero [data-testid="stCaptionContainer"] p{font-size:1.15rem}
div[class*="st-key-core_"] [data-testid="stCaptionContainer"] p,
.st-key-home_eps [data-testid="stCaptionContainer"] p{font-size:1.05rem;line-height:1.6}
.st-key-tabbar a[data-testid="stPageLink-NavLink"] p{font-family:Amiri,Arial,sans-serif!important;font-size:.9rem!important;line-height:1.25!important}
[data-testid="stIconMaterial"]{font-family:"Material Symbols Rounded"!important}
</style>"""


def configure_page(module: Module) -> None:
    """Langue, titre d'onglet, icône et feuille de style. À appeler en tête de chaque page."""
    import streamlit as st

    i18n.use(i18n.from_session(st.session_state, st.query_params) or i18n.DEFAULT)
    st.set_page_config(page_title=f"{t(module.title)} | {APP_NAME}", page_icon=module.icon,
                       layout="centered", initial_sidebar_state="collapsed")
    st.markdown(_CSS, unsafe_allow_html=True)
    if i18n.is_rtl():
        st.markdown(_RTL_CSS, unsafe_allow_html=True)
        st.markdown(arabic_font_css(), unsafe_allow_html=True)
    else:
        st.markdown(arabic_font_css(mixed=True), unsafe_allow_html=True)


def set_language(lang: str) -> None:
    """Enregistre la langue choisie dans la session et dans l'adresse (rechargement compris)."""
    import streamlit as st

    from .session_context import refresh_text_defaults

    st.session_state[i18n.SESSION_KEY] = lang
    st.query_params[i18n.SESSION_KEY] = lang
    i18n.use(lang)
    refresh_text_defaults(st.session_state)


def language_buttons(key: str, primary: bool = False) -> None:
    """Trois boutons de langue ; la langue courante est mise en valeur."""
    import streamlit as st

    for column, (code, name) in zip(st.columns(3), i18n.LANGUAGES.items()):
        chosen = st.session_state.get(i18n.SESSION_KEY) == code
        column.button(name, key=f"{key}_{code}", use_container_width=True,
                      type="primary" if (chosen or primary) else "secondary",
                      on_click=set_language, args=(code,))


def page_header(module: Module, note: str | None = None, title: str | None = None,
                eyebrow: str = APP_NAME, tagline: str | None = None) -> None:
    """Bandeau d'en-tête lumineux : nom de l'application, titre du module et sa description."""
    import streamlit as st

    with st.container(key="hero"):
        st.markdown(f'<span class="eyebrow">{t(eyebrow)}</span>', unsafe_allow_html=True)
        st.title(t(title or module.title))
        if tagline:
            st.markdown(f'<p class="tagline">{t(tagline)}</p>', unsafe_allow_html=True)
        st.caption(t(module.summary) + (" " + t(note) if note else ""))


def tab_bar(current: str, home_page=None) -> None:
    """Barre d'onglets fixée en bas de l'écran ; l'onglet de la page affichée est mis en valeur."""
    import streamlit as st

    with st.container(key="tabbar"):
        for column, module in zip(st.columns(len(MODULES)), MODULES):
            target = home_page if module.path is None else module.path
            if target is None:
                continue
            state = "active" if module.key == current or (module.key == EPS_SPACE.key and current in {PLANNER.key, LAB.key, FIELD.key, FORMATIVE.key, JOURNAL.key}) else "idle"
            with column, st.container(key=f"tab_{state}_{module.key}"):
                st.page_link(target, label=t(module.short), icon=module.icon, use_container_width=True)
