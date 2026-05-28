"""
Enhanced comparison functions for labour and parts analysis.
Add this to your MotorsAPI.ipynb to replace the compare_years function.
"""

import pandas as pd


def compare_years(make: str, model: str, year1: int, year2: int, excel_file: str = "./output/motor_data.xlsx"):
    """
    Compare labour and parts data between two years for the same make/model.
    Shows detailed side-by-side comparison with summary and hierarchy view.

    Args:
        make (str): Vehicle make - e.g., 'Ford'
        model (str): Vehicle model - e.g., 'Fusion', 'Escape'
        year1 (int): First year - e.g., 2020
        year2 (int): Second year - e.g., 2014

    Usage:
        compare_years("Ford", "Fusion", 2020, 2014)
        compare_years("Ford", "Escape", 2020, 2014)
    """
    df = pd.read_excel(excel_file)

    # Filter by make and model (better filtering)
    df_make = df[df['make_name'].str.lower() == make.lower()].copy()
    df_make = df_make[df_make['model_name'].str.lower() == model.lower()].copy()

    if df_make.empty:
        print(f"❌ No data found for {make} {model}")
        return

    df_year1 = df_make[df_make['year'] == year1].copy()
    df_year2 = df_make[df_make['year'] == year2].copy()

    if df_year1.empty or df_year2.empty:
        print(f"❌ No data found for {make} {model} in one or both years")
        return

    print(f"\n{'='*160}")
    print(f"COMPARISON: {make.upper()} {model.upper()} | {year1} vs {year2}".center(160))
    print(f"{'='*160}\n")

    # ========== SUMMARY TABLE ==========
    print("📊 SUMMARY STATISTICS\n")

    services_y1 = df_year1['service_name'].nunique()
    labour_y1 = df_year1[(df_year1['record_type'] == 'labour') & (pd.notna(df_year1['job_description']))]['application_id'].nunique()
    parts_y1 = df_year1[(df_year1['record_type'] == 'part') & (pd.notna(df_year1['oepr_part_number'])) & (df_year1['oepr_part_number'] != 'NR')]['oepr_part_number'].nunique()

    services_y2 = df_year2['service_name'].nunique()
    labour_y2 = df_year2[(df_year2['record_type'] == 'labour') & (pd.notna(df_year2['job_description']))]['application_id'].nunique()
    parts_y2 = df_year2[(df_year2['record_type'] == 'part') & (pd.notna(df_year2['oepr_part_number'])) & (df_year2['oepr_part_number'] != 'NR')]['oepr_part_number'].nunique()

    summary_data = {
        'Metric': ['Services', 'Labour Items', 'Unique Parts'],
        year1: [services_y1, labour_y1, parts_y1],
        year2: [services_y2, labour_y2, parts_y2],
        'Δ (Difference)': [services_y2 - services_y1, labour_y2 - labour_y1, parts_y2 - parts_y1]
    }
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))

    # ========== DETAILED SIDE-BY-SIDE COMPARISON ==========
    print(f"\n\n{'='*160}")
    print("📋 DETAILED SERVICE HIERARCHY (SIDE-BY-SIDE)")
    print(f"{'='*160}\n")

    col_width = 70
    divider = "  │  "

    # Header
    header_left = f"{year1} DETAILS".center(col_width)
    header_right = f"{year2} DETAILS".center(col_width)
    print(f"{header_left}{divider}{header_right}")
    print("─" * 160)

    services_y1_list = set(df_year1['service_name'].unique())
    services_y2_list = set(df_year2['service_name'].unique())
    common_services = sorted(services_y1_list & services_y2_list)

    for service_name in common_services:
        service_y1 = df_year1[df_year1['service_name'] == service_name]
        service_y2 = df_year2[df_year2['service_name'] == service_name]

        labour_y1_list = service_y1[(service_y1['record_type'] == 'labour') & (pd.notna(service_y1['job_description']))]['application_id'].unique()
        labour_y2_list = service_y2[(service_y2['record_type'] == 'labour') & (pd.notna(service_y2['job_description']))]['application_id'].unique()

        # Service header
        service_display = f"🔧 {service_name}"
        print(f"\n{service_display:<{col_width}}{divider}")
        print("─" * 160)

        max_labour = max(len(labour_y1_list), len(labour_y2_list))

        for labour_idx in range(max_labour):
            app_id_y1 = labour_y1_list[labour_idx] if labour_idx < len(labour_y1_list) else None
            app_id_y2 = labour_y2_list[labour_idx] if labour_idx < len(labour_y2_list) else None

            # Labour details
            y1_labour_text = ""
            y1_parts = []
            if app_id_y1:
                labour_rec = service_y1[service_y1['application_id'] == app_id_y1].iloc[0]
                job_desc = labour_rec['job_description'][:45] + "..." if len(str(labour_rec['job_description'])) > 45 else labour_rec['job_description']
                y1_labour_text = f"  💼 {job_desc}"
                y1_parts = list(service_y1[(service_y1['record_type'] == 'part') & (service_y1['application_id'] == app_id_y1) & (pd.notna(service_y1['oepr_part_number'])) & (service_y1['oepr_part_number'] != 'NR')]['oepr_part_number'].unique())

            y2_labour_text = ""
            y2_parts = []
            if app_id_y2:
                labour_rec = service_y2[service_y2['application_id'] == app_id_y2].iloc[0]
                job_desc = labour_rec['job_description'][:45] + "..." if len(str(labour_rec['job_description'])) > 45 else labour_rec['job_description']
                y2_labour_text = f"  💼 {job_desc}"
                y2_parts = list(service_y2[(service_y2['record_type'] == 'part') & (service_y2['application_id'] == app_id_y2) & (pd.notna(service_y2['oepr_part_number'])) & (service_y2['oepr_part_number'] != 'NR')]['oepr_part_number'].unique())

            print(f"{y1_labour_text:<{col_width}}{divider}{y2_labour_text:<{col_width}}")

            # Parts - side by side
            max_parts = max(len(y1_parts), len(y2_parts))
            for part_idx in range(max_parts):
                y1_part = f"    📦 {y1_parts[part_idx]}" if part_idx < len(y1_parts) else ""
                y2_part = f"    📦 {y2_parts[part_idx]}" if part_idx < len(y2_parts) else ""

                # Highlight common parts
                if part_idx < len(y1_parts) and part_idx < len(y2_parts) and y1_parts[part_idx] == y2_parts[part_idx]:
                    y1_part = f"    ✓ {y1_parts[part_idx]} (common)"
                    y2_part = f"    ✓ {y2_parts[part_idx]} (common)"

                print(f"{y1_part:<{col_width}}{divider}{y2_part:<{col_width}}")

    # Unique services
    unique_y1 = sorted(services_y1_list - services_y2_list)
    unique_y2 = sorted(services_y2_list - services_y1_list)

    if unique_y1 or unique_y2:
        print("\n" + "─" * 160)
        print("📌 SERVICES UNIQUE TO EACH YEAR\n")
        if unique_y1:
            print(f"Only in {year1}:")
            for service in unique_y1:
                parts_count = df_year1[(df_year1['service_name'] == service) & (df_year1['record_type'] == 'part') & (pd.notna(df_year1['oepr_part_number'])) & (df_year1['oepr_part_number'] != 'NR')]['oepr_part_number'].nunique()
                print(f"  • {service} ({parts_count} parts)")
        if unique_y2:
            print(f"\nOnly in {year2}:")
            for service in unique_y2:
                parts_count = df_year2[(df_year2['service_name'] == service) & (df_year2['record_type'] == 'part') & (pd.notna(df_year2['oepr_part_number'])) & (df_year2['oepr_part_number'] != 'NR')]['oepr_part_number'].nunique()
                print(f"  • {service} ({parts_count} parts)")

    print(f"\n{'='*160}\n")
