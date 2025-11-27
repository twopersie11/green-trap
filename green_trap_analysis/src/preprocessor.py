"""Lightweight feature engineering for WDI data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config


def load_raw_data(path: str | Path = config.RAW_DATA_PATH) -> pd.DataFrame:
    """Load raw WDI data from CSV."""

    return pd.read_csv(path)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create a basic feature set ready for modeling.

    - Forward-fills indicator values by economy and sorts by year.
    - Drops rows that remain entirely empty after filling.
    - Adds a simple growth-rate proxy for GDP per capita when available.
    """

    df = df.copy()
    df = df.sort_values(["economy_code", "year"])
    numeric_cols = [col for col in df.columns if col not in {"economy", "economy_code", "year"}]
    df[numeric_cols] = df.groupby("economy_code")[numeric_cols].ffill()

    # Example derived feature
    if "NY.GDP.PCAP.KD" in numeric_cols:
        df["gdp_per_capita_growth"] = df.groupby("economy_code")["NY.GDP.PCAP.KD"].pct_change()

    df = df.dropna(how="all", subset=numeric_cols)
    return df


def summarize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Produce simple summary statistics for the engineered features."""

    numeric_cols = [col for col in df.columns if df[col].dtype != object]
    summary = df[numeric_cols].describe().transpose().reset_index().rename(columns={"index": "feature"})
    return summary


def save_features(features: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Persist engineered features and their summary to disk."""

    features_path = Path(config.FEATURES_PATH)
    features_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(features_path, index=False)

    summary_path = Path(config.FEATURE_SUMMARY_PATH)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)


if __name__ == "__main__":
    raw_df = load_raw_data()
    features_df = engineer_features(raw_df)
    feature_summary_df = summarize_features(features_df)
    save_features(features_df, feature_summary_df)
    print(
        f"Saved engineered features to {config.FEATURES_PATH} and summary to {config.FEATURE_SUMMARY_PATH}."
    )
