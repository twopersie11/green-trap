"""
Enhanced Configuration for Green Trap Analysis
Focus: Turkey's green transition and inflation dynamics compared to peer countries
"""
import os

# ============================================================================
# 1. COUNTRY SELECTION STRATEGY
# ============================================================================
# Core focus: TURKEY + peer comparisons across multiple dimensions

# Turkey's peer group (emerging, energy-dependent, similar structure)
TURKEY_PEERS_EMERGING = ['TUR', 'POL', 'MEX', 'ZAF', 'THA']  # Similar development level

# Fast-growing comparisons (to test if growth masks green costs)
FAST_GROWING = ['CHN', 'IND', 'VNM', 'BGD', 'PHL']

# Advanced with strong green policies (to test "successful transition" cases)
GREEN_LEADERS = ['DEU', 'DNK', 'SWE', 'NLD', 'NOR']

# Energy-dependent economies (different strategies)
ENERGY_DEPENDENT = ['RUS', 'SAU', 'NOR', 'CAN', 'AUS']  # Exporters + importers

# Southern Europe (geographic/climate similarity to Turkey)
SOUTHERN_EUROPE = ['ITA', 'ESP', 'GRC', 'PRT']

# Asian emerging (regional comparison)
ASIAN_EMERGING = ['IDN', 'MYS', 'THA', 'PHL', 'VNM']

# Additional controls
OTHER_COUNTRIES = ['USA', 'JPN', 'GBR', 'FRA', 'BRA', 'KOR', 'CHL', 'NZL']

# Union of all (Turkey MUST be included)
ALL_COUNTRIES = sorted(list(set(
    TURKEY_PEERS_EMERGING + FAST_GROWING + GREEN_LEADERS +
    ENERGY_DEPENDENT + SOUTHERN_EUROPE + ASIAN_EMERGING + OTHER_COUNTRIES
)))

# Verify Turkey is included
assert 'TUR' in ALL_COUNTRIES, "Turkey must be in the analysis!"

# Map countries to analytical groups (for heterogeneity analysis)
COUNTRY_GROUPS = {}
for c in ALL_COUNTRIES:
    if c == 'TUR':
        COUNTRY_GROUPS[c] = 'Turkey_Focus'
    elif c in GREEN_LEADERS:
        COUNTRY_GROUPS[c] = 'Green_Leaders'
    elif c in FAST_GROWING:
        COUNTRY_GROUPS[c] = 'Fast_Growing'
    elif c in ENERGY_DEPENDENT:
        COUNTRY_GROUPS[c] = 'Energy_Dependent'
    elif c in TURKEY_PEERS_EMERGING:
        COUNTRY_GROUPS[c] = 'Turkey_Peers'
    elif c in SOUTHERN_EUROPE:
        COUNTRY_GROUPS[c] = 'Southern_Europe'
    elif c in ASIAN_EMERGING:
        COUNTRY_GROUPS[c] = 'Asian_Emerging'
    else:
        COUNTRY_GROUPS[c] = 'Other_Advanced'

# Energy importer/exporter classification (CRITICAL for Turkey analysis)
ENERGY_IMPORTERS = ['TUR', 'DEU', 'ITA', 'ESP', 'JPN', 'KOR', 'IND', 'CHN', 'GRC', 'PRT', 'THA', 'PHL']
ENERGY_EXPORTERS = ['RUS', 'SAU', 'NOR', 'CAN', 'AUS', 'MEX', 'IDN', 'MYS']

# ============================================================================
# 2. TIME PERIOD (with crisis markers)
# ============================================================================
START_YEAR = 2000
END_YEAR = 2023

# Key periods for Turkey and global economy
PERIOD_LABELS = {
    (2000, 2007): 'Pre_Crisis',
    (2008, 2009): 'Global_Financial_Crisis',
    (2010, 2019): 'Recovery_Green_Transition',
    (2020, 2021): 'Pandemic',
    (2022, 2023): 'Energy_Crisis_High_Inflation'
}

