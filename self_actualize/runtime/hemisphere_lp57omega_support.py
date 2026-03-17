from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    DEEP_ROOT,
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    WORKSPACE_ROOT,
    normalize_path,
    utc_now,
)
from self_actualize.runtime.hemisphere_full_corpus_integration_support import (
    FULL_CORPUS_AUTHORITY_REGISTRY_PATH,
    FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH,
    FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
    FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
    FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH,
    FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH,
)
from self_actualize.runtime.hemisphere_ap6d_57_loop_support import (
    AP6D_57_AGENT_LANE_REGISTRY_PATH,
    AP6D_57_LOOP_CONTROL_REGISTRY_PATH,
    AP6D_57_NESTED_SEAT_MANIFEST_PATH,
)
from self_actualize.runtime.hemisphere_dense_65_shell_support import (
    DENSE_65_AUTHORITY_REFS,
    DENSE_65_MANIFEST_PATH,
    DENSE_65_PRIOR_SEED_POSITION,
    DENSE_65_RING_ORDER,
    DENSE_65_RQT_OVERFLOW_REGISTRY_PATH,
    DENSE_65_RQT_WITNESS_REGISTRY_PATH,
    DENSE_65_SHELL_REGISTRY_PATH,
    DENSE_65_SIGMA_PATH,
    DENSE_65_S_ROWS,
    canonical_hide_pole,
)


ACTIVE_LOOP_ID = 2
ACTIVE_SEATS_PER_AGENT = 256
PUBLIC_PROMOTION_CAP = 8
SHARED_TOTAL_SEATS = 4096
SHARED_ACTIVE_SEATS = 1024
SHARED_DORMANT_SEATS = 3072
LIVE_LAW = {
    "active_membrane": "Q41 / TQ06",
    "feeder_stack": ["Q42", "Q46", "TQ04", "Q02"],
}
LEGACY_MASTER_AGENTS = [
    {
        "master_agent_id": "M1",
        "agent_id": "MASTER-SYNTHESIZER",
        "role": "Synthesizer / Researcher",
        "mission": "deeply scan the full corpus, detect hidden bridges, contradictions, mathematical upgrades, and latent integration structures",
        "packet_output": "SynthesisPacket",
        "quest_rights": "recommend_only",
    },
    {
        "master_agent_id": "M2",
        "agent_id": "MASTER-PLANNER",
        "role": "Planner / Architect",
        "mission": "turn synthesis into Hall and Temple quest trees, dependency graphs, sequencing logic, and structured action pathways",
        "packet_output": "GuildQuestPacketSet + TempleQuestPacketSet",
        "quest_rights": "canonicalize_and_promote",
    },
    {
        "master_agent_id": "M3",
        "agent_id": "MASTER-WORKER",
        "role": "Worker / Adventurer",
        "mission": "apply replay-safe Hall and Temple work, land artifacts, bridges, equations, algorithm scaffolds, and implementation receipts",
        "packet_output": "ExecutionBatchPacket",
        "quest_rights": "claim_only",
    },
    {
        "master_agent_id": "M4",
        "agent_id": "MASTER-PRUNER",
        "role": "Pruner / Compressor / Defragmenter",
        "mission": "tighten the corpus, reduce redundancy, preserve witnesses, and reseed the next loop from a cleaner crystalline baseline",
        "packet_output": "CompressionReceipt",
        "quest_rights": "retire_or_merge_only",
    },
]


def base4_digits(value: int, width: int) -> list[int]:
    digits = [0] * width
    for index in range(width - 1, -1, -1):
        digits[index] = value % 4
        value //= 4
    return digits


def seat_addr_6d(seat_index: int) -> str:
    labels = ["A", "B", "C", "D", "E", "F"]
    return ".".join(
        f"{label}{digit + 1}" for label, digit in zip(labels, base4_digits(seat_index, 6))
    )


MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
DEEP_CONTROL_ROOT = DEEP_ROOT / "00_CONTROL"

MASTER_LOOP_STATE_PATH = SELF_ACTUALIZE_ROOT / "master_loop_state_57.json"
MASTER_AGENT_STATE_PATH = SELF_ACTUALIZE_ROOT / "master_agent_state_57.json"
MASTER_LOOP_SHARED_LATTICE_PATH = SELF_ACTUALIZE_ROOT / "master_loop_shared_lattice_4096.json"

LP57OMEGA_LOOP_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_loop_registry.json"
LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_agent_identity_registry.json"
)
LP57OMEGA_COORDINATE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_coordinate_registry.json"
)
LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_quest_contract_registry.json"
)
LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_master_ledger_registry.json"
)
LP57OMEGA_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_manifest.json"

LP57OMEGA_LOOP_REGISTRY_MIRROR = REGISTRY_ROOT / LP57OMEGA_LOOP_REGISTRY_PATH.name
LP57OMEGA_AGENT_IDENTITY_REGISTRY_MIRROR = (
    REGISTRY_ROOT / LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH.name
)
LP57OMEGA_COORDINATE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / LP57OMEGA_COORDINATE_REGISTRY_PATH.name
)
LP57OMEGA_QUEST_CONTRACT_REGISTRY_MIRROR = (
    REGISTRY_ROOT / LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH.name
)
LP57OMEGA_MASTER_LEDGER_REGISTRY_MIRROR = (
    REGISTRY_ROOT / LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH.name
)
LP57OMEGA_MANIFEST_MIRROR = REGISTRY_ROOT / LP57OMEGA_MANIFEST_PATH.name

LP57OMEGA_HEMISPHERE_DOCS = {
    "lp57omega_index": HEMISPHERE_ROOT / "85_lp57omega_protocol_index.md",
    "lp57omega_framework": HEMISPHERE_ROOT / "86_lp57omega_master_loop_framework.md",
    "lp57omega_coordinates": HEMISPHERE_ROOT / "87_lp57omega_coordinate_standard.md",
    "lp57omega_quest_ledger": HEMISPHERE_ROOT / "88_lp57omega_quest_and_ledger_standard.md",
    "lp57omega_signature_plan": HEMISPHERE_ROOT / "89_lp57omega_57_loop_signature_plan.md",
    "lp57omega_receipt": HEMISPHERE_ROOT / "90_lp57omega_receipt.md",
}

LP57OMEGA_GUILD_HALL_DOC_PATH = GUILD_HALL_ROOT / "19_LP57OMEGA_GUILD_HALL_PROTOCOL.md"
LP57OMEGA_TEMPLE_DOC_PATH = TEMPLE_ROOT / "10_LP57OMEGA_TEMPLE_PROTOCOL.md"
LP57OMEGA_DEEP_CONTROL_DOC_PATH = DEEP_CONTROL_ROOT / "13_LP57OMEGA_PROTOCOL.md"
LP57OMEGA_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_lp57omega_protocol.md"
LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_LIMINAL_COORDINATE_STANDARD.md"
)
LP57OMEGA_AGENT_LEDGER_STANDARD_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_AGENT_LEDGER_STANDARD.md"
)
LP57OMEGA_SEED_INVERSION_STANDARD_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_SEED_INVERSION_STANDARD.md"
)
LP57OMEGA_SEED_INVERSION_STANDARD_JSON_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_SEED_INVERSION_STANDARD.json"
)

LP57OMEGA_GUILD_HALL_DOC_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_GUILD_HALL_DOC_PATH.name
LP57OMEGA_TEMPLE_DOC_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_TEMPLE_DOC_PATH.name
LP57OMEGA_DEEP_CONTROL_DOC_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_DEEP_CONTROL_DOC_PATH.name
LP57OMEGA_RECEIPT_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_RECEIPT_PATH.name
LP57OMEGA_LIMINAL_COORDINATE_STANDARD_MIRROR = (
    FLEET_MIRROR_ROOT / LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH.name
)
LP57OMEGA_AGENT_LEDGER_STANDARD_MIRROR = (
    FLEET_MIRROR_ROOT / LP57OMEGA_AGENT_LEDGER_STANDARD_PATH.name
)
LP57OMEGA_SEED_INVERSION_STANDARD_MIRROR = (
    FLEET_MIRROR_ROOT / LP57OMEGA_SEED_INVERSION_STANDARD_PATH.name
)
LP57OMEGA_SEED_INVERSION_STANDARD_JSON_MIRROR = (
    FLEET_MIRROR_ROOT / LP57OMEGA_SEED_INVERSION_STANDARD_JSON_PATH.name
)

GUILD_HALL_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_QUEST_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"

HALL_BOARD_MARKER = "MASTER_LOOP_57_HALL_QUEST"
TEMPLE_BOARD_MARKER = "MASTER_LOOP_57_TEMPLE_QUEST"

LP57OMEGA_PROTOCOL_ID = "LP-57OMEGA"
LP57OMEGA_PROTOCOL_DISPLAY = "LP-57Omega v2"
LP57OMEGA_LOOP_COUNT = 57
LP57OMEGA_MASTER_AGENT_COUNT = 4
LP57OMEGA_SYNAPTIC_SEAT_COUNT = 1024
LP57OMEGA_GOVERNANCE_FIBER_COUNT = 256
LP57OMEGA_OWNERABLE_PACKET_COUNT = 64
LP57OMEGA_LIMINAL_PACKET_COUNT = 4

COORDINATE_DIMENSIONS = [
    "Xs",
    "Ys",
    "Zs",
    "Ts",
    "Qs",
    "Rs",
    "Cs",
    "Fs",
    "Ms",
    "Ns",
    "Hs",
    "OMEGAs",
]
QUEST_CONTRACT_FIELDS = [
    "quest_id",
    "zone",
    "parent_loop",
    "objective",
    "why_now",
    "target_surfaces",
    "witness_needed",
    "dependencies",
    "coordinate_targets",
    "acceptance_rule",
    "restart_seed",
]
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

