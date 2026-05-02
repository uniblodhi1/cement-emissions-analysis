"""
Script extracted from notebook cell 2.
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
# Convert CO2_total_t from tonnes to million tonnes (Mt)
df['CO2_total_Mt'] = df['CO2_total_t'] / 1e6

# Extract year and emissions
years = df['year']
emissions_Mt = df['CO2_total_Mt']

print(f"Total emissions range: {emissions_Mt.min():.2f} to {emissions_Mt.max():.2f} Mt CO₂\n")

# ============================================================================
# CREATE PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Plot line graph
ax.plot(years, emissions_Mt, linewidth=2.5, color='#d62728', marker='o',
        markersize=4, markerfacecolor='#d62728', markeredgecolor='white',
        markeredgewidth=0.5)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title("Total CO₂ emissions from Pakistan's cement sector (Scope 1–3)",
             fontsize=13, fontweight='bold', pad=20)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis to show every few years for clarity
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_min, y_max = emissions_Mt.min(), emissions_Mt.max()
y_margin = (y_max - y_min) * 0.05
ax.set_ylim(y_min - y_margin, y_max + y_margin)

# Tight layout to prevent label cutoff
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_co2_emissions_plot.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# Print summary statistics
print("=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)
print(f"Minimum emissions: {emissions_Mt.min():.2f} Mt CO₂ (Year {df.loc[emissions_Mt.idxmin(), 'year']:.0f})")
print(f"Maximum emissions: {emissions_Mt.max():.2f} Mt CO₂ (Year {df.loc[emissions_Mt.idxmax(), 'year']:.0f})")
print(f"Average emissions: {emissions_Mt.mean():.2f} Mt CO₂")
print(f"Median emissions: {emissions_Mt.median():.2f} Mt CO₂")
print(f"Total growth (1991-2023): {((emissions_Mt.iloc[-1] / emissions_Mt.iloc[0]) - 1) * 100:.1f}%")