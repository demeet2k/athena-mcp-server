from __future__ import annotations

import numpy as np


PAIRWISE_REGISTRY = {
    "fw": {"elements": ("fire", "water"), "title": "living_transmission"},
    "fa": {"elements": ("fire", "air"), "title": "directed_orchestration"},
    "fe": {"elements": ("fire", "earth"), "title": "executable_theorem"},
    "wa": {"elements": ("water", "air"), "title": "narrated_routing"},
    "we": {"elements": ("water", "earth"), "title": "archive_distillation"},
    "ae": {"elements": ("air", "earth"), "title": "verified_topology"},
}

TRIAD_REGISTRY = {
    "fwa": {"elements": ("fire", "water", "air"), "title": "animate_swarm"},
    "fwe": {"elements": ("fire", "water", "earth"), "title": "embodied_archive"},
    "fae": {"elements": ("fire", "air", "earth"), "title": "protocol_chassis"},
    "wae": {"elements": ("water", "air", "earth"), "title": "cartographic_memory_mesh"},
}

FULL_REGISTRY = {
    "fwae": {"elements": ("fire", "water", "air", "earth"), "title": "whole_organism"}
}

SYMMETRY_REGISTRY = {
    "pairwise": PAIRWISE_REGISTRY,
    "triads": TRIAD_REGISTRY,
    "full": FULL_REGISTRY,
}


def _fuse_vectors(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    midpoint = (left + right) / 2.0
    synergy = 1.0 - np.abs(left - right)
    return np.clip((midpoint + synergy) / 2.0, 0.0, 1.0)


def _score_pair(left_score: float, right_score: float) -> float:
    return float((left_score * right_score) ** 0.5)


def compute_symmetry_state(elemental_state: dict[str, dict[str, object]], top_k: int) -> dict[str, object]:
    """Compute sparse active pairwise fusions and the omega aggregator."""
    scored_pairs: list[tuple[str, float, np.ndarray]] = []
    for pair_id, meta in PAIRWISE_REGISTRY.items():
        left_name, right_name = meta["elements"]
        left = elemental_state[left_name]
        right = elemental_state[right_name]
        fused = _fuse_vectors(np.array(left["vector"]), np.array(right["vector"]))
        score = _score_pair(float(left["score"]), float(right["score"]))
        scored_pairs.append((pair_id, score, fused))

    scored_pairs.sort(key=lambda item: item[1], reverse=True)
    active_pairs = scored_pairs[:top_k]

    active_fusions: dict[str, dict[str, object]] = {}
    omega_pool = [np.array(value["vector"], dtype=float) for value in elemental_state.values()]
    for pair_id, score, fused in active_pairs:
        active_fusions[pair_id] = {
            "score": float(score),
            "vector": fused.tolist(),
            "title": PAIRWISE_REGISTRY[pair_id]["title"],
            "elements": list(PAIRWISE_REGISTRY[pair_id]["elements"]),
        }
        omega_pool.append(fused)

    omega_vector = np.mean(np.stack(omega_pool, axis=0), axis=0)
    omega_state = {
        "score": float(omega_vector.mean()),
        "vector": np.clip(omega_vector, 0.0, 1.0).tolist(),
        "title": FULL_REGISTRY["fwae"]["title"],
    }

    return {
        "active_fusions": active_fusions,
        "triad_registry": TRIAD_REGISTRY,
        "full_registry": FULL_REGISTRY,
        "omega": omega_state,
    }
