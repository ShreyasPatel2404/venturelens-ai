"""
VentureLens AI — Branded PDF Generator
Uses ReportLab to produce a professional investment report PDF.
Install: pip install reportlab
"""

import re
from datetime import date
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, HRFlowable, PageBreak,
)

# ── Brand colours ──────────────────────────────────────────────────────────────
AMBER   = colors.HexColor("#F59E0B")
DARK    = colors.HexColor("#030712")
GRAY900 = colors.HexColor("#111827")
GRAY700 = colors.HexColor("#374151")
GRAY300 = colors.HexColor("#D1D5DB")
WHITE   = colors.white
EMERALD = colors.HexColor("#34D399")
RED     = colors.HexColor("#F87171")

SCORE_LABEL_MAP = {
    "market_opportunity":      "Market Opportunity",
    "team_strength":           "Team Strength",
    "product_differentiation": "Product Differentiation",
    "traction":                "Traction",
    "financial_health":        "Financial Health",
}

VERDICT_COLORS = {
    "STRONG BUY": colors.HexColor("#059669"),
    "BUY":        colors.HexColor("#10B981"),
    "PROMISING":  colors.HexColor("#D97706"),
    "HOLD":       colors.HexColor("#CA8A04"),
    "NEUTRAL":    GRAY700,
    "RISKY":      colors.HexColor("#EA580C"),
    "PASS":       colors.HexColor("#DC2626"),
}


def _header_footer(canvas, doc):
    """Draw branded header/footer on every page."""
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(DARK)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)

    # Logo mark
    canvas.setFillColor(AMBER)
    canvas.roundRect(1 * cm, h - 0.95 * cm, 0.6 * cm, 0.6 * cm, 3, fill=1, stroke=0)
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(1.3 * cm, h - 0.72 * cm, "V")

    # Product name
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.9 * cm, h - 0.72 * cm, "VENTURELENS AI")

    # Page number
    canvas.setFillColor(GRAY300)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(w - 1 * cm, h - 0.72 * cm, f"Page {doc.page}")

    # Footer
    canvas.setFillColor(GRAY700)
    canvas.rect(0, 0, w, 0.8 * cm, fill=1, stroke=0)
    canvas.setFillColor(GRAY300)
    canvas.setFont("Helvetica", 6)
    canvas.drawString(1 * cm, 0.28 * cm,
        "CONFIDENTIAL — VentureLens AI Investment Report. Not financial advice.")
    canvas.drawRightString(w - 1 * cm, 0.28 * cm, f"© {date.today().year} VentureLens AI")

    canvas.restoreState()


