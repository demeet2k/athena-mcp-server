#!/usr/bin/env python3
"""
PoleStarGEMM: Quick GEMM benchmark + ablation demo

Run:
    python -m scripts.bench_matmul

Or:
    python scripts/bench_matmul.py

This prints summary tables for:
- exact dense GEMM (BLAS)
- approximate-enabled (low-rank opportunism + validation)
- reuse + noncontiguous (cached contiguity)
"""

import numpy as np

from polestargemm.core import PoleStarGEMM, make_ablation_configs, summarize_ablation


def make_workloads(seed: int = 0):
    rng = np.random.default_rng(seed)

    # Dense baseline
    A1 = rng.standard_normal((128, 128))
    B1 = rng.standard_normal((128, 128))

    # Rectangular
    A2 = rng.standard_normal((256, 64))
    B2 = rng.standard_normal((64, 128))

    # Low-rank A (rank ~ 12)
    U = rng.standard_normal((256, 12))
    V = rng.standard_normal((12, 256))
    A3 = U @ V
    B3 = rng.standard_normal((256, 128))

    # Noncontiguous A (transpose slice)
    A4 = rng.standard_normal((240, 180)).T  # non-contig (180,240)
    B4 = rng.standard_normal((240, 120))

    return [(A1, B1), (A2, B2), (A3, B3), (A4, B4)]


def run_case(case_name: str, *, allow_approx: bool, rtol: float, reuse_a: bool, reuse_b: bool):
    workloads = make_workloads(seed=1)

    print("\n" + "=" * 80)
    print(case_name)
    print("=" * 80)

    configs = make_ablation_configs(verbose=False)
    rows_by_cfg = {}

    for name, engine in configs:
        rows = engine.ablation_run(
            workloads,
            repeats=2,
            allow_approx=allow_approx,
            rtol=rtol,
            reuse_a=reuse_a,
            reuse_b=reuse_b,
        )
        rows_by_cfg[name] = rows

    # Print summary table
    names = list(rows_by_cfg.keys())
    summary = {n: summarize_ablation(rows_by_cfg[n]) for n in names}

    header = f"{'CONFIG':<14} {'mean_ms':>10} {'p50_ms':>10} {'best_ms':>10} {'mean_err':>12} {'worst_err':>12}"
    print(header)
    print("-" * len(header))
    for n in names:
        s = summary[n]
        print(
            f"{n:<14} "
            f"{s['mean_time_ms']:>10.3f} "
            f"{s['p50_time_ms']:>10.3f} "
            f"{s['best_time_ms']:>10.3f} "
            f"{str(None if s['mean_err'] is None else round(s['mean_err'], 6)):>12} "
            f"{str(None if s['worst_err'] is None else round(s['worst_err'], 6)):>12}"
        )


if __name__ == "__main__":
    run_case("EXACT (allow_approx=False)", allow_approx=False, rtol=1e-2, reuse_a=False, reuse_b=False)
    run_case("APPROX ENABLED (rtol=1e-2)", allow_approx=True, rtol=1e-2, reuse_a=True, reuse_b=False)
    run_case("REUSE NONCONTIG A (exact, reuse_a=True)", allow_approx=False, rtol=1e-2, reuse_a=True, reuse_b=False)
