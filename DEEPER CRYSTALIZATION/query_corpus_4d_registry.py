#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from corpus_4d_fronts import load_json, query_registry_nodes, render_registry_markdown, resolve_path


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_REGISTRY = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the consolidated corpus 4D registry.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--ms")
    parser.add_argument("--path-prefix")
    parser.add_argument("--chapter")
    parser.add_argument("--appendix")
    parser.add_argument("--lens")
    parser.add_argument("--truth")
    parser.add_argument("--family")
    parser.add_argument("--duplicate-group")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--format", choices=["json", "md"], default="json")
    return parser.parse_args()


def run(args: argparse.Namespace) -> list[dict[str, object]]:
    workspace_root = Path(args.workspace_root).resolve()
    registry_path = resolve_path(workspace_root, args.registry)
    registry = load_json(registry_path)
    return query_registry_nodes(
        registry,
        ms=args.ms,
        path_prefix=args.path_prefix,
        chapter=args.chapter,
        appendix=args.appendix,
        lens=args.lens,
        truth=args.truth,
        family=args.family,
        duplicate_group=args.duplicate_group,
        limit=args.limit,
    )


def main() -> int:
    args = parse_args()
    nodes = run(args)
    if args.format == "md":
        text = render_registry_markdown(nodes)
    else:
        text = json.dumps({"count": len(nodes), "nodes": nodes}, indent=2, ensure_ascii=False) + "\n"
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
