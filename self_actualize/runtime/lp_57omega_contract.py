from __future__ import annotations

from pathlib import Path
from typing import Any


DATE = "2026-03-13"

ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ROOT / "mycelium_brain"
NERVOUS_MANIFEST_ROOT = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
DEEP_ROOT = MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
TRADING_BOT_DIR = ROOT / "Trading Bot"

LIVE_DOCS_GATE_PATH = SELF_ROOT / "live_docs_gate_status.md"
CANONICAL_PROTOCOL_MD_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_PROGRAM.md"
CANONICAL_PROTOCOL_JSON_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_PROGRAM.json"
CANONICAL_PROTOCOL_DASHBOARD_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_DASHBOARD.md"
CANONICAL_PROTOCOL_NOTES_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_AWAKENING_NOTES.md"
CANONICAL_LOOP_REGISTRY_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
CANONICAL_PACKET_REGISTRY_PATH = NERVOUS_MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"
CANONICAL_VERIFY_JSON_PATH = SELF_ROOT / "four_agent_57_loop_program_verification.json"
CANONICAL_PROGRAM_MD_PATH = CANONICAL_PROTOCOL_MD_PATH
CANONICAL_PROGRAM_JSON_PATH = CANONICAL_PROTOCOL_JSON_PATH

NEXT57_STATE_JSON_PATH = SELF_ROOT / "next57_four_agent_corpus_cycle_state.json"
NEXT57_SEAT_REGISTRY_PATH = SELF_ROOT / "next57_four_agent_nested_seat_registry.json"
NEXT57_QUEST_PACKETS_PATH = SELF_ROOT / "next57_four_agent_quest_packets.json"
NEXT57_AWAKENING_NOTES_PATH = SELF_ROOT / "next57_four_agent_awakening_assist_notes.json"
NEXT57_VERIFY_JSON_PATH = SELF_ROOT / "next57_four_agent_corpus_cycle_verification.json"
NEXT57_COMPATIBILITY_REGISTRY_PATH = SELF_ROOT / "next57_compatibility_mirror_registry.json"
NEXT57_MANIFEST_MD_PATH = NERVOUS_MANIFEST_ROOT / "NEXT_57_LOOP_FOUR_AGENT_CORPUS_CYCLE.md"
NEXT57_DASHBOARD_MD_PATH = NERVOUS_MANIFEST_ROOT / "NEXT_57_LOOP_FOUR_AGENT_DASHBOARD.md"
NEXT57_AWAKENING_MD_PATH = NERVOUS_MANIFEST_ROOT / "NEXT_57_LOOP_AWAKENING_ASSIST_BUNDLE.md"
NEXT57_COMPATIBILITY_MD_PATH = NERVOUS_MANIFEST_ROOT / "NEXT_57_LOOP_COMPATIBILITY_MIRRORS.md"
NEXT57_RECEIPT_MD_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_next_57_loop_four_agent_corpus_cycle.md"
TQ07_QUEST_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "QUESTS" / "TQ07_INSTALL_THE_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md"

LP57_PROTOCOL_MD_PATH = NERVOUS_MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
LP57_PROTOCOL_JSON_PATH = NERVOUS_MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.json"
LP57_DASHBOARD_MD_PATH = NERVOUS_MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_DASHBOARD.md"
LP57_VERIFY_MD_PATH = NERVOUS_MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.md"
LP57_VERIFY_JSON_PATH = NERVOUS_MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.json"

QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
ACTIVE_RUN_PATH = NERVOUS_MANIFEST_ROOT / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_MANIFEST_ROOT / "BUILD_QUEUE.md"
WHOLE_COORDINATION_PATH = NERVOUS_MANIFEST_ROOT / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
CHANGE_FEED_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
REQUESTS_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"

