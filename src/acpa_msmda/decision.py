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


def _latin(text: str) -> str:
    """Texte limité aux caractères des polices PDF standard (les noms en écriture arabe sont omis)."""
    text = str(text).replace("\u2009", " ").replace("\u202f", " ")
    return text.encode("cp1252", "ignore").decode("cp1252")


def report_pdf(query: str, items, matches: Sequence[dict], examined: int, elapsed_ms: float,
               keyword_label, limit: int = 10) -> bytes:
    """Rapport des recommandations en PDF, en français ou en anglais.

    Interface en arabe : le rapport sort en français (l'écriture arabe demande une police et une mise
    en forme que les PDF standard n'offrent pas). La demande saisie en arabe est alors remplacée par
    ce que l'application en a compris, déjà exprimé en français."""
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    from .store_info import cautions as store_cautions

    shown = i18n.current()
    out = shown if shown in ("fr", "en") else "fr"
    token = i18n.use(out)
    try:
        e = lambda x: html.escape(_latin(x))
        base = getSampleStyleSheet()
        body = ParagraphStyle("b", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12.5)
        muted = ParagraphStyle("m", parent=body, textColor=colors.HexColor("#52606d"))
        h1 = ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, spaceAfter=4)
        h2 = ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, spaceBefore=10, spaceAfter=2)
        story = [Paragraph(e(t("Rapport des recommandations")), h1)]
        typed = _latin(query).strip() if shown != "ar" else ""
        if typed:
            story.append(Paragraph(e(t("Demande : ")) + e(typed), body))
        labels = understood_labels(items, keyword_label)
        if labels:
            story.append(Paragraph(e(t("Compris : ")) + e(" · ".join(labels)), body))
        story.append(Paragraph(e(t("Date : ")) + date.today().isoformat() + " · " + e(t(
            "{n} applications examinées, {m} retenues, analyse en {ms} ms.", n=examined, m=len(matches),
            ms=round(elapsed_ms))), muted))

        def bar(value):
            if value is None:
                return Paragraph(e(t("non renseigné")), muted)
            table = Table([["", ""]], colWidths=[max(.5, value) * .55 * mm, max(.5, 100 - value) * .55 * mm], rowHeights=[2.6 * mm])
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#2563eb")),
                                       ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#e4e7eb")),
                                       ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
            return table

        for rank, tool in enumerate(matches[:limit], 1):
            name = _latin(tool["name"]).strip() or tool.get("id", "")
            status = t("Fonctions vérifiées") if tool.get("verified") else t("À vérifier")
            story.append(Paragraph(f"{rank}. {e(name)}", h2))
            story.append(Paragraph(e(status + " · " + t(tool.get("category", ""))), muted))
            rows = [[Paragraph(e(t("Adéquation à la demande")), body), f"{tool.get('fit', 0):.0f}", bar(tool.get("fit"))]]
            for label, value in bars(tool.get("criteria_scores")):
                rows.append([Paragraph(e(t(label)), body), "" if value is None else f"{value:.0f}", bar(value)])
            grid = Table(rows, colWidths=[62 * mm, 12 * mm, 60 * mm], hAlign="LEFT")
            grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                                      ("FONTSIZE", (1, 0), (1, -1), 9)]))
            story.append(grid)
            # Mises en garde recalculées dans la langue du rapport (celles de l'écran suivent l'interface).
            notes = [tool.get("caution", "")] + store_cautions(tool)
            if tool.get("device"):
                notes.append("Matériel requis : montre ou capteur compatible.")
            for note in [n for n in notes if n]:
                story.append(Paragraph("• " + e(t(note)), muted))
            if tool.get("source_url"):
                url = html.escape(tool["source_url"])
                story.append(Paragraph(f"<link href='{url}' color='#1d4ed8'>{url}</link>", muted))
        story += [Spacer(1, 6 * mm), Paragraph(e(t("Fonctions annoncées par les éditeurs : à essayer avant la séance. Vérifiez les conditions d’utilisation et l’âge minimal requis avant tout usage avec des élèves.")), muted)]
        stream = BytesIO()
        SimpleDocTemplate(stream, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                          bottomMargin=14 * mm, title=_latin(t("Rapport des recommandations")),
                          author="ACPA/MSMDA").build(story)
        return stream.getvalue()
    finally:
        i18n.use(shown)
        del token


def understood_labels(items, keyword_label) -> list[str]:
    """Libellés « Paramètre : valeur (confiance) » dans la langue de l'interface."""
    from .understanding import confidence_label

    return [t(i.parameter) + i18n.colon()
            + (keyword_label(i.value) if i.parameter in ("Activité", "Fonction") else t(i.value))
            + f" ({t(confidence_label(i.confidence))})" for i in items]


__all__ = ["GROUPS", "REFINEMENTS", "bars", "refine", "understood_labels", "tj"]
