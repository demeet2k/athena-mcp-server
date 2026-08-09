from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "liminal_beacon_effect_v11_replay.py"
SPEC = importlib.util.spec_from_file_location("liminal_beacon_effect_v11_replay", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class LiminalBeaconEffectV11ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.run_replay(parent_ci_green=True)
        print("LIMINAL_BEACON_V11_REPLAY_RESULT=" + json.dumps(cls.result, sort_keys=True))

    def test_replay_is_bound_to_frozen_successor_head(self):
        self.assertEqual(
            "7b58380c6ec81f8e47bae6ad38c042a492a5f20a",
            self.result["parent_candidate_head"],
        )
        self.assertEqual(
            "429a480a80eeefb9e2bff1ea3015adf571d76b0e",
            self.result["parent_runtime_base"],
        )
        for field in ("historical_fixture_digest", "replay_fixture_digest", "treatment_delta_digest"):
            self.assertEqual(64, len(self.result[field]))

    def test_primary_discovery_gain_is_preserved_without_rescoring_v1(self):
        metrics = self.result["metrics"]
        self.assertEqual(0.0, metrics["missed_material_delta_rate"])
        self.assertEqual(0, metrics["accidental_duplicate_action_count"])
        self.assertLessEqual(metrics["time_to_first_useful_sibling_discovery"], 10.0)
        historical = self.result["historical_v1_challenger"]
        self.assertEqual("FAIL", historical["comparison_status"])
        self.assertEqual(0.0, historical["correction_reach"])
        self.assertFalse(historical["critical_blocker_presented"])

    def test_typed_correction_closes_observed_reverse_route_gap(self):
        metrics = self.result["metrics"]
        self.assertEqual(1.0, metrics["correction_reach"])
        self.assertTrue(metrics["reverse_correction_route"])
        self.assertEqual("RUNTIME_METADATA_ONLY", metrics["semantic_evidence_ceiling"])
        self.assertTrue(metrics["full_tool_result_absent_from_semantic_packet"])

    def test_bounded_critical_reserve_closes_overload_gap_without_bypass(self):
        metrics = self.result["metrics"]
        self.assertTrue(metrics["critical_blocker_presented"])
        self.assertTrue(metrics["critical_blocker_reserved"])
        self.assertLessEqual(metrics["max_critical_reserve_used"], 1)
        self.assertTrue(metrics["low_salience_filtered"])
        self.assertTrue(metrics["direct_low_salience_filtered"])

    def test_scope_restart_budget_and_persistence_boundaries_hold(self):
        metrics = self.result["metrics"]
        self.assertTrue(metrics["guild_scope_isolated"])
        self.assertTrue(metrics["restart_epoch_rotated"])
        self.assertEqual(0, metrics["stale_or_scope_invalid_presentation_count"])
        self.assertEqual(0, metrics["existing_tool_regression_count"])
        self.assertEqual(0, metrics["durable_coordination_git_write_count"])
        self.assertTrue(metrics["hard_context_budget_preserved"])
        for view in self.result["rendezvous_accounting"]:
            if view["context_budget"]:
                self.assertLessEqual(view["context_used"], view["context_budget"])
            self.assertLessEqual(view["critical_reserve_used"], view["critical_quota"])

    def test_complete_frozen_replay_rule_passes(self):
        self.assertEqual("PASS", self.result["status"])
        self.assertTrue(all(value is True for value in self.result["criteria"].values()))
        self.assertEqual(
            "MATCHED_DETERMINISTIC_REPLAY_NOT_GENERAL_CAUSAL_EFFECT",
            self.result["standing"],
        )

    def test_missing_parent_ci_witness_prevents_full_pass(self):
        result = MODULE.run_replay(parent_ci_green=False)
        self.assertEqual("UNKNOWN", result["metrics"]["existing_tool_regression_count"])
        self.assertEqual("UNKNOWN", result["criteria"]["existing_tools"])
        self.assertEqual("UNKNOWN", result["status"])


if __name__ == "__main__":
    unittest.main()
