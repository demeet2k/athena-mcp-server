from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .orchestration_explain import decision_explanation, measurement_requests, pareto_successor_frontier
from .orchestration_gate import promotion_gate
from .orchestration_graph import candidate_id, dependency_graph
from .orchestration_score import (
    REWARD_NEGATIVE,
    REWARD_POSITIVE,
    frontier_score,
    rank_key,
    residual_score,
    reward_score,
    successor_score,
)

AOR_VERSION = "AOR.3"

TRANSFORMS = (
    "decompose", "formalize", "dual", "invert", "compose", "recur",
    "edge", "contradict", "fail", "falsify", "bridge", "implement",
    "test", "compress", "reconstruct", "successor",
)

EDGE_TYPES = (
    "define", "derive", "depend", "support", "contradict", "test", "fail",
    "implement", "bridge", "reconstruct", "fork", "merge", "next",
)

RUN_STAGES = (
    "reconstruct", "extract", "retrieve", "hug", "graph", "gap", "compile",
    "measure", "test", "observe", "repair", "retest", "verify", "reward",
    "reallocate", "output", "successor", "replay",
)

TEST_BRANCHES = ("main", "counter", "edge", "fail")
COORDINATE_FIBER = ("KC144", "JSPACE_GRAPH", "LINEAGE", "SEMANTIC", "TIME_NATIVE")


def _numeric_positive(value: Any) -> bool:
    if isinstance(value, bool): return value
    try: return float(value) > 0
    except (TypeError, ValueError): return False


def _allocation(item: Mapping[str, Any], reward: Mapping[str, Any], gate: Mapping[str, Any], dep: Mapping[str, Any]) -> List[str]:
    if not dep.get("ready", True): return ["resolve_dependency"]
    if gate.get("status") == "BLOCKED": return ["branch", "repair", "retest"]
    if reward.get("status") != "KNOWN": return ["measure"]
    value = float(reward["value"])
    if value > 0: return ["deepen", "replicate", "braid"]
    if _numeric_positive(item.get("duplicate")): return ["hibernate"]
    return ["retain", "measure"]


def _candidate_row(item: Mapping[str, Any], index: int, dep: Mapping[str, Any]) -> Dict[str, Any]:
    ident = candidate_id(item, index)
    frontier = frontier_score(item); successor = successor_score(item); reward = reward_score(item); gate = promotion_gate(item)
    unresolved = not bool(item.get("resolved", False))
    rankable_frontier = dep.get("ready", True) and gate["status"] == "PASS" and frontier["status"] == "KNOWN"
    rankable_successor = unresolved and dep.get("ready", True) and gate["status"] == "PASS" and successor["status"] == "KNOWN"
    unknown = sorted(set(frontier.get("missing", []) + successor.get("missing", []) + reward.get("missing", [])))
    return {
        "id": ident,
        "resolved": not unresolved,
        "dependency": dep,
        "gate": gate,
        "scores": {"frontier": frontier, "successor": successor, "reward": reward},
        "rankable_frontier": rankable_frontier,
        "rankable_successor": rankable_successor,
        "unknown_metrics": unknown,
        "allocation": _allocation(item, reward, gate, dep),
        "source": dict(item),
    }


def _frontier_sort(row: Mapping[str, Any]):
    return rank_key(row["scores"]["frontier"], str(row["id"]))


def _successor_sort(row: Mapping[str, Any]):
    score = row["scores"]["successor"]; frontier = row["scores"]["frontier"]
    sv = float(score["value"]) if score.get("status") == "KNOWN" else 0.0
    fv = float(frontier["value"]) if frontier.get("status") == "KNOWN" else 0.0
    return (0 if score.get("status") == "KNOWN" else 1, -sv, -fv, str(row["id"]))


