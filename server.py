"""server.py：本机服务（基线只有无条件的读写接口）。"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from kvstore import KV

STORE = KV()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = self.path.rsplit("/", 1)[-1]
        value = STORE.get(key)
        body = json.dumps({"key": key, "value": value, "version": STORE.version(key)}).encode()
        self.send_response(200 if value is not None else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_PUT(self):
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        key = self.path.rsplit("/", 1)[-1]
        version = STORE.put(key, payload.get("value"))
        body = json.dumps({"key": key, "version": version}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def serve(port: int = 0):
    server = HTTPServer(("127.0.0.1", port), Handler)
    return server


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print("listening on http://127.0.0.1:%d" % port)
    serve(port).serve_forever()
