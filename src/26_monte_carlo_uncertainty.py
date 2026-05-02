"""
Script extracted from notebook cell 26.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

"""
================================================================================
MONTE CARLO UNCERTAINTY ANALYSIS FOR PAKISTAN CEMENT SECTOR EMISSIONS
================================================================================
This code performs probabilistic emissions projections with uncertainty bands.
Run this AFTER generating outputs_historical_scopes.csv

Author: Research Team
Date: February 2026
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================
N_SIMULATIONS = 10000  # Number of Monte Carlo simulations
START_YEAR = 2023
END_YEAR = 2050
PROJECTION_YEARS = np.arange(START_YEAR, END_YEAR + 1)

print("=" * 80)
print("MONTE CARLO UNCERTAINTY ANALYSIS")
print("=" * 80)
print(f"\nConfiguration:")
print(f"  Simulations: {N_SIMULATIONS:,}")
print(f"  Projection period: {START_YEAR} to {END_YEAR}")
print(f"  Years: {len(PROJECTION_YEARS)}")
print()

# ============================================================================
# STEP 1: LOAD HISTORICAL DATA AND EXTRACT BASELINE
# ============================================================================
print("=" * 80)
print("STEP 1: LOAD HISTORICAL DATA")
print("=" * 80)
print()

hist = pd.read_csv('outputs_historical_scopes.csv')
hist = hist.sort_values('year').reset_index(drop=True)

BASE_YEAR = int(hist['year'].max())
baseline_row = hist[hist['year'] == BASE_YEAR].iloc[0]

print(f"✓ Loaded historical data: {len(hist)} years")
print(f"✓ Base year: {BASE_YEAR}")
print()

# Extract baseline values
CEMENT_BASE = baseline_row['cement_t']  # tonnes
COAL_INT_BASE = baseline_row['coal_int_kgpt']  # kg coal / t cement
ELEC_INT_BASE = baseline_row['elec_int_kwhpt']  # kWh / t cement
CLINKER_RATIO_BASE = baseline_row['clinker_ratio']  # fraction
NCV = baseline_row['ncv']  # TJ/t coal
CO2_EF_COAL = baseline_row['co2_ef_tco2_per_tj']  # tCO2/TJ
OXID_FRAC = baseline_row['oxid_frac']  # fraction
CALC_EF = baseline_row['calc_ef']  # tCO2/t clinker
GRID_EF_BASE = baseline_row['grid_ef_kg_per_kwh']  # kgCO2/kWh

# Transport parameters
LOCAL_T_BASE = baseline_row['local_t']
EXP_N_T_BASE = baseline_row['exp_n_t']
EXP_S_T_BASE = baseline_row['exp_s_t']
DIST_LOCAL = baseline_row['dist_local_km']
DIST_EXP_N = baseline_row['dist_exp_n_km']
DIST_EXP_S = baseline_row['dist_exp_s_km']
CAP_ALLOWED = baseline_row['cap_allowed_t']
CAP_OVER = baseline_row['cap_over_t']
EF_ALLOWED = baseline_row['ef_allowed_gpkm']
EF_OVER = baseline_row['ef_over_gpkm']
FRAC_ALLOWED = 0.40
FRAC_OVER = 0.60

print("Baseline values extracted:")
print(f"  Cement production: {CEMENT_BASE/1e6:.2f} Mt")
print(f"  Coal intensity: {COAL_INT_BASE:.0f} kg/t")
print(f"  Electricity intensity: {ELEC_INT_BASE:.0f} kWh/t")
print(f"  Clinker ratio: {CLINKER_RATIO_BASE:.2f}")
print(f"  Grid EF: {GRID_EF_BASE:.4f} kgCO2/kWh")
print()

# ============================================================================
# STEP 2: DEFINE PARAMETER DISTRIBUTIONS
# ============================================================================
print("=" * 80)
print("STEP 2: DEFINE PARAMETER DISTRIBUTIONS")
print("=" * 80)
print()

# Parameter distributions for Monte Carlo sampling
# Format: (distribution_type, parameters)

