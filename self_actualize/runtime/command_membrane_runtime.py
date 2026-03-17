#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from self_actualize.runtime.command_spine_adapter import CommandMembraneService, read_json, utc_now


def _source_ids(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    rows = [part.strip() for part in raw.split(",") if part.strip()]
    return rows or None


def _print(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
        return
    if isinstance(payload, dict):
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
        return
    print(str(payload))


def _load_emit_seed(raw_source: str) -> tuple[Path, str]:
    candidate = Path(raw_source)
    if candidate.is_file() and candidate.suffix.lower() == ".json":
        try:
            payload = read_json(candidate, {})
        except json.JSONDecodeError:
            return candidate, "updated"
        if isinstance(payload, dict) and payload.get("full_path"):
            return Path(str(payload["full_path"])), str(payload.get("change_type") or "updated")
    return candidate, "updated"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the unified local swarm command membrane.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Refresh protocol artifacts and live ledgers.")
    build.add_argument("--json", action="store_true", dest="as_json")

    watch = subparsers.add_parser("watch", help="Watch the configured local swarm surfaces.")
    watch.add_argument("--source-ids", help="Comma-separated watched surface ids.")
    watch.add_argument("--once", action="store_true")
    watch.add_argument("--emit-only", action="store_true")
    watch.add_argument("--bootstrap-existing", action="store_true")
    watch.add_argument("--timeout-sec", type=int, default=0)
    watch.add_argument("--json", action="store_true", dest="as_json")

    emit = subparsers.add_parser("emit", help="Emit one event packet for a path or seed json.")
    emit.add_argument("event_source")
    emit.add_argument("--change-type", default="")
    emit.add_argument("--source-ids", help="Comma-separated watched surface ids.")
    emit.add_argument("--json", action="store_true", dest="as_json")

    route = subparsers.add_parser("route", help="Route one event through the local swarm.")
    route.add_argument("event_id")
    route.add_argument("--json", action="store_true", dest="as_json")

    claim = subparsers.add_parser("claim", help="Claim one routed event with first-lease semantics.")
    claim.add_argument("event_id")
    claim.add_argument("--ant-id")
    claim.add_argument("--role", default="worker")
    claim.add_argument("--lease-ms", type=int)
    claim.add_argument("--json", action="store_true", dest="as_json")

    reinforce = subparsers.add_parser("reinforce", help="Reinforce one completed route.")
    reinforce.add_argument("event_id")
    reinforce.add_argument("--path")
    reinforce.add_argument("--result", default="success")
    reinforce.add_argument("--latency-score", type=float)
    reinforce.add_argument("--json", action="store_true", dest="as_json")

    status = subparsers.add_parser("status", help="Show live swarm health across watched surfaces.")
    status.add_argument("--source-ids", help="Comma-separated watched surface ids.")
    status.add_argument("--json", action="store_true", dest="as_json")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = CommandMembraneService()

    if args.command == "build":
        protocol = service.ensure_protocol_artifacts()
        state = service.sync_public_surfaces()
        payload = {
            "protocol": protocol,
            "public_state": state,
            "live_manifest": read_json(service.config.live_manifest_path, {}),
        }
        _print(payload, args.as_json)
        return 0

    if args.command == "watch":
        payload = service.watch_command_folder(
            once=args.once,
            timeout_secs=args.timeout_sec,
            bootstrap_existing=args.bootstrap_existing,
            emit_only=args.emit_only,
            source_ids=_source_ids(args.source_ids),
        )
        _print(payload, args.as_json)
        return 0

    if args.command == "emit":
        event_path, fallback_change_type = _load_emit_seed(args.event_source)
        packet = service.emit_change(
            source_path=event_path,
            change_type=args.change_type or fallback_change_type,
            detected_ts=utc_now(),
            source_ids=_source_ids(args.source_ids),
        )
        payload = service.packet_to_summary(packet) if packet is not None else {"status": "duplicate_or_ignored"}
        _print(payload, args.as_json)
        return 0

    if args.command == "route":
        payload = service.route_event(args.event_id)
        _print(payload, args.as_json)
        return 0

    if args.command == "claim":
        payload = service.claim_event(
            args.event_id,
            ant_id=args.ant_id,
            role=args.role,
            lease_ms=args.lease_ms,
        )
        _print(payload, args.as_json)
        return 0

    if args.command == "reinforce":
        payload = service.reinforce_event(
            args.event_id,
            path=args.path,
            result=args.result,
            latency_score=args.latency_score,
        )
        _print(payload, args.as_json)
        return 0

    if args.command == "status":
        state = service.sync_public_surfaces()
        source_ids = _source_ids(args.source_ids)
        if source_ids is not None:
            state["source_health"] = service.source_health(source_ids).get("rows", [])
            state["watched_surface_count"] = len(state["source_health"])
        state["live_manifest"] = read_json(service.config.live_manifest_path, {})
        state["watched_surface_registry"] = service.watched_surface_registry(source_ids)
        _print(state, args.as_json)
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
