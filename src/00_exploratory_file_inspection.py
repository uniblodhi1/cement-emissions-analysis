"""
Script extracted from notebook cell 0.
Original notebook: Python_Code(paper_1)11_Feb_26.ipynb
Run from project root. Required input: Paper_Data.xlsx (or adjust INPUT_PATH in the script).
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
INPUT_PATH = "/content/Paper_Data.xlsx"
OUTPUT_CSV = "outputs_historical_scopes.csv"

# Flag: assume calcination EF is per ton clinker (True) or per ton cement (False)
CALC_EF_IS_PER_CLINKER = True

# Weighted split for Scope 3 trucking: 60% overloaded, 40% allowed
OVERLOAD_FRAC = 0.60
ALLOWED_FRAC = 0.40

# ============================================================================
# STEP 1: INSPECT FILE STRUCTURE
# ============================================================================
print("=" * 80)
print("STEP 1: FILE INSPECTION")
print("=" * 80)

# Read Excel to inspect sheets and headers
excel_file = pd.ExcelFile(INPUT_PATH)
sheet_names = excel_file.sheet_names
print(f"\nAvailable sheets: {sheet_names}")

# Use first sheet if not sure
sheet_name = sheet_names[0]
print(f"Using sheet: '{sheet_name}'")

# Read first few rows to detect header structure
df_raw = pd.read_excel(INPUT_PATH, sheet_name=sheet_name, nrows=5)
print(f"\nFirst 5 rows (raw):\n{df_raw}\n")
print(f"Column names: {df_raw.columns.tolist()}\n")

# ============================================================================
# STEP 2: HANDLE HEADERS & READ FULL DATA
# ============================================================================
print("=" * 80)
print("STEP 2: READ FULL DATA & HANDLE HEADERS")
print("=" * 80)

# Try to detect if there are two header rows by reading with multiindex
try:
    df_check = pd.read_excel(INPUT_PATH, sheet_name=sheet_name, header=[0, 1], nrows=2)
    # If second row looks like units, keep it; otherwise use single header
    print("Attempting to read with 2-row header...")
    print(f"Multi-index columns:\n{df_check.columns.tolist()}\n")
    has_dual_header = True
except Exception as e:
    print(f"Could not parse as dual header: {e}")
    has_dual_header = False

# Read with appropriate header strategy
if has_dual_header:
    # Flatten multi-index columns by combining name + unit
    df = pd.read_excel(INPUT_PATH, sheet_name=sheet_name, header=[0, 1])
    df.columns = [f"{col[0]}_{col[1]}".strip() if col[1] and col[1] != '' else col[0]
                  for col in df.columns]
else:
    df = pd.read_excel(INPUT_PATH, sheet_name=sheet_name, header=0)

print(f"Data shape: {df.shape}")
print(f"\nAll columns in file:\n{df.columns.tolist()}\n")
print(f"First 3 data rows:\n{df.head(3)}\n")
print(f"Data types:\n{df.dtypes}\n")

# ============================================================================
# STEP 3: COLUMN MAPPING
# ============================================================================
print("=" * 80)
print("STEP 3: BUILD COLUMN MAPPING")
print("=" * 80)

# Create a mapping from raw column names to standardized names
# USER: Please verify/adjust these mappings based on actual column names above
COLUMN_MAPPING = {
    # Update these to match your actual column names
    # Example: 'FY' -> 'year', 'Cement Production (tons)' -> 'cement_t', etc.
}

print("COLUMN_MAPPING (PLEASE VERIFY):")
print(COLUMN_MAPPING)
print("\nIf the mappings above are empty or incorrect, please provide the actual")
print("column names from the file so I can build the correct mapping.\n")

# For now, let's print available columns for user reference
print("=" * 80)
print("AVAILABLE COLUMNS (for mapping):")
print("=" * 80)
for i, col in enumerate(df.columns):
    print(f"{i:2d}. '{col}'")

print("\n" + "=" * 80)
print("NEXT STEP: Please provide column mapping!")
print("=" * 80)
print("""
Please tell me which columns correspond to:
  - year / fiscal year
  - cement_t (total cement production)
  - local_t (local dispatches)
  - exp_n_t (exports north)
  - exp_s_t (exports south)
  - coal_int_kgpt (kg coal per ton cement)
  - elec_int_kwhpt (kWh per ton cement)
  - clinker_ratio
  - ncv (net calorific value)
  - co2_ef_tco2_per_tj (combustion EF)
  - oxid_frac (oxidation fraction)
  - calc_ef (calcination EF)
  - grid_ef_kg_per_kwh
  - cap_allowed_t, cap_over_t (truck capacities)
  - ef_allowed_gpkm, ef_over_gpkm (truck emissions factors)
  - dist_local_km, dist_exp_n_km, dist_exp_s_km (distances)
""")