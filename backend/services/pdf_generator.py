"""
VentureLens AI — Branded PDF Generator (DAY 7 — fixed bullet/bold formatting)
Strips **bold** and *italic* markdown before rendering so no raw markers appear.
"""

import re
from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, HRFlowable, PageBreak,
)

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


def _clean(text: str) -> str:
    """Strip markdown markers so ReportLab doesn't show raw **bold** syntax."""
    # Convert **bold** → ReportLab <b> tag
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Convert *italic* → ReportLab <i> tag
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Strip remaining lone * or # characters at line start
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Strip HTML entities that look bad in PDF
    text = text.replace("&amp;", "&").replace("&;", "")
    return text.strip()


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(DARK)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.roundRect(1 * cm, h - 0.95 * cm, 0.6 * cm, 0.6 * cm, 3, fill=1, stroke=0)
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(1.3 * cm, h - 0.72 * cm, "V")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.9 * cm, h - 0.72 * cm, "VENTURELENS AI")
    canvas.setFillColor(GRAY300)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(w - 1 * cm, h - 0.72 * cm, f"Page {doc.page}")
    canvas.setFillColor(GRAY700)
    canvas.rect(0, 0, w, 0.8 * cm, fill=1, stroke=0)
    canvas.setFillColor(GRAY300)
    canvas.setFont("Helvetica", 6)
    canvas.drawString(1 * cm, 0.28 * cm, "CONFIDENTIAL — VentureLens AI. Not financial advice.")
    canvas.drawRightString(w - 1 * cm, 0.28 * cm, f"© {date.today().year} VentureLens AI")
    canvas.restoreState()


