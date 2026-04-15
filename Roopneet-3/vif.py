import pandas as pd
import numpy as np
from typing import Tuple

def apply_vif(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    if not config.get("vif", {}).get("enabled", True):
        log = {"step": "vif", "action": "VIF skipped", "reason": "Disabled by user", "impact": "None"}
        return df, log

    try:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
    except ImportError:
        log = {"step": "vif", "action": "VIF skipped", "reason": "statsmodels not installed", "impact": "None"}
        return df, log

    threshold = config.get("vif", {}).get("threshold", 10)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) < 2:
        log = {"step": "vif", "action": "VIF skipped", "reason": "Not enough numeric columns", "impact": "None"}
        return df, log

    removed = []
    max_iter = 50
    iteration = 0

    while iteration < max_iter:
        iteration += 1
        sub = df[numeric_cols].dropna()
        if sub.shape[1] < 2:
            break
        vif_data = pd.DataFrame()
        vif_data["feature"] = sub.columns
        try:
            vif_data["vif"] = [variance_inflation_factor(sub.values, i) for i in range(sub.shape[1])]
        except Exception:
            break
        max_vif = vif_data["vif"].max()
        if max_vif <= threshold:
            break
        drop_col = vif_data.sort_values("vif", ascending=False).iloc[0]["feature"]
        numeric_cols.remove(drop_col)
        df = df.drop(columns=[drop_col])
        removed.append(drop_col)

    log = {
        "step": "vif",
        "action": f"Removed {len(removed)} columns with VIF > {threshold}: {removed}" if removed else f"All features passed VIF threshold ({threshold})",
        "reason": f"Remove multicollinear features exceeding VIF threshold {threshold}",
        "impact": f"Dropped {len(removed)} features",
        "removed": removed,
    }
    return df, log