PARAM_DISTRIBUTIONS = {
    # Demand growth rate (annual compound)
    # Triangular: (min=1%, mode=3%, max=5%)
    'demand_growth': ('triangular', 0.01, 0.03, 0.05),

    # Coal intensity improvement rate (annual)
    # Normal: mean=1.0%, std=0.3%
    'coal_efficiency_rate': ('normal', 0.010, 0.003),

    # Electricity intensity improvement rate (annual)
    # Normal: mean=1.2%, std=0.3%
    'elec_efficiency_rate': ('normal', 0.012, 0.003),

    # Clinker ratio target by 2050
    # Triangular: (min=0.70, mode=0.75, max=0.82)
    'clinker_ratio_2050': ('triangular', 0.70, 0.75, 0.82),

    # Grid EF reduction rate (annual)
    # Triangular: (min=1.0%, mode=2.0%, max=3.0%)
    'grid_ef_reduction_rate': ('triangular', 0.01, 0.02, 0.03),

    # Truck EF reduction rate (annual)
    # Triangular: (min=0.2%, mode=0.5%, max=1.0%)
    'truck_ef_reduction_rate': ('triangular', 0.002, 0.005, 0.010),

    # Process emission factor uncertainty
    # Normal: mean=0.523, std=0.02 (IPCC uncertainty ~5%)
    'calc_ef_uncertainty': ('normal', CALC_EF, CALC_EF * 0.05),

    # Coal emission factor uncertainty
    # Normal: mean=94.6, std=2.0 (IPCC uncertainty ~2%)
    'coal_ef_uncertainty': ('normal', CO2_EF_COAL, 2.0),
}

print("Parameter distributions defined:")
print()
for param, dist in PARAM_DISTRIBUTIONS.items():
    if dist[0] == 'triangular':
        print(f"  {param}: Triangular(min={dist[1]:.3f}, mode={dist[2]:.3f}, max={dist[3]:.3f})")
    elif dist[0] == 'normal':
        print(f"  {param}: Normal(mean={dist[1]:.4f}, std={dist[2]:.4f})")
print()

# ============================================================================
# STEP 3: SAMPLING FUNCTION
# ============================================================================
def sample_parameters(n_samples):
    """
    Sample parameters from defined distributions.

    Returns:
        dict: Dictionary of parameter arrays, each of length n_samples
    """
    samples = {}

    for param, dist in PARAM_DISTRIBUTIONS.items():
        if dist[0] == 'triangular':
            # scipy.stats.triang: c = (mode - min) / (max - min)
            min_val, mode_val, max_val = dist[1], dist[2], dist[3]
            c = (mode_val - min_val) / (max_val - min_val)
            scale = max_val - min_val
            samples[param] = stats.triang.rvs(c, loc=min_val, scale=scale, size=n_samples)

        elif dist[0] == 'normal':
            mean_val, std_val = dist[1], dist[2]
            samples[param] = stats.norm.rvs(loc=mean_val, scale=std_val, size=n_samples)

    return samples

# ============================================================================
# STEP 4: EMISSIONS CALCULATION FUNCTIONS
# ============================================================================
def calculate_scope1_fuel(cement_t, coal_int_kgpt, ncv, co2_ef, oxid_frac):
    """Calculate Scope 1 fuel combustion emissions (tonnes CO2)"""
    coal_t = cement_t * coal_int_kgpt / 1000  # Convert kg to tonnes
    energy_tj = coal_t * ncv
    co2_t = energy_tj * co2_ef * oxid_frac
    return co2_t

def calculate_scope1_process(cement_t, clinker_ratio, calc_ef):
    """Calculate Scope 1 process emissions (tonnes CO2)"""
    clinker_t = cement_t * clinker_ratio
    co2_t = clinker_t * calc_ef
    return co2_t

