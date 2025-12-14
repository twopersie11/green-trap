import pandas as pd
import wbgapi as wb
from . import config
import os


def fetch_data():
    """Fetches WDI data and reshapes it to [Country, Year, Var1, Var2...] format."""
    print("Initializing WDI Fetch...")

    # 1. Get definitions
    indicators_map = config.WDI_VARIABLES  # Code -> Name
    indicator_codes = list(indicators_map.keys())

    print(f"Fetching {len(indicator_codes)} indicators for {len(config.ALL_COUNTRIES)} countries...")

    try:
        # 2. Fetch data (Returns Wide Format: Index=[economy, series], Cols=[2000, 2001...])
        raw_df = wb.data.DataFrame(
            indicator_codes,
            economy=config.ALL_COUNTRIES,
            time=range(config.START_YEAR, config.END_YEAR + 1),
            numericTimeKeys=True,  # Returns years as integers (2000) not strings ('YR2000')
            labels=False
        )

        # 3. Reshape: Wide -> Long
        # Reset index to get 'economy' and 'series' as columns
        df = raw_df.reset_index()

        # Identify year columns (they are integers)
        year_cols = [c for c in df.columns if isinstance(c, int)]

        # MELT: Turn year columns into rows
        # Result: [economy, series, Year, Value]
        df_melted = df.melt(
            id_vars=['economy', 'series'],
            value_vars=year_cols,
            var_name='Year',
            value_name='Value'
        )

        # 4. Reshape: Series -> Columns
        # We want one column per indicator (e.g., GDP, Inflation)
        # Result: Index=[economy, Year], Columns=[NY.GDP..., FP.CPI...]
        df_pivoted = df_melted.pivot(index=['economy', 'Year'], columns='series', values='Value')

        # 5. Clean Up
        df_final = df_pivoted.reset_index()

        # Rename columns using config mapping
        rename_dict = {'economy': 'Country_Code'}
        rename_dict.update(indicators_map)  # Map codes to friendly names

        df_final = df_final.rename(columns=rename_dict)

        # Enforce column order (optional but nice)
        cols = ['Country_Code', 'Year'] + [c for c in df_final.columns if c not in ['Country_Code', 'Year']]
        df_final = df_final[cols]

        print(f"Data fetched and reshaped successfully. Shape: {df_final.shape}")
        return df_final

    except Exception as e:
        print(f"Error fetching/processing data: {e}")
        # Debug info
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_data()
    if not df.empty:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config.RAW_DATA_PATH), exist_ok=True)
        df.to_csv(config.RAW_DATA_PATH, index=False)
        print(f"Saved to {config.RAW_DATA_PATH}")
    else:
        print("Failed to fetch data.")