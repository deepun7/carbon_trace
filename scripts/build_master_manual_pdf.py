"""
CARBONTRACE // TECHNICAL MASTER MANUAL & VISUAL UI EXAMINER'S GUIDE
Full Master Manual & Technical Blueprint Generator
Target Output: CarbonTrace_Master_Manual_A_to_Z.pdf
"""

import os
import sys
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# Import modular section builders
from manual_builder.section1 import build_section_1
from manual_builder.section2 import build_section_2
from manual_builder.section3 import build_section_3
from manual_builder.section4 import build_section_4
from manual_builder.section5 import build_section_5
from manual_builder.section6 import build_section_6

# ----------------------------------------------------------------------
# 1. LUXURY EDITORIAL COLOR PALETTE
# ----------------------------------------------------------------------
COLOR_ESPRESSO = colors.HexColor("#1A110B")
COLOR_MOCHA = colors.HexColor("#3E2723")
COLOR_CHAMPAGNE = colors.HexColor("#C89B3C")
COLOR_LIGHT_GOLD = colors.HexColor("#F4D9A0")
COLOR_AMBER = colors.HexColor("#C8792C")
COLOR_PARCHMENT = colors.HexColor("#FAF8F5")
COLOR_DARK_TEXT = colors.HexColor("#212121")
COLOR_MUTED_TEXT = colors.HexColor("#5D4037")
COLOR_BORDER = colors.HexColor("#D7CCC8")
COLOR_LIGHT_BG = colors.HexColor("#F7F5F0")
COLOR_CARD_BG = colors.HexColor("#FFFFFF")
COLOR_ACCENT_GREEN = colors.HexColor("#2E7D32")
COLOR_ACCENT_BLUE = colors.HexColor("#1565C0")
COLOR_WARN_BG = colors.HexColor("#FFF8E1")
COLOR_WARN_BORDER = colors.HexColor("#FFE082")
COLOR_CODE_BG = colors.HexColor("#211914")

COLORS_DICT = {
    "espresso": COLOR_ESPRESSO,
    "mocha": COLOR_MOCHA,
    "champagne": COLOR_CHAMPAGNE,
    "light_gold": COLOR_LIGHT_GOLD,
    "amber": COLOR_AMBER,
    "parchment": COLOR_PARCHMENT,
    "dark_text": COLOR_DARK_TEXT,
    "muted_text": COLOR_MUTED_TEXT,
    "border": COLOR_BORDER,
    "light_bg": COLOR_LIGHT_BG,
    "card_bg": COLOR_CARD_BG,
    "accent_green": COLOR_ACCENT_GREEN,
    "accent_blue": COLOR_ACCENT_BLUE,
    "warn_bg": COLOR_WARN_BG,
    "warn_border": COLOR_WARN_BORDER,
    "code_bg": COLOR_CODE_BG,
}

