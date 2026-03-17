from __future__ import annotations

from ..contracts import stable_hash


def prepare_lift_seed(
    state,
    metric_tensor: dict[str, float],
    witness_bundle: dict[str, object],
    improvement_ledger: dict[str, object],
    symmetry_state: dict[str, object],
) -> dict[str, object]:
    seed = {
        "compression_ratio": 0.125,
        "function_gain": float(metric_tensor["self_growth_gain"] + metric_tensor["novelty_gain"]),
        "coverage": float(metric_tensor["coverage"]),
        "bloat": float(1.0 - metric_tensor["pruning_efficiency"]),
        "omega_score": float(symmetry_state["omega"]["score"]),
        "active_fusions": list(symmetry_state.get("active_fusions", {}).keys()),
        "required_sections": list(improvement_ledger.get("required_sections", [])),
        "witness_strength": float(witness_bundle.get("strength", 0.0)),
    }
    seed["seed_id"] = stable_hash(seed)
    state.replay.setdefault("seed_history", []).append(seed)
    state.replay["latest_seed"] = seed
    return seed
