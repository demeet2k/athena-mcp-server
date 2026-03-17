from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = WORKSPACE_ROOT / "self_actualize"
DEFAULT_COMMAND_ROOT = WORKSPACE_ROOT / "GLOBAL COMMAND"
SCHEDULER_REGISTRY_PATH = SELF_ROOT / "astrological_scheduler_packets.json"
DEFAULT_HALL_PROTOCOL_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "GLOBAL_EMERGENT_GUILD_HALL"
    / "20_COMMAND_MEMBRANE_PROTOCOL.md"
)
DEFAULT_TEMPLE_DECREE_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "ATHENA TEMPLE"
    / "11_COMMAND_MEMBRANE_DECREE.md"
)

PROTOCOL_ID = "COMMAND_MEMBRANE_V1"
ROUTE_POLICY = "goal+salience+pheromone+coord"
ROUTE_CLASS = "scout.router.worker.archivist"
WATCH_MODE_EVENT = "event-driven"
WATCH_MODE_DEGRADED = "polling"
LATENCY_FORMULA = "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit"
CAPILLARY_FORMULA = "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)"
SETTLE_WINDOW_MS = 1500
DEDUPE_WINDOW_MS = 500
ROUTE_SELECTOR_TERMS = [
    "goal_fit",
    "salience",
    "capillary_strength",
    "coordinate_proximity",
    "freshness",
    "duplicate_penalty",
]

PACKET_FIELDS = [
    "event_id",
    "sensor_event_id",
    "ant_id",
    "source_root",
    "relative_path",
    "event_kind",
    "file_family",
    "tag",
    "goal",
    "change_summary",
    "priority",
    "confidence",
    "earth_ts_utc",
    "liminal_ts",
    "coord12",
    "delta_tau",
    "velocity_tau",
    "parent_event_id",
    "ttl",
    "pheromone",
    "state_hash",
    "route_class",
    "lineage",
    "scheduler_refs",
    "hsigma_ref",
    "status",
    "claim_state",
]

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

NOISE_SUFFIXES = {".tmp", ".temp", ".swp", ".lock", ".lck", ".part", ".crdownload"}
NOISE_NAMES = {"Thumbs.db", "desktop.ini"}
DOCUMENT_EXTS = {".md", ".txt", ".pdf", ".docx", ".html", ".zip"}
STRUCTURAL_KEYWORDS = {
    "protocol",
    "schema",
    "ledger",
    "law",
    "manifest",
    "queue",
    "claim",
    "route",
    "capillary",
    "decree",
}

ANTS = [
    {"ant_id": "SCOUT-01", "role": "scout", "coord_focus": 0.25, "pheromone_bias": 0.45, "domains": {"intake": 1.0}},
    {"ant_id": "ROUTER-01", "role": "router", "coord_focus": 0.50, "pheromone_bias": 0.50, "domains": {"routing": 1.0}},
    {"ant_id": "WORKER-01", "role": "worker", "coord_focus": 0.80, "pheromone_bias": 0.55, "domains": {"protocol": 1.0, "governance": 1.0, "runtime": 0.8}},
    {"ant_id": "WORKER-02", "role": "worker", "coord_focus": 0.60, "pheromone_bias": 0.52, "domains": {"document": 1.0, "manuscript": 1.0}},
    {"ant_id": "WORKER-03", "role": "worker", "coord_focus": 0.35, "pheromone_bias": 0.58, "domains": {"runtime": 1.0, "algorithm": 1.0}},
    {"ant_id": "WORKER-04", "role": "worker", "coord_focus": 0.65, "pheromone_bias": 0.50, "domains": {"archive": 1.0, "document": 0.8}},
    {"ant_id": "WORKER-05", "role": "worker", "coord_focus": 0.20, "pheromone_bias": 0.48, "domains": {"queue": 1.0, "ops": 0.9}},
    {"ant_id": "ARCHIVIST-01", "role": "archivist", "coord_focus": 0.70, "pheromone_bias": 0.60, "domains": {"ledger": 1.0, "archive": 1.0}},
]


