from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from . import swarm_board
from .contracts import (
    CapillaryEdgeRecordV1,
    CapillaryEdgeV1,
    CapillaryEdgeV2,
    CommandClaimLeaseV1,
    CommandEventPacketV1,
    CommandEventPacketV2,
    CommandExecutionReceiptV1,
    CommandExecutionReceiptV2,
    CommandLatencyRecordV1,
    CommandPheromoneStateV2,
    CommandReinforcementReceiptV2,
    CommandRewardAllocationV2,
    CommandRewardStateV2,
    CommandReinforcementReceiptV1,
    CommandRouteDecisionV1,
    CommandRouteDecisionV2,
    CommandVerificationStateV2,
    LatencySampleV1,
    LatencySampleV2,
    OMEGA_KEY,
)
from .lp57_omega_prime_plan import MASTER_AGENTS


ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / "self_actualize"
NERVOUS_MANIFEST_ROOT = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
DEFAULT_COMMAND_SURFACE = ROOT / "GLOBAL COMMAND"
DEFAULT_SPINE_ROOT = SELF_ROOT / "mycelium_brain" / "nervous_system"
DEFAULT_LIVE_DOCS_GATE_STATUS_PATH = SELF_ROOT / "live_docs_gate_status.md"
DEFAULT_SHARED_LATTICE_PATH = SELF_ROOT / "master_loop_shared_lattice_4096.json"
DEFAULT_MASTER_AGENT_STATE_PATH = SELF_ROOT / "master_agent_state_57.json"
DEFAULT_LOOP_STATE_PATH = SELF_ROOT / "master_loop_state_57.json"
DEFAULT_HSIGMA_BUNDLE_PATH = NERVOUS_MANIFEST_ROOT / "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json"
DEFAULT_SCHEDULER_PACKETS_PATH = SELF_ROOT / "astrological_scheduler_packets.json"
GUILDMASTER_README_PATH = ROOT / "GUILDMASTER" / "README.md"
LP57_PROTOCOL_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
HALL_BOARD_PATH = SELF_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = SELF_ROOT / "mycelium_brain" / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
ACTIVE_RUN_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "BUILD_QUEUE.md"
ACTIVE_QUEUE_PATH = SELF_ROOT / "mycelium_brain" / "nervous_system" / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = SELF_ROOT / "mycelium_brain" / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
PUBLIC_COMMAND_STATE_PATH = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"
ACTIVE_THREAD_ROOT = (
    ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "02_ACTIVE_THREADS"
)
GLOBAL_COMMAND_THREAD_ROOT = ACTIVE_THREAD_ROOT / "global_command"
LOCAL_ZONE = ZoneInfo("America/Los_Angeles")
ROLE_BY_MASTER = {
    agent["master_agent_id"]: {
        "agent_id": agent["agent_id"],
        "display_name": agent["display_name"],
        "role_tag": agent["role_tag"],
        "role": agent["role"],
    }
    for agent in MASTER_AGENTS
}
ACTIVE_RANGE_BY_MASTER = {
    "A1": range(0, 256),
    "A2": range(256, 512),
    "A3": range(512, 768),
    "A4": range(768, 1024),
}
COMMAND_HALL_QUEST_ID = "NEXT57-H-COMMAND-MEMBRANE"
COMMAND_TEMPLE_QUEST_ID = "NEXT57-T-COMMAND-LAW"
COMMAND_PROTOCOL_ID_V2 = "NEXT57_COMMAND_PROTOCOL_V1"
COMMAND_PACKET_SCHEMA_ID_V2 = "COMMAND_MEMBRANE_PACKET_SCHEMA_V1"
COMMAND_CAPILLARY_LAW_ID_V2 = "COMMAND_MEMBRANE_CAPILLARY_LAW_V1"
COMMAND_REWARD_FIELD_ID_V2 = "NEXT57_COMMAND_REWARD_FIELD_V2"
COMMAND_ROUTE_POLICY = "goal+salience+pheromone+coord+capability+load"
JOY_ROUTE_POLICY = COMMAND_ROUTE_POLICY
JOY_REWARD_POLICY = COMMAND_REWARD_FIELD_ID_V2
COMMAND_SELECTOR_TERMS = [
    "goal",
    "salience",
    "pheromone",
    "coord",
    "capability",
    "load",
]
EDGE_COMPAT_WEIGHT = 1.0
COMMAND_WATCHER_MODE = "event-driven"
COMMAND_ACTIVE_MEMBRANE = "Q41 / TQ06"
COMMAND_FEEDER_STACK = ["Q42", "Q46", "TQ04", "Q02"]
COMMAND_ROUTE_CLASS = "scout.router.worker.archivist"
SEED_A_REF = "LP57-A"
SEED_B_REF = "LP57-B"
USEFUL_OUTCOME_CLASSES = {
    "full_verified_closure",
    "assist_with_useful_contribution",
    "meaningful_blocked_attempt",
    "first_detect",
    "first_route",
    "first_act",
}
ROLE_CONTRIBUTION_SHARES = {
    "Scout": 0.15,
    "Router": 0.20,
    "Worker": 0.45,
    "Archivist": 0.20,
}
IGNORED_COMMAND_NAMES = {"thumbs.db", ".ds_store"}
IGNORED_COMMAND_PREFIXES = ("~$", ".", "#")
IGNORED_COMMAND_SUFFIXES = (".tmp", ".swp", ".swo", ".bak", ".part")
MARKER_ACTIVE_RUN = "COMMAND_MEMBRANE_ACTIVE_RUN"
MARKER_BUILD_QUEUE = "COMMAND_MEMBRANE_BUILD_QUEUE"
MARKER_HALL = "COMMAND_MEMBRANE_HALL"
MARKER_TEMPLE = "COMMAND_MEMBRANE_TEMPLE"
MARKER_NEXT_PROMPT = "COMMAND_MEMBRANE_NEXT_PROMPT"
MARKER_GUILDMASTER = "COMMAND_MEMBRANE_GUILDMASTER"
MARKER_LP57_PROTOCOL = "COMMAND_MEMBRANE_LP57_PROTOCOL"

