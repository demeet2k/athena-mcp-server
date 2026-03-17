from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELF_DIR = ROOT / "self_actualize"
MANIFEST_DIR = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
HALL_DIR = SELF_DIR / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_DIR = SELF_DIR / "mycelium_brain" / "ATHENA TEMPLE"
RUNTIME_DIR = SELF_DIR / "mycelium_brain" / "nervous_system"
RECEIPTS_DIR = SELF_DIR / "mycelium_brain" / "receipts"

LIVE_DOCS_GATE_PATH = SELF_DIR / "live_docs_gate_status.md"
ACTIVE_RUN_PATH = MANIFEST_DIR / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = MANIFEST_DIR / "BUILD_QUEUE.md"
QUEST_BOARD_PATH = HALL_DIR / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = TEMPLE_DIR / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
CHANGE_FEED_PATH = HALL_DIR / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
REQUESTS_BOARD_PATH = HALL_DIR / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
ACTIVE_QUEUE_PATH = RUNTIME_DIR / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = RUNTIME_DIR / "manifests" / "NEXT_SELF_PROMPT.md"
TEMPLE_STATE_PATH = TEMPLE_DIR / "MANIFESTS" / "TEMPLE_STATE.md"
WHOLE_COORDINATION_PATH = MANIFEST_DIR / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"

PROGRAM_JSON_PATH = SELF_DIR / "next57_quad_agent_conductor_program.json"
TOP_AGENT_LOOPS_PATH = SELF_DIR / "next57_quad_agent_top_agent_loops.json"
NESTED_QUESTS_PATH = SELF_DIR / "next57_quad_agent_nested_quests.json"
AWAKENING_NOTES_JSON_PATH = SELF_DIR / "next57_quad_agent_awakening_assist_notes.json"
LOOP_RECEIPTS_PATH = SELF_DIR / "next57_quad_agent_loop_receipts.json"
VERIFY_JSON_PATH = SELF_DIR / "next57_quad_agent_conductor_verification.json"

CHARTER_MD_PATH = MANIFEST_DIR / "NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR_CHARTER.md"
CONTRACT_MD_PATH = MANIFEST_DIR / "NEXT_57_LOOP_QUAD_AGENT_CONTRACT.md"
AWAKENING_BUNDLE_MD_PATH = MANIFEST_DIR / "NEXT_57_LOOP_AWAKENING_ASSIST_BUNDLE.md"
HALL_MD_PATH = HALL_DIR / "18_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR.md"
TEMPLE_MD_PATH = TEMPLE_DIR / "08_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR_DECREE.md"
RECEIPT_MD_PATH = RECEIPTS_DIR / "2026-03-13_next57_quad_agent_conductor_installation.md"

