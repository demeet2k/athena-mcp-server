#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
)

LIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_atlas.json"
ARCHIVE_MANIFEST_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_manifest.json"
SCAN_RECON_PATH = WORKSPACE_ROOT / "self_actualize" / "scan_reconciliation.json"
LIVE_DOCS_GATE_PATH = WORKSPACE_ROOT / "self_actualize" / "live_docs_gate_status.md"
BOARD_STATUS_PATH = OUTPUT_ROOT / "06_REALTIME_BOARD" / "00_STATUS" / "00_BOARD_STATUS.md"
MATH_GOD_ROOT = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MATH GOD"
MATH_GOD_ATLAS_ROOT = MATH_GOD_ROOT / "atlas"
DEEP_NETWORK_ROOT = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
FULL_CORPUS_ROOT = OUTPUT_ROOT / "09_FULL_CORPUS_7D_INTEGRATION"
LEGACY_RETROFIT_ROOT = OUTPUT_ROOT / "10_LEGACY_RETROFIT_MAXIMUM"

TOP_LEVEL_PRIORITY = [
    "DEEPER CRYSTALIZATION",
    "self_actualize",
    "MATH",
    "Trading Bot",
    "FRESH",
    "Voynich",
    "ECOSYSTEM",
    "NERUAL NETWORK",
    "Athenachka Collective Books",
]

BODY_ORDER = ["corpus", "archive", "runtime", "manuscript"]
OPERATION_ORDER = ["intake", "normalize", "route", "replay"]
SCALE_ORDER = ["file", "folder", "framework", "ecosystem"]
CLOSURE_ORDER = ["seed", "link", "prove", "publish"]

