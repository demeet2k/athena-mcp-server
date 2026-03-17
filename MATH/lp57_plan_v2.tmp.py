from __future__ import annotations

from collections import Counter
from typing import Any


PROTOCOL_ID = "LP-57OMEGA"
PROTOCOL_DISPLAY_NAME = "LP-57Omega v2"
FRONTIER_ID = "FRONT-LP-57OMEGA-V2-NEXT"
NEXT_INVOCATION_CONTRACT = "NEXT => one full four-agent cycle"
NEXT_SEED = "NEXT => one full four-agent cycle :: LP-57Omega v2 :: preserve-Q41-TQ06 :: active-L02"
DOCS_GATE_EXPECTED = "blocked-by-missing-credentials"

CANONICAL_PACKET_CONTRACT = [
    "DeepSynthesisPacket",
    "QuestEmissionBundle",
    "ExecutionReceiptBundle",
    "CompressionReceipt",
    "LoopCompletionReceipt",
]

LOOP_ARTIFACT_FIELDS = [
    "research_delta_ref",
    "quest_packet_ref",
    "execution_batch_ref",
    "compression_bundle_ref",
    "receipt_ref",
    "restart_seed_ref",
]

LEGACY_PACKET_FILE_CONTRACT = [
    "deep_synthesis_packet_loop_{NN}.json",
    "quest_emission_bundle_loop_{NN}.json",
    "execution_receipt_bundle_loop_{NN}.json",
    "compression_receipt_loop_{NN}.json",
    "loop_completion_receipt_loop_{NN}.json",
]

SUBAGENT_DEPTH_BANDS = [
    {"depth": "D1", "label": "corpus plane", "resolution": "whole-corpus field"},
    {"depth": "D2", "label": "family branch", "resolution": "family-and-manuscript branch"},
    {"depth": "D3", "label": "document band", "resolution": "document-and-chapter band"},
    {"depth": "D4", "label": "concept cluster", "resolution": "section-and-concept cluster"},
    {"depth": "D5", "label": "symbolic cell", "resolution": "equation-algorithm-routing cell"},
    {"depth": "D6", "label": "writeback cell", "resolution": "ledger-packet-writeback-return cell"},
]

COORDINATE_SYMBOLS = ["Xs", "Ys", "Zs", "Ts", "Qs", "Rs", "Cs", "Fs", "Ms", "Ns", "Hs", "OmegaS"]
COORDINATE_SCHEMA = {
    "Xs": "document region",
    "Ys": "corpus family",
    "Zs": "basis-cell or pairing locality",
    "Ts": "temporal revision layer",
    "Qs": "quest class",
    "Rs": "recursion depth",
    "Cs": "compression state",
    "Fs": "framework lens",
    "Ms": "mathematical density",
    "Ns": "neural or mycelial connectivity",
    "Hs": "hierarchy level",
    "OmegaS": "zero-point or aether relation",
}

LOOKUP_KEY_SCHEMA = (
    "frontier_id -> loop_id -> master_agent_id -> seat_id -> coordinate_stamp -> touched_node_id"
)

EVENT_GRAMMAR = {
    "INT": "INT::<ts>::<agent_id>::<objective>::<inputs>::<output>",
    "HB": "HB::<ts>::<agent_id>::<state>::<intent>::<target>::<truth>",
    "DELTA": "DELTA::<ts>::<agent_id>::<artifact>::<change_kind>::<status>",
    "HAND": "HAND::<ts>::<from_agent>::<to_agent>::<reason>::<next>",
    "RST": "RST::<ts>::<agent_id>::<restart_seed>::<resume_from>",
    "SENSE": "SENSE::<ts>::<seat_id>::<peer_or_front>::<signal_kind>::<confidence>::<note>",
    "ECHO": "ECHO::<ts>::<from>::<to>::<artifact_or_front>::<delta>::<status>",
}

