"""
Script extracted from notebook cell 17.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# LOAD DATA
# ============================================================================
print("=" * 80)
print("FUTURE CEMENT SECTOR EMISSIONS PROJECTIONS (2024–2050)")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')
hist = hist.sort_values('year').reset_index(drop=True)
BASE_YEAR = int(hist['year'].max())

demand = pd.read_csv('cement_demand_projection_tonnes.csv')
paths = pd.read_csv('cement_decarbonization_pathways.csv')

print(f"✓ Loaded historical data: {len(hist)} years")
print(f"✓ Loaded demand projections: {len(demand)} years")
print(f"✓ Loaded pathways: {len(paths)} years\n")

# ============================================================================
# EXTRACT BASELINE VALUES & PARAMETERS
# ============================================================================
print("Extracting baseline values and transport parameters...")
print()

baseline_row = hist[hist['year'] == BASE_YEAR].iloc[0]

# Baseline intensity parameters
coal_int_base = baseline_row['coal_int_kgpt']
elec_int_base = baseline_row['elec_int_kwhpt']
clinker_ratio_base = baseline_row['clinker_ratio']
ncv_base = baseline_row['ncv']
co2_ef_coal_base = baseline_row['co2_ef_tco2_per_tj']
oxid_frac_base = baseline_row['oxid_frac']
calc_ef_base = baseline_row['calc_ef']
grid_ef_base = baseline_row['grid_ef_kg_per_kwh']

print(f"Coal intensity base:         {coal_int_base:.2f} kg/t")
print(f"Elec intensity base:         {elec_int_base:.2f} kWh/t")
print(f"Clinker ratio base:          {clinker_ratio_base:.4f}")
print(f"NCV base:                    {ncv_base:.4f} TJ/t")
print(f"CO2 combustion EF base:      {co2_ef_coal_base:.2f} tCO2/TJ")
print(f"Oxidation fraction:          {oxid_frac_base:.1f}")
print(f"Calcination EF base:         {calc_ef_base:.6f} tCO2/t clinker")
print(f"Grid EF base:                {grid_ef_base:.6f} kgCO2/kWh")
print()

# Transport parameters
cap_allowed = baseline_row['cap_allowed_t']
cap_over = baseline_row['cap_over_t']
ef_allowed_base = baseline_row['ef_allowed_gpkm']
ef_over_base = baseline_row['ef_over_gpkm']

dist_local = 250.0    # Fixed local distance (km)
dist_exp_n = 1000.0   # Fixed export north distance (km)
dist_exp_s = 200.0    # Fixed export south distance (km)

frac_allowed = 0.40
frac_over = 0.60

print(f"Transport parameters (fixed):")
print(f"  Local distance:           {dist_local:.0f} km")
print(f"  Export North distance:    {dist_exp_n:.0f} km")
print(f"  Export South distance:    {dist_exp_s:.0f} km")
print(f"  Truck cap (allowed):      {cap_allowed:.1f} t")
print(f"  Truck cap (overload):     {cap_over:.1f} t")
print(f"  EF allowed:               {ef_allowed_base:.2f} gCO2/km")
print(f"  EF overload:              {ef_over_base:.2f} gCO2/km")
print(f"  Loading split:            {frac_allowed*100:.0f}% allowed, {frac_over*100:.0f}% overload")
print()

# Extract transport flows as shares from BASE_YEAR
total_dispatch = baseline_row['cement_t']
local_flow_base = baseline_row['local_t']
exp_n_flow_base = baseline_row['exp_n_t']
exp_s_flow_base = baseline_row['exp_s_t']

local_share = local_flow_base / total_dispatch
exp_n_share = exp_n_flow_base / total_dispatch
exp_s_share = exp_s_flow_base / total_dispatch

print(f"Transport shares (from BASE_YEAR):")
print(f"  Local:        {local_share*100:5.1f}%")
print(f"  Export North: {exp_n_share*100:5.1f}%")
print(f"  Export South: {exp_s_share*100:5.1f}%")
print(f"  Total:        {(local_share + exp_n_share + exp_s_share)*100:5.1f}%")
print()

# ============================================================================
# DEFINE PATHWAY MAPPING
# ============================================================================
pathway_map = {
    'Baseline': ('coal_int_baseline', 'elec_int_baseline', 'clinker_ratio_baseline',
                 'grid_ef_baseline', 'truck_ef_allowed_baseline', 'truck_ef_over_baseline'),
    'Efficiency': ('coal_int_eff', 'elec_int_eff', 'clinker_ratio_baseline',
                   'grid_ef_baseline', 'truck_ef_allowed_baseline', 'truck_ef_over_baseline'),
    'Clinker_Reduction': ('coal_int_clinker', 'elec_int_clinker', 'clinker_ratio_clinker',
                          'grid_ef_baseline', 'truck_ef_allowed_baseline', 'truck_ef_over_baseline'),
    'Integrated': ('coal_int_integrated', 'elec_int_integrated', 'clinker_ratio_integrated',
                   'grid_ef_integrated', 'truck_ef_allowed_integrated', 'truck_ef_over_integrated'),
}

print(f"Pathways defined:")
for pathway_name in pathway_map.keys():
    print(f"  {pathway_name}")
print()

# ============================================================================
# EMISSIONS CALCULATION FUNCTION
# ============================================================================
def calculate_scope3_route(flow_t, distance_km, cap_allowed, cap_over,
                          ef_allowed, ef_over, frac_allowed, frac_over):
    """Calculate Scope 3 CO₂ for a single transport route."""
    trips_allowed = flow_t / cap_allowed
    trips_over = flow_t / cap_over
    gco2 = distance_km * (frac_allowed * trips_allowed * ef_allowed +
                          frac_over * trips_over * ef_over)
    tco2 = gco2 / 1e6
    return tco2

# ============================================================================
# COMPUTE FUTURE EMISSIONS
# ============================================================================
print("=" * 80)
print("COMPUTING FUTURE EMISSIONS...")
print("=" * 80)
print()

results_list = []
count = 0

for demand_case in ['Low', 'Med', 'High']:
    for pathway_name in pathway_map.keys():
        # Get pathway column names
        coal_int_col, elec_int_col, clinker_col, grid_ef_col, truck_ef_allowed_col, truck_ef_over_col = pathway_map[pathway_name]

        for idx, row in paths.iterrows():
            year = int(row['Year'])

            # Get demand for this year and case
            demand_row = demand[demand['Year'] == year]
            if demand_case == 'Low':
                cement_t = demand_row['Demand_Low'].values[0]
            elif demand_case == 'Med':
                cement_t = demand_row['Demand_Med'].values[0]
            else:  # High
                cement_t = demand_row['Demand_High'].values[0]

            # Get intensity parameters for this pathway
            coal_int = row[coal_int_col]
            elec_int = row[elec_int_col]
            clinker_ratio = row[clinker_col]
            grid_ef = row[grid_ef_col]
            truck_ef_allowed = row[truck_ef_allowed_col]
            truck_ef_over = row[truck_ef_over_col]

            # ========== SCOPE 1: FUEL ==========
            coal_t = cement_t * (coal_int / 1000.0)  # Convert kg to tonnes
            energy_TJ = coal_t * ncv_base
            co2_s1_fuel_t = energy_TJ * co2_ef_coal_base * oxid_frac_base

            # ========== SCOPE 1: PROCESS ==========
            clinker_t = cement_t * clinker_ratio
            co2_s1_process_t = clinker_t * calc_ef_base

            # ========== SCOPE 2: ELECTRICITY ==========
            elec_kwh = cement_t * elec_int
            co2_s2_elec_t = (elec_kwh * grid_ef) / 1000.0  # Convert kg to tonnes

            # ========== SCOPE 3: TRANSPORT ==========
            # Calculate flows based on shares
            local_flow = cement_t * local_share
            exp_n_flow = cement_t * exp_n_share
            exp_s_flow = cement_t * exp_s_share

            # Local transport
            co2_s3_local_t = calculate_scope3_route(
                local_flow, dist_local, cap_allowed, cap_over,
                truck_ef_allowed, truck_ef_over, frac_allowed, frac_over
            )

            # Export North
            co2_s3_exp_n_t = calculate_scope3_route(
                exp_n_flow, dist_exp_n, cap_allowed, cap_over,
                truck_ef_allowed, truck_ef_over, frac_allowed, frac_over
            )

            # Export South
            co2_s3_exp_s_t = calculate_scope3_route(
                exp_s_flow, dist_exp_s, cap_allowed, cap_over,
                truck_ef_allowed, truck_ef_over, frac_allowed, frac_over
            )

            # Total Scope 3
            co2_s3_transport_t = co2_s3_local_t + co2_s3_exp_n_t + co2_s3_exp_s_t

            # ========== TOTAL & INTENSITY ==========
            co2_total_t = co2_s1_fuel_t + co2_s1_process_t + co2_s2_elec_t + co2_s3_transport_t
            co2_intensity = co2_total_t / cement_t if cement_t > 0 else 0

            # Append to results
            results_list.append({
                'Year': year,
                'DemandCase': demand_case,
                'Pathway': pathway_name,
                'CO2_S1_fuel_t': co2_s1_fuel_t,
                'CO2_S1_process_t': co2_s1_process_t,
                'CO2_S2_elec_t': co2_s2_elec_t,
                'CO2_S3_transport_t': co2_s3_transport_t,
                'CO2_total_t': co2_total_t,
                'CO2_intensity': co2_intensity,
            })

            count += 1

print(f"✓ Computed {count} scenario-year combinations\n")

# Create results dataframe
results_future = pd.DataFrame(results_list)

print(f"Results dataframe shape: {results_future.shape}")
print(f"Columns: {results_future.columns.tolist()}")
print(f"Years: {int(results_future['Year'].min())} to {int(results_future['Year'].max())}")
print(f"Demand cases: {results_future['DemandCase'].unique().tolist()}")
print(f"Pathways: {results_future['Pathway'].unique().tolist()}")
print()

# ============================================================================
# DISPLAY SAMPLE RESULTS
# ============================================================================
print("=" * 80)
print("SAMPLE RESULTS (2050 projections)")
print("=" * 80)
print()

results_2050 = results_future[results_future['Year'] == 2050].copy()
results_2050_display = results_2050[['Year', 'DemandCase', 'Pathway', 'CO2_total_t', 'CO2_intensity']].copy()
results_2050_display['CO2_total_t'] = results_2050_display['CO2_total_t'] / 1e6  # Convert to Mt
results_2050_display = results_2050_display.sort_values(['DemandCase', 'Pathway'])

pd.options.display.float_format = '{:.4f}'.format
print(results_2050_display.to_string(index=False))
print()

# ============================================================================
# SCENARIO COMPARISON
# ============================================================================
print("=" * 80)
print("2050 SCENARIO COMPARISON")
print("=" * 80)
print()

for demand_case in ['Low', 'Med', 'High']:
    print(f"{demand_case} demand case:")
    subset = results_2050[results_2050['DemandCase'] == demand_case].sort_values('Pathway')

    for _, row in subset.iterrows():
        co2_mt = row['CO2_total_t'] / 1e6
        intensity = row['CO2_intensity']
        print(f"  {row['Pathway']:20s}: {co2_mt:7.2f} Mt CO₂, {intensity:.4f} tCO₂/t cement")

    # Calculate reduction from baseline
    baseline_row = subset[subset['Pathway'] == 'Baseline'].iloc[0]
    baseline_co2 = baseline_row['CO2_total_t']

    print(f"  Reductions vs baseline:")
    for _, row in subset.iterrows():
        if row['Pathway'] != 'Baseline':
            reduction = (baseline_co2 - row['CO2_total_t']) / baseline_co2 * 100
            print(f"    {row['Pathway']:20s}: {reduction:+6.1f}%")
    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
output_csv = 'outputs_future_scenarios.csv'
results_future.to_csv(output_csv, index=False)
print(f"✓ Results saved to: {output_csv}\n")

# ============================================================================
# CREATE VISUALIZATION
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Future Cement Sector Emissions Scenarios (2024–2050)',
             fontsize=15, fontweight='bold', y=0.995)

colors = {'Low': '#2ca02c', 'Med': '#ff7f0e', 'High': '#d62728'}
markers = {'Baseline': 'o', 'Efficiency': 's', 'Clinker_Reduction': '^', 'Integrated': 'd'}

# ===== Total CO2 (Mt) by Demand Case =====
ax = axes[0, 0]
for demand_case in ['Low', 'Med', 'High']:
    subset = results_future[results_future['DemandCase'] == demand_case]
    baseline_subset = subset[subset['Pathway'] == 'Baseline']
    ax.plot(baseline_subset['Year'], baseline_subset['CO2_total_t'] / 1e6,
            marker='o', linewidth=2, label=f"{demand_case} demand", color=colors[demand_case])
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Total CO₂ (Mt)', fontweight='bold')
ax.set_title('Total Emissions by Demand Case (Baseline Pathway)', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Total CO2 (Mt) by Pathway =====
ax = axes[0, 1]
for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    subset = results_future[(results_future['DemandCase'] == 'Med') &
                            (results_future['Pathway'] == pathway)]
    ax.plot(subset['Year'], subset['CO2_total_t'] / 1e6,
            marker=markers[pathway], linewidth=2, label=pathway)
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Total CO₂ (Mt)', fontweight='bold')
ax.set_title('Total Emissions by Pathway (Medium Demand)', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Carbon Intensity by Demand =====
ax = axes[1, 0]
for demand_case in ['Low', 'Med', 'High']:
    subset = results_future[results_future['DemandCase'] == demand_case]
    baseline_subset = subset[subset['Pathway'] == 'Baseline']
    ax.plot(baseline_subset['Year'], baseline_subset['CO2_intensity'],
            marker='o', linewidth=2, label=f"{demand_case} demand", color=colors[demand_case])
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Carbon Intensity (tCO₂/t cement)', fontweight='bold')
ax.set_title('Carbon Intensity by Demand Case (Baseline Pathway)', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Carbon Intensity by Pathway =====
ax = axes[1, 1]
for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    subset = results_future[(results_future['DemandCase'] == 'Med') &
                            (results_future['Pathway'] == pathway)]
    ax.plot(subset['Year'], subset['CO2_intensity'],
            marker=markers[pathway], linewidth=2, label=pathway)
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Carbon Intensity (tCO₂/t cement)', fontweight='bold')
ax.set_title('Carbon Intensity by Pathway (Medium Demand)', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()

output_plot = 'cement_future_scenarios.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Visualization saved to: {output_plot}\n")

plt.show()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print()

print(f"Total scenarios: {len(results_future)}")
print(f"  Years: {len(results_future['Year'].unique())}")
print(f"  Demand cases: {len(results_future['DemandCase'].unique())}")
print(f"  Pathways: {len(results_future['Pathway'].unique())}")
print(f"  Combinations: {len(results_future['Year'].unique())} × {len(results_future['DemandCase'].unique())} × {len(results_future['Pathway'].unique())} = {len(results_future)}")
print()

# 2050 extremes
results_2050 = results_future[results_future['Year'] == 2050]

co2_max = results_2050['CO2_total_t'].max()
co2_max_row = results_2050[results_2050['CO2_total_t'] == co2_max].iloc[0]

co2_min = results_2050['CO2_total_t'].min()
co2_min_row = results_2050[results_2050['CO2_total_t'] == co2_min].iloc[0]

print(f"2050 extremes:")
print(f"  Maximum CO₂:  {co2_max/1e6:.2f} Mt ({co2_max_row['DemandCase']} demand, {co2_max_row['Pathway']})")
print(f"  Minimum CO₂:  {co2_min/1e6:.2f} Mt ({co2_min_row['DemandCase']} demand, {co2_min_row['Pathway']})")
print(f"  Range:        {(co2_max - co2_min)/1e6:.2f} Mt ({((co2_max - co2_min)/co2_min)*100:.0f}% spread)")
print()

# Intensity extremes
intensity_max = results_2050['CO2_intensity'].max()
intensity_max_row = results_2050[results_2050['CO2_intensity'] == intensity_max].iloc[0]

intensity_min = results_2050['CO2_intensity'].min()
intensity_min_row = results_2050[results_2050['CO2_intensity'] == intensity_min].iloc[0]

print(f"2050 carbon intensity extremes:")
print(f"  Maximum: {intensity_max:.4f} tCO₂/t ({intensity_max_row['DemandCase']} demand, {intensity_max_row['Pathway']})")
print(f"  Minimum: {intensity_min:.4f} tCO₂/t ({intensity_min_row['DemandCase']} demand, {intensity_min_row['Pathway']})")
print()

print("=" * 80)
print("✓ Future emissions projections complete")
print("=" * 80)
print()