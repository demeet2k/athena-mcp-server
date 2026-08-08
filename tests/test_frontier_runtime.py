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
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        p.write_text(value, encoding="utf-8")
    else:
        p.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _fixture(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")

    prompt_manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    }
    _write(root, "prompts/PROMPT.manifest.json", prompt_manifest)
    _write(root, "prompts/state/ACTIVE.json", {"status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")

    # Test-only pinned scheduler contracts.
    _write(root, "orchestration/v3/reducer.py", "REDUCER CONTRACT\n")
    _write(root, "orchestration/v3/ready.py", "READY CONTRACT\n")
    _write(root, "orchestration/v3/claim.py", "CLAIM CONTRACT\n")

    objective = {
        "objective_id": "objective.alpha",
        "artifact_target": "artifact.md",
        "priority": 100,
        "risk_class": "LOW",
        "work_class": "PROJECT",
        "production_authority": "HOLD",
    }
    run = {
        "run_id": "run.alpha",
        "objective_ref": "objective.alpha",
        "artifact_target": "artifact.md",
        "work_class": "PROJECT",
        "nodes": [
            {"node_id": "build", "role_capability": "builder", "depends_on": [], "max_attempts": 2, "not_before_pulse": 0, "claim_path": "runtime/runs/run.alpha/claims/build.json"},
            {"node_id": "verify", "role_capability": "verifier", "depends_on": ["build"], "max_attempts": 1, "not_before_pulse": 0, "claim_path": "runtime/runs/run.alpha/claims/verify.json"},
        ],
    }
    _write(root, "runtime/queue/objective.alpha.json", objective)
    _write(root, "runtime/runs/run.alpha/manifest.json", run)
    events = [
        {"schema_version": "EVENT_V1", "event_id": "e1", "sequence": 1, "run_id": "run.alpha", "event_type": "RUN_CREATED", "at": "2026-08-08T00:00:00Z", "node_id": None, "data": {}},
        {"schema_version": "EVENT_V1", "event_id": "e2", "sequence": 2, "run_id": "run.alpha", "event_type": "RUN_ADMITTED", "at": "2026-08-08T00:00:01Z", "node_id": None, "data": {"verdict": "PASS"}},
    ]
    for i, event in enumerate(events, start=1):
        _write(root, f"runtime/runs/run.alpha/events/{i:03d}.json", event)

    # A second terminal run deliberately lacks events to test coverage semantics.
    objective2 = {**objective, "objective_id": "objective.beta", "artifact_target": "beta.md", "priority": 50}
    run2 = {**run, "run_id": "run.beta", "objective_ref": "objective.beta", "artifact_target": "beta.md", "nodes": [{"node_id": "build", "role_capability": "builder", "depends_on": [], "max_attempts": 1, "not_before_pulse": 0, "claim_path": "runtime/runs/run.beta/claims/build.json"}]}
    _write(root, "runtime/queue/objective.beta.json", objective2)
    _write(root, "runtime/runs/run.beta/manifest.json", run2)
    _write(root, "runtime/runs/run.beta/terminal.json", {"record_type": "RUN_TERMINAL_V1", "run_id": "run.beta", "disposition": "COMMITTED", "node_states": {"build": "SUCCEEDED"}, "next_frontier": "observe successor"})

    _run(root, "add", ".")
    _run(root, "commit", "-m", "fixture")
    contract = {
        path: _run(root, "rev-parse", f"HEAD:{path}")
        for path in ("orchestration/v3/reducer.py", "orchestration/v3/ready.py", "orchestration/v3/claim.py")
    }
    return root, contract


class FrontierRuntimeTests(unittest.TestCase):
    def _runtime(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root, contract = _fixture(Path(td.name))
        git = GitBackend(root)
        return FrontierRuntime(git, PromptRuntime(git), contract_blobs=contract), root

    def test_event_reduced_ready_work_and_terminal_projection_are_distinct(self):
        runtime, _ = self._runtime()
        packet = runtime.hydrate(source_ref="HEAD", fetch=False)
        self.assertEqual(packet["sched_contract"]["status"], "PASS")
        alpha = next(r for r in packet["runs"] if r["run_id"] == "run.alpha")
        beta = next(r for r in packet["runs"] if r["run_id"] == "run.beta")
        self.assertEqual(alpha["reduction_basis"], "EVENT_REDUCED")
        self.assertEqual(alpha["projection"]["ready_nodes"], ["build"])
        self.assertEqual(beta["reduction_basis"], "TERMINAL_PROJECTION_ONLY")
        self.assertEqual(beta["projection"]["ready_nodes"], [])
        self.assertEqual(packet["source_coverage"]["event_reduced_runs"], 1)
        self.assertEqual(packet["source_coverage"]["terminal_projection_only_runs"], 1)
        self.assertTrue(any(r["kind"] == "SOURCE_COVERAGE" and r["run_id"] == "run.beta" for r in packet["residuals"]))

    def test_frontier_digest_is_deterministic_and_distinct_from_prompt_digest(self):
        runtime, _ = self._runtime()
        a = runtime.hydrate(source_ref="HEAD", fetch=False)
        b = runtime.hydrate(source_ref="HEAD", fetch=False)
        self.assertEqual(a["frontier_digest"], b["frontier_digest"])
        self.assertNotEqual(a["frontier_digest"], a["prompt_stack_digest"])
        self.assertIn("PROMPT_STACK_DIGEST != FRONTIER_DIGEST", a["laws"])

    def test_select_uses_only_replayable_ready_nodes(self):
        runtime, _ = self._runtime()
        selected = runtime.select(source_ref="HEAD", fetch=False)
        # fetch=False intentionally means the source is not a freshly verified remote;
        # selection therefore fails closed even though the pure reduction finds READY work.
        self.assertEqual(selected["status"], "FRONTIER_HOLD")
        self.assertEqual(selected["reason"], "FRONTIER_REMOTE_UNVERIFIED_HOLD")
        self.assertEqual([x["node_id"] for x in selected["frontier"]["ready_work"]], ["build"])

    def test_contract_drift_holds_and_removes_selection_authority(self):
        runtime, root = self._runtime()
        _write(root, "orchestration/v3/ready.py", "CHANGED CONTRACT\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "contract drift")
        packet = runtime.hydrate(source_ref="HEAD", fetch=False)
        self.assertEqual(packet["sched_contract"]["status"], "SCHED_CONTRACT_CHANGED_HOLD")
        self.assertEqual(packet["status"], "FRONTIER_REMOTE_UNVERIFIED_HOLD")
        # Contract mismatch remains independently visible even when remote freshness is also absent.
        self.assertFalse(packet["sched_contract"]["contracts"]["orchestration/v3/ready.py"]["match"])

    def test_freshness_tracks_three_independent_coordinates(self):
        runtime, root = self._runtime()
        first = runtime.hydrate(source_ref="HEAD", fetch=False)
        _write(root, "runtime/queue/objective.alpha.json", {"objective_id": "objective.alpha", "artifact_target": "artifact.md", "priority": 101, "risk_class": "LOW", "work_class": "PROJECT", "production_authority": "HOLD"})
        _run(root, "add", ".")
        _run(root, "commit", "-m", "frontier change")
        fresh = runtime.freshness(first["source_head"], first["frontier_digest"], first["prompt_stack_digest"], source_ref="HEAD", fetch=False)
        self.assertEqual(fresh["status"], "STALE")
        self.assertTrue(fresh["changed"]["shared_source_head"])
        self.assertTrue(fresh["changed"]["frontier_digest"])
        self.assertFalse(fresh["changed"]["prompt_stack_digest"])


if __name__ == "__main__":
    unittest.main()