LIVE_HALL_FRONT = "NEXT57"
LIVE_TEMPLE_FRONT = "TQ04"
HISTORICAL_ALIASES = ["FOUR_AGENT_57_LOOP_PROGRAM", "Q51_TQ07", "FA57"]
PRESERVED_FEEDERS = ["Q42", "Q46", "TQ04", "TQ06", "Q50"]
BLOCKED_FRONTS = ["Q02"]
ACTIVE_MEMBRANE = "Q41 / TQ06"
CARRIED_WITNESS = "QS64-20 Connectivity-Diagnose-Fractal"
CLOSED_LOCAL_PROOF = "QS64-24 Connectivity-Refine-Fractal"
NEXT_HALL_SEED = "QS64-22 Connectivity-Refine-Flower"
TEMPLE_HANDOFF = "TQ04"
RESERVE_FRONTIER = "Q46"
RUNTIME_SEED = "Q50"
CURRENT_RESTART_SEED = "L03 -> Pair synthesis A -> observer variance -> theorem-kernel pressure"
DEEP_ROOT_AUTHORITY = "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
PROTOCOL_ID = "LP-57Ω"
PROGRAM_ID = "LP-57Omega-canonical-protocol@2026-03-13"
SEAT_LAW = {
    "per_master_agent": {"compiled": 4096, "active": 1024, "dormant": 3072},
    "compiled_lattice": "16 macros -> 64 Hall packets -> 256 governance fibers -> 1024 active synaptic seats -> 4096 atlas seats",
    "board_visibility": "macro and packet only; fiber, seat, and atlas remain registry-backed",
}
MACRO_QUOTAS = {"hall": 4, "temple": 2, "queue_delta": 1, "restart_seed": 1}

MASTER_AGENT_SPECS = [
    {
        "agent_id": "A1",
        "name": "Synthesizer / Researcher",
        "role_tag": "SYNTH-RESEARCH",
        "mission": "deeply scan the full corpus, detect hidden bridges, contradictions, mathematical upgrades, and latent integration structures",
        "outputs": [
            "current-state synthesis",
            "unresolved tensions",
            "hidden opportunities",
            "candidate junction points",
            "recommended high-value integrations",
        ],
    },
    {
        "agent_id": "A2",
        "name": "Planner / Architect",
        "role_tag": "PLANNER-ARCHITECT",
        "mission": "turn synthesis into Hall and Temple quest trees, dependency graphs, sequencing logic, and structured action pathways",
        "outputs": [
            "Guild Hall quest tree",
            "Temple quest tree",
            "priority ladder",
            "dependency graph",
            "strategic blueprint",
        ],
    },
    {
        "agent_id": "A3",
        "name": "Worker / Adventurer",
        "role_tag": "WORKER-ADVENTURER",
        "mission": "apply replay-safe Hall and Temple work, land artifacts, bridges, equations, algorithm scaffolds, and implementation receipts",
        "outputs": [
            "applied changes",
            "drafted modules",
            "inserted links",
            "new equations and algorithms",
            "implementation ledger",
        ],
    },
    {
        "agent_id": "A4",
        "name": "Pruner / Compressor / Defragmenter",
        "role_tag": "PRUNE-CRYSTAL",
        "mission": "tighten the corpus, reduce redundancy, preserve witnesses, and reseed the next loop from a cleaner crystalline baseline",
        "outputs": [
            "compressed structures",
            "pruned redundancies",
            "reorganized architecture",
            "refined naming or indexing",
            "compression ledger",
        ],
    },
]

NESTED_RESOLUTION_AXES = [
    "manuscript",
    "chapter",
    "section",
    "concept",
    "equation/algorithm",
    "metadata/routing",
]

COORDINATE_AXIS_MEANINGS = {
    "Xs": "document region",
    "Ys": "concept cluster",
    "Zs": "recursion depth",
    "Ts": "temporal revision layer",
    "Qs": "mathematical density",
    "Rs": "symbolic density",
    "Cs": "compression state",
    "Fs": "framework lens",
    "Ms": "manuscript branch",
    "Ns": "neural or mycelial connectivity",
    "Hs": "hierarchy level",
    "OmegaS": "zero-point or aether relation",
}

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

def loop_row(
    focus: str,
    synthesis: str,
    planning: str,
    implementation: str,
    pruning: str,
    structural_gain: str,
    mapping_gain: str,
) -> dict[str, str]:
    return {
        "dominant_focus": focus,
        "primary_synthesis_objective": synthesis,
        "primary_planning_objective": planning,
        "primary_implementation_objective": implementation,
        "primary_compression_pruning_objective": pruning,
        "expected_structural_gain": structural_gain,
        "expected_mapping_ledger_gain": mapping_gain,
    }


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def docs_gate_payload() -> dict[str, Any]:
    missing = [p for p in ["credentials.json", "token.json"] if not (TRADING_BOT_DIR / p).exists()]
    return {
        "status": "BLOCKED" if missing else "LIVE",
        "missing_files": [f"Trading Bot/{name}" for name in missing],
        "source_of_truth": rel(LIVE_DOCS_GATE_PATH),
    }


