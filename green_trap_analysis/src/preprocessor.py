"""
Enhanced Preprocessor for Green Trap Analysis
Focus: Turkey-centric feature engineering with careful handling of missing data
"""
import pandas as pd
import numpy as np
from . import config
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_raw_data():
    """Load raw data with validation."""
    if not os.path.exists(config.RAW_DATA_PATH):
        raise FileNotFoundError(
            f"❌ Raw data not found at {config.RAW_DATA_PATH}\n"
            f"   Run 'python -m src.data_loader' first!"
        )

    logger.info(f"📂 Loading raw data from: {config.RAW_DATA_PATH}")
    df = pd.read_csv(config.RAW_DATA_PATH)
    logger.info(f"   Shape: {df.shape}")
    return df


def smart_imputation(df):
    """
    Intelligent missing data handling:
    - NO interpolation for volatile variables (inflation, growth)
    - Forward-fill for structural variables
    - Keep NaN where appropriate
    """
    logger.info("\n🔧 SMART IMPUTATION")
    logger.info("=" * 60)

    df = df.sort_values(['Country_Code', 'Year']).copy()

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Track missing before/after
    missing_before = df[numeric_cols].isna().sum().sum()
    logger.info(f"Missing values before imputation: {missing_before:,}")

    # 1. FORWARD-FILL for slow-moving structural variables
    logger.info("\n1️⃣ Forward-filling structural variables...")
    ff_vars = [v for v in config.FORWARD_FILL_OK if v in df.columns]
    logger.info(f"   Variables: {len(ff_vars)}")

    for var in ff_vars:
        df[var] = df.groupby('Country_Code')[var].ffill(limit=3)

    # 2. NO IMPUTATION for volatile variables (preserve NaN)
    logger.info("\n2️⃣ Preserving NaN for volatile variables...")
    no_imp_vars = [v for v in config.NO_INTERPOLATE if v in df.columns]
    logger.info(f"   Variables: {len(no_imp_vars)}")
    logger.info("   (These will remain NaN if missing - no artificial values)")

    # 3. INTERPOLATION for energy/emissions (gradual changes)
    logger.info("\n3️⃣ Interpolating energy/emissions variables...")
    interpolate_vars = [
        v for v in numeric_cols
        if v not in config.NO_INTERPOLATE
           and v not in config.FORWARD_FILL_OK
           and v not in ['Country_Code', 'Year']
    ]
    logger.info(f"   Variables: {len(interpolate_vars)}")

    for var in interpolate_vars:
        if var in df.columns:
            df[var] = df.groupby('Country_Code')[var].transform(
                lambda x: x.interpolate(method='linear', limit=2, limit_area='inside')
            )

    # 4. Backward fill for edge cases (start of series)
    logger.info("\n4️⃣ Backward filling edge cases...")
    df[ff_vars + interpolate_vars] = df.groupby('Country_Code')[ff_vars + interpolate_vars].bfill(limit=1)

    missing_after = df[numeric_cols].isna().sum().sum()
    logger.info(f"\n✅ Missing values after imputation: {missing_after:,}")
    logger.info(
        f"   Reduced by: {missing_before - missing_after:,} ({(1 - missing_after / missing_before) * 100:.1f}%)")

    # 5. CRITICAL: Drop rows where outcome variables are missing
    outcome_vars = ['Inflation_CPI_Pct', 'GDP_Growth_Pct']
    existing_outcomes = [v for v in outcome_vars if v in df.columns]

    if existing_outcomes:
        rows_before = len(df)
        df = df.dropna(subset=existing_outcomes, how='any')
        rows_dropped = rows_before - len(df)
        logger.info(f"\n⚠️ Dropped {rows_dropped} rows with missing outcome variables")
        logger.info(f"   Remaining: {len(df)} observations")

    return df


