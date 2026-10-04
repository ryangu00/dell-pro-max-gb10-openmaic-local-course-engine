#!/usr/bin/env python3
"""Receive course JSON on loopback, with a fixed output folder and safe names."""
import argparse
import http.server
import json
import os
from pathlib import Path
import re


def handler_for(output, origin):
    output = Path(output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    class Receiver(http.server.BaseHTTPRequestHandler):
        def cors(self):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def reply(self, status, body):
            payload = json.dumps(body).encode()
            self.send_response(status)
            self.cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_OPTIONS(self):
            self.send_response(204)
            self.cors()
            self.end_headers()

        def do_POST(self):
            name = self.path[1:] if self.path.startswith("/") else ""
            if re.fullmatch(r"[A-Za-z0-9_-]+", name) is None:
                self.reply(400, {"error": "Use a plain alphanumeric, underscore or hyphen name"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0:
                    raise ValueError
            except ValueError:
                self.reply(400, {"error": "Invalid Content-Length"})
                return
            body = self.rfile.read(size)
            path = output / (name + ".json")
            # A pre-existing symlink must not redirect a write outside the folder.
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(body)
            except OSError:
                self.reply(400, {"error": "Cannot write output file"})
                return
            self.reply(200, {"saved": path.name, "bytes": len(body)})

        def log_message(self, *args):
            pass

    return Receiver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="exports")
    parser.add_argument("--port", type=int, default=9977, help="Loopback receiver port")
    parser.add_argument("--origin", default="http://localhost:3000", help="Exact application origin for CORS")
    args = parser.parse_args()
    handler = handler_for(args.output, args.origin)
    with http.server.HTTPServer(("127.0.0.1", args.port), handler) as server:
        print("Loopback receiver ready", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
