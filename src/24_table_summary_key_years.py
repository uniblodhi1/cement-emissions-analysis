"""
Script extracted from notebook cell 24.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np

# ============================================================================
# LOAD DATA
# ============================================================================
print("=" * 80)
print("SUMMARY TABLE - KEY YEARS")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')
future = pd.read_csv('outputs_future_scenarios.csv')

print(f"✓ Loaded historical data: {len(hist)} rows")
print(f"✓ Loaded future scenarios: {len(future)} rows\n")

# ============================================================================
# EXTRACT BASE YEAR (HISTORICAL)
# ============================================================================
BASE_YEAR = int(hist['year'].max())
print(f"Base year (historical): {BASE_YEAR}\n")

base_row = hist[hist['year'] == BASE_YEAR].iloc[0]

base_year_data = {
    'Year': BASE_YEAR,
    'Scenario': 'Historical',
    'Total_CO2_Mt': (base_row['CO2_total_t'] / 1e6),
    'CO2_intensity': base_row['CO2_intensity_t_per_tcement'],
    'S1_fuel_pct': (base_row['CO2_S1_fuel_t'] / base_row['CO2_total_t']) * 100,
    'S1_process_pct': (base_row['CO2_S1_process_t'] / base_row['CO2_total_t']) * 100,
    'S2_elec_pct': (base_row['CO2_S2_elec_t'] / base_row['CO2_total_t']) * 100,
    'S3_transport_pct': (base_row['CO2_S3_transport_t'] / base_row['CO2_total_t']) * 100,
}

print(f"BASE YEAR ({BASE_YEAR}) - HISTORICAL")
print(f"─" * 80)
print(f"Total CO₂:        {base_year_data['Total_CO2_Mt']:.2f} Mt")
print(f"Intensity:        {base_year_data['CO2_intensity']:.4f} tCO₂/t cement")
print(f"Scope 1 Fuel:     {base_year_data['S1_fuel_pct']:.1f}%")
print(f"Scope 1 Process:  {base_year_data['S1_process_pct']:.1f}%")
print(f"Scope 2 Elec:     {base_year_data['S2_elec_pct']:.1f}%")
print(f"Scope 3 Transport:{base_year_data['S3_transport_pct']:.1f}%")
print()

# ============================================================================
# EXTRACT FUTURE YEARS
# ============================================================================
future_med = future[future['DemandCase'] == 'Med'].copy()

key_years = [2030, 2040, 2050]
summary_rows = [base_year_data]

for year in key_years:
    print(f"Year {year} - FUTURE (Medium demand)")
    print(f"─" * 80)

    # Baseline scenario
    baseline_row = future_med[(future_med['Year'] == year) &
                             (future_med['Pathway'] == 'Baseline')].iloc[0]

    baseline_total = baseline_row['CO2_total_t'] / 1e6
    baseline_intensity = baseline_row['CO2_intensity']
    baseline_s1_fuel_pct = (baseline_row['CO2_S1_fuel_t'] / baseline_row['CO2_total_t']) * 100
    baseline_s1_process_pct = (baseline_row['CO2_S1_process_t'] / baseline_row['CO2_total_t']) * 100
    baseline_s2_elec_pct = (baseline_row['CO2_S2_elec_t'] / baseline_row['CO2_total_t']) * 100
    baseline_s3_transport_pct = (baseline_row['CO2_S3_transport_t'] / baseline_row['CO2_total_t']) * 100

    print(f"BASELINE:")
    print(f"  Total CO₂:        {baseline_total:.2f} Mt")
    print(f"  Intensity:        {baseline_intensity:.4f} tCO₂/t cement")
    print(f"  Scope 1 Fuel:     {baseline_s1_fuel_pct:.1f}%")
    print(f"  Scope 1 Process:  {baseline_s1_process_pct:.1f}%")
    print(f"  Scope 2 Elec:     {baseline_s2_elec_pct:.1f}%")
    print(f"  Scope 3 Transport:{baseline_s3_transport_pct:.1f}%")

    summary_rows.append({
        'Year': year,
        'Scenario': 'Baseline',
        'Total_CO2_Mt': baseline_total,
        'CO2_intensity': baseline_intensity,
        'S1_fuel_pct': baseline_s1_fuel_pct,
        'S1_process_pct': baseline_s1_process_pct,
        'S2_elec_pct': baseline_s2_elec_pct,
        'S3_transport_pct': baseline_s3_transport_pct,
    })

    # Integrated scenario
    integrated_row = future_med[(future_med['Year'] == year) &
                               (future_med['Pathway'] == 'Integrated')].iloc[0]

    integrated_total = integrated_row['CO2_total_t'] / 1e6
    integrated_intensity = integrated_row['CO2_intensity']
    integrated_s1_fuel_pct = (integrated_row['CO2_S1_fuel_t'] / integrated_row['CO2_total_t']) * 100
    integrated_s1_process_pct = (integrated_row['CO2_S1_process_t'] / integrated_row['CO2_total_t']) * 100
    integrated_s2_elec_pct = (integrated_row['CO2_S2_elec_t'] / integrated_row['CO2_total_t']) * 100
    integrated_s3_transport_pct = (integrated_row['CO2_S3_transport_t'] / integrated_row['CO2_total_t']) * 100

    print(f"\nINTEGRATED:")
    print(f"  Total CO₂:        {integrated_total:.2f} Mt")
    print(f"  Intensity:        {integrated_intensity:.4f} tCO₂/t cement")
    print(f"  Scope 1 Fuel:     {integrated_s1_fuel_pct:.1f}%")
    print(f"  Scope 1 Process:  {integrated_s1_process_pct:.1f}%")
    print(f"  Scope 2 Elec:     {integrated_s2_elec_pct:.1f}%")
    print(f"  Scope 3 Transport:{integrated_s3_transport_pct:.1f}%")

    # Calculate mitigation
    mitigation_total = baseline_total - integrated_total
    mitigation_pct = (mitigation_total / baseline_total) * 100

    print(f"\nMITIGATION (Integrated vs Baseline):")
    print(f"  Absolute: {mitigation_total:+.2f} Mt CO₂")
    print(f"  Percent:  {mitigation_pct:+.1f}%")
    print()

    summary_rows.append({
        'Year': year,
        'Scenario': 'Integrated',
        'Total_CO2_Mt': integrated_total,
        'CO2_intensity': integrated_intensity,
        'S1_fuel_pct': integrated_s1_fuel_pct,
        'S1_process_pct': integrated_s1_process_pct,
        'S2_elec_pct': integrated_s2_elec_pct,
        'S3_transport_pct': integrated_s3_transport_pct,
    })

# ============================================================================
# CREATE SUMMARY DATAFRAME
# ============================================================================
summary_df = pd.DataFrame(summary_rows)

print("=" * 80)
print("SUMMARY TABLE - COMPLETE")
print("=" * 80)
print()

# Display with formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Reorder columns for better readability
display_cols = ['Year', 'Scenario', 'Total_CO2_Mt', 'CO2_intensity',
                'S1_fuel_pct', 'S1_process_pct', 'S2_elec_pct', 'S3_transport_pct']
summary_display = summary_df[display_cols].copy()

pd.options.display.float_format = '{:.4f}'.format
print(summary_display.to_string(index=False))
print()

# ============================================================================
# SAVE TO CSV
# ============================================================================
output_csv = 'table_summary_key_years.csv'
summary_df.to_csv(output_csv, index=False)
print(f"✓ Summary table saved: {output_csv}\n")

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("KEY FINDINGS BY YEAR")
print("=" * 80)
print()

# 2030 Analysis
print("2030 PROJECTION:")
print("─" * 80)
baseline_2030 = summary_df[(summary_df['Year'] == 2030) &
                           (summary_df['Scenario'] == 'Baseline')].iloc[0]
integrated_2030 = summary_df[(summary_df['Year'] == 2030) &
                             (summary_df['Scenario'] == 'Integrated')].iloc[0]

mit_2030_total = baseline_2030['Total_CO2_Mt'] - integrated_2030['Total_CO2_Mt']
mit_2030_pct = (mit_2030_total / baseline_2030['Total_CO2_Mt']) * 100
intensity_improvement_2030 = ((baseline_2030['CO2_intensity'] - integrated_2030['CO2_intensity']) /
                              baseline_2030['CO2_intensity']) * 100

print(f"Baseline:         {baseline_2030['Total_CO2_Mt']:.2f} Mt CO₂, {baseline_2030['CO2_intensity']:.4f} tCO₂/t")
print(f"Integrated:       {integrated_2030['Total_CO2_Mt']:.2f} Mt CO₂, {integrated_2030['CO2_intensity']:.4f} tCO₂/t")
print(f"Mitigation:       {mit_2030_total:.2f} Mt ({mit_2030_pct:.1f}%)")
print(f"Intensity improvement: {intensity_improvement_2030:.1f}%")
print()

# 2040 Analysis
print("2040 PROJECTION:")
print("─" * 80)
baseline_2040 = summary_df[(summary_df['Year'] == 2040) &
                           (summary_df['Scenario'] == 'Baseline')].iloc[0]
integrated_2040 = summary_df[(summary_df['Year'] == 2040) &
                             (summary_df['Scenario'] == 'Integrated')].iloc[0]

mit_2040_total = baseline_2040['Total_CO2_Mt'] - integrated_2040['Total_CO2_Mt']
mit_2040_pct = (mit_2040_total / baseline_2040['Total_CO2_Mt']) * 100
intensity_improvement_2040 = ((baseline_2040['CO2_intensity'] - integrated_2040['CO2_intensity']) /
                              baseline_2040['CO2_intensity']) * 100

print(f"Baseline:         {baseline_2040['Total_CO2_Mt']:.2f} Mt CO₂, {baseline_2040['CO2_intensity']:.4f} tCO₂/t")
print(f"Integrated:       {integrated_2040['Total_CO2_Mt']:.2f} Mt CO₂, {integrated_2040['CO2_intensity']:.4f} tCO₂/t")
print(f"Mitigation:       {mit_2040_total:.2f} Mt ({mit_2040_pct:.1f}%)")
print(f"Intensity improvement: {intensity_improvement_2040:.1f}%")
print()

# 2050 Analysis
print("2050 PROJECTION:")
print("─" * 80)
baseline_2050 = summary_df[(summary_df['Year'] == 2050) &
                           (summary_df['Scenario'] == 'Baseline')].iloc[0]
integrated_2050 = summary_df[(summary_df['Year'] == 2050) &
                             (summary_df['Scenario'] == 'Integrated')].iloc[0]

mit_2050_total = baseline_2050['Total_CO2_Mt'] - integrated_2050['Total_CO2_Mt']
mit_2050_pct = (mit_2050_total / baseline_2050['Total_CO2_Mt']) * 100
intensity_improvement_2050 = ((baseline_2050['CO2_intensity'] - integrated_2050['CO2_intensity']) /
                              baseline_2050['CO2_intensity']) * 100

print(f"Baseline:         {baseline_2050['Total_CO2_Mt']:.2f} Mt CO₂, {baseline_2050['CO2_intensity']:.4f} tCO₂/t")
print(f"Integrated:       {integrated_2050['Total_CO2_Mt']:.2f} Mt CO₂, {integrated_2050['CO2_intensity']:.4f} tCO₂/t")
print(f"Mitigation:       {mit_2050_total:.2f} Mt ({mit_2050_pct:.1f}%)")
print(f"Intensity improvement: {intensity_improvement_2050:.1f}%")
print()

# ============================================================================
# TRAJECTORY ANALYSIS
# ============================================================================
print("=" * 80)
print("TRAJECTORY ANALYSIS")
print("=" * 80)
print()

# Historical to 2050 comparison
base_2023_co2 = base_year_data['Total_CO2_Mt']
base_2050_co2 = baseline_2050['Total_CO2_Mt']
int_2050_co2 = integrated_2050['Total_CO2_Mt']

baseline_growth = ((base_2050_co2 / base_2023_co2) - 1) * 100
integrated_growth = ((int_2050_co2 / base_2023_co2) - 1) * 100

print(f"Emissions trajectory (2023 → 2050):")
print()
print(f"Historical (2023):        {base_2023_co2:.2f} Mt CO₂")
print()
print(f"Baseline (no action):     {base_2050_co2:.2f} Mt CO₂")
print(f"  Growth:                 {baseline_growth:+.1f}% ({base_2050_co2 - base_2023_co2:+.2f} Mt)")
print()
print(f"Integrated (full action): {int_2050_co2:.2f} Mt CO₂")
print(f"  Growth:                 {integrated_growth:+.1f}% ({int_2050_co2 - base_2023_co2:+.2f} Mt)")
print()
print(f"Difference (avoided):     {base_2050_co2 - int_2050_co2:.2f} Mt CO₂")
print()

# Carbon intensity trajectory
base_2023_int = base_year_data['CO2_intensity']
base_2050_int = baseline_2050['CO2_intensity']
int_2050_int = integrated_2050['CO2_intensity']

int_change_baseline = ((base_2050_int / base_2023_int) - 1) * 100
int_change_integrated = ((int_2050_int / base_2023_int) - 1) * 100

print(f"Carbon intensity trajectory (2023 → 2050):")
print()
print(f"Historical (2023):        {base_2023_int:.4f} tCO₂/t cement")
print()
print(f"Baseline (no action):     {base_2050_int:.4f} tCO₂/t cement")
print(f"  Change:                 {int_change_baseline:+.1f}%")
print()
print(f"Integrated (full action): {int_2050_int:.4f} tCO₂/t cement")
print(f"  Change:                 {int_change_integrated:+.1f}%")
print()

# ============================================================================
# SCOPE COMPOSITION TRENDS
# ============================================================================
print("=" * 80)
print("SCOPE COMPOSITION TRENDS")
print("=" * 80)
print()

years_to_show = [BASE_YEAR, 2030, 2040, 2050]

print("BASELINE SCENARIO - Scope shares (%)")
print("─" * 80)
print(f"{'Year':<10} {'S1 Fuel':<12} {'S1 Process':<15} {'S2 Electricity':<18} {'S3 Transport':<15}")
print("─" * 80)

for year in years_to_show:
    row = summary_df[(summary_df['Year'] == year) & (summary_df['Scenario'].isin(['Historical', 'Baseline']))]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"{int(year):<10} {r['S1_fuel_pct']:>10.1f}%  {r['S1_process_pct']:>12.1f}%  {r['S2_elec_pct']:>15.1f}%  {r['S3_transport_pct']:>12.1f}%")

print()
print("INTEGRATED SCENARIO - Scope shares (%)")
print("─" * 80)
print(f"{'Year':<10} {'S1 Fuel':<12} {'S1 Process':<15} {'S2 Electricity':<18} {'S3 Transport':<15}")
print("─" * 80)

for year in years_to_show[1:]:  # Skip BASE_YEAR for integrated
    row = summary_df[(summary_df['Year'] == year) & (summary_df['Scenario'] == 'Integrated')]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"{int(year):<10} {r['S1_fuel_pct']:>10.1f}%  {r['S1_process_pct']:>12.1f}%  {r['S2_elec_pct']:>15.1f}%  {r['S3_transport_pct']:>12.1f}%")

print()

# ============================================================================
# KEY INSIGHTS
# ============================================================================
print("=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print()

cumulative_mitigation = mit_2030_total + mit_2040_total + mit_2050_total

print(f"""
1. SCALE OF TRANSFORMATION NEEDED:
   • Baseline pathway: +{baseline_growth:.0f}% emissions growth by 2050
   • Despite 3%/year demand growth, Integrated limits growth to {integrated_growth:+.1f}%
   • Demonstrates possibility of absolute emissions decoupling

