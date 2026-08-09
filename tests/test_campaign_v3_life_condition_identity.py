from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_life_binding import compile_campaign_v3_life_quest_packet
from athena_mcp.campaign_v3_life_condition_identity import (
    freeze_campaign_v3_life_condition_identity,
    translate_campaign_v3_life_dispatch_with_frozen_identity_v1,
    validate_campaign_v3_life_condition_identity,
    verify_campaign_v3_life_condition_identity_against_packet,
)
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor

CAMPAIGN_ID = "RHC-ID-1"
BRANCH_ID = "B-ID-1"
AGENT_ID = "ATHENA-CV3-ID-1"
QUEST_ID = "Q-ID"
QUEST_VERSION = "1"
DEFINITIONS = ["verification gate passes", "durable return exists"]
IDS = ["C-VERIFY", "C-RETURN"]


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse():
    actions = []
    for step, horizon, state in (
        (1, "I", "SATISFIED"), (2, "I", "SATISFIED"), (3, "I", "RESIDUAL"),
        (4, "I", "RESIDUAL"), (5, "M", "RESIDUAL"), (6, "M", "RESIDUAL"),
        (7, "M", "RESIDUAL"), (8, "L", "RESIDUAL"), (9, "L", "RESIDUAL"),
        (10, "L", "RESIDUAL"),
    ):
        actions.append({
            "step": step,
            "horizon": horizon,
            "text": f"historical action {step}",
            "current_state": state,
            "history_preserved": True,
        })
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger-digest",
        "source_issue": 177,
        "verification_issue": 185,
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "historical_horizon_coverage": {"I": 4, "M": 3, "L": 3},
        "current_status_counts": {},
        "actions": actions,
        "residual_steps": [row["step"] for row in actions if row["current_state"] == "RESIDUAL"],
        "hold_steps": [],
        "current_coordinates": {"git_head": "runtime-head", "shared_fresh": True},
        "operational_basis_status": "PASS",
        "operational_basis_digest": "basis-digest",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": ["PULSE_100_RESEED_REQUIRED"],
    }
    value["pulse_digest"] = _sha(value)
    return value


def _positions():
    return [
        {"repo": "demeet2k/athena-mcp-server", "ref": "refs/heads/master", "head": "runtime-head", "tree": "runtime-tree"},
        {"repo": "demeet2k/Athena", "ref": "refs/heads/main", "head": "athena-head", "tree": "athena-tree"},
    ]


def _anchor():
    pulse = _pulse()
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=CAMPAIGN_ID,
        campaign_state_digest="campaign-state",
        campaign_checkpoint_head="campaign-head",
        loop_id="LOOP-ID-1",
        loop_state_digest="loop-state",
        anchor_id="RA-ID-1",
        run_id="RUN-ID-1",
        agent_coordinate_name=AGENT_ID,
        reseed_epoch=1,
        pulse_age_before=10,
        git_positions=_positions(),
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="runtime-old",
        prompt_digest="prompt-digest",
        issue_pressure_digest="issue-149",
        durable_returns=["runtime:issue:149"],
        witnesses=["readback:condition-identity"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:identity-aware-dispatch",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": QUEST_ID, "version": QUEST_VERSION}],
    )


def _packet():
    return compile_campaign_v3_life_quest_packet(
        pulse=_pulse(),
        residual_step=3,
        campaign_id=CAMPAIGN_ID,
        branch_id=BRANCH_ID,
        agent_coordinate_name=AGENT_ID,
        quest_id=QUEST_ID,
        quest_version=QUEST_VERSION,
        clear_conditions=DEFINITIONS,
        reseed_anchor=_anchor(),
        extra_life_reward_candidate=None,
    )


def _identity(packet=None):
    return freeze_campaign_v3_life_condition_identity(
        campaign_packet=packet or _packet(),
        criterion_ids=IDS,
        identity_ref="quest-contract://Q-ID@1",
    )


def _observations():
    return [
        {"id": "C-VERIFY", "definition": "verification gate passes", "satisfied": True},
        {"id": "C-RETURN", "definition": "durable return exists", "satisfied": False},
    ]


