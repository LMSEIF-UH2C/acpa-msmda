"""Ajoute au catalogue les applications identifiées et vérifiées automatiquement.

Sources (toutes réelles, aucune fiche inventée) :
1. App Store : API publique de recherche d'Apple, filtrée sur la pertinence EPS (nom et
   description officielle), au moins 100 avis, genres utiles, hors contenu 17+.
2. Sites officiels : page accessible et nom de l'application présent dans le titre ou l'adresse.
3. Liste de prospection fournie par le porteur du projet : seuls les noms confirmés à
   l'identique sur l'App Store (au moins 20 avis) sont ajoutés.

Les fiches ajoutées ont le statut OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW : masquées par
défaut, jamais suggérées, fonctions à vérifier.
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "real_tools_catalog.json"
RETRIEVED = "2026-11-22"
PENDING = "OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW"

CAPS = {"Activité physique et entraînement": 140, "Activité et bien-être": 70, "Montage et supports": 50,
        "Suivi et GPS": 110, "Sports collectifs et tactique": 120, "Accessibilité et communication": 60,
        "Gestion et planification": 70, "Capteurs et tests": 77, "Analyse vidéo et mouvement": 60,
        "Cartographie et parcours": 45, "Course et chronométrage": 50, "Évaluation et recherche pédagogique": 38,
        "Questionnaires et évaluation": 34, "Conception pédagogique et multimédia": 29,
        "Ressources et apprentissage": 20, "Natation et sports aquatiques": 13}

BASKET_MAP = {
    "IA — assistants et recherche": "Assistants IA et recherche", "IA et assistants": "Assistants IA et recherche",
    "Entraînement et préparation": "Activité physique et entraînement", "Tests et mesures": "Capteurs et tests",
    "EPS et pédagogie": "Ressources et apprentissage", "Natation et sports individuels": "Activité physique et entraînement",
    "Course et endurance": "Suivi et GPS", "Analyse vidéo et mouvement": "Analyse vidéo et mouvement",
    "Sports collectifs": "Sports collectifs et tactique", "Données et automatisation": "Données et automatisation",
    "Automatisation et intégrations": "Données et automatisation", "Analyse et données": "Données et automatisation",
    "Gestion des tâches et To-do": "Organisation et bureautique", "Gestion de projet et SaaS": "Organisation et bureautique",
    "Bureautique et documents": "Organisation et bureautique", "Stockage et partage": "Organisation et bureautique",
    "Orientation plein air": "Cartographie et parcours", "Accessibilité et adaptation": "Accessibilité et communication",
    "Accessibilité et traduction": "Accessibilité et communication", "Création et communication visuelle": "Montage et supports",
    "Jeux actifs et ludification": "Jeux actifs et ludification", "Communication et organisation": "Communication et visioconférence",
    "Communication et messagerie": "Communication et visioconférence", "Visioconférence et réunions": "Communication et visioconférence",
    "Plateformes pédagogiques LMS": "Ressources et apprentissage", "Planification et réservations": "Gestion et planification",
    "Gestion sportive et compétitions": "Gestion et planification", "Formulaires et enquêtes": "Questionnaires et évaluation",
}


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", (text or "").replace("\xa0", " ").casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def core(name: str) -> str:
    name = name.replace("\xa0", " ")
    name = re.split(r"\s[:\-–—|]\s|:\s|・|\s\|\s|,", name)[0]
    return norm(re.sub(r"\(.*?\)", "", name))


def clean_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.replace("\xa0", " ")).strip()


def swim(name: str) -> bool:
    return bool(re.search(r"swim|natation|nage|piscine", norm(name)))


def entry(**kw) -> dict:
    base = {"activities": [], "uses": [], "requirement": "à vérifier", "evidence_status": PENDING,
            "criteria_scores": None, "retrieved_at": RETRIEVED}
    base.update(kw)
    return base


def main(work: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    tools = catalog["tools"]
    seen = {core(t["name"]) for t in tools} | {t["name"].casefold() for t in tools}
    ids = {t["id"] for t in tools}
    added: list[dict] = []

    def duplicate(key: str) -> bool:
        # « Runmeter Running GPS Tracker » double « Runmeter » : un nom existant d'au moins
        # 5 caractères suivi d'un espace en début de nom suffit à considérer le doublon.
        return any(key.startswith(k + " ") for k in seen if len(k) >= 5)

    def add(e: dict) -> bool:
        key = core(e["name"])
        if not key or key in seen or e["name"].casefold() in seen or e["id"] in ids or duplicate(key):
            return False
        seen.add(key); seen.add(e["name"].casefold()); ids.add(e["id"])
        added.append(e)
        return True

    caution_store = ("Fiche identifiée sur l'App Store : fonctions, prix, fonctionnement hors connexion et "
                     "conditions d'usage avec des élèves à vérifier avant toute utilisation en classe.")
    # 1. Liste de prospection confirmée sur l'App Store
    basket = json.loads((work / "basket_found.json").read_text(encoding="utf-8"))
    resolved = work / "basket_resolved.json"
    if resolved.exists():
        basket += json.loads(resolved.read_text(encoding="utf-8"))
    for item in basket:
        row, app = item["row"], item["app"]
        if app.get("contentAdvisoryRating") == "17+":
            continue
        category = BASKET_MAP[row["categorie_prospection"]]
        if row["categorie_prospection"] == "Natation et sports individuels" and swim(row["nom"]):
            category = "Natation et sports aquatiques"
        add(entry(id=f"ios-{app['trackId']}", name=clean_name(row["nom"]), category=category,
                  source_url=app["url"].replace("/fr/", "/us/").replace("/gb/", "/us/"), publisher=app.get("seller"),
                  caution=caution_store, origin="Liste de prospection, confirmée sur l'App Store"))
    # 2. Sites officiels vérifiés
    for x in json.loads((work / "web_verified_1.json").read_text(encoding="utf-8")):
        slug = re.sub(r"[^a-z0-9]+", "-", norm(x["name"])).strip("-")
        add(entry(id=f"web-{slug}", name=clean_name(x["name"]), category=x["category"], source_url=x["url"],
                  caution="Site officiel vérifié automatiquement ; fonctions et conditions d'usage à vérifier.",
                  origin="Site officiel (page accessible, nom présent dans le titre ou l'adresse)"))
    # 3. App Store, sélection par pertinence et usage
    relevant = json.loads((work / "relevant.json").read_text(encoding="utf-8"))
    by_cat: dict[str, list] = {}
    for a in relevant:
        by_cat.setdefault(a["category"], []).append(a)
    for cat, items in by_cat.items():
        items.sort(key=lambda a: -(a["relevance"] * math.log10(a["ratings"] + 10)))
        taken = 0
        for a in items:
            if taken >= CAPS.get(cat, 0):
                break
            if add(entry(id=f"ios-{a['trackId']}", name=clean_name(a["name"]), category=cat,
                         source_url=a["url"], publisher=a.get("seller"), caution=caution_store,
                         origin="App Store (recherche publique Apple, filtrée sur la pertinence EPS)")):
                taken += 1

    tools.extend(added)
    status = Counter(t["evidence_status"] for t in tools)
    catalog["total"] = len(tools)
    catalog["source_links_added"] = sum(bool(t.get("source_url")) for t in tools)
    catalog["feature_verified_count"] = status.get("FEATURES_VERIFIED_ON_OFFICIAL_SITE", 0)
    catalog["status_counts"] = dict(sorted(status.items()))
    catalog["notice"] = ("Répertoire d'outils réels issu de la cartographie des applications. Les suggestions portent sur l'ensemble "
                         "du répertoire ; chaque fiche indique si ses fonctions ont été relevées sur une source officielle (evidence_status). "
                         "Les notes des 18 critères sont établies selon la méthode propre à chaque fiche (criteria_method) : estimation "
                         "à partir de la description de l'éditeur, double notation indépendante ou fonctions vérifiées. Ces notes ne sont "
                         "pas des mesures validées d'efficacité.")
    catalog["criteria_method_counts"] = dict(sorted(Counter(t["criteria_method"] for t in tools).items()))
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ajoutées : {len(added)} ; total : {len(tools)}")
    print(Counter(e["origin"] for e in added))
    print(Counter(t["category"] for t in tools).most_common())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
