"""
Bulk Document Loader for RAG
Uploads multiple documents from a directory to the RAG knowledge base
"""

import os
import sys
import requests
import time
from pathlib import Path

API_URL = "http://localhost:8000"
DOCS_DIR = "docs"

# Supported file types
SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.md', '.csv']

def setup_auth():
    """Authenticate and get token"""
    print("🔐 Authenticating...")
    
    # Try to register (will fail if user exists, that's OK)
    try:
        requests.post(f"{API_URL}/api/auth/register", json={
            "email": "doc_loader@system.local",
            "password": "DocLoader2026!",
            "display_name": "Document Loader"
        }, timeout=10)
    except:
        pass
    
    # Login
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "doc_loader@system.local",
        "password": "DocLoader2026!"
    }, timeout=10)
    
    if resp.status_code == 200:
        print("✅ Authentication successful")
        return resp.json()['token']
    else:
        print(f"❌ Authentication failed: {resp.text}")
        sys.exit(1)

def upload_document(file_path: Path, token: str) -> bool:
    """Upload a single document"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            resp = requests.post(
                f"{API_URL}/api/documents/upload",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                timeout=60
            )
        
        if resp.status_code == 201:
            data = resp.json()
            print(f"  ✅ {file_path.name}: {data.get('chunks_added', 0)} chunks")
            return True
        else:
            print(f"  ❌ {file_path.name}: {resp.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ❌ {file_path.name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("MicroLLM-PrivateStack - Bulk Document Loader")
    print("=" * 60)
    
    # Get token
    token = setup_auth()
    
    # Find documents
    docs_path = Path(DOCS_DIR)
    if not docs_path.exists():
        print(f"❌ Directory not found: {DOCS_DIR}")
        sys.exit(1)
    
    # Get list of supported files
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(docs_path.glob(f"**/*{ext}"))
    
    if not files:
        print(f"⚠️ No supported documents found in {DOCS_DIR}")
        print(f"   Supported types: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(0)
    
    print(f"\n📁 Found {len(files)} documents to process:\n")
    
    # Upload each document
    success_count = 0
    start_time = time.time()
    
    for file_path in files:
        if upload_document(file_path, token):
            success_count += 1
    
    duration = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total files: {len(files)}")
    print(f"  Successful:  {success_count}")
    print(f"  Failed:      {len(files) - success_count}")
    print(f"  Duration:    {duration:.1f}s")
    print("=" * 60)

if __name__ == "__main__":
    main()
