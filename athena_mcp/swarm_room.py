from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping


SWARM_ROOM_VERSION = "ATHENA.SWARM.ROOM.1"
SWARM_ROOM_RESOURCE_URI = "athena://swarm-room/v1"
ROOM_DETAILS_PREFIX = "ATHENA_SWARM_ROOM_JSON:"

HORIZONS = ("W0", "W1", "W2")
QUEUE_SLOTS = {"W0": "Q1", "W1": "Q2", "W2": "Q3"}
DEFAULT_HORIZON_WEIGHTS = {"W0": 600, "W1": 250, "W2": 150}
JOB_FAMILIES = (
    "GIT_ENGINEERING",
    "MATH_MINING",
    "MYTH_MINING",
    "NAVIGATION_ALGORITHMS",
    "LIMITS_RESEARCH",
    "DRIVE_DISTILLATION",
    "TOOL_CAPACITY",
    "ALCHEMIC_TOOL_BUILDING",
    "META_OBSERVATION",
)
RESOURCE_DIMENSIONS = ("tool_calls", "tokens", "wall_seconds", "write_ops", "api_calls")
SCORE_FIELDS = (
    "dependency_unlock",
    "downstream_reach",
    "verified_gain",
    "information_gain",
    "evidence_gain",
    "urgency",
    "reversibility",
    "risk",
    "estimated_cost",
)

LAWS = (
    "MESSAGE_BOARD_CAS_IS_SOLE_PRESENCE_AND_CLAIM_AUTHORITY",
    "SCHEDULED_WAKE != WORKER",
    "PLAN != CLAIM != EXECUTION != RETURN",
    "MATCH != CLAIM",
    "ROUTE != CONSUMPTION",
    "ACK != CLAIM",
    "PARENT_CANNOT_CLAIM_OR_RETURN_FOR_SIBLING",
    "CALLER_AGENT_ID_REQUIRES_HOST_AUTHENTICATION_FOR_STRONG_SELF_OWNERSHIP",
    "NO_READY_QUESTS => NO_ASSIGNMENT",
    "UNKNOWN_COST != ZERO_COST",
    "ONE_WORKER != THREE_CONCURRENT_WAVES",
    "RUNNING_VALID_CLAIMS_ARE_NOT_PREEMPTED_BY_REALLOCATION",
    "LEASE_EXPIRY != COMPLETION",
    "SELF_PLAY_PROPOSAL != PRODUCTION_POLICY",
    "DONE_REQUIRES_ACCEPTANCE_AND_EVIDENCE",
    "SIGN_OUT_PRESERVES_FAILURES_AND_HISTORY",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def contract() -> dict[str, Any]:
    core = {
        "version": SWARM_ROOM_VERSION,
        "entry_sequence": [
            "COMPILE_CURRENT_MAXDEV_PROMPT",
            "READ_SHARED_MESSAGE_BOARD",
            "VALIDATE_REAL_QUESTS_AND_RESOURCES",
            "SELECT_ONE_SELF_OWNED_LANE",
            "ATOMIC_ROOM_ENTER_AND_CLAIM",
        ],
        "exit_sequence": [
            "REVALIDATE_HEAD_PROMPT_AND_OWN_CLAIM",
            "VERIFY_ACCEPTANCE_OR_PRESERVE_FAILURE",
            "ATOMIC_ROOM_RETURN_AND_RELEASE",
        ],
        "horizons": {
            "W0": "IMMEDIATE_DELIVERY_Q1",
            "W1": "MIDDLE_ENGINEERING_Q2",
            "W2": "RECURSIVE_META_OBSERVATION_Q3",
        },
        "default_horizon_weights": DEFAULT_HORIZON_WEIGHTS,
        "job_families": list(JOB_FAMILIES),
        "resource_dimensions": list(RESOURCE_DIMENSIONS),
        "score_fields": list(SCORE_FIELDS),
        "laws": list(LAWS),
        "authority": "NONE_BEYOND_SELF_OWNED_MESSAGE_BOARD_CAS",
        "identity_ceiling": "agent_id is caller-asserted until a host-authenticated context binding is supplied",
    }
    return {**core, "room_contract_digest": digest(core)}


def encode_details(value: Mapping[str, Any]) -> str:
    return ROOM_DETAILS_PREFIX + canonical_json(dict(value))


def decode_details(value: Any) -> dict[str, Any] | None:
    text = str(value or "")
    if not text.startswith(ROOM_DETAILS_PREFIX):
        return None
    try:
        parsed = json.loads(text[len(ROOM_DETAILS_PREFIX) :])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) and parsed.get("room_protocol") == SWARM_ROOM_VERSION else None