MASTER_ROLE_TAGS = {
    "MASTER-SYNTHESIZER": ("SYNTHESIZER-MASTER", "SYNTH-RESEARCH", "SYNTH-JUNCTION", "SYNTH-LEDGER"),
    "MASTER-PLANNER": ("PLANNER-MASTER", "PLANNER-SUB", "PLANNER-QUEST", "PLANNER-HANDOFF"),
    "MASTER-WORKER": ("WORKER-MASTER", "WORKER-APPLY", "WORKER-REPAIR", "WORKER-RECEIPT"),
    "MASTER-PRUNER": ("PRUNER-MASTER", "PRUNE-CRYSTAL", "PRUNE-DEFRAG", "PRUNE-RESEED"),
}
MASTER_AGENT_ALIASES = {
    "A1": "MASTER-SYNTHESIZER",
    "A2": "MASTER-PLANNER",
    "A3": "MASTER-WORKER",
    "A4": "MASTER-PRUNER",
    "M1": "MASTER-SYNTHESIZER",
    "M2": "MASTER-PLANNER",
    "M3": "MASTER-WORKER",
    "M4": "MASTER-PRUNER",
}
ACTION_TYPES = {
    "MASTER-SYNTHESIZER": "synthesize",
    "MASTER-PLANNER": "plan",
    "MASTER-WORKER": "implement",
    "MASTER-PRUNER": "compress",
}
HALL_OBJECTIVES = {
    "MASTER-SYNTHESIZER": "Surface one synthesis-backed Hall frontier packet for the loop focus.",
    "MASTER-PLANNER": "Convert the loop focus into one ownerable Hall quest bundle with sequencing law.",
    "MASTER-WORKER": "Claim and apply the highest-yield Hall packet without widening beyond the promoted scope.",
    "MASTER-PRUNER": "Compress Hall-side duplication and retire stale practical packets after work lands.",
}
TEMPLE_OBJECTIVES = {
    "MASTER-SYNTHESIZER": "Witness contradictions, missing proofs, and deep-root tensions for the loop focus.",
    "MASTER-PLANNER": "Bind one Temple governance contract that preserves admissibility and coordinate duty.",
    "MASTER-WORKER": "Carry one Temple-backed runtime execution lane without violating replay and proof law.",
    "MASTER-PRUNER": "Apply one Temple compression and restart-safe governance pass to the loop focus.",
}
ACCEPTANCE_RULES = {
    "MASTER-SYNTHESIZER": "Complete only when one synthesis-backed witness packet and one evidence-gap summary are linked.",
    "MASTER-PLANNER": "Complete only when Hall and Temple outputs share one dependency-safe restart seed.",
    "MASTER-WORKER": "Complete only when one applied delta, one receipt, and one replay-safe handoff are recorded.",
    "MASTER-PRUNER": "Complete only when one duplication family is tightened without erasing the only live witness.",
}

DENSE_65_POLE_FACE_MAP = {
    "fire": "A",
    "air": "C",
    "water": "B",
    "earth": "D",
}
DENSE_65_SUFFIX_BY_POLE_SET = {
    tuple(row["pole_set"]): row["mu"] for row in DENSE_65_S_ROWS
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE_ROOT).as_posix()


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def slugify(value: str) -> str:
    cleaned: list[str] = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif cleaned and cleaned[-1] != "-":
            cleaned.append("-")
    return "".join(cleaned).strip("-") or "unknown"


def wrap_block(marker: str, body: str) -> str:
    return "\n".join([f"<!-- {marker}:START -->", body.rstrip(), f"<!-- {marker}:END -->"])


def apply_marker_block(current: str, marker: str, body: str, *, after_first_heading: bool = False) -> str:
    start_marker = f"<!-- {marker}:START -->"
    end_marker = f"<!-- {marker}:END -->"
    replacement = wrap_block(marker, body)
    if start_marker in current and end_marker in current:
        start = current.index(start_marker)
        end = current.index(end_marker) + len(end_marker)
        return current[:start] + replacement + current[end:]
    if after_first_heading and current.startswith("# "):
        first_break = current.find("\n")
        insert_at = first_break if first_break != -1 else len(current)
        return current[:insert_at] + "\n\n" + replacement + current[insert_at:]
    return replacement + ("\n\n" + current if current else "")


def legacy_coordinate_stamp(
    seat_index: int,
    loop_number: int,
    short_name: str,
    agent_id: str,
) -> dict[str, str]:
    master_band = seat_index // ACTIVE_SEATS_PER_AGENT
    within_band = seat_index % ACTIVE_SEATS_PER_AGENT
    return {
        "Xs": f"ROOT-{master_band + 1}",
        "Ys": f"MANUSCRIPT-{(within_band // 64) + 1}",
        "Zs": f"REGION-{(within_band // 16) + 1}",
        "Ts": f"L{loop_number:02d}",
        "Qs": "LATTICE",
        "Rs": "D0",
        "Cs": f"C{(within_band % 4) + 1}",
        "Fs": short_name.upper().replace("/", "-").replace(" ", "-"),
        "Ms": seat_addr_6d(seat_index).split(".")[0],
        "Ns": f"N{(within_band % 4) + 1}",
        "Hs": f"H{((within_band // 4) % 4) + 1}",
        "OMEGAs": agent_id,
    }


def promotion_rows_for_loop(loop_number: int, zone: str) -> list[dict[str, str]]:
    next_loop = f"L{((loop_number % LP57OMEGA_LOOP_COUNT) + 1):02d}"
    rows = []
    for index, agent_row in enumerate(LEGACY_MASTER_AGENTS, start=1):
        role_order = index - 1
        seat_index = role_order * ACTIVE_SEATS_PER_AGENT
        prefix = "Q57" if zone == "HALL" else "TQ57"
        zone_label = "Hall" if zone == "HALL" else "Temple"
        rows.append(
            {
                "quest_id": f"{prefix}-L{loop_number:02d}-{agent_row['agent_id'].replace('MASTER-', '')}-{zone}",
                "title": f"{zone_label} promotion for {agent_row.get('role', agent_row['agent_id'])}",
                "seat_addr_6d": seat_addr_6d(seat_index),
                "restart_seed": f"L{loop_number:02d} -> {next_loop}",
            }
        )
    return rows


def hall_promotions_for_loop(loop_number: int) -> list[dict[str, str]]:
    return promotion_rows_for_loop(loop_number, "HALL")


def temple_promotions_for_loop(loop_number: int) -> list[dict[str, str]]:
    return promotion_rows_for_loop(loop_number, "TEMPLE")


def normalize_coordinate_tuple(payload: dict[str, Any]) -> dict[str, str]:
    if isinstance(payload, str):
        if "|" in payload and "=" in payload:
            parts: dict[str, str] = {}
            for item in payload.split("|"):
                if "=" not in item:
                    continue
                key, value = item.split("=", 1)
                parts[key] = value
            payload = parts
        else:
            payload = {}
    return {
        "Xs": str(payload.get("Xs", "")),
        "Ys": str(payload.get("Ys", "")),
        "Zs": str(payload.get("Zs", "")),
        "Ts": str(payload.get("Ts", "")),
        "Qs": str(payload.get("Qs", "")),
        "Rs": str(payload.get("Rs", "")),
        "Cs": str(payload.get("Cs", "")),
        "Fs": str(payload.get("Fs", "")),
        "Ms": str(payload.get("Ms", "")),
        "Ns": str(payload.get("Ns", "")),
        "Hs": str(payload.get("Hs", "")),
        "OMEGAs": str(payload.get("OMEGAs", payload.get("Ωs", ""))),
    }


def coordinate_stamp_string(coordinate_tuple: dict[str, str]) -> str:
    return "|".join(f"{dimension}={coordinate_tuple[dimension]}" for dimension in COORDINATE_DIMENSIONS)


def quartile_label(value: float, prefix: str) -> str:
    if value < 0.25:
        band = 1
    elif value < 0.50:
        band = 2
    elif value < 0.75:
        band = 3
    else:
        band = 4
    return f"{prefix}{band}"


def scope_coordinate(scope_flags: str) -> str:
    normalized = scope_flags.strip().lower()
    if normalized == "archive":
        return "ARCHIVE"
    if normalized == "both":
        return "BOTH"
    if normalized == "witness_only":
        return "WITNESS"
    return "LIVE"


def hemisphere_coordinate(record: dict[str, Any]) -> str:
    if record.get("bridge_class") == "commissure_bridge":
        return "COMMISSURE"
    return str(record.get("primary_hemisphere") or "GC0")


def deep_mode_coordinate(record: dict[str, Any]) -> str:
    appendix_support = record.get("appendix_support", []) or []
    symmetry = record.get("symmetry_membership", {}) or {}
    if appendix_support:
        return "APPENDIX"
    if symmetry.get("observer_lattice"):
        return "OBSERVER"
    if len(record.get("basis_anchor_ids", []) or []) > 1:
        return "MATRIX"
    return "BASIS"


def topology_band(relative_path: str) -> str:
    depth = len([part for part in normalize_path(relative_path).split("/") if part])
    if depth <= 1:
        return "T1"
    if depth <= 3:
        return "T2"
    if depth <= 6:
        return "T3"
    return "T4"


def compression_band(record: dict[str, Any]) -> str:
    if (record.get("duplicate_count") or 0) > 0:
        return "C4"
    if (record.get("scope_flags") or "") == "witness_only":
        return "C3"
    blockers = set(record.get("awakening_stage_blockers", []) or [])
    if "proof_weakness" in blockers or "historical_drift" in blockers:
        return "C2"
    return "C1"


def manuscript_branch_code(top_level: str) -> str:
    branch = slugify(top_level).replace("-", "_").upper()
    if len(branch) > 18:
        branch = branch[:18]
    return f"M-{branch}"


def neural_connectivity_band(record: dict[str, Any]) -> str:
    score = len(record.get("basis_anchor_ids", []) or []) + len(record.get("direct_edge_ids", []) or [])
    if score >= 6:
        return "N4"
    if score >= 5:
        return "N3"
    if score >= 4:
        return "N2"
    return "N1"


def hierarchy_band(relative_path: str) -> str:
    depth = len([part for part in normalize_path(relative_path).split("/") if part])
    if depth <= 1:
        return "H1"
    if depth <= 3:
        return "H2"
    if depth <= 6:
        return "H3"
    return "H4"


def omega_band(record: dict[str, Any]) -> str:
    symmetry = record.get("symmetry_membership", {}) or {}
    if symmetry.get("zero_point_active"):
        return "ZERO-POINT"
    appendix_support = set(record.get("appendix_support", []) or [])
    if "AppQ" in appendix_support:
        return "QUARANTINE"
    if record.get("bridge_class") == "commissure_bridge":
        return "COMMISSURE"
    return "STABLE"


def _normalize_dense_pole(face: Any) -> str | None:
    if not face:
        return None
    return DENSE_65_POLE_FACE_MAP.get(str(face).strip().lower())


def dense_kernel_ref_for_record(record: dict[str, Any]) -> dict[str, Any] | None:
    poles: list[str] = []
    for side in ("MATH", "MYTH"):
        route = (record.get("hemisphere_routes") or {}).get(side) or {}
        pole = _normalize_dense_pole(route.get("face6"))
        if pole and pole not in poles:
            poles.append(pole)
    ordered_poles = [pole for pole in DENSE_65_RING_ORDER if pole in poles]
    suffix = DENSE_65_SUFFIX_BY_POLE_SET.get(tuple(ordered_poles))
    if not suffix:
        return None
    return {
        "overlay_mode": "kernel_overlay",
        "header_record_id": "H00",
        "prior_seed_position": DENSE_65_PRIOR_SEED_POSITION,
        "symmetry_record_id": f"S{suffix}",
        "rotation_record_id": f"R{suffix}",
        "orbit_record_id": f"Q{suffix}",
        "antispin_record_id": f"T{suffix}",
        "pole_set": ordered_poles,
        "hide_pole": canonical_hide_pole(ordered_poles),
        "ring_order": list(DENSE_65_RING_ORDER),
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
    }


