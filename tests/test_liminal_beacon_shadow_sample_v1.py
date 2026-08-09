from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest


RUNNER = pathlib.Path(__file__).parent / "experiments" / "liminal_beacon_shadow_sample_v1.py"
MODULE_NAME = "athena_liminal_beacon_shadow_sample_v1"
spec = importlib.util.spec_from_file_location(MODULE_NAME, RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load frozen shadow sample runner")
module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)


class LiminalBeaconShadowSampleV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = module.run_sample()
        print(
            "LIMINAL_BEACON_SHADOW_SAMPLE_RESULT="
            + json.dumps(cls.packet, sort_keys=True, separators=(",", ":"))
        )

    def test_frozen_fixture_is_bound_to_qualified_shadow_parent(self):
        fixture = self.packet["fixture"]
        self.assertEqual(fixture["contract_issue"], 339)
        self.assertEqual(fixture["shadow_parent_head"], "3fa883c40e12ac49e62e8055021b22bf7e5d6861")
        self.assertEqual(fixture["integration_parent_head"], "df74f7388cdb43c36cfdeeff684724b73fdfc117")
        self.assertEqual(fixture["master_ancestry"], "d8bb4cc6e2e6861eeb7141dc52a2efcea252ff36")
        self.assertEqual(fixture["trial_count"], 3)

    def test_all_three_actual_dispatch_trials_pass_frozen_boundaries(self):
        self.assertEqual(len(self.packet["trials"]), 3)
        for trial in self.packet["trials"]:
            with self.subTest(trial=trial["trial"]):
                self.assertEqual(trial["status"], "PASS")
                self.assertTrue(all(trial["criteria"].values()))

    def test_paired_domain_outputs_remain_literal_canonical_equal(self):
        for trial in self.packet["trials"]:
            for pair in trial["pairs"]:
                with self.subTest(trial=trial["trial"], crossing=pair["name"]):
                    self.assertTrue(pair["equal"])
                    self.assertFalse(pair["shadow_injection"])

    def test_seed_is_would_presented_once_then_suppressed_without_receipt(self):
        for trial in self.packet["trials"]:
            self.assertGreaterEqual(trial["first_b_new_would"], 1)
            self.assertEqual(trial["duplicate_b_new_would"], 0)
            self.assertEqual(trial["source_shadow_receipt_count"], 0)
            self.assertEqual(trial["source_shadow_cursor_nonzero_count"], 0)

    def test_unknown_agent_control_never_invents_identity_or_packet(self):
        for trial in self.packet["trials"]:
            self.assertEqual(trial["unknown_agent"], "UNKNOWN")
            self.assertEqual(trial["unknown_packet_delta"], 0)

    def test_live_carrier_isolation_and_fast_plane_firewalls(self):
        for trial in self.packet["trials"]:
            self.assertTrue(trial["live_control"]["equal"])
            self.assertFalse(trial["live_control"]["domain_has_liminal_injection"])
            self.assertEqual(trial["fast_plane_git_write_intent_count"], 0)
            self.assertEqual(trial["durable_bridge_count"], 0)
            self.assertEqual(trial["full_result_leak_count"], 0)
            self.assertEqual(trial["evidence_or_authority_field_count"], 0)

    def test_restart_is_empty_process_local_state_not_continuity_claim(self):
        self.assertTrue(self.packet["restart"]["reset"])
        self.assertEqual(self.packet["restart"]["hidden_process_count"], "UNKNOWN")
        self.assertEqual(self.packet["restart"]["independent_process_count"], "UNKNOWN")

    def test_latency_is_reported_but_not_a_pass_threshold(self):
        latency = self.packet["latency"]
        self.assertEqual(latency["rule"], "MEASUREMENT_ONLY_NO_PASS_THRESHOLD")
        self.assertEqual(latency["off_wall"]["count"], 12)
        self.assertEqual(latency["shadow_wall"]["count"], 12)
        self.assertEqual(latency["overhead_delta"]["count"], 12)
        self.assertIsNotNone(latency["off_wall"]["p50_us"])
        self.assertIsNotNone(latency["shadow_wall"]["p50_us"])

    def test_aggregate_standing_is_scoped_shadow_observation_only(self):
        self.assertEqual(self.packet["status"], "PASS")
        self.assertEqual(self.packet["standing"], "SCOPED_ACTUAL_DISPATCH_SHADOW_OBSERVATION")
        self.assertEqual(self.packet["hidden_process_count"], "UNKNOWN")
        self.assertEqual(self.packet["independent_process_count"], "UNKNOWN")
        self.assertIn("SHADOW_PASS != ACTIVATION", self.packet["firewalls"])
        self.assertIn("SHADOW_PASS != CANONICAL_PROMOTION", self.packet["firewalls"])


if __name__ == "__main__":
    unittest.main()
