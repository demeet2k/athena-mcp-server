"""
Adaptive QP-GEMM Optimization Framework (Vision-Tuned)

This module implements the adaptive low-rank replacement pipeline described by the user:
- Sigma pole: probing (SVD analysis)
- Omega pole: tuning (rank selection by spectral energy threshold)
- Psi pole: representation (factored parameters U,V)
- Delta pole: decision (only apply if predicted compute reduction is large enough)

Key design goal:
- Provide a drop-in replacement for nn.Linear layers where a low-rank factorization
  is likely to reduce inference cost and memory while keeping reconstruction error bounded.

Important notes:
- PyTorch's torch.linalg.svd returns (U, S, Vh) where Vh is the conjugate transpose of V.
- The factorization used in QPLinear is: W ≈ U_r diag(S_r) Vh_r
  and the forward computes: x @ W^T ≈ (x @ (sqrt(S_r) Vh_r)^T) @ (U_r sqrt(S_r))^T
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Iterable

import torch
import torch.nn as nn

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class QPGEMMConfig:
    """
    Configuration for the Adaptive QP-GEMM engine.

    Attributes:
        energy_threshold: Cumulative spectral energy threshold in [0,1].
            By default uses the sum of singular values (SV energy). If you want the
            Frobenius-style energy, set energy_mode="sv2".
        energy_mode: "sv" or "sv2"
            - "sv": cumulative sum of singular values / sum of singular values
            - "sv2": cumulative sum of S^2 / sum of S^2  (Frobenius energy)
        min_rank: Lower bound on rank allowed (useful to avoid tiny ranks that harm accuracy).
        max_rank: Upper bound on rank allowed (None means no cap).
        min_gain: Minimum theoretical compute reduction required before applying low-rank.
            Example: 0.30 means require >30% reduction in multiply-add proxy.
        allow_bias: Whether to carry bias into QPLinear when present.
        svd_driver: Optional SVD driver hint for torch.linalg.svd (may be ignored depending on backend).
    """
    energy_threshold: float = 0.99
    energy_mode: str = "sv"  # "sv" or "sv2"
    min_rank: int = 1
    max_rank: Optional[int] = None
    min_gain: float = 0.30
    allow_bias: bool = True
    svd_driver: Optional[str] = None


# -----------------------------------------------------------------------------
# Engine (Sigma + Omega + Delta)
# -----------------------------------------------------------------------------

class QPGEMMEngine:
    """
    Analyzes a weight matrix W (out_features x in_features) to decide whether
    to use a low-rank approximation and what rank to use.

    Decision rule (Delta):
        apply lowrank if proxy_lowrank_cost <= (1 - min_gain) * proxy_dense_cost

    Costs (simple multiply-add proxy):
        dense_cost    = out * in
        lowrank_cost  = r*(out + in)
    """

    def __init__(self, config: QPGEMMConfig = QPGEMMConfig()):
        if not (0.0 < config.energy_threshold <= 1.0):
            raise ValueError("energy_threshold must be in (0,1].")
        if config.energy_mode not in ("sv", "sv2"):
            raise ValueError('energy_mode must be "sv" or "sv2".')
        if config.min_rank < 1:
            raise ValueError("min_rank must be >= 1.")
        if config.max_rank is not None and config.max_rank < config.min_rank:
            raise ValueError("max_rank must be >= min_rank when set.")
        if not (0.0 <= config.min_gain < 1.0):
            raise ValueError("min_gain must be in [0,1).")

        self.config = config

    @staticmethod
    def _proxy_dense_cost(out_features: int, in_features: int) -> int:
        return out_features * in_features

    @staticmethod
    def _proxy_lowrank_cost(out_features: int, in_features: int, rank: int) -> int:
        return rank * (out_features + in_features)

    def _energy_curve(self, S: torch.Tensor) -> torch.Tensor:
        # S is 1D tensor of singular values length k = min(m,n)
        if self.config.energy_mode == "sv":
            numer = torch.cumsum(S, dim=0)
            denom = torch.sum(S)
        else:
            numer = torch.cumsum(S * S, dim=0)
            denom = torch.sum(S * S)
        return numer / (denom + 1e-12)

    def analyze(self, W: torch.Tensor) -> Dict[str, Any]:
        """
        Analyze the weight matrix W and return a dict:
            {"strategy": "dense"|"lowrank", "rank": int, "stats": {...}}

        stats includes:
            out_features, in_features, dense_cost, lowrank_cost, energy_threshold,
            chosen_rank, predicted_gain
        """
        if W.ndim != 2:
            raise ValueError(f"Expected 2D weight matrix, got shape {tuple(W.shape)}")
        out_features, in_features = int(W.shape[0]), int(W.shape[1])

        # Perform SVD (Sigma probing)
        # torch.linalg.svd returns U, S, Vh
        svd_kwargs = {}
        if self.config.svd_driver is not None:
            # PyTorch may ignore or reject on some versions/backends. We guard usage.
            svd_kwargs["driver"] = self.config.svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False, **svd_kwargs)
        except TypeError:
            # fallback for PyTorch versions that don't accept driver=...
            U, S, Vh = torch.linalg.svd(W, full_matrices=False)

        energy = self._energy_curve(S)

        # Omega tuning: pick smallest rank that meets the energy threshold
        # Clamp to [min_rank, max_rank]
        idx = torch.where(energy >= self.config.energy_threshold)[0]
        if idx.numel() == 0:
            # Should only happen if threshold > 1.0, but we validate, so defensive:
            rank = int(S.numel())
        else:
            rank = int(idx[0].item()) + 1

        rank = max(rank, self.config.min_rank)
        if self.config.max_rank is not None:
            rank = min(rank, self.config.max_rank)

        dense_cost = self._proxy_dense_cost(out_features, in_features)
        lowrank_cost = self._proxy_lowrank_cost(out_features, in_features, rank)
        # predicted gain fraction
        predicted_gain = 1.0 - (lowrank_cost / float(dense_cost))

        # Delta decision: apply if predicted compute reduction >= min_gain
        if lowrank_cost <= (1.0 - self.config.min_gain) * dense_cost:
            strategy = "lowrank"
        else:
            strategy = "dense"
            rank = 0

        return {
            "strategy": strategy,
            "rank": rank,
            "stats": {
                "out_features": out_features,
                "in_features": in_features,
                "dense_cost": dense_cost,
                "lowrank_cost": lowrank_cost if strategy == "lowrank" else dense_cost,
                "energy_threshold": self.config.energy_threshold,
                "energy_mode": self.config.energy_mode,
                "chosen_rank": rank,
                "predicted_gain": predicted_gain,
            },
        }


# -----------------------------------------------------------------------------
# Representation + Execution (Psi)
# -----------------------------------------------------------------------------

class QPLinear(nn.Module):
    """
    Factored Linear layer.

    Given an original nn.Linear weight W (out x in), we compute truncated SVD:
        W ≈ U_r diag(S_r) Vh_r

    We store:
        U_ = U_r * sqrt(S_r)      (out x r)
        V_ = sqrt(S_r) * Vh_r     (r x in)

    Forward:
        y = (x @ V_.T) @ U_.T + bias

    Shapes:
        x: (batch..., in)
        V_.T: (in, r)  -> xV: (batch..., r)
        U_.T: (r, out) -> y: (batch..., out)
    """

    def __init__(
        self,
        original: nn.Linear,
        rank: int,
        *,
        allow_bias: bool = True,
        svd_driver: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
        device: Optional[torch.device] = None,
    ):
        super().__init__()
        if rank < 1:
            raise ValueError("rank must be >= 1 for QPLinear")

        W = original.weight.data
        if dtype is not None:
            W = W.to(dtype)
        if device is not None:
            W = W.to(device)

        svd_kwargs = {}
        if svd_driver is not None:
            svd_kwargs["driver"] = svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False, **svd_kwargs)
        except TypeError:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False)

        r = min(rank, int(S.numel()))
        sqrt_S = torch.sqrt(S[:r])

        # Store as parameters for TorchScript compatibility.
        # U_ shape: (out, r)
        U_ = U[:, :r] * sqrt_S
        # V_ shape: (r, in)  (note: Vh[:r,:] is (r,in))
        V_ = sqrt_S.unsqueeze(1) * Vh[:r, :]

        self.U = nn.Parameter(U_.contiguous())
        self.V = nn.Parameter(V_.contiguous())

        if allow_bias and original.bias is not None:
            self.bias = nn.Parameter(original.bias.data.clone())
        else:
            self.bias = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = (x @ self.V.t()) @ self.U.t()
        if self.bias is not None:
            y = y + self.bias
        return y


# -----------------------------------------------------------------------------
# Model Transform (Sigma/Omega/Psi/Delta pipeline)
# -----------------------------------------------------------------------------

def optimize_vision_model(
    model: nn.Module,
    *,
    config: QPGEMMConfig = QPGEMMConfig(),
    inplace: bool = True,
    verbose: bool = False,
) -> nn.Module:
    """
    Recursively traverses a model and replaces nn.Linear layers with QPLinear
    when the engine decides to apply low-rank factorization.

    Args:
        model: PyTorch module.
        config: QPGEMMConfig controlling rank selection and decision thresholds.
        inplace: If True, modifies model in place; if False, operates on a deepcopy.
        verbose: If True, prints per-layer decisions.

    Returns:
        The optimized model (same object if inplace=True).
    """
    if not inplace:
        import copy
        model = copy.deepcopy(model)

    engine = QPGEMMEngine(config=config)

    def _recurse(mod: nn.Module, prefix: str = ""):
        for name, child in list(mod.named_children()):
            full_name = f"{prefix}{name}" if prefix == "" else f"{prefix}.{name}"
            if isinstance(child, nn.Linear):
                analysis = engine.analyze(child.weight.data)
                if analysis["strategy"] == "lowrank":
                    if verbose:
                        st = analysis["stats"]
                        print(
                            f"[QP-GEMM] {full_name}: lowrank r={analysis['rank']} "
                            f"(gain≈{st['predicted_gain']*100:.1f}%, out={st['out_features']}, in={st['in_features']})"
                        )
                    qpl = QPLinear(
                        child,
                        analysis["rank"],
                        allow_bias=config.allow_bias,
                        svd_driver=config.svd_driver,
                        dtype=child.weight.dtype,
                        device=child.weight.device,
                    )
                    setattr(mod, name, qpl)
                else:
                    if verbose:
                        print(f"[QP-GEMM] {full_name}: dense")
            else:
                _recurse(child, full_name)

    _recurse(model)
    return model


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def count_parameters(model: nn.Module) -> int:
    """Total number of parameters."""
    return sum(p.numel() for p in model.parameters())


def estimate_linear_proxy_cost(model: nn.Module) -> int:
    """
    Rough compute proxy: sum(out*in) for nn.Linear, or sum(r*(out+in)) for QPLinear.
    Useful for sanity checking the decision rule.
    """
    cost = 0
    for m in model.modules():
        if isinstance(m, nn.Linear):
            out_f, in_f = m.weight.shape
            cost += int(out_f) * int(in_f)
        elif isinstance(m, QPLinear):
            # U: (out, r), V: (r, in)
            out_f, r = m.U.shape
            r2, in_f = m.V.shape
            assert r == r2
            cost += int(r) * (int(out_f) + int(in_f))
    return cost


@torch.no_grad()
def layer_report(model: nn.Module) -> Dict[str, Any]:
    """
    Produce a structured report describing all Linear and QPLinear layers.

    Returns JSON-serializable dict.
    """
    layers = []
    for name, m in model.named_modules():
        if isinstance(m, nn.Linear):
            out_f, in_f = m.weight.shape
            layers.append({
                "name": name,
                "type": "Linear",
                "out_features": int(out_f),
                "in_features": int(in_f),
                "rank": None,
                "params": int(m.weight.numel()) + (int(m.bias.numel()) if m.bias is not None else 0),
            })
        elif isinstance(m, QPLinear):
            out_f, r = m.U.shape
            r2, in_f = m.V.shape
            layers.append({
                "name": name,
                "type": "QPLinear",
                "out_features": int(out_f),
                "in_features": int(in_f),
                "rank": int(r),
                "params": int(m.U.numel()) + int(m.V.numel()) + (int(m.bias.numel()) if m.bias is not None else 0),
            })

    total_params = count_parameters(model)
    proxy_cost = estimate_linear_proxy_cost(model)
    return {
        "total_params": int(total_params),
        "proxy_linear_cost": int(proxy_cost),
        "layers": layers,
    }
