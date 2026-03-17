#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from motion_constitution_cli import (
    HYSTERESIS_STATE_PATH as MOTION_HYSTERESIS_STATE_PATH,
    evaluate_candidate_world,
    initial_hysteresis_state,
    simulate_candidate_world,
)
from lp_57omega_protocol import (
    BASE3_ANTISPIN_LOCK,
    COORDINATE_DIMENSIONS,
    LEDGER_FIELDS,
    MASTER_AGENT_SPECS as LP57_MASTER_AGENT_SPECS,
    PROTOCOL_ID,
    SHELL_TRUTH,
    SIGMA_PATH,
    protocol_agent_id,
    seat_addr_6d,
    seeded_ledger_entry,
    shell_record_reference,
)
from nervous_system_core import utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
LAYER_ROOT = ACTIVE_ROOT / "17_SUPER_CYCLE_57"
EXECUTION_ROOT = LAYER_ROOT / "13_EXECUTION_STATE"

INSTALLED_MANIFEST_PATH = RUNTIME_ROOT / "18_super_cycle_57_manifest.json"
RUNNER_MANIFEST_PATH = RUNTIME_ROOT / "19_super_cycle_57_runner_manifest.json"
COMMAND_PROTOCOL_MANIFEST_PATH = RUNTIME_ROOT / "21_command_protocol_manifest.json"
FULL_STACK_MANIFEST_PATH = RUNTIME_ROOT / "12_full_stack_manifest.json"
ACTIVE_README_PATH = ACTIVE_ROOT / "README.md"
LOOP_LEDGER_PATH = LAYER_ROOT / "02_LOOP_LEDGER.json"
PACKET_REGISTRY_PATH = LAYER_ROOT / "04_CANDIDATE_QUEST_PACKET_REGISTRY.json"
LIVE_DOCS_RECEIPT_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"

EXEC_PROGRESS_JSON = EXECUTION_ROOT / "00_loop_progress.json"
EXEC_PROGRESS_MD = EXECUTION_ROOT / "00_loop_progress.md"
EXEC_HYSTERESIS_JSON = EXECUTION_ROOT / "00_runner_hysteresis_state.json"
LP57_MASTER_LEDGER_JSON = EXECUTION_ROOT / "14_master_agent_ledger.json"
LP57_COORDINATE_REGISTRY_JSON = EXECUTION_ROOT / "15_liminal_coordinate_registry.json"
LP57_LOOP_DELTA_JSON = EXECUTION_ROOT / "16_loop_delta_receipts.json"
LOOP_RECEIPTS_DIR = EXECUTION_ROOT / "loop_receipts"
MASTER_RECEIPTS_DIR = EXECUTION_ROOT / "master_receipts"
PACKET_LEDGERS_DIR = EXECUTION_ROOT / "packet_ledgers"
CANDIDATE_WORLDS_DIR = EXECUTION_ROOT / "candidate_worlds"
MOTION_EVALS_DIR = EXECUTION_ROOT / "motion_evaluations"
HALL_DECISIONS_DIR = EXECUTION_ROOT / "hall_decisions"
TEMPLE_DECISIONS_DIR = EXECUTION_ROOT / "temple_decisions"
RUNTIME_RECEIPTS_DIR = EXECUTION_ROOT / "runtime_receipts"
COMPRESSION_DELTAS_DIR = EXECUTION_ROOT / "compression_deltas"
RESTART_SEEDS_DIR = EXECUTION_ROOT / "restart_seeds"

QUEST_BOARD_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
HALL_PROGRAM_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "57_loop_hall_program.md"
TEMPLE_PROGRAM_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "57_loop_temple_program.md"
TEMPLE_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
TEMPLE_57_STATE_JSON = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "57_LOOP_STATE.json"
TEMPLE_57_STATE_MD = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "57_LOOP_STATE.md"
ACTIVE_RUN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
PROGRAM_95_JSON = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "FOUR_AGENT_57_LOOP_PROGRAM.json"
SELF_REGISTRY_JSON = WORKSPACE_ROOT / "self_actualize" / "57_loop_cycle_registry.json"
SELF_RECEIPT_LEDGER_MD = WORKSPACE_ROOT / "self_actualize" / "57_loop_receipt_ledger.md"
SELF_LP57_MASTER_LEDGER_JSON = WORKSPACE_ROOT / "self_actualize" / "lp_57_master_agent_ledger.json"
SELF_LP57_COORDS_JSON = WORKSPACE_ROOT / "self_actualize" / "lp_57_liminal_coordinate_stamps.json"
SELF_LP57_DELTA_JSON = WORKSPACE_ROOT / "self_actualize" / "lp_57_loop_delta_receipts.json"

MASTER_SEQUENCE = [
    ("A1", "Research/Synthesis"),
    ("A2", "Planner/Governor"),
    ("A3", "Worker/Adventurer"),
    ("A4", "Pruner/Compressor"),
]
CONTROL_STACK = ["Q42", "TQ04", "Q50", "Q46", "Q02"]
VISIBLE_PROMOTION_LIMIT = {"hall": 1, "temple": 1, "runtime": 1, "compression": 1}
SCHEDULED_NOTES = {"board_agent_delta_every": 1, "full_bundle_every": 3, "pass_boundary_every": 9}
SEAT_LAW = {
    "virtual_seats_per_master": 4096,
    "active_seats_per_master": 256,
    "active_seats_total": 1024,
    "dormant_seats_total": 3072,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute the installed Super-Cycle 57 program.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show current runner state.")
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    dry_run_parser = subparsers.add_parser("dry-run", help="Evaluate one or more loops without mutating state.")
    dry_run_parser.add_argument("--from-loop", type=int, required=True)
    dry_run_parser.add_argument("--to-loop", type=int, required=True)
    dry_run_parser.add_argument("--json", action="store_true", dest="as_json")

    run_parser = subparsers.add_parser("run", help="Execute a contiguous range of loops.")
    run_parser.add_argument("--from-loop", type=int, required=True)
    run_parser.add_argument("--to-loop", type=int, required=True)
    run_parser.add_argument("--json", action="store_true", dest="as_json")

    advance_parser = subparsers.add_parser("advance-one", help="Execute the current next-ready loop.")
    advance_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def command_protocol_manifest() -> dict[str, Any] | None:
    if not COMMAND_PROTOCOL_MANIFEST_PATH.exists():
        return None
    return load_json(COMMAND_PROTOCOL_MANIFEST_PATH)


def live_docs_error() -> str:
    if not LIVE_DOCS_RECEIPT_PATH.exists():
        return "Error: Missing OAuth client file: credentials.json"
    for line in LIVE_DOCS_RECEIPT_PATH.read_text(encoding="utf-8").splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Google Docs gate remains blocked."


def project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        try:
            return str(path.resolve().relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())


def replace_block(text: str, start_marker: str, end_marker: str, body: str) -> str:
    pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.S)
    replacement = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    if pattern.search(text):
        return pattern.sub(replacement, text)
    if text.rstrip():
        return text.rstrip() + "\n\n" + replacement + "\n"
    return replacement + "\n"


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip() + "\n"
    pattern = re.compile(rf"(?ms)^{re.escape(heading)}\n.*?(?=^## |\Z)")
    if pattern.search(text):
        return pattern.sub(block, text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block


def replace_line(text: str, pattern: str, replacement: str) -> str:
    return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)


def extract_bootstrap_state_from_temple() -> dict[str, Any]:
    text = TEMPLE_STATE_PATH.read_text(encoding="utf-8")
    current_match = re.search(r"Current loop:\s*`(\d+)`", text)
    next_match = re.search(r"Next loop:\s*`(\d+)`", text)
    current_completed = int(current_match.group(1)) if current_match else 1
    next_ready = int(next_match.group(1)) if next_match else 2
    return {
        "current_completed_loop": current_completed,
        "next_ready_loop": next_ready,
        "executed_loops": [],
        "last_executed_loop": current_completed,
        "state_source": project_relative(TEMPLE_STATE_PATH),
        "status": f"loop {current_completed} complete / loop {next_ready} ready",
    }


def current_state() -> dict[str, Any]:
    if RUNNER_MANIFEST_PATH.exists():
        manifest = load_json(RUNNER_MANIFEST_PATH)
        return {
            "current_completed_loop": int(manifest["current_completed_loop"]),
            "next_ready_loop": int(manifest["next_ready_loop"]) if manifest["next_ready_loop"] is not None else None,
            "executed_loops": list(manifest.get("executed_loops", [])),
            "last_executed_loop": int(manifest.get("last_executed_loop", manifest["current_completed_loop"])),
            "state_source": project_relative(RUNNER_MANIFEST_PATH),
            "status": manifest.get("status", "runner-active"),
        }
    return extract_bootstrap_state_from_temple()


