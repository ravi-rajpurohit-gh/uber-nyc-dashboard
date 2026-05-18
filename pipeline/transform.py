import pandas as pd
import numpy as np

# Approximate bounding boxes for NYC boroughs.
# A production pipeline would use a GeoPandas spatial join against NYC's
# official borough boundary GeoJSON from NYC Open Data.
_BOROUGHS = [
    ("Staten Island", 40.477, 40.651, -74.259, -74.034),
    ("Bronx",         40.785, 40.920, -73.933, -73.748),
    ("Queens",        40.541, 40.812, -73.962, -73.700),
    ("Brooklyn",      40.570, 40.739, -74.056, -73.833),
    ("Manhattan",     40.700, 40.880, -74.020, -73.907),
]


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date/time"] = pd.to_datetime(df["date/time"])
    df["hour"] = df["date/time"].dt.hour
    df["day_name"] = df["date/time"].dt.day_name()
    df["day_num"] = df["date/time"].dt.dayofweek  # 0 = Monday
    df["is_weekend"] = df["day_num"] >= 5
    df["date"] = df["date/time"].dt.date
    df["borough"] = _assign_boroughs(df["lat"].to_numpy(), df["lon"].to_numpy())
    return df


def _assign_boroughs(lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    out = np.full(len(lats), "Other", dtype=object)
    for name, lat_min, lat_max, lon_min, lon_max in _BOROUGHS:
        mask = (
            (lats >= lat_min) & (lats <= lat_max) &
            (lons >= lon_min) & (lons <= lon_max)
        )
        out[mask] = name
    return out
