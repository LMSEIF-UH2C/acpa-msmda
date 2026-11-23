"""Informations des magasins d'applications affichées sur une fiche du catalogue.

Les données proviennent de la fiche officielle de l'application (App Store, Aptoide ou F-Droid),
relevée par ``tools/catalog/enrich_from_stores.py``. Les fonctions sont celles qu'annonce
l'éditeur dans sa description ; elles ne sont pas vérifiées en situation.
"""
from __future__ import annotations

import datetime as dt

from .i18n import is_rtl, t, tj

LANGUAGES = {"FR": "français", "AR": "arabe", "EN": "anglais", "ES": "espagnol", "DE": "allemand",
             "IT": "italien", "PT": "portugais", "NL": "néerlandais", "TR": "turc"}
MONTHS = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc.")
STALE_YEARS = 3
MAX_FEATURES = 6


def _month_year(iso: str | None) -> str | None:
    try:
        d = dt.date.fromisoformat(iso[:10])
    except (TypeError, ValueError):
        return None
    return f"{t(MONTHS[d.month - 1])} {d.year}"


def languages_label(codes: list[str]) -> str | None:
    """Français et arabe d'abord, puis l'anglais, puis le nombre d'autres langues."""
    if not codes:
        return None
    codes = [c.upper() for c in codes]
    shown = [LANGUAGES[c] for c in ("FR", "AR", "EN") if c in codes]
    others = len([c for c in codes if c not in ("FR", "AR", "EN")])
    parts = [t(name) for name in shown]
    if others:
        parts.append(t("{n} autres", n=others) if others > 1 else t("1 autre"))
    return ("، " if is_rtl() else ", ").join(parts)


def details(tool: dict) -> list[tuple[str, str]]:
    """Lignes « libellé : valeur » à afficher, dans l'ordre utile à l'enseignant."""
    store = tool.get("store") or {}
    if not store.get("available"):
        return []
    rows = []
    price = store.get("price")
    if price:
        rows.append((t("Prix"), t(price) + (" · " + t("avec publicité") if store.get("ads") else "")))
    langs = languages_label(store.get("languages", []))
    if langs:
        rows.append((t("Langues"), langs))
    elif store.get("has_fr") or store.get("has_ar"):
        rows.append((t("Langues"), tj(l for l, ok in (("français", store.get("has_fr")),
                                                     ("arabe", store.get("has_ar"))) if ok)))
    if store.get("platforms"):
        rows.append((t("Plateformes"), tj(store["platforms"])))
    if store.get("age_rating"):
        rows.append((t("Âge"), store["age_rating"]))
    updated = _month_year(store.get("last_update"))
    if updated:
        rows.append((t("Mise à jour"), updated))
    if store.get("publisher"):
        rows.append((t("Éditeur"), store["publisher"]))
    return rows


def announced(tool: dict) -> list[str]:
    return [t(f) for f in (tool.get("features_announced") or [])[:MAX_FEATURES]]


def cautions(tool: dict, today: dt.date | None = None) -> list[str]:
    """Points de vigilance tirés des informations du magasin."""
    store = tool.get("store") or {}
    out = []
    today = today or dt.date.today()
    try:
        last = dt.date.fromisoformat((store.get("last_update") or "")[:10])
    except ValueError:
        last = None
    if last and (today - last).days > STALE_YEARS * 365:
        out.append(t("Peu mise à jour : dernière version en {year}.", year=last.year))
    age = str(store.get("age_rating") or "")
    if age in ("17+", "PEGI-16", "PEGI-18", "18+"):
        out.append(t("Classée {age} par le magasin : déconseillée avec des élèves.", age=age))
    if store.get("uses_internet") is False:
        out.append(t("Fonctionne sans Internet (l'application ne demande aucun accès au réseau)."))
    return out


def source_note(tool: dict) -> str | None:
    store = tool.get("store") or {}
    if not store.get("available"):
        return None
    when = _month_year(store.get("checked_at"))
    name = store.get("name") or t("du magasin")
    return t("Informations de la fiche {name}, relevées en {when}.", name=name, when=when) if when \
        else t("Informations de la fiche {name}.", name=name)


def works_offline(tool: dict) -> bool:
    """Usage hors connexion annoncé par l'éditeur ou garanti par l'absence d'accès au réseau."""
    store = tool.get("store") or {}
    return bool(tool.get("offline_hint") or store.get("uses_internet") is False
                or "Fonctionne hors connexion" in (tool.get("features_announced") or []))
