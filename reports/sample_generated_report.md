# Automated Organizational Carbon Footprint & OWID Benchmark Report — ITC Limited

> **Data Provenance & Boundary Notice:** Organization activity records in this prototype report are **VERIFIED_BRSR_FILING** data (`SQLITE_DEMO_DB (test_enterprise_telemetry.db)`), aggregated across **1 facilities** for **ITC Limited**. Estimates reflect **included activity categories only** (stationary diesel/natural gas, diesel fleet, purchased grid electricity, business flights, and HGV road freight), not a complete corporate inventory. National macro benchmark data is sourced from the **Our World in Data (OWID) CO2 Dataset** for **India**.

## 1. Executive Summary & Corporate Carbon Trajectory
Between **2015** and **2025**, **ITC Limited** recorded a starting organizational footprint (across included categories) of **3768.31 tCO2e** and a latest annual footprint of **4613.8 tCO2e**, representing a net change of **22.44%** and a compound annual growth rate (CAGR) of **2.04%**. Cumulative emissions across the period totaled **45260.99 tCO2e**.

| Metric Category | Organizational Value (ITC Limited) | National OWID Benchmark (India) |
| :--- | :--- | :--- |
| **Data Provenance & Boundary** | **VERIFIED_BRSR_FILING (1 Facilities, Included Categories)** | **OWID National Macro Dataset** |
| **Latest Annual Emissions (2025)** | **4613.8 tCO2e** | **2955.0 Mt CO2** |
| **Net Trajectory Change (2015–2025)** | **22.44%** | **29.89%** |
| **Compound Annual Growth Rate (CAGR)** | **2.04%** | **2.65%** |
| **CAGR Decoupling Alpha** | **-0.6%** | Baseline Reference |

