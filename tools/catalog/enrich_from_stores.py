"""Complète les fiches du catalogue à partir des fiches officielles des magasins d'applications.

Sources publiques, sans compte :
- App Store : API de recherche d'Apple (``itunes.apple.com/lookup``), par lots de 150 identifiants ;
- Aptoide : API ``ws75.aptoide.com/api/7/app/getMeta`` ;
- F-Droid : index officiel ``f-droid.org/repo/index-v2.json``.

Pour chaque fiche, le script ajoute un bloc ``store`` (magasin, disponibilité, éditeur, prix,
langues de l'interface, âge minimal, date de dernière mise à jour, plateformes et, pour F-Droid,
licence et usage d'Internet) et la liste ``features_announced`` (fonctions repérées dans la
description officielle, voir ``feature_vocabulary.py``). La description elle-même n'est jamais
enregistrée dans le catalogue.

Les fiches sans lien vers un magasin (sites d'éditeurs, fiches sans lien) ne sont pas modifiées.

Usage :
    python tools/catalog/enrich_from_stores.py --cache /chemin/cache            # télécharge puis applique
    python tools/catalog/enrich_from_stores.py --cache /chemin/cache --offline  # applique le cache seul
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feature_vocabulary import announced_features  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "real_tools_catalog.json"
UA = {"User-Agent": "acpa-msmda-catalog/1.0 (research; contact via GitHub LMSEIF-UH2C)"}

# Les mentions génériques « à vérifier » sont remplacées : prix, langues et âge sont désormais connus.
STORE_CAUTION = ("Fonctions annoncées par l'éditeur, à essayer avant la séance ; vérifier les conditions "
                 "d'usage avec des élèves.")
GENERIC_CAUTIONS = ("Fiche présélectionnée", "Fiche identifiée", "Référence à")


def refresh_caution(t: dict) -> None:
    if not t.get("caution") or t["caution"].startswith(GENERIC_CAUTIONS):
        t["caution"] = STORE_CAUTION


LANG_NAMES = {"FR": "français", "AR": "arabe", "EN": "anglais", "ES": "espagnol", "DE": "allemand"}


def get_json(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001 - réseau : on réessaie puis on abandonne la ligne
            time.sleep(2 * (attempt + 1))
    return None


def store_of(url: str | None) -> str | None:
    if not url:
        return None
    if "apps.apple.com" in url:
        return "appstore"
    if "aptoide.com" in url:
        return "aptoide"
    if "f-droid.org/packages/" in url:
        return "fdroid"
    return None


def appstore_id(url: str) -> str | None:
    m = re.search(r"/id(\d+)", url)
    return m.group(1) if m else None


def aptoide_id(url: str) -> str | None:
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    return (q.get("app_id") or [None])[0]


def fdroid_pkg(url: str) -> str | None:
    m = re.search(r"f-droid\.org/packages/([^/?#]+)", url)
    return m.group(1) if m else None


# ---------------------------------------------------------------- téléchargement (cache)

def fetch(tools: list[dict], cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    # App Store : la boutique française d'abord (prix en euros, langues), puis États-Unis, puis Maroc.
    ids = sorted({appstore_id(t["source_url"]) for t in tools if store_of(t.get("source_url")) == "appstore"} - {None})
    path = cache / "appstore.json"
    found = json.loads(path.read_text()) if path.exists() else {}
    for country in ("fr", "us", "ma"):
        missing = [i for i in ids if i not in found]
        for k in range(0, len(missing), 150):
            batch = missing[k:k + 150]
            data = get_json(f"https://itunes.apple.com/lookup?id={','.join(batch)}&country={country}&entity=software")
            for r in (data or {}).get("results", []):
                if str(r.get("trackId")) in batch:
                    r["_country"] = country
                    found[str(r["trackId"])] = r
            time.sleep(1.5)
        path.write_text(json.dumps(found, ensure_ascii=False))
    print(f"App Store : {len(found)}/{len(ids)} fiches trouvées")

    # Aptoide
    path = cache / "aptoide.json"
    meta = json.loads(path.read_text()) if path.exists() else {}
    for t in tools:
        if store_of(t.get("source_url")) != "aptoide":
            continue
        aid = aptoide_id(t["source_url"])
        if not aid or aid in meta:
            continue
        data = get_json(f"https://ws75.aptoide.com/api/7/app/getMeta?app_id={aid}")
        meta[aid] = (data or {}).get("data") or {"_missing": True}
        time.sleep(0.3)
    path.write_text(json.dumps(meta, ensure_ascii=False))
    print(f"Aptoide : {sum(1 for v in meta.values() if not v.get('_missing'))}/{len(meta)} fiches trouvées")

    # F-Droid : index complet
    path = cache / "fdroid_index_v2.json"
    if not path.exists():
        with urllib.request.urlopen(urllib.request.Request("https://f-droid.org/repo/index-v2.json", headers=UA),
                                    timeout=300) as r:
            path.write_bytes(r.read())
    print("F-Droid : index présent")


# ---------------------------------------------------------------- mise en forme

def iso_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return dt.datetime.fromtimestamp(value / 1000, dt.timezone.utc).date().isoformat()
    return str(value)[:10]


def apple_platforms(devices: list[str]) -> list[str]:
    out = []
    joined = " ".join(devices or [])
    for key, label in (("iPhone", "iPhone"), ("iPad", "iPad"), ("Watch", "Apple Watch")):
        if key in joined:
            out.append(label)
    return out


def from_appstore(r: dict, checked: str) -> tuple[dict, list[str]]:
    price = r.get("price")
    langs = [c.upper() for c in r.get("languageCodesISO2A") or []]
    store = {
        "name": "App Store", "checked_at": checked, "available": True,
        "publisher": r.get("sellerName") or r.get("artistName"),
        "price": "Téléchargement gratuit" if price == 0 else (r.get("formattedPrice") or "Payant"),
        "languages": langs, "has_fr": "FR" in langs, "has_ar": "AR" in langs,
        "age_rating": r.get("contentAdvisoryRating") or r.get("trackContentRating"),
        "last_update": iso_date(r.get("currentVersionReleaseDate")),
        "platforms": apple_platforms(r.get("supportedDevices")),
    }
    return store, announced_features(r.get("description", ""))


def from_aptoide(d: dict, checked: str) -> tuple[dict, list[str]]:
    age = d.get("age") or {}
    appc = d.get("appcoins") or {}
    store = {
        "name": "Aptoide", "checked_at": checked, "available": True,
        "publisher": (d.get("developer") or {}).get("name"),
        "price": "Payant" if d.get("pay") else "Téléchargement gratuit",
        "languages": [], "has_fr": None, "has_ar": None,
        "age_rating": age.get("pegi") or age.get("title"),
        "last_update": iso_date(d.get("updated") or d.get("modified")),
        "platforms": ["Android"],
    }
    if appc.get("advertising"):
        store["ads"] = True
    desc = (d.get("media") or {}).get("description") or ""
    return store, announced_features(desc)


def from_fdroid(pkg: dict, checked: str) -> tuple[dict, list[str]]:
    m = pkg.get("metadata", {})
    desc_locales = set((m.get("description") or {}).keys()) | set((m.get("summary") or {}).keys())
    versions = sorted(pkg.get("versions", {}).values(), key=lambda v: v.get("added", 0), reverse=True)
    latest = versions[0] if versions else {}
    perms = [p.get("name") for p in (latest.get("manifest", {}).get("usesPermission") or [])]
    anti = set((latest.get("antiFeatures") or {}).keys())
    store = {
        "name": "F-Droid", "checked_at": checked, "available": True,
        "publisher": m.get("authorName"),
        "price": "Gratuit, logiciel libre",
        "license": m.get("license"),
        "languages": [], "has_fr": any(l.lower().startswith("fr") for l in desc_locales) or None,
        "has_ar": any(l.lower().startswith("ar") for l in desc_locales) or None,
        "age_rating": None,
        "last_update": iso_date(m.get("lastUpdated")),
        "platforms": ["Android"],
        "uses_internet": "android.permission.INTERNET" in perms,
    }
    if "Ads" in anti:
        store["ads"] = True
    if "Tracking" in anti:
        store["tracking"] = True
    desc = " ".join((m.get("description") or {}).values()) + " " + " ".join((m.get("summary") or {}).values())
    feats = announced_features(desc)
    if not store["uses_internet"] and "Fonctionne hors connexion" not in feats:
        feats.append("Fonctionne hors connexion")
    return store, feats


# ---------------------------------------------------------------- application au catalogue

def apply(catalog: dict, cache: Path, checked: str) -> dict:
    apple = json.loads((cache / "appstore.json").read_text())
    apto = json.loads((cache / "aptoide.json").read_text())
    fdroid = json.loads((cache / "fdroid_index_v2.json").read_text())["packages"]
    counts = {"enriched": 0, "unavailable": 0, "skipped": 0}
    for t in catalog["tools"]:
        kind = store_of(t.get("source_url"))
        source = None
        if kind == "appstore":
            r = apple.get(appstore_id(t["source_url"]) or "")
            source = from_appstore(r, checked) if r else None
        elif kind == "aptoide":
            d = apto.get(aptoide_id(t["source_url"]) or "")
            source = from_aptoide(d, checked) if d and not d.get("_missing") else None
        elif kind == "fdroid":
            p = fdroid.get(fdroid_pkg(t["source_url"]) or "")
            source = from_fdroid(p, checked) if p else None
        else:
            counts["skipped"] += 1
            continue
        if source is None:
            t["store"] = {"name": {"appstore": "App Store", "aptoide": "Aptoide", "fdroid": "F-Droid"}[kind],
                          "checked_at": checked, "available": False}
            counts["unavailable"] += 1
            continue
        store, feats = source
        t["store"] = {k: v for k, v in store.items() if v not in (None, [], "")} | {"available": True}
        t["features_announced"] = feats
        if not t.get("publisher") and store.get("publisher"):
            t["publisher"] = store["publisher"]
        refresh_caution(t)
        counts["enriched"] += 1
    return counts


# ---------------------------------------------------------------- fiches sans lien

MIN_RATINGS = 20  # même seuil que resolve_names.py : écarte les homonymes confidentiels
# Correspondances de nom relues à la main et rejetées : autre éditeur que l'outil visé.
REJECTED_MATCHES = {"Live Transcribe": "Mighty Fine Apps LLC", "Mural": "Da Vinci Eye LLC"}


def _norm_name(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def resolve_unlinked(catalog: dict, cache: Path, checked: str, online: bool) -> int:
    """Cherche sur l'App Store les fiches sans lien : nom identique (ou nom suivi d'un sous-titre)
    et au moins MIN_RATINGS avis. Les fiches non retrouvées restent sans lien et ne sont pas suggérées."""
    path = cache / "unlinked_search.json"
    found = json.loads(path.read_text()) if path.exists() else {}
    resolved = 0
    for t in catalog["tools"]:
        if t.get("source_url"):
            continue
        name = re.sub(r"\s*\(.*?\)", "", t["name"]).strip()
        if online and t["id"] not in found:
            best = None
            for country in ("fr", "us"):
                q = urllib.parse.urlencode({"term": name, "country": country, "entity": "software", "limit": 15})
                for r in (get_json(f"https://itunes.apple.com/search?{q}") or {}).get("results", []):
                    tn, nn = _norm_name(r["trackName"]), _norm_name(name)
                    if (tn == nn or tn.startswith(nn + " ")) and (
                            best is None or r.get("userRatingCount", 0) > best.get("userRatingCount", 0)):
                        best = r
                time.sleep(1.2)
                if best:
                    break
            found[t["id"]] = best
        r = found.get(t["id"])
        if not r or r.get("userRatingCount", 0) < MIN_RATINGS or REJECTED_MATCHES.get(name) == r.get("sellerName"):
            continue
        t["source_url"] = r["trackViewUrl"].split("?")[0]
        t["origin"] = "App Store, recherche par nom exact (au moins 20 avis)"
        t["retrieved_at"] = checked
        t["evidence_status"] = "OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW"
        store, feats = from_appstore(r, checked)
        t["store"] = {k: v for k, v in store.items() if v not in (None, [], "")} | {"available": True}
        t["features_announced"] = feats
        t["publisher"] = t.get("publisher") or store.get("publisher")
        refresh_caution(t)
        resolved += 1
    path.write_text(json.dumps(found, ensure_ascii=False))
    return resolved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--offline", action="store_true", help="n'utiliser que le cache existant")
    ap.add_argument("--checked-at", default=dt.date.today().isoformat())
    args = ap.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not args.offline:
        fetch(catalog["tools"], args.cache)
    counts = apply(catalog, args.cache, args.checked_at)
    counts["linked_from_name"] = resolve_unlinked(catalog, args.cache, args.checked_at, not args.offline)
    counts["still_unlinked"] = sum(1 for t in catalog["tools"] if not t.get("source_url"))
    catalog["source_links_added"] = sum(1 for t in catalog["tools"] if t.get("source_url"))
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
