"""
Script extracted from notebook cell 18.
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
print("PROJECTED CO₂ EMISSIONS - MEDIUM DEMAND SCENARIO")
print("=" * 80)
print()

results = pd.read_csv('outputs_future_scenarios.csv')

print(f"✓ Loaded future scenarios: {len(results)} rows\n")

# Filter for Medium demand case
results_med = results[results['DemandCase'] == 'Med'].copy()

print(f"✓ Filtered to Medium demand: {len(results_med)} rows")
print(f"  Years: {int(results_med['Year'].min())} to {int(results_med['Year'].max())}")
print(f"  Pathways: {results_med['Pathway'].unique().tolist()}")
print()

# ============================================================================
# CONVERT TO Mt CO₂
# ============================================================================
results_med['CO2_total_Mt'] = results_med['CO2_total_t'] / 1e6

print("Total CO₂ emissions (Mt CO₂) - Medium demand:")
print()

# Display summary by pathway
for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    subset = results_med[results_med['Pathway'] == pathway]
    co2_2024 = subset[subset['Year'] == subset['Year'].min()]['CO2_total_Mt'].values[0]
    co2_2050 = subset[subset['Year'] == subset['Year'].max()]['CO2_total_Mt'].values[0]
    change = ((co2_2050 / co2_2024) - 1) * 100

    print(f"{pathway:20s}: {co2_2024:7.2f} Mt (2024) → {co2_2050:7.2f} Mt (2050) "
          f"({change:+6.1f}%)")

print()

# ============================================================================
# CREATE LINE PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(13, 7))

# Define colors and markers for pathways
pathway_styles = {
    'Baseline': {'color': '#1f77b4', 'marker': 'o', 'linestyle': '-'},
    'Efficiency': {'color': '#ff7f0e', 'marker': 's', 'linestyle': '-'},
    'Clinker_Reduction': {'color': '#2ca02c', 'marker': '^', 'linestyle': '-'},
    'Integrated': {'color': '#d62728', 'marker': 'd', 'linestyle': '-'},
}

# Plot each pathway
for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    subset = results_med[results_med['Pathway'] == pathway].sort_values('Year')

    ax.plot(subset['Year'], subset['CO2_total_Mt'],
            linewidth=2.8,
            color=pathway_styles[pathway]['color'],
            marker=pathway_styles[pathway]['marker'],
            markersize=6,
            markerfacecolor=pathway_styles[pathway]['color'],
            markeredgecolor='white',
            markeredgewidth=0.8,
            label=pathway,
            alpha=0.85)

# Labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Projected total CO₂ emissions (Medium demand)',
             fontsize=14, fontweight='bold', pad=20)

# Legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95,
          edgecolor='black', fancybox=True, title='Pathway', title_fontsize=11)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# X-axis ticks
ax.set_xticks(range(2024, 2051, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Y-axis formatting
ax.yaxis.set_major_locator(plt.MaxNLocator(10))

# Add annotations for 2050 values
results_2050 = results_med[results_med['Year'] == 2050]
for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    co2_2050 = results_2050[results_2050['Pathway'] == pathway]['CO2_total_Mt'].values[0]
    ax.text(2050.3, co2_2050, f'{co2_2050:.1f}',
            fontsize=9, fontweight='bold',
            color=pathway_styles[pathway]['color'],
            va='center')

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE PLOT
# ============================================================================
output_plot = 'cement_medium_demand_projection.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_plot}\n")

plt.show()

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("DETAILED ANALYSIS - MEDIUM DEMAND SCENARIO")
print("=" * 80)
print()

# 2050 comparison
print("2050 PROJECTIONS:")
print()
results_2050 = results_med[results_med['Year'] == 2050].sort_values('CO2_total_Mt')

baseline_2050 = results_2050[results_2050['Pathway'] == 'Baseline']['CO2_total_Mt'].values[0]

for _, row in results_2050.iterrows():
    co2_mt = row['CO2_total_Mt']
    pathway = row['Pathway']
    intensity = row['CO2_intensity']

    if pathway == 'Baseline':
        print(f"{pathway:20s}: {co2_mt:7.2f} Mt CO₂, {intensity:.4f} tCO₂/t cement")
    else:
        reduction = ((baseline_2050 - co2_mt) / baseline_2050) * 100
        print(f"{pathway:20s}: {co2_mt:7.2f} Mt CO₂, {intensity:.4f} tCO₂/t cement "
              f"({reduction:+6.1f}% vs baseline)")

print()

# Reductions achieved
print("EMISSION REDUCTIONS VS BASELINE (2050):")
print()

baseline_co2_2050 = results_2050[results_2050['Pathway'] == 'Baseline']['CO2_total_Mt'].values[0]

for pathway in ['Efficiency', 'Clinker_Reduction', 'Integrated']:
    pathway_co2_2050 = results_2050[results_2050['Pathway'] == pathway]['CO2_total_Mt'].values[0]
    absolute_reduction = baseline_co2_2050 - pathway_co2_2050
    percent_reduction = (absolute_reduction / baseline_co2_2050) * 100

    print(f"{pathway:20s}: {absolute_reduction:6.2f} Mt CO₂ ({percent_reduction:5.1f}%)")

print()

# Growth comparison
print("GROWTH TRAJECTORY COMPARISON:")
print()

results_2024 = results_med[results_med['Year'] == 2024]

for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    co2_2024 = results_2024[results_2024['Pathway'] == pathway]['CO2_total_Mt'].values[0]
    co2_2050 = results_2050[results_2050['Pathway'] == pathway]['CO2_total_Mt'].values[0]

    growth = co2_2050 - co2_2024
    growth_pct = ((co2_2050 / co2_2024) - 1) * 100

    print(f"{pathway:20s}: {co2_2024:6.2f} Mt (2024) → {co2_2050:6.2f} Mt (2050) "
          f"({growth:+6.2f} Mt, {growth_pct:+6.1f}%)")

print()

# Key milestones
print("KEY MILESTONES (Medium demand):")
print()

baseline_subset = results_med[results_med['Pathway'] == 'Baseline'].sort_values('Year')
baseline_2024 = baseline_subset[baseline_subset['Year'] == 2024]['CO2_total_Mt'].values[0]

# Find year when Integrated reaches different levels
integrated_subset = results_med[results_med['Pathway'] == 'Integrated'].sort_values('Year')

for multiple in [0.75, 0.50]:
    target = baseline_2024 * multiple
    year_reached = integrated_subset[integrated_subset['CO2_total_Mt'] <= target]['Year'].min()

    if pd.notna(year_reached):
        co2_at_year = integrated_subset[integrated_subset['Year'] == year_reached]['CO2_total_Mt'].values[0]
        print(f"Integrated pathway reaches {multiple*100:.0f}% of 2024 level: {int(year_reached)}")
        print(f"  CO₂ emissions: {co2_at_year:.2f} Mt CO₂")
    else:
        print(f"Integrated pathway does not reach {multiple*100:.0f}% of 2024 level by 2050")

print()

# Decade-by-decade comparison
print("DECADE-BY-DECADE COMPARISON (Medium demand):")
print()

decades = [2024, 2030, 2040, 2050]

for pathway in ['Baseline', 'Efficiency', 'Clinker_Reduction', 'Integrated']:
    print(f"{pathway}:")
    subset = results_med[results_med['Pathway'] == pathway]

    for decade in decades:
        co2_mt = subset[subset['Year'] == decade]['CO2_total_Mt'].values[0]
        intensity = subset[subset['Year'] == decade]['CO2_intensity'].values[0]
        print(f"  {decade}: {co2_mt:7.2f} Mt, {intensity:.4f} tCO₂/t")

    print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS - MEDIUM DEMAND SCENARIO")
print("=" * 80)
print()

baseline_2024 = results_2024[results_2024['Pathway'] == 'Baseline']['CO2_total_Mt'].values[0]
baseline_2050 = results_2050[results_2050['Pathway'] == 'Baseline']['CO2_total_Mt'].values[0]
integrated_2050 = results_2050[results_2050['Pathway'] == 'Integrated']['CO2_total_Mt'].values[0]

print(f"""
• Under medium demand growth (3%/yr):
  - Baseline emissions nearly TRIPLE from {baseline_2024:.1f} Mt (2024) to {baseline_2050:.1f} Mt (2050)
  - This represents a +{((baseline_2050/baseline_2024)-1)*100:.0f}% growth over 26 years

