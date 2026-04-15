import pandas as pd
from typing import Tuple, List

from column_removal import remove_columns
from missing import handle_missing
from outliers import handle_outliers
from encoding import apply_encoding
from scaling import apply_scaling
from vif import apply_vif
from rfe import apply_rfe
from pca import apply_pca

def run_pipeline(df: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, List[dict]]:
    logs = []

    df, log = remove_columns(df, config.get("remove_columns", []))
    logs.append(log)

    df, log = handle_missing(df, config)
    logs.append(log)

    df, log = handle_outliers(df, config)
    logs.append(log)

    df, log = apply_encoding(df, config)
    logs.append(log)

    df, log = apply_scaling(df, config)
    logs.append(log)

    df, log = apply_vif(df, config)
    logs.append(log)

    df, log = apply_rfe(df, config)
    logs.append(log)

    df, log = apply_pca(df, config)
    logs.append(log)

    return df, logs