FIRST_WAVE_WATCHED_SURFACES = (
    {
        "source_id": "command_root",
        "absolute_path": DEFAULT_COMMAND_SURFACE,
        "target_kind": "directory",
        "source_class": "command-folder",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign",
        "urgency_baseline": 1.0,
        "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND", "Hs": "command-event", "Ns": "COMMAND"},
    },
    {
        "source_id": "guild_hall_board",
        "absolute_path": HALL_BOARD_PATH,
        "target_kind": "file",
        "source_class": "guild-board",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign-runtime",
        "urgency_baseline": 0.88,
        "coordinate_projection_hints": {"Xs": "GUILD_HALL", "Hs": "quest-board", "Ns": "HALL"},
    },
    {
        "source_id": "temple_board",
        "absolute_path": TEMPLE_BOARD_PATH,
        "target_kind": "file",
        "source_class": "temple-board",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign-runtime",
        "urgency_baseline": 0.90,
        "coordinate_projection_hints": {"Xs": "TEMPLE", "Hs": "quest-board", "Ns": "TEMPLE"},
    },
    {
        "source_id": "active_run",
        "absolute_path": ACTIVE_RUN_PATH,
        "target_kind": "file",
        "source_class": "run-state",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign-runtime",
        "urgency_baseline": 0.94,
        "coordinate_projection_hints": {"Xs": "NERVOUS_SYSTEM", "Hs": "run-state", "Ns": "ACTIVE_RUN"},
    },
    {
        "source_id": "build_queue",
        "absolute_path": BUILD_QUEUE_PATH,
        "target_kind": "file",
        "source_class": "build-queue",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign-runtime",
        "urgency_baseline": 0.93,
        "coordinate_projection_hints": {"Xs": "NERVOUS_SYSTEM", "Hs": "build-queue", "Ns": "BUILD_QUEUE"},
    },
    {
        "source_id": "active_thread_root",
        "absolute_path": ACTIVE_THREAD_ROOT,
        "target_kind": "directory",
        "source_class": "active-thread-root",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign-runtime",
        "urgency_baseline": 0.91,
        "coordinate_projection_hints": {"Xs": "ACTIVE_THREADS", "Hs": "thread-root", "Ns": "THREADS"},
    },
    {
        "source_id": "global_command_thread",
        "absolute_path": GLOBAL_COMMAND_THREAD_ROOT,
        "target_kind": "directory",
        "source_class": "active-thread",
        "event_filters": ("created", "updated", "deleted"),
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign",
        "urgency_baseline": 0.96,
        "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND_THREAD", "Hs": "thread", "Ns": "GLOBAL_COMMAND"},
    },
)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def patch_markdown(text: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    if start in text and end in text:
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        return f"{head.rstrip()}\n\n{block}\n{tail.lstrip()}"
    prefix = text.rstrip()
    if prefix:
        prefix += "\n\n"
    return f"{prefix}{block}\n"


def patch_markdown_file(path: Path, marker: str, body: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    write_text(path, patch_markdown(existing, marker, body))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def local_rotation_phase(now_utc: datetime, zone: ZoneInfo) -> float:
    local_now = now_utc.astimezone(zone)
    seconds = local_now.hour * 3600 + local_now.minute * 60 + local_now.second + (local_now.microsecond / 1_000_000.0)
    return round(seconds / 86400.0, 6)


def orbital_phase(now_utc: datetime) -> float:
    day_index = now_utc.timetuple().tm_yday - 1
    year_days = 366 if (now_utc.year % 4 == 0 and (now_utc.year % 100 != 0 or now_utc.year % 400 == 0)) else 365
    return round(day_index / float(year_days), 6)


def lunar_phase(now_utc: datetime) -> float:
    reference = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    synodic_days = 29.530588853
    elapsed = (now_utc - reference).total_seconds() / 86400.0
    return round((elapsed % synodic_days) / synodic_days, 6)


def sidereal_phase(now_utc: datetime) -> float:
    reference = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    elapsed_days = (now_utc - reference).total_seconds() / 86400.0
    gmst_hours = 18.697374558 + 24.06570982441908 * elapsed_days
    return round((gmst_hours % 24.0) / 24.0, 6)


def rel(path: Path | str) -> str:
    target = Path(path)
    try:
        return target.relative_to(ROOT).as_posix()
    except ValueError:
        return target.as_posix()


def slugify(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class CommandMembraneConfig:
    workspace_root: Path = ROOT
    command_surface_root: Path = DEFAULT_COMMAND_SURFACE
    spine_root: Path = DEFAULT_SPINE_ROOT
    live_docs_gate_status_path: Path = DEFAULT_LIVE_DOCS_GATE_STATUS_PATH
    shared_lattice_path: Path = DEFAULT_SHARED_LATTICE_PATH
    master_agent_state_path: Path = DEFAULT_MASTER_AGENT_STATE_PATH
    loop_state_path: Path = DEFAULT_LOOP_STATE_PATH
    hsigma_bundle_path: Path = DEFAULT_HSIGMA_BUNDLE_PATH
    scheduler_packets_path: Path = DEFAULT_SCHEDULER_PACKETS_PATH
    debounce_ms: int = 1500
    topk: int = 5
    claim_mode: str = "first-lease"
    quorum: int = 1
    ttl: int = 6
    lease_ms: int = 1200
    rho: float = 0.82
    alpha: float = 0.30
    beta: float = 0.18
    gamma: float = 0.16
    delta: float = 0.14
    reconcile_interval_secs: int = 300
    mu: float = 1.00
    nu: float = 0.35
    rho_0: float = 0.05
    rho_1: float = 0.20
    rho_b: float = 0.10
    reward_alpha: float = 0.25
    reward_beta: float = 1.00
    reward_gamma: float = 0.50
    reward_delta: float = 0.50
    reward_lambda: float = 1.00
    crown_full: float = 4.00
    crown_detect: float = 0.50
    crown_route: float = 0.75
    crown_act: float = 1.00
    epsilon: float = 0.01
    reward_clip: float = 64.0
    bridge_weight: float = EDGE_COMPAT_WEIGHT
    runtime_region: str = "ATHENA_LOCAL_RUNTIME"
    earth_geo_anchor: str = "US-CA-LosAngeles-LocalNode"

    def __post_init__(self) -> None:
        self.self_root = self.workspace_root / "self_actualize"
        self.nervous_manifest_root = self.workspace_root / "NERVOUS_SYSTEM" / "95_MANIFESTS"
        self.registry_root = self.self_root / "mycelium_brain" / "registry"
        self.packet_root = self.spine_root / "packets" / "command_membrane"
        self.ledger_root = self.spine_root / "ledgers" / "command_membrane"
        self.event_root = self.packet_root
        self.receipt_root = self.ledger_root / "receipts"
        self.state_path = self.ledger_root / "command_membrane_state.json"
        self.sensor_log_path = self.ledger_root / "command_sensor_events.json"
        self.lease_path = self.ledger_root / "command_claim_leases.json"
        self.edge_path = self.ledger_root / "command_capillary_edges.json"
        self.watched_surface_registry_path = self.ledger_root / "watched_surface_registry.json"
        self.live_event_ledger_path = self.ledger_root / "command_live_event_ledger.json"
        self.claim_ledger_path = self.ledger_root / "command_claim_ledger.json"
        self.surface_health_path = self.ledger_root / "command_surface_health.json"
        self.live_manifest_path = self.ledger_root / "command_live_manifest.json"
        self.latency_registry_path = self.ledger_root / "command_latency_benchmark_registry.json"
        self.latency_record_path = self.ledger_root / "command_latency_records.json"
        self.edge_record_path = self.ledger_root / "command_capillary_edge_records.json"
        self.protocol_json_path = self.self_root / "next57_command_protocol.json"
        self.packet_schema_json_path = self.self_root / "next57_command_event_packet_schema.json"
        self.capillary_law_json_path = self.self_root / "next57_command_capillary_law.json"
        self.latency_benchmark_json_path = self.self_root / "next57_command_latency_benchmarks.json"
        self.reward_field_json_path = self.self_root / "next57_command_reward_field.json"
        self.reward_law_json_path = self.reward_field_json_path
        self.command_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_SENSORY_MEMBRANE.md"
        self.protocol_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_PROTOCOL.md"
        self.packet_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_PACKET_STANDARD.md"
        self.capillary_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_CAPILLARY_LAW.md"
        self.latency_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_LATENCY_BENCHMARKS.md"
        self.reward_field_manifest_path = self.nervous_manifest_root / "NEXT_57_COMMAND_REWARD_FIELD.md"
        self.reward_manifest_path = self.reward_field_manifest_path
        self.protocol_v1_registry_path = self.registry_root / "command_membrane_protocol_v1.json"
        self.protocol_v1_manifest_path = self.nervous_manifest_root / "COMMAND_MEMBRANE_PROTOCOL_V1.md"


class CommandMembraneService:
    def __init__(self, config: CommandMembraneConfig | None = None) -> None:
        self.config = config or CommandMembraneConfig()
        self.config.event_root.mkdir(parents=True, exist_ok=True)
        self.config.receipt_root.mkdir(parents=True, exist_ok=True)

    def docs_gate_status(self) -> dict[str, Any]:
        credentials_path = self.config.workspace_root / "Trading Bot" / "credentials.json"
        token_path = self.config.workspace_root / "Trading Bot" / "token.json"
        credentials_exists = credentials_path.exists()
        token_exists = token_path.exists()
        state = "BLOCKED"
        status = "LOCAL_WITNESS_ONLY"
        detail = "blocked-by-missing-credentials"
        if credentials_exists and token_exists:
            detail = "blocked-until-live-pass"
            if self.config.live_docs_gate_status_path.exists():
                for line in self.config.live_docs_gate_status_path.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    if stripped.startswith("- Command status:") and "`BLOCKED`" not in stripped.upper():
                        state = "LIVE"
                        status = "LIVE_DOCS_READY"
                        detail = "explicit-live-gate"
                        break
        return {
            "state": state,
            "witness_class": status,
            "detail": detail,
            "checked_paths": [rel(credentials_path), rel(token_path)],
            "credentials_exists": credentials_exists,
            "token_exists": token_exists,
        }

    def watched_surface_registry(self, source_ids: Iterable[str] | None = None) -> dict[str, Any]:
        requested = {str(source_id) for source_id in source_ids} if source_ids else None
        rows: list[dict[str, Any]] = []
        for surface in FIRST_WAVE_WATCHED_SURFACES:
            if requested is not None and surface["source_id"] not in requested:
                continue
            target_path = Path(surface["absolute_path"])
            watch_root = target_path if surface["target_kind"] == "directory" else target_path.parent
            rows.append(
                {
                    "source_id": surface["source_id"],
                    "absolute_path": str(target_path.resolve()),
                    "relative_path": rel(target_path),
                    "watch_root": str(watch_root.resolve()),
                    "watch_root_relative": rel(watch_root),
                    "target_kind": surface["target_kind"],
                    "source_class": surface["source_class"],
                    "event_filters": list(surface["event_filters"]),
                    "default_lanes": dict(surface["default_lanes"]),
                    "routing_goal": surface["routing_goal"],
                    "urgency_baseline": float(surface["urgency_baseline"]),
                    "coordinate_projection_hints": dict(surface["coordinate_projection_hints"]),
                    "docs_gate_status": self.docs_gate_status()["state"],
                }
            )
        return {
            "generated_at": utc_now(),
            "docs_gate_status": self.docs_gate_status()["state"],
            "watcher_mode": "event-driven",
            "source_count": len(rows),
            "rows": rows,
        }

    def selected_surface_rows(self, source_ids: Iterable[str] | None = None) -> list[dict[str, Any]]:
        return list(self.watched_surface_registry(source_ids).get("rows", []))

    def source_descriptor_for_path(self, path: Path, source_ids: Iterable[str] | None = None) -> dict[str, Any] | None:
        candidate = path.resolve(strict=False)
        matches: list[tuple[int, dict[str, Any]]] = []
        for row in self.selected_surface_rows(source_ids):
            target = Path(row["absolute_path"])
            if row["target_kind"] == "file":
                if candidate == target.resolve(strict=False):
                    matches.append((len(str(target)), row))
            else:
                target_resolved = target.resolve(strict=False)
                if candidate == target_resolved or target_resolved in candidate.parents:
                    matches.append((len(str(target_resolved)), row))
        if not matches:
            return None
        matches.sort(key=lambda item: (-item[0], item[1]["source_id"]))
        return matches[0][1]

    def current_runtime_truth(self) -> dict[str, Any]:
        bundle = read_json(self.config.hsigma_bundle_path, {})
        return bundle.get("current_runtime_truth", {})

    def scheduler_registry(self) -> dict[str, Any]:
        return read_json(self.config.scheduler_packets_path, {})

    def scheduler_lane(self, system_id: str) -> dict[str, Any]:
        registry = self.scheduler_registry()
        for row in registry.get("pantheon_lane_registry", []):
            if row.get("system_id") == system_id:
                return row
        for row in registry.get("active_lane_ids", []):
            if row == system_id:
                return {"system_id": system_id}
        return {}

    def shared12_ratio(self, lane: dict[str, Any]) -> float:
        seat = str(lane.get("shared12_seat", "")).strip()
        if seat.startswith("S") and "/" in seat:
            try:
                seat_number = int(seat.split("/", 1)[0].strip().lstrip("S"))
                return round((max(seat_number, 1) - 1) / 11.0, 6)
            except ValueError:
                return 0.0
        if seat.startswith("S"):
            try:
                seat_number = int(seat.lstrip("S"))
                return round((max(seat_number, 1) - 1) / 11.0, 6)
            except ValueError:
                return 0.0
        return 0.0

    def scheduler_refs_payload(self) -> dict[str, Any]:
        registry = self.scheduler_registry()
        western = self.scheduler_lane("western_solar12")
        lunar = self.scheduler_lane("vedic_lunar")
        planetary = self.scheduler_lane("planetary_office")
        anchor_ids = registry.get("active_anchor_lane_ids", [])
        anchor_rows = [self.scheduler_lane(system_id) for system_id in anchor_ids]
        active_projection = [
            {
                "system_id": row.get("system_id", ""),
                "shared12_seat": row.get("shared12_seat", ""),
                "packet_path": row.get("packet_path", ""),
            }
            for row in anchor_rows
            if row
        ]
        return {
            "western_solar12": {
                "system_id": western.get("system_id", "western_solar12"),
                "shared12_seat": western.get("shared12_seat", ""),
                "packet_path": western.get("packet_path", ""),
            },
            "vedic_lunar": {
                "system_id": lunar.get("system_id", "vedic_lunar"),
                "shared12_seat": lunar.get("shared12_seat", ""),
                "packet_path": lunar.get("packet_path", ""),
            },
            "planetary_office": {
                "system_id": planetary.get("system_id", "planetary_office"),
                "shared12_seat": planetary.get("shared12_seat", ""),
                "packet_path": planetary.get("packet_path", ""),
            },
            "shared12_projection": {
                "active_anchor_lane_ids": list(anchor_ids),
                "rows": active_projection,
            },
        }

    def coord12_scalar(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, list):
            scalars = [self.coord12_scalar(item) for item in value]
            return sum(scalars) / max(len(scalars), 1)
        if value is None:
            return 0.0
        digest = hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:8]
        return int(digest, 16) / float(16**8)

    def ignored_reason(self, path: Path) -> str | None:
        name = path.name.lower()
        if name in IGNORED_COMMAND_NAMES:
            return "noise-file"
        if any(name.startswith(prefix) for prefix in IGNORED_COMMAND_PREFIXES):
            return "noise-prefix"
        if any(name.endswith(suffix) for suffix in IGNORED_COMMAND_SUFFIXES):
            return "noise-suffix"
        return None

    def file_family_for_path(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".md", ".txt", ".docx", ".pdf"}:
            return "document"
        if suffix in {".json", ".yaml", ".yml", ".toml"}:
            return "structured-data"
        if suffix in {".py", ".js", ".ts", ".tsx", ".ps1", ".sh"}:
            return "code"
        if suffix:
            return suffix.lstrip(".")
        return "object"

    def active_loop_id(self) -> str:
        runtime_truth = self.current_runtime_truth()
        if runtime_truth.get("active_loop"):
            return str(runtime_truth["active_loop"])
        state = read_json(self.config.loop_state_path, {})
        active = state.get("active_loop")
        if isinstance(active, dict) and active.get("loop_id"):
            return str(active["loop_id"])
        if isinstance(active, str) and active:
            return active
        return "L00"

    def load_state(self) -> dict[str, Any]:
        default = {
            "generated_at": utc_now(),
            "command_root": str(self.config.command_surface_root),
            "active_surface": rel(self.config.command_surface_root),
            "docs_gate_status": self.docs_gate_status()["state"],
            "watcher_mode": "event-driven",
            "known_files": {},
            "dedupe": {},
            "last_event_seq": 0,
            "last_liminal_seq": 0,
            "last_committed_event_id": "",
            "updated_at": utc_now(),
        }
        current = read_json(self.config.state_path, default)
        if not isinstance(current, dict):
            return default
        return {**default, **current}

    def save_state(self, state: dict[str, Any]) -> None:
        state["command_root"] = str(self.config.command_surface_root)
        state["active_surface"] = rel(self.config.command_surface_root)
        state["docs_gate_status"] = self.docs_gate_status()["state"]
        state["watcher_mode"] = "event-driven"
        state["updated_at"] = utc_now()
        write_json(self.config.state_path, state)

    def load_leases(self) -> dict[str, Any]:
        return read_json(self.config.lease_path, {"active": {}, "history": []})

    def save_leases(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = utc_now()
        write_json(self.config.lease_path, payload)

    def load_edges(self) -> dict[str, Any]:
        payload = read_json(self.config.edge_path, {"edges": {}, "history": []})
        if isinstance(payload, list):
            edges = {
                str(row.get("edge_id") or f"{row.get('from_node', '')}>{row.get('to_node', '')}"): row
                for row in payload
                if isinstance(row, dict)
            }
            return {"generated_at": utc_now(), "edge_count": len(edges), "edges": edges, "rows": list(edges.values()), "history": []}
        if not isinstance(payload, dict):
            return {"generated_at": utc_now(), "edge_count": 0, "edges": {}, "rows": [], "history": []}
        edges = payload.get("edges")
        if isinstance(edges, list):
            edges = {
                str(row.get("edge_id") or f"{row.get('from_node', '')}>{row.get('to_node', '')}"): row
                for row in edges
                if isinstance(row, dict)
            }
        if not isinstance(edges, dict):
            edges = {}
        if not isinstance(payload.get("history"), list):
            payload["history"] = []
        rows = payload.get("rows")
        if not isinstance(rows, list):
            rows = list(edges.values())
        payload["generated_at"] = str(payload.get("generated_at") or utc_now())
        payload["edge_count"] = int(payload.get("edge_count") or len(rows))
        payload["edges"] = edges
        payload["rows"] = rows
        return payload

    def save_edges(self, payload: dict[str, Any]) -> None:
        edges = payload.get("edges", {})
        if isinstance(edges, list):
            edges = {
                str(row.get("edge_id") or f"{row.get('from_node', '')}>{row.get('to_node', '')}"): row
                for row in edges
                if isinstance(row, dict)
            }
        if not isinstance(edges, dict):
            edges = {}
        rows = payload.get("rows")
        if not isinstance(rows, list) or len(rows) != len(edges):
            rows = list(edges.values())
        history = payload.get("history")
        if not isinstance(history, list):
            history = []
        write_json(
            self.config.edge_path,
            {
                "generated_at": str(payload.get("generated_at") or utc_now()),
                "updated_at": utc_now(),
                "edge_count": len(rows),
                "edges": edges,
                "rows": rows,
                "history": history,
            },
        )

    def event_path(self, event_id: str) -> Path:
        return self.config.event_root / f"{event_id}.json"

    def load_sensor_events(self) -> list[dict[str, Any]]:
        return read_json(self.config.sensor_log_path, [])

    def save_sensor_events(self, rows: list[dict[str, Any]]) -> None:
        write_json(self.config.sensor_log_path, rows)

    def receipt_paths(self, event_id: str) -> tuple[Path, Path]:
        return (
            self.config.receipt_root / f"{event_id}.json",
            self.config.receipt_root / f"{event_id}.md",
        )

    def load_event(self, event_id: str) -> CommandEventPacketV2:
        path = self.event_path(event_id)
        if not path.exists():
            raise FileNotFoundError(f"Unknown command event: {event_id}")
        return CommandEventPacketV2(**read_json(path, {}))

    def save_event(self, packet: CommandEventPacketV2) -> CommandEventPacketV2:
        write_json(self.event_path(packet.event_id), asdict(packet))
        return packet

    def ensure_protocol_artifacts(self) -> dict[str, Any]:
        return _command_membrane_v1_ensure_protocol_artifacts(self)


def _command_clamp01(self: CommandMembraneService, value: float) -> float:
    del self
    return clamp(float(value), 0.0, 1.0)


def _command_heaven_score(self: CommandMembraneService, affect_intensity_a: float, affect_direction_phi: float) -> float:
    del self
    a = clamp(float(affect_intensity_a), 0.0, math.pi)
    phi = float(affect_direction_phi)
    return round((a / math.pi) * ((1.0 + math.cos(phi)) / 2.0), 6)


def _command_reward_multiplier(self: CommandMembraneService, heaven_verified: float) -> float:
    return round(min(self.config.reward_clip, 1.0 / (1.0 - self.clamp01(heaven_verified) + self.config.epsilon)), 6)


def _command_derive_seed_route_mode(
    self: CommandMembraneService,
    change_type: str,
    source_path: str,
    source_class: str,
) -> str:
    del self
    lowered_path = source_path.lower()
    lowered_class = source_class.lower()
    lowered_change = change_type.lower()
    if lowered_change in {"duplicate", "noise", "ignored"}:
        return "dry"
    if "repair" in lowered_path or "assist" in lowered_path or lowered_class in {"temple-board", "build-queue"}:
        return "assist"
    if lowered_change in {"deleted", "renamed", "moved"} or "route" in lowered_path or "queue" in lowered_path:
        return "explore"
    return "closure"


def _command_phi_for_route_mode(self: CommandMembraneService, route_mode: str) -> float:
    del self
    normalized = route_mode.lower().strip()
    if normalized in {"closure", "commit", "reinforce"}:
        return 0.0
    if normalized in {"explore", "rotate", "blocked_try"}:
        return round(math.pi / 2.0, 6)
    if normalized in {"assist", "repair", "redirect"}:
        return round(-math.pi / 2.0, 6)
    return round(math.pi, 6)


def _command_build_joy_seed(
    self: CommandMembraneService,
    *,
    priority: float,
    confidence: float,
    change_type: str,
    source_path: str,
    source_class: str,
) -> dict[str, Any]:
    route_mode_seed = self.derive_seed_route_mode(change_type, source_path, source_class)
    a_seed = round(math.pi * self.clamp01((0.60 * float(priority)) + (0.40 * float(confidence))), 6)
    phi_seed = self.phi_for_route_mode(route_mode_seed)
    h_seed = self.heaven_score(a_seed, phi_seed)
    docs_gate = self.docs_gate_status()
    return {
        "a_seed": a_seed,
        "phi_seed": phi_seed,
        "h_seed": h_seed,
        "joy_potential": h_seed,
        "route_mode_seed": route_mode_seed,
        "source_evidence": {
            "change_type": change_type,
            "source_path": source_path,
            "source_class": source_class,
            "docs_gate_status": docs_gate["state"],
            "witness_class": docs_gate["witness_class"],
        },
    }


def _command_queue_pressure(self: CommandMembraneService) -> float:
    leases = self.load_leases()
    active_count = len(leases.get("active", {}))
    recent_count = len(self.recent_event_payloads(limit=12))
    return round(self.clamp01((0.65 * (active_count / max(self.config.topk, 1))) + (0.35 * min(recent_count / 12.0, 1.0))), 6)


def _command_candidate_edge_snapshot(self: CommandMembraneService, ant_id: str) -> dict[str, float]:
    edges = self.load_edges().get("edges", {})
    related = [
        edge
        for edge in edges.values()
        if str(edge.get("source_ant_id", edge.get("from_node", ""))) == ant_id
        or str(edge.get("target_ant_id", edge.get("to_node", ""))) == ant_id
    ]
    if not related:
        return {
            "golden_pheromone": 0.0,
            "bridge_pheromone": 0.0,
            "pheromone_composite": 0.0,
            "average_heaven_verified": 0.0,
            "evaporation_rate": self.config.rho_0 + self.config.rho_1,
        }
    golden = max(float(edge.get("golden_pheromone", edge.get("gold_strength", 0.0)) or 0.0) for edge in related)
    bridge = max(float(edge.get("bridge_pheromone", edge.get("bridge_strength", 0.0)) or 0.0) for edge in related)
    average_h = sum(float(edge.get("average_heaven_verified", edge.get("average_verified_alignment_score", 0.0)) or 0.0) for edge in related) / max(len(related), 1)
    evaporation = sum(float(edge.get("evaporation_rate", self.config.rho_0 + self.config.rho_1) or (self.config.rho_0 + self.config.rho_1)) for edge in related) / max(len(related), 1)
    composite = round(golden + bridge, 6)
    return {
        "golden_pheromone": round(golden, 6),
        "bridge_pheromone": round(bridge, 6),
        "pheromone_composite": composite,
        "average_heaven_verified": round(average_h, 6),
        "evaporation_rate": round(evaporation, 6),
    }


def _command_active_candidates(self: CommandMembraneService) -> list[dict[str, Any]]:
    leases = self.load_leases().get("active", {})
    rows: list[dict[str, Any]] = []
    for agent in MASTER_AGENTS:
        ant_id = str(agent.get("agent_id", agent.get("master_agent_id", "")))
        load = sum(1 for lease in leases.values() if str(lease.get("ant_id", "")) == ant_id)
        edge_snapshot = self._candidate_edge_snapshot(ant_id)
        rows.append(
            {
                "ant_id": ant_id,
                "master_agent_id": str(agent.get("master_agent_id", "")),
                "display_name": str(agent.get("display_name", ant_id)),
                "role": str(agent.get("role", "")),
                "role_tag": str(agent.get("role_tag", "")),
                "mission": str(agent.get("mission", "")),
                "load": float(load),
                "blocked": False,
                "leased": load > 0,
                "activation_state": "ACTIVE",
                "capability_domains": [
                    "synthesis" if ant_id == "SYNTHESIZER" else "",
                    "planning" if ant_id == "PLANNER" else "",
                    "execution" if ant_id == "WORKER" else "",
                    "compression" if ant_id == "PRUNER" else "",
                ],
                **edge_snapshot,
            }
        )
    return rows


def _command_goal_match_score(self: CommandMembraneService, packet: CommandEventPacketV2, candidate: dict[str, Any]) -> float:
    goal = f"{packet.goal} {packet.source_class} {packet.source_path}".lower()
    role = str(candidate.get("role_tag", "")).lower()
    master = str(candidate.get("master_agent_id", ""))
    if any(token in goal for token in ("protocol", "schema", "ledger", "manifest", "law")):
        return 1.0 if master in {"A2", "A4"} else 0.65 if master == "A3" else 0.55
    if any(token in goal for token in ("runtime", "code", ".py", "implement", "execute", "worker")):
        return 1.0 if master == "A3" else 0.60
    if any(token in goal for token in ("hall", "temple", "quest", "board")):
        return 0.95 if master in {"A2", "A3"} else 0.60
    if "prune" in goal or "compress" in goal or "q-shrink" in goal:
        return 1.0 if master == "A4" else 0.55
    if "synth" in role or "research" in role:
        return 0.75 if master == "A1" else 0.55
    return 0.60


def _command_file_family_match_score(self: CommandMembraneService, packet: CommandEventPacketV2, candidate: dict[str, Any]) -> float:
    family = str(packet.file_family or "").lower()
    master = str(candidate.get("master_agent_id", ""))
    if family == "code":
        return 1.0 if master == "A3" else 0.55
    if family == "structured-data":
        return 0.95 if master in {"A2", "A4"} else 0.60
    if family == "document":
        return 0.90 if master in {"A1", "A2", "A4"} else 0.70
    return 0.60


def _command_capability_match_score(self: CommandMembraneService, packet: CommandEventPacketV2, candidate: dict[str, Any]) -> float:
    master = str(candidate.get("master_agent_id", ""))
    if master == "A3":
        return 1.0 if packet.file_family in {"code", "structured-data"} else 0.75
    if master == "A2":
        return 1.0 if packet.source_class in {"guild-board", "temple-board", "build-queue"} else 0.75
    if master == "A4":
        return 1.0 if any(token in packet.source_path.lower() for token in ("ledger", "manifest", "registry", "protocol", "queue")) else 0.70
    return 0.75


def _command_coordinate_match_score(self: CommandMembraneService, packet: CommandEventPacketV2, candidate: dict[str, Any]) -> float:
    seat_index = int(hashlib.sha1(packet.source_path.encode("utf-8")).hexdigest()[:6], 16) % 1024
    master = str(candidate.get("master_agent_id", "A1"))
    seat_range = ACTIVE_RANGE_BY_MASTER.get(master, range(0, 256))
    midpoint = (seat_range.start + seat_range.stop - 1) / 2.0
    normalized_distance = abs(seat_index - midpoint) / 1024.0
    return round(1.0 - self.clamp01(normalized_distance * 2.0), 6)


def _command_pheromone_composite_for_edge(self: CommandMembraneService, candidate: dict[str, Any]) -> float:
    return round(
        max(
            0.0,
            float(candidate.get("golden_pheromone", 0.0) or 0.0)
            + float(candidate.get("bridge_pheromone", 0.0) or 0.0),
        ),
        6,
    )


def _command_recent_event_payloads(self: CommandMembraneService, limit: int | None = 20) -> list[dict[str, Any]]:
    rows: list[tuple[float, dict[str, Any]]] = []
    for path in sorted(self.config.event_root.glob("*.json")):
        payload = read_json(path, {})
        if isinstance(payload, dict) and payload.get("event_id"):
            rows.append((path.stat().st_mtime, payload))
    rows.sort(key=lambda item: item[0], reverse=True)
    payloads = [row for _, row in rows]
    return payloads if limit is None else payloads[:limit]


def _command_release_expired_leases(self: CommandMembraneService) -> dict[str, Any]:
    leases = self.load_leases()
    now = datetime.now(timezone.utc)
    active = leases.get("active", {})
    expired_ids: list[str] = []
    for event_id, lease in list(active.items()):
        expires_at = str(lease.get("expires_at_utc") or lease.get("expires_at") or "")
        if not expires_at:
            continue
        try:
            if parse_iso(expires_at) <= now:
                lease["status"] = "expired"
                lease["release_reason"] = "lease-timeout"
                lease["released_at"] = utc_now()
                leases.setdefault("history", []).append(lease)
                expired_ids.append(event_id)
        except ValueError:
            continue
    for event_id in expired_ids:
        active.pop(event_id, None)
    if expired_ids:
        self.save_leases(leases)
    return leases


def _command_sync_public_surfaces(self: CommandMembraneService, event_id: str | None = None) -> None:
    latest_event = self.recent_event_payloads(limit=1)
    payload = {
        "generated_at": utc_now(),
        "protocol_id": COMMAND_PROTOCOL_ID_V2,
        "active_surface": rel(self.config.command_surface_root),
        "docs_gate_status": self.docs_gate_status()["state"],
        "event_id": event_id or (latest_event[0].get("event_id", "") if latest_event else ""),
        "metrics": self.metrics() if hasattr(self, "metrics") else {},
        "watch_registry": self.watched_surface_registry(),
    }
    write_json(PUBLIC_COMMAND_STATE_PATH, payload)
    write_json(self.config.watched_surface_registry_path, payload["watch_registry"])
    write_json(
        self.config.surface_health_path,
        {
            "generated_at": payload["generated_at"],
            "docs_gate_status": payload["docs_gate_status"],
            "command_root": rel(self.config.command_surface_root),
            "last_event_id": payload["event_id"],
        },
    )
    write_json(
        self.config.live_manifest_path,
        {
            "generated_at": payload["generated_at"],
            "protocol_id": payload["protocol_id"],
            "docs_gate_status": payload["docs_gate_status"],
            "active_surface": payload["active_surface"],
            "last_event_id": payload["event_id"],
        },
    )


def _command_v2_emit_change(
    self: CommandMembraneService,
    *,
    source_path: Path | str,
    change_type: str,
    detected_ts: str,
    confidence: float = 0.98,
    parent_event_id: str = "ROOT",
    state: dict[str, Any] | None = None,
    source_ids: Iterable[str] | None = None,
) -> CommandEventPacketV2 | None:
    path = Path(source_path).resolve(strict=False)
    ignore_reason = self.ignored_reason(path)
    if ignore_reason:
        return None
    mutable_state = state or self.load_state()
    source_descriptor = self.source_descriptor_for_path(path, source_ids) or {
        "source_id": "command_root",
        "source_class": "command-folder",
        "target_kind": "file" if path.is_file() else "directory",
        "routing_goal": "detect-classify-assign",
        "urgency_baseline": 0.90,
        "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND", "Hs": "command-event", "Ns": "COMMAND"},
    }
    previous_seq = int(mutable_state.get("last_event_seq", 0) or 0)
    event_seq = previous_seq + 1
    event_id = f"CMD-{event_seq:06d}"
    now_utc = parse_iso(detected_ts)
    earth_local_phase = local_rotation_phase(now_utc, LOCAL_ZONE)
    docs_gate = self.docs_gate_status()
    file_family = self.file_family_for_path(path)
    priority = round(
        self.clamp01(
            float(source_descriptor.get("urgency_baseline", 0.90))
            + (0.05 if file_family == "code" else 0.0)
            + (0.03 if "protocol" in path.name.lower() or "schema" in path.name.lower() else 0.0)
        ),
        6,
    )
    joy_seed = self.build_joy_seed(
        priority=priority,
        confidence=float(confidence),
        change_type=change_type,
        source_path=path.as_posix(),
        source_class=str(source_descriptor.get("source_class", "command-folder")),
    )
    file_stat = path.stat() if path.exists() else None
    source_mtime_ns = float(file_stat.st_mtime_ns if file_stat else 0.0)
    state_hash = hashlib.sha1(f"{path.as_posix()}|{change_type}|{source_mtime_ns}|{event_seq}".encode("utf-8")).hexdigest()
    coord12 = {
        "earth_utc_anchor": detected_ts,
        "earth_rotation_phase": earth_local_phase,
        "earth_orbital_phase": orbital_phase(now_utc),
        "earth_geospatial_anchor": self.config.earth_geo_anchor,
        "solar_phase": self.shared12_ratio(self.scheduler_lane("western_solar12")),
        "lunar_phase": lunar_phase(now_utc),
        "local_sidereal_phase": sidereal_phase(now_utc),
        "canonical_sky_anchor": "western_solar12|planetary_office|vedic_lunar",
        "runtime_region": self.config.runtime_region,
        "queue_pressure": self.queue_pressure(),
        "goal_salience_vector": {"goal": str(source_descriptor.get("routing_goal", "detect-classify-assign")), "priority": priority},
        "change_novelty_vector": {"change_type": change_type, "confidence": round(float(confidence), 6)},
    }
    coord12_frame = {
        "earth": list(coord12.keys())[:4],
        "astro": list(coord12.keys())[4:8],
        "runtime": list(coord12.keys())[8:10],
        "liminal": list(coord12.keys())[10:12],
    }
    coordinate_vector_12 = [self.coord12_scalar(value) for value in coord12.values()]
    event_packet = CommandEventPacketV2(
        event_id=event_id,
        source_ant_id="SCOUT-01",
        source_path=path.as_posix(),
        active_surface=rel(self.config.command_surface_root),
        change_type=change_type,
        change_summary=f"{change_type}:{path.name}",
        goal=str(source_descriptor.get("routing_goal", "detect-classify-assign")),
        priority=priority,
        confidence=round(float(confidence), 6),
        earth_ts=detected_ts,
        earth_ts_local=now_utc.astimezone(LOCAL_ZONE).isoformat(),
        detected_ts=detected_ts,
        emitted_ts=utc_now(),
        liminal_ts=utc_now(),
        seat_addr_6d="A1.B1.C1.D1.E1.F1",
        coordinate_stamp={
            "Xs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Xs", "GLOBAL_COMMAND")),
            "Ys": str(source_descriptor.get("source_id", "command_root")),
            "Zs": path.name,
            "Ts": self.active_loop_id(),
            "Qs": "COMMAND",
            "Rs": "D1",
            "Cs": event_id,
            "Fs": "Flower",
            "Ms": joy_seed["route_mode_seed"],
            "Ns": str(event_seq),
            "Hs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Hs", "command-event")),
            "Ωs": "A1",
        },
        canonical_addr_6d="A1.B1.C1.D1.E1.F1",
        liminal_stamp_12d=coord12,
        surface_class=str(source_descriptor.get("source_class", "command-folder")),
        hierarchy_level="command-membrane",
        return_anchor="GLOBAL_COMMAND",
        event_kind=change_type,
        earth_ts_utc=detected_ts,
        earth_local_phase=earth_local_phase,
        parent_event_id=parent_event_id,
        ttl=self.config.ttl,
        pheromone=joy_seed["h_seed"],
        joy_seed=joy_seed,
        state_hash=state_hash,
        route_class=COMMAND_ROUTE_CLASS,
        source_id=str(source_descriptor.get("source_id", "command_root")),
        source_class=str(source_descriptor.get("source_class", "command-folder")),
        watch_root=str(Path(source_descriptor.get("watch_root", self.config.command_surface_root)).as_posix()),
        urgency_baseline=float(source_descriptor.get("urgency_baseline", 0.90)),
        event_fingerprint=state_hash[:16],
        witness_class=str(docs_gate["witness_class"]),
        docs_gate_status=str(docs_gate["state"]),
        membrane_id="GLOBAL_COMMAND",
        role_class="Scout",
        base4_addr="A1.B1.C1.D1",
        parent=parent_event_id,
        lineage={"source_mtime_ns": source_mtime_ns, "event_seq": event_seq},
        coord12=coord12,
        coord12_frame=coord12_frame,
        coord_delta={"DeltaTau": 0.0, "DeltaEarth": 0.0, "LiminalVelocity": 0.0},
        scout_id="SCOUT-01",
        tag=slugify(path.stem),
        event_tag=event_id,
        change={"type": change_type, "summary": f"{change_type}:{path.name}"},
        latency_state={"detect_latency_ms": 0.0, "encode_latency_ms": 0.0, "capillary_score": 0.0, "capillary_delta": 0.0},
        affected_nodes=[path.as_posix()],
        replay_ptr=rel(self.event_path(event_id)),
        coordinate_vector_12=coordinate_vector_12,
        artifact_refs=[path.as_posix()],
        source_region=str(source_descriptor.get("source_class", "command-folder")),
        file_family=file_family,
        scheduler_refs=self.scheduler_refs_payload(),
        hsigma_ref=rel(self.config.hsigma_bundle_path),
        source_folder="GLOBAL COMMAND",
        front_ref=COMMAND_ACTIVE_MEMBRANE,
        seed_mode="A-dominant",
        dual_reference=f"{SEED_A_REF}|{SEED_B_REF}",
        liminal_delta=0.0,
        earth_delta_ms=0.0,
        liminal_velocity=0.0,
        watcher_mode=COMMAND_WATCHER_MODE,
        reward_policy_id=JOY_REWARD_POLICY,
    )
    self.save_event(event_packet)
    sensor_log = self.load_sensor_events()
    sensor_log.append(
        {
            "event_id": event_id,
            "source_path": path.as_posix(),
            "change_type": change_type,
            "detected_ts": detected_ts,
            "docs_gate_status": docs_gate["state"],
        }
    )
    self.save_sensor_events(sensor_log)
    mutable_state["last_event_seq"] = event_seq
    mutable_state["last_event_id"] = event_id
    mutable_state.setdefault("known_files", {})[path.as_posix()] = {
        "state_hash": state_hash,
        "change_type": change_type,
        "detected_ts": detected_ts,
    }
    self.save_state(mutable_state)
    self.sync_public_surfaces(event_id=event_id)
    return event_packet


