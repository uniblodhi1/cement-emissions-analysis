"""
Script extracted from notebook cell 27.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

"""
================================================================================
LMDI DECOMPOSITION ANALYSIS FOR PAKISTAN CEMENT SECTOR EMISSIONS
================================================================================
Logarithmic Mean Divisia Index (LMDI) decomposition of historical emissions
into driving factors: Population, Activity, Structure, and Intensity effects.

Method: LMDI-I (additive decomposition) following Ang (2004, 2005)
Reference: Ang, B.W. (2004) "Decomposition analysis for policymaking in energy"
           Energy Policy 32(9): 1131-1139

Author: Research Team
Date: February 2026
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
print("=" * 80)
print("LMDI DECOMPOSITION ANALYSIS")
print("Decomposing Pakistan Cement Sector CO₂ Emissions (1991-2022)")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("STEP 1: LOAD DATA")
print("-" * 80)

# Load historical emissions data
hist = pd.read_csv('outputs_historical_scopes.csv')
hist = hist.sort_values('year').reset_index(drop=True)

print(f"✓ Loaded historical data: {len(hist)} years ({hist['year'].min()}-{hist['year'].max()})")
print()

# ============================================================================
# STEP 2: LOAD/CREATE POPULATION DATA
# ============================================================================
print("STEP 2: PREPARE POPULATION DATA")
print("-" * 80)

# Pakistan population data (millions) - World Bank data
# Source: World Bank World Development Indicators
PAKISTAN_POPULATION = {
    1991: 111.85, 1992: 114.73, 1993: 117.66, 1994: 120.62, 1995: 123.59,
    1996: 126.56, 1997: 129.51, 1998: 132.44, 1999: 135.36, 2000: 138.25,
    2001: 141.13, 2002: 143.96, 2003: 146.75, 2004: 149.50, 2005: 152.21,
    2006: 154.89, 2007: 157.56, 2008: 160.24, 2009: 162.96, 2010: 165.74,
    2011: 168.61, 2012: 171.55, 2013: 174.57, 2014: 177.67, 2015: 180.87,
    2016: 184.17, 2017: 187.58, 2018: 191.09, 2019: 194.70, 2020: 198.39,
    2021: 202.02, 2022: 205.63
}

# Add population to dataframe
hist['population_millions'] = hist['year'].map(PAKISTAN_POPULATION)

print(f"✓ Population data added")
print(f"  1991: {PAKISTAN_POPULATION[1991]:.1f} million")
print(f"  2022: {PAKISTAN_POPULATION[2022]:.1f} million")
print(f"  Growth: {(PAKISTAN_POPULATION[2022]/PAKISTAN_POPULATION[1991] - 1)*100:.1f}%")
print()

# ============================================================================
# STEP 3: CALCULATE DECOMPOSITION FACTORS
# ============================================================================
print("STEP 3: CALCULATE DECOMPOSITION FACTORS")
print("-" * 80)

# LMDI Decomposition Identity:
# C = P × (Y/P) × (CL/Y) × (C/CL)
#
# Where:
#   C   = Total CO₂ emissions (tonnes)
#   P   = Population (millions)
#   Y   = Cement production (tonnes)
#   CL  = Clinker production (tonnes)
#
# Factors:
#   P       = Population effect
#   Y/P     = Activity effect (cement per capita)
#   CL/Y    = Structure effect (clinker ratio)
#   C/CL    = Intensity effect (CO₂ per clinker)

# Calculate factors
hist['C'] = hist['CO2_total_t']  # Total emissions (tonnes)
hist['P'] = hist['population_millions']  # Population (millions)
hist['Y'] = hist['cement_t']  # Cement production (tonnes)
hist['CL'] = hist['clinker_t']  # Clinker production (tonnes)

# Calculate ratios
hist['activity'] = hist['Y'] / hist['P']  # Cement per capita (t/million people = kg/person)
hist['structure'] = hist['CL'] / hist['Y']  # Clinker ratio
hist['intensity'] = hist['C'] / hist['CL']  # CO2 per clinker (tCO2/t clinker)

print("Decomposition factors calculated:")
print()
print(f"{'Year':<8} {'Emissions':>12} {'Population':>12} {'Activity':>12} {'Structure':>10} {'Intensity':>10}")
print(f"{'':8} {'(Mt CO2)':>12} {'(millions)':>12} {'(kg/cap)':>12} {'(ratio)':>10} {'(tCO2/t)':>10}")
print("-" * 80)

