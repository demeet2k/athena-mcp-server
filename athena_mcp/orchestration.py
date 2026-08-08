from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .orchestration_budget import allocate_budget
from .orchestration_explain import decision_explanation, measurement_requests, pareto_successor_frontier
from .orchestration_gate import promotion_gate
from .orchestration_graph import candidate_id, dependency_graph
from .orchestration_metric import calibration_requests, contract_summary, formula_calibration, normalize_item
from .orchestration_reward import reallocation_plan
from .orchestration_score import (
    REWARD_NEGATIVE,
    REWARD_POSITIVE,
    frontier_score,
    rank_key,
    residual_score,
    reward_score,
    successor_score,
)
from .orchestration_successor import successor_packet
from .orchestration_test import validation_bundle

AOR_VERSION = "AOR.3.1"

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
    "measure", "calibrate", "validate_test", "validate_persistence", "test",
    "observe", "repair", "retest", "verify", "reward", "reallocate",
    "allocate_budget", "output", "successor", "replay",
)

TEST_BRANCHES = ("main", "counter", "edge", "fail")
COORDINATE_FIBER = ("KC144", "JSPACE_GRAPH", "LINEAGE", "SEMANTIC", "TIME_NATIVE")


def _numeric_positive(value: Any) -> bool:
    if isinstance(value, bool): return value
    try: return float(value) > 0
    except (TypeError, ValueError): return False


def _allocation(item: Mapping[str, Any], reward: Mapping[str, Any], reward_calibration: Mapping[str, Any], gate: Mapping[str, Any], dep: Mapping[str, Any], validation: Mapping[str, Any]) -> List[str]:
    if not dep.get("ready", True): return ["resolve_dependency"]
    if gate.get("status") == "BLOCKED" or validation.get("status") == "BLOCKED": return ["branch", "repair", "retest"]
    if not reward_calibration.get("ranking_allowed", True): return ["calibrate_metrics"]
    if reward.get("status") != "KNOWN": return ["measure"]
    value = float(reward["value"])
    if value > 0: return ["deepen", "replicate", "braid"]
    if _numeric_positive(item.get("duplicate")): return ["hibernate"]
    return ["retain", "measure"]


def _candidate_row(raw_item: Mapping[str, Any], scoring_item: Mapping[str, Any], calibration_report: Mapping[str, Any], index: int, dep: Mapping[str, Any]) -> Dict[str, Any]:
    ident = candidate_id(raw_item, index)
    frontier = frontier_score(scoring_item)
    successor = successor_score(scoring_item)
    reward = reward_score(scoring_item)
    gate = promotion_gate(raw_item)
    validation = validation_bundle(raw_item)
    calibration = {
        "frontier": formula_calibration(calibration_report, "frontier"),
        "successor": formula_calibration(calibration_report, "successor"),
        "reward": formula_calibration(calibration_report, "reward"),
    }
    unresolved = not bool(raw_item.get("resolved", False))
    rankable_frontier = (
        unresolved
        and dep.get("ready", True)
        and gate["status"] == "PASS"
        and validation["promotion_allowed"]
        and calibration["frontier"]["ranking_allowed"]
        and frontier["status"] == "KNOWN"
    )
    rankable_successor = (
        unresolved
        and dep.get("ready", True)
        and gate["status"] == "PASS"
        and validation["promotion_allowed"]
        and calibration["successor"]["ranking_allowed"]
        and successor["status"] == "KNOWN"
    )
    unknown = sorted(set(frontier.get("missing", []) + successor.get("missing", []) + reward.get("missing", [])))
    return {
        "id": ident,
        "resolved": not unresolved,
        "dependency": dep,
        "gate": gate,
        "validation": validation,
        "metric_calibration": calibration,
        "metric_report": dict(calibration_report),
        "scores": {"frontier": frontier, "successor": successor, "reward": reward},
        "rankable_frontier": rankable_frontier,
        "rankable_successor": rankable_successor,
        "unknown_metrics": unknown,
        "allocation": _allocation(raw_item, reward, calibration["reward"], gate, dep, validation),
        "source": dict(raw_item),
        "scoring_source": dict(scoring_item),
    }


def _frontier_sort(row: Mapping[str, Any]):
    return rank_key(row["scores"]["frontier"], str(row["id"]))


