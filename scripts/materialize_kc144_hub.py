#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from athena_mcp.kc144_topology import manifest, validate_topology


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize the deterministic KC144 topological command hub crystal.")
    parser.add_argument("output", nargs="?", default="build/kc144-topological-command-hub.json")
    parser.add_argument("--without-edges", action="store_true", help="Write graph summaries instead of all generated edge records.")
    parser.add_argument("--validation-output", default="build/kc144-topological-command-hub.validation.json")
    args = parser.parse_args()

    output = Path(args.output)
    validation_output = Path(args.validation_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    validation_output.parent.mkdir(parents=True, exist_ok=True)

    crystal = manifest(include_edges=not args.without_edges)
    validation = validate_topology()
    if validation["status"] != "PASS":
        raise SystemExit("KC144 structural validation failed; crystal was not released")

    output.write_text(json.dumps(crystal, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    validation_output.write_text(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": "MATERIALIZED",
        "output": str(output),
        "manifest_digest": crystal["manifest_digest"],
        "validation_output": str(validation_output),
        "validation_receipt": validation["receipt_digest"],
        "promotion": "HOLD",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
