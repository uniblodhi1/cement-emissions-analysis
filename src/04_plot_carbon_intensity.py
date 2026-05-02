"""
Script extracted from notebook cell 4.
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
years = df['year']
intensity = df['CO2_intensity_t_per_tcement']

print(f"Carbon intensity range: {intensity.min():.3f} to {intensity.max():.3f} tCO₂/t cement\n")

# ============================================================================
# CREATE PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(years, intensity, linewidth=2.5, color='#1f77b4', marker='o',
        markersize=4, markerfacecolor='#1f77b4', markeredgecolor='white',
        markeredgewidth=0.5)

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Carbon Intensity (tCO₂ / t cement)', fontsize=12, fontweight='bold')
ax.set_title('Carbon intensity of cement production', fontsize=13, fontweight='bold', pad=20)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis to show every few years for clarity
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_min, y_max = intensity.min(), intensity.max()
y_margin = (y_max - y_min) * 0.05
ax.set_ylim(y_min - y_margin, y_max + y_margin)

# Tight layout to prevent label cutoff
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_carbon_intensity_plot.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("=" * 60)
print("CARBON INTENSITY STATISTICS")
print("=" * 60)

min_intensity = intensity.min()
max_intensity = intensity.max()
mean_intensity = intensity.mean()
min_year = df.loc[intensity.idxmin(), 'year']
max_year = df.loc[intensity.idxmax(), 'year']

start_intensity = intensity.iloc[0]
end_intensity = intensity.iloc[-1]
change_intensity = end_intensity - start_intensity
pct_change_intensity = ((end_intensity / start_intensity) - 1) * 100

print(f"Minimum intensity: {min_intensity:.4f} tCO₂/t cement (Year {min_year:.0f})")
print(f"Maximum intensity: {max_intensity:.4f} tCO₂/t cement (Year {max_year:.0f})")
print(f"Average intensity: {mean_intensity:.4f} tCO₂/t cement")
print(f"Range: {(max_intensity - min_intensity):.4f} tCO₂/t cement\n")

print("Trend Analysis:")
print(f"Start ({years.min():.0f}): {start_intensity:.4f} tCO₂/t cement")
print(f"End ({years.max():.0f}): {end_intensity:.4f} tCO₂/t cement")
print(f"Absolute change: {change_intensity:+.4f} tCO₂/t cement")
print(f"Percentage change: {pct_change_intensity:+.2f}%\n")

print("Interpretation: Pakistan's cement sector shows a highly stable carbon intensity over the 33-year period (1991–2022), fluctuating around 0.96 tCO₂/t cement. This indicates consistent production efficiency despite significant variations in cement production volumes.")