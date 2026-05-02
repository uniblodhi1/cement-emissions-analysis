"""
Script extracted from notebook cell 12.
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
print("SCOPE 3 TRANSPORT LOADING SENSITIVITY ANALYSIS")
print("=" * 80)
print()

df = pd.read_csv('outputs_historical_scopes.csv')

print(f"✓ Loaded historical data: {len(df)} years\n")

# ============================================================================
# STEP 1: EXTRACT SCOPE 3 CALCULATION INPUTS
# ============================================================================
print("Extracting Scope 3 calculation inputs from historical data...")
print()

years_data = df['year'].values

# Transport flows (tonnes)
local_t = df['local_t'].values
exp_n_t = df['exp_n_t'].values
exp_s_t = df['exp_s_t'].values

# Distances (km) - assume constant per route
dist_local_km = df['dist_local_km'].values[0]  # Use first year (assumed constant)
dist_exp_n_km = df['dist_exp_n_km'].values[0]
dist_exp_s_km = df['dist_exp_s_km'].values[0]

# Truck parameters (assume constant)
cap_allowed_t = df['cap_allowed_t'].values[0]
cap_over_t = df['cap_over_t'].values[0]
ef_allowed_gpkm = df['ef_allowed_gpkm'].values[0]
ef_over_gpkm = df['ef_over_gpkm'].values[0]

print(f"Transport flows (tonnes/year):")
print(f"  Local:            {local_t[0]/1e6:.2f} Mt (Year {int(years_data[0])})")
print(f"  Export North:     {exp_n_t[0]/1e6:.2f} Mt")
print(f"  Export South:     {exp_s_t[0]/1e6:.2f} Mt")
print()

print(f"Distances (km):")
print(f"  Local:            {dist_local_km:.0f} km")
print(f"  Export North:     {dist_exp_n_km:.0f} km")
print(f"  Export South:     {dist_exp_s_km:.0f} km")
print()

print(f"Truck parameters:")
print(f"  Capacity (allowed): {cap_allowed_t:.1f} tonnes")
print(f"  Capacity (overload): {cap_over_t:.1f} tonnes")
print(f"  EF (allowed):     {ef_allowed_gpkm:.2f} gCO₂/km")
print(f"  EF (overload):    {ef_over_gpkm:.2f} gCO₂/km")
print()

# ============================================================================
# STEP 2: DEFINE TRANSPORT EMISSION FUNCTION
# ============================================================================
def calculate_scope3_route(flow_t, distance_km, cap_allowed, cap_over,
                          ef_allowed, ef_over, frac_allowed, frac_over):
    """
    Calculate Scope 3 CO₂ for a single transport route.

    Args:
        flow_t: annual flow in tonnes
        distance_km: distance in km
        cap_allowed: truck capacity (allowed load) in tonnes
        cap_over: truck capacity (overload) in tonnes
        ef_allowed: emission factor (allowed) in gCO₂/km
        ef_over: emission factor (overload) in gCO₂/km
        frac_allowed: fraction of trips in allowed load mode (0-1)
        frac_over: fraction of trips in overload mode (0-1)

    Returns:
        CO₂ in tonnes (not Mt)
    """
    # Number of trips for each mode
    trips_allowed = flow_t / cap_allowed
    trips_over = flow_t / cap_over

    # gCO₂ = distance * (allowed_frac * trips_allowed * EF_allowed +
    #                    overload_frac * trips_over * EF_over)
    gco2 = (distance_km *
            (frac_allowed * trips_allowed * ef_allowed +
             frac_over * trips_over * ef_over))

    # Convert grams to tonnes
    tco2 = gco2 / 1e6

    return tco2

# ============================================================================
# STEP 3: DEFINE LOADING SCENARIOS
# ============================================================================
loading_scenarios = {
    'S3_100_allowed': {'frac_allowed': 1.00, 'frac_over': 0.00},
    'S3_100_over': {'frac_allowed': 0.00, 'frac_over': 1.00},
    'S3_50_50': {'frac_allowed': 0.50, 'frac_over': 0.50},
    'S3_60_40': {'frac_allowed': 0.40, 'frac_over': 0.60},
    'S3_70_30': {'frac_allowed': 0.30, 'frac_over': 0.70},
}

print(f"Loading scenarios:")
for scenario_name, fractions in loading_scenarios.items():
    print(f"  {scenario_name:15s}: {fractions['frac_allowed']*100:3.0f}% allowed, "
          f"{fractions['frac_over']*100:3.0f}% overload")
print()

# ============================================================================
# STEP 4: COMPUTE SCOPE 3 FOR EACH SCENARIO
# ============================================================================
print("Computing Scope 3 transport emissions for each scenario...")
print()

# Initialize results dataframe
results = pd.DataFrame()
results['Year'] = years_data

# For each scenario, calculate S3 transport
for scenario_name, fractions in loading_scenarios.items():
    frac_allowed = fractions['frac_allowed']
    frac_over = fractions['frac_over']

    s3_local = []
    s3_exp_n = []
    s3_exp_s = []
    s3_total = []

    for i in range(len(df)):
        # Local
        s3_local_t = calculate_scope3_route(
            local_t[i], dist_local_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )
        s3_local.append(s3_local_t)

        # Export North
        s3_exp_n_t = calculate_scope3_route(
            exp_n_t[i], dist_exp_n_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )
        s3_exp_n.append(s3_exp_n_t)

        # Export South
        s3_exp_s_t = calculate_scope3_route(
            exp_s_t[i], dist_exp_s_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )
        s3_exp_s.append(s3_exp_s_t)

        # Total for year
        s3_total_t = s3_local_t + s3_exp_n_t + s3_exp_s_t
        s3_total.append(s3_total_t)

    # Convert to Mt and add to results
    results[scenario_name] = np.array(s3_total) / 1e6  # Convert tonnes to Mt

print("✓ Calculations complete\n")

# ============================================================================
# STEP 5: DISPLAY RESULTS TABLE
# ============================================================================
print("=" * 80)
print("RESULTS TABLE: SCOPE 3 TRANSPORT EMISSIONS (Mt CO₂)")
print("=" * 80)
print()

# Show first 5, last 5, and key years
display_indices = list(range(min(5, len(results)))) + list(range(max(0, len(results)-5), len(results)))
display_indices = sorted(set(display_indices))  # Remove duplicates and sort

display_df = results.iloc[display_indices].copy()

pd.options.display.float_format = '{:.4f}'.format
print(display_df.to_string(index=False))
print()

# ============================================================================
# STEP 6: SENSITIVITY ANALYSIS
# ============================================================================
print("=" * 80)
print("SENSITIVITY ANALYSIS")
print("=" * 80)
print()

latest_idx = len(results) - 1
latest_year = int(results.loc[latest_idx, 'Year'])

print(f"Latest year ({latest_year}):")
s3_100_allowed = results.loc[latest_idx, 'S3_100_allowed']
s3_100_over = results.loc[latest_idx, 'S3_100_over']
s3_50_50 = results.loc[latest_idx, 'S3_50_50']
s3_60_40 = results.loc[latest_idx, 'S3_60_40']
s3_70_30 = results.loc[latest_idx, 'S3_70_30']

print(f"  100% allowed:    {s3_100_allowed:.4f} Mt CO₂")
print(f"  50/50 split:     {s3_50_50:.4f} Mt CO₂")
print(f"  60/40 split:     {s3_60_40:.4f} Mt CO₂")
print(f"  70/30 split:     {s3_70_30:.4f} Mt CO₂")
print(f"  100% overload:   {s3_100_over:.4f} Mt CO₂")
print()

# Range
range_value = s3_100_over - s3_100_allowed
range_pct = (range_value / s3_100_allowed) * 100
print(f"Range (100% allowed to 100% overload):")
print(f"  Absolute: {range_value:+.4f} Mt CO₂")
print(f"  Relative: {range_pct:+.1f}%")
print()

# 50/50 vs 70/30 comparison
diff_50_70 = s3_70_30 - s3_50_50
diff_50_70_pct = (diff_50_70 / s3_50_50) * 100
print(f"Comparison: 50/50 vs 70/30:")
print(f"  50/50:    {s3_50_50:.4f} Mt CO₂")
print(f"  70/30:    {s3_70_30:.4f} Mt CO₂")
print(f"  Difference: {diff_50_70:+.4f} Mt CO₂ ({diff_50_70_pct:+.1f}%)")
print()

# Historical comparison
print(f"Comparison with historical data ({latest_year}):")
if 'CO2_S3_transport_t' in df.columns:
    historical_s3 = df.loc[latest_idx, 'CO2_S3_transport_t'] / 1e6
    print(f"  Historical (60/40): {historical_s3:.4f} Mt CO₂")
    print(f"  Recalculated (60/40): {s3_60_40:.4f} Mt CO₂")
    diff_check = abs(historical_s3 - s3_60_40) / historical_s3 * 100
    print(f"  Match: {100-diff_check:.1f}% (diff: {diff_check:.2f}%)")
print()

# ============================================================================
# STEP 7: SAVE RESULTS
# ============================================================================
output_csv = 'cement_scope3_loading_sensitivity.csv'
results.to_csv(output_csv, index=False)
print(f"✓ Results saved to: {output_csv}\n")

# ============================================================================
# STEP 8: CREATE LINE CHART
# ============================================================================
fig, ax = plt.subplots(figsize=(13, 7))

colors = ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd']
markers = ['o', 's', '^', 'D', 'v']
scenario_names = ['100% Allowed', '50/50 Split', '60/40 Split', '70/30 Split', '100% Overload']
scenario_cols = ['S3_100_allowed', 'S3_50_50', 'S3_60_40', 'S3_70_30', 'S3_100_over']

for col, scenario_name, color, marker in zip(scenario_cols, scenario_names, colors, markers):
    ax.plot(results['Year'], results[col], linewidth=2.5, color=color,
            marker=marker, markersize=4, markerfacecolor=color, markeredgecolor='white',
            markeredgewidth=0.5, label=scenario_name, alpha=0.85)

# Labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Scope 3 Transport Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Scope 3 Sensitivity: Truck Loading Assumptions', fontsize=14, fontweight='bold', pad=20)

# Legend
ax.legend(loc='best', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# X-axis ticks
ax.set_xticks(range(int(results['Year'].min()), int(results['Year'].max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

plt.tight_layout()

output_plot = 'cement_scope3_loading_sensitivity.png'
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
• Scope 3 transport emissions are highly sensitive to truck loading assumptions.

• Using 100% allowed capacity (best case) vs 100% overload (worst case)
  creates a {range_pct:.1f}% spread in annual emissions.

• The difference between 50/50 and 70/30 loading splits is {abs(diff_50_70_pct):.1f}%,
  demonstrating that even small shifts in fleet composition impact total Scope 3.

• Historical baseline assumes 60/40 split, generating {s3_60_40:.4f} Mt CO₂ in {latest_year}.

• For more efficient fleet utilization, improving loaded trip fraction
  (i.e., moving from 70/30 to 50/50 split) could reduce Scope 3 by ~{abs(diff_50_70_pct):.1f}%.
""")

print()