def generate_pdf(result: dict, markdown_text: str = "") -> bytes:
    """
    Generate a branded PDF for one analysis result.
    Returns raw PDF bytes.
    """
    buf = BytesIO()

    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=1.5 * cm,
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=frame, onPage=_header_footer)
    ])

    styles = getSampleStyleSheet()

    # ── Custom styles ──────────────────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    title_style   = S("VLTitle",  fontSize=28, leading=34, textColor=WHITE,
                       fontName="Helvetica-Bold", spaceAfter=6)
    sub_style     = S("VLSub",    fontSize=11, leading=16, textColor=AMBER,
                       fontName="Helvetica-Bold", spaceAfter=4)
    h2_style      = S("VLH2",     fontSize=9,  leading=12, textColor=AMBER,
                       fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=16,
                       textTransform="uppercase", letterSpacing=2)
    h3_style      = S("VLH3",     fontSize=11, leading=14, textColor=WHITE,
                       fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=8)
    body_style    = S("VLBody",   fontSize=9,  leading=14, textColor=GRAY300,
                       fontName="Helvetica",   spaceAfter=6)
    bullet_style  = S("VLBullet", fontSize=9,  leading=13, textColor=GRAY300,
                       fontName="Helvetica",   spaceAfter=3, leftIndent=12,
                       bulletIndent=0, bulletText="▸")
    caption_style = S("VLCaption",fontSize=7,  leading=10, textColor=GRAY700,
                       fontName="Helvetica",   spaceAfter=2, alignment=TA_CENTER)
    meta_style    = S("VLMeta",   fontSize=8,  leading=12, textColor=GRAY300,
                       fontName="Helvetica",   alignment=TA_CENTER)

    story = []

    # ── COVER PAGE ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))

    # Dark background block simulated with a Table
    verdict      = result.get("verdict", "NEUTRAL")
    verdict_col  = VERDICT_COLORS.get(verdict, GRAY700)
    score        = result.get("overall_score", 0)
    startup_name = result.get("startup_name", "Unknown")

    cover_data = [[Paragraph(
        f'<font color="#F59E0B"><b>INVESTMENT ANALYSIS REPORT</b></font>', sub_style
    )]]
    cover_tbl = Table(cover_data, colWidths=[doc.width])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), DARK),
        ("TOPPADDING",  (0,0), (-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1), 14),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [8,8,8,8]),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(startup_name, title_style))
    story.append(Spacer(1, 0.3 * cm))

    # Score + verdict badge row
    badge_data = [[
        Paragraph(f'<b>{score}</b><br/><font size="7" color="#9CA3AF">OVERALL SCORE</font>',
                  S("sc", fontSize=28, leading=34, textColor=WHITE, fontName="Helvetica-Bold",
                    alignment=TA_CENTER)),
        Paragraph(f'<b>{verdict}</b>',
                  S("vd", fontSize=14, leading=18, textColor=WHITE, fontName="Helvetica-Bold",
                    alignment=TA_CENTER)),
    ]]
    badge_tbl = Table(badge_data, colWidths=[doc.width * 0.3, doc.width * 0.7])
    badge_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), GRAY900),
        ("BACKGROUND",    (1,0), (1,0), verdict_col),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [6,6,6,6]),
    ]))
    story.append(badge_tbl)
    story.append(Spacer(1, 0.5 * cm))

    # Meta info
    industry = result.get("industry", "")
    stage    = result.get("stage", "")
    story.append(Paragraph(
        f'{industry}  ·  {stage.upper()}  ·  {date.today().strftime("%B %d, %Y")}',
        meta_style
    ))
    story.append(Spacer(1, 0.8 * cm))

    # ── SCORES TABLE ───────────────────────────────────────────────────────────
    story.append(Paragraph("DIMENSION SCORES", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY700, spaceAfter=8))

    scores = result.get("scores", {})
    score_rows = [["Dimension", "Score", "Rating"]]
    for key, label in SCORE_LABEL_MAP.items():
        val = scores.get(key, 0)
        bar = "█" * (val // 10) + "░" * (10 - val // 10)
        rating = "Excellent" if val >= 80 else "Good" if val >= 65 else "Fair" if val >= 50 else "Weak"
        score_rows.append([label, str(val), f"{bar}  {rating}"])

    score_tbl = Table(score_rows, colWidths=[doc.width * 0.4, doc.width * 0.1, doc.width * 0.5])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), AMBER),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("TEXTCOLOR",     (0,1), (-1,-1), GRAY300),
        ("BACKGROUND",    (0,1), (-1,-1), GRAY900),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [GRAY900, colors.HexColor("#0D1117")]),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.25, GRAY700),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 0.8 * cm))

    # ── SUMMARY ────────────────────────────────────────────────────────────────
    story.append(Paragraph("EXECUTIVE SUMMARY", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY700, spaceAfter=8))
    summary = result.get("summary", "")
    if summary:
        story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 0.6 * cm))

    # ── GREEN / RED FLAGS ──────────────────────────────────────────────────────
    green_flags = result.get("green_flags", [])
    red_flags   = result.get("red_flags", [])

    if green_flags or red_flags:
        flags_data = [
            [Paragraph("✓ GREEN FLAGS", S("gh", fontSize=8, fontName="Helvetica-Bold",
                        textColor=EMERALD, leading=12)),
             Paragraph("✗ RED FLAGS", S("rh", fontSize=8, fontName="Helvetica-Bold",
                        textColor=RED, leading=12))],
            [
                "\n".join(f"▸ {f}" for f in green_flags),
                "\n".join(f"▸ {f}" for f in red_flags),
            ]
        ]
        flags_tbl = Table(flags_data, colWidths=[doc.width / 2 - 0.3*cm, doc.width / 2 - 0.3*cm],
                          spaceBefore=4)
        flags_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1), colors.HexColor("#052E16")),
            ("BACKGROUND",    (1,0), (1,-1), colors.HexColor("#1C0A0A")),
            ("TEXTCOLOR",     (0,1), (0,-1), GRAY300),
            ("TEXTCOLOR",     (1,1), (1,-1), GRAY300),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("LEADING",       (0,1), (-1,-1), 13),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("GRID",          (0,0), (-1,-1), 0.25, GRAY700),
        ]))
        story.append(flags_tbl)
        story.append(Spacer(1, 0.8 * cm))

    # ── FULL REPORT (from markdown) ────────────────────────────────────────────
    if markdown_text:
        story.append(PageBreak())
        story.append(Paragraph("FULL INVESTMENT REPORT", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=AMBER, spaceAfter=12))

        for line in markdown_text.splitlines():
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            if line.startswith("# "):
                story.append(Paragraph(line[2:], h3_style))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], h2_style))
            elif line.startswith("### "):
                story.append(Paragraph(line[4:], h3_style))
            elif line.startswith(("- ", "* ", "▸ ")):
                text = line.lstrip("-*▸ ")
                text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
                story.append(Paragraph(f"▸ {text}", bullet_style))
            elif line.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.25, color=GRAY700,
                                         spaceAfter=6, spaceBefore=6))
            else:
                line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
                line = re.sub(r"\*(.+?)\*",   r"<i>\1</i>", line)
                story.append(Paragraph(line, body_style))

    # ── DISCLAIMER ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.25, color=GRAY700, spaceAfter=6))
    story.append(Paragraph(
        "This report is generated by AI and is for informational purposes only. "
        "It does not constitute financial advice. Always conduct your own due diligence.",
        caption_style,
    ))

    doc.build(story)
    return buf.getvalue()