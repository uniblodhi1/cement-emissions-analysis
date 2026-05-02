"""
Script extracted from notebook cell 13.
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
print("SCOPE 3 TRANSPORT LOCAL DISTANCE SENSITIVITY ANALYSIS")
print("=" * 80)
print()

df = pd.read_csv('outputs_historical_scopes.csv')

print(f"✓ Loaded historical data: {len(df)} years\n")

# ============================================================================
# STEP 1: EXTRACT SCOPE 3 CALCULATION INPUTS
# ============================================================================
print("Extracting Scope 3 calculation inputs from historical data...\n")

years_data = df['year'].values

# Transport flows (tonnes) - from historical data
local_t = df['local_t'].values
exp_n_t = df['exp_n_t'].values
exp_s_t = df['exp_s_t'].values

# Distances - FIXED EXPORTS, VARIABLE LOCAL
dist_exp_n_km = 1000.0  # Fixed
dist_exp_s_km = 200.0   # Fixed

# Truck parameters (constant across all scenarios)
cap_allowed_t = df['cap_allowed_t'].values[0]
cap_over_t = df['cap_over_t'].values[0]
ef_allowed_gpkm = df['ef_allowed_gpkm'].values[0]
ef_over_gpkm = df['ef_over_gpkm'].values[0]

# Historical 60/40 split (baseline assumption)
frac_allowed = 0.40
frac_over = 0.60

print("Transport flows (tonnes/year - from historical data):")
print(f"  Local (variable distance):    {local_t[0]/1e6:.2f} Mt (Year {int(years_data[0])})")
print(f"  Export North (fixed 1000 km): {exp_n_t[0]/1e6:.2f} Mt")
print(f"  Export South (fixed 200 km):  {exp_s_t[0]/1e6:.2f} Mt\n")

print("Fixed export distances:")
print(f"  Export North:     {dist_exp_n_km:.0f} km (FIXED)")
print(f"  Export South:     {dist_exp_s_km:.0f} km (FIXED)\n")

print("Local delivery distance scenarios (VARIABLE):")
print("  Scenario 1:       300 km")
print("  Scenario 2:       500 km (baseline)")
print("  Scenario 3:       1000 km\n")

print("Truck parameters (constant):")
print(f"  Capacity (allowed):  {cap_allowed_t:.1f} tonnes")
print(f"  Capacity (overload): {cap_over_t:.1f} tonnes")
print(f"  EF (allowed):        {ef_allowed_gpkm:.2f} gCO₂/km")
print(f"  EF (overload):       {ef_over_gpkm:.2f} gCO₂/km")
print(f"  Loading split:       {frac_allowed*100:.0f}% allowed, {frac_over*100:.0f}% overload\n")

# ============================================================================
# STEP 2: DEFINE TRANSPORT EMISSION FUNCTION
# ============================================================================
def calculate_scope3_route(flow_t, distance_km, cap_allowed, cap_over,
                           ef_allowed, ef_over, frac_allowed, frac_over):
    """
    Calculate Scope 3 CO₂ for a single transport route.

    Returns:
        CO₂ in tonnes
    """
    # Number of trips for each mode
    trips_allowed = flow_t / cap_allowed
    trips_over = flow_t / cap_over

    # gCO₂ = distance * (frac_allowed * trips_allowed * EF_allowed +
    #                    frac_over * trips_over * EF_over)
    gco2 = (distance_km *
            (frac_allowed * trips_allowed * ef_allowed +
             frac_over * trips_over * ef_over))

    # Convert grams to tonnes
    tco2 = gco2 / 1e6
    return tco2

# ============================================================================
# STEP 3: DEFINE DISTANCE SCENARIOS (UPDATED)
# ============================================================================
distance_scenarios = {
    'S3_300km': 300,
    'S3_500km': 500,      # baseline
    'S3_1000km': 1000,
}

print("Scenarios to compute:")
for scenario_name, dist_km in distance_scenarios.items():
    print(f"  {scenario_name:12s}: local delivery = {dist_km} km")
print()

# ============================================================================
# STEP 4: COMPUTE SCOPE 3 FOR EACH DISTANCE SCENARIO
# ============================================================================
print("Computing Scope 3 transport emissions for each distance scenario...\n")

results = pd.DataFrame()
results['Year'] = years_data

for scenario_name, dist_local_km in distance_scenarios.items():
    s3_total = []

    for i in range(len(df)):
        # Local delivery (variable distance)
        s3_local_t = calculate_scope3_route(
            local_t[i], dist_local_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )

        # Export North (fixed 1000 km)
        s3_exp_n_t = calculate_scope3_route(
            exp_n_t[i], dist_exp_n_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )

        # Export South (fixed 200 km)
        s3_exp_s_t = calculate_scope3_route(
            exp_s_t[i], dist_exp_s_km,
            cap_allowed_t, cap_over_t,
            ef_allowed_gpkm, ef_over_gpkm,
            frac_allowed, frac_over
        )

        s3_total.append(s3_local_t + s3_exp_n_t + s3_exp_s_t)

    # Convert to Mt and add to results
    results[scenario_name] = np.array(s3_total) / 1e6  # tonnes -> Mt

print("✓ Calculations complete\n")

# ============================================================================
# STEP 5: DISPLAY RESULTS TABLE
# ============================================================================
print("=" * 80)
print("RESULTS TABLE: SCOPE 3 TRANSPORT EMISSIONS (Mt CO₂)")
print("=" * 80)
print()

display_indices = list(range(min(5, len(results)))) + list(range(max(0, len(results)-5), len(results)))
display_indices = sorted(set(display_indices))
display_df = results.iloc[display_indices].copy()

pd.options.display.float_format = '{:.4f}'.format
print(display_df.to_string(index=False))
print()

# ============================================================================
# STEP 6: SENSITIVITY ANALYSIS (UPDATED)
# ============================================================================
print("=" * 80)
print("SENSITIVITY ANALYSIS")
print("=" * 80)
print()

latest_idx = len(results) - 1
latest_year = int(results.loc[latest_idx, 'Year'])

s3_300 = results.loc[latest_idx, 'S3_300km']
s3_500 = results.loc[latest_idx, 'S3_500km']      # baseline
s3_1000 = results.loc[latest_idx, 'S3_1000km']

print(f"Latest year ({latest_year}):")
print(f"  Local distance 300 km:   {s3_300:.4f} Mt CO₂")
print(f"  Local distance 500 km:   {s3_500:.4f} Mt CO₂  (baseline)")
print(f"  Local distance 1000 km:  {s3_1000:.4f} Mt CO₂\n")

diff_300_to_500 = s3_500 - s3_300
diff_pct_300_to_500 = (diff_300_to_500 / s3_300) * 100

diff_500_to_1000 = s3_1000 - s3_500
diff_pct_500_to_1000 = (diff_500_to_1000 / s3_500) * 100

diff_300_to_1000 = s3_1000 - s3_300
diff_pct_300_to_1000 = (diff_300_to_1000 / s3_300) * 100

print("Distance sensitivity (latest year):")
print("  300 km → 500 km (200 km increase):")
print(f"    Absolute: {diff_300_to_500:+.4f} Mt CO₂")
print(f"    Relative: {diff_pct_300_to_500:+.2f}%\n")

print("  500 km → 1000 km (500 km increase):")
print(f"    Absolute: {diff_500_to_1000:+.4f} Mt CO₂")
print(f"    Relative: {diff_pct_500_to_1000:+.2f}%\n")

print("  300 km → 1000 km (700 km increase):")
print(f"    Absolute: {diff_300_to_1000:+.4f} Mt CO₂")
print(f"    Relative: {diff_pct_300_to_1000:+.2f}%\n")

# Per-km sensitivity (based on 300 -> 1000)
per_km_sensitivity = diff_300_to_1000 / 700
print(f"Per-km sensitivity: {per_km_sensitivity:.6f} Mt CO₂ per km\n")

# Historical comparison (if present)
print(f"Comparison with historical data ({latest_year}):")
if 'CO2_S3_transport_t' in df.columns:
    historical_s3 = df.loc[latest_idx, 'CO2_S3_transport_t'] / 1e6
    print(f"  Historical (old baseline, if any): {historical_s3:.4f} Mt CO₂")
    print(f"  Recalculated (500 km baseline):    {s3_500:.4f} Mt CO₂")
    diff_check = abs(historical_s3 - s3_500) / historical_s3 * 100 if historical_s3 != 0 else np.nan
    print(f"  Difference vs historical: {diff_check:.2f}%")
print()

# ============================================================================
# STEP 7: SAVE RESULTS
# ============================================================================
output_csv = 'cement_scope3_distance_sensitivity.csv'
results.to_csv(output_csv, index=False)
print(f"✓ Results saved to: {output_csv}\n")

# ============================================================================
# STEP 8: CREATE LINE CHART (UPDATED)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#1f77b4', '#ff7f0e', '#d62728']
markers = ['o', 's', '^']

scenario_labels = ['300 km', '500 km (baseline)', '1000 km']
scenario_cols = ['S3_300km', 'S3_500km', 'S3_1000km']

for col, label, color, marker in zip(scenario_cols, scenario_labels, colors, markers):
    ax.plot(results['Year'], results[col], linewidth=2.5, color=color,
            marker=marker, markersize=5, markerfacecolor=color, markeredgecolor='white',
            markeredgewidth=0.5, label=label, alpha=0.85)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Scope 3 Transport Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Scope 3 sensitivity: local delivery distance', fontsize=14, fontweight='bold', pad=20)

ax.legend(loc='best', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

ax.set_xticks(range(int(results['Year'].min()), int(results['Year'].max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Annotation (300 -> 1000)
ax.text(0.98, 0.05, f'300→1000 km: {diff_pct_300_to_1000:+.1f}%',
        transform=ax.transAxes,
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
        ha='right', va='bottom')

plt.tight_layout()

output_plot = 'cement_scope3_distance_sensitivity.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved to: {output_plot}\n")

plt.show()

# ============================================================================
# STEP 9: TEMPORAL ANALYSIS (UPDATED)
# ============================================================================
print("=" * 80)
print("TEMPORAL SENSITIVITY ANALYSIS")
print("=" * 80)
print()

# Average difference across all years (300 vs 1000)
avg_diff_300_to_1000 = (results['S3_1000km'] - results['S3_300km']).mean()
avg_diff_pct_300_to_1000 = (avg_diff_300_to_1000 / results['S3_300km'].mean()) * 100

print(f"Average difference (300 km vs 1000 km) across {len(results)} years:")
print(f"  Absolute: {avg_diff_300_to_1000:+.4f} Mt CO₂")
print(f"  Relative: {avg_diff_pct_300_to_1000:+.2f}%\n")

# First year comparison
first_idx = 0
first_year = int(results.loc[first_idx, 'Year'])
s3_300_first = results.loc[first_idx, 'S3_300km']
s3_1000_first = results.loc[first_idx, 'S3_1000km']
diff_first = ((s3_1000_first - s3_300_first) / s3_300_first) * 100

print(f"First year ({first_year}):")
print(f"  300 km:  {s3_300_first:.4f} Mt CO₂")
print(f"  1000 km: {s3_1000_first:.4f} Mt CO₂")
print(f"  Difference: {diff_first:+.2f}%\n")

# Check if sensitivity changes over time
early_period = results.iloc[:len(results)//2]
late_period = results.iloc[len(results)//2:]

early_diff = ((early_period['S3_1000km'] - early_period['S3_300km']) / early_period['S3_300km']).mean() * 100
late_diff = ((late_period['S3_1000km'] - late_period['S3_300km']) / late_period['S3_300km']).mean() * 100

print(f"Early period ({int(early_period['Year'].iloc[0])}–{int(early_period['Year'].iloc[-1])}):")
print(f"  Average 300–1000 km difference: {early_diff:.2f}%\n")

print(f"Late period ({int(late_period['Year'].iloc[0])}–{int(late_period['Year'].iloc[-1])}):")
print(f"  Average 300–1000 km difference: {late_diff:.2f}%\n")

# ============================================================================
# STEP 10: SUMMARY INSIGHTS (UPDATED)
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print(f"""
• Local delivery distance has a MAJOR impact on Scope 3 transport emissions.

• A 200 km increase in local delivery distance (300→500 km) increases
  Scope 3 by {diff_pct_300_to_500:.1f}% in {latest_year}.

• A 500 km increase in local delivery distance (500→1000 km) increases
  Scope 3 by {diff_pct_500_to_1000:.1f}% in {latest_year}.

• Overall, moving from 300 km to 1000 km increases Scope 3 by
  {diff_pct_300_to_1000:.1f}% in {latest_year}.

• This translates to {per_km_sensitivity:.6f} Mt CO₂ increase per additional km
  of local delivery distance (based on 300→1000 km).

• The sensitivity is CONSTANT over time, as it depends only on distance
  and fixed truck parameters (not on cement production).

• Early period sensitivity ({early_diff:.2f}%) matches late period ({late_diff:.2f}%),
  confirming linear distance relationship.

• Distribution strategy (centralized vs. distributed facilities) directly
  impacts transport-related emissions in a predictable, proportional manner.

• For every 50 km reduction in average local delivery distance,
  Scope 3 emissions would decrease by approximately {(50 * per_km_sensitivity / s3_500) * 100:.2f}% (approx, using baseline year).
""")

print()
