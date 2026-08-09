from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from .collective_robust import _policy_action

_INTERNAL_HISTORY_NAMES={"A1","L1","A2","Y"}


def _finite(value: Any, label: str) -> float:
    x=float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite")
    return x


def validate_longitudinal_baseline(
    baseline: Sequence[str] | None,
    treatment1: str,
    intermediate: str,
    treatment2: str,
    outcome: str,
) -> list[str]:
    """Validate the named time ordering before constructing normalized rows."""
    observed=[str(treatment1),str(intermediate),str(treatment2),str(outcome)]
    if any(not name for name in observed):
        raise ValueError("longitudinal observed field names must be non-empty")
    if len(set(observed)) != 4:
        raise ValueError("treatment1, intermediate, treatment2, and outcome must name four distinct observed fields")
    base=[str(name) for name in (baseline or [])]
    if any(not name for name in base):
        raise ValueError("baseline feature names must be non-empty")
    if len(set(base)) != len(base):
        raise ValueError("baseline feature names must be unique")
    overlap=set(base) & set(observed)
    if overlap:
        raise ValueError("baseline cannot include named treatment, intermediate, or outcome fields: "+", ".join(sorted(overlap)))
    internal=set(base) & _INTERNAL_HISTORY_NAMES
    if internal:
        raise ValueError("baseline feature names collide with normalized longitudinal history names: "+", ".join(sorted(internal)))
    return base


def validate_longitudinal_sample_values(samples: Sequence[Mapping[str, Any]], baseline: Sequence[str]) -> None:
    """Reject non-finite/missing baseline state before nuisance fitting."""
    for row_index,row in enumerate(samples):
        if not isinstance(row,Mapping):
            raise ValueError("longitudinal samples must be objects")
        for name in baseline:
            if name not in row:
                raise ValueError(f"sample {row_index} is missing baseline feature {name}")
            _finite(row[name],f"sample {row_index} baseline {name}")


def validate_propensity_clip(value: Any) -> float:
    clip=_finite(value,"propensity_clip")
    if not 0.0<clip<0.5:
        raise ValueError("propensity_clip must lie in (0,0.5)")
    return max(0.01,min(0.25,clip))


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
        _finite(spec.get("intercept",0.0),f"{label} intercept")
        _finite(spec.get("threshold",0.0),f"{label} threshold")
        for name,value in coefficients.items():
            _finite(value,f"{label} coefficient {name}")
    projected={name:_finite(row[name],f"{label} history {name}") for name in allowed}
    return _policy_action(spec,projected,label)
