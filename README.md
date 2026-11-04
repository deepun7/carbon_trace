# CarbonTrace — A Multi-Agent Prototype for Automated Organizational Carbon Tracking, with Simulated Activity Data and OWID National Benchmarking

**B.Tech 4th-Year CSE (AI/ML) Capstone Prototype**

## Overview
CarbonTrace is a 5-agent LangGraph prototype that automates organizational greenhouse gas (GHG) accounting across selected operational categories and benchmarks organizational emission trajectories against national macro data from the **Our World in Data (OWID) CO₂ Dataset**.

### Key Prototype Design & Honest Boundaries
- **Simulated Demo Data vs External CSV:** Seeded SQLite records (`data/enterprise_telemetry.db`) represent two multi-facility demo organizations (`Apex Manufacturing Pvt Ltd` and `GreenGrid Logistics Corp`) and are explicitly labeled as `SIMULATED_DEMO`. Users can also supply external CSV activity files (`--csv` or dashboard upload), which undergo strict validation (schema, numeric types, non-negativity, duplicate `(org_id, facility_id, year)` checks, and provenance consistency).
- **Included Activity Categories Only:** Calculations cover selected Scope 1 (stationary diesel, natural gas, diesel commercial fleet), Scope 2 (location-based grid electricity), and Scope 3 (short/medium-haul business flights, HGV road freight) categories rather than a complete corporate inventory.
- **Static 2024 Reference Factor Limitation:** Documented conversion factors (`data/emission_factors_registry.json` from UK DESNZ 2024, US EPA 2024, CEA India v19.0, IEA) are applied as static reference values across historical years for consistent prototype trend comparison.
- **Walk-Forward Validation vs Naive Persistence Baseline:** The ML Engine evaluates an Autoregressive Ridge model using expanding-window walk-forward validation against a **Naive Persistence Baseline ($\hat{y}_t = y_{t-1}$)** and explicitly warns when the regression RMSE exceeds the naive baseline on small or volatile samples. Anomaly F1 measures **unsupervised inter-method agreement** (Isolation Forest vs Z-Score), not ground-truth accuracy.

## 5-Agent Architecture
1. **Ingestion Agent (`agents/ingestion.py`):** Queries SQLite or validates an external CSV filtered strictly by `org_id`, aggregates multi-facility records by `(org_id, year)`, and loads OWID national benchmark data with a **24-hour cache TTL**.
2. **Calculation Agent (`agents/calculation.py`):** Applies documented conversion factors to compute Scope 1, 2, and 3 emissions in `tCO₂e` while keeping OWID national macro totals (`Mt CO₂`) strictly separate.
3. **ML Engine Agent (`agents/ml_engine.py`):** Runs expanding-window walk-forward cross-validation against a naive persistence baseline, computes dynamic forecast horizons (`last_year + 1` onward) with approximate heuristic error bands (`±1.96 × RMSE × √step`), and evaluates inter-method anomaly agreement plus optional exploratory K-Means grouping.
4. **Reporting Agent (`agents/reporting.py`):** Compiles a deterministic Markdown report (`reports/sample_generated_report.md`) first, with optional LLM executive commentary (`--use-llm`).
5. **Critic Agent (`agents/critic.py`):** Verifies required sections, exact calculated figures, scope values, and provenance disclosures before persisting runs to `data/pipeline_runs_ledger.db`.

## CLI Usage, Testing & Periodic Scheduling

```bash
# 1. Initialize or safely migrate the SQLite demo database & factor registry
python seed_enterprise_db.py

# 2. Run the isolated offline pytest suite (uses tmp_path; never resets data/)
python -m pytest tests/test_pipeline.py

# 3. Run single CLI execution and regenerate reports/sample_generated_report.md
python main.py --org "Apex Manufacturing Pvt Ltd" --country "India" --start 2000 --end 2023

# 4. Run periodic scheduled pipeline (validates positive interval & retries with backoff)
python main.py --schedule --interval-minutes 60

# 5. Launch Streamlit dashboard
streamlit run app.py