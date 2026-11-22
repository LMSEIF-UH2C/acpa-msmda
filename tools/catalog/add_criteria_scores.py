"""Ajoute au catalogue les notes des 18 critères issues des notations indépendantes.

Entrées (dossier de travail, non versionné car les fichiers contiennent des extraits des descriptions) :
- seconde_v2.csv : notation complète des 18 critères (grille version 2), une citation par note ;
- v3_a.csv et v3_b.csv : deux notations indépendantes de C6, C9, C10, C14 et C15 (grille version 3).

Règles de consolidation :
- C6, C9, C10, C14, C15 : moyenne des deux notations quand les deux sont chiffrées ; la seule note
  chiffrée sinon ; « SO » si l'une des deux vaut SO et aucune n'est chiffrée ; « NR » sinon ;
- autres critères et risque : notation complète ;
- C9 et C10 valent « SO » quand C13 vaut « SO » (outil sans activité physique).
Seules les notes sont écrites dans le catalogue, jamais les citations.

Usage : python tools/catalog/add_criteria_scores.py <dossier contenant les trois fichiers>
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1].parent
CATALOG = ROOT / "data" / "real_tools_catalog.json"
CODES = [f"C{i}" for i in range(1, 19)]
DOUBLE = ["C6", "C9", "C10", "C14", "C15"]


def _read(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def _cell(raw: str):
    raw = raw.strip()
    if raw in ("NR", "SO"):
        return raw
    value = float(raw.replace(",", "."))
    if not 0 <= value <= 10:
        raise ValueError(raw)
    return value


def _merge(a, b):
    nums = [v for v in (a, b) if isinstance(v, float)]
    if nums:
        return round(sum(nums) / len(nums), 1)
    return "SO" if "SO" in (a, b) else "NR"


def consolidate(full: dict, first: dict, second: dict) -> dict[str, dict]:
    if not (set(full) == set(first) == set(second)):
        raise ValueError("Les trois notations ne portent pas sur les mêmes fiches")
    result = {}
    for tid, row in full.items():
        scores = {c: _cell(row[c]) for c in CODES}
        for c in DOUBLE:
            scores[c] = _merge(_cell(first[tid][c]), _cell(second[tid][c]))
        if scores["C13"] == "SO":
            scores["C9"] = scores["C10"] = "SO"
        risk = float(row["risque"].replace(",", "."))
        if risk not in (0.0, 0.5, 1.0):
            raise ValueError(f"Risque invalide pour {tid}")
        scores["risque"] = risk
        result[tid] = scores
    return result


def main(work: Path) -> None:
    scores = consolidate(_read(work / "seconde_v2.csv"), _read(work / "v3_a.csv"), _read(work / "v3_b.csv"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    known = {t["id"] for t in catalog["tools"]}
    missing = set(scores) - known
    if missing:
        raise ValueError(f"Fiches absentes du catalogue : {sorted(missing)[:5]}")
    for tool in catalog["tools"]:
        if tool["id"] in scores:
            tool["criteria_scores"] = scores[tool["id"]]
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(scores)} fiches notées sur {len(catalog['tools'])}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
