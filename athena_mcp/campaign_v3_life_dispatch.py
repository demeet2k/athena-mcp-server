from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, MutableMapping, Sequence

from .campaign_v3_binding import ARTIFACT as BIND_ARTIFACT, bind_current_pulse_branch_to_loop
from .campaign_v3_reseed_anchor import POSITIVE_CLASSES, validate_campaign_v3_reseed_anchor

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.DISPATCH.V1"
LIFE_POLICY = "STAY_IN_GAME_LIFE_LOOP_V1"
LIFE_SCHEMA_VERSION = "ATHENA.STAY_IN_GAME.LIFE.LOOP.V1"
BASE_LIVES = 3
MAX_EXTRA_LIVES = 9

# Cross-repo source pins. These identify the exact Athena candidate whose life
# semantics this adapter binds into Campaign V3; they are provenance, not a
# claim that the candidate has been canonically promoted.
ATHENA_LIFE_SOURCE_REPO = "demeet2k/Athena"
ATHENA_LIFE_SOURCE_HEAD = "60a7bc798412088977d7ab9adf16a0e7dca3a1c9"
ATHENA_LIFE_SOURCE_BLOB = "c6f35cf39d9f25333ee0c748b5e4bacedbb544a1"

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
GTC_NO_LIFE_STOPS = {"SUCCESS_CLOSED", "NO_POSITIVE_FRONTIER", "PREMATURE_MODEL_STOP"}
GTC_CLASSES = HOLD_CLASSES | GTC_NO_LIFE_STOPS
COMPLETION_STATES = {"SUCCEEDED", "PARTIAL", "HELD", "FAILED", "NO_PROGRESS"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def freeze_clear_condition_digest(clear_condition_ids: Sequence[Any]) -> tuple[list[str], str]:
    values: list[str] = []
    for raw in clear_condition_ids:
        value = str(raw or "").strip()
        if not value:
            raise ValueError("clear condition ids must be nonempty")
        if value in values:
            raise ValueError(f"duplicate clear condition id: {value}")
        values.append(value)
    if not values:
        raise ValueError("at least one clear condition id is required")
    return values, _sha({"clear_condition_ids": values})


def _anchor_digest(anchor: Mapping[str, Any]) -> str:
    return _sha(anchor)


def _anchor_errors(anchor: Any) -> list[str]:
    if not isinstance(anchor, Mapping):
        return ["reseed_anchor_required"]
    errors = list(validate_campaign_v3_reseed_anchor(anchor))
    if errors:
        return errors
    if anchor.get("continuation_value_class") not in POSITIVE_CLASSES:
        return ["reseed_anchor_not_renewable"]
    if not str(anchor.get("selected_successor") or "").strip():
        return ["reseed_anchor_successor_required"]
    return []


def _anchor_subject_errors(anchor: Mapping[str, Any], agent_id: str, quest_id: str, quest_version: str) -> list[str]:
    errors: list[str] = []
    if str(anchor.get("agent_coordinate_name")) != str(agent_id):
        errors.append("reseed_anchor_agent_mismatch")
    targets = {
        str(item.get("id")): str(item.get("version"))
        for item in anchor.get("target_versions", [])
        if isinstance(item, Mapping) and item.get("id") and item.get("version")
    }
    if targets.get(str(quest_id)) != str(quest_version):
        errors.append("reseed_anchor_quest_mismatch")
    return errors


def _position_map(positions: Any) -> dict[str, tuple[str, str]] | None:
    if not isinstance(positions, list) or not positions:
        return None
    out: dict[str, tuple[str, str]] = {}
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


def _attempt_anchor_status(
    world: Mapping[str, Any],
    agent: Mapping[str, Any],
    anchor: Mapping[str, Any] | None,
    current_git_positions: Sequence[Mapping[str, Any]] | None,
) -> tuple[bool, list[str], str | None]:
    base_errors = _anchor_errors(anchor)
    if base_errors or not isinstance(anchor, Mapping):
        return False, base_errors, _anchor_digest(anchor) if isinstance(anchor, Mapping) else None
    anchor_digest = _anchor_digest(anchor)
    if anchor_digest in world.get("consumed_reseed_anchor_digests", []):
        return False, ["reseed_anchor_replay"], anchor_digest
    subject_errors = _anchor_subject_errors(
        anchor, str(agent.get("agent_id")), str(agent.get("quest_id")), str(agent.get("quest_version"))
    )
    if subject_errors:
        return False, subject_errors, anchor_digest
    anchor_positions = _position_map(anchor.get("git_positions"))
    current_positions = _position_map(list(current_git_positions) if current_git_positions is not None else None)
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


def new_world(game_id: str) -> dict[str, Any]:
    game_id = str(game_id or "").strip()
    if not game_id:
        raise ValueError("game_id required")
    return {
        "schema_version": LIFE_SCHEMA_VERSION,
        "game_id": game_id,
        "global_game_age": 0,
        "global_reseed_epoch": 0,
        "agents": {},
        "life_reward_receipts": [],
        "consumed_reseed_anchor_digests": [],
        "platform_counter_reset_claimed": False,
    }


def enter_agent(world: MutableMapping[str, Any], agent_id: str, quest_id: str, quest_version: str) -> dict[str, Any]:
    agent_id = str(agent_id or "").strip()
    quest_id = str(quest_id or "").strip()
    quest_version = str(quest_version or "").strip()
    if not agent_id or not quest_id or not quest_version:
        raise ValueError("agent_id, quest_id, quest_version required")
    agents = world.get("agents")
    if not isinstance(agents, MutableMapping):
        raise ValueError("world agents mapping required")
    if agent_id in agents:
        raise ValueError("agent already entered")
    agents[agent_id] = {
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
    return copy.deepcopy(agents[agent_id])


def _validate_world(world: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if world.get("schema_version") != LIFE_SCHEMA_VERSION:
        errors.append("schema_version")
    if world.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed_must_be_false")
    if not isinstance(world.get("global_game_age"), int) or int(world.get("global_game_age", -1)) < 0:
        errors.append("global_game_age")
    if not isinstance(world.get("global_reseed_epoch"), int) or int(world.get("global_reseed_epoch", -1)) < 0:
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


def _valid_reward(reward: Mapping[str, Any]) -> tuple[bool, str]:
    if not isinstance(reward, Mapping):
        return False, "reward_not_mapping"
    if not str(reward.get("receipt_id") or "").strip():
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


def _coordinates(world: Mapping[str, Any], agent: Mapping[str, Any], quest_id: str, quest_version: str) -> dict[str, str]:
    return {
        "life_coordinate": (
            f"L<{agent['agent_id']}|b{agent['base_lives_remaining']}"
            f"|x{agent['extra_lives_remaining']}|f{agent['fail_count']}|c{agent['clear_count']}>"
        ),
        "loop_coordinate": (
            f"Lambda<G{world['global_reseed_epoch']}:{world['global_game_age']}"
            f"|A:{agent['local_loop_age']}>"
        ),
        "quest_coordinate": f"Q<{quest_id}@{quest_version}>",
    }


def _binding_basis(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in receipt.items() if k != "dispatch_digest"}


def validate_dispatch_binding(receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("artifact") != ARTIFACT:
        errors.append("artifact")
    if receipt.get("status") != "BOUND_LIFE_POLICY":
        errors.append("status")
    if receipt.get("LIFE_POLICY") != LIFE_POLICY:
        errors.append("life_policy")
    if receipt.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed_must_be_false")
    if receipt.get("execution_authority_granted") is not False:
        errors.append("execution_authority_granted_must_be_false")
    if receipt.get("work_executed") is not False:
        errors.append("work_executed_must_be_false")
    digest = str(receipt.get("dispatch_digest") or "")
    if not digest or digest != _sha(_binding_basis(receipt)):
        errors.append("dispatch_digest")
    ids = receipt.get("clear_condition_ids")
    if not isinstance(ids, list):
        errors.append("clear_condition_ids")
    else:
        try:
            normalized, frozen = freeze_clear_condition_digest(ids)
            if normalized != ids or frozen != receipt.get("CLEAR_CONDITION_DIGEST"):
                errors.append("clear_condition_digest")
        except ValueError:
            errors.append("clear_condition_ids")
    if not isinstance(receipt.get("EXTRA_LIFE_REWARD_ELIGIBILITY"), bool):
        errors.append("extra_life_reward_eligibility")
    errors.extend(f"reseed_anchor:{e}" for e in _anchor_errors(receipt.get("RESEED_ANCHOR")))
    binding = receipt.get("campaign_binding")
    if not isinstance(binding, Mapping) or binding.get("artifact") != BIND_ARTIFACT or binding.get("status") != "BOUND":
        errors.append("campaign_binding")
    return errors


def bind_current_pulse_branch_with_life_policy(
    *,
    binding_kwargs: Mapping[str, Any],
    quest_id: str,
    quest_version: str,
    agent_id: str,
    clear_condition_ids: Sequence[Any],
    reseed_anchor: Mapping[str, Any],
    extra_life_reward_eligibility: bool,
) -> dict[str, Any]:
    """Bind the existing Campaign V3 lease/start/bind transaction to Life Loop V1.

    The wrapped Campaign V3 binder remains the sole coordination transaction.
    This adapter freezes the four life-policy inputs only after that binder returns
    BOUND; it does not execute work or grant scheduler/provider authority.
    """
    conditions, clear_digest = freeze_clear_condition_digest(clear_condition_ids)
    anchor_errors = _anchor_errors(reseed_anchor)
    if not anchor_errors:
        anchor_errors.extend(_anchor_subject_errors(reseed_anchor, str(agent_id), str(quest_id), str(quest_version)))
    if anchor_errors:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_INVALID_LIFE_BINDING",
            "standing": "LIFE_POLICY_NOT_BOUND",
            "failures": [f"RESEED_ANCHOR:{e}" for e in anchor_errors],
            "execution_authority_granted": False,
            "work_executed": False,
            "platform_counter_reset_claimed": False,
        }
    if not isinstance(extra_life_reward_eligibility, bool):
        raise ValueError("extra_life_reward_eligibility must be bool")

    binding = bind_current_pulse_branch_to_loop(**dict(binding_kwargs))
    if binding.get("status") != "BOUND":
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_CAMPAIGN_NOT_BOUND",
            "standing": "LIFE_POLICY_NOT_BOUND",
            "campaign_binding": binding,
            "failures": list(binding.get("failures") or []),
            "holds": list(binding.get("holds") or []),
            "execution_authority_granted": False,
            "work_executed": False,
            "platform_counter_reset_claimed": False,
        }

    game_id = str(binding.get("campaign_id") or binding_kwargs.get("campaign_id") or "").strip()
    world = new_world(game_id)
    enter_agent(world, agent_id, quest_id, quest_version)
    receipt: dict[str, Any] = {
        "artifact": ARTIFACT,
        "status": "BOUND_LIFE_POLICY",
        "standing": "BOUND_LOOP_LIFE_POLICY_NOT_WORK_EXECUTED",
        "campaign_binding": copy.deepcopy(binding),
        "game_id": game_id,
        "agent_id": str(agent_id),
        "quest_id": str(quest_id),
        "quest_version": str(quest_version),
        "LIFE_POLICY": LIFE_POLICY,
        "CLEAR_CONDITION_DIGEST": clear_digest,
        "clear_condition_ids": conditions,
        "RESEED_ANCHOR": copy.deepcopy(dict(reseed_anchor)),
        "RESEED_ANCHOR_DIGEST": _anchor_digest(reseed_anchor),
        "EXTRA_LIFE_REWARD_ELIGIBILITY": extra_life_reward_eligibility,
        "life_policy_source": {
            "repo": ATHENA_LIFE_SOURCE_REPO,
            "head": ATHENA_LIFE_SOURCE_HEAD,
            "blob": ATHENA_LIFE_SOURCE_BLOB,
            "standing": "MERGED_HARDENED_EXACT_SOURCE_TESTED",
        },
        "initial_world": world,
        "execution_authority_granted": False,
        "work_executed": False,
        "platform_counter_reset_claimed": False,
        "next": "EXECUTE_BOUND_LOOP_THEN_RESOLVE_OBSERVED_GTC_OUTCOME",
    }
    receipt["dispatch_digest"] = _sha(receipt)
    return receipt


def _no_life_result(status: str, world: Mapping[str, Any], *, gtc_stop_class: str | None = None, failures: Sequence[str] | None = None) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "status": status,
        "gtc_stop_class": gtc_stop_class,
        "life_consumed": False,
        "logical_global_age_reset": False,
        "world": copy.deepcopy(world),
        "failures": list(failures or []),
        "platform_counter_reset_claimed": False,
    }


def _resolve_life_attempt(
    world: Mapping[str, Any],
    *,
    agent_id: str,
    result_class: str,
    quest_id: str,
    quest_version: str,
    witnesses: Sequence[Any],
    hard_gate_status: str | None,
    clear_condition_values: Sequence[bool] | None,
    reseed_anchor: Mapping[str, Any] | None,
    extra_life_reward: Mapping[str, Any] | None,
    current_git_positions: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    world_errors = _validate_world(world)
    if world_errors:
        return _no_life_result("HOLD_INVALID_WORLD", world, failures=world_errors)
    if agent_id not in world["agents"]:
        return _no_life_result("HOLD_UNKNOWN_AGENT", world, failures=["unknown_agent"])
    next_world = copy.deepcopy(world)
    agent = next_world["agents"][agent_id]
    if quest_id != agent.get("quest_id") or quest_version != agent.get("quest_version"):
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["quest_identity_mismatch"])
    if agent.get("game_over"):
        return _no_life_result("GAME_OVER_OUT_OF_LIVES", next_world)

    if result_class in HOLD_CLASSES:
        next_world["global_game_age"] += 1
        agent["local_loop_age"] += 1
        agent["hold_count"] += 1
        return {
            **_no_life_result(result_class, next_world, gtc_stop_class=result_class),
            "coordinates": _coordinates(next_world, agent, quest_id, quest_version),
        }

    if result_class not in {"CLEAR", "FAIL_CLEAR"}:
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["result_class"])
    witness_values = [str(x).strip() for x in witnesses if str(x).strip()]
    if not witness_values:
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["witness_required"])
    if hard_gate_status not in {"PASS", "FAIL"}:
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["hard_gate_status"])
    if not isinstance(clear_condition_values, Sequence) or not clear_condition_values:
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["clear_conditions_required"])
    if not all(value in (True, False) for value in clear_condition_values):
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["clear_condition_boolean_required"])
    all_clear = all(value is True for value in clear_condition_values)
    if result_class == "CLEAR" and not (all_clear and hard_gate_status == "PASS"):
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["clear_claim_not_satisfied"])
    if result_class == "FAIL_CLEAR" and all_clear and hard_gate_status == "PASS":
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["fail_claim_without_failed_condition"])

    next_world["global_game_age"] += 1
    agent["local_loop_age"] += 1
    if result_class == "CLEAR":
        agent["clear_count"] += 1
        reward_status = "NO_EXTRA_LIFE_REWARD"
        if extra_life_reward is not None:
            ok, reason = _valid_reward(extra_life_reward)
            if not ok:
                reward_status = f"REWARD_REJECTED:{reason}"
            elif extra_life_reward["receipt_id"] in next_world["life_reward_receipts"]:
                reward_status = "REWARD_IDEMPOTENT_REPLAY"
            elif agent["extra_lives_remaining"] >= MAX_EXTRA_LIVES:
                reward_status = "REWARD_CAP_REACHED"
            else:
                agent["extra_lives_remaining"] += 1
                next_world["life_reward_receipts"].append(extra_life_reward["receipt_id"])
                reward_status = "EXTRA_LIFE_EARNED"
        return {
            "artifact": ARTIFACT,
            "status": "CLEARED",
            "life_consumed": False,
            "reward_status": reward_status,
            "logical_global_age_reset": False,
            "world": next_world,
            "coordinates": _coordinates(next_world, agent, quest_id, quest_version),
            "platform_counter_reset_claimed": False,
        }

    agent["fail_count"] += 1
    life_source: str | None = None
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
            "artifact": ARTIFACT,
            "status": "GAME_OVER_OUT_OF_LIVES",
            "life_consumed": life_source is not None,
            "life_source": life_source,
            "logical_global_age_reset": False,
            "world": next_world,
            "coordinates": _coordinates(next_world, agent, quest_id, quest_version),
            "platform_counter_reset_claimed": False,
        }

    anchor_ok, anchor_errors, anchor_digest = _attempt_anchor_status(
        next_world, agent, reseed_anchor, current_git_positions
    )
    if not anchor_ok:
        return {
            "artifact": ARTIFACT,
            "status": "LIFE_CONSUMED_ANCHOR_HOLD",
            "life_consumed": True,
            "life_source": life_source,
            "logical_global_age_reset": False,
            "failures": anchor_errors,
            "anchor_digest": anchor_digest,
            "world": next_world,
            "coordinates": _coordinates(next_world, agent, quest_id, quest_version),
            "platform_counter_reset_claimed": False,
        }

    assert anchor_digest is not None
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
    assert isinstance(reseed_anchor, Mapping)
    return {
        "artifact": ARTIFACT,
        "status": status,
        "life_consumed": True,
        "life_source": life_source,
        "logical_global_age_reset": global_reset,
        "anchor_digest": anchor_digest,
        "anchor_id": reseed_anchor.get("anchor_id"),
        "reseed_epoch": reseed_anchor.get("reseed_epoch"),
        "world": next_world,
        "coordinates": _coordinates(next_world, agent, quest_id, quest_version),
        "platform_counter_reset_claimed": False,
    }


