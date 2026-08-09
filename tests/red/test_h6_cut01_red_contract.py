"""Intentional H6 CUT-01 RED contract.

This module is isolated under tests/red and is not a normal promotion witness.
It encodes constitutional obligations that the inventory phase must classify before treatment code is written.
"""

import unittest


class H6Cut01RedContract(unittest.TestCase):
    def test_h01_semantic_identity_policy_is_required(self):
        self.fail("RED:H01 requires canonical semantic identity/alias/ambiguity policy beyond deterministic ID constructors")

    def test_h02_constitutional_seating_authority_is_required(self):
        self.fail("RED:H02 requires explicit frozen-seat/projection separation; deterministic hash placement must not be semantic seating authority")

    def test_h03_canonical_route_and_navrun_contract_is_required(self):
        self.fail("RED:H03 requires one canonical RouteProposal/NAVRUN contract over existing navigation implementations")

    def test_h04_bridge_admission_contract_is_required(self):
        self.fail("RED:H04 requires preserved/lost invariants, validity corridor, evidence, reverse/compensation, and admission status around existing transforms")

    def test_h05_source_claim_evidence_graph_is_required(self):
        self.fail("RED:H05 requires canonical Source->Evidence->Claim + independence/freshness/authority-ceiling projection over existing evidence systems")

    def test_h06_querybundle_and_root_facade_are_required(self):
        self.fail("RED:H06 requires constitutional QueryBundle/H6 root facade over existing frontier/rehydration/reconstruction/successor machinery")


if __name__ == "__main__":
    unittest.main()
