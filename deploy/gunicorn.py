# Gunicorn Configuration for MicroLLM-PrivateStack
# Production-grade WSGI server configuration

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
# NOTE: Only 1 worker — the LLM (GGUF model) is loaded into process memory,
# so each additional worker would load its own full copy of the model and
# blow past the 2GB RAM budget this project is designed around. Concurrency
# within the single worker comes from threads instead. Mirrors Dockerfile.
workers = 1
worker_class = "gthread"  # Threaded worker — avoids the extra `gevent` dependency
threads = 4
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
