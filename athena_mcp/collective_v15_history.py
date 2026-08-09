from __future__ import annotations

from typing import Any, Mapping, Sequence

from .collective_robust import _policy_action

_INTERNAL_HISTORY_NAMES={"A1","L1","A2","Y"}


def validate_longitudinal_baseline(
    baseline: Sequence[str] | None,
    treatment1: str,
    intermediate: str,
    treatment2: str,
    outcome: str,
) -> list[str]:
    """Validate the named time ordering before constructing normalized rows."""
    observed=[str(treatment1),str(intermediate),str(treatment2),str(outcome)]
    if len(set(observed)) != 4:
        raise ValueError("treatment1, intermediate, treatment2, and outcome must name four distinct observed fields")
    base=[str(name) for name in (baseline or [])]
    if len(set(base)) != len(base):
        raise ValueError("baseline feature names must be unique")
    overlap=set(base) & set(observed)
    if overlap:
        raise ValueError("baseline cannot include named treatment, intermediate, or outcome fields: "+", ".join(sorted(overlap)))
    internal=set(base) & _INTERNAL_HISTORY_NAMES
    if internal:
        raise ValueError("baseline feature names collide with normalized longitudinal history names: "+", ".join(sorted(internal)))
    return base


def policy_action_from_history(spec: Any, row: Mapping[str, Any], label: str, allowed_features: Sequence[str]) -> int:
    """Evaluate a supplied policy only on information available at that decision time."""
    allowed=[str(name) for name in allowed_features]
    if isinstance(spec,Mapping):
        coefficients=spec.get("coefficients") or {}
        if not isinstance(coefficients,Mapping):
            raise ValueError(f"{label} coefficients must be an object")
        refs={str(name) for name in coefficients}
        forbidden=sorted(refs-set(allowed))
        if forbidden:
            raise ValueError(f"{label} policy references unavailable or future features: {', '.join(forbidden)}")
    projected={name:row[name] for name in allowed}
    return _policy_action(spec,projected,label)
