# MicroLLM-PrivateStack Docker Image
# Optimized for 2GB RAM deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for llama-cpp
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY models/ ./models/
COPY docs/ ./docs/

# Create data directories
RUN mkdir -p /app/data /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV MODEL_PATH=/app/models/deepseek-r1-1.5b-q4.gguf
ENV MODEL_CONTEXT_LENGTH=512
ENV MODEL_THREADS=2
ENV MODEL_BATCH=256
ENV JWT_SECRET_KEY=change-me-in-production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run with waitress (production WSGI server)
CMD ["python", "-m", "waitress", "--host=0.0.0.0", "--port=8000", "backend.api_gateway:app"]
