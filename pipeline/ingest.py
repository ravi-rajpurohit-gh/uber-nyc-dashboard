import pandas as pd
from pathlib import Path

SCHEMA_COLUMNS = {"date/time", "lat", "lon", "base"}
LOCAL_PATH = Path("uber-raw-data-sep14.csv.gz")
REMOTE_URL = "https://github.com/ravi-rajpurohit-gh/uber-nyc-dashboard/raw/main/uber-raw-data-sep14.csv.gz"


def load_raw() -> pd.DataFrame:
    source = LOCAL_PATH if LOCAL_PATH.exists() else REMOTE_URL
    df = pd.read_csv(source)
    df.columns = df.columns.str.lower().str.strip()
    _validate(df)
    return df


def _validate(df: pd.DataFrame) -> None:
    missing = SCHEMA_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Schema validation failed — missing columns: {missing}")
