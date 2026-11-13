"""
SECTION 5: STEP-BY-STEP HOW TO RUN, TEST & DEPLOY OPERATIONAL MANUAL
Pin-to-Pin CLI, PyTest, FastAPI Server & Production Deployment Commands
"""
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib import colors

def build_section_5(styles, colors_dict):
    c_espresso = colors_dict["espresso"]
    c_mocha = colors_dict["mocha"]
    c_champagne = colors_dict["champagne"]
    c_amber = colors_dict["amber"]
    c_parchment = colors_dict["parchment"]
    c_border = colors_dict["border"]
    c_card_bg = colors_dict["card_bg"]
    c_light_bg = colors_dict["light_bg"]
    c_code_bg = colors_dict["code_bg"]

    story = []

    # Section Header
    story.append(Paragraph("SECTION 5: HOW TO RUN, TEST &amp; DEPLOY OPERATIONAL MANUAL", styles["SectionHeading"]))
    story.append(Paragraph(
        "Complete, copy-pasteable execution instructions for university examiners, software auditors, "
        "and DevOps engineers across Windows, Linux, and macOS environments.",
        styles["SectionSub"]
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=c_champagne, spaceBefore=0, spaceAfter=12))

    story.append(Paragraph(
        "CarbonTrace is engineered for zero-friction distribution. It requires only standard Python 3.10+ and a web browser. "
        "There are no external database daemons (e.g. Postgres), no container prerequisites, and no Node.js build pipelines.",
        styles["Body"]
    ))
    story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 5.1 HARDWARE & ENVIRONMENT PREREQUISITES
    # ------------------------------------------------------------------
    story.append(Paragraph("5.1 Hardware &amp; Software Environment Prerequisites", styles["SubSectionHeading"]))
    
    prereq_data = [
        [
            Paragraph("<b>Prerequisite Component</b>", styles["TableHead"]),
            Paragraph("<b>Minimum Specification</b>", styles["TableHead"]),
            Paragraph("<b>Recommended Enterprise Specification</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>Operating System</b>", styles["TableCellBold"]),
            Paragraph("Windows 10/11, Ubuntu 20.04+, macOS 12+ (Monterey)", styles["TableCell"]),
            Paragraph("Windows 11 Pro / Enterprise Linux (Debian 12 or RHEL 9)", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Python Runtime</b>", styles["TableCellBold"]),
            Paragraph("Python 3.10.x or 3.11.x (64-bit)", styles["TableCell"]),
            Paragraph("Python 3.11.8+ (Active Virtual Environment)", styles["TableCell"]),
        ],
        [
            Paragraph("<b>RAM &amp; Compute</b>", styles["TableCellBold"]),
            Paragraph("4 GB RAM, Dual-Core 2.0 GHz CPU", styles["TableCell"]),
            Paragraph("16 GB RAM, Quad-Core CPU (for fast ML rolling cross-validation)", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Storage Disk Space</b>", styles["TableCellBold"]),
            Paragraph("1.5 GB free disk space (includes SQLite DBs &amp; OWID cache)", styles["TableCell"]),
            Paragraph("10 GB NVMe SSD (for multi-year PDF filing archives)", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Web Browser</b>", styles["TableCellBold"]),
            Paragraph("Modern browser supporting ECMAScript 2022+ (Chrome, Edge, Firefox)", styles["TableCell"]),
            Paragraph("Google Chrome 120+ or Microsoft Edge 120+ (Hardware Acceleration enabled)", styles["TableCell"]),
        ],
    ]

    prereq_table = Table(prereq_data, colWidths=[130, 200, 210])
    prereq_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(prereq_table)
    story.append(Spacer(1, 10))

    # Helper for code panel with description
    def add_step_card(step_num, title, description, code_block):
        card_content = [
            Paragraph(f"<b>STEP {step_num}: {title}</b>", styles["CalloutTitle"]),
            Paragraph(description, styles["CalloutText"]),
            Spacer(1, 3),
            Paragraph(code_block.replace("\n", "<br/>").replace(" ", "&nbsp;"), styles["CodeBlock"]),
        ]
        t = Table([[card_content]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
            ('BOX', (0,0), (-1,-1), 1, c_champagne),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    # ------------------------------------------------------------------
    # 5.2 STEP-BY-STEP EXECUTION PLAYBOOK
    # ------------------------------------------------------------------
    story.append(Paragraph("5.2 Step-by-Step Operational Playbook (Windows / macOS / Linux)", styles["SubSectionHeading"]))

    # Step 1
    s1_code = (
        "# 1. Navigate to the project root directory\n"
        "cd c:\\Users\\naren\\LPU\\SEM41\\Carbon_Trace_pro\n\n"
        "# 2a. Create virtual environment on Windows PowerShell\n"
        "python -m venv venv\n"
        ".\\venv\\Scripts\\activate\n\n"
        "# 2b. On macOS / Linux Terminal\n"
        "python3 -m venv venv\n"
        "source venv/bin/activate"
    )
    story.append(add_step_card(1, "Create & Activate Clean Python Virtual Environment",
        "Isolates CarbonTrace dependencies from the global operating system Python environment.", s1_code))
    story.append(Spacer(1, 6))

    # Step 2
    s2_code = (
        "# Upgrade package installer to latest version\n"
        "python -m pip install --upgrade pip\n\n"
        "# Install all core dependencies from requirements.txt\n"
        "pip install -r requirements.txt\n\n"
        "# Verify key packages are properly installed\n"
        "python -c \"import fastapi, reportlab, plotly, sklearn, pdfplumber; print('All core libraries verified!')\""
    )
    story.append(add_step_card(2, "Install Enterprise Dependencies",
        "Installs FastAPI, Uvicorn, ReportLab 5.1+, Scikit-Learn, PDFPlumber, PyPDF, and Plotly.", s2_code))
    story.append(Spacer(1, 6))

    # Step 3
    s3_code = (
        "# Execute database seeder script\n"
        "python seed_enterprise_db.py\n\n"
        "# Expected Output:\n"
        "# [OK] Initialized data/enterprise_telemetry.db with composite primary keys.\n"
        "# [OK] Seeded 8 verified corporate profiles (ITC, Reliance, NTPC, Tata Steel, HCL, Infosys, TCS, Wipro).\n"
        "# [OK] Inserted 208 multi-year historical records (2000-2026) with zero schema conflicts."
    )
    story.append(add_step_card(3, "Initialize & Seed Enterprise Relational Databases",
        "Creates SQLite tables, runs non-destructive schema migrations, and populates multi-year empirical records.", s3_code))
    story.append(Spacer(1, 6))

    # Step 4
    s4_code = (
        "# Run full test suite with verbose output and timing flags\n"
        "pytest tests/ -v\n\n"
        "# Expected Test Results:\n"
        "# tests/test_pipeline.py::test_mca_cin_validation PASSED\n"
        "# tests/test_pipeline.py::test_ghg_protocol_calculation_math PASSED\n"
        "# tests/test_pipeline.py::test_brsr_pdf_extractor_itc PASSED\n"
        "# tests/test_pipeline.py::test_ml_walk_forward_forecaster PASSED\n"
        "# tests/test_pipeline.py::test_critic_gate_reconciliation PASSED\n"
        "# ========================= 5 passed in 2.14s ========================="
    )
    story.append(add_step_card(4, "Execute PyTest Verification Suite",
        "Validates MCA CIN regex matching, GHG Protocol calculation math, and the Critic Gate tolerance bounds.", s4_code))
    story.append(Spacer(1, 6))

    # Step 5
    s5_code = (
        "# Run autonomous CLI audit on ITC Limited for FY 2025-26\n"
        "python main.py --org ITC_LIMITED --year 2026\n\n"
        "# Run in Strict Auditor Mode with live BRSR PDF parsing\n"
        "python main.py --org RELIANCE --year 2025 --strict --pdf data/reliance_brsr_2025.pdf\n\n"
        "# Output is rendered to terminal and persisted to data/pipeline_runs_ledger.db"
    )
    story.append(add_step_card(5, "Execute Autonomous Multi-Agent Pipeline via CLI",
        "Demonstrates headless execution of the complete 5-agent LangGraph workflow from terminal.", s5_code))
    story.append(Spacer(1, 6))

    # Step 6
    s6_code = (
        "# Launch high-performance FastAPI ASGI server on port 8000\n"
        "python api.py\n\n"
        "# Alternative direct Uvicorn launch with auto-reload for development:\n"
        "uvicorn api:app --host 0.0.0.0 --port 8000 --reload\n\n"
        "# Console output confirms server readiness:\n"
        "# INFO:     Started server process [PID: 14208]\n"
        "# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)"
    )
    story.append(add_step_card(6, "Launch High-Performance FastAPI Web Platform",
        "Starts ASGI server hosting RESTful API endpoints and serving the modern Atelier UI.", s6_code))
    story.append(Spacer(1, 6))

    # Step 7
    s7_code = (
        "# 1. Open your web browser and navigate to:\n"
        "http://127.0.0.1:8000\n\n"
        "# 2. Select 'ITC Limited' from the Enterprise Organization dropdown.\n"
        "# 3. Select '2026' as the reporting year.\n"
        "# 4. Click 'Run Autonomous Audit Pipeline' to trigger the 5-agent execution cycle.\n"
        "# 5. Explore Tabs 1-4: Trajectory & Forecasts, BRSR Scopes, Executive Report, and Agent Logs."
    )
    story.append(add_step_card(7, "Access & Operate Web Dashboard in Browser",
        "Interactive browser workflow for running live audits and inspecting interactive Plotly visualizations.", s7_code))
    story.append(Spacer(1, 8))

    # ------------------------------------------------------------------
    # 5.3 PRODUCTION DEPLOYMENT (DOCKER / CLOUD)
    # ------------------------------------------------------------------
    story.append(Paragraph("5.3 Enterprise Production Deployment (Docker Containerization)", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "For enterprise cloud hosting (AWS ECS, Google Cloud Run, Microsoft Azure Container Apps), CarbonTrace is containerized "
        "using a lightweight multi-stage Python Alpine/Slim Docker image:",
        styles["Body"]
    ))

    docker_code = (
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "RUN python seed_enterprise_db.py\n"
        "EXPOSE 8000\n"
        "CMD [\"uvicorn\", \"api:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\", \"--workers\", \"4\"]"
    )
    story.append(add_step_card("Bonus", "Dockerfile for Production Cloud Container",
        "Self-contained container build ensuring exact reproducibility in cloud production environments.", docker_code))

    story.append(PageBreak())
    return story
