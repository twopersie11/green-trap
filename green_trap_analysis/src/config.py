"""
Configuration file for Green Trap Analysis
Contains country lists, WDI variable mappings, and project parameters
"""

# ============================================================================
# COUNTRY LISTS (ISO-3 Codes)
# ============================================================================

# Developed economies
DEVELOPED = ['DEU', 'DNK', 'SWE', 'FRA', 'USA', 'JPN', 'GBR', 'CAN', 'AUS', 'NLD']

# Developing economies
DEVELOPING = ['TUR', 'IND', 'BRA', 'MEX', 'IDN', 'VNM', 'POL', 'ZAF', 'THA', 'MYS']

# Fast growing economies
FAST_GROWING = ['CHN', 'VNM', 'POL', 'BGD', 'PHL']

# Policy comparison group
POLICY_COMPARISON = ['NOR', 'ESP', 'ITA', 'GRC', 'PRT', 'KOR', 'CHL', 'SAU', 'RUS', 'NZL']

# Consolidated unique list
ALL_COUNTRIES = sorted(list(set(
    DEVELOPED + DEVELOPING + FAST_GROWING + POLICY_COMPARISON
)))

print(f"Total unique countries: {len(ALL_COUNTRIES)}")
print(f"Countries: {', '.join(ALL_COUNTRIES)}")


# ============================================================================
# TIME PERIOD
# ============================================================================

START_YEAR = 2000
END_YEAR = 2023


# ============================================================================
# WDI VARIABLE MAPPINGS
# Each key is a human-readable name, value is the World Bank WDI Series ID
# ============================================================================

WDI_VARIABLES = {
    # ---- OUTCOME VARIABLES ----
    'GDP_Growth': 'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
    'CPI_Inflation': 'FP.CPI.TOTL.ZG',  # Inflation, consumer prices (annual %)
    
    # ---- GREEN TRANSITION INDICATORS ----
    'Renewable_Energy_Consumption': 'EG.FEC.RNEW.ZS',  # Renewable energy consumption (% of total)
    'Renewable_Electricity_Output': 'EG.ELC.RNEW.ZS',  # Renewable electricity output (% of total)
    'Fossil_Fuel_Consumption': 'EG.USE.COMM.FO.ZS',  # Fossil fuel energy consumption (% of total)
    'Alternative_Nuclear_Energy': 'EG.USE.COMM.CL.ZS',  # Alternative and nuclear energy (% of total)
    
    # ---- ENERGY EFFICIENCY ----
    'Energy_Use_Per_Capita': 'EG.USE.PCAP.KG.OE',  # Energy use (kg of oil equivalent per capita)
    'Energy_Intensity': 'EG.EGY.PRIM.PP.KD',  # Energy intensity level (MJ/$2017 PPP GDP)
    
    # ---- ENERGY DEPENDENCY ----
    'Net_Energy_Imports': 'EG.IMP.CONS.ZS',  # Energy imports, net (% of energy use)
    'Fuel_Imports': 'TM.VAL.FUEL.ZS.UN',  # Fuel imports (% of merchandise imports)
    
    # ---- MACROECONOMIC & FINANCIAL ----
    'GDP_Per_Capita': 'NY.GDP.PCAP.KD',  # GDP per capita (constant 2015 US$)
    'Broad_Money': 'FM.LBL.BMNY.GD.ZS',  # Broad money (% of GDP)
    'Domestic_Credit': 'FS.AST.DOMS.GD.ZS',  # Domestic credit to private sector (% of GDP)
    'Real_Effective_Exchange_Rate': 'PX.REX.REER',  # Real effective exchange rate index
    'Official_Exchange_Rate': 'PA.NUS.FCRF',  # Official exchange rate (LCU per US$, period average)
    
    # ---- TRADE ----
    'Trade_GDP': 'NE.TRD.GNFS.ZS',  # Trade (% of GDP)
    'Current_Account_Balance': 'BN.CAB.XOKA.GD.ZS',  # Current account balance (% of GDP)
    'Exports_GDP': 'NE.EXP.GNFS.ZS',  # Exports of goods and services (% of GDP)
    'Imports_GDP': 'NE.IMP.GNFS.ZS',  # Imports of goods and services (% of GDP)
    
    # ---- FISCAL INDICATORS ----
    'Gov_Expenditure': 'NE.CON.GOVT.ZS',  # General government final consumption expenditure (% of GDP)
    'Tax_Revenue': 'GC.TAX.TOTL.GD.ZS',  # Tax revenue (% of GDP)
    'Gross_Fixed_Capital_Formation': 'NE.GDI.FTOT.ZS',  # Gross fixed capital formation (% of GDP)
    
    # ---- CARBON & EMISSIONS ----
    'CO2_Emissions_Per_Capita': 'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
    'CO2_Emissions_Total': 'EN.ATM.CO2E.KT',  # CO2 emissions (kt)
    'CO2_Intensity_GDP': 'EN.ATM.CO2E.PP.GD',  # CO2 emissions (kg per 2017 PPP $ of GDP)
    
    # ---- ADDITIONAL MACRO CONTROLS ----
    'Unemployment_Rate': 'SL.UEM.TOTL.ZS',  # Unemployment, total (% of total labor force)
    'Population_Growth': 'SP.POP.GROW',  # Population growth (annual %)
    'Urban_Population': 'SP.URB.TOTL.IN.ZS',  # Urban population (% of total)
    'FDI_Net_Inflows': 'BX.KLT.DINV.WD.GD.ZS',  # Foreign direct investment, net inflows (% of GDP)
    'Inflation_GDP_Deflator': 'NY.GDP.DEFL.KD.ZG',  # Inflation, GDP deflator (annual %)
    
    # ---- ELECTRICITY ACCESS & QUALITY ----
    'Access_Electricity': 'EG.ELC.ACCS.ZS',  # Access to electricity (% of population)
    'Electric_Power_Consumption': 'EG.USE.ELEC.KH.PC',  # Electric power consumption (kWh per capita)
    
    # ---- COMMODITY PRICES (if available for some countries) ----
    'Fuel_Exports': 'TX.VAL.FUEL.ZS.UN',  # Fuel exports (% of merchandise exports)
}