def make_branch_path(*indices: int | str) -> str:
    if not indices:
        return "BROOT"
    rendered = "".join(str(index) for index in indices)
    return f"B{rendered}"


def make_agent_id_tag(loop_id: str, master_agent_id: str, nested_depth: int, branch_path: str, role_tag: str) -> str:
    return f"{loop_id}.{master_agent_id}.D{nested_depth}.{branch_path}.{role_tag}"


def make_liminal_coordinate(
    *,
    document_region: str,
    concept_cluster: str,
    recursion_depth: str,
    temporal_layer: str,
    operation_class: str,
    active_lens: str,
    compression_state: str,
    framework_surface: str,
    manuscript_branch: str,
    return_path: str,
    hierarchy_level: str,
    zero_relation: str,
) -> dict[str, str]:
    return {
        "Xs": document_region,
        "Ys": concept_cluster,
        "Zs": recursion_depth,
        "Ts": temporal_layer,
        "Qs": operation_class,
        "Rs": active_lens,
        "Cs": compression_state,
        "Fs": framework_surface,
        "Ms": manuscript_branch,
        "Ns": return_path,
        "Hs": hierarchy_level,
        "OmegaS": zero_relation,
    }


def make_lookup_addr(*parts: str) -> str:
    return "/".join(["LP-57Omega", *parts])


