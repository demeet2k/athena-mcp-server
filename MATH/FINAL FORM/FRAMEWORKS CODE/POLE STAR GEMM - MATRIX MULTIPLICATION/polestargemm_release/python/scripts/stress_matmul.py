#!/usr/bin/env python3
"""
PoleStarGEMM: GEMM stress test harness (NumPy)

This script stress-tests:
- correctness in exact mode
- validation + fallback behavior in approximate mode
- stability under noncontiguous inputs and reuse hints
- performance trends across matrix sizes and structures

Usage:
    python scripts/stress_matmul.py --out results.csv --approx

Outputs:
    - CSV with per-case timings and error stats
    - printed summary statistics
"""

import argparse
import csv
import math
import time
from dataclasses import asdict
from typing import Dict, List, Tuple

import numpy as np

from polestargemm.core import PoleStarGEMM


def make_case(rng: np.random.Generator, kind: str, m: int, k: int, n: int, lowrank_r: int = 32, sparsity: float = 0.9):
    if kind == "dense":
        A = rng.standard_normal((m, k))
        B = rng.standard_normal((k, n))
    elif kind == "lowrankA":
        r = min(lowrank_r, m, k)
        U = rng.standard_normal((m, r))
        V = rng.standard_normal((r, k))
        A = U @ V
        B = rng.standard_normal((k, n))
    elif kind == "lowrankB":
        r = min(lowrank_r, k, n)
        U = rng.standard_normal((k, r))
        V = rng.standard_normal((r, n))
        B = U @ V
        A = rng.standard_normal((m, k))
    elif kind == "sparseA":
        A = rng.standard_normal((m, k))
        mask = rng.random((m, k)) < sparsity
        A[mask] = 0.0
        B = rng.standard_normal((k, n))
    elif kind == "noncontigA":
        A = rng.standard_normal((k, m)).T  # (m,k) but noncontig
        B = rng.standard_normal((k, n))
    else:
        raise ValueError(f"Unknown kind={kind}")
    return A, B


def rel_error(C: np.ndarray, C_ref: np.ndarray) -> float:
    denom = np.linalg.norm(C_ref) + 1e-12
    return float(np.linalg.norm(C - C_ref) / denom)


def time_call(fn, repeats: int = 5) -> float:
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        _ = fn()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return float(np.median(times))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=str, default="polestargemm_stress_results.csv")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--approx", action="store_true", help="Enable allow_approx with validation")
    p.add_argument("--rtol", type=float, default=1e-2)
    p.add_argument("--repeats", type=int, default=3)
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)

    engine = PoleStarGEMM(verbose=False, key_mode="sample_hash")

    shapes: List[Tuple[int, int, int]] = [
        (128, 128, 128),
        (256, 256, 256),
        (512, 512, 512),
        (256, 64, 128),
        (1024, 256, 256),
        (256, 1024, 256),
    ]
    kinds = ["dense", "lowrankA", "lowrankB", "sparseA", "noncontigA"]

    rows: List[Dict[str, float]] = []
    for (m, k, n) in shapes:
        for kind in kinds:
            A, B = make_case(rng, kind, m, k, n)

            # Baseline: BLAS
            t_blas = time_call(lambda: (A @ B), repeats=args.repeats)
            C_ref = A @ B

            # Adaptive
            t_adapt = time_call(lambda: engine.matmul(A, B, allow_approx=args.approx, rtol=args.rtol, reuse_a=True, reuse_b=False).C,
                                repeats=args.repeats)

            res = engine.matmul(A, B, allow_approx=args.approx, rtol=args.rtol, reuse_a=True, reuse_b=False)
            C = res.C
            err = rel_error(C, C_ref)

            rows.append({
                "m": m, "k": k, "n": n,
                "kind": kind,
                "approx": 1.0 if args.approx else 0.0,
                "rtol": float(args.rtol),
                "plan": res.plan,
                "t_blas_ms": t_blas * 1000.0,
                "t_adapt_ms": t_adapt * 1000.0,
                "speedup": (t_blas / max(1e-12, t_adapt)),
                "rel_error": err,
            })

            print(f"{kind:10s} {m:4d}x{k:4d}x{n:4d} | plan={res.plan:12s} | "
                  f"blas={t_blas*1000:8.2f} ms | adapt={t_adapt*1000:8.2f} ms | "
                  f"speedup={t_blas/max(1e-12,t_adapt):5.2f}x | err={err:.2e}")

    # Write CSV
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Summary
    speedups = np.array([r["speedup"] for r in rows])
    errs = np.array([r["rel_error"] for r in rows])
    print("\nSUMMARY")
    print("-------")
    print(f"Cases: {len(rows)}")
    print(f"Speedup median: {np.median(speedups):.2f}x  p90: {np.quantile(speedups,0.90):.2f}x  max: {np.max(speedups):.2f}x")
    print(f"Error  median: {np.median(errs):.2e}  max: {np.max(errs):.2e}")
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
