from __future__ import annotations

import base64
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib import error

from athena_mcp.frontier_claim import CLAIM_CONTRACT_BLOBS, FRONTIER_CLAIM_TOOLS, FrontierClaimRuntime, _provider_packet
from athena_mcp.frontier_claim_idempotency import install_frontier_claim_idempotency
from athena_mcp.frontier_claim_provider import (
    GitHubContentsCreateProvider,
    claim_execute,
    install_frontier_claim_provider,
    ready_execute,
    reconcile_execute,
)


class FakeResponse:
    def __init__(self, payload: dict, status: int = 201):
        self.payload = payload
        self.status = status

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeFrontier:
    def __init__(self, *, ready=True):
        self.contract_actual = dict(CLAIM_CONTRACT_BLOBS)
        self.rev = 1
        self.claims: dict[str, dict] = {}
        self.provider_files: dict[str, dict] = {}
        self.manifest = {
            "schema_version": "RUN_MANIFEST_V1",
            "run_id": "run.test",
            "objective_ref": "objective.test",
            "policy_commit": "a" * 40,
            "work_class": "PROJECT_WORK",
            "nodes": [
                {
                    "node_id": "claim",
                    "role_capability": "verifier",
                    "depends_on": [],
                    "max_attempts": 2,
                    "claim_path": "runtime/runs/run.test/claims/claim.json",
                }
            ],
        }
        self.events = [
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
        ]
        if ready:
            self.events.append(
                {
                    "schema_version": "EVENT_V1",
                    "event_id": "e3",
                    "sequence": 3,
                    "run_id": "run.test",
                    "event_type": "NODE_READY",
                    "at": "2026-08-08T20:00:03Z",
                    "node_id": "claim",
                    "data": {},
                }
            )
        self.ext: FrontierClaimRuntime | None = None

    def _projection(self):
        return self._reduce_events(self.manifest, self.events)

    def hydrate(self, **kwargs):
        projection = self._projection()
        ready_work = []
        if projection["node_states"]["claim"] == "PENDING":
            ready_work.append(
                {
                    "run_id": "run.test",
                    "objective_id": "objective.test",
                    "node_id": "claim",
                    "role_capability": "verifier",
                    "claim_path": "runtime/runs/run.test/claims/claim.json",
                    "priority": 100,
                    "dependency_release": 0,
                    "attempts_remaining": 2,
                    "production_authority": "HOLD",
                }
            )
        base = {
            "status": "HYDRATED",
            "source_ref": "agent/sched-v3-event-journal-v1",
            "source_head": f"source-head-{self.rev}",
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
                    "projection": projection,
                }
            ],
            "pressures": [],
            "ready_work": ready_work,
            "claims": [copy.deepcopy(value) for value in self.claims.values()],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {},
            "authority": {},
            "sched_contract": {"status": "PASS"},
            "prompt_stack_digest": "prompt-digest-1",
            "laws": [],
            "frontier_digest": "base-digest",
        }
        return self.ext.augment_packet(base) if self.ext else base

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
        if "/claims/" in path:
            return copy.deepcopy(self.claims.get(path))
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
        ready_nodes = []
        for node in manifest.get("nodes") or []:
            node_id = str(node["node_id"])
            if states[node_id] == "PENDING" and all(states[str(dep)] == "SUCCEEDED" for dep in node.get("depends_on") or []):
                ready_nodes.append(node_id)
        return {"run_state": run_state, "node_states": states, "attempts": attempts, "ready_nodes": ready_nodes}


