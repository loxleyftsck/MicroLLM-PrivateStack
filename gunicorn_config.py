# Gunicorn Configuration for MicroLLM-PrivateStack
# Production-grade WSGI server configuration

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "gevent"  # Async worker for better I/O handling
worker_connections = 1000
timeout = 120  # Longer timeout for LLM inference
keepalive = 5

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "microllm-privatestack"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 70)
    print(" MicroLLM-PrivateStack - Starting Gunicorn Server")
    print("=" * 70)
    print(f" Workers: {workers}")
    print(f" Worker Class: {worker_class}")
    print(f" Binding: {bind}")
    print("=" * 70)

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("🔄 Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print("✅ MicroLLM-PrivateStack is ready to accept requests!")
    print(f"🌐 HTTP: http://localhost:8000")
    print(f"📊 Health Check: http://localhost:8000/health")
    print(f"💬 Chat API: http://localhost:8000/api/chat")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️  Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"❌ Worker {worker.pid} aborted")
