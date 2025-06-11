import os
import time
import pandas as pd

def process_kf_report(usage_file: str, calls_file: str, client_name: str) -> str:
    """
    Process Knight Frank report from usage and calls CSV files.
    
    Args:
        usage_file (str): Path to the usage CSV file
        calls_file (str): Path to the calls CSV file
        client_name (str): Name of the client for the output file
        
    Returns:
        str: Path to the generated report
    """
    # Define the desired column headers for the final output
    desired_columns = [
        "CallDate", "CallTime", "CustomerCode", "CustomerName", "ContractName",
        "Custom 1", "Service", "UserName", "DialledNumber", "Duration",
        "Data (KB)", "Usage Type", "Usage Category", "Bundle Type", "Cost",
        "Country Code", "Vat Code"
    ]

    # Load the usage CSV data into a DataFrame
    print("Reading usage CSV file...")
    df = pd.read_csv(usage_file)
    print("Usage CSV loaded. Rows:", len(df))

    # Load the calls CSV data (for lookup)
    print("Reading calls CSV file for lookup...")
    calls_df = pd.read_csv(calls_file)
    print("Calls CSV loaded. Rows:", len(calls_df))

    # Create a lookup dictionary from calls_df:
    # Map the "Service" column to its corresponding "Custom 1" value
    lookup_dict = calls_df.set_index("Service")["Custom 1"].to_dict()

    # Update the "Custom 1" column in the usage DataFrame using the lookup dictionary.
    # This mimics an Excel XLOOKUP based on the "Service" column.
    print("Performing lookup for 'Custom 1' values...")
    df["Custom 1"] = df["Service"].map(lookup_dict)

    # Convert the looked-up "Custom 1" values to numeric format.
    # Any non-convertible value will be set as NaN.
    df["Custom 1"] = pd.to_numeric(df["Custom 1"], errors="coerce")
    print("'Custom 1' column updated and converted to numeric.")

    # Ensure the "DialledNumber" column is numeric with no decimals
    print("Converting 'DialledNumber' column to numeric (no decimals)...")
    # Convert to numeric, coercing errors to NaN, then fill NaN with 0
    df["DialledNumber"] = pd.to_numeric(df["DialledNumber"], errors="coerce").fillna(0)
    # Convert to integer to remove decimal places
    df["DialledNumber"] = df["DialledNumber"].astype('Int64')  # Using Int64 to handle larger numbers

    # Reorder (or select) the DataFrame columns to match the desired order.
    # Any extra columns not in desired_columns will be dropped.
    print("Reordering columns to match desired order...")
    df = df.reindex(columns=desired_columns)

    # Filter to only include rows where "Usage Type" is "Voice"
    print(f"Filtering data to only include 'Voice' usage type. Before filtering: {len(df)} rows")
    df = df[df["Usage Type"] == "Voice"]
    print(f"After filtering: {len(df)} rows")

    # Write the DataFrame to an Excel file in Downloads folder with month_year_Bill_Run format
    downloads_path = os.path.expanduser("~/Downloads")
    prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
    current_year = pd.Timestamp.now().year
    output_path = os.path.join(downloads_path, f"{prev_month}_{current_year}_Bill_Run_{client_name}.xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="KF Report")
        
        # Get the workbook and the worksheet
        workbook = writer.book
        worksheet = writer.sheets["KF Report"]
        
        # Find the column index for "DialledNumber"
        dialled_number_col_idx = desired_columns.index("DialledNumber") + 1  # +1 because Excel is 1-indexed
        
        # Set the number format for the "DialledNumber" column to Number with no decimal places
        for row in range(2, len(df) + 2):  # +2 because Excel is 1-indexed and we have a header row
            cell = worksheet.cell(row=row, column=dialled_number_col_idx)
            cell.number_format = '0'  # '0' is the format code for Number with no decimal places

    return output_path
