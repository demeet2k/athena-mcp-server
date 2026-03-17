from __future__ import annotations

import json
import math
import re
import statistics
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from zoneinfo import ZoneInfo

from self_actualize.runtime.derive_qshrink_ap6d_full_corpus_integration import (
    ROOT_CLASSIFICATION,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MASTER_LEDGER_ROOT = SELF_ACTUALIZE_ROOT / "master_ledger"

CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "archive_atlas.json"
AUTHORITY_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_authority_registry.json"
ROUTE_COVERAGE_PATH = SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_route_coverage_registry.json"
APPENDIX_GOVERNANCE_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_appendix_governance_ledger.json"
)
BASIS_CROSSWALK_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_basis_crosswalk_registry.json"
)
AWAKENING_STAGE_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_awakening_stage_registry.json"
)
VISUAL_NODE_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_node_registry.json"
VISUAL_EDGE_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_edge_registry.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
ASTRO_SCHEDULER_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ASTROLOGICAL_SCHEDULER_REGISTRY.md"
)
TESSERACT_HEADER_SCHEMA_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "70_SCHEMAS" / "17_TESSERACT_HEADER_SCHEMA.md"
)
TCOORD_SCHEMA_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "70_SCHEMAS" / "18_TCOORD_SCHEMA.md"
ROUTE_PLAN_SCHEMA_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "70_SCHEMAS" / "19_ROUTE_PLAN_SCHEMA.md"
)
QSHRINK_RAW_ATLAS_PATH = (
    WORKSPACE_ROOT
    / "Athena FLEET"
    / "QSHRINK2_CORPUS_ECOSYSTEM"
    / "02_QSHRINK2_CORPUS_ATLAS.json"
)

OUTPUT_JSON_PATH = MASTER_LEDGER_ROOT / "ATHENACHKA_MASTER_LEDGER.json"
OUTPUT_MD_PATH = MASTER_LEDGER_ROOT / "ATHENACHKA_MASTER_LEDGER.md"

DERIVATION_VERSION = "2026-03-13.athenachka-master-ledger.rev2"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_athenachka_master_ledger"
DOCS_GATE_EXPECTED = "BLOCKED"
LEGACY_WITNESS_RECORD_COUNT = 8656
LOCAL_TZ = ZoneInfo("America/Los_Angeles")
LOCAL_TZ_NAME = "America/Los_Angeles"
APPROX_LOCATION = {
    "label": "Burbank, California, United States",
    "latitude": 34.18028,
    "longitude": -118.32833,
    "precision": "approximate",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".csv",
    ".ps1",
    ".sh",
    ".cmd",
    ".html",
    ".htm",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".ini",
    ".xml",
    ".sql",
}
EXACT_TEXT_SIZE_LIMIT = 1_500_000
MAX_HEADING_NODES = 12
MAX_SEGMENT_LINES = 200
MAX_SEGMENT_PARAGRAPHS = 20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slugify(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = lowered.strip("-")
    return lowered or "unknown"


def unique_list(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def dt_to_utc_iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).isoformat()


def dt_to_local_iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(LOCAL_TZ).isoformat()


def parse_docs_gate_status() -> dict[str, Any]:
    text = DOCS_GATE_PATH.read_text(encoding="utf-8", errors="ignore")
    missing_files: list[str] = []
    if "Trading Bot/credentials.json" in text:
        missing_files.append("Trading Bot/credentials.json")
    if "Trading Bot/token.json" in text:
        missing_files.append("Trading Bot/token.json")
    return {
        "status": "BLOCKED" if "BLOCKED" in text else "UNKNOWN",
        "source_path": str(DOCS_GATE_PATH),
        "missing_files": missing_files,
        "local_only": True,
        "checked_at": utc_now(),
    }


def split_archive_locator(locator: str) -> tuple[Path, str] | None:
    if "::" not in locator:
        return None
    outer, inner = locator.split("::", 1)
    return Path(outer), inner


def file_stat_bundle(locator: str, fallback_modified_at: str) -> dict[str, Any]:
    parsed = split_archive_locator(locator)
    last_observed = utc_now()
    if parsed is not None:
        modified_dt = parse_iso(fallback_modified_at)
        return {
            "file_created_at": "",
            "file_modified_at": dt_to_utc_iso(modified_dt),
            "last_observed_at": last_observed,
            "timestamp_precision": "bounded",
            "source_local_timestamp": dt_to_local_iso(modified_dt),
            "utc_timestamp": dt_to_utc_iso(modified_dt),
        }
    path = Path(locator)
    if not path.exists():
        modified_dt = parse_iso(fallback_modified_at)
        return {
            "file_created_at": "",
            "file_modified_at": dt_to_utc_iso(modified_dt),
            "last_observed_at": last_observed,
            "timestamp_precision": "near-exact" if modified_dt else "unresolved",
            "source_local_timestamp": dt_to_local_iso(modified_dt),
            "utc_timestamp": dt_to_utc_iso(modified_dt),
        }
    stat = path.stat()
    created_dt = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
    modified_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    return {
        "file_created_at": created_dt.isoformat(),
        "file_modified_at": modified_dt.isoformat(),
        "last_observed_at": last_observed,
        "timestamp_precision": "exact",
        "source_local_timestamp": dt_to_local_iso(modified_dt),
        "utc_timestamp": dt_to_utc_iso(modified_dt),
    }


def julian_date(dt: datetime) -> float:
    utc_dt = dt.astimezone(timezone.utc)
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + utc_dt.microsecond / 3_600_000_000.0
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
        + hour / 24.0
    )


def wrap_degrees(value: float) -> float:
    return value % 360.0


def gmst_hours(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000.0
    )
    return wrap_degrees(gmst) / 15.0


def sidereal_time_hours(jd: float, longitude_deg: float) -> float:
    return (gmst_hours(jd) + longitude_deg / 15.0) % 24.0


def solar_longitude_deg(jd: float) -> float:
    n = jd - 2451545.0
    l = wrap_degrees(280.460 + 0.9856474 * n)
    g = wrap_degrees(357.528 + 0.9856003 * n)
    g_rad = math.radians(g)
    return wrap_degrees(l + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad))


