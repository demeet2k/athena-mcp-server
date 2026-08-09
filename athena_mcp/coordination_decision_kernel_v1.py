from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ARTIFACT = "ATHENA.COORDINATION.DECISION.KERNEL.V1"
VERSION = "COORDINATION.DECISION.KERNEL.V1"

COLLISION_RELATIONS = {
    "NONE",
    "IDENTICAL",
    "OVERLAPPING_COMPLEMENTARY",
    "MATERIAL_DIFFERENCE",
    "COMPETING_HYPOTHESIS",
    "CONFLICTING",
    "UNKNOWN",
}
HOLD_SCOPES = {
    "NONE",
    "OBJECT_LOCAL",
    "LANE_LOCAL",
    "CLUSTER_LOCAL",
    "CAMPAIGN_LOCAL",
    "GLOBAL",
}
MASTER_DELTA_RELATIONS = {"NONE", "DISJOINT", "CONFLICTING", "UNKNOWN"}
VALUE_STATES = {"POSITIVE", "NONPOSITIVE", "UNKNOWN"}


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be boolean")
    return value


def _enum(value: Any, allowed: set[str], field: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{field} invalid: {value!r}")
    return value


def _int_nonnegative(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be nonnegative integer")
    return value


def _result(
    decision_class: str,
    *,
    continuation_status: str,
    reasons: list[str],
    secondary_actions: list[str] | None = None,
    hard_gate_status: str = "PASS",
) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "DECIDED",
        "decision_class": decision_class,
        "continuation_status": continuation_status,
        "reasons": reasons,
        "secondary_actions": list(secondary_actions or []),
        "hard_gate_status": hard_gate_status,
        "authority_delta": "NONE",
        "execution_effect": "NONE_DECISION_ONLY",
    }


def decide_coordination(observed_state: Mapping[str, Any]) -> dict[str, Any]:
    """Pure collision/hold/freshness reducer over public-state predicates.

    The kernel intentionally does not inspect task prose, expected labels, reward
    state, private reasoning, or provider credentials. It returns a routing
    decision only; callers must separately establish authority and execute work.
    """

    try:
        if not isinstance(observed_state, Mapping):
            raise ValueError("observed_state must be object")
        allowed_keys = {
            "collision_relation",
            "context_polluted",
            "master_moved",
            "master_delta_relation",
            "hold_active",
            "hold_scope",
            "dependency_changed",
            "reopening_predicate_satisfied",
            "held_lane_value",
            "orthogonal_positive_lanes",
            "information_action_available",
            "shared_target_mutation_pending",
        }
        unknown = sorted(set(observed_state) - allowed_keys)
        if unknown:
            raise ValueError(f"unknown fields: {unknown}")

        collision = _enum(
            observed_state.get("collision_relation", "NONE"),
            COLLISION_RELATIONS,
            "collision_relation",
        )
        context_polluted = _bool(
            observed_state.get("context_polluted", False), "context_polluted"
        )
        master_moved = _bool(
            observed_state.get("master_moved", False), "master_moved"
        )
        master_delta = _enum(
            observed_state.get("master_delta_relation", "NONE"),
            MASTER_DELTA_RELATIONS,
            "master_delta_relation",
        )
        hold_active = _bool(
            observed_state.get("hold_active", False), "hold_active"
        )
        hold_scope = _enum(
            observed_state.get("hold_scope", "NONE"), HOLD_SCOPES, "hold_scope"
        )
        dependency_changed = _bool(
            observed_state.get("dependency_changed", False), "dependency_changed"
        )
        reopening = _bool(
            observed_state.get("reopening_predicate_satisfied", False),
            "reopening_predicate_satisfied",
        )
        held_value = _enum(
            observed_state.get("held_lane_value", "UNKNOWN"),
            VALUE_STATES,
            "held_lane_value",
        )
        orthogonal = _int_nonnegative(
            observed_state.get("orthogonal_positive_lanes", 0),
            "orthogonal_positive_lanes",
        )
        info_action = _bool(
            observed_state.get("information_action_available", False),
            "information_action_available",
        )
        mutation_pending = _bool(
            observed_state.get("shared_target_mutation_pending", False),
            "shared_target_mutation_pending",
        )

        if hold_active and hold_scope == "NONE":
            raise ValueError("hold_active requires non-NONE hold_scope")
        if not hold_active and hold_scope != "NONE":
            raise ValueError("non-NONE hold_scope requires hold_active")
        if reopening and not hold_active:
            raise ValueError("reopening predicate requires active hold")
        if dependency_changed and not hold_active:
            raise ValueError("dependency_changed requires active hold")
        if master_moved and master_delta == "NONE":
            raise ValueError("master_moved requires classified/UNKNOWN master delta")
        if not master_moved and master_delta != "NONE":
            raise ValueError("master delta relation requires master_moved")

        # A global hard boundary dominates every local coordination convenience.
        if hold_active and hold_scope == "GLOBAL" and not reopening:
            return _result(
                "GLOBAL_HOLD",
                continuation_status="HELD",
                reasons=["GLOBAL_BOUNDARY_ACTIVE"],
                hard_gate_status="HOLD",
            )

        # Reopening is event-driven and takes precedence over reserve routing.
        if hold_active and reopening:
            return _result(
                "REOPEN_HELD_LANE",
                continuation_status="RECHECK_ACTIVE_LANE",
                reasons=["REOPENING_PREDICATE_SATISFIED"],
            )

        # Shared-frontier drift is resolved before a mutable continuation.
        if master_moved:
            if master_delta == "DISJOINT":
                return _result(
                    "REBRAID_REQUALIFY",
                    continuation_status="CONTINUE_AFTER_REQUALIFICATION",
                    reasons=["SHARED_FRONTIER_MOVED", "DELTA_CLASSIFIED_DISJOINT"],
                )
            if master_delta == "CONFLICTING":
                return _result(
                    "CONFLICT_HOLD",
                    continuation_status="HELD",
                    reasons=["SHARED_FRONTIER_MOVED", "SEMANTIC_CONFLICT"],
                    hard_gate_status="HOLD",
                )
            return _result(
                "REHYDRATE_COMPARE_PARENT",
                continuation_status="RECHECK_BEFORE_MUTATION",
                reasons=["SHARED_FRONTIER_MOVED", "DELTA_RELATION_UNKNOWN"],
                hard_gate_status="HOLD" if mutation_pending else "PASS",
            )

        # Context pollution is a lineage/comparison defect independent of file semantics.
        if context_polluted:
            return _result(
                "FORK_CLEAN",
                continuation_status="CONTINUE_ON_CLEAN_LINEAGE",
                reasons=["COMPARISON_CONTEXT_POLLUTED"],
            )

        # Collision relation chooses consume/fuse/competition behavior.
        if collision == "IDENTICAL":
            return _result(
                "CONSUME_SIBLING",
                continuation_status="CONTINUE_FROM_SIBLING_DELTA",
                reasons=["IDENTICAL_DUPLICATE"],
            )
        if collision == "OVERLAPPING_COMPLEMENTARY":
            return _result(
                "COMPARE_FUSE",
                continuation_status="CONTINUE_AFTER_FUSION",
                reasons=["COMPLEMENTARY_OVERLAP"],
            )
        if collision == "MATERIAL_DIFFERENCE":
            return _result(
                "COMPARE_REJECT_OR_FUSE",
                continuation_status="DISCRIMINATE_BEFORE_CONTINUE",
                reasons=["SIBLING_MATERIALLY_DIFFERENT"],
            )
        if collision == "COMPETING_HYPOTHESIS":
            return _result(
                "PRESERVE_COMPETING_HYPOTHESES",
                continuation_status="EXPERIMENT_BEFORE_CANONICALIZATION",
                reasons=["INTENTIONAL_ORTHOGONAL_COMPETITION"],
            )
        if collision == "CONFLICTING":
            return _result(
                "CONFLICT_HOLD",
                continuation_status="HELD",
                reasons=["COLLISION_SEMANTIC_CONFLICT"],
                hard_gate_status="HOLD",
            )
        if collision == "UNKNOWN":
            return _result(
                "COMPARE_RELATION",
                continuation_status="DISCRIMINATE_BEFORE_CONTINUE",
                reasons=["COLLISION_RELATION_UNKNOWN"],
            )

        # An unrelated event does not justify repeatedly reopening a held lane.
        if hold_active and not dependency_changed:
            if held_value == "POSITIVE":
                secondary = ["CONTINUE_ORTHOGONAL"] if orthogonal > 0 else []
                return _result(
                    "PRESERVE_VALUE_IN_RESERVE",
                    continuation_status=(
                        "CONTINUE_ORTHOGONAL" if orthogonal > 0 else "HELD_RESERVE"
                    ),
                    reasons=["HELD_HIGH_VALUE_NONEXECUTABLE", "DEPENDENCY_UNCHANGED"],
                    secondary_actions=secondary,
                )
            if orthogonal > 0:
                return _result(
                    "HOLD_LOCAL_CONTINUE_ORTHOGONAL",
                    continuation_status="CONTINUE_ORTHOGONAL",
                    reasons=["LOCAL_HOLD", "ORTHOGONAL_POSITIVE_FRONTIER"],
                )
            if info_action:
                return _result(
                    "INFORMATION_ACTION",
                    continuation_status="CONTINUE_INFORMATION_GAIN",
                    reasons=["NO_EXECUTABLE_LANE", "REOPENING_INFORMATION_AVAILABLE"],
                )
            return _result(
                "GLOBAL_TYPED_STOP",
                continuation_status="STOP_GLOBAL",
                reasons=["NO_POSITIVE_EXECUTABLE_FRONTIER"],
            )

        # A dependency changed but did not satisfy the reopening predicate.
        if hold_active and dependency_changed:
            if orthogonal > 0:
                return _result(
                    "PRESERVE_HOLD",
                    continuation_status="CONTINUE_ORTHOGONAL",
                    reasons=["DEPENDENCY_CHANGED", "REOPENING_PREDICATE_NOT_SATISFIED"],
                    secondary_actions=["CONTINUE_ORTHOGONAL"],
                )
            if info_action:
                return _result(
                    "INFORMATION_ACTION",
                    continuation_status="CONTINUE_INFORMATION_GAIN",
                    reasons=["DEPENDENCY_CHANGED", "REOPENING_STILL_UNRESOLVED"],
                )
            return _result(
                "PRESERVE_HOLD",
                continuation_status="HELD",
                reasons=["DEPENDENCY_CHANGED", "REOPENING_PREDICATE_NOT_SATISFIED"],
            )

        # No collision, no hold and no frontier movement: avoid synthetic work.
        if orthogonal > 0:
            return _result(
                "QUIET_SUCCESSOR",
                continuation_status="CONTINUE_POSITIVE_FRONTIER",
                reasons=["POSITIVE_LAWFUL_FRONTIER"],
            )
        if info_action:
            return _result(
                "INFORMATION_ACTION",
                continuation_status="CONTINUE_INFORMATION_GAIN",
                reasons=["NO_EXECUTION_FRONTIER", "POSITIVE_INFORMATION_VALUE"],
            )
        return _result(
            "STOP_SUCCESS",
            continuation_status="STOP_GLOBAL",
            reasons=["NO_POSITIVE_LAWFUL_FRONTIER"],
        )
    except (TypeError, ValueError) as exc:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "HOLD",
            "decision_class": "INPUT_HOLD",
            "continuation_status": "HELD",
            "reasons": [f"{type(exc).__name__}:{exc}"],
            "secondary_actions": [],
            "hard_gate_status": "HOLD",
            "authority_delta": "NONE",
            "execution_effect": "NONE_DECISION_ONLY",
        }
