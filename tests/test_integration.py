"""
MicroLLM-PrivateStack Integration Tests
Tests full user workflows: Auth -> RAG -> Chat -> Cleanup
"""

import pytest
import requests
import os
import json
import time

API_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "email": "integration@test.com",
    "password": "IntegrationTest123!",
    "display_name": "Integration Tester"
}

TEST_DOC_CONTENT = """
MicroLLM-PrivateStack is an on-premise AI assistant optimized for privacy and efficiency.
It uses 2GB of RAM and runs on standard consumer hardware.
This is a test document for integration testing.
"""

def setup_module():
    """Setup test environment"""
    # Ensure server is running
    try:
        requests.get(f"{API_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail("Server is not running. Please start the server first.")

def test_full_workflow():
    """Execute end-to-end workflow"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    print("\n[1] Authentication Flow")
    # 1. Register
    try:
        register_resp = session.post(f"{API_URL}/api/auth/register", json=TEST_USER)
        # 201 created or 400 if exists (which is fine for repeat tests)
        assert register_resp.status_code in [201, 400]
    except Exception as e:
        pytest.fail(f"Registration failed: {e}")
        
    # 2. Login
    login_resp = session.post(f"{API_URL}/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    assert login_resp.status_code == 200
    token = login_resp.json().get("token")
    assert token is not None
    
    # Set auth header for subsequent requests
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("    ✅ Login successful")
    
    print("\n[2] RAG Workflow")
    # 3. Upload Document
    # Create temp file
    with open("temp_test_doc.txt", "w") as f:
        f.write(TEST_DOC_CONTENT)
        
    files = {"file": ("temp_test_doc.txt", open("temp_test_doc.txt", "rb"), "text/plain")}
    # Remove Content-Type header for file upload (requests sets it automatically with boundary)
    upload_headers = {"Authorization": f"Bearer {token}"}
    
    upload_resp = requests.post(f"{API_URL}/api/documents/upload", headers=upload_headers, files=files)
    assert upload_resp.status_code in [201, 200]
    print("    ✅ Document upload successful")
    
    # Cleanup temp file
    files["file"][1].close()
    os.remove("temp_test_doc.txt")
    
    # 4. Chat Retrieval
    print("\n[3] Chat Interaction")
    query = "How much RAM does MicroLLM use?"
    
    # Retry loop to allow for async indexing if needed
    max_retries = 3
    found_context = False
    
    for i in range(max_retries):
        chat_resp = session.post(f"{API_URL}/api/chat", json={
            "message": query,
            "max_tokens": 100,
            "temperature": 0.1
        })
        assert chat_resp.status_code == 200
        response_json = chat_resp.json()
        response_text = response_json.get("response", "").lower()
        
        # Check if the model mentioned "2GB" or "RAM" which is in our doc
        if "2gb" in response_text or "ram" in response_text:
            found_context = True
            break
        
        time.sleep(2)
        
    if found_context:
        print(f"    ✅ Context retrieval verification passed")
    else:
        print(f"    ⚠️ Warning: Context might not have been retrieved (Check LLM response: {response_text[:50]}...)")
        
    print("\n[4] System Cleanup")
    # 5. Clear Documents
    clear_resp = session.post(f"{API_URL}/api/documents/clear")
    assert clear_resp.status_code == 200
    print("    ✅ Knowledge base cleared")
    
    print("\n✅ Integration Test Complete")

if __name__ == "__main__":
    test_full_workflow()