• Decarbonization pathways significantly mitigate growth:
  - Integrated pathway limits 2050 emissions to {integrated_2050:.1f} Mt
  - This is a {((integrated_2050/baseline_2050)-1)*100:.0f}% reduction vs baseline
  - Absolute avoided emissions: {baseline_2050 - integrated_2050:.1f} Mt CO₂

• Pathway comparison (2050 emissions):
  1. Baseline:           {results_2050[results_2050['Pathway']=='Baseline']['CO2_total_Mt'].values[0]:.2f} Mt (no action)
  2. Efficiency:         {results_2050[results_2050['Pathway']=='Efficiency']['CO2_total_Mt'].values[0]:.2f} Mt (fuel/elec improvements)
  3. Clinker_Reduction:  {results_2050[results_2050['Pathway']=='Clinker_Reduction']['CO2_total_Mt'].values[0]:.2f} Mt (clinker substitution)
  4. Integrated:         {results_2050[results_2050['Pathway']=='Integrated']['CO2_total_Mt'].values[0]:.2f} Mt (all measures combined)

• Carbon intensity improvements:
  - Baseline:    ~{results_2050[results_2050['Pathway']=='Baseline']['CO2_intensity'].values[0]:.4f} tCO₂/t (constant)
  - Integrated:  ~{results_2050[results_2050['Pathway']=='Integrated']['CO2_intensity'].values[0]:.4f} tCO₂/t (−{((1-results_2050[results_2050['Pathway']=='Integrated']['CO2_intensity'].values[0]/results_2050[results_2050['Pathway']=='Baseline']['CO2_intensity'].values[0])*100):.0f}%)

• Achieving net-zero in cement requires multiple interventions:
  - Fuel/electricity efficiency alone insufficient
  - Clinker substitution crucial for process emissions
  - Grid decarbonization amplifies Scope 2 benefits
  - Integrated approach combines all measures for maximum impact
""")

print()