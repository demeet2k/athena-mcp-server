from __future__ import annotations

import json
import unittest

from athena_mcp.liminal_beacon_mesh_protocol import (
    LIMINAL_BEACON_RESOURCE,
    LIMINAL_BEACON_TOOLS,
    LIMINAL_BEACON_TOOL_NAMES,
    RECEIPT_STAGES,
)


class LiminalBeaconMeshProtocolTests(unittest.TestCase):
    def test_tool_names_unique_and_json_serializable(self):
        self.assertEqual(len(LIMINAL_BEACON_TOOLS), len(LIMINAL_BEACON_TOOL_NAMES))
        json.dumps(LIMINAL_BEACON_TOOLS, sort_keys=True)

    def test_receipt_ladder_preserves_cognition_distinctions(self):
        self.assertEqual(
            ["PRESENTED", "CONSUMED", "INCORPORATED", "DECISION_CHANGED", "PROPAGATED"],
            RECEIPT_STAGES,
        )

    def test_resource_is_explicitly_candidate_liminal_surface(self):
        self.assertEqual("athena://liminal/beacon-mesh", LIMINAL_BEACON_RESOURCE["uri"])
        self.assertIn("Candidate", LIMINAL_BEACON_RESOURCE["name"])


if __name__ == "__main__":
    unittest.main()
