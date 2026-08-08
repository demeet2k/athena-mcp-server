from __future__ import annotations

from typing import Any, Dict, Mapping

from .orchestration_authority import AUTHORITY_ORDER

CHALLENGED = {"CHALLENGED", "CANONICAL_CHALLENGED"}


def authority_gate(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    """Evaluate public typed authority state without inferring confidence or truth."""
    minimum = candidate.get("min_authority")
    state = candidate.get("authority_state") or {}
    current = state.get("y")
    status = str(state.get("status") or "UNTRACKED").upper()

    if minimum is not None and minimum not in AUTHORITY_ORDER:
        return {
            "status": "BLOCKED",
            "promotion_allowed": False,
            "route": "invalid_min_authority",
            "reason": "min_authority must be one of ?,+,!,#",
            "minimum": minimum,
            "current": current,
            "authority_status": status,
        }

    # A material challenge blocks automatic routing for linked claims even when
    # a caller forgot to declare min_authority. Exploration can continue by
    # creating an unlinked hypothesis candidate; the challenged claim itself
    # must be resolved rather than silently reused.
    if status in CHALLENGED:
        return {
            "status": "BLOCKED",
            "promotion_allowed": False,
            "route": "resolve_canonical_challenge" if status == "CANONICAL_CHALLENGED" else "resolve_challenge",
            "reason": status.lower(),
            "minimum": minimum,
            "current": current,
            "authority_status": status,
        }

    if minimum is None:
        return {
            "status": "PASS",
            "promotion_allowed": True,
            "route": "explore",
            "reason": "no minimum authority declared",
            "minimum": None,
            "current": current,
            "authority_status": status,
        }

    if not state or current not in AUTHORITY_ORDER:
        return {
            "status": "BLOCKED",
            "promotion_allowed": False,
            "route": "resolve_or_register_claim",
            "reason": "missing_authority_state",
            "minimum": minimum,
            "current": current,
            "authority_status": status,
        }

    if AUTHORITY_ORDER[current] < AUTHORITY_ORDER[minimum]:
        route = {
            "+": "gather_verified_support",
            "!": "execute_witnessed_test",
            "#": "obtain_canonical_authority",
        }.get(minimum, "resolve_authority")
        return {
            "status": "BLOCKED",
            "promotion_allowed": False,
            "route": route,
            "reason": "authority_below_minimum",
            "minimum": minimum,
            "current": current,
            "authority_status": status,
        }

    return {
        "status": "PASS",
        "promotion_allowed": True,
        "route": "authority_satisfied",
        "reason": "minimum_authority_satisfied",
        "minimum": minimum,
        "current": current,
        "authority_status": status,
    }
