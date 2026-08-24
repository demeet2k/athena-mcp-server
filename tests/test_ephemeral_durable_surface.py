from __future__ import annotations

import unittest

from athena_mcp import protocol
from athena_mcp import aor_development_surface as aor
from athena_mcp.ephemeral_durable_bridge_extension import install_ephemeral_durable_bridge
from athena_mcp.ephemeral_durable_bridge_protocol import (
    EPHEMERAL_DURABLE_RESOURCE,
    EPHEMERAL_DURABLE_TOOL_NAMES,
)


class EphemeralDurableSurfaceTests(unittest.TestCase):
    def test_tool_and_resource_registries_are_mutated_in_place(self):
        protocol_names = {row["name"] for row in protocol.TOOLS}
        aor_names = {row["name"] for row in aor.AOR_DEVELOPMENT_TOOLS}
        self.assertTrue(EPHEMERAL_DURABLE_TOOL_NAMES <= protocol_names)
        self.assertTrue(EPHEMERAL_DURABLE_TOOL_NAMES <= aor_names)
        self.assertTrue(EPHEMERAL_DURABLE_TOOL_NAMES <= aor.AOR_DEVELOPMENT_TOOL_NAMES)
        self.assertIn(EPHEMERAL_DURABLE_RESOURCE["uri"], aor.AOR_DEVELOPMENT_RESOURCE_URIS)
        self.assertIn(
            EPHEMERAL_DURABLE_RESOURCE["uri"],
            {row["uri"] for row in aor.AOR_DEVELOPMENT_RESOURCES},
        )
        self.assertTrue(getattr(aor.AorDevelopmentSurface, "_athena_ephemeral_durable_bridge_v1_registered", False))

    def test_installer_is_idempotent_without_wrapper_or_registry_growth(self):
        before = {
            "init": aor.AorDevelopmentSurface.__init__,
            "call": aor.AorDevelopmentSurface.call_tool,
            "read": aor.AorDevelopmentSurface.read_resource,
            "benchmark": aor.AorDevelopmentSurface.benchmark,
            "tool_len": len(aor.AOR_DEVELOPMENT_TOOLS),
            "resource_len": len(aor.AOR_DEVELOPMENT_RESOURCES),
            "protocol_len": len(protocol.TOOLS),
        }
        install_ephemeral_durable_bridge()
        self.assertIs(aor.AorDevelopmentSurface.__init__, before["init"])
        self.assertIs(aor.AorDevelopmentSurface.call_tool, before["call"])
        self.assertIs(aor.AorDevelopmentSurface.read_resource, before["read"])
        self.assertIs(aor.AorDevelopmentSurface.benchmark, before["benchmark"])
        self.assertEqual(len(aor.AOR_DEVELOPMENT_TOOLS), before["tool_len"])
        self.assertEqual(len(aor.AOR_DEVELOPMENT_RESOURCES), before["resource_len"])
        self.assertEqual(len(protocol.TOOLS), before["protocol_len"])


if __name__ == "__main__":
    unittest.main()