def _successor_sort(row: Mapping[str, Any]):
    score = row["scores"]["successor"]
    frontier = row["scores"]["frontier"]
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
        "metric_law": "cross-candidate arithmetic is performed on one declared basis; x'=(x-offset)/abs(scale). strict basis blocks formulas with uncalibrated/invalid operands; non-strict basis exposes WARN_RAW",
        "gap_law": "grow = argmax(severity * leverage * information_gain / cost) over KNOWN calibration-allowed residual scores",
        "frontier_law": "F = argmax(readiness * gain * independence * bridge / cost) over unresolved dependency-ready gate-passing validation-passing KNOWN calibration-allowed candidates",
        "successor_law": "next = structured highest successor route among budget-allocated unresolved dependency-ready gate-passing validation-passing KNOWN calibration-allowed candidates; no textual-order fallback",
        "pareto_law": "preserve all successor candidates not dominated on the same scoring basis over delta_j, information_gain, bridge, option_value and cost",
        "budget_law": "resource allocation maximizes sum(readiness*gain*independence*bridge) subject to raw resource_cost/cost capacity and max_branches; exact enumeration for <=18 costed candidates, otherwise explicitly heuristic greedy density",
        "reward": {"positive": list(REWARD_POSITIVE), "negative": list(REWARD_NEGATIVE), "reallocation": "known positive reward deepens/replicates/braids; low-reward duplicates hibernate without erasure; unknown reward routes to measurement"},
        "test": {"branches": list(TEST_BRANCHES), "claim_requires": ["procedure", "observation", "result", "witness"], "invalid_claim": "BLOCK_PROMOTION"},
        "transaction": {"stages": ["attempt", "action", "commit?", "receipt", "verify", "rollback?"], "persisted_claim_requires": ["commit", "receipt", "verify"], "invalid_claim": "BLOCK_PROMOTION", "fake_success": False},
        "allocation": {"high_reward": ["deepen", "replicate", "braid"], "low_reward_duplicate": ["hibernate"], "unknown_reward": ["measure"], "uncalibrated_strict_reward": ["calibrate_metrics"], "dependency_blocked": ["resolve_dependency"], "gate_or_validation_blocked": ["branch", "repair", "retest"], "hibernate_is_erase": False},
        "continuation": {"deadend": ["backtrack", "nearest_live_branch", "reseed_from_residual"], "stop": "only when requested object complete and no actionable frontier/residual/measurement/calibration/dependency pressure remains"},
        "carrier_budget_law": "P* = argmax_|P|<=B(development + extraction + graph + coordinates + evidence + replay + navigation + successor)",
    }


