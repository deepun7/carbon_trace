from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    precision_score, recall_score, f1_score, silhouette_score
)
from state import CarbonAgentState


def predict_walk_forward_fold(records: list[dict], fold_index: int) -> dict[str, Any]:
    """Predict a single walk-forward fold strictly without look-ahead leakage.
    
    Slices train_series = series[:fold_index] BEFORE constructing lag features or
    fitting scalers, ensuring bit-for-bit invariance to future target changes.
    """
    df = pd.DataFrame(records).sort_values("year").reset_index(drop=True)
    if fold_index < 2 or fold_index >= len(df):
        raise ValueError(f"Invalid fold_index {fold_index} for series of length {len(df)}")
    train_slice = df.iloc[:fold_index]
    X_train = np.column_stack([
        train_slice["year"].iloc[1:].values,
        train_slice["total_org_tco2e"].iloc[:-1].values
    ])
    y_train = train_slice["total_org_tco2e"].iloc[1:].values
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    model.fit(X_train, y_train)
    target_year = int(df["year"].iloc[fold_index])
    last_train_val = float(train_slice["total_org_tco2e"].iloc[-1])
    pred = float(model.predict([[target_year, last_train_val]])[0])
    return {
        "target_year": target_year,
        "prediction": pred,
        "X_train": X_train.tolist(),
        "y_train": y_train.tolist(),
    }


