"""
Script extracted from notebook cell 15.
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
print("CEMENT DEMAND PROJECTION TO 2050")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')

# Sort by year and get base year
hist = hist.sort_values('year').reset_index(drop=True)
BASE_YEAR = int(hist['year'].max())

print(f"Base year: {BASE_YEAR}\n")

# Extract cement production baseline
if 'cement_t' in hist.columns:
    cement_base = hist[hist['year'] == BASE_YEAR]['cement_t'].iloc[0]
    print(f"Cement production baseline (cement_base): {cement_base:.0f} tonnes")
    print(f"                                           {cement_base/1e6:.2f} Mt\n")
else:
    print("ERROR: 'cement_t' column not found in historical data")
    exit()

# ============================================================================
# DEFINE DEMAND GROWTH SCENARIOS
# ============================================================================
print("Demand growth scenarios:")
print()

growth_rates = {
    'Demand_Low': 0.01,      # 1% annual
    'Demand_Med': 0.03,      # 3% annual
    'Demand_High': 0.05,     # 5% annual
}

for scenario_name, growth_rate in growth_rates.items():
    print(f"  {scenario_name:15s}: {growth_rate*100:.1f}% annual growth")

print()

# ============================================================================
# CREATE PROJECTION YEARS
# ============================================================================
start_year = BASE_YEAR + 1
end_year = 2050

projection_years = np.arange(start_year, end_year + 1)

print(f"Projection period: {start_year} to {end_year} ({len(projection_years)} years)\n")

# ============================================================================
# APPLY COMPOUND GROWTH TO CALCULATE FUTURE DEMAND
# ============================================================================
print("Calculating future cement demand with compound growth...")
print()

# Formula: Future_Value = Base_Value * (1 + growth_rate)^years_from_base

demand_data = {
    'Year': projection_years,
    'Demand_Low': [],
    'Demand_Med': [],
    'Demand_High': [],
}

for year in projection_years:
    years_from_base = year - BASE_YEAR

    # Low scenario (1% annual)
    demand_low = cement_base * (1 + growth_rates['Demand_Low']) ** years_from_base
    demand_data['Demand_Low'].append(demand_low)

    # Medium scenario (3% annual)
    demand_med = cement_base * (1 + growth_rates['Demand_Med']) ** years_from_base
    demand_data['Demand_Med'].append(demand_med)

    # High scenario (5% annual)
    demand_high = cement_base * (1 + growth_rates['Demand_High']) ** years_from_base
    demand_data['Demand_High'].append(demand_high)

# Create dataframe
demand = pd.DataFrame(demand_data)

print("✓ Demand projection complete\n")

# ============================================================================
# DISPLAY RESULTS TABLE
# ============================================================================
print("=" * 80)
print("CEMENT DEMAND PROJECTION (tonnes)")
print("=" * 80)
print()

# Show key years: BASE_YEAR, next 5 years, then every 5 years, and final year
display_years = [BASE_YEAR]  # Add base year for reference
display_years.extend(range(start_year, end_year + 1, 5))
if end_year not in display_years:
    display_years.append(end_year)

display_indices = []
for year in display_years:
    if year >= start_year:
        idx = demand[demand['Year'] == year].index
        if len(idx) > 0:
            display_indices.append(idx[0])

display_indices = sorted(set(display_indices))

# Add base year for reference
base_year_row = pd.DataFrame({
    'Year': [BASE_YEAR],
    'Demand_Low': [cement_base],
    'Demand_Med': [cement_base],
    'Demand_High': [cement_base]
})

display_df = pd.concat([base_year_row, demand.iloc[display_indices]], ignore_index=True)

# Format for display
pd.options.display.float_format = '{:.0f}'.format
print(display_df.to_string(index=False))
print()

# ============================================================================
# CONVERT TO Mt FOR ANALYSIS
# ============================================================================
demand_Mt = demand.copy()
demand_Mt['Demand_Low'] = demand_Mt['Demand_Low'] / 1e6
demand_Mt['Demand_Med'] = demand_Mt['Demand_Med'] / 1e6
demand_Mt['Demand_High'] = demand_Mt['Demand_High'] / 1e6

print("=" * 80)
print("CEMENT DEMAND PROJECTION (Mt)")
print("=" * 80)
print()

# Show same indices in Mt
display_df_Mt = pd.concat([
    pd.DataFrame({
        'Year': [BASE_YEAR],
        'Demand_Low': [cement_base/1e6],
        'Demand_Med': [cement_base/1e6],
        'Demand_High': [cement_base/1e6]
    }),
    demand_Mt.iloc[display_indices]
], ignore_index=True)

pd.options.display.float_format = '{:.2f}'.format
print(display_df_Mt.to_string(index=False))
print()

# ============================================================================
# DEMAND GROWTH ANALYSIS
# ============================================================================
print("=" * 80)
print("DEMAND GROWTH ANALYSIS")
print("=" * 80)
print()

# Final year (2050) analysis
final_idx = len(demand) - 1
final_year = int(demand.loc[final_idx, 'Year'])
demand_2050_low = demand.loc[final_idx, 'Demand_Low']
demand_2050_med = demand.loc[final_idx, 'Demand_Med']
demand_2050_high = demand.loc[final_idx, 'Demand_High']

print(f"Year {final_year} projections:")
print(f"  Low (1%/yr):    {demand_2050_low/1e6:8.2f} Mt  ({demand_2050_low/cement_base:5.1f}x base)")
print(f"  Medium (3%/yr): {demand_2050_med/1e6:8.2f} Mt  ({demand_2050_med/cement_base:5.1f}x base)")
print(f"  High (5%/yr):   {demand_2050_high/1e6:8.2f} Mt  ({demand_2050_high/cement_base:5.1f}x base)")
print()

# Cumulative growth
cum_growth_low = ((demand_2050_low / cement_base) - 1) * 100
cum_growth_med = ((demand_2050_med / cement_base) - 1) * 100
cum_growth_high = ((demand_2050_high / cement_base) - 1) * 100

print(f"Cumulative growth ({BASE_YEAR} to {final_year}):")
print(f"  Low (1%/yr):    {cum_growth_low:+7.1f}%")
print(f"  Medium (3%/yr): {cum_growth_med:+7.1f}%")
print(f"  High (5%/yr):   {cum_growth_high:+7.1f}%")
print()

# Absolute differences in 2050
diff_low_med = demand_2050_med - demand_2050_low
diff_med_high = demand_2050_high - demand_2050_med
diff_low_high = demand_2050_high - demand_2050_low

print(f"Scenario spread in {final_year}:")
print(f"  Med − Low:  {diff_low_med/1e6:7.2f} Mt ({(diff_low_med/demand_2050_med)*100:5.1f}%)")
print(f"  High − Med: {diff_med_high/1e6:7.2f} Mt ({(diff_med_high/demand_2050_med)*100:5.1f}%)")
print(f"  High − Low: {diff_low_high/1e6:7.2f} Mt ({(diff_low_high/demand_2050_med)*100:5.1f}%)")
print()

# Milestone analysis
print(f"Milestone analysis (when does demand reach specific multiples):")
print()

for multiple in [1.5, 2.0, 2.5]:
    target = cement_base * multiple
    for scenario, col in [('Low', 'Demand_Low'), ('Med', 'Demand_Med'), ('High', 'Demand_High')]:
        year_reached = demand[demand[col] >= target]['Year'].min()
        if pd.notna(year_reached):
            print(f"  {multiple:.1f}x base: {scenario:3s} scenario reaches in {int(year_reached)}")
        else:
            print(f"  {multiple:.1f}x base: {scenario:3s} scenario does not reach within projection")
    print()

# ============================================================================
# SAVE RESULTS (BOTH IN TONNES AND Mt)
# ============================================================================
output_csv_tonnes = 'cement_demand_projection_tonnes.csv'
demand.to_csv(output_csv_tonnes, index=False)
print(f"✓ Demand projection (tonnes) saved to: {output_csv_tonnes}\n")

output_csv_mt = 'cement_demand_projection_Mt.csv'
demand_Mt.to_csv(output_csv_mt, index=False)
print(f"✓ Demand projection (Mt) saved to: {output_csv_mt}\n")

# ============================================================================
# CREATE VISUALIZATION
# ============================================================================
fig, ax = plt.subplots(figsize=(13, 7))

colors = ['#1f77b4', '#ff7f0e', '#d62728']
markers = ['o', 's', '^']
scenario_labels = ['Low (1%/yr)', 'Medium (3%/yr)', 'High (5%/yr)']
scenario_cols = ['Demand_Low', 'Demand_Med', 'Demand_High']

# Plot demand projection (in Mt)
for col, label, color, marker in zip(scenario_cols, scenario_labels, colors, markers):
    ax.plot(demand_Mt['Year'], demand_Mt[col], linewidth=2.5, color=color,
            marker=marker, markersize=5, markerfacecolor=color, markeredgecolor='white',
            markeredgewidth=0.5, label=label, alpha=0.85)

# Add vertical line at BASE_YEAR to show historical/projection boundary
ax.axvline(x=BASE_YEAR, color='gray', linestyle='--', linewidth=1.5, alpha=0.5, label=f'Base year ({BASE_YEAR})')

# Labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Cement Demand (Mt)', fontsize=12, fontweight='bold')
ax.set_title('Cement demand projection to 2050', fontsize=14, fontweight='bold', pad=20)

# Legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# X-axis ticks
ax.set_xticks(range(BASE_YEAR, 2051, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add annotation showing 2050 values
annotation_text = f'{final_year} projections:\nLow: {demand_2050_low/1e6:.1f} Mt\nMed: {demand_2050_med/1e6:.1f} Mt\nHigh: {demand_2050_high/1e6:.1f} Mt'
ax.text(0.98, 0.05, annotation_text,
        transform=ax.transAxes,
        fontsize=9, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
        ha='right', va='bottom', family='monospace')

plt.tight_layout()

output_plot = 'cement_demand_projection.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved to: {output_plot}\n")

plt.show()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"Cement demand projection created with three scenarios:")
print()
print(f"Base year:           {BASE_YEAR}")
print(f"Base cement demand:  {cement_base/1e6:.2f} Mt")
print()
print(f"Projection period:   {start_year} to {final_year}")
print(f"Projection horizon:  {len(projection_years)} years")
print()
print(f"Growth scenarios:")
print(f"  Low:    {growth_rates['Demand_Low']*100:.1f}% annual → {cum_growth_low:+.1f}% by {final_year}")
print(f"  Medium: {growth_rates['Demand_Med']*100:.1f}% annual → {cum_growth_med:+.1f}% by {final_year}")
print(f"  High:   {growth_rates['Demand_High']*100:.1f}% annual → {cum_growth_high:+.1f}% by {final_year}")
print()
print(f"Scenario spread in {final_year}: {diff_low_high/1e6:.2f} Mt ({(diff_low_high/demand_2050_med)*100:.1f}%)")
print()
print(f"Output dataframes:")
print(f"  demand (in tonnes): Year, Demand_Low, Demand_Med, Demand_High")
print(f"  demand_Mt (in Mt):  Year, Demand_Low, Demand_Med, Demand_High")
print()
print("Ready for emissions projection calculations.")
print()