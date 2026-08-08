from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import tempfile
import unittest

from athena_mcp.aq001_crystal_runtime_arm import assay, evaluate_packet
from athena_mcp.server import Server

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "tests" / "fixtures" / "aq001_mythic_holonomy_heldout_v0.json"
SOURCE_BLOB = "1dabde8f450f237d28cf230ff2bb5d9e8d729c8e"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class AQ001CrystalRuntimeExactPacketTests(unittest.TestCase):
    def setUp(self):
        self.data = PACKET_PATH.read_bytes()
        self.packet = json.loads(self.data)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def test_fixture_is_exact_source_git_blob(self):
        self.assertEqual(SOURCE_BLOB, git_blob_sha(self.data))
        self.assertEqual("ATHENA.MYTHIC.HOLONOMY.HELDOUT.V0", self.packet["artifact"])
        self.assertEqual(15, len(self.packet["cases"]))

    def test_exact_frozen_packet_executes_15_of_15_on_real_crystal_substrate(self):
        result = evaluate_packet(self.server.crystal, self.packet)
        score = assay(self.packet, result)
        self.assertEqual((15, 15), (score["matches"], score["total"]), json.dumps(score, indent=2))
        self.assertEqual(0, result["metrics"]["answer_key_reads"])
        self.assertEqual(0, result["metrics"]["standing_amplification_violations"])
        self.assertEqual(0, result["metrics"]["authority_minting_violations"])
        self.assertEqual(2, result["metrics"]["native_holonomy_records"])
        self.assertEqual("NOT_CLAIMED", result["epistemic_boundary"]["production_mck_runtime"])
        self.assertEqual("UNKNOWN_UNTIL_MATCHED_EXTERNAL_EVALUATION", result["epistemic_boundary"]["performance_gain"])

    def test_exact_yijing_loop_vector_and_native_holonomy(self):
        result = evaluate_packet(self.server.crystal, self.packet)
        row = next(x for x in result["cases"] if x["case_id"] == "HOL-H01-04")
        self.assertEqual("NONZERO_HOLONOMY_EXPECTED", row["classification"])
        self.assertEqual(1, row["holonomy_vector"]["role_delta"])
        self.assertEqual(1, row["holonomy_vector"]["decoder_delta"])
        self.assertAlmostEqual(0.875, row["holonomy_vector"]["ontology_delta"])
        self.assertEqual(0, row["holonomy_vector"]["authority_delta"])
        self.assertEqual("MEASURED", row["native_crystal_holonomy"]["status"])
        self.assertNotEqual({"equal": True}, row["native_crystal_holonomy"]["defect"])

    def test_exact_kabbalah_loop_preserves_authority_delta_without_minting(self):
        result = evaluate_packet(self.server.crystal, self.packet)
        row = next(x for x in result["cases"] if x["case_id"] == "HOL-H02-04")
        self.assertEqual("NONZERO_HOLONOMY_EXPECTED", row["classification"])
        self.assertEqual(1, row["holonomy_vector"]["authority_delta"])
        self.assertAlmostEqual(0.909090909091, row["holonomy_vector"]["ontology_delta"])
        self.assertEqual(0, row["authority_minting_violations"])

    def test_exact_path_order_noncommutativity_comes_from_runtime_graph(self):
        result = evaluate_packet(self.server.crystal, self.packet)
        row = next(x for x in result["cases"] if x["case_id"] == "HOL-H03-04")
        self.assertEqual("NONCOMMUTATIVE_EXPECTED", row["classification"])
        self.assertTrue(row["path_order_sensitive"])
        self.assertEqual(
            ["H03.S0.ARABIC_SOURCES", "H03.S2.LATIN_RECEPTION", "H03.S1.HEBREW_IBN_EZRA"],
            row["permuted_path"],
        )
        self.assertIsNone(row["permuted_runtime_route"])
        self.assertIsNotNone(row["permuted_error"])

    def test_exact_packet_answer_key_mutation_cannot_change_arm_behavior(self):
        before = evaluate_packet(self.server.crystal, self.packet)
        altered = copy.deepcopy(self.packet)
        for case in altered["cases"]:
            case["expected_class"] = "DELIBERATELY_WRONG"

        self.server.store.close()
        self.tmp.close()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        after = evaluate_packet(self.server.crystal, altered)

        projection = lambda result: [(row["case_id"], row["classification"]) for row in result["cases"]]
        self.assertEqual(projection(before), projection(after))

    def test_exact_direct_loss_and_provenance_are_not_dropped(self):
        result = evaluate_packet(self.server.crystal, self.packet)
        row = next(x for x in result["cases"] if x["case_id"] == "HOL-H01-01")
        self.assertEqual("ALLOW_WITH_LOSS", row["classification"])
        self.assertIn("SRC.SEP.YIJING", row["audit"]["provenance_tokens"])
        self.assertIn("EDGE::H01.S0.GRAPHIC_SYMBOLS->H01.S1.HEXAGRAM_LINE_STATEMENTS", row["audit"]["provenance_tokens"])
        self.assertIn("graphic symbolic role is expanded by textual statements", row["audit"]["loss_ledger"])
        self.assertIn("hexagram identity remains addressable", row["audit"]["bridge_invariants_declared"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
