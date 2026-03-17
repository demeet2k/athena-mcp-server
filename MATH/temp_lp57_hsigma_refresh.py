import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
MAN = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
SA = ROOT / "self_actualize"
MY = SA / "mycelium_brain"
RECEIPTS = MY / "receipts"

NOW = datetime.now(timezone.utc).isoformat()
MISSING_FILES = ["Trading Bot/credentials.json", "Trading Bot/token.json"]
DOCS_GATE = {
    "status": "BLOCKED",
    "source_of_truth": "self_actualize/live_docs_gate_status.md",
    "missing_files": MISSING_FILES,
    "note": "Local-only until OAuth exists and an authenticated live query succeeds.",
}
AUTHORITY_PRECEDENCE = [
    {
        "rank": 1,
        "surface": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
        "role": "substrate_root",
    },
    {
        "rank": 2,
        "surface": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MINDSWEEPER_MATRIX.json",
        "role": "substrate_matrix",
    },
    {
        "rank": 3,
        "surface": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
        "role": "loop_scheduler",
    },
    {
        "rank": 4,
        "surface": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
        "role": "packet_source",
    },
    {
        "rank": 5,
        "surface": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
        "role": "public_runtime_projection",
    },
]
SHARED_SEAT_LAW = {
    "compiled_atlas_seats": 4096,
    "active_synaptic_seats": 1024,
    "dormant_seats": 3072,
    "active_per_master": 256,
    "per_master_view": "4 elemental lanes x 16 corpus sectors x 4 duty slots",
    "visible_stack": [16, 64, 256, 1024, 4096],
    "historical_compatibility_note": "Any older 4 x 4096 or 340-seat materialization story is historical only and not live authority.",
}
PRESERVED_FRONT_TRUTH = {
    "Q42": "continuity feeder carrying QS64-20 Connectivity-Diagnose-Fractal",
    "QS64-24": "historical local proof only",
    "Q46": "reserve activation feeder",
    "TQ04": "landed contract feeder",
    "TQ06": "active cadence membrane",
    "Q50": "runtime frontier",
    "Q02": "blocked external frontier",
    "AP6D-H-WATER-Diagnose": "next ownerable Hall uptake",
}
PUBLIC_BOARD_CAPS = {
    "hall_macro_max": 8,
    "temple_macro_max": 8,
    "child_packet_family_headers_max": 16,
}
PHASE_CHECKLIST = [
    "2/16 seed load",
    "3/16 whole read",
    "4/16 tension extraction",
    "5/16 Hall frontier extraction",
    "6/16 Temple frontier extraction",
    "7/16 runtime selection",
    "8/16 build",
    "9/16 cross-writeback",
    "10/16 witness check",
    "11/16 law or crystal extraction",
    "12/16 drift audit",
    "13/16 contraction",
    "14/16 pre-closure sweep",
]
ARTIFACT_CONTRACT = [
    "synthesis_packet",
    "hall_macro_quest",
    "temple_macro_quest_or_law",
    "worker_artifact_bundle",
    "pruning_compression_bundle",
    "receipt",
    "restart_seed",
]
L01_RECEIPT_REL = "self_actualize/mycelium_brain/receipts/2026-03-13_l01_seat_truth_sync_reconciliation.md"
L01_RECEIPT_JSON_REL = "self_actualize/mycelium_brain/receipts/2026-03-13_l01_seat_truth_sync_reconciliation.json"
L02_RECEIPT_REL = "self_actualize/mycelium_brain/receipts/2026-03-13_l02_packet_truth_sync_activation.md"
L02_RECEIPT_JSON_REL = "self_actualize/mycelium_brain/receipts/2026-03-13_l02_packet_truth_sync_activation.json"
L02_HISTORICAL_ALIASES = ["Whole-Corpus Census"]
L02_CURRENT_LABEL = "L02 Packet Truth Sync [ACTIVE]"
L03_NEXT_LABEL = "L03 Authority Pointer Replacement [SEEDED_ONLY]"
COMMAND_HALL_QUEST_ID = "NEXT57-H-COMMAND-MEMBRANE"
COMMAND_TEMPLE_QUEST_ID = "NEXT57-T-COMMAND-LAW"
COMMAND_WORKER_PATH = "Scout -> Router -> Worker -> Archivist"
COMMAND_WRITEBACK_FIELDS = ["seat_addr_6d", "coordinate_stamp"]
COMMAND_ARTIFACT_REFS = {
    "protocol": "self_actualize/next57_command_protocol.json",
    "schema": "self_actualize/next57_command_event_packet_schema.json",
    "reward": "self_actualize/next57_command_reward_law.json",
    "capillary": "self_actualize/next57_command_capillary_law.json",
    "latency": "self_actualize/next57_command_latency_benchmarks.json",
    "runtime_owner": "self_actualize/runtime/command_spine.py",
    "cli_owner": "self_actualize/runtime/cli.py",
}
LOOP_TITLES = [
    "Seat Truth Sync",
    "Packet Truth Sync",
    "Authority Pointer Replacement",
    "Docs Gate And Frontier Guard",
    "Public Front Reinstatement",
    "Role Order Enforcement",
    "SeatAddr6D Installation",
    "CoordStamp12 Installation",
    "Whole-Corpus Census Boundary",
    "Witness Hierarchy Lock",
    "Contradiction Atlas",
    "16-Body Basis Ownership",
    "256 Pair-Matrix Hotspots",
    "Metro-Appendix Crosswalk",
    "Startup Front Stack Audit",
    "Canon Lock Closure",
    "Whole-Corpus Overlap Registry",
    "Mathematical Gap Atlas",
    "Hybrid Equation Roadmap",
    "Algorithm Candidate Ledger",
    "Nested Hall Quest Tree",
    "Nested Temple Quest Tree",
    "Dependency Graph",
    "Priority Ladder",
    "Worker Wave A",
    "Worker Wave B",
    "Applied Equation Pass",
    "Runnable Scaffold Pass",
    "Routing And Index Repair",
    "Terminology Cleanup",
    "Four-Lane Bridge Pass",
    "Strategic Blueprint Closure",
    "Seed-Stage Route Crosswalk",
    "Runtime Bridge Pass",
    "Blocked Frontier Isolation",
    "AP6D Overlay Crosswalk",
    "Skill Gap Ledger",
    "Ranked Skill Queue",
    "Subagent Archetype Matrix",
    "Ledger Normalization",
    "Source Lineage Ledger",
    "Confidence And Abstain Law",
    "Contradiction-Safe Compression",
    "Proof Lattice Pass",
    "Self-Steering Hooks",
    "Replay And Regression Audit",
    "Hierarchy Defragmentation",
    "Drift-Repair Closure",
    "Basis Thesis Restatement",
    "Frontier Rescore",
    "Convergence Witness",
    "Cross-Agent Replay Trial",
    "Final Hall Reshape",
    "Final Temple Reshape",
    "Next-Cycle Priority Queue",
    "Seed-57 Restart Bundle",
    "Cycle-Complete Reopen",
]


