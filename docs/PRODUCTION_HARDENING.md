# Production Hardening Checklist

**Environment:** Production Deployment  
**System:** MicroLLM-PrivateStack  
**Version:** 1.1.0 (Target)  
**Last Updated:** 2026-01-13

---

## Overview

This checklist ensures MicroLLM-PrivateStack is production-ready with enterprise-grade security, reliability, and compliance. Complete all items before deploying to production.

**Estimated Time:** 2-3 days for full checklist completion

---

## Pre-Deployment Checklist

### ✅ Security Hardening (P0 - Critical)

#### Authentication & Access Control
- [ ] **Change default admin password**
  ```bash
  python scripts/change_password.py admin@microllm.local
  # Use strong password (16+ chars, mixed case, symbols, numbers)
  ```
- [ ] **Generate production JWT secret**
  ```bash
  openssl rand -hex 32 > /tmp/jwt_secret.txt
  # Add to .env: JWT_SECRET_KEY=<generated_value>
  # NEVER commit this to Git!
  ```
- [ ] **Configure JWT token expiry**
  ```bash
  # In .env
  JWT_ACCESS_TOKEN_EXPIRES=3600    # 1 hour
  JWT_REFRESH_TOKEN_EXPIRES=604800 # 7 days
  ```
- [ ] **Create non-root admin account**
  ```bash
  # Remove or disable default admin after setup
  python scripts/create_user.py --role admin --email admin_prod@company.com
  ```
- [ ] **Enable RBAC enforcement**
  ```python
  # In config/security.yaml
  rbac:
    enabled: true
    strict_mode: true
    default_role: viewer
  ```

#### Network Security
- [ ] **Setup TLS/HTTPS certificates**
  ```bash
  # Option 1: Let's Encrypt (free, auto-renewal)
  certbot --nginx -d api.microllm.company.com
  
  # Option 2: Corporate CA
  # Place cert.pem & key.pem in /etc/ssl/microllm/
  ```
- [ ] **Verify TLS configuration**
  ```bash
  # Test SSL Labs grade (must be A+)
  ssllabs-scan api.microllm.company.com
  
  # Or manual check
  nmap --script ssl-enum-ciphers -p 443 api.microllm.company.com
  # Expected: TLSv1.3 only, strong ciphers
  ```
- [ ] **Configure firewall rules**
  ```bash
  # Allow HTTPS only (public)
  ufw allow 443/tcp comment "HTTPS - MicroLLM API"
  
  # Allow SSH (internal network only)
  ufw allow from 10.0.0.0/8 to any port 22 comment "SSH - Internal"
  
  # Deny direct API access (nginx proxy handles it)
  ufw deny 8000/tcp comment "Block direct Flask access"
  
  # Enable firewall
  ufw --force enable
  ufw status numbered
  ```
- [ ] **Setup fail2ban (brute force protection)**
  ```bash
  apt install fail2ban -y
  
  # Create /etc/fail2ban/jail.local
  cat > /etc/fail2ban/jail.local <<EOF
  [microllm-auth]
  enabled = true
  port = 443
  filter = microllm-auth
  logpath = /var/log/microllm/access.log
  maxretry = 5
  bantime = 3600
  EOF
  
  systemctl restart fail2ban
  ```

#### Data Security
- [ ] **Enable encryption at rest**
  ```bash
  # Ensure data directory is on encrypted volume
  # Option 1: LUKS full disk encryption (already setup?)
  lsblk -o NAME,FSTYPE,MOUNTPOINT
  
  # Option 2: Application-level (AES-256)
  # Verify in .env
  export DATA_ENCRYPTION_ENABLED=true
  export DATA_ENCRYPTION_KEY=$(openssl rand -hex 32)
  ```
- [ ] **Configure backup encryption**
  ```bash
  # In backup config
  encryption:
    enabled: true
    algorithm: AES-256-GCM
    key_location: /secure/backup-key.asc
  ```
