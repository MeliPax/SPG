# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import datetime, time
import os
from dotenv import load_dotenv

import matplotlib.pyplot as plt

import re
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# %%

def establish_db_connection(server, database, username, password, driver):
    connection_string = (
        f"mssql+pyodbc://{username}:{password}@{server}/{database}"
        f"?driver={driver.replace(' ', '+')}"
    )
    engine = create_engine(connection_string)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            for row in result:
                print("Connected successfully. SQL Server version:")
                print(row[0])
            return engine
    except Exception as e:
        print("Connection failed:")
        print(e)
        return None

# Adjust to include error handling for the db connection method



# %%
def load_env():
    load_dotenv(dotenv_path="creds\\.env")


def SERVER_conn(input_site):

    load_env()

    # DB server
    site_server = os.getenv(input_site)
    
    
    paramz = {
        "site": os.getenv('site_server'),
        "userName": os.getenv('USER_NAME'),
        "Password": os.getenv('PASSWORD_dev-test'),
        "Driver": os.getenv("ODBC_DRIVER")
    }

    db = os.getenv(input_site)

    server_conn = establish_db_connection(
        paramz["site"],
        db, 
        paramz["userName"],     
        paramz["Password"],
        paramz["Driver"])
        
    return server_conn


def db_request(query, server_conn_str):
    if server_conn_str is None:
        raise Exception("Database connection failed. Please check your credentials and connection settings.")

    # start_time = time.time()
    df = pd.read_sql(query, server_conn_str)

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"db_request must return a DataFrame, got {type(df)}")

    # end_time = time.time()
    # print(f"Query executed in {end_time - start_time:.2f} seconds")
    return df



# %%

# %%

# RO_all = "SELECT *  from Ops_tblRepairOrder where fldLastUpdated > '2020-01-1' AND fldStatus = 3 AND fldDivision IN (1)"
# query_all_requests = "SELECT *  from Ops_tblRequests where fldLastUpdated > '2020-01-1' AND fldAddWorkStatus IN (100, 300, 400)" 
# query_all_LabourLine = "SELECT *  from Ops_tblLabourLine where fldLastUpdated > '2020-01-1'"
# query_all_PartsLine = "SELECT *  from Ops_tblPartsLine where fldLastUpdated > '2020-01-1'"

# # More queries
# 
# 
# 

# get all F150 closed RO with relevant requests
RO_all = "SELECT RO.fldId, RO.fldContactRef, RO.fldVehicleRef, RO.fldDateOpened, RO.fldDateClosed FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName in ('F150', 'F-150') AND REQ.fldAddWorkStatus IN (100, 300, 400)"

query_all_requests = "SELECT Req.fldId, Req.fldWorkItemRef, Req.fldSequence, Req.fldDescription, Req.fldRequestCodeRef, Req.fldRequestCode, Req.fldRequestedTime, Req.fldOrderNumber, Req.fldLastUpdated FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef  WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName in ('F150', 'F-150') AND REQ.fldAddWorkStatus IN (100, 300, 400)" 
query_all_PartsLine = "SELECT PL.fldID, PL.fldRequestRef, PL.fldSequence, PL.fldPartNumber, PL.fldPartDesc, PL.fldRequested, PL.fldShipped, PL.fldOrderType, PL.fldDateAdded FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef  INNER JOIN Ops_tblPartsLine PL WITH(NOLOCK) ON PL.fldRequestRef = REQ.fldId WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName in ('F150', 'F-150') AND REQ.fldAddWorkStatus IN (100, 300, 400)"

query_all_LabourLine = f"SELECT LL.fldID, LL.fldRequestRef, LL.fldOpCodeRef, LL.fldActualHours, LL.fldSoldHours, LL.fldDescription, LL.fldAddedDate FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef INNER JOIN Ops_tblLabourLine LL WITH(NOLOCK) ON LL.fldRequestRef = REQ.fldId WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName in ('F150', 'F-150') AND REQ.fldAddWorkStatus IN (100, 300, 400)"
 

# %%
# search for op_codes_based_on_key_words

# select * from 
# Ops_tblOpCode2
# where fldDescription like ('%Water Pump%')

# %%

def pull_data_by_server(server_conn_str):
    # pull data for 
    RO_tbl = db_request(RO_all, server_conn_str)
    request_tbl = db_request(query_all_requests, server_conn_str)
    labourline_tbl = db_request(query_all_LabourLine, server_conn_str)
    partslines_tbl = db_request(query_all_PartsLine, server_conn_str)

    return RO_tbl, request_tbl, labourline_tbl, partslines_tbl

