"""
Underwater Treasure Hunt — Multi-Port Web Server
Serves the web client simultaneously on ports 8000, 3000, and 5000 so localhost connects immediately.
"""

import http.server
import socketserver
import os
import sys
import threading

PORTS = [8000, 3000, 5000]
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin-allow-popups")
        super().end_headers()

    def log_message(self, format, *args):
        # Silent or minimal logging
        pass

def serve_on_port(port):
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), QuietHTTPHandler) as httpd:
            print(f"  -> http://localhost:{port}")
            sys.stdout.flush()
            httpd.serve_forever()
    except Exception as e:
        pass

def main():
    print("\n=======================================================")
    print("Underwater Treasure Hunt Web Server Running!")
    print("Accessible at any of the following URLs:")
    threads = []
    for port in PORTS:
        t = threading.Thread(target=serve_on_port, args=(port,), daemon=True)
        t.start()
        threads.append(t)
    print("=======================================================\n")
    sys.stdout.flush()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n[Web Server] Shutting down...")

if __name__ == "__main__":
    main()