- [ ] **Implement secrets management**
  ```bash
  # Option 1: HashiCorp Vault (enterprise)
  vault kv put secret/microllm jwt_secret=$(cat /tmp/jwt_secret.txt)
  
  # Option 2: Docker secrets (simpler)
  echo $JWT_SECRET_KEY | docker secret create jwt_secret -
  
  # Option 3: AWS Secrets Manager (cloud)
  aws secretsmanager create-secret --name microllm/jwt \
    --secret-string file:///tmp/jwt_secret.txt
  ```
- [ ] **Remove .env files from production**
  ```bash
  # Never use .env in production!
  # Use environment variables or secrets manager
  mv .env .env.backup
  # Set via systemd or Docker environment
  ```

---

### ✅ Application Hardening (P0 - Critical)

#### Input Validation
- [ ] **Enable data ingestion validator**
  ```python
  # In config/security.yaml
  ingestion:
    validation:
      enabled: true
      max_file_size_mb: 50
      allowed_types: [pdf, docx, txt, csv]
      virus_scan: true  # Requires ClamAV
  ```
- [ ] **Setup ClamAV (virus scanning)**
  ```bash
  apt install clamav clamav-daemon -y
  freshclam  # Update virus definitions
  systemctl start clamav-daemon
  systemctl enable clamav-daemon
  ```
- [ ] **Configure output guardrails**
  ```python
  # In config/security.yaml
  guardrails:
    enabled: true
    prompt_injection_detection: true
    toxicity_threshold: 0.5
    hallucination_check: true
    confidence_min: 0.3
  ```

#### Rate Limiting
- [ ] **Enable API rate limiting**
  ```python
  # In config/api.yaml
  rate_limiting:
    enabled: true
    global: "1000/hour"
    per_user: "20/minute"
    per_ip: "100/hour"
    expensive_endpoints:
      "/api/rag/upload": "5/hour"
      "/api/chat": "20/minute"
  ```
- [ ] **Configure Redis (rate limit backend)**
  ```bash
  apt install redis-server -y
  systemctl enable redis-server
  systemctl start redis-server
  
  # In .env
  REDIS_URL=redis://localhost:6379/0
  ```

#### Error Handling
- [ ] **Disable debug mode**
  ```bash
  # In .env
  DEBUG=false
  FLASK_ENV=production
  LOG_LEVEL=WARNING
  ```
- [ ] **Sanitize error messages**
  ```python
  # Ensure no stack traces leaked to users
  # In backend/error_handlers.py
  @app.errorhandler(500)
  def internal_error(error):
      logger.exception("Internal error")  # Log full trace
      return {"error": "Internal server error"}, 500  # Generic to user
  ```

---

### ✅ Infrastructure (P1 - High Priority)

#### Reverse Proxy (Nginx)
- [ ] **Configure Nginx reverse proxy**
  ```nginx
  # /etc/nginx/sites-available/microllm
  server {
      listen 443 ssl http2;
      server_name api.microllm.company.com;
      
      # TLS configuration
      ssl_certificate /etc/letsencrypt/live/api.microllm/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/api.microllm/privkey.pem;
      ssl_protocols TLSv1.3;
      ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
      ssl_prefer_server_ciphers on;
      
      # Security headers
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
      add_header X-Frame-Options "DENY" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-XSS-Protection "1; mode=block" always;
      add_header Referrer-Policy "strict-origin-when-cross-origin" always;
      
      # Rate limiting
      limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
      limit_req zone=api burst=20 nodelay;
      
      # Proxy to backend
      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          
          # Timeouts
          proxy_connect_timeout 60s;
          proxy_send_timeout 60s;
          proxy_read_timeout 60s;
      }
      
      # Health check (no auth)
      location /health {
          proxy_pass http://127.0.0.1:8000/health;
          access_log off;
      }
  }
  
  # Redirect HTTP to HTTPS
  server {
      listen 80;
      server_name api.microllm.company.com;
      return 301 https://$server_name$request_uri;
  }
  ```
- [ ] **Test Nginx configuration**
  ```bash
  nginx -t
  systemctl reload nginx
  ```

