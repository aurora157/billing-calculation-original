import os
import time
import platform
import tempfile
import subprocess
from pathlib import Path
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

# Import report processing modules
from Islestar_report import process_billing_data
from tysers_reports import create_tysers_report
from kf_reports import process_kf_report
from icr_report import process_icr_report
from convatecuk_report import process_and_combine_csv as process_and_combine_csv_uk
from convatecuk_report import generate_billing_report as generate_billing_report_uk
from convatecuk_report import ensure_directories_exist as ensure_directories_exist_uk
from convatec_ipad_report import process_and_combine_csv as process_and_combine_csv_ipad
from convatec_ipad_report import generate_billing_report as generate_billing_report_ipad
from convatec_ipad_report import ensure_directories_exist as ensure_directories_exist_ipad

# List of supported clients
CLIENTS = [
    'Islestarr',
    'ConvaTec UK',
    'ConvaTec iPad',
    'ConvaTec US',
    'Tysers',
    'Knight Frank',
    'Institute of Cancer Research'
]

# Store the path of the most recently generated report
last_report_path = None

def index(request):
    """
    Render the main page with the form for report generation.
    """
    return render(request, 'index.html', {'clients': CLIENTS})

@csrf_exempt
def generate_report(request):
    """
    Handle report generation based on uploaded files and selected client.
    """
    global last_report_path
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    client = request.POST.get('client')
    if not client:
        return JsonResponse({'error': 'Client selection is required'}, status=400)
    
    try:
        # Create temp directory if it doesn't exist
        temp_dir = settings.TEMP_DIR
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = int(time.time())
        
        if client == 'Tysers':
            # Handle Tysers specific case with 3 files
            if ('usage_file' not in request.FILES or 
                'service_file' not in request.FILES or 
                'data_usage_file' not in request.FILES):
                return JsonResponse({'error': 'Please upload all required files'}, status=400)

            usage_file = request.FILES['usage_file']
            service_file = request.FILES['service_file']
            data_usage_file = request.FILES['data_usage_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            usage_path = fs.save(f"usage_{client}.csv", usage_file)
            service_path = fs.save(f"service_breakdown_{client}.csv", service_file)
            data_usage_path = fs.save(f"data_usage_{client}.csv", data_usage_file)
            
            usage_path = os.path.join(temp_dir, usage_path)
            service_path = os.path.join(temp_dir, service_path)
            data_usage_path = os.path.join(temp_dir, data_usage_path)

            # Get pre-tax and total tax amounts
            pre_tax_amount = float(request.POST.get('pre_tax_amount', 0))
            total_tax_amount = float(request.POST.get('total_tax_amount', 0))

            try:
                output_path = create_tysers_report(
                    service_path, 
                    data_usage_path,
                    usage_path, 
                    client,
                    pre_tax_amount=pre_tax_amount,
                    total_tax_amount=total_tax_amount
                )
            finally:
                # Clean up temporary files
                for path in [usage_path, service_path, data_usage_path]:
                    if os.path.exists(path):
                        os.remove(path)

        elif client == 'Knight Frank':
            # Handle Knight Frank case with 2 files
            if 'usage_file' not in request.FILES or 'service_file' not in request.FILES:
                return JsonResponse({'error': 'Please upload both files'}, status=400)

            usage_file = request.FILES['usage_file']
            service_file = request.FILES['service_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            usage_path = fs.save(f"usage_{client}.csv", usage_file)
            service_path = fs.save(f"service_breakdown_{client}.csv", service_file)
            
            usage_path = os.path.join(temp_dir, usage_path)
            service_path = os.path.join(temp_dir, service_path)

            try:
                # Note: The original large usage file has been removed
                # This function will now expect the user to upload the usage file
                output_path = process_kf_report(usage_path, service_path, client)
            finally:
                # Clean up temporary files
                for path in [usage_path, service_path]:
                    if os.path.exists(path):
                        os.remove(path)

        elif client == 'Institute of Cancer Research':
            # Handle ICR case with 2 files
            if 'usage_file' not in request.FILES or 'service_file' not in request.FILES:
                return JsonResponse({'error': 'Please upload both files'}, status=400)

            usage_file = request.FILES['usage_file']
            service_file = request.FILES['service_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            usage_path = fs.save(f"usage_{client}.csv", usage_file)
            service_path = fs.save(f"service_breakdown_{client}.csv", service_file)
            
            usage_path = os.path.join(temp_dir, usage_path)
            service_path = os.path.join(temp_dir, service_path)

            try:
                output_path = process_icr_report(service_path, usage_path, client)
            finally:
                # Clean up temporary files
                for path in [usage_path, service_path]:
                    if os.path.exists(path):
                        os.remove(path)
                        
        elif client == 'ConvaTec UK':
            # Handle ConvaTec UK case with 3 files
            if ('convatec_limited_file' not in request.FILES or 
                'convatec_plc_file' not in request.FILES or 
                'list_of_services_file' not in request.FILES):
                return JsonResponse({'error': 'Please upload all required files'}, status=400)

            convatec_limited_file = request.FILES['convatec_limited_file']
            convatec_plc_file = request.FILES['convatec_plc_file']
            list_of_services_file = request.FILES['list_of_services_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            convatec_limited_path = fs.save(f"convatec_limited_{timestamp}.csv", convatec_limited_file)
            convatec_plc_path = fs.save(f"convatec_plc_{timestamp}.csv", convatec_plc_file)
            list_of_services_path = fs.save(f"list_of_services_{timestamp}.csv", list_of_services_file)
            
            convatec_limited_path = os.path.join(temp_dir, convatec_limited_path)
            convatec_plc_path = os.path.join(temp_dir, convatec_plc_path)
            list_of_services_path = os.path.join(temp_dir, list_of_services_path)
            
            try:
                # Ensure required directories exist
                ensure_directories_exist_uk()
                
                # Create the data/input/convatec directory if it doesn't exist
                os.makedirs(os.path.join("data", "input", "convatec"), exist_ok=True)
                
                # First combine the service breakdown files
                combined_df = process_and_combine_csv_uk(convatec_limited_path, convatec_plc_path)
                
                # Save the list of services file to the expected location
                list_services_dest = os.path.join("data", "input", "convatec", "reports__listOfServices.csv")
                os.makedirs(os.path.dirname(list_services_dest), exist_ok=True)
                with open(list_of_services_path, 'rb') as src_file, open(list_services_dest, 'wb') as dest_file:
                    dest_file.write(src_file.read())
                
                # Generate the billing report
                output_path = generate_billing_report_uk(combined_df)
            finally:
                # Clean up temporary files
                for path in [convatec_limited_path, convatec_plc_path, list_of_services_path]:
                    if os.path.exists(path):
                        os.remove(path)
                        
        elif client == 'ConvaTec iPad':
            # Handle ConvaTec iPad case with 4 files
            if ('ipad_project_file' not in request.FILES or 
                'ipad_europe_file' not in request.FILES or 
                'ipad_europe_services_file' not in request.FILES or
                'ipad_uk_services_file' not in request.FILES):
                return JsonResponse({'error': 'Please upload all required files'}, status=400)

            ipad_project_file = request.FILES['ipad_project_file']
            ipad_europe_file = request.FILES['ipad_europe_file']
            ipad_europe_services_file = request.FILES['ipad_europe_services_file']
            ipad_uk_services_file = request.FILES['ipad_uk_services_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            ipad_project_path = fs.save(f"ipad_project_{timestamp}.csv", ipad_project_file)
            ipad_europe_path = fs.save(f"ipad_europe_{timestamp}.csv", ipad_europe_file)
            ipad_europe_services_path = fs.save(f"ipad_europe_services_{timestamp}.csv", ipad_europe_services_file)
            ipad_uk_services_path = fs.save(f"ipad_uk_services_{timestamp}.csv", ipad_uk_services_file)
            
            ipad_project_path = os.path.join(temp_dir, ipad_project_path)
            ipad_europe_path = os.path.join(temp_dir, ipad_europe_path)
            ipad_europe_services_path = os.path.join(temp_dir, ipad_europe_services_path)
            ipad_uk_services_path = os.path.join(temp_dir, ipad_uk_services_path)
            
            try:
                # Ensure required directories exist
                ensure_directories_exist_ipad()
                
                # Create the data/input/convatec_ipad directory if it doesn't exist
                os.makedirs(os.path.join("data", "input", "convatec_ipad"), exist_ok=True)
                
                # First combine the service breakdown files
                combined_df = process_and_combine_csv_ipad(ipad_project_path, ipad_europe_path)
                
                # Save the list of services files to the expected locations
                ipad_europe_services_dest = os.path.join("data", "input", "convatec_ipad", "ipad_europe_services.csv")
                ipad_uk_services_dest = os.path.join("data", "input", "convatec_ipad", "ipad_uk_services.csv")
                
                os.makedirs(os.path.dirname(ipad_europe_services_dest), exist_ok=True)
                
                with open(ipad_europe_services_path, 'rb') as src_file, open(ipad_europe_services_dest, 'wb') as dest_file:
                    dest_file.write(src_file.read())
                    
                with open(ipad_uk_services_path, 'rb') as src_file, open(ipad_uk_services_dest, 'wb') as dest_file:
                    dest_file.write(src_file.read())
                
                # Generate the billing report
                output_path = generate_billing_report_ipad(combined_df)
            finally:
                # Clean up temporary files
                for path in [ipad_project_path, ipad_europe_path, ipad_europe_services_path, ipad_uk_services_path]:
                    if os.path.exists(path):
                        os.remove(path)

        else:
            # Handle other clients (Isle Star, etc.)
            if 'usage_file' not in request.FILES or 'service_file' not in request.FILES:
                return JsonResponse({'error': 'Please upload both files'}, status=400)

            usage_file = request.FILES['usage_file']
            service_file = request.FILES['service_file']

            # Save files temporarily
            fs = FileSystemStorage(location=temp_dir)
            usage_path = fs.save(f"usage_{client}.csv", usage_file)
            service_path = fs.save(f"service_breakdown_{client}.csv", service_file)
            
            usage_path = os.path.join(temp_dir, usage_path)
            service_path = os.path.join(temp_dir, service_path)

            try:
                output_path = process_billing_data(service_path, usage_path, client)
            finally:
                # Clean up temporary files
                for path in [usage_path, service_path]:
                    if os.path.exists(path):
                        os.remove(path)

        # Store the path for the "Open Report" button
        last_report_path = output_path

        # Get previous month and current year for filename
        prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
        current_year = pd.Timestamp.now().year
        
        # Send file for download
        response = FileResponse(
            open(output_path, 'rb'),
            as_attachment=True,
            filename=f"{prev_month}_{current_year}_Bill_Run_{client}.xlsx"
        )
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def open_report(request):
    """
    Open the most recently generated report using the system's default application.
    """
    global last_report_path
    
    if not last_report_path or not os.path.exists(last_report_path):
        return JsonResponse({'status': 'error', 'message': 'No report found'})
    
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', last_report_path])
        elif platform.system() == 'Windows':
            subprocess.run(['start', last_report_path], shell=True)
        elif platform.system() == 'Linux':
            subprocess.run(['xdg-open', last_report_path])
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
