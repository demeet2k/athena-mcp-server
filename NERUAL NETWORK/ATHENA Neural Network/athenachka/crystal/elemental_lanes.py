from __future__ import annotations

import numpy as np


def _entropy(probs: np.ndarray) -> float:
    probs = np.clip(probs, 1e-10, 1.0)
    return float(-(probs * np.log(probs)).sum() / np.log(len(probs)))


def _clip_vector(values: list[float]) -> np.ndarray:
    return np.clip(np.array(values, dtype=float), 0.0, 1.0)


def project_elemental_state(trace: dict[str, object], state, mode: str = "fast") -> dict[str, dict[str, object]]:
    """Project kernel trace into explicit Fire/Water/Air/Earth lanes."""
    probs = np.asarray(trace["legacy_probs"])
    hypotheses: list[dict[str, object]] = list(trace["hypotheses"])
    feature_summary = dict(trace["feature_summary"])

    candidate_count = len(hypotheses)
    count_norm = min(1.0, candidate_count / (12.0 if mode == "full" else 6.0))
    qualities = np.array([float(item["quality"]) for item in hypotheses], dtype=float) if hypotheses else np.zeros(1)
    disagreements = (
        np.array([float(item["disagreement"]) for item in hypotheses], dtype=float) if hypotheses else np.zeros(1)
    )
    confidences = (
        np.array([float(item["confidence"]) for item in hypotheses], dtype=float) if hypotheses else np.array([float(probs.max())])
    )

    top_probs = np.sort(probs)[-2:]
    margin = float(top_probs[-1] - top_probs[-2]) if len(top_probs) >= 2 else float(top_probs[-1])
    entropy = _entropy(probs)
    replay_depth = min(1.0, len(state.replay.get("seed_history", [])) / 8.0)
    prior_coherence = float(state.metrics.get("coherence", 0.5))

    fire_vec = _clip_vector(
        [
            1.0 - margin,
            float(qualities.mean()) if candidate_count else 0.0,
            count_norm,
            float(disagreements.mean()) if candidate_count else 0.0,
            float(confidences.max()),
            entropy,
            float(state.growth.get("novelty_bias", 0.5)),
            1.0 if candidate_count > 1 else 0.25,
        ]
    )
    water_vec = _clip_vector(
        [
            float(confidences.mean()),
            1.0 - float(disagreements.mean()) if candidate_count else 0.75,
            1.0 - min(1.0, abs(count_norm - 0.5)),
            prior_coherence,
            margin,
            float(state.process.get("continuity_bias", 0.5)),
            replay_depth,
            1.0 - entropy,
        ]
    )
    air_vec = _clip_vector(
        [
            float(feature_summary.get("mean", 0.0)),
            float(feature_summary.get("std", 0.0)),
            float(feature_summary.get("norm", 0.0)),
            1.0 - float(feature_summary.get("sparsity", 0.0)),
            float(state.corpus.get("compression_bias", 0.5)),
            entropy,
            count_norm,
            float(feature_summary.get("mask_mass_mean", 0.0)),
        ]
    )
    earth_vec = _clip_vector(
        [
            margin,
            1.0 - entropy,
            1.0 - float(disagreements.mean()) if candidate_count else 0.75,
            float(feature_summary.get("mask_mass_mean", 0.0)),
            float(state.replay.get("witness_bias", 0.5)),
            float(probs.max()),
            float(state.metrics.get("proof_density", 0.5)),
            1.0 if candidate_count > 0 else 0.0,
        ]
    )

    elemental_vectors = {
        "fire": fire_vec,
        "water": water_vec,
        "air": air_vec,
        "earth": earth_vec,
    }

    elemental_state: dict[str, dict[str, object]] = {}
    for name, vector in elemental_vectors.items():
        elemental_state[name] = {
            "vector": vector.tolist(),
            "score": float(vector.mean()),
            "budget": float(vector.max()),
            "channel": name.upper(),
        }
    return elemental_state
