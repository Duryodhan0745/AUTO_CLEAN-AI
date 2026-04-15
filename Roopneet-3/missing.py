import pandas as pd
from typing import Tuple

def handle_missing(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    actions = []
    strategy_map = config.get("missing", {})
    global_strategy = config.get("missing_global", "mean")

    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue
        strategy = strategy_map.get(col, global_strategy)
        if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].mean()
            df[col] = df[col].fillna(fill_val)
            actions.append(f"{col}: filled with mean ({round(float(fill_val),4)})")
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median()
            df[col] = df[col].fillna(fill_val)
            actions.append(f"{col}: filled with median ({round(float(fill_val),4)})")
        elif strategy == "mode":
            fill_val = df[col].mode()[0] if not df[col].mode().empty else None
            if fill_val is not None:
                df[col] = df[col].fillna(fill_val)
                actions.append(f"{col}: filled with mode ({fill_val})")
        elif strategy == "drop_rows":
            before = len(df)
            df = df.dropna(subset=[col])
            actions.append(f"{col}: dropped {before - len(df)} rows with missing values")
        elif strategy == "drop_column":
            df = df.drop(columns=[col])
            actions.append(f"{col}: column dropped (too many missing)")
        else:
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].mean()
                df[col] = df[col].fillna(fill_val)
                actions.append(f"{col}: filled with mean (default)")
            else:
                fill_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                df[col] = df[col].fillna(fill_val)
                actions.append(f"{col}: filled with mode (default)")

    log = {
        "step": "missing_values",
        "action": "; ".join(actions) if actions else "No missing values detected",
        "reason": "Handle missing values to ensure complete dataset",
        "impact": f"Processed {len(actions)} columns with missing values",
    }
    return df, log
