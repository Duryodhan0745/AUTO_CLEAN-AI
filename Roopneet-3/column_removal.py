import pandas as pd
from typing import List, Tuple

def remove_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, dict]:
    existing = [c for c in columns if c in df.columns]
    df = df.drop(columns=existing)
    log = {
        "step": "column_removal",
        "action": f"Removed columns: {existing}" if existing else "No columns removed",
        "reason": "User specified columns to remove",
        "impact": f"Dropped {len(existing)} columns",
        "removed": existing,
    }
    return df, log