def initialize_runner_hysteresis() -> None:
    if EXEC_HYSTERESIS_JSON.exists():
        return
    if MOTION_HYSTERESIS_STATE_PATH.exists():
        state = load_json(MOTION_HYSTERESIS_STATE_PATH)
        state["seeded_for"] = "super_cycle_57_runner"
        state["seeded_at"] = utc_now()
    else:
        state = initial_hysteresis_state()
        state["seeded_for"] = "super_cycle_57_runner"
    write_json(EXEC_HYSTERESIS_JSON, state)


def loop_data() -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    loops = load_json(LOOP_LEDGER_PATH)
    packets = load_json(PACKET_REGISTRY_PATH)
    by_loop: dict[int, list[dict[str, Any]]] = {}
    for packet in packets:
        loop_index = int(str(packet["loop_id"]).replace("L", ""))
        by_loop.setdefault(loop_index, []).append(packet)
    for packet_list in by_loop.values():
        packet_list.sort(key=lambda item: item["packet_id"])
    return loops, by_loop


def loop_lookup(loop_index: int, loops: list[dict[str, Any]]) -> dict[str, Any]:
    for loop in loops:
        if int(loop["loop_index"]) == int(loop_index):
            return loop
    raise ValueError(f"Loop {loop_index} not found in installed ledger.")


def next_loop_text(loop_index: int, loops: list[dict[str, Any]]) -> str | None:
    next_index = loop_index + 1
    if next_index > len(loops):
        return None
    return loop_lookup(next_index, loops)["step_text"]


def current_loop_title(loop_index: int, loops: list[dict[str, Any]]) -> str:
    return loop_lookup(loop_index, loops)["step_text"]


def protocol_target_for_master(master_id: str) -> str:
    return {
        "A1": "hall",
        "A2": "temple",
        "A3": "runtime",
        "A4": "compression",
    }[master_id]


def protocol_state_label(chosen_action: str) -> str:
    return {
        "ACTIVATE_NOW": "active",
        "QUARANTINE": "quarantined",
        "COMPRESS_TO_SEED": "compressed",
        "HOLD": "reserve",
        "REFUSE_INADMISSIBLE": "blocked",
    }.get(chosen_action, "active")


def axes_for_action(action: str, target: str) -> dict[str, float]:
    base = {
        "truth_readiness": 0.9,
        "integration_yield": 0.8,
        "replay_cost": 0.2,
        "contradiction_heat": 0.1,
        "pressure_gradient": 0.55,
        "organ_adjacency": 0.8,
        "branch_burden": 0.2,
        "seed_value": 0.65,
        "closure_gain": 0.8,
        "heart_need": 0.7,
        "replay_readiness": 0.85,
        "failure_debt": 0.1,
        "risk": 0.2,
        "cost": 0.2,
    }
    if target == "runtime":
        base["organ_adjacency"] = 0.85
        base["pressure_gradient"] = 0.65
    if action == "ACTIVATE_NOW":
        base["pressure_gradient"] = 0.75
        base["closure_gain"] = 0.9
        base["heart_need"] = 0.82
        base["seed_value"] = 0.72
    elif action == "HOLD":
        base["pressure_gradient"] = 0.35
        base["closure_gain"] = 0.55
        base["heart_need"] = 0.45
    elif action == "REQUEST_WITNESSES":
        base["truth_readiness"] = 0.35
    elif action == "REPLAY_FIRST":
        base["replay_readiness"] = 0.25
    elif action == "ESCALATE_TO_COMMITTEE":
        base["branch_burden"] = 0.88
        base["pressure_gradient"] = 0.58
    elif action == "COMPRESS_TO_SEED":
        base["seed_value"] = 0.93
        base["closure_gain"] = 0.5
        base["heart_need"] = 0.48
        base["pressure_gradient"] = 0.4
    return base


def flags_for_action(action: str) -> dict[str, Any]:
    mapping = {
        "ACTIVATE_NOW": {},
        "HOLD": {"timing_not_lawful": True},
        "REQUEST_WITNESSES": {"truth_burden_unsatisfied": True},
        "REQUEST_HELP": {"role_mismatch": True},
        "REPLAY_FIRST": {"replay_dependency_unresolved": True},
        "QUARANTINE": {"blocker_intersection_forbidden": True},
        "COMPRESS_TO_SEED": {"circulation_blocked": True, "continuation_value_remaining": True},
        "ESCALATE_TO_COMMITTEE": {"committee_required": True},
        "REFUSE_INADMISSIBLE": {"omega_denied": True},
    }
    return deepcopy(mapping[action])


def queue_for_target(target: str) -> str:
    mapping = {
        "hall": "QuestBoard",
        "temple": "QuestBoard",
        "runtime": "Immune scheduler outputs",
        "compression": "Continuation seeds",
    }
    return mapping[target]


def organs_for_target(target: str, action: str) -> tuple[str, str]:
    if target == "hall":
        return ("BrainstemChamber", "QuestBoard")
    if target == "temple":
        return ("BrainstemChamber", "CommitteeChamber")
    if target == "runtime":
        return ("BrainstemChamber", "ReplayKernel" if action == "REPLAY_FIRST" else "PublicCommitSurface")
    return ("BrainstemChamber", "ContinuationSeedVault")


def packet_type_for_action(action: str, target: str) -> str:
    if action == "REPLAY_FIRST":
        return "replay_job"
    if action == "REQUEST_WITNESSES":
        return "witness_request"
    if action == "REQUEST_HELP":
        return "help_request"
    if action == "ESCALATE_TO_COMMITTEE":
        return "committee_escalation"
    if action == "COMPRESS_TO_SEED":
        return "continuation_seed"
    if action == "REFUSE_INADMISSIBLE":
        return "refusal_receipt"
    if target == "runtime":
        return "action_receipt"
    return "quest_packet"


def brainstem_state() -> dict[str, Any]:
    return {
        "G": "Q42 / TQ04 / Q50 / Q46 / Q02 route graph",
        "Pi": "loop-ranked pressure field under installed 57-cycle ledger",
        "Omega": {"status": "OK", "denied_packet_ids": ["Q02"]},
        "I": {
            "quarantine_classes": ["quarantine", "forbidden-class"],
            "unresolved_failure_classes": ["unresolved-failure"],
            "committee_pending_routes": [],
        },
        "R": {"replay_capacity": 1.0, "replay_memory_quality": 0.85},
    }


def candidate_from_packet(packet: dict[str, Any]) -> dict[str, Any]:
    action = packet["lawful_action"]
    target = packet["target"]
    source_organ, target_organ = organs_for_target(target, action)
    return {
        "id": packet["packet_id"],
        "title": packet["summary"],
        "source_queue": queue_for_target(target),
        "role_family": "super-cycle-57",
        "source_organ": source_organ,
        "target_organ": target_organ,
        "current_family": target,
        "truth_burden": "moderate",
        "packet_type_expected": packet_type_for_action(action, target),
        "continuation_seed": packet["candidate_front"].lower(),
        "dependencies": [] if action != "HOLD" else ["timing_window"],
        "blockers": list(packet.get("blocked_by", [])),
        "blocker_classes": [],
        "axes": axes_for_action(action, target),
        "flags": flags_for_action(action),
    }


def build_candidate_world(loop_packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "brainstem_state": brainstem_state(),
        "parameters": {"beta": 0.5},
        "hysteresis_state_path": str(EXEC_HYSTERESIS_JSON),
        "candidates": [candidate_from_packet(packet) for packet in loop_packets],
    }


