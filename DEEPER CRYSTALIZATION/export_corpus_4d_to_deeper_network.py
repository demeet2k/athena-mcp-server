#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import export_corpus_4d_to_deeper_network, resolve_path


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_REGISTRY = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json")
DEFAULT_DEEPER_NETWORK_ROOT = Path(
    "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the corpus 4D registry into the deeper-network overlay surfaces.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--deeper-network-root", default=str(DEFAULT_DEEPER_NETWORK_ROOT))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict[str, str]:
    workspace_root = Path(args.workspace_root).resolve()
    registry_path = resolve_path(workspace_root, args.registry)
    deeper_network_root = resolve_path(workspace_root, args.deeper_network_root)
    return export_corpus_4d_to_deeper_network(registry_path, deeper_network_root)


def main() -> int:
    result = run(parse_args())
    print(f"Overlay: {result['overlay_path']}")
    print(f"Appendix: {result['appendix_path']}")
    print(f"Transition map: {result['transition_map_path']}")
    print(f"Transition appendix: {result['transition_appendix_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
