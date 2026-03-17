#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import build_corpus_4d_registry, resolve_path, write_json


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_AUDIT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json")
DEFAULT_ARCHIVE_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json")
DEFAULT_REGISTRY = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the consolidated corpus 4D registry.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT))
    parser.add_argument("--archive-manifest", default=str(DEFAULT_ARCHIVE_MANIFEST))
    parser.add_argument("--registry-out", default=str(DEFAULT_REGISTRY))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    workspace_root = Path(args.workspace_root).resolve()
    manifest_path = resolve_path(workspace_root, args.manifest)
    audit_path = resolve_path(workspace_root, args.audit)
    archive_manifest_path = resolve_path(workspace_root, args.archive_manifest)
    registry_path = resolve_path(workspace_root, args.registry_out)
    registry = build_corpus_4d_registry(manifest_path, audit_path, archive_manifest_path)
    write_json(registry_path, registry)
    return registry


def main() -> int:
    registry = run(parse_args())
    print(f"Nodes: {registry['summary']['node_count']}")
    print(f"Docs gate: {registry['docs_gate_status']}")
    print(f"Duplicate groups: {registry['summary']['duplicate_group_count']}")
    print(f"AMBIG archive parents: {registry['summary']['ambig_archive_parent_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
