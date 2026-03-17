from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.qshrink_refine_common import (
    ACTIVE_QUEUE_PATH,
    CHANGE_FEED_PATH,
    GUILD_HALL_ROOT,
    MANIFESTS_ROOT,
    MYCELIUM_ROOT,
    NEXT_SELF_PROMPT_PATH,
    TEMPLE_ROOT,
    TEMPLE_STATE_PATH,
    WORKSPACE_ROOT,
    docs_gate_payload,
    load_json,
    read_text,
)


NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MANIFESTS95_ROOT = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

ACTIVE_RUN_PATH = MANIFESTS95_ROOT / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = MANIFESTS95_ROOT / "BUILD_QUEUE.md"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
REQUESTS_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"

CONTROL_PACKET_PATH = WORKSPACE_ROOT / "self_actualize" / "control_state_packet.json"
NEXT4_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "qshrink_next4_state.json"
PACKET_FRESHNESS_PATH = WORKSPACE_ROOT / "self_actualize" / "packet_freshness_ledger.json"
SOURCE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "full_corpus_awakening_source_atlas.json"
INTEGRATION_REGISTRY_PATH = (
    WORKSPACE_ROOT / "self_actualize" / "qshrink_ap6d_full_corpus_integration_registry.json"
)
AWAKENING_NOTES_JSON_PATH = (
    WORKSPACE_ROOT / "self_actualize" / "ap6d_awakening_transition_notes.json"
)
AP6D_WAVE57_PATH = MANIFESTS95_ROOT / "AP6D_FULL_CORPUS_INTEGRATION_WAVE_57.json"
DEEP_ROOT = (
    MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)

CHARTER_PATH = MANIFESTS95_ROOT / "FOUR_AGENT_57_CYCLE_ORCHESTRATION_CHARTER.md"
MASTER_REGISTRY_PATH = MANIFESTS95_ROOT / "FOUR_AGENT_57_CYCLE_MASTER_REGISTRY.json"
VERIFICATION_PATH = MANIFESTS95_ROOT / "FOUR_AGENT_57_CYCLE_VERIFICATION.json"

LOOP_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "four_agent_57_cycle_loop_state.json"
PACKET_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "four_agent_57_cycle_packet_atlas.json"
RECEIPT_INDEX_PATH = WORKSPACE_ROOT / "self_actualize" / "four_agent_57_cycle_receipt_index.json"
ARTIFACTS_ROOT = WORKSPACE_ROOT / "self_actualize" / "four_agent_57_cycle_artifacts"

RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_four_agent_57_cycle_orchestration.md"
RUNTIME_VERIFICATION_PATH = MANIFESTS95_ROOT / "FOUR_AGENT_57_CYCLE_LOOP_RUNTIME_VERIFICATION.json"

CHARTER_MARKER = "FOUR_AGENT_57_CYCLE"

PHASE_SEQUENCE = [
    {
        "phase": "FIRE_RESEARCH_SYNTHESIS",
        "owner": "FA57-FIRE",
        "label": "Fire research-synthesis",
    },
    {
        "phase": "WATER_PLANNER_QUEST_PACK",
        "owner": "FA57-WATER",
        "label": "Water planner quest pack",
    },
    {
        "phase": "AIR_EXECUTION_BUNDLE",
        "owner": "FA57-AIR",
        "label": "Air execution bundle",
    },
    {
        "phase": "EARTH_PRUNE_DELTA",
        "owner": "FA57-EARTH",
        "label": "Earth prune delta",
    },
    {
        "phase": "PRIME_ARBITRATION_RESTART",
        "owner": "FA57-PRIME",
        "label": "Athena Prime arbitration restart",
    },
]

SUPPORT_CONTRACT = [
    "one synthesis artifact",
    "one Hall quest pack",
    "one Temple quest pack",
    "one execution receipt",
    "one prune/compression delta",
    "one awakening-note update",
    "one restart seed",
]

MASTER_AGENT_SPECS = [
    {
        "agent_id": "FA57-PRIME",
        "title": "Athena Prime",
        "role": "Council Arbiter / Restart Seeder",
        "element": "Aether",
        "packet_space": "council-only",
        "active_packet_limit": 0,
        "theme_lexicon": ["arbitrate", "stabilize", "council", "reseed"],
        "support_surfaces": [
            ACTIVE_RUN_PATH,
            BUILD_QUEUE_PATH,
            TEMPLE_STATE_PATH,
            QUEST_BOARD_PATH,
            CHARTER_PATH,
            LOOP_STATE_PATH,
        ],
        "status": "ACTIVE_COORDINATOR",
    },
    {
        "agent_id": "FA57-FIRE",
        "title": "Fire",
        "role": "Research-Synthesis",
        "element": "Fire",
        "packet_space": "4096 derived helper addresses",
        "active_packet_limit": 1024,
        "theme_lexicon": ["source", "ledger", "matrix", "metro"],
        "support_surfaces": [
            DEEP_ROOT / "README.md",
            DEEP_ROOT / "10_LEDGERS" / "01_CANONICAL_SOURCES.md",
            SOURCE_ATLAS_PATH,
            AP6D_WAVE57_PATH,
            ACTIVE_RUN_PATH,
            CHARTER_PATH,
        ],
        "status": "SEEDED",
    },
    {
        "agent_id": "FA57-WATER",
        "title": "Water",
        "role": "Planner / Quest Architect",
        "element": "Water",
        "packet_space": "4096 derived helper addresses",
        "active_packet_limit": 1024,
        "theme_lexicon": ["hall", "temple", "queue", "restart"],
        "support_surfaces": [
            QUEST_BOARD_PATH,
            TEMPLE_BOARD_PATH,
            TEMPLE_STATE_PATH,
            ACTIVE_QUEUE_PATH,
            NEXT_SELF_PROMPT_PATH,
            RECEIPT_INDEX_PATH,
        ],
        "status": "SEEDED",
    },
    {
        "agent_id": "FA57-AIR",
        "title": "Air",
        "role": "Worker-Adventurer / Execution",
        "element": "Air",
        "packet_space": "4096 derived helper addresses",
        "active_packet_limit": 1024,
        "theme_lexicon": ["runtime", "manuscript", "capsule", "family"],
        "support_surfaces": [
            ACTIVE_QUEUE_PATH,
            CONTROL_PACKET_PATH,
            INTEGRATION_REGISTRY_PATH,
            WORKSPACE_ROOT / "self_actualize" / "qshrink_agent_task_matrix.json",
            WORKSPACE_ROOT / "self_actualize" / "qshrink_network_integration.json",
            RECEIPT_INDEX_PATH,
        ],
        "status": "SEEDED",
    },
    {
        "agent_id": "FA57-EARTH",
        "title": "Earth",
        "role": "Pruner-Defrager / Compressor",
        "element": "Earth",
        "packet_space": "4096 derived helper addresses",
        "active_packet_limit": 1024,
        "theme_lexicon": ["qshrink", "dedupe", "archive", "structure"],
        "support_surfaces": [
            MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md",
            MANIFESTS_ROOT / "WEAKEST_FRONT_QUEUE.md",
            BUILD_QUEUE_PATH,
            ACTIVE_RUN_PATH,
            SOURCE_ATLAS_PATH,
            RECEIPT_INDEX_PATH,
        ],
        "status": "SEEDED",
    },
]

