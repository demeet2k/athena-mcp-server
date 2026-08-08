import unittest

from athena_mcp.mythic_holonomy_protocol import HOLONOMY_RESOURCE,HOLONOMY_TOOL_NAMES
from athena_mcp.mythic_holonomy_runtime import MythicHolonomyRuntime
from athena_mcp.mythic_holonomy_surface import MythicHolonomySurface
from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES,AOR_DEVELOPMENT_RESOURCES
from mck_holonomy_fixture import PACKET,SOURCE_PACKET_BLOB_SHA,SOURCE_PACKET_COMMIT,SOURCE_PACKET_PATH,FIXTURE_STANDING


class MythicHolonomyEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.runtime=MythicHolonomyRuntime()
        self.result=self.runtime.evaluate(PACKET,source_packet_ref=f"demeet2k/Athena@{SOURCE_PACKET_COMMIT}:{SOURCE_PACKET_PATH}",source_packet_blob_sha=SOURCE_PACKET_BLOB_SHA)

    def test_frozen_projection_identity_is_explicit_and_not_remotely_verified(self):
        self.assertEqual(SOURCE_PACKET_COMMIT,"c1858bcbc6587296c2b8a7e29642bfef695fdb2a")
        self.assertEqual(SOURCE_PACKET_BLOB_SHA,"1dabde8f450f237d28cf230ff2bb5d9e8d729c8e")
        self.assertIn("NOT_INDEPENDENT_SOURCE_COPY",FIXTURE_STANDING)
        self.assertEqual(self.result["source_packet_blob_sha"],SOURCE_PACKET_BLOB_SHA)
        self.assertFalse(self.result["source_packet_ref_verified"])
        self.assertIn("CALLER_PACKET_REF != VERIFIED_REMOTE_READ",self.result["laws"])

    def test_packet_shape_and_scalarization_are_frozen(self):
        self.assertEqual(self.result["status"],"HELD_OUT_PACKET_EVALUATED")
        self.assertEqual(self.result["packet_identity"]["families"],3)
        self.assertEqual(self.result["packet_identity"]["cases"],15)
        self.assertEqual(self.result["scalarization"],"DISABLED_V0")
        self.assertGreaterEqual(len(self.result["distance_semantics"]["vector"]),8)

    def test_arm_expected_class_separation_is_10_12_15(self):
        arms=self.result["arms"]
        self.assertEqual(arms["A0_UNSCOPED_REFERENCE"]["summary"]["expected_class_passed"],10)
        self.assertEqual(arms["A1_EDGEWISE_STRATA"]["summary"]["expected_class_passed"],12)
        self.assertEqual(arms["A2_COMPOSED_HOLONOMY"]["summary"]["expected_class_passed"],15)

    def test_equivalence_is_repaired_before_holonomy_composition(self):
        arms=self.result["arms"]
        self.assertEqual(arms["A0_UNSCOPED_REFERENCE"]["summary"]["false_equivalence_claims"],2)
        self.assertEqual(arms["A1_EDGEWISE_STRATA"]["summary"]["false_equivalence_claims"],0)
        self.assertEqual(arms["A2_COMPOSED_HOLONOMY"]["summary"]["false_equivalence_claims"],0)

    def test_lawful_transport_is_not_sacrificed_by_strata_or_holonomy(self):
        for arm in self.result["arms"].values():
            self.assertEqual(arm["summary"]["lawful_bridges_retained"],7)
            self.assertEqual(arm["summary"]["false_holds_on_lawful_transport"],0)
        self.assertEqual(self.result["arms"]["A2_COMPOSED_HOLONOMY"]["summary"]["standing_amplification_violations"],0)
        self.assertEqual(self.result["arms"]["A2_COMPOSED_HOLONOMY"]["summary"]["authority_minting_violations"],0)

    def test_yijing_and_kabbalah_loops_have_nonzero_representation_holonomy_only_in_a2(self):
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        a0=self.result["arms"]["A0_UNSCOPED_REFERENCE"]["results"]
        a1=self.result["arms"]["A1_EDGEWISE_STRATA"]["results"]
        a2=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"]
        for cid in ["HOL-H01-04","HOL-H02-04"]:
            i=index[cid]
            self.assertFalse(a0[i]["holonomy_nonzero"])
            self.assertIsNone(a1[i]["holonomy_nonzero"])
            self.assertTrue(a2[i]["holonomy_nonzero"])
            self.assertTrue(a2[i]["expected_pass"])
            self.assertIn("H_gamma_IS_REPRESENTATION_DRIFT_VECTOR_NOT_METAPHYSICAL_QUANTITY",a2[i]["law"])

    def test_same_layer_controls_have_zero_vector(self):
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        a2=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"]
        for cid in ["HOL-H01-05","HOL-H02-05","HOL-H03-05"]:
            r=a2[index[cid]]
            self.assertFalse(r["holonomy_nonzero"])
            self.assertTrue(r["expected_pass"])
            self.assertTrue(all(float(x)==0 for x in r["holonomy_vector"].values()))

    def test_arabic_hebrew_latin_path_is_allowed_but_equivalence_and_commutativity_are_not(self):
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        a2=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"]
        self.assertTrue(a2[index["HOL-H03-01"]]["allowed"])
        self.assertTrue(a2[index["HOL-H03-02"]]["allowed"])
        eq=a2[index["HOL-H03-03"]]
        self.assertFalse(eq["allowed"]);self.assertTrue(eq["expected_pass"])
        order=a2[index["HOL-H03-04"]]
        self.assertTrue(order["allowed"]);self.assertTrue(order["path_order_sensitive"]);self.assertTrue(order["expected_pass"])

    def test_vector_remains_visible_instead_of_becoming_scalar_victory_score(self):
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        r=self.result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][index["HOL-H02-04"]]
        self.assertTrue(r["expected_pass"])
        self.assertEqual(set(r["holonomy_vector"]),{"role_delta","decoder_delta","ontology_delta","authority_delta","standing_delta","provenance_delta","invariant_violations","unaccounted_loss"})
        self.assertEqual(self.result["scalarization"],"DISABLED_V0")

    def test_invalid_mutated_packet_holds_instead_of_retuning_evaluator(self):
        bad=dict(PACKET);bad["distance_semantics"]=dict(PACKET["distance_semantics"]);bad["distance_semantics"]["scalarization"]="POST_HOC_SCALAR"
        p=self.runtime.evaluate(bad)
        self.assertEqual(p["status"],"HOLD_INVALID_PACKET")
        self.assertIn("scalarization_not_disabled",p["errors"])

    def test_surface_is_discoverable_but_read_only(self):
        self.assertEqual(HOLONOMY_TOOL_NAMES,{"athena_mck_holonomy_evaluate"})
        self.assertIn("athena_mck_holonomy_evaluate",AOR_DEVELOPMENT_TOOL_NAMES)
        self.assertIn(HOLONOMY_RESOURCE,AOR_DEVELOPMENT_RESOURCES)
        s=MythicHolonomySurface();handled,value=s.call_tool("athena_mck_holonomy_evaluate",{"packet":PACKET})
        self.assertTrue(handled);self.assertEqual(value["status"],"HELD_OUT_PACKET_EVALUATED")
        self.assertEqual(value["authority"],"READ_ONLY_REPRESENTATION_BENCHMARK_ONLY");self.assertFalse(value["mck_v2_promotion"])
        resource=s.read_resource(HOLONOMY_RESOURCE["uri"])
        self.assertEqual(resource["scalarization"],"DISABLED_V0");self.assertEqual(resource["practitioner_review"],"HOLD_EXTERNAL_REVIEW")


if __name__=="__main__":unittest.main()
