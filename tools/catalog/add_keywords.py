"""Ajoute à chaque fiche du catalogue les mots-clés EPS tirés de son nom et de sa description officielle.

Les descriptions ne sont pas copiées dans le catalogue : seuls les mots-clés du vocabulaire commun
(src/acpa_msmda/keywords.py) sont conservés, avec l'indication « fonctionne hors connexion »
quand la description l'affirme.

Usage : python tools/catalog/add_keywords.py <dossier de travail>
Le dossier contient catalog/details.json (App Store), aptoide/aptoide_meta.json et fdroid/index-v2.json.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.keywords import keywords_in, mentions_offline  # noqa: E402

CATALOG = ROOT / "data" / "real_tools_catalog.json"


def localized(value) -> str:
    if isinstance(value, dict):
        return value.get("fr") or value.get("fr-FR") or value.get("en-US") or next(iter(value.values()), "")
    return value or ""


def main(work: Path) -> None:
    ios = json.loads((work / "catalog" / "details.json").read_text(encoding="utf-8"))
    apt = json.loads((work / "aptoide" / "aptoide_meta.json").read_text(encoding="utf-8"))
    fdr = json.loads((work / "fdroid" / "index-v2.json").read_text(encoding="utf-8"))["packages"]

    def description(tool_id: str) -> str:
        kind, _, ref = tool_id.partition("-")
        if kind == "ios":
            return (ios.get(ref) or {}).get("description", "")
        if kind == "apt":
            meta = apt.get(ref) or {}
            return " ".join([meta.get("summary") or "", meta.get("description") or ""])
        if kind == "fd" and ref in fdr:
            md = fdr[ref]["metadata"]
            return " ".join([localized(md.get("summary")), localized(md.get("description"))])
        return ""

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    stats = Counter()
    for tool in catalog["tools"]:
        listed = " ".join([tool.get("category", ""), tool.get("screening_use", "")]
                          + tool.get("activities", []) + tool.get("uses", []) + tool.get("features", []))
        desc = description(tool["id"])
        # Mots-clés du nom seul : ils pèsent davantage dans le classement que ceux de la description.
        tool["title_keywords"] = keywords_in(tool["name"])
        tool["keywords"] = sorted(set(tool["title_keywords"]) | set(keywords_in(listed)) | set(keywords_in(desc)))
        tool["offline_hint"] = mentions_offline(desc)
        stats["avec description"] += bool(desc)
        stats["avec mots-clés"] += bool(tool["keywords"])
        stats["hors connexion annoncé"] += tool["offline_hint"]
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(len(catalog["tools"]), dict(stats))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