def generate_pdf(result: dict, markdown_text: str = "") -> bytes:
    buf = BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=1.5*cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_header_footer)])

    def S(name, **kw): return ParagraphStyle(name, **kw)

    title_style   = S("T",  fontSize=28, leading=34, textColor=WHITE, fontName="Helvetica-Bold", spaceAfter=6)
    sub_style     = S("Su", fontSize=11, leading=16, textColor=AMBER,  fontName="Helvetica-Bold", spaceAfter=4)
    h2_style      = S("H2", fontSize=9,  leading=12, textColor=AMBER,  fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=16)
    h3_style      = S("H3", fontSize=11, leading=14, textColor=WHITE,  fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=8)
    body_style    = S("B",  fontSize=9,  leading=14, textColor=GRAY300, fontName="Helvetica",     spaceAfter=6)
    bullet_style  = S("Bu", fontSize=9,  leading=13, textColor=GRAY300, fontName="Helvetica",     spaceAfter=3, leftIndent=12)
    caption_style = S("Ca", fontSize=7,  leading=10, textColor=GRAY700, fontName="Helvetica",     spaceAfter=2, alignment=TA_CENTER)
    meta_style    = S("M",  fontSize=8,  leading=12, textColor=GRAY300, fontName="Helvetica",     alignment=TA_CENTER)

    story = []
    story.append(Spacer(1, 1.5*cm))

    verdict     = result.get("verdict", "NEUTRAL")
    verdict_col = VERDICT_COLORS.get(verdict, GRAY700)
    score       = result.get("overall_score", 0)
    name        = result.get("startup_name", "Unknown")

    # Cover header
    cover_tbl = Table([[Paragraph('<font color="#F59E0B"><b>INVESTMENT ANALYSIS REPORT</b></font>', sub_style)]],
                      colWidths=[doc.width])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), DARK),
        ("TOPPADDING", (0,0),(-1,-1), 14), ("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1), 16),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 0.3*cm))

    badge_tbl = Table([[
        Paragraph(f'<b>{score}</b><br/><font size="7" color="#9CA3AF">OVERALL SCORE</font>',
                  S("sc", fontSize=28, leading=34, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f'<b>{verdict}</b>',
                  S("vd", fontSize=14, leading=18, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]], colWidths=[doc.width*0.3, doc.width*0.7])
    badge_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), GRAY900), ("BACKGROUND",(1,0),(1,0), verdict_col),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),14), ("BOTTOMPADDING",(0,0),(-1,-1),14),
    ]))
    story.append(badge_tbl)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f'{result.get("industry","")}  ·  {result.get("stage","").upper()}  ·  {date.today().strftime("%B %d, %Y")}',
        meta_style))
    story.append(Spacer(1, 0.8*cm))

    # Scores table
    story.append(Paragraph("DIMENSION SCORES", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY700, spaceAfter=8))
    scores = result.get("scores", {})
    rows = [["Dimension", "Score", "Rating"]]
    for key, label in SCORE_LABEL_MAP.items():
        val = scores.get(key, 0)
        bar = "█"*(val//10) + "░"*(10-val//10)
        rating = "Excellent" if val>=80 else "Good" if val>=65 else "Fair" if val>=50 else "Weak"
        rows.append([label, str(val), f"{bar}  {rating}"])
    score_tbl = Table(rows, colWidths=[doc.width*0.4, doc.width*0.1, doc.width*0.5])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), DARK), ("TEXTCOLOR",(0,0),(-1,0), AMBER),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),8),
        ("TEXTCOLOR",(0,1),(-1,-1), GRAY300),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY900, colors.HexColor("#0D1117")]),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("GRID",(0,0),(-1,-1),0.25,GRAY700),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 0.8*cm))

    # Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY700, spaceAfter=8))
    summary = _clean(result.get("summary", ""))
    if summary:
        story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 0.6*cm))

    # Flags
    green_flags = result.get("green_flags", [])
    red_flags   = result.get("red_flags", [])
    if green_flags or red_flags:
        flags_tbl = Table([[
            Paragraph("✓ GREEN FLAGS", S("gh", fontSize=8, fontName="Helvetica-Bold", textColor=EMERALD, leading=12)),
            Paragraph("✗ RED FLAGS",   S("rh", fontSize=8, fontName="Helvetica-Bold", textColor=RED,     leading=12)),
        ],[
            "\n".join(f"▸ {_clean(f)}" for f in green_flags),
            "\n".join(f"▸ {_clean(f)}" for f in red_flags),
        ]], colWidths=[doc.width/2-0.3*cm, doc.width/2-0.3*cm], spaceBefore=4)
        flags_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,-1), colors.HexColor("#052E16")),
            ("BACKGROUND",(1,0),(1,-1), colors.HexColor("#1C0A0A")),
            ("TEXTCOLOR",(0,1),(0,-1), GRAY300), ("TEXTCOLOR",(1,1),(1,-1), GRAY300),
            ("FONTSIZE",(0,0),(-1,-1),8), ("LEADING",(0,1),(-1,-1),13),
            ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("GRID",(0,0),(-1,-1),0.25,GRAY700),
        ]))
        story.append(flags_tbl)
        story.append(Spacer(1, 0.8*cm))

    # Full markdown report
    if markdown_text:
        story.append(PageBreak())
        story.append(Paragraph("FULL INVESTMENT REPORT", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=AMBER, spaceAfter=12))

        for line in markdown_text.splitlines():
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4)); continue
            if line.startswith("# "):
                story.append(Paragraph(_clean(line[2:]), h3_style))
            elif line.startswith("## ") or line.startswith("### "):
                text = line.lstrip("# ")
                story.append(Paragraph(_clean(text), h2_style))
            elif line.startswith(("- ", "* ", "▸ ")):
                text = line.lstrip("-*▸ ")
                story.append(Paragraph(f"▸ {_clean(text)}", bullet_style))
            elif line.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.25, color=GRAY700, spaceAfter=6, spaceBefore=6))
            else:
                story.append(Paragraph(_clean(line), body_style))

    # Disclaimer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.25, color=GRAY700, spaceAfter=6))
    story.append(Paragraph(
        "AI-generated report for informational purposes only. Not financial advice. Conduct your own due diligence.",
        caption_style))

    doc.build(story)
    return buf.getvalue()