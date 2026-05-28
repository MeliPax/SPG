# Implementation Plan: Pipeline to DataFrame with Excel Export

## Overview
Create a modular system to convert Motors API pipeline results to a DataFrame and save to Excel with deduplication logic.

## Architecture: Modular Helper Functions

```
Main Function: pipeline_to_excel(pipeline_results)
│
├── Helper 1: setup_output_directory()
│   └── Creates/validates output folder using pathlib
│
├── Helper 2: flatten_pipeline_to_rows(pipeline_results)
│   └── Converts nested dict structure to list of flat rows
│   └── Yields one row per part with work item context
│
├── Helper 3: rows_to_dataframe(rows)
│   └── Converts list of row dicts to pandas DataFrame
│   └── Handles data type conversions (price: str→float, etc)
│
├── Helper 4: load_existing_data(file_path)
│   └── Loads existing Excel file if it exists
│   └── Returns empty DataFrame if file doesn't exist
│
├── Helper 5: deduplicate_rows(new_df, existing_df)
│   └── Checks for duplicate rows by comparing key columns
│   └── Returns only new/updated rows
│   └── Deduplication keys: vehicle_id + application_id + part_app_id
│
├── Helper 6: append_to_excel(file_path, new_df, existing_df)
│   └── Appends new rows to existing file
│   └── Overwrites entire file with combined data
│   └── Maintains Excel formatting
│
└── Main Logic: Orchestrate all helpers
    └── Setup → Flatten → Convert → Load → Deduplicate → Append
```

## Detailed Function Specifications

### 1. `setup_output_directory()`
```python
def setup_output_directory() -> Path:
    """
    Create output folder if it doesn't exist.
    Uses pathlib for cross-platform compatibility.
    
    Returns:
        Path: Path to output directory
    """
    # Get current working directory using pathlib
    output_dir = Path.cwd() / "output"
    
    # Create directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    return output_dir
```

**Pathlib Pattern Used:** `Path.cwd() / "folder_name"` and `mkdir(exist_ok=True)`

---

### 2. `flatten_pipeline_to_rows(pipeline_results: dict) -> List[dict]`
```python
def flatten_pipeline_to_rows(pipeline_results: dict) -> List[dict]:
    """
    Convert nested pipeline structure to flat rows.
    One row per part, with work item context preserved.
    
    Input:
    {
        'Service_Name': [
            {
                'application_id': '...',
                'parts': {'part_id_1': {...}, 'part_id_2': {...}}
            }
        ]
    }
    
    Output:
    [
        {'service_name': '...', 'application_id': '...', 'part_app_id': '...', ...},
        {'service_name': '...', 'application_id': '...', 'part_app_id': '...', ...}
    ]
    
    Algorithm:
    - For each service_name in results:
      - For each work_item in work_items:
        - For each part_app_id in parts dict:
          - Create row combining:
            * service_name (add to row)
            * all work_item fields
            * part_app_id + all part fields
          - Yield row
    """
```

---

### 3. `rows_to_dataframe(rows: List[dict]) -> pd.DataFrame`
```python
def rows_to_dataframe(rows: List[dict]) -> pd.DataFrame:
    """
    Convert list of flat row dicts to DataFrame.
    Handles data type conversions.
    
    Type Conversions:
    - price: str → float
    - base_labor_time: str → float
    - all_labor_time: str → float
    - is_active: str → bool
    
    Returns:
        pd.DataFrame: Flattened data with proper types
    """
```

---

### 4. `load_existing_data(file_path: Path) -> pd.DataFrame`
```python
def load_existing_data(file_path: Path) -> pd.DataFrame:
    """
    Load existing Excel file if it exists.
    
    Returns:
        pd.DataFrame: Existing data if file exists, empty DataFrame otherwise
    
    Logic:
    - Check if file_path.exists()
    - If exists: read Excel file
    - If not exists: return empty DataFrame with proper column structure
    """
```

---

### 5. `deduplicate_rows(new_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame`
```python
def deduplicate_rows(new_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows from new_df that already exist in existing_df.
    
    Deduplication Strategy:
    - Key columns: ['vehicle_id', 'application_id', 'part_app_id']
    - If all three columns match an existing row → skip
    - Otherwise → include in results
    
    Returns:
        pd.DataFrame: Only new/updated rows from new_df
    
    Logic:
    - Create a concat key: vehicle_id + application_id + part_app_id
    - Compare concat keys between new_df and existing_df
    - Use ~isin() to filter out duplicates
    """
```

