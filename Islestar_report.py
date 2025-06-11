import os
import time
from typing import Dict, List
import pandas as pd

timestamp = int(time.time())


# Initialize category mapping
CATEGORY_MAPPING: Dict[str, str] = {
    "Daily Rate Roaming": "Daily Rate Roaming",
    "UK to Abroad SMS": "UK to Abroad",
    "UK to Abroad": "UK to Abroad",
    "Channel Islands & Isle of Man": "UK to Abroad",
    "Data Abroad": "Roaming Data",
    "Voda Red Data Overage": "Roaming Data",
    "Roam Call MO": "Roaming Calls",
    "Roam Call MT": "Roaming Calls",
    "Landline": "Other",
    "Domestic Data": "Other",
    "International SMS": "Other",
    "International": "Other",
    "Data UK": "Other",
    "On-Net": "Other",
    "Cross-Net": "Other",
    "Roam Text MT": "Other",
    "Special Numbers": "Other",
    "Text Msg UK": "Other",
    "Non Geo": "Other",
    "MMS": "Other",
    "Voicemail": "Other",
    "Roam Text MO": "Other",
    "Service": "Other",
    "Other Std": "Other",
    "SMS": "Other"
}

# Initialize billing columns
BILLING_COLUMNS: List[str] = [
    "EU Daily Roaming Charges",
    "RoW Daily Roaming Charges",
    "Daily Rate Roaming",
    "Roaming Calls",
    "Roaming Data",
    "UK to Abroad",
    "Other Charges",
    "Total",
    "No Usage"
]


def load_service_breakdown(file_path: str) -> pd.DataFrame:
    """
    Load the service breakdown CSV file and process it.

    Args:
        file_path (str): Path to the service breakdown CSV file

    Returns:
        pd.DataFrame: Processed DataFrame
    """
    df = pd.read_csv(file_path, dtype={"Service": str})  # Ensure "Service" is read as a string
    new_df = pd.DataFrame()
    new_df["Department"] = df["Cost Centre"]
    new_df["User"] = df["Name"]
    new_df["Number"] = df["Service"].astype(str).str.strip()
    df["Fixed Charges"] = pd.to_numeric(df["Fixed Charges"], errors="coerce").fillna(0)
    new_df["Fixed Charges"] = df["Fixed Charges"]
    return new_df


def process_billing_data(service_breakdown_path: str, usage_csv_path: str, client_name: str) -> str:
    """
    Process the billing data for Islestar

    Args:
        service_breakdown_path (str): Path to the service breakdown CSV file
        usage_csv_path (str): Path to the usage CSV file
        client_name (str): Name of the client for the output file

    Returns:
        str: Path to the generated report
    """
    new_df = load_service_breakdown(service_breakdown_path)

    for col in BILLING_COLUMNS:
        new_df[col] = 0  # Default all charge columns to 0

    # Load the usage CSV file
    if os.path.exists(usage_csv_path):
        usage_df = pd.read_csv(usage_csv_path, dtype={"Service": str})
        usage_df["Service"] = usage_df["Service"].astype(str).str.strip()
        usage_df["Usage Category"] = usage_df["Usage Category"].map(CATEGORY_MAPPING).fillna("Other")
        usage_df["Cost"] = pd.to_numeric(usage_df["Cost"], errors="coerce").fillna(0)

        # Correctly update "No Usage" column
        new_df["No Usage"] = ~new_df["Number"].isin(usage_df["Service"])
        new_df["No Usage"] = new_df["No Usage"].replace({True: "X", False: ""})

        # Process category costs and map to correct columns
        for category in set(CATEGORY_MAPPING.values()):
            category_costs = usage_df[usage_df["Usage Category"] == category].groupby("Service")["Cost"].sum()

            # Map the costs to the correct column in billing report
            if category == "Other":
                new_df["Other Charges"] = new_df["Number"].map(category_costs).fillna(0)
            else:
                new_df[category] = new_df["Number"].map(category_costs).fillna(0)

        # Count occurrences based on Cost values (Pivot Table Logic)
        daily_roaming_df = usage_df[usage_df["Usage Category"] == "Daily Rate Roaming"]

        # Count occurrences where Cost == 2 (EU Roaming)
        eu_roaming_count = daily_roaming_df[daily_roaming_df["Cost"] == 2].groupby("Service").size()

        # Count occurrences where Cost == 5 (RoW Roaming)
        row_roaming_count = daily_roaming_df[daily_roaming_df["Cost"] == 5].groupby("Service").size()

        # Map to Billing Report by aligning "Service" in Usage CSV with "Number" in Billing Report
        new_df["EU Daily Roaming Charges"] = new_df["Number"].map(eu_roaming_count).fillna(0).astype(int)
        new_df["RoW Daily Roaming Charges"] = new_df["Number"].map(row_roaming_count).fillna(0).astype(int)

    # Calculate Total Charges (EXCLUDES Roaming Counts)
    new_df["Total"] = (
            new_df["Fixed Charges"] +
            new_df["Daily Rate Roaming"] +
            new_df["UK to Abroad"] +
            new_df["Roaming Data"] +
            new_df["Roaming Calls"] +
            new_df["Other Charges"]
    )

    # Format monetary values correctly
    monetary_columns = [
        "Fixed Charges", "Daily Rate Roaming", "UK to Abroad",
        "Roaming Data", "Roaming Calls", "Other Charges", "Total"
    ]

    for col in monetary_columns:
        new_df[col] = new_df[col].apply(lambda x: f"£{x:,.2f}")

    # Ensure EU & RoW Roaming Charges remain as integers (not currency)
    new_df["EU Daily Roaming Charges"] = new_df["EU Daily Roaming Charges"].astype(int)
    new_df["RoW Daily Roaming Charges"] = new_df["RoW Daily Roaming Charges"].astype(int)

    # Save to Excel in Downloads folder with month_year_Bill_Run format
    downloads_path = os.path.expanduser("~/Downloads")
    prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
    current_year = pd.Timestamp.now().year
    output_path = os.path.join(downloads_path, f"{prev_month}_{current_year}_Bill_Run_{client_name}.xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        new_df.to_excel(writer, index=False, sheet_name="Billing Report")

    return output_path
