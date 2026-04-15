import pandas as pd
import numpy as np
from typing import Tuple
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression, LinearRegression

def apply_rfe(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    rfe_cfg = config.get("rfe", {})
    if not rfe_cfg.get("enabled", True):
        log = {"step": "rfe", "action": "RFE skipped", "reason": "Disabled by user", "impact": "None"}
        return df, log

    target = rfe_cfg.get("target")
    n_features = rfe_cfg.get("n_features", None)

    if not target or target not in df.columns:
        log = {"step": "rfe", "action": "RFE skipped", "reason": "No valid target column specified", "impact": "None"}
        return df, log

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c != target]

    if len(feature_cols) < 2:
        log = {"step": "rfe", "action": "RFE skipped", "reason": "Not enough feature columns", "impact": "None"}
        return df, log

    X = df[feature_cols].fillna(0)
    y = df[target].fillna(0)

    n_select = n_features if n_features and n_features < len(feature_cols) else max(1, len(feature_cols) // 2)

    unique_targets = y.nunique()
    if unique_targets <= 10:
        estimator = LogisticRegression(max_iter=500, solver="lbfgs")
    else:
        estimator = LinearRegression()

    try:
        selector = RFE(estimator=estimator, n_features_to_select=n_select)
        selector.fit(X, y)
        selected = [feature_cols[i] for i, s in enumerate(selector.support_) if s]
        dropped = [c for c in feature_cols if c not in selected]
        df = df[[c for c in df.columns if c not in dropped]]
        log = {
            "step": "rfe",
            "action": f"Selected {len(selected)} features: {selected}. Dropped: {dropped}",
            "reason": f"RFE to select top {n_select} features using target '{target}'",
            "impact": f"Removed {len(dropped)} low-importance features",
            "selected": selected,
            "dropped": dropped,
        }
    except Exception as e:
        log = {"step": "rfe", "action": f"RFE failed: {str(e)}", "reason": "Error during RFE", "impact": "None"}

    return df, log
