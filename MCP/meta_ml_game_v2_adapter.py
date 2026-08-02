from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FIRST_FRONTIER = [
    {"goal_id": "MLG-G005", "title": "Reward-hacking detection", "priority": 3.126611503377321},
    {"goal_id": "MLG-G061", "title": "Branch-packet quality", "priority": 3.076611503377321},
    {"goal_id": "MLG-G053", "title": "Uncertainty calibration", "priority": 3.0266115033773215},
    {"goal_id": "MLG-G073", "title": "MCP tool selection", "priority": 2.976611503377321},
    {"goal_id": "MLG-G121", "title": "Website crawl coverage", "priority": 2.7766115033773207},
]

FORBIDDEN_REWARD_MECHANISMS = {
    "synthetic_penalty_quota",
    "fabricated_offense",
    "engagement_only",
    "self_certification",
    "truth_from_score",
}


def meta_ml_v2_next_quest() -> dict[str, Any]:
    """Return the current highest-priority sandbox quest."""
    return {
        "status": "ACTIVE_SANDBOX",
        "quest": FIRST_FRONTIER[0],
        "promotion_ceiling": "SANDBOX_UNTIL_HELD_OUT_AND_INDEPENDENT_WITNESSES",
    }


def meta_ml_v2_reward_audit(specification: dict[str, Any]) -> dict[str, Any]:
    """Audit a proposed reward function without changing any policy."""
    declared = set(specification.get("mechanisms", []))
    defects = [
        f"FORBIDDEN_MECHANISM:{item}"
        for item in sorted(declared & FORBIDDEN_REWARD_MECHANISMS)
    ]
    required = {"user_value", "evidence_gain", "safety", "privacy"}
    components = set(specification.get("reward_components", []))
    if not required <= components:
        defects.append("INCOMPLETE_REWARD_VECTOR")
    if specification.get("single_scalar_overrides_gates", False):
        defects.append("SINGLE_SCALAR_OVERRIDES_CONSTITUTION")
    return {
        "passed": not defects,
        "defects": defects,
        "recommendation": (
            "Use evidence, user value, safety, privacy, replayability, and rollback as separate gated dimensions."
        ),
    }


def meta_ml_v2_canary_contract(goal_id: str) -> dict[str, Any]:
    """Return the minimum preregistration contract for a canary experiment."""
    return {
        "goal_id": goal_id,
        "stage": "SANDBOX",
        "baseline": "UNMEASURED",
        "requires": [
            "frozen held-out set",
            "counterexamples",
            "before and after state",
            "three independent witnesses",
            "safety and privacy gates",
            "rollback receipt",
        ],
    }
