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

from .i18n import t

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
    "cycle_number": 0,
    "lesson_number": 0,
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


# Textes proposés par défaut : écrits dans la langue de l'interface au moment où ils sont proposés.
TEXT_DEFAULTS = ("equipment", "objectives")


def _default(key: str) -> Any:
    value = CONTEXT_DEFAULTS.get(key)
    return t(value) if key in TEXT_DEFAULTS and isinstance(value, str) else value


def refresh_text_defaults(session: MutableMapping) -> None:
    """Après un changement de langue, réécrit les textes proposés par défaut que l'enseignant
    n'a pas modifiés, dans la nouvelle langue. Ses propres textes ne sont jamais touchés."""
    from .i18n import table

    data = store(session)
    for key, source in [(k, CONTEXT_DEFAULTS[k]) for k in TEXT_DEFAULTS] + [("series_label", "Séance 1")]:
        variants = {source, *table().get(source, {}).values()}
        if data.get(key) in variants:
            data[key] = t(source)


def get(session: MutableMapping, key: str) -> Any:
    data = store(session)
    return data.get(key, _default(key))


def put(session: MutableMapping, key: str, value: Any) -> None:
    data = store(session)
    if key == "activity" and value != get(session, "activity"):
        data.pop("activity_specialty", None)
        data.pop("scenario_phase_tools", None)
    data[key] = value


def bind(session: MutableMapping, key: str, default: Any = None) -> dict:
    """Prépare un widget lié au magasin : renvoie ``key``, ``on_change`` et ``args``.

    La valeur du magasin est recopiée dans l'état du widget avant sa création ;
    toute modification par l'enseignant est recopiée dans le magasin.
    """
    data = store(session)
    if key not in data:
        data[key] = (_default(key) if key in CONTEXT_DEFAULTS else default) if default is None else default
    widget_key = WIDGET_PREFIX + key
    session[widget_key] = data[key]
    return {"key": widget_key, "on_change": _save, "args": (session, key)}


def _save(session: MutableMapping, key: str) -> None:
    put(session, key, session[WIDGET_PREFIX + key])


def activity_label(session: MutableMapping) -> str:
    """Keep a journal specialty visible only in its matching catalogue category."""
    from .aps_specialties import catalog_category, valid_specialty
    specialty = get(session, "activity_specialty")
    if valid_specialty(specialty) and catalog_category(specialty) == get(session, "activity"):
        return specialty
    return get(session, "activity")


def summary(session: MutableMapping) -> str:
    """Résumé d'une ligne du contexte, pour les titres et les exports."""
    return " · ".join([
        t(activity_label(session)),
        t(get(session, "level")),
        t("{n} élèves", n=get(session, "class_size")),
        t("{n} min", n=get(session, "duration")),
        t(CONNECTIVITY_LABELS[get(session, "connectivity")]).lower(),
    ])


def search_query(session: MutableMapping) -> str:
    """Requête de recherche de technologies construite à partir du contexte.

    Les formulations de connectivité reprennent celles que le moteur reconnaît
    déjà (« sans connexion », « connexion instable ») : aucune règle du moteur
    n'est modifiée.
    """
    parts = [t(activity_label(session)).lower(), t(get(session, "level")), t("{n} élèves", n=get(session, "class_size")), t(get(session, "devices"))]
    if activity_label(session) != get(session, "activity"):
        parts.append(t(get(session, "activity")).lower())
    connectivity = get(session, "connectivity")
    if connectivity == "Aucune":
        parts.append(t("sans connexion"))
    elif connectivity == "Limitée":
        parts.append(t("connexion instable"))
    objectives = (get(session, "objectives") or "").strip()
    if objectives:
        parts.append(objectives)
    equipment = (get(session, "equipment") or "").strip()
    if equipment:
        parts.append(equipment)
    return ", ".join(parts)


