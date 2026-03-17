from __future__ import annotations

import numpy as np
from scipy import ndimage


def generate_mask(attention: np.ndarray, R: np.ndarray, tau: float) -> np.ndarray:
    """Generate a single binary hypothesis mask."""
    mask = ((attention >= tau) | (R >= tau + 0.1)).astype(np.float32)

    if mask.sum() < 10:
        return np.zeros_like(mask)

    mask = ndimage.binary_opening(mask, structure=np.ones((2, 2))).astype(np.float32)

    labeled, num = ndimage.label(mask)
    if num > 0:
        sizes = ndimage.sum(mask, labeled, range(1, num + 1))
        largest = np.argmax(sizes) + 1
        mask = (labeled == largest).astype(np.float32)

    mask = ndimage.binary_fill_holes(mask).astype(np.float32)
    return mask


def compile_hypotheses(
    attention: np.ndarray,
    R: np.ndarray,
    thresholds: list[float],
    max_hypotheses: int | None = None,
) -> list[dict[str, np.ndarray | float]]:
    """Compile threshold proposals into bounded binary hypotheses."""
    hypotheses: list[dict[str, np.ndarray | float]] = []
    for tau in thresholds:
        mask = generate_mask(attention, R, tau)
        if mask.sum() < 15:
            continue
        hypotheses.append({"threshold": float(tau), "mask": mask})
        if max_hypotheses is not None and len(hypotheses) >= max_hypotheses:
            break
    return hypotheses
