import os
import time
import pandas as pd

def load_services_breakdown(file_path: str) -> pd.DataFrame:
    """
    Load the Tysers Services Breakdown CSV file and clean its column names.
    """
    df = pd.read_csv(file_path, dtype=str)
    df.columns = df.columns.str.strip()
    print("Services CSV Columns:", df.columns.tolist())
    return df

def load_data_usage_summary(file_path: str) -> dict:
    """
    Load the Data Usage Summary CSV file and return a mapping of service to usage.
    The usage value is taken from the column immediately to the right of the "Service" column.
    """
    df = pd.read_csv(file_path, dtype=str)
    df.columns = df.columns.str.strip()
    print("Data Usage Summary Columns:", df.columns.tolist())
    
    if "Service" not in df.columns:
        print("Error: 'Service' column not found in Data Usage Summary.")
        return {}
    
    service_index = df.columns.get_loc("Service")
    if service_index + 1 >= len(df.columns):
        print("Error: No usage column found next to 'Service' column.")
        return {}
    
    usage_col = df.columns[service_index + 1]
    print(f"Mapping usage from column: {usage_col}")
    
    mapping = dict(zip(
        df["Service"].astype(str).str.strip(), 
        df[usage_col].astype(str).str.strip()
    ))
    return mapping

def load_usage_data(file_path: str) -> pd.DataFrame:
    """
    Load the Usage CSV file for cost categorization and clean its column names.
    """
    df = pd.read_csv(file_path, dtype=str)
    df.columns = df.columns.str.strip()
    if "Service" in df.columns:
        df["Service"] = df["Service"].str.strip()
    if "Cost" in df.columns:
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0)
    if "Usage Category" in df.columns:
        df["Usage Category"] = df["Usage Category"].str.strip()
    return df

def lookup_and_format(service: str, mapping: dict) -> str:
    """
    Look up the usage value for a given service from the data usage mapping and format it to two decimals.
    (Used for the "Data (GB)" column.)
    """
    value = mapping.get(service, "")
    try:
        return f"{float(value):.2f}" if value != "" else "00.00"
    except Exception:
        return "00.00"

