import pandas as pd
import numpy as np
from typing import Tuple

def handle_outliers(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    strategy = config.get("outliers", {}).get("strategy", "cap")
    if strategy == "keep":
        log = {
            "step": "outliers",
            "action": "Outliers kept as-is",
            "reason": "User selected keep strategy",
            "impact": "No changes made",
        }
        return df, log

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    actions = []
    rows_before = len(df)

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        if outlier_count == 0:
            continue

        if strategy == "remove":
            df = df[(df[col] >= lower) & (df[col] <= upper)]
            actions.append(f"{col}: removed {outlier_count} outliers")
        elif strategy == "cap":
            df[col] = df[col].clip(lower=lower, upper=upper)
            actions.append(f"{col}: capped {outlier_count} outliers to [{round(lower,4)}, {round(upper,4)}]")

    log = {
        "step": "outliers",
        "action": "; ".join(actions) if actions else "No outliers detected",
        "reason": f"Outlier strategy: {strategy} using IQR method",
        "impact": f"Rows before: {rows_before}, after: {len(df)}",
    }
    return df, log
