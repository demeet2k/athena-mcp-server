from __future__ import annotations

import copy
import math
from collections import defaultdict, deque
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .nexus4d_types import (
    EVIDENCE_DIMENSIONS, EVENT_TYPES, LIFECYCLE_RANK, PRESSURE_CHANNELS, VERSION,
    _authority_checks, _blank_evidence, _blank_pressure, _canonical, _clean_id, _digest,
    _eval_predicate, _evidence_meets, _get_path, _sets_intersect, _state_digest,
)


def _index_spec(spec: Mapping[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, List[str]], Dict[str, List[str]]]:
    goals = {item["id"]: item for item in spec["goals"]}
    nodes = {item["id"]: item for item in spec["nodes"]}
    producers: Dict[str, List[str]] = {goal_id: [] for goal_id in goals}
    dependents: Dict[str, List[str]] = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        for goal_id in node["goals"]:
            producers[goal_id].append(node["id"])
        for dependency in node["requires"]:
            dependents[dependency].append(node["id"])
    for value in producers.values():
        value.sort()
    for value in dependents.values():
        value.sort()
    return goals, nodes, producers, dependents


def _empty_node_state(node: Mapping[str, Any], revision: int = 0) -> Dict[str, Any]:
    return {
        "stage": "OPEN",
        "attempt": 0,
        "claim": None,
        "candidate": None,
        "evidence": _blank_evidence(),
        "evidence_refs": [],
        "consumer_receipts": [],
        "outcome_receipts": [],
        "holds": [],
        "queue_depth": 0,
        "capacity": int(node["capacity"]),
        "last_event_seq": revision,
        "wait_since_revision": revision,
    }


def _new_snapshot(spec: Mapping[str, Any]) -> Dict[str, Any]:
    nodes = {item["id"]: item for item in spec["nodes"]}
    return {
        "version": VERSION,
        "revision": 0,
        "topology_epoch": 1,
        "state": copy.deepcopy(spec["initial_state"]),
        "authorities": list(spec["authorities"]),
        "node_state": {node_id: _empty_node_state(nodes[node_id], 0) for node_id in sorted(nodes)},
        "retired_node_state": {},
        "contradictions": [],
        "topology_candidates": {},
        "last_changed_paths": [],
        "last_event_id": None,
    }