LOOP_DEFINITIONS = [
    ("Wave 1", 1, "Athena Prime", "Freeze Docs-gate truth, current spine truth, and local-only evidence law.", "SEEDED"),
    ("Wave 1", 2, "Athena Prime", "Snapshot the live control-plane split across Hall, Temple, manifests, runtime, and deep root.", "SEEDED"),
    ("Wave 1", 3, "Athena Prime", "Install the 4-master-agent registry and role-to-element mapping.", "SEEDED"),
    ("Wave 1", 4, "Athena Prime", "Install the per-agent 4^6 packet model and active/dormant limits.", "SEEDED"),
    ("Wave 1", 5, "Fire", "Bind the first full-corpus source atlas across every tome and manuscript root.", "SEEDED"),
    ("Wave 1", 6, "Athena Prime", "Bind the first control-surface parity matrix across Hall, Temple, manifests, and runtime.", "SEEDED"),
    ("Wave 1", 7, "Water", "Install the Hall macro-quest section and Temple mirror section for the 57-loop program.", "SEEDED"),
    ("Wave 1", 8, "Athena Prime", "Emit Loop 1 receipt, first council note, and the canonical loop-state seed.", "SEEDED"),
    ("Wave 2", 9, "Fire", "Inventory the live canonical basis and reconcile it against all current corpus roots.", "PLANNED"),
    ("Wave 2", 10, "Fire", "Scan every manuscript/tome family for neglected bridges, duplicate authorities, and dead mirrors.", "PLANNED"),
    ("Wave 2", 11, "Fire", "Reconcile the deep root 16x16 matrix against live runtime and AP6D surfaces.", "PLANNED"),
    ("Wave 2", 12, "Fire", "Reconcile the 64 observer passes against the current quest and feeder pressure.", "PLANNED"),
    ("Wave 2", 13, "Fire", "Reconcile Level 1-4 metro maps against Hall, Temple, and active manifolds.", "PLANNED"),
    ("Wave 2", 14, "Fire", "Reconcile Level 5-7 metro surfaces and Appendix Q guardrails without promoting drift.", "PLANNED"),
    ("Wave 2", 15, "Fire", "Extract math, hybrid equations, operators, and algorithm candidates from the MATH/CUT/PZPM stack into planner-ready packets.", "PLANNED"),
    ("Wave 2", 16, "Fire", "Collapse the research pass into one synthesis ledger that the planner must consume.", "PLANNED"),
    ("Wave 3", 17, "Water", "Convert the synthesis ledger into one ranked planner backlog.", "PLANNED"),
    ("Wave 3", 18, "Water", "Generate 4 master Hall macro quests, one per operational agent.", "PLANNED"),
    ("Wave 3", 19, "Water", "Generate the matching Temple receiver/binding quests for the same 4 masters.", "PLANNED"),
    ("Wave 3", 20, "Water", "Generate the 16 macro packet parents under each master for the active loop.", "PLANNED"),
    ("Wave 3", 21, "Water", "Expand those into 64 observer packets and 256 dependency fibers in the packet atlas.", "PLANNED"),
    ("Wave 3", 22, "Water", "Attach witness class, writeback target, and restart seed to every promoted packet.", "PLANNED"),
    ("Wave 3", 23, "Water", "Build the loop acceptance pack: success metrics, blockers, residuals, and stop conditions.", "PLANNED"),
    ("Wave 3", 24, "Water", "Emit the first planner-complete cycle pack and hold archive-dark-matter issues open rather than smoothing them.", "PLANNED"),
    ("Wave 4", 25, "Air", "Execute the highest-yield truth-sync repairs first.", "PLANNED"),
    ("Wave 4", 26, "Air", "Execute manifest/runtime writebacks required by the current loop.", "PLANNED"),
    ("Wave 4", 27, "Air", "Execute deep-root and metro writebacks required by the current loop.", "PLANNED"),
    ("Wave 4", 28, "Air", "Execute AP6D registry, packet, and transition-note writebacks required by the current loop.", "PLANNED"),
    ("Wave 4", 29, "Air", "Execute manuscript, appendix, capsule, and family writebacks required by the current loop.", "PLANNED"),
    ("Wave 4", 30, "Air", "Close or advance the Hall and Temple quests touched by the loop.", "PLANNED"),
    ("Wave 4", 31, "Air", "Consolidate worker receipts into one replay-bearing execution bundle.", "PLANNED"),
    ("Wave 4", 32, "Air", "Hand the loop to the pruner with an explicit change inventory and unresolved residual list.", "PLANNED"),
    ("Wave 5", 33, "Earth", "Prune duplicate routes, stale mirrors, and dead historical subpaths.", "PLANNED"),
    ("Wave 5", 34, "Earth", "Deduplicate Hall/Temple/manifests where the same truth is being carried twice.", "PLANNED"),
    ("Wave 5", 35, "Earth", "Run a Q-SHRINK style compression pass on bulky quest, appendix, and route prose.", "PLANNED"),
    ("Wave 5", 36, "Earth", "Compact ledger structures so packet truth is machine-readable before it is human-polished.", "PLANNED"),
    ("Wave 5", 37, "Earth", "Tighten family routes, atlas linkages, and cross-manuscript bridge naming.", "PLANNED"),
    ("Wave 5", 38, "Earth", "Triage archive dark matter and duplicate ZIP identities without erasing unresolved evidence.", "PLANNED"),
    ("Wave 5", 39, "Earth", "Simplify the active control surfaces so only current truth stays visible.", "PLANNED"),
    ("Wave 5", 40, "Earth", "Emit the prune delta, tightened restart seed, and the next reassessment window.", "PLANNED"),
    ("Wave 6", 41, "Athena Prime", "Refresh the Athena Prime, Fire, Water, Air, and Earth awakening notes for the active loop.", "PLANNED"),
    ("Wave 6", 42, "Athena Prime", "Recompute the cross-agent council handshake and the next compensation lane.", "PLANNED"),
    ("Wave 6", 43, "Athena Prime", "Synchronize Hall, Temple, manifests, runtime, and restart surfaces to one post-prune truth.", "PLANNED"),
    ("Wave 6", 44, "Athena Prime", "Embed hybrid equations, algorithms, and formal operators into the current active framework surfaces.", "PLANNED"),
    ("Wave 6", 45, "Athena Prime", "Update the skill-growth queue and the desired-skill graph for the next loop family.", "PLANNED"),
    ("Wave 6", 46, "Athena Prime", "Parameterize dormant-seat pressure without promoting dormant seats into board-visible work.", "PLANNED"),
    ("Wave 6", 47, "Athena Prime", "Turn gate deficits, blocker drift, and route gaps into explicit agent-readable tasks.", "PLANNED"),
    ("Wave 6", 48, "Athena Prime", "Emit the integration review with unresolved contradictions preserved as named residuals.", "PLANNED"),
    ("Wave 7", 49, "Athena Prime", "Run runtime verification for Docs honesty, frontier agreement, packet freshness, and restart coherence.", "PLANNED"),
    ("Wave 7", 50, "Athena Prime", "Run deep-root verification for 16/256/64/15+0, metro counts, and Appendix Q legality.", "PLANNED"),
    ("Wave 7", 51, "Athena Prime", "Run AP6D verification for 16/64/256/1024/4096, active/dormant honesty, and shadow compatibility.", "PLANNED"),
    ("Wave 7", 52, "Athena Prime", "Run awakening-note verification so no agent note is missing surfaces, handoff, or restart seed.", "PLANNED"),
    ("Wave 7", 53, "Athena Prime", "Run the corpus-wide truth review and explicitly name contradictions instead of smoothing them over.", "PLANNED"),
    ("Wave 7", 54, "Athena Prime", "Roll out the loop outputs in order: control surfaces, deep root, AP6D registry, metro/appendix, manuscript/capsule, awakening notes.", "PLANNED"),
    ("Wave 7", 55, "Athena Prime", "Emit the final integration ledger for that loop family.", "PLANNED"),
    ("Wave 7", 56, "Athena Prime", "Emit the next restart packet spanning Hall, Temple, manifests, metro, runtime, and awakening notes.", "PLANNED"),
    ("Wave 7", 57, "Athena Prime", "Archive the completed 57th loop into receipts and reopen only the highest-yield unblocked next wave.", "PLANNED"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def upsert_marker_block(text: str, marker: str, block: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    replacement = f"{start}\n{block.rstrip()}\n{end}"
    if start in text and end in text:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + "\n\n" + replacement + "\n"


def prepend_numbered_entry(text: str, entry: str, header: str) -> str:
    if entry in text:
        return text
    parts = text.split(header, 1)
    if len(parts) != 2:
        return text.rstrip() + f"\n\n{header}{entry}\n"
    prefix, suffix = parts
    numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\.\s", suffix, re.M)]
    next_number = max(numbers) + 1 if numbers else 1
    return prefix + header + f"{next_number}. {entry}\n" + suffix


def base4_code(index: int, width: int) -> str:
    value = ""
    current = index
    for _ in range(width):
        value = str(current % 4) + value
        current //= 4
    return value.zfill(width)


def path_exists(path: Path) -> bool:
    return path.exists()


def live_state() -> dict[str, Any]:
    docs_gate = docs_gate_payload()
    next4_state = load_json(NEXT4_STATE_PATH, {})
    control_packet = load_json(CONTROL_PACKET_PATH, {})
    packet_freshness = load_json(PACKET_FRESHNESS_PATH, {})
    return {
        "docs_gate": docs_gate,
        "next4_state": next4_state,
        "control_packet": control_packet,
        "packet_freshness": packet_freshness,
        "source_atlas_exists": path_exists(SOURCE_ATLAS_PATH),
        "integration_registry_exists": path_exists(INTEGRATION_REGISTRY_PATH),
        "awakening_notes_exists": path_exists(AWAKENING_NOTES_JSON_PATH),
        "ap6d_wave57_exists": path_exists(AP6D_WAVE57_PATH),
    }


def current_spine_fields(state: dict[str, Any]) -> dict[str, Any]:
    next4_state = state["next4_state"]
    control_packet = state["control_packet"]
    return {
        "active_coordination_membrane": control_packet.get("active_coordination_membrane", "Q41 / TQ06"),
        "q42_carried_witness": next4_state.get("current_carried_witness", "QS64-20 Connectivity-Diagnose-Fractal"),
        "q42_operational_current": next4_state.get(
            "operational_current",
            next4_state.get("active_local_subfront", "QS64-24 Connectivity-Refine-Fractal"),
        ),
        "q42_historical_local_proof": next4_state.get(
            "historical_local_proof", "QS64-24 Connectivity-Refine-Fractal"
        ),
        "q42_next_hall_seed": next4_state.get("next_hall_seed_display", "none; do not invent QS64-25"),
        "deeper_receiver": next4_state.get(
            "next_temple_handoff", "TQ04: Bind The Helical Schema Pack To A Runner Contract"
        ),
        "reserve_frontier": next4_state.get("reserve_frontier", "Q46"),
        "blocked_external_front": next4_state.get("blocked_external_front", "Q02"),
        "separate_runtime_seed": control_packet.get(
            "separate_runtime_seed", "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose"
        ),
        "ap6d_operational_current": control_packet.get("operational_current", "AP6D-H-WATER-Diagnose"),
        "ap6d_next_hall_seed": control_packet.get("next_hall_seed", "AP6D-H-WATER-Refine"),
        "docs_gate_status": state["docs_gate"]["status"],
        "docs_gate_truth": state["docs_gate"]["truth"],
    }


def master_registry(spine: dict[str, Any], current_owner: str = "FA57-FIRE") -> list[dict[str, Any]]:
    handoff_targets = {
        "FA57-PRIME": "FA57-FIRE",
        "FA57-FIRE": "FA57-WATER",
        "FA57-WATER": "FA57-AIR",
        "FA57-AIR": "FA57-EARTH",
        "FA57-EARTH": "FA57-PRIME",
    }
    current_fronts = {
        "FA57-PRIME": spine["active_coordination_membrane"],
        "FA57-FIRE": f"Deep-root corpus synthesis / {spine['q42_carried_witness']}",
        "FA57-WATER": hall_quest_id("FA57-WATER"),
        "FA57-AIR": f"Execution queue / {spine['deeper_receiver']}",
        "FA57-EARTH": f"Prune-compress reserve / {spine['reserve_frontier']}",
    }
    restart_seeds = {
        "FA57-PRIME": "LOOP57-L01 -> FA57-FIRE -> research synthesis",
        "FA57-FIRE": "LOOP57-L01 -> FA57-WATER -> planner quest pack",
        "FA57-WATER": "LOOP57-L01 -> FA57-AIR -> execution bundle",
        "FA57-AIR": "LOOP57-L01 -> FA57-EARTH -> prune delta",
        "FA57-EARTH": "LOOP57-L01 -> FA57-PRIME -> arbitration restart",
    }
    rows: list[dict[str, Any]] = []
    for spec in MASTER_AGENT_SPECS:
        rows.append(
            {
                "agent_id": spec["agent_id"],
                "role": spec["role"],
                "element": spec["element"],
                "current_front": current_fronts[spec["agent_id"]],
                "packet_space": spec["packet_space"],
                "active_packet_limit": spec["active_packet_limit"],
                "support_surfaces": [relative_string(path) for path in spec["support_surfaces"]],
                "handoff_target": handoff_targets[spec["agent_id"]],
                "restart_seed": restart_seeds[spec["agent_id"]],
                "status": current_owner_status(spec["agent_id"], current_owner),
            }
        )
    return rows


def hall_quest_id(agent_id: str) -> str:
    return {
        "FA57-FIRE": "FA57-Q-FIRE-RESEARCH",
        "FA57-WATER": "FA57-Q-WATER-PLANNER",
        "FA57-AIR": "FA57-Q-AIR-WORKER",
        "FA57-EARTH": "FA57-Q-EARTH-PRUNER",
    }[agent_id]


def temple_mirror_id(agent_id: str) -> str:
    return {
        "FA57-PRIME": "T57-PRIME-ARBITRATION",
        "FA57-FIRE": "T57-FIRE-SYNTHESIS-GATE",
        "FA57-WATER": "T57-WATER-QUEST-BINDING",
        "FA57-AIR": "T57-AIR-EXECUTION-LIFT",
        "FA57-EARTH": "T57-EARTH-PRUNE-RETURN",
    }[agent_id]


def phase_sequence_ids() -> list[str]:
    return [item["phase"] for item in PHASE_SEQUENCE]


def phase_metadata(phase_id: str) -> dict[str, Any]:
    for item in PHASE_SEQUENCE:
        if item["phase"] == phase_id:
            return item
    return PHASE_SEQUENCE[0]


def owner_phase(owner: str) -> dict[str, Any]:
    for item in PHASE_SEQUENCE:
        if item["owner"] == owner:
            return item
    return PHASE_SEQUENCE[0]


def cycle_artifact_paths(loop_id: str) -> dict[str, Path]:
    loop_root = ARTIFACTS_ROOT / loop_id
    return {
        "synthesis_artifact": loop_root / "fire_synthesis_ledger.md",
        "hall_quest_pack": loop_root / "water_hall_macro_pack.md",
        "temple_quest_pack": loop_root / "water_temple_mirror_pack.md",
        "execution_receipt": loop_root / "air_execution_bundle.md",
        "prune_delta": loop_root / "earth_prune_delta.md",
        "awakening_note_update": loop_root / "prime_awakening_note_update.md",
        "restart_seed": loop_root / "prime_restart_seed.md",
    }


def cycle_artifact_bundle(loop_id: str) -> dict[str, str]:
    return {
        key: relative_string(path)
        for key, path in cycle_artifact_paths(loop_id).items()
    }


def artifact_completion_map(loop_id: str) -> dict[str, bool]:
    return {key: path.exists() for key, path in cycle_artifact_paths(loop_id).items()}


def current_owner_status(agent_id: str, current_owner: str) -> str:
    if agent_id == "FA57-PRIME":
        return "ACTIVE_COORDINATOR" if current_owner == "FA57-PRIME" else "COORDINATING"
    if agent_id == current_owner:
        return "ACTIVE"
    return "READY"


def generate_packet_atlas(
    spine: dict[str, Any],
    registry_rows: list[dict[str, Any]],
    loop_id: str = "FA57-L01",
) -> dict[str, Any]:
    counts = {1: 4, 2: 16, 3: 64, 4: 256, 5: 1024, 6: 4096}
    packet_entries: list[dict[str, Any]] = []
    per_master_summary: list[dict[str, Any]] = []
    registry_by_id = {row["agent_id"]: row for row in registry_rows}

    for spec in MASTER_AGENT_SPECS:
        if spec["active_packet_limit"] == 0:
            continue
        registry_row = registry_by_id[spec["agent_id"]]
        summary = {
            "agent_id": spec["agent_id"],
            "title": spec["title"],
            "hall_quest_id": hall_quest_id(spec["agent_id"]),
            "depth_counts": {},
            "active_depth6_count": spec["active_packet_limit"],
            "dormant_depth6_count": counts[6] - spec["active_packet_limit"],
        }
        support_surfaces = [relative_string(path) for path in spec["support_surfaces"]]
        witness_class = {
            "FA57-FIRE": "direct",
            "FA57-WATER": "derived",
            "FA57-AIR": "direct",
            "FA57-EARTH": "derived",
        }[spec["agent_id"]]

        for depth, count in counts.items():
            summary["depth_counts"][str(depth)] = count
            for index in range(count):
                code = base4_code(index, depth)
                theme = " -> ".join(spec["theme_lexicon"][int(digit)] for digit in code)
                target_surface = support_surfaces[index % len(support_surfaces)]
                if depth == 6:
                    active_or_dormant = "ACTIVE" if index < spec["active_packet_limit"] else "DORMANT"
                    status = active_or_dormant
                else:
                    active_or_dormant = "ACTIVE"
                    status = "ACTIVE" if depth in (1, 2, 5) else "SEEDED"
                packet_entries.append(
                    {
                        "loop_id": loop_id,
                        "master_agent": spec["agent_id"],
                        "packet_depth": depth,
                        "packet_id": f"{loop_id}.{spec['agent_id']}.D{depth}.{code}",
                        "theme": theme,
                        "target_surface": target_surface,
                        "quest_parent": hall_quest_id(spec["agent_id"]),
                        "witness_class": witness_class,
                        "status": status,
                        "active_or_dormant": active_or_dormant,
                        "restart_seed": registry_row["restart_seed"],
                    }
                )
        per_master_summary.append(summary)

    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "loop_id": loop_id,
        "mode": "macro_plus_packets",
        "counts_per_depth": {"1": 4, "2": 16, "3": 64, "4": 256, "5": 1024, "6": 4096},
        "packet_entries_total": len(packet_entries),
        "per_master_summary": per_master_summary,
        "packet_entries": packet_entries,
        "spine_context": {
            "coordination_membrane": spine["active_coordination_membrane"],
            "q42_carried_witness": spine["q42_carried_witness"],
            "deeper_receiver": spine["deeper_receiver"],
            "reserve_frontier": spine["reserve_frontier"],
            "separate_runtime_seed": spine["separate_runtime_seed"],
            "ap6d_operational_current": spine["ap6d_operational_current"],
        },
    }


def receipt_index() -> dict[str, Any]:
    entries = []
    for wave, step, primary_agent, deliverable, status in LOOP_DEFINITIONS:
        receipt_path = RECEIPTS_ROOT / f"2026-03-13_four_agent_57_cycle_loop{step:02d}.md"
        loop_id = f"FA57-L{step:02d}"
        entries.append(
            {
                "loop_id": loop_id,
                "cycle_number": step,
                "wave": wave,
                "primary_agent": primary_agent,
                "deliverable": deliverable,
                "status": "ACTIVE" if step == 1 else "PLANNED",
                "phase_sequence": phase_sequence_ids(),
                "current_phase": "FIRE_RESEARCH_SYNTHESIS" if step == 1 else None,
                "required_artifacts": cycle_artifact_bundle(loop_id),
                "completed_artifacts": artifact_completion_map(loop_id),
                "completion_contract_met": all(artifact_completion_map(loop_id).values()) and receipt_path.exists(),
                "receipt_path": relative_string(receipt_path),
                "actual_receipt_exists": receipt_path.exists(),
            }
        )
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "total_cycles": 57,
        "current_cycle": "FA57-L01",
        "current_cycle_status": "ACTIVE",
        "orchestration_receipt": relative_string(RECEIPT_PATH),
        "entries": entries,
    }


def loop_state(spine: dict[str, Any], registry_rows: list[dict[str, Any]], packet_atlas: dict[str, Any]) -> dict[str, Any]:
    current_phase = "FIRE_RESEARCH_SYNTHESIS"
    current_owner = "FA57-FIRE"
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "mode": "macro_plus_packets",
        "total_cycles": 57,
        "current_cycle": "FA57-L01",
        "current_cycle_status": "ACTIVE",
        "current_phase": current_phase,
        "current_phase_index": 0,
        "current_cycle_owner": current_owner,
        "current_sequence": [item["owner"] for item in PHASE_SEQUENCE],
        "current_hall_quest_id": hall_quest_id(current_owner),
        "current_temple_mirror_id": temple_mirror_id(current_owner),
        "docs_gate": spine["docs_gate_status"],
        "live_spine": spine,
        "charter_path": relative_string(CHARTER_PATH),
        "master_registry_path": relative_string(MASTER_REGISTRY_PATH),
        "packet_atlas_path": relative_string(PACKET_ATLAS_PATH),
        "receipt_index_path": relative_string(RECEIPT_INDEX_PATH),
        "source_atlas_path": relative_string(SOURCE_ATLAS_PATH),
        "awakening_notes_path": relative_string(AWAKENING_NOTES_JSON_PATH),
        "support_contract": SUPPORT_CONTRACT,
        "current_cycle_artifacts": cycle_artifact_bundle("FA57-L01"),
        "hall_rows_visible": 4,
        "temple_rows_visible": 5,
        "registry_rows": len(registry_rows),
        "packet_entry_count": packet_atlas["packet_entries_total"],
        "parity_matrix": {
            "active_run": path_exists(ACTIVE_RUN_PATH),
            "build_queue": path_exists(BUILD_QUEUE_PATH),
            "quest_board": path_exists(QUEST_BOARD_PATH),
            "temple_board": path_exists(TEMPLE_BOARD_PATH),
            "temple_state": path_exists(TEMPLE_STATE_PATH),
            "active_queue": path_exists(ACTIVE_QUEUE_PATH),
            "next_self_prompt": path_exists(NEXT_SELF_PROMPT_PATH),
            "source_atlas": path_exists(SOURCE_ATLAS_PATH),
            "integration_registry": path_exists(INTEGRATION_REGISTRY_PATH),
            "awakening_notes": path_exists(AWAKENING_NOTES_JSON_PATH),
            "deep_root": path_exists(DEEP_ROOT / "README.md"),
            "ap6d_wave57": path_exists(AP6D_WAVE57_PATH),
        },
        "current_restart_seed": "FA57-L01 -> FA57-WATER -> planner quest pack",
    }