def compile_orchestration(
    seed: Any,
    candidates: Optional[Iterable[Mapping[str, Any]]] = None,
    residuals: Optional[Iterable[Mapping[str, Any]]] = None,
    budget: Optional[Mapping[str, Any]] = None,
    metric_contract: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    source_candidates = [dict(item) for item in (candidates or [])]
    unique: Dict[str, Dict[str, Any]] = {}
    duplicate_ids: List[str] = []
    for index, item in enumerate(source_candidates):
        ident = candidate_id(item, index)
        if ident in unique:
            duplicate_ids.append(ident)
            continue
        unique[ident] = item
    source_candidates = list(unique.values())

    dep_graph = dependency_graph(source_candidates)
    rows = []
    calibration_plan = []
    for index, raw_item in enumerate(source_candidates):
        ident = candidate_id(raw_item, index)
        scoring_item, calibration_report = normalize_item(raw_item, metric_contract)
        row = _candidate_row(raw_item, scoring_item, calibration_report, index, dep_graph["readiness"].get(ident, {"ready": True, "blockers": []}))
        rows.append(row)
        calibration_plan.extend(calibration_requests(ident, calibration_report))

    frontier = sorted(rows, key=_frontier_sort)
    executable_frontier = [row for row in frontier if row["rankable_frontier"]]
    successor_frontier = sorted((row for row in rows if row["rankable_successor"]), key=_successor_sort)
    measurement_frontier = [row for row in frontier if row["unknown_metrics"]]
    calibration_frontier = [row for row in frontier if any((row["metric_calibration"][name]["status"] == "BLOCKED") for name in ("frontier", "successor", "reward"))]
    validation_frontier = [row for row in frontier if row["validation"]["status"] == "BLOCKED"]
    measurement_plan = measurement_requests(frontier)
    pareto_ids = pareto_successor_frontier(successor_frontier)

    allocation_plan = allocate_budget(executable_frontier, budget)
    budget_active = bool((budget or {}).get("total_cost") is not None or (budget or {}).get("max_branches") is not None)
    allocated_ids = set(allocation_plan.get("selected", []))
    if allocation_plan.get("status") == "INVALID_BUDGET":
        budgeted_successor_frontier = []
    elif budget_active:
        budgeted_successor_frontier = [row for row in successor_frontier if row["id"] in allocated_ids]
    else:
        budgeted_successor_frontier = successor_frontier

    residual_rows = []
    for index, raw_item in enumerate(residuals or []):
        raw_item = dict(raw_item)
        ident = str(raw_item.get("id") or raw_item.get("name") or f"residual:{index:04d}")
        scoring_item, calibration_report = normalize_item(raw_item, metric_contract)
        calibration = formula_calibration(calibration_report, "residual")
        residual_rows.append({"id": ident, "score": residual_score(scoring_item), "metric_calibration": calibration, "metric_report": calibration_report, "source": raw_item, "scoring_source": scoring_item})
        for request in calibration_requests(ident, calibration_report):
            if request["formula"] == "residual": calibration_plan.append(request)
    residual_frontier = sorted(residual_rows, key=lambda row: rank_key(row["score"], row["id"]))
    known_residuals = [row for row in residual_frontier if row["score"]["status"] == "KNOWN" and row["metric_calibration"]["ranking_allowed"]]

    next_row = budgeted_successor_frontier[0] if budgeted_successor_frontier else None
    next_id = next_row["id"] if next_row else None
    explanation = decision_explanation(frontier, next_id, allocated_ids, budget_active)
    metric_summary = contract_summary(metric_contract)
    reward_reallocation = reallocation_plan(frontier)
    calibration_plan = sorted(calibration_plan, key=lambda x: (not x["strict_block"], x["candidate"], x["formula"]))
    successor = successor_packet(
        next_row,
        budgeted_successor_frontier,
        known_residuals,
        measurement_plan,
        calibration_plan,
        dep_graph["cycles"],
        (budget or {}).get("return_coordinate"),
    )
    decision = {
        "metric_basis": metric_summary,
        "budget_allocation": {k: allocation_plan.get(k) for k in ("status","solver","optimality","capacity","max_branches","selected","used","remaining","utility")},
        "executable_frontier": [row["id"] for row in executable_frontier],
        "successor_frontier": [row["id"] for row in successor_frontier],
        "budgeted_successor_frontier": [row["id"] for row in budgeted_successor_frontier],
        "pareto_successor_frontier": pareto_ids,
        "measurement_frontier": [row["id"] for row in measurement_frontier],
        "calibration_frontier": [row["id"] for row in calibration_frontier],
        "validation_frontier": [row["id"] for row in validation_frontier],
        "grow": known_residuals[0]["id"] if known_residuals else None,
        "next": next_id,
        "successor_status": successor["status"],
        "dependency_cycles": dep_graph["cycles"],
        "reallocation": {"active": reward_reallocation["active"], "blocked": reward_reallocation["blocked"], "dormant": reward_reallocation["dormant"]},
    }

    result = {
        "kernel": AOR_VERSION,
        "seed": seed,
        "budget": dict(budget or {}),
        "allocation_plan": allocation_plan,
        "reward_reallocation": reward_reallocation,
        "metric_contract": metric_summary,
        "law": orchestration_law(),
        "extraction_plan": [{"transform": transform, "seed": seed} for transform in TRANSFORMS],
        "candidate_dedup": {"mode": "explicit_identity_only", "duplicate_ids": duplicate_ids},
        "dependency_graph": dep_graph,
        "frontier": frontier,
        "executable_frontier": executable_frontier,
        "successor_frontier": successor_frontier,
        "budgeted_successor_frontier": budgeted_successor_frontier,
        "pareto_successor_frontier": pareto_ids,
        "measurement_frontier": measurement_frontier,
        "measurement_plan": measurement_plan,
        "calibration_frontier": calibration_frontier,
        "calibration_plan": calibration_plan,
        "validation_frontier": validation_frontier,
        "residual_frontier": residual_frontier,
        "grow": known_residuals[0] if known_residuals else None,
        "next": next_row,
        "successor": successor,
        "decision_explanation": explanation,
        "return": {"required": ["result", "math", "graph", "coordinates", "evidence", "residuals", "witnesses", "delta", "next"], "missing_witness": "downgrade_and_block_claimed_test", "missing_coordinate": "repair_before_promotion", "unknown_metric": "measure_not_zero", "uncalibrated_metric": "calibrate_before_ranking_when_strict", "dependency_blocked": "resolve_dependency", "invalid_budget": "block_budgeted_successor", "invalid_persistence_claim": "block_promotion_until_commit_receipt_verify", "error": ["rollback", "branch"], "high_residual": "continue"},
    }
    result["decision_digest"] = _decision_digest(decision)
    return result
