from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_life_binding import (
    ARTIFACT,
    LIFE_LOOP_SCHEMA_BLOB,
    LIFE_LOOP_SCRIPT_BLOB,
    LIFE_LOOP_SOURCE_COMMIT,
    LIFE_LOOP_REPAIR_HEAD,
    LIFE_LOOP_TEST_BLOB,
    compile_campaign_v3_life_quest_packet,
    validate_campaign_v3_life_quest_packet,
    verify_campaign_v3_life_quest_packet,
)
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor


CAMPAIGN_ID = "RHC-LIFE-1"
BRANCH_ID = "B-LIFE-1"
AGENT_ID = "ATHENA-CV3-LIFE-1"
QUEST_ID = "QUEST-LIFE-001"
QUEST_VERSION = "1"


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse():
    actions = []
    for step, horizon, state in (
        (1, "I", "SATISFIED"),
        (2, "I", "SUPERSEDED"),
        (3, "I", "RESIDUAL"),
        (4, "I", "RESIDUAL"),
        (5, "M", "RESIDUAL"),
        (6, "M", "RESIDUAL"),
        (7, "M", "RESIDUAL"),
        (8, "L", "RESIDUAL"),
        (9, "L", "RESIDUAL"),
        (10, "L", "RESIDUAL"),
    ):
        actions.append(
            {
                "step": step,
                "horizon": horizon,
                "text": f"historical action {step}",
                "current_state": state,
                "history_preserved": True,
            }
        )
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
        {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": "runtime-head",
            "tree": "runtime-tree",
        },
        {
            "repo": "demeet2k/Athena",
            "ref": "refs/heads/main",
            "head": "athena-head",
            "tree": "athena-tree",
        },
    ]


def _anchor(*, pulse=None, agent=AGENT_ID, quest_id=QUEST_ID, quest_version=QUEST_VERSION):
    pulse = pulse or _pulse()
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=CAMPAIGN_ID,
        campaign_state_digest="campaign-state",
        campaign_checkpoint_head="campaign-head",
        loop_id="LOOP-LIFE-1",
        loop_state_digest="loop-state",
        anchor_id="RA-LIFE-PACKET-1",
        run_id="RUN-LIFE-PACKET-1",
        agent_coordinate_name=agent,
        reseed_epoch=1,
        pulse_age_before=10,
        git_positions=_positions(),
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="runtime-old",
        prompt_digest="prompt-digest",
        issue_pressure_digest="issue-149",
        durable_returns=["runtime:issue:149", "semantic:pr:284"],
        witnesses=["readback:campaign-v3-life-packet"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:life-quest:execute",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": quest_id, "version": quest_version}],
    )


def _packet(**overrides):
    pulse = overrides.pop("pulse", _pulse())
    kwargs = {
        "pulse": pulse,
        "residual_step": 3,
        "campaign_id": CAMPAIGN_ID,
        "branch_id": BRANCH_ID,
        "agent_coordinate_name": AGENT_ID,
        "quest_id": QUEST_ID,
        "quest_version": QUEST_VERSION,
        "clear_conditions": [
            "all required repository tests pass",
            "packet readback matches committed source",
            "no authority or platform-reset firewall regresses",
        ],
        "reseed_anchor": _anchor(pulse=pulse),
        "extra_life_reward_candidate": None,
    }
    kwargs.update(overrides)
    return compile_campaign_v3_life_quest_packet(**kwargs)


