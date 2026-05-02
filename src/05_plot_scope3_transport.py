"""
Script extracted from notebook cell 5.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np # Import numpy

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
# Convert CO2_S3_transport_t from tonnes to million tonnes (Mt)
df['S3_transport_Mt'] = df['CO2_S3_transport_t'] / 1e6

# Extract year and transport emissions
years = df['year'].values
transport_Mt = df['S3_transport_Mt'].values

print("Scope 3 Transport Emissions Statistics:")
print(f"  Minimum: {transport_Mt.min():.4f} Mt CO₂ (Year {df.loc[transport_Mt.argmin(), 'year']:.0f})")
print(f"  Maximum: {transport_Mt.max():.4f} Mt CO₂ (Year {df.loc[transport_Mt.argmax(), 'year']:.0f})")
print(f"  Average: {transport_Mt.mean():.4f} Mt CO₂")
print(f"  Median:  {np.median(transport_Mt):.4f} Mt CO₂") # Corrected line
print(f"  Range:   {transport_Mt.max() - transport_Mt.min():.4f} Mt CO₂\n")

# ============================================================================
# CREATE LINE PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(11, 6.5))

# Plot line graph
ax.plot(years, transport_Mt, linewidth=2.5, color='#d62728', marker='o',
        markersize=5, markerfacecolor='#d62728', markeredgecolor='white',
        markeredgewidth=0.5)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Scope 3 downstream transport emissions', fontsize=13, fontweight='bold', pad=20)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis ticks to show every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_min, y_max = transport_Mt.min(), transport_Mt.max()
y_margin = (y_max - y_min) * 0.1
ax.set_ylim(y_min - y_margin, y_max + y_margin)

# Tight layout to prevent label cutoff
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_scope3_transport_plot.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# SUMMARY ANALYSIS
# ============================================================================
print("=" * 70)
print("SCOPE 3 TRANSPORT EMISSIONS ANALYSIS")
print("=" * 70)

# Calculate trend
transport_change = transport_Mt[-1] - transport_Mt[0]
transport_pct_change = ((transport_Mt[-1] / transport_Mt[0]) - 1) * 100

print(f"\nPeriod: 1991 to 2023 ({len(years)} years)")
print(f"  Starting transport emissions (1991): {transport_Mt[0]:.4f} Mt CO₂")
print(f"  Ending transport emissions (2023):   {transport_Mt[-1]:.4f} Mt CO₂")
print(f"  Absolute change:                     {transport_change:+.4f} Mt CO₂")
print(f"  Percentage change:                   {transport_pct_change:+.2f}%")

# Find inflection points
min_idx = transport_Mt.argmin()
max_idx = transport_Mt.argmax()
print(f"\nKey observations:")
print(f"  Lowest transport emissions:  {transport_Mt[min_idx]:.4f} Mt CO₂ in year {df.loc[min_idx, 'year']:.0f}")
print(f"  Highest transport emissions: {transport_Mt[max_idx]:.4f} Mt CO₂ in year {df.loc[max_idx, 'year']:.0f}")

# Relationship to total emissions
total_emissions = df['CO2_total_t'].values / 1e6
transport_pct_of_total = (transport_Mt / total_emissions) * 100

print(f"\nTransport as percentage of total emissions:")
print(f"  1991: {transport_pct_of_total[0]:.2f}%")
print(f"  2023: {transport_pct_of_total[-1]:.2f}%")
print(f"  Average: {transport_pct_of_total.mean():.2f}%")

# Correlation with cement production
cement_production = df['cement_t'].values / 1e6
correlation = pd.Series(transport_Mt).corr(pd.Series(cement_production))
print(f"\nCorrelation with cement production: {correlation:.4f}")
if correlation > 0.8:
    print("  → Strong positive correlation (transport scales with production)")
elif correlation > 0.5:
    print("  → Moderate positive correlation")
else:
    print("  → Weak correlation")

# Decade analysis
print(f"\nDecade-wise transport emissions:")
for decade in [1990, 2000, 2010, 2020]:
    decade_mask = (df['year'] >= decade) & (df['year'] < decade + 10)
    if decade_mask.sum() > 0:
        decade_avg = df.loc[decade_mask, 'S3_transport_Mt'].mean()
        print(f"  {decade}s: {decade_avg:.4f} Mt CO₂")