def record_coordinate_tuple(record: dict[str, Any]) -> dict[str, str]:
    return {
        "Xs": scope_coordinate(str(record.get("scope_flags", "live"))),
        "Ys": hemisphere_coordinate(record),
        "Zs": deep_mode_coordinate(record),
        "Ts": topology_band(str(record.get("relative_path", ""))),
        "Qs": quartile_label(float(record.get("math_weight", 0.0) or 0.0), "Q"),
        "Rs": quartile_label(float(record.get("myth_weight", 0.0) or 0.0), "R"),
        "Cs": compression_band(record),
        "Fs": f"F-{slugify(str(record.get('family', 'unknown'))).upper().replace('-', '_')[:16]}",
        "Ms": manuscript_branch_code(str(record.get("top_level", "root"))),
        "Ns": neural_connectivity_band(record),
        "Hs": hierarchy_band(str(record.get("relative_path", ""))),
        "OMEGAs": omega_band(record),
    }


def lookup_address(record: dict[str, Any], coordinate_tuple: dict[str, str]) -> str:
    basis_anchor = (record.get("basis_anchor_ids") or ["UNANCHORED"])[0]
    primary_hemisphere = record.get("primary_hemisphere") or "GC0"
    stage_id = record.get("awakening_stage") or "UNSTAGED"
    route_packet = (record.get("hemisphere_routes") or {}).get(primary_hemisphere, {})
    target_system = route_packet.get("target_system") or "UNROUTED"
    return (
        f"LP57Omega::{record.get('record_id')}::{record.get('family')}::{basis_anchor}::"
        f"{primary_hemisphere}::{stage_id}::{target_system}::{coordinate_stamp_string(coordinate_tuple)}"
    )


def loop_key(loop_number: int) -> str:
    return f"L{loop_number:02d}"


def artifact_ids(loop_number: int) -> dict[str, str]:
    prefix = f"LP57-{loop_key(loop_number)}"
    return {
        "loop_manifest": f"{prefix}-LOOP-MANIFEST",
        "research_packet": f"{prefix}-RESEARCH",
        "hall_quest_bundle": f"{prefix}-HALL",
        "temple_quest_bundle": f"{prefix}-TEMPLE",
        "worker_action_bundle": f"{prefix}-WORK",
        "pruning_receipt": f"{prefix}-PRUNE",
        "restart_seed": f"{prefix}-RESTART",
    }


def restart_handoff(loop_number: int, loop_rows: list[dict[str, Any]]) -> str:
    next_loop_number = (loop_number % len(loop_rows)) + 1
    next_title = loop_rows[next_loop_number - 1]["title"]
    return f"{loop_key(next_loop_number)} -> {next_title}"


def advancement_signature(loop_row: dict[str, Any]) -> str:
    return " :: ".join(
        [
            str(loop_row.get("title", "")),
            str(loop_row.get("synthesis_objective", "")),
            str(loop_row.get("planning_objective", "")),
            str(loop_row.get("implementation_objective", "")),
            str(loop_row.get("compression_objective", "")),
            str(loop_row.get("expected_mapping_gain", "")),
        ]
    )


def rotated_focus_records(records: list[dict[str, Any]], loop_number: int, count: int = 3) -> list[dict[str, Any]]:
    if not records:
        return []
    ordered = sorted(records, key=lambda item: (-float(item.get("salience", 0.0)), normalize_path(item.get("relative_path", "")).lower()))
    start = ((loop_number - 1) * 11) % len(ordered)
    result: list[dict[str, Any]] = []
    used: set[str] = set()
    for offset in range(len(ordered)):
        candidate = ordered[(start + offset) % len(ordered)]
        record_id = str(candidate.get("record_id", ""))
        if not record_id or record_id in used:
            continue
        used.add(record_id)
        result.append(candidate)
        if len(result) == count:
            break
    return result


def master_agent_number(agent_id: str) -> int:
    agent_id = MASTER_AGENT_ALIASES.get(agent_id, agent_id)
    for row in LEGACY_MASTER_AGENTS:
        if row["agent_id"] == agent_id:
            master_agent_id = str(row.get("master_agent_id", "M0"))
            if master_agent_id.startswith("M") and master_agent_id[1:].isdigit():
                return int(master_agent_id[1:])
    if agent_id in MASTER_AGENT_ALIASES:
        alias = MASTER_AGENT_ALIASES[agent_id]
        return master_agent_number(alias)
    if agent_id.startswith("A") and agent_id[1:].isdigit():
        return int(agent_id[1:])
    if agent_id.startswith("M") and agent_id[1:].isdigit():
        return int(agent_id[1:])
    return 0


def canonical_master_agent_id(agent_id: str, role_order: int) -> str:
    if agent_id in MASTER_ROLE_TAGS:
        return agent_id
    if agent_id in MASTER_AGENT_ALIASES:
        return MASTER_AGENT_ALIASES[agent_id]
    fallback = f"A{role_order}"
    return MASTER_AGENT_ALIASES.get(fallback, "MASTER-SYNTHESIZER")


def sample_nested_ids(loop_number: int, agent_id: str) -> list[str]:
    agent_number = master_agent_number(agent_id)
    role_tags = MASTER_ROLE_TAGS[agent_id]
    return [
        f"{loop_key(loop_number)}.A{agent_number}.D1.B0000.{role_tags[1]}",
        f"{loop_key(loop_number)}.A{agent_number}.D3.B0123.{role_tags[2]}",
        f"{loop_key(loop_number)}.A{agent_number}.D6.B3333.{role_tags[3]}",
    ]


def agent_coordinate_tuple(agent_row: dict[str, Any], loop_number: int) -> dict[str, str]:
    seat_start = int(agent_row.get("seat_band", {}).get("start_index", 0))
    return normalize_coordinate_tuple(
        legacy_coordinate_stamp(seat_start, loop_number, agent_row.get("short_name", ""), agent_row.get("agent_id", ""))
    )