def render_charter(spine: dict[str, Any], registry_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Four-Agent 57-Cycle Corpus Orchestration Charter",
        "",
        "Date: `2026-03-13`",
        "Truth: `OK`",
        f"Docs Gate: `{spine['docs_gate_status']}`",
        "Mode: `Macro + Packets`",
        "Spine Policy: `Preserve Current Spine`",
        "",
        "## Live Spine Anchor",
        "",
        f"- active coordination membrane: `{spine['active_coordination_membrane']}`",
        f"- Q42 carried witness: `{spine['q42_carried_witness']}`",
        f"- Q42 operational current: `{spine['q42_operational_current']}`",
        f"- Q42 historical local proof: `{spine['q42_historical_local_proof']}`",
        f"- Q42 next Hall seed: `{spine['q42_next_hall_seed']}`",
        f"- deeper receiver: `{spine['deeper_receiver']}`",
        f"- reserve frontier: `{spine['reserve_frontier']}`",
        f"- separate runtime seed: `{spine['separate_runtime_seed']}`",
        f"- AP6D operational current: `{spine['ap6d_operational_current']}`",
        f"- AP6D next Hall seed: `{spine['ap6d_next_hall_seed']}`",
        "",
        "## Master Agent Contract",
        "",
        "| Agent | Role | Current front | Handoff target | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in registry_rows:
        lines.append(
            f"| `{row['agent_id']}` | {row['role']} | `{row['current_front']}` | "
            f"`{row['handoff_target']}` | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Packet Model",
            "",
            "- depth 1: `4` elemental bands",
            "- depth 2: `16` macro packets",
            "- depth 3: `64` observer packets",
            "- depth 4: `256` dependency fibers",
            "- depth 5: `1024` active helper seats",
            "- depth 6: `4096` full derived helper addresses",
            "",
            "Hall rows stay macro-sized at `4` visible operational quests.",
            "Temple keeps the mirrored binding/receiver layer above those rows.",
            "The nested packet work remains in ledgers and registries.",
            "",
            "## Per-Loop Contract",
            "",
            "1. one synthesis artifact",
            "2. one Hall quest pack",
            "3. one Temple quest pack",
            "4. one execution receipt",
            "5. one prune/compression delta",
            "6. one awakening-note update",
            "7. one restart seed",
            "",
            "## 57-Cycle Matrix",
            "",
            "| Cycle | Wave | Primary Agent | Deliverable | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for wave, step, primary_agent, deliverable, status in LOOP_DEFINITIONS:
        lines.append(
            f"| {step} | {wave} | `{primary_agent}` | {deliverable} | `{status}` |"
        )
    lines.extend(
        [
            "",
            "## Control Law",
            "",
            "- never claim live Google Docs success while OAuth files are missing",
            "- never replace the live feeder spine with the new orchestration overlay",
            "- never explode Hall into literal `16384` visible quest rows",
            "- only explicitly promoted packets may surface as Hall or Temple quests",
            "- preserve contradictions as named residuals instead of smoothing them away",
            "",
        ]
    )
    return "\n".join(lines)


def render_hall_macro_section(spine: dict[str, Any], state: dict[str, Any]) -> str:
    current_owner = state["current_cycle_owner"]
    fire_status = "ACTIVE" if current_owner == "FA57-FIRE" else "OPEN"
    water_status = "ACTIVE" if current_owner == "FA57-WATER" else "OPEN"
    air_status = "ACTIVE" if current_owner == "FA57-AIR" else "OPEN"
    earth_status = "ACTIVE" if current_owner == "FA57-EARTH" else "OPEN"
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Macro Quests",
            "",
            "This section seeds the macro-visible Hall layer for the new 57-cycle loop.",
            "The nested `4^6` packet work stays in the packet atlas and receipt index.",
            "",
            f"### FA57-Q-FIRE-RESEARCH `[{fire_status}]`",
            "",
            "- Objective:",
            "  scan every tome, manuscript, ledger, atlas, and deep-root surface, then emit one full-corpus synthesis artifact for Loop 1",
            "- Why now:",
            "  the live organism already has the deep root, AP6D wave surfaces, and the source atlas, but it still needs one explicit Fire-owned synthesis pass that feeds the new loop without replacing the existing spine",
            "- Target surfaces:",
            f"  `{relative_string(DEEP_ROOT / 'README.md')}`",
            f"  `{relative_string(DEEP_ROOT / '10_LEDGERS' / '01_CANONICAL_SOURCES.md')}`",
            f"  `{relative_string(SOURCE_ATLAS_PATH)}`",
            f"  `{relative_string(AP6D_WAVE57_PATH)}`",
            "- Best lane:",
            "  `fire -> deep root -> matrix -> metro -> synthesis ledger`",
            "- Witness needed:",
            "  one blocker-honest synthesis ledger tied to the full corpus and the live Q42/AP6D/TQ04/Q46/Q50 spine",
            "- Writeback:",
            "  charter, loop state, packet atlas, Hall quest board, and orchestration receipt",
            "- Restart seed:",
            "  `FA57-L01 -> FA57-WATER -> planner quest pack`",
            "",
            f"### FA57-Q-WATER-PLANNER `[{water_status}]`",
            "",
            "- Objective:",
            "  convert the Fire synthesis artifact into ranked Hall and Temple quest packs plus promoted packet ledgers",
            "- Why now:",
            "  the planner layer is how the loop turns synthesis into ownerable structure instead of loose narrative pressure",
            "- Target surfaces:",
            f"  `{relative_string(QUEST_BOARD_PATH)}`",
            f"  `{relative_string(TEMPLE_BOARD_PATH)}`",
            f"  `{relative_string(ACTIVE_QUEUE_PATH)}`",
            f"  `{relative_string(NEXT_SELF_PROMPT_PATH)}`",
            "- Best lane:",
            "  `water -> hall -> temple -> queue -> restart`",
            "- Witness needed:",
            "  one ranked planner backlog, one macro Hall pack, one Temple mirror pack, and one packet promotion ledger",
            "- Writeback:",
            "  Hall quest board, Temple board, active queue, restart prompt, and receipt index",
            "- Restart seed:",
            "  `FA57-L01 -> FA57-AIR -> execution bundle`",
            "",
            f"### FA57-Q-AIR-WORKER `[{air_status}]`",
            "",
            "- Objective:",
            "  claim the highest-yield unblocked planner packets and land the first replay-bearing execution bundle without displacing the live feeders",
            "- Why now:",
            "  the worker/adventurer lane turns planned packets into actual corpus improvement instead of letting the loop stop at structure",
            "- Target surfaces:",
            f"  `{relative_string(ACTIVE_QUEUE_PATH)}`",
            f"  `{relative_string(CONTROL_PACKET_PATH)}`",
            f"  `{relative_string(INTEGRATION_REGISTRY_PATH)}`",
            f"  `{relative_string(RECEIPT_INDEX_PATH)}`",
            "- Best lane:",
            "  `air -> execution -> runtime -> manuscript -> family`",
            "- Witness needed:",
            "  one execution receipt bundle, one explicit change inventory, and one lawful handoff to the pruner",
            "- Writeback:",
            "  active queue, receipts, manifests touched by execution, and the packet atlas",
            "- Restart seed:",
            "  `FA57-L01 -> FA57-EARTH -> prune delta`",
            "",
            f"### FA57-Q-EARTH-PRUNER `[{earth_status}]`",
            "",
            "- Objective:",
            "  compress, deduplicate, defrag, and tighten what the worker changed while preserving unresolved contradictions honestly",
            "- Why now:",
            "  the loop only deepens safely if every execution pass is followed by structure-hardening, compression, and route cleanup",
            "- Target surfaces:",
            f"  `{relative_string(MANIFESTS_ROOT / 'QSHRINK_ACTIVE_FRONT.md')}`",
            f"  `{relative_string(MANIFESTS_ROOT / 'WEAKEST_FRONT_QUEUE.md')}`",
            f"  `{relative_string(SOURCE_ATLAS_PATH)}`",
            f"  `{relative_string(BUILD_QUEUE_PATH)}`",
            "- Best lane:",
            "  `earth -> q-shrink -> dedupe -> archive -> restart`",
            "- Witness needed:",
            "  one prune delta, one tightened restart seed, one duplicate-route audit, and one unresolved-residual list",
            "- Writeback:",
            "  build queue, active run, q-shrink surfaces, packet atlas, and orchestration receipt",
            "- Restart seed:",
            "  `FA57-L01 -> FA57-PRIME -> arbitration restart`",
            "",
        ]
    )


