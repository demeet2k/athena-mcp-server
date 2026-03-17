from __future__ import annotations

import argparse
import json

from self_actualize.runtime.hemisphere_navigator_query_engine import SEARCH_FILTER_TO_FACET
from self_actualize.runtime.hemisphere_observatory_support import (
    facet,
    load_observatory_registries,
    page,
    record,
    search,
)


def add_search_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query", default="")
    parser.add_argument("--hemisphere")
    parser.add_argument("--family")
    parser.add_argument("--anchor")
    parser.add_argument("--system")
    parser.add_argument("--lens")
    parser.add_argument("--field")
    parser.add_argument("--zpoint")
    parser.add_argument("--space")
    parser.add_argument("--tract")
    parser.add_argument("--route-role", dest="route_role")
    parser.add_argument("--route-mode", dest="route_mode")
    parser.add_argument("--proof-state", dest="proof_state")
    parser.add_argument("--top-level", dest="top_level")


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief the top Myth/MATH observatory layer.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("query", nargs="?", default="")
    record_parser.add_argument("--record-id", dest="record_id", default="")
    record_parser.add_argument("--path", default="")
    record_parser.add_argument("--title", default="")
    record_parser.add_argument("--expanded", action="store_true")

    search_parser = subparsers.add_parser("search")
    add_search_filters(search_parser)
    search_parser.add_argument("--expanded", action="store_true")

    facet_parser = subparsers.add_parser("facet")
    facet_parser.add_argument("--system")
    facet_parser.add_argument("--family")
    facet_parser.add_argument("--anchor")
    facet_parser.add_argument("--hemisphere")
    facet_parser.add_argument("--expanded", action="store_true")

    page_parser = subparsers.add_parser("page")
    page_parser.add_argument("--page-id", dest="page_id", required=True)
    page_parser.add_argument("--expanded", action="store_true")

    args = parser.parse_args()
    registries = load_observatory_registries()

    if args.mode == "record":
        if not any([args.record_id, args.path, args.title, args.query]):
            parser.error("record requires --record-id, --path, --title, or a query string")
        result = record(
            registries,
            record_id=args.record_id,
            path=args.path,
            title=args.title,
            query_text=args.query,
            expanded=args.expanded,
        )
    elif args.mode == "search":
        filters = {
            key: value
            for key, value in {
                "hemisphere": args.hemisphere,
                "family": args.family,
                "anchor": args.anchor,
                "system": args.system,
                "lens": args.lens,
                "field": args.field,
                "zpoint": args.zpoint,
                "space": args.space,
                "tract": args.tract,
                "route_role": args.route_role,
                "route_mode": args.route_mode,
                "proof_state": args.proof_state,
                "top_level": args.top_level,
            }.items()
            if value
        }
        result = search(
            args.query,
            registries,
            filters=filters,
            expanded=args.expanded,
        )
    elif args.mode == "facet":
        selected = [
            (SEARCH_FILTER_TO_FACET["system"], args.system),
            (SEARCH_FILTER_TO_FACET["family"], args.family),
            (SEARCH_FILTER_TO_FACET["anchor"], args.anchor),
            (SEARCH_FILTER_TO_FACET["hemisphere"], args.hemisphere),
        ]
        chosen = [(facet_name, value) for facet_name, value in selected if value]
        if len(chosen) != 1:
            parser.error("facet requires exactly one facet selector")
        facet_name, facet_value = chosen[0]
        result = facet(
            registries,
            facet_name=facet_name,
            facet_value=facet_value,
            expanded=args.expanded,
        )
    else:
        result = page(
            registries,
            page_id=args.page_id,
            expanded=args.expanded,
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
