"""
Thorough stress test harness for Adaptive QP-GEMM (Python).

This script is meant to detect:
- numerical regressions (relative error drift)
- performance cliffs across batch sizes / distributions / scaling
- stability issues under repeated runs

It can test:
- a TorchScript optimized artifact (.pt)
- optionally a baseline TorchScript artifact for accuracy comparisons

Outputs:
- JSON report with per-test metrics

Example:
  python stress_test_qpgemm.py --pt artifacts/vision_model_qpgemm.pt --baseline_pt artifacts/vision_model_dense.pt \
      --device cpu --batch_list 1,4,8,16,32,64,128 --input_size 2048 --iters 200

Tip:
- Use --soak_seconds for a long-running test.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, Any, List, Tuple

import numpy as np
import torch


def rel_l2(a: torch.Tensor, b: torch.Tensor, eps=1e-12) -> float:
    num = (a - b).norm().item()
    den = max(b.norm().item(), eps)
    return float(num / den)


def max_abs(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a - b).abs().max().item())


def cosine_sim(a: torch.Tensor, b: torch.Tensor, eps=1e-12) -> float:
    a2 = a.flatten()
    b2 = b.flatten()
    num = torch.dot(a2, b2).item()
    den = max((a2.norm() * b2.norm()).item(), eps)
    return float(num / den)


def percentile(xs, p):
    xs = np.asarray(xs, dtype=np.float64)
    return float(np.percentile(xs, p))


@torch.inference_mode()
def time_model(model, x, iters=200, warmup=20, synchronize_cuda: bool = True) -> Dict[str, Any]:
    # Warmup
    for _ in range(warmup):
        _ = model(x)
    if x.is_cuda and synchronize_cuda:
        torch.cuda.synchronize()

    lat = []
    for _ in range(iters):
        t0 = time.perf_counter()
        _ = model(x)
        if x.is_cuda and synchronize_cuda:
            torch.cuda.synchronize()
        lat.append((time.perf_counter() - t0) * 1000.0)

    return {
        "p50_ms": percentile(lat, 50),
        "p90_ms": percentile(lat, 90),
        "p99_ms": percentile(lat, 99),
        "mean_ms": float(np.mean(lat)),
        "max_ms": float(np.max(lat)),
    }


def make_distributions(input_size: int, device: torch.device, dtype: torch.dtype):
    # Return list of (name, generator_fn(batch)->tensor)
    return [
        ("normal", lambda b: torch.randn(b, input_size, device=device, dtype=dtype)),
        ("uniform", lambda b: (torch.rand(b, input_size, device=device, dtype=dtype) * 2 - 1)),
        ("scaled_1e3", lambda b: torch.randn(b, input_size, device=device, dtype=dtype) * 1e3),
        ("scaled_1e-3", lambda b: torch.randn(b, input_size, device=device, dtype=dtype) * 1e-3),
        ("outliers", lambda b: (torch.randn(b, input_size, device=device, dtype=dtype).clamp(-2, 2)
                               + (torch.rand(b, input_size, device=device, dtype=dtype) < 0.001).to(dtype) * 20.0)),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pt", required=True, help="Path to optimized TorchScript .pt")
    ap.add_argument("--baseline_pt", default=None, help="Optional baseline TorchScript .pt for accuracy comparisons")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--input_size", type=int, default=2048)
    ap.add_argument("--batch_list", default="1,4,8,16,32,64", help="Comma-separated batch sizes")
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--warmup", type=int, default=20)

    ap.add_argument("--soak_seconds", type=int, default=0, help="If >0, run a steady-state soak test for N seconds")
    ap.add_argument("--soak_batch", type=int, default=32)
    ap.add_argument("--soak_dist", default="normal")
    ap.add_argument("--soak_report_every", type=int, default=10, help="Seconds between soak stat dumps")

    ap.add_argument("--report", default="qpgemm_stress_report.json")
    args = ap.parse_args()

    device = torch.device(args.device)
    dtype_map = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}
    dtype = dtype_map[args.dtype]

    qpgemm = torch.jit.load(args.pt, map_location=device).eval()
    baseline = torch.jit.load(args.baseline_pt, map_location=device).eval() if args.baseline_pt else None

    batches = [int(x.strip()) for x in args.batch_list.split(",") if x.strip()]

    report: Dict[str, Any] = {
        "pt": args.pt,
        "baseline_pt": args.baseline_pt,
        "device": args.device,
        "dtype": args.dtype,
        "input_size": args.input_size,
        "runs": [],
        "nan_inf_test": None,
        "soak": None,
    }

    dists = make_distributions(args.input_size, device, dtype)

    # Main sweep
    for b in batches:
        for name, gen in dists:
            x = gen(b)
            y = qpgemm(x)
            run: Dict[str, Any] = {
                "batch": b,
                "dist": name,
                "output_shape": list(y.shape),
                "perf": time_model(qpgemm, x, iters=args.iters, warmup=args.warmup),
            }
            if baseline is not None:
                y_ref = baseline(x)
                run.update({
                    "rel_l2": rel_l2(y, y_ref),
                    "max_abs": max_abs(y, y_ref),
                    "cosine": cosine_sim(y, y_ref),
                })
            report["runs"].append(run)
            print(f"[b={b:4d} dist={name:10s}] p50={run['perf']['p50_ms']:.3f}ms"
                  + (f" rel_l2={run.get('rel_l2', float('nan')):.6f}" if baseline is not None else ""))

    # NaN/Inf robustness test (should not crash)
    x = torch.randn(max(batches), args.input_size, device=device, dtype=dtype)
    x.view(-1)[0] = float("nan")
    x.view(-1)[1] = float("inf")
    try:
        _ = qpgemm(x)
        report["nan_inf_test"] = "ok"
    except Exception as e:
        report["nan_inf_test"] = f"failed: {repr(e)}"

    # Soak test (optional)
    if args.soak_seconds > 0:
        dist_map = {name: gen for name, gen in dists}
        if args.soak_dist not in dist_map:
            raise ValueError(f"--soak_dist must be one of: {list(dist_map.keys())}")

        x = dist_map[args.soak_dist](args.soak_batch)
        # Warmup
        for _ in range(50):
            _ = qpgemm(x)
        if x.is_cuda:
            torch.cuda.synchronize()

        start = time.time()
        next_report = start + args.soak_report_every
        lat = []
        calls = 0

        while time.time() - start < args.soak_seconds:
            t0 = time.perf_counter()
            _ = qpgemm(x)
            if x.is_cuda:
                torch.cuda.synchronize()
            lat.append((time.perf_counter() - t0) * 1000.0)
            calls += 1

            now = time.time()
            if now >= next_report:
                # Rolling stats
                snap = {
                    "elapsed_s": float(now - start),
                    "calls": int(calls),
                    "p50_ms": percentile(lat, 50),
                    "p99_ms": percentile(lat, 99),
                    "max_ms": float(np.max(lat)),
                }
                print(f"[soak] t={snap['elapsed_s']:.1f}s calls={snap['calls']} p50={snap['p50_ms']:.3f} p99={snap['p99_ms']:.3f}")
                report["soak"] = snap
                next_report = now + args.soak_report_every

    with open(args.report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Wrote report: {args.report}")


if __name__ == "__main__":
    main()