# ============================================================================
# 3. COMPREHENSIVE WDI VARIABLE MAPPINGS
# ============================================================================
WDI_VARIABLES = {
    # ========================================================================
    # OUTCOME VARIABLES (Target for models)
    # ========================================================================
    'FP.CPI.TOTL.ZG': 'Inflation_CPI_Pct',           # Main target
    'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Pct',           # Main target
    'NY.GDP.DEFL.KD.ZG': 'GDP_Deflator_Growth_Pct',  # Alternative inflation measure

    # ========================================================================
    # GREEN TRANSITION INDICATORS (Main explanatory variables)
    # ========================================================================
    'EG.FEC.RNEW.ZS': 'Renewable_Energy_Consumption_Pct',        # Total renewables
    'EG.ELC.RNEW.ZS': 'Renewable_Electricity_Output_Pct',        # Renewable power
    'EG.ELC.RNWX.ZS': 'Renewable_Electricity_NoHydro_Pct',       # Modern renewables (KEY!)
    'EG.USE.COMM.FO.ZS': 'Fossil_Fuel_Consumption_Pct',          # Fossil dependence
    'EG.USE.COMM.CL.ZS': 'Alternative_Nuclear_Energy_Pct',       # Nuclear + other

    # ========================================================================
    # ENERGY STRUCTURE & EFFICIENCY
    # ========================================================================
    'EG.USE.PCAP.KG.OE': 'Energy_Use_Per_Capita_KgOE',           # Consumption level
    'EG.USE.COMM.GD.PP.KD': 'Energy_Use_Per_GDP_PPP',            # Efficiency (KEY!)
    'EG.EGY.PRIM.PP.KD': 'Energy_Intensity_Primary_MJ_Per_GDP',  # Primary energy efficiency
    'EG.USE.ELEC.KH.PC': 'Electric_Power_Consumption_Per_Capita', # Electricity demand

    # ========================================================================
    # ENERGY DEPENDENCE & VULNERABILITY (CRITICAL for Turkey)
    # ========================================================================
    'EG.IMP.CONS.ZS': 'Energy_Imports_Net_Pct',                  # Import dependence
    'TM.VAL.FUEL.ZS.UN': 'Fuel_Imports_Pct_Merchandise',         # Trade exposure

    # ========================================================================
    # MACROECONOMIC FUNDAMENTALS
    # ========================================================================
    'NY.GDP.PCAP.PP.KD': 'GDP_Per_Capita_PPP',                   # Development level
    'NY.GDP.MKTP.PP.KD': 'GDP_Total_PPP',                        # Economy size
    'SP.POP.TOTL': 'Population_Total',                           # Scale

    # ========================================================================
    # MONETARY & FINANCIAL
    # ========================================================================
    'FM.LBL.BMNY.GD.ZS': 'Broad_Money_Pct_GDP',                  # Liquidity
    'FM.LBL.BMNY.ZG': 'Broad_Money_Growth_Pct',                  # Money supply growth (KEY!)
    'FD.AST.PRVT.GD.ZS': 'Domestic_Credit_Private_Pct_GDP',      # Financial depth
    'FR.INR.RINR': 'Real_Interest_Rate_Pct',                     # Monetary policy stance

    # ========================================================================
    # EXTERNAL SECTOR (CRITICAL for Turkey's inflation dynamics)
    # ========================================================================
    'NE.TRD.GNFS.ZS': 'Trade_Pct_GDP',                           # Openness
    'NE.EXP.GNFS.ZS': 'Exports_Pct_GDP',                         # Export performance
    'NE.IMP.GNFS.ZS': 'Imports_Pct_GDP',                         # Import dependence
    'BN.CAB.XOKA.GD.ZS': 'Current_Account_Balance_Pct_GDP',      # External balance
    'BX.KLT.DINV.WD.GD.ZS': 'FDI_Net_Inflows_Pct_GDP',          # Capital flows

    # ========================================================================
    # EXCHANGE RATE & COMPETITIVENESS (KEY for Turkey)
    # ========================================================================
    'PA.NUS.FCRF': 'Official_Exchange_Rate_LCU_Per_USD',         # Nominal rate
    'PX.REX.REER': 'Real_Effective_Exchange_Rate_Index',         # Competitiveness

    # ========================================================================
    # FISCAL POLICY
    # ========================================================================
    'NE.CON.GOVT.ZS': 'Gov_Expenditure_Pct_GDP',                 # Fiscal stance
    'GC.TAX.TOTL.GD.ZS': 'Tax_Revenue_Pct_GDP',                  # Fiscal capacity
    'GC.DOD.TOTL.GD.ZS': 'Central_Gov_Debt_Pct_GDP',             # Debt burden
    'NE.GDI.FTOT.ZS': 'Gross_Fixed_Capital_Formation_Pct_GDP',   # Investment

    # ========================================================================
    # CARBON INTENSITY & EMISSIONS (for green transition measurement)
    # ========================================================================
    'EN.ATM.CO2E.PP.GD.KD': 'Carbon_Intensity_CO2_Per_GDP',      # Efficiency
    'EN.ATM.CO2E.PC': 'CO2_Emissions_Per_Capita_Tons',           # Per capita
    'EN.ATM.CO2E.KT': 'CO2_Emissions_Total_Kt',                  # Total emissions
    'EN.ATM.GHGT.KT.CE': 'GHG_Emissions_Total_KtCO2e',           # Total GHG
    'EN.ATM.GHGT.ZG': 'GHG_Emissions_Growth_Pct',                # Emissions growth

    # ========================================================================
    # STRUCTURAL & DEVELOPMENT
    # ========================================================================
    'NV.IND.MANF.ZS': 'Manufacturing_Value_Added_Pct_GDP',       # Industrial structure
    'NV.AGR.TOTL.ZS': 'Agriculture_Value_Added_Pct_GDP',         # Agricultural share
    'SI.POV.GINI': 'Gini_Index',                                 # Inequality
    'SL.UEM.TOTL.ZS': 'Unemployment_Rate_Pct',                   # Labor market
}

