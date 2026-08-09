from __future__ import annotations

import copy
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]

from athena_mcp.campaign_v3_life_attempt_identity import (
    ATTEMPT_REPLAY_EXTENSION,
    IDENTITY_POLICY,
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
    def test_stale_semantic_extension_metadata_fails_validation(self, _validate):
        envelope = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="HOST-EVENT-1",
        )
        stale = copy.deepcopy(envelope)
        stale["attempt_replay_extension"]["pull_request"] = 291
        errors = validate_campaign_v3_life_attempt_identity(stale)
        self.assertIn("semantic_replay_extension_stale_pr", errors)
        self.assertIn("envelope_digest", errors)

        promoted = copy.deepcopy(envelope)
        promoted["attempt_replay_extension"]["canonical_promotion"] = True
        errors = validate_campaign_v3_life_attempt_identity(promoted)
        self.assertIn("candidate_extension_promotion_firewall", errors)
        self.assertIn("envelope_digest", errors)

    @patch(
        "athena_mcp.campaign_v3_life_attempt_identity.validate_campaign_v3_life_quest_packet",
        return_value=[],
    )
    def test_runtime_cannot_claim_semantic_replay_ownership(self, _validate):
        envelope = bind_campaign_v3_life_attempt_identity(
            packet=self._packet(),
            execution_event_id="HOST-EVENT-1",
        )
        tampered = copy.deepcopy(envelope)
        tampered["identity_policy"]["semantic_replay_decision_owned_by_runtime"] = True
        errors = validate_campaign_v3_life_attempt_identity(tampered)
        self.assertIn("semantic_replay_ownership_firewall", errors)
        self.assertIn("envelope_digest", errors)

    def test_semantic_source_standing_is_explicit_and_candidate_extension_is_not_promoted(self):
        self.assertEqual(
            "60a7bc798412088977d7ab9adf16a0e7dca3a1c9",
            SEMANTIC_BASE["commit"],
        )
        self.assertEqual(16, int(SEMANTIC_BASE["exact_source_local_tests"].split("/")[0]))
        self.assertEqual("SEMANTIC_EXECUTION_REPLAY_V2", ATTEMPT_REPLAY_EXTENSION["kind"])
        self.assertEqual(315, ATTEMPT_REPLAY_EXTENSION["pull_request"])
        self.assertEqual(291, ATTEMPT_REPLAY_EXTENSION["supersedes_pull_request"])
        self.assertEqual(
            "97ebac3d47b607a43eb31fda372afbe10a0ddfdc",
            ATTEMPT_REPLAY_EXTENSION["branch_head_at_binding"],
        )
        self.assertEqual("46/46 PASS", ATTEMPT_REPLAY_EXTENSION["combined_exact_source_local_tests"])
        self.assertFalse(ATTEMPT_REPLAY_EXTENSION["canonical_promotion"])
        self.assertFalse(ATTEMPT_REPLAY_EXTENSION["github_actions_ci"])
        self.assertTrue(ATTEMPT_REPLAY_EXTENSION["semantic_base_commit_remains_canonical"])
        self.assertTrue(IDENTITY_POLICY["stable_across_transport_retry"])
        self.assertFalse(IDENTITY_POLICY["delivery_id_participates_in_attempt_identity"])
        self.assertTrue(IDENTITY_POLICY["execution_event_id_forwarded_unchanged_to_semantic_reducer"])
        self.assertTrue(IDENTITY_POLICY["attempt_id_is_settlement_identity"])
        self.assertFalse(IDENTITY_POLICY["semantic_replay_decision_owned_by_runtime"])

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