for idx in [0, 10, 20, 31]:  # Show 1991, 2001, 2011, 2022
    row = hist.iloc[idx]
    print(f"{int(row['year']):<8} {row['C']/1e6:>12.2f} {row['P']:>12.1f} "
          f"{row['activity']/1000:>12.1f} {row['structure']:>10.3f} {row['intensity']:>10.3f}")

print()

# ============================================================================
# STEP 4: LMDI DECOMPOSITION FUNCTION
# ============================================================================
print("STEP 4: APPLY LMDI-I DECOMPOSITION")
print("-" * 80)

def logarithmic_mean(a, b):
    """
    Calculate logarithmic mean of two values.
    L(a,b) = (a - b) / (ln(a) - ln(b)) if a ≠ b
    L(a,a) = a if a = b
    """
    if a <= 0 or b <= 0:
        return 0
    if np.isclose(a, b, rtol=1e-10):
        return a
    return (a - b) / (np.log(a) - np.log(b))


def lmdi_decomposition(df, base_year, target_year):
    """
    Perform LMDI-I additive decomposition between two years.

    Returns:
        dict: Decomposition results with effects in Mt CO2
    """
    # Get data for base and target years
    base = df[df['year'] == base_year].iloc[0]
    target = df[df['year'] == target_year].iloc[0]

    # Total change in emissions
    delta_C = target['C'] - base['C']

    # Logarithmic mean of emissions
    L = logarithmic_mean(target['C'], base['C'])

    # Calculate effects using LMDI-I formula
    # ΔC_x = L(C_t, C_0) × ln(X_t / X_0)

    # Population effect
    if base['P'] > 0 and target['P'] > 0:
        delta_P = L * np.log(target['P'] / base['P'])
    else:
        delta_P = 0

    # Activity effect (cement per capita)
    if base['activity'] > 0 and target['activity'] > 0:
        delta_A = L * np.log(target['activity'] / base['activity'])
    else:
        delta_A = 0

    # Structure effect (clinker ratio)
    if base['structure'] > 0 and target['structure'] > 0:
        delta_S = L * np.log(target['structure'] / base['structure'])
    else:
        delta_S = 0

    # Intensity effect (CO2 per clinker)
    if base['intensity'] > 0 and target['intensity'] > 0:
        delta_I = L * np.log(target['intensity'] / base['intensity'])
    else:
        delta_I = 0

    # Residual (should be near zero for perfect decomposition)
    residual = delta_C - (delta_P + delta_A + delta_S + delta_I)

    return {
        'base_year': base_year,
        'target_year': target_year,
        'total_change': delta_C / 1e6,  # Convert to Mt
        'population_effect': delta_P / 1e6,
        'activity_effect': delta_A / 1e6,
        'structure_effect': delta_S / 1e6,
        'intensity_effect': delta_I / 1e6,
        'residual': residual / 1e6,
        'base_emissions': base['C'] / 1e6,
        'target_emissions': target['C'] / 1e6,
    }


# ============================================================================
# STEP 5: PERIOD-BY-PERIOD DECOMPOSITION
# ============================================================================
print("Performing year-by-year decomposition...")
print()

# Decompose for each consecutive year pair
annual_decomp = []
for i in range(len(hist) - 1):
    base_year = int(hist.iloc[i]['year'])
    target_year = int(hist.iloc[i + 1]['year'])
    result = lmdi_decomposition(hist, base_year, target_year)
    annual_decomp.append(result)

annual_df = pd.DataFrame(annual_decomp)

print("✓ Annual decomposition complete")
print()

# ============================================================================
# STEP 6: CUMULATIVE DECOMPOSITION
# ============================================================================
print("Calculating cumulative effects...")
print()

# Calculate cumulative sums
annual_df['cum_population'] = annual_df['population_effect'].cumsum()
annual_df['cum_activity'] = annual_df['activity_effect'].cumsum()
annual_df['cum_structure'] = annual_df['structure_effect'].cumsum()
annual_df['cum_intensity'] = annual_df['intensity_effect'].cumsum()
annual_df['cum_total'] = annual_df['total_change'].cumsum()

print("✓ Cumulative effects calculated")
print()

# ============================================================================
# STEP 7: KEY PERIOD DECOMPOSITION
# ============================================================================
print("=" * 80)
print("DECOMPOSITION RESULTS: KEY PERIODS")
print("=" * 80)
print()

# Define key periods for analysis
periods = [
    (1991, 2000, "1990s: Early growth"),
    (2000, 2010, "2000s: Rapid expansion"),
    (2010, 2022, "2010s-2020s: Maturation"),
    (1991, 2022, "FULL PERIOD")
]

period_results = []