def calculate_scope2(cement_t, elec_int_kwhpt, grid_ef_kg_per_kwh):
    """Calculate Scope 2 electricity emissions (tonnes CO2)"""
    elec_kwh = cement_t * elec_int_kwhpt
    co2_t = elec_kwh * grid_ef_kg_per_kwh / 1000  # Convert kg to tonnes
    return co2_t

def calculate_scope3_transport(cement_t, local_frac, exp_n_frac, exp_s_frac,
                               dist_local, dist_exp_n, dist_exp_s,
                               cap_allowed, cap_over, ef_allowed, ef_over,
                               frac_allowed, frac_over):
    """Calculate Scope 3 transport emissions (tonnes CO2)"""

    local_t = cement_t * local_frac
    exp_n_t = cement_t * exp_n_frac
    exp_s_t = cement_t * exp_s_frac

    def route_emissions(flow_t, dist_km):
        trips_allowed = flow_t / cap_allowed
        trips_over = flow_t / cap_over

        co2_allowed = dist_km * frac_allowed * trips_allowed * ef_allowed / 1e6  # g to tonnes
        co2_over = dist_km * frac_over * trips_over * ef_over / 1e6

        return co2_allowed + co2_over

    co2_local = route_emissions(local_t, dist_local)
    co2_exp_n = route_emissions(exp_n_t, dist_exp_n)
    co2_exp_s = route_emissions(exp_s_t, dist_exp_s)

    return co2_local + co2_exp_n + co2_exp_s

# ============================================================================
# STEP 5: RUN MONTE CARLO SIMULATION
# ============================================================================
print("=" * 80)
print("STEP 5: RUN MONTE CARLO SIMULATION")
print("=" * 80)
print()

print(f"Running {N_SIMULATIONS:,} simulations...")
print()

# Sample all parameters
param_samples = sample_parameters(N_SIMULATIONS)

# Calculate transport flow fractions from baseline
total_flow_base = LOCAL_T_BASE + EXP_N_T_BASE + EXP_S_T_BASE
LOCAL_FRAC = LOCAL_T_BASE / total_flow_base
EXP_N_FRAC = EXP_N_T_BASE / total_flow_base
EXP_S_FRAC = EXP_S_T_BASE / total_flow_base

# Initialize results arrays
# Shape: (n_simulations, n_years)
results_total = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))
results_s1_fuel = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))
results_s1_process = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))
results_s2_elec = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))
results_s3_transport = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))
results_intensity = np.zeros((N_SIMULATIONS, len(PROJECTION_YEARS)))