2. CARBON INTENSITY IMPROVEMENTS:
   • Baseline remains constant ({base_2050_int:.4f} tCO₂/t, unchanged)
   • Integrated achieves {int_change_integrated:.0f}% improvement to {int_2050_int:.4f} tCO₂/t
   • {intensity_improvement_2050:.0f}% intensity reduction by 2050 (vs baseline)

3. MITIGATION MAGNITUDE:
   • 2030: {mit_2030_total:.2f} Mt CO₂ avoidance ({mit_2030_pct:.0f}%)
   • 2040: {mit_2040_total:.2f} Mt CO₂ avoidance ({mit_2040_pct:.0f}%)
   • 2050: {mit_2050_total:.2f} Mt CO₂ avoidance ({mit_2050_pct:.0f}%)
   • Approximate cumulative (3 snapshots): {cumulative_mitigation:.0f} Mt CO₂

4. SCOPE EVOLUTION:
   • Scope 1 remains dominant ({integrated_2050['S1_fuel_pct'] + integrated_2050['S1_process_pct']:.0f}% by 2050)
   • Scope 2 shrinks due to grid decarbonization (−{baseline_2050['S2_elec_pct'] - integrated_2050['S2_elec_pct']:.1f} pct points)
   • Process emissions (S1 Process) become larger share (clinker substitution limits absolute reduction)
   • Scope 3 remains negligible (<1% throughout)

5. DECARBONIZATION TIMELINE:
   • Early phase (2023-2030): Limited mitigation ({mit_2030_pct:.0f}% reduction)
   • Mid phase (2030-2040): Accelerating ({mit_2040_pct:.0f}% reduction)
   • Late phase (2040-2050): Maximum maturity ({mit_2050_pct:.0f}% reduction)
   • Demonstrates importance of immediate action (benefits compound over time)

6. POLICY IMPLICATIONS:
   • Neither demand constraint nor efficiency alone is sufficient
   • Integrated approach REQUIRED to achieve climate targets
   • Grid decarbonization is critical co-dependency
   • Clinker substitution cannot be delayed (linear to 2050 is tight)
   • Success requires coordinated action across sector and energy system
""")

print()