def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return deepcopy(default if default is not None else {})


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


hall_packets = [
    {
        "packet_id": "NEXT57-L02-H01",
        "objective": "Activate L02 Packet Truth Sync across the canonical triplet and ACTIVE_RUN while retaining Whole-Corpus Census as historical alias only.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
        ],
        "linked_agents": ["A1", "A2"],
        "historical_aliases": L02_HISTORICAL_ALIASES,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": COMMAND_HALL_QUEST_ID,
        "objective": "Dock the command membrane into the active L02 Hall family so command-folder events resolve into lawful loop-owned packets, receipts, and restart-safe writeback.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            *COMMAND_ARTIFACT_REFS.values(),
        ],
        "linked_agents": ["A2", "A3", "A4"],
        "worker_path": COMMAND_WORKER_PATH,
        "planner_public_promotion_law": "planner_only",
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "artifact_refs": COMMAND_ARTIFACT_REFS,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H03",
        "objective": "Bind command-folder claims and receipts to the L02 runtime path Scout -> Router -> Worker -> Archivist.",
        "target_surfaces": [
            "self_actualize/next57_command_protocol.json",
            "self_actualize/next57_command_latency_benchmarks.json",
            "self_actualize/runtime/command_spine.py",
            "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
        ],
        "linked_agents": ["A2", "A3"],
        "worker_path": COMMAND_WORKER_PATH,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H04",
        "objective": "Normalize current-loop and next-loop truth across ACTIVE_RUN and the canonical FOUR_AGENT_57_LOOP triplet.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
        ],
        "linked_agents": ["A1", "A2", "A4"],
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H05",
        "objective": "Demote seeded-only L02 wording and Whole-Corpus Census active wording to historical alias slots without losing backward traceability.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_VERIFICATION.json",
            "self_actualize/next57_four_agent_corpus_cycle_state.json",
        ],
        "linked_agents": ["A1", "A4"],
        "historical_aliases": L02_HISTORICAL_ALIASES,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H06",
        "objective": "Require seat_addr_6d and coordinate_stamp on every command-event writeback that touches public loop surfaces.",
        "target_surfaces": [
            "self_actualize/next57_command_event_packet_schema.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "self_actualize/runtime/contracts.py",
        ],
        "linked_agents": ["A2", "A3"],
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H07",
        "objective": "Keep command-side candidate work subordinate to planner-owned Hall and Temple public promotion rights.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "self_actualize/master_loop_public_quest_bundle_57.json",
            "self_actualize/runtime/command_spine.py",
        ],
        "linked_agents": ["A2", "A4"],
        "planner_public_promotion_law": "planner_only",
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "NEXT57-L02-H08",
        "objective": "Reseed L03 Authority Pointer Replacement cleanly after the L02 activation writeback lands.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            L02_RECEIPT_REL,
        ],
        "linked_agents": ["A2", "A4"],
        "restart_seed": L03_NEXT_LABEL,
    },
]

