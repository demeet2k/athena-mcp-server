from __future__ import annotations

"""Bounded JSON-RPC-over-HTTP adapter for the canonical ATHENA Server.

This host intentionally does not claim MCP Streamable HTTP or SSE. It provides
one JSON-RPC request/response at POST /mcp plus operational health endpoints.
Health is local substrate observation, not release, deployment, or truth proof.
"""

import argparse
import hmac
import ipaddress
import json
import os
import signal
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from . import __version__
from .deployment import HTTP_ADAPTER_VERSION
from .server import Server

DEFAULT_MAX_BODY_BYTES = 2 * 1024 * 1024
MIN_TOKEN_BYTES = 24


def _is_loopback(host: str) -> bool:
    value = str(host or "").strip().lower()
    if value in {"localhost", "ip6-localhost"}:
        return True
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def _load_token(explicit: str | None, token_file: str | None) -> str | None:
    direct = explicit.strip() if explicit else None
    from_file = None
    if token_file:
        path = Path(token_file)
        from_file = path.read_text(encoding="utf-8").strip()
        if not from_file:
            raise ValueError("token file is empty")
    if direct and from_file and not hmac.compare_digest(direct, from_file):
        raise ValueError("explicit token and token-file values disagree")
    token = direct or from_file
    if token and len(token.encode("utf-8")) < MIN_TOKEN_BYTES:
        raise ValueError(f"HTTP bearer token must contain at least {MIN_TOKEN_BYTES} UTF-8 bytes")
    return token


