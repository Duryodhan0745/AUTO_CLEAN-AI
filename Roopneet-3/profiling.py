import pandas as pd
import numpy as np

def profile_dataset(df: pd.DataFrame) -> dict:
    profile = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": [],
        "preview": df.head(10).fillna("").astype(str).to_dict(orient="records"),
        "column_names": df.columns.tolist(),
    }

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        missing = int(series.isna().sum())
        missing_pct = round(float(missing / len(series) * 100), 2)
        unique = int(series.nunique())

        col_info = {
            "name": col,
            "dtype": dtype,
            "missing": missing,
            "missing_pct": missing_pct,
            "unique": unique,
        }

        if pd.api.types.is_numeric_dtype(series):
            col_info["type"] = "numeric"
            col_info["mean"] = round(float(series.mean()), 4) if not series.isna().all() else None
            col_info["std"] = round(float(series.std()), 4) if not series.isna().all() else None
            col_info["min"] = round(float(series.min()), 4) if not series.isna().all() else None
            col_info["max"] = round(float(series.max()), 4) if not series.isna().all() else None
            col_info["median"] = round(float(series.median()), 4) if not series.isna().all() else None
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = int(((series < lower) | (series > upper)).sum())
            col_info["outliers"] = outliers
        else:
            col_info["type"] = "categorical"
            top = series.value_counts().head(5)
            col_info["top_values"] = {str(k): int(v) for k, v in top.items()}

        profile["columns"].append(col_info)

    return profile
