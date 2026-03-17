from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ledger_writer import (
    claim_ledger_path,
    event_ledger_path,
    front_memory_path,
    hall_fronts_path,
    promotion_receipts_path,
    read_json,
    read_jsonl,
    route_receipts_path,
    temple_fronts_path,
)
from .liminal_coord import load_config


def _read_fronts(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        latest[row["front_key"]] = row
    return sorted(latest.values(), key=lambda item: item["promoted_at"], reverse=True)


def _read_event_index() -> dict[str, dict[str, Any]]:
    return {row["packet"]["event_id"]: row for row in read_jsonl(event_ledger_path())}


def _read_route_index() -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(route_receipts_path()):
        latest[row.get("event_id")] = row
    return latest


def _read_claim_index() -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(claim_ledger_path()):
        latest[row.get("event_id")] = row
    return latest


def _read_promotion_index() -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(promotion_receipts_path()):
        latest[row.get("source_event_id")] = row
    return latest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _replace_marker_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        return
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    path.write_text(prefix + replacement + suffix, encoding="utf-8")


def _command_temple_section(fronts: list[dict[str, Any]]) -> str:
    if not fronts:
        return "\n".join(
            [
                "## COMMAND Membrane Temple Family",
                "",
                "- Quest id: `NEXT57-T-COMMAND-LAW`",
                "- Surface: no active command-promoted Temple fronts yet.",
                "- Docs gate: `LOCAL_WITNESS_ONLY` / `blocked-by-missing-credentials`",
                "- Top capillary: `awaiting reinforced Temple path`",
                "- Strongest edge class: `pending`",
            ]
        )
    top = fronts[0]
    strongest = "vein" if float(top.get("route_quality", 0.0)) >= 0.82 else ("capillary" if float(top.get("route_quality", 0.0)) >= 0.65 else "emergent")
    lines = [
        "## COMMAND Membrane Temple Family",
        "",
        f"- Quest id: `{top['quest_id']}`",
        "- Surface: docs-gate honesty, coordinate law, capillary law, and no-rumor routing discipline.",
        "- Docs gate: `LOCAL_WITNESS_ONLY` / `blocked-by-missing-credentials`",
        f"- Top capillary: `{top['best_lane']}`",
        f"- Strongest edge class: `{strongest}`",
        "",
        "### Active Temple Command Fronts",
    ]
    for front in fronts[:5]:
        lines.append(f"- `{front['quest_id']}` `{front['front_id']}` `{front['truth']}` `{front['best_lane']}` -> {front['objective']}")
    return "\n".join(lines)


def _command_hall_section(fronts: list[dict[str, Any]], latest_event_id: str | None) -> str:
    if not fronts:
        return "\n".join(
            [
                "## COMMAND Membrane Hall Family",
                "",
                "- Quest id: `NEXT57-H-COMMAND-MEMBRANE`",
                "- Surface: practical command intake, lawful worker claim, and receipt-backed closure.",
                "- Current executable event: `none`",
                "- Owner lane: `awaiting first-lease`",
                "- Source path: `none`",
                "- Replay pointer: `registry/command_protocol/route_receipts.jsonl`",
            ]
        )
    top = fronts[0]
    return "\n".join(
        [
            "## COMMAND Membrane Hall Family",
            "",
            f"- Quest id: `{top['quest_id']}`",
            "- Surface: practical command intake, lawful worker claim, and receipt-backed closure.",
            f"- Current executable event: `{latest_event_id or top['source_event_id']}`",
            f"- Owner lane: `{top['best_lane']}`",
            f"- Source path: `{top.get('source_path', 'see queue board')}`",
            "- Replay pointer: `registry/command_protocol/route_receipts.jsonl`",
            "",
            "### Active Hall Command Fronts",
            *[
                f"- `{front['quest_id']}` `{front['front_id']}` `{front['truth']}` `{front['best_lane']}` -> {front['objective']}"
                for front in fronts[:6]
            ],
        ]
    )


def sync_command_boards() -> dict[str, Any]:
    config = load_config()
    temple_root = Path(config.temple_root)
    hall_root = Path(config.hall_root)
    qshrink_root = Path(config.qshrink_root)
    temple_board = temple_root / "BOARDS" / "04_COMMAND_PROMOTION_BOARD.md"
    hall_event_board = hall_root / "BOARDS" / "09_COMMAND_EVENT_QUEUE_BOARD.md"
    hall_claim_board = hall_root / "BOARDS" / "10_COMMAND_CLAIM_LEASE_BOARD.md"
    hall_route_board = hall_root / "BOARDS" / "11_COMMAND_ROUTE_QUALITY_BOARD.md"
    temple_quest_board = temple_root / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
    hall_quest_board = hall_root / "BOARDS" / "06_QUEST_BOARD.md"
    mirror_path = qshrink_root / "NERVOUS_SYSTEM" / "analysis" / "COMMAND_PROTOCOL_MIRROR.md"

    temple_fronts = _read_fronts(temple_fronts_path())
    hall_fronts = _read_fronts(hall_fronts_path())
    front_memory = read_json(front_memory_path(), {"active_fronts": {}})
    events = list(reversed(read_jsonl(event_ledger_path())))
    routes = _read_route_index()
    claims = _read_claim_index()
    promotions = _read_promotion_index()
    docs_gate = "BLOCKED"
    today = datetime.now(tz=UTC).date().isoformat()

    _write(
        temple_board,
        "\n".join(
            [
                "# Command Promotion Board",
                "",
                f"Date: `{today}`",
                f"Docs Gate: `{docs_gate}`",
                "",
                "## Function",
                "",
                "This board materializes committed command events into Temple-facing structural fronts.",
                "",
                "## Active Temple Fronts",
                "",
            ]
            + (
                [
                    line
                    for front in temple_fronts[:8]
                    for line in [
                        f"- `{front['quest_id']}` `{front['front_id']}` `{front['truth']}` `{front['best_lane']}` quality=`{front['route_quality']}`",
                        f"  - Objective: {front['objective']}",
                        f"  - Why now: {front['why_now']}",
                        f"  - Writeback: {', '.join(front['writeback'])}",
                    ]
                ]
                if temple_fronts
                else ["- No active Temple command fronts yet."]
            )
            + [
                "",
                "## Upsert Memory",
                "",
                f"- active front keys: `{len(front_memory.get('active_fronts', {}))}`",
                f"- Temple front count: `{len(temple_fronts)}`",
            ]
        ),
    )

    queue_lines = [
        "# Command Event Queue Board",
        "",
        f"Date: `{today}`",
        f"Docs Gate: `{docs_gate}`",
        "",
        "## Active Command Events",
        "",
    ]
    for event in events[:12]:
        event_id = event["packet"]["event_id"]
        route = routes.get(event_id)
        claim = claims.get(event_id)
        promotion = promotions.get(event_id)
        promoted_planes = ", ".join(promotion.get("planes", [])) if promotion else "none"
        if not promoted_planes:
            promoted_planes = "none"
        queue_lines.extend(
            [
                f"- `{event_id}` `{event['packet']['tag']}` `{event['packet']['goal']}`",
                f"  - path: `{event.get('source_path', '')}`",
                f"  - selected: `{', '.join(route.get('selected_targets', [])) if route else 'unrouted'}`",
                f"  - claim: `{claim.get('status', 'unclaimed') if claim else 'unclaimed'}`",
                f"  - promoted planes: `{promoted_planes}`",
            ]
        )
    _write(hall_event_board, "\n".join(queue_lines))

    claim_lines = [
        "# Command Claim / Lease Board",
        "",
        f"Date: `{today}`",
        f"Docs Gate: `{docs_gate}`",
        "",
        "## Recent Claims",
        "",
    ]
    for claim in list(reversed(read_jsonl(claim_ledger_path())))[:15]:
        claim_lines.extend(
            [
                f"- `{claim['event_id']}` `{claim['claimer_id']}` `{claim['status']}`",
                f"  - lease_ms: `{claim['lease_ms']}`",
                f"  - claimed_at: `{claim['claimed_at']}`",
                f"  - expires_at: `{claim['expires_at']}`",
            ]
        )
    _write(hall_claim_board, "\n".join(claim_lines))

    route_lines = [
        "# Command Route Quality Board",
        "",
        f"Date: `{today}`",
        f"Docs Gate: `{docs_gate}`",
        "",
        "## Recent Route and Latency Receipts",
        "",
    ]
    receipt_rows = list(reversed(read_jsonl(route_receipts_path())))[:20]
    for row in receipt_rows:
        event_id = row.get("event_id", "unknown")
        if row.get("receipt_type") == "route_decision":
            route_lines.extend(
                [
                    f"- `{event_id}` route selected `{', '.join(row.get('selected_targets', []))}`",
                    f"  - topk: `{row.get('topk', 0)}`",
                    f"  - path class: `{row.get('route_inputs', {}).get('path_class', 'unknown')}`",
                ]
            )
        elif row.get("receipt_type") == "latency_receipt":
            route_lines.extend(
                [
                    f"- `{event_id}` latency verdict `{row.get('verdict', 'NEAR')}` capillary=`{row.get('capillary_score', 0.0)}`",
                    f"  - detect/encode/route/claim/resolve: `{row.get('detect_ms', 0.0)}/{row.get('encode_ms', 0.0)}/{row.get('route_ms', 0.0)}/{row.get('claim_ms', 0.0)}/{row.get('resolve_ms', 0.0)}`",
                ]
            )
    duplicate_count = sum(max(0, int(front.get("occurrence_count", 1)) - 1) for front in front_memory.get("active_fronts", {}).values())
    route_lines.extend(
        [
            "",
            "## Duplicate Suppression Snapshot",
            "",
            f"- active front keys: `{len(front_memory.get('active_fronts', {}))}`",
            f"- duplicate pressure absorbed by upsert: `{duplicate_count}`",
        ]
    )
    _write(hall_route_board, "\n".join(route_lines))

    _replace_marker_block(temple_quest_board, "COMMAND_MEMBRANE_TEMPLE", _command_temple_section(temple_fronts))
    latest_event_id = events[0]["packet"]["event_id"] if events else None
    _replace_marker_block(hall_quest_board, "COMMAND_MEMBRANE_HALL", _command_hall_section(hall_fronts, latest_event_id))

    mirror_lines = [
        "# Command Protocol Mirror",
        "",
        "This surface is the Q-SHRINK-side witness mirror of the COMMAND Protocol v1 membrane.",
        "",
        "## Role",
        "",
        "- upstream sensory membrane: `GLOBAL COMMAND`",
        "- upstream governance: Athena Temple and Global Emergent Guild Hall",
        "- downstream witness body: Q-SHRINK",
        "",
        "Q-SHRINK mirrors only:",
        "",
        "- landed command events",
        "- witnessed route receipts",
        "- explicit frontier-typed command fronts",
        "",
        "It does not become the command governance crown.",
        "",
        "## Automatic Promotion Layer",
        "",
        "- committed command events may upsert one Temple front and one Hall front",
        "- Temple remains the law and mapping plane",
        "- Hall remains the executable owner plane",
        "- Q-SHRINK mirrors landed or explicit frontier-typed command matter only",
        "",
        "## Writeback Law",
        "",
        "- Temple writeback targets command-law and quest-routing surfaces",
        "- Hall writeback targets event queue, claim/lease, route quality, and quest-facing surfaces",
        "- Q-SHRINK keeps downstream witness traces and does not govern promotion",
        "",
        "## Fixed Truth",
        "",
        f"- docs gate: `{docs_gate}`",
        "- local-witness grounded until OAuth exists",
        f"- mirrored Temple command fronts: `{len(temple_fronts)}`",
        f"- mirrored Hall command fronts: `{len(hall_fronts)}`",
        "",
        "## Mirrored Command Fronts",
        "",
    ]
    for front in (temple_fronts + hall_fronts)[:10]:
        if front["truth"] in {"OK", "NEAR"}:
            mirror_lines.extend(
                [
                    f"- `{front['plane']}` `{front['quest_id']}` `{front['truth']}` `{front['source_event_id']}`",
                    f"  - objective: {front['objective']}",
                    f"  - writeback: {', '.join(front['writeback'])}",
                ]
            )
    _write(mirror_path, "\n".join(mirror_lines))

    return {
        "temple_front_count": len(temple_fronts),
        "hall_front_count": len(hall_fronts),
        "active_front_keys": len(front_memory.get("active_fronts", {})),
        "boards": [
            str(temple_board),
            str(hall_event_board),
            str(hall_claim_board),
            str(hall_route_board),
            str(mirror_path),
        ],
    }
