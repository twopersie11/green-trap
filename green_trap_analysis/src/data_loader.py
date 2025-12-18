"""
Enhanced Data Loader for Green Trap Analysis
Features:
- Chunked fetching to avoid timeouts
- Caching to avoid redundant API calls
- Comprehensive validation
- Turkey-specific checks
"""
import pandas as pd
import numpy as np
import wbgapi as wb
from . import config
import os
import pickle
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_data_chunked(chunk_years=5, use_cache=True):
    """
    Fetches WDI data in chunks to avoid API timeouts.

    Args:
        chunk_years: Number of years to fetch per API call
        use_cache: If True, load from cache if available

    Returns:
        pd.DataFrame: Wide format [Country, Year, Var1, Var2...]
    """

    # Check cache first
    if use_cache and os.path.exists(config.CACHE_PATH):
        cache_age_hours = (datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(config.CACHE_PATH)
        )).total_seconds() / 3600

        if cache_age_hours < 24:  # Cache valid for 24 hours
            logger.info(f"📦 Loading from cache (age: {cache_age_hours:.1f} hours)")
            with open(config.CACHE_PATH, 'rb') as f:
                return pickle.load(f)
        else:
            logger.info("⏰ Cache expired, fetching new data...")

    # Prepare fetch
    indicator_codes = list(config.WDI_VARIABLES.keys())
    countries = config.ALL_COUNTRIES

    logger.info("=" * 60)
    logger.info("🌍 GREEN TRAP ANALYSIS - DATA FETCH")
    logger.info("=" * 60)
    logger.info(f"📊 Indicators: {len(indicator_codes)}")
    logger.info(f"🌐 Countries: {len(countries)}")
    logger.info(f"📅 Period: {config.START_YEAR} - {config.END_YEAR}")
    logger.info(f"🇹🇷 Turkey included: {'TUR' in countries}")
    logger.info("=" * 60)

    # Fetch in chunks
    all_chunks = []
    years = list(range(config.START_YEAR, config.END_YEAR + 1))

    for i in range(0, len(years), chunk_years):
        chunk_start = years[i]
        chunk_end = min(years[i + chunk_years - 1], config.END_YEAR)

        logger.info(f"Fetching years {chunk_start}-{chunk_end}...")

        try:
            chunk_df = wb.data.DataFrame(
                indicator_codes,
                economy=countries,
                time=range(chunk_start, chunk_end + 1),
                numericTimeKeys=True,
                labels=False
            )

            if not chunk_df.empty:
                all_chunks.append(chunk_df)
                logger.info(f"  ✅ Success: {chunk_df.shape[0]} observations")
            else:
                logger.warning(f"  ⚠️ Empty response for {chunk_start}-{chunk_end}")

        except Exception as e:
            logger.error(f"  ❌ Failed for {chunk_start}-{chunk_end}: {e}")
            continue

    if not all_chunks:
        logger.error("💥 CRITICAL: No data fetched from any chunk!")
        return pd.DataFrame()

    # Combine chunks
    logger.info("\n🔄 Combining chunks...")
    raw_df = pd.concat(all_chunks, axis=0)

    # Reshape: Wide -> Long -> Wide (to clean format)
    logger.info("🔄 Reshaping data...")
    df = raw_df.reset_index()

    # Identify year columns
    year_cols = [c for c in df.columns if isinstance(c, int)]

    # Melt
    df_melted = df.melt(
        id_vars=['economy', 'series'],
        value_vars=year_cols,
        var_name='Year',
        value_name='Value'
    )

    # Pivot
    df_pivoted = df_melted.pivot(
        index=['economy', 'Year'],
        columns='series',
        values='Value'
    )

    # Clean up
    df_final = df_pivoted.reset_index()
    rename_dict = {'economy': 'Country_Code'}
    rename_dict.update(config.WDI_VARIABLES)

    df_final = df_final.rename(columns=rename_dict)

    # Validate
    logger.info("\n🔍 Validating data...")
    validation_passed = validate_data(df_final)

    if not validation_passed:
        logger.warning("⚠️ Data validation found issues (see above)")

    # Cache the result
    logger.info(f"\n💾 Caching data to {config.CACHE_PATH}")
    os.makedirs(os.path.dirname(config.CACHE_PATH), exist_ok=True)
    with open(config.CACHE_PATH, 'wb') as f:
        pickle.dump(df_final, f)

    logger.info(f"\n✅ Data fetch complete: {df_final.shape}")
    logger.info(f"   Countries: {df_final['Country_Code'].nunique()}")
    logger.info(f"   Years: {df_final['Year'].min()} - {df_final['Year'].max()}")

    return df_final