def pull_data_by_server_with_args(server_conn_str, queries, modelName):
    # pull data for 

    # RO_tbl = server_conn_str.execute(queries["RO_tbl"], {"model": modelName}).fetchall()
    # request_tbl = server_conn_str.execute(queries["Req_tbl"], {"model": modelName}).fetchall()
    # labourline_tbl = server_conn_str.execute(queries["Labour_tbl"], {"model": modelName}).fetchall()
    # partslines_tbl = server_conn_str.execute(queries["Parts_tbl"], {"model": modelName}).fetchall()

    RO_tbl = db_request(queries["RO_tbl"], server_conn_str)
    request_tbl = db_request(queries["Req_tbl"], server_conn_str)
    labourline_tbl = db_request(queries["Labour_tbl"], server_conn_str)
    partslines_tbl = db_request(queries["Parts_tbl"], server_conn_str)

    return RO_tbl, request_tbl, labourline_tbl, partslines_tbl


# %%

# # pull data for 
# RO_tbl_vw_174 = db_request(RO_all, vw_18_db)
# request_tbl_vw_174 = db_request(query_all_requests, vw_18_db)
# labourline_tbl_vw_174 = db_request(query_all_LabourLine, vw_18_db)
# partslines_tbl_vw_174 = db_request(query_all_PartsLine, vw_18_db)


# %%

# function to drop empty columns
def drop_empty_columns(df):
    df_cleaning = df.copy()
    # drop empty columns - must all empty
    df_cleaning = df_cleaning.dropna(axis=1, how='all')
    
    return df_cleaning
 


# %%
# function to filter columns
def filter_for_essential_columns(df, essential_cols):
    df_selected = df[essential_cols].copy()
    return df_selected


# %%
# Defined essential columns for each table

essential_columns_request_tbl = ['fldId', 'fldWorkItemRef', 'fldSequence', 'fldDescription',
       'fldRequestCodeRef', 'fldRequestCode', 'fldRequestedTime', 'fldOrderNumber',
        'fldLastUpdated']


essential_cols_labourline_tbl = ['fldID', 'fldRequestRef', 'fldOpCodeRef',
       'fldActualHours', 'fldSoldHours', 'fldDescription',
       'fldAddedDate']

essential_cols_partlines_tbl = ['fldID', 'fldRequestRef', 'fldSequence', 'fldPartNumber', 'fldPartDesc',
       'fldRequested', 'fldShipped', 'fldOrderType', 'fldDateAdded']


essential_cols_RO_tbl = ['fldId', 'fldContactRef', 'fldVehicleRef', 'fldDateOpened',
       'fldDateClosed'
       ]
       
  

# %%

# %%

def clean_datset(df, tbl_type):
    df_dropped_empty_cols = drop_empty_columns(df)

    if tbl_type == "request":
        df_filtered = filter_for_essential_columns(df_dropped_empty_cols, essential_columns_request_tbl)
    
    elif tbl_type == "labourline":
        df_filtered = filter_for_essential_columns(df_dropped_empty_cols, essential_cols_labourline_tbl)

    elif tbl_type == "partslines":
        df_filtered = filter_for_essential_columns(df_dropped_empty_cols, essential_cols_partlines_tbl)

    elif tbl_type == "RO_tbl":
        df_filtered = filter_for_essential_columns(df_dropped_empty_cols, essential_cols_RO_tbl)
        # remove
        
    return df_filtered
 


# %%

# request_tbl_vw_174 = clean_datset(request_tbl_vw_174, tbl_type="request")
# labor_tbl_vw_174 = clean_datset(labourline_tbl_vw_174, tbl_type="labourline")
# parts_tbl_vw_174 = clean_datset(partslines_tbl_vw_174, tbl_type="partslines")
# RO_tbl_vw_174 = clean_datset(RO_tbl_vw_174, tbl_type="RO_tbl")

# %%

# %% [markdown]
# #### Find a list of labour and parts for the following repair jobs 
#
# - water pump 
# - Timing belt
# - Electrical - exterior lights
#

# %%
def search_columns_for_keyword(df, keyword, column):
    if (column not in df.columns) or column=="":
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    filtered_df = df[df[column].str.contains(keyword, case=False, na=False)]
    return filtered_df

def get_top_ten_opcodes(df):
    top_ten = df["fldRequestCode"].value_counts().head(20)
    return top_ten

def search_request_by_opcode(df, opcode):
    search_result = df[df["fldRequestCode"]== opcode]
    
    return search_result

def search_request_by_list_of_opcodes(df, opcode_list):
    search_result = df[df["fldRequestCode"].isin(opcode_list)]
    
    return search_result



def part_items_metrics(parts_df):

    uniq_item_by_description = set(parts_df['fldPartDesc'].unique())
    metrics = pd.DataFrame(columns = ['partDesc','#UniqParts','#Qty','uniq_partNumbers'])

    for desc in uniq_item_by_description:
        item_count = len(parts_df[parts_df['fldPartDesc'] == desc]) 
        total_units = parts_df[parts_df['fldPartDesc'] == desc]['fldRequested'].sum()
        uniq_partNumbers = parts_df[parts_df['fldPartDesc'] == desc]['fldPartNumber'].unique().tolist()
        new_row = {
                    'partDesc': desc, 
                    '#UniqParts': item_count, 
                    '#Qty': total_units,
                    'uniq_partNumbers': uniq_partNumbers
                    }
        
        # metrics = pd.DataFrame(columns = ['partDesc','#UniqParts','#Qty','uniq_partNumbers'])
        
        new_row_df = pd.DataFrame([new_row]).reindex(columns=metrics.columns)
        metrics = pd.concat([metrics, new_row_df], ignore_index=True)
    return metrics




