from __future__ import annotations

import copy
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]

from athena_mcp.campaign_v3_life_attempt_identity import (
    ATTEMPT_REPLAY_EXTENSION,
    IDENTITY_POLICY,
    REQUIRED_REPLAY_BLOCKERS,
    SEMANTIC_BASE,
    bind_campaign_v3_life_attempt_identity,
    derive_attempt_id,
    validate_campaign_v3_life_attempt_identity,
)


class CampaignV3LifeOwnershipFirewallTests(unittest.TestCase):
    def _packet(self):
        return {
            "artifact": "ATHENA.CAMPAIGN.V3.LIFE.QUEST.PACKET.V1",
            "packet_digest": "a" * 64,
        }

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_same_execution_event_is_stable_across_delivery_retries(self, _validate):
        packet = self._packet()
        first = bind_campaign_v3_life_attempt_identity(
            packet=packet,
            execution_event_id="HOST-EVENT-42",
            delivery_id="DELIVERY-A",
        )
        second = bind_campaign_v3_life_attempt_identity(
            packet=packet,
            execution_event_id="HOST-EVENT-42",
            delivery_id="DELIVERY-B",
        )
        self.assertEqual("BOUND_ATTEMPT_IDENTITY", first["status"])
        self.assertEqual(first["attempt_id"], second["attempt_id"])
        self.assertNotEqual(first["envelope_digest"], second["envelope_digest"])
        self.assertEqual([], validate_campaign_v3_life_attempt_identity(first))
        self.assertEqual([], validate_campaign_v3_life_attempt_identity(second))
        self.assertEqual("INTEGRATION_HOLD", first["attempt_replay_extension"]["status"])
        self.assertFalse(first["attempt_replay_extension"]["semantic_replay_compatibility"])

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_new_host_execution_event_changes_attempt_identity(self, _validate):
        packet = self._packet()
        a = bind_campaign_v3_life_attempt_identity(
            packet=packet,
            execution_event_id="HOST-EVENT-1",
        )
        b = bind_campaign_v3_life_attempt_identity(
            packet=packet,
            execution_event_id="HOST-EVENT-2",
        )
        self.assertNotEqual(a["attempt_id"], b["attempt_id"])
        self.assertEqual(
            a["attempt_id"],
            derive_attempt_id(
                packet_digest=packet["packet_digest"],
                execution_event_id="HOST-EVENT-1",
            ),
        )

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=["packet_digest"],
    )
    def test_invalid_quest_packet_holds_before_attempt_identity(self, _validate):
        out = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="HOST-EVENT-1",
        )
        self.assertEqual("HOLD_INVALID_LIFE_QUEST_PACKET", out["status"])
        self.assertIsNone(out["attempt_id"])
        self.assertFalse(out["execution_authority"])
        self.assertFalse(out["platform_counter_reset_claimed"])

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_empty_host_execution_event_holds(self, _validate):
        out = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="   ",
        )
        self.assertEqual("HOLD_EXECUTION_EVENT_ID_REQUIRED", out["status"])
        self.assertIsNone(out["attempt_id"])

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_tampered_attempt_identity_or_authority_bit_fails_validation(self, _validate):
        envelope = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="HOST-EVENT-1",
        )
        tampered = copy.deepcopy(envelope)
        tampered["attempt_id"] = "LIFE-ATTEMPT-TAMPERED"
        self.assertIn("attempt_id", validate_campaign_v3_life_attempt_identity(tampered))

        tampered = copy.deepcopy(envelope)
        tampered["execution_authority"] = True
        errors = validate_campaign_v3_life_attempt_identity(tampered)
        self.assertIn("execution_authority_must_be_false", errors)
        self.assertIn("envelope_digest", errors)

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_semantic_replay_hold_cannot_be_rewritten_as_pass(self, _validate):
        envelope = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="HOST-EVENT-REPLAY-HOLD",
        )
        tampered = copy.deepcopy(envelope)
        tampered["attempt_replay_extension"]["status"] = "PASS"
        tampered["attempt_replay_extension"]["semantic_replay_compatibility"] = True
        tampered["attempt_replay_extension"]["blockers"] = []
        errors = validate_campaign_v3_life_attempt_identity(tampered)
        self.assertIn("semantic_replay_compatibility_hold", errors)
        self.assertIn("semantic_replay_compatibility_must_be_false", errors)
        self.assertIn("semantic_replay_blockers", errors)

    def test_semantic_source_and_live_replay_hold_are_explicit(self):
        self.assertEqual(
            "60a7bc798412088977d7ab9adf16a0e7dca3a1c9",
            SEMANTIC_BASE["commit"],
        )
        self.assertEqual("MERGED_HARDENED_LIFE_LOOP_BASE", SEMANTIC_BASE["standing"])
        self.assertEqual(16, int(SEMANTIC_BASE["exact_source_local_tests"].split("/")[0]))
        self.assertEqual(291, ATTEMPT_REPLAY_EXTENSION["pull_request"])
        self.assertEqual("f0d2efb9a0bdc999ae7aef93041cf8e69f4eb51e", ATTEMPT_REPLAY_EXTENSION["observed_head"])
        self.assertEqual(
            "9aeddf08bf3d73e35ba0a67107e4c420e83aa416",
            ATTEMPT_REPLAY_EXTENSION["observed_against_athena_main"],
        )
        self.assertEqual("INTEGRATION_HOLD", ATTEMPT_REPLAY_EXTENSION["status"])
        self.assertEqual(
            "SEMANTIC_REPLAY_COMPATIBILITY_NOT_ESTABLISHED",
            ATTEMPT_REPLAY_EXTENSION["standing"],
        )
        self.assertFalse(ATTEMPT_REPLAY_EXTENSION["canonical_promotion"])
        self.assertFalse(ATTEMPT_REPLAY_EXTENSION["semantic_replay_compatibility"])
        self.assertTrue(REQUIRED_REPLAY_BLOCKERS.issubset(set(ATTEMPT_REPLAY_EXTENSION["blockers"])))
        self.assertTrue(IDENTITY_POLICY["stable_across_transport_retry"])
        self.assertFalse(IDENTITY_POLICY["delivery_id_participates_in_attempt_identity"])
        self.assertFalse(IDENTITY_POLICY["host_event_identity_is_canonical_semantic_execution_identity"])
        self.assertFalse(IDENTITY_POLICY["semantic_alias_replay_safety_established"])
        self.assertFalse(IDENTITY_POLICY["continuation_retry_settlement_established"])
        self.assertFalse(IDENTITY_POLICY["quest_dispatch_attempt_id_abi_established"])

    def test_runtime_package_does_not_own_a_second_life_state_machine(self):
        forbidden_paths = [
            ROOT / "athena_mcp" / "stay_in_game_life_loop.py",
            ROOT / "athena_mcp" / "stay_in_game_life_loop_protocol.py",
        ]
        for path in forbidden_paths:
            self.assertFalse(path.exists(), f"duplicate Life reducer/protocol forbidden: {path}")

        compiler_source = (
            ROOT / "athena_mcp" / "campaign_v3_life_binding.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "def new_world(",
            "def enter_agent(",
            "def resolve_attempt(",
            "StayInGameLifeLoopRuntime",
            "athena_life_world_new",
            "athena_life_agent_enter",
            "athena_life_resolve",
        ):
            self.assertNotIn(forbidden, compiler_source)

        aor_source = (
            ROOT / "athena_mcp" / "aor_collective_transport_surface.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "StayInGameLifeLoopRuntime",
            "athena_life_world_new",
            "athena_life_agent_enter",
            "athena_life_resolve",
        ):
            self.assertNotIn(forbidden, aor_source)


if __name__ == "__main__":
    unittest.main()
