"""
Motors API Pipeline to Excel Export Module

Converts nested pipeline results to flat DataFrame and saves to Excel with deduplication.
Provides modular helper functions for data transformation and file handling.
"""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import numpy as np


# ============================================================================
# HELPER 1: Setup Output Directory
# ============================================================================

def setup_output_directory(base_dir: Path = None) -> Path:
    """
    Create output folder if it doesn't exist using pathlib.

    Args:
        base_dir: Base directory (default: current working directory)

    Returns:
        Path: Path to output directory

    Example:
        output_dir = setup_output_directory()
        # Creates ./output/ if it doesn't exist
    """
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)

    output_dir = base_dir / "output"

    # Create directory with exist_ok=True to avoid error if already exists
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"Output directory ready: {output_dir}")
    return output_dir


# ============================================================================
# HELPER 2: Flatten Pipeline to Rows
# ============================================================================

def flatten_pipeline_to_rows(pipeline_results: Dict) -> List[Dict]:
    """
    Convert nested pipeline structure to flat list of row dictionaries.
    One row per part with all work item context preserved.

    Input structure:
    {
        'Service_Name': [
            {
                'application_id': '...',
                'vehicle_id': '...',
                'base_labor_time': '...',
                'parts': {
                    'part_app_id_1': {'part_number': '...', 'price': '...'},
                    'part_app_id_2': {...}
                }
            }
        ]
    }

    Output: List of dicts with one row per part

    Args:
        pipeline_results: Output from run_pipeline()

    Returns:
        List[Dict]: Flattened rows, one per part
    """
    rows = []

    # Iterate through each service
    for service_name, work_items in pipeline_results.items():
        # Iterate through each work item in this service
        for work_item in work_items:
            # Get the parts dict for this work item
            parts_dict = work_item.get('parts', {})

            # Iterate through each part in this work item
            for part_app_id, part_data in parts_dict.items():
                # Create a row combining work item + part data
                row = {
                    'service_name': service_name,
                    'part_app_id': part_app_id,
                    **work_item,  # Add all work item fields
                    **part_data   # Add all part fields (overrides if same key)
                }

                # Remove 'parts' dict from row (we extracted it already)
                row.pop('parts', None)

                rows.append(row)

    print(f"Flattened {len(rows)} rows from pipeline results")
    return rows


# ============================================================================
# HELPER 3: Convert Rows to DataFrame
# ============================================================================

def rows_to_dataframe(rows: List[Dict]) -> pd.DataFrame:
    """
    Convert list of flat row dictionaries to DataFrame.
    Handles data type conversions for numeric and boolean fields.

    Type Conversions:
    - price: str → float
    - base_labor_time: str → float
    - all_labor_time: str → float
    - base_labor_time_average: str → float
    - is_active: str → bool

    Args:
        rows: List of flat row dictionaries

    Returns:
        pd.DataFrame: Flattened data with proper types
    """
    if not rows:
        print("No rows to convert to DataFrame")
        return pd.DataFrame()

    # Create DataFrame from rows
    df = pd.DataFrame(rows)

    # Fields to convert to float
    float_fields = [
        'price', 'base_labor_time', 'all_labor_time',
        'base_labor_time_average', 'base_warranty_labor_time',
        'all_warranty_labor_time', 'additional_labor_time',
        'additional_warranty_labor_time'
    ]

    # Convert numeric fields
    for field in float_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce')

    # Convert boolean fields
    if 'is_active' in df.columns:
        df['is_active'] = df['is_active'].map({'true': True, 'false': False})

    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df


# ============================================================================
# HELPER 4: Load Existing Data
# ============================================================================

def load_existing_data(file_path: Path) -> pd.DataFrame:
    """
    Load existing Excel file if it exists.
    Returns empty DataFrame if file doesn't exist.

    Args:
        file_path: Path to Excel file

    Returns:
        pd.DataFrame: Existing data if file exists, empty DataFrame otherwise
    """
    # Check if file exists
    if file_path.exists():
        try:
            df = pd.read_excel(file_path)
            print(f"Loaded existing data: {len(df)} rows")
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return pd.DataFrame()
    else:
        print(f"No existing file found at {file_path}")
        return pd.DataFrame()


# ============================================================================
# HELPER 5: Deduplicate Rows
# ============================================================================

