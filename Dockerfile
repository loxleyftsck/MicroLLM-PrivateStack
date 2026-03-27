# MicroLLM-PrivateStack Docker Image
# Optimized for 2GB RAM deployment
# Hardened (2026-03-27): removed hardcoded JWT, non-root user, read-only FS

FROM python:3.11-slim

# Security: non-root user
RUN groupadd -r microllm && useradd -r -g microllm -d /app -s /sbin/nologin microllm

WORKDIR /app

# Install system dependencies for llama-cpp
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY docs/ ./docs/

# Create data directories and set ownership
RUN mkdir -p /app/data /app/logs /app/models \
    && chown -R microllm:microllm /app/data /app/logs

# Models mounted via volume — do NOT bake into image (large binary)
VOLUME ["/app/models", "/app/data", "/app/logs"]

# Environment variables — secrets MUST be injected at runtime via env vars
# JWT_SECRET_KEY is intentionally NOT set here — server hard-fails if absent or weak
ENV PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    MODEL_PATH=/app/models/deepseek-r1-1.5b-q4.gguf \
    MODEL_CONTEXT_LENGTH=512 \
    MODEL_THREADS=2 \
    MODEL_BATCH=256 \
    DEBUG=false \
    CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:8000

# Expose port
EXPOSE 8000

# Security: drop to non-root
USER microllm

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn (production WSGI server) — waitress has no worker isolation
CMD ["python", "-m", "gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "1", \
     "--threads", "4", \
     "--timeout", "120", \
     "--worker-class", "gthread", \
     "--access-logfile", "/app/logs/access.log", \
     "--error-logfile", "/app/logs/error.log", \
     "backend.api_gateway:app"]
