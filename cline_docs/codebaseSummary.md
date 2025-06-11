# Codebase Summary

## Key Components and Their Interactions

### Django Project Structure
- billing_reports/ - Django project settings and configuration
- reports/ - Django app for report generation
- manage.py - Django command-line utility

### Web Application (reports/views.py)
- View functions for the Django application
- Handles file uploads and client selection
- URL patterns for report generation and opening
- Manages temporary file storage
- Implements charge calculations
- Generates and serves Excel reports

### Frontend (templates/index.html)
- Elegant user interface with pink/blue theme
- Client selection dropdown
- Drag and drop file upload areas
- Progress indicators and status messages
- Report download and open functionality
- Form state persistence
- Dynamic button management:
  - Generate Report and Reset Form always visible
  - Open Report appears after generation
  - Open Report removed on form reset
- Asynchronous file processing with CSRF protection

### Data Processing Flow
1. User Interface → File Upload
2. Form State Management
3. Django View Processing
4. Asynchronous Processing
5. CSV Input → DataFrame
6. Data Mapping and Transformation
7. Category-based Charge Calculations
8. Roaming Charge Processing
9. Excel File Generation with Formatting
10. File Download
11. Dynamic UI Updates
12. Open Report Option

### Client-Specific Processing
1. ConvaTec UK
   - Combines two service breakdown files (convatec Limited and convatec plc)
   - Uses List of Services Report for tariff mapping
   - Generates simplified billing report without Email, Employee ID, and User ID columns
   - Handles phone number standardization and user name cleaning
   - Identifies spare lines based on name patterns
   - Automatically calculates Total Spend from Line Rental and Out of Bundle spend
   - Converts data usage from KB and MB to GB for consistent reporting
   - Maps Start/End Date and Cost Centre from List of Services

2. Tysers
   - Processes three input files (Usage, Service Breakdown, Data Usage Summary)
   - Includes pre-tax and total tax amount inputs
   - Generates specialized report format

3. Standard Clients
   - Processes two input files (Usage and Service Breakdown)
   - Applies standard charge calculations and formatting

## Data Flow

1. Input Processing
   - File upload handling
   - Temporary file storage
   - Read service breakdown CSV
   - Read usage CSV
   - Extract required columns
   - Clean and format data
   - Handle data type conversions

2. Data Transformation
   - Map columns to new structure
   - Apply category mapping
   - Process usage data
   - Calculate roaming charges
   - Format monetary values

3. Charge Calculations
   - EU Daily Roaming Charges
   - RoW Daily Roaming Charges
   - Daily Rate Roaming
   - Roaming Calls
   - Roaming Data
   - UK to Abroad
   - Other Charges
   - Total Calculations

4. Output Generation
   - Create Excel file
   - Add period information table
   - Apply monetary formatting
   - Set column widths
   - Save to downloads folder
   - Serve file for download
   - Provide open functionality

## External Dependencies
- Django: Web application framework
  - URL routing
  - View functions
  - Template rendering
  - Static file serving
  - File uploads
  - CSRF protection
- pandas: Data processing and file operations
  - DataFrame manipulations
  - CSV reading
  - Excel writing
  - Data grouping and aggregation
- openpyxl: Excel file handling
  - Formatting
  - Cell styling
  - Number formats
- os: File path operations
  - Path joining
  - Downloads path resolution
  - Temporary file management

## Recent Significant Changes
- Enhanced ConvaTec UK report generation to remove dependency on Master file and Previous Bill file
- Updated ConvaTec UK report to calculate Total Spend from Line Rental and Out of Bundle spend
- Improved data usage conversion from KB and MB to GB for ConvaTec UK reports
- Modified ConvaTec UK report format to remove Email, Employee ID, and User ID columns
- Implemented ConvaTec UK report generation functionality
- Added specialized file upload interface for different clients
- Created logic to combine multiple service breakdown files
- Integrated List of Services Report for tariff mapping
- Implemented proper directory structure creation
- Added error handling for missing files or columns
- Converted Flask application to Django
- Removed large Knight Frank usage file to reduce repository size
- Implemented file upload interface
- Added client selection functionality
- Added period information table
- Implemented complete charge calculation system
- Added EU/RoW roaming differentiation
- Integrated usage data processing
- Added category-based charge mapping
- Implemented monetary value formatting
- Added "No Usage" tracking
- Enhanced Excel output formatting
- Added report download and open features

## User Feedback Integration
- Elegant and intuitive user interface
- Drag and drop file upload support
- Auto-adjusted column widths for better readability
- Clear file output location
- Structured documentation
- Proper monetary value formatting
- Categorized charges for better understanding
- Clear usage status indicators
- Progress indicators during processing
- Success/error message display
- Form state persistence
- Dynamic button visibility
- Loading indicators
- File selection feedback
- Clear reset functionality
