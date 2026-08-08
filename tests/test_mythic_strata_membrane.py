import unittest

from athena_mcp.mythic_strata_protocol import STRATA_RESOURCE,STRATA_TOOL_NAMES
from athena_mcp.mythic_strata_runtime import MythicStrataRuntime
from athena_mcp.mythic_strata_surface import MythicStrataSurface
from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES,AOR_DEVELOPMENT_RESOURCES


def L(layer,standing="SECONDARY_SCHOLARSHIP",category="COMPOSITE",corpus="LAYERED",auth="PUBLIC"):
    return {
        "layer_id":layer,"standing":standing,"category_scope":category,
        "corpus_mutability":corpus,"authorization_scope":auth,
    }


class MythicStrataMembraneTests(unittest.TestCase):
    def test_regression12_execute_and_reject_all_illegal_transports(self):
        b=MythicStrataRuntime().benchmark()
        self.assertEqual(b["regression_cases"],12)
        self.assertEqual(b["regression_passed"],12)
        self.assertEqual(b["illegal_transports_admitted"],0)
        self.assertTrue(all(x["pass"] for x in b["outcomes"]))

    def test_v1_unscoped_reference_vs_strata_comparison_is_explicitly_synthetic(self):
        b=MythicStrataRuntime().benchmark()
        self.assertEqual(b["unscoped_reference_admits"],12)
        self.assertEqual(b["illegal_transports_admitted"],0)
        self.assertEqual(b["controls"],3)
        self.assertEqual(b["controls_allowed"],3)
        self.assertEqual(b["false_holds"],0)
        self.assertTrue(b["bridge_loss_retained"])
        self.assertIn("UNSCOPED_REFERENCE_MODEL != OBSERVED_V1_FAILURE_RATE",b["laws"])
        self.assertIn("SYNTHETIC_REGRESSION_PASS != GENERAL_EFFECTIVENESS",b["laws"])

    def test_same_layer_transport_is_allowed_without_identity_claim(self):
        a=L("same.layer")
        p=MythicStrataRuntime().transport(a,a,"SEMANTIC_TRANSPORT")
        self.assertEqual(p["status"],"WITHIN_LAYER_ALLOWED")
        self.assertTrue(p["allowed"])
        self.assertFalse(p["identity_equivalence"])
        self.assertEqual(p["execution_authority"],"NONE")

    def test_cross_layer_transport_requires_complete_source_bearing_bridge(self):
        r=MythicStrataRuntime()
        src=L("old")
        dst=L("new")
        blocked=r.transport(src,dst,"SEMANTIC_TRANSPORT")
        self.assertEqual(blocked["status"],"HOLD_EXPLICIT_BRIDGE_REQUIRED")
        incomplete=r.transport(src,dst,"SEMANTIC_TRANSPORT",explicit_bridge={
            "source_ref":"source://x","evidence_standing":"SECONDARY_SCHOLARSHIP",
            "invariants":[],"transform_loss":["loss"],"authority":"SCHOLARLY_MAPPING",
        })
        self.assertEqual(incomplete["status"],"HOLD_INCOMPLETE_BRIDGE")
        bridge={
            "source_ref":"source://x","evidence_standing":"SECONDARY_SCHOLARSHIP",
            "invariants":["preserve layer identity"],
            "transform_loss":["decoder semantics differ"],
            "authority":"SCHOLARLY_MAPPING",
        }
        allowed=r.transport(src,dst,"SEMANTIC_TRANSPORT",explicit_bridge=bridge)
        self.assertEqual(allowed["status"],"BRIDGE_ALLOWED_WITH_LOSS")
        self.assertTrue(allowed["allowed"])
        self.assertFalse(allowed["identity_equivalence"])
        self.assertEqual(allowed["transform_loss"],["decoder semantics differ"])
        self.assertEqual(allowed["execution_authority"],"NONE")

    def test_bridge_cannot_escalate_target_standing_above_evidence(self):
        r=MythicStrataRuntime()
        bridge={
            "source_ref":"source://secondary","evidence_standing":"SECONDARY_SCHOLARSHIP",
            "invariants":["preserve provenance"],"transform_loss":["layer mismatch"],
            "authority":"SCHOLARLY_MAPPING",
        }
        p=r.transport(
            L("secondary","SECONDARY_SCHOLARSHIP"),
            L("primary","PRIMARY_EVIDENCE"),
            "SEMANTIC_TRANSPORT",explicit_bridge=bridge,
        )
        self.assertEqual(p["status"],"HOLD_STANDING_ESCALATION")
        self.assertFalse(p["allowed"])

    def test_runtime_never_mints_initiatory_authority_even_with_bridge(self):
        bridge={
            "source_ref":"source://description","evidence_standing":"SECONDARY_SCHOLARSHIP",
            "invariants":["authorization exists"],"transform_loss":["no authorization granted"],
            "authority":"SCHOLARLY_MAPPING",
        }
        p=MythicStrataRuntime().transport(
            L("public",auth="PUBLIC"),
            L("initiatory",standing="TRADITION_INTERNAL",auth="INITIATORY"),
            "AUTHORITY_GRANT",explicit_bridge=bridge,
        )
        self.assertEqual(p["status"],"HOLD_AUTHORITY_MINT")
        self.assertEqual(p["execution_authority"],"NONE")

    def test_surface_is_composed_through_aor_without_changing_six_mck_tools(self):
        self.assertEqual(STRATA_TOOL_NAMES,{"athena_mck_strata_transport"})
        self.assertIn("athena_mck_strata_transport",AOR_DEVELOPMENT_TOOL_NAMES)
        self.assertIn(STRATA_RESOURCE,AOR_DEVELOPMENT_RESOURCES)
        s=MythicStrataSurface()
        handled,value=s.call_tool("athena_mck_strata_transport",{
            "source":L("x"),"target":L("x"),"operation":"SEMANTIC_TRANSPORT"
        })
        self.assertTrue(handled)
        self.assertEqual(value["status"],"WITHIN_LAYER_ALLOWED")
        resource=s.read_resource(STRATA_RESOURCE["uri"])
        self.assertEqual(resource["benchmark"]["regression_passed"],12)
        self.assertFalse(resource["mck_v2_promotion"])
        self.assertEqual(resource["practitioner_review"],"HOLD_EXTERNAL_REVIEW")


if __name__=="__main__":
    unittest.main()
