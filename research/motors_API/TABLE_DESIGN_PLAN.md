# DataFrame Structure Plan for Motors API Pipeline Data

## Current Data Structure
```python
{
    'Service_Name': [
        {
            # Labor/Work Item Fields
            'application_id': '244560030',
            'vehicle_id': '85215',
            'job_description': '...',
            'base_labor_time': '0.4',
            'all_labor_time': '0.4',
            ... (18+ labor fields),
            
            # Parts Data
            'parts': {
                'part_app_id_1': {
                    'part_number': 'KG9Z 3504-H',
                    'price': '2718.18',
                    'manufacturer_name': 'Ford',
                    ... (10+ part fields)
                },
                'part_app_id_2': {...}
            }
        }
    ]
}
```

## Proposed Table Structure: FLAT/DENORMALIZED

### Rationale
Since each work item typically has multiple parts, the best approach for analysis is a **flat table with one row per part**. This:
- Eliminates need for joins
- Keeps all context (work item data) on each row
- Makes filtering and aggregation easier
- Works naturally with pandas operations

### Columns (57 total)

#### Vehicle Context
- `vehicle_id` - The base vehicle ID
- `service_name` - The service/job name (e.g., "Rack & Pinion Assembly R&R")

#### Work Item / Labor Fields (20 fields)
- `application_id` - Work time application ID
- `job_description` - Full job description
- `base_labor_time` - Base labor hours
- `all_labor_time` - Total labor hours
- `base_labor_time_description` - Description (e.g., "One Side")
- `all_labor_time_description` - Description
- `base_warranty_labor_time` - Warranty hours (base)
- `all_warranty_labor_time` - Warranty hours (total)
- `additional_labor_time` - Additional labor
- `additional_labor_time_description` - Description
- `additional_warranty_labor_time` - Additional warranty hours
- `estimated_work_time_id` - Estimated work time ID
- `labor_time_interval` - Unit (e.g., "Hours")
- `required_skill` - Required skill description
- `service_type` - Type (e.g., "Service")
- `base_labor_time_average` - Average base labor time
- `is_active` - Active status (true/false)
- `type` - Type (e.g., "Main Operation")

#### Part Fields (15+ fields, dynamic based on API)
- `part_app_id` - Part application ID (becomes row key combined with work item)
- `part_number` - Part number
- `price` - Part price
- `manufacturer_name` - Manufacturer
- `updated_date` - Last updated date
- `estimated_time_to_delivery` - Delivery estimate
- `(other part fields as provided by API)` - Additional part attributes

## Alternative Options

### Option 1: Normalized (2 DataFrames)
**Pros:** No data duplication, follows database normalization
**Cons:** Requires joins for analysis, more complex

### Option 2: Nested Structure (per service)
**Pros:** Preserves original hierarchy
**Cons:** Harder to query and analyze

## Recommendation: FLAT DENORMALIZED (Option 1 Above)
- Best for analysis and filtering
- Easy to aggregate by service, part number, price range, etc.
- Natural pandas operations (groupby, filter, sort)
- Can always re-denormalize back to original structure if needed

## Example Row
```
vehicle_id | service_name                  | application_id | job_description        | base_labor_time | ... | part_app_id | part_number   | price    | manufacturer_name
85215      | Rack & Pinion Assembly R&R    | 244560030      | Includes: The removal. | 0.4             | ... | 338614419   | KG9Z 3504-H   | 2718.18  | Ford
85215      | Rack & Pinion Assembly R&R    | 244560030      | Includes: The removal. | 0.4             | ... | 338614420   | ABC123        | 500.00   | Supplier2
85215      | Steering Knuckle R&R          | 244560031      | Removal and R&R        | 1.5             | ... | 338614421   | XYZ789        | 350.00   | Ford
```

## Implementation Plan
1. Create function `pipeline_to_dataframe(pipeline_results)` 
2. Iterate through services → work items → parts
3. For each part, create a row with:
   - All work item fields
   - Part fields
   - Service name as context
4. Return pandas DataFrame

## Questions to Confirm
1. Is flat denormalized structure preferred? ✓
2. Should we include a row number/index? ✓
3. Any fields you want to exclude or transform? ✓
4. Want to preserve original data types or convert (e.g., strings to numbers for prices)? ✓
