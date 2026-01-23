#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Test Suite for MicroLLM-PrivateStack
Tests API performance with and without caching
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:8000"

# Test queries - mix of common and unique
TEST_QUERIES = [
    "What is artificial intelligence?",
    "Explain machine learning in simple terms",
    "What are the benefits of AI?",
    "How does deep learning work?",
    "What is natural language processing?",
    # Repeat some for cache testing
    "What is artificial intelligence?",
    "Explain machine learning in simple terms",
    "What are the benefits of AI?",
]

# Global headers
HEADERS = {"Content-Type": "application/json"}

def setup_auth():
    """Register and login a test user to get JWT token"""
    print("\n🔐 Setting up authentication...")
    
    # 1. Register
    reg_data = {
        "email": "perf@test.com",
        "password": "StrongPass123!",
        "display_name": "Performance Tester"
    }
    
    try:
        requests.post(f"{API_URL}/api/auth/register", json=reg_data)
        # Ignore error if already exists
    except Exception:
        pass
        
    # 2. Login
    login_data = {
        "email": "perf@test.com",
        "password": "StrongPass123!"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Login successful. Token acquired.")
            HEADERS["Authorization"] = f"Bearer {token}"
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False

def test_single_request(query, test_id):
    """Test a single API request"""
    start = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": query, "max_tokens": 50},
            headers=HEADERS,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            return {
                'test_id': test_id,
                'query': query[:50],
                'status': 'success',
                'response_time': elapsed,
                'response_length': len(data.get('response', '')),
                'cached': 'Cache HIT' in str(data)  # Heuristic
            }
        else:
            return {
                'test_id': test_id,
                'query': query[:50],
                'status': 'error',
                'response_time': elapsed,
                'error': f"Status {response.status_code}"
            }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'test_id': test_id,
            'query': query[:50],
            'status': 'exception',
            'response_time': elapsed,
            'error': str(e)
        }

def test_sequential():
    """Test sequential requests"""
    print("\n" + "="*70)
    print("SEQUENTIAL REQUEST TEST")
    print("="*70)
    
    results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n[{i}/{len(TEST_QUERIES)}] Testing: {query[:50]}...")
        result = test_single_request(query, i)
        results.append(result)
        
        print(f"  Status: {result['status']}")
        print(f"  Time: {result['response_time']:.2f}s")
        if result.get('cached'):
            print(f"  🎯 Cache HIT!")
        if result['status'] != 'success':
            print(f"  Error: {result.get('error')}")
    
    return results

def test_concurrent(num_workers=3):
    """Test concurrent requests"""
    print("\n" + "="*70)
    print(f"CONCURRENT REQUEST TEST ({num_workers} workers)")
    print("="*70)
    
    results = []
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(test_single_request, query, i): (i, query)
            for i, query in enumerate(TEST_QUERIES, 1)
        }
        
        for future in as_completed(futures):
            test_id, query = futures[future]
            result = future.result()
            results.append(result)
            
            print(f"\n[{test_id}] Completed: {query[:50]}")
            print(f"  Time: {result['response_time']:.2f}s")
    
    return results

def analyze_results(results, test_name="Test"):
    """Analyze and print test results"""
    print("\n" + "="*70)
    print(f"{test_name} - RESULTS ANALYSIS")
    print("="*70)
    
    success = [r for r in results if r['status'] == 'success']
    errors = [r for r in results if r['status'] != 'success']
    
    if not success:
        print("❌ No successful requests!")
        if errors:
            print(f"Sample error: {errors[0].get('error')}")
        return
    
    times = [r['response_time'] for r in success]
    
    print(f"\n📊 Success Rate: {len(success)}/{len(results)} ({len(success)/len(results)*100:.1f}%)")
    print(f"\n⏱️  Response Times:")
    print(f"  Min:    {min(times):.2f}s")
    print(f"  Max:    {max(times):.2f}s")
    print(f"  Mean:   {statistics.mean(times):.2f}s")
    print(f"  Median: {statistics.median(times):.2f}s")
    
    if len(times) > 1:
        print(f"  StdDev: {statistics.stdev(times):.2f}s")
    
    # Cache analysis (if detectable)
    cached = sum(1 for r in success if r.get('cached', False))
    if cached > 0:
        print(f"\n🎯 Cache Hits: {cached}/{len(success)} ({cached/len(success)*100:.1f}%)")
        
        cached_times = [r['response_time'] for r in success if r.get('cached', False)]
        uncached_times = [r['response_time'] for r in success if not r.get('cached', False)]
        
        if cached_times and uncached_times:
            print(f"  Cached avg:   {statistics.mean(cached_times):.2f}s")
            print(f"  Uncached avg: {statistics.mean(uncached_times):.2f}s")
            speedup = statistics.mean(uncached_times) / statistics.mean(cached_times)
            print(f"  Speedup:      {speedup:.1f}x faster!")
    
    if errors:
        print(f"\n❌ Errors: {len(errors)}")
        for err in errors[:3]:  # Show first 3 errors
            print(f"  - {err['query']}: {err.get('error', 'Unknown')}")

def main():
    """Run all performance tests"""
    print("\n" + "="*70)
    print("🚀 MicroLLM-PrivateStack Performance Test Suite")
    print("="*70)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"\n✅ Server is running: {response.json()}")
    except Exception as e:
        print(f"\n❌ Server not accessible: {e}")
        print("\nPlease start the server first:")
        print("  python backend/api_gateway.py")
        return
        
    # Setup Auth
    if not setup_auth():
        print("⚠️ Running without auth (requests may fail if auth is required)")
    
    # Test 1: Sequential requests
    seq_results = test_sequential()
    analyze_results(seq_results, "SEQUENTIAL TEST")
    
    # Test 2: Concurrent requests (Stress Test)
    conc_results = test_concurrent(num_workers=4)
    analyze_results(conc_results, "CONCURRENT STRESS TEST")
    
    # 3. Accuracy/Quality Check
    print("\n" + "="*70)
    print("🧠 ACCURACY & QUALITY SAMPLE")
    print("="*70)
    success_results = [r for r in seq_results if r['status'] == 'success']
    if success_results:
        # Get Sample Response
        sample = success_results[0]
        # We need to fetch the actual text content which wasn't stored in the result dict previously
        # Rerun one query to show full output
        print(f"Query: {sample['query']}")
        try:
            resp = requests.post(
                f"{API_URL}/api/chat",
                json={"message": sample['query'], "max_tokens": 100},
                headers=HEADERS,
                timeout=30
            ) 
            data = resp.json()
            print(f"Response:\n{data.get('response', 'No response')[:500]}...")
        except Exception as e:
            print(f"Failed to fetch sample: {e}")
    
    print("\n" + "="*70)
    print("✅ All tests completed!")
    print("="*70)
    
    # Summary
    print("\n📈 PERFORMANCE SUMMARY:")
    print(f"  Total requests: {len(seq_results)}")
    print(f"  Test duration: ~{sum(r['response_time'] for r in seq_results):.1f}s")
    print("\n💡 TIP: Run tests multiple times to see cache improvements!")

if __name__ == "__main__":
    main()
