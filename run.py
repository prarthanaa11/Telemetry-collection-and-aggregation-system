import subprocess
import time
import socket
import requests
import webbrowser
import sys
import atexit
import os

GRAFANA_URL = "http://localhost:3000"
INFLUXDB_URL = "http://localhost:8086"
KAFKA_PORT = 9092

processes = []

def cleanup():
    print("\n[Shutting down] Stopping background processes...")
    for p in processes:
        p.terminate()
        p.wait()
    print("[Shutting down] Stopping Docker containers...")
    subprocess.run(["docker-compose", "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Cleanup complete.")

atexit.register(cleanup)

def wait_for_port(port, host='localhost', timeout=120):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(2)
    return False

def wait_for_http(url, timeout=120):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except requests.exceptions.RequestException:
            time.sleep(2)
    return False

def setup_grafana():
    print("[Setup] Configuring Grafana Data Source and Dashboard...")
    auth = ('admin', 'admin')
    
    # 1. Create InfluxDB Data Source
    ds_payload = {
        "name": "InfluxDB",
        "type": "influxdb",
        "url": "http://influxdb:8086",
        "access": "proxy",
        "jsonData": {
            "version": "Flux",
            "organization": "my-org",
            "defaultBucket": "telemetry_bucket"
        },
        "secureJsonData": {
            "token": "my-token"
        }
    }
    
    try:
        r = requests.post(f"{GRAFANA_URL}/api/datasources", json=ds_payload, auth=auth)
        if r.status_code in (200, 201, 409):
            print("[Setup] InfluxDB Data Source added successfully.")
        else:
            print(f"[Setup] Failed to add data source: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[Setup] Error adding data source: {e}")

    # 2. Create Dashboard
    dashboard_payload = {
        "dashboard": {
            "id": None,
            "uid": "telemetry_auto_1",
            "title": "Automated Telemetry Dashboard",
            "tags": [ "telemetry" ],
            "timezone": "browser",
            "panels": [
                {
                    "title": "CPU Usage (%)",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 9},
                    "datasource": {"type": "influxdb", "uid": "InfluxDB"},
                    "targets": [
                        {
                            "query": 'from(bucket: "telemetry_bucket") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "system_telemetry") |> filter(fn: (r) => r["_field"] == "cpu_usage_percent" or r["_field"] == "cpu_rolling_avg") |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false) |> yield(name: "mean")',
                            "refId": "A"
                        }
                    ]
                },
                {
                    "title": "Memory Usage (%)",
                    "type": "timeseries",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 9},
                    "datasource": {"type": "influxdb", "uid": "InfluxDB"},
                    "targets": [
                        {
                            "query": 'from(bucket: "telemetry_bucket") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "system_telemetry") |> filter(fn: (r) => r["_field"] == "memory_usage_percent") |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false) |> yield(name: "mean")',
                            "refId": "A"
                        }
                    ]
                }
            ],
            "schemaVersion": 36,
            "version": 1
        },
        "folderId": 0,
        "overwrite": True
    }
    
    try:
        r = requests.post(f"{GRAFANA_URL}/api/dashboards/db", json=dashboard_payload, auth=auth)
        if r.status_code in (200, 201):
            url = r.json().get('url')
            print(f"[Setup] Dashboard created successfully.")
            return url
        else:
            print(f"[Setup] Failed to create dashboard: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[Setup] Error creating dashboard: {e}")
    
    return "/"

def main():
    print("==================================================")
    print("  🚀 Starting Telemetry Automation System")
    print("==================================================")
    
    print("\n[Step 1] Starting Docker containers (Kafka, InfluxDB, Grafana)...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
    except subprocess.CalledProcessError:
        print("\n==================================================")
        print(" ❌ ERROR: DOCKER IS NOT RUNNING")
        print("==================================================")
        print(" Docker Desktop needs to be running before this script can start the services.")
        print(" -> Please open the 'Docker Desktop' application on your computer, wait for it to fully load, and try running this script again.")
        print("==================================================\n")
        sys.exit(1)
    except FileNotFoundError:
        print("\n==================================================")
        print(" ❌ ERROR: DOCKER IS NOT INSTALLED")
        print("==================================================")
        print(" -> Please ensure that Docker Desktop is installed on your computer.")
        print("==================================================\n")
        sys.exit(1)
    
    print("\n[Step 2] Waiting for services to become ready...")
    print(" - Waiting for Kafka (9092)...", end="", flush=True)
    if wait_for_port(KAFKA_PORT):
        print(" OK")
    else:
        print(" Failed! Is Docker running?")
        sys.exit(1)
        
    print(" - Waiting for InfluxDB (8086)...", end="", flush=True)
    if wait_for_http(f"{INFLUXDB_URL}/health"):
         print(" OK")
    else:
         print(" Failed!")
         sys.exit(1)
         
    print(" - Waiting for Grafana (3000)...", end="", flush=True)
    if wait_for_http(f"{GRAFANA_URL}/api/health"):
         print(" OK")
    else:
         print(" Failed!")
         sys.exit(1)

    time.sleep(3) # Small buffer for Grafana APIs to be ready
    
    dashboard_url = setup_grafana()
    
    print("\n[Step 4] Starting Consumer (consumer.py) in background...")
    proc_consumer = subprocess.Popen([sys.executable, "consumer.py"])
    processes.append(proc_consumer)
    
    print("\n[Step 5] Starting Agent (agent.py) in background...")
    proc_agent = subprocess.Popen([sys.executable, "agent.py"])
    processes.append(proc_agent)
    
    full_dashboard_url = f"{GRAFANA_URL}{dashboard_url}"
    print(f"\n[Step 6] Opening Grafana automatically: {full_dashboard_url}")
    webbrowser.open(full_dashboard_url)
    
    print("\n==================================================")
    print("  ✅ All systems are GO! Telemetry is streaming.")
    print("  Grafana Login: admin / admin")
    print("  Press Ctrl+C to safely stop Docker and Python scripts.")
    print("==================================================\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass # atexit hook cleans up

if __name__ == "__main__":
    main()
