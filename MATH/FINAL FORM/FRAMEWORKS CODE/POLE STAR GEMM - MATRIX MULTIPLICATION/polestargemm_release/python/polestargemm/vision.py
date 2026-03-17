"""
PoleStarGEMM Vision Optimizer (PyTorch)
======================================

This module provides the Vision-tuned portion of PoleStarGEMM: an adaptive
low-rank replacement pipeline for neural-network layers.

It implements the "Quad-Polar" idea:

- Σ (Sigma) probing: SVD analysis of weight matrices
- Ω (Omega) tuning: choose the minimal rank that preserves a spectral-energy target
- Ψ (Psi) representation: replace a large weight matrix with two skinny factors (U,V)
- Δ (Delta) decision: only apply when predicted compute/parameter savings exceed a threshold

Primary target:
- Vision models (Linear projections and optionally Conv2d) where weights are often
  compressible or at least partially low-rank after training.

Export target:
- TorchScript `.pt` for deployment in C++ (LibTorch).

Important notes:
- This optimizer is intended for **inference**. The factored parameters are stored with
  requires_grad=False by default.
- Performance gains are hardware-dependent. Always benchmark on your target CPU/GPU.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Iterable, List

import copy
import math
import time

import torch
import torch.nn as nn
import torch.nn.functional as F


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PoleStarVisionConfig:
    """
    Configuration for vision-layer optimization.

    energy_threshold:
        Minimal cumulative spectral energy retained by the truncated SVD.
        Default 0.99 is a common production tradeoff for vision inference.

    energy_mode:
        - "sv2": cumulative sum of S^2 / sum of S^2 (Frobenius energy)  [recommended]
        - "sv" : cumulative sum of S / sum of S

    min_gain:
        Minimum theoretical *compute proxy* reduction required to apply low-rank.
        Example: 0.30 => require >30% reduction.

    rank_multiple:
        If >1, rounds chosen rank up to a multiple of this (helps SIMD/tensor-core alignment).

    min_rank / max_rank:
        Safety bounds on rank.

    optimize_conv2d:
        If True, attempts a low-rank factorization for Conv2d (groups=1 only).
        Default False to keep behavior conservative.
    """
    energy_threshold: float = 0.99
    energy_mode: str = "sv2"     # "sv2" (recommended) or "sv"
    min_gain: float = 0.30
    rank_multiple: int = 8
    min_rank: int = 1
    max_rank: Optional[int] = None
    optimize_conv2d: bool = False
    svd_driver: Optional[str] = None


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _validate_config(cfg: PoleStarVisionConfig) -> None:
    if not (0.0 < cfg.energy_threshold <= 1.0):
        raise ValueError("energy_threshold must be in (0,1].")
    if cfg.energy_mode not in ("sv", "sv2"):
        raise ValueError("energy_mode must be 'sv' or 'sv2'.")
    if not (0.0 <= cfg.min_gain < 1.0):
        raise ValueError("min_gain must be in [0,1).")
    if cfg.rank_multiple < 1:
        raise ValueError("rank_multiple must be >= 1.")
    if cfg.min_rank < 1:
        raise ValueError("min_rank must be >= 1.")
    if cfg.max_rank is not None and cfg.max_rank < cfg.min_rank:
        raise ValueError("max_rank must be >= min_rank (or None).")


def _align_rank(r: int, multiple: int) -> int:
    if multiple <= 1:
        return int(r)
    return int(((r + multiple - 1) // multiple) * multiple)


def _energy_curve(S: torch.Tensor, mode: str) -> torch.Tensor:
    if S.numel() == 0:
        return torch.zeros_like(S)
    if mode == "sv2":
        e = S * S
    else:
        e = S
    return torch.cumsum(e, dim=0) / (torch.sum(e) + 1e-12)


def _linear_cost(out_features: int, in_features: int) -> int:
    # Simple proxy (multiplications) for a single output element.
    return int(out_features * in_features)


def _lowrank_cost(out_features: int, in_features: int, rank: int) -> int:
    # Proxy for two matmuls (x @ V.T) then (@ U.T)
    return int(rank * (out_features + in_features))


def _conv_param_count(out_ch: int, in_ch: int, kH: int, kW: int) -> int:
    return int(out_ch * in_ch * kH * kW)


def _conv_lowrank_param_count(out_ch: int, in_ch: int, kH: int, kW: int, rank: int) -> int:
    # conv1: rank x in_ch x kH x kW; conv2: out_ch x rank x 1 x 1
    return int(rank * in_ch * kH * kW + out_ch * rank)


def _clone_bias(bias: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
    return bias.detach().clone() if bias is not None else None


# -----------------------------------------------------------------------------
# Σ + Ω + Δ: analysis engine
# -----------------------------------------------------------------------------

class PoleStarAnalyzer:
    """
    Decide whether a given weight matrix should be replaced by a low-rank factorization.

    For Linear weight W with shape [out, in]:
        dense_cost   = out*in
        lowrank_cost = r*(out+in)
        Apply if lowrank_cost <= (1 - min_gain) * dense_cost
    """

    def __init__(self, config: PoleStarVisionConfig):
        _validate_config(config)
        self.cfg = config

    @torch.no_grad()
    def analyze_linear(self, W: torch.Tensor) -> Dict[str, Any]:
        if W.ndim != 2:
            raise ValueError(f"Expected 2D weight, got {tuple(W.shape)}")
        out_features, in_features = int(W.shape[0]), int(W.shape[1])

        svd_kwargs: Dict[str, Any] = {}
        if self.cfg.svd_driver is not None:
            svd_kwargs["driver"] = self.cfg.svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False, **svd_kwargs)
        except TypeError:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False)

        energy = _energy_curve(S, mode=self.cfg.energy_mode)
        idx = torch.where(energy >= self.cfg.energy_threshold)[0]
        if idx.numel() == 0:
            rank = int(S.numel())
        else:
            rank = int(idx[0].item() + 1)

        # Clamp + align
        rank = max(self.cfg.min_rank, rank)
        if self.cfg.max_rank is not None:
            rank = min(rank, int(self.cfg.max_rank))
        rank = min(rank, min(out_features, in_features))
        rank = _align_rank(rank, self.cfg.rank_multiple)
        rank = min(rank, min(out_features, in_features))

        dense_cost = _linear_cost(out_features, in_features)
        lowrank_cost = _lowrank_cost(out_features, in_features, rank)
        predicted_gain = 1.0 - (lowrank_cost / max(1, dense_cost))

        # Δ decision
        apply = lowrank_cost <= int((1.0 - self.cfg.min_gain) * dense_cost)

        return {
            "strategy": "lowrank" if apply else "dense",
            "rank": rank if apply else 0,
            "out_features": out_features,
            "in_features": in_features,
            "dense_cost": dense_cost,
            "lowrank_cost": lowrank_cost,
            "predicted_gain": predicted_gain,
            "energy_threshold": self.cfg.energy_threshold,
            "energy_mode": self.cfg.energy_mode,
        }

    @torch.no_grad()
    def analyze_conv2d(self, W: torch.Tensor) -> Dict[str, Any]:
        """
        Analyze Conv2d weights by flattening to [out_ch, in_ch*kH*kW] and using SVD.

        This is conservative; many Conv2d layers are not globally low-rank.
        """
        if W.ndim != 4:
            raise ValueError(f"Expected 4D conv weight, got {tuple(W.shape)}")
        out_ch, in_ch, kH, kW = map(int, W.shape)
        W2d = W.reshape(out_ch, in_ch * kH * kW)

        svd_kwargs: Dict[str, Any] = {}
        if self.cfg.svd_driver is not None:
            svd_kwargs["driver"] = self.cfg.svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W2d, full_matrices=False, **svd_kwargs)
        except TypeError:
            U, S, Vh = torch.linalg.svd(W2d, full_matrices=False)

        energy = _energy_curve(S, mode=self.cfg.energy_mode)
        idx = torch.where(energy >= self.cfg.energy_threshold)[0]
        if idx.numel() == 0:
            rank = int(S.numel())
        else:
            rank = int(idx[0].item() + 1)

        rank = max(self.cfg.min_rank, rank)
        if self.cfg.max_rank is not None:
            rank = min(rank, int(self.cfg.max_rank))
        rank = min(rank, min(W2d.shape))
        rank = _align_rank(rank, self.cfg.rank_multiple)
        rank = min(rank, min(W2d.shape))

        dense_params = _conv_param_count(out_ch, in_ch, kH, kW)
        lowrank_params = _conv_lowrank_param_count(out_ch, in_ch, kH, kW, rank)
        predicted_gain = 1.0 - (lowrank_params / max(1, dense_params))

        apply = lowrank_params <= int((1.0 - self.cfg.min_gain) * dense_params)

        return {
            "strategy": "lowrank" if apply else "dense",
            "rank": rank if apply else 0,
            "shape": (out_ch, in_ch, kH, kW),
            "dense_params": dense_params,
            "lowrank_params": lowrank_params,
            "predicted_gain": predicted_gain,
            "energy_threshold": self.cfg.energy_threshold,
            "energy_mode": self.cfg.energy_mode,
        }


# -----------------------------------------------------------------------------
# Ψ: replacement layers
# -----------------------------------------------------------------------------

class PoleStarLinear(nn.Module):
    """
    Factored Linear layer.

    Original: y = x @ W.T + b   where W is [out, in]
    Low-rank: W ≈ U diag(S) Vh  (truncate to rank r)
      Let U' = U[:, :r] * sqrt(S[:r])
          V' = sqrt(S[:r]).unsqueeze(1) * Vh[:r, :]
      Then x @ W.T ≈ (x @ V'.T) @ U'.T

    This matches the classic sqrt(S) split for numeric stability.
    """

    def __init__(
        self,
        original: nn.Linear,
        rank: int,
        *,
        allow_bias: bool = True,
        svd_driver: Optional[str] = None,
    ):
        super().__init__()
        if rank < 1:
            raise ValueError("rank must be >= 1")

        W = original.weight.detach()
        if W.ndim != 2:
            raise ValueError("Expected Linear weight to be 2D")

        svd_kwargs: Dict[str, Any] = {}
        if svd_driver is not None:
            svd_kwargs["driver"] = svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False, **svd_kwargs)
        except TypeError:
            U, S, Vh = torch.linalg.svd(W, full_matrices=False)

        r = min(int(rank), int(S.numel()))
        sqrt_S = torch.sqrt(S[:r])

        U_fac = U[:, :r] * sqrt_S
        V_fac = sqrt_S.unsqueeze(1) * Vh[:r, :]

        # Store as parameters w/ requires_grad=False (inference)
        self.U = nn.Parameter(U_fac.contiguous(), requires_grad=False)
        self.V = nn.Parameter(V_fac.contiguous(), requires_grad=False)

        if allow_bias and original.bias is not None:
            self.bias = nn.Parameter(_clone_bias(original.bias), requires_grad=False)
        else:
            self.register_parameter("bias", None)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = (x @ self.V.t()) @ self.U.t()
        if self.bias is not None:
            y = y + self.bias
        return y


class PoleStarConv2d(nn.Module):
    """
    Optional low-rank Conv2d approximation (groups=1).

    Decompose W2d = reshape(W, [out_ch, in_ch*kH*kW]) ≈ U diag(S) Vh

    Then implement as:
      conv1: in_ch -> rank with kernel (kH,kW) weights from Vh
      conv2: rank -> out_ch with 1x1 weights from U

    Bias is applied after conv2.
    """

    def __init__(
        self,
        original: nn.Conv2d,
        rank: int,
        *,
        allow_bias: bool = True,
        svd_driver: Optional[str] = None,
    ):
        super().__init__()
        if original.groups != 1:
            raise ValueError("PoleStarConv2d only supports groups=1")
        if rank < 1:
            raise ValueError("rank must be >= 1")

        W = original.weight.detach()
        out_ch, in_ch, kH, kW = map(int, W.shape)

        W2d = W.reshape(out_ch, in_ch * kH * kW)

        svd_kwargs: Dict[str, Any] = {}
        if svd_driver is not None:
            svd_kwargs["driver"] = svd_driver

        try:
            U, S, Vh = torch.linalg.svd(W2d, full_matrices=False, **svd_kwargs)
        except TypeError:
            U, S, Vh = torch.linalg.svd(W2d, full_matrices=False)

        r = min(int(rank), int(S.numel()))
        sqrt_S = torch.sqrt(S[:r])

        # V' -> conv1 weights
        V_fac = (sqrt_S.unsqueeze(1) * Vh[:r, :]).reshape(r, in_ch, kH, kW)

        # U' -> conv2 weights (1x1 conv)
        U_fac = (U[:, :r] * sqrt_S).reshape(out_ch, r, 1, 1)

        self.conv1 = nn.Conv2d(
            in_channels=in_ch,
            out_channels=r,
            kernel_size=(kH, kW),
            stride=original.stride,
            padding=original.padding,
            dilation=original.dilation,
            bias=False,
        )
        self.conv2 = nn.Conv2d(
            in_channels=r,
            out_channels=out_ch,
            kernel_size=(1, 1),
            stride=1,
            padding=0,
            dilation=1,
            bias=False,
        )

        self.conv1.weight = nn.Parameter(V_fac.contiguous(), requires_grad=False)
        self.conv2.weight = nn.Parameter(U_fac.contiguous(), requires_grad=False)

        if allow_bias and original.bias is not None:
            self.bias = nn.Parameter(_clone_bias(original.bias), requires_grad=False)
        else:
            self.register_parameter("bias", None)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.conv2(self.conv1(x))
        if self.bias is not None:
            y = y + self.bias.view(1, -1, 1, 1)
        return y


# -----------------------------------------------------------------------------
# Model optimization + reporting
# -----------------------------------------------------------------------------

@dataclass
class OptimizationReport:
    original_params: int
    optimized_params: int
    compression_ratio: float
    layers_modified: int
    layers_total: int
    per_layer: List[Dict[str, Any]]
    config: PoleStarVisionConfig


def optimize_model(
    model: nn.Module,
    *,
    config: PoleStarVisionConfig = PoleStarVisionConfig(),
    skip_name_substrings: Optional[List[str]] = None,
    verbose: bool = True,
) -> Tuple[nn.Module, OptimizationReport]:
    """
    Recursively replace eligible layers with PoleStar low-rank variants.

    Returns a new model instance (deepcopy) plus a report.
    """
    _validate_config(config)
    if skip_name_substrings is None:
        skip_name_substrings = []

    model_opt = copy.deepcopy(model).eval()
    analyzer = PoleStarAnalyzer(config)

    original_params = sum(p.numel() for p in model_opt.parameters())
    per_layer: List[Dict[str, Any]] = []
    layers_modified = 0
    layers_total = 0

    def should_skip(name: str) -> bool:
        return any(s in name for s in skip_name_substrings)

    def recurse(module: nn.Module, prefix: str = "") -> None:
        nonlocal layers_modified, layers_total, per_layer

        for name, child in list(module.named_children()):
            full_name = f"{prefix}.{name}" if prefix else name

            if should_skip(full_name):
                if verbose:
                    print(f"SKIP: {full_name}")
                continue

            if isinstance(child, nn.Linear):
                layers_total += 1
                info = analyzer.analyze_linear(child.weight.detach())
                if info["strategy"] == "lowrank":
                    setattr(module, name, PoleStarLinear(child, info["rank"], allow_bias=True, svd_driver=config.svd_driver))
                    layers_modified += 1
                    per_layer.append({"name": full_name, "type": "Linear", **info})
                    if verbose:
                        print(f"OPT:  {full_name} Linear {info['out_features']}x{info['in_features']} -> rank={info['rank']} gain~{info['predicted_gain']*100:.1f}%")
                else:
                    if verbose:
                        print(f"KEEP: {full_name} Linear (dense)")

            elif config.optimize_conv2d and isinstance(child, nn.Conv2d):
                layers_total += 1
                if child.groups != 1:
                    if verbose:
                        print(f"KEEP: {full_name} Conv2d (groups={child.groups})")
                    continue
                info = analyzer.analyze_conv2d(child.weight.detach())
                if info["strategy"] == "lowrank":
                    setattr(module, name, PoleStarConv2d(child, info["rank"], allow_bias=True, svd_driver=config.svd_driver))
                    layers_modified += 1
                    per_layer.append({"name": full_name, "type": "Conv2d", **info})
                    if verbose:
                        print(f"OPT:  {full_name} Conv2d {info['shape']} -> rank={info['rank']} gain~{info['predicted_gain']*100:.1f}%")
                else:
                    if verbose:
                        print(f"KEEP: {full_name} Conv2d (dense)")

            else:
                # recurse into other modules
                if len(list(child.children())) > 0:
                    recurse(child, full_name)

    recurse(model_opt)

    optimized_params = sum(p.numel() for p in model_opt.parameters())
    compression = (original_params / optimized_params) if optimized_params > 0 else 1.0

    report = OptimizationReport(
        original_params=original_params,
        optimized_params=optimized_params,
        compression_ratio=float(compression),
        layers_modified=layers_modified,
        layers_total=layers_total,
        per_layer=per_layer,
        config=config,
    )
    return model_opt, report


# -----------------------------------------------------------------------------
# Benchmarking + validation
# -----------------------------------------------------------------------------

@torch.no_grad()
def benchmark_model(
    model: nn.Module,
    example_input: torch.Tensor,
    *,
    warmup: int = 20,
    iters: int = 200,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Benchmark inference latency for the given model and example input.
    Returns ms statistics.
    """
    model = model.eval().to(device)
    x = example_input.to(device)

    # Warmup
    for _ in range(max(0, int(warmup))):
        _ = model(x)

    if device.startswith("cuda"):
        torch.cuda.synchronize()

    times: List[float] = []
    for _ in range(max(1, int(iters))):
        t0 = time.perf_counter()
        _ = model(x)
        if device.startswith("cuda"):
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    t = torch.tensor(times)
    return {
        "mean_ms": float(t.mean().item()),
        "p50_ms": float(t.median().item()),
        "p95_ms": float(t.quantile(0.95).item()),
        "min_ms": float(t.min().item()),
        "max_ms": float(t.max().item()),
        "iters": float(len(times)),
    }


@torch.no_grad()
def validate_relative_error(
    model_ref: nn.Module,
    model_opt: nn.Module,
    example_input: torch.Tensor,
    *,
    samples: int = 10,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Compare outputs between reference and optimized models on random inputs.
    """
    model_ref = model_ref.eval().to(device)
    model_opt = model_opt.eval().to(device)

    errs: List[float] = []
    for _ in range(max(1, int(samples))):
        x = torch.randn_like(example_input).to(device)
        y0 = model_ref(x)
        y1 = model_opt(x)
        denom = y0.abs().mean() + 1e-8
        rel = (y0 - y1).abs().mean() / denom
        errs.append(float(rel.item()))

    t = torch.tensor(errs)
    return {
        "mean_relative_error": float(t.mean().item()),
        "max_relative_error": float(t.max().item()),
        "std_relative_error": float(t.std(unbiased=False).item()),
        "samples": float(len(errs)),
    }


# -----------------------------------------------------------------------------
# TorchScript export
# -----------------------------------------------------------------------------

def export_torchscript(
    model: nn.Module,
    example_input: torch.Tensor,
    out_path: str,
    *,
    method: str = "trace",
) -> str:
    """
    Export model to TorchScript `.pt`.

    method:
        - "trace": torch.jit.trace (fast, requires static control flow)
        - "script": torch.jit.script (handles control flow, may fail for some models)
    """
    model = model.eval()
    if method not in ("trace", "script"):
        raise ValueError("method must be 'trace' or 'script'")

    if method == "script":
        ts = torch.jit.script(model)
    else:
        ts = torch.jit.trace(model, example_input)

    ts.save(out_path)
    return out_path