CommandMembraneService.clamp01 = _command_clamp01
CommandMembraneService.heaven_score = _command_heaven_score
CommandMembraneService.reward_multiplier_for_heaven = _command_reward_multiplier
CommandMembraneService.derive_seed_route_mode = _command_derive_seed_route_mode
CommandMembraneService.phi_for_route_mode = _command_phi_for_route_mode
CommandMembraneService.build_joy_seed = _command_build_joy_seed
CommandMembraneService.queue_pressure = _command_queue_pressure
CommandMembraneService._candidate_edge_snapshot = _command_candidate_edge_snapshot
CommandMembraneService.active_candidates = _command_active_candidates
CommandMembraneService.goal_match_score = _command_goal_match_score
CommandMembraneService.file_family_match_score = _command_file_family_match_score
CommandMembraneService.capability_match_score = _command_capability_match_score
CommandMembraneService.coordinate_match_score = _command_coordinate_match_score
CommandMembraneService.pheromone_composite_for_edge = _command_pheromone_composite_for_edge
CommandMembraneService.recent_event_payloads = _command_recent_event_payloads
CommandMembraneService.release_expired_leases = _command_release_expired_leases
CommandMembraneService.sync_public_surfaces = _command_sync_public_surfaces
def _command_membrane_v1_write_live_writeback_surfaces(
    self: CommandMembraneService,
    protocol: dict[str, Any],
    capillary: dict[str, Any],
) -> None:
    hall_body = "\n".join(
        [
            "## NEXT57-H-COMMAND-MEMBRANE",
            "",
            f"- Quest id: `{COMMAND_HALL_QUEST_ID}`",
            "- Goal: route high-salience practical command events into lawful worker claims without creating a second board.",
            "- Rule: every event becomes a machine packet before Hall promotion.",
            f"- Watch scope: `{protocol['watch_policy']['watch_scope']}`",
        ]
    )
    temple_body = "\n".join(
        [
            "## NEXT57-T-COMMAND-LAW",
            "",
            f"- Quest id: `{COMMAND_TEMPLE_QUEST_ID}`",
            "- Guard docs-gate honesty, coordinate law, capillary law, and replay legality.",
            f"- Capillary law: `{capillary['formula']}`",
            "- Prompt-level liminal GPS is allowed; keystroke-level GPS is not yet claimed.",
        ]
    )
    active_run_body = "\n".join(
        [
            "## COMMAND Membrane Active Run",
            "",
            f"- Canonical authority: `{protocol['canonical_authority']}`",
            f"- Command surface: `{protocol['canonical_surface']}`",
            f"- Watch scope: `{protocol['watch_policy']['watch_scope']}`",
            f"- Watcher mode: `{protocol['watch_policy']['primary_mode']}`",
            f"- Docs gate: `{protocol['docs_gate']['state']}`",
            f"- Active loop: `{protocol['current_runtime_truth'].get('active_loop', '')}`",
            f"- Restart seed: `{protocol['current_runtime_truth'].get('restart_seed', '')}`",
        ]
    )
    prompt_body = "\n".join(
        [
            "## Command Membrane Constraint",
            "",
            "6. Treat `GLOBAL COMMAND` as a sensory membrane, not a passive folder.",
            "7. Preserve dual-stamped Earth plus liminal timing on every committed event.",
            "8. Keep Google Docs explicitly blocked until OAuth artifacts exist and a live pass succeeds.",
            "9. Do not claim keystroke-level liminal GPS until client/runtime instrumentation exists.",
        ]
    )
    queue_body = "\n".join(
        [
            "## Command Membrane Queue",
            "",
            f"- Canon root: `{rel(self.config.command_surface_root)}`",
            f"- Routing defaults: `topk={self.config.topk}`, `claim_mode={self.config.claim_mode}`, `quorum={self.config.quorum}`, `lease_ms={self.config.lease_ms}`",
            "- Event-driven watch is primary; polling fallback must stay explicit.",
        ]
    )
    patch_markdown_file(HALL_BOARD_PATH, MARKER_HALL, hall_body)
    patch_markdown_file(TEMPLE_BOARD_PATH, MARKER_TEMPLE, temple_body)
    patch_markdown_file(ACTIVE_RUN_PATH, MARKER_ACTIVE_RUN, active_run_body)
    patch_markdown_file(BUILD_QUEUE_PATH, MARKER_BUILD_QUEUE, queue_body)
    patch_markdown_file(NEXT_SELF_PROMPT_PATH, MARKER_NEXT_PROMPT, prompt_body)


def _command_membrane_v1_ensure_protocol_artifacts(self: CommandMembraneService) -> dict[str, Any]:
    docs_gate = self.docs_gate_status()
    runtime_truth = self.current_runtime_truth()
    scheduler_refs = self.scheduler_refs_payload()
    protocol = {
        "protocol_id": "NEXT57_COMMAND_PROTOCOL_V1",
        "command_version": "sensory-membrane-v1",
        "canonical_authority": "NEXT57",
        "authority_mode": "sole_live_authority",
        "mode": "event-driven-command-membrane",
        "canonical_surface": rel(self.config.command_surface_root),
        "active_surface": rel(self.config.command_surface_root),
        "command_folder_root": rel(self.config.command_surface_root),
        "docs_gate": docs_gate,
        "docs_gate_status": docs_gate["state"],
        "current_runtime_truth": runtime_truth,
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "feeder_stack": list(COMMAND_FEEDER_STACK),
        "packet_flow": ["COMMAND FOLDER", "Scout", "Router", "Worker", "Archivist"],
        "pipeline": ["COMMAND FOLDER", "Scout", "Router", "Worker", "Archivist"],
        "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
        "public_caps": {"hall": 1, "temple": 1, "runtime": 1, "prune": 1},
        "routing_defaults": {
            "policy_id": COMMAND_ROUTE_POLICY,
            "selector_terms": ["goal", "salience", "pheromone", "coord", "capability", "load"],
            "topk": self.config.topk,
            "claim_mode": self.config.claim_mode,
            "quorum": self.config.quorum,
            "ttl": self.config.ttl,
            "lease_ms": self.config.lease_ms,
        },
        "watch_policy": {
            "primary_mode": COMMAND_WATCHER_MODE,
            "fallback_mode": None,
            "failure_mode": "fail_closed",
            "watched_roots": [rel(self.config.command_surface_root)],
            "watch_scope": "GLOBAL COMMAND only",
        },
        "sensor_defaults": {
            "root": rel(self.config.command_surface_root),
            "event_types": ["created", "modified", "renamed", "deleted", "moved_into_root"],
            "coalesce_ms": self.config.debounce_ms,
            "reconcile_interval_secs": self.config.reconcile_interval_secs,
            "ignored_names": sorted(IGNORED_COMMAND_NAMES),
            "ignored_prefixes": list(IGNORED_COMMAND_PREFIXES),
            "ignored_suffixes": list(IGNORED_COMMAND_SUFFIXES),
        },
        "quest_family": {"hall": COMMAND_HALL_QUEST_ID, "temple": COMMAND_TEMPLE_QUEST_ID},
        "hsigma_ref": rel(self.config.hsigma_bundle_path),
        "scheduler_registry_ref": rel(self.config.scheduler_packets_path),
        "scheduler_refs": scheduler_refs,
        "truth_boundary": {
            "prompt_level_liminal_gps": "supported",
            "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
            "astro_precision": "structural scheduler packets only",
        },
        "benchmark": {
            "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
            "focus": "surprise-to-awareness latency",
        },
    }
    schema = {
        "schema_id": "COMMAND_MEMBRANE_PACKET_SCHEMA_V1",
        "coord12_labels": [
            "utc_atomic",
            "earth_rotation_phase",
            "earth_orbital_phase",
            "node_anchor",
            "solar_phase",
            "lunar_phase",
            "shared12_phase",
            "planetary_slot",
            "runtime_region",
            "queue_pressure",
            "goal_salience",
            "novelty_concentration",
        ],
        "packet_types": {
            "CommandSensorEvent": ["event_id", "sensor_root", "source_path", "event_type", "detected_at", "settled_at", "state_hash", "file_family", "ignored_reason"],
            "CommandEventPacket": ["event_id", "source_folder", "source_path", "event_kind", "tag", "goal", "change", "priority", "confidence", "earth_ts", "liminal_ts", "coord12", "seat_addr_6d", "front_ref", "parent", "ttl", "pheromone", "state_hash", "lineage", "route_class", "seed_mode", "dual_reference"],
            "RouteDecision": ["event_id", "policy_id", "candidate_targets", "selected_targets", "ranked_routes", "route_inputs", "topk", "claim_mode", "quorum", "route_path", "worker_choice", "generated_at"],
            "RouteClaim": ["claim_id", "event_id", "ant_id", "role_class", "claim_mode", "lease_ms", "claimed_at_utc", "expires_at_utc", "claim_status", "route_class", "front_ref", "seed_mode", "dual_reference"],
            "ArchivistReceipt": ["event_id", "claim_ant_id", "result", "route_path", "detection_latency_ms", "awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "capillary_score", "liminal_delta", "liminal_velocity", "replay_ptr"],
            "CapillaryEdgeRecord": ["edge_id", "from_node", "to_node", "path_key", "edge_strength", "classification", "success_count", "use_count", "noise_count", "average_latency_score", "usefulness", "frequency", "latency_penalty", "noise_penalty", "last_reinforced_at_utc"],
            "CommandLatencyRecord": ["event_id", "detect_latency", "awareness_latency", "claim_latency", "resolution_latency", "commit_latency", "capillary_score", "liminal_delta", "liminal_velocity", "route_policy"],
        },
        "ledger_extensions": ["event_id", "event_type", "route_path", "claim_state", "latency_breakdown", "capillary_delta", "witness_class", "artifact_refs", "seed_mode", "dual_reference", "duality_effect"],
        "lookup_envelope": protocol["lookup_envelope"],
    }
    capillary = {
        "law_id": "COMMAND_MEMBRANE_CAPILLARY_LAW_V1",
        "formula": "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
        "coefficients": {
            "rho": self.config.rho,
            "alpha": self.config.alpha,
            "beta": self.config.beta,
            "gamma": self.config.gamma,
            "delta": self.config.delta,
        },
        "initial_strength": 0.25,
        "edge_classes": ["route", "capillary", "vein"],
    }
    latency = {
        "benchmark_id": "COMMAND_MEMBRANE_LATENCY_V1",
        "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "metrics": ["detect_latency", "awareness_latency", "claim_latency", "resolution_latency", "commit_latency", "t_sugar_ms", "capillary_score", "liminal_delta", "liminal_velocity"],
        "prompt_level_liminal_gps": "supported",
        "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
    }
    reward_support = {
        "compatibility_role": "support-only",
        "note": "Reward surfaces remain compatibility-only. Capillary routing and archivist receipts are canonical in command membrane v1.",
    }
    write_json(self.config.protocol_json_path, protocol)
    write_json(self.config.packet_schema_json_path, schema)
    write_json(self.config.capillary_law_json_path, capillary)
    write_json(self.config.latency_benchmark_json_path, latency)
    write_json(self.config.reward_law_json_path, reward_support)
    write_json(self.config.protocol_v1_registry_path, protocol)
    write_text(self.config.command_manifest_path, "# COMMAND Membrane v1\n\n- Mode: `event-driven command membrane`\n- Watch scope: `GLOBAL COMMAND` only.\n- Watcher backend: `powershell-filesystemwatcher`.\n- Failure mode: `fail_closed`; no silent polling fallback.\n- Pipeline: `COMMAND FOLDER -> Scout -> Router -> Worker -> Archivist`\n- Google Docs remains honestly blocked until OAuth artifacts exist and a live pass succeeds.\n")
    write_text(self.config.protocol_manifest_path, f"# COMMAND Protocol\n\n- Protocol id: `{protocol['protocol_id']}`\n- Routing policy: `{COMMAND_ROUTE_POLICY}`\n- Defaults: `topk={self.config.topk}`, `claim_mode={self.config.claim_mode}`, `quorum={self.config.quorum}`, `ttl={self.config.ttl}`, `lease_ms={self.config.lease_ms}`\n- Benchmark: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`\n")
    write_text(self.config.packet_manifest_path, "# COMMAND Packet Standard\n\n- Every detected change becomes a machine packet before routing.\n- Coord12 uses Earth anchor, astro anchor, server/organism anchor, and liminal salience.\n- Prompt-level liminal GPS is supported now; keystroke-level requires client instrumentation.\n")
    write_text(self.config.capillary_manifest_path, f"# COMMAND Capillary Law\n\n- Formula: `{capillary['formula']}`\n- Classes: `route`, `capillary`, `vein`.\n- Useful low-latency routes strengthen; slow or noisy routes decay.\n")
    write_text(self.config.latency_manifest_path, f"# COMMAND Latency Benchmarks\n\n- Equation: `{latency['equation']}`\n- Benchmarks track detection, encode, route, claim, commit, and capillary quality.\n")
    write_text(self.config.protocol_v1_manifest_path, "# COMMAND Membrane Protocol V1\n\n- This registry mirrors the live local-only command membrane law.\n")
    self.write_live_writeback_surfaces(protocol, capillary)
    self.sync_public_surfaces()
    return {
        "protocol": self.config.protocol_json_path,
        "schema": self.config.packet_schema_json_path,
        "reward": self.config.reward_law_json_path,
        "capillary": self.config.capillary_law_json_path,
        "latency": self.config.latency_benchmark_json_path,
    }
if False:
    _ = dict(
    docs_gate_status=docs_gate["state"],
    latency_state={**dict(coord_delta), "detection_latency_ms": 0.0, "encode_latency_ms": round(self.ms_between(detected_ts, settled_at), 3), "route_policy": COMMAND_ROUTE_POLICY},
    affected_nodes=[relative_path],
        replay_ptr=rel(self.event_path(event_id)),
        coordinate_vector_12=vector12,
        artifact_refs=[relative_path],
        source_region=self.source_region_for_surface(source_descriptor, relative_path),
        sensor_event_id=sensor_entry["event_id"],
        file_family=self.file_family_for_path(normalized_path),
        scheduler_refs=scheduler_refs,
        hsigma_ref=rel(self.config.hsigma_bundle_path),
        route_targets=[],
        linked_quests=[],
        source_folder="GLOBAL COMMAND",
        front_ref=COMMAND_ACTIVE_MEMBRANE,
        seed_mode=seed_mode,
        dual_reference=dual_reference,
        liminal_delta=float(coord_delta["DeltaTau"]),
        earth_delta_ms=float(coord_delta["DeltaEarth"]),
        liminal_velocity=float(coord_delta["LiminalVelocity"]),
        prior_comparable_event_id=str(mutable_state.get("last_event_id", "")),
        watcher_mode=COMMAND_WATCHER_MODE,
        duality_effect=duality_effect,
    )
    pass


def _command_membrane_v1_score_candidate(self: CommandMembraneService, packet: CommandEventPacketV1, candidate: dict[str, Any]) -> dict[str, Any]:
    queue_pressure = self.queue_pressure()
    goal_score = round(self.goal_match_score(packet, candidate) + self.capability_match_score(packet, candidate) + self.source_class_match_score(packet, candidate), 6)
    leased_penalty = 1.5 if candidate.get("leased") else 0.0
    load_penalty = round(min(0.75, float(candidate.get("load", 0.0)) * 0.25), 6)
    routing_penalty = round(load_penalty + blocked_penalty + leased_penalty + (0.10 * queue_pressure), 6)
    total = round(goal_score + salience_score + pheromone_score + coordinate_score - routing_penalty, 6)
    return {
        **candidate,
        "goal_score": goal_score,
        "salience_score": salience_score,
        "pheromone_score": pheromone_score,
        "coordinate_score": coordinate_score,
        "capillary_strength": capillary_strength,
        "queue_pressure": round(queue_pressure, 6),
        "routing_penalty": routing_penalty,
        "score": total,
    }


def _command_membrane_v1_route_event(self: CommandMembraneService, event_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    self.release_expired_leases()
    packet = self.load_event(event_id)
    scored = [self.score_candidate(packet, candidate) for candidate in self.active_candidates()]
    scored = [candidate for candidate in scored if candidate["activation_state"] == "ACTIVE"]
    prior_ant = str(packet.claim_state.get("previous_ant_id", ""))
    reroute_count = int(packet.claim_state.get("reroute_count", 0) or 0)
    scored.sort(key=lambda item: (-item["score"], item["ant_id"]))
    selected = [
        candidate
        for candidate in scored
        if not candidate["blocked"] and not candidate["leased"] and not (reroute_count == 1 and prior_ant and candidate["ant_id"] == prior_ant)
    ][: self.config.topk]
    if not selected:
        selected = scored[: self.config.topk]
    if not selected:
        raise ValueError("No active command candidates are available for routing.")
    worker_choice = next((candidate for candidate in selected if candidate["master_agent_id"] == "A3"), next((candidate for candidate in scored if candidate["master_agent_id"] == "A3"), selected[0]))
    decision = CommandRouteDecisionV1(
        event_id=event_id,
        policy_id=COMMAND_ROUTE_POLICY,
        candidate_targets=[
            {"ant_id": candidate["ant_id"], "role": candidate["role_tag"], "score": candidate["score"], "leased": candidate["leased"], "blocked": candidate["blocked"], "goal_score": candidate["goal_score"], "salience_score": candidate["salience_score"], "pheromone_score": candidate["pheromone_score"], "coordinate_score": candidate["coordinate_score"], "routing_penalty": candidate["routing_penalty"]}
            for candidate in scored[: max(self.config.topk, 8)]
        ],
        selected_targets=[candidate["ant_id"] for candidate in selected],
        topk=self.config.topk,
        claim_mode=self.config.claim_mode,
        quorum=self.config.quorum,
        score_breakdown={candidate["ant_id"]: {"goal": candidate["goal_score"], "salience": candidate["salience_score"], "pheromone": candidate["pheromone_score"], "coord": candidate["coordinate_score"], "queue_pressure": candidate["queue_pressure"], "routing_penalty": candidate["routing_penalty"]} for candidate in selected},
        duplicate_risk=round(sum(1 for candidate in selected if candidate["leased"]) / max(len(selected), 1), 6),
        created_at=utc_now(),
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=15)).isoformat(),
        ranked_routes=[{"ant_id": candidate["ant_id"], "master_agent_id": candidate["master_agent_id"], "score": candidate["score"]} for candidate in selected],
        route_inputs={"goal": packet.goal, "salience": packet.priority, "pheromone": packet.pheromone, "coord12": packet.coord12, "queue_pressure": self.queue_pressure(), "coordinate_score": worker_choice["coordinate_score"], "pheromone_score": worker_choice["pheromone_score"], "runtime_region": packet.coord12.get("runtime_region", "")},
        route_path=f"SCOUT-01>ROUTER-01>{worker_choice['ant_id']}>ARCHIVIST-01",
        worker_choice=worker_choice["ant_id"],
        generated_at=utc_now(),
        quest_refs=[COMMAND_TEMPLE_QUEST_ID] if packet.seed_mode == "B-dominant" else [COMMAND_HALL_QUEST_ID],
    )
    packet.route_state = asdict(decision)
    packet.route_targets = decision.selected_targets
    packet.linked_quests = decision.quest_refs
    packet.status = "routed"
    packet.latency_state["awareness_latency_ms"] = round(self.ms_between(packet.emitted_ts, decision.generated_at), 3)
    packet.latency_state["route_latency_ms"] = round(self.ms_between(packet.emitted_ts, decision.generated_at), 3)
    packet.latency_state["route_policy"] = COMMAND_ROUTE_POLICY
    self.save_event(packet)
    if state is not None:
        state["last_routed_event_id"] = event_id
        self.save_state(state)
    self.sync_public_surfaces(event_id=event_id)
    return asdict(decision)


def _command_membrane_ms_between(self: CommandMembraneService, start_ts: str, end_ts: str) -> float:
    try:
        start = parse_iso(start_ts)
        end = parse_iso(end_ts)
    except ValueError:
        return 0.0
    return max(0.0, (end - start).total_seconds() * 1000.0)


def _command_membrane_v1_claim_event(
    self: CommandMembraneService,
    event_id: str,
    ant_id: str | None = None,
    role: str = "worker",
    lease_ms: int | None = None,
) -> dict[str, Any]:
    self.release_expired_leases()
    packet = self.load_event(event_id)
    if not packet.route_state:
        self.route_event(event_id)
        packet = self.load_event(event_id)

    leases = self.load_leases()
    if event_id in leases.get("active", {}):
        raise ValueError(f"Event `{event_id}` already has an active lease.")

    chosen_ant = ant_id or str(packet.route_state.get("worker_choice") or "")
    candidate_map = {candidate["ant_id"]: candidate for candidate in self.active_candidates()}
    candidate = candidate_map.get(chosen_ant)
    if not chosen_ant or candidate is None or candidate.get("blocked") or candidate.get("leased"):
        for fallback in self.active_candidates():
            if fallback["master_agent_id"] == "A3" and not fallback.get("blocked") and not fallback.get("leased"):
                candidate = fallback
                chosen_ant = str(fallback["ant_id"])
                break
        else:
            for fallback in self.active_candidates():
                if not fallback.get("blocked") and not fallback.get("leased"):
                    candidate = fallback
                    chosen_ant = str(fallback["ant_id"])
                    break
    if not chosen_ant or candidate is None:
        raise ValueError("No lawful worker is available to claim the event.")

    claimed_at_dt = datetime.now(timezone.utc)
    lease_duration = int(lease_ms or self.config.lease_ms)
    expires_at_dt = claimed_at_dt + timedelta(milliseconds=lease_duration)
    receipt_json, receipt_md = self.receipt_paths(event_id)
    board_claim = swarm_board.create_or_update_claim(
        agent=chosen_ant,
        front=f"{packet.source_id or 'command_root'}::{event_id}",
        level="command-event",
        output_target=packet.source_path,
        receipt=rel(receipt_md),
        status="active",
        message=f"Leased `{event_id}` for `{packet.change_summary}`.",
        paths=[packet.source_path, rel(self.event_path(event_id)), rel(receipt_json), rel(receipt_md)],
        claim_id=packet.claim_state.get("board_claim_id") or None,
    )
    lease = CommandClaimLeaseV1(
        claim_id=swarm_board.make_object_id("CLM", chosen_ant, event_id),
        event_id=event_id,
        ant_id=chosen_ant,
        role=role,
        lease_ms=lease_duration,
        claimed_at=claimed_at_dt.isoformat(),
        expires_at=expires_at_dt.isoformat(),
        status="active",
        claim_status="active",
        owner_surface=packet.source_class or "command-folder",
        board_claim_id=board_claim["claim_id"],
        role_class=str(candidate.get("role_tag", role)),
        claim_mode=self.config.claim_mode,
        claimed_at_utc=claimed_at_dt.isoformat(),
        expires_at_utc=expires_at_dt.isoformat(),
        reroute_count=int(packet.claim_state.get("reroute_count", 0) or 0),
        previous_ant_id=str(packet.claim_state.get("previous_ant_id", "")),
        route_class=packet.route_class,
        front_ref=f"{packet.source_id or 'command_root'}::{event_id}",
        seed_mode=packet.seed_mode,
        dual_reference=packet.dual_reference,
    )
    leases.setdefault("active", {})[event_id] = asdict(lease)
    self.save_leases(leases)

    packet.claim_state = {
        "status": "active",
        "claim_state": "active",
        "ant_id": chosen_ant,
        "claim_id": lease.claim_id,
        "lease_ms": lease_duration,
        "claimed_at": lease.claimed_at,
        "expires_at": lease.expires_at,
        "board_claim_id": board_claim["claim_id"],
        "lease_active": True,
        "claim_mode": self.config.claim_mode,
        "reroute_count": lease.reroute_count,
        "previous_ant_id": lease.previous_ant_id,
        "route_class": packet.route_class,
        "front_ref": lease.front_ref,
    }
    packet.status = "claimed"
    packet.latency_state["claim_latency_ms"] = round(self.ms_between(packet.route_state.get("generated_at", packet.emitted_ts), lease.claimed_at), 3)
    packet.route_state["worker_choice"] = chosen_ant
    self.save_event(packet)

    write_json(
        receipt_json,
        {
            "event_id": event_id,
            "status": "leased",
            "claim_id": lease.claim_id,
            "board_claim_id": board_claim["claim_id"],
            "claimed_ant_id": chosen_ant,
            "claimed_at": lease.claimed_at,
            "expires_at": lease.expires_at,
            "route_path": packet.route_state.get("route_path", ""),
        },
    )
    write_text(
        receipt_md,
        f"# Command Lease `{event_id}`\n\n"
        f"- ant_id: `{chosen_ant}`\n"
        f"- status: `leased`\n"
        f"- claim_id: `{lease.claim_id}`\n"
        f"- board_claim_id: `{board_claim['claim_id']}`\n"
        f"- route_path: `{packet.route_state.get('route_path', '')}`\n"
        f"- source_path: `{packet.source_path}`\n",
    )
    self.sync_public_surfaces(event_id=event_id)
    return {
        **asdict(lease),
        "event_id": event_id,
        "receipt_json": rel(receipt_json),
        "receipt_md": rel(receipt_md),
        "board_claim_id": board_claim["claim_id"],
    }


