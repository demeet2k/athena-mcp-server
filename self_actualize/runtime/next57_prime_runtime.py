from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime.command_spine_adapter import CommandMembraneService
else:
    from .command_spine_adapter import CommandMembraneService

ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / "self_actualize"
MANIFEST_ROOT = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
RECEIPTS_ROOT = SELF_ROOT / "mycelium_brain" / "receipts"

PROGRAM_JSON = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_PROGRAM.json"
CYCLE_JSON = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
PACKETS_JSON = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"

STATE_PATH = SELF_ROOT / "next57_four_agent_corpus_cycle_state.json"
MASTER_LOOP_STATE_PATH = SELF_ROOT / "master_loop_state_57.json"
SEAT_REGISTRY_PATH = SELF_ROOT / "next57_four_agent_nested_seat_registry.json"
QUEST_PACKET_PATH = SELF_ROOT / "next57_four_agent_quest_packets.json"
AWAKENING_NOTES_PATH = SELF_ROOT / "next57_four_agent_awakening_assist_notes.json"
VERIFY_PATH = SELF_ROOT / "next57_four_agent_corpus_cycle_verification.json"
COMPAT_PATH = SELF_ROOT / "next57_compatibility_mirror_registry.json"
PRIME_PROTOCOL_PATH = SELF_ROOT / "next57_prime_loop_protocol.json"
LOOP_CATALOG_PATH = SELF_ROOT / "next57_loop_catalog_57.json"
COORDINATE_REGISTRY_PATH = SELF_ROOT / "next57_liminal_coordinate_registry.json"
LEDGER_SCHEMA_PATH = SELF_ROOT / "next57_agent_ledger_schema.json"
HALL_TREE_PATH = SELF_ROOT / "next57_guild_hall_quest_tree.json"
TEMPLE_TREE_PATH = SELF_ROOT / "next57_temple_quest_tree.json"
COMMAND_PROTOCOL_PATH = SELF_ROOT / "next57_command_protocol.json"
COMMAND_PACKET_SCHEMA_PATH = SELF_ROOT / "next57_command_event_packet_schema.json"
COMMAND_CAPILLARY_LAW_PATH = SELF_ROOT / "next57_command_capillary_law.json"
COMMAND_LATENCY_PATH = SELF_ROOT / "next57_command_latency_benchmarks.json"

COMPAT_MD_PATH = MANIFEST_ROOT / "NEXT_57_LOOP_COMPATIBILITY_MIRRORS.md"
PRIME_PROTOCOL_MD_PATH = MANIFEST_ROOT / "NEXT_57_LOOP_PRIME_PROTOCOL.md"
CORPUS_CYCLE_MD_PATH = MANIFEST_ROOT / "NEXT_57_LOOP_FOUR_AGENT_CORPUS_CYCLE.md"
RECEIPT_MD_PATH = RECEIPTS_ROOT / "2026-03-13_next57_compatibility_mirror_refresh.md"

