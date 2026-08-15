#!/bin/bash
# Start MicroLLM-PrivateStack with Gunicorn (Production Mode)

echo "=================================="
echo "Starting MicroLLM-PrivateStack"
echo "Production Mode: Gunicorn"
echo "=================================="

# Resolve paths relative to this script's location so it works regardless
# of the caller's working directory (script lives in deploy/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create logs directory if not exists
mkdir -p "$PROJECT_ROOT/logs"

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "gunicorn.*api_gateway" || true
pkill -f "python.*api_gateway.py" || true

sleep 2

# Start Gunicorn
echo "Starting Gunicorn server..."
cd "$PROJECT_ROOT/backend"

gunicorn \
  --config "$PROJECT_ROOT/deploy/gunicorn.py" \
  --chdir . \
  api_gateway:app

echo "Server stopped."