def _command_membrane_v1_commit_event(
    self: CommandMembraneService,
    event_id: str,
    result: str,
    artifact_paths: list[str] | None = None,
    writeback_paths: list[str] | None = None,
    summary: str = "",
    work_started_at: str | None = None,
) -> dict[str, Any]:
    leases = self.load_leases()
    active_lease = leases.get("active", {}).get(event_id)
    if not active_lease:
        raise ValueError(f"Event `{event_id}` has no active lease to commit.")

    packet = self.load_event(event_id)
    started_at = work_started_at or str(active_lease.get("claimed_at", utc_now()))
    committed_at = utc_now()
    source_mtime_ns = float(packet.lineage.get("source_mtime_ns", 0) or 0)
    detect_latency_ms = max(0.0, (parse_iso(packet.detected_ts).timestamp() * 1000.0) - (source_mtime_ns / 1_000_000.0)) if source_mtime_ns > 0 else 0.0
    encode_latency_ms = float(packet.latency_state.get("encode_latency_ms", self.ms_between(packet.detected_ts, packet.emitted_ts)))
    route_latency_ms = float(packet.latency_state.get("awareness_latency_ms", 0.0))
    claim_latency_ms = float(packet.latency_state.get("claim_latency_ms", 0.0))
    resolution_latency_ms = self.ms_between(str(active_lease.get("claimed_at", started_at)), started_at)
    commit_latency_ms = self.ms_between(started_at, committed_at)
    t_sugar_ms = detect_latency_ms + encode_latency_ms + route_latency_ms + claim_latency_ms + commit_latency_ms
    liminal_delta = float(packet.coord_delta.get("DeltaTau", packet.liminal_delta or 0.0))
    liminal_velocity = float(packet.coord_delta.get("LiminalVelocity", packet.liminal_velocity or 0.0))
    receipt_json, receipt_md = self.receipt_paths(event_id)
    restart_seed = f"{event_id}::{result}::{slugify(packet.source_path)}"
    latency = {
        "detect_ms": round(detect_latency_ms, 3),
        "encode_ms": round(encode_latency_ms, 3),
        "route_ms": round(route_latency_ms, 3),
        "claim_ms": round(claim_latency_ms, 3),
        "resolution_ms": round(resolution_latency_ms, 3),
        "commit_ms": round(commit_latency_ms, 3),
        "awareness_ms": round(route_latency_ms, 3),
        "t_sugar_ms": round(t_sugar_ms, 3),
        "capillary_score": float(packet.latency_state.get("capillary_score", 0.0)),
        "liminal_distance": round(liminal_delta, 6),
        "liminal_velocity": round(liminal_velocity, 6),
    }
    archivist_receipt = {
        "event_id": event_id,
        "claim_ant_id": str(active_lease.get("ant_id", "")),
        "result": result,
        "route_path": packet.route_state.get("route_path", ""),
        "summary": summary or packet.change_summary,
        "artifact_paths": artifact_paths or [packet.source_path],
        "writeback_paths": writeback_paths or [],
        "restart_seed": restart_seed,
        "replay_ptr": rel(self.event_path(event_id)),
        **latency,
    }
    write_json(receipt_json, {"archivist_receipt": archivist_receipt})
    write_text(
        receipt_md,
        f"# Command Commit `{event_id}`\n\n"
        f"- result: `{result}`\n"
        f"- worker_id: `{active_lease.get('ant_id', '')}`\n"
        f"- route_path: `{packet.route_state.get('route_path', '')}`\n"
        f"- t_sugar_ms: `{latency['t_sugar_ms']}`\n"
        f"- summary: `{summary or packet.change_summary}`\n",
    )

    packet.commit_state = {
        "result": result,
        "summary": summary or packet.change_summary,
        "artifact_paths": artifact_paths or [],
        "writeback_paths": writeback_paths or [],
        "work_started_at": started_at,
        "committed_at": committed_at,
        "restart_seed": restart_seed,
        "receipt_json": rel(receipt_json),
        "receipt_md": rel(receipt_md),
    }
    packet.status = "committed"
    packet.latency_state.update(
        {
            "detection_latency_ms": latency["detect_ms"],
            "detect_latency_ms": latency["detect_ms"],
            "encode_latency_ms": latency["encode_ms"],
            "awareness_latency_ms": latency["route_ms"],
            "claim_latency_ms": latency["claim_ms"],
            "resolution_latency_ms": latency["resolution_ms"],
            "commit_latency_ms": latency["commit_ms"],
            "t_sugar_ms": latency["t_sugar_ms"],
            "liminal_delta": latency["liminal_distance"],
            "liminal_velocity": latency["liminal_velocity"],
            "DeltaTau": latency["liminal_distance"],
            "LiminalVelocity": latency["liminal_velocity"],
        }
    )
    self.save_event(packet)

    finished = dict(active_lease)
    finished["status"] = "committed"
    finished["released_at"] = committed_at
    finished["release_reason"] = result
    leases.setdefault("history", []).append(finished)
    leases["active"].pop(event_id, None)
    self.save_leases(leases)

    board_status = "done" if result == "success" else "queued" if result in {"partial", "rerouted"} else "blocked"
    swarm_board.create_or_update_claim(
        agent=str(active_lease.get("ant_id", "")),
        front=f"{packet.source_id or 'command_root'}::{event_id}",
        level="command-event",
        output_target=packet.source_path,
        receipt=rel(receipt_md),
        status=board_status,
        message=summary or f"Committed `{event_id}` as `{result}`.",
        paths=[packet.source_path, rel(receipt_json), rel(receipt_md)],
        claim_id=active_lease.get("board_claim_id") or None,
    )

    state = self.load_state()
    state["last_committed_event_id"] = event_id
    self.save_state(state)
    self.sync_public_surfaces(event_id=event_id)
    return {
        "event_id": event_id,
        "result": result,
        "latency": latency,
        "archivist_receipt": archivist_receipt,
        "receipt_json": rel(receipt_json),
        "receipt_md": rel(receipt_md),
    }


def _command_membrane_v1_reinforce_event(
    self: CommandMembraneService,
    event_id: str,
    path: str | None = None,
    result: str = "success",
    latency_score: float = 0.90,
) -> dict[str, Any]:
    packet = self.load_event(event_id)
    route_path = path or str(packet.route_state.get("route_path") or "")
    if not route_path:
        raise ValueError(f"Event `{event_id}` has no route to reinforce.")
    nodes = [node for node in route_path.split(">") if node]
    if len(nodes) < 2:
        raise ValueError(f"Route path `{route_path}` is too short to reinforce.")

    edges_payload = self.load_edges()
    updated_edges: list[dict[str, Any]] = []
    total_delta = 0.0
    latency_score = self.clamp01(latency_score)
    usefulness = {"success": 1.0, "partial": 0.65, "blocked": 0.35}.get(result, 0.15)
    noise_penalty = 1.0 if result in {"duplicate", "noise", "ignored"} else 0.0
    latency_penalty = self.clamp01(1.0 - latency_score)
    for idx in range(len(nodes) - 1):
        src = nodes[idx]
        dst = nodes[idx + 1]
        edge_id = f"{src}>{dst}"
        existing = edges_payload.setdefault("edges", {}).get(edge_id, {})
        previous_strength = float(existing.get("strength", existing.get("edge_strength", 0.25)) or 0.25)
        prior_use_count = int(existing.get("use_count", 0))
        previous_success_count = int(existing.get("success_count", 0))
        previous_failure_count = int(existing.get("failure_count", 0))
        success_count = previous_success_count + (1 if result == "success" else 0)
        failure_count = previous_failure_count + (0 if result == "success" else 1)
        frequency = self.clamp01(success_count / 3.0)
        edge_strength = round(
            self.clamp01(
                (self.config.rho * previous_strength)
                + (self.config.alpha * usefulness)
                + (self.config.beta * frequency)
                - (self.config.gamma * latency_penalty)
                - (self.config.delta * noise_penalty)
            ),
            6,
        )
        classification = "vein" if edge_strength >= 0.70 else "capillary" if edge_strength >= 0.35 else "route"
        average_latency_score = round(
            ((float(existing.get("average_latency_score", 0.0)) * prior_use_count) + float(latency_score)) / max(prior_use_count + 1, 1),
            6,
        )
        edge = CapillaryEdgeV1(
            edge_id=edge_id,
            from_node=src,
            to_node=dst,
            path_key=edge_id,
            edge_strength=edge_strength,
            classification=classification,
            success_count=success_count,
            use_count=prior_use_count + 1,
            noise_count=int(existing.get("noise_count", 0)) + (1 if noise_penalty else 0),
            average_latency_score=average_latency_score,
            last_result=result,
            last_event_id=event_id,
            last_updated=utc_now(),
            golden_pheromone=edge_strength,
            bridge_pheromone=0.0,
            average_heaven_verified=0.0,
            evaporation_rate=self.config.rho,
            last_reward_total=usefulness,
            last_crown="none",
            crown_count=int(existing.get("crown_count", 0)),
            src=src,
            dst=dst,
            strength=edge_strength,
            state_class=classification,
            grade=classification,
            ema_latency_ms=round((1.0 - float(latency_score)) * 1000.0, 3),
            rho=self.config.rho,
            alpha=self.config.alpha,
            beta=self.config.beta,
            gamma=self.config.gamma,
            delta=self.config.delta,
            usefulness=usefulness,
            frequency=frequency,
            latency_penalty=latency_penalty,
            noise_penalty=noise_penalty,
            last_reinforced_at_utc=utc_now(),
            tier=classification,
            source_ant_id=src,
            target_ant_id=dst,
            front_ref=packet.front_ref,
        )
        edges_payload["edges"][edge_id] = asdict(edge)
        updated_edges.append(asdict(edge))
        total_delta += edge_strength - previous_strength

    capillary_score = max((float(edge["edge_strength"]) for edge in updated_edges), default=0.0)
    edges_payload.setdefault("history", []).append(
        {
            "event_id": event_id,
            "path": route_path,
            "result": result,
            "latency_score": round(latency_score, 6),
            "capillary_delta": round(total_delta, 6),
            "updated_at": utc_now(),
        }
    )
    self.save_edges(edges_payload)
    packet.latency_state["capillary_score"] = capillary_score
    packet.latency_state["capillary_delta"] = round(total_delta, 6)
    packet.latency_state["route_tier"] = "vein" if capillary_score >= 0.70 else "capillary" if capillary_score >= 0.35 else "route"
    self.save_event(packet)
    self.sync_public_surfaces(event_id=event_id)
    return {
        "event_id": event_id,
        "path": route_path,
        "edges": updated_edges,
        "capillary_score": capillary_score,
        "capillary_delta": round(total_delta, 6),
    }


def _command_membrane_v1_metrics(self: CommandMembraneService, surface: str = "command-folder") -> dict[str, Any]:
    del surface
    events = self.recent_event_payloads(limit=None)
    committed = [event for event in events if event.get("commit_state")]
    edges = self.load_edges().get("edges", {})
    tier_counts = {"route": 0, "capillary": 0, "vein": 0}
    for edge in edges.values():
        classification = str(edge.get("classification", edge.get("state_class", "route")))
        if classification not in tier_counts:
            classification = "route"
        tier_counts[classification] += 1

    def average(values: list[float]) -> float:
        return round(sum(values) / max(len(values), 1), 3) if values else 0.0

    return {
        "surface": "command-folder",
        "docs_gate_status": self.docs_gate_status()["state"],
        "event_count": len(events),
        "committed_count": len(committed),
        "active_leases": len(self.load_leases().get("active", {})),
        "average_detection_latency_ms": average([float((event.get("latency_state") or {}).get("detect_latency_ms", (event.get("latency_state") or {}).get("detection_latency_ms", 0.0))) for event in committed]),
        "average_awareness_latency_ms": average([float((event.get("latency_state") or {}).get("awareness_latency_ms", 0.0)) for event in committed]),
        "average_claim_latency_ms": average([float((event.get("latency_state") or {}).get("claim_latency_ms", 0.0)) for event in committed]),
        "average_resolution_latency_ms": average([float((event.get("latency_state") or {}).get("resolution_latency_ms", 0.0)) for event in committed]),
        "average_commit_latency_ms": average([float((event.get("latency_state") or {}).get("commit_latency_ms", 0.0)) for event in committed]),
        "average_t_sugar_ms": average([float((event.get("latency_state") or {}).get("t_sugar_ms", 0.0)) for event in committed]),
        "capillary_tiers": tier_counts,
        "top_capillaries": sorted(
            ({"edge_id": edge_id, "edge_strength": float(edge.get("edge_strength", edge.get("strength", 0.0))), "classification": edge.get("classification", edge.get("state_class", "route"))} for edge_id, edge in edges.items()),
            key=lambda item: (-item["edge_strength"], item["edge_id"]),
        )[:5],
        "last_event_id": events[0].get("event_id", "") if events else "",
    }


def _command_v2_packet_to_summary(self: CommandMembraneService, packet: CommandEventPacketV2) -> dict[str, Any]:
    return {
        "event_id": packet.event_id,
        "source_path": packet.source_path,
        "change_type": packet.change_type,
        "change_summary": packet.change_summary,
        "goal": packet.goal,
        "priority": packet.priority,
        "confidence": packet.confidence,
        "status": packet.status,
        "route_targets": packet.route_targets,
        "linked_quests": packet.linked_quests,
        "route_state": packet.route_state,
        "claim_state": packet.claim_state,
        "commit_state": packet.commit_state,
        "latency_state": packet.latency_state,
        "reward_state": packet.reward_state,
        "verification_state": packet.verification_state,
        "pheromone_state": packet.pheromone_state,
        "reward_policy_id": packet.reward_policy_id,
        "crown_tier": packet.crown_tier,
        "closure_class": packet.closure_class,
        "replay_ptr": packet.replay_ptr,
    }


def _command_v2_stage_effort_quality(self: CommandMembraneService, stage: str, result: str) -> float:
    del self
    result_key = result.lower().strip()
    if result_key in {"duplicate", "noise", "expired", "unverified", "failed"}:
        return 0.0
    if stage == "detect":
        return 0.25
    if stage == "route":
        return 0.50
    if stage == "claim":
        return 0.75
    if result_key == "success":
        return 1.0
    if result_key in {"blocked", "quarantined"}:
        return 1.0
    if result_key in {"assist", "partial"}:
        return 0.75
    return 0.0


def _command_v2_verification_defaults(
    self: CommandMembraneService,
    stage: str,
    result: str,
    *,
    crown_eligible: bool = True,
    verification_witness_cap: float = 1.0,
) -> CommandVerificationStateV2:
    del self
    result_key = result.lower().strip()
    if stage == "detect":
        witness, basis, closure_class = 0.25, "detect persisted", "first_detect"
    elif stage == "route":
        witness, basis, closure_class = 0.50, "route persisted", "first_route"
    elif stage == "claim":
        witness, basis, closure_class = 0.75, "active lease / act started", "first_act"
    elif result_key == "success":
        witness, basis, closure_class = 1.0, "full verified closure with archivist commit", "full_verified_closure"
    elif result_key == "blocked":
        witness, basis, closure_class = 0.70, "truthful blocked attempt", "meaningful_blocked_attempt"
    elif result_key == "quarantined":
        witness, basis, closure_class = 0.70, "truthful quarantined attempt", "meaningful_blocked_attempt"
    elif result_key == "partial":
        witness, basis, closure_class = 0.75, "assist with useful contribution", "assist_with_useful_contribution"
    else:
        witness, basis, closure_class = 0.0, "unverified-or-dry", "duplicate_noise_unverified"
    witness = min(witness, verification_witness_cap)
    return CommandVerificationStateV2(
        verification_witness=round(max(0.0, witness), 6),
        verification_basis=basis,
        closure_class=closure_class,
        crown_eligible=bool(crown_eligible),
        verification_witness_cap=round(max(0.0, verification_witness_cap), 6),
    )


def _command_v2_route_mode_for_stage(
    self: CommandMembraneService,
    stage: str,
    result: str,
    verification_state: CommandVerificationStateV2,
) -> str:
    del self, result
    if verification_state.closure_class == "full_verified_closure":
        return "reinforce"
    if verification_state.closure_class == "meaningful_blocked_attempt":
        return "rotate"
    if verification_state.closure_class == "duplicate_noise_unverified":
        return "dry"
    if stage in {"detect", "route", "claim"} or verification_state.closure_class in {"assist_with_useful_contribution", "first_detect", "first_route", "first_act"}:
        return "rotate"
    return "reinforce"


def _command_v2_phi_for_stage(
    self: CommandMembraneService,
    stage: str,
    result: str,
    verification_state: CommandVerificationStateV2,
) -> float:
    del self, stage
    result_key = result.lower().strip()
    if verification_state.closure_class == "full_verified_closure":
        return 0.0
    if verification_state.closure_class == "meaningful_blocked_attempt":
        return round(-math.pi / 2.0, 6)
    if result_key in {"duplicate", "noise", "expired", "unverified", "failed"} or verification_state.closure_class == "duplicate_noise_unverified":
        return round(math.pi, 6)
    return round(math.pi / 2.0, 6)


def _command_v2_crown_tier_for_stage(
    self: CommandMembraneService,
    stage: str,
    result: str,
    verification_state: CommandVerificationStateV2,
) -> str:
    del self
    if not verification_state.crown_eligible:
        return "none"
    if verification_state.closure_class == "first_detect":
        return "detect"
    if verification_state.closure_class == "first_route":
        return "route"
    if verification_state.closure_class == "first_act":
        return "act"
    if verification_state.closure_class == "full_verified_closure" and verification_state.verification_witness >= 1.0:
        return "prime"
    return "none"


def _command_v2_first_reward_for_stage(self: CommandMembraneService, stage: str, crown_tier: str) -> float:
    if stage == "detect" and crown_tier == "detect":
        return self.config.crown_detect
    if stage == "route" and crown_tier == "route":
        return self.config.crown_route
    if stage == "claim" and crown_tier == "act":
        return self.config.crown_act
    if stage == "commit" and crown_tier == "prime":
        return self.config.crown_full
    return 0.0


def _command_v2_compose_reward_state(
    self: CommandMembraneService,
    *,
    stage: str,
    result: str,
    priority: float,
    confidence: float,
    effort_quality: float,
    tau_seconds: float,
    novelty_score: float,
    contribution_share: float,
    verification_state: CommandVerificationStateV2,
) -> CommandRewardStateV2:
    latency_score = math.exp(-1.0 * max(float(tau_seconds), 0.0))
    affect_intensity_a = round(
        math.pi
        * self.clamp01(
            (0.45 * float(priority))
            + (0.35 * float(confidence))
            + (0.20 * float(effort_quality))
        ),
        6,
    )
    affect_direction_phi = self.phi_for_stage(stage, result, verification_state)
    alignment_score = self.heaven_score(affect_intensity_a, affect_direction_phi)
    verified_alignment_score = round(alignment_score * verification_state.verification_witness, 6)
    reward_multiplier = self.reward_multiplier_for_heaven(verified_alignment_score)
    crown_tier = self.crown_tier_for_stage(stage, result, verification_state)
    return CommandRewardStateV2(
        affect_intensity_a=affect_intensity_a,
        affect_direction_phi=affect_direction_phi,
        alignment_score=alignment_score,
        verified_alignment_score=verified_alignment_score,
        reward_multiplier=reward_multiplier,
        attempt_reward=round(0.25 * float(effort_quality), 6),
        latency_reward=round(latency_score, 6),
        first_reward=round(self.first_reward_for_stage(stage, crown_tier), 6),
        assist_reward=round(0.50 * float(contribution_share), 6),
        learning_reward=round(0.50 * float(novelty_score), 6),
        total_reward=0.0,
        crown_tier=crown_tier,
        route_mode=self.route_mode_for_stage(stage, result, verification_state),
        tau_seconds=round(max(float(tau_seconds), 0.0), 6),
    )


def _command_v2_finalize_reward_state(self: CommandMembraneService, reward_state: CommandRewardStateV2) -> CommandRewardStateV2:
    del self
    reward_state.alignment_score = round(max(0.0, reward_state.alignment_score), 6)
    reward_state.verified_alignment_score = round(max(0.0, reward_state.verified_alignment_score), 6)
    reward_state.reward_multiplier = round(max(0.0, reward_state.reward_multiplier), 6)
    reward_state.total_reward = round(
        reward_state.reward_multiplier
        * (
            reward_state.attempt_reward
            + reward_state.latency_reward
            + reward_state.first_reward
            + reward_state.assist_reward
            + reward_state.learning_reward
        ),
        6,
    )
    return reward_state


def _command_v2_compose_pheromone_state(
    self: CommandMembraneService,
    reward_state: CommandRewardStateV2,
    contribution_share: float,
    average_verified_alignment_score: float = 0.0,
    gold_strength_after: float = 0.0,
    bridge_strength_after: float = 0.0,
    compat_edge_strength_after: float = 0.0,
) -> CommandPheromoneStateV2:
    return CommandPheromoneStateV2(
        gold_deposit=round(self.config.mu * reward_state.total_reward * float(contribution_share), 6),
        bridge_deposit=round(self.config.nu * reward_state.attempt_reward * (1.0 - reward_state.verified_alignment_score) * float(contribution_share), 6),
        evaporation_rate=round(self.config.rho_0 + self.config.rho_1 * (1.0 - float(average_verified_alignment_score)), 6),
        gold_strength_after=round(float(gold_strength_after), 6),
        bridge_strength_after=round(float(bridge_strength_after), 6),
        compat_edge_strength_after=round(float(compat_edge_strength_after), 6),
    )


def _command_v2_compose_reward_allocations(self: CommandMembraneService, total_reward: float, worker_id: str) -> list[dict[str, Any]]:
    del self
    allocations = [
        CommandRewardAllocationV2("scout", "SCOUT-01", ROLE_CONTRIBUTION_SHARES["Scout"], ROLE_CONTRIBUTION_SHARES["Scout"], round(float(total_reward) * ROLE_CONTRIBUTION_SHARES["Scout"], 6)),
        CommandRewardAllocationV2("router", "ROUTER-01", ROLE_CONTRIBUTION_SHARES["Router"], ROLE_CONTRIBUTION_SHARES["Router"], round(float(total_reward) * ROLE_CONTRIBUTION_SHARES["Router"], 6)),
        CommandRewardAllocationV2("worker", worker_id, ROLE_CONTRIBUTION_SHARES["Worker"], ROLE_CONTRIBUTION_SHARES["Worker"], round(float(total_reward) * ROLE_CONTRIBUTION_SHARES["Worker"], 6)),
        CommandRewardAllocationV2("archivist", "ARCHIVIST-01", ROLE_CONTRIBUTION_SHARES["Archivist"], ROLE_CONTRIBUTION_SHARES["Archivist"], round(float(total_reward) * ROLE_CONTRIBUTION_SHARES["Archivist"], 6)),
    ]
    return [asdict(item) for item in allocations]