# ----------------------------------------------------------------------
# 2. NUMBERED CANVAS WITH RUNNING HEADERS & FOOTERS
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress on cover page

        self.saveState()
        
        # Running Top Header
        self.setFont("Helvetica-Bold", 7.2)
        self.setFillColor(COLOR_MOCHA)
        self.drawString(36, 762, "CARBONTRACE // TECHNICAL MASTER MANUAL & BLUEPRINT")
        self.setFont("Helvetica", 7.2)
        self.setFillColor(COLOR_MUTED_TEXT)
        self.drawRightString(576, 762, "SEBI BRSR PRINCIPLE 6 & OWID MACRO-BENCHMARKING")
        self.setStrokeColor(COLOR_CHAMPAGNE)
        self.setLineWidth(0.75)
        self.line(36, 756, 576, 756)

        # Running Bottom Footer
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(36, 40, 576, 40)
        self.setFont("Helvetica", 7.2)
        self.setFillColor(COLOR_MUTED_TEXT)
        self.drawString(36, 28, "B.Tech CSE (AI/ML) Capstone • Autonomous 5-Agent Architecture • Confidential Examiner Manual")
        self.setFont("Helvetica-Bold", 7.2)
        self.setFillColor(COLOR_MOCHA)
        self.drawRightString(576, 28, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


# ----------------------------------------------------------------------
# 3. TYPOGRAPHY & PARAGRAPH STYLES
# ----------------------------------------------------------------------
def setup_styles():
    base = getSampleStyleSheet()
    styles = {
        "CoverSuper": ParagraphStyle(
            "CoverSuper",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=COLOR_CHAMPAGNE,
            spaceAfter=8,
        ),
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            textColor=COLOR_ESPRESSO,
            spaceAfter=10,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15.5,
            textColor=COLOR_MOCHA,
            spaceAfter=16,
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12.5,
            textColor=COLOR_DARK_TEXT,
        ),
        "CoverMetaBold": ParagraphStyle(
            "CoverMetaBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=12.5,
            textColor=COLOR_ESPRESSO,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=COLOR_ESPRESSO,
            spaceBefore=12,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "SectionSub": ParagraphStyle(
            "SectionSub",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=13,
            textColor=COLOR_MUTED_TEXT,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "SubSectionHeading": ParagraphStyle(
            "SubSectionHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=COLOR_MOCHA,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "SubSubSectionHeading": ParagraphStyle(
            "SubSubSectionHeading",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=COLOR_AMBER,
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=12,
            textColor=COLOR_DARK_TEXT,
            spaceAfter=5,
        ),
        "BodyBold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.2,
            leading=12,
            textColor=COLOR_ESPRESSO,
            spaceAfter=5,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=12,
            textColor=COLOR_DARK_TEXT,
            leftIndent=12,
            spaceAfter=3,
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=10,
            textColor=COLOR_PARCHMENT,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9.8,
            textColor=COLOR_DARK_TEXT,
        ),
        "TableCellBold": ParagraphStyle(
            "TableCellBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9.8,
            textColor=COLOR_ESPRESSO,
        ),
        "TableCellCode": ParagraphStyle(
            "TableCellCode",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=6.6,
            leading=8.8,
            textColor=COLOR_MOCHA,
        ),
        "CalloutText": ParagraphStyle(
            "CalloutText",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=11,
            textColor=COLOR_DARK_TEXT,
        ),
        "CalloutTitle": ParagraphStyle(
            "CalloutTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.2,
            leading=11.5,
            textColor=COLOR_AMBER,
            spaceAfter=2,
        ),
        "CodeBlock": ParagraphStyle(
            "CodeBlock",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=6.8,
            leading=9,
            textColor=colors.HexColor("#FAF0E6"),
        ),
        "FormulaBox": ParagraphStyle(
            "FormulaBox",
            parent=base["Normal"],
            fontName="Courier-Bold",
            fontSize=8,
            leading=11,
            textColor=COLOR_ESPRESSO,
            alignment=1,
        ),
        "ImageCaption": ParagraphStyle(
            "ImageCaption",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=COLOR_MOCHA,
            alignment=1,
            spaceBefore=3,
            spaceAfter=6,
        ),
        "QAQuestion": ParagraphStyle(
            "QAQuestion",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=12,
            textColor=COLOR_ESPRESSO,
            spaceBefore=6,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "QAAnswer": ParagraphStyle(
            "QAAnswer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11.5,
            textColor=COLOR_DARK_TEXT,
            spaceAfter=6,
        ),
    }
    return styles

# ----------------------------------------------------------------------
# 4. MAIN COMPILATION ENGINE
# ----------------------------------------------------------------------
def compile_master_manual():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    pdf_path = os.path.join(project_root, "CarbonTrace_Master_Manual_A_to_Z.pdf")
    screenshots_dir = os.path.join(project_root, "manual_assets", "screenshots")

    print("=" * 70)
    print("CARBONTRACE // COMPILING TECHNICAL MASTER MANUAL & BLUEPRINT")
    print(f"Target Output Path: {pdf_path}")
    print(f"Screenshots Directory: {screenshots_dir}")
    print("=" * 70)

    # Document Geometry: Letter size (612 x 792 pt), 36 pt (0.5 in) margins
    # Printable area: 540 x 720 pt
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=46,
    )

    styles = setup_styles()

    story = []

    print("[1/6] Building Section 1: Executive Summary & Beginner Foundation...")
    story.extend(build_section_1(styles, COLORS_DICT))

    print("[2/6] Building Section 2: Architectural Decisions & Alternatives Matrix...")
    story.extend(build_section_2(styles, COLORS_DICT))

    print("[3/6] Building Section 3: Pin-to-Pin Code, Math & ITC Worked Proofs...")
    story.extend(build_section_3(styles, COLORS_DICT))

    print("[4/6] Building Section 4: Visual UI Guide & Numbered Component Encyclopedia [1]–[25]...")
    story.extend(build_section_4(styles, COLORS_DICT, screenshots_dir))

    print("[5/6] Building Section 5: Step-by-Step How to Run, Test & Deploy Manual...")
    story.extend(build_section_5(styles, COLORS_DICT))

    print("[6/6] Building Section 6: 36 Viva-Voce & Professor Defense Q&A Bank...")
    story.extend(build_section_6(styles, COLORS_DICT))

    print("Assembling document flowables with NumberedCanvas...")
    doc.build(story, canvasmaker=NumberedCanvas)

    if os.path.exists(pdf_path):
        size_bytes = os.path.getsize(pdf_path)
        size_mb = size_bytes / (1024 * 1024)
        print("=" * 70)
        print(f"[SUCCESS] Master Manual successfully generated!")
        print(f"File Path: {pdf_path}")
        print(f"File Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        print("=" * 70)
        return True
    else:
        print("[ERROR] PDF generation failed!")
        return False

if __name__ == "__main__":
    success = compile_master_manual()
    if not success:
        sys.exit(1)
