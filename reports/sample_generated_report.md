# Automated Organizational Carbon Footprint & OWID Benchmark Report — GreenGrid Logistics Corp

> **Data Provenance & Boundary Notice:** Organization activity records in this prototype report are **SIMULATED_DEMO** data (`SQLITE_DEMO_DB (enterprise_telemetry.db)`), aggregated across **2 facilities** for **GreenGrid Logistics Corp**. Estimates reflect **included activity categories only** (stationary diesel/natural gas, diesel fleet, purchased grid electricity, business flights, and HGV road freight), not a complete corporate inventory. National macro benchmark data is sourced from the **Our World in Data (OWID) CO2 Dataset** for **India**.

## 1. Executive Summary & Corporate Carbon Trajectory
Between **2011** and **2019**, **GreenGrid Logistics Corp** recorded a starting organizational footprint (across included categories) of **2469.72 tCO2e** and a latest annual footprint of **3181.08 tCO2e**, representing a net change of **28.8%** and a compound annual growth rate (CAGR) of **3.21%**. Cumulative emissions across the period totaled **25464.84 tCO2e**.

| Metric Category | Organizational Value (GreenGrid Logistics Corp) | National OWID Benchmark (India) |
| :--- | :--- | :--- |
| **Data Provenance & Boundary** | **SIMULATED_DEMO (2 Facilities, Included Categories)** | **OWID National Macro Dataset** |
| **Latest Annual Emissions (2019)** | **3181.08 tCO2e** | **2611.175 Mt CO2** |
| **Net Trajectory Change (2011–2019)** | **28.8%** | **47.88%** |
| **Compound Annual Growth Rate (CAGR)** | **3.21%** | **5.01%** |
| **CAGR Decoupling Alpha** | **-1.8%** | Baseline Reference |