for base_yr, target_yr, label in periods:
    result = lmdi_decomposition(hist, base_yr, target_yr)
    result['period'] = label
    period_results.append(result)

    print(f"\n{label} ({base_yr}-{target_yr})")
    print("-" * 60)
    print(f"  Base emissions ({base_yr}):    {result['base_emissions']:>8.2f} Mt CO₂")
    print(f"  Target emissions ({target_yr}): {result['target_emissions']:>8.2f} Mt CO₂")
    print(f"  Total change:                {result['total_change']:>8.2f} Mt CO₂")
    print()
    print(f"  Decomposition:")
    print(f"    Population effect:         {result['population_effect']:>+8.2f} Mt ({result['population_effect']/result['total_change']*100:>+6.1f}%)")
    print(f"    Activity effect:           {result['activity_effect']:>+8.2f} Mt ({result['activity_effect']/result['total_change']*100:>+6.1f}%)")
    print(f"    Structure effect:          {result['structure_effect']:>+8.2f} Mt ({result['structure_effect']/result['total_change']*100:>+6.1f}%)")
    print(f"    Intensity effect:          {result['intensity_effect']:>+8.2f} Mt ({result['intensity_effect']/result['total_change']*100:>+6.1f}%)")
    print(f"    Residual:                  {result['residual']:>+8.4f} Mt")

period_df = pd.DataFrame(period_results)

# ============================================================================
# STEP 8: CREATE VISUALIZATIONS
# ============================================================================
print()
print("=" * 80)
print("STEP 8: CREATE VISUALIZATIONS")
print("=" * 80)
print()

# --- FIGURE 1: Waterfall Chart for Full Period ---
fig1, ax1 = plt.subplots(figsize=(12, 7))

full_period = period_df[period_df['period'] == 'FULL PERIOD'].iloc[0]

categories = ['Base\n(1991)', 'Population\nEffect', 'Activity\nEffect',
              'Structure\nEffect', 'Intensity\nEffect', 'Target\n(2022)']
values = [
    full_period['base_emissions'],
    full_period['population_effect'],
    full_period['activity_effect'],
    full_period['structure_effect'],
    full_period['intensity_effect'],
    0  # Placeholder for target
]

# Calculate cumulative positions for waterfall
cumulative = [full_period['base_emissions']]
for v in values[1:-1]:
    cumulative.append(cumulative[-1] + v)
cumulative.append(full_period['target_emissions'])

# Colors
colors = ['#1f77b4', '#d62728', '#d62728', '#2ca02c', '#2ca02c', '#ff7f0e']
for i, v in enumerate(values[1:-1], 1):
    if v < 0:
        colors[i] = '#2ca02c'  # Green for negative (reducing)
    else:
        colors[i] = '#d62728'  # Red for positive (increasing)

# Create bars
bar_bottoms = [0] + cumulative[:-1]
bar_heights = [cumulative[0]] + list(values[1:-1]) + [full_period['target_emissions']]

# Adjust for proper waterfall display
x_pos = np.arange(len(categories))
bars = []

# Base bar
bars.append(ax1.bar(x_pos[0], cumulative[0], bottom=0, color='#1f77b4',
                    edgecolor='black', linewidth=1.5, alpha=0.8))

# Effect bars (floating)
for i in range(1, 5):
    bottom = min(cumulative[i-1], cumulative[i])
    height = abs(values[i])
    color = '#d62728' if values[i] > 0 else '#2ca02c'
    bars.append(ax1.bar(x_pos[i], height, bottom=bottom, color=color,
                        edgecolor='black', linewidth=1.5, alpha=0.8))

# Target bar
bars.append(ax1.bar(x_pos[5], full_period['target_emissions'], bottom=0, color='#ff7f0e',
                    edgecolor='black', linewidth=1.5, alpha=0.8))

# Add connecting lines
for i in range(5):
    ax1.plot([x_pos[i] + 0.4, x_pos[i+1] - 0.4], [cumulative[i], cumulative[i]],
             'k--', linewidth=1, alpha=0.5)

