"""Contract tests for the KC144.XNAV.W14 memory digest capsule."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / ".athena" / "receipts" / "w14-memory-digest-capsule.json"
MOUNTS = ROOT / "MCP" / "data" / "w11_source_mounts.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_capsule_materializes_both_exact_seven_field_packets() -> None:
    capsule = _load(CAPSULE)
    body = capsule["memory_digest_capsule"]
    assert capsule["verdict"].startswith("PASS_EXPLICIT_DIGEST_CAPSULE_MATERIALIZED")
    assert body["object_count"] == 2
    assert body["exact_fields_per_object"] == 7
    assert body["exact_address_fields_materialized"] == 14
    assert body["possible_address_fields"] == 14
    assert body["explicit_address_coverage"] == 1.0
    assert body["assertion"] == "PASS_EXPLICIT_PACKET_MATERIALIZED_NOT_RECALLED"


def test_capsule_packets_equal_the_runtime_source_mounts() -> None:
    capsule = _load(CAPSULE)
    mounts = _load(MOUNTS)
    by_station = {item["station"]: item for item in capsule["memory_digest_capsule"]["objects"]}
    mounted = {item["station"]: item for item in mounts["mounts"]}

    assert set(by_station) == {"F07", "M09"}
    for station, packet in by_station.items():
        source_mount = mounted[station]
        source = source_mount["source"]
        assert packet["rid"] == source_mount["rid"]
        assert packet["file_id"] == source["file_id"]
        assert packet["drive_revision_id"] == source["revision_id"]
        assert packet["tab_id"] == source["tab_id"]
        assert packet["half_open_range"] == f'[{source["range"]["start"]},{source["range"]["end"]})'
        assert packet["literal"] == source["literal"]
        assert packet["full_sha256"] == source["literal_sha256"]
        assert packet["return_locator"] == source["return_locator"]


def test_capsule_does_not_rewrite_the_w13_measurement() -> None:
    capsule = _load(CAPSULE)
    prior = capsule["prior_memory_measurement"]
    future = capsule["future_uncued_reentry_gate"]

    assert prior["conversation_memory_exact_fields"] == 10
    assert prior["persisted_file_join_exact_fields"] == 12
    assert prior["possible_fields"] == 14
    assert prior["exact_full_packet_reconstruction_demonstrated"] is False
    assert future["state"] == "UNTESTED"
    assert future["same_turn_retest_forbidden"] is True
    assert future["explicit_capsule_presence_does_not_imply_recall"] is True


def test_endpoint_authority_remains_fail_closed() -> None:
    capsule = _load(CAPSULE)
    endpoint = capsule["endpoint_binding"]
    boundaries = capsule["boundaries"]

    assert endpoint["state"] == "HOLD_AUTHORITY_INPUTS_UNRESOLVED"
    assert endpoint["activation_packet"] == "UNRESOLVED"
    assert len(endpoint["unresolved_authority_inputs"]) == 13
    assert endpoint["witness_plan"] == {
        "samples": 3,
        "interval_seconds": 20,
        "minimum_span_seconds": 40,
        "execute_live_witness_default": False,
    }
    assert endpoint["endpoint_contacted"] is False
    assert endpoint["persistent_witness_executed"] is False
    assert all(boundaries.values())