def ml_engine_agent(state: CarbonAgentState) -> dict:
    records = state.get("annual_emissions_records", [])
    logs = list(state.get("agent_logs", []))

    if len(records) < 5:
        logs.append(f"⚠️ [ML Engine Agent] Series length ({len(records)} yrs) < 5 minimum required for walk-forward validation.")
        return {
            "ml_evaluation_metrics": {
                "status": "SKIPPED_SHORT_HISTORY",
                "reason": f"Requires >= 5 annual observations (found {len(records)}).",
                "forecast_horizon_label": "N/A",
                "worse_than_baseline": False,
                "baseline_comparison_note": "Skipped due to short history."
            },
            "forecast_records": [],
            "agent_logs": logs
        }

    logs.append("🧠 [ML Engine Agent] Running Leak-Free Walk-Forward Validation vs Naive Persistence Baseline & Method Agreement...")
    df = pd.DataFrame(records).sort_values("year").reset_index(drop=True)
    n = len(df)
    years = df["year"].values
    y = df["total_org_tco2e"].values

    min_train_size = max(3, min(int(n * 0.6), n - 2))
    y_true_wf, y_pred_wf, y_naive_wf, test_years = [], [], [], []
    fold_predictions = []

    # Strictly leak-free expanding window walk-forward validation
    for i in range(min_train_size, n):
        # 1. Slice training series strictly BEFORE computing lag features or scaling
        train_slice = df.iloc[:i]
        
        # 2. Build autoregressive lag features strictly inside the fold's training slice
        # Row 0 has no preceding lag, so training pairs start from index 1
        X_train_i = np.column_stack([
            train_slice["year"].iloc[1:].values,
            train_slice["total_org_tco2e"].iloc[:-1].values  # lag1
        ])
        y_train_i = train_slice["total_org_tco2e"].iloc[1:].values

        # 3. Fit scaler and Ridge regression strictly on (X_train_i, y_train_i)
        model_step = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
        model_step.fit(X_train_i, y_train_i)

        # 4. Predict one-step-ahead test target at index i using last training ground-truth as lag1
        target_year = int(years[i])
        last_train_target = float(train_slice["total_org_tco2e"].iloc[-1])
        X_test_i = np.array([[target_year, last_train_target]])
        pred_i = float(model_step.predict(X_test_i)[0])

        true_val = float(y[i])
        naive_val = last_train_target

        y_true_wf.append(true_val)
        y_pred_wf.append(pred_i)
        y_naive_wf.append(naive_val)
        test_years.append(target_year)
        fold_predictions.append({
            "year": target_year,
            "y_true": true_val,
            "y_pred": pred_i,
            "y_naive": naive_val,
        })

    y_true_arr = np.array(y_true_wf)
    y_pred_arr = np.array(y_pred_wf)
    y_naive_arr = np.array(y_naive_wf)

    wf_r2 = float(r2_score(y_true_arr, y_pred_arr)) if len(y_true_arr) > 1 else 0.0
    wf_rmse = float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr)))
    wf_mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
    wf_mape = float(np.mean(np.abs((y_true_arr - y_pred_arr) / np.maximum(y_true_arr, 1e-5))) * 100.0)

    naive_rmse = float(np.sqrt(mean_squared_error(y_true_arr, y_naive_arr)))
    naive_mae = float(mean_absolute_error(y_true_arr, y_naive_arr))
    naive_mape = float(np.mean(np.abs((y_true_arr - y_naive_arr) / np.maximum(y_true_arr, 1e-5))) * 100.0)
    skill_over_naive_pct = ((naive_rmse - wf_rmse) / naive_rmse * 100.0) if naive_rmse > 0 else 0.0

    worse_than_baseline = bool(wf_rmse > naive_rmse)
    if worse_than_baseline:
        baseline_note = (
            f"WARNING: Ridge Walk-Forward RMSE ({wf_rmse:.2f} tCO2e) is higher than Naive Persistence Baseline RMSE "
            f"({naive_rmse:.2f} tCO2e) over {test_years[0]}–{test_years[-1]} due to small sample size / shock volatility. "
            f"Prefer the Naive Baseline for short-term point estimates."
        )
        logs.append(f"⚠️ [ML Engine Agent] {baseline_note}")
    else:
        baseline_note = (
            f"Ridge Walk-Forward RMSE ({wf_rmse:.2f} tCO2e) outperformed Naive Persistence Baseline RMSE "
            f"({naive_rmse:.2f} tCO2e) by {skill_over_naive_pct:.2f}%."
        )

    # Fit full model strictly on all historical pairs
    X_full = np.column_stack([
        df["year"].iloc[1:].values,
        df["total_org_tco2e"].iloc[:-1].values  # lag1
    ])
    y_full = df["total_org_tco2e"].iloc[1:].values

    full_model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    full_model.fit(X_full, y_full)

    last_year = int(df["year"].max())
    fc_start_year = last_year + 1
    fc_end_year = max(2030, last_year + 7)

    # Recursive autoregressive multi-step projection without ground-truth peeking
    current_lag = float(df["total_org_tco2e"].iloc[-1])
    forecast_records = []
    for step, yr in enumerate(range(fc_start_year, fc_end_year + 1), start=1):
        x_next = np.array([[yr, current_lag]])
        pred_val = float(max(0.0, full_model.predict(x_next)[0]))
        approx_band = 1.96 * wf_rmse * np.sqrt(step)
        forecast_records.append({
            "year": int(yr),
            "predicted_org_tco2e": round(pred_val, 2),
            "ci_lower_tco2e": round(max(0.0, pred_val - approx_band), 2),
            "ci_upper_tco2e": round(pred_val + approx_band, 2)
        })
        current_lag = pred_val

    # Anomaly Z-Score without future look-ahead (expanding statistics)
    df["org_yoy_clean"] = df["org_yoy_pct"].fillna(0.0)
    df["owid_yoy_clean"] = df["owid_national_yoy_pct"].fillna(0.0)

    z_scores = []
    for t in range(len(df)):
        hist_slice = df["org_yoy_clean"].iloc[:t+1]
        if len(hist_slice) < 3:
            z_scores.append(0.0)
        else:
            m_t = float(hist_slice.mean())
            s_t = float(hist_slice.std())
            z_scores.append((float(df["org_yoy_clean"].iloc[t]) - m_t) / max(s_t, 1e-5))

    z_series = pd.Series(z_scores, index=df.index)
    parametric_flags = (z_series.abs() >= 1.65).astype(int).to_numpy(copy=True)
    if parametric_flags.sum() == 0 and len(z_scores) > 0:
        parametric_flags[int(z_series.abs().idxmax())] = 1

    contamination_rate = max(0.05, min(0.25, float(parametric_flags.mean())))
    X_anom = StandardScaler().fit_transform(df[["org_yoy_clean", "owid_yoy_clean"]].values)
    iso = IsolationForest(contamination=contamination_rate, random_state=42)
    iso_flags = np.where(iso.fit_predict(X_anom) == -1, 1, 0)

    consensus_precision = float(precision_score(parametric_flags, iso_flags, zero_division=0))
    consensus_recall = float(recall_score(parametric_flags, iso_flags, zero_division=0))
    consensus_f1 = float(f1_score(parametric_flags, iso_flags, zero_division=0))

    cluster_X = StandardScaler().fit_transform(
        df[["scope_1_tco2e", "scope_2_tco2e", "scope_3_tco2e"]].values
    )
    n_clusters = min(3, max(2, len(df) // 3))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(cluster_X)
    sil_score = float(silhouette_score(cluster_X, labels)) if len(set(labels)) > 1 else 0.0

    test_period_str = f"{test_years[0]}–{test_years[-1]}" if test_years else "N/A"
    horizon_label = f"{fc_start_year}–{fc_end_year}"

    ml_metrics = {
        "status": "COMPLETED",
        "forecast_model": "Autoregressive Ridge (Walk-Forward CV)",
        "baseline_model": "Naive Persistence Baseline (y_t = y_{t-1})",
        "test_period": test_period_str,
        "forecast_horizon_label": horizon_label,
        "walk_forward_folds": int(len(y_true_arr)),
        "fold_predictions": fold_predictions,
        "r2_score": round(wf_r2, 4),
        "rmse_tco2e": round(wf_rmse, 2),
        "mae_tco2e": round(wf_mae, 2),
        "mape_pct": round(wf_mape, 2),
        "baseline_naive_rmse_tco2e": round(naive_rmse, 2),
        "baseline_naive_mae_tco2e": round(naive_mae, 2),
        "baseline_naive_mape_pct": round(naive_mape, 2),
        "rmse_skill_over_naive_pct": round(skill_over_naive_pct, 2),
        "worse_than_baseline": worse_than_baseline,
        "baseline_comparison_note": baseline_note,
        "predicted_end_org_tco2e": forecast_records[-1]["predicted_org_tco2e"] if forecast_records else 0.0,
        "predicted_2030_org_tco2e": forecast_records[-1]["predicted_org_tco2e"] if forecast_records else 0.0,
        "anomaly_model": "Isolation Forest vs Parametric Z-Score (Inter-Method Agreement)",
        "evaluation_methodology": "Agreement between unsupervised methods (not ground-truth accuracy)",
        "consensus_precision": round(consensus_precision, 4),
        "consensus_recall": round(consensus_recall, 4),
        "consensus_f1_score": round(consensus_f1, 4),
        "clustering_model": f"Exploratory K-Means Scope Pattern Grouping (k={n_clusters})",
        "silhouette_score": round(sil_score, 4)
    }

    logs.append(
        f"✅ [ML Engine Agent] Test Period {test_period_str} ({len(y_true_arr)} folds): "
        f"Ridge RMSE={ml_metrics['rmse_tco2e']} vs Naive RMSE={ml_metrics['baseline_naive_rmse_tco2e']} tCO2e "
        f"| Forecast Horizon: {horizon_label}."
    )

    return {
        "ml_evaluation_metrics": ml_metrics,
        "forecast_records": forecast_records,
        "agent_logs": logs
    }