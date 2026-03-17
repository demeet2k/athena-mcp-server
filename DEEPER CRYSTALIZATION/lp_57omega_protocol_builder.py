#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from canonical_manuscript_builder import build_manuscript_volumes
from lp_57omega_protocol import (
    BASE3_ANTISPIN_LOCK,
    COORDINATE_DIMENSIONS,
    ENTITY_STATES,
    LAYER_FOLDER,
    LEDGER_FIELDS,
    MASTER_AGENT_SPECS,
    ROTATION_CARRIERS,
    PROTOCOL_DISPLAY_NAME,
    PROTOCOL_ID,
    RUNTIME_MANIFEST_NAME,
    SHELL_TRUTH,
    SIGMA_PATH,
    TARGET_AXIS,
)
from nervous_system_core import utc_now, write_json, write_text
from self_actualize.runtime.hemisphere_dense_65_shell_support import build_dense_65_canonical_payloads

ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
LAYER_ROOT = ACTIVE_ROOT / LAYER_FOLDER

SUPER_CYCLE_MANIFEST_PATH = RUNTIME_ROOT / "18_super_cycle_57_manifest.json"
RUNNER_MANIFEST_PATH = RUNTIME_ROOT / "19_super_cycle_57_runner_manifest.json"
CORPUS_MANIFEST_PATH = RUNTIME_ROOT / "17_corpus_wide_integration_manifest.json"
MOTION_MANIFEST_PATH = RUNTIME_ROOT / "16_motion_constitution_manifest.json"
FULL_STACK_MANIFEST_PATH = RUNTIME_ROOT / "12_full_stack_manifest.json"
ACTIVE_README_PATH = ACTIVE_ROOT / "README.md"
LIVE_DOCS_RECEIPT_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
LOOP_LEDGER_PATH = ACTIVE_ROOT / "17_SUPER_CYCLE_57" / "02_LOOP_LEDGER.json"

QUEST_BOARD_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_RUN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "BUILD_QUEUE.md"
HSIGMA_MACHINE_CORE_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "H_SIGMA_MACHINE_CORE.json"
HSIGMA_CYCLE_REGISTRY_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
HSIGMA_PROGRAM_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "FOUR_AGENT_57_LOOP_PROGRAM.json"
HSIGMA_QUEST_PACKETS_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"
MASTER_LOOP_STATE_57_PATH = WORKSPACE_ROOT / "self_actualize" / "master_loop_state_57.json"
HSIGMA_RECONCILIATION_RECEIPT_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "receipts"
    / "2026-03-13_lp57omega_hsigma_l02_seed_reconciliation.md"
)

LEGACY_CYCLE_RECORDS_PATH = WORKSPACE_ROOT / "self_actualize" / "lp_57_prime_loop_cycle_records.json"
LEGACY_LEDGER_PATH = WORKSPACE_ROOT / "self_actualize" / "lp_57_master_agent_ledger.json"
LEGACY_COORDS_PATH = WORKSPACE_ROOT / "self_actualize" / "lp_57_liminal_coordinate_stamps.json"
LEGACY_PROTOCOL_MARKDOWN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"

SELF_PROTOCOL_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_lp_57omega_program_state.json"
SELF_PROTOCOL_CATALOG_PATH = WORKSPACE_ROOT / "self_actualize" / "lp_57_prime_loop_cycle_records.json"

OUTPUT_MANIFEST_PATH = RUNTIME_ROOT / RUNTIME_MANIFEST_NAME

README_PATH = LAYER_ROOT / "README.md"
EXEC_OVERVIEW_MD = LAYER_ROOT / "00_EXECUTIVE_OVERVIEW.md"
MASTER_FRAMEWORK_MD = LAYER_ROOT / "01_MASTER_LOOP_FRAMEWORK.md"
COORDINATE_STANDARD_MD = LAYER_ROOT / "02_LIMINAL_IDENTITY_AND_COORDINATE_STANDARD.md"
LEDGER_STANDARD_MD = LAYER_ROOT / "03_AGENT_LEDGER_STANDARD.md"
LOOP_PLAN_MD = LAYER_ROOT / "04_57_LOOP_PLAN.md"
FINAL_SYNTHESIS_MD = LAYER_ROOT / "05_FINAL_SYNTHESIS.md"
COORDINATE_SCHEMA_JSON = LAYER_ROOT / "06_LIMINAL_COORDINATE_SCHEMA.json"
LEDGER_SCHEMA_JSON = LAYER_ROOT / "07_AGENT_LEDGER_SCHEMA.json"
NESTED_LATTICE_JSON = LAYER_ROOT / "08_NESTED_SUBAGENT_LATTICE.json"
LOOP_CATALOG_JSON = LAYER_ROOT / "09_LOOP_CATALOG.json"
PROTOCOL_STATE_JSON = LAYER_ROOT / "10_PROTOCOL_STATE.json"
COMPATIBILITY_WITNESSES_JSON = LAYER_ROOT / "11_COMPATIBILITY_WITNESSES.json"
SHELL_SPEC_MD = LAYER_ROOT / "12_dense_65_shell_spec.md"
SHELL_REGISTRY_JSON = LAYER_ROOT / "13_dense_65_shell_registry.json"
TRANSFER_WITNESS_JSON = LAYER_ROOT / "14_rqt_transfer_signature_registry.json"
TRANSFER_WITNESS_MD = LAYER_ROOT / "15_rqt_transfer_signature_and_metro_witness.md"
AETHER_POINTER_REGISTRY_JSON = LAYER_ROOT / "16_aether_witness_replay_pointer_registry.json"
AETHER_POINTER_WITNESS_MD = LAYER_ROOT / "17_aether_witness_replay_pointer_witness.md"
AETHER_POINTER_SCHEMA_JSON = LAYER_ROOT / "18_aether_witness_replay_pointer_schema.json"

MANUSCRIPT_MANIFEST_PATH = PROJECT_ROOT / "canonical_manuscript_manifest.json"
MANUSCRIPT_SECTIONS_DIR = WORKSPACE_ROOT / "self_actualize" / "manuscript_sections"
SHELL_SUPPLEMENT_PATH = MANUSCRIPT_SECTIONS_DIR / "025_lp_57omega_dense_65_shell.md"
TRANSFER_SUPPLEMENT_PATH = MANUSCRIPT_SECTIONS_DIR / "026_lp_57omega_rqt_transfer_signature_and_metro_witness_registry.md"

FLEET_B_PRIME_COMPAT_PATH = WORKSPACE_ROOT / "Athena FLEET" / "FLEET_MYCELIUM_NETWORK" / "HEMISPHERES" / "91_lp57omega_b_prime_witnessed_inversion_shell.md"
SELF_B_PRIME_COMPAT_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "hemispheres" / "91_lp57omega_b_prime_witnessed_inversion_shell.md"

VISIBLE_PROMOTION_LAW = {
    "hall": 1,
    "temple": 1,
    "runtime": 1,
    "compression": 1,
}

POINTER_LAYER_CLASSIFICATION = {
    "dense_shell_role": "L01-closed substrate enhancement",
    "packet_truth_sync_role": "L02 Packet Truth Sync input witness",
}

HSIGMA_AUTHORITY_CHAIN = [
    "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
    "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
    "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the canonical LP-57Omega protocol layer.")
    parser.set_defaults(as_json=False)
    subparsers = parser.add_subparsers(dest="command")
    build_parser = subparsers.add_parser("build", help="Build the LP-57Omega protocol layer.")
    build_parser.add_argument("--json", action="store_true", dest="as_json")
    parser.set_defaults(command="build")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        try:
            return str(path.resolve().relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())


def live_docs_error() -> str:
    if not LIVE_DOCS_RECEIPT_PATH.exists():
        return "Error: Missing OAuth client file: credentials.json"
    for line in LIVE_DOCS_RECEIPT_PATH.read_text(encoding="utf-8").splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Google Docs gate blocked."


def raw_dense_65_payloads() -> dict[str, Any]:
    return build_dense_65_canonical_payloads("BLOCKED")


def dense_65_canonical_payloads() -> dict[str, Any]:
    return raw_dense_65_payloads()


def dense_65_transfer_index(transfer_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["record_id"]: record for record in transfer_registry["records"]}


def dense_65_counts(
    shell_registry: dict[str, Any],
    transfer_registry: dict[str, Any],
    pointer_registry: dict[str, Any] | None = None,
) -> dict[str, int]:
    counts = dict(shell_registry["group_counts"])
    counts["total"] = sum(counts.values())
    counts["active_dense"] = counts["total"] - counts["H"]
    counts["enriched_transfer"] = transfer_registry["enriched_transfer_record_count"]
    counts["phase_bindings"] = sum(
        len(record["orientation_bindings"]) for record in transfer_registry["records"]
    )
    counts["concrete_pointers"] = transfer_registry.get(
        "concrete_pointer_count",
        pointer_registry.get("concrete_pointer_count", 0) if pointer_registry else 0,
    )
    return counts


def shell_registry_payload() -> dict[str, Any]:
    return dense_65_canonical_payloads()["shell_registry"]


def transfer_registry_payload() -> dict[str, Any]:
    return dense_65_canonical_payloads()["transfer_registry"]


def shell_counts() -> dict[str, int]:
    return dense_65_counts(shell_registry_payload(), transfer_registry_payload())


ENRICHED_TRANSFER_RECORDS = transfer_registry_payload()["records"]


def render_dense_block(shell_registry: dict[str, Any], transfer_registry: dict[str, Any]) -> str:
    transfer_index = dense_65_transfer_index(transfer_registry)
    lines = ["1/65) H00 | prior_seed_header_shell | status=reserved | truth=NEAR-derived"]
    for row in shell_registry["rows"]:
        cell_id = row["cell_id"]
        if row["cell_family"] == "H":
            continue
        if row["cell_family"] == "P":
            lines.append(
                f"{row['shell_position']}) {cell_id} | {row['pole']}={row['label']} | "
                f"theta={row['theta']} | rot+={row['rot_plus']} | inv={row['inverse']} | "
                f"rot-={row['rot_minus']} | z={row['z']} | ae={row['ae']}"
            )
            continue
        if row["cell_family"] == "S":
            lines.append(
                f"{row['shell_position']}) {cell_id} | mu={row['mu']} | "
                f"set={row['pole_set']} | card={row['card']}"
            )
            continue
        record = transfer_index[cell_id]
        if row["cell_family"] == "R":
            plus_binding, minus_binding = record["orientation_bindings"]
            lines.append(
                f"{row['shell_position']}) {cell_id} | set={record['source_set']} | "
                f"AE+={plus_binding['ae_token']} | "
                f"AE-={minus_binding['ae_token']} | "
                f"z={record['z_binding']} | ck={record['check_key']} | rt={record['route_key']}"
            )
            continue
        if row["cell_family"] == "Q":
            binding = record["orientation_bindings"][0]
            lines.append(
                f"{row['shell_position']}) {cell_id} | set={record['source_set']} | "
                f"AE={binding['ae_token']} | "
                f"z={record['z_binding']} | ck={record['check_key']} | rt={record['route_key']}"
            )
            continue
        binding = record["orientation_bindings"][0]
        lines.append(
            f"{row['shell_position']}) {cell_id} | hide={record['hidden_pole']} | set={record['source_set']} | "
            f"AE={binding['ae_token']} | "
            f"z={record['z_binding']} | ck={record['check_key']} | rt={record['route_key']}"
        )
    return "\n".join(lines)


def render_orientation_bindings_markdown(orientation_bindings: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for binding in orientation_bindings:
        lines.extend(
            [
                f"#### {binding['orientation_id']}",
                "",
                "```json",
                json.dumps(binding, indent=2),
                "```",
                "",
            ]
        )
    return lines


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip() + "\n"
    pattern = re.compile(rf"(?ms)^{re.escape(heading)}\n.*?(?=^## |\Z)")
    if pattern.search(text):
        return pattern.sub(block, text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block


def replace_block(text: str, start_marker: str, end_marker: str, body: str) -> str:
    pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.S)
    replacement = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    if pattern.search(text):
        return pattern.sub(replacement, text)
    return text.rstrip() + "\n\n" + replacement + "\n"


def replace_line(text: str, pattern: str, replacement: str) -> str:
    return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)