def resolve_observed_gtc_outcome(
    *,
    dispatch_receipt: Mapping[str, Any],
    world: Mapping[str, Any],
    completion: Mapping[str, Any],
    executed: bool,
    hard_gate_status: str | None,
    clear_condition_outcomes: Mapping[str, Any] | None,
    witnesses: Sequence[Any] | None,
    gtc_stop_class: str | None = None,
    reseed_anchor: Mapping[str, Any] | None = None,
    extra_life_reward: Mapping[str, Any] | None = None,
    current_git_positions: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve one observed Campaign V3/Rehydration completion under GTC + Life V1.

    GTC stops/holds never become played failures. A life is consumed only when an
    executed, witnessed completion is coherently classified as FAIL_CLEAR.
    """
    binding_errors = validate_dispatch_binding(dispatch_receipt)
    if binding_errors:
        return _no_life_result("HOLD_INVALID_DISPATCH_BINDING", world, failures=binding_errors)
    if completion.get("observed") is not True:
        return _no_life_result("HOLD_UNOBSERVED_COMPLETION", world, failures=["observed_required"])
    completion_status = str(completion.get("status") or "").upper()
    if completion_status not in COMPLETION_STATES:
        return _no_life_result("HOLD_INVALID_COMPLETION", world, failures=["completion_status"])

    gtc_stop_class = str(gtc_stop_class or "").strip().upper() or None
    if gtc_stop_class is not None:
        if gtc_stop_class not in GTC_CLASSES:
            return _no_life_result("HOLD_INVALID_GTC_CLASS", world, failures=["gtc_stop_class"])
        if gtc_stop_class in GTC_NO_LIFE_STOPS:
            return _no_life_result("GTC_STOP_NO_LIFE", world, gtc_stop_class=gtc_stop_class)
        return _resolve_life_attempt(
            world,
            agent_id=str(dispatch_receipt["agent_id"]),
            result_class=gtc_stop_class,
            quest_id=str(dispatch_receipt["quest_id"]),
            quest_version=str(dispatch_receipt["quest_version"]),
            witnesses=[],
            hard_gate_status=None,
            clear_condition_values=None,
            reseed_anchor=None,
            extra_life_reward=None,
            current_git_positions=None,
        )

    if not executed:
        return _no_life_result("HOLD_UNPLAYED_COMPLETION", world, failures=["executed_required_for_clear_or_fail"])

    frozen_ids = list(dispatch_receipt["clear_condition_ids"])
    if not isinstance(clear_condition_outcomes, Mapping):
        return _no_life_result("HOLD_CLEAR_CONDITION_MISMATCH", world, failures=["clear_condition_outcomes_required"])
    if set(clear_condition_outcomes) != set(frozen_ids):
        return _no_life_result("HOLD_CLEAR_CONDITION_MISMATCH", world, failures=["clear_condition_keyset_mismatch"])
    values = [clear_condition_outcomes[key] for key in frozen_ids]
    if any(value not in (True, False) for value in values):
        return _no_life_result("HOLD_CLEAR_CONDITION_MISMATCH", world, failures=["clear_condition_boolean_required"])
    witness_values = [str(x).strip() for x in (witnesses or []) if str(x).strip()]
    if not witness_values:
        return _no_life_result("HOLD_INVALID_ATTEMPT", world, failures=["witness_required"])

    all_clear = all(value is True for value in values)
    gates_clear = hard_gate_status == "PASS" and all_clear
    gates_failed = hard_gate_status == "FAIL" or not all_clear
    if completion_status == "SUCCEEDED" and gates_clear:
        result_class = "CLEAR"
    elif completion_status in {"PARTIAL", "FAILED", "NO_PROGRESS"} and gates_failed:
        result_class = "FAIL_CLEAR"
    else:
        return _no_life_result(
            "HOLD_COMPLETION_GATE_CONTRADICTION",
            world,
            failures=[f"completion={completion_status};hard_gate={hard_gate_status};all_clear={all_clear}"],
        )

    reward = extra_life_reward
    reward_suppressed = False
    if reward is not None and dispatch_receipt.get("EXTRA_LIFE_REWARD_ELIGIBILITY") is not True:
        reward = None
        reward_suppressed = True

    anchor = reseed_anchor if reseed_anchor is not None else dispatch_receipt.get("RESEED_ANCHOR")
    result = _resolve_life_attempt(
        world,
        agent_id=str(dispatch_receipt["agent_id"]),
        result_class=result_class,
        quest_id=str(dispatch_receipt["quest_id"]),
        quest_version=str(dispatch_receipt["quest_version"]),
        witnesses=witness_values,
        hard_gate_status=hard_gate_status,
        clear_condition_values=values,
        reseed_anchor=anchor,
        extra_life_reward=reward,
        current_git_positions=current_git_positions,
    )
    result["gtc_result_class"] = result_class
    result["completion_status"] = completion_status
    result["CLEAR_CONDITION_DIGEST"] = dispatch_receipt["CLEAR_CONDITION_DIGEST"]
    result["LIFE_POLICY"] = LIFE_POLICY
    if reward_suppressed:
        result["reward_policy_status"] = "REWARD_SUPPRESSED_NOT_ELIGIBLE"
    return result
