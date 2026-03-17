from __future__ import annotations

from pathlib import Path
from typing import Any

from ..command_membrane_runtime import main
from ..command_spine_adapter import (
    BENCHMARK_FIELDS,
    CAPILLARY_FORMULA,
    COORD12_FRAME_GROUPS,
    COORD12_LABELS,
    COMMAND_ROUTE_POLICY,
    CommandMembraneConfig,
    CommandMembraneService,
    LATENCY_FORMULA,
    PROTOCOL_ID,
    ROOT,
    ROUTE_SELECTOR_TERMS,
    WATCH_MODE_DEGRADED,
    WATCH_MODE_EVENT,
    read_json,
    rel,
    utc_now,
    write_json,
)
from ..command_spine import (
    COMMAND_CAPILLARY_LAW_ID_V2,
    COMMAND_PACKET_SCHEMA_ID_V2,
    COMMAND_REWARD_FIELD_ID_V2,
    FIRST_WAVE_WATCHED_SURFACES,
    SELF_ROOT,
)


DEFAULT_CONFIG = CommandMembraneConfig()
PUBLIC_STATE_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"
PROTOCOL_JSON_PATH = DEFAULT_CONFIG.protocol_json_path
PACKET_SCHEMA_JSON_PATH = DEFAULT_CONFIG.packet_schema_json_path
CAPILLARY_LAW_JSON_PATH = DEFAULT_CONFIG.capillary_law_json_path
LATENCY_BENCHMARK_JSON_PATH = DEFAULT_CONFIG.latency_benchmark_json_path
REWARD_LAW_JSON_PATH = DEFAULT_CONFIG.reward_field_json_path
RUNTIME_WITNESS_PATH = DEFAULT_CONFIG.command_manifest_path
SCHEMA_DOC_PATH = DEFAULT_CONFIG.packet_manifest_path
TOOLKIT_DOC_PATH = DEFAULT_CONFIG.protocol_v1_manifest_path
WATCHED_SURFACE_REGISTRY_PATH = DEFAULT_CONFIG.watched_surface_registry_path
LIVE_EVENT_LEDGER_PATH = DEFAULT_CONFIG.live_event_ledger_path
CLAIM_LEDGER_PATH = DEFAULT_CONFIG.claim_ledger_path
CAPILLARY_LEDGER_PATH = DEFAULT_CONFIG.edge_path
LATENCY_REGISTRY_PATH = DEFAULT_CONFIG.latency_registry_path
LIVE_MANIFEST_PATH = DEFAULT_CONFIG.live_manifest_path
SURFACE_HEALTH_PATH = DEFAULT_CONFIG.surface_health_path
EVENT_PACKETS_LEDGER_PATH = LIVE_EVENT_LEDGER_PATH
ROUTE_RECEIPTS_LEDGER_PATH = LIVE_EVENT_LEDGER_PATH
ROUTE_POLICY = COMMAND_ROUTE_POLICY
PACKET_SCHEMA_ID = COMMAND_PACKET_SCHEMA_ID_V2
CAPILLARY_LAW_ID = COMMAND_CAPILLARY_LAW_ID_V2
REWARD_FIELD_ID = COMMAND_REWARD_FIELD_ID_V2


def make_service(config: CommandMembraneConfig | None = None) -> CommandMembraneService:
    return CommandMembraneService(config or DEFAULT_CONFIG)


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
    from time import perf_counter

    svc = service or make_service()
    source_path = Path(str(change.get("source_path") or resolve_source_path(change.get("relative_path", "ATHENA"), service=svc)))
    change_type = str(change.get("change_type") or change.get("kind") or "updated")
    detected_ts = utc_now()
    started = perf_counter()
    packet = svc.emit_change(
        source_path=source_path,
        change_type=change_type,
        detected_ts=detected_ts,
        parent_event_id=str(change.get("parent_event_id") or "ROOT"),
        state=state,
    )
    ended = perf_counter()
    if packet is None:
        last_event_id = str(svc.load_state().get("last_event_id", ""))
        if not last_event_id:
            raise RuntimeError(f"COMMAND packet was deduplicated before any event existed for `{source_path}`.")
        packet = svc.load_event(last_event_id)
    if watcher_mode:
        packet.watcher_mode = watcher_mode
    coord12_frame = dict(getattr(packet, "coord12_frame", {}) or {})
    coord12_frame.setdefault("coord12_labels", list(COORD12_LABELS))
    packet.coord12_frame = coord12_frame
    return packet, 0.0, round((ended - started) * 1000.0, 4)


def rank_worker_candidates(
    packet: Any,
    *,
    state: dict[str, Any] | None = None,
    topk: int = 5,
    service: CommandMembraneService | None = None,
) -> tuple[list[dict[str, Any]], float]:
    from time import perf_counter

    svc = service or make_service()
    started = perf_counter()
    payload = svc.route_event(packet.event_id, state=state)
    ended = perf_counter()
    return list(payload.get("candidate_targets", []))[:topk], round((ended - started) * 1000.0, 4)


def build(config: CommandMembraneConfig | None = None) -> dict[str, Any]:
    svc = make_service(config)
    artifacts = svc.ensure_protocol_artifacts()
    public_state = svc.sync_public_surfaces()
    return {
        "truth": "OK",
        "protocol_id": PROTOCOL_ID,
        "artifacts": {
            key: rel(Path(value))
            for key, value in artifacts.items()
            if isinstance(value, (str, Path))
        },
        "public_state": public_state,
    }