# def parts_summary(parts_tbl_df, total_req_count):
#     # Count occurrences of each unique part
#     # part_counts = parts_tbl_df['fldPartDesc'].value_counts()

#     part_counts = parts_tbl_df.groupby("fldPartDesc", as_index=False).agg(
#     count = ("fldPartNumber", "count"),
#     PartNum = ("fldPartNumber", lambda x: list(x.unique()))
#     ).sort_values("count", ascending=False)
#     part_counts = part_counts[~part_counts["fldPartDesc"].str.contains('ENV Fee|Core charge', case=False, regex=True)]


#     # Calculate percentage occurrence
#     part_counts["perc_occurence"] = round((part_counts['count'] / total_req_count * 100), 2)
    

#     # Sort for readability
#     metrics = metrics.sort_values(by='#perc_occurence', ascending=False)


#     # display(metrics)
#     return metrics



def parts_summary_v1(parts_tbl_df, total_req_count, similarity_threshold, ignore_words):
    """
    Summarizes parts occurrence and groups similar descriptions based on keyword similarity.
    
    Parameters:
    ----------
    parts_tbl_df : pd.DataFrame
        DataFrame containing part descriptions and request references.
    total_req_count : int
        Total number of requests for percentage calculation.
    similarity_threshold : float, optional (default=0.2)
        Jaccard similarity threshold for grouping descriptions.
    ignore_words : list of str, optional
        Words to ignore when determining similarity and forming combined names.
    
    Returns:
    -------
    pd.DataFrame
        DataFrame with combined part names and % occurrence.
    """
    
    if ignore_words is None:
        ignore_words = []
    
    # Normalize descriptions
    parts_tbl_df.loc[parts_tbl_df["fldPartDesc"].notna(), "fldPartDesc"] = (
        parts_tbl_df.loc[parts_tbl_df["fldPartDesc"].notna(), "fldPartDesc"].str.upper()
    )

    # Calculate initial metrics
    metrics = (
        parts_tbl_df[['fldPartDesc', 'fldRequestRef']]
        .drop_duplicates()
        .groupby('fldPartDesc')
        .size()
        .reset_index(name='Count')
    )

    # Tokenize descriptions and remove ignored words
    metrics['Tokens'] = metrics['fldPartDesc'].apply(
        lambda x: set(word for word in re.split(r'\W+', x) if word and word not in [w.upper() for w in ignore_words])
    )

    # Group similar descriptions
    grouped = []
    visited = set()

    for i, row_i in metrics.iterrows():
        if i in visited:
            continue
        group = [i]
        for j, row_j in metrics.iterrows():
            if j in visited or i == j:
                continue
            # Jaccard similarity
            sim = len(row_i['Tokens'] & row_j['Tokens']) / len(row_i['Tokens'] | row_j['Tokens'])
            if sim >= similarity_threshold:
                group.append(j)
        visited.update(group)
        grouped.append(group)

    # Aggregate groups
    new_rows = []
    for group in grouped:
        part_names = metrics.loc[group, 'fldPartDesc'].tolist()
        counts = metrics.loc[group, 'Count'].sum()
        common_tokens = set.intersection(*metrics.loc[group, 'Tokens']) if len(group) > 1 else metrics.loc[group, 'Tokens'].iloc[0]
        common_name = " ".join(sorted(common_tokens)) if common_tokens else part_names[0]
        new_rows.append({'Part': common_name, 'Count': counts})

    # Create final DataFrame
    final_df = pd.DataFrame(new_rows)
    final_df['%Occurrence'] = (final_df['Count'] / total_req_count) * 100
    final_df['%Occurrence'] = final_df['%Occurrence'].round(2)
    final_df = final_df.sort_values(by='%Occurrence', ascending=False).reset_index(drop=True)
    final_df = final_df[["Part", "%Occurrence"]]
    return final_df



