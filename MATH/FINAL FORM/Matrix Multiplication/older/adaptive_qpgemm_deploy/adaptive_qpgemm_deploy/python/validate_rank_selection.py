"""
Rank-selection validation for Adaptive QP-GEMM.

This script answers questions like:
- For each Linear layer, what rank was chosen?
- Does the chosen rank satisfy the requested energy threshold?
- What is the actual reconstruction error at that rank?

This is a framework-level validation (Sigma/Omega correctness), not a model-output test.

Usage:
  python validate_rank_selection.py --input_size 2048 --hidden 2048 --num_layers 4 --threshold 0.99
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Any, List

import torch
import torch.nn as nn

from qpgemm import QPGEMMConfig, QPGEMMEngine
from export_torchscript import SimVisionStack


def frob_rel_error(W: torch.Tensor, W_hat: torch.Tensor, eps=1e-12) -> float:
    num = (W - W_hat).norm().item()
    den = max(W.norm().item(), eps)
    return float(num / den)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.99)
    ap.add_argument("--energy_mode", choices=["sv", "sv2"], default="sv")
    ap.add_argument("--min_gain", type=float, default=0.30)
    ap.add_argument("--min_rank", type=int, default=1)
    ap.add_argument("--max_rank", type=int, default=None)

    ap.add_argument("--input_size", type=int, default=2048)
    ap.add_argument("--hidden", type=int, default=2048)
    ap.add_argument("--num_layers", type=int, default=4)
    ap.add_argument("--num_classes", type=int, default=1000)

    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--out_json", default="rank_validation_report.json")
    args = ap.parse_args()

    device = torch.device(args.device)
    dtype_map = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}
    dtype = dtype_map[args.dtype]

    cfg = QPGEMMConfig(
        energy_threshold=args.threshold,
        energy_mode=args.energy_mode,
        min_gain=args.min_gain,
        min_rank=args.min_rank,
        max_rank=args.max_rank,
    )
    engine = QPGEMMEngine(cfg)

    model = SimVisionStack(args.input_size, args.hidden, args.num_layers, args.num_classes).to(device=device, dtype=dtype).eval()

    rows: List[Dict[str, Any]] = []
    for name, m in model.named_modules():
        if isinstance(m, nn.Linear):
            W = m.weight.data
            analysis = engine.analyze(W)
            strategy = analysis["strategy"]
            rank = analysis["rank"]

            # Compute the "energy satisfied?" for the chosen rank
            # and compute actual reconstruction error (relative Frobenius).
            with torch.no_grad():
                U, S, Vh = torch.linalg.svd(W, full_matrices=False)
                if rank > 0:
                    Ur = U[:, :rank]
                    Sr = S[:rank]
                    Vhr = Vh[:rank, :]
                    W_hat = Ur @ torch.diag(Sr) @ Vhr
                    err = frob_rel_error(W, W_hat)
                else:
                    err = 0.0

                # compute cumulative energy at rank
                if cfg.energy_mode == "sv":
                    energy = torch.cumsum(S, 0) / (torch.sum(S) + 1e-12)
                else:
                    energy = torch.cumsum(S*S, 0) / (torch.sum(S*S) + 1e-12)
                energy_at_rank = float(energy[rank-1].item()) if rank > 0 else 1.0

            row = {
                "layer": name,
                "shape": [int(W.shape[0]), int(W.shape[1])],
                "strategy": strategy,
                "rank": int(rank),
                "energy_at_rank": energy_at_rank,
                "energy_threshold": cfg.energy_threshold,
                "reconstruction_rel_frob_err": err,
                "proxy_stats": analysis["stats"],
            }
            rows.append(row)

            print(f"[{name}] {row['shape']} strategy={strategy} rank={rank} energy={energy_at_rank:.4f} frob_err={err:.4f}")

    report = {
        "config": {
            "threshold": cfg.energy_threshold,
            "energy_mode": cfg.energy_mode,
            "min_gain": cfg.min_gain,
            "min_rank": cfg.min_rank,
            "max_rank": cfg.max_rank,
        },
        "layers": rows,
    }
    with open(args.out_json, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Wrote: {args.out_json}")


if __name__ == "__main__":
    main()
