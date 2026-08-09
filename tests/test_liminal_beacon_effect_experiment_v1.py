from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "liminal_beacon_effect_v1.py"
SPEC = importlib.util.spec_from_file_location("liminal_beacon_effect_v1", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class LiminalBeaconEffectExperimentV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.run_experiment(parent_ci_green=True)

    def test_fixture_is_bound_to_exact_parent_candidate(self):
        result = self.result
        self.assertEqual(
            "87b5f3b34271e68f5c2d6e712ea8efeab49740df",
            result["parent_candidate_head"],
        )
        self.assertEqual(
            "114790cf5173ca5ab78d1b505849708b209f81a0",
            result["parent_runtime_base"],
        )
        self.assertTrue(result["parent_ci_green"])
        self.assertEqual(64, len(result["fixture_digest"]))

    def test_baseline_has_manual_poll_delay_and_duplicate_action(self):
        metrics = self.result["baseline"]["metrics"]
        self.assertEqual(1.0, metrics["missed_material_delta_rate"])
        self.assertEqual(1, metrics["accidental_duplicate_action_count"])
        self.assertEqual(30.0, metrics["time_to_first_useful_sibling_discovery"])
        self.assertEqual(1.0, metrics["correction_reach"])
        self.assertEqual(2, metrics["durable_coordination_git_write_count"])

    def test_challenger_discovers_unknown_sender_delta_on_topology_entry(self):
        metrics = self.result["challenger"]["metrics"]
        self.assertEqual(0.0, metrics["missed_material_delta_rate"])
        self.assertEqual(0, metrics["accidental_duplicate_action_count"])
        self.assertEqual(10.0, metrics["time_to_first_useful_sibling_discovery"])
        self.assertEqual(0, metrics["durable_coordination_git_write_count"])
        self.assertEqual(0.0, metrics["git_write_amplification"])

    def test_attention_scope_and_restart_guards_hold_in_scored_fixture(self):
        metrics = self.result["challenger"]["metrics"]
        self.assertTrue(metrics["low_salience_filtered"])
        self.assertTrue(metrics["critical_blocker_presented"])
        self.assertTrue(metrics["direct_low_salience_filtered"])
        self.assertTrue(metrics["guild_scope_isolated"])
        self.assertTrue(metrics["restart_epoch_rotated"])
        self.assertEqual(0, metrics["stale_or_scope_invalid_presentation_count"])
        self.assertEqual(0, metrics["existing_tool_regression_count"])

    def test_scored_challenger_exposes_current_autohook_correction_gap(self):
        metrics = self.result["challenger"]["metrics"]
        # The current V1 autohook can surface the correction-like tool event via
        # the scout path, but does not derive correction_of(D1) from arbitrary
        # result metadata. Do not mis-credit that presentation as reverse causal
        # correction reach.
        self.assertTrue(metrics["correction_was_presented_by_any_route"])
        self.assertEqual(0.0, metrics["correction_reach"])
        comparison = self.result["comparison"]
        self.assertFalse(comparison["criteria"]["scripted_reverse_correction_reach"])
        self.assertEqual("FAIL", comparison["status"])

    def test_failure_does_not_erase_primary_improvements(self):
        comparison = self.result["comparison"]
        self.assertTrue(comparison["criteria"]["missed_delta_non_regression"])
        self.assertTrue(comparison["criteria"]["duplicate_non_regression"])
        self.assertTrue(comparison["criteria"]["strict_primary_improvement"])
        self.assertEqual(-1.0, comparison["primary_deltas"]["missed_material_delta_rate"])
        self.assertEqual(-1, comparison["primary_deltas"]["accidental_duplicate_action_count"])
        self.assertEqual(-20.0, comparison["primary_deltas"]["discovery_latency"])
        self.assertEqual(
            "MATCHED_DETERMINISTIC_FIXTURE_DIFFERENCE_NOT_GENERAL_CAUSAL_EFFECT",
            comparison["interpretation_ceiling"],
        )

    def test_without_parent_ci_existing_tool_regression_stays_unknown(self):
        result = MODULE.run_experiment(parent_ci_green=False)
        self.assertEqual(
            "UNKNOWN",
            result["challenger"]["metrics"]["existing_tool_regression_count"],
        )
        self.assertEqual(
            "UNKNOWN",
            result["comparison"]["criteria"]["no_existing_tool_regression"],
        )

    def test_simulated_instances_do_not_claim_real_process_independence(self):
        state = self.result["challenger"]["state_summary"]
        self.assertEqual("UNKNOWN", state["hidden_process_count"])
        self.assertEqual("UNKNOWN", state["independent_process_count"])


if __name__ == "__main__":
    unittest.main()