def lunar_longitude_deg(jd: float) -> float:
    d = jd - 2451545.0
    l0 = wrap_degrees(218.316 + 13.176396 * d)
    m_moon = wrap_degrees(134.963 + 13.064993 * d)
    m_sun = wrap_degrees(357.529 + 0.98560028 * d)
    d_moon = wrap_degrees(297.850 + 12.190749 * d)
    m_moon_rad = math.radians(m_moon)
    d_moon_rad = math.radians(d_moon)
    m_sun_rad = math.radians(m_sun)
    longitude = (
        l0
        + 6.289 * math.sin(m_moon_rad)
        + 1.274 * math.sin(2 * d_moon_rad - m_moon_rad)
        + 0.658 * math.sin(2 * d_moon_rad)
        + 0.214 * math.sin(2 * m_moon_rad)
        - 0.186 * math.sin(m_sun_rad)
    )
    return wrap_degrees(longitude)


ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def zodiac_position(longitude: float) -> dict[str, Any]:
    sign_index = int(longitude // 30) % 12
    degree = longitude % 30.0
    return {
        "sign": ZODIAC_SIGNS[sign_index],
        "degree": round(degree, 3),
    }


def lunar_phase_name(phase_angle: float) -> str:
    if phase_angle < 22.5 or phase_angle >= 337.5:
        return "New Moon"
    if phase_angle < 67.5:
        return "Waxing Crescent"
    if phase_angle < 112.5:
        return "First Quarter"
    if phase_angle < 157.5:
        return "Waxing Gibbous"
    if phase_angle < 202.5:
        return "Full Moon"
    if phase_angle < 247.5:
        return "Waning Gibbous"
    if phase_angle < 292.5:
        return "Last Quarter"
    return "Waning Crescent"


def astro_overlay(timestamp_iso: str) -> dict[str, Any]:
    dt = parse_iso(timestamp_iso)
    if dt is None:
        return {
            "status": "pending",
            "reason": "missing_timestamp",
        }
    local_dt = dt.astimezone(LOCAL_TZ)
    jd = julian_date(dt)
    solar_lon = solar_longitude_deg(jd)
    lunar_lon = lunar_longitude_deg(jd)
    phase_angle = wrap_degrees(lunar_lon - solar_lon)
    return {
        "status": "computed",
        "truth_policy": "structural calendar layer, not scientific proof",
        "local_calendar_date": local_dt.date().isoformat(),
        "local_clock_time": local_dt.timetz().isoformat(),
        "utc_time": dt.astimezone(timezone.utc).isoformat(),
        "julian_date": round(jd, 6),
        "sidereal_time_hours_local": round(
            sidereal_time_hours(jd, APPROX_LOCATION["longitude"]), 6
        ),
        "solar_longitude": round(solar_lon, 6),
        "lunar_longitude": round(lunar_lon, 6),
        "lunar_phase_angle": round(phase_angle, 6),
        "lunar_phase": lunar_phase_name(phase_angle),
        "solar_zodiac": zodiac_position(solar_lon),
        "lunar_zodiac": zodiac_position(lunar_lon),
        "house_context": "pending_exact_location_basis",
        "location_basis": APPROX_LOCATION,
        "precessional_frame": "tropical_structural",
    }


def load_support_maps() -> dict[str, Any]:
    live_atlas = load_json(CORPUS_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    authority = load_json(AUTHORITY_REGISTRY_PATH)
    route_coverage = load_json(ROUTE_COVERAGE_PATH)
    appendix_governance = load_json(APPENDIX_GOVERNANCE_PATH)
    basis_crosswalk = load_json(BASIS_CROSSWALK_PATH)
    awakening_stage = load_json(AWAKENING_STAGE_PATH)
    raw_qshrink = load_json(QSHRINK_RAW_ATLAS_PATH)
    return {
        "live_atlas": live_atlas,
        "archive_atlas": archive_atlas,
        "authority": authority,
        "route_coverage": route_coverage,
        "appendix_governance": appendix_governance,
        "basis_crosswalk": basis_crosswalk,
        "awakening_stage": awakening_stage,
        "raw_qshrink": raw_qshrink,
        "live_map": {record["record_id"]: record for record in live_atlas.get("records", [])},
        "archive_map": {record["record_id"]: record for record in archive_atlas.get("records", [])},
        "governance_map": {row["record_id"]: row for row in appendix_governance.get("rows", [])},
        "basis_map": {row["record_id"]: row for row in basis_crosswalk.get("rows", [])},
        "stage_map": {
            row["record_id"]: row for row in awakening_stage.get("record_assignments", [])
        },
    }


LAYER_REGISTRY = [
    {"layer_id": "L1", "name": "Metro", "description": "Discrete transfer-optimized routing graph."},
    {"layer_id": "L2", "name": "Mycelium", "description": "Branching adaptive diffusion graph."},
    {"layer_id": "L3", "name": "Neural", "description": "Convergence/divergence associative graph."},
    {"layer_id": "L4", "name": "Zero", "description": "Collapse and normalization pole."},
    {"layer_id": "L5", "name": "Liminal", "description": "Phase-shift and uncertainty mediation layer."},
    {"layer_id": "L6", "name": "Aether", "description": "Expansion, lift, and outward projection pole."},
    {"layer_id": "L7", "name": "Tunnel", "description": "Nonlocal bypass layer."},
    {"layer_id": "L8", "name": "BridgeReturn", "description": "Transfer, return, fold, and hinge layer."},
    {"layer_id": "L9", "name": "Dimensional", "description": "Lift, crossing, and manifold transit layer."},
    {"layer_id": "L10", "name": "ReplayWitnessProof", "description": "Evidentiary replay, witness, and proof layer."},
    {"layer_id": "L11", "name": "SeedRegeneration", "description": "Compression, seed, and regeneration layer."},
]

DIMENSIONAL_STRATA = [
    {"stratum_id": "D0", "name": "Planar routing stratum", "description": "Metro, mycelium, and neural surface-level navigation."},
    {"stratum_id": "D1", "name": "Hinge and liminal stratum", "description": "Transfer, phase-shift, bridge approach, and ambiguity mediation."},
    {"stratum_id": "D2", "name": "Pole stratum", "description": "Zero collapse and aether expansion."},
    {"stratum_id": "D3", "name": "Nonlocal transit stratum", "description": "Tunnels, lifts, crossings, and nonlocal bridgework."},
    {"stratum_id": "D4", "name": "Evidentiary and regenerative stratum", "description": "Replay, witness, proof closure, seed preservation, and regeneration."},
]

ROUTE_GATE_BOOK = {
    "R1": {"name": "Metro rail", "q0": {0, 1}, "q1": {0, 1}, "q2": {0, 1}, "q3": {0, 1}},
    "R2": {"name": "Mycelial filament", "q0": {1, 2}, "q1": {2, 3}, "q2": {1, 2}, "q3": {2, 3}},
    "R3": {"name": "Neural link", "q0": {1, 2, 3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "R4": {"name": "Zero-collapse route", "q0": {0, 2}, "q1": {0, 1}, "q2": {0, 1, 2}, "q3": {0, 2}},
    "R5": {"name": "Liminal transition route", "q0": {0, 1, 2, 3}, "q1": {1, 2, 3}, "q2": {1, 2}, "q3": {3}},
    "R6": {"name": "Aether expansion route", "q0": {1, 3}, "q1": {0, 2}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "R7": {"name": "Tunnel bypass route", "q0": {0, 1, 2, 3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {3}},
    "R8": {"name": "Bridge and hinge route", "q0": {0, 1, 3}, "q1": {0, 1, 3}, "q2": {0, 1, 2, 3}, "q3": {0, 1, 3}},
    "R9": {"name": "Dimensional lift route", "q0": {1, 3}, "q1": {1, 2, 3}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "R10": {"name": "Manifold crossing route", "q0": {2, 3}, "q1": {3}, "q2": {1, 2, 3}, "q3": {3}},
    "R11": {"name": "Replay loop", "q0": {3}, "q1": {0, 1, 3}, "q2": {1, 2, 3}, "q3": {0, 3}},
    "R12": {"name": "Witness and proof-bearing route", "q0": {0, 3}, "q1": {0, 2}, "q2": {0, 1, 2}, "q3": {0, 2, 3}},
    "R13": {"name": "Seed and regeneration route", "q0": {1, 3}, "q1": {2, 3}, "q2": {1, 2, 3}, "q3": {2, 3}},
}

NEXUS_CLASS_BOOK = {
    "Z0": {"node_name": "Global Zero Anchor", "node_class": "zero_anchor", "host_layers": ["Zero", "Liminal", "Tunnel", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R4", "R5", "R7", "R8", "R9", "R11"], "deg_s": 6, "cen": 0.86, "span": 4, "w0": 83, "polarity": "Z++", "related_hubs": ["L0", "TE", "DB", "RA"], "touching_tunnels": ["T-ZC", "T-RR", "T-BC"], "status": "seated", "q0": {0, 2}, "q1": {0, 1}, "q2": {0, 1, 2}, "q3": {0, 2, 3}},
    "ZL": {"node_name": "Local Zero Point", "node_class": "local_zero_point", "host_layers": ["Zero", "Liminal", "Tunnel"], "incident_routes": ["R4", "R5", "R7"], "deg_s": 3, "cen": 0.43, "span": 3, "w0": 50, "polarity": "Z+", "related_hubs": ["L0", "TE", "Z0"], "touching_tunnels": ["T-ZC"], "status": "seated", "q0": {0, 2}, "q1": {0, 2}, "q2": {0, 1, 2}, "q3": {0, 2}},
    "A0": {"node_name": "Primary Aether Point", "node_class": "aether_point", "host_layers": ["Aether", "Liminal", "Tunnel", "Dimensional", "SeedRegeneration"], "incident_routes": ["R5", "R6", "R7", "R8", "R9"], "deg_s": 5, "cen": 0.71, "span": 4, "w0": 75, "polarity": "A++", "related_hubs": ["L0", "TX", "DL", "SC"], "touching_tunnels": ["T-AL", "T-DJ"], "status": "seated", "q0": {1, 3}, "q1": {0, 2}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "L0": {"node_name": "Liminal Transfer Point", "node_class": "liminal_transfer_hinge", "host_layers": ["Liminal", "Zero", "Aether", "Tunnel", "BridgeReturn", "Dimensional"], "incident_routes": ["R4", "R5", "R6", "R7", "R8", "R9", "R10"], "deg_s": 7, "cen": 1.0, "span": 4, "w0": 92, "polarity": "balanced_mediator", "related_hubs": ["Z0", "A0", "MS", "DB"], "touching_tunnels": ["T-LS", "T-ZC", "T-AL", "T-DJ"], "status": "seated", "q0": {0, 1, 2, 3}, "q1": {1, 2, 3}, "q2": {1, 2}, "q3": {3}},
    "MT": {"node_name": "Metro Transfer Hub", "node_class": "metro_transfer_hub", "host_layers": ["Metro", "Liminal", "BridgeReturn", "ReplayWitnessProof"], "incident_routes": ["R1", "R5", "R8", "R11"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "neutral", "related_hubs": ["MS", "L0", "RA"], "touching_tunnels": ["T-LS", "T-BC"], "status": "seated", "q0": {0, 1, 3}, "q1": {0, 1}, "q2": {0, 1}, "q3": {0, 1}},
    "MS": {"node_name": "Master Transfer Station", "node_class": "cross_family_master_interchange", "host_layers": ["Metro", "Mycelium", "Neural", "Liminal", "BridgeReturn", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R1", "R2", "R3", "R5", "R8", "R9", "R11"], "deg_s": 7, "cen": 1.0, "span": 4, "w0": 92, "polarity": "neutral_structural_hinge", "related_hubs": ["MT", "MY", "NN", "DB"], "touching_tunnels": ["T-LS", "T-BC", "T-DJ"], "status": "seated", "q0": {0, 1, 2, 3}, "q1": {0, 1, 2}, "q2": {0, 1, 2}, "q3": {0, 3}},
    "MY": {"node_name": "Mycelium Branch Hub", "node_class": "mycelial_branching_hub", "host_layers": ["Mycelium", "Liminal", "Aether", "SeedRegeneration"], "incident_routes": ["R2", "R5", "R6", "R7", "R13"], "deg_s": 5, "cen": 0.71, "span": 4, "w0": 75, "polarity": "A+", "related_hubs": ["MS", "A0", "SC", "L0"], "touching_tunnels": ["T-LS", "T-AL"], "status": "seated", "q0": {1, 2}, "q1": {2, 3}, "q2": {1, 2}, "q3": {2, 3}},
    "NN": {"node_name": "Neural Convergence Hub", "node_class": "neural_convergence_hub", "host_layers": ["Neural", "Liminal", "Aether", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R3", "R5", "R6", "R7", "R10", "R12"], "deg_s": 6, "cen": 0.86, "span": 5, "w0": 91, "polarity": "balanced_liminal", "related_hubs": ["MS", "MC", "WA", "L0"], "touching_tunnels": ["T-LS", "T-DJ"], "status": "seated", "q0": {1, 2, 3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "TE": {"node_name": "Tunnel Entrance", "node_class": "tunnel_entrance", "host_layers": ["Tunnel", "Zero", "Liminal", "BridgeReturn"], "incident_routes": ["R4", "R5", "R7", "R8"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "Z+_entry", "related_hubs": ["Z0", "L0", "DB"], "touching_tunnels": ["T-ZC", "T-LS", "T-DJ"], "status": "seated", "q0": {0, 2}, "q1": {1, 3}, "q2": {0, 1, 2}, "q3": {3}},
    "TX": {"node_name": "Tunnel Exit", "node_class": "tunnel_exit", "host_layers": ["Tunnel", "Aether", "Liminal", "BridgeReturn"], "incident_routes": ["R5", "R6", "R7", "R8"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "A+_release", "related_hubs": ["A0", "L0", "DL"], "touching_tunnels": ["T-AL", "T-LS", "T-DJ"], "status": "seated", "q0": {1, 3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {3}},
    "DB": {"node_name": "Dimensional Bridge Station", "node_class": "dimensional_bridge_station", "host_layers": ["BridgeReturn", "Liminal", "Dimensional", "Tunnel"], "incident_routes": ["R5", "R7", "R8", "R9", "R10"], "deg_s": 5, "cen": 0.71, "span": 3, "w0": 67, "polarity": "balanced", "related_hubs": ["L0", "MS", "MC", "TE", "TX"], "touching_tunnels": ["T-DJ", "T-BC"], "status": "seated", "q0": {1, 2, 3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "DL": {"node_name": "Dimensional Lift", "node_class": "dimensional_lift_station", "host_layers": ["Dimensional", "Aether", "Tunnel"], "incident_routes": ["R6", "R7", "R9", "R10"], "deg_s": 4, "cen": 0.57, "span": 2, "w0": 50, "polarity": "A+", "related_hubs": ["A0", "DB", "MC", "TX"], "touching_tunnels": ["T-AL", "T-DJ"], "status": "seated", "q0": {1, 3}, "q1": {1, 2, 3}, "q2": {1, 2, 3}, "q3": {1, 3}},
    "MC": {"node_name": "Manifold Crossing", "node_class": "manifold_crossing_station", "host_layers": ["Dimensional", "BridgeReturn", "Neural", "ReplayWitnessProof"], "incident_routes": ["R7", "R8", "R9", "R10", "R12"], "deg_s": 5, "cen": 0.71, "span": 3, "w0": 67, "polarity": "balanced_opposed", "related_hubs": ["DB", "DL", "NN", "WA"], "touching_tunnels": ["T-DJ", "T-BC"], "status": "seated", "q0": {2, 3}, "q1": {3}, "q2": {1, 2, 3}, "q3": {3}},
    "RA": {"node_name": "Replay Anchor", "node_class": "replay_anchor", "host_layers": ["ReplayWitnessProof", "BridgeReturn", "SeedRegeneration"], "incident_routes": ["R8", "R11", "R12", "R13"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "Z_return_bias", "related_hubs": ["MR", "WA", "SC", "MT"], "touching_tunnels": ["T-RR", "T-BC"], "status": "seated", "q0": {3}, "q1": {0, 1, 3}, "q2": {1, 2, 3}, "q3": {0, 3}},
    "WA": {"node_name": "Witness Anchor", "node_class": "witness_anchor", "host_layers": ["ReplayWitnessProof", "Neural"], "incident_routes": ["R5", "R11", "R12"], "deg_s": 3, "cen": 0.43, "span": 2, "w0": 42, "polarity": "Z_stabilized", "related_hubs": ["RA", "NN", "PA"], "touching_tunnels": ["T-RR"], "status": "seated", "q0": {0, 3}, "q1": {0, 2}, "q2": {0, 1, 2}, "q3": {0, 2, 3}},
    "SC": {"node_name": "Seed Crystal", "node_class": "seed_crystal", "host_layers": ["SeedRegeneration", "Aether", "Mycelium", "ReplayWitnessProof"], "incident_routes": ["R6", "R11", "R12", "R13"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "A_seeded", "related_hubs": ["A0", "MY", "RA"], "touching_tunnels": ["T-AL", "T-RR"], "status": "seated", "q0": {1, 3}, "q1": {2, 3}, "q2": {1, 2, 3}, "q3": {2, 3}},
    "MR": {"node_name": "Mobius Return Hinge", "node_class": "return_hinge", "host_layers": ["BridgeReturn", "ReplayWitnessProof", "Zero"], "incident_routes": ["R4", "R7", "R8", "R11"], "deg_s": 4, "cen": 0.57, "span": 3, "w0": 58, "polarity": "cyclic_return", "related_hubs": ["RA", "Z0", "DB"], "touching_tunnels": ["T-RR", "T-ZC"], "status": "frontier", "q0": {3}, "q1": {1, 3}, "q2": {1, 2, 3}, "q3": {0, 3}},
    "PA": {"node_name": "Proof Anchor", "node_class": "proof_anchor", "host_layers": ["ReplayWitnessProof", "BridgeReturn"], "incident_routes": ["R8", "R11", "R12"], "deg_s": 3, "cen": 0.43, "span": 2, "w0": 42, "polarity": "Z_stabilized_evidentiary_closure", "related_hubs": ["WA", "RA", "MR"], "touching_tunnels": [], "status": "frontier", "q0": {3}, "q1": {0, 2}, "q2": {0, 1, 2}, "q3": {0, 3}},
    "LP": {"node_name": "Latent Pressure Hub", "node_class": "latent_pressure_hub", "host_layers": ["Liminal", "BridgeReturn", "Dimensional"], "incident_routes": ["R5", "R7", "R8", "R9", "R10"], "deg_s": 5, "cen": 0.57, "span": 3, "w0": 55, "polarity": "unresolved", "related_hubs": ["L0", "DB", "MC", "MS"], "touching_tunnels": ["T-LS", "T-DJ", "T-BC"], "status": "inferred", "q0": {1, 2, 3}, "q1": {2, 3}, "q2": {1, 2, 3}, "q3": {3}},
}

TOPOLOGY_SEED = {
    "Metro": ["Liminal", "BridgeReturn", "ReplayWitnessProof"],
    "Mycelium": ["Liminal", "Aether", "SeedRegeneration"],
    "Neural": ["Liminal", "ReplayWitnessProof", "Dimensional"],
    "Zero": ["Liminal", "Tunnel", "ReplayWitnessProof"],
    "Aether": ["Liminal", "Tunnel", "Dimensional", "SeedRegeneration"],
    "Liminal": ["Metro", "Mycelium", "Neural", "Zero", "Aether", "Tunnel", "BridgeReturn", "Dimensional"],
    "Tunnel": ["Zero", "Aether", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "BridgeReturn": ["Metro", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "Dimensional": ["BridgeReturn", "Tunnel", "ReplayWitnessProof"],
    "ReplayWitnessProof": ["Zero", "BridgeReturn", "Neural", "SeedRegeneration"],
    "SeedRegeneration": ["Aether", "Mycelium", "ReplayWitnessProof"],
}

TUNNEL_CLASS_BOOK = {
    "T-ZC": {"name": "Zero-collapse tunnel", "route_bias": ["R4", "R7"], "entrance_node": "TE", "exit_node": "Z0"},
    "T-AL": {"name": "Aether-lift tunnel", "route_bias": ["R6", "R7"], "entrance_node": "L0", "exit_node": "TX"},
    "T-LS": {"name": "Liminal-shortcut tunnel", "route_bias": ["R5", "R7"], "entrance_node": "L0", "exit_node": "MS"},
    "T-DJ": {"name": "Dimensional-jump tunnel", "route_bias": ["R7", "R9", "R10"], "entrance_node": "DB", "exit_node": "DL"},
    "T-RR": {"name": "Replay-return tunnel", "route_bias": ["R11", "R12"], "entrance_node": "RA", "exit_node": "WA"},
    "T-BC": {"name": "Bridge-compression tunnel", "route_bias": ["R8", "R11"], "entrance_node": "MS", "exit_node": "RA"},
}

MASTER_KEY_STATES = {
    "K0": {"byte": 0, "tuple": [0, 0, 0, 0], "use": "baseline seating"},
    "K1": {"byte": 212, "tuple": [0, 1, 1, 3], "use": "hidden tunnel probe"},
    "K2": {"byte": 81, "tuple": [1, 0, 1, 1], "use": "aether lift"},
    "K3": {"byte": 217, "tuple": [1, 2, 1, 3], "use": "mycelial branching"},
    "K4": {"byte": 166, "tuple": [2, 1, 2, 2], "use": "counterphase floor cut"},
    "K5": {"byte": 222, "tuple": [2, 3, 1, 3], "use": "manifold crossing"},
    "K6": {"byte": 51, "tuple": [3, 0, 3, 0], "use": "replay closure"},
    "K7": {"byte": 247, "tuple": [3, 1, 3, 3], "use": "mobius-return test"},
    "K8": {"byte": 235, "tuple": [3, 2, 2, 3], "use": "seed recovery"},
    "K9": {"byte": 255, "tuple": [3, 3, 3, 3], "use": "maximal frontier saturation"},
}

PHRASE_MACROS = {
    "hidden_excavation": [0, 212, 217, 222, 255, 247, 51],
    "regeneration": [0, 81, 235, 247, 51],
    "transfer_triangulation": [0, 166, 217, 212],
}

HIDDEN_CANDIDATES = [
    {"candidate_id": "C1", "name": "Zero to Aether Mediating Lift Hub", "evidence_states": [212, 166, 222, 247, 255], "adjacent_explicit_nodes": ["Z0", "L0", "A0", "TE", "TX"], "confidence": "medium-high", "disposition": "frontier"},
    {"candidate_id": "C2", "name": "Metro Mycelium Neural Composite Transfer Node", "evidence_states": [217, 166, 212], "adjacent_explicit_nodes": ["MT", "MS", "MY", "NN", "L0"], "confidence": "high_structural", "disposition": "frontier"},
    {"candidate_id": "C3", "name": "Dimensional Midspan Bridge", "evidence_states": [222, 247, 255], "adjacent_explicit_nodes": ["DB", "DL", "MC", "TE", "TX"], "confidence": "high_structural", "disposition": "frontier"},
    {"candidate_id": "C4", "name": "Replay Proof Closure Junction", "evidence_states": [51, 247, 255], "adjacent_explicit_nodes": ["RA", "WA", "MR", "PA"], "confidence": "medium", "disposition": "frontier"},
    {"candidate_id": "C5", "name": "Seed Replay Regeneration Coupler", "evidence_states": [81, 235, 247], "adjacent_explicit_nodes": ["SC", "A0", "RA", "MY"], "confidence": "medium", "disposition": "frontier"},
    {"candidate_id": "C6", "name": "Frontier Liminal Distributor", "evidence_states": [222, 235, 247, 255], "adjacent_explicit_nodes": ["L0", "ZL", "A0", "MS"], "confidence": "low-medium", "disposition": "frontier"},
]


def decode_byte(byte: int) -> tuple[int, int, int, int]:
    q0 = byte % 4
    q1 = (byte // 4) % 4
    q2 = (byte // 16) % 4
    q3 = (byte // 64) % 4
    return q0, q1, q2, q3


def toroidal_neighbors(byte: int) -> list[int]:
    q = list(decode_byte(byte))
    neighbors: list[int] = []
    for index in range(4):
        for delta in (-1, 1):
            candidate = list(q)
            candidate[index] = (candidate[index] + delta) % 4
            neighbors.append(candidate[0] + 4 * candidate[1] + 16 * candidate[2] + 64 * candidate[3])
    return sorted(set(neighbors))


def gate_score(entry: dict[str, Any], byte: int) -> float:
    q0, q1, q2, q3 = decode_byte(byte)
    hits = 0
    hits += 1 if q0 in entry["q0"] else 0
    hits += 1 if q1 in entry["q1"] else 0
    hits += 1 if q2 in entry["q2"] else 0
    hits += 1 if q3 in entry["q3"] else 0
    return hits / 4.0


def active_route_ids(byte: int) -> list[str]:
    return [route_id for route_id, entry in ROUTE_GATE_BOOK.items() if gate_score(entry, byte) >= 0.5]


def active_tunnel_ids(byte: int) -> list[str]:
    q0, q1, q2, q3 = decode_byte(byte)
    active: list[str] = []
    if q0 in {0, 2} and q2 in {0, 1, 2} and q3 in {0, 2}:
        active.append("T-ZC")
    if q0 in {1, 3} and q2 in {1, 2, 3} and q3 in {1, 3}:
        active.append("T-AL")
    if q1 in {2, 3} and q3 == 3:
        active.append("T-LS")
    if q1 == 3 and q3 == 3:
        active.append("T-DJ")
    if q0 == 3 and q1 in {1, 3}:
        active.append("T-RR")
    if q3 in {0, 3}:
        active.append("T-BC")
    return unique_list(active)


def precision_class_for_record(record: dict[str, Any], stat_bundle: dict[str, Any]) -> str:
    if stat_bundle["timestamp_precision"] == "exact":
        return "exact"
    if split_archive_locator(record.get("path", "")):
        return "bounded"
    if record.get("modified_at"):
        return "near-exact"
    return "unresolved"


def read_text_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    except OSError:
        return None


def read_docx_paragraphs(path: Path) -> list[str]:
    paragraphs: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            with archive.open("word/document.xml") as handle:
                root = ET.fromstring(handle.read())
    except Exception:
        return paragraphs
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for paragraph in root.findall(".//w:p", namespaces):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespaces)]
        joined = "".join(texts).strip()
        if joined:
            paragraphs.append(joined)
    return paragraphs


def read_pdf_segments(path: Path) -> list[str]:
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
        except Exception:
            continue
        try:
            reader = module.PdfReader(str(path))
            segments: list[str] = []
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                if text:
                    segments.append(text)
            return segments
        except Exception:
            return []
    return []


def heading_line_indices(lines: list[str], heading_candidates: list[str]) -> list[int]:
    candidates = [candidate.strip().lstrip("#").strip() for candidate in heading_candidates if candidate.strip()]
    indices: list[int] = []
    if not candidates:
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                indices.append(index)
            if len(indices) >= MAX_HEADING_NODES:
                break
        return indices
    normalized_candidates = {candidate.lower(): candidate for candidate in candidates}
    for index, line in enumerate(lines):
        stripped = line.strip().lstrip("#").strip().lower()
        if stripped in normalized_candidates:
            indices.append(index)
        if len(indices) >= MAX_HEADING_NODES:
            break
    return sorted(set(indices))


def infer_band(record: dict[str, Any]) -> str:
    rel = record.get("relative_path", "").lower()
    title = record.get("title", "").lower()
    combined = f"{rel} {title}"
    if "reverse appendix" in combined or "reverse_appendix" in combined:
        return "reverse_field"
    if "appendix" in combined or re.search(r"\\app[a-z0-9]", rel):
        return "appendix"
    if re.search(r"(chapter|ch\\d+|_ch\\d+)", combined):
        return "chapter"
    if "emergent" in combined:
        return "emergent_body"
    if "metro" in combined or "map" in combined:
        return "metro_map"
    if "prompt" in combined:
        return "prompt_stack"
    if "seed" in combined:
        return "seed"
    if "review" in combined:
        return "review"
    if "route" in combined or "registry" in combined or "ledger" in combined:
        return "route_spec"
    return "document"


def infer_source_type(record: dict[str, Any], atlas_record: dict[str, Any] | None) -> str:
    if atlas_record:
        evidence = atlas_record.get("evidence", {})
        if evidence.get("source_type"):
            return str(evidence["source_type"])
        if atlas_record.get("kind"):
            return str(atlas_record["kind"])
    if record.get("kind"):
        return str(record["kind"])
    return "unknown"


def infer_body_class(top_level: str) -> str:
    classification = ROOT_CLASSIFICATION.get(top_level)
    if classification:
        return classification["qshrink_body"]
    if top_level.startswith("."):
        return "Hidden Support Body"
    return "Auxiliary Body"


def confidence_class(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.6:
        return "medium"
    return "low"


def scalar_bucket(value: float, buckets: int = 10) -> int:
    return max(0, min(buckets - 1, int(value * buckets)))


def file_exists_and_small(locator: str) -> bool:
    parsed = split_archive_locator(locator)
    if parsed is not None:
        return False
    path = Path(locator)
    return path.exists() and path.is_file() and path.stat().st_size <= EXACT_TEXT_SIZE_LIMIT


def extract_node_segments(record: dict[str, Any]) -> list[dict[str, Any]]:
    node_segments: list[dict[str, Any]] = []
    locator = record.get("path", "")
    extension = str(record.get("extension", "")).lower()
    heading_candidates = list(record.get("heading_candidates", []))
    if extension in TEXT_EXTENSIONS and file_exists_and_small(locator):
        text = read_text_file(Path(locator))
        if text:
            lines = text.splitlines()
            heading_indices = heading_line_indices(lines, heading_candidates)
            if heading_indices:
                heading_indices.append(len(lines))
                for ordinal, start in enumerate(heading_indices[:-1], start=1):
                    end = heading_indices[ordinal] if ordinal < len(heading_indices) else len(lines)
                    title = lines[start].strip() or f"segment_{ordinal}"
                    node_segments.append({"node_name": title[:120], "node_class": "heading_span", "locator_type": "line_range", "line_start": start + 1, "line_end": end, "precision": "exact"})
            else:
                for chunk_start in range(0, len(lines), MAX_SEGMENT_LINES):
                    chunk_end = min(len(lines), chunk_start + MAX_SEGMENT_LINES)
                    node_segments.append({"node_name": f"lines_{chunk_start + 1}_{chunk_end}", "node_class": "line_segment", "locator_type": "line_range", "line_start": chunk_start + 1, "line_end": chunk_end, "precision": "exact"})
            return node_segments[: max(MAX_HEADING_NODES, 1) * 2]
    if extension == ".docx" and "::" not in locator:
        path = Path(locator)
        if path.exists():
            paragraphs = read_docx_paragraphs(path)
            if paragraphs:
                for index in range(0, len(paragraphs), MAX_SEGMENT_PARAGRAPHS):
                    end = min(len(paragraphs), index + MAX_SEGMENT_PARAGRAPHS)
                    title = paragraphs[index][:80] or f"paragraphs_{index + 1}_{end}"
                    node_segments.append({"node_name": title, "node_class": "paragraph_segment", "locator_type": "paragraph_range", "paragraph_start": index + 1, "paragraph_end": end, "precision": "bounded"})
                return node_segments[: MAX_HEADING_NODES]
    if extension == ".pdf" and "::" not in locator:
        path = Path(locator)
        if path.exists():
            segments = read_pdf_segments(path)
            if segments:
                for index, segment in enumerate(segments[:MAX_HEADING_NODES], start=1):
                    node_segments.append({"node_name": segment.splitlines()[0][:80] or f"page_{index}", "node_class": "pdf_segment", "locator_type": "segment_index", "segment_index": index, "precision": "bounded"})
                return node_segments
    if record.get("text_extractable"):
        heading_candidates = heading_candidates or [record.get("excerpt", "")[:80] or "bounded_segment_1"]
        for index, heading in enumerate(heading_candidates[:MAX_HEADING_NODES], start=1):
            node_segments.append({"node_name": heading[:120], "node_class": "bounded_surrogate", "locator_type": "surrogate_index", "segment_index": index, "precision": "bounded"})
    return node_segments


def dimensional_stratum_from_record(record: dict[str, Any], atlas_record: dict[str, Any] | None) -> str:
    bindings = (atlas_record or {}).get("dimensional_bindings", {})
    d6 = bindings.get("d6_overlay", {})
    d5 = bindings.get("d5_overlay", {})
    if d6.get("state") == "addressable":
        return "D4"
    if d5.get("state") == "addressable":
        return "D3"
    if bindings.get("d4_native", {}).get("active"):
        return "D1"
    return "D0"


def zero_aether_polarity(record: dict[str, Any]) -> str:
    math_route = (record.get("hemisphere_routes") or {}).get("MATH", {})
    myth_route = (record.get("hemisphere_routes") or {}).get("MYTH", {})
    math_aether = ((math_route.get("aether_point") or {}).get("aether_density") or 0.0)
    myth_aether = ((myth_route.get("aether_point") or {}).get("aether_density") or 0.0)
    math_zero = ((math_route.get("aether_point") or {}).get("zero_proximity") or 0.0)
    myth_zero = ((myth_route.get("aether_point") or {}).get("zero_proximity") or 0.0)
    aether = max(math_aether, myth_aether)
    zero = max(math_zero, myth_zero)
    if aether - zero >= 0.25:
        return "A++"
    if aether > zero:
        return "A+"
    if zero - aether >= 0.25:
        return "Z++"
    if zero > aether:
        return "Z+"
    return "balanced"


def witness_state(record: dict[str, Any], governance_row: dict[str, Any] | None) -> str:
    route_packets = record.get("hemisphere_routes", {})
    proof_states = {
        str(route_packets.get("MATH", {}).get("proof_state", "")),
        str(route_packets.get("MYTH", {}).get("proof_state", "")),
    }
    if governance_row and governance_row.get("proof_uplift_required"):
        return "proof"
    if "OK" in proof_states:
        return "proof"
    if governance_row and governance_row.get("replay_required"):
        return "replay"
    if record.get("tract") == "replay":
        return "replay"
    if "NEAR" in proof_states or "AMBIG" in proof_states:
        return "witness"
    return "none"


def build_coordinate_standard(top_levels: list[str], families: list[str], bands: list[str], stages: list[str]) -> dict[str, Any]:
    macro_values = ["HSigma", "Document", "Node", "Route", "Nexus", "Tunnel", "ReadingRoute", *top_levels]
    ordinal_tables = {
        "L0": {value: index for index, value in enumerate(unique_list(macro_values))},
        "L1": {value: index for index, value in enumerate(["meta", *families, "hologram"])},
        "L2": {value: index for index, value in enumerate(unique_list(["document", *bands, "class_nexus", "class_route", "class_tunnel", "reading_route"]))},
        "L3": {value: index for index, value in enumerate(unique_list(["global", *top_levels, "section", "segment"]))},
        "L5": {value: index for index, value in enumerate(["MATH", "MYTH", "COMMISSURE", "MULTI", "LIMINAL", "ZERO", "AETHER", "REPLAY"])},
        "L6": {value: index for index, value in enumerate(["local", "branch", "hub", "transfer", "crossing", "frontier", "latent"])},
        "L7": {value: index for index, value in enumerate(unique_list(["UNSPECIFIED", *stages]))},
        "L8": {value: index for index, value in enumerate(["D0", "D1", "D2", "D3", "D4"])},
        "L9": {value: index for index, value in enumerate(["Z++", "Z+", "balanced", "A+", "A++", "unresolved"])},
        "L10": {value: index for index, value in enumerate(["none", "witness", "replay", "proof", "frontier"])},
    }
    return {
        "symbolic_grammar": "LM::<L0>::<L1>::<L2>::<L3>::<L4>::<L5>::<L6>::<L7>::<L8>::<L9>::<L10>::<L11>",
        "axes": [
            {"axis": "L0", "name": "corpus manifold or macro body"},
            {"axis": "L1", "name": "family"},
            {"axis": "L2", "name": "chapter or appendix band"},
            {"axis": "L3", "name": "section or subregion"},
            {"axis": "L4", "name": "identity ordinal"},
            {"axis": "L5", "name": "route rail or edge cluster"},
            {"axis": "L6", "name": "nexus density or transfer status"},
            {"axis": "L7", "name": "orbit phase or recurrence position"},
            {"axis": "L8", "name": "dimensional stratum"},
            {"axis": "L9", "name": "zero to aether polarity"},
            {"axis": "L10", "name": "witness replay proof state"},
            {"axis": "L11", "name": "pressure priority load intensity"},
        ],
        "ordinal_tables": ordinal_tables,
    }


def coordinate_for_entity(*, coordinate_standard: dict[str, Any], l0: str, l1: str, l2: str, l3: str, l4: int, l5: str, l6: str, l7: str, l8: str, l9: str, l10: str, l11: int) -> tuple[str, list[int]]:
    tables = coordinate_standard["ordinal_tables"]
    vector = [tables["L0"].get(l0, 0), tables["L1"].get(l1, 0), tables["L2"].get(l2, 0), tables["L3"].get(l3, 0), l4, tables["L5"].get(l5, 0), tables["L6"].get(l6, 0), tables["L7"].get(l7, 0), tables["L8"].get(l8, 0), tables["L9"].get(l9, 0), tables["L10"].get(l10, 0), l11]
    return "LM::" + "::".join(str(value) for value in vector), vector


def build_hologram_back_pointer(*, entity_type: str, host_layers: list[str], incident_routes: list[str], dimensional_span: list[str], timing_rule: str, nearest_hubs: list[str], regeneration_links: list[str]) -> dict[str, Any]:
    return {
        "type": entity_type,
        "host_layers": host_layers,
        "incident_routes": incident_routes,
        "dimensional_span": dimensional_span,
        "timing_exposure_rule": timing_rule,
        "nearest_hubs": nearest_hubs,
        "regeneration_links": regeneration_links,
    }


def liminal_time_bridge(*, utc_timestamp: str, precision_class: str, jd: float | None, orbit_phase_index: int, revision_depth: int, dimensional_stratum: str, route_recurrence_index: int, zero_aether_polarity: str) -> dict[str, Any]:
    lti = f"LTI::{orbit_phase_index:03d}::{revision_depth}::{dimensional_stratum}::{route_recurrence_index}::{zero_aether_polarity}"
    return {
        "liminal_time_index": lti,
        "formula": "F(utc_timestamp, precision_class, julian_date, orbit_phase_index, revision_depth, dimensional_stratum, route_recurrence_index, zero_aether_polarity)",
        "utc_timestamp": utc_timestamp,
        "precision_class": precision_class,
        "julian_date": jd,
        "orbit_phase_index": orbit_phase_index,
        "revision_depth": revision_depth,
        "dimensional_stratum": dimensional_stratum,
        "route_recurrence_index": route_recurrence_index,
        "zero_aether_polarity": zero_aether_polarity,
    }


def host_layers_for_record(record: dict[str, Any], governance_row: dict[str, Any] | None) -> list[str]:
    layers: list[str] = []
    routes = record.get("hemisphere_routes") or {}
    math_route = routes.get("MATH", {})
    myth_route = routes.get("MYTH", {})
    target_systems = {math_route.get("target_system", ""), myth_route.get("target_system", "")}
    if any(system for system in target_systems):
        layers.append("Metro")
    if record.get("primary_hemisphere") == "MYTH" or record.get("family") in {"mythic-sign-systems"}:
        layers.append("Mycelium")
    if record.get("tract") in {"relation", "replay"}:
        layers.append("Neural")
    if (math_route.get("zpoint_id") or "").startswith("Z"):
        layers.append("Zero")
    if (math_route.get("aether_point") or {}).get("aether_density", 0.0) >= 0.65 or (myth_route.get("aether_point") or {}).get("aether_density", 0.0) >= 0.65:
        layers.append("Aether")
    if any(route.get("route_mode") != "direct_native" for route in routes.values()):
        layers.append("BridgeReturn")
    if any(route.get("geodesic_mode") != "rail transit" for route in routes.values()):
        layers.append("Tunnel")
    if len(target_systems - {""}) > 1 or any(route.get("supported_spaces") for route in routes.values()):
        layers.append("Dimensional")
    if governance_row and (governance_row.get("replay_required") or governance_row.get("proof_uplift_required")):
        layers.append("ReplayWitnessProof")
    if record.get("appendix_support"):
        layers.append("SeedRegeneration")
    layers.append("Liminal")
    return unique_list(layers)


def class_nexus_reach(byte: int, start_id: str) -> dict[str, Any]:
    active_routes = set(active_route_ids(byte))
    visible = {node_id for node_id, entry in NEXUS_CLASS_BOOK.items() if gate_score(entry, byte) >= 0.5}
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left_id, left_entry in NEXUS_CLASS_BOOK.items():
        if left_id not in visible:
            continue
        left_routes = set(left_entry["incident_routes"]) & active_routes
        for right_id, right_entry in NEXUS_CLASS_BOOK.items():
            if right_id == left_id or right_id not in visible:
                continue
            right_routes = set(right_entry["incident_routes"]) & active_routes
            if left_routes & right_routes:
                adjacency[left_id].add(right_id)
    reached: set[str] = set()
    frontier_count = 0
    route_hits: set[str] = set()
    depth2_layers: set[str] = set()
    queue = [(start_id, 0)]
    seen = {start_id}
    while queue:
        node_id, depth = queue.pop(0)
        if node_id in visible:
            reached.add(node_id)
            entry = NEXUS_CLASS_BOOK[node_id]
            route_hits.update(set(entry["incident_routes"]) & active_routes)
            depth2_layers.update(entry["host_layers"])
            if depth >= 2:
                continue
            for neighbor in sorted(adjacency.get(node_id, set())):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
    full_layers: set[str] = set()
    for node_id in reached:
        full_layers.update(NEXUS_CLASS_BOOK[node_id]["host_layers"])
        if NEXUS_CLASS_BOOK[node_id]["status"] == "frontier":
            frontier_count += 1
    return {
        "reached": reached,
        "route_hits": route_hits,
        "frontier_count": frontier_count,
        "full_layers": full_layers,
        "depth2_layers": depth2_layers,
    }


def build_hsigma_mindsweeper() -> dict[str, Any]:
    rows = sorted(NEXUS_CLASS_BOOK)
    base_cells: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    reach_sets: dict[str, dict[int, set[str]]] = defaultdict(dict)
    exposed_counts_by_row: dict[str, list[int]] = defaultdict(list)
    for node_id in rows:
        entry = NEXUS_CLASS_BOOK[node_id]
        c_score = entry["cen"]
        for byte in range(256):
            exposure = gate_score(entry, byte)
            reach = class_nexus_reach(byte, node_id)
            reach_sets[node_id][byte] = reach["reached"]
            exposed_count = len(reach["reached"])
            exposed_counts_by_row[node_id].append(exposed_count)
            tunnels = active_tunnel_ids(byte)
            replay_access = 1 if "RA" in reach["reached"] else 0
            witness_access = 1 if "WA" in reach["reached"] else 0
            proof_access = 1 if "PA" in reach["reached"] else 0
            seed_access = 1 if "SC" in reach["reached"] else 0
            p_value = (replay_access + witness_access + 0.5 * proof_access + seed_access) / 3.5
            r_value = exposed_count / 18.0
            t_value = len(tunnels) / 6.0
            d_value = min(1.0, len(reach["full_layers"]) / 5.0)
            full_layer_count = max(1, len(reach["full_layers"]))
            k_value = len(reach["depth2_layers"]) / full_layer_count
            u_cross = 1.0 if "R10" in reach["route_hits"] and "MC" not in reach["reached"] else 0.0
            u_tunnel = 1.0 if tunnels and not ({"TE", "TX"} <= reach["reached"]) else 0.0
            u_pole = 1.0 if {"Z0", "A0"} <= reach["reached"] and "L0" not in reach["reached"] else 0.0
            u_replay = 1.0 if "R11" in reach["route_hits"] and "PA" not in reach["reached"] else 0.0
            u_transfer = 1.0 if {"MT", "MY", "NN"} <= reach["reached"] and "MS" not in reach["reached"] else 0.0
            hidden_pressure = (u_cross + u_tunnel + u_pole + u_replay + u_transfer) / 5.0
            v_pole = 1 if {"Z0", "A0"} <= reach["reached"] and exposure < 0.5 else 0
            v_tunnel = 1 if "R7" in reach["route_hits"] and not ({"TE", "TX"} <= reach["reached"]) else 0
            v_dim = 1 if {"R9", "R10"} & reach["route_hits"] and not ({"DB", "DL", "MC"} & reach["reached"]) else 0
            v_replay = 1 if "R11" in reach["route_hits"] and "RA" not in reach["reached"] else 0
            contradiction = (v_pole + v_tunnel + v_dim + v_replay) / 4.0
            frontier_fraction = reach["frontier_count"] / max(1, exposed_count)
            weight = 20 * c_score + 20 * r_value + 15 * t_value + 15 * d_value + 10 * k_value + 10 * p_value
            base_cells[node_id][byte] = {
                "byte": byte,
                "weight_pre_novelty": round(weight, 6),
                "visibility": "explicit" if exposure >= 0.5 else ("implied" if exposure >= 0.25 else "absent"),
                "hidden_pressure": round(hidden_pressure, 6),
                "contradiction": round(contradiction, 6),
                "frontier_fraction": round(frontier_fraction, 6),
                "route_density": round(len(reach["route_hits"]) / max(1, len(entry["incident_routes"])), 6),
                "exposed_nexus_count": exposed_count,
                "exposed_tunnel_count": len(tunnels),
                "active_route_ids": sorted(reach["route_hits"]),
                "active_tunnel_ids": tunnels,
                "reached_node_ids": sorted(reach["reached"]),
                "reached_layer_ids": sorted(reach["full_layers"]),
                "dominant_exposure": exposure >= 0.75,
            }
    final_cells: list[dict[str, Any]] = []
    row_stats: dict[str, dict[str, float]] = {}
    for node_id in rows:
        count_series = exposed_counts_by_row[node_id]
        row_stats[node_id] = {"mu": statistics.mean(count_series), "sigma": statistics.pstdev(count_series) if len(count_series) > 1 else 0.0}
    for node_id in rows:
        for byte in range(256):
            novelty = len(reach_sets[node_id][byte] - set.intersection(*[reach_sets[node_id][neighbor] for neighbor in toroidal_neighbors(byte)])) / 18.0
            weight = base_cells[node_id][byte]["weight_pre_novelty"] + 10 * novelty
            neighbor_weight_values = [base_cells[node_id][neighbor]["weight_pre_novelty"] for neighbor in toroidal_neighbors(byte)]
            instability = (max(neighbor_weight_values) - min(neighbor_weight_values)) / 100.0 if neighbor_weight_values else 0.0
            cell = dict(base_cells[node_id][byte])
            cell["novel_nexus_exposure"] = round(novelty, 6)
            cell["weight"] = round(weight, 6)
            cell["timing_instability"] = round(instability, 6)
            stats = row_stats[node_id]
            if cell["contradiction"] >= 0.40:
                cell_class = "contradictory"
            elif cell["weight"] >= 80 and len(cell["reached_layer_ids"]) >= 4 and cell["contradiction"] < 0.25 and cell["exposed_nexus_count"] >= stats["mu"] + stats["sigma"]:
                cell_class = "master-key"
            elif cell["hidden_pressure"] >= 0.45 and cell["contradiction"] < 0.40:
                cell_class = "hidden-pressure"
            elif cell["frontier_fraction"] > 0.50 and cell["contradiction"] < 0.40:
                cell_class = "frontier"
            elif cell["timing_instability"] >= 0.25 and cell["contradiction"] < 0.40:
                cell_class = "unstable"
            elif cell["weight"] >= 70 and cell["hidden_pressure"] < 0.30 and cell["contradiction"] < 0.25:
                cell_class = "seated"
            elif 55 <= cell["weight"] < 70 and cell["contradiction"] < 0.40:
                cell_class = "promising"
            else:
                cell_class = "degenerate"
            cell["class"] = cell_class
            cell["nexus_id"] = node_id
            final_cells.append(cell)
    return {
        "row_count": len(rows),
        "column_count": 256,
        "cell_count": len(final_cells),
        "row_stats": row_stats,
        "cells": final_cells,
    }


def build_document_records(support: dict[str, Any], coordinate_standard: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    documents: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    for index, record in enumerate(support["authority"]["records"], start=1):
        live_atlas_record = support["live_map"].get(record["record_id"])
        archive_atlas_record = support["archive_map"].get(record["record_id"])
        atlas_record = live_atlas_record or archive_atlas_record
        governance_row = support["governance_map"].get(record["record_id"])
        stage_row = support["stage_map"].get(record["record_id"], {})
        stat_bundle = file_stat_bundle(record.get("path", ""), record.get("modified_at", ""))
        astro = astro_overlay(stat_bundle["utc_timestamp"])
        jd = astro.get("julian_date") if astro.get("status") == "computed" else None
        band = infer_band(record)
        source_type = infer_source_type(record, atlas_record)
        dim_stratum = dimensional_stratum_from_record(record, atlas_record)
        polarity = zero_aether_polarity(record)
        w_state = witness_state(record, governance_row)
        unresolved_flags: list[str] = []
        if governance_row and governance_row.get("quarantine_required"):
            unresolved_flags.append("quarantine_required")
        if governance_row and governance_row.get("repair_eligible"):
            unresolved_flags.append("repair_eligible")
        if not record.get("local_addr"):
            unresolved_flags.append("missing_local_addr")
        if not record.get("global_addr"):
            unresolved_flags.append("missing_global_addr")
        if not record.get("tesseract_header"):
            unresolved_flags.append("missing_tesseract_header")
        if not record.get("text_extractable"):
            unresolved_flags.append("non_text_extractable")
        if split_archive_locator(record.get("path", "")):
            unresolved_flags.append("archive_precision_bounded")
        pressure = min(9, len(unresolved_flags))
        host_layers = host_layers_for_record(record, governance_row)
        symbolic, vector = coordinate_for_entity(
            coordinate_standard=coordinate_standard,
            l0=record.get("top_level", "Document"),
            l1=record.get("family", "meta"),
            l2=band,
            l3=record.get("top_level", "global"),
            l4=index,
            l5=record.get("primary_hemisphere", "MULTI"),
            l6="transfer" if record.get("bridge_intensity", 0.0) >= 0.5 else "local",
            l7=stage_row.get("stage_label", "UNSPECIFIED"),
            l8=dim_stratum,
            l9=polarity,
            l10=w_state,
            l11=pressure,
        )
        document_id = f"DOC-{record['record_id']}"
        route_ids = [route["route_id"] for route in (record.get("hemisphere_routes") or {}).values() if route.get("route_id")]
        back_pointer = build_hologram_back_pointer(
            entity_type="document",
            host_layers=host_layers,
            incident_routes=route_ids,
            dimensional_span=[dim_stratum],
            timing_rule=f"track via stage={stage_row.get('stage_label', 'UNSPECIFIED')} and polarity={polarity}",
            nearest_hubs=unique_list([str(record.get("hub_id", "")), str(record.get("grand_central", "")), f"NEXUS-FAMILY-{slugify(record.get('family', 'general-corpus'))}"]),
            regeneration_links=unique_list(list(record.get("appendix_support", []))),
        )
        bridge_memberships = []
        if record.get("bridge_class"):
            bridge_memberships.append(f"BRIDGE-{slugify(record['bridge_class'])}")
        tunnel_memberships = []
        for hemisphere, route in (record.get("hemisphere_routes") or {}).items():
            if route.get("geodesic_mode") != "rail transit" or route.get("interlock_ids"):
                tunnel_memberships.append(f"TUNNEL-{record['record_id']}-{hemisphere}")
        summary = f"{record.get('family_label', record.get('family', 'general-corpus'))}; primary hemisphere {record.get('primary_hemisphere', 'UNKNOWN')}; tract {record.get('tract', 'unknown')}"
        document_record = {
            "document_id": document_id,
            "record_id": record["record_id"],
            "canonical_title": record.get("title") or Path(record.get("relative_path", "")).stem,
            "aliases": unique_list([Path(record.get("relative_path", "")).stem, *(Path(item).stem for item in record.get("duplicate_paths", []))]),
            "corpus_family": record.get("family", "general-corpus"),
            "body_class": infer_body_class(record.get("top_level", "")),
            "source_type": source_type,
            "source_pointer": record.get("path", ""),
            "relative_path": record.get("relative_path", ""),
            "source_scopes": list(record.get("source_scopes", [])),
            "local_timestamp": stat_bundle["source_local_timestamp"],
            "utc_timestamp": stat_bundle["utc_timestamp"],
            "timestamp_precision": precision_class_for_record(record, stat_bundle),
            "file_created_at": stat_bundle["file_created_at"],
            "file_modified_at": stat_bundle["file_modified_at"],
            "last_observed_at": stat_bundle["last_observed_at"],
            "revision_timestamp": dt_to_utc_iso(parse_iso(record.get("modified_at", ""))),
            "astrological_overlay": astro,
            "liminal_time_bridge": liminal_time_bridge(utc_timestamp=stat_bundle["utc_timestamp"], precision_class=precision_class_for_record(record, stat_bundle), jd=jd, orbit_phase_index=index % 256, revision_depth=len(record.get("source_scopes", [])), dimensional_stratum=dim_stratum, route_recurrence_index=len(route_ids), zero_aether_polarity=polarity),
            "liminal_coordinate_symbolic": symbolic,
            "liminal_coordinate_vector": vector,
            "dimensional_stratum": dim_stratum,
            "zero_point_relation": "collapse_bias" if polarity.startswith("Z") else "mediated",
            "aether_point_relation": "expansion_bias" if polarity.startswith("A") else "mediated",
            "zero_aether_polarity": polarity,
            "parent_nodes": [],
            "child_nodes": [],
            "upstream_routes": route_ids,
            "downstream_routes": route_ids,
            "nexus_memberships": unique_list([f"NEXUS-TOP-{slugify(record.get('top_level', 'unknown'))}", f"NEXUS-FAMILY-{slugify(record.get('family', 'general-corpus'))}", f"NEXUS-BAND-{slugify(band)}"]),
            "tunnel_memberships": tunnel_memberships,
            "bridge_memberships": bridge_memberships,
            "witness_role": "witness" if w_state in {"witness", "proof"} else "none",
            "replay_role": "replay" if w_state in {"replay", "proof"} else "none",
            "proof_role": "proof" if w_state == "proof" else "pending",
            "summary_of_function": summary,
            "whole_organism_role": f"{record.get('top_level', 'unknown')} -> {record.get('family', 'general-corpus')} -> {record.get('tract', 'unknown')}",
            "unresolved_load": {"score": pressure, "flags": unresolved_flags},
            "confidence_class": confidence_class(float(record.get("confidence", 0.0))),
            "confidence_score": float(record.get("confidence", 0.0)),
            "evidence_basis": {"atlas_record_id": atlas_record.get("record_id") if atlas_record else "", "authority_registry": str(AUTHORITY_REGISTRY_PATH), "governance_row": governance_row or {}, "basis_crosswalk": support["basis_map"].get(record["record_id"], {}), "stage_assignment": stage_row},
            "runtime_route_fields": {"local_addr": record.get("local_addr", ""), "global_addr": record.get("global_addr", ""), "tesseract_header": record.get("tesseract_header", ""), "hubs_seq": list(record.get("hubs_seq", [])), "route_plan_id": record.get("route_plan_id", ""), "holo_address": record.get("holo_address", "")},
            "hologram_back_pointer": back_pointer,
        }
        documents.append(document_record)
        root_node_id = f"NODE-{record['record_id']}-ROOT"
        document_record["parent_nodes"] = [root_node_id]
        root_symbolic, root_vector = coordinate_for_entity(
            coordinate_standard=coordinate_standard,
            l0=record.get("top_level", "Node"),
            l1=record.get("family", "meta"),
            l2=band,
            l3="section",
            l4=index,
            l5=record.get("primary_hemisphere", "MULTI"),
            l6="hub" if record.get("hub_id") else "local",
            l7=stage_row.get("stage_label", "UNSPECIFIED"),
            l8=dim_stratum,
            l9=polarity,
            l10=w_state,
            l11=pressure,
        )
        nodes.append({"node_id": root_node_id, "node_name": document_record["canonical_title"], "node_class": "document_root", "host_document": document_id, "exact_coordinate": {"symbolic": root_symbolic, "vector": root_vector}, "timestamps": {"local_timestamp": stat_bundle["source_local_timestamp"], "utc_timestamp": stat_bundle["utc_timestamp"], "precision": document_record["timestamp_precision"]}, "local_law": "document_root", "route_role": record.get("primary_hemisphere", "UNKNOWN"), "transfer_role": "hub" if record.get("hub_id") else "local", "nearest_hub": record.get("hub_id", ""), "upstream_links": route_ids, "downstream_links": route_ids, "bridge_links": bridge_memberships, "tunnel_links": tunnel_memberships, "replay_links": route_ids, "witness_links": route_ids, "load_intensity": pressure, "certainty": document_record["confidence_class"], "evidence_basis": {"host_record_id": record["record_id"], "locator": record.get("path", "")}, "hologram_back_pointer": back_pointer})
        child_node_ids = [root_node_id]
        for segment_index, segment in enumerate(extract_node_segments(record), start=1):
            node_id = f"NODE-{record['record_id']}-{segment_index:03d}"
            seg_symbolic, seg_vector = coordinate_for_entity(
                coordinate_standard=coordinate_standard,
                l0=record.get("top_level", "Node"),
                l1=record.get("family", "meta"),
                l2=band,
                l3="segment",
                l4=index * 100 + segment_index,
                l5=record.get("primary_hemisphere", "MULTI"),
                l6="branch",
                l7=stage_row.get("stage_label", "UNSPECIFIED"),
                l8=dim_stratum,
                l9=polarity,
                l10=w_state,
                l11=pressure,
            )
            nodes.append({"node_id": node_id, "node_name": segment["node_name"], "node_class": segment["node_class"], "host_document": document_id, "exact_coordinate": {"symbolic": seg_symbolic, "vector": seg_vector}, "timestamps": {"local_timestamp": stat_bundle["source_local_timestamp"], "utc_timestamp": stat_bundle["utc_timestamp"], "precision": segment["precision"]}, "local_law": segment["locator_type"], "route_role": record.get("primary_hemisphere", "UNKNOWN"), "transfer_role": "branch", "nearest_hub": record.get("hub_id", ""), "upstream_links": [root_node_id], "downstream_links": route_ids, "bridge_links": bridge_memberships, "tunnel_links": tunnel_memberships, "replay_links": [], "witness_links": [], "load_intensity": pressure, "certainty": segment["precision"], "evidence_basis": {"host_record_id": record["record_id"], "locator": segment}, "hologram_back_pointer": back_pointer})
            child_node_ids.append(node_id)
        document_record["child_nodes"] = child_node_ids
    return documents, nodes


def build_instance_routes(documents: list[dict[str, Any]], support: dict[str, Any], coordinate_standard: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    routes: list[dict[str, Any]] = []
    tunnel_records: list[dict[str, Any]] = []
    station_ids: set[str] = set()
    authority_by_id = {item["record_id"]: item for item in support["authority"]["records"]}
    for index, document in enumerate(documents, start=1):
        authority_record = authority_by_id[document["record_id"]]
        for hemisphere, route in authority_record.get("hemisphere_routes", {}).items():
            target_system = route.get("target_system", "GrandCentral")
            for station_id in route.get("station_path", []):
                station_ids.add(station_id)
            for station_id in route.get("return_path", []):
                station_ids.add(station_id)
            dim_span = ["D0"]
            if route.get("route_mode") != "direct_native":
                dim_span.append("D1")
            if route.get("zpoint_id"):
                dim_span.append("D2")
            if route.get("geodesic_mode") != "rail transit" or route.get("interlock_ids"):
                dim_span.append("D3")
            if route.get("proof_state") in {"OK", "NEAR"} or authority_record.get("tract") == "replay":
                dim_span.append("D4")
            dim_span = unique_list(dim_span)
            witness_state_value = "proof" if route.get("proof_state") == "OK" else ("witness" if route.get("proof_state") in {"NEAR", "AMBIG"} else "none")
            polarity = zero_aether_polarity(authority_record)
            route_symbolic, route_vector = coordinate_for_entity(
                coordinate_standard=coordinate_standard,
                l0=authority_record.get("top_level", "Route"),
                l1=authority_record.get("family", "meta"),
                l2="document",
                l3="global",
                l4=index,
                l5=hemisphere if hemisphere in {"MATH", "MYTH"} else "MULTI",
                l6="crossing" if route.get("route_mode") != "direct_native" else "transfer",
                l7=support["stage_map"].get(document["record_id"], {}).get("stage_label", "UNSPECIFIED"),
                l8=dim_span[-1],
                l9=polarity,
                l10=witness_state_value,
                l11=scalar_bucket(float(route.get("dynamic_weights", {}).get("salience", 0.0))),
            )
            route_record = {
                "route_id": route["route_id"],
                "route_name": f"{document['canonical_title']}::{hemisphere}",
                "route_type": "instance_route",
                "origin_node": document["parent_nodes"][0],
                "destination_node": f"NEXUS-SYSTEM-{slugify(target_system)}",
                "intermediate_nodes": [f"NEXUS-STATION-{slugify(item)}" for item in route.get("station_path", [])],
                "route_coordinate": {"symbolic": route_symbolic, "vector": route_vector},
                "dimensional_span": dim_span,
                "route_length_class": "short" if len(route.get("station_path", [])) <= 2 else ("deep" if len(route.get("station_path", [])) >= 4 else "medium"),
                "shortest_path_status": False,
                "deepest_path_status": False,
                "local_time_span": [document["local_timestamp"], document["local_timestamp"]],
                "liminal_time_span": [document["liminal_time_bridge"]["liminal_time_index"]],
                "astrological_time_span": [document["astrological_overlay"]],
                "bridge_conditions": {"route_mode": route.get("route_mode", ""), "bridge_intensity": float(authority_record.get("bridge_intensity", 0.0))},
                "replay_conditions": {"replay_policy": route.get("replay_policy", ""), "return_path": list(route.get("return_path", []))},
                "witness_conditions": {"proof_state": route.get("proof_state", ""), "truth_state": route.get("truth_state", "")},
                "proof_conditions": {"docs_gate_status": route.get("docs_gate_status", DOCS_GATE_EXPECTED), "hcrl_pass": route.get("hcrl_pass", False)},
                "notes_on_use": f"{route.get('route_mode', 'direct_native')} to {target_system}",
                "native_payload": route,
                "hologram_back_pointer": build_hologram_back_pointer(entity_type="route", host_layers=["Metro", "Liminal", "Dimensional"] if len(dim_span) > 1 else ["Metro"], incident_routes=[], dimensional_span=dim_span, timing_rule=f"use HSigma byte affinity for hemisphere {hemisphere}", nearest_hubs=unique_list([route.get("hub_id", ""), route.get("grand_central_exchange", "")]), regeneration_links=unique_list(list(route.get("appendix_support", [])))),
            }
            routes.append(route_record)
            if route.get("geodesic_mode") != "rail transit" or route.get("interlock_ids"):
                tunnel_type = "dimensional_jump"
                if route.get("geodesic_mode") == "z-point tunnel":
                    tunnel_type = "zero_point_collapse"
                elif (route.get("aether_point") or {}).get("aether_density", 0.0) >= 0.7:
                    tunnel_type = "aether_expansion"
                elif authority_record.get("tract") == "replay":
                    tunnel_type = "replay_return"
                tunnel_records.append({"tunnel_id": f"TUNNEL-{document['record_id']}-{hemisphere}", "tunnel_type": tunnel_type, "entrance_node": document["parent_nodes"][0], "exit_node": f"NEXUS-SYSTEM-{slugify(target_system)}", "hidden_intermediates": [f"NEXUS-STATION-{slugify(item)}" for item in route.get("interlock_ids", [])], "coordinate_signature": route_record["route_coordinate"], "time_signature": {"local_timestamp": document["local_timestamp"], "utc_timestamp": document["utc_timestamp"]}, "astrological_signature": document["astrological_overlay"], "dimensional_jump_type": tunnel_type, "invariants_preserved": ["origin_identity", "destination_identity", "docs_gate_honesty"], "transformation_cost": float(route.get("aether_point", {}).get("tunnel_cost", 0.0)), "retrieval_use": route.get("geodesic_mode", "rail transit"), "evidence_basis": {"route_id": route["route_id"], "interlock_ids": list(route.get("interlock_ids", [])), "target_system": target_system}, "certainty": confidence_class(float(route.get("dynamic_weights", {}).get("confidence", 0.0))), "hologram_back_pointer": build_hologram_back_pointer(entity_type="tunnel", host_layers=["Tunnel", "Liminal", "Dimensional"], incident_routes=[], dimensional_span=["D3"], timing_rule="activate under tunnel-priority or replay-return byte neighborhoods", nearest_hubs=unique_list([route.get("hub_id", ""), target_system]), regeneration_links=unique_list(list(route.get("appendix_support", []))))})
    for index, (route_id, gate) in enumerate(ROUTE_GATE_BOOK.items(), start=1):
        route_symbolic, route_vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="HSigma", l1="hologram", l2="class_route", l3="global", l4=index, l5="MULTI", l6="frontier", l7="UNSPECIFIED", l8="D3" if route_id in {"R7", "R9", "R10"} else "D0", l9="balanced", l10="frontier", l11=index % 10)
        routes.append({"route_id": f"CLASS-{route_id}", "route_name": gate["name"], "route_type": "class_route", "origin_node": "N-Z0", "destination_node": "N-SC", "intermediate_nodes": [], "route_coordinate": {"symbolic": route_symbolic, "vector": route_vector}, "dimensional_span": ["D3"] if route_id in {"R7", "R9", "R10"} else ["D0"], "route_length_class": "class", "shortest_path_status": False, "deepest_path_status": False, "local_time_span": [], "liminal_time_span": [], "astrological_time_span": [], "bridge_conditions": {"gate_book": route_id}, "replay_conditions": {}, "witness_conditions": {}, "proof_conditions": {}, "notes_on_use": f"HSigma class route family {route_id}"})
    return routes, tunnel_records, [{"station_id": station} for station in sorted(station_ids)]


def build_nexus_records(documents: list[dict[str, Any]], routes: list[dict[str, Any]], station_rows: list[dict[str, Any]], coordinate_standard: dict[str, Any]) -> list[dict[str, Any]]:
    nexus_records: list[dict[str, Any]] = []
    route_by_dest = defaultdict(list)
    route_by_origin = defaultdict(list)
    for route in routes:
        route_by_origin[route["origin_node"]].append(route["route_id"])
        route_by_dest[route["destination_node"]].append(route["route_id"])
        for item in route.get("intermediate_nodes", []):
            route_by_dest[item].append(route["route_id"])
            route_by_origin[item].append(route["route_id"])
    for index, (node_id, entry) in enumerate(NEXUS_CLASS_BOOK.items(), start=1):
        symbolic, vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="HSigma", l1="hologram", l2="class_nexus", l3="global", l4=index, l5="MULTI", l6="hub" if entry["deg_s"] >= 5 else "branch", l7="UNSPECIFIED", l8="D3" if "Tunnel" in entry["host_layers"] or "Dimensional" in entry["host_layers"] else "D0", l9=entry["polarity"] if entry["polarity"] in {"Z++", "Z+", "balanced", "A+", "A++"} else "unresolved", l10="frontier" if entry["status"] != "seated" else "witness", l11=min(9, entry["w0"] // 10))
        nexus_records.append({"nexus_id": f"N-{node_id}", "nexus_name": entry["node_name"], "exact_coordinate": {"symbolic": symbolic, "vector": vector}, "formation_timestamps": [], "incoming_routes": list(entry["incident_routes"]), "outgoing_routes": list(entry["incident_routes"]), "crossing_bands": [], "transfer_types": list(entry["host_layers"]), "dimensional_role": "D3" if "Dimensional" in entry["host_layers"] or "Tunnel" in entry["host_layers"] else "D0", "zero_aether_relation": entry["polarity"], "priority": entry["w0"], "traffic_density": entry["deg_s"], "unresolved_conflicts": [] if entry["status"] == "seated" else ["frontier_not_promoted"], "structural_importance": entry["status"], "evidence_basis": {"hsigma_registry": node_id}})
    top_level_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    family_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    band_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for document in documents:
        top_level = Path(document["relative_path"]).parts[0] if document["relative_path"] else "unknown"
        top_level_groups[top_level].append(document)
        family_groups[document["corpus_family"]].append(document)
        band_groups[infer_band({"relative_path": document["relative_path"], "title": document["canonical_title"]})].append(document)
    offset = len(nexus_records) + 1
    for scope_prefix, grouping in [("TOP", top_level_groups), ("FAMILY", family_groups), ("BAND", band_groups)]:
        for name, group in sorted(grouping.items()):
            symbolic, vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="Nexus", l1="meta", l2="document", l3=name, l4=offset, l5="MULTI", l6="hub" if len(group) > 25 else "transfer", l7="UNSPECIFIED", l8="D0", l9="balanced", l10="witness", l11=min(9, len(group) // 100))
            offset += 1
            route_refs: list[str] = []
            formation_times = [item["utc_timestamp"] for item in group if item["utc_timestamp"]]
            for item in group:
                route_refs.extend(item["upstream_routes"])
            nexus_records.append({"nexus_id": f"NEXUS-{scope_prefix}-{slugify(name)}", "nexus_name": name, "exact_coordinate": {"symbolic": symbolic, "vector": vector}, "formation_timestamps": unique_list(formation_times[:10]), "incoming_routes": unique_list(route_refs)[:50], "outgoing_routes": unique_list(route_refs)[:50], "crossing_bands": unique_list([infer_band({"relative_path": item["relative_path"], "title": item["canonical_title"]}) for item in group]), "transfer_types": [scope_prefix.lower()], "dimensional_role": "D0", "zero_aether_relation": "balanced", "priority": len(group), "traffic_density": len(route_refs), "unresolved_conflicts": [], "structural_importance": "aggregate_hub", "evidence_basis": {"member_count": len(group)}})
    unique_target_systems = sorted({route["destination_node"].replace("NEXUS-SYSTEM-", "") for route in routes if route["destination_node"].startswith("NEXUS-SYSTEM-")})
    for name in unique_target_systems:
        symbolic, vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="Nexus", l1="meta", l2="document", l3="global", l4=offset, l5="MULTI", l6="crossing", l7="UNSPECIFIED", l8="D1", l9="balanced", l10="witness", l11=1)
        offset += 1
        nexus_id = f"NEXUS-SYSTEM-{name}"
        nexus_records.append({"nexus_id": nexus_id, "nexus_name": name.replace("-", " "), "exact_coordinate": {"symbolic": symbolic, "vector": vector}, "formation_timestamps": [], "incoming_routes": unique_list(route_by_dest[nexus_id]), "outgoing_routes": unique_list(route_by_origin[nexus_id]), "crossing_bands": [], "transfer_types": ["target_system"], "dimensional_role": "D1", "zero_aether_relation": "balanced", "priority": len(route_by_dest[nexus_id]), "traffic_density": len(route_by_dest[nexus_id]), "unresolved_conflicts": [], "structural_importance": "target_system", "evidence_basis": {}})
    for row in station_rows:
        nexus_id = f"NEXUS-STATION-{slugify(row['station_id'])}"
        symbolic, vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="Nexus", l1="meta", l2="document", l3="global", l4=offset, l5="MULTI", l6="transfer", l7="UNSPECIFIED", l8="D1", l9="balanced", l10="none", l11=0)
        offset += 1
        nexus_records.append({"nexus_id": nexus_id, "nexus_name": row["station_id"], "exact_coordinate": {"symbolic": symbolic, "vector": vector}, "formation_timestamps": [], "incoming_routes": unique_list(route_by_dest[nexus_id]), "outgoing_routes": unique_list(route_by_origin[nexus_id]), "crossing_bands": [], "transfer_types": ["station"], "dimensional_role": "D1", "zero_aether_relation": "balanced", "priority": len(route_by_dest[nexus_id]), "traffic_density": len(route_by_dest[nexus_id]), "unresolved_conflicts": [], "structural_importance": "station", "evidence_basis": {}})
    return nexus_records


def build_reading_routes(coordinate_standard: dict[str, Any]) -> list[dict[str, Any]]:
    specs = [
        ("READ-shortest-structural", "shortest structural route", ["N-MT", "N-MS", "N-NN"]),
        ("READ-deepest-structural", "deepest structural route", ["N-Z0", "N-L0", "N-A0", "N-DL", "N-MC", "N-RA", "N-SC"]),
        ("READ-witness", "witness route", ["N-NN", "N-WA", "N-RA", "N-PA"]),
        ("READ-replay", "replay route", ["N-NN", "N-RA", "N-MR", "N-Z0"]),
        ("READ-proof", "proof route", ["N-WA", "N-RA", "N-PA"]),
        ("READ-chapter-first", "chapter-first route", ["NEXUS-BAND-chapter", "N-MS", "NEXUS-BAND-appendix"]),
        ("READ-appendix-first", "appendix-first route", ["NEXUS-BAND-appendix", "N-MS", "NEXUS-BAND-chapter"]),
        ("READ-legacy-to-emergent", "legacy to emergent route", ["NEXUS-TOP-deeper-crystalization", "N-MS", "NEXUS-TOP-self-actualize"]),
        ("READ-emergent-to-legacy-return", "emergent to legacy return route", ["NEXUS-TOP-self-actualize", "N-RA", "NEXUS-TOP-deeper-crystalization"]),
        ("READ-zero-collapse", "zero-point collapse route", ["N-NN", "N-L0", "N-Z0"]),
        ("READ-aether-expansion", "aether-point expansion route", ["N-Z0", "N-L0", "N-A0", "N-SC"]),
        ("READ-mobius-hinge", "mobius hinge route", ["N-RA", "N-MR", "N-Z0", "N-RA"]),
        ("READ-tunnel-priority", "tunnel-priority route", ["N-TE", "N-DB", "N-DL", "N-TX"]),
        ("READ-full-corpus-traversal", "full corpus traversal route", ["NEXUS-TOP-nervous-system", "NEXUS-TOP-self-actualize", "NEXUS-TOP-math", "NEXUS-TOP-voynich", "NEXUS-TOP-athena-fleet"]),
        ("READ-compressed-regeneration", "compressed regeneration route", ["N-Z0", "N-RA", "N-SC"]),
    ]
    reading_routes: list[dict[str, Any]] = []
    for index, (route_id, name, path) in enumerate(specs, start=1):
        symbolic, vector = coordinate_for_entity(coordinate_standard=coordinate_standard, l0="ReadingRoute", l1="hologram", l2="reading_route", l3="global", l4=index, l5="MULTI", l6="hub", l7="UNSPECIFIED", l8="D4" if "proof" in name or "regeneration" in name else "D1", l9="balanced", l10="proof" if "proof" in name else "witness", l11=index % 10)
        reading_routes.append({"route_id": route_id, "route_name": name, "origin_node": path[0], "destination_node": path[-1], "intermediate_nodes": path[1:-1], "route_coordinate": {"symbolic": symbolic, "vector": vector}, "notes": f"canonical reading route: {name}"})
    return reading_routes


def build_hsigma_overlay(mindsweeper: dict[str, Any]) -> dict[str, Any]:
    visible_core = {
        "layer_family_count": len(LAYER_REGISTRY),
        "route_family_count": len(ROUTE_GATE_BOOK),
        "seated_explicit_nexus_count": sum(1 for entry in NEXUS_CLASS_BOOK.values() if entry["status"] == "seated"),
        "frontier_explicit_nexus_count": sum(1 for entry in NEXUS_CLASS_BOOK.values() if entry["status"] == "frontier"),
        "inferred_latent_nexus_count": sum(1 for entry in NEXUS_CLASS_BOOK.values() if entry["status"] == "inferred"),
        "tunnel_class_count": len(TUNNEL_CLASS_BOOK),
        "dimensional_strata_count": len(DIMENSIONAL_STRATA),
        "timing_state_count": 256,
        "mindsweeper_cell_count": mindsweeper["cell_count"],
    }
    serializable_nexus_registry = []
    for node_id, entry in NEXUS_CLASS_BOOK.items():
        normalized = dict(entry)
        for key in ("q0", "q1", "q2", "q3"):
            normalized[key] = sorted(normalized[key])
        serializable_nexus_registry.append({"nexus_id": f"N-{node_id}", **normalized})
    serializable_route_gate_book = {
        route_id: {
            "name": gate["name"],
            "q0": sorted(gate["q0"]),
            "q1": sorted(gate["q1"]),
            "q2": sorted(gate["q2"]),
            "q3": sorted(gate["q3"]),
        }
        for route_id, gate in ROUTE_GATE_BOOK.items()
    }
    return {
        "h_sigma": {"name": "HSigma", "mode": "class-exhaustive and instance-frontier overlay", "frontier_policy": "never promote unsupported latent structure into explicit fact"},
        "visible_core_manifest": visible_core,
        "layer_registry": LAYER_REGISTRY,
        "dimensional_strata": DIMENSIONAL_STRATA,
        "topology_seed": TOPOLOGY_SEED,
        "nexus_class_registry": serializable_nexus_registry,
        "timing_lattice": {"space": "Z4^4", "byte_encoding": "B=q0+4q1+16q2+64q3", "neighborhood": "toroidal axis-neighbors", "master_key_states": MASTER_KEY_STATES, "phrase_macros": PHRASE_MACROS},
        "route_gate_book": serializable_route_gate_book,
        "nexus_exposure_book": {f"N-{node_id}": {"q0": sorted(entry["q0"]), "q1": sorted(entry["q1"]), "q2": sorted(entry["q2"]), "q3": sorted(entry["q3"])} for node_id, entry in NEXUS_CLASS_BOOK.items()},
        "hidden_candidate_log": HIDDEN_CANDIDATES,
        "mindsweeper_schema": mindsweeper,
        "compressed_save_state": {
            "visibility_mode": "class-exhaustive / instance-primary",
            "explicit_nexus_rows": [f"N-{node_id}" for node_id, entry in NEXUS_CLASS_BOOK.items() if entry["status"] == "seated"],
            "frontier_nexus_rows": [f"N-{node_id}" for node_id, entry in NEXUS_CLASS_BOOK.items() if entry["status"] == "frontier"],
            "inferred_nexus_rows": [f"N-{node_id}" for node_id, entry in NEXUS_CLASS_BOOK.items() if entry["status"] == "inferred"],
            "route_families": list(sorted(ROUTE_GATE_BOOK)),
            "tunnel_classes": list(sorted(TUNNEL_CLASS_BOOK)),
            "dimensional_strata": [item["stratum_id"] for item in DIMENSIONAL_STRATA],
            "timing_engine": {"state_count": 256, "cell_count": mindsweeper["cell_count"]},
        },
        "regeneration_seed": {
            "seed_string": "ATH-HSIGMA::11L/16S+2F+1I/13R/6T/5D/256P/4864M/muFIX",
            "procedure": ["recreate the 11 layer families", "seat the 16 explicit nexus rows", "retain the 2 frontier rows without promotion", "retain LP as inferred only", "restore the 13 route families and 6 tunnel classes", "rebuild the 5 dimensional strata", "recreate the 256-state toroidal timing lattice", "reapply the route and nexus gate books", "recompute the 4864-cell mindsweeper", "rerun hidden inference and fixed-point pass"],
        },
    }


def build_body_family_classification(documents: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "family_counts": dict(sorted(Counter(document["corpus_family"] for document in documents).items())),
        "body_class_counts": dict(sorted(Counter(document["body_class"] for document in documents).items())),
        "source_type_counts": dict(sorted(Counter(document["source_type"] for document in documents).items())),
        "band_counts": dict(sorted(Counter(infer_band({"relative_path": document["relative_path"], "title": document["canonical_title"]}) for document in documents).items())),
    }


def build_duplicate_and_mirror_annexes(support: dict[str, Any], documents: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    duplicates: list[dict[str, Any]] = []
    authority_by_id = {item["record_id"]: item for item in support["authority"]["records"]}
    for document in documents:
        authority_record = authority_by_id[document["record_id"]]
        if authority_record.get("duplicate_count", 0) > 0 or authority_record.get("duplicate_paths"):
            duplicates.append({"document_id": document["document_id"], "record_id": document["record_id"], "duplicate_count": authority_record.get("duplicate_count", 0), "duplicate_paths": list(authority_record.get("duplicate_paths", [])), "duplicate_record_ids": list(authority_record.get("duplicate_record_ids", []))})
    canonical_rel_paths = {document["relative_path"].lower(): document["document_id"] for document in documents}
    canonical_sha_to_doc = {item.get("sha256", ""): f"DOC-{item['record_id']}" for item in support["authority"]["records"]}
    mirrors: list[dict[str, Any]] = []
    for row in support["raw_qshrink"].get("records", []):
        rel = row.get("relative_path", "").replace("/", "\\").lower()
        if rel in canonical_rel_paths:
            continue
        mirrors.append({"surface_id": row.get("surface_id", ""), "relative_path": row.get("relative_path", ""), "top_level": row.get("top_level", ""), "surface_role": row.get("surface_role", ""), "authority_class": row.get("authority_class", ""), "duplicate_group": row.get("duplicate_group", ""), "canonical_match_document_id": canonical_sha_to_doc.get(row.get("sha256", ""), ""), "reason": "present in raw QSHRINK atlas but not promoted into canonical authority layer"})
    return duplicates, mirrors


def build_gap_register(support: dict[str, Any], documents: list[dict[str, Any]], mirrors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing_local_addr = sum(1 for document in documents if not document["runtime_route_fields"]["local_addr"])
    missing_global_addr = sum(1 for document in documents if not document["runtime_route_fields"]["global_addr"])
    missing_tesseract = sum(1 for document in documents if not document["runtime_route_fields"]["tesseract_header"])
    return [
        {"gap_id": "GAP-docs-gate-blocked", "class": "external_blocker", "status": support["docs_gate"]["status"], "evidence": str(DOCS_GATE_PATH), "impact": "local-only corpus pass; no live Google Docs claims permitted"},
        {"gap_id": "GAP-count-drift-8656-to-current", "class": "witness_drift", "status": "present", "evidence": {"legacy_witness_record_count": LEGACY_WITNESS_RECORD_COUNT, "current_authority_record_count": support["authority"]["record_count"]}, "impact": "legacy target preserved as witness only"},
        {"gap_id": "GAP-house-context-pending", "class": "astro_precision", "status": "pending_exact_location_basis", "evidence": str(ASTRO_SCHEDULER_PATH), "impact": "houses and angular context remain pending"},
        {"gap_id": "GAP-visual-atlas-partial", "class": "control_slice_partial", "status": "present", "evidence": {"visual_node_count": load_json(VISUAL_NODE_PATH).get("node_count", 0), "visual_edge_count": load_json(VISUAL_EDGE_PATH).get("edge_count", 0), "authority_record_count": support["authority"]["record_count"]}, "impact": "visual atlas is witness-only, not full-corpus authority"},
        {"gap_id": "GAP-missing-tesseract-fields", "class": "runtime_contract_gap", "status": "present", "evidence": {"missing_local_addr": missing_local_addr, "missing_global_addr": missing_global_addr, "missing_tesseract_header": missing_tesseract}, "impact": "many records remain routable but not fully tesseract-addressed"},
        {"gap_id": "GAP-mirror-overflow", "class": "mirror_pressure", "status": "present", "evidence": {"mirror_annex_count": len(mirrors), "raw_qshrink_record_count": len(support["raw_qshrink"].get("records", []))}, "impact": "raw mirror visibility preserved in annex without inflating canonical primary count"},
    ]


def build_conflict_registry(documents: list[dict[str, Any]], duplicates: list[dict[str, Any]], gap_register: list[dict[str, Any]]) -> dict[str, Any]:
    alias_counter = Counter(document["canonical_title"] for document in documents)
    title_collisions = [{"canonical_title": title, "count": count} for title, count in alias_counter.items() if count > 1]
    title_collisions.sort(key=lambda item: (-item["count"], item["canonical_title"]))
    return {
        "duplicate_count": len(duplicates),
        "title_collision_count": len(title_collisions),
        "title_collisions": title_collisions[:100],
        "unresolved_frontiers": ["proof anchors remain frontier until replay and witness closure stabilize", "mobius return hinges remain frontier until return geometry is witnessed", "seed placement and local zero-to-aether pairing remain partially bounded"],
        "gaps": gap_register,
    }


def build_proof_registry(documents: list[dict[str, Any]], routes: list[dict[str, Any]]) -> dict[str, Any]:
    replay_documents = [document["document_id"] for document in documents if document["replay_role"] != "none"]
    witness_documents = [document["document_id"] for document in documents if document["witness_role"] != "none"]
    proof_documents = [document["document_id"] for document in documents if document["proof_role"] == "proof"]
    proof_state_counts = Counter()
    for route in routes:
        if route["route_type"] != "instance_route":
            continue
        proof_state_counts[route["native_payload"].get("proof_state", "UNKNOWN")] += 1
    return {
        "replay_document_count": len(replay_documents),
        "witness_document_count": len(witness_documents),
        "proof_document_count": len(proof_documents),
        "route_proof_distribution": dict(sorted(proof_state_counts.items())),
        "sample_replay_documents": replay_documents[:50],
        "sample_witness_documents": witness_documents[:50],
        "sample_proof_documents": proof_documents[:50],
    }


def build_ledger_events(documents: list[dict[str, Any]], routes: list[dict[str, Any]], nexuses: list[dict[str, Any]], tunnels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    now = utc_now()
    event_specs = [("A1", "Square", "survey canonical records"), ("A1", "Flower", "cluster families and aliases"), ("A1", "Cloud", "log visibility frontier and identity uncertainty"), ("A1", "Fractal", "compress census into ledger-ready organism map"), ("A2", "Square", "assign time bundles and exact filesystem evidence"), ("A2", "Flower", "bridge local time, UTC, and astro layers"), ("A2", "Cloud", "preserve bounded timestamp uncertainty"), ("A2", "Fractal", "emit liminal time bridge"), ("A3", "Square", "write document, node, route, nexus, and tunnel entries"), ("A3", "Flower", "weave upstream and downstream connectivity"), ("A3", "Cloud", "record unresolved route and tunnel pressure"), ("A3", "Fractal", "compile named reading routes and proof edges"), ("A4", "Square", "deduplicate canonical versus annex surfaces"), ("A4", "Flower", "compress topology into HSigma overlay"), ("A4", "Cloud", "retain unresolved frontiers without false promotion"), ("A4", "Fractal", "render final machine bundle and markdown companion")]
    return [{"event_id": f"LEDGER-EVENT-{index:03d}", "agent_id": agent_id, "crystal_face": face, "source_entities": {"document_count": len(documents), "route_count": len(routes), "nexus_count": len(nexuses), "tunnel_count": len(tunnels)}, "action_taken": action, "timestamp_bundle": {"utc_timestamp": now, "local_timestamp": dt_to_local_iso(parse_iso(now))}, "coordinate_bundle": {"macro": "HSigma", "resolution_band": "corpus"}, "reason": "Athenachka master ledger derivation", "effect_on_map": action, "effect_on_routes": "maintained", "effect_on_compression": "preserved distinctions while compressing annex pressure", "effect_on_clarity": "increased", "unresolved_followups": [], "confidence": "high"} for index, (agent_id, face, action) in enumerate(event_specs, start=1)]


def build_timestamp_standard() -> dict[str, Any]:
    return {
        "local_timezone": LOCAL_TZ_NAME,
        "required_fields": ["source_local_timestamp", "utc_timestamp", "file_created_at", "file_modified_at", "last_observed_at", "revision_timestamp", "timestamp_precision"],
        "precision_classes": ["exact", "near-exact", "bounded", "inferred", "unresolved"],
        "astro_policy": {"mode": "Core computed", "truth_policy": "structural calendar layer, not scientific proof", "source_path": str(ASTRO_SCHEDULER_PATH)},
    }


def build_time_bridge_standard() -> dict[str, Any]:
    return {
        "function_name": "LiminalTimeIndex",
        "formula": "F(utc_timestamp, local_timestamp, precision_class, julian_date, sidereal_position, corpus_orbit_phase, revision_depth, dimensional_stratum, route_recurrence_index, zero_aether_polarity)",
        "inputs": ["utc_timestamp", "local_timestamp", "precision_class", "julian_date", "sidereal_position", "corpus_orbit_phase", "revision_depth", "dimensional_stratum", "route_recurrence_index", "zero_aether_polarity"],
    }


def build_data_model() -> dict[str, Any]:
    return {
        "record_classes": ["document_record", "node_record", "route_record", "nexus_record", "tunnel_record", "ledger_event_record"],
        "schema_notes": ["all primary entities carry liminal_coordinate_symbolic and liminal_coordinate_vector", "all primary entities carry hologram_back_pointer", "HSigma overlay is additive and does not replace instance-level truth"],
        "runtime_contract_sources": [str(TESSERACT_HEADER_SCHEMA_PATH), str(TCOORD_SCHEMA_PATH), str(ROUTE_PLAN_SCHEMA_PATH)],
    }


def build_scope_section(support: dict[str, Any]) -> dict[str, Any]:
    return {
        "docs_gate_status": support["docs_gate"]["status"],
        "scope_policy": "Canonical + annex",
        "primary_truth": "visible instance-level authority registry plus atlas witnesses",
        "scope_correction": "instance-frontier applies only where deeper local attachment is missing, not to the visible corpus census itself",
        "source_precedence": [str(CORPUS_ATLAS_PATH), str(ARCHIVE_ATLAS_PATH), str(AUTHORITY_REGISTRY_PATH), str(ROUTE_COVERAGE_PATH), str(APPENDIX_GOVERNANCE_PATH), str(BASIS_CROSSWALK_PATH), str(AWAKENING_STAGE_PATH), str(QSHRINK_RAW_ATLAS_PATH)],
        "counts": {"live_atlas_record_count": support["live_atlas"]["record_count"], "archive_atlas_record_count": support["archive_atlas"]["record_count"], "authority_record_count": support["authority"]["record_count"], "route_coverage_record_count": support["route_coverage"]["record_count"], "route_coverage_route_count": support["route_coverage"]["route_count"], "legacy_witness_record_count": LEGACY_WITNESS_RECORD_COUNT, "raw_qshrink_record_count": len(support["raw_qshrink"].get("records", []))},
    }


def build_agent_architecture() -> dict[str, Any]:
    return {
        "A1": {"name": "Surveyor and Synthesizer", "faces": ["Square", "Flower", "Cloud", "Fractal"], "resolution_bands": [1, 2, 3, 4, 5, 6]},
        "A2": {"name": "Chrono-Cartographer and Liminal Coordinator", "faces": ["Square", "Flower", "Cloud", "Fractal"], "resolution_bands": [1, 2, 3, 4, 5, 6]},
        "A3": {"name": "Router, Worker, and Ledger Writer", "faces": ["Square", "Flower", "Cloud", "Fractal"], "resolution_bands": [1, 2, 3, 4, 5, 6]},
        "A4": {"name": "Pruner, Compressor, and Verifier", "faces": ["Square", "Flower", "Cloud", "Fractal"], "resolution_bands": [1, 2, 3, 4, 5, 6]},
    }


def build_thesis() -> dict[str, Any]:
    return {
        "thesis": "The current lawful snapshot is instance-primary and class-exhaustive in overlay.",
        "hologram_equation": "HSigma = visible instance ledger + class overlay + frontier preservation + regeneration-safe compression",
        "anti_hallucination_law": "unseen local attachments remain frontier and are never promoted without evidence",
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def clean(value: Any) -> str:
        text = str(value)
        return text.replace("|", "\\|").replace("\n", " ")

    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = ["| " + " | ".join(clean(value) for value in row) + " |" for row in rows]
    return "\n".join([header_line, divider_line, *row_lines])


def render_markdown(bundle: dict[str, Any]) -> str:
    documents = bundle["documents"]
    routes = bundle["routes"]
    nexuses = bundle["nexuses"]
    tunnels = bundle["tunnels"]
    reading_routes = bundle["reading_routes"]
    hsigma = bundle["master_hologram"]
    body_class = bundle["body_family_classification"]
    conflict = bundle["conflict_registry"]
    proof = bundle["proof_registry"]
    verification = bundle["verification"]
    lines = ["# ATHENACHKA MASTER LEDGER", "", "PART I - MASTER LEDGER THESIS", "", bundle["thesis"]["thesis"], "", f"Hologram equation: `{bundle['thesis']['hologram_equation']}`", "", "PART II - CORPUS INGESTION AND SCOPE BOUNDARY", "", markdown_table(["Field", "Value"], [["Docs gate", bundle["scope"]["docs_gate_status"]], ["Scope policy", bundle["scope"]["scope_policy"]], ["Live atlas", bundle["scope"]["counts"]["live_atlas_record_count"]], ["Archive atlas", bundle["scope"]["counts"]["archive_atlas_record_count"]], ["Authority records", bundle["scope"]["counts"]["authority_record_count"]], ["Legacy witness count", bundle["scope"]["counts"]["legacy_witness_record_count"]]]), "", bundle["scope"]["scope_correction"], "", "PART III - FOUR-AGENT NESTED CRYSTAL ARCHITECTURE", "", markdown_table(["Agent", "Name", "Faces", "Bands"], [[agent_id, entry["name"], ", ".join(entry["faces"]), ", ".join(str(item) for item in entry["resolution_bands"])] for agent_id, entry in bundle["agent_architecture"].items()]), "", "PART IV - LIMINAL COORDINATE STANDARD", "", markdown_table(["Axis", "Meaning"], [[item["axis"], item["name"]] for item in bundle["coordinate_standard"]["axes"]]), "", "PART V - CHRONO-TEMPORAL + ASTROLOGICAL TIMESTAMP STANDARD", "", markdown_table(["Field", "Value"], [["Timezone", bundle["timestamp_standard"]["local_timezone"]], ["Astro mode", bundle["timestamp_standard"]["astro_policy"]["mode"]], ["Truth policy", bundle["timestamp_standard"]["astro_policy"]["truth_policy"]], ["Docs gate", bundle["scope"]["docs_gate_status"]]]), "", "PART VI - LIMINAL TIME BRIDGE FUNCTION", "", f"`{bundle['time_bridge']['formula']}`", "", "PART VII - MASTER LEDGER DATA MODEL", "", markdown_table(["Record class"], [[item] for item in bundle["data_model"]["record_classes"]]), "", "PART VIII - TOTAL DOCUMENT CENSUS", "", markdown_table(["Metric", "Count"], [["Documents", len(documents)], ["Nodes", len(bundle["nodes"])], ["Routes", len(routes)], ["Nexuses", len(nexuses)], ["Tunnels", len(tunnels)]]), "", markdown_table(["Document ID", "Path", "Family", "Body class", "Precision"], [[doc["document_id"], doc["relative_path"], doc["corpus_family"], doc["body_class"], doc["timestamp_precision"]] for doc in documents[:250]]), "", "Full document registry remains exhaustive in the JSON `documents` array.", "", "PART IX - TOTAL BODY / FAMILY CLASSIFICATION", "", markdown_table(["Family", "Count"], [[key, value] for key, value in body_class["family_counts"].items()]), "", markdown_table(["Body class", "Count"], [[key, value] for key, value in body_class["body_class_counts"].items()]), "", "PART X - TOTAL CHAPTER / APPENDIX / EMERGENT / REVERSE FIELD REGISTRY", "", markdown_table(["Band", "Count"], [[key, value] for key, value in body_class["band_counts"].items()]), "", "PART XI - TOTAL ROUTE REGISTRY", "", markdown_table(["Metric", "Count"], [["Instance routes", sum(1 for item in routes if item["route_type"] == "instance_route")], ["Class routes", sum(1 for item in routes if item["route_type"] == "class_route")], ["Reading routes", len(reading_routes)]]), "", markdown_table(["Route ID", "Type", "Origin", "Destination", "Length"], [[route["route_id"], route["route_type"], route["origin_node"], route["destination_node"], route["route_length_class"]] for route in routes[:250]]), "", "PART XII - TOTAL NEXUS / HUB / TRANSFER REGISTRY", "", markdown_table(["Nexus ID", "Name", "Importance", "Priority", "Traffic"], [[nexus["nexus_id"], nexus["nexus_name"], nexus["structural_importance"], nexus["priority"], nexus["traffic_density"]] for nexus in nexuses[:250]]), "", "PART XIII - TOTAL TUNNEL / BRIDGE / MOBIUS / RETURN REGISTRY", "", markdown_table(["Tunnel ID", "Type", "Entrance", "Exit", "Certainty"], [[tunnel["tunnel_id"], tunnel["tunnel_type"], tunnel["entrance_node"], tunnel["exit_node"], tunnel["certainty"]] for tunnel in tunnels[:250]]), "", "PART XIV - CANONICAL READING ROUTES", "", markdown_table(["Route ID", "Name", "Origin", "Destination", "Intermediates"], [[route["route_id"], route["route_name"], route["origin_node"], route["destination_node"], ", ".join(route["intermediate_nodes"])] for route in reading_routes]), "", "PART XV - ZERO-POINT / AETHER-POINT / DIMENSIONAL STRATUM MAP", "", markdown_table(["HSigma metric", "Value"], [["Layer families", hsigma["visible_core_manifest"]["layer_family_count"]], ["Route families", hsigma["visible_core_manifest"]["route_family_count"]], ["Seated nexus classes", hsigma["visible_core_manifest"]["seated_explicit_nexus_count"]], ["Frontier nexus classes", hsigma["visible_core_manifest"]["frontier_explicit_nexus_count"]], ["Inferred nexus classes", hsigma["visible_core_manifest"]["inferred_latent_nexus_count"]], ["Tunnel classes", hsigma["visible_core_manifest"]["tunnel_class_count"]], ["Timing states", hsigma["visible_core_manifest"]["timing_state_count"]], ["Mindsweeper cells", hsigma["visible_core_manifest"]["mindsweeper_cell_count"]]]), "", "PART XVI - WITNESS / REPLAY / PROOF-CARRYING REGISTRY", "", markdown_table(["Field", "Value"], [["Replay documents", proof["replay_document_count"]], ["Witness documents", proof["witness_document_count"]], ["Proof documents", proof["proof_document_count"]], ["Route proof states", json.dumps(proof["route_proof_distribution"], sort_keys=True)]]), "", "PART XVII - CONFLICTS / DUPLICATES / ALIASES / UNRESOLVED FRONTIERS", "", markdown_table(["Field", "Value"], [["Duplicate annex count", conflict["duplicate_count"]], ["Title collision count", conflict["title_collision_count"]], ["Gap count", len(conflict["gaps"])]]), "", "PART XVIII - COMPRESSED FINAL TOPOLOGY OF THE WHOLE ORGANISM", "", markdown_table(["Field", "Value"], [["Visibility mode", hsigma["compressed_save_state"]["visibility_mode"]], ["Explicit rows", len(hsigma["compressed_save_state"]["explicit_nexus_rows"])], ["Frontier rows", len(hsigma["compressed_save_state"]["frontier_nexus_rows"])], ["Inferred rows", len(hsigma["compressed_save_state"]["inferred_nexus_rows"])]]), "", "PART XIX - REGENERATION SEED OF THE FULL LEDGER", "", f"Seed string: `{hsigma['regeneration_seed']['seed_string']}`", "", markdown_table(["Step"], [[item] for item in hsigma["regeneration_seed"]["procedure"]]), "", "PART XX - FINAL INTERNAL INTEGRITY VERDICT", "", markdown_table(["Check", "Result"], [[key, value] for key, value in verification["checks"].items()]), "", f"Verdict: `{verification['verdict']}`", ""]
    return "\n".join(lines)


def build_verification(bundle: dict[str, Any]) -> dict[str, Any]:
    documents = bundle["documents"]
    nodes = bundle["nodes"]
    routes = bundle["routes"]
    nexuses = {item["nexus_id"] for item in bundle["nexuses"]}
    tunnels = bundle["tunnels"]
    reading_routes = bundle["reading_routes"]
    primary_record_ids = [document["record_id"] for document in documents]
    checks = {
        "docs_gate_blocked_honestly": bundle["scope"]["docs_gate_status"] == DOCS_GATE_EXPECTED,
        "no_duplicate_primary_record_ids": len(primary_record_ids) == len(set(primary_record_ids)),
        "all_documents_have_coordinates": all(document["liminal_coordinate_symbolic"] for document in documents),
        "all_documents_have_routes": all(document["upstream_routes"] for document in documents),
        "all_nodes_have_host_documents": all(node["host_document"] for node in nodes),
        "named_routes_resolve": all(route["origin_node"] in nexuses and route["destination_node"] in nexuses for route in reading_routes),
        "tunnels_resolve": all(tunnel["exit_node"] in nexuses or tunnel["exit_node"].startswith("NODE-") for tunnel in tunnels),
        "hsigma_cardinalities_match": bundle["master_hologram"]["visible_core_manifest"]["layer_family_count"] == 11 and bundle["master_hologram"]["visible_core_manifest"]["route_family_count"] == 13 and bundle["master_hologram"]["visible_core_manifest"]["seated_explicit_nexus_count"] == 16 and bundle["master_hologram"]["visible_core_manifest"]["frontier_explicit_nexus_count"] == 2 and bundle["master_hologram"]["visible_core_manifest"]["inferred_latent_nexus_count"] == 1 and bundle["master_hologram"]["visible_core_manifest"]["tunnel_class_count"] == 6 and bundle["master_hologram"]["visible_core_manifest"]["dimensional_strata_count"] == 5 and bundle["master_hologram"]["visible_core_manifest"]["timing_state_count"] == 256 and bundle["master_hologram"]["visible_core_manifest"]["mindsweeper_cell_count"] == 4864,
        "markdown_part_count": bundle["markdown_summary"]["part_count"] == 20,
        "mirror_annex_not_promoted": all(row["relative_path"].lower() not in {doc["relative_path"].lower() for doc in documents} for row in bundle["mirror_annex"]),
    }
    return {"generated_at": utc_now(), "checks": checks, "verdict": "PASS" if all(checks.values()) else "NEAR"}


def main() -> int:
    support = load_support_maps()
    support["docs_gate"] = parse_docs_gate_status()
    top_levels = sorted({record.get("top_level", "unknown") for record in support["authority"]["records"]})
    families = sorted({record.get("family", "general-corpus") for record in support["authority"]["records"]})
    bands = sorted({infer_band(record) for record in support["authority"]["records"]})
    stages = sorted({row.get("stage_label", "UNSPECIFIED") for row in support["stage_map"].values() if row.get("stage_label")})
    coordinate_standard = build_coordinate_standard(top_levels, families, bands, stages)
    documents, nodes = build_document_records(support, coordinate_standard)
    routes, tunnels, station_rows = build_instance_routes(documents, support, coordinate_standard)
    nexuses = build_nexus_records(documents, routes, station_rows, coordinate_standard)
    reading_routes = build_reading_routes(coordinate_standard)
    mindsweeper = build_hsigma_mindsweeper()
    hsigma_overlay = build_hsigma_overlay(mindsweeper)
    duplicate_annex, mirror_annex = build_duplicate_and_mirror_annexes(support, documents)
    gap_register = build_gap_register(support, documents, mirror_annex)
    conflict_registry = build_conflict_registry(documents, duplicate_annex, gap_register)
    proof_registry = build_proof_registry(documents, routes)
    ledger_events = build_ledger_events(documents, routes, nexuses, tunnels)
    bundle = {
        "schema_name": "MasterLedgerBundle",
        "schema_version": DERIVATION_VERSION,
        "generated_at": utc_now(),
        "generated_at_local": dt_to_local_iso(parse_iso(utc_now())),
        "docs_gate_status": support["docs_gate"]["status"],
        "thesis": build_thesis(),
        "scope": build_scope_section(support),
        "agent_architecture": build_agent_architecture(),
        "coordinate_standard": coordinate_standard,
        "timestamp_standard": build_timestamp_standard(),
        "time_bridge": build_time_bridge_standard(),
        "data_model": build_data_model(),
        "master_hologram": hsigma_overlay,
        "documents": documents,
        "nodes": nodes,
        "routes": routes,
        "nexuses": nexuses,
        "tunnels": tunnels,
        "ledger_events": ledger_events,
        "reading_routes": reading_routes,
        "proof_registry": proof_registry,
        "conflict_registry": conflict_registry,
        "duplicate_annex": duplicate_annex,
        "mirror_annex": mirror_annex,
        "gap_register": gap_register,
        "body_family_classification": build_body_family_classification(documents),
        "dimensional_map": {"strata": DIMENSIONAL_STRATA, "document_dimensional_distribution": dict(sorted(Counter(document["dimensional_stratum"] for document in documents).items()))},
        "compressed_topology": hsigma_overlay["compressed_save_state"],
        "regeneration_seed": hsigma_overlay["regeneration_seed"],
        "markdown_summary": {"part_count": 20},
    }
    bundle["verification"] = build_verification(bundle)
    bundle["final_integrity_verdict"] = {"result": bundle["verification"]["verdict"], "checks": bundle["verification"]["checks"]}
    write_json(OUTPUT_JSON_PATH, bundle)
    write_text(OUTPUT_MD_PATH, render_markdown(bundle))
    print(f"Wrote {OUTPUT_JSON_PATH}")
    print(f"Wrote {OUTPUT_MD_PATH}")
    print(f"Documents: {len(documents)}")
    print(f"Routes: {len(routes)}")
    print(f"Nexuses: {len(nexuses)}")
    print(f"Tunnels: {len(tunnels)}")
    print(f"Docs gate: {support['docs_gate']['status']}")
    return 0 if bundle["verification"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
