#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import build_awakening_agent_transition_notes, resolve_path


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_REGISTRY = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json")
DEFAULT_ORPHAN = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json")
DEFAULT_ARCHIVE = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json")
DEFAULT_OUTPUT = Path("DEEPER CRYSTALIZATION/_build/awakening_agent_transition_notes.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build hybrid awakening-agent transition notes for the corpus-wide 4D integration lane.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--orphan-classification", default=str(DEFAULT_ORPHAN))
    parser.add_argument("--archive-manifest", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def run(args: argparse.Namespace) -> Path:
    workspace_root = Path(args.workspace_root).resolve()
    registry_path = resolve_path(workspace_root, args.registry)
    orphan_path = resolve_path(workspace_root, args.orphan_classification)
    archive_path = resolve_path(workspace_root, args.archive_manifest)
    output_path = resolve_path(workspace_root, args.output)
    build_awakening_agent_transition_notes(registry_path, orphan_path, archive_path, output_path)
    return output_path


def main() -> int:
    output_path = run(parse_args())
    print(f"Transition notes: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