def parse_loop_number(loop_id: str) -> int:
    return int(loop_id.lstrip("L"))


def reconcile_hsigma_authority_truth() -> None:
    current_loop_id = "L01"
    current_loop_title = "Seat Truth Sync"
    current_loop_completion_state = "COMPLETED"
    next_loop_id = "L02"
    next_loop_title = "Packet Truth Sync"
    next_loop_state = "SEEDED_ONLY"
    current_loop_state = canonical_loop_state_text(current_loop_id, next_loop_id)
    feeder_tuple = ["Q42", "TQ04", "Q50", "Q46", "Q02"]

    if MASTER_LOOP_STATE_57_PATH.exists():
        master_state = load_json(MASTER_LOOP_STATE_57_PATH)
        master_state["generated_at"] = utc_now()
        master_state["active_membrane"] = "Q41 / TQ06"
        master_state["feeder_stack"] = list(feeder_tuple)
        master_state["current_loop_state"] = current_loop_state
        master_state["completed_loop"] = {
            "number": 1,
            "label": f"{current_loop_id} {current_loop_title}",
            "state": current_loop_completion_state,
        }
        master_state["active_loop"] = {
            "number": 2,
            "label": f"{next_loop_id} {next_loop_title}",
            "state": next_loop_state,
        }
        master_state["next_ready_loop"] = {
            "number": 2,
            "label": f"{next_loop_id} {next_loop_title}",
        }
        master_state["next_invocation_contract"] = f"NEXT => {next_loop_id} {next_loop_title} [{next_loop_state}]"
        master_state["restart_seed"] = f"{next_loop_id} {next_loop_title} [{next_loop_state}]"
        for loop in master_state.get("loops", []):
            loop_id = loop.get("loop_id")
            if loop_id == current_loop_id:
                loop["status"] = current_loop_completion_state
            elif loop_id == next_loop_id:
                loop["status"] = next_loop_state
            else:
                loop["status"] = "QUEUED"
        write_json(MASTER_LOOP_STATE_57_PATH, master_state)

    machine_core = load_json(HSIGMA_MACHINE_CORE_PATH)
    machine_core["generated_at"] = utc_now()
    machine_core["current_loop_binding"] = f"{current_loop_id} {current_loop_title}"
    machine_core["next_loop_binding"] = f"{next_loop_id} {next_loop_title}"
    machine_core["current_loop_completion_state"] = current_loop_completion_state
    machine_core["next_loop_state"] = next_loop_state
    machine_core["public_fronts"] = {
        "hall": "NEXT57",
        "temple": "TQ07",
        "hall_compatibility_alias": "Q51",
        "hall_alias_status": "historical_only",
    }
    machine_core["startup_control_story"]["hall_feeder"]["quest"] = "Q42"
    machine_core["startup_control_story"]["landed_receiver"] = "TQ04"
    machine_core["startup_control_story"]["runtime_frontier"] = "Q50"
    machine_core["startup_control_story"]["reserve_activation_feeder"] = "Q46"
    machine_core["startup_control_story"]["blocked_external_frontier"] = "Q02"
    machine_core["visible_core_manifest"]["current_loop_binding"] = (
        f"{current_loop_id} {current_loop_title} [{current_loop_completion_state}]"
    )
    machine_core["visible_core_manifest"]["next_loop_binding"] = (
        f"{next_loop_id} {next_loop_title} [{next_loop_state}]"
    )
    machine_core["visible_core_manifest"]["docs_gate_status"] = "BLOCKED"
    write_json(HSIGMA_MACHINE_CORE_PATH, machine_core)

    cycle_registry = load_json(HSIGMA_CYCLE_REGISTRY_PATH)
    cycle_registry["generated_at"] = utc_now()
    cycle_registry["status"] = "COMPATIBILITY_MIRROR"
    cycle_registry["canonical_authority"] = "self_actualize/master_loop_state_57.json"
    for loop in cycle_registry.get("loops", []):
        loop_id = loop.get("loop_id")
        if loop_id == current_loop_id:
            loop["status"] = current_loop_completion_state
        elif loop_id == next_loop_id:
            loop["status"] = next_loop_state
        else:
            loop["status"] = "QUEUED"
    write_json(HSIGMA_CYCLE_REGISTRY_PATH, cycle_registry)

    public_program = load_json(HSIGMA_PROGRAM_PATH)
    public_program["generated_at"] = utc_now()
    public_program["status"] = "COMPATIBILITY_MIRROR"
    public_program["canonical_authority"] = "self_actualize/master_loop_state_57.json"
    public_program["current_loop_state"] = current_loop_state
    public_program["completed_loop"] = f"{current_loop_id} {current_loop_title}"
    public_program["active_loop"] = f"{next_loop_id} {next_loop_title} [{next_loop_state}]"
    public_program["current_loop_id"] = current_loop_id
    public_program["current_loop_title"] = current_loop_title
    public_program["current_loop_completion_state"] = current_loop_completion_state
    public_program["next_loop_id"] = next_loop_id
    public_program["next_loop_title"] = next_loop_title
    public_program["next_loop_state"] = next_loop_state
    public_program["public_fronts"] = {"hall": "NEXT57", "temple": "TQ07"}
    public_program["compatibility_aliases"] = {"Q51": "historical_hall_alias_only"}
    public_program["feeder_stack"] = [
        {"front_id": "Q42", "state": "VISIBLE", "role": "Hall-side feeder"},
        {"front_id": "TQ04", "state": "VISIBLE", "role": "deeper receiver"},
        {"front_id": "Q50", "state": "VISIBLE", "role": "runtime frontier"},
        {"front_id": "Q46", "state": "VISIBLE", "role": "reserve frontier"},
        {"front_id": "Q02", "state": "BLOCKED", "role": "external docs gate"},
    ]
    public_program["current_cycle_summary"] = {
        "completed_loop": f"{current_loop_id} {current_loop_title}",
        "active_loop": f"{next_loop_id} {next_loop_title} [{next_loop_state}]",
        "restart_seed": f"{next_loop_id} {next_loop_title} [{next_loop_state}]",
        "next_invocation_contract": f"NEXT => {next_loop_id} {next_loop_title} [{next_loop_state}]",
    }
    write_json(HSIGMA_PROGRAM_PATH, public_program)


def hsigma_authority_payloads() -> dict[str, Any]:
    return {
        "machine_core": load_json(HSIGMA_MACHINE_CORE_PATH),
        "cycle_registry": load_json(HSIGMA_CYCLE_REGISTRY_PATH),
        "program": load_json(HSIGMA_PROGRAM_PATH),
        "quest_packets": load_json(HSIGMA_QUEST_PACKETS_PATH),
    }


def hsigma_control_stack(machine_core: dict[str, Any], program: dict[str, Any]) -> list[str]:
    startup = machine_core["startup_control_story"]
    preserved = machine_core.get("preserved_front_truth", {})
    reserve_frontier = "Q46" if "Q46" in preserved else startup.get("reserve_activation_feeder", "Q46")
    return [
        startup["hall_feeder"]["quest"],
        startup["landed_receiver"],
        startup["runtime_frontier"],
        reserve_frontier,
        startup["blocked_external_frontier"],
    ]


def canonical_loop_state_text(current_loop_id: str, next_loop_id: str) -> str:
    return f"{current_loop_id} complete / {next_loop_id} seeded"


def loop_ledger_index(loops: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(loop["loop_index"]): loop for loop in loops}


def canonicalize_runner_manifest(
    runner_manifest: dict[str, Any],
    authority: dict[str, Any],
    loops: list[dict[str, Any]],
) -> dict[str, Any]:
    machine_core = authority["machine_core"]
    cycle_registry = authority["cycle_registry"]
    program = authority["program"]
    public_fronts = machine_core["public_fronts"]
    current_loop_id = machine_core["current_loop_binding"].split(" ", 1)[0]
    next_loop_id = machine_core["next_loop_binding"].split(" ", 1)[0]
    current_loop_title = machine_core["current_loop_binding"].split(" ", 1)[1]
    next_loop_title = machine_core["next_loop_binding"].split(" ", 1)[1]
    current_loop_completion_state = machine_core["current_loop_completion_state"]
    next_loop_state = machine_core["next_loop_state"]
    current_loop_number = parse_loop_number(current_loop_id)
    next_loop_number = parse_loop_number(next_loop_id)
    seat_law = machine_core["visible_core_manifest"]["synaptic_seat_law"]
    indexed_loops = loop_ledger_index(loops)
    current_loop_record = indexed_loops.get(current_loop_number, {})
    cycle_rows = {row.get("loop_id"): row for row in cycle_registry.get("rows", [])}
    current_cycle_row = cycle_rows.get(current_loop_id, {})
    last_bundle = {
        "loop_id": current_loop_id,
        "pass_title": current_loop_title,
        "step_text": current_loop_record.get("step_text", current_loop_title),
        "hall_decision": current_loop_record.get("hall_decision", {}).get("action", "HOLD"),
        "temple_decision": current_loop_record.get("temple_decision", {}).get("action", "HOLD"),
        "runtime_decision": current_loop_record.get("runtime_decision", {}).get("action", "HOLD"),
        "compression_decision": current_loop_record.get("compression_decision", {}).get("action", "HOLD"),
        "restart_seed": f"{next_loop_id} {next_loop_title} [{next_loop_state}]",
        "receipt_id": current_cycle_row.get("receipt_id"),
    }
    canonical_runner = dict(runner_manifest)
    canonical_runner.update(
        {
            "status": canonical_loop_state_text(current_loop_id, next_loop_id),
            "current_completed_loop": current_loop_number,
            "next_ready_loop": next_loop_number,
            "last_executed_loop": current_loop_number,
            "executed_loops": [current_loop_number],
            "hall_macro_front": public_fronts["hall"],
            "temple_macro_front": public_fronts["temple"],
            "active_membrane": "Q41 / TQ06",
            "control_stack": hsigma_control_stack(machine_core, program),
            "seat_law": {
                "virtual_seats_per_master": seat_law["compiled_atlas_seats"],
                "active_seats_per_master": machine_core["shared_seat_law"]["active_per_master"],
                "active_seats_total": seat_law["active_synaptic_seats"],
                "dormant_seats_total": machine_core["shared_seat_law"]["dormant_seats"],
            },
            "current_completed_step": current_loop_title,
            "next_ready_step": f"{next_loop_title} [{next_loop_state}]",
            "last_bundle": last_bundle,
            "loop_authority_source": "HΣ First",
            "pointer_layer_classification": dict(POINTER_LAYER_CLASSIFICATION),
            "cycle_registry_support_state": current_cycle_row.get("status", current_loop_completion_state),
            "public_front_aliases": {
                public_fronts["hall_compatibility_alias"]: public_fronts["hall_alias_status"],
            },
        }
    )
    return canonical_runner


