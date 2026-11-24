"""Séries de mesures d'une classe, indicateurs de bilan et exports.

Règles :
- les élèves sont désignés par un code anonyme (E01, E02…), jamais par leur nom ;
- un indicateur affiche toujours sa base de calcul (numérateur / dénominateur) ;
- aucune norme, aucun barème ni aucune interprétation physiologique n'est ajouté :
  seules les formules documentées dans le registre des épreuves sont calculées.
"""
from __future__ import annotations

import csv
import html
import io
import math
from dataclasses import dataclass
from statistics import mean, median, stdev
from typing import Optional, Sequence

from . import i18n
from .i18n import t
from .scenario_engine import safe_cell

MAX_PUPILS = 150


def fr(value: float, digits: Optional[int] = None, sign: bool = False) -> str:
    """Nombre au format français : virgule décimale, signe explicite si demandé."""
    if digits is None:
        text = f"{value:+g}" if sign else f"{value:g}"
    else:
        text = f"{value:+.{digits}f}" if sign else f"{value:.{digits}f}"
    return text.replace(".", ",")


def pupil_codes(count: int) -> list[str]:
    if not 1 <= count <= MAX_PUPILS:
        raise ValueError("Effectif invalide")
    width = max(2, len(str(count)))
    return [f"E{i:0{width}d}" for i in range(1, count + 1)]


@dataclass(frozen=True)
class ParseResult:
    values: list[Optional[float]]
    errors: list[str]


def parse_series(text: str, count: int, signed: bool = False) -> ParseResult:
    """Lit une valeur par ligne, dans l'ordre des codes élèves.

    Une ligne vide ou « abs » signifie absent. La virgule décimale est acceptée.
    """
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    errors: list[str] = []
    if len(lines) > count:
        errors.append(t("{n} lignes saisies pour {count} élèves.", n=len(lines), count=count))
    values: list[Optional[float]] = []
    for index in range(count):
        raw = lines[index].strip() if index < len(lines) else ""
        if raw == "" or raw.casefold() in ("abs", "absent", "-", "غ", "غائب"):
            values.append(None)
            continue
        try:
            value = float(raw.replace(",", ".").replace(" ", ""))
        except ValueError:
            errors.append(t("Ligne {i} : « {raw} » n'est pas un nombre.", i=index + 1, raw=raw))
            values.append(None)
            continue
        if not math.isfinite(value):
            errors.append(t("Ligne {i} : valeur non valide.", i=index + 1))
            values.append(None)
        elif value < 0 and not signed:
            errors.append(t("Ligne {i} : valeur négative non prévue pour cette épreuve.", i=index + 1))
            values.append(None)
        else:
            values.append(value)
    if not any(v is not None for v in values) and not errors:
        errors.append(t("Aucune valeur saisie."))
    return ParseResult(values, errors)


@dataclass(frozen=True)
class Indicator:
    label: str
    value: str
    ratio: Optional[float]  # 0..1 pour la barre ; None si une barre n'aurait pas de sens
    basis: str


def series_indicators(values: Sequence[Optional[float]], unit: str) -> list[Indicator]:
    measured = [v for v in values if v is not None]
    total = len(values)
    if not measured:
        return [Indicator(t("Élèves mesurés"), f"0 / {total}", 0.0, t("Aucune valeur saisie."))]
    unit = t(unit)
    out = [Indicator(t("Élèves mesurés"), f"{len(measured)} / {total}", len(measured) / total,
                     t("{n} absent(s) ou non mesuré(s).", n=total - len(measured)))]
    out.append(Indicator(t("Moyenne"), f"{fr(mean(measured), 2)} {unit}", None,
                         t("Calculée sur {n} élève(s) mesuré(s).", n=len(measured))))
    out.append(Indicator(t("Médiane"), f"{fr(median(measured), 2)} {unit}", None,
                         t("La moitié des élèves mesurés est au-dessus, l'autre moitié en dessous.")))
    if len(measured) >= 2:
        out.append(Indicator(t("Écart-type (échantillon)"), f"{fr(stdev(measured), 2)} {unit}", None, t("Dispersion des mesures autour de la moyenne ; dénominateur n − 1.")))
    out.append(Indicator(t("Étendue"), t("{a} à {b}", a=fr(min(measured)), b=fr(max(measured))) + f" {unit}", None,
                         t("Plus petite et plus grande valeur saisies.")))
    return out


def comparison(first: Sequence[Optional[float]], last: Sequence[Optional[float]],
               higher_is_better: Optional[bool], unit: str = "") -> tuple[list[Indicator], list[Optional[float]]]:
    """Compare deux séries d'une même épreuve, élève par élève.

    Sans sens favorable connu (``higher_is_better`` à None), l'indicateur décrit
    des hausses et des baisses, sans parler de progrès.
    """
    if len(first) != len(last):
        raise ValueError("Les deux séries doivent porter sur le même effectif")
    deltas = [(b - a) if a is not None and b is not None else None for a, b in zip(first, last)]
    paired = [d for d in deltas if d is not None]
    n = len(paired)
    if n == 0:
        return [Indicator(t("Élèves mesurés aux deux séances"), "0", 0.0,
                          t("Aucun élève n'a de valeur dans les deux séries."))], deltas
    up = sum(d > 0 for d in paired)
    down = sum(d < 0 for d in paired)
    same = n - up - down
    base = t("Sur {n} élève(s) mesuré(s) aux deux séances.", n=n)
    unit = t(unit) if unit else unit
    if higher_is_better is None:
        out = [Indicator(t("Valeur en hausse"), f"{up} / {n}", up / n, base),
               Indicator(t("Valeur en baisse"), f"{down} / {n}", down / n, base),
               Indicator(t("Valeur identique"), f"{same} / {n}", same / n, base)]
    else:
        better = up if higher_is_better else down
        worse = down if higher_is_better else up
        out = [Indicator(t("Variation favorable"), f"{better} / {n}", better / n,
                         base + " " + t("Selon le sens favorable choisi pour l'épreuve.")),
               Indicator(t("Variation défavorable"), f"{worse} / {n}", worse / n, base),
               Indicator(t("Résultat identique"), f"{same} / {n}", same / n, base)]
    if n >= 2:
        sd = stdev(paired)
        out.append(Indicator(t("Écart-type des différences"), f"{fr(sd, 2)} {unit}".strip(), None, base))
        if sd > 0:
            out.append(Indicator(t("Taille d’effet appariée (d_z)"), fr(mean(paired)/sd, 3, sign=True), None, t("Différence moyenne divisée par son écart-type ; signe après moins avant. Aucune interprétation causale.")))
    out.append(Indicator(t("Variation moyenne"), f"{fr(mean(paired), 2, sign=True)} {unit}".strip(), None, base))
    return out, deltas


