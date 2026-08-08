from __future__ import annotations

import json
import unittest

from athena_mcp.frontier_claim import CLAIM_CONTRACT_BLOBS, FRONTIER_CLAIM_TOOLS, FrontierClaimRuntime
from athena_mcp.frontier_claim_idempotency import install_frontier_claim_idempotency
from athena_mcp.frontier_claim_provider import GitHubContentsCreateProvider, claim_execute, install_frontier_claim_provider
from athena_mcp.frontier_claim_provider_guard import install_frontier_claim_provider_guard
from tests.test_frontier_claim_provider import FakeFrontier, FakeOpener


class FrontierClaimProviderGuardTests(unittest.TestCase):
    def _runtime(self):
        fake = FakeFrontier(ready=True)
        runtime = FrontierClaimRuntime(fake, environ={"GITHUB_TOKEN": "guard-secret-token"})
        fake.ext = runtime
        runtime._remote_repo = lambda remote: "demeet2k/Athena"
        install_frontier_claim_idempotency(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        install_frontier_claim_provider(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        install_frontier_claim_provider_guard(FrontierClaimRuntime)
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

    def test_http_200_update_like_response_is_not_create_success(self):
        fake, runtime, opener = self._runtime()
        opener.force_status = 200
        prepared = runtime.claim_prepare(**self._args(runtime))
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=prepared["provider"],
        )
        self.assertEqual(result["status"], "PROVIDER_HOLD")
        self.assertEqual(result["http_status"], 200)
        self.assertIn("HTTP_200_UPDATE_SEMANTICS", result["law"])
        self.assertNotIn("guard-secret-token", json.dumps(result, sort_keys=True))

    def test_contract_drift_after_claim_create_blocks_journal_effect(self):
        fake, runtime, opener = self._runtime()
        original = opener.__call__
        calls = {"n": 0}

        def drift_after_first(req, timeout=20):
            response = original(req, timeout=timeout)
            calls["n"] += 1
            if calls["n"] == 1:
                first_path = next(iter(CLAIM_CONTRACT_BLOBS))
                fake.contract_actual[first_path] = "drifted-blob"
            return response

        runtime._athena_claim_provider_opener = drift_after_first
        result = claim_execute(runtime, self._args(runtime))
        self.assertEqual(result["status"], "CLAIM_EFFECT_UNJOURNALED_HOLD")
        self.assertIn("scheduler interpretation contract changed", result["journal"]["reason"])
        self.assertIn("runtime/runs/run.test/claims/claim.json", fake.claims)
        self.assertEqual(fake._projection()["node_states"]["claim"], "READY")
        self.assertEqual(calls["n"], 1)

    def test_guard_is_idempotent(self):
        fake, runtime, opener = self._runtime()
        install_frontier_claim_provider_guard(FrontierClaimRuntime)
        install_frontier_claim_provider_guard(FrontierClaimRuntime)
        opener.force_status = 200
        prepared = runtime.claim_prepare(**self._args(runtime))
        result = GitHubContentsCreateProvider(runtime, opener=opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=prepared["provider"],
        )
        self.assertEqual(result["status"], "PROVIDER_HOLD")


if __name__ == "__main__":
    unittest.main()