class CampaignV3LifeConditionIdentityTests(unittest.TestCase):
    def test_freeze_binds_ids_to_unplayed_packet_digest(self):
        packet = _packet()
        identity = _identity(packet)
        self.assertEqual("FROZEN_PREPLAY_PACKET_BOUND", identity["status"])
        self.assertEqual(packet["packet_digest"], identity["packet_digest"])
        self.assertEqual([], validate_campaign_v3_life_condition_identity(identity))
        self.assertFalse(identity["outcomes_observed"])
        self.assertFalse(identity["temporal_creation_proof"])
        self.assertFalse(identity["execution_authority"])
        self.assertFalse(identity["platform_counter_reset_claimed"])

    def test_freeze_is_deterministic(self):
        packet = _packet()
        first = _identity(packet)
        second = _identity(copy.deepcopy(packet))
        self.assertEqual(first["condition_identity_digest"], second["condition_identity_digest"])
        self.assertEqual(first["envelope_digest"], second["envelope_digest"])

    def test_id_count_duplicate_and_empty_ref_fail_closed(self):
        packet = _packet()
        with self.assertRaises(ValueError):
            freeze_campaign_v3_life_condition_identity(
                campaign_packet=packet, criterion_ids=["ONLY-ONE"], identity_ref="ref://x"
            )
        with self.assertRaises(ValueError):
            freeze_campaign_v3_life_condition_identity(
                campaign_packet=packet, criterion_ids=["DUP", "DUP"], identity_ref="ref://x"
            )
        with self.assertRaises(ValueError):
            freeze_campaign_v3_life_condition_identity(
                campaign_packet=packet, criterion_ids=IDS, identity_ref=""
            )

    def test_identity_tamper_is_detected(self):
        identity = _identity()
        tampered = copy.deepcopy(identity)
        tampered["conditions"][0]["definition"] = "changed"
        errors = validate_campaign_v3_life_condition_identity(tampered)
        self.assertIn("condition_identity_digest", errors)
        self.assertIn("envelope_digest", errors)

    def test_identity_must_bind_exact_campaign_packet(self):
        first = _packet()
        identity = _identity(first)
        second = compile_campaign_v3_life_quest_packet(
            pulse=_pulse(), residual_step=3, campaign_id=CAMPAIGN_ID,
            branch_id=BRANCH_ID, agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID, quest_version=QUEST_VERSION,
            clear_conditions=[*DEFINITIONS, "another criterion"],
            reseed_anchor=_anchor(), extra_life_reward_candidate=None,
        )
        check = verify_campaign_v3_life_condition_identity_against_packet(identity, second)
        self.assertEqual("HOLD", check["status"])
        self.assertIn("packet_digest_binding", check["errors"])
        self.assertIn("condition_definition_binding", check["errors"])

    def test_identity_aware_dispatch_uses_frozen_ids(self):
        packet = _packet()
        identity = _identity(packet)
        out = translate_campaign_v3_life_dispatch_with_frozen_identity_v1(
            campaign_packet=packet,
            condition_identity=identity,
            agent_id=AGENT_ID,
            condition_observations=_observations(),
            result_class="FAIL_CLEAR",
            executed=True,
            hard_gate_status="FAIL",
            witnesses=["execution://event-1"],
            current_git_positions=_positions(),
        )
        self.assertEqual("TRANSLATED_WITH_FROZEN_IDENTITY", out["status"])
        self.assertEqual(identity["condition_identity_digest"], out["condition_identity_digest"])
        self.assertIn("FROZEN_AGAINST_UNPLAYED_COMPILER_PACKET_DIGEST", out["condition_identity_standing"])
        dispatch = out["dispatch_translation"]["dispatch_packet"]
        self.assertEqual({"C-VERIFY", "C-RETURN"}, {row["id"] for row in dispatch["frozen_clear_conditions"]})
        self.assertFalse(out["execution_authority"])

    def test_observation_id_or_definition_substitution_holds_before_translation(self):
        packet = _packet()
        identity = _identity(packet)
        changed_id = _observations()
        changed_id[0]["id"] = "C-OTHER"
        out = translate_campaign_v3_life_dispatch_with_frozen_identity_v1(
            campaign_packet=packet, condition_identity=identity, agent_id=AGENT_ID,
            condition_observations=changed_id, result_class="FAIL_CLEAR", executed=True,
            hard_gate_status="FAIL", witnesses=["execution://event-1"],
            current_git_positions=_positions(),
        )
        self.assertEqual("HOLD_CONDITION_IDENTITY", out["status"])
        self.assertIn("observation_identity_mismatch", out["observation_errors"])

        changed_definition = _observations()
        changed_definition[0]["definition"] = "changed definition"
        out = translate_campaign_v3_life_dispatch_with_frozen_identity_v1(
            campaign_packet=packet, condition_identity=identity, agent_id=AGENT_ID,
            condition_observations=changed_definition, result_class="FAIL_CLEAR", executed=True,
            hard_gate_status="FAIL", witnesses=["execution://event-1"],
            current_git_positions=_positions(),
        )
        self.assertEqual("HOLD_CONDITION_IDENTITY", out["status"])

    def test_identity_envelope_contains_no_outcome_or_reward_settlement_payload(self):
        identity = _identity()
        serialized = json.dumps(identity, sort_keys=True)
        self.assertNotIn("satisfied", serialized)
        self.assertNotIn("extra_life_reward", identity)
        self.assertNotIn("reward_receipt", serialized.casefold())
        self.assertFalse(identity["reward_issuance_authority"])
        self.assertFalse(identity["outcomes_observed"])

    def test_identity_ref_is_frozen_but_not_claimed_as_authority(self):
        identity = _identity()
        self.assertEqual("quest-contract://Q-ID@1", identity["identity_ref"])
        self.assertIn("CALLER_DECLARED_IDENTITY_REF", identity["standing"])
        self.assertIn("CREATION_TIME_IS_NOT_INDEPENDENTLY_PROVEN", identity["standing"])

    def test_identity_aware_wrapper_preserves_translation_hold(self):
        packet = _packet()
        identity = _identity(packet)
        out = translate_campaign_v3_life_dispatch_with_frozen_identity_v1(
            campaign_packet=packet,
            condition_identity=identity,
            agent_id=AGENT_ID,
            condition_observations=_observations(),
            result_class="FAIL_CLEAR",
            executed=False,
            hard_gate_status="FAIL",
            witnesses=["execution://event-1"],
            current_git_positions=_positions(),
        )
        self.assertEqual("HOLD_TRANSLATION", out["status"])
        self.assertEqual("HOLD_DISPATCH_TRANSLATION", out["dispatch_translation"]["status"])


if __name__ == "__main__":
    unittest.main()
