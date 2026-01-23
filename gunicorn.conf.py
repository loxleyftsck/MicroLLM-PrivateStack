"""
Gunicorn Configuration for MicroLLM-PrivateStack
Production deployment with 3x throughput optimization
"""

import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes (2 * CPU cores for 2GB RAM constraint)
workers = min(int(os.getenv("GUNICORN_WORKERS", 2 * multiprocessing.cpu_count())), 4)
worker_class = "sync"  # Use sync for llama.cpp (not thread-safe)
worker_connections = 100
threads = 1  # Single-threaded per worker for LLM inference

# Timeouts (extended for LLM inference)
timeout = 120  # 2 minutes for long inference
graceful_timeout = 30
keepalive = 5

# Memory optimization for 2GB RAM
max_requests = 500  # Restart worker after N requests (prevent memory leaks)
max_requests_jitter = 50  # Add randomness to prevent thundering herd

# Logging
accesslog = "../logs/access.log"
errorlog = "../logs/error.log"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "microllm-api"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 60)
    print("MicroLLM-PrivateStack - Gunicorn Production Server")
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print(f"Timeout: {timeout}s")
    print("=" * 60)

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Reloading workers...")

def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    print(f"⚠️ Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    print(f"❌ Worker {worker.pid} aborted")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"✅ Worker {worker.pid} spawned")

def post_worker_init(worker):
    """Called just after a worker has initialized."""
    print(f"🚀 Worker {worker.pid} ready to serve")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"👋 Worker {worker.pid} exited")
