import unittest

from athena_mcp.rehydration_loop import _state_digest
from athena_mcp.rehydration_regret import (
    SuccessorRegretAB,
    install_regret_ab_extension,
    maximize_linear_over_bounded_simplex,
)
from athena_mcp.rehydration_successor import ALL_METRICS


class _Runtime:
    def __init__(self):
        self.state = {
            "artifact": "ATHENA.REHYDRATION.LOOP.V1",
            "loop_id": "LOOP-AB",
            "status": "ACTIVE",
            "goal": "Complete the current mission",
            "task": "Current bounded slice",
            "step_index": 2,
            "last_completion": None,
        }
        self.state["state_digest"] = _state_digest(self.state)

    def _read_state(self, loop_id):
        if loop_id != self.state["loop_id"]:
            raise ValueError("loop not found")
        return dict(self.state), {"base": "prompts/rehydration/LOOP-AB"}


def policy(**weights):
    full = {metric: 0.0 for metric in ALL_METRICS}
    full.update(weights)
    return {"weights": full, "tie_epsilon": 1e-9}


def candidate(candidate_id, **metrics):
    full = {
        "utility": 0.5,
        "dependency_unblocking": 0.5,
        "uncertainty_reduction": 0.5,
        "novelty": 0.5,
        "risk": 0.5,
        "cost": 0.5,
        "repetition": 0.5,
    }
    full.update(metrics)
    return {"task": candidate_id, "candidate_id": candidate_id, "metrics": full}


