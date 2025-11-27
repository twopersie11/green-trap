"""Configuration for the Green Trap analysis project."""

from __future__ import annotations

# Economies to analyze (ISO-2 or ISO-3 codes accepted by WDI)
ECONOMIES: list[str] = [
    "USA",
    "CHN",
    "IND",
    "DEU",
    "BRA",
]

# Indicator codes from the World Development Indicators (WDI) catalog
# Update this list to match the metrics you plan to model.
INDICATORS: dict[str, str] = {
    "NY.GDP.PCAP.KD": "GDP per capita (constant 2015 US$)",
    "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)",
    "EG.USE.PCAP.KG.OE": "Energy use (kg of oil equivalent per capita)",
    "SP.POP.TOTL": "Population, total",
}

# Time range for the data pull
START_YEAR: int = 2000
END_YEAR: int = 2022

# Default file locations
RAW_DATA_PATH: str = "data/raw/wdi_data.csv"
DATA_SUMMARY_PATH: str = "data/raw/data_summary.csv"
FEATURES_PATH: str = "data/processed/features.csv"
FEATURE_SUMMARY_PATH: str = "data/processed/feature_summary.csv"
