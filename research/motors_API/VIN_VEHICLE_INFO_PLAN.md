# Plan: Add VIN & Vehicle Info to Pipeline and Support Multiple VINs

## Goal
1. Include VIN, model_name, make_name, engine_description in Excel output
2. Support processing a list of VINs (not just one)
3. Combine results from all VINs in single Excel file

## Current Flow
```
step_1(vin) → vehicle_data (HAS VIN info)
      ↓
step_2(vehicle_data) → summaries (LOSES VIN info)
      ↓
step_3(summaries) → work_items (LOSES VIN info)
      ↓
step_4(work_items) → enriched_data (LOSES VIN info)
      ↓
flatten_pipeline_to_rows() → rows (MISSING VIN info)
      ↓
Excel file (MISSING VIN, model_name, make_name, engine_description)
```

## Required Changes

### 1. Modify step_2 to Pass Vehicle Info
**Current:** Returns only `{application_ids: [...], vehicle_id: '...'}`
**New:** Also include vehicle information

```python
def step2(data):
    # ... existing code ...
    data_out = extract_keywords_from_xml(resp)
    data_out["vehicle_id"] = vehicle_id
    
    # NEW: Pass vehicle info through
    data_out["vin"] = data["vehicles"][0].get("vehicle_id")  # The actual VIN
    data_out["make_name"] = data["vehicles"][0].get("make_name")
    data_out["model_name"] = data["vehicles"][0].get("model_name")
    data_out["engine_description"] = data["vehicles"][0].get("engine_description")
    
    return data_out
```

### 2. Modify step_3 to Preserve Vehicle Info
**Current:** Returns list of dicts with work_items
**New:** Include vehicle info in each work item

Add to each work_item in step_3:
```python
# Inside the work_item dict creation:
work_item = {
    'application_id': app_id,
    'vehicle_id': vehicle_id,
    
    # NEW: Add vehicle info to every work item
    'vin': data.get("vin"),
    'make_name': data.get("make_name"),
    'model_name': data.get("model_name"),
    'engine_description': data.get("engine_description"),
    
    # ... rest of fields ...
}
```

### 3. Modify step_4 to Preserve Vehicle Info
**Current:** Preserves work_item fields with `**work_item`
**No change needed!** Already uses `**work_item` which will preserve VIN fields

### 4. Modify flatten_pipeline_to_rows() in pipeline_to_excel.py
**Current:** Only extracts service_name + part fields
**New:** Also extract and include VIN + vehicle info

```python
def flatten_pipeline_to_rows(pipeline_results: dict) -> list:
    rows = []
    
    for service_name, work_items in pipeline_results.items():
        for work_item in work_items:
            parts_dict = work_item.get('parts', {})
            
            for part_app_id, part_data in parts_dict.items():
                row = {
                    # NEW: Add VIN and vehicle info first
                    'vin': work_item.get('vin'),
                    'make_name': work_item.get('make_name'),
                    'model_name': work_item.get('model_name'),
                    'engine_description': work_item.get('engine_description'),
                    
                    # Existing fields
                    'service_name': service_name,
                    'part_app_id': part_app_id,
                    **work_item,
                    **part_data
                }
                
                row.pop('parts', None)
                rows.append(row)
    
    return rows
```

### 5. Modify run_pipeline() to Handle List of VINs
**Current:** Takes single VIN string
**New:** Takes either single VIN string OR list of VIN strings

