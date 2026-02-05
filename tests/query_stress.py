import requests
import time
import json
import threading
import statistics
from datetime import datetime

API_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@microllm.local"
ADMIN_PASSWORD = "Admin@123456"

def get_token():
    print(f"Logging in as {ADMIN_EMAIL}...")
    try:
        response = requests.post(f"{API_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        response.raise_for_status()
        data = response.json()
        print("✅ Login successful")
        return data['token']
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_health(count=10):
    print(f"\nTEST: Health Check Spam ({count}x)")
    latencies = []
    for i in range(count):
        start = time.time()
        try:
            r = requests.get(f"{API_URL}/health")
            r.raise_for_status()
            latencies.append((time.time() - start) * 1000)
        except Exception as e:
            print(f"  Error on request {i+1}: {e}")
    
    if latencies:
        avg = statistics.mean(latencies)
        print(f"  Average Health Latency: {avg:.2f}ms")
        print(f"  Success Rate: {len(latencies)}/{count}")
    return latencies

def test_chat_sequential(token, queries):
    print(f"\nTEST: Chat Sequential ({len(queries)} queries)")
    headers = {"Authorization": f"Bearer {token}"}
    latencies = []
    
    for i, q in enumerate(queries):
        print(f"  Query {i+1}: '{q[:30]}...' ", end="", flush=True)
        start = time.time()
        try:
            r = requests.post(f"{API_URL}/api/chat", headers=headers, json={
                "message": q,
                "max_tokens": 128
            })
            r.raise_for_status()
            duration = time.time() - start
            latencies.append(duration)
            print(f"✅ {duration:.2f}s")
        except Exception as e:
            print(f"❌ Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"     Details: {e.response.text}")
    
    if latencies:
        avg = statistics.mean(latencies)
        print(f"  Average Chat Latency: {avg:.2f}s")
    return latencies

def test_chat_concurrent(token, query, count=3):
    print(f"\nTEST: Chat Concurrent ({count} queries)")
    headers = {"Authorization": f"Bearer {token}"}
    latencies = []
    threads = []
    
    def worker(idx):
        start = time.time()
        try:
            r = requests.post(f"{API_URL}/api/chat", headers=headers, json={
                "message": f"{query} (Req {idx})",
                "max_tokens": 64
            })
            r.raise_for_status()
            latencies.append(time.time() - start)
            print(f"    Request {idx} finished")
        except Exception as e:
            print(f"    Request {idx} failed: {e}")

    start_all = time.time()
    for i in range(count):
        t = threading.Thread(target=worker, args=(i+1,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    total_time = time.time() - start_all
    print(f"  Total Wall Time: {total_time:.2f}s")
    if latencies:
        avg = statistics.mean(latencies)
        print(f"  Average Individual Latency: {avg:.2f}s")
    return latencies

def main():
    print("=== MICROLLM ENHANCED STRESS TEST ===")
    print(f"Started at: {datetime.now().isoformat()}")
    
    token = get_token()
    if not token:
        print("Aborting test due to login failure.")
        return

    # 1. Health checks
    test_health(20)

    # 2. Sequential Chat
    queries = [
        "Hello!",
        "Explain what MicroLLM is in two sentences.",
        "What are the benefits of on-premise AI deployment for a financial institution?",
        "Write a short Python script to sort a list of numbers.",
        "APA ITU AI?"
    ]
    test_chat_sequential(token, queries)

    # 3. Concurrent Chat (Stress the batch processor)
    test_chat_concurrent(token, "Explain the importance of cybersecurity.", count=4)

    print("\n" + "=" * 40)
    print("STRESS TEST COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    main()
