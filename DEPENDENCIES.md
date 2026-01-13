# MicroLLM-PrivateStack - Dependency Analysis

## 📊 Summary

| Category | Full | Minimal | Notes |
|----------|------|---------|-------|
| **Total packages** | 45+ | 20 | Minimal for 2GB RAM |
| **Estimated size** | ~2.5GB | ~1.8GB | With models excluded |
| **Install time** | 10-15 min | 5-8 min | On decent connection |

---

## ✅ Yang Sudah Ada (Original)

```txt
✓ flask, flask-cors, flask-jwt-extended  # Web framework
✓ llama-cpp-python                       # LLM inference
✓ sentence-transformers, numpy, faiss    # RAG
✓ bcrypt, cryptography                   # Security
✓ prometheus-client                      # Monitoring
✓ pytest, black, flake8, mypy            # Development
```

**Status:** Basic tapi kurang untuk production-ready

---

## 🆕 Yang Ditambahkan (Enhanced)

### 1. Document Processing
```txt
+ pypdf==3.17.4                # PDF parsing
+ python-docx==1.1.0           # Word documents
+ openpyxl==3.1.2              # Excel files
+ pillow==10.1.0               # Image processing
```

**Why:** Untuk RAG yang bisa process berbagai format dokumen

### 2. Database & ORM
```txt
+ sqlalchemy==2.0.25           # Database ORM
+ alembic==1.13.1              # Migrations
```

**Why:** User management, audit logs, vector store persistence

### 3. Production Server
```txt
+ gunicorn==21.2.0             # WSGI server
+ gevent==23.9.1               # Async workers
```

**Why:** Flask dev server NOT for production. Gunicorn = industry standard

### 4. Advanced Features
```txt
+ langchain==0.1.0             # RAG orchestration
+ chromadb==0.4.22             # Vector DB (alternative)
+ flask-limiter==3.5.0         # Rate limiting
+ loguru==0.7.2                # Better logging
```

**Why:** Production-ready features untuk enterprise

### 5. Async Support
```txt
+ httpx==0.25.2                # Async HTTP
+ aiofiles==23.2.1             # Async file I/O
+ pytest-asyncio==0.23.2       # Async testing
```

**Why:** Better performance untuk concurrent requests

### 6. Data Processing
```txt
+ pandas==2.1.4                # Spreadsheet analysis
+ pydantic-settings==2.1.0     # Config validation
+ marshmallow==3.20.1          # Serialization
```

**Why:** Data interpretation use case

---

## 🎯 Recommendations

### For Development (Your Machine)
```bash
# Full install
pip install -r requirements.txt
```

### For Production 2GB Server
```bash
# Minimal install
pip install -r requirements-minimal.txt
```

### For GPU Acceleration
```bash
# Install llama-cpp with CUDA
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

# Or with Metal (M1/M2 Mac)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

---

## 🔧 Installation Strategy

### Step 1: Core Dependencies
```bash
pip install flask flask-cors flask-jwt-extended python-dotenv
pip install gunicorn sqlalchemy bcrypt
```

### Step 2: LLM Engine (Takes time!)
```bash
# This can take 10-15 minutes due to C++ compilation
pip install llama-cpp-python==0.2.36
```

### Step 3: RAG Components
```bash
pip install sentence-transformers chromadb pypdf python-docx
```

### Step 4: Optional Enhancements
```bash
pip install langchain loguru flask-limiter pandas
```

---

## ⚠️ Potential Issues & Solutions

### Issue 1: llama-cpp-python compilation fails
**Solution:**
```bash
# Install build tools first
# Ubuntu/Debian:
sudo apt-get install build-essential cmake

# macOS:
brew install cmake

# Windows:
# Install Visual Studio Build Tools
```

### Issue 2: faiss-cpu install fails
**Solution:**
```bash
# Use chromadb instead (lighter)
pip install chromadb==0.4.22

# Or install faiss from conda
conda install -c conda-forge faiss-cpu
```

### Issue 3: Out of memory during install
**Solution:**
```bash
# Install one by one with --no-cache-dir
pip install --no-cache-dir llama-cpp-python
pip install --no-cache-dir sentence-transformers
```

### Issue 4: Slow download
**Solution:**
```bash
# Use mirror
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple llama-cpp-python
```

---

## 📦 Dependency Size Breakdown

```
llama-cpp-python:        ~50MB  (but compiles C++, needs build tools)
sentence-transformers:   ~2GB   (includes models!)
torch (dependency):      ~800MB (for sentence-transformers)
numpy:                   ~15MB
flask:                   ~5MB
sqlalchemy:              ~10MB
pandas:                  ~100MB
langchain:               ~50MB

TOTAL (without models):  ~1.8-2.5GB
```

---

## 🚀 Quick Install Commands

### Full Installation
```bash
cd "c:\Users\LENOVO\Documents\LLM ringan"

# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask, llama_cpp; print('✓ Core OK')"
python -c "from sentence_transformers import SentenceTransformer; print('✓ RAG OK')"
```

### Minimal Installation (2GB RAM)
```bash
pip install -r requirements-minimal.txt
```

---

## ✅ Next Steps After Install

1. **Test imports:**
```python
python -c "
import flask
import llama_cpp
from sentence_transformers import SentenceTransformer
print('All imports successful!')
"
```

2. **Download model:**
```bash
./scripts/download_model.sh
```

3. **Initialize database:**
```bash
python scripts/init_db.py
```

4. **Run server:**
```bash
python backend/api_gateway.py
```

---

**Status:** Ready to install! Choose requirements.txt (full) or requirements-minimal.txt (2GB) based on your deployment target.
