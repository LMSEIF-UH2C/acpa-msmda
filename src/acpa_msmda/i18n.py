"""Langues de l'interface : français (langue source), arabe et anglais.

Chaque texte de l'interface est écrit en français dans le code et passe par ``t()`` :
``t("Accueil")`` renvoie la traduction de la langue courante, ou le français si aucune traduction
n'existe. Les traductions sont réunies dans ``data/translations.json`` (une entrée par texte
français, avec ses versions ``ar`` et ``en``) pour pouvoir être relues sans toucher au code.

Les valeurs enregistrées (choix d'activité, de niveau, de connexion…) restent en français dans
l'état de la session : seule leur présentation est traduite. Le moteur ne dépend donc pas de la
langue choisie.

La langue courante est propre à chaque exécution de page : elle est fixée au début de chaque
page par ``configure_page`` (voir ``ui.py``) à partir du choix de l'enseignant.
"""
from __future__ import annotations

import json
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

LANGUAGES = {"fr": "Français", "ar": "العربية", "en": "English"}
DEFAULT = "fr"
RTL = {"ar"}
SESSION_KEY = "lang"
PATH = Path(__file__).resolve().parents[2] / "data" / "translations.json"

_current: ContextVar[str] = ContextVar("acpa_lang", default=DEFAULT)


@lru_cache(maxsize=1)
def _read_table(path: Path, modified_ns: int, size: int) -> dict[str, dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def table() -> dict[str, dict[str, str]]:
    """Refresh translations when a deployment changes the JSON file in a live process."""
    stat = PATH.stat()
    return _read_table(PATH, stat.st_mtime_ns, stat.st_size)


table.cache_clear = _read_table.cache_clear


def use(lang: str | None) -> str:
    """Fixe la langue de l'exécution en cours ; une valeur inconnue donne le français."""
    code = lang if lang in LANGUAGES else DEFAULT
    _current.set(code)
    return code


def current() -> str:
    return _current.get()


def is_rtl(lang: str | None = None) -> bool:
    return (lang or current()) in RTL


def t(text: str, **values) -> str:
    """Traduit un texte français, puis insère les valeurs nommées ``{nom}``."""
    lang = current()
    out = text if lang == DEFAULT else (table().get(text, {}).get(lang) or text)
    return out.format(**values) if values else out


def colon() -> str:
    """Deux-points entre un libellé et sa valeur : espace avant en français seulement."""
    return " : " if current() == "fr" else ": "


def tj(items) -> str:
    """Liste traduite, séparée par des virgules (séparateur arabe en arabe)."""
    sep = "، " if is_rtl() else ", "
    return sep.join(t(i) for i in items)


def from_session(session, query_params=None) -> str | None:
    """Langue choisie : d'abord la session, puis le paramètre d'adresse ``?lang=``."""
    lang = session.get(SESSION_KEY)
    if lang in LANGUAGES:
        return lang
    if query_params is not None:
        try:
            lang = query_params.get(SESSION_KEY)
        except Exception:  # noqa: BLE001 - paramètres d'adresse absents en test
            lang = None
        if lang in LANGUAGES:
            session[SESSION_KEY] = lang
            return lang
    return None


def literals_in(source: str) -> set[str]:
    """Textes passés littéralement à ``t()`` dans un fichier source (pour les tests)."""
    import ast

    found = set()
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "t"
                and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            found.add(node.args[0].value)
    return found
