from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_life_attempt_identity import bind_campaign_v3_life_attempt_identity
from athena_mcp.campaign_v3_life_binding import compile_campaign_v3_life_quest_packet
from athena_mcp.campaign_v3_life_dispatch_bridge import (
    DISPATCH_SCHEMA_VERSION,
    LIFE_POLICY,
    compute_pinned_dispatch_clear_condition_digest,
    translate_campaign_v3_life_dispatch_v1,
    validate_campaign_v3_life_dispatch_bridge,
    validate_pinned_dispatch_packet_shape,
    verify_campaign_v3_life_dispatch_bridge,
)
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor

CAMPAIGN_ID = "RHC-BRIDGE-1"
BRANCH_ID = "B-BRIDGE-1"
AGENT_ID = "ATHENA-CV3-BRIDGE-1"
QUEST_ID = "Q-BRIDGE"
QUEST_VERSION = "1"
DEFINITIONS = ["verification gate passes", "durable return exists"]
OBSERVATIONS = [
    {"id": "C-VERIFY", "definition": "verification gate passes", "satisfied": True},
    {"id": "C-RETURN", "definition": "durable return exists", "satisfied": False},
]


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
        loop_id="LOOP-BRIDGE-1",
        loop_state_digest="loop-state",
        anchor_id="RA-BRIDGE-1",
        run_id="RUN-BRIDGE-1",
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
        witnesses=["readback:campaign-v3-life-dispatch-bridge"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:life-dispatch",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": QUEST_ID, "version": QUEST_VERSION}],
    )


def _packet(*, reward_candidate=None):
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
        extra_life_reward_candidate=reward_candidate,
    )


def _translate(**overrides):
    kwargs = {
        "campaign_packet": _packet(),
        "agent_id": AGENT_ID,
        "condition_observations": copy.deepcopy(OBSERVATIONS),
        "condition_identity_ref": "quest-contract://Q-BRIDGE@1",
        "result_class": "FAIL_CLEAR",
        "executed": True,
        "hard_gate_status": "FAIL",
        "witnesses": ["execution://event-1"],
        "current_git_positions": _positions(),
    }
    kwargs.update(overrides)
    return translate_campaign_v3_life_dispatch_v1(**kwargs)