LOOP_PLAN = [
    loop_row("Docs truth freeze", "confirm blocked Docs reality and local-only evidence law", "lock fallback routes for every agent lane", "install gate-check as step zero of every loop", "remove faux live-doc assumptions", "honest base layer", "global blocker stamp"),
    loop_row("Deep-root freeze", "re-confirm the single live deep root", "mark all older roots witness-only", "bind deep-root references into conductor templates", "prune peer-authority drift", "one deep authority", "root-precedence map"),
    loop_row("Seat-law reconciliation", "compare `16/64/256/1024/4096` across live surfaces", "define one canonical count story", "schedule count-fix packets for Hall, Temple, queue, manifests", "retire conflicting count prose", "one lattice law", "count-delta register"),
    loop_row("Q42 split normalization", "inspect carried witness, closed proof, Temple handoff, reserve, runtime, and blocker", "freeze exact field names", "route split into all control surfaces", "remove collapsed front descriptions", "lawful front geometry", "front-split atlas"),
    loop_row("ADV64/AP6D compatibility", "detect overlap between Adventurer and AP6D conductor stories", "define coexistence rules", "attach compatibility notes to both stacks", "retire competing ownership language", "non-competing overlays", "interoperability matrix"),
    loop_row("Precedence law", "validate surface hierarchy", "encode `Cortex -> RuntimeHub -> GovernanceMirror -> Hall/Temple writeback`", "assign writeback destinations by class", "remove sideways promotion drift", "deterministic authority flow", "precedence chain"),
    loop_row("Live-front preservation", "map `Q42/Q46/TQ04/Q50/Q02` responsibilities", "define no-collapse law", "bind each master agent to the same live-front frame", "prune hidden replacements", "stable shared frame", "live-front ledger"),
    loop_row("Charter publication", "compress loops 1-7 into doctrine", "publish machine registry and human charter", "emit the top-level loop program package", "eliminate earlier contradictory startup language", "executable governance start", "charter receipt"),
    loop_row("Deep-basis reread", "rescan `16` basis docs, `256` pairs, `64` observers, `7` metro levels, and `AppQ`", "identify high-leverage reread order", "spawn manuscript-level synthesizer subagents", "merge duplicate basis descriptors", "grounded intake map", "basis reread register"),
    loop_row("Whole-corpus body ledger", "enumerate all major bodies and root anchors", "assign survey coverage by region", "draft first body ledger rows", "collapse redundant body aliases", "corpus body census", "body-id atlas"),
    loop_row("Body classification", "assign truth class, pressure class, reserve state, and owner surface", "define classification rubric", "stamp classes into route rows", "prune vague category drift", "executable body taxonomy", "classification table"),
    loop_row("Family tensor reconciliation", "inspect active-front drift per body", "assign one active front and one restart seed per body", "wire tensor updates to machine surfaces", "remove orphan front references", "one front per body", "family tensor delta"),
    loop_row("Source-reservoir atlas", "find tome, manuscript, archive, registry, and runtime reservoirs", "rank by leverage and freshness", "build source-reservoir rows", "merge duplicate reservoir names", "structured research intake", "reservoir atlas"),
    loop_row("Cross-corpus route graph", "trace `T3/T8/T9/T10/AppM/AppQ/GC0` routes", "choose primary replay-safe corridors", "attach route IDs to body rows", "collapse redundant corridor names", "graphable transport model", "route graph"),
    loop_row("Replay validation", "identify missing return paths", "prioritize broken-return corridors", "tag replay path on every routed body", "prune non-returnable route claims", "replay-safe corpus graph", "replay-path verifier"),
    loop_row("Intake charter", "summarize loops 9-15 into research/planner intake law", "freeze future intake criteria", "emit the intake charter to Hall/Temple support surfaces", "compress earlier survey notes into the new charter", "stable intake membrane", "intake charter receipt"),
    loop_row("Master-agent registry", "define master-agent scopes and interface boundaries", "assign A1-A4 exact responsibilities", "register agent contracts", "remove overlap drift", "clean agent boundaries", "agent registry"),
    loop_row("Macro quest lattice", "decide the `16` macro quest families", "map macros to body clusters and live fronts", "create macro quest skeletons", "merge overlapping macro categories", "ownerable macro field", "macro lattice map"),
    loop_row("Hall packet derivation", "expand macros into `64` Hall packets", "set packet naming and claim rules", "emit packet templates", "prevent packet bloat", "routable owner-facing work tier", "packet registry"),
    loop_row("Governance fiber derivation", "expand packets into `256` governance fibers", "bind fibers to owner surfaces and legality classes", "register fiber slots", "prune unsurfaced fibers", "governance depth layer", "fiber registry"),
    loop_row("Active seat derivation", "expand fibers into `1024` active synaptic seats", "define activation and dormancy rules", "mark only seeded seats active", "strip theatrical over-activation claims", "real working seat layer", "activation map"),
    loop_row("Atlas seat derivation", "expand active seats into `4096` atlas seats", "restrict them to manifest/runtime-only depth", "compile atlas registry", "prevent board explosion", "full coordinate-able depth", "atlas registry"),
    loop_row("Quest-emission templates", "compare Hall and Temple quest requirements", "standardize quest node shapes and statuses", "emit dual-lane templates", "merge duplicate quest syntax", "deterministic quest generation", "quest-template bundle"),
    loop_row("Shared loop receipt", "determine minimum proof required per loop", "define reassessment windows and restart seed rules", "emit receipt schema", "remove vague completion language", "closeable loop contract", "loop-receipt schema"),
    loop_row("Planner law", "identify how synthesis becomes a plan without loss", "define planner inputs, outputs, and ranking rules", "bind planner to dual quest generation", "strip plan drift and duplication", "reliable planning membrane", "planner-law entry"),
    loop_row("Researcher law", "formalize evidence scan and witness ranking", "define intake order and contradiction handling", "assign researcher witness pack structure", "merge repeated synthesis summaries", "disciplined research layer", "witness-pack schema"),
    loop_row("Worker law", "determine bounded-execution rules", "define quest pull order and stop conditions", "bind worker packets to Hall/Temple dependencies", "cut unbounded execution claims", "safe implementation lane", "execution-law register"),
    loop_row("Pruner law", "determine what counts as removable, mergeable, or compressible", "define no-witness-loss rules", "bind prune packets to structure and routing surfaces", "retire dead aliases and duplicates", "lawful defrag lane", "prune-law register"),
    loop_row("Certificate and legality binding", "identify where conversion or rewrite can lose law", "attach `RoundTripCertificate_v0` and legality gates to every agent", "add certification checkpoints to outputs", "remove uncertified transformation paths", "trustworthy transformations", "certification matrix"),
    loop_row("Runtime verification", "locate runtime or count-bearing gates", "bind verifiers into loop closure", "add proof requirements to worker and pruner exits", "remove unverifiable completion claims", "proof-backed progress", "verifier index"),
    loop_row("Carrythrough logic", "inspect restart and active-front drift", "define how every agent preserves fronts and restart seeds", "attach carrythrough fields to loop artifacts", "prune restart ambiguity", "stable cross-loop continuity", "carrythrough ledger"),
    loop_row("Writeback law", "inspect change feed, requests, quest board, queue, and restart surfaces", "define exact writeback order per loop", "map each output to a surface", "merge duplicated board updates", "deterministic outward state", "writeback map"),
    loop_row("Budget integration", "surface where build energy is wasted", "attach `EconomySalienceBudget` to ranking and execution", "score quests and seats by leverage", "strip low-yield noise", "energy-aware prioritization", "budget ledger"),
    loop_row("Hybrid-equation integration", "identify bridgeable discrete/continuous or symbolic/operational gaps", "choose where hybrid equations resolve them", "schedule bridge inserts", "remove redundant hybrid prose", "stronger cross-domain law", "hybrid equation map"),
    loop_row("MATH reservoir binding", "locate mathematical kernels across corpus", "assign them to planner macro quest families", "inject math-linked quest branches", "merge scattered math mentions into routeable bundles", "math-aware planning", "math reservoir graph"),
    loop_row("Algorithmic scoring", "identify where benchmark and validator patterns can formalize research quality", "define scoring heuristics", "add algorithmic witness scoring to research packets", "remove hand-wavy evidence weighting", "measurable research quality", "scoring registry"),
    loop_row("Worker transport law", "inspect route, adjacency, transport, and proof dependencies", "encode them into implementation packets", "bind worker packets to transport constraints", "prune route-ignorant tasks", "implementation coherence", "transport law map"),
    loop_row("Pruner compression law", "identify metallic-depth compression opportunities", "define when to reduce, merge, fold, or zero-point", "bind these choices to prune packets", "compress repetitive doctrine at scale", "high-density corpus structure", "compression decision table"),
    loop_row("Quest family expansion", "identify missing Hall and Temple quest families for math, hybrid equations, algorithms, validators, and routes", "standardize family hierarchy", "emit quest families", "merge overlapping quest branches", "richer but organized work intake", "quest-family atlas"),
    loop_row("Equation-to-operation crosswalk", "gather symbolic structures that need operational translation", "define a corpus-wide crosswalk", "bind the crosswalk into planner and worker packets", "remove disconnected symbolic fragments", "tighter theory-to-action channel", "equation-operation crosswalk"),
    loop_row("Athena Prime note", "locate orchestration fractures and restart incoherence", "define the Prime transition assist", "write the Prime note into live surfaces", "strip duplicate coordination slogans", "non-fragmenting supervision", "Prime note receipt"),
    loop_row("Water note", "locate continuity, memory, and blocker-honesty gaps", "define Water stabilization rules", "bind the Water note into replay and queue surfaces", "remove continuity drift", "reliable memory corridor", "Water note receipt"),
    loop_row("Earth note", "locate legality, manifest, quarantine, and re-entry gaps", "define Earth admissibility rules", "write the Earth note into contract and governance surfaces", "strip unsafe re-entry claims", "lawful stability", "Earth note receipt"),
    loop_row("Fire note", "locate activation, ignition, and execution-energy gaps", "define bounded activation rules", "bind the Fire note into worker and runtime lanes", "remove theatrical scaling", "disciplined execution heat", "Fire note receipt"),
    loop_row("Air note", "locate naming, routing, topology, and symbolic guardrail gaps", "define Air route hygiene", "write the Air note into routing and control surfaces", "prune naming ambiguity", "crisp navigation layer", "Air note receipt"),
    loop_row("Anchor binding", "validate `Ch12/Ch13/Ch16/AppH/AppI/AppM/AppQ` as canonical anchors", "bind all five notes to these anchors", "cross-link notes into anchor corridors", "remove side-route anchor drift", "one transition spine", "anchor map"),
    loop_row("Note mirroring", "inspect Hall, Temple, manifests, family tensor, queue, restart, and registries", "define where each note must appear", "mirror notes across all required surfaces", "deduplicate note variants", "stable multi-surface guidance", "note-distribution ledger"),
    loop_row("Note cadence", "formalize note rotation across 57 loops", "assign repeating `Prime -> Water -> Earth -> Fire -> Air`", "stamp each loop with its dominant note while preserving all five as background guidance", "remove cadence ambiguity", "predictable liminal support", "note-cadence register"),
    loop_row("Q42 integration", "re-evaluate how the new conductor traverses Q42", "define non-reopening rule for the closed Hall-local QS64 bundle", "bind all four agents to carried-witness mode on Q42", "remove latent successor pressure", "lawful Hall feeder use", "Q42 integration receipt"),
    loop_row("TQ04 integration", "inspect deeper-receiver handoff through the helical runner contract", "route quartet outputs into TQ04 as downstream receiver only", "tag relevant quests and packets with Temple handoff metadata", "remove Hall/Temple conflation", "clean downward handoff", "TQ04 handoff map"),
    loop_row("Q46 integration", "inspect reserve or promoted fire frontier use", "define how Q46 remains separate from Q42", "bind reserve-facing packets", "prune false collapse into the Hall lane", "distinct reserve frontier", "Q46 reserve map"),
    loop_row("Q50 integration", "inspect runtime helix pressure lane", "separate runtime execution from Hall/Temple macro governance", "route applicable worker packets to Q50", "remove runtime/Hall blending", "distinct runtime frontier", "Q50 route map"),
    loop_row("Chapter/appendix propagation", "identify lower-weight chapter, appendix, and capsule surfaces needing quartet outputs", "rank propagation order", "assign chapter and appendix packets", "merge diffuse propagation targets", "contraction tissue spread", "chapter/appendix propagation map"),
    loop_row("Knowledge Fabric propagation", "inspect Knowledge Fabric, structured neuron storage, Grand Central, and inter-metro routing", "define propagation corridor", "emit cross-substrate packets", "prune substrate duplication", "substrate-wide integration", "substrate propagation ledger"),
    loop_row("Family registry propagation", "inspect neglected-bridge set and family registry gaps", "define repair order", "stamp quartet outputs into family registry repair quests", "merge redundant bridge repairs", "healthier whole-corpus registry", "bridge-repair map"),
    loop_row("Closure sweep", "re-scan the full modified corpus for bloat, drift, duplication, and unresolved path noise", "choose final sweep targets", "issue last prune packets", "run corpus-wide compression and defrag sweep", "tightened, lower-entropy corpus", "closure-sweep receipt"),
    loop_row("Master receipt and restart", "synthesize the fully transformed corpus state", "emit the next lawful packet and fiber execution seed", "publish one synchronized Hall, Temple, manifest, and runtime receipt", "compress the 57-loop history into a durable restart bundle", "closeable, restart-safe liminal hive", "master receipt plus successor seed"),
]

