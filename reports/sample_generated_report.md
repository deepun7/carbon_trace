# Automated Organizational Carbon Footprint & OWID Benchmark Report — Apex Manufacturing Pvt Ltd

> **Data Provenance & Boundary Notice:** Organization activity records in this prototype report are **SIMULATED_DEMO** data (`SQLITE_DEMO_DB (enterprise_telemetry.db)`), aggregated across **2 facilities** for **Apex Manufacturing Pvt Ltd**. Estimates reflect **included activity categories only** (stationary diesel/natural gas, diesel fleet, purchased grid electricity, business flights, and HGV road freight), not a complete corporate inventory. National macro benchmark data is sourced from the **Our World in Data (OWID) CO2 Dataset** for **India**.

## 1. Executive Summary & Corporate Carbon Trajectory
Between **2007** and **2023**, **Apex Manufacturing Pvt Ltd** recorded a starting organizational footprint (across included categories) of **2953.64 tCO2e** and a latest annual footprint of **4212.46 tCO2e**, representing a net change of **42.62%** and a compound annual growth rate (CAGR) of **2.24%**. Cumulative emissions across the period totaled **59060.35 tCO2e**.

| Metric Category | Organizational Value (Apex Manufacturing Pvt Ltd) | National OWID Benchmark (India) |
| :--- | :--- | :--- |
| **Data Provenance & Boundary** | **SIMULATED_DEMO (2 Facilities, Included Categories)** | **OWID National Macro Dataset** |
| **Latest Annual Emissions (2023)** | **4212.46 tCO2e** | **3062.756 Mt CO2** |
| **Net Trajectory Change (2007–2023)** | **42.62%** | **119.79%** |
| **Compound Annual Growth Rate (CAGR)** | **2.24%** | **5.05%** |
| **CAGR Decoupling Alpha** | **-2.8%** | Baseline Reference |

## 2. Included GHG Scope 1, 2 & 3 Activity Categories & Factor Citations
Facility-level operational inputs were aggregated by `(org_id, year)` and converted into **tCO2e** using documented conversion factors (Registry `2024.3`).
> **Static Reference Factor Limitation:** Static 2024 reference emission factors are applied across all historical years in this prototype for consistent trend comparison; formal historical regulatory accounting requires year-specific annual grid and fuel factors.
- **Scope 1 (Included Stationary & Fleet Combustion):** **897.84 tCO2e**
  - *Stationary Diesel:* `2.68787 kg CO2e/L` — UK DESNZ / DEFRA Greenhouse Gas Conversion Factors 2024 (https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  - *Natural Gas:* `2.02135 kg CO2e/m3` — US EPA GHG Emission Factors Hub (2024) (https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
  - *Fleet Transport (Assumed Diesel LCV Average):* `0.17048 kg CO2e/km` — UK DESNZ 2024 Conversion Factors (Average Diesel Van / LCV)
- **Scope 2 (Purchased Electricity — Location-Based):** **2803.14 tCO2e**
  - *Grid Emission Factor (India):* `0.716 kg CO2e/kWh` — Central Electricity Authority (CEA) India CO2 Baseline Database v19.0 (2023-24) (https://cea.nic.in/cdm-co2-baseline-database/)
- **Scope 3 (Included Business Air Travel & HGV Road Freight Only):** **511.48 tCO2e**
  - *Business Air Travel:* `0.15102 kg CO2e/pkm` — UK DESNZ 2024 Business Travel - Air (without radiative forcing)
  - *HGV Road Freight:* `0.10455 kg CO2e/ton-km` — UK DESNZ 2024 Freighting Goods - All HGV Average

## 3. National Benchmarking Against OWID Macro Telemetry
National territorial emissions for **India** from the Our World in Data (OWID) dataset reached **3062.756 Mt CO2** with a national CAGR of **5.05%**. Organizational estimates (`tCO2e`) are maintained strictly separate from national macro totals (`Mt CO2`).

## 4. Walk-Forward Forecast (2024–2030) vs Baseline & Anomaly Method Agreement

> ✔️ **Baseline Comparison Note:** Ridge Walk-Forward RMSE (359.22 tCO2e) outperformed Naive Persistence Baseline RMSE (419.32 tCO2e) by 14.33%.

- **Walk-Forward Evaluation Window:** **2017–2023** (**7** expanding one-step-ahead test folds).
- **Primary Model (Autoregressive Ridge (Walk-Forward CV)):** **RMSE = 359.22 tCO2e**, **MAE = 190.5 tCO2e**, **MAPE = 5.59%**, **Out-of-Sample R² (Variance Explained vs Mean Baseline, NOT Accuracy) = -0.3645**.
- **Baseline Comparison (Naive Persistence Baseline (y_t = y_{t-1})):** **Naive RMSE = 419.32 tCO2e**, **Naive MAE = 312.61 tCO2e**, **Naive MAPE = 8.65%** (RMSE Skill vs Baseline: **14.33%**).
- **Anomaly Method Agreement (Isolation Forest vs Parametric Z-Score (Inter-Method Agreement)):** **Agreement F1 = 1.0** (Precision: `1.0`, Recall: `1.0`). *Note: This measures agreement between two unsupervised methods (Isolation Forest vs Z-Score), not ground-truth accuracy.*
- **Optional Exploratory Scope Pattern Grouping:** Exploratory K-Means Scope Pattern Grouping (k=3) Silhouette Score = **0.4573**.

### Detected Statistical Volatility Outliers (`|Z| >= 1.65`)
| Year | Organizational Emissions | YoY Change | Z-Score | Classification |
| :--- | :--- | :--- | :--- | :--- |
| 2008 | 2585.43 tCO2e | -12.47% | -1.7 | CONTRACTION_OUTLIER |
| 2020 | 3193.95 tCO2e | -20.79% | -2.63 | CONTRACTION_OUTLIER |
| 2021 | 3831.05 tCO2e | 19.95% | 1.95 | SURGE_OUTLIER |

### 2024–2030 Illustrative Walk-Forward Projection
*Note: Projections from limited annual observations are illustrative trend extrapolations. The error band (`±1.96 × Walk-Forward RMSE × √step`) is an approximate heuristic error band, not a formally calibrated 95% prediction interval.*
| Year | Projected Footprint | Approximate Error Band (±1.96 × RMSE × √step) |
| :--- | :--- | :--- |
| 2024 | 4215.1 tCO2e | 3511.02 – 4919.18 tCO2e |
| 2025 | 4279.13 tCO2e | 3283.42 – 5274.85 tCO2e |
| 2026 | 4355.99 tCO2e | 3136.48 – 5575.49 tCO2e |
| 2027 | 4435.51 tCO2e | 3027.36 – 5843.67 tCO2e |
| 2028 | 4515.6 tCO2e | 2941.23 – 6089.97 tCO2e |
| 2029 | 4595.81 tCO2e | 2871.17 – 6320.44 tCO2e |
| 2030 | 4676.04 tCO2e | 2813.22 – 6538.85 tCO2e |

## 5. Automated Decarbonization Roadmap & Scope Abatement Actions
1. **Scope 2 Renewable Electricity Procurement:** Transitioning purchased facility electricity (`2803.14 tCO2e`) to renewable PPAs reduces location-based grid exposure (`0.716 kg CO2e/kWh`).
2. **Scope 1 Thermal & Fleet Decarbonization:** Electrifying diesel commercial fleets and upgrading stationary combustion units across all **2 facilities**.
3. **Scope 3 Freight & Aviation Optimization:** Shifting HGV road freight (`0.10455 kg CO2e/ton-km`) to rail corridors and prioritizing virtual collaboration.
