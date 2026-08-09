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

AGENT = "ATHENA-BOUND-LIFE-1"
QUEST = "QUEST-BOUND-LIFE-001"
VERSION = "1"


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _pulse(tag="A"):
    states = ["SATISFIED", "SUPERSEDED"] + ["RESIDUAL"] * 8
    actions = [
        {
            "step": i + 1,
            "horizon": "I" if i < 4 else ("M" if i < 7 else "L"),
            "text": f"historical action {i + 1}",
            "current_state": state,
            "history_preserved": True,
        }
        for i, state in enumerate(states)
    ]
    pulse = {
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
        "operational_basis_digest": "basis",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": ["PULSE_100_RESEED_REQUIRED"],
    }
    pulse["pulse_digest"] = _sha(pulse)
    return pulse


def _anchor(pulse, campaign):
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=campaign,
        campaign_state_digest="campaign-state",
        campaign_checkpoint_head="campaign-head",
        loop_id="LOOP-BOUND-LIFE-1",
        loop_state_digest="loop-state",
        anchor_id=f"RA-{campaign}",
        run_id=f"RUN-{campaign}",
        agent_coordinate_name=AGENT,
        reseed_epoch=1,
        pulse_age_before=10,
        git_positions=[
            {"repo": "demeet2k/athena-mcp-server", "ref": "refs/heads/master", "head": "runtime-head", "tree": "runtime-tree"},
            {"repo": "demeet2k/Athena", "ref": "refs/heads/main", "head": "athena-head", "tree": "athena-tree"},
        ],
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="runtime-old",
        prompt_digest="prompt",
        issue_pressure_digest="issue-149",
        durable_returns=["runtime:issue:149"],
        witnesses=["readback:bound-life"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:life-quest:execute",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": QUEST, "version": VERSION}],
    )


def _packet(*, campaign="RHC-BOUND-LIFE-1", branch="B-BOUND-LIFE-1", step=3, pulse=None):
    pulse = pulse or _pulse()
    return compile_campaign_v3_life_quest_packet(
        pulse=pulse,
        residual_step=step,
        campaign_id=campaign,
        branch_id=branch,
        agent_coordinate_name=AGENT,
        quest_id=QUEST,
        quest_version=VERSION,
        clear_conditions=[
            "all required repository tests pass",
            "packet readback matches committed source",
            "no authority or platform-reset firewall regresses",
        ],
        reseed_anchor=_anchor(pulse, campaign),
        extra_life_reward_candidate=None,
    )


def _bound(*, campaign="RHC-BOUND-LIFE-1", branch="B-BOUND-LIFE-1", step=3, pulse_digest=None):
    return {
        "artifact": BINDING_ARTIFACT,
        "status": "BOUND",
        "campaign_id": campaign,
        "branch_id": branch,
        "residual_step": step,
        "standing": "BOUND_LOOP_NOT_WORK_EXECUTED",
        "failures": [],
        "holds": [],
        "execution_authority_granted": False,
        "work_executed": False,
        "pulse_digest": pulse_digest or _pulse()["pulse_digest"],
        "task": f"historical action {step}",
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
            "CAMPAIGN_BINDING != WORK_EXECUTION",
            "BOUND_LOOP != OBSERVED_SUCCESS",
        ],
    }


def _reseal(value, field):
    value = copy.deepcopy(value)
    value.pop(field, None)
    value[field] = _sha(value)
    return value