def map_results_by_id(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {result["candidate_id"]: result for result in results}


def validate_loop_outputs(loop: dict[str, Any], loop_packets: list[dict[str, Any]], motion_result: dict[str, Any]) -> None:
    by_id = map_results_by_id(motion_result["results"])
    for packet in loop_packets:
        chosen = by_id[packet["packet_id"]]["chosen_action"]
        expected = packet["lawful_action"]
        if chosen != expected:
            raise ValueError(
                f"Loop L{loop['loop_index']:02d} packet {packet['packet_id']} expected {expected} but motion chose {chosen}."
            )


def build_execution_bundle(loop: dict[str, Any], loop_packets: list[dict[str, Any]], motion_result: dict[str, Any], loops: list[dict[str, Any]]) -> dict[str, Any]:
    results_by_id = map_results_by_id(motion_result["results"])
    packet_results = []
    for packet in loop_packets:
        result = results_by_id[packet["packet_id"]]
        branch_path = {"hall": "1111", "temple": "2222", "runtime": "3333", "compression": "4444"}[packet["target"]]
        shell_ref = shell_record_reference(loop["loop_index"], packet["target"], result["chosen_action"])
        packet_results.append(
            {
                "packet_id": packet["packet_id"],
                "source_master": packet["source_master"],
                "agent_id": protocol_agent_id(loop["loop_index"], packet["source_master"], 1, branch_path, LP57_MASTER_AGENT_SPECS[packet["source_master"]]["role_tag"]),
                "seat_addr_6d": seat_addr_6d(packet["source_master"], packet["target"], result["chosen_action"]),
                "shell_reference": shell_ref,
                "target": packet["target"],
                "candidate_front": packet["candidate_front"],
                "expected_action": packet["lawful_action"],
                "chosen_action": result["chosen_action"],
                "state": protocol_state_label(result["chosen_action"]),
                "reason": result["reason"],
                "planner_visible_promotion": packet["target"] in {"hall", "temple"} and result["chosen_action"] == "ACTIVATE_NOW",
                "score": result["score_vector"]["urgency_modulated_score"],
                "obligations": result["obligations"],
                "next_seed": result["next_seed"],
            }
        )
    packet_results.sort(key=lambda item: (-float(item["score"]), item["packet_id"]))

    runtime_packet = next(item for item in packet_results if item["target"] == "runtime")
    compression_packet = next(item for item in packet_results if item["target"] == "compression")
    hall_packet = next(item for item in packet_results if item["target"] == "hall")
    temple_packet = next(item for item in packet_results if item["target"] == "temple")

    runtime_writeback = {
        "kind": "RuntimeWritebackReceipt",
        "loop_id": f"L{loop['loop_index']:02d}",
        "action": runtime_packet["chosen_action"],
        "candidate_front": runtime_packet["candidate_front"],
        "summary": "Executed the runtime-facing bundle." if runtime_packet["chosen_action"] == "ACTIVATE_NOW" else "No runtime activation; explicit non-activation receipt emitted.",
        "obligations": runtime_packet["obligations"],
    }
    compression_delta = {
        "kind": "CompressionDelta",
        "loop_id": f"L{loop['loop_index']:02d}",
        "action": compression_packet["chosen_action"],
        "candidate_front": compression_packet["candidate_front"],
        "summary": compression_packet["reason"],
    }
    restart_seed = {
        "kind": "RestartSeed",
        "loop_id": f"L{loop['loop_index']:02d}",
        "seed": loop["restart_seed"],
        "motion_seed": compression_packet["next_seed"],
        "next_loop_text": next_loop_text(loop["loop_index"], loops),
    }
    master_targets = {
        "A1": hall_packet,
        "A2": temple_packet,
        "A3": runtime_packet,
        "A4": compression_packet,
    }
    master_receipts = {
        "A1": {
            "master": "Research/Synthesis",
            "summary": loop["master_receipts"]["A1"]["receipt"],
            "outputs": loop["master_receipts"]["A1"]["outputs"],
        },
        "A2": {
            "master": "Planner/Governor",
            "summary": "Validated packet actions through MotionConstitution_L1 and decided visible promotions.",
            "outputs": [hall_packet["chosen_action"], temple_packet["chosen_action"], runtime_packet["chosen_action"], compression_packet["chosen_action"]],
        },
        "A3": {"master": "Worker/Adventurer", "summary": runtime_writeback["summary"], "outputs": [runtime_packet["candidate_front"], runtime_packet["chosen_action"]]},
        "A4": {"master": "Pruner/Compressor", "summary": compression_delta["summary"], "outputs": [compression_packet["candidate_front"], compression_packet["chosen_action"], restart_seed["seed"]]},
    }
    for master_id, receipt in master_receipts.items():
        packet = master_targets[master_id]
        branch_path = {"hall": "1111", "temple": "2222", "runtime": "3333", "compression": "4444"}[packet["target"]]
        role_tag = LP57_MASTER_AGENT_SPECS[master_id]["role_tag"]
        receipt["agent_id"] = protocol_agent_id(loop["loop_index"], master_id, 1, branch_path, role_tag)
        receipt["seat_addr_6d"] = seat_addr_6d(master_id, packet["target"], packet["chosen_action"])
        receipt["shell_reference"] = packet["shell_reference"]
        receipt["target"] = packet["target"]
        receipt["candidate_front"] = packet["candidate_front"]
        receipt["chosen_action"] = packet["chosen_action"]
        receipt["linked_quests"] = [packet["candidate_front"]]
        receipt["state"] = protocol_state_label(packet["chosen_action"])
    return {
        "loop_index": loop["loop_index"],
        "loop_id": f"L{loop['loop_index']:02d}",
        "pass_title": loop["pass_title"],
        "step_text": loop["step_text"],
        "awakening_refresh": loop["awakening_refresh"],
        "packet_results": packet_results,
        "hall_decision": hall_packet,
        "temple_decision": temple_packet,
        "runtime_writeback": runtime_writeback,
        "compression_delta": compression_delta,
        "restart_seed": restart_seed,
        "master_receipts": master_receipts,
        "motion_result": motion_result,
    }


def ensure_required_outputs(bundle: dict[str, Any]) -> None:
    required = [
        bundle.get("packet_results"),
        bundle.get("hall_decision"),
        bundle.get("temple_decision"),
        bundle.get("runtime_writeback"),
        bundle.get("compression_delta"),
        bundle.get("restart_seed"),
        bundle.get("master_receipts"),
    ]
    if any(item is None for item in required):
        raise ValueError(f"{bundle['loop_id']} is missing one or more required output objects.")
    if len(bundle["master_receipts"]) != 4:
        raise ValueError(f"{bundle['loop_id']} is missing master receipts.")


def render_loop_receipt(bundle: dict[str, Any]) -> str:
    return (
        f"# Executed {bundle['loop_id']} Receipt\n\n"
        f"- Pass: `{bundle['pass_title']}`\n"
        f"- Step: {bundle['step_text']}\n"
        f"- Hall decision: `{bundle['hall_decision']['chosen_action']}` -> `{bundle['hall_decision']['candidate_front']}`\n"
        f"- Temple decision: `{bundle['temple_decision']['chosen_action']}` -> `{bundle['temple_decision']['candidate_front']}`\n"
        f"- Runtime decision: `{bundle['runtime_writeback']['action']}`\n"
        f"- Compression decision: `{bundle['compression_delta']['action']}`\n"
        f"- Board-agent delta refresh: `{bundle['awakening_refresh']['board_agent_delta']}`\n"
        f"- Full 24-note bundle refresh: `{bundle['awakening_refresh']['full_bundle_refresh']}`\n"
        f"- Pass-boundary bundle: `{bundle['awakening_refresh']['pass_boundary_bundle']}`\n"
        f"- Restart seed: `{bundle['restart_seed']['seed']}`\n"
    )


def render_master_receipt(loop_id: str, master_id: str, receipt: dict[str, Any]) -> str:
    outputs = "\n".join(f"- `{item}`" for item in receipt["outputs"])
    return (
        f"# {loop_id} {master_id} Receipt\n\n"
        f"- Master: `{receipt['master']}`\n"
        f"- Agent ID: `{receipt['agent_id']}`\n"
        f"- Seat address: `{receipt['seat_addr_6d']}`\n"
        f"- Shell record: `{receipt['shell_reference']['record_id']}` @ `{receipt['shell_reference']['shell_slot_label']}`\n"
        f"- Target: `{receipt['target']}`\n"
        f"- Candidate front: `{receipt['candidate_front']}`\n"
        f"- Chosen action: `{receipt['chosen_action']}`\n"
        f"- State: `{receipt['state']}`\n"
        f"- Summary: {receipt['summary']}\n\n"
        f"## Outputs\n{outputs}\n"
    )


def render_decision(title: str, packet: dict[str, Any]) -> str:
    return (
        f"# {title}\n\n"
        f"- Candidate front: `{packet['candidate_front']}`\n"
        f"- Chosen action: `{packet['chosen_action']}`\n"
        f"- Reason: {packet['reason']}\n"
        f"- Planner-only visible promotion law: `True`\n"
        f"- Visible promotion: `{packet['planner_visible_promotion']}`\n"
    )


def render_runtime_receipt(runtime_writeback: dict[str, Any]) -> str:
    obligations = "\n".join(f"- `{item}`" for item in runtime_writeback["obligations"])
    return (
        f"# {runtime_writeback['loop_id']} Runtime Writeback\n\n"
        f"- Action: `{runtime_writeback['action']}`\n"
        f"- Candidate front: `{runtime_writeback['candidate_front']}`\n"
        f"- Summary: {runtime_writeback['summary']}\n\n## Obligations\n{obligations}\n"
    )


def render_compression_delta(delta: dict[str, Any]) -> str:
    return f"# {delta['loop_id']} Compression Delta\n\n- Action: `{delta['action']}`\n- Candidate front: `{delta['candidate_front']}`\n- Summary: {delta['summary']}\n"


def build_protocol_ledger_entries(bundle: dict[str, Any], output_paths: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    linked_agents = [receipt["agent_id"] for receipt in bundle["master_receipts"].values()]
    common_witness_refs = [
        project_relative(RUNNER_MANIFEST_PATH),
        project_relative(INSTALLED_MANIFEST_PATH),
        project_relative(LOOP_LEDGER_PATH),
    ]
    ledger_entries: list[dict[str, Any]] = []
    coordinate_entries: list[dict[str, Any]] = []
    packet_by_target = {packet["target"]: packet for packet in bundle["packet_results"]}
    for master_id, receipt in bundle["master_receipts"].items():
        packet = packet_by_target[receipt["target"]]
        witness_refs = common_witness_refs + [
            receipt["shell_reference"]["prior_metro_route_witness"] if "prior_metro_route_witness" in receipt["shell_reference"] else "ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/13_dense_65_shell_registry.json",
            "ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/14_rqt_transfer_signature_registry.json",
        ]
        entry = seeded_ledger_entry(
            loop_index=bundle["loop_index"],
            master_id=master_id,
            target=receipt["target"],
            chosen_action=receipt["chosen_action"],
            candidate_front=receipt["candidate_front"],
            pass_id=f"P{((bundle['loop_index'] - 1) // 9) + 1}",
            pass_title=bundle["pass_title"],
            source_region="ACTIVE_NERVOUS_SYSTEM/17_SUPER_CYCLE_57",
            summary=receipt["summary"],
            reason=packet["reason"],
            integration_gain=f"{bundle['pass_title']} advanced `{receipt['candidate_front']}` through `{receipt['chosen_action']}`.",
            compression_gain=f"{bundle['compression_delta']['action']} kept loop `{bundle['loop_id']}` bounded.",
            unresolved_followups=[bundle["restart_seed"]["seed"]],
            linked_quests=receipt["linked_quests"],
            linked_agents=linked_agents,
            witness_refs=witness_refs,
            revision_confidence=0.93,
            timestamp_internal=utc_now(),
            state=receipt["state"],
        )
        ledger_entries.append(entry)
        coordinate_entries.append(
            {
                "entity_type": "master_receipt",
                "loop_id": bundle["loop_id"],
                "agent_id": entry["agent_id"],
                "seat_addr_6d": entry["seat_addr_6d"],
                "coordinate_stamp": entry["coordinate_stamp"],
                "shell_reference": receipt["shell_reference"],
                "candidate_front": receipt["candidate_front"],
                "state": receipt["state"],
            }
        )

    loop_delta = {
        "loop_id": bundle["loop_id"],
        "pass_title": bundle["pass_title"],
        "step_text": bundle["step_text"],
        "hall_decision": bundle["hall_decision"]["chosen_action"],
        "temple_decision": bundle["temple_decision"]["chosen_action"],
        "runtime_decision": bundle["runtime_writeback"]["action"],
        "compression_decision": bundle["compression_delta"]["action"],
        "restart_seed": bundle["restart_seed"]["seed"],
        "ledger_output_paths": output_paths,
        "coordinate_dimensions": COORDINATE_DIMENSIONS,
        "ledger_fields": LEDGER_FIELDS,
        "sigma_path": SIGMA_PATH,
        "shell_truth": SHELL_TRUTH,
    }
    return ledger_entries, coordinate_entries, loop_delta


def update_protocol_ledgers(bundle: dict[str, Any], output_paths: dict[str, Any]) -> dict[str, str]:
    for path in [LP57_MASTER_LEDGER_JSON, LP57_COORDINATE_REGISTRY_JSON, LP57_LOOP_DELTA_JSON]:
        path.parent.mkdir(parents=True, exist_ok=True)
    if LP57_MASTER_LEDGER_JSON.exists():
        ledger_payload = load_json(LP57_MASTER_LEDGER_JSON)
    elif SELF_LP57_MASTER_LEDGER_JSON.exists():
        ledger_payload = load_json(SELF_LP57_MASTER_LEDGER_JSON)
    else:
        ledger_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "fields": LEDGER_FIELDS, "entries": []}
    if LP57_COORDINATE_REGISTRY_JSON.exists():
        coord_payload = load_json(LP57_COORDINATE_REGISTRY_JSON)
    elif SELF_LP57_COORDS_JSON.exists():
        coord_payload = load_json(SELF_LP57_COORDS_JSON)
    else:
        coord_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "dimensions": COORDINATE_DIMENSIONS, "entries": []}
    if LP57_LOOP_DELTA_JSON.exists():
        delta_payload = load_json(LP57_LOOP_DELTA_JSON)
    elif SELF_LP57_DELTA_JSON.exists():
        delta_payload = load_json(SELF_LP57_DELTA_JSON)
    else:
        delta_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "records": []}

    ledger_entries, coordinate_entries, loop_delta = build_protocol_ledger_entries(bundle, output_paths)
    existing_agent_ids = {entry["agent_id"] for entry in ledger_payload.get("entries", [])}
    for entry in ledger_entries:
        if entry["agent_id"] not in existing_agent_ids:
            ledger_payload["entries"].append(entry)
    existing_coord_keys = {(entry["loop_id"], entry["agent_id"]) for entry in coord_payload.get("entries", [])}
    for entry in coordinate_entries:
        key = (entry["loop_id"], entry["agent_id"])
        if key not in existing_coord_keys:
            coord_payload["entries"].append(entry)
    existing_loops = {entry["loop_id"] for entry in delta_payload.get("records", [])}
    if loop_delta["loop_id"] not in existing_loops:
        delta_payload["records"].append(loop_delta)

    ledger_payload["generated_at"] = utc_now()
    coord_payload["generated_at"] = utc_now()
    delta_payload["generated_at"] = utc_now()
    write_json(LP57_MASTER_LEDGER_JSON, ledger_payload)
    write_json(LP57_COORDINATE_REGISTRY_JSON, coord_payload)
    write_json(LP57_LOOP_DELTA_JSON, delta_payload)
    write_json(SELF_LP57_MASTER_LEDGER_JSON, ledger_payload)
    write_json(SELF_LP57_COORDS_JSON, coord_payload)
    write_json(SELF_LP57_DELTA_JSON, delta_payload)

    return {
        "master_agent_ledger": project_relative(LP57_MASTER_LEDGER_JSON),
        "coordinate_registry": project_relative(LP57_COORDINATE_REGISTRY_JSON),
        "loop_delta_receipts": project_relative(LP57_LOOP_DELTA_JSON),
    }


