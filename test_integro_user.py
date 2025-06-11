import pandas as pd
import os
from tysers_reports import create_tysers_report

# File paths from the user
services_file = os.path.expanduser("~/Downloads/ServicesBreakdown (9).csv")
data_usage_file = os.path.expanduser("~/Downloads/DataUsageSummary.csv")
usage_file = os.path.expanduser("~/Downloads/USAGE-1001917-250300102187.csv")

# Run the report generation
output_path = create_tysers_report(
    services_file, 
    data_usage_file, 
    usage_file, 
    "Integro_Test"
)

# Read the generated report to check values
report_df = pd.read_excel(output_path)

# Find the Integro Shared Data Bundle user
integro_row = report_df[report_df["User"] == "Integro Shared Data Bundle"]

if not integro_row.empty:
    print("\n=== Integro Shared Data Bundle User Details ===")
    
    # Print all columns for this user
    print("\nAll columns:")
    print(integro_row.to_string(index=False))
    
    # Print key financial columns
    print("\nKey financial columns:")
    financial_cols = ["User", "Total Usage", "Recurring", "Net", "VAT", "Gross"]
    print(integro_row[financial_cols].to_string(index=False))
    
    # Print usage breakdown columns
    print("\nUsage breakdown:")
    usage_cols = ["Voice", "International/Roam", "SMS/MMS", "Business Traveller", "Data UK (£)", "Data Roaming (£)"]
    print(integro_row[["User"] + usage_cols].to_string(index=False))
    
    # Verify calculations
    try:
        # Get values as floats for calculation
        total_usage = float(integro_row["Total Usage"].iloc[0].replace("£", "").replace(",", "")) if isinstance(integro_row["Total Usage"].iloc[0], str) else float(integro_row["Total Usage"].iloc[0])
        recurring = float(integro_row["Recurring"].iloc[0].replace("£", "").replace(",", "")) if isinstance(integro_row["Recurring"].iloc[0], str) else float(integro_row["Recurring"].iloc[0])
        net = float(integro_row["Net"].iloc[0].replace("£", "").replace(",", "")) if isinstance(integro_row["Net"].iloc[0], str) else float(integro_row["Net"].iloc[0])
        
        # Calculate expected net
        expected_net = total_usage + recurring
        
        print("\nCalculation verification:")
        print(f"Total Usage: {total_usage}")
        print(f"Recurring: {recurring}")
        print(f"Actual Net: {net}")
        print(f"Expected Net (Total Usage + Recurring): {expected_net}")
        print(f"Net calculation correct: {abs(net - expected_net) < 0.01}")
        
        # Verify Total Usage calculation
        usage_values = []
        for col in usage_cols:
            val = integro_row[col].iloc[0]
            val = float(val.replace("£", "").replace(",", "")) if isinstance(val, str) else float(val)
            usage_values.append(val)
        
        sum_of_usage_cols = sum(usage_values)
        print(f"\nSum of all usage columns: {sum_of_usage_cols}")
        print(f"Total Usage value: {total_usage}")
        print(f"Total Usage calculation correct: {abs(sum_of_usage_cols - total_usage) < 0.01}")
        
    except Exception as e:
        print(f"\nError during calculation verification: {e}")
else:
    print("Integro Shared Data Bundle user not found in the report")

print(f"\nTest completed. Report saved to: {output_path}")
