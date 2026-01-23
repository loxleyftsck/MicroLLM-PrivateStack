"""
MicroLLM-PrivateStack System Monitor
Logs system metrics and health status to CSV for historical analysis.
Run this as a background service.
"""

import time
import requests
import psutil
import csv
import datetime
from pathlib import Path

API_URL = "http://localhost:8000"
LOG_FILE = Path(__file__).parent.parent / "logs" / "system_metrics.csv"

def init_log():
    """Initialize CSV log file"""
    if not LOG_FILE.parent.exists():
        LOG_FILE.parent.mkdir(parents=True)
        
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", 
                "CPU_Percent", 
                "RAM_Percent", 
                "RAM_Used_GB", 
                "Cache_Entries",
                "Cache_Hit_Rate",
                "API_Status",
                "Latency_Check_MS"
            ])

def collect_metrics():
    """Collect metrics from system and API"""
    timestamp = datetime.datetime.now().isoformat()
    
    # System stats
    cpu_pct = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_pct = ram.percent
    ram_used = round(ram.used / (1024**3), 2)
    
    # API stats
    api_status = "DOWN"
    latency = 0
    cache_entries = 0
    cache_hit_rate = 0
    
    try:
        start = time.time()
        resp = requests.get(f"{API_URL}/health", timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        
        if resp.status_code == 200:
            api_status = "UP"
            data = resp.json()
            if "model" in data and "cache" in data["model"]:
                cache_entries = data["model"]["cache"].get("current_entries", 0)
                cache_hit_rate = data["model"]["cache"].get("hit_rate_pct", 0)
    except:
        pass
        
    return [
        timestamp,
        cpu_pct,
        ram_pct,
        ram_used,
        cache_entries,
        cache_hit_rate,
        api_status,
        latency
    ]

def main():
    print(f"Starting System Monitor...")
    print(f"Logging to: {LOG_FILE}")
    
    init_log()
    
    try:
        while True:
            metrics = collect_metrics()
            
            with open(LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(metrics)
            
            # Print status to console
            print(f"[{metrics[0]}] Status: {metrics[6]} | CPU: {metrics[1]}% | RAM: {metrics[3]}GB | Latency: {metrics[7]}ms")
            
            # Log every 60 seconds
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Monitor stopped.")

if __name__ == "__main__":
    main()
