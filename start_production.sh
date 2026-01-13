#!/bin/bash
# Start MicroLLM-PrivateStack with Gunicorn (Production Mode)

echo "=================================="
echo "Starting MicroLLM-PrivateStack"
echo "Production Mode: Gunicorn + Gevent"
echo "=================================="

# Create logs directory if not exists
mkdir -p logs

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "gunicorn.*api_gateway" || true
pkill -f "python.*api_gateway.py" || true

sleep 2

# Start Gunicorn
echo "Starting Gunicorn server..."
cd backend

gunicorn \
  --config ../gunicorn_config.py \
  --chdir . \
  api_gateway:app

echo "Server stopped."
