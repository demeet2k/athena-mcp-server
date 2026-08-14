from __future__ import annotations

"""NEXUS-4D: durable bidirectional obligation/pressure control kernel.

The kernel never executes arbitrary code. It compiles terminal predicates and node
contracts into obligations, derives typed pressure backward, derives readiness
forward, emits conflict-free executable nexus packets, and accepts independently
witnessed lifecycle events. Only recomputed terminal predicates plus evidence,
consumption, and outcome receipts can close a goal.
"""

import copy
import hashlib
import json
import math
import time
from collections import defaultdict, deque
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

VERSION = "ATHENA.NEXUS4D.1"
SCHEMA = "ATHENA.NEXUS4D.MACHINE.1"
RESOURCE_URI = "athena://nexus4d"

PRESSURE_CHANNELS = (
    "goal",
    "constraint",
    "evidence",
    "uncertainty",
    "freshness",
    "integration",
    "repair",
    "queue",
    "outcome",
)
EVIDENCE_DIMENSIONS = (
    "provenance",
    "local",
    "replay",
    "integration",
    "hosted",
    "behavioral",
    "causal",
    "freshness",
)
LIFECYCLE = (
    "OPEN",
    "CLAIMED",
    "CANDIDATE",
    "VERIFIED",
    "COMMITTED",
    "CONSUMED",
    "OUTCOME_OBSERVED",
    "HELD",
    "INVALIDATED",
)
LIFECYCLE_RANK = {name: index for index, name in enumerate(LIFECYCLE)}
AUTHORITY_ORDER = {"?": 0, "+": 1, "!": 2, "#": 3}
EVENT_TYPES = {
    "STATE_OBSERVED",
    "CLAIMED",
    "CANDIDATE_PRODUCED",
    "EVIDENCE_RECORDED",
    "VERIFIED",
    "COMMITTED",
    "CONSUMED",
    "OUTCOME_OBSERVED",
    "HELD",
    "RELEASED",
    "INVALIDATED",
    "AUTHORITY_UPDATED",
    "CAPACITY_UPDATED",
    "QUEUE_UPDATED",
    "CONTRADICTION_RECORDED",
    "TOPOLOGY_CANDIDATE",
    "TOPOLOGY_TESTED",
    "TOPOLOGY_PROMOTED",
    "TOPOLOGY_ROLLED_BACK",
}

