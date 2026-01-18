# MicroLLM-PrivateStack API Documentation

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Register a New User
**POST** `/api/auth/register`

Request:
```json
{
  "email": "user@company.com",
  "password": "SecurePass123!",
  "display_name": "John Doe"
}
```

Response (201):
```json
{
  "message": "Registration successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid-here",
    "email": "user@company.com",
    "display_name": "John Doe"
  },
  "workspace_id": "default-workspace-uuid"
}
```

### Login
**POST** `/api/auth/login`

Request:
```json
{
  "email": "user@company.com",
  "password": "SecurePass123!"
}
```

Response (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid-here",
    "email": "user@company.com",
    "display_name": "John Doe"
  }
}
```

## Chat API

### Send Message
**POST** `/api/chat`

Request:
```json
{
  "message": "What is machine learning?",
  "max_tokens": 256,
  "temperature": 0.7,
  "workspace_id": "optional-workspace-uuid"
}
```

Response (200):
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "status": "success",
  "model_loaded": true,
  "tokens_generated": 45,
  "security": {
    "validated": true,
    "confidence_score": 0.95,
    "warnings": [],
    "asvs_compliance": ["V5.3.1", "V5.3.4"]
  }
}
```

## Document Management (RAG)

### Upload Document
**POST** `/api/documents/upload`

Request: `multipart/form-data`
- `file`: The document file (PDF, TXT, MD, CSV)

Response (201):
```json
{
  "message": "Document processed and added to knowledge base",
  "filename": "report.pdf",
  "chunks_added": 15,
  "total_chunks": 42
}
```

### Clear Knowledge Base
**POST** `/api/documents/clear`

Response (200):
```json
{
  "message": "Knowledge base cleared"
}
```

## Workspace Management

### List Workspaces
**GET** `/api/workspaces`

Response (200):
```json
{
  "workspaces": [
    {
      "id": "uuid-1",
      "name": "Default Workspace",
      "description": "Your personal workspace"
    },
    {
      "id": "uuid-2",
      "name": "Project Alpha",
      "description": "Q1 2026 initiatives"
    }
  ]
}
```

### Create Workspace
**POST** `/api/workspaces`

Request:
```json
{
  "name": "Project Beta",
  "description": "New product development"
}
```

Response (201):
```json
{
  "message": "Workspace created",
  "workspace_id": "new-uuid"
}
```

## System Endpoints

### Health Check
**GET** `/api/health`

Response (200):
```json
{
  "status": "healthy",
  "service": "MicroLLM-PrivateStack",
  "version": "1.0.1-optimized",
  "model": {
    "llm_loaded": true,
    "cache": {
      "enabled": true,
      "hit_rate_pct": 45.2,
      "current_entries": 128
    }
  }
}
```

### Model Information
**GET** `/api/models/list`

Response (200):
```json
{
  "loaded": "DeepSeek-R1-1.5B",
  "status": "active",
  "parameters": "1.5B",
  "context_length": 512
}
```

### Security Status
**GET** `/api/security/status`

Response (200):
```json
{
  "encryption": "AES-256-GCM",
  "compliance": ["GDPR", "SOC 2", "ISO 27001"],
  "data_residency": "On-premise",
  "private": true,
  "security_features": {
    "prompt_injection_detection": true,
    "pii_masking": true,
    "secrets_scanning": true
  }
}
```

### System Metrics
**GET** `/api/metrics/system`

Response (200):
```json
{
  "ram_total_gb": 8.0,
  "ram_used_gb": 4.5,
  "ram_percent": 56.0,
  "cpu_percent": 15.0,
  "timestamp": "2026-01-18T14:30:00.000000"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing 'message' in request body"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Request blocked by security guardrails",
  "reason": "Potential prompt injection detected",
  "status": "blocked"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message",
  "status": "error"
}
```
