import pandas as pd
import numpy as np
from typing import Tuple
from sklearn.decomposition import PCA

def apply_pca(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, dict]:
    pca_cfg = config.get("pca", {})
    if not pca_cfg.get("enabled", False):
        log = {"step": "pca", "action": "PCA skipped", "reason": "Disabled by user", "impact": "None"}
        return df, log

    variance = pca_cfg.get("variance", 0.95)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) < 2:
        log = {"step": "pca", "action": "PCA skipped", "reason": "Not enough numeric columns", "impact": "None"}
        return df, log

    X = df[numeric_cols].fillna(0)
    non_numeric = df.drop(columns=numeric_cols)

    pca = PCA(n_components=variance, svd_solver="full")
    transformed = pca.fit_transform(X)
    pca_cols = [f"PC{i+1}" for i in range(transformed.shape[1])]
    pca_df = pd.DataFrame(transformed, columns=pca_cols, index=df.index)

    df = pd.concat([non_numeric.reset_index(drop=True), pca_df.reset_index(drop=True)], axis=1)

    log = {
        "step": "pca",
        "action": f"Applied PCA: {len(numeric_cols)} features → {len(pca_cols)} components ({int(variance*100)}% variance retained)",
        "reason": f"Dimensionality reduction retaining {int(variance*100)}% explained variance",
        "impact": f"Reduced from {len(numeric_cols)} to {len(pca_cols)} components",
        "components": pca_cols,
    }
    return df, log