_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS nexus4d_machines(
    machine_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    revision INTEGER NOT NULL,
    genesis_spec_json TEXT NOT NULL,
    spec_json TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    snapshot_digest TEXT NOT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS nexus4d_events(
    machine_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    event_id TEXT NOT NULL,
    idempotency_key TEXT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    event_digest TEXT NOT NULL,
    created_at REAL NOT NULL,
    PRIMARY KEY(machine_id,seq),
    UNIQUE(machine_id,event_id),
    UNIQUE(machine_id,idempotency_key),
    FOREIGN KEY(machine_id) REFERENCES nexus4d_machines(machine_id)
);
CREATE INDEX IF NOT EXISTS idx_nexus4d_events_machine ON nexus4d_events(machine_id,seq);
"""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _digest(prefix: str, value: Any) -> str:
    raw = _canonical(value).encode("utf-8")
    return f"{prefix}.{hashlib.sha256(raw).hexdigest().upper()}"


def _clean_id(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    if len(text) > 256:
        raise ValueError(f"{field} exceeds 256 characters")
    return text


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _bounded(value: Any, field: str, low: float = 0.0, high: float = 1.0) -> float:
    number = _finite_number(value, field)
    if number < low or number > high:
        raise ValueError(f"{field} must be in [{low},{high}]")
    return number


def _blank_pressure() -> Dict[str, float]:
    return {name: 0.0 for name in PRESSURE_CHANNELS}


def _blank_evidence() -> Dict[str, float]:
    return {name: 0.0 for name in EVIDENCE_DIMENSIONS}


def _normalize_evidence(value: Any, field: str = "evidence") -> Dict[str, float]:
    if value is None:
        return _blank_evidence()
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    unknown = sorted(set(value) - set(EVIDENCE_DIMENSIONS))
    if unknown:
        raise ValueError(f"{field} has unknown dimensions: {unknown}")
    out = _blank_evidence()
    for name, raw in value.items():
        out[name] = _bounded(raw, f"{field}.{name}")
    return out


def _evidence_meets(actual: Mapping[str, float], required: Mapping[str, float]) -> bool:
    return all(float(actual.get(name, 0.0)) + 1e-12 >= float(required.get(name, 0.0)) for name in EVIDENCE_DIMENSIONS)


def _merge_evidence(left: Mapping[str, float], right: Mapping[str, float]) -> Dict[str, float]:
    return {name: max(float(left.get(name, 0.0)), float(right.get(name, 0.0))) for name in EVIDENCE_DIMENSIONS}


def _get_path(state: Mapping[str, Any], path: str) -> Tuple[bool, Any]:
    if path == "" or path is None:
        return True, state
    current: Any = state
    for part in str(path).split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _set_path(state: MutableMapping[str, Any], path: str, value: Any) -> None:
    parts = [part for part in str(path).split(".") if part]
    if not parts:
        if not isinstance(value, Mapping):
            raise ValueError("root state delta must be an object")
        state.clear()
        state.update(copy.deepcopy(dict(value)))
        return
    current: MutableMapping[str, Any] = state
    for part in parts[:-1]:
        child = current.get(part)
        if child is None:
            child = {}
            current[part] = child
        if not isinstance(child, MutableMapping):
            raise ValueError(f"cannot descend through non-object state path {path}")
        current = child
    current[parts[-1]] = copy.deepcopy(value)


def _apply_delta(state: MutableMapping[str, Any], delta: Mapping[str, Any]) -> List[str]:
    if not isinstance(delta, Mapping):
        raise ValueError("state_delta must be an object mapping dot paths to values")
    changed: List[str] = []
    for path in sorted(delta):
        text = str(path)
        _set_path(state, text, delta[path])
        changed.append(text)
    return changed


def _path_intersects(left: str, right: str) -> bool:
    return left == right or left.startswith(right + ".") or right.startswith(left + ".")


def _sets_intersect(left: Iterable[str], right: Iterable[str]) -> bool:
    return any(_path_intersects(a, b) for a in left for b in right)


def _path_covered(path: str, declared: str) -> bool:
    return path == declared or path.startswith(declared + ".")


def _state_projection(state: Mapping[str, Any], paths: Iterable[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for path in sorted(set(paths)):
        exists, value = _get_path(state, path)
        out[path] = {"exists": exists, "value": value if exists else None}
    return out


def _state_digest(state: Mapping[str, Any], paths: Iterable[str] | None = None) -> str:
    payload: Any = state if paths is None else _state_projection(state, paths)
    return _digest("NXSTATE", payload)


def _eval_predicate(predicate: Mapping[str, Any], state: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(predicate, Mapping):
        raise ValueError("predicate must be an object")
    kind = str(predicate.get("kind") or "state_equals")
    path = str(predicate.get("path") or "")
    exists, actual = _get_path(state, path)

    if kind == "exists":
        expected = bool(predicate.get("value", True))
        passed = exists is expected
        return {"kind": kind, "path": path, "known": True, "actual": exists, "expected": expected, "residual": 0.0 if passed else 1.0, "passed": passed}
    if kind == "state_equals":
        expected = predicate.get("value")
        passed = exists and actual == expected
        return {"kind": kind, "path": path, "known": exists, "actual": actual if exists else None, "expected": expected, "residual": 0.0 if passed else 1.0, "passed": passed}
    if kind == "boolean_true":
        passed = exists and actual is True
        return {"kind": kind, "path": path, "known": exists, "actual": actual if exists else None, "expected": True, "residual": 0.0 if passed else 1.0, "passed": passed}
    if kind in {"numeric_at_most", "numeric_at_least", "numeric_near"}:
        target = _finite_number(predicate.get("value"), "predicate.value")
        if not exists or isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isfinite(float(actual)):
            return {"kind": kind, "path": path, "known": False, "actual": None, "expected": target, "residual": 1.0, "passed": False}
        number = float(actual)
        if kind == "numeric_at_most":
            residual = max(0.0, number - target)
        elif kind == "numeric_at_least":
            residual = max(0.0, target - number)
        else:
            residual = abs(number - target)
        tolerance = _finite_number(predicate.get("tolerance", 0.0), "predicate.tolerance")
        passed = residual <= tolerance + 1e-12
        return {"kind": kind, "path": path, "known": True, "actual": number, "expected": target, "tolerance": tolerance, "residual": residual, "passed": passed}
    if kind == "list_contains":
        expected = predicate.get("value")
        known = exists and isinstance(actual, list)
        passed = known and expected in actual
        return {"kind": kind, "path": path, "known": known, "actual": actual if known else None, "expected": expected, "residual": 0.0 if passed else 1.0, "passed": passed}
    if kind in {"all", "any"}:
        children = predicate.get("predicates")
        if not isinstance(children, list) or not children:
            raise ValueError(f"{kind} predicate requires non-empty predicates")
        results = [_eval_predicate(child, state) for child in children]
        passed = all(item["passed"] for item in results) if kind == "all" else any(item["passed"] for item in results)
        residual = max(item["residual"] for item in results) if kind == "all" else min(item["residual"] for item in results)
        return {"kind": kind, "known": all(item["known"] for item in results), "children": results, "residual": residual, "passed": passed}
    if kind == "not":
        child = _eval_predicate(predicate.get("predicate") or {}, state)
        return {"kind": kind, "known": child["known"], "child": child, "residual": 0.0 if not child["passed"] else 1.0, "passed": not child["passed"]}
    raise ValueError(f"unsupported predicate kind {kind}")


def _normalize_paths(value: Any, field: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    out: List[str] = []
    for raw in value:
        path = str(raw or "").strip()
        if not path:
            raise ValueError(f"{field} contains an empty path")
        if path not in out:
            out.append(path)
    return out


def _normalize_goal(raw: Mapping[str, Any]) -> Dict[str, Any]:
    goal_id = _clean_id(raw.get("id"), "goal.id")
    predicate = copy.deepcopy(raw.get("predicate") or {})
    _eval_predicate(predicate, {})
    weight = _finite_number(raw.get("weight", 1.0), f"goal[{goal_id}].weight")
    consequence = _finite_number(raw.get("consequence", 1.0), f"goal[{goal_id}].consequence")
    if weight <= 0 or consequence <= 0:
        raise ValueError("goal weight and consequence must be positive")
    return {
        "id": goal_id,
        "predicate": predicate,
        "weight": weight,
        "consequence": consequence,
        "evidence_threshold": _normalize_evidence(raw.get("evidence_threshold"), f"goal[{goal_id}].evidence_threshold"),
        "consumer": str(raw.get("consumer") or "").strip() or None,
        "require_outcome": bool(raw.get("require_outcome", False)),
        "external_only": bool(raw.get("external_only", False)),
        "freshness_keys": _normalize_paths(raw.get("freshness_keys"), f"goal[{goal_id}].freshness_keys"),
    }


def _normalize_authority_claims(value: Any, field: str) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    result = []
    seen = set()
    for raw in value:
        if isinstance(raw, str):
            item = {"claim_id": raw, "min_y": "!", "required_status": "ACTIVE"}
        elif isinstance(raw, Mapping):
            item = dict(raw)
        else:
            raise ValueError(f"{field} items must be strings or objects")
        claim_id = _clean_id(item.get("claim_id"), f"{field}.claim_id")
        min_y = str(item.get("min_y") or "!")
        if min_y not in AUTHORITY_ORDER:
            raise ValueError(f"{field}.min_y must be one of ?, +, !, #")
        required_status = str(item.get("required_status") or "ACTIVE")
        key = (claim_id, min_y, required_status)
        if key not in seen:
            result.append({"claim_id": claim_id, "min_y": min_y, "required_status": required_status})
            seen.add(key)
    return sorted(result, key=lambda item: (item["claim_id"], item["min_y"], item["required_status"]))


def _authority_checks(requirements: Sequence[Mapping[str, Any]], states: Mapping[str, Mapping[str, Any]] | None) -> List[Dict[str, Any]]:
    states = states or {}
    checks = []
    for requirement in requirements:
        claim_id = requirement["claim_id"]
        state = states.get(claim_id)
        observed_y = str(state.get("y")) if state else None
        observed_status = str(state.get("status")) if state else None
        passed = bool(
            state
            and observed_y in AUTHORITY_ORDER
            and AUTHORITY_ORDER[observed_y] >= AUTHORITY_ORDER[requirement["min_y"]]
            and observed_status == requirement["required_status"]
        )
        checks.append({
            "claim_id": claim_id,
            "min_y": requirement["min_y"],
            "required_status": requirement["required_status"],
            "observed_y": observed_y,
            "observed_status": observed_status,
            "last_eid": state.get("last_eid") if state else None,
            "canonical_ref": state.get("canonical_ref") if state else None,
            "passed": passed,
        })
    return checks


def _normalize_node(raw: Mapping[str, Any]) -> Dict[str, Any]:
    node_id = _clean_id(raw.get("id"), "node.id")
    capacity = int(raw.get("capacity", 1))
    if capacity < 1 or capacity > 10000:
        raise ValueError(f"node[{node_id}].capacity must be in [1,10000]")
    queue_limit = int(raw.get("queue_limit", max(1, capacity * 4)))
    if queue_limit < 1 or queue_limit > 1000000:
        raise ValueError(f"node[{node_id}].queue_limit must be in [1,1000000]")
    required_state = raw.get("required_state") or []
    if not isinstance(required_state, list):
        raise ValueError(f"node[{node_id}].required_state must be an array")
    for predicate in required_state:
        _eval_predicate(predicate, {})
    authorities = raw.get("required_authorities") or []
    if not isinstance(authorities, list):
        raise ValueError(f"node[{node_id}].required_authorities must be an array")
    required_authorities = sorted({_clean_id(value, f"node[{node_id}].required_authorities") for value in authorities})
    goals = raw.get("goals") or []
    requires = raw.get("requires") or []
    if not isinstance(goals, list) or not isinstance(requires, list):
        raise ValueError(f"node[{node_id}] goals/requires must be arrays")
    dependency_stage = str(raw.get("dependency_stage") or "COMMITTED")
    if dependency_stage not in {"VERIFIED", "COMMITTED", "CONSUMED", "OUTCOME_OBSERVED"}:
        raise ValueError(f"node[{node_id}].dependency_stage is invalid")
    return {
        "id": node_id,
        "goals": sorted({_clean_id(value, f"node[{node_id}].goals") for value in goals}),
        "requires": sorted({_clean_id(value, f"node[{node_id}].requires") for value in requires}),
        "dependency_stage": dependency_stage,
        "required_state": copy.deepcopy(required_state),
        "readset": _normalize_paths(raw.get("readset"), f"node[{node_id}].readset"),
        "writeset": _normalize_paths(raw.get("writeset"), f"node[{node_id}].writeset"),
        "freshness_keys": _normalize_paths(raw.get("freshness_keys"), f"node[{node_id}].freshness_keys"),
        "required_authorities": required_authorities,
        "required_authority_claims": _normalize_authority_claims(raw.get("required_authority_claims"), f"node[{node_id}].required_authority_claims"),
        "capacity": capacity,
        "queue_limit": queue_limit,
        "cost": max(0.0, _finite_number(raw.get("cost", 1.0), f"node[{node_id}].cost")),
        "latency": max(0.0, _finite_number(raw.get("latency", 0.0), f"node[{node_id}].latency")),
        "risk": max(0.0, _finite_number(raw.get("risk", 0.0), f"node[{node_id}].risk")),
        "expected_gain": max(0.0, _finite_number(raw.get("expected_gain", 1.0), f"node[{node_id}].expected_gain")),
        "information_gain": max(0.0, _finite_number(raw.get("information_gain", 0.0), f"node[{node_id}].information_gain")),
        "evidence_threshold": _normalize_evidence(raw.get("evidence_threshold"), f"node[{node_id}].evidence_threshold"),
        "consumer": str(raw.get("consumer") or "").strip() or None,
        "require_outcome": bool(raw.get("require_outcome", False)),
        "failure_routes": copy.deepcopy(raw.get("failure_routes") or {}),
        "idempotent": bool(raw.get("idempotent", True)),
    }


def _detect_cycles(nodes: Mapping[str, Mapping[str, Any]]) -> List[List[str]]:
    index = 0
    indices: Dict[str, int] = {}
    low: Dict[str, int] = {}
    stack: List[str] = []
    on_stack: set[str] = set()
    cycles: List[List[str]] = []

    def visit(node_id: str) -> None:
        nonlocal index
        indices[node_id] = index
        low[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)
        for dependency in nodes[node_id]["requires"]:
            if dependency not in indices:
                visit(dependency)
                low[node_id] = min(low[node_id], low[dependency])
            elif dependency in on_stack:
                low[node_id] = min(low[node_id], indices[dependency])
        if low[node_id] == indices[node_id]:
            component: List[str] = []
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.append(item)
                if item == node_id:
                    break
            if len(component) > 1 or node_id in nodes[node_id]["requires"]:
                cycles.append(sorted(component))

    for node_id in sorted(nodes):
        if node_id not in indices:
            visit(node_id)
    return cycles


def normalize_spec(raw: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("spec must be an object")
    goals_raw = raw.get("goals")
    nodes_raw = raw.get("nodes")
    if not isinstance(goals_raw, list) or not goals_raw:
        raise ValueError("spec.goals must be a non-empty array")
    if not isinstance(nodes_raw, list):
        raise ValueError("spec.nodes must be an array")
    goals_list = [_normalize_goal(item) for item in goals_raw]
    nodes_list = [_normalize_node(item) for item in nodes_raw]
    goals = {item["id"]: item for item in goals_list}
    nodes = {item["id"]: item for item in nodes_list}
    if len(goals) != len(goals_list):
        raise ValueError("goal ids must be unique")
    if len(nodes) != len(nodes_list):
        raise ValueError("node ids must be unique")
    for node in nodes.values():
        missing_goals = sorted(set(node["goals"]) - set(goals))
        missing_nodes = sorted(set(node["requires"]) - set(nodes))
        if missing_goals:
            raise ValueError(f"node {node['id']} references unknown goals {missing_goals}")
        if missing_nodes:
            raise ValueError(f"node {node['id']} references unknown dependencies {missing_nodes}")
    producers = defaultdict(list)
    for node in nodes.values():
        for goal_id in node["goals"]:
            producers[goal_id].append(node["id"])
    missing_producers = [goal_id for goal_id, goal in goals.items() if not goal["external_only"] and not producers[goal_id]]
    if missing_producers:
        raise ValueError(f"goals without producers or external_only=true: {missing_producers}")
    cycles = _detect_cycles(nodes)
    cycle_policy = copy.deepcopy(raw.get("cycle_policy") or {})
    if cycles:
        max_iterations = int(cycle_policy.get("max_iterations", 0) or 0)
        gain_predicate = cycle_policy.get("gain_predicate")
        if max_iterations < 1 or not isinstance(gain_predicate, Mapping):
            raise ValueError(f"dependency cycles require cycle_policy.max_iterations and gain_predicate: {cycles}")
        _eval_predicate(gain_predicate, {})
    invariants = raw.get("hard_invariants") or []
    if not isinstance(invariants, list):
        raise ValueError("spec.hard_invariants must be an array")
    normalized_invariants = []
    for index, item in enumerate(invariants):
        if not isinstance(item, Mapping):
            raise ValueError("hard invariant must be an object")
        invariant_id = _clean_id(item.get("id") or f"INV{index+1}", "hard_invariant.id")
        predicate = copy.deepcopy(item.get("predicate") or {})
        _eval_predicate(predicate, {})
        normalized_invariants.append({"id": invariant_id, "predicate": predicate})
    authorities = raw.get("authorities") or []
    if not isinstance(authorities, list):
        raise ValueError("spec.authorities must be an array")
    initial_state = copy.deepcopy(raw.get("initial_state") or {})
    if not isinstance(initial_state, Mapping):
        raise ValueError("spec.initial_state must be an object")
    policy = raw.get("scheduler") or {}
    if not isinstance(policy, Mapping):
        raise ValueError("spec.scheduler must be an object")
    spec = {
        "schema": SCHEMA,
        "name": str(raw.get("name") or "NEXUS-4D machine"),
        "goals": [goals[key] for key in sorted(goals)],
        "nodes": [nodes[key] for key in sorted(nodes)],
        "hard_invariants": sorted(normalized_invariants, key=lambda item: item["id"]),
        "authorities": sorted({_clean_id(value, "spec.authorities") for value in authorities}),
        "initial_state": initial_state,
        "cycle_policy": cycle_policy,
        "topology_authority_claims": _normalize_authority_claims(raw.get("topology_authority_claims"), "spec.topology_authority_claims"),
        "scheduler": {
            "max_batch": int(policy.get("max_batch", 8)),
            "max_cost": max(0.0, _finite_number(policy.get("max_cost", 100.0), "scheduler.max_cost")),
            "aging_gain": max(0.0, _finite_number(policy.get("aging_gain", 0.05), "scheduler.aging_gain")),
            "information_gain_weight": max(0.0, _finite_number(policy.get("information_gain_weight", 0.25), "scheduler.information_gain_weight")),
            "unblock_weight": max(0.0, _finite_number(policy.get("unblock_weight", 0.1), "scheduler.unblock_weight")),
        },
    }
    if spec["scheduler"]["max_batch"] < 1 or spec["scheduler"]["max_batch"] > 1000:
        raise ValueError("scheduler.max_batch must be in [1,1000]")
    failed_initial = [item["id"] for item in spec["hard_invariants"] if not _eval_predicate(item["predicate"], spec["initial_state"])["passed"]]
    if failed_initial:
        raise ValueError(f"initial_state violates hard invariants {failed_initial}")
    for goal in spec["goals"]:
        if goal["external_only"] and (any(goal["evidence_threshold"].values()) or goal["consumer"] is not None or goal["require_outcome"]):
            raise ValueError(f"external-only goal {goal['id']} cannot require producer evidence, consumption, or outcome receipts")
    return spec
