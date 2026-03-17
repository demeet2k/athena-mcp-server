from __future__ import annotations

import numpy as np
from scipy import ndimage


def rank_transform(img: np.ndarray) -> np.ndarray:
    """Convert intensity to ordinal rank values."""
    flat = img.flatten()
    ranks = np.zeros_like(flat)
    sorted_idx = np.argsort(flat)
    ranks[sorted_idx] = np.linspace(0, 1, len(flat))
    return ranks.reshape(img.shape)


def compute_gradients(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sobel gradients used throughout the kernel."""
    gy = ndimage.sobel(img, axis=0)
    gx = ndimage.sobel(img, axis=1)
    mag = np.sqrt(gx**2 + gy**2)
    angle = np.arctan2(gy, gx)
    return mag, angle
