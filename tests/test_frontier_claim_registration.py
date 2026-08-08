from __future__ import annotations

import importlib
import unittest


class FrontierClaimRegistrationTests(unittest.TestCase):
    def test_server_bootstrap_exposes_claim_prepare_tools_through_dispatch(self):
        # The supported console entrypoint is athena_mcp.server:main. Importing
        # server imports bootstrap before dispatch, so bootstrap's additive
        # registration must mutate the same frontier/prompt tool registries that
        # dispatch later publishes through protocol.TOOLS.
        server = importlib.import_module("athena_mcp.server")
        frontier_runtime = importlib.import_module("athena_mcp.frontier_runtime")
        prompt_runtime = importlib.import_module("athena_mcp.prompt_runtime")
        protocol = importlib.import_module("athena_mcp.protocol")
        dispatch = importlib.import_module("athena_mcp.dispatch")

        expected = {
            "athena_frontier_provider_status",
            "athena_frontier_claim_prepare",
        }
        self.assertTrue(expected.issubset(frontier_runtime.FRONTIER_TOOL_NAMES))
        self.assertTrue(expected.issubset(prompt_runtime.PROMPT_RUNTIME_TOOL_NAMES))
        self.assertTrue(expected.issubset({tool["name"] for tool in frontier_runtime.FRONTIER_TOOLS}))
        self.assertTrue(expected.issubset({tool["name"] for tool in prompt_runtime.PROMPT_RUNTIME_TOOLS}))
        self.assertTrue(expected.issubset({tool["name"] for tool in protocol.TOOLS}))
        self.assertIsNotNone(dispatch)
        self.assertIsNotNone(server)

    def test_registration_keeps_legacy_frontier_tools(self):
        import athena_mcp.server  # noqa: F401 - triggers canonical bootstrap registration
        from athena_mcp.frontier_runtime import FRONTIER_TOOL_NAMES

        self.assertTrue(
            {
                "athena_frontier_hydrate",
                "athena_frontier_freshness",
                "athena_frontier_select",
                "athena_frontier_provider_status",
                "athena_frontier_claim_prepare",
            }.issubset(FRONTIER_TOOL_NAMES)
        )


if __name__ == "__main__":
    unittest.main()
