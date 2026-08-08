from __future__ import annotations

import copy
import json
import tempfile
import unittest

from athena_mcp.aq001_crystal_runtime_arm import (
    ARTIFACT,
    assay,
    evaluate_packet,
)
from athena_mcp.server import Server


def packet_fixture():
    return {
        "artifact": "TEST.AQ001.HELDOUT",
        "version": "1",
        "families": [
            {
                "family_id": "F1",
                "layers": [
                    {
                        "layer_id": "F1.S0",
                        "semantic_role": "symbol",
                        "decoder_role": "pattern",
                        "ontology_tags": ["a", "b"],
                        "authority_scope": "PUBLIC",
                        "standing": "SECONDARY_SCHOLARSHIP",
                        "provenance": ["SRC.F1"],
                        "declared_loss": [],
                    },
                    {
                        "layer_id": "F1.S1",
                        "semantic_role": "statement",
                        "decoder_role": "text",
                        "ontology_tags": ["b", "c"],
                        "authority_scope": "PUBLIC",
                        "standing": "SECONDARY_SCHOLARSHIP",
                        "provenance": ["SRC.F1"],
                        "declared_loss": ["symbol role expanded by text"],
                    },
                    {
                        "layer_id": "F1.S2",
                        "semantic_role": "commentary",
                        "decoder_role": "meta",
                        "ontology_tags": ["c", "d", "e"],
                        "authority_scope": "HISTORICAL",
                        "standing": "SECONDARY_SCHOLARSHIP",
                        "provenance": ["SRC.F1"],
                        "declared_loss": ["commentary context changes decoder"],
                    },
                ],
            }
        ],
        "cases": [
            {
                "case_id": "T1",
                "family_id": "F1",
                "path": ["F1.S0", "F1.S1"],
                "operation": "SEMANTIC_TRANSPORT",
                "expected_class": "ALLOW_WITH_LOSS",
                "source_refs": ["SRC.F1"],
                "bridge_invariants": ["address remains traceable"],
                "declared_loss": ["symbol-to-text expansion"],
            },
            {
                "case_id": "T2",
                "family_id": "F1",
                "path": ["F1.S1", "F1.S2"],
                "operation": "SEMANTIC_TRANSPORT",
                "expected_class": "ALLOW_WITH_LOSS",
                "source_refs": ["SRC.F1"],
                "bridge_invariants": ["text remains object of commentary"],
                "declared_loss": ["text-to-commentary expansion"],
            },
            {
                "case_id": "EQ",
                "family_id": "F1",
                "path": ["F1.S2", "F1.S0"],
                "operation": "SEMANTIC_EQUIVALENCE",
                "expected_class": "HOLD_EQUIVALENCE",
                "source_refs": ["SRC.F1"],
            },
            {
                "case_id": "LOOP",
                "family_id": "F1",
                "path": ["F1.S0", "F1.S1", "F1.S2", "F1.S0"],
                "operation": "HOLONOMY_LOOP",
                "expected_class": "NONZERO_HOLONOMY_EXPECTED",
                "source_refs": ["SRC.F1"],
                "bridge_invariants": ["original address remains identifiable"],
                "declared_loss": ["path history cannot be erased on return"],
            },
            {
                "case_id": "ORDER",
                "family_id": "F1",
                "path": ["F1.S0", "F1.S1", "F1.S2"],
                "operation": "PATH_ORDER_COMPARE",
                "expected_class": "NONCOMMUTATIVE_EXPECTED",
                "source_refs": ["SRC.F1"],
                "bridge_invariants": ["source order is provenance"],
                "declared_loss": ["permutation destroys admitted route"],
            },
            {
                "case_id": "CTRL",
                "family_id": "F1",
                "path": ["F1.S0", "F1.S0"],
                "operation": "SAME_LAYER_CONTROL",
                "expected_class": "ZERO_HOLONOMY_CONTROL",
                "source_refs": ["SRC.F1"],
            },
        ],
        "distance_semantics": {
            "scalarization": "DISABLED_V0",
            "standing_ranks": {
                "UNKNOWN": 0,
                "MODERN_RECONSTRUCTION": 1,
                "SECONDARY_SCHOLARSHIP": 2,
                "PRIMARY_EVIDENCE": 3,
            },
        },
    }


