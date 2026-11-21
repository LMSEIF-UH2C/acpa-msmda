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
from statistics import mean, median
from typing import Optional, Sequence

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
        errors.append(f"{len(lines)} lignes saisies pour {count} élèves.")
    values: list[Optional[float]] = []
    for index in range(count):
        raw = lines[index].strip() if index < len(lines) else ""
        if raw == "" or raw.casefold() in ("abs", "absent", "-"):
            values.append(None)
            continue
        try:
            value = float(raw.replace(",", ".").replace(" ", ""))
        except ValueError:
            errors.append(f"Ligne {index + 1} : « {raw} » n'est pas un nombre.")
            values.append(None)
            continue
        if not math.isfinite(value):
            errors.append(f"Ligne {index + 1} : valeur non valide.")
            values.append(None)
        elif value < 0 and not signed:
            errors.append(f"Ligne {index + 1} : valeur négative non prévue pour cette épreuve.")
            values.append(None)
        else:
            values.append(value)
    if not any(v is not None for v in values) and not errors:
        errors.append("Aucune valeur saisie.")
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
        return [Indicator("Élèves mesurés", f"0 / {total}", 0.0, "Aucune valeur saisie.")]
    out = [Indicator("Élèves mesurés", f"{len(measured)} / {total}", len(measured) / total,
                     f"{total - len(measured)} absent(s) ou non mesuré(s).")]
    out.append(Indicator("Moyenne", f"{fr(mean(measured), 2)} {unit}", None,
                         f"Calculée sur {len(measured)} élève(s) mesuré(s)."))
    out.append(Indicator("Médiane", f"{fr(median(measured), 2)} {unit}", None,
                         "La moitié des élèves mesurés est au-dessus, l'autre moitié en dessous."))
    out.append(Indicator("Étendue", f"{fr(min(measured))} à {fr(max(measured))} {unit}", None,
                         "Plus petite et plus grande valeur saisies."))
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
        return [Indicator("Élèves mesurés aux deux séances", "0", 0.0,
                          "Aucun élève n'a de valeur dans les deux séries.")], deltas
    up = sum(d > 0 for d in paired)
    down = sum(d < 0 for d in paired)
    same = n - up - down
    base = f"Sur {n} élève(s) mesuré(s) aux deux séances."
    if higher_is_better is None:
        out = [Indicator("Valeur en hausse", f"{up} / {n}", up / n, base),
               Indicator("Valeur en baisse", f"{down} / {n}", down / n, base),
               Indicator("Valeur identique", f"{same} / {n}", same / n, base)]
    else:
        better = up if higher_is_better else down
        worse = down if higher_is_better else up
        out = [Indicator("Élèves en progression", f"{better} / {n}", better / n,
                         base + " Selon le sens favorable choisi pour l'épreuve."),
               Indicator("Élèves en recul", f"{worse} / {n}", worse / n, base),
               Indicator("Résultat identique", f"{same} / {n}", same / n, base)]
    out.append(Indicator("Variation moyenne", f"{fr(mean(paired), 2, sign=True)} {unit}".strip(), None, base))
    return out, deltas


def cooper_speed_kmh(distance_m: float) -> float:
    """Vitesse moyenne sur 12 minutes : distance (m) / 200 = km/h."""
    return distance_m / 200


def series_csv(rows: Sequence[dict]) -> bytes:
    """Export long : une ligne par élève et par série."""
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Séance", "Date", "Épreuve", "Unité", "Élève", "Valeur"])
    for row in rows:
        for code, value in zip(row["codes"], row["values"]):
            writer.writerow([safe_cell(row["label"]), row["date"], row["test_name"], row["unit"], code,
                             "" if value is None else value])
    return stream.getvalue().encode("utf-8-sig")


def report_html(title: str, context_line: str, sections: Sequence[tuple[str, Sequence[Indicator]]],
                table_header: Sequence[str], table_rows: Sequence[Sequence[str]], notes: Sequence[str]) -> bytes:
    """Bilan autonome en HTML, lisible sur téléphone et imprimable en PDF depuis le navigateur."""
    e = html.escape
    parts = [
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>",
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
    parts.append("<h2>Détail par élève</h2><table><thead><tr>"
                 + "".join(f"<th>{e(h)}</th>" for h in table_header) + "</tr></thead><tbody>")
    for row in table_rows:
        parts.append("<tr>" + "".join(f"<td class='n'>{e(c)}</td>" if i else f"<td>{e(c)}</td>"
                                      for i, c in enumerate(row)) + "</tr>")
    parts.append("</tbody></table><div class='notes'>" + "".join(f"<p>{e(n)}</p>" for n in notes) + "</div></body></html>")
    return "".join(parts).encode("utf-8")
