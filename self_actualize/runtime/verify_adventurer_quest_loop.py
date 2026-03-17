from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .derive_adventurer_quest_loop import (
    AGENT_STATE_PATH,
    CLAIM_TRACKER_PATH,
    CONDUCTOR_STATE_PATH,
    LOOP_STATE_PATH,
    MANIFEST_PATH,
    QUEST_REGISTRY_PATH,
    ROUND_TRIP_CERTIFICATES_PATH,
    STALE_SCAN_THRESHOLD,
    WAVE_CAPACITY,
    WAVE_ID,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "adventurer_quest_loop_verification.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_adventurer_quest_loop"
DERIVATION_VERSION = "2026-03-13.adventurer.64pow4.hybrid_conductor.round_trip.verify.v2"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"label": label, "status": "OK", "details": fn()}
    except Exception as exc:  # noqa: BLE001
        return {"label": label, "status": "FAIL", "details": str(exc)}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_registry() -> dict[str, Any]:
    payload = load_json(QUEST_REGISTRY_PATH)
    records = payload["quest_records"]
    ensure(records, "quest registry is empty")
    active_like = [record for record in records if record["status"] in {"OPEN", "ACTIVE", "SEEDED"}]
    addresses = [record["quest_address"] for record in active_like]
    ensure(len(addresses) == len(set(addresses)), "active-or-seeded quest addresses are not unique")
    q42 = next((record for record in records if record["quest_id"] == "Q42"), None)
    q46 = next((record for record in records if record["quest_id"] == "Q46"), None)
    seeded = [record for record in records if record.get("registration_kind") == "seeded"]
    ensure(q42 is not None and q42["status"] == "OPEN", "Q42 is not open")
    ensure(q46 is not None and q46["status"] == "OPEN", "Q46 is not open")
    ensure(len(seeded) == 2, "seeded registration count is not two")
    return {
        "quest_count": len(records),
        "active_unique_address_count": len(addresses),
        "seeded_ids": [record["quest_id"] for record in seeded],
    }


def verify_agent_state() -> dict[str, Any]:
    payload = load_json(AGENT_STATE_PATH)
    agents = payload["agents"]
    ensure(payload["wave_id"] == WAVE_ID, "agent state wave id drifted")
    ensure(payload["max_parallel_claims"] == WAVE_CAPACITY, "agent state wave capacity drifted")
    ensure(len(agents) == WAVE_CAPACITY, "floating agent count drifted")
    active_claims = [agent["active_claim"] for agent in agents if agent["active_claim"]]
    ensure(len(active_claims) <= WAVE_CAPACITY, "active claim count exceeds wave capacity")
    ensure("Q42" in active_claims, "Q42 is not assigned to an active floating agent")
    ensure("Q46" in active_claims, "Q46 is not assigned to an active floating agent")
    return {
        "agent_ids": [agent["agent_id"] for agent in agents],
        "active_claims": active_claims,
    }


def verify_loop_state() -> dict[str, Any]:
    payload = load_json(LOOP_STATE_PATH)
    ensure(payload["answer_space"] == 64**4, "answer space is not 64^4")
    ensure(payload["wave_id"] == WAVE_ID, "loop state wave id drifted")
    ensure(payload["wave_capacity"] == WAVE_CAPACITY, "loop state wave capacity drifted")
    ensure(payload["seeded_count"] == 2, "loop state seeded count drifted")
    ensure(payload["stale_release_after_inactive_cycles"] == STALE_SCAN_THRESHOLD, "stale release threshold drifted")
    return {
        "answer_space": payload["answer_space"],
        "open_count": payload["open_count"],
        "active_front_count": payload["active_front_count"],
        "seeded_count": payload["seeded_count"],
    }


def verify_conductor_state() -> dict[str, Any]:
    payload = load_json(CONDUCTOR_STATE_PATH)
    packets = payload["packets"]
    ensure(payload["wave_id"] == WAVE_ID, "conductor wave id drifted")
    ensure(payload["docs_gate_status"] == "BLOCKED", "conductor docs gate is not blocked")
    ensure(payload["max_parallel_claims"] == WAVE_CAPACITY, "conductor max parallel claims drifted")
    ensure(payload["round_trip_registry_path"].endswith("adventurer_round_trip_certificates.json"), "round-trip registry path missing")
    ensure(payload["round_trip_governed_fronts"] == ["Q42", "Q46", "TQ04"], "round-trip governed fronts drifted")
    ensure(7 <= len(packets) <= WAVE_CAPACITY, "conductor packet count is outside the current lawful range")
    ensure(packets[0]["source_front"] == "Q42", "Q42 is not the first packet")
    ensure(packets[1]["source_front"] == "Q46", "Q46 is not the second packet")
    packet_sources = [packet["source_front"] for packet in packets]
    ensure("ADV64-S01" in packet_sources, "ADV64-S01 is not in the seeded slice")
    ensure("ADV64-S02" in packet_sources, "ADV64-S02 is not in the seeded slice")
    for packet in packets:
        ensure(packet["max_parallel_claims"] == WAVE_CAPACITY, "packet max parallel claims drifted")
        ensure(packet["success_gate"]["requires_all"] == ["artifact_landed", "board_update_landed", "writeback_landed", "restart_seed"], "packet success gate contract drifted")
    q42_packet = next(packet for packet in packets if packet["source_front"] == "Q42")
    q46_packet = next(packet for packet in packets if packet["source_front"] == "Q46")
    ensure(q42_packet["round_trip_certificate_id"] == "RTC-v0-Q42", "Q42 packet missing round-trip certificate")
    ensure(q42_packet["round_trip_class"] == "law_equivalent", "Q42 packet round-trip class drifted")
    ensure(q46_packet["round_trip_certificate_id"] == "RTC-v0-Q46", "Q46 packet missing round-trip certificate")
    ensure(q46_packet["round_trip_class"] == "law_equivalent", "Q46 packet round-trip class drifted")
    return {
        "packet_ids": [packet["packet_id"] for packet in packets],
        "seeded_registration_ids": payload["seeded_registration_ids"],
    }


