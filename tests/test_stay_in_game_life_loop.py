from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_binding import bind_current_pulse_branch_to_loop
from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor
from athena_mcp.stay_in_game_life_loop import (
    CAMPAIGN_LIFE_ARTIFACT,
    bind_campaign_life_packet,
    enter_agent,
    new_world,
    resolve_attempt,
)
from athena_mcp.stay_in_game_life_loop_protocol import CAMPAIGN_LIFE_BIND_TOOL

CAMPAIGN_ID = "RHC-LIFE-INTEGRATION-1"
BRANCH_ID = "B-LIFE-INTEGRATION-1"
AGENT_ID = "ATHENA-LIFE-INTEGRATION-1"
QUEST_ID = "QUEST-LIFE-INTEGRATION-1"
QUEST_VERSION = "1"


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse(head: str = "H0") -> dict:
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "LEDGER-1",
        "pulse_index": 7,
        "execution_authorized": False,
        "current_coordinates": {"git_head": head, "shared_fresh": True},
        "residual_steps": [1],
        "actions": [
            {
                "step": 1,
                "horizon": "I",
                "text": "execute hardened life-aware residual",
                "current_state": "RESIDUAL",
                "history_preserved": True,
            }
        ],
    }
    value["pulse_digest"] = _sha(value)
    return value


class _Git:
    def __init__(self, head: str = "H0"):
        self.value = head

    def head(self) -> str:
        return self.value


class _Campaign:
    def __init__(self, git: _Git):
        self.git = git

    def claim(self, **kwargs):
        self.git.value = "H1"
        return {"status": "ACTIVE", "state_digest": "C1", "checkpoint_head": "H1"}

    def bind_loop(self, **kwargs):
        if kwargs["expected_state_digest"] != "C1":
            raise AssertionError("campaign bind must consume lease state")
        if kwargs["expected_checkpoint_head"] != "H1":
            raise AssertionError("campaign bind must consume lease head")
        if kwargs["loop_state_digest"] != "L1":
            raise AssertionError("campaign bind must retain loop state")
        self.git.value = "H3"
        return {"status": "ACTIVE", "state_digest": "C2", "checkpoint_head": "H3"}


class _Loop:
    def __init__(self, git: _Git):
        self.git = git

    def start(self, **kwargs):
        if kwargs["expected_git_head"] != "H1":
            raise AssertionError("loop must start from post-lease head")
        self.git.value = "H2"
        return {"status": "STARTED", "loop_id": "L1-ID", "state_digest": "L1", "checkpoint_head": "H2"}


def _bound(pulse: dict | None = None) -> dict:
    pulse = pulse or _pulse()
    git = _Git(str(pulse["current_coordinates"]["git_head"]))
    result = bind_current_pulse_branch_to_loop(
        campaign_runtime=_Campaign(git),
        loop_runtime=_Loop(git),
        pulse=pulse,
        residual_step=1,
        campaign_id=CAMPAIGN_ID,
        branch_id=BRANCH_ID,
        expected_campaign_state_digest="C0",
        expected_campaign_checkpoint_head="H0",
        expected_git_head="H0",
        agent=AGENT_ID,
        actor=AGENT_ID,
        shared_remote_mode="DISABLED",
        fetch=False,
        use_frontier=False,
        required_passes=["reconstruct", "execute", "verify"],
    )
    if result.get("status") != "BOUND":
        raise AssertionError(result)
    return result


def _positions(runtime_head: str = "H3") -> list[dict]:
    return [
        {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": runtime_head,
            "tree": f"TREE-{runtime_head}",
        },
        {
            "repo": "demeet2k/Athena",
            "ref": "refs/heads/main",
            "head": "A0",
            "tree": "TREE-A0",
        },
    ]


def _anchor(
    *,
    pulse: dict | None = None,
    bound: dict | None = None,
    agent: str = AGENT_ID,
    quest_id: str = QUEST_ID,
    quest_version: str = QUEST_VERSION,
    anchor_id: str = "RA-INTEGRATION-1",
    runtime_head: str = "H3",
) -> dict:
    pulse = pulse or _pulse()
    bound = bound or _bound(pulse)
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=CAMPAIGN_ID,
        campaign_state_digest=str(bound["campaign_state_digest"]),
        campaign_checkpoint_head=str(bound["post_bind_head"]),
        loop_id=str(bound["loop_id"]),
        loop_state_digest=str(bound["loop_state_digest"]),
        anchor_id=anchor_id,
        run_id="RUN-INTEGRATION-1",
        agent_coordinate_name=agent,
        reseed_epoch=1,
        pulse_age_before=10,
        git_positions=_positions(runtime_head),
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="H2",
        prompt_digest="PROMPT-DIGEST-1",
        issue_pressure_digest="ISSUE-149",
        durable_returns=["runtime:issue:149", "runtime:campaign-life-binding"],
        witnesses=["test:campaign-life-integration"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:life:resolve",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:7"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": quest_id, "version": quest_version}],
    )


