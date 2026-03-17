#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import audit_corpus_4d_rewrites, resolve_path, write_json


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_AUDIT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit sibling Mycelium Metro v4 rewrite outputs.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit-out", default=str(DEFAULT_AUDIT))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    workspace_root = Path(args.workspace_root).resolve()
    manifest_path = resolve_path(workspace_root, args.manifest)
    audit_path = resolve_path(workspace_root, args.audit_out)
    receipt = audit_corpus_4d_rewrites(workspace_root, manifest_path)
    write_json(audit_path, receipt)
    return receipt


def main() -> int:
    receipt = run(parse_args())
    print(f"Entries: {receipt['summary']['entry_count']}")
    print(f"Missing outputs: {receipt['summary']['missing_output_count']}")
    print(f"Orphan outputs: {receipt['summary']['orphan_output_count']}")
    print(f"Stale outputs: {receipt['summary']['stale_output_count']}")
    print(f"Contract failures: {receipt['summary']['contract_failure_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
