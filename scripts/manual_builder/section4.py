"""
SECTION 4: LIVE WEBSITE SCREENSHOTS & NUMBERED UI COMPONENT GUIDE
Visual Architecture, Interactive Wireframes & Detailed Component Encyclopedia [1] to [25]
"""
import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, HRFlowable
from reportlab.lib import colors

def build_section_4(styles, colors_dict, screenshots_dir):
    c_espresso = colors_dict["espresso"]
    c_mocha = colors_dict["mocha"]
    c_champagne = colors_dict["champagne"]
    c_amber = colors_dict["amber"]
    c_border = colors_dict["border"]
    c_card_bg = colors_dict["card_bg"]
    c_light_bg = colors_dict["light_bg"]

    story = []

    # Section Header
    story.append(Paragraph("SECTION 4: VISUAL UI GUIDE &amp; NUMBERED COMPONENT ENCYCLOPEDIA", styles["SectionHeading"]))
    story.append(Paragraph(
        "A pin-to-pin visual breakdown of the live CarbonTrace platform. Features 9 high-resolution production screenshots "
        "paired with an exhaustive component guide covering elements [1] through [25].",
        styles["SectionSub"]
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=c_champagne, spaceBefore=0, spaceAfter=12))

    story.append(Paragraph(
        "The CarbonTrace user interface is designed in a luxury editorial atelier style, combining a high-contrast espresso "
        "and champagne palette with responsive, zero-build ECMAScript 2024 controls and Plotly.js data visualizations. "
        "The platform eliminates all generic student demo widgets in favor of an institutional-grade regulatory portal.",
        styles["Body"]
    ))
    story.append(Spacer(1, 6))

    # Helper function to embed screenshot safely
    def embed_img(filename, width=520, height=140, caption=""):
        img_path = os.path.join(screenshots_dir, filename)
        elements = []
        if os.path.exists(img_path):
            img = Image(img_path, width=width, height=height)
            elements.append(img)
            if caption:
                elements.append(Paragraph(caption, styles["ImageCaption"]))
        else:
            elements.append(Paragraph(f"[Asset Missing: {filename}]", styles["CalloutTitle"]))
        return elements

    # ------------------------------------------------------------------
    # 4.1 FULL DASHBOARD OVERVIEW & TOP NAVIGATION
    # ------------------------------------------------------------------
    story.append(Paragraph("4.1 Master Dashboard Overview &amp; Pipeline Stepper", styles["SubSectionHeading"]))
    story.extend(embed_img("00_full_dashboard_overview.png", width=520, height=210, caption="Figure 4.1: Master Overview of CarbonTrace Live Platform on Port 8000"))
    story.append(Spacer(1, 4))
    story.extend(embed_img("01_top_header_and_stepper.png", width=520, height=95, caption="Figure 4.2: Top Header Navigation, Live System Heartbeat &amp; 5-Step Agent Execution Stepper"))
    story.append(Spacer(1, 6))

    comp_table_1_data = [
        [
            Paragraph("<b>Ref # &amp; Component Name</b>", styles["TableHead"]),
            Paragraph("<b>What Is Shown</b>", styles["TableHead"]),
            Paragraph("<b>Why It Exists</b>", styles["TableHead"]),
            Paragraph("<b>How It Operates Behind the Scenes</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>[1] Top Header &amp; Health Beacon</b>", styles["TableCellBold"]),
            Paragraph("Brand insignia, MCA/SEBI regulatory subtitle, and green glowing heartbeat badge (`FastAPI 8000 Active`).", styles["TableCell"]),
            Paragraph("Provides immediate orientation and verifies that the ASGI backend server is reachable and responsive.", styles["TableCell"]),
            Paragraph("Asynchronously pings `/api/status` every 30 seconds. If unreachable, changes beacon color to amber and alerts the auditor.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[2] 5-Step Agent Execution Stepper</b>", styles["TableCellBold"]),
            Paragraph("5 sequential pipeline stages: (1) Ingestion &amp; CIN, (2) BRSR Extractor, (3) Calculation, (4) ML Engine, (5) Reporting.", styles["TableCell"]),
            Paragraph("Transforms a complex asynchronous multi-agent graph into an intuitive visual workflow for examiners.", styles["TableCell"]),
            Paragraph("Listens to server state updates. As each LangGraph node finishes, its icon transitions from idle to pulsing gold to verified checkmark.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[3] Enterprise Org Selector</b>", styles["TableCellBold"]),
            Paragraph("Dropdown listing 8 verified Indian conglomerates (ITC, Reliance, NTPC, Tata Steel, HCL, Infosys, TCS, Wipro).", styles["TableCell"]),
            Paragraph("Allows instant multi-tenant switching across distinct corporate structures and industrial sectors.", styles["TableCell"]),
            Paragraph("Fetches `/api/companies` to populate options; selecting an enterprise dynamically refreshes CIN and registry telemetry.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[4] Audit Reporting Year Selector</b>", styles["TableCellBold"]),
            Paragraph("Selectable year range (2000–2026) focusing the regulatory audit on specific reporting periods.", styles["TableCell"]),
            Paragraph("Enables historical retrospective compliance audits as well as latest FY 2025-26 regulatory reconciliations.", styles["TableCell"]),
            Paragraph("Sets `reporting_year` in the API payload, pulling corresponding operational records from `data/enterprise_telemetry.db`.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[5] SEBI BRSR PDF Dropzone</b>", styles["TableCellBold"]),
            Paragraph("Interactive drag-and-drop file upload zone accepting official corporate BRSR PDF filings.", styles["TableCell"]),
            Paragraph("Allows auditing unseeded external reports and verifying live extraction from genuine PDF documents.", styles["TableCell"]),
            Paragraph("Submits multipart `POST /api/upload-brsr`. Triggers `agents/brsr_extractor.py` and returns structured extracted indicators.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[6] Audit Mode Strictness Toggle</b>", styles["TableCellBold"]),
            Paragraph("Toggle switch between Standard Mode and Strict Regulatory Audit Mode ($\\pm 5.0\\%$ variance gate).", styles["TableCell"]),
            Paragraph("Demonstrates the independent Critic Agent's rejection mechanism when disclosures contain anomalies.", styles["TableCell"]),
            Paragraph("Toggles `strict_mode: true` in state. If calculated variance exceeds $\\pm 5\\%$, critic routes to `REJECTED` and halts approval.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[7] Run Autonomous Pipeline CTA</b>", styles["TableCellBold"]),
            Paragraph("High-contrast champagne button: 'Run Autonomous Audit Pipeline'.", styles["TableCell"]),
            Paragraph("The primary user action that triggers the complete 5-agent LangGraph execution cycle.", styles["TableCell"]),
            Paragraph("Calls `POST /api/run-pipeline`. Disables inputs, animates stepper, and streams real-time execution results to the client.", styles["TableCell"]),
        ],
    ]

    comp_table_1 = Table(comp_table_1_data, colWidths=[105, 135, 140, 160])
    comp_table_1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(comp_table_1)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 4.2 KPI CARDS & ATELIER SIDEBAR CONTROLS
    # ------------------------------------------------------------------
    story.append(Paragraph("4.2 Executive KPI Metric Cards &amp; Atelier Control Panel", styles["SubSectionHeading"]))
    story.extend(embed_img("03_kpi_cards.png", width=520, height=95, caption="Figure 4.3: Executive KPI Cards Displaying Total Footprint, Scope 1, Energy, ML Skill &amp; Compliance"))
    story.append(Spacer(1, 4))

    comp_table_2_data = [
        [
            Paragraph("<b>Ref # &amp; Component Name</b>", styles["TableHead"]),
            Paragraph("<b>What Is Shown</b>", styles["TableHead"]),
            Paragraph("<b>Why It Exists</b>", styles["TableHead"]),
            Paragraph("<b>How It Operates Behind the Scenes</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>[8] Total Extracted Footprint KPI</b>", styles["TableCellBold"]),
            Paragraph("Total corporate carbon emissions (e.g. `2,657 ktCO2e`) with YoY growth/decline percentage badge.", styles["TableCell"]),
            Paragraph("The primary North Star metric required by SEBI and investors for statutory environmental disclosure.", styles["TableCell"]),
            Paragraph("Calculated dynamically as $\\text{Scope 1} + \\text{Scope 2 (Location)} + \\text{Scope 3}$. Formatted with comma separators.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[9] Scope 1 Direct Combustion KPI</b>", styles["TableCellBold"]),
            Paragraph("Direct operational emissions (e.g. `1,045 ktCO2e`) resulting from fuel, boiler, and fleet combustion.", styles["TableCell"]),
            Paragraph("Measures emissions under the direct operational control of the enterprise.", styles["TableCell"]),
            Paragraph("Extracted from SEBI Principle 6 Table 2 and cross-verified against fuel consumption activity data.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[10] Total Energy Consumed KPI</b>", styles["TableCellBold"]),
            Paragraph("Total energy in Terajoules (e.g. `24,025 TJ`) with renewable percentage badge (`51.3% Renewable`).", styles["TableCell"]),
            Paragraph("Measures operational efficiency and clean energy transition progress under SEBI Principle 6 Essential Indicators.", styles["TableCell"]),
            Paragraph("Sums renewable (12,334 TJ) and non-renewable (11,691 TJ) energy. Evaluates renewable share formula.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[11] ML Walk-Forward Skill KPI</b>", styles["TableCellBold"]),
            Paragraph("Forecasting accuracy score (e.g. `Ridge R² = 0.94`, `MAPE = 3.2%`, `CV Folds = 5`).", styles["TableCell"]),
            Paragraph("Provides mathematical confidence that forward trajectory projections are statistically valid.", styles["TableCell"]),
            Paragraph("Extracted from `agents/ml_engine.py` walk-forward rolling split evaluation matrix.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[12] SEBI Compliance Status KPI</b>", styles["TableCellBold"]),
            Paragraph("Regulatory verification status badge (`100% Compliant — KPMG ISAE 3000 Verified`).", styles["TableCell"]),
            Paragraph("Confirms whether third-party statutory assurance has been conducted on the reported data.", styles["TableCell"]),
            Paragraph("Parsed from the Independent Assurance Statement section of the company's annual report.", styles["TableCell"]),
        ],
    ]

    comp_table_2 = Table(comp_table_2_data, colWidths=[110, 135, 135, 160])
    comp_table_2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(comp_table_2)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 4.3 TAB 1: TRAJECTORY & ML FORECASTING VIEW
    # ------------------------------------------------------------------
    story.append(Paragraph("4.3 Tab 1: Historical Trajectory &amp; ML Walk-Forward Forecasts", styles["SubSectionHeading"]))
    story.extend(embed_img("04_tab01_trajectory_ml_forecast.png", width=520, height=210, caption="Figure 4.4: Historical Emissions Trajectory (2000–2026), Ridge ML Projections (2027–2030) with 95% Error Bands &amp; Anomaly Overlay"))
    story.append(Spacer(1, 4))

    comp_table_3_data = [
        [
            Paragraph("<b>Ref # &amp; Component Name</b>", styles["TableHead"]),
            Paragraph("<b>What Is Shown</b>", styles["TableHead"]),
            Paragraph("<b>Why It Exists</b>", styles["TableHead"]),
            Paragraph("<b>How It Operates Behind the Scenes</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>[13] Tab 1 Navigation Tab</b>", styles["TableCellBold"]),
            Paragraph("Top tab button labelled 'Trajectory &amp; ML Forecast'.", styles["TableCell"]),
            Paragraph("Enables instant navigation to multi-year historical trends and forward predictive intelligence.", styles["TableCell"]),
            Paragraph("Client-side event handler displays Tab 1 pane while hiding Tabs 2–4 without page reloading.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[14] Historical Trajectory &amp; ML Forecast Chart</b>", styles["TableCellBold"]),
            Paragraph("Interactive Plotly.js chart displaying historical emissions curve (2000–2026) connected to 2027–2030 projections with shaded error bands.", styles["TableCell"]),
            Paragraph("Visualizes corporate decarbonization velocity against India's 2070 Net Zero commitments.", styles["TableCell"]),
            Paragraph("Combines historical telemetry points with Ridge model forecasts. Computes $\\pm 1.96 \\times \\text{RMSE} \\times \\sqrt{h}$ error boundaries.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[15] Consensus Anomaly Markers</b>", styles["TableCellBold"]),
            Paragraph("Prominent red circular markers overlaid on specific historical years (e.g. 2020 COVID dip).", styles["TableCell"]),
            Paragraph("Alerts auditors to abnormal emissions deviations that require statutory investigation.", styles["TableCell"]),
            Paragraph("Rendered as a scatter trace overlay where `consensus_anomaly == True` (Isolation Forest + Modified Z-Score consensus).", styles["TableCell"]),
        ],
    ]

    comp_table_3 = Table(comp_table_3_data, colWidths=[110, 135, 135, 160])
    comp_table_3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(comp_table_3)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 4.4 TAB 2: SEBI BRSR PRINCIPLE 6 SCOPES VIEW
    # ------------------------------------------------------------------
    story.append(Paragraph("4.4 Tab 2: SEBI BRSR Principle 6 Scopes &amp; Energy Composition", styles["SubSectionHeading"]))
    story.extend(embed_img("05_tab02_brsr_scopes_view.png", width=520, height=210, caption="Figure 4.5: SEBI BRSR Principle 6 View — Scopes 1/2/3 Breakdown, Renewable Energy Donut &amp; Reconciliation Table"))
    story.append(Spacer(1, 4))

    comp_table_4_data = [
        [
            Paragraph("<b>Ref # &amp; Component Name</b>", styles["TableHead"]),
            Paragraph("<b>What Is Shown</b>", styles["TableHead"]),
            Paragraph("<b>Why It Exists</b>", styles["TableHead"]),
            Paragraph("<b>How It Operates Behind the Scenes</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>[16] Tab 2 Navigation Tab</b>", styles["TableCellBold"]),
            Paragraph("Top tab button labelled 'SEBI BRSR Scopes'.", styles["TableCell"]),
            Paragraph("Provides dedicated access to official Principle 6 environmental indicator breakdowns.", styles["TableCell"]),
            Paragraph("DOM tab switcher triggers Plotly relayout to ensure full responsive width rendering.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[17] Scopes 1, 2, &amp; 3 Bar Chart</b>", styles["TableCellBold"]),
            Paragraph("Grouped bar chart comparing Scope 1, Scope 2 Location-Based, Scope 2 Market-Based, and Scope 3.", styles["TableCell"]),
            Paragraph("Fulfills mandatory GHG Protocol Scope 2 Dual-Reporting standard.", styles["TableCell"]),
            Paragraph("Renders 4 distinct bar traces in champagne, amber, mocha, and bronze tones.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[18] Renewable Energy Donut Chart</b>", styles["TableCellBold"]),
            Paragraph("Donut chart illustrating percentage breakdown: Renewable Energy vs Non-Renewable Fuel/Grid.", styles["TableCell"]),
            Paragraph("Audits compliance with SEBI's mandate for increased renewable energy adoption.", styles["TableCell"]),
            Paragraph("Calculates values from `telemetry.renewable_energy_tj` and `non_renewable_energy_tj`.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[19] Audit Reconciliation Table</b>", styles["TableCellBold"]),
            Paragraph("Detailed table listing Activity-Calculated emissions, Reported BRSR emissions, Variance %, and Critic Gate status.", styles["TableCell"]),
            Paragraph("Provides the core empirical proof that prevents corporate greenwashing or misreporting.", styles["TableCell"]),
            Paragraph("Compares calculated vs reported data. If $\\le 5.0\\%$, displays green 'PASSED'; else flags red 'DISCREPANCY'.", styles["TableCell"]),
        ],
    ]

    comp_table_4 = Table(comp_table_4_data, colWidths=[110, 135, 135, 160])
    comp_table_4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(comp_table_4)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 4.5 TAB 3 & 4: EXECUTIVE REPORT & AGENT AUDIT LOGS
    # ------------------------------------------------------------------
    story.append(Paragraph("4.5 Tab 3 &amp; 4: Executive Report Viewer &amp; Agent Audit Ledger", styles["SubSectionHeading"]))
    story.extend(embed_img("07_tab03_executive_report_viewer.png", width=520, height=180, caption="Figure 4.6: Tab 3 — Synthesized Executive ESG Memorandum, Decoupling Metrics &amp; Assurance Summary"))
    story.append(Spacer(1, 4))
    story.extend(embed_img("08_tab04_agent_logs_and_citations.png", width=520, height=180, caption="Figure 4.7: Tab 4 — Live Autonomous Agent Execution Logs &amp; Official Regulatory Citations Ledger"))
    story.append(Spacer(1, 4))

    comp_table_5_data = [
        [
            Paragraph("<b>Ref # &amp; Component Name</b>", styles["TableHead"]),
            Paragraph("<b>What Is Shown</b>", styles["TableHead"]),
            Paragraph("<b>Why It Exists</b>", styles["TableHead"]),
            Paragraph("<b>How It Operates Behind the Scenes</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>[20] Tab 3: Executive Report Tab</b>", styles["TableCellBold"]),
            Paragraph("Navigation tab for executive compliance memorandum.", styles["TableCell"]),
            Paragraph("Gives board-level executives and auditors a clean, ready-to-sign summary memo.", styles["TableCell"]),
            Paragraph("Switches viewing pane to Tab 3.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[21] Executive ESG Memorandum</b>", styles["TableCellBold"]),
            Paragraph("Full-text report synthesizing financial revenue, carbon trajectory, SEBI scoring, and audit findings.", styles["TableCell"]),
            Paragraph("Eliminates weeks of manual ESG report drafting by corporate sustainability teams.", styles["TableCell"]),
            Paragraph("Generated by `agents/reporting.py` using structured data templates with zero LLM hallucinations.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[22] Decoupling Alpha Metric Box</b>", styles["TableCellBold"]),
            Paragraph("Highlighted box displaying Decoupling Spread ($\\alpha = +11.45\\%$) and Elasticity ($\\beta$).", styles["TableCell"]),
            Paragraph("Mathematically proves whether corporate revenue expanded faster than emissions grew.", styles["TableCell"]),
            Paragraph("Evaluates $\\Delta \\text{Revenue} (\\%) - \\Delta \\text{Emissions} (\\%)$.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[23] Tab 4: Agent Logs &amp; Citations</b>", styles["TableCellBold"]),
            Paragraph("Navigation tab for system provenance and debugging.", styles["TableCell"]),
            Paragraph("Essential for external examiners to verify that real agent logic executed.", styles["TableCell"]),
            Paragraph("Switches viewing pane to Tab 4.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[24] Live Agent Execution Stream</b>", styles["TableCellBold"]),
            Paragraph("Timestamped monospace log terminal showing node activations, math calculations, and state writes.", styles["TableCell"]),
            Paragraph("Ensures 100% transparency; eliminates 'black box' skepticism during university viva.", styles["TableCell"]),
            Paragraph("Renders array of `execution_logs` captured in the `AgentState` ledger during pipeline runtime.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>[25] Regulatory Citations Table</b>", styles["TableCellBold"]),
            Paragraph("Authoritative citation list referencing CEA Grid Baseline v19.0, GHG Protocol, and SEBI Circulars.", styles["TableCell"]),
            Paragraph("Guarantees statutory audit compliance and legal defensibility.", styles["TableCell"]),
            Paragraph("Aggregates citation objects appended by each agent during data ingestion and emission factor application.", styles["TableCell"]),
        ],
    ]

    comp_table_5 = Table(comp_table_5_data, colWidths=[110, 135, 135, 160])
    comp_table_5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_espresso),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_card_bg, c_light_bg]),
    ]))
    story.append(comp_table_5)

    story.append(PageBreak())
    return story
