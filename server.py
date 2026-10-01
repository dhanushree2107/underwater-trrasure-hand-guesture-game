"""
Underwater Treasure Hunt — Multi-Port Web Server
Serves the web client simultaneously on Render's assigned PORT as well as local ports (8000, 3000, 5000).
Zero external dependencies — pure Python standard library.
"""

import http.server
import socketserver
import os
import sys
import threading

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve from directory containing index.html
if os.path.exists(os.path.join(BASE_DIR, "index.html")):
    WEB_DIR = BASE_DIR
else:
    WEB_DIR = os.path.join(BASE_DIR, "web")

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin-allow-popups")
        super().end_headers()

    def log_message(self, format, *args):
        pass

def serve_on_port(port):
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), QuietHTTPHandler) as httpd:
            print(f"  -> Serving on port {port}")
            sys.stdout.flush()
            httpd.serve_forever()
    except Exception as e:
        pass

def main():
    print("\n=======================================================")
    print("Underwater Treasure Hunt Web Server Running!")
    print(f"Primary Port: {PORT}")
    print("=======================================================\n")
    sys.stdout.flush()

    # In local development (no PORT env var), run aux ports in background threads
    if "PORT" not in os.environ:
        for aux_port in [3000, 5000]:
            t = threading.Thread(target=serve_on_port, args=(aux_port,), daemon=True)
            t.start()

    try:
        serve_on_port(PORT)
    except KeyboardInterrupt:
        print("\n[Web Server] Shutting down...")

if __name__ == "__main__":
    main()