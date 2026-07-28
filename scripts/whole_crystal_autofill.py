#!/usr/bin/env python3
"""Inspect the frozen KC144 Ω whole-crystal structural fixed point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.whole_crystal_autofill import (  # noqa: E402
    FrozenWholeCrystalAutofill,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--fixed-point", action="store_true")
    parser.add_argument("--defect-tensor", action="store_true")
    parser.add_argument("--gid", type=int)
    parser.add_argument("--octave", type=int, default=0)
    args = parser.parse_args()

    compiler = FrozenWholeCrystalAutofill.load()
    if args.gid is not None:
        result = compiler.station(args.gid, octave=args.octave)
    elif args.defect_tensor:
        result = compiler.defect_tensor()
    elif args.fixed_point:
        result = compiler.compile_fixed_point(octave=args.octave)
    else:
        result = compiler.status()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