def validate_data(df):
    """
    Comprehensive data quality checks.

    Returns:
        bool: True if all checks pass
    """
    issues = []

    # 1. Check Turkey is present
    if 'TUR' not in df['Country_Code'].values:
        issues.append("🚨 CRITICAL: Turkey (TUR) not found in data!")
    else:
        turkey_years = df[df['Country_Code'] == 'TUR']['Year'].nunique()
        logger.info(f"   🇹🇷 Turkey: {turkey_years} years of data")
        if turkey_years < config.MIN_OBSERVATIONS_PER_COUNTRY:
            issues.append(f"⚠️ Turkey has only {turkey_years} years (min: {config.MIN_OBSERVATIONS_PER_COUNTRY})")

    # 2. Check all target countries
    missing_countries = set(config.ALL_COUNTRIES) - set(df['Country_Code'].unique())
    if missing_countries:
        issues.append(f"⚠️ Missing countries: {missing_countries}")

    # 3. Check year range
    year_min, year_max = df['Year'].min(), df['Year'].max()
    if year_min > config.START_YEAR or year_max < config.END_YEAR:
        issues.append(f"⚠️ Year range {year_min}-{year_max} doesn't match config {config.START_YEAR}-{config.END_YEAR}")

    # 4. Check for duplicate rows
    dupes = df.duplicated(subset=['Country_Code', 'Year'])
    if dupes.any():
        issues.append(f"❌ CRITICAL: {dupes.sum()} duplicate country-year rows!")

    # 5. Check outcome variables exist and have data
    outcome_vars = ['Inflation_CPI_Pct', 'GDP_Growth_Pct']
    for var in outcome_vars:
        if var not in df.columns:
            issues.append(f"❌ CRITICAL: Outcome variable '{var}' not found!")
        else:
            missing_pct = df[var].isna().sum() / len(df) * 100
            logger.info(f"   {var}: {missing_pct:.1f}% missing")
            if missing_pct > config.MAX_MISSING_PCT_PER_VARIABLE * 100:
                issues.append(
                    f"⚠️ {var} missing {missing_pct:.1f}% (threshold: {config.MAX_MISSING_PCT_PER_VARIABLE * 100}%)")

    # 6. Check for inflation outliers (potential data errors)
    if 'Inflation_CPI_Pct' in df.columns:
        outliers = df[df['Inflation_CPI_Pct'].abs() > config.OUTLIER_THRESHOLD_INFLATION]
        if not outliers.empty:
            logger.warning(f"   ⚠️ {len(outliers)} inflation outliers (>100%):")
            for _, row in outliers.head(5).iterrows():
                logger.warning(f"      {row['Country_Code']} {row['Year']}: {row['Inflation_CPI_Pct']:.1f}%")

    # 7. Check for GDP growth outliers
    if 'GDP_Growth_Pct' in df.columns:
        outliers = df[df['GDP_Growth_Pct'].abs() > config.OUTLIER_THRESHOLD_GDP_GROWTH]
        if not outliers.empty:
            logger.warning(f"   ⚠️ {len(outliers)} GDP growth outliers (>|20%|):")
            for _, row in outliers.head(5).iterrows():
                logger.warning(f"      {row['Country_Code']} {row['Year']}: {row['GDP_Growth_Pct']:.1f}%")

    # 8. Check green variables coverage
    green_vars_in_df = [v for v in config.GREEN_VARS if v in df.columns]
    logger.info(f"   Green variables: {len(green_vars_in_df)}/{len(config.GREEN_VARS)} present")

    # Report issues
    if issues:
        logger.warning("\n⚠️ DATA QUALITY ISSUES:")
        for issue in issues:
            logger.warning(f"   {issue}")
        return False
    else:
        logger.info("   ✅ All validation checks passed!")
        return True


