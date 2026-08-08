from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.dispatch import _call_prompt_runtime_tool
from athena_mcp.git_backend import GitBackend, GitStaleHead


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _shared_brain(base: Path):
    local = base / "agent-a"
    local.mkdir()
    _run(local, "init")
    _run(local, "config", "user.name", "agent-a")
    _run(local, "config", "user.email", "agent-a@example.invalid")

    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core", "self_engineering"]},
        "modules": {
            "core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True},
            "self_engineering": {"path": "prompts/modules/SELF_ENGINEERING.md", "order": 10, "mandatory": True},
        },
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core", "self_engineering"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(local, "prompts/PROMPT.manifest.json", json.dumps(manifest, indent=2))
    _write(local, "prompts/state/ACTIVE.json", json.dumps(active, indent=2))
    _write(local, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(local, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(local, "prompts/modules/SELF_ENGINEERING.md", "SELF\n")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed shared brain")

    origin = base / "brain.git"
    p = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "HEAD:master")

    sibling = base / "agent-b"
    p = subprocess.run(["git", "clone", str(origin), str(sibling)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(sibling, "config", "user.name", "agent-b")
    _run(sibling, "config", "user.email", "agent-b@example.invalid")
    return local, sibling


class _Server:
    def __init__(self, root: Path):
        self.git = GitBackend(root)


class PromptSharedLoopTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, sibling = _shared_brain(Path(td.name))
        return _Server(local), local, sibling

    def test_hydrate_auto_fast_forwards_sibling_learning(self):
        server, local, sibling = self._fixture()
        _write(sibling, "prompts/sibling-learning.md", "B learned this\n")
        _run(sibling, "add", ".")
        _run(sibling, "commit", "-m", "agent b learning")
        sibling_head = _run(sibling, "rev-parse", "HEAD")
        _run(sibling, "push", "origin", "master")

        hydrated = _call_prompt_runtime_tool(server, "athena_prompt_hydrate", {"task": "continue"})
        self.assertEqual(hydrated["remote_sync"]["status"], "FAST_FORWARDED")
        self.assertTrue(hydrated["shared_frontier_verified"])
        self.assertEqual(_run(local, "rev-parse", "HEAD"), sibling_head)
        self.assertEqual((local / "prompts" / "sibling-learning.md").read_text(), "B learned this\n")

    def test_prompt_proposal_auto_publishes_for_sibling_consumption(self):
        server, local, sibling = self._fixture()
        head = _run(local, "rev-parse", "HEAD")
        result = _call_prompt_runtime_tool(server, "athena_prompt_propose", {
            "module_id": "self_engineering",
            "content": "SELF V2 SHARED\n",
            "defect": "agents rediscover prompt routing defect",
            "expected_effect": "shared tested prompt candidate",
            "scope": ["profile:MAXDEV"],
            "tests": ["two-agent readback"],
            "falsifier": "sibling cannot reconstruct candidate",
            "rollback": "retire candidate",
            "expected_git_head": head,
            "actor": "agent-a",
            "profile": "MAXDEV",
        })
        self.assertTrue(result["durable_return"])
        self.assertEqual(result["remote_publish"]["status"], "PUBLISHED_SHARED")

        _run(sibling, "pull", "--ff-only", "origin", "master")
        candidate = sibling / result["candidate_ref"]
        self.assertTrue(candidate.is_file())
        self.assertIn("SELF V2 SHARED", candidate.read_text())
        self.assertEqual(_run(sibling, "rev-parse", "HEAD"), result["git"]["head"])

    def test_sibling_advance_between_read_and_write_rejects_stale_agent(self):
        server, local, sibling = self._fixture()
        stale_head = _run(local, "rev-parse", "HEAD")

        _write(sibling, "prompts/new-pressure.md", "new shared pressure\n")
        _run(sibling, "add", ".")
        _run(sibling, "commit", "-m", "new shared pressure")
        sibling_head = _run(sibling, "rev-parse", "HEAD")
        _run(sibling, "push", "origin", "master")

        with self.assertRaises(GitStaleHead):
            _call_prompt_runtime_tool(server, "athena_prompt_propose", {
                "module_id": "self_engineering",
                "content": "STALE MUTATION\n",
                "defect": "stale",
                "expected_effect": "none",
                "scope": ["profile:MAXDEV"],
                "tests": ["stale rejection"],
                "falsifier": "write succeeds",
                "rollback": "none",
                "expected_git_head": stale_head,
                "actor": "agent-a",
                "profile": "MAXDEV",
            })
        self.assertEqual(_run(local, "rev-parse", "HEAD"), sibling_head)
        self.assertFalse((local / "prompts" / "candidates" / "self_engineering").exists())


if __name__ == "__main__":
    unittest.main()
