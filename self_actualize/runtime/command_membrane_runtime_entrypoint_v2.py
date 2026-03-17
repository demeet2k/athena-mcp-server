from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime import swarm_board
else:
    from . import swarm_board


ROOT = swarm_board.WORKSPACE_ROOT
GLOBAL_COMMAND_ROOT = swarm_board.COMMAND_FOLDER_ROOT
RUNTIME_STATE_PATH = swarm_board.COMMAND_RUNTIME_STATE_PATH
ROUTER_ID = "ROUTER-01"
ARCHIVIST_ID = "ARCHIVIST-01"
ACTIVE_PROTOCOL_VERSION = "V2"
COMMAND_POLICY_ID = "goal_fit+priority+gold_signal+bridge_signal+coord_proximity+freshness+joy_q"


def rel(path: Path | str) -> str:
    target = Path(path)
    try:
        return target.relative_to(ROOT).as_posix()
    except ValueError:
        return target.as_posix()


def read_json(path: Path, default: Any) -> Any:
    return swarm_board.read_json(path, default)


def write_json(path: Path, payload: Any) -> None:
    swarm_board.write_json(path, payload)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def active_protocol_defaults() -> dict[str, Any]:
    defaults_payload = swarm_board.command_protocol_defaults()
    routing = defaults_payload.get("routing_policy", {})
    return {
        "active_version": defaults_payload.get("active_version", ACTIVE_PROTOCOL_VERSION),
        "policy_id": routing.get("policy_id", COMMAND_POLICY_ID),
        "policy_expression": routing.get("policy_expression", COMMAND_POLICY_ID),
        "topk": int(routing.get("topk", 5)),
        "quorum": int(routing.get("quorum", 1)),
        "claim_mode": routing.get("claim_mode", "first-lease"),
    }


def detect_watcher_mode() -> str:
    return "event-driven" if os.name == "nt" else "polling"


def _resolve_command_path(source: str | Path) -> Path:
    source_path = Path(source)
    if source_path.is_absolute():
        return source_path
    if source_path.parts and source_path.parts[0] == "GLOBAL COMMAND":
        return (ROOT / source_path).resolve()
    return (GLOBAL_COMMAND_ROOT / source_path).resolve()


def build_change_record(source: str | Path, change_type: str) -> dict[str, Any]:
    source_path = _resolve_command_path(source)
    if source_path.exists():
        stat = source_path.stat()
        mtime_ns = stat.st_mtime_ns
        mtime_iso = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    else:
        mtime_ns = time.time_ns()
        mtime_iso = utc_now()
    try:
        relative_path = source_path.relative_to(ROOT).as_posix()
    except ValueError:
        relative_path = source_path.as_posix()
    kind = {
        "add": "added",
        "create": "added",
        "created": "added",
        "modify": "modified",
        "modified": "modified",
        "update": "modified",
        "updated": "modified",
        "rename": "modified",
        "renamed": "modified",
        "move": "modified",
        "moved": "modified",
        "delete": "removed",
        "deleted": "removed",
        "remove": "removed",
    }.get(change_type.lower(), "modified")
    return {
        "kind": kind,
        "relative_path": relative_path,
        "top_level": Path(relative_path).parts[0] if Path(relative_path).parts else "GLOBAL COMMAND",
        "mtime_ns": mtime_ns,
        "mtime_iso": mtime_iso,
    }


def _diff_for_change(change: dict[str, Any]) -> dict[str, Any]:
    kind = change["kind"]
    return {
        "added": 1 if kind == "added" else 0,
        "modified": 1 if kind == "modified" else 0,
        "removed": 1 if kind == "removed" else 0,
        "total": 1,
        "changes": [change],
    }


def _packet_by_id(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_json(swarm_board.COMMAND_PACKET_LOG_PATH, [])):
        if row.get("event_id") == event_id:
            return row
    return None


def _route_by_id(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_json(swarm_board.COMMAND_ROUTE_LOG_PATH, [])):
        if row.get("event_id") == event_id:
            payload = dict(row)
            if "policy" not in payload and "policy_id" in payload:
                payload["policy"] = payload["policy_id"]
            return payload
    return None


def _claim_by_event_id(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_json(swarm_board.COMMAND_LEASE_LOG_PATH, [])):
        if row.get("event_id") == event_id:
            return row
    return None