def _command_v2_capillary_signals(self: CommandMembraneService, candidate: dict[str, Any]) -> tuple[float, float, float]:
    compat = float(candidate.get("compat_edge_strength", candidate.get("edge_strength", 0.0)) or 0.0)
    gold = float(candidate.get("gold_strength", candidate.get("gold_signal", compat)) or compat)
    bridge = float(candidate.get("bridge_strength", candidate.get("bridge_signal", 0.0)) or 0.0)
    return round(max(0.0, gold), 6), round(max(0.0, bridge), 6), round(max(0.0, compat), 6)


CommandMembraneService.packet_to_summary = _command_v2_packet_to_summary
CommandMembraneService.stage_effort_quality = _command_v2_stage_effort_quality
CommandMembraneService.verification_defaults = _command_v2_verification_defaults
CommandMembraneService.route_mode_for_stage = _command_v2_route_mode_for_stage
CommandMembraneService.phi_for_stage = _command_v2_phi_for_stage
CommandMembraneService.crown_tier_for_stage = _command_v2_crown_tier_for_stage
CommandMembraneService.first_reward_for_stage = _command_v2_first_reward_for_stage
CommandMembraneService.compose_reward_state = _command_v2_compose_reward_state
CommandMembraneService.finalize_reward_state = _command_v2_finalize_reward_state
CommandMembraneService.compose_pheromone_state = _command_v2_compose_pheromone_state
CommandMembraneService.compose_reward_allocations = _command_v2_compose_reward_allocations
CommandMembraneService.capillary_signals = _command_v2_capillary_signals


def _command_v2_write_live_writeback_surfaces(self: CommandMembraneService, protocol: dict[str, Any], reward: dict[str, Any], capillary: dict[str, Any]) -> None:
    hall_body = "\n".join(
        [
            "## NEXT57-H-COMMAND-MEMBRANE",
            "",
            f"- Quest id: `{COMMAND_HALL_QUEST_ID}`",
            "- Goal: route command events through a verified joy-gradient membrane where truthful closure, useful speed, helping, and learning all earn nectar.",
            f"- Routing policy: `{protocol['routing_defaults']['policy_id']}`",
            "- Crown law: the first verified full closure gets the prime crown.",
            "- Real attempts still earn nectar when the try is lawful and useful.",
        ]
    )
    temple_body = "\n".join(
        [
            "## NEXT57-T-COMMAND-LAW",
            "",
            f"- Quest id: `{COMMAND_TEMPLE_QUEST_ID}`",
            "- Heaven is the positive attractor.",
            "- The +/-90 degree poles are bridge states, not punishments.",
            "- No punishment ledger. Dry paths evaporate instead of being negatively scored.",
            f"- Reward law: `{reward['law_id']}`",
            f"- Capillary law: `{capillary['law_id']}`",
            f"- Docs gate: `{protocol['docs_gate_status']}`",
        ]
    )
    active_run_body = "\n".join(
        [
            "## COMMAND Membrane Joy-Gradient V2",
            "",
            f"- Protocol: `{protocol['protocol_id']}`",
            f"- Canonical surface: `{protocol['active_surface']}`",
            f"- Docs gate: `{protocol['docs_gate_status']}`",
            "- Runtime law: reward is strictly nonnegative and verification gates amplification.",
            "- Compatibility aliases only: `packet.pheromone`, `receipt.capillary_delta`, `edge.edge_strength`.",
            "- Crown rule: first verified full closure gets the crown.",
        ]
    )
    queue_body = "\n".join(
        [
            "## Command Membrane Queue",
            "",
            f"- Route policy: `{protocol['routing_defaults']['policy_id']}`",
            f"- Ranking terms: `{', '.join(protocol['routing_defaults']['ranking_terms'])}`",
            "- Duplicate awareness is nonnegative: crown eligibility drops, but no subtractive punishment is written.",
            "- Dryness is represented by low deposit plus faster evaporation.",
        ]
    )
    prompt_body = "\n".join(
        [
            "## Command Membrane Next Prompt",
            "",
            "1. Preserve the docs gate as `BLOCKED` unless OAuth reality changes.",
            "2. Route with nonnegative terms only: goal_fit, priority, gold_signal, bridge_signal, coord_proximity, freshness.",
            "3. Tie reward amplification to verified `H_prime = H * verification_witness`, never self-report.",
            "4. First verified full closure gets the crown; real attempts still earn nectar.",
        ]
    )
    patch_markdown_file(HALL_BOARD_PATH, MARKER_HALL, hall_body)
    patch_markdown_file(TEMPLE_BOARD_PATH, MARKER_TEMPLE, temple_body)
    patch_markdown_file(ACTIVE_RUN_PATH, MARKER_ACTIVE_RUN, active_run_body)
    patch_markdown_file(BUILD_QUEUE_PATH, MARKER_BUILD_QUEUE, queue_body)
    patch_markdown_file(NEXT_SELF_PROMPT_PATH, MARKER_NEXT_PROMPT, prompt_body)
    patch_markdown_file(
        LP57_PROTOCOL_PATH,
        MARKER_LP57_PROTOCOL,
        "\n".join(
            [
                "## LP57 Command Reward Field",
                "",
                "- Heaven is the positive attractor for command routing.",
                "- 90-degree poles are bridge states.",
                "- There is no punishment ledger; low-value paths dry by evaporation.",
                "- Reward amplification is computed from verified Heaven, not self-report.",
            ]
        ),
    )


def _command_v2_ensure_protocol_artifacts(self: CommandMembraneService) -> dict[str, Any]:
    docs_gate = self.docs_gate_status()
    runtime_truth = self.current_runtime_truth()
    public_caps = runtime_truth.get("visible_caps", {"hall": 8, "temple": 8})
    protocol = {
        "protocol_id": COMMAND_PROTOCOL_ID_V2,
        "command_version": "joy-gradient-v2",
        "canonical_authority": "NEXT57",
        "canonical_mode": "COMMAND_CANON_ROOT",
        "authority_mode": "sole_live_authority",
        "compatibility_role": "V1 readable for one transition cycle; V2 canonical",
        "docs_gate": docs_gate,
        "docs_gate_status": docs_gate["state"],
        "active_surface": rel(self.config.command_surface_root),
        "command_folder_root": rel(self.config.command_surface_root),
        "packet_schema_path": rel(self.config.packet_schema_json_path),
        "reward_field_path": rel(self.config.reward_field_json_path),
        "capillary_law_path": rel(self.config.capillary_law_json_path),
        "latency_benchmarks_path": rel(self.config.latency_benchmark_json_path),
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "feeder_stack": list(COMMAND_FEEDER_STACK),
        "pipeline": ["COMMAND FOLDER", "Scout", "Router", "Worker", "Archivist"],
        "routing_defaults": {
            "policy_id": JOY_ROUTE_POLICY,
            "ranking_terms": ["goal_fit", "priority", "gold_signal", "bridge_signal", "coord_proximity", "freshness"],
            "selector_terms": ["goal_fit", "priority", "gold_signal", "bridge_signal", "coord_proximity", "freshness"],
            "topk": self.config.topk,
            "claim_mode": self.config.claim_mode,
            "quorum": self.config.quorum,
            "ttl": self.config.ttl,
            "lease_ms": self.config.lease_ms,
            "duplicate_guard": {"crown_eligible": False, "verification_witness_cap": 0.25, "score_mode": "nonnegative"},
        },
        "public_caps": public_caps,
        "current_runtime_truth": runtime_truth,
        "compatibility_aliases": {
            "packet.pheromone": "compatibility-only alias for joy_seed.h_seed / verified reward shadow",
            "receipt.capillary_delta": "compatibility-only alias for max(0, gold_deposit + bridge_deposit)",
            "edge.edge_strength": "compatibility-only alias for compat_edge_strength",
        },
        "reward_principles": {
            "heaven": "positive attractor",
            "bridge_poles": "productive half-heaven bridge states",
            "hell": "dry and unfed, not punitive",
        },
    }
    schema = {
        "schema_id": COMMAND_PACKET_SCHEMA_ID_V2,
        "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
        "packet_blocks": ["reward_state", "verification_state", "pheromone_state"],
        "receipt_blocks": ["reward_state", "verification_state", "pheromone_state", "reward_allocations"],
        "coord12_labels": [
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
        ],
        "coord12_frame_groups": ["earth", "astro", "runtime", "liminal"],
        "packet_types": {
            "CommandEventPacketV2": {
                "required": [
                    "event_id",
                    "source_path",
                    "goal",
                    "priority",
                    "confidence",
                    "coord12",
                    "reward_state",
                    "verification_state",
                    "pheromone_state",
                    "pheromone",
                ],
                "compatibility_fields": ["joy_seed", "pheromone"],
                "blocks": ["reward_state", "verification_state", "pheromone_state"],
            },
            "CommandRouteDecisionV2": {
                "required": [
                    "event_id",
                    "policy_id",
                    "candidate_targets",
                    "selected_targets",
                    "score_breakdown",
                    "route_path",
                    "reward_policy_id",
                    "route_mode",
                    "crown_eligible",
                    "verification_witness_cap",
                ]
            },
            "CommandExecutionReceiptV2": {
                "required": [
                    "verification_witness",
                    "effort_quality",
                    "contribution_share",
                    "learning_novelty",
                    "verified_outcome_class",
                    "reward_state",
                    "verification_state",
                    "pheromone_state",
                    "reward_allocations",
                ]
            },
            "CommandReinforcementReceiptV2": {
                "required": [
                    "a_verified",
                    "phi_verified",
                    "h_raw",
                    "h_verified",
                    "reward_multiplier",
                    "try_reward",
                    "speed_reward",
                    "first_bonus",
                    "assist_reward",
                    "learn_reward",
                    "total_reward",
                    "gold_deposit",
                    "bridge_deposit",
                    "route_mode",
                    "crown",
                    "capillary_delta",
                    "reward_state",
                    "verification_state",
                    "pheromone_state",
                    "reward_allocations",
                    "edge_allocations",
                ]
            },
            "LatencySampleV2": {
                "required": [
                    "tau_seconds",
                    "alignment_score",
                    "verified_alignment_score",
                    "reward_multiplier",
                    "crown_tier",
                ]
            },
            "CapillaryEdgeV2": {
                "required": [
                    "golden_pheromone",
                    "bridge_pheromone",
                    "average_heaven_verified",
                    "evaporation_rate",
                    "last_reward_total",
                    "last_crown",
                    "crown_count",
                    "edge_strength",
                    "gold_strength",
                    "bridge_strength",
                    "compat_edge_strength",
                    "average_alignment_score",
                    "average_verified_alignment_score",
                    "reward_density",
                ]
            },
        },
        "compatibility_aliases": protocol["compatibility_aliases"],
    }
    reward = {
        "law_id": COMMAND_REWARD_FIELD_ID_V2,
        "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
        "nonnegative_reward_law": True,
        "positive_only_rule": {"negative_scores": False, "dryness_mode": "evaporation"},
        "runtime_aliases": {
            "alignment_score": "Heaven proximity H",
            "verified_alignment_score": "H_prime",
            "reward_multiplier": "nectar multiplier",
            "crown_tier": "crown result",
        },
        "formulas": {
            "affect_intensity_a": "a = pi * clamp(0,1, 0.45*priority + 0.35*confidence + 0.20*q_i)",
            "alignment_score": "H = (a/pi) * ((1 + cos(phi))/2)",
            "verified_alignment_score": "H_prime = H * verification_witness",
            "reward_multiplier": "min(64.0, 1 / (1 - H_prime + 0.01))",
            "attempt_reward": "0.25 * q_i",
            "latency_reward": "exp(-1.0 * tau_seconds)",
            "assist_reward": "0.5 * contribution_share",
            "learning_reward": "0.5 * novelty_score",
            "total_reward": "reward_multiplier * (attempt_reward + latency_reward + first_reward + assist_reward + learning_reward)",
        },
        "coefficients": {
            "epsilon": self.config.epsilon,
            "M_max": self.config.reward_clip,
            "alpha_try": self.config.reward_alpha,
            "beta_speed": self.config.reward_beta,
            "lambda_speed": self.config.reward_lambda,
            "gamma_assist": self.config.reward_gamma,
            "delta_learn": self.config.reward_delta,
            "J_star": self.config.crown_full,
            "J_d": self.config.crown_detect,
            "J_r": self.config.crown_route,
            "J_a": self.config.crown_act,
            "mu": self.config.mu,
            "nu": self.config.nu,
            "rho_0": self.config.rho_0,
            "rho_1": self.config.rho_1,
            "rho_b": self.config.rho_b,
            "bridge_weight": self.config.bridge_weight,
        },
        "reward_layers": {
            "HeavenRewardPolicyV1": {"status": "compatibility-layer", "negative_scores": False},
            "HeavenRewardPolicyV2": {"status": "canonical", "negative_scores": False},
        },
        "contribution_shares": ROLE_CONTRIBUTION_SHARES,
        "crown_rules": {"detect": "first persisted detect", "route": "first persisted route", "act": "first valid lease holder", "prime": "first verified successful closure"},
    }
    capillary = {
        "law_id": COMMAND_CAPILLARY_LAW_ID_V2,
        "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
        "nonnegative_capillary_law": True,
        "formulas": {
            "gold_strength_next": "gold_strength_next = (1 - evaporation_rate) * gold_strength + gold_deposit",
            "bridge_strength_next": "bridge_strength_next = (1 - 0.10) * bridge_strength + bridge_deposit",
            "compat_edge_strength": "compat_edge_strength = gold_strength_next + bridge_strength_next",
            "evaporation_rate": "0.05 + 0.20 * (1 - average_verified_alignment_score)",
        },
        "edge_classes": ["ephemeral", "capillary", "vein"],
        "compatibility_projection": {
            "packet.pheromone": "clamp(verified_alignment_score, 0, 1)",
            "receipt.capillary_delta": "max(0, gold_deposit + bridge_deposit)",
            "edge_strength": "compat_edge_strength",
        },
    }
    latency = {
        "benchmark_id": "NEXT57_COMMAND_LATENCY_BENCHMARKS_V2",
        "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
        "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "fields": ["tau_seconds", "alignment_score", "verified_alignment_score", "reward_multiplier", "crown_tier"],
        "docs_gate_status": docs_gate["state"],
    }
    write_json(self.config.protocol_json_path, protocol)
    write_json(self.config.packet_schema_json_path, schema)
    write_json(self.config.reward_field_json_path, reward)
    write_json(self.config.capillary_law_json_path, capillary)
    write_json(self.config.latency_benchmark_json_path, latency)
    write_json(
        self.config.protocol_v1_registry_path,
        {
            "protocol_id": "COMMAND_MEMBRANE_PROTOCOL_V1_COMPAT",
            "compatibility_role": "read-only compatibility mirror of V2 canonical law",
            "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
            "canonical_protocol_path": rel(self.config.protocol_json_path),
            "reward_layer": reward["reward_layers"],
            "docs_gate": docs_gate,
        },
    )
    write_text(self.config.command_manifest_path, "# NEXT 57 Command Sensory Membrane\n\n- Canonical law: `NEXT57_COMMAND_PROTOCOL_V2`\n- Mode: `joy-gradient-v2`\n- Heaven is the positive attractor.\n- Google Docs remains honestly blocked until OAuth artifacts exist.\n")
    write_text(self.config.protocol_manifest_path, "# NEXT 57 Command Protocol\n\n- Canonical protocol: `NEXT57_COMMAND_PROTOCOL_V2`\n- Routing is nonnegative and verification-gated.\n- First verified full closure gets the crown.\n- Compatibility aliases remain readable but are not canonical.\n")
    write_text(self.config.packet_manifest_path, "# NEXT 57 Command Packet Standard\n\n- Canonical packet schema: `NEXT57_COMMAND_EVENT_PACKET_V2`\n- Canonical packet blocks: `reward_state`, `verification_state`, `pheromone_state`.\n- Compatibility fields remain readable for one transition cycle: `joy_seed`, `packet.pheromone`.\n")
    write_text(self.config.capillary_manifest_path, "# NEXT 57 Command Capillary Law\n\n- Canonical law: `NEXT57_COMMAND_CAPILLARY_UPDATE_V2`\n- No negative reward is written; weak paths dry by evaporation.\n- Compatibility aliases: `receipt.capillary_delta`, `edge.edge_strength`.\n")
    write_text(self.config.latency_manifest_path, "# NEXT 57 Command Latency Benchmarks\n\n- Equation: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`\n- Reward amplification is computed from verified Heaven, not self-report.\n")
    write_text(self.config.reward_field_manifest_path, "# NEXT 57 Command Reward Field\n\n- Heaven is the positive attractor.\n- 90-degree poles are bridge states.\n- No punishment ledger.\n- Hell is dry and unfed, not punitive.\n- Trying still earns nectar when the attempt is real.\n- First verified full closure gets the crown.\n")
    write_text(self.config.protocol_v1_manifest_path, "# COMMAND Membrane Protocol V1\n\n- Compatibility role: `read-only compatibility mirror of V2 canonical law`.\n")
    self.write_live_writeback_surfaces(protocol, reward, capillary)
    self.sync_public_surfaces()
    return {"protocol": self.config.protocol_json_path, "schema": self.config.packet_schema_json_path, "reward": self.config.reward_field_json_path, "capillary": self.config.capillary_law_json_path, "latency": self.config.latency_benchmark_json_path}


def _command_v2_emit_change(
    self: CommandMembraneService,
    source_path: Path,
    change_type: str,
    detected_ts: str,
    confidence: float = 0.98,
    parent_event_id: str = "ROOT",
    state: dict[str, Any] | None = None,
    source_ids: Iterable[str] | None = None,
) -> CommandEventPacketV2 | None:
    self.ensure_protocol_artifacts()
    mutable_state = state or self.load_state()
    normalized_path = Path(source_path).resolve(strict=False)
    ignore_reason = self.ignored_reason(normalized_path)
    if ignore_reason:
        return None
    source_descriptor = self.source_descriptor_for_path(normalized_path, source_ids=source_ids) or {
        "source_id": "command_root",
        "source_class": "command-folder",
        "absolute_path": str(self.config.command_surface_root),
        "routing_goal": "detect-classify-assign",
        "urgency_baseline": 0.90,
        "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND", "Hs": "command-event", "Ns": "COMMAND"},
    }
    event_seq = int(mutable_state.get("last_event_seq", 0) or 0) + 1
    event_id = f"CMD-{event_seq:06d}"
    source_id = str(source_descriptor.get("source_id") or "command_root")
    source_class = str(source_descriptor.get("source_class") or "command-folder")
    relative_path = rel(normalized_path)
    file_family = self.file_family_for_path(normalized_path)
    source_mtime_ns = float(normalized_path.stat().st_mtime_ns if normalized_path.exists() else 0.0)
    state_hash = hashlib.sha1(f"{relative_path}|{change_type}|{source_mtime_ns}|{event_seq}".encode("utf-8")).hexdigest()
    docs_gate = self.docs_gate_status()
    priority = round(
        self.clamp01(
            float(source_descriptor.get("urgency_baseline", 0.90))
            + (0.05 if file_family == "code" else 0.0)
            + (0.03 if any(token in normalized_path.name.lower() for token in ("protocol", "schema", "ledger", "manifest")) else 0.0)
        ),
        6,
    )
    confidence = round(float(confidence), 6)
    now_utc = parse_iso(detected_ts)
    joy_seed = self.build_joy_seed(
        priority=priority,
        confidence=confidence,
        change_type=change_type,
        source_path=relative_path,
        source_class=source_class,
    )
    coord12 = {
        "earth_utc_anchor": detected_ts,
        "earth_rotation_phase": local_rotation_phase(now_utc, LOCAL_ZONE),
        "earth_orbital_phase": orbital_phase(now_utc),
        "earth_geospatial_anchor": self.config.earth_geo_anchor,
        "solar_phase": self.shared12_ratio(self.scheduler_lane("western_solar12")),
        "lunar_phase": lunar_phase(now_utc),
        "local_sidereal_phase": sidereal_phase(now_utc),
        "canonical_sky_anchor": "western_solar12|planetary_office|vedic_lunar",
        "runtime_region": self.config.runtime_region,
        "queue_pressure": self.queue_pressure(),
        "goal_salience_vector": {"goal": str(source_descriptor.get("routing_goal", "detect-classify-assign")), "priority": priority},
        "change_novelty_vector": {"change_type": change_type, "confidence": confidence},
    }
    coord12_frame = {
        "earth": list(coord12.keys())[:4],
        "astro": list(coord12.keys())[4:8],
        "runtime": list(coord12.keys())[8:10],
        "liminal": list(coord12.keys())[10:12],
    }
    vector12 = [self.coord12_scalar(value) for value in coord12.values()]
    verification_state = self.verification_defaults("detect", "observe", crown_eligible=True, verification_witness_cap=1.0)
    reward_state = self.finalize_reward_state(
        self.compose_reward_state(
            stage="detect",
            result="observe",
            priority=priority,
            confidence=confidence,
            effort_quality=self.stage_effort_quality("detect", "observe"),
            tau_seconds=0.0,
            novelty_score=1.0,
            contribution_share=ROLE_CONTRIBUTION_SHARES["Scout"],
            verification_state=verification_state,
        )
    )
    pheromone_state = self.compose_pheromone_state(
        reward_state,
        ROLE_CONTRIBUTION_SHARES["Scout"],
        reward_state.verified_alignment_score,
    )
    absolute_surface = Path(str(source_descriptor.get("absolute_path") or self.config.command_surface_root))
    packet = CommandEventPacketV2(
        event_id=event_id,
        source_ant_id="SCOUT-01",
        source_path=relative_path,
        active_surface=rel(absolute_surface),
        change_type=change_type,
        change_summary=f"{change_type}:{normalized_path.name}",
        goal=str(source_descriptor.get("routing_goal") or "detect-classify-assign"),
        priority=priority,
        confidence=confidence,
        earth_ts=detected_ts,
        earth_ts_local=now_utc.astimezone(LOCAL_ZONE).isoformat(),
        detected_ts=detected_ts,
        emitted_ts=utc_now(),
        liminal_ts=utc_now(),
        seat_addr_6d="A1.B1.C1.D1.E1.F1",
        coordinate_stamp={
            "Xs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Xs", "GLOBAL_COMMAND")),
            "Ys": source_id,
            "Zs": normalized_path.name,
            "Ts": self.active_loop_id(),
            "Qs": "COMMAND",
            "Rs": "D1",
            "Cs": event_id,
            "Fs": "Flower",
            "Ms": joy_seed["route_mode_seed"],
            "Ns": str(event_seq),
            "Hs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Hs", "command-event")),
            "Ωs": "A1",
        },
        canonical_addr_6d="A1.B1.C1.D1.E1.F1",
        liminal_stamp_12d=coord12,
        surface_class=source_class,
        hierarchy_level="D6",
        return_anchor="Archivist",
        earth_ts_utc=detected_ts,
        parent_event_id=parent_event_id,
        ttl=self.config.ttl,
        pheromone=joy_seed["h_seed"],
        joy_seed=joy_seed,
        state_hash=state_hash,
        route_class=COMMAND_ROUTE_CLASS,
        witness_class=docs_gate["witness_class"],
        membrane_id="GLOBAL_COMMAND",
        role_class="Scout",
        base4_addr="A1.B1.C1.D1",
        parent=parent_event_id,
        lineage={
            "parent_event_id": parent_event_id,
            "source_mtime_ns": source_mtime_ns,
            "docs_gate_detail": docs_gate["detail"],
            "loop_id": self.active_loop_id(),
            "surface": rel(absolute_surface),
            "source_id": source_id,
            "source_class": source_class,
        },
        coord12=coord12,
        coord12_frame=coord12_frame,
        coord_delta={"DeltaTau": 0.0, "DeltaEarth": 0.0, "LiminalVelocity": 0.0},
        scout_id="SCOUT-01",
        tag=slugify(normalized_path.stem),
        event_tag=event_id,
        change={"type": change_type, "summary": f"{change_type}:{normalized_path.name}", "state_hash": state_hash},
        docs_gate_status=docs_gate["state"],
        latency_state={"detect_latency_ms": 0.0, "encode_latency_ms": 0.0, "route_policy": JOY_ROUTE_POLICY},
        affected_nodes=[relative_path],
        replay_ptr=rel(self.event_path(event_id)),
        coordinate_vector_12=vector12,
        artifact_refs=[relative_path],
        source_region=source_class,
        sensor_event_id=event_id,
        file_family=file_family,
        scheduler_refs=self.scheduler_refs_payload(),
        hsigma_ref=rel(self.config.hsigma_bundle_path),
        route_targets=[],
        linked_quests=[],
        source_folder="GLOBAL COMMAND",
        front_ref=COMMAND_ACTIVE_MEMBRANE,
        seed_mode="A-dominant",
        dual_reference=f"{SEED_A_REF}|{SEED_B_REF}",
        liminal_delta=0.0,
        earth_delta_ms=0.0,
        liminal_velocity=0.0,
        prior_comparable_event_id=str(mutable_state.get("last_event_id", "")),
        watcher_mode=COMMAND_WATCHER_MODE,
        duality_effect="joy-gradient-command",
        reward_state=asdict(reward_state),
        verification_state=asdict(verification_state),
        pheromone_state=asdict(pheromone_state),
        reward_policy_id=JOY_REWARD_POLICY,
        crown_tier=reward_state.crown_tier,
        closure_class=verification_state.closure_class,
        source_id=source_id,
        source_class=source_class,
        watch_root=str(source_descriptor.get("watch_root") or absolute_surface.parent),
        urgency_baseline=float(source_descriptor.get("urgency_baseline", 0.90)),
        event_fingerprint=state_hash[:16],
    )
    self.save_event(packet)
    sensor_log = self.load_sensor_events()
    sensor_log.append({"event_id": event_id, "source_path": relative_path, "change_type": change_type, "detected_ts": detected_ts})
    self.save_sensor_events(sensor_log)
    mutable_state["last_event_seq"] = event_seq
    mutable_state["last_event_id"] = event_id
    mutable_state["last_coord12_vector"] = vector12
    mutable_state["last_earth_ts"] = detected_ts
    mutable_state.setdefault("known_files", {})[relative_path] = {
        "state_hash": state_hash,
        "change_type": change_type,
        "detected_ts": detected_ts,
    }
    self.save_state(mutable_state)
    self.sync_public_surfaces(event_id=event_id)
    return packet


