from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .command_spine_adapter import CommandMembraneConfig, CommandMembraneService
from .engine import SelfActualizeEngine


KNOWN_SUBCOMMANDS = {
    "watch",
    "watch-command-folder",
    "emit",
    "route",
    "claim",
    "commit",
    "reinforce",
    "metrics",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Athena runtime CLI.")
    subparsers = parser.add_subparsers(dest="command")

    watch_alias = subparsers.add_parser("watch", help="Watch a named runtime surface.")
    watch_alias.add_argument("surface", choices=["command"], help="Runtime surface to watch.")
    watch_alias.add_argument("--path", default="", help="Optional command surface override.")
    watch_alias.add_argument("--once", action="store_true", help="Return after the first emitted event.")
    watch_alias.add_argument("--timeout-secs", type=int, default=0, help="Optional timeout for the watcher session.")
    watch_alias.add_argument(
        "--bootstrap-existing",
        action="store_true",
        help="Emit events for the startup snapshot diff instead of seeding silently.",
    )
    watch_alias.add_argument("--emit-only", action="store_true", help="Emit packets without routing them.")
    watch_alias.add_argument("--json", action="store_true", help="Print JSON output.")

    watch = subparsers.add_parser("watch-command-folder", help="Watch GLOBAL COMMAND/ATHENA for command events.")
    watch.add_argument("--path", default="", help="Optional command surface override.")
    watch.add_argument("--once", action="store_true", help="Return after the first emitted event.")
    watch.add_argument("--timeout-secs", type=int, default=0, help="Optional timeout for the watcher session.")
    watch.add_argument(
        "--bootstrap-existing",
        action="store_true",
        help="Emit events for the startup snapshot diff instead of seeding silently.",
    )
    watch.add_argument("--emit-only", action="store_true", help="Emit packets without routing them.")
    watch.add_argument("--json", action="store_true", help="Print JSON output.")

    emit = subparsers.add_parser("emit", help="Create or replay a command event packet.")
    emit.add_argument("--path", required=True, help="Path inside the command surface.")
    emit.add_argument("--change-type", default="updated", help="created, updated, or deleted")
    emit.add_argument("--detected-ts", default="", help="Optional detection timestamp in ISO8601 UTC.")
    emit.add_argument("--parent-event-id", default="ROOT", help="Optional parent event id.")
    emit.add_argument("--json", action="store_true", help="Print JSON output.")

    route = subparsers.add_parser("route", help="Route a command event to top-k relevant ants.")
    route.add_argument("event_id", help="Command event id.")
    route.add_argument("--json", action="store_true", help="Print JSON output.")

    claim = subparsers.add_parser("claim", help="Acquire a first lease for a command event.")
    claim.add_argument("event_id", help="Command event id.")
    claim.add_argument("--ant-id", default="", help="Optional explicit worker ant id.")
    claim.add_argument("--role", default="worker", help="Claim role.")
    claim.add_argument("--lease-ms", type=int, default=0, help="Optional lease duration override.")
    claim.add_argument("--json", action="store_true", help="Print JSON output.")

    commit = subparsers.add_parser("commit", help="Commit a claimed command event.")
    commit.add_argument("event_id", help="Command event id.")
    commit.add_argument("--result", required=True, choices=["success", "partial", "fail"], help="Commit result.")
    commit.add_argument("--summary", default="", help="Optional commit summary.")
    commit.add_argument("--artifact", action="append", default=[], help="Linked artifact path.")
    commit.add_argument("--writeback", action="append", default=[], help="Linked writeback path.")
    commit.add_argument("--work-started-at", default="", help="Optional work-start timestamp.")
    commit.add_argument("--json", action="store_true", help="Print JSON output.")

    reinforce = subparsers.add_parser("reinforce", help="Reinforce a successful command path.")
    reinforce.add_argument("event_id", help="Command event id.")
    reinforce.add_argument("--path", default="", help="Optional explicit route path.")
    reinforce.add_argument("--result", default="success", choices=["success", "partial", "fail"], help="Route result.")
    reinforce.add_argument("--latency-score", type=float, default=0.90, help="Latency score from 0.0 to 1.0.")
    reinforce.add_argument("--json", action="store_true", help="Print JSON output.")

    metrics = subparsers.add_parser("metrics", help="Summarize command membrane latency and capillary metrics.")
    metrics.add_argument("--surface", default="command-folder", help="Surface name filter.")
    metrics.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)


def service_from_args(path_override: str = "") -> CommandMembraneService:
    if path_override:
        config = CommandMembraneConfig(command_surface_root=Path(path_override))
        return CommandMembraneService(config)
    return CommandMembraneService()


def emit_output(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    if isinstance(payload, dict):
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    print(payload)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or [])
    if not argv or argv[0] in {"-h", "--help"}:
        args = parse_args(argv)
    elif argv[0] not in KNOWN_SUBCOMMANDS:
        objective = " ".join(argv).strip()
        engine = SelfActualizeEngine()
        packet = engine.run(objective)
        print(engine.packet_to_json(packet))
        return 0
    else:
        args = parse_args(argv)

    if not args.command:
        raise SystemExit("No command provided.")

    service = service_from_args(getattr(args, "path", ""))
    if args.command == "watch":
        if args.surface != "command":
            raise ValueError(f"Unsupported watch surface: {args.surface}")
        payload = service.watch_command_folder(
            once=args.once,
            timeout_secs=args.timeout_secs,
            bootstrap_existing=args.bootstrap_existing,
            emit_only=args.emit_only,
        )
        emit_output(payload, args.json)
        return 0
    if args.command == "watch-command-folder":
        payload = service.watch_command_folder(
            once=args.once,
            timeout_secs=args.timeout_secs,
            bootstrap_existing=args.bootstrap_existing,
            emit_only=args.emit_only,
        )
        emit_output(payload, args.json)
        return 0
    if args.command == "emit":
        emit_path = Path(args.path)
        if not emit_path.is_absolute():
            emit_path = service.config.command_surface_root / emit_path
        packet = service.emit_change(
            source_path=emit_path,
            change_type=args.change_type,
            detected_ts=args.detected_ts or datetime.now(timezone.utc).isoformat(),
            parent_event_id=args.parent_event_id,
        )
        emit_output(service.packet_to_summary(packet) if packet else {"status": "deduped"}, args.json)
        return 0
    if args.command == "route":
        emit_output(service.route_event(args.event_id), args.json)
        return 0
    if args.command == "claim":
        emit_output(
            service.claim_event(
                args.event_id,
                ant_id=args.ant_id or None,
                role=args.role,
                lease_ms=args.lease_ms or None,
            ),
            args.json,
        )
        return 0
    if args.command == "commit":
        emit_output(
            service.commit_event(
                args.event_id,
                result=args.result,
                artifact_paths=args.artifact,
                writeback_paths=args.writeback,
                summary=args.summary,
                work_started_at=args.work_started_at or None,
            ),
            args.json,
        )
        return 0
    if args.command == "reinforce":
        emit_output(
            service.reinforce_event(
                args.event_id,
                path=args.path or None,
                result=args.result,
                latency_score=args.latency_score,
            ),
            args.json,
        )
        return 0
    if args.command == "metrics":
        emit_output(service.metrics(surface=args.surface), args.json)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
