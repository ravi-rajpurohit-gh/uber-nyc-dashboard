import pandas as pd
import numpy as np

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def hourly_counts(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("hour").size().reset_index(name="pickups")


def borough_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("borough").size()
        .reset_index(name="pickups")
        .sort_values("pickups", ascending=False)
    )


def day_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["day_name", "hour"]).size()
        .reset_index(name="pickups")
        .pivot(index="day_name", columns="hour", values="pickups")
        .reindex(DAYS_ORDER)
        .fillna(0)
        .astype(int)
    )


def weekend_vs_weekday(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["is_weekend", "hour"]).size()
        .reset_index(name="pickups")
        .assign(period=lambda x: x["is_weekend"].map({True: "Weekend", False: "Weekday"}))
        .drop(columns="is_weekend")
    )


def anomaly_hours(df: pd.DataFrame) -> pd.DataFrame:
    hc = hourly_counts(df)
    mean, std = hc["pickups"].mean(), hc["pickups"].std()
    hc["z_score"] = ((hc["pickups"] - mean) / std).round(2)
    hc["anomaly"] = hc["z_score"].abs() > 1.8
    return hc


def peak_hour(df: pd.DataFrame) -> int:
    return int(df["hour"].value_counts().idxmax())


def peak_borough(df: pd.DataFrame) -> str:
    bc = borough_counts(df)
    top = bc[bc["borough"] != "Other"]
    return str(top.iloc[0]["borough"]) if not top.empty else "N/A"
