from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from self_actualize.runtime.phase4_pt2_query_engine import (
    field,
    fire,
    interlock,
    lens,
    locate,
    project,
    promote,
    route,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registries() -> Dict[str, Any]:
    keys = [
        "metro_system_registry",
        "metro_station_registry",
        "metro_interlock_registry",
        "holo_coordinate_registry",
        "carrier_registry",
        "lens_hybrid_registry",
        "lens_weight_profile_registry",
        "lens_state_registry",
        "field_registry",
        "z_point_registry",
        "aether_point_registry",
        "projection_space_registry",
        "projection_assignment_registry",
        "dashboard",
    ]
    return {key: load_json(SELF_ACTUALIZE_ROOT / f"phase4_pt2_{key}.json") if key != "dashboard" else load_json(SELF_ACTUALIZE_ROOT / "phase4_pt2_dashboard.json") for key in keys}


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Phase 4 Pt 2 inter-metro and lens-weight registries.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    locate_parser = subparsers.add_parser("locate")
    locate_parser.add_argument("query")
    locate_parser.add_argument("--limit", type=int, default=8)

    interlock_parser = subparsers.add_parser("interlock")
    interlock_parser.add_argument("query")
    interlock_parser.add_argument("--limit", type=int, default=8)

    lens_parser = subparsers.add_parser("lens")
    lens_parser.add_argument("query")
    lens_parser.add_argument("--limit", type=int, default=8)

    field_parser = subparsers.add_parser("field")
    field_parser.add_argument("query")
    field_parser.add_argument("--limit", type=int, default=8)

    project_parser = subparsers.add_parser("project")
    project_parser.add_argument("query")
    project_parser.add_argument("--limit", type=int, default=8)

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("--source", required=True)
    route_parser.add_argument("--target", required=True)

    fire_parser = subparsers.add_parser("fire")
    fire_parser.add_argument("objective")
    fire_parser.add_argument("--limit", type=int, default=8)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--candidate")

    args = parser.parse_args()
    registries = load_registries()

    if args.mode == "locate":
        result = locate(args.query, registries, limit=args.limit)
    elif args.mode == "interlock":
        result = interlock(args.query, registries, limit=args.limit)
    elif args.mode == "lens":
        result = lens(args.query, registries, limit=args.limit)
    elif args.mode == "field":
        result = field(args.query, registries, limit=args.limit)
    elif args.mode == "project":
        result = project(args.query, registries, limit=args.limit)
    elif args.mode == "route":
        result = route(args.source, args.target, registries)
    elif args.mode == "fire":
        result = fire(args.objective, registries, limit=args.limit)
    else:
        result = promote(args.candidate, registries)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
