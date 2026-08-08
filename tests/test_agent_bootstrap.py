from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.agent_bootstrap import AgentBootstrapRuntime
from athena_mcp.frontier_runtime import FRONTIER_TOOL_NAMES, FrontierRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime


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


def _fixture(base: Path):
    root = base / "brain"
    remote = base / "remote.git"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")

    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {
            "core": {
                "path": "prompts/ORCHESTRATION_CORE.md",
                "order": 0,
                "mandatory": True,
            }
        },
    }
    _write(root, "prompts/PROMPT.manifest.json", manifest)
    _write(
        root,
        "prompts/state/ACTIVE.json",
        {
            "status": "ACTIVE",
            "profile": "MAXDEV",
            "enabled_modules": ["core"],
            "active_scoped_overlays": [],
            "revision": 1,
        },
    )
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(root, "orchestration/v3/reducer.py", "REDUCER CONTRACT\n")
    _write(root, "orchestration/v3/ready.py", "READY CONTRACT\n")
    _write(root, "orchestration/v3/claim.py", "CLAIM CONTRACT\n")
    _write(
        root,
        "runtime/queue/objective.alpha.json",
        {
            "objective_id": "objective.alpha",
            "artifact_target": "artifact.md",
            "priority": 100,
            "risk_class": "LOW",
            "work_class": "PROJECT",
            "production_authority": "HOLD",
        },
    )
    _write(
        root,
        "runtime/runs/run.alpha/manifest.json",
        {
            "run_id": "run.alpha",
            "objective_ref": "objective.alpha",
            "artifact_target": "artifact.md",
            "work_class": "PROJECT",
            "nodes": [
                {
                    "node_id": "build",
                    "role_capability": "builder",
                    "depends_on": [],
                    "max_attempts": 2,
                    "not_before_pulse": 0,
                    "claim_path": "runtime/runs/run.alpha/claims/build.json",
                }
            ],
        },
    )
    events = [
        {
            "schema_version": "EVENT_V1",
            "event_id": "e1",
            "sequence": 1,
            "run_id": "run.alpha",
            "event_type": "RUN_CREATED",
            "at": "2026-08-08T00:00:00Z",
            "node_id": None,
            "data": {},
        },
        {
            "schema_version": "EVENT_V1",
            "event_id": "e2",
            "sequence": 2,
            "run_id": "run.alpha",
            "event_type": "RUN_ADMITTED",
            "at": "2026-08-08T00:00:01Z",
            "node_id": None,
            "data": {"verdict": "PASS"},
        },
    ]
    for seq, event in enumerate(events, start=1):
        _write(root, f"runtime/runs/run.alpha/events/{seq:08d}.json", event)

    _run(root, "add", ".")
    _run(root, "commit", "-m", "fixture")
    contract = {
        path: _run(root, "rev-parse", f"HEAD:{path}")
        for path in (
            "orchestration/v3/reducer.py",
            "orchestration/v3/ready.py",
            "orchestration/v3/claim.py",
        )
    }
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, text=True, capture_output=True)
    _run(root, "remote", "add", "origin", str(remote))
    _run(root, "push", "origin", "HEAD:refs/heads/athena-runtime-v3-candidate")
    return root, contract


