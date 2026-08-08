from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_runtime import FrontierRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _seed_brain(root: Path):
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "seed")
    _run(root, "config", "user.email", "seed@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    })
    _write(root, "prompts/state/ACTIVE.json", {"status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(root, "orchestration/v3/reducer.py", "REDUCER CONTRACT\n")
    _write(root, "orchestration/v3/ready.py", "READY CONTRACT\n")
    _write(root, "orchestration/v3/claim.py", "CLAIM CONTRACT\n")
    _write(root, "runtime/queue/objective.alpha.json", {
        "objective_id": "objective.alpha", "artifact_target": "artifact.md", "priority": 100,
        "risk_class": "LOW", "work_class": "PROJECT", "production_authority": "HOLD"
    })
    _write(root, "runtime/runs/run.alpha/manifest.json", {
        "run_id": "run.alpha", "objective_ref": "objective.alpha", "artifact_target": "artifact.md", "work_class": "PROJECT",
        "nodes": [{"node_id": "build", "role_capability": "builder", "depends_on": [], "max_attempts": 1, "not_before_pulse": 0, "claim_path": "runtime/runs/run.alpha/claims/build.json"}]
    })
    _write(root, "runtime/runs/run.alpha/events/001.json", {"schema_version": "EVENT_V1", "event_id": "e1", "sequence": 1, "run_id": "run.alpha", "event_type": "RUN_CREATED", "at": "2026-08-08T00:00:00Z", "node_id": None, "data": {}})
    _write(root, "runtime/runs/run.alpha/events/002.json", {"schema_version": "EVENT_V1", "event_id": "e2", "sequence": 2, "run_id": "run.alpha", "event_type": "RUN_ADMITTED", "at": "2026-08-08T00:00:01Z", "node_id": None, "data": {"verdict": "PASS"}})
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed frontier")
    _run(root, "branch", "athena-runtime-v3-candidate")
    return {
        path: _run(root, "rev-parse", f"HEAD:{path}")
        for path in ("orchestration/v3/reducer.py", "orchestration/v3/ready.py", "orchestration/v3/claim.py")
    }


def _runtime(root: Path, contracts):
    git = GitBackend(root)
    return FrontierRuntime(git, PromptRuntime(git), contract_blobs=contracts)


class FrontierCoordinateFactorizationTests(unittest.TestCase):
    def _local(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name) / "brain-a"
        contracts = _seed_brain(root)
        return root, contracts

    def test_unrelated_git_clock_does_not_mutate_frontier_content_identity(self):
        root, contracts = self._local()
        runtime = _runtime(root, contracts)
        first = runtime.hydrate(source_ref="HEAD", fetch=False)

        _write(root, "notes/unrelated.txt", "repository clock only\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "unrelated repository event")
        second = runtime.hydrate(source_ref="HEAD", fetch=False)

        self.assertNotEqual(first["source_head"], second["source_head"])
        self.assertEqual(first["frontier_digest"], second["frontier_digest"])
        self.assertEqual(first["prompt_stack_digest"], second["prompt_stack_digest"])
        self.assertIn("excludes source_head", second["frontier_digest_basis"])

        objective = json.loads((root / "runtime/queue/objective.alpha.json").read_text())
        objective["priority"] = 101
        _write(root, "runtime/queue/objective.alpha.json", objective)
        _run(root, "add", ".")
        _run(root, "commit", "-m", "actual frontier mutation")
        third = runtime.hydrate(source_ref="HEAD", fetch=False)
        self.assertNotEqual(second["frontier_digest"], third["frontier_digest"])

    def test_generated_from_contains_event_and_projection_sources(self):
        root, contracts = self._local()
        packet = _runtime(root, contracts).hydrate(source_ref="HEAD", fetch=False)
        self.assertIn("runtime/runs/run.alpha/events/001.json", packet["generated_from"])
        self.assertIn("runtime/runs/run.alpha/events/002.json", packet["generated_from"])
        self.assertIn("runtime/runs/run.alpha/manifest.json", packet["generated_from"])
        self.assertIn("runtime/queue/objective.alpha.json", packet["generated_from"])

    def test_two_checkout_paths_same_shared_frontier_same_digest(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        a = base / "agent-a"
        contracts = _seed_brain(a)
        origin = base / "brain.git"
        p = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr or p.stdout)
        _run(a, "remote", "add", "origin", str(origin))
        _run(a, "push", "origin", "master")
        _run(a, "push", "origin", "athena-runtime-v3-candidate")

        b = base / "different-path-agent-b"
        p = subprocess.run(["git", "clone", str(origin), str(b)], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr or p.stdout)
        _run(b, "config", "user.name", "b")
        _run(b, "config", "user.email", "b@example.invalid")

        packet_a = _runtime(a, contracts).hydrate(source_ref="athena-runtime-v3-candidate", fetch=True)
        packet_b = _runtime(b, contracts).hydrate(source_ref="athena-runtime-v3-candidate", fetch=True)
        self.assertTrue(packet_a["remote_checked"])
        self.assertTrue(packet_b["remote_checked"])
        self.assertNotEqual(packet_a["source_repo"], packet_b["source_repo"])
        self.assertEqual(packet_a["source_head"], packet_b["source_head"])
        self.assertEqual(packet_a["frontier_digest"], packet_b["frontier_digest"])
        self.assertEqual(packet_a["prompt_stack_digest"], packet_b["prompt_stack_digest"])

    def test_missing_requested_remote_branch_cannot_inherit_fetch_witness(self):
        root, contracts = self._local()
        td = Path(root).parent
        origin = td / "master-only.git"
        p = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr or p.stdout)
        _run(root, "remote", "add", "origin", str(origin))
        _run(root, "push", "origin", "master")
        # Local candidate branch exists, but it is intentionally absent on origin.
        source = _runtime(root, contracts)._source("athena-runtime-v3-candidate", fetch=True)
        self.assertFalse(source["remote_checked"])
        self.assertIn("requested remote source ref unavailable", source["fetch_error"])


if __name__ == "__main__":
    unittest.main()
