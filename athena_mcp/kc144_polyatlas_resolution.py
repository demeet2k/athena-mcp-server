from __future__ import annotations

"""Exact transport over the odd N=3m, m odd resolution family."""

from fractions import Fraction
import math
from typing import Any

from .kc144_polyatlas_identity import POLYATLAS_VERSION, bounded_int, digest


def fraction_payload(value: Fraction) -> dict[str, Any]:
    return {"numerator": value.numerator, "denominator": value.denominator,
            "fraction": f"{value.numerator}/{value.denominator}", "decimal": float(value)}

def validate_resolution(name: str, value: Any) -> int:
    value = bounded_int(name, value, 3, 2_147_483_647)
    if value % 3 or value % 2 == 0 or (value // 3) % 2 == 0:
        raise ValueError(f"{name} must equal 3*m for positive odd m")
    return value


def resolution_descriptor(resolution: int) -> dict[str, Any]:
    resolution = validate_resolution("resolution", resolution)
    m = resolution // 3
    prime = m > 1 and all(m % divisor for divisor in range(2, math.isqrt(m) + 1))
    residual = resolution
    while residual % 3 == 0:
        residual //= 3
    pure = residual == 1
    return {"resolution": resolution, "factorization": [3, m], "center": (resolution + 1) // 2,
            "mirror_law": f"i->{resolution + 1}-i", "family_index": (m - 1) // 2,
            "previous": resolution - 6 if resolution > 3 else None, "next": resolution + 6,
            "species": "PURE_TERNARY_POWER" if pure else ("PRIME_FIBRE" if prime else "ODD_COMPOSITE_FIBRE")}


def resolution_family(*, start_multiplier: int = 1, count: int = 10) -> dict[str, Any]:
    start_multiplier = bounded_int("start_multiplier", start_multiplier, 1, 715_827_881)
    count = bounded_int("count", count, 1, 200)
    if start_multiplier % 2 == 0 or 3 * (start_multiplier + 2 * (count - 1)) > 2_147_483_647:
        raise ValueError("requested odd-resolution family segment is outside bounds")
    items = [resolution_descriptor(3 * (start_multiplier + 2 * offset)) for offset in range(count)]
    return {"version": POLYATLAS_VERSION, "items": items, "resolution_step": 6,
            "center_step": 3, "law": "N=3m,m odd", "digest": digest(items)}


def resolution_transport(source_resolution: int, target_resolution: int, station: int) -> dict[str, Any]:
    source_resolution = validate_resolution("source_resolution", source_resolution)
    target_resolution = validate_resolution("target_resolution", target_resolution)
    station = bounded_int("station", station, 1, source_resolution)
    u = Fraction(station - 1, source_resolution - 1)
    xi = 2 * u - 1
    target_zero = u * (target_resolution - 1)
    lower_zero = target_zero.numerator // target_zero.denominator
    offset = target_zero - lower_zero
    lower = lower_zero + 1
    support = ([{"station": lower, "weight": fraction_payload(Fraction(1))}]
               if offset == 0 else [{"station": lower, "weight": fraction_payload(1 - offset)},
                                    {"station": lower + 1, "weight": fraction_payload(offset)}])
    mirror_source = source_resolution + 1 - station
    mirror_target = Fraction(mirror_source - 1, source_resolution - 1) * (target_resolution - 1)
    payload = {
        "version": POLYATLAS_VERSION, "source": resolution_descriptor(source_resolution),
        "target": resolution_descriptor(target_resolution), "station": station,
        "normalized_u": fraction_payload(u), "centered_xi": fraction_payload(xi),
        "exact_target_zero_based": fraction_payload(target_zero),
        "exact_target_one_based": fraction_payload(target_zero + 1), "support": support,
        "exact_station": lower if offset == 0 else None, "lower_station": lower,
        "upper_station": lower if offset == 0 else lower + 1, "fractional_offset": fraction_payload(offset),
        "invariants": {"endpoints_preserved": station not in (1, source_resolution) or (offset == 0 and lower in (1, target_resolution)),
                       "source_center_preserved": station != (source_resolution + 1) // 2 or (offset == 0 and lower == (target_resolution + 1) // 2),
                       "mirror_commutes": mirror_target == (target_resolution - 1) - target_zero,
                       "weights_sum_to_one": sum(Fraction(item["weight"]["numerator"], item["weight"]["denominator"]) for item in support) == 1},
        "rounding_policy": "NONE", "semantic_boundary": "normalized position is not semantic identity",
    }
    payload["digest"] = digest(payload)
    return payload
