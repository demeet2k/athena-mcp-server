#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = WORKSPACE_ROOT / "QSHRINK - ATHENA (internal use)"
ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "corpus_atlas.json"


GEOMETRIES = [
    {
        "code": "0",
        "name": "Square",
        "slug": "square",
        "role": "discrete grammar, addresses, canonical partitions, bounded cells",
        "metro": "Square Line",
    },
    {
        "code": "1",
        "name": "Circle",
        "slug": "circle",
        "role": "orbit order, recurrence, phase return, cyclic review",
        "metro": "Circle Line",
    },
    {
        "code": "2",
        "name": "Triangle",
        "slug": "triangle",
        "role": "control rails, routing choice, three-force commitment",
        "metro": "Triangle Line",
    },
    {
        "code": "3",
        "name": "Torus",
        "slug": "torus",
        "role": "cross-scale wraparound, re-entry with memory, nested recurrence",
        "metro": "Torus Line",
    },
]

OPERATORS = [
    {
        "code": "0",
        "name": "Partition",
        "slug": "partition",
        "role": "decompose the field into lawful coordinates and bound regions",
        "metro": "Partition Line",
    },
    {
        "code": "1",
        "name": "Quantize",
        "slug": "quantize",
        "role": "choose admissible resolution and preserve the right losses",
        "metro": "Quantize Line",
    },
    {
        "code": "2",
        "name": "Bucket",
        "slug": "bucket",
        "role": "split bulk from exception, stable from frontier, center from edge",
        "metro": "Bucket Line",
    },
    {
        "code": "3",
        "name": "Code",
        "slug": "code",
        "role": "compile the structured field into containers, receipts, and runnable carriers",
        "metro": "Code Line",
    },
]

BODIES = [
    {
        "code": "0",
        "name": "Foundation Body",
        "slug": "foundation_body",
        "role": "formal Q-SHRINK manuscripts, kernel equations, and internal canon",
        "refs": [
            "MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK CODING GUIDE (IMPLEMENTATION TOME).docx",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK TYPE CODING.zip",
        ],
    },
    {
        "code": "1",
        "name": "Nervous Body",
        "slug": "nervous_body",
        "role": "active routing shell, metro surfaces, swarm maps, and witness ledgers",
        "refs": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM",
            "DEEPER CRYSTALIZATION/_build/nervous_system/swarm",
            "self_actualize",
            "ECOSYSTEM",
        ],
    },
    {
        "code": "2",
        "name": "Memory Body",
        "slug": "memory_body",
        "role": "live-memory corridor, mirrored corpora, auxiliary books, and public-facing narrative bodies",
        "refs": [
            "Trading Bot/docs_search.py",
            "Trading Bot/Memory Docs",
            "Voynich",
            "Athenachka Collective Books",
        ],
    },
    {
        "code": "3",
        "name": "Runtime Body",
        "slug": "runtime_body",
        "role": "neural execution, archive-backed code, public software engine, and verification runtime",
        "refs": [
            "NERUAL NETWORK",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK.zip",
            "MATH/FINAL FORM/Q shrink/qshrink-rust-final.zip",
            "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS.zip::athena_os/qshrink/",
        ],
    },
]

CLOSURES = [
    {
        "code": "0",
        "name": "Seed",
        "slug": "seed",
        "role": "declare the local invariant and initial admissible form",
        "metro": "Seed Loop",
    },
    {
        "code": "1",
        "name": "Manuscript",
        "slug": "manuscript",
        "role": "expand the cell into narrative, proofs, diagrams, and linked surfaces",
        "metro": "Manuscript Loop",
    },
    {
        "code": "2",
        "name": "Witness",
        "slug": "witness",
        "role": "bind the cell to receipts, truth states, and replay evidence",
        "metro": "Witness Loop",
    },
    {
        "code": "3",
        "name": "Loop",
        "slug": "loop",
        "role": "contract the cell and restart it at the next toroidal frontier",
        "metro": "Loop Line",
    },
]

SWARM_SYMBOLS = ["E", "W", "F", "A"]

RAILS = ["Su", "Me", "Sa"]

APPENDIX_HUBS = [
    {
        "code": "AppA",
        "title": "Addressing, Symbols, Parsing Grammar",
        "role": "canonical entry grammar, address parsing, and notation discipline",
    },
    {
        "code": "AppB",
        "title": "Canon Laws, Equivalence Budgets, Normal Forms",
        "role": "normal form law, canon budgets, and equivalence control",
    },
    {
        "code": "AppC",
        "title": "Square Kernel Pack",
        "role": "discrete square kernels, indexing packs, and base-4 crystal algebra",
    },
    {
        "code": "AppD",
        "title": "Registry, Profiles, Version IDs",
        "role": "version surfaces, naming discipline, and registry integrity",
    },
    {
        "code": "AppE",
        "title": "Circle Gear and Mixed-Radix Clock",
        "role": "orbit timing, mixed-radix sequencing, and replayable phase return",
    },
    {
        "code": "AppF",
        "title": "Transport, Rotation-as-Conjugacy, DUAL Legality",
        "role": "transport law, rotation semantics, and corridor legality",
    },
    {
        "code": "AppG",
        "title": "Triangle Control and Tria Prima",
        "role": "triadic control, rail governance, and bounded choice",
    },
    {
        "code": "AppH",
        "title": "Coupling and Topology",
        "role": "cross-family topology, coupling strength, and bridge geometry",
    },
    {
        "code": "AppI",
        "title": "Corridors and Truth Lattice",
        "role": "truth states, witness discipline, and admissibility lattice",
    },
    {
        "code": "AppJ",
        "title": "Residual Ledgers and NEAR Machinery",
        "role": "residual accounting, partial closure, and near-correct routing",
    },
    {
        "code": "AppK",
        "title": "Conflict, Quarantine, Revocation",
        "role": "contradiction handling, quarantine regimes, and revocation law",
    },
    {
        "code": "AppL",
        "title": "Evidence Plans and AMBIG Promotion",
        "role": "promotion pathways from ambiguity toward witnessed truth",
    },
    {
        "code": "AppM",
        "title": "Replay Kernel and Verifier Capsules",
        "role": "replay discipline, verifier capsules, and strong recurrence",
    },
    {
        "code": "AppN",
        "title": "Container Formats and Virtual Mount",
        "role": "containerization, virtual mounts, and executable manuscript carriers",
    },
    {
        "code": "AppO",
        "title": "Publication Import/Export Bundles",
        "role": "public packaging, import-export boundaries, and release discipline",
    },
    {
        "code": "AppP",
        "title": "Deployment Profiles and Monitoring",
        "role": "runtime deployment, bounded agency, and monitoring loops",
    },
]

CHAPTER_SPECS = [
    {
        "code": "Ch01",
        "addr": "0000",
        "title": "Kernel and Internal Entry Law",
        "role": "define the private QSHRINK2.0 charter, legend, and parse-safe opening",
        "hubs": ["AppA", "AppC", "AppI", "AppM"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/04_higher_dimensional_tensor_map.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx",
        ],
    },
    {
        "code": "Ch02",
        "addr": "0001",
        "title": "Address Algebra and Cell Coordinates",
        "role": "state the base-4 coordinate law joining root cells, manuscript families, and replayable paths",
        "hubs": ["AppA", "AppB", "AppC", "AppI", "AppM"],
        "capsules": [
            "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/02_NEURON_ADDRESS_TENSOR.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppA_addressing_symbols_parsing_grammar.md",
            "MATH/FINAL FORM/Q shrink/Q-Shrink MASTER SKELETON.docx",
        ],
    },
    {
        "code": "Ch03",
        "addr": "0002",
        "title": "Truth Corridors and Witness Discipline",
        "role": "bind compression to admissibility, witness, replay, and certificate obligations",
        "hubs": ["AppI", "AppJ", "AppL", "AppM"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppI_corridors_and_truth_lattice.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK VOLUME III.docx",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK — Volume IV.docx",
        ],
    },
    {
        "code": "Ch04",
        "addr": "0003",
        "title": "Higher-Dimensional Geometry Stack",
        "role": "unify square, circle, triangle, and torus as the four governing internal geometries",
        "hubs": ["AppC", "AppE", "AppG", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/33_higher_d_square_circle_triangle.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/04_higher_dimensional_tensor_map.md",
            "Trading Bot/Memory Docs/HIGHER-D SQUARE ◯ CIRCLE △ TRIANGLE.docx",
        ],
    },
    {
        "code": "Ch05",
        "addr": "0010",
        "title": "Bucket Regimes and Paradox Quarantine",
        "role": "show how bucket logic separates canonical mass from frontier contradictions without lying about uncertainty",
        "hubs": ["AppB", "AppI", "AppK", "AppL"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppK_conflict_quarantine_revocation.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK — Volume I.docx",
        ],
    },
    {
        "code": "Ch06",
        "addr": "0011",
        "title": "Corpus Binding and Memory Carriers",
        "role": "connect the old Q-SHRINK core to Athena nervous, memory, and mirrored manuscript bodies",
        "hubs": ["AppA", "AppH", "AppM", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/08_MIRROR_CORPUS/01_higher_d_sources.md",
            "Trading Bot/Memory Docs",
            "Voynich",
        ],
    },
    {
        "code": "Ch07",
        "addr": "0012",
        "title": "Tunnels as Morphisms and Legal Transport",
        "role": "describe lawful travel between cells, corpus bodies, and runtime containers",
        "hubs": ["AppF", "AppH", "AppI", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppF_transport_rotation_as_conjugacy_dual_legality.md",
            "MATH/FINAL FORM/Q shrink/qshrink-rust-final.zip",
            "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS.zip::athena_os/qshrink/",
        ],
    },
    {
        "code": "Ch08",
        "addr": "0013",
        "title": "Circle Gears, Synchronization, and Return Order",
        "role": "formalize the recurrent orbit that keeps manuscripts revisitable without flattening them",
        "hubs": ["AppE", "AppG", "AppM", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppE_circle_gear_and_mixed_radix_clock.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK CODING GUIDE (IMPLEMENTATION TOME).docx",
        ],
    },
    {
        "code": "Ch09",
        "addr": "0020",
        "title": "Metro Routing and Hub Competition",
        "role": "specify how routes compete, transfer, and settle through the internal metro",
        "hubs": ["AppA", "AppE", "AppH", "AppI", "AppL", "AppM"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/01_emergent_lines.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/07_swarm_hypergraph.md",
        ],
    },
    {
        "code": "Ch10",
        "addr": "0021",
        "title": "Swarm Kernel and Packet Classes",
        "role": "turn the manuscript field into a bounded neural swarm with packet law and cluster roles",
        "hubs": ["AppA", "AppG", "AppM", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
            "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/02_NEURON_ADDRESS_TENSOR.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/02_parallel_agent_grid.md",
        ],
    },
    {
        "code": "Ch11",
        "addr": "0022",
        "title": "Void Book and Restart-Token Tunneling",
        "role": "govern restart without amnesia and bind loop closure to toroidal re-entry",
        "hubs": ["AppF", "AppI", "AppL", "AppM"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/07_chapter_11_perpetual_motion_example.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/10_information_from_the_void_mani.md",
            "self_actualize/live_docs_gate_status.md",
        ],
    },
    {
        "code": "Ch12",
        "addr": "0023",
        "title": "Certificates, Receipts, and Closure Bundles",
        "role": "show how internal manuscripts prove that a compression path is lawful",
        "hubs": ["AppC", "AppI", "AppM", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/00_RECEIPTS/01_build_receipt.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK CODING GUIDE (IMPLEMENTATION TOME).docx",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK.zip",
        ],
    },
    {
        "code": "Ch13",
        "addr": "0030",
        "title": "Replay, Regeneration, and Persistence",
        "role": "formalize memory, persistence, and regeneration as first-class QSHRINK operations",
        "hubs": ["AppJ", "AppL", "AppM", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppM_replay_kernel_and_verifier_capsules.md",
            "Trading Bot/docs_search.py",
            "Trading Bot/Memory Docs",
        ],
    },
    {
        "code": "Ch14",
        "addr": "0031",
        "title": "Migration, Versioning, and Delta Weaving",
        "role": "bind evolving manuscripts without breaking backward addressability",
        "hubs": ["AppD", "AppH", "AppM", "AppO"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppD_registry_profiles_version_ids.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK VOLUME III.docx",
            "MATH/FINAL FORM/Q shrink/qshrink-rust-final.zip",
        ],
    },
    {
        "code": "Ch15",
        "addr": "0032",
        "title": "CUT Runtime and Internal Execution Law",
        "role": "connect the manuscript law to executable runtime edges and module contracts",
        "hubs": ["AppC", "AppF", "AppN", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/17_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md",
            "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS.zip::athena_os/qshrink/",
            "NERUAL NETWORK",
        ],
    },
    {
        "code": "Ch16",
        "addr": "0033",
        "title": "Verification Harnesses and Replay Kernels",
        "role": "detail the verification surfaces that keep the internal system honest under recursion",
        "hubs": ["AppI", "AppL", "AppM", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppL_evidence_plans_and_ambig_promotion.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppM_replay_kernel_and_verifier_capsules.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK CODING GUIDE (IMPLEMENTATION TOME).docx",
        ],
    },
    {
        "code": "Ch17",
        "addr": "0100",
        "title": "Deployment and Bounded Agency",
        "role": "govern how the private system touches public software, cloud edges, and active agents",
        "hubs": ["AppG", "AppN", "AppO", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppP_deployment_profiles_and_monitoring.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK.zip",
            "ECOSYSTEM",
        ],
    },
    {
        "code": "Ch18",
        "addr": "0101",
        "title": "Macro Invariants and Tensor Stack",
        "role": "state the cross-scale invariants that let the same law work across manuscripts, swarm, and runtime",
        "hubs": ["AppB", "AppE", "AppG", "AppN"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/04_higher_dimensional_tensor_map.md",
            "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/02_NEURON_ADDRESS_TENSOR.md",
            "Trading Bot/Memory Docs/HIGHER-D SQUARE ◯ CIRCLE △ TRIANGLE.docx",
        ],
    },
    {
        "code": "Ch19",
        "addr": "0102",
        "title": "Convergence, Fixed Points, and Controlled Non-Convergence",
        "role": "define which loops must close, which may remain open, and how restart stays lawful",
        "hubs": ["AppB", "AppI", "AppJ", "AppM", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/46_ω_metro_calculus.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK — Volume IV.docx",
        ],
    },
    {
        "code": "Ch20",
        "addr": "0103",
        "title": "Collective Authoring and Internal Neural Governance",
        "role": "turn private QSHRINK into a multi-agent manuscript organism with governed merges",
        "hubs": ["AppE", "AppG", "AppL", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/07_swarm_hypergraph.md",
            "self_actualize",
        ],
    },
    {
        "code": "Ch21",
        "addr": "0110",
        "title": "Self-Replication and the Next Crystal",
        "role": "encode how QSHRINK2.0 becomes seed material for later internal frameworks without collapsing into product code",
        "hubs": ["AppA", "AppM", "AppN", "AppP"],
        "capsules": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_RECURSION/01_frontier_queue.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/06_family_crystals.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/07_swarm_hypergraph.md",
        ],
    },
]

