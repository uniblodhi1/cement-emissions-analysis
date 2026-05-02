"""
Script extracted from notebook cell 21.
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
print("MITIGATION ANALYSIS: INTEGRATED VS BASELINE")
print("=" * 80)
print()

results = pd.read_csv('outputs_future_scenarios.csv')

print(f"✓ Loaded future scenarios: {len(results)} rows\n")

# Filter for Medium demand
results_med = results[results['DemandCase'] == 'Med'].copy()

# Extract Baseline and Integrated pathways
baseline = results_med[results_med['Pathway'] == 'Baseline'].copy().sort_values('Year')
integrated = results_med[results_med['Pathway'] == 'Integrated'].copy().sort_values('Year')

print(f"✓ Filtered to Medium demand")
print(f"  Baseline rows: {len(baseline)}")
print(f"  Integrated rows: {len(integrated)}")
print()

# ============================================================================
# COMPUTE MITIGATION
# ============================================================================
print("Computing mitigation (Baseline − Integrated)...")
print()

# Years to analyze
analysis_years = [2030, 2040, 2050]

mitigation_data = {
    'Year': [],
    'Fuel_Mitigation_Mt': [],
    'Process_Mitigation_Mt': [],
    'Electricity_Mitigation_Mt': [],
    'Transport_Mitigation_Mt': [],
    'Total_Mitigation_Mt': [],
}

for year in analysis_years:
    # Get baseline values
    base_row = baseline[baseline['Year'] == year].iloc[0]
    base_fuel = base_row['CO2_S1_fuel_t'] / 1e6
    base_process = base_row['CO2_S1_process_t'] / 1e6
    base_elec = base_row['CO2_S2_elec_t'] / 1e6
    base_transport = base_row['CO2_S3_transport_t'] / 1e6
    base_total = base_fuel + base_process + base_elec + base_transport

    # Get integrated values
    int_row = integrated[integrated['Year'] == year].iloc[0]
    int_fuel = int_row['CO2_S1_fuel_t'] / 1e6
    int_process = int_row['CO2_S1_process_t'] / 1e6
    int_elec = int_row['CO2_S2_elec_t'] / 1e6
    int_transport = int_row['CO2_S3_transport_t'] / 1e6
    int_total = int_fuel + int_process + int_elec + int_transport

    # Calculate mitigation
    fuel_mit = base_fuel - int_fuel
    process_mit = base_process - int_process
    elec_mit = base_elec - int_elec
    transport_mit = base_transport - int_transport
    total_mit = base_total - int_total

    # Store results
    mitigation_data['Year'].append(year)
    mitigation_data['Fuel_Mitigation_Mt'].append(fuel_mit)
    mitigation_data['Process_Mitigation_Mt'].append(process_mit)
    mitigation_data['Electricity_Mitigation_Mt'].append(elec_mit)
    mitigation_data['Transport_Mitigation_Mt'].append(transport_mit)
    mitigation_data['Total_Mitigation_Mt'].append(total_mit)

# Create mitigation dataframe
mitigation_df = pd.DataFrame(mitigation_data)

print("✓ Mitigation computed\n")

# ============================================================================
# DISPLAY MITIGATION TABLE
# ============================================================================
print("=" * 80)
print("MITIGATION SUMMARY (Mt CO₂) - MEDIUM DEMAND")
print("=" * 80)
print()

pd.options.display.float_format = '{:.4f}'.format
print(mitigation_df.to_string(index=False))
print()

# ============================================================================
# DETAILED MITIGATION ANALYSIS
# ============================================================================
print("=" * 80)
print("DETAILED MITIGATION ANALYSIS")
print("=" * 80)
print()

for _, row in mitigation_df.iterrows():
    year = int(row['Year'])
    fuel_mit = row['Fuel_Mitigation_Mt']
    process_mit = row['Process_Mitigation_Mt']
    elec_mit = row['Electricity_Mitigation_Mt']
    transport_mit = row['Transport_Mitigation_Mt']
    total_mit = row['Total_Mitigation_Mt']

    # Get baseline total for percentage calculation
    base_row = baseline[baseline['Year'] == year].iloc[0]
    base_total = (base_row['CO2_S1_fuel_t'] + base_row['CO2_S1_process_t'] +
                  base_row['CO2_S2_elec_t'] + base_row['CO2_S3_transport_t']) / 1e6

    print(f"Year {year}:")
    print(f"  Baseline total:              {base_total:.2f} Mt CO₂")
    print(f"  Total mitigation:            {total_mit:.2f} Mt CO₂ ({(total_mit/base_total)*100:.1f}% reduction)")
    print()

    print(f"  Mitigation by scope:")
    print(f"    Fuel mitigation:           {fuel_mit:.2f} Mt ({(fuel_mit/total_mit)*100:5.1f}% of total mitigation)")
    print(f"    Process mitigation:        {process_mit:.2f} Mt ({(process_mit/total_mit)*100:5.1f}% of total mitigation)")
    print(f"    Electricity mitigation:    {elec_mit:.2f} Mt ({(elec_mit/total_mit)*100:5.1f}% of total mitigation)")
    print(f"    Transport mitigation:      {transport_mit:.2f} Mt ({(transport_mit/total_mit)*100:5.1f}% of total mitigation)")
    print()

# ============================================================================
# CUMULATIVE & GROWTH ANALYSIS
# ============================================================================
print("=" * 80)
print("MITIGATION PATHWAY COMPARISON")
print("=" * 80)
print()

for year in analysis_years:
    base_row = baseline[baseline['Year'] == year].iloc[0]
    int_row = integrated[integrated['Year'] == year].iloc[0]

    base_total = (base_row['CO2_S1_fuel_t'] + base_row['CO2_S1_process_t'] +
                  base_row['CO2_S2_elec_t'] + base_row['CO2_S3_transport_t']) / 1e6
    int_total = (int_row['CO2_S1_fuel_t'] + int_row['CO2_S1_process_t'] +
                 int_row['CO2_S2_elec_t'] + int_row['CO2_S3_transport_t']) / 1e6

    print(f"Year {year}:")
    print(f"  Baseline:     {base_total:7.2f} Mt CO₂")
    print(f"  Integrated:   {int_total:7.2f} Mt CO₂")
    print(f"  Mitigation:   {base_total - int_total:7.2f} Mt CO₂ ({((base_total - int_total)/base_total)*100:5.1f}%)")
    print()

# ============================================================================
# SCOPE DOMINANCE ANALYSIS
# ============================================================================
print("=" * 80)
print("SCOPE DOMINANCE - WHERE DOES MITIGATION COME FROM?")
print("=" * 80)
print()

total_fuel_mit = mitigation_df['Fuel_Mitigation_Mt'].sum()
total_process_mit = mitigation_df['Process_Mitigation_Mt'].sum()
total_elec_mit = mitigation_df['Electricity_Mitigation_Mt'].sum()
total_transport_mit = mitigation_df['Transport_Mitigation_Mt'].sum()
total_all_mit = total_fuel_mit + total_process_mit + total_elec_mit + total_transport_mit

print("Cumulative mitigation 2030-2050 (3 years analyzed):")
print()
print(f"Scope 1 Fuel:        {total_fuel_mit:6.2f} Mt ({(total_fuel_mit/total_all_mit)*100:5.1f}%)")
print(f"Scope 1 Process:     {total_process_mit:6.2f} Mt ({(total_process_mit/total_all_mit)*100:5.1f}%)")
print(f"Scope 2 Electricity: {total_elec_mit:6.2f} Mt ({(total_elec_mit/total_all_mit)*100:5.1f}%)")
print(f"Scope 3 Transport:   {total_transport_mit:6.2f} Mt ({(total_transport_mit/total_all_mit)*100:5.1f}%)")
print(f"{'─' * 50}")
print(f"TOTAL MITIGATION:    {total_all_mit:6.2f} Mt (100.0%)")
print()

# ============================================================================
# MITIGATION TRAJECTORY
# ============================================================================
print("=" * 80)
print("MITIGATION TRAJECTORY (2030 → 2050)")
print("=" * 80)
print()

mit_2030 = mitigation_df[mitigation_df['Year'] == 2030]['Total_Mitigation_Mt'].values[0]
mit_2040 = mitigation_df[mitigation_df['Year'] == 2040]['Total_Mitigation_Mt'].values[0]
mit_2050 = mitigation_df[mitigation_df['Year'] == 2050]['Total_Mitigation_Mt'].values[0]

print(f"Total mitigation by year:")
print(f"  2030: {mit_2030:.2f} Mt CO₂")
print(f"  2040: {mit_2040:.2f} Mt CO₂")
print(f"  2050: {mit_2050:.2f} Mt CO₂")
print()

growth_2030_2040 = ((mit_2040 / mit_2030) - 1) * 100
growth_2040_2050 = ((mit_2050 / mit_2040) - 1) * 100

print(f"Mitigation growth rates:")
print(f"  2030 → 2040: {growth_2030_2040:+.1f}%")
print(f"  2040 → 2050: {growth_2040_2050:+.1f}%")
print()

print("Interpretation:")
if growth_2030_2040 > 0 and growth_2040_2050 > 0:
    print("  ✓ Mitigation increases over time (decarbonization accelerating)")
    print(f"  ✓ Integrated pathway's benefit grows as we move toward 2050")
else:
    print("  ⚠ Mitigation growth is slowing")

print()

# ============================================================================
# CREATE STACKED BAR CHART
# ============================================================================
fig, ax = plt.subplots(figsize=(11, 7))

# Data for plotting
years = mitigation_df['Year'].values
fuel_mit = mitigation_df['Fuel_Mitigation_Mt'].values
process_mit = mitigation_df['Process_Mitigation_Mt'].values
elec_mit = mitigation_df['Electricity_Mitigation_Mt'].values
transport_mit = mitigation_df['Transport_Mitigation_Mt'].values

# Bar positions
x_pos = np.arange(len(years))
bar_width = 0.5

# Create stacked bars
p1 = ax.bar(x_pos, fuel_mit, bar_width,
            label='Scope 1 Fuel', color='#1f77b4', edgecolor='white', linewidth=2)

p2 = ax.bar(x_pos, process_mit, bar_width, bottom=fuel_mit,
            label='Scope 1 Process', color='#ff7f0e', edgecolor='white', linewidth=2)

bottom_2 = fuel_mit + process_mit
p3 = ax.bar(x_pos, elec_mit, bar_width, bottom=bottom_2,
            label='Scope 2 Electricity', color='#2ca02c', edgecolor='white', linewidth=2)

bottom_3 = fuel_mit + process_mit + elec_mit
p4 = ax.bar(x_pos, transport_mit, bar_width, bottom=bottom_3,
            label='Scope 3 Transport', color='#d62728', edgecolor='white', linewidth=2)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Mitigation (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Mitigation contribution by lever/scope (Integrated vs Baseline)',
             fontsize=14, fontweight='bold', pad=20)

# Set x-axis labels
ax.set_xticks(x_pos)
ax.set_xticklabels([str(int(y)) for y in years], fontsize=11, fontweight='bold')

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95,
          edgecolor='black', fancybox=True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
ax.set_axisbelow(True)

# Add value labels on bars showing total mitigation
for i, year in enumerate(years):
    total = fuel_mit[i] + process_mit[i] + elec_mit[i] + transport_mit[i]
    ax.text(i, total + 0.5, f'{total:.1f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add percentage label
    base_row = baseline[baseline['Year'] == int(year)].iloc[0]
    base_total = (base_row['CO2_S1_fuel_t'] + base_row['CO2_S1_process_t'] +
                  base_row['CO2_S2_elec_t'] + base_row['CO2_S3_transport_t']) / 1e6
    pct = (total / base_total) * 100
    ax.text(i, total/2, f'{pct:.0f}%\nreduction',
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='white', bbox=dict(boxstyle='round,pad=0.3',
                                     facecolor='black', alpha=0.6))

# Y-axis formatting
ax.yaxis.set_major_locator(plt.MaxNLocator(10))

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE PLOT
# ============================================================================
output_plot = 'cement_mitigation_stacked_bar.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_plot}\n")

plt.show()

# ============================================================================
# SAVE MITIGATION DATAFRAME
# ============================================================================
output_csv = 'cement_mitigation_analysis.csv'
mitigation_df.to_csv(output_csv, index=False)
print(f"✓ Mitigation dataframe saved: {output_csv}\n")

# ============================================================================
# KEY INSIGHTS
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS - MITIGATION ANALYSIS")
print("=" * 80)
print()

avg_total_mit = mitigation_df['Total_Mitigation_Mt'].mean()
avg_process_mit_pct = (mitigation_df['Process_Mitigation_Mt'].mean() / avg_total_mit) * 100
avg_fuel_mit_pct = (mitigation_df['Fuel_Mitigation_Mt'].mean() / avg_total_mit) * 100
avg_elec_mit_pct = (mitigation_df['Electricity_Mitigation_Mt'].mean() / avg_total_mit) * 100

print(f"""
MITIGATION BY SCOPE (averaged across 2030, 2040, 2050):