def _resource_errors(value: Any, label: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label}_NOT_OBJECT"]
    errors = []
    for name in RESOURCE_DIMENSIONS:
        raw = value.get(name)
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            errors.append(f"{label}_{name}_UNBOUND")
    sinks = value.get("shared_sinks")
    if not isinstance(sinks, list) or any(not _nonblank(item) for item in sinks):
        errors.append(f"{label}_shared_sinks_UNBOUND")
    return errors


def validate_quest(raw: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(raw, Mapping):
        return None, ["QUEST_NOT_OBJECT"]
    quest = dict(raw)
    errors: list[str] = []
    for field in ("quest_id", "title", "work_key", "integration_owner"):
        if not _nonblank(quest.get(field)):
            errors.append(f"MISSING_{field.upper()}")
    horizon = str(quest.get("horizon") or "").upper()
    if horizon not in HORIZONS:
        errors.append("INVALID_HORIZON")
    if quest.get("queue_slot") != QUEUE_SLOTS.get(horizon):
        errors.append("QUEUE_SLOT_HORIZON_MISMATCH")
    family = str(quest.get("job_family") or "").upper()
    if family not in JOB_FAMILIES:
        errors.append("INVALID_JOB_FAMILY")
    for field in ("targets", "required_capabilities", "source_refs", "acceptance", "dependency_refs", "satisfied_dependency_refs", "allowed_mutations", "forbidden_claims"):
        value = quest.get(field)
        if not isinstance(value, list) or any(not _nonblank(item) for item in value):
            errors.append(f"INVALID_{field.upper()}")
    for field in ("targets", "source_refs", "acceptance", "forbidden_claims"):
        if isinstance(quest.get(field), list) and not quest[field]:
            errors.append(f"EMPTY_{field.upper()}")
    dependencies = set(_names(quest.get("dependency_refs")))
    satisfied = set(_names(quest.get("satisfied_dependency_refs")))
    if not dependencies.issubset(satisfied):
        errors.append("DEPENDENCIES_UNSATISFIED")
    errors.extend(_resource_errors(quest.get("resource_upper_bound"), "QUEST_RESOURCE"))
    scores = quest.get("scores")
    if not isinstance(scores, Mapping):
        errors.append("SCORES_UNBOUND")
    else:
        for field in SCORE_FIELDS:
            value = scores.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 5:
                errors.append(f"INVALID_SCORE_{field.upper()}")
    if quest.get("admitted") is not True:
        errors.append("QUEST_NOT_ADMITTED")
    if errors:
        return None, sorted(set(errors))
    normalized = {
        **quest,
        "quest_id": str(quest["quest_id"]).strip(),
        "title": str(quest["title"]).strip(),
        "work_key": str(quest["work_key"]).strip(),
        "integration_owner": str(quest["integration_owner"]).strip(),
        "horizon": horizon,
        "queue_slot": QUEUE_SLOTS[horizon],
        "job_family": family,
        "targets": _names(quest["targets"]),
        "required_capabilities": _names(quest["required_capabilities"]),
        "source_refs": _names(quest["source_refs"]),
        "acceptance": _names(quest["acceptance"]),
        "dependency_refs": _names(quest["dependency_refs"]),
        "satisfied_dependency_refs": _names(quest["satisfied_dependency_refs"]),
        "allowed_mutations": _names(quest["allowed_mutations"]),
        "forbidden_claims": _names(quest["forbidden_claims"]),
        "resource_upper_bound": {
            **{name: int(quest["resource_upper_bound"][name]) for name in RESOURCE_DIMENSIONS},
            "shared_sinks": _names(quest["resource_upper_bound"]["shared_sinks"]),
        },
        "scores": {name: int(scores[name]) for name in SCORE_FIELDS},
    }
    normalized["quest_digest"] = digest({key: value for key, value in normalized.items() if key != "quest_digest"})
    return normalized, []


def validate_quests(values: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(values, list):
        return [], [{"quest_id": None, "reasons": ["QUESTS_NOT_ARRAY"]}]
    ready, held, seen = [], [], set()
    for raw in values:
        quest, errors = validate_quest(raw)
        quest_id = str(raw.get("quest_id") or "") if isinstance(raw, Mapping) else None
        if quest_id in seen and quest_id:
            errors = sorted(set(errors + ["DUPLICATE_QUEST_ID"]))
            quest = None
        if quest_id:
            seen.add(quest_id)
        if errors:
            held.append({"quest_id": quest_id or None, "reasons": errors})
        else:
            ready.append(quest)
    return sorted(ready, key=lambda row: row["quest_id"]), held


def _score(quest: Mapping[str, Any]) -> int:
    score = quest["scores"]
    return (
        5 * score["dependency_unlock"]
        + 4 * score["downstream_reach"]
        + 4 * score["verified_gain"]
        + 3 * score["information_gain"]
        + 3 * score["evidence_gain"]
        + 2 * score["urgency"]
        + 2 * score["reversibility"]
        - 4 * score["risk"]
        - 2 * score["estimated_cost"]
    )


def _percentages(counts: Mapping[str, int], total: int) -> dict[str, dict[str, int]]:
    keys = sorted(counts)
    if total <= 0:
        return {key: {"workers": int(counts[key]), "basis_points": 0} for key in keys}
    floors = {key: int(counts[key]) * 10000 // total for key in keys}
    residues = sorted(
        keys,
        key=lambda key: (-(int(counts[key]) * 10000 % total), key),
    )
    for key in residues[: 10000 - sum(floors.values())]:
        floors[key] += 1
    return {key: {"workers": int(counts[key]), "basis_points": floors[key]} for key in keys}


def target_horizon_counts(population: int, ready_horizons: Iterable[str], weights: Mapping[str, int] | None = None) -> dict[str, int]:
    population = max(0, int(population))
    active = [name for name in HORIZONS if name in set(ready_horizons)]
    result = {name: 0 for name in HORIZONS}
    if not active or not population:
        return result
    policy = {name: int((weights or DEFAULT_HORIZON_WEIGHTS).get(name, 0)) for name in active}
    if any(value <= 0 for value in policy.values()):
        raise ValueError("horizon weights must be positive for every ready horizon")
    remaining = population
    if population >= len(active):
        for name in active:
            result[name] = 1
        remaining -= len(active)
    total_weight = sum(policy.values())
    raw = {name: remaining * policy[name] for name in active}
    for name in active:
        result[name] += raw[name] // total_weight
    leftover = population - sum(result.values())
    order = sorted(active, key=lambda name: (-(raw[name] % total_weight), HORIZONS.index(name)))
    for name in order[:leftover]:
        result[name] += 1
    return result


def _active_room_profiles(active_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    profiles = []
    for row in active_rows:
        details = decode_details(row.get("details"))
        if details:
            profiles.append({"agent_id": row.get("agent_id"), "claim_id": row.get("claim_id"), **details})
    return profiles


def _budget_feasible(quest: Mapping[str, Any], active_profiles: Iterable[Mapping[str, Any]], room_budget: Any, protected_reserve: Any) -> list[str]:
    errors = _resource_errors(room_budget, "ROOM_BUDGET") + _resource_errors(protected_reserve, "PROTECTED_RESERVE")
    if errors:
        return sorted(set(errors))
    active_profiles = list(active_profiles)
    room_budget_digest = digest(room_budget)
    protected_reserve_digest = digest(protected_reserve)
    if any(profile.get("room_budget_digest") != room_budget_digest for profile in active_profiles):
        errors.append("ROOM_BUDGET_POLICY_DRIFT_HOLD")
    if any(profile.get("protected_reserve_digest") != protected_reserve_digest for profile in active_profiles):
        errors.append("PROTECTED_RESERVE_POLICY_DRIFT_HOLD")
    for name in RESOURCE_DIMENSIONS:
        used = sum(int((profile.get("resource_upper_bound") or {}).get(name, 0)) for profile in active_profiles)
        need = int(quest["resource_upper_bound"][name])
        if used + need + int(protected_reserve[name]) > int(room_budget[name]):
            errors.append(f"RESOURCE_HOLD_{name}")
    active_sinks = {
        sink
        for profile in active_profiles
        for sink in _names((profile.get("resource_upper_bound") or {}).get("shared_sinks"))
    }
    collisions = sorted(active_sinks & set(quest["resource_upper_bound"]["shared_sinks"]))
    if collisions:
        errors.append("SHARED_SINK_HOLD:" + ",".join(collisions))
    return sorted(set(errors))


def select_quest(
    *,
    active_rows: Iterable[Mapping[str, Any]],
    quests: Any,
    capabilities: Iterable[str],
    room_budget: Any,
    protected_reserve: Any,
    horizon_weights: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    ready, held = validate_quests(quests)
    active_rows = list(active_rows)
    profiles = _active_room_profiles(active_rows)
    capabilities = set(_names(capabilities))
    try:
        policy = {name: int((horizon_weights or DEFAULT_HORIZON_WEIGHTS).get(name, 0)) for name in HORIZONS}
    except (AttributeError, TypeError, ValueError):
        policy = {name: 0 for name in HORIZONS}
    policy_errors = []
    if any(value <= 0 for value in policy.values()):
        policy_errors.append("HORIZON_POLICY_UNBOUND")
    policy_digest = digest(policy)
    if any(profile.get("horizon_policy_digest") != policy_digest for profile in profiles):
        policy_errors.append("HORIZON_POLICY_DRIFT_HOLD")
    feasible = []
    for quest in ready:
        reasons = list(policy_errors)
        missing = sorted(set(quest["required_capabilities"]) - capabilities)
        if missing:
            reasons.append("MISSING_CAPABILITY:" + ",".join(missing))
        reasons.extend(_budget_feasible(quest, profiles, room_budget, protected_reserve))
        if reasons:
            held.append({"quest_id": quest["quest_id"], "reasons": sorted(set(reasons))})
        else:
            feasible.append(quest)
    if not feasible:
        return {
            "status": "NO_READY_QUESTS",
            "selected": None,
            "ready_count": 0,
            "held": sorted(held, key=lambda row: str(row.get("quest_id"))),
            "authority": "NONE",
        }
    existing = Counter(profile.get("horizon") for profile in profiles if profile.get("horizon") in HORIZONS)
    ready_horizons = {quest["horizon"] for quest in feasible}
    target = target_horizon_counts(len(profiles) + 1, ready_horizons, policy)
    missing_horizons = [name for name in HORIZONS if name in ready_horizons and target[name] > existing[name]]
    pool = [quest for quest in feasible if quest["horizon"] in missing_horizons] or feasible
    selected = sorted(pool, key=lambda quest: (-_score(quest), HORIZONS.index(quest["horizon"]), quest["quest_id"]))[0]
    return {
        "status": "QUEST_SELECTED",
        "selected": selected,
        "selected_score": _score(selected),
        "ready_count": len(feasible),
        "held": sorted(held, key=lambda row: str(row.get("quest_id"))),
        "current_horizon_counts": {name: existing[name] for name in HORIZONS},
        "target_horizon_counts_after_entry": target,
        "authority": "SELF_CLAIM_REQUIRED",
    }


def compile_pulse(snapshot: Mapping[str, Any], quests: Any = None, horizon_weights: Mapping[str, int] | None = None) -> dict[str, Any]:
    active = list(snapshot.get("active") or [])
    profiles = _active_room_profiles(active)
    external = len(active) - len(profiles)
    horizon_counts = Counter(profile.get("horizon") for profile in profiles)
    family_counts = Counter(profile.get("job_family") for profile in profiles)
    if external:
        horizon_counts["EXTERNAL_UNCLASSIFIED"] += external
        family_counts["EXTERNAL_UNCLASSIFIED"] += external
    for name in HORIZONS:
        horizon_counts.setdefault(name, 0)
    for name in JOB_FAMILIES:
        family_counts.setdefault(name, 0)
    ready, held = validate_quests(quests if quests is not None else [])
    ready_horizons = {quest["horizon"] for quest in ready}
    target = target_horizon_counts(len(active), ready_horizons, horizon_weights) if ready_horizons else {name: 0 for name in HORIZONS}
    return {
        "artifact": "ATHENA.SWARM.ROOM.PULSE.1",
        "status": snapshot.get("status"),
        "git_head": snapshot.get("git_head"),
        "observed_active_workers": len(active),
        "observed_room_workers": len(profiles),
        "external_unclassified_workers": external,
        "population_source": "NONEXPIRED_MESSAGE_BOARD_PRESENCE_ONLY",
        "actual_horizon_population": _percentages(horizon_counts, len(active)),
        "actual_job_population": _percentages(family_counts, len(active)),
        "ready_quest_count": len(ready),
        "held_quests": held,
        "advisory_target_for_observed_population": target,
        "waves": [
            {"wave": "IMMEDIATE", "horizon": "W0", "queue_slot": "Q1", "workers": horizon_counts["W0"]},
            {"wave": "MIDDLE", "horizon": "W1", "queue_slot": "Q2", "workers": horizon_counts["W1"]},
            {"wave": "RECURSIVE_META", "horizon": "W2", "queue_slot": "Q3", "workers": horizon_counts["W2"]},
        ],
        "observed_concurrency": "UNKNOWN_UNLESS_SEPARATELY_ATTESTED",
        "scheduler_authority": False,
        "execution_authority": False,
        "claim_authority": False,
        "laws": list(LAWS),
    }


def compile_shadow(snapshot: Mapping[str, Any], quests: Any, variants: Any) -> dict[str, Any]:
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants must be a nonempty array")
    ready, held = validate_quests(quests)
    ready_horizons = {quest["horizon"] for quest in ready}
    population = len(snapshot.get("active") or [])
    outputs = []
    seen = set()
    for variant in variants:
        if not isinstance(variant, Mapping) or not _nonblank(variant.get("variant_id")):
            raise ValueError("every variant requires variant_id")
        variant_id = str(variant["variant_id"]).strip()
        if variant_id in seen:
            raise ValueError("duplicate variant_id")
        seen.add(variant_id)
        weights = variant.get("horizon_weights")
        if not isinstance(weights, Mapping) or set(weights) != set(HORIZONS):
            raise ValueError("variant horizon_weights must bind W0, W1 and W2")
        counts = target_horizon_counts(population, ready_horizons, weights)
        outputs.append({"variant_id": variant_id, "horizon_weights": {name: int(weights[name]) for name in HORIZONS}, "counterfactual_seats": counts})
    return {
        "artifact": "ATHENA.SWARM.ROOM.SHADOW.1",
        "status": "COUNTERFACTUAL_ONLY",
        "git_head": snapshot.get("git_head"),
        "population": population,
        "ready_quest_count": len(ready),
        "held_quests": held,
        "variants": outputs,
        "winner": None,
        "production_credit": False,
        "mutation_performed": False,
        "promotion_authority": False,
        "evidence_ceiling": "STRUCTURAL_COUNTERFACTUAL_NOT_OBSERVED_OUTCOME",
    }


def room_profile(*, quest: Mapping[str, Any], capabilities: Iterable[str], prompt: Mapping[str, Any], room_contract_digest: str, room_budget: Mapping[str, Any], protected_reserve: Mapping[str, Any], horizon_weights: Mapping[str, int] | None = None) -> dict[str, Any]:
    policy = {name: int((horizon_weights or DEFAULT_HORIZON_WEIGHTS)[name]) for name in HORIZONS}
    return {
        "room_protocol": SWARM_ROOM_VERSION,
        "room_contract_digest": room_contract_digest,
        "quest_id": quest["quest_id"],
        "quest_digest": quest["quest_digest"],
        "horizon": quest["horizon"],
        "queue_slot": quest["queue_slot"],
        "job_family": quest["job_family"],
        "capabilities": _names(capabilities),
        "acceptance": list(quest["acceptance"]),
        "source_refs": list(quest["source_refs"]),
        "allowed_mutations": list(quest["allowed_mutations"]),
        "forbidden_claims": list(quest["forbidden_claims"]),
        "integration_owner": quest["integration_owner"],
        "resource_upper_bound": dict(quest["resource_upper_bound"]),
        "room_budget_digest": digest(room_budget),
        "protected_reserve_digest": digest(protected_reserve),
        "horizon_policy_digest": digest(policy),
        "prompt_profile": prompt.get("profile"),
        "prompt_stack_digest": prompt.get("prompt_stack_digest"),
        "prompt_git_head": prompt.get("git_head"),
        "selected_modules": list(prompt.get("selected_modules") or []),
        "selected_overlays": list(prompt.get("selected_overlays") or []),
        "claim_ceiling": "SELF_OWNED_COORDINATION_CLAIM_ONLY",
    }
