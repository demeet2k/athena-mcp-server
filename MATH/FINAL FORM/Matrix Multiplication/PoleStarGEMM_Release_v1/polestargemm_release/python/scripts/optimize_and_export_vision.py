#!/usr/bin/env python3
"""
PoleStarGEMM: Optimize a PyTorch model + export TorchScript (.pt)

Examples:
    # Toy MLP
    python scripts/optimize_and_export_vision.py --model toy_mlp --input-dim 2048 --batch 32 --out vision_polestargemm.pt

    # Torchvision ResNet (requires torchvision)
    python scripts/optimize_and_export_vision.py --model resnet18 --image-size 224 --batch 8 --optimize-conv2d --out resnet18_polestargemm.pt
"""

import argparse
import copy
import os
import time
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from polestargemm.vision import (
    PoleStarVisionConfig,
    optimize_model,
    benchmark_model,
    validate_relative_error,
    export_torchscript,
)


class ToyMLP(nn.Module):
    def __init__(self, input_dim: int = 2048, hidden: int = 2048, layers: int = 4):
        super().__init__()
        blocks = []
        d = input_dim
        for i in range(layers):
            blocks.append(nn.Linear(d, hidden))
            blocks.append(nn.GELU())
            d = hidden
        blocks.append(nn.Linear(d, hidden))
        self.net = nn.Sequential(*blocks)

    def forward(self, x):
        return self.net(x)


def load_model(name_or_path: str) -> nn.Module:
    if os.path.exists(name_or_path) and (name_or_path.endswith(".pt") or name_or_path.endswith(".pth")):
        obj = torch.load(name_or_path, map_location="cpu")
        if isinstance(obj, nn.Module):
            return obj
        if isinstance(obj, dict):
            raise ValueError("Loaded a state_dict; please provide code to construct the model and load state_dict.")
        raise ValueError("Unsupported .pt/.pth content")
    # torchvision model
    try:
        import torchvision.models as models  # type: ignore
        fn = getattr(models, name_or_path, None)
        if fn is None:
            raise ValueError(f"Unknown torchvision model: {name_or_path}")
        return fn(weights=None).eval()
    except Exception as e:
        raise ValueError(f"Could not load model '{name_or_path}'. If this is a torchvision model, install torchvision. Error: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=str, default="toy_mlp", help="toy_mlp, torchvision name, or path to .pt/.pth (module object)")
    p.add_argument("--out", type=str, default="polestargemm_model.pt")
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--input-dim", type=int, default=2048, help="For toy_mlp inputs")
    p.add_argument("--image-size", type=int, default=224, help="For torchvision image inputs")
    p.add_argument("--energy-threshold", type=float, default=0.99)
    p.add_argument("--energy-mode", type=str, default="sv2", choices=["sv", "sv2"])
    p.add_argument("--min-gain", type=float, default=0.30)
    p.add_argument("--rank-multiple", type=int, default=8)
    p.add_argument("--optimize-conv2d", action="store_true")
    p.add_argument("--bench-iters", type=int, default=100)
    p.add_argument("--ts-method", type=str, default="trace", choices=["trace", "script"])
    args = p.parse_args()

    # Load model
    if args.model == "toy_mlp":
        model = ToyMLP(input_dim=args.input_dim).eval()
        example = torch.randn(args.batch, args.input_dim)
    else:
        model = load_model(args.model).eval()
        example = torch.randn(args.batch, 3, args.image_size, args.image_size)

    cfg = PoleStarVisionConfig(
        energy_threshold=args.energy_threshold,
        energy_mode=args.energy_mode,
        min_gain=args.min_gain,
        rank_multiple=args.rank_multiple,
        optimize_conv2d=args.optimize_conv2d,
    )

    print("\n=== Optimizing model ===")
    model_opt, report = optimize_model(model, config=cfg, verbose=True)
    print(f"\nCompression: {report.compression_ratio:.2f}x  Layers modified: {report.layers_modified}/{report.layers_total}")

    print("\n=== Benchmarking ===")
    b0 = benchmark_model(model, example, iters=args.bench_iters, device=args.device)
    b1 = benchmark_model(model_opt, example, iters=args.bench_iters, device=args.device)
    print(f"Original mean:  {b0['mean_ms']:.3f} ms  p50: {b0['p50_ms']:.3f} ms")
    print(f"Optimized mean: {b1['mean_ms']:.3f} ms  p50: {b1['p50_ms']:.3f} ms")
    print(f"Speedup (mean): {b0['mean_ms']/max(1e-12,b1['mean_ms']):.2f}x")

    print("\n=== Validating output drift ===")
    err = validate_relative_error(model, model_opt, example, samples=10, device=args.device)
    print(err)

    print("\n=== Exporting TorchScript ===")
    out_path = export_torchscript(model_opt.to("cpu"), example.to("cpu"), args.out, method=args.ts_method)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