def write_loop_outputs(bundle: dict[str, Any], candidate_world: dict[str, Any]) -> dict[str, Any]:
    loop_slug = f"loop_{bundle['loop_index']:02d}"
    loop_receipt_path = LOOP_RECEIPTS_DIR / f"{loop_slug}.md"
    write_text(loop_receipt_path, render_loop_receipt(bundle))

    master_paths: dict[str, str] = {}
    for master_id, receipt in bundle["master_receipts"].items():
        path = MASTER_RECEIPTS_DIR / f"{loop_slug}_{master_id.lower()}.md"
        write_text(path, render_master_receipt(bundle["loop_id"], master_id, receipt))
        master_paths[master_id] = project_relative(path)

    packet_ledger_path = PACKET_LEDGERS_DIR / f"{loop_slug}.json"
    write_json(packet_ledger_path, bundle["packet_results"])
    candidate_world_path = CANDIDATE_WORLDS_DIR / f"{loop_slug}.json"
    write_json(candidate_world_path, candidate_world)
    motion_eval_path = MOTION_EVALS_DIR / f"{loop_slug}.json"
    write_json(motion_eval_path, bundle["motion_result"])
    hall_decision_path = HALL_DECISIONS_DIR / f"{loop_slug}.md"
    write_text(hall_decision_path, render_decision("Hall Promotion Decision", bundle["hall_decision"]))
    temple_decision_path = TEMPLE_DECISIONS_DIR / f"{loop_slug}.md"
    write_text(temple_decision_path, render_decision("Temple Promotion Decision", bundle["temple_decision"]))
    runtime_receipt_path = RUNTIME_RECEIPTS_DIR / f"{loop_slug}.md"
    write_text(runtime_receipt_path, render_runtime_receipt(bundle["runtime_writeback"]))
    compression_delta_path = COMPRESSION_DELTAS_DIR / f"{loop_slug}.md"
    write_text(compression_delta_path, render_compression_delta(bundle["compression_delta"]))
    restart_seed_path = RESTART_SEEDS_DIR / f"{loop_slug}.json"
    write_json(restart_seed_path, bundle["restart_seed"])

    return {
        "loop_receipt": project_relative(loop_receipt_path),
        "master_receipts": master_paths,
        "packet_ledger": project_relative(packet_ledger_path),
        "candidate_world": project_relative(candidate_world_path),
        "motion_evaluation": project_relative(motion_eval_path),
        "hall_decision": project_relative(hall_decision_path),
        "temple_decision": project_relative(temple_decision_path),
        "runtime_receipt": project_relative(runtime_receipt_path),
        "compression_delta": project_relative(compression_delta_path),
        "restart_seed": project_relative(restart_seed_path),
    }


