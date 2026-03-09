"""
Export helper for Adaptive QP-GEMM -> TorchScript .pt artifact.

This script is intentionally "self-contained": it includes a small simulated 4-layer
vision-style MLP stack so you can export and validate end-to-end without wiring
in your production model first.

You can adapt `build_model()` to construct your actual vision model.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from dataclasses import asdict
from typing import Dict, Any

import torch
import torch.nn as nn

from qpgemm import QPGEMMConfig, optimize_vision_model, layer_report


class SimVisionStack(nn.Module):
    """
    Simulated "4-layer vision stack" (MLP-style) used for exporting and validation.

    Input:  (B, input_size)
    Output: (B, num_classes)
    """
    def __init__(self, input_size: int = 2048, hidden: int = 2048, num_layers: int = 4, num_classes: int = 1000):
        super().__init__()
        layers = []
        dim = input_size
        for i in range(num_layers - 1):
            layers.append(nn.Linear(dim, hidden))
            layers.append(nn.GELU())
            dim = hidden
        layers.append(nn.Linear(dim, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def build_model(args: argparse.Namespace) -> nn.Module:
    # Replace this with your production vision model constructor if desired.
    return SimVisionStack(
        input_size=args.input_size,
        hidden=args.hidden,
        num_layers=args.num_layers,
        num_classes=args.num_classes,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default="artifacts", help="Output directory for .pt and reports.")
    ap.add_argument("--input_size", type=int, default=2048)
    ap.add_argument("--hidden", type=int, default=2048)
    ap.add_argument("--num_layers", type=int, default=4)
    ap.add_argument("--num_classes", type=int, default=1000)

    ap.add_argument("--threshold", type=float, default=0.99, help="Spectral energy threshold.")
    ap.add_argument("--energy_mode", choices=["sv", "sv2"], default="sv")
    ap.add_argument("--min_gain", type=float, default=0.30, help="Min theoretical compute gain to apply lowrank.")
    ap.add_argument("--min_rank", type=int, default=1)
    ap.add_argument("--max_rank", type=int, default=None)

    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--freeze", action="store_true", help="Apply torch.jit.freeze before saving.")
    ap.add_argument("--save_baseline", action="store_true", help="Also export a baseline dense TorchScript model.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    device = torch.device(args.device)
    dtype_map = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    dtype = dtype_map[args.dtype]

    torch.manual_seed(0)

    # Build baseline model
    baseline = build_model(args).to(device=device, dtype=dtype).eval()

    # Build QP-GEMM optimized model
    cfg = QPGEMMConfig(
        energy_threshold=args.threshold,
        energy_mode=args.energy_mode,
        min_rank=args.min_rank,
        max_rank=args.max_rank,
        min_gain=args.min_gain,
    )
    optimized = optimize_vision_model(baseline, config=cfg, inplace=False, verbose=args.verbose).eval()

    # Dummy input to trace
    example = torch.randn(args.batch, args.input_size, device=device, dtype=dtype)

    with torch.inference_mode():
        ts_opt = torch.jit.trace(optimized, example)
        if args.freeze:
            # freeze requires eval() module
            ts_opt = torch.jit.freeze(ts_opt)

    # Attach metadata + layer report in extra files
    meta: Dict[str, Any] = {
        "framework": "Adaptive QP-GEMM Optimization Framework",
        "tuned_for": "Vision Models",
        "export": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "device": str(device),
            "dtype": args.dtype,
            "example_input_shape": [args.batch, args.input_size],
        },
        "qpgemm_config": asdict(cfg),
    }
    extra_files = {
        "qpgemm_meta.json": json.dumps(meta, indent=2).encode("utf-8"),
        "qpgemm_layer_report.json": json.dumps(layer_report(optimized), indent=2).encode("utf-8"),
    }

    opt_path = os.path.join(args.out_dir, "vision_model_qpgemm.pt")
    torch.jit.save(ts_opt, opt_path, _extra_files=extra_files)
    print(f"[OK] Saved optimized TorchScript: {opt_path}")

    # Save baseline if requested
    if args.save_baseline:
        with torch.inference_mode():
            ts_base = torch.jit.trace(baseline, example)
            if args.freeze:
                ts_base = torch.jit.freeze(ts_base)

        base_path = os.path.join(args.out_dir, "vision_model_dense.pt")
        torch.jit.save(ts_base, base_path)
        print(f"[OK] Saved baseline TorchScript: {base_path}")

    # Also write metadata as plain files for convenience
    with open(os.path.join(args.out_dir, "qpgemm_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    with open(os.path.join(args.out_dir, "qpgemm_layer_report.json"), "w") as f:
        json.dump(layer_report(optimized), f, indent=2)

    print("[Done]")


if __name__ == "__main__":
    main()
