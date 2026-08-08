from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.agent_bootstrap import AgentBootstrapRuntime
from athena_mcp.agent_bootstrap_handoff import install_agent_bootstrap_handoff
from athena_mcp.git_backend import GitBackend


class _Prompt:
    available = True

    def __init__(self, git):
        self.git = git

    def compile(self, task="", profile=None, include_text=False):
        return {
            "profile": profile or "BUILD",
            "selected_modules": ["core"],
            "selected_overlays": [],
            "git_head": self.git.head(),
            "prompt_stack_digest": "p" * 64,
            "ancestry": {"policy": "test"},
        }


class _Frontier:
    def __init__(self):
        self.digest = "f" * 64

    def hydrate(self, **kwargs):
        return {
            "status": "HYDRATED",
            "source_ref": kwargs.get("source_ref"),
            "resolved_ref": kwargs.get("source_ref"),
            "source_head": "s" * 40,
            "frontier_digest": self.digest,
            "ready_work": [],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {"event_reduced_runs": 1},
            "sched_contract": {"status": "PASS", "contracts": {"reducer": "ok"}},
            "remote_checked": True,
            "fetch_error": None,
        }

    def select(self, **kwargs):
        return {"status": "NO_REPLAYABLE_READY_WORK", "selected": None, "pareto_front": []}


class _Issues:
    def snapshot(self, **kwargs):
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": "demeet2k/Athena",
            "relevant": [],
            "digest": "i" * 64,
            "witness": {"provider": "test", "http_status": 200},
        }


class _Loop:
    def __init__(self, loops=None):
        self.loops = list(loops or [])

    def index(self, shared_remote_mode="REQUIRED", remote="origin"):
        return {
            "status": "OK",
            "count": len(self.loops),
            "loops": list(self.loops),
            "shared_frontier_verified": shared_remote_mode != "DISABLED",
            "freshness_law": "INDEX_SYNC_SHARED_GIT_BEFORE_LISTING_LOOP_TIPS",
            "remote_sync": {"status": "UP_TO_DATE" if shared_remote_mode != "DISABLED" else "DISABLED"},
        }


class _Handoff:
    def __init__(self):
        self.digest = "h" * 64
        self.mode = "DELTA_ONLY"
        self.routing = {
            "artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1",
            "status": "SELECTED",
            "selected": {"task": "continue verified work"},
            "baton_digest": "r" * 64,
        }
        self.calls = []

    def derive(self, loop_id, shared_remote_mode="REQUIRED", remote="origin"):
        self.calls.append(loop_id)
        return {
            "artifact": "ATHENA.REHYDRATION.HANDOFF.DELTA.V1",
            "status": "HANDOFF_READY" if shared_remote_mode != "BEST_EFFORT" else "HANDOFF_READY_UNVERIFIED",
            "loop_id": loop_id,
            "handoff_digest": self.digest,
            "routing_successor": self.routing,
            "handoff": {
                "hydration": {"mode": self.mode},
                "affected_cone": {"components": ["project_work"], "paths": {"project_work": ["feature.txt"]}},
            },
            "shared_frontier_verified": shared_remote_mode == "REQUIRED",
        }


def _git_root(base: Path) -> GitBackend:
    root = base / "brain"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m", "seed"], check=True, capture_output=True)
    return GitBackend(root)


def _active(loop_id: str, step: int = 1):
    return {
        "loop_id": loop_id,
        "status": "ACTIVE",
        "step_index": step,
        "goal": "ship",
        "task": "continue",
        "updated_at": f"2026-08-08T12:00:0{step}-07:00",
        "state_digest": (str(step) * 64)[:64],
        "chain_digest": (hex(step)[2:] * 64)[:64],
        "checkpoint_head": "c" * 40,
    }


class BootstrapHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_agent_bootstrap_handoff(AgentBootstrapRuntime)

    def _runtime(self, loops=None):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        git = _git_root(Path(td.name))
        runtime = AgentBootstrapRuntime(git, _Prompt(git), _Frontier(), _Issues())
        runtime._agent_bootstrap_rehydration_loop_v1 = _Loop(loops)
        runtime._agent_bootstrap_handoff_runtime_v1 = _Handoff()
        return runtime

    def test_no_active_loop_is_lawful_empty_continuation(self):
        runtime = self._runtime([])
        packet = runtime.bootstrap(
            agent_id="a1",
            task="build",
            fetch=False,
            shared_remote_mode="DISABLED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(packet["status"], "BOOTSTRAPPED")
        self.assertEqual(packet["continuation"]["status"], "NO_ACTIVE_CONTINUATION")
        self.assertIsNone(packet["continuation"]["handoff_digest"])
        self.assertIn("rehydration_continuation_digest", packet["address"])
        self.assertIn("sibling_state_digest", packet["address"])

    def test_multiple_active_loops_preserve_ambiguity(self):
        runtime = self._runtime([_active("RHL-A"), _active("RHL-B")])
        packet = runtime.bootstrap(
            agent_id="a1",
            task="build",
            fetch=False,
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(packet["status"], "BOOTSTRAP_HOLD")
        self.assertEqual(packet["continuation"]["status"], "CONTINUATION_AMBIGUOUS_HOLD")
        self.assertEqual(packet["continuation"]["active_count"], 2)
        self.assertEqual(runtime._agent_bootstrap_handoff_runtime_v1.calls, [])

    def test_explicit_loop_binds_handoff_without_rescoring_routing(self):
        runtime = self._runtime([_active("RHL-A"), _active("RHL-B")])
        packet = runtime.bootstrap(
            agent_id="a1",
            task="build",
            fetch=False,
            continuation_loop_id="RHL-B",
            continuation_shared_remote_mode="DISABLED",
        )
        continuation = packet["continuation"]
        self.assertEqual(continuation["status"], "SELECTED")
        self.assertEqual(continuation["selected_loop_id"], "RHL-B")
        self.assertEqual(continuation["handoff_digest"], "h" * 64)
        self.assertEqual(continuation["hydration_mode"], "DELTA_ONLY")
        self.assertEqual(
            continuation["routing_successor"],
            runtime._agent_bootstrap_handoff_runtime_v1.routing,
        )
        self.assertIn("WHAT_NEXT != WHAT_TO_REHYDRATE", continuation["laws"])

    def test_handoff_only_change_refreshes_only_continuation_cone(self):
        runtime = self._runtime([_active("RHL-A")])
        first = runtime.bootstrap(
            agent_id="a1",
            task="build",
            fetch=False,
            continuation_shared_remote_mode="DISABLED",
        )
        runtime._agent_bootstrap_handoff_runtime_v1.digest = "z" * 64
        second = runtime.refresh(
            session_id=first["session_id"],
            continuation_shared_remote_mode="DISABLED",
        )
        changed = second["refresh"]["changed"]
        self.assertTrue(changed["rehydration_continuation_digest"])
        self.assertFalse(changed["git_head"])
        self.assertFalse(changed["prompt_stack_digest"])
        self.assertFalse(changed["frontier_digest"])
        self.assertFalse(changed["issue_pressure_digest"])
        self.assertEqual(second["refresh"]["affected_dependency_cone"], ["rehydration_handoff"])

    def test_continuation_address_is_independent_from_world_coordinates(self):
        runtime = self._runtime([_active("RHL-A")])
        first = runtime.bootstrap(
            agent_id="a1",
            task="build",
            fetch=False,
            continuation_shared_remote_mode="DISABLED",
        )
        old = dict(first["address"])
        runtime._agent_bootstrap_handoff_runtime_v1.digest = "y" * 64
        second = runtime.bootstrap(
            agent_id="a2",
            task="build",
            fetch=False,
            continuation_shared_remote_mode="DISABLED",
        )
        new = second["address"]
        for key in (
            "git_head",
            "prompt_stack_digest",
            "frontier_source_head",
            "frontier_digest",
            "sched_contract_digest",
            "issue_pressure_digest",
            "sibling_state_digest",
        ):
            self.assertEqual(old[key], new[key], key)
        self.assertNotEqual(old["rehydration_continuation_digest"], new["rehydration_continuation_digest"])


if __name__ == "__main__":
    unittest.main()