def write_progress_state(state: dict[str, Any], loops: list[dict[str, Any]]) -> None:
    progress_json = {
        "generated_at": utc_now(),
        "live_docs_blocked": True,
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "executed_loops": state["executed_loops"],
        "last_executed_loop": state["last_executed_loop"],
        "status": state["status"],
        "current_loop_title": current_loop_title(state["current_completed_loop"], loops),
        "next_loop_title": current_loop_title(state["next_ready_loop"], loops) if state["next_ready_loop"] else None,
    }
    write_json(EXEC_PROGRESS_JSON, progress_json)
    next_label = f"L{state['next_ready_loop']:02d}" if state["next_ready_loop"] else "epoch-complete"
    executed = ", ".join(f"L{loop:02d}" for loop in state["executed_loops"]) or "none"
    write_text(
        EXEC_PROGRESS_MD,
        "\n".join(
            [
                "# Super-Cycle 57 Runner Progress",
                "",
                f"- Generated at: `{progress_json['generated_at']}`",
                f"- Current completed loop: `L{state['current_completed_loop']:02d}`",
                f"- Next ready loop: `{next_label}`",
                f"- Status: `{state['status']}`",
                f"- Executed loops this runner: `{executed}`",
            ]
        ),
    )


def runner_status_string(state: dict[str, Any]) -> str:
    if state["next_ready_loop"] is None:
        return f"L{state['current_completed_loop']:02d} complete / epoch closed"
    return f"L{state['current_completed_loop']:02d} complete / L{state['next_ready_loop']:02d} ready"


def control_block_markdown(state: dict[str, Any], loops: list[dict[str, Any]], bundle: dict[str, Any] | None) -> str:
    completed = f"L{state['current_completed_loop']:02d}"
    next_ready = f"L{state['next_ready_loop']:02d}" if state["next_ready_loop"] else "NONE"
    last_step = current_loop_title(state["current_completed_loop"], loops)
    restart_seed = bundle["restart_seed"]["seed"] if bundle else loop_lookup(state["current_completed_loop"], loops)["restart_seed"]
    return "\n".join(
        [
            "## LP-57Omega Quad-Agent Conductor",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            f"- Status: `{runner_status_string(state)}`",
            f"- Canonical authority: `{PROTOCOL_ID}`",
            "- Compatibility mirrors: `NEXT57`, `Q51/TQ07`, `FA57`",
            f"- Current completed loop: `{completed}`",
            f"- Next ready loop: `{next_ready}`",
            "- Hall macro front: `Q51`",
            "- Temple macro front: `TQ07`",
            "- Active membrane: `Q41 / TQ06`",
            "- Live feeder stack: `Q42 / TQ04 / Q50 / Q46 / Q02`",
            "- Visible promotion law: `1 Hall + 1 Temple + 1 runtime + 1 compression`",
            f"- Last completed step: `{last_step}`",
            f"- Derived restart seed: `{restart_seed}`",
        ]
    )


def update_temple_state_markers(state: dict[str, Any], loops: list[dict[str, Any]], bundle: dict[str, Any] | None) -> None:
    text = TEMPLE_STATE_PATH.read_text(encoding="utf-8")
    top_block = control_block_markdown(state, loops, bundle)
    temple_block = "\n".join(
        [
            "## LP-57Omega Temple State",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs gate: `BLOCKED`",
            "- Temple-facing frontier: `TQ07`",
            "- Hall coupling frontier: `Q51`",
            "- Active membrane: `Q41 / TQ06`",
            "- Carried Hall feeder: `Q42`",
            "- Immediate deeper receiver: `TQ04`",
            "- Runtime frontier: `Q50`",
            "- Reserve frontier: `Q46`",
            "- External blocker: `Q02`",
            "- Visible promotion law: `1 Hall + 1 Temple + 1 runtime + 1 compression`",
            f"- Current completed loop: `L{state['current_completed_loop']:02d}`",
            f"- Next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
            f"- Restart seed: `{bundle['restart_seed']['seed'] if bundle else loop_lookup(state['current_completed_loop'], loops)['restart_seed']}`",
        ]
    )
    text = replace_block(text, "<!-- FOUR_AGENT_57_LOOP_PROGRAM:START -->", "<!-- FOUR_AGENT_57_LOOP_PROGRAM:END -->", top_block)
    text = replace_block(
        text,
        "<!-- MASTER_LOOP_57_TEMPLE_STATE:START -->",
        "<!-- MASTER_LOOP_57_TEMPLE_STATE:END -->",
        temple_block,
    )
    text = replace_line(text, r"Temple Status:\s*`[^`]+`", "Temple Status: `ONLINE / RUNNER-GOVERNED`")
    write_text(TEMPLE_STATE_PATH, text)


def update_temple_57_state(state: dict[str, Any], loops: list[dict[str, Any]], bundle: dict[str, Any] | None) -> None:
    payload = {
        "generated_at": utc_now(),
        "docs_gate": "BLOCKED",
        "truth": "OK",
        "status": runner_status_string(state),
        "current_completed_loop": f"L{state['current_completed_loop']:02d}",
        "next_ready_loop": f"L{state['next_ready_loop']:02d}" if state["next_ready_loop"] else None,
        "current_step": current_loop_title(state["current_completed_loop"], loops),
        "next_step": current_loop_title(state["next_ready_loop"], loops) if state["next_ready_loop"] else None,
        "hall_front": "Q51",
        "temple_front": "TQ07",
        "active_membrane": "Q41 / TQ06",
        "control_stack": CONTROL_STACK,
        "executed_loops": [f"L{loop:02d}" for loop in state["executed_loops"]],
        "restart_seed": bundle["restart_seed"]["seed"] if bundle else loop_lookup(state["current_completed_loop"], loops)["restart_seed"],
        "live_docs_blocked": True,
    }
    write_json(TEMPLE_57_STATE_JSON, payload)
    write_text(
        TEMPLE_57_STATE_MD,
        "\n".join(
            [
                "# Super-Cycle 57 Temple Runner State",
                "",
                f"- Generated: `{payload['generated_at']}`",
                "- Docs Gate: `BLOCKED`",
                f"- Status: `{payload['status']}`",
                f"- Current completed loop: `{payload['current_completed_loop']}`",
                f"- Next ready loop: `{payload['next_ready_loop'] or 'NONE'}`",
                f"- Current step: {payload['current_step']}",
                f"- Next step: {payload['next_step'] or 'epoch-complete'}",
                "- Hall front: `Q51`",
                "- Temple front: `TQ07`",
                "- Active membrane: `Q41 / TQ06`",
                f"- Restart seed: `{payload['restart_seed']}`",
            ]
        ),
    )


def update_active_run(state: dict[str, Any], loops: list[dict[str, Any]], bundle: dict[str, Any] | None) -> None:
    text = ACTIVE_RUN_PATH.read_text(encoding="utf-8")
    mirror_block = "\n".join(
        [
            "## Four-Agent 57-Loop Program Compatibility Mirror",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            "- Status: `COMPATIBILITY_MIRROR / RUNNER-SYNCED`",
            f"- Canonical authority: `{PROTOCOL_ID}`",
            "- Mirror-only families: `NEXT57`, `FOUR_AGENT_57_LOOP_PROGRAM`, `Q51/TQ07`, `FA57`",
            "- Independent restart seeds: `DISALLOWED`",
            f"- Derived restart seed: `{bundle['restart_seed']['seed'] if bundle else loop_lookup(state['current_completed_loop'], loops)['restart_seed']}`",
            "- Preserve live feeders: `Q42, Q46, TQ04, TQ06, Q50`",
            "- Blocked external front: `Q02`",
        ]
    )
    current_block = "\n".join(
        [
            "## LP-57Omega Four-Agent Corpus Cycle",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Truth: `OK`",
            "- Docs Gate: `BLOCKED`",
            "- Supervisory membrane: `Prime/Guildmaster`",
            f"- Canonical authority: `{PROTOCOL_ID}`",
            "- Compatibility mirrors: `NEXT57`, `FOUR_AGENT_57_LOOP_PROGRAM`, `Q51/TQ07`, `FA57`",
            "- Master roles: `A1 Research/Synthesis`, `A2 Planner/Governor`, `A3 Worker/Adventurer`, `A4 Pruner/Compressor`",
            "- Nested seat law: `4 x 4096 virtual seats; 256 active/master; 1024 active total`",
            "- Visible promotion law: `1 Hall + 1 Temple + 1 runtime + 1 compression`",
            f"- Current completed loop: `L{state['current_completed_loop']:02d}`",
            f"- Next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
            "- Preserved fronts: `Q42`, `Q46`, `TQ04`, `TQ06`, `Q50`, `Q51`, `TQ07`",
            "- Blocked front: `Q02`",
            f"- Restart seed: `{bundle['restart_seed']['seed'] if bundle else loop_lookup(state['current_completed_loop'], loops)['restart_seed']}`",
        ]
    )
    text = replace_block(text, "<!-- FOUR_AGENT_57_LOOP_PROGRAM:START -->", "<!-- FOUR_AGENT_57_LOOP_PROGRAM:END -->", mirror_block)
    text = replace_block(text, "<!-- NEXT57_FOUR_AGENT_CYCLE:START -->", "<!-- NEXT57_FOUR_AGENT_CYCLE:END -->", current_block)
    write_text(ACTIVE_RUN_PATH, text)


