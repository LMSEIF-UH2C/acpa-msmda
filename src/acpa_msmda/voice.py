"""Dictée de la demande par la reconnaissance vocale du navigateur (français, anglais, arabe).

Interface en arabe : deux boutons, dictée en arabe (ar-MA) ou en français, beaucoup d'enseignants
mêlant les deux. Aucun son n'est envoyé à l'application : le navigateur renvoie seulement le texte
reconnu. La qualité de la reconnaissance dépend du navigateur du téléphone.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

from . import i18n
from .i18n import t

_component = components.declare_component("acpa_voice", path=str(Path(__file__).parent / "components" / "voice"))
SPEECH = {"fr": "fr-FR", "en": "en-US", "ar": "ar-MA"}
_TEXTS = {"stop": "Arrêter la dictée", "listening": "Parlez, puis touchez « Arrêter ».",
          "unsupported": "Dictée non disponible sur ce navigateur.",
          "denied": "Micro refusé : autorisez-le dans les réglages du navigateur.",
          "failed": "Dictée interrompue : réessayez."}


def _button(key: str, speech: str, start: str) -> dict | None:
    return _component(key=key, default=None, lang=speech, start=start, **{k: t(v) for k, v in _TEXTS.items()})


def dictation(key: str) -> dict | None:
    """Bouton(s) de dictée ; renvoie la dictée la plus récente {"text", "at"}, sinon None."""
    lang = i18n.current()
    if lang != "ar":
        return _button(key, SPEECH[lang], t("Dicter ma demande"))
    import streamlit as st

    arabic, french = st.columns(2)
    with arabic:
        a = _button(key + "_ar", SPEECH["ar"], t("Dicter en arabe"))
    with french:
        f = _button(key + "_fr", SPEECH["fr"], t("Dicter en français"))
    spoken = [v for v in (a, f) if v]
    return max(spoken, key=lambda v: v.get("at", 0)) if spoken else None
