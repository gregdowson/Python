"""
✅ Quick Service Status Checker
This script uses the pywin32 library (win32serviceutil) to query whether a service is Running, Stopped, or in Error.

📦 Step 1: Install Required Module
Run this in your terminal (Command Prompt or PowerShell):
    pip install pywin32
"""

import win32serviceutil

# List of Windows service names to check
services_to_check = [
    "MSSQLSERVER",         # Default SQL Server service
    "SQLAgent$SQLEXPRESS", # SQL Agent (if named instance)
    "W3SVC",               # IIS Web Server
    "IISADMIN",            # IIS Admin Service
    "wuauserv",            # Windows Update
    "Spooler",             # Print Spooler (example)
]

def check_services(service_list):
    status_report = {}
    for service in service_list:
        try:
            status_code = win32serviceutil.QueryServiceStatus(service)[1]
            if status_code == 4:
                status_report[service] = "Running"
            elif status_code == 1:
                status_report[service] = "Stopped"
            else:
                status_report[service] = f"Other (Status Code {status_code})"
        except Exception as e:
            status_report[service] = f"Error: {str(e)}"
    return status_report

if __name__ == "__main__":
    report = check_services(services_to_check)
    print("🔧 Windows Service Status Report:")
    for svc, status in report.items():
        print(f"• {svc}: {status}")