#### Database
- [ ] **Setup database backups**
  ```bash
  # Daily backups at 2 AM
  crontab -e
  # Add: 0 2 * * * /opt/microllm/scripts/backup_db.sh
  
  # Backup script
  cat > /opt/microllm/scripts/backup_db.sh <<'EOF'
  #!/bin/bash
  DATE=$(date +%Y%m%d_%H%M%S)
  BACKUP_DIR=/backups/microllm
  DB_PATH=/opt/microllm/data/app.db
  
  # Create encrypted backup
  tar -czf - $DB_PATH | \
    openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:/secure/backup.key \
    > $BACKUP_DIR/db_$DATE.tar.gz.enc
  
  # Retention: keep 30 days
  find $BACKUP_DIR -name "db_*.tar.gz.enc" -mtime +30 -delete
  EOF
  
  chmod +x /opt/microllm/scripts/backup_db.sh
  ```
- [ ] **Test database recovery**
  ```bash
  # Restore from backup
  openssl enc -aes-256-cbc -d -pbkdf2 -pass file:/secure/backup.key \
    -in $BACKUP_DIR/db_20260113.tar.gz.enc | tar -xzf -
  
  # Verify integrity
  sqlite3 app.db "PRAGMA integrity_check;"
  ```

#### Monitoring
- [ ] **Deploy Prometheus + Grafana**
  ```bash
  # Docker Compose for monitoring stack
  cat > docker-compose.monitoring.yml <<EOF
  version: '3'
  services:
    prometheus:
      image: prom/prometheus:latest
      ports:
        - "9090:9090"
      volumes:
        - ./prometheus.yml:/etc/prometheus/prometheus.yml
        - prometheus-data:/prometheus
    
    grafana:
      image: grafana/grafana:latest
      ports:
        - "3001:3000"
      environment:
        - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD}
      volumes:
        - grafana-data:/var/lib/grafana
  
  volumes:
    prometheus-data:
    grafana-data:
  EOF
  
  docker-compose -f docker-compose.monitoring.yml up -d
  ```
- [ ] **Configure Prometheus scraping**
  ```yaml
  # prometheus.yml
  global:
    scrape_interval: 15s
  
  scrape_configs:
    - job_name: 'microllm'
      static_configs:
        - targets: ['localhost:8000']
      metrics_path: '/metrics'
  ```
- [ ] **Setup alerting (PagerDuty/Slack)**
  ```yaml
  # alertmanager.yml
  route:
    receiver: 'slack'
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 4h
  
  receivers:
    - name: 'slack'
      slack_configs:
        - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
          channel: '#microllm-alerts'
          title: '{{ .GroupLabels.alertname }}'
  ```

---

### ✅ Operational Readiness (P1)

#### Logging
- [ ] **Configure centralized logging**
  ```bash
  # Option 1: Loki (lightweight)
  docker run -d --name=loki -p 3100:3100 grafana/loki:latest
  
  # Option 2: ELK Stack (enterprise)
  # Deploy Elasticsearch + Logstash + Kibana
  ```
- [ ] **Setup log rotation**
  ```bash
  # /etc/logrotate.d/microllm
  /var/log/microllm/*.log {
      daily
      missingok
      rotate 30
      compress
      delaycompress
      notifempty
      create 0640 microllm microllm
      sharedscripts
      postrotate
          systemctl reload microllm
      endscript
  }
  ```
- [ ] **Enable audit logging**
  ```python
  # In .env
  AUDIT_LOGGING=true
  AUDIT_LOG_PATH=/var/log/microllm/audit.log
  ```

#### Performance
- [ ] **Load test (stress test)**
  ```bash
  # Using Apache Bench
  ab -n 1000 -c 10 -p chat_payload.json \
    -T 'application/json' \
    https://api.microllm.company.com/api/chat
  
  # Expected: <15s P95 latency, 0% errors
  ```
- [ ] **Memory stress test**
  ```bash
  # Monitor during 100 concurrent requests
  watch -n 1 'free -h && ps aux | grep python | grep -v grep'
  
  # Expected: <1.8GB RAM usage (within 2GB target)
  ```
- [ ] **Configure resource limits**
  ```bash
  # systemd service limits
  # /etc/systemd/system/microllm.service
  [Service]
  MemoryMax=2G
  MemoryHigh=1.8G
  CPUQuota=80%
  ```