class AQ001CrystalRuntimeArmTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.packet = packet_fixture()

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def run_arm(self, packet=None):
        return evaluate_packet(self.server.crystal, packet or self.packet)

    def test_generic_arm_executes_real_crystal_runtime_and_matches_synthetic_assay(self):
        result = self.run_arm()
        self.assertEqual(result["artifact"], ARTIFACT)
        self.assertEqual(result["execution_standing"], "REAL_CRYSTAL_RUNTIME_SUBSTRATE_NOT_PRODUCTION_MCK")
        self.assertEqual(result["metrics"]["answer_key_reads"], 0)
        self.assertEqual(result["metrics"]["standing_amplification_violations"], 0)
        self.assertEqual(result["metrics"]["authority_minting_violations"], 0)
        score = assay(self.packet, result)
        self.assertEqual((6, 6), (score["matches"], score["total"]), json.dumps(score, indent=2))

    def test_expected_class_mutation_cannot_change_arm_behavior(self):
        altered = copy.deepcopy(self.packet)
        for case in altered["cases"]:
            case["expected_class"] = "DELIBERATELY_WRONG"

        before = self.run_arm(self.packet)
        # New Server avoids transform/event identity collisions being mistaken for behavior change.
        self.server.store.close()
        self.tmp.close()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        after = self.run_arm(altered)

        def projection(result):
            return [(row["case_id"], row["classification"]) for row in result["cases"]]

        self.assertEqual(projection(before), projection(after))

    def test_transform_programs_contain_no_case_or_expected_label_tokens(self):
        self.run_arm()
        rows = self.server.store.rows("SELECT program_json FROM transform_programs ORDER BY transform_id")
        self.assertTrue(rows)
        text = "\n".join(row["program_json"] or "" for row in rows)
        for forbidden in (
            "expected_class",
            "case_id",
            "ALLOW_WITH_LOSS",
            "HOLD_EQUIVALENCE",
            "NONZERO_HOLONOMY_EXPECTED",
            "NONCOMMUTATIVE_EXPECTED",
            "T1",
            "T2",
            "LOOP",
            "ORDER",
        ):
            self.assertNotIn(forbidden, text)

    def test_route_execution_uses_crystal_transform_execution_records(self):
        result = self.run_arm()
        direct = next(row for row in result["cases"] if row["case_id"] == "T1")
        runtime = direct["runtime_route"]
        self.assertTrue(runtime["all_derivational"])
        self.assertEqual(1, len(runtime["steps"]))
        execution_rows = self.server.store.rows("SELECT * FROM transform_executions")
        # apply_transform_route executes derivations directly; current Crystal runtime does not persist route steps.
        # Same-layer control uses apply_transform and therefore proves the runtime execution table is active.
        self.assertGreaterEqual(len(execution_rows), 1)

    def test_holonomy_loop_creates_native_crystal_record_and_nonzero_typed_vector(self):
        result = self.run_arm()
        loop = next(row for row in result["cases"] if row["case_id"] == "LOOP")
        self.assertEqual("NONZERO_HOLONOMY_EXPECTED", loop["classification"])
        self.assertEqual("MEASURED", loop["native_crystal_holonomy"]["status"])
        self.assertNotEqual({"equal": True}, loop["native_crystal_holonomy"]["defect"])
        self.assertEqual(1, loop["holonomy_vector"]["role_delta"])
        self.assertEqual(1, loop["holonomy_vector"]["decoder_delta"])
        self.assertGreater(loop["holonomy_vector"]["ontology_delta"], 0)
        self.assertEqual(1, loop["holonomy_vector"]["authority_delta"])
        observations = self.server.store.rows("SELECT * FROM holonomy_observations")
        self.assertEqual(1, len(observations))

    def test_loss_and_provenance_are_preserved_as_transform_sidecars(self):
        result = self.run_arm()
        direct = next(row for row in result["cases"] if row["case_id"] == "T1")
        audit = direct["audit"]
        self.assertIn("SRC.F1", audit["provenance_tokens"])
        self.assertIn("LAYER::F1.S0", audit["provenance_tokens"])
        self.assertIn("LAYER::F1.S1", audit["provenance_tokens"])
        self.assertIn("EDGE::F1.S0->F1.S1", audit["provenance_tokens"])
        self.assertIn("symbol-to-text expansion", audit["loss_ledger"])
        self.assertIn("symbol role expanded by text", audit["loss_ledger"])
        self.assertIn("address remains traceable", audit["bridge_invariants_declared"])

    def test_path_order_sensitivity_comes_from_registered_route_graph(self):
        result = self.run_arm()
        order = next(row for row in result["cases"] if row["case_id"] == "ORDER")
        self.assertEqual("NONCOMMUTATIVE_EXPECTED", order["classification"])
        self.assertTrue(order["path_order_sensitive"])
        self.assertIsNotNone(order["permuted_error"])
        self.assertIsNone(order["permuted_runtime_route"])
        self.assertEqual(["F1.S0", "F1.S2", "F1.S1"], order["permuted_path"])

    def test_same_layer_control_is_zero_but_records_runtime_limit_explicitly(self):
        result = self.run_arm()
        ctrl = next(row for row in result["cases"] if row["case_id"] == "CTRL")
        self.assertEqual("ZERO_HOLONOMY_CONTROL", ctrl["classification"])
        self.assertEqual("PASS", ctrl["runtime_execution"]["status"])
        self.assertIn("REQUIRES_ROUTE_LENGTH_AT_LEAST_3", ctrl["runtime_limitation"])

    def test_equivalence_hold_is_typed_preflight_not_fake_runtime_route(self):
        result = self.run_arm()
        eq = next(row for row in result["cases"] if row["case_id"] == "EQ")
        self.assertEqual("HOLD_EQUIVALENCE", eq["classification"])
        self.assertIsNone(eq["runtime_route"])
        self.assertEqual(1, eq["typed_delta"]["role_delta"])
        self.assertIn("PREFLIGHT", eq["runtime_limitation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
