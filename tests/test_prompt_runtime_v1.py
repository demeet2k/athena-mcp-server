from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server


class PromptRuntimeV1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "athena-brain"
        self.root.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.name", "fixture")
        self._git("config", "user.email", "fixture@example.com")
        self._install_brain_fixture()
        self._git("add", ".")
        self._git("commit", "-m", "fixture prompt brain")
        self.db = Path(self.tmp.name) / "athena.db"
        self.server = Server(str(self.db), str(self.root))
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

    def _install_brain_fixture(self) -> None:
        manifest = {
            "artifact": "ATHENA.PROMPT.RUNTIME.V1",
            "authority_ceiling": "Repository prompt runtime is below host authority.",
            "bootstrap": "prompts/BOOTSTRAP.md",
            "policy": "policies/PROMPT_RUNTIME.md",
            "active_state": "prompts/state/ACTIVE.json",
            "default_profile": "MAXDEV",
            "profiles": {"MAXDEV": ["core", "git_organism"]},
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
            },
        }
        active = {
            "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
            "prompt_runtime": "ATHENA.PROMPT.RUNTIME.V1",
            "profile": "MAXDEV",
            "enabled_modules": ["core", "git_organism"],
            "active_scoped_overlays": [],
            "revision": 1,
            "status": "ACTIVE",
        }
        self._write("prompts/PROMPT.manifest.json", json.dumps(manifest, indent=2) + "\n")
        self._write("prompts/BOOTSTRAP.md", "# Bootstrap\n")
        self._write("policies/PROMPT_RUNTIME.md", "# Prompt policy witness\n")
        self._write("prompts/state/ACTIVE.json", json.dumps(active, indent=2) + "\n")
        self._write("prompts/ORCHESTRATION_CORE.md", "# Core v1\n")
        self._write("prompts/modules/GIT_ORGANISM.md", "# Git organism\n")

    def rpc(self, method: str, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def tool(self, name: str, arguments: dict):
        response = self.rpc("tools/call", {"name": name, "arguments": arguments})
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def test_surface_exposes_prompt_tools_and_resource(self):
        tools = {row["name"] for row in self.rpc("tools/list")["result"]["tools"]}
        resources = {row["uri"] for row in self.rpc("resources/list")["result"]["resources"]}
        self.assertTrue(
            {
                "athena_prompt_hydrate",
                "athena_prompt_compile",
                "athena_prompt_propose",
                "athena_prompt_experiment",
                "athena_prompt_activate",
                "athena_prompt_promote",
            }
            <= tools
        )
        self.assertIn("athena://prompt/runtime", resources)
        resource = json.loads(
            self.rpc("resources/read", {"uri": "athena://prompt/runtime"})["result"]["contents"][0]["text"]
        )
        self.assertEqual(resource["status"], "READY", resource)
        self.assertIn("host platform/system/developer/current-user", resource["authority_law"])

    def test_hydrate_and_compile_are_exact_head_body_bound_and_deterministic(self):
        head = self._git("rev-parse", "HEAD")
        hydrated = self.tool("athena_prompt_hydrate", {"scope": ["build"]})
        self.assertEqual(hydrated["git"]["head"], head)
        self.assertFalse(hydrated["git"]["dirty"])
        self.assertEqual(hydrated["source_capsule"]["coverage_ratio"], 1.0)
        self.assertTrue(hydrated["source_capsule"]["sealed"])
        self.assertTrue(all(source["body_bound"] for source in hydrated["source_capsule"]["sources"]))
        compiled1 = self.tool("athena_prompt_compile", {"scope": ["build"]})
        compiled2 = self.tool("athena_prompt_compile", {"scope": ["build"]})
        self.assertEqual(compiled1["stack_digest"], compiled2["stack_digest"])
        self.assertEqual(compiled1["compiled_digest"], compiled2["compiled_digest"])
        self.assertIn("# Core v1", compiled1["compiled_text"])
        self.assertIn("repository addendum only", compiled1["compilation_law"])

    def test_missing_manifest_and_dirty_worktree_fail_explicitly(self):
        manifest = self.root / "prompts/PROMPT.manifest.json"
        manifest.rename(manifest.with_suffix(".missing"))
        response = self.rpc(
            "tools/call", {"name": "athena_prompt_hydrate", "arguments": {}}
        )["result"]
        self.assertTrue(response["isError"])
        self.assertIn("DIRTY_GIT_WORKTREE", response["content"][0]["text"])
        manifest.with_suffix(".missing").rename(manifest)
        self._git("reset", "--hard", "HEAD")
        manifest.unlink()
        self._git("add", "-u")
        self._git("commit", "-m", "remove manifest")
        response = self.rpc(
            "tools/call", {"name": "athena_prompt_hydrate", "arguments": {}}
        )["result"]
        self.assertTrue(response["isError"])
        self.assertIn("required prompt body is missing", response["content"][0]["text"])

    def test_full_candidate_experiment_activation_promotion_lifecycle(self):
        head0 = self._git("rev-parse", "HEAD")
        proposal = self.tool(
            "athena_prompt_propose",
            {
                "expected_git_head": head0,
                "module_id": "core",
                "version": "1.1",
                "scope": ["build"],
                "content": "# Core v2\n",
                "defect": "Core lacks an executable continuation boundary.",
                "expected_effect": "Cold continuation compiles deterministically.",
                "metrics": ["cold_reconstruction"],
                "tests": ["cold-start replay"],
                "rollback": "git revert the promotion commit",
                "depends_on": ["git_organism"],
                "triggers": ["NEXT"],
                "actor": "athena-test",
            },
        )
        candidate_path = proposal["candidate_path"]
        self.assertTrue((self.root / candidate_path).is_file())
        self.assertEqual(proposal["status"], "CANDIDATE")
        head1 = proposal["commit"]["head"]

        stale = self.rpc(
            "tools/call",
            {
                "name": "athena_prompt_propose",
                "arguments": {
                    "expected_git_head": head0,
                    "module_id": "core",
                    "version": "1.2",
                    "scope": ["build"],
                    "content": "stale",
                    "defect": "stale",
                    "expected_effect": "stale",
                    "metrics": ["m"],
                    "tests": ["t"],
                    "rollback": "revert",
                },
            },
        )["result"]
        self.assertTrue(stale["isError"])
        self.assertEqual(stale["structuredContent"]["status"], "STALE_GIT_HEAD")

        experiment = self.tool(
            "athena_prompt_experiment",
            {
                "expected_git_head": head1,
                "experiment_id": "core-v2-pass",
                "candidate_path": candidate_path,
                "hypothesis": "v2 improves cold continuation",
                "protocol": {"method": "cold-start", "samples": 1},
                "result_status": "PASSED",
                "observations": [{"metric": "cold_reconstruction", "value": 1.0}],
                "witness": {"kind": "local-test", "command": "fixture"},
                "actor": "athena-test",
            },
        )
        head2 = experiment["commit"]["head"]

        activation = self.tool(
            "athena_prompt_activate",
            {
                "expected_git_head": head2,
                "candidate_path": candidate_path,
                "scope": ["build"],
                "experiment_refs": [experiment["experiment_path"]],
                "witness": {
                    "authority": "maintainer-test",
                    "decision": "ACTIVATE_SCOPED",
                    "approved_by": "fixture",
                },
                "actor": "athena-test",
            },
        )
        head3 = activation["commit"]["head"]
        changed = self._git(
            "diff-tree", "--no-commit-id", "--name-only", "-r", head3
        ).splitlines()
        self.assertEqual(changed, ["prompts/state/ACTIVE.json"])
        scoped = self.tool("athena_prompt_compile", {"scope": ["build"]})
        unscoped = self.tool("athena_prompt_compile", {"scope": ["research"]})
        self.assertIn("# Core v2", scoped["compiled_text"])
        self.assertTrue(scoped["applicable_overlays"])
        self.assertFalse(unscoped["applicable_overlays"])

        promoted = self.tool(
            "athena_prompt_promote",
            {
                "expected_git_head": head3,
                "candidate_path": candidate_path,
                "target_module_id": "core",
                "experiment_refs": [experiment["experiment_path"]],
                "evidence_refs": ["policies/PROMPT_RUNTIME.md"],
                "witness": {
                    "authority": "maintainer-test",
                    "decision": "PROMOTE",
                    "approved_by": "fixture",
                },
                "actor": "athena-test",
            },
        )
        self.assertTrue(promoted["candidate_preserved"])
        self.assertEqual((self.root / "prompts/ORCHESTRATION_CORE.md").read_text(), "# Core v2\n")
        state = json.loads((self.root / "prompts/state/ACTIVE.json").read_text())
        self.assertEqual(state["active_scoped_overlays"], [])
        self.assertEqual(promoted["removed_scoped_overlays"], 1)
        self.assertFalse(promoted["commit"]["push_performed"])

    def test_experiment_cannot_claim_observation_without_witness(self):
        head = self._git("rev-parse", "HEAD")
        proposal = self.tool(
            "athena_prompt_propose",
            {
                "expected_git_head": head,
                "module_id": "core",
                "version": "1.1",
                "scope": ["build"],
                "content": "# candidate\n",
                "defect": "d",
                "expected_effect": "e",
                "metrics": ["m"],
                "tests": ["t"],
                "rollback": "revert",
            },
        )
        response = self.rpc(
            "tools/call",
            {
                "name": "athena_prompt_experiment",
                "arguments": {
                    "expected_git_head": proposal["commit"]["head"],
                    "experiment_id": "fake-pass",
                    "candidate_path": proposal["candidate_path"],
                    "hypothesis": "h",
                    "protocol": {"method": "none"},
                    "result_status": "PASSED",
                    "observations": [{"metric": "m", "value": 1}],
                },
            },
        )["result"]
        self.assertTrue(response["isError"])
        self.assertIn("execution witness", response["content"][0]["text"])

    def test_candidate_base_digest_blocks_stale_canonical_promotion(self):
        head = self._git("rev-parse", "HEAD")
        proposal = self.tool(
            "athena_prompt_propose",
            {
                "expected_git_head": head,
                "module_id": "core",
                "version": "1.1",
                "scope": ["build"],
                "content": "# candidate\n",
                "defect": "d",
                "expected_effect": "e",
                "metrics": ["m"],
                "tests": ["t"],
                "rollback": "revert",
            },
        )
        experiment = self.tool(
            "athena_prompt_experiment",
            {
                "expected_git_head": proposal["commit"]["head"],
                "experiment_id": "pass",
                "candidate_path": proposal["candidate_path"],
                "hypothesis": "h",
                "protocol": {"method": "fixture"},
                "result_status": "PASSED",
                "observations": [{"metric": "m", "value": 1}],
                "witness": {"kind": "fixture"},
            },
        )
        self._write("prompts/ORCHESTRATION_CORE.md", "# intervening canonical change\n")
        self._git("add", "prompts/ORCHESTRATION_CORE.md")
        self._git("commit", "-m", "intervening canonical change")
        current = self._git("rev-parse", "HEAD")
        response = self.rpc(
            "tools/call",
            {
                "name": "athena_prompt_promote",
                "arguments": {
                    "expected_git_head": current,
                    "candidate_path": proposal["candidate_path"],
                    "target_module_id": "core",
                    "experiment_refs": [experiment["experiment_path"]],
                    "evidence_refs": ["policies/PROMPT_RUNTIME.md"],
                    "witness": {
                        "authority": "maintainer-test",
                        "decision": "PROMOTE",
                        "approved_by": "fixture",
                    },
                },
            },
        )["result"]
        self.assertTrue(response["isError"])
        self.assertIn("STALE_PROMPT_BASE", response["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