def _route_command_packet_v2(packet: dict[str, Any], topk: int | None = None) -> dict[str, Any]:
    route = dict(swarm_board.route_command_packet(packet))
    if topk is not None:
        route["topk"] = int(topk)
    route["policy"] = route.get("policy_id", COMMAND_POLICY_ID)
    return route


def build_event_packet(change: dict[str, Any], watcher_mode: str | None = None) -> tuple[dict[str, Any], float, float]:
    watcher_mode = watcher_mode or detect_watcher_mode()
    detected_at = datetime.now(timezone.utc)
    detection_started = time.perf_counter()
    packet = swarm_board.build_command_packet(
        _diff_for_change(change),
        watcher_mode,
        detected_at,
        watch_fallback=watcher_mode != "event-driven",
    )
    encode_done = time.perf_counter()
    return packet, round((encode_done - detection_started) * 1000.0, 4), 0.0


def rank_worker_candidates(packet: dict[str, Any], topk: int = 5) -> tuple[list[dict[str, Any]], float]:
    started = time.perf_counter()
    route = _route_command_packet_v2(packet, topk=topk)
    return route["candidate_targets"][:topk], round((time.perf_counter() - started) * 1000.0, 4)


def handle_emit(event_source: str, change_type: str, as_json: bool = False) -> dict[str, Any]:
    change = build_change_record(event_source, change_type)
    packet, detect_ms, encode_ms = build_event_packet(change, watcher_mode=detect_watcher_mode())
    packet["active_protocol_version"] = ACTIVE_PROTOCOL_VERSION
    packet["detection_latency_ms"] = detect_ms
    packet["encode_latency_ms"] = encode_ms
    swarm_board.append_limited_json_list(swarm_board.COMMAND_PACKET_LOG_PATH, packet)
    swarm_board.append_ndjson(
        swarm_board.COMMAND_EVT_FEED_PATH,
        {
            "event_id": packet["event_id"],
            "event_type": "EVT",
            "ts_utc": packet["earth_ts_utc"],
            "actor_id": packet["detected_by"],
            "role_class": "Scout",
            "relative_path": packet["relative_path"],
            "goal": packet["goal"],
            "route_class": packet["route_class"],
            "truth_class": "NEAR",
            "witness_ptr": packet["witness_ptr"],
            "replay_ptr": packet["replay_ptr"],
        },
    )
    runtime_state = read_json(RUNTIME_STATE_PATH, {})
    runtime_state.update(
        {
            "generated_at": utc_now(),
            "docs_gate_status": swarm_board.docs_gate_status()["status"],
            "command_folder_root": rel(GLOBAL_COMMAND_ROOT),
            "watcher_mode": packet["detection_mode"],
            "last_event_id": packet["event_id"],
            "last_event": packet,
        }
    )
    write_json(RUNTIME_STATE_PATH, runtime_state)
    swarm_board.refresh_board()
    payload = {"packet": packet, "detect_ms": detect_ms, "encode_ms": encode_ms}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Emitted {packet['event_id']} for {packet['relative_path']}")
    return payload


def handle_route(event_id: str, topk: int, as_json: bool = False) -> dict[str, Any]:
    packet = _packet_by_id(event_id)
    if packet is None:
        raise ValueError(f"Unknown command event: {event_id}")
    route = _route_command_packet_v2(packet, topk=topk)
    swarm_board.append_limited_json_list(swarm_board.COMMAND_ROUTE_LOG_PATH, route)
    swarm_board.append_ndjson(
        swarm_board.COMMAND_RTE_FEED_PATH,
        {
            "event_id": route["event_id"],
            "event_type": "RTE",
            "ts_utc": route["generated_at"],
            "actor_id": ROUTER_ID,
            "role_class": "Router",
            "policy": route["policy_id"],
            "selected_targets": route["selected_targets"],
            "route_path": route["route_path"],
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
        },
    )
    if as_json:
        print(json.dumps(route, indent=2))
    else:
        print(f"Routed {event_id} via {route['route_path']}")
    return route