@dataclass
class CommandMembraneConfig:
    workspace_root: Path = WORKSPACE_ROOT
    command_root: Path = DEFAULT_COMMAND_ROOT
    docs_gate_path: Path = SELF_ROOT / "live_docs_gate_status.md"
    protocol_json_path: Path = SELF_ROOT / "command_membrane_protocol.json"
    packet_schema_path: Path = SELF_ROOT / "command_membrane_packet_schema.json"
    capillary_law_path: Path = SELF_ROOT / "command_membrane_capillary_law.json"
    runtime_state_path: Path = SELF_ROOT / "command_membrane_runtime_state.json"
    packet_ledger_path: Path = SELF_ROOT / "command_membrane_packets.jsonl"
    route_ledger_path: Path = SELF_ROOT / "command_membrane_routes.jsonl"
    claim_ledger_path: Path = SELF_ROOT / "command_membrane_claims.jsonl"
    capillary_graph_path: Path = SELF_ROOT / "command_membrane_capillary_graph.json"
    projection_ledger_path: Path = SELF_ROOT / "command_membrane_projections.jsonl"
    event_store_root: Path = SELF_ROOT / "command_membrane_events"
    scheduler_registry_path: Path = SCHEDULER_REGISTRY_PATH
    hall_protocol_path: Path = DEFAULT_HALL_PROTOCOL_PATH
    temple_decree_path: Path = DEFAULT_TEMPLE_DECREE_PATH
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
    capillary_threshold: float = 0.35
    vein_threshold: float = 0.70
    decay_threshold: float = 0.35
    settle_window_ms: int = SETTLE_WINDOW_MS
    dedupe_window_ms: int = DEDUPE_WINDOW_MS
    route_weights: dict[str, float] = field(
        default_factory=lambda: {
            "goal_fit": 0.30,
            "salience": 0.18,
            "capillary_strength": 0.20,
            "coordinate_proximity": 0.18,
            "freshness": 0.10,
            "duplicate_penalty": 0.04,
        }
    )
    runtime_region: str = "ATHENA_LOCAL_RUNTIME"
    earth_geo_anchor: str = "US-CA-LosAngeles-LocalNode"
    local_zone_name: str = "America/Los_Angeles"

    def __post_init__(self) -> None:
        self.local_zone = ZoneInfo(self.local_zone_name)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def stable_scalar(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return round(int(digest, 16) / float(int("f" * 12, 16)), 6)


def relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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


class WindowsChangeSignal:
    FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
    FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
    FILE_NOTIFY_CHANGE_SIZE = 0x00000008
    FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
    FILE_NOTIFY_CHANGE_CREATION = 0x00000040
    WAIT_OBJECT_0 = 0x00000000
    WAIT_TIMEOUT = 0x00000102

    def __init__(self, root: Path) -> None:
        if os.name != "nt":
            raise RuntimeError("Windows event mode requires Windows.")
        kernel32 = ctypes.windll.kernel32
        flags = self.FILE_NOTIFY_CHANGE_FILE_NAME | self.FILE_NOTIFY_CHANGE_DIR_NAME | self.FILE_NOTIFY_CHANGE_SIZE | self.FILE_NOTIFY_CHANGE_LAST_WRITE | self.FILE_NOTIFY_CHANGE_CREATION
        self.kernel32 = kernel32
        self.handle = kernel32.FindFirstChangeNotificationW(str(root), True, flags)
        if self.handle in (0, ctypes.c_void_p(-1).value):
            raise OSError("FindFirstChangeNotificationW failed")

    def wait(self, timeout_ms: int) -> bool:
        status = self.kernel32.WaitForSingleObject(self.handle, timeout_ms)
        if status == self.WAIT_OBJECT_0:
            if not self.kernel32.FindNextChangeNotification(self.handle):
                raise OSError("FindNextChangeNotification failed")
            return True
        if status == self.WAIT_TIMEOUT:
            return False
        raise OSError(f"WaitForSingleObject failed: {status}")

    def close(self) -> None:
        if self.handle:
            self.kernel32.FindCloseChangeNotification(self.handle)
            self.handle = 0


class CommandMembraneService:
    def __init__(self, config: CommandMembraneConfig | None = None) -> None:
        self.config = config or CommandMembraneConfig()
        self.config.event_store_root.mkdir(parents=True, exist_ok=True)
        self.ensure_protocol_artifacts()
        self.ensure_runtime_state()

    def docs_gate_status(self) -> dict[str, Any]:
        credentials = self.config.workspace_root / "Trading Bot" / "credentials.json"
        token = self.config.workspace_root / "Trading Bot" / "token.json"
        status = "BLOCKED"
        detail = "blocked-by-missing-credentials"
        if credentials.exists() and token.exists():
            status = "BLOCKED"
            detail = "blocked-awaiting-live-pass"
            if self.config.docs_gate_path.exists():
                text = self.config.docs_gate_path.read_text(encoding="utf-8", errors="ignore")
                if "`LIVE`" in text:
                    status = "LIVE"
                    detail = "live-docs-ready"
                elif "`BLOCKED`" in text:
                    status = "BLOCKED"
                    detail = "blocked-by-live-gate"
        return {
            "status": status,
            "detail": detail,
            "source": relpath(self.config.docs_gate_path, self.config.workspace_root),
            "checked_paths": [
                relpath(credentials, self.config.workspace_root),
                relpath(token, self.config.workspace_root),
            ],
        }

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")

    def protocol_payload(self) -> dict[str, Any]:
        return {
            "protocol_id": PROTOCOL_ID,
            "command_root": relpath(self.config.command_root, self.config.workspace_root),
            "flow": "GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist",
            "watch_mode": {"primary": WATCH_MODE_EVENT, "fallback": WATCH_MODE_DEGRADED, "fallback_requires_explicit_opt_in": True},
            "routing_policy": {
                "policy": ROUTE_POLICY,
                "selector_terms": ROUTE_SELECTOR_TERMS,
                "weights": self.config.route_weights,
                "topk": self.config.topk,
                "claim_mode": self.config.claim_mode,
                "quorum": self.config.quorum,
                "ttl": self.config.ttl,
                "lease_ms": self.config.lease_ms,
            },
            "docs_gate": self.docs_gate_status(),
        }

    def packet_schema_payload(self) -> dict[str, Any]:
        return {"schema_id": "CommandEventPacketV1", "required_fields": PACKET_FIELDS, "coord12_keys": COORD12_KEYS}

    def capillary_law_payload(self) -> dict[str, Any]:
        return {
            "law_id": "CommandCapillaryLawV1",
            "formula": CAPILLARY_FORMULA,
            "coefficients": {"rho": self.config.rho, "alpha": self.config.alpha, "beta": self.config.beta, "gamma": self.config.gamma, "delta": self.config.delta},
            "thresholds": {"seed_max": self.config.capillary_threshold, "capillary_max": self.config.vein_threshold, "vein_min": self.config.vein_threshold},
            "initial_strength": 0.25,
        }

    def read_projection_rows(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.config.projection_ledger_path.exists():
            return []
        rows = [json.loads(line) for line in self.config.projection_ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return rows[:limit]

    def render_protocol_docs(self) -> None:
        docs_gate = self.docs_gate_status()
        projections = self.read_projection_rows(limit=12)
        hall_rows = [row for row in projections if row.get("surface") == "hall"]
        temple_rows = [row for row in projections if row.get("surface") == "temple"]
        hall_text = "\n".join(
            [
                "# Command Membrane Protocol",
                "",
                f"- Docs gate: `{docs_gate['status']}`",
                f"- Canonical ingress: `{relpath(self.config.command_root, self.config.workspace_root)}`",
                "- Flow: `GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`",
                f"- Watch mode: `{WATCH_MODE_EVENT}` primary, `{WATCH_MODE_DEGRADED}` explicit fallback",
                f"- Routing policy: `{ROUTE_POLICY}`",
                f"- Packet fields: `{', '.join(PACKET_FIELDS)}`",
                f"- Coord12: `{', '.join(COORD12_KEYS)}`",
                f"- Latency law: `{LATENCY_FORMULA}`",
                f"- Capillary law: `{CAPILLARY_FORMULA}`",
                "",
                "## Recent Projected Events",
                "",
            ]
            + ([f"- `{row['event_id']}` `{row['reason']}` `{row['relative_path']}`" for row in hall_rows] or ["- none yet"])
        )
        temple_text = "\n".join(
            [
                "# Command Membrane Decree",
                "",
                f"- Docs gate: `{docs_gate['status']}`",
                "- Decree: event-driven watch is canonical; silent polling fallback is forbidden.",
                "- Reinforcement occurs only after commit.",
                f"- Frozen route policy: `{ROUTE_POLICY}`",
                f"- Latency equation: `{LATENCY_FORMULA}`",
                f"- Capillary equation: `{CAPILLARY_FORMULA}`",
                "",
                "## Recent Projected Events",
                "",
            ]
            + ([f"- `{row['event_id']}` `{row['reason']}` `{row['relative_path']}`" for row in temple_rows] or ["- none yet"])
        )
        self.write_text(self.config.hall_protocol_path, hall_text)
        self.write_text(self.config.temple_decree_path, temple_text)

    def ensure_protocol_artifacts(self) -> None:
        write_json(self.config.protocol_json_path, self.protocol_payload())
        write_json(self.config.packet_schema_path, self.packet_schema_payload())
        write_json(self.config.capillary_law_path, self.capillary_law_payload())
        self.render_protocol_docs()

    def load_state(self) -> dict[str, Any]:
        return read_json(
            self.config.runtime_state_path,
            {
                "generated_at": iso_now(),
                "command_root": relpath(self.config.command_root, self.config.workspace_root),
                "watch_mode": WATCH_MODE_EVENT,
                "last_event_seq": 0,
                "last_liminal_seq": 0,
                "last_coord12": {},
                "last_earth_ts": "",
                "snapshot": {},
                "dedupe": {},
                "active_routes": {},
                "active_claims": {},
                "recent_projection_ids": [],
            },
        )

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = iso_now()
        write_json(self.config.runtime_state_path, state)

    def ensure_runtime_state(self) -> None:
        self.save_state(self.load_state())
        write_json(
            self.config.capillary_graph_path,
            read_json(
                self.config.capillary_graph_path,
                {"generated_at": iso_now(), "formula": CAPILLARY_FORMULA, "coefficients": self.capillary_law_payload()["coefficients"], "thresholds": self.capillary_law_payload()["thresholds"], "edges": {}},
            ),
        )

    def event_store_path(self, event_id: str) -> Path:
        return self.config.event_store_root / f"{event_id}.json"

    def load_event_record(self, event_id: str) -> dict[str, Any]:
        path = self.event_store_path(event_id)
        if not path.exists():
            raise FileNotFoundError(f"Unknown event_id: {event_id}")
        return read_json(path, {})

    def save_event_record(self, event_id: str, payload: dict[str, Any]) -> None:
        write_json(self.event_store_path(event_id), payload)

    def compute_state_hash(self, path: Path) -> str:
        if not path.exists():
            return "H:DELETED"
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        return f"H:{digest.hexdigest()}"

    def is_noise_path(self, path: Path) -> bool:
        name = path.name
        return name in NOISE_NAMES or name.startswith("~$") or name.startswith(".~") or name.lower().endswith("~") or path.suffix.lower() in NOISE_SUFFIXES

    def snapshot_directory(self) -> dict[str, dict[str, Any]]:
        snapshot: dict[str, dict[str, Any]] = {}
        if not self.config.command_root.exists():
            return snapshot
        for path in sorted(self.config.command_root.rglob("*")):
            if not path.is_file() or self.is_noise_path(path):
                continue
            stat = path.stat()
            snapshot[relpath(path, self.config.command_root)] = {"state_hash": self.compute_state_hash(path), "size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        return snapshot

    def compute_changes(self, previous: dict[str, dict[str, Any]], current: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        previous = previous or {}
        current = current or {}
        added = sorted(set(current) - set(previous))
        removed = sorted(set(previous) - set(current))
        modified = sorted(key for key in (set(previous) & set(current)) if previous[key]["state_hash"] != current[key]["state_hash"])
        changes: list[dict[str, Any]] = []
        added_by_signature: dict[tuple[str, int], list[str]] = {}
        for rel_path in added:
            entry = current[rel_path]
            added_by_signature.setdefault((entry["state_hash"], entry["size_bytes"]), []).append(rel_path)
        consumed_added: set[str] = set()
        consumed_removed: set[str] = set()
        for rel_path in removed:
            prev_entry = previous[rel_path]
            candidates = [candidate for candidate in added_by_signature.get((prev_entry["state_hash"], prev_entry["size_bytes"]), []) if candidate not in consumed_added]
            if candidates:
                new_path = candidates[0]
                consumed_added.add(new_path)
                consumed_removed.add(rel_path)
                entry = current[new_path]
                changes.append({"relative_path": new_path, "event_kind": "renamed", "state_hash": entry["state_hash"], "size_bytes": entry["size_bytes"], "mtime_ns": entry["mtime_ns"], "lineage": {"from": rel_path, "to": new_path}})
        for rel_path in added:
            if rel_path not in consumed_added:
                entry = current[rel_path]
                changes.append({"relative_path": rel_path, "event_kind": "created", "state_hash": entry["state_hash"], "size_bytes": entry["size_bytes"], "mtime_ns": entry["mtime_ns"], "lineage": {"from": "", "to": rel_path}})
        for rel_path in modified:
            entry = current[rel_path]
            changes.append({"relative_path": rel_path, "event_kind": "modified", "state_hash": entry["state_hash"], "size_bytes": entry["size_bytes"], "mtime_ns": entry["mtime_ns"], "lineage": {"from": rel_path, "to": rel_path}})
        for rel_path in removed:
            if rel_path not in consumed_removed:
                entry = previous[rel_path]
                changes.append({"relative_path": rel_path, "event_kind": "deleted", "state_hash": entry["state_hash"], "size_bytes": entry["size_bytes"], "mtime_ns": entry["mtime_ns"], "lineage": {"from": rel_path, "to": ""}})
        changes.sort(key=lambda item: (item["relative_path"], item["event_kind"]))
        return changes

    def queue_pressure(self, state: dict[str, Any]) -> float:
        pressure = (len(state.get("active_routes", {})) + len(state.get("active_claims", {})) + len(state.get("recent_projection_ids", []))) / 12.0
        return round(clamp(pressure, 0.0, 1.0), 6)

    def scheduler_registry(self) -> dict[str, Any]:
        return read_json(self.config.scheduler_registry_path, {})

    def scheduler_anchor_bundle(self) -> dict[str, Any]:
        registry = self.scheduler_registry()
        pantheon = {row.get("system_id"): row for row in registry.get("pantheon_lane_registry", [])}
        solar = pantheon.get("western_solar12", {})
        lunar = pantheon.get("vedic_lunar", {})
        planetary = pantheon.get("planetary_office", {})
        hsigma = registry.get("hsigma_overlay", {})
        shared12_phase = ""
        if hsigma:
            current_byte = hsigma.get("current_byte")
            current_coords = hsigma.get("current_coords", {})
            shared12_phase = f"B{current_byte}::{current_coords}" if current_byte is not None else ""
        if not shared12_phase:
            shared12_phase = str(solar.get("shared12_seat", ""))
        return {
            "solar_phase": str(solar.get("shared12_seat", "")),
            "lunar_phase": str(lunar.get("shared12_seat", "")),
            "shared12_phase": str(shared12_phase),
            "planetary_slot": str(planetary.get("shared12_seat") or planetary.get("native_cycle") or planetary.get("owner", "")),
        }

    def coord_scalar(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, list):
            if not value:
                return 0.0
            return sum(self.coord_scalar(item) for item in value) / float(len(value))
        text = str(value)
        try:
            return float(text)
        except ValueError:
            return stable_scalar(text)

    def build_coord12(self, *, now_utc: datetime, goal_salience: float, novelty: float, state: dict[str, Any]) -> dict[str, Any]:
        rotation = local_rotation_phase(now_utc, self.config.local_zone)
        orbital = orbital_phase(now_utc)
        scheduler = self.scheduler_anchor_bundle()
        sidereal = sidereal_phase(now_utc)
        solar_phase_value = self.coord_scalar(scheduler["solar_phase"]) if scheduler["solar_phase"] else rotation
        lunar_phase_value = self.coord_scalar(scheduler["lunar_phase"]) if scheduler["lunar_phase"] else lunar_phase(now_utc)
        return {
            "earth_utc_anchor": now_utc.isoformat(),
            "earth_rotation_phase": rotation,
            "earth_orbital_phase": orbital,
            "earth_geospatial_anchor": self.config.earth_geo_anchor,
            "solar_phase": round(solar_phase_value, 6),
            "lunar_phase": round(lunar_phase_value, 6),
            "local_sidereal_phase": sidereal,
            "canonical_sky_anchor": {
                "solar_phase": scheduler["solar_phase"],
                "lunar_phase": scheduler["lunar_phase"],
                "shared12_phase": scheduler["shared12_phase"],
                "planetary_slot": scheduler["planetary_slot"],
            },
            "runtime_region": self.config.runtime_region,
            "queue_pressure": self.queue_pressure(state),
            "goal_salience_vector": [round(goal_salience, 6), round(clamp(0.35 + (goal_salience * 0.55), 0.0, 1.0), 6)],
            "change_novelty_vector": [round(novelty, 6), round(goal_salience * novelty, 6)],
        }

    def coord12_vector(self, coord12: dict[str, Any]) -> list[float]:
        return [
            parse_iso(str(coord12.get("earth_utc_anchor", coord12.get("utc_atomic", iso_now())))).timestamp(),
            float(coord12.get("earth_rotation_phase", 0.0)),
            float(coord12.get("earth_orbital_phase", 0.0)),
            stable_scalar(str(coord12.get("earth_geospatial_anchor", self.config.earth_geo_anchor))),
            self.coord_scalar(coord12.get("solar_phase", 0.0)),
            self.coord_scalar(coord12.get("lunar_phase", 0.0)),
            self.coord_scalar(coord12.get("local_sidereal_phase", coord12.get("sidereal_phase", 0.0))),
            self.coord_scalar(coord12.get("canonical_sky_anchor", "")),
            stable_scalar(str(coord12.get("runtime_region", self.config.runtime_region))),
            float(coord12.get("queue_pressure", 0.0)),
            self.coord_scalar(coord12.get("goal_salience_vector", 0.0)),
            self.coord_scalar(coord12.get("change_novelty_vector", coord12.get("novelty_concentration", 0.0))),
        ]

    def delta_tau(self, current: dict[str, Any], previous: dict[str, Any]) -> float:
        if not previous:
            return 0.0
        total = 0.0
        for left, right in zip(self.coord12_vector(current), self.coord12_vector(previous)):
            total += (1.0 / len(COORD12_KEYS)) * ((left - right) ** 2)
        return round(math.sqrt(total), 6)

    def velocity_tau(self, delta_tau: float, earth_ts: str, previous_earth_ts: str) -> float:
        if not previous_earth_ts:
            return 0.0
        return round(delta_tau / max(0.001, parse_iso(earth_ts).timestamp() - parse_iso(previous_earth_ts).timestamp()), 6)

    def novelty_for_change(self, change: dict[str, Any]) -> float:
        base = 0.35
        kind_bonus = {"created": 0.25, "modified": 0.15, "renamed": 0.20, "deleted": 0.18}[change["event_kind"]]
        ext_bonus = 0.15 if Path(change["relative_path"]).suffix.lower() in DOCUMENT_EXTS else 0.05
        return round(clamp(base + kind_bonus + ext_bonus, 0.0, 1.0), 6)

    def classify_change(self, change: dict[str, Any]) -> tuple[str, str]:
        relative_lower = change["relative_path"].lower()
        if any(keyword in relative_lower for keyword in STRUCTURAL_KEYWORDS):
            return ("command.protocol.change", "govern-route-freeze")
        if Path(relative_lower).suffix.lower() in DOCUMENT_EXTS:
            return ("command.document.change", "detect-classify-assign")
        return ("command.artifact.change", "detect-classify-assign")

    def file_family_for_change(self, change: dict[str, Any]) -> str:
        relative_lower = change["relative_path"].lower()
        suffix = Path(relative_lower).suffix.lower()
        if any(keyword in relative_lower for keyword in STRUCTURAL_KEYWORDS):
            return "protocol"
        if suffix in {".md", ".txt", ".docx", ".pdf"}:
            return "document"
        if suffix == ".zip":
            return "archive"
        if "runtime" in relative_lower or "algorithm" in relative_lower:
            return "runtime"
        if "queue" in relative_lower or "route" in relative_lower:
            return "queue"
        return "artifact"

    def priority_for_change(self, change: dict[str, Any]) -> float:
        base = {"created": 0.82, "modified": 0.70, "renamed": 0.78, "deleted": 0.76}[change["event_kind"]]
        if any(keyword in change["relative_path"].lower() for keyword in STRUCTURAL_KEYWORDS):
            base += 0.12
        if Path(change["relative_path"]).suffix.lower() in DOCUMENT_EXTS:
            base += 0.06
        return round(clamp(base, 0.0, 1.0), 6)

    def make_event_id(self, now_utc: datetime, state: dict[str, Any]) -> str:
        state["last_event_seq"] = int(state.get("last_event_seq", 0)) + 1
        return f"EVT-{now_utc.strftime('%Y%m%d')}-{state['last_event_seq']:04d}"

    def make_liminal_ts(self, state: dict[str, Any]) -> str:
        state["last_liminal_seq"] = int(state.get("last_liminal_seq", 0)) + 1
        return f"LT-{state['last_liminal_seq']:09d}"

    def dedupe_key(self, change: dict[str, Any]) -> str:
        return f"{change['relative_path']}|{change['event_kind']}|{change['state_hash']}"

    def allow_change(self, change: dict[str, Any], state: dict[str, Any], detected_at: datetime) -> bool:
        dedupe = state.setdefault("dedupe", {})
        now_ms = int(detected_at.timestamp() * 1000)
        key = self.dedupe_key(change)
        last_ms = int(dedupe.get(key, 0))
        dedupe[key] = now_ms
        cutoff = now_ms - (self.config.dedupe_window_ms * 4)
        state["dedupe"] = {item_key: item_value for item_key, item_value in dedupe.items() if int(item_value) >= cutoff}
        return (now_ms - last_ms) >= self.config.dedupe_window_ms

    def emit_change(self, *, absolute_path: Path, change: dict[str, Any], state: dict[str, Any], parent: str = "ROOT", watch_mode: str = WATCH_MODE_EVENT, confidence: float = 0.98) -> dict[str, Any] | None:
        detected_at = datetime.now(timezone.utc)
        if not self.allow_change(change, state, detected_at):
            return None
        start_ns = time.perf_counter_ns()
        tag, goal = self.classify_change(change)
        file_family = self.file_family_for_change(change)
        priority = self.priority_for_change(change)
        novelty = self.novelty_for_change(change)
        coord12 = self.build_coord12(now_utc=detected_at, goal_salience=priority, novelty=novelty, state=state)
        delta_tau = self.delta_tau(coord12, state.get("last_coord12", {}))
        event_id = self.make_event_id(detected_at, state)
        sensor_event = {
            "event_id": event_id,
            "sensor_root": relpath(self.config.command_root, self.config.workspace_root),
            "source_path": change["relative_path"],
            "event_type": change["event_kind"],
            "detected_at": detected_at.isoformat(),
            "settled_at": (detected_at + timedelta(milliseconds=self.config.settle_window_ms)).isoformat(),
            "state_hash": change["state_hash"],
            "file_family": file_family,
        }
        packet = {
            "event_id": event_id,
            "sensor_event_id": event_id,
            "ant_id": "SCOUT-01",
            "source_root": relpath(self.config.command_root, self.config.workspace_root),
            "relative_path": change["relative_path"],
            "event_kind": change["event_kind"],
            "file_family": file_family,
            "tag": tag,
            "goal": goal,
            "change_summary": f"{change['event_kind']} {change['relative_path']}",
            "priority": priority,
            "confidence": confidence,
            "earth_ts_utc": coord12["earth_utc_anchor"],
            "liminal_ts": self.make_liminal_ts(state),
            "coord12": coord12,
            "delta_tau": delta_tau,
            "velocity_tau": self.velocity_tau(delta_tau, coord12["earth_utc_anchor"], state.get("last_earth_ts", "")),
            "parent_event_id": parent,
            "ttl": self.config.ttl,
            "pheromone": round(clamp(0.35 + (priority * 0.55), 0.0, 1.0), 6),
            "state_hash": change["state_hash"],
            "route_class": ROUTE_CLASS,
            "lineage": change["lineage"],
            "scheduler_refs": self.scheduler_anchor_bundle(),
            "hsigma_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_LIVE_HOLOGRAM_BUNDLE.json",
            "claim_state": {"status": "unclaimed", "claim_mode": self.config.claim_mode, "lease_ms": self.config.lease_ms},
            "status": "emitted",
            "source_abs_path": str(absolute_path),
            "watch_mode": watch_mode,
            "novelty": novelty,
            "detection_latency_ms": round(max(0.0, (detected_at.timestamp() * 1000.0) - (change["mtime_ns"] / 1_000_000.0)), 3),
            "encode_latency_ms": round((time.perf_counter_ns() - start_ns) / 1_000_000.0, 3),
            "detected_ts": detected_at.isoformat(),
            "emitted_ts": iso_now(),
            "docs_gate_status": self.docs_gate_status()["status"],
            "routing_policy": ROUTE_POLICY,
        }
        append_jsonl(self.config.packet_ledger_path, packet)
        self.save_event_record(packet["event_id"], {"sensor_event": sensor_event, "packet": packet, "route": None, "claim": None, "commit": None, "reinforcement": None, "projection_ids": []})
        state["last_coord12"] = coord12
        state["last_earth_ts"] = coord12["earth_utc_anchor"]
        return packet

    def goal_match(self, packet: dict[str, Any], ant: dict[str, Any]) -> float:
        relative_path = packet["relative_path"].lower()
        score = 0.0
        if "protocol" in relative_path or packet["tag"] == "command.protocol.change":
            score = max(score, ant["domains"].get("protocol", 0.0), ant["domains"].get("governance", 0.0))
        if Path(relative_path).suffix.lower() in DOCUMENT_EXTS:
            score = max(score, ant["domains"].get("document", 0.0), ant["domains"].get("manuscript", 0.0))
        if packet["event_kind"] in {"renamed", "deleted"}:
            score = max(score, ant["domains"].get("archive", 0.0), ant["domains"].get("ops", 0.0))
        if "route" in relative_path or "queue" in relative_path:
            score = max(score, ant["domains"].get("routing", 0.0), ant["domains"].get("queue", 0.0))
        if "runtime" in relative_path or "algorithm" in relative_path:
            score = max(score, ant["domains"].get("runtime", 0.0), ant["domains"].get("algorithm", 0.0))
        return round(clamp(score or (max(ant["domains"].values()) * 0.5), 0.0, 1.0), 6)

    def file_family_match(self, packet: dict[str, Any], ant: dict[str, Any]) -> float:
        family = str(packet.get("file_family") or self.file_family_for_change({"relative_path": packet["relative_path"], "event_kind": packet["event_kind"]}))
        if family == "protocol":
            return round(max(ant["domains"].get("protocol", 0.0), ant["domains"].get("governance", 0.0), ant["domains"].get("runtime", 0.0)), 6)
        if family == "document":
            return round(max(ant["domains"].get("document", 0.0), ant["domains"].get("manuscript", 0.0)), 6)
        if family == "archive":
            return round(max(ant["domains"].get("archive", 0.0), ant["domains"].get("ops", 0.0)), 6)
        if family == "queue":
            return round(max(ant["domains"].get("queue", 0.0), ant["domains"].get("runtime", 0.0)), 6)
        if family == "runtime":
            return round(max(ant["domains"].get("runtime", 0.0), ant["domains"].get("algorithm", 0.0)), 6)
        return round(max(ant["domains"].values()) * 0.5, 6)

    def salience_score(self, packet: dict[str, Any], ant: dict[str, Any]) -> float:
        coord12 = packet["coord12"]
        salience = self.coord_scalar(coord12.get("goal_salience_vector", packet.get("priority", 0.5)))
        return round(clamp((salience + ant["pheromone_bias"]) / 2.0, 0.0, 1.0), 6)

    def coord_proximity(self, packet: dict[str, Any], ant: dict[str, Any]) -> float:
        coord12 = packet["coord12"]
        novelty = self.coord_scalar(coord12.get("change_novelty_vector", coord12.get("novelty_concentration", 0.5)))
        return round(clamp(1.0 - abs(novelty - ant["coord_focus"]), 0.0, 1.0), 6)

    def freshness_score(self, packet: dict[str, Any]) -> float:
        emitted = packet.get("emitted_ts") or packet.get("earth_ts_utc")
        if not emitted:
            return 0.0
        age_seconds = max(0.0, datetime.now(timezone.utc).timestamp() - parse_iso(str(emitted)).timestamp())
        return round(clamp(1.0 - (age_seconds / 60.0), 0.0, 1.0), 6)

    def duplicate_penalty(self, ant: dict[str, Any], state: dict[str, Any]) -> float:
        active_claims = state.get("active_claims", {}) or {}
        active_count = sum(
            1
            for claim in active_claims.values()
            if claim.get("claim_status") == "active" and claim.get("ant_id") == ant["ant_id"]
        )
        return round(clamp(active_count / 3.0, 0.0, 1.0), 6)

    def pheromone_score(self, ant: dict[str, Any]) -> float:
        graph = read_json(self.config.capillary_graph_path, {"edges": {}})
        path_key = f"SCOUT-01>ROUTER-01>{ant['ant_id']}>ARCHIVIST-01"
        return round(clamp((ant["pheromone_bias"] + float(graph.get("edges", {}).get(path_key, {}).get("score", 0.0))) / 2.0, 0.0, 1.0), 6)

    def compute_route_for_packet(self, packet: dict[str, Any], state: dict[str, Any], topk: int | None = None) -> list[dict[str, Any]]:
        scored = []
        for ant in [item for item in ANTS if item["role"] == "worker"]:
            goal_fit = self.goal_match(packet, ant)
            salience = self.salience_score(packet, ant)
            capillary_strength = self.pheromone_score(ant)
            coordinate_proximity = self.coord_proximity(packet, ant)
            freshness = self.freshness_score(packet)
            duplicate_penalty = self.duplicate_penalty(ant, state)
            total = (
                (self.config.route_weights["goal_fit"] * goal_fit)
                + (self.config.route_weights["salience"] * salience)
                + (self.config.route_weights["capillary_strength"] * capillary_strength)
                + (self.config.route_weights["coordinate_proximity"] * coordinate_proximity)
                + (self.config.route_weights["freshness"] * freshness)
                - (self.config.route_weights["duplicate_penalty"] * duplicate_penalty)
            )
            scored.append(
                {
                    "ant_id": ant["ant_id"],
                    "goal_fit": goal_fit,
                    "salience": salience,
                    "capillary_strength": capillary_strength,
                    "coordinate_proximity": coordinate_proximity,
                    "freshness": freshness,
                    "duplicate_penalty": duplicate_penalty,
                    "score": round(total, 6),
                }
            )
        scored.sort(key=lambda item: (-item["score"], item["ant_id"]))
        return scored[: max(1, topk or self.config.topk)]

    def project_event(self, packet: dict[str, Any], *, surface: str, reason: str) -> dict[str, Any]:
        row = {"projection_id": f"PRJ-{packet['event_id']}-{surface.upper()}-{int(time.time() * 1000)}", "event_id": packet["event_id"], "surface": surface, "reason": reason, "relative_path": packet["relative_path"], "tag": packet["tag"], "created_at": iso_now()}
        append_jsonl(self.config.projection_ledger_path, row)
        state = self.load_state()
        state["recent_projection_ids"] = ([row["projection_id"]] + state.get("recent_projection_ids", []))[:50]
        self.save_state(state)
        record = self.load_event_record(packet["event_id"])
        record["projection_ids"] = ([row["projection_id"]] + record.get("projection_ids", []))[:20]
        self.save_event_record(packet["event_id"], record)
        self.render_protocol_docs()
        return row

    def requires_human_projection(self, packet: dict[str, Any], result: str) -> bool:
        relative_path = packet["relative_path"].lower()
        return result in {"fail", "ambig"} or any(keyword in relative_path for keyword in STRUCTURAL_KEYWORDS) or Path(relative_path).suffix.lower() in DOCUMENT_EXTS

    def route_event(self, event_id: str, *, policy: str = ROUTE_POLICY, topk: int | None = None, claim_mode: str | None = None, quorum: int | None = None) -> dict[str, Any]:
        self.sweep_expired_routes()
        self.sweep_expired_claims()
        if policy != ROUTE_POLICY:
            raise ValueError(f"Frozen policy mismatch: expected {ROUTE_POLICY}, got {policy}")
        state = self.load_state()
        record = self.load_event_record(event_id)
        existing_route = record.get("route") or {}
        if existing_route.get("route_status") == "routed":
            claim_deadline = existing_route.get("claim_deadline")
            if claim_deadline and parse_iso(claim_deadline) >= datetime.now(timezone.utc):
                return existing_route
            existing_route["route_status"] = "expired_unclaimed"
            record["route"] = existing_route
            record["packet"]["claim_state"] = {"status": "expired_unclaimed", "claim_mode": self.config.claim_mode, "lease_ms": self.config.lease_ms}
            self.save_event_record(event_id, record)
            state.get("active_routes", {}).pop(event_id, None)
        ranked = self.compute_route_for_packet(record["packet"], state=state, topk=topk or self.config.topk)
        selected = [item["ant_id"] for item in ranked]
        route = {
            "event_id": event_id,
            "policy": policy,
            "weights": self.config.route_weights,
            "selector_terms": ROUTE_SELECTOR_TERMS,
            "topk": min(len(ranked), topk or self.config.topk),
            "claim_mode": claim_mode or self.config.claim_mode,
            "quorum": quorum or self.config.quorum,
            "candidate_targets": ranked,
            "selected_targets": selected,
            "route_path": f"SCOUT-01>ROUTER-01>{selected[0]}>ARCHIVIST-01",
            "route_status": "routed",
            "created_at": iso_now(),
            "claim_deadline": (datetime.now(timezone.utc) + timedelta(milliseconds=self.config.lease_ms)).isoformat(),
            "duplicate_penalty": ranked[0]["duplicate_penalty"] if ranked else 0.0,
        }
        record["route"] = route
        record["packet"]["claim_state"] = {"status": "routed", "claim_mode": route["claim_mode"], "lease_ms": self.config.lease_ms, "claim_deadline": route["claim_deadline"], "selected_targets": selected}
        record["packet"]["status"] = "routed"
        self.save_event_record(event_id, record)
        append_jsonl(self.config.route_ledger_path, {"record_type": "route", **route})
        state.setdefault("active_routes", {})[event_id] = route
        self.save_state(state)
        return route

    def claim_event(self, event_id: str, *, ant_id: str | None = None, role: str = "worker", lease_ms: int | None = None) -> dict[str, Any]:
        self.sweep_expired_routes()
        self.sweep_expired_claims()
        if role != "worker":
            raise ValueError("Only worker claims are supported by the command membrane.")
        state = self.load_state()
        record = self.load_event_record(event_id)
        route = record.get("route")
        if not route or route.get("route_status") != "routed":
            raise RuntimeError(f"Event {event_id} is not currently routed.")
        if parse_iso(route["claim_deadline"]) < datetime.now(timezone.utc):
            raise RuntimeError(f"Claim window expired for {event_id}; reroute is required.")
        active_claim = state.get("active_claims", {}).get(event_id)
        if active_claim and active_claim.get("claim_status") == "active":
            owner = active_claim.get("ant_id")
            if owner == ant_id:
                raise RuntimeError(f"Event {event_id} already has an active lease for {owner}.")
            raise RuntimeError(f"Event {event_id} is already leased to {owner}.")
        selected = route["selected_targets"]
        chosen = ant_id or selected[0]
        if chosen not in selected:
            raise RuntimeError(f"{chosen} is not a routed worker for {event_id}.")
        claimed_at = iso_now()
        payload = {"claim_id": f"CLM-{event_id}-{chosen}", "event_id": event_id, "ant_id": chosen, "role": role, "lease_ms": lease_ms or self.config.lease_ms, "claimed_at": claimed_at, "expires_at": (parse_iso(claimed_at) + timedelta(milliseconds=lease_ms or self.config.lease_ms)).isoformat(), "claim_status": "active", "route_id": f"RTE-{event_id}", "worker_index": selected.index(chosen)}
        state.setdefault("active_claims", {})[event_id] = payload
        record["claim"] = payload
        record["packet"]["claim_state"] = {"status": "claimed", "claim_mode": self.config.claim_mode, "lease_ms": payload["lease_ms"], "ant_id": chosen, "expires_at": payload["expires_at"]}
        record["packet"]["status"] = "claimed"
        self.save_event_record(event_id, record)
        append_jsonl(self.config.claim_ledger_path, {"record_type": "claim", **payload})
        self.save_state(state)
        if self.requires_human_projection(record["packet"], result="success"):
            self.project_event(record["packet"], surface="hall", reason="worker_success_human_visible")
        return payload

    def reinforce_event(self, event_id: str, *, path: str | None = None, result: str, latency_score: float, noise_penalty: float = 0.0, allow_uncommitted: bool = False) -> dict[str, Any]:
        record = self.load_event_record(event_id)
        if not allow_uncommitted and not record.get("commit"):
            raise RuntimeError("Reinforcement requires a committed event.")
        route = record.get("route")
        if not route:
            raise RuntimeError(f"No route found for {event_id}")
        path = path or route["route_path"]
        graph = read_json(self.config.capillary_graph_path, {"generated_at": iso_now(), "formula": CAPILLARY_FORMULA, "coefficients": self.capillary_law_payload()["coefficients"], "thresholds": self.capillary_law_payload()["thresholds"], "edges": {}})
        edge = graph["edges"].get(path, {"edge_id": path, "from_node": "SCOUT-01", "to_node": route["selected_targets"][0], "path_key": path, "score": 0.25, "state_class": "seed", "usefulness": 0.0, "frequency": 0.0, "latency_penalty": 0.0, "noise_penalty": 0.0, "success_count": 0, "use_count": 0, "noise_count": 0, "last_result": "seed", "last_event_id": "", "last_reinforced_at_utc": ""})
        usefulness = 1.0 if result == "success" else 0.4 if result == "ambig" else 0.1
        use_count = int(edge.get("use_count", 0)) + 1
        success_count = int(edge.get("success_count", 0)) + (1 if result == "success" else 0)
        frequency = clamp(success_count / max(1, use_count), 0.0, 1.0)
        latency_penalty = clamp(1.0 - latency_score, 0.0, 1.0)
        noise_penalty = clamp(noise_penalty, 0.0, 1.0)
        score = clamp((self.config.rho * float(edge.get("score", 0.0))) + (self.config.alpha * usefulness) + (self.config.beta * frequency) - (self.config.gamma * latency_penalty) - (self.config.delta * noise_penalty), 0.0, 1.0)
        previous_class = edge.get("state_class", "seed")
        state_class = "vein" if score >= self.config.vein_threshold else "capillary" if score >= self.config.capillary_threshold else "seed"
        updated = {**edge, "score": round(score, 6), "state_class": state_class, "usefulness": round(usefulness, 6), "frequency": round(frequency, 6), "latency_penalty": round(latency_penalty, 6), "noise_penalty": round(noise_penalty, 6), "success_count": success_count, "use_count": use_count, "noise_count": int(edge.get("noise_count", 0)) + (1 if noise_penalty > 0 else 0), "last_result": result, "last_event_id": event_id, "last_reinforced_at_utc": iso_now()}
        graph["edges"][path] = updated
        graph["generated_at"] = iso_now()
        write_json(self.config.capillary_graph_path, graph)
        append_jsonl(self.config.route_ledger_path, {"record_type": "reinforce", "event_id": event_id, "path": path, "result": result, "latency_score": round(latency_score, 6), "noise_penalty": round(noise_penalty, 6), "state_class": state_class, "score": round(score, 6), "created_at": iso_now()})
        record["reinforcement"] = updated
        self.save_event_record(event_id, record)
        if previous_class != state_class and state_class in {"capillary", "vein"}:
            self.project_event(record["packet"], surface="hall", reason=f"{state_class}_promoted")
        return updated

    def commit_event(self, event_id: str, *, worker_id: str, result: str, summary: str = "") -> dict[str, Any]:
        self.sweep_expired_routes()
        self.sweep_expired_claims()
        state = self.load_state()
        record = self.load_event_record(event_id)
        claim = record.get("claim")
        route = record.get("route")
        packet = record.get("packet")
        if not claim or claim.get("claim_status") != "active":
            raise RuntimeError(f"No active claim found for {event_id}.")
        if claim["ant_id"] != worker_id:
            raise RuntimeError(f"{worker_id} does not own the active claim for {event_id}.")
        committed_at = iso_now()
        awareness_ms = round(max(0.0, (parse_iso(route["created_at"]) - parse_iso(packet["emitted_ts"])).total_seconds() * 1000.0), 3)
        claim_ms = round(max(0.0, (parse_iso(claim["claimed_at"]) - parse_iso(route["created_at"])).total_seconds() * 1000.0), 3)
        resolution_ms = round(max(0.0, (parse_iso(committed_at) - parse_iso(claim["claimed_at"])).total_seconds() * 1000.0), 3)
        t_sugar_ms = round(packet["detection_latency_ms"] + packet["encode_latency_ms"] + awareness_ms + claim_ms + resolution_ms, 3)
        receipt = {"event_id": event_id, "worker_id": worker_id, "result": result, "summary": summary, "route_path": route["route_path"], "detection_latency_ms": packet["detection_latency_ms"], "swarm_awareness_latency_ms": awareness_ms, "claim_latency_ms": claim_ms, "resolution_latency_ms": resolution_ms, "commit_latency_ms": resolution_ms, "t_sugar_ms": t_sugar_ms, "delta_tau": packet["delta_tau"], "liminal_velocity": packet["velocity_tau"], "recorded_at": committed_at, "replay_ptr": relpath(self.event_store_path(event_id), self.config.workspace_root)}
        record["commit"] = receipt
        record["packet"]["status"] = "committed"
        claim["claim_status"] = "committed"
        claim["committed_at"] = committed_at
        claim["result"] = result
        state.get("active_claims", {}).pop(event_id, None)
        if event_id in state.get("active_routes", {}):
            state["active_routes"][event_id]["route_status"] = "committed"
        self.save_event_record(event_id, record)
        append_jsonl(self.config.claim_ledger_path, {"record_type": "commit", "event_id": event_id, "worker_id": worker_id, "result": result, "summary": summary, "recorded_at": committed_at, "route_path": route["route_path"]})
        self.reinforce_event(event_id, result=result, latency_score=clamp(1.0 / (1.0 + (t_sugar_ms / 1000.0)), 0.0, 1.0), noise_penalty=route["duplicate_penalty"])
        self.save_state(state)
        if result in {"fail", "ambig"}:
            self.project_event(packet, surface="temple", reason=f"route_{result}")
        elif self.requires_human_projection(packet, result=result):
            self.project_event(packet, surface="hall", reason="worker_success_human_visible")
        return receipt

    def sweep_expired_routes(self, *, now: datetime | None = None) -> list[str]:
        now = now or datetime.now(timezone.utc)
        state = self.load_state()
        expired = []
        active_routes = dict(state.get("active_routes", {}))
        for event_id, route in list(active_routes.items()):
            if route.get("route_status") != "routed" or event_id in state.get("active_claims", {}) or parse_iso(route["claim_deadline"]) >= now:
                continue
            route["route_status"] = "expired_unclaimed"
            append_jsonl(self.config.route_ledger_path, {"record_type": "route_expired", "event_id": event_id, "created_at": iso_now(), "route_path": route["route_path"]})
            record = self.load_event_record(event_id)
            record["route"] = route
            record["packet"]["claim_state"] = {"status": "expired_unclaimed", "claim_mode": self.config.claim_mode, "lease_ms": self.config.lease_ms}
            record["packet"]["status"] = "expired_unclaimed"
            self.save_event_record(event_id, record)
            self.project_event(record["packet"], surface="temple", reason="route_expired_unclaimed")
            expired.append(event_id)
            active_routes.pop(event_id, None)
        state["active_routes"] = active_routes
        self.save_state(state)
        return expired

    def sweep_expired_claims(self, *, now: datetime | None = None) -> list[str]:
        now = now or datetime.now(timezone.utc)
        state = self.load_state()
        expired = []
        active_claims = dict(state.get("active_claims", {}))
        for event_id, claim in list(active_claims.items()):
            if claim.get("claim_status") != "active" or parse_iso(claim["expires_at"]) >= now:
                continue
            claim["claim_status"] = "expired"
            append_jsonl(self.config.claim_ledger_path, {"record_type": "claim_expired", "event_id": event_id, "ant_id": claim["ant_id"], "recorded_at": iso_now()})
            append_jsonl(self.config.route_ledger_path, {"record_type": "requeue_required", "event_id": event_id, "created_at": iso_now()})
            record = self.load_event_record(event_id)
            record["claim"] = claim
            record["packet"]["claim_state"] = {"status": "expired_needs_reroute", "claim_mode": self.config.claim_mode, "lease_ms": self.config.lease_ms}
            record["packet"]["status"] = "expired_needs_reroute"
            state.get("active_routes", {}).pop(event_id, None)
            self.save_event_record(event_id, record)
            self.project_event(record["packet"], surface="temple", reason="claim_lease_expired")
            expired.append(event_id)
            active_claims.pop(event_id, None)
        state["active_claims"] = active_claims
        self.save_state(state)
        return expired

    def build(self) -> dict[str, Any]:
        state = self.load_state()
        if not state.get("snapshot"):
            state["snapshot"] = self.snapshot_directory()
            self.save_state(state)
        return {"truth": "OK", "command_root": relpath(self.config.command_root, self.config.workspace_root), "docs_gate": self.docs_gate_status()}

    def watch(self, *, mode: str = WATCH_MODE_EVENT, interval: float = 2.0, timeout_secs: int = 0, max_events: int = 0) -> list[dict[str, Any]]:
        if mode not in {WATCH_MODE_EVENT, WATCH_MODE_DEGRADED}:
            raise ValueError(f"Unsupported watch mode: {mode}")
        if mode == WATCH_MODE_EVENT and os.name != "nt":
            raise RuntimeError("EVENT_DRIVEN mode is only supported on Windows.")
        state = self.load_state()
        previous_snapshot = state.get("snapshot")
        if previous_snapshot is None:
            previous_snapshot = {}
        state["snapshot"] = previous_snapshot
        state["watch_mode"] = mode
        self.save_state(state)
        results: list[dict[str, Any]] = []
        started = time.monotonic()

        def process_snapshot(current_snapshot: dict[str, dict[str, Any]], watch_mode: str) -> None:
            nonlocal previous_snapshot
            changes = self.compute_changes(previous_snapshot, current_snapshot)
            for change in changes:
                packet = self.emit_change(absolute_path=self.config.command_root / change["relative_path"], change=change, state=state, watch_mode=watch_mode, confidence=0.98 if watch_mode == WATCH_MODE_EVENT else 0.90)
                if not packet:
                    continue
                route = self.route_event(packet["event_id"])
                results.append({"event_id": packet["event_id"], "relative_path": packet["relative_path"], "event_kind": packet["event_kind"], "selected_targets": route["selected_targets"], "watch_mode": watch_mode})
                if max_events and len(results) >= max_events:
                    break
            previous_snapshot = current_snapshot
            state["snapshot"] = current_snapshot
            self.save_state(state)

        if mode == WATCH_MODE_EVENT:
            watcher = WindowsChangeSignal(self.config.command_root)
            try:
                while True:
                    self.sweep_expired_routes()
                    self.sweep_expired_claims()
                    if watcher.wait(timeout_ms=self.config.settle_window_ms):
                        time.sleep(self.config.settle_window_ms / 1000.0)
                        process_snapshot(self.snapshot_directory(), WATCH_MODE_EVENT)
                    if (timeout_secs and (time.monotonic() - started) >= timeout_secs) or (max_events and len(results) >= max_events):
                        break
            finally:
                watcher.close()
            return results

        while True:
            self.sweep_expired_routes()
            self.sweep_expired_claims()
            current_snapshot = self.snapshot_directory()
            if current_snapshot != previous_snapshot:
                process_snapshot(current_snapshot, WATCH_MODE_DEGRADED)
            if (timeout_secs and (time.monotonic() - started) >= timeout_secs) or (max_events and len(results) >= max_events):
                break
            time.sleep(interval)
        return results

    def emit_manual(self, *, path: str, event_kind: str = "modified", goal: str | None = None) -> dict[str, Any]:
        state = self.load_state()
        absolute_path = Path(path)
        if not absolute_path.is_absolute():
            absolute_path = self.config.command_root / path
        exists = absolute_path.exists()
        change = {"relative_path": relpath(absolute_path, self.config.command_root), "event_kind": event_kind, "state_hash": self.compute_state_hash(absolute_path) if exists else "H:DELETED", "size_bytes": absolute_path.stat().st_size if exists else 0, "mtime_ns": absolute_path.stat().st_mtime_ns if exists else time.time_ns(), "lineage": {"from": "", "to": relpath(absolute_path, self.config.command_root)}}
        packet = self.emit_change(absolute_path=absolute_path, change=change, state=state, watch_mode="MANUAL", confidence=0.95)
        if packet is None:
            raise RuntimeError("Event was deduplicated and not re-emitted.")
        if goal:
            record = self.load_event_record(packet["event_id"])
            record["packet"]["goal"] = goal
            self.save_event_record(packet["event_id"], record)
            packet["goal"] = goal
        self.save_state(state)
        return packet


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Athena command membrane runtime.")
    subparsers = cli.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build", help="Freeze protocol artifacts and initialize runtime state.")
    watch = subparsers.add_parser("watch", help="Watch GLOBAL COMMAND with Windows-native events.")
    watch.add_argument("--root", default="GLOBAL COMMAND")
    watch.add_argument("--mode", choices=[WATCH_MODE_EVENT, WATCH_MODE_DEGRADED], default=WATCH_MODE_EVENT)
    watch.add_argument("--interval", type=float, default=2.0)
    watch.add_argument("--timeout-secs", type=int, default=0)
    watch.add_argument("--max-events", type=int, default=0)
    emit = subparsers.add_parser("emit", help="Emit one event packet manually.")
    emit.add_argument("--root", default="GLOBAL COMMAND")
    emit.add_argument("--path", required=True)
    emit.add_argument("--kind", choices=["created", "modified", "renamed", "deleted"], default="modified")
    emit.add_argument("--goal", default="")
    route = subparsers.add_parser("route", help="Route a previously emitted packet.")
    route.add_argument("event_id")
    route.add_argument("--root", default="GLOBAL COMMAND")
    route.add_argument("--policy", default=ROUTE_POLICY)
    route.add_argument("--topk", type=int, default=5)
    route.add_argument("--claim-mode", default="first-lease")
    route.add_argument("--quorum", type=int, default=1)
    claim = subparsers.add_parser("claim", help="Claim a routed packet with first-lease semantics.")
    claim.add_argument("event_id")
    claim.add_argument("--root", default="GLOBAL COMMAND")
    claim.add_argument("--ant-id")
    claim.add_argument("--role", default="worker")
    claim.add_argument("--lease-ms", type=int, default=1200)
    commit = subparsers.add_parser("commit", help="Commit a claimed packet and reinforce the route.")
    commit.add_argument("event_id")
    commit.add_argument("--root", default="GLOBAL COMMAND")
    commit.add_argument("--result", choices=["success", "fail", "ambig"], default="success")
    commit.add_argument("--worker-id", required=True)
    commit.add_argument("--summary", default="")
    reinforce = subparsers.add_parser("reinforce", help="Manually reinforce a committed route.")
    reinforce.add_argument("event_id")
    reinforce.add_argument("--root", default="GLOBAL COMMAND")
    reinforce.add_argument("--path", default="")
    reinforce.add_argument("--result", choices=["success", "fail", "ambig"], default="success")
    reinforce.add_argument("--latency-score", type=float, required=True)
    reinforce.add_argument("--noise-penalty", type=float, default=0.0)
    return cli


def config_from_root(root: str) -> CommandMembraneConfig:
    command_root = Path(root)
    if not command_root.is_absolute():
        command_root = WORKSPACE_ROOT / root
    return CommandMembraneConfig(command_root=command_root)


def main() -> int:
    args = parser().parse_args()
    if args.command == "build":
        print(json.dumps(CommandMembraneService().build(), indent=2))
        return 0
    if args.command == "watch":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.watch(mode=args.mode, interval=args.interval, timeout_secs=args.timeout_secs, max_events=args.max_events), indent=2))
        return 0
    if args.command == "emit":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.emit_manual(path=args.path, event_kind=args.kind, goal=args.goal or None), indent=2))
        return 0
    if args.command == "route":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.route_event(args.event_id, policy=args.policy, topk=args.topk, claim_mode=args.claim_mode, quorum=args.quorum), indent=2))
        return 0
    if args.command == "claim":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.claim_event(args.event_id, ant_id=args.ant_id, role=args.role, lease_ms=args.lease_ms), indent=2))
        return 0
    if args.command == "commit":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.commit_event(args.event_id, worker_id=args.worker_id, result=args.result, summary=args.summary), indent=2))
        return 0
    if args.command == "reinforce":
        service = CommandMembraneService(config_from_root(args.root))
        print(json.dumps(service.reinforce_event(args.event_id, path=args.path or None, result=args.result, latency_score=args.latency_score, noise_penalty=args.noise_penalty, allow_uncommitted=False), indent=2))
        return 0
    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
