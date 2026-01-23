MicroLLM-PrivateStack is a lightweight, on-premise AI assistant designed for corporate environments.

## Key Features

### 1. Optimized for Low-Resource Hardware
The system is specifically designed to run efficiently on machines with as little as 2GB of RAM. This is achieved through:
- Quantized model weights (Q4 format reduces memory footprint by 4x)
- Struct-of-Arrays (SoA) semantic caching for 3.5x faster lookups
- Context window optimization (512 tokens default)
- Memory-mapped file loading

### 2. Complete Data Privacy
All data processing happens locally on your infrastructure:
- No external API calls
- No data transmission to cloud services
- Full GDPR, SOC 2, and ISO 27001 compliance
- Audit logging for all operations

### 3. Security-First Architecture
Built with OWASP ASVS Level 2 compliance:
- Prompt injection detection
- PII (Personally Identifiable Information) masking
- Secrets scanning in outputs
- JWT-based authentication with session management
- Rate limiting on all endpoints

### 4. RAG (Retrieval-Augmented Generation)
Upload your company documents and get AI answers based on your knowledge base:
- Supports PDF, TXT, MD, and CSV files
- Automatic text extraction and chunking
- Vector similarity search using mean-pooled embeddings
- Context injection into LLM prompts

## Technical Specifications

| Component | Specification |
|-----------|---------------|
| LLM Model | DeepSeek-R1-1.5B (Quantized Q4) |
| Model Size | ~1GB |
| RAM Required | 2GB minimum, 4GB recommended |
| CPU | Any x86-64 processor |
| GPU | Optional (CPU-only mode supported) |
| OS | Windows, Linux, macOS |

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat` - Chat with AI (requires auth)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/documents/upload` - Upload document for RAG
- `GET /api/workspaces` - List user workspaces
- `GET /api/models/list` - Get model information
- `GET /api/security/status` - Security compliance status
- `GET /api/metrics/system` - System metrics (RAM/CPU)

## Deployment Options

1. **Local Development**: Run directly with Python
2. **Production (Windows)**: Use Waitress WSGI server
3. **Production (Linux)**: Use Gunicorn WSGI server
4. **Docker**: Full containerized deployment with Redis and Nginx

## Getting Started

1. Clone the repository
2. Download the model: `python scripts/download_model.py`
3. Start the server: `.\start_production.ps1` (Windows) or `./start_production.sh` (Linux)
4. Open browser: `http://localhost:8000`

## License

MIT License - Free for commercial use.
