import requests
import json
import sys
import time

API_URL = "http://localhost:8000"
USER_EMAIL = "rag_tester@test.com"
USER_PASS = "RagPass123!"

def setup_auth():
    print("🔐 Authenticating...")
    # Register
    try:
        requests.post(f"{API_URL}/api/auth/register", json={
            "email": USER_EMAIL,
            "password": USER_PASS,
            "display_name": "RAG Tester"
        })
    except:
        pass
        
    # Login
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASS
    })
    
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        print(f"❌ Login failed: {resp.text}")
        sys.exit(1)

def test_rag():
    token = setup_auth()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Upload Document
    print("\n📄 Uploading document...")
    files = {'file': ('test_doc.txt', open('test_doc.txt', 'rb'), 'text/plain')}
    
    resp = requests.post(
        f"{API_URL}/api/documents/upload",
        headers=headers,
        files=files
    )
    
    if resp.status_code == 201:
        print(f"✅ Upload success: {resp.json()}")
    else:
        print(f"❌ Upload failed: {resp.text}")
        sys.exit(1)
        
    # 2. Query RAG
    print("\n❓ Querying RAG...")
    query = "What is MicroLLM-PrivateStack designed for?"
    
    start = time.time()
    resp = requests.post(
        f"{API_URL}/api/chat",
        headers=headers,
        json={"message": query, "temperature": 0.1}
    )
    duration = time.time() - start
    
    if resp.status_code == 200:
        ans = resp.json()['response']
        print(f"\nResponse ({duration:.2f}s):\n{ans}")
        
        if "2GB RAM" in ans or "security" in ans.lower():
            print("\n✅ Verification PASSED: RAG context used.")
        else:
            print("\n⚠️ Verification WARNING: RAG context might not have been used.")
    else:
        print(f"❌ Query failed: {resp.text}")

if __name__ == "__main__":
    test_rag()
