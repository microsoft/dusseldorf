"""Minimal mock API server for local UI development."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "path": self.path}).encode())

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Mock API running on http://localhost:8080")
    server.serve_forever()
