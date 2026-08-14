import copy
import sqlite3
import tempfile
import threading
import unittest

from athena_mcp.nexus4d import Nexus4dRuntime


class StubStore:
    def __init__(self, path):
        self._lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row

    def one(self, sql, args=()):
        row = self.db.execute(sql, args).fetchone()
        return dict(row) if row else None

    def rows(self, sql, args=()):
        return [dict(row) for row in self.db.execute(sql, args).fetchall()]

    def close(self):
        self.db.close()


class FakeAuthority:
    def __init__(self):
        self.states = {}

    def state(self, claim_id):
        value = self.states.get(claim_id)
        return copy.deepcopy(value) if value else None


def base_spec(authorities=None):
    return {
        "name": "repair service",
        "initial_state": {
            "source": {"revision": 1},
            "analysis": {"diagnosed": False},
            "system": {"healthy": False},
        },
        "authorities": ["WRITE"] if authorities is None else authorities,
        "hard_invariants": [
            {"id": "SOURCE_REVISION_PRESENT", "predicate": {"kind": "exists", "path": "source.revision", "value": True}}
        ],
        "goals": [
            {
                "id": "HEALTHY",
                "predicate": {"kind": "state_equals", "path": "system.healthy", "value": True},
                "evidence_threshold": {"local": 1.0, "replay": 1.0},
                "consumer": "runtime",
                "require_outcome": True,
            }
        ],
        "nodes": [
            {
                "id": "inspect",
                "goals": [],
                "requires": [],
                "readset": ["source.revision"],
                "writeset": ["analysis.diagnosed"],
                "evidence_threshold": {"local": 1.0},
                "cost": 1,
            },
            {
                "id": "repair",
                "goals": ["HEALTHY"],
                "requires": ["inspect"],
                "dependency_stage": "COMMITTED",
                "readset": ["source.revision", "analysis.diagnosed"],
                "writeset": ["system.healthy"],
                "required_authorities": ["WRITE"],
                "evidence_threshold": {"local": 1.0, "replay": 1.0},
                "consumer": "runtime",
                "require_outcome": True,
                "cost": 2,
            },
        ],
    }