class CampaignV3LifeBoundIdentityTests(unittest.TestCase):
    def test_exact_alignment_is_structural_only(self):
        pulse = _pulse()
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=_packet(pulse=pulse),
        )
        self.assertEqual((ARTIFACT, "ALIGNED"), (receipt["artifact"], receipt["status"]))
        self.assertTrue(receipt["structural_alignment"])
        for field in ("receipt_provenance_proven", "execution_authority", "work_executed", "life_dispatch_executed", "platform_counter_reset_claimed"):
            self.assertFalse(receipt[field])
        self.assertEqual([], validate_campaign_v3_life_bound_identity(receipt))
        self.assertEqual("PASS", verify_campaign_v3_life_bound_identity(receipt)["status"])

    def test_individually_valid_identity_mismatches_hold(self):
        pulse_a, pulse_b = _pulse("A"), _pulse("B")
        cases = [
            (_bound(pulse_digest=pulse_a["pulse_digest"]), _packet(pulse=pulse_b), "pulse_digest"),
            (_bound(campaign="C-A", pulse_digest=pulse_a["pulse_digest"]), _packet(campaign="C-B", pulse=pulse_a), "campaign_id"),
            (_bound(branch="B-A", pulse_digest=pulse_a["pulse_digest"]), _packet(branch="B-B", pulse=pulse_a), "branch_id"),
            (_bound(step=3, pulse_digest=pulse_a["pulse_digest"]), _packet(step=4, pulse=pulse_a), "residual_step"),
        ]
        for bound, packet, field in cases:
            with self.subTest(field=field):
                out = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
                self.assertEqual("HOLD_IDENTITY_MISMATCH", out["status"])
                self.assertIn(f"identity_mismatch:{field}", out["failures"])

    def test_inconsistent_bound_receipts_hold_before_alignment(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)
        mutations = [
            ("status", "HOLD"),
            ("standing", "LEASED_NOT_BOUND"),
            ("loop_id", ""),
            ("failures", ["synthetic"]),
            ("holds", [{"kind": "synthetic"}]),
            ("next", "SKIP_EXECUTION"),
            ("post_lease_head", "H0"),
            ("post_bind_head", "H2"),
        ]
        for field, value in mutations:
            bound = _bound(pulse_digest=pulse["pulse_digest"])
            bound[field] = value
            with self.subTest(field=field):
                out = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
                self.assertEqual("HOLD_INVALID_BOUND_RECEIPT", out["status"])

        bound = _bound(pulse_digest=pulse["pulse_digest"])
        bound["laws"].remove("BOUND_RECEIPT_RETAINS_VERIFIED_PULSE_DIGEST")
        out = align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)
        self.assertEqual("HOLD_INVALID_BOUND_RECEIPT", out["status"])

    def test_authority_smuggling_and_packet_tamper_hold(self):
        pulse = _pulse()
        packet = _packet(pulse=pulse)
        for field in ("execution_authority_granted", "work_executed"):
            bound = _bound(pulse_digest=pulse["pulse_digest"])
            bound[field] = True
            self.assertEqual(
                "HOLD_INVALID_BOUND_RECEIPT",
                align_campaign_v3_bound_life_packet(bound_receipt=bound, life_packet=packet)["status"],
            )

        authority_packet = _packet(pulse=pulse)
        authority_packet["execution_authority"] = True
        authority_packet = _reseal(authority_packet, "packet_digest")
        self.assertEqual(
            "HOLD_INVALID_LIFE_PACKET",
            align_campaign_v3_bound_life_packet(
                bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
                life_packet=authority_packet,
            )["status"],
        )

        tampered = _packet(pulse=pulse)
        tampered["campaign"]["branch_id"] = "TAMPERED"
        out = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]), life_packet=tampered
        )
        self.assertEqual("HOLD_INVALID_LIFE_PACKET", out["status"])
        self.assertTrue(any("packet_digest" in error for error in out["failures"]))

    def test_output_firewalls_survive_digest_recomputation(self):
        pulse = _pulse()
        receipt = align_campaign_v3_bound_life_packet(
            bound_receipt=_bound(pulse_digest=pulse["pulse_digest"]),
            life_packet=_packet(pulse=pulse),
        )

        extra = copy.deepcopy(receipt)
        extra["authority"] = True
        extra = _reseal(extra, "alignment_digest")
        self.assertIn("unknown:authority", validate_campaign_v3_life_bound_identity(extra))

        forged = copy.deepcopy(receipt)
        forged["receipt_provenance_proven"] = True
        forged = _reseal(forged, "alignment_digest")
        self.assertIn(
            "receipt_provenance_proven_must_be_false",
            validate_campaign_v3_life_bound_identity(forged),
        )


if __name__ == "__main__":
    unittest.main()