def handle_claim(event_id: str, ant_id: str | None, lease_ms: int, as_json: bool = False) -> dict[str, Any]:
    packet = _packet_by_id(event_id)
    if packet is None:
        raise ValueError(f"Unknown command event: {event_id}")
    route = _route_by_id(event_id) or handle_route(
        event_id,
        int(active_protocol_defaults().get("topk", 5)),
        True,
    )
    worker_id = ant_id or route["worker_choice"]
    claimed_at = datetime.now(timezone.utc)
    expires_at = (claimed_at + timedelta(milliseconds=lease_ms)).isoformat()
    lease = {
        "claim_id": f"CLM-{event_id}",
        "event_id": event_id,
        "ant_id": worker_id,
        "role": "worker",
        "lease_ms": lease_ms,
        "claimed_at": claimed_at.isoformat(),
        "expires_at": expires_at,
        "status": "leased",
        "claim_status": "leased",
        "role_class": "Worker",
        "claim_mode": "first-lease",
        "claimed_at_utc": claimed_at.isoformat(),
        "expires_at_utc": expires_at,
        "front_ref": packet.get("front_ref", "GLOBAL COMMAND"),
        "seed_mode": packet.get("seed_mode", ""),
        "dual_reference": packet.get("dual_reference", ""),
        "claim_rank": 1,
        "lease_expires_at": expires_at,
        "claim_source_event": event_id,
        "route_path": route["route_path"],
        "route_class": packet["route_class"],
    }
    route["worker_choice"] = worker_id
    claim_payload = swarm_board.command_claim_payload(packet, route, lease)
    swarm_board.append_limited_json_list(swarm_board.COMMAND_LEASE_LOG_PATH, lease)
    swarm_board.append_ndjson(
        swarm_board.COMMAND_CLM_FEED_PATH,
        {
            "event_id": event_id,
            "event_type": "CLM",
            "ts_utc": lease["claimed_at_utc"],
            "actor_id": worker_id,
            "role_class": "Worker",
            "claim_id": claim_payload["claim_id"],
            "claim_mode": lease["claim_mode"],
            "lease_ms": lease_ms,
            "expires_at_utc": expires_at,
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
        },
    )
    swarm_board.refresh_board()
    payload = {"route": route, "lease": lease, "claim": claim_payload}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Claimed {event_id} with {worker_id} for {lease_ms}ms")
    return payload