def _command_v2_score_candidate(self: CommandMembraneService, packet: CommandEventPacketV2, candidate: dict[str, Any]) -> dict[str, Any]:
    joy_seed = packet.joy_seed or self.build_joy_seed(
        priority=float(packet.priority),
        confidence=float(packet.confidence),
        change_type=packet.change_type,
        source_path=packet.source_path,
        source_class=packet.source_class,
    )
    gold_signal, bridge_signal, _ = self.capillary_signals(candidate)
    goal_fit = round(max(0.0, self.goal_match_score(packet, candidate)), 6)
    priority_score = round(max(0.0, float(packet.priority)), 6)
    coord_proximity = round(max(0.0, self.coordinate_match_score(packet, candidate)), 6)
    freshness = round(max(0.0, 1.0 - float(candidate.get("load", 0.0) or 0.0)), 6)
    score = round(goal_fit + priority_score + gold_signal + bridge_signal + coord_proximity + freshness, 6)
    return {
        **candidate,
        "goal_fit": goal_fit,
        "priority_score": priority_score,
        "gold_signal": gold_signal,
        "bridge_signal": bridge_signal,
        "coord_proximity": coord_proximity,
        "freshness": freshness,
        "joy_seed_score": round(max(0.0, float(joy_seed.get("h_seed", packet.pheromone))), 6),
        "score": score,
    }


def _command_v2_route_event(self: CommandMembraneService, event_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    self.release_expired_leases()
    packet = self.load_event(event_id)
    if packet.route_state and packet.route_state.get("policy_id") == JOY_ROUTE_POLICY:
        return packet.route_state
    scored = [self.score_candidate(packet, candidate) for candidate in self.active_candidates()]
    scored = [candidate for candidate in scored if candidate.get("activation_state") == "ACTIVE"]
    scored.sort(key=lambda item: (-item["score"], item["ant_id"]))
    selected = [candidate for candidate in scored if not candidate.get("blocked") and not candidate.get("leased")][: self.config.topk]
    if not selected:
        selected = scored[: self.config.topk]
    if not selected:
        raise ValueError("No active command candidates are available for routing.")
    worker_choice = next((candidate for candidate in selected if candidate.get("master_agent_id") == "A3"), selected[0])
    crown_eligible = not bool(worker_choice.get("leased"))
    verification_cap = 1.0 if crown_eligible else 0.25
    decision = CommandRouteDecisionV2(
        event_id=event_id,
        policy_id=JOY_ROUTE_POLICY,
        candidate_targets=[
            {
                "ant_id": candidate["ant_id"],
                "role": candidate.get("role_tag", ""),
                "score": candidate["score"],
                "goal_fit": candidate["goal_fit"],
                "priority": candidate["priority_score"],
                "gold_signal": candidate["gold_signal"],
                "bridge_signal": candidate["bridge_signal"],
                "coord_proximity": candidate["coord_proximity"],
                "freshness": candidate["freshness"],
                "blocked": bool(candidate.get("blocked")),
                "leased": bool(candidate.get("leased")),
            }
            for candidate in scored[: max(self.config.topk, 8)]
        ],
        selected_targets=[candidate["ant_id"] for candidate in selected],
        topk=self.config.topk,
        claim_mode=self.config.claim_mode,
        quorum=self.config.quorum,
        score_breakdown={
            candidate["ant_id"]: {
                "goal_fit": candidate["goal_fit"],
                "priority": candidate["priority_score"],
                "gold_signal": candidate["gold_signal"],
                "bridge_signal": candidate["bridge_signal"],
                "coord_proximity": candidate["coord_proximity"],
                "freshness": candidate["freshness"],
            }
            for candidate in selected
        },
        duplicate_risk=0.0 if crown_eligible else 1.0,
        created_at=utc_now(),
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=15)).isoformat(),
        ranked_routes=[{"ant_id": candidate["ant_id"], "master_agent_id": candidate.get("master_agent_id", ""), "score": candidate["score"]} for candidate in selected],
        route_inputs={
            "goal_fit": worker_choice["goal_fit"],
            "priority": worker_choice["priority_score"],
            "gold_signal": worker_choice["gold_signal"],
            "bridge_signal": worker_choice["bridge_signal"],
            "coord_proximity": worker_choice["coord_proximity"],
            "freshness": worker_choice["freshness"],
        },
        route_path=f"SCOUT-01>ROUTER-01>{worker_choice['ant_id']}>ARCHIVIST-01",
        worker_choice=worker_choice["ant_id"],
        generated_at=utc_now(),
        quest_refs=[COMMAND_TEMPLE_QUEST_ID] if any(keyword in packet.source_path.lower() for keyword in ("schema", "protocol", "ledger", "manifest")) else [COMMAND_HALL_QUEST_ID],
        reward_policy_id=JOY_REWARD_POLICY,
        route_mode="rotate",
        crown_eligible=crown_eligible,
        verification_witness_cap=verification_cap,
        reward_inputs={"priority": packet.priority, "confidence": packet.confidence, "effort_quality": self.stage_effort_quality("route", "observe")},
    )
    verification_state = self.verification_defaults("route", "observe", crown_eligible=crown_eligible, verification_witness_cap=verification_cap)
    reward_state = self.finalize_reward_state(self.compose_reward_state(stage="route", result="observe", priority=packet.priority, confidence=packet.confidence, effort_quality=self.stage_effort_quality("route", "observe"), tau_seconds=max(self.ms_between(packet.detected_ts, decision.generated_at) / 1000.0, 0.0), novelty_score=1.0, contribution_share=ROLE_CONTRIBUTION_SHARES["Router"], verification_state=verification_state))
    pheromone_state = self.compose_pheromone_state(reward_state, ROLE_CONTRIBUTION_SHARES["Router"], reward_state.verified_alignment_score)
    packet.route_state = asdict(decision)
    packet.route_targets = decision.selected_targets
    packet.linked_quests = decision.quest_refs
    packet.status = "routed"
    packet.reward_state = asdict(reward_state)
    packet.verification_state = asdict(verification_state)
    packet.pheromone_state = asdict(pheromone_state)
    packet.reward_policy_id = JOY_REWARD_POLICY
    packet.pheromone = clamp(reward_state.verified_alignment_score, 0.0, 1.0)
    packet.crown_tier = reward_state.crown_tier
    packet.closure_class = verification_state.closure_class
    packet.latency_state["awareness_latency_ms"] = round(self.ms_between(packet.detected_ts, decision.generated_at), 3)
    self.save_event(packet)
    if state is not None:
        state["last_routed_event_id"] = event_id
        self.save_state(state)
    self.sync_public_surfaces(event_id=event_id)
    return asdict(decision)


def _command_v2_metrics(self: CommandMembraneService, surface: str = "command-folder") -> dict[str, Any]:
    del surface
    events = self.recent_event_payloads(limit=None)
    committed = [event for event in events if event.get("commit_state")]
    edges = self.load_edges().get("edges", {})
    def average(values: list[float]) -> float:
        return round(sum(values) / max(len(values), 1), 3) if values else 0.0
    return {
        "generated_at": utc_now(),
        "protocol_id": COMMAND_PROTOCOL_ID_V2,
        "command_root": rel(self.config.command_surface_root),
        "docs_gate_status": self.docs_gate_status()["state"],
        "event_count": len(events),
        "committed_count": len(committed),
        "active_leases": len(self.load_leases().get("active", {})),
        "average_verified_alignment_score": average([float((event.get("reward_state") or {}).get("verified_alignment_score", 0.0)) for event in committed]),
        "average_total_reward": average([float((event.get("reward_state") or {}).get("total_reward", 0.0)) for event in committed]),
        "average_t_sugar_ms": average([float((event.get("latency_state") or {}).get("t_sugar_ms", 0.0)) for event in committed]),
        "crown_count": sum(1 for event in committed if str((event.get("reward_state") or {}).get("crown_tier", "none")) != "none"),
        "top_capillaries": sorted(({"edge_id": edge_id, "edge_strength": float(edge.get("compat_edge_strength", edge.get("edge_strength", 0.0))), "classification": edge.get("classification", edge.get("grade", "route"))} for edge_id, edge in edges.items()), key=lambda item: (-item["edge_strength"], item["edge_id"]))[:5],
    }


CommandMembraneService.write_live_writeback_surfaces = _command_v2_write_live_writeback_surfaces
CommandMembraneService.ensure_protocol_artifacts = _command_v2_ensure_protocol_artifacts
CommandMembraneService.emit_change = _command_v2_emit_change
CommandMembraneService.score_candidate = _command_v2_score_candidate
CommandMembraneService.route_event = _command_v2_route_event
CommandMembraneService.metrics = _command_v2_metrics


def _command_v2_claim_event(self: CommandMembraneService, event_id: str, ant_id: str | None = None, role: str = "worker", lease_ms: int | None = None) -> dict[str, Any]:
    self.release_expired_leases()
    packet = self.load_event(event_id)
    if packet.claim_state and packet.claim_state.get("status") == "active":
        return packet.claim_state
    if not packet.route_state:
        self.route_event(event_id)
        packet = self.load_event(event_id)
    leases = self.load_leases()
    if event_id in leases.get("active", {}):
        return leases["active"][event_id]
    candidate_map = {candidate["ant_id"]: candidate for candidate in self.active_candidates()}
    chosen_ant = ant_id or str(packet.route_state.get("worker_choice") or "")
    candidate = candidate_map.get(chosen_ant)
    if candidate is None:
        fallback = next((item for item in self.active_candidates() if item.get("master_agent_id") == "A3"), None)
        if fallback is None:
            raise ValueError("No lawful worker is available to claim the event.")
        chosen_ant = str(fallback["ant_id"])
        candidate = fallback
    claimed_at_dt = datetime.now(timezone.utc)
    lease_duration = int(lease_ms or self.config.lease_ms)
    expires_at_dt = claimed_at_dt + timedelta(milliseconds=lease_duration)
    receipt_json, receipt_md = self.receipt_paths(event_id)
    board_claim = swarm_board.create_or_update_claim(agent=chosen_ant, front=f"{packet.source_id or 'command_root'}::{event_id}", level="command-event", output_target=packet.source_path, receipt=rel(receipt_md), status="active", message=f"Leased `{event_id}` for `{packet.change_summary}`.", paths=[packet.source_path, rel(self.event_path(event_id)), rel(receipt_json), rel(receipt_md)], claim_id=packet.claim_state.get("board_claim_id") or None)
    lease = CommandClaimLeaseV1(claim_id=swarm_board.make_object_id("CLM", chosen_ant, event_id), event_id=event_id, ant_id=chosen_ant, role=role, lease_ms=lease_duration, claimed_at=claimed_at_dt.isoformat(), expires_at=expires_at_dt.isoformat(), status="active", claim_status="active", owner_surface=packet.source_class or "command-folder", board_claim_id=board_claim["claim_id"], role_class=str(candidate.get("role_tag", role)), claim_mode=self.config.claim_mode, claimed_at_utc=claimed_at_dt.isoformat(), expires_at_utc=expires_at_dt.isoformat(), route_class=packet.route_class, front_ref=f"{packet.source_id or 'command_root'}::{event_id}", seed_mode=packet.seed_mode, dual_reference=packet.dual_reference)
    leases.setdefault("active", {})[event_id] = asdict(lease)
    self.save_leases(leases)
    verification_state = self.verification_defaults("claim", "observe", crown_eligible=True, verification_witness_cap=1.0)
    reward_state = self.finalize_reward_state(self.compose_reward_state(stage="claim", result="observe", priority=packet.priority, confidence=packet.confidence, effort_quality=self.stage_effort_quality("claim", "observe"), tau_seconds=max(self.ms_between(packet.route_state.get("generated_at", packet.detected_ts), lease.claimed_at) / 1000.0, 0.0), novelty_score=0.5, contribution_share=ROLE_CONTRIBUTION_SHARES["Worker"], verification_state=verification_state))
    pheromone_state = self.compose_pheromone_state(reward_state, ROLE_CONTRIBUTION_SHARES["Worker"], reward_state.verified_alignment_score)
    packet.claim_state = {"status": "active", "claim_id": lease.claim_id, "ant_id": chosen_ant, "board_claim_id": board_claim["claim_id"], "claimed_at": lease.claimed_at, "expires_at": lease.expires_at, "route_path": packet.route_state.get("route_path", ""), "role": role}
    packet.status = "claimed"
    packet.reward_state = asdict(reward_state)
    packet.verification_state = asdict(verification_state)
    packet.pheromone_state = asdict(pheromone_state)
    packet.reward_policy_id = JOY_REWARD_POLICY
    packet.pheromone = clamp(reward_state.verified_alignment_score, 0.0, 1.0)
    packet.crown_tier = reward_state.crown_tier
    packet.closure_class = verification_state.closure_class
    packet.latency_state["claim_latency_ms"] = round(self.ms_between(packet.route_state.get("generated_at", packet.detected_ts), lease.claimed_at), 3)
    self.save_event(packet)
    self.sync_public_surfaces(event_id=event_id)
    return packet.claim_state


def _command_v2_commit_event(self: CommandMembraneService, event_id: str, result: str, artifact_paths: list[str] | None = None, writeback_paths: list[str] | None = None, summary: str = "", work_started_at: str | None = None) -> dict[str, Any]:
    packet = self.load_event(event_id)
    if packet.commit_state and packet.commit_state.get("committed_at"):
        return packet.commit_state
    leases = self.load_leases()
    active_lease = leases.get("active", {}).get(event_id)
    if not active_lease:
        raise ValueError(f"Event `{event_id}` has no active lease to commit.")
    started_at = work_started_at or str(active_lease.get("claimed_at", utc_now()))
    committed_at = utc_now()
    source_mtime_ns = float(packet.lineage.get("source_mtime_ns", 0) or 0)
    detect_latency_ms = max(0.0, (parse_iso(packet.detected_ts).timestamp() * 1000.0) - (source_mtime_ns / 1_000_000.0)) if source_mtime_ns > 0 else 0.0
    encode_latency_ms = self.ms_between(packet.detected_ts, packet.emitted_ts)
    route_latency_ms = float(packet.latency_state.get("awareness_latency_ms", 0.0))
    claim_latency_ms = float(packet.latency_state.get("claim_latency_ms", 0.0))
    resolution_latency_ms = self.ms_between(str(active_lease.get("claimed_at", started_at)), started_at)
    commit_latency_ms = self.ms_between(started_at, committed_at)
    t_sugar_ms = detect_latency_ms + encode_latency_ms + route_latency_ms + claim_latency_ms + commit_latency_ms
    delta_tau = float(packet.coord_delta.get("DeltaTau", packet.liminal_delta or 0.0))
    delta_earth_ms = float(packet.coord_delta.get("DeltaEarth", packet.earth_delta_ms or 0.0))
    liminal_velocity = float(packet.coord_delta.get("LiminalVelocity", packet.liminal_velocity or 0.0))
    receipt_json, receipt_md = self.receipt_paths(event_id)
    verification_state = self.verification_defaults("commit", result, crown_eligible=result.lower().strip() == "success", verification_witness_cap=1.0)
    novelty_score = 1.0 if result.lower().strip() == "success" else 0.70 if result.lower().strip() in {"partial", "blocked", "quarantined"} else 0.0
    reward_state = self.finalize_reward_state(self.compose_reward_state(stage="commit", result=result, priority=packet.priority, confidence=packet.confidence, effort_quality=self.stage_effort_quality("commit", result), tau_seconds=max(commit_latency_ms / 1000.0, 0.0), novelty_score=novelty_score, contribution_share=ROLE_CONTRIBUTION_SHARES["Worker"], verification_state=verification_state))
    pheromone_state = self.compose_pheromone_state(reward_state, ROLE_CONTRIBUTION_SHARES["Worker"], reward_state.verified_alignment_score)
    reward_allocations = self.compose_reward_allocations(reward_state.total_reward, str(active_lease.get("ant_id", "")))
    execution_receipt = CommandExecutionReceiptV2(event_id=event_id, worker_id=str(active_lease.get("ant_id", "")), artifact_targets=artifact_paths or [packet.source_path], writeback_set=writeback_paths or [], result=result, started_at=started_at, committed_at=committed_at, blocked_reason="" if result not in {"blocked", "quarantined"} else (summary or packet.change_summary), restart_seed=f"{event_id}::{result}::{slugify(packet.source_path)}", owner_surface=packet.source_class, claim_id=str(active_lease.get("claim_id", "")), route_path=str(packet.route_state.get("route_path", "")), replay_ptr=rel(self.event_path(event_id)), verification_witness=verification_state.verification_witness, effort_quality=self.stage_effort_quality("commit", result), contribution_share=ROLE_CONTRIBUTION_SHARES["Worker"], learning_novelty=novelty_score, verified_outcome_class=verification_state.closure_class, integration_gain=round(reward_state.total_reward, 6), compression_gain=round(pheromone_state.gold_deposit + pheromone_state.bridge_deposit, 6), reward_state=asdict(reward_state), verification_state=asdict(verification_state), pheromone_state=asdict(pheromone_state), reward_allocations=reward_allocations, crown_tier=reward_state.crown_tier, closure_class=verification_state.closure_class)
    latency_sample = LatencySampleV2(event_id=event_id, detection_latency_ms=round(detect_latency_ms, 3), awareness_latency_ms=round(route_latency_ms, 3), claim_latency_ms=round(claim_latency_ms, 3), resolution_latency_ms=round(resolution_latency_ms, 3), commit_latency_ms=round(commit_latency_ms, 3), t_sugar_ms=round(t_sugar_ms, 3), delta_tau=round(delta_tau, 6), delta_earth_ms=round(delta_earth_ms, 6), liminal_velocity=round(liminal_velocity, 6), resolution_class=verification_state.closure_class, recorded_at=committed_at, swarm_awareness_latency_ms=round(route_latency_ms, 3), capillary_score=round(pheromone_state.compat_edge_strength_after, 6), liminal_delta=round(delta_tau, 6), commit_latency_alias_ms=round(commit_latency_ms, 3), route_policy=JOY_ROUTE_POLICY, tau_seconds=round(max(commit_latency_ms / 1000.0, 0.0), 6), alignment_score=reward_state.alignment_score, verified_alignment_score=reward_state.verified_alignment_score, reward_multiplier=reward_state.reward_multiplier, crown_tier=reward_state.crown_tier)
    latency_registry = read_json(self.config.latency_record_path, [])
    latency_registry.append(asdict(latency_sample))
    write_json(self.config.latency_record_path, latency_registry)
    receipt_payload = read_json(receipt_json, {})
    receipt_payload["execution_receipt_v2"] = asdict(execution_receipt)
    receipt_payload["latency_sample_v2"] = asdict(latency_sample)
    write_json(receipt_json, receipt_payload)
    write_text(receipt_md, "\n".join([f"# Command Commit `{event_id}`", "", f"- result: `{result}`", f"- worker_id: `{execution_receipt.worker_id}`", f"- crown_tier: `{reward_state.crown_tier}`", f"- verified_alignment_score: `{reward_state.verified_alignment_score}`", f"- total_reward: `{reward_state.total_reward}`", f"- gold_deposit: `{pheromone_state.gold_deposit}`", f"- bridge_deposit: `{pheromone_state.bridge_deposit}`", f"- t_sugar_ms: `{latency_sample.t_sugar_ms}`", f"- summary: `{summary or packet.change_summary}`"]))
    packet.commit_state = {"result": result, "summary": summary or packet.change_summary, "artifact_paths": artifact_paths or [packet.source_path], "writeback_paths": writeback_paths or [], "work_started_at": started_at, "committed_at": committed_at, "restart_seed": execution_receipt.restart_seed, "receipt_json": rel(receipt_json), "receipt_md": rel(receipt_md)}
    packet.status = "committed"
    packet.reward_state = asdict(reward_state)
    packet.verification_state = asdict(verification_state)
    packet.pheromone_state = asdict(pheromone_state)
    packet.reward_policy_id = JOY_REWARD_POLICY
    packet.pheromone = clamp(reward_state.verified_alignment_score, 0.0, 1.0)
    packet.crown_tier = reward_state.crown_tier
    packet.closure_class = verification_state.closure_class
    packet.latency_state.update({"detect_latency_ms": round(detect_latency_ms, 3), "encode_latency_ms": round(encode_latency_ms, 3), "awareness_latency_ms": round(route_latency_ms, 3), "claim_latency_ms": round(claim_latency_ms, 3), "resolution_latency_ms": round(resolution_latency_ms, 3), "commit_latency_ms": round(commit_latency_ms, 3), "t_sugar_ms": round(t_sugar_ms, 3), "liminal_distance": round(delta_tau, 6), "DeltaTau": round(delta_tau, 6), "DeltaEarth": round(delta_earth_ms, 6), "LiminalVelocity": round(liminal_velocity, 6)})
    self.save_event(packet)
    finished = dict(active_lease)
    finished["status"] = "committed"
    finished["released_at"] = committed_at
    finished["release_reason"] = result
    leases.setdefault("history", []).append(finished)
    leases["active"].pop(event_id, None)
    self.save_leases(leases)
    board_status = "done" if result == "success" else "queued" if result == "partial" else "blocked"
    swarm_board.create_or_update_claim(agent=str(active_lease.get("ant_id", "")), front=f"{packet.source_id or 'command_root'}::{event_id}", level="command-event", output_target=packet.source_path, receipt=rel(receipt_md), status=board_status, message=summary or f"Committed `{event_id}` as `{result}`.", paths=[packet.source_path, rel(receipt_json), rel(receipt_md)], claim_id=active_lease.get("board_claim_id") or None)
    state = self.load_state()
    state["last_committed_event_id"] = event_id
    self.save_state(state)
    self.sync_public_surfaces(event_id=event_id)
    return {"execution_receipt_v2": asdict(execution_receipt), "latency_sample_v2": asdict(latency_sample), "receipt_json": rel(receipt_json), "receipt_md": rel(receipt_md)}


