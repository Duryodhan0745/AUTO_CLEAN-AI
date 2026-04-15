import json
from typing import List

def build_pipeline_script(config: dict, logs: List[dict]) -> str:
    lines = []
    lines.append("# AutoPrep AI - Generated Pipeline Script")
    lines.append("# This script reproduces all preprocessing steps applied to your dataset.")
    lines.append("")
    lines.append("import pandas as pd")
    lines.append("import numpy as np")
    lines.append("from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler")
    lines.append("from sklearn.feature_selection import RFE")
    lines.append("from sklearn.linear_model import LogisticRegression, LinearRegression")
    lines.append("from sklearn.decomposition import PCA")
    lines.append("try:")
    lines.append("    from statsmodels.stats.outliers_influence import variance_inflation_factor")
    lines.append("except ImportError:")
    lines.append("    variance_inflation_factor = None")
    lines.append("")
    lines.append("# ── CONFIG ──────────────────────────────────────────────────────────────────")
    lines.append(f"CONFIG = {json.dumps(config, indent=4)}")
    lines.append("")
    lines.append("# ── LOAD DATA ───────────────────────────────────────────────────────────────")
    lines.append("df = pd.read_csv('your_dataset.csv')")
    lines.append("")

    for log in logs:
        step = log.get("step", "unknown")
        lines.append(f"# ── STEP: {step.upper()} ─────────────────────────────────────────────")
        lines.append(f"# Action: {log.get('action', '')}")
        lines.append(f"# Reason: {log.get('reason', '')}")

        if step == "column_removal":
            removed = log.get("removed", [])
            if removed:
                lines.append(f"df = df.drop(columns={removed}, errors='ignore')")

        elif step == "missing_values":
            global_strat = config.get("missing_global", "mean")
            lines.append(f"for col in df.columns:")
            lines.append(f"    strategy = CONFIG.get('missing', {{}}).get(col, '{global_strat}')")
            lines.append(f"    if df[col].isna().sum() == 0:")
            lines.append(f"        continue")
            lines.append(f"    if strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):")
            lines.append(f"        df[col] = df[col].fillna(df[col].mean())")
            lines.append(f"    elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):")
            lines.append(f"        df[col] = df[col].fillna(df[col].median())")
            lines.append(f"    elif strategy == 'mode':")
            lines.append(f"        df[col] = df[col].fillna(df[col].mode()[0])")
            lines.append(f"    elif strategy == 'drop_rows':")
            lines.append(f"        df = df.dropna(subset=[col])")
            lines.append(f"    elif strategy == 'drop_column':")
            lines.append(f"        df = df.drop(columns=[col])")
            lines.append(f"    else:")
            lines.append(f"        if pd.api.types.is_numeric_dtype(df[col]):")
            lines.append(f"            df[col] = df[col].fillna(df[col].mean())")
            lines.append(f"        else:")
            lines.append(f"            df[col] = df[col].fillna(df[col].mode()[0])")

        elif step == "outliers":
            strategy = config.get("outliers", {}).get("strategy", "cap")
            if strategy != "keep":
                lines.append(f"for col in df.select_dtypes(include=[np.number]).columns:")
                lines.append(f"    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)")
                lines.append(f"    iqr = q3 - q1")
                lines.append(f"    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr")
                if strategy == "remove":
                    lines.append(f"    df = df[(df[col] >= lower) & (df[col] <= upper)]")
                else:
                    lines.append(f"    df[col] = df[col].clip(lower=lower, upper=upper)")

        elif step == "encoding":
            strategy = config.get("encoding", {}).get("strategy", "onehot")
            lines.append(f"cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()")
            if strategy == "label":
                lines.append(f"le = LabelEncoder()")
                lines.append(f"for col in cat_cols:")
                lines.append(f"    df[col] = le.fit_transform(df[col].astype(str))")
            else:
                lines.append(f"df = pd.get_dummies(df, columns=cat_cols, drop_first=False)")

        elif step == "scaling":
            strategy = config.get("scaling", {}).get("strategy", "standard")
            if strategy == "minmax":
                lines.append(f"scaler = MinMaxScaler()")
            elif strategy == "robust":
                lines.append(f"scaler = RobustScaler()")
            else:
                lines.append(f"scaler = StandardScaler()")
            lines.append(f"numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()")
            lines.append(f"df[numeric_cols] = scaler.fit_transform(df[numeric_cols])")

        elif step == "vif":
            threshold = config.get("vif", {}).get("threshold", 10)
            if config.get("vif", {}).get("enabled", True):
                lines.append(f"if variance_inflation_factor:")
                lines.append(f"    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()")
                lines.append(f"    for _ in range(50):")
                lines.append(f"        sub = df[numeric_cols].dropna()")
                lines.append(f"        vifs = [variance_inflation_factor(sub.values, i) for i in range(sub.shape[1])]")
                lines.append(f"        max_vif = max(vifs)")
                lines.append(f"        if max_vif <= {threshold}: break")
                lines.append(f"        drop_idx = vifs.index(max_vif)")
                lines.append(f"        drop_col = numeric_cols[drop_idx]")
                lines.append(f"        numeric_cols.remove(drop_col)")
                lines.append(f"        df = df.drop(columns=[drop_col])")

        elif step == "rfe":
            rfe_cfg = config.get("rfe", {})
            target = rfe_cfg.get("target", "")
            n_features = rfe_cfg.get("n_features", None)
            if rfe_cfg.get("enabled", True) and target:
                n_sel = n_features if n_features else "max(1, len(feature_cols) // 2)"
                lines.append(f"target = '{target}'")
                lines.append(f"feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target]")
                lines.append(f"X, y = df[feature_cols].fillna(0), df[target].fillna(0)")
                lines.append(f"n_select = {n_sel if isinstance(n_sel, int) else 'max(1, len(feature_cols) // 2)'}")
                lines.append(f"estimator = LogisticRegression(max_iter=500) if y.nunique() <= 10 else LinearRegression()")
                lines.append(f"selector = RFE(estimator=estimator, n_features_to_select=n_select)")
                lines.append(f"selector.fit(X, y)")
                lines.append(f"selected = [feature_cols[i] for i, s in enumerate(selector.support_) if s]")
                lines.append(f"dropped = [c for c in feature_cols if c not in selected]")
                lines.append(f"df = df[[c for c in df.columns if c not in dropped]]")

        elif step == "pca":
            pca_cfg = config.get("pca", {})
            if pca_cfg.get("enabled", False):
                variance = pca_cfg.get("variance", 0.95)
                lines.append(f"numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()")
                lines.append(f"non_numeric = df.drop(columns=numeric_cols)")
                lines.append(f"pca = PCA(n_components={variance}, svd_solver='full')")
                lines.append(f"transformed = pca.fit_transform(df[numeric_cols].fillna(0))")
                lines.append(f"pca_df = pd.DataFrame(transformed, columns=[f'PC{{i+1}}' for i in range(transformed.shape[1])], index=df.index)")
                lines.append(f"df = pd.concat([non_numeric.reset_index(drop=True), pca_df.reset_index(drop=True)], axis=1)")

        lines.append("")

    lines.append("# ── SAVE OUTPUT ─────────────────────────────────────────────────────────────")
    lines.append("df.to_csv('cleaned_dataset.csv', index=False)")
    lines.append("print(f'Done. Shape: {df.shape}')")
    lines.append("")

    return "\n".join(lines)
