"""Ce que l'application a compris d'une demande, paramètre par paramètre, avec un degré de confiance.

Paramètres : activité, fonction recherchée, niveau, effectif, contraintes (connexion, budget,
effectif nombreux, inclusion). La confiance est déterministe et explicable :

- 0,9 : forme canonique trouvée telle quelle (« natation », « collège », « 30 élèves »)
- 0,7 : forme trouvée après normalisation de l'arabe ou par un synonyme (« swim », « السباحة »)
- 0,5 : indice faible (un nombre seul, sans « élèves » ni « تلميذ » à côté)

Ce n'est pas une probabilité statistique : c'est un repère pour que l'enseignant voie d'un coup
d'œil ce qui a été reconnu et puisse corriger sa demande.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .context_engine import detect_language, extract_flags, normalize_text
from .keywords import ACTIVITIES, VOCABULARY, keywords_in

LEVELS = {
    "Primaire": ("primaire", "ecole primaire", "primary", "elementary", "ابتدائي", "الابتدائي"),
    "Collège": ("college", "secondaire collegial", "middle school", "اعدادي", "الاعدادي", "الثانوي الاعدادي"),
    "Lycée": ("lycee", "secondaire qualifiant", "high school", "ثانوي", "الثانوي", "التاهيلي", "الثانوي التاهيلي",
              "tronc commun", "bac", "baccalaureat"),
    "Supérieur": ("universite", "university", "superieur", "ens", "جامعة"),
}
CONSTRAINTS = {
    "connectivite_faible": "Sans connexion",
    "budget_serre": "Budget limité",
    "grand_effectif": "Classe nombreuse",
    "inclusion": "Élèves en situation de handicap",
}
PUPIL_WORDS = r"(?:eleves?|élèves?|students?|pupils?|kids|enfants|joueurs?|players?|تلميذ\w*|تلاميذ|طالب\w*|لاعب\w*)"


@dataclass(frozen=True)
class Item:
    parameter: str   # « Activité », « Fonction », « Niveau », « Effectif », « Contrainte »
    value: str       # libellé en français (traduit à l'affichage)
    confidence: float


def _exact(key: str, text: str) -> bool:
    """Le mot-clé figure sous sa forme canonique (première forme du vocabulaire), sans synonyme."""
    padded = f" {normalize_text(text)} "
    return f" {normalize_text(VOCABULARY[key][0]).strip()} " in padded


def _level(text: str) -> Item | None:
    padded = " " + " ".join(normalize_text(text).split()) + " "
    for label, forms in LEVELS.items():
        for i, form in enumerate(forms):
            if f" {normalize_text(form).strip()} " in padded:
                return Item("Niveau", label, .9 if i == 0 else .7)
    return None


def _headcount(text: str) -> Item | None:
    m = re.search(r"(\d{1,3})\s*" + PUPIL_WORDS, text, re.IGNORECASE) \
        or re.search(PUPIL_WORDS + r"\s*(?:de|of|:)?\s*(\d{1,3})", text, re.IGNORECASE)
    m = m or re.search(r"(?:classe|class|groupe|group|قسم|فوج)\s*(?:de|of|من)?\s*(\d{1,3})", text, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 200:
            return Item("Effectif", str(n), .9)
    bare = re.findall(r"(?<![\d.,])(\d{2})(?![\d.,]|\s*(?:m\b|min|km|%|s\b|ans|years|سنة|د\b|م\b))", text)
    if len(bare) == 1 and 10 <= int(bare[0]) <= 60:
        return Item("Effectif", bare[0], .5)
    return None


def understand(text: str) -> list[Item]:
    """Paramètres reconnus dans la demande, dans un ordre stable."""
    if not text or not text.strip():
        return []
    arabic = detect_language(text) == "ar"
    items: list[Item] = []
    flags = extract_flags(text)
    for key in keywords_in(text):
        if key == "inclusion" and "inclusion" in flags:
            continue
        confidence = .7 if arabic or not _exact(key, text) else .9
        items.append(Item("Activité" if key in ACTIVITIES else "Fonction", key, confidence))
    for item in (_level(text), _headcount(text)):
        if item:
            items.append(item)
    for flag in flags:
        if flag in CONSTRAINTS:
            items.append(Item("Contrainte", CONSTRAINTS[flag], .8))
    return items


def confidence_label(value: float) -> str:
    return "sûr" if value >= .85 else ("probable" if value >= .65 else "à confirmer")
