import pandas as pd
import wbgapi as wb
from . import config
import os


def fetch_data():
    """Fetches WDI data and reshapes it to [Country, Year, Var1, Var2...] format."""
    print("Initializing WDI Fetch...")

    # 1. Get definitions
    indicators_map = config.WDI_VARIABLES
    indicator_codes = list(indicators_map.keys())

    print(f"Fetching {len(indicator_codes)} indicators for {len(config.ALL_COUNTRIES)} countries...")
    print(f"Time period: {config.START_YEAR} - {config.END_YEAR}")

    try:
        # 2. Fetch data
        raw_df = wb.data.DataFrame(
            indicator_codes,
            economy=config.ALL_COUNTRIES,
            time=range(config.START_YEAR, config.END_YEAR + 1),
            numericTimeKeys=True,
            labels=False
        )

        if raw_df.empty:
            print("WARNING: WDI returned no data. Check your internet connection or VPN.")
            return pd.DataFrame()

        # 3. Reshape: Wide -> Long
        df = raw_df.reset_index()

        # Identify year columns
        year_cols = [c for c in df.columns if isinstance(c, int)]

        # MELT
        df_melted = df.melt(
            id_vars=['economy', 'series'],
            value_vars=year_cols,
            var_name='Year',
            value_name='Value'
        )

        # 4. Pivot
        df_pivoted = df_melted.pivot(index=['economy', 'Year'], columns='series', values='Value')

        # 5. Clean Up
        df_final = df_pivoted.reset_index()
        rename_dict = {'economy': 'Country_Code'}
        rename_dict.update(indicators_map)

        df_final = df_final.rename(columns=rename_dict)

        print(f"Data fetched successfully. Shape: {df_final.shape}")
        return df_final

    except Exception as e:
        print(f"CRITICAL ERROR in fetch_data: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_data()
    if not df.empty:
        os.makedirs(os.path.dirname(config.RAW_DATA_PATH), exist_ok=True)
        df.to_csv(config.RAW_DATA_PATH, index=False)
        print(f"SUCCESS: Raw data saved to {config.RAW_DATA_PATH}")
    else:
        print("FAILURE: No data fetched.")