# Run simulations
for sim in range(N_SIMULATIONS):
    if sim % 2000 == 0:
        print(f"  Simulation {sim:,} / {N_SIMULATIONS:,}...")

    # Get sampled parameters for this simulation
    demand_growth = param_samples['demand_growth'][sim]
    coal_eff_rate = param_samples['coal_efficiency_rate'][sim]
    elec_eff_rate = param_samples['elec_efficiency_rate'][sim]
    clinker_2050 = param_samples['clinker_ratio_2050'][sim]
    grid_ef_rate = param_samples['grid_ef_reduction_rate'][sim]
    truck_ef_rate = param_samples['truck_ef_reduction_rate'][sim]
    calc_ef_sim = param_samples['calc_ef_uncertainty'][sim]
    coal_ef_sim = param_samples['coal_ef_uncertainty'][sim]

    # Calculate year-by-year emissions
    for y_idx, year in enumerate(PROJECTION_YEARS):
        years_from_base = year - BASE_YEAR

        # Project cement production
        cement_t = CEMENT_BASE * (1 + demand_growth) ** years_from_base

        # Project coal intensity (efficiency improvement)
        coal_int = COAL_INT_BASE * (1 - coal_eff_rate) ** years_from_base

        # Project electricity intensity (efficiency improvement)
        elec_int = ELEC_INT_BASE * (1 - elec_eff_rate) ** years_from_base

        # Project clinker ratio (linear interpolation to 2050 target)
        years_to_2050 = END_YEAR - BASE_YEAR
        clinker_progress = years_from_base / years_to_2050
        clinker_ratio = CLINKER_RATIO_BASE - (CLINKER_RATIO_BASE - clinker_2050) * clinker_progress

        # Project grid emission factor (annual reduction)
        grid_ef = GRID_EF_BASE * (1 - grid_ef_rate) ** years_from_base

        # Project truck emission factors (annual reduction)
        ef_allowed_sim = EF_ALLOWED * (1 - truck_ef_rate) ** years_from_base
        ef_over_sim = EF_OVER * (1 - truck_ef_rate) ** years_from_base

        # Calculate emissions by scope
        s1_fuel = calculate_scope1_fuel(cement_t, coal_int, NCV, coal_ef_sim, OXID_FRAC)
        s1_process = calculate_scope1_process(cement_t, clinker_ratio, calc_ef_sim)
        s2_elec = calculate_scope2(cement_t, elec_int, grid_ef)
        s3_transport = calculate_scope3_transport(
            cement_t, LOCAL_FRAC, EXP_N_FRAC, EXP_S_FRAC,
            DIST_LOCAL, DIST_EXP_N, DIST_EXP_S,
            CAP_ALLOWED, CAP_OVER, ef_allowed_sim, ef_over_sim,
            FRAC_ALLOWED, FRAC_OVER
        )

        # Store results
        total_co2 = s1_fuel + s1_process + s2_elec + s3_transport
        results_s1_fuel[sim, y_idx] = s1_fuel
        results_s1_process[sim, y_idx] = s1_process
        results_s2_elec[sim, y_idx] = s2_elec
        results_s3_transport[sim, y_idx] = s3_transport
        results_total[sim, y_idx] = total_co2
        results_intensity[sim, y_idx] = total_co2 / cement_t

print()
print("✓ Monte Carlo simulation complete!")
print()

# ============================================================================
# STEP 6: CALCULATE PERCENTILES
# ============================================================================
print("=" * 80)
print("STEP 6: CALCULATE PERCENTILES")
print("=" * 80)
print()

percentile_levels = [5, 10, 25, 50, 75, 90, 95]

# Calculate percentiles for total emissions (in Mt)
percentiles_total = {}
for p in percentile_levels:
    percentiles_total[f'p{p}'] = np.percentile(results_total, p, axis=0) / 1e6  # Convert to Mt

# Calculate percentiles for intensity
percentiles_intensity = {}
for p in percentile_levels:
    percentiles_intensity[f'p{p}'] = np.percentile(results_intensity, p, axis=0)

print("Percentiles calculated for each projection year")
print()

# Display key statistics
print("TOTAL EMISSIONS (Mt CO₂) - KEY YEARS:")
print("-" * 80)
print(f"{'Year':<8} {'5th':>10} {'25th':>10} {'50th':>10} {'75th':>10} {'95th':>10}")
print("-" * 80)

for year in [2025, 2030, 2035, 2040, 2045, 2050]:
    y_idx = year - START_YEAR
    print(f"{year:<8} "
          f"{percentiles_total['p5'][y_idx]:>10.1f} "
          f"{percentiles_total['p25'][y_idx]:>10.1f} "
          f"{percentiles_total['p50'][y_idx]:>10.1f} "
          f"{percentiles_total['p75'][y_idx]:>10.1f} "
          f"{percentiles_total['p95'][y_idx]:>10.1f}")

print()
print("CARBON INTENSITY (tCO₂/t cement) - KEY YEARS:")
print("-" * 80)
print(f"{'Year':<8} {'5th':>10} {'25th':>10} {'50th':>10} {'75th':>10} {'95th':>10}")
print("-" * 80)

for year in [2025, 2030, 2035, 2040, 2045, 2050]:
    y_idx = year - START_YEAR
    print(f"{year:<8} "
          f"{percentiles_intensity['p5'][y_idx]:>10.3f} "
          f"{percentiles_intensity['p25'][y_idx]:>10.3f} "
          f"{percentiles_intensity['p50'][y_idx]:>10.3f} "
          f"{percentiles_intensity['p75'][y_idx]:>10.3f} "
          f"{percentiles_intensity['p95'][y_idx]:>10.3f}")

