import pandas as pd
from pathlib import Path

SCHEMA_COLUMNS = {"date/time", "lat", "lon", "base"}
LOCAL_CSV = Path("uber-raw-data-sep14.csv.gz")
LOCAL_PARQUET = Path("uber-raw-data-sep14.parquet")
REMOTE_URL = "https://github.com/ravi-rajpurohit-gh/uber-nyc-dashboard/raw/main/uber-raw-data-sep14.csv.gz"


def load_raw() -> pd.DataFrame:
    # Parquet reads ~4x faster than gzip CSV; prefer it when available
    if LOCAL_PARQUET.exists():
        return pd.read_parquet(LOCAL_PARQUET)

    source = LOCAL_CSV if LOCAL_CSV.exists() else REMOTE_URL
    df = pd.read_csv(source)
    df.columns = df.columns.str.lower().str.strip()
    _validate(df)

    try:
        df.to_parquet(LOCAL_PARQUET, index=False)
    except OSError:
        pass  # Read-only filesystem (e.g. Streamlit Cloud) — not a problem

    return df


def _validate(df: pd.DataFrame) -> None:
    missing = SCHEMA_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Schema validation failed — missing columns: {missing}")
