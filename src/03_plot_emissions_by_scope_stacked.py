"""
Script extracted from notebook cell 3.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# LOAD DATA
# ============================================================================
df = pd.read_csv('outputs_historical_scopes.csv')

print("Data loaded successfully")
print(f"Shape: {df.shape}")
print(f"Year range: {df['year'].min():.0f} to {df['year'].max():.0f}\n")

# ============================================================================
# PREPARE DATA
# ============================================================================
# Convert all emissions from tonnes to million tonnes (Mt)
df['S1_fuel_Mt'] = df['CO2_S1_fuel_t'] / 1e6
df['S1_process_Mt'] = df['CO2_S1_process_t'] / 1e6
df['S2_elec_Mt'] = df['CO2_S2_elec_t'] / 1e6
df['S3_transport_Mt'] = df['CO2_S3_transport_t'] / 1e6

# Extract year
years = df['year'].values

# Prepare data for stacked area plot
s1_fuel = df['S1_fuel_Mt'].values
s1_process = df['S1_process_Mt'].values
s2_elec = df['S2_elec_Mt'].values
s3_transport = df['S3_transport_Mt'].values

print("Emissions by scope (Mt CO₂) - Summary Statistics:")
print(f"  S1 Fuel:        min={s1_fuel.min():.2f}, max={s1_fuel.max():.2f}, mean={s1_fuel.mean():.2f}")
print(f"  S1 Process:     min={s1_process.min():.2f}, max={s1_process.max():.2f}, mean={s1_process.mean():.2f}")
print(f"  S2 Electricity: min={s2_elec.min():.2f}, max={s2_elec.max():.2f}, mean={s2_elec.mean():.2f}")
print(f"  S3 Transport:   min={s3_transport.min():.2f}, max={s3_transport.max():.2f}, mean={s3_transport.mean():.2f}\n")

# ============================================================================
# CREATE STACKED AREA PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Define colors for each scope
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# Create stacked area plot
ax.stackplot(years, s1_fuel, s1_process, s2_elec, s3_transport,
             labels=['Scope 1 Fuel', 'Scope 1 Process', 'Scope 2 Electricity', 'Scope 3 Transport'],
             colors=colors, alpha=0.8, edgecolor='white', linewidth=0.5)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('CO₂ emissions by scope', fontsize=14, fontweight='bold', pad=20)

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')

# Set x-axis ticks to show every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_max = (s1_fuel + s1_process + s2_elec + s3_transport).max()
ax.set_ylim(0, y_max * 1.05)

# Tight layout to prevent label cutoff
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_co2_by_scope_stacked.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("=" * 70)
print("SCOPE CONTRIBUTION ANALYSIS")
print("=" * 70)

# Calculate total by scope
total_s1_fuel = s1_fuel.sum()
total_s1_process = s1_process.sum()
total_s2_elec = s2_elec.sum()
total_s3_transport = s3_transport.sum()
total_all = total_s1_fuel + total_s1_process + total_s2_elec + total_s3_transport

# Calculate percentages
pct_s1_fuel = (total_s1_fuel / total_all) * 100
pct_s1_process = (total_s1_process / total_all) * 100
pct_s2_elec = (total_s2_elec / total_all) * 100
pct_s3_transport = (total_s3_transport / total_all) * 100

print(f"\nTotal cumulative emissions (1991–2023):")
print(f"  Scope 1 Fuel:        {total_s1_fuel:>8.2f} Mt CO₂ ({pct_s1_fuel:>5.1f}%)")
print(f"  Scope 1 Process:     {total_s1_process:>8.2f} Mt CO₂ ({pct_s1_process:>5.1f}%)")
print(f"  Scope 2 Electricity: {total_s2_elec:>8.2f} Mt CO₂ ({pct_s2_elec:>5.1f}%)")
print(f"  Scope 3 Transport:   {total_s3_transport:>8.2f} Mt CO₂ ({pct_s3_transport:>5.1f}%)")
print(f"  " + "─" * 50)
print(f"  TOTAL:               {total_all:>8.2f} Mt CO₂ (100.0%)")

print(f"\nLatest year (2023) breakdown:")
latest_s1_fuel = s1_fuel[-1]
latest_s1_process = s1_process[-1]
latest_s2_elec = s2_elec[-1]
latest_s3_transport = s3_transport[-1]
latest_total = latest_s1_fuel + latest_s1_process + latest_s2_elec + latest_s3_transport

print(f"  Scope 1 Fuel:        {latest_s1_fuel:>8.2f} Mt CO₂ ({(latest_s1_fuel/latest_total)*100:>5.1f}%)")
print(f"  Scope 1 Process:     {latest_s1_process:>8.2f} Mt CO₂ ({(latest_s1_process/latest_total)*100:>5.1f}%)")
print(f"  Scope 2 Electricity: {latest_s2_elec:>8.2f} Mt CO₂ ({(latest_s2_elec/latest_total)*100:>5.1f}%)")
print(f"  Scope 3 Transport:   {latest_s3_transport:>8.2f} Mt CO₂ ({(latest_s3_transport/latest_total)*100:>5.1f}%)")
print(f"  " + "─" * 50)
print(f"  TOTAL:               {latest_total:>8.2f} Mt CO₂ (100.0%)")