from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


CONFIG_PATH = Path(__file__).with_name("config_v1.json")
SYNODIC_MONTH = 29.53058867
LUNAR_EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)


@dataclass(slots=True)
class Config:
    node_id: str
    timezone: str
    lat: float | None
    lon: float | None
    watch_root: str
    temple_root: str
    hall_root: str
    qshrink_root: str
    registry_root: str
    receipts_root: str
    docs_gate_file: str
    reconcile_seconds: int
    dedupe_window_ms: int


def load_config() -> Config:
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return Config(**raw)


def _julian_date(dt_utc: datetime) -> float:
    unix_epoch_jd = 2440587.5
    return unix_epoch_jd + dt_utc.timestamp() / 86400.0


def _sidereal_phase(dt_utc: datetime, lon: float | None) -> float:
    jd = _julian_date(dt_utc)
    t = (jd - 2451545.0) / 36525.0
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t - (t * t * t) / 38710000.0
    lmst = gmst + (lon or 0.0)
    return (lmst % 360.0) / 360.0


def _lunar_phase(dt_utc: datetime) -> float:
    days = (dt_utc - LUNAR_EPOCH).total_seconds() / 86400.0
    return (days / SYNODIC_MONTH) % 1.0


def _solar_phase(local_dt: datetime) -> float:
    equinox_offset = 79
    return ((local_dt.timetuple().tm_yday - equinox_offset) % 365) / 365.0


def _orbital_phase(local_dt: datetime) -> float:
    year_days = 366 if local_dt.year % 4 == 0 and (local_dt.year % 100 != 0 or local_dt.year % 400 == 0) else 365
    return (local_dt.timetuple().tm_yday - 1 + local_dt.hour / 24.0) / year_days


def _rotation_phase(local_dt: datetime) -> float:
    seconds = local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second + local_dt.microsecond / 1_000_000
    return seconds / 86400.0


def _sky_slot(sidereal_phase: float) -> int:
    return int(math.floor(sidereal_phase * 12)) % 12


def _goal_salience(priority: float, confidence: float) -> float:
    return round((priority + confidence) / 2.0, 6)


def _novelty_score(event_type: str, path_depth: int, watch_fallback: bool) -> float:
    base = {
        "create": 0.95,
        "move": 0.8,
        "modify": 0.65,
        "delete": 0.75,
    }.get(event_type, 0.5)
    depth_adjust = min(0.2, path_depth * 0.01)
    fallback_penalty = 0.15 if watch_fallback else 0.0
    return max(0.0, min(1.0, round(base + depth_adjust - fallback_penalty, 6)))


def liminal_timestamp(dt_utc: datetime) -> str:
    return f"LT-{dt_utc.timestamp():012.3f}"


def build_coord12(
    *,
    event_type: str,
    source_path: str,
    priority: float,
    confidence: float,
    queue_pressure: float,
    watch_fallback: bool = False,
) -> tuple[dict[str, object], str]:
    config = load_config()
    zone = ZoneInfo(config.timezone)
    dt_utc = datetime.now(tz=UTC)
    local_dt = dt_utc.astimezone(zone)
    coord_quality = "OK" if config.lat is not None and config.lon is not None else "NEAR"
    sidereal = _sidereal_phase(dt_utc, config.lon)
    dimensions = {
        "earth_utc_anchor": dt_utc.isoformat(),
        "earth_rotation_phase": round(_rotation_phase(local_dt), 6),
        "earth_orbital_phase": round(_orbital_phase(local_dt), 6),
        "earth_geospatial_anchor": {
            "node_id": config.node_id,
            "lat": config.lat,
            "lon": config.lon,
            "quality": coord_quality,
        },
        "solar_phase": round(_solar_phase(local_dt), 6),
        "lunar_phase": round(_lunar_phase(dt_utc), 6),
        "local_sidereal_phase": round(sidereal, 6),
        "canonical_sky_anchor": f"slot-{_sky_slot(sidereal)}",
        "runtime_region": config.node_id,
        "queue_pressure": round(max(0.0, min(1.0, queue_pressure)), 6),
        "goal_salience_vector": _goal_salience(priority, confidence),
        "change_novelty_vector": _novelty_score(event_type, len(Path(source_path).parts), watch_fallback),
    }
    values = [
        dimensions["earth_rotation_phase"],
        dimensions["earth_orbital_phase"],
        1.0 if coord_quality == "OK" else 0.5,
        dimensions["solar_phase"],
        dimensions["lunar_phase"],
        dimensions["local_sidereal_phase"],
        _sky_slot(sidereal) / 12.0,
        dimensions["queue_pressure"],
        dimensions["goal_salience_vector"],
        dimensions["change_novelty_vector"],
        1.0 if not watch_fallback else 0.5,
        1.0 if "ATHENA" in source_path.upper() else 0.6,
    ]
    return {
        "dimensions": dimensions,
        "values": values,
        "coord_quality": coord_quality,
    }, liminal_timestamp(dt_utc)


def earth_timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


def make_lookup_addr(
    *,
    node_id: str,
    liminal_gps: dict[str, object],
    zero_class: str,
    organ_class: str,
    current: str,
    phase_role: str,
    witness_class: str,
) -> dict[str, object]:
    return {
        "NodeId": node_id,
        "LiminalGPS": liminal_gps,
        "ZeroClass": zero_class,
        "OrganClass": organ_class,
        "Current": current,
        "PhaseRole": phase_role,
        "WitnessClass": witness_class,
    }
