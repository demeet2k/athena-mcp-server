from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Iterable, Mapping, Optional

from .orchestration import compile_orchestration
from .orchestration_authority_gate import authority_gate
from .orchestration_budget import allocate_budget
from .orchestration_explain import decision_explanation, pareto_successor_frontier


def _digest(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _apply_authority(rows):
    authority_frontier = []
    authority_plan = []
    for row in rows:
        gate = authority_gate(row.get("source") or {})
        row.setdefault("gate", {}).setdefault("gates", {})["authority"] = gate
        if not gate["promotion_allowed"]:
            row["gate"]["status"] = "BLOCKED"
            blocked = row["gate"].setdefault("blocked_by", [])
            if "authority" not in blocked:
                blocked.append("authority")
            row["rankable_frontier"] = False
            row["rankable_successor"] = False
            row["allocation"] = [gate["route"]]
            authority_frontier.append(row)
            authority_plan.append({
                "candidate": row["id"],
                "route": gate["route"],
                "reason": gate["reason"],
                "minimum": gate.get("minimum"),
                "current": gate.get("current"),
                "authority_status": gate.get("authority_status"),
            })
    return authority_frontier, sorted(authority_plan, key=lambda x: x["candidate"])


def compile_authority_orchestration(
    seed: Any,
    candidates: Optional[Iterable[Mapping[str, Any]]] = None,
    residuals: Optional[Iterable[Mapping[str, Any]]] = None,
    budget: Optional[Mapping[str, Any]] = None,
    metric_contract: Optional[Mapping[str, Any]] = None,
):
    """Compile AOR using already-snapshotted authority_state on candidates.

    This function intentionally does not query a live AuthorityLedger. Callers
    enrich candidates first, then persist those snapshots in AORRUN input.
    Replay can therefore use the exact historical snapshot after live claim
    authority changes.
    """
    result = copy.deepcopy(compile_orchestration(
        seed=seed,
        candidates=candidates,
        residuals=residuals,
        budget=budget,
        metric_contract=metric_contract,
    ))

    rows = result["frontier"]
    authority_frontier, authority_plan = _apply_authority(rows)
    executable = [row for row in rows if row.get("rankable_frontier")]

    # The base compiler's successor order is already deterministic. Filter that
    # ordering by the authority-adjusted eligibility rather than inventing a
    # second ranking law.
    eligible = {row["id"] for row in rows if row.get("rankable_successor")}
    base_order = [row["id"] for row in result["successor_frontier"]]
    by_id = {row["id"]: row for row in rows}
    successor = [by_id[ident] for ident in base_order if ident in eligible]

    pareto_ids = pareto_successor_frontier(successor)
    allocation = allocate_budget(executable, budget)
    budget_active = bool((budget or {}).get("total_cost") is not None or (budget or {}).get("max_branches") is not None)
    allocated = set(allocation.get("selected", []))
    if allocation.get("status") == "INVALID_BUDGET":
        budgeted_successor = []
    elif budget_active:
        budgeted_successor = [row for row in successor if row["id"] in allocated]
    else:
        budgeted_successor = successor

    next_row = budgeted_successor[0] if budgeted_successor else None
    next_id = next_row["id"] if next_row else None
    explanation = decision_explanation(rows, next_id, allocated, budget_active)

    authority_snapshot = {
        row["id"]: {
            "claim_id": (row.get("source") or {}).get("claim_id"),
            "min_authority": (row.get("source") or {}).get("min_authority"),
            "authority_state": copy.deepcopy((row.get("source") or {}).get("authority_state")),
            "gate": copy.deepcopy(row["gate"]["gates"]["authority"]),
        }
        for row in rows
        if (row.get("source") or {}).get("claim_id") or (row.get("source") or {}).get("min_authority") is not None
    }

    result.update({
        "frontier": rows,
        "executable_frontier": executable,
        "successor_frontier": successor,
        "budgeted_successor_frontier": budgeted_successor,
        "pareto_successor_frontier": pareto_ids,
        "authority_frontier": authority_frontier,
        "authority_plan": authority_plan,
        "authority_snapshot": authority_snapshot,
        "allocation_plan": allocation,
        "next": next_row,
        "decision_explanation": explanation,
    })

    decision = {
        "metric_basis": result.get("metric_contract"),
        "budget_allocation": {
            key: allocation.get(key)
            for key in ("status", "solver", "optimality", "capacity", "max_branches", "selected", "used", "remaining", "utility")
        },
        "authority_snapshot": authority_snapshot,
        "executable_frontier": [row["id"] for row in executable],
        "successor_frontier": [row["id"] for row in successor],
        "budgeted_successor_frontier": [row["id"] for row in budgeted_successor],
        "pareto_successor_frontier": pareto_ids,
        "measurement_frontier": [row["id"] for row in result.get("measurement_frontier", [])],
        "calibration_frontier": [row["id"] for row in result.get("calibration_frontier", [])],
        "grow": (result.get("grow") or {}).get("id"),
        "next": next_id,
        "dependency_cycles": result.get("dependency_graph", {}).get("cycles", []),
    }
    result["decision_digest"] = _digest(decision)
    return result