## 2. Included GHG Scope 1, 2 & 3 Activity Categories & Factor Citations
Facility-level operational inputs were aggregated by `(org_id, year)` and converted into **tCO2e** using documented conversion factors (Registry `2024.3`).
> **Static Reference Factor Limitation:** Static 2024 reference emission factors are applied across all historical years in this prototype for consistent trend comparison; formal historical regulatory accounting requires year-specific annual grid and fuel factors.
- **Scope 1 (Included Stationary & Fleet Combustion):** **976.94 tCO2e**
  - *Stationary Diesel:* `2.68787 kg CO2e/L` — UK DESNZ / DEFRA Greenhouse Gas Conversion Factors 2024 (https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  - *Natural Gas:* `2.02135 kg CO2e/m3` — US EPA GHG Emission Factors Hub (2024) (https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
  - *Fleet Transport (Assumed Diesel LCV Average):* `0.17048 kg CO2e/km` — UK DESNZ 2024 Conversion Factors (Average Diesel Van / LCV)
- **Scope 2 (Purchased Electricity — Location-Based):** **3078.62 tCO2e**
  - *Grid Emission Factor (India):* `0.716 kg CO2e/kWh` — Central Electricity Authority (CEA) India CO2 Baseline Database v19.0 (2023-24) (https://cea.nic.in/cdm-co2-baseline-database/)
- **Scope 3 (Included Business Air Travel & HGV Road Freight Only):** **558.23 tCO2e**
  - *Business Air Travel:* `0.15102 kg CO2e/pkm` — UK DESNZ 2024 Business Travel - Air (without radiative forcing)
  - *HGV Road Freight:* `0.10455 kg CO2e/ton-km` — UK DESNZ 2024 Freighting Goods - All HGV Average

## 3. MCA CIN Registry & BRSR Principle 6 Provenance
- **Company:** ITC Limited
- **MCA CIN:** L16005WB1910PLC001985
- **BSE Code:** 500875
- **NSE Symbol:** ITC
- **Filing section:** Section C: Principle 6
- **BRSR metadata provenance:** VERIFIED_BRSR_FILING
- **BRSR source:** Report and Accounts / BRSR — Section C: Principle 6 (Assurance: KPMG ISAE 3000)
- **Operational activity provenance:** VERIFIED_BRSR_FILING (generated demo activity is not a reported BRSR value)
- **Document format & extraction engine:** NATIVE_DIGITAL_TEXT (1 pages, pdfplumber+pypdf)
- **Reported energy consumption:** 24025.0 TJ (6673616450.0 kWh)
- **Reported Scope 1 (BRSR):** 1045000.0 tCO2e; activity-based variance: -1044023.06 tCO2e
- **Reported Scope 2 (BRSR):** 170000.0 tCO2e; activity-based variance: -166921.38 tCO2e
- **Reported Scope 3 (BRSR):** 1442000.0 tCO2e; activity-based variance: -1441441.77 tCO2e
- **Total Extracted Footprint:** None tCO2e

## 4. National Benchmarking Against OWID Macro Telemetry
National territorial emissions for **India** from the Our World in Data (OWID) dataset reached **2955.0 Mt CO2** with a national CAGR of **2.65%**. Organizational estimates (`tCO2e`) are maintained strictly separate from national macro totals (`Mt CO2`).

## 5. Walk-Forward Forecast (2026–2032) vs Baseline & Anomaly Method Agreement

> ✔️ **Baseline Comparison Note:** Ridge Walk-Forward RMSE (312.84 tCO2e) outperformed Naive Persistence Baseline RMSE (334.53 tCO2e) by 6.48%.

- **Walk-Forward Evaluation Window:** **2021–2025** (**5** expanding one-step-ahead test folds).
- **Primary Model (Autoregressive Ridge (Walk-Forward CV)):** **RMSE = 312.84 tCO2e**, **MAE = 293.75 tCO2e**, **MAPE = 6.7%**, **Out-of-Sample R² (Variance Explained vs Mean Baseline, NOT Accuracy) = -1.3261**.
- **Baseline Comparison (Naive Persistence Baseline (y_t = y_{t-1})):** **Naive RMSE = 334.53 tCO2e**, **Naive MAE = 252.03 tCO2e**, **Naive MAPE = 6.01%** (RMSE Skill vs Baseline: **6.48%**).
- **Anomaly Method Agreement (Isolation Forest vs Parametric Z-Score (Inter-Method Agreement)):** **Agreement F1 = 0.5** (Precision: `0.5`, Recall: `0.5`). *Note: This measures agreement between two unsupervised methods (Isolation Forest vs Z-Score), not ground-truth accuracy.*
- **Optional Exploratory Scope Pattern Grouping:** Exploratory K-Means Scope Pattern Grouping (k=3) Silhouette Score = **0.496**.

### Detected Statistical Volatility Outliers (`|Z| >= 1.65`)
| Year | Organizational Emissions | YoY Change | Z-Score | Classification |
| :--- | :--- | :--- | :--- | :--- |
| 2020 | 3353.64 tCO2e | -20.79% | -2.37 | CONTRACTION_OUTLIER |
| 2021 | 4022.61 tCO2e | 19.95% | 1.78 | SURGE_OUTLIER |

### 2026–2032 Illustrative Walk-Forward Projection
*Note: Projections from limited annual observations are illustrative trend extrapolations. The error band (`±1.96 × Walk-Forward RMSE × √step`) is an approximate heuristic error band, not a formally calibrated 95% prediction interval.*
| Year | Projected Footprint | Approximate Error Band (±1.96 × RMSE × √step) |
| :--- | :--- | :--- |
| 2026 | 4551.8 tCO2e | 3938.64 – 5164.97 tCO2e |
| 2027 | 4605.32 tCO2e | 3738.17 – 5472.46 tCO2e |
| 2028 | 4672.97 tCO2e | 3610.94 – 5735.0 tCO2e |
| 2029 | 4742.36 tCO2e | 3516.04 – 5968.69 tCO2e |
| 2030 | 4811.96 tCO2e | 3440.89 – 6183.04 tCO2e |
| 2031 | 4881.59 tCO2e | 3379.66 – 6383.53 tCO2e |
| 2032 | 4951.22 tCO2e | 3328.95 – 6573.5 tCO2e |

## 6. Automated Decarbonization Roadmap & Scope Abatement Actions
1. **Scope 2 Renewable Electricity Procurement:** Transitioning purchased facility electricity (`3078.62 tCO2e`) to renewable PPAs reduces location-based grid exposure (`0.716 kg CO2e/kWh`).
2. **Scope 1 Thermal & Fleet Decarbonization:** Electrifying diesel commercial fleets and upgrading stationary combustion units across all **1 facilities**.
3. **Scope 3 Freight & Aviation Optimization:** Shifting HGV road freight (`0.10455 kg CO2e/ton-km`) to rail corridors and prioritizing virtual collaboration.
