import pandas as pd
import numpy as np
from typing import Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

def apply_scaling(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    strategy = config.get("scaling", {}).get("strategy", "standard")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        log = {
            "step": "scaling",
            "action": "No numeric columns to scale",
            "reason": "Scaling skipped",
            "impact": "None",
        }
        return df, log

    if strategy == "minmax":
        scaler = MinMaxScaler()
    elif strategy == "robust":
        scaler = RobustScaler()
    else:
        scaler = StandardScaler()

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    log = {
        "step": "scaling",
        "action": f"Applied {strategy} scaling to {len(numeric_cols)} numeric columns",
        "reason": f"Normalize feature magnitudes using {strategy} scaler",
        "impact": f"Scaled: {numeric_cols}",
    }
    return df, log
