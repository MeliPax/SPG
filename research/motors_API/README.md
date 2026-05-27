# Motors API Pipeline Implementation

## Overview

Complete end-to-end pipeline for extracting vehicle service and parts data from the Motors API using a VIN (Vehicle Identification Number) as input.

## Architecture

The pipeline consists of 5 sequential steps:

### Step 1: Vehicle Lookup (`step_1`)
- **Input**: VIN string
- **Output**: Vehicle data including make, model, year, base_vehicle_id
- **API Call**: `/v1/Information/Vehicles/Search/ByVIN?vin={vin}`

### Step 2: Work-Time Summaries (`step2`)
- **Input**: Vehicle data from Step 1
- **Output**: List of application IDs with service names
- **API Call**: `/v1/Information/Vehicles/Attributes/BaseVehicleId/{vehicle_id}/Content/Summaries/Of/EstimatedWorkTimes/`

### Step 3: Work Item Extraction (`step3`)
- **Input**: Application IDs from Step 2
- **Output**: Nested structure with service names mapping to lists of work items
- **Features**: 
  - Extracts ALL work items (not just first)
  - Preserves all 20+ labor detail fields per work item
  - Handles multiple EstimatedWorkTime elements per application
- **API Calls**: `/v1/Information/Vehicles/Attributes/BaseVehicleId/{vehicle_id}/Content/Details/Of/EstimatedWorkTimes/{application_id}`

### Step 4: Parts Enrichment (`step_4`)
- **Input**: Work items structure from Step 3
- **Output**: Same structure with 'parts' list added to each work item
- **Features**:
  - Gets parts summary for each work item
  - Extracts ALL part application IDs
  - Fetches complete details for each part
  - Preserves all labor fields while adding parts
- **API Calls**: 
  - `/v1/Information/Vehicles/Attributes/BaseVehicleId/{vehicle_id}/Content/Summaries/Of/Parts/RelatedTo/EstimatedWorkTimes/{application_id}`
  - `/v1/Information/Vehicles/Attributes/BaseVehicleId/{vehicle_id}/Content/Details/Of/Parts/{part_app_id}`

### Complete Pipeline (`run_pipeline`)
- **Input**: VIN string
- **Output**: Complete nested structure with all data
- **Usage**: Simple single function call that orchestrates steps 1-4

## Output Structure

```python
[
    {
        'Rack & Pinion Assembly R&R': [
            {
                # Labor fields (20+ fields)
                'application_id': '244560030',
                'vehicle_id': '85215',
                'job_description': '...',
                'base_labor_time': '0.4',
                'all_labor_time': '0.4',
                'base_labor_time_description': 'One Side',
                'all_labor_time_description': 'One Side',
                'estimated_work_time_id': '10613',
                'labor_time_interval': 'Hours',
                'required_skill': '...',
                'service_type': 'Service',
                'base_labor_time_average': '0.4',
                'is_active': 'true',
                'type': 'Main Operation',
                # ... additional labor fields
                
                # Parts list
                'parts': [
                    {
                        'part_app_id': '338614419',
                        'part_number': 'KG9Z 3504-H',
                        'price': '2718.18',
                        'manufacturer_name': 'Ford',
                        'updated_date': '2024-01-15',
                        'estimated_time_to_delivery': '2 weeks',
                        # ... additional part fields (12+ fields total)
                    },
                    { second_part },
                    ...
                ]
            },
            { second_work_item },
            ...
        ]
    },
    {
        'Steering Knuckle R&R': [ ... ],
        'Tie Rod R&R': [ ... ],
        ...
    }
]
```

## Usage

### Basic Usage

```python
# Run the complete pipeline with a VIN
results = run_pipeline("3FA6P0D9XLR115438")

# Access results by service name and work item
for service_dict in results:
    for service_name, work_items in service_dict.items():
        print(f"Service: {service_name}")
        for work_item in work_items:
            print(f"  Work Item: {work_item['job_description']}")
            print(f"  Parts: {len(work_item['parts'])}")
            for part in work_item['parts']:
                print(f"    - {part['part_number']}: ${part['price']}")
```

### Step-by-Step Usage

```python
# For more granular control, use individual steps
vehicle_data = step_1(vin)
work_time_summaries = step2(vehicle_data)
work_items = step3(work_time_summaries)
complete_data = step_4(work_items)
```

## Helper Functions

### XML Parsing Functions
- `extract_keywords_from_xml()`: Extract application IDs and display names
- `extract_all_part_application_ids()`: Extract all part ApplicationIDs (not just first)
- `extract_estimated_work_time()`: Extract labor details
- `extract_part_details()`: Extract part details

### Utility Functions
- `strip_ns()`: Remove XML namespace prefixes from tags
- `get_text()`: Extract text from XML child elements

## Key Features

1. **Complete Data Extraction**: Gets ALL work items and ALL parts (not just first of each)
2. **Nested Organization**: Results organized by service name for easy navigation
3. **Comprehensive Fields**: Preserves all 20+ labor fields and 12+ part fields
4. **Error Handling**: Graceful handling of API responses and missing data
5. **XML Namespace Handling**: Properly strips XML namespaces for reliable parsing
6. **Authentication**: HMAC-SHA256 authentication with Motors API

## Data Fields

### Labor Fields (per work item)
- application_id
- vehicle_id
- job_description
- base_labor_time
- all_labor_time
- base_labor_time_description
- all_labor_time_description
- base_warranty_labor_time
- all_warranty_labor_time
- additional_labor_time
- additional_labor_time_description
- additional_warranty_labor_time
- estimated_work_time_id
- labor_time_interval
- required_skill
- service_type
- base_labor_time_average
- is_active
- type

### Part Fields (per part)
- part_app_id
- part_number
- price
- manufacturer_name
- updated_date
- estimated_time_to_delivery
- (and additional fields based on API response)

## Testing

The notebook includes test cells that verify:
1. API connectivity
2. Step-by-step execution with known VIN
3. Complete pipeline execution
4. Result validation

To test:
1. Ensure `.env` file has `C_PUBLIC_KEY` and `C_PRIVATE_KEY`
2. Run all setup cells (imports, authentication, helpers)
3. Run the pipeline test cell

## Notes

- The pipeline handles multiple work items per application
- The pipeline handles multiple parts per work item
- Results are organized hierarchically for easy navigation
- All API calls include proper HMAC-SHA256 authentication
- XML responses are parsed to extract structured data
