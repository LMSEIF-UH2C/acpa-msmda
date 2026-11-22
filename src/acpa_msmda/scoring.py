"""Évaluation des applications du catalogue sur 18 critères.

Chaque fiche évaluée porte, pour chaque critère, une note de 0 à 10, « NR » (la description de
l'éditeur n'en dit rien) ou « SO » (le critère ne concerne pas ce type d'outil), ainsi qu'un risque
sécurité de 0 à 1. Les notes sont établies à partir de la description officielle de l'éditeur.

Score d'une fiche pour une demande :
    S = (Σ αⱼ Cⱼ + m × 5) / (Σ αⱼ + m) × (1 − β × risque), sur les critères notés,
avec αⱼ les poids contextuels (somme 1, majorés selon les contraintes de la demande), m = 0,30
(une fiche peu documentée est ramenée vers la note neutre 5) et β = 0,15. Le score est exprimé sur 100.
Une fiche dont l'alignement avec les programmes d'EPS (C13) est sans objet ou au plus 2 n'est pas
recommandée ; elle reste dans le catalogue.
"""
from __future__ import annotations

from typing import Mapping, Sequence

CODES = tuple(f"C{i}" for i in range(1, 19))

LABELS = {
    "C1": "Précision des capteurs", "C2": "Retour en temps réel", "C3": "Fiabilité",
    "C4": "Protection des données", "C5": "Export des données", "C6": "Fonctionnement hors connexion",
    "C7": "Économie de batterie", "C8": "Efficacité pour l'apprentissage moteur",
    "C9": "Engagement des élèves", "C10": "Motivation", "C11": "Facilité d'usage",
    "C12": "Accessibilité", "C13": "Lien avec les programmes d'EPS", "C14": "Coût",
    "C15": "Usage avec une classe", "C16": "Aide et support", "C17": "Liaison avec d'autres outils",
    "C18": "Retour sur investissement",
}

# Note du type d'outil, pas de l'application elle-même : l'affichage le précise.
TYPE_LEVEL = {"C8"}

# Libellés montrés aux enseignants (sans numéros de critères ni vocabulaire de méthode).
PUBLIC_LABELS = {**LABELS, "C8": "Type d'outil efficace pour les apprentissages",
                 "C13": "Adapté aux programmes d'EPS", "C14": "Coût", "C15": "Utilisable avec une classe"}

NEUTRAL = 5.0
SHRINK = 0.30
SAFETY_BETA = 0.15
RELEVANCE_MIN = 2.0  # C13 ≤ 2 : hors programme


def _value(raw):
    if raw in (None, "NR", "SO"):
        return None
    return float(raw)


def relevant(scores: Mapping) -> bool:
    """Faux si l'application est sans lien avec l'activité physique ou hors programme (C13)."""
    c13 = scores.get("C13")
    if c13 == "SO":
        return False
    value = _value(c13)
    return value is None or value > RELEVANCE_MIN


def documented(scores: Mapping) -> list[str]:
    return [c for c in CODES if _value(scores.get(c)) is not None]


def applicable(scores: Mapping) -> list[str]:
    return [c for c in CODES if scores.get(c) != "SO"]


def score(scores: Mapping, weights: Sequence[float]) -> float:
    """Score sur 100 d'une fiche notée, pour les poids contextuels donnés (18 valeurs, somme 1)."""
    if len(weights) != len(CODES):
        raise ValueError("18 poids requis")
    num = den = 0.0
    for code, alpha in zip(CODES, weights):
        value = _value(scores.get(code))
        if value is not None:
            if not 0 <= value <= 10:
                raise ValueError(f"Note hors échelle pour {code}")
            num += alpha * value
            den += alpha
    risk = float(scores.get("risque", 0) or 0)
    if not 0 <= risk <= 1:
        raise ValueError("Risque hors échelle")
    base = (num + SHRINK * NEUTRAL) / (den + SHRINK)
    return round(10 * base * (1 - SAFETY_BETA * risk), 1)


def strengths(scores: Mapping, limit: int = 3) -> list[str]:
    """Critères les mieux notés (≥ 7), du plus fort au moins fort."""
    ranked = sorted(((v, c) for c in CODES if (v := _value(scores.get(c))) is not None and v >= 7),
                    key=lambda x: (-x[0], CODES.index(x[1])))
    return [c for _, c in ranked[:limit]]


# C1 à 4 signifie « capteur utilisé, précision non indiquée » : ce n'est pas un point faible affiché.
NOT_A_WEAKNESS = {"C1"}


def weaknesses(scores: Mapping, limit: int = 2) -> list[str]:
    """Critères notés au plus 4."""
    ranked = sorted(((v, c) for c in CODES if c not in NOT_A_WEAKNESS
                     and (v := _value(scores.get(c))) is not None and v <= 4),
                    key=lambda x: (x[0], CODES.index(x[1])))
    return [c for _, c in ranked[:limit]]