print()

# ============================================================================
# STEP 7: CREATE UNCERTAINTY BAND PLOTS
# ============================================================================
print("=" * 80)
print("STEP 7: CREATE UNCERTAINTY BAND PLOTS")
print("=" * 80)
print()

# --- FIGURE 1: Total Emissions with Uncertainty Bands ---
fig1, ax1 = plt.subplots(figsize=(12, 7))

# Plot uncertainty bands (from outer to inner for proper layering)
ax1.fill_between(PROJECTION_YEARS, percentiles_total['p5'], percentiles_total['p95'],
                 alpha=0.2, color='#d62728', label='90% CI (5th–95th percentile)')
ax1.fill_between(PROJECTION_YEARS, percentiles_total['p10'], percentiles_total['p90'],
                 alpha=0.3, color='#d62728', label='80% CI (10th–90th percentile)')
ax1.fill_between(PROJECTION_YEARS, percentiles_total['p25'], percentiles_total['p75'],
                 alpha=0.4, color='#d62728', label='50% CI (25th–75th percentile)')

# Plot median line
ax1.plot(PROJECTION_YEARS, percentiles_total['p50'], linewidth=2.5, color='#d62728',
         label='Median (50th percentile)', marker='o', markersize=4,
         markerfacecolor='#d62728', markeredgecolor='white', markeredgewidth=0.5)

# Add historical data for context
hist_years = hist['year'].values
hist_emissions = hist['CO2_total_t'].values / 1e6
ax1.plot(hist_years, hist_emissions, linewidth=2, color='#1f77b4',
         marker='s', markersize=4, label='Historical (1991–2022)')

# Labels and formatting
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax1.set_title('Projected CO₂ Emissions with Uncertainty Bands\n(Monte Carlo: 10,000 simulations)',
              fontsize=14, fontweight='bold', pad=20)

ax1.legend(loc='upper left', fontsize=10, framealpha=0.95)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_xlim(1990, 2052)

# Add annotation for 2050 range
y_idx_2050 = 2050 - START_YEAR
ax1.annotate(f'2050: {percentiles_total["p50"][y_idx_2050]:.0f} Mt\n'
             f'(90% CI: {percentiles_total["p5"][y_idx_2050]:.0f}–{percentiles_total["p95"][y_idx_2050]:.0f})',
             xy=(2050, percentiles_total['p50'][y_idx_2050]),
             xytext=(-80, 30), textcoords='offset points',
             fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.9),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'))

plt.tight_layout()
plt.savefig('monte_carlo_emissions_uncertainty.png', dpi=300, bbox_inches='tight')
print("✓ Saved: monte_carlo_emissions_uncertainty.png")
plt.show()

# --- FIGURE 2: Carbon Intensity with Uncertainty Bands ---
fig2, ax2 = plt.subplots(figsize=(12, 7))

# Plot uncertainty bands
ax2.fill_between(PROJECTION_YEARS, percentiles_intensity['p5'], percentiles_intensity['p95'],
                 alpha=0.2, color='#2ca02c', label='90% CI (5th–95th percentile)')
ax2.fill_between(PROJECTION_YEARS, percentiles_intensity['p10'], percentiles_intensity['p90'],
                 alpha=0.3, color='#2ca02c', label='80% CI (10th–90th percentile)')
ax2.fill_between(PROJECTION_YEARS, percentiles_intensity['p25'], percentiles_intensity['p75'],
                 alpha=0.4, color='#2ca02c', label='50% CI (25th–75th percentile)')

# Plot median line
ax2.plot(PROJECTION_YEARS, percentiles_intensity['p50'], linewidth=2.5, color='#2ca02c',
         label='Median (50th percentile)', marker='o', markersize=4,
         markerfacecolor='#2ca02c', markeredgecolor='white', markeredgewidth=0.5)