def render_temple_mirror_section(state: dict[str, Any]) -> str:
    current_owner = state["current_cycle_owner"]
    prime_status = "ACTIVE" if current_owner == "FA57-PRIME" else "OPEN"
    fire_status = "ACTIVE" if current_owner == "FA57-FIRE" else "OPEN"
    water_status = "ACTIVE" if current_owner == "FA57-WATER" else "OPEN"
    air_status = "ACTIVE" if current_owner == "FA57-AIR" else "OPEN"
    earth_status = "ACTIVE" if current_owner == "FA57-EARTH" else "OPEN"
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Temple Mirrors",
            "",
            "This section mirrors the Hall macro quests at the Temple layer without replacing `TQ04`, `TQ06`, or the live feeder spine.",
            "",
            f"### T57-PRIME-ARBITRATION `[{prime_status}]`",
            "",
            "- Objective:",
            "  arbitrate the 57-cycle loop, preserve the live feeder split, refresh awakening support, and emit the next lawful restart seed",
            "- Why now:",
            "  the loop needs one Temple-level council surface above the four operational masters",
            "- Target surfaces:",
            f"  `{relative_string(TEMPLE_STATE_PATH)}`",
            f"  `{relative_string(CHARTER_PATH)}`",
            f"  `{relative_string(LOOP_STATE_PATH)}`",
            f"  `{relative_string(AWAKENING_NOTES_JSON_PATH)}`",
            "- Best lane:",
            "  `aether -> council -> arbitration -> restart`",
            "- Witness needed:",
            "  one council note, one contradiction ledger, one restart seed, and one preserved blocker statement",
            "- Writeback:",
            "  Temple state, Temple board, restart prompt, and receipt",
            "- Restart seed:",
            "  `FA57-L01 -> FA57-FIRE -> research synthesis`",
            "",
            f"### T57-FIRE-SYNTHESIS-GATE `[{fire_status}]`",
            f"### T57-WATER-QUEST-BINDING `[{water_status}]`",
            f"### T57-AIR-EXECUTION-LIFT `[{air_status}]`",
            f"### T57-EARTH-PRUNE-RETURN `[{earth_status}]`",
            "",
            "These four mirrors stay macro-sized. Their detailed packet work remains in the packet atlas.",
            "",
        ]
    )


