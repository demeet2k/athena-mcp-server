from __future__ import annotations

import numpy as np


def detect_contradictions(
    candidate_set: list[dict[str, object]],
    trace: dict[str, object],
    symmetry_state: dict[str, object],
    corridor_profile: dict[str, object],
) -> dict[str, object]:
    probs = np.asarray(trace["legacy_probs"], dtype=float)
    top_two = np.sort(probs)[-2:]
    margin = float(top_two[-1] - top_two[-2]) if len(top_two) >= 2 else float(top_two[-1])
    flags: list[str] = []

    predicted_classes = {int(item["predicted_class"]) for item in candidate_set}
    if len(predicted_classes) > 1:
        flags.append("multi_hypothesis_class_conflict")

    if margin <= float(corridor_profile["ambiguity_margin"]):
        flags.append("narrow_margin_ambiguity")

    if not symmetry_state.get("active_fusions"):
        flags.append("no_active_fusions")

    disagreements = [float(item["disagreement"]) for item in candidate_set]
    if disagreements and float(np.mean(disagreements)) > 0.2:
        flags.append("observer_disagreement_pressure")

    pressure = min(
        1.0,
        0.15 * len(flags)
        + 0.35 * (1.0 - margin)
        + (0.2 * float(np.mean(disagreements)) if disagreements else 0.0),
    )
    return {
        "flags": flags,
        "pressure": float(pressure),
        "quarantined": bool(flags),
    }
