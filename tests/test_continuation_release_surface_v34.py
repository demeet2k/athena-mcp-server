import json
import tempfile
import unittest
from pathlib import Path

from athena_mcp.continuation_raw_observer_manifest import OBSERVER_ORGAN_ID, OBSERVER_TOOL
from athena_mcp.server import Server


ROOT = Path(__file__).resolve().parents[1]


class ContinuationReleaseSurfaceV34Tests(unittest.TestCase):
    def test_current_distribution_requires_the_observer_surface(self):
        manifest = json.loads((ROOT / "release" / "v3.4.0.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.4.0")
        self.assertEqual(manifest["runtime"]["manifest"], "ATHENA.RUNTIME.UNIFIED.11")
        self.assertIn(OBSERVER_TOOL, manifest["runtime"]["required_tools"])
        gates = "\n".join(manifest["gates"])
        self.assertIn("continuation raw-observer", gates)
        boundaries = "\n".join(manifest["authority_boundaries"])
        self.assertIn("raw observer exports tracked runtime facts only", boundaries)
        self.assertIn("does not convert those facts into assay classifications", boundaries)

    def test_release_notes_expose_observer_and_claim_ceiling(self):
        notes = (ROOT / "release" / "v3.4.0.md").read_text(encoding="utf-8")
        for phrase in (
            "Continuation raw-observation organ",
            "athena_continuation_raw_trace",
            "RAW_TRACE != ASSAY_CLASSIFICATION",
            "RAW_RUNTIME_FACT != BEHAVIORAL_EFFECT",
            "EXACT_BYTE_DIGEST != CANONICAL_RECORD_DIGEST",
            "READ_ONLY_OBSERVER != CONTROLLER",
            "V3.3 release reproduction/publication is now manual-only",
        ):
            self.assertIn(phrase, notes)

    def test_live_v34_source_surface_matches_distribution_requirement(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".db")
        server = Server(tmp.name)
        try:
            tools = {
                item["name"]
                for item in server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
            }
            self.assertIn(OBSERVER_TOOL, tools)
            response = server.handle(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "athena_runtime_manifest", "arguments": {}},
                }
            )
            self.assertFalse(response["result"].get("isError"), response)
            manifest = response["result"]["structuredContent"]
            self.assertEqual(manifest["artifact"], "ATHENA.RUNTIME.UNIFIED.11")
            self.assertIn(OBSERVER_ORGAN_ID, manifest["organs"])
            self.assertEqual(manifest["organs"][OBSERVER_ORGAN_ID]["tool"], OBSERVER_TOOL)
            self.assertFalse(any(manifest["organs"][OBSERVER_ORGAN_ID]["authority"].values()))
        finally:
            server.store.close()
            tmp.close()


if __name__ == "__main__":
    unittest.main()
