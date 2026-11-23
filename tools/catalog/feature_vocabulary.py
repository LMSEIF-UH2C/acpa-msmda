"""Fonctions annoncées : étiquettes repérées dans la description officielle d'une application.

Chaque étiquette n'est retenue que si la description contient l'une de ses expressions, en entier
(comparaison après passage en minuscules et suppression des accents). Les expressions sont
volontairement précises : un mot isolé et ambigu (« course », « orientation », « timer » seul dans
un jeu) ne suffit pas. Seules les étiquettes sont conservées dans le catalogue, jamais le texte de
la description. Elles sont affichées comme fonctions « annoncées par l'éditeur ».
"""
from __future__ import annotations

import re
import unicodedata

FEATURES: dict[str, tuple[str, ...]] = {
    "Chronomètre": ("stopwatch", "chronometre", "lap timer", "split times", "lap times", "temps intermediaires"),
    "Minuteur d'intervalles": ("interval timer", "hiit timer", "tabata timer", "round timer", "emom timer",
                               "minuteur d'intervalles", "minuteur fractionne"),
    "Suivi GPS": ("gps tracking", "gps tracker", "track your route", "tracks your route", "records your route",
                  "record your route", "gps running", "suivi gps", "parcours gps"),
    "Cartes hors connexion": ("offline maps", "offline map", "download maps", "cartes hors ligne",
                              "cartes hors connexion"),
    "Boussole": ("compass", "boussole"),
    "Podomètre": ("pedometer", "step counter", "counts your steps", "count your steps", "podometre",
                  "compteur de pas"),
    "Fréquence cardiaque": ("heart rate monitor", "heart rate tracking", "measure your heart rate",
                            "heart rate zones", "frequence cardiaque"),
    "Ralenti et analyse vidéo": ("slow motion", "frame by frame", "frame-by-frame", "side by side comparison",
                               "side-by-side", "video analysis", "analyse video", "ralenti", "image par image"),
    "Dessin sur vidéo": ("drawing tools", "draw on video", "annotate video", "video annotation", "angle measurement",
                         "outils de dessin"),
    "Exercices en vidéo": ("video demonstrations", "exercise videos", "workout videos", "video tutorials",
                           "videos d'exercices", "video guides"),
    "Programmes d'entraînement": ("training plan", "training plans", "workout plan", "workout plans",
                                  "training program", "training programs", "programme d'entrainement",
                                  "plan d'entrainement"),
    "Suivi des progrès": ("track your progress", "progress tracking", "progress charts", "progress graphs",
                          "personal records", "personal bests", "suivi des progres", "suivez vos progres"),
    "Statistiques de match": ("player stats", "team stats", "game stats", "match stats", "live stats",
                              "statistiques de match", "statistiques des joueurs"),
    "Feuille de score": ("scoreboard", "scorekeeper", "score keeper", "keep score", "keep track of the score",
                         "tableau de score", "feuille de match"),
    "Tableau tactique": ("tactic board", "tactics board", "tactical board", "whiteboard for coaches",
                         "playbook", "tableau tactique"),
    "Gestion d'équipe": ("roster", "team management", "manage your team", "manage teams", "lineup", "lineups",
                         "gestion d'equipe", "composition d'equipe"),
    "Plusieurs élèves ou athlètes": ("multiple athletes", "multiple runners", "multiple players", "whole team",
                                     "entire group", "your athletes", "your students", "class roster",
                                     "plusieurs eleves", "plusieurs athletes"),
    "Évaluation et quiz": ("quiz", "quizzes", "rubric", "rubrics", "grading", "fitness test", "fitness tests",
                           "skill test", "skill tests", "beep test", "assess your students", "questionnaire"),
    "Export CSV ou Excel": ("export to csv", "csv export", "export csv", "excel export", "export to excel",
                            "export data", "export your data", "exporter les donnees"),
    "Export PDF": ("export to pdf", "pdf export", "export pdf", "pdf report", "rapport pdf"),
    "Annonces vocales": ("voice feedback", "audio cues", "voice coach", "audio feedback", "voice prompts",
                         "spoken", "annonces vocales", "coach vocal"),
    "Apple Santé ou Google Fit": ("apple health", "healthkit", "health app", "google fit", "health connect"),
    "Montre connectée": ("apple watch", "wear os", "garmin", "smartwatch", "montre connectee"),
    "Fonctionne hors connexion": ("works offline", "offline mode", "no internet", "without internet",
                                  "fully offline", "without an internet connection", "hors connexion",
                                  "sans connexion", "sans internet", "hors ligne"),
    "Sans compte": ("no account", "no sign up", "no signup", "no registration", "no login", "sans compte",
                    "sans inscription"),
    "Sans publicité": ("no ads", "ad-free", "ad free", "without ads", "sans publicite"),
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()
    return " " + re.sub(r"[^a-z0-9'\-]+", " ", text) + " "


_PATTERNS = {label: [_normalize(p) for p in phrases] for label, phrases in FEATURES.items()}


def announced_features(description: str) -> list[str]:
    """Étiquettes de fonctions dont une expression figure en entier dans la description."""
    text = _normalize(description)
    return [label for label, phrases in _PATTERNS.items() if any(p in text for p in phrases)]