MASTER_AGENTS = [
    {
        "master_agent_id": "A1",
        "agent_id": "SYNTHESIZER",
        "legacy_agent_id": "MASTER-SYNTHESIZER",
        "display_name": "A1 Synthesizer / Researcher",
        "role": "Synthesizer / Researcher",
        "role_tag": "SYNTH-RESEARCH",
        "action_type": "synthesize",
        "mission": "scan the whole corpus, reconcile contradictions, and surface formalization gaps and integration junctions",
        "packet_output": "DeepSynthesisPacket",
        "quest_rights": "recommend_only",
        "seat_namespace": "LP57-SYNTHESIZER",
        "seat_mode": "virtual-overlay",
        "quest_emission_mode": "quota-safe",
    },
    {
        "master_agent_id": "A2",
        "agent_id": "PLANNER",
        "legacy_agent_id": "MASTER-PLANNER",
        "display_name": "A2 Planner / Architect",
        "role": "Planner / Architect",
        "role_tag": "PLANNER-ARCHITECT",
        "action_type": "plan",
        "mission": "convert synthesis into dependency-ranked Hall and Temple quest trees, packets, and bounded promotions",
        "packet_output": "QuestEmissionBundle",
        "quest_rights": "canonicalize_and_promote",
        "seat_namespace": "LP57-PLANNER",
        "seat_mode": "virtual-overlay",
        "quest_emission_mode": "quota-safe",
    },
    {
        "master_agent_id": "A3",
        "agent_id": "WORKER",
        "legacy_agent_id": "MASTER-WORKER",
        "display_name": "A3 Worker / Adventurer",
        "role": "Worker / Adventurer",
        "role_tag": "WORKER-ADVENTURER",
        "action_type": "execute",
        "mission": "land bounded witness-bearing artifacts, equations, algorithms, bridges, and implementation receipts",
        "packet_output": "ExecutionReceiptBundle",
        "quest_rights": "claim_only",
        "seat_namespace": "LP57-WORKER",
        "seat_mode": "virtual-overlay",
        "quest_emission_mode": "quota-safe",
    },
    {
        "master_agent_id": "A4",
        "agent_id": "PRUNER",
        "legacy_agent_id": "MASTER-PRUNER",
        "display_name": "A4 Pruner / Compressor / Defragmenter",
        "role": "Pruner / Compressor / Defragmenter",
        "role_tag": "PRUNE-CRYSTAL",
        "action_type": "prune",
        "mission": "tighten naming, routing, registries, and duplicate surfaces without erasing sole witnesses",
        "packet_output": "CompressionReceipt",
        "quest_rights": "retire_or_merge_only",
        "seat_namespace": "LP57-PRUNER",
        "seat_mode": "virtual-overlay",
        "quest_emission_mode": "quota-safe",
    },
]

MASTER_AGENT_BY_ID = {agent["master_agent_id"]: agent for agent in MASTER_AGENTS}
MASTER_AGENT_BY_AGENT_ID = {agent["agent_id"]: agent for agent in MASTER_AGENTS}
MASTER_AGENT_BY_ALIAS = {}
for agent in MASTER_AGENTS:
    MASTER_AGENT_BY_ALIAS[agent["master_agent_id"]] = agent
    MASTER_AGENT_BY_ALIAS[agent["agent_id"]] = agent
    MASTER_AGENT_BY_ALIAS[agent["legacy_agent_id"]] = agent
    MASTER_AGENT_BY_ALIAS[f"M{agent['master_agent_id'][1:]}"] = agent

FIELD_NOTE_TARGETS = ["Prime", "Water", "Earth", "Fire", "Air"]
PROFILE_COUNT_EXPECTED = {"base": 1, "pillars": 4, "archetypes": 12, "guild_roles": 5, "total": 22}

