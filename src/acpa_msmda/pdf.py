"""Outils communs aux documents PDF de l'application (rapport, scénario, organisation de séance).

Une seule police, DejaVu Sans (licence libre, assets/fonts), couvre le latin et l'arabe. Pour l'arabe,
le texte est coupé en lignes dans l'ordre logique, puis chaque ligne est mise en forme : lettres liées
(arabic_reshaper) et ordre de droite à gauche (python-bidi). Les tableaux sont inversés en arabe.
"""
from __future__ import annotations

import html
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Sequence

from . import i18n
from .i18n import t

FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"
ARABIC = ("؀", "ۿ")


def fonts() -> tuple[str, str]:
    """Police enregistrée une fois pour reportlab : (normale, grasse)."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", str(FONTS / "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONTS / "DejaVuSans-Bold.ttf")))
    return "DejaVu", "DejaVu-Bold"


def rtl_lines(text: str, font: str, size: float, width: float) -> list[str]:
    """Lignes d'un texte arabe prêtes à l'affichage (coupe logique, puis liaison et ordre visuel)."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase.pdfmetrics import stringWidth

    out: list[str] = []
    for paragraph in str(text).split("\n"):
        lines, current = [], ""
        for word in paragraph.split():
            trial = f"{current} {word}".strip()
            if current and stringWidth(arabic_reshaper.reshape(trial), font, size) > width:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
        out += lines
    return [get_display(arabic_reshaper.reshape(line), base_dir="R") for line in out]


