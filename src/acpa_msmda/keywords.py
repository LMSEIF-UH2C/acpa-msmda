"""Vocabulaire EPS commun aux fiches du catalogue et aux demandes des enseignants.

Chaque mot-clé canonique (en français) regroupe les formes rencontrées dans les descriptions des
magasins d'applications (souvent en anglais) et dans les demandes des enseignants (en français).
Les formes sont comparées après normalisation (minuscules, sans accents ni ponctuation).
"""
from __future__ import annotations

from .context_engine import normalize_text

VOCABULARY: dict[str, tuple[str, ...]] = {
    "course": ("course", "courir", "run", "running", "runner", "jogging", "jog", "marathon", "5k", "10k"),
    "endurance": ("endurance", "cardio", "aerobic", "aerobie", "vo2", "vo2max", "cooper", "beep test",
                  "bleep test", "shuttle run", "navette", "leger"),
    "vitesse": ("vitesse", "sprint", "sprints", "speed", "acceleration"),
    "chronometrage": ("chronometrage", "chronometre", "chrono", "stopwatch", "timer", "lap timer", "laps",
                      "countdown", "minuteur", "temps de passage"),
    "intervalles": ("intervalle", "intervalles", "interval", "intervals", "hiit", "tabata", "emom", "circuit"),
    "marche": ("marche", "walk", "walking", "pedometer", "podometre", "step counter", "steps"),
    "frequence cardiaque": ("frequence cardiaque", "heart rate", "pulse", "bpm", "cardiofrequencemetre"),
    "natation": ("natation", "nage", "nager", "swim", "swimming", "swimmer", "pool", "piscine"),
    "football": ("football", "soccer", "futsal"),
    "basketball": ("basketball", "basket", "hoops"),
    "volleyball": ("volleyball", "volley"),
    "handball": ("handball",),
    "rugby": ("rugby",),
    "tennis": ("tennis", "padel"),
    "badminton": ("badminton",),
    "tennis de table": ("tennis de table", "table tennis", "ping pong", "pingpong"),
    "athletisme": ("athletisme", "athletics", "track and field", "javelin", "javelot", "shot put", "lancer de poids",
                   "hurdles", "haies", "relais", "relay"),
    "saut": ("saut", "sauter", "jump", "jumping", "vertical jump", "long jump", "high jump", "detente"),
    "corde a sauter": ("corde a sauter", "corde", "jump rope", "skipping rope", "skipping"),
    "gymnastique": ("gymnastique", "gym artistique", "gymnastics", "tumbling", "acrobatics", "acrobatie",
                    "acrosport", "trampoline"),
    "yoga": ("yoga",),
    "pilates": ("pilates",),
    "musculation": ("musculation", "strength", "weight training", "weightlifting", "dumbbell", "dumbbells",
                    "barbell", "bodybuilding", "kettlebell"),
    "renforcement": ("renforcement", "gainage", "bodyweight", "calisthenics", "core", "abs", "plank",
                     "push up", "push ups", "pushups", "squat", "squats"),
    "souplesse": ("souplesse", "etirement", "etirements", "stretch", "stretching", "flexibility", "mobility",
                  "splits"),
    "echauffement": ("echauffement", "warm up", "warmup", "warm-up"),
    "danse": ("danse", "dance", "dancing", "choreography", "choregraphie", "zumba"),
    "sports de combat": ("combat", "boxe", "boxing", "judo", "karate", "taekwondo", "martial arts",
                         "arts martiaux", "lutte", "wrestling"),
    "velo": ("velo", "cyclisme", "cycling", "bike", "bicycle", "vtt"),
    "orientation": ("orientation", "course d orientation", "orienteering", "boussole", "compass", "carte",
                    "map", "maps", "gps", "topographic", "topo"),
    "randonnee": ("randonnee", "hiking", "hike", "trail", "trek", "trekking"),
    "escalade": ("escalade", "climbing", "bouldering"),
    "video": ("video", "videos", "ralenti", "slow motion", "slow mo", "replay", "frame by frame"),
    "analyse": ("analyse", "analyser", "analysis", "analytics", "statistiques", "statistics", "stats"),
    "tactique": ("tactique", "tactic", "tactics", "playbook", "tactical board", "strategy board", "whiteboard"),
    "score": ("score", "scores", "scoreboard", "scorekeeper", "score keeper", "marque", "tableau de marque"),
    "tournoi": ("tournoi", "tournament", "bracket", "league", "championnat", "fixtures"),
    "equipes": ("equipes", "equipe", "groupes", "groupe", "team generator", "team picker", "random teams",
                "team maker", "split teams"),
    "ateliers": ("ateliers", "atelier", "rotations", "circuit training"),
    "evaluation": ("evaluation", "evaluer", "notation", "gradebook", "grading", "grade book",
                   "assessment", "rubric", "bareme", "quiz"),
    "planification": ("planification", "planifier", "planning", "planner", "lesson plan", "schedule",
                      "session plan"),
    "entrainement": ("entrainement", "training", "workout", "workouts", "exercise", "exercises", "drills",
                     "coach", "coaching"),
    "mesure": ("mesure", "mesurer", "measure", "measurement", "tracker", "tracking", "suivi",
               "performance", "performances", "progression", "progress"),
    "respiration": ("respiration", "breathing", "relaxation", "retour au calme", "cool down"),
    "inclusion": ("inclusion", "inclusive", "adapte", "adaptive", "handicap", "disability", "accessibilite"),
}

OFFLINE_FORMS = ("offline", "no internet", "without internet", "works without", "sans connexion",
                 "hors ligne", "hors connexion", "no connection", "no wifi")

_FORMS = sorted(((normalize_text(form), key) for key, forms in VOCABULARY.items() for form in forms),
                key=lambda pair: -len(pair[0]))


def keywords_in(text: str) -> list[str]:
    """Mots-clés canoniques présents dans un texte (forme entière, pas un fragment de mot)."""
    padded = f" {normalize_text(text or '')} "
    return sorted({key for form, key in _FORMS if form and f" {form} " in padded})


def mentions_offline(text: str) -> bool:
    padded = f" {normalize_text(text or '')} "
    return any(f" {normalize_text(form)} " in padded for form in OFFLINE_FORMS)