class Nexus4dTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = StubStore(self.tmp.name)
        self.runtime = Nexus4dRuntime(self.store)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def compile(self, spec=None, machine_id="M1"):
        return self.runtime.compile(spec or base_spec(), machine_id=machine_id)

    def apply_node(self, machine_id, node_id, state_delta, evidence, consumer=None, outcome=False):
        plan = self.runtime.plan(machine_id)
        item = next(row for row in plan["batch"] if row["node_id"] == node_id)
        packet = item["nexus_packet"]
        revision = plan["revision"]
        candidate_id = f"C-{node_id}-{revision}"
        events = [
            {
                "type": "CLAIMED",
                "idempotency_key": f"claim-{node_id}-{revision}",
                "payload": {
                    "node_id": node_id,
                    "claim_id": f"CL-{node_id}-{revision}",
                    "readset_digest": packet["readset_digest"],
                    "writeset": packet["writeset"],
                    "lease_until_revision": revision + 20,
                },
            },
            {
                "type": "CANDIDATE_PRODUCED",
                "payload": {
                    "node_id": node_id,
                    "claim_id": f"CL-{node_id}-{revision}",
                    "candidate_id": candidate_id,
                    "readset_digest": packet["readset_digest"],
                    "state_delta": state_delta,
                    "claims": [f"{node_id} produced its bounded delta"],
                },
            },
            {
                "type": "EVIDENCE_RECORDED",
                "payload": {
                    "node_id": node_id,
                    "candidate_id": candidate_id,
                    "profile": evidence,
                    "refs": [f"TEST:{node_id}:{revision}"],
                },
            },
            {
                "type": "VERIFIED",
                "payload": {
                    "node_id": node_id,
                    "candidate_id": candidate_id,
                    "passed": True,
                    "verifier_ref": f"VERIFIER:{node_id}:{revision}",
                },
            },
            {
                "type": "COMMITTED",
                "payload": {
                    "node_id": node_id,
                    "candidate_id": candidate_id,
                    "authority_ref": "AUTH:WRITE",
                },
            },
        ]
        result = self.runtime.advance(machine_id, revision, events)
        if consumer:
            result = self.runtime.advance(
                machine_id,
                result["revision"],
                [{"type": "CONSUMED", "payload": {"node_id": node_id, "consumer": consumer, "receipt_ref": f"CONSUME:{node_id}"}}],
            )
        if outcome:
            result = self.runtime.advance(
                machine_id,
                result["revision"],
                [{"type": "OUTCOME_OBSERVED", "payload": {"node_id": node_id, "observation_ref": f"OBS:{node_id}", "state_delta": {"observations.repair_confirmed": True}}}],
            )
        return result

    def test_reverse_demand_meets_forward_readiness(self):
        compiled = self.compile()
        self.assertEqual(compiled["plan"]["status"], "PLANNED")
        self.assertEqual([row["node_id"] for row in compiled["plan"]["batch"]], ["inspect"])
        pressure = compiled["plan"]["derived"]["pressure"]
        self.assertGreater(pressure["repair"]["goal"], 0)
        self.assertGreater(pressure["inspect"]["goal"], 0)
        self.assertIn("DEPENDENCIES_NOT_READY", compiled["plan"]["derived"]["readiness"]["repair"]["reasons"])

    def test_full_lifecycle_closes_only_after_consumption_and_outcome(self):
        self.compile()
        first = self.apply_node("M1", "inspect", {"analysis.diagnosed": True}, {"local": 1.0})
        self.assertEqual(first["plan"]["batch"][0]["node_id"], "repair")
        repair = self.apply_node("M1", "repair", {"system.healthy": True}, {"local": 1.0, "replay": 1.0})
        self.assertFalse(repair["terminal"]["terminal"])
        self.assertIn("CONSUMPTION", repair["terminal"]["goals"]["HEALTHY"]["deficits"])
        consumed = self.runtime.advance(
            "M1",
            repair["revision"],
            [{"type": "CONSUMED", "payload": {"node_id": "repair", "consumer": "runtime", "receipt_ref": "CONSUME:repair"}}],
        )
        self.assertFalse(consumed["terminal"]["terminal"])
        self.assertIn("OUTCOME", consumed["terminal"]["goals"]["HEALTHY"]["deficits"])
        observed = self.runtime.advance(
            "M1",
            consumed["revision"],
            [{"type": "OUTCOME_OBSERVED", "payload": {"node_id": "repair", "observation_ref": "OBS:repair", "state_delta": {"observations.repair_confirmed": True}}}],
        )
        self.assertTrue(observed["terminal"]["terminal"])
        self.assertEqual(observed["status"], "TERMINAL")

    def test_commit_before_verification_is_rejected(self):
        self.compile()
        plan = self.runtime.plan("M1")
        packet = plan["batch"][0]["nexus_packet"]
        claim = {"type": "CLAIMED", "payload": {"node_id": "inspect", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"]}}
        candidate = {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "inspect", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"analysis.diagnosed": True}}}
        commit = {"type": "COMMITTED", "payload": {"node_id": "inspect", "candidate_id": "C", "authority_ref": "AUTH"}}
        with self.assertRaisesRegex(ValueError, "VERIFIED"):
            self.runtime.advance("M1", 0, [claim, candidate, commit])
        self.assertEqual(self.runtime.state("M1")["revision"], 0)

    def test_evidence_lattice_is_componentwise(self):
        self.compile()
        self.apply_node("M1", "inspect", {"analysis.diagnosed": True}, {"local": 1.0})
        plan = self.runtime.plan("M1")
        packet = plan["batch"][0]["nexus_packet"]
        events = [
            {"type": "CLAIMED", "payload": {"node_id": "repair", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"]}},
            {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "repair", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"system.healthy": True}}},
            {"type": "EVIDENCE_RECORDED", "payload": {"node_id": "repair", "candidate_id": "C", "profile": {"local": 1.0}, "refs": ["LOCAL"]}},
            {"type": "VERIFIED", "payload": {"node_id": "repair", "candidate_id": "C", "passed": True, "verifier_ref": "V"}},
        ]
        with self.assertRaisesRegex(ValueError, "evidence profile"):
            self.runtime.advance("M1", plan["revision"], events)

    def test_pressure_never_grants_authority(self):
        self.compile(base_spec(authorities=[]))
        self.apply_node("M1", "inspect", {"analysis.diagnosed": True}, {"local": 1.0})
        plan = self.runtime.plan("M1")
        self.assertEqual(plan["batch"], [])
        readiness = plan["derived"]["readiness"]["repair"]
        self.assertIn("AUTHORITY_SCOPE", readiness["reasons"])
        self.assertGreater(plan["derived"]["pressure"]["repair"]["goal"], 0)

    def test_relevant_state_drift_invalidates_candidate(self):
        self.compile()
        self.apply_node("M1", "inspect", {"analysis.diagnosed": True}, {"local": 1.0})
        plan = self.runtime.plan("M1")
        packet = plan["batch"][0]["nexus_packet"]
        claimed = self.runtime.advance(
            "M1",
            plan["revision"],
            [
                {"type": "CLAIMED", "payload": {"node_id": "repair", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"], "lease_until_revision": plan["revision"] + 10}},
                {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "repair", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"system.healthy": True}}},
            ],
        )
        drifted = self.runtime.advance(
            "M1",
            claimed["revision"],
            [{"type": "STATE_OBSERVED", "payload": {"source_ref": "EXTERNAL:REVISION", "state_delta": {"source.revision": 2}}}],
        )
        self.assertEqual(self.runtime.state("M1")["snapshot"]["node_state"]["repair"]["stage"], "INVALIDATED")
        with self.assertRaisesRegex(ValueError, "VERIFIED"):
            self.runtime.advance("M1", drifted["revision"], [{"type": "COMMITTED", "payload": {"node_id": "repair", "candidate_id": "C", "authority_ref": "AUTH"}}])

    def test_conflicting_writesets_are_not_batched(self):
        spec = {
            "initial_state": {"x": 0, "y": 0},
            "goals": [
                {"id": "G1", "predicate": {"kind": "state_equals", "path": "x", "value": 1}},
                {"id": "G2", "predicate": {"kind": "state_equals", "path": "y", "value": 1}},
            ],
            "nodes": [
                {"id": "A", "goals": ["G1"], "writeset": ["shared"]},
                {"id": "B", "goals": ["G2"], "writeset": ["shared.child"]},
            ],
            "scheduler": {"max_batch": 2},
        }
        compiled = self.compile(spec, "M2")
        self.assertEqual(len(compiled["plan"]["batch"]), 1)

    def test_idempotent_event_replay_does_not_advance_revision(self):
        self.compile()
        event = {"type": "STATE_OBSERVED", "idempotency_key": "OBS-1", "payload": {"source_ref": "S", "state_delta": {"telemetry.tick": 1}}}
        first = self.runtime.advance("M1", 0, [event])
        second = self.runtime.advance("M1", first["revision"], [event])
        self.assertEqual(second["status"], "IDEMPOTENT_REPLAY")
        self.assertEqual(second["revision"], first["revision"])

    def test_replay_reconstructs_exact_snapshot(self):
        self.compile()
        self.apply_node("M1", "inspect", {"analysis.diagnosed": True}, {"local": 1.0})
        replay = self.runtime.replay("M1")
        self.assertEqual(replay["status"], "REPLAY_MATCH", replay)
        self.assertTrue(replay["match"])

    def test_cycle_without_bounded_gain_policy_is_rejected(self):
        spec = {
            "initial_state": {"done": False},
            "goals": [{"id": "G", "predicate": {"kind": "state_equals", "path": "done", "value": True}}],
            "nodes": [
                {"id": "A", "goals": ["G"], "requires": ["B"]},
                {"id": "B", "requires": ["A"]},
            ],
        }
        with self.assertRaisesRegex(ValueError, "cycle_policy"):
            self.compile(spec, "CYCLE")

    def test_topology_promotion_requires_observed_gain_and_rollback(self):
        self.compile()
        replacement = base_spec()
        replacement["nodes"].append({"id": "audit", "goals": [], "requires": [], "readset": ["source.revision"], "writeset": []})
        candidate = {
            "type": "TOPOLOGY_CANDIDATE",
            "payload": {"change_id": "T1", "patch": {"add": "audit"}, "replacement_spec": replacement, "rollback": {"remove": "audit"}, "falsifier": "BENCH:T1"},
        }
        tested = {"type": "TOPOLOGY_TESTED", "payload": {"change_id": "T1", "observed_gain": 0.0, "invariant_regressions": []}}
        first = self.runtime.advance("M1", 0, [candidate, tested])
        with self.assertRaisesRegex(ValueError, "positive observed gain"):
            self.runtime.advance("M1", first["revision"], [{"type": "TOPOLOGY_PROMOTED", "payload": {"change_id": "T1", "authority_ref": "AUTH"}}])

    def test_y1_authority_claims_gate_plan_and_commit_and_replay(self):
        authority = FakeAuthority()
        authority.states["AUTH.REPAIR"] = {"claim_id": "AUTH.REPAIR", "y": "+", "status": "ACTIVE", "last_eid": "E1", "canonical_ref": None, "source_ref": "POLICY"}
        runtime = Nexus4dRuntime(self.store, authority)
        spec = {
            "initial_state": {"x": 0},
            "goals": [{"id": "G", "predicate": {"kind": "state_equals", "path": "x", "value": 1}}],
            "nodes": [{"id": "N", "goals": ["G"], "readset": ["x"], "writeset": ["x"], "required_authority_claims": [{"claim_id": "AUTH.REPAIR", "min_y": "!"}]}],
        }
        compiled = runtime.compile(spec, machine_id="AUTHM")
        self.assertEqual(compiled["plan"]["batch"], [])
        self.assertIn("CANONICAL_AUTHORITY", compiled["plan"]["derived"]["readiness"]["N"]["reasons"])
        authority.states["AUTH.REPAIR"].update({"y": "!", "last_eid": "E2"})
        plan = runtime.plan("AUTHM")
        packet = plan["batch"][0]["nexus_packet"]
        staged = runtime.advance(
            "AUTHM",
            0,
            [
                {"type": "CLAIMED", "payload": {"node_id": "N", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"], "lease_until_revision": 20}},
                {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "N", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"x": 1}}},
                {"type": "VERIFIED", "payload": {"node_id": "N", "candidate_id": "C", "passed": True, "verifier_ref": "V"}},
            ],
        )
        authority.states["AUTH.REPAIR"].update({"y": "?", "status": "CHALLENGED", "last_eid": "E3"})
        with self.assertRaisesRegex(ValueError, "canonical authority"):
            runtime.advance("AUTHM", staged["revision"], [{"type": "COMMITTED", "payload": {"node_id": "N", "candidate_id": "C", "authority_ref": "AUTH.REPAIR"}}])
        authority.states["AUTH.REPAIR"].update({"y": "#", "status": "ACTIVE", "last_eid": "E4", "canonical_ref": "CANON:REPAIR"})
        committed = runtime.advance("AUTHM", staged["revision"], [{"type": "COMMITTED", "payload": {"node_id": "N", "candidate_id": "C", "authority_ref": "CANON:REPAIR"}}])
        self.assertEqual(committed["revision"], staged["revision"] + 1)
        self.assertEqual(runtime.replay("AUTHM")["status"], "REPLAY_MATCH")

    def test_candidate_cannot_write_outside_declared_writeset(self):
        self.compile()
        plan = self.runtime.plan("M1")
        packet = plan["batch"][0]["nexus_packet"]
        events = [
            {"type": "CLAIMED", "payload": {"node_id": "inspect", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"], "lease_until_revision": 10}},
            {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "inspect", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"system.healthy": True}}},
        ]
        with self.assertRaisesRegex(ValueError, "declared writeset"):
            self.runtime.advance("M1", 0, events)
        self.assertEqual(self.runtime.state("M1")["revision"], 0)

    def test_initial_hard_invariant_must_hold(self):
        spec = base_spec()
        spec["initial_state"]["source"].pop("revision")
        with self.assertRaisesRegex(ValueError, "initial_state violates"):
            self.compile(spec, "BADINV")

    def test_expired_claim_can_be_lawfully_reclaimed(self):
        self.compile()
        plan = self.runtime.plan("M1")
        packet = plan["batch"][0]["nexus_packet"]
        first = self.runtime.advance(
            "M1",
            0,
            [{"type": "CLAIMED", "payload": {"node_id": "inspect", "claim_id": "OLD", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"], "lease_until_revision": 0}}],
        )
        reclaim_plan = self.runtime.plan("M1", expected_revision=first["revision"])
        self.assertEqual(reclaim_plan["batch"][0]["node_id"], "inspect")
        reclaimed = self.runtime.advance(
            "M1",
            first["revision"],
            [{"type": "CLAIMED", "payload": {"node_id": "inspect", "claim_id": "NEW", "readset_digest": reclaim_plan["batch"][0]["nexus_packet"]["readset_digest"], "writeset": reclaim_plan["batch"][0]["nexus_packet"]["writeset"], "lease_until_revision": 20}}],
        )
        self.assertEqual(self.runtime.state("M1")["snapshot"]["node_state"]["inspect"]["claim"]["claim_id"], "NEW")
        self.assertEqual(reclaimed["revision"], 2)

    def test_topology_rewrite_and_rollback_are_replayable(self):
        self.compile()
        replacement = base_spec()
        replacement["nodes"].append({"id": "audit", "goals": [], "requires": [], "readset": ["source.revision"], "writeset": [], "capacity": 2})
        promoted = self.runtime.advance(
            "M1",
            0,
            [
                {"type": "TOPOLOGY_CANDIDATE", "payload": {"change_id": "T2", "patch": {"add": "audit"}, "replacement_spec": replacement, "rollback": {"remove": "audit"}, "falsifier": "BENCH:T2"}},
                {"type": "TOPOLOGY_TESTED", "payload": {"change_id": "T2", "observed_gain": 0.2, "invariant_regressions": []}},
                {"type": "TOPOLOGY_PROMOTED", "payload": {"change_id": "T2", "authority_ref": "AUTH:TOPOLOGY"}},
            ],
        )
        promoted_state = self.runtime.state("M1")
        self.assertIn("audit", promoted_state["snapshot"]["node_state"])
        self.assertEqual(promoted_state["topology_epoch"], 2)
        self.assertEqual(self.runtime.replay("M1")["status"], "REPLAY_MATCH")
        rolled_back = self.runtime.advance(
            "M1",
            promoted["revision"],
            [{"type": "TOPOLOGY_ROLLED_BACK", "payload": {"change_id": "T2", "rollback_receipt": "ROLLBACK:T2", "authority_ref": "AUTH:TOPOLOGY"}}],
        )
        rolled_state = self.runtime.state("M1")
        self.assertNotIn("audit", rolled_state["snapshot"]["node_state"])
        self.assertEqual(rolled_state["topology_epoch"], 3)
        self.assertEqual(rolled_back["revision"], 4)
        replay = self.runtime.replay("M1")
        self.assertEqual(replay["status"], "REPLAY_MATCH", replay)
        self.assertTrue(replay["active_spec_match"])

    def test_external_unknown_remains_open_not_zero(self):
        spec = {
            "initial_state": {},
            "goals": [{"id": "EXTERNAL", "external_only": True, "predicate": {"kind": "state_equals", "path": "world.result", "value": "PASS"}}],
            "nodes": [],
        }
        compiled = self.compile(spec, "EXT")
        self.assertFalse(compiled["terminal"]["terminal"])
        self.assertEqual(compiled["terminal"]["status"], "QUIESCENT_BLOCKED")
        self.assertFalse(compiled["plan"]["derived"]["goals"]["EXTERNAL"]["known"])
        self.assertGreater(compiled["plan"]["derived"]["goals"]["EXTERNAL"]["residual"], 0)

    def test_commit_rejects_hard_invariant_regression(self):
        spec = {
            "initial_state": {"x": 0},
            "hard_invariants": [
                {"id": "X_BOUNDED", "predicate": {"kind": "numeric_at_most", "path": "x", "value": 1}}
            ],
            "goals": [
                {"id": "G", "predicate": {"kind": "state_equals", "path": "x", "value": 1}}
            ],
            "nodes": [
                {"id": "N", "goals": ["G"], "readset": ["x"], "writeset": ["x"]}
            ],
        }
        self.compile(spec, "INVCOMMIT")
        plan = self.runtime.plan("INVCOMMIT")
        packet = plan["batch"][0]["nexus_packet"]
        events = [
            {"type": "CLAIMED", "payload": {"node_id": "N", "claim_id": "CL", "readset_digest": packet["readset_digest"], "writeset": packet["writeset"], "lease_until_revision": 10}},
            {"type": "CANDIDATE_PRODUCED", "payload": {"node_id": "N", "claim_id": "CL", "candidate_id": "C", "readset_digest": packet["readset_digest"], "state_delta": {"x": 2}}},
            {"type": "VERIFIED", "payload": {"node_id": "N", "candidate_id": "C", "passed": True, "verifier_ref": "V"}},
            {"type": "COMMITTED", "payload": {"node_id": "N", "candidate_id": "C", "authority_ref": "AUTH"}},
        ]
        with self.assertRaisesRegex(ValueError, "hard invariants"):
            self.runtime.advance("INVCOMMIT", 0, events)
        self.assertEqual(self.runtime.state("INVCOMMIT")["revision"], 0)

    def test_duplicate_event_id_is_rejected_without_partial_commit(self):
        self.compile()
        event = {
            "type": "STATE_OBSERVED",
            "event_id": "E-DUP",
            "payload": {"source_ref": "S", "state_delta": {"telemetry.tick": 1}},
        }
        first = self.runtime.advance("M1", 0, [event])
        with self.assertRaisesRegex(ValueError, "event_id already exists"):
            self.runtime.advance("M1", first["revision"], [event])
        self.assertEqual(self.runtime.state("M1")["revision"], first["revision"])

    def test_local_authority_mutation_requires_a_receipt(self):
        self.compile()
        with self.assertRaisesRegex(ValueError, "authority_ref"):
            self.runtime.advance(
                "M1",
                0,
                [{"type": "AUTHORITY_UPDATED", "payload": {"add": ["ADMIN"], "remove": []}}],
            )
        changed = self.runtime.advance(
            "M1",
            0,
            [{"type": "AUTHORITY_UPDATED", "payload": {"add": ["ADMIN"], "remove": [], "authority_ref": "AUTH:POLICY"}}],
        )
        self.assertIn("ADMIN", self.runtime.state("M1")["snapshot"]["authorities"])

    def test_topology_transition_requires_union_of_outgoing_and_incoming_authority(self):
        authority = FakeAuthority()
        authority.states["AUTH.BASE"] = {
            "claim_id": "AUTH.BASE", "y": "#", "status": "ACTIVE", "last_eid": "BASE1", "canonical_ref": "CANON:BASE", "source_ref": "POLICY"
        }
        authority.states["AUTH.NEW"] = {
            "claim_id": "AUTH.NEW", "y": "+", "status": "ACTIVE", "last_eid": "NEW1", "canonical_ref": None, "source_ref": "POLICY"
        }
        runtime = Nexus4dRuntime(self.store, authority)
        spec = base_spec()
        spec["topology_authority_claims"] = [{"claim_id": "AUTH.BASE", "min_y": "#"}]
        runtime.compile(spec, machine_id="TOPOAUTH")
        replacement = base_spec()
        replacement["topology_authority_claims"] = [{"claim_id": "AUTH.NEW", "min_y": "!"}]
        replacement["nodes"].append({"id": "audit", "goals": [], "readset": ["source.revision"], "writeset": []})
        staged = runtime.advance(
            "TOPOAUTH",
            0,
            [
                {"type": "TOPOLOGY_CANDIDATE", "payload": {"change_id": "T", "patch": {"add": "audit"}, "replacement_spec": replacement, "rollback": {"remove": "audit"}, "falsifier": "BENCH:T"}},
                {"type": "TOPOLOGY_TESTED", "payload": {"change_id": "T", "observed_gain": 0.5, "invariant_regressions": []}},
            ],
        )
        with self.assertRaisesRegex(ValueError, "topology promotion lacks"):
            runtime.advance(
                "TOPOAUTH",
                staged["revision"],
                [{"type": "TOPOLOGY_PROMOTED", "payload": {"change_id": "T", "authority_ref": "CANON:BASE+NEW"}}],
            )
        authority.states["AUTH.NEW"].update({"y": "!", "last_eid": "NEW2"})
        promoted = runtime.advance(
            "TOPOAUTH",
            staged["revision"],
            [{"type": "TOPOLOGY_PROMOTED", "payload": {"change_id": "T", "authority_ref": "CANON:BASE+NEW"}}],
        )
        authority.states["AUTH.BASE"].update({"y": "?", "status": "CHALLENGED", "last_eid": "BASE2"})
        with self.assertRaisesRegex(ValueError, "topology rollback lacks"):
            runtime.advance(
                "TOPOAUTH",
                promoted["revision"],
                [{"type": "TOPOLOGY_ROLLED_BACK", "payload": {"change_id": "T", "rollback_receipt": "RB:T", "authority_ref": "CANON:BASE+NEW"}}],
            )
        authority.states["AUTH.BASE"].update({"y": "#", "status": "ACTIVE", "last_eid": "BASE3"})
        rolled = runtime.advance(
            "TOPOAUTH",
            promoted["revision"],
            [{"type": "TOPOLOGY_ROLLED_BACK", "payload": {"change_id": "T", "rollback_receipt": "RB:T", "authority_ref": "CANON:BASE+NEW"}}],
        )
        self.assertNotIn("audit", runtime.state("TOPOAUTH")["snapshot"]["node_state"])
        self.assertEqual(runtime.replay("TOPOAUTH")["status"], "REPLAY_MATCH")


if __name__ == "__main__":
    unittest.main()
