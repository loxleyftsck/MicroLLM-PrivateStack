"""
Tier 1 Optimization Benchmark Script
Tests performance improvements from:
1. Sliding window attention (n_ctx=2048)
2. Memory mapping optimization
3. Prompt prefix caching
"""

import time
import requests
import json
import sys

API_URL = "http://localhost:8000"

# Test queries
TEST_QUERIES = [
    # Repeated queries (test prompt cache)
    "What is MicroLLM?",
    "What is MicroLLM?",  # Should hit prompt cache
    "What is MicroLLM-PrivateStack?",
    "What is MicroLLM-PrivateStack?",  # Should hit prompt cache
    
    # Similar queries (test semantic cache)
    "How does the system work?",
    "How does this system function?",  # Similar, should hit semantic cache
    
    # Long context queries (test sliding window)
    "Explain the architecture of MicroLLM-PrivateStack in detail, including all components.",
    
    # Fresh queries
    "What are the benefits of on-premise AI?",
]

def register_and_login():
    """Register and login to get token"""
    # Register
    register_data = {
        "email": "tier1_benchmark@test.com",
        "password": "Benchmark123!",
        "display_name": "Tier1 Benchmark"
    }
    
    try:
        requests.post(f"{API_URL}/api/auth/register", json=register_data)
    except:
        pass  # May already exist
    
    # Login
    login_resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": register_data["email"],
        "password": register_data["password"]
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.text}")
        sys.exit(1)
    
    return login_resp.json()["token"]

def run_benchmark(token):
    """Run optimization benchmark"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=" * 70)
    print("TIER 1 OPTIMIZATION BENCHMARK")
    print("=" * 70)
    print()
    
    results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] Query: {query[:50]}...")
        
        start = time.time()
        resp = requests.post(f"{API_URL}/api/chat", 
                           headers=headers,
                           json={
                               "message": query,
                               "max_tokens": 100,
                               "temperature": 0.7
                           })
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            response = data.get("response", "")
            
            results.append({
                "query_num": i,
                "query": query[:50],
                "response_length": len(response),
                "time_seconds": round(elapsed, 3),
                "status": "✅ OK"
            })
            
            print(f"  Time: {elapsed:.3f}s | Response: {len(response)} chars")
        else:
            results.append({
                "query_num": i,
                "query": query[:50],
                "time_seconds": round(elapsed, 3),
                "status": f"❌ {resp.status_code}"
            })
            print(f"  ❌ Error: {resp.status_code}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    
    successful = [r for r in results if "OK" in r["status"]]
    if successful:
        times = [r["time_seconds"] for r in successful]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"Total Queries: {len(TEST_QUERIES)}")
        print(f"Successful: {len(successful)}")
        print(f"Average Time: {avg_time:.3f}s")
        print(f"Min Time: {min_time:.3f}s (fastest)")
        print(f"Max Time: {max_time:.3f}s (slowest)")
        print()
        
        # Identify cache hits (very fast responses)
        fast_queries = [r for r in successful if r["time_seconds"] < 0.5]
        if fast_queries:
            print(f"⚡ Fast Responses (<0.5s): {len(fast_queries)} (likely cache hits)")
            for r in fast_queries:
                print(f"   Query {r['query_num']}: {r['time_seconds']:.3f}s")
    
    print("=" * 70)
    
    # Save results
    with open("tier1_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"📊 Results saved to: tier1_benchmark_results.json")

if __name__ == "__main__":
    print("Starting Tier 1 Optimization Benchmark...")
    print()
    
    token = register_and_login()
    print("✅ Authenticated\n")
    
    run_benchmark(token)
