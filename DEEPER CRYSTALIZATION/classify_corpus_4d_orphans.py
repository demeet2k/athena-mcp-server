#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import classify_corpus_4d_orphans, resolve_path, write_json


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_AUDIT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json")
DEFAULT_OUTPUT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify the corpus-wide 4D orphan frontier.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    workspace_root = Path(args.workspace_root).resolve()
    manifest_path = resolve_path(workspace_root, args.manifest)
    audit_path = resolve_path(workspace_root, args.audit)
    output_path = resolve_path(workspace_root, args.output)
    receipt = classify_corpus_4d_orphans(workspace_root, manifest_path, audit_path, output_path)
    write_json(output_path, receipt)
    return receipt


def main() -> int:
    receipt = run(parse_args())
    print(f"Candidates: {receipt['summary']['candidate_count']}")
    print(f"True sibling orphans: {receipt['summary']['true_sibling_orphan_count']}")
    print(f"Standalone 4D: {receipt['summary']['standalone_4d_count']}")
    print(f"Historical 4D: {receipt['summary']['historical_4d_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
