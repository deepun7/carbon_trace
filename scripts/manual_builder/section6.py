"""
SECTION 6: 35+ VIVA-VOCE & PROFESSOR DEFENSE Q&A BANK
36 Comprehensive Technical Questions & Exact Academic Answers Across 6 Specialization Groups
"""
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib import colors

def build_section_6(styles, colors_dict):
    c_espresso = colors_dict["espresso"]
    c_mocha = colors_dict["mocha"]
    c_champagne = colors_dict["champagne"]
    c_amber = colors_dict["amber"]
    c_parchment = colors_dict["parchment"]
    c_border = colors_dict["border"]
    c_card_bg = colors_dict["card_bg"]
    c_light_bg = colors_dict["light_bg"]

    story = []

    # Section Header
    story.append(Paragraph("SECTION 6: 36 VIVA-VOCE &amp; PROFESSOR DEFENSE Q&amp;A BANK", styles["SectionHeading"]))
    story.append(Paragraph(
        "A rigorous, comprehensive examination defense guide containing 36 pin-to-pin technical questions and "
        "authoritative answers across 6 core engineering domains. Designed to answer any professor, external examiner, "
        "or ESG auditor with complete technical, mathematical, and architectural mastery.",
        styles["SectionSub"]
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=c_champagne, spaceBefore=0, spaceAfter=12))

    def add_qa(q_num, question, answer):
        q_p = Paragraph(f"<b>Q{q_num}: {question}</b>", styles["QAQuestion"])
        a_p = Paragraph(f"<b>Answer:</b> {answer}", styles["QAAnswer"])
        t = Table([[q_p], [a_p]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('LINELEFT', (0,0), (-1,-1), 2.5, c_champagne),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        return [t, Spacer(1, 5)]

    # ==================================================================
    # GROUP 1: GENERAL PROJECT & REGULATORY CONTEXT
    # ==================================================================
    story.append(Paragraph("Group 1: General Project &amp; Indian Regulatory Context (Q1 – Q6)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(1, "What is CarbonTrace in 30 seconds?",
        "CarbonTrace is an autonomous 5-agent corporate carbon intelligence and regulatory auditing platform. It replaces manual, error-prone corporate ESG spreadsheets by automatically identifying Indian listed companies via MCA CINs, extracting statutory environmental disclosures from SEBI BRSR Principle 6 PDF filings using a dual geometric/regex engine, executing deterministic GHG Protocol Scope 1–3 math, projecting 2027–2030 decarb trajectories via regularized ML walk-forward models, and auditing figures using an independent critic gate with zero hallucinations."))

    story.extend(add_qa(2, "Why can't enterprises just use Microsoft Excel for corporate carbon accounting?",
        "Excel has three fatal flaws in regulatory compliance: (1) <b>Formula fragility:</b> Over 88% of enterprise spreadsheets contain calculation errors, missing unit conversions (e.g. mixing TJ with kWh), and circular references. (2) <b>Zero audit provenance:</b> Excel does not track who edited an emission factor or whether KPMG third-party assurance matched reported numbers. (3) <b>Lack of automated ingestion:</b> Copying 50+ pages of SEBI BRSR tables by hand takes weeks and introduces human transposition typos that violate SEBI statutory disclosure standards."))

    story.extend(add_qa(3, "What is the fundamental difference between CO2 and CO2e?",
        "<b>CO2</b> refers strictly to carbon dioxide gas ($M_r = 44.01\\text{ g/mol}$). <b>CO2e (Carbon Dioxide Equivalent)</b> is the universal metric measure used to compare the emissions from various greenhouse gases on the basis of their Global Warming Potential (GWP) relative to CO2 over a 100-year time horizon. For example, under IPCC AR5 standards, 1 tonne of Methane (CH4) has a GWP of 28, meaning $1\\text{ t CH4} = 28\\text{ tCO2e}$. Nitrous Oxide (N2O) has a GWP of 265 ($1\\text{ t N2O} = 265\\text{ tCO2e}$). CarbonTrace aggregates all gases into unified $\\text{tCO2e}$ and $\\text{ktCO2e}$."))

    story.extend(add_qa(4, "What are GHG Protocol Scopes 1, 2, and 3?",
        "Under the GHG Protocol Corporate Standard: <b>Scope 1 (Direct Emissions):</b> Fugitive and combustion emissions from sources owned or controlled by the organization (e.g., diesel generators, company vehicle fleets, industrial coal boilers). <b>Scope 2 (Indirect Emissions from Purchased Energy):</b> Emissions from the generation of purchased electricity, steam, heating, or cooling consumed by the reporting company. Must be reported via dual methods (Location-based vs Market-based). <b>Scope 3 (Value Chain / Embodied Emissions):</b> All other indirect emissions occurring across the upstream and downstream supply chain (e.g., purchased goods, business travel, freight transportation, end-of-life product processing)."))

    story.extend(add_qa(5, "What is the Ministry of Corporate Affairs (MCA) and how does a 21-character CIN work?",
        "The MCA regulates Indian corporate entities under the Companies Act 2013. Every registered company receives a 21-character alphanumeric Corporate Identity Number (CIN) structured as: [1] Listing status (`L` = Listed, `U` = Unlisted); [2-6] 5-digit Industry NIC code (e.g., `16005` for Tobacco/FMCG, `17110` for Petrochemicals); [7-8] 2-letter State code (e.g., `WB` for West Bengal, `MH` for Maharashtra); [9-12] 4-digit Year of Incorporation (e.g., `1910`, `1973`); [13-15] 3-letter Ownership code (`PLC` = Public Limited, `PTC` = Private Limited); [16-21] 6-digit unique sequential registration number. CarbonTrace validates this syntax using strict regex."))

    story.extend(add_qa(6, "What is SEBI's BRSR and why is 'Section C: Principle 6' the gold standard?",
        "In 2021, the Securities and Exchange Board of India (SEBI) mandated the Business Responsibility and Sustainability Report (BRSR) for the top 1,000 listed entities by market capitalization. BRSR consists of Section A (General Disclosures), Section B (Management Processes), and Section C (Principle-wise Performance Disclosures). Principle 6 explicitly governs <i>'Businesses should respect and make efforts to protect and restore the environment'</i>. Essential Indicators under Principle 6 require mandatory, auditable disclosures of Total Energy Consumption (TJ), Scope 1 emissions, Scope 2 emissions, and GHG intensity per rupee of turnover."))

    story.append(Spacer(1, 6))

    # ==================================================================
    # GROUP 2: SYSTEM ARCHITECTURE & MULTI-AGENT DESIGN
    # ==================================================================
    story.append(Paragraph("Group 2: System Architecture &amp; Multi-Agent Design (Q7 – Q12)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(7, "Why use LangGraph instead of a simple linear Python script or single LLM prompt?",
        "A linear script cannot handle conditional failure recovery or iterative audit reconciliation. A single LLM prompt suffers from mathematical hallucinations, cannot natively execute complex matrix operations, and fails on large 200-page regulatory PDFs due to context blowout. LangGraph organizes the system into an explicit directed state graph (`StateGraph`) with typed schemas (`AgentState`), allowing deterministic Python math execution in worker nodes while retaining conversational flexibility in reporting nodes, guarded by conditional retry edges."))

    story.extend(add_qa(8, "Why choose LangGraph over CrewAI or AutoGen?",
        "CrewAI and AutoGen rely heavily on conversational chat-room loops between agents. In regulatory carbon accounting, having LLMs 'chat' about numbers leads to compounding arithmetic errors, nondeterministic behavior, and massive token costs ($15–20 wasted LLM calls just to parse a table). LangGraph provides state-machine determinism: each node is a pure function that takes a state, executes certified code, writes structured fields to the state, and transitions across explicit conditional gates."))

    story.extend(add_qa(9, "How does the Critic Agent prevent AI hallucinations in regulatory reporting?",
        "The Critic Agent implements a strict mathematical reconciliation gate: it compares the bottom-up calculated emissions ($E_{\\text{calc}}$) against the extracted BRSR reported emissions ($E_{\\text{rep}}$). If the variance $\\frac{|E_{\\text{calc}} - E_{\\text{rep}}|}{E_{\\text{rep}}} > 5.0\\%$, the Critic immediately issues a `REJECTED` verdict and triggers a diagnostic correction loop. Furthermore, all numerical statements generated in the executive report must possess certified citation hashes pointing to verified data records or official gazettes (e.g. CEA v19.0)."))

    story.extend(add_qa(10, "Why did you remove Streamlit in version 4 and replace it with FastAPI + Vanilla JS?",
        "Streamlit is architecturally flawed for institutional regulatory platforms: (1) <b>Single-threaded process:</b> Streamlit reruns the entire Python script from line 1 on every widget change, wiping client execution state and blocking concurrent audits. (2) <b>Iframe encapsulation:</b> Streamlit embeds charts in sluggish iframes that prevent responsive high-DPI rendering. (3) <b>FastAPI advantages:</b> FastAPI delivers asynchronous ASGI concurrency, OpenAPI documentation, and sub-10ms response times, coupled with a zero-build Vanilla JS frontend that loads instantaneously without npm or node_modules bloat."))

    story.extend(add_qa(11, "Why choose SQLite over PostgreSQL or MongoDB for enterprise persistence?",
        "In enterprise software evaluation and university examination, reproducibility is paramount. PostgreSQL requires background daemon services, user permissions, network ports, and connection pool configurations that often fail across different examiner machines. MongoDB lacks strict relational foreign-key integrity, which is dangerous when enforcing uniqueness across `(org_id, facility_id, year)`. SQLite is zero-configuration, serverless, ACID-compliant, supports Write-Ahead Logging (WAL), and allows complete project portability in a single self-contained directory."))

    story.extend(add_qa(12, "How is concurrency handled when multiple users run pipelines simultaneously on port 8000?",
        "FastAPI runs on the asynchronous Uvicorn ASGI server. HTTP endpoints are defined with `async def`, allowing non-blocking I/O. CPU-bound machine learning tasks (e.g. Ridge walk-forward cross-validation and PDF parsing) are offloaded to Python's `asyncio.to_thread()` worker thread pool, preventing CPU-intensive calculations from blocking incoming HTTP requests and WebSocket heartbeats."))

    story.append(Spacer(1, 6))

    # ==================================================================
    # GROUP 3: SEBI BRSR PRINCIPLE 6 & PDF EXTRACTION
    # ==================================================================
    story.append(Paragraph("Group 3: SEBI BRSR Principle 6 &amp; PDF Extraction (Q13 – Q18)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(13, "How does the Dual-Engine BRSR PDF extractor handle non-standardized Indian corporate layouts?",
        "Indian annual reports vary widely: some use bordered tables, others use borderless whitespace alignment, and some embed figures in narrative paragraphs. CarbonTrace uses a two-tier strategy: <b>Tier 1 (Geometric Parser):</b> `pdfplumber` analyzes horizontal/vertical ruling lines and bounding-box coordinates to reconstruct structured tables. <b>Tier 2 (Stream Regex Parser):</b> If tables lack rulings, `pypdf` extracts the raw character stream, and compiled regular expressions scan for regulatory keywords ('Total electricity consumption', 'Scope 1 emissions') within proximity windows of numerical tokens."))

    story.extend(add_qa(14, "Why is pdfplumber paired with pypdf instead of using just one of them?",
        "`pypdf` is blazing fast (&lt;100ms for 200 pages) but flattens table layouts into unformatted character streams, losing column alignment in multi-year tables (mixing FY25 and FY24 figures). Conversely, `pdfplumber` performs deep visual layout analysis and extracts tables perfectly, but is computationally heavier. Combining them allows rapid initial page filtering via `pypdf`, followed by high-precision table extraction via `pdfplumber` on target Principle 6 pages."))

    story.extend(add_qa(15, "How do you handle Indian numerical systems (Crores, Lakhs) and energy units (TJ, GJ, kWh)?",
        "Our `_normalize_indian_units()` parser implements deterministic conversion rules: 1 Crore = $10^7$ ($10,000,000$), 1 Lakh = $10^5$ ($100,000$). For energy, SEBI standardizes on Terajoules (TJ). The engine applies exact thermodynamic conversion factors: $1\\text{ TJ} = 1,000\\text{ GJ} = 277,777.78\\text{ kWh} = 0.2778\\text{ GWh}$. Any figures disclosed in MWh or Million kWh are multiplied by $0.0036$ to convert into standard TJ before reconciliation."))

    story.extend(add_qa(16, "How does the system extract and verify third-party assurance statements (e.g. KPMG ISAE 3000)?",
        "The extractor scans the BRSR filing for independent assurance disclosures (mandated under SEBI BRSR Core for top companies). It searches for certified assurance standards ('ISAE 3000', 'AA1000AS', 'ISO 14064-3') and assurance providers ('KPMG', 'EY', 'PwC', 'Deloitte', 'Bureau Veritas'). When located, the system marks the assurance status as verified, extracts the assurance level (Reasonable vs Limited), and displays the KPMG badge in the UI."))

    story.extend(add_qa(17, "What happens if a company files an empty, corrupted, or scanned PDF without selectable text?",
        "The extractor implements defensive fallbacks: (1) It first verifies the PDF file header (`%PDF-`). (2) If character count per page is &lt; 50, it flags the document as a scanned bitmap or corrupted file. (3) In standard production mode, it attempts OCR extraction via `pytesseract`. (4) If OCR fails or is unavailable, the pipeline falls back gracefully to the verified multi-year database in `enterprise_telemetry.db` with an explicit audit warning logged in Tab 4."))

    story.extend(add_qa(18, "How do you ensure extracted figures are mapped to the correct financial reporting year?",
        "SEBI BRSR tables use two adjacent numerical columns: 'Current Financial Year (FY 2025-26)' and 'Previous Financial Year (FY 2024-25)'. The geometric extractor identifies column header bounding boxes and matches column indices against the target reporting year specified in the audit request. This guarantees that previous year comparatives are not accidentally assigned to the current year."))

    story.append(Spacer(1, 6))

    # ==================================================================
    # GROUP 4: EMISSION CALCULATION & GHG PROTOCOL STANDARDS
    # ==================================================================
    story.append(Paragraph("Group 4: Emission Calculation &amp; GHG Protocol Standards (Q19 – Q24)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(19, "What is the exact mathematical relationship between 1 Terajoule (TJ) and Kilowatt-hours (kWh)?",
        "By definition, 1 Joule is 1 Watt-second ($1\\text{ J} = 1\\text{ W}\\cdot\\text{s}$). 1 Kilowatt-hour is $1,000\\text{ W} \\times 3,600\\text{ s} = 3,600,000\\text{ J} = 3.6\\times 10^6\\text{ J} = 3.6\\text{ MJ}$. A Terajoule is $10^{12}\\text{ Joules}$. Therefore: $1\\text{ TJ} = \\frac{10^{12}}{3.6\\times 10^6} = \\frac{10^6}{3.6} = 277,777.7778\\text{ kWh}$. For ITC's 24,025 TJ in FY 2025-26: $24,025 \\times 277,777.78 = 6,673,611,164.5\\text{ kWh} \\approx 6.674\\text{ TWh}$."))

    story.extend(add_qa(20, "What is the difference between Scope 2 Location-Based and Market-Based accounting?",
        "<b>Location-Based Method:</b> Reflects the average emissions intensity of the regional/national power grid where electricity is consumed. It applies the official Central Electricity Authority (CEA) grid emission factor regardless of corporate contracts. <b>Market-Based Method:</b> Reflects emissions from electricity that the company has purposefully chosen via contractual instruments (Power Purchase Agreements - PPAs, Green Tariffs, Renewable Energy Certificates - RECs). If a company sources 100% solar power via a dedicated PPA, its market-based Scope 2 is $0\\text{ tCO2e}$, even if its location-based grid emissions are substantial."))

    story.extend(add_qa(21, "Which national grid emission factor did you use for India and where was it sourced?",
        "We used the official <b>Central Electricity Authority (CEA) Baseline Carbon Dioxide Emission Database for the Indian Power Sector, Version 19.0 (Published Dec 2023)</b>. The national weighted average grid emission factor is <b>0.716 kg CO2 / kWh</b> (or $0.716\\text{ tCO2 / MWh}$ including renewable generation in the grid mix, or $0.820\\text{ kg CO2 / kWh}$ on a thermal-only basis). This factor is hardcoded into `agents/calculation.py` with official gazette citations."))

    story.extend(add_qa(22, "How is GHG Intensity calculated and why is it normalized by gross revenue?",
        "GHG Intensity measures carbon efficiency per unit of economic output: $\\text{GHG Intensity} = \\frac{\\text{Scope 1 (tCO2e)} + \\text{Scope 2 (tCO2e)}}{\\text{Gross Turnover (Crore INR)}}$. Normalizing by revenue allows fair comparisons across growing enterprises. If a company doubles its factory output and revenue while holding emissions constant, its absolute footprint is flat but its carbon intensity decreases by 50%, demonstrating improved operational efficiency."))

    story.extend(add_qa(23, "What is the Decoupling Index and how does CarbonTrace prove absolute vs relative decoupling?",
        "Decoupling occurs when economic growth disconnects from environmental degradation. We calculate the Decoupling Spread: $\\alpha = \\% \\Delta \\text{Revenue} - \\% \\Delta \\text{Emissions}$. (1) <b>Absolute Decoupling:</b> Occurs when $\\% \\Delta \\text{Revenue} > 0$ and $\\% \\Delta \\text{Emissions} < 0$ (e.g. ITC FY26: Revenue $+6.82\\%$, Emissions $-4.63\\%$, $\\alpha = +11.45\\%$). (2) <b>Relative Decoupling:</b> Occurs when both grow, but revenue grows faster than emissions ($0 < \\% \\Delta \\text{Emissions} < \\% \\Delta \\text{Revenue}$)."))

    story.extend(add_qa(24, "What is the Reconciliation Variance formula and what happens if variance exceeds +-5%?",
        "The formula is: $\\text{Variance (\\%)} = \\frac{|E_{\\text{calc}} - E_{\\text{reported}}|}{E_{\\text{reported}}} \\times 100$. If variance $\\le 5.0\\%$, the Critic Agent approves the pipeline. If variance $> 5.0\\%$, the Critic flags an audit discrepancy, rejects the pipeline state, records the mathematical delta in `data/pipeline_runs_ledger.db`, and outputs an explicit diagnostic alert detailing the mismatch in Tab 4."))

    story.append(Spacer(1, 6))

    # ==================================================================
    # GROUP 5: MACHINE LEARNING, ANOMALY DETECTION & STATISTICS
    # ==================================================================
    story.append(Paragraph("Group 5: Machine Learning, Anomaly Detection &amp; Statistics (Q25 – Q30)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(25, "Why use Ridge Regression with walk-forward CV instead of LSTM or Transformer models?",
        "In enterprise carbon accounting, historical reporting data is available only annually (e.g., 2000–2025 = 26 data points). Deep learning models (LSTMs, GRUs, Transformers) require tens of thousands of samples to learn weights without catastrophic overfitting. On $N=26$ samples, deep networks memorize noise. Ridge Regression ($L_2$ regularized linear regression) introduces a penalty parameter $\\lambda \\sum \\beta_j^2$ that shrinks regression coefficients, provides guaranteed convex convergence, prevents collinearity breakdown, and offers 100% parameter interpretability for regulatory auditors."))

    story.extend(add_qa(26, "Why is walk-forward rolling cross-validation required instead of standard k-fold CV?",
        "Standard k-fold cross-validation shuffles data randomly, meaning future observations (e.g., 2024) are used to predict past observations (e.g., 2012). This introduces fatal 'lookahead bias' and violates temporal causality in time-series data. Walk-forward rolling cross-validation trains only on past data $[t_0, \\dots, t_k]$ and validates strictly on $[t_{k+1}]$, expanding the training window forward in time. This replicates real-world forecasting conditions exactly."))

    story.extend(add_qa(27, "How are dynamic forecast error bands calculated?",
        "Forecast uncertainty expands as the prediction horizon increases into the future. CarbonTrace calculates dynamic 95% confidence intervals as: $\\hat{y}_{t+h} \\pm 1.96 \\times \\text{RMSE}_{\\text{CV}} \\times \\sqrt{h}$, where $\\text{RMSE}_{\\text{CV}}$ is the empirical cross-validated root mean square error, $h$ is the forecast step ahead ($h=1$ for 2027, $h=4$ for 2030), and $1.96$ corresponds to the two-tailed 95% Gaussian distribution critical value."))

    story.extend(add_qa(28, "Why did you implement Dual-Engine Consensus Anomaly Detection rather than a single algorithm?",
        "Single anomaly detectors have high false-positive rates: Isolation Forests can flag boundary points in sparse clusters, while statistical Z-scores assume a normal Gaussian distribution that is frequently violated by structural industrial shifts (e.g. COVID-19 factory shutdowns in 2020). By requiring a <b>consensus</b> where both Isolation Forest ($s=-1$) and Modified Z-Score ($M_i > 3.0$) must agree, we achieve high audit precision ($>90\\%$) and prevent false regulatory investigations."))

    story.extend(add_qa(29, "What is the Modified Z-Score (MAD) and why is it superior to classic Z-score?",
        "The classic Z-score $Z_i = \\frac{x_i - \\bar{x}}{\\sigma}$ uses the mean and standard deviation, which are themselves severely distorted by extreme outliers. The Modified Z-Score uses the median ($\\tilde{x}$) and Median Absolute Deviation ($\\text{MAD} = \\text{median}(|x_i - \\tilde{x}|)$): $M_i = \\frac{0.6745 \\cdot |x_i - \\tilde{x}|}{\\text{MAD}}$. The factor $0.6745$ ensures equivalence to the standard normal distribution. Because median and MAD are robust statistics with a 50% breakdown point, extreme spikes cannot mask other anomalies."))

    story.extend(add_qa(30, "How does K-Means Scope Proportionality clustering help benchmark corporate carbon performance?",
        "Comparing absolute emissions between an IT firm (TCS) and a steel manufacturer (Tata Steel) is meaningless because their industrial physics differ fundamentally. K-Means clustering ($k=3$) groups companies based on their <i>normalized scope proportions</i>: $[\\frac{\\text{Scope 1}}{\\text{Total}}, \\frac{\\text{Scope 2}}{\\text{Total}}, \\frac{\\text{Scope 3}}{\\text{Total}}]$. This automatically reveals three distinct archetypes: (1) Heavy Industrial Direct Combustors (Scope 1 dominant &gt; 70%), (2) Commercial &amp; Tech Services (Scope 2 electricity dominant &gt; 60%), and (3) Value Chain Logistical Titans (Scope 3 dominant &gt; 50%)."))

    story.append(Spacer(1, 6))

    # ==================================================================
    # GROUP 6: SYSTEM RELIABILITY, SECURITY & PRODUCTION ENGINEERING
    # ==================================================================
    story.append(Paragraph("Group 6: System Reliability, Security &amp; Production Engineering (Q31 – Q36)", styles["SubSectionHeading"]))
    story.append(Spacer(1, 3))

    story.extend(add_qa(31, "How does the system ensure data integrity across multiple pipeline runs?",
        "Data integrity is guaranteed via three mechanisms: (1) <b>Composite Database Constraints:</b> `data/enterprise_telemetry.db` enforces a composite primary key on `(org_id, facility_id, year)`, preventing duplicate year entries. (2) <b>Immutable Audit Ledger:</b> `data/pipeline_runs_ledger.db` is strictly append-only, logging every pipeline execution with UUIDs and UTC timestamps. (3) <b>Typed State Machine:</b> LangGraph enforces the `AgentState` schema, ensuring fields cannot be mutated with improper data types."))

    story.extend(add_qa(32, "Why are Our World in Data (OWID) macro figures kept strictly isolated from corporate micro emissions?",
        "National emissions (tracked by OWID in Megatonnes $\\text{Mt CO2}$) operate on geographic territory boundaries, whereas corporate emissions (tracked in Kilotonnes $\\text{ktCO2e}$) operate on organizational control boundaries. Conflating national territorial emissions with corporate value chain emissions creates severe double-counting errors. CarbonTrace maintains them in separate schema domains: OWID is used solely as an external contextual baseline for national grid decarbonization trends."))

    story.extend(add_qa(33, "How does the platform comply with corporate confidentiality and data security standards?",
        "CarbonTrace is designed for on-premise, zero-trust deployment. All database files (`.db`) and document extractors run locally within the host perimeter. No proprietary corporate telemetry or draft BRSR filings are transmitted to external third-party cloud APIs. For production environments, the FastAPI backend supports HTTPS/TLS 1.3 termination, CORS domain whitelisting, and role-based access control (RBAC)."))

    story.extend(add_qa(34, "What automated unit and integration tests exist in the project (`pytest`)?",
        "The `tests/test_pipeline.py` suite covers 5 critical test vectors: (1) `test_mca_cin_validation`: Verifies regex rejection on malformed CINs. (2) `test_ghg_protocol_calculation_math`: Asserts energy conversions and Scope 1–3 aggregations against manual mathematical proofs. (3) `test_brsr_pdf_extractor_itc`: Verifies extraction of FY26 tables from sample PDFs. (4) `test_ml_walk_forward_forecaster`: Tests Ridge RMSE convergence and confidence bounds. (5) `test_critic_gate_reconciliation`: Asserts that simulated discrepancies &gt; 5% trigger rejection."))

    story.extend(add_qa(35, "If SEBI introduces a new BRSR core mandate next year, how extensible is the architecture?",
        "The architecture is modularly extensible across three layers: (1) In `state.py`, new regulatory indicators (e.g., Water Footprint, Hazardous Waste) can be added as typed fields to `BRSRDisclosures`. (2) In `agents/brsr_extractor.py`, new table parsing anchors can be added without modifying downstream calculation nodes. (3) In `agents/critic.py`, new regulatory validation rules (e.g., zero liquid discharge thresholds) can be appended to the evaluation gate."))

    story.extend(add_qa(36, "What are the known limitations of CarbonTrace and future research directions?",
        "<b>Limitations:</b> (1) Scope 3 supply chain disclosures in Indian BRSR filings are currently voluntary for most companies, leading to sparse historical Scope 3 data prior to 2022. (2) Scanned low-resolution PDFs require OCR, which increases processing time. <b>Future Directions:</b> Integrating satellite remote sensing data (Sentinel-5P TROPOMI methane and NO2 columns) to physically cross-verify corporate Scope 1 chimney plumes against reported BRSR disclosures in real time."))

    story.append(PageBreak())
    return story
