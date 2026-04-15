import pandas as pd
from typing import Tuple
from sklearn.preprocessing import LabelEncoder

def apply_encoding(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    actions = []

    # Use LabelEncoder for all categorical columns
    for col in cat_cols:
        le = LabelEncoder()
        # Convert to string and encode
        df[col] = le.fit_transform(df[col].astype(str))
        actions.append(f"{col}: label encoded ({len(le.classes_)} unique values)")

    log = {
        "step": "encoding",
        "action": "; ".join(actions) if actions else "No categorical columns to encode",
        "reason": "Encode categorical features using LabelEncoder (numeric mapping)",
        "impact": f"Processed {len(cat_cols)} categorical columns using LabelEncoder",
    }
    return df, log
