"""
Script extracted from notebook cell 10.
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
# CREATE INDEXED SERIES (BASE YEAR = 100)
# ============================================================================
# Get first year value as base
base_value = df['CO2_total_t'].iloc[0]
base_year = df['year'].iloc[0]

print(f"Base year: {base_year:.0f}")
print(f"Base value (CO₂): {base_value / 1e6:.2f} Mt CO₂\n")

# Calculate index: (current value / base value) * 100
df['CO2_index'] = (df['CO2_total_t'] / base_value) * 100

# Extract year and index data
years = df['year'].values
index = df['CO2_index'].values

print("Indexed Series Summary:")
print(f"  Base index (1991): {index[0]:.2f}")
print(f"  Minimum index: {index.min():.2f} (Year {df.loc[index.argmin(), 'year']:.0f})")
print(f"  Maximum index: {index.max():.2f} (Year {df.loc[index.argmax(), 'year']:.0f})")
print(f"  Latest index ({int(years[-1])}): {index[-1]:.2f}\n")

# Growth analysis
total_growth = index[-1] - index[0]
pct_growth = ((index[-1] / index[0]) - 1) * 100
print(f"Overall Growth ({int(base_year)} to {int(years[-1])}):")
print(f"  Absolute change: {total_growth:+.2f} index points")
print(f"  Percentage change: {pct_growth:+.1f}%\n")

# ============================================================================
# CREATE INDEXED GROWTH PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Plot indexed line
ax.plot(years, index, linewidth=2.8, color='#d62728', marker='o',
        markersize=5, markerfacecolor='#d62728', markeredgecolor='white',
        markeredgewidth=0.5, label='CO₂ Emissions Index')

# Add baseline (100) reference line
ax.axhline(y=100, color='#1f77b4', linestyle='--', linewidth=2, alpha=0.7, label='Base year (100)')

# Highlight key milestones
if index.max() >= 150:
    ax.axhline(y=150, color='#ff7f0e', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(years[0], 151, '150', fontsize=9, color='#ff7f0e', fontweight='bold')

if index.min() <= 90:
    ax.axhline(y=90, color='#2ca02c', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(years[0], 89, '90', fontsize=9, color='#2ca02c', fontweight='bold')

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Index (Base Year = 100)', fontsize=12, fontweight='bold')
ax.set_title('Indexed growth of cement sector CO₂ emissions (base year = 100)',
             fontsize=14, fontweight='bold', pad=20)

# Add legend
ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black', fancybox=True)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis ticks every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Set y-axis with appropriate range
y_min = max(50, index.min() - 10)
y_max = min(250, index.max() + 10)
ax.set_ylim(y_min, y_max)

# Add annotation for final value
ax.annotate(f'Index: {index[-1]:.1f}\n({pct_growth:+.1f}% growth)',
            xy=(years[-1], index[-1]),
            xytext=(-80, 30),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', lw=1.5))

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_indexed_growth.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("INDEXED GROWTH ANALYSIS")
print("=" * 80)

# Period-by-period analysis
print(f"\nGrowth by decade:")
decades = [(1991, 2000), (2000, 2010), (2010, 2020), (2020, 2024)]
for start, end in decades:
    mask = (df['year'] >= start) & (df['year'] <= end)
    if mask.sum() > 0:
        start_idx = df.loc[mask, 'CO2_index'].iloc[0]
        end_idx = df.loc[mask, 'CO2_index'].iloc[-1]
        decade_growth = end_idx - start_idx
        decade_pct = ((end_idx / start_idx) - 1) * 100
        print(f"  {start}–{end}: {start_idx:.1f} → {end_idx:.1f} "
              f"(+{decade_growth:.1f} points, {decade_pct:+.1f}%)")

# Year-over-year growth rates (latest 10 years)
print(f"\nYear-over-year growth rates (latest 10 years):")
for i in range(max(0, len(df) - 10), len(df) - 1):
    year = int(df['year'].iloc[i])
    next_year = int(df['year'].iloc[i + 1])
    yoy_change = df['CO2_index'].iloc[i + 1] - df['CO2_index'].iloc[i]
    yoy_pct = (yoy_change / df['CO2_index'].iloc[i]) * 100
    print(f"  {year} → {next_year}: {yoy_change:+.1f} points ({yoy_pct:+.2f}%)")

# Volatility analysis
print(f"\nVolatility Analysis:")
yoy_changes = np.diff(index)
print(f"  Average annual change: {yoy_changes.mean():.2f} index points")
print(f"  Std dev of changes: {yoy_changes.std():.2f}")
print(f"  Max increase (year): +{yoy_changes.max():.2f}")
print(f"  Max decrease (year): {yoy_changes.min():.2f}")

# Identify turning points
print(f"\nKey turning points:")
local_min = []
local_max = []
for i in range(1, len(index) - 1):
    if index[i] < index[i-1] and index[i] < index[i+1]:
        local_min.append((i, index[i], years[i]))
    elif index[i] > index[i-1] and index[i] > index[i+1]:
        local_max.append((i, index[i], years[i]))

if local_min:
    print(f"  Minimum points:")
    for idx, val, year in local_min:
        print(f"    Year {int(year)}: {val:.1f}")

if local_max:
    print(f"  Maximum points:")
    for idx, val, year in local_max[-3:]:  # Show last 3
        print(f"    Year {int(year)}: {val:.1f}")

# Categorize growth phases
print(f"\n" + "=" * 80)
print("GROWTH PHASE ANALYSIS")
print("=" * 80)

early_period = (df['year'] >= 1991) & (df['year'] < 2000)
middle_period = (df['year'] >= 2000) & (df['year'] < 2010)
recent_period = (df['year'] >= 2010)

early_avg = df.loc[early_period, 'CO2_index'].mean()
middle_avg = df.loc[middle_period, 'CO2_index'].mean()
recent_avg = df.loc[recent_period, 'CO2_index'].mean()

print(f"\nAverage index by period:")
print(f"  1991–1999:   {early_avg:.1f}")
print(f"  2000–2009:   {middle_avg:.1f}")
print(f"  2010–2023:   {recent_avg:.1f}")

# Calculate acceleration
early_to_mid = middle_avg - early_avg
mid_to_recent = recent_avg - middle_avg
print(f"\nGrowth rate:")
print(f"  1990s→2000s:  {early_to_mid:+.1f} index points")
print(f"  2000s→2010s:  {mid_to_recent:+.1f} index points")

if mid_to_recent > 0 and early_to_mid > 0:
    if mid_to_recent > early_to_mid:
        print(f"  → Accelerating growth")
    else:
        print(f"  → Decelerating growth")
elif mid_to_recent < 0:
    print(f"  → Recent decline or stabilization")

# Comparison to cement production index
print(f"\n" + "=" * 80)
print("COMPARISON: CO₂ INDEX vs CEMENT PRODUCTION INDEX")
print("=" * 80)

cement_base = df['cement_t'].iloc[0]
df['cement_index'] = (df['cement_t'] / cement_base) * 100

cement_index_final = df['cement_index'].iloc[-1]
cement_growth = ((cement_index_final / 100) - 1) * 100

print(f"\nCement production index (base year = 100):")
print(f"  Final value ({int(years[-1])}): {cement_index_final:.1f}")
print(f"  Growth: {cement_growth:+.1f}%")
print(f"\nCO₂ emissions index (base year = 100):")
print(f"  Final value ({int(years[-1])}): {index[-1]:.1f}")
print(f"  Growth: {pct_growth:+.1f}%")
print(f"\nIntensity relationship:")
if abs(index[-1] - cement_index_final) < 5:
    print(f"  → CO₂ and cement production grow at similar rates (constant intensity)")
elif index[-1] > cement_index_final:
    print(f"  → CO₂ growing faster than production (worsening intensity)")
else:
    print(f"  → CO₂ growing slower than production (improving intensity)")

print()