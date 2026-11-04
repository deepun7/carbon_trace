# Automated Organizational Carbon Footprint & OWID Benchmark Report — Apex Manufacturing Pvt Ltd

> **Data Provenance & Boundary Notice:** Organization activity records in this prototype report are **SIMULATED_DEMO** data (`SQLITE_DEMO_DB (enterprise_telemetry.db)`), aggregated across **2 facilities** for **Apex Manufacturing Pvt Ltd**. Estimates reflect **included activity categories only** (stationary diesel/natural gas, diesel fleet, purchased grid electricity, business flights, and HGV road freight), not a complete corporate inventory. National macro benchmark data is sourced from the **Our World in Data (OWID) CO2 Dataset** for **World**.

## 1. Executive Summary & Corporate Carbon Trajectory
Between **2004** and **2023**, **Apex Manufacturing Pvt Ltd** recorded a starting organizational footprint (across included categories) of **1960.02 tCO2e** and a latest annual footprint of **3116.26 tCO2e**, representing a net change of **58.99%** and a compound annual growth rate (CAGR) of **2.47%**. Cumulative emissions across the period totaled **49788.74 tCO2e**.

| Metric Category | Organizational Value (Apex Manufacturing Pvt Ltd) | National OWID Benchmark (World) |
| :--- | :--- | :--- |
| **Data Provenance & Boundary** | **SIMULATED_DEMO (2 Facilities, Included Categories)** | **OWID National Macro Dataset** |
| **Latest Annual Emissions (2023)** | **3116.26 tCO2e** | **38094.039 Mt CO2** |
| **Net Trajectory Change (2004–2023)** | **58.99%** | **33.15%** |
| **Compound Annual Growth Rate (CAGR)** | **2.47%** | **1.52%** |
| **CAGR Decoupling Alpha** | **0.95%** | Baseline Reference |

## 2. Included GHG Scope 1, 2 & 3 Activity Categories & Factor Citations
Facility-level operational inputs were aggregated by `(org_id, year)` and converted into **tCO2e** using documented conversion factors (Registry `2024.3`).
> **Static Reference Factor Limitation:** Static 2024 reference emission factors are applied across all historical years in this prototype for consistent trend comparison; formal historical regulatory accounting requires year-specific annual grid and fuel factors.
- **Scope 1 (Included Stationary & Fleet Combustion):** **897.84 tCO2e**
  - *Stationary Diesel:* `2.68787 kg CO2e/L` — UK DESNZ / DEFRA Greenhouse Gas Conversion Factors 2024 (https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  - *Natural Gas:* `2.02135 kg CO2e/m3` — US EPA GHG Emission Factors Hub (2024) (https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
  - *Fleet Transport (Assumed Diesel LCV Average):* `0.17048 kg CO2e/km` — UK DESNZ 2024 Conversion Factors (Average Diesel Van / LCV)
- **Scope 2 (Purchased Electricity — Location-Based):** **1706.94 tCO2e**
  - *Grid Emission Factor (World):* `0.436 kg CO2e/kWh` — IEA Emissions Factors 2023 Global Benchmark (https://www.iea.org/data-and-statistics)
- **Scope 3 (Included Business Air Travel & HGV Road Freight Only):** **511.48 tCO2e**
  - *Business Air Travel:* `0.15102 kg CO2e/pkm` — UK DESNZ 2024 Business Travel - Air (without radiative forcing)
  - *HGV Road Freight:* `0.10455 kg CO2e/ton-km` — UK DESNZ 2024 Freighting Goods - All HGV Average

## 3. National Benchmarking Against OWID Macro Telemetry
National territorial emissions for **World** from the Our World in Data (OWID) dataset reached **38094.039 Mt CO2** with a national CAGR of **1.52%**. Organizational estimates (`tCO2e`) are maintained strictly separate from national macro totals (`Mt CO2`).

## 4. Walk-Forward Forecast (2024–2030) vs Baseline & Anomaly Method Agreement

> ✔️ **Baseline Comparison Note:** Ridge Walk-Forward RMSE (255.96 tCO2e) outperformed Naive Persistence Baseline RMSE (305.89 tCO2e) by 16.32%.

- **Walk-Forward Evaluation Window:** **2016–2023** (**8** expanding one-step-ahead test folds).
- **Primary Model (Autoregressive Ridge (Walk-Forward CV)):** **RMSE = 255.96 tCO2e**, **MAE = 155.21 tCO2e**, **MAPE = 6.06%**, **Out-of-Sample R² (Variance Explained vs Mean Baseline, NOT Accuracy) = -0.2839**.
- **Baseline Comparison (Naive Persistence Baseline (y_t = y_{t-1})):** **Naive RMSE = 305.89 tCO2e**, **Naive MAE = 220.74 tCO2e**, **Naive MAPE = 8.31%** (RMSE Skill vs Baseline: **16.32%**).
- **Anomaly Method Agreement (Isolation Forest vs Parametric Z-Score (Inter-Method Agreement)):** **Agreement F1 = 0.6667** (Precision: `0.6667`, Recall: `0.6667`). *Note: This measures agreement between two unsupervised methods (Isolation Forest vs Z-Score), not ground-truth accuracy.*
- **Optional Exploratory Scope Pattern Grouping:** Exploratory K-Means Scope Pattern Grouping (k=3) Silhouette Score = **0.497**.

### Detected Statistical Volatility Outliers (`|Z| >= 1.65`)
| Year | Organizational Emissions | YoY Change | Z-Score | Classification |
| :--- | :--- | :--- | :--- | :--- |
| 2008 | 1910.63 tCO2e | -12.73% | -1.83 | CONTRACTION_OUTLIER |
| 2020 | 2331.55 tCO2e | -21.9% | -2.91 | CONTRACTION_OUTLIER |
| 2021 | 2825.85 tCO2e | 21.2% | 2.16 | SURGE_OUTLIER |

### 2024–2030 Illustrative Walk-Forward Projection
*Note: Projections from limited annual observations are illustrative trend extrapolations. The error band (`±1.96 × Walk-Forward RMSE × √step`) is an approximate heuristic error band, not a formally calibrated 95% prediction interval.*
| Year | Projected Footprint | Approximate Error Band (±1.96 × RMSE × √step) |
| :--- | :--- | :--- |
| 2024 | 3098.84 tCO2e | 2597.16 – 3600.52 tCO2e |
| 2025 | 3138.84 tCO2e | 2429.35 – 3848.33 tCO2e |
| 2026 | 3191.38 tCO2e | 2322.44 – 4060.32 tCO2e |
| 2027 | 3246.65 tCO2e | 2243.28 – 4250.02 tCO2e |
| 2028 | 3302.52 tCO2e | 2180.72 – 4424.32 tCO2e |
| 2029 | 3358.52 tCO2e | 2129.65 – 4587.39 tCO2e |
| 2030 | 3414.55 tCO2e | 2087.22 – 4741.88 tCO2e |

## 5. Automated Decarbonization Roadmap & Scope Abatement Actions
1. **Scope 2 Renewable Electricity Procurement:** Transitioning purchased facility electricity (`1706.94 tCO2e`) to renewable PPAs reduces location-based grid exposure (`0.436 kg CO2e/kWh`).
2. **Scope 1 Thermal & Fleet Decarbonization:** Electrifying diesel commercial fleets and upgrading stationary combustion units across all **2 facilities**.
3. **Scope 3 Freight & Aviation Optimization:** Shifting HGV road freight (`0.10455 kg CO2e/ton-km`) to rail corridors and prioritizing virtual collaboration.
