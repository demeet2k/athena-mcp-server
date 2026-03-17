from __future__ import annotations

import numpy as np

from ..contracts import AthenachkaState


def build_initial_state(
    mode: str = "fast",
    seed_history: list[dict[str, object]] | None = None,
    docs_gate_status: str = "BLOCKED",
) -> AthenachkaState:
    state = AthenachkaState(
        corpus={
            "mode": mode,
            "compression_bias": 0.5 if mode == "fast" else 0.75,
            "coverage_anchor": 0.5,
            "docs_gate_status": docs_gate_status,
        },
        process={
            "phase_history": [],
            "continuity_bias": 0.6,
            "full_path_enabled": mode == "full",
        },
        growth={
            "novelty_bias": 0.55 if mode == "fast" else 0.8,
            "repair_bias": 0.65,
            "journey_gain": 0.0,
        },
        metrics={
            "coverage": 0.5,
            "coherence": 0.5,
            "proof_density": 0.5,
            "replayability": 0.5,
            "frontier_clarity": 0.5,
        },
        bridges={
            "candidate_receipts": [],
            "promoted_receipts": [],
        },
        replay={
            "seed_history": list(seed_history or []),
            "witness_bias": 0.6,
            "phase_replay": [],
        },
        phase_index="2/16",
    )
    return state


def build_metric_tensor(
    trace: dict[str, object],
    elemental_state: dict[str, dict[str, object]],
    symmetry_state: dict[str, object],
    born_coordinates: list[dict[str, object]],
    contradictions: dict[str, object],
    witness_bundle: dict[str, object],
    mode: str,
) -> dict[str, float]:
    probs = np.asarray(trace["legacy_probs"], dtype=float)
    candidate_set: list[dict[str, object]] = list(trace["hypotheses"])
    top_two = np.sort(probs)[-2:]
    margin = float(top_two[-1] - top_two[-2]) if len(top_two) >= 2 else float(top_two[-1])
    entropy = float(-(np.clip(probs, 1e-10, 1.0) * np.log(np.clip(probs, 1e-10, 1.0))).sum() / np.log(len(probs)))
    active_fusions = dict(symmetry_state.get("active_fusions", {}))
    contradiction_pressure = float(contradictions.get("pressure", 0.0))
    witness_strength = float(witness_bundle.get("strength", 0.0))
    replay_strength = float(witness_bundle.get("replay_score", 0.0))

    coverage = min(1.0, 0.45 + 0.08 * len(candidate_set) + 0.05 * len(active_fusions))
    coherence = float(np.clip(1.0 - entropy * 0.55 - contradiction_pressure * 0.35, 0.0, 1.0))
    born_rate = float(min(1.0, len(born_coordinates) / (3.0 if mode == "full" else 1.0)))
    operator_closure = float(np.clip(0.35 + 0.4 * margin + 0.25 * len(active_fusions) / 6.0, 0.0, 1.0))
    proof_density = float(np.clip(0.4 + 0.6 * witness_strength, 0.0, 1.0))
    replayability = float(np.clip(0.35 + 0.65 * replay_strength, 0.0, 1.0))
    retrieval_quality = float(np.clip(0.45 + 0.3 * coverage + 0.2 * witness_strength, 0.0, 1.0))
    registry_completeness = float(np.clip(0.3 + 0.4 * len(active_fusions) / 6.0 + 0.2 * witness_strength, 0.0, 1.0))
    novelty_gain = float(np.clip(0.3 + 0.45 * born_rate + 0.25 * elemental_state["fire"]["score"], 0.0, 1.0))
    pruning_efficiency = float(np.clip(0.2 + 0.5 * margin + 0.2 * elemental_state["earth"]["score"], 0.0, 1.0))
    compression_ratio = float(np.clip(0.125 if mode == "full" else 0.5, 0.0, 1.0))
    cross_domain_transfer = float(np.clip(0.2 + 0.5 * elemental_state["air"]["score"] + 0.2 * len(active_fusions) / 6.0, 0.0, 1.0))
    meta_process_quality = float(np.clip(0.25 + 0.45 * elemental_state["water"]["score"] + 0.2 * replay_strength, 0.0, 1.0))
    self_growth_gain = float(np.clip(0.2 + 0.4 * novelty_gain + 0.3 * meta_process_quality, 0.0, 1.0))
    frontier_clarity = float(np.clip(0.2 + 0.5 * (1.0 - entropy) + 0.2 * contradiction_pressure, 0.0, 1.0))

    return {
        "coverage": coverage,
        "coherence": coherence,
        "contradiction_pressure": contradiction_pressure,
        "born_coordinate_discovery_rate": born_rate,
        "operator_closure": operator_closure,
        "proof_density": proof_density,
        "replayability": replayability,
        "retrieval_quality": retrieval_quality,
        "registry_completeness": registry_completeness,
        "novelty_gain": novelty_gain,
        "pruning_efficiency": pruning_efficiency,
        "compression_ratio": compression_ratio,
        "cross_domain_transfer": cross_domain_transfer,
        "meta_process_quality": meta_process_quality,
        "self_growth_gain": self_growth_gain,
        "frontier_clarity": frontier_clarity,
    }
