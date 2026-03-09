"""
Benchmark & validation suite for Adaptive QP-GEMM (Python).

This script can benchmark:
- baseline nn.Module (dense)
- optimized nn.Module (QP-GEMM)
- TorchScript versions of each

It reports:
- latency statistics (p50/p90/p99)
- parameter counts
- proxy compute cost
- relative error between baseline and optimized outputs

Usage examples:
  python benchmark.py --device cpu --input_size 2048 --batch 32 --iters 200
  python benchmark.py --device cuda --input_size 2048 --batch 32 --iters 500

If you already have exported artifacts:
  python benchmark.py --load_pt artifacts/vision_model_qpgemm.pt --baseline_pt artifacts/vision_model_dense.pt
"""

from __future__ import annotations

import argparse
import time
import numpy as np
import torch
import torch.nn as nn

from qpgemm import QPGEMMConfig, optimize_vision_model, count_parameters, estimate_linear_proxy_cost

from export_torchscript import SimVisionStack


def percentile(xs, p):
    xs = np.asarray(xs, dtype=np.float64)
    return float(np.percentile(xs, p))


@torch.inference_mode()
def run_timing(model, x, warmup: int, iters: int):
    # Warmup
    for _ in range(warmup):
        _ = model(x)
    # Timed
    lat = []
    for _ in range(iters):
        t0 = time.perf_counter()
        _ = model(x)
        lat.append((time.perf_counter() - t0) * 1000.0)
    return {
        "p50_ms": percentile(lat, 50),
        "p90_ms": percentile(lat, 90),
        "p99_ms": percentile(lat, 99),
        "mean_ms": float(np.mean(lat)),
        "max_ms": float(np.max(lat)),
    }


def rel_l2(a: torch.Tensor, b: torch.Tensor, eps=1e-12) -> float:
    num = (a - b).norm().item()
    den = max(b.norm().item(), eps)
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--input_size", type=int, default=2048)
    ap.add_argument("--hidden", type=int, default=2048)
    ap.add_argument("--num_layers", type=int, default=4)
    ap.add_argument("--num_classes", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--iters", type=int, default=200)

    ap.add_argument("--threshold", type=float, default=0.99)
    ap.add_argument("--energy_mode", choices=["sv", "sv2"], default="sv")
    ap.add_argument("--min_gain", type=float, default=0.30)

    ap.add_argument("--load_pt", default=None, help="Path to optimized TorchScript .pt")
    ap.add_argument("--baseline_pt", default=None, help="Path to baseline TorchScript .pt")
    args = ap.parse_args()

    device = torch.device(args.device)
    dtype_map = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}
    dtype = dtype_map[args.dtype]

    x = torch.randn(args.batch, args.input_size, device=device, dtype=dtype)

    if args.load_pt:
        opt = torch.jit.load(args.load_pt, map_location=device).eval()
        base = torch.jit.load(args.baseline_pt, map_location=device).eval() if args.baseline_pt else None
        print(f"[Load] optimized={args.load_pt}")
        if args.baseline_pt:
            print(f"[Load] baseline={args.baseline_pt}")
    else:
        # Build baseline -> optimize
        base = SimVisionStack(args.input_size, args.hidden, args.num_layers, args.num_classes).to(device=device, dtype=dtype).eval()
        cfg = QPGEMMConfig(energy_threshold=args.threshold, energy_mode=args.energy_mode, min_gain=args.min_gain)
        opt = optimize_vision_model(base, config=cfg, inplace=False).eval()

    # Report parameter counts & proxy costs only for eager models
    if isinstance(opt, nn.Module) and not isinstance(opt, torch.jit.RecursiveScriptModule):
        print(f"Params baseline:  {count_parameters(base):,}")
        print(f"Params optimized: {count_parameters(opt):,}")
        print(f"Proxy cost baseline:  {estimate_linear_proxy_cost(base):,}")
        print(f"Proxy cost optimized: {estimate_linear_proxy_cost(opt):,}")

    # Accuracy
    if base is not None:
        with torch.inference_mode():
            y_base = base(x)
            y_opt = opt(x)
        print(f"rel_l2 error: {rel_l2(y_opt, y_base):.6f}")
        print(f"max abs error: {(y_opt - y_base).abs().max().item():.6f}")

    # Perf
    print("\n[Perf] Baseline")
    if base is not None:
        print(run_timing(base, x, args.warmup, args.iters))
    else:
        print("N/A (no baseline loaded)")

    print("\n[Perf] Optimized")
    print(run_timing(opt, x, args.warmup, args.iters))


if __name__ == "__main__":
    main()
