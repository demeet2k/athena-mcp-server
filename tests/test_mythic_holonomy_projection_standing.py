import unittest
from copy import deepcopy

from athena_mcp.mythic_holonomy_runtime import MythicHolonomyRuntime
from athena_mcp.mythic_holonomy_standing import (
    CLOSED_LOOP_STANDING,PROJECTION_OPERATOR,PROXY_STANDING,apply_projection_standing,
)
from athena_mcp.mythic_holonomy_surface import MythicHolonomySurface
from athena_mcp.mythic_holonomy_protocol import HOLONOMY_RESOURCE
from mck_holonomy_fixture import PACKET


class MythicHolonomyProjectionStandingTests(unittest.TestCase):
    def setUp(self):
        self.runtime=MythicHolonomyRuntime()
        self.raw=self.runtime.evaluate(PACKET)
        self.surface=MythicHolonomySurface()
        handled,self.exposed=self.surface.call_tool("athena_mck_holonomy_evaluate",{"packet":PACKET})
        self.assertTrue(handled)
        self.index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}

    def test_raw_loop_executes_open_forward_path_not_return_projection(self):
        case=next(c for c in PACKET["cases"] if c["case_id"]=="HOL-H01-04")
        row=self.raw["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-04"]]
        self.assertEqual(len(case["path"]),5)
        self.assertEqual(len(row["composition"]["receipts"]),3)
        self.assertEqual(row["projection_back_to"],case["path"][0])
        self.assertNotIn("projection_back_executed",row)
        self.assertEqual(row["status"],"HOLONOMY_VECTOR_COMPUTED")

    def test_exposed_loop_downgrades_raw_vector_to_open_path_proxy(self):
        raw=self.raw["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-04"]]
        row=self.exposed["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-04"]]
        self.assertEqual(row["status"],"OPEN_PATH_DRIFT_PROXY_COMPUTED")
        self.assertEqual(row["raw_runtime_status"],"HOLONOMY_VECTOR_COMPUTED")
        self.assertEqual(row["representation_drift_proxy_vector"],raw["holonomy_vector"])
        self.assertEqual(row["holonomy_vector"],raw["holonomy_vector"])
        self.assertEqual(row["holonomy_vector_standing"],PROXY_STANDING)
        self.assertFalse(row["projection_back_executed"])
        self.assertEqual(row["projection_back_operator"],PROJECTION_OPERATOR)
        self.assertEqual(row["closed_loop_holonomy"],"UNKNOWN")
        self.assertEqual(row["closed_loop_holonomy_standing"],CLOSED_LOOP_STANDING)
        self.assertTrue(row["expected_pass"])
        self.assertIn("NOT_TRUE_CLOSED_LOOP_WITNESS",row["expected_class_assay_standing"])

    def test_same_layer_control_remains_zero_control_not_proxy_loop(self):
        row=self.exposed["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H01-05"]]
        self.assertEqual(row["status"],"SAME_LAYER_CONTROL_EVALUATED")
        self.assertNotIn("closed_loop_holonomy",row)
        self.assertFalse(row["holonomy_nonzero"])
        self.assertTrue(all(float(v)==0.0 for v in row["holonomy_vector"].values()))

    def test_summary_separates_proxy_cases_from_true_closed_loop_execution(self):
        summary=self.exposed["arms"]["A2_COMPOSED_HOLONOMY"]["summary"]
        self.assertEqual(summary["open_path_drift_proxy_cases"],2)
        self.assertEqual(summary["true_closed_loop_projection_executed_cases"],0)
        self.assertEqual(summary["closed_loop_holonomy_unknown_cases"],2)
        self.assertEqual(summary["closed_loop_holonomy_standing"],CLOSED_LOOP_STANDING)
        self.assertEqual(summary["frozen_expected_class_assay_uses_proxy_for_loop_cases"],2)
        self.assertEqual(summary["expected_class_passed"],15)

    def test_projection_label_cannot_self_mint_projection_execution(self):
        forged=deepcopy(self.raw)
        row=forged["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H02-04"]]
        row["projection_back_to"]="H02.S0.PREMODERN"
        row["projection_back_executed"]=True
        row["projection_back_operator"]="CALLER_CLAIMED_MAGIC_OPERATOR"
        exposed=apply_projection_standing(PACKET,forged)
        hardened=exposed["arms"]["A2_COMPOSED_HOLONOMY"]["results"][self.index["HOL-H02-04"]]
        self.assertFalse(hardened["projection_back_executed"])
        self.assertEqual(hardened["projection_back_operator"],PROJECTION_OPERATOR)
        self.assertEqual(hardened["closed_loop_holonomy"],"UNKNOWN")

    def test_resource_contract_declares_projection_hold(self):
        resource=self.surface.read_resource(HOLONOMY_RESOURCE["uri"])
        self.assertEqual(resource["loop_vector_standing"],PROXY_STANDING)
        self.assertFalse(resource["projection_back_executed"])
        self.assertEqual(resource["projection_back_operator"],PROJECTION_OPERATOR)
        self.assertEqual(resource["closed_loop_holonomy"],CLOSED_LOOP_STANDING)
        self.assertIn("OPEN_PATH_ENDPOINT_DRIFT != CLOSED_LOOP_HOLONOMY",resource["laws"])


if __name__=="__main__":
    unittest.main()
