from __future__ import annotations

import json
import unittest

from athena_mcp.party_coordination_v3 import (
    PARTY_RESULT_ARTIFACT,
    PARTY_REWARD_VERSION,
    PartyCoordinationRuntimeV3,
)
from athena_mcp.party_coordination_v3_1 import (
    PARTY_REWARD_ENVELOPE_VERSION,
    PartyCoordinationRuntimeV31,
)


class PartyRewardV31EnvelopeTests(unittest.TestCase):
    @staticmethod
    def event(
        *,
        version=PARTY_REWARD_VERSION,
        evidence_kind="RESULT",
        outer_kind="DISCOVERY",
        artifact=PARTY_RESULT_ARTIFACT,
    ):
        packet = {
            "artifact": artifact,
            "version": version,
            "party_id": "PARTY.TEST",
            "goal_id": "goal.analysis",
            "agent_id": "alpha",
            "claim_id": "MBC-alpha",
            "root_work_id": "WORK:alpha",
            "evidence_kind": evidence_kind,
            "result_ref": "result://alpha",
            "witness_ref": "witness://alpha",
            "recipients": ["beta"],
        }
        return {
            "artifact": "ATHENA.MESSAGE.BOARD.EVENT.V1",
            "event_id": "MBE-1",
            "kind": "MESSAGE",
            "agent_id": "alpha",
            "created_at": "2026-08-09T00:00:00+00:00",
            "payload": {
                "message_kind": outer_kind,
                "message": json.dumps(packet, sort_keys=True),
                "claim_id": "MBC-alpha",
            },
            "recipients": ["beta"],
        }

    def preflight(self, event):
        runtime = object.__new__(PartyCoordinationRuntimeV31)
        return runtime._validate_result_provenance(
            events=[event],
            event_map={"MBE-1": event},
            party={},
            member={},
            current_presence={},
            result={"result_event_ref": "MBE-1"},
            reward_window_start=None,
        )

    def test_v31_is_strict_subclass_without_replacing_v3_protocol_version(self):
        self.assertTrue(issubclass(PartyCoordinationRuntimeV31, PartyCoordinationRuntimeV3))
        self.assertEqual(PARTY_REWARD_VERSION, "PARTY.REWARD.PROVENANCE.3")
        self.assertEqual(PARTY_REWARD_ENVELOPE_VERSION, "PARTY.REWARD.PROVENANCE.3.1")

    def test_exact_result_discovery_pair_decodes(self):
        packet = PartyCoordinationRuntimeV31._decode_result_event(self.event())
        self.assertIsNotNone(packet)
        self.assertEqual(packet["evidence_kind"], "RESULT")

    def test_exact_verify_answer_pair_decodes(self):
        packet = PartyCoordinationRuntimeV31._decode_result_event(
            self.event(evidence_kind="VERIFY", outer_kind="ANSWER")
        )
        self.assertIsNotNone(packet)
        self.assertEqual(packet["evidence_kind"], "VERIFY")

    def test_missing_packet_version_fails_closed_with_typed_hold(self):
        event = self.event(version=None)
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        provenance, reasons = self.preflight(event)
        self.assertIsNone(provenance)
        self.assertEqual(reasons, ["RESULT_EVENT_VERSION_MISMATCH:MBE-1:MISSING"])

    def test_wrong_packet_version_fails_closed_with_typed_hold(self):
        event = self.event(version="PARTY.REWARD.PROVENANCE.2")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(
            reasons,
            ["RESULT_EVENT_VERSION_MISMATCH:MBE-1:PARTY.REWARD.PROVENANCE.2"],
        )

    def test_result_inner_answer_outer_is_role_mismatch(self):
        event = self.event(evidence_kind="RESULT", outer_kind="ANSWER")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(
            reasons,
            ["RESULT_EVENT_ROLE_MISMATCH:MBE-1:RESULT:ANSWER:DISCOVERY"],
        )

    def test_verify_inner_discovery_outer_is_role_mismatch(self):
        event = self.event(evidence_kind="VERIFY", outer_kind="DISCOVERY")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(
            reasons,
            ["RESULT_EVENT_ROLE_MISMATCH:MBE-1:VERIFY:DISCOVERY:ANSWER"],
        )

    def test_unknown_outer_kind_is_role_mismatch(self):
        event = self.event(evidence_kind="RESULT", outer_kind="INFO")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(
            reasons,
            ["RESULT_EVENT_ROLE_MISMATCH:MBE-1:RESULT:INFO:DISCOVERY"],
        )

    def test_unknown_inner_evidence_kind_fails_closed(self):
        event = self.event(evidence_kind="CLAIM", outer_kind="INFO")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(reasons, ["RESULT_EVENT_KIND_INVALID:MBE-1:CLAIM"])

    def test_artifact_only_handwritten_json_cannot_bypass_version_check(self):
        event = self.event(version="", artifact=PARTY_RESULT_ARTIFACT)
        raw_packet = json.loads(event["payload"]["message"])
        self.assertEqual(raw_packet["artifact"], PARTY_RESULT_ARTIFACT)
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(reasons, ["RESULT_EVENT_VERSION_MISMATCH:MBE-1:MISSING"])

    def test_wrong_artifact_remains_contract_mismatch(self):
        event = self.event(artifact="ATHENA.PARTY.RESULT.V0")
        self.assertIsNone(PartyCoordinationRuntimeV31._decode_result_event(event))
        _, reasons = self.preflight(event)
        self.assertEqual(reasons, ["RESULT_EVENT_CONTRACT_MISMATCH:MBE-1"])

    def test_coherence_does_not_claim_truth_or_independence(self):
        # Exact envelope coherence is a necessary provenance check only.
        packet = PartyCoordinationRuntimeV31._decode_result_event(self.event())
        self.assertIsNotNone(packet)
        self.assertNotIn("truth_verified", packet)
        self.assertNotIn("independent_verification", packet)


if __name__ == "__main__":
    unittest.main()
