from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "liminal_beacon_v11_heldout_matrix.py"
SPEC = importlib.util.spec_from_file_location("liminal_beacon_v11_heldout_matrix", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class LiminalBeaconV11HeldOutMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.run_matrix(parent_ci_green=True)
        print("LIMINAL_BEACON_V11_HELDOUT_RESULT=" + json.dumps(cls.result, sort_keys=True))

    def test_matrix_is_bound_to_exact_tested_parent(self):
        self.assertEqual(
            "7b58380c6ec81f8e47bae6ad38c042a492a5f20a",
            self.result["parent_candidate_head"],
        )
        self.assertEqual(
            "429a480a80eeefb9e2bff1ea3015adf571d76b0e",
            self.result["parent_runtime_base"],
        )
        self.assertEqual(64, len(self.result["fixture_digest"]))

    def test_all_nine_frozen_scenarios_exist(self):
        self.assertEqual(
            {"H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"},
            set(self.result["scenarios"]),
        )

    def test_each_held_out_scenario_passes_its_predeclared_rule(self):
        failures = {
            sid: row
            for sid, row in self.result["scenarios"].items()
            if row["status"] != "PASS"
        }
        self.assertEqual({}, failures)
        for row in self.result["scenarios"].values():
            self.assertTrue(all(value is True for value in row["criteria"].values()))
            self.assertEqual(64, len(row["fixture_digest"]))
            self.assertEqual(64, len(row["treatment_digest"]))

    def test_aggregate_frozen_rule_passes_without_boundary_violation(self):
        aggregate = self.result["aggregate"]
        self.assertEqual("PASS", aggregate["status"])
        self.assertTrue(all(value is True for value in aggregate["criteria"].values()))
        self.assertEqual(0, aggregate["full_result_leak_count"])
        self.assertEqual(0, aggregate["evidence_ceiling_violation_count"])
        self.assertEqual(0, aggregate["false_presented_receipt_count"])
        self.assertEqual(0, aggregate["durable_coordination_git_write_count"])
        self.assertEqual(0, aggregate["existing_tool_regression_count"])
        self.assertLessEqual(aggregate["max_critical_reserve_used"], 1)
        self.assertTrue(aggregate["hard_context_budget_preserved"])
        self.assertEqual(
            "REPEATED_DETERMINISTIC_HELD_OUT_FIXTURE_SUPPORT",
            self.result["standing"],
        )

    def test_negative_controls_are_fail_closed_or_inert(self):
        rows = self.result["scenarios"]
        self.assertTrue(rows["H0"]["criteria"]["unrelated_packet_absent"])
        self.assertTrue(rows["H4"]["criteria"]["oversized_critical_absent"])
        self.assertTrue(rows["H5"]["criteria"]["all_malformed_cases_hold"])
        self.assertTrue(rows["H6"]["criteria"]["guild_packet_absent"])
        self.assertTrue(rows["H7"]["criteria"]["addressed_local_attention_filtered"])
        self.assertTrue(rows["H8"]["criteria"]["explicit_identity_deterministic"])

    def test_generalization_routes_are_not_original_object_fixture_only(self):
        rows = self.result["scenarios"]
        self.assertTrue(rows["H1"]["criteria"]["late_dependency_discovery"])
        self.assertTrue(rows["H1"]["criteria"]["reverse_correction_after_departure"])
        self.assertTrue(rows["H2"]["criteria"]["late_multiplex_discovery"])
        self.assertTrue(rows["H3"]["criteria"]["highest_ranked_blocker_reserved"])

    def test_repeated_matrix_preserves_decision_packets_not_ephemeral_ids(self):
        second = MODULE.run_matrix(parent_ci_green=True)
        self.assertEqual(self.result["fixture_digest"], second["fixture_digest"])
        self.assertEqual(self.result["aggregate"], second["aggregate"])
        self.assertEqual(self.result["standing"], second["standing"])
        for sid in self.result["scenarios"]:
            first_row = self.result["scenarios"][sid]
            second_row = second["scenarios"][sid]
            for field in ("fixture_digest", "treatment_digest", "metrics", "criteria", "status"):
                self.assertEqual(first_row[field], second_row[field])
        # Raw packet ids/session epochs are intentionally not compared.

    def test_missing_parent_ci_witness_forces_aggregate_unknown(self):
        result = MODULE.run_matrix(parent_ci_green=False)
        self.assertEqual("UNKNOWN", result["aggregate"]["status"])
        self.assertEqual("UNKNOWN", result["aggregate"]["existing_tool_regression_count"])
        self.assertEqual("UNKNOWN", result["aggregate"]["criteria"]["existing_tool_regressions"])


if __name__ == "__main__":
    unittest.main()