def create_derived_features(df):
    """
    Feature engineering focused on green transition dynamics.
    """
    logger.info("\n🔨 FEATURE ENGINEERING")
    logger.info("=" * 60)

    # Sort for time-based operations
    df = df.sort_values(['Country_Code', 'Year']).copy()

    # ========================================================================
    # 1. GREEN TRANSITION DYNAMICS
    # ========================================================================
    logger.info("\n1️⃣ Green transition dynamics...")

    # Transition speed (year-over-year change in renewable share)
    if 'Renewable_Energy_Consumption_Pct' in df.columns:
        df['Green_Transition_Speed'] = df.groupby('Country_Code')['Renewable_Energy_Consumption_Pct'].diff()
        logger.info("   ✅ Green_Transition_Speed")

    # Modern renewables growth (excluding hydro - key for "new" transition)
    if 'Renewable_Electricity_NoHydro_Pct' in df.columns:
        df['Modern_Renewables_Growth'] = df.groupby('Country_Code')['Renewable_Electricity_NoHydro_Pct'].diff()
        logger.info("   ✅ Modern_Renewables_Growth")

    # Fossil fuel reduction rate
    if 'Fossil_Fuel_Consumption_Pct' in df.columns:
        df['Fossil_Reduction_Rate'] = df.groupby('Country_Code')['Fossil_Fuel_Consumption_Pct'].diff()
        logger.info("   ✅ Fossil_Reduction_Rate")

    # ========================================================================
    # 2. ENERGY VULNERABILITY (CRITICAL for Turkey)
    # ========================================================================
    logger.info("\n2️⃣ Energy vulnerability indicators...")

    # Energy import dependence × energy intensity = vulnerability
    if 'Energy_Imports_Net_Pct' in df.columns and 'Energy_Intensity_Primary_MJ_Per_GDP' in df.columns:
        df['Energy_Vulnerability_Index'] = (
                df['Energy_Imports_Net_Pct'] * df['Energy_Intensity_Primary_MJ_Per_GDP'] / 100
        )
        logger.info("   ✅ Energy_Vulnerability_Index")

    # Fuel import exposure (share of trade)
    if 'Fuel_Imports_Pct_Merchandise' in df.columns and 'Trade_Pct_GDP' in df.columns:
        df['Fuel_Import_Exposure'] = (
                df['Fuel_Imports_Pct_Merchandise'] * df['Trade_Pct_GDP'] / 100
        )
        logger.info("   ✅ Fuel_Import_Exposure")

    # Energy importer dummy (Turkey is a major importer!)
    df['Is_Energy_Importer'] = df['Country_Code'].isin(config.ENERGY_IMPORTERS).astype(int)
    logger.info("   ✅ Is_Energy_Importer")

    # ========================================================================
    # 3. MACROECONOMIC INDICATORS
    # ========================================================================
    logger.info("\n3️⃣ Macroeconomic indicators...")

    # Log transformations (for skewed distributions)
    if 'GDP_Per_Capita_PPP' in df.columns:
        df['Log_GDP_Per_Capita'] = np.log1p(df['GDP_Per_Capita_PPP'])
        logger.info("   ✅ Log_GDP_Per_Capita")

    # Inflation volatility (rolling std over 3 years)
    if 'Inflation_CPI_Pct' in df.columns:
        df['Inflation_Volatility_3Y'] = (
            df.groupby('Country_Code')['Inflation_CPI_Pct']
            .transform(lambda x: x.rolling(3, min_periods=2).std())
        )
        logger.info("   ✅ Inflation_Volatility_3Y")

    # GDP growth volatility
    if 'GDP_Growth_Pct' in df.columns:
        df['GDP_Growth_Volatility_3Y'] = (
            df.groupby('Country_Code')['GDP_Growth_Pct']
            .transform(lambda x: x.rolling(3, min_periods=2).std())
        )
        logger.info("   ✅ GDP_Growth_Volatility_3Y")

    # Real exchange rate change (competitiveness shock)
    if 'Real_Effective_Exchange_Rate_Index' in df.columns:
        df['REER_Change'] = df.groupby('Country_Code')['Real_Effective_Exchange_Rate_Index'].diff()
        logger.info("   ✅ REER_Change")

    # Current account pressure (deficit/surplus relative to GDP)
    if 'Current_Account_Balance_Pct_GDP' in df.columns:
        df['CA_Deficit_Dummy'] = (df['Current_Account_Balance_Pct_GDP'] < -3).astype(int)
        logger.info("   ✅ CA_Deficit_Dummy (>3% deficit)")

    # ========================================================================
    # 4. LAGGED VARIABLES (for temporal dynamics)
    # ========================================================================
    logger.info("\n4️⃣ Creating lagged variables...")

    lag_vars = [
        'Renewable_Energy_Consumption_Pct',
        'Energy_Imports_Net_Pct',
        'Broad_Money_Growth_Pct',
        'Green_Transition_Speed'
    ]

    for var in lag_vars:
        if var in df.columns:
            df[f'{var}_Lag1'] = df.groupby('Country_Code')[var].shift(1)
            df[f'{var}_Lag2'] = df.groupby('Country_Code')[var].shift(2)
            logger.info(f"   ✅ {var}_Lag1, _Lag2")

    # ========================================================================
    # 5. CARBON EFFICIENCY
    # ========================================================================
    logger.info("\n5️⃣ Carbon efficiency metrics...")

    # Distance from carbon efficiency frontier (within each year)
    if 'Carbon_Intensity_CO2_Per_GDP' in df.columns:
        df['Carbon_Efficiency_Frontier'] = df.groupby('Year')['Carbon_Intensity_CO2_Per_GDP'].transform('min')
        df['Carbon_Efficiency_Gap'] = df['Carbon_Intensity_CO2_Per_GDP'] / df['Carbon_Efficiency_Frontier']
        logger.info("   ✅ Carbon_Efficiency_Gap")

    # Emissions reduction rate
    if 'CO2_Emissions_Per_Capita_Tons' in df.columns:
        df['Emissions_Reduction_Rate'] = df.groupby('Country_Code')['CO2_Emissions_Per_Capita_Tons'].pct_change()
        logger.info("   ✅ Emissions_Reduction_Rate")

    # ========================================================================
    # 6. PERIOD INDICATORS (for crisis analysis)
    # ========================================================================
    logger.info("\n6️⃣ Creating period indicators...")

    df['Period'] = pd.cut(
        df['Year'],
        bins=[1999, 2007, 2009, 2019, 2021, 2024],
        labels=['Pre_Crisis', 'Financial_Crisis', 'Recovery_Green', 'Pandemic', 'Energy_Crisis']
    )
    logger.info("   ✅ Period (5 crisis/transition periods)")

    # Post-2020 dummy (energy crisis + high inflation era)
    df['Post_2020'] = (df['Year'] >= 2020).astype(int)
    logger.info("   ✅ Post_2020")

    # ========================================================================
    # 7. COUNTRY GROUP INDICATORS
    # ========================================================================
    logger.info("\n7️⃣ Adding country classifications...")

    df['Country_Group'] = df['Country_Code'].map(config.COUNTRY_GROUPS)
    df['Is_Turkey'] = (df['Country_Code'] == 'TUR').astype(int)
    df['Is_Green_Leader'] = df['Country_Code'].isin(config.GREEN_LEADERS).astype(int)
    df['Is_Turkey_Peer'] = df['Country_Code'].isin(config.TURKEY_PEERS_EMERGING).astype(int)

    logger.info("   ✅ Country_Group, Is_Turkey, Is_Green_Leader, Is_Turkey_Peer")

    # ========================================================================
    # 8. INTERACTION TERMS (for heterogeneity analysis)
    # ========================================================================
    logger.info("\n8️⃣ Creating interaction terms...")

    # Green transition × Energy importer (key hypothesis!)
    if 'Renewable_Energy_Consumption_Pct' in df.columns:
        df['Green_X_Importer'] = (
                df['Renewable_Energy_Consumption_Pct'] * df['Is_Energy_Importer']
        )
        logger.info("   ✅ Green_X_Importer")

    # Green transition × Development level
    if 'Renewable_Energy_Consumption_Pct' in df.columns and 'Log_GDP_Per_Capita' in df.columns:
        df['Green_X_Development'] = (
                df['Renewable_Energy_Consumption_Pct'] * df['Log_GDP_Per_Capita']
        )
        logger.info("   ✅ Green_X_Development")

    # Green transition × Post-2020
    if 'Renewable_Energy_Consumption_Pct' in df.columns:
        df['Green_X_Post2020'] = (
                df['Renewable_Energy_Consumption_Pct'] * df['Post_2020']
        )
        logger.info("   ✅ Green_X_Post2020")

    logger.info(f"\n✅ Feature engineering complete. New shape: {df.shape}")
    return df


