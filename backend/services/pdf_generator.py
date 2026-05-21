"""
VentureLens AI — Branded PDF Generator (DAY 7 Final)
White background with dark text for maximum readability.
Clean professional layout matching the 8-page report style.
"""

import re
from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether,
)

# ── Color palette — dark text on white for readability ────────────────────────
BLACK       = colors.HexColor("#0F172A")   # headings
DARK_GRAY   = colors.HexColor("#1E293B")   # body text
MID_GRAY    = colors.HexColor("#475569")   # captions / meta
LIGHT_GRAY  = colors.HexColor("#94A3B8")   # subtle labels
RULE_GRAY   = colors.HexColor("#CBD5E1")   # dividers
BG_LIGHT    = colors.HexColor("#F8FAFC")   # section backgrounds
BG_WHITE    = colors.white

AMBER       = colors.HexColor("#D97706")   # brand amber (darker for print)
AMBER_LIGHT = colors.HexColor("#FEF3C7")   # amber background tint
EMERALD     = colors.HexColor("#065F46")   # green flags text
EMERALD_BG  = colors.HexColor("#ECFDF5")   # green flags bg
RED_TEXT    = colors.HexColor("#991B1B")   # red flags text
RED_BG      = colors.HexColor("#FEF2F2")   # red flags bg
BLUE_DARK   = colors.HexColor("#1E3A5F")   # section header bg

VERDICT_COLORS = {
    "STRONG BUY": colors.HexColor("#065F46"),
    "BUY":        colors.HexColor("#047857"),
    "PROMISING":  colors.HexColor("#B45309"),
    "HOLD":       colors.HexColor("#78350F"),
    "NEUTRAL":    colors.HexColor("#374151"),
    "RISKY":      colors.HexColor("#9A3412"),
    "PASS":       colors.HexColor("#7F1D1D"),
}

VERDICT_BG = {
    "STRONG BUY": colors.HexColor("#ECFDF5"),
    "BUY":        colors.HexColor("#D1FAE5"),
    "PROMISING":  colors.HexColor("#FEF3C7"),
    "HOLD":       colors.HexColor("#FEF9C3"),
    "NEUTRAL":    colors.HexColor("#F3F4F6"),
    "RISKY":      colors.HexColor("#FFF7ED"),
    "PASS":       colors.HexColor("#FEF2F2"),
}

SCORE_LABEL_MAP = {
    "market_opportunity":      "Market Opportunity",
    "team_strength":           "Team Strength",
    "product_differentiation": "Product Differentiation",
    "traction":                "Traction",
    "financial_health":        "Financial Health",
}


