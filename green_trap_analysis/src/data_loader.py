"""Tools for fetching World Development Indicators data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import wbgapi as wb

from . import config


def fetch_wdi_data(
    indicators: Iterable[str],
    economies: Iterable[str],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """Fetch WDI data for the given indicators, economies, and years."""

    df = wb.data.DataFrame(
        series=list(indicators),
        economy=list(economies),
        time=(start_year, end_year),
        labels=True,
        numericTimeKeys=True,
    )

    # Move the time index into a column for easier processing
    df = df.reset_index().rename(columns={"economy": "economy_code", "Time": "year"})
    return df


def summarize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a small data quality summary."""

    summary = {
        "rows": [len(df)],
        "economies": [df["economy_code"].nunique()],
        "years": [df["year"].nunique()],
        "indicators": [len([col for col in df.columns if col not in {"economy_code", "year", "economy"}])],
    }
    return pd.DataFrame(summary)


def save_outputs(raw_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    """Persist raw data and summary reports to disk."""

    raw_path = Path(config.RAW_DATA_PATH)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(raw_path, index=False)

    summary_path = Path(config.DATA_SUMMARY_PATH)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_path, index=False)


if __name__ == "__main__":
    data = fetch_wdi_data(
        indicators=config.INDICATORS.keys(),
        economies=config.ECONOMIES,
        start_year=config.START_YEAR,
        end_year=config.END_YEAR,
    )
    summary = summarize_data(data)
    save_outputs(data, summary)
    print(f"Saved raw data to {config.RAW_DATA_PATH} and summary to {config.DATA_SUMMARY_PATH}.")
