from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(root), *args], text=True, capture_output=True
    )
    if process.returncode:
        raise AssertionError(process.stderr or process.stdout)
    return process.stdout.strip()


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PromptRuntimeRemoteV1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.agent_a = base / "agent-a"
        self.agent_a.mkdir()
        _run(self.agent_a, "init", "-b", "main")
        _run(self.agent_a, "config", "user.name", "agent-a")
        _run(self.agent_a, "config", "user.email", "agent-a@example.invalid")
        self._install_brain(self.agent_a)
        _run(self.agent_a, "add", ".")
        _run(self.agent_a, "commit", "-m", "seed shared prompt brain")

        self.origin = base / "origin.git"
        process = subprocess.run(
            ["git", "init", "--bare", str(self.origin)],
            text=True,
            capture_output=True,
        )
        if process.returncode:
            raise AssertionError(process.stderr or process.stdout)
        _run(self.agent_a, "remote", "add", "origin", str(self.origin))
        _run(self.agent_a, "push", "-u", "origin", "HEAD:main")

        self.agent_b = base / "agent-b"
        process = subprocess.run(
            ["git", "clone", "-b", "main", str(self.origin), str(self.agent_b)],
            text=True,
            capture_output=True,
        )
        if process.returncode:
            raise AssertionError(process.stderr or process.stdout)
        _run(self.agent_b, "config", "user.name", "agent-b")
        _run(self.agent_b, "config", "user.email", "agent-b@example.invalid")

        self.server_a = Server(str(base / "agent-a.db"), str(self.agent_a))
        self.server_b = Server(str(base / "agent-b.db"), str(self.agent_b))
        self.seq = 0

    def tearDown(self):
        self.server_a.store.close()
        self.server_b.store.close()
        self.tmp.cleanup()

    @staticmethod
    def _install_brain(root: Path) -> None:
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
        _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest, indent=2) + "\n")
        _write(root, "prompts/BOOTSTRAP.md", "# Bootstrap\n")
        _write(root, "policies/PROMPT_RUNTIME.md", "# Prompt policy\n")
        _write(root, "prompts/state/ACTIVE.json", json.dumps(active, indent=2) + "\n")
        _write(root, "prompts/ORCHESTRATION_CORE.md", "# Core\n")
        _write(root, "prompts/modules/GIT_ORGANISM.md", "# Git organism\n")

    def rpc(self, server: Server, method: str, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server: Server, name: str, arguments: dict):
        response = self.rpc(
            server, "tools/call", {"name": name, "arguments": arguments}
        )
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def test_hydrate_is_network_silent_and_explicit_sync_fast_forwards(self):
        initial_a = _run(self.agent_a, "rev-parse", "HEAD")
        _write(self.agent_b, "prompts/shared-note.md", "agent-b learning\n")
        _run(self.agent_b, "add", ".")
        _run(self.agent_b, "commit", "-m", "agent b learning")
        shared_head = _run(self.agent_b, "rev-parse", "HEAD")
        _run(self.agent_b, "push", "origin", "main")

        hydrated = self.tool(self.server_a, "athena_prompt_hydrate", {})
        self.assertEqual(hydrated["git"]["head"], initial_a)
        self.assertEqual(_run(self.agent_a, "rev-parse", "HEAD"), initial_a)
        self.assertFalse((self.agent_a / "prompts/shared-note.md").exists())

        observed = self.tool(
            self.server_a,
            "athena_prompt_remote_status",
            {"fetch": False},
        )
        self.assertFalse(observed["remote_checked"])
        self.assertFalse(observed["shared_frontier_verified"])

        synced = self.tool(
            self.server_a,
            "athena_prompt_sync",
            {"expected_git_head": initial_a},
        )
        self.assertEqual(synced["status"], "FAST_FORWARDED_SHARED")
        self.assertTrue(synced["shared_frontier_verified"])
        self.assertEqual(_run(self.agent_a, "rev-parse", "HEAD"), shared_head)
        self.assertEqual(
            (self.agent_a / "prompts/shared-note.md").read_text(),
            "agent-b learning\n",
        )

    def test_local_candidate_requires_explicit_publish_then_sibling_sync(self):
        origin_before = _run(self.origin, "rev-parse", "refs/heads/main")
        proposal = self.tool(
            self.server_a,
            "athena_prompt_propose",
            {
                "expected_git_head": origin_before,
                "module_id": "core",
                "version": "1.1",
                "scope": ["build"],
                "content": "# Core candidate\n",
                "defect": "Agents rediscover one prompt defect.",
                "expected_effect": "Candidate becomes a replayable shared Git body.",
                "metrics": ["shared_visibility"],
                "tests": ["remote sibling readback"],
                "rollback": "git revert the proposal commit",
                "actor": "agent-a",
            },
        )
        local_head = proposal["commit"]["head"]
        self.assertEqual(_run(self.origin, "rev-parse", "refs/heads/main"), origin_before)

        published = self.tool(
            self.server_a,
            "athena_prompt_publish",
            {"expected_git_head": local_head},
        )
        self.assertEqual(published["status"], "PUBLISHED_SHARED")
        self.assertTrue(published["shared_frontier_verified"])
        self.assertEqual(_run(self.origin, "rev-parse", "refs/heads/main"), local_head)

        sibling_before = _run(self.agent_b, "rev-parse", "HEAD")
        synced = self.tool(
            self.server_b,
            "athena_prompt_sync",
            {"expected_git_head": sibling_before},
        )
        self.assertEqual(synced["status"], "FAST_FORWARDED_SHARED")
        self.assertEqual(_run(self.agent_b, "rev-parse", "HEAD"), local_head)
        self.assertTrue((self.agent_b / proposal["candidate_path"]).is_file())

    def test_divergence_holds_without_merge_reset_or_force_push(self):
        seed = _run(self.agent_a, "rev-parse", "HEAD")
        proposal = self.tool(
            self.server_a,
            "athena_prompt_propose",
            {
                "expected_git_head": seed,
                "module_id": "core",
                "version": "1.1-local",
                "scope": ["build"],
                "content": "# Local branch\n",
                "defect": "local",
                "expected_effect": "local",
                "metrics": ["m"],
                "tests": ["t"],
                "rollback": "revert",
            },
        )
        local_head = proposal["commit"]["head"]

        _write(self.agent_b, "prompts/remote-branch.md", "remote branch\n")
        _run(self.agent_b, "add", ".")
        _run(self.agent_b, "commit", "-m", "remote branch")
        _run(self.agent_b, "push", "origin", "main")

        synced = self.tool(
            self.server_a,
            "athena_prompt_sync",
            {"expected_git_head": local_head},
        )
        self.assertEqual(synced["status"], "SYNC_HOLD_DIVERGED_HOLD")
        self.assertFalse(synced["mutation_performed"])
        self.assertEqual(_run(self.agent_a, "rev-parse", "HEAD"), local_head)

        published = self.tool(
            self.server_a,
            "athena_prompt_publish",
            {"expected_git_head": local_head},
        )
        self.assertEqual(published["status"], "PUBLISH_HOLD_DIVERGED_HOLD")
        self.assertFalse(published["push_performed"])
        self.assertEqual(_run(self.agent_a, "rev-parse", "HEAD"), local_head)

    def test_failed_fetch_stale_head_dirty_tree_and_invalid_remote_fail_closed(self):
        head = _run(self.agent_a, "rev-parse", "HEAD")
        missing = self.agent_a.parent / "missing-origin.git"
        _run(self.agent_a, "remote", "set-url", "origin", str(missing))
        unavailable = self.tool(
            self.server_a,
            "athena_prompt_sync",
            {"expected_git_head": head},
        )
        self.assertEqual(unavailable["status"], "REMOTE_SYNC_UNAVAILABLE_HOLD")
        self.assertFalse(unavailable["shared_frontier_verified"])

        _run(self.agent_a, "remote", "set-url", "origin", str(self.origin))
        _write(self.agent_a, "prompts/dirty.md", "dirty\n")
        dirty = self.rpc(
            self.server_a,
            "tools/call",
            {
                "name": "athena_prompt_sync",
                "arguments": {"expected_git_head": head},
            },
        )["result"]
        self.assertTrue(dirty["isError"])
        self.assertIn("DIRTY_GIT_WORKTREE", dirty["content"][0]["text"])
        (self.agent_a / "prompts/dirty.md").unlink()

        _write(self.agent_a, "prompts/local.md", "local\n")
        _run(self.agent_a, "add", ".")
        _run(self.agent_a, "commit", "-m", "advance local")
        stale = self.rpc(
            self.server_a,
            "tools/call",
            {
                "name": "athena_prompt_publish",
                "arguments": {"expected_git_head": head},
            },
        )["result"]
        self.assertTrue(stale["isError"])
        self.assertEqual(stale["structuredContent"]["status"], "STALE_GIT_HEAD")

        invalid = self.rpc(
            self.server_a,
            "tools/call",
            {
                "name": "athena_prompt_remote_status",
                "arguments": {"remote": "--upload-pack=bad", "fetch": True},
            },
        )["result"]
        self.assertTrue(invalid["isError"])

    def test_transport_tools_are_discoverable_without_implicit_coupling(self):
        tools = {
            row["name"]
            for row in self.rpc(self.server_a, "tools/list")["result"]["tools"]
        }
        self.assertTrue(
            {
                "athena_prompt_remote_status",
                "athena_prompt_sync",
                "athena_prompt_publish",
            }
            <= tools
        )
        resource = json.loads(
            self.rpc(
                self.server_a,
                "resources/read",
                {"uri": "athena://prompt/runtime"},
            )["result"]["contents"][0]["text"]
        )
        self.assertIn("remote_transport", resource["laws"])
        self.assertIn("implicit remote fetch", resource["non_goals"])


if __name__ == "__main__":
    unittest.main()