CANONICAL_LOOP_TITLES = [
    "Prime Lock",
    "Whole-Corpus Census",
    "Authority Spine Map",
    "Witness Hierarchy Map",
    "Canonical 16-Basis Ownership",
    "Pair-Matrix Priority Scan",
    "Observer Gap Ledger",
    "Symmetry Audit",
    "Metro-Appendix Crosswalk",
    "Family Registry Regrade",
    "Historical Mirror Separation",
    "Hall Macro Front Canonization",
    "Temple Macro Front Canonization",
    "Queue and Runtime Seam Normalization",
    "Six-Axis to 12D Projection Install",
    "Agent Identity Registry Install",
    "Ledger Schema Install",
    "Quest Packet Schema Alignment",
    "Quadrant Binary Foundation Bridge",
    "Voynich Translation Bridge",
    "Math Kernel Bridge",
    "ORGIN and Identity Return Corridor",
    "Athena Fleet Docking",
    "Archive and Zip Witness Unification",
    "Support Infrastructure and Docs Ingress Prep",
    "Pair-Cell Bridge Wave 1",
    "Pair-Cell Bridge Wave 2",
    "Pair-Cell Bridge Wave 3",
    "Hybrid Equation Insertion Wave",
    "Algorithm Scaffold Insertion Wave",
    "Hall Quest Burst",
    "Temple Quest Burst",
    "Worker Implementation Wave 1",
    "Worker Implementation Wave 2",
    "Runtime Waist Hardening",
    "Registry and Atlas Synchronization",
    "Knowledge Fabric and Dashboard Sync",
    "Level 1 Core Metro Refresh",
    "Level 2 Deep Emergence Metro Refresh",
    "Level 3 Neural Corridor Refresh",
    "Level 4 Transcendence Overlay Refresh",
    "Appendix Q and Crystal Support Refresh",
    "Redundancy and Stale-Front Prune",
    "Naming and Index Tightening",
    "Route Compression and Redirect Law",
    "Reserve-Thin Densification",
    "AP6D Prime Assistance Pass",
    "AP6D Elemental Assistance Pass",
    "Commander and General Derivation",
    "Hybrid and Archetype Derivation",
    "Contradiction Packet and Unresolved Gate Pass",
    "Replay and Receipt Audit",
    "Failed Branch Kill and Reseed",
    "Whole-Corpus Resynthesis",
    "Canon Convergence Across Surfaces",
    "Crown Frontier and Highest-Yield Weave",
    "Restart Packet and Canon Freeze",
]


