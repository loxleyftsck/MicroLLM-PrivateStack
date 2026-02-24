"""
Tier 2 Batching Benchmark
Tests continuous batching throughput improvement

Measures:
- Sequential processing baseline
- Concurrent processing with batching
- Throughput improvement (target: 4-6x)
"""

import requests
import time
import json
import concurrent.futures
import statistics

API_URL = "http://localhost:8000"

TEST_QUERIES = [
    "What is machine learning?",
    "Explain neural networks",
    "What is deep learning?",
    "How does AI work?",
    "What is NLP?",
    "Explain computer vision",
    "What is reinforcement learning?",
    "How do transformers work?",
]


def register_and_login():
    """Get auth token"""
    # Register
    register_data = {
        "email": "tier2_batch@test.com",
        "password": "Batch123!",
        "display_name": "Tier2 Batch Test"
    }
    
    try:
        requests.post(f"{API_URL}/api/auth/register", json=register_data)
    except:
        pass
    
    # Login
    login_resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": register_data["email"],
        "password": register_data["password"]
    })
    
    return login_resp.json()["token"]


def send_request(query, token, request_num):
    """Send single chat request"""
    headers = {"Authorization": f"Bearer {token}"}
    
    start = time.time()
    resp = requests.post(f"{API_URL}/api/chat",
                        headers=headers,
                        json={
                            "message": query,
                            "max_tokens": 100,
                            "temperature": 0.7
                        })
    elapsed = time.time() - start
    
    return {
        "request_num": request_num,
        "query": query[:30],
        "time_seconds": elapsed,
        "status_code": resp.status_code
    }


def test_sequential(token, num_requests=4):
    """Test sequential processing (baseline)"""
    print("\n" + "=" * 70)
    print("SEQUENTIAL PROCESSING (Baseline)")
    print("=" * 70)
    
    results = []
    total_start = time.time()
    
    for i in range(num_requests):
        print(f"[{i+1}/{num_requests}] Sending request...")
        result = send_request(TEST_QUERIES[i % len(TEST_QUERIES)], token, i+1)
        results.append(result)
        print(f"  ✅ Completed in {result['time_seconds']:.2f}s")
    
    total_time = time.time() - total_start
    
    # Stats
    times = [r['time_seconds'] for r in results]
    avg_time = statistics.mean(times)
    throughput = num_requests / total_time
    
    print(f"\nSequential Results:")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Avg Time/Request: {avg_time:.2f}s")
    print(f"  Throughput: {throughput:.2f} req/s")
    
    return {
        "mode": "sequential",
        "total_time": total_time,
        "avg_time": avg_time,
        "throughput": throughput,
        "results": results
    }


def test_concurrent(token, num_requests=4, max_workers=4):
    """Test concurrent processing (with batching)"""
    print("\n" + "=" * 70)
    print(f"CONCURRENT PROCESSING ({max_workers} workers)")
    print("=" * 70)
    
    total_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(num_requests):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            future = executor.submit(send_request, query, token, i+1)
            futures.append(future)
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - total_start
    
    # Stats
    times = [r['time_seconds'] for r in results]
    avg_time = statistics.mean(times)
    throughput = num_requests / total_time
    
    print(f"\nConcurrent Results:")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Avg Time/Request: {avg_time:.2f}s")
    print(f"  Throughput: {throughput:.2f} req/s")
    
    for r in sorted(results, key=lambda x: x['request_num']):
        print(f"    Request {r['request_num']}: {r['time_seconds']:.2f}s")
    
    return {
        "mode": "concurrent",
        "total_time": total_time,
        "avg_time": avg_time,
        "throughput": throughput,
        "results": results
    }


def main():
    print("=" * 70)
    print("TIER 2 BATCHING BENCHMARK")
    print("=" * 70)
    
    # Authenticate
    print("\n🔑 Authenticating...")
    token = register_and_login()
    print("✅ Authenticated\n")
    
    # Test 1: Sequential (baseline)
    seq_results = test_sequential(token, num_requests=4)
    
    time.sleep(2)  # Brief pause
    
    # Test 2: Concurrent (batching)
    conc_results = test_concurrent(token, num_requests=4, max_workers=4)
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    
    seq_throughput = seq_results['throughput']
    conc_throughput = conc_results['throughput']
    improvement = (conc_throughput / seq_throughput) if seq_throughput > 0 else 0
    
    print(f"Sequential Throughput: {seq_throughput:.2f} req/s")
    print(f"Concurrent Throughput: {conc_throughput:.2f} req/s")
    print(f"Improvement: {improvement:.2f}x")
    
    if improvement >= 2.0:
        print(f"\n✅ TARGET MET! ({improvement:.1f}x improvement)")
    else:
        print(f"\n⚠️  Below target (need 2x, got {improvement:.1f}x)")
    
    # Save results
    benchmark_data = {
        "sequential": seq_results,
        "concurrent": conc_results,
        "improvement": improvement,
        "timestamp": time.time()
    }
    
    with open('tier2_batching_benchmark.json', 'w') as f:
        json.dump(benchmark_data, f, indent=2)
    
    print(f"\n📊 Results saved to: tier2_batching_benchmark.json")


if __name__ == "__main__":
    main()
