from __future__ import annotations

import numpy as np


class CompressionPrior:
    """Minimum Description Length prior."""

    def __init__(self, pca_rank: int = 8):
        self.pca_rank = pca_rank
        self.templates: dict[int, np.ndarray] = {}
        self.bases: dict[int, np.ndarray] = {}
        self.trained = False

    def train(self, X_flat: np.ndarray, Y: np.ndarray) -> None:
        for d in range(10):
            mask = Y.argmax(1) == d
            if mask.sum() < self.pca_rank + 2:
                continue

            X_d = X_flat[mask]
            self.templates[d] = X_d.mean(0)

            centered = X_d - self.templates[d]
            try:
                _, _, vt = np.linalg.svd(centered, full_matrices=False)
                self.bases[d] = vt[: self.pca_rank].T
            except np.linalg.LinAlgError:
                self.bases[d] = np.eye(784, self.pca_rank)

        self.trained = True

    def get_logits(self, x_flat: np.ndarray) -> np.ndarray:
        if not self.trained:
            return np.zeros(10)

        logits = np.zeros(10)
        for d in range(10):
            if d not in self.templates:
                logits[d] = -100
                continue

            centered = x_flat - self.templates[d]
            coeffs = self.bases[d].T @ centered
            reconstruction = self.templates[d] + self.bases[d] @ coeffs
            residual = np.abs(x_flat - reconstruction)

            coeff_cost = np.sum(np.abs(coeffs)) * 0.1
            exception_cost = np.sum(residual > 0.15) * 0.3
            residual_cost = residual.sum() * 0.15

            logits[d] = -(coeff_cost + exception_cost + residual_cost)

        return logits
