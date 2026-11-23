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
from pathlib import Path
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


FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"


def _fonts() -> tuple[str, str]:
    """Police DejaVu Sans (latin et arabe) enregistrée une fois pour reportlab."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", str(FONTS / "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONTS / "DejaVuSans-Bold.ttf")))
    return "DejaVu", "DejaVu-Bold"


def _rtl_lines(text: str, font: str, size: float, width: float) -> list[str]:
    """Coupe un texte arabe en lignes (ordre logique), puis met chaque ligne en forme pour l'affichage :
    liaison des lettres et ordre de droite à gauche, ligne par ligne pour que le retour à la ligne
    reste dans le bon ordre."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase.pdfmetrics import stringWidth

    lines, current = [], ""
    for word in str(text).split():
        trial = f"{current} {word}".strip()
        if current and stringWidth(arabic_reshaper.reshape(trial), font, size) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return [get_display(arabic_reshaper.reshape(line), base_dir="R") for line in lines]


def report_pdf(query: str, items, matches: Sequence[dict], examined: int, elapsed_ms: float,
               keyword_label, limit: int = 10) -> bytes:
    """Rapport des recommandations en PDF, dans la langue de l'interface (français, anglais ou arabe).

    L'arabe utilise une police qui contient ses lettres (DejaVu Sans, licence libre, dans
    assets/fonts), la liaison des lettres (arabic_reshaper) et l'ordre de droite à gauche
    (python-bidi), appliqués ligne par ligne."""
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    from .store_info import cautions as store_cautions

    regular, bold = _fonts()
    rtl = i18n.is_rtl()
    page_width = A4[0] - 32 * mm
    align = TA_RIGHT if rtl else TA_LEFT
    body = ParagraphStyle("b", fontName=regular, fontSize=9.5, leading=13, alignment=align)
    muted = ParagraphStyle("m", parent=body, textColor=colors.HexColor("#52606d"))
    h1 = ParagraphStyle("h1", fontName=bold, fontSize=16, leading=21, spaceAfter=4, alignment=align)
    h2 = ParagraphStyle("h2", fontName=bold, fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=2, alignment=align)

    def para(text: str, style, width: float = page_width) -> Paragraph:
        if rtl and any("\u0600" <= c <= "\u06ff" for c in str(text)):
            lines = _rtl_lines(text, style.fontName, style.fontSize, width - 2)
            return Paragraph("<br/>".join(html.escape(line) for line in lines), style)
        return Paragraph(html.escape(str(text)), style)

    story = [para(t("Rapport des recommandations"), h1)]
    if query.strip():
        story.append(para(t("Demande : ") + query.strip(), body))
    labels = understood_labels(items, keyword_label)
    if labels:
        story.append(para(t("Compris : ") + " · ".join(labels), body))
    story.append(para(t("Date : ") + date.today().isoformat() + " · " + t(
        "{n} applications examinées, {m} retenues, analyse en {ms} ms.", n=examined, m=len(matches),
        ms=round(elapsed_ms)), muted))

    def bar(value):
        if value is None:
            return para(t("non renseigné"), muted, 60 * mm)
        cells = [max(.5, value), max(.5, 100 - value)]
        table = Table([["", ""]], colWidths=[c * .55 * mm for c in (reversed(cells) if rtl else cells)],
                      rowHeights=[2.6 * mm])
        filled, empty = ((1, 0), (0, 0)) if rtl else ((0, 0), (1, 0))
        table.setStyle(TableStyle([("BACKGROUND", filled, filled, colors.HexColor("#2563eb")),
                                   ("BACKGROUND", empty, empty, colors.HexColor("#e4e7eb")),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return table

    widths = [62 * mm, 12 * mm, 60 * mm]
    for rank, tool in enumerate(matches[:limit], 1):
        status = t("Fonctions vérifiées") if tool.get("verified") else t("À vérifier")
        story.append(para(f"{rank}. {tool['name']}", h2))
        story.append(para(status + " · " + t(tool.get("category", "")), muted))
        rows = [[para(t("Adéquation à la demande"), body, widths[0]), f"{tool.get('fit', 0):.0f}", bar(tool.get("fit"))]]
        for label, value in bars(tool.get("criteria_scores")):
            rows.append([para(t(label), body, widths[0]), "" if value is None else f"{value:.0f}", bar(value)])
        if rtl:
            rows = [list(reversed(r)) for r in rows]
        grid = Table(rows, colWidths=list(reversed(widths)) if rtl else widths, hAlign="RIGHT" if rtl else "LEFT")
        grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("FONTNAME", (0, 0), (-1, -1), regular),
                                  ("FONTSIZE", (0, 0), (-1, -1), 9), ("ALIGN", (0, 0), (-1, -1), "RIGHT" if rtl else "LEFT")]))
        story.append(grid)
        # Mises en garde recalculées dans la langue du rapport.
        notes = [tool.get("caution", "")] + store_cautions(tool)
        if tool.get("device"):
            notes.append("Matériel requis : montre ou capteur compatible.")
        for note in [n for n in notes if n]:
            story.append(para("• " + t(note), muted))
        if tool.get("source_url"):
            url = html.escape(tool["source_url"])
            story.append(Paragraph(f"<link href='{url}' color='#1d4ed8'>{url}</link>", ParagraphStyle("u", parent=muted, alignment=TA_LEFT)))
    story += [Spacer(1, 6 * mm), para(t("Fonctions annoncées par les éditeurs : à essayer avant la séance. Vérifiez les conditions d’utilisation et l’âge minimal requis avant tout usage avec des élèves."), muted)]
    stream = BytesIO()
    SimpleDocTemplate(stream, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                      bottomMargin=14 * mm, title=t("Rapport des recommandations"), author="ACPA/MSMDA").build(story)
    return stream.getvalue()


def understood_labels(items, keyword_label) -> list[str]:
    """Libellés « Paramètre : valeur (confiance) » dans la langue de l'interface."""
    from .understanding import confidence_label

    return [t(i.parameter) + i18n.colon()
            + (keyword_label(i.value) if i.parameter in ("Activité", "Fonction") else t(i.value))
            + f" ({t(confidence_label(i.confidence))})" for i in items]


__all__ = ["GROUPS", "REFINEMENTS", "bars", "refine", "understood_labels", "tj"]