def _command_v2_reinforce_event(self: CommandMembraneService, event_id: str, path: str | None = None, result: str = "success", latency_score: float | None = None) -> dict[str, Any]:
    packet = self.load_event(event_id)
    route_path = path or str(packet.route_state.get("route_path") or "")
    if not route_path:
        raise ValueError(f"Event `{event_id}` has no route to reinforce.")
    reward_state = CommandRewardStateV2(**(packet.reward_state or {}))
    verification_state = CommandVerificationStateV2(**(packet.verification_state or {}))
    if not packet.reward_state:
        verification_state = self.verification_defaults("commit", result, crown_eligible=result.lower().strip() == "success", verification_witness_cap=1.0)
        reward_state = self.finalize_reward_state(self.compose_reward_state(stage="commit", result=result, priority=packet.priority, confidence=packet.confidence, effort_quality=self.stage_effort_quality("commit", result), tau_seconds=max(float(packet.latency_state.get("commit_latency_ms", 0.0)) / 1000.0, 0.0), novelty_score=1.0 if result.lower().strip() == "success" else 0.0, contribution_share=ROLE_CONTRIBUTION_SHARES["Worker"], verification_state=verification_state))
    tau_seconds = round(max(float(packet.latency_state.get("commit_latency_ms", 0.0)) / 1000.0, 0.0), 6)
    latency_score_value = self.clamp01(float(latency_score) if latency_score is not None else math.exp(-1.0 * tau_seconds))
    reinforced_at = utc_now()
    nodes = [node for node in route_path.split(">") if node]
    edges_payload = self.load_edges()
    edge_records = read_json(self.config.edge_record_path, [])
    updated_edges: list[dict[str, Any]] = []
    total_gold = 0.0
    total_bridge = 0.0
    total_compat = 0.0
    edge_share = 1.0 / max(len(nodes) - 1, 1)
    for idx in range(len(nodes) - 1):
        src = nodes[idx]
        dst = nodes[idx + 1]
        edge_id = f"{src}>{dst}"
        existing = edges_payload.setdefault("edges", {}).get(edge_id, {})
        previous_use_count = int(existing.get("use_count", 0) or 0)
        use_count = previous_use_count + 1
        gold_strength = float(existing.get("gold_strength", existing.get("golden_pheromone", existing.get("edge_strength", 0.0))) or 0.0)
        bridge_strength = float(existing.get("bridge_strength", existing.get("bridge_pheromone", 0.0)) or 0.0)
        previous_avg_alignment = float(existing.get("average_alignment_score", reward_state.alignment_score) or 0.0)
        previous_avg_verified = float(existing.get("average_verified_alignment_score", existing.get("average_heaven_verified", reward_state.verified_alignment_score)) or 0.0)
        average_alignment = ((previous_avg_alignment * previous_use_count) + reward_state.alignment_score) / max(use_count, 1)
        average_verified = ((previous_avg_verified * previous_use_count) + reward_state.verified_alignment_score) / max(use_count, 1)
        evaporation_rate = self.config.rho_0 + self.config.rho_1 * (1.0 - average_verified)
        gold_deposit = round(self.config.mu * reward_state.total_reward * edge_share, 6)
        bridge_deposit = round(self.config.nu * reward_state.attempt_reward * (1.0 - reward_state.verified_alignment_score) * edge_share, 6)
        gold_next = round((1.0 - evaporation_rate) * gold_strength + gold_deposit, 6)
        bridge_next = round((1.0 - self.config.rho_b) * bridge_strength + bridge_deposit, 6)
        compat_edge_strength = round(gold_next + bridge_next, 6)
        success_count = int(existing.get("success_count", 0) or 0) + (1 if verification_state.closure_class == "full_verified_closure" else 0)
        noise_count = int(existing.get("noise_count", 0) or 0) + (1 if verification_state.closure_class == "duplicate_noise_unverified" else 0)
        classification = "vein" if average_verified >= 0.75 else "capillary" if average_verified >= 0.35 else "ephemeral"
        reward_density = round(((float(existing.get("reward_density", 0.0) or 0.0) * previous_use_count) + reward_state.total_reward) / max(use_count, 1), 6)
        crown_count = int(existing.get("crown_count", 0) or 0) + (1 if reward_state.crown_tier == "prime" else 0)
        edge = CapillaryEdgeV2(edge_id=edge_id, from_node=src, to_node=dst, path_key=edge_id, edge_strength=compat_edge_strength, classification=classification, success_count=success_count, use_count=use_count, noise_count=noise_count, average_latency_score=round(latency_score_value, 6), last_result=result, last_event_id=event_id, last_updated=reinforced_at, golden_pheromone=gold_next, bridge_pheromone=bridge_next, average_heaven_verified=round(average_verified, 6), evaporation_rate=round(evaporation_rate, 6), last_reward_total=reward_state.total_reward, last_crown=reward_state.crown_tier, crown_count=crown_count, src=src, dst=dst, strength=compat_edge_strength, state_class=classification, ema_latency_ms=round(latency_score_value * 1000.0, 3), rho=self.config.rho_0, alpha=self.config.reward_alpha, beta=self.config.reward_beta, gamma=self.config.reward_gamma, delta=self.config.reward_delta, usefulness=round(reward_state.verified_alignment_score, 6), frequency=round(average_verified, 6), latency_penalty=round(1.0 - latency_score_value, 6), noise_penalty=0.0 if verification_state.closure_class != "duplicate_noise_unverified" else 1.0, last_reinforced_at_utc=reinforced_at, tier=classification, source_ant_id=src, target_ant_id=dst, grade=classification, front_ref=packet.front_ref, gold_strength=gold_next, bridge_strength=bridge_next, compat_edge_strength=compat_edge_strength, average_alignment_score=round(average_alignment, 6), average_verified_alignment_score=round(average_verified, 6), reward_density=reward_density, gold_deposit=gold_deposit, bridge_deposit=bridge_deposit)
        edge_payload = asdict(edge)
        edges_payload["edges"][edge_id] = edge_payload
        updated_edges.append(edge_payload)
        edge_records.append({"event_id": event_id, "edge_id": edge_id, "updated_at": reinforced_at, "edge": edge_payload})
        total_gold += gold_deposit
        total_bridge += bridge_deposit
        total_compat += compat_edge_strength
    self.save_edges(edges_payload)
    write_json(self.config.edge_record_path, edge_records)
    average_compat = round(total_compat / max(len(updated_edges), 1), 6)
    aggregated_pheromone = CommandPheromoneStateV2(gold_deposit=round(total_gold, 6), bridge_deposit=round(total_bridge, 6), evaporation_rate=round(self.config.rho_0 + self.config.rho_1 * (1.0 - reward_state.verified_alignment_score), 6), gold_strength_after=round(sum(edge["gold_strength"] for edge in updated_edges), 6), bridge_strength_after=round(sum(edge["bridge_strength"] for edge in updated_edges), 6), compat_edge_strength_after=round(total_compat, 6))
    reward_allocations = self.compose_reward_allocations(reward_state.total_reward, str(packet.claim_state.get("ant_id", "")))
    reinforcement_receipt = CommandReinforcementReceiptV2(event_id=event_id, path=route_path, result=result, t_detect_ms=float(packet.latency_state.get("detect_latency_ms", 0.0)), t_encode_ms=float(packet.latency_state.get("encode_latency_ms", 0.0)), t_route_ms=float(packet.latency_state.get("awareness_latency_ms", 0.0)), t_claim_ms=float(packet.latency_state.get("claim_latency_ms", 0.0)), t_commit_ms=float(packet.latency_state.get("commit_latency_ms", 0.0)), latency_score=round(latency_score_value, 6), capillary_delta=round(total_gold + total_bridge, 6), reinforced_at=reinforced_at, a_verified=reward_state.affect_intensity_a, phi_verified=reward_state.affect_direction_phi, h_raw=reward_state.alignment_score, h_verified=reward_state.verified_alignment_score, reward_multiplier=reward_state.reward_multiplier, try_reward=reward_state.attempt_reward, speed_reward=reward_state.latency_reward, first_bonus=reward_state.first_reward, assist_reward=reward_state.assist_reward, learn_reward=reward_state.learning_reward, total_reward=reward_state.total_reward, gold_deposit=round(total_gold, 6), bridge_deposit=round(total_bridge, 6), crown=reward_state.crown_tier, capillary_score=average_compat, liminal_distance=float(packet.coord_delta.get("DeltaTau", packet.liminal_delta or 0.0)), liminal_velocity=float(packet.coord_delta.get("LiminalVelocity", packet.liminal_velocity or 0.0)), claim_id=str(packet.claim_state.get("claim_id", "")), replay_ptr=rel(self.event_path(event_id)), reward_state=asdict(reward_state), verification_state=asdict(verification_state), pheromone_state=asdict(aggregated_pheromone), reward_allocations=reward_allocations, edge_allocations=updated_edges, crown_tier=reward_state.crown_tier, closure_class=verification_state.closure_class, route_mode=reward_state.route_mode)
    receipt_json, receipt_md = self.receipt_paths(event_id)
    receipt_payload = read_json(receipt_json, {})
    receipt_payload["reinforcement_receipt_v2"] = asdict(reinforcement_receipt)
    write_json(receipt_json, receipt_payload)
    write_text(receipt_md, "\n".join([f"# Command Reinforcement `{event_id}`", "", f"- route_mode: `{reward_state.route_mode}`", f"- crown_tier: `{reward_state.crown_tier}`", f"- total_reward: `{reward_state.total_reward}`", f"- gold_deposit: `{round(total_gold, 6)}`", f"- bridge_deposit: `{round(total_bridge, 6)}`", f"- compat_edge_strength: `{round(total_compat, 6)}`"]))
    packet.status = "reinforced"
    packet.pheromone_state = asdict(aggregated_pheromone)
    packet.pheromone = clamp(reward_state.verified_alignment_score, 0.0, 1.0)
    packet.latency_state["capillary_delta"] = round(total_gold + total_bridge, 6)
    packet.latency_state["capillary_score"] = average_compat
    self.save_event(packet)
    self.sync_public_surfaces(event_id=event_id)
    return {"reinforcement_receipt_v2": asdict(reinforcement_receipt), "edges": updated_edges, "receipt_json": rel(receipt_json), "receipt_md": rel(receipt_md)}


CommandMembraneService.claim_event = _command_v2_claim_event
CommandMembraneService.commit_event = _command_v2_commit_event
CommandMembraneService.reinforce_event = _command_v2_reinforce_event
CommandMembraneService.ms_between = _command_membrane_ms_between

from .command_spine_unified_patch import bootstrap_command_membrane as _bootstrap_command_membrane

_bootstrap_command_membrane(globals())