def cooper_speed_kmh(distance_m: float) -> float:
    """Vitesse moyenne sur 12 minutes : distance (m) / 200 = km/h."""
    return distance_m / 200


def series_csv(rows: Sequence[dict]) -> bytes:
    """Export long : une ligne par élève et par série."""
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow([t(h) for h in ("Séance", "Date", "Épreuve", "Unité", "Élève", "Valeur", "Code du groupe (non nominatif)", "Numéro du cycle", "Numéro de séance", "Conditions de mesure")])
    for row in rows:
        for code, value in zip(row["codes"], row["values"]):
            writer.writerow([safe_cell(row["label"]), row["date"], t(row["test_name"]), t(row["unit"]), code,
                             "" if value is None else value, safe_cell(row.get("group","")), row.get("cycle",""), row.get("lesson",""), safe_cell(row.get("protocol",""))])
    return stream.getvalue().encode("utf-8-sig")


def report_html(title: str, context_line: str, sections: Sequence[tuple[str, Sequence[Indicator]]],
                table_header: Sequence[str], table_rows: Sequence[Sequence[str]], notes: Sequence[str]) -> bytes:
    """Bilan autonome en HTML, lisible sur téléphone et imprimable en PDF depuis le navigateur."""
    e = html.escape
    parts = [
        f"<!DOCTYPE html><html lang='{i18n.current()}' dir='{'rtl' if i18n.is_rtl() else 'ltr'}'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        f"<title>{e(title)}</title><style>",
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#1f2933;max-width:820px}",
        "h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.1rem;margin:28px 0 8px}",
        ".ctx{color:#52606d;margin-bottom:16px}.ind{display:grid;grid-template-columns:minmax(120px,1.2fr) minmax(80px,.8fr) 2fr;",
        "gap:4px 12px;align-items:center;padding:6px 0;border-bottom:1px solid #e4e7eb}",
        ".bar{height:10px;background:#e4e7eb;border-radius:5px;overflow:hidden}.bar span{display:block;height:100%;background:#2f6f8f}",
        ".basis{grid-column:1/-1;color:#616e7c;font-size:.85rem}table{border-collapse:collapse;width:100%;font-size:.9rem}",
        "th,td{border-bottom:1px solid #e4e7eb;padding:4px 6px;text-align:left}td.n{text-align:right}",
        ".notes{color:#616e7c;font-size:.85rem;margin-top:24px}@media print{body{margin:0}}</style></head><body>",
        f"<h1>{e(title)}</h1><div class='ctx'>{e(context_line)}</div>",
    ]
    for heading, indicators in sections:
        parts.append(f"<h2>{e(heading)}</h2>")
        for ind in indicators:
            bar = (f"<div class='bar'><span style='width:{max(0.0, min(1.0, ind.ratio)) * 100:.0f}%'></span></div>"
                   if ind.ratio is not None else "<div></div>")
            parts.append(f"<div class='ind'><strong>{e(ind.label)}</strong><span>{e(ind.value)}</span>{bar}"
                         f"<div class='basis'>{e(ind.basis)}</div></div>")
    parts.append(f"<h2>{e(t('Détail par élève'))}</h2><table><thead><tr>"
                 + "".join(f"<th>{e(h)}</th>" for h in table_header) + "</tr></thead><tbody>")
    for row in table_rows:
        parts.append("<tr>" + "".join(f"<td class='n'>{e(c)}</td>" if i else f"<td>{e(c)}</td>"
                                      for i, c in enumerate(row)) + "</tr>")
    parts.append("</tbody></table><div class='notes'>" + "".join(f"<p>{e(n)}</p>" for n in notes) + "</div></body></html>")
    return "".join(parts).encode("utf-8")


def comparable_series(a, b):
    """Conservative eligibility; teacher must additionally confirm stable pupil codes."""
    return (bool(a.get("group")) and a.get("group") == b.get("group")
            and bool(a.get("cycle")) and a.get("cycle") == b.get("cycle")
            and a.get("activity") == b.get("activity") and a.get("level") == b.get("level")
            and a.get("test_id") == b.get("test_id") and a.get("unit") == b.get("unit")
            and bool(a.get("protocol")) and a.get("protocol") == b.get("protocol")
            and a.get("codes") == b.get("codes")
            and a.get("date", "") <= b.get("date", "")
            and a.get("lesson", 0) > 0 and a.get("lesson", 0) < b.get("lesson", 0))
