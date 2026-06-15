#!/usr/bin/env python3
"""Run the stdlib EvidenceOps demo server."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.demo_app import build_search_response, build_summary_payload, load_chunks, render_index


class EvidenceOpsHandler(BaseHTTPRequestHandler):
    server_version = "EvidenceOpsDemo/0.1"

    def write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.write_html(render_index())
            return
        if parsed.path == "/healthz":
            self.write_json({"status": "ok"})
            return
        if parsed.path == "/api/summary":
            self.write_json(build_summary_payload(ROOT))
            return
        if parsed.path == "/api/search":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            intended_use = params.get("intended_use", ["project_demo"])[0]
            top_k = int(params.get("top_k", ["5"])[0])
            if not query.strip():
                self.write_json({"status": "error", "message": "Missing q query parameter"}, HTTPStatus.BAD_REQUEST)
                return
            self.write_json(build_search_response(query, load_chunks(ROOT), intended_use=intended_use, top_k=top_k))
            return
        self.write_json({"status": "not_found", "path": parsed.path}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("demo-server: " + (format % args) + "\n")


class EvidenceOpsServer(ThreadingHTTPServer):
    """Threading server that avoids reverse-DNS lookups during bind."""

    def server_bind(self) -> None:
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()
        host, port = self.server_address[:2]
        self.server_name = str(host)
        self.server_port = int(port)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    server = EvidenceOpsServer((args.host, args.port), EvidenceOpsHandler)
    print(f"EvidenceOps demo server listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