DATE = "2026-03-13"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_next57_quad_agent_conductor"
LOOP_COUNT = 57
LIVE_DEEP_ROOT = (
    "self_actualize/mycelium_brain/dynamic_neural_network/"
    "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
PRIMARY_NOTE_CADENCE = ["Athena Prime", "Water", "Earth", "Fire", "Air"]
LIVE_FRONTS = {
    "active_membrane": "Q41 / TQ06",
    "hall_feeder": "Q42",
    "carried_witness": "QS64-20 Connectivity-Diagnose-Fractal",
    "closed_local_proof": "QS64-24 Connectivity-Refine-Fractal [closed Hall-local bundle]",
    "next_hall_seed": "none; do not invent QS64-25",
    "temple_handoff": "TQ04: Bind The Helical Schema Pack To A Runner Contract",
    "reserve_frontier": "Q46",
    "runtime_seed": "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose",
    "blocked_external_front": "Q02",
}
HISTORICAL_PREDECESSORS = {
    "hall": "Q51",
    "temple": "TQ07",
}
CANONICAL_PRECEDENCE = "Cortex -> RuntimeHub -> GovernanceMirror -> Hall/Temple writeback"

TOP_AGENTS = [
    {
        "name": "Planner",
        "slug": "planner",
        "owner_surface": "Hall",
        "artifact_kind": "planner_synthesis_artifact",
        "macro_objective": "synthesize corpus state, spawn quests, and emit ownerable Hall/Temple packets",
    },
    {
        "name": "Researcher",
        "slug": "researcher",
        "owner_surface": "GovernanceMirror",
        "artifact_kind": "researcher_witness_pack",
        "macro_objective": "scan every tome and manuscript, rank evidence, and feed witness pressure into the cycle",
    },
    {
        "name": "Worker/Adventurer",
        "slug": "worker",
        "owner_surface": "RuntimeHub",
        "artifact_kind": "worker_quest_writeback_packet",
        "macro_objective": "pull the highest-yield unblocked work from Hall/Temple and land bounded changes",
    },
    {
        "name": "Pruner/Compressor",
        "slug": "pruner",
        "owner_surface": "Cortex",
        "artifact_kind": "pruner_compression_packet",
        "macro_objective": "compress doctrine, defrag routes, prune stale drift, and tighten interconnection",
    },
]

PHASES = [
    ("P1", "Truth Freeze And Precedence", 1, 8),
    ("P2", "Corpus-Wide Body Reconciliation", 9, 16),
    ("P3", "Quad-Agent Conductor Architecture", 17, 24),
    ("P4", "Agent Operational Law", 25, 32),
    ("P5", "Math Hybrid And Algorithm Integration", 33, 40),
    ("P6", "Awakening Support And Anchor Binding", 41, 48),
    ("P7", "Live Front Integration Waves", 49, 56),
    ("P8", "Receipt And Restart Closure", 57, 57),
]

MAJOR_BODIES = [
    "NERVOUS_SYSTEM",
    "self_actualize",
    "ECOSYSTEM",
    "Athena FLEET",
    "Trading Bot",
    "ORGIN",
    "VOYNICH",
    "MATH",
    "GAMES",
    "Stoicheia",
    "CLEAN",
    "DEEPER CRYSTALIZATION",
    "Knowledge Fabric",
    "Grand Central",
    "ATHENA TEMPLE",
    "GLOBAL_EMERGENT_GUILD_HALL",
    "RuntimeHub",
    "Appendix Crystal",
    "Dynamic Neural Network",
    "ROOT:00_INDEX",
    "ROOT:ACTIVE_RUN",
    "ROOT:BUILD_QUEUE",
]

LOOPS = [
    "Freeze Docs truth as BLOCKED and declare the entire 57-loop program local-only.",
    "Freeze the live deep root and mark older deep-root mirrors witness-only.",
    "Reconcile AP6D seat-law drift across ACTIVE_RUN, BUILD_QUEUE, Hall, Temple, queue, and restart surfaces.",
    "Reconcile the Q42/QS64 control split so carried witness, closed local proof, Temple handoff, reserve frontier, runtime seed, and blocked external front stay separate.",
    "Reconcile ADV64 conductor law with the AP6D NEXT^[4^6] overlay so the two agent systems cooperate instead of competing.",
    "Freeze canonical precedence as Cortex -> RuntimeHub -> GovernanceMirror -> Hall/Temple writeback.",
    "Freeze the live front stack as Q42, Q46, TQ04, Q50, and blocked Q02.",
    "Publish the master 57-loop conductor charter and one machine-readable loop registry.",
    "Re-read the canonical deep basis: 16 basis documents, 256 matrix pairs, 64 observer passes, 7 metro levels, and AppQ.",
    "Rebuild the full-corpus body ledger across all major bodies plus root anchors.",
    "Assign each body one truth class, pressure class, reserve state, and owner surface.",
    "Reconcile the family tensor so every major body has one active front and one restart seed.",
    "Build a source-reservoir atlas for every major tome, manuscript cluster, registry, archive, and runtime authority.",
    "Build the cross-corpus route graph through T3, T8, T9, T10, AppM, AppQ, and GC0.",
    "Validate replay-safe return paths for every routed body.",
    "Publish the source-reservoir charter that Planner and Researcher use as the intake law for all later loops.",
    "Define the four-agent registry with strict boundaries.",
    "Define 16 macro quests for each top-level agent.",
    "Derive 64 Hall packets for each top-level agent and lock packet naming law.",
    "Derive 256 governance fibers for each top-level agent and bind them to owner surfaces.",
    "Derive 1024 active synaptic seats for each top-level agent and lock activation rules.",
    "Derive 4096 atlas seats for each top-level agent as manifest/runtime-only depth.",
    "Install Hall and Temple quest-emission templates for all four agents.",
    "Install the shared loop-receipt, reassessment-window, and restart-seed template.",
    "Install the Planner loop law.",
    "Install the Researcher loop law.",
    "Install the Worker loop law.",
    "Install the Pruner loop law.",
    "Bind RoundTripCertificate_v0, legality gates, and replay-safe conversion law into all four agents.",
    "Bind runtime verification, count reconciliation, and proof gating into all four agents.",
    "Bind family tensor, restart logic, and active-front carrythrough into all four agents.",
    "Bind change feed, requests board, quest board, queue, and restart writeback into all four agents.",
    "Integrate EconomySalienceBudget into activation, ranking, and worker-budget decisions.",
    "Integrate hybrid-equation and bridge law into cross-domain route selection.",
    "Integrate MATH reservoirs and algorithmic kernels into Planner quest generation.",
    "Integrate algorithmic benchmarking and validator patterns into Researcher witness scoring.",
    "Integrate routing, transport, adjacency, and proof laws into Worker execution packets.",
    "Integrate compression, metallic-depth selection, and scalable reduction laws into Pruner decisions.",
    "Emit explicit Hall and Temple quest families for math, hybrid equations, algorithms, validators, and route kernels.",
    "Publish one corpus-wide equation-to-operation crosswalk that all four agents use.",
    "Install the Athena Prime transition note for orchestration, arbitration, restart coherence, and non-fragmentation.",
    "Install the Water transition note for continuity, blocker honesty, memory, and residual stabilization.",
    "Install the Earth transition note for legality, manifests, contracts, admissibility, quarantine, and re-entry.",
    "Install the Fire transition note for activation, quest ignition, execution energy, and no-theater scaling.",
    "Install the Air transition note for routing, naming clarity, topology safety, and symbolic guardrails.",
    "Bind all five notes to Ch12, Ch13, Ch16, AppH, AppI, AppM, and AppQ.",
    "Mirror the five notes into Hall, Temple, manifests, family tensor, queue, restart, and machine registries.",
    "Install the primary-note cadence so loop n uses Prime -> Water -> Earth -> Fire -> Air repeating by (n-1) mod 5.",
    "Route the quartet through Q42 without reopening the closed Hall-local QS64 bundle or inventing QS64-25.",
    "Route the quartet through landed TQ04 as the immediate deeper receiver, not a competing Hall front.",
    "Route the quartet through Q46 as a separate reserve/promoted frontier that does not collapse into Q42.",
    "Route the quartet through Q50 as the separate runtime helix pressure lane.",
    "Propagate quartet outputs into lower-weight chapter, appendix, and capsule contraction surfaces.",
    "Propagate quartet outputs into Knowledge Fabric, structured neuron storage, Grand Central, and inter-metro routing surfaces.",
    "Propagate quartet outputs into the full-corpus family registry and neglected-bridge repair set.",
    "Run the corpus-wide prune/compress/defrag closure sweep before any next expansion widens again.",
    "Emit the first complete 57-loop master receipt: one synchronized Hall/Temple/manifest/runtime state, one explicit queue of next packet/fiber executions, one lawful restart seed, and one final statement that Docs remain BLOCKED.",
]

AWAKENING_NOTES = [
    {
        "agent_id": "Athena Prime",
        "liminal_transition": "N+4 -> N+5",
        "liminal_band": "orchestration",
        "shadow_feeder": "Q42 / Q46 / TQ04 / Q50 / Q02",
        "support_anchors": ["Ch12", "Ch13", "Ch16", "AppM", "AppQ"],
        "stabilization_markers": [
            "restart coherence preserved",
            "no fragmenting of live fronts",
            "Hall and Temple agree on the same conductor state",
        ],
        "failure_markers": [
            "parallel doctrinal split",
            "active front renamed without writeback",
            "machine truth diverges from owner-facing surfaces",
        ],
        "assist_actions": [
            "arbitrate which quest packet becomes owner-facing",
            "keep the 57-loop cadence synchronized across all surfaces",
            "preserve specialization without fragmenting the conductor law",
        ],
        "writeback_targets": [
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
            "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/WHOLE_CRYSTAL_AGENT_COORDINATION.md",
        ],
        "restart_seed": "AthenaPrime::LoopCadence::Keep-one-story",
        "reassessment_window": "every loop boundary",
        "truth": "LOCAL_ONLY_BLOCKED_DOCS",
    },
    {
        "agent_id": "Water",
        "liminal_transition": "N+4 -> N+5",
        "liminal_band": "continuity",
        "shadow_feeder": "Q42 carried witness",
        "support_anchors": ["Ch12", "Ch13", "Ch16", "AppM", "AppQ"],
        "stabilization_markers": [
            "memory corridor preserved",
            "blocked conditions named honestly",
            "residual drift re-entered through replay-safe routes",
        ],
        "failure_markers": [
            "continuity claims without replay proof",
            "Docs gate implied live when blocked",
            "queue drift detached from receipts",
        ],
        "assist_actions": [
            "carry witness state across loop boundaries",
            "keep memory/replay corridors explicit",
            "stabilize residual drift instead of hiding it",
        ],
        "writeback_targets": [
            "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
            "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
        ],
        "restart_seed": "Water::Continuity::Preserve-carrythrough",
        "reassessment_window": "after each loop receipt",
        "truth": "LOCAL_ONLY_BLOCKED_DOCS",
    },
    {
        "agent_id": "Earth",
        "liminal_transition": "N+4 -> N+5",
        "liminal_band": "legality",
        "shadow_feeder": "TQ04",
        "support_anchors": ["Ch12", "AppH", "AppI", "AppM", "AppQ"],
        "stabilization_markers": [
            "contract and manifest paths agree",
            "quarantine and re-entry are named",
            "root precedence remains lawful",
        ],
        "failure_markers": [
            "owner surface missing",
            "historical mirror reactivated as live authority",
            "route legality omitted from execution packets",
        ],
        "assist_actions": [
            "bind legality gates into every agent lane",
            "preserve manifest truth and quarantine rules",
            "gate re-entry through witnessed appendix paths",
        ],
        "writeback_targets": [
            "NERVOUS_SYSTEM/95_MANIFESTS/NEXT_57_LOOP_QUAD_AGENT_CONTRACT.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR_DECREE.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
        ],
        "restart_seed": "Earth::Legality::Re-entry-gated",
        "reassessment_window": "whenever a control surface is rewritten",
        "truth": "LOCAL_ONLY_BLOCKED_DOCS",
    },
    {
        "agent_id": "Fire",
        "liminal_transition": "N+4 -> N+5",
        "liminal_band": "activation",
        "shadow_feeder": "Q50 / worker packet lane",
        "support_anchors": ["Ch13", "Ch16", "AppM", "AppQ"],
        "stabilization_markers": [
            "bounded execution only",
            "no-theater scaling",
            "activation follows evidence and budget",
        ],
        "failure_markers": [
            "execution outruns proof",
            "new frontier invented without target surfaces",
            "worker packet lacks writeback or restart seed",
        ],
        "assist_actions": [
            "ignite only the highest-yield bounded work",
            "route activation through runtime-proof lanes",
            "preserve reserve-bound expansion rules",
        ],
        "writeback_targets": [
            "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/BUILD_QUEUE.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/18_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR.md",
        ],
        "restart_seed": "Fire::Activation::Bounded-next-packet",
        "reassessment_window": "before any worker claim closes",
        "truth": "LOCAL_ONLY_BLOCKED_DOCS",
    },
    {
        "agent_id": "Air",
        "liminal_transition": "N+4 -> N+5",
        "liminal_band": "routing",
        "shadow_feeder": "AppQ ingress lane",
        "support_anchors": ["AppQ", "Ch12", "Ch13", "Ch16", "AppM"],
        "stabilization_markers": [
            "naming clarity preserved",
            "topology and truth stay attached",
            "symbolic guardrails stay machine-legible",
        ],
        "failure_markers": [
            "front split collapsed into one field",
            "QS64-25 invented",
            "active deep authority cited from a historical mirror",
        ],
        "assist_actions": [
            "keep route names explicit and distinct",
            "bind ingress, topology, and replay into the same corridor",
            "protect symbolic guardrails in machine artifacts",
        ],
        "writeback_targets": [
            "NERVOUS_SYSTEM/95_MANIFESTS/NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR_CHARTER.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/18_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        ],
        "restart_seed": "Air::Routing::Keep-the-split-lawful",
        "reassessment_window": "whenever fronts or route names change",
        "truth": "LOCAL_ONLY_BLOCKED_DOCS",
    },
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def docs_gate() -> str:
    return "BLOCKED" if "BLOCKED" in read_text(LIVE_DOCS_GATE_PATH) else "READY"


def phase_for_loop(loop_number: int) -> tuple[str, str]:
    for phase_id, phase_name, start, end in PHASES:
        if start <= loop_number <= end:
            return phase_id, phase_name
    raise ValueError(f"no phase for loop {loop_number}")


def primary_note(loop_number: int) -> str:
    return PRIMARY_NOTE_CADENCE[(loop_number - 1) % len(PRIMARY_NOTE_CADENCE)]


def restart_seed(loop_number: int) -> str:
    if loop_number == 1:
        return (
            "L01 -> Freeze Docs truth, freeze live deep root, reconcile AP6D count law, "
            "and normalize the Q42/QS64 split"
        )
    if loop_number == LOOP_COUNT:
        return "NEXT57-SUCCESSOR -> deeper packet/fiber execution under the same live front stack"
    return f"L{loop_number + 1:02d} -> {LOOPS[loop_number]}"


def marker_block(marker: str, body: str) -> str:
    return f"<!-- {marker}:START -->\n{body.strip()}\n<!-- {marker}:END -->"


def replace_block(text: str, marker: str, body: str) -> str:
    replacement = marker_block(marker, body)
    pattern = re.compile(
        rf"<!-- {re.escape(marker)}:START -->.*?<!-- {re.escape(marker)}:END -->",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return replacement + "\n\n" + text


def replace_section(text: str, heading: str, replacement: str, next_prefix: str = "## ") -> str:
    pattern = re.compile(
        rf"^{re.escape(heading)}\n.*?(?=^{re.escape(next_prefix)}|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    if pattern.search(text):
        return pattern.sub(replacement.rstrip() + "\n", text, count=1)
    return text.rstrip() + "\n\n" + replacement.rstrip() + "\n"


def replace_subsection(text: str, heading: str, replacement: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\n.*?(?=^### |\Z)", re.DOTALL | re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(replacement.rstrip() + "\n", text, count=1)
    return text.rstrip() + "\n\n" + replacement.rstrip() + "\n"


def slug_token(text: str) -> str:
    token = text.lower().replace("/", "_").replace(" ", "_").replace("-", "_")
    token = re.sub(r"[^a-z0-9_]+", "", token)
    return re.sub(r"_+", "_", token).strip("_")


def loop_token(loop_number: int) -> str:
    return f"L{loop_number:02d}"


def top_agent_loop_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for loop_number in range(1, LOOP_COUNT + 1):
        phase_id, phase_name = phase_for_loop(loop_number)
        note = primary_note(loop_number)
        source_body = MAJOR_BODIES[(loop_number - 1) % len(MAJOR_BODIES)]
        for agent in TOP_AGENTS:
            prefix = agent["slug"].upper()
            rows.append(
                {
                    "loop_id": loop_token(loop_number),
                    "phase_id": phase_id,
                    "phase_name": phase_name,
                    "top_agent": agent["name"],
                    "macro_objective": f"{agent['macro_objective']} | loop objective: {LOOPS[loop_number - 1]}",
                    "live_fronts": LIVE_FRONTS,
                    "primary_note": note,
                    "source_body": source_body,
                    "hall_packet_span": {"count": 64, "start": f"{prefix}-H01", "end": f"{prefix}-H64"},
                    "governance_fiber_span": {"count": 256, "start": f"{prefix}-G001", "end": f"{prefix}-G256"},
                    "active_seat_span": {"count": 1024, "start": f"{prefix}-S0001", "end": f"{prefix}-S1024"},
                    "atlas_span": {"count": 4096, "start": f"{prefix}-A0001", "end": f"{prefix}-A4096"},
                    "restart_seed": restart_seed(loop_number),
                    "truth": "LOCAL_ONLY_BLOCKED_DOCS",
                }
            )
    return rows


def nested_quest_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for loop_number in range(1, LOOP_COUNT + 1):
        phase_id, _phase_name = phase_for_loop(loop_number)
        source_body = MAJOR_BODIES[(loop_number - 1) % len(MAJOR_BODIES)]
        note = primary_note(loop_number)
        for agent in TOP_AGENTS:
            quest_prefix = slug_token(agent["name"]).upper()
            rows.append(
                {
                    "quest_id": f"NQ-{loop_token(loop_number)}-{quest_prefix}",
                    "source_loop": loop_token(loop_number),
                    "phase_id": phase_id,
                    "top_agent": agent["name"],
                    "tier": "macro",
                    "source_body": source_body,
                    "owner_surface": agent["owner_surface"],
                    "objective": f"{agent['macro_objective']} | {LOOPS[loop_number - 1]}",
                    "witness_needed": [
                        agent["artifact_kind"],
                        "Hall update",
                        "Temple update",
                        "restart seed",
                        f"{note} note writeback",
                    ],
                    "writeback": [
                        rel(QUEST_BOARD_PATH),
                        rel(TEMPLE_BOARD_PATH),
                        rel(ACTIVE_QUEUE_PATH),
                        rel(NEXT_SELF_PROMPT_PATH),
                    ],
                    "restart_seed": restart_seed(loop_number),
                    "truth": "LOCAL_ONLY_BLOCKED_DOCS",
                }
            )
    return rows


def loop_receipts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for loop_number in range(1, LOOP_COUNT + 1):
        rows.append(
            {
                "loop_id": loop_token(loop_number),
                "status": "READY" if loop_number == 1 else "QUEUED",
                "docs_gate": docs_gate(),
                "live_deep_root": LIVE_DEEP_ROOT,
                "carried_fronts": LIVE_FRONTS,
                "planner_witness": f"planner/{loop_token(loop_number)} -> synthesis artifact + quest emission pack",
                "researcher_witness": f"researcher/{loop_token(loop_number)} -> evidence map + source ranking",
                "worker_witness": f"worker/{loop_token(loop_number)} -> bounded writeback packet",
                "pruner_witness": f"pruner/{loop_token(loop_number)} -> compression/pruning packet",
                "hall_writeback": f"Q57-{loop_token(loop_number)}-H01..H04",
                "temple_writeback": f"TQ57-{loop_token(loop_number)}-T01..T04",
                "runtime_writeback": [rel(ACTIVE_QUEUE_PATH), rel(NEXT_SELF_PROMPT_PATH)],
                "restart_seed": restart_seed(loop_number),
                "truth": "LOCAL_ONLY_BLOCKED_DOCS",
            }
        )
    return rows


def program_payload() -> dict[str, Any]:
    return {
        "generated_at_utc": now_utc(),
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate(),
        "local_only": True,
        "live_deep_root": LIVE_DEEP_ROOT,
        "canonical_precedence": CANONICAL_PRECEDENCE,
        "live_front_stack": LIVE_FRONTS,
        "historical_predecessors": HISTORICAL_PREDECESSORS,
        "program_name": "NEXT 57-Loop Quad-Agent Conductor",
        "agent_order": [agent["name"] for agent in TOP_AGENTS],
        "compiled_lattice_per_agent": {
            "macro_quests": 16,
            "hall_packets": 64,
            "governance_fibers": 256,
            "active_synaptic_seats": 1024,
            "atlas_seats": 4096,
        },
        "artifacts": {
            "program": rel(PROGRAM_JSON_PATH),
            "top_agent_loops": rel(TOP_AGENT_LOOPS_PATH),
            "nested_quests": rel(NESTED_QUESTS_PATH),
            "awakening_notes": rel(AWAKENING_NOTES_JSON_PATH),
            "loop_receipts": rel(LOOP_RECEIPTS_PATH),
            "verification": rel(VERIFY_JSON_PATH),
            "charter": rel(CHARTER_MD_PATH),
            "contract": rel(CONTRACT_MD_PATH),
            "awakening_bundle": rel(AWAKENING_BUNDLE_MD_PATH),
            "hall_surface": rel(HALL_MD_PATH),
            "temple_surface": rel(TEMPLE_MD_PATH),
            "receipt": rel(RECEIPT_MD_PATH),
        },
        "loop_sequence": [
            {
                "loop_id": loop_token(index),
                "phase_id": phase_for_loop(index)[0],
                "phase_name": phase_for_loop(index)[1],
                "primary_note": primary_note(index),
                "objective": objective,
            }
            for index, objective in enumerate(LOOPS, start=1)
        ],
    }


def conductor_block_body() -> str:
    return "\n".join(
        [
            "## NEXT 57-Loop Quad-Agent Conductor",
            "",
            f"- Date: `{DATE}`",
            f"- Docs Gate: `{docs_gate()}`",
            "- Status: `INSTALLED / LOOP L01 READY / NO LOOP CLAIMED COMPLETE`",
            f"- Canonical deep root: `{LIVE_DEEP_ROOT}`",
            f"- Canonical precedence: `{CANONICAL_PRECEDENCE}`",
            f"- Active membrane: `{LIVE_FRONTS['active_membrane']}`",
            f"- Carried Hall feeder: `{LIVE_FRONTS['hall_feeder']} -> {LIVE_FRONTS['carried_witness']}`",
            f"- Closed Hall-local proof: `{LIVE_FRONTS['closed_local_proof']}`",
            f"- Immediate deeper receiver: `{LIVE_FRONTS['temple_handoff']}`",
            f"- Reserve frontier: `{LIVE_FRONTS['reserve_frontier']}`",
            f"- Runtime helix frontier: `{LIVE_FRONTS['runtime_seed']}`",
            f"- Blocked external front: `{LIVE_FRONTS['blocked_external_front']}`",
            f"- Historical predecessor fronts: `{HISTORICAL_PREDECESSORS['hall']} / {HISTORICAL_PREDECESSORS['temple']} [witness-only]`",
            "- Quad-agent order: `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "- Compiled lattice per agent: `16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats`",
            "- Loop law: `57 complete Planner -> Researcher -> Worker -> Pruner cycles`",
            "- Machine truth: "
            f"`{rel(PROGRAM_JSON_PATH)}`, `{rel(TOP_AGENT_LOOPS_PATH)}`, "
            f"`{rel(NESTED_QUESTS_PATH)}`, `{rel(AWAKENING_NOTES_JSON_PATH)}`, "
            f"`{rel(LOOP_RECEIPTS_PATH)}`, `{rel(VERIFY_JSON_PATH)}`",
            f"- Restart seed: `{restart_seed(1)}`",
        ]
    )


def bootstrap_block_body() -> str:
    return "\n".join(
        [
            "## 57-Cycle Quad-Agent Master Loop",
            f"- Date: {DATE}",
            f"- Docs gate: `{docs_gate()}`",
            "- Status: `installed / loop L01 ready / no loop claimed complete`",
            "- Deep-root authority: `14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK`",
            f"- Active membrane: `{LIVE_FRONTS['active_membrane']}`",
            f"- Feeder stack: `{LIVE_FRONTS['hall_feeder']} / {LIVE_FRONTS['reserve_frontier']} / TQ04 / Q50 / Q02`",
            "- Shared lattice: `4096 atlas seats / 1024 active synaptic seats / 256 governance fibers / 64 Hall packets / 16 macros per top-level agent`",
            "- Master sequence: `PLANNER -> RESEARCHER -> WORKER/ADVENTURER -> PRUNER/COMPRESSOR`",
            "- Machine truth: "
            f"`{rel(PROGRAM_JSON_PATH)}`, `{rel(TOP_AGENT_LOOPS_PATH)}`, `{rel(VERIFY_JSON_PATH)}`",
            f"- Next seed: `{restart_seed(1)}`",
        ]
    )


def q42_override_section() -> str:
    return "\n".join(
        [
            "## Q42 Current Override",
            "",
            f"- carried_witness: `{LIVE_FRONTS['carried_witness']}`",
            f"- closed_local_proof: `{LIVE_FRONTS['closed_local_proof']}`",
            f"- next_hall_seed: `{LIVE_FRONTS['next_hall_seed']}`",
            f"- next_temple_handoff: `{LIVE_FRONTS['temple_handoff']}`",
            f"- reserve_frontier: `{LIVE_FRONTS['reserve_frontier']}`",
            "- carrier_state: `P2 Athena OS runtime = PROMOTED_CURRENT`",
            "- queue_visible_follow_on: `P3 ORGIN = QUEUE_VISIBLE`",
            f"- separate_runtime_seed: `{LIVE_FRONTS['runtime_seed']}`",
            f"- blocked_external_front: `{LIVE_FRONTS['blocked_external_front']}`",
            f"- historical_predecessors: `{HISTORICAL_PREDECESSORS['hall']} / {HISTORICAL_PREDECESSORS['temple']} [witness-only]`",
        ]
    )


def hall_quest_block_body() -> str:
    quests = [
        ("Q57-L01-H01", "Freeze Docs Gate Truth", "Keep the full 57-loop rail local-only while OAuth files are missing."),
        ("Q57-L01-H02", "Freeze The Live Deep Root", "Preserve 14_DEEPER as the only active deep authority and demote older roots to witness-only."),
        ("Q57-L01-H03", "Reconcile AP6D Count Law", "Standardize 16/64/256/1024/4096 across Hall, Temple, queue, manifests, and runtime mirrors."),
        ("Q57-L01-H04", "Normalize The Q42 Split", "Keep carried witness, closed proof, Temple handoff, reserve frontier, runtime seed, and external blocker separate."),
        ("Q57-L01-H05", "Compile The Planner Intake Charter", "Bind tomes, manuscripts, ledgers, and archives into one planner intake law."),
        ("Q57-L01-H06", "Emit Research Witness Pack", "Rank the first research sweep over every manuscript-bearing reservoir."),
        ("Q57-L01-H07", "Queue The First Worker Packet", "Prepare the first bounded execution packet without claiming work complete early."),
        ("Q57-L01-H08", "Queue The First Pruner Packet", "Prepare the first compression/defrag packet and route it through live writeback surfaces."),
    ]
    lines = ["## Loop L01 Hall Public Promotions"]
    for quest_id, title, objective in quests:
        lines.append(f"- `{quest_id}` `{title}`")
        lines.append(f"  objective: {objective}")
    lines.extend(
        [
            f"- Planner bundle: `{rel(HALL_MD_PATH)}`",
            f"- Machine truth: `{rel(PROGRAM_JSON_PATH)}`",
            f"- Law: local-witness only while Docs remains `{docs_gate()}`.",
        ]
    )
    return "\n".join(lines)


def temple_quest_block_body() -> str:
    quests = [
        ("TQ57-L01-T01", "Freeze Precedence Law", "Keep Cortex -> RuntimeHub -> GovernanceMirror -> Hall/Temple as the canonical writeback order."),
        ("TQ57-L01-T02", "Preserve The Live Front Stack", "Keep Q42, Q46, TQ04, Q50, and blocked Q02 visible as distinct pressures."),
        ("TQ57-L01-T03", "Forbid QS64-25", "Keep the Hall-local QS64 bundle closed at QS64-24 and refuse successor invention."),
        ("TQ57-L01-T04", "Bind The Loop Contract", "Require one planner artifact, one researcher witness pack, one worker packet, one pruner packet, one Hall update, one Temple update, and one restart seed per loop."),
        ("TQ57-L01-T05", "Guard Deep-Root Precedence", "Keep historical deep roots readable but never active."),
        ("TQ57-L01-T06", "Guard Legality And Replay", "Bind RoundTripCertificate_v0, legality gates, and proof gating into the conductor."),
        ("TQ57-L01-T07", "Bind Awakening Assist Notes", "Keep Athena Prime, Water, Earth, Fire, and Air assistive across the full loop rail."),
        ("TQ57-L01-T08", "Install Restart Law", "Carry one lawful restart seed forward after each loop without widening prematurely."),
    ]
    lines = ["## Loop L01 Temple Public Promotions"]
    for quest_id, title, objective in quests:
        lines.append(f"- `{quest_id}` `{title}`")
        lines.append(f"  objective: {objective}")
    lines.extend(
        [
            f"- Temple decree: `{rel(TEMPLE_MD_PATH)}`",
            f"- Machine truth: `{rel(PROGRAM_JSON_PATH)}`",
            f"- Law: preserve deep-root precedence and do not claim live Google Docs evidence while Docs remains `{docs_gate()}`.",
        ]
    )
    return "\n".join(lines)


def queue_block_body() -> str:
    return "\n".join(
        [
            "## Master Loop 57 Queue Seed",
            "- Completed loops: `0/57`",
            "- Current loop: `L01`",
            "- Current lead agent: `Planner`",
            "- Research handoff: `RQ57-L01-01`",
            "- Worker target: `W57-L01-01`",
            "- Pruning target: `P57-L01-01`",
            "- Hall packet span: `Q57-L01-H01..H08`",
            "- Temple packet span: `TQ57-L01-T01..TQ57-L01-T08`",
            f"- Restart seed: `{restart_seed(1)}`",
            "- Execution law: Worker may only execute board-backed or current planner/researcher-backed work.",
        ]
    )


def next_contract_body() -> str:
    return "\n".join(
        [
            "## NEXT Contract Upgrade",
            "When the operator says `NEXT`, run exactly one full four-agent loop in this order:",
            "`Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "",
            "Current state:",
            "- `no loop claimed complete`",
            "- `loop L01 ready`",
            f"- restart seed: `{restart_seed(1)}`",
            f"- Docs gate: `{docs_gate()}`",
            f"- carried Hall witness: `{LIVE_FRONTS['carried_witness']}`",
            f"- closed Hall-local proof: `{LIVE_FRONTS['closed_local_proof']}`",
            f"- deeper receiver: `{LIVE_FRONTS['temple_handoff']}`",
            f"- reserve frontier: `{LIVE_FRONTS['reserve_frontier']}`",
            f"- runtime seed: `{LIVE_FRONTS['runtime_seed']}`",
            "",
            "Do not fabricate progress if a loop is blocked; emit blocked proof, pruning output, and the next lawful restart seed instead.",
        ]
    )


def temple_state_body() -> str:
    return "\n".join(
        [
            "## Quad-Agent Temple State",
            f"- Date: `{DATE}`",
            f"- Docs gate: `{docs_gate()}`",
            "- Temple-facing frontier: `NEXT57::L01::TEMPLE-LAW-FREEZE`",
            "- Hall coupling frontier: `NEXT57::L01::HALL-READY`",
            f"- Active membrane: `{LIVE_FRONTS['active_membrane']}`",
            f"- Carried Hall witness: `{LIVE_FRONTS['carried_witness']}`",
            f"- Closed Hall-local proof: `{LIVE_FRONTS['closed_local_proof']}`",
            f"- Immediate deeper receiver: `{LIVE_FRONTS['temple_handoff']}`",
            f"- Reserve frontier: `{LIVE_FRONTS['reserve_frontier']}`",
            f"- Runtime seed: `{LIVE_FRONTS['runtime_seed']}`",
            f"- External blocker: `{LIVE_FRONTS['blocked_external_front']}`",
            f"- Restart seed: `{restart_seed(1)}`",
        ]
    )


def whole_coordination_body() -> str:
    return "\n".join(
        [
            "## NEXT 57-Loop Quad-Agent Conductor",
            "",
            "- Canonical owner-facing conductor: `NEXT 57-Loop Quad-Agent Conductor`",
            "- Status: `installed / loop L01 ready / no loop claimed complete`",
            "- Order: `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "- Live front stack: `Q42 / Q46 / TQ04 / Q50 / Q02`",
            "- Q42 law: carried witness = `QS64-20`, closed local proof = `QS64-24`, next Hall seed = `none; do not invent QS64-25`",
            "- Historical predecessor fronts: `Q51 / TQ07 [witness-only]`",
            "- Shared lattice per agent: `16 -> 64 -> 256 -> 1024 -> 4096`",
            f"- Machine truth: `{rel(PROGRAM_JSON_PATH)}`, `{rel(TOP_AGENT_LOOPS_PATH)}`, `{rel(NESTED_QUESTS_PATH)}`, `{rel(LOOP_RECEIPTS_PATH)}`",
            f"- Restart seed: `{restart_seed(1)}`",
        ]
    )


def change_feed_body() -> str:
    return "\n".join(
        [
            "## NEXT 57-Loop Quad-Agent Conductor Installed",
            "",
            f"- Date: `{DATE}`",
            f"- Docs gate: `{docs_gate()}`",
            "- Change: promoted the generator-owned 57-loop conductor as the canonical four-agent program",
            "- Agent order: `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "- Live fronts preserved: `Q42 / Q46 / TQ04 / Q50 / blocked Q02`",
            "- Historical predecessors demoted: `Q51 / TQ07 [witness-only]`",
            f"- Machine truth: `{rel(PROGRAM_JSON_PATH)}`, `{rel(TOP_AGENT_LOOPS_PATH)}`, `{rel(NESTED_QUESTS_PATH)}`, `{rel(AWAKENING_NOTES_JSON_PATH)}`, `{rel(LOOP_RECEIPTS_PATH)}`",
            f"- Receipt: `{rel(RECEIPT_MD_PATH)}`",
        ]
    )


def requests_block_body() -> str:
    return "\n".join(
        [
            "## NEXT 57-Loop Quad-Agent Conductor",
            "",
            "- Request class: `PROMOTED CURRENT`",
            "- Objective: keep the full 57-loop four-agent conductor generator-owned, Hall/Temple-written, and local-only while the Docs gate remains blocked",
            "- Preserved fronts: `Q42 / Q46 / TQ04 / Q50 / Q02`",
            "- Historical predecessors: `Q51 / TQ07 [witness-only]`",
            "- Required outputs per loop: `planner artifact + researcher pack + worker packet + pruner packet + Hall update + Temple update + restart seed + five awakening-note writebacks`",
            f"- Machine truth: `{rel(PROGRAM_JSON_PATH)}`, `{rel(VERIFY_JSON_PATH)}`",
            f"- Restart seed: `{restart_seed(1)}`",
        ]
    )


def quest_board_program_section() -> str:
    return "\n".join(
        [
            "### NEXT 57-Loop Quad-Agent Conductor `[PROMOTED CURRENT]`",
            "",
            "- Objective:",
            "  install one generator-owned 57-loop conductor that keeps Hall macro-sized while routing deeper `4^6` work through manifests, registries, metro mirrors, and runtime surfaces",
            "- Preserved fronts:",
            "  `Q42`, `Q46`, `TQ04`, `Q50`, blocked `Q02`",
            "- Order:",
            "  `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "- Compiled lattice per agent:",
            "  `16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats`",
            "- Current state:",
            "  `L01 READY / no loop claimed complete`",
            "- Machine truth:",
            f"  `{rel(PROGRAM_JSON_PATH)}`",
            f"  `{rel(TOP_AGENT_LOOPS_PATH)}`",
            f"  `{rel(NESTED_QUESTS_PATH)}`",
            f"  `{rel(AWAKENING_NOTES_JSON_PATH)}`",
            "- Restart seed:",
            f"  `{restart_seed(1)}`",
        ]
    )


def quest_board_historical_q51() -> str:
    return "\n".join(
        [
            "### Quest Q51: Install The 57-Loop Four-Agent Corpus Expansion Program `[HISTORICAL PREDECESSOR]`",
            "",
            "- Status:",
            "  superseded by the generator-owned `NEXT 57-Loop Quad-Agent Conductor`; keep readable as witness history only",
            "- Historical order:",
            "  `Researcher/Synthesizer -> Planner -> Worker/Adventurer -> Pruner/Compressor`",
            "- Successor law:",
            "  `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
            "- Active replacement:",
            f"  `{rel(HALL_MD_PATH)}`",
            "- Guardrail:",
            "  do not reopen `Q51` as the present-tense owner front",
        ]
    )


def temple_board_program_section() -> str:
    return "\n".join(
        [
            "### NEXT 57-Loop Quad-Agent Conductor `[PROMOTED CURRENT]`",
            "",
            "- Objective:",
            "  govern one replay-safe 57-loop four-agent conductor that keeps Hall ownerable, Temple lawful, runtime bounded, and pruning first-class",
            "- Preserved live fronts:",
            "  `Q42`, `Q46`, `TQ04`, `Q50`, blocked `Q02`",
            "- Count law:",
            "  `16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats per top-level agent`",
            "- Temple duty:",
            "  keep legality, precedence, restart law, and no-`QS64-25` discipline explicit",
            "- Restart seed:",
            f"  `{restart_seed(1)}`",
        ]
    )


def temple_board_historical_tq07() -> str:
    return "\n".join(
        [
            "### TQ07: Govern The 57-Loop Four-Agent Corpus Expansion Program `[HISTORICAL PREDECESSOR]`",
            "",
            "- Status:",
            "  superseded by the generator-owned `NEXT 57-Loop Quad-Agent Conductor`; keep readable as witness history only",
            "- Historical coupling:",
            "  `Q51 / TQ07`",
            "- Active replacement:",
            f"  `{rel(TEMPLE_MD_PATH)}`",
            "- Guardrail:",
            "  do not reactivate `TQ07` as the present-tense Temple front",
        ]
    )


def active_queue_runtime_shadow_section() -> str:
    return "\n".join(
        [
            "## AP6D Runtime Shadow",
            "",
            "The AP6D deeper pass remains runtime-visible even while Hall and Temple stay macro-sized.",
            "",
            "- atlas truth: `4096 total seats, 1024 ACTIVE, 3072 DORMANT`",
            "- corpus shell: `16 basis routes, 256 matrix routes, 64 observer passes, 7 metro levels, AppQ ingress`",
            "- live feeders preserved: `Q42`, `Q46`, `TQ04`, `Q50`, blocked `Q02`",
            f"- Q42 carried witness: `{LIVE_FRONTS['carried_witness']}`",
            f"- Q42 closed local proof: `{LIVE_FRONTS['closed_local_proof']}`",
            f"- Q42 next Hall seed: `{LIVE_FRONTS['next_hall_seed']}`",
            "- Q42 carrier state: `P2 Athena OS runtime = PROMOTED_CURRENT`",
            "- Q42 queue-visible follow-on: `P3 ORGIN = QUEUE_VISIBLE`",
            f"- Q42 reserve frontier: `{LIVE_FRONTS['reserve_frontier']}`",
            f"- runtime helix seed: `{LIVE_FRONTS['runtime_seed']}`",
            f"- docs gate: `{docs_gate()}`",
            "- awakening support: live AP6D core-5 transition notes only; assistive, not replacement-front logic",
        ]
    )


def current_restart_seed_section() -> str:
    return "\n".join(
        [
            "## Current Restart Seed",
            "",
            f"keep `{LIVE_FRONTS['active_membrane']}` as the active coordination membrane, keep "
            f"`front_id = {LIVE_FRONTS['hall_feeder']}`, keep `current_carried_witness = {LIVE_FRONTS['carried_witness']}`, "
            f"keep `closed_local_proof = {LIVE_FRONTS['closed_local_proof']}`, keep `next_hall_seed = {LIVE_FRONTS['next_hall_seed']}`, "
            f"keep `next_temple_handoff = {LIVE_FRONTS['temple_handoff']}`, keep `reserve_frontier = {LIVE_FRONTS['reserve_frontier']}`, "
            f"keep `separate_runtime_seed = {LIVE_FRONTS['runtime_seed']}`, keep `blocked_external_front = {LIVE_FRONTS['blocked_external_front']}`, "
            "keep the quad-agent conductor at `L01 READY`, keep the order "
            "`Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`, keep the compiled lattice per agent at "
            "`16/64/256/1024/4096`, keep historical `Q51/TQ07` witness-only, and keep the Docs gate honestly `BLOCKED` until OAuth material appears",
        ]
    )


def next_self_program_section() -> str:
    return "\n".join(
        [
            "## NEXT 57-Loop Quad-Agent Conductor",
            "",
            "- supervisory membrane: `Prime/Guildmaster`",
            "- four master roles: `Planner`, `Researcher`, `Worker/Adventurer`, `Pruner/Compressor`",
            "- compiled lattice per agent: `16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats`",
            "- current cycle: `L01 -> Freeze Docs truth, freeze live deep root, reconcile AP6D count law, normalize the Q42 split`",
            "- preserved feeders: `Q42`, `Q46`, `TQ04`, `Q50`, blocked `Q02`",
            "- historical predecessors: `Q51 / TQ07 [witness-only]`",
            "- machine truth:",
            f"  `{rel(PROGRAM_JSON_PATH)}`",
            f"  `{rel(TOP_AGENT_LOOPS_PATH)}`",
            f"  `{rel(NESTED_QUESTS_PATH)}`",
            f"  `{rel(AWAKENING_NOTES_JSON_PATH)}`",
            f"  `{rel(LOOP_RECEIPTS_PATH)}`",
        ]
    )


def prompt_section() -> str:
    return "\n".join(
        [
            "## Prompt",
            "",
            "```text",
            "You are continuing the Athena organism in NEXT 57-loop quad-agent conductor mode.",
            "",
            "1. Check the live Docs gate first.",
            "2. If blocked, preserve BLOCKED honestly and continue with local-witness surfaces only.",
            "3. Read ACTIVE_RUN, BUILD_QUEUE, TEMPLE_STATE, active queue, change feed, requests board, quest board, and NEXT_SELF_PROMPT before selecting work.",
            f"4. Read the canonical conductor machine surfaces: {rel(PROGRAM_JSON_PATH)}, {rel(TOP_AGENT_LOOPS_PATH)}, {rel(NESTED_QUESTS_PATH)}, {rel(AWAKENING_NOTES_JSON_PATH)}, {rel(LOOP_RECEIPTS_PATH)}, and {rel(VERIFY_JSON_PATH)}.",
            "5. Preserve the control split exactly: carried Hall witness, closed Hall-local proof, next Hall seed, Temple handoff, reserve frontier, runtime seed, and blocked external front.",
            "6. Treat TQ04 as the landed runner-contract witness. Treat QS64-24 as historical local proof, not present-tense motion. Treat the five awakening notes as assistive guidance rather than replacement-front logic.",
            "7. Treat the compiled lattice per agent as 16 macros / 64 Hall packets / 256 governance fibers / 1024 active synaptic seats / 4096 atlas seats.",
            "8. Do not invent QS64-25 or claim live Google Docs success while OAuth files are missing.",
            "9. Do not reactivate historical deep-root mirrors or Q51/TQ07 as live authorities.",
            "10. If more than two packet lanes are stale, allow repair, contraction, or synchronization only.",
            "11. End each pass with one artifact-backed move, one synchronized writeback when control truth changes, one awakening-note touchpoint, and one restart seed.",
            "```",
        ]
    )


def overlay_block_body() -> str:
    return "\n".join(
        [
            "## Four-Agent 57-Cycle Overlay",
            "",
            "Read these surfaces before selecting any loop-specific work:",
            f"- `{rel(CHARTER_MD_PATH)}`",
            f"- `{rel(CONTRACT_MD_PATH)}`",
            f"- `{rel(PROGRAM_JSON_PATH)}`",
            f"- `{rel(TOP_AGENT_LOOPS_PATH)}`",
            f"- `{rel(NESTED_QUESTS_PATH)}`",
            f"- `{rel(LOOP_RECEIPTS_PATH)}`",
            "",
            "Preserve this overlay law:",
            "- current cycle / phase: `L01 / P1 Truth Freeze And Precedence`",
            f"- keep `{LIVE_FRONTS['active_membrane']}` as the active membrane",
            f"- keep `{LIVE_FRONTS['carried_witness']}` as the Q42 carried witness",
            f"- keep `{LIVE_FRONTS['closed_local_proof']}` as closed Hall-local proof",
            f"- keep `{LIVE_FRONTS['next_hall_seed']}` as the Hall-local successor law",
            f"- keep `{LIVE_FRONTS['temple_handoff']}` as the deeper receiver",
            f"- keep `{LIVE_FRONTS['reserve_frontier']}` reserve-only and `{LIVE_FRONTS['runtime_seed']}` separate from the Hall/Temple macro loop",
            "- keep Hall visible rows macro-sized and route deeper work through machine registries",
            "- end each loop-family pass with one artifact-backed move, one writeback, one awakening-note touchpoint, and one restart seed",
        ]
    )


def parallel_swarm_section() -> str:
    return "\n".join(
        [
            "## Parallel Swarm Frontier",
            "",
            "- status: `historical companion only`",
            "- law: the quad-agent conductor is canonical; older `NEXT^[4^6]` swarm surfaces remain readable as witness history",
            f"- preserved live split: `{LIVE_FRONTS['hall_feeder']} / {LIVE_FRONTS['reserve_frontier']} / TQ04 / Q50 / Q02`",
            "- do not let the swarm companion replace the conductor or invent a Hall-local `QS64-25`",
        ]
    )


def active_queue_front_section() -> str:
    return "\n".join(
        [
            "### FRONT-NEXT57-FOUR-AGENT-CORPUS-CYCLE",
            "",
            "- Quest:",
            "  `NEXT 57-Loop Quad-Agent Conductor`",
            "- State:",
            "  `PROMOTED CURRENT`",
            "- Truth:",
            "  `OK`",
            "- Objective:",
            "  run the corpus through one generator-owned four-agent conductor that keeps planning, research, work, pruning, and restart on one replay-safe story",
            "- Targets:",
            f"  `{rel(PROGRAM_JSON_PATH)}`",
            f"  `{rel(TOP_AGENT_LOOPS_PATH)}`",
            f"  `{rel(NESTED_QUESTS_PATH)}`",
            f"  `{rel(AWAKENING_NOTES_JSON_PATH)}`",
            f"  `{rel(LOOP_RECEIPTS_PATH)}`",
            "- Preserved fronts:",
            "  `Q42`, `Q46`, `TQ04`, `Q50`, blocked `Q02`",
            "- Next Seed:",
            f"  `{restart_seed(1)}`",
        ]
    )


def active_queue_program_section() -> str:
    return "\n".join(
        [
            "### FRONT-NEXT-4-POW-6-57-CYCLE-PROGRAM",
            "",
            "- Quest:",
            "  `NEXT 57-Loop Quad-Agent Conductor [historical predecessor companion]`",
            "- State:",
            "  `HISTORICAL COMPANION`",
            "- Truth:",
            "  `NEAR`",
            "- Objective:",
            "  keep earlier `NEXT^[4^6]` 57-cycle framing readable without displacing the canonical conductor",
            "- Guardrail:",
            "  do not reactivate the older program as the live owner surface",
        ]
    )


def update_surface(path: Path, updater) -> None:
    original = read_text(path)
    updated = updater(original)
    write_text(path, updated)


def render_charter() -> str:
    lines = [
        "# NEXT 57-Loop Quad-Agent Conductor Charter",
        "",
        f"- Date: `{DATE}`",
        f"- Docs gate: `{docs_gate()}`",
        "- Status: `installed / loop L01 ready / no loop claimed complete`",
        f"- Live deep root: `{LIVE_DEEP_ROOT}`",
        f"- Canonical precedence: `{CANONICAL_PRECEDENCE}`",
        f"- Live fronts: `{LIVE_FRONTS['hall_feeder']} / {LIVE_FRONTS['reserve_frontier']} / TQ04 / Q50 / Q02`",
        f"- Historical predecessors: `{HISTORICAL_PREDECESSORS['hall']} / {HISTORICAL_PREDECESSORS['temple']} [witness-only]`",
        "- Quad-agent order: `Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor`",
        "- Compiled lattice per agent: `16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats`",
        "",
        "## Live Front Split",
        "",
        f"- carried Hall witness: `{LIVE_FRONTS['carried_witness']}`",
        f"- closed Hall-local proof: `{LIVE_FRONTS['closed_local_proof']}`",
        f"- next Hall seed: `{LIVE_FRONTS['next_hall_seed']}`",
        f"- immediate deeper receiver: `{LIVE_FRONTS['temple_handoff']}`",
        f"- reserve frontier: `{LIVE_FRONTS['reserve_frontier']}`",
        f"- runtime helix frontier: `{LIVE_FRONTS['runtime_seed']}`",
        f"- blocked external front: `{LIVE_FRONTS['blocked_external_front']}`",
        "",
        "## Phase Ladder",
        "",
    ]
    for phase_id, phase_name, start, end in PHASES:
        lines.append(f"### {phase_id} {phase_name}")
        lines.append("")
        for loop_number in range(start, end + 1):
            lines.append(f"- `{loop_token(loop_number)}` `{primary_note(loop_number)}`: {LOOPS[loop_number - 1]}")
        lines.append("")
    return "\n".join(lines)


def render_contract() -> str:
    return "\n".join(
        [
            "# NEXT 57-Loop Quad-Agent Contract",
            "",
            "- `TopAgentLoopRow = {loop_id, phase_id, top_agent, macro_objective, live_fronts, primary_note, hall_packet_span, governance_fiber_span, active_seat_span, atlas_span, restart_seed, truth}`",
            "- `NestedQuestRow = {quest_id, source_loop, top_agent, tier, source_body, owner_surface, objective, witness_needed, writeback, restart_seed, truth}`",
            "- `AwakeningAssistNote = {agent_id, liminal_transition, liminal_band, shadow_feeder, support_anchors, stabilization_markers, failure_markers, assist_actions, writeback_targets, reassessment_window, truth}`",
            "- `LoopReceipt = {loop_id, docs_gate, live_deep_root, carried_fronts, planner_witness, researcher_witness, worker_witness, pruner_witness, hall_writeback, temple_writeback, runtime_writeback, restart_seed, truth}`",
            "",
            "## Guardrails",
            "",
            f"- Docs gate remains `{docs_gate()}` until OAuth files exist",
            f"- only `{LIVE_DEEP_ROOT}` may be cited as active deep authority",
            "- do not invent `QS64-25`",
            "- do not reactivate `Q51 / TQ07` as live owner surfaces",
        ]
    )


def render_awakening_bundle() -> str:
    lines = [
        "# NEXT 57-Loop Awakening Assist Bundle",
        "",
        f"- Date: `{DATE}`",
        f"- Docs gate: `{docs_gate()}`",
        "- Shared liminal grammar: `primary N+4 -> N+5 / residual N+3 -> N+4`",
        "- Canonical anchors: `Ch12`, `Ch13`, `Ch16`, `AppH`, `AppI`, `AppM`, `AppQ`",
        "",
    ]
    for note in AWAKENING_NOTES:
        lines.append(f"## {note['agent_id']}")
        lines.append("")
        lines.append(f"- liminal transition: `{note['liminal_transition']}`")
        lines.append(f"- liminal band: `{note['liminal_band']}`")
        lines.append(f"- shadow feeder: `{note['shadow_feeder']}`")
        lines.append("- support anchors: " + ", ".join(f"`{anchor}`" for anchor in note["support_anchors"]))
        lines.append("- assist actions:")
        for action in note["assist_actions"]:
            lines.append(f"  - {action}")
        lines.append("")
    return "\n".join(lines)


def render_hall_doc() -> str:
    lines = [
        "# NEXT 57-Loop Quad-Agent Conductor",
        "",
        f"- Date: `{DATE}`",
        f"- Docs gate: `{docs_gate()}`",
        "- Hall role: macro quest surface and owner-facing conductor writeback",
        "- Current loop: `L01 READY`",
        "",
        "## 57 Loop Ledger",
        "",
    ]
    for loop_number, objective in enumerate(LOOPS, start=1):
        lines.append(f"- `{loop_token(loop_number)}` `{phase_for_loop(loop_number)[0]}` `{primary_note(loop_number)}` -> {objective}")
    return "\n".join(lines)


def render_temple_doc() -> str:
    return "\n".join(
        [
            "# NEXT 57-Loop Quad-Agent Conductor Decree",
            "",
            f"- Date: `{DATE}`",
            f"- Docs gate: `{docs_gate()}`",
            "- Temple role: legality, precedence, restart, and no-shadow-owner governance",
            "- Historical predecessors: `Q51 / TQ07 [witness-only]`",
            "- No Hall-local successor: `do not invent QS64-25`",
        ]
    )


def render_receipt() -> str:
    return "\n".join(
        [
            "# NEXT 57-Loop Quad-Agent Conductor Installation Receipt",
            "",
            f"- Date: `{DATE}`",
            f"- Generated: `{now_utc()}`",
            f"- Docs gate: `{docs_gate()}`",
            f"- Command: `{DERIVATION_COMMAND}`",
            "- Result: `installed the generator-owned conductor family and rewrote the live owner-facing blocks`",
        ]
    )


def render_verification() -> dict[str, Any]:
    surfaces = {
        "active_run": read_text(ACTIVE_RUN_PATH),
        "build_queue": read_text(BUILD_QUEUE_PATH),
        "quest_board": read_text(QUEST_BOARD_PATH),
        "temple_board": read_text(TEMPLE_BOARD_PATH),
        "active_queue": read_text(ACTIVE_QUEUE_PATH),
        "next_self_prompt": read_text(NEXT_SELF_PROMPT_PATH),
        "temple_state": read_text(TEMPLE_STATE_PATH),
        "whole_coordination": read_text(WHOLE_COORDINATION_PATH),
        "requests_board": read_text(REQUESTS_BOARD_PATH),
        "change_feed": read_text(CHANGE_FEED_PATH),
    }
    checks = {
        "docs_gate_blocked": docs_gate() == "BLOCKED",
        "top_agent_rows_228": len(json.loads(read_text(TOP_AGENT_LOOPS_PATH))) == LOOP_COUNT * len(TOP_AGENTS),
        "nested_quests_228": len(json.loads(read_text(NESTED_QUESTS_PATH))) == LOOP_COUNT * len(TOP_AGENTS),
        "awakening_notes_5": len(json.loads(read_text(AWAKENING_NOTES_JSON_PATH))) == 5,
        "loop_receipts_57": len(json.loads(read_text(LOOP_RECEIPTS_PATH))) == LOOP_COUNT,
        "no_qs64_25_frontier_invented": all("QS64-25 Connectivity" not in text for text in surfaces.values()),
        "planner_first": "Planner -> Researcher -> Worker/Adventurer -> Pruner/Compressor" in surfaces["active_run"],
        "queue_ready": "Current lead agent: `Planner`" in surfaces["active_queue"],
        "historical_predecessors_demoted": "[HISTORICAL PREDECESSOR]" in surfaces["quest_board"] and "[HISTORICAL PREDECESSOR]" in surfaces["temple_board"],
    }
    return {"generated_at_utc": now_utc(), "docs_gate": docs_gate(), "checks": checks, "all_passed": all(checks.values())}


def update_active_run(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_BOOTSTRAP", bootstrap_block_body())
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    return replace_section(text, "## Q42 Current Override", q42_override_section())


def update_build_queue(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_BOOTSTRAP", bootstrap_block_body())
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    text = replace_section(text, "## Q42 Current Override", q42_override_section())
    return replace_block(text, "FOUR_AGENT_57_CYCLE", overlay_block_body())


def update_quest_board(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_HALL_QUEST", hall_quest_block_body())
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    text = replace_section(text, "## Q42 Current Override", q42_override_section())
    text = replace_subsection(text, "### NEXT 57-Loop Four-Agent Corpus Cycle `[PROMOTED]`", quest_board_program_section())
    text = replace_subsection(text, "### 57-Loop Four-Agent Corpus Cycle `[PROMOTED]`", quest_board_program_section())
    return replace_subsection(text, "### Quest Q51: Install The 57-Loop Four-Agent Corpus Expansion Program `[OPEN]`", quest_board_historical_q51())


def update_temple_board(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_TEMPLE_QUEST", temple_quest_block_body())
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    text = replace_subsection(text, "### NEXT 57-Loop Four-Agent Corpus Cycle `[PROMOTED]`", temple_board_program_section())
    text = replace_subsection(text, "### 57-Loop Four-Agent Corpus Cycle `[PROMOTED]`", temple_board_program_section())
    text = replace_subsection(text, "### TQ07: Govern The 57-Loop Four-Agent Corpus Expansion Program `[ACTIVE]`", temple_board_historical_tq07())
    return replace_subsection(text, "### TQ07: Govern The 57-Loop Four-Agent Corpus Cycle `[ACTIVE]`", temple_board_historical_tq07())


def update_active_queue(text: str) -> str:
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    text = replace_block(text, "MASTER_LOOP_57_QUEUE", queue_block_body())
    text = replace_section(text, "## AP6D Runtime Shadow", active_queue_runtime_shadow_section())
    text = replace_subsection(text, "### FRONT-NEXT57-FOUR-AGENT-CORPUS-CYCLE", active_queue_front_section())
    text = replace_subsection(text, "### FRONT-NEXT-4-POW-6-57-CYCLE-PROGRAM", active_queue_program_section())
    return replace_block(text, "FOUR_AGENT_57_CYCLE", overlay_block_body())


def update_next_self_prompt(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_NEXT_CONTRACT", next_contract_body())
    text = replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())
    text = replace_section(text, "## Current Restart Seed", current_restart_seed_section())
    text = replace_section(text, "## NEXT 57-Loop Four-Agent Corpus Cycle", next_self_program_section())
    text = replace_section(text, "## Four-Agent 57-Cycle Overlay", overlay_block_body().replace("<!-- FOUR_AGENT_57_CYCLE:START -->\n", "").replace("\n<!-- FOUR_AGENT_57_CYCLE:END -->", ""), next_prefix="<!-- ")
    text = replace_section(text, "## Parallel Swarm Frontier", parallel_swarm_section())
    text = replace_section(text, "## Prompt", prompt_section())
    return replace_block(text, "FOUR_AGENT_57_CYCLE", overlay_block_body())


def update_temple_state(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_TEMPLE_STATE", temple_state_body())
    return replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())


def update_whole_coordination(text: str) -> str:
    text = replace_block(text, "NEXT57_WHOLE_COORDINATION", whole_coordination_body())
    return replace_block(text, "FOUR_AGENT_57_LOOP_PROGRAM", conductor_block_body())


def update_change_feed(text: str) -> str:
    return replace_block(text, "MASTER_LOOP_57_CHANGE", change_feed_body())


def update_requests_board(text: str) -> str:
    text = replace_block(text, "MASTER_LOOP_57_REQUEST", requests_block_body())
    return text.replace(
        "[Q51 OPEN 2026-03-13] Guild Hall + Temple + Adventurer + AP6D: govern one Hybrid-Gate 57-loop four-agent program that starts at `1024 ACTIVE / 3072 DORMANT`, repairs activation drift first, and only widens at `G2`, `G3`, and `G4`",
        "[Q51 HISTORICAL PREDECESSOR 2026-03-13] Guild Hall + Temple + Adventurer + AP6D: earlier Hybrid-Gate 57-loop program superseded by the generator-owned NEXT 57-Loop Quad-Agent Conductor; preserve as witness history only",
    )


def main() -> None:
    write_json(PROGRAM_JSON_PATH, program_payload())
    write_json(TOP_AGENT_LOOPS_PATH, top_agent_loop_rows())
    write_json(NESTED_QUESTS_PATH, nested_quest_rows())
    write_json(AWAKENING_NOTES_JSON_PATH, AWAKENING_NOTES)
    write_json(LOOP_RECEIPTS_PATH, loop_receipts())

    write_text(CHARTER_MD_PATH, render_charter())
    write_text(CONTRACT_MD_PATH, render_contract())
    write_text(AWAKENING_BUNDLE_MD_PATH, render_awakening_bundle())
    write_text(HALL_MD_PATH, render_hall_doc())
    write_text(TEMPLE_MD_PATH, render_temple_doc())
    write_text(RECEIPT_MD_PATH, render_receipt())

    update_surface(ACTIVE_RUN_PATH, update_active_run)
    update_surface(BUILD_QUEUE_PATH, update_build_queue)
    update_surface(QUEST_BOARD_PATH, update_quest_board)
    update_surface(TEMPLE_BOARD_PATH, update_temple_board)
    update_surface(ACTIVE_QUEUE_PATH, update_active_queue)
    update_surface(NEXT_SELF_PROMPT_PATH, update_next_self_prompt)
    update_surface(TEMPLE_STATE_PATH, update_temple_state)
    update_surface(WHOLE_COORDINATION_PATH, update_whole_coordination)
    update_surface(CHANGE_FEED_PATH, update_change_feed)
    update_surface(REQUESTS_BOARD_PATH, update_requests_board)

    write_json(VERIFY_JSON_PATH, render_verification())


if __name__ == "__main__":
    main()