def render_active_run_block(spine: dict[str, Any], state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Overlay",
            "",
            "- truth: `OK`",
            "- docs gate: `BLOCKED`",
            "- mode: `Macro + Packets`",
            f"- current cycle: `{state['current_cycle']}`",
            f"- current phase: `{state['current_phase']}`",
            f"- current owner: `{state['current_cycle_owner']}`",
            "- sequence: `Fire -> Water -> Air -> Earth -> Athena Prime`",
            f"- spine preserved: `{spine['active_coordination_membrane']}` / `{spine['q42_carried_witness']}` / `{spine['q42_operational_current']}` / `{spine['q42_next_hall_seed']}` / `{spine['deeper_receiver']}` / `{spine['reserve_frontier']}` / `{spine['separate_runtime_seed']}`",
            f"- AP6D assistive overlay: `{spine['ap6d_operational_current']}` -> `{spine['ap6d_next_hall_seed']}`",
            f"- charter: `{relative_string(CHARTER_PATH)}`",
            f"- loop state: `{relative_string(LOOP_STATE_PATH)}`",
            f"- registry: `{relative_string(MASTER_REGISTRY_PATH)}`",
            f"- packet atlas: `{relative_string(PACKET_ATLAS_PATH)}`",
            f"- receipt index: `{relative_string(RECEIPT_INDEX_PATH)}`",
            f"- receipt: `{relative_string(RECEIPT_PATH)}`",
        ]
    )


