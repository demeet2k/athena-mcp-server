import unittest

from athena_mcp.mythic_computation_protocol import MCK_RESOURCE, MCK_TOOL_NAMES
from athena_mcp.mythic_computation_runtime import MythicComputationRuntime
from athena_mcp.mythic_computation_surface import MythicComputationSurface
from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES, AOR_DEVELOPMENT_RESOURCES


class MythicComputationKernelTests(unittest.TestCase):
    def test_symbolic_address_selects_only_from_supplied_space_and_preserves_source(self):
        r=MythicComputationRuntime()
        p=r.symbolic_address(
            "branch reconciliation topology",
            [
                {"id":"A","terms":["oracle","sample"],"source_ref":"source://a","standing":"SOURCE_REPORTED"},
                {"id":"B","terms":["branch","topology","reconciliation"],"source_ref":"source://b","standing":"SYMBOLIC_INFERENCE"},
            ],
        )
        self.assertEqual(p["status"],"ADDRESS_SELECTED")
        self.assertEqual(p["selected"]["id"],"B")
        self.assertEqual(p["provenance"],["source://b"])
        self.assertEqual(p["authority"],"SYMBOLIC_ADDRESS_SELECTION_ONLY")

    def test_symbolic_address_holds_when_nothing_matches(self):
        p=MythicComputationRuntime().symbolic_address(
            "unrelated query",
            [{"id":"A","terms":["xylophone"],"standing":"UNKNOWN"}],
        )
        self.assertEqual(p["status"],"HOLD_NO_ADDRESS_MATCH")
        self.assertEqual(p["authority"],"NONE")

    def test_correspondence_route_preserves_edge_standing_and_denies_causal_authority(self):
        p=MythicComputationRuntime().correspondence_route(
            "a","c",
            [
                {"src":"a","dst":"b","relation":"symbolic_correspondence","standing":"SOURCE_REPORTED","source_ref":"s1"},
                {"src":"b","dst":"c","relation":"analogy","standing":"SYMBOLIC_INFERENCE","source_ref":"s2"},
            ],
        )
        self.assertEqual(p["status"],"ROUTE_FOUND")
        self.assertEqual(p["standing_trace"],["SOURCE_REPORTED","SYMBOLIC_INFERENCE"])
        self.assertEqual(p["weakest_standing"],"SYMBOLIC_INFERENCE")
        self.assertFalse(p["causal_authority"])

    def test_oracle_decode_keeps_sampler_witness_decoder_and_update_separate(self):
        p=MythicComputationRuntime().oracle_decode(
            "creative reframing",
            [
                {"code":"00","interpretation":"contract","standing":"SYMBOLIC_INFERENCE","source_ref":"source://0"},
                {"code":"01","interpretation":"expand","standing":"TRADITION_INTERNAL","source_ref":"source://1"},
            ],
            sample=3,
            use_case="CREATIVE",
        )
        self.assertEqual(p["status"],"SYMBOLIC_GENERATION_ONLY")
        self.assertEqual(p["R_sampler"]["index"],1)
        self.assertEqual(p["W_witness"]["code"],"01")
        self.assertEqual(p["D_decoder"]["interpretation"],"expand")
        self.assertEqual(p["U_update"]["decision_authority"],"NONE")

    def test_protocol_machine_requires_boundary_then_phase(self):
        r=MythicComputationRuntime()
        self.assertEqual(r.protocol_machine({"authorized":False},{"ready":True},["x"])["status"],"HOLD_BOUNDARY")
        self.assertEqual(r.protocol_machine({"authorized":True},{"ready":False},["x"])["status"],"HOLD_PHASE")
        p=r.protocol_machine({"authorized":True},{"ready":True},["x","y"],witness={"result":"observed"})
        self.assertEqual(p["status"],"SIMULATED_PROTOCOL")
        self.assertTrue(p["B_Theta_Pi_separation"])
        self.assertEqual(p["state_trace"][-1],"CLOSED")
        self.assertEqual(p["execution_authority"],"NONE")

    def test_model_bridge_preserves_unmapped_residue_and_nonidentity(self):
        p=MythicComputationRuntime().model_bridge(
            {"alpha":1,"beta":2,"gamma":3},
            {"existing":9},
            {"alpha":"a","beta":"b"},
            invariants=["keep lineage"],
            source_ref="model://left",
            target_ref="model://right",
        )
        self.assertEqual(p["status"],"BRIDGE_COMPILED")
        self.assertEqual(p["target_output"]["a"],1)
        self.assertEqual(p["unmapped_residue"],{"gamma":3})
        self.assertFalse(p["identity_equivalence"])
        self.assertTrue(p["transform_loss"])

    def test_epistemic_split_allows_only_witnessed_observation_promotion(self):
        r=MythicComputationRuntime()
        bad=r.epistemic_split(
            [{"claim":"reported","status":"SOURCE_REPORTED","source_ref":"source://x"}],
            requested_promotion="OBSERVED",
        )
        self.assertEqual(bad["promotion"]["status"],"REJECTED_UNSUPPORTED_PROMOTION")
        good=r.epistemic_split(
            [{"claim":"measurement","status":"OBSERVED","witness_ref":"test://measurement"}],
            requested_promotion="OBSERVED",
        )
        self.assertEqual(good["promotion"]["status"],"ALLOWED_WITHIN_DECLARED_SCOPE")

    def test_surface_exposes_six_tools_and_resource_through_aor_composition(self):
        s=MythicComputationSurface()
        self.assertEqual(len(MCK_TOOL_NAMES),6)
        for name in MCK_TOOL_NAMES:
            self.assertIn(name,AOR_DEVELOPMENT_TOOL_NAMES)
        self.assertIn(MCK_RESOURCE,AOR_DEVELOPMENT_RESOURCES)
        handled,value=s.call_tool(
            "athena_mck_symbolic_address",
            {"query":"alpha","address_space":[{"id":"a","terms":["alpha"],"standing":"UNKNOWN"}]},
        )
        self.assertTrue(handled)
        self.assertEqual(value["status"],"ADDRESS_SELECTED")
        resource=s.read_resource(MCK_RESOURCE["uri"])
        self.assertEqual(resource["version"],"MCK.RUNTIME.V1")
        self.assertEqual(resource["benchmark"]["protected_illegal_promotions"],0)


if __name__ == "__main__":
    unittest.main()