class FakeIssueProvider:
    def __init__(self):
        self.revision = 1

    def snapshot(self, *, task, issue_repo=None, remote="origin", limit=10):
        relevant = [
            {
                "issue_number": 160,
                "title": "One-call cold-start agent bootstrap",
                "body_digest": hashlib.sha256(f"body-{self.revision}".encode()).hexdigest(),
                "labels": ["P0"],
                "updated_at": f"2026-08-08T00:00:0{self.revision}Z",
                "state": "open",
                "url": "https://example.invalid/160",
                "routing_score": 10,
                "standing": "PRESSURE_ONLY",
            }
        ]
        digest = hashlib.sha256(
            json.dumps(
                {"repo": issue_repo or "demeet2k/Athena", "task": task, "relevant": relevant},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": issue_repo or "demeet2k/Athena",
            "relevant": relevant[:limit],
            "digest": digest,
            "witness": {
                "provider": "fake_github_api",
                "repo": issue_repo or "demeet2k/Athena",
                "retrieved_at": f"2026-08-08T00:00:0{self.revision}Z",
                "http_status": 200,
            },
            "laws": ["ISSUE_PRESSURE != SCHED_READY", "ISSUE_BODY != EXECUTABLE_STATE"],
        }


class AgentBootstrapRuntimeTests(unittest.TestCase):
    def _runtime(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root, contract = _fixture(Path(td.name))
        git = GitBackend(root)
        prompt = PromptRuntime(git)
        frontier = FrontierRuntime(git, prompt, contract_blobs=contract)
        issues = FakeIssueProvider()
        return AgentBootstrapRuntime(git, prompt, frontier, issues), root, issues

    def test_bootstrap_factorizes_sources_and_session_identity(self):
        runtime, _, _ = self._runtime()
        a = runtime.bootstrap(
            agent_id="agent-a",
            task="cold-start bootstrap pressure",
            issue_repo="demeet2k/Athena",
            shared_remote_mode="DISABLED",
        )
        b = runtime.bootstrap(
            agent_id="agent-b",
            task="cold-start bootstrap pressure",
            issue_repo="demeet2k/Athena",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(a["status"], "BOOTSTRAPPED")
        self.assertEqual(b["status"], "BOOTSTRAPPED")
        self.assertNotEqual(a["session_id"], b["session_id"])
        self.assertEqual(a["address"], b["address"])
        self.assertEqual(a["composite_digest"], b["composite_digest"])
        self.assertNotEqual(a["prompt"]["prompt_stack_digest"], a["frontier"]["frontier_digest"])
        self.assertEqual(a["issue_pressure"]["relevant"][0]["standing"], "PRESSURE_ONLY")
        self.assertFalse(a["execution_surface"]["claim_tool_exposed"])
        self.assertNotIn("athena_frontier_claim", FRONTIER_TOOL_NAMES)

    def test_issue_pressure_change_only_changes_issue_coordinate(self):
        runtime, _, issues = self._runtime()
        first = runtime.bootstrap(agent_id="agent-a", task="bootstrap issue pressure", issue_repo="demeet2k/Athena")
        issues.revision = 2
        refreshed = runtime.refresh(session_id=first["session_id"])
        changed = refreshed["refresh"]["changed"]
        self.assertTrue(changed["issue_pressure_digest"])
        for key, value in changed.items():
            if key != "issue_pressure_digest":
                self.assertFalse(value, key)
        self.assertEqual(refreshed["refresh"]["affected_dependency_cone"], ["issue_pressure_routing"])

    def test_issue_pressure_never_manufactures_scheduler_ready_work(self):
        runtime, _, _ = self._runtime()
        packet = runtime.bootstrap(agent_id="agent-a", task="claim build from issue body", issue_repo="demeet2k/Athena")
        self.assertEqual([x["node_id"] for x in packet["frontier"]["ready_work"]], ["build"])
        self.assertEqual(packet["issue_pressure"]["relevant"][0]["standing"], "PRESSURE_ONLY")
        self.assertIn("ISSUE_BODY != EXECUTION", packet["laws"])

    def test_scheduler_change_changes_frontier_not_prompt_content_digest(self):
        runtime, root, _ = self._runtime()
        first = runtime.bootstrap(agent_id="agent-a", task="bootstrap", issue_repo="demeet2k/Athena")
        _write(
            root,
            "runtime/runs/run.alpha/claims/build.json",
            {
                "schema_version": "CLAIM_V1",
                "run_id": "run.alpha",
                "node_id": "build",
                "worker_role": "other-agent",
                "attempt": 1,
                "policy_commit": "a" * 40,
                "claimed_at": "2026-08-08T00:00:02Z",
                "lease_expires_at": "2026-08-08T00:10:02Z",
                "input_snapshot_digest": "b" * 64,
                "production_authority": "HOLD",
            },
        )
        _run(root, "add", ".")
        _run(root, "commit", "-m", "provider claim")
        _run(root, "push", "origin", "HEAD:refs/heads/athena-runtime-v3-candidate")
        second = runtime.refresh(prior_address=first["address"], agent_id="agent-a", task="bootstrap", issue_repo="demeet2k/Athena")
        changed = second["refresh"]["changed"]
        self.assertTrue(changed["git_head"])
        self.assertTrue(changed["frontier_source_head"])
        self.assertTrue(changed["frontier_digest"])
        self.assertFalse(changed["prompt_stack_digest"])
        self.assertFalse(changed["issue_pressure_digest"])

    def test_prompt_change_changes_prompt_coordinate_without_issue_change(self):
        runtime, root, _ = self._runtime()
        first = runtime.bootstrap(agent_id="agent-a", task="bootstrap", issue_repo="demeet2k/Athena")
        _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE CHANGED\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "prompt change")
        second = runtime.refresh(prior_address=first["address"], agent_id="agent-a", task="bootstrap", issue_repo="demeet2k/Athena")
        changed = second["refresh"]["changed"]
        self.assertTrue(changed["git_head"])
        self.assertTrue(changed["prompt_stack_digest"])
        self.assertFalse(changed["frontier_source_head"])
        self.assertFalse(changed["frontier_digest"])
        self.assertFalse(changed["issue_pressure_digest"])

    def test_missing_session_fails_closed(self):
        runtime, _, _ = self._runtime()
        result = runtime.refresh(session_id="unknown")
        self.assertEqual(result["status"], "SESSION_NOT_FOUND_HOLD")
        self.assertTrue(result["requires_prior_address"])

    def test_tools_registered_on_prompt_runtime_surface(self):
        self.assertIn("athena_agent_bootstrap", PROMPT_RUNTIME_TOOL_NAMES)
        self.assertIn("athena_agent_refresh", PROMPT_RUNTIME_TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()