def enforce_hsigma_runner_state(
    runner_manifest: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    machine_core = authority["machine_core"]
    public_fronts = machine_core["public_fronts"]
    current_loop_id = machine_core["current_loop_binding"].split(" ", 1)[0]
    next_loop_id = machine_core["next_loop_binding"].split(" ", 1)[0]
    current_loop_title = machine_core["current_loop_binding"].split(" ", 1)[1]
    next_loop_title = machine_core["next_loop_binding"].split(" ", 1)[1]
    current_loop_number = parse_loop_number(current_loop_id)
    next_loop_number = parse_loop_number(next_loop_id)
    payload = dict(runner_manifest)
    payload.update(
        {
            "status": canonical_loop_state_text(current_loop_id, next_loop_id),
            "current_completed_loop": current_loop_number,
            "next_ready_loop": next_loop_number,
            "last_executed_loop": current_loop_number,
            "executed_loops": [current_loop_number],
            "hall_macro_front": public_fronts["hall"],
            "temple_macro_front": public_fronts["temple"],
            "active_membrane": "Q41 / TQ06",
            "control_stack": hsigma_control_stack(machine_core, authority["program"]),
            "current_completed_step": current_loop_title,
            "next_ready_step": f"{next_loop_title} [{machine_core['next_loop_state']}]",
            "loop_authority_source": "HΣ First",
            "pointer_layer_classification": dict(POINTER_LAYER_CLASSIFICATION),
        }
    )
    return payload


def enforce_hsigma_protocol_state(
    protocol_manifest: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    machine_core = authority["machine_core"]
    public_fronts = machine_core["public_fronts"]
    current_loop_id = machine_core["current_loop_binding"].split(" ", 1)[0]
    next_loop_id = machine_core["next_loop_binding"].split(" ", 1)[0]
    payload = dict(protocol_manifest)
    payload.update(
        {
            "current_loop_state": canonical_loop_state_text(current_loop_id, next_loop_id),
            "current_completed_loop": parse_loop_number(current_loop_id),
            "next_ready_loop": parse_loop_number(next_loop_id),
            "hall_macro_front": public_fronts["hall"],
            "temple_macro_front": public_fronts["temple"],
            "active_membrane": "Q41 / TQ06",
            "control_stack": hsigma_control_stack(machine_core, authority["program"]),
            "loop_authority_source": "HΣ First",
            "pointer_layer_classification": dict(POINTER_LAYER_CLASSIFICATION),
        }
    )
    return payload


def seeded_l02_packet_bundle(protocol_manifest: dict[str, Any]) -> dict[str, Any]:
    restart_seed = "L02 Packet Truth Sync [SEEDED_ONLY]"
    hall_packets = [
        {
            "packet_id": "NEXT57-L02-H01",
            "objective": "Synchronize packet truth between HΣ authority and LP-57 mirror surfaces.",
            "target_surfaces": [
                project_relative(HSIGMA_MACHINE_CORE_PATH),
                project_relative(HSIGMA_CYCLE_REGISTRY_PATH),
                project_relative(OUTPUT_MANIFEST_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A1", "A2"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "NEXT57-L02-H02",
            "objective": "Attach `12/13/14/15/16/17/18` as canonical L02 packet-input witnesses without promoting loop completion.",
            "target_surfaces": [
                project_relative(SHELL_SPEC_MD),
                project_relative(AETHER_POINTER_REGISTRY_JSON),
                project_relative(AETHER_POINTER_WITNESS_MD),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A1", "A3"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "NEXT57-L02-H03",
            "objective": "Preserve feeder tuple law `Q42 / TQ04 / Q50 / Q46 / Q02` during packet truth synchronization.",
            "target_surfaces": [
                project_relative(HSIGMA_PROGRAM_PATH),
                project_relative(QUEST_BOARD_PATH),
                project_relative(BUILD_QUEUE_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A2", "A3"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "NEXT57-L02-H04",
            "objective": "Preserve blocked Docs truth and explicitly suppress premature `L03 Authority Pointer Replacement` exposure.",
            "target_surfaces": [
                "self_actualize/live_docs_gate_status.md",
                project_relative(QUEST_BOARD_PATH),
                project_relative(ACTIVE_RUN_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A3", "A4"],
            "restart_seed": restart_seed,
        },
    ]
    temple_packets = [
        {
            "packet_id": "TQ07-L02-T01",
            "objective": "Ratify HΣ -> cycle registry -> quest packets -> program -> LP-57 mirrors as the packet truth precedence chain.",
            "target_surfaces": [
                project_relative(HSIGMA_MACHINE_CORE_PATH),
                project_relative(HSIGMA_CYCLE_REGISTRY_PATH),
                project_relative(HSIGMA_PROGRAM_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A1", "A2"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "TQ07-L02-T02",
            "objective": "Classify the dense-shell and pointer layer as `L01-closed substrate enhancement` plus `L02 Packet Truth Sync input witness` only.",
            "target_surfaces": [
                project_relative(TRANSFER_WITNESS_MD),
                project_relative(AETHER_POINTER_WITNESS_MD),
                project_relative(PROTOCOL_STATE_JSON),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A1", "A2"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "TQ07-L02-T03",
            "objective": "Preserve feeder tuple law and keep `NEXT57 / TQ07` live while `Q51` remains compatibility-only.",
            "target_surfaces": [
                project_relative(HSIGMA_PROGRAM_PATH),
                project_relative(TEMPLE_STATE_PATH),
                project_relative(QUEST_BOARD_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A2", "A3"],
            "restart_seed": restart_seed,
        },
        {
            "packet_id": "TQ07-L02-T04",
            "objective": "Preserve docs-blocker law and keep `L02 Packet Truth Sync` seeded-only until packet truth closure is actually witnessed.",
            "target_surfaces": [
                "self_actualize/live_docs_gate_status.md",
                project_relative(TEMPLE_STATE_PATH),
                project_relative(HSIGMA_RECONCILIATION_RECEIPT_PATH),
            ],
            "state": "SEEDED_ONLY",
            "linked_agents": ["A3", "A4"],
            "restart_seed": restart_seed,
        },
    ]
    return {
        "loop_id": "L02",
        "title": "Packet Truth Sync",
        "state": "SEEDED_ONLY",
        "classification": dict(POINTER_LAYER_CLASSIFICATION),
        "feeder_tuple": list(protocol_manifest["control_stack"]),
        "docs_gate_status": "BLOCKED",
        "hall_packets": hall_packets,
        "temple_packets": temple_packets,
        "restart_seed": restart_seed,
    }


def render_seeded_packet_lines(packets: list[dict[str, Any]]) -> list[str]:
    return [
        f"- `{packet['packet_id']}` {packet['objective']} :: state `{packet['state']}` :: restart `{packet['restart_seed']}`"
        for packet in packets
    ]


def sync_hsigma_seeded_packet_sources(protocol_manifest: dict[str, Any]) -> dict[str, Any]:
    seed_bundle = seeded_l02_packet_bundle(protocol_manifest)
    quest_packets = load_json(HSIGMA_QUEST_PACKETS_PATH)
    quest_packets["generated_at"] = utc_now()
    quest_packets["active_loop_id"] = "L01"
    quest_packets["current_loop_id"] = "L01"
    quest_packets["current_loop_title"] = "Seat Truth Sync"
    quest_packets["current_loop_completion_state"] = "COMPLETED"
    quest_packets["next_loop_id"] = "L02"
    quest_packets["next_loop_title"] = "Packet Truth Sync"
    quest_packets["next_loop_state"] = "SEEDED_ONLY"
    quest_packets["public_fronts"] = {"hall": "NEXT57", "temple": "TQ07"}
    quest_packets["compatibility_aliases"] = {"Q51": "historical_hall_alias_only"}
    quest_packets["feeder_tuple"] = list(seed_bundle["feeder_tuple"])
    quest_packets["hall_promotions"] = list(seed_bundle["hall_packets"])
    quest_packets["temple_promotions"] = list(seed_bundle["temple_packets"])
    quest_packets["seeded_next_packets"] = seed_bundle
    quest_packets["restart_seed"] = seed_bundle["restart_seed"]
    write_json(HSIGMA_QUEST_PACKETS_PATH, quest_packets)

    public_program = load_json(HSIGMA_PROGRAM_PATH)
    public_program["generated_at"] = utc_now()
    public_program["current_loop_id"] = "L01"
    public_program["current_loop_title"] = "Seat Truth Sync"
    public_program["current_loop_completion_state"] = "COMPLETED"
    public_program["current_loop_state"] = canonical_loop_state_text("L01", "L02")
    public_program["completed_loop"] = "L01 Seat Truth Sync"
    public_program["active_loop"] = "L02 Packet Truth Sync [SEEDED_ONLY]"
    public_program["next_loop_id"] = "L02"
    public_program["next_loop_title"] = "Packet Truth Sync"
    public_program["next_loop_state"] = "SEEDED_ONLY"
    public_program["public_fronts"] = {"hall": "NEXT57", "temple": "TQ07"}
    public_program["compatibility_aliases"] = {"Q51": "historical_hall_alias_only"}
    public_program["feeder_stack"] = [
        {"front_id": "Q42", "state": "VISIBLE", "role": "Hall-side feeder"},
        {"front_id": "TQ04", "state": "VISIBLE", "role": "deeper receiver"},
        {"front_id": "Q50", "state": "VISIBLE", "role": "runtime frontier"},
        {"front_id": "Q46", "state": "VISIBLE", "role": "reserve frontier"},
        {"front_id": "Q02", "state": "BLOCKED", "role": "external docs gate"},
    ]
    public_program["current_cycle_summary"] = {
        "completed_loop": "L01 Seat Truth Sync",
        "active_loop": "L02 Packet Truth Sync [SEEDED_ONLY]",
        "restart_seed": seed_bundle["restart_seed"],
        "next_invocation_contract": "NEXT => L02 Packet Truth Sync [SEEDED_ONLY]",
    }
    public_program["seeded_next_packets"] = {
        "loop_id": seed_bundle["loop_id"],
        "title": seed_bundle["title"],
        "state": seed_bundle["state"],
        "hall_packet_ids": [packet["packet_id"] for packet in seed_bundle["hall_packets"]],
        "temple_packet_ids": [packet["packet_id"] for packet in seed_bundle["temple_packets"]],
        "classification": seed_bundle["classification"],
        "feeder_tuple": seed_bundle["feeder_tuple"],
        "docs_gate_status": "BLOCKED",
        "restart_seed": seed_bundle["restart_seed"],
    }
    write_json(HSIGMA_PROGRAM_PATH, public_program)
    return seed_bundle


def write_hsigma_reconciliation_receipt(protocol_manifest: dict[str, Any], seed_bundle: dict[str, Any]) -> None:
    receipt_lines = [
        "# LP-57Omega HΣ-First Reconciliation and L02 Seed Receipt",
        "",
        f"- Date: `{utc_now()[:10]}`",
        "- Docs Gate: `BLOCKED`",
        "- Authority choice: `HΣ First`",
        f"- Authority chain: `{ ' -> '.join(HSIGMA_AUTHORITY_CHAIN) }`",
        "- Reconciled LP-57 state: `L01 complete / L02 seeded`",
        "- Rejected drift: `L02 complete / L03 ready`",
        f"- Hall front: `{protocol_manifest['hall_macro_front']}`",
        f"- Temple front: `{protocol_manifest['temple_macro_front']}`",
        f"- Feeder tuple preserved: `{ ' / '.join(protocol_manifest['control_stack']) }`",
        "",
        "## Pointer Layer Classification",
        "",
        f"- Dense shell role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
        f"- Packet truth role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        "",
        "## Seeded L02 Hall Packets",
        "",
        *render_seeded_packet_lines(seed_bundle["hall_packets"]),
        "",
        "## Seeded L02 Temple Packets",
        "",
        *render_seeded_packet_lines(seed_bundle["temple_packets"]),
        "",
        f"- Restart law: `{seed_bundle['restart_seed']}`",
    ]
    write_text(HSIGMA_RECONCILIATION_RECEIPT_PATH, "\n".join(receipt_lines) + "\n")


def legacy_records_index() -> dict[str, dict[str, Any]]:
    if not LEGACY_CYCLE_RECORDS_PATH.exists():
        return {}
    payload = load_json(LEGACY_CYCLE_RECORDS_PATH)
    return {record["loop_id"]: record for record in payload.get("records", [])}


def coerce_advancement_tuple(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        fields = [
            "advancement_label",
            "synthesis_problem",
            "planning_problem",
            "implementation_target",
            "compression_target",
            "mapping_target",
        ]
        return {
            field: item
            for field, item in zip(fields, value)
            if item not in (None, "")
        }
    return {}


def merged_loop_catalog(loops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    legacy = legacy_records_index()
    merged: list[dict[str, Any]] = []
    for loop in loops:
        loop_id = f"L{int(loop['loop_index']):02d}"
        legacy_record = legacy.get(loop_id, {})
        advancement = coerce_advancement_tuple(legacy_record.get("advancement_tuple"))
        merged.append(
            {
                "loop_id": loop_id,
                "loop_index": int(loop["loop_index"]),
                "pass_id": loop["pass_id"],
                "pass_title": loop["pass_title"],
                "theme": loop["theme"],
                "step_text": loop["step_text"],
                "dominant_focus": legacy_record.get("dominant_focus", loop["step_text"]),
                "primary_synthesis_objective": advancement.get("synthesis_problem", loop["step_text"]),
                "primary_planning_objective": advancement.get("planning_problem", loop["hall_decision"]["reason"]),
                "primary_implementation_objective": advancement.get("implementation_target", loop["runtime_decision"]["reason"]),
                "primary_compression_objective": advancement.get("compression_target", loop["compression_decision"]["reason"]),
                "expected_structural_gain": legacy_record.get("expected_structural_gain", loop["pass_title"]),
                "expected_mapping_gain": advancement.get("mapping_target", loop["restart_seed"]),
                "hall_action": loop["hall_decision"]["action"],
                "temple_action": loop["temple_decision"]["action"],
                "runtime_action": loop["runtime_decision"]["action"],
                "compression_action": loop["compression_decision"]["action"],
                "starting_control_stack": loop["starting_control_stack"],
                "seat_activation": loop["seat_activation"],
                "awakening_refresh": loop["awakening_refresh"],
                "restart_seed": loop["restart_seed"],
            }
        )
    return merged


def render_executive_overview(runner_manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# LP-57Omega Executive Overview",
            "",
            "LP-57Omega treats the Athena corpus as a living, recursively governed hive rather than a static archive. The protocol begins from the installed local state already present in this workspace and remains strictly local-witnessed while the Google Docs gate is blocked.",
            "",
            "## Starting Anchor",
            "",
            f"- Current loop state: `{runner_manifest['status']}`",
            f"- Hall macro front: `{runner_manifest['hall_macro_front']}`",
            f"- Temple macro front: `{runner_manifest['temple_macro_front']}`",
            f"- Active membrane: `{runner_manifest['active_membrane']}`",
            f"- Control stack: `{ ' / '.join(runner_manifest['control_stack']) }`",
            "- Truth regime: `local-witnessed`",
            f"- Live-doc gate: `BLOCKED` :: {runner_manifest['live_docs_error']}",
            "",
            "## Prime-Cycle Law",
            "",
            "- `57` is treated as a prime-cycle stabilizer against repetitive nexus-lock patterns.",
            "- Every loop must produce a distinct advancement tuple rather than a cosmetic replay.",
            "- Novelty, urgency, and diligence are preserved by enforcing non-identical synthesis, planning, implementation, compression, and mapping gains.",
            "",
            "## Continuity Law",
            "",
            "- liminal coordinates give every touched node, frontier, contradiction, and compression node a stable lookup address",
            "- cumulative ledgers preserve what each agent observed, changed, fixed, compressed, and left unresolved",
            "- restart seeds move the organism forward without losing traceability",
        ]
    ) + "\n"


def render_master_loop_framework() -> str:
    lines = ["# Master Loop Framework", "", "## Four-Master Cycle", ""]
    for master_id, spec in MASTER_AGENT_SPECS.items():
        lines.extend(
            [
                f"### {master_id} :: {spec['label']}",
                f"- Primary action type: `{spec['action_type']}`",
                f"- Role tag: `{spec['role_tag']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Nested 4^6 Seat Law",
            "",
            "- Each master owns `4096` virtual seats across six axes of resolution and function.",
            "- Sparse activation law: `256 active seats/master`, `1024 active seats total`, `3072 dormant seats total`.",
            "- Default active split per master: `64 corpus + 64 family + 64 chapter/appendix/supplement + 64 runtime/board`.",
            "",
            "## Seat Axes",
            "",
            "- Axis 1 / Resolution: `corpus`, `family`, `chapter_appendix`, `runtime_board`",
            "- Axis 2 / Lens: `square`, `flower`, `cloud`, `fractal`",
            "- Axis 3 / Truth Mode: `witness`, `replay`, `pressure`, `blocker`",
            "- Axis 4 / Output Organ: `hall`, `temple`, `runtime`, `supplement`",
            "- Axis 5 / Action Mode: `observe`, `derive`, `route`, `prune`",
            "- Axis 6 / Priority Band: `immediate`, `near`, `reserve`, `dormant`",
            "",
            "## Hall / Temple Quest Law",
            "",
            "- `Guild Hall` carries practical build, rewrite, repair, integration, indexing, math, algorithmization, and runtime work.",
            "- `Temple` carries structural, ontological, symbolic, coordinate, compression, and emergence work.",
            "- Only the Planner may promote visible macro quests.",
            f"- Visible promotion law per loop: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression`.",
            "",
            "## Loop Invariants",
            "",
            "- one loop receipt",
            "- four master-agent receipts",
            "- one ranked internal quest-packet ledger",
            "- one Hall decision",
            "- one Temple decision",
            "- one runtime writeback receipt or explicit no-op",
            "- one compression delta",
            "- one restart seed",
        ]
    )
    return "\n".join(lines) + "\n"


def render_coordinate_standard() -> str:
    return "\n".join(
        [
            "# Liminal Identity and Coordinate Standard",
            "",
            "## Agent Identity",
            "",
            "- Agent ID format: `[LoopID].[MasterAgentID].[NestedDepth].[BranchPath].[RoleTag]`",
            "- Example: `L07.A2.D4.B0312.PLANNER-ARCHITECT`",
            "- Example: `L21.A4.D6.B4444.PRUNE-COMPRESS`",
            "",
            "## Coordinate Tuple",
            "",
            f"- Dimensions: `{', '.join(COORDINATE_DIMENSIONS)}`",
            "- `Xs`: document or region anchor",
            "- `Ys`: family or concept cluster",
            "- `Zs`: recursion depth",
            "- `Ts`: loop or revision layer",
            "- `Qs`: active frontier or quest pressure",
            "- `Rs`: replay or witness burden",
            "- `Cs`: compression state",
            "- `Fs`: framework lens",
            "- `Ms`: manuscript branch",
            "- `Ns`: neural or mycelial connectivity",
            "- `Hs`: hierarchy level",
            "- `Omega_s`: legality or zero-point relation",
            "",
            "## Lookup Address Law",
            "",
            "- every touched idea, section, bridge, contradiction, unresolved frontier, and compression node receives a coordinate stamp",
            "- every promoted bridge remains localized",
            "- every unresolved issue remains coordinate-addressable",
            "- every compression pack keeps back-references to the expanded surfaces it contracts",
            "",
            "## State Vocabulary",
            "",
            f"- Entity states: `{', '.join(ENTITY_STATES)}`",
        ]
    ) + "\n"


def render_ledger_standard() -> str:
    lines = ["# Agent Ledger Standard", "", "## Required Fields", ""]
    lines.extend([f"- `{field}`" for field in LEDGER_FIELDS])
    lines.extend(
        [
            "",
            "## Continuity Law",
            "",
            "- ledger continuity is cumulative and inherited across loops",
            "- each loop carries prior observations, touched branches, contradictions, seeds, blockages, interfaces, and emerging patterns forward",
            "- no loop may claim advancement without a ledger delta, coordinate update, quest relation, and explicit gain or explicit no-gain explanation",
        ]
    )
    return "\n".join(lines) + "\n"


def render_loop_plan(loop_catalog: list[dict[str, Any]]) -> str:
    lines = ["# 57-Loop Plan", ""]
    current_pass = None
    for loop in loop_catalog:
        if loop["pass_title"] != current_pass:
            current_pass = loop["pass_title"]
            lines.extend(["", f"## {current_pass}"])
        lines.extend(
            [
                f"### {loop['loop_id']} :: {loop['dominant_focus']}",
                f"- Dominant focus: `{loop['dominant_focus']}`",
                f"- Primary synthesis objective: `{loop['primary_synthesis_objective']}`",
                f"- Primary planning objective: `{loop['primary_planning_objective']}`",
                f"- Primary implementation objective: `{loop['primary_implementation_objective']}`",
                f"- Primary compression/pruning objective: `{loop['primary_compression_objective']}`",
                f"- Expected structural gain: `{loop['expected_structural_gain']}`",
                f"- Expected mapping / ledger gain: `{loop['expected_mapping_gain']}`",
                f"- Action tuple: `Hall={loop['hall_action']} / Temple={loop['temple_action']} / Runtime={loop['runtime_action']} / Compression={loop['compression_action']}`",
            ]
        )
    return "\n".join(lines) + "\n"


def render_final_synthesis() -> str:
    return "\n".join(
        [
            "# Final Synthesis",
            "",
            "After 57 loops, the corpus no longer behaves like a loose pile of tomes, chapters, code, runtime notes, and support essays. It behaves like a liminal hive architecture with stable identity, bounded governance, explicit routing, and replay-safe compression.",
            "",
            "## Expected End State",
            "",
            "- every active idea, bridge, contradiction, frontier, and compression node is addressable",
            "- spine, supplements, runtime, Hall, Temple, motion, metro, and neural layers are linked through explicit routes",
            "- the system can contract into seeds without losing replayability or route traceability",
            "- the Planner can promote lawful macro fronts from a dense internal lattice without flooding the visible boards",
            "- restart seeds preserve memory continuity from one epoch to the next",
            "",
            "The result is not finished knowledge. It is a lawful, self-steering, higher-dimensional corpus organism that can synthesize, plan, execute, compress, map, and reseed while remaining honest about blocked sources and witness burden.",
        ]
    ) + "\n"


def coordinate_schema() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "dimensions": COORDINATE_DIMENSIONS,
        "entity_states": ENTITY_STATES,
        "target_axes": TARGET_AXIS,
        "lookup_rules": {
            "address_every_touched_object": True,
            "address_every_promoted_bridge": True,
            "address_every_unresolved_issue": True,
            "compression_requires_back_references": True,
        },
    }


def ledger_schema() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "fields": LEDGER_FIELDS,
        "continuity": {
            "cumulative": True,
            "inherits_prior_observations": True,
            "inherits_prior_blockers": True,
            "requires_delta_per_loop": True,
        },
    }


def nested_lattice() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "virtual_seats_per_master": 4096,
        "active_seats_per_master": 256,
        "active_seats_total": 1024,
        "dormant_seats_total": 3072,
        "active_partition_per_master": {
            "corpus": 64,
            "family": 64,
            "chapter_appendix_supplement": 64,
            "runtime_board": 64,
        },
        "axes": {
            "resolution": ["corpus", "family", "chapter_appendix", "runtime_board"],
            "lens": ["square", "flower", "cloud", "fractal"],
            "truth_mode": ["witness", "replay", "pressure", "blocker"],
            "output_organ": ["hall", "temple", "runtime", "supplement"],
            "action_mode": ["observe", "derive", "route", "prune"],
            "priority_band": ["immediate", "near", "reserve", "dormant"],
        },
        "master_agents": MASTER_AGENT_SPECS,
    }


def protocol_state(
    shell_registry: dict[str, Any],
    transfer_registry: dict[str, Any],
    pointer_registry: dict[str, Any],
    super_cycle_manifest: dict[str, Any],
    runner_manifest: dict[str, Any],
    corpus_manifest: dict[str, Any],
    motion_manifest: dict[str, Any],
) -> dict[str, Any]:
    counts = dense_65_counts(shell_registry, transfer_registry, pointer_registry)
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "status": "canonical-installed",
        "truth_regime": "local-witnessed",
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(),
        "current_loop_state": runner_manifest["status"],
        "current_completed_loop": runner_manifest["current_completed_loop"],
        "next_ready_loop": runner_manifest["next_ready_loop"],
        "hall_macro_front": runner_manifest["hall_macro_front"],
        "temple_macro_front": runner_manifest["temple_macro_front"],
        "active_membrane": runner_manifest["active_membrane"],
        "control_stack": runner_manifest["control_stack"],
        "seat_law": runner_manifest["seat_law"],
        "loop_authority_source": runner_manifest.get("loop_authority_source", "HΣ First"),
        "pointer_layer_classification": dict(POINTER_LAYER_CLASSIFICATION),
        "visible_promotion_law": VISIBLE_PROMOTION_LAW,
        "sigma_path": SIGMA_PATH,
        "rotation_carriers": ROTATION_CARRIERS,
        "shell_truth": SHELL_TRUTH,
        "shell_record_count": counts["total"],
        "active_dense_record_count": counts["active_dense"],
        "enriched_transfer_record_count": counts["enriched_transfer"],
        "phase_binding_count": counts["phase_bindings"],
        "concrete_pointer_count": counts["concrete_pointers"],
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "record_count": corpus_manifest["record_count"],
        "motion_truth": motion_manifest["truth"],
        "super_cycle_status": super_cycle_manifest["status"],
    }


def compatibility_witnesses() -> dict[str, Any]:
    paths = [
        LIVE_DOCS_RECEIPT_PATH,
        LOOP_LEDGER_PATH,
        SUPER_CYCLE_MANIFEST_PATH,
        RUNNER_MANIFEST_PATH,
        CORPUS_MANIFEST_PATH,
        MOTION_MANIFEST_PATH,
        QUEST_BOARD_PATH,
        TEMPLE_STATE_PATH,
        ACTIVE_RUN_PATH,
        LEGACY_CYCLE_RECORDS_PATH,
        LEGACY_LEDGER_PATH,
        LEGACY_COORDS_PATH,
    ]
    return {
        "protocol_id": PROTOCOL_ID,
        "witness_paths": [project_relative(path) for path in paths if path.exists()],
        "legacy_mirror_policy": "reuse as compatibility witnesses, not independent authority",
        "canonical_authority": project_relative(OUTPUT_MANIFEST_PATH),
    }


def render_shell_spec(
    shell_registry: dict[str, Any] | None = None,
    transfer_registry: dict[str, Any] | None = None,
    pointer_registry: dict[str, Any] | None = None,
) -> str:
    shell_registry = shell_registry or shell_registry_payload()
    transfer_registry = transfer_registry or transfer_registry_payload()
    pointer_registry = pointer_registry or dense_65_canonical_payloads()["pointer_registry"]
    counts = dense_65_counts(shell_registry, transfer_registry, pointer_registry)
    return "\n".join(
        [
            "# LP-57Omega Dense 65-Shell",
            "",
            "- Truth status: `NEAR-derived`",
            f"- LP-57 role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
            f"- Packet sync role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
            "- Reserved slot: `1/65 = prior seed/header shell`",
            "- Active dense range: `2/65 -> 65/65`",
            f"- Sigma path: `{' -> '.join(SIGMA_PATH)}`",
            f"- Rotation carriers: `{' / '.join(ROTATION_CARRIERS)}`",
            f"- Base-3 antispin lock: `{BASE3_ANTISPIN_LOCK}`",
            "- Operator lens lock: `Flower / F`",
            "- Phase map: `Phi0=R+ / Phi1=R- / Phi2=Q4 / Phi3=T3`",
            f"- Route presets: `rtL={pointer_registry['route_constants']['rtL']}` and `rtZ={pointer_registry['route_constants']['rtZ']}`",
            "- Pole gauge: `A=Fire, C=Air, B=Water, D=Earth`",
            "- Lawful adjacency cycle: `Fire -> Air -> Water -> Earth -> Fire`",
            "- Opposite-pole shortcuts are forbidden except by adjacent bridging or `Z*` tunneling.",
            "",
            "## Counts",
            "",
            f"- Total shell slots: `{counts['total']}`",
            f"- Active dense records: `{counts['active_dense']}`",
            f"- Partition: `{counts['P']} P + {counts['S']} S + {counts['R']} R + {counts['Q']} Q + {counts['T']} T`",
            f"- Enriched operator records: `{counts['enriched_transfer']}`",
            f"- Phase bindings: `{counts['phase_bindings']}`",
            f"- Concrete pointers: `{counts['concrete_pointers']}`",
            "",
            "## Dense Block",
            "",
            "```text",
            render_dense_block(shell_registry, transfer_registry),
            "```",
        ]
    ) + "\n"


def render_transfer_witness_markdown(transfer_registry: dict[str, Any] | None = None) -> str:
    transfer_registry = transfer_registry or transfer_registry_payload()
    orientation_binding_count = sum(len(record["orientation_bindings"]) for record in transfer_registry["records"])
    lines = [
        "# R/Q/T Transfer Signature and Metro Witness Registry",
        "",
        f"- Truth status: `{SHELL_TRUTH}`",
        f"- LP-57 role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
        f"- Packet sync role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        f"- Sigma path: `{' -> '.join(SIGMA_PATH)}`",
        f"- Base-3 antispin lock: `{BASE3_ANTISPIN_LOCK}`",
        f"- Enriched logical records: `{transfer_registry['enriched_transfer_record_count']}`",
        f"- Total orientation bindings: `{orientation_binding_count}`",
        "- Dual-shape mode: `legacy summaries + structured orientation_bindings`",
        f"- Full pointer ABI: `{project_relative(AETHER_POINTER_REGISTRY_JSON)}` and `{project_relative(AETHER_POINTER_WITNESS_MD)}`",
        "",
    ]
    for record_type, title in [("R", "Rotation Records"), ("Q", "Base-4 Q4 Orbits"), ("T", "Base-3 T3 Residual Orbits")]:
        lines.extend(["## " + title, ""])
        for record in transfer_registry["records"]:
            if record["record_type"] != record_type:
                continue
            bindings = record["orientation_bindings"]
            lines.extend(
                [
                    f"### {record['record_id']} :: slot `{record['shell_slot_label']}`",
                    f"- Source set: `{record['source_set']}`",
                    f"- Z binding: `{record['z_binding']}`",
                    f"- Check key: `{record['check_key']}`",
                    f"- Route key: `{record['route_key']}`",
                    f"- Orbit mechanics ref: `{record['orbit_mechanics_ref']}`",
                    f"- Z* transfer signature: {record['z_transfer_signature']}",
                    f"- AETHER transfer signature: {record['aether_transfer_signature']}",
                    f"- Prior metro route witness: `{record['prior_metro_route_witness']}`",
                    f"- Packaging status: `{record['packaging_status']}`",
                    f"- Phase binding count: `{len(bindings)}`",
                    "- Full field-level bindings:",
                    "",
                ]
            )
            lines.extend(render_orientation_bindings_markdown(bindings))
    return "\n".join(lines).rstrip() + "\n"


def render_pointer_witness_markdown(pointer_registry: dict[str, Any]) -> str:
    lines = [
        "# LP-57Omega AETHER Witness/Replay Pointer Witness",
        "",
        f"- Truth status: `{pointer_registry['truth_status']}`",
        f"- LP-57 role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
        f"- Packet sync role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        f"- Record count: `{pointer_registry['record_count']}`",
        f"- Concrete pointer count: `{pointer_registry['concrete_pointer_count']}`",
        f"- Lens lock: `{pointer_registry['aether_lattice_abi']['lens']}`",
        "- Phase map: `Phi0=R+ / Phi1=R- / Phi2=Q4 / Phi3=T3`",
        f"- Sigma path: `{' -> '.join(pointer_registry['sigma_path'])}`",
        f"- Route preset `rtL`: `{pointer_registry['route_constants']['rtL']}`",
        f"- Route preset `rtZ`: `{pointer_registry['route_constants']['rtZ']}`",
        "",
        "## Pointer ABI Lock",
        "",
        "```json",
        json.dumps(
            {
                "aether_lattice_abi": pointer_registry["aether_lattice_abi"],
                "witness_lock": pointer_registry["witness_lock"],
                "replay_lock": pointer_registry["replay_lock"],
            },
            indent=2,
        ),
        "```",
        "",
    ]
    for record_type, title in [("R", "Rotation Pairs"), ("Q", "Base-4 Q4 Records"), ("T", "Base-3 T3 Residual Records")]:
        lines.extend([f"## {title}", ""])
        for record in pointer_registry["records"]:
            if record["record_type"] != record_type:
                continue
            lines.extend(
                [
                    f"### {record['record_id']} :: slot `{record['shell_slot_label']}`",
                    f"- Source set: `{record['source_set']}`",
                    f"- Z alias: `{record['z_alias']}`",
                    f"- Z expanded: `{record['z_expanded']}`",
                    f"- Check key: `{record['ck']}`",
                    f"- Route key: `{record['rt']}`",
                    f"- Route path: `{record['rt_path']}`",
                    f"- Packaging status: `{record['packaging_status']}`",
                ]
            )
            if record["hidden_pole"]:
                lines.append(f"- Hidden pole: `{record['hidden_pole']}`")
            lines.extend(["", "```json", json.dumps(record["pointers"], indent=2), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_shell_supplement(shell_registry: dict[str, Any] | None = None, transfer_registry: dict[str, Any] | None = None) -> str:
    shell_registry = shell_registry or shell_registry_payload()
    transfer_registry = transfer_registry or transfer_registry_payload()
    counts = dense_65_counts(shell_registry, transfer_registry)
    return "\n".join(
        [
            "# LP-57Omega Dense 65-Shell",
            "",
            "The LP-57Omega dense shell freezes a 65-slot coordinate substrate for the prime-loop hive protocol.",
            "",
            "## Shell Law",
            "",
            "- `1/65` is reserved as the prior seed/header shell.",
            "- `2/65 -> 65/65` form the active dense block.",
            "- Pole gauge: `A=Fire, C=Air, B=Water, D=Earth`.",
            "- Lawful cycle: `Fire -> Air -> Water -> Earth -> Fire`.",
            "- Opposite-pole shortcuts are forbidden except by adjacent bridging or `Z*` tunneling.",
            f"- Sigma path: `{' -> '.join(SIGMA_PATH)}` with `{' / '.join(ROTATION_CARRIERS)}` carrying orbit and rail rotation mechanics.",
            f"- Base-3 antispin lock: `{BASE3_ANTISPIN_LOCK}`.",
            "",
            "## Partition",
            "",
            f"- Total shell slots: `{counts['total']}`",
            f"- Active dense records: `{counts['active_dense']}`",
            f"- Record partition: `{counts['P']} P + {counts['S']} S + {counts['R']} R + {counts['Q']} Q + {counts['T']} T`",
            f"- Enriched transfer bindings: `{counts['enriched_transfer']} logical records / {sum(len(record['orientation_bindings']) for record in transfer_registry['records'])} orientation bindings`",
            "",
            "## Explicit AE Lock",
            "",
            "- All operator-family coordinates in this shell are pinned to the Flower lens `F`.",
            "- `R` records carry paired `R+ / R-` coordinates in `Core`.",
            "- `Q` records carry single `Q4` coordinates in `Core`.",
            "- `T` records carry single `T3` coordinates in `Residual` with explicit hidden-pole suffixes.",
            "",
            "## Truth Boundary",
            "",
            "- Status: `NEAR-derived`",
            "- Corpus-grounded basis: `base-4 address discipline`, `order-4 lens rotation`, `order-3 rail rotation`.",
            "- Packaging note: `base-3 antispin lock` is a deterministic packaging choice layered on top of corpus law, not a verbatim corpus term.",
            "",
            "## Canonical Runtime Surfaces",
            "",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/12_dense_65_shell_spec.md`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/13_dense_65_shell_registry.json`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/14_rqt_transfer_signature_registry.json`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/15_rqt_transfer_signature_and_metro_witness.md`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/16_aether_witness_replay_pointer_registry.json`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/17_aether_witness_replay_pointer_witness.md`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/18_aether_witness_replay_pointer_schema.json`",
            "",
            "The next lawful nesting layer is the additive per-record `R/Q/T` AETHER witness/replay pointer ABI.",
        ]
    ) + "\n"


def render_transfer_supplement(transfer_registry: dict[str, Any] | None = None) -> str:
    transfer_registry = transfer_registry or transfer_registry_payload()
    return "\n".join(
        [
            "# LP-57Omega R/Q/T Transfer Signature and Metro Witness Registry",
            "",
            "This supplement freezes the first witness-bearing enrichment pass over the dense shell.",
            "",
            "## Scope",
            "",
            "- Raw shell records remain canonical for `P` and `S`.",
            "- Only `R`, `Q`, and `T` receive explicit `Z* / AETHER / WitnessPtr / ReplayPtr` payloads in this pass.",
            "- `R` records keep one logical row with `plus` and `minus` phase bindings; `Q` keeps a `spin` binding and `T` keeps an `antispin` binding.",
            "",
            "## Registry Law",
            "",
            f"- Truth status: `{SHELL_TRUTH}`",
            f"- Sigma path: `{' -> '.join(SIGMA_PATH)}`",
            f"- All operator-family bindings are pinned to the Flower lens and remain local-only while the docs gate is blocked: `{transfer_registry['phase_binding_count']}` phase bindings across `{transfer_registry['enriched_transfer_record_count']}` logical rows.",
            "- Every enriched record keeps the legacy summary strings and now derives them from explicit `phase_bindings` and full field-level pointer payloads.",
            "- `R` rows expose `plus` and `minus`; `Q` rows expose `spin`; `T` rows expose `antispin` with explicit hidden-pole and `Residual` slot law.",
            "",
            "## Route Witness Anchors",
            "",
            "- `R` records anchor to `03_METRO/00_core_metro_map.md :: Ch07<0012>`",
            "- `Q` records anchor to `03_METRO/00_core_metro_map.md :: Ch08<0013>`",
            "- `T` records anchor to `04_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md`",
            "",
            "## Canonical Runtime Surfaces",
            "",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/14_rqt_transfer_signature_registry.json`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/15_rqt_transfer_signature_and_metro_witness.md`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/16_aether_witness_replay_pointer_registry.json`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/17_aether_witness_replay_pointer_witness.md`",
            "- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/18_aether_witness_replay_pointer_schema.json`",
            "",
            "The registry is supplements-facing documentation of the runtime shell object and is not part of the strict spine.",
        ]
    ) + "\n"


def ensure_supplement_entries() -> dict[str, Any]:
    registry = load_json(MANUSCRIPT_MANIFEST_PATH)
    desired_entries = [
        {
            "canonical_id": "Supp09",
            "display_title": "LP-57Omega Dense 65-Shell",
            "kind": "supplement",
            "volume": "supplements",
            "order": 90,
            "source_file": SHELL_SUPPLEMENT_PATH.name,
            "canonical_target_file": SHELL_SUPPLEMENT_PATH.name,
            "status": "supplement",
        },
        {
            "canonical_id": "Supp10",
            "display_title": "LP-57Omega R/Q/T Transfer Signature and Metro Witness Registry",
            "kind": "supplement",
            "volume": "supplements",
            "order": 100,
            "source_file": TRANSFER_SUPPLEMENT_PATH.name,
            "canonical_target_file": TRANSFER_SUPPLEMENT_PATH.name,
            "status": "supplement",
        },
    ]
    entry_by_id = {entry["canonical_id"]: entry for entry in registry["entries"]}
    for desired in desired_entries:
        entry_by_id[desired["canonical_id"]] = desired
    ordered_entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in registry["entries"]:
        canonical_id = entry["canonical_id"]
        if canonical_id in {"Supp09", "Supp10"}:
            if canonical_id in seen:
                continue
            ordered_entries.append(entry_by_id[canonical_id])
            seen.add(canonical_id)
            continue
        ordered_entries.append(entry)
        seen.add(canonical_id)
    for desired in desired_entries:
        if desired["canonical_id"] not in seen:
            ordered_entries.append(desired)
    registry["entries"] = ordered_entries
    write_json(MANUSCRIPT_MANIFEST_PATH, registry)
    return registry


def publish_supplements(shell_registry: dict[str, Any], transfer_registry: dict[str, Any]) -> dict[str, Any]:
    ensure_supplement_entries()
    write_text(SHELL_SUPPLEMENT_PATH, render_shell_supplement(shell_registry, transfer_registry))
    write_text(TRANSFER_SUPPLEMENT_PATH, render_transfer_supplement(transfer_registry))
    return build_manuscript_volumes(MANUSCRIPT_MANIFEST_PATH)


def update_runner_manifest(shell_manifest: dict[str, Any], runner_manifest: dict[str, Any]) -> None:
    payload = load_json(RUNNER_MANIFEST_PATH)
    payload["status"] = shell_manifest["current_loop_state"]
    payload["current_completed_loop"] = shell_manifest["current_completed_loop"]
    payload["next_ready_loop"] = shell_manifest["next_ready_loop"]
    payload["last_executed_loop"] = runner_manifest.get("last_executed_loop", shell_manifest["current_completed_loop"])
    payload["executed_loops"] = runner_manifest.get("executed_loops", [shell_manifest["current_completed_loop"]])
    payload["hall_macro_front"] = shell_manifest["hall_macro_front"]
    payload["temple_macro_front"] = shell_manifest["temple_macro_front"]
    payload["active_membrane"] = shell_manifest["active_membrane"]
    payload["control_stack"] = list(shell_manifest["control_stack"])
    payload["seat_law"] = runner_manifest.get("seat_law", payload.get("seat_law"))
    payload["current_completed_step"] = runner_manifest.get("current_completed_step", payload.get("current_completed_step"))
    payload["next_ready_step"] = runner_manifest.get("next_ready_step", payload.get("next_ready_step"))
    payload["last_bundle"] = runner_manifest.get("last_bundle", payload.get("last_bundle"))
    payload["loop_authority_source"] = shell_manifest["loop_authority_source"]
    payload["pointer_layer_classification"] = dict(shell_manifest["pointer_layer_classification"])
    payload["protocol_id"] = PROTOCOL_ID
    payload["shell_protocol_manifest"] = f"06_RUNTIME/{RUNTIME_MANIFEST_NAME}"
    payload["shell_reference_ready"] = True
    payload["shell_record_count"] = shell_manifest["shell_record_count"]
    payload["active_dense_record_count"] = shell_manifest["active_dense_record_count"]
    payload["enriched_transfer_record_count"] = shell_manifest["enriched_transfer_record_count"]
    payload["phase_binding_count"] = shell_manifest["phase_binding_count"]
    payload["concrete_pointer_count"] = shell_manifest["concrete_pointer_count"]
    payload["shell_truth"] = shell_manifest["shell_truth"]
    payload["sigma_path"] = SIGMA_PATH
    payload["base3_antispin_lock"] = BASE3_ANTISPIN_LOCK
    write_json(RUNNER_MANIFEST_PATH, payload)


def update_active_readme(manifest: dict[str, Any]) -> None:
    text = ACTIVE_README_PATH.read_text(encoding="utf-8")
    bullet = (
        "- `18_LP_57OMEGA_PROTOCOL`: canonical prime-loop hive protocol, liminal coordinate standard, "
        "agent ledger schema, dense 65-shell, and R/Q/T transfer witness registry. Manifest: `06_RUNTIME/20_lp_57omega_protocol_manifest.json`."
    )
    anchor = "- `17_SUPER_CYCLE_57`: four-master orchestration layer, 57 loop ledger, packet registry, promotion decisions, and sparse `4^6` seat law. Manifest: `06_RUNTIME/18_super_cycle_57_manifest.json`."
    if bullet not in text:
        text = text.replace(anchor, anchor + "\n" + bullet, 1) if anchor in text else text.rstrip() + "\n" + bullet + "\n"
    section_lines = [
        f"- Status: `{manifest['status']}`",
        "- Layer root: `18_LP_57OMEGA_PROTOCOL`",
        "- Runtime manifest: `06_RUNTIME/20_lp_57omega_protocol_manifest.json`",
        f"- Current loop state: `{manifest['current_loop_state']}`",
        f"- Dense shell counts: `{manifest['shell_record_count']} total / {manifest['active_dense_record_count']} active / {manifest['enriched_transfer_record_count']} enriched RQT / {manifest['phase_binding_count']} phase bindings / {manifest['concrete_pointer_count']} concrete pointers`",
        f"- Sigma path: `{' -> '.join(SIGMA_PATH)}`",
        f"- Base-3 antispin lock: `{BASE3_ANTISPIN_LOCK}`",
        f"- Visible promotion law: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression`",
        "- Live Google Docs: `BLOCKED`",
    ]
    text = replace_or_append_section(text, "## LP-57Omega Protocol State", section_lines)
    text = replace_line(text, r"^- Supplement entries: `\d+`$", f"- Supplement entries: `{manifest['supplement_entry_count']}`")
    write_text(ACTIVE_README_PATH, text)


def update_full_stack_manifest(manifest: dict[str, Any]) -> None:
    payload = load_json(FULL_STACK_MANIFEST_PATH)
    payload["generated_at"] = utc_now()
    payload["live_docs_blocked"] = True
    payload.setdefault("layers", {})
    payload["layers"]["lp_57omega_protocol"] = {
        "manifest": f"06_RUNTIME/{RUNTIME_MANIFEST_NAME}",
        "layer_root": LAYER_FOLDER,
        "status": manifest["status"],
        "protocol_id": PROTOCOL_ID,
        "current_loop_state": manifest["current_loop_state"],
        "current_completed_loop": manifest["current_completed_loop"],
        "next_ready_loop": manifest["next_ready_loop"],
        "shell_record_count": manifest["shell_record_count"],
        "active_dense_record_count": manifest["active_dense_record_count"],
        "enriched_transfer_record_count": manifest["enriched_transfer_record_count"],
        "phase_binding_count": manifest["phase_binding_count"],
        "concrete_pointer_count": manifest["concrete_pointer_count"],
        "shell_truth": manifest["shell_truth"],
        "sigma_path": SIGMA_PATH,
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "visible_promotion_law": VISIBLE_PROMOTION_LAW,
        "live_docs_blocked": True,
    }
    if "canonical_spine_registry" in payload["layers"]:
        payload["layers"]["canonical_spine_registry"]["supplement_entry_count"] = manifest["supplement_entry_count"]
        payload["layers"]["canonical_spine_registry"]["supplement_entry_ids"] = manifest["supplement_entry_ids"]
    write_json(FULL_STACK_MANIFEST_PATH, payload)


def sync_compatibility_markdown(protocol_manifest: dict[str, Any]) -> None:
    protocol_markdown = "\n".join(
        [
            f"# {PROTOCOL_DISPLAY_NAME}: 57-Prime Loop Liminal Hive Protocol",
            "",
            "## Canonical State",
            "",
            f"- Runtime manifest: `{project_relative(OUTPUT_MANIFEST_PATH)}`",
            f"- Status: `{protocol_manifest['current_loop_state']}`",
            f"- Hall macro front: `{protocol_manifest['hall_macro_front']}`",
            f"- Temple macro front: `{protocol_manifest['temple_macro_front']}`",
            f"- Active membrane: `{protocol_manifest['active_membrane']}`",
            f"- Control stack: `{ ' / '.join(protocol_manifest['control_stack']) }`",
            f"- Visible promotion law: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression`",
            f"- Dense shell: `{protocol_manifest['shell_record_count']} total / {protocol_manifest['enriched_transfer_record_count']} enriched RQT / {protocol_manifest['phase_binding_count']} phase bindings / {protocol_manifest['concrete_pointer_count']} concrete pointers`",
            "- Docs gate: `BLOCKED`",
            "",
            "## Compatibility Rule",
            "",
            "- `LP-57OMEGA` is canonical.",
            "- `NEXT57`, `Q51/TQ07`, and older swarm-program surfaces are compatibility mirrors only.",
        ]
    )
    write_text(LEGACY_PROTOCOL_MARKDOWN_PATH, protocol_markdown)


def sync_b_prime_pointer_compatibility(protocol_manifest: dict[str, Any]) -> None:
    compatibility_markdown = "\n".join(
        [
            "# B' Witnessed Inversion Shell",
            "",
            "Docs gate: `BLOCKED`",
            f"Protocol: `{PROTOCOL_DISPLAY_NAME}`",
            "Shell law: `A -> B -> B'`",
            "",
            "## Compatibility Lock",
            "",
            "- `B'` remains the compatibility name for the explicit Flower-lens witnessed inversion shell.",
            "- This surface no longer maintains an independent pointer grammar.",
            f"- Canonical pointer registry: `{project_relative(AETHER_POINTER_REGISTRY_JSON)}`",
            f"- Canonical pointer witness: `{project_relative(AETHER_POINTER_WITNESS_MD)}`",
            f"- Canonical pointer schema: `{project_relative(AETHER_POINTER_SCHEMA_JSON)}`",
            f"- Dense shell counts: `{protocol_manifest['shell_record_count']} total / {protocol_manifest['enriched_transfer_record_count']} enriched RQT / {protocol_manifest['phase_binding_count']} phase bindings / {protocol_manifest['concrete_pointer_count']} concrete pointers`",
            "",
            "## Route Law",
            "",
            "- `Sigma = AppA -> AppI -> AppM` remains mandatory.",
            "- `rtL` and `rtZ` are sourced from the canonical pointer registry.",
            "- `R/Q` stay in `Core`; `T` stays in `Residual` with explicit hidden-pole payloads.",
            "- Docs access remains blocked until authenticated OAuth files exist.",
        ]
    ) + "\n"
    write_text(FLEET_B_PRIME_COMPAT_PATH, compatibility_markdown)
    write_text(SELF_B_PRIME_COMPAT_PATH, compatibility_markdown)


def sync_external_protocol_state(protocol_manifest: dict[str, Any], loop_catalog: list[dict[str, Any]]) -> None:
    state_payload = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "status": protocol_manifest["current_loop_state"],
        "truth_regime": "local-witnessed",
        "live_docs_blocked": True,
        "hall_macro_front": protocol_manifest["hall_macro_front"],
        "temple_macro_front": protocol_manifest["temple_macro_front"],
        "active_membrane": protocol_manifest["active_membrane"],
        "control_stack": protocol_manifest["control_stack"],
        "loop_authority_source": protocol_manifest["loop_authority_source"],
        "pointer_layer_classification": protocol_manifest["pointer_layer_classification"],
        "visible_promotion_law": VISIBLE_PROMOTION_LAW,
        "shell_record_count": protocol_manifest["shell_record_count"],
        "active_dense_record_count": protocol_manifest["active_dense_record_count"],
        "enriched_transfer_record_count": protocol_manifest["enriched_transfer_record_count"],
        "phase_binding_count": protocol_manifest["phase_binding_count"],
        "concrete_pointer_count": protocol_manifest["concrete_pointer_count"],
        "shell_truth": protocol_manifest["shell_truth"],
        "sigma_path": SIGMA_PATH,
        "current_completed_loop": protocol_manifest["current_completed_loop"],
        "next_ready_loop": protocol_manifest["next_ready_loop"],
        "loop_catalog_path": project_relative(LOOP_CATALOG_JSON),
    }
    write_json(SELF_PROTOCOL_STATE_PATH, state_payload)
    write_json(
        SELF_PROTOCOL_CATALOG_PATH,
        {
            "generated_at": utc_now()[:10],
            "protocol_id": PROTOCOL_ID,
            "protocol_display_name": PROTOCOL_DISPLAY_NAME,
            "truth": "LOCAL-WITNESSED",
            "current_loop": protocol_manifest["current_completed_loop"],
            "records": [
                {
                    "loop_id": item["loop_id"],
                    "pass_title": item["pass_title"],
                    "dominant_focus": item["dominant_focus"],
                    "step_text": item["step_text"],
                    "restart_seed": item["restart_seed"],
                    "action_tuple": {
                        "hall": item["hall_action"],
                        "temple": item["temple_action"],
                        "runtime": item["runtime_action"],
                        "compression": item["compression_action"],
                    },
                    "expected_structural_gain": item["expected_structural_gain"],
                    "expected_mapping_gain": item["expected_mapping_gain"],
                }
                for item in loop_catalog
            ],
        },
    )


def sync_runtime_surfaces(protocol_manifest: dict[str, Any]) -> None:
    seed_bundle = seeded_l02_packet_bundle(protocol_manifest)
    hall_seed_lines = render_seeded_packet_lines(seed_bundle["hall_packets"])
    temple_seed_lines = render_seeded_packet_lines(seed_bundle["temple_packets"])
    mirror_block = "\n".join(
        [
            "## Four-Agent 57-Loop Program Compatibility Mirror",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            "- Status: `COMPATIBILITY_MIRROR / PROTOCOL-SYNCED`",
            "- Canonical authority: `HΣ First`",
            f"- Authority chain: `{ ' -> '.join(HSIGMA_AUTHORITY_CHAIN) }`",
            "- Compatibility family: `NEXT57`",
            f"- Next seed: `{seed_bundle['restart_seed']}`",
            "- Independent restart seeds: `DISALLOWED`",
        ]
    )
    hall_block = "\n".join(
        [
            "## LP-57Omega Hall Quest Interface",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            f"- Canonical authority: `{project_relative(HSIGMA_MACHINE_CORE_PATH)} -> {project_relative(HSIGMA_CYCLE_REGISTRY_PATH)} -> {project_relative(HSIGMA_PROGRAM_PATH)} -> {project_relative(OUTPUT_MANIFEST_PATH)}`",
            f"- Public Hall front: `{protocol_manifest['hall_macro_front']}`",
            f"- Public Temple front: `{protocol_manifest['temple_macro_front']}`",
            "- Historical Hall alias only: `Q51`",
            f"- Completed loop: `L{protocol_manifest['current_completed_loop']:02d}`",
            f"- Next seeded loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
            f"- Active membrane: `{protocol_manifest['active_membrane']}`",
            f"- Feeder stack: `{ ' / '.join(protocol_manifest['control_stack']) }`",
            f"- Planner public cap: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression per loop`",
            "- Shared lattice: `4^6 = 4096 indexed / 1024 ACTIVE / 3072 DORMANT`",
            f"- Pointer role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
            f"- Packet input role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
            "",
            "### Seeded L02 Hall Packets",
            "",
            *hall_seed_lines,
        ]
    )
    temple_block = "\n".join(
        [
            "## LP-57Omega Temple State",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs gate: `BLOCKED`",
            f"- Active membrane: `{protocol_manifest['active_membrane']}`",
            f"- Current Temple support loop: `L{protocol_manifest['current_completed_loop']:02d}`",
            f"- Next seeded Temple loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
            f"- Current Hall feeder: `{protocol_manifest['control_stack'][0]}`",
            f"- Landed contract feeder: `{protocol_manifest['control_stack'][1]}`",
            f"- Runtime frontier: `{protocol_manifest['control_stack'][2]}`",
            f"- Reserve activation feeder: `{protocol_manifest['control_stack'][3]}`",
            f"- External blocker: `{protocol_manifest['control_stack'][4]}`",
            "",
            "### Seeded L02 Temple Packets",
            "",
            *temple_seed_lines,
        ]
    )
    active_run_block = "\n".join(
        [
            "## LP-57Omega Four-Agent Corpus Cycle",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            f"- Canonical authority: `{ ' -> '.join(HSIGMA_AUTHORITY_CHAIN) }`",
            "- Compatibility mirrors: `NEXT57`, `Q51/TQ07`, `FA57`",
            f"- Status: `{protocol_manifest['current_loop_state']}`",
            f"- Seeded next loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
            f"- Visible promotion law: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression`",
            f"- Active membrane: `{protocol_manifest['active_membrane']}`",
            f"- Control stack: `{ ' / '.join(protocol_manifest['control_stack']) }`",
            f"- Pointer layer role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        ]
    )
    runner_section_lines = [
        f"- Status: `{protocol_manifest['current_loop_state']}`",
        f"- Current completed loop: `L{protocol_manifest['current_completed_loop']:02d}`",
        f"- Next ready loop: `{f'L{protocol_manifest['next_ready_loop']:02d}' if protocol_manifest['next_ready_loop'] else 'NONE'}`",
        "- Planner-only visible promotion law: `True`",
        f"- Visible promotion ceiling: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression`",
    ]
    active_run_seed_section = [
        f"- Seed bundle: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        f"- Pointer witness role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        f"- Restart law: `{seed_bundle['restart_seed']}`",
        f"- Reconciliation receipt: `{project_relative(HSIGMA_RECONCILIATION_RECEIPT_PATH)}`",
    ]
    active_run_front_lines = [
        f"- Current loop: `L{protocol_manifest['current_completed_loop']:02d} Seat Truth Sync [COMPLETED]`",
        f"- Next loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        "- Current order: `SYNTHESIZER -> PLANNER -> WORKER -> PRUNER`",
        "- Docs gate: `BLOCKED`",
        f"- Restart seed: `{seed_bundle['restart_seed']}`",
        f"- Public fronts: `{protocol_manifest['hall_macro_front']} / {protocol_manifest['temple_macro_front']}`",
        "- Historical Hall alias only: `Q51`",
    ]
    active_run_control_lines = [
        f"- Date: `{utc_now()[:10]}`",
        "- Docs Gate: `BLOCKED`",
        f"- Canonical authority: `{ ' -> '.join(HSIGMA_AUTHORITY_CHAIN) }`",
        f"- Current state: `{protocol_manifest['current_loop_state']}`",
        f"- Completed loop: `L{protocol_manifest['current_completed_loop']:02d} Seat Truth Sync`",
        f"- Next ready loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        f"- Active membrane: `{protocol_manifest['active_membrane']}`",
        f"- Feeder stack: `{ ' / '.join(protocol_manifest['control_stack']) }`",
        "- Shared lattice: `4096 total / 1024 ACTIVE / 3072 DORMANT`",
        "- Role namespace: `4096 per master over shared 4096`",
        "- Packet contract: `research_delta, quest_packet, execution_batch, compression_bundle, receipt, restart_seed`",
        f"- Pointer packet role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
    ]
    build_queue_section_lines = [
        f"- Hall front: `{protocol_manifest['hall_macro_front']}`",
        f"- Temple front: `{protocol_manifest['temple_macro_front']}`",
        f"- Current loop: `L{protocol_manifest['current_completed_loop']:02d} Seat Truth Sync [COMPLETED]`",
        f"- Next loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        "- Historical Hall alias only: `Q51`",
        "- Shared seat law: `4096 compiled / 1024 active / 3072 dormant / 256 per master`",
        "- Visible law stack: `16 -> 64 -> 256 -> 1024 -> 4096`",
        f"- Pointer packet role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
    ]
    build_queue_front_lines = [
        "- Shared seats: `4096`",
        "- Virtual overlay: `4 x 4096`",
        f"- Hall front: `{protocol_manifest['hall_macro_front']}`",
        f"- Temple front: `{protocol_manifest['temple_macro_front']}`",
        f"- Current loop: `L{protocol_manifest['current_completed_loop']:02d} Seat Truth Sync [COMPLETED]`",
        f"- Next seeded loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        f"- Latest receipt: `{project_relative(HSIGMA_RECONCILIATION_RECEIPT_PATH)}`",
        f"- Pointer packet role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        "- Historical Hall alias only: `Q51`",
    ]
    quest_board_front_lines = [
        "- Docs gate: `BLOCKED`",
        f"- Canonical authority: `{ ' -> '.join(HSIGMA_AUTHORITY_CHAIN) }`",
        f"- Public Hall front: `{protocol_manifest['hall_macro_front']}`",
        f"- Public Temple front: `{protocol_manifest['temple_macro_front']}`",
        "- Historical Hall alias only: `Q51`",
        f"- Current loop: `L{protocol_manifest['current_completed_loop']:02d} Seat Truth Sync [COMPLETED]`",
        f"- Next loop: `{seed_bundle['loop_id']} {seed_bundle['title']} [{seed_bundle['state']}]`",
        f"- Active membrane: `{protocol_manifest['active_membrane']}`",
        f"- Feeder tuple: `{ ' / '.join(protocol_manifest['control_stack']) }`",
        f"- Pointer role: `{POINTER_LAYER_CLASSIFICATION['dense_shell_role']}`",
        f"- Packet input role: `{POINTER_LAYER_CLASSIFICATION['packet_truth_sync_role']}`",
        "",
        "### Seeded L02 Hall Packets",
        "",
        *hall_seed_lines,
    ]
    if QUEST_BOARD_PATH.exists():
        text = QUEST_BOARD_PATH.read_text(encoding="utf-8")
        text = text.replace("## NEXT57 Runner Execution State", "## LP-57Omega Runner Execution State")
        text = replace_or_append_section(text, "## LP-57Omega v2 Hall Quest Interface", quest_board_front_lines)
        text = replace_block(text, "<!-- FOUR_AGENT_57_LOOP_PROGRAM:START -->", "<!-- FOUR_AGENT_57_LOOP_PROGRAM:END -->", mirror_block)
        text = replace_block(text, "<!-- MASTER_LOOP_57_HALL_QUEST:START -->", "<!-- MASTER_LOOP_57_HALL_QUEST:END -->", hall_block)
        text = replace_or_append_section(
            text,
            "## Current Hall Packets",
            ["- See `### Seeded L02 Hall Packets` in `## LP-57Omega v2 Hall Quest Interface` above."],
        )
        text = replace_or_append_section(text, "## LP-57Omega Runner Execution State", runner_section_lines)
        write_text(QUEST_BOARD_PATH, text)
    if TEMPLE_STATE_PATH.exists():
        text = TEMPLE_STATE_PATH.read_text(encoding="utf-8")
        text = replace_block(text, "<!-- MASTER_LOOP_57_TEMPLE_STATE:START -->", "<!-- MASTER_LOOP_57_TEMPLE_STATE:END -->", temple_block)
        write_text(TEMPLE_STATE_PATH, text)
    if ACTIVE_RUN_PATH.exists():
        text = ACTIVE_RUN_PATH.read_text(encoding="utf-8")
        text = replace_or_append_section(text, "## LP-57Omega v2 Active Run", active_run_front_lines)
        text = replace_block(text, "<!-- NEXT57_FOUR_AGENT_CYCLE:START -->", "<!-- NEXT57_FOUR_AGENT_CYCLE:END -->", active_run_block)
        text = replace_or_append_section(text, "## LP-57Ω Packet Truth Sync Seed", active_run_seed_section)
        text = replace_or_append_section(text, "## LP-57Omega v2 Control Plane", active_run_control_lines)
        write_text(ACTIVE_RUN_PATH, text)
    if BUILD_QUEUE_PATH.exists():
        text = BUILD_QUEUE_PATH.read_text(encoding="utf-8")
        text = replace_or_append_section(text, "## LP-57Omega v2 Build Queue", build_queue_front_lines)
        text = replace_or_append_section(text, "## LP-57Ω Queue", build_queue_section_lines)
        text = replace_or_append_section(text, "## Current Hall Packets", hall_seed_lines)
        text = replace_or_append_section(text, "## Current Temple Packets", temple_seed_lines)
        write_text(BUILD_QUEUE_PATH, text)


def build_protocol() -> dict[str, Any]:
    reconcile_hsigma_authority_truth()
    authority = hsigma_authority_payloads()
    super_cycle_manifest = load_json(SUPER_CYCLE_MANIFEST_PATH)
    corpus_manifest = load_json(CORPUS_MANIFEST_PATH)
    motion_manifest = load_json(MOTION_MANIFEST_PATH)
    loops = load_json(LOOP_LEDGER_PATH)
    runner_manifest = enforce_hsigma_runner_state(
        canonicalize_runner_manifest(load_json(RUNNER_MANIFEST_PATH), authority, loops),
        authority,
    )
    loop_catalog = merged_loop_catalog(loops)
    dense_65_payloads = dense_65_canonical_payloads()
    shell_payload = dense_65_payloads["shell_registry"]
    transfer_registry = dense_65_payloads["transfer_registry"]
    pointer_registry = dense_65_payloads["pointer_registry"]
    pointer_schema = dense_65_payloads["pointer_schema"]
    dense_counts = dense_65_counts(shell_payload, transfer_registry, pointer_registry)
    state_payload = protocol_state(
        shell_payload,
        transfer_registry,
        pointer_registry,
        super_cycle_manifest,
        runner_manifest,
        corpus_manifest,
        motion_manifest,
    )
    supplements_receipt = publish_supplements(shell_payload, transfer_registry)
    supplement_ids = supplements_receipt["volumes"]["supplements"]["entry_ids"]

    write_text(EXEC_OVERVIEW_MD, render_executive_overview(runner_manifest))
    write_text(MASTER_FRAMEWORK_MD, render_master_loop_framework())
    write_text(COORDINATE_STANDARD_MD, render_coordinate_standard())
    write_text(LEDGER_STANDARD_MD, render_ledger_standard())
    write_text(LOOP_PLAN_MD, render_loop_plan(loop_catalog))
    write_text(FINAL_SYNTHESIS_MD, render_final_synthesis())
    write_json(COORDINATE_SCHEMA_JSON, coordinate_schema())
    write_json(LEDGER_SCHEMA_JSON, ledger_schema())
    write_json(NESTED_LATTICE_JSON, nested_lattice())
    write_json(LOOP_CATALOG_JSON, loop_catalog)
    write_json(PROTOCOL_STATE_JSON, state_payload)
    write_json(COMPATIBILITY_WITNESSES_JSON, compatibility_witnesses())
    write_text(SHELL_SPEC_MD, render_shell_spec(shell_payload, transfer_registry, pointer_registry))
    write_json(SHELL_REGISTRY_JSON, shell_payload)
    write_json(TRANSFER_WITNESS_JSON, transfer_registry)
    write_json(AETHER_POINTER_REGISTRY_JSON, pointer_registry)
    write_json(AETHER_POINTER_SCHEMA_JSON, pointer_schema)
    write_text(TRANSFER_WITNESS_MD, render_transfer_witness_markdown(transfer_registry))
    write_text(AETHER_POINTER_WITNESS_MD, render_pointer_witness_markdown(pointer_registry))
    write_text(
        README_PATH,
        "\n".join(
            [
                "# LP-57Omega Protocol",
                "",
                f"- Protocol ID: `{PROTOCOL_ID}`",
                "- Status: `canonical-installed`",
                f"- Current loop state: `{runner_manifest['status']}`",
                "- Truth regime: `local-witnessed`",
                f"- Sigma path: `{' -> '.join(SIGMA_PATH)}`",
                f"- Dense shell counts: `{dense_counts['total']} total / {dense_counts['active_dense']} active / {dense_counts['enriched_transfer']} enriched RQT / {dense_counts['phase_bindings']} phase bindings / {dense_counts['concrete_pointers']} concrete pointers`",
                f"- Base-3 antispin lock: `{BASE3_ANTISPIN_LOCK}`",
                f"- Visible promotion law: `{VISIBLE_PROMOTION_LAW['hall']} Hall + {VISIBLE_PROMOTION_LAW['temple']} Temple + {VISIBLE_PROMOTION_LAW['runtime']} runtime + {VISIBLE_PROMOTION_LAW['compression']} compression per loop`",
                "- This layer is the canonical coordination/spec surface for the 57-prime liminal hive protocol.",
            ]
        )
        + "\n"
    )

    manifest = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "status": "canonical-installed",
        "truth_regime": "local-witnessed",
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(),
        "layer_root": LAYER_FOLDER,
        "current_loop_state": runner_manifest["status"],
        "current_completed_loop": runner_manifest["current_completed_loop"],
        "next_ready_loop": runner_manifest["next_ready_loop"],
        "hall_macro_front": runner_manifest["hall_macro_front"],
        "temple_macro_front": runner_manifest["temple_macro_front"],
        "active_membrane": runner_manifest["active_membrane"],
        "control_stack": runner_manifest["control_stack"],
        "loop_authority_source": runner_manifest["loop_authority_source"],
        "pointer_layer_classification": dict(POINTER_LAYER_CLASSIFICATION),
        "sigma_path": SIGMA_PATH,
        "rotation_carriers": ROTATION_CARRIERS,
        "shell_truth": SHELL_TRUTH,
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "visible_promotion_law": VISIBLE_PROMOTION_LAW,
        "loop_count": len(loop_catalog),
        "master_agent_count": len(MASTER_AGENT_SPECS),
        "record_count": corpus_manifest["record_count"],
        "shell_record_count": dense_counts["total"],
        "active_dense_record_count": dense_counts["active_dense"],
        "enriched_transfer_record_count": dense_counts["enriched_transfer"],
        "phase_binding_count": dense_counts["phase_bindings"],
        "concrete_pointer_count": dense_counts["concrete_pointers"],
        "shell_partition": {
            "P": dense_counts["P"],
            "S": dense_counts["S"],
            "R": dense_counts["R"],
            "Q": dense_counts["Q"],
            "T": dense_counts["T"],
        },
        "supplement_entry_count": supplements_receipt["volumes"]["supplements"]["entry_count"],
        "supplement_entry_ids": supplement_ids,
        "supplement_outputs": supplements_receipt["volumes"]["supplements"],
        "source_manifests": {
            "super_cycle": project_relative(SUPER_CYCLE_MANIFEST_PATH),
            "runner": project_relative(RUNNER_MANIFEST_PATH),
            "corpus_integration": project_relative(CORPUS_MANIFEST_PATH),
            "motion": project_relative(MOTION_MANIFEST_PATH),
        },
        "artifacts": {
            "readme": project_relative(README_PATH),
            "executive_overview": project_relative(EXEC_OVERVIEW_MD),
            "master_loop_framework": project_relative(MASTER_FRAMEWORK_MD),
            "coordinate_standard": project_relative(COORDINATE_STANDARD_MD),
            "ledger_standard": project_relative(LEDGER_STANDARD_MD),
            "loop_plan": project_relative(LOOP_PLAN_MD),
            "final_synthesis": project_relative(FINAL_SYNTHESIS_MD),
            "coordinate_schema": project_relative(COORDINATE_SCHEMA_JSON),
            "ledger_schema": project_relative(LEDGER_SCHEMA_JSON),
            "nested_lattice": project_relative(NESTED_LATTICE_JSON),
            "loop_catalog": project_relative(LOOP_CATALOG_JSON),
            "protocol_state": project_relative(PROTOCOL_STATE_JSON),
            "compatibility_witnesses": project_relative(COMPATIBILITY_WITNESSES_JSON),
            "shell_spec": project_relative(SHELL_SPEC_MD),
            "shell_registry": project_relative(SHELL_REGISTRY_JSON),
            "transfer_witness_registry": project_relative(TRANSFER_WITNESS_JSON),
            "transfer_witness_markdown": project_relative(TRANSFER_WITNESS_MD),
            "pointer_registry": project_relative(AETHER_POINTER_REGISTRY_JSON),
            "pointer_witness_markdown": project_relative(AETHER_POINTER_WITNESS_MD),
            "pointer_schema": project_relative(AETHER_POINTER_SCHEMA_JSON),
            "shell_supplement": project_relative(SHELL_SUPPLEMENT_PATH),
            "transfer_supplement": project_relative(TRANSFER_SUPPLEMENT_PATH),
            "hsigma_reconciliation_receipt": project_relative(HSIGMA_RECONCILIATION_RECEIPT_PATH),
        },
    }
    manifest = enforce_hsigma_protocol_state(manifest, authority)
    seed_bundle = sync_hsigma_seeded_packet_sources(manifest)
    write_json(OUTPUT_MANIFEST_PATH, manifest)
    write_hsigma_reconciliation_receipt(manifest, seed_bundle)
    update_runner_manifest(manifest, runner_manifest)
    update_active_readme(manifest)
    update_full_stack_manifest(manifest)
    sync_compatibility_markdown(manifest)
    sync_b_prime_pointer_compatibility(manifest)
    sync_external_protocol_state(manifest, loop_catalog)
    sync_runtime_surfaces(manifest)
    runner_manifest = enforce_hsigma_runner_state(load_json(RUNNER_MANIFEST_PATH), authority)
    manifest = enforce_hsigma_protocol_state(manifest, authority)
    write_json(OUTPUT_MANIFEST_PATH, manifest)
    update_runner_manifest(manifest, runner_manifest)
    sync_external_protocol_state(manifest, loop_catalog)
    sync_runtime_surfaces(manifest)
    final_seed_bundle = sync_hsigma_seeded_packet_sources(manifest)
    write_hsigma_reconciliation_receipt(manifest, final_seed_bundle)
    return manifest


def main() -> None:
    args = parse_args()
    manifest = build_protocol()
    if args.as_json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"Built {PROTOCOL_ID} at {LAYER_ROOT}")
        print(f"Runtime manifest: {OUTPUT_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
