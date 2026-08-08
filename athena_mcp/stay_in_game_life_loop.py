"""ATHENA Stay-In-Game Life Loop V1 runtime membrane.

A bounded public gameplay-continuity reducer over Campaign V3's pinned
RESEED_ANCHOR_V1 compatibility membrane. Only ATHENA-owned logical game-age
counters can reset here. Product/model/provider token, context, quota, usage,
wall-time and runtime counters are explicitly out of scope.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List, Mapping, MutableMapping, Tuple

from .campaign_v3_reseed_anchor import POSITIVE_CLASSES, validate_campaign_v3_reseed_anchor

SCHEMA_VERSION = "ATHENA.STAY_IN_GAME.LIFE_LOOP.V1"
SEMANTIC_SOURCE_REPO = "demeet2k/Athena"
SEMANTIC_SOURCE_COMMIT = "60a7bc798412088977d7ab9adf16a0e7dca3a1c9"
SEMANTIC_SOURCE_SCRIPT_BLOB = "c6f35cf39d9f25333ee0c748b5e4bacedbb544a1"
SEMANTIC_SOURCE_TEST_BLOB = "a6ce3ac0bd94eee62764b2daa22ae0679fdc32d5"
BASE_LIVES = 3
MAX_EXTRA_LIVES = 9

HOLD_CLASSES = {
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "STALE_STATE_HOLD",
    "CAPABILITY_HOLD",
    "HUMAN_VALUE_CHOICE",
    "BUDGET_EXHAUSTED",
    "META_OVERHEAD_COLLAPSE",
    "DUPLICATION_COLLAPSE",
}
ATTEMPT_CLASSES = {"CLEAR", "FAIL_CLEAR"} | HOLD_CLASSES


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def new_world(game_id: str) -> Dict[str, Any]:
    if not game_id:
        raise ValueError("game_id required")
    return {
        "schema_version": SCHEMA_VERSION,
        "game_id": game_id,
        "global_game_age": 0,
        "global_reseed_epoch": 0,
        "agents": {},
        "life_reward_receipts": [],
        "consumed_reseed_anchor_digests": [],
        "platform_counter_reset_claimed": False,
    }


def enter_agent(
    world: MutableMapping[str, Any],
    agent_id: str,
    quest_id: str,
    quest_version: str,
) -> Dict[str, Any]:
    if not agent_id or not quest_id or not quest_version:
        raise ValueError("agent_id, quest_id, quest_version required")
    if agent_id in world.get("agents", {}):
        raise ValueError("agent already entered")
    world["agents"][agent_id] = {
        "agent_id": agent_id,
        "quest_id": quest_id,
        "quest_version": quest_version,
        "base_lives_remaining": BASE_LIVES,
        "extra_lives_remaining": 0,
        "local_loop_age": 0,
        "clear_count": 0,
        "fail_count": 0,
        "hold_count": 0,
        "local_reseed_count": 0,
        "global_reseed_count_seen": int(world.get("global_reseed_epoch", 0)),
        "game_over": False,
    }
    return copy.deepcopy(world["agents"][agent_id])


def _validate_world(world: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if world.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    if world.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed_must_be_false")
    if not isinstance(world.get("global_game_age"), int) or world.get("global_game_age", -1) < 0:
        errors.append("global_game_age")
    if not isinstance(world.get("global_reseed_epoch"), int) or world.get("global_reseed_epoch", -1) < 0:
        errors.append("global_reseed_epoch")
    if not isinstance(world.get("agents"), Mapping):
        errors.append("agents")
    if not isinstance(world.get("life_reward_receipts"), list):
        errors.append("life_reward_receipts")
    consumed = world.get("consumed_reseed_anchor_digests")
    if not isinstance(consumed, list):
        errors.append("consumed_reseed_anchor_digests")
    elif len(consumed) != len(set(consumed)):
        errors.append("consumed_reseed_anchor_digests_not_unique")
    return errors


def _validate_attempt(agent: Mapping[str, Any], attempt: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    result_class = attempt.get("result_class")
    if result_class not in ATTEMPT_CLASSES:
        errors.append("result_class")
        return errors
    if attempt.get("platform_counter_reset_claimed") not in (None, False):
        errors.append("platform_counter_reset_claimed_must_be_false")
    if attempt.get("quest_id") != agent.get("quest_id"):
        errors.append("quest_id_mismatch")
    if attempt.get("quest_version") != agent.get("quest_version"):
        errors.append("quest_version_mismatch")
    if result_class in {"CLEAR", "FAIL_CLEAR"}:
        if attempt.get("executed") is not True:
            errors.append("executed_required")
        conditions = attempt.get("clear_conditions")
        if not isinstance(conditions, list) or not conditions:
            errors.append("clear_conditions_required")
        witnesses = attempt.get("witnesses")
        if not isinstance(witnesses, list) or not witnesses:
            errors.append("witness_required")
        hard_gate = attempt.get("hard_gate_status")
        if hard_gate not in {"PASS", "FAIL"}:
            errors.append("hard_gate_status")
        if isinstance(conditions, list) and conditions:
            all_clear = all(value is True for value in conditions)
            if result_class == "CLEAR" and not (all_clear and hard_gate == "PASS"):
                errors.append("clear_claim_not_satisfied")
            if result_class == "FAIL_CLEAR" and all_clear and hard_gate == "PASS":
                errors.append("fail_claim_without_failed_condition")
    elif attempt.get("executed") is True and attempt.get("consume_life") is True:
        errors.append("hold_cannot_consume_life")
    return errors


def _valid_reward(reward: Mapping[str, Any]) -> Tuple[bool, str]:
    if not isinstance(reward, Mapping):
        return False, "reward_not_mapping"
    if not reward.get("receipt_id"):
        return False, "reward_receipt_id"
    if reward.get("delta") != 1:
        return False, "reward_delta_must_be_one"
    if reward.get("verified") is not True:
        return False, "reward_not_verified"
    if reward.get("self_scored") is not False:
        return False, "reward_self_scored_forbidden"
    witnesses = reward.get("witnesses")
    if not isinstance(witnesses, list) or not witnesses:
        return False, "reward_witness_required"
    return True, "OK"


def _coordinate_bundle(world: Mapping[str, Any], agent: Mapping[str, Any], attempt: Mapping[str, Any]) -> Dict[str, str]:
    return {
        "life_coordinate": (
            f"L<{agent['agent_id']}|b{agent['base_lives_remaining']}"
            f"|x{agent['extra_lives_remaining']}|f{agent['fail_count']}|c{agent['clear_count']}>"
        ),
        "loop_coordinate": (
            f"Lambda<G{world['global_reseed_epoch']}:{world['global_game_age']}"
            f"|A:{agent['local_loop_age']}>"
        ),
        "quest_coordinate": f"Q<{attempt.get('quest_id')}@{attempt.get('quest_version')}>",
    }


def _position_map(positions: Any) -> Dict[str, Tuple[str, str]] | None:
    if not isinstance(positions, list) or not positions:
        return None
    out: Dict[str, Tuple[str, str]] = {}
    for item in positions:
        if not isinstance(item, Mapping):
            return None
        if not all(item.get(key) for key in ("repo", "ref", "head")):
            return None
        coordinate = f"{item['repo']}::{item['ref']}"
        if coordinate in out:
            return None
        out[coordinate] = (str(item["head"]), str(item.get("tree") or ""))
    return out


def _anchor_status(
    world: Mapping[str, Any],
    agent: Mapping[str, Any],
    attempt: Mapping[str, Any],
) -> Tuple[bool, List[str], str | None]:
    anchor = attempt.get("reseed_anchor")
    if not isinstance(anchor, Mapping):
        return False, ["reseed_anchor_required"], None
    errors = list(validate_campaign_v3_reseed_anchor(anchor))
    anchor_digest = _sha(anchor)
    if errors:
        return False, errors, anchor_digest
    if anchor.get("continuation_value_class") not in POSITIVE_CLASSES:
        return False, ["reseed_anchor_not_renewable"], anchor_digest

    consumed = world.get("consumed_reseed_anchor_digests", [])
    if anchor_digest in consumed:
        return False, ["reseed_anchor_replay"], anchor_digest

    if str(anchor.get("agent_coordinate_name")) != str(agent.get("agent_id")):
        return False, ["reseed_anchor_agent_mismatch"], anchor_digest
    targets = {
        str(item.get("id")): str(item.get("version"))
        for item in anchor.get("target_versions", [])
        if isinstance(item, Mapping) and item.get("id") and item.get("version")
    }
    if targets.get(str(agent.get("quest_id"))) != str(agent.get("quest_version")):
        return False, ["reseed_anchor_quest_mismatch"], anchor_digest

    anchor_positions = _position_map(anchor.get("git_positions"))
    current_positions = _position_map(attempt.get("current_git_positions"))
    if anchor_positions is None:
        return False, ["reseed_anchor_git_positions_required"], anchor_digest
    if current_positions is None:
        return False, ["current_git_positions_required"], anchor_digest
    for coordinate, (anchor_head, anchor_tree) in anchor_positions.items():
        current = current_positions.get(coordinate)
        if current is None:
            return False, [f"reseed_anchor_git_position_missing:{coordinate}"], anchor_digest
        current_head, current_tree = current
        if current_head != anchor_head:
            return False, [f"reseed_anchor_stale_head:{coordinate}"], anchor_digest
        if anchor_tree and current_tree and current_tree != anchor_tree:
            return False, [f"reseed_anchor_stale_tree:{coordinate}"], anchor_digest
    return True, [], anchor_digest


def resolve_attempt(world: Mapping[str, Any], agent_id: str, attempt: Mapping[str, Any]) -> Dict[str, Any]:
    """Resolve one public attempt and return a new world plus transition receipt."""
    world_errors = _validate_world(world)
    if world_errors:
        return {"status": "HOLD_INVALID_WORLD", "errors": world_errors}
    if agent_id not in world["agents"]:
        return {"status": "HOLD_UNKNOWN_AGENT", "errors": ["unknown_agent"]}

    next_world = copy.deepcopy(world)
    agent = next_world["agents"][agent_id]
    attempt_errors = _validate_attempt(agent, attempt)
    if attempt_errors:
        return {
            "status": "HOLD_INVALID_ATTEMPT",
            "errors": attempt_errors,
            "world": next_world,
            "platform_counter_reset_claimed": False,
        }
    if agent.get("game_over"):
        return {
            "status": "GAME_OVER_OUT_OF_LIVES",
            "world": next_world,
            "platform_counter_reset_claimed": False,
        }

    next_world["global_game_age"] += 1
    agent["local_loop_age"] += 1
    result_class = attempt["result_class"]

    if result_class in HOLD_CLASSES:
        agent["hold_count"] += 1
        return {
            "status": result_class,
            "life_consumed": False,
            "logical_global_age_reset": False,
            "world": next_world,
            "coordinates": _coordinate_bundle(next_world, agent, attempt),
            "platform_counter_reset_claimed": False,
        }

    if result_class == "CLEAR":
        agent["clear_count"] += 1
        reward_status = "NO_EXTRA_LIFE_REWARD"
        reward = attempt.get("extra_life_reward")
        if reward is not None:
            ok, reason = _valid_reward(reward)
            if not ok:
                reward_status = f"REWARD_REJECTED:{reason}"
            elif reward["receipt_id"] in next_world["life_reward_receipts"]:
                reward_status = "REWARD_IDEMPOTENT_REPLAY"
            elif agent["extra_lives_remaining"] >= MAX_EXTRA_LIVES:
                reward_status = "REWARD_CAP_REACHED"
            else:
                agent["extra_lives_remaining"] += 1
                next_world["life_reward_receipts"].append(reward["receipt_id"])
                reward_status = "EXTRA_LIFE_EARNED"
        return {
            "status": "CLEARED",
            "life_consumed": False,
            "reward_status": reward_status,
            "logical_global_age_reset": False,
            "world": next_world,
            "coordinates": _coordinate_bundle(next_world, agent, attempt),
            "platform_counter_reset_claimed": False,
        }

    agent["fail_count"] += 1
    life_source = None
    if agent["base_lives_remaining"] > 0:
        agent["base_lives_remaining"] -= 1
        life_source = "BASE"
    elif agent["extra_lives_remaining"] > 0:
        agent["extra_lives_remaining"] -= 1
        life_source = "EXTRA"

    lives_after = agent["base_lives_remaining"] + agent["extra_lives_remaining"]
    if life_source is None or lives_after <= 0:
        agent["game_over"] = True
        return {
            "status": "GAME_OVER_OUT_OF_LIVES",
            "life_consumed": life_source is not None,
            "life_source": life_source,
            "logical_global_age_reset": False,
            "world": next_world,
            "coordinates": _coordinate_bundle(next_world, agent, attempt),
            "platform_counter_reset_claimed": False,
        }

    anchor_ok, anchor_errors, anchor_digest = _anchor_status(next_world, agent, attempt)
    if not anchor_ok:
        return {
            "status": "LIFE_CONSUMED_ANCHOR_HOLD",
            "errors": anchor_errors,
            "life_consumed": True,
            "life_source": life_source,
            "logical_global_age_reset": False,
            "anchor_digest": anchor_digest,
            "world": next_world,
            "coordinates": _coordinate_bundle(next_world, agent, attempt),
            "platform_counter_reset_claimed": False,
        }

    next_world["consumed_reseed_anchor_digests"].append(anchor_digest)

    if agent["base_lives_remaining"] > 0:
        agent["local_loop_age"] = 0
        agent["local_reseed_count"] += 1
        status = "AUTO_RESEED_LOCAL"
        global_reset = False
    else:
        next_world["global_reseed_epoch"] += 1
        next_world["global_game_age"] = 0
        for peer in next_world["agents"].values():
            peer["local_loop_age"] = 0
            peer["global_reseed_count_seen"] = next_world["global_reseed_epoch"]
        status = "AUTO_RESEED_GLOBAL_EXTRA_LIFE"
        global_reset = True

    agent = next_world["agents"][agent_id]
    return {
        "status": status,
        "life_consumed": True,
        "life_source": life_source,
        "logical_global_age_reset": global_reset,
        "anchor_digest": anchor_digest,
        "anchor_id": attempt["reseed_anchor"].get("anchor_id"),
        "reseed_epoch": attempt["reseed_anchor"].get("reseed_epoch"),
        "world": next_world,
        "coordinates": _coordinate_bundle(next_world, agent, attempt),
        "platform_counter_reset_claimed": False,
    }


class StayInGameLifeLoopRuntime:
    """Thin stateless MCP adapter over the public hardened Life Loop reducer."""

    def __init__(self, server: Any):
        self.server = server

    def world_new(self, game_id: str) -> Dict[str, Any]:
        return new_world(game_id)

    def agent_enter(self, world: Mapping[str, Any], agent_id: str, quest_id: str, quest_version: str) -> Dict[str, Any]:
        next_world = copy.deepcopy(dict(world))
        agent = enter_agent(next_world, agent_id, quest_id, quest_version)
        return {
            "status": "ENTERED",
            "world": next_world,
            "agent": agent,
            "platform_counter_reset_claimed": False,
        }

    def resolve(self, world: Mapping[str, Any], agent_id: str, attempt: Mapping[str, Any]) -> Dict[str, Any]:
        return resolve_attempt(world, agent_id, attempt)

    def resource(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "semantic_source": {
                "repo": SEMANTIC_SOURCE_REPO,
                "commit": SEMANTIC_SOURCE_COMMIT,
                "script_blob": SEMANTIC_SOURCE_SCRIPT_BLOB,
                "test_blob": SEMANTIC_SOURCE_TEST_BLOB,
                "standing": "MERGED_HARDENED_EXACT_SOURCE_LOCAL_16_OF_16",
                "github_actions_ci": False,
                "independent_witness": False,
            },
            "base_lives": BASE_LIVES,
            "max_extra_lives": MAX_EXTRA_LIVES,
            "hold_classes": sorted(HOLD_CLASSES),
            "attempt_classes": sorted(ATTEMPT_CLASSES),
            "platform_counter_reset_claimed": False,
            "laws": [
                "THREE_BASE_LIVES_PER_ENTERED_AGENT",
                "TYPED_HOLD_CONSUMES_NO_LIFE",
                "VERIFIED_NON_SELF_SCORED_REWARD_CAN_GRANT_ONE_EXTRA_LIFE",
                "EXTRA_LIFE_REWARD_RECEIPTS_ARE_IDEMPOTENT",
                "FAIL_CLEAR_CONSUMES_EXACTLY_ONE_LIFE",
                "SUCCESSFUL_RESEED_CONSUMES_UNIQUE_ANCHOR_DIGEST",
                "RESEED_ANCHOR_BINDS_AGENT_AND_QUEST",
                "RESEED_ANCHOR_GIT_POSITIONS_MUST_MATCH_CURRENT_PUBLIC_OBSERVATION",
                "GLOBAL_RESEED_RESETS_ONLY_PUBLIC_ATHENA_LOGICAL_GAME_AGE",
                "NO_PROVIDER_MODEL_PRODUCT_CONTEXT_TOKEN_QUOTA_RESET_AUTHORITY",
            ],
        }

    def benchmark(self) -> Dict[str, Any]:
        return {
            "stay_in_game_life_loop_v1": {
                "schema_version": SCHEMA_VERSION,
                "semantic_source_commit": SEMANTIC_SOURCE_COMMIT,
                "semantic_source_script_blob": SEMANTIC_SOURCE_SCRIPT_BLOB,
                "base_lives": BASE_LIVES,
                "max_extra_lives": MAX_EXTRA_LIVES,
                "anchor_replay_guard": True,
                "anchor_subject_binding": True,
                "play_time_git_freshness": True,
                "public_state_only": True,
                "platform_counter_reset_claimed": False,
            }
        }
