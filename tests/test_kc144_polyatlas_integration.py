import json
import tempfile
import unittest

from athena_mcp.hub_server import HubServer


class KC144PolyatlasIntegrationTests(unittest.TestCase):
    def test_polyatlas_is_live_on_composed_mcp_surface(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as handle:
            server = HubServer(handle.name)
            names = {item["name"] for item in server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
            expected = {
                "athena_kc144_polyatlas_status", "athena_kc144_polyatlas_manifest",
                "athena_kc144_polyatlas_seat", "athena_kc144_polyatlas_rosetta",
                "athena_kc144_resolution_transport", "athena_kc144_resolution_family",
                "athena_kc144_sphere_atlas", "athena_kc144_polyatlas_route",
                "athena_kc144_polyatlas_validate",
            }
            self.assertLessEqual(expected, names)
            uris = {item["uri"] for item in server.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})["result"]["resources"]}
            expected_uris = {f"athena://kc144/polyatlas/{name}" for name in ("status", "manifest", "sources", "sphere", "family", "validation")}
            self.assertLessEqual(expected_uris, uris)

            def call(identifier, name, arguments):
                reply = server.handle({"jsonrpc": "2.0", "id": identifier, "method": "tools/call", "params": {"name": name, "arguments": arguments}})["result"]
                self.assertFalse(reply.get("isError"), reply)
                return reply["structuredContent"]

            receipt = call(3, "athena_kc144_polyatlas_validate", {"include_details": False})
            self.assertEqual(receipt["status"], "PASS")
            rosetta = call(4, "athena_kc144_polyatlas_rosetta", {"chapter": 14, "shelf": 14, "target_resolution": 21})
            self.assertEqual(rosetta["coordinates"]["C06"]["six_trit"], "111111")
            self.assertEqual(rosetta["coordinates"]["C07"]["gid729"], 365)
            self.assertEqual(rosetta["coordinates"]["C15"]["exact_station"], 11)
            resource = server.handle({"jsonrpc": "2.0", "id": 5, "method": "resources/read", "params": {"uri": "athena://kc144/polyatlas/status"}})["result"]
            self.assertEqual(json.loads(resource["contents"][0]["text"])["version"], "KC144.POLYATLAS.1.0.0")
            server.store.close()


if __name__ == "__main__":
    unittest.main()
