"""Inventaire des textes français que l'interface peut afficher, et des traductions manquantes.

Sources : les textes passés à ``t()`` dans le code, les listes de choix et libellés des modules,
les catégories, fonctions et mentions du catalogue, le registre des épreuves et les modèles de séance.

Usage :
    python tools/i18n_strings.py            # nombre de textes et de traductions manquantes
    python tools/i18n_strings.py --missing  # textes sans traduction arabe ou anglaise (JSON)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools" / "catalog"))

from acpa_msmda import i18n, keywords, scoring, session_context, ui  # noqa: E402
from acpa_msmda.store_info import LANGUAGES as STORE_LANGUAGES, MONTHS  # noqa: E402

CODE = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "src" / "acpa_msmda").glob("*.py"))]


def required() -> set[str]:
    texts: set[str] = set()
    for path in CODE:
        texts |= i18n.literals_in(path.read_text(encoding="utf-8"))
    for m in ui.MODULES:
        texts |= {m.title, m.summary, m.short}
    texts |= {ui.PRIVACY_NOTE, "EPS · collège et lycée", "De l’idée à la séance."}
    sc = session_context
    texts |= set(sc.APS) | set(sc.LEVELS) | set(sc.DEVICES) | set(sc.SPACES) | set(sc.CONNECTIVITY_LABELS.values())
    texts |= {sc.CONTEXT_DEFAULTS["equipment"], sc.CONTEXT_DEFAULTS["objectives"]}
    page = (ROOT / "pages" / "5_Studio_Pedagogique.py").read_text(encoding="utf-8")
    ns: dict = {}
    for name in ("PHASE_NAMES", "SUPPORTS", "MODALITIES"):
        line = next(l for l in page.splitlines() if l.startswith(name + " ="))
        exec(line, ns)  # noqa: S102 - constantes littérales du fichier de page
        texts |= set(ns[name])
    texts |= {"Séance vierge", "Toutes", "Tous", "Non précisé", "Valeur plus élevée", "Valeur plus faible",
              "Accueil et consignes", "Ateliers et rotations", "Retour au calme", "Bilan et traces"}
    texts |= set(scoring.LABELS.values()) | set(scoring.PUBLIC_LABELS.values())
    texts |= {keywords.LABELS.get(k, k) for k in keywords.VOCABULARY}
    texts |= set(MONTHS) | set(STORE_LANGUAGES.values())
    from feature_vocabulary import FEATURES
    texts |= set(FEATURES)
    catalog = json.loads((ROOT / "data" / "real_tools_catalog.json").read_text(encoding="utf-8"))["tools"]
    for tool in catalog:
        texts.add(tool["category"])
        for key in ("caution", "pricing", "offline"):
            if tool.get(key):
                texts.add(tool[key])
        for key in ("features", "platforms"):
            texts |= set(tool.get(key) or [])
        price = (tool.get("store") or {}).get("price")
        if price and not any(ch.isdigit() for ch in price):
            texts.add(price)
    for test in json.loads((ROOT / "data" / "performance_tests.json").read_text(encoding="utf-8"))["tests"]:
        texts |= {test[k] for k in ("name", "measure", "unit", "domain", "protocol_note") if test.get(k)}
    for tpl in json.loads((ROOT / "data" / "scenario_templates.json").read_text(encoding="utf-8"))["templates"]:
        texts |= {tpl[k] for k in ("title", "objectives", "prerequisites", "constraints")}
        for phase in tpl["phases"]:
            texts |= {phase["activity"], phase["success"]}
    # Textes neutres : identiques dans toutes les langues.
    return {x for x in texts if x and any(c.isalpha() for c in x)} - NEUTRAL


NEUTRAL = {"ACPA/MSMDA", "Android", "iOS", "iPadOS", "watchOS", "Windows", "HIIT", "m", "cm", "s", "km/h"}


def missing() -> dict[str, list[str]]:
    table = i18n.table()
    out: dict[str, list[str]] = {}
    for text in sorted(required()):
        langs = [lang for lang in ("ar", "en") if not table.get(text, {}).get(lang)]
        if langs:
            out[text] = langs
    return out


if __name__ == "__main__":
    gaps = missing()
    if "--missing" in sys.argv:
        print(json.dumps(sorted(gaps), ensure_ascii=False, indent=1))
    else:
        print(f"{len(required())} textes, {len(gaps)} sans traduction complète")