---

### 6. `append_to_excel(file_path: Path, new_df: pd.DataFrame, existing_df: pd.DataFrame) -> None`
```python
def append_to_excel(file_path: Path, new_df: pd.DataFrame, existing_df: pd.DataFrame) -> None:
    """
    Append new rows to Excel file.
    
    Logic:
    1. Concatenate existing_df + new_df (new at bottom)
    2. Drop duplicates if needed (safety check)
    3. Write to file_path using pandas ExcelWriter
    4. Print summary of changes
    
    Returns:
        None
    """
```

---

### 7. `pipeline_to_excel(pipeline_results: dict, file_name: str = "motor_data") -> None`
```python
def pipeline_to_excel(pipeline_results: dict, file_name: str = "motor_data") -> None:
    """
    Main orchestration function.
    
    Steps:
    1. Setup output directory
    2. Flatten pipeline to rows
    3. Convert rows to DataFrame
    4. Load existing data (if file exists)
    5. Deduplicate new rows
    6. Append to Excel
    
    Args:
        pipeline_results: Output from run_pipeline()
        file_name: Name of Excel file (without extension)
    
    Returns:
        None
    
    Example:
        results = run_pipeline(vin)
        pipeline_to_excel(results)  # Saves to output/motor_data.xlsx
    """
```

---

## File Structure
```
motors_API/
├── MotorsAPI.ipynb
├── output/
│   └── motor_data.xlsx  ← Generated/updated here
├── IMPLEMENTATION_PLAN.md  ← This file
└── pipeline_to_excel.py    ← New file with all functions
```

## Data Flow Diagram
```
Pipeline Results (dict)
    ↓
flatten_pipeline_to_rows() → List[dict]
    ↓
rows_to_dataframe() → DataFrame (new data)
    ↓
load_existing_data() → DataFrame (existing data, or empty)
    ↓
deduplicate_rows() → DataFrame (only new/updated rows)
    ↓
append_to_excel() → Excel file
    ↓
motor_data.xlsx (in output/ folder)
```

## Key Design Decisions

| Decision | Reasoning |
|----------|-----------|
| **Pathlib** | Cross-platform, cleaner syntax, object-oriented |
| **Generator for flattening** | Memory efficient for large datasets |
| **Check file existence** | Don't error on first run |
| **Deduplicate by key** | Prevent duplicate rows on multiple runs |
| **Append mode** | Keep all historical data |
| **Modular helpers** | Easy to test and maintain |

## Deduplication Example

**Run 1:**
- New data: 3 work items × 5 parts each = 15 rows
- Excel saves: 15 rows

**Run 2 (same VIN):**
- New data: 3 work items × 5 parts each = 15 rows
- Existing: 15 rows
- After deduplicate: 0 new rows
- Excel stays: 15 rows (no duplicates added)

**Run 3 (different VIN):**
- New data: 2 work items × 4 parts each = 8 rows
- Existing: 15 rows
- After deduplicate: 8 rows (all new)
- Excel now: 23 rows

## Implementation Checklist
- [ ] Create `setup_output_directory()` with pathlib
- [ ] Create `flatten_pipeline_to_rows()` with nested loops
- [ ] Create `rows_to_dataframe()` with type conversion
- [ ] Create `load_existing_data()` with file checking
- [ ] Create `deduplicate_rows()` with key comparison
- [ ] Create `append_to_excel()` with pandas ExcelWriter
- [ ] Create main `pipeline_to_excel()` orchestration function
- [ ] Test with sample pipeline data
- [ ] Add to notebook or separate Python module

---

## Questions for Review
1. ✓ Use pathlib with `Path.cwd() / "output"`?
2. ✓ One row per part (flat table)?
3. ✓ Dedup by vehicle_id + application_id + part_app_id?
4. ✓ Append new rows (keep history)?
5. ✓ Excel format (.xlsx)?
6. ✓ File name: `motor_data.xlsx`?

**Ready to implement?** Yes/No
