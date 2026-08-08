import json
import unittest
from pathlib import Path

from athena_mcp import kc144_topology as topo


class KC144SeedTests(unittest.TestCase):
    def test_seed_is_bound_to_generator_and_validation(self):
        root = Path(__file__).resolve().parents[1]
        seed = json.loads((root / "spec" / "kc144-topological-command-hub.seed.json").read_text(encoding="utf-8"))
        manifest = topo.manifest(include_edges=False)
        validation = topo.validate_topology()
        self.assertEqual(seed["structural_manifest_digest"], manifest["manifest_digest"])
        self.assertEqual(seed["structural_validation_receipt"], validation["receipt_digest"])
        self.assertEqual(seed["parent_runtime_sha"], topo.PARENT_RUNTIME_SHA)
        self.assertEqual(seed["full_aor_source_sha"], topo.FULL_AOR_SOURCE_SHA)
        self.assertEqual(seed["git_brain_source_sha"], topo.GIT_BRAIN_SOURCE_SHA)

    def test_full_crystal_is_materializable(self):
        crystal = topo.manifest(include_edges=True)
        generated = {item["name"]: item for item in crystal["graphs"] if item["name"] in topo.GRAPH_BUILDERS}
        self.assertEqual(set(generated), set(topo.GRAPH_BUILDERS))
        for name, expected in topo.GRAPH_EXPECTED_COUNTS.items():
            self.assertEqual(len(generated[name]["edges"]), expected)
        self.assertEqual(len(crystal["seats"]), 144)
        self.assertEqual(crystal["readiness"]["promotion"], "HOLD")


if __name__ == "__main__":
    unittest.main()