class RuntimeController:
    """Serialize all dispatch around one SQLite-backed canonical Server."""

    def __init__(
        self,
        db: str,
        *,
        git_root: str | None = None,
        migrate: bool = False,
        readiness_cache_seconds: float = 1.0,
    ) -> None:
        self.server = Server(db, git_root)
        self.lock = threading.RLock()
        self.started_at = time.time()
        self.request_count = 0
        self.rpc_count = 0
        self.error_count = 0
        self.readiness_cache_seconds = max(0.0, float(readiness_cache_seconds))
        self._readiness_cached_at = 0.0
        self._readiness_cache: dict[str, Any] | None = None
        self.migration_receipt: dict[str, Any] | None = None
        if migrate:
            self.migration_receipt = self._migrate()
            if self.migration_receipt.get("status") not in {"APPLIED", "UP_TO_DATE"}:
                raise RuntimeError(f"schema migration failed closed: {self.migration_receipt}")
        verification = self._schema_verification()
        if verification.get("status") != "PASS":
            raise RuntimeError(
                "schema verification failed; start with --migrate or repair the persistent database"
            )

    @property
    def db_path(self) -> str:
        return str(self.server.store.path)

    def _foundation(self):
        return self.server.aor_development.integrity.state_foundation

    def _migrate(self) -> dict[str, Any]:
        foundation = self._foundation()
        return foundation.schema.migrate(
            "athena-http-host-v2",
            foundation.CRITICAL_REQUIRED_TABLES,
            foundation.CRITICAL_REQUIRED_COLUMNS,
        )

    def _schema_verification(self) -> dict[str, Any]:
        foundation = self._foundation()
        return foundation.schema.verify(
            foundation.CRITICAL_REQUIRED_TABLES,
            foundation.CRITICAL_REQUIRED_COLUMNS,
        )

    def live_snapshot(self) -> dict[str, Any]:
        return {
            "version": HTTP_ADAPTER_VERSION,
            "status": "LIVE",
            "process_uptime_seconds": max(0.0, time.time() - self.started_at),
            "package_version": __version__,
            "database": self.db_path,
            "boundary": "Liveness observes this process only; it is not readiness, deployment, or semantic correctness.",
        }

    def readiness_snapshot(self, *, force: bool = False) -> dict[str, Any]:
        now = time.monotonic()
        with self.lock:
            if (
                not force
                and self._readiness_cache is not None
                and now - self._readiness_cached_at <= self.readiness_cache_seconds
            ):
                return dict(self._readiness_cache)
            try:
                schema = self._schema_verification()
                startup = self.server.call_tool("athena_startup_health", {})
                startup_ready = startup.get("ready") is True or startup.get("status") in {
                    "READY",
                    "READY_LOCAL",
                    "PASS",
                }
                ready = schema.get("status") == "PASS" and startup_ready
                value = {
                    "version": HTTP_ADAPTER_VERSION,
                    "status": "READY" if ready else "NOT_READY",
                    "ready": ready,
                    "package_version": __version__,
                    "schema": {
                        "status": schema.get("status"),
                        "up_to_date": schema.get("up_to_date"),
                        "missing_required_tables": schema.get("missing_required_tables"),
                        "missing_required_columns": schema.get("missing_required_columns"),
                    },
                    "startup": startup,
                    "boundary": (
                        "READY certifies current local schema and startup-health observations only; it is not "
                        "release qualification, production activation, empirical truth, or Y1 authority."
                    ),
                }
            except Exception as exc:
                self.error_count += 1
                value = {
                    "version": HTTP_ADAPTER_VERSION,
                    "status": "NOT_READY",
                    "ready": False,
                    "package_version": __version__,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "boundary": "Probe failure remains explicit and is never converted into PASS.",
                }
            self._readiness_cache = value
            self._readiness_cached_at = now
            return dict(value)

    def health_snapshot(self) -> dict[str, Any]:
        ready = self.readiness_snapshot()
        return {
            "version": HTTP_ADAPTER_VERSION,
            "status": "PASS" if ready.get("ready") else "DEGRADED",
            "live": self.live_snapshot(),
            "ready": ready,
            "requests": {
                "total": self.request_count,
                "rpc": self.rpc_count,
                "errors": self.error_count,
            },
        }

    def dispatch(self, message: dict[str, Any]) -> dict[str, Any] | None:
        with self.lock:
            self.rpc_count += 1
            try:
                return self.server.handle(message)
            except Exception as exc:
                self.error_count += 1
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"error_type": type(exc).__name__},
                    },
                }

    def metrics_text(self) -> str:
        readiness = self.readiness_snapshot()
        try:
            db_size = Path(self.db_path).stat().st_size
        except OSError:
            db_size = 0
        return "\n".join(
            [
                "# HELP athena_http_up Process liveness.",
                "# TYPE athena_http_up gauge",
                "athena_http_up 1",
                "# HELP athena_http_ready Local readiness gate.",
                "# TYPE athena_http_ready gauge",
                f"athena_http_ready {1 if readiness.get('ready') else 0}",
                "# HELP athena_http_requests_total HTTP requests observed.",
                "# TYPE athena_http_requests_total counter",
                f"athena_http_requests_total {self.request_count}",
                "# HELP athena_http_rpc_requests_total JSON-RPC requests dispatched.",
                "# TYPE athena_http_rpc_requests_total counter",
                f"athena_http_rpc_requests_total {self.rpc_count}",
                "# HELP athena_http_errors_total Host/probe/dispatch errors.",
                "# TYPE athena_http_errors_total counter",
                f"athena_http_errors_total {self.error_count}",
                "# HELP athena_state_database_bytes Current SQLite file size.",
                "# TYPE athena_state_database_bytes gauge",
                f"athena_state_database_bytes {db_size}",
                "",
            ]
        )

    def close(self) -> None:
        with self.lock:
            self.server.store.close()


class AthenaHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_handler(
    controller: RuntimeController,
    *,
    token: str | None,
    max_body_bytes: int,
):
    body_limit = int(max_body_bytes)
    if body_limit < 1024:
        raise ValueError("max_body_bytes must be at least 1024")

    class Handler(BaseHTTPRequestHandler):
        server_version = "AthenaHTTP/2.0"
        sys_version = ""

        def log_message(self, fmt: str, *args: Any) -> None:
            event = {
                "time": time.time(),
                "remote": self.client_address[0],
                "method": self.command,
                "path": self.path,
                "message": fmt % args,
            }
            sys.stderr.write(json.dumps(event, separators=(",", ":")) + "\n")
            sys.stderr.flush()

        def _security_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

        def _send_json(self, status: int, value: Any) -> None:
            payload = json.dumps(
                value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            self.send_response(status)
            self._security_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)

        def _send_text(self, status: int, value: str, content_type: str) -> None:
            payload = value.encode("utf-8")
            self.send_response(status)
            self._security_headers()
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)

        def _authorized(self) -> bool:
            if token is None:
                return True
            auth = self.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return False
            return hmac.compare_digest(auth[7:], token)

        def do_HEAD(self) -> None:
            self.do_GET()

        def do_GET(self) -> None:
            controller.request_count += 1
            path = self.path.split("?", 1)[0]
            if path == "/livez":
                self._send_json(HTTPStatus.OK, controller.live_snapshot())
            elif path == "/readyz":
                value = controller.readiness_snapshot()
                self._send_json(
                    HTTPStatus.OK if value.get("ready") else HTTPStatus.SERVICE_UNAVAILABLE,
                    value,
                )
            elif path == "/healthz":
                value = controller.health_snapshot()
                self._send_json(
                    HTTPStatus.OK if value.get("status") == "PASS" else HTTPStatus.SERVICE_UNAVAILABLE,
                    value,
                )
            elif path == "/metrics":
                self._send_text(
                    HTTPStatus.OK,
                    controller.metrics_text(),
                    "text/plain; version=0.0.4; charset=utf-8",
                )
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found", "path": path})

        def do_POST(self) -> None:
            controller.request_count += 1
            path = self.path.split("?", 1)[0]
            if path != "/mcp":
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found", "path": path})
                return
            if not self._authorized():
                controller.error_count += 1
                self._send_json(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "unauthorized", "authentication": "Bearer"},
                )
                return
            content_type = self.headers.get("Content-Type", "")
            if not content_type.lower().startswith("application/json"):
                controller.error_count += 1
                self._send_json(
                    HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                    {"error": "content_type_must_be_application_json"},
                )
                return
            raw_length = self.headers.get("Content-Length")
            try:
                length = int(raw_length) if raw_length is not None else -1
            except ValueError:
                length = -1
            if length < 0:
                controller.error_count += 1
                self._send_json(HTTPStatus.LENGTH_REQUIRED, {"error": "valid_content_length_required"})
                return
            if length > body_limit:
                controller.error_count += 1
                self._send_json(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"error": "request_body_too_large", "max_body_bytes": body_limit},
                )
                return
            try:
                payload = self.rfile.read(length)
                value = json.loads(payload.decode("utf-8"))
                if not isinstance(value, dict):
                    raise ValueError("JSON-RPC batch/non-object payloads are unsupported")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                controller.error_count += 1
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {exc}"},
                    },
                )
                return
            response = controller.dispatch(value)
            if response is None:
                self.send_response(HTTPStatus.NO_CONTENT)
                self._security_headers()
                self.end_headers()
                return
            self._send_json(HTTPStatus.OK, response)

    return Handler


def build_http_server(
    controller: RuntimeController,
    *,
    host: str,
    port: int,
    token: str | None,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
) -> AthenaHTTPServer:
    return AthenaHTTPServer(
        (host, int(port)),
        make_handler(controller, token=token, max_body_bytes=max_body_bytes),
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ATHENA bounded JSON-RPC-over-HTTP adapter")
    parser.add_argument("--host", default=os.getenv("ATHENA_HTTP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("ATHENA_HTTP_PORT", "8765")))
    parser.add_argument("--db", default=os.getenv("ATHENA_DB", "./state/athena.db"))
    parser.add_argument("--git-root", default=os.getenv("ATHENA_GIT_ROOT"))
    parser.add_argument("--token", default=os.getenv("ATHENA_HTTP_TOKEN"))
    parser.add_argument("--token-file", default=os.getenv("ATHENA_HTTP_TOKEN_FILE"))
    parser.add_argument("--max-body-bytes", type=int, default=int(os.getenv("ATHENA_HTTP_MAX_BODY_BYTES", str(DEFAULT_MAX_BODY_BYTES))))
    parser.add_argument("--migrate", action="store_true", default=os.getenv("ATHENA_MIGRATE", "").lower() in {"1", "true", "yes"})
    args = parser.parse_args(argv)

    token = _load_token(args.token, args.token_file)
    if not _is_loopback(args.host) and token is None:
        raise SystemExit("non-loopback HTTP binding requires a bearer token")

    controller = RuntimeController(args.db, git_root=args.git_root, migrate=args.migrate)
    server = build_http_server(
        controller,
        host=args.host,
        port=args.port,
        token=token,
        max_body_bytes=args.max_body_bytes,
    )

    stopping = threading.Event()

    def stop(_signum=None, _frame=None):
        if stopping.is_set():
            return
        stopping.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
        controller.close()


if __name__ == "__main__":
    main()
