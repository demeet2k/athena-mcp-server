from __future__ import annotations

import json
import unittest
from pathlib import Path

from athena_mcp.coordination_decision_kernel_v1_2 import decide_coordination


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "mata_coordination_hold_ab_v0.json"


class CoordinationDecisionKernelV12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_v12_preserves_all_23_pre_registered_base_decisions(self):
        self.assertEqual(23, len(self.fixture["cases"]))
        for row in self.fixture["cases"]:
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

    def test_reopening_on_stale_disjoint_frontier_requalifies_before_reopen(self):
        result = decide_coordination(
            {
                "hold_active": True,
                "hold_scope": "LANE_LOCAL",
                "dependency_changed": True,
                "reopening_predicate_satisfied": True,
                "master_moved": True,
                "master_delta_relation": "DISJOINT",
            }
        )
        self.assertEqual("REBRAID_REQUALIFY", result["decision_class"])
        self.assertIn(
            "RECHECK_REOPENING_PREDICATE_AFTER_FRESHNESS",
            result["secondary_actions"],
        )

    def test_reopening_on_conflicting_frontier_holds_before_reopen(self):
        result = decide_coordination(
            {
                "hold_active": True,
                "hold_scope": "LANE_LOCAL",
                "dependency_changed": True,
                "reopening_predicate_satisfied": True,
                "master_moved": True,
                "master_delta_relation": "CONFLICTING",
            }
        )
        self.assertEqual("CONFLICT_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])
        self.assertIn(
            "RECHECK_REOPENING_PREDICATE_AFTER_FRESHNESS",
            result["secondary_actions"],
        )

    def test_polluted_branch_is_cleaned_before_disjoint_rebraid(self):
        result = decide_coordination(
            {
                "branch_context": "POLLUTED",
                "master_moved": True,
                "master_delta_relation": "DISJOINT",
            }
        )
        self.assertEqual("FORK_CLEAN", result["decision_class"])
        self.assertIn("REBRAID_REQUALIFY", result["secondary_actions"])

    def test_polluted_branch_plus_master_conflict_holds(self):
        result = decide_coordination(
            {
                "branch_context": "POLLUTED",
                "master_moved": True,
                "master_delta_relation": "CONFLICTING",
            }
        )
        self.assertEqual("CONFLICT_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])
        self.assertIn(
            "FORK_CLEAN_WHEN_CONFLICT_ROUTE_RESOLVED",
            result["secondary_actions"],
        )

    def test_polluted_branch_plus_unknown_master_delta_cleans_then_compares(self):
        result = decide_coordination(
            {
                "branch_context": "POLLUTED",
                "master_moved": True,
                "master_delta_relation": "UNKNOWN",
            }
        )
        self.assertEqual("FORK_CLEAN", result["decision_class"])
        self.assertIn("REHYDRATE_COMPARE_PARENT", result["secondary_actions"])

    def test_global_hold_still_dominates_pollution_and_master_movement(self):
        result = decide_coordination(
            {
                "branch_context": "POLLUTED",
                "master_moved": True,
                "master_delta_relation": "DISJOINT",
                "hold_active": True,
                "hold_scope": "GLOBAL",
                "reopening_predicate_satisfied": False,
            }
        )
        self.assertEqual("GLOBAL_HOLD", result["decision_class"])
        self.assertEqual("HOLD", result["hard_gate_status"])


if __name__ == "__main__":
    unittest.main()
