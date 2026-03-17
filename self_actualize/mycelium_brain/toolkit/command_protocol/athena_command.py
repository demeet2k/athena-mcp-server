from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from command_protocol.board_materializer import sync_command_boards
    from command_protocol.capillary_memory import load_memory, reinforce_edge
    from command_protocol.claim_manager import claim_event
    from command_protocol.command_packet import build_packet
    from command_protocol.ledger_writer import (
        append_jsonl,
        blocked_docs_receipt_path,
        claim_ledger_path,
        event_ledger_path,
        front_memory_path,
        hall_fronts_path,
        install_receipt_path,
        latency_receipt_path,
        promotion_receipts_path,
        read_json,
        read_jsonl,
        route_receipts_path,
        temple_fronts_path,
        write_json,
    )
    from command_protocol.liminal_coord import build_coord12, earth_timestamp, load_config, make_lookup_addr
    from command_protocol.quest_promotion import promote_event
    from command_protocol.route_engine import route_packet
    from command_protocol.watch_command_folder import WatchEvent, watch_loop
else:
    from .board_materializer import sync_command_boards
    from .capillary_memory import load_memory, reinforce_edge
    from .claim_manager import claim_event
    from .command_packet import build_packet
    from .ledger_writer import (
        append_jsonl,
        blocked_docs_receipt_path,
        claim_ledger_path,
        event_ledger_path,
        front_memory_path,
        hall_fronts_path,
        install_receipt_path,
        latency_receipt_path,
        promotion_receipts_path,
        read_json,
        read_jsonl,
        route_receipts_path,
        temple_fronts_path,
        write_json,
    )
    from .liminal_coord import build_coord12, earth_timestamp, load_config, make_lookup_addr
    from .quest_promotion import promote_event
    from .route_engine import route_packet
    from .watch_command_folder import WatchEvent, watch_loop


def _load_event_record(event_id: str) -> dict[str, Any]:
    for row in reversed(read_jsonl(event_ledger_path())):
        if row["packet"]["event_id"] == event_id:
            return row
    raise KeyError(f"unknown event_id: {event_id}")


def _queue_pressure() -> float:
    claims = read_jsonl(claim_ledger_path())
    routes = read_jsonl(route_receipts_path())
    active_claims = sum(1 for row in claims if row.get("status") == "claimed")
    return min(1.0, (active_claims + len(routes) * 0.1) / 20.0)


def _classify_lookup(source_path: str) -> tuple[str, str, str, str, str]:
    lowered = source_path.lower()
    if "temple" in lowered:
        return "Z0", "Organ-4", "Current-2", "seed-law", "OK"
    if "guild" in lowered or "quest" in lowered or "board" in lowered:
        return "Z3", "Organ-4", "Current-4", "quest-route", "NEAR"
    if lowered.endswith((".py", ".rs", ".toml", ".json")):
        return "Z1", "Organ-2", "Current-2", "worker-runtime", "NEAR"
    if any(s in lowered for s in ["witness", "receipt", "replay"]):
        return "Z0", "Organ-3", "Current-3", "witness-closure", "OK"
    if "aether" in lowered or "sky" in lowered:
        return "Z4", "Organ-5", "Current-4", "aether-frontier", "AMBIG"
    return "Z2", "Organ-1", "Current-1", "archive-intake", "NEAR"


def emit_event_record(
    *,
    ant_id: str,
    source_path: str,
    event_type: str,
    change: str,
    priority: float = 1.0,
    confidence: float = 0.98,
    watch_fallback: bool = False,
) -> dict[str, Any]:
    detected_at = datetime.now(tz=UTC)
    coord12, liminal_ts = build_coord12(
        event_type=event_type,
        source_path=source_path,
        priority=priority,
        confidence=confidence,
        queue_pressure=_queue_pressure(),
        watch_fallback=watch_fallback,
    )
    zero_class, organ_class, current, phase_role, witness_class = _classify_lookup(source_path)
    event_id = f"EVT-{datetime.now(tz=UTC).strftime('%Y%m%d-%H%M%S-%f')}"
    lookup = make_lookup_addr(
        node_id=Path(source_path).name or "GLOBAL_COMMAND_NODE",
        liminal_gps=coord12,
        zero_class=zero_class,
        organ_class=organ_class,
        current=current,
        phase_role=phase_role,
        witness_class=witness_class,
    )
    packet = build_packet(
        event_id=event_id,
        ant_id=ant_id,
        source_path=source_path,
        event_type=event_type,
        change=change,
        earth_ts=earth_timestamp(),
        liminal_ts=liminal_ts,
        coord12=coord12,
        lookup_addr=lookup,
        priority=priority,
        confidence=confidence,
        watch_fallback=watch_fallback,
    )
    record = packet.to_record()
    record["detected_at"] = detected_at.isoformat()
    record["encoded_at"] = datetime.now(tz=UTC).isoformat()
    append_jsonl(event_ledger_path(), record)
    return record