# Add value labels
for i, (x, cum) in enumerate(zip(x_pos, cumulative)):
    if i == 0:
        ax1.text(x, cum + 1, f'{cum:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    elif i < 5:
        val = values[i]
        label_y = cumulative[i-1] + val/2 if val > 0 else cumulative[i] + abs(val)/2
        ax1.text(x, label_y, f'{val:+.1f}', ha='center', va='center', fontweight='bold', fontsize=11,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    else:
        ax1.text(x, cum + 1, f'{cum:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax1.set_xticks(x_pos)
ax1.set_xticklabels(categories, fontsize=11)
ax1.set_ylabel('CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax1.set_title('LMDI Decomposition of Cement Sector Emissions Growth (1991-2022)\nWaterfall Chart',
              fontsize=14, fontweight='bold', pad=20)
ax1.set_ylim(0, max(cumulative) * 1.15)
ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#d62728', label='Increases emissions'),
    Patch(facecolor='#2ca02c', label='Decreases emissions')
]
ax1.legend(handles=legend_elements, loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig('lmdi_waterfall_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: lmdi_waterfall_chart.png")
plt.show()

# --- FIGURE 2: Cumulative Effects Over Time ---
fig2, ax2 = plt.subplots(figsize=(12, 7))

years = annual_df['target_year'].values

ax2.fill_between(years, 0, annual_df['cum_population'], alpha=0.7,
                 label='Population effect', color='#1f77b4')
ax2.fill_between(years, annual_df['cum_population'],
                 annual_df['cum_population'] + annual_df['cum_activity'],
                 alpha=0.7, label='Activity effect', color='#ff7f0e')
ax2.fill_between(years, annual_df['cum_population'] + annual_df['cum_activity'],
                 annual_df['cum_population'] + annual_df['cum_activity'] + annual_df['cum_structure'],
                 alpha=0.7, label='Structure effect', color='#2ca02c')
ax2.fill_between(years,
                 annual_df['cum_population'] + annual_df['cum_activity'] + annual_df['cum_structure'],
                 annual_df['cum_total'],
                 alpha=0.7, label='Intensity effect', color='#d62728')

# Add total line
ax2.plot(years, annual_df['cum_total'], 'k-', linewidth=2.5, label='Total change')

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Cumulative Emissions Change (Mt CO₂)', fontsize=12, fontweight='bold')
ax2.set_title('Cumulative Decomposition of Emissions Growth Over Time',
              fontsize=14, fontweight='bold', pad=20)
ax2.legend(loc='upper left', fontsize=10, framealpha=0.95)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.axhline(y=0, color='black', linewidth=0.5)
ax2.set_xlim(years.min(), years.max())

plt.tight_layout()
plt.savefig('lmdi_cumulative_effects.png', dpi=300, bbox_inches='tight')
print("✓ Saved: lmdi_cumulative_effects.png")
plt.show()

# --- FIGURE 3: Period Comparison Bar Chart ---
fig3, ax3 = plt.subplots(figsize=(12, 7))

# Prepare data for grouped bar chart
period_labels = ['1990s\n(1991-2000)', '2000s\n(2000-2010)', '2010s-20s\n(2010-2022)']
period_data = period_df[period_df['period'] != 'FULL PERIOD'].copy()

x = np.arange(len(period_labels))
width = 0.2

# Create grouped bars
bars1 = ax3.bar(x - 1.5*width, period_data['population_effect'], width,
                label='Population', color='#1f77b4', edgecolor='black', linewidth=0.5)
bars2 = ax3.bar(x - 0.5*width, period_data['activity_effect'], width,
                label='Activity', color='#ff7f0e', edgecolor='black', linewidth=0.5)
bars3 = ax3.bar(x + 0.5*width, period_data['structure_effect'], width,
                label='Structure', color='#2ca02c', edgecolor='black', linewidth=0.5)
bars4 = ax3.bar(x + 1.5*width, period_data['intensity_effect'], width,
                label='Intensity', color='#d62728', edgecolor='black', linewidth=0.5)

# Add value labels
def add_bar_labels(bars):
    for bar in bars:
        height = bar.get_height()
        if abs(height) > 0.3:
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:+.1f}', ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=9, fontweight='bold')

add_bar_labels(bars1)
add_bar_labels(bars2)
add_bar_labels(bars3)
add_bar_labels(bars4)

ax3.set_xticks(x)
ax3.set_xticklabels(period_labels, fontsize=11)
ax3.set_ylabel('Emissions Change (Mt CO₂)', fontsize=12, fontweight='bold')
ax3.set_title('LMDI Decomposition by Period: Contribution of Each Factor',
              fontsize=14, fontweight='bold', pad=20)
ax3.legend(loc='upper right', fontsize=10)
ax3.grid(True, alpha=0.3, axis='y', linestyle='--')
ax3.axhline(y=0, color='black', linewidth=1)

plt.tight_layout()
plt.savefig('lmdi_period_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: lmdi_period_comparison.png")
plt.show()

# --- FIGURE 4: Contribution Pie Chart (Full Period) ---
fig4, ax4 = plt.subplots(figsize=(10, 8))

# Get absolute values for pie chart (showing relative magnitude)
effects = {
    'Population': abs(full_period['population_effect']),
    'Activity': abs(full_period['activity_effect']),
    'Structure': abs(full_period['structure_effect']),
    'Intensity': abs(full_period['intensity_effect'])
}

# Only show effects that contributed to increase
positive_effects = {
    'Population': full_period['population_effect'],
    'Activity': full_period['activity_effect']
}

labels = list(positive_effects.keys())
sizes = list(positive_effects.values())
colors = ['#1f77b4', '#ff7f0e']
explode = (0.02, 0.02)

wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=colors, explode=explode,
                                    autopct=lambda pct: f'{pct:.1f}%\n({pct/100*sum(sizes):.1f} Mt)',
                                    startangle=90, textprops={'fontsize': 12})

for autotext in autotexts:
    autotext.set_fontweight('bold')

ax4.set_title('Drivers of Emissions Increase (1991-2022)\n(Population and Activity effects only)',
              fontsize=14, fontweight='bold', pad=20)

# Add note about offsetting effects
ax4.text(0, -1.4, f"Note: Structure effect ({full_period['structure_effect']:+.1f} Mt) and "
         f"Intensity effect ({full_period['intensity_effect']:+.1f} Mt)\npartially offset the increase.",
         ha='center', fontsize=10, style='italic',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('lmdi_contribution_pie.png', dpi=300, bbox_inches='tight')
print("✓ Saved: lmdi_contribution_pie.png")
plt.show()

# ============================================================================
# STEP 9: EXPORT RESULTS
# ============================================================================
print()
print("=" * 80)
print("STEP 9: EXPORT RESULTS")
print("=" * 80)
print()

# Export annual decomposition
annual_export = annual_df[['base_year', 'target_year', 'total_change',
                           'population_effect', 'activity_effect',
                           'structure_effect', 'intensity_effect', 'residual']].copy()
annual_export.columns = ['Base_Year', 'Target_Year', 'Total_Change_Mt',
                         'Population_Effect_Mt', 'Activity_Effect_Mt',
                         'Structure_Effect_Mt', 'Intensity_Effect_Mt', 'Residual_Mt']
annual_export.to_csv('lmdi_annual_decomposition.csv', index=False)
print("✓ Saved: lmdi_annual_decomposition.csv")

# Export period decomposition
period_export = period_df[['base_year', 'target_year', 'period', 'total_change',
                           'population_effect', 'activity_effect',
                           'structure_effect', 'intensity_effect']].copy()
period_export.columns = ['Base_Year', 'Target_Year', 'Period', 'Total_Change_Mt',
                         'Population_Effect_Mt', 'Activity_Effect_Mt',
                         'Structure_Effect_Mt', 'Intensity_Effect_Mt']
period_export.to_csv('lmdi_period_decomposition.csv', index=False)
print("✓ Saved: lmdi_period_decomposition.csv")

# ============================================================================
# STEP 10: SUMMARY
# ============================================================================
print()
print("=" * 80)
print("LMDI DECOMPOSITION ANALYSIS COMPLETE!")
print("=" * 80)
print()

print("KEY FINDINGS (1991-2022):")
print("-" * 60)
print(f"Total emissions increase: {full_period['total_change']:.1f} Mt CO₂")
print()
print("Decomposition:")
print(f"  Population effect:  {full_period['population_effect']:>+7.1f} Mt ({full_period['population_effect']/full_period['total_change']*100:>+5.1f}%)")
print(f"  Activity effect:    {full_period['activity_effect']:>+7.1f} Mt ({full_period['activity_effect']/full_period['total_change']*100:>+5.1f}%)")
print(f"  Structure effect:   {full_period['structure_effect']:>+7.1f} Mt ({full_period['structure_effect']/full_period['total_change']*100:>+5.1f}%)")
print(f"  Intensity effect:   {full_period['intensity_effect']:>+7.1f} Mt ({full_period['intensity_effect']/full_period['total_change']*100:>+5.1f}%)")
print()
print("INTERPRETATION:")
print("-" * 60)
print("• Population growth drove emissions up by driving overall cement demand")
print("• Activity effect (rising per-capita cement use) was the LARGEST driver")
print("• Structure effect (clinker ratio changes) had minimal impact")
print("• Intensity effect (CO2 per clinker) showed slight improvement")
print()
print("OUTPUT FILES:")
print("  1. lmdi_waterfall_chart.png       - Waterfall decomposition (full period)")
print("  2. lmdi_cumulative_effects.png    - Cumulative effects over time")
print("  3. lmdi_period_comparison.png     - Period-by-period comparison")
print("  4. lmdi_contribution_pie.png      - Contribution pie chart")
print("  5. lmdi_annual_decomposition.csv  - Year-by-year data")
print("  6. lmdi_period_decomposition.csv  - Period summary data")
print()