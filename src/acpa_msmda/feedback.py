"""Avis des enseignants sur les fiches du catalogue : « utile en séance » ou « pas utile ».

Chaque avis est anonyme : identifiant de la fiche, avis et date, rien d'autre. Les avis sont
ajoutés ligne par ligne à un fichier JSON Lines (chemin réglable par ACPA_FEEDBACK_PATH),
ce qui suffit pour une installation sur un poste ou un serveur de l'établissement.
"""
from __future__ import annotations

import json
import os
import threading
from collections import Counter
from datetime import date
from pathlib import Path
from .i18n import t

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "feedback" / "votes.jsonl"
_LOCK = threading.Lock()


def store_path() -> Path:
    return Path(os.environ.get("ACPA_FEEDBACK_PATH", DEFAULT_PATH))


def record(tool_id: str, useful: bool, previous: bool | None = None) -> None:
    """Enregistre un avis ; si l'enseignant change d'avis, l'ancien est retiré."""
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if previous is not None:
        lines.append({"tool": tool_id, "useful": previous, "delta": -1, "day": date.today().isoformat()})
    lines.append({"tool": tool_id, "useful": useful, "delta": 1, "day": date.today().isoformat()})
    with _LOCK, path.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def apply_vote(votes: dict, tool_id: str, useful: bool) -> bool:
    """Applique l'avis d'une session ; renvoie False si l'avis est inchangé (pas de double vote)."""
    previous = votes.get(tool_id)
    if previous is useful:
        return False
    record(tool_id, useful, previous)
    votes[tool_id] = useful
    return True


def tallies() -> dict[str, Counter]:
    """Nombre d'avis « utile » et « pas utile » par fiche."""
    path = store_path()
    result: dict[str, Counter] = {}
    if not path.exists():
        return result
    with path.open(encoding="utf-8") as f:
        for raw in f:
            try:
                row = json.loads(raw)
                key = "useful" if row["useful"] else "not_useful"
                result.setdefault(str(row["tool"]), Counter())[key] += int(row.get("delta", 1))
            except (ValueError, KeyError, TypeError):
                continue  # une ligne abîmée ne doit pas bloquer le catalogue
    return result


def score(counts: Counter | None) -> int:
    """Solde des avis, utilisé pour faire remonter les fiches jugées utiles."""
    return 0 if not counts else counts["useful"] - counts["not_useful"]


def label(counts: Counter | None) -> str:
    if not counts or (counts["useful"] <= 0 and counts["not_useful"] <= 0):
        return t("Pas encore d'avis d'enseignant.")
    u, n = max(counts["useful"], 0), max(counts["not_useful"], 0)
    from .i18n import current
    if current() == "fr":
        return f"Avis d'enseignants : {u} utile{'s' if u > 1 else ''} en séance, {n} pas utile{'s' if n > 1 else ''}."
    return t("Avis d'enseignants : {u} utile(s) en séance, {n} pas utile(s).", u=u, n=n)