class SuccessorRegretABTests(unittest.TestCase):
    def setUp(self):
        self.runtime = _Runtime()
        self.ab = SuccessorRegretAB(self.runtime)

    def compare(self, *, candidates, policy_value, **kwargs):
        return self.ab.compare(
            loop_id="LOOP-AB",
            expected_state_digest=self.runtime.state["state_digest"],
            completion={"status": "SUCCEEDED", "residuals": []},
            candidates=candidates,
            policy=policy_value,
            **kwargs,
        )

    def test_zero_radius_reproduces_v1_selected_semantics(self):
        rows = [
            candidate("A", utility=0.9, risk=0.2, cost=0.2),
            candidate("B", utility=0.6, risk=0.4, cost=0.4),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=2.0, risk=-1.0, cost=-0.5),
            weight_radii=[0.0, 0.2],
        )
        self.assertEqual(out["status"], "PASS")
        self.assertTrue(out["calibration_pass"])
        self.assertEqual(out["v1"]["selection_tasks"], ("A",))
        zero = out["v2"]["sensitivity"][0]
        self.assertEqual(zero["selection_tasks"], ("A",))

    def test_weight_uncertainty_can_overturn_fragile_v1_winner(self):
        rows = [
            candidate("A", utility=1.0, risk=0.8),
            candidate("B", utility=0.4, risk=0.1),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=2.0, risk=-1.0),
            weight_radii=[0.0, 0.1, 0.25, 1.0],
            analysis_radius=1.0,
        )
        self.assertTrue(out["calibration_pass"])
        self.assertEqual(out["v1"]["selection_tasks"], ("A",))
        self.assertTrue(out["metrics"]["semantic_change_observed"])
        self.assertIsNotNone(out["metrics"]["first_semantic_change_radius"])
        self.assertNotEqual(out["v2"]["sensitivity"][-1]["selection_tasks"], ("A",))

    def test_true_v1_tie_calibrates_at_zero_radius(self):
        rows = [
            candidate("A", utility=1.0, risk=1.0),
            candidate("B", utility=0.0, risk=0.0),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=-1.0),
            weight_radii=[0.0, 1.0],
        )
        self.assertTrue(out["calibration_pass"])
        self.assertEqual(out["v1"]["status"], "AMBIGUOUS")
        self.assertEqual(out["v1"]["selection_tasks"], ("A", "B"))
        self.assertEqual(out["v2"]["sensitivity"][0]["status"], "AMBIGUOUS")

    def test_voc_prefers_cheaper_information_channel(self):
        rows = [
            candidate("A", utility=1.0, risk=1.0),
            candidate("B", utility=0.0, risk=0.0),
        ]
        utility = {
            "lower": {metric: (0.75 if metric == "utility" else 0.0) for metric in ALL_METRICS},
            "upper": {
                metric: (1.0 if metric == "utility" else 0.25 if metric == "risk" else 0.0)
                for metric in ALL_METRICS
            },
        }
        safety = {
            "lower": {metric: (0.75 if metric == "risk" else 0.0) for metric in ALL_METRICS},
            "upper": {
                metric: (1.0 if metric == "risk" else 0.25 if metric == "utility" else 0.0)
                for metric in ALL_METRICS
            },
        }
        outcomes = [
            {"outcome_id": "utility", "probability": 0.5, "weight_bounds": utility},
            {"outcome_id": "safety", "probability": 0.5, "weight_bounds": safety},
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=-1.0),
            weight_radii=[0.0, 1.0],
            analysis_radius=1.0,
            information_actions=[
                {"action_id": "tool-test", "kind": "TEST", "costs": {"tool": 1}, "outcomes": outcomes},
                {
                    "action_id": "ask-human",
                    "kind": "ASK_HUMAN",
                    "costs": {"human_interrupt": 1},
                    "outcomes": outcomes,
                },
            ],
            shadow_prices={"tool": 0.1, "human_interrupt": 0.6},
        )
        self.assertEqual(out["meta_decision"]["status"], "COMPUTE")
        self.assertEqual(out["meta_decision"]["selected"]["action_id"], "tool-test")

    def test_expensive_information_is_pruned_by_regret_upper_bound(self):
        rows = [
            candidate("A", utility=1.0, risk=1.0),
            candidate("B", utility=0.0, risk=0.0),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=-1.0),
            weight_radii=[0.0, 1.0],
            analysis_radius=1.0,
            information_actions=[
                {
                    "action_id": "expensive",
                    "kind": "TEST",
                    "costs": {"tool": 2},
                    "outcomes": [{"outcome_id": "unused", "probability": 1.0}],
                }
            ],
            shadow_prices={"tool": 0.6},
        )
        action = out["meta_decision"]["actions"][0]
        self.assertEqual(action["status"], "PRUNED_BY_REGRET_BOUND")
        self.assertEqual(action["outcomes"], [])
        self.assertEqual(out["meta_decision"]["status"], "STOP_COMPUTING")

    def test_authority_query_remains_outside_information_voc(self):
        rows = [
            candidate("A", utility=1.0, risk=1.0),
            candidate("B", utility=0.0, risk=0.0),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=-1.0),
            weight_radii=[0.0, 1.0],
            analysis_radius=1.0,
            information_actions=[
                {
                    "action_id": "approval",
                    "kind": "ASK_HUMAN",
                    "authority_required": True,
                    "costs": {"human_interrupt": 999},
                }
            ],
            shadow_prices={"human_interrupt": 999},
        )
        action = out["meta_decision"]["actions"][0]
        self.assertEqual(action["status"], "OUTSIDE_INFORMATION_VOC")
        self.assertIsNone(action["net_voc"])

    def test_compare_is_read_only(self):
        before = dict(self.runtime.state)
        rows = [
            candidate("A", utility=0.8, risk=0.2),
            candidate("B", utility=0.6, risk=0.3),
        ]
        self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=-1.0),
            weight_radii=[0.0, 0.2],
        )
        self.assertEqual(self.runtime.state, before)

    def test_incompatible_v1_weight_orientation_holds(self):
        rows = [
            candidate("A", utility=0.8, risk=0.2),
            candidate("B", utility=0.6, risk=0.3),
        ]
        out = self.compare(
            candidates=rows,
            policy_value=policy(utility=1.0, risk=1.0),
            weight_radii=[0.0],
        )
        self.assertEqual(out["status"], "UNSUPPORTED_POLICY_ORIENTATION_HOLD")
        self.assertFalse(out["calibration_pass"])

    def test_box_simplex_support_manual_fixture(self):
        bounds = {
            "lower": {metric: 0.0 for metric in ALL_METRICS},
            "upper": {
                metric: (
                    0.6 if metric == "utility"
                    else 0.8 if metric == "risk"
                    else 1.0 if metric == "cost"
                    else 0.0
                )
                for metric in ALL_METRICS
            },
        }
        coefficients = {metric: 0.0 for metric in ALL_METRICS}
        coefficients.update({"utility": 3.0, "risk": 2.0, "cost": 1.0})
        solved = maximize_linear_over_bounded_simplex(coefficients, bounds)
        self.assertAlmostEqual(solved["value"], 2.6)
        self.assertAlmostEqual(solved["weights"]["utility"], 0.6)
        self.assertAlmostEqual(solved["weights"]["risk"], 0.4)

    def test_extension_routes_read_only_compare_tool(self):
        class FakeRuntime(_Runtime):
            def call_tool(self, name, arguments):
                return {"legacy": name}

        install_regret_ab_extension(FakeRuntime)
        runtime = FakeRuntime()
        out = runtime.call_tool(
            "athena_rehydration_successor_regret_compare",
            {
                "loop_id": "LOOP-AB",
                "expected_state_digest": runtime.state["state_digest"],
                "completion": {"status": "SUCCEEDED", "residuals": []},
                "candidates": [
                    candidate("A", utility=0.9, risk=0.2),
                    candidate("B", utility=0.6, risk=0.4),
                ],
                "policy": policy(utility=1.0, risk=-1.0),
                "weight_radii": [0.0, 0.2],
            },
        )
        self.assertTrue(out["calibration_pass"])
        self.assertEqual(runtime.state["task"], "Current bounded slice")


if __name__ == "__main__":
    unittest.main()