@dataclass
class Kit:
    """Styles et fabrique de paragraphes pour la langue de l'interface."""
    rtl: bool
    width: float
    regular: str
    bold: str
    styles: dict

    def para(self, text, style: str = "body", width: float | None = None):
        from reportlab.platypus import Paragraph

        st = self.styles[style]
        text = "" if text is None else str(text)
        if self.rtl and any(ARABIC[0] <= c <= ARABIC[1] for c in text):
            lines = rtl_lines(text, st.fontName, st.fontSize, (width or self.width) - 4)
            return Paragraph("<br/>".join(html.escape(line) for line in lines), st)
        return Paragraph(html.escape(text).replace("\n", "<br/>"), st)

    def table(self, rows: Sequence[Sequence], widths: Sequence[float], header: bool = True, style: str = "cell"):
        """Tableau à cellules texte, inversé en arabe ; la première ligne en en-tête."""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        cells = [[self.para(c, "head" if header and i == 0 else style, w) for c, w in zip(row, widths)]
                 for i, row in enumerate(rows)]
        widths = list(widths)
        if self.rtl:
            cells = [list(reversed(r)) for r in cells]
            widths = list(reversed(widths))
        table = Table(cells, colWidths=widths, repeatRows=1 if header else 0, hAlign="RIGHT" if self.rtl else "LEFT")
        commands = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#cbd2d9")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
        if header:
            commands.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eefc")))
        table.setStyle(TableStyle(commands))
        return table

    def bar(self, ratio: float, width: float):
        """Barre horizontale (ratio de 0 à 1), remplie depuis la droite en arabe."""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        ratio = max(.005, min(.995, ratio))
        cells = [ratio * width, (1 - ratio) * width]
        table = Table([["", ""]], colWidths=list(reversed(cells)) if self.rtl else cells, rowHeights=[7])
        filled, empty = ((1, 0), (0, 0)) if self.rtl else ((0, 0), (1, 0))
        table.setStyle(TableStyle([("BACKGROUND", filled, filled, colors.HexColor("#2563eb")),
                                   ("BACKGROUND", empty, empty, colors.HexColor("#e4e7eb")),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return table


def kit() -> Kit:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm

    regular, bold = fonts()
    rtl = i18n.is_rtl()
    align = TA_RIGHT if rtl else TA_LEFT
    body = ParagraphStyle("body", fontName=regular, fontSize=9.5, leading=13, alignment=align)
    styles = {
        "body": body,
        "muted": ParagraphStyle("muted", parent=body, textColor=colors.HexColor("#52606d")),
        "h1": ParagraphStyle("h1", fontName=bold, fontSize=16, leading=21, spaceAfter=4, alignment=align),
        "h2": ParagraphStyle("h2", fontName=bold, fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=3, alignment=align),
        "cell": ParagraphStyle("cell", parent=body, fontSize=8.8, leading=11.5),
        "head": ParagraphStyle("head", parent=body, fontName=bold, fontSize=8.8, leading=11.5),
        "link": ParagraphStyle("link", parent=body, textColor=colors.HexColor("#52606d"), alignment=TA_LEFT),
    }
    return Kit(rtl=rtl, width=A4[0] - 32 * mm, regular=regular, bold=bold, styles=styles)


def build(story: list, title: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate

    stream = BytesIO()

    def footer(canvas, doc):
        regular, _ = fonts()
        canvas.saveState()
        canvas.setFont(regular, 7.5)
        canvas.setFillGray(.45)
        canvas.drawString(16 * mm, 9 * mm, "ACPA/MSMDA")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, str(doc.page))
        canvas.restoreState()

    SimpleDocTemplate(stream, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                      bottomMargin=16 * mm, title=title, author="ACPA/MSMDA").build(
        story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


def scenario_pdf(metadata: dict, rows: Sequence[dict], validation: dict, issues: Sequence[str]) -> bytes:
    """Fiche de séance : contexte, déroulement par phase, répartition du temps, points à compléter."""
    from reportlab.lib.units import mm
    from reportlab.platypus import Spacer

    k = kit()
    title = t("Scénario de séance d'EPS")
    story = [k.para(title, "h1")]
    meta = [(key, value) for key, value in metadata.items() if str(value or "").strip()]
    story.append(k.table([(key, value) for key, value in meta], [45 * mm, k.width - 45 * mm], header=False))
    story.append(k.para(t("Déroulement"), "h2"))
    from .scenario_engine import COLUMNS as columns

    widths = [29 * mm, 18 * mm, 58 * mm, 33 * mm, k.width - 138 * mm]
    body = [[t(c) for c in columns]] + [[t(r.get("Phase", "")), r.get("Durée (min)", ""), r.get("Activité / consignes", ""),
                                         r.get("Supports", ""), r.get("Évaluation / feedback", "")] for r in rows]
    story.append(k.table(body, widths))
    story.append(k.para(t("Répartition du temps"), "h2"))
    total = sum(r.get("Durée (min)", 0) for r in rows) or 1
    lines = [[t(r.get("Phase", "")), t("{n} min", n=r.get("Durée (min)", 0)), k.bar(r.get("Durée (min)", 0) / total, 80 * mm)]
             for r in rows]
    from reportlab.platypus import Table, TableStyle
    cells = [[k.para(a, "cell", 45 * mm), k.para(b, "cell", 22 * mm), c] for a, b, c in lines]
    widths = [45 * mm, 22 * mm, 82 * mm]
    if k.rtl:
        cells = [list(reversed(r)) for r in cells]
        widths = list(reversed(widths))
    grid = Table(cells, colWidths=widths, hAlign="RIGHT" if k.rtl else "LEFT")
    grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(grid)
    if validation["balanced"]:
        story.append(k.para(t("Les phases occupent exactement la durée prévue : {n} min.", n=validation["available_minutes"]), "muted"))
    else:
        story.append(k.para(t("Les phases totalisent {used} min pour une séance de {n} min (écart : {gap} min).",
                              used=validation["used_minutes"], n=validation["available_minutes"],
                              gap=f"{validation['difference_minutes']:+d}"), "muted"))
    if issues:
        story.append(k.para(t("Points à compléter : {n}", n=len(issues)), "h2"))
        story += [k.para("• " + issue, "body") for issue in issues]
    story += [Spacer(1, 5 * mm), k.para(t("Document de préparation : à adapter à votre classe et à votre terrain."), "muted")]
    return build(story, title)


def organisation_pdf(context: dict, phases: Sequence[tuple[str, int]], groups: Sequence[int], rotation: float,
                     advice: Sequence[str]) -> bytes:
    """Organisation d'une séance en ateliers : contexte, phases, groupes, temps par atelier."""
    from reportlab.lib.units import mm
    from reportlab.platypus import Spacer

    k = kit()
    title = t("Organisation de la séance en ateliers")
    story = [k.para(title, "h1"),
             k.table([(key, value) for key, value in context.items() if str(value or "").strip()],
                     [45 * mm, k.width - 45 * mm], header=False),
             k.para(t("Organisation proposée"), "h2"),
             k.table([[t("Phase"), t("Durée (min)")]] + [[t(name), minutes] for name, minutes in phases],
                     [k.width - 30 * mm, 30 * mm]),
             k.para(t("Groupes par atelier"), "h2"),
             k.table([[t("Atelier"), t("Élèves")]] + [[str(i), str(n)] for i, n in enumerate(groups, 1)],
                     [40 * mm, 30 * mm]),
             Spacer(1, 3 * mm),
             k.para(t("Temps par atelier :") + " " + t("{n} min, transitions comprises.", n=f"{rotation:.1f}"), "body")]
    story += [k.para("• " + a, "muted") for a in advice]
    story += [Spacer(1, 5 * mm), k.para(t("Répartition indicative : environ 10 % du temps pour l'accueil, le retour au calme et le bilan. "
                                         "À adapter à votre terrain."), "muted")]
    return build(story, title)