## 2. Included GHG Scope 1, 2 & 3 Activity Categories & Factor Citations
Facility-level operational inputs were aggregated by `(org_id, year)` and converted into **tCO2e** using documented conversion factors (Registry `2024.3`).
> **Static Reference Factor Limitation:** Static 2024 reference emission factors are applied across all historical years in this prototype for consistent trend comparison; formal historical regulatory accounting requires year-specific annual grid and fuel factors.
- **Scope 1 (Included Stationary & Fleet Combustion):** **567.21 tCO2e**
  - *Stationary Diesel:* `2.68787 kg CO2e/L` — UK DESNZ / DEFRA Greenhouse Gas Conversion Factors 2024 (https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  - *Natural Gas:* `2.02135 kg CO2e/m3` — US EPA GHG Emission Factors Hub (2024) (https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
  - *Fleet Transport (Assumed Diesel LCV Average):* `0.17048 kg CO2e/km` — UK DESNZ 2024 Conversion Factors (Average Diesel Van / LCV)
- **Scope 2 (Purchased Electricity — Location-Based):** **2008.38 tCO2e**
  - *Grid Emission Factor (India):* `0.716 kg CO2e/kWh` — Central Electricity Authority (CEA) India CO2 Baseline Database v19.0 (2023-24) (https://cea.nic.in/cdm-co2-baseline-database/)
- **Scope 3 (Included Business Air Travel & HGV Road Freight Only):** **605.49 tCO2e**
  - *Business Air Travel:* `0.15102 kg CO2e/pkm` — UK DESNZ 2024 Business Travel - Air (without radiative forcing)
  - *HGV Road Freight:* `0.10455 kg CO2e/ton-km` — UK DESNZ 2024 Freighting Goods - All HGV Average

## 3. National Benchmarking Against OWID Macro Telemetry
National territorial emissions for **India** from the Our World in Data (OWID) dataset reached **2611.175 Mt CO2** with a national CAGR of **5.01%**. Organizational estimates (`tCO2e`) are maintained strictly separate from national macro totals (`Mt CO2`).

## 4. Walk-Forward Forecast (2020–2030) vs Baseline & Anomaly Method Agreement

> ✔️ **Baseline Comparison Note:** Ridge Walk-Forward RMSE (11.22 tCO2e) outperformed Naive Persistence Baseline RMSE (87.57 tCO2e) by 87.19%.

- **Walk-Forward Evaluation Window:** **2016–2019** (**4** expanding one-step-ahead test folds).
- **Primary Model (Autoregressive Ridge (Walk-Forward CV)):** **RMSE = 11.22 tCO2e**, **MAE = 10.7 tCO2e**, **MAPE = 0.35%**, **Out-of-Sample R² (Variance Explained vs Mean Baseline, NOT Accuracy) = 0.9869**.
- **Baseline Comparison (Naive Persistence Baseline (y_t = y_{t-1})):** **Naive RMSE = 87.57 tCO2e**, **Naive MAE = 87.48 tCO2e**, **Naive MAPE = 2.87%** (RMSE Skill vs Baseline: **87.19%**).
- **Anomaly Method Agreement (Isolation Forest vs Parametric Z-Score (Inter-Method Agreement)):** **Agreement F1 = 1.0** (Precision: `1.0`, Recall: `1.0`). *Note: This measures agreement between two unsupervised methods (Isolation Forest vs Z-Score), not ground-truth accuracy.*
- **Optional Exploratory Scope Pattern Grouping:** Exploratory K-Means Scope Pattern Grouping (k=3) Silhouette Score = **0.4778**.

### Detected Statistical Volatility Outliers (`|Z| >= 1.65`)
| Year | Organizational Emissions | YoY Change | Z-Score | Classification |
| :--- | :--- | :--- | :--- | :--- |
| 2019 | 3181.08 tCO2e | 2.62% | -1.74 | CONTRACTION_OUTLIER |

### 2020–2030 Illustrative Walk-Forward Projection
*Note: Projections from limited annual observations are illustrative trend extrapolations. The error band (`±1.96 × Walk-Forward RMSE × √step`) is an approximate heuristic error band, not a formally calibrated 95% prediction interval.*
| Year | Projected Footprint | Approximate Error Band (±1.96 × RMSE × √step) |
| :--- | :--- | :--- |
| 2020 | 3256.04 tCO2e | 3234.05 – 3278.02 tCO2e |
| 2021 | 3336.08 tCO2e | 3304.99 – 3367.17 tCO2e |
| 2022 | 3418.52 tCO2e | 3380.44 – 3456.61 tCO2e |
| 2023 | 3502.1 tCO2e | 3458.13 – 3546.07 tCO2e |
| 2024 | 3586.22 tCO2e | 3537.05 – 3635.38 tCO2e |
| 2025 | 3670.58 tCO2e | 3616.73 – 3724.43 tCO2e |
| 2026 | 3755.07 tCO2e | 3696.9 – 3813.24 tCO2e |
| 2027 | 3839.61 tCO2e | 3777.42 – 3901.79 tCO2e |
| 2028 | 3924.18 tCO2e | 3858.22 – 3990.13 tCO2e |
| 2029 | 4008.76 tCO2e | 3939.23 – 4078.28 tCO2e |
| 2030 | 4093.34 tCO2e | 4020.43 – 4166.26 tCO2e |

## 5. Automated Decarbonization Roadmap & Scope Abatement Actions
1. **Scope 2 Renewable Electricity Procurement:** Transitioning purchased facility electricity (`2008.38 tCO2e`) to renewable PPAs reduces location-based grid exposure (`0.716 kg CO2e/kWh`).
2. **Scope 1 Thermal & Fleet Decarbonization:** Electrifying diesel commercial fleets and upgrading stationary combustion units across all **2 facilities**.
3. **Scope 3 Freight & Aviation Optimization:** Shifting HGV road freight (`0.10455 kg CO2e/ton-km`) to rail corridors and prioritizing virtual collaboration.