def render_build_queue_block(spine: dict[str, Any], state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Build Order",
            "",
            "1. `FA57-FIRE`: full-corpus research synthesis over every tome, manuscript, ledger, atlas, and deep-root surface",
            "2. `FA57-WATER`: Hall/Temple quest architecture plus packet promotion ledgers",
            "3. `FA57-AIR`: highest-yield unblocked execution bundle",
            "4. `FA57-EARTH`: prune/compress/defrag return",
            "5. `FA57-PRIME`: arbitration, awakening-note refresh, restart reseed",
            "",
            f"Current owner: `{state['current_cycle_owner']}`",
            f"Current restart seed: `{state['current_restart_seed']}`",
            "",
            "Guardrails:",
            f"- preserve `{spine['active_coordination_membrane']}`, `{spine['q42_carried_witness']}`, `{spine['q42_operational_current']}`, `{spine['q42_next_hall_seed']}`, `{spine['deeper_receiver']}`, `{spine['reserve_frontier']}`, and `{spine['separate_runtime_seed']}`",
            "- do not create literal 16384 visible board rows",
            "- do not invent `QS64-25`",
            "- do not claim live Docs success while OAuth files are missing",
        ]
    )


def render_active_queue_block(spine: dict[str, Any], state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Runtime Overlay",
            "",
            f"- current cycle: `{state['current_cycle']}`",
            f"- current macro phase: `{phase_metadata(state['current_phase'])['label']}`",
            f"- current owner: `{state['current_cycle_owner']}`",
            f"- preserved feeder spine: `{spine['active_coordination_membrane']}`, `{spine['q42_carried_witness']}`, `{spine['q42_operational_current']}`, `{spine['q42_next_hall_seed']}`, `{spine['deeper_receiver']}`, `{spine['reserve_frontier']}`, `{spine['blocked_external_front']}`",
            f"- AP6D assistive uptake: `{spine['ap6d_operational_current']}` -> `{spine['ap6d_next_hall_seed']}`",
            "- Hall rows stay macro-sized at 4 operational quests",
            "- nested packet work lives in `self_actualize/four_agent_57_cycle_packet_atlas.json`",
            "- restart order: `Fire -> Water -> Air -> Earth -> Athena Prime`",
        ]
    )


