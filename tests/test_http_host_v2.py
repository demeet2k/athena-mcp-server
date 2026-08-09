import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from athena_mcp.http_host import (
    MIN_TOKEN_BYTES,
    RuntimeController,
    _load_token,
    build_http_server,
)
from athena_mcp.protocol import SERVER_INFO


class HTTPHostV2Tests(unittest.TestCase):
    def test_token_contract(self):
        with self.assertRaises(ValueError):
            _load_token("x" * (MIN_TOKEN_BYTES - 1), None)
        token = "x" * MIN_TOKEN_BYTES
        self.assertEqual(_load_token(token, None), token)

    def test_authenticated_rpc_health_and_persistent_restart(self):
        token = "deployment-test-token-1234567890"
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "athena.db")
            controller = RuntimeController(db, migrate=True, readiness_cache_seconds=0)
            server = build_http_server(
                controller,
                host="127.0.0.1",
                port=0,
                token=token,
                max_body_bytes=8192,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"

            def post(message):
                request = Request(
                    base + "/mcp",
                    data=json.dumps(message).encode(),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    method="POST",
                )
                return json.loads(urlopen(request, timeout=5).read())

            try:
                live = json.loads(urlopen(base + "/livez", timeout=5).read())
                self.assertEqual(live["status"], "LIVE")
                self.assertEqual(live["version"], "ATHENA.JSONRPC.HTTP.ADAPTER.2")

                initialize_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-11-25"},
                }
                unauthenticated = Request(
                    base + "/mcp",
                    data=json.dumps(initialize_message).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(HTTPError) as raised:
                    urlopen(unauthenticated, timeout=5)
                self.assertEqual(raised.exception.code, 401)

                initialized = post(initialize_message)
                self.assertEqual(initialized["result"]["serverInfo"], SERVER_INFO)
                deployment = post(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_deployment_manifest",
                            "arguments": {},
                        },
                    }
                )
                self.assertFalse(deployment["result"]["isError"], deployment)
                self.assertEqual(
                    deployment["result"]["structuredContent"]["version"],
                    "ATHENA.DEPLOYMENT.2",
                )
                metrics = urlopen(base + "/metrics", timeout=5).read().decode()
                self.assertIn("athena_http_rpc_requests_total 2", metrics)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
                controller.close()

            self.assertTrue(Path(db).is_file())
            reopened = RuntimeController(db, migrate=False, readiness_cache_seconds=0)
            try:
                self.assertEqual(reopened._schema_verification()["status"], "PASS")
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