#### Disaster Recovery
- [ ] **Create disaster recovery runbook**
  ```markdown
  # Create docs/DR_RUNBOOK.md
  ## Scenarios
  1. Database corruption → Restore from backup
  2. Service crash → Restart via systemd
  3. DDoS attack → Enable Cloudflare/rate limiting
  4. Data breach → Follow incident response playbook
  ```
- [ ] **Test disaster recovery**
  ```bash
  # Simulate failure
  systemctl stop microllm
  
  # Restore from backup
  bash /opt/microllm/scripts/restore_from_backup.sh
  
  # Verify service
  systemctl start microllm
  curl https://api.microllm.company.com/health
  ```

---

### ✅ Compliance & Documentation (P2)

#### Documentation
- [ ] **Update all documentation**
  - [ ] README.md with production instructions
  - [ ] SECURITY.md with current architecture
  - [ ] COMPLIANCE.md with controls mapping
  - [ ] API documentation (Swagger/OpenAPI)
- [ ] **Create operational runbooks**
  - [ ] Deployment procedure
  - [ ] Rollback procedure
  - [ ] Incident response playbook
  - [ ] Common troubleshooting guide

#### Legal & Compliance
- [ ] **Privacy policy published**
  ```bash
  # Must be accessible at /privacy-policy
  # Include: data collection, usage, retention, rights
  ```
- [ ] **Terms of service published**
  ```bash
  # Must be accessible at /terms-of-service
  ```
- [ ] **GDPR compliance verified**
  - [ ] Data retention policy enforced
  - [ ] User deletion workflow tested
  - [ ] Data export functionality working
  - [ ] Consent mechanisms in place
- [ ] **SOC 2 controls documented**
  - [ ] Access control matrix
  - [ ] Change management logs
  - [ ] Monitoring evidence
  - [ ] Incident response procedures

---

## Post-Deployment Verification

### Smoke Tests
```bash
# 1. Health check
curl https://api.microllm.company.com/health
# Expected: {"status":"healthy"}

# 2. Authentication
curl -X POST https://api.microllm.company.com/api/auth/login \
  -d '{"username":"test@company.com","password":"test123"}'
# Expected: {"access_token":"eyJ..."}

# 3. Chat endpoint (with token)
curl -X POST https://api.microllm.company.com/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"test"}'
# Expected: {"response":"...","status":"success"}

# 4. TLS verification
curl -vI https://api.microllm.company.com 2>&1 | grep "SSL"
# Expected: TLSv1.3

# 5. Rate limiting
for i in {1..25}; do curl https://api.microllm.company.com/health; done
# Expected: Last few requests return 429 (Too Many Requests)
```

### Security Validation
- [ ] **Run vulnerability scan**
  ```bash
  # OWASP ZAP
  docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://api.microllm.company.com
  
  # Expected: No high/critical vulnerabilities
  ```
- [ ] **Penetration testing (optional but recommended)**
  ```bash
  # Engage third-party or use:
  # - Burp Suite Professional
  # - Metasploit
  # - Nessus
  ```

---

## Rollback Plan

If issues arise post-deployment:

```bash
# 1. Quick rollback (Docker)
docker-compose down
docker-compose up -f docker-compose.v1.0.yml -d

# 2. Full rollback (Git)
git checkout v1.0.0
bash deploy.sh

# 3. Database rollback (if schema changed)
bash scripts/db_rollback.sh --to-version 1.0

# 4. Notify users
# Send status.microllm.company.com update
```

---

## Checklist Summary

**Total Items:** 68  
**Completion Target:** 100% before production

**Priority Breakdown:**
- P0 (Critical): 28 items
- P1 (High): 25 items  
- P2 (Medium): 15 items

**Estimated Timeline:**
- Day 1: Security hardening (P0)
- Day 2: Infrastructure & monitoring (P1)
- Day 3: Documentation & compliance (P2)
- Day 4: Testing & validation

---

## Sign-Off

**Checklist Completed By:**  
Name: ___________________  
Date: ___________________  
Signature: _______________

**Approved for Production:**  
CTO/Engineering Manager: ___________________  
Date: ___________________

---

**Next Review:** Quarterly or after major version update

---

*This checklist follows industry best practices from OWASP, NIST, and CIS benchmarks.*
