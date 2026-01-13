# Sprint 1 - Quick Start Guide (UPDATED)

## ⚠️ Known Issues & Fixes

### Issue 1: llama-cpp-python Takes Long to Compile
**Solution:** Skip it for now, use demo mode first!

```bash
# Install everything EXCEPT llama-cpp-python
pip install flask flask-cors python-dotenv
pip install gunicorn sqlalchemy bcrypt pyjwt
pip install requests pyyaml loguru

# llama-cpp-python akan di-skip dulu (compile 10-15 menit)
# API akan jalan dalam DEMO MODE tanpa real inference
```

### Issue 2: Import Module Error
**Solution:** Run from backend directory

```bash
cd backend
python api_gateway.py
```

### Issue 3: Model Download 401 Error  
**Solution:** Model sudah di-update ke alternatif yang lebih kecil

```bash
python scripts/download_model.py
# Pilih option 1 (Qwen 0.5B - 350MB, lebih cepat)
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Core Dependencies (Skip llama-cpp for now)

```bash
# Minimal install (tanpa llama-cpp-python)
pip install flask flask-cors python-dotenv
pip install sqlalchemy bcrypt pyjwt loguru
```

### Step 2: Initialize Database

```bash
python scripts/init_db.py
```

### Step 3: Run API in Demo Mode

```bash
cd backend
python api_gateway.py
```

Visit: **http://localhost:8000/health**

---

## 💬 Test the API (Demo Mode)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Test question\"}"
```

**Response akan dari mock/demo, bukan real LLM** (karena model belum loaded)

---

## 🔧 Optional: Enable Real LLM (Nanti)

Jika mau real inference:

```bash
# 1. Install llama-cpp-python (compile 10-15 menit!)
pip install llama-cpp-python

# 2. Download model kecil (Qwen 0.5B)
python scripts/download_model.py

# 3. Create .env file
cp .env.example .env

# 4. Edit .env, set:
MODEL_PATH=./models/qwen-0.5b-q4.gguf

# 5. Restart server
cd backend
python api_gateway.py
```

---

## ✅ What Works Now

- ✅ API server running
- ✅ Health check endpoint
- ✅ Chat endpoint (demo/mock mode)
- ✅ Database initialized
- ✅ Web UI accessible

## 🔜 Next: Real LLM

Optional upgrade nanti setelah foundation stable!

---

**Current Status:** API running in demo mode, ready to test! 🎉
