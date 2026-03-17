#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reward_architecture import (
    apply_receipt_file,
    build_reward_architecture,
    reward_promotions,
    reward_status,
    score_quest_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reward Architecture v2 runtime CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build the shared reward architecture layer.")
    build_parser.add_argument("--json", action="store_true", dest="as_json")

    score_parser = subparsers.add_parser("score-quest", help="Score one quest payload JSON file.")
    score_parser.add_argument("payload")
    score_parser.add_argument("--json", action="store_true", dest="as_json")

    apply_parser = subparsers.add_parser("apply-receipt", help="Apply one reward receipt JSON file to the authoritative state.")
    apply_parser.add_argument("receipt")
    apply_parser.add_argument("--json", action="store_true", dest="as_json")

    mirror_parser = subparsers.add_parser("mirror", help="Alias of build for mirror and doctrine refresh.")
    mirror_parser.add_argument("--json", action="store_true", dest="as_json")

    promote_parser = subparsers.add_parser("promote", help="Show agents eligible for mini-hive promotion.")
    promote_parser.add_argument("--json", action="store_true", dest="as_json")

    status_parser = subparsers.add_parser("status", help="Show current reward runtime status.")
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    return parser.parse_args()


def emit(payload: object, as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, indent=2))
        return 0
    print(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    args = parse_args()

    if args.command in {"build", "mirror"}:
        return emit(build_reward_architecture(), args.as_json)
    if args.command == "score-quest":
        return emit(score_quest_file(Path(args.payload)), args.as_json)
    if args.command == "apply-receipt":
        return emit(apply_receipt_file(Path(args.receipt)), args.as_json)
    if args.command == "promote":
        return emit(reward_promotions(), args.as_json)
    if args.command == "status":
        return emit(reward_status(), args.as_json)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
