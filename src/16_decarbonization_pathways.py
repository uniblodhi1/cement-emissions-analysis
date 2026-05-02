"""
Script extracted from notebook cell 16.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# LOAD HISTORICAL DATA AND GET BASELINE
# ============================================================================
print("=" * 80)
print("CEMENT SECTOR DECARBONIZATION PATHWAYS (2024–2050)")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')

# Sort by year and get base year
hist = hist.sort_values('year').reset_index(drop=True)
BASE_YEAR = int(hist['year'].max())

print(f"Base year: {BASE_YEAR}\n")

# ============================================================================
# EXTRACT BASELINE VALUES
# ============================================================================
print("Extracting baseline values from BASE_YEAR...")
print()

baseline_row = hist[hist['year'] == BASE_YEAR].iloc[0]

# Extract baseline values with error handling
baseline = {}

# Coal intensity (kg/t)
if 'coal_int_kgpt' in hist.columns:
    baseline['coal_int'] = baseline_row['coal_int_kgpt']
    print(f"✓ Coal intensity baseline:      {baseline['coal_int']:.2f} kg/t")
else:
    print("ERROR: 'coal_int_kgpt' not found")
    exit()

# Electricity intensity (kWh/t)
if 'elec_int_kwhpt' in hist.columns:
    baseline['elec_int'] = baseline_row['elec_int_kwhpt']
    print(f"✓ Electricity intensity baseline: {baseline['elec_int']:.2f} kWh/t")
else:
    print("ERROR: 'elec_int_kwhpt' not found")
    exit()

# Clinker ratio (fraction)
if 'clinker_ratio' in hist.columns:
    baseline['clinker_ratio'] = baseline_row['clinker_ratio']
    print(f"✓ Clinker ratio baseline:       {baseline['clinker_ratio']:.4f}")
else:
    print("ERROR: 'clinker_ratio' not found")
    exit()

# Grid EF (kgCO2/kWh)
if 'grid_ef_kg_per_kwh' in hist.columns:
    baseline['grid_ef'] = baseline_row['grid_ef_kg_per_kwh']
    print(f"✓ Grid EF baseline:             {baseline['grid_ef']:.6f} kgCO2/kWh")
else:
    print("ERROR: 'grid_ef_kg_per_kwh' not found")
    exit()

# Truck EF - allowed (gCO2/km)
if 'ef_allowed_gpkm' in hist.columns:
    baseline['truck_ef_allowed'] = baseline_row['ef_allowed_gpkm']
    print(f"✓ Truck EF (allowed) baseline:  {baseline['truck_ef_allowed']:.2f} gCO2/km")
else:
    print("ERROR: 'ef_allowed_gpkm' not found")
    exit()

# Truck EF - overload (gCO2/km)
if 'ef_over_gpkm' in hist.columns:
    baseline['truck_ef_over'] = baseline_row['ef_over_gpkm']
    print(f"✓ Truck EF (overload) baseline: {baseline['truck_ef_over']:.2f} gCO2/km")
else:
    print("ERROR: 'ef_over_gpkm' not found")
    exit()

print()

# ============================================================================
# DEFINE PROJECTION YEARS AND PATHWAYS
# ============================================================================
start_year = BASE_YEAR + 1
end_year = 2050
projection_years = np.arange(start_year, end_year + 1)

print(f"Projection period: {start_year} to {end_year} ({len(projection_years)} years)\n")

# ============================================================================
# DEFINE PATHWAY PARAMETERS
# ============================================================================
print("Pathway definitions:")
print()

# Coal intensity pathways
print("COAL INTENSITY (kg/t cement):")
print("  Baseline:    No change (constant)")
print("  Efficiency:  1.8% annual decline")
print("  Clinker:     1.0% annual decline (clinker ratio optimization)")
print("  Integrated:  1.0% annual decline (combined with clinker)")
print()

# Electricity intensity pathways
print("ELECTRICITY INTENSITY (kWh/t cement):")
print("  Baseline:    No change (constant)")
print("  Efficiency:  2.0% annual decline")
print("  Clinker:     1.2% annual decline (clinker ratio optimization)")
print("  Integrated:  1.2% annual decline (combined with clinker)")
print()

# Clinker ratio pathways
print("CLINKER RATIO (fraction):")
print("  Baseline:    No change (constant)")
print("  Clinker:     Linear decline to 0.75 by 2050 (substitution)")
print("  Integrated:  Linear decline to 0.75 by 2050 (full integration)")
print()

# Grid EF pathways
print("GRID EMISSION FACTOR (kgCO2/kWh):")
print("  Baseline:    No change (constant)")
print("  Integrated:  2.0% annual decline (grid decarbonization)")
print()

# Truck EF pathways
print("TRUCK EF (gCO2/km) - applied to both allowed & overload:")
print("  Baseline:    No change (constant)")
print("  Integrated:  0.5% annual decline (fleet efficiency)")
print()

# ============================================================================
# CALCULATE PATHWAYS
# ============================================================================
print("=" * 80)
print("CALCULATING PATHWAYS...")
print("=" * 80)
print()

# Floor value to prevent negative values
FLOOR = 1e-6

paths_data = {
    'Year': projection_years,
    # Coal intensity pathways
    'coal_int_baseline': [],
    'coal_int_eff': [],
    'coal_int_clinker': [],
    'coal_int_integrated': [],
    # Electricity intensity pathways
    'elec_int_baseline': [],
    'elec_int_eff': [],
    'elec_int_clinker': [],
    'elec_int_integrated': [],
    # Clinker ratio pathways
    'clinker_ratio_baseline': [],
    'clinker_ratio_clinker': [],
    'clinker_ratio_integrated': [],
    # Grid EF pathways
    'grid_ef_baseline': [],
    'grid_ef_integrated': [],
    # Truck EF pathways
    'truck_ef_allowed_baseline': [],
    'truck_ef_allowed_integrated': [],
    'truck_ef_over_baseline': [],
    'truck_ef_over_integrated': [],
}

for year in projection_years:
    years_from_base = year - BASE_YEAR

    # ========== COAL INTENSITY ==========
    # Baseline: constant
    coal_int_baseline = baseline['coal_int']
    paths_data['coal_int_baseline'].append(coal_int_baseline)

    # Efficiency: 1.8% annual decline
    coal_int_eff = baseline['coal_int'] * (1 - 0.018) ** years_from_base
    coal_int_eff = max(coal_int_eff, FLOOR)
    paths_data['coal_int_eff'].append(coal_int_eff)

    # Clinker: 1.0% annual decline (through clinker ratio improvement, see below)
    # Here we show the intensity declining, but clinker ratio is what actually changes
    coal_int_clinker = baseline['coal_int'] * (1 - 0.01) ** years_from_base
    coal_int_clinker = max(coal_int_clinker, FLOOR)
    paths_data['coal_int_clinker'].append(coal_int_clinker)

    # Integrated: 1.0% annual decline
    coal_int_integrated = baseline['coal_int'] * (1 - 0.01) ** years_from_base
    coal_int_integrated = max(coal_int_integrated, FLOOR)
    paths_data['coal_int_integrated'].append(coal_int_integrated)

    # ========== ELECTRICITY INTENSITY ==========
    # Baseline: constant
    elec_int_baseline = baseline['elec_int']
    paths_data['elec_int_baseline'].append(elec_int_baseline)

    # Efficiency: 2.0% annual decline
    elec_int_eff = baseline['elec_int'] * (1 - 0.02) ** years_from_base
    elec_int_eff = max(elec_int_eff, FLOOR)
    paths_data['elec_int_eff'].append(elec_int_eff)

    # Clinker: 1.2% annual decline (clinker ratio optimization)
    elec_int_clinker = baseline['elec_int'] * (1 - 0.012) ** years_from_base
    elec_int_clinker = max(elec_int_clinker, FLOOR)
    paths_data['elec_int_clinker'].append(elec_int_clinker)

    # Integrated: 1.2% annual decline
    elec_int_integrated = baseline['elec_int'] * (1 - 0.012) ** years_from_base
    elec_int_integrated = max(elec_int_integrated, FLOOR)
    paths_data['elec_int_integrated'].append(elec_int_integrated)

    # ========== CLINKER RATIO ==========
    # Baseline: constant
    clinker_ratio_baseline = baseline['clinker_ratio']
    paths_data['clinker_ratio_baseline'].append(clinker_ratio_baseline)

    # Clinker pathway: linear decline from baseline to 0.75 by 2050
    # Target: 0.75, Years available: 2050 - BASE_YEAR = (end_year - BASE_YEAR)
    total_years = end_year - BASE_YEAR
    clinker_decline_per_year = (baseline['clinker_ratio'] - 0.75) / total_years
    clinker_ratio_clinker = baseline['clinker_ratio'] - (clinker_decline_per_year * years_from_base)
    clinker_ratio_clinker = max(clinker_ratio_clinker, 0.75)  # Floor at target
    paths_data['clinker_ratio_clinker'].append(clinker_ratio_clinker)

    # Integrated: same as clinker pathway
    clinker_ratio_integrated = baseline['clinker_ratio'] - (clinker_decline_per_year * years_from_base)
    clinker_ratio_integrated = max(clinker_ratio_integrated, 0.75)
    paths_data['clinker_ratio_integrated'].append(clinker_ratio_integrated)

    # ========== GRID EMISSION FACTOR ==========
    # Baseline: constant
    grid_ef_baseline = baseline['grid_ef']
    paths_data['grid_ef_baseline'].append(grid_ef_baseline)

    # Integrated: 2.0% annual decline (grid decarbonization)
    grid_ef_integrated = baseline['grid_ef'] * (1 - 0.02) ** years_from_base
    grid_ef_integrated = max(grid_ef_integrated, FLOOR)
    paths_data['grid_ef_integrated'].append(grid_ef_integrated)

    # ========== TRUCK EF - ALLOWED ==========
    # Baseline: constant
    truck_ef_allowed_baseline = baseline['truck_ef_allowed']
    paths_data['truck_ef_allowed_baseline'].append(truck_ef_allowed_baseline)

    # Integrated: 0.5% annual decline (fleet efficiency)
    truck_ef_allowed_integrated = baseline['truck_ef_allowed'] * (1 - 0.005) ** years_from_base
    truck_ef_allowed_integrated = max(truck_ef_allowed_integrated, FLOOR)
    paths_data['truck_ef_allowed_integrated'].append(truck_ef_allowed_integrated)

    # ========== TRUCK EF - OVERLOAD ==========
    # Baseline: constant
    truck_ef_over_baseline = baseline['truck_ef_over']
    paths_data['truck_ef_over_baseline'].append(truck_ef_over_baseline)

    # Integrated: 0.5% annual decline (same as allowed)
    truck_ef_over_integrated = baseline['truck_ef_over'] * (1 - 0.005) ** years_from_base
    truck_ef_over_integrated = max(truck_ef_over_integrated, FLOOR)
    paths_data['truck_ef_over_integrated'].append(truck_ef_over_integrated)

# Create dataframe
paths = pd.DataFrame(paths_data)

print("✓ Pathways calculated successfully\n")

# ============================================================================
# DISPLAY RESULTS
# ============================================================================
print("=" * 80)
print("DECARBONIZATION PATHWAYS - SELECTED YEARS")
print("=" * 80)
print()

# Show key years
display_years = [BASE_YEAR]
display_years.extend(range(start_year, end_year + 1, 10))
if end_year not in display_years:
    display_years.append(end_year)

display_indices = []
for year in display_years:
    if year >= start_year:
        idx = paths[paths['Year'] == year].index
        if len(idx) > 0:
            display_indices.append(idx[0])

display_indices = sorted(set(display_indices))

# Add base year for reference
base_year_row = pd.DataFrame({
    'Year': [BASE_YEAR],
    'coal_int_baseline': [baseline['coal_int']],
    'coal_int_eff': [baseline['coal_int']],
    'coal_int_clinker': [baseline['coal_int']],
    'coal_int_integrated': [baseline['coal_int']],
})

print("COAL INTENSITY (kg/t):")
display_coal = pd.concat([
    base_year_row[['Year', 'coal_int_baseline', 'coal_int_eff', 'coal_int_clinker', 'coal_int_integrated']],
    paths.iloc[display_indices][['Year', 'coal_int_baseline', 'coal_int_eff', 'coal_int_clinker', 'coal_int_integrated']]
], ignore_index=True)
pd.options.display.float_format = '{:.1f}'.format
print(display_coal.to_string(index=False))
print()

print("ELECTRICITY INTENSITY (kWh/t):")
display_elec = pd.concat([
    pd.DataFrame({
        'Year': [BASE_YEAR],
        'elec_int_baseline': [baseline['elec_int']],
        'elec_int_eff': [baseline['elec_int']],
        'elec_int_clinker': [baseline['elec_int']],
        'elec_int_integrated': [baseline['elec_int']],
    }),
    paths.iloc[display_indices][['Year', 'elec_int_baseline', 'elec_int_eff', 'elec_int_clinker', 'elec_int_integrated']]
], ignore_index=True)
print(display_elec.to_string(index=False))
print()

print("CLINKER RATIO (fraction):")
display_clinker = pd.concat([
    pd.DataFrame({
        'Year': [BASE_YEAR],
        'clinker_ratio_baseline': [baseline['clinker_ratio']],
        'clinker_ratio_clinker': [baseline['clinker_ratio']],
        'clinker_ratio_integrated': [baseline['clinker_ratio']],
    }),
    paths.iloc[display_indices][['Year', 'clinker_ratio_baseline', 'clinker_ratio_clinker', 'clinker_ratio_integrated']]
], ignore_index=True)
pd.options.display.float_format = '{:.4f}'.format
print(display_clinker.to_string(index=False))
print()

print("GRID EMISSION FACTOR (kgCO2/kWh):")
display_grid = pd.concat([
    pd.DataFrame({
        'Year': [BASE_YEAR],
        'grid_ef_baseline': [baseline['grid_ef']],
        'grid_ef_integrated': [baseline['grid_ef']],
    }),
    paths.iloc[display_indices][['Year', 'grid_ef_baseline', 'grid_ef_integrated']]
], ignore_index=True)
pd.options.display.float_format = '{:.6f}'.format
print(display_grid.to_string(index=False))
print()

# ============================================================================
# PATHWAY COMPARISON (2050)
# ============================================================================
print("=" * 80)
print(f"2050 COMPARISON (% change from {BASE_YEAR})")
print("=" * 80)
print()

final_idx = len(paths) - 1

# Coal intensity
coal_baseline_2050 = paths.loc[final_idx, 'coal_int_baseline']
coal_eff_2050 = paths.loc[final_idx, 'coal_int_eff']
coal_clinker_2050 = paths.loc[final_idx, 'coal_int_clinker']
coal_integrated_2050 = paths.loc[final_idx, 'coal_int_integrated']

print("Coal intensity:")
print(f"  Baseline:    {baseline['coal_int']:.1f} kg/t (no change)")
print(f"  Efficiency:  {coal_eff_2050:.1f} kg/t ({((coal_eff_2050/baseline['coal_int'])-1)*100:+.1f}%)")
print(f"  Clinker:     {coal_clinker_2050:.1f} kg/t ({((coal_clinker_2050/baseline['coal_int'])-1)*100:+.1f}%)")
print(f"  Integrated:  {coal_integrated_2050:.1f} kg/t ({((coal_integrated_2050/baseline['coal_int'])-1)*100:+.1f}%)")
print()

# Electricity intensity
elec_baseline_2050 = paths.loc[final_idx, 'elec_int_baseline']
elec_eff_2050 = paths.loc[final_idx, 'elec_int_eff']
elec_clinker_2050 = paths.loc[final_idx, 'elec_int_clinker']
elec_integrated_2050 = paths.loc[final_idx, 'elec_int_integrated']

print("Electricity intensity:")
print(f"  Baseline:    {baseline['elec_int']:.1f} kWh/t (no change)")
print(f"  Efficiency:  {elec_eff_2050:.1f} kWh/t ({((elec_eff_2050/baseline['elec_int'])-1)*100:+.1f}%)")
print(f"  Clinker:     {elec_clinker_2050:.1f} kWh/t ({((elec_clinker_2050/baseline['elec_int'])-1)*100:+.1f}%)")
print(f"  Integrated:  {elec_integrated_2050:.1f} kWh/t ({((elec_integrated_2050/baseline['elec_int'])-1)*100:+.1f}%)")
print()

# Clinker ratio
clinker_baseline_2050 = paths.loc[final_idx, 'clinker_ratio_baseline']
clinker_pathway_2050 = paths.loc[final_idx, 'clinker_ratio_clinker']
clinker_integrated_2050 = paths.loc[final_idx, 'clinker_ratio_integrated']

print("Clinker ratio:")
print(f"  Baseline:    {clinker_baseline_2050:.4f} (no change)")
print(f"  Clinker:     {clinker_pathway_2050:.4f} (linear to 0.75)")
print(f"  Integrated:  {clinker_integrated_2050:.4f} (linear to 0.75)")
print()

# Grid EF
grid_baseline_2050 = paths.loc[final_idx, 'grid_ef_baseline']
grid_integrated_2050 = paths.loc[final_idx, 'grid_ef_integrated']

print("Grid EF:")
print(f"  Baseline:    {grid_baseline_2050:.6f} kgCO2/kWh (no change)")
print(f"  Integrated:  {grid_integrated_2050:.6f} kgCO2/kWh ({((grid_integrated_2050/baseline['grid_ef'])-1)*100:+.1f}%)")
print()

# Truck EF
truck_ef_allowed_baseline_2050 = paths.loc[final_idx, 'truck_ef_allowed_baseline']
truck_ef_allowed_integrated_2050 = paths.loc[final_idx, 'truck_ef_allowed_integrated']
truck_ef_over_baseline_2050 = paths.loc[final_idx, 'truck_ef_over_baseline']
truck_ef_over_integrated_2050 = paths.loc[final_idx, 'truck_ef_over_integrated']

print("Truck EF (allowed):")
print(f"  Baseline:    {truck_ef_allowed_baseline_2050:.2f} gCO2/km (no change)")
print(f"  Integrated:  {truck_ef_allowed_integrated_2050:.2f} gCO2/km ({((truck_ef_allowed_integrated_2050/baseline['truck_ef_allowed'])-1)*100:+.1f}%)")
print()

print("Truck EF (overload):")
print(f"  Baseline:    {truck_ef_over_baseline_2050:.2f} gCO2/km (no change)")
print(f"  Integrated:  {truck_ef_over_integrated_2050:.2f} gCO2/km ({((truck_ef_over_integrated_2050/baseline['truck_ef_over'])-1)*100:+.1f}%)")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
output_csv = 'cement_decarbonization_pathways.csv'
paths.to_csv(output_csv, index=False)
print(f"✓ Pathways saved to: {output_csv}\n")

# ============================================================================
# CREATE VISUALIZATION
# ============================================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Cement Sector Decarbonization Pathways to 2050', fontsize=16, fontweight='bold', y=0.995)

# ===== Coal Intensity =====
ax = axes[0, 0]
ax.plot(paths['Year'], paths['coal_int_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['coal_int_eff'], 's-', linewidth=2, label='Efficiency (1.8%/yr)', color='#ff7f0e')
ax.plot(paths['Year'], paths['coal_int_clinker'], '^-', linewidth=2, label='Clinker (1%/yr)', color='#2ca02c')
ax.plot(paths['Year'], paths['coal_int_integrated'], 'd-', linewidth=2, label='Integrated (1%/yr)', color='#d62728')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('kg/t cement', fontweight='bold')
ax.set_title('Coal Intensity', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Electricity Intensity =====
ax = axes[0, 1]
ax.plot(paths['Year'], paths['elec_int_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['elec_int_eff'], 's-', linewidth=2, label='Efficiency (2%/yr)', color='#ff7f0e')
ax.plot(paths['Year'], paths['elec_int_clinker'], '^-', linewidth=2, label='Clinker (1.2%/yr)', color='#2ca02c')
ax.plot(paths['Year'], paths['elec_int_integrated'], 'd-', linewidth=2, label='Integrated (1.2%/yr)', color='#d62728')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('kWh/t cement', fontweight='bold')
ax.set_title('Electricity Intensity', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Clinker Ratio =====
ax = axes[0, 2]
ax.plot(paths['Year'], paths['clinker_ratio_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['clinker_ratio_clinker'], 's-', linewidth=2, label='Clinker pathway', color='#2ca02c')
ax.plot(paths['Year'], paths['clinker_ratio_integrated'], '^-', linewidth=2, label='Integrated', color='#d62728')
ax.axhline(y=0.75, color='gray', linestyle='--', alpha=0.5, label='2050 target')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Fraction', fontweight='bold')
ax.set_title('Clinker Ratio', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Grid EF =====
ax = axes[1, 0]
ax.plot(paths['Year'], paths['grid_ef_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['grid_ef_integrated'], 's-', linewidth=2, label='Integrated (2%/yr)', color='#d62728')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('kgCO₂/kWh', fontweight='bold')
ax.set_title('Grid Emission Factor', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Truck EF (Allowed) =====
ax = axes[1, 1]
ax.plot(paths['Year'], paths['truck_ef_allowed_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['truck_ef_allowed_integrated'], 's-', linewidth=2, label='Integrated (0.5%/yr)', color='#d62728')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('gCO₂/km', fontweight='bold')
ax.set_title('Truck EF (Allowed Load)', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

# ===== Truck EF (Overload) =====
ax = axes[1, 2]
ax.plot(paths['Year'], paths['truck_ef_over_baseline'], 'o-', linewidth=2, label='Baseline', color='#1f77b4')
ax.plot(paths['Year'], paths['truck_ef_over_integrated'], 's-', linewidth=2, label='Integrated (0.5%/yr)', color='#d62728')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('gCO₂/km', fontweight='bold')
ax.set_title('Truck EF (Overload)', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()

output_plot = 'cement_decarbonization_pathways.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Pathways visualization saved to: {output_plot}\n")

plt.show()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"Decarbonization pathways generated for {len(paths)} years ({start_year}–{end_year})")
print()
print("Pathways dataframe columns:")
print("  Year")
print("  coal_int_baseline, coal_int_eff, coal_int_clinker, coal_int_integrated")
print("  elec_int_baseline, elec_int_eff, elec_int_clinker, elec_int_integrated")
print("  clinker_ratio_baseline, clinker_ratio_clinker, clinker_ratio_integrated")
print("  grid_ef_baseline, grid_ef_integrated")
print("  truck_ef_allowed_baseline, truck_ef_allowed_integrated")
print("  truck_ef_over_baseline, truck_ef_over_integrated")
print()
print(f"All values floored at {FLOOR} to prevent negatives")
print()
print("Ready for emissions projection with demand × pathways calculations")
print()