def _decision_digest(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def orchestration_law() -> Dict[str, Any]:
    return {
        "version": AOR_VERSION,
        "run": list(RUN_STAGES),
        "seed_law": "SX+ = dedup(SX U T(SX))",
        "transform_bank": list(TRANSFORMS),
        "graph": {"edge_types": list(EDGE_TYPES), "dependency_law": "ready iff prerequisites exist+resolved and candidate is not in an unresolved dependency cycle"},
        "coordinates": {"fiber": list(COORDINATE_FIBER), "law": "coordinate != identity; UNKNOWN is preserved; required coordinate gaps block promotion"},
        "unknown_law": "UNKNOWN != 0; incomplete required formulas are non-rankable and route to measurement",
        "gap_law": "grow = argmax(severity * leverage * information_gain / cost) over KNOWN residual scores",
        "frontier_law": "F = argmax(readiness * gain * independence * bridge / cost) over dependency-ready gate-passing KNOWN candidates",
        "successor_law": "next = argmax_unresolved(delta_j * information_gain * bridge * option_value / cost) over dependency-ready gate-passing KNOWN candidates",
        "pareto_law": "preserve all successor candidates not dominated on delta_j, information_gain, bridge, option_value and cost",
        "reward": {"positive": list(REWARD_POSITIVE), "negative": list(REWARD_NEGATIVE)},
        "test": {"branches": list(TEST_BRANCHES), "claim_requires": ["procedure", "observation", "result", "witness"]},
        "transaction": {"stages": ["attempt", "action", "commit?", "receipt", "verify", "rollback?"], "persisted_claim_requires": ["commit", "receipt", "verify"], "fake_success": False},
        "allocation": {"high_reward": ["deepen", "replicate", "braid"], "low_reward_duplicate": ["hibernate"], "unknown_reward": ["measure"], "dependency_blocked": ["resolve_dependency"], "gate_blocked": ["branch", "repair", "retest"], "hibernate_is_erase": False},
        "budget_law": "P* = argmax_|P|<=B(development + extraction + graph + coordinates + evidence + replay + navigation + successor)",
    }


def compile_orchestration(seed: Any, candidates: Optional[Iterable[Mapping[str, Any]]] = None, residuals: Optional[Iterable[Mapping[str, Any]]] = None, budget: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    source_candidates = [dict(item) for item in (candidates or [])]
    unique: Dict[str, Dict[str, Any]] = {}; duplicate_ids: List[str] = []
    for index, item in enumerate(source_candidates):
        ident = candidate_id(item, index)
        if ident in unique: duplicate_ids.append(ident); continue
        unique[ident] = item
    source_candidates = list(unique.values())

    dep_graph = dependency_graph(source_candidates)
    rows = []
    for index, item in enumerate(source_candidates):
        ident = candidate_id(item, index)
        rows.append(_candidate_row(item, index, dep_graph["readiness"].get(ident, {"ready": True, "blockers": []})))

    frontier = sorted(rows, key=_frontier_sort)
    executable_frontier = [row for row in frontier if row["rankable_frontier"]]
    successor_frontier = sorted((row for row in rows if row["rankable_successor"]), key=_successor_sort)
    measurement_frontier = [row for row in frontier if row["unknown_metrics"]]
    measurement_plan = measurement_requests(frontier)
    pareto_ids = pareto_successor_frontier(successor_frontier)

    residual_rows = []
    for index, item in enumerate(residuals or []):
        item = dict(item); ident = str(item.get("id") or item.get("name") or f"residual:{index:04d}")
        residual_rows.append({"id": ident, "score": residual_score(item), "source": item})
    residual_frontier = sorted(residual_rows, key=lambda row: rank_key(row["score"], row["id"]))
    known_residuals = [row for row in residual_frontier if row["score"]["status"] == "KNOWN"]

    next_id = successor_frontier[0]["id"] if successor_frontier else None
    explanation = decision_explanation(frontier, next_id)
    decision = {
        "executable_frontier": [row["id"] for row in executable_frontier],
        "successor_frontier": [row["id"] for row in successor_frontier],
        "pareto_successor_frontier": pareto_ids,
        "measurement_frontier": [row["id"] for row in measurement_frontier],
        "grow": known_residuals[0]["id"] if known_residuals else None,
        "next": next_id,
        "dependency_cycles": dep_graph["cycles"],
    }

    result = {
        "kernel": AOR_VERSION,
        "seed": seed,
        "budget": dict(budget or {}),
        "law": orchestration_law(),
        "extraction_plan": [{"transform": transform, "seed": seed} for transform in TRANSFORMS],
        "candidate_dedup": {"mode": "explicit_identity_only", "duplicate_ids": duplicate_ids},
        "dependency_graph": dep_graph,
        "frontier": frontier,
        "executable_frontier": executable_frontier,
        "successor_frontier": successor_frontier,
        "pareto_successor_frontier": pareto_ids,
        "measurement_frontier": measurement_frontier,
        "measurement_plan": measurement_plan,
        "residual_frontier": residual_frontier,
        "grow": known_residuals[0] if known_residuals else None,
        "next": successor_frontier[0] if successor_frontier else None,
        "decision_explanation": explanation,
        "return": {"required": ["result", "math", "graph", "coordinates", "evidence", "residuals", "witnesses", "delta", "next"], "missing_witness": "downgrade", "missing_coordinate": "repair_before_promotion", "unknown_metric": "measure_not_zero", "dependency_blocked": "resolve_dependency", "error": ["rollback", "branch"], "high_residual": "continue"},
    }
    result["decision_digest"] = _decision_digest(decision)
    return result
