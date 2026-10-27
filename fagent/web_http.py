"""Loopback-only HTTP transport with origin/Host and mutation header checks."""
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from .protocol import ProtocolError, require
from .registry import unique_keys
from .web_routes import route


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, jobs, static):
        require(address[0] == "127.0.0.1", "Only loopback binding is supported")
        self.jobs, self.static = jobs, static.resolve()
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, status, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'")
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self):
        self.body_consumed = False
        try:
            port = self.server.server_port
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            require(self.headers.get("Host") in hosts, "Invalid local Host")
            origin = self.headers.get("Origin")
            allowed = {f"http://{host}" for host in hosts} | {"http://localhost:5173", "http://127.0.0.1:5173"}
            require(origin is None or origin in allowed, "Cross-origin access denied")
            path = unquote(urlsplit(self.path).path)
            if not path.startswith("/api/"):
                require(self.command == "GET", "Method not allowed")
                return self.static_file(path)
            data = {}
            if self.command != "GET":
                require(self.headers.get("X-FAgent-Client") == "web", "Missing local client header")
                require(not self.headers.get("Transfer-Encoding"), "Chunked bodies are unsupported")
                length = int(self.headers.get("Content-Length", "0"))
                require(0 <= length <= 65536, "Request body exceeds 64 KiB")
                raw = self.rfile.read(length)
                self.body_consumed = True
                data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys) if raw else {}
                require(isinstance(data, dict), "JSON body must be an object")
            self.send(200, route(self.server.jobs, self.command, path, data))
        except ProtocolError as error:
            self.drain_rejected_body()
            self.send(400, {"error": str(error)})
        except (ValueError, KeyError, OSError, TypeError):
            self.drain_rejected_body()
            self.send(400, {"error": "Request failed. Check input, connection and run status."})

    def drain_rejected_body(self):
        """Avoid a Windows TCP reset hiding a rejection with an unread body.

        Discard only a bounded amount, without parsing it or waiting indefinitely.
        HTTP/1.0 closes this connection after the response; no request is replayed.
        """
        if self.body_consumed:
            return
        timeout = self.connection.gettimeout()
        try:
            length = int(self.headers.get("Content-Length", "0"))
            self.connection.settimeout(0.25)
            if length > 0:
                self.rfile.read(min(length, 65537))
        except (OSError, ValueError):
            pass
        finally:
            self.connection.settimeout(timeout)

    def static_file(self, path):
        root = self.server.static
        target = (root / path.lstrip("/")).resolve()
        require(target.is_relative_to(root), "Path escapes static directory")
        if target.is_dir() or not target.exists() and "." not in target.name:
            target = root / "index.html"
        if not target.is_file():
            return self.send(404, b"Build the frontend first: cd web && npm install && npm run build", "text/plain")
        return self.send(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or "application/octet-stream")

    do_GET = dispatch
    do_POST = dispatch
    do_DELETE = dispatch