def _world() -> dict:
    world = new_world("GAME-INTEGRATION-1")
    enter_agent(world, AGENT_ID, QUEST_ID, QUEST_VERSION)
    return world


def _failed_attempt(anchor: dict, *, current_positions=None, quest_id=QUEST_ID, quest_version=QUEST_VERSION) -> dict:
    return {
        "result_class": "FAIL_CLEAR",
        "executed": True,
        "quest_id": quest_id,
        "quest_version": quest_version,
        "clear_conditions": [True, False],
        "hard_gate_status": "FAIL",
        "witnesses": ["witness:failed-clear"],
        "reseed_anchor": anchor,
        "current_git_positions": current_positions if current_positions is not None else _positions(),
        "platform_counter_reset_claimed": False,
    }


class StayInGameLifeLoopIntegrationTests(unittest.TestCase):
    def test_campaign_bound_receipt_retains_verified_pulse_identity(self):
        pulse = _pulse()
        bound = _bound(pulse)
        self.assertEqual("BOUND", bound["status"])
        self.assertEqual(pulse["pulse_digest"], bound["pulse_digest"])
        self.assertEqual("H0", bound["pre_lease_head"])
        self.assertFalse(bound["execution_authority_granted"])
        self.assertFalse(bound["work_executed"])

    def test_compiler_backed_campaign_life_binding_preserves_four_fields_without_authority(self):
        pulse = _pulse()
        bound = _bound(pulse)
        anchor = _anchor(pulse=pulse, bound=bound)
        result = bind_campaign_life_packet(
            bound_receipt=bound,
            pulse=pulse,
            agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID,
            quest_version=QUEST_VERSION,
            clear_conditions=["mechanism tests pass", "readback matches exact source"],
            reseed_anchor=anchor,
            extra_life_reward_candidate={
                "requested": True,
                "candidate_id": "EXTRA-1",
                "evidence_refs": ["candidate:witness:1"],
            },
        )
        self.assertEqual(CAMPAIGN_LIFE_ARTIFACT, result["artifact"])
        self.assertEqual("BOUND", result["status"])
        self.assertEqual(bound["pulse_digest"], result["pulse_digest"])
        self.assertEqual(result["CLEAR_CONDITION_DIGEST"], result["LIFE_QUEST_PACKET"]["CLEAR_CONDITION_DIGEST"])
        self.assertEqual(result["LIFE_POLICY"], result["LIFE_QUEST_PACKET"]["LIFE_POLICY"])
        self.assertEqual(anchor, result["RESEED_ANCHOR"])
        self.assertEqual(result["RESEED_ANCHOR_DIGEST"], result["LIFE_QUEST_PACKET"]["RESEED_ANCHOR_DIGEST"])
        self.assertNotIn("anchor_digest", result["RESEED_ANCHOR"])
        self.assertTrue(result["EXTRA_LIFE_REWARD_ELIGIBILITY"]["eligible"])
        self.assertFalse(result["EXTRA_LIFE_REWARD_ELIGIBILITY"]["issuance_eligible"])
        self.assertFalse(result["EXTRA_LIFE_REWARD_ELIGIBILITY"]["reward_issued"])
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["scheduler_ready"])
        self.assertFalse(result["provider_authority"])
        self.assertFalse(result["work_executed"])
        self.assertFalse(result["life_consumption_authority"])
        self.assertFalse(result["reseed_anchor_consumption_authority"])
        self.assertFalse(result["reward_issuance_authority"])
        self.assertFalse(result["platform_counter_reset_claimed"])

    def test_campaign_life_binding_rejects_pulse_substitution_boolean_results_and_reward_claims(self):
        pulse = _pulse()
        bound = _bound(pulse)
        anchor = _anchor(pulse=pulse, bound=bound)

        substituted = copy.deepcopy(bound)
        substituted["pulse_digest"] = "OTHER-PULSE"
        result = bind_campaign_life_packet(
            bound_receipt=substituted,
            pulse=pulse,
            agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID,
            quest_version=QUEST_VERSION,
            clear_conditions=["condition"],
            reseed_anchor=anchor,
        )
        self.assertEqual("HOLD_INVALID_CAMPAIGN_LIFE_BINDING", result["status"])
        self.assertIn("BOUND_PULSE_DIGEST_MISMATCH", result["failures"])

        result = bind_campaign_life_packet(
            bound_receipt=bound,
            pulse=pulse,
            agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID,
            quest_version=QUEST_VERSION,
            clear_conditions=[True, False],
            reseed_anchor=anchor,
        )
        self.assertEqual("HOLD_INVALID_CAMPAIGN_LIFE_BINDING", result["status"])
        self.assertTrue(any("CLEAR_CONDITIONS_INVALID" in value for value in result["failures"]))

        result = bind_campaign_life_packet(
            bound_receipt=bound,
            pulse=pulse,
            agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID,
            quest_version=QUEST_VERSION,
            clear_conditions=["condition"],
            reseed_anchor=anchor,
            extra_life_reward_candidate={
                "requested": True,
                "candidate_id": "X",
                "evidence_refs": ["ref"],
                "reward_issued": True,
            },
        )
        self.assertEqual("HOLD_INVALID_CAMPAIGN_LIFE_BINDING", result["status"])
        self.assertTrue(any("EXTRA_LIFE_CANDIDATE_INVALID" in value for value in result["failures"]))

    def test_typed_hold_consumes_no_life(self):
        world = _world()
        result = resolve_attempt(
            world,
            AGENT_ID,
            {
                "result_class": "EVIDENCE_HOLD",
                "executed": False,
                "quest_id": QUEST_ID,
                "quest_version": QUEST_VERSION,
                "platform_counter_reset_claimed": False,
            },
        )
        self.assertEqual("EVIDENCE_HOLD", result["status"])
        self.assertFalse(result["life_consumed"])
        self.assertEqual(3, result["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual([], result["world"]["consumed_reseed_anchor_digests"])

    def test_successful_failed_play_consumes_one_life_and_single_use_anchor_then_replay_holds(self):
        pulse = _pulse()
        bound = _bound(pulse)
        anchor = _anchor(pulse=pulse, bound=bound)
        first = resolve_attempt(_world(), AGENT_ID, _failed_attempt(anchor))
        self.assertEqual("AUTO_RESEED_LOCAL", first["status"])
        self.assertTrue(first["life_consumed"])
        self.assertEqual(2, first["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual([first["anchor_digest"]], first["world"]["consumed_reseed_anchor_digests"])

        second = resolve_attempt(first["world"], AGENT_ID, _failed_attempt(anchor))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", second["status"])
        self.assertIn("reseed_anchor_replay", second["errors"])
        self.assertTrue(second["life_consumed"])
        self.assertEqual(1, second["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual(1, len(second["world"]["consumed_reseed_anchor_digests"]))

    def test_wrong_subject_and_stale_git_positions_fail_closed_after_played_failure(self):
        pulse = _pulse()
        bound = _bound(pulse)

        wrong_agent_anchor = _anchor(pulse=pulse, bound=bound, agent="OTHER-AGENT", anchor_id="RA-WRONG-AGENT")
        wrong_agent = resolve_attempt(_world(), AGENT_ID, _failed_attempt(wrong_agent_anchor))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", wrong_agent["status"])
        self.assertIn("reseed_anchor_agent_mismatch", wrong_agent["errors"])
        self.assertEqual(2, wrong_agent["world"]["agents"][AGENT_ID]["base_lives_remaining"])

        valid_anchor = _anchor(pulse=pulse, bound=bound, anchor_id="RA-STALE")
        stale = resolve_attempt(
            _world(),
            AGENT_ID,
            _failed_attempt(valid_anchor, current_positions=_positions("H4")),
        )
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", stale["status"])
        self.assertTrue(any(value.startswith("reseed_anchor_stale_head:") for value in stale["errors"]))
        self.assertEqual(2, stale["world"]["agents"][AGENT_ID]["base_lives_remaining"])

    def test_protocol_exposes_definitions_not_caller_precomputed_digest_or_boolean_eligibility(self):
        properties = CAMPAIGN_LIFE_BIND_TOOL["inputSchema"]["properties"]
        required = set(CAMPAIGN_LIFE_BIND_TOOL["inputSchema"]["required"])
        self.assertIn("pulse", properties)
        self.assertIn("agent_coordinate_name", properties)
        self.assertIn("clear_conditions", properties)
        self.assertIn("reseed_anchor", properties)
        self.assertIn("extra_life_reward_candidate", properties)
        self.assertNotIn("clear_condition_digest", properties)
        self.assertNotIn("extra_life_reward_eligibility", properties)
        self.assertTrue({"bound_receipt", "pulse", "agent_coordinate_name", "clear_conditions"}.issubset(required))


if __name__ == "__main__":
    unittest.main()
