from __future__ import annotations

import copy
import unittest

from athena_mcp.frontier_claim import CLAIM_CONTRACT_BLOBS, FRONTIER_CLAIM_TOOLS, FrontierClaimRuntime
from athena_mcp.frontier_claim_idempotency import install_frontier_claim_idempotency
from tests.test_frontier_claim import FakeFrontier


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
        kwargs = {
            **self._common(fake, contract),
            "run_id": "run.test",
            "node_id": "claim",
            "worker_role": "verifier",
            "lease_seconds": 600,
            "operation_at": "2026-08-08T20:40:00Z",
        }
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
        fake.events["run.test"] = fake.events["run.test"][:2]
        fake.packet["runs"][0]["projection"]["node_states"] = {"route": "PENDING", "claim": "PENDING"}
        fake.packet = ext.augment_packet(fake.packet)
        contract = ext._contract(fake.packet["source_head"])
        kwargs = {
            **self._common(fake, contract),
            "run_id": "run.test",
            "node_id": "route",
            "worker_role": "builder",
            "operation_at": "2026-08-08T20:41:00+00:00",
        }
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
        base = {
            **self._common(fake, contract),
            "run_id": "run.test",
            "node_id": "claim",
            "worker_role": "verifier",
            "lease_seconds": 600,
        }
        first = ext.claim_prepare(**base, operation_at="2026-08-08T20:40:00Z")
        second = ext.claim_prepare(**base, operation_at="2026-08-08T20:40:01Z")
        self.assertNotEqual(first["operation_id"], second["operation_id"])
        self.assertNotEqual(first["prepared_packet_digest"], second["prepared_packet_digest"])

    def test_operation_at_requires_timezone(self):
        fake, ext, contract = self._runtime()
        with self.assertRaisesRegex(ValueError, "timezone"):
            ext.claim_prepare(
                **self._common(fake, contract),
                run_id="run.test",
                node_id="claim",
                worker_role="verifier",
                operation_at="2026-08-08T20:40:00",
            )

    def test_public_schema_requires_operation_at(self):
        install_frontier_claim_idempotency(FrontierClaimRuntime, FRONTIER_CLAIM_TOOLS)
        tool = next(x for x in FRONTIER_CLAIM_TOOLS if x["name"] == "athena_frontier_claim_prepare")
        self.assertIn("operation_at", tool["inputSchema"]["required"])
        self.assertIn("operation_at", tool["inputSchema"]["properties"])


if __name__ == "__main__":
    unittest.main()
