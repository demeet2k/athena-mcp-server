from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_binding import ARTIFACT as BINDING_ARTIFACT
from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_life_binding import compile_campaign_v3_life_quest_packet
from athena_mcp.campaign_v3_life_bound_identity import (
    ARTIFACT,
    align_campaign_v3_bound_life_packet,
    validate_campaign_v3_life_bound_identity,
    verify_campaign_v3_life_bound_identity,
)
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor


AGENT_ID = "ATHENA-BOUND-LIFE-1"
QUEST_ID = "QUEST-BOUND-LIFE-001"
QUEST_VERSION = "1"


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse(*, tag: str = "A") -> dict:
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
        "ledger_digest": f"ledger-{tag}",
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


def _anchor(*, pulse: dict, campaign_id: str):
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=campaign_id,
        campaign_state_digest="campaign-state",
        campaign_checkpoint_head="campaign-head",
        loop_id="LOOP-BOUND-LIFE-1",
        loop_state_digest="loop-state",
        anchor_id=f"RA-{campaign_id}",
        run_id=f"RUN-{campaign_id}",
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
        witnesses=["readback:bound-life-identity"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:life-quest:execute",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": QUEST_ID, "version": QUEST_VERSION}],
    )


def _packet(
    *,
    campaign_id: str = "RHC-BOUND-LIFE-1",
    branch_id: str = "B-BOUND-LIFE-1",
    residual_step: int = 3,
    pulse: dict | None = None,
) -> dict:
    pulse = pulse or _pulse()
    return compile_campaign_v3_life_quest_packet(
        pulse=pulse,
        residual_step=residual_step,
        campaign_id=campaign_id,
        branch_id=branch_id,
        agent_coordinate_name=AGENT_ID,
        quest_id=QUEST_ID,
        quest_version=QUEST_VERSION,
        clear_conditions=[
            "all required repository tests pass",
            "packet readback matches committed source",
            "no authority or platform-reset firewall regresses",
        ],
        reseed_anchor=_anchor(pulse=pulse, campaign_id=campaign_id),
        extra_life_reward_candidate=None,
    )


def _bound(
    *,
    campaign_id: str = "RHC-BOUND-LIFE-1",
    branch_id: str = "B-BOUND-LIFE-1",
    residual_step: int = 3,
    pulse_digest: str | None = None,
) -> dict:
    pulse_digest = pulse_digest or _pulse()["pulse_digest"]
    return {
        "artifact": BINDING_ARTIFACT,
        "status": "BOUND",
        "campaign_id": campaign_id,
        "branch_id": branch_id,
        "residual_step": residual_step,
        "standing": "BOUND_LOOP_NOT_WORK_EXECUTED",
        "failures": [],
        "holds": [],
        "execution_authority_granted": False,
        "work_executed": False,
        "pulse_digest": pulse_digest,
        "task": "historical action 3",
        "loop_id": "LOOP-BOUND-LIFE-1",
        "loop_state_digest": "loop-state",
        "campaign_state_digest": "campaign-state",
        "pre_lease_head": "H0",
        "post_lease_head": "H1",
        "post_loop_start_head": "H2",
        "post_bind_head": "H3",
        "next": "RESUME_EXPLICIT_LOOP_AND_EXECUTE_ONE_LAWFUL_CYCLE",
        "laws": [
            "PULSE_DIGEST_VERIFIED_BEFORE_LEASE",
            "BOUND_RECEIPT_RETAINS_VERIFIED_PULSE_DIGEST",
            "CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM",
            "CAMPAIGN_BINDING != WORK_EXECUTION",
            "BOUND_LOOP != OBSERVED_SUCCESS",
        ],
    }


def _reseal_packet(packet: dict) -> dict:
    packet = copy.deepcopy(packet)
    packet.pop("packet_digest", None)
    packet["packet_digest"] = _sha(packet)
    return packet


def _reseal_alignment(receipt: dict) -> dict:
    receipt = copy.deepcopy(receipt)
    receipt.pop("alignment_digest", None)
    receipt["alignment_digest"] = _sha(receipt)
    return receipt