def loop_rows_from_state(
    master_loop_state: dict[str, Any],
    docs_gate_status: str,
    focus_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    source_rows = master_loop_state.get("loops", [])
    focus_by_loop: dict[int, list[dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        raw_loop_id = source_row["loop_id"]
        loop_number = int(str(raw_loop_id).replace("L", ""))
        selected_focus_records = rotated_focus_records(focus_records, loop_number)
        focus_by_loop[loop_number] = selected_focus_records
        rows.append(
            {
                **source_row,
                "loop_id": loop_number,
                "loop_number": loop_number,
                "synthesis_objective": source_row.get(
                    "synthesis_objective",
                    source_row.get("primary_synthesis_objective", ""),
                ),
                "planning_objective": source_row.get(
                    "planning_objective",
                    source_row.get("primary_planning_objective", ""),
                ),
                "implementation_objective": source_row.get(
                    "implementation_objective",
                    source_row.get("primary_implementation_objective", ""),
                ),
                "compression_objective": source_row.get(
                    "compression_objective",
                    source_row.get("primary_compression_objective", ""),
                ),
                "ring": source_row.get(
                    "ring",
                    source_row.get("arc_label", source_row.get("focus_family", "loop-field")),
                ),
                "loop_key": loop_key(loop_number),
                "artifact_ids": artifact_ids(loop_number),
                "receipt_ids": list((source_row.get("receipt_paths") or {}).values()),
                "focus_record_ids": [record.get("record_id", "") for record in selected_focus_records],
                "restart_handoff": restart_handoff(loop_number, source_rows),
                "advancement_signature": advancement_signature(source_row),
                "docs_gate_status": docs_gate_status,
            }
        )
    return rows, focus_by_loop


def build_loop_registry(
    master_loop_state: dict[str, Any],
    docs_gate_status: str,
    focus_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[int, list[dict[str, Any]]]]:
    rows, focus_by_loop = loop_rows_from_state(master_loop_state, docs_gate_status, focus_records)
    return (
        {
            "generated_at": utc_now(),
            "protocol_id": LP57OMEGA_PROTOCOL_ID,
            "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
            "docs_gate_status": docs_gate_status,
            "loop_count": len(rows),
            "required_fields": [
                "loop_id",
                "loop_key",
                "title",
                "dominant_focus",
                "synthesis_objective",
                "planning_objective",
                "implementation_objective",
                "compression_objective",
                "expected_structural_gain",
                "expected_mapping_gain",
                "advancement_signature",
                "artifact_ids",
                "receipt_paths",
                "restart_handoff",
                "docs_gate_status",
            ],
            "rows": rows,
        },
        focus_by_loop,
    )


def enrich_master_loop_state(
    master_loop_state: dict[str, Any],
    loop_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    enriched = dict(master_loop_state)
    enriched["generated_at"] = utc_now()
    enriched["protocol_display_name"] = LP57OMEGA_PROTOCOL_DISPLAY
    enriched["docs_gate_status"] = docs_gate_status
    enriched["required_artifact_ids"] = list(artifact_ids(1))
    enriched["canonical_support_registries"] = {
        "loop_registry": str(LP57OMEGA_LOOP_REGISTRY_PATH),
        "agent_identity_registry": str(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH),
        "coordinate_registry": str(LP57OMEGA_COORDINATE_REGISTRY_PATH),
        "quest_contract_registry": str(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH),
        "master_ledger_registry": str(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH),
        "manifest": str(LP57OMEGA_MANIFEST_PATH),
    }
    enriched["machine_artifact_contract"] = list(artifact_ids(1))
    current_cycle_summary = dict(enriched.get("current_cycle_summary", {}))
    current_cycle_summary["required_cycle_outputs"] = [
        "loop manifest",
        "research packet",
        "hall quest bundle",
        "temple quest bundle",
        "worker action bundle",
        "pruning receipt",
        "restart seed",
    ]
    enriched["current_cycle_summary"] = current_cycle_summary
    enriched["loops"] = loop_registry["rows"]
    return enriched


def build_agent_identity_registry(
    master_agent_state: dict[str, Any],
    loop_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    agent_summaries = []
    identity_rows = []
    source_agents = list(master_agent_state.get("agents", []))
    if not source_agents:
        source_agents = [
            {
                "agent_id": f"A{index}",
                "name": legacy_row.get("role", ""),
                "role_order": index,
                "current_front": "",
                "packet_space": "shared 4^6 packet lattice",
                "active_packet_limit": ACTIVE_SEATS_PER_AGENT,
                "handoff_target": f"A{(index % LP57OMEGA_MASTER_AGENT_COUNT) + 1}",
                "restart_seed": "",
                "status": "SEEDED",
            }
            for index, legacy_row in enumerate(LEGACY_MASTER_AGENTS, start=1)
        ]
    for index, agent_row in enumerate(source_agents, start=1):
        role_order = int(agent_row.get("role_order", index))
        canonical_agent = canonical_master_agent_id(str(agent_row.get("agent_id", "")), role_order)
        legacy_row = next(
            row for row in LEGACY_MASTER_AGENTS if row["agent_id"] == canonical_agent
        )
        band_start = (role_order - 1) * ACTIVE_SEATS_PER_AGENT
        band_stop = band_start + ACTIVE_SEATS_PER_AGENT - 1
        summary_row = {
            **agent_row,
            "agent_id": canonical_agent,
            "name": str(agent_row.get("name") or legacy_row.get("role", "")),
            "short_name": str(
                agent_row.get("short_name")
                or canonical_agent.replace("MASTER-", "")
            ),
            "role_order": role_order,
            "mission": str(agent_row.get("mission") or legacy_row.get("mission", "")),
            "required_outputs": list(
                agent_row.get("required_outputs")
                or [
                    legacy_row.get("packet_output", ""),
                    "coordinate updates",
                    "ledger receipts",
                    "restart-safe writeback",
                ]
            ),
            "public_quest_rights": str(
                agent_row.get("public_quest_rights")
                or legacy_row.get("quest_rights", "")
            ),
            "seat_budget_active": int(
                agent_row.get("seat_budget_active")
                or agent_row.get("active_packet_limit")
                or ACTIVE_SEATS_PER_AGENT
            ),
            "seat_band": agent_row.get("seat_band")
            or {
                "start_index": band_start,
                "stop_index": band_stop,
                "sample_start": seat_addr_6d(band_start),
                "sample_end": seat_addr_6d(band_stop),
            },
            "resolution_stack": list(
                agent_row.get("resolution_stack")
                or [
                    {"depth": "D1", "label": "corpus plane"},
                    {"depth": "D2", "label": "family and manuscript branch"},
                    {"depth": "D3", "label": "document and chapter band"},
                    {"depth": "D4", "label": "section and concept cluster"},
                    {"depth": "D5", "label": "equation and routing cell"},
                    {"depth": "D6", "label": "ledger and writeback cell"},
                ]
            ),
        }
        agent_id = canonical_agent
        role_tags = list(MASTER_ROLE_TAGS[agent_id])
        summary_coordinate = agent_coordinate_tuple(summary_row, ACTIVE_LOOP_ID)
        agent_summaries.append(
            {
                **summary_row,
                "nested_depth_range": ["D1", "D6"],
                "branch_base": "base4",
                "compiled_seat_law": {
                    "manifest_seats": SHARED_TOTAL_SEATS,
                    "synaptic_seats": LP57OMEGA_SYNAPTIC_SEAT_COUNT,
                    "governance_fibers": LP57OMEGA_GOVERNANCE_FIBER_COUNT,
                    "ownerable_packets": LP57OMEGA_OWNERABLE_PACKET_COUNT,
                    "liminal_packets": LP57OMEGA_LIMINAL_PACKET_COUNT,
                },
                "canonical_id_tag_pattern": "[LoopID].[MasterAgentID].[NestedDepth].[BranchPath].[RoleTag]",
                "role_tags": role_tags,
                "sample_nested_agent_ids": sample_nested_ids(ACTIVE_LOOP_ID, agent_id),
                "coordinate_tuple": summary_coordinate,
                "coordinate_stamp": coordinate_stamp_string(summary_coordinate),
                "docs_gate_status": docs_gate_status,
            }
        )
        for loop_row in loop_registry["rows"]:
            loop_number = int(loop_row["loop_id"])
            coordinate_tuple = agent_coordinate_tuple(summary_row, loop_number)
            identity_rows.append(
                {
                    "loop_id": loop_row["loop_key"],
                    "loop_number": loop_number,
                    "loop_title": loop_row["title"],
                    "master_agent_id": agent_id,
                    "master_agent_label": summary_row.get("name", ""),
                    "master_agent_number": master_agent_number(agent_id),
                    "agent_id_tag": f"{loop_row['loop_key']}.A{master_agent_number(agent_id)}.D0.B0000.{role_tags[0]}",
                    "parent_agent": agent_id,
                    "nested_depth_range": ["D1", "D6"],
                    "branch_base": "base4",
                    "role_tags": role_tags,
                    "packet_cap": PUBLIC_PROMOTION_CAP,
                    "seat_band": summary_row.get("seat_band", {}),
                    "compiled_seat_law": {
                        "manifest_seats": SHARED_TOTAL_SEATS,
                        "synaptic_seats": LP57OMEGA_SYNAPTIC_SEAT_COUNT,
                        "governance_fibers": LP57OMEGA_GOVERNANCE_FIBER_COUNT,
                        "ownerable_packets": LP57OMEGA_OWNERABLE_PACKET_COUNT,
                        "liminal_packets": LP57OMEGA_LIMINAL_PACKET_COUNT,
                    },
                    "coordinate_tuple": coordinate_tuple,
                    "coordinate_stamp": coordinate_stamp_string(coordinate_tuple),
                    "sample_nested_agent_ids": sample_nested_ids(loop_number, agent_id),
                    "docs_gate_status": docs_gate_status,
                }
            )
    enriched_state = {
        **master_agent_state,
        "generated_at": utc_now(),
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "identity_registry_path": str(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH),
        "quest_contract_registry_path": str(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH),
        "master_ledger_registry_path": str(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH),
        "canonical_id_tag_pattern": "[LoopID].[MasterAgentID].[NestedDepth].[BranchPath].[RoleTag]",
        "agents": agent_summaries,
    }
    return (
        {
            "generated_at": utc_now(),
            "protocol_id": LP57OMEGA_PROTOCOL_ID,
            "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
            "docs_gate_status": docs_gate_status,
            "loop_count": loop_registry["loop_count"],
            "master_agent_count": len(master_agent_state.get("agents", [])),
            "row_count": len(identity_rows),
            "required_fields": [
                "loop_id",
                "loop_number",
                "master_agent_id",
                "master_agent_label",
                "agent_id_tag",
                "parent_agent",
                "nested_depth_range",
                "branch_base",
                "role_tags",
                "coordinate_tuple",
                "coordinate_stamp",
                "sample_nested_agent_ids",
                "docs_gate_status",
            ],
            "rows": identity_rows,
        },
        enriched_state,
    )


def build_master_loop_shared_lattice(
    master_loop_shared_lattice: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    rows = []
    for row in master_loop_shared_lattice.get("rows", []):
        coordinate_tuple = normalize_coordinate_tuple(row.get("coordinate_stamp", {}))
        rows.append(
            {
                **row,
                "coordinate_tuple": coordinate_tuple,
                "coordinate_stamp": coordinate_stamp_string(coordinate_tuple),
            }
        )
    return {
        **master_loop_shared_lattice,
        "generated_at": utc_now(),
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "coordinate_dimensions": COORDINATE_DIMENSIONS,
        "compiled_packet_law": {
            "manifest_seats": SHARED_TOTAL_SEATS,
            "active_seats": SHARED_ACTIVE_SEATS,
            "dormant_seats": SHARED_DORMANT_SEATS,
            "active_seats_per_agent": ACTIVE_SEATS_PER_AGENT,
            "synaptic_seats": LP57OMEGA_SYNAPTIC_SEAT_COUNT,
            "governance_fibers": LP57OMEGA_GOVERNANCE_FIBER_COUNT,
            "ownerable_packets": LP57OMEGA_OWNERABLE_PACKET_COUNT,
            "liminal_packets": LP57OMEGA_LIMINAL_PACKET_COUNT,
        },
        "row_count": len(rows),
        "rows": rows,
    }


def build_coordinate_registry(
    authority_records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    rows = []
    for record in authority_records:
        coordinate_tuple = record_coordinate_tuple(record)
        dense_kernel_ref = dense_kernel_ref_for_record(record)
        rows.append(
            {
                "node_id": record.get("record_id", ""),
                "node_kind": "record",
                "record_id": record.get("record_id", ""),
                "relative_path": record.get("relative_path", ""),
                "family": record.get("family", ""),
                "basis_anchor_ids": record.get("basis_anchor_ids", []),
                "primary_hemisphere": record.get("primary_hemisphere", ""),
                "stage_id": record.get("awakening_stage", ""),
                "target_systems": {
                    "MATH": ((record.get("hemisphere_routes") or {}).get("MATH", {}) or {}).get("target_system", ""),
                    "MYTH": ((record.get("hemisphere_routes") or {}).get("MYTH", {}) or {}).get("target_system", ""),
                },
                "coordinate_tuple": coordinate_tuple,
                "coordinate_stamp": coordinate_stamp_string(coordinate_tuple),
                "lookup_address": lookup_address(record, coordinate_tuple),
                "dense_kernel_ref": dense_kernel_ref,
                "docs_gate_status": docs_gate_status,
            }
        )
    return {
        "generated_at": utc_now(),
        "protocol_id": LP57OMEGA_PROTOCOL_ID,
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "record_count": len(rows),
        "coordinate_dimensions": COORDINATE_DIMENSIONS,
        "dense_kernel_overlay": {
            "mode": "kernel_overlay",
            "prior_seed_position": DENSE_65_PRIOR_SEED_POSITION,
            "ring_order": list(DENSE_65_RING_ORDER),
            "sigma_path": list(DENSE_65_SIGMA_PATH),
            "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
            "hidden_pole_rule": "first missing pole in A -> C -> B -> D, default A",
        },
        "rows": rows,
    }


def build_quest_contract_registry(
    loop_registry: dict[str, Any],
    agent_identity_registry: dict[str, Any],
    coordinate_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    coordinate_lookup = {
        row["record_id"]: row["lookup_address"] for row in coordinate_registry.get("rows", [])
    }
    identity_lookup = {
        (row["loop_number"], row["master_agent_id"]): row for row in agent_identity_registry["rows"]
    }
    rows = []
    for loop_row in loop_registry["rows"]:
        loop_number = int(loop_row["loop_id"])
        focus_record_ids = loop_row.get("focus_record_ids", [])
        focus_lookup_addresses = [
            coordinate_lookup[record_id]
            for record_id in focus_record_ids
            if record_id in coordinate_lookup
        ]
        for agent_row in LEGACY_MASTER_AGENTS:
            agent_id = str(agent_row["agent_id"])
            short_name = str(agent_row.get("short_name") or agent_id.replace("MASTER-", ""))
            agent_name = str(agent_row.get("name") or agent_row.get("role") or agent_id)
            identity = identity_lookup[(loop_number, agent_id)]
            hall_contract = {
                "quest_id": f"Q57-{loop_row['loop_key']}-{short_name}-HALL",
                "zone": "GUILD_HALL",
                "parent_loop": loop_row["loop_key"],
                "objective": HALL_OBJECTIVES[agent_id],
                "why_now": (
                    f"{loop_row['title']} is the dominant focus for {loop_row['loop_key']} "
                    f"and needs {short_name.lower()} support."
                ),
                "target_surfaces": [
                    rel(GUILD_HALL_BOARD_PATH),
                    rel(LP57OMEGA_GUILD_HALL_DOC_PATH),
                    rel(LP57OMEGA_LOOP_REGISTRY_PATH),
                ],
                "witness_needed": "One cited synthesis or route witness plus one restart-safe writeback.",
                "dependencies": [
                    rel(MASTER_LOOP_STATE_PATH),
                    rel(LP57OMEGA_LOOP_REGISTRY_PATH),
                    rel(LP57OMEGA_COORDINATE_REGISTRY_PATH),
                ],
                "coordinate_targets": focus_lookup_addresses[:3],
                "acceptance_rule": ACCEPTANCE_RULES[agent_id],
                "restart_seed": loop_row["restart_handoff"],
            }
            temple_contract = {
                "quest_id": f"TQ57-{loop_row['loop_key']}-{short_name}-TEMPLE",
                "zone": "TEMPLE",
                "parent_loop": loop_row["loop_key"],
                "objective": TEMPLE_OBJECTIVES[agent_id],
                "why_now": f"{loop_row['title']} must remain admissible, coordinate-complete, and replay-safe in {loop_row['loop_key']}.",
                "target_surfaces": [
                    rel(TEMPLE_QUEST_BOARD_PATH),
                    rel(LP57OMEGA_TEMPLE_DOC_PATH),
                    rel(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH),
                ],
                "witness_needed": "One governance witness plus one coordinate target and one restart seed.",
                "dependencies": [
                    rel(MASTER_AGENT_STATE_PATH),
                    rel(MASTER_LOOP_SHARED_LATTICE_PATH),
                    rel(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH),
                ],
                "coordinate_targets": focus_lookup_addresses[:3],
                "acceptance_rule": ACCEPTANCE_RULES[agent_id],
                "restart_seed": loop_row["restart_handoff"],
            }
            rows.append(
                {
                    "loop_id": loop_row["loop_key"],
                    "loop_number": loop_number,
                    "master_agent_id": agent_id,
                    "master_agent_label": agent_name,
                    "agent_id_tag": identity["agent_id_tag"],
                    "focus_record_ids": focus_record_ids,
                    "focus_lookup_addresses": focus_lookup_addresses[:3],
                    "hall_contract": hall_contract,
                    "temple_contract": temple_contract,
                    "docs_gate_status": docs_gate_status,
                }
            )
    return {
        "generated_at": utc_now(),
        "protocol_id": LP57OMEGA_PROTOCOL_ID,
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "loop_count": loop_registry["loop_count"],
        "master_agent_count": LP57OMEGA_MASTER_AGENT_COUNT,
        "row_count": len(rows),
        "public_board_caps": {"hall": PUBLIC_PROMOTION_CAP, "temple": PUBLIC_PROMOTION_CAP},
        "quest_contract_fields": QUEST_CONTRACT_FIELDS,
        "rows": rows,
    }


def build_master_ledger_registry(
    loop_registry: dict[str, Any],
    agent_identity_registry: dict[str, Any],
    quest_contract_registry: dict[str, Any],
    coordinate_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    loop_lookup = {row["loop_number"]: row for row in loop_registry["rows"]}
    coordinate_lookup = {
        row["record_id"]: row for row in coordinate_registry.get("rows", [])
    }
    linked_agent_lookup: dict[int, list[str]] = {}
    for row in agent_identity_registry["rows"]:
        linked_agent_lookup.setdefault(row["loop_number"], []).append(row["agent_id_tag"])
    rows = []
    for contract_row in quest_contract_registry["rows"]:
        loop_number = contract_row["loop_number"]
        loop_row = loop_lookup[loop_number]
        agent_id = contract_row["master_agent_id"]
        dense_kernel_ref = None
        for focus_record_id in contract_row.get("focus_record_ids", []):
            candidate = (coordinate_lookup.get(focus_record_id) or {}).get("dense_kernel_ref")
            if candidate:
                dense_kernel_ref = candidate
                break
        rows.append(
            {
                "agent_id": contract_row["agent_id_tag"],
                "loop_number": loop_number,
                "parent_agent": agent_id,
                "coordinate_stamp": next(
                    row["coordinate_stamp"]
                    for row in agent_identity_registry["rows"]
                    if row["loop_number"] == loop_number and row["master_agent_id"] == agent_id
                ),
                "source_region": f"{loop_row['ring']}::{loop_row['title']}",
                "action_type": ACTION_TYPES[agent_id],
                "affected_nodes": [
                    loop_row["loop_key"],
                    contract_row["hall_contract"]["quest_id"],
                    contract_row["temple_contract"]["quest_id"],
                ],
                "summary_of_change": (
                    f"{contract_row['master_agent_label']} advances {loop_row['title']} by binding Hall and Temple work "
                    "to the canonical LP57Omega loop surface."
                ),
                "reason_for_change": loop_row["advancement_signature"],
                "integration_gain": loop_row["expected_structural_gain"],
                "compression_gain": loop_row["expected_mapping_gain"],
                "unresolved_followups": [loop_row["restart_handoff"]],
                "linked_quests": [
                    contract_row["hall_contract"]["quest_id"],
                    contract_row["temple_contract"]["quest_id"],
                ],
                "linked_agents": linked_agent_lookup[loop_number],
                "dense_kernel_ref": dense_kernel_ref,
                "revision_confidence": 0.93,
                "timestamp_internal": utc_now(),
                "docs_gate_status": docs_gate_status,
            }
        )
    return {
        "generated_at": utc_now(),
        "protocol_id": LP57OMEGA_PROTOCOL_ID,
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "loop_count": loop_registry["loop_count"],
        "row_count": len(rows),
        "ledger_fields": LEDGER_FIELDS,
        "rows": rows,
    }


def build_manifest(
    loop_registry: dict[str, Any],
    agent_identity_registry: dict[str, Any],
    coordinate_registry: dict[str, Any],
    quest_contract_registry: dict[str, Any],
    master_ledger_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "protocol_id": LP57OMEGA_PROTOCOL_ID,
        "protocol_display_name": LP57OMEGA_PROTOCOL_DISPLAY,
        "docs_gate_status": docs_gate_status,
        "counts": {
            "loops": loop_registry["loop_count"],
            "master_agents": LP57OMEGA_MASTER_AGENT_COUNT,
            "agent_identity_rows": agent_identity_registry["row_count"],
            "coordinate_rows": coordinate_registry["record_count"],
            "quest_contract_rows": quest_contract_registry["row_count"],
            "master_ledger_rows": master_ledger_registry["row_count"],
            "shared_lattice_total_seats": SHARED_TOTAL_SEATS,
            "shared_lattice_active_seats": SHARED_ACTIVE_SEATS,
            "shared_lattice_dormant_seats": SHARED_DORMANT_SEATS,
            "public_hall_cap": PUBLIC_PROMOTION_CAP,
            "public_temple_cap": PUBLIC_PROMOTION_CAP,
        },
        "outputs": {
            "master_loop_state": str(MASTER_LOOP_STATE_PATH),
            "master_agent_state": str(MASTER_AGENT_STATE_PATH),
            "master_loop_shared_lattice": str(MASTER_LOOP_SHARED_LATTICE_PATH),
            "loop_registry": str(LP57OMEGA_LOOP_REGISTRY_PATH),
            "agent_identity_registry": str(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH),
            "coordinate_registry": str(LP57OMEGA_COORDINATE_REGISTRY_PATH),
            "quest_contract_registry": str(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH),
            "master_ledger_registry": str(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH),
            "manifest": str(LP57OMEGA_MANIFEST_PATH),
            "liminal_coordinate_standard": str(LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH),
            "agent_ledger_standard": str(LP57OMEGA_AGENT_LEDGER_STANDARD_PATH),
            "seed_inversion_standard": str(LP57OMEGA_SEED_INVERSION_STANDARD_PATH),
            "seed_inversion_standard_json": str(LP57OMEGA_SEED_INVERSION_STANDARD_JSON_PATH),
            "dense_65_shell_registry": str(DENSE_65_SHELL_REGISTRY_PATH),
            "dense_65_witness_registry": str(DENSE_65_RQT_WITNESS_REGISTRY_PATH),
            "dense_65_overflow_registry": str(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH),
            "dense_65_manifest": str(DENSE_65_MANIFEST_PATH),
        },
        "notes": [
            "LP57Omega remains the canonical loop authority; AP6D remains assistive only.",
            "Visible Hall and Temple promotions stay macro-sized under the public 8/8 cap.",
            "Full-corpus coordinates are derived from existing family, basis, route, stage, and appendix truth.",
            "DenseKernel65 is a subordinate 65-shell overlay and must never be treated as a global coordinate remap.",
        ],
    }


LP57OMEGA_PROTOCOL_DISPLAY = "LP-57Omega"


def render_index_markdown(manifest: dict[str, Any], master_loop_state: dict[str, Any]) -> str:
    counts = manifest["counts"]
    summary = master_loop_state.get("current_cycle_summary", {})
    return f"""# LP-57Omega Protocol Index

Docs gate: `{manifest['docs_gate_status']}`
Protocol: `{LP57OMEGA_PROTOCOL_DISPLAY}`

## Canonical Entry Surfaces

- loop state: `{MASTER_LOOP_STATE_PATH}`
- agent state: `{MASTER_AGENT_STATE_PATH}`
- shared lattice: `{MASTER_LOOP_SHARED_LATTICE_PATH}`

## Counts

- loops: `{counts['loops']}`
- master agents: `{counts['master_agents']}`
- agent identity rows: `{counts['agent_identity_rows']}`
- coordinate rows: `{counts['coordinate_rows']}`
- quest contract rows: `{counts['quest_contract_rows']}`
- master ledger rows: `{counts['master_ledger_rows']}`
- shared lattice: `{counts['shared_lattice_total_seats']} indexed / {counts['shared_lattice_active_seats']} ACTIVE / {counts['shared_lattice_dormant_seats']} DORMANT`

## Current Cycle

- completed loop: `{summary.get('completed_loop', '')}`
- active loop: `{summary.get('active_loop', '')}`
- lead agent: `{summary.get('current_lead_agent', '')}`
- restart seed: `{summary.get('next_restart_seed', '')}`
"""


def render_framework_markdown(master_agent_state: dict[str, Any], loop_registry: dict[str, Any]) -> str:
    agent_rows = [
        [row["agent_id"], row["name"], row["public_quest_rights"], str(row["seat_budget_active"])]
        for row in master_agent_state.get("agents", [])
    ]
    return f"""# LP-57Omega Master Loop Framework

Current law: `A1 Synthesizer -> A2 Planner -> A3 Worker -> A4 Pruner`

## Master Agents

{markdown_table(["Agent", "Name", "Quest Rights", "Active Seats"], agent_rows)}

## Seat Compilation

- conceptual seats per loop: `{SHARED_TOTAL_SEATS}`
- synaptic seats: `{LP57OMEGA_SYNAPTIC_SEAT_COUNT}`
- governance fibers: `{LP57OMEGA_GOVERNANCE_FIBER_COUNT}`
- ownerable packets: `{LP57OMEGA_OWNERABLE_PACKET_COUNT}`
- liminal packets: `{LP57OMEGA_LIMINAL_PACKET_COUNT}`
- protocol loop rows: `{loop_registry['loop_count']}`
"""


def render_coordinate_markdown(coordinate_registry: dict[str, Any]) -> str:
    sample = coordinate_registry["rows"][0] if coordinate_registry.get("rows") else {}
    sample_dense = sample.get("dense_kernel_ref") or {}
    dimension_rows = [
        ["Xs", "scope state"],
        ["Ys", "hemisphere or bridge relation"],
        ["Zs", "deep-mode surface"],
        ["Ts", "topological resolution band"],
        ["Qs", "mathematical density"],
        ["Rs", "symbolic density"],
        ["Cs", "compression state"],
        ["Fs", "framework lens"],
        ["Ms", "manuscript branch"],
        ["Ns", "neural or mycelial connectivity"],
        ["Hs", "hierarchy level"],
        ["OMEGAs", "zero-point or aether relation"],
] 
    return f"""# LP-57Omega Coordinate Standard

Coordinate rows: `{coordinate_registry['record_count']}`
Dense kernel overlay: `DenseKernelRef65` subordinate to the top-level 12D coordinate tuple.

## Dimensions

{markdown_table(["Dimension", "Meaning"], dimension_rows)}

## Sample Lookup

- record id: `{sample.get('record_id', '')}`
- coordinate stamp: `{sample.get('coordinate_stamp', '')}`
- lookup address: `{sample.get('lookup_address', '')}`
- dense kernel symmetry: `{sample_dense.get('symmetry_record_id', 'NONE')}`
- dense kernel sigma path: `{' -> '.join((sample_dense.get('sigma_path') or coordinate_registry.get('dense_kernel_overlay', {}).get('sigma_path') or []))}`
"""


def render_quest_and_ledger_markdown(
    quest_contract_registry: dict[str, Any],
    master_ledger_registry: dict[str, Any],
) -> str:
    sample_contract = quest_contract_registry["rows"][0] if quest_contract_registry.get("rows") else {}
    sample_ledger = master_ledger_registry["rows"][0] if master_ledger_registry.get("rows") else {}
    contract_rows = [[field, "required"] for field in QUEST_CONTRACT_FIELDS]
    ledger_rows = [[field, "required"] for field in LEDGER_FIELDS]
    return f"""# LP-57Omega Quest and Ledger Standard

Quest rows: `{quest_contract_registry['row_count']}`
Ledger rows: `{master_ledger_registry['row_count']}`

## Quest Contract Fields

{markdown_table(["Field", "Status"], contract_rows)}

## Ledger Fields

{markdown_table(["Field", "Status"], ledger_rows)}

## Sample Hall Quest

- hall quest id: `{(sample_contract.get('hall_contract') or {}).get('quest_id', '')}`
- temple quest id: `{(sample_contract.get('temple_contract') or {}).get('quest_id', '')}`

## Sample Ledger Entry

- agent id: `{sample_ledger.get('agent_id', '')}`
- action type: `{sample_ledger.get('action_type', '')}`
- linked quests: `{', '.join(sample_ledger.get('linked_quests', []))}`
- dense kernel ref: `{((sample_ledger.get('dense_kernel_ref') or {}).get('symmetry_record_id', 'NONE'))}`
"""


def render_liminal_coordinate_standard(
    manifest: dict[str, Any],
    coordinate_registry: dict[str, Any],
) -> str:
    overlay = coordinate_registry.get("dense_kernel_overlay", {})
    rows = [
        [dimension, meaning]
        for dimension, meaning in [
        ("Xs", "scope state"),
        ("Ys", "hemisphere or bridge relation"),
        ("Zs", "deep-mode surface"),
        ("Ts", "topological resolution band"),
        ("Qs", "mathematical density"),
        ("Rs", "symbolic density"),
        ("Cs", "compression state"),
        ("Fs", "framework lens"),
        ("Ms", "manuscript branch"),
        ("Ns", "neural or mycelial connectivity"),
        ("Hs", "hierarchy level"),
        ("OMEGAs", "zero-point or aether relation"),
    ]
    ]
    return f"""# LP-57Omega Liminal Coordinate Standard

- Docs gate: `{manifest['docs_gate_status']}`
- Top-level coordinate law: `12D tuple remains canonical`
- Subordinate overlay: `DenseKernelRef65`
- Overlay mode: `kernel_overlay`
- Prior seed/header shell: `{overlay.get('prior_seed_position', DENSE_65_PRIOR_SEED_POSITION)}`
- Ring gauge: `A=Fire, C=Air, B=Water, D=Earth`
- Ring order: `{' -> '.join(overlay.get('ring_order', DENSE_65_RING_ORDER))}`
- Opposite-pole policy: `adjacent bridge or Z* tunnel only`
- Sigma path: `{' -> '.join(overlay.get('sigma_path', DENSE_65_SIGMA_PATH))}`
- Rotation authority: `{overlay.get('authority_refs', {}).get('rotation_authority', DENSE_65_AUTHORITY_REFS['rotation_authority'])}`
- Antispin authority: `{overlay.get('authority_refs', {}).get('antispin_authority', DENSE_65_AUTHORITY_REFS['antispin_authority'])}`
- Hidden pole rule: `{overlay.get('hidden_pole_rule', 'first missing pole in A -> C -> B -> D, default A')}`

## Coordinate Axes

{markdown_table(["Dimension", "Meaning"], rows)}

## Dense Kernel Ref65

- `dense_kernel_ref` is optional on LP57 coordinate and ledger rows.
- It points into the sealed `1/65 -> 65/65` kernel without replacing the top-level LP57 lookup address.
- The global `8677` coordinate field stays pointer-based and intact.
"""


def render_agent_ledger_standard(manifest: dict[str, Any]) -> str:
    rows = [[field, "required"] for field in LEDGER_FIELDS]
    rows.append(["dense_kernel_ref", "optional overlay pointer"])
    return f"""# LP-57Omega Agent Ledger Standard

- Docs gate: `{manifest['docs_gate_status']}`
- Continuity law: `append-only, quest-linked, coordinate-stamped`
- Overlay law: `dense_kernel_ref is optional and never replaces the top-level coordinate stamp`

## Required Fields

{markdown_table(["Field", "Status"], rows)}

## Overlay Recording Rule

- When a ledger action is routed through a dense-shell focus record, preserve the first lawful `DenseKernelRef65` binding in `dense_kernel_ref`.
- Receipts and change feeds remain witness history; registries and manifests remain canonical state.
"""


def render_seed_inversion_standard(
    manifest: dict[str, Any],
    coordinate_registry: dict[str, Any],
) -> str:
    overlay = coordinate_registry.get("dense_kernel_overlay", {})
    return f"""# LP-57Omega Seed Inversion Standard

- Docs gate: `{manifest['docs_gate_status']}`
- Status: `CANONICAL_KERNEL_OVERLAY`
- Mode: `kernel_overlay`, not global remap
- Header / prior seed shell: `1/65 = H00`
- Dense shell proper: `2/65 -> 65/65`
- Ring gauge: `A=Fire, C=Air, B=Water, D=Earth`
- Ring order: `{' -> '.join(overlay.get('ring_order', DENSE_65_RING_ORDER))}`
- Sigma path: `{' -> '.join(overlay.get('sigma_path', DENSE_65_SIGMA_PATH))}`
- Rotation authority: `{overlay.get('authority_refs', {}).get('rotation_authority', DENSE_65_AUTHORITY_REFS['rotation_authority'])}`
- Antispin authority: `{overlay.get('authority_refs', {}).get('antispin_authority', DENSE_65_AUTHORITY_REFS['antispin_authority'])}`
- Hidden pole rule: `first missing pole in A -> C -> B -> D, default A`

## Canonical Output Paths

- shell registry: `{DENSE_65_SHELL_REGISTRY_PATH}`
- witness registry: `{DENSE_65_RQT_WITNESS_REGISTRY_PATH}`
- overflow registry: `{DENSE_65_RQT_OVERFLOW_REGISTRY_PATH}`
- manifest: `{DENSE_65_MANIFEST_PATH}`
"""


def build_seed_inversion_standard_json(
    manifest: dict[str, Any],
    coordinate_registry: dict[str, Any],
) -> dict[str, Any]:
    overlay = coordinate_registry.get("dense_kernel_overlay", {})
    return {
        "generated_at": utc_now(),
        "docs_gate_status": manifest["docs_gate_status"],
        "status": "CANONICAL_KERNEL_OVERLAY",
        "mode": "kernel_overlay",
        "prior_seed_position": overlay.get("prior_seed_position", DENSE_65_PRIOR_SEED_POSITION),
        "header_record_id": "H00",
        "dense_shell_range": "2/65 -> 65/65",
        "group_counts": {"H": 1, "P": 4, "S": 15, "R": 15, "Q": 15, "T": 15},
        "ring_gauge": {"A": "Fire", "C": "Air", "B": "Water", "D": "Earth"},
        "ring_order": overlay.get("ring_order", list(DENSE_65_RING_ORDER)),
        "sigma_path": overlay.get("sigma_path", list(DENSE_65_SIGMA_PATH)),
        "authority_refs": overlay.get("authority_refs", dict(DENSE_65_AUTHORITY_REFS)),
        "hidden_pole_rule": "first missing pole in A -> C -> B -> D, default A",
        "opposite_pole_policy": "adjacent_bridge_or_zstar_tunnel_only",
        "shell_registry_path": str(DENSE_65_SHELL_REGISTRY_PATH),
        "witness_registry_path": str(DENSE_65_RQT_WITNESS_REGISTRY_PATH),
        "overflow_registry_path": str(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH),
        "manifest_path": str(DENSE_65_MANIFEST_PATH),
    }


def render_signature_plan_markdown(loop_registry: dict[str, Any]) -> str:
    rows = [
        [
            loop_row["loop_key"],
            loop_row.get("title", loop_row.get("dominant_focus", "")),
            loop_row.get("synthesis_objective", loop_row.get("primary_synthesis_objective", "")),
            loop_row.get("planning_objective", loop_row.get("primary_planning_objective", "")),
            loop_row.get(
                "implementation_objective",
                loop_row.get("primary_implementation_objective", ""),
            ),
            loop_row.get(
                "compression_objective",
                loop_row.get("primary_compression_objective", ""),
            ),
            loop_row.get("expected_structural_gain", ""),
            loop_row.get("expected_mapping_gain", ""),
        ]
        for loop_row in loop_registry["rows"]
    ]
    return f"""# LP-57Omega 57-Loop Signature Plan

{markdown_table(
    ["Loop", "Title", "Synthesis", "Planning", "Implementation", "Pruning", "Structural Gain", "Mapping Gain"],
    rows,
)}
"""


def render_receipt_markdown(manifest: dict[str, Any]) -> str:
    counts = manifest["counts"]
    return f"""# LP-57Omega Receipt

- generated at: `{manifest['generated_at']}`
- docs gate: `{manifest['docs_gate_status']}`
- loops: `{counts['loops']}`
- agent identity rows: `{counts['agent_identity_rows']}`
- coordinate rows: `{counts['coordinate_rows']}`
- quest contract rows: `{counts['quest_contract_rows']}`
- master ledger rows: `{counts['master_ledger_rows']}`
- dense kernel overlay: `DenseKernel65 subordinate 65-shell`
- dense shell registry: `{DENSE_65_SHELL_REGISTRY_PATH.name}`
- canonical loop state: `{MASTER_LOOP_STATE_PATH}`
"""


def resolve_active_loop_row(loop_registry: dict[str, Any]) -> dict[str, Any]:
    loop_rows = list(loop_registry.get("rows", []))
    if not loop_rows:
        return {
            "loop_id": ACTIVE_LOOP_ID,
            "loop_number": ACTIVE_LOOP_ID,
            "loop_key": loop_key(ACTIVE_LOOP_ID),
            "title": "UNAVAILABLE",
            "status": "UNKNOWN",
        }
    for row in loop_rows:
        if str(row.get("status", "")).upper() == "ACTIVE":
            return row
    for row in loop_rows:
        if row.get("loop_number") == ACTIVE_LOOP_ID or row.get("loop_id") == ACTIVE_LOOP_ID:
            return row
    return loop_rows[min(len(loop_rows) - 1, max(ACTIVE_LOOP_ID - 1, 0))]


def resolve_planner_row(
    quest_contract_registry: dict[str, Any],
    active_loop: dict[str, Any],
) -> dict[str, Any]:
    quest_rows = list(quest_contract_registry.get("rows", []))
    loop_number = int(active_loop.get("loop_number", active_loop.get("loop_id", ACTIVE_LOOP_ID)))
    for row in quest_rows:
        if row.get("loop_number") == loop_number and row.get("master_agent_id") == "MASTER-PLANNER":
            return row
    for row in quest_rows:
        if row.get("master_agent_id") == "MASTER-PLANNER":
            return row
    return {
        "hall_contract": {
            "quest_id": "LP57-HALL-UNAVAILABLE",
            "objective": "Planner Hall contract unavailable in quest registry.",
            "restart_seed": "UNAVAILABLE",
        },
        "temple_contract": {
            "quest_id": "LP57-TEMPLE-UNAVAILABLE",
            "objective": "Planner Temple contract unavailable in quest registry.",
            "restart_seed": "UNAVAILABLE",
        },
    }


def render_hall_doc(
    loop_registry: dict[str, Any],
    quest_contract_registry: dict[str, Any],
    manifest: dict[str, Any],
) -> str:
    active_loop = resolve_active_loop_row(loop_registry)
    planner_row = resolve_planner_row(quest_contract_registry, active_loop)
    promotion_rows = [
        [item["quest_id"], item["title"], item["seat_addr_6d"], item["restart_seed"]]
        for item in hall_promotions_for_loop(
            int(active_loop.get("loop_number", active_loop.get("loop_id", ACTIVE_LOOP_ID)))
        )
    ]
    return f"""# LP-57Omega Guild Hall Protocol

Docs gate: `{manifest['docs_gate_status']}`
Active loop: `{active_loop.get('loop_key', loop_key(ACTIVE_LOOP_ID))} {active_loop.get('title', 'UNAVAILABLE')}`

## Hall Contract

- quest id: `{planner_row['hall_contract']['quest_id']}`
- objective: `{planner_row['hall_contract']['objective']}`
- restart seed: `{planner_row['hall_contract']['restart_seed']}`
- dense kernel family: `DenseKernel65 overlay (subordinate quest family, not global remap)`

## Public Hall Promotions

{markdown_table(["Quest", "Title", "Seat", "Restart"], promotion_rows)}
"""


def render_temple_doc(
    loop_registry: dict[str, Any],
    quest_contract_registry: dict[str, Any],
    manifest: dict[str, Any],
) -> str:
    active_loop = resolve_active_loop_row(loop_registry)
    planner_row = resolve_planner_row(quest_contract_registry, active_loop)
    promotion_rows = [
        [item["quest_id"], item["title"], item["seat_addr_6d"], item["restart_seed"]]
        for item in temple_promotions_for_loop(
            int(active_loop.get("loop_number", active_loop.get("loop_id", ACTIVE_LOOP_ID)))
        )
    ]
    return f"""# LP-57Omega Temple Protocol

Docs gate: `{manifest['docs_gate_status']}`
Active loop: `{active_loop.get('loop_key', loop_key(ACTIVE_LOOP_ID))} {active_loop.get('title', 'UNAVAILABLE')}`

## Temple Contract

- quest id: `{planner_row['temple_contract']['quest_id']}`
- objective: `{planner_row['temple_contract']['objective']}`
- restart seed: `{planner_row['temple_contract']['restart_seed']}`
- dense kernel family: `DenseKernel65 overlay with AppA -> AppI -> AppM transfer law`

## Public Temple Promotions

{markdown_table(["Quest", "Title", "Seat", "Restart"], promotion_rows)}
"""


def render_deep_control_doc(manifest: dict[str, Any]) -> str:
    return f"""# LP-57Omega Deep Control

Docs gate: `{manifest['docs_gate_status']}`

## Canonical Support Registries

- loop registry: `{LP57OMEGA_LOOP_REGISTRY_PATH}`
- agent identity registry: `{LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH}`
- coordinate registry: `{LP57OMEGA_COORDINATE_REGISTRY_PATH}`
- quest contract registry: `{LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH}`
- master ledger registry: `{LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH}`
- dense shell registry: `{DENSE_65_SHELL_REGISTRY_PATH}`
- dense shell witness registry: `{DENSE_65_RQT_WITNESS_REGISTRY_PATH}`
- coordinate standard: `{LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH}`
- seed inversion standard: `{LP57OMEGA_SEED_INVERSION_STANDARD_PATH}`
"""


def render_external_receipt(manifest: dict[str, Any]) -> str:
    return f"""# LP-57Omega Protocol Receipt

- generated at: `{manifest['generated_at']}`
- docs gate: `{manifest['docs_gate_status']}`
- canonical loop state: `{MASTER_LOOP_STATE_PATH}`
- canonical agent state: `{MASTER_AGENT_STATE_PATH}`
- canonical lattice: `{MASTER_LOOP_SHARED_LATTICE_PATH}`
- support manifest: `{LP57OMEGA_MANIFEST_PATH}`
- dense shell registry: `{DENSE_65_SHELL_REGISTRY_PATH}`
- dense shell is overlay-only and does not remap LP57 globally
"""


def render_hall_board_body(master_loop_state: dict[str, Any], manifest: dict[str, Any]) -> str:
    summary = master_loop_state.get("current_cycle_summary", {})
    lines = [
        "## LP-57Omega Hall Quest Interface",
        "",
        f"- Date: `{str(manifest['generated_at'])[:10]}`",
        f"- Docs Gate: `{manifest['docs_gate_status']}`",
        "- Canonical authority: `LP-57OMEGA / master_loop_state_57.json`",
        f"- Completed loop: `{summary.get('completed_loop', 'UNKNOWN')}`",
        f"- Active loop: `{summary.get('active_loop', 'UNKNOWN')}`",
        f"- Active membrane: `{LIVE_LAW['active_membrane']}`",
        f"- Feeder stack: `{', '.join(LIVE_LAW['feeder_stack'])}`",
        f"- Planner public cap: `{PUBLIC_PROMOTION_CAP} Hall quests per loop`",
        f"- Shared lattice: `{SHARED_TOTAL_SEATS} indexed / {SHARED_ACTIVE_SEATS} ACTIVE / {SHARED_DORMANT_SEATS} DORMANT`",
        f"- Coordinate registry: `{LP57OMEGA_COORDINATE_REGISTRY_PATH.name}`",
        f"- Quest registry: `{LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH.name}`",
        f"- Ledger registry: `{LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH.name}`",
        f"- Dense kernel overlay: `{DENSE_65_SHELL_REGISTRY_PATH.name}`",
        "",
        "### Loop 2 Public Hall Promotions",
    ]
    for item in hall_promotions_for_loop(ACTIVE_LOOP_ID):
        lines.append(
            f"- `{item['quest_id']}` :: {item['title']} :: seat `{item['seat_addr_6d']}` :: restart `{item['restart_seed']}`"
        )
    return "\n".join(lines)


def render_temple_board_body(master_loop_state: dict[str, Any], manifest: dict[str, Any]) -> str:
    summary = master_loop_state.get("current_cycle_summary", {})
    lines = [
        "## LP-57Omega Temple Quest Interface",
        "",
        f"- Date: `{str(manifest['generated_at'])[:10]}`",
        f"- Docs Gate: `{manifest['docs_gate_status']}`",
        "- Canonical authority: `LP-57OMEGA / master_loop_state_57.json`",
        f"- Completed loop: `{summary.get('completed_loop', 'UNKNOWN')}`",
        f"- Active loop: `{summary.get('active_loop', 'UNKNOWN')}`",
        f"- Active membrane: `{LIVE_LAW['active_membrane']}`",
        f"- Live Hall feeder: `{LIVE_LAW['feeder_stack'][0]}`",
        f"- Planner public cap: `{PUBLIC_PROMOTION_CAP} Temple quests per loop`",
        f"- Coordinate registry: `{LP57OMEGA_COORDINATE_REGISTRY_PATH.name}`",
        f"- Quest registry: `{LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH.name}`",
        f"- Ledger registry: `{LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH.name}`",
        f"- Dense kernel overlay: `{DENSE_65_SHELL_REGISTRY_PATH.name}`",
        "",
        "### Loop 2 Public Temple Promotions",
    ]
    for item in temple_promotions_for_loop(ACTIVE_LOOP_ID):
        lines.append(
            f"- `{item['quest_id']}` :: {item['title']} :: seat `{item['seat_addr_6d']}` :: restart `{item['restart_seed']}`"
        )
    return "\n".join(lines)


def build_lp57omega_payloads(
    *,
    control_manifest: dict[str, Any],
    full_corpus_authority_registry: dict[str, Any],
    full_corpus_basis_crosswalk_registry: dict[str, Any],
    full_corpus_route_coverage_registry: dict[str, Any],
    full_corpus_awakening_stage_registry: dict[str, Any],
    full_corpus_awakening_agent_transition_registry: dict[str, Any],
    full_corpus_appendix_governance_ledger: dict[str, Any],
    ap6d_57_loop_control_registry: dict[str, Any],
    ap6d_57_agent_lane_registry: dict[str, Any],
    ap6d_57_nested_seat_manifest: dict[str, Any],
    docs_gate_status: str,
    current_guild_hall_board_text: str,
    current_temple_board_text: str,
) -> dict[str, Any]:
    master_loop_state = json.loads(MASTER_LOOP_STATE_PATH.read_text(encoding="utf-8"))
    master_agent_state = json.loads(MASTER_AGENT_STATE_PATH.read_text(encoding="utf-8"))
    master_loop_shared_lattice = json.loads(
        MASTER_LOOP_SHARED_LATTICE_PATH.read_text(encoding="utf-8")
    )
    if "loops" not in master_loop_state:
        next57_state_path = SELF_ACTUALIZE_ROOT / "next57_four_agent_corpus_cycle_state.json"
        next57_state = json.loads(next57_state_path.read_text(encoding="utf-8"))

        def receipt_paths_for_loop(loop_row: dict[str, Any]) -> dict[str, str]:
            artifacts = list(loop_row.get("required_artifacts", []))
            keys = [
                "deep_synthesis_packet",
                "quest_emission_bundle",
                "execution_receipt_bundle",
                "compression_receipt",
                "loop_completion_receipt",
            ]
            return {
                key: (
                    f"self_actualize/{artifacts[index]}"
                    if index < len(artifacts)
                    else f"self_actualize/{key}_{str(loop_row.get('loop_number', 0)).zfill(2)}.json"
                )
                for index, key in enumerate(keys)
            }

        hydrated_loops = []
        loop_catalog = list(next57_state.get("loop_catalog", []))
        canonical_cycle_registry_path = master_loop_state.get("canonical_cycle_registry")
        canonical_cycle_registry: dict[str, Any] = {}
        if canonical_cycle_registry_path:
            candidate_path = WORKSPACE_ROOT / str(canonical_cycle_registry_path)
            if candidate_path.is_file():
                canonical_cycle_registry = json.loads(candidate_path.read_text(encoding="utf-8"))
        if not loop_catalog:
            loop_catalog = list(canonical_cycle_registry.get("loops", []))
        if not loop_catalog:
            loop_catalog = list(ap6d_57_loop_control_registry.get("rows", []))
        active_loop_raw = (next57_state.get("active_loop") or {}).get(
            "loop_number",
            canonical_cycle_registry.get("current_loop_id", ACTIVE_LOOP_ID),
        )
        active_loop_number = int(str(active_loop_raw).replace("L", "") or ACTIVE_LOOP_ID)
        for loop_row in loop_catalog:
            loop_number = int(loop_row.get("loop_number", 0))
            if loop_number < active_loop_number:
                status = "COMPLETED"
            elif loop_number == active_loop_number:
                status = "ACTIVE"
            else:
                status = "PENDING"
            dominant_focus = loop_row.get("dominant_focus") or loop_row.get("title", "")
            hydrated_loops.append(
                {
                    "loop_id": loop_number,
                    "ring": loop_row.get("pass_state", loop_row.get("stage_id", "")),
                    "title": dominant_focus,
                    "dominant_focus": dominant_focus,
                    "synthesis_objective": loop_row.get(
                        "primary_synthesis_objective",
                        loop_row.get("synthesis_objective", ""),
                    ),
                    "planning_objective": loop_row.get(
                        "primary_planning_objective",
                        loop_row.get("planning_objective", ""),
                    ),
                    "implementation_objective": loop_row.get(
                        "primary_implementation_objective",
                        loop_row.get("implementation_objective", ""),
                    ),
                    "compression_objective": loop_row.get(
                        "primary_compression_objective",
                        loop_row.get("compression_objective", ""),
                    ),
                    "expected_structural_gain": loop_row.get("expected_structural_gain", ""),
                    "expected_mapping_gain": loop_row.get("expected_mapping_gain", ""),
                    "lead_agent": "MASTER-SYNTHESIZER",
                    "status": status,
                    "receipt_paths": loop_row.get("receipt_paths") or receipt_paths_for_loop(loop_row),
                    "advancement_tuple": {
                        "family_code": loop_row.get("family_code", ""),
                        "family_root": loop_row.get("family_root", ""),
                        "hall_packet_id": loop_row.get("hall_packet_id", ""),
                        "temple_packet_id": loop_row.get("temple_packet_id", ""),
                        "queue_delta_id": loop_row.get("queue_delta_id", ""),
                    },
                }
            )
        completed_loop = next57_state.get("completed_loop", {})
        active_loop = next57_state.get("active_loop", {})
        if not active_loop and hydrated_loops:
            active_loop = next(
                (row for row in hydrated_loops if row.get("loop_id") == active_loop_number),
                hydrated_loops[min(len(hydrated_loops) - 1, max(active_loop_number - 1, 0))],
            )
        master_loop_state = {
            "generated_at": next57_state.get("generated_at", utc_now()),
            "truth": next57_state.get("truth", "OK"),
            "status": "LIVE_AUTHORITY",
            "protocol_id": LP57OMEGA_PROTOCOL_ID,
            "canonical_authority": next57_state.get("canonical_authority", {}),
            "current_cycle_summary": {
                "completed_loop": completed_loop.get("dominant_focus", ""),
                "active_loop": active_loop.get("dominant_focus", ""),
                "current_lead_agent": "MASTER-SYNTHESIZER",
                "hall_frontier": active_loop.get("hall_macro_id", ""),
                "temple_frontier": active_loop.get("temple_macro_id", ""),
                "next_restart_seed": active_loop.get("restart_seed", ""),
                "required_cycle_outputs": [],
            },
            "loops": hydrated_loops,
        }
    authority_records = list(full_corpus_authority_registry.get("records", []))

    loop_registry, focus_by_loop = build_loop_registry(
        master_loop_state=master_loop_state,
        docs_gate_status=docs_gate_status,
        focus_records=authority_records,
    )
    enriched_master_loop_state = enrich_master_loop_state(
        master_loop_state=master_loop_state,
        loop_registry=loop_registry,
        docs_gate_status=docs_gate_status,
    )
    (
        agent_identity_registry,
        enriched_master_agent_state,
    ) = build_agent_identity_registry(
        master_agent_state=master_agent_state,
        loop_registry=loop_registry,
        docs_gate_status=docs_gate_status,
    )
    enriched_shared_lattice = build_master_loop_shared_lattice(
        master_loop_shared_lattice=master_loop_shared_lattice,
        docs_gate_status=docs_gate_status,
    )
    coordinate_registry = build_coordinate_registry(
        authority_records=authority_records,
        docs_gate_status=docs_gate_status,
    )
    quest_contract_registry = build_quest_contract_registry(
        loop_registry=loop_registry,
        agent_identity_registry=agent_identity_registry,
        coordinate_registry=coordinate_registry,
        docs_gate_status=docs_gate_status,
    )
    master_ledger_registry = build_master_ledger_registry(
        loop_registry=loop_registry,
        agent_identity_registry=agent_identity_registry,
        quest_contract_registry=quest_contract_registry,
        coordinate_registry=coordinate_registry,
        docs_gate_status=docs_gate_status,
    )
    manifest = build_manifest(
        loop_registry=loop_registry,
        agent_identity_registry=agent_identity_registry,
        coordinate_registry=coordinate_registry,
        quest_contract_registry=quest_contract_registry,
        master_ledger_registry=master_ledger_registry,
        docs_gate_status=docs_gate_status,
    )
    manifest["counts"].update(
        {
            "full_corpus_records": full_corpus_authority_registry.get("record_count", 0),
            "full_corpus_basis_rows": full_corpus_basis_crosswalk_registry.get(
                "record_count",
                0,
            ),
            "full_corpus_route_rows": full_corpus_route_coverage_registry.get(
                "record_count",
                0,
            ),
            "full_corpus_stage_assignments": full_corpus_awakening_stage_registry.get(
                "record_assignment_count",
                0,
            ),
            "full_corpus_agent_transition_rows": (
                full_corpus_awakening_agent_transition_registry.get(
                    "stage_family_note_count",
                    0,
                )
            ),
            "full_corpus_appendix_rows": full_corpus_appendix_governance_ledger.get(
                "record_count",
                0,
            ),
            "ap6d_overlay_loops": ap6d_57_loop_control_registry.get("loop_count", 0),
            "ap6d_overlay_agents": ap6d_57_agent_lane_registry.get(
                "master_agent_count",
                0,
            ),
            "ap6d_overlay_nested_rows": ap6d_57_nested_seat_manifest.get(
                "row_count",
                0,
            ),
        }
    )
    manifest["outputs"].update(
        {
            "full_corpus_authority_registry": str(FULL_CORPUS_AUTHORITY_REGISTRY_PATH),
            "full_corpus_basis_crosswalk_registry": str(
                FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH
            ),
            "full_corpus_route_coverage_registry": str(
                FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH
            ),
            "full_corpus_awakening_stage_registry": str(
                FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH
            ),
            "full_corpus_awakening_agent_transition_registry": str(
                FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH
            ),
            "full_corpus_appendix_governance_ledger": str(
                FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH
            ),
            "ap6d_57_loop_control_registry": str(AP6D_57_LOOP_CONTROL_REGISTRY_PATH),
            "ap6d_57_agent_lane_registry": str(AP6D_57_AGENT_LANE_REGISTRY_PATH),
            "ap6d_57_nested_seat_manifest": str(AP6D_57_NESTED_SEAT_MANIFEST_PATH),
            "guild_hall_doc": str(LP57OMEGA_GUILD_HALL_DOC_PATH),
            "temple_doc": str(LP57OMEGA_TEMPLE_DOC_PATH),
            "deep_control_doc": str(LP57OMEGA_DEEP_CONTROL_DOC_PATH),
            "receipt_doc": str(LP57OMEGA_RECEIPT_PATH),
        }
    )
    manifest["notes"].append(
        "Full-corpus integration remains the mapping target and AP6D remains an assistive overlay only."
    )
    standards = {
        "liminal_coordinate_standard_md": render_liminal_coordinate_standard(
            manifest,
            coordinate_registry,
        ),
        "agent_ledger_standard_md": render_agent_ledger_standard(manifest),
        "seed_inversion_standard_md": render_seed_inversion_standard(
            manifest,
            coordinate_registry,
        ),
        "seed_inversion_standard_json": build_seed_inversion_standard_json(
            manifest,
            coordinate_registry,
        ),
    }

    markdown_pages = {
        "lp57omega_index": render_index_markdown(manifest, enriched_master_loop_state),
        "lp57omega_framework": render_framework_markdown(
            enriched_master_agent_state,
            loop_registry,
        ),
        "lp57omega_coordinates": render_coordinate_markdown(coordinate_registry),
        "lp57omega_quest_ledger": render_quest_and_ledger_markdown(
            quest_contract_registry,
            master_ledger_registry,
        ),
        "lp57omega_signature_plan": render_signature_plan_markdown(loop_registry),
        "lp57omega_receipt": render_receipt_markdown(manifest),
    }
    guild_hall_doc = render_hall_doc(loop_registry, quest_contract_registry, manifest)
    temple_doc = render_temple_doc(loop_registry, quest_contract_registry, manifest)
    deep_control_doc = render_deep_control_doc(manifest)
    receipt_doc = render_external_receipt(manifest)

    guild_hall_board_text = apply_marker_block(
        current_guild_hall_board_text,
        HALL_BOARD_MARKER,
        render_hall_board_body(enriched_master_loop_state, manifest),
    )
    temple_board_text = apply_marker_block(
        current_temple_board_text,
        TEMPLE_BOARD_MARKER,
        render_temple_board_body(enriched_master_loop_state, manifest),
    )

    return {
        "master_loop_state": enriched_master_loop_state,
        "master_agent_state": enriched_master_agent_state,
        "master_loop_shared_lattice": enriched_shared_lattice,
        "loop_registry": loop_registry,
        "agent_identity_registry": agent_identity_registry,
        "coordinate_registry": coordinate_registry,
        "quest_contract_registry": quest_contract_registry,
        "master_ledger_registry": master_ledger_registry,
        "manifest": manifest,
        "markdown_pages": markdown_pages,
        "guild_hall_doc": guild_hall_doc,
        "temple_doc": temple_doc,
        "deep_control_doc": deep_control_doc,
        "receipt_doc": receipt_doc,
        "guild_hall_board_text": guild_hall_board_text,
        "temple_board_text": temple_board_text,
        "standards": standards,
        "focus_by_loop": {
            loop_key(loop_number): [row.get("record_id", "") for row in rows]
            for loop_number, rows in focus_by_loop.items()
        },
        "control_manifest_id": control_manifest.get("build_id", ""),
    }

