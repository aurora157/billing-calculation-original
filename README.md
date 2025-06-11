# Billing Report Generator

A Django web application that processes Vodafone usage and service data to generate detailed billing reports for multiple clients.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

There are two ways to run the application:

### Option 1: Standard Django Server (Default Port)

1. Start the Django development server:

```bash
python manage.py runserver
```

2. Open your web browser and navigate to:

```bash
http://127.0.0.1:8000
```

### Option 2: Custom Port (Recommended to Avoid Port Conflicts)

1. Use the provided run_app.py script to start the server on a custom port (default: 8090):

```bash
# Run on default port 8090
python run_app.py

# Or specify a custom port
python run_app.py 8095
```

2. Open your web browser and navigate to the URL shown in the terminal (e.g., http://127.0.0.1:8090)

## Web Interface

- Select the client from the dropdown
- Upload the Usage CSV file
- Upload the Service Breakdown CSV file
- For Tysers, also upload the Data Usage Summary CSV file
- Click "Generate Report"

The generated report will be automatically downloaded as an Excel file

You can click "Open Last Report" to view the most recently generated report

## Note

The large Knight Frank usage file has been removed to reduce repository size. When processing Knight Frank reports, you will need to upload both the usage file and service breakdown file through the web interface.
