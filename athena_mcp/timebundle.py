from __future__ import annotations
from datetime import datetime, timezone, timedelta
import math, time

# Verified for 2026-08-07 from IERS Bulletin C 72 (published 2026-07-06): UTC-TAI = -37 s.
TAI_MINUS_UTC = 37
TT_MINUS_TAI = 32.184
TIME_PROVENANCE = {
    "authority": "IERS Earth Orientation Centre",
    "bulletin": "Bulletin C 72",
    "published": "2026-07-06",
    "utc_minus_tai_seconds": -37,
    "validity": "2017-01-01T00:00:00Z until further notice",
}

def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="microseconds").replace("+00:00", "Z")

def julian_date(dt: datetime) -> float:
    """UTC-like Julian Date from a timezone-aware datetime."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    y, m = dt.year, dt.month
    day = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond/1e6)/60)/60)/24
    if m <= 2:
        y -= 1; m += 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25*(y+4716)) + math.floor(30.6001*(m+1)) + day + b - 1524.5

def bundle(*, logical_clock: int | None = None, liminal: dict | None = None, ephemeris: dict | None = None, now: datetime | None = None) -> dict:
    utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    tai = utc + timedelta(seconds=TAI_MINUS_UTC)
    tt = tai + timedelta(seconds=TT_MINUS_TAI)
    unix_ns = time.time_ns() if now is None else int(utc.timestamp()*1_000_000_000)
    return {
        "UTC": _iso(utc),
        "UNIX_NS": unix_ns,
        "TAI": _iso(tai),
        "TT": _iso(tt),
        "TAI_MINUS_UTC_S": TAI_MINUS_UTC,
        "TT_MINUS_TAI_S": TT_MINUS_TAI,
        "JULIAN_DATE_UTC": julian_date(utc),
        "LOGICAL": logical_clock,
        "LIMINAL": liminal or {"status": "UNKNOWN"},
        "ASTRO_EPHEMERIS": ephemeris or {"status": "UNKNOWN", "note": "No ephemeris solution supplied; symbolic/astronomical layer is not fabricated."},
        "PROVENANCE": TIME_PROVENANCE,
    }