def verify_claim_tracker() -> dict[str, Any]:
    payload = load_json(CLAIM_TRACKER_PATH)
    claims = payload["claims"]
    active_claims = [claim for claim in claims.values() if claim["status"] == "active"]
    active_addresses = [claim["address"] for claim in active_claims]
    ensure(payload["wave_id"] == WAVE_ID, "claim tracker wave id drifted")
    ensure(payload["release_after_inactive_cycles"] == STALE_SCAN_THRESHOLD, "claim tracker stale threshold drifted")
    ensure(7 <= len(active_claims) <= WAVE_CAPACITY, "active claim count is outside the current lawful range")
    ensure(len(active_addresses) == len(set(active_addresses)), "active claim addresses are not unique")
    for claim in active_claims:
        ensure(bool(claim["stale_after"]), "claim stale_after missing")
        ensure(bool(claim["claimed_at"]), "claim claimed_at missing")
        ensure(bool(claim["receipt_pointer"]), "claim receipt_pointer missing")
    return {
        "active_claim_ids": [claim["claim_id"] for claim in active_claims],
        "active_frontiers": [claim["frontier"] for claim in active_claims],
    }


def verify_manifest() -> dict[str, Any]:
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    ensure("ADVENTURER 64^4 STATE" in text, "manifest title missing")
    ensure(WAVE_ID in text, "manifest missing wave id")
    ensure("Q42" in text and "Q46" in text, "manifest missing current hall fronts")
    ensure("ADV64-S01" in text and "ADV64-S02" in text, "manifest missing seeded registrations")
    ensure("Round trip: a conversion is valid only if it preserves law" in text, "manifest missing round-trip law")
    return {
        "manifest_path": str(MANIFEST_PATH),
        "contains_wave": True,
    }


def verify_round_trip_registry() -> dict[str, Any]:
    payload = load_json(ROUND_TRIP_CERTIFICATES_PATH)
    ensure(payload["docs_gate_status"] == "BLOCKED", "round-trip registry docs gate drifted")
    ensure(payload["required_route_min"] == ["AppA", "AppI", "AppM"], "required route minimum drifted")
    ensure(len(payload["transform_laws"]) == 5, "transform law count drifted")
    ensure(len(payload["illegal_loss_tests"]) == 7, "illegal loss test count drifted")
    ensure(payload["governed_fronts"] == ["Q42", "Q46", "TQ04"], "governed fronts drifted")
    certificates = {item["quest_id"]: item for item in payload["governed_certificates"]}
    ensure(certificates["Q42"]["round_trip_class"] == "law_equivalent", "Q42 round-trip certificate drifted")
    ensure(certificates["Q46"]["round_trip_class"] == "law_equivalent", "Q46 round-trip certificate drifted")
    ensure(certificates["TQ04"]["round_trip_class"] == "exact", "TQ04 round-trip certificate drifted")
    residual = next(item for item in payload["reference_examples"] if item["certificate_id"] == "RTC-v0-reference-residualized")
    illegal = next(item for item in payload["reference_examples"] if item["certificate_id"] == "RTC-v0-reference-illegal")
    ensure(residual["round_trip_class"] == "residualized", "residualized reference example drifted")
    ensure(illegal["round_trip_class"] == "illegal", "illegal reference example drifted")
    ensure("route_min_sigma_loss" in illegal["loss_findings"], "illegal reference lost sigma-loss linter")
    return {
        "registry_path": str(ROUND_TRIP_CERTIFICATES_PATH),
        "governed_fronts": payload["governed_fronts"],
    }


def verify_payload() -> dict[str, Any]:
    checks = [
        run_check("registry", verify_registry),
        run_check("agent_state", verify_agent_state),
        run_check("loop_state", verify_loop_state),
        run_check("conductor_state", verify_conductor_state),
        run_check("round_trip_registry", verify_round_trip_registry),
        run_check("claim_tracker", verify_claim_tracker),
        run_check("manifest", verify_manifest),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    truth = "OK" if not failed else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
    }


def main() -> int:
    payload = verify_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote adventurer verification json: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
