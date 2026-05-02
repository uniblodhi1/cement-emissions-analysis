"""
Script extracted from notebook cell 6.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# LOAD DATA
# ============================================================================
df = pd.read_csv('outputs_historical_scopes.csv')

print("Data loaded successfully")
print(f"Shape: {df.shape}")
print(f"Year range: {df['year'].min():.0f} to {df['year'].max():.0f}\n")

# ============================================================================
# SELECT LATEST YEAR
# ============================================================================
latest_idx = df.shape[0] - 1
latest_year = df.loc[latest_idx, 'year']
print(f"Latest year: {latest_year:.0f}\n")

# ============================================================================
# PREPARE DATA FOR LATEST YEAR
# ============================================================================
s1_fuel = df.loc[latest_idx, 'CO2_S1_fuel_t']
s1_process = df.loc[latest_idx, 'CO2_S1_process_t']
s2_elec = df.loc[latest_idx, 'CO2_S2_elec_t']
s3_transport = df.loc[latest_idx, 'CO2_S3_transport_t']

# Calculate total
total = s1_fuel + s1_process + s2_elec + s3_transport

# Calculate percentages
pct_s1_fuel = (s1_fuel / total) * 100
pct_s1_process = (s1_process / total) * 100
pct_s2_elec = (s2_elec / total) * 100
pct_s3_transport = (s3_transport / total) * 100

print(f"Emissions breakdown for {latest_year:.0f}:")
print(f"  Total CO₂: {total / 1e6:.2f} Mt CO₂\n")
print(f"  Scope 1 Fuel:      {s1_fuel / 1e6:>8.2f} Mt ({pct_s1_fuel:>5.1f}%)")
print(f"  Scope 1 Process:   {s1_process / 1e6:>8.2f} Mt ({pct_s1_process:>5.1f}%)")
print(f"  Scope 2 Elec:      {s2_elec / 1e6:>8.2f} Mt ({pct_s2_elec:>5.1f}%)")
print(f"  Scope 3 Transport: {s3_transport / 1e6:>8.2f} Mt ({pct_s3_transport:>5.1f}%)\n")

# ============================================================================
# CREATE BAR CHART
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 7))

# Scope names and percentages
scopes = ['Scope 1\nFuel', 'Scope 1\nProcess', 'Scope 2\nElectricity', 'Scope 3\nTransport']
percentages = [pct_s1_fuel, pct_s1_process, pct_s2_elec, pct_s3_transport]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# Create bars
bars = ax.bar(scopes, percentages, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)

# Add percentage labels on top of bars
for bar, pct in zip(bars, percentages):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
            f'{pct:.1f}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Set labels and title
ax.set_ylabel('Percentage of Total CO₂ (%)', fontsize=12, fontweight='bold')
ax.set_title('Emission share by scope (latest year)', fontsize=14, fontweight='bold', pad=20)

# Set y-axis limits
ax.set_ylim(0, max(percentages) + 10)

# Add grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
ax.set_axisbelow(True)

# Add year annotation
ax.text(0.98, 0.97, f'Year: {latest_year:.0f}',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Customize ticks
ax.tick_params(axis='both', which='major', labelsize=10)

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_emission_share_by_scope.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# DETAILED SUMMARY
# ============================================================================
print("=" * 70)
print(f"EMISSION SHARE ANALYSIS - YEAR {latest_year:.0f}")
print("=" * 70)

print(f"\nScope 1 (Fuel Combustion + Process Emissions):")
s1_total = s1_fuel + s1_process
s1_total_pct = pct_s1_fuel + pct_s1_process
print(f"  Combined: {s1_total / 1e6:.2f} Mt CO₂ ({s1_total_pct:.1f}%)")
print(f"    ├─ Fuel combustion:    {s1_fuel / 1e6:.2f} Mt ({pct_s1_fuel:.1f}%)")
print(f"    └─ Clinker calcination: {s1_process / 1e6:.2f} Mt ({pct_s1_process:.1f}%)")

print(f"\nScope 2 (Electricity):")
print(f"  {s2_elec / 1e6:.2f} Mt CO₂ ({pct_s2_elec:.1f}%)")

print(f"\nScope 3 (Transport):")
print(f"  {s3_transport / 1e6:.2f} Mt CO₂ ({pct_s3_transport:.1f}%)")

print(f"\n" + "=" * 70)
print(f"TOTAL: {total / 1e6:.2f} Mt CO₂ (100.0%)")
print("=" * 70)

# Interpretation
print(f"\nKey Insights:")
if pct_s1_process > pct_s1_fuel:
    print(f"  • Clinker calcination (process emissions) slightly dominates fuel combustion")
else:
    print(f"  • Fuel combustion slightly exceeds process emissions")
print(f"  • Scope 1 (fuel + process) accounts for {s1_total_pct:.1f}% of total emissions")
print(f"  • Scope 2 (electricity) contributes {pct_s2_elec:.1f}%")
print(f"  • Scope 3 (transport) represents only {pct_s3_transport:.1f}% (minimal impact)")