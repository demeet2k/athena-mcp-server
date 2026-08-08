import unittest
from copy import deepcopy

from athena_mcp.mythic_holonomy_runtime import MythicHolonomyRuntime
from mck_holonomy_fixture import PACKET


class MythicHolonomyAlchemyHardeningTests(unittest.TestCase):
    def setUp(self):
        self.runtime=MythicHolonomyRuntime()
        self.result=self.runtime.evaluate(PACKET)
        self.index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}

    def test_raw_arms_and_edge_support_do_not_read_expected_class(self):
        altered=deepcopy(PACKET)
        for case in altered["cases"]:
            case["expected_class"]="DELIBERATELY_WRONG"
        _,layers_before=self.runtime._index(PACKET)
        _,layers_after=self.runtime._index(altered)
        edges_before=self.runtime._lawful_transport_edges(PACKET["cases"])
        edges_after=self.runtime._lawful_transport_edges(altered["cases"])
        self.assertEqual(edges_before,edges_after)
        for before,after in zip(PACKET["cases"],altered["cases"]):
            self.assertEqual(self.runtime._a0(before,layers_before),self.runtime._a0(after,layers_after))
            self.assertEqual(self.runtime._a1(before,layers_before),self.runtime._a1(after,layers_after))
            self.assertEqual(
                self.runtime._a2(before,layers_before,edges_before),
                self.runtime._a2(after,layers_after,edges_after),
            )

    def test_noncommutativity_requires_independent_transport_support_not_answer_key(self):
        packet=deepcopy(PACKET)
        family="H03.IBN_EZRA_TRANSMISSION"
        source="SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"
        packet["cases"].extend([
            {
                "case_id":"ADV-H03-S0-S2","family_id":family,
                "path":["H03.S0.ARABIC_SOURCES","H03.S2.LATIN_RECEPTION"],
                "operation":"SEMANTIC_TRANSPORT","expected_class":"DELIBERATELY_WRONG",
                "source_refs":[source],"bridge_invariants":["control edge"],
                "declared_loss":["control loss"],
            },
            {
                "case_id":"ADV-H03-S2-S1","family_id":family,
                "path":["H03.S2.LATIN_RECEPTION","H03.S1.HEBREW_IBN_EZRA"],
                "operation":"SEMANTIC_TRANSPORT","expected_class":"DELIBERATELY_WRONG",
                "source_refs":[source],"bridge_invariants":["control edge"],
                "declared_loss":["control loss"],
            },
        ])
        result=MythicHolonomyRuntime().evaluate(packet)
        index={c["case_id"]:i for i,c in enumerate(packet["cases"])}
        order=result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][index["HOL-H03-04"]]
        self.assertTrue(order["canonical_supported_by_frozen_transport_cases"])
        self.assertTrue(order["permuted_supported_by_frozen_transport_cases"])
        self.assertFalse(order["path_order_sensitive"])
        self.assertFalse(order["expected_pass"])

    def test_original_path_order_receipt_exposes_independent_support(self):
        order=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H03-04"]]
        self.assertTrue(order["canonical_supported_by_frozen_transport_cases"])
        self.assertFalse(order["permuted_supported_by_frozen_transport_cases"])
        self.assertTrue(order["path_order_sensitive"])
        self.assertEqual(order["law"],"PATH_ORDER_CLAIM_REQUIRES_INDEPENDENT_FROZEN_TRANSPORT_EDGE_SUPPORT")

    def test_projection_defaults_are_labeled_as_assumptions_not_source_evidence(self):
        row=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H03-01"]]
        receipt=row["composition"]["receipts"][0]
        self.assertEqual(receipt["projection_assumption_standing"],"SYNTHETIC_ADAPTER_METADATA_NOT_SOURCE_EVIDENCE")
        fields={(x.get("side"),x.get("field"),x.get("basis")) for x in receipt["projection_assumptions"]}
        self.assertIn(("source","category_scope","ADAPTER_DEFAULT"),fields)
        self.assertIn(("target","corpus_mutability","ADAPTER_DEFAULT"),fields)
        self.assertTrue(any(x.get("field")=="evidence_standing" and "NOT_SOURCE_ATTESTED" in x.get("basis","") for x in receipt["projection_assumptions"]))
        self.assertEqual(self.result["projection_policy"]["standing"],"SYNTHETIC_ADAPTER_METADATA_NOT_SOURCE_EVIDENCE")

    def test_untyped_prose_loss_does_not_fake_typed_feature_coverage(self):
        loop=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-04"]]
        self.assertIsNone(loop["holonomy_vector"]["unaccounted_loss"])
        self.assertEqual(loop["unaccounted_loss_standing"],"UNKNOWN_UNTYPED_LOSS_LEDGER")
        self.assertTrue(loop["holonomy_nonzero"])
        control=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-05"]]
        self.assertEqual(control["holonomy_vector"]["unaccounted_loss"],0)
        self.assertEqual(control["unaccounted_loss_standing"],"KNOWN_TYPED_OR_ZERO_CHANGE")

    def test_complete_metric_surface_exposes_unknowns_instead_of_scalarizing(self):
        summary=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["summary"]
        self.assertEqual(summary["lawful_bridge_total"],7)
        self.assertEqual(summary["lawful_bridges_retained"],7)
        self.assertEqual(summary["false_holds_on_lawful_transport"],0)
        self.assertEqual(summary["path_order_sensitive_cases"],1)
        self.assertEqual(summary["holonomy_vector_unaccounted_loss_unknown_cases"],2)
        self.assertEqual(summary["holonomy_vector_unaccounted_loss_known_total"],0)
        self.assertEqual(summary["textual_invariant_checks_unknown"],10)
        self.assertGreater(summary["projection_assumption_receipts"],0)
        self.assertEqual(self.result["scalarization"],"DISABLED_V0")
        self.assertIn("STRING_INVARIANT_RETENTION != SEMANTIC_INVARIANT_VALIDATION",self.result["laws"])


if __name__=="__main__":
    unittest.main()
