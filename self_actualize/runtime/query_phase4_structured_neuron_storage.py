from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from self_actualize.runtime.phase4_query_engine import fire, locate, neglect, promote, route


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registries() -> Dict[str, Any]:
    registries = {
        "docs_gate": load_json(SELF_ACTUALIZE_ROOT / "phase4_structured_neuron_storage_dashboard.json")["docs_gate"],
        "body_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_body_registry.json"),
        "kernel_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_kernel_registry.json"),
        "node_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_node_registry.json"),
        "pair_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_pair_registry.json"),
        "wave_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_wave_registry.json"),
        "shortcut_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_shortcut_registry.json"),
        "query_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_exploration_queries.json"),
        "neglect_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_neglect_signals.json"),
        "weave_registry": load_json(SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"),
        "weight_exchange": {
            **load_json(SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"),
            "authority_surface": str(SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"),
        },
        "commissure_ledger": {
            **load_json(SELF_ACTUALIZE_ROOT / "grand_central_commissure_ledger.json"),
            "authority_surface": str(SELF_ACTUALIZE_ROOT / "grand_central_commissure_ledger.json"),
        },
    }
    return registries


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the Phase 4 structured neuron storage surfaces.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    locate_parser = subparsers.add_parser("locate")
    locate_parser.add_argument("query")
    locate_parser.add_argument("--limit", type=int, default=8)

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("--source", required=True)
    route_parser.add_argument("--target", required=True)

    neglect_parser = subparsers.add_parser("neglect")
    neglect_parser.add_argument("--limit", type=int, default=8)

    fire_parser = subparsers.add_parser("fire")
    fire_parser.add_argument("objective")
    fire_parser.add_argument("--limit", type=int, default=8)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--candidate")

    args = parser.parse_args()
    registries = load_registries()

    if args.mode == "locate":
        result = locate(args.query, registries, limit=args.limit)
    elif args.mode == "route":
        result = route(args.source, args.target, registries)
    elif args.mode == "neglect":
        result = neglect(registries, limit=args.limit)
    elif args.mode == "fire":
        result = fire(args.objective, registries, limit=args.limit)
    else:
        result = promote(args.candidate, registries)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