def docs_gate_status(config: CommandMembraneConfig | None = None) -> dict[str, Any]:
    return make_service(config).docs_gate_status()


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
    svc.sync_public_surfaces()
    return svc.packet_to_summary(packet) if packet else {"status": "deduped", "source_path": str(source_path)}


def route(event_id: str, *, service: CommandMembraneService | None = None) -> dict[str, Any]:
    svc = service or make_service()
    payload = svc.route_event(event_id)
    svc.sync_public_surfaces()
    return payload


def claim(
    event_id: str,
    *,
    ant_id: str | None = None,
    role: str = "worker",
    lease_ms: int | None = None,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    svc = service or make_service()
    payload = svc.claim_event(event_id, ant_id=ant_id, role=role, lease_ms=lease_ms)
    svc.sync_public_surfaces()
    payload.setdefault("event_id", event_id)
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
    svc = service or make_service()
    payload = svc.commit_event(
        event_id,
        result=result,
        artifact_paths=artifact_paths,
        writeback_paths=writeback_paths,
        summary=summary,
        work_started_at=work_started_at,
    )
    svc.sync_public_surfaces()
    if "latency" in payload:
        return payload
    latency_sample = dict(payload.get("latency_sample_v2") or {})
    execution_receipt = dict(payload.get("execution_receipt_v2") or {})
    return {
        "event_id": event_id,
        "result": execution_receipt.get("result", result),
        "summary": execution_receipt.get("summary", summary),
        "latency": {
            "detect_ms": latency_sample.get("detection_latency_ms", 0.0),
            "encode_ms": latency_sample.get("t_encode_ms", 0.0),
            "route_ms": latency_sample.get("t_route_ms", latency_sample.get("swarm_awareness_latency_ms", 0.0)),
            "claim_ms": latency_sample.get("t_claim_ms", latency_sample.get("claim_latency_ms", 0.0)),
            "commit_ms": latency_sample.get("t_commit_ms", latency_sample.get("commit_latency_ms", 0.0)),
            "awareness_ms": latency_sample.get("swarm_awareness_latency_ms", latency_sample.get("t_route_ms", 0.0)),
            "t_sugar_ms": latency_sample.get("t_sugar_ms", 0.0),
            "liminal_distance": latency_sample.get("liminal_delta", latency_sample.get("delta_tau", 0.0)),
            "liminal_velocity": latency_sample.get("liminal_velocity", 0.0),
        },
        "execution_receipt_v2": execution_receipt,
        "latency_sample_v2": latency_sample,
        "receipt_json": payload.get("receipt_json", ""),
        "receipt_md": payload.get("receipt_md", ""),
    }


def reinforce(
    event_id: str,
    *,
    path: str | None = None,
    result: str = "success",
    latency_score: float = 0.90,
    service: CommandMembraneService | None = None,
) -> dict[str, Any]:
    svc = service or make_service()
    payload = svc.reinforce_event(event_id, path=path, result=result, latency_score=latency_score)
    svc.sync_public_surfaces()
    return payload


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
    svc = service or make_service()
    payload = svc.watch_command_folder(
        once=once,
        timeout_secs=timeout_secs,
        bootstrap_existing=bootstrap_existing,
        emit_only=emit_only,
    )
    svc.sync_public_surfaces()
    return payload


def status(*, service: CommandMembraneService | None = None) -> dict[str, Any]:
    return (service or make_service()).sync_public_surfaces()


def metrics(surface: str = "command-folder", *, service: CommandMembraneService | None = None) -> dict[str, Any]:
    return (service or make_service()).metrics(surface=surface)


__all__ = [
    "BENCHMARK_FIELDS",
    "CAPILLARY_FORMULA",
    "CAPILLARY_LAW_ID",
    "CAPILLARY_LAW_JSON_PATH",
    "CAPILLARY_LEDGER_PATH",
    "COORD12_FRAME_GROUPS",
    "COORD12_LABELS",
    "CLAIM_LEDGER_PATH",
    "CommandMembraneConfig",
    "CommandMembraneService",
    "DEFAULT_CONFIG",
    "EVENT_PACKETS_LEDGER_PATH",
    "FIRST_WAVE_WATCHED_SURFACES",
    "LATENCY_BENCHMARK_JSON_PATH",
    "LATENCY_FORMULA",
    "LATENCY_REGISTRY_PATH",
    "LIVE_EVENT_LEDGER_PATH",
    "LIVE_MANIFEST_PATH",
    "PACKET_SCHEMA_ID",
    "PACKET_SCHEMA_JSON_PATH",
    "PROTOCOL_ID",
    "PROTOCOL_JSON_PATH",
    "PUBLIC_STATE_PATH",
    "REWARD_FIELD_ID",
    "REWARD_LAW_JSON_PATH",
    "ROOT",
    "ROUTE_POLICY",
    "ROUTE_RECEIPTS_LEDGER_PATH",
    "ROUTE_SELECTOR_TERMS",
    "RUNTIME_WITNESS_PATH",
    "SCHEMA_DOC_PATH",
    "SELF_ROOT",
    "SURFACE_HEALTH_PATH",
    "TOOLKIT_DOC_PATH",
    "WATCHED_SURFACE_REGISTRY_PATH",
    "WATCH_MODE_DEGRADED",
    "WATCH_MODE_EVENT",
    "build",
    "build_change_record",
    "build_event_packet",
    "claim",
    "commit",
    "docs_gate_status",
    "emit",
    "main",
    "make_service",
    "metrics",
    "rank_worker_candidates",
    "read_json",
    "rel",
    "reinforce",
    "resolve_source_path",
    "route",
    "service",
    "status",
    "utc_now",
    "watch",
    "write_json",
]
