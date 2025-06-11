import os
import re
import time
from typing import Optional, Union
import pandas as pd
from datetime import datetime, timedelta

def ensure_directories_exist():
    """
    Ensure all required directories exist for ConvaTec UK report generation.
    """
    os.makedirs(os.path.join("data", "input", "convatec"), exist_ok=True)
    os.makedirs(os.path.join("data", "output"), exist_ok=True)

# File paths
GTN_SERVICES_FILE = os.path.join("data", "input", "convatec", "reports__listOfServices.csv")


def format_phone_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove leading zeros from phone numbers

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with phone numbers formatted
    """
    for col in df.columns:
        if df[col].astype(str).str.startswith("07").any():
            df[col] = df[col].apply(lambda x: str(x).strip() if str(x).startswith("07") else x)
    return df


def process_and_combine_csv(input_filepath_1: str, input_filepath_2: str) -> pd.DataFrame:
    """
    Process and combine two CSV files

    Args:
        input_filepath_1: Filepath to first CSV file
        input_filepath_2: Filepath to second CSV file

    Returns:
        Combined DataFrame
    """
    timestamp = int(time.time())
    output_combined_file = os.path.join("data", "output", f"Convatec_Combined_Service_Breakdown_{timestamp}.csv")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.join("data", "output"), exist_ok=True)
    
    df1 = pd.read_csv(input_filepath_1, dtype=str)
    df2 = pd.read_csv(input_filepath_2, dtype=str)

    df1 = df1.sort_values(by=df1.columns.tolist(), ascending=True)
    df2 = df2.sort_values(by=df2.columns.tolist(), ascending=True)

    df1 = format_phone_numbers(df1)
    df2 = format_phone_numbers(df2)

    output_combined_df = pd.concat([df1, df2], ignore_index=True)

    # Save the combined CSV for debugging
    output_combined_df.to_csv(output_combined_file, index=False)
    print(f"Combined CSV saved as: {output_combined_file}")

    return output_combined_df


def find_column(df: pd.DataFrame, possible_names: list[str]) -> Optional[str]:
    """
    Find column in DataFrame based on possible names

    Args:
        df: Input DataFrame
        possible_names: List of possible column names

    Returns:
        Column name if found, otherwise None
    """
    for name in possible_names:
        for col in df.columns:
            if name.lower() in col.lower():
                return col
    return None


def convert_data_usage(value: str) -> Optional[float]:
    """
    Convert data usage string to gigabytes (GB).

    Args:
        value (str): Data usage string with unit (e.g., "500 MB", "1.5 GB", "800 KB")

    Returns:
        Optional[float]: Data usage in GB rounded to 2 decimal places, or None if conversion fails
    """
    match = re.match(r"(\d+(?:\.\d+)?)\s*(GB|MB|KB)", str(value), re.IGNORECASE)
    if match:
        num, unit = float(match.group(1)), match.group(2).upper()
        if unit == "GB":
            return round(num, 2)
        elif unit == "MB":
            # Convert MB to GB: divide by 1024
            return round(num / 1024, 2)
        elif unit == "KB":
            # Convert KB to GB: divide by 1024*1024
            return round(num / (1024 * 1024), 2)
    return None


def get_date_ranges() -> tuple[str, str]:
    """
    Get billing period and usage period strings.

    Returns:
        Tuple of billing period and usage period strings
    """
    today = datetime.today()
    first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = today.replace(day=1) - timedelta(days=1)

    return (
        today.strftime("%b-%y"),
        f"{first_day.strftime('%d/%m/%y')} - {last_day.strftime('%d/%m/%y')}"
    )


def clean_user_name(name: str) -> tuple[str, bool]:
    """
    Clean username and determine if it's a spare line.

    Args:
        name: Username string

    Returns:
        Tuple of cleaned name and True if it's a spare line, False otherwise
    """
    name = str(name).strip()
    is_spare = bool(re.search(r"\bspare(?:\swas)?\b", name, re.IGNORECASE))
    clean_name = re.sub(r"\b(spare|was|-)+\b", "", name, flags=re.IGNORECASE).strip()
    return clean_name, is_spare


def check_spare_status(name: str) -> bool:
    """
    Check if a line is spare by looking at the name.

    Args:
        name: Username string

    Returns:
        bool: True if name indicates it's a spare line
    """
    name = str(name).strip()
    return bool(re.search(r"\bspare(?:\swas)?\b", name, re.IGNORECASE))


def standardise_phone_number(number: str) -> str:
    """
    Standardise phone number format by removing non-numeric characters.

    Args:
        number (str): Phone number string that may contain non-numeric characters
            (e.g., spaces, dashes, parentheses)

    Returns:
        str: Standardised phone number string containing only digits
            (e.g., "07123456789")
    """
    return re.sub(r'[^0-9]', '', str(number).strip())


def generate_billing_report(service_breakdown: pd.DataFrame) -> str:
    """
    Generate billing report with improved organization and error handling.

    Args:
        service_breakdown: Combined DataFrame with billing data
        
    Returns:
        Path to the generated Excel report
    """

    # 1️⃣ Load and clean List of Services (Tariff Information)
    services_df = pd.read_csv(GTN_SERVICES_FILE, dtype=str)
    services_df.columns = services_df.columns.str.strip()
    
    # Create mappings from List of Services
    service_mappings = {}
    for _, service_row in services_df.iterrows():
        service_no = service_row.get("SERVICE_NO", "")
        if service_no:
            service_mappings[service_no] = {
                "Tariff": service_row.get("TEMPLATE_NAME", "Unknown"),
                "Start/End Date": service_row.get("CONTRACT_START_DATE", ""),
                "Cost Centre": service_row.get("ADDITIONAL_FIELD_1", "")
            }

    # 2️⃣ Process Each Row in `service_breakdown` and Generate Report
    report_data = []
    for _, row in service_breakdown.iterrows():
        number = standardise_phone_number(row["Service"])
        user_name, is_spare = clean_user_name(row["Name"])
        
        # Get service details from mapping
        service_details = service_mappings.get(number, {
            "Tariff": "Unknown",
            "Start/End Date": "",
            "Cost Centre": ""
        })
        
        # Get line rental and out of bundle spend
        # Clean and convert numeric values, handling commas and spaces
        def clean_numeric(value):
            if isinstance(value, (int, float)):
                return float(value)
            if not value or value == '':
                return 0.0
            # Remove spaces, commas, and handle negative values
            cleaned = str(value).strip().replace(',', '')
            try:
                return float(cleaned)
            except ValueError:
                # If conversion fails, return 0
                return 0.0
        
        line_rental = clean_numeric(row.get("Fixed Charges", 0))
        out_of_bundle = clean_numeric(row.get("Usage Charges", 0))
        
        # Calculate total spend
        total_spend = line_rental + out_of_bundle
        
        # Convert data usage to GB
        data_usage_gb = convert_data_usage(row.get("Data Usage", 0))
        
        report_data.append({
            "Number": number,
            "User": user_name,
            "Spare?": "TRUE" if is_spare else "",
            "Company": row.get("Cost Centre", "").strip(),
            "Start/End Date": service_details["Start/End Date"],
            "Tariff": service_details["Tariff"],
            "Line Rental": line_rental,
            "Out of Bundle spend": out_of_bundle,
            "Total Spend": total_spend,
            "Data Used (GB)": data_usage_gb if data_usage_gb is not None else row.get("Data Usage", 0)
        })

    # Convert to DataFrame and Save Report
    report_df = pd.DataFrame(report_data)
    
    # Generate output file path
    timestamp = int(time.time())
    downloads_path = os.path.expanduser("~/Downloads")
    # Ensure the Downloads directory exists
    os.makedirs(downloads_path, exist_ok=True)
    prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
    current_year = pd.Timestamp.now().year
    # Add timestamp to filename to ensure uniqueness
    output_path = os.path.join(downloads_path, f"{prev_month}_{current_year}_Bill_Run_ConvaTec UK_{timestamp}.xlsx")
    print(f"Will save report to: {output_path}")

    billing_period, usage_period = get_date_ranges()
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Summary Report")
        header_format = workbook.add_format({'bold': True, 'bg_color': 'black', 'font_color': 'white'})

        worksheet.write(0, 0, "Billing Period", header_format)
        worksheet.write(0, 1, billing_period)
        worksheet.write(1, 0, "Usage Period", header_format)
        worksheet.write(1, 1, usage_period)

        report_df.to_excel(writer, sheet_name="Summary Report", startrow=2, index=False)

    print(f"Billing report saved as: {output_path}")
    return output_path


if __name__ == "__main__":
    # Ensure required directories exist
    ensure_directories_exist()
    
    # Example usage
    file1 = "data/input/convatec/ServicesBreakdown (4).csv"
    file2 = "data/input/convatec/ServicesBreakdown (3).csv"

    combined_df = process_and_combine_csv(file1, file2)
    generate_billing_report(combined_df)