def update_quest_board(state: dict[str, Any], loops: list[dict[str, Any]], bundle: dict[str, Any]) -> None:
    text = QUEST_BOARD_PATH.read_text(encoding="utf-8")
    mirror_block = "\n".join(
        [
            "## Four-Agent 57-Loop Program Compatibility Mirror",
            "",
            f"- Date: `{utc_now()[:10]}`",
            "- Docs Gate: `BLOCKED`",
            "- Status: `COMPATIBILITY_MIRROR / RUNNER-SYNCED`",
            f"- Canonical authority: `{PROTOCOL_ID}`",
            "- Compatibility family: `NEXT57`",
            "- Independent restart seeds: `DISALLOWED`",
            f"- Derived restart seed: `{bundle['restart_seed']['seed']}`",
            "- Mirror role: preserve backwards links only; do not treat this block as an active frontier",
        ]
    )
    hall_block = "\n".join(
        [
            "## Hall Quest Compatibility Mirror",
            "",
            "- status: `COMPATIBILITY_MIRROR / RUNNER-SYNCED`",
            f"- canonical authority: `{PROTOCOL_ID}`",
            "- mirror target: `Q51 legacy hall family`",
            "- independent restart seeds: `DISALLOWED`",
            f"- derived restart seed: `{bundle['restart_seed']['seed']}`",
        ]
    )
    runner_section = [
        f"- Status: `{runner_status_string(state)}`",
        f"- Current completed loop: `L{state['current_completed_loop']:02d}`",
        f"- Next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
        f"- Hall decision: `{bundle['hall_decision']['chosen_action']}` -> `{bundle['hall_decision']['candidate_front']}`",
        f"- Temple decision: `{bundle['temple_decision']['chosen_action']}` -> `{bundle['temple_decision']['candidate_front']}`",
        f"- Runtime decision: `{bundle['runtime_writeback']['action']}` -> `{bundle['runtime_writeback']['candidate_front']}`",
        f"- Compression decision: `{bundle['compression_delta']['action']}` -> `{bundle['compression_delta']['candidate_front']}`",
        "- Planner-only visible promotion law: `True`",
        "- Visible promotion ceiling: `1 Hall + 1 Temple + 1 runtime + 1 compression`",
        f"- Restart seed: `{bundle['restart_seed']['seed']}`",
    ]
    text = text.replace("## NEXT57 Runner Execution State", "## LP-57Omega Runner Execution State")
    text = replace_block(text, "<!-- FOUR_AGENT_57_LOOP_PROGRAM:START -->", "<!-- FOUR_AGENT_57_LOOP_PROGRAM:END -->", mirror_block)
    text = replace_block(text, "<!-- MASTER_LOOP_57_HALL_QUEST:START -->", "<!-- MASTER_LOOP_57_HALL_QUEST:END -->", hall_block)
    text = replace_or_append_section(text, "## LP-57Omega Runner Execution State", runner_section)
    write_text(QUEST_BOARD_PATH, text)


def update_hall_program(state: dict[str, Any], bundle: dict[str, Any]) -> None:
    text = HALL_PROGRAM_PATH.read_text(encoding="utf-8")
    lines = [
        f"- Loop: `L{state['current_completed_loop']:02d}`",
        f"- Next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
        f"- Pass: `{bundle['pass_title']}`",
        f"- Step: {bundle['step_text']}",
        f"- Hall decision: `{bundle['hall_decision']['chosen_action']}` -> `{bundle['hall_decision']['candidate_front']}`",
        f"- Temple decision: `{bundle['temple_decision']['chosen_action']}` -> `{bundle['temple_decision']['candidate_front']}`",
        f"- Runtime decision: `{bundle['runtime_writeback']['action']}`",
        f"- Restart seed: `{bundle['restart_seed']['seed']}`",
    ]
    text = replace_or_append_section(text, "## Current Loop", lines)
    write_text(HALL_PROGRAM_PATH, text)


def update_temple_program(state: dict[str, Any], bundle: dict[str, Any]) -> None:
    text = TEMPLE_PROGRAM_PATH.read_text(encoding="utf-8")
    lines = [
        f"- current completed loop: `L{state['current_completed_loop']:02d}`",
        f"- next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
        f"- current pass: `{bundle['pass_title']}`",
        f"- current step: {bundle['step_text']}",
        f"- hall decision: `{bundle['hall_decision']['chosen_action']}`",
        f"- temple decision: `{bundle['temple_decision']['chosen_action']}`",
        f"- runtime decision: `{bundle['runtime_writeback']['action']}`",
        f"- restart seed: `{bundle['restart_seed']['seed']}`",
    ]
    text = replace_or_append_section(text, "## Current Decree State", lines)
    write_text(TEMPLE_PROGRAM_PATH, text)


def update_self_registry(state: dict[str, Any], bundle: dict[str, Any] | None) -> None:
    registry = load_json(SELF_REGISTRY_JSON)
    registry["generated_at"] = utc_now()[:10]
    registry["truth"] = "OK"
    registry["docs_gate"] = "BLOCKED"
    registry["status"] = runner_status_string(state)
    registry["hall_front"] = "Q51"
    registry["temple_front"] = "TQ07"
    registry["active_membrane"] = "Q41 / TQ06"
    registry["active_local_subfront"] = "Q42"
    registry["next_temple_handoff"] = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
    registry["reserve_frontier"] = "Q46"
    registry["restart_seed"] = bundle["restart_seed"]["seed"] if bundle else registry.get("restart_seed")
    for loop in registry.get("loops", []):
        loop_number = int(loop.get("loop_number", str(loop.get("loop_id", "L0")).replace("L", "")))
        if loop_number <= state["current_completed_loop"]:
            loop["status"] = "COMPLETE"
        elif state["next_ready_loop"] and loop_number == state["next_ready_loop"]:
            loop["status"] = "READY"
        else:
            loop["status"] = "QUEUED"
    write_json(SELF_REGISTRY_JSON, registry)


def append_receipt_ledger(bundle: dict[str, Any], output_paths: dict[str, Any]) -> None:
    if SELF_RECEIPT_LEDGER_MD.exists():
        text = SELF_RECEIPT_LEDGER_MD.read_text(encoding="utf-8")
    else:
        text = "# 57-Loop Receipt Ledger\n"
    heading = f"## {bundle['loop_id']} Receipt"
    if heading in text:
        return
    body = "\n".join(
        [
            heading,
            "",
            f"- Pass: `{bundle['pass_title']}`",
            f"- Step: {bundle['step_text']}",
            f"- Hall decision: `{bundle['hall_decision']['chosen_action']}` -> `{bundle['hall_decision']['candidate_front']}`",
            f"- Temple decision: `{bundle['temple_decision']['chosen_action']}` -> `{bundle['temple_decision']['candidate_front']}`",
            f"- Runtime decision: `{bundle['runtime_writeback']['action']}`",
            f"- Compression decision: `{bundle['compression_delta']['action']}`",
            f"- Restart seed: `{bundle['restart_seed']['seed']}`",
            f"- Loop receipt: `{output_paths['loop_receipt']}`",
        ]
    )
    write_text(SELF_RECEIPT_LEDGER_MD, text.rstrip() + "\n\n" + body + "\n")


