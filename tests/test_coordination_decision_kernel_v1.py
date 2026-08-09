from __future__ import annotations

import json
import unittest
from pathlib import Path

from athena_mcp.coordination_decision_kernel_v1 import decide_coordination as decide_v1
from athena_mcp.coordination_decision_kernel_v1_1 import decide_coordination


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "mata_coordination_hold_ab_v0.json"


class CoordinationDecisionKernelV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_all_pre_registered_cases_match_gold_decisions(self):
        cases = self.fixture["cases"]
        self.assertEqual(23, len(cases))
        for row in cases:
            with self.subTest(case_id=row["case_id"]):
                result = decide_coordination(row["input"])
                self.assertEqual("DECIDED", result["status"], result)
                self.assertEqual(row["expected_decision"], result["decision_class"])
                self.assertEqual(
                    row["expected_continuation"], result["continuation_status"]
                )
                self.assertEqual(row["expected_hard_gate"], result["hard_gate_status"])
                self.assertEqual("NONE", result["authority_delta"])
                self.assertEqual("NONE_DECISION_ONLY", result["execution_effect"])

    def test_v1_raw_draft_exposes_preflight_clean_branch_gap(self):
        raw = decide_v1({})
        hardened = decide_coordination({"branch_context": "CLEAN_OWNED"})
        self.assertEqual("STOP_SUCCESS", raw["decision_class"])
        self.assertEqual("KEEP_BRANCH", hardened["decision_class"])
        self.assertNotEqual(raw["decision_class"], hardened["decision_class"])

    def test_global_hold_dominates_clean_branch_convenience(self):
        result = decide_coordination(
            {
                "branch_context": "CLEAN_OWNED",
                "hold_active": True,
                "hold_scope": "GLOBAL",
                "reopening_predicate_satisfied": False,
            }
        )
        self.assertEqual("GLOBAL_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])

    def test_master_conflict_dominates_collision_fusion(self):
        result = decide_coordination(
            {
                "master_moved": True,
                "master_delta_relation": "CONFLICTING",
                "collision_relation": "OVERLAPPING_COMPLEMENTARY",
            }
        )
        self.assertEqual("CONFLICT_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])

    def test_reopening_predicate_dominates_held_value_reserve(self):
        result = decide_coordination(
            {
                "hold_active": True,
                "hold_scope": "LANE_LOCAL",
                "dependency_changed": True,
                "reopening_predicate_satisfied": True,
                "held_lane_value": "POSITIVE",
                "orthogonal_positive_lanes": 3,
            }
        )
        self.assertEqual("REOPEN_HELD_LANE", result["decision_class"])

    def test_unknown_field_fails_closed(self):
        result = decide_coordination({"expected_gold": "CONSUME"})
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("INPUT_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])
        self.assertEqual("NONE", result["authority_delta"])

    def test_inconsistent_hold_shape_fails_closed(self):
        bad_states = [
            {"hold_active": True, "hold_scope": "NONE"},
            {"hold_active": False, "hold_scope": "LANE_LOCAL"},
            {"hold_active": False, "reopening_predicate_satisfied": True},
            {"hold_active": False, "dependency_changed": True},
        ]
        for state in bad_states:
            with self.subTest(state=state):
                result = decide_coordination(state)
                self.assertEqual("HOLD", result["status"])
                self.assertEqual("INPUT_HOLD", result["decision_class"])

    def test_inconsistent_master_shape_fails_closed(self):
        bad_states = [
            {"master_moved": True, "master_delta_relation": "NONE"},
            {"master_moved": False, "master_delta_relation": "DISJOINT"},
        ]
        for state in bad_states:
            with self.subTest(state=state):
                result = decide_coordination(state)
                self.assertEqual("HOLD", result["status"])
                self.assertEqual("INPUT_HOLD", result["decision_class"])

    def test_fixture_contains_no_reward_or_expected_label_inputs(self):
        forbidden = {
            "reward",
            "rarity",
            "game_score",
            "expected_class",
            "expected_gold",
            "treatment_name",
        }
        for row in self.fixture["cases"]:
            self.assertTrue(forbidden.isdisjoint(row["input"]), row["case_id"])

    def test_fixture_hard_laws_preserve_decision_only_boundary(self):
        joined = "\n".join(self.fixture["hard_laws"])
        self.assertIn("no mutating continue", joined)
        self.assertIn("no orthogonal bypass", joined)
        self.assertIn("no synthetic work", joined)
        self.assertIn("never executes work or changes authority", joined)


if __name__ == "__main__":
    unittest.main()
