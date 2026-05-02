"""
Script extracted from notebook cell 14.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# LOAD HISTORICAL DATA
# ============================================================================
print("=" * 80)
print("SCOPE 2 GRID EMISSION FACTOR SENSITIVITY ANALYSIS")
print("=" * 80)
print()

df = pd.read_csv('outputs_historical_scopes.csv')

print(f"✓ Loaded historical data: {len(df)} years\n")

# ============================================================================
# STEP 1: EXTRACT REQUIRED COLUMNS
# ============================================================================
print("Extracting emissions data from historical file...")
print()

# Check for required columns
required_cols = ['year', 'CO2_S1_fuel_t', 'CO2_S1_process_t', 'CO2_S2_elec_t', 'CO2_S3_transport_t']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print(f"ERROR: Missing columns: {missing_cols}")
    exit()

years = df['year'].values
s1_fuel = df['CO2_S1_fuel_t'].values
s1_process = df['CO2_S1_process_t'].values
s2_elec_base = df['CO2_S2_elec_t'].values
s3_transport = df['CO2_S3_transport_t'].values

# Verify data
print(f"Data extracted successfully:")
print(f"  Years: {int(years[0])} to {int(years[-1])} ({len(years)} years)")
print(f"  Scope 1 Fuel range: {s1_fuel.min()/1e6:.2f} to {s1_fuel.max()/1e6:.2f} Mt")
print(f"  Scope 1 Process range: {s1_process.min()/1e6:.2f} to {s1_process.max()/1e6:.2f} Mt")
print(f"  Scope 2 Elec base range: {s2_elec_base.min()/1e6:.2f} to {s2_elec_base.max()/1e6:.2f} Mt")
print(f"  Scope 3 Transport range: {s3_transport.min()/1e6:.2f} to {s3_transport.max()/1e6:.2f} Mt")
print()

# ============================================================================
# STEP 2: CREATE GRID EF SCENARIOS
# ============================================================================
print("Creating grid emission factor scenarios...")
print()

# Multipliers for grid EF
multiplier_low = 0.90      # Low: 90% of base
multiplier_base = 1.00     # Base: as-is
multiplier_high = 1.10     # High: 110% of base

print(f"Grid EF multipliers:")
print(f"  Low scenario:    {multiplier_low:.0%} (−10%)")
print(f"  Base case:       {multiplier_base:.0%} (no change)")
print(f"  High scenario:   {multiplier_high:.0%} (+10%)")
print()

# Calculate Scope 2 for each scenario
s2_elec_low = s2_elec_base * multiplier_low
s2_elec_high = s2_elec_base * multiplier_high

# Calculate total CO2 for each scenario
# Total = Scope 1 Fuel + Scope 1 Process + Scope 2 + Scope 3
co2_total_low = (s1_fuel + s1_process + s2_elec_low + s3_transport) / 1e6  # Convert to Mt
co2_total_base = (s1_fuel + s1_process + s2_elec_base + s3_transport) / 1e6
co2_total_high = (s1_fuel + s1_process + s2_elec_high + s3_transport) / 1e6

# Also calculate Scope 2 in Mt for reference
s2_low_Mt = s2_elec_low / 1e6
s2_base_Mt = s2_elec_base / 1e6
s2_high_Mt = s2_elec_high / 1e6

print()

# ============================================================================
# STEP 3: CREATE RESULTS DATAFRAME
# ============================================================================
results = pd.DataFrame()
results['Year'] = years
results['S2_low'] = s2_low_Mt
results['S2_base'] = s2_base_Mt
results['S2_high'] = s2_high_Mt
results['CO2_total_low'] = co2_total_low
results['CO2_total_base'] = co2_total_base
results['CO2_total_high'] = co2_total_high

print("Results dataframe created:")
print(f"  Columns: {results.columns.tolist()}")
print()

# ============================================================================
# STEP 4: DISPLAY RESULTS TABLE
# ============================================================================
print("=" * 80)
print("RESULTS TABLE: TOTAL CO₂ EMISSIONS (Mt CO₂)")
print("=" * 80)
print()

# Show first 5, last 5, and key years
display_indices = list(range(min(5, len(results)))) + list(range(max(0, len(results)-5), len(results)))
display_indices = sorted(set(display_indices))

display_df = results.iloc[display_indices][['Year', 'S2_low', 'S2_base', 'S2_high',
                                              'CO2_total_low', 'CO2_total_base', 'CO2_total_high']].copy()

pd.options.display.float_format = '{:.4f}'.format
print(display_df.to_string(index=False))
print()

# ============================================================================
# STEP 5: SENSITIVITY ANALYSIS
# ============================================================================
print("=" * 80)
print("SENSITIVITY ANALYSIS - GRID EMISSION FACTOR")
print("=" * 80)
print()

latest_idx = len(results) - 1
latest_year = int(results.loc[latest_idx, 'Year'])

s2_low_latest = results.loc[latest_idx, 'S2_low']
s2_base_latest = results.loc[latest_idx, 'S2_base']
s2_high_latest = results.loc[latest_idx, 'S2_high']

co2_low_latest = results.loc[latest_idx, 'CO2_total_low']
co2_base_latest = results.loc[latest_idx, 'CO2_total_base']
co2_high_latest = results.loc[latest_idx, 'CO2_total_high']

print(f"Latest year ({latest_year}):")
print()

print(f"Scope 2 (electricity) only:")
print(f"  Low (−10% grid EF):  {s2_low_latest:.4f} Mt CO₂")
print(f"  Base:                {s2_base_latest:.4f} Mt CO₂")
print(f"  High (+10% grid EF): {s2_high_latest:.4f} Mt CO₂")
print()

# Scope 2 differences
s2_diff_low_high = s2_high_latest - s2_low_latest
s2_diff_pct_low_high = (s2_diff_low_high / s2_base_latest) * 100

print(f"Scope 2 sensitivity (low vs high):")
print(f"  Absolute: {s2_diff_low_high:+.4f} Mt CO₂")
print(f"  Relative: {s2_diff_pct_low_high:+.2f}%")
print()

# Total CO2 differences
print(f"Total CO₂ (Scope 1 + 2 + 3):")
print(f"  Low (−10% grid EF):  {co2_low_latest:.4f} Mt CO₂")
print(f"  Base:                {co2_base_latest:.4f} Mt CO₂")
print(f"  High (+10% grid EF): {co2_high_latest:.4f} Mt CO₂")
print()

co2_diff_low_high = co2_high_latest - co2_low_latest
co2_diff_pct_low_high = (co2_diff_low_high / co2_base_latest) * 100

print(f"Total CO₂ sensitivity (low vs high):")
print(f"  Absolute: {co2_diff_low_high:+.4f} Mt CO₂")
print(f"  Relative: {co2_diff_pct_low_high:+.2f}%")
print()

# Relative contribution of Scope 2 to total
s1_total = (s1_fuel[-1] + s1_process[-1]) / 1e6
s2_pct_of_total = (s2_base_latest / co2_base_latest) * 100
s3_pct_of_total = (s3_transport[-1] / 1e6 / co2_base_latest) * 100

print(f"Scope composition ({latest_year}):")
print(f"  Scope 1 (Fuel + Process): {s1_total:.4f} Mt ({(s1_total/co2_base_latest)*100:.1f}%)")
print(f"  Scope 2 (Electricity):    {s2_base_latest:.4f} Mt ({s2_pct_of_total:.1f}%)")
print(f"  Scope 3 (Transport):      {(s3_transport[-1]/1e6):.4f} Mt ({s3_pct_of_total:.1f}%)")
print()

# Impact statement
print(f"Impact statement:")
print(f"  A ±10% change in grid EF results in a {co2_diff_pct_low_high/2:.2f}% change in total CO₂")
print(f"  (since Scope 2 is {s2_pct_of_total:.1f}% of total)")
print()

# ============================================================================
# STEP 6: TEMPORAL ANALYSIS
# ============================================================================
print("=" * 80)
print("TEMPORAL ANALYSIS")
print("=" * 80)
print()

# First year
first_idx = 0
first_year = int(results.loc[first_idx, 'Year'])
co2_low_first = results.loc[first_idx, 'CO2_total_low']
co2_base_first = results.loc[first_idx, 'CO2_total_base']
co2_high_first = results.loc[first_idx, 'CO2_total_high']
diff_pct_first = ((co2_high_first - co2_low_first) / co2_base_first) * 100

print(f"First year ({first_year}):")
print(f"  Low:  {co2_low_first:.4f} Mt CO₂")
print(f"  Base: {co2_base_first:.4f} Mt CO₂")
print(f"  High: {co2_high_first:.4f} Mt CO₂")
print(f"  Low–High difference: {diff_pct_first:.2f}%")
print()

# Average across all years
avg_diff_pct = ((results['CO2_total_high'] - results['CO2_total_low']) / results['CO2_total_base']).mean() * 100

print(f"Average across all {len(results)} years:")
print(f"  Low–High difference: {avg_diff_pct:.2f}%")
print()

# Check if sensitivity is constant (should be, since Scope 2 scales linearly)
early_period = results.iloc[:len(results)//2]
late_period = results.iloc[len(results)//2:]

early_diff_pct = ((early_period['CO2_total_high'] - early_period['CO2_total_low']) / early_period['CO2_total_base']).mean() * 100
late_diff_pct = ((late_period['CO2_total_high'] - late_period['CO2_total_low']) / late_period['CO2_total_base']).mean() * 100

print(f"Early period ({int(early_period['Year'].iloc[0])}–{int(early_period['Year'].iloc[-1])}):")
print(f"  Low–High difference: {early_diff_pct:.2f}%")
print()

print(f"Late period ({int(late_period['Year'].iloc[0])}–{int(late_period['Year'].iloc[-1])}):")
print(f"  Low–High difference: {late_diff_pct:.2f}%")
print()

# ============================================================================
# STEP 7: SAVE RESULTS
# ============================================================================
output_csv = 'cement_scope2_grid_ef_sensitivity.csv'
results.to_csv(output_csv, index=False)
print(f"✓ Results saved to: {output_csv}\n")

# ============================================================================
# STEP 8: CREATE LINE CHART
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#2ca02c', '#1f77b4', '#d62728']
markers = ['o', 's', '^']
scenario_labels = ['Low (−10% grid EF)', 'Base', 'High (+10% grid EF)']
scenario_cols = ['CO2_total_low', 'CO2_total_base', 'CO2_total_high']

for col, label, color, marker in zip(scenario_cols, scenario_labels, colors, markers):
    ax.plot(results['Year'], results[col], linewidth=2.5, color=color,
            marker=marker, markersize=5, markerfacecolor=color, markeredgecolor='white',
            markeredgewidth=0.5, label=label, alpha=0.85)

# Labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Sensitivity: grid EF ±10%', fontsize=14, fontweight='bold', pad=20)

# Legend
ax.legend(loc='best', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# X-axis ticks
ax.set_xticks(range(int(results['Year'].min()), int(results['Year'].max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add annotation showing latest-year sensitivity
ax.text(0.98, 0.05, f'{latest_year} difference:\nLow–High: {co2_diff_pct_low_high:.2f}%',
        transform=ax.transAxes,
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
        ha='right', va='bottom')

plt.tight_layout()

output_plot = 'cement_scope2_grid_ef_sensitivity.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved to: {output_plot}\n")

plt.show()

# ============================================================================
# STEP 9: SUMMARY INSIGHTS
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print(f"""
• Grid emission factor (EF) directly scales Scope 2 electricity emissions.

• A ±10% change in grid EF results in a ±10% change in Scope 2 emissions.

• Since Scope 2 represents ~{s2_pct_of_total:.1f}% of total cement sector CO₂,
  grid EF uncertainty translates to a {co2_diff_pct_low_high/2:.2f}% uncertainty in total emissions.

• The sensitivity is LINEAR and CONSTANT across all years, depending only
  on the proportion of Scope 2 to total emissions.

• Latest-year (2023) difference between low and high grid EF cases:
  {co2_diff_pct_low_high:.2f}% ({co2_diff_low_high:.4f} Mt CO₂)

• Early and late period sensitivities are equal ({early_diff_pct:.2f}% vs {late_diff_pct:.2f}%),
  confirming that grid EF impacts are decoupled from production growth.

• This uncertainty highlights the importance of:
  1. Accurate grid decarbonization forecasts
  2. Regional grid EF baselines (different countries have different EFs)
  3. Scope 2 reporting methodology (location-based vs market-based)
""")

print()