def _goal_statuses(spec: Mapping[str, Any], snapshot: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    goals, nodes, producers, _ = _index_spec(spec)
    result: Dict[str, Dict[str, Any]] = {}
    for goal_id, goal in goals.items():
        predicate = _eval_predicate(goal["predicate"], snapshot["state"])
        producer_states = [(node_id, snapshot["node_state"][node_id]) for node_id in producers[goal_id]]
        evidence_ok = not any(goal["evidence_threshold"].values())
        evidence_source = None
        if not evidence_ok:
            for node_id, node_state in producer_states:
                if _dependency_reached(node_state, "VERIFIED") and _evidence_meets(node_state["evidence"], goal["evidence_threshold"]):
                    evidence_ok = True
                    evidence_source = node_id
                    break
        consumed_ok = goal["consumer"] is None
        outcome_ok = not goal["require_outcome"]
        if producer_states:
            if goal["consumer"] is not None:
                consumed_ok = any(any(receipt.get("consumer") == goal["consumer"] for receipt in state["consumer_receipts"]) for _, state in producer_states)
            if goal["require_outcome"]:
                outcome_ok = any(bool(state["outcome_receipts"]) for _, state in producer_states)
        freshness_ok = True
        if goal["freshness_keys"]:
            freshness_ok = all(_get_path(snapshot["state"], path)[0] for path in goal["freshness_keys"])
        closed = predicate["passed"] and evidence_ok and consumed_ok and outcome_ok and freshness_ok
        deficits = []
        if not predicate["passed"]:
            deficits.append("GOAL_RESIDUAL")
        if not evidence_ok:
            deficits.append("EVIDENCE")
        if not consumed_ok:
            deficits.append("CONSUMPTION")
        if not outcome_ok:
            deficits.append("OUTCOME")
        if not freshness_ok:
            deficits.append("FRESHNESS")
        result[goal_id] = {
            "goal_id": goal_id,
            "closed": closed,
            "predicate": predicate,
            "residual": float(predicate["residual"]),
            "known": bool(predicate["known"]),
            "evidence_ok": evidence_ok,
            "evidence_source": evidence_source,
            "consumed_ok": consumed_ok,
            "outcome_ok": outcome_ok,
            "freshness_ok": freshness_ok,
            "deficits": deficits,
            "producers": producers[goal_id],
        }
    return result


def _invariant_statuses(spec: Mapping[str, Any], snapshot: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [{"id": item["id"], **_eval_predicate(item["predicate"], snapshot["state"])} for item in spec["hard_invariants"]]


def _dependency_reached(node_state: Mapping[str, Any], required_stage: str) -> bool:
    return LIFECYCLE_RANK.get(str(node_state.get("stage")), -1) >= LIFECYCLE_RANK[required_stage] and node_state.get("stage") not in {"HELD", "INVALIDATED"}


def _active_claims(snapshot: Mapping[str, Any], revision: int) -> List[Tuple[str, Mapping[str, Any]]]:
    active = []
    for node_id, state in snapshot["node_state"].items():
        claim = state.get("claim")
        if claim and int(claim.get("lease_until_revision", revision)) >= revision and state.get("stage") == "CLAIMED":
            active.append((node_id, claim))
    return active


def _node_readiness(spec: Mapping[str, Any], snapshot: Mapping[str, Any], demanded: set[str], authority_states: Mapping[str, Mapping[str, Any]] | None = None) -> Dict[str, Dict[str, Any]]:
    _, nodes, _, _ = _index_spec(spec)
    authorities = set(snapshot["authorities"])
    active = _active_claims(snapshot, int(snapshot["revision"]))
    result: Dict[str, Dict[str, Any]] = {}
    for node_id, node in nodes.items():
        state = snapshot["node_state"][node_id]
        reasons: List[str] = []
        if node_id not in demanded:
            reasons.append("NO_BACKWARD_DEMAND")
        if state["stage"] in {"COMMITTED", "CONSUMED", "OUTCOME_OBSERVED"}:
            reasons.append("ALREADY_PRODUCED")
        if state["stage"] == "HELD":
            reasons.append("HELD")
        if state["stage"] == "CLAIMED":
            claim = state.get("claim") or {}
            if int(claim.get("lease_until_revision", snapshot["revision"])) >= int(snapshot["revision"]):
                reasons.append("ALREADY_CLAIMED")
        missing_dependencies = [dep for dep in node["requires"] if not _dependency_reached(snapshot["node_state"][dep], node["dependency_stage"])]
        if missing_dependencies:
            reasons.append("DEPENDENCIES_NOT_READY")
        state_checks = [_eval_predicate(predicate, snapshot["state"]) for predicate in node["required_state"]]
        if any(not item["passed"] for item in state_checks):
            reasons.append("STATE_PRECONDITION")
        missing_authority = sorted(set(node["required_authorities"]) - authorities)
        if missing_authority:
            reasons.append("AUTHORITY_SCOPE")
        authority_claim_checks = _authority_checks(node["required_authority_claims"], authority_states)
        if any(not item["passed"] for item in authority_claim_checks):
            reasons.append("CANONICAL_AUTHORITY")
        missing_freshness = [path for path in node["freshness_keys"] if not _get_path(snapshot["state"], path)[0]]
        if missing_freshness:
            reasons.append("FRESHNESS")
        capacity = int(state.get("capacity", node["capacity"]))
        claimed_count = sum(1 for active_node, _ in active if active_node == node_id)
        if claimed_count >= capacity:
            reasons.append("CAPACITY")
        queue_depth = int(state.get("queue_depth", 0))
        if queue_depth >= int(node["queue_limit"]):
            reasons.append("BACKPRESSURE")
        conflicting_claims = []
        for other_id, claim in active:
            if other_id == node_id:
                continue
            if _sets_intersect(node["writeset"], claim.get("writeset") or []):
                conflicting_claims.append(str(claim.get("claim_id") or other_id))
        if conflicting_claims:
            reasons.append("WRITE_CONFLICT")
        result[node_id] = {
            "node_id": node_id,
            "ready": not reasons,
            "reasons": reasons,
            "missing_dependencies": missing_dependencies,
            "state_checks": state_checks,
            "missing_authority": missing_authority,
            "authority_claim_checks": authority_claim_checks,
            "missing_freshness": missing_freshness,
            "conflicting_claims": sorted(conflicting_claims),
            "readset_digest": _state_digest(snapshot["state"], node["readset"]),
        }
    return result


def _demand_and_pressure(spec: Mapping[str, Any], snapshot: Mapping[str, Any], goal_statuses: Mapping[str, Mapping[str, Any]]) -> Tuple[set[str], Dict[str, Dict[str, float]], List[Dict[str, Any]]]:
    goals, nodes, producers, _ = _index_spec(spec)
    demanded: set[str] = set()
    per_node_goal: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(dict)
    obligations: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for goal_id in sorted(goals):
        goal = goals[goal_id]
        status = goal_statuses[goal_id]
        if status["closed"]:
            obligations[(goal_id, "ROOT")] = {
                "obligation_id": _digest("NXOBL", [goal_id, "ROOT"]),
                "root_goal_id": goal_id,
                "node_id": None,
                "parent_ids": [],
                "closure_rule": "TERMINAL_PREDICATE_AND_EVIDENCE_AND_CONSUMPTION_AND_OUTCOME",
                "status": "CLOSED",
                "pressure": _blank_pressure(),
            }
            continue
        residual_mass = max(1.0 if not status["known"] else float(status["residual"]), 1.0 if status["deficits"] else 0.0)
        base = float(goal["weight"]) * float(goal["consequence"]) * residual_mass
        root_pressure = _blank_pressure()
        if "GOAL_RESIDUAL" in status["deficits"]:
            root_pressure["goal"] = base
        if "EVIDENCE" in status["deficits"]:
            root_pressure["evidence"] = base
        if "CONSUMPTION" in status["deficits"]:
            root_pressure["integration"] = base
        if "OUTCOME" in status["deficits"]:
            root_pressure["outcome"] = base
        if "FRESHNESS" in status["deficits"]:
            root_pressure["freshness"] = base
        if not status["known"]:
            root_pressure["uncertainty"] = base
        obligations[(goal_id, "ROOT")] = {
            "obligation_id": _digest("NXOBL", [goal_id, "ROOT"]),
            "root_goal_id": goal_id,
            "node_id": None,
            "parent_ids": [],
            "closure_rule": "TERMINAL_PREDICATE_AND_EVIDENCE_AND_CONSUMPTION_AND_OUTCOME",
            "status": "OPEN",
            "pressure": root_pressure,
        }
        queue = deque((node_id, None) for node_id in producers[goal_id])
        visited: set[str] = set()
        while queue:
            node_id, parent_node = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)
            demanded.add(node_id)
            node_state = snapshot["node_state"][node_id]
            contribution = dict(root_pressure)
            if node_state["stage"] == "COMMITTED":
                contribution = _blank_pressure()
                contribution["integration"] = base
            elif node_state["stage"] == "CONSUMED" and (goal["require_outcome"] or nodes[node_id]["require_outcome"]):
                contribution = _blank_pressure()
                contribution["outcome"] = base
            elif node_state["stage"] == "VERIFIED":
                contribution = _blank_pressure()
                contribution["integration"] = base
            elif node_state["stage"] == "CANDIDATE":
                contribution = _blank_pressure()
                contribution["evidence"] = base
            elif node_state["stage"] == "INVALIDATED":
                contribution["freshness"] = max(contribution["freshness"], base)
                contribution["repair"] = max(contribution["repair"], base)
            elif node_state["holds"]:
                contribution["repair"] = max(contribution["repair"], base)
            if snapshot["contradictions"]:
                contribution["uncertainty"] = max(contribution["uncertainty"], base)
            queue_depth = int(node_state.get("queue_depth", 0))
            if queue_depth > 0:
                contribution["queue"] = base * min(1.0, queue_depth / max(1, nodes[node_id]["queue_limit"]))
            per_node_goal[node_id][goal_id] = contribution
            parent_key = (goal_id, parent_node or "ROOT")
            obligation_key = (goal_id, node_id)
            obligation = obligations.get(obligation_key)
            parent_id = obligations[parent_key]["obligation_id"] if parent_key in obligations else obligations[(goal_id, "ROOT")]["obligation_id"]
            if obligation is None:
                obligation = {
                    "obligation_id": _digest("NXOBL", [goal_id, node_id]),
                    "root_goal_id": goal_id,
                    "node_id": node_id,
                    "parent_ids": [parent_id],
                    "closure_rule": "NODE_LIFECYCLE_TO_REQUIRED_STAGE",
                    "status": "CLOSED" if node_state["stage"] in {"COMMITTED", "CONSUMED", "OUTCOME_OBSERVED"} else ("HELD" if node_state["stage"] == "HELD" else "OPEN"),
                    "pressure": contribution,
                }
                obligations[obligation_key] = obligation
            elif parent_id not in obligation["parent_ids"]:
                obligation["parent_ids"].append(parent_id)
            for dependency in nodes[node_id]["requires"]:
                queue.append((dependency, node_id))

    pressure: Dict[str, Dict[str, float]] = {}
    for node_id in sorted(nodes):
        vector = _blank_pressure()
        for goal_contribution in per_node_goal.get(node_id, {}).values():
            for channel in PRESSURE_CHANNELS:
                vector[channel] += float(goal_contribution.get(channel, 0.0))
        pressure[node_id] = vector
    return demanded, pressure, sorted(obligations.values(), key=lambda item: (item["root_goal_id"], item["node_id"] or ""))


def derive(spec: Mapping[str, Any], snapshot: Mapping[str, Any], authority_states: Mapping[str, Mapping[str, Any]] | None = None) -> Dict[str, Any]:
    goal_statuses = _goal_statuses(spec, snapshot)
    invariant_statuses = _invariant_statuses(spec, snapshot)
    demanded, pressure, obligations = _demand_and_pressure(spec, snapshot, goal_statuses)
    if any(not item["passed"] for item in invariant_statuses):
        for node_id in pressure:
            if node_id in demanded:
                pressure[node_id]["constraint"] += 1.0
    readiness = _node_readiness(spec, snapshot, demanded, authority_states)
    return {
        "goals": goal_statuses,
        "hard_invariants": invariant_statuses,
        "demanded_nodes": sorted(demanded),
        "pressure": pressure,
        "readiness": readiness,
        "obligations": obligations,
    }


def _terminal(spec: Mapping[str, Any], snapshot: Mapping[str, Any], derived: Mapping[str, Any]) -> Dict[str, Any]:
    goals_closed = all(item["closed"] for item in derived["goals"].values())
    invariants_pass = all(item["passed"] for item in derived["hard_invariants"])
    actionable = sorted(node_id for node_id, value in derived["readiness"].items() if value["ready"])
    held = sorted(node_id for node_id, value in snapshot["node_state"].items() if value["stage"] == "HELD")
    active_claims = [claim for _, claim in _active_claims(snapshot, int(snapshot["revision"]))]
    if goals_closed and invariants_pass:
        status = "TERMINAL"
    elif actionable or active_claims:
        status = "ACTIVE"
    elif held:
        status = "HELD"
    else:
        status = "QUIESCENT_BLOCKED"
    proof_payload = {
        "machine_revision": snapshot["revision"],
        "status": status,
        "goals": {key: {"closed": value["closed"], "residual": value["residual"], "deficits": value["deficits"]} for key, value in derived["goals"].items()},
        "invariants": {value["id"]: value["passed"] for value in derived["hard_invariants"]},
        "actionable_nodes": actionable,
        "held_nodes": held,
        "active_claim_ids": sorted(str(item.get("claim_id")) for item in active_claims),
    }
    return {
        **proof_payload,
        "terminal": status == "TERMINAL",
        "proof_digest": _digest("NXTERM", proof_payload),
        "law": "TERMINAL requires recomputed terminal predicates, evidence, consumption, outcome and hard-invariant closure; producer self-report is never terminal authority",
    }


def _node_utility(spec: Mapping[str, Any], snapshot: Mapping[str, Any], derived: Mapping[str, Any], node_id: str) -> Dict[str, Any]:
    _, nodes, _, dependents = _index_spec(spec)
    node = nodes[node_id]
    vector = derived["pressure"][node_id]
    pressure_mass = sum(float(value) for value in vector.values())
    state = snapshot["node_state"][node_id]
    wait_age = max(0, int(snapshot["revision"]) - int(state.get("wait_since_revision", 0)))
    policy = spec["scheduler"]
    numerator = pressure_mass * max(0.0, float(node["expected_gain"]))
    numerator += policy["information_gain_weight"] * float(node["information_gain"])
    numerator += policy["unblock_weight"] * len(dependents[node_id])
    numerator += policy["aging_gain"] * wait_age
    denominator = 1.0 + float(node["cost"]) + float(node["latency"]) + float(node["risk"])
    queue_depth = int(state.get("queue_depth", 0))
    backpressure_factor = max(0.0, 1.0 - queue_depth / max(1, int(node["queue_limit"])))
    utility = numerator / denominator * backpressure_factor
    return {
        "node_id": node_id,
        "utility": utility,
        "pressure_mass": pressure_mass,
        "pressure": vector,
        "predicted_gain": node["expected_gain"],
        "information_gain": node["information_gain"],
        "downstream_unblock_count": len(dependents[node_id]),
        "wait_age": wait_age,
        "cost": node["cost"],
        "backpressure_factor": backpressure_factor,
    }


def plan_snapshot(spec: Mapping[str, Any], snapshot: Mapping[str, Any], max_nodes: int | None = None, max_cost: float | None = None, authority_states: Mapping[str, Mapping[str, Any]] | None = None) -> Dict[str, Any]:
    derived = derive(spec, snapshot, authority_states)
    terminal = _terminal(spec, snapshot, derived)
    if terminal["terminal"]:
        return {"status": "TERMINAL", "revision": snapshot["revision"], "batch": [], "terminal": terminal, "derived": derived}
    limit = int(max_nodes if max_nodes is not None else spec["scheduler"]["max_batch"])
    if limit < 1 or limit > 1000:
        raise ValueError("max_nodes must be in [1,1000]")
    budget = float(max_cost if max_cost is not None else spec["scheduler"]["max_cost"])
    if not math.isfinite(budget) or budget < 0:
        raise ValueError("max_cost must be a non-negative finite number")
    _, nodes, _, _ = _index_spec(spec)
    scored = [_node_utility(spec, snapshot, derived, node_id) for node_id, value in derived["readiness"].items() if value["ready"]]
    scored.sort(key=lambda item: (-item["utility"], item["node_id"]))
    selected = []
    selected_writes: List[str] = []
    spent = 0.0
    for item in scored:
        node = nodes[item["node_id"]]
        if len(selected) >= limit:
            break
        if spent + float(node["cost"]) > budget + 1e-12:
            continue
        if _sets_intersect(selected_writes, node["writeset"]):
            continue
        obligations = [obligation["obligation_id"] for obligation in derived["obligations"] if obligation.get("node_id") == node["id"] and obligation["status"] != "CLOSED"]
        packet_basis = {
            "version": VERSION,
            "revision": snapshot["revision"],
            "topology_epoch": snapshot["topology_epoch"],
            "node_id": node["id"],
            "obligation_ids": obligations,
            "pressure": item["pressure"],
            "readset": node["readset"],
            "readset_digest": derived["readiness"][node["id"]]["readset_digest"],
            "writeset": node["writeset"],
            "required_authorities": node["required_authorities"],
            "required_authority_claims": node["required_authority_claims"],
            "authority_claim_checks": derived["readiness"][node["id"]]["authority_claim_checks"],
            "evidence_threshold": node["evidence_threshold"],
            "consumer": node["consumer"],
            "require_outcome": node["require_outcome"],
        }
        selected.append({**item, "nexus_packet": {**packet_basis, "packet_id": _digest("NXPKT", packet_basis)}})
        selected_writes.extend(node["writeset"])
        spent += float(node["cost"])
    status = "PLANNED" if selected else terminal["status"]
    return {
        "status": status,
        "revision": snapshot["revision"],
        "batch": selected,
        "spent_cost": spent,
        "candidate_count": len(scored),
        "terminal": terminal,
        "derived": derived,
        "law": "selection maximizes deterministic expected verified pressure reduction under hard authority, freshness, capacity, dependency, budget and writeset-conflict gates",
    }


def _decision_cone(spec: Mapping[str, Any], changed_paths: Sequence[str]) -> set[str]:
    _, nodes, _, dependents = _index_spec(spec)
    affected = {node_id for node_id, node in nodes.items() if _sets_intersect(changed_paths, node["readset"] + node["freshness_keys"])}
    queue = deque(sorted(affected))
    while queue:
        node_id = queue.popleft()
        for dependent in dependents[node_id]:
            if dependent not in affected:
                affected.add(dependent)
                queue.append(dependent)
    return affected


def _candidate_readset_digest(spec: Mapping[str, Any], snapshot: Mapping[str, Any], node_id: str) -> str:
    _, nodes, _, _ = _index_spec(spec)
    return _state_digest(snapshot["state"], nodes[node_id]["readset"])


def _validate_event_envelope(raw: Mapping[str, Any]) -> Tuple[str, Dict[str, Any], str | None, str | None]:
    if not isinstance(raw, Mapping):
        raise ValueError("event must be an object")
    event_type = str(raw.get("type") or "")
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unsupported event type {event_type}")
    payload = copy.deepcopy(raw.get("payload") or {})
    if not isinstance(payload, Mapping):
        raise ValueError("event.payload must be an object")
    event_id = str(raw.get("event_id") or "").strip() or None
    idempotency_key = str(raw.get("idempotency_key") or "").strip() or None
    return event_type, dict(payload), event_id, idempotency_key


def _require_node(spec: Mapping[str, Any], snapshot: Mapping[str, Any], payload: Mapping[str, Any]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    _, nodes, _, _ = _index_spec(spec)
    node_id = _clean_id(payload.get("node_id"), "event.payload.node_id")
    if node_id not in nodes:
        raise ValueError(f"unknown node {node_id}")
    return node_id, nodes[node_id], snapshot["node_state"][node_id]
