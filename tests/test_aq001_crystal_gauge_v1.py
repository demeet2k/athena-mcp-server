from __future__ import annotations

import json
import tempfile
import unittest

from athena_mcp.aq001_crystal_gauge_v1 import ARTIFACT, run_semantic_twin_gauge
from athena_mcp.server import Server


class AQ001CrystalGaugeV1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def run_gauge(self):
        return run_semantic_twin_gauge(self.server.crystal)

    def test_semantic_twin_has_zero_typed_semantic_delta(self):
        result = self.run_gauge()
        self.assertEqual(ARTIFACT, result["artifact"])
        self.assertTrue(result["typed_semantic_delta_zero"])
        self.assertEqual(
            {
                "role_delta": 0,
                "decoder_delta": 0,
                "ontology_delta": 0.0,
                "authority_delta": 0,
            },
            result["typed_semantic_delta_start_to_alias"],
        )

    def test_current_traceful_connection_produces_native_nonzero_on_semantic_twin(self):
        result = self.run_gauge()
        arm = result["arms"]["full_traceful_previous_state"]
        self.assertTrue(arm["all_derivational"])
        self.assertEqual("MEASURED", arm["native_holonomy"]["status"])
        self.assertNotEqual({"equal": True}, arm["native_holonomy"]["defect"])

    def test_semantic_history_without_representation_trace_is_zero_on_twin(self):
        result = self.run_gauge()
        arm = result["arms"]["semantic_history_no_representation_trace"]
        self.assertTrue(arm["all_derivational"])
        self.assertEqual("MEASURED", arm["native_holonomy"]["status"])
        self.assertEqual({"equal": True}, arm["native_holonomy"]["defect"])

    def test_endpoint_only_connection_is_zero_on_twin(self):
        result = self.run_gauge()
        arm = result["arms"]["endpoint_only"]
        self.assertTrue(arm["all_derivational"])
        self.assertEqual("MEASURED", arm["native_holonomy"]["status"])
        self.assertEqual({"equal": True}, arm["native_holonomy"]["defect"])

    def test_native_length_three_same_layer_control_is_zero(self):
        result = self.run_gauge()
        arm = result["arms"]["same_layer_native_identity_control"]
        self.assertTrue(arm["all_derivational"])
        self.assertEqual("MEASURED", arm["native_holonomy"]["status"])
        self.assertEqual({"equal": True}, arm["native_holonomy"]["defect"])

    def test_gauge_challenge_downgrades_native_defect_standing(self):
        result = self.run_gauge()
        self.assertEqual("REPRESENTATION_SENSITIVE_RUNTIME_DEFECT", result["classification"], json.dumps(result, indent=2))
        self.assertEqual(
            "REPRESENTATION_SENSITIVE_RUNTIME_DEFECT_NOT_VALIDATED_SEMANTIC_HOLONOMY",
            result["standing"]["native_crystal_holonomy"],
        )
        self.assertEqual("UNKNOWN_NO_VALIDATED_CONNECTION", result["standing"]["mck_closed_loop_holonomy"])
        self.assertEqual("HOLD", result["standing"]["mck_v2_promotion"])
        self.assertEqual(0, result["standing"]["game_reward_delta"])

    def test_all_four_arms_execute_actual_native_closed_routes(self):
        result = self.run_gauge()
        for name, arm in result["arms"].items():
            self.assertTrue(arm["all_derivational"], name)
            self.assertEqual("MEASURED", arm["native_holonomy"]["status"], name)
            self.assertEqual(3, len(arm["route"]), name)

    def test_no_expected_label_or_benchmark_case_is_needed(self):
        result = self.run_gauge()
        rendered = json.dumps(result, sort_keys=True)
        self.assertNotIn("expected_class", rendered)
        self.assertNotIn("HOL-H01", rendered)
        self.assertNotIn("HOL-H02", rendered)
        self.assertNotIn("HOL-H03", rendered)
        self.assertIn("NEGATIVE_RESULT_IS_REUSABLE_EVIDENCE", result["laws"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