def create_turkey_comparison_dataset(df):
    """
    Create a focused dataset for Turkey vs. peer comparisons.
    """
    logger.info("\n🇹🇷 CREATING TURKEY COMPARISON DATASET")
    logger.info("=" * 60)

    # Select Turkey + comparison countries
    comparison_countries = (
            ['TUR'] +
            config.TURKEY_PEER_COMPARISON_COUNTRIES +
            config.TURKEY_ADVANCED_COMPARISON
    )

    df_comparison = df[df['Country_Code'].isin(comparison_countries)].copy()

    logger.info(f"Countries included: {comparison_countries}")
    logger.info(f"Observations: {len(df_comparison)}")
    logger.info(f"Years: {df_comparison['Year'].min()} - {df_comparison['Year'].max()}")

    # Add comparison flags
    df_comparison['Comparison_Type'] = df_comparison['Country_Code'].map({
        'TUR': 'Turkey',
        **{c: 'Peer' for c in config.TURKEY_PEER_COMPARISON_COUNTRIES},
        **{c: 'Advanced' for c in config.TURKEY_ADVANCED_COMPARISON}
    })

    # Save
    os.makedirs(os.path.dirname(config.TURKEY_COMPARISON_PATH), exist_ok=True)
    df_comparison.to_csv(config.TURKEY_COMPARISON_PATH, index=False)
    logger.info(f"✅ Turkey comparison data saved to: {config.TURKEY_COMPARISON_PATH}")

    return df_comparison


