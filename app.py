from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
from Islestar_report import process_billing_data
from tysers_reports import create_tysers_report
from kf_reports import process_kf_report
from icr_report import process_icr_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        client = request.form.get('client')

        try:
            if client == 'Tysers':
                # Handle Tysers specific case with 3 files
                if ('usage_file' not in request.files or 
                    'service_file' not in request.files or 
                    'data_usage_file' not in request.files):
                    return {'error': 'Please upload all required files'}, 400

                usage_file = request.files['usage_file']
                service_file = request.files['service_file']
                data_usage_file = request.files['data_usage_file']

                if (usage_file.filename == '' or 
                    service_file.filename == '' or 
                    data_usage_file.filename == ''):
                    return {'error': 'Please upload all required files'}, 400

                # Save files temporarily
                usage_path = os.path.join(app.config['UPLOAD_FOLDER'], f"usage_{client}.csv")
                service_path = os.path.join(app.config['UPLOAD_FOLDER'], f"service_breakdown_{client}.csv")
                data_usage_path = os.path.join(app.config['UPLOAD_FOLDER'], f"data_usage_{client}.csv")

                usage_file.save(usage_path)
                service_file.save(service_path)
                data_usage_file.save(data_usage_path)

                # Get pre-tax and total tax amounts
                pre_tax_amount = float(request.form.get('pre_tax_amount', 0))
                total_tax_amount = float(request.form.get('total_tax_amount', 0))

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
                    os.remove(usage_path)
                    os.remove(service_path)
                    os.remove(data_usage_path)

            elif client == 'Knight Frank':
                # Handle Knight Frank case with 2 files
                if 'usage_file' not in request.files or 'service_file' not in request.files:
                    return {'error': 'Please upload both files'}, 400

                usage_file = request.files['usage_file']
                service_file = request.files['service_file']

                if usage_file.filename == '' or service_file.filename == '':
                    return {'error': 'Please upload both files'}, 400

                # Save files temporarily
                usage_path = os.path.join(app.config['UPLOAD_FOLDER'], f"usage_{client}.csv")
                service_path = os.path.join(app.config['UPLOAD_FOLDER'], f"service_breakdown_{client}.csv")

                usage_file.save(usage_path)
                service_file.save(service_path)

                try:
                    output_path = process_kf_report(usage_path, service_path, client)
                finally:
                    # Clean up temporary files
                    os.remove(usage_path)
                    os.remove(service_path)

            elif client == 'Institute of Cancer Research':
                # Handle ICR case with 2 files
                if 'usage_file' not in request.files or 'service_file' not in request.files:
                    return {'error': 'Please upload both files'}, 400

                usage_file = request.files['usage_file']
                service_file = request.files['service_file']

                if usage_file.filename == '' or service_file.filename == '':
                    return {'error': 'Please upload both files'}, 400

                # Save files temporarily
                usage_path = os.path.join(app.config['UPLOAD_FOLDER'], f"usage_{client}.csv")
                service_path = os.path.join(app.config['UPLOAD_FOLDER'], f"service_breakdown_{client}.csv")

                usage_file.save(usage_path)
                service_file.save(service_path)

                try:
                    output_path = process_icr_report(service_path, usage_path, client)
                finally:
                    # Clean up temporary files
                    os.remove(usage_path)
                    os.remove(service_path)

            else:
                # Handle other clients (Isle Star, etc.)
                if 'usage_file' not in request.files or 'service_file' not in request.files:
                    return {'error': 'Please upload both files'}, 400

                usage_file = request.files['usage_file']
                service_file = request.files['service_file']

                if usage_file.filename == '' or service_file.filename == '':
                    return {'error': 'Please upload both files'}, 400

                # Save files temporarily
                usage_path = os.path.join(app.config['UPLOAD_FOLDER'], f"usage_{client}.csv")
                service_path = os.path.join(app.config['UPLOAD_FOLDER'], f"service_breakdown_{client}.csv")

                usage_file.save(usage_path)
                service_file.save(service_path)

                try:
                    output_path = process_billing_data(service_path, usage_path, client)
                finally:
                    # Clean up temporary files
                    os.remove(usage_path)
                    os.remove(service_path)

            # Store the path for the "Open Report" button
            global last_report_path
            last_report_path = output_path

            # Get previous month and current year for filename
            prev_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')
            current_year = pd.Timestamp.now().year
            
            # Send file for download
            return send_file(
                output_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{prev_month}_{current_year}_Bill_Run_{client}.xlsx"
            )

        except Exception as e:
            return {'error': str(e)}, 400

    return render_template('index.html', clients=CLIENTS)


@app.route('/open_report')
def open_report():
    import subprocess
    import platform

    if last_report_path and os.path.exists(last_report_path):
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', last_report_path])
            elif platform.system() == 'Windows':
                subprocess.run(['start', last_report_path], shell=True)
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', last_report_path])
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    return {'status': 'error', 'message': 'No report found'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True, threaded=True)