class CampaignV3LifeDispatchBridgeTests(unittest.TestCase):
    def test_pinned_digest_matches_canonical_known_vector(self):
        self.assertEqual(
            "sha256:c61a52733dc74074d56fe7c25d5550f47b222085bddc417b9e0eecbf7c57794d",
            compute_pinned_dispatch_clear_condition_digest(
                QUEST_ID, QUEST_VERSION, copy.deepcopy(OBSERVATIONS)
            ),
        )

    def test_translates_to_canonical_dispatch_shape_without_authority(self):
        out = _translate()
        self.assertEqual("TRANSLATED", out["status"])
        self.assertEqual([], validate_campaign_v3_life_dispatch_bridge(out))
        self.assertEqual("PASS", verify_campaign_v3_life_dispatch_bridge(out)["status"])
        dispatch = out["dispatch_packet"]
        self.assertEqual(DISPATCH_SCHEMA_VERSION, dispatch["dispatch_schema_version"])
        self.assertEqual(LIFE_POLICY, dispatch["life_policy"])
        self.assertEqual([], validate_pinned_dispatch_packet_shape(dispatch))
        self.assertFalse(out["execution_authority"])
        self.assertFalse(out["life_consumption_authority"])
        self.assertFalse(out["reward_issuance_authority"])
        self.assertFalse(out["platform_counter_reset_claimed"])

    def test_campaign_digest_is_not_silently_reused_as_canonical_digest(self):
        out = _translate()
        self.assertNotEqual(out["campaign_clear_condition_digest"], out["canonical_clear_condition_digest"])
        self.assertTrue(out["canonical_clear_condition_digest"].startswith("sha256:"))
        self.assertEqual(out["canonical_clear_condition_digest"], out["dispatch_packet"]["clear_condition_digest"])

    def test_condition_observation_order_does_not_change_output(self):
        first = _translate()
        second = _translate(condition_observations=list(reversed(OBSERVATIONS)))
        self.assertEqual(first["canonical_clear_condition_digest"], second["canonical_clear_condition_digest"])
        self.assertEqual(first["dispatch_packet"]["frozen_clear_conditions"], second["dispatch_packet"]["frozen_clear_conditions"])

    def test_definition_substitution_or_duplicate_ids_holds(self):
        changed = copy.deepcopy(OBSERVATIONS)
        changed[0]["definition"] = "invented criterion"
        out = _translate(condition_observations=changed)
        self.assertEqual("HOLD_DISPATCH_TRANSLATION", out["status"])
        self.assertTrue(any("CONDITION_OBSERVATIONS_INVALID" in item for item in out["failures"]))
        duplicate = copy.deepcopy(OBSERVATIONS)
        duplicate[1]["id"] = duplicate[0]["id"]
        out = _translate(condition_observations=duplicate)
        self.assertEqual("HOLD_DISPATCH_TRANSLATION", out["status"])
        self.assertTrue(any("duplicate condition observation id" in item for item in out["failures"]))

    def test_condition_identity_ref_and_agent_binding_are_required(self):
        no_ref = _translate(condition_identity_ref="")
        self.assertIn("CONDITION_IDENTITY_REF_REQUIRED", no_ref["failures"])
        wrong = _translate(agent_id="ANOTHER-AGENT")
        self.assertIn("AGENT_ID_CAMPAIGN_COORDINATE_MISMATCH", wrong["failures"])

    def test_reseed_anchor_is_forwarded_by_value_and_digest_stays_sibling_metadata(self):
        packet = _packet()
        self.assertIn("RESEED_ANCHOR_DIGEST", packet)
        self.assertNotIn("anchor_digest", packet["RESEED_ANCHOR"])
        out = _translate(campaign_packet=packet)
        self.assertEqual("TRANSLATED", out["status"])
        self.assertEqual(packet["RESEED_ANCHOR"], out["dispatch_packet"]["reseed_anchor"])
        self.assertEqual(packet["RESEED_ANCHOR_DIGEST"], out["campaign_reseed_anchor_digest"])
        self.assertNotIn("RESEED_ANCHOR_DIGEST", out["dispatch_packet"])

    def test_current_git_positions_are_forwarded_not_prejudged(self):
        changed = _positions()
        changed[0]["head"] = "new-head"
        out = _translate(current_git_positions=changed)
        self.assertEqual("TRANSLATED", out["status"])
        positions = {f"{row['repo']}::{row['ref']}": row for row in out["dispatch_packet"]["current_git_positions"]}
        self.assertEqual("new-head", positions["demeet2k/athena-mcp-server::refs/heads/master"]["head"])

    def test_reward_is_forwarded_only_when_campaign_eligibility_is_true(self):
        candidate = {
            "requested": True,
            "candidate_id": "REWARD-CANDIDATE-1",
            "evidence_refs": ["evidence://clear-1"],
        }
        packet = _packet(reward_candidate=candidate)
        reward = {
            "receipt_id": "REWARD-1",
            "delta": 1,
            "verified": True,
            "self_scored": False,
            "witnesses": ["verifier://1"],
        }
        all_clear = [{**row, "satisfied": True} for row in OBSERVATIONS]
        out = _translate(
            campaign_packet=packet,
            result_class="CLEAR",
            hard_gate_status="PASS",
            condition_observations=all_clear,
            extra_life_reward=reward,
        )
        self.assertTrue(out["dispatch_packet"]["extra_life_reward_eligibility"])
        self.assertEqual(reward, out["dispatch_packet"]["extra_life_reward"])
        held = _translate(
            result_class="CLEAR",
            hard_gate_status="PASS",
            condition_observations=all_clear,
            extra_life_reward=reward,
        )
        self.assertIn("EXTRA_LIFE_REWARD_NOT_ELIGIBLE", held["failures"])

    def test_attempt_identity_is_preserved_out_of_band_not_injected_into_v1(self):
        packet = _packet()
        identity = bind_campaign_v3_life_attempt_identity(
            packet=packet, execution_event_id="host-event-1", delivery_id="delivery-A"
        )
        out = _translate(campaign_packet=packet, attempt_identity_envelope=identity)
        self.assertEqual("PRESERVED_OUT_OF_BAND", out["attempt_compatibility"]["status"])
        self.assertFalse(out["attempt_compatibility"]["supported_by_pinned_dispatch"])
        self.assertNotIn("attempt_id", out["dispatch_packet"])

    def test_attempt_identity_must_bind_same_campaign_packet(self):
        first = _packet()
        second = compile_campaign_v3_life_quest_packet(
            pulse=_pulse(), residual_step=3, campaign_id=CAMPAIGN_ID,
            branch_id=BRANCH_ID, agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID, quest_version=QUEST_VERSION,
            clear_conditions=[*DEFINITIONS, "another criterion"],
            reseed_anchor=_anchor(), extra_life_reward_candidate=None,
        )
        identity = bind_campaign_v3_life_attempt_identity(packet=first, execution_event_id="host-event-1")
        out = _translate(
            campaign_packet=second,
            condition_observations=[
                *copy.deepcopy(OBSERVATIONS),
                {"id": "C-EXTRA", "definition": "another criterion", "satisfied": True},
            ],
            attempt_identity_envelope=identity,
        )
        self.assertTrue(any("packet_digest mismatch" in item for item in out["failures"]))

    def test_source_pin_and_uncertainty_are_explicit(self):
        out = _translate()
        source = out["semantic_dispatch_source"]
        self.assertEqual("9aeddf08bf3d73e35ba0a67107e4c420e83aa416", source["commit"])
        self.assertEqual("08624386100fd56178dc99ee2ede27009427cca7", source["script_blob"])
        self.assertEqual("5f9435dea0cb1e74bdf0143714417a33a8fa502a", source["schema_blob"])
        self.assertEqual("UNKNOWN", source["performance_effect"])
        self.assertIn("UNVERIFIED_EXTERNAL_CONTRACT_COORDINATE", out["condition_identity_standing"])

    def test_bridge_tamper_is_detected(self):
        out = _translate()
        tampered = copy.deepcopy(out)
        tampered["dispatch_packet"]["clear_condition_digest"] = "sha256:" + ("0" * 64)
        errors = validate_campaign_v3_life_dispatch_bridge(tampered)
        self.assertIn("dispatch_packet:clear_condition_digest", errors)
        self.assertIn("bridge_digest", errors)

    def test_platform_reset_cannot_enter_translated_packet(self):
        out = _translate()
        self.assertFalse(out["dispatch_packet"]["platform_counter_reset_claimed"])
        self.assertFalse(out["platform_counter_reset_claimed"])


if __name__ == "__main__":
    unittest.main()