class CampaignV3LifeBoundIdentityTests(unittest.TestCase):
    def test_exact_bound_and_life_packet_align_without_authority_or_provenance_claim(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=packet,
        )
        self.assertEqual(ARTIFACT, receipt["artifact"])
        self.assertEqual("ALIGNED", receipt["status"])
        self.assertTrue(receipt["structural_alignment"])
        self.assertFalse(receipt["receipt_provenance_proven"])
        self.assertFalse(receipt["execution_authority"])
        self.assertFalse(receipt["work_executed"])
        self.assertFalse(receipt["life_dispatch_executed"])
        self.assertFalse(receipt["platform_counter_reset_claimed"])
        self.assertEqual([], validate_campaign_v3_life_bound_identity(receipt))
        self.assertEqual("PASS", verify_campaign_v3_life_bound_identity(receipt)["status"])
        self.assertIn("STRUCTURAL_ALIGNMENT != RECEIPT_PROVENANCE", receipt["laws"])

    def test_pulse_mismatch_holds_even_when_both_source_objects_are_individually_valid(self):
        pulse_a = _pulse(tag="A")
        pulse_b = _pulse(tag="B")
        packet = _packet(pulse=pulse_b)
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse_a["pulse_digest"]),
            life_packet=packet,
        )
        self.assertEqual("HOLD_IDENTITY_MISMATCH", receipt["status"])
        self.assertIn("identity_mismatch:pulse_digest", receipt["failures"])

    def test_campaign_branch_and_residual_mismatches_hold(self):
        pulse = _pulse()
        cases = [
            (_bound(campaign_id="C-A", pulse_digest=pulse["pulse_digest"]), _packet(campaign_id="C-B", pulse=pulse), "campaign_id"),
            (_bound(branch_id="B-A", pulse_digest=pulse["pulse_digest"]), _packet(branch_id="B-B", pulse=pulse), "branch_id"),
            (_bound(residual_step=3, pulse_digest=pulse["pulse_digest"]), _packet(residual_step=4, pulse=pulse), "residual_step"),
        ]
        for bound, packet, field in cases:
            with self.subTest(field=field):
                receipt = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
                self.assertEqual("HOLD_IDENTITY_MISMATCH", receipt["status"])
                self.assertIn(f"identity_mismatch:{field}", receipt["failures"])

    def test_non_bound_or_incomplete_binding_receipt_holds(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)
        for mutate in (
            lambda x: x.__setitem__("status", "HOLD"),
            lambda x: x.__setitem__("standing", "LEASED_NOT_BOUND"),
            lambda x: x.__setitem__("loop_id", ""),
            lambda x: x["laws"].remove("BOUND_RECEIPT_RETAINS_VERIFIED_PULSE_DIGEST"),
        ):
            bound = _bound(pulse_digest=pulse["pulse_digest"])
            mutate(bound)
            with self.subTest(bound=bound):
                receipt = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
                self.assertEqual("HOLD_INVALID_BOUND_RECEIPT", receipt["status"])
                self.assertFalse(receipt["structural_alignment"])

    def test_forged_execution_or_work_authority_holds_fail_closed(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)

        bound = _bound(pulse_digest=pulse["pulse_digest"])
        bound["execution_authority_granted"] = True
        receipt = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
        self.assertEqual("HOLD_INVALID_BOUND_RECEIPT", receipt["status"])

        bound = _bound(pulse_digest=pulse["pulse_digest"])
        bound["work_executed"] = True
        receipt = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
        self.assertEqual("HOLD_INVALID_BOUND_RECEIPT", receipt["status"])

        packet = _packet(pulse=pulse)
        packet["execution_authority"] = True
        packet = _reseal_packet(packet)
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=packet,
        )
        self.assertEqual("HOLD_INVALID_LIFE_PACKET", receipt["status"])

    def test_packet_tamper_without_digest_reseal_holds_before_identity_comparison(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)
        packet["campaign"]["branch_id"] = "TAMPERED"
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=packet,
        )
        self.assertEqual("HOLD_INVALID_LIFE_PACKET", receipt["status"])
        self.assertTrue(any("packet_digest" in item for item in receipt["failures"]))

    def test_alignment_output_validator_rejects_unknown_wrapper_field_even_with_recomputed_digest(self):
        pulse = _pulse()
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=_packet(pulse=pulse),
        )
        receipt["authority"] = True
        receipt = _reseal_alignment(receipt)
        errors = validate_campaign_v3_life_bound_identity(receipt)
        self.assertIn("unknown:authority", errors)

    def test_structural_alignment_never_promotes_caller_supplied_receipt_to_provenance(self):
        pulse = _pulse()
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=_packet(pulse=pulse),
        )
        receipt["receipt_provenance_proven"] = True
        receipt = _reseal_alignment(receipt)
        errors = validate_campaign_v3_life_bound_identity(receipt)
        self.assertIn("receipt_provenance_proven_must_be_false", errors)


if __name__ == "__main__":
    unittest.main()
