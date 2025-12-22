"""
Robust Data Loader with Retry Logic for Green Trap Analysis
"""
import pandas as pd
import numpy as np
import wbgapi as wb
from . import config
import os
import pickle
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_with_retry(indicator_codes, countries, years, max_retries=3, delay=10):
    """
    Fetch data with exponential backoff retry logic.

    Args:
        indicator_codes: List of WDI indicator codes
        countries: List of country codes
        years: Range of years
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)

    Returns:
        pd.DataFrame or None
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"   Attempt {attempt + 1}/{max_retries}...")

            df = wb.data.DataFrame(
                indicator_codes,
                economy=countries,
                time=years,
                numericTimeKeys=True,
                labels=False
            )

            if not df.empty:
                logger.info(f"   ✅ Success on attempt {attempt + 1}")
                return df
            else:
                logger.warning(f"   ⚠️ Empty response on attempt {attempt + 1}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"   ❌ Attempt {attempt + 1} failed: {error_msg[:100]}")

            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logger.info(f"   ⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"   💥 All {max_retries} attempts failed")
                return None

    return None


def fetch_data_chunked(chunk_years=5, use_cache=True, max_retries=3):
    """
    Fetches WDI data in chunks with retry logic.
    """
    # Check cache first
    if use_cache and os.path.exists(config.CACHE_PATH):
        try:
            cache_mtime = os.path.getmtime(config.CACHE_PATH)
            cache_age_hours = (datetime.now() - datetime.fromtimestamp(cache_mtime)).total_seconds() / 3600

            if cache_age_hours < 24:
                logger.info(f"📦 Loading from cache (age: {cache_age_hours:.1f} hours)")
                with open(config.CACHE_PATH, 'rb') as f:
                    return pickle.load(f)
            else:
                logger.info("⏰ Cache expired, fetching new data...")
        except Exception as e:
            logger.warning(f"⚠️ Could not read cache: {e}. Fetching fresh data.")

    # Prepare fetch
    indicator_codes = list(config.WDI_VARIABLES.keys())
    countries = config.ALL_COUNTRIES

    logger.info("=" * 60)
    logger.info("🌍 GREEN TRAP ANALYSIS - DATA FETCH (ROBUST)")
    logger.info("=" * 60)
    logger.info(f"📊 Indicators: {len(indicator_codes)}")
    logger.info(f"🌐 Countries: {len(countries)}")
    logger.info(f"📅 Period: {config.START_YEAR} - {config.END_YEAR}")
    logger.info(f"🔁 Max retries per chunk: {max_retries}")
    logger.info("=" * 60)

    # Fetch in chunks
    all_chunks = []
    years = list(range(config.START_YEAR, config.END_YEAR + 1))

    for i in range(0, len(years), chunk_years):
        chunk_start = years[i]
        end_idx = min(i + chunk_years - 1, len(years) - 1)
        chunk_end = years[end_idx]

        logger.info(f"\n📥 Fetching years {chunk_start}-{chunk_end}...")

        # Try to fetch with retries
        chunk_df = fetch_with_retry(
            indicator_codes,
            countries,
            range(chunk_start, chunk_end + 1),
            max_retries=max_retries
        )

        if chunk_df is not None and not chunk_df.empty:
            # Melt immediately
            chunk_df = chunk_df.reset_index()
            chunk_melted = chunk_df.melt(
                id_vars=['economy', 'series'],
                var_name='Year',
                value_name='Value'
            )
            chunk_melted['Year'] = pd.to_numeric(chunk_melted['Year'])
            all_chunks.append(chunk_melted)
            logger.info(f"  ✅ Chunk saved: {len(chunk_melted)} records")
        else:
            logger.error(f"  ❌ Chunk {chunk_start}-{chunk_end} completely failed")
            logger.info(f"  ℹ️ Continuing with other chunks...")

    if not all_chunks:
        logger.error("💥 CRITICAL: No data fetched from any chunk!")
        logger.error("   The World Bank API may be down.")
        logger.error("   Please try again later or use Solution 3 (manual download).")
        return pd.DataFrame()

    # Combine chunks
    logger.info("\n🔄 Combining chunks...")
    df_long = pd.concat(all_chunks, axis=0)

    # Pivot to wide format
    logger.info("🔄 Reshaping data...")
    df_pivoted = df_long.pivot(
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
    from .data_loader import validate_data, generate_data_quality_report
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

    # Generate quality report
    generate_data_quality_report(df_final)

    # Save raw data
    os.makedirs(os.path.dirname(config.RAW_DATA_PATH), exist_ok=True)
    df_final.to_csv(config.RAW_DATA_PATH, index=False)
    logger.info(f"✅ Raw data saved to: {config.RAW_DATA_PATH}")

    return df_final


if __name__ == "__main__":
    logger.info("🚀 Starting robust data fetch...")

    df = fetch_data_chunked(chunk_years=5, use_cache=True, max_retries=5)

    if df.empty:
        logger.error("💥 Data fetch failed. Exiting.")
        exit(1)

    logger.info("\n" + "=" * 70)
    logger.info("✅ DATA FETCH COMPLETE")
    logger.info("=" * 70)
    logger.info("Next step: Run 'python -m src.preprocessor' to engineer features")