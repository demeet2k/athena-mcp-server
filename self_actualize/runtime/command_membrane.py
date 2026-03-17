from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime.command_spine_adapter import (
        CommandMembraneConfig,
        CommandMembraneService,
        read_json,
        rel,
        utc_now,
        write_json,
    )
else:
    from .command_spine_adapter import (
        CommandMembraneConfig,
        CommandMembraneService,
        read_json,
        rel,
        utc_now,
        write_json,
    )
    ROOT = Path(__file__).resolve().parents[2]


DEFAULT_CONFIG = CommandMembraneConfig()
SELF_ROOT = ROOT / "self_actualize"
GLOBAL_COMMAND_ROOT = DEFAULT_CONFIG.command_surface_root
STATE_PATH = DEFAULT_CONFIG.state_path
LEASE_PATH = DEFAULT_CONFIG.lease_path
EDGE_PATH = DEFAULT_CONFIG.edge_path
PUBLIC_STATE_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"
ACTIVE_RUN_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "BUILD_QUEUE.md"
ACTIVE_QUEUE_PATH = ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "06_active_queue.md"
HALL_BOARD_PATH = ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
PROTOCOL_JSON_PATH = DEFAULT_CONFIG.protocol_json_path
PACKET_SCHEMA_JSON_PATH = DEFAULT_CONFIG.packet_schema_json_path
CAPILLARY_LAW_JSON_PATH = DEFAULT_CONFIG.capillary_law_json_path
LATENCY_BENCHMARK_JSON_PATH = DEFAULT_CONFIG.latency_benchmark_json_path
REWARD_LAW_JSON_PATH = DEFAULT_CONFIG.reward_law_json_path
PROTOCOL_REGISTRY_PATH = DEFAULT_CONFIG.protocol_v1_registry_path
PROTOCOL_MANIFEST_PATH = DEFAULT_CONFIG.protocol_manifest_path
RUNTIME_WITNESS_PATH = DEFAULT_CONFIG.command_manifest_path
SCHEMA_DOC_PATH = DEFAULT_CONFIG.packet_manifest_path
TOOLKIT_DOC_PATH = DEFAULT_CONFIG.protocol_v1_manifest_path
PROTOCOL_ID = "COMMAND_MEMBRANE_V1"
ACTIVE_MEMBRANE = "Q41 / TQ06"
FEEDERS = ["Q42", "Q46", "TQ04", "Q02"]
NATIVE_WATCH_BACKEND = "windows-native-filesystem-events"
WATCHER_MODE = "event-driven"
WATCH_FAILURE_MODE = "degraded-board-reconciliation"
RECONCILIATION_MODE = "whole-workspace board scan fallback and reconciliation"
ROUTE_POLICY = "goal+salience+pheromone+coord"
COORD12_KEYS = [
    "earth_utc_anchor",
    "earth_rotation_phase",
    "earth_orbital_phase",
    "earth_geospatial_anchor",
    "solar_phase",
    "lunar_phase",
    "local_sidereal_phase",
    "canonical_sky_anchor",
    "runtime_region",
    "queue_pressure",
    "goal_salience_vector",
    "change_novelty_vector",
]
COORD12_FRAME_GROUPS = ["earth", "astro", "runtime", "liminal"]
ROUTE_SELECTOR_TERMS = ["goal_fit", "salience", "capillary_strength", "coordinate_proximity", "freshness", "duplicate_penalty"]
BENCHMARK_FIELDS = [
    "detect_latency",
    "awareness_latency",
    "claim_latency",
    "resolution_latency",
    "commit_latency",
    "capillary_score",
    "liminal_delta",
    "earth_delta",
    "liminal_velocity",
    "T_detect_ms",
    "T_encode_ms",
    "T_route_ms",
    "T_claim_ms",
    "T_commit_ms",
    "T_sugar_ms",
    "duplicate_suppression_rate",
    "lease_collision_rate",
    "route_win_rate",
    "capillary_half_life",
]
CAPILLARY_FORMULA = "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)"
LATENCY_EQUATION = "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit"
SCOUT_ID = "SCOUT-01"
ROUTER_ID = "ROUTER-01"
ARCHIVIST_ID = "ARCHIVIST-01"
MARKER_ACTIVE_RUN = "COMMAND_MEMBRANE_ACTIVE_RUN"
MARKER_BUILD_QUEUE = "COMMAND_MEMBRANE_BUILD_QUEUE"
MARKER_HALL = "COMMAND_MEMBRANE_HALL"
MARKER_TEMPLE = "COMMAND_MEMBRANE_TEMPLE"
NEXT_HALL_QUEST_ID = "NEXT57-H-COMMAND-MEMBRANE"
NEXT_TEMPLE_QUEST_ID = "NEXT57-T-COMMAND-LAW"
ACTIVE_LOOP_LABEL = "L02 Survey :: A02 self_actualize"
RESTART_SEED = "L03 Survey A03 ECOSYSTEM"
DUAL_REFERENCE = "LP57-A|LP57-B"