def parts_summary(parts_tbl_df):
    

    parts_tbl_df.loc[parts_tbl_df["fldPartDesc"].notna(), "fldPartDesc"] = (
        parts_tbl_df.loc[parts_tbl_df["fldPartDesc"].notna(), "fldPartDesc"].str.upper()
    )

    parts_tbl_df = parts_tbl_df[~parts_tbl_df["fldPartDesc"].str.contains("ENV FEE | CORE", case=False, regex = True)] 

    total_req_count = len(parts_tbl_df['fldRequestRef'].unique())

    metrics = (parts_tbl_df[['fldPartDesc', 'fldRequestRef']]
               .drop_duplicates()
               .groupby('fldPartDesc', as_index=False)
                .agg(
                    uniq_fldPartDesc_count= ("fldRequestRef","nunique")
                    )
                )
        

    metrics["freq_perc"] = (metrics["uniq_fldPartDesc_count"]/total_req_count*100).round(2)

    partNumber_uniqueList = (parts_tbl_df.groupby('fldPartDesc',as_index=False)
                                .agg(PartNumbers = ('fldPartNumber', lambda x: list(pd.unique(x))))
                            )
    
    results = metrics.merge(partNumber_uniqueList, on = 'fldPartDesc')
    results = results.sort_values("freq_perc", ascending=False)

    results = results.reset_index(drop=True).set_axis(range(1, len(results) + 1))


    print(f"Sample size: {total_req_count} ROs")
    # print(f"# Unique opcodes: {len(filtered_df["fldRequestCode"].unique())}")
    results.columns =["Part","Count", "frequency_%", "PartNumbers"]

    return results[["Part", "frequency_%", "PartNumbers"]]



def search_parts_and_labour_by_req_id(labor, parts, req_id):

    if "fldRequestRef" not in labor.columns or "fldRequestRef" not in parts.columns:
        raise ValueError("The required column 'fldRequestRef' does not exist in one of the DataFrames.")
    
    labor_result = labor[labor["fldRequestRef"]== req_id]
    parts_result = parts[parts["fldRequestRef"]== req_id]
        
    print(f"Labour items for Request ID {req_id}:")
    display(labor_result)
    print(f"Parts items for Request ID {req_id}:")
    display(part_items_metrics(parts_result))
    


# %%

# %%