```python
def run_pipeline(vins):
    """
    Process one or more VINs.
    
    Args:
        vins: Single VIN string OR list of VIN strings
              Examples:
                run_pipeline("3FA6P0D9XLR115438")
                run_pipeline(["3FA6P0D9XLR115438", "1FMCU9G97EUB92197"])
    
    Returns:
        Dict with all services/work items/parts from all VINs
    """
    # Handle both single VIN and list of VINs
    if isinstance(vins, str):
        vins = [vins]
    
    print(f"Starting pipeline for {len(vins)} VIN(s)\n")
    
    all_results = {}  # Combine results from all VINs
    
    for vin in vins:
        print(f"\nProcessing VIN: {vin}")
        print("-" * 80)
        
        # STEP 1: Vehicle lookup
        print("STEP 1: Vehicle lookup...")
        vehicle_data = step_1(vin)
        vin_info = vehicle_data['vehicles'][0]
        print(f"OK: {vin_info['make_name']} {vin_info['model_name']} {vin_info['year']}")
        
        # STEP 2: Get work-time summaries
        print("STEP 2: Get work-time summaries...")
        summaries = step2(vehicle_data)
        num_apps = len(summaries['application_ids'])
        print(f"OK: Found {num_apps} work-time applications")
        
        # STEP 3: Extract work items
        print("STEP 3: Extract work items...")
        labor_items = step3(summaries)
        print(f"OK: Processed {len(labor_items)} services")
        
        # STEP 4: Enrich with parts
        print("STEP 4: Enrich with parts data...")
        complete_data = step_4(labor_items)
        
        # Count parts
        total_parts = sum(len(work_item.get('parts', {})) 
                         for work_items in complete_data.values() 
                         for work_item in work_items)
        print(f"OK: Found {total_parts} total parts")
        
        # Merge results (handle duplicate service names)
        for service_name, work_items in complete_data.items():
            if service_name in all_results:
                all_results[service_name].extend(work_items)
            else:
                all_results[service_name] = work_items
    
    print("\n" + "=" * 80)
    print(f"Pipeline complete!")
    print(f"VINs processed: {len(vins)}")
    print(f"Services: {len(all_results)}")
    
    return all_results
```

## Updated Usage Pattern

### Single VIN (backwards compatible)
```python
results = run_pipeline("3FA6P0D9XLR115438")
file_path = pipeline_to_excel(results)
```

### Multiple VINs (new!)
```python
vins = [
    "3FA6P0D9XLR115438",  # Ford Fusion 2020
    "1FMCU9G97EUB92197"   # Ford Escape 2014
]
results = run_pipeline(vins)
file_path = pipeline_to_excel(results)
```

## Excel Output Changes
**Before:**
- service_name, part_app_id, application_id, vehicle_id, job_description, ...

**After:**
- **vin** ← NEW
- **make_name** ← NEW
- **model_name** ← NEW
- **engine_description** ← NEW
- service_name, part_app_id, application_id, vehicle_id, job_description, ...

## Files to Modify

| File | Function | Change |
|------|----------|--------|
| MotorsAPI.ipynb | step2 | Add VIN & vehicle info |
| MotorsAPI.ipynb | step3 | Add VIN & vehicle info to each work_item |
| MotorsAPI.ipynb | run_pipeline | Handle single VIN OR list of VINs |
| pipeline_to_excel.py | flatten_pipeline_to_rows | Extract VIN & vehicle info |

## Testing Plan

1. **Single VIN test:**
   ```python
   results = run_pipeline("3FA6P0D9XLR115438")
   pipeline_to_excel(results)
   # Check that rows contain vin, make_name, model_name, engine_description
   ```

2. **Multiple VIN test:**
   ```python
   vins = ["3FA6P0D9XLR115438", "1FMCU9G97EUB92197"]
   results = run_pipeline(vins)
   pipeline_to_excel(results)
   # Check that all VINs are in the output
   # Check deduplication works across VINs
   ```

3. **Verify Excel columns:**
   - Check first 4 columns are: vin, make_name, model_name, engine_description
   - Check they're populated for all rows
   - Check dedup columns include vin (vehicle_id + application_id + part_app_id + vin)

## Data Flow After Changes

```
step_1(vin) 
  ↓ (vehicle_data WITH vin/make/model/engine)
step_2(vehicle_data) 
  ↓ (summaries WITH vin/make/model/engine)
step_3(summaries)
  ↓ (work_items WITH vin/make/model/engine)
step_4(work_items)
  ↓ (enriched_data WITH vin/make/model/engine in every work_item)
flatten_pipeline_to_rows()
  ↓ (rows WITH vin/make/model/engine in every row)
Excel file ✓ (HAS vin, make_name, model_name, engine_description)
```

## Summary

- ✓ VIN info flows through entire pipeline
- ✓ Excel contains vin, make_name, model_name, engine_description
- ✓ Support single VIN (backwards compatible)
- ✓ Support multiple VINs (new feature)
- ✓ Deduplication works across multiple VINs
- ✓ Results combined into single Excel file with all data

Ready to implement?
