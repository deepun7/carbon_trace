import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("data", exist_ok=True)
pdf_path = os.path.join("data", "sample_reliance_brsr_p6.pdf")

doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle",
    parent=styles["Heading1"],
    fontSize=16,
    leading=20,
    textColor=colors.HexColor("#1A365D"),
    spaceAfter=10,
)
heading_style = ParagraphStyle(
    "HeadingStyle",
    parent=styles["Heading2"],
    fontSize=13,
    leading=16,
    textColor=colors.HexColor("#2B6CB0"),
    spaceBefore=12,
    spaceAfter=6,
)
body_style = ParagraphStyle(
    "BodyStyle",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#2D3748"),
    spaceAfter=6,
)

story = []

story.append(Paragraph("BUSINESS RESPONSIBILITY & SUSTAINABILITY REPORT (BRSR)", title_style))
story.append(Paragraph("<b>Company Name:</b> Reliance Industries Limited &nbsp;|&nbsp; <b>CIN:</b> L17110MH1973PLC019786", body_style))
story.append(Paragraph("<b>Reporting Period:</b> Financial Year 2022-2023 (April 1, 2022 to March 31, 2023)", body_style))
story.append(Spacer(1, 12))

story.append(Paragraph("SECTION C: PRINCIPLE-WISE PERFORMANCE DISCLOSURE", heading_style))
story.append(Paragraph("<b>PRINCIPLE 6: Businesses should respect and make efforts to protect and restore the environment</b>", heading_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Essential Indicators: Energy & Greenhouse Gas (GHG) Telemetry</b>", body_style))
story.append(Paragraph("1. Details of total energy consumption (in Joules or multiples) and energy intensity:", body_style))

energy_data = [
    ["Parameter", "FY 2022-23 (Current Financial Year)", "FY 2021-22 (Previous Financial Year)"],
    ["Total electricity consumption (A) (GJ)", "312,500,000", "298,400,000"],
    ["Total fuel consumption (B) (GJ)", "812,500,000", "785,100,000"],
    ["Energy consumption through other sources (C) (GJ)", "0", "0"],
    ["Total energy consumption (A+B+C) (GJ)", "1,125,000,000", "1,083,500,000"],
]

t_energy = Table(energy_data, colWidths=[240, 140, 140])
t_energy.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A202C")),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
]))
story.append(t_energy)
story.append(Spacer(1, 14))

story.append(Paragraph("2. Details of greenhouse gas emissions (Scope 1 and Scope 2 emissions) & its intensity:", body_style))

ghg_data = [
    ["Parameter", "Unit", "FY 2022-23 (Current Financial Year)", "FY 2021-22 (Previous Financial Year)"],
    ["Total Scope 1 emissions (Metric tonnes of CO2 equivalent)", "tCO2e", "27,650,000.0", "26,820,000.0"],
    ["Total Scope 2 emissions (Metric tonnes of CO2 equivalent)", "tCO2e", "9,420,000.0", "9,150,000.0"],
    ["Total Scope 1 and Scope 2 emissions", "tCO2e", "37,070,000.0", "35,970,000.0"],
]

t_ghg = Table(ghg_data, colWidths=[200, 50, 135, 135])
t_ghg.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A202C")),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
]))
story.append(t_ghg)
story.append(Spacer(1, 14))

story.append(Paragraph("SECTION C: PRINCIPLE 7: Businesses, when engaging in influencing public and regulatory policy, should do so in a manner that is responsible and transparent", heading_style))
story.append(Paragraph("Essential Indicators: Details of affiliations with trade and industry chambers/associations...", body_style))

doc.build(story)
print(f"Generated sample BRSR PDF filing at: {pdf_path}")

