import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.store import Store


class H6RootAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        bootstrap(self.core)
        self.crystal = CrystalRuntime(self.core)
        self.h6 = H6RootRuntime(self.core, self.crystal)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def register(self, name):
        return self.core.register("MODEL", "H6_ADV", "TEST", name, "FIXTURE", {}, {})

    def test_h01_multiple_candidates_hold_ambiguity(self):
        a = self.register("A")
        b = self.register("B")
        d = self.h6.identity_decide("UNRESOLVED.H6.ALIAS", candidate_oids=[a["object"]["oid"], b["object"]["oid"]])
        self.assertEqual(d["decision"], "AMBIG_HOLD")
        self.assertIsNone(d["selected_oid"])
        self.assertEqual(len(d["candidate_oids"]), 2)
        self.assertFalse(d["mutation"])

    def test_h02_unknown_object_is_unmapped_without_authority(self):
        d = self.h6.projection_decide("OID.DOES.NOT.EXIST", "KC144")
        self.assertEqual(d["status"], "UNMAPPED")
        self.assertEqual(d["authority"], "NONE")
        self.assertIsNone(d["constitutional_gid"])

    def test_h03_unreachable_route_holds(self):
        a = self.register("ROUTE_A")
        b = self.register("ROUTE_B")
        d = self.h6.route_propose(a["object"]["oid"], b["object"]["oid"], query_id="Q.H6.NO_PATH")
        self.assertEqual(d["hard_gate_status"], "HOLD")
        self.assertEqual(d["route_status"], "HOLD")
        self.assertEqual(d["gain_vector"]["reachability"], 0.0)
        self.assertEqual(d["authority"], "PROPOSAL_ONLY")

    def test_h04_complete_isomorphism_contract_can_be_admitted(self):
        forward = self.crystal.register_transform(
            "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        reverse = self.crystal.register_transform(
            "JSPACE", "KC144", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        d = self.h6.bridge_decide(forward["transform_id"], {
            "preserved_invariants": ["IDENTITY", "VALUE"],
            "lost_invariants": [],
            "validity_corridor": {"type": "ALL_FIXTURE_VALUES"},
            "evidence_refs": ["TEST.H6.BRIDGE.ROUNDTRIP"],
            "required_authority": ["READ_ONLY_TRANSFORM"],
            "reverse_transform_id": reverse["transform_id"],
            "counterexamples": ["OUTSIDE_DECLARED_FIXTURE_DOMAIN"],
        })
        self.assertEqual(d["decision"], "ADMITTED")
        self.assertEqual(d["missing_obligations"], [])
        self.assertEqual(d["defects"], [])

    def test_h04_fake_reverse_transform_does_not_admit(self):
        forward = self.crystal.register_transform(
            "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        d = self.h6.bridge_decide(forward["transform_id"], {
            "preserved_invariants": ["IDENTITY"],
            "lost_invariants": [],
            "validity_corridor": {"type": "ALL_FIXTURE_VALUES"},
            "evidence_refs": ["TEST.H6.BRIDGE"],
            "reverse_transform_id": "TRANSFORM.NOT.REAL",
            "counterexamples": ["OUTSIDE_DOMAIN"],
        })
        self.assertNotEqual(d["decision"], "ADMITTED")
        self.assertIn("REVERSE_TRANSFORM_UNKNOWN", d["defects"])

    def test_h05_independent_evidence_can_be_sufficient_without_promotion(self):
        d = self.h6.evidence_decide(
            {"claim_id": "CLAIM.OK", "evidence_floor": {"minimum_independent": 2}},
            [
                {"evidence_id": "E1", "source_id": "S1", "source_revision": "R1", "independence_group": "G1", "support_direction": "SUPPORT"},
                {"evidence_id": "E2", "source_id": "S2", "source_revision": "R1", "independence_group": "G2", "support_direction": "SUPPORT"},
            ])
        self.assertEqual(d["status"], "EVIDENCE_SUFFICIENT")
        self.assertEqual(d["independent_count"], 2)
        self.assertFalse(d["promotion_authority"])

    def test_h05_stale_evidence_fails_closed(self):
        d = self.h6.evidence_decide(
            {"claim_id": "CLAIM.STALE", "evidence_floor": {"minimum_independent": 1}},
            [{"evidence_id": "E1", "source_id": "S1", "source_revision": "R1", "independence_group": "G1", "freshness": "STALE"}])
        self.assertEqual(d["status"], "EVIDENCE_INSUFFICIENT")
        self.assertIn("stale_evidence", d["defects"])

    def test_h05_counterevidence_prevents_unqualified_sufficiency(self):
        d = self.h6.evidence_decide(
            {"claim_id": "CLAIM.CONFLICT", "evidence_floor": {"minimum_independent": 2}},
            [
                {"evidence_id": "E1", "source_id": "S1", "source_revision": "R1", "independence_group": "G1", "support_direction": "SUPPORT"},
                {"evidence_id": "E2", "source_id": "S2", "source_revision": "R1", "independence_group": "G2", "support_direction": "CONTRADICT"},
            ])
        self.assertEqual(d["status"], "EVIDENCE_INSUFFICIENT")
        self.assertIn("counterevidence_present", d["defects"])
        self.assertEqual(len(d["counterevidence"]), 1)
        self.assertFalse(d["promotion_authority"])

    def test_h06_unresolved_identity_makes_compile_conditional(self):
        r = self.h6.compile_query(
            request="compile unknown target", goal="hold unresolved identity",
            identity_targets=["OID.UNKNOWN.H6"], semantic_vids=[], git_head="HEAD.TEST",
            topology_version="KC144.EPOCH-B-EIGHT-BLOCK", prompt_digest="PROMPT.TEST",
            evidence_floor="E1", authority_envelope={"mode": "READ_ONLY"},
            completion_predicate={"type": "EXPLICIT", "value": "COMPILED"},
            stop_predicate={"type": "NO_POSITIVE_LAWFUL_FRONTIER"}, return_target="H01_PRIME")
        self.assertEqual(r["admission"], "CONDITIONAL")
        self.assertTrue(any(h["type"] == "IDENTITY_HOLD" for h in r["holds"]))
        self.assertFalse(r["active_subcrystal_candidate"]["execution_authority"])

    def test_h06_stale_semantic_vid_is_explicit_hold(self):
        target = self.register("VID_TARGET")
        oid = target["object"]["oid"]
        current_vid = target["version"]["vid"]
        r = self.h6.compile_query(
            request="compile stale semantic target", goal="surface semantic CAS mismatch",
            identity_targets=[oid], semantic_vids=["VID.STALE.H6"], git_head="HEAD.TEST",
            topology_version="KC144.EPOCH-B-EIGHT-BLOCK", prompt_digest="PROMPT.TEST",
            evidence_floor="E1", authority_envelope={"mode": "READ_ONLY"},
            completion_predicate={"type": "EXPLICIT", "value": "COMPILED"},
            stop_predicate={"type": "NO_POSITIVE_LAWFUL_FRONTIER"}, return_target="H01_PRIME")
        self.assertEqual(r["admission"], "CONDITIONAL")
        holds = [h for h in r["holds"] if h["type"] == "SEMANTIC_VID_HOLD"]
        self.assertEqual(len(holds), 1)
        self.assertEqual(holds[0]["oid"], oid)
        self.assertEqual(holds[0]["current_vid"], current_vid)
        self.assertIn("VID.STALE.H6", holds[0]["supplied_semantic_vids"])


if __name__ == "__main__":
    unittest.main()
