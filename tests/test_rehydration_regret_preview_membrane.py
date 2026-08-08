import unittest

from athena_mcp.rehydration_loop import _state_digest
from athena_mcp.rehydration_regret import (
    REGRET_AB_TOOLS,
    install_regret_ab_extension,
)
from athena_mcp.rehydration_successor import ALL_METRICS
from athena_mcp.rehydration_terminal import install_terminal_gate


class _RemoteSync:
    def __init__(self, *, verified=True):
        self.verified = verified
        self.calls = []

    def sync(self, remote):
        self.calls.append(remote)
        return {
            "status": "UP_TO_DATE" if self.verified else "REMOTE_UNVERIFIED_HOLD",
            "remote": remote,
            "shared_frontier_verified": self.verified,
        }


class _Runtime:
    def __init__(self, *, verified=True):
        self.state = {
            "artifact": "ATHENA.REHYDRATION.LOOP.V1",
            "loop_id": "LOOP-AB-FRESH",
            "status": "ACTIVE",
            "goal": "Complete the current mission",
            "task": "Current bounded slice",
            "step_index": 3,
            "last_completion": None,
            "depth_policy": {"required_passes": []},
            "stop_conditions": [],
            "budget": {"max_prompt_chars": 20000},
        }
        self.state["state_digest"] = _state_digest(self.state)
        self.remote_sync = _RemoteSync(verified=verified)
        self.read_calls = 0

    def _read_state(self, loop_id):
        self.read_calls += 1
        if loop_id != self.state["loop_id"]:
            raise ValueError("loop not found")
        return dict(self.state), {"state": "prompts/rehydration/LOOP-AB-FRESH/state.json"}

    def _remote_mode(self, value):
        mode = str(value or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("bad remote mode")
        return mode

    def _path_last_commit(self, path):
        return "checkpoint-head"

    def _render_prompt(self, state, context, previous_completion):
        return "## Completion contract\n- The agent must finish this bounded cycle before requesting the next one.\n"

    def advance(self, *args, **kwargs):
        return {"status": "ACTIVE"}

    def call_tool(self, name, arguments):
        return {"legacy": name}


def _policy():
    weights = {metric: 0.0 for metric in ALL_METRICS}
    weights["utility"] = 1.0
    weights["risk"] = -1.0
    return {"weights": weights, "tie_epsilon": 1e-9}


def _candidate(name, utility, risk):
    metrics = {
        "utility": utility,
        "dependency_unblocking": 0.5,
        "uncertainty_reduction": 0.5,
        "novelty": 0.5,
        "risk": risk,
        "cost": 0.5,
        "repetition": 0.5,
    }
    return {"candidate_id": name, "task": name, "metrics": metrics}


def _install(runtime_cls):
    install_regret_ab_extension(runtime_cls)
    install_terminal_gate(runtime_cls, [])


class RegretPreviewMembraneTests(unittest.TestCase):
    def test_required_mode_syncs_before_rejecting_stale_state_digest(self):
        class Runtime(_Runtime):
            pass

        _install(Runtime)
        runtime = Runtime()
        out = runtime.call_tool(
            "athena_rehydration_successor_regret_compare",
            {
                "loop_id": "LOOP-AB-FRESH",
                "expected_state_digest": "old-state-digest",
                "completion": {"status": "SUCCEEDED", "residuals": []},
                "candidates": [
                    _candidate("A", 0.9, 0.2),
                    _candidate("B", 0.6, 0.4),
                ],
                "policy": _policy(),
                "weight_radii": [0.0, 0.2],
            },
        )
        self.assertEqual(out["status"], "STALE_SUCCESSOR_REGRET_COMPARE")
        self.assertEqual(runtime.remote_sync.calls, ["origin"])
        self.assertEqual(runtime.read_calls, 1)
        self.assertTrue(out["shared_frontier_verified"])
        self.assertTrue(out["requires_rehydrate"])
        self.assertEqual(out["detail"]["current_state_digest"], runtime.state["state_digest"])
        self.assertEqual(out["detail"]["current_step_index"], 3)
        self.assertIn("LOCAL_AB_PREVIEW != SHARED_CURRENT_AB_PREVIEW", out["laws"])
        self.assertNotIn("v2", out)

    def test_required_unverified_remote_holds_before_read_or_analysis(self):
        class Runtime(_Runtime):
            pass

        _install(Runtime)
        runtime = Runtime(verified=False)
        out = runtime.call_tool(
            "athena_rehydration_successor_regret_compare",
            {
                "loop_id": "LOOP-AB-FRESH",
                "expected_state_digest": runtime.state["state_digest"],
                "completion": {"status": "SUCCEEDED", "residuals": []},
                "candidates": [
                    _candidate("A", 0.9, 0.2),
                    _candidate("B", 0.6, 0.4),
                ],
                "policy": _policy(),
            },
        )
        self.assertEqual(out["status"], "REHYDRATION_SUCCESSOR_REGRET_COMPARE_SHARED_FRONTIER_HOLD")
        self.assertEqual(runtime.remote_sync.calls, ["origin"])
        self.assertEqual(runtime.read_calls, 0)
        self.assertFalse(out["shared_frontier_verified"])
        self.assertTrue(out["requires_rehydrate"])

    def test_disabled_mode_is_explicit_local_only_analysis(self):
        class Runtime(_Runtime):
            pass

        _install(Runtime)
        runtime = Runtime()
        out = runtime.call_tool(
            "athena_rehydration_successor_regret_compare",
            {
                "loop_id": "LOOP-AB-FRESH",
                "expected_state_digest": runtime.state["state_digest"],
                "completion": {"status": "SUCCEEDED", "residuals": []},
                "candidates": [
                    _candidate("A", 0.9, 0.2),
                    _candidate("B", 0.6, 0.4),
                ],
                "policy": _policy(),
                "weight_radii": [0.0, 0.2],
                "shared_remote_mode": "DISABLED",
            },
        )
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(runtime.remote_sync.calls, [])
        self.assertFalse(out["shared_frontier_verified"])
        self.assertEqual(out["preview_verification"], "LOCAL_ONLY_UNVERIFIED")
        self.assertEqual(out["freshness_law"], "SUCCESSOR_REGRET_COMPARE_SYNC_SHARED_GIT_BEFORE_ANALYSIS")
        self.assertTrue(out["calibration_pass"])

    def test_schema_exposes_shared_freshness_controls_after_terminal_install(self):
        class Runtime(_Runtime):
            pass

        _install(Runtime)
        tool = next(row for row in REGRET_AB_TOOLS if row["name"] == "athena_rehydration_successor_regret_compare")
        props = tool["inputSchema"]["properties"]
        self.assertIn("shared_remote_mode", props)
        self.assertIn("remote", props)
        self.assertIn("Fresh-sync shared Git", tool["description"])
        self.assertIn("closure request", props["completion"]["description"])


if __name__ == "__main__":
    unittest.main()
