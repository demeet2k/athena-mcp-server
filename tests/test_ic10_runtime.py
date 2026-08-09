import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.ic10_runtime import IC10Compiler
from athena_mcp.promotion import PromotionLedger
from athena_mcp.store import Store


HEAD = "HEAD.IC10.GREEN"


class IC10RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        bootstrap(self.core)
        self.crystal = CrystalRuntime(self.core)
        self.h6 = H6RootRuntime(self.core, self.crystal)
        self.promotion = PromotionLedger(self.core)
        self.ic10 = IC10Compiler()

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def qualified_promotion(self, *, trusted=True, head=HEAD):
        ci = {"observed": True, "ref": "CI.IC10.GREEN", "head_sha": head, "conclusion": "success"}
        smoke = {"observed": True, "ref": "SMOKE.IC10.GREEN", "head_sha": head, "conclusion": "success"}
        verification = None
        if trusted:
            verification = {
                "observed": True,
                "verifier": "TEST.TRUSTED.HOST",
                "verification_ref": "VERIFY.IC10.GREEN",
                "head_sha": head,
                "ci_ref": ci["ref"],
                "smoke_ref": smoke["ref"],
            }
        return self.promotion.evaluate(
            "Server", head,
            {"surface_status": "PASS", "composition": {"status": "PASS"}},
            ci, smoke,
            local_git_status={"enabled": False},
            trusted_external_verification=verification,
            persist=False,
        )

    def candidate(self, *, promotion=None):
        target = self.crystal.crystallize_output(
            {
                "kind": "MODEL", "domain": "IC10", "verb": "QUALIFY",
                "object_name": "IC10_TARGET", "method": "FIXTURE",
                "input_contract": {}, "output_contract": {},
            },
            "IC10 gate-chain target", "memory://ic10/target",
            "IC10.TEST", "ic10", 1,
        )
        oid = target["manifest"]["identity"]["OID"]
        identity = self.h6.identity_decide(oid, candidate_oids=[oid])
        forward = self.crystal.register_transform(
            "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        reverse = self.crystal.register_transform(
            "JSPACE", "KC144", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        bridge = self.h6.bridge_decide(forward["transform_id"], {
            "preserved_invariants": ["IDENTITY", "TYPE"],
            "lost_invariants": [],
            "validity_corridor": {"type": "FIXTURE_DOMAIN"},
            "evidence_refs": ["BRIDGE.IC10.E1"],
            "reverse_transform_id": reverse["transform_id"],
            "counterexamples": ["OUTSIDE_FIXTURE_DOMAIN"],
        })
        evidence = self.h6.evidence_decide(
            {"claim_id": "CLAIM.IC10", "evidence_floor": {"minimum_independent": 2}},
            [
                {"evidence_id": "E1", "source_id": "S1", "source_revision": "R1", "independence_group": "G1", "support_direction": "SUPPORT"},
                {"evidence_id": "E2", "source_id": "S2", "source_revision": "R1", "independence_group": "G2", "support_direction": "SUPPORT"},
            ])
        return {
            "candidate_ref": "IC10.CANDIDATE.TEST",
            "git_head": HEAD,
            "identity_decision": identity,
            "provenance_refs": ["SOURCE.IC10.TARGET"],
            "syntax_witness": {"observed": True, "status": "PASS", "ref": "SYNTAX.IC10", "normalized": True, "dependencies_explicit": True, "trust_class": "RUNTIME_OBSERVED"},
            "type_carrier_witness": {"observed": True, "status": "PASS", "ref": "TYPE.IC10", "type": "MODEL", "carrier": "text/plain", "units_status": "NOT_APPLICABLE", "trust_class": "RUNTIME_OBSERVED"},
            "scope_witness": {"observed": True, "status": "PASS", "ref": "SCOPE.IC10", "scope": "FIXTURE", "validity_corridor": "FIXTURE_DOMAIN", "evidence_alignment": "PASS", "trust_class": "RUNTIME_OBSERVED"},
            "invariant_witness": {"observed": True, "status": "PASS", "ref": "INV.IC10", "declared_invariants": ["IDENTITY", "TYPE"], "violations": [], "trust_class": "RUNTIME_OBSERVED"},
            "evidence_decision": evidence,
            "dependency_replay_witness": {"observed": True, "status": "PASS", "ref": "DEP.IC10", "dependencies_closed": True, "replay_prerequisites": True, "exact_versions": True, "trust_class": "RUNTIME_OBSERVED"},
            "bridge_decision": bridge,
            "audit_replay_witness": {"observed": True, "status": "PASS", "ref": "REPLAY.IC10", "audit_complete": True, "replay_complete": True, "replay_digest": "REPLAY.DIGEST.IC10", "trust_class": "RUNTIME_OBSERVED"},
            "promotion_certificate": promotion or self.qualified_promotion(),
        }

    def test_full_chain_satisfied_without_minting_promotion(self):
        c = self.candidate()
        before = self.store.one("SELECT COUNT(*) n FROM events")["n"]
        result = self.ic10.evaluate(c)
        after = self.store.one("SELECT COUNT(*) n FROM events")["n"]
        self.assertEqual(result["decision"], "IC10_CHAIN_SATISFIED")
        self.assertTrue(all(g["status"] == "PASS" for g in result["gates"]))
        self.assertIsNone(result["first_hold"])
        self.assertFalse(result["promotion_authority"])
        self.assertEqual(result["canonical_emission_authority"], "EXISTING_PROMOTION_LEDGER_ONLY")
        self.assertEqual(before, after)

    def test_i03_hold_blocks_i10_even_with_qualified_promotion(self):
        c = self.candidate()
        c["type_carrier_witness"]["units_status"] = "UNKNOWN"
        result = self.ic10.evaluate(c)
        self.assertEqual(result["decision"], "IC10_HOLD")
        self.assertEqual(result["first_hold"], "I03_TYPE_UNIT_CARRIER")
        self.assertIn("units_not_validated", result["gate_map"]["I03_TYPE_UNIT_CARRIER"]["defects"])
        self.assertIn("predecessor_gate_hold", result["gate_map"]["I10_EXISTING_PROMOTION_QUALIFICATION"]["defects"])
        self.assertEqual(result["promotion_status_observed"], "QUALIFIED")

    def test_i06_counterevidence_blocks_chain(self):
        c = self.candidate()
        c["evidence_decision"] = {
            "status": "EVIDENCE_INSUFFICIENT",
            "promotion_authority": False,
            "defects": ["counterevidence_present"],
        }
        result = self.ic10.evaluate(c)
        self.assertEqual(result["first_hold"], "I06_EVIDENCE_SUFFICIENCY_INDEPENDENCE")
        self.assertEqual(result["decision"], "IC10_HOLD")

    def test_i08_bridge_hold_blocks_chain(self):
        c = self.candidate()
        c["bridge_decision"] = {
            "decision": "HOLD",
            "missing_obligations": ["validity_corridor"],
            "defects": [],
        }
        result = self.ic10.evaluate(c)
        self.assertEqual(result["first_hold"], "I08_BRIDGE_GLUING_RETURN_DEFECT")
        self.assertEqual(result["decision"], "IC10_HOLD")

    def test_i10_requires_trusted_qualified_promotion(self):
        c = self.candidate(promotion=self.qualified_promotion(trusted=False))
        result = self.ic10.evaluate(c)
        self.assertEqual(c["promotion_certificate"]["status"], "ATTESTED_READY")
        self.assertEqual(result["first_hold"], "I10_EXISTING_PROMOTION_QUALIFICATION")
        self.assertIn("promotion_not_qualified", result["gate_map"]["I10_EXISTING_PROMOTION_QUALIFICATION"]["defects"])

    def test_i10_requires_exact_same_git_head(self):
        c = self.candidate(promotion=self.qualified_promotion(head="HEAD.OTHER"))
        result = self.ic10.evaluate(c)
        self.assertEqual(result["decision"], "IC10_HOLD")
        self.assertIn("promotion_git_head_mismatch", result["gate_map"]["I10_EXISTING_PROMOTION_QUALIFICATION"]["defects"])

    def test_decision_digest_is_deterministic(self):
        c = self.candidate()
        a = self.ic10.evaluate(c)
        b = self.ic10.evaluate(c)
        self.assertEqual(a["decision_digest"], b["decision_digest"])


if __name__ == "__main__":
    unittest.main()
