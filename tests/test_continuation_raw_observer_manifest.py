import json
import tempfile
import unittest

from athena_mcp.continuation_raw_observer_manifest import (
    OBSERVER_ARTIFACT,
    OBSERVER_LAWS,
    OBSERVER_ORGAN_ID,
    OBSERVER_TOOL,
)
from athena_mcp.server import Server


class ContinuationRawObserverManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def tool(self, name, args=None):
        response = self.rpc("tools/call", {"name": name, "arguments": args or {}})
        self.assertFalse(response["result"].get("isError"), response)
        return response["result"]["structuredContent"]

    def read_json(self, uri):
        return json.loads(
            self.rpc("resources/read", {"uri": uri})["result"]["contents"][0]["text"]
        )

    def assert_observer_organ(self, manifest):
        self.assertEqual(manifest["artifact"], "ATHENA.RUNTIME.UNIFIED.11")
        self.assertIn(OBSERVER_ORGAN_ID, manifest["organs"])
        organ = manifest["organs"][OBSERVER_ORGAN_ID]
        self.assertEqual(organ["artifact"], OBSERVER_ARTIFACT)
        self.assertEqual(organ["tool"], OBSERVER_TOOL)
        self.assertEqual(organ["standing"], "RAW_RUNTIME_FACTS")
        self.assertEqual(organ["mode"], "READ_ONLY")
        self.assertEqual(
            organ["source_namespaces"],
            [
                "prompts/rehydration/*/receipts/*.json",
                "prompts/rehydration/*/events/*.json",
                "runtime/message_board/v1/events/**/*.json",
            ],
        )
        self.assertEqual(
            organ["identity"]["record_sha256"],
            "exact persisted source bytes",
        )
        self.assertEqual(
            organ["identity"]["record_canonical_sha256"],
            "canonical decoded record",
        )
        for key in ("classification", "behavioral_effect", "causal_effect", "promotion", "mutation"):
            self.assertIs(organ["authority"][key], False, key)
        for law in OBSERVER_LAWS:
            self.assertIn(law, organ["laws"])
            self.assertIn(law, manifest["invariants"])

    def test_tool_registry_manifest_tool_and_both_manifest_resources_commute(self):
        names = {tool["name"] for tool in self.rpc("tools/list")["result"]["tools"]}
        self.assertIn(OBSERVER_TOOL, names)

        tool_manifest = self.tool("athena_runtime_manifest")
        runtime_resource = self.read_json("athena://runtime/unified-manifest")
        canonical_resource = self.read_json("athena://manifest")
        for manifest in (tool_manifest, runtime_resource, canonical_resource):
            self.assert_observer_organ(manifest)

        self.assertEqual(
            tool_manifest["organs"][OBSERVER_ORGAN_ID],
            runtime_resource["organs"][OBSERVER_ORGAN_ID],
        )
        self.assertEqual(
            tool_manifest["organs"][OBSERVER_ORGAN_ID],
            canonical_resource["organs"][OBSERVER_ORGAN_ID],
        )

    def test_self_model_does_not_upgrade_raw_observer_authority(self):
        manifest = self.tool("athena_runtime_manifest")
        organ = manifest["organs"][OBSERVER_ORGAN_ID]
        joined = "\n".join(manifest["invariants"])
        self.assertIn("RAW_RUNTIME_FACT != BEHAVIORAL_EFFECT", joined)
        self.assertIn("READ_ONLY_OBSERVER != CONTROLLER", joined)
        self.assertNotIn('"behavioral_effect": true', json.dumps(organ).lower())
        self.assertFalse(any(organ["authority"].values()))


if __name__ == "__main__":
    unittest.main()
