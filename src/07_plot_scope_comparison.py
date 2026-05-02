"""
Script extracted from notebook cell 7.
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
# COMPUTE ANNUAL SCOPE TOTALS (IN MT CO₂)
# ============================================================================
# Scope 1 = Fuel + Process
df['Scope1_Mt'] = (df['CO2_S1_fuel_t'] + df['CO2_S1_process_t']) / 1e6

# Scope 2 = Electricity
df['Scope2_Mt'] = df['CO2_S2_elec_t'] / 1e6

# Scope 3 = Transport
df['Scope3_Mt'] = df['CO2_S3_transport_t'] / 1e6

# Extract year and scope data
years = df['year'].values
scope1 = df['Scope1_Mt'].values
scope2 = df['Scope2_Mt'].values
scope3 = df['Scope3_Mt'].values

print("Scope Summary Statistics (Mt CO₂):\n")
print("SCOPE 1 (Fuel + Process):")
print(f"  Min: {scope1.min():.2f} Mt (Year {df.loc[scope1.argmin(), 'year']:.0f})")
print(f"  Max: {scope1.max():.2f} Mt (Year {df.loc[scope1.argmax(), 'year']:.0f})")
print(f"  Mean: {scope1.mean():.2f} Mt\n")

print("SCOPE 2 (Electricity):")
print(f"  Min: {scope2.min():.2f} Mt (Year {df.loc[scope2.argmin(), 'year']:.0f})")
print(f"  Max: {scope2.max():.2f} Mt (Year {df.loc[scope2.argmax(), 'year']:.0f})")
print(f"  Mean: {scope2.mean():.2f} Mt\n")

print("SCOPE 3 (Transport):")
print(f"  Min: {scope3.min():.2f} Mt (Year {df.loc[scope3.argmin(), 'year']:.0f})")
print(f"  Max: {scope3.max():.2f} Mt (Year {df.loc[scope3.argmax(), 'year']:.0f})")
print(f"  Mean: {scope3.mean():.2f} Mt\n")

# ============================================================================
# CREATE MULTI-LINE PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Plot three lines
ax.plot(years, scope1, linewidth=2.5, color='#1f77b4', marker='o',
        markersize=5, markerfacecolor='#1f77b4', markeredgecolor='white',
        markeredgewidth=0.5, label='Scope 1 (Fuel + Process)')

ax.plot(years, scope2, linewidth=2.5, color='#2ca02c', marker='s',
        markersize=5, markerfacecolor='#2ca02c', markeredgecolor='white',
        markeredgewidth=0.5, label='Scope 2 (Electricity)')

ax.plot(years, scope3, linewidth=2.5, color='#d62728', marker='^',
        markersize=5, markerfacecolor='#d62728', markeredgecolor='white',
        markeredgewidth=0.5, label='Scope 3 (Transport)')

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Comparison of Scope 1, Scope 2 and Scope 3 emissions',
             fontsize=14, fontweight='bold', pad=20)

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis ticks to show every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_min = min(scope1.min(), scope2.min(), scope3.min())
y_max = max(scope1.max(), scope2.max(), scope3.max())
y_margin = (y_max - y_min) * 0.05
ax.set_ylim(y_min - y_margin, y_max + y_margin)

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_scopes_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("SCOPE COMPARISON ANALYSIS (1991-2023)")
print("=" * 80)

# Cumulative totals
cum_scope1 = scope1.sum()
cum_scope2 = scope2.sum()
cum_scope3 = scope3.sum()
cum_total = cum_scope1 + cum_scope2 + cum_scope3

print(f"\nCumulative emissions over {len(years)} years:")
print(f"  Scope 1: {cum_scope1:>8.2f} Mt CO₂ ({(cum_scope1/cum_total)*100:>5.1f}%)")
print(f"  Scope 2: {cum_scope2:>8.2f} Mt CO₂ ({(cum_scope2/cum_total)*100:>5.1f}%)")
print(f"  Scope 3: {cum_scope3:>8.2f} Mt CO₂ ({(cum_scope3/cum_total)*100:>5.1f}%)")
print(f"  " + "─" * 45)
print(f"  TOTAL:   {cum_total:>8.2f} Mt CO₂ (100.0%)")

# Trend analysis
print(f"\nTrend Analysis:")
print(f"\n  Scope 1 (Fuel + Process):")
s1_change = scope1[-1] - scope1[0]
s1_pct_change = ((scope1[-1] / scope1[0]) - 1) * 100
print(f"    1991: {scope1[0]:.2f} Mt CO₂")
print(f"    2023: {scope1[-1]:.2f} Mt CO₂")
print(f"    Change: {s1_change:+.2f} Mt ({s1_pct_change:+.1f}%)")

print(f"\n  Scope 2 (Electricity):")
s2_change = scope2[-1] - scope2[0]
s2_pct_change = ((scope2[-1] / scope2[0]) - 1) * 100
print(f"    1991: {scope2[0]:.2f} Mt CO₂")
print(f"    2023: {scope2[-1]:.2f} Mt CO₂")
print(f"    Change: {s2_change:+.2f} Mt ({s2_pct_change:+.1f}%)")

print(f"\n  Scope 3 (Transport):")
s3_change = scope3[-1] - scope3[0]
s3_pct_change = ((scope3[-1] / scope3[0]) - 1) * 100
print(f"    1991: {scope3[0]:.2f} Mt CO₂")
print(f"    2023: {scope3[-1]:.2f} Mt CO₂")
print(f"    Change: {s3_change:+.2f} Mt ({s3_pct_change:+.1f}%)")

# Year-over-year growth analysis
print(f"\n\nYear-on-year growth rates (latest 5 years):")
for i in range(len(years) - 5, len(years) - 1):
    year = int(years[i])
    next_year = int(years[i + 1])
    s1_growth = ((scope1[i + 1] / scope1[i]) - 1) * 100
    s2_growth = ((scope2[i + 1] / scope2[i]) - 1) * 100
    s3_growth = ((scope3[i + 1] / scope3[i]) - 1) * 100
    print(f"  {year} → {next_year}:")
    print(f"    Scope 1: {s1_growth:>6.1f}% | Scope 2: {s2_growth:>6.1f}% | Scope 3: {s3_growth:>6.1f}%")

# Peak year analysis
print(f"\n\nPeak emissions by scope:")
print(f"  Scope 1 peak: {scope1.max():.2f} Mt in year {df.loc[scope1.argmax(), 'year']:.0f}")
print(f"  Scope 2 peak: {scope2.max():.2f} Mt in year {df.loc[scope2.argmax(), 'year']:.0f}")
print(f"  Scope 3 peak: {scope3.max():.2f} Mt in year {df.loc[scope3.argmax(), 'year']:.0f}")

print(f"\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print(f"""
• Scope 1 (fuel combustion + process) dominates, accounting for ~{(cum_scope1/cum_total)*100:.0f}% of total
  emissions, and closely follows cement production trends.

• Scope 2 (electricity) contributes ~{(cum_scope2/cum_total)*100:.0f}%, reflecting grid emissions from power
  consumption for clinker grinding and other processes.

• Scope 3 (transport) is minimal at ~{(cum_scope3/cum_total)*100:.0f}%, indicating trucking has low carbon
  intensity relative to production processes.

• The significant variation in all three scopes reflects cement production
  fluctuations driven by demand and industrial activity.
""")