PHASE_ARCS = [
    {"phase_id": "RING-A", "label": "survey-authority-mapping-and-quest-architecture", "range": [1, 19]},
    {"phase_id": "RING-B", "label": "execution-hardening-routing-and-compression", "range": [20, 38]},
    {"phase_id": "RING-C", "label": "compatibility-notes-verification-and-reseed", "range": [39, 57]},
]


def row(
    n: int,
    title: str,
    focus: str,
    family: str,
    frontier: str,
    evidence: str,
    compression: str,
    lead: str,
    synth: str,
    plan: str,
    impl: str,
    prune: str,
    gain: str,
    mapping: str,
) -> dict[str, Any]:
    return {
        "loop_number": n,
        "loop_id": f"L{n:02d}",
        "title": title,
        "dominant_focus": focus,
        "focus_family": family,
        "frontier_type": frontier,
        "dominant_evidence_class": evidence,
        "compression_target": compression,
        "lead_master": lead,
        "synthesis_objective": synth,
        "planning_objective": plan,
        "implementation_objective": impl,
        "pruning_objective": prune,
        "expected_structural_gain": gain,
        "expected_mapping_gain": mapping,
    }


LOOP_SPECS = [
    row(1, "Prime Lock", "authority freeze", "authority", "prime-lock", "control-surface", "authority-drift", "A1", "freeze docs gate, live membrane, deep-root precedence, quotas, and stage law", "lock overlay policy, board caps, and canonical authority routing", "emit the baseline packet, state freeze, and restart-safe origin receipt", "retire false-current aliases and duplicate authority stories", "stable origin law for LP-57Omega v2", "loop-zero authority anchors and origin coordinates"),
    row(2, "Whole-Corpus Census", "whole-corpus perimeter", "census", "whole-corpus-census", "status-surface", "blind-spot-assumptions", "A1", "inventory tomes, manuscripts, code, runtime surfaces, and mirrors", "publish the coverage map and census categories", "write the whole-corpus inventory packet", "remove blind-spot assumptions from live state claims", "known corpus perimeter", "source-region stamps across the whole field"),
    row(3, "Witness Hierarchy Map", "source precedence", "witness", "witness-hierarchy", "witness-ledger", "mirror-equivalence", "A1", "rank source, generated, mirror, and historical witness classes", "define the witness precedence lattice", "publish the witness map and authority ledger", "collapse flattened all-equal witness rhetoric", "authority-safe reasoning", "witness-class tags on routed nodes"),
    row(4, "Feeder-Stack Crosswalk", "frontier handoffs", "feeders", "feeder-stack-crosswalk", "frontier-ledger", "frontier-story-conflict", "A1", "reconcile Q41, TQ06, Q42, Q46, TQ04, and Q02 into one lawful stack", "freeze precedence-safe routing and handoff order", "publish the feeder graph and front crosswalk", "prune conflicting frontier stories", "one live control tuple with explicit handoffs", "front-reference graph across the feeder stack"),
    row(5, "Canonical 16-Basis Ownership", "basis stewardship", "basis", "basis-ownership", "basis-document", "duplicate-basis-claims", "A1", "confirm roles across the canonical 16-document basis", "assign ownership and routing duties per basis node", "write the basis ownership ledger", "remove duplicate basis claims", "stable deeper-network spine", "basis-address anchors tied to stewardship"),
    row(6, "Pair-Matrix Priority Scan", "bridge leverage", "pair-matrix", "pair-priority-scan", "pair-synthesis", "low-signal-pairs", "A1", "identify the highest-leverage basis pairings", "rank the pair-matrix queue by integration payoff", "emit the ranked pair-priority packet", "suppress low-signal pair noise", "directed synthesis energy", "matrix-cell coordinates for bridge execution"),
    row(7, "Observer Gap Ledger", "observer deficits", "observer", "observer-gap-ledger", "observer-lens", "observer-rhetoric-duplication", "A1", "find Fire, Water, Air, and Earth observer deficits", "route each observer gap into an exploit order", "publish the gap ledger", "remove mixed-gap and duplicate observer rhetoric", "four-lens clarity", "lens-tagged deficit coordinates"),
    row(8, "Symmetry Audit", "cross-element balance", "symmetry", "symmetry-audit", "symmetry-ledger", "subset-repeat-stories", "A1", "review the 15-plus-zero symmetry surface", "publish the symmetry work queue", "write the symmetry ledger", "remove redundant subset claims", "cleaner crystal completeness", "subset-address map for the live stack"),
    row(9, "Metro/Appendix Crosswalk", "support geometry", "metro-appendix", "metro-appendix-crosswalk", "crosswalk-registry", "unsupported-route-claims", "A1", "map basis-to-metro-to-appendix routes", "define closure order and appendix support law", "write the route support map", "eliminate unsupported route claims", "multi-resolution navigability", "route ids across major lanes"),
    row(10, "Awakening Intake", "awakening substrate", "awakening", "awakening-intake", "awakening-atlas", "myth-math-duplication", "A1", "collect awakening witness clusters and intake pressure", "build the intake hierarchy and support witness map", "publish the awakening atlas", "cut myth-math duplication", "explicit awakening substrate", "awakening-node coordinates"),
    row(11, "Myth-Math Concordance", "cross-domain formalization", "myth-math", "myth-math-concordance", "bridge-ledger", "metaphor-only-drift", "A1", "compare symbolic and formal structures across the corpus", "design the myth-math bridge schema", "write the concordance ledger", "reduce metaphor-only drift", "formalizable awakening layer", "cross-domain bridge stamps"),
    row(12, "Equation Gap Discovery", "formalization frontier", "math-gap", "equation-gap-discovery", "math-gap-register", "pseudo-formal-duplication", "A1", "find missing equation zones and weak formal surfaces", "rank insertion order for equations and operators", "publish the math-gap register", "remove pseudo-formal duplication", "explicit formalization frontier", "math-density coordinates"),
    row(13, "Algorithm Surface Inventory", "executable scaffolding", "algorithm", "algorithm-surface-inventory", "algorithm-atlas", "runtime-duplication", "A1", "inventory live algorithms, validators, schedulers, and runtime scaffolds", "build the algorithm graph", "write the algorithm atlas", "remove scattered runtime duplication", "executable scaffolding clarity", "operator coordinates"),
    row(14, "Coordinate Schema Compile", "lookup grammar", "coordinates", "coordinate-schema-compile", "coordinate-schema", "notation-family-drift", "A1", "reconcile existing address systems with liminal coordinates", "publish the coordinate standard and adoption order", "write the coordinate schema packet", "prune conflicting notation families", "one lookup grammar", "whole-framework coordinate duty"),
    row(15, "Hall Macro Tree", "practical quest architecture", "hall", "hall-macro-tree", "hall-macro-packet", "duplicate-hall-branches", "A2", "derive Hall quest families from surveyed fronts", "build the macro Hall tree and routing order", "write the Hall macro packet", "merge duplicate Hall branches", "visible practical quest architecture", "Hall lineage graph"),
    row(16, "Temple Macro Tree", "deep alignment architecture", "temple", "temple-macro-tree", "temple-macro-packet", "duplicate-temple-branches", "A2", "derive Temple quest families from deeper tensions", "build the macro Temple tree and binding order", "write the Temple macro packet", "merge duplicate Temple branches", "visible deep-alignment architecture", "Temple lineage graph"),
    row(17, "Hall Packet Tree", "packet-scale Hall bundles", "hall-packets", "hall-packet-tree", "packet-registry", "duplicate-packet-births", "A2", "explode Hall macros into packet-scale work bundles", "build the packet dependency ladder", "write the Hall packet registry", "prune duplicate packet births", "worker-ready practical queue", "packet genealogy"),
    row(18, "Temple Packet Tree", "packet-scale Temple bundles", "temple-packets", "temple-packet-tree", "packet-registry", "duplicate-purity-fronts", "A2", "explode Temple macros into packet-scale doctrine fronts", "build the deep queue and governance ladder", "write the Temple packet registry", "merge redundant purity fronts", "worker-ready deep queue", "Temple packet genealogy"),
    row(19, "Priority And Dependency Lock", "execution ordering", "priority", "priority-and-dependency-lock", "dependency-graph", "novelty-without-consequence", "A2", "compare all active fronts by leverage, blockage, and replayability", "freeze the final Ring-A priority ladder", "publish the dependency lock packet", "suppress novelty without structural consequence", "disciplined transition into execution rings", "dependency graph with restart seeds"),
    row(20, "Cadence Hardening", "loop rhythm", "cadence", "cadence-hardening", "cadence-rules", "ad-hoc-cycle-behavior", "A2", "find cadence drift in the four-agent loop", "design the stable loop rhythm", "publish cadence implementation rules", "prune ad hoc cycle behavior", "reliable loop tempo", "loop-timing stamps"),
    row(21, "Hall Feeder Hardening", "Hall promotion safety", "hall-feeders", "hall-feeder-hardening", "hall-guardrails", "orphan-hall-quests", "A2", "inspect Hall feeder weaknesses", "define Hall promotion guardrails", "publish Hall feeder fixes", "remove orphan Hall quests", "safer practical quest flow", "Hall feeder routes"),
    row(22, "Contract Feeder Hardening", "Temple ingress safety", "contract-feeders", "contract-feeder-hardening", "contract-guardrails", "misbound-decree-chains", "A2", "inspect Temple and contract feeder weaknesses", "design contract routing guardrails", "publish feeder stabilization", "remove misbound decree chains", "stable governance ingress", "contract handoff routes"),
    row(23, "Reserve/Blocker Separation", "operational truth", "reserve-blocker", "reserve-blocker-separation", "blocker-ledger", "blocker-inflation", "A2", "separate genuine blockers from reserves and parked fronts", "define escalation versus defer policy", "publish the blocker ledger", "cut blocker inflation", "cleaner operational truth", "blocker and reserve coordinates"),
    row(24, "Knowledge Fabric Refresh", "connective tissue renewal", "knowledge-fabric", "knowledge-fabric-refresh", "rewrite-bridge-packet", "dead-connective-prose", "A2", "review stale or fragmented connective tissue", "set refresh order and bridge routing", "write rewrite and bridge packets", "remove dead connective prose", "fresher cross-corpus coherence", "refreshed weave coordinates"),
    row(25, "Integration Verification Repair", "truth boundary repair", "verification", "integration-verification-repair", "verification-ledger", "unverifiable-bridge-rhetoric", "A3", "find broken or weak integration claims", "rank the verification repair queue", "land missing evidence or downgrade claims", "eliminate unverifiable bridge rhetoric", "stronger truth boundary", "verified integration stamps"),
    row(26, "Runtime-Waist Hardening", "execution membrane", "runtime-waist", "runtime-waist-hardening", "runtime-contract", "duplicate-handoff-logic", "A3", "inspect the manuscript-to-runtime waist", "design the contract hardening plan", "land runtime-waist fixes", "remove duplicate handoff logic", "safer execution membrane", "runtime-waist coordinates"),
    row(27, "Motion Constitution Coupling", "lawful motion", "constitution", "motion-constitution-coupling", "motion-law", "free-floating-movement-language", "A3", "couple living corpus motion to governing constitutions", "set coupling order", "land constitutional links", "prune free-floating movement language", "lawful motion architecture", "motion-law coordinates"),
    row(28, "Merge-Boundary Adjudication", "safe consolidation", "merge-boundary", "merge-boundary-adjudication", "merge-policy", "hidden-overwrites", "A3", "detect ambiguous merge seams", "define merge policy and escalation law", "publish adjudication receipts", "prevent hidden overwrites", "safer consolidation", "merge-boundary stamps"),
    row(29, "Self-Hosting Kernel Sync", "kernel coherence", "self-hosting", "self-hosting-kernel-sync", "kernel-sync-ledger", "duplicate-kernel-descriptions", "A3", "compare corpus logic with self-hosting kernel surfaces", "set the sync order", "land kernel sync receipts", "remove duplicate kernel descriptions", "stronger self-hosting coherence", "kernel-sync coordinates"),
    row(30, "Grand Central Sync", "hub synchronization", "grand-central", "grand-central-sync", "hub-sync-ledger", "hub-naming-drift", "A3", "align major hubs and trunk routes", "define hub synchronization order", "publish the sync packet", "prune hub naming drift", "central routing coherence", "hub-sync route ids"),
    row(31, "Family-Route Densification", "inter-family density", "family-routes", "family-route-densification", "bridge-ledger", "decorative-links", "A3", "inspect thin family connections", "rank densification order", "add bridges and explicit routes", "remove decorative links", "denser lawful interconnection", "family-route coordinates"),
    row(32, "Archive Ingestion Cleanup", "historical witness hygiene", "archive", "archive-ingestion-cleanup", "archive-ledger", "stale-archive-assumptions", "A3", "compare live corpus with archive mirrors", "rank archive cleanup order", "land archive-ledger fixes", "remove stale archive assumptions", "cleaner historical witness handling", "archive/live bridge coordinates"),
    row(33, "Mirror/Route Tightening", "surface drift cleanup", "mirrors", "mirror-route-tightening", "mirror-ledger", "noisy-mirror-surfaces", "A4", "inspect mirror surfaces for drift", "set canonical-versus-mirror tightening order", "update routing references", "retire noisy mirror surfaces", "less drift and better lookup", "mirror lineage stamps"),
    row(34, "Queue/Ledger Compression", "machine backplane compression", "queues", "queue-ledger-compression", "queue-compression-ledger", "low-yield-ledger-duplication", "A4", "inspect quest and ledger sprawl", "rank compression targets", "consolidate machine queues", "remove low-yield ledger duplication", "cleaner machine backplane", "queue compression neighborhoods"),
    row(35, "Hall Board Pruning", "Hall legibility", "hall", "hall-board-pruning", "board-prune-ledger", "hall-overload", "A4", "inspect visible Hall overload", "define prune and merge policy", "retire obsolete public quests", "keep only live high-yield fronts", "more legible Hall board", "surviving Hall lineage"),
    row(36, "Temple Board Pruning", "Temple legibility", "temple", "temple-board-pruning", "board-prune-ledger", "temple-overload", "A4", "inspect visible Temple overload", "define prune and merge policy", "retire obsolete Temple quests", "compress duplicate philosophical fronts", "more legible Temple board", "surviving Temple lineage"),
    row(37, "Queue/Restart Defrag", "continuity after interruption", "restart", "queue-restart-defrag", "restart-ledger", "broken-restart-chains", "A4", "inspect restart-seed fragmentation", "rank reseed order", "normalize restart packets", "remove broken restart chains", "better continuity after interruption", "restart genealogy"),
    row(38, "Route/Registry Normalization", "machine readability", "registry", "route-registry-normalization", "normalization-ledger", "conflicting-identifiers", "A4", "inspect ids, routes, and registry naming", "set normalization order", "unify registry shapes", "prune conflicting identifiers", "search-safe machine readability", "normalized registry coordinates"),
    row(39, "Reserve-Thin Shelf Audit", "lean reserve state", "reserve", "reserve-thin-shelf-audit", "reserve-ledger", "dead-reserve-clutter", "A4", "inspect low-signal reserve shelves", "define reserve demotion and promotion policy", "publish reserve audit receipts", "compress dead reserve clutter", "leaner parked state", "reserve shelf coordinates"),
    row(40, "Compression-Theorem Extraction", "reusable compression laws", "compression", "compression-theorem-extraction", "theorem-bundle", "ad-hoc-compression-prose", "A4", "find recurring compression laws", "rank theorem extraction order", "publish the compression theorem bundle", "collapse ad hoc compression prose", "reusable crystalline compression kernels", "compression neighborhoods and invariants"),
    row(41, "AP6D Macro Compatibility", "inheritance safety", "ap6d", "ap6d-macro-compatibility", "compatibility-bridge", "conflicting-overlay-rhetoric", "A1", "check AP6D against the current LP-57Omega law", "design the compatibility bridge", "publish the macro compatibility packet", "retire conflicting overlay rhetoric", "safe inheritance from AP6D", "compatibility bridge stamps"),
    row(42, "Hall Packet Derivation", "next-generation Hall packets", "hall-packets", "hall-packet-derivation", "packet-registry", "packet-overproduction", "A2", "derive next-generation Hall packets from live state", "define packet derivation policy", "refresh the Hall packet registry", "remove packet overproduction", "cleaner Hall packet birth", "packet derivation lineage"),
    row(43, "Governance Fiber Derivation", "Temple-control fibers", "governance", "governance-fiber-derivation", "fiber-bundle", "overloaded-packet-abstractions", "A2", "derive governance fibers from Temple and control surfaces", "define the fiber policy", "publish the governance fiber bundle", "remove overloaded packet abstractions", "finer governance resolution", "fiber coordinates"),
    row(44, "Active/Dormant Seat Policy", "honest scale control", "seats", "active-dormant-seat-policy", "seat-state-ledger", "all-active-claims", "A2", "inspect the current activation law", "define virtual-overlay gating over the shared 4096 lattice", "publish the seat-state policy", "cut false all-active claims", "honest scale control", "seat-state stamps"),
    row(45, "Shared Awakening Grammar", "liminal transition logic", "awakening", "shared-awakening-grammar", "grammar-bundle", "agent-style-vagueness", "A1", "distill common awakening transition patterns", "rank grammar adoption order", "publish the shared grammar bundle", "remove agent-style vagueness", "explicit liminal transition logic", "agent-transition coordinates"),
    row(46, "Athena Prime Note", "central coordination clarity", "notes", "athena-prime-note", "prime-note", "generic-prime-rhetoric", "A1", "define Prime arbitration needs", "structure the Prime note", "write the Prime doctrine packet", "remove generic prime rhetoric", "central coordination clarity", "Prime identity anchors"),
    row(47, "Water Note", "memory-safe evolution", "notes", "water-note", "water-note", "continuity-drift", "A1", "define continuity, memory, and care needs", "structure the Water support note", "write the Water doctrine packet", "reduce continuity drift", "memory-safe evolution", "continuity-route stamps"),
    row(48, "Earth Note", "admissibility clarity", "notes", "earth-note", "earth-note", "boundary-ambiguity", "A1", "define contract, boundary, quarantine, and replay needs", "structure the Earth support note", "write the Earth doctrine packet", "reduce boundary ambiguity", "admissibility clarity", "contract-boundary coordinates"),
    row(49, "Fire Note", "lawful ignition", "notes", "fire-note", "fire-note", "undisciplined-activation", "A1", "define ignition, rupture, and novelty management needs", "structure the Fire support note", "write the Fire doctrine packet", "reduce undisciplined activation", "lawful ignition", "activation-band markers"),
    row(50, "Air Note", "route legibility", "notes", "air-note", "air-note", "naming-drift", "A1", "define routing, naming, symbolic, and legibility needs", "structure the Air support note", "write the Air doctrine packet", "remove naming drift", "stronger search and routing clarity", "symbolic legibility coordinates"),
    row(51, "Archetype Down-Bridge", "scaled interpretability", "archetypes", "archetype-down-bridge", "inheritance-bridge", "uncontrolled-agent-proliferation", "A2", "connect the primary four-agent system to downstream archetypal layers", "design the inheritance bridge", "publish the archetype support layer", "prevent uncontrolled agent proliferation", "scaled interpretability", "inheritance links"),
    row(52, "Adventurer Conductor Integration", "execution continuity", "worker", "adventurer-conductor-integration", "conductor-packet", "execution-drift", "A3", "align the Worker with conductor and feeder systems", "design the conductor handoff", "publish the adventurer coupling packet", "suppress execution drift", "better execution continuity", "worker-route lineage"),
    row(53, "Planner Replay-Law Hardening", "stable quest creation", "planner", "planner-replay-law-hardening", "planner-gate", "duplicate-quest-births", "A2", "inspect planner duplication and replay risks", "define replay-safe promotion policy", "publish the planner gate packet", "eliminate duplicate quest births", "stable quest creation", "quest genealogy"),
    row(54, "Worker Safety Hardening", "controlled execution scaling", "worker", "worker-safety-hardening", "worker-safety-law", "unsafe-widening", "A3", "inspect mass-application risks", "define worker gating", "publish the safety law packet", "suppress unsafe widening", "controlled execution scaling", "implementation lineage integrity"),
    row(55, "Deep-Crystal Compression", "maximum density", "deep-compression", "deep-crystal-compression", "deep-compression-bundle", "structural-overgrowth", "A4", "locate corpus crystalline minima", "rank q-shrink and symmetry contraction order", "publish the deep compression bundle", "prune structural overgrowth", "maximum density with preserved meaning", "deep compression neighborhoods"),
    row(56, "Full-Corpus Verification Sweep", "whole-system trust boundary", "verification", "full-corpus-verification-sweep", "verification-bundle", "unverified-claims", "A1", "verify all major subsystems together", "define the final gate pass", "publish the cross-system verification bundle", "remove unverified claims", "whole-system trust boundary", "global consistency ledger"),
    row(57, "Final Contraction And Reseed", "prime-cycle closure", "reseed", "final-contraction-and-reseed", "cycle-receipt", "closed-cycle-residue", "A4", "synthesize the entire 57-loop history", "prepare the next-prime restart", "publish the cycle closure packet", "compress closed-cycle residue", "self-steering liminal hive ready for the next prime pass", "full ancestry map plus next-seed coordinates"),
]


