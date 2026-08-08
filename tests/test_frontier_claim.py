from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_claim import (
    CLAIM_CONTRACT_BLOBS,
    FRONTIER_CLAIM_TOOL_NAMES,
    FrontierClaimRuntime,
    install_frontier_claim_extension,
)


class FakeFrontier:
    def __init__(self):
        self.contract_actual = dict(CLAIM_CONTRACT_BLOBS)
        self.manifests = {
            "run.test": {
                "schema_version": "RUN_MANIFEST_V1",
                "run_id": "run.test",
                "objective_ref": "objective.test",
                "policy_commit": "a" * 40,
                "work_class": "PROJECT_WORK",
                "nodes": [
                    {
                        "node_id": "route",
                        "role_capability": "builder",
                        "depends_on": [],
                        "max_attempts": 2,
                        "claim_path": "runtime/runs/run.test/claims/route.json",
                    },
                    {
                        "node_id": "claim",
                        "role_capability": "verifier",
                        "depends_on": [],
                        "max_attempts": 2,
                        "claim_path": "runtime/runs/run.test/claims/claim.json",
                    },
                ],
            }
        }
        self.events = {
            "run.test": [
                {
                    "schema_version": "EVENT_V1",
                    "event_id": "e1",
                    "sequence": 1,
                    "run_id": "run.test",
                    "event_type": "RUN_CREATED",
                    "at": "2026-08-08T20:00:01Z",
                    "node_id": None,
                    "data": {},
                },
                {
                    "schema_version": "EVENT_V1",
                    "event_id": "e2",
                    "sequence": 2,
                    "run_id": "run.test",
                    "event_type": "RUN_ADMITTED",
                    "at": "2026-08-08T20:00:02Z",
                    "node_id": None,
                    "data": {"verdict": "PASS"},
                },
                {
                    "schema_version": "EVENT_V1",
                    "event_id": "e3",
                    "sequence": 3,
                    "run_id": "run.test",
                    "event_type": "NODE_READY",
                    "at": "2026-08-08T20:00:03Z",
                    "node_id": "claim",
                    "data": {},
                },
            ]
        }
        self.packet = self._packet()

    def _packet(self):
        return {
            "status": "HYDRATED",
            "source_ref": "agent/sched-v3-event-journal-v1",
            "source_head": "source-head-1",
            "resolved_ref": "refs/remotes/origin/agent/sched-v3-event-journal-v1",
            "remote_checked": True,
            "generated_from": [],
            "objectives": [],
            "runs": [
                {
                    "run_id": "run.test",
                    "objective_id": "objective.test",
                    "priority": 100,
                    "production_authority": "HOLD",
                    "reduction_basis": "EVENT_REDUCED",
                    "projection": {
                        "run_state": "RUNNING",
                        "node_states": {"route": "PENDING", "claim": "READY"},
                        "attempts": {"route": 0, "claim": 0},
                    },
                }
            ],
            "pressures": [],
            "ready_work": [
                {
                    "run_id": "run.test",
                    "objective_id": "objective.test",
                    "node_id": "route",
                    "role_capability": "builder",
                    "claim_path": "runtime/runs/run.test/claims/route.json",
                    "priority": 100,
                    "dependency_release": 0,
                    "attempts_remaining": 2,
                    "production_authority": "HOLD",
                }
            ],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {},
            "authority": {"law": "FRONTIER_BRAID != EXECUTION_AUTHORIZATION"},
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
            run_id = path.split("/")[2]
            return copy.deepcopy(self.manifests.get(run_id))
        if "/events/" in path:
            run_id = path.split("/")[2]
            filename = path.rsplit("/", 1)[1]
            sequence = int(filename.split(".")[0])
            for event in self.events.get(run_id, []):
                if int(event["sequence"]) == sequence:
                    return copy.deepcopy(event)
        return None

    def _paths(self, source_head, *prefixes):
        out = []
        for prefix in prefixes:
            if prefix.endswith("/events"):
                run_id = prefix.split("/")[2]
                out.extend(
                    f"runtime/runs/{run_id}/events/{int(e['sequence']):08d}.json"
                    for e in self.events.get(run_id, [])
                )
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
            if typ == "RUN_CREATED":
                run_state = "QUEUED"
            elif typ == "RUN_ADMITTED":
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


class FrontierClaimTests(unittest.TestCase):
    def _extension(self):
        fake = FakeFrontier()
        ext = FrontierClaimRuntime(fake, environ={})
        ext._remote_repo = lambda remote: "demeet2k/Athena"
        return fake, ext

    def test_augment_separates_routing_ready_from_event_ready(self):
        fake, ext = self._extension()
        packet = ext.augment_packet(fake.hydrate())
        self.assertEqual([x["node_id"] for x in packet["routing_ready_work"]], ["route"])
        self.assertFalse(packet["routing_ready_work"][0]["claim_eligible"])
        self.assertEqual(packet["routing_ready_work"][0]["reducer_state"], "PENDING")
        self.assertEqual([x["node_id"] for x in packet["claimable_work"]], ["claim"])
        self.assertTrue(packet["claimable_work"][0]["claim_eligible"])
        self.assertEqual(packet["claimable_work"][0]["readiness_basis"], "EVENT_READY")
        self.assertIn("INFERRED_READY != EVENT_READY", packet["laws"])
        self.assertNotEqual(packet["frontier_digest"], "legacy-digest")

    def test_existing_fixed_claim_suppresses_event_ready_claimability(self):
        fake, ext = self._extension()
        fake.packet["claims"] = [{"run_id": "run.test", "node_id": "claim", "worker_role": "verifier"}]
        packet = ext.augment_packet(fake.hydrate())
        self.assertEqual(packet["claimable_work"], [])
        self.assertTrue(any(x.get("node_id") == "claim" for x in packet["claim_readiness_suppressed"]))
        self.assertTrue(any(x.get("code") == "EVENT_READY_WITH_PROVIDER_CLAIM_PRESENT" for x in packet["residuals"]))

    def test_five_blob_contract_fails_closed_when_journal_is_missing(self):
        fake, ext = self._extension()
        fake.contract_actual.pop("orchestration/v3/journal.py")
        status = ext._contract("source-head-1")
        self.assertEqual(status["status"], "CLAIM_CONTRACT_UNAVAILABLE_HOLD")
        self.assertIsNone(status["contracts"]["orchestration/v3/journal.py"]["actual_blob"])

    def test_provider_status_never_exposes_token(self):
        fake = FakeFrontier()
        ext = FrontierClaimRuntime(fake, environ={"ATHENA_GITHUB_TOKEN": "super-secret-token"})
        ext._remote_repo = lambda remote: "demeet2k/Athena"
        fake.packet = ext.augment_packet(fake.packet)
        result = ext.provider_status(source_ref="agent/sched-v3-event-journal-v1", remote="origin", fetch=True)
        self.assertTrue(result["provider_token_configured"])
        self.assertNotIn("super-secret-token", json.dumps(result, sort_keys=True))
        self.assertEqual(result["claim_contract"]["status"], "PASS")

    def test_stale_address_holds_before_claim_packet(self):
        fake, ext = self._extension()
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        result = ext.claim_prepare(
            expected_source_head="stale-head",
            expected_frontier_digest=fake.packet["frontier_digest"],
            expected_prompt_stack_digest=fake.packet["prompt_stack_digest"],
            expected_claim_contract_digest=contract["claim_contract_digest"],
            run_id="run.test",
            node_id="claim",
            worker_role="verifier",
            source_ref="agent/sched-v3-event-journal-v1",
            remote="origin",
        )
        self.assertEqual(result["status"], "CLAIM_STALE_ADDRESS_HOLD")
        self.assertTrue(result["changed"]["source_head"])
        self.assertNotIn("provider", result)

    def test_inferred_ready_returns_node_ready_prerequisite_not_claim(self):
        fake, ext = self._extension()
        fake.events["run.test"] = fake.events["run.test"][:2]
        fake.packet["runs"][0]["projection"]["node_states"] = {"route": "PENDING", "claim": "PENDING"}
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        result = ext.claim_prepare(
            expected_source_head=fake.packet["source_head"],
            expected_frontier_digest=fake.packet["frontier_digest"],
            expected_prompt_stack_digest=fake.packet["prompt_stack_digest"],
            expected_claim_contract_digest=contract["claim_contract_digest"],
            run_id="run.test",
            node_id="route",
            worker_role="builder",
            source_ref="agent/sched-v3-event-journal-v1",
            remote="origin",
        )
        self.assertEqual(result["status"], "EVENT_READY_REQUIRED_HOLD")
        ready = result["readiness_prerequisite"]
        self.assertEqual(ready["status"], "NODE_READY_APPEND_PREPARED")
        self.assertEqual(ready["provider"]["provider_operation"], "CREATE_FILE_IF_ABSENT")
        self.assertEqual(ready["provider"]["path"], "runtime/runs/run.test/events/00000003.json")
        self.assertEqual(ready["projection_after"]["node_states"]["route"], "READY")
        self.assertNotEqual(ready["provider"]["kind"], "CLAIM_V1")

    def test_event_ready_prepares_exact_claim_v1_without_write(self):
        fake, ext = self._extension()
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        result = ext.claim_prepare(
            expected_source_head=fake.packet["source_head"],
            expected_frontier_digest=fake.packet["frontier_digest"],
            expected_prompt_stack_digest=fake.packet["prompt_stack_digest"],
            expected_claim_contract_digest=contract["claim_contract_digest"],
            run_id="run.test",
            node_id="claim",
            worker_role="verifier",
            lease_seconds=600,
            source_ref="agent/sched-v3-event-journal-v1",
            remote="origin",
        )
        self.assertEqual(result["status"], "CLAIM_EFFECT_PREPARED")
        self.assertEqual(result["claim_path"], "runtime/runs/run.test/claims/claim.json")
        self.assertEqual(result["provider"]["provider_operation"], "CREATE_FILE_IF_ABSENT")
        self.assertEqual(result["provider"]["kind"], "CLAIM_V1")
        claim = result["provider"]["content"]
        self.assertEqual(set(claim), {
            "schema_version", "run_id", "node_id", "worker_role", "attempt", "policy_commit",
            "claimed_at", "lease_expires_at", "input_snapshot_digest", "production_authority"
        })
        self.assertEqual(claim["schema_version"], "CLAIM_V1")
        self.assertEqual(claim["production_authority"], "HOLD")
        self.assertEqual(len(claim["input_snapshot_digest"]), 64)
        self.assertEqual(result["address"]["frontier_digest"], fake.packet["frontier_digest"])

    def test_installer_is_additive_and_does_not_execute_write(self):
        class DummyRuntime:
            def hydrate(self, **kwargs):
                return {"status": "HYDRATED", "runs": [], "ready_work": [], "claims": [], "residuals": [], "source_coverage": {}, "laws": [], "objectives": [], "pressures": [], "authority": {}, "sched_contract": {}, "generated_from": [], "source_head": "h", "prompt_stack_digest": "p", "frontier_digest": "f"}
            def call_tool(self, name, arguments):
                return {"legacy": name}

        tools = []
        install_frontier_claim_extension(DummyRuntime, tools)
        self.assertEqual({x["name"] for x in tools}, FRONTIER_CLAIM_TOOL_NAMES)
        runtime = DummyRuntime()
        self.assertEqual(runtime.call_tool("legacy", {})["legacy"], "legacy")


if __name__ == "__main__":
    unittest.main()
