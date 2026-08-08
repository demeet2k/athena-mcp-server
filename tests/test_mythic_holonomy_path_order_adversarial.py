import unittest
from copy import deepcopy

from athena_mcp.mythic_holonomy_runtime import MythicHolonomyRuntime
from mck_holonomy_fixture import PACKET


class MythicHolonomyPathOrderAdversarialTests(unittest.TestCase):
    def test_noncommutativity_requires_independently_frozen_edge_support(self):
        packet=deepcopy(PACKET)
        family="H03.IBN_EZRA_TRANSMISSION"
        source="SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"

        # The frozen H03-04 permutation is S0 -> S2 -> S1.  Add those two
        # alternate edges as independently admitted transport cases.  A valid
        # order evaluator must then stop calling the permutation unsupported
        # merely because it differs from the canonical path.
        packet["cases"].extend([
            {
                "case_id":"ADV-H03-S0-S2",
                "family_id":family,
                "path":["H03.S0.ARABIC_SOURCES","H03.S2.LATIN_RECEPTION"],
                "operation":"SEMANTIC_TRANSPORT",
                "expected_class":"ALLOW_WITH_LOSS",
                "source_refs":[source],
                "bridge_invariants":["adversarial alternate edge is independently frozen"],
                "declared_loss":["adversarial alternate edge retains explicit loss"],
            },
            {
                "case_id":"ADV-H03-S2-S1",
                "family_id":family,
                "path":["H03.S2.LATIN_RECEPTION","H03.S1.HEBREW_IBN_EZRA"],
                "operation":"SEMANTIC_TRANSPORT",
                "expected_class":"ALLOW_WITH_LOSS",
                "source_refs":[source],
                "bridge_invariants":["adversarial alternate edge is independently frozen"],
                "declared_loss":["adversarial alternate edge retains explicit loss"],
            },
        ])

        result=MythicHolonomyRuntime().evaluate(packet)
        index={c["case_id"]:i for i,c in enumerate(packet["cases"])}
        order=result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][index["HOL-H03-04"]]

        self.assertTrue(order["canonical_supported_by_frozen_transport_cases"])
        self.assertTrue(order["permuted_supported_by_frozen_transport_cases"])
        self.assertFalse(order["path_order_sensitive"])
        self.assertFalse(order["expected_pass"])

    def test_original_frozen_packet_still_has_independent_order_evidence(self):
        result=MythicHolonomyRuntime().evaluate(PACKET)
        index={c["case_id"]:i for i,c in enumerate(PACKET["cases"])}
        order=result["arms"]["A2_COMPOSED_HOLONOMY"]["results"][index["HOL-H03-04"]]

        self.assertTrue(order["canonical_supported_by_frozen_transport_cases"])
        self.assertFalse(order["permuted_supported_by_frozen_transport_cases"])
        self.assertTrue(order["path_order_sensitive"])
        self.assertTrue(order["expected_pass"])
        self.assertEqual(
            order["law"],
            "PATH_ORDER_CLAIM_REQUIRES_INDEPENDENT_FROZEN_TRANSPORT_EDGE_SUPPORT",
        )


if __name__=="__main__":
    unittest.main()
