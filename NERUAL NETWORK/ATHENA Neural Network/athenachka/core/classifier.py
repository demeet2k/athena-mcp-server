from __future__ import annotations

import numpy as np


class NeuralClassifier:
    """Efficient three-layer MLP."""

    def __init__(self, input_dim: int, hidden1: int = 128, hidden2: int = 64, seed: int = 42):
        rng = np.random.RandomState(seed)

        self.W1 = rng.randn(input_dim, hidden1) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden1)
        self.W2 = rng.randn(hidden1, hidden2) * np.sqrt(2.0 / hidden1)
        self.b2 = np.zeros(hidden2)
        self.W3 = rng.randn(hidden2, 10) * np.sqrt(2.0 / hidden2)
        self.b3 = np.zeros(10)

    def forward(self, X: np.ndarray) -> np.ndarray:
        self.h1 = np.maximum(0, X @ self.W1 + self.b1)
        self.h2 = np.maximum(0, self.h1 @ self.W2 + self.b2)
        logits = self.h2 @ self.W3 + self.b3

        logits_stable = logits - logits.max(axis=-1, keepdims=True)
        exp_logits = np.exp(logits_stable)
        self.probs = exp_logits / exp_logits.sum(axis=-1, keepdims=True)
        return self.probs

    def backward(self, X: np.ndarray, Y: np.ndarray, lr: float = 0.01, wd: float = 0.001) -> None:
        batch_size = len(X)

        dlogits = (self.probs - Y) / batch_size

        dW3 = self.h2.T @ dlogits + wd * self.W3
        db3 = dlogits.sum(0)
        dh2 = dlogits @ self.W3.T
        dh2[self.h2 <= 0] = 0

        dW2 = self.h1.T @ dh2 + wd * self.W2
        db2 = dh2.sum(0)
        dh1 = dh2 @ self.W2.T
        dh1[self.h1 <= 0] = 0

        dW1 = X.T @ dh1 + wd * self.W1
        db1 = dh1.sum(0)

        self.W3 -= lr * dW3
        self.b3 -= lr * db3
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
