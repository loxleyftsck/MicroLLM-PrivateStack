# Quick Test Instructions

## ✅ API Server is Running
Port: 8000  
Status: ✅ Active

## 🎯 How to Test Frontend

### Option 1: Direct File (Simplest)
1. Right-click `frontend/index.html`
2. Choose "Open with" → Your browser
3. Interface akan muncul di `file:///...`

### Option 2: Test Page (Recommended)
1. Right-click `frontend/test.html`
2. Open with browser
3. Klik "Test /health" untuk verify API
4. Klik "Open Chat UI" untuk main interface

### Option 3: Python HTTP Server
```bash
# Terminal baru (jangan stop API server)
cd frontend
python -m http.server 3000
```
Then visit: http://localhost:3000

---

## ⚠️ Common Issues

### Issue: ERR_EMPTY_RESPONSE on port 5500
**Fix:** Port salah! API di port **8000**, bukan 5500
- `app.js` sudah di-update ke port 8000
- Refresh browser

### Issue: CORS Error
**Fix:** API sudah enable CORS untuk semua origins
- Check API server masih running
- Restart browser

---

## ✅ Expected Behavior

1. **Health Indicator:** Green dot (connected) atau Red (disconnected)
2. **Send Message:** Type question → Click send
3. **Demo Response:** [DEMO MODE] message appears
4. **Status:** "Model not loaded" = normal (demo mode)

---

**Current Status:** Frontend fixed, ready to test! 🚀