def deduplicate_rows(new_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows from new_df that already exist in existing_df.

    Deduplication Strategy:
    - Key columns: ['vehicle_id', 'application_id', 'part_app_id']
    - If all three columns match an existing row → skip
    - Otherwise → include in results

    Args:
        new_df: DataFrame with new rows
        existing_df: DataFrame with existing rows

    Returns:
        pd.DataFrame: Only new/updated rows from new_df
    """
    # If no existing data, all new rows are unique
    if existing_df.empty:
        print(f"No existing data, all {len(new_df)} rows are new")
        return new_df

    # Create composite key from dedup columns
    dedup_cols = ['vehicle_id', 'application_id', 'part_app_id']

    # Check that all dedup columns exist
    missing_cols = [col for col in dedup_cols if col not in new_df.columns]
    if missing_cols:
        print(f"Warning: Missing dedup columns {missing_cols}, skipping deduplication")
        return new_df

    # Create composite keys
    new_keys = new_df[dedup_cols].astype(str).agg('_'.join, axis=1)
    existing_keys = existing_df[dedup_cols].astype(str).agg('_'.join, axis=1)

    # Find rows that don't exist in existing data
    new_rows_mask = ~new_keys.isin(existing_keys)
    new_rows = new_df[new_rows_mask]

    duplicates = len(new_df) - len(new_rows)
    print(f"Deduplication: {duplicates} duplicates removed, {len(new_rows)} new rows remain")

    return new_rows


# ============================================================================
# HELPER 6: Append to Excel
# ============================================================================

def append_to_excel(file_path: Path, new_df: pd.DataFrame, existing_df: pd.DataFrame) -> None:
    """
    Append new rows to Excel file.
    Combines existing + new data and writes to file.

    Args:
        file_path: Path to Excel file
        new_df: DataFrame with new rows
        existing_df: DataFrame with existing rows

    Returns:
        None
    """
    # Combine existing + new data
    if existing_df.empty:
        combined_df = new_df.copy()
        print(f"Creating new file with {len(combined_df)} rows")
    else:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        print(f"Combined data: {len(existing_df)} existing + {len(new_df)} new = {len(combined_df)} total rows")

    # Write to Excel
    try:
        combined_df.to_excel(file_path, index=False, sheet_name='Motor Data')
        print(f"Successfully saved to {file_path}")
    except Exception as e:
        print(f"Error writing to Excel: {e}")


# ============================================================================
# MAIN FUNCTION: Pipeline to Excel
# ============================================================================

def pipeline_to_excel(
    pipeline_results: Dict,
    file_name: str = "motor_data",
    output_dir: Path = None
) -> Path:
    """
    Main orchestration function.
    Converts pipeline results to DataFrame and saves to Excel with deduplication.

    Workflow:
    1. Setup output directory
    2. Flatten pipeline to rows
    3. Convert rows to DataFrame
    4. Load existing data (if file exists)
    5. Deduplicate new rows
    6. Append to Excel

    Args:
        pipeline_results: Output from run_pipeline()
        file_name: Name of Excel file without extension (default: "motor_data")
        output_dir: Output directory path (default: ./output)

    Returns:
        Path: Path to saved Excel file

    Example:
        results = run_pipeline("3FA6P0D9XLR115438")
        file_path = pipeline_to_excel(results)
        # Saves to output/motor_data.xlsx
    """
    print("\n" + "="*80)
    print("PIPELINE TO EXCEL CONVERSION")
    print("="*80 + "\n")

    # STEP 1: Setup output directory
    print("STEP 1: Setting up output directory...")
    output_directory = setup_output_directory(output_dir)
    file_path = output_directory / f"{file_name}.xlsx"
    print()

    # STEP 2: Flatten pipeline to rows
    print("STEP 2: Flattening pipeline results...")
    rows = flatten_pipeline_to_rows(pipeline_results)
    if not rows:
        print("ERROR: No rows generated from pipeline results")
        return file_path
    print()

    # STEP 3: Convert rows to DataFrame
    print("STEP 3: Converting to DataFrame...")
    new_df = rows_to_dataframe(rows)
    print()

    # STEP 4: Load existing data
    print("STEP 4: Loading existing data...")
    existing_df = load_existing_data(file_path)
    print()

    # STEP 5: Deduplicate rows
    print("STEP 5: Deduplicating rows...")
    unique_rows = deduplicate_rows(new_df, existing_df)
    print()

    # STEP 6: Append to Excel
    print("STEP 6: Saving to Excel...")
    if unique_rows.empty:
        print("No new rows to save")
    else:
        append_to_excel(file_path, unique_rows, existing_df)
    print()

    print("="*80)
    print(f"COMPLETE: Data saved to {file_path}")
    print("="*80 + "\n")

    return file_path


# ============================================================================
# UTILITY: Display DataFrame Summary
# ============================================================================

def display_summary(file_path: Path) -> None:
    """
    Display summary of saved Excel file.

    Args:
        file_path: Path to Excel file
    """
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    df = pd.read_excel(file_path)

    print("\n" + "="*80)
    print("EXCEL FILE SUMMARY")
    print("="*80)
    print(f"File: {file_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\nFirst 5 Rows:")
    print(df.head().to_string())
    print("="*80 + "\n")


if __name__ == "__main__":
    print("Pipeline to Excel module loaded successfully")
    print("Available functions:")
    print("  - setup_output_directory()")
    print("  - flatten_pipeline_to_rows()")
    print("  - rows_to_dataframe()")
    print("  - load_existing_data()")
    print("  - deduplicate_rows()")
    print("  - append_to_excel()")
    print("  - pipeline_to_excel()")
    print("  - display_summary()")