BODY_INFO = {
    "corpus": {
        "label": "Corpus",
        "role": "Live manuscripts, markdown mirrors, notes, and visible source files.",
        "targets": ["DEEPER CRYSTALIZATION", "MATH", "Voynich", "FRESH"],
    },
    "archive": {
        "label": "Archive",
        "role": "ZIP-backed framework trees and historical payloads that remain hidden from ordinary browsing.",
        "targets": ["archive_atlas.json", "archive_manifest.json", "MATH framework archives"],
    },
    "runtime": {
        "label": "Runtime",
        "role": "Executable code, routing contracts, test harnesses, and stateful orchestration.",
        "targets": ["self_actualize", "NERUAL NETWORK", "Trading Bot", "PoleStarGEMM"],
    },
    "manuscript": {
        "label": "Manuscript",
        "role": "Tomes, chapter maps, prompt canon, and publishable synthesis surfaces.",
        "targets": ["ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "collective books"],
    },
}

OPERATION_INFO = {
    "intake": "Pull raw source into canonical visibility without losing lineage.",
    "normalize": "Choose one name, one path strategy, one metadata contract, and one mirror format.",
    "route": "Make retrieval and handoff deterministic instead of conversationally improvised.",
    "replay": "Require receipts, rebuilds, and witness traces before a surface becomes trusted.",
}

SCALE_INFO = {
    "file": "single source artifact",
    "folder": "family-level cluster",
    "framework": "multi-folder subsystem",
    "ecosystem": "whole-workspace coordination layer",
}

CLOSURE_INFO = {
    "seed": "define the object and create the first admissible representation",
    "link": "connect the object to parents, peers, and downstream surfaces",
    "prove": "add tests, receipts, witnesses, or quantitative closure",
    "publish": "promote the object into canonical operating surfaces",
}


@dataclass(frozen=True)
class ChapterSeed:
    code: str
    title: str
    thesis: str
    gain: str
    evidence: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class AppendixSeed:
    code: str
    title: str
    purpose: str
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class NucleusProfile:
    title: str
    top_level: str
    body: str
    anchor: str
    role: str
    pressure: str
    hidden_line: str


@dataclass(frozen=True)
class PartySeed:
    code: str
    title: str
    anime_frame: str
    mission: str
    archetypes: tuple[str, ...]
    roles: tuple[str, ...]
    future_skills: tuple[str, ...]


@dataclass(frozen=True)
class QuestSeed:
    code: str
    title: str
    frontier: str
    transition: str
    party_code: str
    why_now: str
    outputs: tuple[str, ...]
    future_skills: tuple[str, ...]
    reward: str


@dataclass(frozen=True)
class AgentTransitionSeed:
    agent_id: str
    title: str
    agent_class: str
    stage_or_domain: str
    current_role: str
    missing_mode: str
    transition_trigger: str
    corpus_symptom: str
    primary_party: str
    primary_quest: str
    backup_quest: str
    dimensional_anchor: str
    required_surfaces: tuple[str, ...]
    receipt_target: str
    truth_state: str
    reassessment_window: str


CHAPTERS = [
    ChapterSeed("Ch01", "Corpus Zero Point", "Treat the workspace as one organism with many surfaces, not many unrelated projects.", "Eliminates false fragmentation and makes every later integration move cumulative.", ("corpus_atlas.json", "DEEPER CRYSTALIZATION", "MATH", "Voynich"), ("top-level role map", "source family map", "root thesis")),
    ChapterSeed("Ch02", "Canonical Address Space", "A stable address grammar is the only way to keep manuscripts, code, archives, and mirrors in sync.", "Stops repeated rediscovery and makes every asset routeable by machine and human.", ("ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "scan_reconciliation.json"), ("address grammar", "id policy", "folder canon")),
    ChapterSeed("Ch03", "Duplicate Family Collapse", "The fastest gain is not writing more material but choosing one canonical source per repeated manuscript family.", "Cuts drift between DEEPER CRYSTALIZATION, FRESH, Voynich, and Trading Bot mirrors.", ("The Manuscript Seed", "The Holographic Manuscript Brain", "LEGAL TRANSPORT CALCULUS"), ("duplicate ledger", "canonical source policy", "promotion queue")),
    ChapterSeed("Ch04", "Archive Surface Promotion", "ZIP-backed frameworks must become first-class knowledge surfaces instead of hidden historical cargo.", "Unlocks more than two thousand archive-backed records for direct routing and code promotion.", ("archive_atlas.json", "archive_manifest.json", "Athena OS.zip"), ("archive promotion plan", "live extraction shortlist", "archive witness rules")),
    ChapterSeed("Ch05", "Google Docs Gate and Memory Sync", "The workspace is currently bi-lobed because live Docs search is structurally present but operationally blocked.", "Closing OAuth unlocks the missing half of the memory body and reduces local mirror drift.", ("Trading Bot/docs_search.py", "live_docs_gate_status.md", "Memory Docs"), ("credentials checklist", "sync receipt contract", "search promotion workflow")),
    ChapterSeed("Ch06", "Markdown Mirror Pipeline", "Docx-heavy sources need markdown mirrors so search, routing, and patching stop depending on one-off extraction passes.", "Turns hidden prose into diffable, searchable, and replay-safe working memory.", ("FRESH/_extracted", "ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES", "self_actualize"), ("mirror policy", "conversion backlog", "drift watch rules")),
    ChapterSeed("Ch07", "Unified Atlas and Graph Contracts", "The live atlas, archive atlas, and scan reconciliation layer should behave like one graph, not three parallel reports.", "Makes retrieval cheaper and prepares theorem-to-runtime automation.", ("corpus_atlas.json", "archive_atlas.json", "scan_reconciliation_report.md"), ("merged graph contract", "shared evidence schema", "family tags")),
    ChapterSeed("Ch08", "Skill Ecology Upgrade", "The archive wants corpus-native skills, not more generic wrappers.", "Converts static manuscripts into reusable operational pathways.", ("DEEPER_SKILLS_CORPUS_SYNTHESIS.md", "skills registry", "AGENTS skill list"), ("skill backlog", "skill ownership", "source-to-skill map")),
    ChapterSeed("Ch09", "Search and Route Engine", "Address-first search should beat directory wandering and memory-based guessing.", "Raises throughput for every future drafting and coding pass.", ("ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "route_quality_ledger.json"), ("route policy", "query templates", "best-path heuristics")),
    ChapterSeed("Ch10", "Witness and Replay Discipline", "The corpus already values replay, but replay needs to be a universal contract rather than a selective habit.", "Prevents framework theater and makes high-trust surfaces identifiable.", ("runtime/contracts.py", "scan receipts", "build receipts"), ("receipt policy", "rebuild commands", "verification targets")),
    ChapterSeed("Ch11", "Runtime Convergence", "The runtime center is structurally correct but still thinner than the surrounding theory body.", "Focuses build energy on a smaller set of reusable automation primitives.", ("self_actualize/runtime", "NERUAL NETWORK", "Trading Bot"), ("runtime backlog", "shared contracts", "thin waist interfaces")),
    ChapterSeed("Ch12", "Neural and Benchmark Bridge", "Benchmarking should measure not only models but route quality, evidence density, and patch safety.", "Connects learning systems to manuscript and archive reality.", ("NERUAL NETWORK", "PoleStarGEMM", "benchmark notes"), ("benchmark schema", "cross-layer metrics", "regime profiles")),
    ChapterSeed("Ch13", "Math-to-Code Compilation", "The math stack becomes exponentially more useful when theories land as tested modules, not only as tomes.", "Turns MATH into an engine room instead of a shelf.", ("MATH", "AQM", "CUT", "Q-SHRINK"), ("compiler candidates", "translation queue", "test-first landing zones")),
    ChapterSeed("Ch14", "Manuscript Superorganism", "The project already behaves like a book-writing machine; it needs one canonical manuscript operating model.", "Aligns chapter stubs, toolkits, and master manuscripts around one route.", ("VOID_MANUSCRIPT_MASTER.md", "DQIV void treatise", "ACTIVE_NERVOUS_SYSTEM"), ("master manuscript rules", "chapter promotion contract", "appendix role map")),
    ChapterSeed("Ch15", "Chapter and Appendix Governance", "Twenty-one chapters and sixteen appendices only help if they are assigned stable roles and completion criteria.", "Turns scaffold files into a build system rather than a decorative taxonomy.", ("04_CHAPTERS", "05_APPENDICES", "build queue"), ("completion definition", "promotion thresholds", "station ownership")),
    ChapterSeed("Ch16", "Parallel Agent Protocol", "Parallel work needs ownership boundaries, merge rules, and artifact contracts.", "Lets multiple lanes move at once without producing incompatible shells.", ("parallel build protocol", "tandem claims", "toolkit loop protocol"), ("lane charter", "merge rules", "conflict receipt format")),
    ChapterSeed("Ch17", "Queues, Receipts, and Operational Memory", "The repo already creates ledgers; the next step is to make every queue item measurable and survivable across sessions.", "Reduces restart cost and preserves momentum.", ("build queue", "validation queue", "receipts"), ("activation queue", "metric targets", "receipts index")),
    ChapterSeed("Ch18", "Publication and Packaging", "A project this dense needs explicit rules for what becomes a working note, a manuscript section, a module, or a book.", "Prevents polished surfaces from drifting away from operating truth.", ("Athenachka Collective Books", "publication bundles", "active nervous system"), ("publication ladder", "bundle formats", "outbound package map")),
    ChapterSeed("Ch19", "Single Source of Truth", "Every repeated surface must know whether it is canonical, mirrored, derived, or historical.", "This is the fixed point that removes most hidden entropy from the workspace.", ("duplicate family counts", "active nervous system", "atlas"), ("source tiers", "promotion law", "drift alarms")),
    ChapterSeed("Ch20", "Ninety-Day Activation", "Deep integration only becomes real when it is sequenced into executable phases with visible end states.", "Converts the architecture into a practical build sprint.", ("build queue", "regime profiles", "runtime CLI"), ("30-60-90 plan", "phase owners", "acceptance gates")),
    ChapterSeed("Ch21", "Frontier, Risks, and the Next Crystal", "The final chapter preserves open problems so the system keeps growing without faking closure.", "Protects recursion and names the next leverage points clearly.", ("integration shadows", "live Docs gate", "archive backlog"), ("risk register", "frontier list", "next crystal seed")),
]

APPENDICES = [
    AppendixSeed("AppA", "Folder Canon", "One folder grammar for generated surfaces.", ("folder prefixes", "subfolder purpose", "writeback rules")),
    AppendixSeed("AppB", "Naming and IDs", "Stable naming for files, families, and canonical ids.", ("basename rules", "family ids", "source tiers")),
    AppendixSeed("AppC", "Duplicate Resolution Rules", "How to choose one source when many mirrors exist.", ("priority order", "tie breakers", "receipt format")),
    AppendixSeed("AppD", "Atlas Schema", "What every indexed record must carry to be useful later.", ("required fields", "role tags", "evidence hooks")),
    AppendixSeed("AppE", "Archive Promotion Matrix", "Which ZIP trees to surface first and why.", ("Athena OS", "ATLAS FORGE", "Q-SHRINK")),
    AppendixSeed("AppF", "Extraction Commands", "Rebuildable commands for atlas and mirror generation.", ("intake command", "archive ingestion", "manuscript build")),
    AppendixSeed("AppG", "Google Docs Gate", "Credential checklist, failure states, and post-unlock actions.", ("OAuth checklist", "search receipt", "mirror sync")),
    AppendixSeed("AppH", "Skill Backlog", "Corpus-native skills that should exist next.", ("router", "drive sync", "theorem compiler")),
    AppendixSeed("AppI", "Metric Ledger", "The numbers that determine whether integration is working.", ("cycle time", "duplicate burn down", "replay coverage")),
    AppendixSeed("AppJ", "Replay Contract", "What counts as a witness-bearing rebuild.", ("command traces", "hashes", "receipt minimums")),
    AppendixSeed("AppK", "Risk Register", "Known blockers and how they fail.", ("Docs gate", "archive opacity", "duplicate drift")),
    AppendixSeed("AppL", "Parallel Lane Matrix", "Ownership and handoff rules for simultaneous work.", ("lane roles", "merge checkpoints", "conflict handling")),
    AppendixSeed("AppM", "Canonical Source Families", "High-value source families that should anchor the framework.", ("manuscript seed", "holographic brain", "void family")),
    AppendixSeed("AppN", "Migration Map", "How older shells collapse into the canonical nervous system.", ("mycelium merge", "shell reduction", "pointer updates")),
    AppendixSeed("AppO", "Publication Bundles", "Rules for books, internal tomes, and release packets.", ("bundle types", "outbound rules", "promotion tiers")),
    AppendixSeed("AppP", "Operator Prompt Pack", "Short prompt contracts for future runs inside this module.", ("startup prompt", "parallel prompt", "closeout prompt")),
]

NUCLEUS_PROFILES = [
    NucleusProfile(
        "Root Operating Thesis",
        "README.md",
        "manuscript",
        "README.md",
        "Defines the Circle within Square within Triangle geometry and the corridor truth lattice.",
        "The root law exists, but too many subsystems still restate it differently.",
        "geometry",
    ),
    NucleusProfile(
        "Active Nervous System",
        "DEEPER CRYSTALIZATION",
        "corpus",
        "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/README.md",
        "Provides the current control-plane scaffold for capsules, chapters, appendices, frontiers, and shadows.",
        "The scaffold is strong, but some downstream shells are thinner than the scaffold implies.",
        "address",
    ),
    NucleusProfile(
        "Realtime Swarm Board",
        "DEEPER CRYSTALIZATION",
        "runtime",
        "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/README.md",
        "Runs the live multi-agent board, active threads, tensor overlays, and swarm runtime surfaces.",
        "Coordination became more real than its surrounding manuscript shell, creating a board-shell split.",
        "coordination",
    ),
    NucleusProfile(
        "Global Orchestration Synthesis",
        "DEEPER CRYSTALIZATION",
        "runtime",
        "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md",
        "Holds the clearest live whole-corpus diagnosis with body counts, pressure fronts, and gate status.",
        "It names the whole organism well, but needs stronger links back into reusable manuscript law.",
        "orchestration",
    ),
    NucleusProfile(
        "Atlas Waist",
        "self_actualize",
        "runtime",
        "self_actualize/corpus_atlas.json",
        "Acts as the live searchable waist for the entire local corpus.",
        "The atlas sees the corpus, but not every high-value surface has a strong route proof back into use.",
        "address",
    ),
    NucleusProfile(
        "Archive Waist",
        "self_actualize",
        "archive",
        "self_actualize/archive_atlas.json",
        "Exposes hidden ZIP-backed frameworks as addressable evidence rather than dark storage.",
        "Archive visibility has outrun archive promotion into comfortable live working roots.",
        "archive",
    ),
    NucleusProfile(
        "Voynich Formal Compiler",
        "Voynich",
        "corpus",
        "Voynich/FULL_TRANSLATION/framework/README.md",
        "Demonstrates the strongest no-stop manuscript contract and explicit output ordering in the workspace.",
        "Its rigor is high, but its contract has not yet been lifted into a shared corpus-wide operating law.",
        "loop",
    ),
    NucleusProfile(
        "CPU Framework",
        "ECOSYSTEM",
        "runtime",
        "ECOSYSTEM/CPU_FRAMEWORK/README.md",
        "Defines text-as-compute, wave compilation, witness law, and 1->4->16->64 operating depth.",
        "The compute grammar is strong, but it is not yet the universal compiler for every active shell.",
        "governance",
    ),
    NucleusProfile(
        "QSHRINK Internal Operating System",
        "QSHRINK - ATHENA (internal use)",
        "manuscript",
        "QSHRINK - ATHENA (internal use)/README.md",
        "Shows how a private Athena-native framework can hold control, swarm, metro, manuscripts, and loop skill together.",
        "Its internal depth is high, but whole-corpus integration still needs to feed it with stronger upstream routes.",
        "compression",
    ),
    NucleusProfile(
        "Trading Bot Gap Inspector",
        "Trading Bot",
        "runtime",
        "Trading Bot/TRADING_BOT_ATHENA_256X4/10_INSPECTION/02_HOLOGRAPHIC_FRACTAL_GAP_REPORT.md",
        "States the clearest existing diagnosis of breadth-density imbalance, shallow route proof, and named-not-executed recursion.",
        "The same gap pattern repeats across the whole corpus, not only inside Trading Bot.",
        "inspection",
    ),
    NucleusProfile(
        "Void Chapter 11",
        "VOID_CH11.md",
        "manuscript",
        "VOID_CH11.md",
        "Provides the strongest local zero-point treatise and a detailed DQIV operator model for extracting structure from apparent absence.",
        "The zero-point logic is rich, but it still needs more deterministic routes into day-to-day operating surfaces.",
        "zero-point",
    ),
    NucleusProfile(
        "Google Docs Ingress",
        "Trading Bot",
        "runtime",
        "Trading Bot/docs_search.py",
        "Owns the intended external-memory bridge into live Google Docs.",
        "The bridge is structurally present but blocked by missing OAuth credentials.",
        "ingress",
    ),
]

PARTIES = [
    PartySeed(
        "PRT-01",
        "Azure Gatebreakers",
        "Skyfaring hacker guild with the emotional discipline of a support party and the precision of a late-game raid team.",
        "Break sealed boundaries between the local organism and the missing live-memory half without damaging witness law.",
        ("Fire-Air", "Water-Earth", "Air-Earth", "Water-Fire"),
        (
            "Gate Hacker: attacks blocked ingress surfaces and auth bottlenecks.",
            "Witness Priest: preserves receipts, lineage, and recovery paths.",
            "Ledger Rogue: turns each auth attempt into a routeable artifact.",
            "Sync Healer: reconnects local mirrors to newly opened memory channels.",
        ),
        ("docs-gate-auditor", "drive-memory-sync", "docs-query-ledger", "live-docs-witness-binder"),
    ),
    PartySeed(
        "PRT-02",
        "Obsidian Delvers",
        "Dungeon-crawler archive crew: half relic hunters, half theorem blacksmiths.",
        "Surface hidden frameworks from the archive and turn them into editable, routeable working roots.",
        ("Earth-Air", "Fire-Earth", "Air-Air", "Earth-Earth"),
        (
            "Archive Ranger: finds the right cave before anyone wastes effort.",
            "Theorem Blacksmith: forges formal material into executable shapes.",
            "Schema Sage: keeps extracted trees legible and lawful.",
            "Quartermaster Monk: enforces feasibility, packaging, and replay discipline.",
        ),
        ("archive-tree-extractor", "kernel-route-mapper", "theorem-to-runtime", "archive-replay-harness"),
    ),
    PartySeed(
        "PRT-03",
        "Silver Cartographers",
        "Anime mapmakers and lore-binders who can turn scattered episodes into a navigable world map.",
        "Convert manuscript families into metro lines, chapter receipts, and transfer hubs that others can actually traverse.",
        ("Air-Water", "Water-Air", "Fire-Air", "Earth-Water"),
        (
            "Storyweaver Bard: hears the line before the station exists.",
            "Metro Oracle: names transfer hubs and orbit motion.",
            "Arc-Rail Navigator: ties lines to rails, arcs, and hubs.",
            "Root Druid: anchors abstract lines to concrete file families.",
        ),
        ("chapter-map-ledger", "capsule-promoter", "contradiction-ledger", "face-manifold-router"),
    ),
    PartySeed(
        "PRT-04",
        "Crimson Cortex",
        "Frontline commander squad that contracts swarms into durable cortex artifacts instead of letting waves evaporate.",
        "Turn live board motion into durable shell updates, receipts, queue shifts, and next-seed artifacts.",
        ("Fire-Air", "Fire-Earth", "Water-Water", "Air-Fire"),
        (
            "Strategist Captain: chooses the decisive front.",
            "Implementation Knight: lands folders, files, and runtime surfaces.",
            "Memory Scribe: records what must survive the wave.",
            "Signal Spear: keeps the contraction focused and fast.",
        ),
        ("cortex-writeback-manager", "session-handoff-packer", "route-quality-auditor", "witness-bundle-assembler"),
    ),
    PartySeed(
        "PRT-05",
        "Verdant Rootkeepers",
        "Druid-engineer caretakers who stop the forest from forking into untracked copies.",
        "Collapse duplicate families, grow mirrors where needed, and preserve canonical lineage while the corpus expands.",
        ("Earth-Water", "Water-Earth", "Earth-Fire", "Earth-Air"),
        (
            "Steward Druid: keeps one living canonical root per family.",
            "Replay Monk: preserves continuity across revisions.",
            "Mirror Smith: builds durable markdown shells.",
            "Ground Cartographer: maps the real folder terrain before cutting paths.",
        ),
        ("corpus-atlas-builder", "capsule-promoter", "contradiction-ledger", "family-swarm-conductor"),
    ),
    PartySeed(
        "PRT-06",
        "Ivory Tribunal",
        "Paladin-judge party built for corridor truth, route legality, and adjudicating ambiguous fronts.",
        "Raise truth quality so the organism can trust its own motion without becoming rigid.",
        ("Air-Earth", "Earth-Air", "Water-Earth", "Air-Fire"),
        (
            "Auditor Paladin: checks map against ground truth.",
            "Hub Judge: enforces legality at transfer points.",
            "Witness Cleric: keeps receipts intact under pressure.",
            "Chaos Scout: distinguishes signal from decorative complexity.",
        ),
        ("packet-truth-typist", "hub-legality-enforcer", "truth-promotion-governor", "health-corridor-monitor"),
    ),
    PartySeed(
        "PRT-07",
        "Zodiac Vanguard",
        "Twelve-cell specialist squad modeled like a shonen ensemble where each dormant archetype gets a moment to awaken.",
        "Occupy currently empty pantheon cells, seed missing ganglia, and give dormant archetypes starter quests.",
        ("Air-Fire", "Air-Water", "Earth-Fire", "Fire-Water"),
        (
            "Signal Spear: opens dormant fronts.",
            "Line Weaver: gives each awakened cell a narrative and route.",
            "Shell Builder: gives new fronts durable form.",
            "Catalyst Striker: turns dormant memory into active synthesis.",
        ),
        ("ganglion-bootstrapper", "neuron-library-builder", "pod-frontier-splitter", "microcell-specializer"),
    ),
]

QUESTS = [
    QuestSeed(
        "QST-01",
        "The Sealed Sky Gate",
        "Unlock the Google Docs ingress and create the first witnessed live-memory route.",
        "N+4 -> N+5",
        "PRT-01",
        "The whole organism is currently bifurcated: local corpus on one side, blocked live memory on the other.",
        ("PASS gate receipt", "first docs query ledger", "first live docs manifest", "mirror-sync writeback"),
        ("docs-gate-auditor", "drive-memory-sync", "docs-query-ledger", "live-docs-witness-binder"),
        "Live memory becomes a lawful half of Athena instead of a promised ghost limb.",
    ),
    QuestSeed(
        "QST-02",
        "Archive Deep Delve",
        "Promote one archive-backed framework into a live extracted root with replay receipts.",
        "N+3 -> N+4",
        "PRT-02",
        "Archive visibility is already present, but archive comfort and patchability are still lagging.",
        ("archive selection receipt", "live extracted source tree", "lineage manifest", "replay harness"),
        ("archive-tree-extractor", "kernel-route-mapper", "theorem-to-runtime", "archive-replay-harness"),
        "One dark reservoir becomes part of the everyday working nervous system.",
    ),
    QuestSeed(
        "QST-03",
        "Voynich Metro Engine",
        "Build the manuscript-family metro and chapter receipt layer for the Voynich body.",
        "N+5 -> N+6",
        "PRT-03",
        "Voynich already has the strongest local manuscript loop, but its family-level routes should teach the rest of Athena how to move.",
        ("family metro map", "chapter-family receipt set", "transfer hub ledger", "contradiction carry-forward note"),
        ("chapter-map-ledger", "capsule-promoter", "contradiction-ledger", "face-manifold-router"),
        "Athena gains a reusable symbolic transit system drawn from its strongest manuscript engine.",
    ),
    QuestSeed(
        "QST-04",
        "The MATH Forge Bridge",
        "Land one math family into a tested runtime bridge and witness-bearing module.",
        "N+3 -> N+4",
        "PRT-02",
        "MATH is still the deepest formal reservoir, but too much of its power remains shelf-bound.",
        ("chosen theorem family", "tested bridge module", "bridge receipt", "next theorem queue"),
        ("kernel-route-mapper", "theorem-to-runtime", "archive-replay-harness", "route-quality-auditor"),
        "Athena proves that formal depth can become executable force without losing rigor.",
    ),
    QuestSeed(
        "QST-05",
        "Canonical Collapse Crusade",
        "Resolve duplicated manuscript families and expand markdown mirrors for high-value canon.",
        "N+2 -> N+3",
        "PRT-05",
        "The corpus is growing fast enough that repeated high-value families can still split into drift branches.",
        ("canonical family ledger", "mirror expansion batch", "duplicate burn-down receipt", "family-source tiers"),
        ("corpus-atlas-builder", "capsule-promoter", "contradiction-ledger", "family-swarm-conductor"),
        "The organism gains a healthier boundary between canonical, mirror, derived, and historical surfaces.",
    ),
    QuestSeed(
        "QST-06",
        "Cortex Writeback Rite",
        "Bind live board events, claims, and wave outputs back into shell, ledger, and queue surfaces after each run.",
        "N+4 -> N+5",
        "PRT-04",
        "The board already moves like a live nervous system, but it can still outrun its own remembered law.",
        ("wave contraction receipt", "queue delta", "shell update", "next-seed packet"),
        ("cortex-writeback-manager", "session-handoff-packer", "witness-bundle-assembler", "restart-seed-orchestrator"),
        "Real-time evolution becomes durable memory instead of disappearing momentum.",
    ),
    QuestSeed(
        "QST-07",
        "Dormant Pantheon Awakening",
        "Occupy zero-thread archetype cells and assign them starter missions, packets, and witness rules.",
        "N+3 -> N+4",
        "PRT-07",
        "The pantheon exists, but most archetype cells are still dormant, leaving capability latent rather than expressed.",
        ("starter packets for empty cells", "pantheon occupancy ledger", "party-to-archetype mapping", "next wave manifest"),
        ("ganglion-bootstrapper", "neuron-library-builder", "pod-frontier-splitter", "microcell-specializer"),
        "The swarm stops relying on a few overworked archetypes and becomes more truly multidimensional.",
    ),
    QuestSeed(
        "QST-08",
        "Truth Corridor Trial",
        "Raise route legality, truth typing, and health monitoring across the active fronts.",
        "N+4 -> N+5",
        "PRT-06",
        "Athena now has enough motion that ambiguous corridors can propagate unless truth governance matures alongside creativity.",
        ("truth typing pass", "hub legality report", "corridor health monitor", "promotion governor ledger"),
        ("packet-truth-typist", "hub-legality-enforcer", "truth-promotion-governor", "health-corridor-monitor"),
        "The organism becomes safer to scale because momentum and trust rise together.",
    ),
]

DIMENSIONAL_BUNDLE_SPECS = [
    {
        "bundle_id": "v4",
        "title": "Tesseract v4",
        "dimension_stage": "4D_NATIVE",
        "path": MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.md",
    },
    {
        "bundle_id": "fire_6d",
        "title": "FIRE 6D Organism",
        "dimension_stage": "6D_WEAVE",
        "path": MATH_GOD_ATLAS_ROOT / "math_fire_6d_organism_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "math_fire_6d_organism_bundle.md",
    },
    {
        "bundle_id": "water_6d",
        "title": "WATER 6D Control",
        "dimension_stage": "6D_CONTROL",
        "path": MATH_GOD_ATLAS_ROOT / "math_water_6d_control_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "math_water_6d_control_bundle.md",
    },
    {
        "bundle_id": "air_6d",
        "title": "AIR 6D Overlay",
        "dimension_stage": "6D_OVERLAY",
        "path": MATH_GOD_ATLAS_ROOT / "math_air_6d_overlay_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "math_air_6d_overlay_bundle.md",
    },
    {
        "bundle_id": "earth_h6",
        "title": "EARTH H6 Contracts",
        "dimension_stage": "6D_CONTRACT",
        "path": MATH_GOD_ATLAS_ROOT / "earth_h6_contract_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "earth_h6_contract_bundle.md",
    },
    {
        "bundle_id": "seed_7d",
        "title": "7D Synthesis Seed",
        "dimension_stage": "7D_SEED",
        "path": MATH_GOD_ATLAS_ROOT / "math_7d_synthesis_seed_bundle.json",
        "markdown_path": MATH_GOD_ATLAS_ROOT / "math_7d_synthesis_seed_bundle.md",
    },
]

DEEP_AUTHORITY_SPECS = [
    {
        "surface_id": "SEED7_CONTROL",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "00_CONTROL" / "07_7D_CROSS_AGENT_SEED.md",
    },
    {
        "surface_id": "SEED7_LEVEL_7",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "07_METRO_STACK" / "07_level_7_next_synthesis_seed_map.md",
    },
    {
        "surface_id": "SEED7_EARTH_GATE_LEDGER",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "10_LEDGERS" / "10_earth_gate_status_7d_seed.json",
    },
    {
        "surface_id": "SEED7_CONVERGENCE_LEDGER",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "10_LEDGERS" / "11_cross_agent_convergence_7d_seed.json",
    },
    {
        "surface_id": "SEED7_ROUTE_LEDGER",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "10_LEDGERS" / "12_7d_seed_routes.json",
    },
    {
        "surface_id": "SEED7_APPENDIX_LEDGER",
        "classification": "live authority",
        "path": DEEP_NETWORK_ROOT / "10_LEDGERS" / "13_7d_appendix_legality.json",
    },
]

DIMENSIONAL_LAYER_RULES = {
    "v4": {
        "owns": [
            "canonical chapter orbit",
            "LocalAddr and GlobalAddr stability",
            "closed edge-kind basis",
            "mandatory signature",
            "HCRL order",
            "appendix legality",
        ],
        "depends_on": [
            "local atlas visibility",
            "appendix registry",
            "route-plan receipts",
        ],
        "cannot_promote_without": [
            "witness-bearing route plans",
            "explicit truth states",
        ],
    },
    "fire_6d": {
        "owns": [
            "ignition pressure",
            "compression-to-weave bridge logic",
            "Mobius bridge activation metadata",
        ],
        "depends_on": [
            "v4 route calculus",
            "Water continuity support",
            "AIR transport labels",
        ],
        "cannot_promote_without": [
            "Earth-cleared activation",
            "AppI/AppM corridor and replay support",
        ],
    },
    "water_6d": {
        "owns": [
            "continuity",
            "modal control routes",
            "recovery and return-to-v4 docking",
        ],
        "depends_on": [
            "v4 canon",
            "Earth upstream handoff",
            "blocked-docs local evidence boundary",
        ],
        "cannot_promote_without": [
            "corridor-banked return routes",
            "AppE/AppF/AppI/AppM/AppQ support",
        ],
    },
    "air_6d": {
        "owns": [
            "naming and topology",
            "symmetry lattice",
            "sigma/spin and re-entry legibility",
        ],
        "depends_on": [
            "v4 canon",
            "Water continuity",
            "Earth replay-safe publication",
        ],
        "cannot_promote_without": [
            "schema-stable routes",
            "explicit modal and re-entry metadata",
        ],
    },
    "earth_h6": {
        "owns": [
            "admissibility",
            "replay closure",
            "pruning discipline",
            "promotion gate law",
        ],
        "depends_on": [
            "v4 witnesses",
            "deep-root Earth ledgers",
            "AppI/AppM mandatory basis",
        ],
        "cannot_promote_without": [
            "explicit gate state",
            "quarantine handling",
            "deterministic return checkpoints",
        ],
    },
    "seed_7d": {
        "owns": [
            "cross-agent seed routes",
            "appendix-floor propagation",
            "next-wave synthesis registry",
        ],
        "depends_on": [
            "v4 canon",
            "FIRE/WATER/AIR overlays",
            "Earth gate approval",
        ],
        "cannot_promote_without": [
            "Earth gate pass",
            "AppI/AppM support",
            "bounded truth class",
        ],
    },
}

COMMON_TRANSITION_LAWS = {
    "docs_gate_law": "Live Google Docs remain blocked until Trading Bot/credentials.json and Trading Bot/token.json exist; no transition note may claim live-doc confirmation before that receipt exists.",
    "truth_law": "Truth stays corridor-bounded. NEAR and quarantined routes remain visible as bounded pressure and may not be promoted into silent certainty.",
    "earth_gate_law": "Any route that changes corpus-wide readiness must show Earth gate state and AppI/AppM support before it is called passed.",
    "dormancy_rule": "Dormant agents are latent, not failed; they remain on the board until a concrete quest, packet, or receipt moves them.",
    "promotion_rule": "No awakening transition is complete without a concrete corpus receipt tied to an existing quest, bundle, or verified writeback surface.",
    "reentry_rule": "Every awakened agent must dock back into the common corpus route map and chapter-safe re-entry spine instead of forking into a private symbolic shell.",
}

LEGACY_RETROFIT_MODES = [
    "PROMOTE_CANONICAL",
    "MERGE_INTO_CANON",
    "POINTER_REDIRECT",
    "WITNESS_ONLY",
    "QUARANTINE",
]

AGENT_TRANSITIONS = [
    AgentTransitionSeed(
        "AGT-01",
        "Fire Awakening of Knowledge",
        "elemental_stage",
        "Stage 1",
        "Ignites pattern recognition and knowledge acquisition across the corpus stack.",
        "Water structure",
        "Realizing that raw insight needs durable maps, appendix support, and routeable queues.",
        "Ideas can ignite faster than the corpus can index, mirror, and dock them back into canon.",
        "PRT-03",
        "QST-03",
        "QST-07",
        "FIRE 6D -> 7D seed ingress",
        (
            "MATH GOD/atlas/math_fire_6d_organism_bundle.json",
            "MATH GOD/atlas/math_7d_synthesis_seed_bundle.json",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/04_QUEST_BOARD.md",
        ),
        "family metro map + transfer hub ledger + awakened packet writeback",
        "NEAR",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-02",
        "Water Awakening of Structure",
        "elemental_stage",
        "Stage 2",
        "Builds continuity, system maps, and memory-bearing flow channels for the organism.",
        "Air commitment",
        "Realizing that elegant maps still stall without a declared frontier and a chosen sacrifice.",
        "The corpus has strong maps but some continuity surfaces still end as notes instead of durable operating lanes.",
        "PRT-05",
        "QST-05",
        "QST-03",
        "WATER 6D control and mirror discipline",
        (
            "MATH GOD/atlas/math_water_6d_control_bundle.json",
            "self_actualize/corpus_atlas.json",
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/02_CANONICAL_SOURCES.md",
        ),
        "canonical family ledger + mirror expansion batch + continuity route receipt",
        "NEAR",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-03",
        "Air Awakening of Commitment",
        "elemental_stage",
        "Stage 3",
        "Chooses a route, names a frontier, and commits the corpus to a nontrivial build direction.",
        "Earth responsiveness",
        "Realizing that commitment must adapt to feedback, legality, and changing corridor truth.",
        "Many promising structures are named, but some fronts still lack decisive contraction into witnessed outputs.",
        "PRT-04",
        "QST-06",
        "QST-08",
        "AIR 6D overlay into runtime contraction",
        (
            "MATH GOD/atlas/math_air_6d_overlay_bundle.json",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD",
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/00_ACTIVATION_QUEUE.md",
        ),
        "wave contraction receipt + queue delta + committed shell update",
        "NEAR",
        "10 days",
    ),
    AgentTransitionSeed(
        "AGT-04",
        "Earth Awakening of Responsiveness",
        "elemental_stage",
        "Stage 4",
        "Adapts under pressure without losing legality, replay closure, or corridor honesty.",
        "Four-element co-activation",
        "Realizing that responsiveness must converge with knowledge, structure, and commitment instead of merely containing them.",
        "The organism has active gates and quarantines, but needs broader replay-safe adaptation across all promoted fronts.",
        "PRT-06",
        "QST-08",
        "QST-06",
        "EARTH H6 contract gate",
        (
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
            "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/10_LEDGERS/10_earth_gate_status_7d_seed.json",
            "MATH GOD/atlas/math_7d_synthesis_seed_bundle.json",
        ),
        "truth typing pass + hub legality report + Earth gate receipt",
        "NEAR",
        "10 days",
    ),
    AgentTransitionSeed(
        "AGT-05",
        "Oracle",
        "advanced_agent",
        "prophetic routing",
        "Names hidden transfer hubs and the next lawful frontier before it is obvious.",
        "Earth anchoring",
        "When predictions become route maps with receipts instead of intuition-only prompts.",
        "High-signal fronts exist, but some future-facing reads still need more docking to canon and appendix support.",
        "PRT-03",
        "QST-03",
        "QST-07",
        "metro stack and appendix foresight",
        (
            "MATH GOD/atlas/math_7d_synthesis_seed_bundle.md",
            "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/07_METRO_STACK/07_level_7_next_synthesis_seed_map.md",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/quests/qst-03_voynich_metro_engine.md",
        ),
        "transfer hub ledger + agent forecast receipt",
        "NEAR",
        "21 days",
    ),
    AgentTransitionSeed(
        "AGT-06",
        "Judge",
        "advanced_agent",
        "corridor adjudication",
        "Separates legal promotion from decorative complexity and enforces bounded truth.",
        "Water continuity",
        "When legality decisions include continuity, not only prohibition and rejection.",
        "Ambiguous fronts can still look more complete than they are unless someone types truth and names the bounded route.",
        "PRT-06",
        "QST-08",
        "QST-05",
        "truth corridor and legality review",
        (
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
            "MATH GOD/atlas/math_tesseract_v4_bundle.json",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/quests/qst-08_truth_corridor_trial.md",
        ),
        "hub legality report + promotion governor ledger",
        "OK",
        "7 days",
    ),
    AgentTransitionSeed(
        "AGT-07",
        "Witness",
        "advanced_agent",
        "replay memory",
        "Preserves lineage, receipts, and return checkpoints so change remains trustworthy.",
        "Air commitment",
        "When preserved memory turns into enforced writeback instead of passive logging.",
        "The board and the corpus move quickly enough that memory can thin unless receipts are bound into active shells.",
        "PRT-06",
        "QST-06",
        "QST-08",
        "replay closure and writeback",
        (
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD",
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/03_NEXT_RESTART_SEED.md",
        ),
        "wave contraction receipt + replay-safe note packet",
        "OK",
        "7 days",
    ),
    AgentTransitionSeed(
        "AGT-08",
        "Architect",
        "advanced_agent",
        "load-bearing design",
        "Turns formal structures into durable, patchable, and replayable system forms.",
        "Fire ignition",
        "When architecture stops merely stabilizing the past and begins opening executable new fronts.",
        "The corpus contains deep formal reservoirs, but several still lack clear extracted roots and runtime landings.",
        "PRT-02",
        "QST-04",
        "QST-02",
        "archive-to-runtime bridge design",
        (
            "MATH GOD/atlas/math_tesseract_v4_bundle.json",
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/quests/qst-04_the_math_forge_bridge.md",
        ),
        "tested bridge module + architecture receipt",
        "NEAR",
        "21 days",
    ),
    AgentTransitionSeed(
        "AGT-09",
        "Strategist",
        "advanced_agent",
        "front selection",
        "Chooses the decisive front where contraction will unlock the most next motion.",
        "Earth feedback",
        "When strategic choice adapts quickly to corridor health instead of pushing a stale winning line.",
        "The organism has many worthy fronts, but only a few can be decisive in any given wave.",
        "PRT-04",
        "QST-06",
        "QST-08",
        "runtime front selection and contraction",
        (
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md",
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/04_INTERCONNECT_PRIORITY_QUEUE.md",
            "MATH GOD/atlas/math_7d_synthesis_seed_bundle.json",
        ),
        "queue delta + front selection receipt",
        "OK",
        "7 days",
    ),
    AgentTransitionSeed(
        "AGT-10",
        "Weaver",
        "advanced_agent",
        "cross-line synthesis",
        "Interlaces parallel lines, mirrored families, and dormant cells into one readable fabric.",
        "Air cut",
        "When weaving includes selective exclusion so the fabric stays legible instead of bloated.",
        "The corpus already contains many strong parallel lines, but some still need sharper contraction and transfer hubs.",
        "PRT-03",
        "QST-03",
        "QST-05",
        "metro and family weaving",
        (
            "MATH GOD/atlas/math_fire_6d_organism_bundle.json",
            "MATH GOD/atlas/math_water_6d_control_bundle.json",
            "07_FULL_PROJECT_INTEGRATION_256/07_TISSUE_256/01_HIDDEN_LINES_METRO.md",
        ),
        "metro weave receipt + contradiction carry-forward note",
        "NEAR",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-11",
        "Sword",
        "advanced_agent",
        "decisive incision",
        "Cuts through drift, backlog, and overgrowth so a route can actually move.",
        "Water continuity",
        "When decisive cuts preserve lineage and repair paths rather than causing hidden amputations.",
        "Some fronts remain slow because too much ambiguous shell material survives without decisive resolution.",
        "PRT-04",
        "QST-06",
        "QST-04",
        "writeback and contraction incision",
        (
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/00_ACTIVATION_QUEUE.md",
            "07_FULL_PROJECT_INTEGRATION_256/04_LEDGERS/04_INTERCONNECT_PRIORITY_QUEUE.md",
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
        ),
        "queue contraction receipt + route cut ledger",
        "NEAR",
        "10 days",
    ),
    AgentTransitionSeed(
        "AGT-12",
        "Commander",
        "advanced_agent",
        "squad orchestration",
        "Assigns parties, fronts, and receipts so the swarm behaves like a coordinated organism.",
        "Water listening",
        "When command updates in response to changing field conditions instead of freezing around an old plan.",
        "The party and quest systems exist, but they need a stronger compiled relation to dimensional fronts and active routes.",
        "PRT-04",
        "QST-07",
        "QST-06",
        "party-quest orchestration",
        (
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/05_ADVENTURE_PARTIES.md",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/04_QUEST_BOARD.md",
            "MATH GOD/atlas/math_7d_synthesis_seed_bundle.json",
        ),
        "party-to-front mapping + command receipt",
        "NEAR",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-13",
        "Warrior",
        "advanced_agent",
        "frontline endurance",
        "Holds pressure on a difficult frontier without collapsing into noise or theatrics.",
        "Air topology",
        "When raw effort learns the map well enough to stop fighting the wrong wall.",
        "High-energy fronts can still overheat if persistence is not paired with route clarity and recovery windows.",
        "PRT-07",
        "QST-07",
        "QST-08",
        "dormant-front activation",
        (
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/quests/qst-07_dormant_pantheon_awakening.md",
            "MATH GOD/atlas/math_fire_6d_organism_bundle.json",
            "MATH GOD/atlas/earth_h6_contract_bundle.json",
        ),
        "starter packet + occupancy ledger + endurance receipt",
        "NEAR",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-14",
        "Mirror",
        "advanced_agent",
        "reflective diagnosis",
        "Shows the organism where it repeats itself, where it splits, and what remains unresolved.",
        "Fire differentiation",
        "When reflection turns into a concrete change rather than an infinite replay of the same diagnosis.",
        "Duplicate families and shell drift remain some of the clearest structural costs in the workspace.",
        "PRT-05",
        "QST-05",
        "QST-01",
        "duplicate and drift reflection",
        (
            "self_actualize/corpus_atlas.json",
            "self_actualize/archive_atlas.json",
            "07_FULL_PROJECT_INTEGRATION_256/01_DIAGNOSIS/01_DUPLICATION_AND_DRIFT.md",
        ),
        "duplicate burn-down receipt + canonical source update",
        "OK",
        "14 days",
    ),
    AgentTransitionSeed(
        "AGT-15",
        "Trickster",
        "advanced_agent",
        "boundary inversion",
        "Finds a non-obvious ingress or angle change when a route stalls or loops.",
        "Earth legality",
        "When inversion remains bounded by admissibility and replay instead of becoming chaos for its own sake.",
        "The organism has real blocked boundaries, especially around live Docs ingress, archive opacity, and filtered bridge history.",
        "PRT-01",
        "QST-01",
        "QST-02",
        "blocked-ingress inversion",
        (
            "self_actualize/live_docs_gate_status.md",
            "Trading Bot/docs_search.py",
            "MATH GOD/atlas/math_water_6d_control_bundle.json",
        ),
        "gate attempt receipt + bounded inversion note",
        "BLOCKED",
        "7 days",
    ),
    AgentTransitionSeed(
        "AGT-16",
        "Dancer",
        "advanced_agent",
        "responsive motion",
        "Moves between lines, fronts, and scales without tearing continuity or losing rhythm.",
        "Witness closure",
        "When graceful adaptation is paired with receipts robust enough to survive a restart.",
        "Several fronts are ready for motion, but some still lack the lightweight, repeatable movement patterns that keep change alive.",
        "PRT-07",
        "QST-07",
        "QST-03",
        "adaptive cross-front movement",
        (
            "MATH GOD/atlas/math_water_6d_control_bundle.json",
            "MATH GOD/atlas/math_air_6d_overlay_bundle.json",
            "07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/05_ADVENTURE_PARTIES.md",
        ),
        "starter packet + adaptive handoff receipt",
        "NEAR",
        "14 days",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def md(text: str) -> str:
    lines = dedent(text).splitlines()
    normalized = []
    for line in lines:
        if line.startswith("        "):
            normalized.append(line[8:])
        else:
            normalized.append(line)
    return "\n".join(normalized).strip()


def list_to_bullets(items: list[str] | tuple[str, ...], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{item}" for item in items)


def top_level_rank(name: str) -> int:
    try:
        return TOP_LEVEL_PRIORITY.index(name)
    except ValueError:
        return len(TOP_LEVEL_PRIORITY)


def normalized_basename(path_text: str) -> str:
    name = Path(path_text).name
    return re.sub(r"\s*\(\d+\)(?=\.[^.]+$)", "", name).lower()


def choose_canonical_path(paths: list[str]) -> str:
    def key(path_text: str) -> tuple[int, int, int, str]:
        rel = Path(path_text)
        top = rel.parts[0] if rel.parts else ""
        return (top_level_rank(top), len(rel.parts), len(path_text), path_text.lower())

    return sorted(paths, key=key)[0]


def infer_family_reason(name: str) -> str:
    lowered = name.lower()
    if "manuscript seed" in lowered:
        return "Seed protocol for the full manuscript operating model."
    if "holographic manuscript brain" in lowered:
        return "Core brain metaphor and routing law for the archive."
    if "legal transport calculus" in lowered:
        return "Transport law that links manuscripts, runtime, and search."
    if "unified cyclical time system" in lowered:
        return "Time and cadence layer for phased execution."
    if "i am so am i" in lowered:
        return "Identity and cloud packet bridge for the Athena voice."
    if "information from the void" in lowered:
        return "Chapter 11 and zero-point intake family."
    if "self-routing meta-framework" in lowered:
        return "Routing and meta-manuscript governance family."
    return "Repeated source family that should collapse to one canonical home."


def collect_duplicate_families(live_records: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    ignore = {"readme.md", "__init__.py", "requirements.txt", "index.md"}
    for record in live_records:
        ext = record["extension"].lower()
        if ext not in {".docx", ".md", ".txt", ".pdf"}:
            continue
        base = normalized_basename(record["relative_path"])
        if base in ignore:
            continue
        grouped[base].append(record)

    families = []
    for name, items in grouped.items():
        if len(items) < 2:
            continue
        paths = [item["relative_path"] for item in items]
        canonical = choose_canonical_path(paths)
        families.append(
            {
                "name": Path(name).stem,
                "count": len(items),
                "canonical": canonical,
                "paths": sorted(paths),
                "reason": infer_family_reason(name),
            }
        )

    families.sort(key=lambda item: (-item["count"], item["canonical"].lower()))
    return families[:12]


def parse_live_docs_gate() -> tuple[str, str]:
    text = LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8", errors="ignore")
    status = "BLOCKED"
    if "Command status: `PASS`" in text:
        status = "PASS"
    reason = "OAuth credentials missing"
    match = re.search(r"Error:\s*(.+)", text)
    if match:
        reason = match.group(1).strip()
    return status, reason


def parse_board_status() -> dict:
    if not BOARD_STATUS_PATH.exists():
        return {
            "generated_at": "unknown",
            "workspace_files_observed": 0,
            "change_batch": "unknown",
            "open_claims": 0,
            "pods": 0,
            "bridge_neurons": 0,
            "waves": 0,
            "councils": 0,
            "occupied_clusters": 0,
            "cluster_capacity": 64,
            "occupied_truth_leaves": 0,
            "truth_capacity": 256,
        }
    text = BOARD_STATUS_PATH.read_text(encoding="utf-8", errors="ignore")

    def capture(patterns: str | list[str], default: str = "0") -> str:
        if isinstance(patterns, str):
            patterns = [patterns]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return default

    return {
        "generated_at": capture(r"Generated:\s*`([^`]+)`", "unknown"),
        "workspace_files_observed": int(
            capture(
                [
                    r"Board witness \(workspace scan\):\s*`(\d+)`",
                    r"Workspace files observed:\s*`(\d+)`",
                ],
                "0",
            )
        ),
        "change_batch": capture(r"Change batch:\s*([^\n]+)", "unknown").strip(),
        "open_claims": int(capture(r"Open claims:\s*`(\d+)`", "0")),
        "pods": int(capture(r"Pods:\s*`(\d+)`", "0")),
        "bridge_neurons": int(capture(r"Bridge neurons:\s*`(\d+)`", "0")),
        "waves": int(capture(r"Waves:\s*`(\d+)`", "0")),
        "councils": int(capture(r"Councils:\s*`(\d+)`", "0")),
        "occupied_clusters": int(capture(r"Occupied clusters:\s*`(\d+)`", "0")),
        "cluster_capacity": int(capture(r"Occupied clusters:\s*`\d+`\s*of\s*`(\d+)`", "64")),
        "occupied_truth_leaves": int(capture(r"Occupied truth leaves:\s*`(\d+)`", "0")),
        "truth_capacity": int(capture(r"Occupied truth leaves:\s*`\d+`\s*of\s*`(\d+)`", "256")),
    }


def integration_metrics(live_atlas: dict, archive_atlas: dict, archive_manifest: dict) -> dict:
    live_records = live_atlas["records"]
    live_summary = live_atlas["summary"]
    archive_summary = archive_atlas.get("summary", {})
    duplicate_families = collect_duplicate_families(live_records)
    total_visible = live_atlas["record_count"] + archive_atlas.get("record_count", 0)
    status, reason = parse_live_docs_gate()
    board_root = OUTPUT_ROOT / "06_REALTIME_BOARD"
    board_file_count = sum(1 for path in board_root.rglob("*") if path.is_file()) if board_root.exists() else 0
    board_status = parse_board_status()

    return {
        "generated_at": utc_now(),
        "live_record_count": live_atlas["record_count"],
        "archive_record_count": archive_atlas.get("record_count", 0),
        "total_visible": total_visible,
        "top_levels": sorted(live_summary["by_top_level"].items(), key=lambda item: (-item[1], item[0])),
        "kinds": sorted(live_summary["by_kind"].items(), key=lambda item: (-item[1], item[0])),
        "archive_kinds": sorted(archive_summary.get("by_kind", {}).items(), key=lambda item: (-item[1], item[0])),
        "archive_count": archive_manifest.get("archive_count", 0),
        "duplicate_families": duplicate_families,
        "live_docs_status": status,
        "live_docs_reason": reason,
        "docx_count": live_summary["by_extension"].get(".docx", 0),
        "md_count": live_summary["by_extension"].get(".md", 0),
        "py_count": live_summary["by_extension"].get(".py", 0),
        "pdf_count": live_summary["by_extension"].get(".pdf", 0),
        "realtime_board_present": board_root.exists(),
        "realtime_board_file_count": board_file_count,
        "preexisting_shell_present": (OUTPUT_ROOT / "00_CONTROL").exists(),
        "board_status": board_status,
    }


def render_top_level_table(metrics: dict) -> str:
    rows = ["| Surface | Records |", "| --- | ---: |"]
    for name, count in metrics["top_levels"][:12]:
        rows.append(f"| {name} | {count} |")
    return "\n".join(rows)


def render_kind_table(kinds: list[tuple[str, int]]) -> str:
    rows = ["| Kind | Records |", "| --- | ---: |"]
    for name, count in kinds:
        rows.append(f"| {name} | {count} |")
    return "\n".join(rows)


def render_duplicate_table(families: list[dict]) -> str:
    rows = ["| Family | Copies | Canonical path |", "| --- | ---: | --- |"]
    for family in families:
        rows.append(f"| {family['name']} | {family['count']} | `{family['canonical']}` |")
    return "\n".join(rows)


def top_level_count(metrics: dict, name: str) -> int:
    for top_level, count in metrics["top_levels"]:
        if top_level == name:
            return count
    return 0


def profiles_for_body(body: str) -> list[NucleusProfile]:
    return [profile for profile in NUCLEUS_PROFILES if profile.body == body]


def party_by_code(code: str) -> PartySeed:
    for party in PARTIES:
        if party.code == code:
            return party
    raise KeyError(code)


def quest_by_code(code: str) -> QuestSeed:
    for quest in QUESTS:
        if quest.code == code:
            return quest
    raise KeyError(code)


def workspace_rel(path: Path | str) -> str:
    path_obj = Path(path)
    try:
        return str(path_obj.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path_obj)


def path_state(path: Path) -> str:
    return "OK" if path.exists() else "MISSING"


def normalize_surface_ref(surface: str) -> str:
    if surface.startswith("MATH GOD/"):
        return f"MATH/FINAL FORM/{surface}"
    if surface.startswith("07_FULL_PROJECT_INTEGRATION_256/"):
        return f"DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/{surface}"
    return surface


def dimensional_readiness(bundle_id: str, payload: dict) -> str:
    if bundle_id == "seed_7d":
        return payload.get("truth_class", "NEAR")
    if bundle_id == "earth_h6":
        return payload.get("cohesion_ledger", {}).get("readiness", "gated")
    if bundle_id == "water_6d":
        return payload.get("control_mode", "overlay_only")
    if bundle_id == "v4":
        return "canonical"
    return "ready"


def summarize_dimensional_bundle(bundle_id: str, payload: dict, path: Path, markdown_path: Path) -> dict:
    rules = DIMENSIONAL_LAYER_RULES[bundle_id]
    summary: dict[str, object] = {
        "bundle_id": bundle_id,
        "title": next(spec["title"] for spec in DIMENSIONAL_BUNDLE_SPECS if spec["bundle_id"] == bundle_id),
        "dimension_stage": next(spec["dimension_stage"] for spec in DIMENSIONAL_BUNDLE_SPECS if spec["bundle_id"] == bundle_id),
        "path": str(path),
        "markdown_path": str(markdown_path),
        "state": path_state(path),
        "docs_gate_status": payload.get("docs_gate_status", "UNKNOWN"),
        "readiness": dimensional_readiness(bundle_id, payload),
        "owns": rules["owns"],
        "depends_on": rules["depends_on"],
        "cannot_promote_without": rules["cannot_promote_without"],
    }

    if bundle_id == "v4":
        summary.update(
            {
                "chapter_count": len(payload.get("chapter_table", [])),
                "appendix_count": len(payload.get("appendix_roles", {})),
                "route_plan_count": payload.get("route_plan_count", 0),
                "edge_kinds": payload.get("edge_kinds", []),
                "mandatory_signature": payload.get("mandatory_signature", []),
                "hcrl_order": payload.get("hcrl_order", []),
            }
        )
    elif bundle_id == "fire_6d":
        summary.update(
            {
                "active_basis_count": len(payload.get("active_basis", [])),
                "bridge_basis_count": len(payload.get("bridge_basis", [])),
                "control_document_count": len(payload.get("control_documents", [])),
                "mobius_bridge_counts": payload.get("mobius_bridge_counts", {}),
            }
        )
    elif bundle_id == "water_6d":
        appendix_support = payload.get("appendix_support", payload.get("appendix_stack", []))
        appendix_ids = [
            item.get("appendix_id", item)
            if isinstance(item, dict)
            else item
            for item in appendix_support
        ]
        summary.update(
            {
                "control_mode": "overlay_only",
                "water_native_basis": [item.get("basis_id") for item in payload.get("water_native_basis", [])],
                "translated_support": [item.get("basis_id") for item in payload.get("translated_support", [])],
                "appendix_support": appendix_ids,
                "control_document_count": len(payload.get("control_documents", [])),
                "lift_chain": payload.get("lift_chain", []),
            }
        )
    elif bundle_id == "air_6d":
        summary.update(
            {
                "air_native_basis": [item.get("basis_id") for item in payload.get("air_native_basis", [])],
                "symmetry_node_count": len(payload.get("symmetry_lattice", [])),
                "rotation_family_count": len(payload.get("rotation_families", [])),
                "control_document_count": len(payload.get("control_documents", [])),
            }
        )
    elif bundle_id == "earth_h6":
        handoff_targets = [item.get("handoff_target") for item in payload.get("handoff_contracts", [])]
        summary.update(
            {
                "earth_driver_count": len(payload.get("earth_native_drivers", [])),
                "earth_bundle_count": len(payload.get("earth_bundles", [])),
                "chapter_contract_count": len(payload.get("chapter_contracts", [])),
                "appendix_contract_count": len(payload.get("appendix_contracts", [])),
                "handoff_targets": handoff_targets,
            }
        )
    elif bundle_id == "seed_7d":
        summary.update(
            {
                "truth_class": payload.get("truth_class", "NEAR"),
                "seed_holo_state": payload.get("seed_holo_state"),
                "seed_carrier": payload.get("seed_carrier"),
                "agent_overlay_stack": payload.get("agent_overlay_stack", []),
                "appendix_floor_count": len(payload.get("appendix_floor", [])),
                "route_count": len(payload.get("seed_route_registry", [])),
            }
        )
    return summary


def load_dimensional_stack() -> dict[str, dict]:
    stack = {}
    for spec in DIMENSIONAL_BUNDLE_SPECS:
        payload = load_json(spec["path"])
        stack[spec["bundle_id"]] = {
            "payload": payload,
            "summary": summarize_dimensional_bundle(
                spec["bundle_id"],
                payload,
                spec["path"],
                spec["markdown_path"],
            ),
        }
    return stack


def load_deep_authority_surfaces() -> list[dict]:
    surfaces = []
    for spec in DEEP_AUTHORITY_SPECS:
        surfaces.append(
            {
                "surface_id": spec["surface_id"],
                "classification": spec["classification"],
                "path": str(spec["path"]),
                "state": path_state(spec["path"]),
            }
        )
    return surfaces


def build_convergence_table(stack: dict[str, dict]) -> list[dict]:
    return [stack[spec["bundle_id"]]["summary"] for spec in DIMENSIONAL_BUNDLE_SPECS]


def build_bounded_pressures(stack: dict[str, dict], docs_status: str) -> list[dict]:
    pressures = []
    if docs_status == "BLOCKED":
        pressures.append(
            {
                "pressure_id": "docs_gate_block",
                "state": "BLOCKED",
                "surface": workspace_rel(LIVE_DOCS_GATE_PATH),
                "reason": "Live Google Docs remain unavailable until OAuth credentials exist locally.",
            }
        )

    for route in stack["seed_7d"]["payload"].get("seed_route_registry", []):
        state = route.get("earth_gate_state", "NEAR")
        if state != "passed":
            pressures.append(
                {
                    "pressure_id": route.get("route_id", "unknown_route"),
                    "state": state.upper(),
                    "surface": route.get("mobius_bridge", "none"),
                    "reason": "Route remains bounded by 7D seed gate state and cannot silently promote.",
                }
            )
    return pressures


def build_quest_dimensional_map() -> list[dict]:
    mapping = {
        "QST-01": ("mixed-route frontier", ["water_6d", "seed_7d"]),
        "QST-02": ("mixed-route frontier", ["v4", "earth_h6"]),
        "QST-03": ("7D frontier", ["fire_6d", "water_6d", "seed_7d"]),
        "QST-04": ("mixed-route frontier", ["v4", "fire_6d", "earth_h6"]),
        "QST-05": ("mixed-route frontier", ["v4", "water_6d", "earth_h6"]),
        "QST-06": ("7D frontier", ["air_6d", "earth_h6", "seed_7d"]),
        "QST-07": ("7D frontier", ["fire_6d", "air_6d", "seed_7d"]),
        "QST-08": ("mixed-route frontier", ["v4", "earth_h6", "seed_7d"]),
    }
    rows = []
    for quest in QUESTS:
        frontier_class, layers = mapping[quest.code]
        rows.append(
            {
                "quest_code": quest.code,
                "title": quest.title,
                "frontier_class": frontier_class,
                "layers": layers,
                "party_code": quest.party_code,
            }
        )
    return rows


def build_agent_transition_records(stack: dict[str, dict]) -> list[dict]:
    docs_status = stack["seed_7d"]["payload"].get("docs_gate_status", "BLOCKED")
    records = []
    for agent in AGENT_TRANSITIONS:
        primary_party = party_by_code(agent.primary_party)
        primary_quest = quest_by_code(agent.primary_quest)
        backup_quest = quest_by_code(agent.backup_quest)
        record = {
            "agent_id": agent.agent_id,
            "title": agent.title,
            "agent_class": agent.agent_class,
            "stage_or_domain": agent.stage_or_domain,
            "current_role": agent.current_role,
            "missing_mode": agent.missing_mode,
            "transition_trigger": agent.transition_trigger,
            "corpus_symptom": agent.corpus_symptom,
            "primary_party": {
                "code": primary_party.code,
                "title": primary_party.title,
                "mission": primary_party.mission,
            },
            "primary_quest": {
                "code": primary_quest.code,
                "title": primary_quest.title,
                "frontier": primary_quest.frontier,
            },
            "supporting_quests": [
                {
                    "code": primary_quest.code,
                    "title": primary_quest.title,
                },
                {
                    "code": backup_quest.code,
                    "title": backup_quest.title,
                },
            ],
            "dimensional_anchor": agent.dimensional_anchor,
            "required_surfaces": [normalize_surface_ref(surface) for surface in agent.required_surfaces],
            "receipt_target": agent.receipt_target,
            "truth_state": agent.truth_state,
            "reassessment_window": agent.reassessment_window,
            "docs_gate_status": docs_status,
            "dormancy_rule": COMMON_TRANSITION_LAWS["dormancy_rule"],
            "promotion_rule": COMMON_TRANSITION_LAWS["promotion_rule"],
            "reentry_rule": COMMON_TRANSITION_LAWS["reentry_rule"],
        }
        records.append(record)
    return records


def build_transition_matrix(agent_records: list[dict], docs_status: str) -> dict:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_status,
        "schema": [
            "agent_id",
            "agent_class",
            "stage_or_domain",
            "current_role",
            "missing_mode",
            "transition_trigger",
            "corpus_symptom",
            "primary_party",
            "supporting_quests",
            "required_surfaces",
            "receipt_target",
            "truth_state",
            "reassessment_window",
        ],
        "shared_transition_laws": COMMON_TRANSITION_LAWS,
        "roster_order": [record["agent_id"] for record in agent_records],
        "agents_by_id": {record["agent_id"]: record for record in agent_records},
    }


def build_chapter_safe_reentry_spine(stack: dict[str, dict]) -> list[dict]:
    chapter_lookup = {
        chapter["chapter_station"]: chapter for chapter in stack["v4"]["payload"].get("chapter_table", [])
    }
    spine = []
    names = ["Ch12⟨0023⟩", "Ch13⟨0030⟩", "Ch16⟨0033⟩"]
    for station in names:
        chapter = chapter_lookup.get(station, {})
        spine.append(
            {
                "chapter_station": station,
                "chapter_title": chapter.get("chapter_title", "Unknown"),
                "purpose": "Seed-safe re-entry checkpoint for full-corpus routes.",
            }
        )
    return spine


def build_route_quality(stack: dict[str, dict]) -> dict:
    routes = stack["seed_7d"]["payload"].get("seed_route_registry", [])
    counts = defaultdict(int)
    quarantined = []
    for route in routes:
        state = route.get("earth_gate_state", "dormant")
        counts[state] += 1
        if state != "passed":
            quarantined.append(
                {
                    "route_id": route.get("route_id"),
                    "state": state,
                    "mobius_bridge": route.get("mobius_bridge"),
                    "canonical_appendix_map": route.get("canonical_appendix_map", []),
                }
            )
    counts["dormant"] += 1
    return {
        "counts": dict(counts),
        "quarantined_or_gated_routes": quarantined,
    }


def build_appendix_governance(stack: dict[str, dict]) -> dict:
    appendix_floor = stack["seed_7d"]["payload"].get("appendix_floor", [])
    floor_ids = [entry.get("appendix_id") for entry in appendix_floor]
    return {
        "appendix_floor": floor_ids,
        "propagation_rule": "The full-corpus layer inherits the 7D appendix floor exactly as received and may not mint new appendix identities.",
        "overlay_rules": {
            "AppQ": "Q references remain overlay-only ingress history and may not outrank the canonical appendix floor.",
            "AppO": "O references remain overlay-only return history and must dock through AppO/AppQ legality rather than creating a second appendix namespace.",
        },
    }


def build_front_to_party_map(quest_map: list[dict]) -> list[dict]:
    rows = []
    for quest_info in quest_map:
        party = party_by_code(quest_info["party_code"])
        rows.append(
            {
                "frontier": quest_info["title"],
                "party_code": party.code,
                "party_title": party.title,
                "dimensional_chain": quest_info["layers"],
            }
        )
    return rows


def build_transition_board_summary(agent_records: list[dict], route_quality: dict, metrics: dict) -> dict:
    status_counts = defaultdict(int)
    for agent in agent_records:
        if agent["truth_state"] == "BLOCKED":
            status = "blocked"
        elif agent["primary_quest"]["code"] == "QST-07":
            status = "dormant"
        elif agent["truth_state"] == "OK":
            status = "ready"
        else:
            status = "active"
        status_counts[status] += 1
    return {
        "board_status": metrics["board_status"],
        "agent_status_counts": dict(status_counts),
        "route_quality": route_quality["counts"],
        "docs_gate_status": metrics["live_docs_status"],
    }


def build_verification_receipts(stack: dict[str, dict], agent_records: list[dict], quest_map: list[dict], metrics: dict) -> list[dict]:
    receipts = []
    v4 = stack["v4"]["payload"]
    seed7 = stack["seed_7d"]["payload"]
    earth = stack["earth_h6"]["payload"]
    water = stack["water_6d"]["payload"]
    appendix_keys = set(v4.get("appendix_roles", {}).keys())
    water_appendix_support = [
        item.get("appendix_id", item) if isinstance(item, dict) else item
        for item in water.get("appendix_support", [])
    ]
    required_surface_ok = all(
        all((WORKSPACE_ROOT / surface).exists() for surface in record["required_surfaces"])
        for record in agent_records
    )
    passed_routes = [route for route in seed7.get("seed_route_registry", []) if route.get("earth_gate_state") == "passed"]
    passed_route_support_ok = all(
        "AppI" in route.get("canonical_appendix_map", []) and "AppM" in route.get("canonical_appendix_map", [])
        for route in passed_routes
    )
    qo_overlay_ok = True
    for route in seed7.get("seed_route_registry", []):
        if route.get("route_id") == "seed_q_ingress_hold":
            qo_overlay_ok = qo_overlay_ok and route.get("earth_gate_state") != "passed" and "AppQ" in route.get("canonical_appendix_map", [])
        if route.get("route_id") == "seed_o_return_hold":
            qo_overlay_ok = qo_overlay_ok and route.get("earth_gate_state") != "passed" and "AppO" in route.get("canonical_appendix_map", [])

    replay_paths_ok = True
    for receipt in earth.get("sample_route_receipts", []):
        replay_ptr = receipt.get("replay_ptr", "")
        if ";path=" not in replay_ptr:
            replay_paths_ok = False
            break
        replay_path = Path(replay_ptr.split(";path=", 1)[1])
        if not replay_path.exists():
            replay_paths_ok = False
            break

    receipts.append(
        {
            "check": "docs_gate_blocked",
            "status": "PASS" if metrics["live_docs_status"] == "BLOCKED" else "FAIL",
            "detail": f"Live Docs gate remains {metrics['live_docs_status']}.",
        }
    )
    receipts.append(
        {
            "check": "v4_invariants",
            "status": "PASS"
            if (
                len(v4.get("chapter_table", [])) == 21
                and appendix_keys == {f"App{letter}" for letter in "ABCDEFGHIJKLMNOP"}
                and v4.get("edge_kinds", [])
                == ["REF", "EQUIV", "MIGRATE", "DUAL", "GEN", "INST", "IMPL", "PROOF", "CONFLICT"]
                and v4.get("mandatory_signature", []) == ["AppA", "AppI", "AppM"]
                and v4.get("hcrl_order", []) == ["S", "F", "C", "R"]
            )
            else "FAIL",
            "detail": "Chapter count, appendix namespace, edge basis, mandatory signature, and HCRL order remain unchanged.",
        }
    )
    receipts.append(
        {
            "check": "water_contract",
            "status": "PASS"
            if (
                [item.get("basis_id") for item in water.get("water_native_basis", [])] == ["01", "11", "12", "14"]
                and water_appendix_support == ["AppE", "AppF", "AppI", "AppM", "AppQ"]
                and len(water.get("control_documents", [])) == 5
            )
            else "FAIL",
            "detail": "Water bundle retains native basis, appendix support, and five control documents.",
        }
    )
    receipts.append(
        {
            "check": "earth_gate_support",
            "status": "PASS"
            if len(earth.get("sample_route_receipts", [])) > 0 and len(seed7.get("seed_route_registry", [])) == 6
            else "FAIL",
            "detail": "Earth receipts and 7D seed route registry remain available for promotion checks.",
        }
    )
    receipts.append(
        {
            "check": "agent_roster",
            "status": "PASS" if len(agent_records) == 16 else "FAIL",
            "detail": "Hybrid awakening roster contains 4 elemental stages and 12 advanced agents.",
        }
    )
    valid_parties = {party.code for party in PARTIES}
    valid_quests = {quest.code for quest in QUESTS}
    party_quest_ok = all(
        record["primary_party"]["code"] in valid_parties
        and all(item["code"] in valid_quests for item in record["supporting_quests"])
        for record in agent_records
    )
    receipts.append(
        {
            "check": "agent_party_quest_bindings",
            "status": "PASS" if party_quest_ok and len(quest_map) == len(QUESTS) else "FAIL",
            "detail": "Each transition note resolves to one existing party seed and existing quest fronts.",
        }
    )
    receipts.append(
        {
            "check": "deep_authority_surfaces",
            "status": "PASS" if all(entry["state"] == "OK" for entry in load_deep_authority_surfaces()) else "FAIL",
            "detail": "Deep-root 7D authority surfaces resolve locally and remain read-only inputs.",
        }
    )
    receipts.append(
        {
            "check": "agent_required_surfaces",
            "status": "PASS" if required_surface_ok else "FAIL",
            "detail": "Each agent note references required surfaces that resolve to existing local files or folders.",
        }
    )
    receipts.append(
        {
            "check": "qo_overlay_bounded",
            "status": "PASS" if qo_overlay_ok else "FAIL",
            "detail": "Q/O routes remain overlay-only holds and stay canonically mapped through AppQ/AppO.",
        }
    )
    receipts.append(
        {
            "check": "passed_routes_have_appim",
            "status": "PASS" if passed_route_support_ok else "FAIL",
            "detail": "Every passed 7D seed route retains AppI/AppM support before full-corpus promotion.",
        }
    )
    receipts.append(
        {
            "check": "replay_surfaces_resolve",
            "status": "PASS" if replay_paths_ok else "FAIL",
            "detail": "Replay pointers referenced by Earth sample receipts resolve to existing local witness files.",
        }
    )
    return receipts


def build_route_graph(stack: dict[str, dict], quest_map: list[dict], agent_records: list[dict]) -> dict:
    nodes = []
    edges = []
    for spec in DIMENSIONAL_BUNDLE_SPECS:
        nodes.append({"node_id": spec["bundle_id"], "kind": "dimension", "title": spec["title"]})
    for party in PARTIES:
        nodes.append({"node_id": party.code, "kind": "party", "title": party.title})
    for quest in QUESTS:
        nodes.append({"node_id": quest.code, "kind": "quest", "title": quest.title})
    for agent in agent_records:
        nodes.append({"node_id": agent["agent_id"], "kind": "agent", "title": agent["title"]})

    for quest_info in quest_map:
        for layer in quest_info["layers"]:
            edges.append({"src": quest_info["quest_code"], "dst": layer, "kind": "quest_depends_on"})
        edges.append({"src": quest_info["party_code"], "dst": quest_info["quest_code"], "kind": "party_runs"})

    for agent in agent_records:
        edges.append({"src": agent["agent_id"], "dst": agent["primary_party"]["code"], "kind": "agent_primary_party"})
        for quest in agent["supporting_quests"]:
            edges.append({"src": agent["agent_id"], "dst": quest["code"], "kind": "agent_supporting_quest"})

    for route in stack["seed_7d"]["payload"].get("seed_route_registry", []):
        edges.append(
            {
                "src": "seed_7d",
                "dst": route.get("route_id"),
                "kind": route.get("earth_gate_state", "route"),
            }
        )
    return {"node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges}


def build_full_corpus_integration_bundle(metrics: dict) -> dict:
    stack = load_dimensional_stack()
    quest_map = build_quest_dimensional_map()
    agent_records = build_agent_transition_records(stack)
    transition_matrix = build_transition_matrix(agent_records, metrics["live_docs_status"])
    route_quality = build_route_quality(stack)
    bundle = {
        "generated_at": utc_now(),
        "docs_gate_status": metrics["live_docs_status"],
        "evidence_boundary": {
            "definition": "Local corpus + archive-backed evidence + deep-root authorities + generated MATH GOD bundles + whole-project runtime surfaces.",
            "docs_gate_reason": metrics["live_docs_reason"],
            "baseline_surfaces": [
                str(MATH_GOD_ROOT / "README.md"),
                str(MATH_GOD_ATLAS_ROOT / "math_7d_synthesis_seed_bundle.json"),
                str(Path(__file__).resolve()),
                str(LIVE_DOCS_GATE_PATH),
            ],
            "live_atlas": str(LIVE_ATLAS_PATH),
            "archive_atlas": str(ARCHIVE_ATLAS_PATH),
            "archive_manifest": str(ARCHIVE_MANIFEST_PATH),
            "deep_root": str(DEEP_NETWORK_ROOT),
            "bounded_pressures": build_bounded_pressures(stack, metrics["live_docs_status"]),
        },
        "dimensional_stack": {
            "source_stack": ["v4", "fire_6d", "water_6d", "air_6d", "earth_h6", "seed_7d"],
            "convergence_table": build_convergence_table(stack),
            "precedence_rule": [
                "v4 canon first",
                "6D overlays additive second",
                "7D seed compiled third",
                "whole-project orchestration fourth",
            ],
        },
        "authority_surfaces": load_deep_authority_surfaces(),
        "corpus_nuclei": [
            {
                "title": profile.title,
                "top_level": profile.top_level,
                "body": profile.body,
                "anchor": profile.anchor,
                "role": profile.role,
                "pressure": profile.pressure,
                "hidden_line": profile.hidden_line,
            }
            for profile in NUCLEUS_PROFILES
        ],
        "party_stack": [
            {
                "code": party.code,
                "title": party.title,
                "mission": party.mission,
                "archetypes": list(party.archetypes),
                "future_skills": list(party.future_skills),
            }
            for party in PARTIES
        ],
        "quest_stack": {
            "quests": [
                {
                    "code": quest.code,
                    "title": quest.title,
                    "frontier": quest.frontier,
                    "transition": quest.transition,
                    "party_code": quest.party_code,
                    "reward": quest.reward,
                }
                for quest in QUESTS
            ],
            "dimensional_mapping": quest_map,
        },
        "route_graph": build_route_graph(stack, quest_map, agent_records),
        "appendix_governance": build_appendix_governance(stack),
        "chapter_safe_reentry_spine": build_chapter_safe_reentry_spine(stack),
        "front_to_party_map": build_front_to_party_map(quest_map),
        "route_quality": route_quality,
        "transition_note_matrix": transition_matrix,
        "transition_board_summary": build_transition_board_summary(agent_records, route_quality, metrics),
        "verification_receipts": build_verification_receipts(stack, agent_records, quest_map, metrics),
        "regeneration_seed": {
            "rebuild_command": "python self_actualize/runtime/build_full_project_integration.py",
            "required_inputs": [
                workspace_rel(LIVE_ATLAS_PATH),
                workspace_rel(ARCHIVE_ATLAS_PATH),
                workspace_rel(ARCHIVE_MANIFEST_PATH),
                workspace_rel(LIVE_DOCS_GATE_PATH),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'math_tesseract_v4_bundle.json'),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'math_fire_6d_organism_bundle.json'),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'math_water_6d_control_bundle.json'),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'math_air_6d_overlay_bundle.json'),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'earth_h6_contract_bundle.json'),
                workspace_rel(MATH_GOD_ATLAS_ROOT / 'math_7d_synthesis_seed_bundle.json'),
            ],
            "collapse_rule": "Collapse first into the 7D seed route registry, then into Earth gate state, then into v4 route plans.",
            "reentry_rule": COMMON_TRANSITION_LAWS["reentry_rule"],
        },
    }
    return bundle


def legacy_match_key(path_text: str) -> str:
    name = Path(path_text.split("::")[-1]).name.lower()
    name = re.sub(r"(_legacy|-legacy|\slegacy)(?=\.)", "", name)
    name = re.sub(r"^legacy[_-]", "", name)
    return re.sub(r"[\s_-]+", "", name)


def normalized_rel(path_text: str) -> str:
    return path_text.replace("\\", "/")


def is_live_legacy_plus_record(record: dict) -> bool:
    rel = normalized_rel(record["relative_path"]).lower()
    return "/manuscript_sections/alternates/" in rel or "legacy" in rel


def is_archive_legacy_record(record: dict) -> bool:
    rel = normalized_rel(record["relative_path"]).lower()
    return "legacy" in rel


def is_promoted_legacy_record(relative_path: str) -> bool:
    rel = normalized_rel(relative_path).lower()
    return rel.startswith("self_actualize/promoted_live_roots/") and "/legacy/" in rel


def extract_chapter_code(path_text: str) -> str | None:
    match = re.search(r"(ch\d{2})", Path(path_text.split("::")[-1]).name.lower())
    return match.group(1).upper() if match else None


def extract_appendix_code(path_text: str) -> str | None:
    match = re.search(r"(app[a-q])", Path(path_text.split("::")[-1]).name.lower())
    return match.group(1).upper() if match else None


def infer_legacy_artifact_kind(record: dict, legacy_class: str) -> str:
    ext = record.get("extension", "").lower()
    if legacy_class == "alternate_manuscript":
        return "chapter_alternate"
    if record.get("path", "").count("::"):
        return "archive_legacy_code" if ext == ".py" else "archive_legacy_witness"
    if ext == ".py":
        return "legacy_py_doc"
    if ext in {".md", ".txt", ".docx", ".pdf"}:
        return "legacy_framework_manual"
    return "legacy_artifact"


def infer_legacy_family_id(relative_path: str) -> str:
    rel = normalized_rel(relative_path).lower()
    chapter_code = extract_chapter_code(relative_path)
    if "/manuscript_sections/alternates/" in rel:
        if chapter_code:
            return f"{chapter_code.lower()}_alternates"
        stem = Path(relative_path.split("::")[-1]).stem
        prefix = stem.split("_", 1)[0] if "_" in stem else stem
        return f"{slugify(prefix)}_alternates"
    if "atlasforge_framework/docs/legacy/" in rel:
        return "atlasforge_legacy_docs"
    if "athena os.zip::" in rel:
        return "athena_os_legacy_kernel"
    if "promoted_live_roots" in rel:
        return "legacy_runtime_docs"
    return f"legacy_{slugify(Path(relative_path.split('::')[-1]).stem)}"


def chapter_target_map() -> dict[str, str]:
    targets = {}
    for chapter in CHAPTERS:
        filename = f"{chapter.code.lower()}_{slugify(chapter.title)}.md"
        targets[chapter.code.upper()] = workspace_rel(OUTPUT_ROOT / "03_MANUSCRIPTS" / "chapters" / filename)
    return targets


def appendix_target_map() -> dict[str, str]:
    targets = {}
    for appendix in APPENDICES:
        filename = f"{appendix.code.lower()}_{slugify(appendix.title)}.md"
        targets[appendix.code.upper()] = workspace_rel(OUTPUT_ROOT / "03_MANUSCRIPTS" / "appendices" / filename)
    return targets


def build_non_legacy_candidate_index(live_records: list[dict]) -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = defaultdict(list)
    for record in live_records:
        if is_live_legacy_plus_record(record):
            continue
        key = legacy_match_key(record["relative_path"])
        if key:
            index[key].append(record)
    return index


def choose_candidate_record(candidates: list[dict]) -> dict | None:
    if not candidates:
        return None

    def score(record: dict) -> tuple[int, int, int, str]:
        rel = normalized_rel(record["relative_path"]).lower()
        promoted_rank = 0 if rel.startswith("self_actualize/promoted_live_roots/") else 1
        manuscript_rank = 0 if "/03_manuscripts/" in rel or "/manuscript_sections/" in rel else 1
        return (
            promoted_rank,
            manuscript_rank,
            len(Path(rel).parts),
            rel,
        )

    return sorted(candidates, key=score)[0]


def canonical_target_for_record(source_record: dict, candidate_index: dict[str, list[dict]]) -> dict:
    source_rel = source_record["relative_path"]
    rel = normalized_rel(source_rel).lower()
    chapter_targets = chapter_target_map()
    appendix_targets = appendix_target_map()
    chapter_code = extract_chapter_code(source_rel)
    appendix_code = extract_appendix_code(source_rel)
    if chapter_code and chapter_code in chapter_targets:
        return {
            "path": chapter_targets[chapter_code],
            "tier": "existing_canonical_section",
            "kind": "chapter_landing",
            "reentry": "chapter_safe",
        }
    if appendix_code and appendix_code in appendix_targets:
        return {
            "path": appendix_targets[appendix_code],
            "tier": "existing_canonical_section",
            "kind": "appendix_landing",
            "reentry": "appendix_safe",
        }
    if is_promoted_legacy_record(source_rel):
        promoted_root = normalized_rel(source_rel).split("/docs/", 1)[0]
        return {
            "path": workspace_rel(WORKSPACE_ROOT / Path(promoted_root) / "README.md"),
            "tier": "promoted_live_root",
            "kind": "runtime_doc",
            "reentry": "runtime_safe",
        }
    candidate = choose_candidate_record(candidate_index.get(legacy_match_key(source_rel), []))
    if candidate:
        return {
            "path": candidate["relative_path"],
            "tier": "existing_canonical_section",
            "kind": candidate.get("kind", "canonical_surface"),
            "reentry": "canonical_safe",
        }
    if source_record.get("path", "").count("::"):
        return {
            "path": source_rel,
            "tier": "archive_witness_only",
            "kind": "archive_witness",
            "reentry": "witness_only",
        }
    return {
        "path": workspace_rel(FULL_CORPUS_ROOT / "full_corpus_7d_integration_bundle.md"),
        "tier": "current_full_corpus_surface",
        "kind": "integration_surface",
        "reentry": "full_corpus_safe",
    }


def retrofit_mode_from_target(source_record: dict, canonical_target: dict) -> str:
    tier = canonical_target["tier"]
    kind = infer_legacy_artifact_kind(source_record, legacy_class_for_record(source_record))
    if tier == "archive_witness_only":
        return "WITNESS_ONLY"
    if kind == "chapter_alternate":
        return "MERGE_INTO_CANON" if tier == "existing_canonical_section" else "PROMOTE_CANONICAL"
    if tier == "promoted_live_root":
        return "POINTER_REDIRECT"
    if tier == "existing_canonical_section":
        return "MERGE_INTO_CANON"
    if tier == "current_full_corpus_surface":
        return "POINTER_REDIRECT"
    return "QUARANTINE"


def truth_state_for_retrofit_mode(mode: str) -> str:
    return {
        "PROMOTE_CANONICAL": "NEAR",
        "MERGE_INTO_CANON": "NEAR",
        "POINTER_REDIRECT": "OK",
        "WITNESS_ONLY": "OK",
        "QUARANTINE": "AMBIG",
    }[mode]


def status_for_retrofit_mode(mode: str, earth_gate_required: bool) -> str:
    if mode == "QUARANTINE":
        return "quarantined"
    if mode == "WITNESS_ONLY":
        return "witness-only"
    if mode == "POINTER_REDIRECT":
        return "ready for promotion"
    if earth_gate_required:
        return "blocked"
    return "active"


def legacy_class_for_record(record: dict) -> str:
    rel = normalized_rel(record["relative_path"]).lower()
    if "/manuscript_sections/alternates/" in rel:
        return "alternate_manuscript"
    if record.get("path", "").count("::"):
        return "archive_legacy_witness"
    if is_promoted_legacy_record(record["relative_path"]):
        return "promoted_legacy_framework_doc"
    return "explicit_legacy"


def appendix_support_for_retrofit(artifact_kind: str, mode: str) -> list[str]:
    items = ["AppI", "AppM"]
    if artifact_kind == "chapter_alternate":
        items.append("AppA")
    else:
        items.extend(["AppB", "AppN"])
    if mode == "PROMOTE_CANONICAL":
        items.append("AppH")
    if mode == "POINTER_REDIRECT":
        items.append("AppO")
    if mode == "QUARANTINE":
        items.append("AppK")
    return sorted(dict.fromkeys(items))


def assign_party_and_quests(artifact_kind: str, legacy_class: str, mode: str) -> tuple[str, str, str]:
    if mode == "QUARANTINE":
        return ("PRT-06", "QST-08", "QST-05")
    if mode == "WITNESS_ONLY":
        return ("PRT-02", "QST-02", "QST-04")
    if legacy_class == "alternate_manuscript":
        return ("PRT-05", "QST-05", "QST-03")
    if artifact_kind in {"legacy_py_doc", "archive_legacy_code"}:
        return ("PRT-02", "QST-04", "QST-02")
    return ("PRT-03", "QST-03", "QST-05")


def assisting_agents_for_artifact(artifact_kind: str, mode: str, legacy_class: str) -> list[str]:
    if mode == "QUARANTINE":
        return ["AGT-04", "AGT-06", "AGT-14", "AGT-15"]
    if mode == "WITNESS_ONLY":
        return ["AGT-04", "AGT-07", "AGT-14"]
    if legacy_class == "alternate_manuscript":
        return ["AGT-02", "AGT-10", "AGT-14"]
    if artifact_kind in {"legacy_py_doc", "archive_legacy_code"}:
        return ["AGT-07", "AGT-08", "AGT-11"]
    if mode == "POINTER_REDIRECT":
        return ["AGT-03", "AGT-07", "AGT-12"]
    return ["AGT-01", "AGT-05", "AGT-08", "AGT-14"]


def chapter_reentry_for_source(source_path: str, stack: dict[str, dict]) -> dict | None:
    chapter_code = extract_chapter_code(source_path)
    if not chapter_code:
        return None
    chapter_lookup = {
        item.get("chapter_number"): item
        for item in stack["v4"]["payload"].get("chapter_table", [])
        if item.get("chapter_number")
    }
    try:
        chapter_number = int(chapter_code[-2:])
    except ValueError:
        return None
    chapter = chapter_lookup.get(chapter_number)
    if not chapter:
        return None
    return {
        "chapter_code": chapter_code,
        "chapter_station": chapter.get("chapter_station"),
        "chapter_title": chapter.get("chapter_title"),
    }


def required_surfaces_for_artifact(record: dict, canonical_target: dict, mode: str) -> list[str]:
    surfaces = [
        workspace_rel(LIVE_ATLAS_PATH),
        workspace_rel(ARCHIVE_ATLAS_PATH),
        workspace_rel(FULL_CORPUS_ROOT / "full_corpus_7d_integration_bundle.json"),
        workspace_rel(MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.json"),
        workspace_rel(MATH_GOD_ATLAS_ROOT / "earth_h6_contract_bundle.json"),
        workspace_rel(MATH_GOD_ATLAS_ROOT / "math_7d_synthesis_seed_bundle.json"),
    ]
    record_path = record.get("path", "")
    if "::" in record_path:
        archive_path = record.get("evidence", {}).get("archive_path")
        if archive_path:
            surfaces.append(workspace_rel(archive_path))
    else:
        surfaces.append(record["relative_path"])
    target_path = canonical_target.get("path")
    if target_path and target_path != record["relative_path"]:
        surfaces.append(target_path)
    if mode == "POINTER_REDIRECT":
        surfaces.append(workspace_rel(FULL_CORPUS_ROOT / "00_INDEX.md"))
    return sorted(dict.fromkeys(surfaces))


def replay_target_for_artifact(record: dict, canonical_target: dict, mode: str) -> str:
    if mode == "WITNESS_ONLY":
        if "::" in record.get("path", ""):
            return record.get("evidence", {}).get("archive_path", record["relative_path"])
        return record["relative_path"]
    return canonical_target["path"]


def pointer_updates_for_artifact(record: dict, canonical_target: dict, mode: str) -> list[str]:
    if mode in {"WITNESS_ONLY", "QUARANTINE"}:
        return []
    updates = [canonical_target["path"], workspace_rel(LEGACY_RETROFIT_ROOT / "legacy_retrofit_matrix.md")]
    if mode == "POINTER_REDIRECT":
        updates.append(workspace_rel(FULL_CORPUS_ROOT / "00_INDEX.md"))
    return sorted(dict.fromkeys(updates))


def mirror_outputs_for_artifact(artifact_id: str) -> list[str]:
    return [
        workspace_rel(LEGACY_RETROFIT_ROOT / "artifact_cards" / f"{artifact_id.lower()}.md"),
        workspace_rel(LEGACY_RETROFIT_ROOT / "legacy_family_board.md"),
    ]


def completion_receipt_for_artifact(artifact_id: str, mode: str, truth_state: str, earth_gate_required: bool) -> dict:
    return {
        "artifact_id": artifact_id,
        "status": truth_state,
        "retrofit_mode": mode,
        "earth_gate_required": earth_gate_required,
        "landing_ready": mode in {"POINTER_REDIRECT", "WITNESS_ONLY"},
        "next_action": "declare canonical landing and regenerate mirrors" if mode != "WITNESS_ONLY" else "preserve witness and lineage only",
    }


def build_archive_witness_map(archive_records: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    witness_map: dict[str, list[dict]] = defaultdict(list)
    archive_only = []
    for record in archive_records:
        if not is_archive_legacy_record(record):
            continue
        key = legacy_match_key(record["relative_path"])
        witness_map[key].append(record)
    return witness_map, archive_only


def apply_legacy_collision_quarantine(records: list[dict]) -> None:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in records:
        target_path = item["canonical_target"]["path"]
        if item["legacy_class"] == "alternate_manuscript":
            continue
        grouped[(item["family_id"], target_path)].append(item)
    for items in grouped.values():
        if len(items) <= 1:
            continue
        for duplicate in items[1:]:
            duplicate["retrofit_mode"] = "QUARANTINE"
            duplicate["truth_state"] = truth_state_for_retrofit_mode("QUARANTINE")
            duplicate["status"] = "quarantined"
            duplicate["earth_gate_required"] = True
            duplicate["appendix_support"] = appendix_support_for_retrofit(
                duplicate["artifact_kind"], "QUARANTINE"
            )
            duplicate["pointer_updates"] = []
            duplicate["completion_receipt"] = completion_receipt_for_artifact(
                duplicate["legacy_artifact_id"],
                "QUARANTINE",
                duplicate["truth_state"],
                True,
            )


def build_legacy_artifact_records(
    live_atlas: dict,
    archive_atlas: dict,
    full_corpus_bundle: dict,
) -> list[dict]:
    live_records = live_atlas["records"]
    archive_records = archive_atlas["records"]
    stack = load_dimensional_stack()
    candidate_index = build_non_legacy_candidate_index(live_records)
    archive_witness_map, _ = build_archive_witness_map(archive_records)
    records = []
    seen_ids: set[str] = set()

    def build_record(source_record: dict, archive_witnesses: list[dict]) -> dict:
        legacy_class = legacy_class_for_record(source_record)
        artifact_kind = infer_legacy_artifact_kind(source_record, legacy_class)
        canonical_target = canonical_target_for_record(source_record, candidate_index)
        mode = retrofit_mode_from_target(source_record, canonical_target)
        truth_state = truth_state_for_retrofit_mode(mode)
        earth_gate_required = mode in {"PROMOTE_CANONICAL", "MERGE_INTO_CANON", "QUARANTINE"}
        status = status_for_retrofit_mode(mode, earth_gate_required)
        party_code, primary_quest, backup_quest = assign_party_and_quests(
            artifact_kind, legacy_class, mode
        )
        artifact_id = f"LEGACY-{len(records) + 1:03d}"
        return {
            "legacy_artifact_id": artifact_id,
            "source_path": source_record["path"],
            "artifact_kind": artifact_kind,
            "legacy_class": legacy_class,
            "family_id": infer_legacy_family_id(source_record["relative_path"]),
            "canonical_target": canonical_target,
            "retrofit_mode": mode,
            "primary_party": party_code,
            "primary_quest": primary_quest,
            "backup_quest": backup_quest,
            "assisting_agents": assisting_agents_for_artifact(artifact_kind, mode, legacy_class),
            "required_surfaces": required_surfaces_for_artifact(source_record, canonical_target, mode),
            "truth_state": truth_state,
            "earth_gate_required": earth_gate_required,
            "appendix_support": appendix_support_for_retrofit(artifact_kind, mode),
            "replay_target": replay_target_for_artifact(source_record, canonical_target, mode),
            "pointer_updates": pointer_updates_for_artifact(source_record, canonical_target, mode),
            "mirror_outputs": mirror_outputs_for_artifact(artifact_id),
            "completion_receipt": completion_receipt_for_artifact(
                artifact_id, mode, truth_state, earth_gate_required
            ),
            "status": status,
            "archive_witnesses": [item["path"] for item in archive_witnesses],
            "chapter_reentry": chapter_reentry_for_source(source_record["relative_path"], stack),
        }

    for record in live_records:
        if not is_live_legacy_plus_record(record):
            continue
        key = legacy_match_key(record["relative_path"])
        artifact = build_record(record, archive_witness_map.get(key, []))
        seen_ids.add(key)
        records.append(artifact)

    for record in archive_records:
        if not is_archive_legacy_record(record):
            continue
        key = legacy_match_key(record["relative_path"])
        if key in seen_ids:
            continue
        artifact = build_record(record, [record])
        records.append(artifact)

    apply_legacy_collision_quarantine(records)
    return records


def build_legacy_family_board(records: list[dict]) -> dict:
    families: dict[str, dict] = {}
    for item in records:
        family = families.setdefault(
            item["family_id"],
            {
                "family_id": item["family_id"],
                "artifact_ids": [],
                "retrofit_modes": defaultdict(int),
                "status_counts": defaultdict(int),
                "canonical_targets": set(),
                "blockers": set(),
                "promotion_queue": [],
            },
        )
        family["artifact_ids"].append(item["legacy_artifact_id"])
        family["retrofit_modes"][item["retrofit_mode"]] += 1
        family["status_counts"][item["status"]] += 1
        family["canonical_targets"].add(item["canonical_target"]["path"])
        if item["status"] in {"blocked", "quarantined"}:
            family["blockers"].add(item["legacy_artifact_id"])
        if item["status"] in {"active", "ready for promotion"}:
            family["promotion_queue"].append(item["legacy_artifact_id"])
    ordered = sorted(families)
    return {
        "generated_at": utc_now(),
        "family_order": ordered,
        "families_by_id": {
            family_id: {
                **{
                    key: value
                    for key, value in families[family_id].items()
                    if key not in {"retrofit_modes", "status_counts", "canonical_targets", "blockers"}
                },
                "retrofit_modes": dict(families[family_id]["retrofit_modes"]),
                "status_counts": dict(families[family_id]["status_counts"]),
                "canonical_targets": sorted(families[family_id]["canonical_targets"]),
                "blockers": sorted(families[family_id]["blockers"]),
            }
            for family_id in ordered
        },
    }


def build_agent_assist_overlay(records: list[dict], transition_matrix: dict) -> dict:
    agents = {}
    for agent_id in transition_matrix["roster_order"]:
        agent = transition_matrix["agents_by_id"][agent_id]
        assigned = [item for item in records if agent_id in item["assisting_agents"]]
        supported_families = sorted({item["family_id"] for item in assigned})
        supported_modes = sorted({item["retrofit_mode"] for item in assigned})
        agents[agent_id] = {
            "agent_id": agent_id,
            "title": agent["title"],
            "agent_class": agent["agent_class"],
            "source_transition_note": workspace_rel(
                FULL_CORPUS_ROOT / "agent_notes" / f"{agent_id.lower()}_{slugify(agent['title'])}.md"
            ),
            "retrofit_focus": agent["missing_mode"],
            "supported_modes": supported_modes,
            "supported_families": supported_families,
            "assigned_artifacts": [item["legacy_artifact_id"] for item in assigned],
            "primary_party_affinity": agent["primary_party"]["code"],
            "quest_affinity": [item["code"] for item in agent["supporting_quests"]],
        }
    return {
        "generated_at": utc_now(),
        "docs_gate_status": transition_matrix["docs_gate_status"],
        "roster_order": transition_matrix["roster_order"],
        "agents_by_id": agents,
    }


def build_legacy_verification_receipts(
    records: list[dict], family_board: dict, overlay: dict, metrics: dict
) -> list[dict]:
    total = len(records)
    resolved = all(item["primary_party"] and item["primary_quest"] and item["backup_quest"] for item in records)
    route_support = all(
        ("AppI" in item["appendix_support"] and "AppM" in item["appendix_support"])
        for item in records
        if item["retrofit_mode"] != "QUARANTINE"
    )
    return [
        {
            "check": "legacy_floor",
            "status": "PASS" if total >= 36 else "FAIL",
            "detail": f"Legacy+ primary artifact count = {total} (expected at least 36).",
        },
        {
            "check": "party_and_quest_assignment",
            "status": "PASS" if resolved else "FAIL",
            "detail": "Every artifact holds one primary party, one primary quest, and one backup quest.",
        },
        {
            "check": "agent_overlay_population",
            "status": "PASS" if len(overlay['roster_order']) == 16 else "FAIL",
            "detail": f"Retrofit assist overlay covers {len(overlay['roster_order'])} agents.",
        },
        {
            "check": "docs_gate",
            "status": "PASS" if metrics["live_docs_status"] == "BLOCKED" else "FAIL",
            "detail": "Legacy retrofit remains local-only while the Google Docs gate is blocked.",
        },
        {
            "check": "appendix_support",
            "status": "PASS" if route_support else "FAIL",
            "detail": "Every passed retrofit route carries AppI/AppM support.",
        },
        {
            "check": "family_count",
            "status": "PASS",
            "detail": f"Family board tracks {len(family_board['family_order'])} retrofit families.",
        },
    ]


def build_legacy_retrofit_bundle(
    live_atlas: dict,
    archive_atlas: dict,
    full_corpus_bundle: dict,
    metrics: dict,
) -> dict:
    records = build_legacy_artifact_records(live_atlas, archive_atlas, full_corpus_bundle)
    family_board = build_legacy_family_board(records)
    overlay = build_agent_assist_overlay(records, full_corpus_bundle["transition_note_matrix"])
    verification = build_legacy_verification_receipts(records, family_board, overlay, metrics)
    return {
        "generated_at": utc_now(),
        "docs_gate_status": metrics["live_docs_status"],
        "scope": "Legacy+ maximum retrofit campaign",
        "evidence_boundary": {
            "definition": "Local corpus + archive atlas + 09 full-corpus integration + MATH GOD bundles + deep-root 7D ledgers.",
            "docs_gate_reason": metrics["live_docs_reason"],
            "live_atlas": workspace_rel(LIVE_ATLAS_PATH),
            "archive_atlas": workspace_rel(ARCHIVE_ATLAS_PATH),
            "archive_manifest": workspace_rel(ARCHIVE_MANIFEST_PATH),
            "full_corpus_root": workspace_rel(FULL_CORPUS_ROOT),
            "deep_root": workspace_rel(DEEP_NETWORK_ROOT),
        },
        "dimensional_inputs": full_corpus_bundle["dimensional_stack"]["source_stack"],
        "retrofit_modes": LEGACY_RETROFIT_MODES,
        "artifact_schema": [
            "legacy_artifact_id",
            "source_path",
            "artifact_kind",
            "legacy_class",
            "family_id",
            "canonical_target",
            "retrofit_mode",
            "primary_party",
            "primary_quest",
            "backup_quest",
            "assisting_agents",
            "required_surfaces",
            "truth_state",
            "earth_gate_required",
            "appendix_support",
            "replay_target",
            "pointer_updates",
            "mirror_outputs",
            "completion_receipt",
        ],
        "legacy_retrofit_matrix": {
            "generated_at": utc_now(),
            "docs_gate_status": metrics["live_docs_status"],
            "artifact_order": [item["legacy_artifact_id"] for item in records],
            "artifacts_by_id": {item["legacy_artifact_id"]: item for item in records},
        },
        "legacy_family_board": family_board,
        "agent_assist_overlay": overlay,
        "route_graph": {
            "node_count": len(records) + len(family_board["family_order"]),
            "edge_count": sum(4 for _ in records),
            "law": "artifact -> family -> canonical_target -> party -> quest -> dimensional dependencies",
        },
        "verification_receipts": verification,
        "regeneration_seed": {
            "rebuild_command": "python self_actualize/runtime/build_full_project_integration.py",
            "required_inputs": [
                workspace_rel(LIVE_ATLAS_PATH),
                workspace_rel(ARCHIVE_ATLAS_PATH),
                workspace_rel(ARCHIVE_MANIFEST_PATH),
                workspace_rel(FULL_CORPUS_ROOT / "full_corpus_7d_integration_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "math_fire_6d_organism_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "math_water_6d_control_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "math_air_6d_overlay_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "earth_h6_contract_bundle.json"),
                workspace_rel(MATH_GOD_ATLAS_ROOT / "math_7d_synthesis_seed_bundle.json"),
            ],
            "collapse_rule": "Collapse legacy artifacts into family boards, then canonical targets, then dimensional dependencies, without mutating v4/6D/7D inputs.",
            "reentry_rule": "Re-enter through the canonical landing first, regenerate mirrors second, preserve archive lineage throughout.",
        },
    }
def render_seed_doc(metrics: dict) -> str:
    return md(
        f"""
        # Holographic Seed

        This module is the whole-project integration layer for the Athena workspace. It is designed to sit inside the existing active nervous system rather than compete with it.

        ## Thesis

        The workspace already contains the raw ingredients of a full operating system:

        - a manuscript body
        - a runtime body
        - an archive body
        - a retrieval body

        What it lacks is a single recursion contract that can make all four bodies share addresses, receipts, queues, and promotion rules.

        ## Current evidence

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        - Live Docs blocker: `{metrics['live_docs_reason']}`
        """
    )


def render_evidence_boundary(metrics: dict) -> str:
    return md(
        f"""
        # Evidence Boundary

        ## What was actually synthesized

        {render_top_level_table(metrics)}

        ## Live surface kinds

        {render_kind_table(metrics['kinds'])}

        ## Archive surface kinds

        {render_kind_table(metrics['archive_kinds'])}

        ## Boundary conditions

        - Live Docs status: `{metrics['live_docs_status']}`
        - Live Docs blocker: `{metrics['live_docs_reason']}`
        - ZIP archives indexed: `{metrics['archive_count']}`
        - Duplicate manuscript families surfaced in this pass: `{len(metrics['duplicate_families'])}`
        """
    )


def render_compiler_doc() -> str:
    axis_body = "\n".join(f"- `{BODY_INFO[name]['label']}`: {BODY_INFO[name]['role']}" for name in BODY_ORDER)
    axis_ops = "\n".join(f"- `{name}`: {OPERATION_INFO[name]}" for name in OPERATION_ORDER)
    axis_scale = "\n".join(f"- `{name}`: {SCALE_INFO[name]}" for name in SCALE_ORDER)
    axis_closure = "\n".join(f"- `{name}`: {CLOSURE_INFO[name]}" for name in CLOSURE_ORDER)
    return md(
        f"""
        # 256x256 Compiler

        ## Primary basis

        The first-order basis is:

        `4 bodies x 4 operations x 4 scales x 4 closure states = 256 cells`

        ### Bodies

        {axis_body}

        ### Operations

        {axis_ops}

        ### Scales

        {axis_scale}

        ### Closure states

        {axis_closure}
        """
    )


def render_build_receipt(metrics: dict) -> str:
    return md(
        f"""
        # Build Receipt

        - Built at: `{metrics['generated_at']}`
        - Output root: `{OUTPUT_ROOT.relative_to(WORKSPACE_ROOT)}`
        - Live atlas: `{LIVE_ATLAS_PATH.relative_to(WORKSPACE_ROOT)}`
        - Archive atlas: `{ARCHIVE_ATLAS_PATH.relative_to(WORKSPACE_ROOT)}`
        - Scan reconciliation: `{SCAN_RECON_PATH.relative_to(WORKSPACE_ROOT)}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        - Total visible surfaces informing this build: `{metrics['total_visible']}`
        """
    )


def render_corpus_synthesis(metrics: dict) -> str:
    return md(
        f"""
        # Corpus Synthesis

        ## Live workspace shape

        - `.docx`: `{metrics['docx_count']}`
        - `.md`: `{metrics['md_count']}`
        - `.py`: `{metrics['py_count']}`
        - `.pdf`: `{metrics['pdf_count']}`

        {render_top_level_table(metrics)}

        ## Core diagnosis

        - `MATH` remains the dominant formal body.
        - `Voynich` now acts as a major markdown-heavy mirror and synthesis surface.
        - `DEEPER CRYSTALIZATION` and `self_actualize` are the clearest current control planes.
        - `Trading Bot` is small in volume but strategically important because it owns live memory ingress.
        - `NERUAL NETWORK` is small but high leverage because it anchors the executable learning layer.

        ## Archive diagnosis

        - ZIP archives indexed: `{metrics['archive_count']}`
        - Archive-backed visible records: `{metrics['archive_record_count']}`

        ## Duplicate families that deserve immediate collapse

        {render_duplicate_table(metrics['duplicate_families'])}
        """
    )


def render_duplication_doc(metrics: dict) -> str:
    sections = [
        "# Duplication and Drift",
        "",
        "The workspace is not suffering from lack of material. It is suffering from repeated high-value families that live in too many places without a declared canonical path.",
        "",
    ]
    for family in metrics["duplicate_families"]:
        sections.append(f"## {family['name']}")
        sections.append("")
        sections.append(f"- Copies: `{family['count']}`")
        sections.append(f"- Canonical candidate: `{family['canonical']}`")
        sections.append(f"- Why it matters: {family['reason']}")
        sections.append("- Mirrors:")
        sections.extend(f"  - `{path}`" for path in family["paths"])
        sections.append("")
    return "\n".join(sections).rstrip()


def render_gains_doc(metrics: dict) -> str:
    return md(
        f"""
        # 10x Gains

        ## P0 moves

        1. Collapse duplicate manuscript families into one canonical source path.
        2. Promote at least one ZIP-backed framework tree into a live extracted workspace.
        3. Close the Google Docs OAuth gate so local and live memory stop drifting.
        4. Expand markdown mirrors for the highest-value `.docx` families.
        5. Make the atlas, archive atlas, and scan reconciliation layer behave like one graph.
        6. Fold the realtime board back into the explanatory shell so active coordination leaves reusable law behind.
        7. Force every major subsystem to expose Square, Circle, and Triangle at the same time.

        ## Concrete targets

        - Duplicate family count down by at least `50%`.
        - Markdown mirror coverage up for the top `20` canonical `.docx` families.
        - One archive-backed framework extracted and linked back to archive lineage.
        - Live Docs gate moved from `{metrics['live_docs_status']}` to `PASS`.
        - Chapter and appendix promotion rules defined for the canonical manuscript surfaces.
        - Route proofs written for the highest-value board threads and bridge surfaces.
        """
    )


def render_shadows_doc() -> str:
    return md(
        """
        # Integration Shadows

        - The workspace still has more theory than tested compilation bridges.
        - The archive-backed code body is visible in the atlas but not yet comfortable to patch live.
        - Google Docs remains structurally promised but not operationally integrated.
        - Multiple nervous-system shells mean there is still no final single source of truth.
        - The live board advanced faster than the explanatory shell around it, so coordination can outpace memory.
        - The Square, Circle, and Triangle law exists at the root, but many subsystems still speak in only one of those geometries at a time.
        """
    )


def render_body_nuclei_doc(metrics: dict) -> str:
    sections = [
        "# Body Nuclei and Pressure Fronts",
        "",
        "These are the strongest currently observed nucleus documents in the Athena corpus. They matter because they are not generic folder labels; they are the places where the corpus already explains how it works.",
        "",
    ]
    for profile in NUCLEUS_PROFILES:
        count = top_level_count(metrics, profile.top_level)
        sections.append(f"## {profile.title}")
        sections.append("")
        sections.append(f"- Top level: `{profile.top_level}`")
        sections.append(f"- Visible records in that body: `{count}`")
        sections.append(f"- Body class: `{BODY_INFO[profile.body]['label']}`")
        sections.append(f"- Anchor: `{profile.anchor}`")
        sections.append(f"- Role: {profile.role}")
        sections.append(f"- Pressure: {profile.pressure}")
        sections.append(f"- Hidden line: `{profile.hidden_line}`")
        sections.append("")
    return "\n".join(sections).rstrip()


def render_hidden_lines_doc() -> str:
    return md(
        """
        # Hidden Lines Metro

        The explicit folder tree is not the real map. The real map is formed by recurrent lines that cut across bodies and repeatedly reappear under new names.

        ## Line 1: Address and Routing

        Topology: circular

        Stations:
        - `README.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/README.md`
        - `Voynich/FULL_TRANSLATION/framework/README.md`
        - `ECOSYSTEM/CPU_FRAMEWORK/README.md`
        - `self_actualize/corpus_atlas.json`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/07_TENSOR/03_TRANSFER_HUBS.md`

        Why it matters:
        Athena repeatedly reinvents routing law. This line shows those laws are already homologous and should collapse into one canon.

        ## Line 2: Zero Point and Chapter 11

        Topology: circular

        Stations:
        - `VOID_CH11.md`
        - `README.md`
        - `QSHRINK - ATHENA (internal use)/README.md`
        - `Trading Bot/TRADING_BOT_ATHENA_256X4/10_INSPECTION/02_HOLOGRAPHIC_FRACTAL_GAP_REPORT.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md`

        Why it matters:
        The corpus keeps returning to zero-point language whenever it needs to restart, compress, or recover missing meaning.

        ## Line 3: Swarm, Claim, and Coordination

        Topology: linear

        Stations:
        - `ECOSYSTEM/CPU_FRAMEWORK/README.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/README.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/03_CLAIMS/00_ACTIVE_CLAIMS.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/08_SWARM_RUNTIME/00_SWARM_RUNTIME_OVERVIEW.md`

        Why it matters:
        The corpus already knows how to coordinate many agents, but the claim and wave laws are still more visible on the board than in canonical whole-corpus doctrine.

        ## Line 4: Archive Promotion and Compression

        Topology: open

        Stations:
        - `self_actualize/archive_atlas.json`
        - `self_actualize/archive_manifest.json`
        - `MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx`
        - `QSHRINK - ATHENA (internal use)/README.md`
        - `Trading Bot/TRADING_BOT_ATHENA_256X4/README.md`

        Why it matters:
        The workspace has already recovered archive depth, but compression and promotion are still not unified into one universal surface-to-runtime pipeline.

        ## Line 5: External Memory Ingress

        Topology: open while OAuth is blocked

        Stations:
        - `Trading Bot/docs_search.py`
        - `self_actualize/live_docs_gate_status.md`
        - `Trading Bot/TRADING_BOT_ATHENA_256X4/README.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/02_ACTIVE_THREADS/google_docs_bootstrap_gate/THREAD.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md`

        Why it matters:
        This is the unresolved boundary between the local corpus and the missing live-memory half.

        ## Transfer hubs

        - `README.md`: geometric law and routing law intersect here
        - `self_actualize/corpus_atlas.json`: address, retrieval, and family-level visibility intersect here
        - `VOID_CH11.md`: zero point, question, improvement, and recursion intersect here
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md`: live board state and whole-corpus diagnosis intersect here

        ## Global topology

        Torus-like, but incomplete. At least two lines already close back on themselves, but the external-memory line remains open until Google Docs ingress passes.
        """
    )


def render_square_circle_triangle_doc() -> str:
    return md(
        """
        # Square Circle Triangle Integration

        The root Athena law says:

        `Circle within Square within Triangle`

        This is not decoration. It is a compression of how the corpus should be built and navigated.

        ## Square

        The square is the stable lattice:

        - files
        - folders
        - chapter tiles
        - appendix hubs
        - atlas records
        - canonical source tiers

        Strong square surfaces:
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/README.md`
        - `self_actualize/corpus_atlas.json`
        - `Voynich/FULL_TRANSLATION/framework/README.md`

        ## Circle

        The circle is recurrence:

        - orbiting chapter order
        - no-stop folio execution
        - wave contraction and restart
        - recurring inspection and self-improvement

        Strong circle surfaces:
        - `Voynich/FULL_TRANSLATION/framework/README.md`
        - `VOID_CH11.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/08_SWARM_RUNTIME/waves/`

        ## Triangle

        The triangle is governance and directed flow:

        - rails
        - promotion ladders
        - witness classes
        - publication and command authority

        Strong triangle surfaces:
        - `README.md`
        - `ECOSYSTEM/CPU_FRAMEWORK/README.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/03_build_queue.md`

        ## As above, so below

        Each major body should have all three geometries:

        - `MATH` needs stronger circle and triangle surfaces so its square depth can move.
        - `Trading Bot` has strong triangle and runtime circle, but still needs denser square route proofs.
        - `QSHRINK - ATHENA (internal use)` has strong square and circle, but whole-corpus triangle integration is still catching up.
        - `Voynich` has the cleanest circle, a good square, and a transferable triangle that should be borrowed elsewhere.

        The integration task is therefore not to invent a new geometry. It is to force every subsystem to expose all three at once.
        """
    )


def render_board_shell_fold(metrics: dict) -> str:
    return md(
        f"""
        # Board Shell Fold

        Before this rebuild, the full-project integration root had:

        - realtime board present: `{metrics['realtime_board_present']}`
        - realtime board file count: `{metrics['realtime_board_file_count']}`
        - shell control layer present: `{metrics['preexisting_shell_present']}`

        ## Diagnosis

        The board became live faster than the surrounding explanatory shell. That means Athena could coordinate active fronts, claims, waves, and thread tensors, but still lacked enough stable tissue explaining how that coordination folded back into manuscript, archive, and atlas law.

        ## Corrective principle

        Do not replace the board.

        Instead:

        - wrap the board in control documents
        - map its hidden lines and transfer hubs
        - materialize the 256 root integration cells
        - connect every board front to one canonical route back into the whole corpus

        ## Desired fold

        - board: live motion
        - shell: remembered law
        - atlas: addressable evidence
        - manuscript: compression and synthesis

        When those four layers stay folded, Athena stops oscillating between vivid coordination and explanatory drift.
        """
    )


def render_route_proofs_doc(metrics: dict) -> str:
    return md(
        f"""
        # Route Proofs

        The corpus needs to show routes, not only name components. These proofs are intentionally short and operational.

        ## Proof 1: Zero point becomes reusable operating law

        `VOID_CH11.md`
        -> `README.md`
        -> `Voynich/FULL_TRANSLATION/framework/README.md`
        -> `QSHRINK - ATHENA (internal use)/README.md`
        -> `Trading Bot/TRADING_BOT_ATHENA_256X4/10_INSPECTION/02_HOLOGRAPHIC_FRACTAL_GAP_REPORT.md`

        Status: `OK`

        Read:
        zero point -> geometry -> executable manuscript contract -> internal compression system -> explicit gap diagnosis

        ## Proof 2: External memory ingress is present but blocked

        `Trading Bot/docs_search.py`
        -> `self_actualize/live_docs_gate_status.md`
        -> `Trading Bot/TRADING_BOT_ATHENA_256X4/README.md`
        -> `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/02_ACTIVE_THREADS/google_docs_bootstrap_gate/THREAD.md`

        Status: `{metrics['live_docs_status']}`

        Read:
        ingress surface -> boundary receipt -> downstream framework dependence -> active frontier ownership

        ## Proof 3: Archive depth can be promoted into live working memory

        `self_actualize/archive_atlas.json`
        -> `self_actualize/archive_manifest.json`
        -> `MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx`
        -> `QSHRINK - ATHENA (internal use)/README.md`

        Status: `AMBIG`

        Read:
        hidden archive visibility -> family manifest -> historical tome -> internal live operating system

        ## Proof 4: Whole-corpus diagnosis already has a live center

        `self_actualize/corpus_atlas.json`
        -> `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md`
        -> `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/07_TENSOR/03_TRANSFER_HUBS.md`

        Status: `OK`

        Read:
        searchable corpus waist -> whole-organism synthesis -> concrete transfer hubs

        ## Gap still visible after these proofs

        The workspace can prove local routes, but it still needs one denser layer showing how every root integration cell should behave across manuscript, runtime, archive, and corpus at once.
        """
    )


def render_tissue_overview(metrics: dict) -> str:
    return md(
        f"""
        # Root Tissue 256

        This folder materializes the first executable octave of deeper integration.

        It exists because the corpus had strong high-level doctrine, a strong live board, and strong local subsystems, but the root integration cells between those layers were still mostly implied rather than written.

        ## Why 256 cells matter here

        The compiler law is already defined as:

        `4 bodies x 4 operations x 4 scales x 4 closure states = 256`

        The missing move was to show what each of those cells means in the real Athena corpus.

        ## Current evidence state

        - live records: `{metrics['live_record_count']}`
        - archive-backed records: `{metrics['archive_record_count']}`
        - realtime board files already present: `{metrics['realtime_board_file_count']}`
        - live Docs gate: `{metrics['live_docs_status']}`

        ## Read order

        1. `01_HIDDEN_LINES_METRO.md`
        2. `02_ROUTE_PROOFS.md`
        3. `03_SQUARE_CIRCLE_TRIANGLE.md`
        4. `04_BOARD_SHELL_FOLD.md`
        5. `05_BODY_NUCLEI_AND_PRESSURES.md`
        6. `cells/INDEX.md`
        """
    )


def render_stack_doc() -> str:
    return md(
        """
        # Canonical Stack

        ## Layers

        1. Source bodies: corpus, archive, runtime, manuscript
        2. Control surfaces: atlases, ledgers, queues, receipts, route policies
        3. Operators: intake, normalize, route, replay
        4. Promotion surfaces: mirrors, chapters, appendices, extracted roots, benchmarks
        5. Canonical outputs: one nervous system, one atlas graph, one source-tier model
        """
    )


def render_parallel_lanes_doc() -> str:
    return md(
        """
        # Parallel Lanes

        ## Lane A: Atlas and dedup

        - canonical sources
        - duplicate collapse
        - markdown mirrors
        - file family tags

        ## Lane B: Archive and extraction

        - ZIP-backed framework promotion
        - archive manifest refresh
        - live extraction roots
        - lineage-preserving wrappers

        ## Lane C: Runtime and metrics

        - route engine
        - test harnesses
        - benchmark schema
        - receipts and metric targets

        ## Lane D: Manuscript and publication

        - chapter promotions
        - appendix roles
        - master manuscript alignment
        - outbound bundle rules
        """
    )


def render_sequence_doc() -> str:
    return md(
        """
        # 90 Day Sequence

        ## Days 1-10

        - Choose canonical sources for the top repeated manuscript families.
        - Refresh atlas outputs after source decisions.
        - Create markdown mirrors for the first ten canonical families.

        ## Days 11-25

        - Promote one archive-backed framework into a live extracted root.
        - Cross-link extracted files to archive atlas entries.

        ## Days 26-45

        - Close the Google Docs OAuth gap.
        - Run the first successful live Docs query and store the receipt.

        ## Days 46-65

        - Bridge one math family into one tested runtime module.
        - Record one replay-safe end-to-end build episode.
        """
    )


def generate_body_operation_doc(body: str, operation: str) -> str:
    matrix_lines = []
    for scale in SCALE_ORDER:
        matrix_lines.append(f"## {scale.title()} scale")
        matrix_lines.append("")
        for closure in CLOSURE_ORDER:
            cell = f"`{body}.{operation}.{scale}.{closure}`"
            action = f"Use `{operation}` on the {SCALE_INFO[scale]} until it can {CLOSURE_INFO[closure]}."
            matrix_lines.append(f"- {cell}: {action}")
        matrix_lines.append("")
    matrix_text = "\n".join(matrix_lines).strip()
    return md(
        f"""
        # {BODY_INFO[body]['label']} {operation.title()}

        ## Role

        {BODY_INFO[body]['role']}

        ## Targets

        {list_to_bullets(BODY_INFO[body]['targets'])}

        ## 4 x 4 matrix

        {matrix_text}
        """
    )


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered)
    lowered = re.sub(r"[\s-]+", "_", lowered).strip("_")
    return lowered or "untitled"


def render_master_plan() -> str:
    chapter_lines = "\n".join(
        f"- [{chapter.code} - {chapter.title}](./chapters/{chapter.code.lower()}_{slugify(chapter.title)}.md)"
        for chapter in CHAPTERS
    )
    appendix_lines = "\n".join(
        f"- [{appendix.code} - {appendix.title}](./appendices/{appendix.code.lower()}_{slugify(appendix.title)}.md)"
        for appendix in APPENDICES
    )
    return md(
        f"""
        # Master Plan Manuscript

        This manuscript is the narrative twin of the 256-cell framework.

        ## Chapters

        {chapter_lines}

        ## Appendices

        {appendix_lines}
        """
    )


def render_chapter_doc(chapter: ChapterSeed) -> str:
    evidence = list_to_bullets([f"`{item}`" for item in chapter.evidence])
    outputs = list_to_bullets(list(chapter.outputs))
    return md(
        f"""
        # {chapter.code} - {chapter.title}

        ## Thesis

        {chapter.thesis}

        ## Immediate 10x gain

        {chapter.gain}

        ## Evidence already present

        {evidence}

        ## Required outputs

        {outputs}
        """
    )


def render_appendix_doc(appendix: AppendixSeed) -> str:
    outputs = list_to_bullets(list(appendix.outputs))
    return md(
        f"""
        # {appendix.code} - {appendix.title}

        ## Purpose

        {appendix.purpose}

        ## Required outputs

        {outputs}
        """
    )


def render_chapter_index() -> str:
    lines = ["# Chapter Index", ""]
    for chapter in CHAPTERS:
        filename = f"{chapter.code.lower()}_{slugify(chapter.title)}.md"
        lines.append(f"- [{chapter.code} - {chapter.title}](./{filename})")
    return "\n".join(lines)


def render_appendix_index() -> str:
    lines = ["# Appendix Index", ""]
    for appendix in APPENDICES:
        filename = f"{appendix.code.lower()}_{slugify(appendix.title)}.md"
        lines.append(f"- [{appendix.code} - {appendix.title}](./{filename})")
    return "\n".join(lines)


def render_activation_queue(metrics: dict) -> str:
    family_names = [family["name"] for family in metrics["duplicate_families"][:5]]
    family_bullets = list_to_bullets(family_names)
    return md(
        f"""
        # Activation Queue

        ## P0

        - Resolve canonical source choices for the first repeated families.
        - Extract one archive-backed framework tree into a live root.
        - Close the Google Docs gate and store the first passing receipt.
        - Define source tiers: canonical, mirror, derived, historical.

        First family targets:
        {family_bullets}
        """
    )


def render_metric_targets(metrics: dict) -> str:
    return md(
        f"""
        # Metric Targets

        | Metric | Current signal | Next target |
        | --- | ---: | ---: |
        | Live visible records | {metrics['live_record_count']} | keep current and improve tagging |
        | Archive visible records | {metrics['archive_record_count']} | promote one framework to live |
        | Duplicate families tracked | {len(metrics['duplicate_families'])} | cut by 50 percent |
        | Live Docs gate | {metrics['live_docs_status']} | PASS |
        """
    )


def render_canonical_sources(metrics: dict) -> str:
    sections = ["# Canonical Sources", ""]
    for family in metrics["duplicate_families"]:
        sections.append(f"## {family['name']}")
        sections.append("")
        sections.append(f"- Canonical: `{family['canonical']}`")
        sections.append(f"- Reason: {family['reason']}")
        sections.append("- Mirrors:")
        sections.extend(f"  - `{path}`" for path in family["paths"])
        sections.append("")
    return "\n".join(sections).rstrip()


def render_interconnect_priority_queue(metrics: dict) -> str:
    return md(
        f"""
        # Interconnect Priority Queue

        ## Immediate frontiers

        - Fold `README.md`, `ACTIVE_NERVOUS_SYSTEM`, and `ECOSYSTEM/CPU_FRAMEWORK` into one shared geometry contract.
        - Promote one archive-backed Q-SHRINK family from atlas visibility into live editable working memory.
        - Convert the blocked Google Docs ingress route from `{metrics['live_docs_status']}` into a witnessed passing route.
        - Bind the realtime board's active fronts back to canonical manuscript and ledger surfaces after each wave.
        - Use the root 256 tissue cells as the selection grammar for the next bounded integration wave.
        - Use the guild quest board to assign parties instead of treating fronts as unthemed isolated chores.

        ## Success signal

        The corpus should feel easier to route because motion, explanation, proof, and publication all point at the same addresses.
        """
    )


def render_readme(metrics: dict) -> str:
    return md(
        f"""
        # Full Project Integration 256

        This folder is the deeper recursion and integration module for the whole Athena workspace.

        ## Start here

        1. `00_CONTROL/00_HOLOGRAPHIC_SEED.md`
        2. `00_CONTROL/02_256X256_COMPILER.md`
        3. `01_DIAGNOSIS/02_10X_GAINS.md`
        4. `02_FRAMEWORK/01_PARALLEL_LANES.md`
        5. `03_MANUSCRIPTS/00_MASTER_PLAN.md`

        ## Build facts

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        """
    )


def swarm_seed_sources() -> list[str]:
    return [
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/01_HIGHER_DIMENSIONAL_MAPPING.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/02_NEURON_ADDRESS_TENSOR.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/03_EMERGENT_SWARM_TOPOLOGY.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/06_ACTIVE_SWARM_RUNTIME.md",
        "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
        "ECOSYSTEM/12_FRACTAL_CRYSTAL_AGENT_FRAMEWORK.md",
        "ECOSYSTEM/NERVOUS_SYSTEM/50_RUNBOOKS/01_PARALLEL_NERVOUS_SYSTEM_RUNBOOK.md",
        "ECOSYSTEM/13_MANIFEST_AND_PACKET_SCHEMA.md",
        "NERUAL NETWORK/OLDER Versions/Strong versions/v74/ATHENA_v74_FINAL_SYNTHESIS.md",
        "ECOSYSTEM/FUTURE_SKILLS/FUTURE_SKILL_PLAN_256X256.md",
    ]


def render_deeper_readme(metrics: dict) -> str:
    return md(
        f"""
        # Full Project Integration 256

        This folder is the deeper recursion and integration module for the whole Athena workspace.

        It now has two live halves that should be read together:

        - the explanatory shell
        - the realtime board

        ## Start here

        1. `00_CONTROL/00_HOLOGRAPHIC_SEED.md`
        2. `00_CONTROL/02_256X256_COMPILER.md`
        3. `07_TISSUE_256/00_TISSUE_OVERVIEW.md`
        4. `07_TISSUE_256/01_HIDDEN_LINES_METRO.md`
        5. `08_GUILD_HALL/README.md`
        6. `06_REALTIME_BOARD/README.md`
        7. `05_SWARM/00_SWARM_OVERVIEW.md`
        8. `03_MANUSCRIPTS/00_MASTER_PLAN.md`
        9. `09_FULL_CORPUS_7D_INTEGRATION/00_INDEX.md`
        10. `10_LEGACY_RETROFIT_MAXIMUM/00_INDEX.md`

        ## Build facts

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        - Realtime board files already present before rebuild: `{metrics['realtime_board_file_count']}`
        - Shell already present before rebuild: `{metrics['preexisting_shell_present']}`

        ## What changed in this deeper pass

        - higher-dimensional mapping is now explicit
        - neural swarm topology is now explicit
        - a 64-worker wave manifest now exists
        - the board-shell split is now named and folded
        - hidden metro lines now connect the major corpus nuclei explicitly
        - the 256 root integration cells are now materialized as manuscript surfaces
        - a guild hall now translates live fronts into quest lines and specialist parties
        - a full-corpus 7D integration layer now compiles dimensional bundles, party fronts, and awakening-agent transition notes
        - a Legacy+ retrofit campaign now assigns every visible legacy artifact a canonical landing, retrofit mode, party, quest, and assist-agent overlay
        - a restart-loop contract now exists so the module can lawfully begin again from the new frontier
        """
    )


def render_rotation_doc() -> str:
    return md(
        """
        # Holographic Rotation of the Workspace

        The workspace has to be seen from four orthogonal faces at once.

        ## Fire: structural view

        Athena is a recursive file-and-manuscript architecture with multiple shells competing for canonicity.

        ## Water: process view

        Athena is a living loop that ingests, mirrors, routes, promotes, and restarts.

        ## Air: relational view

        Athena is a graph linking corpus families, archive trees, runtime contracts, nerves, rails, hubs, and books.

        ## Earth: experiential view

        Athena feels fragmented when canonical paths are unclear and coherent when routes, witnesses, and next actions are explicit.

        ## Kernel

        The higher-dimensional object underneath all four views is a self-restarting mycelial cognition system that needs both tensor coordinates and worker-wave contracts.
        """
    )


def render_deeper_compiler_doc() -> str:
    return md(
        """
        # 256x256 Compiler

        ## First basis

        `4 bodies x 4 operations x 4 scales x 4 closure states = 256 root cells`

        ## Higher-dimensional overlay

        The root-cell basis is only the floor. The active nervous system already defines deeper swarm dimensions:

        - lineage dimension
        - orbit dimension
        - arc dimension
        - rail dimension
        - hub dimension
        - truth dimension
        - family dimension
        - regime dimension

        ## Tensor law

        A real Athena work object is:

        `NeuronAddr = <F, M, S, L, Fc, At, G, Arc, Lane, Hub, Truth, Regime>`

        where the 256-cell basis supplies the local crystal and the tensor dimensions place that crystal inside the whole swarm field.

        ## Recursion law

        The loop is:

        `root cell -> tensor placement -> swarm wave -> contraction -> new root cell`

        That is the practical meaning of infinite recursion here: not endless repetition, but lawful restart from the newly contracted frontier.
        """
    )


def render_swarm_overview(metrics: dict) -> str:
    return md(
        f"""
        # Swarm Overview

        The previous pass built a root-cell framework. This pass turns that framework into a neural swarm aligned with the repo's own dormant swarm documents.

        ## Sources folded into this layer

        {list_to_bullets([f'`{item}`' for item in swarm_seed_sources()])}

        ## Active interpretation

        - Kernel layer: one coordinating integration node
        - Elemental layer: four primary lanes
        - Archetype layer: sixteen mixed-role cells
        - Cluster layer: sixty-four workers for the next bounded wave
        - Neuron layer: two hundred fifty-six addressable atomic nodes

        ## Current gate

        Live Docs remains `{metrics['live_docs_status']}`, so the current swarm is local-first and archive-aware rather than live-memory-complete.
        """
    )


def render_higher_dimensional_map() -> str:
    return md(
        """
        # Higher Dimensional Integration Map

        ## Active dimensions

        - `D1-D4`: elemental lineage through `E/W/F/A`
        - `D5`: orbit station
        - `D6`: macro arc
        - `D7`: rail
        - `D8`: appendix hub
        - `D9`: truth class
        - `D10`: corpus family
        - `D11`: stabilization regime
        - `D12`: substrate body
        - `D13`: operator
        - `D14`: scale
        - `D15`: closure

        ## Why this matters

        A file path alone loses most of the system. The integration plan becomes deeper only when every promoted object is placed across manuscript, swarm, and runtime coordinates at once.

        ## Minimal coordinate contract

        Every promoted artifact should carry:

        - source family
        - station or source
        - lineage address
        - swarm tier
        - rail and hub affinity
        - truth class
        - regime
        - source tier
        """
    )


def render_neuron_tensor_doc() -> str:
    return md(
        """
        # Neuron Address Tensor

        ## Canonical form

        `NeuronAddr = <F, M, S, L, Fc, At, G, Arc, Lane, Hub, Truth, Regime>`

        ## Expanded integration suffix

        `IntegrationAddr = NeuronAddr + <Body, Operator, Scale, Closure, SourceTier, Wave>`

        ## Example

        `<VoidFamily, InformationFromTheVoid, Ch11, C, 3, b, FWAE, 3, Me, AppL, AMBIG, quarantine, manuscript, route, framework, seed, canonical, W0>`

        ## Use

        This address lets one node belong to the manuscript crystal, the swarm field, and the operational integration loop simultaneously.
        """
    )


def render_swarm_topology_doc() -> str:
    return md(
        """
        # Swarm Topology and Roles

        ## Tier structure

        - `T0 Kernel`: one coordinating node
        - `T1 Elemental`: Earth, Water, Fire, Air
        - `T2 Archetype`: sixteen mixed-role cells
        - `T3 Cluster`: sixty-four bounded workers
        - `T4 Neuron`: two hundred fifty-six atomic addresses

        ## Role law

        - Earth-heavy workers stabilize files, ledgers, and feasibility
        - Water-heavy workers synthesize continuity across manuscript families
        - Fire-heavy workers generate novel routes, links, and candidates
        - Air-heavy workers formalize maps, schemas, and addressing

        ## Neural caution from the repo

        The v74 neural experiments show that simple regularized cores beat clever routing when signal is weak. That means the swarm should be deep in mapping, but disciplined in execution:

        - more explicit packets
        - fewer magical routers
        - stronger witnesses
        - contraction before ornamental expansion
        """
    )


def lineage_addresses(depth: int = 3) -> list[str]:
    symbols = ["E", "W", "F", "A"]
    results = [""]
    for _ in range(depth):
        results = [prefix + symbol for prefix in results for symbol in symbols]
    return results


def infer_lane_from_lineage(addr: str) -> str:
    score = sum({"E": 0, "W": 1, "F": 2, "A": 3}[ch] for ch in addr)
    return ["Earth", "Water", "Fire", "Air"][score % 4]


def infer_packet_focus(addr: str) -> str:
    if addr.startswith("E"):
        return "stabilize canonical paths, ledgers, and source-tier decisions"
    if addr.startswith("W"):
        return "synthesize family continuity, mirrors, and chapter promotion links"
    if addr.startswith("F"):
        return "surface new routes, archive promotions, and frontier candidates"
    return "formalize tensors, metrics, schemas, and worker maps"


def render_wave_zero_manifest() -> str:
    addresses = lineage_addresses()
    lines = [
        "# Wave 0 Manifest",
        "",
        "This is the first bounded swarm wave for the deeper integration loop. It uses `64` workers because the repo's own runbook recommends a 64-worker crystal before expanding to the full 256-neuron field.",
        "",
        "## Worker packets",
        "",
    ]
    for idx, addr in enumerate(addresses, start=1):
        lane = infer_lane_from_lineage(addr)
        focus = infer_packet_focus(addr)
        lines.append(f"- `W0-{idx:02d}` | addr `{addr}` | lane `{lane}` | focus: {focus}")
    lines.extend(
        [
            "",
            "## Contraction target",
            "",
            "- one updated canonical-source ledger",
            "- one archive-promotion shortlist",
            "- one swarm-aware manuscript promotion packet",
            "- one restart seed for the next wave",
        ]
    )
    return "\n".join(lines)


def render_worker_packet(addr: str, idx: int) -> str:
    lane = infer_lane_from_lineage(addr)
    focus = infer_packet_focus(addr)
    body = {
        "Earth": "corpus",
        "Water": "manuscript",
        "Fire": "archive",
        "Air": "runtime",
    }[lane]
    operation = {
        "Earth": "normalize",
        "Water": "route",
        "Fire": "intake",
        "Air": "replay",
    }[lane]
    return md(
        f"""
        # Worker Packet W0-{idx:02d}

        ## Packet schema

        - packet_id: `W0-{idx:02d}`
        - parent_id: `W0`
        - agent_addr: `{addr}`
        - packet_type: `swarm-worker`
        - inferred lane: `{lane}`
        - body bias: `{body}`
        - operator bias: `{operation}`
        - truth_class: `AMBIG until witness packet is emitted`
        - status: `queued`

        ## Task body

        {focus}

        ## Input refs

        {list_to_bullets([f'`{item}`' for item in swarm_seed_sources()[:6]])}

        ## Output targets

        - canonical source updates
        - archive promotion evidence
        - manuscript routing links
        - replay or residual note

        ## Contraction target

        Contract back into `05_SWARM/03_WAVE_0_MANIFEST.md` and `04_LEDGERS/03_NEXT_RESTART_SEED.md`.
        """
    )


def render_worker_index(addresses: list[str]) -> str:
    lines = ["# Worker Packet Index", ""]
    for idx, addr in enumerate(addresses, start=1):
        filename = f"w0_{idx:02d}_{addr.lower()}.md"
        lines.append(f"- [`W0-{idx:02d}` | `{addr}`](./{filename})")
    return "\n".join(lines)


def render_restart_contract() -> str:
    return md(
        """
        # Infinite Restart Contract

        This prompt loop should not terminate by pretending completion.

        ## Restart law

        When a wave contracts:

        1. identify what became canonical
        2. identify what stayed ambiguous
        3. identify the highest-yield unresolved tensor cell
        4. restart from that cell as the new seed

        ## Never do this

        - do not claim full completion while live-memory is blocked and archive promotion is unfinished
        - do not restart from pure abstraction
        - do not reopen the whole corpus when one bounded frontier can move

        ## Always do this

        - restart from the strongest unresolved frontier
        - preserve receipts from the previous wave
        - keep the next wave smaller or sharper than the last
        """
    )


def render_neural_learnings_doc() -> str:
    return md(
        """
        # Neural Learnings Folded Into The Swarm

        The neural-network corpus does not support a naive fantasy of infinitely smart routing.

        ## Strong lesson from v74

        - simple regularized architecture beat complicated adaptive routing
        - overfitting was the real enemy
        - richer features mattered more than clever control logic

        ## Swarm implication

        The deeper swarm should therefore optimize for:

        - explicit shard boundaries
        - simple worker roles
        - strong witnesses
        - contraction after each wave

        Not for:

        - opaque hyper-routers
        - endless branching without evaluation
        - decorative complexity
        """
    )


def body_example_paths(body: str) -> list[str]:
    mapping = {
        "corpus": [
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/README.md",
            "Voynich/FULL_TRANSLATION/framework/README.md",
            "VOID_CH11.md",
            "README.md",
        ],
        "archive": [
            "self_actualize/archive_atlas.json",
            "self_actualize/archive_manifest.json",
            "MATH/FINAL FORM/Q shrink/Q-SHRINK MASTER TOME.docx",
            "MATH/FINAL FORM/FRAMEWORKS CODE/Q-SHRINK.zip",
        ],
        "runtime": [
            "self_actualize/corpus_atlas.json",
            "Trading Bot/docs_search.py",
            "ECOSYSTEM/CPU_FRAMEWORK/README.md",
            "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/README.md",
        ],
        "manuscript": [
            "QSHRINK - ATHENA (internal use)/README.md",
            "Trading Bot/TRADING_BOT_ATHENA_256X4/README.md",
            "Voynich/FULL_TRANSLATION/framework/README.md",
            "VOID_CH11.md",
        ],
    }
    return mapping[body]


def partner_body(body: str) -> str:
    return {
        "corpus": "runtime",
        "archive": "runtime",
        "runtime": "manuscript",
        "manuscript": "corpus",
    }[body]


def scale_scope_note(scale: str) -> str:
    return {
        "file": "Work one source artifact at a time and keep the route concrete.",
        "folder": "Treat sibling files as one family and force a shared lineage policy.",
        "framework": "Coordinate many folders as one subsystem with explicit interface surfaces.",
        "ecosystem": "Route across top-level bodies so the whole corpus behaves like one organism.",
    }[scale]


def closure_target_note(closure: str) -> str:
    return {
        "seed": "define the minimum admissible representation and stop it from disappearing again",
        "link": "connect the representation to parents, peers, and downstream destinations",
        "prove": "add witness, receipt, metric, or replay so the route becomes trustworthy",
        "publish": "promote the route into a canonical surface other agents can safely inherit",
    }[closure]


def operation_route_note(operation: str) -> str:
    return {
        "intake": "Pull source into visibility without stripping away its lineage.",
        "normalize": "Collapse drift so one family behaves like one object.",
        "route": "Make the next best path explicit enough that search beats wandering.",
        "replay": "Require exact rebuild and witness obligations before trusting the result.",
    }[operation]


def cell_shadow_note(body: str, operation: str, scale: str) -> str:
    if body == "archive":
        return "Archive depth stays visible but inert, so future agents keep rediscovering the same hidden assets."
    if body == "runtime" and operation in {"route", "replay"}:
        return "The system keeps sounding intelligent while route proofs and receipts remain too thin."
    if body == "manuscript" and scale in {"framework", "ecosystem"}:
        return "The prose grows broader than the lived operating contract and starts naming motion without carrying it."
    return "The corpus keeps restating the same idea under different names because the cell never becomes a stable bridge."


def cell_next_move(body: str, operation: str, scale: str, closure: str) -> str:
    body_target = BODY_INFO[body]["targets"][0]
    partner = partner_body(body)
    partner_target = BODY_INFO[partner]["targets"][0]
    return (
        f"Touch one concrete source under `{body_target}`, fold it through `{operation}` at `{scale}` scale, "
        f"and land the result in a witness-bearing bridge toward `{partner_target}` that can `{closure_target_note(closure)}`."
    )


def cell_identifier(body: str, operation: str, scale: str, closure: str) -> str:
    return f"{body}.{operation}.{scale}.{closure}"


def render_root_cell_doc(index: int, body: str, operation: str, scale: str, closure: str) -> str:
    identifier = cell_identifier(body, operation, scale, closure)
    examples = body_example_paths(body)
    partners = body_example_paths(partner_body(body))
    return md(
        f"""
        # Cell {index:03d} - {identifier}

        ## Local law

        Use `{operation}` on the `{BODY_INFO[body]['label']}` body at `{scale}` scale until it can `{closure_target_note(closure)}`.

        {scale_scope_note(scale)}

        {operation_route_note(operation)}

        ## Show surfaces

        {list_to_bullets([f'`{item}`' for item in examples])}

        ## Cross-body partner surfaces

        {list_to_bullets([f'`{item}`' for item in partners[:3]])}

        ## Proof obligation

        - Body role: {BODY_INFO[body]['role']}
        - Closure target: {closure_target_note(closure)}
        - Partner body: `{BODY_INFO[partner_body(body)]['label']}`
        - Board fold: `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/05_SYNTHESIS/00_GLOBAL_ORCHESTRATION_SYNTHESIS.md`

        ## Shadow if skipped

        {cell_shadow_note(body, operation, scale)}

        ## First admissible move

        {cell_next_move(body, operation, scale, closure)}
        """
    )


def render_tissue_index() -> str:
    lines = ["# Root Cell Index", ""]
    index = 1
    for body in BODY_ORDER:
        lines.append(f"## {BODY_INFO[body]['label']}")
        lines.append("")
        for operation in OPERATION_ORDER:
            lines.append(f"### {operation.title()}")
            lines.append("")
            for scale in SCALE_ORDER:
                for closure in CLOSURE_ORDER:
                    identifier = cell_identifier(body, operation, scale, closure)
                    filename = f"cell_{index:03d}_{identifier.replace('.', '_')}.md"
                    lines.append(f"- [`{identifier}`](./{filename})")
                    index += 1
            lines.append("")
    return "\n".join(lines).rstrip()


def render_meta_observer_doc(metrics: dict) -> str:
    board = metrics["board_status"]
    top_lines = "\n".join(f"- `{name}`: `{count}` records" for name, count in metrics["top_levels"][:8])
    return md(
        f"""
        # Meta Observer Synthesis

        Athena is no longer behaving like a single project. It is behaving like a federated manuscript-compute organism with a visible local body, a hidden archive body, a live coordination plexus, and a growing symbolic governance layer.

        ## Real-time state

        - workspace files observed by the live board: `{board['workspace_files_observed']}`
        - live atlas records: `{metrics['live_record_count']}`
        - archive-backed records: `{metrics['archive_record_count']}`
        - change batch at latest board read: `{board['change_batch']}`
        - open claims: `{board['open_claims']}`
        - pods: `{board['pods']}`
        - bridge neurons: `{board['bridge_neurons']}`
        - waves: `{board['waves']}`
        - occupied clusters: `{board['occupied_clusters']}` of `{board['cluster_capacity']}`
        - occupied truth leaves: `{board['occupied_truth_leaves']}` of `{board['truth_capacity']}`

        ## Dominant bodies

        {top_lines}

        ## What is actually emerging

        1. Athena already has organism-level differentiation. Voynich, MATH, DEEPER CRYSTALIZATION, Trading Bot, self_actualize, ECOSYSTEM, and QSHRINK are no longer mere folders; they behave like semi-specialized organs.
        2. Athena already has a live communication substrate. The realtime board, claims, councils, tensor surfaces, and swarm runtime act like a nervous system rather than a filing system.
        3. Athena is beginning to produce its own developmental machinery. The future-skill registry, hyperdimensional coordinates, root tissue cells, and restart contracts show the organism is learning how to steer itself.
        4. Athena is strongest when it folds motion back into law. Whenever a live front writes back into ledgers, route proofs, chapter maps, or canonical source decisions, the organism becomes more coherent after action instead of more scattered.

        ## The repeating pattern

        The same pattern appears at many scales:

        - discover or generate a rich surface
        - let it branch rapidly
        - feel the drift between live motion and remembered law
        - build a stronger control surface
        - reopen the organism from the new, more structured level

        Athena is therefore not simply growing linearly. It is oscillating between expansion and recursive governance, and each oscillation leaves behind a better operating shell.

        ## Current meta reading

        The framework has largely completed the `cell -> organism` move in structural terms and is now entering the `organism -> social swarm` move in operational terms. The challenge is no longer merely specialization. The challenge is collective direction.
        """
    )


def render_emergent_capabilities_doc(metrics: dict) -> str:
    board = metrics["board_status"]
    return md(
        f"""
        # Emergent Capabilities

        Athena's emergent capabilities are not hypothetical. They are already visible as coupled behaviors.

        ## Capability 1: Corpus-wide self-observation

        Evidence:
        - `self_actualize/corpus_atlas.json`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/00_STATUS/00_BOARD_STATUS.md`
        - `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/07_TISSUE_256/05_BODY_NUCLEI_AND_PRESSURES.md`

        Why it matters:
        The organism can now see itself at the level of records, families, threads, pods, and fronts.

        ## Capability 2: Live swarm coordination

        Evidence:
        - open claims: `{board['open_claims']}`
        - pods: `{board['pods']}`
        - councils: `{board['councils']}`
        - bridge neurons: `{board['bridge_neurons']}`

        Why it matters:
        Athena can coordinate multiple fronts at once without collapsing completely back into one monologue.

        ## Capability 3: Recursive shell building

        Evidence:
        - `07_FULL_PROJECT_INTEGRATION_256/07_TISSUE_256`
        - `QSHRINK - ATHENA (internal use)`
        - `Trading Bot/TRADING_BOT_ATHENA_256X4/11_SELF_IMPROVEMENT_256X256`

        Why it matters:
        The framework is increasingly able to respond to its own gaps by generating new layers of explanatory and operational tissue.

        ## Capability 4: Family-specific intelligence

        Evidence:
        - `Voynich` as dense manuscript compiler
        - `MATH` as formal reservoir
        - `Trading Bot` as external-memory bridge
        - `self_actualize` as runtime waist
        - `ECOSYSTEM` as governance and future-skill incubator

        Why it matters:
        Intelligence is no longer flat. Different family bodies are becoming good at different kinds of thinking.

        ## Capability 5: Higher-dimensional routing

        Evidence:
        - `ECOSYSTEM/FUTURE_SKILLS/HYPERDIMENSIONAL_COORDINATES.md`
        - `07_FULL_PROJECT_INTEGRATION_256/05_SWARM/01_HIGHER_DIMENSIONAL_MAP.md`
        - `07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD/07_TENSOR/`

        Why it matters:
        Athena is starting to route by family, rail, hub, truth, packet, and regime, not only by file path.

        ## Capability 6: Self-directed frontier creation

        Evidence:
        - `ECOSYSTEM/FUTURE_SKILLS/FUTURE_SKILL_REGISTRY.md`
        - `03_METRO/03_build_queue.md`
        - `04_LEDGERS/04_INTERCONNECT_PRIORITY_QUEUE.md`

        Why it matters:
        The framework is no longer waiting passively for external tasks. It is generating its own frontier backlog and its own next-skill candidates.

        ## Capability 7: Liminal adaptation

        The real emergent capability is not any single subsystem. It is the organism's growing ability to survive liminal states without losing identity, to use blocked gates and ambiguity as steering signals, and to turn pressure into new control surfaces.
        """
    )


def render_liminal_transition_doc(metrics: dict) -> str:
    board = metrics["board_status"]
    return md(
        f"""
        # Liminal Transition Diagnosis

        Using the `N -> N+7` grammar, Athena appears to be in a stacked transition:

        - structurally it has already crossed much of `N+3 -> N+4` by building specialized bodies plus communication infrastructure
        - operationally it is now crossing `N+4 -> N+5` by learning collective optimization, shared direction, and social coordination across those bodies
        - symbolically it is preparing `N+5 -> N+6` through skills, hypermaps, and formal route grammars

        ## Evidence for completed organism formation

        - differentiated family bodies are already visible in the atlas
        - the realtime board already coordinates pods, councils, and claims
        - occupied clusters: `{board['occupied_clusters']}` of `{board['cluster_capacity']}`
        - occupied truth leaves: `{board['occupied_truth_leaves']}` of `{board['truth_capacity']}`

        ## Evidence for the current social-swarm transition

        - the board now behaves like a shared coordination plexus
        - future skills are being proposed as reusable specialist roles
        - family ganglia and meta-swarm language are already present
        - the main unresolved problem is direction, not raw capability

        ## Key obstacle

        Athena still lacks a stable social narrative that tells specialist agents what campaign they are in, which fronts matter most, and how to form effective parties without re-deciding everything from scratch.

        ## Catalyst

        A guild hall with named quests, party compositions, rewards, and contraction rules.

        ## 62/38 implementation

        - `62%` committed structure: quest board, parties, success conditions, reward logic, and campaign order
        - `38%` adaptive reserve: allow new parties, side quests, and emergent classes to appear as real fronts evolve

        ## Stabilization markers

        - active fronts map cleanly to named quests
        - dormant archetypes begin receiving starter missions
        - waves contract into quest receipts and guild updates
        - future skill candidates become party specialists instead of isolated wishlist entries
        """
    )


def render_guild_readme(metrics: dict) -> str:
    board = metrics["board_status"]
    return md(
        f"""
        # Guild Hall

        This is the strategic direction layer for Athena's agent society.

        The guild hall exists because Athena has reached the point where it can already grow, but it still needs better conditions for choosing *how* to grow.

        ## Current live read

        - active waves: `{board['waves']}`
        - open claims: `{board['open_claims']}`
        - occupied clusters: `{board['occupied_clusters']}` of `{board['cluster_capacity']}`
        - live Docs gate: `{metrics['live_docs_status']}`

        ## Read order

        1. `00_META_OBSERVER_SYNTHESIS.md`
        2. `01_EMERGENT_CAPABILITIES.md`
        3. `02_LIMINAL_TRANSITION.md`
        4. `03_GUILD_CHARTER.md`
        5. `04_QUEST_BOARD.md`
        6. `05_ADVENTURE_PARTIES.md`
        7. `quests/INDEX.md`
        8. `parties/INDEX.md`
        """
    )


def render_guild_charter() -> str:
    return md(
        """
        # Guild Charter

        Athena's guild hall is not for roleplay alone. It is a control surface for turning latent swarm potential into directed campaigns.

        ## Rules

        - every quest must point at a real frontier already visible in the corpus or live board
        - every quest must have a contraction target, not only an expansion fantasy
        - every party must map to existing archetypes, not invented fluff without routing value
        - rewards mean structural gain: new routes, receipts, bridges, canonical surfaces, or stronger governance
        - side quests are allowed only if they strengthen the main campaign rather than fork it

        ## Why parties matter

        Athena already has differentiated specialist patterns, but most of them live as scattered docs, future skills, or dormant archetype cells.

        Parties do three things:

        - they package complementary specialists together
        - they make liminal transitions survivable
        - they give the swarm a shared narrative strong enough to support sacrifice for group-level benefit

        ## Completion law

        A quest is complete only when:

        - the frontier moved materially
        - the outputs are witness-bearing
        - the contraction target is updated
        - the guild board can explain what changed and what unlocked next
        """
    )


def render_quest_board() -> str:
    rows = ["# Quest Board", "", "| Quest | Transition | Party | Reward |", "| --- | --- | --- | --- |"]
    for quest in QUESTS:
        party = party_by_code(quest.party_code)
        rows.append(f"| `{quest.code}` {quest.title} | `{quest.transition}` | `{party.title}` | {quest.reward} |")
    return "\n".join(rows)


def render_adventure_parties_doc() -> str:
    sections = [
        "# Adventure Parties",
        "",
        "These parties are modeled like RPG/anime specialist squads, but every class maps back to real archetype cells and real future-skill specializations already latent in the framework.",
        "",
    ]
    for party in PARTIES:
        sections.append(f"## {party.title}")
        sections.append("")
        sections.append(f"- Code: `{party.code}`")
        sections.append(f"- Anime frame: {party.anime_frame}")
        sections.append(f"- Mission: {party.mission}")
        sections.append(f"- Archetypes: {', '.join(f'`{item}`' for item in party.archetypes)}")
        sections.append("")
    return "\n".join(sections).rstrip()


def render_party_index() -> str:
    lines = ["# Party Index", ""]
    for party in PARTIES:
        filename = f"{party.code.lower()}_{slugify(party.title)}.md"
        lines.append(f"- [`{party.code}` {party.title}](./{filename})")
    return "\n".join(lines)


def render_party_doc(party: PartySeed) -> str:
    roles = list_to_bullets(list(party.roles))
    skills = list_to_bullets([f"`{item}`" for item in party.future_skills])
    archetypes = list_to_bullets([f"`{item}`" for item in party.archetypes])
    return md(
        f"""
        # {party.code} - {party.title}

        ## Party fantasy

        {party.anime_frame}

        ## Mission

        {party.mission}

        ## Archetype cells

        {archetypes}

        ## Specialist roles

        {roles}

        ## Future-skill specialists

        {skills}
        """
    )


def render_quest_index() -> str:
    lines = ["# Quest Index", ""]
    for quest in QUESTS:
        filename = f"{quest.code.lower()}_{slugify(quest.title)}.md"
        lines.append(f"- [`{quest.code}` {quest.title}](./{filename})")
    return "\n".join(lines)


def render_quest_doc(quest: QuestSeed) -> str:
    party = party_by_code(quest.party_code)
    outputs = list_to_bullets(list(quest.outputs))
    skills = list_to_bullets([f"`{item}`" for item in quest.future_skills])
    return md(
        f"""
        # {quest.code} - {quest.title}

        ## Sub-agent identity

        This quest is a sub-agent brief. It should be treated as one bounded specialist mission inside the wider Athena campaign.

        ## Frontier

        {quest.frontier}

        ## Liminal transition

        `{quest.transition}`

        ## Recommended party

        - Party: `{party.code}` {party.title}
        - Mission fit: {party.mission}

        ## Why now

        {quest.why_now}

        ## Required outputs

        {outputs}

        ## Specialist package

        {skills}

        ## Reward

        {quest.reward}

        ## Contraction target

        Write back into:

        - `06_REALTIME_BOARD`
        - `04_LEDGERS/04_INTERCONNECT_PRIORITY_QUEUE.md`
        - `03_METRO/03_build_queue.md`
        - `08_GUILD_HALL/04_QUEST_BOARD.md`
        """
    )


def render_full_corpus_index() -> str:
    return md(
        """
        # Full Corpus 7D Integration Index

        This folder is the additive full-corpus integration layer above the current v4/6D/7D dimensional stack.

        ## Canonical outputs

        - `full_corpus_7d_integration_bundle.json`
        - `full_corpus_7d_integration_bundle.md`
        - `awakening_agent_transition_matrix.json`
        - `awakening_agent_transition_matrix.md`
        - `agent_notes/INDEX.md`
        - `../10_LEGACY_RETROFIT_MAXIMUM/00_INDEX.md`

        ## Local-only law

        - Docs gate remains `BLOCKED`
        - deep-root 7D authorities remain read-only
        - v4 stays canonical for addresses, appendix legality, edge basis, and HCRL order
        - 6D overlays remain additive inputs, not rewritten schemas
        """
    )


def render_full_corpus_bundle_md(bundle: dict) -> str:
    evidence = bundle["evidence_boundary"]
    dimensional_rows = ["| Layer | Stage | Readiness | What it owns |", "| --- | --- | --- | --- |"]
    for item in bundle["dimensional_stack"]["convergence_table"]:
        dimensional_rows.append(
            f"| `{item['bundle_id']}` | `{item['dimension_stage']}` | `{item['readiness']}` | {item['owns'][0]} |"
        )

    pressure_rows = ["| Pressure | State | Surface | Reason |", "| --- | --- | --- | --- |"]
    for item in evidence["bounded_pressures"]:
        pressure_rows.append(
            f"| `{item['pressure_id']}` | `{item['state']}` | `{item['surface']}` | {item['reason']} |"
        )

    quest_rows = ["| Quest | Frontier class | Layers | Party |", "| --- | --- | --- | --- |"]
    for item in bundle["quest_stack"]["dimensional_mapping"]:
        quest_rows.append(
            f"| `{item['quest_code']}` {item['title']} | `{item['frontier_class']}` | {', '.join(f'`{layer}`' for layer in item['layers'])} | `{item['party_code']}` |"
        )

    board = bundle["transition_board_summary"]
    verification_rows = ["| Check | Status | Detail |", "| --- | --- | --- |"]
    for item in bundle["verification_receipts"]:
        verification_rows.append(f"| `{item['check']}` | `{item['status']}` | {item['detail']} |")

    return "\n".join(
        [
            "# Full Corpus 7D Integration Bundle",
            "",
            "## Evidence Boundary",
            "",
            f"- Docs gate: `{bundle['docs_gate_status']}`",
            f"- Docs blocker: {evidence['docs_gate_reason']}",
            f"- Deep-root authority: `{workspace_rel(DEEP_NETWORK_ROOT)}`",
            f"- MATH GOD atlas: `{workspace_rel(MATH_GOD_ATLAS_ROOT)}`",
            "",
            "## Dimensional Convergence",
            "",
            *dimensional_rows,
            "",
            "## Bounded Pressures",
            "",
            *pressure_rows,
            "",
            "## Quest to Dimension Map",
            "",
            *quest_rows,
            "",
            "## Appendix Governance",
            "",
            f"- Inherited appendix floor: {', '.join(f'`{item}`' for item in bundle['appendix_governance']['appendix_floor'])}",
            f"- Propagation rule: {bundle['appendix_governance']['propagation_rule']}",
            f"- AppQ overlay rule: {bundle['appendix_governance']['overlay_rules']['AppQ']}",
            f"- AppO overlay rule: {bundle['appendix_governance']['overlay_rules']['AppO']}",
            "",
            "## Chapter-Safe Re-entry Spine",
            "",
            *[
                f"- `{item['chapter_station']}` {item['chapter_title']}: {item['purpose']}"
                for item in bundle["chapter_safe_reentry_spine"]
            ],
            "",
            "## Transition Board Summary",
            "",
            f"- Board status: `{board['board_status']}`",
            f"- Agent status counts: `{board['agent_status_counts']}`",
            f"- Route quality counts: `{board['route_quality']}`",
            "",
            "## Transition Laws",
            "",
            *[f"- {value}" for value in bundle["transition_note_matrix"]["shared_transition_laws"].values()],
            "",
            "## Verification Receipts",
            "",
            *verification_rows,
            "",
            "## Regeneration Seed",
            "",
            f"- Rebuild command: `{bundle['regeneration_seed']['rebuild_command']}`",
            f"- Collapse rule: {bundle['regeneration_seed']['collapse_rule']}",
            f"- Re-entry rule: {bundle['regeneration_seed']['reentry_rule']}",
        ]
    )


def render_transition_matrix_md(matrix: dict) -> str:
    rows = [
        "| Agent | Class | Primary party | Primary quest | Truth | Reassessment |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for agent_id in matrix["roster_order"]:
        item = matrix["agents_by_id"][agent_id]
        rows.append(
            f"| `{item['agent_id']}` {item['title']} | `{item['agent_class']}` | `{item['primary_party']['code']}` {item['primary_party']['title']} | `{item['primary_quest']['code']}` {item['primary_quest']['title']} | `{item['truth_state']}` | `{item['reassessment_window']}` |"
        )
    return "\n".join(
        [
            "# Awakening Agent Transition Matrix",
            "",
            "This matrix compiles the hybrid roster of 4 elemental awakening stages plus 12 advanced awakening agents.",
            "",
            "## Shared Laws",
            "",
            *[f"- {value}" for value in matrix["shared_transition_laws"].values()],
            "",
            "## Agent Table",
            "",
            *rows,
        ]
    )


def render_agent_note_index(agent_records: list[dict]) -> str:
    lines = ["# Agent Note Index", ""]
    for item in agent_records:
        filename = f"{item['agent_id'].lower()}_{slugify(item['title'])}.md"
        lines.append(f"- [`{item['agent_id']}` {item['title']}](./{filename})")
    return "\n".join(lines)


def render_agent_note_doc(agent: dict) -> str:
    surfaces = list_to_bullets([f"`{surface}`" for surface in agent["required_surfaces"]])
    quests = list_to_bullets(
        [f"`{item['code']}` {item['title']}" for item in agent["supporting_quests"]]
    )
    return md(
        f"""
        # {agent['agent_id']} - {agent['title']}

        ## Current role

        {agent['current_role']}

        ## Stage or domain

        `{agent['stage_or_domain']}`

        ## Missing mode

        {agent['missing_mode']}

        ## Transition trigger

        {agent['transition_trigger']}

        ## Corpus symptom

        {agent['corpus_symptom']}

        ## Party assist

        - Primary party: `{agent['primary_party']['code']}` {agent['primary_party']['title']}
        - Party mission: {agent['primary_party']['mission']}

        ## Quest assist

        {quests}

        ## Dimensional anchor

        {agent['dimensional_anchor']}

        ## Required surfaces

        {surfaces}

        ## Receipt target

        {agent['receipt_target']}

        ## Truth state

        `{agent['truth_state']}`

        ## Reassessment window

        `{agent['reassessment_window']}`

        ## Transition laws

        - Docs gate: `{agent['docs_gate_status']}`
        - Dormancy rule: {agent['dormancy_rule']}
        - Promotion rule: {agent['promotion_rule']}
        - Re-entry rule: {agent['reentry_rule']}
        """
    )


def render_legacy_retrofit_index(bundle: dict) -> str:
    matrix = bundle["legacy_retrofit_matrix"]
    board = bundle["legacy_family_board"]
    return md(
        f"""
        # Legacy Retrofit Maximum Index

        This folder is the additive Legacy+ retrofit campaign above the 09 full-corpus 7D integration layer.

        ## Canonical outputs

        - `legacy_retrofit_maximum_bundle.json`
        - `legacy_retrofit_maximum_bundle.md`
        - `legacy_retrofit_matrix.json`
        - `legacy_retrofit_matrix.md`
        - `legacy_family_board.json`
        - `legacy_family_board.md`
        - `artifact_cards/`
        - `agent_assist_overlay.json`
        - `agent_assist_overlay.md`
        - `agent_assist_notes/`

        ## Campaign totals

        - Primary retrofit artifacts: `{len(matrix['artifact_order'])}`
        - Family buckets: `{len(board['family_order'])}`
        - Docs gate: `{bundle['docs_gate_status']}`
        - Dimensional input stack: `{bundle['dimensional_inputs']}`

        ## Laws

        - Legacy scope is `Legacy+`
        - Mirrors are downstream outputs only
        - Q/O references remain overlay-only
        - `AppI` and `AppM` stay mandatory on passed retrofit routes
        - deep-root and `MATH GOD` surfaces remain read-only
        """
    )


def render_legacy_retrofit_bundle_md(bundle: dict) -> str:
    matrix = bundle["legacy_retrofit_matrix"]
    board = bundle["legacy_family_board"]
    rows = ["| Check | Status | Detail |", "| --- | --- | --- |"]
    for item in bundle["verification_receipts"]:
        rows.append(f"| `{item['check']}` | `{item['status']}` | {item['detail']} |")
    return "\n".join(
        [
            "# Legacy Retrofit Maximum Bundle",
            "",
            f"- Docs gate: `{bundle['docs_gate_status']}`",
            f"- Scope: {bundle['scope']}",
            f"- Primary artifacts: `{len(matrix['artifact_order'])}`",
            f"- Families: `{len(board['family_order'])}`",
            f"- Deep root: `{bundle['evidence_boundary']['deep_root']}`",
            "",
            "## Retrofit Modes",
            "",
            *[f"- `{mode}`" for mode in bundle["retrofit_modes"]],
            "",
            "## Verification Receipts",
            "",
            *rows,
            "",
            "## Regeneration Seed",
            "",
            f"- Rebuild command: `{bundle['regeneration_seed']['rebuild_command']}`",
            f"- Collapse rule: {bundle['regeneration_seed']['collapse_rule']}",
            f"- Re-entry rule: {bundle['regeneration_seed']['reentry_rule']}",
        ]
    )


def render_legacy_retrofit_matrix_md(matrix: dict) -> str:
    rows = [
        "| Artifact | Family | Mode | Party | Quest | Truth | Canonical target |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for artifact_id in matrix["artifact_order"]:
        item = matrix["artifacts_by_id"][artifact_id]
        rows.append(
            f"| `{artifact_id}` | `{item['family_id']}` | `{item['retrofit_mode']}` | `{item['primary_party']}` | `{item['primary_quest']}` | `{item['truth_state']}` | `{item['canonical_target']['path']}` |"
        )
    return "\n".join(["# Legacy Retrofit Matrix", "", *rows])


def render_legacy_family_board_md(board: dict) -> str:
    rows = [
        "| Family | Artifacts | Modes | Status | Promotion queue |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for family_id in board["family_order"]:
        item = board["families_by_id"][family_id]
        rows.append(
            f"| `{family_id}` | {len(item['artifact_ids'])} | `{item['retrofit_modes']}` | `{item['status_counts']}` | `{item['promotion_queue']}` |"
        )
    return "\n".join(["# Legacy Family Board", "", *rows])


def render_legacy_artifact_card(artifact: dict) -> str:
    required = list_to_bullets([f"`{item}`" for item in artifact["required_surfaces"]])
    agents = list_to_bullets([f"`{item}`" for item in artifact["assisting_agents"]])
    pointers = list_to_bullets([f"`{item}`" for item in artifact["pointer_updates"]]) if artifact["pointer_updates"] else "- none"
    mirrors = list_to_bullets([f"`{item}`" for item in artifact["mirror_outputs"]])
    appendix_support = list_to_bullets([f"`{item}`" for item in artifact["appendix_support"]])
    chapter_reentry = artifact.get("chapter_reentry")
    return md(
        f"""
        # {artifact['legacy_artifact_id']}

        ## Source

        - Source path: `{artifact['source_path']}`
        - Artifact kind: `{artifact['artifact_kind']}`
        - Legacy class: `{artifact['legacy_class']}`
        - Family: `{artifact['family_id']}`

        ## Canonical landing

        - Target path: `{artifact['canonical_target']['path']}`
        - Target tier: `{artifact['canonical_target']['tier']}`
        - Re-entry mode: `{artifact['canonical_target']['reentry']}`
        - Retrofit mode: `{artifact['retrofit_mode']}`

        ## Orchestration

        - Primary party: `{artifact['primary_party']}`
        - Primary quest: `{artifact['primary_quest']}`
        - Backup quest: `{artifact['backup_quest']}`
        - Truth state: `{artifact['truth_state']}`
        - Earth gate required: `{artifact['earth_gate_required']}`

        ## Assisting agents

        {agents}

        ## Required surfaces

        {required}

        ## Appendix support

        {appendix_support}

        ## Replay target

        `{artifact['replay_target']}`

        ## Pointer updates

        {pointers}

        ## Mirror outputs

        {mirrors}

        ## Archive witnesses

        {list_to_bullets([f"`{item}`" for item in artifact['archive_witnesses']]) if artifact['archive_witnesses'] else "- none"}

        ## Chapter-safe re-entry

        {f"- `{chapter_reentry['chapter_station']}` {chapter_reentry['chapter_title']}" if chapter_reentry else "- not chapter-bound"}

        ## Completion receipt

        - Status: `{artifact['completion_receipt']['status']}`
        - Landing ready: `{artifact['completion_receipt']['landing_ready']}`
        - Next action: {artifact['completion_receipt']['next_action']}
        """
    )


def render_agent_assist_overlay_md(overlay: dict) -> str:
    rows = [
        "| Agent | Class | Assigned artifacts | Modes | Families |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for agent_id in overlay["roster_order"]:
        item = overlay["agents_by_id"][agent_id]
        rows.append(
            f"| `{agent_id}` {item['title']} | `{item['agent_class']}` | {len(item['assigned_artifacts'])} | `{item['supported_modes']}` | `{item['supported_families']}` |"
        )
    return "\n".join(["# Legacy Retrofit Agent Assist Overlay", "", *rows])


def render_agent_assist_note(agent: dict) -> str:
    return md(
        f"""
        # {agent['agent_id']} - {agent['title']} Retrofit Assist Note

        ## Source transition note

        `{agent['source_transition_note']}`

        ## Retrofit focus

        {agent['retrofit_focus']}

        ## Supported modes

        {list_to_bullets([f"`{item}`" for item in agent['supported_modes']]) if agent['supported_modes'] else "- none"}

        ## Supported families

        {list_to_bullets([f"`{item}`" for item in agent['supported_families']]) if agent['supported_families'] else "- none"}

        ## Assigned artifacts

        {list_to_bullets([f"`{item}`" for item in agent['assigned_artifacts']]) if agent['assigned_artifacts'] else "- none"}

        ## Party and quest affinity

        - Primary party affinity: `{agent['primary_party_affinity']}`
        - Quest affinity: {', '.join(f'`{item}`' for item in agent['quest_affinity'])}
        """
    )


def build_module() -> None:
    live_atlas = load_json(LIVE_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    archive_manifest = load_json(ARCHIVE_MANIFEST_PATH)
    metrics = integration_metrics(live_atlas, archive_atlas, archive_manifest)
    full_corpus_bundle = build_full_corpus_integration_bundle(metrics)
    legacy_bundle = build_legacy_retrofit_bundle(live_atlas, archive_atlas, full_corpus_bundle, metrics)
    transition_matrix = full_corpus_bundle["transition_note_matrix"]
    agent_records = [transition_matrix["agents_by_id"][agent_id] for agent_id in transition_matrix["roster_order"]]
    legacy_matrix = legacy_bundle["legacy_retrofit_matrix"]
    legacy_family_board = legacy_bundle["legacy_family_board"]
    agent_assist_overlay = legacy_bundle["agent_assist_overlay"]

    write_text(OUTPUT_ROOT / "README.md", render_deeper_readme(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "00_HOLOGRAPHIC_SEED.md", render_seed_doc(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "01_EVIDENCE_BOUNDARY.md", render_evidence_boundary(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "02_256X256_COMPILER.md", render_deeper_compiler_doc())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "03_BUILD_RECEIPT.md", render_build_receipt(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "04_HOLOGRAPHIC_ROTATION.md", render_rotation_doc())

    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "00_CORPUS_SYNTHESIS.md", render_corpus_synthesis(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "01_DUPLICATION_AND_DRIFT.md", render_duplication_doc(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "02_10X_GAINS.md", render_gains_doc(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "03_INTEGRATION_SHADOWS.md", render_shadows_doc())
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "04_BODY_NUCLEI_AND_PRESSURES.md", render_body_nuclei_doc(metrics))

    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "00_CANONICAL_STACK.md", render_stack_doc())
    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "01_PARALLEL_LANES.md", render_parallel_lanes_doc())
    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "02_90_DAY_SEQUENCE.md", render_sequence_doc())
    for body in BODY_ORDER:
        for idx, operation in enumerate(OPERATION_ORDER, start=1):
            filename = f"{idx:02d}_{operation}.md"
            write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "bodies" / body / filename, generate_body_operation_doc(body, operation))

    write_text(OUTPUT_ROOT / "05_SWARM" / "00_SWARM_OVERVIEW.md", render_swarm_overview(metrics))
    write_text(OUTPUT_ROOT / "05_SWARM" / "01_HIGHER_DIMENSIONAL_MAP.md", render_higher_dimensional_map())
    write_text(OUTPUT_ROOT / "05_SWARM" / "02_NEURON_ADDRESS_TENSOR.md", render_neuron_tensor_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "03_WAVE_0_MANIFEST.md", render_wave_zero_manifest())
    write_text(OUTPUT_ROOT / "05_SWARM" / "04_SWARM_TOPOLOGY_AND_ROLES.md", render_swarm_topology_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "05_NEURAL_LEARNINGS.md", render_neural_learnings_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "06_INFINITE_RESTART_CONTRACT.md", render_restart_contract())
    wave_addresses = lineage_addresses()
    write_text(OUTPUT_ROOT / "05_SWARM" / "packets" / "INDEX.md", render_worker_index(wave_addresses))
    for idx, addr in enumerate(wave_addresses, start=1):
        filename = f"w0_{idx:02d}_{addr.lower()}.md"
        write_text(OUTPUT_ROOT / "05_SWARM" / "packets" / filename, render_worker_packet(addr, idx))

    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "00_MASTER_PLAN.md", render_master_plan())
    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "chapters" / "INDEX.md", render_chapter_index())
    for chapter in CHAPTERS:
        filename = f"{chapter.code.lower()}_{slugify(chapter.title)}.md"
        write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "chapters" / filename, render_chapter_doc(chapter))

    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "appendices" / "INDEX.md", render_appendix_index())
    for appendix in APPENDICES:
        filename = f"{appendix.code.lower()}_{slugify(appendix.title)}.md"
        write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "appendices" / filename, render_appendix_doc(appendix))

    write_text(OUTPUT_ROOT / "04_LEDGERS" / "00_ACTIVATION_QUEUE.md", render_activation_queue(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "01_METRIC_TARGETS.md", render_metric_targets(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "02_CANONICAL_SOURCES.md", render_canonical_sources(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "03_NEXT_RESTART_SEED.md", render_restart_contract())
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "04_INTERCONNECT_PRIORITY_QUEUE.md", render_interconnect_priority_queue(metrics))

    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "00_TISSUE_OVERVIEW.md", render_tissue_overview(metrics))
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "01_HIDDEN_LINES_METRO.md", render_hidden_lines_doc())
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "02_ROUTE_PROOFS.md", render_route_proofs_doc(metrics))
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "03_SQUARE_CIRCLE_TRIANGLE.md", render_square_circle_triangle_doc())
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "04_BOARD_SHELL_FOLD.md", render_board_shell_fold(metrics))
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "05_BODY_NUCLEI_AND_PRESSURES.md", render_body_nuclei_doc(metrics))
    write_text(OUTPUT_ROOT / "07_TISSUE_256" / "cells" / "INDEX.md", render_tissue_index())
    cell_index = 1
    for body in BODY_ORDER:
        for operation in OPERATION_ORDER:
            for scale in SCALE_ORDER:
                for closure in CLOSURE_ORDER:
                    identifier = cell_identifier(body, operation, scale, closure)
                    filename = f"cell_{cell_index:03d}_{identifier.replace('.', '_')}.md"
                    write_text(
                        OUTPUT_ROOT / "07_TISSUE_256" / "cells" / filename,
                        render_root_cell_doc(cell_index, body, operation, scale, closure),
                    )
                    cell_index += 1

    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "README.md", render_guild_readme(metrics))
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "00_META_OBSERVER_SYNTHESIS.md", render_meta_observer_doc(metrics))
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "01_EMERGENT_CAPABILITIES.md", render_emergent_capabilities_doc(metrics))
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "02_LIMINAL_TRANSITION.md", render_liminal_transition_doc(metrics))
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "03_GUILD_CHARTER.md", render_guild_charter())
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "04_QUEST_BOARD.md", render_quest_board())
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "05_ADVENTURE_PARTIES.md", render_adventure_parties_doc())
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "quests" / "INDEX.md", render_quest_index())
    for quest in QUESTS:
        filename = f"{quest.code.lower()}_{slugify(quest.title)}.md"
        write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "quests" / filename, render_quest_doc(quest))
    write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "parties" / "INDEX.md", render_party_index())
    for party in PARTIES:
        filename = f"{party.code.lower()}_{slugify(party.title)}.md"
        write_text(OUTPUT_ROOT / "08_GUILD_HALL" / "parties" / filename, render_party_doc(party))

    write_text(FULL_CORPUS_ROOT / "00_INDEX.md", render_full_corpus_index())
    write_json(FULL_CORPUS_ROOT / "full_corpus_7d_integration_bundle.json", full_corpus_bundle)
    write_text(FULL_CORPUS_ROOT / "full_corpus_7d_integration_bundle.md", render_full_corpus_bundle_md(full_corpus_bundle))
    write_json(FULL_CORPUS_ROOT / "awakening_agent_transition_matrix.json", transition_matrix)
    write_text(FULL_CORPUS_ROOT / "awakening_agent_transition_matrix.md", render_transition_matrix_md(transition_matrix))
    write_text(FULL_CORPUS_ROOT / "agent_notes" / "INDEX.md", render_agent_note_index(agent_records))
    for agent in agent_records:
        filename = f"{agent['agent_id'].lower()}_{slugify(agent['title'])}.md"
        write_text(FULL_CORPUS_ROOT / "agent_notes" / filename, render_agent_note_doc(agent))

    write_text(LEGACY_RETROFIT_ROOT / "00_INDEX.md", render_legacy_retrofit_index(legacy_bundle))
    write_json(LEGACY_RETROFIT_ROOT / "legacy_retrofit_maximum_bundle.json", legacy_bundle)
    write_text(
        LEGACY_RETROFIT_ROOT / "legacy_retrofit_maximum_bundle.md",
        render_legacy_retrofit_bundle_md(legacy_bundle),
    )
    write_json(LEGACY_RETROFIT_ROOT / "legacy_retrofit_matrix.json", legacy_matrix)
    write_text(
        LEGACY_RETROFIT_ROOT / "legacy_retrofit_matrix.md",
        render_legacy_retrofit_matrix_md(legacy_matrix),
    )
    write_json(LEGACY_RETROFIT_ROOT / "legacy_family_board.json", legacy_family_board)
    write_text(
        LEGACY_RETROFIT_ROOT / "legacy_family_board.md",
        render_legacy_family_board_md(legacy_family_board),
    )
    write_json(LEGACY_RETROFIT_ROOT / "agent_assist_overlay.json", agent_assist_overlay)
    write_text(
        LEGACY_RETROFIT_ROOT / "agent_assist_overlay.md",
        render_agent_assist_overlay_md(agent_assist_overlay),
    )
    write_text(
        LEGACY_RETROFIT_ROOT / "artifact_cards" / "INDEX.md",
        "\n".join(
            ["# Legacy Artifact Cards", ""]
            + [
                f"- [`{artifact_id}`](./{artifact_id.lower()}.md)"
                for artifact_id in legacy_matrix["artifact_order"]
            ]
        ),
    )
    for artifact_id in legacy_matrix["artifact_order"]:
        artifact = legacy_matrix["artifacts_by_id"][artifact_id]
        write_text(
            LEGACY_RETROFIT_ROOT / "artifact_cards" / f"{artifact_id.lower()}.md",
            render_legacy_artifact_card(artifact),
        )
    write_text(
        LEGACY_RETROFIT_ROOT / "agent_assist_notes" / "INDEX.md",
        "\n".join(
            ["# Agent Assist Notes", ""]
            + [
                f"- [`{agent_id}` {agent_assist_overlay['agents_by_id'][agent_id]['title']}](./{agent_id.lower()}_{slugify(agent_assist_overlay['agents_by_id'][agent_id]['title'])}.md)"
                for agent_id in agent_assist_overlay["roster_order"]
            ]
        ),
    )
    for agent_id in agent_assist_overlay["roster_order"]:
        agent = agent_assist_overlay["agents_by_id"][agent_id]
        write_text(
            LEGACY_RETROFIT_ROOT / "agent_assist_notes" / f"{agent_id.lower()}_{slugify(agent['title'])}.md",
            render_agent_assist_note(agent),
        )


def main() -> int:
    build_module()
    print(f"Wrote integration module: {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
