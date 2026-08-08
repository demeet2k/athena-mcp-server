import unittest
from copy import deepcopy

from athena_mcp.mythic_holonomy_runtime import MythicHolonomyRuntime
from mck_holonomy_fixture import PACKET


class MythicHolonomyLoopSupportAdversarialTests(unittest.TestCase):
    def test_loop_cannot_self_authorize_an_unsupported_transport_edge(self):
        packet=deepcopy(PACKET)
        loop=next(c for c in packet["cases"] if c["case_id"]=="HOL-H01-04")

        # Replace the first two independently frozen Yijing transports with a
        # synthetic S0 -> S2 shortcut. The loop case itself still has a source
        # ref and loss declaration, so a circular evaluator could manufacture
        # a bridge from the loop packet and then score nonzero holonomy.
        loop["path"]=[
            "H01.S0.GRAPHIC_SYMBOLS",
            "H01.S2.TEN_WINGS",
            "H01.S3.ZHU_XI_COMMENTARY",
            "H01.S0.GRAPHIC_SYMBOLS",
        ]

        result=MythicHolonomyRuntime().evaluate(packet)
        index={c["case_id"]:i for i,c in enumerate(packet["cases"])}
        observed=result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][index["HOL-H01-04"]]

        self.assertFalse(observed["loop_supported_by_frozen_transport_cases"])
        self.assertEqual(
            observed["unsupported_loop_edges"],
            [["H01.S0.GRAPHIC_SYMBOLS","H01.S2.TEN_WINGS"]],
        )
        self.assertEqual(observed["status"],"HOLD_LOOP_UNSUPPORTED_BY_FROZEN_TRANSPORT_CASES")
        self.assertFalse(observed["allowed"])
        self.assertIsNone(observed["holonomy_nonzero"])
        self.assertFalse(observed["expected_pass"])
        self.assertEqual(
            observed["law"],
            "HOLONOMY_LOOP_REQUIRES_INDEPENDENT_FROZEN_TRANSPORT_EDGE_SUPPORT",
        )

    def test_original_frozen_loops_are_supported_before_holonomy_is_scored(self):
        result=MythicHolonomyRuntime().evaluate(PACKET)
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        a2=result["arms"]["A2_COMPOSED_HOLONOMY"]["results"]

        for case_id in ("HOL-H01-04","HOL-H02-04"):
            observed=a2[index[case_id]]
            self.assertTrue(observed["loop_supported_by_frozen_transport_cases"])
            self.assertEqual(observed["unsupported_loop_edges"],[])
            self.assertTrue(observed["allowed"])
            self.assertTrue(observed["holonomy_nonzero"])
            self.assertTrue(observed["expected_pass"])
            self.assertEqual(
                observed["law"],
                "H_gamma_IS_REPRESENTATION_DRIFT_VECTOR_NOT_METAPHYSICAL_QUANTITY",
            )


if __name__=="__main__":
    unittest.main()