def create_tysers_report(services_file: str, data_usage_file: str, usage_file: str, client_name: str, pre_tax_amount: float = 0, total_tax_amount: float = 0) -> str:
    
    # Final report header order
    headers = [
        "Cost Centre", "User", "Number", "Voice", "International/Roam", 
        "SMS/MMS", "Business Traveller", "Data (GB)", "Data UK (£)", 
        "Data Roaming (£)", "Call Duration (hh:mm:ss)", "Total Usage", 
        "Recurring", "Net", "VAT", "Gross"
    ]
    
    # Load input files
    services_df = load_services_breakdown(services_file)
    data_usage_mapping = load_data_usage_summary(data_usage_file)
    usage_df = load_usage_data(usage_file)
    
    # Build the base final report from the Services file
    report_df = pd.DataFrame(columns=headers)
    report_df["Cost Centre"] = services_df.get("Cost Centre", "")
    report_df["User"] = services_df.get("Name", "")
    report_df["Number"] = services_df.get("Service", "").astype(str).str.strip()
    report_df["Recurring"] = services_df.get("Fixed Charges", "")
    
    # Copy Voice Usage to Call Duration (hh:mm:ss)
    if "Voice Usage" in services_df.columns:
        report_df["Call Duration (hh:mm:ss)"] = services_df["Voice Usage"]
    else:
        voice_usage_col = next((col for col in services_df.columns if "voice" in col.lower() and "usage" in col.lower()), "")
        report_df["Call Duration (hh:mm:ss)"] = services_df.get(voice_usage_col, "")
    
    # Populate "Data (GB)" using data_usage_mapping (formatted to two decimals)
    report_df["Data (GB)"] = report_df["Number"].apply(lambda x: lookup_and_format(x, data_usage_mapping))
    
    # ----- Process Usage CSV for cost categorization -----
    category_mapping = {
        "Data UK": "Data UK (£)",
        "Data Abroad": "Data Roaming (£)",
        "Voda Red Data Overage": "Data Roaming (£)",
        "Daily Rate Roaming": "Business Traveller",
        "Channel Islands & Isle of Man Text Msg": "International/Roam",
        "Channel Islands & Isle of Man": "International/Roam",
        "Roam MMS": "International/Roam",
        "UK to Abroad": "International/Roam",
        "Roam Call MT": "International/Roam",
        "Roam Call MO": "International/Roam",
        "Roam Text MO": "International/Roam",
        "Roam Text MT": "International/Roam",
        "UK to Abroad SMS": "International/Roam",
        "Text Msg UK": "SMS/MMS",
        "Premium Text": "SMS/MMS",
        "MMS": "SMS/MMS",
        "Service": "Voice",
        "Cross-Net": "Voice",
        "On-Net": "Voice",
        "Voicemail": "Voice",
        "Landline": "Voice",
        "Premium": "Voice",
        "Non Geo": "Voice",
        "Freephone": "Voice",
        "Call Return": "Voice",
        "Personal": "Voice"
    }
    usage_df["Mapped Category"] = usage_df["Usage Category"].map(category_mapping)
    
    grouped = usage_df.groupby(["Service", "Mapped Category"])["Cost"].sum().reset_index()
    pivot = grouped.pivot(index="Service", columns="Mapped Category", values="Cost")
    pivot = pivot.fillna(0)
    
    target_categories = ["Voice", "International/Roam", "SMS/MMS", "Business Traveller", "Data UK (£)", "Data Roaming (£)"]
    
    def get_cost(service, col):
        if service in pivot.index and col in pivot.columns:
            return f"{float(pivot.loc[service, col]):.2f}"
        else:
            return "00.00"
    
    for col in target_categories:
        report_df[col] = report_df["Number"].apply(lambda x: get_cost(x, col))
    
    # Compute Total Usage as the sum of the target cost columns.
    def compute_total(row):
        try:
            # Sum up all target categories, handling values with commas
            total = 0.0
            for col in target_categories:
                val = row[col]
                if val not in ["", "00.00"]:
                    # Remove any currency symbols or commas
                    val = str(val).replace("£", "").replace(",", "")
                    total += float(val)
            return f"{total:.2f}"
        except Exception as e:
            print(f"Error computing total for row with Number {row.get('Number', 'unknown')}: {e}")
            return "00.00"
    
    report_df["Total Usage"] = report_df.apply(compute_total, axis=1)
    
    # Compute Net as the sum of Total Usage and Recurring.
    def compute_net(row):
        try:
            total_usage = float(row["Total Usage"]) if row["Total Usage"] not in ["", "00.00"] else 0.0
            
            # Handle recurring value more robustly
            recurring_val = row["Recurring"]
            if recurring_val in ["", "00.00"]:
                recurring = 0.0
            else:
                # Remove any currency symbols or commas
                recurring_val = str(recurring_val).replace("£", "").replace(",", "")
                recurring = float(recurring_val)
                
            net_val = total_usage + recurring
            return f"{net_val:.2f}"
        except Exception as e:
            print(f"Error computing net for row with Number {row.get('Number', 'unknown')}: {e}")
            print(f"Total Usage: {row.get('Total Usage', 'N/A')}, Recurring: {row.get('Recurring', 'N/A')}")
            return "00.00"
    
    report_df["Net"] = report_df.apply(compute_net, axis=1)
    
    # Calculate VAT ratio based on provided values
    if pre_tax_amount > 0 and total_tax_amount > 0:
        vat_ratio = total_tax_amount / pre_tax_amount
    else:
        vat_ratio = 0.2  # Default 20% VAT
    
    def compute_vat(row):
        try:
            # Handle net value with commas
            net_val = row["Net"]
            if net_val in ["", "00.00"]:
                net_val = 0.0
            else:
                # Remove any currency symbols or commas
                net_val = str(net_val).replace("£", "").replace(",", "")
                net_val = float(net_val)
                
            vat_val = net_val * vat_ratio
            return f"{vat_val:.2f}"
        except Exception as e:
            print(f"Error computing VAT for row with Number {row.get('Number', 'unknown')}: {e}")
            return "00.00"
    
    report_df["VAT"] = report_df.apply(compute_vat, axis=1)
    
    # Compute Gross as Net + VAT.
    def compute_gross(row):
        try:
            # Handle net value with commas
            net_val = row["Net"]
            if net_val in ["", "00.00"]:
                net_val = 0.0
            else:
                # Remove any currency symbols or commas
                net_val = str(net_val).replace("£", "").replace(",", "")
                net_val = float(net_val)
                
            # Handle VAT value with commas
            vat_val = row["VAT"]
            if vat_val in ["", "00.00"]:
                vat_val = 0.0
            else:
                # Remove any currency symbols or commas
                vat_val = str(vat_val).replace("£", "").replace(",", "")
                vat_val = float(vat_val)
                
            gross_val = net_val + vat_val
            return f"{gross_val:.2f}"
        except Exception as e:
            print(f"Error computing Gross for row with Number {row.get('Number', 'unknown')}: {e}")
            return "00.00"
    
    report_df["Gross"] = report_df.apply(compute_gross, axis=1)
    
    # Save VAT and Gross along with any remaining blank columns.
    # Leave any other columns (if not set) as blank.
    report_df.fillna("", inplace=True)
    
    # Save to Excel in Downloads folder with month_year_Bill_Run format
    downloads_path = os.path.expanduser("~/Downloads")
    prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
    current_year = pd.Timestamp.now().year
    output_path = os.path.join(downloads_path, f"{prev_month}_{current_year}_Bill_Run_{client_name}.xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        report_df.to_excel(writer, index=False, sheet_name="Tysers Report")

    return output_path
