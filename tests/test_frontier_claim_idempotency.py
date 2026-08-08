from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_claim import CLAIM_CONTRACT_BLOBS, FRONTIER_CLAIM_TOOLS, FrontierClaimRuntime
from athena_mcp.frontier_claim_idempotency import install_frontier_claim_idempotency


class FakeFrontier:
    def __init__(self):
        self.contract_actual = dict(CLAIM_CONTRACT_BLOBS)
        self.manifest = {
            "schema_version": "RUN_MANIFEST_V1",
            "run_id": "run.test",
            "objective_ref": "objective.test",
            "policy_commit": "a" * 40,
            "work_class": "PROJECT_WORK",
            "nodes": [
                {"node_id": "route", "role_capability": "builder", "depends_on": [], "max_attempts": 2, "claim_path": "runtime/runs/run.test/claims/route.json"},
                {"node_id": "claim", "role_capability": "verifier", "depends_on": [], "max_attempts": 2, "claim_path": "runtime/runs/run.test/claims/claim.json"},
            ],
        }
        self.events = [
            {"schema_version": "EVENT_V1", "event_id": "e1", "sequence": 1, "run_id": "run.test", "event_type": "RUN_CREATED", "at": "2026-08-08T20:00:01Z", "node_id": None, "data": {}},
            {"schema_version": "EVENT_V1", "event_id": "e2", "sequence": 2, "run_id": "run.test", "event_type": "RUN_ADMITTED", "at": "2026-08-08T20:00:02Z", "node_id": None, "data": {"verdict": "PASS"}},
            {"schema_version": "EVENT_V1", "event_id": "e3", "sequence": 3, "run_id": "run.test", "event_type": "NODE_READY", "at": "2026-08-08T20:00:03Z", "node_id": "claim", "data": {}},
        ]
        self.packet = {
            "status": "HYDRATED",
            "source_ref": "agent/sched-v3-event-journal-v1",
            "source_head": "source-head-1",
            "resolved_ref": "refs/remotes/origin/agent/sched-v3-event-journal-v1",
            "remote_checked": True,
            "generated_from": [],
            "objectives": [],
            "runs": [{
                "run_id": "run.test",
                "objective_id": "objective.test",
                "priority": 100,
                "production_authority": "HOLD",
                "reduction_basis": "EVENT_REDUCED",
                "projection": {"run_state": "ADMITTED", "node_states": {"route": "PENDING", "claim": "READY"}, "attempts": {"route": 0, "claim": 0}},
            }],
            "pressures": [],
            "ready_work": [{
                "run_id": "run.test",
                "objective_id": "objective.test",
                "node_id": "route",
                "role_capability": "builder",
                "claim_path": "runtime/runs/run.test/claims/route.json",
                "priority": 100,
                "dependency_release": 0,
                "attempts_remaining": 2,
                "production_authority": "HOLD",
            }],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {},
            "authority": {},
            "sched_contract": {"status": "PASS"},
            "prompt_stack_digest": "prompt-digest-1",
            "laws": [],
            "frontier_digest": "legacy-digest",
        }

    def hydrate(self, **kwargs):
        return copy.deepcopy(self.packet)

    def _blob(self, source_head, path):
        return self.contract_actual.get(path)

    def _root(self):
        return Path(tempfile.gettempdir())

    def _json(self, source_head, path):
        if path.endswith("/manifest.json"):
            return copy.deepcopy(self.manifest)
        if "/events/" in path:
            sequence = int(path.rsplit("/", 1)[1].split(".")[0])
            return copy.deepcopy(next((e for e in self.events if int(e["sequence"]) == sequence), None))
        return None

    def _paths(self, source_head, *prefixes):
        out = []
        for prefix in prefixes:
            if prefix.endswith("/events"):
                out.extend(f"runtime/runs/run.test/events/{int(e['sequence']):08d}.json" for e in self.events)
        return sorted(out)

    @staticmethod
    def _dependency_release(manifest, node_id):
        return sum(1 for node in manifest.get("nodes") or [] if node_id in (node.get("depends_on") or []))

    def _reduce_events(self, manifest, events):
        states = {str(n["node_id"]): "PENDING" for n in manifest.get("nodes") or []}
        attempts = {node_id: 0 for node_id in states}
        run_state = "QUEUED"
        for event in sorted(events, key=lambda x: int(x["sequence"])):
            typ = event["event_type"]
            node_id = event.get("node_id")
            if typ == "RUN_ADMITTED":
                run_state = "ADMITTED"
            elif typ == "NODE_READY":
                if states[node_id] != "PENDING":
                    raise ValueError("invalid NODE_READY")
                states[node_id] = "READY"
            elif typ == "CLAIM_ACQUIRED":
                if states[node_id] != "READY":
                    raise ValueError("invalid CLAIM_ACQUIRED")
                states[node_id] = "CLAIMED"
        ready = []
        for node in manifest.get("nodes") or []:
            node_id = str(node["node_id"])
            if states[node_id] == "PENDING" and all(states[str(d)] == "SUCCEEDED" for d in node.get("depends_on") or []):
                ready.append(node_id)
        return {"run_state": run_state, "node_states": states, "attempts": attempts, "ready_nodes": ready}