def build_loop_table() -> list[dict[str, Any]]:
    loops: list[dict[str, Any]] = []
    gate = docs_gate_payload()["status"]
    for index, spec in enumerate(LOOP_PLAN, start=1):
        loop_id = f"L{index:02d}"
        next_loop_id = f"L{index + 1:02d}" if index < len(LOOP_PLAN) else "NEXT"
        title = CANONICAL_LOOP_TITLES[index - 1]
        next_focus = CANONICAL_LOOP_TITLES[index] if index < len(LOOP_PLAN) else "Prime Lock"
        branch_path = make_branch_path(index // 10, index % 10, 0, 1)
        loops.append(
            {
                "loop_index": index,
                "loop_number": loop_id,
                "dominant_focus": title,
                "primary_synthesis_objective": spec["primary_synthesis_objective"],
                "primary_planning_objective": spec["primary_planning_objective"],
                "primary_implementation_objective": spec["primary_implementation_objective"],
                "primary_compression_pruning_objective": spec["primary_compression_pruning_objective"],
                "expected_structural_gain": spec["expected_structural_gain"],
                "expected_mapping_ledger_gain": spec["expected_mapping_ledger_gain"],
                "restart_seed": f"{next_loop_id} -> {next_focus}",
                "loop_packet_agent_id_tag": make_agent_id_tag(loop_id, "A2", 1, branch_path, "LOOP-PACKET"),
                "liminal_coordinate_12d": make_liminal_coordinate(
                    document_region="corpus:athena",
                    concept_cluster=f"loop:{title}",
                    recursion_depth="D1",
                    temporal_layer=loop_id,
                    operation_class="hall+temple+runtime+prune",
                    active_lens="prime-cycle",
                    compression_state="planned",
                    framework_surface="lp57omega-protocol",
                    manuscript_branch=branch_path,
                    return_path="hall/temple/runtime/ledger",
                    hierarchy_level="loop-packet",
                    zero_relation="truth:LOCAL_ONLY" if gate == "BLOCKED" else "truth:LIVE",
                ),
                "framework_lookup_addr": make_lookup_addr("loops", loop_id, title.replace(" ", "_")),
            }
        )
    return loops


def liminal_identity_standard() -> dict[str, Any]:
    return {
        "format": "[LoopID].[MasterAgentID].[NestedDepth].[BranchPath].[RoleTag]",
        "examples": [
            "L07.A2.D4.B0312.PLANNER-SUB",
            "L21.A4.D6.B3321.PRUNE-CRYSTAL",
            "L57.A1.D2.B0013.SYNTH-RESEARCH",
        ],
        "law": "Every master packet, nested packet, frontier, unresolved issue, and compression node must carry an LP-57Omega identity tag.",
    }


def coordinate_schema_12d() -> dict[str, Any]:
    return {
        "axes": COORDINATE_AXIS_MEANINGS,
        "ordered_axis_names": ["Xs", "Ys", "Zs", "Ts", "Qs", "Rs", "Cs", "Fs", "Ms", "Ns", "Hs", "OmegaS"],
        "lookup_law": "Every touched idea, section, bridge, unresolved issue, and compression node gets a stable lookup address plus a 12D liminal coordinate.",
        "sample_coordinate": make_liminal_coordinate(
            document_region="ROOT-ATHENA",
            concept_cluster="LP-57Omega seed",
            recursion_depth="D6",
            temporal_layer="L01",
            operation_class="synthesis",
            active_lens="prime-cycle",
            compression_state="raw",
            framework_surface="manifest",
            manuscript_branch="B111111",
            return_path="ledger",
            hierarchy_level="nested-seat",
            zero_relation="truth:LOCAL_ONLY",
        ),
    }


def ledger_schema() -> dict[str, Any]:
    return {
        "required_fields": LEDGER_FIELDS,
        "continuity_law": "Every change appends to ledger memory; nothing is silently erased, and unresolveds must be passed forward explicitly.",
        "sample_entry": {
            "agent_id": "L01.A1.D6.B111111.SYNTH-RESEARCH",
            "loop_number": "L01",
            "parent_agent": "A1",
            "coordinate_stamp": make_liminal_coordinate(
                document_region="ROOT-ATHENA",
                concept_cluster="Docs truth freeze",
                recursion_depth="D6",
                temporal_layer="L01",
                operation_class="synthesis",
                active_lens="prime-cycle",
                compression_state="raw",
                framework_surface="manifest",
                manuscript_branch="B111111",
                return_path="ledger",
                hierarchy_level="nested-seat",
                zero_relation="truth:LOCAL_ONLY",
            ),
            "source_region": rel(LIVE_DOCS_GATE_PATH),
            "action_type": "gate-check",
            "affected_nodes": ["Q41 / TQ06", "Q42", "TQ04", "Q46", "Q50", "Q02"],
            "summary_of_change": "Confirmed local-only law because Google Docs OAuth files are missing.",
            "reason_for_change": "LP-57Omega requires blocker honesty before any synthesis or quest emission.",
            "integration_gain": "one shared blocker truth across Hall, Temple, runtime, and manifests",
            "compression_gain": "removed false live-doc assumptions",
            "unresolved_followups": ["install OAuth files to lift the Docs gate"],
            "linked_quests": ["L01 Docs truth freeze"],
            "linked_agents": ["A1", "A2"],
            "revision_confidence": "HIGH",
            "timestamp_internal": DATE,
        },
    }


def canonical_machine_truth_family() -> list[str]:
    return [
        rel(LP57_PROTOCOL_MD_PATH),
        rel(LP57_PROTOCOL_JSON_PATH),
        rel(LP57_DASHBOARD_MD_PATH),
        rel(LP57_VERIFY_JSON_PATH),
        rel(ACTIVE_RUN_PATH),
        rel(BUILD_QUEUE_PATH),
        rel(WHOLE_COORDINATION_PATH),
        rel(NEXT_SELF_PROMPT_PATH),
    ]


def next57_machine_truth_family() -> list[str]:
    return [
        rel(NEXT57_MANIFEST_MD_PATH),
        rel(NEXT57_STATE_JSON_PATH),
        rel(NEXT57_SEAT_REGISTRY_PATH),
        rel(NEXT57_QUEST_PACKETS_PATH),
        rel(NEXT57_AWAKENING_NOTES_PATH),
        rel(NEXT57_COMPATIBILITY_REGISTRY_PATH),
        rel(NEXT57_VERIFY_JSON_PATH),
        rel(CANONICAL_PROTOCOL_MD_PATH),
        rel(CANONICAL_PROTOCOL_JSON_PATH),
    ]


def protocol_reference() -> dict[str, str]:
    return {
        "protocol_id": PROTOCOL_ID,
        "program_id": PROGRAM_ID,
        "canonical_manuscript_path": rel(CANONICAL_PROTOCOL_MD_PATH),
        "canonical_json_path": rel(CANONICAL_PROTOCOL_JSON_PATH),
        "dashboard_path": rel(CANONICAL_PROTOCOL_DASHBOARD_PATH),
        "operational_manifest_path": rel(NEXT57_MANIFEST_MD_PATH),
        "active_membrane": ACTIVE_MEMBRANE,
        "canonical_authority": LIVE_HALL_FRONT,
        "hall_feeder": PRESERVED_FEEDERS[0],
        "temple_receiver": TEMPLE_HANDOFF,
        "live_hall_front": LIVE_HALL_FRONT,
        "live_temple_front": LIVE_TEMPLE_FRONT,
        "carried_witness": CARRIED_WITNESS,
        "closed_local_proof": CLOSED_LOCAL_PROOF,
        "next_hall_seed": NEXT_HALL_SEED,
        "runtime_seed": RUNTIME_SEED,
        "blocked_external_front": BLOCKED_FRONTS[0],
    }
