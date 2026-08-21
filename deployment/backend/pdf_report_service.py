"""
Alture AI — Enterprise ATS Audit Report PDF Generator
======================================================
Generates an executive, publication-quality 1-2 page PDF ATS Audit Report
detailing ATS Compatibility Score, Semantic Alignment, Matched/Missing Skills,
and Actionable Optimization Strategies.
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_ats_audit_pdf(
    candidate_name: str,
    job_title: str,
    company: str,
    location: str,
    ats_score: float,
    fit_tier: str,
    matched_skills: list,
    missing_skills: list,
    tips: list = None,
    overall_assessment: str = ""
) -> bytes:
    """
    Generate and return bytes of a branded ATS Audit Report PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    COLOR_PRIMARY = colors.HexColor("#0284c7")
    COLOR_DARK = colors.HexColor("#0f172a")
    COLOR_MUTED = colors.HexColor("#64748b")
    COLOR_SUCCESS_BG = colors.HexColor("#f0fdf4")
    COLOR_SUCCESS_TXT = colors.HexColor("#166534")
    COLOR_WARN_BG = colors.HexColor("#fef2f2")
    COLOR_WARN_TXT = colors.HexColor("#991b1b")
    COLOR_CARD_BG = colors.HexColor("#f8fafc")
    COLOR_BORDER = colors.HexColor("#e2e8f0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_DARK
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=COLOR_MUTED
    )

    section_header_style = ParagraphStyle(
        'SecHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # 1. Header Table (Brand Logo & Report Title)
    header_data = [
        [
            Paragraph("<b>ALTURE AI</b><br/><font size='8' color='#64748b'>Enterprise ATS Intelligence & Resume Audit</font>", title_style),
            Paragraph(f"<font color='#0284c7'><b>OFFICIAL ATS AUDIT REPORT</b></font><br/><font size='8' color='#64748b'>Date: {datetime.now().strftime('%B %d, %Y')}<br/>Engine: Hybrid NLP v2.0 (SBERT+XGB)</font>", ParagraphStyle('RightH', parent=subtitle_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceBefore=4, spaceAfter=10))

    # 2. Executive Candidate & Job Target Summary Card
    summary_data = [
        [
            Paragraph(f"<b>Candidate:</b> {candidate_name}", body_style),
            Paragraph(f"<b>Target Position:</b> {job_title}", body_style)
        ],
        [
            Paragraph(f"<b>Document Status:</b> Verified PDF/DOCX Parser", body_style),
            Paragraph(f"<b>Employer / Location:</b> {company} ({location})", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[270, 270])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # 3. Overall Compatibility Score Banner
    score_color_hex = "#16a34a" if ats_score >= 60 else ("#d97706" if ats_score >= 35 else "#dc2626")
    tier_badge = f"<font color='{score_color_hex}'><b>{fit_tier.upper()}</b></font>"

    score_box_data = [
        [
            Paragraph(f"<font size='26' color='{score_color_hex}'><b>{ats_score:.1f}%</b></font><br/><font size='8' color='#64748b'>ATS COMPATIBILITY SCORE</font>", ParagraphStyle('ScoreC', alignment=1)),
            Paragraph(f"<b>Compatibility Assessment:</b> {tier_badge}<br/><br/><font size='8.5' color='#475569'>{overall_assessment or f'This resume exhibits strong alignment across {len(matched_skills)} core technical competencies with actionable optimization opportunities.'}</font>", body_style)
        ]
    ]
    score_table = Table(score_box_data, colWidths=[150, 390])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdfa")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#99f6e4")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # 4. Multi-Modal Technical Skills Analysis (Matched vs Missing)
    elements.append(Paragraph("1. Technical Competency & Skill Gap Analysis", section_header_style))
    
    matched_text = ", ".join(matched_skills) if matched_skills else "No direct keyword matches found (general semantic match)"
    missing_text = ", ".join(missing_skills) if missing_skills else "None! Excellent coverage of all required skills."

    skills_data = [
        [
            Paragraph(f"<font color='{COLOR_SUCCESS_TXT}'><b>MATCHED SKILLS ({len(matched_skills)} Verified):</b></font>", bold_body),
            Paragraph(f"<font color='{COLOR_WARN_TXT}'><b>CRITICAL SKILL GAPS ({len(missing_skills)} Missing):</b></font>", bold_body)
        ],
        [
            Paragraph(f"<font color='{COLOR_SUCCESS_TXT}'>{matched_text}</font>", body_style),
            Paragraph(f"<font color='{COLOR_WARN_TXT}'>{missing_text}</font>", body_style)
        ]
    ]
    skills_table = Table(skills_data, colWidths=[265, 275])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,1), COLOR_SUCCESS_BG),
        ('BACKGROUND', (1,0), (1,1), COLOR_WARN_BG),
        ('BOX', (0,0), (0,1), 1, colors.HexColor("#bbf7d0")),
        ('BOX', (1,0), (1,1), 1, colors.HexColor("#fecaca")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(skills_table)
    elements.append(Spacer(1, 12))

    # 5. Gemini AI Coach Strategic Recommendations
    elements.append(Paragraph("2. Strategic Optimization Plan & Actionable Recommendations", section_header_style))

    tips_rows = []
    if tips and isinstance(tips, list):
        for idx, t in enumerate(tips[:4]):
            t_title = t.get("title", f"Recommendation {idx+1}") if isinstance(t, dict) else str(t)
            t_detail = t.get("detail", "") if isinstance(t, dict) else ""
            prio = t.get("priority", "medium").upper() if isinstance(t, dict) else "ACTION"
            
            prio_color = "#dc2626" if prio == "HIGH" else ("#d97706" if prio == "MEDIUM" else "#16a34a")
            tips_rows.append([
                Paragraph(f"<font color='{prio_color}'><b>[{prio}]</b></font>", bold_body),
                Paragraph(f"<b>{t_title}</b>: {t_detail}", body_style)
            ])
    else:
        # Default high-impact rules
        tips_rows = [
            [Paragraph("<font color='#dc2626'><b>[HIGH]</b></font>", bold_body), Paragraph("<b>Target Keyword Density</b>: Mirror required tools in your Experience section with exact terminology.", body_style)],
            [Paragraph("<font color='#d97706'><b>[MEDIUM]</b></font>", bold_body), Paragraph("<b>Quantifiable Metrics</b>: Quantify project scale, latency reduction, and architectural throughput.", body_style)],
            [Paragraph("<font color='#16a34a'><b>[LOW]</b></font>", bold_body), Paragraph("<b>Single-Column Layout</b>: Use clean single-column structure to ensure 100% ATS parser fidelity.", body_style)]
        ]

    tips_table = Table(tips_rows, colWidths=[65, 475])
    tips_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    elements.append(tips_table)
    elements.append(Spacer(1, 14))

    # 6. Certification & Verification Footer
    footer_text = Paragraph(
        "<font size='7.5' color='#94a3b8'>This report is dynamically synthesized by <b>Alture AI Multi-Modal NLP Intelligence Engine v2.0</b>. Analysis includes Sentence-BERT dense embeddings, Cross-Encoder joint attention, 500+ technical ontology matching, and XGBoost regressor scoring calibrated against real-world ATS benchmarks.</font>",
        ParagraphStyle('FooterText', alignment=1)
    )
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.8, color=COLOR_BORDER, spaceBefore=8, spaceAfter=6),
        footer_text
    ]))

    # Build PDF document
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