class CampaignV3LifeBindingTests(unittest.TestCase):
    def test_compiles_deterministic_non_authoritative_packet(self):
        first = _packet()
        second = _packet()
        self.assertEqual("COMPILED", first["status"])
        self.assertEqual(ARTIFACT, first["artifact"])
        self.assertEqual(first["packet_digest"], second["packet_digest"])
        self.assertEqual([], validate_campaign_v3_life_quest_packet(first))
        self.assertEqual("PASS", verify_campaign_v3_life_quest_packet(first)["status"])
        self.assertFalse(first["execution_authority"])
        self.assertFalse(first["scheduler_ready"])
        self.assertFalse(first["provider_authority"])
        self.assertFalse(first["campaign_success_claim_allowed"])
        self.assertFalse(first["platform_counter_reset_claimed"])
        self.assertFalse(first["life_loop_canonical_promotion"])
        self.assertFalse(first["reseed_anchor_consumption_authority"])
        self.assertFalse(first["life_consumption_authority"])
        self.assertIsNone(first["CLEAR_RESULT_VECTOR"])

    def test_clear_contract_mutation_changes_digest_and_booleans_are_not_contract_definitions(self):
        first = _packet()
        second = _packet(
            clear_conditions=[
                "all required repository tests pass",
                "packet readback matches committed source",
                "additional independent witness passes",
            ]
        )
        self.assertNotEqual(first["CLEAR_CONDITION_DIGEST"], second["CLEAR_CONDITION_DIGEST"])
        self.assertNotEqual(first["packet_digest"], second["packet_digest"])
        invalid = _packet(clear_conditions=[True, False])
        self.assertEqual("HOLD_INVALID_PACKET_INPUT", invalid["status"])
        self.assertTrue(any("CLEAR_CONDITIONS_INVALID" in item for item in invalid["failures"]))

    def test_life_policy_pins_merged_hardened_semantic_source_with_evidence_ceiling(self):
        packet = _packet()
        source = packet["LIFE_POLICY"]["source"]
        self.assertEqual("60a7bc798412088977d7ab9adf16a0e7dca3a1c9", LIFE_LOOP_SOURCE_COMMIT)
        self.assertEqual("18ffcbc21601d71811ae2d81069dbf8e21a82b5b", LIFE_LOOP_REPAIR_HEAD)
        self.assertEqual("c6f35cf39d9f25333ee0c748b5e4bacedbb544a1", LIFE_LOOP_SCRIPT_BLOB)
        self.assertEqual("93212c61e341ec474332c4daa36e776f735d2491", LIFE_LOOP_SCHEMA_BLOB)
        self.assertEqual("a6ce3ac0bd94eee62764b2daa22ae0679fdc32d5", LIFE_LOOP_TEST_BLOB)
        self.assertEqual("CANDIDATE_HARDENED_EXACT_SOURCE_TESTED", source["standing"])
        self.assertEqual("16/16 PASS", source["exact_source_local_tests"])
        self.assertFalse(source["github_actions_ci"])
        self.assertFalse(source["independent_witness"])
        self.assertFalse(source["canonical_promotion"])

    def test_anchor_must_bind_pulse_campaign_quest_and_agent(self):
        pulse = _pulse()

        wrong_quest = _anchor(pulse=pulse, quest_id="OTHER-QUEST", quest_version="9")
        out = _packet(pulse=pulse, reseed_anchor=wrong_quest)
        self.assertEqual("HOLD_INVALID_RESEED_ANCHOR", out["status"])
        self.assertIn("RESEED_ANCHOR_QUEST_BINDING_MISMATCH", out["failures"])

        wrong_agent = _anchor(pulse=pulse, agent="OTHER-AGENT")
        out = _packet(pulse=pulse, reseed_anchor=wrong_agent)
        self.assertEqual("HOLD_INVALID_RESEED_ANCHOR", out["status"])
        self.assertIn("RESEED_ANCHOR_AGENT_BINDING_MISMATCH", out["failures"])

        wrong_campaign = _anchor(pulse=pulse)
        for row in wrong_campaign["target_versions"]:
            if row["id"] == "campaign_v3.campaign_id":
                row["version"] = "OTHER-CAMPAIGN"
        out = _packet(pulse=pulse, reseed_anchor=wrong_campaign)
        self.assertEqual("HOLD_INVALID_RESEED_ANCHOR", out["status"])
        self.assertIn("RESEED_ANCHOR_CAMPAIGN_BINDING_MISMATCH", out["failures"])

    def test_tampered_or_platform_reset_anchor_holds(self):
        anchor = _anchor()
        anchor["platform_counter_reset_claimed"] = True
        out = _packet(reseed_anchor=anchor)
        self.assertEqual("HOLD_INVALID_RESEED_ANCHOR", out["status"])
        self.assertFalse(out["platform_counter_reset_claimed"])
        self.assertTrue(any("platform_counter_reset_claimed" in item for item in out["failures"]))

    def test_reward_eligibility_is_only_pre_clear_candidate_signal(self):
        packet = _packet(
            extra_life_reward_candidate={
                "requested": True,
                "candidate_id": "EXTRA-LIFE-CANDIDATE-1",
                "evidence_refs": ["quest:planned-witness:1"],
            }
        )
        eligibility = packet["EXTRA_LIFE_REWARD_ELIGIBILITY"]
        self.assertTrue(eligibility["eligible"])
        self.assertEqual("PRE_CLEAR_CANDIDATE_SIGNAL_ONLY", eligibility["eligibility_scope"])
        self.assertFalse(eligibility["issuance_eligible"])
        self.assertFalse(eligibility["reward_issued"])
        self.assertFalse(eligibility["self_scored_allowed"])

    def test_reward_candidate_cannot_smuggle_authority_or_issuance_claim(self):
        out = _packet(
            extra_life_reward_candidate={
                "requested": True,
                "candidate_id": "X",
                "evidence_refs": ["ref:1"],
                "reward_issued": True,
            }
        )
        self.assertEqual("HOLD_INVALID_PACKET_INPUT", out["status"])
        self.assertTrue(any("EXTRA_LIFE_CANDIDATE_INVALID" in item for item in out["failures"]))
        self.assertFalse(out["EXTRA_LIFE_REWARD_ELIGIBILITY"]["reward_issued"])

    def test_packet_tampering_fails_even_if_payload_looks_plausible(self):
        packet = _packet()
        packet["CLEAR_CONDITIONS"][0] = "different condition"
        errors = validate_campaign_v3_life_quest_packet(packet)
        self.assertIn("clear_condition_digest", errors)
        self.assertIn("packet_digest", errors)

    def test_observed_results_cannot_be_preloaded_into_compiled_packet(self):
        packet = _packet()
        packet["CLEAR_RESULT_VECTOR"] = [True, True, True]
        errors = validate_campaign_v3_life_quest_packet(packet)
        self.assertIn("clear_result_vector_must_be_unobserved", errors)

    def test_pulse_tamper_or_nonresidual_step_holds(self):
        pulse = _pulse()
        pulse["actions"][0]["text"] = "tampered"
        out = _packet(pulse=pulse, reseed_anchor=_anchor())
        self.assertIn(out["status"], {"HOLD_INVALID_PACKET_INPUT", "HOLD_INVALID_RESEED_ANCHOR"})
        self.assertIn("PULSE_DIGEST_INVALID", out["failures"])

        out = _packet(residual_step=1)
        self.assertEqual("HOLD_INVALID_PACKET_INPUT", out["status"])
        self.assertIn("STEP_NOT_RESIDUAL", out["failures"])

    def test_reseed_anchor_is_embedded_by_value_and_digest_protected(self):
        packet = _packet()
        anchor_digest = packet["RESEED_ANCHOR"]["anchor_digest"]
        self.assertEqual(64, len(anchor_digest))
        packet["RESEED_ANCHOR"]["anchor_id"] = "TAMPERED"
        errors = validate_campaign_v3_life_quest_packet(packet)
        self.assertIn("reseed_anchor_digest", errors)
        self.assertIn("packet_digest", errors)

    def test_validator_rejects_recomputed_digest_after_semantic_firewall_tamper(self):
        packet = _packet()
        packet["execution_authority"] = True
        packet["packet_digest"] = _sha({k: v for k, v in packet.items() if k != "packet_digest"})
        errors = validate_campaign_v3_life_quest_packet(packet)
        self.assertIn("execution_authority_must_be_false", errors)

    def test_hold_does_not_claim_execution_reward_life_or_platform_reset(self):
        out = _packet(clear_conditions=[])
        self.assertEqual("HOLD_INVALID_PACKET_INPUT", out["status"])
        self.assertFalse(out["execution_authority"])
        self.assertFalse(out["scheduler_ready"])
        self.assertFalse(out["provider_authority"])
        self.assertFalse(out["platform_counter_reset_claimed"])
        self.assertFalse(out["work_executed"])


if __name__ == "__main__":
    unittest.main()