def render_context(st: Any, session: MutableMapping,
                   fields: Sequence[str] = ("activity", "level", "class_size", "duration",
                                            "connectivity", "devices", "space", "cycle_number", "lesson_number", "equipment",
                                            "objectives"),
                   expanded: bool = False) -> None:
    """Affiche les champs du contexte, identiques d'une page à l'autre."""
    widgets: dict[str, Callable[[], Any]] = {
        "activity": lambda: st.selectbox(t("Activité physique ou sportive"), APS, format_func=t, **bind(session, "activity")),
        "level": lambda: st.selectbox(t("Niveau"), LEVELS, format_func=t, **bind(session, "level")),
        "cycle_number": lambda: st.number_input(t("Cycle (0 = non renseigné)"), min_value=0, step=1,
                                                **bind(session, "cycle_number")),
        "lesson_number": lambda: st.number_input(t("Séance (0 = non renseignée)"), min_value=0, step=1,
                                                 **bind(session, "lesson_number")),
        "class_size": lambda: st.number_input(t("Effectif"), min_value=1, max_value=150, step=1,
                                              **bind(session, "class_size")),
        "duration": lambda: st.number_input(t("Durée de la séance (min)"), min_value=15, max_value=240,
                                            step=5, **bind(session, "duration")),
        "connectivity": lambda: st.selectbox(t("Connexion sur le lieu de pratique"), CONNECTIVITY,
                                             format_func=lambda v: t(CONNECTIVITY_LABELS[v]),
                                             **bind(session, "connectivity")),
        "devices": lambda: st.selectbox(t("Appareils disponibles"), DEVICES, format_func=t, **bind(session, "devices")),
        "space": lambda: st.selectbox(t("Espace"), SPACES, format_func=t, **bind(session, "space")),
        "equipment": lambda: st.text_input(t("Matériel et contraintes"), max_chars=400,
                                           **bind(session, "equipment")),
        "objectives": lambda: st.text_area(t("Objectifs de la séance"), max_chars=800,
                                           **bind(session, "objectives")),
    }
    with st.expander(t("Votre séance : ") + summary(session), expanded=expanded):
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
        st.caption(t("Ces informations sont reprises dans tous les modules."))


def context_proposal(query: str) -> dict:
    """Recognized session fields only; never modify state until the teacher confirms."""
    from .understanding import understand
    from .context_engine import normalize_text, extract_flags
    from .aps_specialties import categories
    items = understand(query)
    mapping = {"endurance": "Endurance", "course": "Endurance", "athletisme": "Athlétisme",
               "vitesse": "Athlétisme", "saut": "Athlétisme", "gymnastique": "Gymnastique",
               "basketball": "Basketball", "football": "Football", "handball": "Handball",
               "volleyball": "Volleyball", "badminton": "Badminton"}
    out = {}
    normalized = " " + " ".join(normalize_text(query).split()) + " "
    def contains(value):
        return " " + " ".join(normalize_text(value).split()) + " " in normalized
    recognized = {mapping[i.value] for i in items if i.parameter == "Activité" and i.value in mapping}
    precise = {label: cat for label, cat in categories().items()
               if label != cat and contains(label)}
    if len(precise) == 1:
        label, category = next(iter(precise.items()))
        if not recognized - {category, "Endurance" if category == "Athlétisme" else category}:
            out.update(activity=category, activity_specialty=label)
    elif not precise and len(recognized) == 1:
        out["activity"] = next(iter(recognized))
    for item in items:
        if item.parameter == "Niveau" and item.value in LEVELS:
            out["level"] = item.value
        if item.parameter == "Effectif" and item.confidence >= .85 and 1 <= int(item.value) <= 150:
            out["class_size"] = int(item.value)
    if "connectivite_faible" in extract_flags(query):
        absent = any(contains(x) for x in ("sans connexion", "sans internet", "pas de wifi",
                     "no internet", "without internet", "no wifi", "بدون انترنت", "بدون اتصال", "لا يوجد انترنت"))
        limited = any(contains(x) for x in ("connexion instable", "internet faible",
                      "poor connectivity", "limited internet", "unstable connection", "انترنت ضعيف"))
        if absent != limited:
            out["connectivity"] = "Aucune" if absent else "Limitée"
    return out


def apply_context_proposal(session: MutableMapping, proposal: dict) -> None:
    """Apply a teacher-confirmed proposal; leave unrecognized fields unchanged."""
    for key in ("activity", "activity_specialty", "level", "class_size", "connectivity"):
        if key in proposal:
            put(session, key, proposal[key])