def handle_commit(event_id: str, result: str = "success", as_json: bool = False) -> dict[str, Any]:
    commit_started = time.perf_counter()
    packet = _packet_by_id(event_id)
    route = _route_by_id(event_id)
    lease = _claim_by_event_id(event_id)
    if packet is None or route is None or lease is None:
        raise ValueError(f"Commit requires packet, route, and claim for {event_id}")
    committed_at = utc_now()
    committed_at_dt = swarm_board.parse_utc(committed_at)
    claimed_at = swarm_board.parse_utc(lease.get("claimed_at_utc") or lease.get("claimed_at"))
    detected_at = swarm_board.parse_utc(packet.get("earth_ts_utc"))
    routed_at = swarm_board.parse_utc(route.get("generated_at"))
    detection_latency_ms = round(float(packet.get("detection_latency_ms", 0.0)), 3)
    encode_latency_ms = round(float(packet.get("encode_latency_ms", 0.0)), 3)
    route_latency_ms = 0.0
    if routed_at is not None and detected_at is not None:
        raw_route_window_ms = max(0.0, (routed_at - detected_at).total_seconds() * 1000.0)
        route_latency_ms = round(max(0.0, raw_route_window_ms - encode_latency_ms), 3)
    claim_latency_ms = 0.0
    if claimed_at is not None and routed_at is not None:
        claim_latency_ms = round(max(0.0, (claimed_at - routed_at).total_seconds() * 1000.0), 3)
    awareness_latency_ms = round(encode_latency_ms + route_latency_ms, 3)
    resolution_latency_ms = 0.0
    if committed_at_dt is not None and claimed_at is not None:
        resolution_latency_ms = round(max(0.0, (committed_at_dt - claimed_at).total_seconds() * 1000.0), 3)
    commit_latency_ms = round((time.perf_counter() - commit_started) * 1000.0, 3)
    t_sugar_ms = round(detection_latency_ms + encode_latency_ms + route_latency_ms + claim_latency_ms + commit_latency_ms, 3)
    payload = {
        "event_id": event_id,
        "claim_ant_id": lease["ant_id"],
        "result": result,
        "route_path": route["route_path"],
        "detection_latency_ms": detection_latency_ms,
        "swarm_awareness_latency_ms": awareness_latency_ms,
        "claim_latency_ms": claim_latency_ms,
        "resolution_latency_ms": resolution_latency_ms,
        "capillary_score": 0.0,
        "liminal_distance": packet.get("liminal_delta", 0.0),
        "liminal_velocity": packet.get("liminal_velocity", 0.0),
        "encode_latency_ms": encode_latency_ms,
        "route_latency_ms": route_latency_ms,
        "integration_gain": packet.get("priority", 0.0),
        "compression_gain": max(0.0, 1.0 - float(packet.get("priority", 0.0))),
        "unresolved_followups": [],
        "replay_ptr": packet["replay_ptr"],
        "claim_id": lease["claim_id"],
        "commit_latency_ms": commit_latency_ms,
        "t_sugar_ms": t_sugar_ms,
        "committed_at": committed_at,
        "front_ref": packet.get("front_ref", "GLOBAL COMMAND"),
    }
    swarm_board.append_limited_json_list(swarm_board.COMMAND_ARCHIVIST_LOG_PATH, payload)
    swarm_board.append_limited_json_list(
        swarm_board.COMMAND_LATENCY_LOG_PATH,
        {
            "event_id": event_id,
            "detection_latency_ms": detection_latency_ms,
            "swarm_awareness_latency_ms": awareness_latency_ms,
            "claim_latency_ms": claim_latency_ms,
            "resolution_latency_ms": resolution_latency_ms,
            "commit_latency_ms": commit_latency_ms,
            "capillary_score": 0.0,
            "t_sugar_ms": t_sugar_ms,
            "liminal_distance": payload["liminal_distance"],
            "liminal_velocity": payload["liminal_velocity"],
            "encode_latency_ms": encode_latency_ms,
            "route_latency_ms": route_latency_ms,
        },
    )
    swarm_board.append_ndjson(
        swarm_board.COMMAND_CMT_FEED_PATH,
        {
            "event_id": event_id,
            "event_type": "CMT",
            "ts_utc": committed_at,
            "actor_id": lease["ant_id"],
            "role_class": "Worker",
            "result": result,
            "route_path": route["route_path"],
            "t_sugar_ms": t_sugar_ms,
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
        },
    )
    runtime_state = read_json(RUNTIME_STATE_PATH, {})
    runtime_state.update({"generated_at": utc_now(), "last_commit_event_id": event_id, "last_commit": payload})
    write_json(RUNTIME_STATE_PATH, runtime_state)
    swarm_board.refresh_board()
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Committed {event_id} as {result}")
    return payload


def handle_reinforce(event_id: str, result: str, latency_score: float, noise_penalty: float, as_json: bool = False) -> dict[str, Any]:
    packet = _packet_by_id(event_id)
    route = _route_by_id(event_id)
    if packet is None or route is None:
        raise ValueError(f"Reinforce requires packet and route for {event_id}")
    edge = swarm_board.update_command_capillary(
        route["route_path"],
        latency_score,
        result,
        event_id=event_id,
        latency_ms=round(max(0.0, (1.0 - latency_score) * 5000.0), 3),
        noise_penalty=noise_penalty,
    )
    payload = {
        "event_id": event_id,
        "path": route["route_path"],
        "result": result,
        "latency_score": latency_score,
        "noise_penalty": noise_penalty,
        "capillary_score": edge["path_score"],
        "path_class": edge["path_class"],
        "reinforced_at": utc_now(),
    }
    swarm_board.append_ndjson(
        swarm_board.COMMAND_RIN_FEED_PATH,
        {
            "event_id": event_id,
            "event_type": "RIN",
            "ts_utc": payload["reinforced_at"],
            "actor_id": ARCHIVIST_ID,
            "role_class": "Archivist",
            "route_path": route["route_path"],
            "capillary_score": edge["path_score"],
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
        },
    )
    runtime_state = read_json(RUNTIME_STATE_PATH, {})
    runtime_state.update({"generated_at": utc_now(), "last_reinforce_event_id": event_id, "last_reinforcement": payload})
    write_json(RUNTIME_STATE_PATH, runtime_state)
    swarm_board.refresh_board()
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Reinforced {event_id} -> {edge['path_class']} ({edge['path_score']})")
    return payload


