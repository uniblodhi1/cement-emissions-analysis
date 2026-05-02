# Cement Sector CO₂ Emissions Analysis

This repository contains the Python workflow extracted from the notebook `Python_Code(paper_1)11_Feb_26.ipynb`.

## What the code does

The workflow estimates and analyzes Pakistan cement-sector CO₂ emissions using historical production and parameter data from `Paper_Data.xlsx`.

Main components:

1. **Historical emissions calculation**
   - Reads cement-sector input data from Excel.
   - Calculates Scope 1 fuel-combustion emissions.
   - Calculates Scope 1 process/calcination emissions.
   - Calculates Scope 2 grid-electricity emissions.
   - Calculates Scope 3 downstream trucking emissions.
   - Exports `outputs_historical_scopes.csv`.

2. **Historical plots and diagnostics**
   - Total emissions trend.
   - Scope-wise stacked emissions.
   - Carbon intensity.
   - Scope 3 transport emissions.
   - Scope contribution/share.
   - Production vs. emissions relationship.
   - Cumulative emissions.
   - Indexed growth.

3. **Sensitivity analysis**
   - Scope 3 truck-loading assumptions.
   - Scope 3 delivery-distance assumptions.
   - Scope 2 grid-emission-factor assumptions.

4. **Future projections and decarbonization pathways**
   - Cement demand projections to 2050.
   - Baseline and decarbonization pathways.
   - Future scenario comparison.
   - Integrated pathway analysis.
   - Optimistic vs. realistic mitigation comparison.
   - Mitigation lever contribution analysis.

5. **Tables for paper/report writing**
   - Assumption tables.
   - Scenario tables.
   - Key-year summary tables.
   - Robustness table.

6. **Advanced analysis**
   - Monte Carlo uncertainty analysis.
   - Sensitivity/tornado diagram outputs.
   - LMDI decomposition of emissions drivers.

## Repository structure

```text
cement_emissions_analysis_git/
├── notebooks/
│   └── Python_Code_paper_1_11_Feb_26.ipynb
├── src/
│   ├── 01_generate_historical_scope_emissions.py
│   ├── 02_plot_total_emissions.py
│   ├── ...
│   ├── 26_monte_carlo_uncertainty.py
│   └── 27_lmdi_decomposition.py
├── data/
├── outputs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Required input file

The main input file is:

```text
Paper_Data.xlsx
```

This file is now included in the project root. Keep it there, or edit the `INPUT_PATH` variable inside the relevant script if you move it.

## Verification status

The included `Paper_Data.xlsx` file was tested with `src/01_generate_historical_scope_emissions.py`. The script successfully generated `outputs_historical_scopes.csv` for 1991–2022.

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate     # Windows PowerShell
pip install -r requirements.txt
```

## Suggested running order

Run from the project root:

```bash
python src/01_generate_historical_scope_emissions.py
python src/02_plot_total_emissions.py
python src/03_plot_emissions_by_scope_stacked.py
python src/04_plot_carbon_intensity.py
python src/05_plot_scope3_transport.py
python src/06_plot_emission_share_by_scope.py
python src/07_plot_scope_comparison.py
python src/08_plot_production_vs_co2_scatter.py
python src/09_plot_cumulative_emissions.py
python src/10_plot_indexed_growth.py
python src/12_scope3_loading_sensitivity.py
python src/13_scope3_distance_sensitivity.py
python src/14_scope2_grid_ef_sensitivity.py
python src/15_demand_projection_to_2050.py
python src/16_decarbonization_pathways.py
python src/17_future_scenarios.py
python src/18_medium_demand_projection_plot.py
python src/19_integrated_pathway_stacked.py
python src/20_optimistic_vs_realistic_pathway.py
python src/21_mitigation_analysis.py
python src/22_table_assumptions.py
python src/23_table_scenarios.py
python src/24_table_summary_key_years.py
python src/25_table_robustness.py
python src/26_monte_carlo_uncertainty.py
python src/27_lmdi_decomposition.py
```

`00_exploratory_file_inspection.py` is an early exploratory version and is not required for the main workflow.

## Important notes

- The original notebook is preserved unchanged in the `notebooks/` folder.
- The scripts are extracted cell-by-cell from the notebook, so some repeated imports and repeated data-loading steps remain.
- The workflow expects `outputs_historical_scopes.csv` to be generated before plotting, sensitivity, projection, Monte Carlo, and LMDI scripts are run.
- `Paper_Data.xlsx` is excluded from Git by default to avoid accidentally uploading private/raw data.

## GitHub upload commands

After creating a new empty repository on GitHub, run:

```bash
git init
git add .
git commit -m "Initial cement emissions analysis workflow"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```