def route_event_record(event_id: str, topk: int = 5, quorum: int = 1) -> dict[str, Any]:
    return route_packet(_load_event_record(event_id), topk=topk, quorum=quorum)


def reinforce_route(
    event_id: str,
    path: str,
    result: str,
    latency_score: float,
    duplicate_noise: float = 0.0,
) -> dict[str, Any]:
    hops = path.split(">")
    updates = []
    usefulness = 1.0 if result == "success" else 0.3
    latency_penalty = max(0.0, min(1.0, 1.0 - latency_score))
    for src, dst in zip(hops, hops[1:]):
        updates.append(
            reinforce_edge(
                src=src,
                dst=dst,
                usefulness=usefulness,
                frequency_boost=1.0 if result == "success" else 0.2,
                latency_penalty=latency_penalty,
                noise_penalty=duplicate_noise,
            )
        )
    reinforced_at = datetime.now(tz=UTC)
    event_record = _load_event_record(event_id)
    route_receipts = [row for row in read_jsonl(route_receipts_path()) if row.get("event_id") == event_id and row.get("receipt_type") == "route_decision"]
    route_receipt = route_receipts[-1] if route_receipts else None
    claim_rows = [row for row in read_jsonl(claim_ledger_path()) if row.get("event_id") == event_id and row.get("status") == "claimed"]
    claim_row = claim_rows[-1] if claim_rows else None
    detected_at = datetime.fromisoformat(event_record.get("detected_at", event_record["packet"]["earth_ts"]))
    encoded_at = datetime.fromisoformat(event_record.get("encoded_at", event_record["packet"]["earth_ts"]))
    routed_at = datetime.fromisoformat(route_receipt["routed_at"]) if route_receipt else encoded_at
    claimed_at = datetime.fromisoformat(claim_row["claimed_at"]) if claim_row else routed_at
    latency_receipt = {
        "receipt_type": "latency_receipt",
        "event_id": event_id,
        "detect_ms": round(max(0.0, (detected_at - detected_at).total_seconds() * 1000), 3),
        "encode_ms": round(max(0.0, (encoded_at - detected_at).total_seconds() * 1000), 3),
        "route_ms": round(max(0.0, (routed_at - encoded_at).total_seconds() * 1000), 3),
        "claim_ms": round(max(0.0, (claimed_at - routed_at).total_seconds() * 1000), 3),
        "resolve_ms": round(max(0.0, (reinforced_at - claimed_at).total_seconds() * 1000), 3),
        "capillary_score": round(sum(update["Strength"] for update in updates) / len(updates), 6) if updates else 0.0,
        "verdict": "OK" if result == "success" else "NEAR",
        "path": path,
        "result": result,
        "latency_score": latency_score,
        "capillary_updates": updates,
        "reinforced_at": reinforced_at.isoformat(),
    }
    append_jsonl(route_receipts_path(), latency_receipt)
    return latency_receipt


def _status() -> dict[str, Any]:
    config = load_config()
    events = read_jsonl(event_ledger_path())
    claims = read_jsonl(claim_ledger_path())
    routes = read_jsonl(route_receipts_path())
    promotions = read_jsonl(promotion_receipts_path())
    return {
        "watch_root": config.watch_root,
        "docs_gate": "BLOCKED",
        "event_count": len(events),
        "claim_count": len(claims),
        "route_receipt_count": len(routes),
        "promotion_receipt_count": len(promotions),
        "temple_front_count": len(read_jsonl(temple_fronts_path())),
        "hall_front_count": len(read_jsonl(hall_fronts_path())),
        "active_front_keys": len(read_json(front_memory_path(), {"active_fronts": {}}).get("active_fronts", {})),
        "last_event": events[-1] if events else None,
        "latency_targets": read_json(latency_receipt_path(), {}),
        "capillary_edges": len(load_memory()["edges"]),
    }


