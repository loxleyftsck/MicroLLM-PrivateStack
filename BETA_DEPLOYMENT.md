# Beta Deployment - v0.9.0-beta
**Branch:** dev  
**Status:** Internal Beta Testing  
**Date:** January 14, 2026

## Deployment Information

### Version
- **Version:** v0.9.0-beta
- **Branch:** dev
- **Commit:** Latest
- **Production Readiness:** 65%

### Environment
- **Type:** Beta/Development
- **Purpose:** Internal team testing
- **Max Users:** 5-10 testers
- **Uptime Target:** 90% (non-critical)

### Features Enabled
✅ Core API endpoints  
✅ Authentication (JWT)  
✅ LLM inference  
✅ Security guardrails  
✅ Output formatting  
✅ Database persistence  
✅ Admin account creation  

### Features Disabled/Incomplete
⚠️  Frontend not fully integrated  
⚠️  Workspace management (partial)  
⚠️  Document upload (UI only)  
⚠️  Redis caching (not tested)  
❌ HTTPS (not configured)  
❌ Rate limiting  
❌ Monitoring  

### Known Issues
1. Frontend authentication not wired up
2. CORS issues with corporate.html
3. Workspace data not loading from DB
4. Chat history not persisting to frontend
5. Redis cache not tested

### Deployment Commands

#### Start Server (Development Mode)
```bash
cd backend
python api_gateway.py
```

#### Start Server (Production Mode - Gunicorn)
```bash
.\start_production.ps1
```

#### Create Admin Account
```bash
python scripts/create_admin.py
# Default: admin@microllm.local / Admin@123456

# Or custom:
python scripts/create_custom_admin.py
```

### Testing Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Chat API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test query","max_tokens":50}'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@microllm.local","password":"Admin@123456"}'
```

### Beta Tester Instructions

1. **Setup:**
   ```bash
   git clone https://github.com/loxleyftsck/MicroLLM-PrivateStack.git
   cd MicroLLM-PrivateStack
   git checkout dev
   pip install -r requirements.txt
   python scripts/init_db.py
   python scripts/create_admin.py
   ```

2. **Start Server:**
   ```bash
   cd backend
   python api_gateway.py
   ```

3. **Test API:**
   - Access: http://localhost:8000
   - Health: http://localhost:8000/health
   - Docs: See README.md

4. **Report Issues:**
   - GitHub Issues
   - Email: [your-email]
   - Slack: [if applicable]

### Success Metrics (Beta)

- [ ] API responds to health checks
- [ ] Authentication works (login/logout)
- [ ] LLM generates responses
- [ ] Security guardrails block malicious input
- [ ] Database persists user data
- [ ] No critical crashes
- [ ] Acceptable response time (<30s per query)

### Exit Criteria (Move to Staging)

- [ ] All known issues documented
- [ ] 5+ successful user test sessions
- [ ] Frontend integration complete
- [ ] Redis caching tested
- [ ] Database optimization done
- [ ] Performance baseline established

### Rollback Plan

If critical issues found:
```bash
git checkout main
# Run stable version
```

### Support

- **Documentation:** docs/PHASE2_QUICKSTART.md
- **Troubleshooting:** docs/PHASE2_PROGRESS.md
- **Roadmap:** docs/roadmap.md
- **Security:** docs/SECURITY.md

---

## Next Steps

After beta testing completes:
1. Fix reported issues
2. Complete Phase 2 (frontend integration)
3. Start Phase 3 (production hardening)
4. Move to staging environment
5. Public beta (when 95% ready)

---

**Deployed:** January 14, 2026  
**By:** Development Team  
**Status:** 🟡 BETA - Internal Testing Only
