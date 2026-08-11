import importlib
import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.store import Store


RUNTIME_PARENT = "429a480a80eeefb9e2bff1ea3015adf571d76b0e"
SEMANTIC_HEAD = "f32eb817d48de73a0c591b0f7fb3561e4f08e7da"


class H6Cut02ExecutableRed(unittest.TestCase):
    """Intentional REDs for the six source-audited H6 contract gaps.

    Each test first proves the current parent substrate exists and exhibits the
    specific pre-H6 behavior.  Only then does it request the missing
    constitutional facade operation.  The future GREEN implementation should
    make these same tests pass without weakening the underlying primitives.
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        bootstrap(self.core)
        self.crystal = CrystalRuntime(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    @staticmethod
    def semantic(name):
        return {
            "kind": "ARTIFACT",
            "domain": "H6_RED",
            "verb": "TEST",
            "object_name": name,
            "method": "PARENT_BOUND_RED",
            "input_contract": {"input": "object"},
            "output_contract": {"output": "object"},
        }

    def _h6(self, gap_id):
        try:
            module = importlib.import_module("athena_mcp.h6_root")
        except ModuleNotFoundError:
            self.fail(
                f"{gap_id}: current parent exposes the prerequisite substrate "
                "but has no constitutional athena_mcp.h6_root.H6RootRuntime facade"
            )
        cls = getattr(module, "H6RootRuntime", None)
        if cls is None:
            self.fail(f"{gap_id}: athena_mcp.h6_root exists but H6RootRuntime is absent")
        return cls(self.core, self.crystal)

    def test_h6g01_identity_decision(self):
        target = self.core.register(
            "MODEL", "H6", "IDENTIFY", "IDENTITY_TARGET", "FIXTURE", {}, {}
        )
        oid = target["object"]["oid"]
        alias = "ALIAS.H6.CUT02.IDENTITY_TARGET"
        self.core.add_edge(alias, "ALIAS_OF", oid, actor="H6.RED")

        # Parent fact: exact OID/CID/name navigation exists, but this declared
        # alias relation is not itself a semantic IdentityDecision surface.
        current = self.core.navigate(alias)
        self.assertFalse(current["found"])

        h6 = self._h6("H6G01_IDENTITY_DECISION")
        decision = h6.identity_decide(alias, candidate_oids=[oid])
        self.assertEqual(decision["decision"], "RESOLVED_EXISTING")
        self.assertEqual(decision["selected_oid"], oid)
        self.assertIn("lineage_compatibility", decision)
        self.assertIn("referent_compatibility", decision)

    def test_h6g02_projection_authority(self):
        result = self.crystal.crystallize_output(
            self.semantic("PROJECTION_TARGET"),
            "projection fixture",
            "memory://h6/red/projection",
            "H6.RED",
            "projection",
            1,
        )
        oid = result["manifest"]["identity"]["OID"]
        kc = result["manifest"]["coordinates"]["KC144"]

        # Parent fact: hash/index-based KC144 projection is RESOLVED, but it
        # carries no constitutional seating-authority classification.
        self.assertEqual(kc["status"], "RESOLVED")
        self.assertNotIn("authority", kc.get("value", {}))

        h6 = self._h6("H6G02_PROJECTION_AUTHORITY")
        decision = h6.projection_decide(
            oid,
            "KC144",
            epoch="EPOCH-B-EIGHT-BLOCK",
        )
        self.assertEqual(decision["authority"], "PROJECTION_ONLY")
        self.assertIn(decision["status"], {"ACTIVE", "DORMANT", "UNMAPPED", "AMBIG", "SUPERSEDED", "CONFLICT"})
        self.assertIn("constitutional_gid", decision)
        self.assertIn("projection_address", decision)

    def test_h6g04_bridge_admission(self):
        registered = self.crystal.register_transform(
            "KC144",
            "JSPACE",
            status="TESTED",
            mode="ISOMORPHISM",
            program={"op": "identity"},
            metric={"type": "EXACT"},
        )

        # Parent fact: a syntactically executable transform can be registered
        # without H04 preserved/lost invariants, validity corridor, evidence,
        # reverse/compensation or counterexample obligations.  That is lawful
        # transform storage; it is not constitutional bridge admission.
        self.assertEqual(registered["mode"], "ISOMORPHISM")
        self.assertEqual(registered["loss_model"], {})
        self.assertNotIn("preserved_invariants", registered)
        self.assertNotIn("validity_corridor", registered)

        h6 = self._h6("H6G04_BRIDGE_ADMISSION")
        decision = h6.bridge_decide(registered["transform_id"])
        self.assertIn(decision["decision"], {"HOLD", "CONDITIONAL"})
        self.assertTrue(decision["missing_obligations"])
        self.assertIn("preserved_invariants", decision["missing_obligations"])
        self.assertIn("validity_corridor", decision["missing_obligations"])

    def test_h6g05_evidence_graph(self):
        evidence_items = [
            {
                "evidence_id": "EV.H6.DUP",
                "source_id": "SRC.H6.ONE",
                "source_revision": "R1",
                "independence_group": "IG.H6.ONE",
                "support_direction": "SUPPORT",
            },
            {
                "evidence_id": "EV.H6.DUP",
                "source_id": "SRC.H6.ONE",
                "source_revision": "R1",
                "independence_group": "IG.H6.ONE",
                "support_direction": "SUPPORT",
            },
        ]
        raw_evidence = {
            "status": "RESOLVED",
            "claim_id": "CLAIM.H6.RED",
            "items": evidence_items,
            "declared_independent_count": 2,
        }
        result = self.crystal.crystallize_output(
            self.semantic("EVIDENCE_TARGET"),
            "evidence fixture",
            "memory://h6/red/evidence",
            "H6.RED",
            "evidence",
            1,
            evidence=raw_evidence,
        )

        # Parent fact: the crystal carrier faithfully preserves caller evidence
        # payload; it is not itself an H05 independence/freshness/evidence-floor
        # adjudicator.
        self.assertEqual(result["manifest"]["evidence"]["status"], "RESOLVED")
        self.assertEqual(len(result["manifest"]["evidence"]["items"]), 2)

        h6 = self._h6("H6G05_EVIDENCE_GRAPH")
        decision = h6.evidence_decide(
            {
                "claim_id": "CLAIM.H6.RED",
                "evidence_floor": {"minimum_independent": 2},
            },
            evidence_items,
        )
        self.assertIn(decision["status"], {"EVIDENCE_INSUFFICIENT", "HOLD"})
        self.assertLess(decision["independent_count"], 2)
        self.assertIn("duplicate_lineage", decision["defects"])
        self.assertFalse(decision.get("promotion_authority", False))

    def test_h6g03_route_navrun_abi(self):
        a = self.core.register("MODEL", "H6", "ROUTE", "ROUTE_A", "FIXTURE", {}, {})
        b = self.core.register("MODEL", "H6", "ROUTE", "ROUTE_B", "FIXTURE", {}, {})
        aoid = a["object"]["oid"]
        boid = b["object"]["oid"]
        self.core.add_edge(aoid, "DEPENDS_ON", boid, actor="H6.RED")
        path = self.crystal.graph_path(aoid, boid)

        # Parent fact: useful graph routing exists, but its native path object is
        # not the constitutional RouteProposal/NAVRUN ABI.
        self.assertTrue(path["found"])
        self.assertEqual(path["length"], 1)
        self.assertNotIn("hard_gate_status", path)
        self.assertNotIn("required_bridges", path)
        self.assertNotIn("cost_vector", path)

        h6 = self._h6("H6G03_ROUTE_NAVRUN_ABI")
        proposal = h6.route_propose(
            aoid,
            boid,
            query_id="Q.H6.CUT02",
            relations=["DEPENDS_ON"],
        )
        for field in (
            "route_id",
            "source_oid",
            "source_vid",
            "target",
            "steps",
            "required_bridges",
            "required_evidence",
            "required_authority",
            "cost_vector",
            "gain_vector",
            "hard_gate_status",
            "pareto_status",
            "route_status",
        ):
            self.assertIn(field, proposal)

    def test_h6g06_querybundle_root_facade(self):
        target = self.core.register(
            "MODEL", "H6", "COMPILE", "QUERY_TARGET", "FIXTURE", {}, {}
        )
        oid = target["object"]["oid"]
        vid = target["version"]["vid"]
        hydrated = self.core.hydrate()

        # Parent fact: useful hydration exists, but it is not a canonical
        # QueryBundle/H6 root receipt binding all six constitutional dimensions.
        self.assertIn("objects", hydrated)
        self.assertNotIn("query_bundle", hydrated)
        self.assertNotIn("completion_predicate", hydrated)
        self.assertNotIn("return_target", hydrated)

        h6 = self._h6("H6G06_QUERYBUNDLE_ROOT_FACADE")
        receipt = h6.compile_query(
            request="Inspect the current H6 query target",
            goal="produce a bounded constitutional compile receipt",
            identity_targets=[oid],
            semantic_vids=[vid],
            git_head=RUNTIME_PARENT,
            topology_version="KC144.EPOCH-B-EIGHT-BLOCK",
            prompt_digest="ATHENA.PROMPT.RUNTIME.V1@" + SEMANTIC_HEAD,
            evidence_floor="E1_STATICALLY_VALIDATED",
            authority_envelope={"mode": "READ_ONLY"},
            completion_predicate={"type": "EXPLICIT", "value": "H6_COMPILE_RECEIPT_EMITTED"},
            stop_predicate={"type": "NO_POSITIVE_LAWFUL_FRONTIER"},
            return_target="H01_PRIME",
        )
        for field in (
            "query_bundle",
            "identity_decisions",
            "projection_decisions",
            "route_proposals",
            "bridge_decisions",
            "evidence_decisions",
            "admission",
            "active_subcrystal_candidate",
            "holds",
        ):
            self.assertIn(field, receipt)
        self.assertEqual(receipt["query_bundle"]["git_head"], RUNTIME_PARENT)
        self.assertEqual(receipt["query_bundle"]["return_target"], "H01_PRIME")


if __name__ == "__main__":
    unittest.main()
