"""
Script extracted from notebook cell 9.
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
# COMPUTE CUMULATIVE CO₂ EMISSIONS
# ============================================================================
# Convert CO2_total_t from tonnes to gigatonnes (Gt)
df['CO2_total_Gt'] = df['CO2_total_t'] / 1e9

# Calculate cumulative sum
df['cumulative_Gt'] = df['CO2_total_Gt'].cumsum()

# Extract year and cumulative data
years = df['year'].values
cumulative_Gt = df['cumulative_Gt'].values

print("Cumulative CO₂ Emissions (Gt):")
print(f"  Start (1991): {cumulative_Gt[0]:.4f} Gt CO₂")
print(f"  End ({int(years[-1])}): {cumulative_Gt[-1]:.4f} Gt CO₂")
print(f"  Total accumulated: {cumulative_Gt[-1]:.4f} Gt CO₂\n")

# Print key milestones
print("Cumulative emissions milestones:")
for milestone in [0.1, 0.5, 1.0, 1.5]:
    idx = np.where(cumulative_Gt >= milestone)[0]
    if len(idx) > 0:
        first_idx = idx[0]
        print(f"  {milestone:.1f} Gt reached in year {int(years[first_idx])}")
    else:
        print(f"  {milestone:.1f} Gt not reached within data range")

print()

# ============================================================================
# CREATE CUMULATIVE EMISSIONS PLOT
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Plot cumulative line
ax.plot(years, cumulative_Gt, linewidth=3, color='#d62728', marker='o',
        markersize=5, markerfacecolor='#d62728', markeredgecolor='white',
        markeredgewidth=0.5)

# Fill area under curve for visual emphasis
ax.fill_between(years, cumulative_Gt, alpha=0.2, color='#d62728')

# Set labels and title
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Cumulative CO₂ Emissions (Gt CO₂)', fontsize=12, fontweight='bold')
ax.set_title('Cumulative CO₂ emissions from cement sector',
             fontsize=14, fontweight='bold', pad=20)

# Grid for readability
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Set x-axis ticks every 5 years
ax.set_xticks(range(int(years.min()), int(years.max()) + 1, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# Add some padding to y-axis
y_min = 0
y_max = cumulative_Gt[-1]
y_margin = (y_max - y_min) * 0.05
ax.set_ylim(y_min, y_max + y_margin)

# Add annotation for final value
ax.annotate(f'{cumulative_Gt[-1]:.2f} Gt CO₂\n(Year {int(years[-1])})',
            xy=(years[-1], cumulative_Gt[-1]),
            xytext=(-60, -30),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1.5))

# Tight layout
plt.tight_layout()

# ============================================================================
# SAVE AND DISPLAY
# ============================================================================
output_file = 'cement_cumulative_emissions.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved: {output_file}\n")

plt.show()

# ============================================================================
# DETAILED ANALYSIS
# ============================================================================
print("=" * 80)
print("CUMULATIVE EMISSIONS ANALYSIS (1991-" + str(int(years[-1])) + ")")
print("=" * 80)

# Total cumulative
total_cumulative_Mt = df['CO2_total_Gt'].sum() * 1000  # Convert Gt back to Mt for detail
print(f"\nTotal cumulative CO₂ emissions: {cumulative_Gt[-1]:.4f} Gt CO₂")
print(f"                                 {total_cumulative_Mt:.2f} Mt CO₂")

# Average annual emissions
avg_annual = df['CO2_total_Gt'].mean()
print(f"\nAverage annual emissions: {avg_annual:.4f} Gt CO₂")
print(f"                          {avg_annual * 1000:.2f} Mt CO₂")

# Breakdown by decade
print(f"\nCumulative emissions by decade:")
decades = [(1990, 2000), (2000, 2010), (2010, 2020), (2020, 2030)]
for start, end in decades:
    decade_mask = (df['year'] >= start) & (df['year'] < end)
    if decade_mask.sum() > 0:
        decade_total = df.loc[decade_mask, 'CO2_total_Gt'].sum()
        decade_avg = df.loc[decade_mask, 'CO2_total_Gt'].mean()
        print(f"  {start}s: {decade_total:.4f} Gt (avg: {decade_avg:.4f} Gt/year)")

# Rate of accumulation analysis
print(f"\nRate of cumulative accumulation:")
for period_years in [5, 10]:
    if len(df) >= period_years:
        start_cum = cumulative_Gt[0]
        end_cum = cumulative_Gt[-1]
        avg_rate = (end_cum - start_cum) / len(df) * period_years
        print(f"  Per {period_years}-year period: ~{avg_rate:.4f} Gt CO₂")

# Acceleration analysis
print(f"\nAccumulation rate trend (last 3 years vs first 3 years):")
early_rate = cumulative_Gt[2] - cumulative_Gt[0]
late_rate = cumulative_Gt[-1] - cumulative_Gt[-3]
print(f"  First 3 years: {early_rate:.4f} Gt CO₂")
print(f"  Last 3 years:  {late_rate:.4f} Gt CO₂")
if late_rate > early_rate:
    change = ((late_rate / early_rate) - 1) * 100
    print(f"  Change: +{change:.1f}% (accelerating)")
else:
    change = ((early_rate / late_rate) - 1) * 100
    print(f"  Change: -{change:.1f}% (decelerating)")

# Breakdown by scope
print(f"\n" + "=" * 80)
print("CUMULATIVE EMISSIONS BY SCOPE")
print("=" * 80)

# Calculate cumulative by scope
df['cum_S1_fuel'] = (df['CO2_S1_fuel_t'] / 1e9).cumsum()
df['cum_S1_process'] = (df['CO2_S1_process_t'] / 1e9).cumsum()
df['cum_S2_elec'] = (df['CO2_S2_elec_t'] / 1e9).cumsum()
df['cum_S3_transport'] = (df['CO2_S3_transport_t'] / 1e9).cumsum()

s1_fuel_total = df['cum_S1_fuel'].iloc[-1]
s1_process_total = df['cum_S1_process'].iloc[-1]
s2_elec_total = df['cum_S2_elec'].iloc[-1]
s3_transport_total = df['cum_S3_transport'].iloc[-1]

s1_total = s1_fuel_total + s1_process_total
grand_total = cumulative_Gt[-1]

print(f"\nScope 1 (Fuel + Process): {s1_total:.4f} Gt CO₂ ({(s1_total/grand_total)*100:.1f}%)")
print(f"  ├─ Fuel combustion:     {s1_fuel_total:.4f} Gt CO₂ ({(s1_fuel_total/grand_total)*100:.1f}%)")
print(f"  └─ Clinker calcination: {s1_process_total:.4f} Gt CO₂ ({(s1_process_total/grand_total)*100:.1f}%)")
print(f"\nScope 2 (Electricity):    {s2_elec_total:.4f} Gt CO₂ ({(s2_elec_total/grand_total)*100:.1f}%)")
print(f"Scope 3 (Transport):      {s3_transport_total:.4f} Gt CO₂ ({(s3_transport_total/grand_total)*100:.1f}%)")

print(f"\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print(f"""
• Total cumulative CO₂ emissions from Pakistan's cement sector
  (1991–{int(years[-1])}): {cumulative_Gt[-1]:.2f} Gt CO₂

• Average annual emissions: {avg_annual:.4f} Gt CO₂ ({avg_annual*1000:.2f} Mt/year)

• Scope 1 dominates cumulative total, accounting for {(s1_total/grand_total)*100:.0f}% of
  all emissions from the sector over the 33-year period.

• The sector accumulated approximately {cumulative_Gt[-1]/len(df):.4f} Gt CO₂ per year on average.

• Peak accumulation period appears to be around 2015–2021, reflecting
  highest cement production levels in the historical record.
""")

print()