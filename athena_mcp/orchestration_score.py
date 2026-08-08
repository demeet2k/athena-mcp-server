from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

REWARD_POSITIVE = (
    "delta_j", "evidence", "connection", "replay", "navigation",
    "reconstruction", "implementation", "novelty",
)
REWARD_NEGATIVE = (
    "duplicate", "fake", "bloat", "unsupported", "unhandled_contradiction",
    "coordinate_loss",
)
FRONTIER_METRICS = ("readiness", "gain", "independence", "bridge", "cost")
SUCCESSOR_METRICS = ("delta_j", "information_gain", "bridge", "option_value", "cost")
RESIDUAL_METRICS = ("severity", "leverage", "information_gain", "cost")


def finite_number(value: Any) -> Optional[float]:
    """Return a finite numeric value or None. UNKNOWN is never coerced to zero."""
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out != out or out in (float("inf"), float("-inf")):
        return None
    return out


def missing_metrics(item: Mapping[str, Any], names: Iterable[str]) -> list[str]:
    return [name for name in dict.fromkeys(names) if finite_number(item.get(name)) is None]


def _complete_values(item: Mapping[str, Any], names: Sequence[str]) -> Optional[Dict[str, float]]:
    values: Dict[str, float] = {}
    for name in names:
        value = finite_number(item.get(name))
        if value is None:
            return None
        values[name] = value
    return values


def _safe_cost(value: float) -> Optional[float]:
    value = abs(value)
    return value if value > 1e-12 else None


def frontier_score(item: Mapping[str, Any]) -> Dict[str, Any]:
    values = _complete_values(item, FRONTIER_METRICS)
    missing = missing_metrics(item, FRONTIER_METRICS)
    if values is None:
        return {"status": "UNKNOWN", "value": None, "missing": missing}
    cost = _safe_cost(values["cost"])
    if cost is None:
        return {"status": "INVALID", "value": None, "missing": [], "reason": "cost must be non-zero"}
    value = values["readiness"] * values["gain"] * values["independence"] * values["bridge"] / cost
    return {"status": "KNOWN", "value": value, "missing": []}


def successor_score(item: Mapping[str, Any]) -> Dict[str, Any]:
    values = _complete_values(item, SUCCESSOR_METRICS)
    missing = missing_metrics(item, SUCCESSOR_METRICS)
    if values is None:
        return {"status": "UNKNOWN", "value": None, "missing": missing}
    cost = _safe_cost(values["cost"])
    if cost is None:
        return {"status": "INVALID", "value": None, "missing": [], "reason": "cost must be non-zero"}
    value = values["delta_j"] * values["information_gain"] * values["bridge"] * values["option_value"] / cost
    return {"status": "KNOWN", "value": value, "missing": []}


def residual_score(item: Mapping[str, Any]) -> Dict[str, Any]:
    values = _complete_values(item, RESIDUAL_METRICS)
    missing = missing_metrics(item, RESIDUAL_METRICS)
    if values is None:
        return {"status": "UNKNOWN", "value": None, "missing": missing}
    cost = _safe_cost(values["cost"])
    if cost is None:
        return {"status": "INVALID", "value": None, "missing": [], "reason": "cost must be non-zero"}
    value = values["severity"] * values["leverage"] * values["information_gain"] / cost
    return {"status": "KNOWN", "value": value, "missing": []}


def reward_score(item: Mapping[str, Any]) -> Dict[str, Any]:
    names = REWARD_POSITIVE + REWARD_NEGATIVE
    values = _complete_values(item, names)
    missing = missing_metrics(item, names)
    if values is None:
        return {"status": "UNKNOWN", "value": None, "missing": missing}
    positive = sum(values[name] for name in REWARD_POSITIVE)
    negative = sum(values[name] for name in REWARD_NEGATIVE)
    return {
        "status": "KNOWN",
        "value": positive - negative,
        "positive": positive,
        "negative": negative,
        "missing": [],
    }


def rank_key(score: Mapping[str, Any], ident: str) -> tuple[int, float, str]:
    if score.get("status") == "KNOWN":
        return (0, -float(score["value"]), ident)
    return (1, 0.0, ident)
