from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from .collective_calibrated import _binary, _fold_assignment


def _isotonic_blocks_aggregated(examples: Sequence[Mapping[str, Any]]) -> list[dict[str, float]]:
    """Weighted PAV after aggregating identical support coordinates.

    Equal-x observations must share one fitted isotonic value. Aggregating before
    PAV prevents label sort order from manufacturing multiple predictions at the
    same support coordinate.
    """
    grouped: dict[float, dict[str, float]] = {}
    for row in examples:
        support = float(row["support"])
        if not math.isfinite(support) or not 0.0 <= support <= 1.0:
            raise ValueError("structural support must be finite and lie in [0,1]")
        correct = float(_binary(row["correct"], "correct"))
        weight = float(row.get("weight", 1.0))
        if not math.isfinite(weight) or weight <= 0.0:
            raise ValueError("calibration weights must be finite and positive")
        bucket = grouped.setdefault(support, {"weight": 0.0, "success": 0.0})
        bucket["weight"] += weight
        bucket["success"] += weight * correct
    if len(examples) < 8:
        raise ValueError("structural calibration requires at least eight examples")

    blocks: list[dict[str, float]] = []
    for support in sorted(grouped):
        aggregate = grouped[support]
        blocks.append({
            "x_min": support,
            "x_max": support,
            "weight": aggregate["weight"],
            "success": aggregate["success"],
        })
        while len(blocks) >= 2:
            left, right = blocks[-2], blocks[-1]
            p_left = left["success"] / left["weight"]
            p_right = right["success"] / right["weight"]
            if p_left <= p_right + 1e-15:
                break
            blocks[-2:] = [{
                "x_min": left["x_min"],
                "x_max": right["x_max"],
                "weight": left["weight"] + right["weight"],
                "success": left["success"] + right["success"],
            }]

    return [{
        "x_min": float(block["x_min"]),
        "x_max": float(block["x_max"]),
        "probability": float(block["success"] / block["weight"]),
        "weight": float(block["weight"]),
    } for block in blocks]


def _isotonic_step_predict(blocks: Sequence[Mapping[str, Any]], support: float) -> float:
    """Right-continuous monotone step prediction with endpoint extension.

    At an observed knot x_i the fitted value at x_i is used. Between successive
    knots/blocks [x_i, x_{i+1}) the value from the most recent block is carried
    forward. Values below/above the observed support use the first/last block.
    """
    x = float(support)
    if not math.isfinite(x) or not 0.0 <= x <= 1.0:
        raise ValueError("supports to calibrate must be finite and lie in [0,1]")
    if not blocks:
        raise ValueError("calibration curve is empty")
    selected = blocks[0]
    if x < float(selected["x_min"]) - 1e-15:
        return max(0.0, min(1.0, float(selected["probability"])))
    for block in blocks:
        if x < float(block["x_min"]) - 1e-15:
            break
        selected = block
    return max(0.0, min(1.0, float(selected["probability"])))


def structural_reliability_calibrate(
    calibration_examples: Sequence[Mapping[str, Any]],
    supports: Sequence[float] | None = None,
    folds: int = 5,
    seed: int = 0,
) -> dict[str, Any]:
    rows = [dict(row) for row in calibration_examples]
    if len(rows) < 40:
        raise ValueError("structural reliability calibration requires at least forty labelled examples")

    # Validate every row once before fold construction and retain the declared
    # weight for both fitting and scoring diagnostics.
    validated: list[dict[str, float]] = []
    for row in rows:
        support = float(row["support"])
        if not math.isfinite(support) or not 0.0 <= support <= 1.0:
            raise ValueError("structural support must be finite and lie in [0,1]")
        correct = float(_binary(row["correct"], "correct"))
        weight = float(row.get("weight", 1.0))
        if not math.isfinite(weight) or weight <= 0.0:
            raise ValueError("calibration weights must be finite and positive")
        validated.append({"support": support, "correct": correct, "weight": weight})

    assignment = _fold_assignment(len(validated), max(2, min(int(folds), 10)), seed)
    k = max(assignment) + 1
    oof: list[float | None] = [None] * len(validated)
    for fold in range(k):
        train = [validated[i] for i in range(len(validated)) if assignment[i] != fold]
        curve = _isotonic_blocks_aggregated(train)
        for i, row in enumerate(validated):
            if assignment[i] == fold:
                oof[i] = _isotonic_step_predict(curve, row["support"])
    if any(value is None for value in oof):
        raise RuntimeError("out-of-fold structural reliability assignment is incomplete")

    total_weight = sum(row["weight"] for row in validated)
    brier_raw = sum(row["weight"] * (row["support"] - row["correct"]) ** 2 for row in validated) / total_weight
    brier_oof = sum(row["weight"] * (float(oof[i]) - row["correct"]) ** 2 for i, row in enumerate(validated)) / total_weight
    final_curve = _isotonic_blocks_aggregated(validated)

    targets = []
    for value in supports or []:
        x = float(value)
        targets.append({
            "support": x,
            "calibrated_reliability": round(_isotonic_step_predict(final_curve, x), 10),
        })

    return {
        "status": "OUT_OF_FOLD_WEIGHTED_ISOTONIC_STRUCTURAL_RELIABILITY",
        "n": len(validated),
        "unique_support_coordinates": len({row["support"] for row in validated}),
        "folds": k,
        "weighted": any(abs(row["weight"] - 1.0) > 1e-15 for row in validated),
        "interpolation": "RIGHT_CONTINUOUS_MONOTONE_STEP_WITH_ENDPOINT_EXTENSION",
        "brier_raw": round(brier_raw, 10),
        "brier_oof_calibrated": round(brier_oof, 10),
        "oof_improvement": round(brier_raw - brier_oof, 10),
        "curve": [{
            "support_min": round(float(block["x_min"]), 10),
            "support_max": round(float(block["x_max"]), 10),
            "calibrated_reliability": round(float(block["probability"]), 10),
            "weight": round(float(block["weight"]), 10),
        } for block in final_curve],
        "calibrated_supports": targets,
        "law": "identical support coordinates are pooled before weighted PAV, out-of-fold diagnostics use the same declared weights, and the final mapping is an explicit right-continuous monotone step function carrying each fitted block forward until the next support knot; empirical reliability calibration remains distinct from a causal graph posterior or JSPACE authority",
    }
