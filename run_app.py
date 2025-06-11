#!/usr/bin/env python
"""
Script to run the Django application on a custom port.
This helps avoid port conflicts with other applications.
"""
import os
import sys
import subprocess

def run_django_server(port=8090):
    """
    Run the Django development server on the specified port.
    
    Args:
        port (int): The port number to use for the server
    """
    print(f"Starting Django server on port {port}...")
    print("The application is configured to accept both service breakdown and usage files.")
    print("Access the application at: http://127.0.0.1:{}/".format(port))
    print("Press Ctrl+C to stop the server.")
    
    # Run the Django server on the specified port
    subprocess.run([sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"])

if __name__ == "__main__":
    # Check if a port was provided as a command-line argument
    port = 8090
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 8090.")
    
    run_django_server(port)