def _clean(text: str) -> str:
    """Convert markdown to ReportLab XML tags, strip raw markers."""
    text = str(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",   r"<i>\1</i>", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = text.replace("&;", "").replace("&amp;", "&")
    # Escape bare & not part of XML entity
    text = re.sub(r"&(?!(?:amp|lt|gt|apos|quot|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)
    return text.strip()


def _score_color(val: int):
    if val >= 80: return colors.HexColor("#065F46")
    if val >= 65: return colors.HexColor("#B45309")
    if val >= 50: return colors.HexColor("#78350F")
    return colors.HexColor("#7F1D1D")


def _score_bar_color(val: int):
    if val >= 80: return colors.HexColor("#10B981")
    if val >= 65: return colors.HexColor("#F59E0B")
    if val >= 50: return colors.HexColor("#F97316")
    return colors.HexColor("#EF4444")


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Header — dark navy bar
    canvas.setFillColor(BLUE_DARK)
    canvas.rect(0, h - 1.4*cm, w, 1.4*cm, fill=1, stroke=0)

    # Logo mark
    canvas.setFillColor(AMBER)
    canvas.roundRect(1*cm, h - 1.1*cm, 0.7*cm, 0.7*cm, 4, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawCentredString(1.35*cm, h - 0.78*cm, "V")

    # Brand name
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(2*cm, h - 0.78*cm, "VENTURELENS AI")

    # Page number
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 1*cm, h - 0.78*cm, f"Page {doc.page}")

    # Footer
    canvas.setFillColor(colors.HexColor("#F1F5F9"))
    canvas.rect(0, 0, w, 0.9*cm, fill=1, stroke=0)
    canvas.setStrokeColor(RULE_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(0, 0.9*cm, w, 0.9*cm)
    canvas.setFillColor(MID_GRAY)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(1*cm, 0.32*cm, "CONFIDENTIAL — VentureLens AI Investment Report. Not financial advice.")
    canvas.drawRightString(w - 1*cm, 0.32*cm, f"© {date.today().year} VentureLens AI")

    canvas.restoreState()


def generate_pdf(result: dict, markdown_text: str = "") -> bytes:
    buf = BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=1.6*cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_header_footer)])

    def S(name, **kw): return ParagraphStyle(name, **kw)

    # ── Styles ─────────────────────────────────────────────────────────────────
    tag_style     = S("Tag",   fontSize=8,  leading=11, textColor=AMBER,
                       fontName="Helvetica-Bold", spaceAfter=4, tracking=80)
    title_style   = S("Title", fontSize=32, leading=38, textColor=BLACK,
                       fontName="Helvetica-Bold", spaceAfter=8)
    meta_style    = S("Meta",  fontSize=10, leading=14, textColor=MID_GRAY,
                       fontName="Helvetica",  spaceAfter=4)
    h2_style      = S("H2",    fontSize=8,  leading=11, textColor=colors.white,
                       fontName="Helvetica-Bold", spaceAfter=0, spaceBefore=0,
                       leftIndent=6)
    h3_style      = S("H3",    fontSize=12, leading=16, textColor=BLACK,
                       fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)
    body_style    = S("Body",  fontSize=9.5, leading=15, textColor=DARK_GRAY,
                       fontName="Helvetica", spaceAfter=6, alignment=TA_JUSTIFY)
    bullet_style  = S("Bul",  fontSize=9.5, leading=15, textColor=DARK_GRAY,
                       fontName="Helvetica", spaceAfter=4,
                       leftIndent=14, firstLineIndent=-10)
    caption_style = S("Cap",  fontSize=7,  leading=10, textColor=MID_GRAY,
                       fontName="Helvetica", spaceAfter=2, alignment=TA_CENTER)
    label_style   = S("Lbl",  fontSize=7.5, leading=10, textColor=LIGHT_GRAY,
                       fontName="Helvetica-Bold", spaceAfter=2, tracking=60)

    story = []
    verdict      = result.get("verdict", "NEUTRAL")
    score        = result.get("overall_score", 0)
    name         = result.get("startup_name", "Unknown")
    industry     = result.get("industry", "")
    stage        = result.get("stage", "").upper()
    v_color      = VERDICT_COLORS.get(verdict, DARK_GRAY)
    v_bg         = VERDICT_BG.get(verdict, BG_LIGHT)

    # ── COVER ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))

    # Tag line
    story.append(Paragraph("INVESTMENT ANALYSIS REPORT", tag_style))
    story.append(Spacer(1, 0.3*cm))

    # Company name
    story.append(Paragraph(name, title_style))

    # Meta row
    story.append(Paragraph(
        f'{industry}  ·  {stage}  ·  {date.today().strftime("%B %d, %Y")}',
        meta_style))
    story.append(Spacer(1, 0.5*cm))

    # Score + verdict card
    score_tbl = Table([[
        # Score cell
        Paragraph(
            f'<font size="40" color="#0F172A"><b>{score}</b></font><br/>'
            f'<font size="8" color="#94A3B8">OVERALL SCORE</font>',
            S("sc", fontSize=40, leading=46, textColor=BLACK,
              fontName="Helvetica-Bold", alignment=TA_CENTER)),
        # Verdict cell
        Paragraph(
            f'<font size="18" color="{v_color.hexval() if hasattr(v_color,"hexval") else "#065F46"}"><b>{verdict}</b></font>',
            S("vd", fontSize=18, leading=24, fontName="Helvetica-Bold",
              alignment=TA_CENTER, textColor=v_color)),
    ]], colWidths=[doc.width*0.28, doc.width*0.72])

    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), BG_LIGHT),
        ("BACKGROUND",    (1,0),(1,0), v_bg),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 16),
        ("BOTTOMPADDING", (0,0),(-1,-1), 16),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("LINEABOVE",     (0,0),(-1,0), 2, AMBER),
        ("BOX",           (0,0),(-1,-1), 0.5, RULE_GRAY),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 0.8*cm))

    # ── DIMENSION SCORES ───────────────────────────────────────────────────────
    story.append(_section_header("DIMENSION SCORES", h2_style, doc.width))

    scores = result.get("scores", {})
    score_rows = [
        [Paragraph("<b>Dimension</b>", S("sh", fontSize=8, fontName="Helvetica-Bold",
                    textColor=colors.white, leading=11)),
         Paragraph("<b>Score</b>", S("sh2", fontSize=8, fontName="Helvetica-Bold",
                    textColor=colors.white, leading=11, alignment=TA_CENTER)),
         Paragraph("<b>Rating</b>", S("sh3", fontSize=8, fontName="Helvetica-Bold",
                    textColor=colors.white, leading=11))]
    ]
    for key, label in SCORE_LABEL_MAP.items():
        val = scores.get(key, 0)
        rating = "Excellent" if val>=80 else "Good" if val>=65 else "Fair" if val>=50 else "Weak"
        bar = "█" * (val//10) + "░" * (10 - val//10)
        score_rows.append([
            Paragraph(label, S("sl", fontSize=9, fontName="Helvetica", textColor=DARK_GRAY, leading=12)),
            Paragraph(f'<font color="{_score_color(val).hexval() if hasattr(_score_color(val),"hexval") else "#065F46"}"><b>{val}</b></font>',
                      S("sv", fontSize=11, fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
            Paragraph(f'<font color="#{_bar_hex(val)}">{bar}</font>  <font size="8" color="#64748B">{rating}</font>',
                      S("sb", fontSize=8, fontName="Helvetica", leading=11, textColor=DARK_GRAY)),
        ])

    st = Table(score_rows, colWidths=[doc.width*0.42, doc.width*0.1, doc.width*0.48])
    st.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), BLUE_DARK),
        ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BG_WHITE, BG_LIGHT]),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("GRID",          (0,0),(-1,-1), 0.3, RULE_GRAY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.7*cm))

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────────
    summary = _clean(result.get("summary", ""))
    if summary:
        story.append(_section_header("EXECUTIVE SUMMARY", h2_style, doc.width))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 0.5*cm))

    # ── FLAGS ──────────────────────────────────────────────────────────────────
    green_flags = result.get("green_flags", [])
    red_flags   = result.get("red_flags", [])

    def flag_cell(flags, text_color, bg_color, header):
        items = [Paragraph(f'<b>{header}</b>',
                    S("fh", fontSize=8, fontName="Helvetica-Bold",
                      textColor=text_color, leading=11))]
        for f in flags:
            items.append(Paragraph(f"▸  {_clean(f)}",
                S("fi", fontSize=8.5, fontName="Helvetica", textColor=DARK_GRAY,
                  leading=13, leftIndent=8, spaceAfter=3)))
        return items

    if green_flags or red_flags:
        flags_tbl = Table([[
            flag_cell(green_flags, EMERALD, EMERALD_BG, "✓  GREEN FLAGS"),
            flag_cell(red_flags,   RED_TEXT, RED_BG,   "✗  RED FLAGS"),
        ]], colWidths=[doc.width/2 - 0.2*cm, doc.width/2 - 0.2*cm], spaceBefore=4)
        flags_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(0,-1), EMERALD_BG),
            ("BACKGROUND",    (1,0),(1,-1), RED_BG),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("BOX",           (0,0),(0,-1), 0.5, colors.HexColor("#A7F3D0")),
            ("BOX",           (1,0),(1,-1), 0.5, colors.HexColor("#FECACA")),
        ]))
        story.append(flags_tbl)
        story.append(Spacer(1, 0.6*cm))

    # ── FULL REPORT (from markdown) ────────────────────────────────────────────
    if markdown_text:
        story.append(PageBreak())
        story.append(_section_header("FULL INVESTMENT REPORT", h2_style, doc.width))
        story.append(Spacer(1, 0.4*cm))

        for line in markdown_text.splitlines():
            line = line.strip()
            if not line:
                story.append(Spacer(1, 3)); continue

            if line.startswith("# "):
                story.append(Spacer(1, 6))
                story.append(Paragraph(_clean(line[2:]), h3_style))
            elif line.startswith("## ") or line.startswith("### "):
                text = line.lstrip("# ")
                story.append(Spacer(1, 4))
                story.append(_section_header(_clean(text).upper(), h2_style, doc.width))
                story.append(Spacer(1, 4))
            elif line.startswith(("- ", "* ", "▸ ", "■ ")):
                text = re.sub(r"^[-*▸■]+\s*", "", line)
                story.append(Paragraph(f"▸  {_clean(text)}", bullet_style))
            elif line.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.5,
                                         color=RULE_GRAY, spaceAfter=4, spaceBefore=4))
            else:
                story.append(Paragraph(_clean(line), body_style))

    # ── DISCLAIMER ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=RULE_GRAY, spaceAfter=6))
    story.append(Paragraph(
        "AI-generated for informational purposes only. Not financial advice. "
        "Always conduct your own due diligence before making investment decisions.",
        caption_style))

    doc.build(story)
    return buf.getvalue()


def _section_header(text: str, style, width: float):
    """Dark navy header bar with white text."""
    tbl = Table([[Paragraph(text, style)]], colWidths=[width])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BLUE_DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    return tbl


def _bar_hex(val: int) -> str:
    """Return hex color string for progress bar."""
    if val >= 80: return "10B981"
    if val >= 65: return "F59E0B"
    if val >= 50: return "F97316"
    return "EF4444"