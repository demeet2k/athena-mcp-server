from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping


def _known_reward(row: Mapping[str, Any]):
    score = (row.get("scores") or {}).get("reward") or {}
    if score.get("status") != "KNOWN":
        return None
    try:
        return float(score.get("value"))
    except (TypeError, ValueError):
        return None


def reallocation_plan(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Compile candidate-local allocation decisions into an organism-level plan.

    Hibernation preserves identity/lineage. Nothing here authorizes deletion.
    """
    actions: Dict[str, List[str]] = {}
    buckets = {
        "deepen": [], "replicate": [], "braid": [], "hibernate": [],
        "measure": [], "calibrate_metrics": [], "resolve_dependency": [],
        "repair": [], "retain": [],
    }
    reward_values = []
    for row in rows:
        ident = str(row.get("id"))
        local = list(row.get("allocation") or [])
        actions[ident] = local
        reward = _known_reward(row)
        if reward is not None:
            reward_values.append({"id": ident, "reward": reward})
        for action in local:
            buckets.setdefault(action, []).append(ident)

    reward_values.sort(key=lambda x: (-x["reward"], x["id"]))
    counts = Counter(action for local in actions.values() for action in local)
    active = sorted(set(buckets.get("deepen", []) + buckets.get("replicate", []) + buckets.get("braid", []) + buckets.get("retain", [])))
    blocked = sorted(set(buckets.get("measure", []) + buckets.get("calibrate_metrics", []) + buckets.get("resolve_dependency", []) + buckets.get("repair", [])))
    dormant = sorted(set(buckets.get("hibernate", [])))
    return {
        "actions": actions,
        "counts": dict(sorted(counts.items())),
        "active": active,
        "blocked": blocked,
        "dormant": dormant,
        "reward_order": reward_values,
        "laws": {
            "high_reward": ["deepen", "replicate", "braid"],
            "low_reward_duplicate": ["hibernate"],
            "hibernate_is_erase": False,
            "resurrection": "new evidence | residual | bridge demand may return dormant identity to frontier",
        },
    }


def reward_delta(before: Mapping[str, Any], after: Mapping[str, Any]) -> Dict[str, Any]:
    """Measure a small public reward-state delta without claiming causality."""
    keys = (
        "capability", "evidence", "connection", "replay", "navigation",
        "reconstruction", "implementation", "novelty",
    )
    delta = {}
    unknown = []
    for key in keys:
        if key not in before or key not in after:
            unknown.append(key)
            continue
        try:
            delta[key] = float(after[key]) - float(before[key])
        except (TypeError, ValueError):
            unknown.append(key)
    return {
        "delta": delta,
        "unknown": unknown,
        "status": "KNOWN" if not unknown else ("PARTIAL" if delta else "UNKNOWN"),
        "causal_claim": False,
    }
