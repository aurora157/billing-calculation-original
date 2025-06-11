import pandas as pd
import os
from tysers_reports import create_tysers_report

# Create a simple test DataFrame for services
services_data = {
    "Cost Centre": ["Test CC"],
    "Name": ["Integro Shared Data Bundle"],
    "Service": ["12345"],
    "Fixed Charges": ["1,942.00"]  # Note the comma in the value
}
services_df = pd.DataFrame(services_data)
services_csv_path = "test_services.csv"
services_df.to_csv(services_csv_path, index=False)

# Create a simple test DataFrame for data usage summary
data_usage_data = {
    "Service": ["12345"],
    "Usage": ["5.0"]
}
data_usage_df = pd.DataFrame(data_usage_data)
data_usage_csv_path = "test_data_usage.csv"
data_usage_df.to_csv(data_usage_csv_path, index=False)

# Create a simple test DataFrame for usage
usage_data = {
    "Service": ["12345"],
    "Usage Category": ["Data UK"],
    "Cost": ["100.00"]
}
usage_df = pd.DataFrame(usage_data)
usage_csv_path = "test_usage.csv"
usage_df.to_csv(usage_csv_path, index=False)

# Run the report generation
output_path = create_tysers_report(
    services_csv_path, 
    data_usage_csv_path, 
    usage_csv_path, 
    "Test_Client"
)

# Read the generated report to check values
report_df = pd.read_excel(output_path)

# Print all rows in the report for debugging
print("\nAll rows in the report:")
print(report_df.to_string())

# Print the row for Integro Shared Data Bundle
integro_row = report_df[report_df["User"] == "Integro Shared Data Bundle"]
if not integro_row.empty:
    print("\nIntegro Shared Data Bundle row:")
    print(integro_row[["User", "Recurring", "Total Usage", "Net", "VAT", "Gross"]].to_string(index=False))
else:
    print("Integro Shared Data Bundle not found in the report")

# Clean up test files
os.remove(services_csv_path)
os.remove(data_usage_csv_path)
os.remove(usage_csv_path)
print(f"\nTest completed. Report saved to: {output_path}")