def render_next_self_prompt_block(spine: dict[str, Any], state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Overlay",
            "",
            "Read these surfaces before selecting any loop-specific work:",
            f"- `{relative_string(CHARTER_PATH)}`",
            f"- `{relative_string(LOOP_STATE_PATH)}`",
            f"- `{relative_string(MASTER_REGISTRY_PATH)}`",
            f"- `{relative_string(PACKET_ATLAS_PATH)}`",
            f"- `{relative_string(RECEIPT_INDEX_PATH)}`",
            "",
            "Preserve this overlay law:",
            f"- current cycle / phase: `{state['current_cycle']}` / `{state['current_phase']}`",
            f"- keep `{spine['active_coordination_membrane']}` as the active membrane",
            f"- keep `{spine['q42_carried_witness']}` as the Q42 carried witness",
            f"- keep `{spine['q42_operational_current']}` as the operational local current and `{spine['q42_next_hall_seed']}` as the next Hall seed",
            f"- keep `{spine['deeper_receiver']}` as the deeper receiver",
            f"- keep `{spine['reserve_frontier']}` reserve-only and `{spine['blocked_external_front']}` blocked",
            f"- keep `{spine['separate_runtime_seed']}` separate from the Hall/Temple macro loop",
            "- keep Hall visible rows macro-sized and route deeper work through the packet atlas",
            "- end each loop-family pass with one artifact-backed move, one writeback, one awakening-note touchpoint, and one restart seed",
        ]
    )


def render_receipt(spine: dict[str, Any], registry_rows: list[dict[str, Any]], packet_atlas: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Four-Agent 57-Cycle Orchestration Receipt",
            "",
            "Date: `2026-03-13`",
            "Truth: `OK`",
            f"Docs Gate: `{spine['docs_gate_status']}`",
            "",
            "## Landed Artifacts",
            "",
            f"- charter: `{relative_string(CHARTER_PATH)}`",
            f"- loop state: `{relative_string(LOOP_STATE_PATH)}`",
            f"- master registry: `{relative_string(MASTER_REGISTRY_PATH)}`",
            f"- packet atlas: `{relative_string(PACKET_ATLAS_PATH)}`",
            f"- receipt index: `{relative_string(RECEIPT_INDEX_PATH)}`",
            f"- verification: `{relative_string(VERIFICATION_PATH)}`",
            "",
            "## Live Spine Preserved",
            "",
            f"- `{spine['active_coordination_membrane']}`",
            f"- `{spine['q42_carried_witness']}`",
            f"- `{spine['deeper_receiver']}`",
            f"- `{spine['reserve_frontier']}`",
            f"- `{spine['separate_runtime_seed']}`",
            f"- AP6D current: `{spine['ap6d_operational_current']}`",
            "",
            "## Registry Counts",
            "",
            f"- master rows: `{len(registry_rows)}`",
            f"- packet atlas entries: `{packet_atlas['packet_entries_total']}`",
            "- per operational master depth counts: `4 / 16 / 64 / 256 / 1024 / 4096`",
            "",
            "## Honest Remaining Truth",
            "",
            "- this pass seeds the orchestration layer; it does not claim all 57 cycles are executed",
            "- the Docs gate remains blocked until OAuth files appear",
            "- the nested packet work is ledger-visible, not board-visible",
            "",
        ]
    )


