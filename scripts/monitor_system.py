"""
MicroLLM-PrivateStack System Monitor
Logs system metrics, API health, and TTFT performance to CSV.
Run as background service: python scripts/monitor_system.py

Enhanced (Phase 6): tracks TTFT p50/p95/p99 from /api/perf/ttft
"""

import time
import requests
import psutil
import csv
import datetime
import os
from pathlib import Path

API_URL = os.getenv("MICROLLM_API_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("MONITOR_AUTH_TOKEN", "")  # Set via env var — never hardcode
INTERVAL_SEC = int(os.getenv("MONITOR_INTERVAL_SEC", "60"))

LOG_FILE = Path(__file__).parent.parent / "logs" / "system_metrics.csv"

# CSV columns
CSV_HEADERS = [
    "Timestamp",
    "CPU_Percent",
    "RAM_Percent",
    "RAM_Used_GB",
    "Cache_Entries",
    "Cache_Hit_Rate",
    "API_Status",
    "Health_Latency_MS",
    # Phase 6: TTFT columns
    "TTFT_Samples",
    "TTFT_P50_MS",
    "TTFT_P95_MS",
    "TTFT_P99_MS",
    "TTFT_Target_Met_Pct",
    "TTFT_Warmed_Up",
]


def _auth_headers() -> dict:
    """Return Authorization header if token is set."""
    if AUTH_TOKEN:
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    return {}


def init_log():
    """Initialize CSV log file with headers (idempotent)."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADERS)


def collect_metrics() -> list:
    """Collect system + API + TTFT metrics into a flat row."""
    ts = datetime.datetime.now().isoformat()

    # ── System ──────────────────────────────
    cpu_pct = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_pct = round(ram.percent, 1)
    ram_used = round(ram.used / (1024**3), 2)

    # ── API Health ──────────────────────────
    api_status = "DOWN"
    latency_ms = 0
    cache_entries = 0
    cache_hit_rate = 0

    try:
        t0 = time.perf_counter()
        resp = requests.get(f"{API_URL}/health", timeout=5)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        if resp.status_code == 200:
            api_status = "UP"
            data = resp.json()
            model = data.get("model", {})
            cache = model.get("cache", {})
            cache_entries = cache.get("current_entries", 0)
            cache_hit_rate = cache.get("hit_rate_pct", 0)
    except Exception:
        pass

    # ── TTFT Performance (Phase 6) ──────────
    ttft_samples = 0
    ttft_p50 = ""
    ttft_p95 = ""
    ttft_p99 = ""
    ttft_target_pct = ""
    ttft_warmed_up = ""

    if api_status == "UP":
        try:
            r = requests.get(
                f"{API_URL}/api/perf/ttft",
                headers=_auth_headers(),
                timeout=5
            )
            if r.status_code == 200:
                d = r.json()
                ttft_samples = d.get("samples", 0)
                ttft_p50 = d.get("p50_ms", "")
                ttft_p95 = d.get("p95_ms", "")
                ttft_p99 = d.get("p99_ms", "")
                ttft_target_pct = d.get("target_met_pct", "")
                ttft_warmed_up = d.get("warmed_up", "")
        except Exception:
            pass

    return [
        ts,
        cpu_pct,
        ram_pct,
        ram_used,
        cache_entries,
        cache_hit_rate,
        api_status,
        latency_ms,
        ttft_samples,
        ttft_p50,
        ttft_p95,
        ttft_p99,
        ttft_target_pct,
        ttft_warmed_up,
    ]


def main():
    print(f"Starting MicroLLM System Monitor")
    print(f"  API  : {API_URL}")
    print(f"  Log  : {LOG_FILE}")
    print(f"  Interval: {INTERVAL_SEC}s")
    if not AUTH_TOKEN:
        print("  [WARN] MONITOR_AUTH_TOKEN not set — TTFT endpoint will return 401")

    init_log()

    while True:
        try:
            row = collect_metrics()

            with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(row)

            ttft_info = (
                f"p50={row[9]}ms p95={row[10]}ms ({row[12]}% <50ms)"
                if row[8] else "no TTFT data"
            )
            print(
                f"[{row[0]}] {row[6]} | CPU:{row[1]}% RAM:{row[3]}GB "
                f"| Health:{row[7]}ms | TTFT:{ttft_info}"
            )

        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break
        except Exception as e:
            print(f"[ERROR] Metrics collection failed: {e}")

        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