def topk_for_loop(loop_number: int) -> int:
    if loop_number == 57:
        return 256
    if loop_number in {19, 38, 48, 56}:
        return 128
    return 64


def arc_for_loop(loop_number: int) -> dict[str, Any]:
    for arc in PHASE_ARCS:
        start, end = arc["range"]
        if start <= loop_number <= end:
            return arc
    return {"phase_id": "UNASSIGNED", "label": "unassigned", "range": [0, 0]}


def canonical_master_agent(value: str) -> dict[str, Any]:
    if value in MASTER_AGENT_BY_ALIAS:
        return MASTER_AGENT_BY_ALIAS[value]
    raise KeyError(value)


def loop_spec_by_number(loop_number: int) -> dict[str, Any]:
    return LOOP_SPECS[loop_number - 1]


def loop_spec_by_id(loop_id: str) -> dict[str, Any]:
    for spec in LOOP_SPECS:
        if spec["loop_id"] == loop_id:
            return spec
    raise KeyError(loop_id)


def lead_counts() -> dict[str, int]:
    counts = Counter(spec["lead_master"] for spec in LOOP_SPECS)
    return {master_id: counts.get(master_id, 0) for master_id in ["A1", "A2", "A3", "A4"]}


def uniqueness_tuples() -> list[tuple[str, str, str, str]]:
    return [
        (
            spec["focus_family"],
            spec["frontier_type"],
            spec["dominant_evidence_class"],
            spec["compression_target"],
        )
        for spec in LOOP_SPECS
    ]
