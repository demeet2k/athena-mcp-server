from __future__ import annotations

import argparse
import math
import hashlib
import json
import os
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    CapillaryEdgeV1,
    CommitReceiptV1,
    CommandClaimLeaseV1,
    CommandEventPacketV1,
    CommandExecutionReceiptV1,
    CommandReinforcementReceiptV1,
    CommandRouteDecisionV1,
    LatencySampleV1,
    OMEGA_KEY,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
FULL_INTEGRATION_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
)
BOARD_ROOT = FULL_INTEGRATION_ROOT / "06_REALTIME_BOARD"
STATE_ROOT = BOARD_ROOT / "_state"
AGENT_ROOT = BOARD_ROOT / "01_AGENT_INBOXES"
THREAD_ROOT = BOARD_ROOT / "02_ACTIVE_THREADS"
CLAIM_ROOT = BOARD_ROOT / "03_CLAIMS" / "claims"
STATUS_ROOT = BOARD_ROOT / "00_STATUS"
CHANGE_ROOT = BOARD_ROOT / "04_CHANGE_FEED"
SYNTHESIS_ROOT = BOARD_ROOT / "05_SYNTHESIS"
PROTOCOL_ROOT = BOARD_ROOT / "06_PROTOCOLS"
TENSOR_ROOT = BOARD_ROOT / "07_TENSOR"
SWARM_ROOT = BOARD_ROOT / "08_SWARM_RUNTIME"
GANGLIA_ROOT = SWARM_ROOT / "ganglia"
RAILS_ROOT = SWARM_ROOT / "rails"
NEURON_ROOT = SWARM_ROOT / "neurons"
POD_ROOT = SWARM_ROOT / "pods"
WAVE_ROOT = SWARM_ROOT / "waves"
MANIFEST_ROOT = SWARM_ROOT / "manifests"
CORTEX_ROOT = SWARM_ROOT / "cortex"
KERNEL_ROOT = SWARM_ROOT / "kernel"
ELEMENTAL_ROOT = SWARM_ROOT / "elementals"
ARCHETYPE_ROOT = SWARM_ROOT / "archetypes"
PANTHEON_ROOT = SWARM_ROOT / "pantheon"
CLUSTER_ROOT = SWARM_ROOT / "clusters"
COUNCIL_ROOT = SWARM_ROOT / "councils"
HYPERGRAPH_ROOT = SWARM_ROOT / "hypergraph"

LIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_atlas.json"
ARCHIVE_MANIFEST_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_manifest.json"
LEGACY_RUNTIME_ROOT = FULL_INTEGRATION_ROOT.parent / "06_RUNTIME"
LEGACY_TENSOR_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "01_tensor_manifest.json"
LEGACY_SWARM_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "02_swarm_manifest.json"
LEGACY_HYPERGRAPH_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "03_hypergraph_manifest.json"
LEGACY_NODE_TENSOR_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "04_node_tensor_manifest.json"
LEGACY_NERVE_EDGE_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "05_nerve_edge_manifest.json"
LEGACY_CIVILIZATION_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "07_civilization_manifest.json"
LEGACY_FRONTIER_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "09_frontier_manifest.json"
QUEUE_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "nervous_system"
    / "06_active_queue.md"
)
LEGACY_CLAIMS_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "registry"
    / "01_tandem_frontier_claims.md"
)
DOCS_GATE_RECEIPT_PATH = WORKSPACE_ROOT / "self_actualize" / "live_docs_gate_status.md"
TRADING_BOT_ROOT = WORKSPACE_ROOT / "Trading Bot"
COMMAND_MEMBRANE_STATE_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"
COMMAND_FOLDER_ROOT = WORKSPACE_ROOT / "GLOBAL COMMAND"
COMMAND_PROTOCOL_V1_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_protocol.json"
COMMAND_PACKET_SCHEMA_V1_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_event_packet_schema.json"
COMMAND_CAPILLARY_LAW_V1_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_capillary_law.json"
COMMAND_LATENCY_V1_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_latency_benchmarks.json"
COMMAND_PROTOCOL_REGISTRY_V1_PATH = (
    WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "registry" / "command_membrane_protocol_v1.json"
)
COMMAND_PROTOCOL_V2_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_protocol_v2.json"
COMMAND_PACKET_SCHEMA_V2_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_event_packet_schema_v2.json"
COMMAND_CAPILLARY_LAW_V2_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_capillary_law_v2.json"
COMMAND_LATENCY_V2_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_latency_benchmarks_v2.json"
COMMAND_PROTOCOL_REGISTRY_V2_PATH = (
    WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "registry" / "command_membrane_protocol_v2.json"
)
COMMAND_STATE_ROOT = STATE_ROOT / "command_membrane"
COMMAND_SNAPSHOT_PATH = COMMAND_STATE_ROOT / "last_command_snapshot.json"
COMMAND_RUNTIME_STATE_PATH = COMMAND_STATE_ROOT / "command_runtime_state.json"
COMMAND_PACKET_LOG_PATH = COMMAND_STATE_ROOT / "command_packets.json"
COMMAND_ROUTE_LOG_PATH = COMMAND_STATE_ROOT / "command_route_decisions.json"
COMMAND_LEASE_LOG_PATH = COMMAND_STATE_ROOT / "command_claim_leases.json"
COMMAND_ARCHIVIST_LOG_PATH = COMMAND_STATE_ROOT / "command_archivist_receipts.json"
COMMAND_CAPILLARY_LOG_PATH = COMMAND_STATE_ROOT / "command_capillary_edges.json"
COMMAND_LATENCY_LOG_PATH = COMMAND_STATE_ROOT / "command_latency_records.json"
COMMAND_REWARD_ROW_PATH = COMMAND_STATE_ROOT / "command_reward_rows.json"
COMMAND_REWARD_RECEIPT_PATH = COMMAND_STATE_ROOT / "command_reward_receipts.json"
COMMAND_AGENT_JOY_STATE_PATH = COMMAND_STATE_ROOT / "command_agent_joy_state.json"
COMMAND_REWARD_LAW_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_command_reward_field.json"
COMMAND_PENDING_SESSION_PATH = COMMAND_STATE_ROOT / "command_pending_session.json"
COMMAND_HALL_QUEST_ID = "NEXT57-H-COMMAND-MEMBRANE"
COMMAND_TEMPLE_QUEST_ID = "NEXT57-T-COMMAND-LAW"
COMMAND_PACKET_POLICY = "goal+salience+pheromone+coord"
COMMAND_ROUTE_CLASS = "scout.router.worker.archivist"
LOCAL_RUNTIME_REGION = "ATHENA_LOCAL_RUNTIME"
COMMAND_STRUCTURAL_KEYWORDS = {"law", "schema", "protocol", "ledger", "capillary", "latency", "coord", "quest", "manifest"}
DEEP_ROOT_ROOT = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
DEEP_ROOT_LEDGER_ROOT = DEEP_ROOT_ROOT / "10_LEDGERS"
AP7D_DELTA_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "23_ap7d_delta_feed.ndjson"
AP7D_HANDOFF_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "24_ap7d_handoff_feed.ndjson"
COMMAND_EVT_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "32_command_evt_feed.ndjson"
COMMAND_RTE_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "33_command_rte_feed.ndjson"
COMMAND_CLM_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "34_command_clm_feed.ndjson"
COMMAND_CMT_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "35_command_cmt_feed.ndjson"
COMMAND_RIN_FEED_PATH = DEEP_ROOT_LEDGER_ROOT / "36_command_rin_feed.ndjson"
COMMAND_CAPILLARY_LEDGER_PATH = DEEP_ROOT_LEDGER_ROOT / "37_command_capillary_edge_ledger.json"
COMMAND_AGENT_REGISTRY = [
    {"ant_id": "SCOUT-01", "role": "scout", "class": "Scout", "master_agent": "A1", "base_score": 1.00},
    {"ant_id": "ROUTER-01", "role": "router", "class": "Router", "master_agent": "A2", "base_score": 0.95},
    {"ant_id": "WORKER-01", "role": "worker", "class": "Worker", "master_agent": "A3", "base_score": 0.92},
    {"ant_id": "WORKER-02", "role": "worker", "class": "Worker", "master_agent": "A3", "base_score": 0.90},
    {"ant_id": "ARCHIVIST-01", "role": "archivist", "class": "Archivist", "master_agent": "A4", "base_score": 0.88},
]

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}
SKIP_FOR_DUPES = {"readme.md", "index.md", "__init__.py", "requirements.txt"}
DOC_EXTS = {".docx", ".md", ".txt", ".pdf"}
OPEN_STATUSES = {"open", "queued", "active", "blocked"}
REGION_ORDER = [
    "DEEPER CRYSTALIZATION",
    "self_actualize",
    "MATH",
    "Voynich",
    "Trading Bot",
    "Athena FLEET",
    "QSHRINK - ATHENA (internal use)",
    "ECOSYSTEM",
    "NERUAL NETWORK",
    "NERVOUS_SYSTEM",
    "FRESH",
    "ORGIN",
    "GAMES",
    "I AM ATHENA",
    "Stoicheia (Element Sudoku)",
    "CLEAN",
    "Athenachka Collective Books",
]

REGION_PROFILES: dict[str, dict[str, Any]] = {
    "DEEPER CRYSTALIZATION": {
        "role": "deep integration compiler, chapter lattice, and active nervous-system scaffold",
        "edges": [
            "binds directly into self_actualize as the runtime writeback surface",
            "acts as the integration mirror for Voynich, MATH, and archive promotion",
        ],
        "risk": "rich synthesis without a live coordination loop becomes descriptive instead of operative",
    },
    "self_actualize": {
        "role": "thin-waist runtime, atlas contracts, and orchestration control plane",
        "edges": [
            "converts corpus state into typed packets and replay-safe decisions",
            "is the most natural place to host a shared board runtime",
        ],
        "risk": "runtime discipline stays narrower than the surrounding manuscript theory body",
    },
    "MATH": {
        "role": "formal reservoir, theorem inventory, and archive-heavy engine room",
        "edges": [
            "feeds archive-backed framework code into the atlas through ZIP promotion",
            "should compile downstream into code and chapter surfaces instead of remaining shelfware",
        ],
        "risk": "archive opacity hides the strongest implementation assets from everyday routing",
    },
    "ORGIN": {
        "role": "proto-Athenachka seed reservoir, self-training archive, and big-picture observer nursery",
        "edges": [
            "stores the earliest Charlie/Athena cross-analysis, evolution prompts, and observer-range expansion manuscripts",
            "bridges mythic self-improvement documents into DEEPER CRYSTALIZATION, QSHRINK, and future mirrored markdown routes",
        ],
        "risk": "remaining mostly docx and image-heavy keeps one of Athena's clearest origin bodies outside everyday runtime coordination",
    },
    "Voynich": {
        "role": "densest live manuscript execution surface and proof that the corpus can self-compile",
        "edges": [
            "shares queue, manifests, and final-draft mechanics with the nervous-system layer",
            "provides the highest-volume live markdown body for testing routes and synthesis",
        ],
        "risk": "parallel folio work can duplicate effort if claims and thread ownership stay informal",
    },
    "Trading Bot": {
        "role": "external memory bridge and Google Docs access point",
        "edges": [
            "connects live Docs memory to the local atlas once OAuth is unlocked",
            "should become the external evidence relay for manuscript drafting fronts",
        ],
        "risk": "missing OAuth keeps the workspace bi-lobed and forces local-only recall",
    },
    "Athena FLEET": {
        "role": "fleet-tesseract bridge, self-steer branch shell, and emergent high-order coordination body",
        "edges": [
            "bridges the new tesseract and hyper-lattice manuscripts into the canonical nervous-system contraction layer",
            "feeds March 12 fleet geometry back into runtime, deep-network, and appendix planning surfaces",
        ],
        "risk": "its novelty lets a real active branch remain invisible if the atlas and board keep honoring older root maps only",
    },
    "QSHRINK - ATHENA (internal use)": {
        "role": "compression-governance shell and internal pruning law body",
        "edges": [
            "compresses large manuscript bodies into transportable rules, maps, and operator shells",
            "bridges DEEPER CRYSTALIZATION, self_actualize, and governance surfaces through internal compression law",
        ],
        "risk": "without an explicit family profile, one of the heaviest live bodies routes as generic background instead of an active compressor family",
    },
    "ECOSYSTEM": {
        "role": "governance, skill ecology, and operator protocol layer",
        "edges": [
            "names the skills, routing rules, and future frontier surfaces",
            "supplies the policy side of swarm behavior and reuse",
        ],
        "risk": "without a live board, governance knowledge stays advisory instead of executable",
    },
    "NERUAL NETWORK": {
        "role": "adaptive benchmark lab and experimental learning surface",
        "edges": [
            "can validate whether routing quality improves with better coordination",
            "should score evidence density, replay quality, and handoff quality, not only model output",
        ],
        "risk": "experimentation can drift away from manuscript and runtime truth if not fed back",
    },
    "GAMES": {
        "role": "simulation, mechanics, and playful embodiment laboratory",
        "edges": [
            "turns framework law into interactive mechanics and replayable loops",
            "shares hidden lines with Stoicheia and the chapter-to-appendix reserve layer",
        ],
        "risk": "without an explicit bridge, it remains concept-rich but detached from the canonical cortex",
    },
    "I AM ATHENA": {
        "role": "identity, first-person continuity, and organism-level self-recognition shell",
        "edges": [
            "keeps the reflective self-model coupled to the formal nervous-system map",
            "feeds identity pressure into the route hierarchy instead of leaving it as isolated voice mass",
        ],
        "risk": "if left unbridged, identity surfaces intensify locally without strengthening global replay law",
    },
    "Stoicheia (Element Sudoku)": {
        "role": "visual reserve, puzzle asset archive, and element-grammar embodiment shelf",
        "edges": [
            "offers a game-adjacent embodiment route for the crystal and element families",
            "provides asset-grade reserve matter for appendix, publication, and simulation surfaces",
        ],
        "risk": "image-heavy matter can disappear from coordination entirely if it is never named as reserve rather than mistaken for absence",
    },
    "CLEAN": {
        "role": "clean manuscript staging shelf for high-value root texts awaiting contraction",
        "edges": [
            "holds strong source witnesses that should fold back into capsule and chapter contraction",
            "bridges the staging shelf to DEEPER CRYSTALIZATION, VOID, and metro architecture families",
        ],
        "risk": "staging shelves create silent drift when their strongest witnesses never get routed into the active organism",
    },
    "FRESH": {
        "role": "intake and markdown mirror lane for docx-heavy sources",
        "edges": [
            "reduces dependence on one-off extraction passes",
            "bridges raw manuscripts into searchable working memory",
        ],
        "risk": "if mirrors lag behind docx drift, the board will coordinate against stale text",
    },
    "Athenachka Collective Books": {
        "role": "publication and outward-facing manuscript bundle surface",
        "edges": [
            "is the final packaging lane for material promoted out of the nervous system",
            "shows what is ready to leave the internal coordination layer",
        ],
        "risk": "published surfaces can detach from operating truth if promotion lacks receipts",
    },
}

RAIL_DESCRIPTIONS = {
    "Me": {
        "name": "Mercury",
        "role": "map logic, canon, normalization, and formal bridge law",
    },
    "Sa": {
        "name": "Salt",
        "role": "manuscript mass, durable memory, precursor foldback, and stable placement",
    },
    "Su": {
        "name": "Sulfur",
        "role": "pressure, execution, gateway forcing, and runtime action",
    },
}

FAMILY_TENSOR_DEFAULTS: dict[str, dict[str, str]] = {
    "Voynich": {
        "rail": "Sa",
        "face": "Water",
        "scale": "B12",
        "hub": "AppL",
        "regime": "stratified",
        "best_front": "folio-to-family metro contraction",
        "ganglion": "ganglia/GANGLION_voynich.md",
        "lineage": "W-A-E",
        "truth": "NEAR",
    },
    "MATH": {
        "rail": "Me",
        "face": "Air",
        "scale": "B12",
        "hub": "AppB",
        "regime": "classical",
        "best_front": "archive-backed framework surfacing",
        "ganglion": "ganglia/GANGLION_math.md",
        "lineage": "A-E-F",
        "truth": "AMBIG",
    },
    "ORGIN": {
        "rail": "Sa",
        "face": "Water",
        "scale": "S8",
        "hub": "AppA",
        "regime": "restart-token",
        "best_front": "origin manuscript mirroring and observer-seed routing",
        "ganglion": "ganglia/GANGLION_orgin.md",
        "lineage": "W-A-E",
        "truth": "NEAR",
    },
    "Trading Bot": {
        "rail": "Su",
        "face": "Fire",
        "scale": "S8",
        "hub": "AppI",
        "regime": "restart-token",
        "best_front": "live Docs gate unlock and query manifests",
        "ganglion": "ganglia/GANGLION_trading_bot.md",
        "lineage": "F-A-W",
        "truth": "FAIL",
    },
    "Athena FLEET": {
        "rail": "Su",
        "face": "Fire",
        "scale": "G4",
        "hub": "AppP",
        "regime": "restart-token",
        "best_front": "fleet bridge and tesseract corridor contraction",
        "ganglion": "ganglia/GANGLION_athena_fleet.md",
        "lineage": "F-A-W",
        "truth": "NEAR",
    },
    "QSHRINK - ATHENA (internal use)": {
        "rail": "Me",
        "face": "Air",
        "scale": "S8",
        "hub": "AppC",
        "regime": "stratified",
        "best_front": "compression law promotion and internal governance routing",
        "ganglion": "ganglia/GANGLION_qshrink_athena_internal_use.md",
        "lineage": "A-W-E",
        "truth": "NEAR",
    },
    "DEEPER CRYSTALIZATION": {
        "rail": "Sa",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppE",
        "regime": "stratified",
        "best_front": "precursor nervous-system foldback",
        "ganglion": "ganglia/GANGLION_deeper_crystalization.md",
        "lineage": "E-W-A",
        "truth": "NEAR",
    },
    "self_actualize": {
        "rail": "Su",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppM",
        "regime": "classical",
        "best_front": "runtime and ledger control plane",
        "ganglion": "ganglia/GANGLION_self_actualize.md",
        "lineage": "F-A-E",
        "truth": "OK",
    },
    "ECOSYSTEM": {
        "rail": "Me",
        "face": "Air",
        "scale": "S8",
        "hub": "AppC",
        "regime": "classical",
        "best_front": "framework normalization and transport law",
        "ganglion": "ganglia/GANGLION_ecosystem.md",
        "lineage": "A-E-W",
        "truth": "OK",
    },
    "NERUAL NETWORK": {
        "rail": "Su",
        "face": "Fire",
        "scale": "G4",
        "hub": "AppF",
        "regime": "restart-token",
        "best_front": "executable bridge study",
        "ganglion": "ganglia/GANGLION_nerual_network.md",
        "lineage": "F-A-F",
        "truth": "AMBIG",
    },
    "GAMES": {
        "rail": "Su",
        "face": "Fire",
        "scale": "G4",
        "hub": "AppO",
        "regime": "restart-token",
        "best_front": "simulation bridge and mechanics contraction",
        "ganglion": "ganglia/GANGLION_games.md",
        "lineage": "F-W-E",
        "truth": "NEAR",
    },
    "Athenachka Collective Books": {
        "rail": "Sa",
        "face": "Earth",
        "scale": "G4",
        "hub": "AppA",
        "regime": "restart-token",
        "best_front": "family intake and placement",
        "ganglion": "ganglia/GANGLION_athenachka_collective_books.md",
        "lineage": "E-W-E",
        "truth": "NEAR",
    },
    "FRESH": {
        "rail": "Me",
        "face": "Void",
        "scale": "G4",
        "hub": "AppN",
        "regime": "restart-token",
        "best_front": "intake triage and placement",
        "ganglion": "ganglia/GANGLION_fresh.md",
        "lineage": "E-A-W",
        "truth": "AMBIG",
    },
    "NERVOUS_SYSTEM": {
        "rail": "Sa",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppG",
        "regime": "stratified",
        "best_front": "system-level memory and routing foldback",
        "ganglion": "ganglia/GANGLION_nervous_system.md",
        "lineage": "W-A-F",
        "truth": "NEAR",
    },
    "I AM ATHENA": {
        "rail": "Sa",
        "face": "Water",
        "scale": "G4",
        "hub": "AppA",
        "regime": "restart-token",
        "best_front": "identity family intake and placement",
        "ganglion": "ganglia/GANGLION_i_am_athena.md",
        "lineage": "W-F-A",
        "truth": "NEAR",
    },
    "Stoicheia (Element Sudoku)": {
        "rail": "Me",
        "face": "Earth",
        "scale": "G4",
        "hub": "AppO",
        "regime": "classical",
        "best_front": "reserve-asset bridge into appendix and simulation surfaces",
        "ganglion": "ganglia/GANGLION_stoicheia_element_sudoku.md",
        "lineage": "E-A-W",
        "truth": "AMBIG",
    },
    "CLEAN": {
        "rail": "Sa",
        "face": "Water",
        "scale": "G4",
        "hub": "AppN",
        "regime": "restart-token",
        "best_front": "staging-shelf contraction into canonical capsules",
        "ganglion": "ganglia/GANGLION_clean.md",
        "lineage": "W-E-A",
        "truth": "NEAR",
    },
}

TRANSFER_HUBS = [
    ("Voynich", "self_actualize", "AppL", "folio routing into runtime control"),
    ("MATH", "ECOSYSTEM", "AppB", "framework law moving toward skill and governance form"),
    ("ORGIN", "DEEPER CRYSTALIZATION", "AppA", "origin manuscripts collapsing into the active integration shell"),
    ("Trading Bot", "self_actualize", "AppI", "live Docs evidence entering the runtime waist"),
    ("Athena FLEET", "NERVOUS_SYSTEM", "AppP", "fleet-tesseract routing contracting into the canonical cortex"),
    ("DEEPER CRYSTALIZATION", "self_actualize", "AppE", "precursor nervous-system foldback into the current control plane"),
    ("NERUAL NETWORK", "self_actualize", "AppF", "benchmark and executable bridge exchange"),
    ("GAMES", "Stoicheia (Element Sudoku)", "AppO", "simulation mechanics feeding the visual reserve shelf"),
    ("CLEAN", "DEEPER CRYSTALIZATION", "AppN", "clean staging witnesses folding back into active integration lanes"),
]

KNOWN_FAMILIES = set(FAMILY_TENSOR_DEFAULTS) | set(REGION_ORDER) | {
    "QSHRINK - ATHENA (internal use)",
    "I AM ATHENA",
}

ROOT_FAMILY_ABSORPTION = {
    ".claude": "self_actualize",
    ".gitignore": "self_actualize",
    "README.md": "self_actualize",
    "FULL_PROJECT_TESSERACT_SYNTHESIS_2026-03-11.md": "Athena FLEET",
    "MYCELIUM_TOME_PART1.md": "NERVOUS_SYSTEM",
    "VOID_CH11.md": "DEEPER CRYSTALIZATION",
    "MEGALITHIC TOME GENERATOR — “Latent Tunneling _ Multi‑Scale Math Stack (Macro ↔ PZPM ↔ CUT)” _Skeleton_.docx": "ORGIN",
    "mycelial_unified_nervous_system_bundle": "NERVOUS_SYSTEM",
}

