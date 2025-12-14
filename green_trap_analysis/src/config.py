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
    elif c in FAST_GROWING: COUNTRY_GROUPS[c] = 'Fast_Growing'
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
    # --- 1. Outcomes (Bağımlı Değişkenler) ---
    'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Pct',
    'FP.CPI.TOTL.ZG': 'Inflation_Consumer_Prices_Pct',

    # --- 2. Green Transition (Yeşil Dönüşüm) ---
    'EG.FEC.RNEW.ZS': 'Renewable_Energy_Consumption_Pct',
    'EG.ELC.RNEW.ZS': 'Renewable_Electricity_Output_Pct',
    'EG.ELC.RNWX.ZS': 'Renewable_Electricity_NoHydro_Pct', # Hidro hariç (Önemli)
    'EG.USE.COMM.FO.ZS': 'Fossil_Fuel_Consumption_Pct',
    'EG.USE.COMM.CL.ZS': 'Alternative_Nuclear_Energy_Pct',

    # --- 3. Energy Efficiency & Dependence ---
    'EG.USE.PCAP.KG.OE': 'Energy_Use_Per_Capita',
    'EG.EGY.PRIM.PP.KD': 'Energy_Intensity_Level_Primary', # Verimlilik göstergesi
    'EG.IMP.CONS.ZS': 'Energy_Imports_Net_Pct',
    'TM.VAL.FUEL.ZS.UN': 'Fuel_Imports_Pct_Merchandise',

    # --- 4. Macro & Financial ---
    'NY.GDP.PCAP.PP.KD': 'GDP_Per_Capita_PPP', # Satınalma gücü paritesiyle
    'FM.LBL.BMNY.GD.ZS': 'Broad_Money_Pct_GDP',
    'FD.AST.PRVT.GD.ZS': 'Domestic_Credit_Private_Pct_GDP',
    'NE.TRD.GNFS.ZS': 'Trade_Pct_GDP',
    'BN.CAB.XOKA.GD.ZS': 'Current_Account_Balance_Pct_GDP',

    # --- 5. Exchange Rate & Prices ---
    'PX.REX.REER': 'Real_Effective_Exchange_Rate', # Rekabetçilik ve Enflasyon geçişkenliği için

    # --- 6. Government & Investment ---
    'NE.CON.GOVT.ZS': 'Gov_Expenditure_Pct_GDP',
    'NE.GDI.FTOT.ZS': 'Gross_Fixed_Capital_Formation_Pct_GDP', # Yatırımlar

    # --- 7. Carbon & Emissions ---
    'EN.ATM.CO2E.PP.GD.KD': 'Carbon_Intensity_GDP', # GSYH başına emisyon
    'EN.ATM.CO2E.PC': 'CO2_Emissions_Per_Capita',
}

# ============================================================================
# 4. PATHS
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'wb_raw.csv')
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'analysis_ready.csv')