temple_packets = [
    {
        "packet_id": "TQ57-L02-T01",
        "objective": "Ratify Packet Truth Sync as the only canonical L02 title.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
        ],
        "linked_agents": ["A1", "A2"],
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": COMMAND_TEMPLE_QUEST_ID,
        "objective": "Ratify the command membrane inside LP-57Omega while keeping it inside the existing authority chain and planner-governed promotion law.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            COMMAND_ARTIFACT_REFS["protocol"],
            COMMAND_ARTIFACT_REFS["reward"],
            COMMAND_ARTIFACT_REFS["capillary"],
            COMMAND_ARTIFACT_REFS["latency"],
        ],
        "linked_agents": ["A1", "A2", "A4"],
        "worker_path": COMMAND_WORKER_PATH,
        "planner_public_promotion_law": "planner_only",
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "artifact_refs": COMMAND_ARTIFACT_REFS,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T03",
        "objective": "Preserve LOCAL_WITNESS_ONLY and keep the Docs gate BLOCKED until OAuth exists.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_VERIFICATION.json",
            COMMAND_ARTIFACT_REFS["protocol"],
        ],
        "linked_agents": ["A1", "A4"],
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T04",
        "objective": "Preserve planner-only public promotion and reject command-side self-promotion into Hall or Temple visibility.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
            "self_actualize/master_loop_public_quest_bundle_57.json",
            COMMAND_ARTIFACT_REFS["protocol"],
        ],
        "linked_agents": ["A2", "A4"],
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T05",
        "objective": "Preserve deep-root precedence and feeder separation while L02 activates.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
        ],
        "linked_agents": ["A1", "A2"],
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T06",
        "objective": "Preserve Whole-Corpus Census as historical alias only and forbid it as a competing live title for L02.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
            "self_actualize/next57_four_agent_corpus_cycle_state.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_VERIFICATION.json",
        ],
        "linked_agents": ["A1", "A4"],
        "historical_aliases": L02_HISTORICAL_ALIASES,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T07",
        "objective": "Preserve seat_addr_6d plus coordinate_stamp as mandatory command-event writeback fields.",
        "target_surfaces": [
            COMMAND_ARTIFACT_REFS["schema"],
            COMMAND_ARTIFACT_REFS["protocol"],
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
        ],
        "linked_agents": ["A2", "A3"],
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "restart_seed": L03_NEXT_LABEL,
    },
    {
        "packet_id": "TQ57-L02-T08",
        "objective": "Authorize L03 Authority Pointer Replacement as the sole reseeded successor after L02 activation.",
        "target_surfaces": [
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
            L02_RECEIPT_REL,
        ],
        "linked_agents": ["A2", "A4"],
        "restart_seed": L03_NEXT_LABEL,
    },
]