1. PROCESS EMISSIONS (Scope 1 Process): {avg_process_mit_pct:.0f}% of total mitigation
   • Clinker ratio decline (0.95 → 0.75) is the single largest lever
   • Process mitigation grows as clinker substitution accelerates toward 2050
   • Requires fundamental shift to blended cements and alternative binders
   • Most challenging but most impactful intervention

2. FUEL EMISSIONS (Scope 1 Fuel): {avg_fuel_mit_pct:.0f}% of total mitigation
   • Coal intensity improvements (1.8% → 1.0%/year in integrated)
   • Steady savings from industrial efficiency gains
   • Proven technologies with established supply chains
   • Continuous improvement with diminishing returns over time

3. ELECTRICITY (Scope 2): {avg_elec_mit_pct:.0f}% of total mitigation
   • Grid decarbonization (2%/year EF decline) amplifies as grid becomes cleaner
   • Accelerating mitigation benefit: grows from 2030 to 2050
   • Dependent on broader energy policy and renewable deployment
   • "Co-benefit" approach: benefits without cement sector action

4. TRANSPORT (Scope 3): <1% of total mitigation
   • Minimal contribution due to low baseline (~1% of total emissions)
   • Fleet efficiency improvements (0.5%/year) have marginal impact
   • Scope 3 should not be priority focus (focus on Scopes 1 & 2)

STRATEGIC IMPLICATIONS:

• Clinker substitution is NOT OPTIONAL - it's the largest mitigation lever
  (Process mitigation = {total_process_mit:.2f} Mt CO₂ over 2030-2050)

• Grid decarbonization is co-dependent - cement sector benefits automatically
  (Electricity mitigation = {total_elec_mit:.2f} Mt CO₂ over 2030-2050)

• Fuel efficiency is steady-state mitigation - reliable but not transformative
  (Fuel mitigation = {total_fuel_mit:.2f} Mt CO₂ over 2030-2050)

• Total integrated pathway mitigation: {total_all_mit:.2f} Mt CO₂ (2030-2050)
  → This is {(total_all_mit/3):.2f} Mt CO₂ average annual mitigation across 20 years

• Without integrated approach, baseline pathway grows uncontrolled
  → Medium demand alone drives {mit_2050:.2f} Mt CO₂ mitigation by 2050
  → Demonstrates criticality of early action and sustained commitment
""")

print()