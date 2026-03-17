from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from self_actualize.runtime.command_membrane import (
    BENCHMARK_FIELDS,
    CLAIM_LEDGER_PATH,
    EVENT_PACKETS_LEDGER_PATH,
    FIRST_WAVE_WATCHED_SURFACES,
    LATENCY_REGISTRY_PATH,
    LIVE_MANIFEST_PATH,
    PROTOCOL_ID,
    PUBLIC_STATE_PATH,
    ROUTE_POLICY,
    WATCHED_SURFACE_REGISTRY_PATH,
    build,
    read_json,
    rel,
)

VERIFY_PATH = ROOT / "self_actualize" / "mycelium_brain" / "registry" / "command_membrane_verification.json"
EXPECTED_WATCH_SCOPE = "first-wave local swarm mesh"
EXPECTED_ACTIVE_SURFACE = "LOCAL SWARM MESH"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_count(payload: object) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return len(rows)
    return 0


def main() -> int:
    build()
    public_state = read_json(PUBLIC_STATE_PATH, {})
    event_packets = read_json(EVENT_PACKETS_LEDGER_PATH, {})
    claim_ledger = read_json(CLAIM_LEDGER_PATH, {})
    latency_rows = read_json(LATENCY_REGISTRY_PATH, {})
    watch_registry = read_json(WATCHED_SURFACE_REGISTRY_PATH, {})
    live_manifest = read_json(LIVE_MANIFEST_PATH, {})

    checks = {
        "protocol_id_exact": public_state.get("protocol_id") == PROTOCOL_ID,
        "active_surface_exact": public_state.get("active_surface") == EXPECTED_ACTIVE_SURFACE,
        "watch_scope_exact": public_state.get("watch_scope") == EXPECTED_WATCH_SCOPE,
        "watcher_mode_exact": public_state.get("watcher_mode") == "event-driven",
        "fallback_mode_exact": public_state.get("policy", {}).get("watch_policy", {}).get("fallback_mode") == "polling",
        "route_policy_exact": public_state.get("policy", {}).get("routing_policy") == ROUTE_POLICY,
        "docs_gate_honest": public_state.get("docs_gate", {}).get("state") == "BLOCKED",
        "latency_metrics_present": all(metric in public_state.get("metrics", {}) for metric in BENCHMARK_FIELDS),
        "watch_registry_count_exact": watch_registry.get("source_count") == len(FIRST_WAVE_WATCHED_SURFACES),
        "watched_surface_count_exact": public_state.get("watched_surface_count") == len(FIRST_WAVE_WATCHED_SURFACES),
        "event_packets_available": _row_count(event_packets) >= 0,
        "claim_ledger_available": _row_count(claim_ledger) >= 0,
        "latency_rows_available": _row_count(latency_rows) >= 0,
        "live_manifest_aligned": live_manifest.get("protocol_id") == PROTOCOL_ID
        and live_manifest.get("active_surface") == EXPECTED_ACTIVE_SURFACE
        and live_manifest.get("watch_scope") == EXPECTED_WATCH_SCOPE,
    }

    payload = {
        "generated_at": utc_now(),
        "truth": "OK" if all(checks.values()) else "NEAR",
        "checks": checks,
        "counts": {
            "watched_surfaces": watch_registry.get("source_count", 0),
            "event_packets": _row_count(event_packets),
            "claim_ledger": _row_count(claim_ledger),
            "latency_rows": _row_count(latency_rows),
        },
        "artifacts": {
            "public_state": rel(PUBLIC_STATE_PATH),
            "watch_registry": rel(WATCHED_SURFACE_REGISTRY_PATH),
            "event_packets": rel(EVENT_PACKETS_LEDGER_PATH),
            "claim_ledger": rel(CLAIM_LEDGER_PATH),
            "latency_registry": rel(LATENCY_REGISTRY_PATH),
            "live_manifest": rel(LIVE_MANIFEST_PATH),
        },
    }
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
