from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "athena_mcp" / "campaign_v3_life_binding.py"
TRANSPORT_SURFACE = ROOT / "athena_mcp" / "aor_collective_transport_surface.py"
SPEC = ROOT / "spec" / "CAMPAIGN_V3_LIFE_QUEST_PACKET_V1.json"

FORBIDDEN_RUNTIME_OWNERSHIP_PATHS = (
    ROOT / "athena_mcp" / "stay_in_game_life_loop.py",
    ROOT / "athena_mcp" / "stay_in_game_life_loop_protocol.py",
)
FORBIDDEN_LIFE_TRANSITION_TOOLS = (
    "athena_life_world_new",
    "athena_life_agent_enter",
    "athena_life_resolve",
)
FORBIDDEN_COMPILER_SYMBOLS = {
    "new_world",
    "enter_agent",
    "resolve_attempt",
    "StayInGameLifeLoopRuntime",
}


class CampaignV3LifeBindingOwnershipTests(unittest.TestCase):
    def test_runtime_does_not_copy_the_semantic_life_reducer(self) -> None:
        for path in FORBIDDEN_RUNTIME_OWNERSHIP_PATHS:
            self.assertFalse(
                path.exists(),
                f"runtime must not own a second executable Life Loop state machine: {path.relative_to(ROOT)}",
            )

    def test_packet_compiler_has_no_life_transition_implementation(self) -> None:
        source = COMPILER.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported_modules: list[str] = []
        defined_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported_modules.append(node.module or "")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined_names.add(node.name)

        self.assertFalse(
            any("stay_in_game_life_loop" in module for module in imported_modules),
            "pure Campaign packet compiler must not import a runtime-owned Life reducer",
        )
        self.assertEqual(set(), defined_names & FORBIDDEN_COMPILER_SYMBOLS)

    def test_collective_transport_does_not_expose_life_transition_tools(self) -> None:
        surface = TRANSPORT_SURFACE.read_text(encoding="utf-8")
        for tool_name in FORBIDDEN_LIFE_TRANSITION_TOOLS:
            self.assertNotIn(tool_name, surface)

    def test_contract_explicitly_defers_stateful_play_to_life_loop(self) -> None:
        spec = SPEC.read_text(encoding="utf-8")
        self.assertIn('"freshness_rechecked_at_play": true', spec)
        self.assertIn('"consumption_deferred_to_life_loop": true', spec)
        self.assertIn('"issuance_eligible_at_compile": false', spec)
        self.assertIn('"reward_issued_at_compile": false', spec)


if __name__ == "__main__":
    unittest.main()
