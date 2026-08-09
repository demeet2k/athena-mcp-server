from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Optional

from .party_coordination_v3_1 import PartyCoordinationRuntimeV31

PARTY_REWARD_NUMERIC_VERSION = "PARTY.REWARD.PROVENANCE.3.2"


def _finite_nonnegative_xp(value: Any) -> float:
    """Preserve V3 float-coercion compatibility while rejecting unsafe numerics."""
    if isinstance(value, bool):
        raise ValueError("base_xp must be numeric, finite, non-boolean, and non-negative")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError("base_xp must be numeric, finite, non-boolean, and non-negative") from None
    if not math.isfinite(numeric):
        raise ValueError("base_xp must be finite")
    if numeric < 0:
        raise ValueError("base_xp must be non-negative")
    return numeric


class PartyCoordinationRuntimeV32(PartyCoordinationRuntimeV31):
    """Finite-number hardening over the V3.1 provenance membrane.

    This layer changes no reward formula and grants no new authority. It ensures
    the imported base-XP amount is a finite non-boolean real before any inherited
    Message Board read/mutation, source-XP scan, or receipt construction occurs.
    """

    def observe(
        self,
        observation_id: str,
        party_id: str,
        observer: str,
        base_xp: float,
        results: Iterable[Dict[str, Any]],
        witness_ref: str,
        source_xp_ref: Optional[str] = None,
        source_xp_witness_ref: Optional[str] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        finite_base_xp = _finite_nonnegative_xp(base_xp)
        return super().observe(
            observation_id,
            party_id,
            observer,
            finite_base_xp,
            results,
            witness_ref,
            source_xp_ref,
            source_xp_witness_ref,
            remote,
        )

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        reward = dict(value.get("reward_provenance") or {})
        reward.update(
            {
                "numeric_hardening_version": PARTY_REWARD_NUMERIC_VERSION,
                "base_xp_requires_finite": True,
                "base_xp_boolean_allowed": False,
                "finite_numeric_string_compatibility": True,
                "finite_validation_is_upstream_xp_verification": False,
            }
        )
        value["reward_provenance"] = reward
        value["laws"] = list(value.get("laws") or []) + [
            "base_xp must be finite and non-boolean before Party reward processing begins",
            "finite numeric validation preserves imported-amount shape only; it does not verify the upstream XP source or grant mint authority",
        ]
        return value

    def benchmark(self) -> Dict[str, Any]:
        value = dict(super().benchmark())
        value["party_reward_numeric_hardening_version"] = PARTY_REWARD_NUMERIC_VERSION
        return value


__all__ = [
    "PARTY_REWARD_NUMERIC_VERSION",
    "PartyCoordinationRuntimeV32",
    "_finite_nonnegative_xp",
]
