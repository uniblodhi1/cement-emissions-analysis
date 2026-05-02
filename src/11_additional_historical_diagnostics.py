"""
Script extracted from notebook cell 11.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1: LOAD AND PREPARE HISTORICAL DATA
# ============================================================================
print("=" * 80)
print("CEMENT SECTOR CO₂ PROJECTION - BASELINE SETUP")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')

print(f"✓ Loaded CSV: {len(hist)} rows, {len(hist.columns)} columns")
print(f"  Columns: {hist.columns.tolist()}\n")

# Sort by year
hist = hist.sort_values('year').reset_index(drop=True)

# ============================================================================
# STEP 2: IDENTIFY BASE YEAR AND BASELINE VALUES
# ============================================================================
BASE_YEAR = int(hist['year'].max())
print(f"BASE_YEAR: {BASE_YEAR}\n")

# Get latest year row
baseline_row = hist[hist['year'] == BASE_YEAR].iloc[0]

# Extract cement production baseline
if 'cement_t' in hist.columns:
    cement_base = baseline_row['cement_t']
    print(f"✓ Cement production baseline (cement_t): {cement_base:.0f} tonnes")
    print(f"  ({cement_base/1e6:.2f} Mt)\n")
else:
    cement_base = 1.0
    print(f"⚠ Cement production column 'cement_t' not found.")
    print(f"  Using placeholder: cement_base = {cement_base}\n")

# ============================================================================
# STEP 3: EXTRACT BASELINE INTENSITY VALUES
# ============================================================================
print("Baseline intensity values (from latest available year):")
print()

# Initialize baseline dictionaries
baseline_intensities = {}

# Coal intensity (kg coal / ton cement)
if 'coal_int_kgpt' in hist.columns:
    coal_int_base = baseline_row['coal_int_kgpt']
    baseline_intensities['coal_int_kgpt'] = coal_int_base
    print(f"  Coal intensity:         {coal_int_base:.2f} kg coal/t cement")
else:
    coal_int_base = None
    print(f"  Coal intensity:         [PLACEHOLDER - user to provide]")

# Electricity intensity (kWh / ton cement)
if 'elec_int_kwhpt' in hist.columns:
    elec_int_base = baseline_row['elec_int_kwhpt']
    baseline_intensities['elec_int_kwhpt'] = elec_int_base
    print(f"  Electricity intensity:  {elec_int_base:.2f} kWh/t cement")
else:
    elec_int_base = None
    print(f"  Electricity intensity:  [PLACEHOLDER - user to provide]")

# Clinker ratio (fraction)
if 'clinker_ratio' in hist.columns:
    clinker_ratio_base = baseline_row['clinker_ratio']
    baseline_intensities['clinker_ratio'] = clinker_ratio_base
    print(f"  Clinker ratio:          {clinker_ratio_base:.4f} (fraction)")
else:
    clinker_ratio_base = None
    print(f"  Clinker ratio:          [PLACEHOLDER - user to provide]")

# NCV (TJ/ton)
if 'ncv' in hist.columns:
    ncv_base = baseline_row['ncv']
    baseline_intensities['ncv'] = ncv_base
    print(f"  NCV (coal):             {ncv_base:.4f} TJ/ton")
else:
    ncv_base = None
    print(f"  NCV (coal):             [PLACEHOLDER - user to provide]")

# CO2 combustion EF (tCO2/TJ)
if 'co2_ef_tco2_per_tj' in hist.columns:
    co2_ef_base = baseline_row['co2_ef_tco2_per_tj']
    baseline_intensities['co2_ef_tco2_per_tj'] = co2_ef_base
    print(f"  CO2 combustion EF:      {co2_ef_base:.2f} tCO2/TJ")
else:
    co2_ef_base = None
    print(f"  CO2 combustion EF:      [PLACEHOLDER - user to provide]")

# Oxidation fraction
if 'oxid_frac' in hist.columns:
    oxid_frac_base = baseline_row['oxid_frac']
    baseline_intensities['oxid_frac'] = oxid_frac_base
    print(f"  Oxidation fraction:     {oxid_frac_base:.4f}")
else:
    oxid_frac_base = None
    print(f"  Oxidation fraction:     [PLACEHOLDER - user to provide]")

# Calcination EF (tCO2/ton clinker, assuming per clinker)
if 'calc_ef' in hist.columns:
    calc_ef_base = baseline_row['calc_ef']
    baseline_intensities['calc_ef'] = calc_ef_base
    print(f"  Calcination EF:         {calc_ef_base:.6f} tCO2/t clinker")
else:
    calc_ef_base = None
    print(f"  Calcination EF:         [PLACEHOLDER - user to provide]")

# Grid electricity EF (kgCO2/kWh)
if 'grid_ef_kg_per_kwh' in hist.columns:
    grid_ef_base = baseline_row['grid_ef_kg_per_kwh']
    baseline_intensities['grid_ef_kg_per_kwh'] = grid_ef_base
    print(f"  Grid EF:                {grid_ef_base:.6f} kgCO2/kWh")
else:
    grid_ef_base = None
    print(f"  Grid EF:                [PLACEHOLDER - user to provide]")

# Truck parameters (for Scope 3)
if 'ef_allowed_gpkm' in hist.columns:
    truck_ef_allowed = baseline_row['ef_allowed_gpkm']
    baseline_intensities['ef_allowed_gpkm'] = truck_ef_allowed
    print(f"  Truck EF (allowed):     {truck_ef_allowed:.2f} gCO2/km")
else:
    truck_ef_allowed = None
    print(f"  Truck EF (allowed):     [PLACEHOLDER - user to provide]")

if 'ef_over_gpkm' in hist.columns:
    truck_ef_over = baseline_row['ef_over_gpkm']
    baseline_intensities['ef_over_gpkm'] = truck_ef_over
    print(f"  Truck EF (overload):    {truck_ef_over:.2f} gCO2/km")
else:
    truck_ef_over = None
    print(f"  Truck EF (overload):    [PLACEHOLDER - user to provide]")

print()

# ============================================================================
# STEP 4: CALCULATE/DERIVE BASELINE CO2 EMISSIONS (for reference)
# ============================================================================
print("Baseline CO₂ emissions (from historical data):")
print()

if 'CO2_S1_fuel_t' in hist.columns:
    s1_fuel_base = baseline_row['CO2_S1_fuel_t']
    print(f"  Scope 1 Fuel:           {s1_fuel_base/1e6:.2f} Mt CO₂/year")
else:
    s1_fuel_base = None
    print(f"  Scope 1 Fuel:           [NOT IN DATA]")

if 'CO2_S1_process_t' in hist.columns:
    s1_process_base = baseline_row['CO2_S1_process_t']
    print(f"  Scope 1 Process:        {s1_process_base/1e6:.2f} Mt CO₂/year")
else:
    s1_process_base = None
    print(f"  Scope 1 Process:        [NOT IN DATA]")

if 'CO2_S2_elec_t' in hist.columns:
    s2_elec_base = baseline_row['CO2_S2_elec_t']
    print(f"  Scope 2 Electricity:    {s2_elec_base/1e6:.2f} Mt CO₂/year")
else:
    s2_elec_base = None
    print(f"  Scope 2 Electricity:    [NOT IN DATA]")

if 'CO2_S3_transport_t' in hist.columns:
    s3_transport_base = baseline_row['CO2_S3_transport_t']
    print(f"  Scope 3 Transport:      {s3_transport_base/1e6:.2f} Mt CO₂/year")
else:
    s3_transport_base = None
    print(f"  Scope 3 Transport:      [NOT IN DATA]")

if 'CO2_total_t' in hist.columns:
    co2_total_base = baseline_row['CO2_total_t']
    print(f"  TOTAL:                  {co2_total_base/1e6:.2f} Mt CO₂/year")
else:
    co2_total_base = None
    print(f"  TOTAL:                  [NOT IN DATA]")

print()

# ============================================================================
# STEP 5: DEFINE PROJECTION CONSTANTS
# ============================================================================
print("=" * 80)
print("PROJECTION SCENARIO CONSTANTS")
print("=" * 80)
print()

# Demand growth rates
demand_growth_low = 0.01      # 1% annual
demand_growth_med = 0.03      # 3% annual
demand_growth_high = 0.05     # 5% annual

print("Demand growth rates (annual):")
print(f"  Low scenario:      {demand_growth_low*100:.1f}%")
print(f"  Medium scenario:   {demand_growth_med*100:.1f}%")
print(f"  High scenario:     {demand_growth_high*100:.1f}%")
print()

# Scenario improvement rates and targets
# Format: (annual improvement rate, 2050 target)
scenarios = {
    'BAU': {
        'label': 'Business as Usual',
        'demand_growth': demand_growth_med,
        'coal_int_improve_rate': 0.00,   # No improvement
        'coal_int_target_2050': 1.00,    # No change
        'elec_int_improve_rate': 0.00,
        'elec_int_target_2050': 1.00,
        'clinker_ratio_improve_rate': 0.00,
        'clinker_ratio_target_2050': 1.00,
        'grid_ef_improve_rate': 0.00,
        'grid_ef_target_2050': 1.00,
        'truck_ef_improve_rate': 0.00,
        'truck_ef_target_2050': 1.00,
    },
    'Moderate': {
        'label': 'Moderate Decarbonization',
        'demand_growth': demand_growth_med,
        'coal_int_improve_rate': 0.015,  # 1.5% annual improvement
        'coal_int_target_2050': 0.60,    # 40% reduction by 2050
        'elec_int_improve_rate': 0.010,  # 1% annual improvement
        'elec_int_target_2050': 0.75,
        'clinker_ratio_improve_rate': 0.005,  # 0.5% annual
        'clinker_ratio_target_2050': 0.90,
        'grid_ef_improve_rate': 0.030,   # 3% annual (grid decarbonization)
        'grid_ef_target_2050': 0.20,
        'truck_ef_improve_rate': 0.015,
        'truck_ef_target_2050': 0.80,
    },
    'Aggressive': {
        'label': 'Aggressive Decarbonization',
        'demand_growth': demand_growth_low,
        'coal_int_improve_rate': 0.030,  # 3% annual improvement
        'coal_int_target_2050': 0.30,    # 70% reduction by 2050
        'elec_int_improve_rate': 0.020,  # 2% annual improvement
        'elec_int_target_2050': 0.60,
        'clinker_ratio_improve_rate': 0.015,  # 1.5% annual
        'clinker_ratio_target_2050': 0.75,
        'grid_ef_improve_rate': 0.050,   # 5% annual (rapid grid decarbonization)
        'grid_ef_target_2050': 0.05,
        'truck_ef_improve_rate': 0.030,
        'truck_ef_target_2050': 0.60,
    },
}

for scenario_name, params in scenarios.items():
    print(f"{scenario_name} ({params['label']}):")
    print(f"  Demand growth:               {params['demand_growth']*100:.1f}%/year")
    print(f"  Coal intensity improvement:  {params['coal_int_improve_rate']*100:.1f}%/year → {params['coal_int_target_2050']*100:.0f}% by 2050")
    print(f"  Elec intensity improvement:  {params['elec_int_improve_rate']*100:.1f}%/year → {params['elec_int_target_2050']*100:.0f}% by 2050")
    print(f"  Clinker ratio improvement:   {params['clinker_ratio_improve_rate']*100:.1f}%/year → {params['clinker_ratio_target_2050']*100:.0f}% by 2050")
    print(f"  Grid EF improvement:         {params['grid_ef_improve_rate']*100:.1f}%/year → {params['grid_ef_target_2050']*100:.0f}% by 2050")
    print(f"  Truck EF improvement:        {params['truck_ef_improve_rate']*100:.1f}%/year → {params['truck_ef_target_2050']*100:.0f}% by 2050")
    print()

# ============================================================================
# STEP 6: DEFINE PROJECTION YEARS
# ============================================================================
years = np.arange(BASE_YEAR + 1, 2051)

print("=" * 80)
print("PROJECTION SETUP SUMMARY")
print("=" * 80)
print()
print(f"Base year:              {BASE_YEAR}")
print(f"Projection period:      {years[0]} to {years[-1]} ({len(years)} years)")
print(f"Scenarios:              {', '.join(scenarios.keys())}")
print()

# ============================================================================
# STEP 7: SUMMARY TABLE
# ============================================================================
print("=" * 80)
print("BASELINE VALUES SUMMARY")
print("=" * 80)
print()
print(f"Year {BASE_YEAR}:")
print(f"  Cement production:              {cement_base:.0f} tonnes ({cement_base/1e6:.2f} Mt)")

if 'CO2_total_t' in hist.columns:
    print(f"  Total CO₂ emissions:           {co2_total_base/1e6:.2f} Mt CO₂/year")
    print(f"  Carbon intensity:              {co2_total_base/cement_base:.4f} tCO₂/t cement")

print()
print("Baseline intensity parameters:")
for key, value in baseline_intensities.items():
    if value is not None:
        print(f"  {key:30s}: {value:.6f}")

print()
print("=" * 80)
print("✓ Setup complete. Ready for projection modeling.")
print("=" * 80)
print()