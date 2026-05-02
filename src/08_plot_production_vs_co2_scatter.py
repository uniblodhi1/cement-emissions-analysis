"""
Script extracted from notebook cell 8.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# ============================================================================
# LOAD DATA
# ============================================================================
df = pd.read_csv('outputs_historical_scopes.csv')

print("Data loaded successfully")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}\n")

# ============================================================================
# CHECK FOR CEMENT PRODUCTION COLUMN
# ============================================================================
if 'cement_t' not in df.columns:
    print("ERROR: 'cement_t' column not found in CSV")
    print("Available columns:", df.columns.tolist())
    print("\nSkipping scatter plot.")
    exit()

print("Cement production column found: 'cement_t'\n")

# ============================================================================
# PREPARE DATA
# ============================================================================
# Convert cement production from tonnes to million tonnes
cement_Mt = df['cement_t'].values / 1e6

# Convert CO2 from tonnes to million tonnes
co2_Mt = df['CO2_total_t'].values / 1e6

# Extract year for reference
years = df['year'].values

print(f"Year range: {years.min():.0f} to {years.max():.0f}")
print(f"Cement production range: {cement_Mt.min():.2f} to {cement_Mt.max():.2f} Mt")
print(f"Total CO₂ emissions range: {co2_Mt.min():.2f} to {co2_Mt.max():.2f} Mt\n")

# ============================================================================
# CALCULATE LINEAR REGRESSION
# ============================================================================
# Fit linear regression: CO2 = slope * cement + intercept
slope, intercept, r_value, p_value, std_err = stats.linregress(cement_Mt, co2_Mt)

# Calculate R-squared
r_squared = r_value ** 2

# Generate trend line
x_trend = np.array([cement_Mt.min(), cement_Mt.max()])
y_trend = slope * x_trend + intercept

print("=" * 70)
print("LINEAR REGRESSION ANALYSIS")
print("=" * 70)
print(f"\nRegression equation: CO₂ (Mt) = {slope:.4f} × Cement (Mt) + {intercept:.4f}")
print(f"\nStatistics:")
print(f"  Slope: {slope:.4f} (Mt CO₂ per Mt cement)")
print(f"  Intercept: {intercept:.4f} Mt CO₂")
print(f"  R-squared (R²): {r_squared:.4f}")
print(f"  Correlation (r): {r_value:.4f}")
print(f"  P-value: {p_value:.2e}")
print(f"  Standard error: {std_err:.4f}")

# Interpretation
if r_squared > 0.9:
    strength = "Very strong"
elif r_squared > 0.7:
    strength = "Strong"
elif r_squared > 0.5:
    strength = "Moderate"
else:
    strength = "Weak"

print(f"\nInterpretation:")
print(f"  → {strength} positive relationship (R² = {r_squared:.4f})")
print(f"  → For every 1 Mt increase in cement production,")
print(f"     CO₂ emissions increase by ~{slope:.2f} Mt CO₂")

if p_value < 0.001:
    print(f"  → Relationship is statistically significant (p < 0.001)")
elif p_value < 0.05:
    print(f"  → Relationship is statistically significant (p < 0.05)")
else:
    print(f"  → Relationship may not be statistically significant (p ≥ 0.05)")

print()

# ============================================================================
# CREATE SCATTER PLOT WITH TREND LINE
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

# Scatter plot
scatter = ax.scatter(cement_Mt, co2_Mt, s=80, color='#1f77b4', alpha=0.6,
                     edgecolors='#0d47a1', linewidth=1, label='Annual data')

# Add trend line
ax.plot(x_trend, y_trend, color='#d62728', linewidth=2.5, label=f'Linear fit (R² = {r_squared:.4f})')

# Set labels and title
ax.set_xlabel('Cement Production (Mt)', fontsize=12, fontweight='bold')
ax.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Relationship between cement production and CO₂ emissions',
             fontsize=14, fontweight='bold', pad=20)

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Add equation text on plot
equation_text = f'y = {slope:.4f}x + {intercept:.4f}\nR² = {r_squared:.4f}'
ax.text(0.98, 0.05, equation_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        family='monospace')

# Customize ticks
ax.tick_params(axis='both', which='major', labelsize=10)

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_production_vs_co2_scatter.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# ADDITIONAL ANALYSIS
# ============================================================================
print("=" * 70)
print("RESIDUAL ANALYSIS")
print("=" * 70)

# Calculate residuals
predicted = slope * cement_Mt + intercept
residuals = co2_Mt - predicted

print(f"\nResidual Statistics:")
print(f"  Mean: {residuals.mean():.4f} Mt CO₂")
print(f"  Std Dev: {residuals.std():.4f} Mt CO₂")
print(f"  Min: {residuals.min():.4f} Mt CO₂")
print(f"  Max: {residuals.max():.4f} Mt CO₂")

# Find outliers (residuals > 2 std dev)
threshold = 2 * residuals.std()
outliers = np.abs(residuals) > threshold
if outliers.sum() > 0:
    print(f"\nPotential outliers (|residual| > {threshold:.4f}):")
    for i in np.where(outliers)[0]:
        print(f"  Year {int(years[i])}: cement={cement_Mt[i]:.2f} Mt, "
              f"CO₂={co2_Mt[i]:.2f} Mt, residual={residuals[i]:+.4f} Mt")
else:
    print(f"\nNo significant outliers detected")

# Carbon intensity analysis
print(f"\n" + "=" * 70)
print("CARBON INTENSITY ANALYSIS")
print("=" * 70)

# Calculate carbon intensity (CO2 per ton cement)
intensity = (co2_Mt * 1e6) / df['cement_t'].values  # back to tCO₂/t cement

print(f"\nCarbon Intensity (tCO₂/t cement):")
print(f"  Min: {intensity.min():.4f}")
print(f"  Max: {intensity.max():.4f}")
print(f"  Mean: {intensity.mean():.4f}")
print(f"  Std Dev: {intensity.std():.4f}")

# Check if intensity is declining, stable, or increasing
intensity_change = intensity[-1] - intensity[0]
print(f"\nTrend: {intensity[0]:.4f} (1991) → {intensity[-1]:.4f} ({int(years[-1])})")
if abs(intensity_change) < 0.01:
    print(f"  → Intensity is remarkably stable (change: {intensity_change:+.4f})")
elif intensity_change < 0:
    print(f"  → Intensity is improving/declining (change: {intensity_change:+.4f})")
else:
    print(f"  → Intensity is worsening/increasing (change: {intensity_change:+.4f})")

print()