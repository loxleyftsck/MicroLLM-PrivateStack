"""
MicroLLM-PrivateStack Tuning Benchmark
Compares 5 different parameter configurations
"""

import requests
import time
import statistics
import json
import sys

API_URL = "http://localhost:8000"

# Test queries
TEST_QUERIES = [
    "What is artificial intelligence?",
    "Explain machine learning in simple terms",
    "What are the benefits of AI?",
]

# 5 Tuning Configurations to Compare
CONFIGS = [
    {
        "name": "Baseline (Current)",
        "max_tokens": 256,
        "temperature": 0.7,
    },
    {
        "name": "Conservative (Low Temp)",
        "max_tokens": 128,
        "temperature": 0.3,
    },
    {
        "name": "Creative (High Temp)",
        "max_tokens": 256,
        "temperature": 0.9,
    },
    {
        "name": "Speed Optimized",
        "max_tokens": 64,
        "temperature": 0.5,
    },
    {
        "name": "Quality Focus",
        "max_tokens": 256,
        "temperature": 0.1,
    },
]

def setup_auth():
    """Get auth token"""
    try:
        requests.post(f"{API_URL}/api/auth/register", json={
            "email": "tuning@test.com",
            "password": "TuningTest123!",
            "display_name": "Tuning Tester"
        }, timeout=10)
    except:
        pass
    
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "tuning@test.com",
        "password": "TuningTest123!"
    }, timeout=10)
    
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        print(f"Auth failed: {resp.text}")
        sys.exit(1)

def run_benchmark(token: str, config: dict) -> dict:
    """Run benchmark with specific config"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    results = {
        "config": config["name"],
        "times": [],
        "token_counts": [],
        "success_count": 0,
        "error_count": 0,
        "responses": []
    }
    
    for query in TEST_QUERIES:
        start = time.time()
        try:
            resp = requests.post(
                f"{API_URL}/api/chat",
                headers=headers,
                json={
                    "message": query,
                    "max_tokens": config["max_tokens"],
                    "temperature": config["temperature"]
                },
                timeout=60
            )
            duration = time.time() - start
            
            if resp.status_code == 200:
                data = resp.json()
                results["times"].append(duration)
                results["token_counts"].append(data.get("tokens_generated", 0))
                results["success_count"] += 1
                results["responses"].append(data.get("response", "")[:100])
            else:
                results["error_count"] += 1
        except Exception as e:
            results["error_count"] += 1
            
    return results

def calculate_metrics(results: dict) -> dict:
    """Calculate performance metrics"""
    if not results["times"]:
        return {
            "avg_time": 0,
            "min_time": 0,
            "max_time": 0,
            "avg_tokens": 0,
            "success_rate": 0
        }
    
    return {
        "avg_time": round(statistics.mean(results["times"]), 2),
        "min_time": round(min(results["times"]), 2),
        "max_time": round(max(results["times"]), 2),
        "avg_tokens": round(statistics.mean(results["token_counts"]), 1) if results["token_counts"] else 0,
        "success_rate": round(results["success_count"] / len(TEST_QUERIES) * 100, 1)
    }

def main():
    print("=" * 70)
    print("MicroLLM-PrivateStack TUNING BENCHMARK")
    print("=" * 70)
    print(f"Testing {len(CONFIGS)} configurations with {len(TEST_QUERIES)} queries each\n")
    
    # Auth
    print("Authenticating...")
    token = setup_auth()
    print("OK\n")
    
    all_results = []
    
    # Run benchmarks
    for i, config in enumerate(CONFIGS, 1):
        print(f"[{i}/{len(CONFIGS)}] Testing: {config['name']}")
        print(f"    max_tokens={config['max_tokens']}, temperature={config['temperature']}")
        
        results = run_benchmark(token, config)
        metrics = calculate_metrics(results)
        
        print(f"    Avg Time: {metrics['avg_time']}s | Tokens: {metrics['avg_tokens']} | Success: {metrics['success_rate']}%")
        print()
        
        all_results.append({
            "config": config,
            "results": results,
            "metrics": metrics
        })
    
    # Generate Report
    print("\n" + "=" * 70)
    print("TUNING COMPARISON REPORT")
    print("=" * 70)
    
    print("\n{:<25} {:>10} {:>10} {:>10} {:>10}".format(
        "Configuration", "Avg Time", "Tokens", "Success", "Score"
    ))
    print("-" * 70)
    
    for r in all_results:
        m = r["metrics"]
        # Calculate composite score (lower time + higher success = better)
        # Score = Success_Rate / Avg_Time (higher is better)
        score = round(m["success_rate"] / max(m["avg_time"], 0.1), 1)
        
        print("{:<25} {:>10}s {:>10} {:>9}% {:>10}".format(
            r["config"]["name"],
            m["avg_time"],
            m["avg_tokens"],
            m["success_rate"],
            score
        ))
    
    # Find best config
    best = max(all_results, key=lambda x: x["metrics"]["success_rate"] / max(x["metrics"]["avg_time"], 0.1))
    
    print("\n" + "=" * 70)
    print(f"RECOMMENDED CONFIG: {best['config']['name']}")
    print(f"  max_tokens: {best['config']['max_tokens']}")
    print(f"  temperature: {best['config']['temperature']}")
    print("=" * 70)
    
    # Sample response quality
    print("\n📝 SAMPLE RESPONSES (first query):")
    for r in all_results:
        if r["results"]["responses"]:
            print(f"\n[{r['config']['name']}]")
            print(f"  {r['results']['responses'][0]}...")

if __name__ == "__main__":
    main()
