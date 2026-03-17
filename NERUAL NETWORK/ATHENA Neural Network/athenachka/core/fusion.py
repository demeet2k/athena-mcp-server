from __future__ import annotations

import numpy as np
from scipy.special import softmax as scipy_softmax


def fuse_experts(classifier_probs: np.ndarray, mdl_probs: np.ndarray) -> np.ndarray:
    """Product-of-experts style fusion."""
    fused = classifier_probs * mdl_probs
    return fused / (fused.sum() + 1e-10)


def compute_hypothesis_quality(R: np.ndarray, mask: np.ndarray) -> float:
    """Edge-weighted hypothesis quality score."""
    from .rank_encoder import compute_gradients

    mag, _ = compute_gradients(R)
    return float((mag * mask).sum() / (mask.sum() + 1e-8))


def collapse_hypotheses(results: list[dict[str, np.ndarray | float]]) -> tuple[int, np.ndarray, float]:
    """Amplitude collapse across hypothesis results."""
    qualities = np.array([float(r["quality"]) for r in results])
    amplitudes = scipy_softmax(qualities * 5.0)

    final_probs = np.zeros(10)
    for amp, result in zip(amplitudes, results):
        final_probs += amp * np.asarray(result["fused_probs"])

    final_probs = final_probs / (final_probs.sum() + 1e-10)
    confidence = float(amplitudes.max() * final_probs.max())
    return int(final_probs.argmax()), final_probs, confidence
