from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

import athena_mcp.aor_collective_transport_surface as surface
from athena_mcp.tse_forward_port_adapter import (
    BASE_MASTER_HEAD,
    FORWARD_PORT_VERSION,
    SOURCE_HEAD,
)


class TseForwardPortV4Tests(unittest.TestCase):
    def test_current_master_aor_body_is_exact_blob_mirror(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "athena_mcp" / "_aor_collective_transport_surface_master_301547.py"
        proc = subprocess.run(
            ["git", "-C", str(root), "hash-object", str(path)],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("720b749f5d555d45d3be386bf91002fda82b597a", proc.stdout.strip())

    def test_tse_and_current_master_surfaces_are_union_not_replacement(self):
        names = set(surface.AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES)
        for name in (
            "athena_transport_get",
            "athena_party_state",
            "athena_cohesion_matchmake",
            "athena_tse_population_plan",
            "athena_tse_helix_advance",
            "athena_tse_circulation_observe",
        ):
            self.assertIn(name, names)
        uris = set(surface.AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS)
        for uri in (
            "athena://aor-collective/transport",
            "athena://cohesion/mesh/v1",
            "athena://tse-helix/v2",
            "athena://tse-circulation/v1",
        ):
            self.assertIn(uri, uris)

    def test_forward_port_source_manifest_freezes_both_coordinates(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "registry" / "tse_forward_port_v4.json").read_text(encoding="utf-8"))
        self.assertEqual("ATHENA.TSE.FORWARD.PORT.V4", manifest["artifact"])
        self.assertEqual(SOURCE_HEAD, manifest["source"]["qualified_head"])
        self.assertEqual(BASE_MASTER_HEAD, manifest["base"]["master_head"])
        self.assertEqual(FORWARD_PORT_VERSION, manifest["version"])
        self.assertEqual(17, len(manifest["exact_copy_python"]))
        self.assertEqual(6, len(manifest["exact_copy_specs"]))
        self.assertEqual(10, len(manifest["exact_copy_tests"]))
        self.assertEqual("HOLD", manifest["canonical_promotion"])
        self.assertEqual("UNKNOWN", manifest["behavioral_treatment_effect"])

    def test_adapter_declares_integration_only_authority(self):
        self.assertEqual("TSE.FORWARD.PORT.V4", FORWARD_PORT_VERSION)
        self.assertEqual("b486b221be92a141df1afa3e2d895c8cc0e0e1fb", SOURCE_HEAD)
        self.assertEqual("301547b1e2a798013482bab6af1df2ef59a8ee5b", BASE_MASTER_HEAD)


if __name__ == "__main__":
    unittest.main()