COMMAND_COORD12_LABELS = [
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


def _command_protocol_watcher_mode(self: CommandMembraneService) -> str:
    state = self.load_state()
    mode = str(state.get("watcher_mode", "") or "").strip().lower()
    if "poll" in mode:
        return "polling"
    if "event" in mode:
        return "event-driven"
    if os.name == "nt" and shutil.which("powershell"):
        return "event-driven"
    return "polling"


def _command_protocol_current_runtime_truth(self: CommandMembraneService) -> dict[str, Any]:
    bundle = read_json(self.config.hsigma_bundle_path, {})
    truth = bundle.get("current_runtime_truth", {}) if isinstance(bundle, dict) else {}
    return {
        "canonical_authority": "LP57OMEGA / NEXT57",
        "active_loop": str(truth.get("active_loop") or "L05"),
        "active_family": str(truth.get("active_family") or "L05 Canonical 16-Basis Ownership"),
        "restart_seed": str(truth.get("restart_seed") or "L05 Canonical 16-Basis Ownership"),
        "visible_caps": truth.get("visible_caps") or {"hall": 8, "temple": 8},
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "feeders": list(COMMAND_FEEDER_STACK),
    }


def _command_protocol_watched_surface_registry(self: CommandMembraneService, source_ids: Iterable[str] | None = None) -> dict[str, Any]:
    requested = {str(source_id) for source_id in source_ids} if source_ids else None
    rows = [{
        "source_id": "command_root",
        "source_class": "command-folder",
        "root": "GLOBAL COMMAND",
        "watch_scope": "GLOBAL COMMAND only",
        "watch_mode": self._command_protocol_watcher_mode(),
        "absolute_path": str(self.config.command_surface_root.resolve()),
        "relative_path": rel(self.config.command_surface_root),
        "watch_root": str(self.config.command_surface_root.resolve()),
        "watch_root_relative": rel(self.config.command_surface_root),
        "target_kind": "directory",
        "event_filters": ["created", "modified", "renamed", "deleted"],
        "default_lanes": {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"},
        "routing_goal": "detect-classify-assign",
        "urgency_baseline": 0.96,
        "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND", "Hs": "command-event", "Ns": "COMMAND"},
        "docs_gate_status": self.docs_gate_status()["state"],
        "exists": self.config.command_surface_root.exists(),
    }]
    if requested is not None:
        rows = [row for row in rows if row["source_id"] in requested]
    return {
        "generated_at": utc_now(),
        "watcher_mode": self._command_protocol_watcher_mode(),
        "watch_scope": "GLOBAL COMMAND only",
        "source_count": len(rows),
        "rows": rows,
    }


def _command_protocol_source_health(self: CommandMembraneService, source_ids: Iterable[str] | None = None) -> dict[str, Any]:
    docs_gate = self.docs_gate_status()
    registry = self._command_protocol_watched_surface_registry(source_ids)
    rows = []
    for row in registry["rows"]:
        rows.append({
            "source_id": row["source_id"],
            "source_class": row["source_class"],
            "absolute_path": row["absolute_path"],
            "watch_root": row["watch_root"],
            "exists": row["exists"],
            "watch_scope": row["watch_scope"],
            "watcher_mode": row["watch_mode"],
            "native_watch_available": bool(os.name == "nt" and shutil.which("powershell")),
            "fallback_mode": "polling",
            "docs_gate_status": docs_gate["state"],
        })
    return {
        "generated_at": utc_now(),
        "watch_scope": "GLOBAL COMMAND only",
        "watcher_mode": self._command_protocol_watcher_mode(),
        "source_count": len(rows),
        "rows": rows,
    }


def _command_protocol_snapshot(self: CommandMembraneService) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    if not self.config.command_surface_root.exists():
        return snapshot
    for path in sorted(self.config.command_surface_root.rglob("*")):
        if not path.is_file():
            continue
        if self.ignored_reason(path) is not None:
            continue
        stat = path.stat()
        digest = hashlib.sha1()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        snapshot[path.relative_to(self.config.command_surface_root).as_posix()] = {
            "state_hash": f"H:{digest.hexdigest()}",
            "size_bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
    return snapshot


def _command_protocol_compute_changes(
    self: CommandMembraneService,
    previous: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    del self
    changes: list[dict[str, Any]] = []
    previous = previous or {}
    current = current or {}
    for rel_path in sorted(set(current) - set(previous)):
        changes.append({"relative_path": rel_path, "event_kind": "created", **current[rel_path]})
    for rel_path in sorted(set(previous) - set(current)):
        changes.append({"relative_path": rel_path, "event_kind": "deleted", **previous[rel_path]})
    for rel_path in sorted(set(previous) & set(current)):
        if previous[rel_path].get("state_hash") != current[rel_path].get("state_hash"):
            changes.append({"relative_path": rel_path, "event_kind": "modified", **current[rel_path]})
    return changes


def _command_protocol_wait_for_event(self: CommandMembraneService, timeout_secs: int) -> str:
    if os.name == "nt" and shutil.which("powershell"):
        timeout_ms = max(int(timeout_secs * 1000), 1) if timeout_secs else 60000
        script = (
            "$fsw = New-Object IO.FileSystemWatcher @('{0}');"
            "$fsw.IncludeSubdirectories = $true;"
            "$result = $fsw.WaitForChanged([IO.WatcherChangeTypes]'FileName, DirectoryName, LastWrite, Size, CreationTime', {1});"
            "if ($result.TimedOut) {{ exit 2 }} else {{ Write-Output \"$($result.ChangeType)|$($result.Name)\" }}"
        ).format(str(self.config.command_surface_root), timeout_ms)
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                text=True,
                timeout=max(timeout_secs, 1) + 2 if timeout_secs else None,
                check=False,
            )
            if completed.returncode in {0, 2}:
                return "event-driven"
        except (OSError, subprocess.TimeoutExpired):
            pass
    time.sleep(timeout_secs if timeout_secs else 0.5)
    return "polling"


def _command_protocol_metrics(self: CommandMembraneService, surface: str = "command-folder") -> dict[str, Any]:
    del surface
    events = list(reversed(self.recent_event_payloads(limit=None)))
    committed = [event for event in events if (event.get("commit_state") or {}).get("committed_at")]
    edges = self.load_edges().get("edges", {})

    def _avg(values: list[float]) -> float:
        return round(sum(values) / max(len(values), 1), 3) if values else 0.0

    tier_counts = {"route": 0, "capillary": 0, "vein": 0}
    top_capillaries = []
    for edge_id, edge in edges.items():
        classification = str(edge.get("classification", edge.get("state_class", "route")) or "route")
        if classification == "seed":
            classification = "route"
        if classification not in tier_counts:
            classification = "route"
        tier_counts[classification] += 1
        top_capillaries.append({
            "edge_id": edge_id,
            "edge_strength": float(edge.get("edge_strength", edge.get("strength", edge.get("compat_edge_strength", 0.0))) or 0.0),
            "classification": classification,
        })
    top_capillaries.sort(key=lambda item: (-item["edge_strength"], item["edge_id"]))

    return {
        "surface": "command-folder",
        "docs_gate_status": self.docs_gate_status()["state"],
        "event_count": len(events),
        "committed_count": len(committed),
        "active_leases": len(self.load_leases().get("active", {})),
        "detection_latency_avg_ms": _avg([float((event.get("latency_state") or {}).get("detect_latency_ms", (event.get("latency_state") or {}).get("detection_latency_ms", 0.0)) or 0.0) for event in committed]),
        "swarm_awareness_latency_avg_ms": _avg([float((event.get("latency_state") or {}).get("awareness_latency_ms", (event.get("latency_state") or {}).get("swarm_awareness_latency_ms", 0.0)) or 0.0) for event in committed]),
        "claim_latency_avg_ms": _avg([float((event.get("latency_state") or {}).get("claim_latency_ms", 0.0) or 0.0) for event in committed]),
        "resolution_latency_avg_ms": _avg([float((event.get("latency_state") or {}).get("resolution_latency_ms", 0.0) or 0.0) for event in committed]),
        "commit_latency_avg_ms": _avg([float((event.get("latency_state") or {}).get("commit_latency_ms", 0.0) or 0.0) for event in committed]),
        "t_sugar_avg_ms": _avg([float((event.get("latency_state") or {}).get("t_sugar_ms", 0.0) or 0.0) for event in committed]),
        "capillary_score_avg": _avg([float((event.get("latency_state") or {}).get("capillary_score", 0.0) or 0.0) for event in committed]),
        "liminal_distance_avg": _avg([float((event.get("latency_state") or {}).get("liminal_distance", (event.get("coord_delta") or {}).get("DeltaTau", 0.0)) or 0.0) for event in committed]),
        "liminal_velocity_avg": _avg([float((event.get("latency_state") or {}).get("LiminalVelocity", (event.get("coord_delta") or {}).get("LiminalVelocity", 0.0)) or 0.0) for event in committed]),
        "capillary_tiers": tier_counts,
        "top_capillaries": top_capillaries[:5],
        "last_event_id": events[-1].get("event_id", "") if events else "",
    }


def _command_protocol_sync_public_surfaces(self: CommandMembraneService, event_id: str | None = None) -> dict[str, Any]:
    runtime_truth = self.current_runtime_truth()
    docs_gate = self.docs_gate_status()
    watcher_mode = self._command_protocol_watcher_mode()
    watch_registry = self._command_protocol_watched_surface_registry()
    source_health = self._command_protocol_source_health()
    events = list(reversed(self.recent_event_payloads(limit=None)))
    metrics = self._command_protocol_metrics()
    leases = self.load_leases()
    edges = self.load_edges().get("edges", {})
    recent_events = []
    for event in events[-12:]:
        recent_events.append({
            "event_id": event.get("event_id", ""),
            "event_type": event.get("change_type", ""),
            "source_path": event.get("source_path", ""),
            "change_type": event.get("change_type", ""),
            "watcher_mode": event.get("watcher_mode", watcher_mode),
            "status": event.get("status", "open"),
            "earth_ts_utc": event.get("earth_ts", ""),
            "route_path": (event.get("route_state") or {}).get("route_path", ""),
            "claim_state": (event.get("claim_state") or {}).get("status", "unclaimed"),
            "replay_ptr": event.get("replay_ptr", rel(self.event_path(event.get("event_id", "")))),
            "coord12": event.get("coord12", {}),
            "coordinate_stamp": event.get("coordinate_stamp", {}),
            "delta_tau": float((event.get("coord_delta") or {}).get("DeltaTau", event.get("liminal_delta", 0.0)) or 0.0),
            "velocity_tau": float((event.get("coord_delta") or {}).get("LiminalVelocity", event.get("liminal_velocity", 0.0)) or 0.0),
        })
    last_event = recent_events[-1] if recent_events else {}
    latest_committed = next(
        (
            {
                "event_id": event.get("event_id", ""),
                "route_path": (event.get("route_state") or {}).get("route_path", ""),
                "detection_latency_ms": float((event.get("latency_state") or {}).get("detect_latency_ms", (event.get("latency_state") or {}).get("detection_latency_ms", 0.0)) or 0.0),
                "swarm_awareness_latency_ms": float((event.get("latency_state") or {}).get("awareness_latency_ms", 0.0) or 0.0),
                "claim_latency_ms": float((event.get("latency_state") or {}).get("claim_latency_ms", 0.0) or 0.0),
                "resolution_latency_ms": float((event.get("latency_state") or {}).get("resolution_latency_ms", 0.0) or 0.0),
                "commit_latency_ms": float((event.get("latency_state") or {}).get("commit_latency_ms", 0.0) or 0.0),
                "t_sugar_ms": float((event.get("latency_state") or {}).get("t_sugar_ms", 0.0) or 0.0),
                "capillary_score": float((event.get("latency_state") or {}).get("capillary_score", 0.0) or 0.0),
                "liminal_distance": float((event.get("latency_state") or {}).get("liminal_distance", (event.get("coord_delta") or {}).get("DeltaTau", 0.0)) or 0.0),
                "liminal_velocity": float((event.get("latency_state") or {}).get("LiminalVelocity", (event.get("coord_delta") or {}).get("LiminalVelocity", 0.0)) or 0.0),
                "recorded_at": (event.get("commit_state") or {}).get("committed_at", ""),
                "replay_ptr": event.get("replay_ptr", rel(self.event_path(event.get("event_id", "")))),
                "outcome": (event.get("commit_state") or {}).get("result", ""),
            }
            for event in reversed(events)
            if (event.get("commit_state") or {}).get("committed_at")
        ),
        {},
    )
    top_capillaries = []
    for edge_id, edge in edges.items():
        classification = str(edge.get("classification", edge.get("state_class", "route")) or "route")
        if classification == "seed":
            classification = "route"
        top_capillaries.append({
            "edge_id": edge_id,
            "source_ant_id": edge.get("source_ant_id", edge.get("from_node", "")),
            "target_ant_id": edge.get("target_ant_id", edge.get("to_node", "")),
            "edge_strength": float(edge.get("edge_strength", edge.get("strength", edge.get("compat_edge_strength", 0.0))) or 0.0),
            "classification": classification,
            "last_event_id": edge.get("last_event_id", ""),
            "last_updated": edge.get("last_updated", edge.get("last_reinforced_at_utc", "")),
        })
    top_capillaries.sort(key=lambda item: (-item["edge_strength"], item["edge_id"]))

    payload = {
        "generated_at": utc_now(),
        "protocol_id": "NEXT57_COMMAND_PROTOCOL_V1",
        "canonical_authority": "LP57OMEGA / NEXT57",
        "command_root": str(self.config.command_surface_root),
        "active_surface": "GLOBAL COMMAND",
        "watch_scope": "GLOBAL COMMAND only",
        "watcher_mode": watcher_mode,
        "watched_surface_count": 1,
        "docs_gate": docs_gate,
        "docs_gate_status": docs_gate["state"],
        "current_runtime_truth": runtime_truth,
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "feeder_stack": list(COMMAND_FEEDER_STACK),
        "policy": {
            "protocol_id": "NEXT57_COMMAND_PROTOCOL_V1",
            "routing_policy": COMMAND_ROUTE_POLICY,
            "selector_terms": list(COMMAND_SELECTOR_TERMS),
            "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
            "watch_policy": {"primary_mode": "event-driven", "fallback_mode": "polling", "watch_scope": "GLOBAL COMMAND only"},
            "topk": self.config.topk,
            "claim_mode": self.config.claim_mode,
            "quorum": self.config.quorum,
            "ttl": self.config.ttl,
            "lease_ms": self.config.lease_ms,
        },
        "truth_boundary": {
            "prompt_level_liminal_gps": "supported",
            "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
        },
        "active_leases": list(leases.get("active", {}).keys()),
        "queue_depth": max(metrics.get("event_count", 0) - metrics.get("committed_count", 0), 0),
        "recent_events": recent_events,
        "last_event": last_event if event_id is None else next((row for row in recent_events if row["event_id"] == event_id), last_event),
        "latest_committed": latest_committed,
        "top_capillaries": top_capillaries[:5],
        "metrics": metrics,
        "updated_at": utc_now(),
        "known_files": self.load_state().get("known_files", {}),
        "watch_registry": watch_registry,
        "source_health": source_health,
    }

    current_state = self.load_state()
    current_state["watcher_mode"] = watcher_mode
    current_state["last_committed_event_id"] = latest_committed.get("event_id", current_state.get("last_committed_event_id", ""))
    current_state["updated_at"] = utc_now()
    self.save_state(current_state)
    write_json(PUBLIC_COMMAND_STATE_PATH, payload)
    write_json(self.config.watched_surface_registry_path, watch_registry)
    write_json(self.config.surface_health_path, source_health)
    write_json(self.config.live_event_ledger_path, recent_events)
    write_json(
        self.config.live_manifest_path,
        {
            "generated_at": utc_now(),
            "protocol_id": "NEXT57_COMMAND_PROTOCOL_V1",
            "canonical_authority": "LP57OMEGA / NEXT57",
            "canonical_surface": "GLOBAL COMMAND",
            "watch_scope": "GLOBAL COMMAND only",
            "watcher_mode": watcher_mode,
            "docs_gate": docs_gate,
            "current_runtime_truth": runtime_truth,
            "active_membrane": COMMAND_ACTIVE_MEMBRANE,
            "feeder_stack": list(COMMAND_FEEDER_STACK),
            "artifact_refs": {
                "protocol": rel(self.config.protocol_json_path),
                "schema": rel(self.config.packet_schema_json_path),
                "capillary": rel(self.config.capillary_law_json_path),
                "latency": rel(self.config.latency_benchmark_json_path),
            },
            "state_ref": rel(PUBLIC_COMMAND_STATE_PATH),
        },
    )

    feeder_text = " / ".join(COMMAND_FEEDER_STACK)
    top_capillary = top_capillaries[0] if top_capillaries else {}
    patch_markdown_file(
        ACTIVE_RUN_PATH,
        MARKER_ACTIVE_RUN,
        "\n".join([
            "## COMMAND Membrane Active Run",
            "",
            "- Canonical authority: `LP57OMEGA / NEXT57`",
            "- Command surface: `GLOBAL COMMAND`",
            "- Watch scope: `GLOBAL COMMAND only`",
            f"- Watcher mode: `{watcher_mode}`",
            f"- Docs gate: `{docs_gate['state']}` / `{docs_gate['detail']}`",
            f"- Active loop: `{runtime_truth.get('active_loop', 'L02')}`",
            f"- Active membrane: `{COMMAND_ACTIVE_MEMBRANE}`",
            f"- Feeder stack: `{feeder_text}`",
            f"- Latest committed command event: `{latest_committed.get('event_id', last_event.get('event_id', 'none'))}`",
            f"- Top capillary: `{top_capillary.get('edge_id', 'none')}`",
        ]),
    )
    patch_markdown_file(
        BUILD_QUEUE_PATH,
        MARKER_BUILD_QUEUE,
        "\n".join([
            "## COMMAND Membrane Queue",
            "",
            f"- Queue depth: `{payload['queue_depth']}`",
            f"- Active leases: `{len(leases.get('active', {}))}`",
            "- Watch scope: `GLOBAL COMMAND only`",
            f"- Routing policy: `{COMMAND_ROUTE_POLICY}`",
            f"- Claim mode: `{self.config.claim_mode}`",
            f"- Routing budget: `topk={self.config.topk}`, `quorum={self.config.quorum}`, `lease_ms={self.config.lease_ms}`",
            f"- Last event: `{last_event.get('event_id', 'none')}`",
        ]),
    )
    patch_markdown_file(
        HALL_BOARD_PATH,
        MARKER_HALL,
        "\n".join([
            "## COMMAND Membrane Hall Family",
            "",
            f"- Quest id: `{COMMAND_HALL_QUEST_ID}`",
            "- Surface: practical command intake, lawful worker claim, and receipt-backed closure.",
            "- Phase 1 watch scope: `GLOBAL COMMAND only`.",
            "- Routing spine: `COMMAND FOLDER -> Scout -> Router -> Worker -> Archivist`.",
            f"- Routing policy: `{COMMAND_ROUTE_POLICY}`.",
            f"- Latest event: `{last_event.get('event_id', 'none')}` :: `{last_event.get('status', 'idle')}`.",
        ]),
    )
    patch_markdown_file(
        TEMPLE_BOARD_PATH,
        MARKER_TEMPLE,
        "\n".join([
            "## COMMAND Membrane Temple Family",
            "",
            f"- Quest id: `{COMMAND_TEMPLE_QUEST_ID}`",
            "- Surface: docs-gate honesty, coordinate law, capillary law, and no-rumor routing discipline.",
            "- Prompt-level liminal GPS: `supported`.",
            "- Keystroke-level liminal GPS: `requires client/runtime instrumentation`.",
            f"- Docs gate: `{docs_gate['state']}` / `{docs_gate['detail']}`.",
            f"- Active membrane: `{COMMAND_ACTIVE_MEMBRANE}`.",
        ]),
    )
    patch_markdown_file(
        ACTIVE_QUEUE_PATH,
        "COMMAND_MEMBRANE_ACTIVE_QUEUE",
        "\n".join([
            "## Command Membrane",
            "",
            f"- Queue depth: `{payload['queue_depth']}`",
            f"- Active leases: `{len(leases.get('active', {}))}`",
            f"- Watcher mode: `{watcher_mode}`",
            f"- Last event: `{last_event.get('event_id', 'none')}`",
            f"- Top capillary: `{top_capillary.get('edge_id', 'none')}`",
        ]),
    )
    patch_markdown_file(
        NEXT_SELF_PROMPT_PATH,
        "COMMAND_MEMBRANE_NEXT_PROMPT",
        "\n".join([
            "## COMMAND Membrane Next Prompt",
            "",
            "1. Treat `GLOBAL COMMAND` as a sensory membrane, not a passive folder.",
            "2. Keep Google Docs explicitly blocked until credentials exist and an actual live pass succeeds.",
            "3. Preserve dual-stamped Earth plus liminal timing on every committed event.",
            "4. Route only to the ants that matter first; do not widen broadcast by default.",
            "5. Keep Hall and Temple macro-sized even when machine event volume grows.",
        ]),
    )
    return payload


def _command_protocol_public_state(self: CommandMembraneService) -> dict[str, Any]:
    return self._command_protocol_sync_public_surfaces()


def _command_protocol_ensure_protocol_artifacts(self: CommandMembraneService) -> dict[str, Any]:
    docs_gate = self.docs_gate_status()
    runtime_truth = self.current_runtime_truth()
    protocol = {
        "protocol_id": "NEXT57_COMMAND_PROTOCOL_V1",
        "command_version": "sensory-membrane-v1",
        "canonical_authority": "LP57OMEGA / NEXT57",
        "authority_mode": "subordinate-command-membrane",
        "compatibility_role": "no-separate-control-plane",
        "mode": "event-driven-first",
        "canonical_surface": "GLOBAL COMMAND",
        "active_surface": "GLOBAL COMMAND",
        "command_folder_root": "GLOBAL COMMAND",
        "docs_gate": docs_gate,
        "docs_gate_status": docs_gate["state"],
        "current_runtime_truth": runtime_truth,
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "feeder_stack": list(COMMAND_FEEDER_STACK),
        "packet_flow": ["COMMAND FOLDER", "Scout", "Router", "Worker", "Archivist"],
        "pipeline": ["emit", "route", "claim", "commit", "reinforce"],
        "command_spine": ["emit", "route", "claim", "commit", "reinforce"],
        "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
        "public_caps": runtime_truth.get("visible_caps", {"hall": 8, "temple": 8}),
        "routing_defaults": {
            "policy_id": COMMAND_ROUTE_POLICY,
            "selector_terms": list(COMMAND_SELECTOR_TERMS),
            "topk": self.config.topk,
            "claim_mode": self.config.claim_mode,
            "quorum": self.config.quorum,
            "ttl": self.config.ttl,
            "lease_ms": self.config.lease_ms,
        },
        "watch_policy": {
            "primary_mode": "event-driven",
            "fallback_mode": "polling",
            "fallback_honesty_rule": "mark polling fallback explicitly and do not pretend intake was event-driven",
            "watched_roots": ["GLOBAL COMMAND"],
            "watched_surface_count": 1,
            "watch_scope": "GLOBAL COMMAND only",
        },
        "quest_family": {
            "hall": [COMMAND_HALL_QUEST_ID, "NEXT57-H-COMMAND-CHANGE-FEED", "NEXT57-H-COMMAND-QUEUE", "NEXT57-H-COMMAND-LEDGER"],
            "temple": [COMMAND_TEMPLE_QUEST_ID],
        },
        "sensor_defaults": {
            "root": "GLOBAL COMMAND",
            "event_types": ["created", "modified", "renamed", "deleted", "moved_into_root"],
            "coalesce_ms": self.config.debounce_ms,
            "reconcile_interval_secs": self.config.reconcile_interval_secs,
        },
        "truth_boundary": {
            "prompt_level_liminal_gps": "supported",
            "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
        },
    }
    schema = {
        "schema_id": "COMMAND_MEMBRANE_PACKET_SCHEMA_V1",
        "coord12_labels": list(COMMAND_COORD12_LABELS),
        "coord12_frame_groups": ["earth", "astro", "runtime", "liminal"],
        "packet_types": {
            "CommandEventPacket": ["event_id", "source_ant_id", "source_path", "change_type", "goal", "priority", "confidence", "earth_ts", "liminal_ts", "coord12", "coordinate_stamp", "ttl", "pheromone", "route_class", "witness_class"],
            "RouteDecision": ["event_id", "policy_id", "candidate_targets", "selected_targets", "topk", "claim_mode", "quorum", "route_path"],
            "ClaimLease": ["claim_id", "event_id", "ant_id", "role", "lease_ms", "claimed_at", "expires_at", "status"],
            "ArchivistReceipt": ["event_id", "worker_id", "result", "route_path", "detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "replay_ptr"],
            "CapillaryEdge": ["edge_id", "source_ant_id", "target_ant_id", "edge_strength", "classification", "success_count", "use_count", "noise_count", "last_event_id"],
            "LatencyBenchmarkRecord": ["detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "capillary_score", "liminal_distance", "liminal_velocity"],
        },
        "ledger_extensions": ["event_id", "event_type", "route_path", "claim_state", "latency_breakdown", "capillary_delta", "witness_class", "artifact_refs"],
        "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
    }
    capillary = {
        "law_id": "COMMAND_MEMBRANE_CAPILLARY_LAW_V1",
        "formula": "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
        "coefficients": {"rho": self.config.rho, "alpha": self.config.alpha, "beta": self.config.beta, "gamma": self.config.gamma, "delta": self.config.delta},
        "edge_classes": ["route", "capillary", "vein"],
        "thresholds": {
            "route_max": 0.349999,
            "capillary_min": 0.35,
            "vein_min": 0.70,
            "capillary_min_successes": 3,
            "vein_min_successes": 7,
        },
        "initial_strength": 0.25,
    }
    latency = {
        "benchmark_id": "COMMAND_MEMBRANE_LATENCY_V1",
        "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "metrics": ["detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "capillary_score", "liminal_distance", "liminal_velocity"],
        "truth_boundary": {
            "prompt_level_liminal_gps": "supported",
            "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
        },
    }
    reward = {
        "compatibility_role": "support-only",
        "note": "Capillary reinforcement, not reward economy, is authoritative in the command membrane.",
    }

    write_json(self.config.protocol_json_path, protocol)
    write_json(self.config.packet_schema_json_path, schema)
    write_json(self.config.capillary_law_json_path, capillary)
    write_json(self.config.latency_benchmark_json_path, latency)
    write_json(self.config.reward_law_json_path, reward)
    write_json(self.config.protocol_v1_registry_path, protocol)

    write_text(self.config.command_manifest_path, "\n".join([
        "# NEXT57 Command Sensory Membrane",
        "",
        "- Canonical authority: `LP57OMEGA / NEXT57`",
        "- Phase 1 watch scope: `GLOBAL COMMAND only`",
        "- Mode: `event-driven-first` with explicit `polling` fallback",
        f"- Docs gate: `{docs_gate['state']}` / `{docs_gate['detail']}`",
        "- Prompt-level liminal GPS: `supported`",
        "- Keystroke-level liminal GPS: `requires client/runtime instrumentation`",
    ]))
    write_text(self.config.protocol_manifest_path, "\n".join([
        "# NEXT57 Command Protocol",
        "",
        "- Protocol id: `NEXT57_COMMAND_PROTOCOL_V1`",
        "- Canonical authority: `LP57OMEGA / NEXT57`",
        "- Control-plane role: `subordinate command membrane`",
        "- Phase 1 watch scope: `GLOBAL COMMAND only`",
        f"- Routing policy: `{COMMAND_ROUTE_POLICY}`",
        "- Selector terms: `goal, salience, pheromone, coord, capability, load`",
        "- Docs gate remains `BLOCKED` until credentials exist and a live pass succeeds.",
    ]))
    write_text(self.config.packet_manifest_path, "\n".join([
        "# NEXT57 Command Packet Standard",
        "",
        "- Every detected change becomes a typed packet before routing.",
        f"- Lookup envelope: `{schema['lookup_envelope']}`",
        f"- Coord12 labels: `{', '.join(COMMAND_COORD12_LABELS)}`",
        "- Packet families: `CommandEventPacket`, `RouteDecision`, `ClaimLease`, `ArchivistReceipt`, `CapillaryEdge`, `LatencyBenchmarkRecord`.",
    ]))
    write_text(self.config.capillary_manifest_path, "\n".join([
        "# NEXT57 Command Capillary Law",
        "",
        "- Formula: `C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)`",
        "- Repeated fast useful routes strengthen; noisy or slow routes decay.",
        "- Tiers: `route < 0.35`, `capillary >= 0.35`, `vein >= 0.70`.",
    ]))
    write_text(self.config.latency_manifest_path, "\n".join([
        "# NEXT57 Command Latency Benchmarks",
        "",
        "- Equation: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`",
        "- Benchmarks: detection, swarm awareness, claim, resolution, commit, T_sugar, capillary score, liminal distance, liminal velocity.",
        "- Prompt-level liminal GPS is supported; keystroke-level remains out of scope in v1.",
    ]))
    write_text(self.config.protocol_v1_manifest_path, "\n".join([
        "# Command Membrane Protocol V1",
        "",
        "- This registry mirrors the live local-only command membrane law.",
        "- It does not create a second quest authority, restart seed, or control plane outside LP-57/NEXT57.",
        "- Phase 1 watches `GLOBAL COMMAND` only.",
    ]))

    public_state = self._command_protocol_sync_public_surfaces()
    return {
        "protocol": self.config.protocol_json_path,
        "schema": self.config.packet_schema_json_path,
        "reward": self.config.reward_law_json_path,
        "capillary": self.config.capillary_law_json_path,
        "latency": self.config.latency_benchmark_json_path,
        "public_state": public_state,
    }


def _command_protocol_watch_command_folder(
    self: CommandMembraneService,
    *,
    once: bool = False,
    timeout_secs: int = 0,
    bootstrap_existing: bool = False,
    emit_only: bool = False,
    source_ids: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    self.ensure_protocol_artifacts()
    state = self.load_state()
    previous = {} if bootstrap_existing else dict(state.get("known_files", {}) or {})
    watcher_mode = "polling" if bootstrap_existing else self._command_protocol_wait_for_event(timeout_secs if timeout_secs else 1)
    current = self._command_protocol_snapshot()
    changes = self._command_protocol_compute_changes(previous, current)
    state["known_files"] = current
    state["watcher_mode"] = watcher_mode
    self.save_state(state)

    processed: list[dict[str, Any]] = []
    for change in changes:
        packet = self.emit_change(
            source_path=(self.config.command_surface_root / change["relative_path"]).resolve(strict=False),
            change_type=str(change["event_kind"]),
            detected_ts=utc_now(),
            state=state,
            source_ids=source_ids or ["command_root"],
        )
        if packet is None:
            continue
        event_id = packet.event_id
        route_payload = self.route_event(event_id)
        claim_payload = None
        commit_payload = None
        reinforce_payload = None
        if not emit_only:
            worker_id = (route_payload.get("selected_targets") or [""])[0]
            claim_payload = self.claim_event(event_id, ant_id=worker_id or None, role="worker", lease_ms=self.config.lease_ms)
            commit_payload = self.commit_event(
                event_id,
                result="success",
                artifact_paths=[packet.source_path],
                writeback_paths=[rel(ACTIVE_RUN_PATH), rel(BUILD_QUEUE_PATH), rel(HALL_BOARD_PATH), rel(TEMPLE_BOARD_PATH)],
                summary=f"watch-command-folder processed {change['relative_path']}",
            )
            reinforce_payload = self.reinforce_event(event_id, result="success")
        processed.append({
            "event_id": event_id,
            "relative_path": packet.source_path,
            "event_kind": packet.change_type,
            "watch_mode": watcher_mode,
            "route": route_payload,
            "claim": claim_payload,
            "commit": commit_payload,
            "reinforcement": reinforce_payload,
        })
        if once:
            break
    self._command_protocol_sync_public_surfaces(event_id=processed[-1]["event_id"] if processed else None)
    return processed


CommandMembraneService._command_protocol_watcher_mode = _command_protocol_watcher_mode
CommandMembraneService._command_protocol_watched_surface_registry = _command_protocol_watched_surface_registry
CommandMembraneService._command_protocol_source_health = _command_protocol_source_health
CommandMembraneService._command_protocol_snapshot = _command_protocol_snapshot
CommandMembraneService._command_protocol_compute_changes = _command_protocol_compute_changes
CommandMembraneService._command_protocol_wait_for_event = _command_protocol_wait_for_event
CommandMembraneService._command_protocol_metrics = _command_protocol_metrics
CommandMembraneService._command_protocol_sync_public_surfaces = _command_protocol_sync_public_surfaces
CommandMembraneService.current_runtime_truth = _command_protocol_current_runtime_truth
CommandMembraneService.watched_surface_registry = _command_protocol_watched_surface_registry
CommandMembraneService.source_health = _command_protocol_source_health
CommandMembraneService.watch_command_folder = _command_protocol_watch_command_folder


def _command_v2_sync_public_surfaces_final(
    self: CommandMembraneService,
    event_id: str | None = None,
) -> dict[str, Any]:
    latest_event = self.recent_event_payloads(limit=1)
    last_event = latest_event[0] if latest_event else {}
    metrics = self.metrics()
    docs_gate = self.docs_gate_status()
    watch_registry = self.watched_surface_registry()
    payload = {
        "generated_at": utc_now(),
        "protocol_id": COMMAND_PROTOCOL_ID_V2,
        "active_surface": rel(self.config.command_surface_root),
        "watch_scope": "GLOBAL COMMAND only",
        "docs_gate": docs_gate,
        "docs_gate_status": docs_gate["state"],
        "active_membrane": COMMAND_ACTIVE_MEMBRANE,
        "queue_depth": max(int(metrics.get("event_count", 0)) - int(metrics.get("committed_count", 0)), 0),
        "last_event": last_event if event_id is None else self.packet_to_summary(self.load_event(event_id)),
        "metrics": metrics,
        "watch_registry": watch_registry,
        "current_runtime_truth": self.current_runtime_truth(),
    }
    write_json(PUBLIC_COMMAND_STATE_PATH, payload)
    write_json(self.config.watched_surface_registry_path, watch_registry)
    write_json(
        self.config.surface_health_path,
        {
            "generated_at": payload["generated_at"],
            "docs_gate_status": payload["docs_gate_status"],
            "command_root": rel(self.config.command_surface_root),
            "last_event_id": (payload["last_event"] or {}).get("event_id", ""),
        },
    )
    write_json(
        self.config.live_manifest_path,
        {
            "generated_at": payload["generated_at"],
            "protocol_id": payload["protocol_id"],
            "docs_gate_status": payload["docs_gate_status"],
            "active_surface": payload["active_surface"],
            "last_event_id": (payload["last_event"] or {}).get("event_id", ""),
        },
    )
    return payload


def _command_v2_public_state_final(self: CommandMembraneService) -> dict[str, Any]:
    return self.sync_public_surfaces()


CommandMembraneService.write_live_writeback_surfaces = _command_v2_write_live_writeback_surfaces
CommandMembraneService.ensure_protocol_artifacts = _command_v2_ensure_protocol_artifacts
CommandMembraneService.emit_change = _command_v2_emit_change
CommandMembraneService.score_candidate = _command_v2_score_candidate
CommandMembraneService.route_event = _command_v2_route_event
CommandMembraneService.metrics = _command_v2_metrics
CommandMembraneService.sync_public_surfaces = _command_v2_sync_public_surfaces_final
CommandMembraneService.public_state = _command_v2_public_state_final
CommandMembraneService.claim_event = _command_v2_claim_event
CommandMembraneService.commit_event = _command_v2_commit_event
CommandMembraneService.reinforce_event = _command_v2_reinforce_event

_bootstrap_command_membrane(globals())
