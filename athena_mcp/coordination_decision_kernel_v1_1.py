from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from athena_mcp.coordination_decision_kernel_v1 import (
    ARTIFACT as PARENT_ARTIFACT,
    VERSION as PARENT_VERSION,
    decide_coordination as decide_parent,
)

ARTIFACT = "ATHENA.COORDINATION.DECISION.KERNEL.V1.1"
VERSION = "COORDINATION.DECISION.KERNEL.V1.1"
BRANCH_CONTEXTS = {"NONE", "CLEAN_OWNED", "POLLUTED"}


def _result(
    decision_class: str,
    *,
    continuation_status: str,
    reasons: list[str],
) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "DECIDED",
        "decision_class": decision_class,
        "continuation_status": continuation_status,
        "reasons": reasons,
        "secondary_actions": [],
        "hard_gate_status": "PASS",
        "authority_delta": "NONE",
        "execution_effect": "NONE_DECISION_ONLY",
        "parent_kernel": f"{PARENT_ARTIFACT}@{PARENT_VERSION}",
    }


def decide_coordination(observed_state: Mapping[str, Any]) -> dict[str, Any]:
    """V1.1: preserve V1 rules and add explicit clean-branch keep semantics."""

    if not isinstance(observed_state, Mapping):
        parent = decide_parent(observed_state)
        return {**parent, "artifact": ARTIFACT, "version": VERSION}

    branch_context = observed_state.get("branch_context", "NONE")
    if not isinstance(branch_context, str) or branch_context not in BRANCH_CONTEXTS:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "HOLD",
            "decision_class": "INPUT_HOLD",
            "continuation_status": "HELD",
            "reasons": [f"ValueError:branch_context invalid: {branch_context!r}"],
            "secondary_actions": [],
            "hard_gate_status": "HOLD",
            "authority_delta": "NONE",
            "execution_effect": "NONE_DECISION_ONLY",
            "parent_kernel": f"{PARENT_ARTIFACT}@{PARENT_VERSION}",
        }

    state = dict(observed_state)
    state.pop("branch_context", None)

    if branch_context == "POLLUTED":
        state["context_polluted"] = True
    elif branch_context == "CLEAN_OWNED":
        state["context_polluted"] = False
        # If another higher-priority obstruction exists, V1 still owns the decision.
        higher_priority = any(
            (
                state.get("master_moved", False),
                state.get("hold_active", False),
                state.get("collision_relation", "NONE") != "NONE",
            )
        )
        if not higher_priority:
            return _result(
                "KEEP_BRANCH",
                continuation_status="CONTINUE_ON_CURRENT_LINEAGE",
                reasons=["BRANCH_CONTEXT_CLEAN_OWNED"],
            )

    parent = decide_parent(state)
    return {
        **parent,
        "artifact": ARTIFACT,
        "version": VERSION,
        "parent_kernel": f"{PARENT_ARTIFACT}@{PARENT_VERSION}",
    }