def _write_install_receipts() -> None:
    config = load_config()
    install_receipt_path().write_text(
        "\n".join(
            [
                "# COMMAND Protocol Install Receipt",
                "",
                "- protocol: `COMMAND Protocol v1`",
                f"- watch root: `{config.watch_root}`",
                "- mode: event-driven watcher plus CLI",
                "- live Docs gate: `BLOCKED`",
                "- note: local-witness grounded until OAuth credentials exist",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    blocked_docs_receipt_path().write_text(
        "\n".join(
            [
                "# BLOCKED DOCS Boundary Receipt",
                "",
                "- state: `BLOCKED`",
                "- missing: `Trading Bot/credentials.json`",
                "- missing: `Trading Bot/token.json`",
                "- consequence: command membrane remains local-witness grounded",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(
        latency_receipt_path(),
        {
            "DetectionLatencyMsTarget": 250,
            "PacketEncodeLatencyMsTarget": 100,
            "RouteLatencyMsTarget": 250,
            "ClaimLeaseMsTarget": 1200,
            "SwarmAwarenessMsTarget": 2000,
        },
    )


def _handle_watch_event(event: WatchEvent) -> None:
    record = emit_event_record(
        ant_id="SCOUT-01",
        source_path=event.source_path,
        event_type=event.event_type,
        change=f"{event.event_type} under GLOBAL COMMAND",
        watch_fallback=event.watch_fallback,
    )
    route_event_record(record["packet"]["event_id"])


def _auto_promote_if_claimed(claim_receipt: dict[str, Any]) -> dict[str, Any] | None:
    if claim_receipt.get("status") != "claimed":
        return None
    promotion = promote_event(claim_receipt["event_id"])
    sync = sync_command_boards()
    return {"promotion": promotion, "sync": sync}


def main() -> None:
    parser = argparse.ArgumentParser(prog="athena_command")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("watch")

    emit_parser = subparsers.add_parser("emit")
    emit_parser.add_argument("--ant-id", required=True)
    emit_parser.add_argument("--source-path", required=True)
    emit_parser.add_argument("--event-type", required=True, choices=["create", "modify", "move", "delete"])
    emit_parser.add_argument("--change", required=True)
    emit_parser.add_argument("--priority", type=float, default=1.0)
    emit_parser.add_argument("--confidence", type=float, default=0.98)

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("event_id")
    route_parser.add_argument("--topk", type=int, default=5)
    route_parser.add_argument("--quorum", type=int, default=1)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("event_id")
    claim_parser.add_argument("--ant-id", required=True)
    claim_parser.add_argument("--role", default="worker")
    claim_parser.add_argument("--lease-ms", type=int, default=1200)

    reinforce_parser = subparsers.add_parser("reinforce")
    reinforce_parser.add_argument("event_id")
    reinforce_parser.add_argument("--path", required=True)
    reinforce_parser.add_argument("--result", required=True, choices=["success", "failure"])
    reinforce_parser.add_argument("--latency-score", type=float, required=True)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("event_id")

    subparsers.add_parser("sync-boards")
    subparsers.add_parser("status")

    args = parser.parse_args()
    _write_install_receipts()
    if args.command == "watch":
        config = load_config()
        watch_loop(
            root=Path(config.watch_root),
            dedupe_window_ms=config.dedupe_window_ms,
            reconcile_seconds=config.reconcile_seconds,
            on_event=_handle_watch_event,
        )
        return
    if args.command == "emit":
        print(
            json.dumps(
                emit_event_record(
                    ant_id=args.ant_id,
                    source_path=args.source_path,
                    event_type=args.event_type,
                    change=args.change,
                    priority=args.priority,
                    confidence=args.confidence,
                ),
                indent=2,
            )
        )
        return
    if args.command == "route":
        print(json.dumps(route_event_record(args.event_id, topk=args.topk, quorum=args.quorum), indent=2))
        return
    if args.command == "claim":
        claim_receipt = claim_event(args.event_id, args.ant_id, args.role, args.lease_ms)
        payload: dict[str, Any] = {"claim": claim_receipt}
        auto = _auto_promote_if_claimed(claim_receipt)
        if auto:
            payload.update(auto)
        print(json.dumps(payload, indent=2))
        return
    if args.command == "reinforce":
        print(json.dumps(reinforce_route(args.event_id, args.path, args.result, args.latency_score), indent=2))
        return
    if args.command == "promote":
        payload = {"promotion": promote_event(args.event_id), "sync": sync_command_boards()}
        print(json.dumps(payload, indent=2))
        return
    if args.command == "sync-boards":
        print(json.dumps(sync_command_boards(), indent=2))
        return
    if args.command == "status":
        print(json.dumps(_status(), indent=2))


if __name__ == "__main__":
    main()