# ============================================================================
# 4. VARIABLE GROUPINGS (for analysis and feature engineering)
# ============================================================================

# Core green transition variables
GREEN_VARS = [
    'Renewable_Energy_Consumption_Pct',
    'Renewable_Electricity_Output_Pct',
    'Renewable_Electricity_NoHydro_Pct',
    'Fossil_Fuel_Consumption_Pct',
    'Alternative_Nuclear_Energy_Pct'
]

# Energy vulnerability (especially important for Turkey)
ENERGY_VULNERABILITY_VARS = [
    'Energy_Imports_Net_Pct',
    'Fuel_Imports_Pct_Merchandise',
    'Energy_Intensity_Primary_MJ_Per_GDP',
    'Energy_Use_Per_GDP_PPP'
]

# Inflation drivers (for model controls)
INFLATION_CONTROLS = [
    'Broad_Money_Growth_Pct',
    'Real_Effective_Exchange_Rate_Index',
    'Energy_Imports_Net_Pct',
    'Current_Account_Balance_Pct_GDP',
    'Gov_Expenditure_Pct_GDP'
]

# Carbon/emissions variables
EMISSIONS_VARS = [
    'Carbon_Intensity_CO2_Per_GDP',
    'CO2_Emissions_Per_Capita_Tons',
    'GHG_Emissions_Total_KtCO2e',
    'GHG_Emissions_Growth_Pct'
]

# Variables that should NOT be interpolated (volatile, crisis-sensitive)
NO_INTERPOLATE = [
    'Inflation_CPI_Pct',
    'GDP_Growth_Pct',
    'Broad_Money_Growth_Pct',
    'GHG_Emissions_Growth_Pct',
    'GDP_Deflator_Growth_Pct',
    'Real_Interest_Rate_Pct'
]

# Variables suitable for forward-fill (structural, slow-moving)
FORWARD_FILL_OK = [
    'Renewable_Energy_Consumption_Pct',
    'Fossil_Fuel_Consumption_Pct',
    'Energy_Intensity_Primary_MJ_Per_GDP',
    'Population_Total',
    'Manufacturing_Value_Added_Pct_GDP'
]

# ============================================================================
# 5. PATHS
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# File paths
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, 'wb_raw.csv')
PROCESSED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, 'analysis_ready.csv')
TURKEY_COMPARISON_PATH = os.path.join(PROCESSED_DATA_DIR, 'turkey_vs_peers.csv')
DATA_QUALITY_REPORT_PATH = os.path.join(PROCESSED_DATA_DIR, 'data_quality_report.txt')

# Cache for WB API
CACHE_PATH = os.path.join(RAW_DATA_DIR, 'wb_cache.pkl')

# ============================================================================
# 6. ANALYSIS PARAMETERS
# ============================================================================

# For clustering
N_CLUSTERS_RANGE = range(3, 8)  # Test 3-7 clusters
CLUSTERING_FEATURES = GREEN_VARS + ENERGY_VULNERABILITY_VARS + ['Inflation_CPI_Pct', 'GDP_Growth_Pct']

# For Random Forest
RF_PARAMS = {
    'n_estimators': 500,
    'max_depth': 10,
    'min_samples_split': 20,
    'min_samples_leaf': 10,
    'random_state': 42,
    'n_jobs': -1
}

# For panel regression
PANEL_EFFECTS = {
    'entity_effects': True,   # Country fixed effects
    'time_effects': True,      # Year fixed effects
}

# ============================================================================
# 7. RESEARCH-SPECIFIC SETTINGS
# ============================================================================

# Turkey-specific analysis flags
FOCUS_ON_TURKEY = True
TURKEY_PEER_COMPARISON_COUNTRIES = ['POL', 'MEX', 'ZAF', 'THA']  # Main comparisons
TURKEY_ADVANCED_COMPARISON = ['DEU', 'ITA']  # Aspirational comparisons

# Hypothesis testing
TEST_GREENFLATION = True  # Does green transition increase inflation?
TEST_GROWTH_VOLATILITY = True  # Does transition affect growth stability?
TEST_TEMPORAL_DYNAMICS = True  # Is the effect temporary or permanent?

# ============================================================================
# 8. DATA QUALITY THRESHOLDS
# ============================================================================
MIN_OBSERVATIONS_PER_COUNTRY = 15  # At least 15 years of data
MAX_MISSING_PCT_PER_VARIABLE = 0.30  # Drop variables missing >30%
OUTLIER_THRESHOLD_INFLATION = 100  # Flag inflation > 100% as potential error
OUTLIER_THRESHOLD_GDP_GROWTH = 20  # Flag GDP growth > |20%| as potential error

print(f"✅ Configuration loaded successfully")
print(f"📊 Total countries: {len(ALL_COUNTRIES)}")
print(f"🔢 Total indicators: {len(WDI_VARIABLES)}")
print(f"🇹🇷 Turkey comparison strategy: {len(TURKEY_PEER_COMPARISON_COUNTRIES)} peers + {len(TURKEY_ADVANCED_COMPARISON)} advanced")