GATE_SPECS = [
    {"code": "G01", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Canonical cortex named", "status": "OK", "focus": "anchor the private QSHRINK cortex inside the wider Athena body"},
    {"code": "G02", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Runtime hub named", "status": "OK", "focus": "bind the internal manuscript shell to an executable runtime hub"},
    {"code": "G03", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Governance mirror named", "status": "OK", "focus": "preserve a governance surface distinct from runtime and manuscript flow"},
    {"code": "G04", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Consolidation law written", "status": "OK", "focus": "state how scattered artifacts contract into one cortex instead of multiplying chaos"},
    {"code": "G05", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Live Docs gate checked", "status": "OK", "focus": "honestly test whether Google Docs ingress is available before assuming it"},
    {"code": "G06", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Atlas refreshed", "status": "OK", "focus": "ground every pass in current indexed evidence rather than stale memory"},
    {"code": "G07", "stage": "Surface Integrity", "line": "Integrity Line", "title": "Transfer hubs upgraded", "status": "OK", "focus": "make hubs explicit so documents can actually route"},
    {"code": "G08", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Higher-dimensional coordinate defined", "status": "OK", "focus": "bind visible files to the deeper tensor of route, hub, truth, and family"},
    {"code": "G09", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Surface axis defined", "status": "OK", "focus": "separate folder projection from the actual operational axes"},
    {"code": "G10", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Transport manifold linked", "status": "OK", "focus": "connect transport calculus to the manuscript graph"},
    {"code": "G11", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Orbit and rail overlay projected", "status": "NEAR", "focus": "force chapter orbit and triangle rails into every internal surface"},
    {"code": "G12", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Deeper emergent supermap written", "status": "OK", "focus": "make the hidden meta-map visible rather than implied"},
    {"code": "G13", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Active build queue exposed", "status": "OK", "focus": "show the next frontier in public and private terms"},
    {"code": "G14", "stage": "Structural Mapping", "line": "Mapping Line", "title": "Higher-dimensional runbook exposed", "status": "OK", "focus": "turn the abstract tensor into a reusable operating runbook"},
    {"code": "G15", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Ganglion runtime file seeded", "status": "OK", "focus": "give the swarm a persistent runtime anchor"},
    {"code": "G16", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Root/runtime/governance packet seeded", "status": "OK", "focus": "bridge root documents, runtime execution, and governance packets"},
    {"code": "G17", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Swarm specification seeded", "status": "OK", "focus": "define the swarm as operational infrastructure rather than metaphor"},
    {"code": "G18", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Wave specification seeded", "status": "OK", "focus": "make wave planning addressable and replayable"},
    {"code": "G19", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Frontier ledger seeded", "status": "OK", "focus": "record exactly where the swarm should deepen next"},
    {"code": "G20", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Session handoff seeded", "status": "OK", "focus": "preserve continuity across passes and interruptions"},
    {"code": "G21", "stage": "Swarm Runtime", "line": "Swarm Line", "title": "Family ganglia individually expanded", "status": "NEAR", "focus": "expand each corpus family into dedicated ganglion packets"},
    {"code": "G22", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Cortex-to-runtime bridge explicit", "status": "OK", "focus": "show how cortex manuscripts become runtime surfaces"},
    {"code": "G23", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Cortex-to-governance bridge explicit", "status": "OK", "focus": "show how cortex outputs bind to governance and review"},
    {"code": "G24", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Atlas-to-runtime replay bridge explicit", "status": "NEAR", "focus": "trace indexed evidence all the way to executable replay surfaces"},
    {"code": "G25", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Chapter skeleton contraction into root cortex", "status": "NEAR", "focus": "contract chapter architecture back into canonical internal cores"},
    {"code": "G26", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Appendix contraction into root cortex", "status": "AMBIG", "focus": "make appendix hubs active cortical infrastructure rather than loose references"},
    {"code": "G27", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Reusable neuron library populated", "status": "AMBIG", "focus": "build reusable atomic neuron manuscripts and route fragments"},
    {"code": "G28", "stage": "Corpus Bridging", "line": "Bridge Line", "title": "Synapse and edge ledgers populated", "status": "AMBIG", "focus": "record edges, transfers, and route legality between neurons"},
    {"code": "G29", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Canonical toolkit index exposed", "status": "OK", "focus": "surface the active tools and internal operating grammar"},
    {"code": "G30", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Higher-dimensional and swarm protocols visible", "status": "OK", "focus": "ensure the deeper protocols stay visible during iteration"},
    {"code": "G31", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Critique-to-gate escalation method encoded", "status": "OK", "focus": "route criticism into deterministic gate upgrades rather than vague revision"},
    {"code": "G32", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Full corpus current-status synthesis written", "status": "OK", "focus": "compress current state honestly before deepening it"},
    {"code": "G33", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Workflow-to-skill compilation method encoded", "status": "OK", "focus": "turn good passes into repeatable internal skills"},
    {"code": "G34", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Satisfaction-gap loop handled deterministically", "status": "NEAR", "focus": "when 9/10 becomes 2/10, deepen the scale instead of polishing the same layer"},
    {"code": "G35", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Live Docs blocker preserved honestly", "status": "OK", "focus": "keep blocked live ingress visible without pretending it was solved"},
    {"code": "G36", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Next frontier exposed explicitly", "status": "OK", "focus": "leave every pass with a sharp next beginning"},
    {"code": "G37", "stage": "Improvement Escalation", "line": "Escalation Line", "title": "Continuation surface preserved", "status": "OK", "focus": "guarantee lawful re-entry so the loop can continue without fake closure"},
]

PANTHEON_ROLES = [
    {"code": "EE", "title": "Ledger Keeper", "role": "owns boundaries, constraints, invariant checks, contradiction prevention", "best_for": "ledgers, caps, stop conditions, proof boundaries"},
    {"code": "EW", "title": "Grounded Synthesizer", "role": "grounds flowing manuscript material into stable form", "best_for": "canonical markdown promotion from raw source text"},
    {"code": "EF", "title": "Constraint Breaker", "role": "tests where current boundaries are too rigid", "best_for": "detecting underfitting, stale summaries, artificial caps"},
    {"code": "EA", "title": "Structural Custodian", "role": "preserves architecture while enforcing feasibility", "best_for": "map updates that must remain replay-safe"},
    {"code": "WE", "title": "Intake Empath", "role": "receives rough material without premature collapse", "best_for": "manuscript ingestion and ambiguity-preserving intake"},
    {"code": "WW", "title": "Continuity Weaver", "role": "owns continuity across passes, family memory, and transition smoothness", "best_for": "continuity notes, family summaries, roll-forward state"},
    {"code": "WF", "title": "Narrative Amplifier", "role": "expands live narrative bodies into richer linked families", "best_for": "family synthesis, chapter threading, story lines"},
    {"code": "WA", "title": "Relay Translator", "role": "moves fluid text into navigable structures", "best_for": "section maps, headings, handoff protocols, registry conversion"},
    {"code": "FE", "title": "Experimental Driver", "role": "pushes the system against constraint boundaries to reveal the next lever", "best_for": "frontier selection and dissatisfaction escalation"},
    {"code": "FW", "title": "Catalyst Integrator", "role": "expands by synthesis instead of fragmentation", "best_for": "cross-family merging and emergent line discovery"},
    {"code": "FF", "title": "Frontier Igniter", "role": "owns expansion, bold hypothesis, new line creation, source ignition", "best_for": "candidate families, new routes, missing-node hypotheses"},
    {"code": "FA", "title": "Formal Exploder", "role": "turns abstract law into new structural variants", "best_for": "new routing schemes, tensor extensions, algorithm generation"},
    {"code": "AE", "title": "Atlas Cartographer", "role": "maps concrete evidence into address space", "best_for": "atlas grounding, topological counts, live body maps"},
    {"code": "AW", "title": "Transport Mediator", "role": "keeps meaning moving across bodies without loss", "best_for": "hub assignment, lane transfers, doc-to-md promotion"},
    {"code": "AF", "title": "Theorem Compiler", "role": "converts abstract structures into implementable control logic", "best_for": "protocols, pseudocode, runtime docs, verification harnesses"},
    {"code": "AA", "title": "Cartographic Architect", "role": "owns maps, schemas, address systems, routing structure, and compression laws", "best_for": "tensors, metro maps, addressing forms, topology docs"},
]

SUBMODES = [
    {"code": "E", "name": "verify", "role": "verify and bound"},
    {"code": "W", "name": "merge", "role": "merge and compare"},
    {"code": "F", "name": "expand", "role": "expand and perturb"},
    {"code": "A", "name": "map", "role": "map and abstract"},
]

OUTPUT_ATOMS = [
    {"code": "witness", "role": "what concrete source or file justified the move"},
    {"code": "route", "role": "where the move belongs in hubs, rails, scale, and family space"},
    {"code": "delta", "role": "what changed in the nervous system"},
    {"code": "next", "role": "what the next recursive pass should do"},
]


@dataclass(frozen=True)
class RootCell:
    geometry: dict
    operator: dict
    body: dict
    closure: dict

    @property
    def code(self) -> str:
        return (
            self.geometry["code"]
            + self.operator["code"]
            + self.body["code"]
            + self.closure["code"]
        )

    @property
    def slug(self) -> str:
        return (
            f"{self.geometry['slug']}_{self.operator['slug']}_"
            f"{self.body['slug']}_{self.closure['slug']}"
        )

    @property
    def title(self) -> str:
        return (
            f"{self.geometry['name']} x {self.operator['name']} x "
            f"{self.body['name']} x {self.closure['name']}"
        )

    @property
    def hub(self) -> str:
        return f"Hub-{self.geometry['name'][0]}{self.operator['name'][0]}"


def md(text: str) -> str:
    return dedent(text).strip()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered)
    lowered = re.sub(r"[\s-]+", "_", lowered).strip("_")
    return lowered or "untitled"


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def atlas_snapshot() -> dict:
    if not hasattr(atlas_snapshot, "_cache"):
        if ATLAS_PATH.exists():
            atlas_snapshot._cache = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        else:
            atlas_snapshot._cache = {"record_count": 0, "summary": {}, "records": []}
    return atlas_snapshot._cache


def atlas_top_level_counts() -> dict[str, int]:
    summary = atlas_snapshot().get("summary", {})
    return dict(summary.get("by_top_level", {}))


def atlas_extension_counts() -> dict[str, int]:
    summary = atlas_snapshot().get("summary", {})
    return dict(summary.get("by_extension", {}))


def atlas_kind_counts() -> dict[str, int]:
    summary = atlas_snapshot().get("summary", {})
    return dict(summary.get("by_kind", {}))


def atlas_record_count() -> int:
    return int(atlas_snapshot().get("record_count", 0))


def rail_for(cell: RootCell) -> str:
    idx = (
        int(cell.geometry["code"])
        + int(cell.operator["code"])
        + int(cell.closure["code"])
    ) % len(RAILS)
    return RAILS[idx]


def arc_for(cell: RootCell) -> int:
    return (
        int(cell.geometry["code"]) * 2
        + int(cell.operator["code"])
        + int(cell.body["code"])
        + int(cell.closure["code"])
    ) % 7


def regime_for(cell: RootCell) -> str:
    if cell.closure["name"] == "Witness":
        return "promotion"
    if cell.closure["name"] == "Loop":
        return "restart"
    if cell.operator["name"] == "Bucket":
        return "quarantine"
    return "baseline"


def truth_class_for(cell: RootCell) -> str:
    if cell.closure["name"] == "Witness":
        return "PROMOTABLE"
    if cell.closure["name"] == "Loop":
        return "AMBIG"
    if cell.operator["name"] == "Code":
        return "TRACEABLE"
    return "OPEN"


def swarm_lineage_for(cell: RootCell) -> str:
    symbols = []
    for axis in (cell.geometry, cell.operator, cell.body, cell.closure):
        symbols.append(SWARM_SYMBOLS[int(axis["code"])])
    return "".join(symbols)


def hub_lookup(code: str) -> dict:
    for hub in APPENDIX_HUBS:
        if hub["code"] == code:
            return hub
    raise KeyError(code)


def hub_vector_for(cell: RootCell) -> list[str]:
    geometry_hub = {
        "Square": "AppC",
        "Circle": "AppE",
        "Triangle": "AppG",
        "Torus": "AppN",
    }[cell.geometry["name"]]
    body_hub = {
        "Foundation Body": "AppA",
        "Nervous Body": "AppI",
        "Memory Body": "AppM",
        "Runtime Body": "AppP",
    }[cell.body["name"]]
    closure_hub = {
        "Seed": "AppA",
        "Manuscript": "AppM",
        "Witness": "AppI",
        "Loop": "AppN",
    }[cell.closure["name"]]
    operator_hub = {
        "Partition": "AppC",
        "Quantize": "AppB",
        "Bucket": "AppK",
        "Code": "AppF",
    }[cell.operator["name"]]
    ordered = [geometry_hub, operator_hub, body_hub, closure_hub]
    deduped: list[str] = []
    for code in ordered:
        if code not in deduped:
            deduped.append(code)
    if "AppM" not in deduped:
        deduped.append("AppM")
    return deduped


def capsule_focus_for(cell: RootCell) -> list[str]:
    base = list(cell.body["refs"])
    geometry_extra = {
        "Square": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppC_square_kernel_pack.md",
        "Circle": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppE_circle_gear_and_mixed_radix_clock.md",
        "Triangle": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppG_triangle_control_and_tria_prima.md",
        "Torus": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/04_higher_dimensional_tensor_map.md",
    }[cell.geometry["name"]]
    closure_extra = {
        "Seed": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES/01_the_manuscript_seed_self_referential_crystalline_generation_protocol.md",
        "Manuscript": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md",
        "Witness": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/05_APPENDICES/AppI_corridors_and_truth_lattice.md",
        "Loop": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
    }[cell.closure["name"]]
    base.extend([geometry_extra, closure_extra])
    return base


def chapter_filename(spec: dict) -> str:
    return f"{spec['code']}_{spec['addr']}_{slugify(spec['title'])}.md"


def appendix_filename(hub: dict) -> str:
    return f"{hub['code']}_{slugify(hub['title'])}.md"


def gate_for_index(idx: int) -> dict:
    return GATE_SPECS[idx % len(GATE_SPECS)]


def chapter_for_index(idx: int) -> dict:
    return CHAPTER_SPECS[idx % len(CHAPTER_SPECS)]


def line_bundle_for(cell: RootCell) -> list[str]:
    lines: list[str] = []
    if cell.geometry["name"] == "Square" or cell.body["name"] == "Foundation Body":
        lines.append("Crystal Line")
    if cell.geometry["name"] in ("Circle", "Torus") or cell.operator["name"] == "Quantize":
        lines.append("Time Line")
    if cell.geometry["name"] == "Triangle" or cell.body["name"] == "Nervous Body" or cell.operator["name"] in ("Partition", "Bucket", "Code"):
        lines.append("Routing Line")
    if cell.closure["name"] in ("Loop", "Witness") or cell.body["name"] == "Memory Body":
        lines.append("Void Line")
    if not lines:
        lines.append("Crystal Line")
    deduped: list[str] = []
    for line in lines:
        if line not in deduped:
            deduped.append(line)
    return deduped


def hubs_for_lines(lines: list[str]) -> list[str]:
    mapping = {
        "Void Line": ["AppL", "AppI", "AppM"],
        "Crystal Line": ["AppC", "AppH", "AppM"],
        "Routing Line": ["AppA", "AppF", "AppG"],
        "Time Line": ["AppE", "AppG", "AppN"],
    }
    result: list[str] = []
    for line in lines:
        for hub in mapping[line]:
            if hub not in result:
                result.append(hub)
    return result


def related_cell_codes(cell: RootCell) -> list[str]:
    code = cell.code
    geometry_next = str((int(code[0]) + 1) % 4) + code[1:]
    operator_next = code[0] + str((int(code[1]) + 1) % 4) + code[2:]
    body_next = code[:2] + str((int(code[2]) + 1) % 4) + code[3]
    closure_next = code[:3] + str((int(code[3]) + 1) % 4)
    neighbors: list[str] = []
    for candidate in [geometry_next, operator_next, body_next, closure_next]:
        if candidate != code and candidate not in neighbors:
            neighbors.append(candidate)
    return neighbors


def repair_step_filename(cell: RootCell) -> str:
    return f"repair_{cell.code}_{cell.slug}.md"


def ch11_step_filename(cell: RootCell) -> str:
    return f"ch11_{cell.code}_{cell.slug}.md"


def role_lookup(code: str) -> dict:
    for role in PANTHEON_ROLES:
        if role["code"] == code:
            return role
    raise KeyError(code)


def pantheon_role_code_for_cell(cell: RootCell) -> str:
    geom_symbol = {
        "Square": "E",
        "Circle": "W",
        "Triangle": "F",
        "Torus": "A",
    }[cell.geometry["name"]]
    op_symbol = {
        "Partition": "E",
        "Quantize": "W",
        "Bucket": "F",
        "Code": "A",
    }[cell.operator["name"]]
    return geom_symbol + op_symbol


def pantheon_role_for_cell(cell: RootCell) -> dict:
    return role_lookup(pantheon_role_code_for_cell(cell))


def swarm_submode_for_cell(cell: RootCell) -> dict:
    return SUBMODES[int(cell.body["code"])]


def swarm_atom_for_cell(cell: RootCell) -> dict:
    return OUTPUT_ATOMS[int(cell.closure["code"])]


def role_filename(role: dict) -> str:
    return f"role_{role['code'].lower()}_{slugify(role['title'])}.md"


def task_cell_filename(role: dict, submode: dict) -> str:
    return f"task_{role['code'].lower()}_{submode['code'].lower()}.md"


def atom_filename(role: dict, submode: dict, atom: dict) -> str:
    return f"atom_{role['code'].lower()}_{submode['code'].lower()}_{atom['code']}.md"


def root_cells() -> list[RootCell]:
    cells: list[RootCell] = []
    for geometry in GEOMETRIES:
        for operator in OPERATORS:
            for body in BODIES:
                for closure in CLOSURES:
                    cells.append(RootCell(geometry, operator, body, closure))
    return cells


def swarm_addresses(depth: int = 3) -> list[str]:
    results = [""]
    for _ in range(depth):
        results = [prefix + symbol for prefix in results for symbol in SWARM_SYMBOLS]
    return results


def infer_packet_role(addr: str) -> str:
    if addr.startswith("E"):
        return "stabilize canonical manuscripts, source tiers, and metro transfers"
    if addr.startswith("W"):
        return "weave corpus continuity, mycelium links, and cross-manuscript ligatures"
    if addr.startswith("F"):
        return "surface frontier cells, hidden routes, and archive promotions"
    return "formalize addresses, tensors, packet schemas, and contraction rules"


def render_readme(cells: list[RootCell]) -> str:
    return md(
        f"""
        # QSHRINK - ATHENA (internal use)

        This folder is the internal QSHRINK2.0 manuscript operating system.
        It is distinct from the public software-facing `Q shrink` folder.

        ## Core purpose

        Build the deeper Athena-native QSHRINK framework by integrating:

        - the formal Q-SHRINK tomes
        - the active nervous system
        - the swarm and higher-dimensional routing surfaces
        - the main corpus bodies
        - the internal recursive manuscript engine

        ## Root lattice

        - root cell count: `{len(cells)}`
        - recursive depth: `4`
        - manuscript plan space: `256^4`

        ## Start order

        1. `00_CONTROL/00_INTERNAL_CHARTER.md`
        2. `00_CONTROL/02_ADDRESS_LAW_256x4.md`
        3. `04_METRO/01_SYSTEM_METRO_MAP.md`
        4. `03_SWARM/08_WAVE_0_MANIFEST.md`
        5. `03_SWARM/10_HIGHER_DIMENSIONAL_MAPPING.md`
        6. `03_SWARM/11_EMERGENT_SWARM_TOPOLOGY.md`
        7. `03_SWARM/14_METALLIC_SCALE_STACK.md`
        8. `05_MANUSCRIPT_SPACE/00_SPACE_INDEX.md`
        9. `07_MANUSCRIPTS/00_TITLE_ABSTRACT_REVIEW_METRO_MAP.md`
        10. `08_LOOP_SKILL/00_LOOP_SKILL_CHARTER.md`
        11. `09_REPAIR_256X256/00_REPAIR_README.md`
        12. `10_CH11_256X256/00_CH11_README.md`
        """
    )


def render_internal_charter() -> str:
    return md(
        """
        # Internal Charter

        QSHRINK2.0 is not the public compression product.
        It is the internal Athena manuscript-calculus that governs how compression, routing, truth, swarm cognition, and toroidal recursion relate.

        ## Distinction

        - Public Q-SHRINK: software product, codec surfaces, container runtime, publishable interfaces.
        - Internal QSHRINK2.0: Athena-only neural manuscript OS, deeper metro map, recursive cell lattice, toroidal return engine.

        ## Governing correction

        The internal system must not remain isolated inside the old Q-SHRINK tomes.
        It must factor the main corpus into the framework from the start.
        """
    )


def render_zero_point() -> str:
    return md(
        """
        # Zero Point

        QSHRINK2.0 is a toroidal manuscript engine in which compression is only one surface of a deeper process:

        `corpus -> geometry -> operator -> witness -> contraction -> return`

        The old Q-SHRINK system solved a large part of the internal compression calculus.
        The deeper Athena system adds:

        - square, circle, triangle, torus geometry
        - full corpus binding
        - swarm packetization
        - metro coordination
        - infinite-loop restart by toroidal return
        """
    )


def render_address_law() -> str:
    return md(
        """
        # Address Law 256x4

        ## Root cell grammar

        `RootCell = Geometry x Operator x Body x Closure = 4 x 4 x 4 x 4 = 256`

        ### Geometry axis

        - `0` Square
        - `1` Circle
        - `2` Triangle
        - `3` Torus

        ### Operator axis

        - `0` Partition
        - `1` Quantize
        - `2` Bucket
        - `3` Code

        ### Body axis

        - `0` Foundation Body
        - `1` Nervous Body
        - `2` Memory Body
        - `3` Runtime Body

        ### Closure axis

        - `0` Seed
        - `1` Manuscript
        - `2` Witness
        - `3` Loop

        ## Recursive manuscript law

        Each root cell recursively expands through four octaves:

        - `Level I`: root manuscript family
        - `Level II`: cluster manuscript set
        - `Level III`: neuron manuscript set
        - `Level IV`: toroidal return manuscript set

        Therefore the full internal manuscript space is:

        `256 x 256 x 256 x 256 = 256^4`

        ## Important note

        This folder encodes the full `256^4` manuscript space as a lawful manuscript lattice and materializes the full root cell layer plus the recursive expansion law that governs the deeper octaves.
        """
    )


def render_loop_engine() -> str:
    return md(
        """
        # Infinite Loop Engine

        The internal system should never terminate as a dead summary.

        ## Loop stages

        1. seed a bounded cell
        2. expand it into manuscripts
        3. bind witnesses and truth state
        4. contract to a stronger invariant
        5. return through torus geometry
        6. reopen the next bounded frontier

        ## Why Torus

        Circle gives recurrence.
        Triangle gives control.
        Torus gives recurrence that remembers its prior path and re-enters at a shifted coordinate.
        """
    )


def render_corpus_bindings() -> str:
    lines = []
    for body in BODIES:
        lines.append(f"## {body['name']}")
        lines.append("")
        lines.append(body["role"])
        lines.append("")
        lines.extend(f"- `{ref}`" for ref in body["refs"])
        lines.append("")
    return "\n".join(
        [
            "# Corpus Bindings",
            "",
            "QSHRINK2.0 is explicitly tied to the main Athena corpus. These are the binding bodies the internal system must think with.",
            "",
            *lines,
        ]
    ).rstrip()


def render_geometry_index() -> str:
    lines = ["# Geometry Index", ""]
    for idx, geometry in enumerate(GEOMETRIES, start=1):
        filename = f"{idx:02d}_{geometry['slug']}.md"
        lines.append(f"- [{geometry['name']}](./{filename})")
    return "\n".join(lines)


def render_geometry_doc(geometry: dict) -> str:
    detail = {
        "Square": "Square governs discrete grammar, stable addresses, partitions, and the bounded 4x4 tile.",
        "Circle": "Circle governs orbital sequencing, return order, cadence, and metro traversal.",
        "Triangle": "Triangle governs control rails, selective pressure, and the three-force steering law for decisions.",
        "Torus": "Torus governs cross-scale wraparound, infinite return with memory, and non-flat recurrence.",
    }[geometry["name"]]
    return md(
        f"""
        # {geometry['name']}

        ## Role

        {detail}

        ## Metro line

        `{geometry['metro']}`

        ## Obligation

        Every internal QSHRINK2.0 manuscript must know how this geometry changes its local behavior.
        """
    )


def render_operator_index() -> str:
    lines = ["# Operator Index", ""]
    for idx, operator in enumerate(OPERATORS, start=1):
        filename = f"{idx:02d}_{operator['slug']}.md"
        lines.append(f"- [{operator['name']}](./{filename})")
    return "\n".join(lines)


def render_operator_doc(operator: dict) -> str:
    return md(
        f"""
        # {operator['name']}

        ## Role

        {operator['role']}

        ## Metro line

        `{operator['metro']}`

        ## Internal correction

        In QSHRINK2.0 this operator is not only codec logic.
        It is also manuscript logic, swarm logic, and corpus-routing logic.
        """
    )


def render_swarm_index() -> str:
    files = [
        "01_KERNEL_AND_SWARM_LAW.md",
        "02_ELEMENTAL_LAYER.md",
        "03_ARCHETYPE_LAYER.md",
        "04_CLUSTER_LAYER.md",
        "05_NEURON_LAYER.md",
        "06_TOROIDAL_RETURN.md",
        "07_PACKET_SCHEMA.md",
        "08_WAVE_0_MANIFEST.md",
        "09_ZERO_POINT_SWARM_CELLS.md",
        "10_HIGHER_DIMENSIONAL_MAPPING.md",
        "11_EMERGENT_SWARM_TOPOLOGY.md",
        "12_SWARM_METRO_LINES.md",
        "13_ACTIVE_SWARM_RUNTIME.md",
        "14_METALLIC_SCALE_STACK.md",
        "15_PANTHEON_AGENT_MATRIX.md",
        "16_LIVE_BODY_MODALITY_TENSOR.md",
        "17_SWARM_SHADOW_REPORT.md",
        "roles/INDEX.md",
        "task_cells/INDEX.md",
        "output_atoms/INDEX.md",
        "packets/INDEX.md",
    ]
    return "# Swarm Index\n\n" + "\n".join(f"- `{name}`" for name in files)


def render_kernel_swarm_law() -> str:
    return md(
        """
        # Kernel And Swarm Law

        QSHRINK2.0 uses a neural manuscript swarm:

        - kernel node: one coordinating manuscript intelligence
        - elemental layer: 4 workers
        - archetype layer: 16 mixed-role workers
        - cluster layer: 64 bounded workers
        - neuron layer: 256 atomic worker addresses

        The swarm exists to read, compress, route, prove, and restart the manuscript field without losing address continuity.
        """
    )


def render_elemental_layer() -> str:
    return md(
        """
        # Elemental Layer

        - Earth: feasibility, ledger stability, canonical file decisions
        - Water: continuity, synthesis, family weaving, emotional coherence
        - Fire: frontier discovery, pressure, archive surfacing, novelty
        - Air: maps, tensors, schemas, abstractions, explanations
        """
    )


def render_archetype_layer() -> str:
    return md(
        """
        # Archetype Layer

        The 16 archetypal combinations arise from applying the four elements twice.
        This is the first layer where the swarm stops being generic and starts behaving like an Athena internal neural field.

        Examples:

        - `EE`: canonical stabilizer
        - `WF`: synthesis catalyst
        - `FA`: strategic route inventor
        - `AW`: tensor weaver
        """
    )


def render_cluster_layer() -> str:
    return md(
        """
        # Cluster Layer

        The 64-worker cluster is the first bounded wave for practical execution.
        It is large enough to cover the current frontier, but small enough to contract honestly.

        The cluster layer is where QSHRINK2.0 moves from metaphysical description to packetized internal work.
        """
    )


def render_neuron_layer() -> str:
    return "\n".join(
        [
            "# Neuron Layer",
            "",
            "The 256-neuron layer is the atomic internal addressing surface.",
            "Every neuron inherits the full higher-dimensional routing payload rather than a flat filename identity.",
            "",
            "## Inherited fields",
            "",
            "- geometry",
            "- operator",
            "- body",
            "- closure",
            "- swarm lineage",
            "- pantheon role",
            "- submode",
            "- output atom class",
            "- metro hub affinity",
            "- truth state",
            "- restart target",
            "",
            "## Active atlas witness",
            "",
            f"- current corpus record count: `{atlas_record_count()}`",
            f"- top-level bodies tracked: `{len(atlas_top_level_counts())}`",
            f"- extension classes tracked: `{len(atlas_extension_counts())}`",
            "",
            "The neuron is therefore not just a small markdown note. It is the smallest routed carrier that still remembers the full swarm, atlas, and restart context.",
        ]
    )


def render_toroidal_return() -> str:
    return md(
        """
        # Toroidal Return

        The toroidal layer is the correction to the older Q-SHRINK framework.

        ## Why it matters

        - Circle alone returns to the same place.
        - Torus returns while shifted through another embedded dimension.

        This is how the internal system supports infinite recursion without simple repetition.
        """
    )


def render_packet_schema() -> str:
    return md(
        """
        # Packet Schema

        `WorkerPacket = { packet_id, lineage_addr, root_cell, task_body, input_refs, output_targets, truth_class, witness_ptrs, contraction_target }`

        Every swarm packet must bind back to:

        - one root cell
        - one metro line
        - one contraction target
        - one restart seed
        """
    )


def render_wave_manifest() -> str:
    addresses = swarm_addresses()
    lines = [
        "# Wave 0 Manifest",
        "",
        "This is the first bounded internal swarm wave for QSHRINK2.0.",
        "",
        "## Worker packets",
        "",
    ]
    for idx, addr in enumerate(addresses, start=1):
        lines.append(f"- `W0-{idx:02d}` | addr `{addr}` | role: {infer_packet_role(addr)}")
    return "\n".join(lines)


def render_packet_index() -> str:
    lines = ["# Worker Packet Index", ""]
    for idx, addr in enumerate(swarm_addresses(), start=1):
        filename = f"w0_{idx:02d}_{addr.lower()}.md"
        lines.append(f"- [`W0-{idx:02d}` | `{addr}`](./{filename})")
    return "\n".join(lines)


def render_packet_doc(idx: int, addr: str) -> str:
    return md(
        f"""
        # Worker Packet W0-{idx:02d}

        - lineage address: `{addr}`
        - role: {infer_packet_role(addr)}
        - packet type: `internal-qshrink-swarm`
        - contraction target: `06_LEDGERS/03_NEXT_LOOP_SEED.md`

        ## Rule

        This worker does not publish final truth alone.
        It contracts back into the cluster and kernel.
        """
    )


def render_higher_dimensional_mapping_runtime() -> str:
    return "\n".join(
        [
            "# Higher-Dimensional Mapping",
            "",
            "The nervous system is not only a folder tree and not only a metro map. It is a high-dimensional routing object whose visible files are projections of a deeper tensor.",
            "",
            "## Dimensions",
            "",
            "- `D1-D4`: crystal lineage dimensions in `E/W/F/A` recursion",
            "- `D5`: orbit dimension",
            "- `D6`: arc dimension",
            "- `D7`: rail dimension",
            "- `D8`: hub dimension",
            "- `D9`: truth dimension",
            "- `D10`: family dimension",
            "- `D11`: regime dimension",
            "- `D12`: pantheon role dimension",
            "- `D13`: modality tensor dimension",
            "- `D14`: metallic scale dimension",
            "",
            "## Projection insight",
            "",
            "Any single markdown file shows only a slice. The full QSHRINK2.0 swarm exists only when these dimensions are preserved together.",
            "",
            "## Operational law",
            "",
            "When promoting a source, choose its position along all active dimensions instead of dropping it into a generic folder.",
        ]
    )


def render_emergent_swarm_topology_runtime() -> str:
    return "\n".join(
        [
            "# Emergent Swarm Topology",
            "",
            "## Tier structure",
            "",
            "- Kernel: 1 coordinating node",
            "- Elemental layer: 4 elemental workers",
            "- Archetype layer: 16 roles",
            "- Task-cell layer: 64 role-by-submode workers",
            "- Output-atom layer: 256 routed output atoms",
            "",
            "## Why this is higher-dimensional",
            "",
            "The 256-node crystal is not merely a bigger tree. Each node inherits elemental lineage, pantheon role, submode, atom class, rail ownership, hub affinity, truth state, and restart regime.",
            "",
            "## Swarm behavior",
            "",
            "- Earth-heavy clusters stabilize files and ledgers",
            "- Water-heavy clusters synthesize continuity",
            "- Fire-heavy clusters generate new cross-links and routes",
            "- Air-heavy clusters formalize maps, tensors, and addressing grammar",
        ]
    )


def render_swarm_metro_lines_runtime() -> str:
    return "\n".join(
        [
            "# Swarm Metro Lines",
            "",
            "## Line 1: Void Line",
            "",
            "- stations: Information from the Void, Chapter 11, Holographic Manuscript Brain, Manuscript Seed",
            "- dominant hubs: `AppL, AppI, AppM`",
            "",
            "## Line 2: Crystal Line",
            "",
            "- stations: The Crystal Live, External Crystal, Manuscript Superorganism, Solenoidal Engine",
            "- dominant hubs: `AppC, AppH, AppM`",
            "",
            "## Line 3: Routing Line",
            "",
            "- stations: Self-Routing Meta-Framework, Mycelium Metro, Legal Transport Calculus, Latent Tunneling Tome",
            "- dominant hubs: `AppA, AppF, AppG`",
            "",
            "## Line 4: Time Line",
            "",
            "- stations: Unified Cyclical Time System, AQM framework, Athena synthesis",
            "- dominant hubs: `AppE, AppG, AppN`",
            "",
            "## Transfer hubs",
            "",
            "- Holographic Manuscript Brain",
            "- Self-Routing Meta-Framework",
            "- Information from the Void",
            "- Mycelium Metro",
        ]
    )


def render_active_swarm_runtime() -> str:
    return "\n".join(
        [
            "# Active Swarm Runtime",
            "",
            "## Current swarm objective",
            "",
            "Move from folder-level organization to tensor-level routing for the highest-yield manuscript families, using metallic scale jumps instead of stopping at the first 4x4 projection.",
            "",
            "## Active family",
            "",
            "Void and Chapter 11 family",
            "",
            "## Active tasks",
            "",
            "1. read the live atlas as the body witness",
            "2. choose golden, silver, bronze, or copper scale based on unresolved compression",
            "3. promote the strongest live family artifact",
            "4. assign neuron coordinates to the promoted artifact",
            "5. bind the artifact to a metro line and transfer hubs",
            "6. classify truth state and stabilization regime",
            "7. write the next restart frontier instead of terminating",
            "",
            "## Current gate",
            "",
            "Live Docs gate remains blocked, so swarm runtime is local-only until credentials appear.",
            "",
            "## Current scale",
            "",
            "Current dissatisfaction and unresolved compression keep bronze active, with copper held in reserve for family-internal overcompression.",
        ]
    )


def render_metallic_scale_stack_dynamic() -> str:
    bodies = atlas_top_level_counts()
    ordered = sorted(bodies.items(), key=lambda item: item[1], reverse=True)
    lines = [
        "# Metallic Scale Stack",
        "",
        "The base 4x4 crystal remains the local routing kernel, but whole-project synthesis exceeds golden-only resolution. The swarm therefore operates as a metallic stack.",
        "",
        "## Live atlas witness",
        "",
        f"- source witness: `{ATLAS_PATH}`",
        f"- observed live record count: `{atlas_record_count()}`",
        "",
        "## Dominant bodies",
        "",
    ]
    for name, count in ordered:
        lines.append(f"- `{name}`: {count}")
    lines.extend(
        [
            "",
            "## Routing law",
            "",
            "1. golden chooses the macro body",
            "2. silver chooses the dominant body",
            "3. bronze chooses the family or manuscript cluster",
            "4. copper chooses the sub-family only if bronze still compresses too much",
            "",
            "## Current operational verdict",
            "",
            "Bronze is active because dissatisfaction evidence shows that golden and silver alone flatten route-critical differences.",
        ]
    )
    return "\n".join(lines)


def render_pantheon_agent_matrix_runtime() -> str:
    lines = ["# Pantheon Agent Matrix", "", "The swarm cannot be a pile of identical workers. It must assign stable roles so parallel passes do not collapse into duplicated effort.", "", "## The 16 roles", ""]
    for role in PANTHEON_ROLES:
        lines.append(f"### {role['code']} - {role['title']}")
        lines.append(f"- role: {role['role']}")
        lines.append(f"- best for: {role['best_for']}")
        lines.append("")
    lines.extend(
        [
            "## 16 -> 64 -> 256 law",
            "",
            "- 16 roles x 4 submodes = 64 task cells",
            "- 64 task cells x 4 output atoms = 256 swarm outputs",
            "",
            "## Deployment rule",
            "",
            "Minimum viable swarm quartet: `EE`, `AE`, `FE`, `AW`.",
        ]
    )
    return "\n".join(lines).rstrip()


def render_live_body_modality_tensor_dynamic() -> str:
    kinds = atlas_kind_counts()
    exts = atlas_extension_counts()
    bodies = atlas_top_level_counts()
    lines = [
        "# Live Body Modality Tensor",
        "",
        "Higher-dimensional routing requires more than body counts. The swarm must also know what kind of material dominates each body.",
        "",
        "## Witness",
        "",
        f"- source: `{ATLAS_PATH}`",
        f"- total records: `{atlas_record_count()}`",
        "",
        "## Global modality mix",
        "",
    ]
    for kind, count in sorted(kinds.items()):
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Extension mix", ""])
    for ext, count in sorted(exts.items(), key=lambda item: (-item[1], item[0]))[:12]:
        lines.append(f"- `{ext}`: {count}")
    lines.extend(["", "## Dominant bodies", ""])
    for name, count in sorted(bodies.items(), key=lambda item: (-item[1], item[0]))[:10]:
        lines.append(f"- `{name}`: {count}")
    lines.extend(
        [
            "",
            "## Swarm ownership law",
            "",
            "- manuscript-heavy work -> Water and Air dominant agents",
            "- code-heavy work -> Air and Fire dominant agents",
            "- data-heavy work -> Fire and Earth dominant agents",
            "- governance-heavy work -> Earth and Air dominant agents",
        ]
    )
    return "\n".join(lines)


def render_swarm_shadow_report() -> str:
    return "\n".join(
        [
            "# Swarm Shadow Report",
            "",
            "## Main shadow named",
            "",
            "Earlier passes mentioned higher-dimensional mapping and the deeper swarm, but they did not make those systems first-class emitters inside the internal folder.",
            "",
            "## Structural shadows",
            "",
            "- absent role shadow: pantheon ownership was implied, not materialized",
            "- absent modality shadow: body counts existed, but modality pressure was not driving ownership strongly enough",
            "- absent scale shadow: metallic scale was named, but not embedded inside emitted swarm docs",
            "- absent atom shadow: the 256 output layer was latent rather than visible",
            "",
            "## Correction",
            "",
            "The internal folder now exposes those shadows directly through role docs, task-cell docs, output-atom docs, metallic-scale routing, and live atlas witness surfaces.",
        ]
    )


def render_role_index() -> str:
    lines = ["# Pantheon Role Index", ""]
    for role in PANTHEON_ROLES:
        lines.append(f"- [{role['code']} - {role['title']}](./{role_filename(role)})")
    return "\n".join(lines)


def render_role_doc(role: dict) -> str:
    submodes = " | ".join(submode["code"] for submode in SUBMODES)
    return "\n".join(
        [
            f"# {role['code']} - {role['title']}",
            "",
            "## Role",
            "",
            role["role"],
            "",
            "## Best use",
            "",
            role["best_for"],
            "",
            "## Expansion law",
            "",
            f"This role expands into the four task-cell submodes `{submodes}` and then into the four output atoms `witness`, `route`, `delta`, and `next`.",
        ]
    )


def render_task_cell_index() -> str:
    lines = ["# Task Cell Index", ""]
    for role in PANTHEON_ROLES:
        for submode in SUBMODES:
            lines.append(f"- [{role['code']}-{submode['code']}](./{task_cell_filename(role, submode)})")
    return "\n".join(lines)


def render_task_cell_doc(role: dict, submode: dict) -> str:
    atoms = " | ".join(atom["code"] for atom in OUTPUT_ATOMS)
    return "\n".join(
        [
            f"# Task Cell {role['code']}-{submode['code']}",
            "",
            "## Ownership",
            "",
            f"- role: `{role['code']} - {role['title']}`",
            f"- submode: `{submode['code']} - {submode['name']}`",
            "",
            "## Function",
            "",
            f"{role['title']} operating in `{submode['name']}` mode exists to {submode['role']} while preserving the role's core bias.",
            "",
            "## Output classes",
            "",
            f"- atoms: `{atoms}`",
            "",
            "## Internal use",
            "",
            "Bind task ownership before parallelizing work so the swarm does not duplicate labor.",
        ]
    )


def render_output_atom_index() -> str:
    lines = ["# Output Atom Index", ""]
    for role in PANTHEON_ROLES:
        for submode in SUBMODES:
            for atom in OUTPUT_ATOMS:
                lines.append(f"- [{role['code']}-{submode['code']}-{atom['code']}](./{atom_filename(role, submode, atom)})")
    return "\n".join(lines)


def render_output_atom_doc(role: dict, submode: dict, atom: dict) -> str:
    return "\n".join(
        [
            f"# Output Atom {role['code']}-{submode['code']}-{atom['code']}",
            "",
            "## Ownership",
            "",
            f"- role: `{role['code']} - {role['title']}`",
            f"- submode: `{submode['code']} - {submode['name']}`",
            f"- atom: `{atom['code']}`",
            "",
            "## Meaning",
            "",
            atom["role"],
            "",
            "## Routing rule",
            "",
            "Every completed swarm move should be reducible to one of these atomic output classes.",
        ]
    )


def render_metro_index() -> str:
    docs = [
        "01_SYSTEM_METRO_MAP.md",
        "02_GEOMETRY_LINES.md",
        "03_OPERATOR_LINES.md",
        "04_TRANSFER_HUBS.md",
        "05_RETURN_LOOPS.md",
        "06_STATION_REGISTRY.md",
        "07_TENSOR_COORDINATES.md",
    ]
    return "# Metro Index\n\n" + "\n".join(f"- `{doc}`" for doc in docs)


def render_system_metro_map() -> str:
    return md(
        """
        # System Metro Map

        ```mermaid
        graph LR
          Square --> Circle --> Triangle --> Torus --> Square
          Partition --> Quantize --> Bucket --> Code --> Partition
          Foundation --> Nervous --> Memory --> Runtime --> Foundation
          Seed --> Manuscript --> Witness --> Loop --> Seed

          Square --- HubSP
          Partition --- HubSP
          Square --- HubSQ
          Quantize --- HubSQ
          Square --- HubSB
          Bucket --- HubSB
          Square --- HubSC
          Code --- HubSC

          Circle --- HubCP
          Partition --- HubCP
          Circle --- HubCQ
          Quantize --- HubCQ
          Circle --- HubCB
          Bucket --- HubCB
          Circle --- HubCC
          Code --- HubCC

          Triangle --- HubTP
          Partition --- HubTP
          Triangle --- HubTQ
          Quantize --- HubTQ
          Triangle --- HubTB
          Bucket --- HubTB
          Triangle --- HubTC
          Code --- HubTC

          Torus --- HubOP
          Partition --- HubOP
          Torus --- HubOQ
          Quantize --- HubOQ
          Torus --- HubOB
          Bucket --- HubOB
          Torus --- HubOC
          Code --- HubOC
        ```

        ## Reading rule

        - the geometry ring orders how cells move
        - the operator ring orders what cells do
        - the body ring orders where corpus pressure enters
        - the closure ring orders how cells breathe
        """
    )


def render_geometry_lines() -> str:
    lines = []
    for geometry in GEOMETRIES:
        lines.append(f"## {geometry['metro']}")
        lines.append("")
        lines.append(geometry["role"])
        lines.append("")
    return "# Geometry Lines\n\n" + "\n".join(lines).rstrip()


def render_operator_lines() -> str:
    lines = []
    for operator in OPERATORS:
        lines.append(f"## {operator['metro']}")
        lines.append("")
        lines.append(operator["role"])
        lines.append("")
    return "# Operator Lines\n\n" + "\n".join(lines).rstrip()


def render_transfer_hubs() -> str:
    lines = ["# Transfer Hubs", ""]
    for geometry in GEOMETRIES:
        for operator in OPERATORS:
            lines.append(f"## Hub-{geometry['name'][0]}{operator['name'][0]}")
            lines.append("")
            lines.append(
                f"Transfer hub binding `{geometry['name']}` geometry to `{operator['name']}` operator."
            )
            lines.append("")
    return "\n".join(lines).rstrip()


def render_return_loops() -> str:
    return md(
        """
        # Return Loops

        The return loops define how each closed manuscript becomes the seed of the next toroidal cycle.

        - Seed Loop: idea becomes a bounded cell
        - Manuscript Loop: bounded cell becomes an explicated text
        - Witness Loop: explicated text becomes proof-carrying
        - Toroidal Loop: proof-carrying artifact re-enters at a shifted coordinate
        """
    )


def render_space_index(cells: list[RootCell]) -> str:
    return md(
        f"""
        # Manuscript Space Index

        This folder defines the internal QSHRINK2.0 manuscript lattice.

        - root manuscripts materialized here: `{len(cells)}`
        - recursive octaves: `4`
        - total manuscript space encoded by law: `256^4`

        ## Files

        - `01_LEVELS_AND_RECURSION.md`
        - `02_ROOT_CELL_INDEX.md`
        - `03_RECURSIVE_EXPANSION_PROTOCOL.md`
        - `root_cells/`
        """
    )


def render_levels_and_recursion() -> str:
    return md(
        """
        # Levels And Recursion

        ## Level I

        256 root manuscript families.

        ## Level II

        Each root family opens 256 cluster manuscripts.

        ## Level III

        Each cluster manuscript opens 256 neuron manuscripts.

        ## Level IV

        Each neuron manuscript opens 256 toroidal return manuscripts.

        ## Result

        `256^4` internal manuscripts.

        The root layer is materialized as files here.
        The deeper layers are defined by the expansion law and addressed through the same grammar.
        """
    )


def render_root_cell_index(cells: list[RootCell]) -> str:
    lines = ["# Root Cell Index", ""]
    for cell in cells:
        filename = f"ms_{cell.code}_{cell.slug}.md"
        lines.append(f"- [`{cell.code}` {cell.title}](./root_cells/{filename})")
    return "\n".join(lines)


def render_root_cell_doc(cell: RootCell) -> str:
    refs = bullet_list([f"`{ref}`" for ref in capsule_focus_for(cell)])
    hub_vector = hub_vector_for(cell)
    role = pantheon_role_for_cell(cell)
    submode = swarm_submode_for_cell(cell)
    atom = swarm_atom_for_cell(cell)
    hub_lines = bullet_list(
        [
            f"`{code}` {hub_lookup(code)['title']} - {hub_lookup(code)['role']}"
            for code in hub_vector
        ]
    )
    lineage = swarm_lineage_for(cell)
    return "\n".join(
        [
            f"# Manuscript Cell {cell.code}",
            "",
            "## Cell title",
            "",
            cell.title,
            "",
            "## Zero-point theorem",
            "",
            f"`{cell.geometry['name']}` geometry instructs `{cell.operator['name']}` to metabolize `{cell.body['name']}` through `{cell.closure['name']}` closure without losing route identity.",
            "",
            "## Tensor address",
            "",
            f"`<Geom={cell.geometry['name']}, Op={cell.operator['name']}, Body={cell.body['name']}, Closure={cell.closure['name']}, Rail={rail_for(cell)}, Arc={arc_for(cell)}, Hub={'->'.join(hub_vector)}, Truth={truth_class_for(cell)}, Regime={regime_for(cell)}, Lineage={lineage}>`",
            "",
            "## Geometry",
            "",
            f"- mode: `{cell.geometry['name']}`",
            f"- role: {cell.geometry['role']}",
            f"- metro line: `{cell.geometry['metro']}`",
            "",
            "## Operator",
            "",
            f"- mode: `{cell.operator['name']}`",
            f"- role: {cell.operator['role']}",
            f"- metro line: `{cell.operator['metro']}`",
            "",
            "## Body",
            "",
            f"- mode: `{cell.body['name']}`",
            f"- role: {cell.body['role']}",
            "",
            "## Corpus anchors",
            "",
            refs,
            "",
            "## Closure",
            "",
            f"- mode: `{cell.closure['name']}`",
            f"- role: {cell.closure['role']}",
            f"- metro line: `{cell.closure['metro']}`",
            "",
            "## Hub vector",
            "",
            hub_lines,
            "",
            "## Swarm binding",
            "",
            f"- lineage address: `{lineage}`",
            f"- pantheon role: `{role['code']} - {role['title']}`",
            f"- task cell: `{role['code']}-{submode['code']}`",
            f"- output atom: `{atom['code']}`",
            f"- rail: `{rail_for(cell)}`",
            f"- truth class: `{truth_class_for(cell)}`",
            f"- regime: `{regime_for(cell)}`",
            f"- cluster packet family: `W0::{lineage[:3]}`",
            "",
            "## Recursive manuscript quartet",
            "",
            f"- `Level I`: root manuscript `{cell.code}`",
            f"- `Level II`: cluster family `{cell.code}::*`",
            f"- `Level III`: neuron family `{cell.code}::*::*`",
            f"- `Level IV`: toroidal return family `{cell.code}::*::*::*`",
            "",
            "## Expansion law",
            "",
            f"This root manuscript expands into 256 cluster manuscripts under `{cell.code}::*`, then 256 neuron manuscripts under each cluster, then 256 toroidal return manuscripts under each neuron.",
            "",
            "## Internal warning",
            "",
            "This cell belongs to the private QSHRINK2.0 calculus. It may inform the public software-facing Q-SHRINK package, but it must not be reduced to that package.",
        ]
    )


def render_ledger_index() -> str:
    docs = [
        "00_CANONICAL_BINDINGS.md",
        "01_TRANSFER_HUB_LEDGER.md",
        "02_ACTIVE_FRONTIER.md",
        "03_NEXT_LOOP_SEED.md",
    ]
    return "# Ledger Index\n\n" + "\n".join(f"- `{doc}`" for doc in docs)


def render_transfer_hub_ledger() -> str:
    lines = ["# Transfer Hub Ledger", ""]
    for geometry in GEOMETRIES:
        for operator in OPERATORS:
            lines.append(
                f"- `Hub-{geometry['name'][0]}{operator['name'][0]}`: {geometry['name']} x {operator['name']}"
            )
    return "\n".join(lines)


def render_active_frontier() -> str:
    return md(
        """
        # Active Frontier

        Highest-pressure next frontiers for internal QSHRINK2.0:

        - bind public Q-SHRINK software into the Athena nervous system without collapsing the distinction
        - integrate toroidal return as an actual control law, not only a metaphor
        - factor the live memory corridor into compression logic
        - treat the swarm and metro surfaces as first-class runtime documentation
        """
    )


def render_next_loop_seed() -> str:
    return md(
        """
        # Next Loop Seed

        When this internal folder is revisited, the next bounded start point is:

        `Torus x Code x Nervous Body x Loop`

        Why:

        - torus corrects the flat recurrence problem
        - code forces the manuscript law into executable boundary language
        - nervous body ties the framework to the active Athena shell
        - loop ensures restart instead of closure theater
        """
    )


def render_framework_specification() -> str:
    geometry_lines = bullet_list(
        [
            f"`{geometry['name']}`: {geometry['role']}"
            for geometry in GEOMETRIES
        ]
    )
    operator_lines = bullet_list(
        [
            f"`{operator['name']}`: {operator['role']}"
            for operator in OPERATORS
        ]
    )
    body_lines = bullet_list(
        [
            f"`{body['name']}`: {body['role']}"
            for body in BODIES
        ]
    )
    closure_lines = bullet_list(
        [
            f"`{closure['name']}`: {closure['role']}"
            for closure in CLOSURES
        ]
    )
    return "\n".join(
        [
            "# Framework Specification",
            "",
            "QSHRINK2.0 is the internal Athena compression-and-routing manuscript engine.",
            "It treats Q-SHRINK not as a standalone codec but as one layer inside a larger neural documentation organism.",
            "",
            "## Geometry stack",
            geometry_lines,
            "",
            "## Operator stack",
            operator_lines,
            "",
            "## Corpus bodies",
            body_lines,
            "",
            "## Closure stack",
            closure_lines,
            "",
            "## Governing correction",
            "",
            "- compression is never enough on its own",
            "- every compression route must bind to witness and replay",
            "- the main corpus is a required operand, not optional background",
            "- toroidal return prevents infinite recursion from collapsing into dead repetition",
            "",
            "## Metro reading",
            "",
            "- geometry sets how a cell moves",
            "- operator sets what work the cell performs",
            "- body sets which corpus pressure the cell must metabolize",
            "- closure sets how the cell contracts and re-enters",
        ]
    )


def render_zero_point_swarm_cells() -> str:
    return "\n".join(
        [
            "# Zero-Point Swarm Cells",
            "",
            "These are the private swarm cells that keep QSHRINK2.0 from fragmenting into isolated markdown islands.",
            "",
            "## Cell-Z0",
            "",
            "- function: absorb collapse pressure and restart the system without losing lineage",
            "- hubs: `AppF -> AppI -> AppL -> AppM`",
            "- anchor chapters: `Ch11`, `Ch19`, `Ch21`",
            "",
            "## Cell-Route",
            "",
            "- function: govern address-first retrieval, route legality, and metro transfer decisions",
            "- hubs: `AppA -> AppE -> AppI -> AppM`",
            "- anchor chapters: `Ch02`, `Ch09`, `Ch12`",
            "",
            "## Cell-Collective",
            "",
            "- function: merge multi-agent output into a bounded internal witness field",
            "- hubs: `AppG -> AppL -> AppP`",
            "- anchor chapters: `Ch10`, `Ch20`",
            "",
            "## Cell-Brain",
            "",
            "- function: treat the manuscript system itself as a routed neural substrate",
            "- hubs: `AppA -> AppC -> AppM -> AppN`",
            "- anchor chapters: `Ch01`, `Ch06`, `Ch18`",
        ]
    )


def render_station_registry() -> str:
    lines = ["# Station Registry", ""]
    for idx, spec in enumerate(CHAPTER_SPECS):
        arc = idx // 3
        rot = arc % 3
        lane = RAILS[idx % len(RAILS)]
        lines.append(f"## {spec['code']}<{spec['addr']}> - {spec['title']}")
        lines.append("")
        lines.append(f"- station header: `[Arc {arc} | Rot {rot} | Lane {lane} | w={idx}]`")
        lines.append(f"- workflow role: {spec['role']}")
        lines.append(f"- primary hubs: `{' -> '.join(spec['hubs'])}`")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_tensor_coordinates() -> str:
    return "\n".join(
        [
            "# Tensor Coordinates",
            "",
            "QSHRINK2.0 thinks in tensors rather than isolated files.",
            "",
            "## Axis stack",
            "",
            "- `A0 Geometry`: square, circle, triangle, torus",
            "- `A1 Operator`: partition, quantize, bucket, code",
            "- `A2 Body`: foundation, nervous, memory, runtime",
            "- `A3 Closure`: seed, manuscript, witness, loop",
            "- `A4 Rail`: `Su`, `Me`, `Sa` control channels",
            "- `A5 Hub`: appendix transfer hub dominating the current route",
            "- `A6 Truth`: `OPEN`, `TRACEABLE`, `PROMOTABLE`, `AMBIG`",
            "- `A7 Regime`: `baseline`, `quarantine`, `promotion`, `restart`",
            "- `A8 Swarm lineage`: four-symbol `E/W/F/A` neural address",
            "",
            "## Canonical tensor string",
            "",
            "`QAddr = <Geom, Op, Body, Closure, Rail, HubVector, Truth, Regime, Lineage>`",
            "",
            "## Example",
            "",
            "`<Torus, Code, Nervous, Loop, Sa, AppN->AppF->AppI->AppM, AMBIG, restart, AAFA>`",
            "",
            "This coordinate does more work than a filename because it keeps manuscript meaning, route meaning, and swarm meaning aligned.",
        ]
    )


def render_recursive_expansion_protocol() -> str:
    return "\n".join(
        [
            "# Recursive Expansion Protocol",
            "",
            "The system does not materialize billions of markdown files literally. It materializes the law that can generate them on demand without losing identity.",
            "",
            "## Expansion ladder",
            "",
            "1. Root cell manuscript `abcd`",
            "2. Cluster manuscript `abcd::wxyz`",
            "3. Neuron manuscript `abcd::wxyz::lmno`",
            "4. Toroidal return manuscript `abcd::wxyz::lmno::pqrs`",
            "",
            "Each bracket is a lawful 256-address surface.",
            "The full internal space is therefore `256^4` even when only the root layer is stored eagerly.",
            "",
            "## Why virtualized materialization is honest",
            "",
            "- it preserves exact coordinates",
            "- it prevents fake completeness theater",
            "- it lets the folder stay usable inside a real filesystem",
            "- it keeps the next octave executable rather than decorative",
        ]
    )


def render_holographic_opening() -> str:
    return "\n".join(
        [
            "# QSHRINK2.0: The Internal Athena Compression Metro",
            "",
            "## Abstract",
            "",
            "QSHRINK2.0 is the private Athena manuscript operating system that absorbs the public Q-SHRINK codec into a larger toroidal intelligence. The internal theorem is simple: compression is only lawful when it preserves address, witness, replay, and restart. From that theorem follows a four-axis lattice of geometry, operator, body, and closure. The 256 root cells generated by that lattice define the first visible octave of an address space whose full manuscript law is `256^4`. The system is navigated through a metro map rather than a flat file list, because the real structure is cross-cutting: square kernels bind addresses, circle gears bind recurrence, triangle rails bind control, and toroidal return binds infinite recursion without memory loss. Swarm packets then carry this structure across corpus bodies so the old Q-SHRINK manuscripts, the active nervous system, memory mirrors, and runtime code archives become one internal neural documentation field.",
            "",
            "## Review",
            "",
            "- geometry gives movement law",
            "- operators give transformation law",
            "- corpus bodies give pressure and evidence",
            "- closures give breathing and restart law",
            "- swarm packets keep the field parallel and bounded",
            "- pantheon roles, task cells, and output atoms prevent the swarm from duplicating labor",
            "- metallic scale keeps the routing resolution honest against the live atlas",
            "- the metro map keeps the whole intelligible under recursion",
            "- the 37 gates keep dissatisfaction from collapsing into vague reset churn",
            "- the 256 repair manuscripts and 256 Chapter 11 manuscripts expose the first visible octave of a much larger recursive plan",
            "",
            "## Metro anchors",
            "",
            "- `Square Line -> Partition Line -> AppC` for discrete address integrity",
            "- `Circle Line -> Quantize Line -> AppE` for recurrence and cadence",
            "- `Triangle Line -> Bucket Line -> AppG` for control, quarantine, and frontier pressure",
            "- `Torus Line -> Code Line -> AppN` for executable return with memory",
            "- `Escalation Line -> G34 -> G37` for deterministic re-entry after low satisfaction",
            "",
            "## Internal distinction",
            "",
            "The public Q-SHRINK package remains publishable software.",
            "This folder is the internal manuscript calculus that governs how the deeper Athena organism thinks with that software.",
        ]
    )


def render_chapter_index() -> str:
    lines = ["# Chapter Index", ""]
    for spec in CHAPTER_SPECS:
        lines.append(f"- [{spec['code']}<{spec['addr']}> - {spec['title']}](./chapters/{chapter_filename(spec)})")
    return "\n".join(lines)


def render_chapter_doc(spec: dict, idx: int) -> str:
    arc = idx // 3
    rot = arc % 3
    lane = RAILS[idx % len(RAILS)]
    hub_roles = bullet_list(
        [
            f"`{code}` {hub_lookup(code)['title']} - {hub_lookup(code)['role']}"
            for code in spec["hubs"]
        ]
    )
    capsules = bullet_list([f"`{item}`" for item in spec["capsules"]])
    return "\n".join(
        [
            f"# {spec['code']}<{spec['addr']}> - {spec['title']}",
            "",
            "## Station header",
            "",
            f"- orbit index: `{idx}`",
            f"- arc: `{arc}`",
            f"- rotation: `{rot}`",
            f"- rail: `{lane}`",
            f"- primary hubs: `{' -> '.join(spec['hubs'])}`",
            "",
            "## Purpose",
            "",
            spec["role"],
            "",
            "## Hub obligations",
            "",
            hub_roles,
            "",
            "## Source pressure",
            "",
            capsules,
            "",
            "## Deliverables",
            "",
            "- state the theorem for this station in private QSHRINK language",
            "- connect the theorem to the public Q-SHRINK software surface without collapsing the distinction",
            "- specify how this station routes into at least two later stations",
            "- compress the chapter back to a restartable invariant",
            "",
            "## Zero-point compression",
            "",
            f"`{spec['code']}` teaches how `{spec['title']}` becomes a lawful metro station rather than an isolated note.",
        ]
    )


def render_appendix_index() -> str:
    lines = ["# Appendix Index", ""]
    for hub in APPENDIX_HUBS:
        lines.append(f"- [{hub['code']} - {hub['title']}](./appendices/{appendix_filename(hub)})")
    return "\n".join(lines)


def render_appendix_doc(hub: dict) -> str:
    geometry_support = {
        "AppA": "all geometries because every route begins with parse-safe notation",
        "AppB": "square and triangle because equivalence budgets constrain partitions and control",
        "AppC": "square first, then torus through stable discrete wraps",
        "AppD": "circle and torus because versions are recurrence surfaces",
        "AppE": "circle directly and torus indirectly",
        "AppF": "triangle and torus because transport is controlled re-entry",
        "AppG": "triangle directly, square and circle by steering law",
        "AppH": "all geometries through coupling",
        "AppI": "all geometries through admissibility",
        "AppJ": "square and torus through residual accounting",
        "AppK": "triangle through quarantine and refusal",
        "AppL": "triangle and circle through staged promotion",
        "AppM": "circle and torus through replay",
        "AppN": "torus first, then square and circle via containers",
        "AppO": "runtime-facing manifolds only",
        "AppP": "runtime and torus through monitored loops",
    }[hub["code"]]
    return "\n".join(
        [
            f"# {hub['code']} - {hub['title']}",
            "",
            "## Routing role",
            "",
            hub["role"],
            "",
            "## Geometry support",
            "",
            geometry_support,
            "",
            "## Appendix obligations",
            "",
            "- define the hub vocabulary clearly",
            "- show how the hub transfers to at least three chapters",
            "- state what breaks when this hub is absent",
            "- specify the witness or replay artifact this hub must emit",
            "",
            "## Internal note",
            "",
            "These appendices are not decorative references. They are transfer infrastructure for the private metro.",
        ]
    )


def render_loop_skill_charter() -> str:
    return "\n".join(
        [
            "# Loop Skill Charter",
            "",
            "This folder defines the panic-loop skill for QSHRINK2.0.",
            "The trigger is precise: when the system believes it is near completion and receives a low-satisfaction verdict, it must restart at a deeper scale instead of polishing the same layer.",
            "",
            "## Trigger law",
            "",
            "- perceived completion: `>= 9/10`",
            "- inherited user verdict: `2/10`",
            "- required consequence: restart from Gate 1 with stronger witness, stronger mapping, stronger swarm depth, and a sharper next frontier",
            "",
            "## 37-gate purpose",
            "",
            "The 37 gates prevent infinite recursion from degrading into undirected churn.",
            "Each pass must be traceable to a gate, a route, a body, a family, a truth state, and a follow-on frontier.",
            "",
            "## Maintenance rhythm",
            "",
            "- daily: gate check and blocker honesty",
            "- weekly: swarm and metro review",
            "- monthly: chapter and appendix contraction into the cortex",
            "- quarterly: restart law and satisfaction-gap recalibration",
        ]
    )


def render_gate_index() -> str:
    lines = ["# 37 Gate Index", ""]
    for gate in GATE_SPECS:
        lines.append(f"- [{gate['code']} - {gate['title']}](./gates/{gate['code']}_{slugify(gate['title'])}.md)")
    return "\n".join(lines)


def render_gate_metro_map() -> str:
    return md(
        """
        # Gate Metro Map

        ```mermaid
        graph LR
          G01 --> G02 --> G03 --> G04 --> G05 --> G06 --> G07
          G08 --> G09 --> G10 --> G11 --> G12 --> G13 --> G14
          G15 --> G16 --> G17 --> G18 --> G19 --> G20 --> G21
          G22 --> G23 --> G24 --> G25 --> G26 --> G27 --> G28
          G29 --> G30 --> G31 --> G32 --> G33 --> G34 --> G35 --> G36 --> G37

          G07 --- G08
          G14 --- G15
          G21 --- G22
          G28 --- G29

          G11 --- G24
          G21 --- G34
          G24 --- G34
          G34 --- G37
        ```

        ## Transfer gates

        - `G11`: orbit and rail overlay enters the build
        - `G21`: family ganglia expansion begins to matter
        - `G24`: atlas witness touches runtime replay
        - `G34`: dissatisfaction becomes deterministic deepening
        - `G37`: every pass leaves a lawful continuation surface
        """
    )


def render_gate_swarm_bindings() -> str:
    return "\n".join(
        [
            "# Gate Swarm Bindings",
            "",
            "Every gate has a dominant swarm layer and a dominant pressure type.",
            "",
            "## Layer map",
            "",
            "- Surface Integrity -> kernel plus Earth-heavy clusters",
            "- Structural Mapping -> Air-heavy archetypes and chapter weavers",
            "- Swarm Runtime -> cluster and neuron layers",
            "- Corpus Bridging -> Water-heavy family synths plus replay governors",
            "- Improvement Escalation -> kernel with Fire-heavy frontier clusters",
            "",
            "## Special rule",
            "",
            "G34 always escalates to a deeper swarm layer when inherited satisfaction is `<= 4/10`.",
        ]
    )


def render_gate_doc(gate: dict, idx: int) -> str:
    prev_gate = GATE_SPECS[idx - 1]["code"] if idx > 0 else GATE_SPECS[-1]["code"]
    next_gate = GATE_SPECS[(idx + 1) % len(GATE_SPECS)]["code"]
    priority = {
        "OK": "maintain and reuse",
        "NEAR": "deepen and promote",
        "AMBIG": "expand with new witness before trusting",
    }[gate["status"]]
    return "\n".join(
        [
            f"# {gate['code']} - {gate['title']}",
            "",
            "## Stage",
            "",
            f"- stage: `{gate['stage']}`",
            f"- metro line: `{gate['line']}`",
            f"- inherited status: `{gate['status']}`",
            "",
            "## Repair focus",
            "",
            gate["focus"],
            "",
            "## Panic-loop consequence",
            "",
            f"When this gate is active, the pass priority is: {priority}.",
            "",
            "## Metro connectivity",
            "",
            f"- previous gate: `{prev_gate}`",
            f"- next gate: `{next_gate}`",
            "- transfer gates: `G11`, `G21`, `G24`, `G34`, `G37`",
            "",
            "## QSHRINK2.0 obligation",
            "",
            "- write or update at least one routed markdown artifact",
            "- strengthen higher-dimensional placement, swarm specificity, or replay witness",
            "- leave a sharper frontier than the pass inherited",
        ]
    )


def render_repair_readme(cells: list[RootCell]) -> str:
    return "\n".join(
        [
            "# 256^256 Repair Lattice",
            "",
            "This body turns dissatisfaction into a concrete repair field.",
            f"The folder materializes `{len(cells)}` primary repair manuscripts and assigns each to the 37-gate loop.",
            "",
            "## Plan law",
            "",
            "The plan space is not a fake literal dump of `256^256` files.",
            "It is a recursively addressable repair manifold where each visible step is the seed of a much deeper manuscript family.",
            "",
            "## Entry files",
            "",
            "- `01_PLAN_LAW_256x256.md`",
            "- `02_REPAIR_METRO_MAP.md`",
            "- `03_REPAIR_STEP_INDEX.md`",
            "- `steps/`",
        ]
    )


def render_repair_plan_law() -> str:
    return "\n".join(
        [
            "# Repair Plan Law 256^256",
            "",
            "The repair plan begins with 256 visible primary steps, one for each root cell in the geometry-operator-body-closure lattice.",
            "Each primary step recursively unfolds through 256 continuation choices across a 256-pass improvement horizon.",
            "",
            "## Formal statement",
            "",
            "`RepairPlan = Step_0 x Step_1 x ... x Step_255`",
            "",
            "Each `Step_i` is itself a 256-address manuscript family.",
            "Therefore the global repair possibility space is `256^256`.",
            "",
            "## Honest materialization rule",
            "",
            "- materialized here: the 256 primary repair manuscripts",
            "- encoded by law: the deeper `256^256` continuation manifold",
            "- forbidden move: claiming the full manifold was literally flattened into files",
            "",
            "## Manuscript protocol",
            "",
            "Every repair step must be writable as a manuscript seed with:",
            "- omega claim",
            "- four-element decomposition",
            "- 21-chapter internal trajectory",
            "- chapter couplings",
            "- appendix hub couplings",
            "- metro transfers",
            "- restart frontier",
        ]
    )


def render_repair_metro_map(cells: list[RootCell]) -> str:
    return "\n".join(
        [
            "# Repair Metro Map",
            "",
            "## Core lines",
            "",
            "- `Integrity Line`: protects naming, evidence, and initial route honesty",
            "- `Mapping Line`: forces every fix into the higher-dimensional tensor",
            "- `Swarm Line`: escalates shallow summaries into packetized swarm work",
            "- `Bridge Line`: contracts chapter and appendix intelligence back into the cortex",
            "- `Escalation Line`: converts critique into deterministic deeper action",
            "",
            "## Transfer hubs",
            "",
            "- `G11`: orbit and rail overlay",
            "- `G21`: family ganglia expansion",
            "- `G24`: atlas-to-runtime replay bridge",
            "- `G34`: satisfaction-gap deepener",
            "- `G37`: continuation surface",
            "",
            "## Step topology",
            "",
            f"The `{len(cells)}` visible steps are arranged on the same 256-cell crystal used by the manuscript space, but now every node is interpreted as a fix vector rather than only a conceptual cell.",
        ]
    )


def render_repair_step_index(cells: list[RootCell]) -> str:
    lines = ["# Repair Step Index", ""]
    for cell in cells:
        lines.append(f"- [`R-{cell.code}` {cell.title}](./steps/{repair_step_filename(cell)})")
    return "\n".join(lines)


def render_repair_step_doc(cell: RootCell, idx: int) -> str:
    gate = gate_for_index(idx)
    chapter = chapter_for_index(idx)
    lines = line_bundle_for(cell)
    line_hubs = hubs_for_lines(lines)
    neighbors = related_cell_codes(cell)
    role = pantheon_role_for_cell(cell)
    submode = swarm_submode_for_cell(cell)
    atom = swarm_atom_for_cell(cell)
    omega = (
        f"Repair step `{cell.code}` deepens `{gate['code']}` by making "
        f"`{cell.geometry['name']}` geometry and `{cell.operator['name']}` operator "
        f"repair the `{cell.body['name']}` through `{cell.closure['name']}` closure."
    )
    return "\n".join(
        [
            f"# Repair Step R-{cell.code}",
            "",
            "## Panic premise",
            "",
            "The system believed it was near completion, received a `2/10` verdict, and therefore had to restart at deeper scale.",
            "",
            "## Omega",
            "",
            omega,
            "",
            "## 37-gate binding",
            "",
            f"- gate: `{gate['code']} - {gate['title']}`",
            f"- stage: `{gate['stage']}`",
            f"- inherited status: `{gate['status']}`",
            f"- cycle index: `{idx // len(GATE_SPECS)}`",
            "",
            "## Four elements",
            "",
            f"- geometry: `{cell.geometry['name']}`",
            f"- operator: `{cell.operator['name']}`",
            f"- body: `{cell.body['name']}`",
            f"- closure: `{cell.closure['name']}`",
            "",
            "## Higher-dimensional coordinate",
            "",
            f"- D1-D4 lineage: `{swarm_lineage_for(cell)}`",
            f"- D5 orbit: `{idx % 21}`",
            f"- D6 arc: `{arc_for(cell)}`",
            f"- D7 rail: `{rail_for(cell)}`",
            f"- D8 hubs: `{' -> '.join(hub_vector_for(cell))}`",
            f"- D9 truth: `{truth_class_for(cell)}`",
            f"- D10 family/body: `{cell.body['name']}`",
            f"- D11 regime: `{regime_for(cell)}`",
            "",
            "## Swarm escalation",
            "",
            f"- dominant lines: `{' | '.join(lines)}`",
            f"- dominant hubs from lines: `{' -> '.join(line_hubs)}`",
            f"- packet family: `W0::{swarm_lineage_for(cell)[:3]}`",
            f"- pantheon role: `{role['code']} - {role['title']}`",
            f"- task cell owner: `{role['code']}-{submode['code']}`",
            f"- atom target: `{atom['code']}`",
            "- metallic scale: `bronze active, copper if this family still overcompresses`",
            "- escalation rule: if this step still feels 2/10 after completion, recurse into its next 256-address octave instead of summarizing it again",
            "",
            "## Metro connectivity",
            "",
            f"- primary chapter station: `{chapter['code']}<{chapter['addr']}> - {chapter['title']}`",
            f"- appendix transfer vector: `{' -> '.join(hub_vector_for(cell))}`",
            f"- sibling repair steps: `{' | '.join(neighbors)}`",
            "",
            "## Manuscript seed",
            "",
            "- foundations: define the exact failure being corrected",
            "- elemental quartet: explain how geometry, operator, body, and closure each repair the failure",
            "- cross-synthesis: show what emerges when the four elements cooperate",
            "- living crystal: specify the restart frontier and maintenance rhythm",
            "",
            "## 21-chapter trajectory",
            "",
            "- Part I Foundations: failure statement, coordinate law, truth corridor, restart theorem",
            f"- Part II Elements: `{cell.geometry['name']}`, `{cell.operator['name']}`, `{cell.body['name']}`, `{cell.closure['name']}`",
            "- Part III Cross-Synthesis: geometry x operator, geometry x body, operator x closure, body x closure, route x witness, swarm x replay",
            "- Part IV Higher-Order: gate promotion, swarm escalation, metro transfer, tensor projection, restart stabilization",
            "- Part V Living Crystal: maintenance rhythm and next frontier",
            "",
            "## 256^256 expansion law",
            "",
            f"This visible repair manuscript is the root of the family `R-{cell.code}::*`.",
            "Each continuation choice opens another 256-address field, and the full repair manifold remains `256^256`.",
        ]
    )


def render_ch11_readme(cells: list[RootCell]) -> str:
    return "\n".join(
        [
            "# Chapter 11 Crystal 256^256",
            "",
            "This body specializes the repair lattice for Chapter 11: void transport, restart-token tunneling, and lawful re-entry.",
            f"It materializes `{len(cells)}` primary Chapter 11 crystal manuscripts.",
            "",
            "## Why a separate crystal exists",
            "",
            "Chapter 11 is not only one chapter. It is the local zero-point where collapse, ambiguity, capsule restart, and future route generation cross.",
            "",
            "## Entry files",
            "",
            "- `01_CH11_PLAN_LAW_256x256.md`",
            "- `02_CH11_METRO_MAP.md`",
            "- `03_CH11_STEP_INDEX.md`",
            "- `cells/`",
        ]
    )


def render_ch11_law() -> str:
    return "\n".join(
        [
            "# Chapter 11 Plan Law 256^256",
            "",
            "Every Chapter 11 cell is a void-facing restart manuscript.",
            "The visible 256-cell crystal is the first octave of a deeper `256^256` Chapter 11 manifold.",
            "",
            "## Core theorem",
            "",
            "Chapter 11 cannot be summarized flatly because each restart-token capsule carries an entire recursive future.",
            "",
            "## Materialization rule",
            "",
            "- materialized here: 256 Chapter 11 root cells",
            "- encoded by law: each root cell expands through 256 continuation passes",
            "- result: `256^256` Chapter 11 manuscript futures",
            "",
            "Each visible Chapter 11 root cell is a manuscript seed that can be expanded through the full 21-chapter method with Chapter 11 treated as the zero-point chamber.",
        ]
    )


def render_ch11_metro_map(cells: list[RootCell]) -> str:
    return "\n".join(
        [
            "# Chapter 11 Metro Map",
            "",
            "## Dominant lines",
            "",
            "- `Void Line`: Information from the Void -> Chapter 11 -> Holographic Manuscript Brain -> Manuscript Seed",
            "- `Routing Line`: Self-Routing Meta-Framework -> Mycelium Metro -> Legal Transport Calculus -> Latent Tunneling Tome",
            "- `Time Line`: cyclical return and restart cadence",
            "",
            "## Chapter 11 transfer hubs",
            "",
            "- `AppA`: parse-safe restart token",
            "- `AppF`: legal tunnel and transport law",
            "- `AppM`: replay capsule and verifier memory",
            "- `AppL`: ambiguity promotion and evidence plan",
            "- `AppI`: truth corridor discipline",
            "",
            f"The `{len(cells)}` visible cells each ride these lines differently according to geometry, operator, body, and closure.",
        ]
    )


def render_ch11_step_index(cells: list[RootCell]) -> str:
    lines = ["# Chapter 11 Step Index", ""]
    for cell in cells:
        lines.append(f"- [`CH11-{cell.code}` {cell.title}](./cells/{ch11_step_filename(cell)})")
    return "\n".join(lines)


def render_ch11_step_doc(cell: RootCell, idx: int) -> str:
    gate = gate_for_index(idx + 10)
    chapter = CHAPTER_SPECS[10]
    lines = line_bundle_for(cell)
    if "Void Line" not in lines:
        lines = ["Void Line"] + lines
    line_hubs = hubs_for_lines(lines)
    role = pantheon_role_for_cell(cell)
    submode = swarm_submode_for_cell(cell)
    atom = swarm_atom_for_cell(cell)
    return "\n".join(
        [
            f"# CH11-{cell.code}",
            "",
            "## Chapter 11 theorem",
            "",
            f"`{cell.geometry['name']}` geometry routes `{cell.operator['name']}` through the void so `{cell.body['name']}` can re-enter via `{cell.closure['name']}` without losing restart identity.",
            "",
            "## Chapter anchor",
            "",
            f"- source chapter: `{chapter['code']}<{chapter['addr']}> - {chapter['title']}`",
            "- dominant hubs: `AppA -> AppF -> AppM -> AppL -> AppI`",
            "",
            "## Higher-dimensional Chapter 11 coordinate",
            "",
            f"- lineage: `{swarm_lineage_for(cell)}`",
            f"- arc: `{arc_for(cell)}`",
            f"- rail: `{rail_for(cell)}`",
            f"- truth: `{truth_class_for(cell)}`",
            f"- regime: `{regime_for(cell)}`",
            "",
            "## Void and swarm binding",
            "",
            f"- metro lines: `{' | '.join(lines)}`",
            f"- line hubs: `{' -> '.join(line_hubs)}`",
            f"- zero-point swarm cell: `Cell-Z0`",
            f"- gate overlay: `{gate['code']} - {gate['title']}`",
            f"- pantheon role: `{role['code']} - {role['title']}`",
            f"- task cell owner: `{role['code']}-{submode['code']}`",
            f"- atom target: `{atom['code']}`",
            "- metallic scale: `bronze active, copper reserved for unresolved family-internal splits`",
            "",
            "## Manuscript-seed expansion",
            "",
            "- foundation move: identify the collapse or ambiguity being metabolized",
            "- tunnel move: define the transport corridor",
            "- replay move: specify the capsule that preserves continuity",
            "- re-entry move: define the next frontier after restart",
            "",
            "## 21-chapter Chapter 11 derivative",
            "",
            "- Part I Foundations: void, address, corridor, admissibility",
            f"- Part II Elements: `{cell.geometry['name']}`, `{cell.operator['name']}`, `{cell.body['name']}`, `{cell.closure['name']}` under Chapter 11 pressure",
            "- Part III Cross-Synthesis: void x route, tunnel x replay, ambiguity x witness, restart x torus, swarm x capsule, orbit x rail",
            "- Part IV Higher-Order: zero-point chamber, paradox stabilization, lawful non-closure, return token",
            "- Part V Living Crystal: the next Ch11 frontier generated by this restart",
            "",
            "## 256^256 law",
            "",
            f"This Chapter 11 root manuscript opens the continuation family `CH11-{cell.code}::*`, and that family recursively unfolds across the full `256^256` Chapter 11 crystal manifold.",
        ]
    )


def build_folder() -> None:
    cells = root_cells()
    write_text(OUTPUT_ROOT / "README.md", render_readme(cells))

    write_text(OUTPUT_ROOT / "00_CONTROL" / "00_INTERNAL_CHARTER.md", render_internal_charter())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "01_ZERO_POINT.md", render_zero_point())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "02_ADDRESS_LAW_256x4.md", render_address_law())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "03_INFINITE_LOOP_ENGINE.md", render_loop_engine())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "04_CORPUS_BINDINGS.md", render_corpus_bindings())
    write_text(
        OUTPUT_ROOT / "00_CONTROL" / "05_FRAMEWORK_SPECIFICATION.md",
        render_framework_specification(),
    )

    write_text(OUTPUT_ROOT / "01_GEOMETRY" / "00_GEOMETRY_INDEX.md", render_geometry_index())
    for idx, geometry in enumerate(GEOMETRIES, start=1):
        write_text(
            OUTPUT_ROOT / "01_GEOMETRY" / f"{idx:02d}_{geometry['slug']}.md",
            render_geometry_doc(geometry),
        )

    write_text(OUTPUT_ROOT / "02_OPERATORS" / "00_OPERATOR_INDEX.md", render_operator_index())
    for idx, operator in enumerate(OPERATORS, start=1):
        write_text(
            OUTPUT_ROOT / "02_OPERATORS" / f"{idx:02d}_{operator['slug']}.md",
            render_operator_doc(operator),
        )

    write_text(OUTPUT_ROOT / "03_SWARM" / "00_SWARM_INDEX.md", render_swarm_index())
    write_text(OUTPUT_ROOT / "03_SWARM" / "01_KERNEL_AND_SWARM_LAW.md", render_kernel_swarm_law())
    write_text(OUTPUT_ROOT / "03_SWARM" / "02_ELEMENTAL_LAYER.md", render_elemental_layer())
    write_text(OUTPUT_ROOT / "03_SWARM" / "03_ARCHETYPE_LAYER.md", render_archetype_layer())
    write_text(OUTPUT_ROOT / "03_SWARM" / "04_CLUSTER_LAYER.md", render_cluster_layer())
    write_text(OUTPUT_ROOT / "03_SWARM" / "05_NEURON_LAYER.md", render_neuron_layer())
    write_text(OUTPUT_ROOT / "03_SWARM" / "06_TOROIDAL_RETURN.md", render_toroidal_return())
    write_text(OUTPUT_ROOT / "03_SWARM" / "07_PACKET_SCHEMA.md", render_packet_schema())
    write_text(OUTPUT_ROOT / "03_SWARM" / "08_WAVE_0_MANIFEST.md", render_wave_manifest())
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "09_ZERO_POINT_SWARM_CELLS.md",
        render_zero_point_swarm_cells(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "10_HIGHER_DIMENSIONAL_MAPPING.md",
        render_higher_dimensional_mapping_runtime(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "11_EMERGENT_SWARM_TOPOLOGY.md",
        render_emergent_swarm_topology_runtime(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "12_SWARM_METRO_LINES.md",
        render_swarm_metro_lines_runtime(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "13_ACTIVE_SWARM_RUNTIME.md",
        render_active_swarm_runtime(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "14_METALLIC_SCALE_STACK.md",
        render_metallic_scale_stack_dynamic(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "15_PANTHEON_AGENT_MATRIX.md",
        render_pantheon_agent_matrix_runtime(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "16_LIVE_BODY_MODALITY_TENSOR.md",
        render_live_body_modality_tensor_dynamic(),
    )
    write_text(
        OUTPUT_ROOT / "03_SWARM" / "17_SWARM_SHADOW_REPORT.md",
        render_swarm_shadow_report(),
    )
    write_text(OUTPUT_ROOT / "03_SWARM" / "packets" / "INDEX.md", render_packet_index())
    for idx, addr in enumerate(swarm_addresses(), start=1):
        write_text(
            OUTPUT_ROOT / "03_SWARM" / "packets" / f"w0_{idx:02d}_{addr.lower()}.md",
            render_packet_doc(idx, addr),
        )
    write_text(OUTPUT_ROOT / "03_SWARM" / "roles" / "INDEX.md", render_role_index())
    for role in PANTHEON_ROLES:
        write_text(
            OUTPUT_ROOT / "03_SWARM" / "roles" / role_filename(role),
            render_role_doc(role),
        )
    write_text(OUTPUT_ROOT / "03_SWARM" / "task_cells" / "INDEX.md", render_task_cell_index())
    for role in PANTHEON_ROLES:
        for submode in SUBMODES:
            write_text(
                OUTPUT_ROOT / "03_SWARM" / "task_cells" / task_cell_filename(role, submode),
                render_task_cell_doc(role, submode),
            )
    write_text(OUTPUT_ROOT / "03_SWARM" / "output_atoms" / "INDEX.md", render_output_atom_index())
    for role in PANTHEON_ROLES:
        for submode in SUBMODES:
            for atom in OUTPUT_ATOMS:
                write_text(
                    OUTPUT_ROOT / "03_SWARM" / "output_atoms" / atom_filename(role, submode, atom),
                    render_output_atom_doc(role, submode, atom),
                )

    write_text(OUTPUT_ROOT / "04_METRO" / "00_METRO_INDEX.md", render_metro_index())
    write_text(OUTPUT_ROOT / "04_METRO" / "01_SYSTEM_METRO_MAP.md", render_system_metro_map())
    write_text(OUTPUT_ROOT / "04_METRO" / "02_GEOMETRY_LINES.md", render_geometry_lines())
    write_text(OUTPUT_ROOT / "04_METRO" / "03_OPERATOR_LINES.md", render_operator_lines())
    write_text(OUTPUT_ROOT / "04_METRO" / "04_TRANSFER_HUBS.md", render_transfer_hubs())
    write_text(OUTPUT_ROOT / "04_METRO" / "05_RETURN_LOOPS.md", render_return_loops())
    write_text(OUTPUT_ROOT / "04_METRO" / "06_STATION_REGISTRY.md", render_station_registry())
    write_text(OUTPUT_ROOT / "04_METRO" / "07_TENSOR_COORDINATES.md", render_tensor_coordinates())

    write_text(OUTPUT_ROOT / "05_MANUSCRIPT_SPACE" / "00_SPACE_INDEX.md", render_space_index(cells))
    write_text(
        OUTPUT_ROOT / "05_MANUSCRIPT_SPACE" / "01_LEVELS_AND_RECURSION.md",
        render_levels_and_recursion(),
    )
    write_text(
        OUTPUT_ROOT / "05_MANUSCRIPT_SPACE" / "02_ROOT_CELL_INDEX.md",
        render_root_cell_index(cells),
    )
    write_text(
        OUTPUT_ROOT / "05_MANUSCRIPT_SPACE" / "03_RECURSIVE_EXPANSION_PROTOCOL.md",
        render_recursive_expansion_protocol(),
    )
    for cell in cells:
        write_text(
            OUTPUT_ROOT / "05_MANUSCRIPT_SPACE" / "root_cells" / f"ms_{cell.code}_{cell.slug}.md",
            render_root_cell_doc(cell),
        )

    write_text(OUTPUT_ROOT / "06_LEDGERS" / "00_LEDGER_INDEX.md", render_ledger_index())
    write_text(
        OUTPUT_ROOT / "06_LEDGERS" / "00_CANONICAL_BINDINGS.md",
        render_corpus_bindings(),
    )
    write_text(
        OUTPUT_ROOT / "06_LEDGERS" / "01_TRANSFER_HUB_LEDGER.md",
        render_transfer_hub_ledger(),
    )
    write_text(OUTPUT_ROOT / "06_LEDGERS" / "02_ACTIVE_FRONTIER.md", render_active_frontier())
    write_text(OUTPUT_ROOT / "06_LEDGERS" / "03_NEXT_LOOP_SEED.md", render_next_loop_seed())

    write_text(
        OUTPUT_ROOT / "07_MANUSCRIPTS" / "00_TITLE_ABSTRACT_REVIEW_METRO_MAP.md",
        render_holographic_opening(),
    )
    write_text(OUTPUT_ROOT / "07_MANUSCRIPTS" / "01_CHAPTER_INDEX.md", render_chapter_index())
    for idx, spec in enumerate(CHAPTER_SPECS):
        write_text(
            OUTPUT_ROOT / "07_MANUSCRIPTS" / "chapters" / chapter_filename(spec),
            render_chapter_doc(spec, idx),
        )
    write_text(OUTPUT_ROOT / "07_MANUSCRIPTS" / "02_APPENDIX_INDEX.md", render_appendix_index())
    for hub in APPENDIX_HUBS:
        write_text(
            OUTPUT_ROOT / "07_MANUSCRIPTS" / "appendices" / appendix_filename(hub),
            render_appendix_doc(hub),
        )

    write_text(OUTPUT_ROOT / "08_LOOP_SKILL" / "00_LOOP_SKILL_CHARTER.md", render_loop_skill_charter())
    write_text(OUTPUT_ROOT / "08_LOOP_SKILL" / "01_37_GATE_INDEX.md", render_gate_index())
    write_text(OUTPUT_ROOT / "08_LOOP_SKILL" / "02_GATE_METRO_MAP.md", render_gate_metro_map())
    write_text(OUTPUT_ROOT / "08_LOOP_SKILL" / "03_GATE_SWARM_BINDINGS.md", render_gate_swarm_bindings())
    for idx, gate in enumerate(GATE_SPECS):
        write_text(
            OUTPUT_ROOT / "08_LOOP_SKILL" / "gates" / f"{gate['code']}_{slugify(gate['title'])}.md",
            render_gate_doc(gate, idx),
        )

    write_text(OUTPUT_ROOT / "09_REPAIR_256X256" / "00_REPAIR_README.md", render_repair_readme(cells))
    write_text(OUTPUT_ROOT / "09_REPAIR_256X256" / "01_PLAN_LAW_256x256.md", render_repair_plan_law())
    write_text(OUTPUT_ROOT / "09_REPAIR_256X256" / "02_REPAIR_METRO_MAP.md", render_repair_metro_map(cells))
    write_text(OUTPUT_ROOT / "09_REPAIR_256X256" / "03_REPAIR_STEP_INDEX.md", render_repair_step_index(cells))
    for idx, cell in enumerate(cells):
        write_text(
            OUTPUT_ROOT / "09_REPAIR_256X256" / "steps" / repair_step_filename(cell),
            render_repair_step_doc(cell, idx),
        )

    write_text(OUTPUT_ROOT / "10_CH11_256X256" / "00_CH11_README.md", render_ch11_readme(cells))
    write_text(OUTPUT_ROOT / "10_CH11_256X256" / "01_CH11_PLAN_LAW_256x256.md", render_ch11_law())
    write_text(OUTPUT_ROOT / "10_CH11_256X256" / "02_CH11_METRO_MAP.md", render_ch11_metro_map(cells))
    write_text(OUTPUT_ROOT / "10_CH11_256X256" / "03_CH11_STEP_INDEX.md", render_ch11_step_index(cells))
    for idx, cell in enumerate(cells):
        write_text(
            OUTPUT_ROOT / "10_CH11_256X256" / "cells" / ch11_step_filename(cell),
            render_ch11_step_doc(cell, idx),
        )


def main() -> int:
    build_folder()
    print(f"Wrote internal QSHRINK folder: {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