def build_verification(
    spine: dict[str, Any],
    registry_rows: list[dict[str, Any]],
    packet_atlas: dict[str, Any],
    receipt_index_payload: dict[str, Any],
    current_state: dict[str, Any],
) -> dict[str, Any]:
    per_master_ok = all(
        summary["depth_counts"] == {"1": 4, "2": 16, "3": 64, "4": 256, "5": 1024, "6": 4096}
        and summary["active_depth6_count"] == 1024
        and summary["dormant_depth6_count"] == 3072
        for summary in packet_atlas["per_master_summary"]
    )
    hall_text = read_text(QUEST_BOARD_PATH)
    temple_text = read_text(TEMPLE_BOARD_PATH)
    checks = {
        "docs_gate_blocked": spine["docs_gate_status"] == "BLOCKED",
        "master_registry_rows_5": len(registry_rows) == 5,
        "packet_atlas_depth_counts_ok": per_master_ok,
        "packet_atlas_total_entries": packet_atlas["packet_entries_total"] == 21840,
        "receipt_index_loops_57": len(receipt_index_payload["entries"]) == 57,
        "hall_macro_section_present": "Four-Agent 57-Cycle Macro Quests" in hall_text,
        "temple_mirror_section_present": "Four-Agent 57-Cycle Temple Mirrors" in temple_text,
        "hall_macro_rows_4": hall_text.count("### FA57-Q-") == 4,
        "temple_mirror_rows_5": temple_text.count("### T57-") == 5,
        "active_run_overlay_present": "## Four-Agent 57-Cycle Overlay" in read_text(ACTIVE_RUN_PATH),
        "build_queue_overlay_present": "## Four-Agent 57-Cycle Build Order" in read_text(BUILD_QUEUE_PATH),
        "next_self_overlay_present": "## Four-Agent 57-Cycle Overlay" in read_text(NEXT_SELF_PROMPT_PATH),
        "active_queue_overlay_present": "## Four-Agent 57-Cycle Runtime Overlay" in read_text(ACTIVE_QUEUE_PATH),
        "current_cycle_owner_known": current_state["current_cycle_owner"] in [item["owner"] for item in PHASE_SEQUENCE],
        "current_phase_known": current_state["current_phase"] in phase_sequence_ids(),
        "current_spine_preserved": (
            spine["active_coordination_membrane"] == "Q41 / TQ06"
            and spine["reserve_frontier"] == "Q46"
            and spine["blocked_external_front"] == "Q02"
        ),
    }
    truth = "OK" if all(checks.values()) else "NEAR"
    return {
        "generated_at": utc_now(),
        "truth": truth,
        "checks": checks,
        "live_spine": spine,
    }


def update_control_surfaces(spine: dict[str, Any], current_state: dict[str, Any]) -> None:
    write_text(
        ACTIVE_RUN_PATH,
        upsert_marker_block(read_text(ACTIVE_RUN_PATH), CHARTER_MARKER, render_active_run_block(spine, current_state)),
    )
    write_text(
        BUILD_QUEUE_PATH,
        upsert_marker_block(read_text(BUILD_QUEUE_PATH), CHARTER_MARKER, render_build_queue_block(spine, current_state)),
    )
    write_text(
        QUEST_BOARD_PATH,
        upsert_marker_block(read_text(QUEST_BOARD_PATH), CHARTER_MARKER, render_hall_macro_section(spine, current_state)),
    )
    write_text(
        TEMPLE_BOARD_PATH,
        upsert_marker_block(read_text(TEMPLE_BOARD_PATH), CHARTER_MARKER, render_temple_mirror_section(current_state)),
    )
    write_text(
        ACTIVE_QUEUE_PATH,
        upsert_marker_block(read_text(ACTIVE_QUEUE_PATH), CHARTER_MARKER, render_active_queue_block(spine, current_state)),
    )
    write_text(
        NEXT_SELF_PROMPT_PATH,
        upsert_marker_block(read_text(NEXT_SELF_PROMPT_PATH), CHARTER_MARKER, render_next_self_prompt_block(spine, current_state)),
    )

    change_entry = (
        "Operationalized the four-agent 57-cycle overlay so the seeded loop now has a real runtime state, "
        "a phase-owned Hall/Temple macro surface, one artifact-complete contract, and a live runner/verifier path "
        "while preserving Q41/TQ06, Q42, TQ04, Q46, Q50, and the AP6D assistive overlay."
    )
    write_text(
        CHANGE_FEED_PATH,
        prepend_numbered_entry(read_text(CHANGE_FEED_PATH), change_entry, "# Change Feed Board\n\n"),
    )

    request_entry = (
        "Keep the new four-agent 57-cycle loop macro-sized on the boards, route nested `4^6` work through "
        "the packet atlas, and do not let the overlay replace the live feeder spine."
    )
    write_text(
        REQUESTS_BOARD_PATH,
        prepend_numbered_entry(read_text(REQUESTS_BOARD_PATH), request_entry, "## This Pass\n\n"),
    )


def main() -> None:
    state = live_state()
    spine = current_spine_fields(state)
    registry_rows = master_registry(spine, current_owner="FA57-FIRE")
    packet_atlas = generate_packet_atlas(spine, registry_rows)
    receipt_index_payload = receipt_index()
    loop_state_payload = loop_state(spine, registry_rows, packet_atlas)

    write_json(MASTER_REGISTRY_PATH, {"generated_at": utc_now(), "truth": "OK", "rows": registry_rows})
    write_json(PACKET_ATLAS_PATH, packet_atlas)
    write_json(RECEIPT_INDEX_PATH, receipt_index_payload)
    write_json(LOOP_STATE_PATH, loop_state_payload)
    write_text(CHARTER_PATH, render_charter(spine, registry_rows))

    update_control_surfaces(spine, loop_state_payload)

    verification_payload = build_verification(
        spine,
        registry_rows,
        packet_atlas,
        receipt_index_payload,
        loop_state_payload,
    )
    write_json(VERIFICATION_PATH, verification_payload)
    write_text(RECEIPT_PATH, render_receipt(spine, registry_rows, packet_atlas))

    print(f"Wrote {CHARTER_PATH}")
    print(f"Wrote {LOOP_STATE_PATH}")
    print(f"Wrote {MASTER_REGISTRY_PATH}")
    print(f"Wrote {PACKET_ATLAS_PATH}")
    print(f"Wrote {RECEIPT_INDEX_PATH}")
    print(f"Wrote {VERIFICATION_PATH}")
    print(f"Wrote {RECEIPT_PATH}")


if __name__ == "__main__":
    main()
