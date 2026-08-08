from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server


class PromptRuntimeSelectionV1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "athena-brain"
        self.root.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.name", "fixture")
        self._git("config", "user.email", "fixture@example.com")
        self._install_fixture()
        self._git("add", ".")
        self._git("commit", "-m", "fixture selector prompt brain")
        self.server = Server(str(Path(self.tmp.name) / "one.db"), str(self.root))
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.cleanup()

    def _git(self, *args: str) -> str:
        process = subprocess.run(
            ["git", "-C", str(self.root), *args], text=True, capture_output=True
        )
        if process.returncode:
            raise AssertionError(process.stderr or process.stdout)
        return process.stdout.strip()

    def _write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _install_fixture(self) -> None:
        manifest = {
            "artifact": "ATHENA.PROMPT.RUNTIME.V1",
            "authority_ceiling": "Repository prompt runtime is below host authority.",
            "bootstrap": "prompts/BOOTSTRAP.md",
            "policy": "policies/PROMPT_RUNTIME.md",
            "active_state": "prompts/state/ACTIVE.json",
            "default_profile": "BUILD",
            "profiles": {
                "BUILD": ["core", "git_organism"],
                "MAXDEV": [
                    "core",
                    "git_organism",
                    "navigation_support",
                    "crystal_navigation",
                ],
            },
            "modules": {
                "core": {
                    "path": "prompts/ORCHESTRATION_CORE.md",
                    "order": 0,
                    "mandatory": True,
                },
                "git_organism": {
                    "path": "prompts/modules/GIT_ORGANISM.md",
                    "order": 10,
                    "mandatory": True,
                },
                "navigation_support": {
                    "path": "prompts/modules/NAVIGATION_SUPPORT.md",
                    "order": 15,
                },
                "crystal_navigation": {
                    "path": "prompts/modules/CRYSTAL_NAVIGATION.md",
                    "order": 20,
                    "selectors": ["graph", "navigation", "KC144"],
                    "depends_on": ["navigation_support"],
                },
            },
        }
        active = {
            "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
            "prompt_runtime": "ATHENA.PROMPT.RUNTIME.V1",
            "profile": "BUILD",
            "enabled_modules": ["core", "git_organism"],
            "active_scoped_overlays": [],
            "goal_refs": ["github://demeet2k/Athena/issues/153"],
            "pressure_refs": ["git://prompt-runtime-v1"],
            "work_refs": ["prompts/workorders/P0.json"],
            "revision": 1,
            "status": "ACTIVE",
        }
        self._write("prompts/PROMPT.manifest.json", json.dumps(manifest, indent=2) + "\n")
        self._write("prompts/BOOTSTRAP.md", "# Bootstrap\n")
        self._write("policies/PROMPT_RUNTIME.md", "# Prompt policy witness\n")
        self._write("prompts/state/ACTIVE.json", json.dumps(active, indent=2) + "\n")
        self._write("prompts/ORCHESTRATION_CORE.md", "# Core\n")
        self._write("prompts/modules/GIT_ORGANISM.md", "# Git organism\n")
        self._write("prompts/modules/NAVIGATION_SUPPORT.md", "# Navigation support\n")
        self._write("prompts/modules/CRYSTAL_NAVIGATION.md", "# Crystal navigation\n")

    def rpc(self, method: str, params=None, *, server: Server | None = None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return (server or self.server).handle(message)

    def tool(self, name: str, arguments: dict, *, server: Server | None = None):
        response = self.rpc(
            "tools/call", {"name": name, "arguments": arguments}, server=server
        )
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def test_selector_dependency_order_and_frontier_are_deterministic(self):
        plain = self.tool(
            "athena_prompt_compile",
            {"profile": "BUILD", "task": "triage email", "scope": ["build"]},
        )
        graph_one = self.tool(
            "athena_prompt_compile",
            {
                "profile": "BUILD",
                "task": "deep graph navigation",
                "scope": ["build"],
            },
        )
        graph_two = self.tool(
            "athena_prompt_compile",
            {
                "profile": "BUILD",
                "task": "deep graph navigation",
                "scope": ["build"],
            },
        )
        self.assertEqual(
            plain["selection"]["selected_modules"], ["core", "git_organism"]
        )
        self.assertEqual(
            graph_one["selection"]["selected_modules"],
            ["core", "git_organism", "navigation_support", "crystal_navigation"],
        )
        self.assertIn(
            "SELECTOR:graph",
            graph_one["selection"]["selection_reasons"]["crystal_navigation"],
        )
        self.assertIn(
            "DEPENDENCY_OF:crystal_navigation",
            graph_one["selection"]["selection_reasons"]["navigation_support"],
        )
        self.assertEqual(graph_one["compiled_digest"], graph_two["compiled_digest"])
        self.assertEqual(graph_one["stack_digest"], graph_two["stack_digest"])
        self.assertEqual(graph_one["frontier_refs"]["status"], "DECLARED")
        self.assertEqual(
            graph_one["frontier_refs"]["goals"],
            ["github://demeet2k/Athena/issues/153"],
        )

    def test_same_order_collision_is_typed_conflict_not_silent_concatenation(self):
        path = self.root / "prompts/PROMPT.manifest.json"
        manifest = json.loads(path.read_text())
        manifest["modules"]["crystal_navigation"]["order"] = 10
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self._git("add", "prompts/PROMPT.manifest.json")
        self._git("commit", "-m", "introduce order conflict")
        response = self.rpc(
            "tools/call",
            {
                "name": "athena_prompt_compile",
                "arguments": {
                    "profile": "BUILD",
                    "task": "graph",
                    "scope": ["build"],
                },
            },
        )["result"]
        self.assertTrue(response["isError"])
        self.assertIn("PROMPT_ORDER_CONFLICT", response["content"][0]["text"])

    def test_two_sessions_rehydrate_from_shared_git_without_hidden_chat_state(self):
        second = Server(str(Path(self.tmp.name) / "two.db"), str(self.root))
        try:
            first = self.tool("athena_prompt_hydrate", {}, server=self.server)
            second_initial = self.tool("athena_prompt_hydrate", {}, server=second)
            self.assertEqual(first["git"]["head"], second_initial["git"]["head"])
            self.assertEqual(first["stack_digest"], second_initial["stack_digest"])

            proposal = self.tool(
                "athena_prompt_propose",
                {
                    "expected_git_head": first["git"]["head"],
                    "module_id": "core",
                    "version": "1.1",
                    "scope": ["build"],
                    "content": "# Core candidate\n",
                    "defect": "Cold agents lack one tested candidate.",
                    "expected_effect": "The shared Git descendant becomes visible cross-session.",
                    "metrics": ["cross_session_visibility"],
                    "tests": ["freshness invalidation"],
                    "rollback": "git revert the proposal commit",
                    "actor": "session-one",
                },
                server=self.server,
            )
            freshness = self.tool(
                "athena_prompt_freshness",
                {"last_git_head": second_initial["git"]["head"]},
                server=second,
            )
            self.assertEqual(freshness["status"], "STALE")
            self.assertTrue(freshness["rehydration_required"])
            changed = [
                path
                for row in freshness["changed_files"]
                for path in row["paths"]
            ]
            self.assertIn(proposal["candidate_path"], changed)

            second_rehydrated = self.tool(
                "athena_prompt_hydrate",
                {"since_git_head": second_initial["git"]["head"]},
                server=second,
            )
            self.assertEqual(
                second_rehydrated["git"]["head"], proposal["commit"]["head"]
            )
            self.assertNotEqual(
                second_rehydrated["stack_digest"], second_initial["stack_digest"]
            )
        finally:
            second.store.close()

    def test_freshness_tool_is_discoverable_and_current_head_is_fresh(self):
        tools = {row["name"] for row in self.rpc("tools/list")["result"]["tools"]}
        self.assertIn("athena_prompt_freshness", tools)
        head = self._git("rev-parse", "HEAD")
        fresh = self.tool("athena_prompt_freshness", {"last_git_head": head})
        self.assertEqual(fresh["status"], "FRESH")
        self.assertFalse(fresh["rehydration_required"])


if __name__ == "__main__":
    unittest.main()