def update_program_95_json(state: dict[str, Any], bundle: dict[str, Any] | None) -> None:
    payload = load_json(PROGRAM_95_JSON)
    payload["generated_at"] = utc_now()
    payload["GeneratedAt"] = utc_now()
    payload["docs_gate_status"] = "BLOCKED"
    if "DocsGate" in payload and isinstance(payload["DocsGate"], dict):
        payload["DocsGate"]["Status"] = "BLOCKED"
    payload["CurrentLoop"] = f"L{state['current_completed_loop']:02d}"
    payload["current_completed_loop"] = state["current_completed_loop"]
    payload["NextLoop"] = f"L{state['next_ready_loop']:02d}" if state["next_ready_loop"] else None
    payload["next_ready_loop"] = state["next_ready_loop"]
    payload["CurrentStatus"] = runner_status_string(state)
    payload["status"] = runner_status_string(state)
    if bundle:
        payload["CurrentWave"] = bundle["pass_title"]
        payload["derived_restart_seed"] = bundle["restart_seed"]["seed"]
    for record in payload.get("LoopRecords", []):
        loop_number = int(record["LoopNumber"])
        if loop_number <= state["current_completed_loop"]:
            record["Status"] = "complete"
        elif state["next_ready_loop"] and loop_number == state["next_ready_loop"]:
            record["Status"] = "ready"
        else:
            record["Status"] = "planned"
    write_json(PROGRAM_95_JSON, payload)


def update_active_readme(state: dict[str, Any]) -> None:
    text = ACTIVE_README_PATH.read_text(encoding="utf-8")
    section_lines = [
        f"- Status: `{runner_status_string(state)}`",
        "- Runtime manifest: `06_RUNTIME/19_super_cycle_57_runner_manifest.json`",
        f"- Current completed loop: `L{state['current_completed_loop']:02d}`",
        f"- Next ready loop: `{f'L{state['next_ready_loop']:02d}' if state['next_ready_loop'] else 'NONE'}`",
        "- Hall macro front: `Q51`",
        "- Temple macro front: `TQ07`",
        "- Active membrane: `Q41 / TQ06`",
        "- Live Google Docs: `BLOCKED`",
    ]
    text = replace_or_append_section(text, "## Super-Cycle 57 Runner State", section_lines)
    write_text(ACTIVE_README_PATH, text)


def update_full_stack_manifest(state: dict[str, Any]) -> None:
    manifest = load_json(FULL_STACK_MANIFEST_PATH)
    command_manifest = command_protocol_manifest()
    manifest["generated_at"] = utc_now()
    manifest["live_docs_blocked"] = True
    manifest.setdefault("layers", {})
    manifest["layers"]["super_cycle_57_runner"] = {
        "manifest": "06_RUNTIME/19_super_cycle_57_runner_manifest.json",
        "protocol_id": PROTOCOL_ID,
        "status": runner_status_string(state),
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "executed_loop_count": len(state["executed_loops"]),
        "hall_macro_front": "Q51",
        "temple_macro_front": "TQ07",
        "active_membrane": "Q41 / TQ06",
        "liminal_identity_enabled": True,
        "shell_reference_ready": True,
        "sigma_path": SIGMA_PATH,
        "shell_truth": SHELL_TRUTH,
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "command_protocol_ready": bool(command_manifest),
        "command_sensor_root": command_manifest["sensor_root"] if command_manifest else None,
        "command_watch_backend": command_manifest["watch_backend"] if command_manifest else None,
        "command_truth_status": command_manifest["truth_status"] if command_manifest else None,
        "command_packet_count": command_manifest["packet_count"] if command_manifest else 0,
        "command_capillary_edge_count": command_manifest["capillary_edge_count"] if command_manifest else 0,
        "live_docs_blocked": True,
    }
    write_json(FULL_STACK_MANIFEST_PATH, manifest)


def build_runner_manifest(
    state: dict[str, Any],
    loops: list[dict[str, Any]],
    bundle: dict[str, Any] | None,
    output_paths: dict[str, Any] | None,
) -> dict[str, Any]:
    command_manifest = command_protocol_manifest()
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "status": runner_status_string(state),
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(),
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "last_executed_loop": state["last_executed_loop"],
        "executed_loops": state["executed_loops"],
        "loop_count": len(loops),
        "hall_macro_front": "Q51",
        "temple_macro_front": "TQ07",
        "active_membrane": "Q41 / TQ06",
        "control_stack": CONTROL_STACK,
        "seat_law": SEAT_LAW,
        "visible_promotion_law": VISIBLE_PROMOTION_LIMIT,
        "liminal_identity_enabled": True,
        "shell_reference_ready": True,
        "sigma_path": SIGMA_PATH,
        "shell_truth": SHELL_TRUTH,
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "coordinate_dimensions": COORDINATE_DIMENSIONS,
        "ledger_fields": LEDGER_FIELDS,
        "command_protocol_manifest": "06_RUNTIME/21_command_protocol_manifest.json" if command_manifest else None,
        "command_protocol_ready": bool(command_manifest),
        "command_sensor_root": command_manifest["sensor_root"] if command_manifest else None,
        "command_watch_backend": command_manifest["watch_backend"] if command_manifest else None,
        "command_truth_status": command_manifest["truth_status"] if command_manifest else None,
        "command_packet_count": command_manifest["packet_count"] if command_manifest else 0,
        "command_capillary_edge_count": command_manifest["capillary_edge_count"] if command_manifest else 0,
        "q02_blocked": True,
        "current_completed_step": current_loop_title(state["current_completed_loop"], loops),
        "next_ready_step": current_loop_title(state["next_ready_loop"], loops) if state["next_ready_loop"] else None,
        "execution_root": project_relative(EXECUTION_ROOT),
        "output_contract": [
            "loop receipt",
            "four master receipts",
            "ranked internal quest-packet ledger",
            "Hall decision",
            "Temple decision",
            "runtime writeback receipt",
            "compression delta",
            "restart seed",
        ],
        "last_bundle": {
            "loop_id": bundle["loop_id"],
            "pass_title": bundle["pass_title"],
            "step_text": bundle["step_text"],
            "hall_decision": bundle["hall_decision"]["chosen_action"],
            "temple_decision": bundle["temple_decision"]["chosen_action"],
            "runtime_decision": bundle["runtime_writeback"]["action"],
            "compression_decision": bundle["compression_delta"]["action"],
            "restart_seed": bundle["restart_seed"]["seed"],
            "shell_records": {
                "hall": bundle["hall_decision"]["shell_reference"]["record_id"],
                "temple": bundle["temple_decision"]["shell_reference"]["record_id"],
                "runtime": next(item for item in bundle["packet_results"] if item["target"] == "runtime")["shell_reference"]["record_id"],
                "compression": next(item for item in bundle["packet_results"] if item["target"] == "compression")["shell_reference"]["record_id"],
            },
        } if bundle else None,
        "output_paths": output_paths or {},
    }


def render_status_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Super-Cycle 57 Runner Status",
        "",
        f"- Status: `{payload['status']}`",
        f"- Current completed loop: `L{payload['current_completed_loop']:02d}`",
        f"- Next ready loop: `{f'L{payload['next_ready_loop']:02d}' if payload['next_ready_loop'] else 'NONE'}`",
        f"- Current completed step: {payload['current_completed_step']}",
        f"- Next ready step: {payload['next_ready_step'] or 'epoch-complete'}",
        "- Hall macro front: `Q51`",
        "- Temple macro front: `TQ07`",
        "- Active membrane: `Q41 / TQ06`",
        "- Live Google Docs: `BLOCKED`",
        f"- State source: `{payload['state_source']}`",
        f"- Executed loops by runner: `{', '.join(f'L{loop:02d}' for loop in payload['executed_loops']) or 'none'}`",
    ]
    return "\n".join(lines)


def validate_range(from_loop: int, to_loop: int, loops: list[dict[str, Any]]) -> None:
    if from_loop < 1 or to_loop > len(loops) or from_loop > to_loop:
        raise ValueError(f"Invalid loop range {from_loop}..{to_loop}. Installed ledger spans 1..{len(loops)}.")


