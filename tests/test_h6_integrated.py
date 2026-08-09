import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.store import Store


class H6IntegratedTests(unittest.TestCase):
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

    @staticmethod
    def semantic(name):
        return {
            "kind": "ARTIFACT", "domain": "H6_INTEGRATED", "verb": "COMPILE",
            "object_name": name, "method": "INTEGRATED_FIXTURE",
            "input_contract": {"input": "object"}, "output_contract": {"output": "object"},
        }

    def crystallize(self, name):
        return self.crystal.crystallize_output(
            self.semantic(name), f"body {name}", f"memory://h6/integrated/{name.lower()}",
            "H6.INTEGRATED", name.lower(), 1)

    def fixture(self):
        a = self.crystallize("A")
        b = self.crystallize("B")
        aoid, avid = a["manifest"]["identity"]["OID"], a["manifest"]["identity"]["VID"]
        boid, bvid = b["manifest"]["identity"]["OID"], b["manifest"]["identity"]["VID"]
        self.core.add_edge(aoid, "DEPENDS_ON", boid, actor="H6.INTEGRATED")
        forward = self.crystal.register_transform(
            "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        reverse = self.crystal.register_transform(
            "JSPACE", "KC144", status="TESTED", mode="ISOMORPHISM",
            program={"op": "identity"}, metric={"type": "EXACT"})
        claim_id = "CLAIM.H6.INTEGRATED"
        compile_input = {
            "request": "Compile one coupled H6 route",
            "goal": "exercise H01 through H06",
            "identity_targets": [aoid, boid],
            "semantic_vids": [avid, bvid],
            "git_head": "HEAD.H6.INTEGRATED",
            "topology_version": "KC144.EPOCH-B-EIGHT-BLOCK",
            "prompt_digest": "PROMPT.H6.INTEGRATED",
            "evidence_floor": "E2_LOCAL_MECHANISM",
            "authority_envelope": {"mode": "READ_ONLY"},
            "completion_predicate": {"type": "EXPLICIT", "value": "INTEGRATED_COMPILE"},
            "stop_predicate": {"type": "NO_POSITIVE_LAWFUL_FRONTIER"},
            "return_target": "H01_PRIME",
        }
        bridge_contract = {
            "preserved_invariants": ["IDENTITY", "VALUE"],
            "lost_invariants": [],
            "validity_corridor": {"type": "ALL_FIXTURE_VALUES"},
            "evidence_refs": ["EVID.BRIDGE.H6"],
            "required_authority": ["READ_ONLY_TRANSFORM"],
            "reverse_transform_id": reverse["transform_id"],
            "counterexamples": ["OUTSIDE_FIXTURE_DOMAIN"],
        }
        evidence_items = [
            {"evidence_id": "E.H6.1", "source_id": "S.H6.1", "source_revision": "R1", "independence_group": "G.H6.1", "support_direction": "SUPPORT"},
            {"evidence_id": "E.H6.2", "source_id": "S.H6.2", "source_revision": "R1", "independence_group": "G.H6.2", "support_direction": "SUPPORT"},
        ]
        return {
            "aoid": aoid, "boid": boid, "forward": forward, "reverse": reverse,
            "claim_id": claim_id, "compile_input": compile_input,
            "bridge_contract": bridge_contract, "evidence_items": evidence_items,
        }

    def integrated(self, fx, *, bridge_contract=None, evidence_items=None, include_bridge=True,
                   include_evidence=True, route_target=None, required_transform=True, required_claim=True):
        transform_id = fx["forward"]["transform_id"]
        route = {
            "source_oid": fx["aoid"],
            "target": route_target or fx["boid"],
            "relations": ["DEPENDS_ON"],
            "required_transforms": [transform_id] if required_transform else [],
            "required_claims": [fx["claim_id"]] if required_claim else [],
        }
        bridges = [] if not include_bridge else [
            {"transform_id": transform_id, "contract": fx["bridge_contract"] if bridge_contract is None else bridge_contract}
        ]
        evidence = [] if not include_evidence else [
            {"claim": {"claim_id": fx["claim_id"], "evidence_floor": {"minimum_independent": 2}},
             "evidence_items": fx["evidence_items"] if evidence_items is None else evidence_items}
        ]
        return self.h6.compile_integrated(
            compile_input=fx["compile_input"], route_requests=[route],
            bridge_requests=bridges, evidence_requests=evidence)

    def test_positive_coupled_h01_h06_compile_is_admitted(self):
        fx = self.fixture()
        result = self.integrated(fx)
        self.assertEqual(result["admission"], "ADMITTED")
        self.assertEqual(result["holds"], [])
        self.assertEqual(len(result["identity_decisions"]), 2)
        self.assertTrue(all(x["status"] == "ACTIVE" for x in result["projection_decisions"]))
        self.assertEqual(result["route_proposals"][0]["hard_gate_status"], "PASS")
        self.assertEqual(result["bridge_decisions"][0]["decision"], "ADMITTED")
        self.assertEqual(result["evidence_decisions"][0]["status"], "EVIDENCE_SUFFICIENT")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["promotion_authority"])

    def test_navrun_is_deterministic_observation_only_receipt(self):
        fx = self.fixture()
        result = self.integrated(fx)
        route = result["route_proposals"][0]
        kwargs = {
            "actual_cost": {"tool_calls": 0, "hops": 1},
            "observed_gain": {"reachability": 1.0},
            "outcome": "OBSERVED_ROUTE",
            "final_frontier": {"target": fx["boid"]},
        }
        a = self.h6.navrun_observe(route, **kwargs)
        b = self.h6.navrun_observe(route, **kwargs)
        self.assertEqual(a["navrun_id"], b["navrun_id"])
        self.assertEqual(a["status"], "OBSERVED")
        self.assertFalse(a["persisted"])
        self.assertEqual(a["authority"], "OBSERVATION_ONLY")

    def test_incomplete_bridge_blocks_integrated_admission(self):
        fx = self.fixture()
        result = self.integrated(fx, bridge_contract={})
        self.assertEqual(result["admission"], "CONDITIONAL")
        kinds = {h["type"] for h in result["holds"]}
        self.assertIn("BRIDGE_HOLD", kinds)
        self.assertIn("REQUIRED_BRIDGE_HOLD", kinds)

    def test_missing_required_bridge_blocks_route(self):
        fx = self.fixture()
        result = self.integrated(fx, include_bridge=False)
        self.assertEqual(result["admission"], "CONDITIONAL")
        self.assertTrue(any(h["type"] == "REQUIRED_BRIDGE_HOLD" for h in result["holds"]))

    def test_duplicate_evidence_blocks_integrated_admission(self):
        fx = self.fixture()
        dup = [fx["evidence_items"][0], dict(fx["evidence_items"][0])]
        result = self.integrated(fx, evidence_items=dup)
        self.assertEqual(result["admission"], "CONDITIONAL")
        kinds = {h["type"] for h in result["holds"]}
        self.assertIn("EVIDENCE_HOLD", kinds)
        self.assertIn("REQUIRED_EVIDENCE_HOLD", kinds)

    def test_missing_required_evidence_blocks_route(self):
        fx = self.fixture()
        result = self.integrated(fx, include_evidence=False)
        self.assertEqual(result["admission"], "CONDITIONAL")
        self.assertTrue(any(h["type"] == "REQUIRED_EVIDENCE_HOLD" for h in result["holds"]))

    def test_unreachable_route_blocks_even_with_good_bridge_and_evidence(self):
        fx = self.fixture()
        c = self.crystallize("C")
        coid = c["manifest"]["identity"]["OID"]
        result = self.integrated(fx, route_target=coid)
        self.assertEqual(result["admission"], "CONDITIONAL")
        self.assertTrue(any(h["type"] == "ROUTE_HOLD" for h in result["holds"]))


if __name__ == "__main__":
    unittest.main()
