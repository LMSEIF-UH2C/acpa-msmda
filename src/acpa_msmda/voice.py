"""Dictée de la demande par la reconnaissance vocale du navigateur (français et anglais).

Interface en arabe : la dictée se fait en français, la reconnaissance de l'arabe sur les navigateurs
des téléphones n'ayant pas été vérifiée. Aucun son n'est envoyé à l'application : le navigateur
renvoie seulement le texte reconnu.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

from . import i18n
from .i18n import t

_component = components.declare_component("acpa_voice", path=str(Path(__file__).parent / "components" / "voice"))
SPEECH = {"fr": "fr-FR", "en": "en-US", "ar": "fr-FR"}


def dictation(key: str) -> dict | None:
    """Bouton de dictée ; renvoie {"text", "at"} après une dictée, sinon la dernière valeur ou None."""
    lang = i18n.current()
    start = t("Dicter ma demande") if lang != "ar" else t("Dicter ma demande (en français)")
    return _component(key=key, default=None, lang=SPEECH.get(lang, "fr-FR"), start=start,
                      stop=t("Arrêter la dictée"), listening=t("Parlez, puis touchez « Arrêter »."),
                      unsupported=t("Dictée non disponible sur ce navigateur."),
                      denied=t("Micro refusé : autorisez-le dans les réglages du navigateur."),
                      failed=t("Dictée interrompue : réessayez."))
