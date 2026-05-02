"""
Script extracted from notebook cell 1.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
INPUT_PATH = "Paper_Data.xlsx"
OUTPUT_CSV = "outputs_historical_scopes.csv"

# Flag: assume calcination EF is per ton clinker (True) or per ton cement (False)
CALC_EF_IS_PER_CLINKER = True

# Weighted split for Scope 3 trucking: 60% overloaded, 40% allowed
OVERLOAD_FRAC = 0.60
ALLOWED_FRAC = 0.40

# ============================================================================
# STEP 1: READ DATA WITH CORRECT HEADER HANDLING
# ============================================================================
print("=" * 80)
print("STEP 1: READ EXCEL DATA")
print("=" * 80)

# The file has data starting from row 0, with headers in row 0
# Read with header=0 and skip the multi-index parsing issue
df = pd.read_excel(INPUT_PATH, sheet_name='Sheet1', header=0)

print(f"Data shape: {df.shape} (rows, columns)")
print(f"Year range: {df['Fiscal Year - July - June'].min()} to {df['Fiscal Year - July - June'].max()}\n")

# ============================================================================
# STEP 2: COLUMN MAPPING & RENAMING
# ============================================================================
print("=" * 80)
print("STEP 2: STANDARDIZE COLUMN NAMES")
print("=" * 80)

# Map raw column names to standardized internal names
COLUMN_MAPPING = {
    'Fiscal Year - July - June': 'year',
    'Total Cement Production-Tons': 'cement_t',
    'Local dispatches (North, South)-Tons': 'local_t',
    'Exports (North)-Tons': 'exp_n_t',
    'Exports (South)-Tons': 'exp_s_t',
    'Coal intensity - (kg coal / ton cement)': 'coal_int_kgpt',
    'Electricity intensity - (kWh / ton cement)': 'elec_int_kwhpt',
    'Clinker ratio-%': 'clinker_ratio',
    'Coal parameters: NCV': 'ncv',
    'Coal parameters: CO2 combustion EF': 'co2_ef_tco2_per_tj',
    'Coal parameters: Oxidized carbon fraction': 'oxid_frac',
    'Calcination emission factor - (tCO2 / ton clinker)': 'calc_ef',
    'Grid electricity EF - (kgCO2 / kWh)': 'grid_ef_kg_per_kwh',
    'Truck capcity Tons- (Allowed Load)': 'cap_allowed_t',
    'Truck capcity Tons - (Over Load)': 'cap_over_t',
    'Truck emission factor - Allowed (g CO2 /km)': 'ef_allowed_gpkm',
    'Truck emission factor - OverLoad (g CO2 /km)': 'ef_over_gpkm',
    'Local Transport distances - (km) ': 'dist_local_km',
    'North Export Transport distances - (km) ': 'dist_exp_n_km',
    'South Export Transport distances- (km) ': 'dist_exp_s_km',
}

# Rename columns
df = df.rename(columns=COLUMN_MAPPING)

# Keep only standardized columns
standard_cols = list(COLUMN_MAPPING.values())
df = df[standard_cols].copy()

print(f"Standardized columns: {df.columns.tolist()}\n")
print(f"First 3 data rows:\n{df.head(3)}\n")

# ============================================================================
# STEP 3: UNIT SANITY CHECKS & CONVERSIONS
# ============================================================================
print("=" * 80)
print("STEP 3: UNIT SANITY CHECKS & CONVERSIONS")
print("=" * 80)

# Check clinker_ratio: if median > 1.5, treat as percent and divide by 100
clinker_median = df['clinker_ratio'].median()
print(f"Clinker ratio median: {clinker_median}")
if clinker_median > 1.5:
    print("  → Detected as percent. Converting to fraction (divide by 100).")
    df['clinker_ratio'] = df['clinker_ratio'] / 100
else:
    print("  → Detected as fraction (0-1). No conversion needed.")

# Check NCV: if median > 1, assume GJ/ton and convert to TJ/ton
ncv_median = df['ncv'].median()
print(f"NCV median: {ncv_median}")
if ncv_median > 1:
    print("  → Detected as GJ/ton. Converting to TJ/ton (divide by 1000).")
    df['ncv'] = df['ncv'] / 1000
else:
    print("  → Detected as TJ/ton. No conversion needed.")

print()

# ============================================================================
# STEP 4: HANDLE MISSING VALUES
# ============================================================================
print("=" * 80)
print("STEP 4: MISSING VALUE CHECK")
print("=" * 80)

missing_counts = df.isnull().sum()
if missing_counts.sum() > 0:
    print("Missing values detected:")
    print(missing_counts[missing_counts > 0])
    print()
else:
    print("No missing values detected.\n")

# ============================================================================
# STEP 5: SCOPE 1 - FUEL COMBUSTION CO₂
# ============================================================================
print("=" * 80)
print("STEP 5: SCOPE 1 - FUEL COMBUSTION")
print("=" * 80)

# Coal consumption: coal_t = cement_t * (coal_int_kgpt / 1000)
df['coal_t'] = df['cement_t'] * (df['coal_int_kgpt'] / 1000)

# Energy content: energy_TJ = coal_t * ncv_TJ_per_t
df['energy_TJ'] = df['coal_t'] * df['ncv']

# Scope 1 fuel CO₂: CO2_S1_fuel_t = energy_TJ * co2_ef_tco2_per_tj * oxid_frac
df['CO2_S1_fuel_t'] = df['energy_TJ'] * df['co2_ef_tco2_per_tj'] * df['oxid_frac']

print(f"Coal consumption range: {df['coal_t'].min():.0f} to {df['coal_t'].max():.0f} tons")
print(f"Energy TJ range: {df['energy_TJ'].min():.1f} to {df['energy_TJ'].max():.1f} TJ")
print(f"S1 Fuel CO₂ range: {df['CO2_S1_fuel_t'].min():.0f} to {df['CO2_S1_fuel_t'].max():.0f} tCO₂\n")

# ============================================================================
# STEP 6: SCOPE 1 - PROCESS EMISSIONS (CALCINATION)
# ============================================================================
print("=" * 80)
print("STEP 6: SCOPE 1 - PROCESS EMISSIONS (CALCINATION)")
print("=" * 80)

print(f"Assumption: calc_ef is per ton {'CLINKER' if CALC_EF_IS_PER_CLINKER else 'CEMENT'}")

# Clinker production: clinker_t = cement_t * clinker_ratio
df['clinker_t'] = df['cement_t'] * df['clinker_ratio']

# Scope 1 process CO₂: depends on whether calc_ef is per clinker or per cement
if CALC_EF_IS_PER_CLINKER:
    df['CO2_S1_process_t'] = df['clinker_t'] * df['calc_ef']
else:
    df['CO2_S1_process_t'] = df['cement_t'] * df['calc_ef']

print(f"Clinker production range: {df['clinker_t'].min():.0f} to {df['clinker_t'].max():.0f} tons")
print(f"S1 Process CO₂ range: {df['CO2_S1_process_t'].min():.0f} to {df['CO2_S1_process_t'].max():.0f} tCO₂\n")

# ============================================================================
# STEP 7: SCOPE 2 - ELECTRICITY EMISSIONS
# ============================================================================
print("=" * 80)
print("STEP 7: SCOPE 2 - ELECTRICITY")
print("=" * 80)

# Electricity consumption: elec_kwh = cement_t * elec_int_kwhpt
df['elec_kwh'] = df['cement_t'] * df['elec_int_kwhpt']

# Scope 2 CO₂: CO2_S2_elec_t = (elec_kwh * grid_ef_kg_per_kwh) / 1000
df['CO2_S2_elec_t'] = (df['elec_kwh'] * df['grid_ef_kg_per_kwh']) / 1000

print(f"Electricity consumption range: {df['elec_kwh'].min():.0f} to {df['elec_kwh'].max():.0f} kWh")
print(f"S2 Electricity CO₂ range: {df['CO2_S2_elec_t'].min():.0f} to {df['CO2_S2_elec_t'].max():.0f} tCO₂\n")

# ============================================================================
# STEP 8: SCOPE 3 - DOWNSTREAM TRUCKING
# ============================================================================
print("=" * 80)
print("STEP 8: SCOPE 3 - DOWNSTREAM TRUCKING")
print("=" * 80)
print(f"Assumption: {ALLOWED_FRAC*100:.0f}% allowed + {OVERLOAD_FRAC*100:.0f}% overloaded split\n")

def calculate_scope3_route(flow_t, distance_km, cap_allowed, cap_over,
                           ef_allowed, ef_over, route_name):
    """
    Calculate Scope 3 CO₂ for a single transport route.

    Args:
        flow_t: annual flow in tons
        distance_km: distance in km
        cap_allowed: truck capacity (allowed load) in tons
        cap_over: truck capacity (overload) in tons
        ef_allowed: emission factor (allowed) in gCO₂/km
        ef_over: emission factor (overload) in gCO₂/km
        route_name: string for logging

    Returns:
        Series of tCO₂ per year
    """
    # Number of trips for each mode
    trips_allowed = flow_t / cap_allowed
    trips_over = flow_t / cap_over

    # gCO₂ = distance * (allowed_fraction * trips_allowed * EF_allowed +
    #                    overload_fraction * trips_over * EF_over)
    gco2 = (distance_km *
            (ALLOWED_FRAC * trips_allowed * ef_allowed +
             OVERLOAD_FRAC * trips_over * ef_over))

    # Convert grams to tonnes
    tco2 = gco2 / 1e6

    return tco2

# Local transport
df['CO2_S3_local_t'] = calculate_scope3_route(
    df['local_t'], df['dist_local_km'],
    df['cap_allowed_t'], df['cap_over_t'],
    df['ef_allowed_gpkm'], df['ef_over_gpkm'],
    'Local'
)

# Export North transport
df['CO2_S3_exp_n_t'] = calculate_scope3_route(
    df['exp_n_t'], df['dist_exp_n_km'],
    df['cap_allowed_t'], df['cap_over_t'],
    df['ef_allowed_gpkm'], df['ef_over_gpkm'],
    'Export North'
)

# Export South transport
df['CO2_S3_exp_s_t'] = calculate_scope3_route(
    df['exp_s_t'], df['dist_exp_s_km'],
    df['cap_allowed_t'], df['cap_over_t'],
    df['ef_allowed_gpkm'], df['ef_over_gpkm'],
    'Export South'
)

# Total Scope 3
df['CO2_S3_transport_t'] = df['CO2_S3_local_t'] + df['CO2_S3_exp_n_t'] + df['CO2_S3_exp_s_t']

print(f"S3 Local CO₂ range: {df['CO2_S3_local_t'].min():.0f} to {df['CO2_S3_local_t'].max():.0f} tCO₂")
print(f"S3 Export North CO₂ range: {df['CO2_S3_exp_n_t'].min():.0f} to {df['CO2_S3_exp_n_t'].max():.0f} tCO₂")
print(f"S3 Export South CO₂ range: {df['CO2_S3_exp_s_t'].min():.0f} to {df['CO2_S3_exp_s_t'].max():.0f} tCO₂")
print(f"S3 Total Transport CO₂ range: {df['CO2_S3_transport_t'].min():.0f} to {df['CO2_S3_transport_t'].max():.0f} tCO₂\n")

# ============================================================================
# STEP 9: CALCULATE TOTALS & INTENSITY
# ============================================================================
print("=" * 80)
print("STEP 9: CALCULATE TOTALS & INTENSITY")
print("=" * 80)

# Total Scope 1
df['CO2_S1_total_t'] = df['CO2_S1_fuel_t'] + df['CO2_S1_process_t']

# Grand total
df['CO2_total_t'] = (df['CO2_S1_fuel_t'] + df['CO2_S1_process_t'] +
                     df['CO2_S2_elec_t'] + df['CO2_S3_transport_t'])

# Carbon intensity (tCO₂ per ton cement)
df['CO2_intensity_t_per_tcement'] = df['CO2_total_t'] / df['cement_t']

print(f"Total CO₂ range: {df['CO2_total_t'].min():.0f} to {df['CO2_total_t'].max():.0f} tCO₂")
print(f"Intensity range: {df['CO2_intensity_t_per_tcement'].min():.3f} to {df['CO2_intensity_t_per_tcement'].max():.3f} tCO₂/t cement\n")

# ============================================================================
# STEP 10: PREPARE OUTPUT DATAFRAME
# ============================================================================
print("=" * 80)
print("STEP 10: PREPARE OUTPUT")
print("=" * 80)

# Select columns for output (clean view with all key results)
output_cols = [
    'year',
    'cement_t',
    'local_t',
    'exp_n_t',
    'exp_s_t',
    'coal_int_kgpt',
    'elec_int_kwhpt',
    'clinker_ratio',
    'ncv',
    'co2_ef_tco2_per_tj',
    'oxid_frac',
    'calc_ef',
    'grid_ef_kg_per_kwh',
    'cap_allowed_t', # Added missing column
    'cap_over_t',    # Added missing column
    'ef_allowed_gpkm', # Added missing column
    'ef_over_gpkm',  # Added missing column
    'dist_local_km', # Added missing column
    'dist_exp_n_km', # Added missing column
    'dist_exp_s_km', # Added missing column
    'coal_t',
    'energy_TJ',
    'CO2_S1_fuel_t',
    'clinker_t',
    'CO2_S1_process_t',
    'CO2_S1_total_t',
    'elec_kwh',
    'CO2_S2_elec_t',
    'CO2_S3_local_t',
    'CO2_S3_exp_n_t',
    'CO2_S3_exp_s_t',
    'CO2_S3_transport_t',
    'CO2_total_t',
    'CO2_intensity_t_per_tcement',
]

df_output = df[output_cols].copy()

# Save to CSV
df_output.to_csv(OUTPUT_CSV, index=False)
print(f"✓ Saved: {OUTPUT_CSV}\n")

# ============================================================================
# STEP 11: SUMMARY TABLE (LAST 5 YEARS)
# ============================================================================
print("=" * 80)
print("SUMMARY: LAST 5 YEARS OF DATA")
print("=" * 80)

summary_cols = [
    'year', 'cement_t',
    'CO2_S1_fuel_t', 'CO2_S1_process_t', 'CO2_S1_total_t',
    'CO2_S2_elec_t',
    'CO2_S3_transport_t',
    'CO2_total_t',
    'CO2_intensity_t_per_tcement'
]

summary_df = df_output[summary_cols].tail(5).copy()

# Format for display
pd.options.display.float_format = '{:,.2f}'.format
print(summary_df.to_string(index=False))

print("\n" + "=" * 80)
print("EXECUTION COMPLETE")
print("=" * 80)
print(f"\nOutput file: {OUTPUT_CSV}")
print(f"Total rows: {len(df_output)}")
print(f"Year range: {df_output['year'].min():.0f} to {df_output['year'].max():.0f}")