class FakeOpener:
    def __init__(self, frontier: FakeFrontier):
        self.frontier = frontier
        self.calls = []
        self.fail_event = False
        self.force_status = None

    def __call__(self, req, timeout=20):
        self.calls.append(req)
        path = req.full_url.split("/contents/", 1)[1]
        from urllib.parse import unquote

        path = unquote(path)
        if path in self.frontier.provider_files:
            raise error.HTTPError(req.full_url, 422, "exists", {}, io.BytesIO(b"{}"))
        if self.fail_event and "/events/" in path:
            raise error.HTTPError(req.full_url, 500, "event failed", {}, io.BytesIO(b"{}"))
        body = json.loads(req.data.decode("utf-8"))
        content = json.loads(base64.b64decode(body["content"]).decode("utf-8"))
        status = 201 if self.force_status is None else int(self.force_status)
        if status == 201:
            self.frontier.provider_files[path] = copy.deepcopy(content)
            if "/claims/" in path:
                self.frontier.claims[path] = copy.deepcopy(content)
            elif "/events/" in path:
                self.frontier.events.append(copy.deepcopy(content))
                self.frontier.events.sort(key=lambda e: int(e["sequence"]))
            self.frontier.rev += 1
        return FakeResponse({"content": {"sha": f"blob-{self.frontier.rev}"}, "commit": {"sha": f"commit-{self.frontier.rev}"}}, status=status)


