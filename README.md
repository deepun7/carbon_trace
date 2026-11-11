# CarbonTrace — A Multi-Agent Prototype for Automated Organizational Carbon Tracking, with Simulated Activity Data and OWID National Benchmarking

**B.Tech 4th-Year CSE (AI/ML) Capstone Prototype**

## Technical Manual

The [CarbonTrace Technical Manual & Blueprint](./CarbonTrace_Technical_Manual.pdf) is a source-independent guide to the project's purpose, accounting boundaries, five-agent architecture, emission calculations, machine-learning methods, evaluation metrics, tests, and viva questions. It also documents the dashboard interfaces and labels the provenance and runtime limitations of its screenshots.

## Overview
CarbonTrace is a 5-agent LangGraph prototype that automates organizational greenhouse gas (GHG) accounting across selected operational categories and benchmarks organizational emission trajectories against national macro data from the **Our World in Data (OWID) CO₂ Dataset**.

### Key Prototype Design & Honest Boundaries
- **MCA CIN & BRSR Corporate Registry vs Simulated Demo:** Following the official 4-step Indian corporate regulatory workflow, the system integrates verified Corporate Identity Numbers (CINs) and annual Business Responsibility and Sustainability Report (BRSR) Principle 6 filings for leading Indian enterprises:
  - **Reliance Industries Limited** (`CIN: L17110MH1973PLC019786` | `BSE: 500325` | `NSE: RELIANCE`)
  - **NTPC Limited** (`CIN: L40101DL1975GOI007966` | `BSE: 532555` | `NSE: NTPC`)
  - **Tata Steel Limited** (`CIN: L27100MH1907PLC000260` | `BSE: 500470` | `NSE: TATASTEEL`)
  Meanwhile, prototype baseline entities (`Apex Manufacturing Pvt Ltd` and `GreenGrid Logistics Corp`) remain explicitly labeled as `SIMULATED_DEMO`. Users can also supply external CSV activity files or upload annual BRSR PDF filings for automated Section E / Section C: Principle 6 extraction.
- **Included Activity Categories Only:** Calculations cover selected Scope 1 (stationary diesel, natural gas, diesel commercial fleet), Scope 2 (location-based grid electricity), and Scope 3 (short/medium-haul business flights, HGV road freight) categories rather than a complete corporate inventory.
- **Static 2024 Reference Factor Limitation:** Documented conversion factors (`data/emission_factors_registry.json` from UK DESNZ 2024, US EPA 2024, CEA India v19.0, IEA) are applied as static reference values across historical years for consistent prototype trend comparison.
- **Walk-Forward Validation vs Naive Persistence Baseline:** The ML Engine evaluates an Autoregressive Ridge model using expanding-window walk-forward validation against a **Naive Persistence Baseline ($\hat{y}_t = y_{t-1}$)** and explicitly warns when the regression RMSE exceeds the naive baseline on small or volatile samples. Anomaly F1 measures **unsupervised inter-method agreement** (Isolation Forest vs Z-Score), not ground-truth accuracy.
- **BRSR Principle 6 Scope 1 & 2 Reconciliation:** Computes exact variance between activity-based operational models and official regulatory disclosures from BRSR filings ($\text{Variance} = \text{Model} - \text{Reported}$).

## 5-Agent Architecture
1. **Ingestion Agent (`agents/ingestion.py`):** Queries SQLite or validates an external CSV filtered strictly by `org_id`, aggregates multi-facility records by `(org_id, year)`, and loads OWID national benchmark data with a **24-hour cache TTL**.
2. **Calculation Agent (`agents/calculation.py`):** Applies documented conversion factors to compute Scope 1, 2, and 3 emissions in `tCO₂e` while keeping OWID national macro totals (`Mt CO₂`) strictly separate.
3. **ML Engine Agent (`agents/ml_engine.py`):** Runs expanding-window walk-forward cross-validation against a naive persistence baseline, computes dynamic forecast horizons (`last_year + 1` onward) with approximate heuristic error bands (`±1.96 × RMSE × √step`), and evaluates inter-method anomaly agreement plus optional exploratory K-Means grouping.
4. **Reporting Agent (`agents/reporting.py`):** Compiles a deterministic Markdown report (`reports/sample_generated_report.md`) first, with optional LLM executive commentary (`--use-llm`).
5. **Critic Agent (`agents/critic.py`):** Verifies required sections, exact calculated figures, scope values, and provenance disclosures before persisting runs to `data/pipeline_runs_ledger.db`.

## Running the Interfaces

### 1. Luxury Editorial Web Dashboard & FastAPI Backend (Port 8000)

Start the unified API and responsive Luxury Editorial dashboard (featuring Mocha Brown, Champagne Gold, and Burnt Amber theme with full MCA CIN & BRSR Principle 6 controls):

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`. The frontend provides:
- Live company selector across verified listed entities (`ITC Limited`, `Reliance Industries Limited`, `NTPC Limited`, `Tata Steel Limited`, `HCL Technologies Limited`, `Infosys Limited`, `Tata Consultancy Services Limited`, `Wipro Limited`) and demo baselines (`Apex Manufacturing Pvt Ltd`, `GreenGrid Logistics Corp`).
- Corporate Regulatory Panel displaying 21-character MCA CIN, BSE Scrip Code, NSE Symbol, and `Section E / C: Principle 6` filing status.
- BRSR Scope 1, Scope 2, and Scope 3 Reconciliation Matrix and Energy Consumption disclosures.
- Drag-and-drop support for Activity Telemetry CSV and annual BRSR Filing PDF reports with dual-engine OCR fallback.
- REST API endpoints: `/api/health`, `/api/companies`, `/api/run`, `/api/run-csv`, and `/api/upload-brsr-pdf`.

---

## CLI Execution, Testing & Scheduling

```bash
# 1. Initialize or safely migrate the SQLite database & factor registry
python seed_enterprise_db.py

# 2. Run the isolated offline pytest suite (100% isolated via tmp_path; never resets data/)
python -m pytest

# 3. Run single CLI execution for a listed company and regenerate reports/sample_generated_report.md
python main.py --org "Reliance Industries Limited" --country "India" --start 2000 --end 2023

# 4. Run CLI with explicit 21-character MCA CIN identification
python main.py --cin "L17110MH1973PLC019786" --country "India" --start 2000 --end 2023

# 5. Run with an uploaded BRSR PDF for automated Principle 6 extraction
python main.py --org "Reliance Industries Limited" --brsr-pdf "path/to/filing.pdf"

# 6. Run periodic scheduled pipeline (validates positive interval & retries with backoff)
python main.py --schedule --interval-minutes 60
```