class FrontierClaimIdempotencyTests(unittest.TestCase):
    def _runtime(self):
        fake = FakeFrontier()
        ext = FrontierClaimRuntime(fake, environ={})
        ext._remote_repo = lambda remote: "demeet2k/Athena"
        install_frontier_claim_idempotency(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        return fake, ext, contract

    def _common(self, fake, contract):
        return {
            "expected_source_head": fake.packet["source_head"],
            "expected_frontier_digest": fake.packet["frontier_digest"],
            "expected_prompt_stack_digest": fake.packet["prompt_stack_digest"],
            "expected_claim_contract_digest": contract["claim_contract_digest"],
            "source_ref": "agent/sched-v3-event-journal-v1",
            "remote": "origin",
        }

    def test_same_operation_at_yields_byte_identical_claim_packet(self):
        fake, ext, contract = self._runtime()
        kwargs = {**self._common(fake, contract), "run_id": "run.test", "node_id": "claim", "worker_role": "verifier", "lease_seconds": 600, "operation_at": "2026-08-08T20:40:00Z"}
        first = ext.claim_prepare(**kwargs)
        second = ext.claim_prepare(**kwargs)
        self.assertEqual(first["status"], "CLAIM_EFFECT_PREPARED")
        self.assertEqual(first["operation_id"], second["operation_id"])
        self.assertEqual(first["prepared_packet_digest"], second["prepared_packet_digest"])
        self.assertEqual(first["provider"]["content_text"], second["provider"]["content_text"])
        self.assertEqual(first["provider"]["content"]["claimed_at"], "2026-08-08T20:40:00Z")
        self.assertEqual(first["provider"]["content"]["lease_expires_at"], "2026-08-08T20:50:00Z")

    def test_same_operation_at_yields_byte_identical_node_ready_prerequisite(self):
        fake, ext, contract = self._runtime()
        fake.events = fake.events[:2]
        fake.packet["runs"][0]["projection"]["node_states"] = {"route": "PENDING", "claim": "PENDING"}
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        kwargs = {**self._common(fake, contract), "run_id": "run.test", "node_id": "route", "worker_role": "builder", "operation_at": "2026-08-08T20:41:00+00:00"}
        first = ext.claim_prepare(**kwargs)
        second = ext.claim_prepare(**kwargs)
        a = first["readiness_prerequisite"]
        b = second["readiness_prerequisite"]
        self.assertEqual(a["operation_id"], b["operation_id"])
        self.assertEqual(a["prepared_packet_digest"], b["prepared_packet_digest"])
        self.assertEqual(a["provider"]["content_text"], b["provider"]["content_text"])
        self.assertEqual(a["provider"]["content"]["at"], "2026-08-08T20:41:00Z")

    def test_different_operation_at_changes_operation_identity(self):
        fake, ext, contract = self._runtime()
        base = {**self._common(fake, contract), "run_id": "run.test", "node_id": "claim", "worker_role": "verifier", "lease_seconds": 600}
        first = ext.claim_prepare(**base, operation_at="2026-08-08T20:40:00Z")
        second = ext.claim_prepare(**base, operation_at="2026-08-08T20:40:01Z")
        self.assertNotEqual(first["operation_id"], second["operation_id"])
        self.assertNotEqual(first["prepared_packet_digest"], second["prepared_packet_digest"])

    def test_operation_at_requires_timezone(self):
        fake, ext, contract = self._runtime()
        with self.assertRaisesRegex(ValueError, "timezone"):
            ext.claim_prepare(**self._common(fake, contract), run_id="run.test", node_id="claim", worker_role="verifier", operation_at="2026-08-08T20:40:00")

    def test_public_schema_requires_operation_at(self):
        install_frontier_claim_idempotency(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        tool = next(x for x in FRONTIER_CLAIM_TOOLS if x["name"] == "athena_frontier_claim_prepare")
        self.assertIn("operation_at", tool["inputSchema"]["required"])
        self.assertIn("operation_at", tool["inputSchema"]["properties"])


if __name__ == "__main__":
    unittest.main()