LEDGER_FIELDS = [
    "agent_id",
    "loop_number",
    "parent_agent",
    "coordinate_stamp",
    "source_region",
    "action_type",
    "affected_nodes",
    "summary_of_change",
    "reason_for_change",
    "integration_gain",
    "compression_gain",
    "unresolved_followups",
    "linked_quests",
    "linked_agents",
    "revision_confidence",
    "timestamp_internal",
]
COORDINATE_SCHEMA = {
    "Xs": "document region",
    "Ys": "corpus sector",
    "Zs": "recursion depth",
    "Ts": "temporal revision layer",
    "Qs": "quest state",
    "Rs": "routing rail",
    "Cs": "compression state",
    "Fs": "framework lens",
    "Ms": "mathematical density",
    "Ns": "neural or mycelial connectivity",
    "Hs": "hierarchy level",
    "OmegaS": "zero-point or aether relation",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ensure_canonical() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return read_json(PROGRAM_JSON), read_json(CYCLE_JSON), read_json(PACKETS_JSON)


def ensure_command_artifacts() -> dict[str, Path]:
    service = CommandMembraneService()
    artifacts = service.ensure_protocol_artifacts()
    return {key: Path(value) for key, value in artifacts.items()}


def read_master_loop_state() -> dict[str, Any]:
    return read_json(MASTER_LOOP_STATE_PATH) if MASTER_LOOP_STATE_PATH.exists() else {}


def canonical_loop_packet_bundle(master_state: dict[str, Any], fallback_packets: dict[str, Any]) -> dict[str, Any]:
    completed_loop_label = str(master_state.get("completed_loop", {}).get("label", "")).strip()
    completed_loop_id = completed_loop_label.split(" ", 1)[0] if completed_loop_label else ""
    if completed_loop_id:
        packet_path = SELF_ROOT / "lp57_omega_v2_artifacts" / completed_loop_id / "quest_emission_bundle.json"
        if packet_path.exists():
            payload = read_json(packet_path)
            payload.setdefault("quest_emission_mode", "quota-safe")
            payload.setdefault(
                "public_board_caps",
                (master_state.get("shared_lattice", {}) or {}).get(
                    "planner_public_caps",
                    {"hall": 8, "temple": 8, "ap6d_shadow": 16, "adventurer_packets": 16},
                ),
            )
            return payload
    return fallback_packets


def normalize_docs_gate(value: Any) -> dict[str, Any]:
    if isinstance(value, dict) and value:
        state = str(value.get("state") or value.get("docs_gate_status") or "BLOCKED")
        return {
            "state": state,
            "reason": str(value.get("reason") or value.get("detail") or ("blocked-by-missing-credentials" if state == "BLOCKED" else "open")),
            "checked_paths": value.get("checked_paths", []),
        }
    if isinstance(value, str) and value:
        return {
            "state": value,
            "reason": "blocked-by-missing-credentials" if value == "BLOCKED" else "open",
            "checked_paths": [],
        }
    return {"state": "BLOCKED", "reason": "blocked-by-missing-credentials", "checked_paths": []}


def parse_loop_label(value: str) -> tuple[str, str]:
    text = (value or "").strip()
    if not text:
        return "", ""
    if "->" in text:
        left, right = [part.strip() for part in text.split("->", 1)]
        return left, right
    parts = text.split(" ", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")


def mirror_base(program: dict[str, Any]) -> dict[str, Any]:
    command_artifacts = ensure_command_artifacts()
    master_state = read_master_loop_state()
    cycle_summary = program.get("current_cycle_summary", {})
    completed_loop_meta = master_state.get("completed_loop", {})
    active_loop_meta = master_state.get("active_loop", {})
    completed_loop_id = str(completed_loop_meta.get("label", "")).split(" ", 1)[0] or parse_loop_label(cycle_summary.get("completed_loop", ""))[0]
    completed_loop_title = str(completed_loop_meta.get("label", "")).split(" ", 1)[1] if " " in str(completed_loop_meta.get("label", "")) else parse_loop_label(cycle_summary.get("completed_loop", ""))[1]
    active_loop_id = str(active_loop_meta.get("label", "")).split(" ", 1)[0] or parse_loop_label(cycle_summary.get("active_loop", ""))[0]
    active_loop_title = str(active_loop_meta.get("label", "")).split(" ", 1)[1] if " " in str(active_loop_meta.get("label", "")) else parse_loop_label(cycle_summary.get("active_loop", ""))[1]
    restart_seed_id, restart_seed_title = parse_loop_label(cycle_summary.get("restart_seed", ""))
    docs_gate_state = normalize_docs_gate(master_state.get("docs_gate") or program.get("docs_gate") or program.get("seeded_next_packets", {}).get("docs_gate_status"))
    active_membrane = str(master_state.get("active_membrane") or program.get("active_membrane", ""))
    feeder_stack = master_state.get("feeder_stack") or program.get("feeder_stack", [])
    return {
        "generated_at": utc_now(),
        "protocol_id": str(master_state.get("protocol_id") or program["protocol_id"]),
        "status": "COMPATIBILITY_MIRROR",
        "canonical_manifest_triplet": [rel(PROGRAM_JSON), rel(CYCLE_JSON), rel(PACKETS_JSON)],
        "canonical_master_state": rel(MASTER_LOOP_STATE_PATH),
        "live_macro_membrane": active_membrane,
        "current_loop_id": completed_loop_id,
        "current_loop_title": completed_loop_title,
        "current_loop_completion_state": "COMPLETED",
        "next_loop_id": active_loop_id or restart_seed_id,
        "next_loop_title": active_loop_title or restart_seed_title,
        "next_loop_state": str(active_loop_meta.get("state") or ("ACTIVE" if active_loop_id else "SEEDED_ONLY")),
        "helix_state": str(master_state.get("current_loop_state") or program.get("active_stage_law", "")),
        "docs_gate_state": docs_gate_state,
        "feeder_stack": feeder_stack,
        "command_protocol_mode": "sensory-membrane-v1",
        "command_artifacts": {key: rel(Path(value)) for key, value in command_artifacts.items()},
        "compatibility_aliases": {"Q51": "historical_hall_alias_only"},
        "warning": "next57 is a compatibility mirror only. It may not claim live authority, independent restart seeds, or separate seat law.",
    }


def normalized_shared_seat_law(master_state: dict[str, Any], program: dict[str, Any]) -> dict[str, Any]:
    shared = master_state.get("shared_lattice") or program.get("shared_lattice") or {}
    total = int(shared.get("total_seats") or shared.get("indexed") or shared.get("logical_namespace_total_per_master") or 4096)
    active = int(
        shared.get("active_seats")
        or shared.get("active")
        or (int(shared.get("active_seats_per_master", 256)) * 4)
        or 1024
    )
    dormant = int(shared.get("dormant_seats") or shared.get("dormant") or max(total - active, 0))
    return {
        "model": shared.get("model", "role-namespaced-4096-over-shared-4096"),
        "indexed": total,
        "active": active,
        "dormant": dormant,
        "logical_namespace_total_per_master": int(shared.get("logical_namespace_total_per_master") or total),
        "active_seats_per_master": int(shared.get("active_seats_per_master") or max(active // 4, 1)),
        "planner_public_caps": shared.get(
            "planner_public_caps",
            {"hall": 8, "temple": 8, "ap6d_shadow": 16, "adventurer_packets": 16},
        ),
    }


def write_mirrors() -> dict[str, Any]:
    program, cycle, packets = ensure_canonical()
    base = mirror_base(program)
    master_state = read_master_loop_state()
    canonical_packets = canonical_loop_packet_bundle(master_state, packets)
    state_payload = base | {"mirror_family": "next57", "source_role": "state"}
    seat_payload = base | {
        "mirror_family": "next57",
        "source_role": "seat_registry",
        "shared_seat_law": normalized_shared_seat_law(master_state, program),
    }
    packet_payload = base | {
        "mirror_family": "next57",
        "source_role": "quest_packets",
        "hall_promotions": canonical_packets.get("hall_promotions", []),
        "temple_promotions": canonical_packets.get("temple_promotions", []),
        "ap6d_shadow_packets": canonical_packets.get("ap6d_shadow_packets", []),
        "adventurer_packets": canonical_packets.get("adventurer_packets", []),
        "quest_emission_mode": canonical_packets.get("quest_emission_mode", "quota-safe"),
        "public_board_caps": canonical_packets.get(
            "public_board_caps",
            normalized_shared_seat_law(master_state, program).get("planner_public_caps", {}),
        ),
    }
    protocol_payload = base | {
        "mirror_family": "next57",
        "source_role": "prime_protocol",
        "mirror_law": "derived_only",
        "command_reward_model": "compatibility-only-support-surface",
        "seed_polarity_support": ["A", "B", "A↔B"],
        "forbidden_claims": [
            "LIVE_AUTHORITY",
            "independent restart seed",
            "separate seat law",
            "Q51 as current hall membrane",
        ],
    }
    registry_payload = base | {
        "mirror_family": "next57",
        "source_role": "mirror_registry",
        "mirrors": [
            rel(STATE_PATH),
            rel(SEAT_REGISTRY_PATH),
            rel(QUEST_PACKET_PATH),
            rel(PRIME_PROTOCOL_PATH),
            rel(LOOP_CATALOG_PATH),
            rel(COORDINATE_REGISTRY_PATH),
            rel(LEDGER_SCHEMA_PATH),
            rel(HALL_TREE_PATH),
            rel(TEMPLE_TREE_PATH),
            rel(COMMAND_PROTOCOL_PATH),
            rel(COMMAND_PACKET_SCHEMA_PATH),
            rel(COMMAND_CAPILLARY_LAW_PATH),
            rel(COMMAND_LATENCY_PATH),
        ],
    }
    awakening_payload = base | {
        "mirror_family": "next57",
        "source_role": "awakening_assist_notes",
        "preserved_front_truth": program.get("feeder_stack", []),
    }
    loop_catalog_payload = base | {
        "mirror_family": "next57",
        "source_role": "loop_catalog",
        "loops": cycle.get("loops", cycle.get("rows", [])),
    }
    coordinate_payload = base | {
        "mirror_family": "next57",
        "source_role": "coordinate_registry",
        "coordinate_schema": COORDINATE_SCHEMA,
    }
    ledger_payload = base | {
        "mirror_family": "next57",
        "source_role": "ledger_schema",
        "fields": LEDGER_FIELDS,
    }
    hall_tree_payload = base | {
        "mirror_family": "next57",
        "source_role": "hall_tree",
        "macro": packets.get("hall_promotions", []),
    }
    temple_tree_payload = base | {
        "mirror_family": "next57",
        "source_role": "temple_tree",
        "macro": packets.get("temple_promotions", []),
    }

    write_json(STATE_PATH, state_payload)
    write_json(SEAT_REGISTRY_PATH, seat_payload)
    write_json(QUEST_PACKET_PATH, packet_payload)
    write_json(PRIME_PROTOCOL_PATH, protocol_payload)
    write_json(COMPAT_PATH, registry_payload)
    write_json(AWAKENING_NOTES_PATH, awakening_payload)
    write_json(LOOP_CATALOG_PATH, loop_catalog_payload)
    write_json(COORDINATE_REGISTRY_PATH, coordinate_payload)
    write_json(LEDGER_SCHEMA_PATH, ledger_payload)
    write_json(HALL_TREE_PATH, hall_tree_payload)
    write_json(TEMPLE_TREE_PATH, temple_tree_payload)

    write_text(COMPAT_MD_PATH, "\n".join([
        "# NEXT57 Compatibility Mirrors",
        "",
        "- Status: `COMPATIBILITY_MIRROR`",
        f"- Canonical machine truth: `{rel(PROGRAM_JSON)}`, `{rel(CYCLE_JSON)}`, `{rel(PACKETS_JSON)}`",
        f"- Live macro membrane: `{base['live_macro_membrane']}`",
        "- `Q51` is retained only as historical Hall alias.",
        "- `next57_*` files are preserved only as compatibility mirrors.",
        "- No mirror may claim `LIVE_AUTHORITY` or independent restart seeds.",
    ]))
    write_text(PRIME_PROTOCOL_MD_PATH, "\n".join([
        "# NEXT57 Prime Loop Protocol",
        "",
        "This file is a compatibility mirror.",
        f"- Canonical machine truth: `{rel(PROGRAM_JSON)}`, `{rel(CYCLE_JSON)}`, `{rel(PACKETS_JSON)}`",
        f"- Current loop: `{base['current_loop_id']} {base['current_loop_title']} [{base['current_loop_completion_state']}]`",
        f"- Seeded next loop: `{base['next_loop_id']} {base['next_loop_title']} [{base['next_loop_state']}]`",
        f"- Live macro membrane: `{base['live_macro_membrane']}`",
        "- Treat next57 outputs as reverse-lookup compatibility only.",
    ]))
    write_text(CORPUS_CYCLE_MD_PATH, "\n".join([
        "# NEXT57 Four-Agent Corpus Cycle",
        "",
        "Compatibility mirror only.",
        f"- Canonical machine truth: `{rel(PROGRAM_JSON)}`, `{rel(CYCLE_JSON)}`, `{rel(PACKETS_JSON)}`",
        f"- Live macro membrane: `{base['live_macro_membrane']}`",
        f"- Docs gate: `{base['docs_gate_state']['state']}`",
        f"- Current loop: `{base['current_loop_id']} {base['current_loop_title']} [{base['current_loop_completion_state']}]`",
    ]))
    write_text(RECEIPT_MD_PATH, "\n".join([
        "# NEXT57 Compatibility Mirror Refresh",
        "",
        f"- Generated at: `{base['generated_at']}`",
        f"- Canonical machine truth: `{rel(PROGRAM_JSON)}`, `{rel(CYCLE_JSON)}`, `{rel(PACKETS_JSON)}`",
        f"- Live macro membrane: `{base['live_macro_membrane']}`",
        "- `Q51` remains historical compatibility only.",
        "- `next57_*` remains derived and non-authoritative.",
    ]))
    return {"state": state_payload, "registry": registry_payload, "protocol": protocol_payload}


def verify_mirrors() -> dict[str, Any]:
    program, cycle, packets = ensure_canonical()
    master_state = read_master_loop_state()
    canonical_packets = canonical_loop_packet_bundle(master_state, packets)
    command_artifacts = ensure_command_artifacts()
    state = read_json(STATE_PATH)
    protocol = read_json(PRIME_PROTOCOL_PATH)
    registry = read_json(COMPAT_PATH)
    seat = read_json(SEAT_REGISTRY_PATH)
    packet_payload = read_json(QUEST_PACKET_PATH)
    hall_ids = [row.get("quest_id", "") for row in packet_payload.get("hall_promotions", [])]
    temple_ids = [row.get("quest_id", "") for row in packet_payload.get("temple_promotions", [])]
    completed_loop_id = str(master_state.get("completed_loop", {}).get("label", "")).split(" ", 1)[0] or state.get("current_loop_id", "")
    active_loop_id = str(master_state.get("active_loop", {}).get("label", "")).split(" ", 1)[0] or state.get("next_loop_id", "")
    expected_seat_law = normalized_shared_seat_law(master_state, program)
    expected_feeder_stack = list(master_state.get("feeder_stack") or ["Q42", "TQ04", "Q46", "Q02"])
    checks = {
        "status_mirror_only": state["status"] == "COMPATIBILITY_MIRROR" and protocol["status"] == "COMPATIBILITY_MIRROR",
        "live_membrane_q41_tq06": state["live_macro_membrane"] == (master_state.get("active_membrane") or program.get("active_membrane", "")),
        "current_loop_matches_master": state["current_loop_id"] == completed_loop_id,
        "completed_loop_state": state["current_loop_completion_state"] == "COMPLETED",
        "next_loop_matches_master": state["next_loop_id"] == active_loop_id and state["next_loop_state"] == str(master_state.get("active_loop", {}).get("state", "READY")),
        "q51_historical_only": state["compatibility_aliases"]["Q51"] == "historical_hall_alias_only",
        "no_live_authority_claim": protocol["mirror_law"] == "derived_only",
        "seat_law_shared": seat.get("shared_seat_law") == expected_seat_law,
        "canonical_triplet_points_home": registry["canonical_manifest_triplet"] == [rel(PROGRAM_JSON), rel(CYCLE_JSON), rel(PACKETS_JSON)],
        "docs_gate_matches_canonical": state["docs_gate_state"]["state"] == normalize_docs_gate(master_state.get("docs_gate") or program.get("docs_gate"))["state"] == "BLOCKED",
        "loop_catalog_57": len(read_json(LOOP_CATALOG_PATH)["loops"]) == len(cycle.get("loops", cycle.get("rows", []))) == 57,
        "hall_packet_ids_normalized": len(hall_ids) == 8 and all(item.startswith(f"Q57-{completed_loop_id}-H") for item in hall_ids),
        "temple_packet_ids_normalized": len(temple_ids) == 8 and all(item.startswith(f"TQ57-{completed_loop_id}-T") for item in temple_ids),
        "quest_emission_mode_quota_safe": packet_payload.get("quest_emission_mode") == canonical_packets.get("quest_emission_mode") == "quota-safe",
        "public_caps_preserved": packet_payload.get("public_board_caps", {}).get("hall") == canonical_packets.get("public_board_caps", {}).get("hall") == 8 and packet_payload.get("public_board_caps", {}).get("temple") == canonical_packets.get("public_board_caps", {}).get("temple") == 8,
        "feeder_stack_matches_master": state.get("feeder_stack") == expected_feeder_stack,
        "command_docs_gate_blocked": (
            read_json(Path(command_artifacts["protocol"])).get("docs_gate_status") == "BLOCKED"
            or read_json(Path(command_artifacts["protocol"])).get("docs_gate", {}).get("state") == "BLOCKED"
        ),
        "command_capillary_law_present": Path(command_artifacts["capillary"]).exists(),
        "command_latency_present": Path(command_artifacts["latency"]).exists(),
    }
    result = {
        "generated_at": utc_now(),
        "protocol_id": program["protocol_id"],
        "truth": "OK" if all(checks.values()) else "FAIL",
        "checks": checks,
    }
    write_json(VERIFY_PATH, result)
    return result


def main() -> int:
    mirror_result = write_mirrors()
    command_result = {key: rel(path) for key, path in ensure_command_artifacts().items()}
    payload = {
        "generated_at": utc_now(),
        "mirror": mirror_result,
        "command_membrane": command_result,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    return 0


def verify_main() -> int:
    result = verify_mirrors()
    print(json.dumps(result, indent=2, ensure_ascii=True, default=str))
    return 0 if result.get("truth") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
