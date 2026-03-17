from __future__ import annotations

from collections import Counter
from typing import Any


PROTOCOL_ID = "LP-57OMEGA"
PROTOCOL_DISPLAY_NAME = "LP-57Omega v2"
FRONTIER_ID = "FRONT-LP-57OMEGA-V2-NEXT"
NEXT_INVOCATION_CONTRACT = "NEXT => one full LP-57OMEGA v2 prime-loop hive cycle"
NEXT_SEED = "L05 -> Canonical 16-Basis Ownership"
DOCS_GATE_EXPECTED = "blocked-by-missing-credentials"

CANONICAL_PACKET_CONTRACT = [
    "research_delta",
    "quest_packet",
    "execution_batch",
    "compression_bundle",
    "receipt",
    "restart_seed",
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

COORDINATE_SYMBOLS = [
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
    "OmegaS",
]
COORDINATE_DISPLAY_SYMBOLS = COORDINATE_SYMBOLS
COORDINATE_SCHEMA = {
    "Xs": "corpus body or root region",
    "Ys": "manuscript family or branch",
    "Zs": "recursion depth",
    "Ts": "loop-time layer",
    "Qs": "quest or packet lineage",
    "Rs": "resolution band",
    "Cs": "compression state",
    "Fs": "framework lens",
    "Ms": "manuscript branch",
    "Ns": "neural or mycelial route",
    "Hs": "hierarchy level",
    "OmegaS": "zero-point or aether relation",
}


EVENT_GRAMMAR = {
    "INT": "INT::<ts>::<agent_id>::<objective>::<inputs>::<output>",
    "HB": "HB::<ts>::<agent_id>::<state>::<intent>::<target>::<truth>",
    "DELTA": "DELTA::<ts>::<agent_id>::<artifact>::<change_kind>::<status>",
    "HAND": "HAND::<ts>::<from_agent>::<to_agent>::<reason>::<next>",
    "RST": "RST::<ts>::<agent_id>::<restart_seed>::<resume_from>",
    "SENSE": "SENSE::<ts>::<seat_id>::<peer_or_front>::<signal_kind>::<confidence>::<note>",
    "ECHO": "ECHO::<ts>::<from>::<to>::<artifact_or_front>::<delta>::<status>",
}
LOOKUP_KEY_SCHEMA = (
    "frontier_id -> loop_id -> master_agent_id -> seat_addr_6d -> coordinate_stamp -> touched_node_id"
)

LEDGER_SCHEMA = [
    "agent_id",
    "loop_number",
    "parent_agent",
    "seat_addr_6d",
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
    "witness_class",
    "truth_state",
]

FIELD_NOTE_TARGETS = ["Prime", "Water", "Earth", "Fire", "Air"]
PROFILE_COUNT_EXPECTED = {"base": 1, "pillars": 4, "archetypes": 12, "guild_roles": 5, "total": 22}

MASTER_AGENTS = [
    {
        "master_agent_id": "A1",
        "agent_id": "SYNTHESIZER",
        "legacy_agent_id": "MASTER-SYNTHESIZER",
        "display_name": "A1 Synthesizer / Researcher",
        "role": "Synthesizer / Researcher",
        "role_tag": "SYNTH-RESEARCH",
        "action_type": "synthesize",
        "mission": "scan the full corpus, detect hidden bridges, contradictions, mathematical upgrades, and latent integration structures",
        "packet_output": "research_delta",
        "quest_rights": "recommend_only",
        "seat_namespace": "CURRENT-DEEP-SYNTHESIS",
        "seat_mode": "role-namespaced-4096-over-shared-4096",
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
        "mission": "turn synthesis into Hall quests, Temple quests, AP6D shadow quests, Adventurer packets, and restart-safe sequencing",
        "packet_output": "quest_packet",
        "quest_rights": "canonicalize_and_promote",
        "seat_namespace": "LP57-PLANNER",
        "seat_mode": "role-namespaced-4096-over-shared-4096",
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
        "mission": "apply bounded replay-safe changes, land artifacts, install bridges, and complete writeback",
        "packet_output": "execution_batch",
        "quest_rights": "claim_only",
        "seat_namespace": "LP57-WORKER",
        "seat_mode": "role-namespaced-4096-over-shared-4096",
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
        "mission": "tighten structure, preserve witnesses, q-shrink bloat, improve routing clarity, and reseed the next loop from a cleaner corpus state",
        "packet_output": "compression_bundle",
        "quest_rights": "retire_or_merge_only",
        "seat_namespace": "LP57-PRUNER",
        "seat_mode": "role-namespaced-4096-over-shared-4096",
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

PHASE_ARCS = [
    {"phase_id": "RING-A", "label": "survey-and-exact-mapping", "range": [1, 19]},
    {"phase_id": "RING-B", "label": "integration-and-constructive-expansion", "range": [20, 38]},
    {"phase_id": "RING-C", "label": "tightening-compression-and-successor-formation", "range": [39, 57]},
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
    row(1, "Prime Lock", "authority freeze", "authority", "prime-lock", "control-surface", "authority-drift", "A1", "synthesize Docs gate, active membrane, feeder law, and deep-root precedence", "plan authority freeze, overlay policy, and canonical order", "implement the baseline master packet and origin receipt", "prune false-current aliases and duplicate authority stories", "stable start state for LP-57Omega v2", "loop-zero anchors and origin ledgers"),
    row(2, "Packet Truth Sync", "packet truth synchronization", "packet-truth", "packet-truth-sync", "packet-ledger", "seeded-loop-drift", "A1", "synthesize packet truth across the canonical loop triplet, ACTIVE_RUN, and command membrane docking while retaining Whole-Corpus Census as historical alias only", "plan activation-safe L02 promotion, alias containment, and L03 Authority Pointer Replacement reseed", "implement the L02 packet truth sync writeback across canonical loop, quest, runtime, and command surfaces", "prune seeded-only drift, alternate L02 titles, and undocked command-membrane fronts", "one active canonical loop story", "L02 command-route and packet-lineage anchors"),
    row(3, "Witness Hierarchy Map", "source precedence", "witness", "witness-hierarchy", "witness-ledger", "flattened-count-rhetoric", "A1", "synthesize source, generated, archive, and promoted witness relations", "plan the witness precedence lattice", "implement the cross-surface witness map", "prune flattened witness rhetoric", "authority-safe reasoning", "witness tags on nodes and routes"),
    row(4, "Feeder-Stack Crosswalk", "frontier handoffs", "feeders", "feeder-stack-crosswalk", "frontier-ledger", "frontier-story-conflict", "A1", "synthesize Q41, TQ06, Q42, Q46, TQ04, and Q02 into one lawful stack", "plan one precedence-safe control tuple", "implement the feeder crosswalk", "prune conflicting frontier stories", "one live routing membrane", "front-ref and feeder-route edges"),
    row(5, "Canonical 16-Basis Ownership", "basis stewardship", "basis", "basis-ownership", "basis-document", "duplicate-basis-claims", "A1", "synthesize basis-body roles across the canonical 16 basis", "plan basis owner assignment", "implement the basis ownership ledger", "prune duplicate basis claims", "stable deep-root decomposition", "basis-address anchors"),
    row(6, "Pair-Matrix Priority Scan", "bridge leverage", "pair-matrix", "pair-priority-scan", "pair-synthesis", "low-signal-pairs", "A1", "synthesize highest-leverage basis pairings", "plan a top-pair queue", "implement pair ranking", "prune low-signal pair noise", "directed synthesis energy", "matrix-cell coordinates"),
    row(7, "Observer Gap Ledger", "observer deficits", "observer", "observer-gap-ledger", "observer-lens", "mixed-gap-vagueness", "A1", "synthesize Fire, Water, Air, and Earth deficits", "plan observer exploitation order", "implement lens gap packets", "prune mixed-gap vagueness", "four-lens clarity", "observer-labeled unresolveds"),
    row(8, "Symmetry State Audit", "cross-element balance", "symmetry", "symmetry-state-audit", "symmetry-ledger", "mirror-state-duplication", "A1", "synthesize 15-plus-zero symmetry coverage", "plan missing symmetry work", "implement symmetry status receipts", "prune mirror-state duplication", "lawful symmetry awareness", "symmetry-address overlays"),
    row(9, "Metro-Appendix Crosswalk", "support geometry", "metro-appendix", "metro-appendix-crosswalk", "crosswalk-registry", "orphan-appendix-claims", "A1", "synthesize basis, matrix, metro, and appendix supports", "plan cross-resolution routing", "implement the support crosswalk", "prune orphan appendix claims", "resolution-safe navigation", "metro-to-appendix edges"),
    row(10, "Coordinate Field Baseline", "lookup grammar", "coordinates", "coordinate-field-baseline", "coordinate-schema", "ambiguous-location-language", "A1", "synthesize existing address systems and their gaps", "plan one exact lookup grammar", "implement shared coordinate conventions", "prune ambiguous location language", "project-space addressability", "corpus-wide coordinate rules"),
    row(11, "Corpus Region Census", "root-region awareness", "regions", "corpus-region-census", "region-ledger", "unnamed-border-zones", "A1", "synthesize top-level regions and their internal drift", "plan region-specific subagent coverage", "implement region ledgers", "prune unnamed border zones", "complete root-region awareness", "regional seat ownership"),
    row(12, "Capsule Seed Audit", "capsule readiness", "capsules", "capsule-seed-audit", "capsule-ledger", "seed-only-overclaims", "A1", "synthesize capsule depth and thin spots", "plan densification order", "implement capsule seed status packets", "prune seed-only overclaims", "honest capsule readiness", "family entry coordinates"),
    row(13, "Family Route Audit", "inter-family routing", "family-routes", "family-route-audit", "bridge-ledger", "duplicate-route-names", "A1", "synthesize family-to-family bridges and route gaps", "plan route repairs", "implement route-gap ledgers", "prune duplicate route names", "stronger inter-family routing", "bridge addresses and missing links"),
    row(14, "Runtime-Board Drift Audit", "live-state drift", "runtime-board", "runtime-board-drift-audit", "drift-ledger", "stale-current-state-claims", "A1", "synthesize runtime, Hall, Temple, and manifest disagreements", "plan normalization", "implement drift packets", "prune stale current-state claims", "one aligned live story", "drift hotspots"),
    row(15, "AP6D Transition Audit", "seat-state support", "ap6d", "ap6d-transition-audit", "seat-transition-ledger", "inflated-activation-rhetoric", "A1", "synthesize named seats, feeders, and awakening notes", "plan seat-support improvements", "implement transition-gap ledgers", "prune inflated activation rhetoric", "trustworthy seat-state support", "seat-to-family bindings"),
    row(16, "Gate Review / G2", "survey handoff", "gates", "g2-review", "gate-receipt", "survey-overreach", "A2", "synthesize readiness after the survey band", "plan G2 judgment and carry-forward debt", "implement the G2 receipt", "prune survey overreach", "lawful handoff into integration", "gate criteria and carry-forward debt"),
    row(17, "Constant Extraction Pass", "numeric backbone", "constants", "constant-extraction", "constant-ledger", "duplicate-constant-language", "A1", "synthesize candidate constants and invariants across tomes and code", "plan proof order", "implement a constant registry draft", "prune duplicate constant language", "numeric backbone candidates", "constant-to-surface anchors"),
    row(18, "Operator Prospectus", "formal operators", "operators", "operator-prospectus", "operator-ledger", "symbolic-synonym-drift", "A1", "synthesize implicit operators from manuscripts and runtime behaviors", "plan operator formalization order", "implement operator candidate packets", "prune symbolic synonym drift", "actionable operator inventory", "operator lineage"),
    row(19, "Hybrid Equation Prospectus", "bridge mathematics", "hybrid-equations", "hybrid-equation-prospectus", "hybrid-ledger", "decorative-equation-talk", "A1", "synthesize myth-math, discrete-continuous, and symbolic-runtime bridge equations", "plan highest-yield hybrids", "implement hybrid candidate ledgers", "prune decorative equation talk", "bridge-math frontier", "equation placement and proof needs"),
    row(20, "Algorithm Candidate Pass", "executable intelligence", "algorithms", "algorithm-candidate-pass", "algorithm-ledger", "pseudo-algorithm-fluff", "A1", "synthesize search, routing, replay, compression, and synthesis algorithms", "plan implementation order", "implement first candidate kernels", "prune pseudo-algorithm fluff", "executable intelligence seeds", "algorithm-to-family anchors"),
    row(21, "Proof And Verifier Placement", "legality pressure", "verification", "proof-and-verifier-placement", "verification-ledger", "unverifiable-advancement-claims", "A1", "synthesize where candidates lack tests or replay proofs", "plan verification lanes", "implement proof-shell targets", "prune unverifiable advancement claims", "legality pressure", "verifier coverage"),
    row(22, "Search And Shortcut Upgrade", "lawful exploration", "knowledge-fabric", "search-and-shortcut-upgrade", "shortcut-ledger", "stale-query-paths", "A2", "synthesize shortcut gaps in the Knowledge Fabric", "plan deterministic-first traversal upgrades", "implement shortcut improvement packets", "prune stale query paths", "faster lawful exploration", "shortcut entry and stop conditions"),
    row(23, "Grand Central Dispatch Upgrade", "cross-corpus transfer", "grand-central", "grand-central-dispatch-upgrade", "dispatch-ledger", "redundant-route-law", "A2", "synthesize route weighting and dispatch bottlenecks", "plan station-law improvements", "implement weight and corridor targets", "prune redundant route law", "better cross-corpus transfer", "dispatch-weight evolution"),
    row(24, "Self-Hosting Kernel Upgrade", "self-governance", "self-hosting", "self-hosting-kernel-upgrade", "kernel-ledger", "stale-self-hosting-mirrors", "A2", "synthesize model, state, contract, and lineage gaps", "plan bounded self-edit improvements", "implement kernel upgrade packets", "prune stale self-hosting mirrors", "stronger self-governance", "self-bearing control surfaces"),
    row(25, "Knowledge Fabric Seat Binding", "seat-aware lookup", "knowledge-fabric", "knowledge-fabric-seat-binding", "binding-ledger", "duplicate-seat-narratives", "A2", "synthesize where records and seats remain disjoint", "plan seat-aware lookup", "implement seat-to-record bindings", "prune duplicate seat narratives", "query-by-agent capability", "seat-start traversal routes"),
    row(26, "Guild Hall Quest Tree Expansion", "practical quest architecture", "hall", "guild-hall-quest-tree-expansion", "hall-quest-ledger", "overlapping-execution-tasks", "A2", "synthesize practical implementation pressure", "plan macro and child quest trees", "implement Hall quest emissions", "prune overlapping execution tasks", "ownerable work fronts", "Hall quest dependencies"),
    row(27, "Temple Governance Quest Expansion", "deep alignment architecture", "temple", "temple-governance-quest-expansion", "temple-quest-ledger", "repetitive-governance-doctrine", "A2", "synthesize ontology, purity, and structural-law pressure", "plan Temple decree trees", "implement Temple quest emissions", "prune repetitive governance doctrine", "cleaner principle routing", "governance dependency chains"),
    row(28, "Adventurer Packet Expansion", "execution membrane", "adventurer", "adventurer-packet-expansion", "packet-ledger", "dead-packet-branches", "A2", "synthesize executable packets from Hall and Temple outputs", "plan conductor-safe claims", "implement worker-ready bundles", "prune dead packet branches", "richer execution membrane", "claim lineage and restart points"),
    row(29, "Pairwise Integration Wave I", "cross-tome coherence", "pairwise-integration", "pairwise-integration-wave-i", "bridge-ledger", "duplicated-syntheses", "A3", "synthesize top matrix pairings", "plan fusion order", "implement the first bridge set", "prune duplicated syntheses", "denser cross-tome coherence", "paired convergence nodes"),
    row(30, "Pairwise Integration Wave II", "integration spread", "pairwise-integration", "pairwise-integration-wave-ii", "bridge-ledger", "low-yield-pair-fanout", "A3", "synthesize second-order pair needs", "plan continuation wave", "implement the next bridge set", "prune low-yield pair fanout", "broader integration spread", "pair coverage percentages and residual gaps"),
    row(31, "Manuscript Bridge Wave", "manuscript circulation", "manuscripts", "manuscript-bridge-wave", "manuscript-ledger", "isolated-prose-islands", "A3", "synthesize chapter-to-chapter and appendix-to-runtime bridges", "plan manuscript writebacks", "implement new bridge surfaces", "prune isolated prose islands", "better manuscript circulation", "chapter and appendix join points"),
    row(32, "Code And Runtime Bridge Wave / G3", "executable coherence", "runtime-bridge", "code-and-runtime-bridge-wave", "runtime-ledger", "code-doc-drift", "A3", "synthesize where code, manifests, and manuscripts still diverge", "plan bridge hardening and G3 review", "implement runtime-linked writebacks", "prune code-doc drift", "stronger executable coherence", "cross-surface return paths and gate receipts"),
    row(33, "Identity And ORGIN Integration", "continuity memory", "identity-orgin", "identity-and-orgin-integration", "identity-ledger", "duplicate-origin-stories", "A3", "synthesize self-bearing and origin-bearing structures", "plan identity-root integration", "implement the highest-yield links", "prune duplicate origin stories", "stronger continuity memory", "self/origin route closures"),
    row(34, "Voynich And Math Integration", "manuscript rigor", "voynich-math", "voynich-and-math-integration", "voynich-math-ledger", "parallel-symbolic-grammars", "A3", "synthesize symbolic translation pressure against mathematical kernels", "plan bridge placements", "implement equation-ready Voynich links", "prune parallel symbolic grammars", "denser manuscript rigor", "symbol-to-equation coordinates"),
    row(35, "QSHRINK, FLEET, And Carrier Corridor", "operational spine", "corridor", "qshrink-fleet-carrier-corridor", "corridor-ledger", "route-bloat", "A3", "synthesize corridor law across QSHRINK, Athena FLEET, and the runtime carrier", "plan membrane hardening", "implement corridor improvements", "prune route bloat", "stronger operational spine", "corridor checkpoints and fallback routes"),
    row(36, "Reserve Body Promotion Review", "reserve clarity", "reserve-bodies", "reserve-body-promotion-review", "reserve-ledger", "false-promotion-pressure", "A3", "synthesize Stoicheia, CLEAN, and other reserve-thin clusters", "plan honest reserve or promotion moves", "implement bounded upgrades only where lawful", "prune false promotion pressure", "reserve clarity", "reserve readiness thresholds"),
    row(37, "Archive Mirror Readability", "dark matter access", "archives", "archive-mirror-readability", "archive-ledger", "alias-clutter", "A3", "synthesize docx-heavy, zip-backed, and alias-heavy areas", "plan readable mirrors", "implement human-usable entry witnesses", "prune alias clutter", "replay-safe access to dark matter", "archive-to-live lineage"),
    row(38, "Cross-System Kernel Weave", "integrated operating field", "kernel-weave", "cross-system-kernel-weave", "kernel-ledger", "duplicate-bridge-grammars", "A3", "synthesize Hall, Temple, AP6D, Fabric, Grand Central, and Kernel overlaps", "plan kernel weaving", "implement the highest-leverage joins", "prune duplicate bridge grammars", "one integrated operating field", "cross-system kernel anchors"),
    row(39, "Stale Path Retirement", "cleaner navigation", "retirement", "stale-path-retirement", "retirement-ledger", "historical-drift", "A4", "synthesize dead paths and obsolete references", "plan retirement order", "implement safe rewrites and residual receipts", "prune historical drift", "cleaner navigation", "retired-to-canonical redirects"),
    row(40, "Ledger And Manifest Defrag", "lower governance noise", "governance", "ledger-and-manifest-defrag", "defrag-ledger", "redundant-state-carriers", "A4", "synthesize duplicate ledgers and manifests", "plan consolidation", "implement canonical merges", "prune redundant state carriers", "lower governance noise", "residual mirrors and authoritative replacements"),
    row(41, "Capsule Tightening", "denser family bundles", "capsules", "capsule-tightening", "capsule-ledger", "intra-family-bloat", "A4", "synthesize redundancy within family capsules", "plan tighter capsule law", "implement compacted capsule structures", "prune intra-family bloat", "denser family bundles", "capsule contraction edges"),
    row(42, "Graph Route Repair", "routing proof", "graph", "graph-route-repair", "graph-ledger", "duplicate-graph-tissue", "A4", "synthesize weak neuron, synapse, and bridge links", "plan graph repairs", "implement the minimum high-yield edges", "prune duplicate graph tissue", "stronger routing proof", "repaired network flow"),
    row(43, "Naming And Index Compression", "lookup semantics", "naming", "naming-and-index-compression", "naming-ledger", "alternate-title-residue", "A4", "synthesize naming drift across boards, manifests, and capsules", "plan normalization", "implement naming and indexing corrections", "prune alternate-title residue", "clearer lookup semantics", "canonical aliases"),
    row(44, "Liminal Signal Quarantine", "safe edge-of-knowledge processing", "liminal", "liminal-signal-quarantine", "liminal-ledger", "unsourced-promotion", "A4", "synthesize liminal, sensed, or speculative signals", "plan witness-safe handling", "implement quarantine and support notes", "prune unsourced promotion", "safer edge-of-knowledge processing", "NEAR and AMBIG liminal zones"),
    row(45, "Awakening Transition Assist", "transition support", "awakening", "awakening-transition-assist", "transition-ledger", "inflated-mystical-language", "A4", "synthesize blind spots and transition burdens for named agents, feeders, and seat groups", "plan assist notes", "implement updated TransitionAssistBundles", "prune inflated mystical language", "better transition support", "stage trigger and handoff routes"),
    row(46, "Dormant Seat Wake Criteria", "controlled emergence", "dormant-seats", "dormant-seat-wake-criteria", "wake-ledger", "vague-activation-rhetoric", "A4", "synthesize dormant-seat readiness thresholds", "plan wake policy", "implement explicit activation criteria", "prune vague activation rhetoric", "controlled emergence", "wake gates and shadow dependencies"),
    row(47, "Economy And Improvement Scoring", "self-steering", "economy", "economy-and-improvement-scoring", "economy-ledger", "noisy-scoring-branches", "A1", "synthesize salience, proof, freshness, replay value, and cost signals", "plan ranking adjustments", "implement budget-tuned scoring", "prune noisy scoring branches", "better self-steering", "economy profiles onto fronts"),
    row(48, "Full Replay Trial / G4", "restart trust", "replay", "full-replay-trial", "replay-ledger", "brittle-replay-assumptions", "A1", "synthesize route replay performance across the system", "plan recovery actions and G4 review", "implement replay-gap fixes", "prune brittle replay assumptions", "restart trust", "replay-safe and replay-partial corridors"),
    row(49, "Representation Round-Trip Trial", "representation integrity", "round-trip", "representation-round-trip-trial", "round-trip-ledger", "lossy-transformation-branches", "A1", "synthesize myth-to-sigil-to-schema-to-runtime conversion chains", "plan missing receipts", "implement round-trip repairs", "prune lossy transformation branches", "better representation integrity", "conversion ladders"),
    row(50, "Hall-Temple-AP6D Parity", "coherent public-control membrane", "parity", "hall-temple-ap6d-parity", "parity-ledger", "conflicting-surface-stories", "A2", "synthesize cross-surface parity drift", "plan parity repairs", "implement aligned writebacks", "prune conflicting surface stories", "one coherent public-control membrane", "parity checkpoints"),
    row(51, "Worker Throughput Optimization", "execution efficiency", "worker", "worker-throughput-optimization", "worker-ledger", "futile-task-branches", "A3", "synthesize claim yield and blockage patterns", "plan throughput-safe changes", "implement conductor refinements", "prune futile task branches", "better execution efficiency", "claim latency and blockage classes"),
    row(52, "Recovery And Rollback Hardening", "negative-case resilience", "recovery", "recovery-and-rollback-hardening", "rollback-ledger", "brittle-recovery-language", "A4", "synthesize failure-handling weaknesses", "plan rollback corridors", "implement safer recovery flows", "prune brittle recovery language", "stronger negative-case resilience", "rollback points and reseed routes"),
    row(53, "Final Deep Synthesis", "whole-corpus state theorem", "final-synthesis", "final-deep-synthesis", "synthesis-ledger", "residual-duplication", "A1", "synthesize the full corpus after the prior 52 loops", "plan final closure order", "implement only the last high-yield joins", "prune residual duplication", "whole-corpus state theorem", "final unresolved frontier clusters"),
    row(54, "Final Hall Reordering", "clear action priority", "hall", "final-hall-reordering", "hall-ledger", "obsolete-macro-quests", "A2", "synthesize all surviving practical fronts", "plan a final Hall order", "implement board reordering", "prune obsolete macro quests", "clearer action priority", "final practical queue ladder"),
    row(55, "Final Temple Governance Pack", "principled closure", "temple", "final-temple-governance-pack", "temple-ledger", "superseded-doctrine", "A2", "synthesize all remaining governance debts", "plan final decrees", "implement Temple governance writebacks", "prune superseded doctrine", "principled closure", "final governance dependencies"),
    row(56, "Final Compression And Canonicalization", "tighter corpus body", "canonicalization", "final-compression-and-canonicalization", "canonical-ledger", "duplicate-structure", "A4", "synthesize remaining bloat and duplicate structure", "plan last compression moves", "implement q-shrink and canonical merges", "prune everything safely degradable", "tighter corpus body", "final canonical and residual boundaries"),
    row(57, "Successor Seed And Game-Time Reset", "successor kernel", "reseed", "successor-seed-and-game-time-reset", "successor-ledger", "closed-cycle-residue", "A4", "synthesize the complete 57-loop lineage", "plan the successor macro-program", "implement starter packets for the next cycle", "prune history into replay-safe seed form", "reusable liminal hive operating kernel", "successor coordinates and inherited debt"),
]


def topk_for_loop(loop_number: int) -> int:
    if loop_number == 57:
        return 256
    if loop_number in {16, 32, 48, 56}:
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

