import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from athena_mcp.http_host import RuntimeController, build_http_server


class HTTPHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.controller = RuntimeController(
            str(Path(self.temp.name) / "athena.db"), migrate=True, readiness_cache_seconds=0
        )
        self.token = "test-token-with-at-least-sixteen-bytes"
        self.httpd = build_http_server(
            self.controller,
            host="127.0.0.1",
            port=0,
            token=self.token,
            max_body_bytes=1024,
        )
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.httpd.server_address
        self.base = f"http://{host}:{port}"

    def tearDown(self):
        self.httpd.shutdown()
        self.thread.join(timeout=5)
        self.httpd.server_close()
        self.controller.close()
        self.temp.cleanup()

    def _json(self, path):
        with urllib.request.urlopen(self.base + path, timeout=20) as response:
            return response.status, json.loads(response.read())

    def _rpc(self, payload, *, token=None):
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(
            self.base + "/mcp",
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())

    def test_liveness_readiness_and_metrics(self):
        status, live = self._json("/livez")
        self.assertEqual(status, 200)
        self.assertEqual(live["status"], "LIVE")
        status, ready = self._json("/readyz")
        self.assertEqual(status, 200)
        self.assertTrue(ready["ready"])
        with urllib.request.urlopen(self.base + "/metrics", timeout=20) as response:
            metrics = response.read().decode()
        self.assertIn("athena_http_ready 1", metrics)
        self.assertIn("athena_http_requests_total", metrics)

    def test_rpc_requires_bearer_and_initializes_composed_hub(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-11-25"},
        }
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._rpc(payload)
        self.assertEqual(ctx.exception.code, 401)
        status, result = self._rpc(payload, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(result["result"]["serverInfo"]["version"], "3.1.0")
        self.assertEqual(
            result["result"]["serverInfo"]["httpAdapter"],
            "ATHENA.JSONRPC.HTTP.ADAPTER.1",
        )

    def test_body_limit_and_content_type_fail_closed(self):
        oversized = urllib.request.Request(
            self.base + "/mcp",
            data=b"{" + b" " * 2048 + b"}",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token,
            },
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(oversized, timeout=20)
        self.assertEqual(ctx.exception.code, 413)
        wrong_type = urllib.request.Request(
            self.base + "/mcp",
            data=b"{}",
            headers={
                "Content-Type": "text/plain",
                "Authorization": "Bearer " + self.token,
            },
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(wrong_type, timeout=20)
        self.assertEqual(ctx.exception.code, 415)


if __name__ == "__main__":
    unittest.main()
