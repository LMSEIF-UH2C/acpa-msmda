"""Ajoute à chaque fiche du catalogue les mots-clés EPS tirés de son nom et de sa description officielle.

Les descriptions ne sont pas copiées dans le catalogue : seuls les mots-clés du vocabulaire commun
(src/acpa_msmda/keywords.py) sont conservés, avec l'indication « fonctionne hors connexion »
quand la description l'affirme.

Usage : python tools/catalog/add_keywords.py <dossier cache>
Le dossier est celui de enrich_from_stores.py : appstore.json, aptoide.json, fdroid_index_v2.json.
Les formes ambiguës (QUERY_ONLY de keywords.py) ne servent pas à indexer les fiches.
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


def main(cache: Path) -> None:
    sys.path.insert(0, str(ROOT / "tools" / "catalog"))
    from enrich_from_stores import aptoide_id, appstore_id, fdroid_pkg, store_of

    ios = json.loads((cache / "appstore.json").read_text(encoding="utf-8"))
    apt = json.loads((cache / "aptoide.json").read_text(encoding="utf-8"))
    fdr = json.loads((cache / "fdroid_index_v2.json").read_text(encoding="utf-8"))["packages"]

    def description(tool: dict) -> str:
        url = tool.get("source_url") or ""
        kind = store_of(url)
        if kind == "appstore":
            return (ios.get(appstore_id(url) or "") or {}).get("description", "")
        if kind == "aptoide":
            media = (apt.get(aptoide_id(url) or "") or {}).get("media") or {}
            return " ".join([media.get("summary") or "", media.get("description") or ""])
        if kind == "fdroid" and fdroid_pkg(url) in fdr:
            md = fdr[fdroid_pkg(url)]["metadata"]
            return " ".join([localized(md.get("summary")), localized(md.get("description"))])
        return ""

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    stats = Counter()
    for tool in catalog["tools"]:
        # Champs rédigés en français dans le catalogue : toutes les formes servent.
        listed = " ".join([tool.get("category", ""), tool.get("screening_use", "")]
                          + tool.get("activities", []) + tool.get("uses", []) + tool.get("features", []))
        desc = description(tool)
        # Mots-clés du nom seul : ils pèsent davantage dans le classement que ceux de la description.
        tool["title_keywords"] = keywords_in(tool["name"], catalog=True)
        tool["keywords"] = sorted(set(tool["title_keywords"]) | set(keywords_in(listed))
                                 | set(keywords_in(desc, catalog=True)))
        tool["offline_hint"] = mentions_offline(desc) or bool(tool.get("offline_hint"))
        stats["avec description"] += bool(desc)
        stats["avec mots-clés"] += bool(tool["keywords"])
        stats["hors connexion annoncé"] += tool["offline_hint"]
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(len(catalog["tools"]), dict(stats))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