def handle_status(as_json: bool = False) -> dict[str, Any]:
    payload = {
        "generated_at": utc_now(),
        "docs_gate": swarm_board.docs_gate_status(),
        "command_root": rel(GLOBAL_COMMAND_ROOT),
        "watcher_mode": read_json(RUNTIME_STATE_PATH, {}).get("watcher_mode", detect_watcher_mode()),
        "active_protocol_version": ACTIVE_PROTOCOL_VERSION,
        "active_leases": swarm_board.command_active_leases(),
        "recent_events": swarm_board.command_packet_logs(limit=10),
        "recent_latency": swarm_board.command_latency_logs(limit=10),
        "top_capillaries": swarm_board.command_capillary_summary(),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"COMMAND status: docs={payload['docs_gate']['status']} "
            f"watcher={payload['watcher_mode']} "
            f"protocol={payload['active_protocol_version']} "
            f"leases={len(payload['active_leases'])} "
            f"capillaries={len(payload['top_capillaries'])}"
        )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dedicated COMMAND membrane runtime entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Regenerate COMMAND protocol artifacts and verify them.")
    build.add_argument("--json", action="store_true", dest="as_json")

    watch = subparsers.add_parser("watch", help="Watch GLOBAL COMMAND and process event-driven changes.")
    watch.add_argument("--interval", type=float, default=2.0)
    watch.add_argument("--max-cycles", type=int, default=0)

    emit = subparsers.add_parser("emit", help="Emit a manual COMMAND packet for an existing path.")
    emit.add_argument("event_source")
    emit.add_argument("--change-type", default="modified")
    emit.add_argument("--json", action="store_true", dest="as_json")

    route = subparsers.add_parser("route", help="Route an existing COMMAND packet.")
    route.add_argument("event_id")
    route.add_argument("--topk", type=int, default=5)
    route.add_argument("--json", action="store_true", dest="as_json")

    claim = subparsers.add_parser("claim", help="Claim a routed COMMAND packet.")
    claim.add_argument("event_id")
    claim.add_argument("--ant-id")
    claim.add_argument("--lease-ms", type=int, default=1200)
    claim.add_argument("--json", action="store_true", dest="as_json")

    commit = subparsers.add_parser("commit", help="Commit a claimed COMMAND packet.")
    commit.add_argument("event_id")
    commit.add_argument("--result", default="success")
    commit.add_argument("--json", action="store_true", dest="as_json")

    reinforce = subparsers.add_parser("reinforce", help="Reinforce an existing COMMAND route.")
    reinforce.add_argument("event_id")
    reinforce.add_argument("--result", default="success")
    reinforce.add_argument("--latency-score", type=float, default=0.9)
    reinforce.add_argument("--noise-penalty", type=float, default=0.0)
    reinforce.add_argument("--json", action="store_true", dest="as_json")

    status = subparsers.add_parser("status", help="Show COMMAND runtime status.")
    status.add_argument("--json", action="store_true", dest="as_json")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "build":
        if __package__ in {None, ""}:
            from self_actualize.runtime import derive_command_membrane_protocol_v2 as command_protocol_derive
            from self_actualize.runtime import verify_command_membrane_protocol_runtime_v2 as command_protocol_verify
        else:
            from . import derive_command_membrane_protocol_v2 as command_protocol_derive
            from . import verify_command_membrane_protocol_runtime_v2 as command_protocol_verify
        swarm_board.refresh_board()
        manifest = command_protocol_derive.derive_command_membrane_protocol_v2()
        verification = command_protocol_verify.verify_command_membrane_protocol_runtime_v2()
        payload = {"manifest": manifest, "verification": verification}
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"COMMAND build complete: policy={manifest['routing_policy']['policy_id']} "
                f"truth={verification['truth']} docs={manifest['docs_gate']['state']}"
            )
        return 0
    if args.command == "watch":
        return swarm_board.command_watch_command_folder(interval=args.interval, max_cycles=args.max_cycles, mode="auto")
    if args.command == "emit":
        handle_emit(args.event_source, args.change_type, args.as_json)
        return 0
    if args.command == "route":
        handle_route(args.event_id, args.topk, args.as_json)
        return 0
    if args.command == "claim":
        handle_claim(args.event_id, args.ant_id, args.lease_ms, args.as_json)
        return 0
    if args.command == "commit":
        handle_commit(args.event_id, args.result, args.as_json)
        return 0
    if args.command == "reinforce":
        handle_reinforce(args.event_id, args.result, args.latency_score, args.noise_penalty, args.as_json)
        return 0
    if args.command == "status":
        handle_status(args.as_json)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
