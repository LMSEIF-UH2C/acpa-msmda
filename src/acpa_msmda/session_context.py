"""Contexte de séance partagé entre les modules.

Streamlit efface l'état d'un widget dès qu'une page ne l'affiche plus : un champ
rempli dans « Concevoir une séance » serait perdu en passant à « Organiser les
ateliers ». Les valeurs sont donc conservées dans un magasin indépendant des
widgets (``st.session_state[STORE_KEY]``) et recopiées dans chaque widget à
l'affichage. L'enseignant saisit son contexte une fois ; tous les modules le
relisent avec les mêmes libellés et les mêmes listes de choix.

Les données sont conservées dans l'état de session Streamlit, qui réside sur le
serveur de l'application et communique avec le navigateur à chaque interaction.
Ce module ne les enregistre pas volontairement dans une base de données ou un
fichier, et ne les transmet à aucun service tiers. Elles sont perdues à la fin
de la session (rechargement ou fermeture de la page).
"""
from __future__ import annotations

from typing import Any, Callable, MutableMapping, Sequence

STORE_KEY = "acpa_store"
WIDGET_PREFIX = "w:"

APS = ("Endurance", "Athlétisme", "Gymnastique", "Basketball", "Football", "Handball",
       "Volleyball", "Badminton", "Activité physique autonome", "Autre")
LEVELS = ("Primaire", "Collège", "Lycée", "Supérieur", "Formation d'enseignants")
# Valeurs attendues par scenario_engine.recommend_phase_tools.
CONNECTIVITY = ("Aucune", "Limitée", "Disponible")
CONNECTIVITY_LABELS = {"Aucune": "Aucune connexion", "Limitée": "Connexion instable",
                       "Disponible": "Connexion disponible"}
DEVICES = ("Aucun", "Téléphone enseignant", "Téléphones partagés", "Téléphones individuels")
SPACES = ("Terrain extérieur", "Gymnase", "Piste", "Salle polyvalente", "Autre")

CONTEXT_DEFAULTS: dict[str, Any] = {
    "activity": "Endurance",
    "level": "Collège",
    "class_size": 30,
    "duration": 60,
    "connectivity": "Aucune",
    "devices": "Téléphone enseignant",
    "space": "Terrain extérieur",
    "equipment": "Plots, chronomètre, un smartphone enseignant",
    "objectives": "Gérer son allure et analyser sa performance.",
}


def store(session: MutableMapping) -> dict:
    """Magasin persistant de la session (créé au premier appel)."""
    return session.setdefault(STORE_KEY, {})


def get(session: MutableMapping, key: str) -> Any:
    data = store(session)
    return data.get(key, CONTEXT_DEFAULTS.get(key))


def put(session: MutableMapping, key: str, value: Any) -> None:
    store(session)[key] = value


def bind(session: MutableMapping, key: str, default: Any = None) -> dict:
    """Prépare un widget lié au magasin : renvoie ``key``, ``on_change`` et ``args``.

    La valeur du magasin est recopiée dans l'état du widget avant sa création ;
    toute modification par l'enseignant est recopiée dans le magasin.
    """
    data = store(session)
    if key not in data:
        data[key] = CONTEXT_DEFAULTS.get(key, default) if default is None else default
    widget_key = WIDGET_PREFIX + key
    session[widget_key] = data[key]
    return {"key": widget_key, "on_change": _save, "args": (session, key)}


def _save(session: MutableMapping, key: str) -> None:
    store(session)[key] = session[WIDGET_PREFIX + key]


def summary(session: MutableMapping) -> str:
    """Résumé d'une ligne du contexte, pour les titres et les exports."""
    return " · ".join([
        get(session, "activity"),
        get(session, "level"),
        f"{get(session, 'class_size')} élèves",
        f"{get(session, 'duration')} min",
        CONNECTIVITY_LABELS[get(session, "connectivity")].lower(),
    ])


def search_query(session: MutableMapping) -> str:
    """Requête de recherche de technologies construite à partir du contexte.

    Les formulations de connectivité reprennent celles que le moteur reconnaît
    déjà (« sans connexion », « connexion instable ») : aucune règle du moteur
    n'est modifiée.
    """
    parts = [get(session, "activity").lower(), f"{get(session, 'class_size')} élèves"]
    connectivity = get(session, "connectivity")
    if connectivity == "Aucune":
        parts.append("sans connexion")
    elif connectivity == "Limitée":
        parts.append("connexion instable")
    objectives = (get(session, "objectives") or "").strip()
    if objectives:
        parts.append(objectives)
    return ", ".join(parts)


def render_context(st: Any, session: MutableMapping,
                   fields: Sequence[str] = ("activity", "level", "class_size", "duration",
                                            "connectivity", "devices", "space", "equipment",
                                            "objectives"),
                   expanded: bool = False) -> None:
    """Affiche les champs du contexte, identiques d'une page à l'autre."""
    widgets: dict[str, Callable[[], Any]] = {
        "activity": lambda: st.selectbox("Activité physique ou sportive", APS, **bind(session, "activity")),
        "level": lambda: st.selectbox("Niveau", LEVELS, **bind(session, "level")),
        "class_size": lambda: st.number_input("Effectif", min_value=1, max_value=150, step=1,
                                              **bind(session, "class_size")),
        "duration": lambda: st.number_input("Durée de la séance (min)", min_value=15, max_value=240,
                                            step=5, **bind(session, "duration")),
        "connectivity": lambda: st.selectbox("Connexion sur le lieu de pratique", CONNECTIVITY,
                                             format_func=CONNECTIVITY_LABELS.get,
                                             **bind(session, "connectivity")),
        "devices": lambda: st.selectbox("Appareils disponibles", DEVICES, **bind(session, "devices")),
        "space": lambda: st.selectbox("Espace", SPACES, **bind(session, "space")),
        "equipment": lambda: st.text_input("Matériel et contraintes", max_chars=400,
                                           **bind(session, "equipment")),
        "objectives": lambda: st.text_area("Objectifs de la séance", max_chars=800,
                                           **bind(session, "objectives")),
    }
    with st.expander("Votre séance : " + summary(session), expanded=expanded):
        short = [f for f in fields if f not in ("equipment", "objectives")]
        # Une rangée par paire de champs : sur téléphone, les colonnes s'empilent
        # rangée par rangée et l'ordre de lecture reste celui de la liste.
        for start in range(0, len(short), 2):
            for column, field in zip(st.columns(2), short[start:start + 2]):
                with column:
                    widgets[field]()
        for field in fields:
            if field in ("equipment", "objectives"):
                widgets[field]()
        st.caption("Ces informations sont reprises dans tous les modules.")
