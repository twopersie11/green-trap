"""
Configuration file for Green Trap Analysis
"""
import os

# ============================================================================
# 1. COUNTRY LISTS (ISO-3 Codes)
# ============================================================================

DEVELOPED = ['DEU', 'DNK', 'SWE', 'FRA', 'USA', 'JPN', 'GBR', 'CAN', 'AUS', 'NLD']
DEVELOPING = ['TUR', 'IND', 'BRA', 'MEX', 'IDN', 'VNM', 'POL', 'ZAF', 'THA', 'MYS']
FAST_GROWING = ['CHN', 'VNM', 'POL', 'BGD', 'PHL']
POLICY_COMPARISON = ['NOR', 'ESP', 'ITA', 'GRC', 'PRT', 'KOR', 'CHL', 'SAU', 'RUS', 'NZL']

# Union of all lists (set handles duplicates like Poland/Vietnam)
ALL_COUNTRIES = sorted(list(set(DEVELOPED + DEVELOPING + FAST_GROWING + POLICY_COMPARISON)))

# Map codes to group names for analysis
COUNTRY_GROUPS = {}
for c in ALL_COUNTRIES:
    if c in DEVELOPED: COUNTRY_GROUPS[c] = 'Developed'
    elif c in FAST_GROWING: COUNTRY_GROUPS[c] = 'Fast_Growing' # Priority over Developing
    elif c in DEVELOPING: COUNTRY_GROUPS[c] = 'Emerging'
    else: COUNTRY_GROUPS[c] = 'Policy_Comp'

# ============================================================================
# 2. TIME PERIOD
# ============================================================================
START_YEAR = 2000
END_YEAR = 2023

# ============================================================================
# 3. WDI VARIABLE MAPPINGS (Code -> Clean Name)
# ============================================================================
WDI_VARIABLES = {
    # OUTCOMES
    'NY.GDP.MKTP.KD.ZG': 'GDP_Growth',
    'FP.CPI.TOTL.ZG': 'CPI_Inflation',

    # GREEN TRANSITION
    'EG.FEC.RNEW.ZS': 'Renewable_Energy_Consumption_Pct',
    'EG.ELC.RNEW.ZS': 'Renewable_Electricity_Output_Pct',
    'EG.USE.COMM.FO.ZS': 'Fossil_Fuel_Consumption_Pct',
    'EG.USE.COMM.CL.ZS': 'Alternative_Nuclear_Energy_Pct',

    # ENERGY EFFICIENCY & DEPENDENCE
    'EG.USE.PCAP.KG.OE': 'Energy_Use_Per_Capita',
    'EG.EGY.PRIM.PP.KD': 'Energy_Intensity',
    'EG.IMP.CONS.ZS': 'Net_Energy_Imports_Pct',

    # MACRO & FINANCIAL
    'NY.GDP.PCAP.KD': 'GDP_Per_Capita', # Constant 2015 US$
    'FM.LBL.BMNY.GD.ZS': 'Broad_Money_Pct_GDP',
    'FS.AST.DOMS.GD.ZS': 'Domestic_Credit_Pct_GDP',
    'NE.TRD.GNFS.ZS': 'Trade_Pct_GDP',
    'BX.KLT.DINV.WD.GD.ZS': 'FDI_Net_Inflows_Pct_GDP',

    # FISCAL & GOV
    'NE.CON.GOVT.ZS': 'Gov_Expenditure_Pct_GDP',
    'NE.GDI.FTOT.ZS': 'Gross_Fixed_Capital_Formation_Pct_GDP',

    # ---- CARBON & EMISSIONS (Commented out to prevent crashes) ----
    # 'EN.GHG.CO2.PC.CE.AR5': 'CO2_Emissions_Per_Capita',
    # 'EN.ATM.CO2E.KT': 'CO2_Emissions_Total',
    # 'EN.ATM.CO2E.PP.GD': 'CO2_Intensity_GDP',
}

# ============================================================================
# 4. ANALYSIS FEATURES lists
# ============================================================================
# This is the list your clustering code uses.
# I removed CO2 and ensured Fossil_Fuel_Consumption_Pct is here.
features_cluster = [
    'GDP_Growth',
    'FDI_Net_Inflows_Pct_GDP',
    'Energy_Intensity',
    'Renewable_Electricity_Output_Pct',
    'Renewable_Energy_Consumption_Pct',
    'Net_Energy_Imports_Pct',
    'Alternative_Nuclear_Energy_Pct',
    'Fossil_Fuel_Consumption_Pct', # <--- Proxy for CO2
    'Broad_Money_Pct_GDP',
    'CPI_Inflation',
    'Domestic_Credit_Pct_GDP',
    'Gov_Expenditure_Pct_GDP',
    'Gross_Fixed_Capital_Formation_Pct_GDP',
    'Trade_Pct_GDP'
]

# ============================================================================
# 5. PATHS
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'wdi_data.csv')
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'analysis_ready.csv')