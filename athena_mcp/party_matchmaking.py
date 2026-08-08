from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any, Optional

MATCH_VERSION = "PARTY.MATCHMAKING.1"
MATCH_ARTIFACT = "ATHENA.PARTY.MATCHMAKING.V1"

_WEIGHTS = {
    "goal_gap_fit": 0.35,
    "capability_fit": 0.30,
    "capability_novelty": 0.20,
    "capacity_room": 0.15,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _names(values: Optional[Iterable[Any]]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return sorted(out)


def _goal_requirements(goals: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for raw in goals:
        goal_id = str(raw.get("goal_id") or "").strip()
        if goal_id:
            result[goal_id] = _names(raw.get("required_capabilities"))
    return result


def _known_weighted_mean(dimensions: Mapping[str, Optional[float]]) -> float:
    numerator = 0.0
    denominator = 0.0
    for key, value in dimensions.items():
        if value is None:
            continue
        weight = _WEIGHTS[key]
        numerator += weight * value
        denominator += weight
    return numerator / denominator if denominator else 0.0


def rank_party_matches(
    *,
    agent_id: str,
    party_states: Iterable[Mapping[str, Any]],
    capabilities: Optional[Iterable[str]] = None,
    desired_goal_refs: Optional[Iterable[str]] = None,
    limit: int = 10,
    require_shared_frontier: bool = True,
) -> dict[str, Any]:
    """Rank public Party Coordination V1 snapshots without mutating shared state.

    This is a routing helper only. It does not create Message Board presence, form or
    join a party, infer task relation, award XP, or create execution authority.
    """
    agent_id = str(agent_id or "").strip()
    if not agent_id:
        raise ValueError("agent_id must be non-empty")
    limit = int(limit)
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    candidate_capabilities = set(_names(capabilities))
    capability_declared = capabilities is not None
    desired = set(_names(desired_goal_refs))
    desired_declared = desired_goal_refs is not None

    recommendations: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for snapshot in party_states:
        if not isinstance(snapshot, Mapping):
            rejected.append({"party_id": None, "reason": "INVALID_PARTY_STATE"})
            continue
        party = snapshot.get("party")
        members = snapshot.get("members")
        board = snapshot.get("board")
        if not isinstance(party, Mapping) or not isinstance(members, list):
            rejected.append({"party_id": None, "reason": "INVALID_PARTY_STATE"})
            continue

        party_id = str(party.get("party_id") or "").strip()
        if not party_id:
            rejected.append({"party_id": None, "reason": "MISSING_PARTY_ID"})
            continue
        if str(party.get("status") or "") != "OPEN":
            rejected.append({"party_id": party_id, "reason": "PARTY_NOT_OPEN"})
            continue

        member_ids = {
            str(row.get("agent_id") or "").strip()
            for row in members
            if isinstance(row, Mapping) and str(row.get("agent_id") or "").strip()
        }
        if agent_id in member_ids:
            rejected.append({"party_id": party_id, "reason": "ALREADY_MEMBER"})
            continue
        try:
            capacity = int(party.get("capacity") or 0)
        except (TypeError, ValueError):
            capacity = 0
        if capacity <= 0 or len(member_ids) >= capacity:
            rejected.append({"party_id": party_id, "reason": "PARTY_FULL"})
            continue

        shared_frontier_verified = bool(
            isinstance(board, Mapping) and board.get("shared_frontier_verified")
        )
        if require_shared_frontier and not shared_frontier_verified:
            rejected.append({"party_id": party_id, "reason": "SHARED_FRONTIER_HOLD"})
            continue

        requirements = _goal_requirements(party.get("goals") or [])
        assigned = {
            str(goal)
            for row in members
            if isinstance(row, Mapping)
            for goal in (row.get("goal_refs") or [])
            if str(goal) in requirements
        }
        uncovered = sorted(set(requirements) - assigned)
        desired_in_party = sorted(desired & set(requirements))

        if desired_declared:
            target_goals = sorted(desired & set(uncovered))
            goal_gap_fit: Optional[float] = len(target_goals) / len(desired) if desired else 0.0
        else:
            target_goals = uncovered
            goal_gap_fit = len(uncovered) / len(requirements) if requirements else 0.0

        required_for_target = {
            capability
            for goal_id in target_goals
            for capability in requirements.get(goal_id, [])
        }
        if capability_declared:
            capability_fit: Optional[float] = (
                len(required_for_target & candidate_capabilities) / len(required_for_target)
                if required_for_target
                else 1.0
            )
        else:
            capability_fit = None

        existing_capabilities = {
            str(capability).strip()
            for row in members
            if isinstance(row, Mapping)
            for capability in (row.get("capabilities") or [])
            if str(capability).strip()
        }
        if capability_declared:
            capability_novelty: Optional[float] = (
                len(candidate_capabilities - existing_capabilities) / len(candidate_capabilities)
                if candidate_capabilities
                else 0.0
            )
        else:
            capability_novelty = None

        capacity_room = (capacity - len(member_ids)) / capacity
        dimensions = {
            "goal_gap_fit": round(goal_gap_fit, 9),
            "capability_fit": round(capability_fit, 9) if capability_fit is not None else None,
            "capability_novelty": (
                round(capability_novelty, 9) if capability_novelty is not None else None
            ),
            "capacity_room": round(capacity_room, 9),
        }
        score = round(_known_weighted_mean(dimensions), 9)

        suggested_goal_refs = []
        for goal_id in target_goals:
            required = set(requirements.get(goal_id, []))
            if not capability_declared or not required or required.issubset(candidate_capabilities):
                suggested_goal_refs.append(goal_id)

        recommendation = {
            "party_id": party_id,
            "score": score,
            "dimensions": dimensions,
            "dimension_standing": {
                key: "KNOWN" if value is not None else "UNKNOWN"
                for key, value in dimensions.items()
            },
            "uncovered_goal_refs": uncovered,
            "desired_goal_refs_in_party": desired_in_party,
            "suggested_goal_refs": sorted(suggested_goal_refs),
            "remaining_capacity": capacity - len(member_ids),
            "shared_frontier_verified": shared_frontier_verified,
            "next": {
                "tool": "athena_party_join",
                "requires_explicit_task_relation": True,
                "auto_join": False,
            },
            "execution_authority": False,
            "xp_authority": False,
            "law": (
                "PARTY_MATCH != PARTY_JOIN; MATCH_SCORE is routing evidence only; "
                "UNKNOWN capability state is not zero capability."
            ),
        }
        recommendation["match_digest"] = _digest(recommendation)
        recommendations.append(recommendation)

    recommendations.sort(key=lambda row: (-row["score"], row["party_id"]))
    rejected.sort(key=lambda row: (str(row.get("party_id") or ""), row["reason"]))
    result = {
        "artifact": MATCH_ARTIFACT,
        "version": MATCH_VERSION,
        "agent_id": agent_id,
        "status": "OK" if recommendations else "NO_MATCH",
        "recommendations": recommendations[:limit],
        "rejected": rejected,
        "weights": dict(_WEIGHTS),
        "require_shared_frontier": bool(require_shared_frontier),
        "execution_authority": False,
        "xp_authority": False,
        "auto_join": False,
        "epistemic_boundary": (
            "Deterministic routing over supplied public party snapshots. It does not prove outcome gain, "
            "capability truth, task compatibility, or authority."
        ),
    }
    result["result_digest"] = _digest(result)
    return result