def remove_invalid_opcodes(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a pandas DataFrame, got {type(df)}")

    required_cols = ['fldFlatHours', 'fldTimeAllowed', 'fldCode']

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # Apply filter
    return df[(df["fldFlatHours"] > 0) & (df["fldTimeAllowed"] > 0)]
    # return df



def get_valid_op_codes_by_keyword(db_conn, key_word: str) -> list:
    query = f"SELECT * FROM Ops_tblOpCode2 WHERE fldDescription LIKE '%{key_word}%'"
    search_result = db_request(query, db_conn)

    if search_result.empty:
        raise LookupError(f"No matching data for query: {query}")

    filter_results = remove_invalid_opcodes(search_result)

    if filter_results.empty:
        raise LookupError(f"No matching records found for keyword: {key_word}")

    return filter_results



def get_all_op_codes(db_conn) -> pd.DataFrame:
    """
    Retrieves all opcodes from the database.
    """
    query = "SELECT * FROM Ops_tblOpCode2"
    
    search_result = db_request(query, db_conn)

    return search_result



# %%

def clean_data(RO_tbl, request_tbl, labourline_tbl, partslines_tbl):
    RO_tbl_cleaned = clean_datset(RO_tbl, tbl_type="RO_tbl")
    request_tbl_cleaned = clean_datset(request_tbl, tbl_type="request")
    labourline_tbl_cleaned = clean_datset(labourline_tbl, tbl_type="labourline")
    partslines_tbl_cleaned = clean_datset(partslines_tbl, tbl_type="partslines")

    return RO_tbl_cleaned, request_tbl_cleaned, labourline_tbl_cleaned, partslines_tbl_cleaned



# %%

# Function to count the number of times a unique part item appears on a repair job

def parts_analysis(part_items, tracker_count_part_item_once_per_job, parts_summary_df):
    for index, row in part_items.iterrows():
            part_number = row["fldPartNumber"]
            part_desc = row["fldPartDesc"]

            # Count occurrence of each part item used on job             
            if (part_number in parts_summary_df["Part Number"].values) and (part_number not in tracker_count_part_item_once_per_job):
                parts_summary_df.loc[parts_summary_df["Part Number"] == part_number, "Occurrence_count"] += 1
                tracker_count_part_item_once_per_job.add(part_number)
            else:
                new_row = {
                    "Part Number": part_number,
                    "Part Description": part_desc,
                    "Occurrence_count": 1
                }
                parts_summary_df = pd.concat([parts_summary_df, pd.DataFrame([new_row])], ignore_index=True) 
                tracker_count_part_item_once_per_job.add(part_number)
                parts_summary_df.sort_values(by="Occurrence_count", ascending=False, inplace=True)


    return parts_summary_df, tracker_count_part_item_once_per_job
 

# %%


def filter_rows_by_keywords(df, column_name, keywords=[[], []], return_print=True):
    """
    Filters rows in a DataFrame where:
    - All keywords in the first sub-array must be present (AND logic).
    - At least one keyword in the second sub-array must be present (OR logic).
    
    Parameters:
    ----------
    df : pd.DataFrame
        The DataFrame to search.
    column_name : str
        The name of the column to search within.
    keywords : list of two lists
        keywords[0] = list of must-have keywords (AND condition)
        keywords[1] = list of optional keywords (at least one required)
    return_counts : bool, optional (default=True)
        If True, returns value counts of the filtered column.
        If False, returns the filtered DataFrame.
    
    Returns:
    -------
    pd.Series or pd.DataFrame
        Value counts of the filtered column or the filtered DataFrame.
    """
    
    must_have = keywords[0]
    optional = keywords[1]
    
    # Build regex for must-have keywords (AND logic using lookaheads)
    must_pattern = "".join(f"(?=.*{re.escape(word)})" for word in must_have)
    
    # Build regex for optional keywords (OR logic using |)
    optional_pattern = "|".join(re.escape(word) for word in optional)
    
    # Combine patterns: must-have AND (optional OR empty if none)
    if optional:
        pattern = f"{must_pattern}(?=.*(?:{optional_pattern}))"
    else:
        pattern = must_pattern
    
    # Apply filter
    mask = df[column_name].str.contains(pattern, case=False, regex=True)
    filtered_df = df[mask]

    # print(f"Sample size: {len(filtered_df)}")
    # print(f"# Unique opcodes: {len(filtered_df["fldRequestCode"].unique())}")
    key_columns= ['fldRequestCode', 'fldDescription']

    
    return filtered_df[key_columns] if return_print else filtered_df


# %%
def labour_items_analysis(labour_items, tracker_count_labour_item_once_par_job, labour_summary_df):
    for index, row in labour_items.iterrows():
            op_code = row["fldOpCodeRef"]
            labour_desc = row["fldDescription"]

            if op_code in labour_summary_df["fldOpCodeRef"].values and op_code not in tracker_count_labour_item_once_par_job:
                labour_summary_df.loc[labour_summary_df["fldOpCodeRef"] == op_code, "Occurrence_count"] += 1
                tracker_count_labour_item_once_par_job.add(op_code)
            else:
                new_row = {
                    "fldOpCodeRef": op_code,
                    "fldDescription": labour_desc,
                    "Occurrence_count": 1
                }
                labour_summary_df = pd.concat([labour_summary_df, pd.DataFrame([new_row])] , ignore_index=True )
                tracker_count_labour_item_once_par_job.add(op_code)
                labour_summary_df.sort_values(by="Occurrence_count", ascending=False, inplace=True)  
    return labour_summary_df, tracker_count_labour_item_once_par_job


# %%
def requestsLines_analysis(req_id, part_items, labour_items, filtered_requests_df, request_summary_df):
    
    new_row = {
            "Request ID": req_id,
            "Description": filtered_requests_df[filtered_requests_df["fldId"] == req_id ]["fldDescription"].values[0],
            "fldRequestCode": filtered_requests_df[filtered_requests_df["fldId"] == req_id ]["fldRequestCode"].values[0],
            "#_PartItems": len(part_items),
            "#_LaborItems": len(labour_items)
            }

    request_summary_df = pd.concat([request_summary_df, pd.DataFrame([new_row])], ignore_index=True )
    request_summary_df.sort_values(by="#_PartItems", ascending=False, inplace=True)
    
    return request_summary_df

# %%


def run_analysis(labourline_tbl, partslines_tbl, request_tbl):


    filtered_requests_df = request_tbl
    
    # search from labour line and part line where fldRequestRef in filtered_requests_df['fldId']
    filtered_labour_df = labourline_tbl[labourline_tbl["fldRequestRef"].isin(filtered_requests_df['fldId'])]
    filtered_parts_df = partslines_tbl[partslines_tbl["fldRequestRef"].isin(filtered_requests_df['fldId'])]


    parts_summary_df = pd.DataFrame(columns=["Part Number", "Part Description", "Occurrence_count"])
    labour_summary_df = pd.DataFrame(columns=["fldOpCodeRef", "fldDescription", "Occurrence_count"])
    requestLine_summary_df = pd.DataFrame(columns=["Request ID", "Description","fldRequestCode", "#_PartItems", "#_LaborItems"])
 
    for items in filtered_requests_df['fldId'].values:
        req_id = items

        tracker_count_part_item_once_per_job = set()
        tracker_count_labour_item_once_par_job = set()
        

    # print(filtered_requests_df[filtered_requests_df["fldId"] == req_id ]["fldDescription"])

        # search for all parts and labour lines for this req_id
        part_items = filtered_parts_df[filtered_parts_df["fldRequestRef"]== req_id]
        labour_items = filtered_labour_df[filtered_labour_df["fldRequestRef"]==req_id]

        requestLine_summary_df = requestsLines_analysis(req_id, part_items, labour_items, filtered_requests_df, requestLine_summary_df)

        if not part_items.empty:
            parts_summary_df, tracker_count_part_item_once_per_job = parts_analysis(
                                                                                    part_items=part_items, 
                                                                                    tracker_count_part_item_once_per_job = tracker_count_part_item_once_per_job, 
                                                                                    parts_summary_df = parts_summary_df
                                                                                    )


        if not labour_items.empty:
            labour_summary_df, tracker_count_labour_item_once_par_job = labour_items_analysis(
                                                                                        labour_items=labour_items, 
                                                                                        tracker_count_labour_item_once_par_job=tracker_count_labour_item_once_par_job, 
                                                                                        labour_summary_df=labour_summary_df
                                                                                        ) 
                                                           

    return filtered_parts_df


# %%
def plot_stats(requestLine_summary_df):

    parts_stats =  (
    requestLine_summary_df["#_PartItems"]
    .value_counts()
    .reset_index()
    .rename(columns={'index': '#_PartItems', '#_PartItems': '#Parts'})
    )

    labour_stats =  (
        requestLine_summary_df["#_LaborItems"]
        .value_counts()
        .reset_index()
        .rename(columns={'index': '#_LaborItems', '#_LaborItems': '#labour'})
    )

    # Sort for better visualization
    parts_stats = parts_stats.sort_values(by='#Parts').reset_index(drop=True)
    labour_stats = labour_stats.sort_values(by='#labour').reset_index(drop=True)


    # Compute stats for Parts
    mean_parts = parts_stats['#Parts'].mean()
    median_parts = parts_stats['#Parts'].median()
    mode_parts = parts_stats['#Parts'].mode()[0]

    # Compute stats for Labour
    mean_labour = labour_stats['#labour'].mean()
    median_labour = labour_stats['#labour'].median()
    mode_labour = labour_stats['#labour'].mode()[0]


    # Plot Parts line
    plt.plot(parts_stats['#Parts'], parts_stats['count'], color='blue', marker='o', label='Parts')

    # Plot Labour line
    plt.plot(labour_stats['#labour'], labour_stats['count'], color='green', marker='o', label='Labour')


    # Add reference lines for mean
    plt.axvline(mean_parts, color='blue', linestyle='--', alpha=0.5, label=f'Parts Mean: {mean_parts:.2f}')
    plt.axvline(mean_labour, color='green', linestyle='--', alpha=0.5, label=f'Labour Mean: {mean_labour:.2f}')


    # Annotate median and mode
    plt.text(parts_stats['#Parts'].max(), median_parts, f'Median: {median_parts}', color='blue')
    plt.text(parts_stats['#Parts'].max(), mode_parts, f'Mode: {mode_parts}', color='blue')
    plt.text(labour_stats['#labour'].max(), median_labour, f'Median: {median_labour}', color='green')
    plt.text(labour_stats['#labour'].max(), mode_labour, f'Mode: {mode_labour}', color='green')


    # Labels and title
    plt.xlabel('Item Count')
    plt.ylabel('Frequency')
    plt.title('Parts vs Labour Items with Summary Stats')
    plt.legend()
    plt.grid(True)
    plt.show()


# %% [markdown]
# Analysis for Ford Site 130

# %%
def execute_model(request_tbl_df, search_key_words, labour_line_df, parts_line_df, similarity_threshold, ignore_words):
    requests_filtered= filter_rows_by_keywords(request_tbl_df, "fldDescription", search_key_words, False)

    # requestLine_summary_df, parts_summary_df, labour_summary_df, filtered_parts_df = run_analysis(labour_line_df, parts_line_df, requests_filtered)
    filtered_parts_df = run_analysis(labour_line_df, parts_line_df, requests_filtered)

    # print(f"Parts % occurrence in a {key_wrd_172} job")

    # display(parts_summary_v1(parts_tbl_df = filtered_parts_df, total_req_count = all_filtered_req_count, similarity_threshold=similarity_threshold, ignore_words=ignore_words))
    display(parts_summary(parts_tbl_df = filtered_parts_df))






# %%
# db_server_130 = "DB_server_130"
# # key_wrd = "Water Pump Replace"
# key_wrd_130 = "Water Pump or Gasket - Remove and Install"
# server_conn_db_130 = SERVER_conn(db_server_130)

# %%

# %% [markdown]
# Illustration for Site 172

# %%


# db_server_172 = "DB_server_172"
# # key_wrd = "Water Pump Replace"

# server_conn_db_172 = SERVER_conn(db_server_172)

# RO_tbl_db_172, request_tbl_db_172, labourline_tbl_db_172, partslines_tbl_db_172 = pull_data_by_server(server_conn_db_172)
# RO_tbl_db_172, request_tbl_db_172, labourline_tbl_db_172, partslines_tbl_db_172 = clean_data(RO_tbl_db_172, request_tbl_db_172, labourline_tbl_db_172, partslines_tbl_db_172)



# %%


# RO_tbl_db_130, request_tbl_db_130, labourline_tbl_db_130, partslines_tbl_db_130 = pull_data_by_server(server_conn_db_130)
# RO_tbl_db_130, request_tbl_db_130, labourline_tbl_db_130, partslines_tbl_db_130 = clean_data(RO_tbl_db_130, request_tbl_db_130, labourline_tbl_db_130, partslines_tbl_db_130)

 

# %%

# %%

# # Repair 1: Water pump replace - Site 172

# # search_key_words_water_pump_172 = [["water", "pump"], ["replace", "change", "Replacing", "leak"]]
# search_key_words_water_pump_172 = [["water", "pump"], []]

# print("Water pump - Site 172")
# resutlts_water_pump_site_172 = execute_model(request_tbl_db_172, search_key_words_water_pump_172, labourline_tbl_db_172, partslines_tbl_db_172, similarity_threshold=0.7, ignore_words=[" - ", "kit", "ASY", "Rep"])

# # Repair 1: Water pump replace - Site 130

# # search_key_words_water_pump_130 = [["water", "pump"], ["replace", "change", "Replacing", "leak"]]
# search_key_words_water_pump_130 = [["water", "pump"], []]
# print("Water pump - Site 130")
# resutlts_water_pump_site_130 = execute_model(request_tbl_db_130, search_key_words_water_pump_130, labourline_tbl_db_130, partslines_tbl_db_130, similarity_threshold= 0.6, ignore_words=[" - ", "kit", "ASY", "Rep"])


# # Repair 2 : Catalytic Converter Replace - Site 172

# search_key_words_catalytic_replace_172 = [["Catalytic Converter"], []]
# # filter_rows_by_keywords(request_tbl_db_172, "fldDescription", search_key_words_battery_replace_172, False)

# print("Catalytic Converter - Site 172")
# resutlts_Catalytic_Converter_site_172 = execute_model(request_tbl_df= request_tbl_db_172, search_key_words= search_key_words_catalytic_replace_172, labour_line_df= labourline_tbl_db_172, parts_line_df= partslines_tbl_db_172, similarity_threshold=0.7, ignore_words=[" - "])
 

# # Repair 2 : Catalytic Converter Replace - Site 130

# search_key_words_catalytic_replace_130 = [["Catalytic Converter"], []]
# # filter_rows_by_keywords(request_tbl_db_130, "fldDescription", search_key_words_battery_replace_130, False)

# print("Catalytic Converter - Site 130")
# resutlts_Catalytic_Converter_site_130 = execute_model(request_tbl_df= request_tbl_db_130, search_key_words= search_key_words_catalytic_replace_130, labour_line_df= labourline_tbl_db_130, parts_line_df= partslines_tbl_db_130, similarity_threshold=0.7, ignore_words=[" - "])
 


# # Repair 3 : Power Steering - Site 172

# # search_key_words_catalytic_replace_172 = [["Power steering"], ["replace", "change"]]
# search_key_words_catalytic_replace_172 = [["Power steering"], []]
# print("Power Steering - Site 172")
# resutlts_Power_Steering_site_172 = execute_model(request_tbl_df = request_tbl_db_172, search_key_words = search_key_words_catalytic_replace_172, labour_line_df = labourline_tbl_db_172, parts_line_df = partslines_tbl_db_172, similarity_threshold=0.7, ignore_words=[" - "])


 
# # Repair 3 : Power Steering - Site 130

# # search_key_words_catalytic_replace_130 = [["Power steering"], ["replace", "change"]]
# search_key_words_catalytic_replace_130 = [["Power steering"], []]
# print("Power Steering - Site 130")
# resutlts_Power_Steering_site_130 = execute_model(request_tbl_df = request_tbl_db_130, search_key_words = search_key_words_catalytic_replace_130, labour_line_df = labourline_tbl_db_130, parts_line_df = partslines_tbl_db_130, similarity_threshold=0.7, ignore_words=[" - "]) 
 

# %%

# compare_water_pump = resutlts_water_pump_site_172.merge(resutlts_water_pump_site_130, on="Part")
# compare_water_pump


# # print(type(resutlts_water_pump_site_172))

# %%
# Construct queries 


def is_validModel(server_conn, model):
    query = f" SELECT * FROM Veh_tblModel WHERE fldName = '{model}' AND fldInActive = 0"

    retults = db_request(query, server_conn)
    return len(retults)

def query_constructor(model):

    Queries= dict()

    RO_all = f"SELECT RO.fldId, RO.fldContactRef, RO.fldVehicleRef, RO.fldDateOpened, RO.fldDateClosed FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName = '{model}' AND REQ.fldAddWorkStatus IN (100, 300, 400)"

    query_all_requests = f"SELECT Req.fldId, Req.fldWorkItemRef, Req.fldSequence, Req.fldDescription, Req.fldRequestCodeRef, Req.fldRequestCode, Req.fldRequestedTime, Req.fldOrderNumber, Req.fldLastUpdated FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef  WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName = '{model}' AND REQ.fldAddWorkStatus IN (100, 300, 400)" 
    query_all_PartsLine = f"SELECT PL.fldID, PL.fldRequestRef, PL.fldSequence, PL.fldPartNumber, PL.fldPartDesc, PL.fldRequested, PL.fldShipped, PL.fldOrderType, PL.fldDateAdded FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef  INNER JOIN Ops_tblPartsLine PL WITH(NOLOCK) ON PL.fldRequestRef = REQ.fldId WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName = '{model}' AND REQ.fldAddWorkStatus IN (100, 300, 400)"

    query_all_LabourLine = f"SELECT LL.fldID, LL.fldRequestRef, LL.fldOpCodeRef, LL.fldActualHours, LL.fldSoldHours, LL.fldDescription, LL.fldAddedDate FROM Ops_tblRepairOrder RO WITH(NOLOCK) INNER JOIN Ops_tblRequests REQ WITH(NOLOCK) ON RO.fldId = REQ.fldWorkItemRef INNER JOIN Veh_tblVehicle VEH WITH(NOLOCK) ON VEH.fldId = RO.fldVehicleRef INNER JOIN Veh_tblTrim TR WITH(NOLOCK) ON TR.fldId = VEH.fldTrimRef INNER JOIN Veh_tblModel MOD WITH(NOLOCK) ON MOD.fldId = TR.fldModelRef INNER JOIN Ops_tblLabourLine LL WITH(NOLOCK) ON LL.fldRequestRef = REQ.fldId WHERE 1=1 AND RO.fldStatus = 3 AND RO.fldDivision IN (1) AND MOD.fldName = '{model}' AND REQ.fldAddWorkStatus IN (100, 300, 400)"

    Queries["RO_tbl"] = RO_all
    Queries["Req_tbl"] = query_all_requests
    Queries["Parts_tbl"] = query_all_PartsLine
    Queries["Labour_tbl"] = query_all_LabourLine

    return Queries

# %%


def data_pull(modelName,db_server):
    
    # key_wrd = "Replace Water Pump"
    server_conn = SERVER_conn(db_server)
    
    if not is_validModel(server_conn, modelName):
        raise ValueError("Provided Model Name does not exists")
    queries = query_constructor(modelName)
    RO_tbl, request_tbl, labourline_tbl, partslines_tbl = pull_data_by_server_with_args(server_conn, queries, modelName)
    RO_tbl, request_tbl, labourline_tbl, partslines_tbl = clean_data(RO_tbl, request_tbl, labourline_tbl, partslines_tbl)
    return RO_tbl, request_tbl, labourline_tbl, partslines_tbl


def save_data(directoryPath : str, df, siteName):
    # df.to_csv('dat/site')
    return 


def run_model(key_wrd, request_tbl, labourline_tbl, partslines_tbl):
    execute_model(request_tbl_df = request_tbl, search_key_words = key_wrd, labour_line_df = labourline_tbl, parts_line_df = partslines_tbl, similarity_threshold=0.7, ignore_words=[" - "]) 




    

# %%
def dataset_info(RO_tbl, req_tbl, labour_tbl, parts_tbl, site):

    print(f"Sample Size: Site {site}")

    print(f"RO_tbl: {len(RO_tbl)}")
    print(f"Req_tbl: {len(req_tbl)}")
    print(f"LabourLines_tbl: {len(labour_tbl)}")
    print(f"PartLines_tbl: {len(parts_tbl)}")


# %%
modelName = "F-150"
Servers = ["DB_server_130",'DB_server_172']

RO_tbl_130_f150, request_tbl_130_f150, labourline_tbl_130_f150, partslines_tbl_130_f150 = data_pull(modelName, Servers[0])

# %%
key_wrd = "Water Pump"
execute_model(request_tbl_df = request_tbl_130_f150, search_key_words = key_wrd, labour_line_df = labourline_tbl_130_f150, parts_line_df = partslines_tbl_130_f150, similarity_threshold=0.7, ignore_words=[" - "])

# %%
modelName = "Escape"
Servers = ["DB_server_130",'DB_server_172']

RO_tbl_130, request_tbl_130, labourline_tbl_130, partslines_tbl_130 = data_pull(modelName, Servers[0])
RO_tbl_172, request_tbl_172, labourline_tbl_172, partslines_tbl_172 = data_pull(modelName, Servers[1])



# %%

dataset_info(RO_tbl_130, request_tbl_130, labourline_tbl_130, partslines_tbl_130, "130")
print("---------------------------------------------------------------------")
dataset_info(RO_tbl_172, request_tbl_172, labourline_tbl_172, partslines_tbl_172, "172")


# %%

# %%
key_wrds = ["Water Pump", "Power steering", "Catalytic Converter"]

key_wrd = "Water Pump"
execute_model(request_tbl_df = request_tbl_130, search_key_words = key_wrd, labour_line_df = labourline_tbl_130, parts_line_df = partslines_tbl_130, similarity_threshold=0.7, ignore_words=[" - "])
execute_model(request_tbl_df = request_tbl_172, search_key_words = key_wrd, labour_line_df = labourline_tbl_172, parts_line_df = partslines_tbl_172, similarity_threshold=0.7, ignore_words=[" - "])
    

# %%

# %%

# %%

# %%

# %%

# %%
# len(request_tbl_db_130[request_tbl_db_130["fldDescription"].str.contains("Water pump", case=False)])