def _canonical_watch_policy() -> dict[str, Any]:
    return {
        "primary_mode": WATCHER_MODE,
        "fallback_mode": "polling",
        "failure_mode": WATCH_FAILURE_MODE,
        "watch_scope": "GLOBAL COMMAND only",
        "native_backend": NATIVE_WATCH_BACKEND,
        "reconciliation_mode": RECONCILIATION_MODE,
    }


def _canonical_command_packet_fields() -> list[str]:
    return [
        "event_id",
        "source_ant_id",
        "event_tag",
        "goal",
        "change_summary",
        "priority",
        "confidence",
        "earth_ts_utc",
        "earth_ts_local",
        "liminal_ts",
        "coord12",
        "coord12_frame",
        "parent_event_id",
        "ttl",
        "pheromone",
        "state_hash",
        "route_class",
        "lineage",
    ]


def _canonicalize_runtime_surfaces(public_state: dict[str, Any]) -> dict[str, Any]:
    state = dict(public_state or {})
    docs_gate = dict(state.get("docs_gate", {}) or {})
    docs_gate.setdefault("state", "BLOCKED")
    docs_gate.setdefault("mode", "LOCAL_WITNESS_ONLY")
    docs_gate.setdefault("witness_class", "LOCAL_WITNESS_ONLY")
    docs_gate.setdefault(
        "detail_text",
        "Google Docs gate remains BLOCKED because Trading Bot/credentials.json and Trading Bot/token.json are missing.",
    )
    state["docs_gate"] = docs_gate
    runtime_truth = dict(state.get("current_runtime_truth", {}) or {})
    runtime_truth["canonical_authority"] = PROTOCOL_ID
    runtime_truth["parent_authority"] = "NEXT57"
    runtime_truth["active_membrane"] = ACTIVE_MEMBRANE
    runtime_truth["feeders"] = list(FEEDERS)
    runtime_truth.setdefault("active_loop", "L02")
    runtime_truth.setdefault("restart_seed", RESTART_SEED)
    runtime_truth.setdefault("visible_caps", {"hall": 8, "temple": 8})
    runtime_truth["authority_mode"] = "LOCAL_WITNESS_ONLY"
    runtime_truth["witness_class"] = "LOCAL_WITNESS_ONLY"
    state["current_runtime_truth"] = runtime_truth
    state["protocol_id"] = PROTOCOL_ID
    state["canonical_authority"] = PROTOCOL_ID
    state["active_surface"] = "GLOBAL COMMAND"
    state["watch_scope"] = "GLOBAL COMMAND only"
    state["watched_surface_count"] = 1
    state["watcher_mode"] = WATCHER_MODE
    state["active_membrane"] = ACTIVE_MEMBRANE
    state["feeder_stack"] = list(FEEDERS)
    state["ant_roles"] = ["SCOUT", "ROUTER", "WORKER", "ARCHIVIST"]
    state["pipeline"] = ["COMMAND FOLDER", "SCOUT", "ROUTER", "WORKER", "ARCHIVIST"]
    state["policy"] = {
        "route_policy": ROUTE_POLICY,
        "selector_terms": ROUTE_SELECTOR_TERMS,
        "topk": 5,
        "claim_mode": "first-lease",
        "quorum": 1,
        "ttl": 6,
        "lease_ms": 1200,
    }
    state["watch_policy"] = _canonical_watch_policy()
    latency_summary = dict(state.get("latency_summary", {}) or {})
    latency_summary.setdefault("detect_latency", 0.0)
    latency_summary.setdefault("awareness_latency", 0.0)
    latency_summary.setdefault("claim_latency", 0.0)
    latency_summary.setdefault("resolution_latency", 0.0)
    latency_summary.setdefault("commit_latency", 0.0)
    latency_summary.setdefault("capillary_score", 0.0)
    latency_summary.setdefault("liminal_delta", 0.0)
    latency_summary.setdefault("earth_delta", 0.0)
    latency_summary.setdefault("liminal_velocity", 0.0)
    latency_summary.setdefault("T_detect_ms", latency_summary.get("detect_latency", 0.0))
    latency_summary.setdefault("T_encode_ms", 0.0)
    latency_summary.setdefault("T_route_ms", latency_summary.get("awareness_latency", 0.0))
    latency_summary.setdefault("T_claim_ms", latency_summary.get("claim_latency", 0.0))
    latency_summary.setdefault("T_commit_ms", latency_summary.get("commit_latency", 0.0))
    latency_summary.setdefault(
        "T_sugar_ms",
        latency_summary.get("T_detect_ms", 0.0)
        + latency_summary.get("T_encode_ms", 0.0)
        + latency_summary.get("T_route_ms", 0.0)
        + latency_summary.get("T_claim_ms", 0.0)
        + latency_summary.get("T_commit_ms", 0.0),
    )
    latency_summary.setdefault("duplicate_suppression_rate", 1.0)
    latency_summary.setdefault("lease_collision_rate", 0.0)
    latency_summary.setdefault("route_win_rate", 0.0)
    latency_summary.setdefault("capillary_half_life", 0.0)
    state["latency_summary"] = latency_summary
    metrics = dict(state.get("metrics", {}) or {})
    for field in BENCHMARK_FIELDS:
        metrics[field] = latency_summary.get(field, metrics.get(field, 0.0))
    state["metrics"] = metrics
    source_row = {
        "source_id": "command_root",
        "absolute_path": str(GLOBAL_COMMAND_ROOT),
        "relative_path": rel(GLOBAL_COMMAND_ROOT),
        "watch_root": str(GLOBAL_COMMAND_ROOT),
        "watch_root_relative": rel(GLOBAL_COMMAND_ROOT),
        "target_kind": "directory",
        "source_class": "command-folder",
        "routing_goal": "detect-classify-assign",
        "watch_mode": WATCHER_MODE,
        "native_backend": NATIVE_WATCH_BACKEND,
        "fallback_mode": "polling",
        "failure_mode": WATCH_FAILURE_MODE,
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "exists": GLOBAL_COMMAND_ROOT.exists(),
        "docs_gate_status": docs_gate.get("state", "BLOCKED"),
    }
    state["source_health"] = [source_row]
    write_json(PUBLIC_STATE_PATH, state)
    write_json(STATE_PATH, state)
    write_json(
        DEFAULT_CONFIG.watched_surface_registry_path,
        {
            "generated_at": utc_now(),
            "protocol_id": PROTOCOL_ID,
            "docs_gate_status": source_row["docs_gate_status"],
            "watcher_mode": WATCHER_MODE,
            "watch_scope": "GLOBAL COMMAND only",
            "source_count": 1,
            "rows": [source_row],
        },
    )
    packet_types = {
        "CommandEventPacket": {"required_fields": _canonical_command_packet_fields()},
        "CommandClaimLease": {
            "required_fields": [
                "lease_id",
                "event_id",
                "worker_ant_id",
                "router_ant_id",
                "role",
                "claim_mode",
                "quorum",
                "lease_ms",
                "status",
                "claimed_at",
                "expires_at",
                "mirrored_claim_id",
                "route_path",
            ]
        },
        "RouteDecision": {
            "required_fields": [
                "event_id",
                "policy_id",
                "selector_terms",
                "candidate_targets",
                "selected_targets",
                "topk",
                "claim_mode",
                "quorum",
                "route_path",
                "worker_choice",
            ]
        },
        "ArchivistReceipt": {
            "required_fields": [
                "event_id",
                "claim_ant_id",
                "result",
                "route_path",
                "replay_ptr",
                "committed_at",
                "summary",
            ]
        },
        "CapillaryEdgeRecord": {
            "required_fields": [
                "edge_id",
                "source_ant_id",
                "target_ant_id",
                "strength",
                "success_count",
                "failure_count",
                "noise_count",
                "grade",
                "last_event_id",
                "updated_at",
            ]
        },
        "LatencyBenchmarkRecord": {"required_fields": BENCHMARK_FIELDS},
    }
    protocol_payload = {
        "protocol_id": PROTOCOL_ID,
        "canonical_authority": PROTOCOL_ID,
        "canonical_surface": "GLOBAL COMMAND",
        "docs_gate": docs_gate,
        "current_runtime_truth": runtime_truth,
        "pipeline": ["COMMAND FOLDER", "SCOUT", "ROUTER", "WORKER", "ARCHIVIST"],
        "ant_roles": ["SCOUT", "ROUTER", "WORKER", "ARCHIVIST"],
        "routing_defaults": {"policy_id": ROUTE_POLICY, "selector_terms": ROUTE_SELECTOR_TERMS, "topk": 5, "claim_mode": "first-lease", "quorum": 1, "ttl": 6, "lease_ms": 1200},
        "command_spine_operations": {"emit": "athena emit", "route": "athena route", "claim": "athena claim", "reinforce": "athena reinforce"},
        "watch_policy": _canonical_watch_policy(),
        "packet_types": packet_types,
    }
    write_json(PROTOCOL_JSON_PATH, protocol_payload)
    write_json(PROTOCOL_REGISTRY_PATH, protocol_payload)
    write_json(
        PACKET_SCHEMA_JSON_PATH,
        {
            "schema_id": "COMMAND_MEMBRANE_PACKET_SCHEMA_V1",
            "packet_types": packet_types,
            "coord12_labels": COORD12_KEYS,
            "coord12_frame_groups": COORD12_FRAME_GROUPS,
        },
    )
    write_json(
        CAPILLARY_LAW_JSON_PATH,
        {
            "law_id": "COMMAND_MEMBRANE_CAPILLARY_LAW_V1",
            "formula": CAPILLARY_FORMULA,
            "edge_classes": ["candidate_path", "capillary", "vein"],
        },
    )
    write_json(
        LATENCY_BENCHMARK_JSON_PATH,
        {
            "benchmark_id": "COMMAND_MEMBRANE_LATENCY_V1",
            "equation": LATENCY_EQUATION,
            "metrics": BENCHMARK_FIELDS,
        },
    )
    write_json(
        REWARD_LAW_JSON_PATH,
        {
            "compatibility_role": "support-only",
            "note": "Capillary reinforcement is authoritative for COMMAND_MEMBRANE_V1.",
        },
    )
    _write_text(
        PROTOCOL_MANIFEST_PATH,
        "# COMMAND Protocol\n\n"
        "- Protocol id: `COMMAND_MEMBRANE_V1`\n"
        "- Surface: `GLOBAL COMMAND`\n"
        "- Watch scope: `GLOBAL COMMAND only`\n"
        "- Primary mode: `event-driven`\n"
        "- Fallback mode: `polling`\n"
        "- Failure mode: `degraded-board-reconciliation`\n"
        "- Reconciliation path: `whole-workspace board scan fallback and reconciliation`\n"
        "- Route policy: `goal+salience+pheromone+coord`\n"
        "- Claim law: `first-lease`, `quorum=1`, `lease_ms=1200`\n"
        "- Docs gate: `BLOCKED` while `Trading Bot/credentials.json` and `Trading Bot/token.json` are missing.\n",
    )
    _write_text(
        SCHEMA_DOC_PATH,
        "# COMMAND Membrane Schema\n\n"
        "- Surface: `GLOBAL COMMAND`\n"
        "- Core coordinate law: `coord12` plus `coord12_frame`\n"
        f"- CommandEventPacket fields: `{', '.join(_canonical_command_packet_fields())}`\n"
        f"- Latency benchmarks: `{', '.join(BENCHMARK_FIELDS)}`\n",
    )
    _write_text(
        TOOLKIT_DOC_PATH,
        "# COMMAND Membrane Protocol\n\n"
        "Turn `GLOBAL COMMAND` into a sensory membrane instead of a passive folder.\n\n"
        "Event-driven watcher intake is primary. The board poll loop is the degraded fallback and reconciliation path.\n\n"
        f"Capillary law: `{CAPILLARY_FORMULA}`\n",
    )
    _write_text(
        RUNTIME_WITNESS_PATH,
        "# COMMAND Membrane Runtime Witness\n\n"
        f"- Protocol id: `{PROTOCOL_ID}`\n"
        f"- Watcher mode: `{WATCHER_MODE}`\n"
        "- Fallback mode: `polling`\n"
        f"- Failure mode: `{WATCH_FAILURE_MODE}`\n"
        f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')}`\n"
        f"- Route policy: `{ROUTE_POLICY}`\n",
    )
    return state


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _patch_markdown_marker(path: Path, marker: str, content: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{content.rstrip()}\n{end}"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before.rstrip() + "\n\n" + block + after
    else:
        text = (text.rstrip() + "\n\n" + block).strip() + "\n"
    _write_text(path, text)


def _sync_receipt_binding_mirrors(public_state: dict[str, Any]) -> None:
    docs_gate = public_state.get("docs_gate", {}) or {}
    last_event = public_state.get("last_event", {}) or {}
    _patch_markdown_marker(
        ACTIVE_RUN_PATH,
        MARKER_ACTIVE_RUN,
        "\n".join(
            [
                "## COMMAND Membrane Active Run",
                "",
                "- Canonical authority: `COMMAND_MEMBRANE_V1`",
                "- Parent authority: `NEXT57`",
                "- Command surface: `GLOBAL COMMAND`",
                "- Watch scope: `GLOBAL COMMAND only`",
                "- Active membrane: `Q41 / TQ06`",
                "- Feeder stack: `Q42, Q46, TQ04, Q02`",
                f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')} / {docs_gate.get('witness_class', 'LOCAL_WITNESS_ONLY')}`",
                f"- Active loop: `{ACTIVE_LOOP_LABEL}`",
                f"- Next Hall quest: `{NEXT_HALL_QUEST_ID}`",
                f"- Next Temple quest: `{NEXT_TEMPLE_QUEST_ID}`",
                f"- Restart seed: `{RESTART_SEED}`",
                f"- Last event: `{last_event.get('event_id', 'none')}` :: `{last_event.get('status', 'none')}`",
            ]
        ),
    )
    _patch_markdown_marker(
        BUILD_QUEUE_PATH,
        MARKER_BUILD_QUEUE,
        "\n".join(
            [
                "## COMMAND Membrane Queue",
                "",
                f"- Queue depth: `{public_state.get('queue_depth', 0)}`",
                f"- Active leases: `{len(public_state.get('active_leases', []))}`",
                f"- Routing policy: `{ROUTE_POLICY}`",
                "- Claim mode: `first-lease`",
                "- Routing budget: `topk=5`, `quorum=1`, `lease_ms=1200`",
                f"- Active loop: `{ACTIVE_LOOP_LABEL}`",
                f"- Next Hall quest: `{NEXT_HALL_QUEST_ID}`",
                f"- Next Temple quest: `{NEXT_TEMPLE_QUEST_ID}`",
                f"- Restart seed: `{RESTART_SEED}`",
                f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')} / {docs_gate.get('witness_class', 'LOCAL_WITNESS_ONLY')}`",
            ]
        ),
    )
    _patch_markdown_marker(
        HALL_BOARD_PATH,
        MARKER_HALL,
        "\n".join(
            [
                "## COMMAND Membrane Hall Family",
                "",
                f"- Quest id: `{NEXT_HALL_QUEST_ID}`",
                f"- Paired Temple quest: `{NEXT_TEMPLE_QUEST_ID}`",
                "- Surface: practical command intake, lawful worker claim, and receipt-backed closure.",
                "- Routing spine: `COMMAND FOLDER -> SCOUT -> ROUTER -> WORKER -> ARCHIVIST`.",
                "- Public cap: `Hall 8`",
                f"- Route law: `{ROUTE_POLICY}`.",
                f"- Active loop: `{ACTIVE_LOOP_LABEL}`",
                f"- Restart seed: `{RESTART_SEED}`",
                f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')} / {docs_gate.get('witness_class', 'LOCAL_WITNESS_ONLY')}`",
                "- Quest polarity: `A-dominant` outward build, `B-dominant` inward route-tightening.",
            ]
        ),
    )
    _patch_markdown_marker(
        TEMPLE_BOARD_PATH,
        MARKER_TEMPLE,
        "\n".join(
            [
                "## COMMAND Membrane Temple Family",
                "",
                f"- Quest id: `{NEXT_TEMPLE_QUEST_ID}`",
                f"- Paired Hall quest: `{NEXT_HALL_QUEST_ID}`",
                "- Surface: docs-gate honesty, coord12 law, capillary law, and selective propagation.",
                "- Prompt-level liminal GPS: `supported`.",
                "- Keystroke-level liminal GPS: `out of scope until client/runtime instrumentation exists`.",
                f"- Active loop: `{ACTIVE_LOOP_LABEL}`",
                f"- Restart seed: `{RESTART_SEED}`",
                f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')} / {docs_gate.get('witness_class', 'LOCAL_WITNESS_ONLY')}`",
                "- Quest polarity: `A-dominant` expansion, `B-dominant` contradiction recovery and compression.",
            ]
        ),
    )


def _refresh_receipt_binding_overlay(
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    svc = service or make_service()
    svc.ensure_protocol_artifacts()
    public_state = _canonicalize_runtime_surfaces(svc.sync_public_surfaces())
    _sync_receipt_binding_mirrors(public_state)
    return public_state


def make_service(config: CommandMembraneConfig | None = None) -> CommandMembraneService:
    return CommandMembraneService(config or CommandMembraneConfig())


def service(config: CommandMembraneConfig | None = None) -> CommandMembraneService:
    return make_service(config)


def resolve_source_path(source: str | Path, service: CommandMembraneService | None = None) -> Path:
    svc = service or make_service()
    candidate = Path(source)
    if candidate.is_absolute():
        return candidate
    if candidate.parts and candidate.parts[0].upper() == "GLOBAL COMMAND":
        return (ROOT / candidate).resolve()
    return (svc.config.command_surface_root / candidate).resolve()


def detect_watcher_mode(service: CommandMembraneService | None = None) -> str:
    del service
    if shutil.which("powershell") is not None:
        return "event-driven"
    return "polling"


def build_change_record(
    area: str | Path,
    change_type: str,
    source_path: str | Path | None = None,
    confidence: float = 0.98,
    parent_event_id: str = "ROOT",
) -> dict[str, Any]:
    resolved_source = resolve_source_path(source_path or area)
    return {
        "area": str(area),
        "source_path": str(resolved_source),
        "relative_path": rel(resolved_source),
        "change_type": change_type,
        "confidence": confidence,
        "parent_event_id": parent_event_id,
    }


def build_event_packet(
    *,
    change: dict[str, Any],
    state: dict[str, Any] | None = None,
    watcher_mode: str | None = None,
    service: CommandMembraneService | None = None,
) -> tuple[Any, float, float]:
    svc = service or make_service()
    source_path = Path(str(change.get("source_path") or resolve_source_path(change.get("relative_path", "ATHENA"), service=svc)))
    change_type = str(change.get("change_type") or change.get("kind") or "updated")
    detected_ts = utc_now()
    started = time.perf_counter()
    packet = svc.emit_change(
        source_path=source_path,
        change_type=change_type,
        detected_ts=detected_ts,
        parent_event_id=str(change.get("parent_event_id") or "ROOT"),
        state=state,
    )
    ended = time.perf_counter()
    if packet is None:
        last_event_id = str(svc.load_state().get("last_event_id", ""))
        if not last_event_id:
            raise RuntimeError(f"COMMAND packet was deduplicated before any event existed for `{source_path}`.")
        packet = svc.load_event(last_event_id)
    detect_ms = 0.0
    encode_ms = round((ended - started) * 1000.0, 4)
    if watcher_mode:
        packet.watcher_mode = watcher_mode
    return packet, detect_ms, encode_ms


def rank_worker_candidates(
    packet: Any,
    *,
    state: dict[str, Any] | None = None,
    topk: int = 5,
    service: CommandMembraneService | None = None,
) -> tuple[list[dict[str, Any]], float]:
    svc = service or make_service()
    started = time.perf_counter()
    route = svc.route_event(packet.event_id, state=state)
    ended = time.perf_counter()
    return route["candidate_targets"][:topk], round((ended - started) * 1000.0, 4)


def emit(
    source_path: str | Path,
    *,
    change_type: str = "updated",
    confidence: float = 0.98,
    parent_event_id: str = "ROOT",
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    svc = service or make_service()
    packet = svc.emit_change(
        source_path=resolve_source_path(source_path, service=svc),
        change_type=change_type,
        detected_ts=utc_now(),
        confidence=confidence,
        parent_event_id=parent_event_id,
    )
    _refresh_receipt_binding_overlay()
    return svc.packet_to_summary(packet) if packet else {"status": "deduped", "source_path": str(source_path)}


def route(event_id: str, *, service: CommandMembraneService | None = None) -> dict[str, Any]:
    payload = (service or make_service()).route_event(event_id)
    _refresh_receipt_binding_overlay()
    return payload


def claim(
    event_id: str,
    *,
    ant_id: str | None = None,
    role: str = "worker",
    lease_ms: int | None = None,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    payload = (service or make_service()).claim_event(
        event_id,
        ant_id=ant_id,
        role=role,
        lease_ms=lease_ms,
    )
    _refresh_receipt_binding_overlay()
    return payload


def commit(
    event_id: str,
    *,
    result: str = "success",
    summary: str = "",
    artifact_paths: list[str] | None = None,
    writeback_paths: list[str] | None = None,
    work_started_at: str | None = None,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    payload = (service or make_service()).commit_event(
        event_id,
        result=result,
        artifact_paths=artifact_paths,
        writeback_paths=writeback_paths,
        summary=summary,
        work_started_at=work_started_at,
    )
    _refresh_receipt_binding_overlay()
    return payload


def reinforce(
    event_id: str,
    *,
    path: str | None = None,
    result: str = "success",
    latency_score: float = 0.90,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    payload = (service or make_service()).reinforce_event(
        event_id,
        path=path,
        result=result,
        latency_score=latency_score,
    )
    _refresh_receipt_binding_overlay()
    return payload


def reinforce_edges(
    *,
    state: dict[str, Any] | None = None,
    event_id: str,
    path: str,
    result: str,
    latency_score: float,
    noise_penalty: float = 0.0,
    service: CommandMembraneService | None = None,
) -> list[dict[str, Any]]:
    del state, noise_penalty
    payload = reinforce(
        event_id,
        path=path,
        result=result,
        latency_score=latency_score,
        service=service,
    )
    return payload["edges"]


def sync(event_id: str | None = None, *, service: CommandMembraneService | None = None) -> dict[str, Any]:
    del event_id, service
    return _refresh_receipt_binding_overlay()


def metrics(surface: str = "command-folder", *, service: CommandMembraneService | None = None) -> dict[str, Any]:
    del surface, service
    return _refresh_receipt_binding_overlay().get("metrics", {})


def watch(
    surface: str = "command",
    *,
    once: bool = False,
    timeout_secs: int = 0,
    bootstrap_existing: bool = False,
    emit_only: bool = False,
    service: CommandMembraneService | None = None,
) -> list[dict[str, Any]]:
    if surface != "command":
        raise ValueError(f"Unsupported watch surface: {surface}")
    payload = (service or make_service()).watch_command_folder(
        once=once,
        timeout_secs=timeout_secs,
        bootstrap_existing=bootstrap_existing,
        emit_only=emit_only,
    )
    _refresh_receipt_binding_overlay()
    return payload


def status(*, service: CommandMembraneService | None = None) -> dict[str, Any]:
    del service
    return _refresh_receipt_binding_overlay()


def build(*, service: CommandMembraneService | None = None) -> dict[str, Any]:
    del service
    public_state = _refresh_receipt_binding_overlay()
    return {
        "protocol": read_json(PROTOCOL_JSON_PATH, {}),
        "schema": read_json(PACKET_SCHEMA_JSON_PATH, {}),
        "reward": read_json(REWARD_LAW_JSON_PATH, {}),
        "capillary": read_json(CAPILLARY_LAW_JSON_PATH, {}),
        "latency": read_json(LATENCY_BENCHMARK_JSON_PATH, {}),
        "public_state": public_state,
    }


def handle_claim(
    event_id: str,
    ant_id: str | None = None,
    lease_ms: int | None = None,
    as_json: bool = False,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    payload = claim(
        event_id,
        ant_id=ant_id,
        lease_ms=lease_ms,
        service=service,
    )
    if as_json:
        emit_output(payload)
    else:
        emit_output(payload)
    return payload


def handle_reinforce(
    event_id: str,
    result: str = "success",
    latency_score: float = 0.90,
    noise_penalty: float = 0.0,
    as_json: bool = False,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    del noise_penalty
    payload = reinforce(
        event_id,
        result=result,
        latency_score=latency_score,
        service=service,
    )
    if as_json:
        emit_output(payload)
    else:
        emit_output(payload)
    return payload


def handle_status(*, as_json: bool = False, service: CommandMembraneService | None = None) -> dict[str, Any]:
    del service
    payload = status()
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return payload


def default_writeback_paths(service: CommandMembraneService) -> list[str]:
    return [
        rel(service.config.command_manifest_path),
        rel(service.config.capillary_manifest_path),
        rel(service.config.latency_manifest_path),
        "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
        "NERVOUS_SYSTEM/95_MANIFESTS/BUILD_QUEUE.md",
        "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        "self_actualize/mycelium_brain/ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
        "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
        "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
    ]


def emit_output(payload: Any) -> None:
    output = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    if getattr(sys.stdout, "buffer", None) is not None:
        sys.stdout.buffer.write((output + "\n").encode("utf-8", errors="replace"))
        return
    print(output)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical COMMAND membrane runtime.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Freeze protocol artifacts and sync public writebacks.")
    build_parser.add_argument("--json", action="store_true", dest="as_json")

    watch = subparsers.add_parser("watch", help="Watch a canonical membrane surface.")
    watch.add_argument("surface", choices=["command"], help="Membrane surface to watch.")
    watch.add_argument("--once", action="store_true")
    watch.add_argument("--timeout-secs", type=int, default=0)
    watch.add_argument("--bootstrap-existing", action="store_true")
    watch.add_argument("--emit-only", action="store_true")
    watch.add_argument("--json", action="store_true", dest="as_json")

    emit_parser = subparsers.add_parser("emit", help="Emit one event packet from a source path.")
    emit_parser.add_argument("source_path")
    emit_parser.add_argument("--change-type", default="updated")
    emit_parser.add_argument("--confidence", type=float, default=0.98)
    emit_parser.add_argument("--parent-event-id", default="ROOT")
    emit_parser.add_argument("--json", action="store_true", dest="as_json")

    route_parser = subparsers.add_parser("route", help="Route an emitted event.")
    route_parser.add_argument("event_id")
    route_parser.add_argument("--json", action="store_true", dest="as_json")

    claim_parser = subparsers.add_parser("claim", help="Claim a routed event with first-lease semantics.")
    claim_parser.add_argument("event_id")
    claim_parser.add_argument("--ant-id")
    claim_parser.add_argument("--role", default="worker")
    claim_parser.add_argument("--lease-ms", type=int)
    claim_parser.add_argument("--json", action="store_true", dest="as_json")

    commit_parser = subparsers.add_parser("commit", help="Commit a claimed event.")
    commit_parser.add_argument("event_id")
    commit_parser.add_argument("--result", default="success")
    commit_parser.add_argument("--summary", default="")
    commit_parser.add_argument("--artifact-path", action="append", dest="artifact_paths", default=[])
    commit_parser.add_argument("--writeback-path", action="append", dest="writeback_paths", default=[])
    commit_parser.add_argument("--work-started-at")
    commit_parser.add_argument("--json", action="store_true", dest="as_json")

    reinforce_parser = subparsers.add_parser("reinforce", help="Reinforce a committed route.")
    reinforce_parser.add_argument("event_id")
    reinforce_parser.add_argument("--path")
    reinforce_parser.add_argument("--result", default="success")
    reinforce_parser.add_argument("--latency-score", type=float, default=0.90)
    reinforce_parser.add_argument("--json", action="store_true", dest="as_json")

    process_parser = subparsers.add_parser("process", help="Run emit -> route -> claim -> commit -> reinforce.")
    process_parser.add_argument("source_path")
    process_parser.add_argument("--change-type", default="updated")
    process_parser.add_argument("--confidence", type=float, default=0.98)
    process_parser.add_argument("--parent-event-id", default="ROOT")
    process_parser.add_argument("--requires-live-docs", action="store_true")
    process_parser.add_argument("--result", default="command_event_committed")
    process_parser.add_argument("--summary", default="")
    process_parser.add_argument("--json", action="store_true", dest="as_json")

    sync_parser = subparsers.add_parser("sync", help="Refresh public command membrane mirrors.")
    sync_parser.add_argument("--event-id")
    sync_parser.add_argument("--json", action="store_true", dest="as_json")

    status_parser = subparsers.add_parser("status", help="Show public command membrane state.")
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    metrics_parser = subparsers.add_parser("metrics", help="Show command membrane latency and capillary metrics.")
    metrics_parser.add_argument("--surface", default="command-folder")
    metrics_parser.add_argument("--json", action="store_true", dest="as_json")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    service = make_service()

    if args.command == "build":
        emit_output(build(service=service))
        return 0

    if args.command == "watch":
        payload = watch(
            "command",
            once=args.once,
            timeout_secs=args.timeout_secs,
            bootstrap_existing=args.bootstrap_existing,
            emit_only=args.emit_only,
            service=service,
        )
        emit_output(payload)
        return 0

    if args.command == "emit":
        emit_output(
            emit(
                args.source_path,
                change_type=args.change_type,
                confidence=args.confidence,
                parent_event_id=args.parent_event_id,
                service=service,
            )
        )
        return 0

    if args.command == "route":
        emit_output(route(args.event_id, service=service))
        return 0

    if args.command == "claim":
        emit_output(
            claim(
                args.event_id,
                ant_id=args.ant_id,
                role=args.role,
                lease_ms=args.lease_ms,
                service=service,
            )
        )
        return 0

    if args.command == "commit":
        emit_output(
            commit(
                args.event_id,
                result=args.result,
                summary=args.summary,
                artifact_paths=args.artifact_paths,
                writeback_paths=args.writeback_paths or default_writeback_paths(service),
                work_started_at=args.work_started_at,
                service=service,
            )
        )
        return 0

    if args.command == "reinforce":
        emit_output(
            reinforce(
                args.event_id,
                path=args.path,
                result=args.result,
                latency_score=args.latency_score,
                service=service,
            )
        )
        return 0

    if args.command == "process":
        packet = service.emit_change(
            source_path=resolve_source_path(args.source_path, service=service),
            change_type=args.change_type,
            detected_ts=utc_now(),
            confidence=args.confidence,
            parent_event_id=args.parent_event_id,
        )
        if packet is None:
            emit_output({"status": "deduped", "source_path": args.source_path})
            return 0

        route_payload = service.route_event(packet.event_id)
        claim_payload = service.claim_event(packet.event_id, lease_ms=service.config.lease_ms)
        if args.requires_live_docs and service.docs_gate_status()["witness_class"] != "LIVE_DOCS_READY":
            commit_payload = service.commit_event(
                packet.event_id,
                result="blocked",
                artifact_paths=[packet.source_path],
                writeback_paths=default_writeback_paths(service),
                summary=args.summary or "Blocked because live Google Docs credentials are still unavailable.",
            )
            reinforce_payload = service.reinforce_event(packet.event_id, result="blocked", latency_score=0.50)
        else:
            commit_payload = service.commit_event(
                packet.event_id,
                result=args.result,
                artifact_paths=[packet.source_path],
                writeback_paths=default_writeback_paths(service),
                summary=args.summary or packet.change_summary,
            )
            t_sugar = float(commit_payload["latency"]["t_sugar_ms"])
            latency_score = max(0.0, min(1.0, 1.0 - min(t_sugar, 10000.0) / 10000.0))
            reinforce_payload = service.reinforce_event(packet.event_id, result="success", latency_score=latency_score)
        emit_output(
            {
                "packet": service.packet_to_summary(packet),
                "route": route_payload,
                "claim": claim_payload,
                "commit": commit_payload,
                "reinforcement": reinforce_payload,
            }
        )
        _refresh_receipt_binding_overlay()
        return 0

    if args.command == "sync":
        emit_output(sync(event_id=args.event_id, service=service))
        return 0

    if args.command == "status":
        emit_output(status(service=service))
        return 0

    if args.command == "metrics":
        emit_output(metrics(surface=args.surface, service=service))
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
