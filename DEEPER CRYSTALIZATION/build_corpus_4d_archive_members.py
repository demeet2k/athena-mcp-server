#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import build_archive_member_manifest, resolve_path, write_json


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_ARCHIVE_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the archive-member manifest for ambiguous zip-backed 4D rewrites.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--archive-manifest-out", default=str(DEFAULT_ARCHIVE_MANIFEST))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    workspace_root = Path(args.workspace_root).resolve()
    manifest_path = resolve_path(workspace_root, args.manifest)
    output_path = resolve_path(workspace_root, args.archive_manifest_out)
    receipt = build_archive_member_manifest(workspace_root, manifest_path, output_path)
    write_json(output_path, receipt)
    return receipt


def main() -> int:
    receipt = run(parse_args())
    print(f"Zip parents: {receipt['summary']['zip_parent_count']}")
    print(f"Multi-candidate parents: {receipt['summary']['multi_candidate_parent_count']}")
    print(f"Member records: {receipt['summary']['member_record_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
