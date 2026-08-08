from __future__ import annotations

import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from athena_mcp.aor_collective_transport_surface import AorCollectiveTransportSurface
from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor
from athena_mcp.stay_in_game_life_loop import (
    SEMANTIC_SOURCE_COMMIT,
    SEMANTIC_SOURCE_SCRIPT_BLOB,
    StayInGameLifeLoopRuntime,
    enter_agent,
    new_world,
    resolve_attempt,
)
from athena_mcp.stay_in_game_life_loop_protocol import (
    CAMPAIGN_LIFE_BIND_TOOL,
    STAY_IN_GAME_LIFE_LOOP_TOOLS,
)

CAMPAIGN_ID = "RHC-LIFE-RUNTIME-1"
AGENT_ID = "ATHENA-LIFE-RUNTIME-1"
QUEST_ID = "QUEST-LIFE-RUNTIME-1"
QUEST_VERSION = "1"
RUNTIME_REPO = "demeet2k/athena-mcp-server"
RUNTIME_REF = "refs/heads/master"
ATHENA_REPO = "demeet2k/Athena"
ATHENA_REF = "refs/heads/main"


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
                "text": f"runtime life action {step}",
                "current_state": state,
                "history_preserved": True,
            }
        )
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger-life-runtime",
        "source_issue": 149,
        "verification_issue": 192,
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
        "operational_basis_digest": "basis-life-runtime",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": ["PULSE_100_RESEED_REQUIRED"],
    }
    value["pulse_digest"] = _sha(value)
    return value


def _positions(runtime_head="runtime-head", athena_head="athena-head"):
    return [
        {
            "repo": RUNTIME_REPO,
            "ref": RUNTIME_REF,
            "head": runtime_head,
            "tree": "runtime-tree",
        },
        {
            "repo": ATHENA_REPO,
            "ref": ATHENA_REF,
            "head": athena_head,
            "tree": "athena-tree",
        },
    ]


def _anchor(epoch=1, *, agent_id=AGENT_ID, quest_id=QUEST_ID, quest_version=QUEST_VERSION):
    pulse = _pulse()
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id=CAMPAIGN_ID,
        campaign_state_digest="campaign-state-life-runtime",
        campaign_checkpoint_head="campaign-head-life-runtime",
        loop_id="LOOP-LIFE-RUNTIME-1",
        loop_state_digest=f"loop-state-life-runtime-{epoch}",
        anchor_id=f"RA-LIFE-RUNTIME-{agent_id}-{epoch}",
        run_id=f"RUN-LIFE-RUNTIME-{epoch}",
        agent_coordinate_name=agent_id,
        reseed_epoch=epoch,
        pulse_age_before=epoch,
        git_positions=_positions(),
        primary_repo=RUNTIME_REPO,
        primary_ref=RUNTIME_REF,
        primary_head_before="runtime-old",
        prompt_digest="prompt-life-runtime",
        issue_pressure_digest="issue-149",
        durable_returns=["runtime:issue:149", "athena:issue:278"],
        witnesses=["test:stay-in-game-life-loop"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor=f"campaign-v3:life-runtime:{epoch + 1}",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:life-runtime"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": quest_id, "version": quest_version}],
    )


def _world():
    world = new_world("GAME-LIFE-RUNTIME")
    enter_agent(world, AGENT_ID, QUEST_ID, QUEST_VERSION)
    return world


def _clear_attempt(*, reward=None):
    attempt = {
        "result_class": "CLEAR",
        "quest_id": QUEST_ID,
        "quest_version": QUEST_VERSION,
        "executed": True,
        "hard_gate_status": "PASS",
        "clear_conditions": [True, True],
        "witnesses": ["test:clear"],
        "platform_counter_reset_claimed": False,
    }
    if reward is not None:
        attempt["extra_life_reward"] = reward
    return attempt


def _fail_attempt(anchor=None, *, current_positions=None):
    anchor = anchor or _anchor()
    return {
        "result_class": "FAIL_CLEAR",
        "quest_id": QUEST_ID,
        "quest_version": QUEST_VERSION,
        "executed": True,
        "hard_gate_status": "FAIL",
        "clear_conditions": [True, False],
        "witnesses": ["test:fail-clear"],
        "reseed_anchor": anchor,
        "current_git_positions": copy.deepcopy(current_positions or _positions()),
        "platform_counter_reset_claimed": False,
    }


def _reward(receipt_id="LIFE-RUNTIME-R1", *, self_scored=False):
    return {
        "receipt_id": receipt_id,
        "delta": 1,
        "verified": True,
        "self_scored": self_scored,
        "witnesses": ["test:reward"],
    }