def final_cleaning(df):
    """
    Final data cleaning before analysis.
    """
    logger.info("\n🧹 FINAL CLEANING")
    logger.info("=" * 60)

    rows_before = len(df)

    # Remove rows where ALL green variables are missing
    green_vars_in_df = [v for v in config.GREEN_VARS if v in df.columns]
    if green_vars_in_df:
        df = df.dropna(subset=green_vars_in_df, how='all')
        logger.info(f"Dropped {rows_before - len(df)} rows with no green data")

    # Remove extreme outliers (likely data errors)
    rows_before = len(df)
    if 'Inflation_CPI_Pct' in df.columns:
        # Keep hyperinflation cases but remove obvious errors (>500%)
        df = df[df['Inflation_CPI_Pct'].abs() < 500]

    if 'GDP_Growth_Pct' in df.columns:
        # Remove impossible GDP growth (>50% or <-50%)
        df = df[df['GDP_Growth_Pct'].between(-50, 50)]

    logger.info(f"Removed {rows_before - len(df)} extreme outliers")
    logger.info(f"Final dataset: {len(df)} observations")

    return df


def main():
    """
    Main preprocessing pipeline.
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 GREEN TRAP ANALYSIS - PREPROCESSING")
    logger.info("=" * 70)

    # 1. Load
    df = load_raw_data()

    # 2. Smart imputation
    df = smart_imputation(df)

    # 3. Feature engineering
    df = create_derived_features(df)

    # 4. Final cleaning
    df = final_cleaning(df)

    # 5. Create Turkey comparison dataset
    df_turkey = create_turkey_comparison_dataset(df)

    # 6. Save full processed dataset
    os.makedirs(os.path.dirname(config.PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(config.PROCESSED_DATA_PATH, index=False)
    logger.info(f"\n💾 Full processed data saved to: {config.PROCESSED_DATA_PATH}")

    # 7. Summary statistics
    logger.info("\n" + "=" * 70)
    logger.info("📊 PREPROCESSING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Final dataset shape: {df.shape}")
    logger.info(f"Countries: {df['Country_Code'].nunique()}")
    logger.info(f"Years: {df['Year'].min()} - {df['Year'].max()}")
    logger.info(f"Turkey observations: {len(df[df['Country_Code'] == 'TUR'])}")

    # Key variables summary for Turkey
    if 'TUR' in df['Country_Code'].values:
        turkey_df = df[df['Country_Code'] == 'TUR']
        logger.info("\n🇹🇷 Turkey Key Variables (mean over period):")
        key_vars = [
            'Inflation_CPI_Pct',
            'GDP_Growth_Pct',
            'Renewable_Energy_Consumption_Pct',
            'Energy_Imports_Net_Pct',
            'Current_Account_Balance_Pct_GDP'
        ]
        for var in key_vars:
            if var in turkey_df.columns:
                mean_val = turkey_df[var].mean()
                logger.info(f"   {var:40s}: {mean_val:8.2f}")

    logger.info("\n" + "=" * 70)
    logger.info("✅ PREPROCESSING COMPLETE")
    logger.info("=" * 70)
    logger.info("Next step: Open 'notebooks/analysis.ipynb' for clustering and modeling")

    return df


if __name__ == "__main__":
    main()