def generate_data_quality_report(df):
    """
    Creates a detailed data quality report.
    """
    report = []
    report.append("=" * 70)
    report.append("DATA QUALITY REPORT - GREEN TRAP ANALYSIS")
    report.append("=" * 70)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nDataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
    report.append(f"Countries: {df['Country_Code'].nunique()}")
    report.append(f"Years: {df['Year'].min()} - {df['Year'].max()}")

    # Turkey-specific section
    report.append("\n" + "=" * 70)
    report.append("🇹🇷 TURKEY DATA QUALITY")
    report.append("=" * 70)
    turkey_df = df[df['Country_Code'] == 'TUR']
    if not turkey_df.empty:
        report.append(f"Observations: {len(turkey_df)}")
        report.append(f"Year range: {turkey_df['Year'].min()} - {turkey_df['Year'].max()}")

        # Key variables for Turkey
        key_vars = ['Inflation_CPI_Pct', 'GDP_Growth_Pct', 'Renewable_Energy_Consumption_Pct',
                    'Energy_Imports_Net_Pct', 'Current_Account_Balance_Pct_GDP']
        report.append("\nKey variables (% non-missing):")
        for var in key_vars:
            if var in turkey_df.columns:
                non_missing = (1 - turkey_df[var].isna().sum() / len(turkey_df)) * 100
                report.append(f"  {var:45s}: {non_missing:5.1f}%")
    else:
        report.append("❌ NO TURKEY DATA FOUND!")

    # Overall missingness
    report.append("\n" + "=" * 70)
    report.append("MISSING DATA SUMMARY (All countries)")
    report.append("=" * 70)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    missing_summary = df[numeric_cols].isna().sum().sort_values(ascending=False)
    missing_pct = (missing_summary / len(df) * 100).round(1)

    report.append("\nTop 20 variables with missing data:")
    for var, pct in missing_pct.head(20).items():
        count = missing_summary[var]
        report.append(f"  {var:45s}: {pct:5.1f}% ({count:6d} obs)")

    # Country coverage
    report.append("\n" + "=" * 70)
    report.append("COUNTRY COVERAGE")
    report.append("=" * 70)
    country_obs = df.groupby('Country_Code').size().sort_values(ascending=False)
    report.append(f"\nObservations per country (top 15):")
    for country, obs in country_obs.head(15).items():
        group = config.COUNTRY_GROUPS.get(country, 'Unknown')
        report.append(f"  {country} ({group:20s}): {obs:3d} years")

    # Save report
    report_text = "\n".join(report)
    os.makedirs(os.path.dirname(config.DATA_QUALITY_REPORT_PATH), exist_ok=True)
    with open(config.DATA_QUALITY_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_text)

    logger.info(f"\n📋 Data quality report saved to: {config.DATA_QUALITY_REPORT_PATH}")

    return report_text


if __name__ == "__main__":
    logger.info("🚀 Starting data fetch...")

    # Fetch data
    df = fetch_data_chunked(chunk_years=5, use_cache=True)

    if df.empty:
        logger.error("💥 Data fetch failed. Exiting.")
        exit(1)

    # Generate quality report
    generate_data_quality_report(df)

    # Save raw data
    os.makedirs(os.path.dirname(config.RAW_DATA_PATH), exist_ok=True)
    df.to_csv(config.RAW_DATA_PATH, index=False)
    logger.info(f"✅ Raw data saved to: {config.RAW_DATA_PATH}")

    logger.info("\n" + "=" * 70)
    logger.info("✅ DATA FETCH COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Next step: Run 'python -m src.preprocessor' to engineer features")