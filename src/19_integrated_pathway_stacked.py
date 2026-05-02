"""
Script extracted from notebook cell 19.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# LOAD AND FILTER DATA
# ============================================================================
print("=" * 80)
print("EMISSIONS BY SCOPE - INTEGRATED PATHWAY (MEDIUM DEMAND)")
print("=" * 80)
print()

results = pd.read_csv('outputs_future_scenarios.csv')

print(f"✓ Loaded future scenarios: {len(results)} rows\n")

# Filter for Medium demand and Integrated pathway
results_filtered = results[
    (results['DemandCase'] == 'Med') &
    (results['Pathway'] == 'Integrated')
].copy().sort_values('Year')

print(f"✓ Filtered to Medium demand + Integrated pathway: {len(results_filtered)} rows")
print(f"  Years: {int(results_filtered['Year'].min())} to {int(results_filtered['Year'].max())}\n")

# ============================================================================
# CONVERT TO Mt CO₂
# ============================================================================
results_filtered['S1_fuel_Mt'] = results_filtered['CO2_S1_fuel_t'] / 1e6
results_filtered['S1_process_Mt'] = results_filtered['CO2_S1_process_t'] / 1e6
results_filtered['S2_elec_Mt'] = results_filtered['CO2_S2_elec_t'] / 1e6
results_filtered['S3_transport_Mt'] = results_filtered['CO2_S3_transport_t'] / 1e6

print("Scope breakdown (Mt CO₂):\n")

# Display summary by year
display_years = [2024, 2030, 2040, 2050]
for year in display_years:
    row = results_filtered[results_filtered['Year'] == year]
    if len(row) > 0:
        s1_fuel = row['S1_fuel_Mt'].values[0]
        s1_process = row['S1_process_Mt'].values[0]
        s2_elec = row['S2_elec_Mt'].values[0]
        s3_transport = row['S3_transport_Mt'].values[0]
        total = s1_fuel + s1_process + s2_elec + s3_transport

        print(f"Year {year}:")
        print(f"  Scope 1 Fuel:       {s1_fuel:7.2f} Mt ({(s1_fuel/total)*100:5.1f}%)")
        print(f"  Scope 1 Process:    {s1_process:7.2f} Mt ({(s1_process/total)*100:5.1f}%)")
        print(f"  Scope 2 Electricity:{s2_elec:7.2f} Mt ({(s2_elec/total)*100:5.1f}%)")
        print(f"  Scope 3 Transport:  {s3_transport:7.2f} Mt ({(s3_transport/total)*100:5.1f}%)")
        print(f"  TOTAL:              {total:7.2f} Mt (100.0%)")
        print()

# ============================================================================
# CREATE STACKED AREA PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(13, 7.5))

# Extract data for plotting
years = results_filtered['Year'].values
s1_fuel = results_filtered['S1_fuel_Mt'].values
s1_process = results_filtered['S1_process_Mt'].values
s2_elec = results_filtered['S2_elec_Mt'].values
s3_transport = results_filtered['S3_transport_Mt'].values

# Define colors for each scope
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
scope_labels = ['Scope 1 Fuel', 'Scope 1 Process', 'Scope 2 Electricity', 'Scope 3 Transport']

# Create stacked area plot
ax.stackplot(years, s1_fuel, s1_process, s2_elec, s3_transport,
             labels=scope_labels,
             colors=colors,
             alpha=0.80,
             edgecolor='white',
             linewidth=0.5)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Emissions by scope under Integrated pathway (Medium demand)',
             fontsize=14, fontweight='bold', pad=20)

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95,
          edgecolor='black', fancybox=True)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
ax.set_axisbelow(True)

# X-axis ticks every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Set y-axis limits with some padding
y_max = (s1_fuel + s1_process + s2_elec + s3_transport).max()
ax.set_ylim(0, y_max * 1.05)

# Add annotations showing total in key years
annotation_years = [2024, 2035, 2050]
for year in annotation_years:
    row_idx = results_filtered[results_filtered['Year'] == year].index
    if len(row_idx) > 0:
        idx = row_idx[0]
        total = (s1_fuel[idx-results_filtered.index[0]] +
                s1_process[idx-results_filtered.index[0]] +
                s2_elec[idx-results_filtered.index[0]] +
                s3_transport[idx-results_filtered.index[0]])

        if year == 2024:
            y_pos = total
            y_offset = 5
        elif year == 2050:
            y_pos = total
            y_offset = -8
        else:
            y_pos = total
            y_offset = 0

        ax.text(year, y_pos + y_offset, f'{total:.1f} Mt',
                fontsize=9, fontweight='bold', ha='center', va='bottom' if y_offset > 0 else 'top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE PLOT
# ============================================================================
output_plot = 'cement_integrated_pathway_stacked.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_plot}\n")

plt.show()

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("DETAILED SCOPE ANALYSIS - INTEGRATED PATHWAY (MEDIUM DEMAND)")
print("=" * 80)
print()

# 2024 baseline
row_2024 = results_filtered[results_filtered['Year'] == 2024].iloc[0]
s1_fuel_2024 = row_2024['S1_fuel_Mt']
s1_process_2024 = row_2024['S1_process_Mt']
s2_elec_2024 = row_2024['S2_elec_Mt']
s3_transport_2024 = row_2024['S3_transport_Mt']
total_2024 = s1_fuel_2024 + s1_process_2024 + s2_elec_2024 + s3_transport_2024

# 2050 projection
row_2050 = results_filtered[results_filtered['Year'] == 2050].iloc[0]
s1_fuel_2050 = row_2050['S1_fuel_Mt']
s1_process_2050 = row_2050['S1_process_Mt']
s2_elec_2050 = row_2050['S2_elec_Mt']
s3_transport_2050 = row_2050['S3_transport_Mt']
total_2050 = s1_fuel_2050 + s1_process_2050 + s2_elec_2050 + s3_transport_2050

print("SCOPE 1 FUEL COMBUSTION:")
print(f"  2024: {s1_fuel_2024:.2f} Mt ({(s1_fuel_2024/total_2024)*100:.1f}% of total)")
print(f"  2050: {s1_fuel_2050:.2f} Mt ({(s1_fuel_2050/total_2050)*100:.1f}% of total)")
change_fuel = s1_fuel_2050 - s1_fuel_2024
pct_change_fuel = ((s1_fuel_2050 / s1_fuel_2024) - 1) * 100
print(f"  Change: {change_fuel:+.2f} Mt ({pct_change_fuel:+.1f}%)")
print()

print("SCOPE 1 PROCESS (CLINKER CALCINATION):")
print(f"  2024: {s1_process_2024:.2f} Mt ({(s1_process_2024/total_2024)*100:.1f}% of total)")
print(f"  2050: {s1_process_2050:.2f} Mt ({(s1_process_2050/total_2050)*100:.1f}% of total)")
change_process = s1_process_2050 - s1_process_2024
pct_change_process = ((s1_process_2050 / s1_process_2024) - 1) * 100
print(f"  Change: {change_process:+.2f} Mt ({pct_change_process:+.1f}%)")
print()

print("SCOPE 2 ELECTRICITY:")
print(f"  2024: {s2_elec_2024:.2f} Mt ({(s2_elec_2024/total_2024)*100:.1f}% of total)")
print(f"  2050: {s2_elec_2050:.2f} Mt ({(s2_elec_2050/total_2050)*100:.1f}% of total)")
change_elec = s2_elec_2050 - s2_elec_2024
pct_change_elec = ((s2_elec_2050 / s2_elec_2024) - 1) * 100
print(f"  Change: {change_elec:+.2f} Mt ({pct_change_elec:+.1f}%)")
print()

print("SCOPE 3 TRANSPORT:")
print(f"  2024: {s3_transport_2024:.2f} Mt ({(s3_transport_2024/total_2024)*100:.1f}% of total)")
print(f"  2050: {s3_transport_2050:.2f} Mt ({(s3_transport_2050/total_2050)*100:.1f}% of total)")
change_transport = s3_transport_2050 - s3_transport_2024
pct_change_transport = ((s3_transport_2050 / s3_transport_2024) - 1) * 100
print(f"  Change: {change_transport:+.2f} Mt ({pct_change_transport:+.1f}%)")
print()

print("TOTAL EMISSIONS:")
print(f"  2024: {total_2024:.2f} Mt CO₂")
print(f"  2050: {total_2050:.2f} Mt CO₂")
total_change = total_2050 - total_2024
total_pct_change = ((total_2050 / total_2024) - 1) * 100
print(f"  Change: {total_change:+.2f} Mt ({total_pct_change:+.1f}%)")
print()

# ============================================================================
# EMISSION COMPOSITION EVOLUTION
# ============================================================================
print("=" * 80)
print("EMISSION COMPOSITION EVOLUTION")
print("=" * 80)
print()

print("Share of each scope in total emissions:")
print()
print("2024 composition:")
print(f"  Scope 1 Fuel:        {(s1_fuel_2024/total_2024)*100:5.1f}%")
print(f"  Scope 1 Process:     {(s1_process_2024/total_2024)*100:5.1f}%")
print(f"  Scope 2 Electricity: {(s2_elec_2024/total_2024)*100:5.1f}%")
print(f"  Scope 3 Transport:   {(s3_transport_2024/total_2024)*100:5.1f}%")
print()

print("2050 composition:")
print(f"  Scope 1 Fuel:        {(s1_fuel_2050/total_2050)*100:5.1f}%")
print(f"  Scope 1 Process:     {(s1_process_2050/total_2050)*100:5.1f}%")
print(f"  Scope 2 Electricity: {(s2_elec_2050/total_2050)*100:5.1f}%")
print(f"  Scope 3 Transport:   {(s3_transport_2050/total_2050)*100:5.1f}%")
print()

# ============================================================================
# DECARBONIZATION DRIVERS
# ============================================================================
print("=" * 80)
print("DECARBONIZATION DRIVERS - INTEGRATED PATHWAY")
print("=" * 80)
print()

print("Primary mechanisms reducing each scope from 2024 to 2050:")
print()

print("Scope 1 Fuel (−{:.1f}%):".format(pct_change_fuel))
print("  • Coal intensity reduction: 1.0%/year (from 180 to 162 kg/t)")
print("  • Partially offset by cement demand growth")
print()

print("Scope 1 Process (−{:.1f}%):".format(pct_change_process))
print("  • Clinker ratio decline: from 0.95 to 0.75 by 2050")
print("  • Substitute with lower-carbon blended cements")
print("  • Largest absolute emission reduction achieved")
print()

print("Scope 2 Electricity (−{:.1f}%):".format(pct_change_elec))
print("  • Grid decarbonization: 2.0%/year EF reduction")
print("  • Grid EF declines from 0.71 to 0.37 kgCO2/kWh")
print("  • Most dramatic EF improvement across all scopes")
print()

print("Scope 3 Transport (−{:.1f}%):".format(pct_change_transport))
print("  • Truck efficiency improvement: 0.5%/year")
print("  • Modest impact due to small baseline contribution (~1% of total)")
print()

# ============================================================================
# DECADE ANALYSIS
# ============================================================================
print("=" * 80)
print("DECADE-BY-DECADE BREAKDOWN")
print("=" * 80)
print()

decades = [2024, 2030, 2040, 2050]

for i, year in enumerate(decades):
    row = results_filtered[results_filtered['Year'] == year].iloc[0]

    s1f = row['S1_fuel_Mt']
    s1p = row['S1_process_Mt']
    s2e = row['S2_elec_Mt']
    s3t = row['S3_transport_Mt']
    tot = s1f + s1p + s2e + s3t

    intensity = row['CO2_intensity']

    print(f"Year {year}:")
    print(f"  Total: {tot:.2f} Mt, Intensity: {intensity:.4f} tCO₂/t cement")
    print(f"  Scope 1 Fuel:        {s1f:6.2f} Mt ({(s1f/tot)*100:5.1f}%)")
    print(f"  Scope 1 Process:     {s1p:6.2f} Mt ({(s1p/tot)*100:5.1f}%)")
    print(f"  Scope 2 Electricity: {s2e:6.2f} Mt ({(s2e/tot)*100:5.1f}%)")
    print(f"  Scope 3 Transport:   {s3t:6.2f} Mt ({(s3t/tot)*100:5.1f}%)")

    if i < len(decades) - 1:
        next_year = decades[i + 1]
        next_row = results_filtered[results_filtered['Year'] == next_year].iloc[0]
        next_tot = (next_row['S1_fuel_Mt'] + next_row['S1_process_Mt'] +
                    next_row['S2_elec_Mt'] + next_row['S3_transport_Mt'])

        period_change = next_tot - tot
        period_pct = ((next_tot / tot) - 1) * 100
        years_in_period = next_year - year

        print(f"  → {next_year} ({years_in_period}-yr change): {period_change:+.2f} Mt ({period_pct:+.1f}%)")

    print()

# ============================================================================
# KEY INSIGHTS
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print()

s1_total_2024 = s1_fuel_2024 + s1_process_2024
s1_total_2050 = s1_fuel_2050 + s1_process_2050
s1_share_2024 = (s1_total_2024 / total_2024) * 100
s1_share_2050 = (s1_total_2050 / total_2050) * 100

print(f"""
• Scope 1 remains dominant even under integrated pathway:
  - 2024: {s1_share_2024:.0f}% of total emissions
  - 2050: {s1_share_2050:.0f}% of total emissions
  - Combined Scope 1 absolute reduction: {(s1_total_2024-s1_total_2050):.2f} Mt CO₂

• Process emissions (clinker calcination) are hardest to reduce:
  - Clinker ratio declining from 0.95 to 0.75 is the only process mitigation
  - Requires fundamental shift to blended cements and alternative binders
  - {(s1_process_2050/s1_process_2024)*100:.0f}% of 2024 process emissions remain in 2050

• Grid decarbonization drives largest % improvement:
  - Scope 2 drops {abs(pct_change_elec):.0f}% due to 2%/year grid EF decline
  - However, absolute contribution remains modest (~9% of total in 2050)

• Transport emissions barely improve:
  - Scope 3 remains <1% of total due to low baseline contribution
  - Fleet efficiency improvements (0.5%/yr) insufficient to offset demand growth
  - Focus should remain on production-side decarbonization

• Total emissions growth is slowed but not reversed:
  - Integrated pathway: {total_pct_change:+.1f}% by 2050 (vs +204% baseline)
  - Medium demand (3%/yr) growth outpaces efficiency gains initially
  - Post-2040, intensity reductions begin offsetting demand growth
""")

print()