"""Ajoute au catalogue les applications retenues par le criblage automatique des candidates.

Entrées (dossier de travail) :
- candidates_evaluation.csv : candidates pertinentes non intégrées à la première version
  (id neutre, nom, magasin, éditeur, lien, description) ;
- evaluation_eps.csv : décision indépendante par candidate (UTILE / NON UTILE, usage principal) ;
- correspondance_privee.json : id neutre -> source (ios:<trackId>, apt:<package>, fd:<package>).

Seules les candidates UTILE disposant d'un lien public sont ajoutées. Elles gardent le statut
OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW : masquées par défaut, jamais suggérées.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import CATALOG, PENDING, clean_name, core  # noqa: E402

RETRIEVED = "2026-11-22"
USAGE_CATEGORY = {
    "Apprentissage sportif": "Activité physique et entraînement",
    "Planification": "Gestion et planification",
    "Chronométrage": "Course et chronométrage",
    "Mesure de performance": "Capteurs et tests",
    "Gestion de groupes ou ateliers": "Gestion et planification",
    "Analyse vidéo": "Analyse vidéo et mouvement",
    "Évaluation": "Questionnaires et évaluation",
    # Libellés de la relecture avec critères corrigés (exercice malgré la mention de minceur, orientation)
    "Orientation et parcours GPS": "Cartographie et parcours",
    "Apprentissage et pratique d’exercices": "Activité physique et entraînement",
    "Mesure et suivi de performance": "Capteurs et tests",
    "Planification et suivi des exercices": "Gestion et planification",
    "Chronométrage des entraînements": "Course et chronométrage",
    "Organisation de pratique sportive": "Gestion et planification",
}
ORIGIN = {
    "ios": "App Store, présélection automatique sur la description (critères EPS)",
    "apt": "Aptoide (Android), présélection automatique sur la description (critères EPS)",
    "fd": "F-Droid (Android), présélection automatique sur la description (critères EPS)",
}
CAUTION = ("Fiche présélectionnée automatiquement à partir de la description officielle : fonctions, prix, "
           "fonctionnement hors connexion et conditions d'usage avec des élèves à vérifier avant usage en classe.")


def read_csv(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f, delimiter=";")}


def main(work: Path) -> None:
    cands = read_csv(work / "candidates_evaluation.csv")
    decisions = read_csv(work / "evaluation_eps.csv")
    sources = json.loads((work / "correspondance_privee.json").read_text(encoding="utf-8"))
    if list(cands) != list(decisions):
        raise SystemExit("Les identifiants des deux fichiers ne correspondent pas.")

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    tools = catalog["tools"]
    seen = {core(t["name"]) for t in tools} | {t["name"].casefold() for t in tools}
    ids = {t["id"] for t in tools}
    skipped: Counter = Counter()
    added = []
    for cid, d in decisions.items():
        if d["decision"] != "UTILE":
            continue
        c = cands[cid]
        kind, ref = sources[cid].split(":", 1)
        tid = f"{kind}-{ref}"
        name = clean_name(c["nom"]).lstrip("'")
        key = core(name)
        if not c["lien"]:
            skipped["sans lien public"] += 1
            continue
        if not key or key in seen or name.casefold() in seen or tid in ids:
            skipped["déjà au catalogue"] += 1
            continue
        seen.update({key, name.casefold()}); ids.add(tid)
        added.append({"activities": [], "uses": [], "requirement": "à vérifier", "evidence_status": PENDING,
                      "criteria_scores": None, "retrieved_at": RETRIEVED, "id": tid, "name": name,
                      "category": USAGE_CATEGORY[d["usage_principal"]], "source_url": c["lien"],
                      "publisher": c["editeur"].lstrip("'") or None, "caution": CAUTION, "origin": ORIGIN[kind],
                      "screening_use": d["usage_principal"]})

    tools.extend(added)
    status = Counter(t["evidence_status"] for t in tools)
    catalog["total"] = len(tools)
    catalog["source_links_added"] = sum(bool(t.get("source_url")) for t in tools)
    catalog["feature_verified_count"] = status.get("FEATURES_VERIFIED_ON_OFFICIAL_SITE", 0)
    catalog["status_counts"] = dict(sorted(status.items()))
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ajoutées : {len(added)} ; écartées : {dict(skipped)} ; total : {len(tools)}")
    print(Counter(t["origin"].split(",")[0] for t in added))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