# Add historical data
hist_intensity = hist['CO2_intensity_t_per_tcement'].values
ax2.plot(hist_years, hist_intensity, linewidth=2, color='#1f77b4',
         marker='s', markersize=4, label='Historical (1991–2022)')

# Add global average reference line
ax2.axhline(y=0.56, color='#ff7f0e', linestyle='--', linewidth=2, alpha=0.7,
            label='Global average (0.56 tCO₂/t)')

# Labels and formatting
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Carbon Intensity (tCO₂ / t cement)', fontsize=12, fontweight='bold')
ax2.set_title('Projected Carbon Intensity with Uncertainty Bands\n(Monte Carlo: 10,000 simulations)',
              fontsize=14, fontweight='bold', pad=20)

ax2.legend(loc='upper right', fontsize=10, framealpha=0.95)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_xlim(1990, 2052)

# Add annotation for 2050 range
ax2.annotate(f'2050: {percentiles_intensity["p50"][y_idx_2050]:.3f}\n'
             f'(90% CI: {percentiles_intensity["p5"][y_idx_2050]:.3f}–{percentiles_intensity["p95"][y_idx_2050]:.3f})',
             xy=(2050, percentiles_intensity['p50'][y_idx_2050]),
             xytext=(-100, -50), textcoords='offset points',
             fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.9),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2'))

plt.tight_layout()
plt.savefig('monte_carlo_intensity_uncertainty.png', dpi=300, bbox_inches='tight')
print("✓ Saved: monte_carlo_intensity_uncertainty.png")
plt.show()

# --- FIGURE 3: Fan Chart (Alternative Visualization) ---
fig3, ax3 = plt.subplots(figsize=(12, 7))

# Create gradient bands from light to dark
colors = plt.cm.Reds(np.linspace(0.1, 0.7, 4))

# Outermost band
ax3.fill_between(PROJECTION_YEARS, percentiles_total['p5'], percentiles_total['p95'],
                 color=colors[0], alpha=0.8, label='5th–95th percentile')
ax3.fill_between(PROJECTION_YEARS, percentiles_total['p10'], percentiles_total['p90'],
                 color=colors[1], alpha=0.8, label='10th–90th percentile')
ax3.fill_between(PROJECTION_YEARS, percentiles_total['p25'], percentiles_total['p75'],
                 color=colors[2], alpha=0.8, label='25th–75th percentile')

# Median line
ax3.plot(PROJECTION_YEARS, percentiles_total['p50'], linewidth=3, color='darkred',
         label='Median', linestyle='-')

# Historical connection
ax3.plot(hist_years, hist_emissions, linewidth=2, color='#1f77b4',
         marker='s', markersize=3, label='Historical')

ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
ax3.set_ylabel('Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax3.set_title('Fan Chart: Emissions Projection Uncertainty',
              fontsize=14, fontweight='bold', pad=20)

