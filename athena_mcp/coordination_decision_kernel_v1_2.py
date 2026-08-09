from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from athena_mcp.coordination_decision_kernel_v1_1 import (
    ARTIFACT as PARENT_ARTIFACT,
    VERSION as PARENT_VERSION,
    decide_coordination as decide_parent,
)

ARTIFACT = "ATHENA.COORDINATION.DECISION.KERNEL.V1.2"
VERSION = "COORDINATION.DECISION.KERNEL.V1.2"


def _overlay(result: Mapping[str, Any], *, secondary: list[str] | None = None) -> dict[str, Any]:
    base = dict(result)
    base["artifact"] = ARTIFACT
    base["version"] = VERSION
    base["parent_kernel"] = f"{PARENT_ARTIFACT}@{PARENT_VERSION}"
    if secondary:
        existing = list(base.get("secondary_actions", []))
        for action in secondary:
            if action not in existing:
                existing.append(action)
        base["secondary_actions"] = existing
    return base


def decide_coordination(observed_state: Mapping[str, Any]) -> dict[str, Any]:
    """V1.2 composition repair for noncommuting freshness/lineage/reopening rules."""

    if not isinstance(observed_state, Mapping):
        return _overlay(decide_parent(observed_state))

    state = dict(observed_state)
    hold_active = state.get("hold_active", False) is True
    hold_scope = state.get("hold_scope", "NONE")
    reopening = state.get("reopening_predicate_satisfied", False) is True
    master_moved = state.get("master_moved", False) is True
    master_delta = state.get("master_delta_relation", "NONE")
    branch_context = state.get("branch_context", "NONE")

    # Global unresolved boundaries remain dominant and are never routed around.
    if hold_active and hold_scope == "GLOBAL" and not reopening:
        return _overlay(decide_parent(state))

    # A reopening predicate observed on older shared coordinates is provisional.
    # Freshness must be restored before the held lane becomes active again.
    if reopening and master_moved:
        fresh_state = dict(state)
        fresh_state["reopening_predicate_satisfied"] = False
        result = decide_parent(fresh_state)
        return _overlay(
            result,
            secondary=["RECHECK_REOPENING_PREDICATE_AFTER_FRESHNESS"],
        )

    # Cleaning a contaminated comparison lineage precedes a safe disjoint braid;
    # otherwise the braid faithfully carries unrelated history forward.
    if branch_context == "POLLUTED" and master_moved:
        if master_delta == "DISJOINT":
            clean_state = dict(state)
            clean_state["master_moved"] = False
            clean_state["master_delta_relation"] = "NONE"
            result = decide_parent(clean_state)
            return _overlay(result, secondary=["REBRAID_REQUALIFY"])
        if master_delta == "CONFLICTING":
            result = {
                "status": "DECIDED",
                "decision_class": "CONFLICT_HOLD",
                "continuation_status": "HELD",
                "reasons": [
                    "COMPARISON_CONTEXT_POLLUTED",
                    "SHARED_FRONTIER_SEMANTIC_CONFLICT",
                ],
                "secondary_actions": ["FORK_CLEAN_WHEN_CONFLICT_ROUTE_RESOLVED"],
                "hard_gate_status": "HOLD",
                "authority_delta": "NONE",
                "execution_effect": "NONE_DECISION_ONLY",
            }
            return _overlay(result)
        if master_delta == "UNKNOWN":
            clean_state = dict(state)
            clean_state["master_moved"] = False
            clean_state["master_delta_relation"] = "NONE"
            result = decide_parent(clean_state)
            return _overlay(result, secondary=["REHYDRATE_COMPARE_PARENT"])

    return _overlay(decide_parent(state))