class FrontierClaimProviderTests(unittest.TestCase):
    def _runtime(self, *, ready=True):
        fake = FakeFrontier(ready=ready)
        runtime = FrontierClaimRuntime(fake, environ={"GITHUB_TOKEN": "super-secret-token"})
        fake.ext = runtime
        runtime._remote_repo = lambda remote: "demeet2k/Athena"
        install_frontier_claim_idempotency(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        install_frontier_claim_provider(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        opener = FakeOpener(fake)
        runtime._athena_claim_provider_opener = opener
        return fake, runtime, opener

    def _args(self, runtime):
        packet = runtime.frontier.hydrate(source_ref="agent/sched-v3-event-journal-v1", remote="origin", fetch=True)
        contract = runtime._contract(packet["source_head"])
        return {
            "expected_source_head": packet["source_head"],
            "expected_frontier_digest": packet["frontier_digest"],
            "expected_prompt_stack_digest": packet["prompt_stack_digest"],
            "expected_claim_contract_digest": contract["claim_contract_digest"],
            "run_id": "run.test",
            "node_id": "claim",
            "worker_role": "verifier",
            "lease_seconds": 600,
            "operation_at": "2026-08-08T20:40:00Z",
            "source_ref": "agent/sched-v3-event-journal-v1",
            "remote": "origin",
        }

    def test_provider_rejects_arbitrary_path_without_network(self):
        fake, runtime, opener = self._runtime()
        packet = _provider_packet("README.md", {"schema_version": "CLAIM_V1", "run_id": "run.test", "node_id": "claim"}, kind="CLAIM_V1")
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(repo="demeet2k/Athena", branch="test", packet=packet)
        self.assertEqual(result["status"], "PROVIDER_PACKET_REJECTED")
        self.assertEqual(len(opener.calls), 0)

    def test_provider_rejects_path_body_mismatch_without_network(self):
        fake, runtime, opener = self._runtime()
        content = {
            "schema_version": "CLAIM_V1",
            "run_id": "run.other",
            "node_id": "claim",
            "worker_role": "verifier",
            "attempt": 1,
            "policy_commit": "a" * 40,
            "claimed_at": "2026-08-08T20:40:00Z",
            "lease_expires_at": "2026-08-08T20:50:00Z",
            "input_snapshot_digest": "b" * 64,
            "production_authority": "HOLD",
        }
        packet = _provider_packet("runtime/runs/run.test/claims/claim.json", content, kind="CLAIM_V1")
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(repo="demeet2k/Athena", branch="test", packet=packet)
        self.assertEqual(result["status"], "PROVIDER_PACKET_REJECTED")
        self.assertEqual(len(opener.calls), 0)

    def test_success_receipt_never_contains_token(self):
        fake, runtime, opener = self._runtime()
        prepared = runtime.claim_prepare(**self._args(runtime))
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(
            repo="demeet2k/Athena", branch="agent/sched-v3-event-journal-v1", packet=prepared["provider"]
        )
        self.assertEqual(result["status"], "CREATED")
        self.assertNotIn("super-secret-token", json.dumps(result, sort_keys=True))

    def test_http_200_is_not_accepted_as_create(self):
        fake, runtime, opener = self._runtime()
        opener.force_status = 200
        prepared = runtime.claim_prepare(**self._args(runtime))
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(
            repo="demeet2k/Athena", branch="agent/sched-v3-event-journal-v1", packet=prepared["provider"]
        )
        self.assertNotEqual(result["status"], "CREATED")

    def test_claim_execute_creates_claim_and_journals_event(self):
        fake, runtime, opener = self._runtime()
        result = claim_execute(runtime, self._args(runtime))
        self.assertEqual(result["status"], "CLAIM_JOURNALED")
        self.assertEqual(result["observed"]["reducer_state"], "CLAIMED")
        self.assertTrue(result["observed"]["claim_visible"])
        self.assertFalse(result["observed"]["still_claimable"])
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(fake.events[-1]["event_type"], "CLAIM_ACQUIRED")

    def test_claim_execute_lost_race_writes_no_event(self):
        fake, runtime, opener = self._runtime()
        path = "runtime/runs/run.test/claims/claim.json"
        opener.frontier.provider_files[path] = {"occupied": True}
        result = claim_execute(runtime, self._args(runtime))
        self.assertEqual(result["status"], "CLAIM_LOST_RACE")
        self.assertEqual(len(fake.events), 3)

    def test_claim_event_failure_preserves_unjournaled_claim(self):
        fake, runtime, opener = self._runtime()
        opener.fail_event = True
        result = claim_execute(runtime, self._args(runtime))
        self.assertEqual(result["status"], "CLAIM_EFFECT_UNJOURNALED_HOLD")
        self.assertIn("runtime/runs/run.test/claims/claim.json", fake.claims)
        self.assertEqual(fake._projection()["node_states"]["claim"], "READY")

    def test_ready_execute_persists_only_node_ready_then_rehydrates(self):
        fake, runtime, opener = self._runtime(ready=False)
        result = ready_execute(runtime, self._args(runtime))
        self.assertEqual(result["status"], "NODE_READY_JOURNALED")
        self.assertEqual(fake._projection()["node_states"]["claim"], "READY")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(fake.events[-1]["event_type"], "NODE_READY")

    def test_reconcile_journals_existing_unjournaled_claim_only(self):
        fake, runtime, opener = self._runtime()
        prepared = runtime.claim_prepare(**self._args(runtime))
        claim_path = prepared["claim_path"]
        fake.claims[claim_path] = copy.deepcopy(prepared["provider"]["content"])
        fake.provider_files[claim_path] = copy.deepcopy(prepared["provider"]["content"])
        fake.rev += 1
        args = self._args(runtime)
        args.pop("operation_at")
        result = reconcile_execute(runtime, args)
        self.assertEqual(result["status"], "CLAIM_JOURNALED")
        self.assertEqual(fake._projection()["node_states"]["claim"], "CLAIMED")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(fake.events[-1]["event_type"], "CLAIM_ACQUIRED")

    def test_stale_address_rejects_before_provider_call(self):
        fake, runtime, opener = self._runtime()
        args = self._args(runtime)
        args["expected_source_head"] = "stale-head"
        result = claim_execute(runtime, args)
        self.assertEqual(result["status"], "CLAIM_STALE_ADDRESS_HOLD")
        self.assertEqual(len(opener.calls), 0)

    def test_server_registration_exposes_only_bounded_execution_tools(self):
        import athena_mcp.server  # noqa: F401 - triggers bootstrap registration
        from athena_mcp.frontier_runtime import FRONTIER_TOOL_NAMES
        from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES

        expected = {"athena_frontier_ready", "athena_frontier_claim", "athena_frontier_claim_reconcile"}
        self.assertTrue(expected.issubset(FRONTIER_TOOL_NAMES))
        self.assertTrue(expected.issubset(PROMPT_RUNTIME_TOOL_NAMES))
        self.assertNotIn("athena_github_write_file", FRONTIER_TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()