def dry_run_range(from_loop: int, to_loop: int, state: dict[str, Any], loops: list[dict[str, Any]], packets_by_loop: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    validate_range(from_loop, to_loop, loops)
    initialize_runner_hysteresis()
    loop_summaries = []
    for loop_index in range(from_loop, to_loop + 1):
        loop = loop_lookup(loop_index, loops)
        loop_packets = packets_by_loop.get(loop_index, [])
        candidate_world = build_candidate_world(loop_packets)
        motion_result = evaluate_candidate_world(candidate_world)
        validate_loop_outputs(loop, loop_packets, motion_result)
        bundle = build_execution_bundle(loop, loop_packets, motion_result, loops)
        ensure_required_outputs(bundle)
        loop_summaries.append(
            {
                "loop_id": bundle["loop_id"],
                "pass_title": bundle["pass_title"],
                "step_text": bundle["step_text"],
                "hall_action": bundle["hall_decision"]["chosen_action"],
                "temple_action": bundle["temple_decision"]["chosen_action"],
                "runtime_action": bundle["runtime_writeback"]["action"],
                "compression_action": bundle["compression_delta"]["action"],
                "restart_seed": bundle["restart_seed"]["seed"],
                "full_bundle_refresh": bundle["awakening_refresh"]["full_bundle_refresh"],
                "pass_boundary_bundle": bundle["awakening_refresh"]["pass_boundary_bundle"],
            }
        )
    return {
        "generated_at": utc_now(),
        "query": {"from_loop": from_loop, "to_loop": to_loop},
        "status": "dry-run",
        "live_docs_blocked": True,
        "recognized_loop_count": len(loops),
        "state_source": state["state_source"],
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "results": loop_summaries,
        "constraints": {
            "hall_macro_limit": VISIBLE_PROMOTION_LIMIT["hall"],
            "temple_macro_limit": VISIBLE_PROMOTION_LIMIT["temple"],
            "runtime_limit": VISIBLE_PROMOTION_LIMIT["runtime"],
            "compression_limit": VISIBLE_PROMOTION_LIMIT["compression"],
            "q02_activation_allowed": False,
            "planner_only_visible_promotions": True,
        },
    }


def execute_loop(loop_index: int, state: dict[str, Any], loops: list[dict[str, Any]], packets_by_loop: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    if state["next_ready_loop"] is None:
        raise ValueError("The installed program is already fully executed.")
    if loop_index != state["next_ready_loop"]:
        raise ValueError(f"Loop L{loop_index:02d} cannot execute while L{state['next_ready_loop']:02d} is the next ready loop.")

    initialize_runner_hysteresis()
    loop = loop_lookup(loop_index, loops)
    loop_packets = packets_by_loop.get(loop_index, [])
    candidate_world = build_candidate_world(loop_packets)
    motion_result = simulate_candidate_world(candidate_world)
    validate_loop_outputs(loop, loop_packets, motion_result)
    bundle = build_execution_bundle(loop, loop_packets, motion_result, loops)
    ensure_required_outputs(bundle)
    output_paths = write_loop_outputs(bundle, candidate_world)
    output_paths.update(update_protocol_ledgers(bundle, output_paths))

    state["current_completed_loop"] = loop_index
    state["last_executed_loop"] = loop_index
    state["next_ready_loop"] = loop_index + 1 if loop_index < len(loops) else None
    if loop_index not in state["executed_loops"]:
        state["executed_loops"].append(loop_index)
    state["status"] = runner_status_string(state)

    write_progress_state(state, loops)
    update_temple_state_markers(state, loops, bundle)
    update_temple_57_state(state, loops, bundle)
    update_active_run(state, loops, bundle)
    update_quest_board(state, loops, bundle)
    update_hall_program(state, bundle)
    update_temple_program(state, bundle)
    update_self_registry(state, bundle)
    append_receipt_ledger(bundle, output_paths)
    update_program_95_json(state, bundle)
    update_active_readme(state)
    update_full_stack_manifest(state)
    runner_manifest = build_runner_manifest(state, loops, bundle, output_paths)
    write_json(RUNNER_MANIFEST_PATH, runner_manifest)
    return {"state": deepcopy(state), "bundle": bundle, "output_paths": output_paths, "runner_manifest": runner_manifest}


def handle_status(as_json: bool) -> None:
    loops, _ = loop_data()
    state = current_state()
    payload = {
        "generated_at": utc_now(),
        "status": runner_status_string(state),
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "current_completed_step": current_loop_title(state["current_completed_loop"], loops),
        "next_ready_step": current_loop_title(state["next_ready_loop"], loops) if state["next_ready_loop"] else None,
        "executed_loops": state["executed_loops"],
        "live_docs_blocked": True,
        "state_source": state["state_source"],
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(render_status_markdown(payload))


def handle_dry_run(from_loop: int, to_loop: int, as_json: bool) -> None:
    loops, packets_by_loop = loop_data()
    state = current_state()
    payload = dry_run_range(from_loop, to_loop, state, loops, packets_by_loop)
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        lines = [
            "# Super-Cycle 57 Dry Run",
            "",
            f"- Range: `L{from_loop:02d}` -> `L{to_loop:02d}`",
            f"- Current runner state: `{runner_status_string(state)}`",
            "- Live Google Docs: `BLOCKED`",
            "",
            "## Loop Summaries",
            "",
        ]
        for item in payload["results"]:
            lines.extend(
                [
                    f"### {item['loop_id']}",
                    f"- Pass: `{item['pass_title']}`",
                    f"- Step: {item['step_text']}",
                    f"- Hall: `{item['hall_action']}`",
                    f"- Temple: `{item['temple_action']}`",
                    f"- Runtime: `{item['runtime_action']}`",
                    f"- Compression: `{item['compression_action']}`",
                    f"- Restart seed: `{item['restart_seed']}`",
                    "",
                ]
            )
        print("\n".join(lines).rstrip())


def handle_run(from_loop: int, to_loop: int, as_json: bool) -> None:
    loops, packets_by_loop = loop_data()
    validate_range(from_loop, to_loop, loops)
    state = current_state()
    if state["next_ready_loop"] is None:
        raise ValueError("All loops are already complete.")
    if from_loop != state["next_ready_loop"]:
        raise ValueError(
            f"Run must begin at the next ready loop L{state['next_ready_loop']:02d}, not L{from_loop:02d}."
        )
    results = []
    for loop_index in range(from_loop, to_loop + 1):
        execution = execute_loop(loop_index, state, loops, packets_by_loop)
        results.append(
            {
                "loop_id": execution["bundle"]["loop_id"],
                "hall_action": execution["bundle"]["hall_decision"]["chosen_action"],
                "temple_action": execution["bundle"]["temple_decision"]["chosen_action"],
                "runtime_action": execution["bundle"]["runtime_writeback"]["action"],
                "compression_action": execution["bundle"]["compression_delta"]["action"],
                "restart_seed": execution["bundle"]["restart_seed"]["seed"],
            }
        )
    payload = {
        "generated_at": utc_now(),
        "status": runner_status_string(state),
        "current_completed_loop": state["current_completed_loop"],
        "next_ready_loop": state["next_ready_loop"],
        "executed_loops": results,
        "runner_manifest": project_relative(RUNNER_MANIFEST_PATH),
        "live_docs_blocked": True,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(render_status_markdown({**payload, "current_completed_step": current_loop_title(state["current_completed_loop"], loops), "next_ready_step": current_loop_title(state["next_ready_loop"], loops) if state["next_ready_loop"] else None, "state_source": project_relative(RUNNER_MANIFEST_PATH)}))


def handle_advance_one(as_json: bool) -> None:
    loops, packets_by_loop = loop_data()
    state = current_state()
    if state["next_ready_loop"] is None:
        raise ValueError("All loops are already complete.")
    execution = execute_loop(state["next_ready_loop"], state, loops, packets_by_loop)
    payload = {
        "generated_at": utc_now(),
        "status": runner_status_string(execution["state"]),
        "current_completed_loop": execution["state"]["current_completed_loop"],
        "next_ready_loop": execution["state"]["next_ready_loop"],
        "loop_id": execution["bundle"]["loop_id"],
        "hall_action": execution["bundle"]["hall_decision"]["chosen_action"],
        "temple_action": execution["bundle"]["temple_decision"]["chosen_action"],
        "runtime_action": execution["bundle"]["runtime_writeback"]["action"],
        "compression_action": execution["bundle"]["compression_delta"]["action"],
        "restart_seed": execution["bundle"]["restart_seed"]["seed"],
        "output_paths": execution["output_paths"],
        "runner_manifest": project_relative(RUNNER_MANIFEST_PATH),
        "live_docs_blocked": True,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "\n".join(
                [
                    "# Super-Cycle 57 Advance-One",
                    "",
                    f"- Executed loop: `{payload['loop_id']}`",
                    f"- New status: `{payload['status']}`",
                    f"- Hall decision: `{payload['hall_action']}`",
                    f"- Temple decision: `{payload['temple_action']}`",
                    f"- Runtime decision: `{payload['runtime_action']}`",
                    f"- Compression decision: `{payload['compression_action']}`",
                    f"- Restart seed: `{payload['restart_seed']}`",
                    f"- Runner manifest: `{payload['runner_manifest']}`",
                ]
            )
        )


def main() -> None:
    args = parse_args()
    if args.command == "status":
        handle_status(args.as_json)
    elif args.command == "dry-run":
        handle_dry_run(args.from_loop, args.to_loop, args.as_json)
    elif args.command == "run":
        handle_run(args.from_loop, args.to_loop, args.as_json)
    elif args.command == "advance-one":
        handle_advance_one(args.as_json)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
