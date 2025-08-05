"""
✅ Features:
• Health check for CPU, Memory, Disk, Network, Uptime
• Monitors specific Windows Services (e.g., wuauserv, MSSQLSERVER, IISADMIN)
• Sends email alerts if thresholds are exceeded
• Saves output to HTML report
• Customizable alert thresholds

🧰 Step 1: Install Required Packages
Run this in Command Prompt:
pip install psutil pywin32

🛠️ Step 2: Edit Settings
Fill in your own email settings in the script (EMAIL_SETTINGS), and edit which services you want to monitor.

📁 Output:
• HTML Report: C:\Reports\server_health.html
• Email: Sent only if any threshold is exceeded
• Console: “Health check complete” message

🔄 Optional: Schedule It
Use Task Scheduler to run this script every hour:
• Trigger: “Daily” every hour or on boot
• Action: python.exe C:\path\to\windows_server_health_monitor.py
"""

import psutil
import platform
import socket
import smtplib
import win32serviceutil
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== CONFIG ==========
EMAIL_SETTINGS = {
    "from": "your_email@example.com",
    "to": "admin@example.com",
    "subject": "🚨 Server Health Alert",
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "your_email@example.com",
    "password": "your_password"
}

THRESHOLDS = {
    "cpu": 85,
    "memory": 80,
    "disk": 90
}

SERVICES_TO_MONITOR = [
    "wuauserv",       # Windows Update
    "MSSQLSERVER",    # Microsoft SQL Server
    "IISADMIN"        # IIS Admin Service
]

HTML_REPORT_PATH = "C:\\Reports\\server_health.html"
# ============================

def get_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    return datetime.now() - boot_time

def get_cpu():
    return psutil.cpu_percent(interval=1)

def get_memory():
    return psutil.virtual_memory().percent

def get_disk():
    return psutil.disk_usage('C:\\').percent

def get_network():
    net = psutil.net_io_counters()
    return net.bytes_sent, net.bytes_recv

def get_services():
    statuses = []
    for service in SERVICES_TO_MONITOR:
        try:
            status = win32serviceutil.QueryServiceStatus(service)[1]
            statuses.append((service, 'Running' if status == 4 else 'Stopped'))
        except Exception as e:
            statuses.append((service, f"Error: {str(e)}"))
    return statuses

def send_email_alert(body):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = EMAIL_SETTINGS['subject']
    msg['From'] = EMAIL_SETTINGS['from']
    msg['To'] = EMAIL_SETTINGS['to']
    part = MIMEText(body, "html")
    msg.attach(part)

    with smtplib.SMTP(EMAIL_SETTINGS['smtp_server'], EMAIL_SETTINGS['smtp_port']) as server:
        server.starttls()
        server.login(EMAIL_SETTINGS['username'], EMAIL_SETTINGS['password'])
        server.sendmail(EMAIL_SETTINGS['from'], EMAIL_SETTINGS['to'], msg.as_string())

def generate_html(cpu, mem, disk, uptime, services, alert_triggered):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = lambda val, thres: "red" if val >= thres else "green"

    html = f"""
    <html><head><title>Server Health Report</title></head>
    <body>
    <h2>🖥️ Server Health Report - {hostname} ({ip})</h2>
    <p><b>Timestamp:</b> {timestamp}</p>
    <ul>
        <li><b>Uptime:</b> {str(uptime).split('.')[0]}</li>
        <li><b>CPU Usage:</b> <span style="color:{color(cpu, THRESHOLDS['cpu'])}">{cpu}%</span></li>
        <li><b>Memory Usage:</b> <span style="color:{color(mem, THRESHOLDS['memory'])}">{mem}%</span></li>
        <li><b>Disk Usage (C:\):</b> <span style="color:{color(disk, THRESHOLDS['disk'])}">{disk}%</span></li>
    </ul>
    <h3>🔧 Monitored Services:</h3>
    <ul>
    """
    for service, status in services:
        status_color = "green" if status == "Running" else "red"
        html += f"<li>{service}: <span style='color:{status_color}'>{status}</span></li>"
    html += "</ul>"

    if alert_triggered:
        html += "<h3 style='color:red'>⚠️ Alert triggered due to threshold breach</h3>"

    html += "</body></html>"
    return html

def main():
    cpu = get_cpu()
    mem = get_memory()
    disk = get_disk()
    uptime = get_uptime()
    services = get_services()

    alert = cpu > THRESHOLDS['cpu'] or mem > THRESHOLDS['memory'] or disk > THRESHOLDS['disk']
    html = generate_html(cpu, mem, disk, uptime, services, alert)

    with open(HTML_REPORT_PATH, "w") as f:
        f.write(html)

    if alert:
        send_email_alert(html)

    print("✅ Health check complete. HTML report saved.")

if __name__ == "__main__":
    main()