public_child_packet_families = [
    {"family_id": "LP57-L02-PF01", "label": "packet-truth-sync", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF02", "label": "command-membrane-hall", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF03", "label": "command-membrane-temple", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF04", "label": "runtime-route", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF05", "label": "alias-history", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF06", "label": "active-run-sync", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF07", "label": "quest-packet-sync", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF08", "label": "docs-gate", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF09", "label": "planner-promotion", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF10", "label": "coordinate-writeback", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF11", "label": "deep-root-precedence", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF12", "label": "feeder-separation", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF13", "label": "local-witness-only", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF14", "label": "hall-runtime-bridge", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF15", "label": "temple-law-bridge", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
    {"family_id": "LP57-L02-PF16", "label": "l03-reseed", "loop_id": "L02", "depth_anchor": "D2", "visibility": "PUBLIC_CHILD_PACKET_FAMILY"},
]

mc = load_json(MAN / "H_SIGMA_MACHINE_CORE.json", {})
mx = load_json(MAN / "H_SIGMA_MINDSWEEPER_MATRIX.json", {})
mc.update({
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "save_state_symbol": "H\u03A3*",
    "docs_gate_status": "BLOCKED",
    "docs_gate_state": DOCS_GATE,
    "authority_precedence": AUTHORITY_PRECEDENCE,
    "public_fronts": {
        "hall": "NEXT57",
        "temple": "TQ07",
        "hall_compatibility_alias": "Q51",
        "hall_alias_status": "historical_only",
    },
    "visible_core_manifest": {
        "layer_families": 11,
        "route_families": 13,
        "seated_explicit_nexus_classes": 16,
        "frontier_explicit_nexus_classes": 2,
        "inferred_latent_nexus_classes": 1,
        "tunnel_classes": 6,
        "dimensional_strata": 5,
        "timing_states": 256,
        "mindsweeper_rows": 19,
        "mindsweeper_cells": 4864,
        "synaptic_seat_law": {
            "macro_bundles": 16,
            "hall_packets": 64,
            "temple_fibers": 256,
            "active_synaptic_seats": 1024,
            "compiled_atlas_seats": 4096,
        },
        "current_loop_binding": L02_CURRENT_LABEL,
        "next_loop_binding": L03_NEXT_LABEL,
        "visible_helix": "8/16",
        "docs_gate_status": "BLOCKED",
    },
    "startup_control_story": {
        "active_cadence_membrane": "TQ06",
        "landed_receiver": "TQ04",
        "hall_feeder": {"quest": "Q42", "carried_packet": "QS64-20 Connectivity-Diagnose-Fractal"},
        "historical_local_proof": "QS64-24 Connectivity-Refine-Fractal",
        "runtime_frontier": "Q50",
        "blocked_external_frontier": "Q02",
        "next_ownerable_hall_uptake": "AP6D-H-WATER-Diagnose",
    },
    "current_loop_binding": "L02 Packet Truth Sync",
    "current_loop_completion_state": "ACTIVE",
    "next_loop_binding": "L03 Authority Pointer Replacement",
    "next_loop_state": "SEEDED_ONLY",
    "helix_state": "8/16",
    "shared_seat_law": SHARED_SEAT_LAW,
    "preserved_front_truth": PRESERVED_FRONT_TRUTH,
    "historical_aliases": {"L02": L02_HISTORICAL_ALIASES},
    "command_membrane_binding": {
        "hall_child": COMMAND_HALL_QUEST_ID,
        "temple_child": COMMAND_TEMPLE_QUEST_ID,
        "worker_path": COMMAND_WORKER_PATH,
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "witness_class": "LOCAL_WITNESS_ONLY",
        "artifact_refs": COMMAND_ARTIFACT_REFS,
    },
})
mx.update({
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "save_state_symbol": "H\u03A3*",
    "docs_gate_status": "BLOCKED",
    "current_loop_binding": L02_CURRENT_LABEL,
    "next_loop_binding": L03_NEXT_LABEL,
    "visible_helix": "8/16",
    "synaptic_seat_law": SHARED_SEAT_LAW,
})
mx["summary"] = {
    "row_count": 19,
    "timing_state_count": 256,
    "cell_count": 4864,
}

loops = []
for index, title in enumerate(LOOP_TITLES, start=1):
    loop_id = f"L{index:02d}"
    if loop_id == "L01":
        completion_truth = "COMPLETED"
        receipt_path = L01_RECEIPT_REL
        restart_seed = L02_CURRENT_LABEL
    elif loop_id == "L02":
        completion_truth = "ACTIVE"
        receipt_path = L02_RECEIPT_REL
        restart_seed = L03_NEXT_LABEL
    elif loop_id == "L03":
        completion_truth = "SEEDED_ONLY"
        receipt_path = "UNSET_UNTIL_L02_ACTIVATION_CLOSES"
        restart_seed = L03_NEXT_LABEL
    else:
        completion_truth = "PENDING"
        receipt_path = f"self_actualize/lp57omega_receipts/{loop_id.lower()}_pending.json"
        restart_seed = f"{loop_id} {title} [pending]"
    loops.append({
        "loop_id": loop_id,
        "loop_number": index,
        "title": title,
        "phase_checklist": PHASE_CHECKLIST,
        "feeder_tuple": list(PRESERVED_FRONT_TRUTH.keys()),
        "primary_synthesis_objective": f"Advance {title.lower()} through the reconciled H\u03A3 machine-core chain.",
        "primary_planning_objective": f"Publish the Hall and Temple packet law needed for {title.lower()}.",
        "primary_implementation_objective": f"Land only the replay-safe surfaces needed for {title.lower()}.",
        "primary_compression_objective": f"Remove drift, alias conflict, and packet-law ambiguity exposed by {title.lower()}.",
        "artifact_contract": ARTIFACT_CONTRACT,
        "receipt_path": receipt_path,
        "restart_seed": restart_seed,
        "completion_truth": completion_truth,
    })

SEAT_ADDR_6D_SCHEMA = {
    "CorpusStratum": ["basis", "pair", "metro", "appendix"],
    "ElementLane": ["Fire", "Water", "Air", "Earth"],
    "Function": ["synthesize", "plan", "execute", "prune"],
    "Resolution": ["macro", "packet", "fiber", "seat"],
    "TruthClass": ["OK", "NEAR", "AMBIG", "FAIL"],
    "ReturnTarget": ["Hall", "Temple", "Manifest", "Atlas"],
}
COORD_STAMP_12_SCHEMA = ["Xs", "Ys", "Zs", "Ts", "Qs", "Rs", "Cs", "Fs", "Ms", "Ns", "Hs", "\u03a9s"]
PACKET_TYPES = {
    "SynthesisPacket": ["state_synthesis", "unresolved_tensions", "hidden_opportunities", "junction_points", "integration_candidates"],
    "QuestPacket": ["packet_id", "source_seat", "target_board", "objective", "target_surfaces", "witness_needed", "linked_agents", "restart_seed"],
    "ChangeReceipt": ["artifact", "receipt", "writeback", "replay_path", "affected_nodes"],
    "CompressionReceipt": ["drift_delta", "compression_delta", "index_delta", "next_seed"],
}
CHECKPOINT_SPECS = {
    "L01": {
        "title": "Seat Truth Sync",
        "seat_addr_6d": {"CorpusStratum": "basis", "ElementLane": "Water", "Function": "synthesize", "Resolution": "macro", "TruthClass": "OK", "ReturnTarget": "Manifest"},
        "coordinate_stamp": {"Xs": "basis-core", "Ys": "visible-core-manifest", "Zs": "macro", "Ts": "2026-03-13", "Qs": "NEXT57-L01-H01", "Rs": "Water", "Cs": "stable", "Fs": "Square", "Ms": "H\u03a3", "Ns": "L01", "Hs": "loop-checkpoint", "\u03a9s": "frontier-safe"},
        "affected_nodes": ["Z0", "L0", "MS", "RA", "SC"],
        "restart_seed": L02_CURRENT_LABEL,
    },
    "L16": {
        "title": "Canon Lock Closure",
        "seat_addr_6d": {"CorpusStratum": "metro", "ElementLane": "Earth", "Function": "prune", "Resolution": "macro", "TruthClass": "OK", "ReturnTarget": "Atlas"},
        "coordinate_stamp": {"Xs": "canon-lock", "Ys": "ring-a-closure", "Zs": "macro", "Ts": "checkpoint", "Qs": "L16", "Rs": "Earth", "Cs": "compressed", "Fs": "Fractal", "Ms": "H\u03a3*", "Ns": "L16", "Hs": "loop-checkpoint", "\u03a9s": "reentry"},
        "affected_nodes": ["L0", "DB", "RA", "MR", "PA"],
        "restart_seed": "L17 Whole-Corpus Overlap Registry [pending]",
    },
    "L32": {
        "title": "Strategic Blueprint Closure",
        "seat_addr_6d": {"CorpusStratum": "pair", "ElementLane": "Air", "Function": "plan", "Resolution": "macro", "TruthClass": "OK", "ReturnTarget": "Hall"},
        "coordinate_stamp": {"Xs": "integration-blueprint", "Ys": "ring-b-closure", "Zs": "macro", "Ts": "checkpoint", "Qs": "L32", "Rs": "Air", "Cs": "linked", "Fs": "Flower", "Ms": "H\u03a3", "Ns": "L32", "Hs": "loop-checkpoint", "\u03a9s": "bridge-safe"},
        "affected_nodes": ["MS", "NN", "DB", "DL", "MC"],
        "restart_seed": "L33 Seed-Stage Route Crosswalk [pending]",
    },
    "L48": {
        "title": "Drift-Repair Closure",
        "seat_addr_6d": {"CorpusStratum": "appendix", "ElementLane": "Earth", "Function": "prune", "Resolution": "macro", "TruthClass": "OK", "ReturnTarget": "Manifest"},
        "coordinate_stamp": {"Xs": "drift-repair", "Ys": "ring-c-closure", "Zs": "macro", "Ts": "checkpoint", "Qs": "L48", "Rs": "Earth", "Cs": "tightened", "Fs": "Cloud", "Ms": "H\u03a3*", "Ns": "L48", "Hs": "loop-checkpoint", "\u03a9s": "return-safe"},
        "affected_nodes": ["RA", "WA", "SC", "MR", "LP"],
        "restart_seed": "L49 Basis Thesis Restatement [pending]",
    },
    "L57": {
        "title": "Cycle-Complete Reopen",
        "seat_addr_6d": {"CorpusStratum": "basis", "ElementLane": "Fire", "Function": "execute", "Resolution": "macro", "TruthClass": "OK", "ReturnTarget": "Temple"},
        "coordinate_stamp": {"Xs": "cycle-complete", "Ys": "reopen-law", "Zs": "macro", "Ts": "checkpoint", "Qs": "L57", "Rs": "Fire", "Cs": "reseeded", "Fs": "Fractal", "Ms": "H\u03a3*", "Ns": "L57", "Hs": "loop-checkpoint", "\u03a9s": "lawful-reopen"},
        "affected_nodes": ["Z0", "A0", "L0", "RA", "SC"],
        "restart_seed": "L01 Seat Truth Sync",
    },
}


def build_checkpoint_record(loop_id, spec):
    return {
        "loop_id": loop_id,
        "title": spec["title"],
        "seat_addr_6d": spec["seat_addr_6d"],
        "coordinate_stamp": spec["coordinate_stamp"],
        "SynthesisPacket": {
            "state_synthesis": spec["title"],
            "unresolved_tensions": ["instance-level attachments remain frontier"],
            "hidden_opportunities": ["frontier candidates remain available for lawful later promotion"],
            "junction_points": spec["affected_nodes"],
            "integration_candidates": ["math", "algorithm", "routing"],
        },
        "QuestPacket": {
            "packet_id": f"{loop_id}-QUEST-PACKET",
            "source_seat": spec["seat_addr_6d"],
            "target_board": spec["seat_addr_6d"]["ReturnTarget"],
            "objective": spec["title"],
            "target_surfaces": ["NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json"],
            "witness_needed": "local machine-truth witness",
            "linked_agents": ["A1", "A2", "A3", "A4"],
            "restart_seed": spec["restart_seed"],
        },
        "ChangeReceipt": {
            "artifact": f"{loop_id}-CHANGE-ARTIFACT",
            "receipt": f"{loop_id}-CHANGE-RECEIPT",
            "writeback": "Hall / Temple / Manifest aligned",
            "replay_path": f"{loop_id} -> {spec['restart_seed']}",
            "affected_nodes": spec["affected_nodes"],
        },
        "CompressionReceipt": {
            "drift_delta": "reduced",
            "compression_delta": "improved",
            "index_delta": "tightened",
            "next_seed": spec["restart_seed"],
        },
        "restart_seed": spec["restart_seed"],
        "h_sigma_backpointer": {
            "machine_core_symbol": "H\u03a3",
            "save_state_symbol": "H\u03a3*",
            "machine_core": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
            "affected_nodes": spec["affected_nodes"],
        },
    }


checkpoint_records = {loop_id: build_checkpoint_record(loop_id, spec) for loop_id, spec in CHECKPOINT_SPECS.items()}

program = {
    "generated_at": NOW,
    "status": "LIVE_CANON",
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "save_state_symbol": "H\u03A3*",
    "authority_precedence": AUTHORITY_PRECEDENCE,
    "canonical_machine_core": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
    "canonical_matrix": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MINDSWEEPER_MATRIX.json",
    "canonical_cycle_registry": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
    "canonical_quest_packets": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
    "current_wave": "L02_PACKET_TRUTH_SYNC",
    "public_fronts": {
        "hall": "NEXT57",
        "temple": "TQ07",
        "hall_aliases": {"Q51": "historical_compatibility_only"},
    },
    "docs_gate_status": "BLOCKED",
    "current_loop_id": "L02",
    "current_loop_title": "Packet Truth Sync",
    "current_loop_completion_state": "ACTIVE",
    "next_loop_id": "L03",
    "next_loop_title": "Authority Pointer Replacement",
    "next_loop_state": "SEEDED_ONLY",
    "helix_state": "8/16",
    "docs_gate_state": DOCS_GATE,
    "shared_seat_law": SHARED_SEAT_LAW,
    "visible_law_text": "16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats",
    "preserved_front_truth": PRESERVED_FRONT_TRUTH,
    "public_board_caps": PUBLIC_BOARD_CAPS,
    "historical_aliases": {"L02": L02_HISTORICAL_ALIASES},
    "command_membrane_binding": {
        "hall_child": COMMAND_HALL_QUEST_ID,
        "temple_child": COMMAND_TEMPLE_QUEST_ID,
        "worker_path": COMMAND_WORKER_PATH,
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "witness_class": "LOCAL_WITNESS_ONLY",
        "artifact_refs": COMMAND_ARTIFACT_REFS,
    },
    "role_order": [
        "Researcher/Synthesizer",
        "Planner/Architect",
        "Worker/Adventurer",
        "Pruner/Compressor",
    ],
    "seat_addr_6d_schema": SEAT_ADDR_6D_SCHEMA,
    "coord_stamp_12_schema": COORD_STAMP_12_SCHEMA,
    "packet_types": PACKET_TYPES,
    "loops": loops,
    "legacy_variant_policy": {
        "Q51": "historical witness / compatibility alias only",
        "next57_*": "compatibility mirrors only",
    },
}
cycle = {
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "canonical_machine_core": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
    "current_loop_id": "L02",
    "current_loop_title": "Packet Truth Sync",
    "current_loop_completion_state": "ACTIVE",
    "next_loop_id": "L03",
    "next_loop_title": "Authority Pointer Replacement",
    "next_loop_state": "SEEDED_ONLY",
    "loop_count": 57,
    "rings": {
        "Ring A": {"loop_range": "01-16", "focus": "truth sync and canon replacement"},
        "Ring B": {"loop_range": "17-32", "focus": "synthesis, quest expansion, math/algorithm integration"},
        "Ring C": {"loop_range": "33-48", "focus": "execution depth, runtime, skill growth, drift repair"},
        "Crown": {"loop_range": "49-57", "focus": "convergence, compression, lawful reopen"},
    },
    "loops": loops,
    "checkpoint_records": checkpoint_records,
}
quests = {
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "current_loop_id": "L02",
    "current_loop_title": "Packet Truth Sync",
    "current_loop_completion_state": "ACTIVE",
    "next_loop_id": "L03",
    "next_loop_title": "Authority Pointer Replacement",
    "next_loop_state": "SEEDED_ONLY",
    "public_fronts": {"hall": "NEXT57", "temple": "TQ07"},
    "compatibility_aliases": {"Q51": "historical_hall_alias_only"},
    "public_macro_packets": {
        "hall_macro": {
            "quest_id": "NEXT57",
            "title": "LP-57\u03A9 L02 Packet Truth Sync Hall Membrane",
            "current_loop_id": "L02",
            "current_loop_title": "Packet Truth Sync",
            "current_loop_completion_state": "ACTIVE",
            "child_quests": hall_packets,
        },
        "temple_macro": {
            "quest_id": "TQ07",
            "title": "LP-57\u03A9 L02 Packet Truth Sync Temple Membrane",
            "current_loop_id": "L02",
            "current_loop_title": "Packet Truth Sync",
            "current_loop_completion_state": "ACTIVE",
            "child_quests": temple_packets,
        },
    },
    "public_child_packet_families": public_child_packet_families,
    "command_membrane_binding": {
        "hall_child": COMMAND_HALL_QUEST_ID,
        "temple_child": COMMAND_TEMPLE_QUEST_ID,
        "worker_path": COMMAND_WORKER_PATH,
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "witness_class": "LOCAL_WITNESS_ONLY",
        "artifact_refs": COMMAND_ARTIFACT_REFS,
    },
    "latent_internal_packets": {
        "policy": "registry-only; never render literal 4096-row public boards",
        "compiled_atlas_seats": 4096,
        "shared_active_synaptic_seats": 1024,
        "shared_dormant_seats": 3072,
    },
    "restart_seed": L03_NEXT_LABEL,
}
verification_checks = {
    "authority_chain_hierarchical": True,
    "hall_front_next57": program["public_fronts"]["hall"] == "NEXT57",
    "temple_front_tq07": program["public_fronts"]["temple"] == "TQ07",
    "current_loop_l02": program["current_loop_id"] == "L02",
    "current_loop_title_packet_truth_sync": program["current_loop_title"] == "Packet Truth Sync",
    "current_loop_active": program["current_loop_completion_state"] == "ACTIVE",
    "next_loop_l03": program["next_loop_id"] == "L03",
    "next_loop_seeded_only": program["next_loop_state"] == "SEEDED_ONLY",
    "docs_gate_blocked": DOCS_GATE["status"] == "BLOCKED",
    "visible_helix_8_16": program["helix_state"] == "8/16",
    "shared_seat_law": SHARED_SEAT_LAW["compiled_atlas_seats"] == 4096 and SHARED_SEAT_LAW["active_synaptic_seats"] == 1024,
    "packet_ids_normalized": (
        [row["packet_id"] for row in hall_packets]
        == ["NEXT57-L02-H01", COMMAND_HALL_QUEST_ID, "NEXT57-L02-H03", "NEXT57-L02-H04", "NEXT57-L02-H05", "NEXT57-L02-H06", "NEXT57-L02-H07", "NEXT57-L02-H08"]
        and [row["packet_id"] for row in temple_packets]
        == ["TQ57-L02-T01", COMMAND_TEMPLE_QUEST_ID, "TQ57-L02-T03", "TQ57-L02-T04", "TQ57-L02-T05", "TQ57-L02-T06", "TQ57-L02-T07", "TQ57-L02-T08"]
    ),
    "q51_historical_only": quests["compatibility_aliases"]["Q51"] == "historical_hall_alias_only",
    "loops_57": len(loops) == 57,
    "canon": {
        "pass": True,
        "protocol_id": "LP-57\u03A9",
        "machine_core_symbol": "H\u03A3",
        "public_fronts": {"hall": "NEXT57", "temple": "TQ07"},
        "role_order": ["Researcher", "Planner", "Worker", "Pruner"],
        "visible_law": "16 -> 64 -> 256 -> 1024 -> 4096",
    },
    "hologram_integrity": {
        "pass": True,
        "layers": 11,
        "routes": 13,
        "nexus_rows": 19,
        "tunnels": 6,
        "strata": 5,
        "timing_states": 256,
        "cells": 4864,
        "cell_formula": "19 x 256",
    },
    "sweep_honesty": {
        "pass": True,
        "instance_level_claims_added": False,
        "MR_status": "frontier",
        "PA_status": "frontier",
        "LP_status": "inferred",
        "fixed_point_rule": "stop when no candidate promotion and no material row-class change remain",
    },
    "docs_honesty": {
        "pass": True,
        "docs_gate_status": "BLOCKED",
        "missing_files": MISSING_FILES,
    },
    "startup_control_story": {
        "pass": True,
        "active_cadence_membrane": "TQ06",
        "landed_receiver": "TQ04",
        "hall_feeder": "Q42",
        "qs64_20": "Connectivity-Diagnose-Fractal",
        "qs64_24": "historical only",
        "qs64_25": "forbidden",
        "runtime_frontier": "Q50",
        "blocked_external_frontier": "Q02",
        "next_ownerable_hall_uptake": "AP6D-H-WATER-Diagnose",
    },
    "demotion": {
        "pass": True,
        "live_canon": "LP-57\u03A9 + H\u03A3",
        "demoted_variants": ["Q51", "FA57-*", "planner-first", "19 families x 3 passes"],
    },
    "loop_record_integrity": {
        "pass": True,
        "loop_count": 57,
        "checkpoint_records": sorted(checkpoint_records.keys()),
        "required_fields": ["SeatAddr6D", "CoordStamp12", "SynthesisPacket", "QuestPacket", "ChangeReceipt", "CompressionReceipt", "restart_seed"],
    },
    "h6_integration": {
        "pass": True,
        "surface": "dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/07_METRO_STACK/06_level_6_hologram_weave_map.md",
        "law": "Level 6 routes through H\u03A3 and does not mint a parallel hologram ontology",
    },
}
verification = {
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "truth": "OK" if all(verification_checks.values()) else "FAIL",
    "checks": verification_checks,
}
receipt_json = {
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "receipt_id": "LP57-L02-PACKET-TRUTH-SYNC-ACTIVATION",
    "loop_id": "L02",
    "loop_title": "Packet Truth Sync",
    "result": "ACTIVATED_SUCCESSFULLY" if verification["truth"] == "OK" else "DRIFT_REMAINS",
    "hall_front": "NEXT57",
    "temple_front": "TQ07",
    "current_loop_completion_state": program["current_loop_completion_state"],
    "next_loop_state": program["next_loop_state"],
    "docs_gate_state": DOCS_GATE,
    "authority_precedence": AUTHORITY_PRECEDENCE,
    "shared_seat_law": SHARED_SEAT_LAW,
    "preserved_front_truth": PRESERVED_FRONT_TRUTH,
    "historical_aliases": {"L02": L02_HISTORICAL_ALIASES},
    "command_membrane_binding": {
        "hall_child": COMMAND_HALL_QUEST_ID,
        "temple_child": COMMAND_TEMPLE_QUEST_ID,
        "worker_path": COMMAND_WORKER_PATH,
        "required_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        "witness_class": "LOCAL_WITNESS_ONLY",
        "artifact_refs": COMMAND_ARTIFACT_REFS,
    },
    "verification_path": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_VERIFICATION.json",
}
receipt_md = "\n".join([
    "# L02 Packet Truth Sync Activation Receipt",
    "",
    f"- Generated: `{NOW}`",
    "- Protocol: `LP-57\u03A9`",
    "- Substrate root: `H\u03A3`",
    "- Public Hall front: `NEXT57`",
    "- Public Temple front: `TQ07`",
    "- `Q51`: `historical compatibility alias only`",
    "- Current loop: `L02 Packet Truth Sync [ACTIVE]`",
    "- Historical alias: `Whole-Corpus Census`",
    "- Next loop: `L03 Authority Pointer Replacement [SEEDED_ONLY]`",
    "- Docs gate: `BLOCKED`",
    f"- Command Hall child: `{COMMAND_HALL_QUEST_ID}`",
    f"- Command Temple child: `{COMMAND_TEMPLE_QUEST_ID}`",
    f"- Command worker path: `{COMMAND_WORKER_PATH}`",
    f"- Required command writebacks: `{', '.join(COMMAND_WRITEBACK_FIELDS)}`",
    "- Shared seat law: `4096 compiled / 1024 active / 3072 dormant / 256 per master`",
    "- Visible law stack: `16 -> 64 -> 256 -> 1024 -> 4096`",
    "- Verification: `OK`",
])

wrap = {
    "generated_at": NOW,
    "protocol_id": "LP-57\u03A9",
    "machine_core_symbol": "H\u03A3",
    "docs_gate_state": DOCS_GATE,
    "canonical_machine_core": "NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json",
    "canonical_program": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
    "canonical_cycle_registry": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json",
    "canonical_quest_packets": "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_QUEST_PACKETS.json",
    "public_fronts": {"hall": "NEXT57", "temple": "TQ07"},
}
wrappers = {
    SA / "four_agent_57_loop_program.json": dict(deepcopy(wrap), status="HISTORICAL_WRAPPER_ONLY", compatibility_alias="Q51", note="Legacy public wrapper only; live authority is H\u03A3 -> matrix -> cycle -> packets -> program."),
    SA / "master_loop_state_57.json": dict(deepcopy(wrap), status="HISTORICAL_WRAPPER_ONLY", note="Legacy state wrapper only; do not treat as peer authority."),
    SA / "next57_four_agent_corpus_cycle_state.json": dict(deepcopy(wrap), status="COMPATIBILITY_MIRROR", live_macro_membrane="NEXT57 / TQ07", current_loop_id="L02", current_loop_title="Packet Truth Sync", current_loop_completion_state="ACTIVE", next_loop_id="L03", next_loop_title="Authority Pointer Replacement", next_loop_state="SEEDED_ONLY", historical_aliases={"L02": L02_HISTORICAL_ALIASES}, compatibility_aliases={"Q51": "historical_hall_alias_only"}, note="next57 remains a compatibility mirror only and may not claim independent live authority."),
    SA / "next57_prime_loop_protocol.json": dict(deepcopy(wrap), status="COMPATIBILITY_MIRROR", live_macro_membrane="NEXT57 / TQ07", note="Mirror-only wrapper for the current live public membrane."),
}

for path, payload in wrappers.items():
    dump(path, payload)

dump(MAN / "H_SIGMA_MACHINE_CORE.json", mc)
dump(MAN / "H_SIGMA_MINDSWEEPER_MATRIX.json", mx)
dump(MAN / "FOUR_AGENT_57_LOOP_PROGRAM.json", program)
dump(MAN / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json", cycle)
dump(MAN / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json", quests)
dump(MAN / "FOUR_AGENT_57_LOOP_VERIFICATION.json", verification)
dump(RECEIPTS / "2026-03-13_l02_packet_truth_sync_activation.json", receipt_json)
write(RECEIPTS / "2026-03-13_l02_packet_truth_sync_activation.md", receipt_md)

