from __future__ import annotations

import numpy as np
from scipy.special import softmax as scipy_softmax

from .attention_field import generate_attention
from .carrier_stack import extract_all_features
from .classifier import NeuralClassifier
from .fusion import collapse_hypotheses, compute_hypothesis_quality, fuse_experts
from .hypothesis_compiler import compile_hypotheses
from .mdl_prior import CompressionPrior
from .rank_encoder import rank_transform


class AthenaKernel:
    """Modularized Athena perceptual kernel with legacy-compatible behavior."""

    def __init__(self):
        self.feature_dim = 523
        self.classifier = NeuralClassifier(self.feature_dim, hidden1=128, hidden2=64)
        self.mdl_prior = CompressionPrior(pca_rank=8)
        self.feat_mean: np.ndarray | None = None
        self.feat_std: np.ndarray | None = None
        self.fast_thresholds = [0.4, 0.55]
        self.full_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    def _resolve_thresholds(self, max_hypotheses: int | None = None) -> list[float]:
        if max_hypotheses is None or max_hypotheses <= len(self.fast_thresholds):
            return self.fast_thresholds
        return self.full_thresholds[:max_hypotheses]

    def extract_features(self, img: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        return extract_all_features(img, mask)

    def train(
        self,
        X_train: np.ndarray,
        Y_train: np.ndarray,
        epochs: int = 20,
        lr: float = 0.03,
        batch_size: int = 32,
        verbose: bool = True,
    ) -> None:
        n = len(X_train)
        rng = np.random.RandomState(42)

        if verbose:
            print("  Training MDL prior...")
        self.mdl_prior.train(X_train, Y_train)

        if verbose:
            print("  Extracting features (cached)...")
        all_features = np.zeros((n, self.feature_dim), dtype=np.float32)
        for i in range(n):
            all_features[i] = self.extract_features(X_train[i].reshape(28, 28))

        self.feat_mean = all_features.mean(0)
        self.feat_std = all_features.std(0) + 1e-8
        all_features = (all_features - self.feat_mean) / self.feat_std

        if verbose:
            print("  Training classifier...")
        for ep in range(epochs):
            idx = rng.permutation(n)
            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n, batch_size):
                batch_idx = idx[start : start + batch_size]
                X_batch = all_features[batch_idx]
                Y_batch = Y_train[batch_idx]

                probs = self.classifier.forward(X_batch)
                loss = -np.sum(Y_batch * np.log(probs + 1e-10)) / len(Y_batch)
                epoch_loss += loss
                n_batches += 1
                self.classifier.backward(X_batch, Y_batch, lr=lr, wd=0.002)

            if verbose and (ep + 1) % 5 == 0:
                print(f"    Epoch {ep + 1}: loss={epoch_loss / max(1, n_batches):.4f}")

    def forward_trace(self, img: np.ndarray, max_hypotheses: int | None = None) -> dict[str, object]:
        R = rank_transform(img)
        attention = generate_attention(R)
        hypotheses = compile_hypotheses(
            attention,
            R,
            thresholds=self._resolve_thresholds(max_hypotheses),
            max_hypotheses=max_hypotheses,
        )

        results: list[dict[str, object]] = []
        for hypothesis in hypotheses:
            mask = np.asarray(hypothesis["mask"])
            features = self.extract_features(img, mask)
            if self.feat_mean is not None and self.feat_std is not None:
                feats_norm = (features - self.feat_mean) / self.feat_std
            else:
                feats_norm = features

            classifier_probs = self.classifier.forward(feats_norm.reshape(1, -1))[0]
            mdl_logits = self.mdl_prior.get_logits(img.flatten())
            mdl_probs = scipy_softmax(mdl_logits * 0.5)
            fused_probs = fuse_experts(classifier_probs, mdl_probs)
            quality = compute_hypothesis_quality(R, mask)

            results.append(
                {
                    "tau": float(hypothesis["threshold"]),
                    "mask": mask,
                    "features": feats_norm,
                    "classifier_probs": classifier_probs,
                    "mdl_probs": mdl_probs,
                    "fused_probs": fused_probs,
                    "quality": quality,
                    "confidence": float(fused_probs.max()),
                    "disagreement": float(np.abs(classifier_probs - mdl_probs).mean()),
                    "edge_agreement": quality,
                    "predicted_class": int(fused_probs.argmax()),
                    "mask_mass": float(mask.sum() / mask.size),
                }
            )

        if not results:
            fallback_features = self.extract_features(img)
            if self.feat_mean is not None and self.feat_std is not None:
                feats_norm = (fallback_features - self.feat_mean) / self.feat_std
            else:
                feats_norm = fallback_features
            fallback_probs = self.classifier.forward(feats_norm.reshape(1, -1))[0]
            feature_stack = np.array([feats_norm], dtype=float)
            return {
                "R": R,
                "attention": attention,
                "hypotheses": [],
                "legacy_prediction": int(fallback_probs.argmax()),
                "legacy_probs": fallback_probs,
                "legacy_confidence": 0.5,
                "feature_summary": {
                    "mean": float(feature_stack.mean()),
                    "std": float(feature_stack.std()),
                    "norm": float(np.linalg.norm(feature_stack) / np.sqrt(feature_stack.size)),
                    "sparsity": float(np.mean(np.abs(feature_stack) < 1e-3)),
                    "mask_mass_mean": 0.0,
                },
            }

        legacy_prediction, legacy_probs, legacy_confidence = collapse_hypotheses(results)
        feature_stack = np.stack([np.asarray(item["features"]) for item in results], axis=0)
        return {
            "R": R,
            "attention": attention,
            "hypotheses": results,
            "legacy_prediction": legacy_prediction,
            "legacy_probs": legacy_probs,
            "legacy_confidence": legacy_confidence,
            "feature_summary": {
                "mean": float(feature_stack.mean()),
                "std": float(feature_stack.std()),
                "norm": float(np.linalg.norm(feature_stack) / np.sqrt(feature_stack.size)),
                "sparsity": float(np.mean(np.abs(feature_stack) < 1e-3)),
                "mask_mass_mean": float(np.mean([float(item["mask_mass"]) for item in results])),
            },
        }

    def forward(self, img: np.ndarray) -> tuple[int, np.ndarray, float]:
        trace = self.forward_trace(img, max_hypotheses=len(self.fast_thresholds))
        return (
            int(trace["legacy_prediction"]),
            np.asarray(trace["legacy_probs"]),
            float(trace["legacy_confidence"]),
        )

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = []
        for i in range(len(X)):
            pred, _, _ = self.forward(X[i].reshape(28, 28))
            predictions.append(pred)
        return np.array(predictions)

    def evaluate(self, X_test: np.ndarray, Y_test: np.ndarray, verbose: bool = True) -> float:
        correct = 0
        total = len(X_test)
        for i in range(total):
            pred, _, _ = self.forward(X_test[i].reshape(28, 28))
            if pred == int(Y_test[i].argmax()):
                correct += 1
        accuracy = correct / max(1, total)
        if verbose:
            print(f"  Accuracy: {accuracy * 100:.1f}%")
        return accuracy

    def get_param_count(self) -> int:
        classifier_params = (
            self.classifier.W1.size
            + self.classifier.b1.size
            + self.classifier.W2.size
            + self.classifier.b2.size
            + self.classifier.W3.size
            + self.classifier.b3.size
        )
        mdl_params = 10 * 784 + 10 * 784 * 8
        return int(classifier_params + mdl_params)
