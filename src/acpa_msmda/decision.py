"""Interface de décision : trois repères par application, options pour affiner, rapport imprimable.

Les trois repères regroupent les notes de la fiche sans exposer la méthode d'évaluation :

- Intérêt pédagogique : retour en temps réel, efficacité pour les apprentissages, engagement,
  motivation, lien avec les programmes, usage avec une classe ;
- Facilité de mise en œuvre : précision, fiabilité, export, hors connexion, batterie, facilité d'usage,
  accessibilité, aide, liaison avec d'autres outils ;
- Coût : coût et retour sur investissement.

Chaque repère est une moyenne des notes renseignées, ramenée vers la note neutre quand peu de notes
sont connues (même principe que le score). Sans aucune note renseignée, le repère est « non renseigné ».
"""
from __future__ import annotations

import html
from datetime import date
from typing import Iterable, Mapping, Sequence

from . import i18n
from .i18n import t, tj
from .scoring import NEUTRAL

GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Intérêt pédagogique", ("C2", "C8", "C9", "C10", "C13", "C15")),
    ("Facilité de mise en œuvre", ("C1", "C3", "C5", "C6", "C7", "C11", "C12", "C16", "C17")),
    ("Coût", ("C14", "C18")),
)
SHRINK = 1.0  # poids de la note neutre, en nombre de notes


def _value(raw):
    return None if raw in (None, "NR", "SO") else float(raw)


def bars(scores: Mapping | None) -> list[tuple[str, float | None]]:
    """Trois repères sur 100 (None si aucune note renseignée pour le groupe)."""
    out = []
    for label, codes in GROUPS:
        values = [v for v in (_value((scores or {}).get(c)) for c in codes) if v is not None]
        if not values:
            out.append((label, None))
            continue
        mean = (sum(values) + SHRINK * NEUTRAL) / (len(values) + SHRINK)
        out.append((label, round(mean * 10, 1)))
    return out


# Affiner une demande : ajouts courts, écrits dans la langue de l'interface (le moteur les comprend
# dans les trois langues).
REFINEMENTS = ("sans connexion", "budget limité", "classe nombreuse", "élèves en situation de handicap",
               "application en arabe", "gratuit")


def refine(query: str, additions: Iterable[str]) -> str:
    extra = [t(a) for a in additions if t(a).casefold() not in query.casefold()]
    return ", ".join([query.strip().rstrip(",")] + extra) if extra else query


def report_html(query: str, understood: Sequence[str], matches: Sequence[dict], examined: int,
                elapsed_ms: float, limit: int = 10) -> bytes:
    """Rapport des recommandations, autonome, lisible sur téléphone et imprimable en PDF."""
    e = html.escape
    rtl = i18n.is_rtl()
    title = t("Rapport des recommandations")
    parts = [
        f"<!DOCTYPE html><html lang='{i18n.current()}' dir='{'rtl' if rtl else 'ltr'}'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        f"<title>{e(title)}</title><style>",
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#1f2933;max-width:820px}",
        "h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.1rem;margin:24px 0 6px}",
        ".muted{color:#52606d}.tool{border-top:1px solid #e4e7eb;padding:10px 0}",
        ".row{display:grid;grid-template-columns:minmax(140px,1fr) 3.5rem 2fr;gap:4px 10px;align-items:center;margin:3px 0}",
        ".bar{height:9px;background:#e4e7eb;border-radius:5px;overflow:hidden}.bar span{display:block;height:100%;background:#2563eb}",
        "ul{margin:4px 0;padding-inline-start:20px}a{color:#1d4ed8}@media print{body{margin:0}a{color:inherit}}</style></head><body>",
        f"<h1>{e(title)}</h1>",
        f"<p class='muted'>{e(t('Demande : '))}{e(query)}<br>{e(t('Date : '))}{date.today().isoformat()}</p>",
    ]
    if understood:
        parts.append(f"<p>{e(t('Compris : '))}{e(' · '.join(understood))}</p>")
    parts.append(f"<p class='muted'>{e(t('{n} applications examinées, {m} retenues, analyse en {ms} ms.', n=examined, m=len(matches), ms=round(elapsed_ms)))}</p>")

    def row(label: str, value: float | None) -> str:
        if value is None:
            return f"<div class='row'><span>{e(t(label))}</span><span>–</span><span class='muted'>{e(t('non renseigné'))}</span></div>"
        return (f"<div class='row'><span>{e(t(label))}</span><span>{value:.0f}</span>"
                f"<div class='bar'><span style='width:{max(0.0, min(100.0, value)):.0f}%'></span></div></div>")

    for rank, tool in enumerate(matches[:limit], 1):
        status = t("Fonctions vérifiées") if tool.get("verified") else t("À vérifier")
        parts.append(f"<div class='tool'><h2>{rank}. {e(tool['name'])}</h2><p class='muted'>{e(status)} · {e(t(tool.get('category', '')))}</p>")
        parts.append(row("Adéquation à la demande", tool.get("fit")))
        for label, value in bars(tool.get("criteria_scores")):
            parts.append(row(label, value))
        notes = [n for n in tool.get("cautions", []) if n]
        if notes:
            parts.append("<ul>" + "".join(f"<li>{e(t(n))}</li>" for n in notes) + "</ul>")
        if tool.get("source_url"):
            parts.append(f"<p><a href='{e(tool['source_url'])}'>{e(t("Voir l'application"))}</a></p>")
        parts.append("</div>")
    parts.append(f"<p class='muted'>{e(t('Fonctions annoncées par les éditeurs : à essayer avant la séance. Vérifiez les conditions d’utilisation et l’âge minimal requis avant tout usage avec des élèves.'))}</p>")
    parts.append("</body></html>")
    return "".join(parts).encode("utf-8")


def understood_labels(items, keyword_label) -> list[str]:
    """Libellés « Paramètre : valeur (confiance) » dans la langue de l'interface."""
    from .understanding import confidence_label

    return [t(i.parameter) + i18n.colon()
            + (keyword_label(i.value) if i.parameter in ("Activité", "Fonction") else t(i.value))
            + f" ({t(confidence_label(i.confidence))})" for i in items]


__all__ = ["GROUPS", "REFINEMENTS", "bars", "refine", "report_html", "understood_labels", "tj"]