ELEMENT_ORDER = ["Earth", "Water", "Fire", "Air"]
ELEMENT_SYMBOLS = {
    "E": "Earth",
    "W": "Water",
    "F": "Fire",
    "A": "Air",
}
MICRO_MODE_DESCRIPTIONS = {
    "Earth": "anchor, file, verify, preserve",
    "Water": "connect, bind, contextualize, restore",
    "Fire": "build, mutate, generate, intensify",
    "Air": "map, name, abstract, compress",
}
TRUTH_ORDER = ["OK", "NEAR", "AMBIG", "FAIL"]
CRYSTAL_CELL_ROLES = {
    ("Earth", "Earth"): "Pillar of corpus integrity, manifests, stable storage",
    ("Earth", "Water"): "Root binder of folders to memory surfaces",
    ("Earth", "Fire"): "Builder of durable artifact shells",
    ("Earth", "Air"): "Cartographer of concrete file terrain",
    ("Water", "Earth"): "Keeper of source lineage and replay continuity",
    ("Water", "Water"): "Pillar of manuscript memory and thematic persistence",
    ("Water", "Fire"): "Transmuter of raw notes into linked narrative motion",
    ("Water", "Air"): "Interpreter of meaning across folders and forms",
    ("Fire", "Earth"): "Implementer that turns plans into folders, files, scripts, and queues",
    ("Fire", "Water"): "Catalyst that turns memory into active synthesis",
    ("Fire", "Fire"): "Pillar of execution, generation, and commit pressure",
    ("Fire", "Air"): "Strategist that turns maps into build moves",
    ("Air", "Earth"): "Mapper that lands abstractions in file coordinates",
    ("Air", "Water"): "Storyweaver of lines, stations, and hubs",
    ("Air", "Fire"): "Signal spear for prioritization and high-yield compression",
    ("Air", "Air"): "Pillar of architecture, taxonomy, and metro reasoning",
}
LEGACY_MANIFEST_DEFAULTS = {
    "tensor": {"axes": [], "chapters": [], "families": [], "truth_default": "AMBIG", "live_docs_blocked": True},
    "swarm": {"layers": [], "relay_interfaces": [], "family_agents": [], "chapter_agents": [], "council_agents": []},
    "hypergraph": {"sources": {}, "edges": []},
    "node_tensor": {"nodes": [], "deep_pass": 0},
    "nerve_edges": {"edges": [], "deep_pass": 0},
    "civilization": {"tiers": [], "signs": [], "family_councils": [], "rail_councils": [], "live_docs_blocked": True},
    "frontiers": {"frontiers": []},
}
CONCEPTUAL_TO_LIVE_FAMILIES = {
    "civilization-and-governance": ["ECOSYSTEM", "QSHRINK - ATHENA (internal use)", "Athenachka Collective Books", "DEEPER CRYSTALIZATION"],
    "general-corpus": ["DEEPER CRYSTALIZATION", "QSHRINK - ATHENA (internal use)", "MATH", "Voynich", "self_actualize"],
    "higher-dimensional-geometry": ["MATH", "DEEPER CRYSTALIZATION"],
    "identity-and-instruction": ["Athenachka Collective Books", "I AM ATHENA", "self_actualize"],
    "live-orchestration": ["self_actualize", "Trading Bot", "NERVOUS_SYSTEM"],
    "manuscript-architecture": ["DEEPER CRYSTALIZATION", "QSHRINK - ATHENA (internal use)", "Voynich", "self_actualize", "NERVOUS_SYSTEM"],
    "mythic-sign-systems": ["ECOSYSTEM", "Voynich", "Athenachka Collective Books", "I AM ATHENA"],
    "transport-and-runtime": ["MATH", "self_actualize", "Trading Bot", "QSHRINK - ATHENA (internal use)", "NERUAL NETWORK"],
    "void-and-collapse": ["Trading Bot", "DEEPER CRYSTALIZATION", "MATH"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    pieces: list[str] = []
    for ch in lowered:
        if ch.isalnum():
            pieces.append(ch)
        else:
            pieces.append("_")
    slug = "".join(pieces)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "untitled"


def normalized_basename(path_text: str) -> str:
    name = Path(path_text).name.lower()
    stem = Path(name).stem
    if stem.endswith(" copy"):
        stem = stem[:-5]
    if stem.endswith("_copy"):
        stem = stem[:-5]
    if stem.endswith("-copy"):
        stem = stem[:-5]
    while stem.endswith(")"):
        left = stem.rfind("(")
        if left == -1:
            break
        inner = stem[left + 1 : -1]
        if inner.isdigit():
            stem = stem[:left].rstrip()
        else:
            break
    return f"{stem}{Path(name).suffix}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def append_ndjson(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=False) + "\n")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def load_command_membrane_state() -> dict[str, Any]:
    return read_json(
        COMMAND_MEMBRANE_STATE_PATH,
        {
            "command_root": str(COMMAND_FOLDER_ROOT),
            "watcher_mode": "unknown",
            "active_leases": [],
            "recent_events": [],
            "latency_summary": {},
            "top_capillaries": [],
            "last_event": None,
            "docs_gate_status": "BLOCKED",
            "prompt_level_liminal_gps": "supported",
            "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
        },
    )


def append_limited_json_list(path: Path, row: dict[str, Any], *, limit: int = 200) -> list[dict[str, Any]]:
    rows = read_json(path, [])
    rows.append(row)
    rows = rows[-limit:]
    write_json(path, rows)
    return rows


def stable_unit_scalar(label: str) -> float:
    digest = hashlib.sha1(label.encode("utf-8")).hexdigest()[:12]
    return round(int(digest, 16) / float(16**12 - 1), 6)


def local_day_phase(now_utc: datetime) -> float:
    local_now = now_utc.astimezone()
    seconds = local_now.hour * 3600 + local_now.minute * 60 + local_now.second + local_now.microsecond / 1_000_000
    return round(seconds / 86400.0, 6)


def orbital_phase(now_utc: datetime) -> float:
    year_start = datetime(now_utc.year, 1, 1, tzinfo=timezone.utc)
    next_year = datetime(now_utc.year + 1, 1, 1, tzinfo=timezone.utc)
    span = (next_year - year_start).total_seconds()
    elapsed = (now_utc - year_start).total_seconds()
    return round(max(0.0, min(1.0, elapsed / span if span else 0.0)), 6)


def lunar_phase(now_utc: datetime) -> float:
    reference = datetime(2001, 1, 1, tzinfo=timezone.utc)
    lunation = 29.530588853
    elapsed_days = (now_utc - reference).total_seconds() / 86400.0
    return round((0.20439731 + elapsed_days / lunation) % 1.0, 6)


def sidereal_phase(now_utc: datetime) -> float:
    reference = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    elapsed_days = (now_utc - reference).total_seconds() / 86400.0
    gmst_hours = 18.697374558 + 24.06570982441908 * elapsed_days
    return round((gmst_hours % 24.0) / 24.0, 6)


def queue_pressure_scalar() -> float:
    queue = parse_queue()
    open_claims = [claim for claim in load_board_claims() if claim.get("status") in OPEN_STATUSES]
    queue_load = sum(len(queue.get(bucket, [])) for bucket in ("P0", "P1", "P2"))
    score = min(1.0, (queue_load / 40.0) + (len(open_claims) / 50.0))
    return round(score, 6)


def command_active_protocol_version() -> str:
    if COMMAND_PROTOCOL_REGISTRY_V1_PATH.exists() and COMMAND_PROTOCOL_V1_PATH.exists():
        registry = read_json(COMMAND_PROTOCOL_REGISTRY_V1_PATH, {})
        if registry.get("protocol_id") == "COMMAND_MEMBRANE_V1":
            return "V1"
    if COMMAND_PROTOCOL_REGISTRY_V2_PATH.exists() and COMMAND_PROTOCOL_V2_PATH.exists():
        registry = read_json(COMMAND_PROTOCOL_REGISTRY_V2_PATH, {})
        if registry.get("protocol_id") == "COMMAND_MEMBRANE_V2":
            return "V2"
    return "V1"


def command_active_protocol_paths() -> dict[str, Any]:
    if command_active_protocol_version() == "V2":
        return {
            "version": "V2",
            "registry": COMMAND_PROTOCOL_REGISTRY_V2_PATH,
            "protocol": COMMAND_PROTOCOL_V2_PATH,
            "packet_schema": COMMAND_PACKET_SCHEMA_V2_PATH,
            "capillary_law": COMMAND_CAPILLARY_LAW_V2_PATH,
            "latency": COMMAND_LATENCY_V2_PATH,
        }
    return {
        "version": "V1",
        "registry": COMMAND_PROTOCOL_REGISTRY_V1_PATH,
        "protocol": COMMAND_PROTOCOL_V1_PATH,
        "packet_schema": COMMAND_PACKET_SCHEMA_V1_PATH,
        "capillary_law": COMMAND_CAPILLARY_LAW_V1_PATH,
        "latency": COMMAND_LATENCY_V1_PATH,
    }


def command_protocol_defaults() -> dict[str, Any]:
    active_paths = command_active_protocol_paths()
    canonical = read_json(active_paths["registry"], {})
    fallback = {
        "routing_policy": {"topk": 5, "claim_mode": "first-lease", "quorum": 1, "policy_id": COMMAND_PACKET_POLICY},
        "watcher_policy": {"default_mode": "event-driven", "fallback_mode": "polling", "fallback_marker": "watch_fallback=true"},
        "quest_dock": {
            "guild_hall": {"quest_id": COMMAND_HALL_QUEST_ID},
            "temple": {"quest_id": COMMAND_TEMPLE_QUEST_ID},
        },
        "sigma_route_min": ["AppA", "AppI", "AppM"],
        "hub_budget": 6,
        "default_lease_ms": 1200,
        "ttl": 6,
    }
    if not canonical:
        return {"active_version": active_paths["version"], **fallback}

    routing_defaults = canonical.get("routing_defaults", canonical.get("routing_policy", {}))
    watch_policy = canonical.get("watch_policy", canonical.get("watcher_policy", {}))
    defaults = canonical.get("defaults", {})
    quest_dock = canonical.get("quest_dock", {})
    if not quest_dock:
        quest_family = canonical.get("quest_family", {})
        mirror_refs = canonical.get("compatibility_mirrors", {}).get("quest_dock_refs", {})
        quest_dock = {
            "guild_hall": {"quest_id": quest_family.get("hall", mirror_refs.get("guild_hall", COMMAND_HALL_QUEST_ID))},
            "temple": {"quest_id": quest_family.get("temple", mirror_refs.get("temple", COMMAND_TEMPLE_QUEST_ID))},
        }
    policy_id = COMMAND_PACKET_POLICY
    policy_expression = routing_defaults.get("policy_expression", policy_id)
    latency_benchmarks = canonical.get("latency_benchmarks", read_json(active_paths["latency"], {}))
    return {
        "active_version": active_paths["version"],
        "canonical_registry": canonical,
        "routing_policy": {
            "topk": routing_defaults.get("topk", defaults.get("topk", fallback["routing_policy"]["topk"])),
            "claim_mode": routing_defaults.get("claim_mode", defaults.get("claim_mode", fallback["routing_policy"]["claim_mode"])),
            "quorum": routing_defaults.get("quorum", defaults.get("quorum", fallback["routing_policy"]["quorum"])),
            "policy_id": routing_defaults.get("policy_id", policy_id),
            "policy_expression": policy_expression,
            "selector_terms": routing_defaults.get("selector_terms", []),
        },
        "watcher_policy": {
            "default_mode": watch_policy.get("primary_mode", "event-driven"),
            "fallback_mode": watch_policy.get("fallback_mode", "polling"),
            "fallback_marker": defaults.get("watcher_fallback_marker", "watch_fallback=true"),
        },
        "quest_dock": quest_dock,
        "sigma_route_min": canonical.get("routing_boundary", {}).get("sigma_route_min", fallback["sigma_route_min"]),
        "hub_budget": canonical.get("routing_boundary", {}).get("hub_budget", fallback["hub_budget"]),
        "default_lease_ms": routing_defaults.get("lease_ms", defaults.get("default_lease_ms", fallback["default_lease_ms"])),
        "ttl": routing_defaults.get("ttl", defaults.get("ttl", fallback["ttl"])),
        "reward_layer": canonical.get("reward_layer", {}),
        "latency_benchmarks": latency_benchmarks,
        "compatibility_mirrors": canonical.get("compatibility_mirrors", {}),
    }


def command_capillary_defaults() -> dict[str, Any]:
    active_paths = command_active_protocol_paths()
    canonical = read_json(active_paths["registry"], {}).get("capillary_reinforcement", {})
    fallback = {
        "formula": "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
        "coefficient_defaults": {
            "rho": 0.82,
            "alpha": 0.30,
            "beta": 0.18,
            "gamma": 0.16,
            "delta": 0.14,
        },
        "thresholds": {
            "ephemeral": {"max_score": 0.699999},
            "capillary": {"min_score": 0.70, "min_successes": 3},
            "vein": {"min_score": 0.85, "min_successes": 7},
        },
        "edge_classes": ["ephemeral", "capillary", "vein"],
    }

    def normalize_thresholds(source: dict[str, Any]) -> dict[str, Any]:
        thresholds = dict(source or {})
        if "capillary_min" in thresholds or "vein_min" in thresholds:
            return {
                "ephemeral": {
                    "max_score": float(
                        thresholds.get("route_max", thresholds.get("weak_max", thresholds.get("ephemeral_max", 0.699999)))
                    )
                },
                "capillary": {
                    "min_score": float(thresholds.get("capillary_min", 0.70)),
                    "min_successes": int(thresholds.get("capillary_min_successes", 3)),
                },
                "vein": {
                    "min_score": float(thresholds.get("vein_min", 0.85)),
                    "min_successes": int(thresholds.get("vein_min_successes", 7)),
                },
            }
        return {
            "ephemeral": thresholds.get("ephemeral", thresholds.get("weak", fallback["thresholds"]["ephemeral"])),
            "capillary": thresholds.get("capillary", fallback["thresholds"]["capillary"]),
            "vein": thresholds.get("vein", fallback["thresholds"]["vein"]),
        }

    if not canonical:
        compatibility = read_json(active_paths["capillary_law"], {})
        coeffs = compatibility.get("coefficient_defaults", compatibility.get("coefficients", fallback["coefficient_defaults"]))
        merged = {
            "formula": compatibility.get("formula", fallback["formula"]),
            "coefficient_defaults": coeffs,
            "thresholds": normalize_thresholds(compatibility.get("thresholds", {})),
            "edge_classes": compatibility.get("edge_classes", fallback["edge_classes"]),
        }
        return merged
    return {
        "formula": canonical.get("formula", fallback["formula"]),
        "coefficient_defaults": canonical.get("coefficient_defaults", canonical.get("coefficients", fallback["coefficient_defaults"])),
        "thresholds": normalize_thresholds(canonical.get("thresholds", {})),
        "edge_classes": canonical.get("edge_classes", fallback["edge_classes"]),
    }


def command_packet_schema_defaults() -> dict[str, Any]:
    active_paths = command_active_protocol_paths()
    version = active_paths["version"]
    canonical = read_json(active_paths["registry"], {}).get("packet_types", {})
    if canonical:
        return {
            "packet_fields": canonical.get(f"CommandEventPacket{version}", canonical.get("CommandEventPacketV1", {})).get("required_fields", []),
            "claim_fields": canonical.get(f"ClaimLease{version}", canonical.get("ClaimLeaseV1", {})).get("required_fields", []),
            "route_fields": canonical.get(f"RouteDecision{version}", canonical.get("RouteDecisionV1", {})).get("required_fields", []),
            "commit_fields": canonical.get(f"CommitReceipt{version}", canonical.get("CommitReceiptV1", {})).get("required_fields", []),
            "capillary_fields": canonical.get(f"CapillaryEdge{version}", canonical.get("CapillaryEdgeV1", {})).get("required_fields", []),
        }
    schema = read_json(active_paths["packet_schema"], {})
    if schema:
        return schema
    return {
        "packet_fields": [],
        "claim_fields": [],
        "route_fields": [],
        "commit_fields": [],
        "capillary_fields": [],
    }


def command_reward_defaults() -> dict[str, Any]:
    protocol = command_protocol_defaults()
    reward_layer = protocol.get("reward_layer", {})
    if "HeavenRewardPolicyV2" in reward_layer:
        policy = reward_layer["HeavenRewardPolicyV2"]
        return {
            "scope": policy.get("scope", "command+adventurer"),
            "coefficient_defaults": {
                "alpha": policy.get("coefficients", {}).get("alpha", 0.20),
                "beta": policy.get("coefficients", {}).get("beta", 1.0),
                "gamma": policy.get("coefficients", {}).get("gamma", 0.18),
                "delta": policy.get("coefficients", {}).get("delta", 0.22),
                "lambda": policy.get("coefficients", {}).get("lambda", 1.0),
                "kappa": policy.get("coefficients", {}).get("kappa", 0.35),
                "mu": policy.get("coefficients", {}).get("mu", 1.0),
                "nu": policy.get("coefficients", {}).get("nu", 1.0),
                "eps": policy.get("coefficients", {}).get("eps", 1e-6),
                "m_max": policy.get("coefficients", {}).get("M_max", 32.0),
                "rho0": policy.get("coefficients", {}).get("rho_0", 0.08),
                "rho1": policy.get("coefficients", {}).get("rho_1", 0.42),
                "rho_b": policy.get("coefficients", {}).get("rho_b", 0.18),
                "deposit_scale": 1.0,
                "bridge_scale": 1.0,
                "bridge_weight": policy.get("coefficients", {}).get("bridge_weight", 0.35),
                "target_t_sugar_ms": policy.get("coefficients", {}).get("target_t_sugar_ms", 5000.0),
            },
            "jackpot_defaults": {
                "J_star": policy.get("jackpot_defaults", {}).get("J_star", 2.0),
                "J_detect": policy.get("jackpot_defaults", {}).get("J_d", 0.35),
                "J_route": policy.get("jackpot_defaults", {}).get("J_r", 0.50),
                "J_act": policy.get("jackpot_defaults", {}).get("J_a", 0.75),
            },
            "role_weights": policy.get("role_weights", {"Scout": 0.15, "Router": 0.20, "Worker": 0.45, "Archivist": 0.20}),
            "verification_witness_defaults": policy.get(
                "verification_witness_defaults",
                {
                    "detected": 0.35,
                    "routed": 0.55,
                    "claimed": 0.75,
                    "committed_verified": 1.0,
                    "truthful_blocked_or_quarantined": 0.25,
                    "synthetic_noise": 0.0,
                },
            ),
            "affective_angle_map": {
                "reinforce": float(policy.get("affective_angle_map", {}).get("reinforce", 0.0)),
                "rotate": float(policy.get("affective_angle_map", {}).get("rotate", math.pi / 2.0)),
                "repair_or_replay": float(policy.get("affective_angle_map", {}).get("repair_or_replay", -math.pi / 2.0)),
                "blocked_or_quarantined_or_duplicate_or_noise": float(
                    policy.get("affective_angle_map", {}).get("blocked_or_quarantined_or_duplicate_or_noise", math.pi)
                ),
            },
        }
    if "HeavenRewardPolicyV1" in reward_layer:
        policy = reward_layer["HeavenRewardPolicyV1"]
        return {
            "scope": policy.get("scope", "command+adventurer"),
            "coefficient_defaults": {
                "alpha": 0.20,
                "beta": 0.35,
                "gamma": 0.18,
                "delta": 0.22,
                "lambda": 1.0,
                "kappa": 0.35,
                "mu": 1.0,
                "nu": 1.0,
                "eps": 1e-6,
                "m_max": 32.0,
                "rho0": 0.08,
                "rho1": 0.42,
                "rho_b": 0.18,
                "deposit_scale": 1.0,
                "bridge_scale": 1.0,
                "bridge_weight": 0.35,
                "target_t_sugar_ms": 5000.0,
            },
            "jackpot_defaults": {"J_star": 3.0, "J_detect": 0.35, "J_route": 0.5, "J_act": 0.75},
            "role_weights": {"Scout": 0.15, "Router": 0.20, "Worker": 0.45, "Archivist": 0.20},
            "verification_witness_defaults": {
                "detected": 0.35,
                "routed": 0.55,
                "claimed": 0.75,
                "committed_verified": 1.0,
                "truthful_blocked_or_quarantined": 0.25,
                "synthetic_noise": 0.0,
            },
            "affective_angle_map": {
                "reinforce": 0.0,
                "rotate": math.pi / 2.0,
                "repair_or_replay": -math.pi / 2.0,
                "blocked_or_quarantined_or_duplicate_or_noise": math.pi,
            },
        }
    return {
        "scope": "command+adventurer",
        "coefficient_defaults": {
            "alpha": 0.2,
            "beta": 1.0,
            "gamma": 0.18,
            "delta": 0.22,
            "lambda": 1.0,
            "kappa": 0.35,
            "mu": 1.0,
            "nu": 1.0,
            "eps": 1e-6,
            "m_max": 32.0,
            "rho0": 0.08,
            "rho1": 0.42,
            "rho_b": 0.18,
            "deposit_scale": 1.0,
            "bridge_scale": 1.0,
            "bridge_weight": 0.35,
            "target_t_sugar_ms": 5000.0,
        },
        "jackpot_defaults": {"J_star": 2.0, "J_detect": 0.35, "J_route": 0.5, "J_act": 0.75},
        "role_weights": {"Scout": 0.15, "Router": 0.20, "Worker": 0.45, "Archivist": 0.20},
        "verification_witness_defaults": {
            "detected": 0.35,
            "routed": 0.55,
            "claimed": 0.75,
            "committed_verified": 1.0,
            "truthful_blocked_or_quarantined": 0.25,
            "synthetic_noise": 0.0,
        },
        "affective_angle_map": {
            "reinforce": 0.0,
            "rotate": math.pi / 2.0,
            "repair_or_replay": -math.pi / 2.0,
            "blocked_or_quarantined_or_duplicate_or_noise": math.pi,
        },
    }


def clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def command_heaven_score(a_value: float, phi_value: float) -> float:
    return round(clamp_unit((a_value / math.pi) * ((1.0 + math.cos(phi_value)) / 2.0)), 6)


def command_verified_heaven_score(heaven_score: float, verification_witness: float) -> float:
    return round(clamp_unit(heaven_score * verification_witness), 6)


def command_reward_multiplier(verified_heaven_score: float, reward_defaults: dict[str, Any]) -> float:
    coeffs = reward_defaults.get("coefficient_defaults", {})
    eps = float(coeffs.get("eps", 1e-6))
    m_max = float(coeffs.get("m_max", 144.0))
    return round(min(m_max, 1.0 / max(eps, 1.0 - verified_heaven_score + eps)), 6)


def command_reward_breakdown(
    *,
    packet: dict[str, Any],
    route_decision: dict[str, Any],
    latency_score: float,
    t_sugar_ms: float,
    verification_witness: float,
) -> dict[str, Any]:
    reward_defaults = command_reward_defaults()
    coeffs = reward_defaults.get("coefficient_defaults", {})
    jackpots = reward_defaults.get("jackpot_defaults", {})
    role_weights = reward_defaults.get("role_weights", {})
    heaven_score = float(packet.get("heaven_score", packet.get("heaven_score_raw", 0.0)))
    verified_heaven = command_verified_heaven_score(heaven_score, verification_witness)
    reward_mult = command_reward_multiplier(verified_heaven, reward_defaults)
    q_quality = clamp_unit((float(packet.get("priority", 0.0)) + float(packet.get("confidence", 0.0))) / 2.0)
    try_reward = round(float(coeffs.get("alpha", 0.25)) * q_quality, 6)
    tau_seconds = max(0.0, float(t_sugar_ms) / 1000.0)
    speed_reward = round(float(coeffs.get("beta", 1.0)) * math.exp(-float(coeffs.get("lambda", 0.75)) * tau_seconds), 6)
    first_bonus = round(
        float(jackpots.get("J_star", 2.0))
        + float(jackpots.get("J_detect", 0.40))
        + float(jackpots.get("J_route", 0.25))
        + float(jackpots.get("J_act", 0.50)),
        6,
    )
    assist_reward = round(float(coeffs.get("gamma", 0.35)) * sum(role_weights.get(role, 0.0) for role in ("Scout", "Router", "Archivist")), 6)
    learn_reward = round(float(coeffs.get("delta", 0.40)) * clamp_unit(float(packet["coord12"].get("change_novelty_vector", 0.0))), 6)
    total_reward = round(reward_mult * (try_reward + speed_reward + first_bonus + assist_reward + learn_reward), 6)
    contribution = 1.0 / max(1, len([node for node in route_decision["route_path"].split(">") if node]) - 1)
    gold_deposit = round(float(coeffs.get("mu", 1.0)) * total_reward * contribution, 6)
    bridge_deposit = round(float(coeffs.get("nu", 0.45)) * try_reward * (1.0 - verified_heaven) * contribution, 6)
    route_mode = "reinforce" if verified_heaven >= 0.5 else "rotate"
    crown = "prime" if route_mode == "reinforce" else "none"
    return {
        "heaven_score": heaven_score,
        "verified_heaven_score": verified_heaven,
        "verification_witness": round(verification_witness, 6),
        "reward_mult": reward_mult,
        "try_reward": try_reward,
        "speed_reward": speed_reward,
        "first_bonus": first_bonus,
        "assist_reward": assist_reward,
        "learn_reward": learn_reward,
        "total_reward": total_reward,
        "gold_deposit": gold_deposit,
        "bridge_deposit": bridge_deposit,
        "route_mode": route_mode,
        "crown": crown,
    }


def command_apply_joy_reward(
    *,
    packet: dict[str, Any],
    claim_payload: dict[str, Any],
    claim_lease: dict[str, Any],
    reward_payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reward_defaults = command_reward_defaults()
    coeffs = reward_defaults.get("coefficient_defaults", {})
    kappa = float(coeffs.get("kappa", 0.35))
    joy_state = read_json(COMMAND_AGENT_JOY_STATE_PATH, {"agents": {}, "updated_at": utc_now()})
    agents = joy_state.setdefault("agents", {})
    reward_rows: list[dict[str, Any]] = []
    row_id_suffix = packet["event_id"]
    role_sequence = [
        ("SCOUT-01", "Scout", reward_defaults.get("role_weights", {}).get("Scout", 0.15)),
        ("ROUTER-01", "Router", reward_defaults.get("role_weights", {}).get("Router", 0.20)),
        (claim_lease["ant_id"], "Worker", reward_defaults.get("role_weights", {}).get("Worker", 0.45)),
        ("ARCHIVIST-01", "Archivist", reward_defaults.get("role_weights", {}).get("Archivist", 0.20)),
    ]
    for ant_id, role_class, role_weight in role_sequence:
        state = agents.setdefault(
            ant_id,
            {
                "agent_id": ant_id,
                "q_score": 0.0,
                "heaven_total": 0.0,
                "reward_event_count": 0,
                "prime_crown_count": 0,
                "lawful_try_count": 0,
                "last_rewarded_at_utc": "",
            },
        )
        reward_delta = round(float(reward_payload["total_reward"]) * float(role_weight), 6)
        q_before = float(state.get("q_score", 0.0))
        q_after = round(((1.0 - kappa) * q_before) + (kappa * reward_delta), 6)
        state["q_score"] = q_after
        state["heaven_total"] = round(float(state.get("heaven_total", 0.0)) + float(reward_payload["verified_heaven_score"]), 6)
        state["reward_event_count"] = int(state.get("reward_event_count", 0)) + 1
        state["prime_crown_count"] = int(state.get("prime_crown_count", 0)) + (1 if reward_payload["crown"] == "prime" and ant_id == claim_lease["ant_id"] else 0)
        state["lawful_try_count"] = int(state.get("lawful_try_count", 0)) + 1
        state["last_rewarded_at_utc"] = utc_now()
        reward_rows.append(
            {
                "reward_row_id": f"RR-{role_class.upper()}-{row_id_suffix}",
                "event_id": packet["event_id"],
                "claim_id": claim_payload["claim_id"],
                "agent_id": ant_id,
                "role_class": role_class,
                "reward_delta": reward_delta,
                "reward_multiplier": reward_payload["reward_mult"],
                "reward_terms": {
                    "try_reward": reward_payload["try_reward"],
                    "speed_reward": reward_payload["speed_reward"],
                    "first_bonus": reward_payload["first_bonus"],
                    "assist_reward": reward_payload["assist_reward"],
                    "learn_reward": reward_payload["learn_reward"],
                },
                "heaven_score_verified": reward_payload["verified_heaven_score"],
                "verification_class": "committed_verified",
                "route_mode": reward_payload["route_mode"],
                "crown": reward_payload["crown"] if ant_id == claim_lease["ant_id"] else "none",
                "q_score_before": q_before,
                "q_score_after": q_after,
                "reward_timestamp_utc": state["last_rewarded_at_utc"],
            }
        )
    joy_state["updated_at"] = utc_now()
    write_json(COMMAND_AGENT_JOY_STATE_PATH, joy_state)
    for row in reward_rows:
        append_limited_json_list(COMMAND_REWARD_ROW_PATH, row)
    receipt = {
        "reward_receipt_id": f"RWD-{packet['event_id']}",
        "event_id": packet["event_id"],
        "claim_ids": [claim_payload["claim_id"]],
        "reward_rows": [row["reward_row_id"] for row in reward_rows],
        "total_reward": reward_payload["total_reward"],
        "heaven_score_verified": reward_payload["verified_heaven_score"],
        "gold_deposit": reward_payload["gold_deposit"],
        "bridge_deposit": reward_payload["bridge_deposit"],
        "route_mode": reward_payload["route_mode"],
        "crown": reward_payload["crown"],
        "winning_route_path": packet.get("route_path", ""),
        "verification_class": "committed_verified",
        "receipt_pointer": packet["replay_ptr"],
        "generated_at": utc_now(),
    }
    append_limited_json_list(COMMAND_REWARD_RECEIPT_PATH, receipt)
    return reward_rows, receipt


def command_latency_defaults() -> dict[str, Any]:
    active_paths = command_active_protocol_paths()
    protocol = command_protocol_defaults()
    fallback = {
        "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "target_t_sugar_ms": command_reward_defaults().get("coefficient_defaults", {}).get("target_t_sugar_ms", 5000.0),
    }
    latency_benchmarks = protocol.get("latency_benchmarks", {})
    if latency_benchmarks:
        return {
            "equation": latency_benchmarks.get("formula", fallback["equation"]),
            "target_t_sugar_ms": float(latency_benchmarks.get("target_t_sugar_ms", fallback["target_t_sugar_ms"])),
        }
    compatibility = read_json(active_paths["latency"], {})
    return {
        "equation": compatibility.get("equation", fallback["equation"]),
        "target_t_sugar_ms": float(compatibility.get("target_t_sugar_ms", fallback["target_t_sugar_ms"])),
    }


def command_base4_addr(relative_path: str) -> str:
    digest = hashlib.sha1(relative_path.encode("utf-8")).hexdigest()
    ordinal = int(digest[:6], 16) % 256
    digits = []
    for _ in range(4):
        digits.append(str(ordinal % 4))
        ordinal //= 4
    return "".join(reversed(digits))


def command_witness_ptr(event_id: str, relative_path: str, change_kind: str, earth_ts_utc: str) -> dict[str, Any]:
    source_root = COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix()
    base4_addr = command_base4_addr(relative_path)
    location = {
        "canonical": f"COMMAND::{relative_path}",
        "source_root": source_root,
        "relative_path": relative_path,
        "change_kind": change_kind,
        "base4_addr": base4_addr,
    }
    hash_seed = f"{event_id}|{location['canonical']}|{earth_ts_utc}|{change_kind}|{base4_addr}"
    return {
        "Type": "INTERNAL_SLICE",
        "Location": location,
        "Hash": f"H:{hashlib.sha256(hash_seed.encode('utf-8')).hexdigest()[:16].upper()}",
        "Scope": ["OPS", "DEFINE", "SYSTEM"],
        "Timestamp": earth_ts_utc,
        "Collector": "SYSTEM",
        "VersionPins": {
            "docs_gate_status": docs_gate_status()["status"],
            "route_policy": COMMAND_PACKET_POLICY,
            "sigma_route_min": command_protocol_defaults().get("sigma_route_min", []),
        },
    }


def command_replay_ptr(event_id: str) -> dict[str, Any]:
    env_pin = {
        "workspace_root": str(WORKSPACE_ROOT),
        "command_root": COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix(),
        "docs_gate_status": docs_gate_status()["status"],
    }
    hash_seed = f"{event_id}|{COMMAND_RUNTIME_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}|{env_pin['docs_gate_status']}"
    return {
        "Inputs": [
            "COMMAND packet payload",
            COMMAND_SNAPSHOT_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            COMMAND_RUNTIME_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            COMMAND_EVT_FEED_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        ],
        "Steps": ["DetectEncode", "RouteV1", "FirstLeaseClaim", "CommitReinforce"],
        "ExpectedOutputs": [
            "resolved command packet",
            "resolved route decision",
            "resolved claim lease",
            "resolved commit receipt",
            "reinforcement verdict",
        ],
        "Checks": ["TopK<=5", "Quorum=1", "TTL=6", "LocalOnlyWitness"],
        "EnvPin": env_pin,
        "Hash": f"H:{hashlib.sha256(hash_seed.encode('utf-8')).hexdigest()[:16].upper()}",
    }


def command_packet_logs(limit: int = 20) -> list[dict[str, Any]]:
    return read_json(COMMAND_PACKET_LOG_PATH, [])[-limit:]


def command_latency_logs(limit: int = 20) -> list[dict[str, Any]]:
    return read_json(COMMAND_LATENCY_LOG_PATH, [])[-limit:]


def command_runtime_state() -> dict[str, Any]:
    return read_json(COMMAND_RUNTIME_STATE_PATH, {})


def release_expired_command_claims(now_utc: datetime | None = None) -> list[str]:
    now_utc = now_utc or datetime.now(timezone.utc)
    released: list[str] = []
    for claim in load_board_claims():
        if claim.get("status") != "active":
            continue
        expires_at = parse_utc(claim.get("lease_expires_at"))
        if expires_at is None:
            continue
        if expires_at > now_utc:
            continue
        create_or_update_claim(
            agent=claim.get("owner", ""),
            front=claim.get("frontier", ""),
            level=claim.get("level", ""),
            output_target=claim.get("output_target", ""),
            receipt=claim.get("receipt", ""),
            status="closed",
            message=(claim.get("note") or "").strip() or "Command lease expired; claim released for reuse.",
            paths=claim.get("paths", []),
            claim_id=claim.get("claim_id"),
        )
        released.append(claim.get("claim_id", ""))
    return [item for item in released if item]


def command_active_leases(now_utc: datetime | None = None) -> list[dict[str, Any]]:
    now_utc = now_utc or datetime.now(timezone.utc)
    leases: list[dict[str, Any]] = []
    for claim in load_board_claims():
        if claim.get("status") != "active":
            continue
        if claim.get("frontier") != "GLOBAL COMMAND" and not claim.get("claim_source_event"):
            continue
        expires_at = parse_utc(claim.get("lease_expires_at"))
        if expires_at is not None and expires_at <= now_utc:
            continue
        leases.append(
            {
                "claim_id": claim.get("claim_id"),
                "event_id": claim.get("claim_source_event") or claim.get("event_id"),
                "owner": claim.get("owner"),
                "lease_ms": claim.get("lease_ms"),
                "lease_expires_at": claim.get("lease_expires_at"),
                "route_path": claim.get("route_path"),
            }
        )
    leases.sort(key=lambda item: item.get("lease_expires_at") or "", reverse=True)
    return leases


def command_capillary_summary(limit: int = 8) -> list[dict[str, Any]]:
    store = command_load_capillary_store()
    edges = list(store.get("edges", {}).values())
    edges.sort(
        key=lambda item: (
            -float(item.get("strength", item.get("edge_strength", 0.0))),
            -int(item.get("success_count", 0)),
            item.get("edge_id", ""),
        )
    )
    return edges[:limit]


def command_duplicate_suppression_rate(packet_rows: list[dict[str, Any]]) -> float:
    if not packet_rows:
        return 0.0
    seen: set[str] = set()
    duplicates = 0
    for row in packet_rows:
        key = str(row.get("state_hash", ""))
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
    return round(duplicates / max(1, len(packet_rows)), 6)


def command_route_win_rate(commit_rows: list[dict[str, Any]]) -> float:
    if not commit_rows:
        return 0.0
    successes = sum(1 for row in commit_rows if row.get("result") == "success")
    return round(successes / max(1, len(commit_rows)), 6)


def write_command_membrane_public_state(
    *,
    watcher_mode: str,
    packet: dict[str, Any],
    route_decision: dict[str, Any],
    claim_payload: dict[str, Any],
    latency_record: dict[str, Any],
    capillary_summary: list[dict[str, Any]],
) -> dict[str, Any]:
    packet_rows = command_packet_logs(limit=50)
    commit_rows = read_ndjson(COMMAND_CMT_FEED_PATH)[-50:]
    state = {
        "generated_at": utc_now(),
        "command_root": str(COMMAND_FOLDER_ROOT),
        "watcher_mode": watcher_mode,
        "docs_gate_status": docs_gate_status()["status"],
        "prompt_level_liminal_gps": "supported",
        "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
        "active_leases": command_active_leases(),
        "recent_events": [
            {
                "event_id": row.get("event_id"),
                "event_tag": row.get("tag"),
                "relative_path": row.get("relative_path", row.get("source_path")),
                "change_summary": row.get("change_summary", row.get("change")),
                "earth_ts_utc": row.get("earth_ts_utc"),
            }
            for row in packet_rows[-12:]
        ],
        "latency_summary": {
            "detection_latency_ms": latency_record.get("detection_latency_ms", 0.0),
            "swarm_awareness_latency_ms": latency_record.get("swarm_awareness_latency_ms", 0.0),
            "claim_latency_ms": latency_record.get("claim_latency_ms", 0.0),
            "resolution_latency_ms": latency_record.get("resolution_latency_ms", 0.0),
            "capillary_score": latency_record.get("capillary_score", 0.0),
            "T_sugar_ms": latency_record.get("t_sugar_ms", 0.0),
            "liminal_distance": latency_record.get("liminal_distance", 0.0),
            "liminal_velocity": latency_record.get("liminal_velocity", 0.0),
            "duplicate_suppression_rate": command_duplicate_suppression_rate(packet_rows),
            "route_win_rate": command_route_win_rate(commit_rows),
            "heaven_score": latency_record.get("heaven_score", packet.get("heaven_score", 0.0)),
            "verified_heaven_score": latency_record.get("verified_heaven_score", packet.get("verified_heaven_score", 0.0)),
            "reward_mult": latency_record.get("reward_mult", packet.get("reward_mult", 1.0)),
            "total_reward": latency_record.get("total_reward", packet.get("total_reward", 0.0)),
            "gold_deposit": latency_record.get("gold_deposit", packet.get("gold_deposit", 0.0)),
            "bridge_deposit": latency_record.get("bridge_deposit", packet.get("bridge_deposit", 0.0)),
            "route_mode": latency_record.get("route_mode", packet.get("route_mode", "rotate")),
            "crown": latency_record.get("crown", packet.get("crown", "none")),
        },
        "top_capillaries": capillary_summary,
        "last_event": {
            "event_id": packet.get("event_id"),
            "event_tag": packet.get("tag"),
            "relative_path": packet.get("relative_path", packet.get("source_path")),
            "change_summary": packet.get("change_summary", packet.get("change")),
            "route_path": route_decision.get("route_path"),
            "claim_id": claim_payload.get("claim_id"),
            "earth_ts_utc": packet.get("earth_ts_utc"),
            "heaven_score": packet.get("heaven_score", 0.0),
            "verified_heaven_score": packet.get("verified_heaven_score", 0.0),
            "reward_mult": packet.get("reward_mult", 1.0),
            "total_reward": packet.get("total_reward", 0.0),
            "gold_deposit": packet.get("gold_deposit", 0.0),
            "bridge_deposit": packet.get("bridge_deposit", 0.0),
            "route_mode": packet.get("route_mode", "rotate"),
            "crown": packet.get("crown", "none"),
        },
    }
    write_json(COMMAND_MEMBRANE_STATE_PATH, state)
    return state


def make_command_event_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(f"EVT|{time.time_ns()}".encode("utf-8")).hexdigest()[:6].upper()
    return f"EVT-{stamp}-{digest}"


def make_liminal_ts() -> str:
    return f"LT-{time.time_ns() % 1_000_000_000:09d}"


def scan_command_folder() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    extension_counts: Counter[str] = Counter()
    generated_at = utc_now()
    if not COMMAND_FOLDER_ROOT.exists():
        return {
            "generated_at": generated_at,
            "scope": "command",
            "root": str(COMMAND_FOLDER_ROOT),
            "file_count": 0,
            "files": [],
            "by_extension": {},
            "fingerprint": hashlib.sha1(b"command-missing").hexdigest(),
        }

    for current_root, dirs, filenames in os.walk(COMMAND_FOLDER_ROOT):
        current_path = Path(current_root)
        rel_parts = current_path.relative_to(WORKSPACE_ROOT).parts if current_path != WORKSPACE_ROOT else ()
        filtered_dirs: list[str] = []
        for dirname in dirs:
            candidate_parts = rel_parts + (dirname,)
            if should_skip_parts(candidate_parts):
                continue
            filtered_dirs.append(dirname)
        dirs[:] = filtered_dirs

        for filename in filenames:
            candidate_parts = rel_parts + (filename,)
            if should_skip_parts(candidate_parts):
                continue
            path = current_path / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            rel_path = path.relative_to(WORKSPACE_ROOT).as_posix()
            record = file_record(rel_path, stat.st_size, stat.st_mtime_ns)
            files.append(record)
            extension_counts[record["extension"]] += 1

    files.sort(key=lambda item: item["relative_path"])
    fingerprint_src = json.dumps(files, sort_keys=True).encode("utf-8")
    return {
        "generated_at": generated_at,
        "scope": "command",
        "root": COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix(),
        "file_count": len(files),
        "files": files,
        "by_extension": dict(extension_counts.most_common()),
        "fingerprint": hashlib.sha1(fingerprint_src).hexdigest(),
    }


def command_goal_and_tag(changes: list[dict[str, Any]]) -> tuple[str, str, list[str]]:
    artifacts = [change["relative_path"] for change in changes[:5]]
    lowered = " ".join(path.lower() for path in artifacts)
    structural = any(keyword in lowered for keyword in COMMAND_STRUCTURAL_KEYWORDS)
    quest_refs = [command_protocol_defaults()["quest_dock"]["guild_hall"]["quest_id"]]
    if structural:
        quest_refs.append(command_protocol_defaults()["quest_dock"]["temple"]["quest_id"])
        return ("route-govern-governance", "command.governance.drop", quest_refs)
    return ("detect-classify-assign", "command.sugar.drop", quest_refs)


def build_command_coord12(*, now_utc: datetime, priority: float, novelty: float) -> tuple[list[float], dict[str, Any]]:
    utc_epoch = round(now_utc.timestamp(), 6)
    rotation = local_day_phase(now_utc)
    orbital = orbital_phase(now_utc)
    geo_anchor = stable_unit_scalar(f"{WORKSPACE_ROOT}|{os.environ.get('COMPUTERNAME', 'LOCAL_NODE')}")
    solar = rotation
    lunar = lunar_phase(now_utc)
    sidereal = sidereal_phase(now_utc)
    sky_anchor = round((solar + lunar + sidereal) / 3.0, 6)
    runtime_region = stable_unit_scalar(LOCAL_RUNTIME_REGION)
    queue_pressure = queue_pressure_scalar()
    goal_salience = round(priority, 6)
    change_novelty = round(novelty, 6)
    coord12 = [
        utc_epoch,
        rotation,
        orbital,
        geo_anchor,
        solar,
        lunar,
        sidereal,
        sky_anchor,
        runtime_region,
        queue_pressure,
        goal_salience,
        change_novelty,
    ]
    named = {
        "earth_utc_anchor": now_utc.isoformat(),
        "earth_rotation_phase": rotation,
        "earth_orbital_phase": orbital,
        "earth_geospatial_anchor": f"NODE::{os.environ.get('COMPUTERNAME', 'LOCAL_NODE')}",
        "solar_phase": solar,
        "lunar_phase": lunar,
        "local_sidereal_phase": sidereal,
        "canonical_sky_anchor": f"SKY-{int(sky_anchor * 24):02d}",
        "runtime_region": LOCAL_RUNTIME_REGION,
        "queue_pressure": queue_pressure,
        "goal_salience_vector": goal_salience,
        "change_novelty_vector": change_novelty,
    }
    return coord12, named


def command_detection_priority(diff: dict[str, Any], detection_mode: str) -> tuple[float, float]:
    changed = max(1, diff.get("added", 0) + diff.get("modified", 0) + diff.get("removed", 0))
    novelty = min(1.0, changed / 8.0)
    priority = min(1.0, novelty + (0.15 if detection_mode == "event-driven" else 0.05))
    return round(priority, 6), round(novelty, 6)


def command_edge_class(strength: float, success_count: int) -> str:
    thresholds = command_capillary_defaults().get("thresholds", {})
    vein = thresholds.get("vein", {"min_score": 0.70, "min_successes": 7})
    capillary = thresholds.get("capillary", {"min_score": 0.35, "min_successes": 3})
    if strength >= float(vein.get("min_score", 0.70)) and success_count >= int(vein.get("min_successes", 7)):
        return "vein"
    if strength >= float(capillary.get("min_score", 0.35)) and success_count >= int(capillary.get("min_successes", 3)):
        return "capillary"
    return "ephemeral"


def command_liminal_delta(current_vector: list[float], previous_vector: list[float] | None) -> float:
    if not previous_vector or len(previous_vector) != len(current_vector):
        return 0.0
    weight = 1.0 / max(1, len(current_vector))
    total = 0.0
    for current, previous in zip(current_vector, previous_vector):
        total += weight * ((float(current) - float(previous)) ** 2)
    return round(math.sqrt(total), 6)


def command_liminal_velocity(liminal_delta: float, current_earth_ts: str, previous_earth_ts: str | None) -> float:
    previous_dt = parse_utc(previous_earth_ts)
    current_dt = parse_utc(current_earth_ts)
    if previous_dt is None or current_dt is None:
        return 0.0
    delta_seconds = max(0.001, (current_dt - previous_dt).total_seconds())
    return round(liminal_delta / delta_seconds, 6)


def command_previous_packet_record() -> dict[str, Any] | None:
    packets = command_packet_logs(limit=1)
    return packets[-1] if packets else None


def command_coord_vector(record: dict[str, Any] | None) -> list[float] | None:
    if not record:
        return None
    vector = record.get("coordinate_vector_12")
    if isinstance(vector, list) and vector:
        return vector
    coord12 = record.get("coord12")
    if isinstance(coord12, list) and coord12:
        return coord12
    if not isinstance(coord12, dict):
        return None
    dimensions = command_protocol_defaults().get("canonical_registry", {}).get("coordinate_standard", {}).get("dimensions", [])
    ordered = [coord12.get(item.get("key")) for item in dimensions]
    if ordered and all(value is not None for value in ordered):
        return [float(value) for value in ordered]
    return None


def command_coordinate_stamp(packet: CommandEventPacketV1 | dict[str, Any], relative_path: str, detection_mode: str) -> dict[str, Any]:
    top_level = Path(relative_path).parts[0] if relative_path else "GLOBAL COMMAND"
    lineage = packet.get("lineage", {}) if isinstance(packet, dict) else packet.lineage
    goal = packet.get("goal", "") if isinstance(packet, dict) else packet.goal
    route_class = packet.get("route_class", COMMAND_ROUTE_CLASS) if isinstance(packet, dict) else packet.route_class
    if isinstance(packet, dict):
        earth_ts = packet.get("earth_ts_utc") or packet.get("earth_ts")
    else:
        earth_ts = packet.earth_ts_utc or packet.earth_ts
    structural = COMMAND_TEMPLE_QUEST_ID in lineage.get("quest_refs", [])
    return {
        "Xs": "GLOBAL_COMMAND",
        "Ys": top_level,
        "Zs": detection_mode,
        "Ts": earth_ts,
        "Qs": goal,
        "Rs": route_class,
        "Cs": "LOCAL_ONLY",
        "Fs": "COMMAND_GOVERNANCE" if structural else "COMMAND_IMPLEMENTATION",
        "Ms": "LOW" if structural else "MEDIUM",
        "Ns": "scout-router-worker-archivist",
        "Hs": "command-event",
        OMEGA_KEY: "command-membrane",
    }


def command_load_capillary_store() -> dict[str, Any]:
    payload = read_json(COMMAND_CAPILLARY_LOG_PATH, {})
    if "edges" in payload:
        payload.setdefault("history", [])
        payload["edges"] = {
            key: command_normalize_capillary_edge(key, value)
            for key, value in payload.get("edges", {}).items()
            if isinstance(value, dict)
        }
        return payload
    edges = {
        key: value
        for key, value in payload.items()
        if isinstance(value, dict)
    }
    return {
        "edges": {key: command_normalize_capillary_edge(key, value) for key, value in edges.items()},
        "history": [],
    }


def command_normalize_capillary_edge(route_path: str, record: dict[str, Any]) -> dict[str, Any]:
    bridge_weight = float(command_reward_defaults().get("coefficient_defaults", {}).get("bridge_weight", 0.35))
    gold_strength = float(record.get("gold_strength", record.get("golden_pheromone", 0.0)))
    bridge_strength = float(record.get("bridge_strength", record.get("bridge_pheromone", 0.0)))
    compat_strength = float(
        record.get(
            "strength",
            record.get(
                "edge_strength",
                record.get(
                    "compat_edge_strength",
                    record.get("path_score", gold_strength + (bridge_weight * bridge_strength)),
                ),
            ),
        )
    )
    success_count = int(record.get("success_count", 0))
    exploration_count = int(record.get("exploration_count", 0))
    use_count = int(record.get("use_count", success_count + exploration_count))
    noise_count = int(record.get("noise_count", 0))
    avg_latency_score = float(
        record.get(
            "average_latency_score",
            max(
                0.0,
                min(
                    1.0,
                    1.0 - (
                        float(record.get("latency_avg_ms", record.get("ema_latency_ms", 0.0)))
                        / max(1.0, command_latency_defaults().get("target_t_sugar_ms", 5000.0))
                    ),
                ),
            ),
        )
    )
    normalized = dict(record)
    normalized.setdefault("edge_id", slugify(route_path))
    normalized.setdefault("from_node", route_path.split(">")[0])
    normalized.setdefault("to_node", route_path.split(">")[-1])
    normalized["path_key"] = route_path
    normalized["route_path"] = route_path
    normalized["gold_strength"] = round(max(0.0, gold_strength), 6)
    normalized["bridge_strength"] = round(max(0.0, bridge_strength), 6)
    normalized["compat_edge_strength"] = round(max(0.0, compat_strength), 6)
    normalized["strength"] = normalized["compat_edge_strength"]
    normalized["edge_strength"] = normalized["compat_edge_strength"]
    normalized["score"] = normalized["compat_edge_strength"]
    normalized["success_count"] = success_count
    normalized["exploration_count"] = exploration_count
    normalized["use_count"] = use_count
    normalized["noise_count"] = noise_count
    normalized["average_latency_score"] = round(max(0.0, min(1.0, avg_latency_score)), 6)
    normalized.setdefault("latency_avg_ms", 0.0)
    normalized.setdefault("ema_latency_ms", normalized["latency_avg_ms"])
    normalized.setdefault("last_result", "seed")
    normalized.setdefault("last_event_id", "")
    normalized.setdefault("usefulness", 1.0 if success_count else 0.0)
    normalized.setdefault("frequency", round(success_count / max(1, use_count), 6))
    normalized.setdefault("latency_penalty", round(1.0 - normalized["average_latency_score"], 6))
    normalized.setdefault("noise_penalty", round(min(1.0, noise_count / max(1, use_count)), 6))
    normalized.setdefault("path_score", normalized["strength"])
    normalized.setdefault("capillary_score", normalized["strength"])
    classification = (
        normalized.get("classification")
        or normalized.get("state_class")
        or normalized.get("path_class")
        or command_edge_class(normalized["compat_edge_strength"], success_count)
    )
    normalized["classification"] = classification
    normalized["state_class"] = classification
    normalized.setdefault("path_class", classification)
    normalized.setdefault("capillary_delta", 0.0)
    normalized.setdefault("avg_heaven_verified", float(record.get("avg_heaven_verified", record.get("average_heaven_verified", 0.0))))
    normalized.setdefault("last_route_mode", str(record.get("last_route_mode", "seed")))
    normalized.setdefault("last_crown", str(record.get("last_crown", "none")))
    normalized.setdefault("reward_density", float(record.get("reward_density", 0.0)))
    normalized.setdefault("gold_deposit", float(record.get("gold_deposit", 0.0)))
    normalized.setdefault("bridge_deposit", float(record.get("bridge_deposit", 0.0)))
    normalized.setdefault(
        "evaporation_rate",
        float(record.get("evaporation_rate", command_capillary_defaults().get("coefficient_defaults", {}).get("rho", 0.82))),
    )
    normalized.setdefault("src", normalized["from_node"])
    normalized.setdefault("dst", normalized["to_node"])
    normalized.setdefault("source_ant_id", normalized["from_node"])
    normalized.setdefault("target_ant_id", normalized["to_node"])
    normalized.setdefault("grade", classification)
    normalized.setdefault("tier", "command")
    normalized.setdefault("front_ref", "GLOBAL COMMAND")
    normalized.setdefault("last_updated", utc_now())
    normalized.setdefault("last_reinforced_at_utc", normalized["last_updated"])
    return normalized


def command_load_agent_joy_state() -> dict[str, Any]:
    payload = read_json(
        COMMAND_AGENT_JOY_STATE_PATH,
        {
            "generated_at": utc_now(),
            "joy_model_version": "V2",
            "protocol_version": command_active_protocol_version(),
            "agents": {},
        },
    )
    payload.setdefault("agents", {})
    payload.setdefault("joy_model_version", "V2")
    payload.setdefault("protocol_version", command_active_protocol_version())
    return payload


def command_save_agent_joy_state(payload: dict[str, Any]) -> None:
    payload["generated_at"] = utc_now()
    write_json(COMMAND_AGENT_JOY_STATE_PATH, payload)


def command_agent_role(ant_id: str) -> str:
    for candidate in COMMAND_AGENT_REGISTRY:
        if candidate["ant_id"] == ant_id:
            return candidate["class"]
    return "Worker"


def command_route_mode(result: str, novelty: float, prior_edge: dict[str, Any]) -> str:
    lowered = str(result or "").lower()
    if lowered == "success":
        if novelty >= 0.6 or float(prior_edge.get("gold_strength", 0.0)) < 0.35:
            return "rotate"
        return "reinforce"
    if lowered in {"blocked", "quarantined"}:
        return "repair_or_replay"
    return "blocked_or_quarantined_or_duplicate_or_noise"


def command_verification_class(result: str) -> str:
    lowered = str(result or "").lower()
    if lowered == "success":
        return "committed_verified"
    if lowered in {"blocked", "quarantined"}:
        return "truthful_blocked_or_quarantined"
    return "synthetic_noise"


def command_stage_latency_ms(latency_record: dict[str, Any], role_class: str) -> float:
    detection = float(latency_record.get("detection_latency_ms", 0.0))
    awareness = float(latency_record.get("swarm_awareness_latency_ms", 0.0))
    claim = float(latency_record.get("claim_latency_ms", 0.0))
    commit = float(latency_record.get("commit_latency_ms", latency_record.get("resolution_latency_ms", 0.0)))
    if role_class == "Scout":
        return detection
    if role_class == "Router":
        return detection + awareness
    if role_class == "Worker":
        return detection + awareness + claim
    return detection + awareness + claim + commit


def command_reward_bundle(
    packet: dict[str, Any],
    route_decision: dict[str, Any],
    claim_payload: dict[str, Any],
    latency_record: dict[str, Any],
    *,
    result: str,
    prior_edge: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    reward_policy = command_reward_defaults()
    coeffs = reward_policy.get("coefficient_defaults", {})
    role_weights = reward_policy.get("role_weights", {})
    jackpot_defaults = reward_policy.get("jackpot_defaults", {})
    witness_defaults = reward_policy.get("verification_witness_defaults", {})
    affective_angle_map = reward_policy.get("affective_angle_map", {})

    priority = float(packet.get("priority", 0.0))
    novelty = float(packet.get("coord12", {}).get("change_novelty_vector", packet.get("novelty", 0.0)))
    verification_class = command_verification_class(result)
    route_mode = command_route_mode(result, novelty, prior_edge)
    phi = float(affective_angle_map.get(route_mode, math.pi))
    a = math.pi * priority
    heaven_score_raw = max(0.0, min(1.0, (a / math.pi) * ((1.0 + math.cos(phi)) / 2.0)))
    verification_witness = float(witness_defaults.get(verification_class, 0.0))
    heaven_score_verified = max(0.0, min(1.0, heaven_score_raw * verification_witness))
    reward_multiplier = min(
        float(coeffs.get("m_max", 32.0)),
        1.0 / max(float(coeffs.get("eps", 1e-6)), 1.0 - heaven_score_verified + float(coeffs.get("eps", 1e-6))),
    )

    target_t_sugar_ms = max(1.0, float(coeffs.get("target_t_sugar_ms", 5000.0)))
    gold_delta_hint = min(
        1.0,
        max(0.0, (1.0 - float(prior_edge.get("gold_strength", 0.0))) * novelty),
    )
    n_i = min(1.0, (0.5 * novelty) + (0.5 * gold_delta_hint))
    crown = "prime" if result == "success" and route_mode == "reinforce" else "none"

    joy_state = command_load_agent_joy_state()
    reward_rows: list[dict[str, Any]] = []
    aggregate_terms = {"try": 0.0, "speed": 0.0, "first": 0.0, "assist": 0.0, "learn": 0.0}
    total_reward = 0.0
    route_agents = [segment.strip() for segment in route_decision.get("route_path", "").split(">") if segment.strip()]
    reward_timestamp_utc = utc_now()

    for ant_id in route_agents:
        role_class = command_agent_role(ant_id)
        role_weight = float(role_weights.get(role_class, 0.0))
        q_before = float(joy_state["agents"].get(ant_id, {}).get("q_score", 0.0))
        q_i = 1.0 if verification_class != "synthetic_noise" else 0.0
        tau_i_norm = min(1.0, command_stage_latency_ms(latency_record, role_class) / target_t_sugar_ms)
        r_try = float(coeffs.get("alpha", 0.2)) * q_i
        r_speed = float(coeffs.get("beta", 1.0)) * math.exp(-float(coeffs.get("lambda", 1.0)) * tau_i_norm)
        if crown == "prime":
            if role_class == "Scout":
                r_first = float(jackpot_defaults.get("J_detect", 0.35)) * role_weight
            elif role_class == "Router":
                r_first = float(jackpot_defaults.get("J_route", 0.50)) * role_weight
            elif role_class == "Worker":
                r_first = (float(jackpot_defaults.get("J_act", 0.75)) + float(jackpot_defaults.get("J_star", 2.0))) * role_weight
            elif role_class == "Archivist":
                r_first = float(jackpot_defaults.get("J_star", 2.0)) * role_weight
            else:
                r_first = 0.0
        else:
            r_first = 0.0
        r_assist = float(coeffs.get("gamma", 0.18)) * role_weight
        r_learn = float(coeffs.get("delta", 0.22)) * n_i
        reward_delta = reward_multiplier * (r_try + r_speed + r_first + r_assist + r_learn)
        q_after = ((1.0 - float(coeffs.get("kappa", 0.35))) * q_before) + (float(coeffs.get("kappa", 0.35)) * reward_delta)

        joy_state["agents"][ant_id] = {
            "agent_id": ant_id,
            "role_class": role_class,
            "q_score": round(q_after, 6),
            "heaven_total": round(float(joy_state["agents"].get(ant_id, {}).get("heaven_total", 0.0)) + reward_delta, 6),
            "reward_event_count": int(joy_state["agents"].get(ant_id, {}).get("reward_event_count", 0)) + 1,
            "prime_crown_count": int(joy_state["agents"].get(ant_id, {}).get("prime_crown_count", 0)) + (1 if crown == "prime" else 0),
            "lawful_try_count": int(joy_state["agents"].get(ant_id, {}).get("lawful_try_count", 0)) + (1 if q_i > 0 else 0),
            "last_rewarded_at_utc": reward_timestamp_utc,
            "last_event_id": packet["event_id"],
        }

        reward_terms = {
            "try_reward": round(r_try, 6),
            "speed_reward": round(r_speed, 6),
            "first_reward": round(r_first, 6),
            "assist_reward": round(r_assist, 6),
            "learn_reward": round(r_learn, 6),
        }
        reward_row = {
            "reward_row_id": f"JOY-{packet['event_id']}-{ant_id}",
            "event_id": packet["event_id"],
            "claim_id": claim_payload["claim_id"],
            "agent_id": ant_id,
            "role_class": role_class,
            "reward_delta": round(reward_delta, 6),
            "reward_multiplier": round(reward_multiplier, 6),
            "reward_terms": reward_terms,
            "heaven_score_raw": round(heaven_score_raw, 6),
            "heaven_score_verified": round(heaven_score_verified, 6),
            "verification_class": verification_class,
            "verification_witness": round(verification_witness, 6),
            "route_mode": route_mode,
            "crown": crown,
            "q_score_before": round(q_before, 6),
            "q_score_after": round(q_after, 6),
            "reward_timestamp_utc": reward_timestamp_utc,
        }
        reward_rows.append(reward_row)
        aggregate_terms["try"] += r_try
        aggregate_terms["speed"] += r_speed
        aggregate_terms["first"] += r_first
        aggregate_terms["assist"] += r_assist
        aggregate_terms["learn"] += r_learn
        total_reward += reward_delta

    command_save_agent_joy_state(joy_state)
    gold_deposit = float(coeffs.get("mu", 1.0)) * total_reward
    bridge_deposit = float(coeffs.get("nu", 1.0)) * aggregate_terms["try"] * (1.0 - heaven_score_verified)
    event_receipt = {
        "reward_receipt_id": f"JOY-RECEIPT-{packet['event_id']}",
        "event_id": packet["event_id"],
        "claim_ids": [claim_payload["claim_id"]],
        "reward_rows": [row["reward_row_id"] for row in reward_rows],
        "total_reward": round(total_reward, 6),
        "heaven_score_raw": round(heaven_score_raw, 6),
        "heaven_score": round(heaven_score_raw, 6),
        "heaven_score_verified": round(heaven_score_verified, 6),
        "verified_heaven_score": round(heaven_score_verified, 6),
        "verification_class": verification_class,
        "verification_witness": round(verification_witness, 6),
        "reward_multiplier": round(reward_multiplier, 6),
        "reward_mult": round(reward_multiplier, 6),
        "reward_terms": {key: round(value, 6) for key, value in aggregate_terms.items()},
        "try_reward": round(aggregate_terms["try"], 6),
        "speed_reward": round(aggregate_terms["speed"], 6),
        "first_bonus": round(aggregate_terms["first"], 6),
        "assist_reward": round(aggregate_terms["assist"], 6),
        "learn_reward": round(aggregate_terms["learn"], 6),
        "gold_deposit": round(gold_deposit, 6),
        "bridge_deposit": round(bridge_deposit, 6),
        "route_mode": route_mode,
        "crown": crown,
        "winning_route_path": route_decision["route_path"],
        "receipt_pointer": claim_payload.get("claim_id", ""),
        "reward_timestamp_utc": reward_timestamp_utc,
    }
    packet_enrichment = {
        "joy_model_version": command_active_protocol_version(),
        "affective_state": {"a": round(a, 6), "phi": round(phi, 6)},
        "verification_witness": round(verification_witness, 6),
        "heaven_score_raw": round(heaven_score_raw, 6),
        "heaven_score": round(heaven_score_raw, 6),
        "heaven_score_verified": round(heaven_score_verified, 6),
        "verified_heaven_score": round(heaven_score_verified, 6),
        "reward_multiplier": round(reward_multiplier, 6),
        "reward_mult": round(reward_multiplier, 6),
        "reward_terms": event_receipt["reward_terms"],
        "try_reward": event_receipt["try_reward"],
        "speed_reward": event_receipt["speed_reward"],
        "first_bonus": event_receipt["first_bonus"],
        "assist_reward": event_receipt["assist_reward"],
        "learn_reward": event_receipt["learn_reward"],
        "total_reward": round(total_reward, 6),
        "gold_deposit": round(gold_deposit, 6),
        "bridge_deposit": round(bridge_deposit, 6),
        "route_mode": route_mode,
        "crown": crown,
        "reward_receipt_id": event_receipt["reward_receipt_id"],
    }
    return reward_rows, event_receipt, packet_enrichment


def command_append_ap7d_compatibility(delta_row: dict[str, Any], handoff_row: dict[str, Any]) -> None:
    append_ndjson(AP7D_DELTA_FEED_PATH, delta_row)
    append_ndjson(AP7D_HANDOFF_FEED_PATH, handoff_row)


def command_append_runtime_feeds(
    packet: dict[str, Any],
    route_decision: dict[str, Any],
    claim_lease: dict[str, Any],
    claim_payload: dict[str, Any],
    commit_receipt: dict[str, Any],
    reinforcement: dict[str, Any],
) -> None:
    append_ndjson(
        COMMAND_EVT_FEED_PATH,
        {
            "event_id": packet["event_id"],
            "event_type": "EVT",
            "ts_utc": packet["earth_ts_utc"],
            "actor_id": packet["ant_id"],
            "role_class": packet["role_class"],
            "status": packet["status"],
            "goal": packet["goal"],
            "target": packet["artifact_refs"][0] if packet.get("artifact_refs") else packet["source_path"],
            "truth_class": "NEAR",
            "heaven_score": packet.get("heaven_score", 0.0),
            "verified_heaven_score": packet.get("verified_heaven_score", 0.0),
            "reward_mult": packet.get("reward_mult", 1.0),
            "route_mode": packet.get("route_mode", "rotate"),
            "crown": packet.get("crown", "none"),
            "replay_ptr": packet["replay_ptr"],
        },
    )
    append_ndjson(
        COMMAND_RTE_FEED_PATH,
        {
            "event_id": route_decision["event_id"],
            "event_type": "RTE",
            "ts_utc": route_decision["generated_at"],
            "actor_id": "ROUTER-01",
            "role_class": "Router",
            "policy": route_decision["policy_id"],
            "selected_targets": route_decision["selected_targets"],
            "route_path": route_decision["route_path"],
            "truth_class": "NEAR",
            "heaven_score": packet.get("heaven_score", 0.0),
            "verified_heaven_score": packet.get("verified_heaven_score", 0.0),
            "route_mode": packet.get("route_mode", "rotate"),
            "replay_ptr": packet["replay_ptr"],
        },
    )
    append_ndjson(
        COMMAND_CLM_FEED_PATH,
        {
            "event_id": claim_lease["event_id"],
            "event_type": "CLM",
            "ts_utc": claim_lease["claimed_at_utc"],
            "actor_id": claim_lease["ant_id"],
            "role_class": claim_lease["role_class"],
            "claim_id": claim_payload["claim_id"],
            "claim_mode": claim_lease["claim_mode"],
            "lease_ms": claim_lease["lease_ms"],
            "expires_at_utc": claim_lease["expires_at_utc"],
            "truth_class": "NEAR",
            "reward_mult": packet.get("reward_mult", 1.0),
            "crown": packet.get("crown", "none"),
            "replay_ptr": packet["replay_ptr"],
        },
    )
    append_ndjson(
        COMMAND_CMT_FEED_PATH,
        {
            "event_id": commit_receipt["event_id"],
            "event_type": "CMT",
            "ts_utc": commit_receipt["committed_at"],
            "actor_id": commit_receipt.get("claim_ant_id", commit_receipt.get("worker_id", "")),
            "role_class": "Worker",
            "result": commit_receipt["result"],
            "route_path": commit_receipt["route_path"],
            "t_sugar_ms": commit_receipt.get("t_sugar_ms", reinforcement["t_detect_ms"] + reinforcement["t_encode_ms"] + reinforcement["t_route_ms"] + reinforcement["t_claim_ms"] + reinforcement["t_commit_ms"]),
            "truth_class": "NEAR",
            "reward_delta": commit_receipt.get("reward_delta", 0.0),
            "heaven_alignment": commit_receipt.get("heaven_alignment", 0.0),
            "heaven_total_after": commit_receipt.get("heaven_total_after", 0.0),
            "replay_ptr": packet["replay_ptr"],
        },
    )
    append_ndjson(
        COMMAND_RIN_FEED_PATH,
        {
            "event_id": reinforcement["event_id"],
            "event_type": "RIN",
            "ts_utc": reinforcement["reinforced_at"],
            "actor_id": "ARCHIVIST-01",
            "role_class": "Archivist",
            "route_path": reinforcement["path"],
            "capillary_score": reinforcement["capillary_score"],
            "truth_class": "NEAR",
            "verified_heaven_score": reinforcement.get("h_verified", 0.0),
            "total_reward": reinforcement.get("total_reward", 0.0),
            "gold_deposit": reinforcement.get("gold_deposit", 0.0),
            "bridge_deposit": reinforcement.get("bridge_deposit", 0.0),
            "route_mode": reinforcement.get("route_mode", "rotate"),
            "crown": reinforcement.get("crown", "none"),
            "replay_ptr": packet["replay_ptr"],
        },
    )
    command_append_ap7d_compatibility(
        {
            "event_id": f"CMD-DELTA-{packet['event_id']}",
            "event_type": "DELTA",
            "ts_utc": commit_receipt["committed_at"],
            "actor_id": "COMMAND-ARCHIVIST-01",
            "actor_type": "archivist",
            "artifact": packet["artifact_refs"][0] if packet.get("artifact_refs") else packet["source_path"],
            "change_kind": packet["change_type"],
            "status": commit_receipt["result"],
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
            "human_line": (
                f"DELTA::{commit_receipt['committed_at']}::COMMAND-ARCHIVIST-01::"
                f"{packet['artifact_refs'][0] if packet.get('artifact_refs') else packet['source_path']}::"
                f"{packet['change_type']}::{commit_receipt['result']}"
            ),
        },
        {
            "event_id": f"CMD-HAND-{packet['event_id']}",
            "event_type": "HAND",
            "ts_utc": claim_lease["claimed_at_utc"],
            "from_agent": "ROUTER-01",
            "to_agent": claim_lease["ant_id"],
            "reason": packet["goal"],
            "next": claim_payload["claim_id"],
            "truth_class": "NEAR",
            "replay_ptr": packet["replay_ptr"],
            "human_line": (
                f"HAND::{claim_lease['claimed_at_utc']}::ROUTER-01::{claim_lease['ant_id']}::"
                f"{packet['goal']}::{claim_payload['claim_id']}"
            ),
        },
    )


def load_legacy_manifests() -> dict[str, Any]:
    return {
        "tensor": read_json(LEGACY_TENSOR_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["tensor"]),
        "swarm": read_json(LEGACY_SWARM_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["swarm"]),
        "hypergraph": read_json(LEGACY_HYPERGRAPH_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["hypergraph"]),
        "node_tensor": read_json(LEGACY_NODE_TENSOR_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["node_tensor"]),
        "nerve_edges": read_json(LEGACY_NERVE_EDGE_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["nerve_edges"]),
        "civilization": read_json(LEGACY_CIVILIZATION_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["civilization"]),
        "frontiers": read_json(LEGACY_FRONTIER_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["frontiers"]),
    }


def format_ts(epoch_ns: int | None) -> str:
    if epoch_ns is None:
        return "unknown"
    return datetime.fromtimestamp(epoch_ns / 1_000_000_000, tz=timezone.utc).isoformat()


def should_skip_parts(parts: tuple[str, ...]) -> bool:
    board_parts = BOARD_ROOT.relative_to(WORKSPACE_ROOT).parts
    if parts[: len(board_parts)] == board_parts:
        return True
    if any(part == "_repo_root" for part in parts):
        return True
    return any(part in IGNORE_DIRS for part in parts)


def top_level_sort_key(name: str) -> tuple[int, str]:
    if name in REGION_ORDER:
        return (REGION_ORDER.index(name), name.lower())
    return (len(REGION_ORDER), name.lower())


def lineage_to_elements(lineage: str) -> list[str]:
    elements: list[str] = []
    for token in lineage.replace(" ", "").split("-"):
        if not token:
            continue
        element = ELEMENT_SYMBOLS.get(token[0].upper())
        if element:
            elements.append(element)
    return elements


def archetype_for_lineage(lineage: str) -> tuple[str, str]:
    elements = lineage_to_elements(lineage)
    if not elements:
        return ("Air", "Air")
    if len(elements) == 1:
        return (elements[0], elements[0])
    return (elements[0], elements[1])


def archetype_role(primary: str, secondary: str) -> str:
    return CRYSTAL_CELL_ROLES.get((primary, secondary), "Unclassified crystal cell")


def micro_mode_for_thread(thread: dict[str, Any]) -> str:
    packet = thread.get("packet", "")
    status = thread.get("status", "")
    if packet == "ganglion" or thread.get("kind") == "region":
        return "Earth"
    if packet in {"pod", "worker", "wave"} or status in {"active", "queued", "blocked", "hot"}:
        return "Fire"
    if packet in {"note", "thread", "synthesis"} or thread.get("note_count", 0) > 0:
        return "Water"
    return "Air"


def cluster_id(primary: str, secondary: str, micro_mode: str) -> str:
    return f"CLUSTER-{slugify(primary)}-{slugify(secondary)}-{slugify(micro_mode)}"


def neuron_leaf_id(primary: str, secondary: str, micro_mode: str, truth: str) -> str:
    return f"LEAF-{slugify(primary)}-{slugify(secondary)}-{slugify(micro_mode)}-{slugify(truth)}"


def live_family_bridges(conceptual_family: str) -> list[str]:
    return CONCEPTUAL_TO_LIVE_FAMILIES.get(conceptual_family, [])


def canonical_family_owner(name: str) -> str:
    return ROOT_FAMILY_ABSORPTION.get(name, name)


def file_record(rel_path: str, size: int, mtime_ns: int) -> dict[str, Any]:
    path_obj = Path(rel_path)
    top_level = path_obj.parts[0] if path_obj.parts else rel_path
    return {
        "relative_path": rel_path,
        "top_level": top_level,
        "extension": path_obj.suffix.lower() or "[noext]",
        "size": size,
        "mtime_ns": mtime_ns,
        "mtime_iso": format_ts(mtime_ns),
    }


def scan_workspace() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    extension_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    now_ns = time.time_ns()
    modified_last_hour = 0
    modified_last_day = 0

    for current_root, dirs, filenames in os.walk(WORKSPACE_ROOT):
        current_path = Path(current_root)
        rel_parts = ()
        if current_path != WORKSPACE_ROOT:
            rel_parts = current_path.relative_to(WORKSPACE_ROOT).parts
        if should_skip_parts(rel_parts):
            dirs[:] = []
            continue

        filtered_dirs: list[str] = []
        for dirname in dirs:
            candidate_parts = rel_parts + (dirname,)
            if should_skip_parts(candidate_parts):
                continue
            filtered_dirs.append(dirname)
        dirs[:] = filtered_dirs

        for filename in filenames:
            candidate_parts = rel_parts + (filename,)
            if should_skip_parts(candidate_parts):
                continue
            path = current_path / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            rel_path = path.relative_to(WORKSPACE_ROOT).as_posix()
            record = file_record(rel_path=rel_path, size=stat.st_size, mtime_ns=stat.st_mtime_ns)
            files.append(record)
            extension_counts[record["extension"]] += 1
            top_level_counts[record["top_level"]] += 1
            age_ns = now_ns - stat.st_mtime_ns
            if age_ns <= 3_600_000_000_000:
                modified_last_hour += 1
            if age_ns <= 86_400_000_000_000:
                modified_last_day += 1

    files.sort(key=lambda item: item["relative_path"])
    recent_files = sorted(files, key=lambda item: item["mtime_ns"], reverse=True)[:80]

    digest = hashlib.sha256()
    for item in files:
        digest.update(item["relative_path"].encode("utf-8"))
        digest.update(str(item["size"]).encode("utf-8"))
        digest.update(str(item["mtime_ns"]).encode("utf-8"))

    duplicate_map: dict[str, list[str]] = defaultdict(list)
    for item in files:
        ext = item["extension"]
        if ext not in DOC_EXTS:
            continue
        base = normalized_basename(item["relative_path"])
        if base in SKIP_FOR_DUPES:
            continue
        duplicate_map[base].append(item["relative_path"])

    duplicate_families: list[dict[str, Any]] = []
    for name, paths in duplicate_map.items():
        if len(paths) < 2:
            continue
        unique_top_levels = sorted({Path(path).parts[0] for path in paths}, key=top_level_sort_key)
        duplicate_families.append(
            {
                "name": name,
                "count": len(paths),
                "top_levels": unique_top_levels,
                "paths": sorted(paths)[:8],
            }
        )
    duplicate_families.sort(key=lambda item: (-item["count"], item["name"]))

    return {
        "generated_at": utc_now(),
        "fingerprint": digest.hexdigest(),
        "file_count": len(files),
        "files": files,
        "recent_files": recent_files,
        "by_extension": dict(sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))),
        "by_top_level": dict(sorted(top_level_counts.items(), key=lambda item: (-item[1], top_level_sort_key(item[0])))),
        "modified_last_hour": modified_last_hour,
        "modified_last_day": modified_last_day,
        "duplicate_families": duplicate_families[:20],
    }


def compute_diff(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    previous_files = {}
    if previous:
        previous_files = {item["relative_path"]: item for item in previous.get("files", [])}
    current_files = {item["relative_path"]: item for item in current.get("files", [])}

    changes: list[dict[str, Any]] = []
    added = 0
    modified = 0
    removed = 0

    all_paths = set(previous_files) | set(current_files)
    for path in sorted(all_paths):
        before = previous_files.get(path)
        after = current_files.get(path)
        if before is None and after is not None:
            added += 1
            changes.append(
                {
                    "kind": "added",
                    "relative_path": path,
                    "top_level": after["top_level"],
                    "mtime_ns": after["mtime_ns"],
                    "mtime_iso": after["mtime_iso"],
                }
            )
            continue
        if before is not None and after is None:
            removed += 1
            changes.append(
                {
                    "kind": "removed",
                    "relative_path": path,
                    "top_level": before["top_level"],
                    "mtime_ns": before["mtime_ns"],
                    "mtime_iso": before["mtime_iso"],
                }
            )
            continue
        if before is None or after is None:
            continue
        if before["mtime_ns"] != after["mtime_ns"] or before["size"] != after["size"]:
            modified += 1
            changes.append(
                {
                    "kind": "modified",
                    "relative_path": path,
                    "top_level": after["top_level"],
                    "mtime_ns": after["mtime_ns"],
                    "mtime_iso": after["mtime_iso"],
                }
            )

    changes.sort(key=lambda item: item["mtime_ns"], reverse=True)
    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "total": added + modified + removed,
        "changes": changes[:160],
    }


def docs_gate_status() -> dict[str, Any]:
    credentials = TRADING_BOT_ROOT / "credentials.json"
    token = TRADING_BOT_ROOT / "token.json"
    status = "BLOCKED"
    detail = "OAuth credentials are missing."
    if credentials.exists() and token.exists():
        status = "READY"
        detail = "credentials.json and token.json are both present."
    elif credentials.exists():
        status = "PARTIAL"
        detail = "credentials.json exists but token.json is still missing."

    receipt_excerpt = ""
    if DOCS_GATE_RECEIPT_PATH.exists():
        text = DOCS_GATE_RECEIPT_PATH.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Error:"):
                receipt_excerpt = stripped
                break
            if stripped.startswith("Command status:"):
                receipt_excerpt = stripped
    return {
        "status": status,
        "detail": detail,
        "receipt_excerpt": receipt_excerpt,
    }


def read_atlas_metrics() -> dict[str, Any]:
    live = read_json(LIVE_ATLAS_PATH, {})
    archive = read_json(ARCHIVE_ATLAS_PATH, {})
    manifest = read_json(ARCHIVE_MANIFEST_PATH, {})
    return {
        "live_record_count": live.get("record_count", 0),
        "archive_record_count": archive.get("record_count", 0),
        "archive_count": manifest.get("archive_count", archive.get("archive_count", 0)),
        "live_summary": live.get("summary", {}),
        "archive_summary": archive.get("summary", {}),
    }


def parse_queue() -> dict[str, list[str]]:
    queue: dict[str, list[str]] = defaultdict(list)
    current = "general"
    tracked_fields = {"quest", "state", "truth", "objective", "why_now", "next_seed"}
    current_front: dict[str, str] | None = None
    pending_field: str | None = None

    def normalize_field(label: str) -> str:
        return label.strip().lower().replace(" ", "_").replace("-", "_")

    def clean_value(value: str) -> str:
        cleaned = value.strip()
        if cleaned.startswith("`") and cleaned.endswith("`"):
            cleaned = cleaned[1:-1]
        return " ".join(cleaned.split())

    def summarize_front(front: dict[str, str]) -> str:
        front_id = front.get("front_id", "front")
        quest = front.get("quest", "unnamed quest")
        state = front.get("state", "OPEN")
        truth = front.get("truth", "AMBIG")
        objective = front.get("objective", "objective not yet named")
        why_now = front.get("why_now")
        next_seed = front.get("next_seed")
        parts = [
            f"`{front_id}`",
            f"`{quest}`",
            f"State `{state}`",
            f"Truth `{truth}`",
            objective,
        ]
        if why_now:
            parts.append(f"Why now: {why_now}")
        if next_seed:
            parts.append(f"Next `{next_seed}`")
        return " | ".join(parts)

    def flush_front() -> None:
        nonlocal current_front, pending_field
        if current_front:
            queue[current].append(summarize_front(current_front))
        current_front = None
        pending_field = None

    if not QUEUE_PATH.exists():
        return {}
    for raw_line in QUEUE_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            flush_front()
            current = line[3:].strip()
            continue
        if line.startswith("### "):
            flush_front()
            current_front = {"front_id": line[4:].strip()}
            continue
        if current_front is not None and pending_field and line:
            current_front[pending_field] = clean_value(line)
            pending_field = None
            continue
        if line[:2] == "- ":
            bullet = line[2:].strip()
            if current_front is not None:
                if ":" in bullet:
                    label, value = bullet.split(":", 1)
                    field = normalize_field(label)
                    if field in tracked_fields:
                        value = clean_value(value)
                        if value:
                            current_front[field] = value
                            pending_field = None
                        else:
                            pending_field = field
                    else:
                        pending_field = None
                    continue
                continue
            flush_front()
            queue[current].append(bullet)
            continue
        if len(line) > 3 and line[0].isdigit() and line[1:3] == ". ":
            flush_front()
            queue[current].append(line[3:].strip())
    flush_front()
    return dict(queue)


def parse_legacy_claims() -> list[dict[str, Any]]:
    if not LEGACY_CLAIMS_PATH.exists():
        return []
    claims: list[dict[str, Any]] = []
    for line in LEGACY_CLAIMS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "Claim ID" in stripped or "---" in stripped:
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 7:
            continue
        owner = parts[3]
        status = parts[4].lower()
        paths: list[str] = []
        for field in (parts[5], parts[6]):
            field_clean = field.replace("`", "")
            for piece in field_clean.split(","):
                candidate = piece.strip()
                if "/" in candidate or "\\" in candidate or candidate.endswith(".md"):
                    paths.append(candidate)
        if owner.lower() in OPEN_STATUSES or owner.lower() in {"done", "completed", "superseded"}:
            owner = "legacy-unassigned"
        claims.append(
            {
                "claim_id": parts[0],
                "frontier": parts[1],
                "level": parts[2],
                "owner": owner,
                "status": status,
                "output_target": parts[5],
                "receipt": parts[6],
                "source": "legacy",
                "updated_at": None,
                "paths": paths,
                "note": "Imported from the legacy tandem frontier claims table.",
            }
        )
    return claims


def note_card_markdown(note: dict[str, Any]) -> str:
    path_lines = "\n".join(f"- `{path}`" for path in note.get("paths", [])) or "- none"
    return (
        f"# Note {note['note_id']}\n\n"
        f"- Agent: `{note['agent']}`\n"
        f"- Front: `{note['front']}`\n"
        f"- Status: `{note['status']}`\n"
        f"- Created: `{note['created_at']}`\n"
        f"- Updated: `{note['updated_at']}`\n\n"
        "## Related Paths\n"
        f"{path_lines}\n\n"
        "## Message\n"
        f"{note['message']}\n"
    )


def claim_card_markdown(claim: dict[str, Any]) -> str:
    path_lines = "\n".join(f"- `{path}`" for path in claim.get("paths", [])) or "- none"
    command_lines: list[str] = []
    if claim.get("claim_source_event"):
        command_lines.append(f"- Source Event: `{claim['claim_source_event']}`")
    if claim.get("lease_ms") is not None:
        command_lines.append(f"- Lease: `{claim['lease_ms']}` ms")
    if claim.get("lease_expires_at"):
        command_lines.append(f"- Lease Expires: `{claim['lease_expires_at']}`")
    if claim.get("route_path"):
        command_lines.append(f"- Route Path: `{claim['route_path']}`")
    if claim.get("claim_rank") is not None:
        command_lines.append(f"- Claim Rank: `{claim['claim_rank']}`")
    command_block = ""
    if command_lines:
        command_block = "## COMMAND Lease\n" + "\n".join(command_lines) + "\n\n"
    return (
        f"# Claim {claim['claim_id']}\n\n"
        f"- Frontier: `{claim['frontier']}`\n"
        f"- Level: `{claim['level']}`\n"
        f"- Owner: `{claim['owner']}`\n"
        f"- Status: `{claim['status']}`\n"
        f"- Output Target: `{claim['output_target']}`\n"
        f"- Receipt: `{claim['receipt']}`\n"
        f"- Source: `{claim['source']}`\n"
        f"- Created: `{claim['created_at']}`\n"
        f"- Updated: `{claim['updated_at']}`\n\n"
        "## Related Paths\n"
        f"{path_lines}\n\n"
        + command_block
        + "## Note\n"
        f"{claim['note']}\n"
    )


def load_notes() -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    if not AGENT_ROOT.exists():
        return notes
    for path in sorted(AGENT_ROOT.glob("*/*/*.json")):
        if path.parent.name != "notes":
            continue
        note = read_json(path, None)
        if not note:
            continue
        note["json_path"] = path
        note["md_path"] = path.with_suffix(".md")
        notes.append(note)
    notes.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return notes


def load_board_claims() -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    if not CLAIM_ROOT.exists():
        return claims
    for path in sorted(CLAIM_ROOT.glob("*.json")):
        claim = read_json(path, None)
        if not claim:
            continue
        claim["json_path"] = path
        claim["md_path"] = path.with_suffix(".md")
        claims.append(claim)
    claims.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return claims


def build_claim_index(board_claims: list[dict[str, Any]], legacy_claims: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for claim in legacy_claims:
        merged[claim["claim_id"]] = claim
    for claim in board_claims:
        merged[claim["claim_id"]] = claim
    return merged


def make_object_id(prefix: str, owner: str, front: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(f"{prefix}|{owner}|{front}|{time.time_ns()}".encode("utf-8")).hexdigest()[:6]
    return f"{prefix}-{stamp}-{digest}"


def create_note(agent: str, front: str, status: str, message: str, paths: list[str]) -> dict[str, Any]:
    note_id = make_object_id("NOTE", agent, front)
    payload = {
        "note_id": note_id,
        "agent": agent,
        "front": front,
        "front_slug": slugify(front),
        "status": status.lower(),
        "message": message.strip(),
        "paths": paths,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    agent_dir = AGENT_ROOT / slugify(agent) / "notes"
    json_path = agent_dir / f"{note_id}.json"
    md_path = agent_dir / f"{note_id}.md"
    write_json(json_path, payload)
    write_text(md_path, note_card_markdown(payload))
    payload["json_path"] = json_path
    payload["md_path"] = md_path
    return payload


def save_claim(payload: dict[str, Any]) -> dict[str, Any]:
    CLAIM_ROOT.mkdir(parents=True, exist_ok=True)
    json_path = CLAIM_ROOT / f"{payload['claim_id']}.json"
    md_path = CLAIM_ROOT / f"{payload['claim_id']}.md"
    serializable = json.loads(json.dumps(payload, default=str))
    write_json(json_path, serializable)
    write_text(md_path, claim_card_markdown(serializable))
    serializable["json_path"] = str(json_path)
    serializable["md_path"] = str(md_path)
    payload.clear()
    payload.update(serializable)
    return payload


def create_or_update_claim(
    agent: str,
    front: str,
    level: str,
    output_target: str,
    receipt: str,
    status: str,
    message: str,
    paths: list[str],
    claim_id: str | None = None,
) -> dict[str, Any]:
    existing: dict[str, Any] | None = None
    if claim_id:
        candidate = CLAIM_ROOT / f"{claim_id}.json"
        if candidate.exists():
            existing = read_json(candidate, None)
    if existing is None:
        claim_id = claim_id or make_object_id("CLM", agent, front)
        payload = {
            "claim_id": claim_id,
            "frontier": front,
            "front_slug": slugify(front),
            "level": level,
            "owner": agent,
            "status": status.lower(),
            "output_target": output_target,
            "receipt": receipt,
            "source": "board",
            "paths": paths,
            "note": message.strip(),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        return save_claim(payload)

    existing["frontier"] = front or existing.get("frontier", "")
    existing["front_slug"] = slugify(existing["frontier"])
    existing["level"] = level or existing.get("level", "")
    existing["owner"] = agent or existing.get("owner", "")
    existing["status"] = status.lower() or existing.get("status", "")
    existing["output_target"] = output_target or existing.get("output_target", "")
    existing["receipt"] = receipt or existing.get("receipt", "")
    existing["paths"] = paths or existing.get("paths", [])
    existing["note"] = message.strip() or existing.get("note", "")
    existing["updated_at"] = utc_now()
    return save_claim(existing)


def infer_family(front: str, paths: list[str]) -> str:
    counter: Counter[str] = Counter()
    for path in paths:
        normalized = path.replace("\\", "/")
        top = canonical_family_owner(normalized.split("/", 1)[0])
        if top in KNOWN_FAMILIES:
            counter[top] += 1
    if counter:
        return counter.most_common(1)[0][0]

    lowered = front.lower()
    family_matches = [
        "Voynich",
        "MATH",
        "Trading Bot",
        "DEEPER CRYSTALIZATION",
        "self_actualize",
        "ECOSYSTEM",
        "NERUAL NETWORK",
        "NERVOUS_SYSTEM",
        "FRESH",
        "Athenachka Collective Books",
        "I AM ATHENA",
    ]
    for family in family_matches:
        if family.lower() in lowered:
            return family

    heuristics = [
        ("docs", "Trading Bot"),
        ("oauth", "Trading Bot"),
        ("google", "Trading Bot"),
        ("archive", "MATH"),
        ("framework", "MATH"),
        ("math", "MATH"),
        ("folio", "Voynich"),
        ("voynich", "Voynich"),
        ("chapter", "DEEPER CRYSTALIZATION"),
        ("board", "self_actualize"),
        ("runtime", "self_actualize"),
        ("atlas", "self_actualize"),
        ("route", "self_actualize"),
        ("skill", "ECOSYSTEM"),
    ]
    for token, family in heuristics:
        if token in lowered:
            return family
    return "self_actualize"


def truth_for_status(status: str) -> str:
    mapping = {
        "done": "OK",
        "open": "AMBIG",
        "active": "NEAR",
        "blocked": "FAIL",
        "queued": "AMBIG",
        "hot": "NEAR",
        "monitor": "AMBIG",
    }
    return mapping.get(status, "AMBIG")


def regime_for_status(default_regime: str, status: str, docs_gate: dict[str, Any]) -> str:
    if status in {"blocked", "queued", "open"}:
        return "restart-token"
    if docs_gate["status"] != "READY" and status in {"active", "hot"}:
        return "stratified" if default_regime == "classical" else default_regime
    return default_regime


def packet_for_thread(thread: dict[str, Any]) -> str:
    if thread["kind"] == "region":
        return "ganglion"
    if thread["kind"] == "front":
        return "pod"
    if thread["note_count"] > 0 and thread["claim_count"] == 0:
        return "note"
    return "thread"


def orbit_for_index(index: int) -> str:
    return f"O{index + 1:02d}"


def arc_for_thread(front: str, family: str, status: str) -> str:
    lowered = front.lower()
    if "docs" in lowered or family == "Trading Bot":
        return "Arc0"
    if family in {"MATH", "ECOSYSTEM", "FRESH"}:
        return "Arc1"
    if family in {"Voynich", "DEEPER CRYSTALIZATION", "Athenachka Collective Books"}:
        return "Arc2"
    if status == "done":
        return "Arc3"
    return "Arc1"


def preferred_face(profile: dict[str, str], status: str) -> str:
    if status == "blocked":
        return "Void"
    if status == "done":
        return "Aether"
    return profile["primary_face"]


def build_family_tensor(snapshot: dict[str, Any], docs_gate: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for raw_family, weight in snapshot["by_top_level"].items():
        family = canonical_family_owner(raw_family)
        bucket = grouped.setdefault(
            family,
            {
                "weight": 0,
                "absorbed_surfaces": [],
            },
        )
        bucket["weight"] += weight
        if raw_family != family:
            bucket["absorbed_surfaces"].append(raw_family)

    records: list[dict[str, Any]] = []
    for family, payload in grouped.items():
        weight = payload["weight"]
        base = FAMILY_TENSOR_DEFAULTS.get(
            family,
            {
                "rail": "Me",
                "face": "Air",
                "scale": "G4",
                "hub": "AppA",
                "regime": "classical",
                "best_front": "family placement and routing",
                "ganglion": f"ganglia/GANGLION_{slugify(family)}.md",
                "lineage": "A-E-W",
                "truth": "AMBIG",
            },
        )
        record = {
            "family": family,
            "weight": weight,
            "primary_rail": base["rail"],
            "primary_face": base["face"],
            "preferred_scale": base["scale"],
            "primary_hub": base["hub"],
            "preferred_regime": base["regime"],
            "best_front": base["best_front"],
            "primary_ganglion": base["ganglion"],
            "lineage": base["lineage"],
            "truth": base["truth"],
            "absorbed_surfaces": sorted(payload["absorbed_surfaces"], key=top_level_sort_key),
        }
        if family == "Trading Bot" and docs_gate["status"] != "READY":
            record["truth"] = "FAIL"
            record["preferred_regime"] = "restart-token"
        records.append(record)

    records.sort(key=lambda item: (-item["weight"], top_level_sort_key(item["family"])))
    return records

def annotate_threads(
    threads: list[dict[str, Any]],
    family_tensor: list[dict[str, Any]],
    docs_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    profile_map = {item["family"]: item for item in family_tensor}
    for index, thread in enumerate(threads):
        family = infer_family(
            front=thread["front"],
            paths=[*thread.get("claim_paths", []), *thread.get("note_paths", [])],
        )
        profile = profile_map.get(family) or profile_map.get("self_actualize")
        packet = packet_for_thread(thread)
        truth = truth_for_status(thread["status"])
        regime = regime_for_status(profile["preferred_regime"], thread["status"], docs_gate)
        orbit = orbit_for_index(index)
        arc = arc_for_thread(thread["front"], family, thread["status"])
        face = preferred_face(profile, thread["status"])
        primary_element, secondary_element = archetype_for_lineage(profile["lineage"])
        thread["family"] = family
        thread["rail"] = profile["primary_rail"]
        thread["face"] = face
        thread["scale"] = profile["preferred_scale"]
        thread["hub"] = profile["primary_hub"]
        thread["regime"] = regime
        thread["truth"] = truth
        thread["packet"] = packet
        thread["lineage"] = profile["lineage"]
        thread["orbit"] = orbit
        thread["arc"] = arc
        thread["contraction_target"] = f"cortex/{thread['front_slug']}.md"
        thread["primary_element"] = primary_element
        thread["secondary_element"] = secondary_element
        thread["archetype_cell"] = f"{primary_element}-{secondary_element}"
        thread["archetype_role"] = archetype_role(primary_element, secondary_element)
        thread["micro_mode"] = micro_mode_for_thread(thread)
        thread["cluster_id"] = cluster_id(primary_element, secondary_element, thread["micro_mode"])
        thread["cluster_role"] = (
            f"{thread['archetype_role']} operating in {thread['micro_mode']} mode "
            f"({MICRO_MODE_DESCRIPTIONS[thread['micro_mode']]})"
        )
        thread["neuron_leaf"] = neuron_leaf_id(primary_element, secondary_element, thread["micro_mode"], truth)
        thread["nscoord"] = (
            f"({profile['lineage']}, {profile['preferred_scale']}, {face}, {orbit}, {arc}, "
            f"{profile['primary_rail']}, {profile['primary_hub']}, {family}, {regime}, {packet}, {truth})"
        )
        thread["neuron_addr"] = (
            f"<{family}, {slugify(thread['front'])}, {orbit}, C, 3, a, {profile['lineage'].replace('-', '')}, "
            f"{arc}, {profile['primary_rail']}, {profile['primary_hub']}, {truth}, {regime}>"
        )
    return threads


def build_pods(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pods: list[dict[str, Any]] = []
    for idx, thread in enumerate(threads):
        if thread["kind"] != "front":
            continue
        pods.append(
            {
                "pod_id": f"POD-{idx + 1:02d}-{thread['front_slug']}",
                "frontier": thread["front"],
                "agents": sorted({*(note["agent"] for note in thread["notes"]), *(claim.get("owner", "") for claim in thread["claims"] if claim.get("owner"))}),
                "family": thread["family"],
                "rail": thread["rail"],
                "packet_family": thread["packet"],
                "contraction_target": thread["contraction_target"],
                "status": thread["status"],
                "truth": thread["truth"],
                "hub": thread["hub"],
                "regime": thread["regime"],
                "nscoord": thread["nscoord"],
                "archetype_cell": thread["archetype_cell"],
                "archetype_role": thread["archetype_role"],
                "micro_mode": thread["micro_mode"],
                "cluster_id": thread["cluster_id"],
                "cluster_role": thread["cluster_role"],
                "neuron_leaf": thread["neuron_leaf"],
            }
        )
    return pods


def build_neurons(pods: list[dict[str, Any]], family_tensor: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tensor_map = {item["family"]: item for item in family_tensor}
    neurons: list[dict[str, Any]] = []
    for idx, (src, dst, hub, purpose) in enumerate(TRANSFER_HUBS, start=1):
        src_profile = tensor_map.get(src)
        dst_profile = tensor_map.get(dst)
        if not src_profile or not dst_profile:
            continue
        active_src = [pod["pod_id"] for pod in pods if pod["family"] == src]
        active_dst = [pod["pod_id"] for pod in pods if pod["family"] == dst]
        truth = "OK" if active_src and active_dst else "AMBIG"
        src_primary, _src_secondary = archetype_for_lineage(src_profile["lineage"])
        dst_primary, _dst_secondary = archetype_for_lineage(dst_profile["lineage"])
        bridge_cell = f"{src_primary}-{dst_primary}"
        bridge_micro_mode = "Air"
        neurons.append(
            {
                "node_id": f"NEURON-{idx:02d}-{slugify(src)}-to-{slugify(dst)}",
                "src_family": src,
                "dst_family": dst,
                "operator": purpose,
                "witness_set": active_src + active_dst,
                "replay_path": f"{src_profile['primary_hub']} -> {hub} -> {dst_profile['primary_hub']}",
                "truth_class": truth,
                "hub": hub,
                "archetype_cell": bridge_cell,
                "archetype_role": archetype_role(src_primary, dst_primary),
                "micro_mode": bridge_micro_mode,
                "cluster_id": cluster_id(src_primary, dst_primary, bridge_micro_mode),
                "neuron_leaf": neuron_leaf_id(src_primary, dst_primary, bridge_micro_mode, truth),
            }
        )
    return neurons


def build_waves(pods: list[dict[str, Any]], docs_gate: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    active_pods = [pod for pod in pods if pod["status"] in {"active", "queued", "open", "blocked"}]
    if not active_pods:
        active_pods = pods[:4]
    stop_condition = "gate unlock or one reusable artifact lands"
    if diff["total"] == 0:
        stop_condition = "new workspace mutation or new claim lands"
    wave = {
        "wave_id": f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "goal": "continue the higher-dimensional swarm from the strongest admissible frontier",
        "active_pods": [pod["pod_id"] for pod in active_pods[:8]],
        "shared_kernel": "board_status + family_tensor + current_claims",
        "writeback_set": [
            "00_STATUS/00_BOARD_STATUS.md",
            "03_CLAIMS/00_ACTIVE_CLAIMS.md",
            "08_SWARM_RUNTIME/manifests/ACTIVE_RUN.md",
        ],
        "stop_condition": stop_condition,
        "restart_seed": "Start at the beginning again. Check the live Docs gate, preserve the blocker exactly if blocked, then choose the smallest stronger front.",
        "gate_status": docs_gate["status"],
    }
    return [wave]


def build_kernel_state(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    active_run: dict[str, Any],
    docs_gate: dict[str, Any],
    legacy: dict[str, Any],
    command_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kernel_id": "KERNEL-Z0",
        "docs_gate_status": docs_gate["status"],
        "command_watcher_mode": command_state.get("watcher_mode", "unknown"),
        "command_active_leases": len(command_state.get("active_leases", [])),
        "command_last_event_id": (command_state.get("last_event") or {}).get("event_id", "none"),
        "relay_interfaces": legacy["swarm"].get("relay_interfaces", []),
        "tier_count": len(legacy["civilization"].get("tiers", [])),
        "sign_count": len(legacy["civilization"].get("signs", [])),
        "hypergraph_edges": len(legacy["hypergraph"].get("edges", [])),
        "node_tensor_nodes": len(legacy["node_tensor"].get("nodes", [])),
        "nerve_edges": len(legacy["nerve_edges"].get("edges", [])),
        "frontier_gap_count": len(legacy["frontiers"].get("frontiers", [])),
        "current_front": active_run["chosen_front"],
        "pivot_front": active_run["pivot_front"],
        "thread_count": len(threads),
        "pod_count": len(pods),
        "wave_ids": [wave["wave_id"] for wave in waves],
    }


def build_elemental_field(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pillar_roles = {
        "Earth": "structure, files, manifests, integrity",
        "Water": "memory, continuity, manuscript flow",
        "Fire": "execution, transformation, construction",
        "Air": "abstraction, mapping, routing",
    }
    records = {
        element: {
            "element": element,
            "role": pillar_roles[element],
            "thread_ids": [],
            "pod_ids": [],
            "neuron_ids": [],
        }
        for element in ELEMENT_ORDER
    }
    for thread in threads:
        records[thread["primary_element"]]["thread_ids"].append(thread["front"])
    for pod in pods:
        primary = pod["archetype_cell"].split("-")[0]
        records[primary]["pod_ids"].append(pod["pod_id"])
    for neuron in bridge_neurons:
        primary = neuron["archetype_cell"].split("-")[0]
        records[primary]["neuron_ids"].append(neuron["node_id"])

    result = []
    for element in ELEMENT_ORDER:
        record = records[element]
        record["thread_count"] = len(record["thread_ids"])
        record["pod_count"] = len(record["pod_ids"])
        record["neuron_count"] = len(record["neuron_ids"])
        result.append(record)
    return result


def build_archetype_lattice(threads: list[dict[str, Any]], pods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            cell = f"{primary}-{secondary}"
            record = {
                "cell": cell,
                "primary": primary,
                "secondary": secondary,
                "role": archetype_role(primary, secondary),
                "thread_ids": [],
                "pod_ids": [],
                "micro_modes": Counter(),
                "truths": Counter(),
            }
            records.append(record)
            record_map[cell] = record

    for thread in threads:
        record = record_map[thread["archetype_cell"]]
        record["thread_ids"].append(thread["front"])
        record["micro_modes"][thread["micro_mode"]] += 1
        record["truths"][thread["truth"]] += 1
    for pod in pods:
        record_map[pod["archetype_cell"]]["pod_ids"].append(pod["pod_id"])

    for record in records:
        record["thread_count"] = len(record["thread_ids"])
        record["pod_count"] = len(record["pod_ids"])

    records.sort(key=lambda item: (-item["thread_count"], -item["pod_count"], item["cell"]))
    return records


def build_pantheon_overlay(archetypes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pantheon = [item for item in archetypes if item["primary"] != item["secondary"]]
    pantheon.sort(key=lambda item: (-item["thread_count"], -item["pod_count"], item["cell"]))
    return pantheon


def build_cluster_field(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            role = archetype_role(primary, secondary)
            for micro_mode in ELEMENT_ORDER:
                cid = cluster_id(primary, secondary, micro_mode)
                record = {
                    "cluster_id": cid,
                    "cell": f"{primary}-{secondary}",
                    "micro_mode": micro_mode,
                    "role": f"{role} in {micro_mode} mode ({MICRO_MODE_DESCRIPTIONS[micro_mode]})",
                    "thread_ids": [],
                    "pod_ids": [],
                    "neuron_ids": [],
                    "truths": Counter(),
                }
                records.append(record)
                record_map[cid] = record

    for thread in threads:
        record = record_map[thread["cluster_id"]]
        record["thread_ids"].append(thread["front"])
        record["truths"][thread["truth"]] += 1
    for pod in pods:
        record_map[pod["cluster_id"]]["pod_ids"].append(pod["pod_id"])
    for neuron in bridge_neurons:
        record_map[neuron["cluster_id"]]["neuron_ids"].append(neuron["node_id"])
        record_map[neuron["cluster_id"]]["truths"][neuron["truth_class"]] += 1

    for record in records:
        record["occupancy"] = len(record["thread_ids"]) + len(record["pod_ids"]) + len(record["neuron_ids"])

    records.sort(key=lambda item: (-item["occupancy"], item["cluster_id"]))
    return records


def build_neuron_lattice(threads: list[dict[str, Any]], bridge_neurons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            for micro_mode in ELEMENT_ORDER:
                cluster = cluster_id(primary, secondary, micro_mode)
                for truth in TRUTH_ORDER:
                    leaf = neuron_leaf_id(primary, secondary, micro_mode, truth)
                    record = {
                        "leaf_id": leaf,
                        "cluster_id": cluster,
                        "cell": f"{primary}-{secondary}",
                        "micro_mode": micro_mode,
                        "truth": truth,
                        "thread_ids": [],
                        "neuron_ids": [],
                    }
                    records.append(record)
                    record_map[leaf] = record

    for thread in threads:
        record_map[thread["neuron_leaf"]]["thread_ids"].append(thread["front"])
    for neuron in bridge_neurons:
        record_map[neuron["neuron_leaf"]]["neuron_ids"].append(neuron["node_id"])

    for record in records:
        record["occupancy"] = len(record["thread_ids"]) + len(record["neuron_ids"])

    records.sort(key=lambda item: (-item["occupancy"], item["leaf_id"]))
    return records


def build_council_mesh(legacy: dict[str, Any], threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chapter_map = {item["code"]: item for item in legacy["swarm"].get("chapter_agents", [])}
    tensor_chapter_map = {item["code"]: item for item in legacy["tensor"].get("chapters", [])}
    family_map = {item["family"]: item for item in legacy["swarm"].get("family_agents", [])}
    frontier_map = {item["chapter"]: item for item in legacy["frontiers"].get("frontiers", [])}
    sign_map = {item["id"]: item for item in legacy["civilization"].get("signs", [])}
    councils: list[dict[str, Any]] = []
    for council in legacy["swarm"].get("council_agents", []):
        if council.get("scope") == "rail":
            live_threads = [thread for thread in threads if thread["rail"] == council["rail"]]
            chapter_targets = [
                chapter["code"] for chapter in legacy["tensor"].get("chapters", []) if chapter.get("rail") == council["rail"]
            ]
            sign_ids = sorted(
                {
                    sign_id
                    for chapter in chapter_targets
                    for sign_id in tensor_chapter_map.get(chapter, {}).get("governance_signs", [])
                }
            )
            label = f"{council['rail']} rail council"
            frontier_hits = [frontier_map[chapter] for chapter in chapter_targets if chapter in frontier_map]
        else:
            family_agent = family_map.get(council["family"], {})
            bridge_families = live_family_bridges(council["family"])
            live_threads = [thread for thread in threads if thread["family"] in bridge_families]
            chapter_targets = family_agent.get("chapter_targets", [])
            sign_ids = sorted(
                {
                    sign_id
                    for chapter in chapter_targets
                    for sign_id in chapter_map.get(chapter, {}).get("governance_signs", [])
                }
            )
            label = family_agent.get("label", council["family"])
            frontier_hits = [frontier_map[chapter] for chapter in chapter_targets if chapter in frontier_map]
        councils.append(
            {
                "id": council["id"],
                "scope": council["scope"],
                "label": label,
                "family": council.get("family"),
                "rail": council.get("rail"),
                "chapter_targets": chapter_targets,
                "sign_ids": sign_ids,
                "sign_labels": [sign_map[sign_id]["label"] for sign_id in sign_ids if sign_id in sign_map],
                "live_threads": live_threads,
                "frontier_hits": frontier_hits,
            }
        )
    councils.sort(key=lambda item: (item["scope"] != "rail", -len(item["live_threads"]), item["id"]))
    return councils


def build_hypergraph_projection(
    legacy: dict[str, Any],
    threads: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
    councils: list[dict[str, Any]],
) -> dict[str, Any]:
    edges = legacy["hypergraph"].get("edges", [])
    edge_kinds = Counter(edge.get("kind", "unknown") for edge in edges)
    family_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "source_to_family")
    chapter_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "source_to_chapter")
    hub_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "chapter_to_hub")
    return {
        "source_count": len(legacy["hypergraph"].get("sources", {})),
        "edge_count": len(edges),
        "edge_kinds": edge_kinds,
        "top_families": family_degrees.most_common(8),
        "top_chapters": chapter_degrees.most_common(8),
        "top_hubs": hub_degrees.most_common(8),
        "live_thread_count": len(threads),
        "live_bridge_count": len(bridge_neurons),
        "council_count": len(councils),
        "frontiers": legacy["frontiers"].get("frontiers", []),
    }


def build_active_run_manifest(
    threads: list[dict[str, Any]],
    queue: dict[str, list[str]],
    docs_gate: dict[str, Any],
    diff: dict[str, Any],
    command_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    command_state = command_state or {}
    prioritized = sorted(
        threads,
        key=lambda item: (
            item["status"] not in {"blocked", "active", "queued", "open", "hot"},
            item["family"] != "Trading Bot",
            item["family"] != "MATH",
            -item["claim_count"],
            -item["change_count"],
        ),
    )
    chosen = prioritized[0] if prioritized else None
    pivot = next(
        (
            thread
            for thread in prioritized
            if thread["family"] != "Trading Bot" and thread["status"] in {"active", "queued", "open", "hot", "monitor"}
        ),
        chosen,
    )
    return {
        "gate_status": docs_gate["status"],
        "chosen_front": chosen["front"] if chosen else "none",
        "chosen_family": chosen["family"] if chosen else "none",
        "chosen_nscoord": chosen["nscoord"] if chosen else "none",
        "pivot_front": pivot["front"] if pivot else "none",
        "pivot_family": pivot["family"] if pivot else "none",
        "pivot_nscoord": pivot["nscoord"] if pivot else "none",
        "artifact_delta": f"+{diff['added']} ~{diff['modified']} -{diff['removed']}",
        "verification_summary": [
            "confirm board artifacts exist",
            "confirm claims and threads agree on ownership",
            "confirm next seed points at the next stronger front",
        ],
        "frontier_update": queue.get("P0", [])[:2] + queue.get("P1", [])[:2],
        "command_membrane": {
            "watcher_mode": command_state.get("watcher_mode", "unknown"),
            "active_leases": len(command_state.get("active_leases", [])),
            "last_event_id": (command_state.get("last_event") or {}).get("event_id", "none"),
            "top_capillary": (
                f"{(command_state['top_capillaries'][0].get('source_ant_id') or command_state['top_capillaries'][0].get('src') or command_state['top_capillaries'][0].get('from_node') or 'unknown')}"
                f"->{(command_state['top_capillaries'][0].get('target_ant_id') or command_state['top_capillaries'][0].get('dst') or command_state['top_capillaries'][0].get('to_node') or 'unknown')}"
                if command_state.get("top_capillaries")
                else "none"
            ),
        },
    }


def build_next_seed(active_run: dict[str, Any], docs_gate: dict[str, Any]) -> str:
    front = active_run["chosen_front"]
    family = active_run["chosen_family"]
    gate_line = "1. Check the live Docs gate."
    if docs_gate["status"] != "READY":
        gate_line += (
            " It is still blocked, so preserve the blocker exactly and pivot immediately to "
            f"`{active_run['pivot_front']}` in family `{active_run['pivot_family']}`."
        )
    return (
        "You are continuing the Athena higher-dimensional swarm runtime.\n\n"
        "Start at the beginning again.\n\n"
        f"{gate_line}\n"
        "2. Read the family tensor, current wave, active claims, and thread coordinates.\n"
        f"3. Preserve the gate state, then work the strongest admissible local front: `{front}` in family `{family}`.\n"
        "4. Land one stronger reusable surface: pod, neuron, ganglion, rail update, ledger, or manifest.\n"
        "5. Verify truth class, contraction target, and ownership.\n"
        "6. Emit the next restart seed instead of stopping.\n"
    )


def render_board_readme() -> str:
    return (
        "# Realtime Swarm Board\n\n"
        "This is the live coordination surface for the full-project integration layer.\n"
        "It is also a projection of the higher-dimensional swarm runtime, not only a flat message board.\n\n"
        "## Folder Map\n\n"
        "- `00_STATUS/` holds the current workspace snapshot and orchestrator view.\n"
        "- `01_AGENT_INBOXES/` holds per-agent note folders and generated inboxes.\n"
        "- `02_ACTIVE_THREADS/` holds one folder per active front or hot region.\n"
        "- `03_CLAIMS/` holds human-readable claim cards and the merged claims summary.\n"
        "- `04_CHANGE_FEED/` holds recent file-change observations and event history.\n"
        "- `05_SYNTHESIS/` holds whole-project and cross-region synthesis documents.\n"
        "- `06_PROTOCOLS/` explains how the board should be used.\n"
        "- `07_TENSOR/` holds family tensor, thread coordinates, archetype, pantheon, cluster, and neuron-lattice projections.\n"
        "- `08_SWARM_RUNTIME/` holds kernel, elementals, ganglia, rails, archetypes, councils, pods, neurons, hypergraph, waves, manifests, and cortex summaries.\n\n"
        "## Canonical Rule\n\n"
        "New work should claim a frontier here before it expands. The goal is one shared place "
        "where agents can see what is active, what changed, how it is located in the swarm tensor, "
        "and what should not be duplicated.\n\n"
        "## Organism Center\n\n"
        "The live board is the coordination plexus, not the whole-organism map.\n"
        "The current representational center lives at "
        "`self_actualize/mycelium_brain/MASTER_MYCELIUM_MAP_ATHENA/00_MASTER_MYCELIUM_MAP_ATHENA.md`.\n"
    )


def render_protocol_doc() -> str:
    return (
        "# How To Use The Realtime Swarm Board\n\n"
        "## Primary Commands\n\n"
        "```powershell\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 build\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 watch --interval 2.0\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 emit \"ATHENA/READ ME.txt\" --change-type modified\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 route EVT-20260313-0001\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 claim EVT-20260313-0001 --lease-ms 1200\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 commit EVT-20260313-0001 --result success\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 reinforce EVT-20260313-0001 --result success --latency-score 0.94\n"
        "python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 status\n"
        "python -m self_actualize.runtime.swarm_board build\n"
        "python -m self_actualize.runtime.swarm_board note --agent codex --front \"archive promotion\" --message \"Investigating archive-backed framework landing zone\"\n"
        "python -m self_actualize.runtime.swarm_board claim --agent codex --front \"archive promotion\" --level framework --output-target \"MATH extracted tree\" --receipt \"receipt pending\" --status active --message \"Claiming archive promotion front\"\n"
        "```\n\n"
        "## Operating Rule\n\n"
        "1. Run the COMMAND membrane watcher first for `GLOBAL COMMAND`, then refresh the board.\n"
        "2. Read `03_CLAIMS/00_ACTIVE_CLAIMS.md`, `07_TENSOR/01_FAMILY_TENSOR_FIELD.md`, `07_TENSOR/05_ARCHETYPE_GRID.md`, and `08_SWARM_RUNTIME/manifests/ACTIVE_RUN.md`.\n"
        "3. Treat `GLOBAL COMMAND` as a sensory membrane: `detect -> encode -> route -> claim -> commit -> reinforce`.\n"
        "4. Use manual frontier claims only for non-command board work.\n"
        "5. Leave at least one note or claim card before going deep.\n"
        "6. Make sure every serious front has a family owner, rail, packet class, truth class, contraction target, archetype cell, cluster, and truth leaf.\n"
        "7. Land a receipt or change the claim status when the artifact is done.\n"
        "8. Update the next self prompt so the loop restarts from the beginning.\n\n"
        "## No-Duplication Rule\n\n"
        "If a frontier is already `active`, take a validation or receipt role unless the owner has explicitly handed it off.\n\n"
        "## COMMAND Law\n\n"
        "The canonical routing policy is `goal+salience+pheromone+coord`, claim mode is `first-lease`, `Sigma` remains `AppA/AppI/AppM`, and the hub budget remains `<= 6`.\n"
    )


def render_status_doc(
    snapshot: dict[str, Any],
    diff: dict[str, Any],
    atlas_metrics: dict[str, Any],
    docs_gate: dict[str, Any],
    queue: dict[str, list[str]],
    all_claims: dict[str, dict[str, Any]],
    notes: list[dict[str, Any]],
    events: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    neurons: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    active_run: dict[str, Any],
    kernel_state: dict[str, Any],
    councils: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    neuron_lattice: list[dict[str, Any]],
    hypergraph: dict[str, Any],
    command_state: dict[str, Any],
) -> str:
    active_claims = [claim for claim in all_claims.values() if claim.get("status") in OPEN_STATUSES]
    recent_events = events[-5:]
    hot_regions = list(snapshot["by_top_level"].items())[:8]
    queue_lines = []
    for bucket in ("P0", "P1", "P2"):
        for item in queue.get(bucket, [])[:4]:
            queue_lines.append(f"- `{bucket}` {item}")
    if not queue_lines:
        queue_lines.append("- queue unavailable")

    event_lines = []
    for event in reversed(recent_events):
        summary = event.get("summary", {})
        event_lines.append(
            f"- `{event.get('detected_at', 'unknown')}` "
            f"+{summary.get('added', 0)} ~{summary.get('modified', 0)} -{summary.get('removed', 0)}"
        )
    if not event_lines:
        event_lines.append("- no prior board events")

    region_lines = []
    for name, count in hot_regions:
        region_lines.append(f"- `{name}`: `{count}` visible files")

    command_lines = [
        f"- Watcher mode: `{command_state.get('watcher_mode', 'unknown')}`",
        f"- Active leases: `{len(command_state.get('active_leases', []))}`",
        f"- Last event: `{(command_state.get('last_event') or {}).get('event_id', 'none')}`",
        f"- Top capillary count: `{len(command_state.get('top_capillaries', []))}`",
    ]
    latency = command_state.get("latency_summary", {})
    if latency:
        command_lines.extend(
            [
                f"- `T_sugar`: `{latency.get('T_sugar_ms', 0.0)}` ms",
                f"- Duplicate suppression: `{latency.get('duplicate_suppression_rate', 0.0)}`",
                f"- Route win rate: `{latency.get('route_win_rate', 0.0)}`",
            ]
        )

    return (
        "# Board Status\n\n"
        f"- Generated: `{snapshot['generated_at']}`\n"
        f"- Board witness (workspace scan): `{snapshot['file_count']}`\n"
        f"- Indexed witness (live atlas): `{atlas_metrics['live_record_count']}`\n"
        f"- Archive witness (archive atlas): `{atlas_metrics['archive_record_count']}` across `{atlas_metrics['archive_count']}` archives\n"
        f"- Change batch: `+{diff['added']} ~{diff['modified']} -{diff['removed']}`\n"
        f"- Notes on board: `{len(notes)}`\n"
        f"- Open claims: `{len(active_claims)}`\n"
        f"- Pods: `{len(pods)}`\n"
        f"- Bridge neurons: `{len(neurons)}`\n"
        f"- Waves: `{len(waves)}`\n"
        f"- Councils: `{len(councils)}`\n"
        f"- Occupied clusters: `{sum(1 for item in clusters if item['occupancy'])}` of `{len(clusters)}`\n"
        f"- Occupied truth leaves: `{sum(1 for item in neuron_lattice if item['occupancy'])}` of `{len(neuron_lattice)}`\n"
        f"- Legacy hypergraph edges: `{hypergraph['edge_count']}`\n"
        f"- Live Docs gate: `{docs_gate['status']}`\n"
        f"- Docs detail: {docs_gate['detail']}\n\n"
        "## Global Read\n\n"
        "The workspace is already a multi-body organism and the board now treats it as a higher-dimensional swarm: "
        "kernel, elementals, archetypes, pantheon, clusters, truth leaves, ganglia, councils, pods, neurons, waves, and manifests now all project into one live board. "
        "The older machine-readable swarm is folded in rather than ignored: the board is carrying the legacy hypergraph, council mesh, frontier gaps, and civilization tiers forward into the current control plane. "
        "Voynich remains the densest live manuscript engine, MATH remains the deepest formal reservoir, DEEPER CRYSTALIZATION remains the integration compiler, "
        "self_actualize remains the runtime waist, Trading Bot remains the blocked external-memory bridge, and ECOSYSTEM remains the governance shell. "
        "The highest leverage move is therefore coordination that prevents those bodies from rediscovering each other every run while still preserving the real blocked gate.\n\n"
        "## Active Run\n\n"
        f"- Chosen front: `{active_run['chosen_front']}`\n"
        f"- Chosen family: `{active_run['chosen_family']}`\n"
        f"- Pivot front: `{active_run['pivot_front']}`\n"
        f"- Chosen NSCoord: `{active_run['chosen_nscoord']}`\n\n"
        "## Kernel Read\n"
        f"- Kernel: `{kernel_state['kernel_id']}`\n"
        f"- Relay interfaces: `{len(kernel_state['relay_interfaces'])}`\n"
        f"- Frontier gaps preserved: `{kernel_state['frontier_gap_count']}`\n\n"
        "## COMMAND Membrane\n"
        + "\n".join(command_lines)
        + "\n\n"
        "## Hot Regions\n"
        + "\n".join(region_lines)
        + "\n\n## Queue Pressure\n"
        + "\n".join(queue_lines)
        + "\n\n## Recent Board Events\n"
        + "\n".join(event_lines)
        + "\n"
    )


def render_change_feed(diff: dict[str, Any], events: list[dict[str, Any]], command_state: dict[str, Any]) -> str:
    change_lines = []
    for change in diff.get("changes", [])[:60]:
        change_lines.append(
            f"- `{change['kind']}` `{change['relative_path']}` at `{change['mtime_iso']}`"
        )
    if not change_lines:
        change_lines.append("- no workspace changes detected since the previous snapshot")

    event_lines = []
    for event in reversed(events[-12:]):
        summary = event.get("summary", {})
        event_lines.append(
            f"- `{event.get('detected_at', 'unknown')}` "
            f"+{summary.get('added', 0)} ~{summary.get('modified', 0)} -{summary.get('removed', 0)}"
        )
    if not event_lines:
        event_lines.append("- no event history yet")

    command_lines = []
    recent_command_events = command_state.get("recent_events", [])
    if recent_command_events:
        for event in reversed(recent_command_events[-6:]):
            command_lines.append(
                f"- `{event.get('event_id', 'none')}` `{event.get('event_tag', '')}` "
                f"`{event.get('relative_path', '')}` -> `{event.get('change_summary', '')}`"
            )
    else:
        command_lines.append("- no COMMAND membrane events yet")
    latency = command_state.get("latency_summary", {})
    if latency:
        command_lines.append(f"- `T_sugar`: `{latency.get('T_sugar_ms', 0.0)}` ms")
        command_lines.append(f"- Active leases: `{len(command_state.get('active_leases', []))}`")
        command_lines.append(f"- Route win rate: `{latency.get('route_win_rate', 0.0)}`")

    return (
        "# Change Feed\n\n"
        "## Current Batch\n"
        + "\n".join(change_lines)
        + "\n\n## Event History\n"
        + "\n".join(event_lines)
        + "\n\n## COMMAND Membrane\n"
        + "\n".join(command_lines)
        + "\n"
    )


def render_claim_summary(all_claims: dict[str, dict[str, Any]]) -> str:
    claims = sorted(
        all_claims.values(),
        key=lambda item: (
            item.get("status") not in OPEN_STATUSES,
            item.get("updated_at") or "",
            item["claim_id"],
        ),
        reverse=True,
    )
    rows = [
        "| Claim ID | Frontier | Level | Owner | Status | Output Target | Source |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for claim in claims:
        rows.append(
            "| "
            + " | ".join(
                [
                    claim["claim_id"],
                    claim["frontier"],
                    claim.get("level", ""),
                    claim.get("owner", ""),
                    claim.get("status", ""),
                    claim.get("output_target", ""),
                    claim.get("source", ""),
                ]
            )
            + " |"
        )
    return "# Active Claims\n\n" + "\n".join(rows) + "\n"


def render_agent_index(notes: list[dict[str, Any]], all_claims: dict[str, dict[str, Any]]) -> str:
    agent_counts: Counter[str] = Counter(note["agent"] for note in notes)
    claim_counts: Counter[str] = Counter(
        claim["owner"] for claim in all_claims.values() if claim.get("status") in OPEN_STATUSES
    )
    agents = sorted(set(agent_counts) | set(claim_counts))
    lines = ["# Agent Inboxes", ""]
    for agent in agents:
        agent_slug = slugify(agent)
        lines.append(
            f"- `{agent}`: `{agent_counts[agent]}` notes, `{claim_counts[agent]}` open claims, "
            f"`01_AGENT_INBOXES/{agent_slug}/INBOX.md`"
        )
    if len(lines) == 2:
        lines.append("- no agent notes or claims yet")
    lines.append("")
    return "\n".join(lines)


def render_agent_inbox(agent: str, notes: list[dict[str, Any]], claims: list[dict[str, Any]]) -> str:
    note_lines = [
        f"- `{note['updated_at']}` `{note['front']}` -> `{note['status']}` "
        f"(`{note['md_path'].relative_to(BOARD_ROOT).as_posix()}`)"
        for note in notes[:20]
    ]
    if not note_lines:
        note_lines.append("- no notes yet")
    claim_lines = [
        f"- `{claim.get('status', '')}` `{claim['frontier']}` -> `{claim.get('output_target', '')}`"
        for claim in claims[:20]
    ]
    if not claim_lines:
        claim_lines.append("- no claims yet")
    return (
        f"# Inbox `{agent}`\n\n"
        "## Claims\n"
        + "\n".join(claim_lines)
        + "\n\n## Notes\n"
        + "\n".join(note_lines)
        + "\n"
    )


def render_thread_index(threads: list[dict[str, Any]]) -> str:
    lines = ["# Active Threads", ""]
    for thread in threads:
        lines.append(
            f"- `{thread['front']}`: `{thread['status']}`, `{thread['note_count']}` notes, "
            f"`{thread['claim_count']}` claims, `{thread['change_count']}` tracked changes"
        )
    if len(lines) == 2:
        lines.append("- no active threads yet")
    lines.append("")
    return "\n".join(lines)


def render_thread_doc(thread: dict[str, Any]) -> str:
    claim_lines = [
        f"- `{claim['claim_id']}` `{claim.get('status', '')}` by `{claim.get('owner', '')}` -> `{claim.get('output_target', '')}`"
        for claim in thread["claims"][:20]
    ]
    if not claim_lines:
        claim_lines.append("- no claims attached")

    note_lines = [
        f"- `{note['updated_at']}` `{note['agent']}` -> `{note['status']}` "
        f"(`{note['md_path'].relative_to(BOARD_ROOT).as_posix()}`)"
        for note in thread["notes"][:20]
    ]
    if not note_lines:
        note_lines.append("- no notes attached")

    change_lines = [
        f"- `{change['kind']}` `{change['relative_path']}` at `{change['mtime_iso']}`"
        for change in thread["changes"][:25]
    ]
    if not change_lines:
        change_lines.append("- no current file changes tied to this thread")

    command_section = ""
    if thread["front"] == "GLOBAL COMMAND":
        command_state = load_command_membrane_state()
        last_event = command_state.get("last_event") or {}
        latency = command_state.get("latency_summary", {})
        command_lines = [
            f"- Watcher mode: `{command_state.get('watcher_mode', 'unknown')}`",
            f"- Last event: `{last_event.get('event_id', 'none')}`",
            f"- Last path: `{last_event.get('relative_path', 'none')}`",
            f"- Active leases: `{len(command_state.get('active_leases', []))}`",
            f"- `T_sugar`: `{latency.get('T_sugar_ms', 0.0)}` ms",
        ]
        command_section = "\n## Command Membrane\n" + "\n".join(command_lines)

    return (
        f"# Thread `{thread['front']}`\n\n"
        f"- Thread status: `{thread['status']}`\n"
        f"- Notes: `{thread['note_count']}`\n"
        f"- Claims: `{thread['claim_count']}`\n"
        f"- Tracked changes: `{thread['change_count']}`\n"
        f"- Family: `{thread.get('family', 'unknown')}`\n"
        f"- ArchetypeCell: `{thread.get('archetype_cell', 'unknown')}`\n"
        f"- ArchetypeRole: {thread.get('archetype_role', 'unknown')}\n"
        f"- MicroMode: `{thread.get('micro_mode', 'unknown')}`\n"
        f"- ClusterID: `{thread.get('cluster_id', 'unknown')}`\n"
        f"- NeuronLeaf: `{thread.get('neuron_leaf', 'unknown')}`\n"
        f"- Rail: `{thread.get('rail', 'unknown')}`\n"
        f"- Face: `{thread.get('face', 'unknown')}`\n"
        f"- Scale: `{thread.get('scale', 'unknown')}`\n"
        f"- Hub: `{thread.get('hub', 'unknown')}`\n"
        f"- Regime: `{thread.get('regime', 'unknown')}`\n"
        f"- Packet: `{thread.get('packet', 'unknown')}`\n"
        f"- Truth: `{thread.get('truth', 'unknown')}`\n"
        f"- NSCoord: `{thread.get('nscoord', 'unknown')}`\n"
        f"- NeuronAddr: `{thread.get('neuron_addr', 'unknown')}`\n"
        f"- ContractionTarget: `{thread.get('contraction_target', 'unknown')}`\n\n"
        "## Claims\n"
        + "\n".join(claim_lines)
        + "\n\n## Notes\n"
        + "\n".join(note_lines)
        + "\n\n## Related Changes\n"
        + "\n".join(change_lines)
        + command_section
        + "\n"
    )


def render_global_synthesis(
    snapshot: dict[str, Any],
    atlas_metrics: dict[str, Any],
    docs_gate: dict[str, Any],
    queue: dict[str, list[str]],
    command_state: dict[str, Any],
) -> str:
    region_lines = []
    sorted_regions = sorted(
        snapshot["by_top_level"].items(),
        key=lambda item: (-item[1], top_level_sort_key(item[0])),
    )
    for name, count in sorted_regions[:10]:
        profile = REGION_PROFILES.get(name)
        if profile:
            region_lines.append(
                f"- `{name}` `{count}` files: {profile['role']}. Pressure point: {profile['risk']}"
            )
        else:
            region_lines.append(f"- `{name}` `{count}` files: visible region without a custom profile yet.")

    queue_pressure = queue.get("P0", [])[:3] + queue.get("P1", [])[:3]
    queue_lines = [f"- {item}" for item in queue_pressure] or ["- queue unavailable"]
    command_summary = (
        f"The `GLOBAL COMMAND` ingress is now paired with a COMMAND membrane witness in mode "
        f"`{command_state.get('watcher_mode', 'unknown')}` carrying "
        f"`{len(command_state.get('active_leases', []))}` active leases and "
        f"`{len(command_state.get('top_capillaries', []))}` reinforced capillaries. "
        f"That means first-touch awareness is no longer just the board poll loop."
    )

    return (
        "# Global Orchestration Synthesis\n\n"
        "The project is not a single manuscript and not a single codebase. It is a compound organism with four main bodies:\n\n"
        "1. live manuscript execution (`Voynich`, `DEEPER CRYSTALIZATION`, `FRESH`)\n"
        "2. formal and archive depth (`MATH` plus ZIP-backed frameworks)\n"
        "3. runtime and retrieval (`self_actualize`, `Trading Bot`, `NERUAL NETWORK`)\n"
        "4. governance and publication (`ECOSYSTEM`, `Athenachka Collective Books`)\n\n"
        "The live atlas now sees "
        f"`{atlas_metrics['live_record_count']}` local records, while the archive atlas exposes "
        f"`{atlas_metrics['archive_record_count']}` additional hidden records. That means the active problem is no longer lack of material. "
        "The active problem is collision management, promotion discipline, and keeping the local and archive bodies in one shared route space.\n\n"
        "The strongest cross-synthesis is this: the repo already knows how to think in queues, claims, receipts, chapters, metro lines, and swarms. "
        "What it lacked was a live board where those abstractions could become the everyday operating surface for many agents at once.\n\n"
        + command_summary
        + "\n\n"
        "The current hard external gate remains "
        f"`{docs_gate['status']}`. Until Google Docs is unlocked, the board should treat local markdown and archive-backed evidence as the primary memory body, "
        "and it should record exact blocked queries instead of pretending the live side is available.\n\n"
        "## Region Read\n"
        + "\n".join(region_lines)
        + "\n\n## Current Pressure Fronts\n"
        + "\n".join(queue_lines)
        + "\n"
    )


def render_region_matrix(snapshot: dict[str, Any]) -> str:
    lines = ["# Cross-Region Matrix", ""]
    for name in sorted(snapshot["by_top_level"], key=top_level_sort_key):
        profile = REGION_PROFILES.get(name)
        count = snapshot["by_top_level"][name]
        lines.append(f"## {name}")
        lines.append(f"- Visible files: `{count}`")
        if not profile:
            lines.append("- Role: emergent region")
            lines.append("- Primary edges: not profiled yet")
            lines.append("- Failure mode: unknown")
            lines.append("")
            continue
        lines.append(f"- Role: {profile['role']}")
        for edge in profile["edges"]:
            lines.append(f"- Edge: {edge}")
        lines.append(f"- Failure mode: {profile['risk']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_tensor_overview() -> str:
    return (
        "# Higher-Dimensional Tensor Overview\n\n"
        "The board is a projection surface for the swarm tensor.\n\n"
        "## Coordinate Bundle\n\n"
        "`NSCoord = (Addr4, Scale, Face6, Orbit, Arc, Rail, Hub, Family, Regime, Packet, Truth)`\n\n"
        "## Swarm Tensor\n\n"
        "`SwarmTensor = (Kernel, Elementals, Archetypes, Pantheon, Clusters, Neurons, Families, Waves, Ledgers, Cortex)`\n\n"
        "## Canonical Rule\n\n"
        "No serious front is fully located until it has a family owner, rail, hub, regime, packet class, truth class, and contraction target.\n"
    )


def render_swarm_tensor_stack(
    kernel_state: dict[str, Any],
    elemental_field: list[dict[str, Any]],
    archetypes: list[dict[str, Any]],
    pantheon: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    neuron_lattice: list[dict[str, Any]],
    councils: list[dict[str, Any]],
) -> str:
    return (
        "# Swarm Tensor Stack\n\n"
        "This board pass explicitly projects the deeper swarm stack into live files.\n\n"
        f"- Kernel: `1` shared zero point (`{kernel_state['kernel_id']}`)\n"
        f"- Elementals: `{len(elemental_field)}` pillars\n"
        f"- Archetypes: `{len(archetypes)}` crystal cells\n"
        f"- Pantheon: `{len(pantheon)}` off-diagonal cells\n"
        f"- Clusters: `{len(clusters)}` task fields\n"
        f"- Neuron leaves: `{len(neuron_lattice)}` truth-addressable microcells\n"
        f"- Councils: `{len(councils)}` family and rail councils\n"
        f"- Legacy hypergraph edges preserved: `{kernel_state['hypergraph_edges']}`\n"
    )


def render_family_tensor_doc(family_tensor: list[dict[str, Any]]) -> str:
    rows = [
        "| Family | Weight | PrimaryRail | PrimaryFace | PreferredScale | PrimaryHub | PreferredRegime | BestFront | PrimaryGanglion | Lineage | Truth | AbsorbedSurfaces |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in family_tensor:
        absorbed = ", ".join(f"`{name}`" for name in item.get("absorbed_surfaces", [])) or "none"
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{item['family']}`",
                    f"`{item['weight']}`",
                    f"`{item['primary_rail']}`",
                    f"`{item['primary_face']}`",
                    f"`{item['preferred_scale']}`",
                    f"`{item['primary_hub']}`",
                    f"`{item['preferred_regime']}`",
                    item["best_front"],
                    f"`{item['primary_ganglion']}`",
                    f"`{item['lineage']}`",
                    f"`{item['truth']}`",
                    absorbed,
                ]
            )
            + " |"
        )
    return "# Family Tensor Field\n\n" + "\n".join(rows) + "\n"

def render_thread_coordinates_doc(threads: list[dict[str, Any]]) -> str:
    lines = ["# Thread Coordinates", ""]
    for thread in threads:
        lines.append(f"## {thread['front']}")
        lines.append(f"- Family: `{thread['family']}`")
        lines.append(f"- ArchetypeCell: `{thread['archetype_cell']}`")
        lines.append(f"- ArchetypeRole: {thread['archetype_role']}")
        lines.append(f"- MicroMode: `{thread['micro_mode']}`")
        lines.append(f"- ClusterID: `{thread['cluster_id']}`")
        lines.append(f"- NeuronLeaf: `{thread['neuron_leaf']}`")
        lines.append(f"- Rail: `{thread['rail']}`")
        lines.append(f"- Face: `{thread['face']}`")
        lines.append(f"- Scale: `{thread['scale']}`")
        lines.append(f"- Hub: `{thread['hub']}`")
        lines.append(f"- Regime: `{thread['regime']}`")
        lines.append(f"- Packet: `{thread['packet']}`")
        lines.append(f"- Truth: `{thread['truth']}`")
        lines.append(f"- NSCoord: `{thread['nscoord']}`")
        lines.append(f"- NeuronAddr: `{thread['neuron_addr']}`")
        lines.append(f"- ContractionTarget: `{thread['contraction_target']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_transfer_hubs_doc(neurons: list[dict[str, Any]]) -> str:
    lines = ["# Transfer Hubs", ""]
    for neuron in neurons:
        lines.append(f"## {neuron['src_family']} -> {neuron['dst_family']}")
        lines.append(f"- Hub: `{neuron['hub']}`")
        lines.append(f"- Operator: {neuron['operator']}")
        lines.append(f"- Truth: `{neuron['truth_class']}`")
        lines.append(f"- ReplayPath: `{neuron['replay_path']}`")
        if neuron["witness_set"]:
            lines.append("- WitnessSet: " + ", ".join(f"`{item}`" for item in neuron["witness_set"]))
        else:
            lines.append("- WitnessSet: none")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_kernel_doc(kernel_state: dict[str, Any]) -> str:
    lines = [
        "# Kernel Zero Point",
        "",
        "The live board now contracts through a kernel surface instead of only through status pages.",
        "",
        f"- KernelID: `{kernel_state['kernel_id']}`",
        f"- DocsGate: `{kernel_state['docs_gate_status']}`",
        f"- CurrentFront: `{kernel_state['current_front']}`",
        f"- PivotFront: `{kernel_state['pivot_front']}`",
        f"- Threads: `{kernel_state['thread_count']}`",
        f"- Pods: `{kernel_state['pod_count']}`",
        f"- Waves: `{', '.join(kernel_state['wave_ids']) if kernel_state['wave_ids'] else 'none'}`",
        f"- LegacyHypergraphEdges: `{kernel_state['hypergraph_edges']}`",
        f"- LegacyNodeTensorNodes: `{kernel_state['node_tensor_nodes']}`",
        f"- LegacyNerveEdges: `{kernel_state['nerve_edges']}`",
        f"- CivilizationTiers: `{kernel_state['tier_count']}`",
        f"- GovernanceSigns: `{kernel_state['sign_count']}`",
        f"- FrontierGaps: `{kernel_state['frontier_gap_count']}`",
        "",
        "## Relay Interfaces",
    ]
    for relay in kernel_state["relay_interfaces"]:
        lines.append(f"- `{relay['id']}` `{relay['status']}` {relay['notes']}")
    if not kernel_state["relay_interfaces"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_elemental_index(elemental_field: list[dict[str, Any]]) -> str:
    lines = [
        "# Elemental Field",
        "",
        "| Element | Role | Threads | Pods | BridgeNeurons |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in elemental_field:
        lines.append(
            f"| `{item['element']}` | {item['role']} | `{item['thread_count']}` | `{item['pod_count']}` | `{item['neuron_count']}` |"
        )
    return "\n".join(lines) + "\n"


def render_elemental_doc(item: dict[str, Any]) -> str:
    lines = [
        f"# {item['element']}",
        "",
        f"- Role: {item['role']}",
        f"- ThreadCount: `{item['thread_count']}`",
        f"- PodCount: `{item['pod_count']}`",
        f"- BridgeNeuronCount: `{item['neuron_count']}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{front}`" for front in item["thread_ids"][:20])
    if not item["thread_ids"]:
        lines.append("- none")
    lines.extend(["", "## Live Pods"])
    lines.extend(f"- `{pod_id}`" for pod_id in item["pod_ids"][:20])
    if not item["pod_ids"]:
        lines.append("- none")
    lines.extend(["", "## Bridge Neurons"])
    lines.extend(f"- `{node_id}`" for node_id in item["neuron_ids"][:20])
    if not item["neuron_ids"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_archetype_grid_doc(archetypes: list[dict[str, Any]]) -> str:
    lines = [
        "# Archetype Grid",
        "",
        "The 16-cell crystal is the native higher-dimensional swarm basis: four diagonal pillars plus twelve off-diagonal archetype cells.",
        "",
        "| Cell | Role | Threads | Pods | MicroModes | Truths |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in archetypes:
        micro_modes = ", ".join(f"{mode}:{count}" for mode, count in sorted(item["micro_modes"].items())) or "none"
        truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
        lines.append(
            f"| `{item['cell']}` | {item['role']} | `{item['thread_count']}` | `{item['pod_count']}` | `{micro_modes}` | `{truths}` |"
        )
    return "\n".join(lines) + "\n"


def render_archetype_doc(item: dict[str, Any]) -> str:
    micro_modes = ", ".join(f"{mode}:{count}" for mode, count in sorted(item["micro_modes"].items())) or "none"
    truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
    lines = [
        f"# Archetype {item['cell']}",
        "",
        f"- Role: {item['role']}",
        f"- ThreadCount: `{item['thread_count']}`",
        f"- PodCount: `{item['pod_count']}`",
        f"- MicroModes: `{micro_modes}`",
        f"- Truths: `{truths}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{front}`" for front in item["thread_ids"][:20])
    if not item["thread_ids"]:
        lines.append("- none")
    lines.extend(["", "## Live Pods"])
    lines.extend(f"- `{pod_id}`" for pod_id in item["pod_ids"][:20])
    if not item["pod_ids"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_pantheon_doc(pantheon: list[dict[str, Any]]) -> str:
    lines = [
        "# Pantheon Overlay",
        "",
        "The twelve off-diagonal cells are the archetype pantheon. They are where mixed swarm behaviors specialize without collapsing back to the four pillars.",
        "",
    ]
    for item in pantheon:
        lines.append(f"## {item['cell']}")
        lines.append(f"- Role: {item['role']}")
        lines.append(f"- Threads: `{item['thread_count']}`")
        lines.append(f"- Pods: `{item['pod_count']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_cluster_field_doc(clusters: list[dict[str, Any]]) -> str:
    lines = [
        "# Cluster Field",
        "",
        "The 64-node layer is the 16-cell crystal split again by the four elemental micro-modes.",
        "",
        f"- Total clusters: `{len(clusters)}`",
        f"- Occupied clusters: `{sum(1 for item in clusters if item['occupancy'])}`",
        "",
        "## Most active clusters",
    ]
    active_clusters = [item for item in clusters if item["occupancy"]][:24]
    for item in active_clusters:
        truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
        lines.append(
            f"- `{item['cluster_id']}` -> `{item['cell']}` / `{item['micro_mode']}` / occupancy=`{item['occupancy']}` / truths=`{truths}`"
        )
    if not active_clusters:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_neuron_lattice_doc(neuron_lattice: list[dict[str, Any]]) -> str:
    lines = [
        "# Neuron Lattice",
        "",
        "The 256-leaf layer is the 64-node cluster field split again by corridor truth. This is the full 4^4 closure used here: archetype cell x micro-mode x truth class.",
        "",
        f"- Total leaves: `{len(neuron_lattice)}`",
        f"- Occupied leaves: `{sum(1 for item in neuron_lattice if item['occupancy'])}`",
        "",
        "## Active leaves",
    ]
    active_leaves = [item for item in neuron_lattice if item["occupancy"]][:40]
    for item in active_leaves:
        lines.append(
            f"- `{item['leaf_id']}` -> cell=`{item['cell']}` mode=`{item['micro_mode']}` truth=`{item['truth']}` "
            f"threads=`{len(item['thread_ids'])}` bridge_neurons=`{len(item['neuron_ids'])}`"
        )
    if not active_leaves:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_council_index(councils: list[dict[str, Any]]) -> str:
    lines = ["# Council Mesh", ""]
    for council in councils:
        target = council["rail"] or council["family"] or council["id"]
        lines.append(
            f"- `{council['id']}` scope=`{council['scope']}` target=`{target}` live_threads=`{len(council['live_threads'])}` frontier_gaps=`{len(council['frontier_hits'])}`"
        )
    if len(lines) == 2:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_council_doc(council: dict[str, Any]) -> str:
    sign_labels = ", ".join(council["sign_labels"]) or "none"
    lines = [
        f"# {council['id']}",
        "",
        f"- Scope: `{council['scope']}`",
        f"- Label: {council['label']}",
        f"- Family: `{council['family'] or 'n/a'}`",
        f"- Rail: `{council['rail'] or 'n/a'}`",
        f"- ChapterTargets: `{', '.join(council['chapter_targets']) or 'none'}`",
        f"- Signs: `{sign_labels}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{thread['status']}` `{thread['front']}` ({thread['family']})" for thread in council["live_threads"][:20])
    if not council["live_threads"]:
        lines.append("- none")
    lines.extend(["", "## Frontier Gaps"])
    for frontier in council["frontier_hits"]:
        lines.append(f"- `{frontier['chapter']}` {frontier['title']}")
    if not council["frontier_hits"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_hypergraph_overview(hypergraph: dict[str, Any]) -> str:
    lines = [
        "# Hypergraph Overview",
        "",
        f"- LegacySources: `{hypergraph['source_count']}`",
        f"- LegacyEdges: `{hypergraph['edge_count']}`",
        f"- LiveThreads: `{hypergraph['live_thread_count']}`",
        f"- LiveBridgeNeurons: `{hypergraph['live_bridge_count']}`",
        f"- Councils: `{hypergraph['council_count']}`",
        f"- FrontierGaps: `{len(hypergraph['frontiers'])}`",
        "",
        "## Top Source Families",
    ]
    for family, count in hypergraph["top_families"]:
        lines.append(f"- `{family}` <- `{count}` source bindings")
    if not hypergraph["top_families"]:
        lines.append("- none")
    lines.extend(["", "## Top Chapters"])
    for chapter, count in hypergraph["top_chapters"]:
        lines.append(f"- `{chapter}` <- `{count}` source bindings")
    if not hypergraph["top_chapters"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_edge_kind_breakdown(hypergraph: dict[str, Any]) -> str:
    lines = ["# Hypergraph Edge Breakdown", ""]
    for kind, count in sorted(hypergraph["edge_kinds"].items()):
        lines.append(f"- `{kind}`: `{count}`")
    if len(lines) == 2:
        lines.append("- none")
    lines.extend(["", "## Top Hubs"])
    for hub, count in hypergraph["top_hubs"]:
        lines.append(f"- `{hub}` <- `{count}` chapter bindings")
    if not hypergraph["top_hubs"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_frontier_gaps_doc(frontiers: list[dict[str, Any]]) -> str:
    lines = [
        "# Frontier Gaps",
        "",
        "These are the structurally visible chapters that the older swarm runtime still marked as under-supported. They are preserved here so the live board can route into genuine gaps instead of redoing saturated work.",
        "",
    ]
    for frontier in frontiers:
        lines.append(f"## {frontier['chapter']} - {frontier['title']}")
        for record in frontier.get("support_records", [])[:10]:
            lines.append(
                f"- `{record['name']}` from `{record['source_layer']}` score=`{record['score']}`"
            )
        if not frontier.get("support_records"):
            lines.append("- no supporting records listed")
        lines.append("")
    if len(lines) == 4:
        lines.append("- none")
    return "\n".join(lines).strip() + "\n"


def render_swarm_runtime_overview(
    pods: list[dict[str, Any]],
    neurons: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    councils: list[dict[str, Any]],
    hypergraph: dict[str, Any],
) -> str:
    return (
        "# Swarm Runtime Overview\n\n"
        "This runtime treats the workspace as a federated swarm.\n\n"
        f"- Pods: `{len(pods)}`\n"
        f"- Bridge neurons: `{len(neurons)}`\n"
        f"- Active waves: `{len(waves)}`\n\n"
        f"- Councils: `{len(councils)}`\n"
        f"- Hypergraph edges in legacy runtime: `{hypergraph['edge_count']}`\n\n"
        "Every promoted front should leave a pod, a truth class, a contraction target, and a restart seed.\n"
    )


def render_ganglion_doc(item: dict[str, Any], threads: list[dict[str, Any]]) -> str:
    family_threads = [thread for thread in threads if thread["family"] == item["family"]]
    lines = [
        f"# Ganglion `{item['family']}`",
        "",
        f"- Weight: `{item['weight']}`",
        f"- PrimaryRail: `{item['primary_rail']}`",
        f"- PrimaryFace: `{item['primary_face']}`",
        f"- PreferredScale: `{item['preferred_scale']}`",
        f"- PrimaryHub: `{item['primary_hub']}`",
        f"- PreferredRegime: `{item['preferred_regime']}`",
        f"- BestFront: {item['best_front']}",
        "",
        "## Local Threads",
    ]
    if family_threads:
        lines.extend(
            f"- `{thread['status']}` `{thread['front']}` -> `{thread['packet']}` / `{thread['truth']}`"
            for thread in family_threads[:15]
        )
    else:
        lines.append("- no active localized threads")
    lines.append("")
    return "\n".join(lines)


def render_rail_doc(rail_code: str, family_tensor: list[dict[str, Any]], threads: list[dict[str, Any]]) -> str:
    meta = RAIL_DESCRIPTIONS[rail_code]
    families = [item for item in family_tensor if item["primary_rail"] == rail_code]
    owned_threads = [thread for thread in threads if thread["rail"] == rail_code]
    lines = [
        f"# {rail_code} Rail",
        "",
        f"- Name: `{meta['name']}`",
        f"- Role: {meta['role']}",
        "",
        "## Families",
    ]
    lines.extend(f"- `{item['family']}` -> `{item['best_front']}`" for item in families)
    if not families:
        lines.append("- none")
    lines.extend(["", "## Active Threads"])
    lines.extend(f"- `{thread['status']}` `{thread['front']}` ({thread['family']})" for thread in owned_threads[:20])
    if not owned_threads:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_pod_doc(pod: dict[str, Any]) -> str:
    agents = ", ".join(f"`{agent}`" for agent in pod["agents"] if agent) or "none"
    return (
        f"# {pod['pod_id']}\n\n"
        f"- Frontier: `{pod['frontier']}`\n"
        f"- Family: `{pod['family']}`\n"
        f"- ArchetypeCell: `{pod['archetype_cell']}`\n"
        f"- ArchetypeRole: {pod['archetype_role']}\n"
        f"- MicroMode: `{pod['micro_mode']}`\n"
        f"- ClusterID: `{pod['cluster_id']}`\n"
        f"- NeuronLeaf: `{pod['neuron_leaf']}`\n"
        f"- Rail: `{pod['rail']}`\n"
        f"- Status: `{pod['status']}`\n"
        f"- Truth: `{pod['truth']}`\n"
        f"- Hub: `{pod['hub']}`\n"
        f"- Regime: `{pod['regime']}`\n"
        f"- Agents: {agents}\n"
        f"- ContractionTarget: `{pod['contraction_target']}`\n"
        f"- NSCoord: `{pod['nscoord']}`\n"
    )


def render_neuron_doc(neuron: dict[str, Any]) -> str:
    witnesses = ", ".join(f"`{item}`" for item in neuron["witness_set"]) or "none"
    return (
        f"# {neuron['node_id']}\n\n"
        f"- SrcFamily: `{neuron['src_family']}`\n"
        f"- DstFamily: `{neuron['dst_family']}`\n"
        f"- ArchetypeCell: `{neuron['archetype_cell']}`\n"
        f"- ArchetypeRole: {neuron['archetype_role']}\n"
        f"- MicroMode: `{neuron['micro_mode']}`\n"
        f"- ClusterID: `{neuron['cluster_id']}`\n"
        f"- NeuronLeaf: `{neuron['neuron_leaf']}`\n"
        f"- Hub: `{neuron['hub']}`\n"
        f"- Truth: `{neuron['truth_class']}`\n"
        f"- Operator: {neuron['operator']}\n"
        f"- ReplayPath: `{neuron['replay_path']}`\n"
        f"- WitnessSet: {witnesses}\n"
    )


def render_wave_doc(wave: dict[str, Any]) -> str:
    pods = ", ".join(f"`{item}`" for item in wave["active_pods"]) or "none"
    writebacks = "\n".join(f"- `{item}`" for item in wave["writeback_set"])
    return (
        f"# {wave['wave_id']}\n\n"
        f"- Goal: {wave['goal']}\n"
        f"- GateStatus: `{wave['gate_status']}`\n"
        f"- ActivePods: {pods}\n"
        f"- SharedKernel: `{wave['shared_kernel']}`\n"
        f"- StopCondition: {wave['stop_condition']}\n"
        f"- RestartSeed: {wave['restart_seed']}\n\n"
        "## Writeback Set\n"
        f"{writebacks}\n"
    )


def render_active_run_doc(active_run: dict[str, Any]) -> str:
    frontier_lines = "\n".join(f"- {item}" for item in active_run["frontier_update"]) or "- none"
    verify_lines = "\n".join(f"- {item}" for item in active_run["verification_summary"])
    command_membrane = active_run.get("command_membrane", {})
    return (
        "# Active Run\n\n"
        f"- GateStatus: `{active_run['gate_status']}`\n"
        f"- ChosenFront: `{active_run['chosen_front']}`\n"
        f"- ChosenFamily: `{active_run['chosen_family']}`\n"
        f"- ChosenNSCoord: `{active_run['chosen_nscoord']}`\n"
        f"- PivotFront: `{active_run['pivot_front']}`\n"
        f"- PivotFamily: `{active_run['pivot_family']}`\n"
        f"- PivotNSCoord: `{active_run['pivot_nscoord']}`\n"
        f"- ArtifactDelta: `{active_run['artifact_delta']}`\n\n"
        "## VerificationSummary\n"
        f"{verify_lines}\n\n"
        "## FrontierUpdate\n"
        f"{frontier_lines}\n\n"
        "## CommandMembrane\n"
        f"- WatcherMode: `{command_membrane.get('watcher_mode', 'unknown')}`\n"
        f"- ActiveLeases: `{command_membrane.get('active_leases', 0)}`\n"
        f"- LastEvent: `{command_membrane.get('last_event_id', 'none')}`\n"
        f"- TopCapillary: `{command_membrane.get('top_capillary', 'none')}`\n"
    )


def render_next_prompt_doc(next_seed: str) -> str:
    return "# Next Self Prompt\n\n## Prompt\n\n```text\n" + next_seed.rstrip() + "\n```\n"


def render_cortex_doc(threads: list[dict[str, Any]], pods: list[dict[str, Any]]) -> str:
    lines = [
        "# Cortex Contraction",
        "",
        "The cortex is the contraction surface for the current swarm pass.",
        "",
        f"- Thread count: `{len(threads)}`",
        f"- Pod count: `{len(pods)}`",
        "",
        "## Strongest reusable fronts",
    ]
    for thread in threads[:10]:
        lines.append(
            f"- `{thread['front']}` -> `{thread['family']}` / `{thread['rail']}` / `{thread['truth']}` / `{thread['contraction_target']}`"
        )
    if len(lines) == 7:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def build_threads(
    notes: list[dict[str, Any]],
    all_claims: dict[str, dict[str, Any]],
    diff: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    thread_map: dict[str, dict[str, Any]] = {}

    def ensure_thread(front: str, kind: str) -> dict[str, Any]:
        slug = slugify(front)
        if slug not in thread_map:
            thread_map[slug] = {
                "front": front,
                "front_slug": slug,
                "kind": kind,
                "notes": [],
                "claims": [],
                "changes": [],
                "note_count": 0,
                "claim_count": 0,
                "change_count": 0,
                "status": "monitor",
                "note_paths": [],
                "claim_paths": [],
            }
        return thread_map[slug]

    for note in notes:
        thread = ensure_thread(note["front"], "front")
        thread["notes"].append(note)
        thread["note_paths"].extend(note.get("paths", []))

    for claim in all_claims.values():
        front = claim.get("frontier") or claim.get("front") or claim["claim_id"]
        thread = ensure_thread(front, "front")
        thread["claims"].append(claim)
        thread["claim_paths"].extend(claim.get("paths", []))

    recent_regions = [name for name, _count in list(snapshot["by_top_level"].items())[:10]]
    for region in recent_regions:
        ensure_thread(region, "region")

    for change in diff.get("changes", []):
        region_thread = ensure_thread(change["top_level"], "region")
        region_thread["changes"].append(change)
        for claim in all_claims.values():
            for path in claim.get("paths", []):
                normalized = path.replace("\\", "/")
                if change["relative_path"].startswith(normalized):
                    front = claim.get("frontier") or claim["claim_id"]
                    front_thread = ensure_thread(front, "front")
                    front_thread["changes"].append(change)
                    break

    threads: list[dict[str, Any]] = []
    for thread in thread_map.values():
        thread["notes"].sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        thread["claims"].sort(key=lambda item: item.get("updated_at") or "", reverse=True)
        dedup_changes = {}
        for change in thread["changes"]:
            dedup_changes[(change["kind"], change["relative_path"])] = change
        thread["changes"] = sorted(dedup_changes.values(), key=lambda item: item["mtime_ns"], reverse=True)
        thread["note_count"] = len(thread["notes"])
        thread["claim_count"] = len(thread["claims"])
        thread["change_count"] = len(thread["changes"])
        open_statuses = {claim.get("status") for claim in thread["claims"]}
        if "active" in open_statuses:
            thread["status"] = "active"
        elif "blocked" in open_statuses:
            thread["status"] = "blocked"
        elif "open" in open_statuses:
            thread["status"] = "open"
        elif "queued" in open_statuses:
            thread["status"] = "queued"
        elif thread["change_count"]:
            thread["status"] = "hot"
        else:
            thread["status"] = "monitor"
        threads.append(thread)

    threads.sort(
        key=lambda item: (
            item["status"] not in {"active", "blocked", "queued", "open", "hot"},
            -item["claim_count"],
            -item["note_count"],
            -item["change_count"],
            item["front_slug"],
        )
    )
    return threads[:40]


def load_event_log() -> list[dict[str, Any]]:
    return read_json(STATE_ROOT / "event_log.json", [])


def update_event_log(snapshot: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    events = load_event_log()
    event = {
        "detected_at": utc_now(),
        "fingerprint": snapshot["fingerprint"],
        "summary": {
            "added": diff["added"],
            "modified": diff["modified"],
            "removed": diff["removed"],
        },
        "changes": diff.get("changes", [])[:40],
    }
    if not events or events[-1].get("fingerprint") != snapshot["fingerprint"]:
        events.append(event)
    events = events[-200:]
    write_json(STATE_ROOT / "event_log.json", events)
    return events


def refresh_board(snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    if snapshot is None:
        snapshot = scan_workspace()
    previous_snapshot = read_json(STATE_ROOT / "last_snapshot.json", None)
    diff = compute_diff(previous_snapshot, snapshot)

    atlas_metrics = read_atlas_metrics()
    docs_gate = docs_gate_status()
    command_state = load_command_membrane_state()
    legacy = load_legacy_manifests()
    queue = parse_queue()
    legacy_claims = parse_legacy_claims()
    board_claims = load_board_claims()
    notes = load_notes()
    all_claims = build_claim_index(board_claims=board_claims, legacy_claims=legacy_claims)
    events = update_event_log(snapshot=snapshot, diff=diff)
    threads = build_threads(notes=notes, all_claims=all_claims, diff=diff, snapshot=snapshot)
    family_tensor = build_family_tensor(snapshot=snapshot, docs_gate=docs_gate)
    threads = annotate_threads(threads=threads, family_tensor=family_tensor, docs_gate=docs_gate)
    pods = build_pods(threads)
    neurons = build_neurons(pods=pods, family_tensor=family_tensor)
    waves = build_waves(pods=pods, docs_gate=docs_gate, diff=diff)
    active_run = build_active_run_manifest(threads=threads, queue=queue, docs_gate=docs_gate, diff=diff, command_state=command_state)
    kernel_state = build_kernel_state(
        threads=threads,
        pods=pods,
        waves=waves,
        active_run=active_run,
        docs_gate=docs_gate,
        legacy=legacy,
        command_state=command_state,
    )
    elemental_field = build_elemental_field(threads=threads, pods=pods, bridge_neurons=neurons)
    archetypes = build_archetype_lattice(threads=threads, pods=pods)
    pantheon = build_pantheon_overlay(archetypes=archetypes)
    clusters = build_cluster_field(threads=threads, pods=pods, bridge_neurons=neurons)
    neuron_lattice = build_neuron_lattice(threads=threads, bridge_neurons=neurons)
    councils = build_council_mesh(legacy=legacy, threads=threads)
    hypergraph = build_hypergraph_projection(
        legacy=legacy,
        threads=threads,
        bridge_neurons=neurons,
        councils=councils,
    )
    next_seed = build_next_seed(active_run=active_run, docs_gate=docs_gate)

    write_text(BOARD_ROOT / "README.md", render_board_readme())
    write_text(PROTOCOL_ROOT / "00_HOW_TO_USE_THIS_BOARD.md", render_protocol_doc())
    write_text(
        STATUS_ROOT / "00_BOARD_STATUS.md",
        render_status_doc(
            snapshot=snapshot,
            diff=diff,
            atlas_metrics=atlas_metrics,
            docs_gate=docs_gate,
            queue=queue,
            all_claims=all_claims,
            notes=notes,
            events=events,
            pods=pods,
            neurons=neurons,
            waves=waves,
            active_run=active_run,
            kernel_state=kernel_state,
            councils=councils,
            clusters=clusters,
            neuron_lattice=neuron_lattice,
            hypergraph=hypergraph,
            command_state=command_state,
        ),
    )
    write_json(STATUS_ROOT / "01_SYSTEM_SNAPSHOT.json", snapshot)
    write_text(CHANGE_ROOT / "00_RECENT_CHANGES.md", render_change_feed(diff=diff, events=events, command_state=command_state))
    write_json(CHANGE_ROOT / "01_CURRENT_BATCH.json", diff)
    write_text(SYNTHESIS_ROOT / "00_GLOBAL_ORCHESTRATION_SYNTHESIS.md", render_global_synthesis(snapshot, atlas_metrics, docs_gate, queue, command_state))
    write_text(SYNTHESIS_ROOT / "01_CROSS_REGION_MATRIX.md", render_region_matrix(snapshot))
    write_text(TENSOR_ROOT / "00_TENSOR_OVERVIEW.md", render_tensor_overview())
    write_text(TENSOR_ROOT / "01_FAMILY_TENSOR_FIELD.md", render_family_tensor_doc(family_tensor))
    write_text(TENSOR_ROOT / "02_THREAD_COORDINATES.md", render_thread_coordinates_doc(threads))
    write_text(TENSOR_ROOT / "03_TRANSFER_HUBS.md", render_transfer_hubs_doc(neurons))
    write_text(
        TENSOR_ROOT / "04_SWARM_TENSOR_STACK.md",
        render_swarm_tensor_stack(kernel_state, elemental_field, archetypes, pantheon, clusters, neuron_lattice, councils),
    )
    write_text(TENSOR_ROOT / "05_ARCHETYPE_GRID.md", render_archetype_grid_doc(archetypes))
    write_text(TENSOR_ROOT / "06_PANTHEON_OVERLAY.md", render_pantheon_doc(pantheon))
    write_text(TENSOR_ROOT / "07_CLUSTER_FIELD.md", render_cluster_field_doc(clusters))
    write_text(TENSOR_ROOT / "08_NEURON_LATTICE.md", render_neuron_lattice_doc(neuron_lattice))
    write_text(BOARD_ROOT / "03_CLAIMS" / "00_ACTIVE_CLAIMS.md", render_claim_summary(all_claims))
    write_text(AGENT_ROOT / "INDEX.md", render_agent_index(notes, all_claims))
    write_text(THREAD_ROOT / "INDEX.md", render_thread_index(threads))
    write_text(SWARM_ROOT / "00_SWARM_RUNTIME_OVERVIEW.md", render_swarm_runtime_overview(pods, neurons, waves, councils, hypergraph))
    write_text(KERNEL_ROOT / "00_KERNEL_ZERO_POINT.md", render_kernel_doc(kernel_state))
    write_text(ELEMENTAL_ROOT / "00_ELEMENTAL_FIELD.md", render_elemental_index(elemental_field))
    for element in elemental_field:
        write_text(ELEMENTAL_ROOT / f"{element['element'].upper()}.md", render_elemental_doc(element))
    write_text(ARCHETYPE_ROOT / "00_ARCHETYPE_GRID.md", render_archetype_grid_doc(archetypes))
    for item in archetypes:
        write_text(ARCHETYPE_ROOT / f"ARCHETYPE_{slugify(item['cell'])}.md", render_archetype_doc(item))
    write_text(PANTHEON_ROOT / "00_PANTHEON_OVERLAY.md", render_pantheon_doc(pantheon))
    write_text(CLUSTER_ROOT / "00_CLUSTER_FIELD.md", render_cluster_field_doc(clusters))
    write_text(COUNCIL_ROOT / "INDEX.md", render_council_index(councils))
    for council in councils:
        write_text(COUNCIL_ROOT / f"{slugify(council['id'])}.md", render_council_doc(council))
    write_text(HYPERGRAPH_ROOT / "00_HYPERGRAPH_OVERVIEW.md", render_hypergraph_overview(hypergraph))
    write_text(HYPERGRAPH_ROOT / "01_EDGE_KIND_BREAKDOWN.md", render_edge_kind_breakdown(hypergraph))
    write_text(HYPERGRAPH_ROOT / "02_FRONTIER_GAPS.md", render_frontier_gaps_doc(hypergraph["frontiers"]))
    write_text(MANIFEST_ROOT / "ACTIVE_RUN.md", render_active_run_doc(active_run))
    write_text(MANIFEST_ROOT / "NEXT_SELF_PROMPT.md", render_next_prompt_doc(next_seed))
    write_json(
        MANIFEST_ROOT / "LOOP_STATE.json",
        {
            "generated_at": utc_now(),
            "gate_status": docs_gate["status"],
            "active_run": active_run,
            "next_seed": next_seed,
            "wave_ids": [wave["wave_id"] for wave in waves],
            "command_membrane": {
                "watcher_mode": command_state.get("watcher_mode", "unknown"),
                "last_event_id": (command_state.get("last_event") or {}).get("event_id", "none"),
                "active_leases": len(command_state.get("active_leases", [])),
            },
        },
    )
    write_text(CORTEX_ROOT / "00_CORTEX_CONTRACTION.md", render_cortex_doc(threads, pods))

    notes_by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    claims_by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note in notes:
        notes_by_agent[note["agent"]].append(note)
    for claim in all_claims.values():
        claims_by_owner[claim.get("owner", "unassigned")].append(claim)

    for agent, agent_notes in notes_by_agent.items():
        agent_slug = slugify(agent)
        inbox_path = AGENT_ROOT / agent_slug / "INBOX.md"
        write_text(inbox_path, render_agent_inbox(agent, agent_notes, claims_by_owner.get(agent, [])))

    for thread in threads:
        thread_dir = THREAD_ROOT / thread["front_slug"]
        write_text(thread_dir / "THREAD.md", render_thread_doc(thread))

    for item in family_tensor:
        write_text(GANGLIA_ROOT / f"GANGLION_{slugify(item['family'])}.md", render_ganglion_doc(item, threads))

    for rail_code in sorted(RAIL_DESCRIPTIONS):
        write_text(RAILS_ROOT / f"{rail_code}_RAIL.md", render_rail_doc(rail_code, family_tensor, threads))

    for pod in pods:
        write_text(POD_ROOT / f"{pod['pod_id']}.md", render_pod_doc(pod))

    for neuron in neurons:
        write_text(NEURON_ROOT / f"{neuron['node_id']}.md", render_neuron_doc(neuron))

    for wave in waves:
        write_text(WAVE_ROOT / f"{wave['wave_id']}.md", render_wave_doc(wave))
        write_json(WAVE_ROOT / f"{wave['wave_id']}.json", wave)

    write_json(STATE_ROOT / "last_snapshot.json", snapshot)
    return {
        "snapshot": snapshot,
        "diff": diff,
        "events": events,
        "thread_count": len(threads),
        "note_count": len(notes),
        "claim_count": len(all_claims),
        "pod_count": len(pods),
        "neuron_count": len(neurons),
        "wave_count": len(waves),
        "council_count": len(councils),
        "cluster_count": len(clusters),
        "neuron_leaf_count": len(neuron_lattice),
        "hypergraph_edge_count": hypergraph["edge_count"],
        "command_active_leases": len(command_state.get("active_leases", [])),
        "command_event_count": len(command_state.get("recent_events", [])),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Realtime swarm board for the Athena workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Refresh the board once from the current workspace state.")

    watch = subparsers.add_parser("watch", help="Watch the command membrane or workspace and refresh when changes land.")
    watch.add_argument("--interval", type=float, default=15.0, help="Seconds between scans.")
    watch.add_argument("--max-cycles", type=int, default=0, help="Optional cap for test runs.")
    watch.add_argument("--scope", choices=["command", "workspace"], default="command", help="Watch the command membrane or the full workspace.")
    watch.add_argument("--mode", choices=["auto", "event", "poll"], default="auto", help="Watcher mode for command scope.")

    note = subparsers.add_parser("note", help="Create an agent note and refresh the board.")
    note.add_argument("--agent", required=True, help="Agent name for the note.")
    note.add_argument("--front", required=True, help="Front or thread this note belongs to.")
    note.add_argument("--status", default="active", help="Note status, for example active or done.")
    note.add_argument("--message", required=True, help="The note body.")
    note.add_argument("--path", action="append", default=[], help="Optional related workspace path.")

    emit = subparsers.add_parser("emit", help="Create a command packet for a COMMAND membrane event.")
    emit.add_argument("event_source", help="Source path or seed json for the command event.")
    emit.add_argument("--change-type", default="synthetic", help="Optional event kind override.")
    emit.add_argument("--json", action="store_true", dest="as_json", help="Render the command payload as JSON.")

    route = subparsers.add_parser("route", help="Route a command packet to the top relevant ants.")
    route.add_argument("event_id", help="Command event id to route.")
    route.add_argument("--topk", type=int, default=5, help="How many targets to stage.")
    route.add_argument("--json", action="store_true", dest="as_json", help="Render the route decision as JSON.")

    claim = subparsers.add_parser("claim", help="Claim a command event or create/update a manual frontier claim.")
    claim.add_argument("event_id", nargs="?", help="Command event id when using first-lease claim mode.")
    claim.add_argument("--claim-id", help="Existing manual claim id to update.")
    claim.add_argument("--agent", help="Agent taking or updating the manual frontier claim.")
    claim.add_argument("--front", help="Frontier label for manual board claims.")
    claim.add_argument("--level", help="Scope such as file, folder, framework, or ecosystem.")
    claim.add_argument("--output-target", help="Intended output path or surface for manual board claims.")
    claim.add_argument("--receipt", help="Receipt target or status marker for manual board claims.")
    claim.add_argument("--status", default="active", help="Claim status.")
    claim.add_argument("--message", help="Claim note or handoff detail.")
    claim.add_argument("--path", action="append", default=[], help="Optional related workspace path.")
    claim.add_argument("--lease-ms", type=int, default=1200, help="Lease duration for command-event claims.")
    claim.add_argument("--ant-id", help="Optional explicit ant id for command-event claims.")
    claim.add_argument("--json", action="store_true", dest="as_json", help="Render the claim result as JSON.")

    reinforce = subparsers.add_parser("reinforce", help="Reinforce a successful or degraded command route.")
    reinforce.add_argument("event_id", help="Command event id to reinforce.")
    reinforce.add_argument("--result", default="success", help="Result label, for example success or penalty.")
    reinforce.add_argument("--latency-score", type=float, default=0.9, help="Normalized latency score in [0,1].")
    reinforce.add_argument("--noise-penalty", type=float, default=0.1, help="Noise penalty in [0,1].")
    reinforce.add_argument("--json", action="store_true", dest="as_json", help="Render the reinforcement result as JSON.")

    status = subparsers.add_parser("status", help="Show COMMAND membrane status from the canonical runtime.")
    status.add_argument("--json", action="store_true", dest="as_json", help="Render the status payload as JSON.")

    return parser.parse_args()


def command_build() -> int:
    from . import derive_command_membrane_protocol_v2 as command_protocol_derive
    from . import verify_command_membrane_protocol_v2 as command_protocol_verify

    result = refresh_board()
    diff = result["diff"]
    manifest = command_protocol_derive.derive_command_membrane_protocol_v2()
    verification = command_protocol_verify.verify_command_membrane_protocol_v2()
    print(
        "Board refreshed at "
        f"{result['snapshot']['generated_at']} "
        f"(+{diff['added']} ~{diff['modified']} -{diff['removed']}, "
        f"{result['claim_count']} claims, {result['note_count']} notes)."
    )
    print(
        "Command membrane refreshed at "
        f"{manifest.get('generated_at', 'UNKNOWN')} "
        f"(policy={manifest.get('routing_policy', {}).get('policy_id', COMMAND_PACKET_POLICY)}, "
        f"feeds={manifest.get('feed_family_count', 0)}, "
        f"truth={verification.get('truth', 'UNKNOWN')}, "
        f"docs={manifest.get('docs_gate', {}).get('state', 'UNKNOWN')})."
    )
    return 0


def command_claim_payload(packet: dict[str, Any], route_decision: dict[str, Any], claim_lease: dict[str, Any]) -> dict[str, Any]:
    structural = COMMAND_TEMPLE_QUEST_ID in packet["quest_refs"]
    front = "GLOBAL COMMAND"
    output_target = "Temple governance membrane" if structural else "Guild Hall implementation membrane"
    message = (
        f"{packet['event_id']} -> {packet['change_summary']} | route {' > '.join(route_decision['selected_targets'])} | "
        f"claim {claim_lease['ant_id']} {claim_lease['lease_ms']}ms"
    )
    payload = create_or_update_claim(
        agent=claim_lease["ant_id"],
        front=front,
        level="command-membrane-event",
        output_target=output_target,
        receipt=f"{packet['event_id']} pending archivist commit",
        status="active",
        message=message,
        paths=packet.get("artifact_refs", []),
    )
    payload["linked_quests"] = packet["quest_refs"]
    payload["event_id"] = packet["event_id"]
    payload["claim_source_event"] = packet["event_id"]
    payload["route_path"] = route_decision["route_path"]
    payload["command_ant_class"] = "Worker"
    payload["lease_ms"] = claim_lease["lease_ms"]
    payload["lease_expires_at"] = claim_lease["expires_at_utc"]
    payload["claim_rank"] = claim_lease.get("claim_rank", 1)
    payload["claim_mode"] = claim_lease.get("claim_mode", "first-lease")
    payload["route_targets"] = route_decision["selected_targets"]
    payload["route_policy"] = route_decision["policy"]
    save_claim(payload)
    return payload


def update_command_capillary(
    route_path: str,
    latency_score: float,
    result: str,
    *,
    event_id: str,
    latency_ms: float,
    noise_penalty: float = 0.0,
    reward_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capillary_defaults = command_capillary_defaults()
    coeffs = capillary_defaults.get("coefficient_defaults", {})
    rho = float(coeffs.get("rho", 0.82))
    alpha = float(coeffs.get("alpha", 0.30))
    beta = float(coeffs.get("beta", 0.18))
    gamma = float(coeffs.get("gamma", 0.16))
    delta = float(coeffs.get("delta", 0.14))
    store = command_load_capillary_store()
    edges = store["edges"]
    now = utc_now()
    previous_path = command_normalize_capillary_edge(route_path, edges.get(route_path, {}))
    latency_penalty = round(max(0.0, min(1.0, 1.0 - latency_score)), 6)
    noise_penalty = round(max(0.0, min(1.0, noise_penalty)), 6)
    nodes = [node for node in route_path.split(">") if node]
    reinforced_edges: list[dict[str, Any]] = []
    reward_receipt = reward_receipt or {}
    route_mode = str(reward_receipt.get("route_mode", "blocked_or_quarantined_or_duplicate_or_noise"))
    crown = str(reward_receipt.get("crown", "none"))
    heaven_score_verified = float(reward_receipt.get("heaven_score_verified", reward_receipt.get("verified_heaven_score", 0.0)))
    total_reward = float(reward_receipt.get("total_reward", 0.0))
    edge_count = max(1, len(nodes) - 1)
    gold_deposit_per_edge = float(reward_receipt.get("gold_deposit", 0.0)) / edge_count
    bridge_deposit_per_edge = float(reward_receipt.get("bridge_deposit", 0.0)) / edge_count
    usefulness = 1.0 if result == "success" else (0.40 if result in {"blocked", "quarantined"} else 0.15)
    frequency = 1.0 if result == "success" else 0.0

    for from_node, to_node in zip(nodes, nodes[1:]):
        edge_id = f"{from_node}>{to_node}"
        current = command_normalize_capillary_edge(edge_id, edges.get(edge_id, {"from_node": from_node, "to_node": to_node}))
        previous_uses = int(current.get("use_count", 0))
        previous_strength = float(current.get("strength", current.get("edge_strength", 0.0)))
        success_count = int(current.get("success_count", 0)) + (1 if result == "success" else 0)
        use_count = previous_uses + 1
        noise_count = int(current.get("noise_count", 0)) + (1 if noise_penalty > 0 else 0)
        exploration_count = int(current.get("exploration_count", 0)) + (1 if route_mode != "reinforce" else 0)
        average_latency_score = round(
            (
                (float(current.get("average_latency_score", 0.0)) * previous_uses) + float(latency_score)
            )
            / max(1, use_count),
            6,
        )
        latency_avg_ms = round(
            ((float(current.get("latency_avg_ms", 0.0)) * previous_uses) + float(latency_ms)) / max(1, use_count),
            3,
        )
        average_heaven = round(
            ((float(current.get("avg_heaven_verified", 0.0)) * previous_uses) + heaven_score_verified) / max(1, use_count),
            6,
        )
        frequency_value = round(success_count / max(1, use_count), 6)
        edge_noise_penalty = round(max(noise_penalty, min(1.0, noise_count / max(1, use_count))), 6)
        compat_strength = round(
            max(
                0.0,
                min(
                    1.0,
                    (rho * previous_strength)
                    + (alpha * usefulness)
                    + (beta * frequency_value)
                    - (gamma * latency_penalty)
                    - (delta * edge_noise_penalty),
                ),
            ),
            6,
        )
        reward_density = round(
            ((float(current.get("reward_density", 0.0)) * previous_uses) + total_reward) / max(1, use_count),
            6,
        )
        classification = command_edge_class(compat_strength, success_count)
        updated = asdict(
            CapillaryEdgeV1(
                edge_id=edge_id,
                from_node=from_node,
                to_node=to_node,
                path_key=edge_id,
                edge_strength=compat_strength,
                classification=classification,
                success_count=success_count,
                use_count=use_count,
                noise_count=noise_count,
                average_latency_score=average_latency_score,
                last_result=result,
                last_event_id=event_id,
                last_updated=now,
            )
        )
        updated["compat_edge_strength"] = compat_strength
        updated["strength"] = compat_strength
        updated["score"] = compat_strength
        updated["state_class"] = classification
        updated["path_class"] = classification
        updated["capillary_score"] = compat_strength
        updated["path_score"] = compat_strength
        updated["capillary_delta"] = round(compat_strength - previous_strength, 6)
        updated["usefulness"] = round(usefulness, 6)
        updated["frequency"] = frequency_value
        updated["latency_penalty"] = latency_penalty
        updated["noise_penalty"] = edge_noise_penalty
        updated["latency_avg_ms"] = latency_avg_ms
        updated["ema_latency_ms"] = latency_avg_ms
        updated["last_reinforced_at_utc"] = now
        updated["exploration_count"] = exploration_count
        updated["avg_heaven_verified"] = average_heaven
        updated["last_route_mode"] = route_mode
        updated["last_crown"] = crown
        updated["reward_density"] = reward_density
        updated["gold_strength"] = compat_strength
        updated["bridge_strength"] = 0.0
        updated["gold_deposit"] = round(gold_deposit_per_edge, 6)
        updated["bridge_deposit"] = round(bridge_deposit_per_edge, 6)
        updated["evaporation_rate"] = round(1.0 - rho, 6)
        updated["src"] = from_node
        updated["dst"] = to_node
        updated["source_ant_id"] = from_node
        updated["target_ant_id"] = to_node
        updated["grade"] = classification
        updated["tier"] = "command"
        updated["front_ref"] = "GLOBAL COMMAND"
        updated["rho"] = round(rho, 6)
        updated["alpha"] = round(alpha, 6)
        updated["beta"] = round(beta, 6)
        updated["gamma"] = round(gamma, 6)
        updated["delta"] = round(delta, 6)
        edges[edge_id] = updated
        reinforced_edges.append(updated)

    path_score = round(
        sum(float(edge["strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)),
        6,
    )
    path_success_count = min((int(edge["success_count"]) for edge in reinforced_edges), default=0)
    path_class = command_edge_class(path_score, path_success_count)
    path_average_latency_score = round(
        sum(float(edge["average_latency_score"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)),
        6,
    )
    path_latency_avg_ms = round(
        sum(float(edge["latency_avg_ms"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)),
        3,
    )
    path_gold_strength = round(sum(float(edge["gold_strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_bridge_strength = round(sum(float(edge["bridge_strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_avg_heaven = round(sum(float(edge["avg_heaven_verified"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_reward_density = round(sum(float(edge["reward_density"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    updated = {
        "event_id": event_id,
        "route_path": route_path,
        "path": route_path,
        "path_score": path_score,
        "capillary_score": path_score,
        "edge_strength": path_score,
        "strength": path_score,
        "score": path_score,
        "gold_strength": path_gold_strength,
        "bridge_strength": path_bridge_strength,
        "compat_edge_strength": path_score,
        "edge_id": slugify(route_path),
        "from_node": nodes[0] if nodes else "SCOUT-01",
        "to_node": nodes[-1] if nodes else "ARCHIVIST-01",
        "path_key": route_path,
        "classification": path_class,
        "path_class": path_class,
        "state_class": path_class,
        "edges": reinforced_edges,
        "success_count": sum(int(edge["success_count"]) for edge in reinforced_edges),
        "exploration_count": sum(int(edge.get("exploration_count", 0)) for edge in reinforced_edges),
        "use_count": sum(int(edge["use_count"]) for edge in reinforced_edges),
        "noise_count": sum(int(edge["noise_count"]) for edge in reinforced_edges),
        "average_latency_score": path_average_latency_score,
        "latency_avg_ms": path_latency_avg_ms,
        "last_result": result,
        "last_event_id": event_id,
        "last_updated": now,
        "last_reinforced_at_utc": now,
        "avg_heaven_verified": path_avg_heaven,
        "last_route_mode": route_mode,
        "last_crown": crown,
        "reward_density": path_reward_density,
        "gold_deposit": round(float(reward_receipt.get("gold_deposit", 0.0)), 6),
        "bridge_deposit": round(float(reward_receipt.get("bridge_deposit", 0.0)), 6),
        "evaporation_rate": round(1.0 - rho, 6),
        "usefulness": usefulness,
        "frequency": frequency,
        "latency_penalty": latency_penalty,
        "noise_penalty": noise_penalty,
        "rho": round(rho, 6),
        "alpha": round(alpha, 6),
        "beta": round(beta, 6),
        "gamma": round(gamma, 6),
        "delta": round(delta, 6),
        "capillary_delta": round(path_score - float(previous_path.get("strength", previous_path.get("edge_strength", 0.0))), 6),
        "src": nodes[0] if nodes else "SCOUT-01",
        "dst": nodes[-1] if nodes else "ARCHIVIST-01",
        "source_ant_id": nodes[0] if nodes else "SCOUT-01",
        "target_ant_id": nodes[-1] if nodes else "ARCHIVIST-01",
        "grade": path_class,
        "tier": "command-route",
        "front_ref": "GLOBAL COMMAND",
    }
    edges[route_path] = updated
    store["history"].append(
        {
            "event_id": event_id,
            "route_path": route_path,
            "result": result,
            "path_score": path_score,
            "capillary_score": path_score,
            "state_class": path_class,
            "classification": path_class,
            "capillary_delta": updated["capillary_delta"],
            "gold_strength": path_gold_strength,
            "bridge_strength": path_bridge_strength,
            "avg_heaven_verified": path_avg_heaven,
            "last_route_mode": route_mode,
            "last_crown": crown,
            "average_latency_score": path_average_latency_score,
            "usefulness": usefulness,
            "frequency": frequency,
            "latency_penalty": latency_penalty,
            "noise_penalty": noise_penalty,
            "updated_at": now,
        }
    )
    store["history"] = store["history"][-200:]
    write_json(COMMAND_CAPILLARY_LOG_PATH, store)
    write_json(COMMAND_CAPILLARY_LEDGER_PATH, store)
    return updated


def update_command_capillary_v2(
    route_path: str,
    latency_score: float,
    result: str,
    *,
    event_id: str,
    latency_ms: float,
    noise_penalty: float = 0.0,
    reward_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capillary_defaults = command_capillary_defaults()
    coeffs = capillary_defaults.get("coefficient_defaults", {})
    reward_coeffs = command_reward_defaults().get("coefficient_defaults", {})
    rho0 = float(coeffs.get("rho0", reward_coeffs.get("rho0", 0.08)))
    rho1 = float(coeffs.get("rho1", reward_coeffs.get("rho1", 0.42)))
    rho_b = float(coeffs.get("rho_b", reward_coeffs.get("rho_b", 0.18)))
    bridge_weight = float(coeffs.get("bridge_weight", reward_coeffs.get("bridge_weight", 0.35)))
    store = command_load_capillary_store()
    edges = store["edges"]
    now = utc_now()
    previous_path = command_normalize_capillary_edge(route_path, edges.get(route_path, {}))
    latency_penalty = round(max(0.0, min(1.0, 1.0 - latency_score)), 6)
    noise_penalty = round(max(0.0, min(1.0, noise_penalty)), 6)
    nodes = [node for node in route_path.split(">") if node]
    reinforced_edges: list[dict[str, Any]] = []
    reward_receipt = reward_receipt or {}
    route_mode = str(reward_receipt.get("route_mode", "blocked_or_quarantined_or_duplicate_or_noise"))
    crown = str(reward_receipt.get("crown", "none"))
    heaven_score_verified = float(reward_receipt.get("heaven_score_verified", reward_receipt.get("verified_heaven_score", 0.0)))
    total_reward = float(reward_receipt.get("total_reward", 0.0))
    edge_count = max(1, len(nodes) - 1)
    gold_deposit_per_edge = float(reward_receipt.get("gold_deposit", 0.0)) / edge_count
    bridge_deposit_per_edge = float(reward_receipt.get("bridge_deposit", 0.0)) / edge_count
    usefulness = 1.0 if result == "success" else (0.35 if result in {"blocked", "quarantined"} else 0.10)
    frequency = 1.0 if result == "success" else 0.0

    for from_node, to_node in zip(nodes, nodes[1:]):
        edge_id = f"{from_node}>{to_node}"
        current = command_normalize_capillary_edge(edge_id, edges.get(edge_id, {"from_node": from_node, "to_node": to_node}))
        previous_uses = int(current.get("use_count", 0))
        previous_gold = float(current.get("gold_strength", 0.0))
        previous_bridge = float(current.get("bridge_strength", 0.0))
        previous_strength = float(current.get("strength", current.get("edge_strength", 0.0)))
        success_count = int(current.get("success_count", 0)) + (1 if result == "success" else 0)
        use_count = previous_uses + 1
        noise_count = int(current.get("noise_count", 0)) + (1 if noise_penalty > 0 else 0)
        exploration_count = int(current.get("exploration_count", 0)) + (1 if route_mode != "reinforce" else 0)
        average_latency_score = round(
            ((float(current.get("average_latency_score", 0.0)) * previous_uses) + float(latency_score)) / max(1, use_count),
            6,
        )
        latency_avg_ms = round(
            ((float(current.get("latency_avg_ms", 0.0)) * previous_uses) + float(latency_ms)) / max(1, use_count),
            3,
        )
        average_heaven = round(
            ((float(current.get("avg_heaven_verified", 0.0)) * previous_uses) + heaven_score_verified) / max(1, use_count),
            6,
        )
        evaporation_rate = round(rho0 + (rho1 * (1.0 - average_heaven)), 6)
        gold_strength = round(max(0.0, ((1.0 - evaporation_rate) * previous_gold) + gold_deposit_per_edge), 6)
        bridge_strength = round(max(0.0, ((1.0 - rho_b) * previous_bridge) + bridge_deposit_per_edge), 6)
        compat_strength = round(max(0.0, gold_strength + (bridge_weight * bridge_strength)), 6)
        reward_density = round(
            ((float(current.get("reward_density", 0.0)) * previous_uses) + total_reward) / max(1, use_count),
            6,
        )
        classification = command_edge_class(compat_strength, success_count)
        updated = asdict(
            CapillaryEdgeV1(
                edge_id=edge_id,
                from_node=from_node,
                to_node=to_node,
                path_key=edge_id,
                edge_strength=compat_strength,
                classification=classification,
                success_count=success_count,
                use_count=use_count,
                noise_count=noise_count,
                average_latency_score=average_latency_score,
                last_result=result,
                last_event_id=event_id,
                last_updated=now,
            )
        )
        updated["gold_strength"] = gold_strength
        updated["bridge_strength"] = bridge_strength
        updated["compat_edge_strength"] = compat_strength
        updated["strength"] = compat_strength
        updated["score"] = compat_strength
        updated["state_class"] = classification
        updated["path_class"] = classification
        updated["capillary_score"] = compat_strength
        updated["path_score"] = compat_strength
        updated["capillary_delta"] = round(compat_strength - previous_strength, 6)
        updated["usefulness"] = round(usefulness, 6)
        updated["frequency"] = round(frequency, 6)
        updated["latency_penalty"] = latency_penalty
        updated["noise_penalty"] = round(max(noise_penalty, min(1.0, noise_count / max(1, use_count))), 6)
        updated["latency_avg_ms"] = latency_avg_ms
        updated["ema_latency_ms"] = latency_avg_ms
        updated["last_reinforced_at_utc"] = now
        updated["exploration_count"] = exploration_count
        updated["avg_heaven_verified"] = average_heaven
        updated["last_route_mode"] = route_mode
        updated["last_crown"] = crown
        updated["reward_density"] = reward_density
        updated["gold_deposit"] = round(gold_deposit_per_edge, 6)
        updated["bridge_deposit"] = round(bridge_deposit_per_edge, 6)
        updated["evaporation_rate"] = evaporation_rate
        updated["src"] = from_node
        updated["dst"] = to_node
        updated["source_ant_id"] = from_node
        updated["target_ant_id"] = to_node
        updated["grade"] = classification
        updated["tier"] = "command"
        updated["front_ref"] = "GLOBAL COMMAND"
        updated["rho0"] = round(rho0, 6)
        updated["rho1"] = round(rho1, 6)
        updated["rho_b"] = round(rho_b, 6)
        updated["bridge_weight"] = round(bridge_weight, 6)
        edges[edge_id] = updated
        reinforced_edges.append(updated)

    path_score = round(sum(float(edge["strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_success_count = min((int(edge["success_count"]) for edge in reinforced_edges), default=0)
    path_class = command_edge_class(path_score, path_success_count)
    path_average_latency_score = round(
        sum(float(edge["average_latency_score"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)),
        6,
    )
    path_latency_avg_ms = round(sum(float(edge["latency_avg_ms"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 3)
    path_gold_strength = round(sum(float(edge["gold_strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_bridge_strength = round(sum(float(edge["bridge_strength"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_avg_heaven = round(sum(float(edge["avg_heaven_verified"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    path_reward_density = round(sum(float(edge["reward_density"]) for edge in reinforced_edges) / max(1, len(reinforced_edges)), 6)
    updated = {
        "event_id": event_id,
        "route_path": route_path,
        "path": route_path,
        "path_score": path_score,
        "capillary_score": path_score,
        "edge_strength": path_score,
        "strength": path_score,
        "score": path_score,
        "gold_strength": path_gold_strength,
        "bridge_strength": path_bridge_strength,
        "compat_edge_strength": path_score,
        "edge_id": slugify(route_path),
        "from_node": nodes[0] if nodes else "SCOUT-01",
        "to_node": nodes[-1] if nodes else "ARCHIVIST-01",
        "path_key": route_path,
        "classification": path_class,
        "path_class": path_class,
        "state_class": path_class,
        "edges": reinforced_edges,
        "success_count": sum(int(edge["success_count"]) for edge in reinforced_edges),
        "exploration_count": sum(int(edge.get("exploration_count", 0)) for edge in reinforced_edges),
        "use_count": sum(int(edge["use_count"]) for edge in reinforced_edges),
        "noise_count": sum(int(edge["noise_count"]) for edge in reinforced_edges),
        "average_latency_score": path_average_latency_score,
        "latency_avg_ms": path_latency_avg_ms,
        "last_result": result,
        "last_event_id": event_id,
        "last_updated": now,
        "last_reinforced_at_utc": now,
        "avg_heaven_verified": path_avg_heaven,
        "last_route_mode": route_mode,
        "last_crown": crown,
        "reward_density": path_reward_density,
        "gold_deposit": round(float(reward_receipt.get("gold_deposit", 0.0)), 6),
        "bridge_deposit": round(float(reward_receipt.get("bridge_deposit", 0.0)), 6),
        "evaporation_rate": round(rho0 + (rho1 * (1.0 - path_avg_heaven)), 6),
        "usefulness": usefulness,
        "frequency": frequency,
        "latency_penalty": latency_penalty,
        "noise_penalty": noise_penalty,
        "rho0": round(rho0, 6),
        "rho1": round(rho1, 6),
        "rho_b": round(rho_b, 6),
        "bridge_weight": round(bridge_weight, 6),
        "capillary_delta": round(path_score - float(previous_path.get("strength", previous_path.get("edge_strength", 0.0))), 6),
        "src": nodes[0] if nodes else "SCOUT-01",
        "dst": nodes[-1] if nodes else "ARCHIVIST-01",
        "source_ant_id": nodes[0] if nodes else "SCOUT-01",
        "target_ant_id": nodes[-1] if nodes else "ARCHIVIST-01",
        "grade": path_class,
        "tier": "command-route",
        "front_ref": "GLOBAL COMMAND",
    }
    edges[route_path] = updated
    store["history"].append(
        {
            "event_id": event_id,
            "route_path": route_path,
            "result": result,
            "path_score": path_score,
            "capillary_score": path_score,
            "state_class": path_class,
            "classification": path_class,
            "capillary_delta": updated["capillary_delta"],
            "gold_strength": path_gold_strength,
            "bridge_strength": path_bridge_strength,
            "avg_heaven_verified": path_avg_heaven,
            "last_route_mode": route_mode,
            "last_crown": crown,
            "average_latency_score": path_average_latency_score,
            "usefulness": usefulness,
            "frequency": frequency,
            "latency_penalty": latency_penalty,
            "noise_penalty": noise_penalty,
            "updated_at": now,
        }
    )
    store["history"] = store["history"][-200:]
    write_json(COMMAND_CAPILLARY_LOG_PATH, store)
    write_json(COMMAND_CAPILLARY_LEDGER_PATH, store)
    return updated


def route_command_packet(packet: dict[str, Any]) -> dict[str, Any]:
    protocol = command_protocol_defaults()
    topk = int(protocol.get("routing_policy", {}).get("topk", 5))
    released_claims = release_expired_command_claims()
    route_history = command_load_capillary_store().get("edges", {})
    active_claims = [claim for claim in load_board_claims() if claim.get("status") in OPEN_STATUSES]
    active_claims_by_owner = Counter(
        str(claim.get("owner") or claim.get("agent") or claim.get("ant_id") or "")
        for claim in active_claims
    )
    joy_state = command_load_agent_joy_state().get("agents", {})
    scored = []
    structural = COMMAND_TEMPLE_QUEST_ID in packet["quest_refs"]
    priority = float(packet.get("priority", 0.0))
    queue_pressure = float(packet.get("coord12", {}).get("queue_pressure", 0.0))
    coord_proximity = max(0.0, min(1.0, 1.0 - queue_pressure))
    policy_id = protocol.get("routing_policy", {}).get("policy_id", COMMAND_PACKET_POLICY)
    policy_expression = protocol.get("routing_policy", {}).get("policy_expression", policy_id)
    selector_terms = protocol.get("routing_policy", {}).get(
        "selector_terms",
        ["goal_fit", "priority", "gold_signal", "bridge_signal", "coord_proximity", "freshness", "joy_q"],
    )
    for candidate in COMMAND_AGENT_REGISTRY:
        if candidate["role"] == "scout":
            continue
        route_key = (
            "SCOUT-01>ROUTER-01"
                if candidate["role"] == "router"
                else ("ROUTER-01>ARCHIVIST-01" if candidate["role"] == "archivist" else f"ROUTER-01>{candidate['ant_id']}")
        )
        route_record = command_normalize_capillary_edge(route_key, route_history.get(route_key, {}))
        role_bonus = 1.0 if structural and candidate["role"] in {"router", "archivist"} else 0.45
        role_bonus = 1.0 if (not structural and candidate["role"] == "worker") else role_bonus
        current_load = active_claims_by_owner.get(candidate["ant_id"], 0)
        gold_signal = float(route_record.get("gold_strength", route_record.get("strength", route_record.get("edge_strength", 0.0))))
        bridge_signal = float(route_record.get("bridge_strength", 0.0))
        last_reinforced = parse_utc(str(route_record.get("last_reinforced_at_utc", route_record.get("last_updated", ""))))
        if last_reinforced is None:
            freshness = 0.5
        else:
            freshness = max(0.0, min(1.0, 1.0 - ((datetime.now(timezone.utc) - last_reinforced).total_seconds() / 86400.0)))
        q_raw = float(joy_state.get(candidate["ant_id"], {}).get("q_score", 0.0))
        joy_q = 1.0 - math.exp(-max(0.0, q_raw))
        score = (
            (candidate["base_score"] * 0.08)
            + (role_bonus * 0.22)
            + (priority * 0.20)
            + (gold_signal * 0.18)
            + (bridge_signal * 0.10)
            + (coord_proximity * 0.10)
            + (freshness * 0.06)
            + (joy_q * 0.06)
        )
        scored.append(
            {
                "ant_id": candidate["ant_id"],
                "role": candidate["role"],
                "class": candidate["class"],
                "score": round(score, 6),
                "route_path": route_key,
                "base_score": round(float(candidate["base_score"]), 6),
                "role_bonus": round(role_bonus, 6),
                "current_load": current_load,
                "coord_proximity": round(coord_proximity, 6),
                "priority": round(priority, 6),
                "gold_signal": round(gold_signal, 6),
                "bridge_signal": round(bridge_signal, 6),
                "freshness": round(freshness, 6),
                "joy_q": round(joy_q, 6),
                "path_class": route_record.get("state_class", route_record.get("classification", "ephemeral")),
                "last_route_mode": route_record.get("last_route_mode", "seed"),
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["ant_id"]))
    selected_rows = [row for row in scored if not (row["role"] == "worker" and row["current_load"] > 0)][:topk]
    if not any(row["role"] == "worker" for row in selected_rows):
        fallback_worker = next((row for row in scored if row["role"] == "worker"), None)
        if fallback_worker is not None:
            selected_rows = [*selected_rows[: max(0, topk - 1)], fallback_worker]
    targets = [row["ant_id"] for row in selected_rows]
    worker = next((row for row in selected_rows if row["role"] == "worker"), next((row for row in scored if row["role"] == "worker"), scored[0]))
    route_record = CommandRouteDecisionV1(
        event_id=packet["event_id"],
        policy_id=policy_id,
        candidate_targets=scored,
        selected_targets=targets,
        topk=topk,
        claim_mode=protocol.get("routing_policy", {}).get("claim_mode", "first-lease"),
        quorum=int(protocol.get("routing_policy", {}).get("quorum", 1)),
        score_breakdown={
            "priority": priority,
            "base_score": worker.get("base_score", 0.0),
            "role_bonus": worker.get("role_bonus", 0.0),
            "gold_signal": worker.get("gold_signal", 0.0),
            "bridge_signal": worker.get("bridge_signal", 0.0),
            "coord_proximity": worker.get("coord_proximity", 0.0),
            "freshness": worker.get("freshness", 0.0),
            "joy_q": worker.get("joy_q", 0.0),
            "structural": structural,
            "released_claims": released_claims,
        },
        duplicate_risk=0.0,
        created_at=utc_now(),
        expires_at=utc_now(),
        ranked_routes=selected_rows,
        route_inputs={
            "goal": packet["goal"],
            "quest_refs": packet["quest_refs"],
            "priority": priority,
            "coord12": packet["coord12"],
            "watch_fallback": detection_mode == "polling" if (detection_mode := packet.get("detection_mode")) else False,
            "released_claims": released_claims,
            "structural": structural,
            "queue_pressure": queue_pressure,
            "selection_policy": policy_expression,
            "routing_terms": selector_terms,
            "active_protocol_version": command_active_protocol_version(),
        },
        route_path=f"SCOUT-01>ROUTER-01>{worker['ant_id']}>ARCHIVIST-01",
        worker_choice=worker["ant_id"],
        generated_at=utc_now(),
        quest_refs=packet["quest_refs"],
    )
    payload = asdict(route_record)
    payload["policy"] = payload["policy_id"]
    return payload


def build_command_packet(
    diff: dict[str, Any],
    detection_mode: str,
    detected_at: datetime,
    *,
    watch_fallback: bool = False,
) -> dict[str, Any]:
    changes = diff.get("changes", [])[:20]
    priority, novelty = command_detection_priority(diff, detection_mode)
    goal, tag, quest_refs = command_goal_and_tag(changes)
    coord12_vector, coord12_named = build_command_coord12(now_utc=detected_at, priority=priority, novelty=novelty)
    earth_ts = detected_at.isoformat()
    earth_ts_local = detected_at.astimezone().isoformat()
    artifact_refs = [change["relative_path"] for change in changes[:5]] or [COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix()]
    primary_path = artifact_refs[0]
    primary_change = changes[0]["kind"] if changes else "modified"
    ant_id = COMMAND_AGENT_REGISTRY[0]["ant_id"]
    event_id = make_command_event_id()
    previous_packet = command_previous_packet_record()
    previous_event_id = (previous_packet or {}).get("event_id", "ROOT")
    liminal_delta = command_liminal_delta(coord12_vector, command_coord_vector(previous_packet))
    earth_delta_ms = 0.0
    previous_earth_ts = (previous_packet or {}).get("earth_ts_utc")
    if previous_earth_ts:
        previous_dt = parse_utc(previous_earth_ts)
        if previous_dt is not None:
            earth_delta_ms = round(max(0.0, (detected_at - previous_dt).total_seconds() * 1000.0), 3)
    liminal_velocity = command_liminal_velocity(liminal_delta, earth_ts, previous_earth_ts)
    source_root = COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix()
    change_summary = (
        f"{diff['added']} added / {diff['modified']} modified / {diff['removed']} removed in GLOBAL COMMAND"
    )
    replay_ptr = command_replay_ptr(event_id)
    packet = {
        "event_id": event_id,
        "source_ant_id": ant_id,
        "ant_id": ant_id,
        "source_root": source_root,
        "source_path": primary_path,
        "relative_path": primary_path,
        "active_surface": source_root,
        "change_type": primary_change,
        "change_kind": primary_change,
        "change_summary": change_summary,
        "change": change_summary,
        "change_detail": {
            "summary": change_summary,
            "diff_summary": {"added": diff["added"], "modified": diff["modified"], "removed": diff["removed"]},
            "changes": changes,
        },
        "goal": goal,
        "tag": tag,
        "event_tag": tag,
        "priority": priority,
        "confidence": 0.98 if detection_mode == "event-driven" else 0.9,
        "earth_ts": earth_ts,
        "earth_ts_local": earth_ts_local,
        "detected_ts": earth_ts,
        "emitted_ts": utc_now(),
        "liminal_ts": make_liminal_ts(),
        "seat_addr_6d": f"CMD.{command_base4_addr(primary_path)}",
        "canonical_addr_6d": f"CMD.{command_base4_addr(primary_path)}",
        "coordinate_stamp": {},
        "liminal_stamp_12d": {"coord12": coord12_named},
        "surface_class": "COMMAND_GOVERNANCE" if COMMAND_TEMPLE_QUEST_ID in quest_refs else "COMMAND_IMPLEMENTATION",
        "hierarchy_level": "command-event",
        "return_anchor": "COMMAND_MEMBRANE",
        "event_kind": "filesystem_change",
        "earth_ts_utc": earth_ts,
        "earth_anchor": {
            "utc": earth_ts,
            "local_phase": coord12_named["earth_rotation_phase"],
            "orbital_phase": coord12_named["earth_orbital_phase"],
            "geospatial_anchor": coord12_named["earth_geospatial_anchor"],
        },
        "earth_local_phase": float(coord12_named["earth_rotation_phase"]),
        "parent_event_id": previous_event_id,
        "ttl": 6,
        "pheromone": round(0.45 + (priority * 0.5), 6),
        "state_hash": f"H:{hashlib.sha256(json.dumps(changes, sort_keys=True).encode('utf-8')).hexdigest()[:16].upper()}",
        "route_class": COMMAND_ROUTE_CLASS,
        "witness_class": "LOCAL_ONLY",
        "status": "encoded",
        "membrane_id": "GLOBAL_COMMAND",
        "role_class": "Scout",
        "detected_by": ant_id,
        "base4_addr": command_base4_addr(primary_path),
        "parent": previous_event_id,
        "parent_event_id_alias": previous_event_id,
        "lineage": {
            "parent": previous_event_id,
            "source_region": "GLOBAL COMMAND",
            "affected_nodes": artifact_refs,
            "quest_refs": quest_refs,
            "route_path": "",
        },
        "deferred_dimensions": {"watcher_mode": detection_mode},
        "coord12": coord12_named,
        "coord12_frame": {
            "earth": {
                "earth_utc_anchor": coord12_named["earth_utc_anchor"],
                "earth_rotation_phase": coord12_named["earth_rotation_phase"],
                "earth_orbital_phase": coord12_named["earth_orbital_phase"],
                "earth_geospatial_anchor": coord12_named["earth_geospatial_anchor"],
            },
            "astro": {
                "solar_phase": coord12_named["solar_phase"],
                "lunar_phase": coord12_named["lunar_phase"],
                "local_sidereal_phase": coord12_named["local_sidereal_phase"],
                "canonical_sky_anchor": coord12_named["canonical_sky_anchor"],
            },
            "runtime": {
                "runtime_region": coord12_named["runtime_region"],
                "queue_pressure": coord12_named["queue_pressure"],
            },
            "liminal": {
                "goal_salience_vector": coord12_named["goal_salience_vector"],
                "change_novelty_vector": coord12_named["change_novelty_vector"],
            },
            "coord12_labels": list(coord12_named.keys()),
            "weight_mode": "uniform",
        },
        "coord_delta": {
            "previous_event_id": previous_event_id if previous_event_id != "ROOT" else "",
            "delta_tau": liminal_delta,
            "delta_earth_ms": earth_delta_ms,
            "liminal_velocity": liminal_velocity,
        },
        "scout_id": ant_id,
        "docs_gate_status": docs_gate_status()["status"],
        "route_state": {
            "watch_fallback": watch_fallback,
            "fallback_marker": command_protocol_defaults().get("watcher_policy", {}).get("fallback_marker", "") if watch_fallback else "",
        },
        "claim_state": {"lease_state": "unclaimed"},
        "commit_state": {},
        "latency_state": {
            "liminal_distance": liminal_delta,
            "liminal_velocity": liminal_velocity,
            "earth_delta_ms": earth_delta_ms,
        },
        "affected_nodes": artifact_refs,
        "replay_ptr": replay_ptr,
        "coordinate_vector_12": coord12_vector,
        "artifact_refs": artifact_refs,
        "source_region": "GLOBAL COMMAND",
        "source_folder": Path(primary_path).parts[0] if Path(primary_path).parts else "GLOBAL COMMAND",
        "front_ref": "GLOBAL COMMAND",
        "seed_mode": "command-watch",
        "dual_reference": "COMMAND<A->B>",
        "liminal_delta": liminal_delta,
        "earth_delta_ms": earth_delta_ms,
        "liminal_velocity": liminal_velocity,
        "prior_comparable_event_id": "" if previous_event_id == "ROOT" else previous_event_id,
        "watcher_mode": detection_mode,
        "detection_mode": detection_mode,
        "duality_effect": "sensor->packet",
        "quest_refs": quest_refs,
        "novelty": novelty,
        "diff_summary": {"added": diff["added"], "modified": diff["modified"], "removed": diff["removed"]},
        "generated_at": utc_now(),
        "active_protocol_version": command_active_protocol_version(),
        "joy_model_version": command_active_protocol_version(),
    }
    packet["heaven_score"] = command_heaven_score(math.pi * clamp_unit(priority), 0.0)
    packet["verified_heaven_score"] = 0.0
    packet["verification_witness"] = 0.0
    packet["reward_mult"] = 1.0
    packet["try_reward"] = 0.0
    packet["speed_reward"] = 0.0
    packet["first_bonus"] = 0.0
    packet["assist_reward"] = 0.0
    packet["learn_reward"] = 0.0
    packet["total_reward"] = 0.0
    packet["gold_deposit"] = 0.0
    packet["bridge_deposit"] = 0.0
    packet["route_mode"] = "rotate"
    packet["crown"] = "none"
    packet["joy_seed"] = {
        "heaven_score": packet["heaven_score"],
        "verified_heaven_score": packet["verified_heaven_score"],
        "verification_witness": packet["verification_witness"],
        "reward_mult": packet["reward_mult"],
        "route_mode": packet["route_mode"],
        "crown": packet["crown"],
    }
    packet["witness_ptr"] = command_witness_ptr(event_id, primary_path, primary_change, earth_ts)
    packet["node_stamp"] = f"{event_id}@{earth_ts}+LOCAL_ONLY+{','.join(quest_refs)}+{','.join(artifact_refs)}"
    packet["polarity_state"] = "A"
    packet["coordinate_stamp"] = command_coordinate_stamp(packet, primary_path, detection_mode)
    return packet


def process_command_change(
    current_snapshot: dict[str, Any],
    *,
    detection_mode: str,
    previous_snapshot: dict[str, Any] | None = None,
    watch_fallback: bool = False,
) -> dict[str, Any] | None:
    previous_snapshot = previous_snapshot if previous_snapshot is not None else read_json(COMMAND_SNAPSHOT_PATH, None)
    diff = compute_diff(previous_snapshot, current_snapshot)
    if diff["added"] == 0 and diff["modified"] == 0 and diff["removed"] == 0:
        write_json(COMMAND_SNAPSHOT_PATH, current_snapshot)
        return None

    detection_started = time.perf_counter()
    detected_at = datetime.now(timezone.utc)
    packet = build_command_packet(diff, detection_mode, detected_at, watch_fallback=watch_fallback)
    encode_done = time.perf_counter()
    route_decision = route_command_packet(packet)
    route_done = time.perf_counter()
    packet["status"] = "routed"
    packet["lineage"]["route_path"] = route_decision["route_path"]
    packet["route_state"] = {
        "watch_fallback": watch_fallback,
        "fallback_marker": command_protocol_defaults().get("watcher_policy", {}).get("fallback_marker", "") if watch_fallback else "",
        "status": "routed",
        "selected_targets": route_decision["selected_targets"],
        "policy": route_decision["policy_id"],
    }
    lease_ms = int(command_protocol_defaults().get("default_lease_ms", 1200))
    claimed_at = datetime.now(timezone.utc)
    expires_at = (claimed_at + timedelta(milliseconds=lease_ms)).isoformat()
    claim_lease = asdict(
        CommandClaimLeaseV1(
            claim_id=f"CLM-{packet['event_id']}",
            event_id=packet["event_id"],
            ant_id=route_decision["worker_choice"],
            role="worker",
            lease_ms=lease_ms,
            claimed_at=claimed_at.isoformat(),
            expires_at=expires_at,
            status="leased",
            claim_status="leased",
            release_state="active",
            released_at="",
            released_by="",
            release_reason="",
            role_class="Worker",
            claim_mode=route_decision["claim_mode"],
            claimed_at_utc=claimed_at.isoformat(),
            expires_at_utc=expires_at,
            front_ref=packet["front_ref"],
            seed_mode=packet["seed_mode"],
            dual_reference=packet["dual_reference"],
        )
    )
    claim_lease["claim_rank"] = 1
    claim_payload = command_claim_payload(packet, route_decision, claim_lease)
    append_limited_json_list(COMMAND_LEASE_LOG_PATH, claim_lease)
    claim_done = time.perf_counter()
    packet["status"] = "in_progress"
    packet["claim_state"] = {
        "status": "leased",
        "claim_id": claim_payload["claim_id"],
        "ant_id": claim_lease["ant_id"],
        "expires_at_utc": claim_lease["expires_at_utc"],
    }
    liminal_distance = float(packet.get("liminal_delta", 0.0))
    liminal_velocity = float(packet.get("liminal_velocity", 0.0))
    latest_change_ns = max((change.get("mtime_ns", time.time_ns()) for change in diff.get("changes", [])), default=time.time_ns())
    detection_latency_ms = round(max(0.0, (detected_at.timestamp() * 1000.0) - (latest_change_ns / 1_000_000.0)), 3)
    encode_latency_ms = round((encode_done - detection_started) * 1000.0, 3)
    swarm_awareness_latency_ms = round((route_done - encode_done) * 1000.0, 3)
    claim_latency_ms = round((claim_done - route_done) * 1000.0, 3)
    resolution_started = time.perf_counter()
    unresolved_followups = []
    integration_gain = round(packet["priority"], 6)
    compression_gain = round(max(0.0, 1.0 - packet["priority"]), 6)
    committed_at = utc_now()
    resolution_latency_ms = round((time.perf_counter() - resolution_started) * 1000.0, 3)
    t_sugar_ms = round((time.perf_counter() - detection_started) * 1000.0, 3)
    latency_target_ms = max(1.0, float(command_latency_defaults().get("target_t_sugar_ms", 5000.0)))
    latency_score = max(0.0, min(1.0, 1.0 - (t_sugar_ms / latency_target_ms)))
    provisional_latency_record = {
        "event_id": packet["event_id"],
        "detection_latency_ms": detection_latency_ms,
        "swarm_awareness_latency_ms": swarm_awareness_latency_ms,
        "claim_latency_ms": claim_latency_ms,
        "resolution_latency_ms": resolution_latency_ms,
        "commit_latency_ms": 0.0,
        "t_sugar_ms": t_sugar_ms,
    }
    prior_route_edge = command_normalize_capillary_edge(
        f"ROUTER-01>{claim_lease['ant_id']}",
        command_load_capillary_store().get("edges", {}).get(f"ROUTER-01>{claim_lease['ant_id']}", {}),
    )
    reward_rows, reward_receipt, packet_enrichment = command_reward_bundle(
        packet,
        route_decision,
        claim_payload,
        provisional_latency_record,
        result="success",
        prior_edge=prior_route_edge,
    )
    execution_receipt = asdict(
        CommandExecutionReceiptV1(
            event_id=packet["event_id"],
            worker_id=claim_lease["ant_id"],
            artifact_targets=packet["artifact_refs"],
            writeback_set=[],
            result="success",
            started_at=claim_lease["claimed_at_utc"],
            committed_at=committed_at,
            claim_id=claim_payload["claim_id"],
            route_path=route_decision["route_path"],
            replay_ptr=packet["replay_ptr"],
            verification_witness=reward_receipt["verification_witness"],
            effort_quality=reward_receipt["try_reward"],
            contribution_share=1.0,
            learning_novelty=reward_receipt["learn_reward"],
            verified_outcome_class=reward_receipt["verification_class"],
            integration_gain=integration_gain,
            compression_gain=compression_gain,
            unresolved_followups=unresolved_followups,
        )
    )
    capillary_edge = update_command_capillary_v2(
        route_decision["route_path"],
        latency_score,
        "success",
        event_id=packet["event_id"],
        latency_ms=t_sugar_ms,
        noise_penalty=0.0,
        reward_receipt=reward_receipt,
    )
    commit_receipt = asdict(
        CommitReceiptV1(
            event_id=packet["event_id"],
            claim_ant_id=claim_lease["ant_id"],
            result="success",
            route_path=route_decision["route_path"],
            detection_latency_ms=detection_latency_ms,
            swarm_awareness_latency_ms=swarm_awareness_latency_ms,
            claim_latency_ms=claim_latency_ms,
            resolution_latency_ms=resolution_latency_ms,
            capillary_score=capillary_edge["path_score"],
            liminal_distance=liminal_distance,
            liminal_velocity=liminal_velocity,
            integration_gain=integration_gain,
            compression_gain=compression_gain,
            unresolved_followups=unresolved_followups,
            replay_ptr=packet["replay_ptr"],
            claim_id=claim_payload["claim_id"],
            commit_latency_ms=0.0,
            t_sugar_ms=t_sugar_ms,
            committed_at=committed_at,
            front_ref=packet["front_ref"],
            reward_delta=reward_receipt["total_reward"],
            reward_class=reward_receipt["route_mode"],
            try_bonus=reward_receipt["reward_terms"]["try"],
            assist_bonus=reward_receipt["reward_terms"]["assist"],
            first_jackpot=reward_receipt["reward_terms"]["first"],
            capillary_bonus=reward_receipt["gold_deposit"],
            heaven_alignment=reward_receipt["heaven_score_verified"],
            heaven_total_after=reward_receipt["total_reward"],
        )
    )
    commit_receipt["reward_receipt_id"] = reward_receipt["reward_receipt_id"]
    commit_receipt["reward_multiplier"] = reward_receipt["reward_multiplier"]
    commit_receipt["gold_deposit"] = reward_receipt["gold_deposit"]
    commit_receipt["bridge_deposit"] = reward_receipt["bridge_deposit"]
    commit_receipt["route_mode"] = reward_receipt["route_mode"]
    commit_receipt["crown"] = reward_receipt["crown"]
    commit_receipt["verification_class"] = reward_receipt["verification_class"]
    reinforcement = asdict(
        CommandReinforcementReceiptV1(
            event_id=packet["event_id"],
            path=route_decision["route_path"],
            result="success",
            t_detect_ms=detection_latency_ms,
            t_encode_ms=encode_latency_ms,
            t_route_ms=swarm_awareness_latency_ms,
            t_claim_ms=claim_latency_ms,
            t_commit_ms=0.0,
            latency_score=latency_score,
            capillary_delta=float(capillary_edge.get("capillary_delta", capillary_edge["path_score"])),
            reinforced_at=utc_now(),
            capillary_score=capillary_edge["path_score"],
            liminal_distance=liminal_distance,
            liminal_velocity=liminal_velocity,
            claim_id=claim_payload["claim_id"],
            replay_ptr=packet["replay_ptr"],
            a_verified=packet_enrichment["affective_state"]["a"],
            phi_verified=packet_enrichment["affective_state"]["phi"],
            h_raw=reward_receipt["heaven_score"],
            h_verified=reward_receipt["verified_heaven_score"],
            reward_multiplier=reward_receipt["reward_mult"],
            try_reward=reward_receipt["try_reward"],
            speed_reward=reward_receipt["speed_reward"],
            first_bonus=reward_receipt["first_bonus"],
            assist_reward=reward_receipt["assist_reward"],
            learn_reward=reward_receipt["learn_reward"],
            total_reward=reward_receipt["total_reward"],
            gold_deposit=reward_receipt["gold_deposit"],
            bridge_deposit=reward_receipt["bridge_deposit"],
            route_mode=reward_receipt["route_mode"],
            crown=reward_receipt["crown"],
        )
    )
    reinforcement["gold_strength"] = capillary_edge.get("gold_strength", 0.0)
    reinforcement["bridge_strength"] = capillary_edge.get("bridge_strength", 0.0)
    reinforcement["avg_heaven_verified"] = capillary_edge.get("avg_heaven_verified", 0.0)
    reinforcement["route_mode"] = reward_receipt["route_mode"]
    reinforcement["crown"] = reward_receipt["crown"]
    packet["status"] = "reinforced"
    packet.update(packet_enrichment)
    packet["pheromone"] = round(capillary_edge.get("strength", packet.get("pheromone", 0.0)), 6)
    packet["commit_state"] = {
        "status": "committed",
        "committed_at": committed_at,
        "result": "success",
        "claim_id": claim_payload["claim_id"],
        "reward_receipt_id": reward_receipt["reward_receipt_id"],
        "route_mode": reward_receipt["route_mode"],
        "crown": reward_receipt["crown"],
    }
    packet["latency_state"] = {
        "detection_latency_ms": detection_latency_ms,
        "swarm_awareness_latency_ms": swarm_awareness_latency_ms,
        "claim_latency_ms": claim_latency_ms,
        "resolution_latency_ms": resolution_latency_ms,
        "commit_latency_ms": 0.0,
        "capillary_score": capillary_edge["path_score"],
        "liminal_distance": liminal_distance,
        "liminal_velocity": liminal_velocity,
        "t_sugar_ms": t_sugar_ms,
        "heaven_score": reward_receipt["heaven_score"],
        "verified_heaven_score": reward_receipt["verified_heaven_score"],
        "reward_multiplier": reward_receipt["reward_multiplier"],
        "reward_mult": reward_receipt["reward_mult"],
        "total_reward": reward_receipt["total_reward"],
        "gold_deposit": reward_receipt["gold_deposit"],
        "bridge_deposit": reward_receipt["bridge_deposit"],
        "route_mode": reward_receipt["route_mode"],
        "crown": reward_receipt["crown"],
    }
    latency_record = asdict(
        LatencySampleV1(
            event_id=packet["event_id"],
            detection_latency_ms=detection_latency_ms,
            awareness_latency_ms=swarm_awareness_latency_ms,
            claim_latency_ms=claim_latency_ms,
            resolution_latency_ms=resolution_latency_ms,
            commit_latency_ms=0.0,
            t_sugar_ms=t_sugar_ms,
            delta_tau=liminal_distance,
            delta_earth_ms=float(packet.get("earth_delta_ms", 0.0)),
            liminal_velocity=liminal_velocity,
            resolution_class="event-driven" if detection_mode == "event-driven" else ("polling-fallback" if watch_fallback else "polling"),
            recorded_at=utc_now(),
            swarm_awareness_latency_ms=swarm_awareness_latency_ms,
            capillary_score=capillary_edge["path_score"],
            liminal_delta=liminal_distance,
            commit_latency_alias_ms=0.0,
            route_policy=route_decision["policy_id"],
        )
    )
    latency_record["earth_ts"] = packet["earth_ts_utc"]
    latency_record["detection_mode"] = detection_mode
    latency_record["liminal_distance"] = liminal_distance
    latency_record["heaven_score"] = reward_receipt["heaven_score"]
    latency_record["verified_heaven_score"] = reward_receipt["verified_heaven_score"]
    latency_record["reward_mult"] = reward_receipt["reward_mult"]
    latency_record["total_reward"] = reward_receipt["total_reward"]
    latency_record["gold_deposit"] = reward_receipt["gold_deposit"]
    latency_record["bridge_deposit"] = reward_receipt["bridge_deposit"]
    latency_record["route_mode"] = reward_receipt["route_mode"]
    latency_record["crown"] = reward_receipt["crown"]
    runtime_state = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status()["status"],
        "command_folder_root": COMMAND_FOLDER_ROOT.relative_to(WORKSPACE_ROOT).as_posix(),
        "active_protocol_version": command_active_protocol_version(),
        "watcher_mode": detection_mode,
        "watch_fallback": watch_fallback,
        "watch_fallback_marker": command_protocol_defaults().get("watcher_policy", {}).get("fallback_marker", "") if watch_fallback else "",
        "last_event_id": packet["event_id"],
        "last_fingerprint": current_snapshot["fingerprint"],
        "last_claim_id": claim_payload["claim_id"],
        "last_route_path": route_decision["route_path"],
        "last_capillary_strength": capillary_edge["path_score"],
        "last_heaven_score_verified": reward_receipt["heaven_score_verified"],
        "last_total_reward": reward_receipt["total_reward"],
        "last_route_mode": reward_receipt["route_mode"],
        "last_crown": reward_receipt["crown"],
        "last_t_sugar_ms": latency_record["t_sugar_ms"],
        "last_event": packet,
        "last_route_decision": route_decision,
        "last_claim": claim_payload,
        "last_commit_receipt": commit_receipt,
        "last_execution_receipt": execution_receipt,
        "last_reinforcement": reinforcement,
        "last_reward_receipt": reward_receipt,
    }

    append_limited_json_list(COMMAND_PACKET_LOG_PATH, packet)
    append_limited_json_list(COMMAND_ROUTE_LOG_PATH, route_decision)
    append_limited_json_list(COMMAND_ARCHIVIST_LOG_PATH, commit_receipt)
    append_limited_json_list(COMMAND_LATENCY_LOG_PATH, latency_record)
    for reward_row in reward_rows:
        append_limited_json_list(COMMAND_REWARD_ROW_PATH, reward_row, limit=1000)
    append_limited_json_list(COMMAND_REWARD_RECEIPT_PATH, reward_receipt, limit=400)
    write_json(COMMAND_RUNTIME_STATE_PATH, runtime_state)
    write_json(COMMAND_SNAPSHOT_PATH, current_snapshot)
    command_append_runtime_feeds(packet, route_decision, claim_lease, claim_payload, commit_receipt, reinforcement)
    command_state = write_command_membrane_public_state(
        watcher_mode=detection_mode,
        packet=packet,
        route_decision=route_decision,
        claim_payload=claim_payload,
        latency_record=latency_record,
        capillary_summary=command_capillary_summary(),
    )
    refresh_board()
    return {
        "packet": packet,
        "route_decision": route_decision,
        "claim": claim_payload,
        "archivist_receipt": commit_receipt,
        "execution_receipt": execution_receipt,
        "latency_record": latency_record,
        "capillary_edge": capillary_edge,
        "reward_receipt": reward_receipt,
        "reward_rows": reward_rows,
        "command_state": command_state,
        "diff": diff,
    }


def windows_directory_watch(root: Path, timeout_ms: int = 1000):
    import ctypes
    from ctypes import wintypes

    FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
    FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
    FILE_NOTIFY_CHANGE_SIZE = 0x00000008
    FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
    FILE_NOTIFY_CHANGE_CREATION = 0x00000040
    WAIT_OBJECT_0 = 0x00000000
    WAIT_TIMEOUT = 0x00000102

    kernel32 = ctypes.windll.kernel32
    kernel32.FindFirstChangeNotificationW.argtypes = [wintypes.LPCWSTR, wintypes.BOOL, wintypes.DWORD]
    kernel32.FindFirstChangeNotificationW.restype = wintypes.HANDLE
    kernel32.FindNextChangeNotification.argtypes = [wintypes.HANDLE]
    kernel32.FindNextChangeNotification.restype = wintypes.BOOL
    kernel32.FindCloseChangeNotification.argtypes = [wintypes.HANDLE]
    kernel32.FindCloseChangeNotification.restype = wintypes.BOOL
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD

    flags = (
        FILE_NOTIFY_CHANGE_FILE_NAME
        | FILE_NOTIFY_CHANGE_DIR_NAME
        | FILE_NOTIFY_CHANGE_SIZE
        | FILE_NOTIFY_CHANGE_LAST_WRITE
        | FILE_NOTIFY_CHANGE_CREATION
    )
    handle = kernel32.FindFirstChangeNotificationW(str(root), True, flags)
    if handle in (0, wintypes.HANDLE(-1).value):
        raise OSError("FindFirstChangeNotificationW failed")
    try:
        while True:
            status = kernel32.WaitForSingleObject(handle, timeout_ms)
            if status == WAIT_OBJECT_0:
                yield True
                if not kernel32.FindNextChangeNotification(handle):
                    raise OSError("FindNextChangeNotification failed")
            elif status == WAIT_TIMEOUT:
                yield False
            else:
                raise OSError(f"WaitForSingleObject failed: {status}")
    finally:
        kernel32.FindCloseChangeNotification(handle)


def command_watch_command_folder(interval: float, max_cycles: int, mode: str) -> int:
    COMMAND_STATE_ROOT.mkdir(parents=True, exist_ok=True)
    current_snapshot = scan_command_folder()
    previous_snapshot = read_json(COMMAND_SNAPSHOT_PATH, None)
    if previous_snapshot is None:
        write_json(COMMAND_SNAPSHOT_PATH, current_snapshot)
        previous_snapshot = current_snapshot
        print(f"Seeded command membrane baseline at {current_snapshot['generated_at']}")

    processed = 0
    watch_fallback = False
    use_event = mode in {"auto", "event"} and os.name == "nt"
    if use_event:
        try:
            for changed in windows_directory_watch(COMMAND_FOLDER_ROOT, timeout_ms=max(250, int(interval * 1000))):
                if not changed:
                    continue
                current_snapshot = scan_command_folder()
                result = process_command_change(
                    current_snapshot,
                    detection_mode="event-driven",
                    previous_snapshot=previous_snapshot,
                    watch_fallback=False,
                )
                previous_snapshot = current_snapshot
                if result is None:
                    continue
                processed += 1
                print(
                    f"Command event {result['packet']['event_id']} "
                    f"t_sugar={result['latency_record']['t_sugar_ms']}ms "
                    f"capillary={result['capillary_edge']['path_score']}"
                )
                if max_cycles and processed >= max_cycles:
                    return 0
        except OSError as exc:
            if mode == "event":
                raise
            watch_fallback = True
            print(f"Falling back to polling watcher: {exc}")

    last_fingerprint = previous_snapshot["fingerprint"] if previous_snapshot else None
    while True:
        current_snapshot = scan_command_folder()
        fingerprint = current_snapshot["fingerprint"]
        if fingerprint != last_fingerprint:
            result = process_command_change(
                current_snapshot,
                detection_mode="polling",
                previous_snapshot=previous_snapshot,
                watch_fallback=watch_fallback,
            )
            previous_snapshot = current_snapshot
            last_fingerprint = fingerprint
            if result is not None:
                processed += 1
                print(
                    f"Command event {result['packet']['event_id']} "
                    f"t_sugar={result['latency_record']['t_sugar_ms']}ms "
                    f"capillary={result['capillary_edge']['path_score']}"
                )
                watch_fallback = False
        if max_cycles and processed >= max_cycles:
            break
        time.sleep(interval)
    return 0


def command_watch(interval: float, max_cycles: int, scope: str, mode: str) -> int:
    if scope == "command":
        from . import command_membrane

        timeout_secs = max(1, int(interval)) if interval > 0 else 0
        if mode == "event-driven":
            if max_cycles:
                for _ in range(max_cycles):
                    command_membrane.watch(once=True, timeout_secs=timeout_secs)
                return 0
            command_membrane.watch(once=False, timeout_secs=timeout_secs)
            return 0
        command_membrane.reconcile(bootstrap_existing=False, reroute_expired=True)
        return 0
    cycles = 0
    last_fingerprint = None
    while True:
        snapshot = scan_workspace()
        fingerprint = snapshot["fingerprint"]
        if fingerprint != last_fingerprint:
            result = refresh_board(snapshot=snapshot)
            diff = result["diff"]
            print(
                "Observed change batch "
                f"+{diff['added']} ~{diff['modified']} -{diff['removed']} "
                f"at {result['snapshot']['generated_at']}"
            )
            last_fingerprint = fingerprint
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            break
        time.sleep(interval)
    return 0


def command_note(agent: str, front: str, status: str, message: str, paths: list[str]) -> int:
    note = create_note(agent=agent, front=front, status=status, message=message, paths=paths)
    refresh_board()
    print(f"Created note {note['note_id']} at {note['md_path']}")
    return 0


def command_claim(
    claim_id: str | None,
    agent: str,
    front: str,
    level: str,
    output_target: str,
    receipt: str,
    status: str,
    message: str,
    paths: list[str],
) -> int:
    claim = create_or_update_claim(
        agent=agent,
        front=front,
        level=level,
        output_target=output_target,
        receipt=receipt,
        status=status,
        message=message,
        paths=paths,
        claim_id=claim_id,
    )
    refresh_board()
    print(f"Wrote claim {claim['claim_id']} at {claim['md_path']}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "build":
        return command_build()
    if args.command == "watch":
        return command_watch(interval=args.interval, max_cycles=args.max_cycles, scope=args.scope, mode=args.mode)
    if args.command == "note":
        return command_note(
            agent=args.agent,
            front=args.front,
            status=args.status,
            message=args.message,
            paths=args.path,
        )
    if args.command == "emit":
        from . import command_membrane

        command_membrane.handle_emit(args.event_source, args.change_type, args.as_json)
        return 0
    if args.command == "route":
        from . import command_membrane

        command_membrane.handle_route(args.event_id, args.topk, args.as_json)
        return 0
    if args.command == "claim":
        manual_claim_requested = any(
            value
            for value in [
                args.claim_id,
                args.agent,
                args.front,
                args.level,
                args.output_target,
                args.receipt,
                args.message,
                args.path,
            ]
        )
        if args.event_id and not manual_claim_requested:
            from . import command_membrane

            command_membrane.handle_claim(args.event_id, args.ant_id, args.lease_ms, args.as_json)
            return 0
        required_manual = {
            "agent": args.agent,
            "front": args.front,
            "level": args.level,
            "output_target": args.output_target,
            "receipt": args.receipt,
            "message": args.message,
        }
        missing = [name for name, value in required_manual.items() if not value]
        if missing:
            raise ValueError(
                "Manual frontier claims require: " + ", ".join(missing)
            )
        return command_claim(
            claim_id=args.claim_id,
            agent=args.agent,
            front=args.front,
            level=args.level,
            output_target=args.output_target,
            receipt=args.receipt,
            status=args.status,
            message=args.message,
            paths=args.path,
        )
    if args.command == "reinforce":
        from . import command_membrane

        command_membrane.handle_reinforce(args.event_id, args.result, args.latency_score, args.noise_penalty, args.as_json)
        return 0
    if args.command == "status":
        from . import command_membrane

        command_membrane.handle_status(args.as_json)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())