class StayInGameLifeLoopRuntimeTests(unittest.TestCase):
    def test_agent_enters_with_three_lives_and_replay_ledger(self):
        world = _world()
        agent = world["agents"][AGENT_ID]
        self.assertEqual(3, agent["base_lives_remaining"])
        self.assertEqual(0, agent["extra_lives_remaining"])
        self.assertEqual([], world["consumed_reseed_anchor_digests"])
        self.assertFalse(world["platform_counter_reset_claimed"])

    def test_typed_hold_consumes_no_life(self):
        out = resolve_attempt(
            _world(),
            AGENT_ID,
            {
                "result_class": "EVIDENCE_HOLD",
                "quest_id": QUEST_ID,
                "quest_version": QUEST_VERSION,
                "executed": False,
                "platform_counter_reset_claimed": False,
            },
        )
        self.assertEqual("EVIDENCE_HOLD", out["status"])
        self.assertFalse(out["life_consumed"])
        self.assertEqual(3, out["world"]["agents"][AGENT_ID]["base_lives_remaining"])

    def test_failed_clear_consumes_anchor_digest_and_reseeds_locally(self):
        out = resolve_attempt(_world(), AGENT_ID, _fail_attempt(_anchor(1)))
        self.assertEqual("AUTO_RESEED_LOCAL", out["status"])
        self.assertEqual("BASE", out["life_source"])
        self.assertEqual(2, out["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual([out["anchor_digest"]], out["world"]["consumed_reseed_anchor_digests"])

    def test_replayed_anchor_consumes_next_life_but_cannot_reseed(self):
        anchor = _anchor(1)
        first = resolve_attempt(_world(), AGENT_ID, _fail_attempt(anchor))
        second = resolve_attempt(first["world"], AGENT_ID, _fail_attempt(anchor))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", second["status"])
        self.assertIn("reseed_anchor_replay", second["errors"])
        self.assertEqual(1, second["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual(1, len(second["world"]["consumed_reseed_anchor_digests"]))

    def test_stale_git_position_consumes_life_but_cannot_reseed(self):
        stale = _positions(runtime_head="moved-runtime-head")
        out = resolve_attempt(_world(), AGENT_ID, _fail_attempt(_anchor(1), current_positions=stale))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", out["status"])
        self.assertIn(f"reseed_anchor_stale_head:{RUNTIME_REPO}::{RUNTIME_REF}", out["errors"])
        self.assertEqual(2, out["world"]["agents"][AGENT_ID]["base_lives_remaining"])
        self.assertEqual([], out["world"]["consumed_reseed_anchor_digests"])

    def test_wrong_agent_or_quest_anchor_consumes_life_but_cannot_reseed(self):
        wrong_agent = resolve_attempt(_world(), AGENT_ID, _fail_attempt(_anchor(1, agent_id="OTHER-AGENT")))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", wrong_agent["status"])
        self.assertIn("reseed_anchor_agent_mismatch", wrong_agent["errors"])

        wrong_quest_anchor = _anchor(2, quest_id="OTHER-QUEST", quest_version="9")
        wrong_quest = resolve_attempt(_world(), AGENT_ID, _fail_attempt(wrong_quest_anchor))
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", wrong_quest["status"])
        self.assertIn("reseed_anchor_quest_mismatch", wrong_quest["errors"])

    def test_three_failed_clears_without_extra_life_end_game(self):
        world = _world()
        for epoch in (1, 2):
            out = resolve_attempt(world, AGENT_ID, _fail_attempt(_anchor(epoch)))
            self.assertEqual("AUTO_RESEED_LOCAL", out["status"])
            world = out["world"]
        out = resolve_attempt(world, AGENT_ID, _fail_attempt(_anchor(3)))
        self.assertEqual("GAME_OVER_OUT_OF_LIVES", out["status"])
        self.assertTrue(out["world"]["agents"][AGENT_ID]["game_over"])

    def test_verified_extra_life_enables_global_logical_epoch(self):
        world = _world()
        enter_agent(world, "PEER-1", QUEST_ID, QUEST_VERSION)
        earned = resolve_attempt(world, AGENT_ID, _clear_attempt(reward=_reward()))
        self.assertEqual("EXTRA_LIFE_EARNED", earned["reward_status"])
        world = earned["world"]
        world["agents"]["PEER-1"]["local_loop_age"] = 7
        for epoch in (1, 2):
            world = resolve_attempt(world, AGENT_ID, _fail_attempt(_anchor(epoch)))["world"]
        out = resolve_attempt(world, AGENT_ID, _fail_attempt(_anchor(3)))
        self.assertEqual("AUTO_RESEED_GLOBAL_EXTRA_LIFE", out["status"])
        self.assertTrue(out["logical_global_age_reset"])
        self.assertEqual(1, out["world"]["global_reseed_epoch"])
        self.assertEqual(0, out["world"]["global_game_age"])
        self.assertEqual(0, out["world"]["agents"]["PEER-1"]["local_loop_age"])
        self.assertFalse(out["platform_counter_reset_claimed"])

    def test_extra_life_receipt_is_idempotent_and_self_score_rejected(self):
        first = resolve_attempt(_world(), AGENT_ID, _clear_attempt(reward=_reward("R1")))
        second = resolve_attempt(first["world"], AGENT_ID, _clear_attempt(reward=_reward("R1")))
        self.assertEqual("REWARD_IDEMPOTENT_REPLAY", second["reward_status"])
        self.assertEqual(1, second["world"]["agents"][AGENT_ID]["extra_lives_remaining"])

        rejected = resolve_attempt(_world(), AGENT_ID, _clear_attempt(reward=_reward("R2", self_scored=True)))
        self.assertEqual("REWARD_REJECTED:reward_self_scored_forbidden", rejected["reward_status"])
        self.assertEqual(0, rejected["world"]["agents"][AGENT_ID]["extra_lives_remaining"])

    def test_platform_reset_claim_and_duplicate_anchor_ledger_fail_closed(self):
        attempt = _clear_attempt()
        attempt["platform_counter_reset_claimed"] = True
        out = resolve_attempt(_world(), AGENT_ID, attempt)
        self.assertEqual("HOLD_INVALID_ATTEMPT", out["status"])
        self.assertIn("platform_counter_reset_claimed_must_be_false", out["errors"])

        world = _world()
        world["consumed_reseed_anchor_digests"] = ["same", "same"]
        out = resolve_attempt(world, AGENT_ID, _clear_attempt())
        self.assertEqual("HOLD_INVALID_WORLD", out["status"])
        self.assertIn("consumed_reseed_anchor_digests_not_unique", out["errors"])

    def test_protocol_is_strict_and_campaign_tool_matches_pure_compiler_contract(self):
        for tool in STAY_IN_GAME_LIFE_LOOP_TOOLS:
            self.assertFalse(tool["inputSchema"]["additionalProperties"], tool["name"])
        schema = CAMPAIGN_LIFE_BIND_TOOL["inputSchema"]
        self.assertIn("pulse", schema["required"])
        self.assertIn("clear_conditions", schema["required"])
        self.assertNotIn("bound_receipt", schema["properties"])
        candidate = schema["properties"]["extra_life_reward_candidate"]
        self.assertFalse(candidate["additionalProperties"])

    def test_transport_surface_routes_campaign_tool_to_single_packet_compiler(self):
        surface = AorCollectiveTransportSurface.__new__(AorCollectiveTransportSurface)
        surface.life = object()
        args = {
            "pulse": {"artifact": "fixture"},
            "residual_step": 3,
            "campaign_id": CAMPAIGN_ID,
            "branch_id": "BRANCH-LIFE-RUNTIME",
            "agent_coordinate_name": AGENT_ID,
            "quest_id": QUEST_ID,
            "quest_version": QUEST_VERSION,
            "clear_conditions": ["condition one"],
            "reseed_anchor": {"schema_version": "fixture"},
            "extra_life_reward_candidate": {"requested": False},
        }
        sentinel = {"artifact": "SENTINEL-PACKET"}
        with patch(
            "athena_mcp.aor_collective_transport_surface.compile_campaign_v3_life_quest_packet",
            return_value=sentinel,
        ) as compiler:
            handled, result = surface.call_tool("athena_campaign_life_bind", args)
        self.assertTrue(handled)
        self.assertEqual(sentinel, result)
        compiler.assert_called_once_with(
            pulse=args["pulse"],
            residual_step=3,
            campaign_id=CAMPAIGN_ID,
            branch_id="BRANCH-LIFE-RUNTIME",
            agent_coordinate_name=AGENT_ID,
            quest_id=QUEST_ID,
            quest_version=QUEST_VERSION,
            clear_conditions=["condition one"],
            reseed_anchor=args["reseed_anchor"],
            extra_life_reward_candidate={"requested": False},
        )

    def test_resource_pins_merged_hardened_semantic_source(self):
        resource = StayInGameLifeLoopRuntime(None).resource()
        self.assertEqual("60a7bc798412088977d7ab9adf16a0e7dca3a1c9", SEMANTIC_SOURCE_COMMIT)
        self.assertEqual("c6f35cf39d9f25333ee0c748b5e4bacedbb544a1", SEMANTIC_SOURCE_SCRIPT_BLOB)
        self.assertEqual(SEMANTIC_SOURCE_COMMIT, resource["semantic_source"]["commit"])
        self.assertTrue(StayInGameLifeLoopRuntime(None).benchmark()["stay_in_game_life_loop_v1"]["anchor_replay_guard"])
        self.assertFalse(resource["platform_counter_reset_claimed"])


if __name__ == "__main__":
    unittest.main()