# Variables that should undergo log transformation (skewed distributions)
LOG_TRANSFORM_VARS = [
    'GDP_Per_Capita',
    'CO2_Emissions_Per_Capita',
    'CO2_Emissions_Total',
    'Energy_Use_Per_Capita',
    'Trade_GDP',
    'Electric_Power_Consumption'
]

# Variables to create lagged versions (t-1) for temporal analysis
LAG_VARIABLES = [
    'Renewable_Energy_Consumption',
    'Fossil_Fuel_Consumption',
    'Energy_Intensity',
    'Gross_Fixed_Capital_Formation',
    'FDI_Net_Inflows'
]

# ============================================================================
# CLUSTERING PARAMETERS
# ============================================================================

# Features to use for clustering (focusing on energy-macro profile)
CLUSTERING_FEATURES = [
    'Renewable_Energy_Consumption',
    'Energy_Intensity',
    'CPI_Inflation',
    'GDP_Growth',
    'CO2_Emissions_Per_Capita',
    'Trade_GDP',
    'Net_Energy_Imports'
]

# Range of K values to test for elbow method
K_RANGE = range(2, 11)


# ============================================================================
# RANDOM FOREST PARAMETERS
# ============================================================================

# Target variables for prediction
TARGET_VARIABLES = ['CPI_Inflation', 'GDP_Growth']

# Features to exclude from predictors (outcomes and identifiers)
EXCLUDE_FROM_PREDICTORS = TARGET_VARIABLES + ['Country', 'Year']

# Random Forest hyperparameters
RF_PARAMS = {
    'n_estimators': 200,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1  # Use all available cores
}

# Train-test split ratio
TEST_SIZE = 0.2
RANDOM_STATE = 42


# ============================================================================
# DATA QUALITY THRESHOLDS
# ============================================================================

# Maximum percentage of missing values allowed for a variable
MAX_MISSING_PERCENT = 30

# Minimum number of observations required per country
MIN_OBS_PER_COUNTRY = 10


# ============================================================================
# OUTPUT PATHS
# ============================================================================

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
FIGURES_DIR = os.path.join(OUTPUTS_DIR, 'figures')
MODELS_DIR = os.path.join(OUTPUTS_DIR, 'models')

# Create directories if they don't exist
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, FIGURES_DIR, MODELS_DIR]:
    os.makedirs(directory, exist_ok=True)