ax3.legend(loc='upper left', fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.set_xlim(1990, 2052)

plt.tight_layout()
plt.savefig('monte_carlo_fan_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: monte_carlo_fan_chart.png")
plt.show()

# ============================================================================
# STEP 8: PARAMETER SENSITIVITY ANALYSIS (VARIANCE-BASED)
# ============================================================================
print()
print("=" * 80)
print("STEP 8: PARAMETER SENSITIVITY ANALYSIS")
print("=" * 80)
print()

# Calculate correlation between each parameter and 2050 total emissions
y_idx_2050 = 2050 - START_YEAR
emissions_2050 = results_total[:, y_idx_2050]

sensitivity_results = {}
for param in param_samples.keys():
    corr, p_value = stats.pearsonr(param_samples[param], emissions_2050)
    sensitivity_results[param] = {
        'correlation': corr,
        'p_value': p_value,
        'contribution': corr ** 2 * 100  # Approximate variance contribution
    }

# Sort by absolute correlation
sorted_params = sorted(sensitivity_results.items(),
                       key=lambda x: abs(x[1]['correlation']), reverse=True)

print("PARAMETER SENSITIVITY (Correlation with 2050 Emissions):")
print("-" * 80)
print(f"{'Parameter':<30} {'Correlation':>12} {'p-value':>12} {'Var. Contrib.':>15}")
print("-" * 80)

for param, results in sorted_params:
    print(f"{param:<30} {results['correlation']:>12.4f} {results['p_value']:>12.2e} {results['contribution']:>14.1f}%")

print()

# --- FIGURE 4: Tornado Diagram ---
fig4, ax4 = plt.subplots(figsize=(10, 7))

params = [p[0] for p in sorted_params]
correlations = [p[1]['correlation'] for p in sorted_params]

# Color based on positive/negative correlation
colors = ['#d62728' if c > 0 else '#1f77b4' for c in correlations]

y_pos = np.arange(len(params))
ax4.barh(y_pos, correlations, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

# Add value labels
for i, (param, corr) in enumerate(zip(params, correlations)):
    ax4.text(corr + 0.02 if corr > 0 else corr - 0.02, i,
             f'{corr:.3f}', va='center', ha='left' if corr > 0 else 'right',
             fontsize=10, fontweight='bold')

ax4.set_yticks(y_pos)
ax4.set_yticklabels([p.replace('_', ' ').title() for p in params])
ax4.set_xlabel('Correlation with 2050 Total Emissions', fontsize=12, fontweight='bold')
ax4.set_title('Parameter Sensitivity: Tornado Diagram\n(Correlation-based importance ranking)',
              fontsize=14, fontweight='bold', pad=20)
ax4.axvline(x=0, color='black', linewidth=1)
ax4.set_xlim(-1.1, 1.1)
ax4.grid(True, alpha=0.3, axis='x')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#d62728', label='Increases emissions'),
                   Patch(facecolor='#1f77b4', label='Decreases emissions')]
ax4.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('monte_carlo_tornado_diagram.png', dpi=300, bbox_inches='tight')
print("✓ Saved: monte_carlo_tornado_diagram.png")
plt.show()

# ============================================================================
# STEP 9: PROBABILITY DISTRIBUTION OF 2050 EMISSIONS
# ============================================================================
print()
print("=" * 80)
print("STEP 9: PROBABILITY DISTRIBUTION OF 2050 EMISSIONS")
print("=" * 80)
print()

emissions_2050_Mt = emissions_2050 / 1e6

# Calculate statistics
mean_2050 = np.mean(emissions_2050_Mt)
std_2050 = np.std(emissions_2050_Mt)
median_2050 = np.median(emissions_2050_Mt)

print("2050 EMISSIONS DISTRIBUTION STATISTICS:")
print("-" * 50)
print(f"  Mean:     {mean_2050:.1f} Mt CO₂")
print(f"  Std Dev:  {std_2050:.1f} Mt CO₂")
print(f"  Median:   {median_2050:.1f} Mt CO₂")
print(f"  Min:      {np.min(emissions_2050_Mt):.1f} Mt CO₂")
print(f"  Max:      {np.max(emissions_2050_Mt):.1f} Mt CO₂")
print()
print("  90% Confidence Interval:")
print(f"    Lower (5th percentile):  {np.percentile(emissions_2050_Mt, 5):.1f} Mt CO₂")
print(f"    Upper (95th percentile): {np.percentile(emissions_2050_Mt, 95):.1f} Mt CO₂")
print()

# --- FIGURE 5: Histogram of 2050 Emissions ---
fig5, ax5 = plt.subplots(figsize=(10, 6))

n, bins, patches = ax5.hist(emissions_2050_Mt, bins=50, density=True,
                            alpha=0.7, color='#d62728', edgecolor='white', linewidth=0.5)

# Add kernel density estimate
from scipy.stats import gaussian_kde
kde = gaussian_kde(emissions_2050_Mt)
x_range = np.linspace(emissions_2050_Mt.min(), emissions_2050_Mt.max(), 200)
ax5.plot(x_range, kde(x_range), linewidth=2.5, color='darkred', label='KDE')

# Add percentile lines
ax5.axvline(np.percentile(emissions_2050_Mt, 5), color='#1f77b4', linestyle='--',
            linewidth=2, label='5th percentile')
ax5.axvline(np.percentile(emissions_2050_Mt, 50), color='#ff7f0e', linestyle='-',
            linewidth=2, label='50th percentile (median)')
ax5.axvline(np.percentile(emissions_2050_Mt, 95), color='#1f77b4', linestyle='--',
            linewidth=2, label='95th percentile')

ax5.set_xlabel('2050 Total CO₂ Emissions (Mt CO₂)', fontsize=12, fontweight='bold')
ax5.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
ax5.set_title('Distribution of 2050 Emissions Projections\n(Monte Carlo: 10,000 simulations)',
              fontsize=14, fontweight='bold', pad=20)

ax5.legend(loc='upper right', fontsize=10)
ax5.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('monte_carlo_2050_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: monte_carlo_2050_distribution.png")
plt.show()

# ============================================================================
# STEP 10: EXPORT RESULTS TO CSV
# ============================================================================
print()
print("=" * 80)
print("STEP 10: EXPORT RESULTS TO CSV")
print("=" * 80)
print()

# Create summary dataframe
summary_data = {
    'Year': PROJECTION_YEARS,
    'Emissions_p5_Mt': percentiles_total['p5'],
    'Emissions_p10_Mt': percentiles_total['p10'],
    'Emissions_p25_Mt': percentiles_total['p25'],
    'Emissions_p50_Mt': percentiles_total['p50'],
    'Emissions_p75_Mt': percentiles_total['p75'],
    'Emissions_p90_Mt': percentiles_total['p90'],
    'Emissions_p95_Mt': percentiles_total['p95'],
    'Intensity_p5': percentiles_intensity['p5'],
    'Intensity_p10': percentiles_intensity['p10'],
    'Intensity_p25': percentiles_intensity['p25'],
    'Intensity_p50': percentiles_intensity['p50'],
    'Intensity_p75': percentiles_intensity['p75'],
    'Intensity_p90': percentiles_intensity['p90'],
    'Intensity_p95': percentiles_intensity['p95'],
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('monte_carlo_projection_summary.csv', index=False)
print("✓ Saved: monte_carlo_projection_summary.csv")

# Export sensitivity results
sensitivity_df = pd.DataFrame([
    {'Parameter': k, 'Correlation': v['correlation'], 'P_value': v['p_value'],
     'Variance_Contribution_pct': v['contribution']}
    for k, v in sorted_params
])
sensitivity_df.to_csv('monte_carlo_sensitivity_results.csv', index=False)
print("✓ Saved: monte_carlo_sensitivity_results.csv")

print()
print("=" * 80)
print("MONTE CARLO ANALYSIS COMPLETE!")
print("=" * 80)
print()
print("OUTPUT FILES GENERATED:")
print("  1. monte_carlo_emissions_uncertainty.png  - Emissions with uncertainty bands")
print("  2. monte_carlo_intensity_uncertainty.png  - Intensity with uncertainty bands")
print("  3. monte_carlo_fan_chart.png              - Fan chart visualization")
print("  4. monte_carlo_tornado_diagram.png        - Parameter sensitivity ranking")
print("  5. monte_carlo_2050_distribution.png      - 2050 emissions histogram")
print("  6. monte_carlo_projection_summary.csv     - Percentile data by year")
print("  7. monte_carlo_sensitivity_results.csv    - Sensitivity analysis results")
print()
print("KEY RESULTS:")
print(f"  2030 Emissions (90% CI): {percentiles_total['p5'][2030-START_YEAR]:.0f} – {percentiles_total['p95'][2030-START_YEAR]:.0f} Mt CO₂")
print(f"  2050 Emissions (90% CI): {percentiles_total['p5'][2050-START_YEAR]:.0f} – {percentiles_total['p95'][2050-START_YEAR]:.0f} Mt CO₂")
print(f"  Most sensitive parameter: {sorted_params[0][0]} (r = {sorted_params[0][1]['correlation']:.3f})")
print()