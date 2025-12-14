import pandas as pd
import numpy as np
from . import config

def clean_and_feature_engineer():
    df = pd.read_csv(config.RAW_DATA_PATH)
    
    # 1. Sort for time-series operations
    df = df.sort_values(['Country_Code', 'Year'])
    
    # 2. Add Country Group metadata
    df['Region_Group'] = df['Country_Code'].map(config.COUNTRY_GROUPS)
    
    # 3. Missing Value Handling
    # Strategy: Linear Interpolation for gaps inside a series, 
    # then Backfill/Forwardfill for edges.
    numeric_cols = [c for c in df.columns if c not in ['Country_Code', 'Year', 'Region_Group']]
    
    print(f"Missing values before cleaning: {df[numeric_cols].isna().sum().sum()}")
    
    # Group by country to avoid interpolating between e.g., Turkey and USA
    df[numeric_cols] = df.groupby('Country_Code')[numeric_cols].transform(
        lambda group: group.interpolate(method='linear').bfill().ffill()
    )
    
    # 4. Feature Engineering
    
    # A. Log Transforms (for skewed variables)
    for col in ['GDP_Per_Capita', 'CO2_Emissions_Total', 'Energy_Use_Per_Capita']:
        if col in df.columns:
            df[f'Log_{col}'] = np.log1p(df[col])

    # B. Lagged Variables (t-1)
    # Important for "Granger causality" style logic: 
    # Does LAST year's green energy affect THIS year's inflation?
    lag_cols = ['Renewable_Energy_Consumption_Pct', 'Broad_Money_Pct_GDP', 'Energy_Intensity']
    for col in lag_cols:
        if col in df.columns:
            df[f'{col}_Lag1'] = df.groupby('Country_Code')[col].shift(1)
            
    # 5. Final Cleanup
    # Drop rows created by shifting (first year will be NaN for lags)
    df = df.dropna()
    
    print(f"Final shape: {df.shape}")
    
    # Save
    import os
    os.makedirs(os.path.dirname(config.PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(config.PROCESSED_DATA_PATH, index=False)
    print(f"Saved processed data to {config.PROCESSED_DATA_PATH}")
    return df

if __name__ == "__main__":
    clean_and_feature_engineer()