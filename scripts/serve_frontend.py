# Simple HTTP Server to serve login.html
# This fixes the "Failed to fetch" error

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

os.chdir(os.path.dirname(__file__))
os.chdir('..')  # Go to project root

print(f"🌐 Starting HTTP server on port {PORT}...")
print(f"📁 Serving directory: {DIRECTORY}/")
print(f"\n✅ Open in browser:")
print(f"   http://localhost:{PORT}/login.html")
print(f"\n⚠️  Press CTRL+C to stop\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
