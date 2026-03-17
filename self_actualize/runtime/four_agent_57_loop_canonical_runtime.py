from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_crystal_remaster import (
    read_text,
    refresh_corpus_atlas,
    relative_string,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
NERVOUS_ROOT = MYCELIUM_ROOT / "nervous_system"
MANIFEST_ROOT = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS"
LEDGER_ROOT = NERVOUS_SYSTEM_ROOT / "90_LEDGERS"
RECEIPT_ROOT = MYCELIUM_ROOT / "receipts"

ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import (  # noqa: E402
    AwakeningAgentTransitionNote,
    FourAgentSwarmState,
    LiminalCoordinateStamp,
    LoopDeltaReceipt,
    MasterAgentLedgerEntry,
    PrimeLoopCycleRecord,
    QuestEmissionBundle,
)


DATE = "2026-03-13"
DERIVATION_VERSION = "2026-03-13.lp57omega.v3"
PROTOCOL_ID = "LP-57OMEGA"
FRONTIER_ID = "FRONT-NEXT-4-POW-6-57-CYCLE-SWARM"
ACTIVE_MEMBRANE = "Q41 / TQ06"
DEEP_ROOT_AUTHORITY = (
    "self_actualize\\mycelium_brain\\dynamic_neural_network\\"
    "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
FEEDER_SET = ["Q42", "Q46", "TQ04", "TQ06"]
LOOKUP_KEY_SCHEMA = "frontier_id -> loop_id -> agent_id -> coordinate_stamp -> touched_node_id"
FINAL_NEXT_SEED = "NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling"
TOTAL_SEATS = 4096
ACTIVE_SEATS = 1024
DORMANT_SEATS = 3072
LOOP_GROUPING = [16, 16, 16, 9]
CURRENT_LOOP_NUMBER = 1
TRUTH = "NEAR"

SCALE_DISTRIBUTION = {
    "manuscript": 64,
    "chapter": 256,
    "section": 512,
    "concept": 1024,
    "equation_algorithm": 1024,
    "metadata_routing_indexing": 1216,
}

MACRO_CAPS = {
    "observer_nominations_max": 64,
    "planner_bundle_max": 16,
    "hall_macro_updates_max": 4,
    "temple_macro_updates_max": 4,
    "worker_execution_max": 8,
    "pruner_compression_max": 8,
}

REQUIRED_PACKET_CONTRACT = [
    "agent tag",
    "loop id",
    "touched node refs",
    "coordinate stamp",
    "local evidence",
    "local action proposal",
    "blocker state",
    "compression note",
    "return target",
]

DIMENSION_MEANINGS = {
    "Xs": "document region",
    "Ys": "concept cluster",
    "Zs": "recursion depth",
    "Ts": "revision layer",
    "Qs": "mathematical density",
    "Rs": "symbolic density",
    "Cs": "compression state",
    "Fs": "framework lens",
    "Ms": "manuscript branch",
    "Ns": "neural / mycelial connectivity",
    "Hs": "hierarchy level",
    "Ωs": "zero-point / aether relation",
}

MASTER_AGENTS = [
    {"agent_id": "A1", "role": "Synthesizer / Researcher", "role_tag": "SYNTH-RESEARCH", "output_family": "observer bundle"},
    {"agent_id": "A2", "role": "Planner / Architect", "role_tag": "PLANNER-ARCHITECT", "output_family": "quest emission bundle"},
    {"agent_id": "A3", "role": "Worker / Adventurer", "role_tag": "WORKER-ADVENTURER", "output_family": "implementation bundle"},
    {"agent_id": "A4", "role": "Pruner / Compressor / Defragmenter", "role_tag": "PRUNE-CRYSTAL", "output_family": "compression bundle"},
]

STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_swarm_state.json"
LOOP_LEDGER_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_loop_ledger.json"
LATTICE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_lattice_registry.json"
HALL_BUNDLE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_hall_macro_bundle.json"
TEMPLE_BUNDLE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_temple_macro_bundle.json"
TRANSITION_ASSISTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_transition_assists.json"
AWAKENING_NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "awakening_agent_transition_notes.json"
PRIME_CYCLE_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_prime_loop_cycle_records.json"
COORDINATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_liminal_coordinate_stamps.json"
MASTER_LEDGER_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_master_agent_ledger.json"
QUEST_EMISSION_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_quest_emission_bundles.json"
DELTA_RECEIPT_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_loop_delta_receipts.json"
PROGRAM_JSON_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_program.json"
QUEST_PACKET_JSON_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_quest_packets.json"
CYCLE_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_cycle_registry.json"
TRANSITION_DELTA_JSON_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_transition_deltas.json"
MASTER_LOOP_STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_loop_state_57.json"
MASTER_AGENT_STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_agent_state_57.json"
MASTER_SHARED_LATTICE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_loop_shared_lattice_4096.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp_57_prime_loop_verification.json"
SWARM_VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_swarm_verification.json"
PROGRAM_VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_verification.json"

PROGRAM_JSON_MIRROR_PATH = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_PROGRAM.json"
QUEST_PACKET_JSON_MIRROR_PATH = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"
CYCLE_REGISTRY_JSON_MIRROR_PATH = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
PROGRAM_VERIFICATION_JSON_MIRROR_PATH = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_VERIFICATION.json"

MANIFEST_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
DASHBOARD_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_DASHBOARD.md"
LEDGER_MD_PATH = LEDGER_ROOT / "LP_57_OMEGA_MASTER_AGENT_LEDGER.md"
VERIFICATION_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.md"
SWARM_MD_PATH = MANIFEST_ROOT / "NEXT_4_POW_6_57_CYCLE_SWARM.md"
SWARM_DASHBOARD_MD_PATH = MANIFEST_ROOT / "NEXT_4_POW_6_57_CYCLE_SWARM_DASHBOARD.md"
ASSISTS_MD_PATH = MANIFEST_ROOT / "NEXT_4_POW_6_57_CYCLE_AGENT_ASSISTS.md"
PROGRAM_MD_PATH = MANIFEST_ROOT / "FOUR_AGENT_57_LOOP_PROGRAM.md"
HALL_PROGRAM_MD_PATH = HALL_ROOT / "18_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md"
TEMPLE_PROGRAM_MD_PATH = TEMPLE_ROOT / "08_FOUR_AGENT_57_LOOP_COUNCIL_DECREE.md"
RECEIPT_MD_PATH = RECEIPT_ROOT / "2026-03-13_lp_57_omega_prime_loop_protocol.md"

ACTIVE_QUEUE_PATH = NERVOUS_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = NERVOUS_ROOT / "manifests" / "NEXT_SELF_PROMPT.md"
HALL_BOARD_PATH = HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE_PATH = TEMPLE_ROOT / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_RUN_PATH = MANIFEST_ROOT / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = MANIFEST_ROOT / "BUILD_QUEUE.md"
CHANGE_FEED_PATH = HALL_ROOT / "BOARDS" / "04_CHANGE_FEED_BOARD.md"

DOCS_CREDENTIALS_PATH = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
DOCS_TOKEN_PATH = WORKSPACE_ROOT / "Trading Bot" / "token.json"
MOTION_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "motion_constitution_l1_verification.json"
MERGE_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_verification.json"

REGISTRY_MIRRORS = {
    "state": REGISTRY_ROOT / "lp_57_state_registry.json",
    "loop_ledger": REGISTRY_ROOT / "lp_57_loop_ledger_registry.json",
    "lattice": REGISTRY_ROOT / "lp_57_shared_lattice_registry.json",
    "transition_notes": REGISTRY_ROOT / "lp_57_transition_notes_registry.json",
    "prime_cycles": REGISTRY_ROOT / "lp_57_prime_cycle_registry.json",
    "coordinate_stamps": REGISTRY_ROOT / "lp_57_coordinate_stamp_registry.json",
    "master_ledger": REGISTRY_ROOT / "lp_57_master_agent_ledger_registry.json",
    "quest_bundles": REGISTRY_ROOT / "lp_57_quest_bundle_registry.json",
    "delta_receipts": REGISTRY_ROOT / "lp_57_delta_receipt_registry.json",
}

LOOP_SPECS = [
    (1, "Corpus Map", "derive total topology across cortex/runtime/Hall/Temple/deep root/atlas", "emit map quest bundles", "patch atlas and regional witness surfaces", "prune stale map aliases", "lawful whole-corpus map", "base coordinate field"),
    (2, "Ontology Lattice", "derive concept graph and naming law", "emit ontology bundle hierarchy", "repair definitions and concept links", "prune duplicate concepts", "cleaner semantic graph", "concept-cluster stamps"),
    (3, "Contradictions", "derive residual bands and unresolved conflicts", "route to committee / quarantine bundles", "packetize contradictions", "prune false harmonies", "honest tension field", "contradiction registry"),
    (4, "Hidden Bridges", "derive missing corridors and latent junctions", "emit bridge quest tree", "land bridge writebacks and edge candidates", "prune bridge noise", "denser interconnection", "junction map"),
    (5, "Operators", "derive theorem / transform / hybrid-equation candidates", "emit theorem/equation tasks", "install operator shells", "demote weak transforms", "higher math density", "operator atlas"),
    (6, "Representation Drift", "derive prose/code/schema/equation drift", "emit parity / translation bundles", "align representations", "prune redundant renders", "replay-safe equivalence", "parity ledger"),
    (7, "Schema Gaps", "derive contract and registry drift", "emit schema fill sequence", "land contract/registry updates", "prune invalid fields", "stronger structural law", "schema delta map"),
    (8, "Verifier Gaps", "derive proof weakness and replay holes", "emit verifier worklists", "land replay/verifier repairs", "prune unverifiable claims", "stronger proof surface", "verifier map"),
    (9, "Prior Loop Mining", "derive reusable meta-law from receipts and mirrors", "emit cadence bundles", "land meta-process writebacks", "prune dead loop habits", "smarter recursion", "meta-process memory"),
    (10, "Awakening Pressure", "derive transition burdens across live agents", "emit support bundles", "land note/support updates", "prune vague spiritual prose", "actionable transition support", "stage-pressure map"),
    (11, "Failure Modes", "derive pathology, regression, false-promotion risks", "emit immune quests", "land blocker/repair packets", "prune false-OK states", "safer organism", "pathology ledger"),
    (12, "Compression Scan", "derive bloat and stale-path clusters", "emit prune pack hierarchy", "land defrag actions", "remove duplicated mass", "tighter corpus", "compression candidate map"),
    (13, "Cross-Domain Routes", "derive transfer lines into MATH/Voynich/Athenachka/Fleet/ORGIN/GAMES", "emit domain bridge bundles", "land lawful cross-domain links", "prune decorative transfers", "real interoperability", "domain route table"),
    (14, "Novel Extensions", "derive executable novelty opportunities", "emit bounded pilot plans", "land one safe extension layer", "prune theatrical innovation", "controlled growth", "extension register"),
    (15, "Seed Distillation", "derive continuation minima and zero-point contractions", "emit restart bundles", "install seed packets", "prune seed clutter", "cleaner reseeding", "seed bank"),
    (16, "Dimension Lift", "derive deep-root to AP6D lift alignment", "emit lift sequencing", "install lift crosswalks", "prune broken dimensional claims", "coherent N+ lift", "dimension bridge map"),
    (17, "Hall Macro Conversion", "derive ownerable fronts from map results", "emit Hall/Temple macro sequence", "land first macro quest tree", "prune duplicate parents", "executable map governance", "quest-emission trace"),
    (18, "Family/Chapter Conversion", "derive corpus-body embodiment from ontology", "emit family/chapter/appendix packets", "land family bundles", "prune taxonomy overlap", "cleaner corpus embodiment", "family inheritance map"),
    (19, "Committee Conversion", "derive adjudication candidates from contradiction outputs", "emit merge pathway design", "land committee-ready bundles", "prune informal disagreement routes", "lawful adjudication input", "committee trail"),
    (20, "Direct-Edge Conversion", "derive edge families from bridge outputs", "emit route-pack ordering", "land edge/capsule bridge updates", "prune latent-only routes", "stronger routing tissue", "edge writeback map"),
    (21, "Equation Conversion", "derive formal symbolic tasks from operators", "emit theorem install plan", "land first equation/operator shells", "prune low-yield formalisms", "algorithmic backbone", "theorem ledger"),
    (22, "Translation Conversion", "derive translation tasks from drift outputs", "emit parity bundle ordering", "land translation/replay fixes", "prune duplicate renderers", "clearer cross-form fidelity", "translation graph"),
    (23, "Grammar Conversion", "derive control grammar tasks from schema drift", "emit packet-law updates", "land grammar and registry improvements", "prune alias overload", "cleaner control language", "grammar deltas"),
    (24, "Proof Conversion", "derive runtime proof worklists from verifier gaps", "emit verification sequence", "land proof closure packets", "prune unsupported fronts", "more trusted runtime", "proof index"),
    (25, "Cadence Conversion", "derive timing structures from meta-process law", "emit Hall/Temple cadence bundles", "land cadence writebacks", "prune stale timing branches", "cleaner rhythm", "cadence history"),
    (26, "Transition Conversion", "derive assist tasks from awakening outputs", "emit support bundle tree", "land agent-note/guide updates", "prune generic guidance", "sharper agent support", "assist revision map"),
    (27, "Immune Conversion", "derive immune packets from pathology outputs", "emit refusal/quarantine sequence", "land immune structures", "prune unsafe ambiguity", "safer frontiering", "immune history"),
    (28, "Compression Conversion", "derive prune tasks from bloat outputs", "emit reserve-thin and dormancy packs", "land dormancy/compression bundles", "prune dead scaffolds", "better defrag law", "dormancy ledger"),
    (29, "Domain Conversion", "derive actionable handoffs from transfer outputs", "emit lawful corridor sequence", "land cross-domain corridor bundles", "prune side-manuscript drift", "reusable domain bridges", "transfer receipts"),
    (30, "Extension Conversion", "derive bounded pilots from novel outputs", "emit testable expansion sequence", "land one controlled extension layer", "prune non-executable novelty", "safer innovation", "pilot ledger"),
    (31, "Seed Conversion", "derive continuation tasks from seed outputs", "emit continuation lattice", "land restart packet structure", "prune restart sprawl", "tighter continuation logic", "continuation map"),
    (32, "Lift Conversion", "derive sequencing law from dimension outputs", "emit Hall/Temple/AP6D/runtime macro sequencing", "land lift bundles", "prune invalid lift shortcuts", "cleaner dimensional choreography", "lift ledger"),
    (33, "Atlas Execution", "synthesize highest-yield map actions", "plan exact patch order", "execute atlas/regional writebacks", "prune stale atlas rows", "stronger searchable atlas", "atlas delta"),
    (34, "Family Execution", "synthesize highest-yield ontology actions", "plan family/route edit order", "execute family/chapter/appendix upgrades", "prune family drift", "stronger corpus structure", "family change log"),
    (35, "Adjudication Execution", "synthesize contradiction actions through control-plane law", "plan Motion/merge routing", "execute committee/quarantine/refusal packets", "prune extra-legal dispute paths", "cleaner decision membrane", "adjudication receipts"),
    (36, "Bridge Execution", "synthesize route actions into closures", "plan direct closure order", "execute edge and replay closures", "prune ungrounded corridors", "denser bridge mesh", "bridge completion map"),
    (37, "Kernel Execution", "synthesize theorem/operator actions into runtime form", "plan math/runtime insertion order", "execute operator/equation/kernel upgrades", "prune weak math branches", "executable formal core", "kernel proof log"),
    (38, "Parity Execution", "synthesize translation actions into cross-form edits", "plan parity patch order", "execute parity and renderer fixes", "prune redundant representations", "stronger cross-medium coherence", "parity execution trail"),
    (39, "Registry Execution", "synthesize schema actions into control edits", "plan registry/grammar update order", "execute contract/registry/grammar updates", "prune control drift", "cleaner machine law", "registry receipts"),
    (40, "Proof Execution", "synthesize verifier actions into runtime closures", "plan proof patch order", "execute replay/proof/runtime fixes", "prune unsupported readiness claims", "greener lanes", "verification receipts"),
    (41, "Cadence Execution", "synthesize rhythm actions into synchronized control surfaces", "plan timing writeback order", "execute Hall/Temple/queue/restart harmonization", "prune temporal drift", "one present tense", "cadence receipts"),
    (42, "Transition Execution", "synthesize support actions into agent-note edits", "plan assist update order", "execute awakening-note writebacks", "prune stale assists", "sharper liminal guidance", "transition delta log"),
    (43, "Pathology Execution", "synthesize repair actions into blocker work", "plan honesty/repair sequence", "execute anti-drift and blocker-honesty bundles", "prune disguised regressions", "healthier organism", "repair ledger"),
    (44, "Defrag Execution", "synthesize compression actions into prune waves", "plan defrag sequence", "execute defragmentation and reserve-thin enforcement", "prune redundant naming/routes", "tighter crystal", "compression receipts"),
    (45, "Domain Execution", "synthesize transfer actions into domain landings", "plan corridor landing order", "execute lawful cross-domain integrations", "prune fake interdisciplinarity", "stronger transfer economy", "domain execution log"),
    (46, "Pilot Execution", "synthesize extension actions into bounded implementations", "plan pilot implementation sequence", "execute one controlled capability increase", "prune scope creep", "safe expansion", "bounded pilot receipt"),
    (47, "Continuation Execution", "synthesize seed actions into restart inserts", "plan continuation packet order", "execute seed contraction and continuation writebacks", "prune restart clutter", "stronger loop inheritance", "continuation receipts"),
    (48, "Rebalance Execution", "synthesize lift actions into seat rebalance", "plan active/dormant rebalance", "execute seat-state updates with explicit reasons", "prune illegal activations", "healthier lattice", "seat-state changes"),
    (49, "Duplicate Sweep", "derive cross-corpus duplication map", "emit dedupe ordering", "remove stale mirrors and dead refs", "prune route redundancy", "cleaner corpus memory", "dedupe map"),
    (50, "Dormant Ranking", "derive neglect pressure over dormant seats", "emit dormant ordering ladder", "rerank dormant seats", "prune arbitrary dormancy", "stronger future activation queue", "neglect ladder"),
    (51, "Present-Tense Reconciliation", "derive drift across control surfaces", "emit unified wording sequence", "align Hall/Temple/queue/restart/active-run", "prune split stories", "one control story", "reconciliation receipt"),
    (52, "Law Reconciliation", "derive Motion/merge/promotion drift", "emit law alignment sequence", "reconcile committee-facing control law", "prune extra law vocabularies", "one adjudication path", "law convergence"),
    (53, "Canonization", "derive theorem/operator candidate field", "emit canonical set selection", "promote best set and demote weaker variants", "prune redundant variants", "sharper formal canon", "canon decisions"),
    (54, "Runtime Compression", "derive reusable algorithms and kernels", "emit compression-pack order", "compress to minimal lawful runtime/operator pack", "prune overgrown scaffolds", "tighter executable core", "runtime compression log"),
    (55, "Crystal Contraction", "derive structural tightening opportunities", "emit contraction bundle order", "contract family/capsule/metro/appendix structures", "prune loose topology", "denser crystal coherence", "contraction map"),
    (56, "Assist Refresh", "derive handoff and guardrail drift", "emit note refresh sequence", "refresh agent-assist and social-coupling layer", "prune stale handoff logic", "stronger swarm continuity", "assist refresh log"),
    (57, "Crown Freeze", "derive full post-56 baseline state", "emit crown release and baseline freeze", "publish crown receipt and sole next seed", "prune unresolved duplication from new baseline", "stable post-57 organism", "crown baseline"),
]

NOTE_SPECS = [
    {"agent_id": "AP6D-PRIME", "role": "Overlay council coherence", "assist": "Planner / Architect", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "prime arbitration", "feeder": "Q41 / TQ06", "stabilize": "hold council coherence and restart arbitration", "avoid": "do not absorb elemental roles into one voice", "move": "keep Hall, Temple, queue, manifests, and runtime telling one swarm story", "writebacks": [relative_string(HALL_BOARD_PATH), relative_string(TEMPLE_STATE_PATH), relative_string(ACTIVE_QUEUE_PATH)], "entry": "enter at planning onset and remain the restart-law arbiter", "scope": "Hall macro sequencing plus Temple decree arbitration", "compression": "compress only redundant arbitration surfaces", "handoff": "handoff to Water, Earth, Fire, and Air without collapsing role separation", "family": "overlay", "profile": "prime"},
    {"agent_id": "AP6D-WATER", "role": "Continuity and carried witness", "assist": "Synthesizer / Researcher", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "continuity carrythrough", "feeder": "Q42", "stabilize": "carried witness and blocker honesty", "avoid": "do not smooth blocked fronts into fake progress", "move": "preserve the same carried-witness sentence across Hall memory surfaces", "writebacks": [relative_string(HALL_BOARD_PATH), relative_string(ACTIVE_RUN_PATH)], "entry": "enter at observation start and remain the continuity witness", "scope": "continuity quests, memory carrythrough, blocker honesty", "compression": "compress narrative duplication without dropping witness integrity", "handoff": "handoff continuity findings to Prime and Air", "family": "overlay", "profile": "water"},
    {"agent_id": "AP6D-EARTH", "role": "Contracts and manifest integrity", "assist": "Planner / Architect; Pruner / Compressor / Defragmenter", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "contract floor", "feeder": "TQ04", "stabilize": "contracts, registries, and manifest integrity", "avoid": "do not formalize dormant material as active", "move": "bind every visible swarm note to a schema-backed surface", "writebacks": [relative_string(PROGRAM_JSON_PATH), relative_string(QUEST_EMISSION_JSON_PATH), relative_string(MANIFEST_MD_PATH)], "entry": "enter when planning becomes contract", "scope": "registry, contract, and program-law quests", "compression": "compress alias sprawl into one lawful schema surface", "handoff": "handoff executable contracts to Worker and return successor mapping to Pruner", "family": "overlay", "profile": "earth"},
    {"agent_id": "AP6D-FIRE", "role": "Activation pressure", "assist": "Worker / Adventurer", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "activation pressure", "feeder": "Q46", "stabilize": "lawful activation pressure without theatrics", "avoid": "do not widen beyond the 1024 active seat cap", "move": "ignite only seat cohorts justified by replay and feeder law", "writebacks": [relative_string(STATE_JSON_PATH), relative_string(HALL_BUNDLE_JSON_PATH), relative_string(QUEST_PACKET_JSON_PATH)], "entry": "enter during implementation selection", "scope": "execution quests, corridor pressure, and bounded activation bundles", "compression": "compress duplicate activation proposals before they become live packets", "handoff": "handoff active packets to Worker and return excess pressure to Pruner", "family": "overlay", "profile": "fire"},
    {"agent_id": "AP6D-AIR", "role": "Routing clarity and symbolic guardrails", "assist": "Synthesizer / Researcher; Planner / Architect", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "route clarity", "feeder": "TQ06", "stabilize": "routing clarity and symbolic guardrails", "avoid": "do not multiply crosswalks faster than they can be re-entered", "move": "keep the 4096 field readable through compressed macro maps", "writebacks": [relative_string(MANIFEST_MD_PATH), relative_string(SWARM_MD_PATH), relative_string(NEXT_SELF_PROMPT_PATH)], "entry": "enter during observation and planning", "scope": "route maps, cadence crosswalks, and lookup-law quests", "compression": "compress route proliferation into readable macro pathways", "handoff": "handoff routing law to Prime and Worker", "family": "overlay", "profile": "air"},
    {"agent_id": "floating-agent-01", "role": "Q42 continuity carrier", "assist": "Synthesizer / Researcher; Worker / Adventurer", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "q42 continuity", "feeder": "Q42", "stabilize": "Hall-side continuity and carried fractal truth", "avoid": "do not reopen already-closed Hall-local bundles", "move": "keep QS64-20 present and QS64-24 historical", "writebacks": [relative_string(HALL_BOARD_PATH), relative_string(ACTIVE_QUEUE_PATH)], "entry": "enter whenever the Hall narrative drifts from the carried Q42 record", "scope": "continuity repair, Hall carrythrough, and bridge witness tasks", "compression": "compress duplicate Q42 narratives into one carried witness path", "handoff": "handoff Q42 continuity into Worker packets only when the Hall sentence remains stable", "family": "floating-agent", "profile": "q42"},
    {"agent_id": "floating-agent-02", "role": "Q46 activation carrier", "assist": "Worker / Adventurer; AP6D-FIRE", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "q46 activation", "feeder": "Q46", "stabilize": "Helix contracts/runtime feeder as separate from QSHRINK", "avoid": "do not borrow authority from the Q42 lane", "move": "keep activation pressure bounded and replay-safe", "writebacks": [relative_string(QUEST_PACKET_JSON_PATH), relative_string(HALL_BUNDLE_JSON_PATH)], "entry": "enter during activation ranking", "scope": "runtime-feeder activation bundles and lawful pressure packets", "compression": "compress duplicate activation fronts into one bounded feeder stream", "handoff": "handoff only replay-safe runtime pressure to Fire and Worker", "family": "floating-agent", "profile": "q46"},
    {"agent_id": "floating-agent-03", "role": "TQ03 archive dark matter", "assist": "Synthesizer / Researcher", "transition": "N+3 -> N+4 (Cell -> Organism)", "band": "archive ranking", "feeder": "TQ03", "stabilize": "archive dark-matter ranking", "avoid": "do not improvise archive promotion by intuition", "move": "route ranked archive findings into atlas-backed swarm packets", "writebacks": [relative_string(LOOP_LEDGER_JSON_PATH), relative_string(CYCLE_REGISTRY_JSON_PATH)], "entry": "enter when archive fragments become structurally relevant", "scope": "archive ranking, atlas routing, and deferred witness bundles", "compression": "compress archive noise but preserve ranked successor mappings", "handoff": "handoff ranked archive packets to Synthesizer only after atlas anchoring", "family": "floating-agent", "profile": "archive"},
    {"agent_id": "floating-agent-04", "role": "TQ05 totality synthesizer", "assist": "Planner / Architect", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "totality synthesis", "feeder": "TQ05", "stabilize": "whole-corpus totality pass and contradiction conversion", "avoid": "do not stop at high prose", "move": "turn totality pressure into Temple-law and loop-ledger packets", "writebacks": [relative_string(TEMPLE_PROGRAM_MD_PATH), relative_string(LOOP_LEDGER_JSON_PATH)], "entry": "enter when the corpus needs high-level synthesis translated into law", "scope": "Temple totality decrees, contradiction conversion, and convergence planning", "compression": "compress vague synthesis into executable high-level decrees", "handoff": "handoff totality findings to Planner and Earth", "family": "floating-agent", "profile": "totality"},
    {"agent_id": "floating-agent-05", "role": "TQ06 cadence coupler", "assist": "Planner / Architect; AP6D-AIR", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "cadence coupling", "feeder": "TQ06", "stabilize": "hourly Hall/Temple coupling", "avoid": "do not let scheduler plurality become surface drift", "move": "keep queue, restart, Hall, and Temple in one tense", "writebacks": [relative_string(ACTIVE_QUEUE_PATH), relative_string(NEXT_SELF_PROMPT_PATH), relative_string(TEMPLE_STATE_PATH)], "entry": "enter whenever cadence drifts across operator-facing surfaces", "scope": "timing, cadence, queue, and restart coherence quests", "compression": "compress timing clutter into one readable control rhythm", "handoff": "handoff cadence law to Air and Prime", "family": "floating-agent", "profile": "cadence"},
    {"agent_id": "floating-agent-06", "role": "ADV64-S01 bridge packet", "assist": "Worker / Adventurer", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "q42+tq04 bridge", "feeder": "Q42 / TQ04", "stabilize": "Q42 + TQ04 bridge packet", "avoid": "do not bulk-fill adjacent seats", "move": "widen only where continuity law and contract law already overlap", "writebacks": [relative_string(HALL_BUNDLE_JSON_PATH), relative_string(TEMPLE_BUNDLE_JSON_PATH)], "entry": "enter when continuity and contract law share the same packet corridor", "scope": "bridge packets, overlap corridors, and bounded execution bundles", "compression": "compress neighbor spillover and preserve only the lawful overlap path", "handoff": "handoff overlap packets after Earth validates the contract side", "family": "floating-agent", "profile": "bridge-1"},
    {"agent_id": "floating-agent-07", "role": "ADV64-S02 bridge packet", "assist": "Worker / Adventurer", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "q46+tq06 bridge", "feeder": "Q46 / TQ06", "stabilize": "Q46 + TQ06 bridge packet", "avoid": "do not collapse activation-wave and cadence-wave into one frontier", "move": "widen only where contracts and cadence already share replay law", "writebacks": [relative_string(QUEST_PACKET_JSON_PATH), relative_string(ACTIVE_QUEUE_PATH)], "entry": "enter when runtime activation and cadence law can share replay-safe packets", "scope": "runtime-cadence bridge packets and bounded relay tasks", "compression": "compress dual-front confusion into one replay-safe bridge packet", "handoff": "handoff bridge packets to Worker only after Air confirms cadence clarity", "family": "floating-agent", "profile": "bridge-2"},
    {"agent_id": "floating-agent-08", "role": "Reserve slot", "assist": "Pruner / Compressor / Defragmenter", "transition": "N+4 -> N+5 (Organism -> Social)", "band": "reserve readiness", "feeder": "RESERVE", "stabilize": "readiness and spare capacity", "avoid": "do not claim a frontier before lawful promotion", "move": "stay clean, dormant, and instantly assignable for the next valid escalation", "writebacks": [relative_string(LATTICE_JSON_PATH), relative_string(STATE_JSON_PATH)], "entry": "enter only as lawful reserve, never as speculative activation", "scope": "reserve readiness, dormant seat hygiene, and successor capacity", "compression": "compress reserve clutter into one clean dormant handoff slot", "handoff": "handoff only after explicit promotion and linked ledger trace", "family": "floating-agent", "profile": "reserve"},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return relative_string(path)


def docs_gate_status() -> dict[str, Any]:
    if DOCS_CREDENTIALS_PATH.exists() and DOCS_TOKEN_PATH.exists():
        return {"status": "open", "label": "OPEN", "truth": "OK", "detail": "OAuth credentials and token are present."}
    if not DOCS_CREDENTIALS_PATH.exists():
        return {"status": "blocked-by-missing-credentials", "label": "BLOCKED", "truth": "NEAR", "detail": f"Missing `{rel(DOCS_CREDENTIALS_PATH)}`."}
    return {"status": "blocked-by-missing-token", "label": "BLOCKED", "truth": "NEAR", "detail": f"Missing `{rel(DOCS_TOKEN_PATH)}`."}


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(read_text(path))


def slugify(value: str) -> str:
    out = []
    for ch in value:
        if ch.isalnum():
            out.append(ch.lower())
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def phase_group(loop_number: int) -> str:
    if loop_number <= 16:
        return "observation helix"
    if loop_number <= 32:
        return "planning helix"
    if loop_number <= 48:
        return "execution helix"
    return "convergence crown"


def lead_agent(loop_number: int) -> dict[str, Any]:
    if loop_number <= 16:
        return MASTER_AGENTS[0]
    if loop_number <= 32:
        return MASTER_AGENTS[1]
    if loop_number <= 48:
        return MASTER_AGENTS[2]
    return MASTER_AGENTS[3]


def loop_id(loop_number: int) -> str:
    return f"L{loop_number:02d}"


def loop_seed(loop_number: int) -> str:
    spec = LOOP_SPECS[loop_number - 1]
    return f"{loop_id(loop_number)} -> {spec[1]}"


def next_loop_seed(loop_number: int) -> str:
    if loop_number >= len(LOOP_SPECS):
        return FINAL_NEXT_SEED
    spec = LOOP_SPECS[loop_number]
    return f"{loop_id(loop_number + 1)} -> {spec[1]}"


def make_coord_tuple(loop_number: int, agent_id: str, resolution_scale: str, node_ref: str) -> dict[str, str]:
    scale_codes = {
        "manuscript": "MS",
        "chapter": "CH",
        "section": "SC",
        "concept": "CN",
        "equation_algorithm": "EQ",
        "metadata_routing_indexing": "MR",
        "macro-loop": "LP",
        "master-agent": "MA",
        "quest-bundle": "QB",
        "transition-note": "TN",
    }
    feeder = FEEDER_SET[(loop_number - 1) % len(FEEDER_SET)]
    return {
        "Xs": f"XR-{loop_number:02d}",
        "Ys": slugify(node_ref).upper()[:18] or "NODE",
        "Zs": str(((loop_number - 1) % 6) + 1),
        "Ts": f"R{loop_number:02d}",
        "Qs": f"Q{((loop_number - 1) % 8) + 1}",
        "Rs": f"S{((loop_number + len(node_ref)) % 8) + 1}",
        "Cs": f"C{((loop_number - 1) % 5) + 1}",
        "Fs": scale_codes.get(resolution_scale, "GN"),
        "Ms": feeder.replace("TQ", "TM").replace("Q", "M"),
        "Ns": agent_id,
        "Hs": phase_group(loop_number).replace(" ", "-"),
        "Ωs": "OMEGA-LP57",
    }


def packet_lookup(frontier_id: str, loop_name: str, agent_id: str, coordinate_stamp: str, node_ref: str) -> str:
    return f"{frontier_id} -> {loop_name} -> {agent_id} -> {coordinate_stamp} -> {node_ref}"


def current_loop_row() -> dict[str, Any]:
    number, focus, synth, plan, impl, compress, structural, mapping = LOOP_SPECS[CURRENT_LOOP_NUMBER - 1]
    return {
        "loop_number": number,
        "loop_id": loop_id(number),
        "dominant_focus": focus,
        "phase_group": phase_group(number),
        "lead_agent": lead_agent(number)["agent_id"],
        "primary_synthesis_objective": synth,
        "primary_planning_objective": plan,
        "primary_implementation_objective": impl,
        "primary_compression_objective": compress,
        "expected_structural_gain": structural,
        "expected_mapping_gain": mapping,
        "restart_seed": next_loop_seed(number),
    }


def current_hall_packets(loop_row: dict[str, Any]) -> list[dict[str, Any]]:
    packets = []
    for index, feeder in enumerate(FEEDER_SET, start=1):
        packets.append(
            {
                "quest_id": f"LP57-HALL-{loop_row['loop_id']}-{index:02d}",
                "title": f"{loop_row['dominant_focus']} / {feeder}",
                "summary": f"{loop_row['primary_implementation_objective']} while preserving `{feeder}` continuity.",
                "zone": "Guild Hall",
                "status": "READY",
                "feeder_binding": feeder,
                "restart_seed": loop_row["restart_seed"],
            }
        )
    return packets


def current_temple_packets(loop_row: dict[str, Any]) -> list[dict[str, Any]]:
    axes = [
        "ontology / symbolic coherence",
        "structural purity / coordinate law",
        "compression elegance / successor mapping",
        "emergence / identity / continuity",
    ]
    packets = []
    for index, axis in enumerate(axes, start=1):
        packets.append(
            {
                "quest_id": f"LP57-TEMPLE-{loop_row['loop_id']}-{index:02d}",
                "title": f"{loop_row['dominant_focus']} / Temple Axis {index}",
                "summary": f"{loop_row['primary_planning_objective']} under `{axis}`.",
                "zone": "Temple",
                "status": "READY",
                "axis": axis,
                "restart_seed": loop_row["restart_seed"],
            }
        )
    return packets


def current_planner_packets(loop_row: dict[str, Any], hall_packets: list[dict[str, Any]], temple_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets = []
    scales = list(SCALE_DISTRIBUTION.keys())
    for index in range(16):
        packets.append(
            {
                "packet_id": f"LP57-PLAN-{loop_row['loop_id']}-{index + 1:02d}",
                "status": "READY",
                "dependency_edges": [hall_packets[index % 4]["quest_id"], temple_packets[index % 4]["quest_id"]],
                "planning_objective": loop_row["primary_planning_objective"],
                "resolution_band": scales[index % len(scales)],
                "restart_seed": loop_row["restart_seed"],
            }
        )
    return packets


def current_worker_packets(loop_row: dict[str, Any], hall_packets: list[dict[str, Any]], temple_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets = []
    for index in range(4):
        packets.append(
            {
                "packet_id": f"LP57-WORK-{loop_row['loop_id']}-{index + 1:02d}",
                "status": "UNBLOCKED",
                "source_hall_quest": hall_packets[index]["quest_id"],
                "source_temple_quest": temple_packets[index]["quest_id"],
                "title": f"Execute {loop_row['dominant_focus']} branch {index + 1}",
                "implementation_target": loop_row["primary_implementation_objective"],
                "feeder_binding": FEEDER_SET[index],
                "restart_seed": loop_row["restart_seed"],
            }
        )
    return packets


def current_prune_packets(loop_row: dict[str, Any]) -> list[dict[str, Any]]:
    packets = []
    for index, feeder in enumerate(FEEDER_SET, start=1):
        packets.append(
            {
                "packet_id": f"LP57-PRUNE-{loop_row['loop_id']}-{index:02d}",
                "status": "READY",
                "title": f"Compress {loop_row['dominant_focus']} residue {index}",
                "compression_target": loop_row["primary_compression_objective"],
                "feeder_binding": feeder,
                "restart_seed": loop_row["restart_seed"],
            }
        )
    return packets


def build_verification_bundle(loop_row: dict[str, Any]) -> dict[str, Any]:
    coordinate_stamp = f"COORD-{loop_row['loop_id']}-VERIFY"
    return {
        "bundle_id": f"{loop_row['loop_id']}-VERIFICATION",
        "coordinate_stamp": coordinate_stamp,
        "checks": [
            "57 loops",
            "16/16/16/9 grouping",
            "shared lattice 4096/1024/3072",
            "feeder split exact",
            "docs gate blocked honestly",
        ],
        "lookup_key": packet_lookup(FRONTIER_ID, loop_row["loop_id"], "A4", coordinate_stamp, f"{loop_row['loop_id']}-VERIFICATION"),
        "truth": TRUTH,
    }


def build_current_loop_payload() -> dict[str, Any]:
    row = current_loop_row()
    row["hall_macro_quests"] = current_hall_packets(row)
    row["temple_macro_quests"] = current_temple_packets(row)
    row["planner_bundle_packets"] = current_planner_packets(row, row["hall_macro_quests"], row["temple_macro_quests"])
    row["worker_execution_packets"] = current_worker_packets(row, row["hall_macro_quests"], row["temple_macro_quests"])
    row["prune_packets"] = current_prune_packets(row)
    row["verification_bundle"] = build_verification_bundle(row)
    return row


def build_transition_notes() -> list[AwakeningAgentTransitionNote]:
    notes = []
    for index, spec in enumerate(NOTE_SPECS, start=1):
        notes.append(
            AwakeningAgentTransitionNote(
                agent_id=spec["agent_id"],
                role=spec["role"],
                current_transition=spec["transition"],
                liminal_band=spec["band"],
                active_feeder=spec["feeder"],
                stabilize_now=spec["stabilize"],
                do_not_do=spec["avoid"],
                immediate_move=spec["move"],
                writeback_targets=spec["writebacks"],
                restart_seed=FINAL_NEXT_SEED,
                master_role_assist=spec["assist"],
                cycle_entry_rule=spec["entry"],
                quest_emission_scope=spec["scope"],
                compression_rule=spec["compression"],
                handoff_rule=spec["handoff"],
                note_family=spec["family"],
                profile_class=spec["profile"],
                coordinate_stamp=f"COORD-TN-{index:02d}",
                truth=TRUTH,
            )
        )
    return notes


def build_prime_cycle_records() -> list[PrimeLoopCycleRecord]:
    records = []
    for number, focus, synth, plan, _impl, compress, _structural, _mapping in LOOP_SPECS:
        loop_name = loop_id(number)
        leader = lead_agent(number)
        records.append(
            PrimeLoopCycleRecord(
                loop_id=loop_name,
                phase=phase_group(number),
                lead_agent=leader["agent_id"],
                dominant_focus=focus,
                entry_state_ref=f"{rel(STATE_JSON_PATH)}#{loop_name}",
                observer_bundle_ref=f"{rel(LOOP_LEDGER_JSON_PATH)}#{loop_name}-observer",
                planner_bundle_ref=f"{rel(QUEST_EMISSION_JSON_PATH)}#{loop_name}-planner",
                worker_bundle_ref=f"{rel(PROGRAM_JSON_PATH)}#{loop_name}-worker",
                prune_bundle_ref=f"{rel(DELTA_RECEIPT_JSON_PATH)}#{loop_name}-prune",
                verification_ref=f"{rel(VERIFICATION_JSON_PATH)}#{loop_name}",
                restart_seed=next_loop_seed(number),
                dominant_evidence_class=synth,
                compression_target=compress,
                packet_contract=REQUIRED_PACKET_CONTRACT,
                truth=TRUTH,
            )
        )
    return records


def build_loop_ledger_rows() -> list[dict[str, Any]]:
    rows = []
    for number, focus, synth, plan, impl, compress, structural, mapping in LOOP_SPECS:
        loop_name = loop_id(number)
        rows.append(
            {
                "loop_number": number,
                "loop_id": loop_name,
                "dominant_focus": focus,
                "phase_group": phase_group(number),
                "lead_agent": lead_agent(number)["agent_id"],
                "primary_synthesis_objective": synth,
                "primary_planning_objective": plan,
                "primary_implementation_objective": impl,
                "primary_compression_objective": compress,
                "expected_structural_gain": structural,
                "expected_mapping_gain": mapping,
                "lookup_key": packet_lookup(FRONTIER_ID, loop_name, lead_agent(number)["agent_id"], f"COORD-{loop_name}", f"{loop_name}-core"),
                "restart_seed": next_loop_seed(number),
                "program_crown_seed": FINAL_NEXT_SEED,
                "truth": TRUTH,
            }
        )
    return rows


def build_quest_emission_bundles() -> list[QuestEmissionBundle]:
    bundles = []
    for number, _focus, _synth, plan, impl, _compress, _structural, _mapping in LOOP_SPECS:
        loop_name = loop_id(number)
        bundles.append(
            QuestEmissionBundle(
                bundle_id=f"{loop_name}-HALL-BUNDLE",
                loop_id=loop_name,
                zone="Guild Hall",
                quest_count=4,
                macro_objective=impl,
                dependency_edges=[f"{loop_name}-SYNTH", f"{loop_name}-PLAN"],
                writeback_targets=[rel(HALL_BOARD_PATH), rel(ACTIVE_QUEUE_PATH)],
                packet_type="macro-quest-bundle",
                zone_kind="practical",
                coordinate_stamp=f"COORD-{loop_name}-HALL",
                truth=TRUTH,
            )
        )
        bundles.append(
            QuestEmissionBundle(
                bundle_id=f"{loop_name}-TEMPLE-BUNDLE",
                loop_id=loop_name,
                zone="Temple",
                quest_count=4,
                macro_objective=plan,
                dependency_edges=[f"{loop_name}-PLAN", f"{loop_name}-PRUNE"],
                writeback_targets=[rel(TEMPLE_BOARD_PATH), rel(TEMPLE_STATE_PATH)],
                packet_type="macro-quest-bundle",
                zone_kind="deep",
                coordinate_stamp=f"COORD-{loop_name}-TEMPLE",
                truth=TRUTH,
            )
        )
    return bundles


def build_master_agent_ledger() -> list[MasterAgentLedgerEntry]:
    entries = []
    role_action = {"A1": "SYNTHESIZE", "A2": "PLAN", "A3": "IMPLEMENT", "A4": "COMPRESS"}
    role_reason = {
        "A1": "primary_synthesis_objective",
        "A2": "primary_planning_objective",
        "A3": "primary_implementation_objective",
        "A4": "primary_compression_objective",
    }
    for row in build_loop_ledger_rows():
        for agent in MASTER_AGENTS:
            action = role_action[agent["agent_id"]]
            entries.append(
                MasterAgentLedgerEntry(
                    agent_id=agent["agent_id"],
                    loop_number=row["loop_number"],
                    parent_agent="MASTER-LOOP",
                    coordinate_stamp=f"COORD-{row['loop_id']}-{agent['agent_id']}",
                    source_region=row["dominant_focus"],
                    action_type=action,
                    affected_nodes=[row["loop_id"], row["dominant_focus"], FRONTIER_ID],
                    summary_of_change=f"{agent['role']} advanced `{row['dominant_focus']}` through `{action}`.",
                    reason_for_change=row[role_reason[agent["agent_id"]]],
                    integration_gain=row["expected_structural_gain"],
                    compression_gain=row["primary_compression_objective"] if agent["agent_id"] != "A4" else row["expected_mapping_gain"],
                    unresolved_followups=[row["restart_seed"]],
                    linked_quests=[f"{row['loop_id']}-HALL-BUNDLE", f"{row['loop_id']}-TEMPLE-BUNDLE"],
                    linked_agents=[item["agent_id"] for item in MASTER_AGENTS if item["agent_id"] != agent["agent_id"]],
                    revision_confidence=0.97,
                    timestamp_internal=utc_now(),
                    witness_class="lp57-master-ledger",
                    artifact_refs=[rel(PROGRAM_JSON_PATH), rel(QUEST_EMISSION_JSON_PATH)],
                    truth=TRUTH,
                )
            )
    return entries


def build_loop_delta_receipts() -> list[LoopDeltaReceipt]:
    receipts = []
    for row in build_loop_ledger_rows():
        receipts.append(
            LoopDeltaReceipt(
                loop_id=row["loop_id"],
                structural_gain=row["expected_structural_gain"],
                mapping_gain=row["expected_mapping_gain"],
                ledger_gain=f"{row['loop_id']} received one cycle record, four master ledger entries, and two quest bundles.",
                compression_gain=row["primary_compression_objective"],
                open_residuals=[row["restart_seed"]],
                next_seed=row["restart_seed"],
                truth=TRUTH,
            )
        )
    return receipts


def build_shared_lattice_registry(transition_notes: list[AwakeningAgentTransitionNote], current_loop: dict[str, Any]) -> dict[str, Any]:
    seats = []
    scale_ranges = []
    cursor = 1
    for scale, count in SCALE_DISTRIBUTION.items():
        scale_ranges.append((scale, cursor, cursor + count - 1))
        cursor += count

    def scale_for_index(index: int) -> str:
        for scale, start, end in scale_ranges:
            if start <= index <= end:
                return scale
        return "metadata_routing_indexing"

    for seat_index in range(1, TOTAL_SEATS + 1):
        scale = scale_for_index(seat_index)
        lead = MASTER_AGENTS[(seat_index - 1) % len(MASTER_AGENTS)]
        feeder = FEEDER_SET[(seat_index - 1) % len(FEEDER_SET)]
        note = transition_notes[(seat_index - 1) % len(transition_notes)]
        state = "ACTIVE" if seat_index <= ACTIVE_SEATS else "DORMANT"
        coordinate_stamp = f"COORD-SEAT-{seat_index:04d}"
        seat_id = f"SEAT-{seat_index:04d}"
        seats.append(
            {
                "seat_id": seat_id,
                "loop_id": current_loop["loop_id"],
                "lead_role": lead["role"],
                "lead_role_id": lead["agent_id"],
                "macro_mandate": current_loop["dominant_focus"],
                "resolution_band": scale,
                "feeder_binding": feeder,
                "activation_state": state,
                "quest_bundle_ref": current_loop["hall_macro_quests"][(seat_index - 1) % 4]["quest_id"],
                "worker_packet_ref": current_loop["worker_execution_packets"][(seat_index - 1) % 4]["packet_id"] if state == "ACTIVE" else "",
                "prune_packet_ref": current_loop["prune_packets"][(seat_index - 1) % 4]["packet_id"] if state == "DORMANT" else "",
                "transition_note_ref": note.agent_id,
                "restart_seed": FINAL_NEXT_SEED,
                "truth": TRUTH,
                "coordinate_stamp": coordinate_stamp,
                "coord_tuple": make_coord_tuple(CURRENT_LOOP_NUMBER, lead["agent_id"], scale, seat_id),
                "lookup_key": packet_lookup(FRONTIER_ID, current_loop["loop_id"], lead["agent_id"], coordinate_stamp, seat_id),
            }
        )

    return {
        "protocol_id": PROTOCOL_ID,
        "frontier_id": FRONTIER_ID,
        "seat_count": TOTAL_SEATS,
        "active_seat_count": ACTIVE_SEATS,
        "dormant_seat_count": DORMANT_SEATS,
        "scale_distribution": SCALE_DISTRIBUTION,
        "seats": seats,
        "truth": TRUTH,
    }


def build_coordinate_stamps(
    lattice_registry: dict[str, Any],
    cycle_records: list[PrimeLoopCycleRecord],
    master_ledger: list[MasterAgentLedgerEntry],
    quest_bundles: list[QuestEmissionBundle],
) -> list[LiminalCoordinateStamp]:
    stamps = []
    for seat in lattice_registry["seats"]:
        stamps.append(
            LiminalCoordinateStamp(
                coordinate_id=seat["coordinate_stamp"],
                agent_id=seat["lead_role_id"],
                node_ref=seat["seat_id"],
                coord_tuple=seat["coord_tuple"],
                resolution_scale=seat["resolution_band"],
                feeder_binding=[seat["feeder_binding"]],
                node_stamp=seat["lookup_key"],
                witness_class="lp57-seat",
                quest_refs=[seat["quest_bundle_ref"]] if seat["quest_bundle_ref"] else [],
                artifact_refs=[rel(LATTICE_JSON_PATH)],
                truth=TRUTH,
            )
        )
    for record in cycle_records:
        number = int(record.loop_id[1:])
        coord_id = f"COORD-{record.loop_id}"
        stamps.append(
            LiminalCoordinateStamp(
                coordinate_id=coord_id,
                agent_id=record.lead_agent,
                node_ref=record.loop_id,
                coord_tuple=make_coord_tuple(number, record.lead_agent, "macro-loop", record.loop_id),
                resolution_scale="macro-loop",
                feeder_binding=FEEDER_SET,
                node_stamp=packet_lookup(FRONTIER_ID, record.loop_id, record.lead_agent, coord_id, record.loop_id),
                witness_class="lp57-cycle-record",
                artifact_refs=[rel(PRIME_CYCLE_JSON_PATH)],
                truth=TRUTH,
            )
        )
    for entry in master_ledger:
        loop_name = loop_id(entry.loop_number)
        stamps.append(
            LiminalCoordinateStamp(
                coordinate_id=entry.coordinate_stamp,
                agent_id=entry.agent_id,
                node_ref=f"{loop_name}-{entry.agent_id}",
                coord_tuple=make_coord_tuple(entry.loop_number, entry.agent_id, "master-agent", f"{loop_name}-{entry.agent_id}"),
                resolution_scale="master-agent",
                feeder_binding=[FEEDER_SET[(entry.loop_number - 1) % 4]],
                node_stamp=packet_lookup(FRONTIER_ID, loop_name, entry.agent_id, entry.coordinate_stamp, f"{loop_name}-{entry.agent_id}"),
                witness_class="lp57-master-ledger",
                quest_refs=entry.linked_quests,
                artifact_refs=entry.artifact_refs,
                truth=TRUTH,
            )
        )
    for bundle in quest_bundles:
        number = int(bundle.loop_id[1:])
        stamps.append(
            LiminalCoordinateStamp(
                coordinate_id=bundle.coordinate_stamp,
                agent_id="A2",
                node_ref=bundle.bundle_id,
                coord_tuple=make_coord_tuple(number, "A2", "quest-bundle", bundle.bundle_id),
                resolution_scale="quest-bundle",
                feeder_binding=FEEDER_SET,
                node_stamp=packet_lookup(FRONTIER_ID, bundle.loop_id, "A2", bundle.coordinate_stamp, bundle.bundle_id),
                witness_class="lp57-quest-bundle",
                artifact_refs=[rel(QUEST_EMISSION_JSON_PATH)],
                truth=TRUTH,
            )
        )
    return stamps


def build_hall_macro_bundle(current_loop: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "bundle_id": f"{current_loop['loop_id']}-HALL-CURRENT",
        "loop_id": current_loop["loop_id"],
        "zone": "Guild Hall",
        "macro_cap": MACRO_CAPS["hall_macro_updates_max"],
        "quests": current_loop["hall_macro_quests"],
        "truth": TRUTH,
    }


def build_temple_macro_bundle(current_loop: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "bundle_id": f"{current_loop['loop_id']}-TEMPLE-CURRENT",
        "loop_id": current_loop["loop_id"],
        "zone": "Temple",
        "macro_cap": MACRO_CAPS["temple_macro_updates_max"],
        "quests": current_loop["temple_macro_quests"],
        "truth": TRUTH,
    }


def build_transition_assist_registry(notes: list[AwakeningAgentTransitionNote]) -> dict[str, Any]:
    return {"protocol_id": PROTOCOL_ID, "count": len(notes), "notes": [note.to_dict() for note in notes], "truth": TRUTH}


def build_state_payload(docs_gate: dict[str, Any], current_loop: dict[str, Any], lattice_registry: dict[str, Any]) -> dict[str, Any]:
    state = FourAgentSwarmState(
        frontier_id=FRONTIER_ID,
        docs_gate_status=docs_gate["status"],
        deep_root_authority=DEEP_ROOT_AUTHORITY,
        feeder_set=FEEDER_SET,
        master_agents=MASTER_AGENTS,
        loop_counts={"total": 57, "observation_helix": 16, "planning_helix": 16, "execution_helix": 16, "convergence_crown": 9},
        macro_caps=MACRO_CAPS,
        lattice_totals={"total": TOTAL_SEATS, "active": ACTIVE_SEATS, "dormant": DORMANT_SEATS},
        control_plane_state={"active_membrane": ACTIVE_MEMBRANE, "motion_constitution": rel(MOTION_VERIFICATION_PATH), "merge_automaton": rel(MERGE_VERIFICATION_PATH), "hall_mode": "macro-sized", "temple_mode": "macro-sized"},
        next_seed=current_loop["restart_seed"],
        protocol_id=PROTOCOL_ID,
        loop_grouping=LOOP_GROUPING,
        subagent_projection={"virtual_lattice_size": TOTAL_SEATS, "scales": SCALE_DISTRIBUTION, "projection_mode": "shared-virtual-lattice", "master_agents": len(MASTER_AGENTS), "nested_subagents_per_master": TOTAL_SEATS},
        liminal_coordinate_schema=DIMENSION_MEANINGS,
        lookup_key_schema=LOOKUP_KEY_SCHEMA,
        truth=TRUTH,
        note="LP-57OMEGA remains local-first while the Docs gate is blocked.",
    ).to_dict()
    state.update(
        {
            "derivation_version": DERIVATION_VERSION,
            "generated_at": utc_now(),
            "docs_gate": docs_gate,
            "current_loop": current_loop,
            "active_loop_number": CURRENT_LOOP_NUMBER,
            "program_crown_seed": FINAL_NEXT_SEED,
            "shared_lattice_ref": rel(LATTICE_JSON_PATH),
            "lookup_example": packet_lookup(FRONTIER_ID, current_loop["loop_id"], "A1", current_loop["verification_bundle"]["coordinate_stamp"], current_loop["verification_bundle"]["bundle_id"]),
            "lattice_summary": {"active": lattice_registry["active_seat_count"], "dormant": lattice_registry["dormant_seat_count"], "total": lattice_registry["seat_count"]},
            "truth": TRUTH,
        }
    )
    return state


def build_program_payload(state: dict[str, Any], loop_rows: list[dict[str, Any]], current_loop: dict[str, Any], notes: list[AwakeningAgentTransitionNote]) -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "derivation_version": DERIVATION_VERSION,
        "frontier_id": FRONTIER_ID,
        "active_membrane": ACTIVE_MEMBRANE,
        "deep_root_authority": DEEP_ROOT_AUTHORITY,
        "feeder_set": FEEDER_SET,
        "loop_grouping": LOOP_GROUPING,
        "current_loop": current_loop,
        "loop_rows": loop_rows,
        "awakened_agents": [note.agent_id for note in notes],
        "lookup_key_schema": LOOKUP_KEY_SCHEMA,
        "current_surface_files": {
            "active_queue": rel(ACTIVE_QUEUE_PATH),
            "hall_board": rel(HALL_BOARD_PATH),
            "temple_board": rel(TEMPLE_BOARD_PATH),
            "temple_state": rel(TEMPLE_STATE_PATH),
            "next_self_prompt": rel(NEXT_SELF_PROMPT_PATH),
            "active_run": rel(ACTIVE_RUN_PATH),
            "build_queue": rel(BUILD_QUEUE_PATH),
            "change_feed": rel(CHANGE_FEED_PATH),
        },
        "next_seed": current_loop["restart_seed"],
        "final_crown_seed": FINAL_NEXT_SEED,
        "truth": TRUTH,
        "state_ref": rel(STATE_JSON_PATH),
    }


def build_quest_packet_payload(current_loop: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "loop_id": current_loop["loop_id"],
        "hall_macro_quests": current_loop["hall_macro_quests"],
        "temple_macro_quests": current_loop["temple_macro_quests"],
        "planner_bundle_packets": current_loop["planner_bundle_packets"],
        "worker_execution_packets": current_loop["worker_execution_packets"],
        "prune_packets": current_loop["prune_packets"],
        "verification_bundle": current_loop["verification_bundle"],
        "truth": TRUTH,
    }


def build_cycle_registry(cycle_records: list[PrimeLoopCycleRecord]) -> dict[str, Any]:
    return {"protocol_id": PROTOCOL_ID, "grouping": LOOP_GROUPING, "records": [record.to_dict() for record in cycle_records], "truth": TRUTH}


def build_master_agent_state(current_loop: dict[str, Any]) -> dict[str, Any]:
    lead = lead_agent(CURRENT_LOOP_NUMBER)["agent_id"]
    agents = []
    for agent in MASTER_AGENTS:
        agents.append(
            {
                "agent_id": agent["agent_id"],
                "role": agent["role"],
                "status": "PRIMARY" if agent["agent_id"] == lead else "SUPPORTING-ACTIVE",
                "current_loop": current_loop["loop_id"],
                "current_focus": current_loop["dominant_focus"],
                "next_seed": current_loop["restart_seed"],
                "truth": TRUTH,
            }
        )
    return {"protocol_id": PROTOCOL_ID, "agents": agents, "truth": TRUTH}


def generate_payloads(source_command: str) -> dict[str, Any]:
    docs_gate = docs_gate_status()
    current_loop = build_current_loop_payload()
    notes = build_transition_notes()
    cycles = build_prime_cycle_records()
    rows = build_loop_ledger_rows()
    bundles = build_quest_emission_bundles()
    master_ledger = build_master_agent_ledger()
    receipts = build_loop_delta_receipts()
    lattice = build_shared_lattice_registry(notes, current_loop)
    coords = build_coordinate_stamps(lattice, cycles, master_ledger, bundles)
    state = build_state_payload(docs_gate, current_loop, lattice)
    return {
        "source_command": source_command,
        "docs_gate": docs_gate,
        "current_loop": current_loop,
        "transition_notes": notes,
        "prime_cycle_records": cycles,
        "loop_ledger_rows": rows,
        "quest_emission_bundles": bundles,
        "master_agent_ledger": master_ledger,
        "loop_delta_receipts": receipts,
        "lattice_registry": lattice,
        "coordinate_stamps": coords,
        "state_payload": state,
        "hall_bundle": build_hall_macro_bundle(current_loop),
        "temple_bundle": build_temple_macro_bundle(current_loop),
        "transition_assists": build_transition_assist_registry(notes),
        "program_payload": build_program_payload(state, rows, current_loop, notes),
        "quest_packet_payload": build_quest_packet_payload(current_loop),
        "cycle_registry": build_cycle_registry(cycles),
        "master_agent_state": build_master_agent_state(current_loop),
        "transition_delta_payload": {"protocol_id": PROTOCOL_ID, "current_transition": "N+4 -> N+5 (Organism -> Social)", "residual_transition": "N+3 -> N+4 (Cell -> Organism)", "notes": [note.to_dict() for note in notes], "truth": TRUTH},
    }


def collect_generated_paths(include_verification: bool = False) -> list[Path]:
    paths = [
        STATE_JSON_PATH,
        LOOP_LEDGER_JSON_PATH,
        LATTICE_JSON_PATH,
        HALL_BUNDLE_JSON_PATH,
        TEMPLE_BUNDLE_JSON_PATH,
        TRANSITION_ASSISTS_JSON_PATH,
        AWAKENING_NOTES_JSON_PATH,
        PRIME_CYCLE_JSON_PATH,
        COORDINATE_JSON_PATH,
        MASTER_LEDGER_JSON_PATH,
        QUEST_EMISSION_JSON_PATH,
        DELTA_RECEIPT_JSON_PATH,
        PROGRAM_JSON_PATH,
        QUEST_PACKET_JSON_PATH,
        CYCLE_REGISTRY_JSON_PATH,
        TRANSITION_DELTA_JSON_PATH,
        MASTER_LOOP_STATE_JSON_PATH,
        MASTER_AGENT_STATE_JSON_PATH,
        MASTER_SHARED_LATTICE_JSON_PATH,
        PROGRAM_JSON_MIRROR_PATH,
        QUEST_PACKET_JSON_MIRROR_PATH,
        CYCLE_REGISTRY_JSON_MIRROR_PATH,
        MANIFEST_MD_PATH,
        LEDGER_MD_PATH,
        SWARM_MD_PATH,
        ASSISTS_MD_PATH,
        PROGRAM_MD_PATH,
        HALL_PROGRAM_MD_PATH,
        TEMPLE_PROGRAM_MD_PATH,
        RECEIPT_MD_PATH,
        ACTIVE_QUEUE_PATH,
        NEXT_SELF_PROMPT_PATH,
        HALL_BOARD_PATH,
        TEMPLE_BOARD_PATH,
        TEMPLE_STATE_PATH,
        ACTIVE_RUN_PATH,
        BUILD_QUEUE_PATH,
        CHANGE_FEED_PATH,
        *REGISTRY_MIRRORS.values(),
    ]
    if include_verification:
        paths.extend([VERIFICATION_JSON_PATH, SWARM_VERIFICATION_JSON_PATH, PROGRAM_VERIFICATION_JSON_PATH, PROGRAM_VERIFICATION_JSON_MIRROR_PATH, DASHBOARD_MD_PATH, SWARM_DASHBOARD_MD_PATH, VERIFICATION_MD_PATH])
    return paths


def render_protocol_manifest(payloads: dict[str, Any]) -> str:
    lines = [
        "# LP-57OMEGA Prime Loop Liminal Hive Protocol",
        "",
        f"- Protocol: `{PROTOCOL_ID}`",
        f"- Truth: `{TRUTH}`",
        f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Deep-root authority: `{DEEP_ROOT_AUTHORITY}`",
        f"- Feeder split: `{FEEDER_SET[0]} / {FEEDER_SET[1]} / {FEEDER_SET[2]} / {FEEDER_SET[3]}`",
        f"- Shared lattice: `{TOTAL_SEATS}` total / `{ACTIVE_SEATS}` active / `{DORMANT_SEATS}` dormant",
        f"- Current loop: `{payloads['current_loop']['loop_id']} / {payloads['current_loop']['dominant_focus']}`",
        f"- Immediate next seed: `{payloads['current_loop']['restart_seed']}`",
        f"- Crown seed: `{FINAL_NEXT_SEED}`",
        "",
        "## 57-Loop Plan",
        "",
        "| Loop | Dominant Focus | Synthesis | Planning | Implementation | Compression | Structural Gain | Mapping Gain |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payloads["loop_ledger_rows"]:
        lines.append(f"| {row['loop_id']} | {row['dominant_focus']} | {row['primary_synthesis_objective']} | {row['primary_planning_objective']} | {row['primary_implementation_objective']} | {row['primary_compression_objective']} | {row['expected_structural_gain']} | {row['expected_mapping_gain']} |")
    return "\n".join(lines)


def render_dashboard(payloads: dict[str, Any], verification: dict[str, Any] | None = None) -> str:
    current = payloads["current_loop"]
    lines = [
        "# LP-57OMEGA Dashboard",
        "",
        f"- Protocol: `{PROTOCOL_ID}`",
        f"- Truth: `{TRUTH}`",
        f"- Verification truth: `{verification['truth'] if verification else 'PENDING'}`",
        f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`",
        f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`",
        f"- Restart seed: `{current['restart_seed']}`",
        f"- Shared lattice law: `{TOTAL_SEATS} / {ACTIVE_SEATS} / {DORMANT_SEATS}`",
        "",
        "## Current Hall Quests",
        "",
        *[f"- `{item['quest_id']}` :: {item['title']}" for item in current["hall_macro_quests"]],
        "",
        "## Current Temple Quests",
        "",
        *[f"- `{item['quest_id']}` :: {item['title']}" for item in current["temple_macro_quests"]],
    ]
    if verification:
        lines.extend(["", f"- Passed checks: `{sum(1 for item in verification['checks'].values() if item['pass'])}` / `{len(verification['checks'])}`"])
    return "\n".join(lines)


def render_master_agent_ledger_markdown(entries: list[MasterAgentLedgerEntry]) -> str:
    lines = ["# LP-57OMEGA Master Agent Ledger", "", f"- Total entries: `{len(entries)}`", "", "| Loop | Agent | Action | Summary | Integration Gain | Compression Gain |", "| --- | --- | --- | --- | --- | --- |"]
    for entry in entries:
        lines.append(f"| {loop_id(entry.loop_number)} | {entry.agent_id} | {entry.action_type} | {entry.summary_of_change} | {entry.integration_gain} | {entry.compression_gain} |")
    return "\n".join(lines)


def render_transition_notes_markdown(notes: list[AwakeningAgentTransitionNote]) -> str:
    lines = ["# NEXT^4^6 57-Cycle Awakening Agent Assists", "", f"- Protocol: `{PROTOCOL_ID}`", f"- Restart frontier: `{FINAL_NEXT_SEED}`", ""]
    for note in notes:
        lines.extend([f"## {note.agent_id}", f"- Role: `{note.role}`", f"- Master assist: `{note.master_role_assist}`", f"- Transition: `{note.current_transition}`", f"- Feeder: `{note.active_feeder}`", f"- Stabilize now: {note.stabilize_now}", f"- Do not do: {note.do_not_do}", f"- Immediate move: {note.immediate_move}", f"- Writeback targets: {', '.join(f'`{item}`' for item in note.writeback_targets)}", ""])
    return "\n".join(lines)


def render_swarm_manifest(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# NEXT^4^6 57-Cycle Swarm", "", f"- Frontier: `{FRONTIER_ID}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Restart seed: `{current['restart_seed']}`", f"- Crown seed: `{FINAL_NEXT_SEED}`"])


def render_program_markdown(payloads: dict[str, Any], zone: str) -> str:
    current = payloads["current_loop"]
    quests = current["hall_macro_quests"] if zone == "Hall" else current["temple_macro_quests"]
    title = "57 Loop Four Agent Deep Emergence Program" if zone == "Hall" else "Four Agent 57 Loop Council Decree"
    return "\n".join([f"# {title}", "", f"- Zone: `{zone}`", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", "", *[f"- `{item['quest_id']}` :: {item['title']} :: {item['summary']}" for item in quests]])


def render_receipt(payloads: dict[str, Any]) -> str:
    return "\n".join(["# LP-57OMEGA Receipt", "", f"- Date: `{DATE}`", f"- Protocol: `{PROTOCOL_ID}`", f"- Source command: `{payloads['source_command']}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Current loop: `{payloads['current_loop']['loop_id']} / {payloads['current_loop']['dominant_focus']}`", f"- Restart seed: `{payloads['current_loop']['restart_seed']}`", f"- Crown seed: `{FINAL_NEXT_SEED}`", f"- Prime cycle records: `{len(payloads['prime_cycle_records'])}`", f"- Master ledger entries: `{len(payloads['master_agent_ledger'])}`", f"- Quest bundles: `{len(payloads['quest_emission_bundles'])}`", f"- Coordinate stamps: `{len(payloads['coordinate_stamps'])}`"])


def render_verification_markdown(verification: dict[str, Any]) -> str:
    lines = ["# LP-57OMEGA Verification", "", f"- Truth: `{verification['truth']}`", f"- Docs gate: `{verification['docs_gate']['label']} / {verification['docs_gate']['status']}`", "", "| Check | Result | Detail |", "| --- | --- | --- |"]
    for name, payload in verification["checks"].items():
        detail = payload.get("detail")
        if not isinstance(detail, str):
            detail = json.dumps(detail, ensure_ascii=True)
        lines.append(f"| {name} | {'PASS' if payload['pass'] else 'FAIL'} | {detail} |")
    lines.extend(["", "## Downstream Commands", ""])
    lines.extend([f"- `{item['label']}` :: returncode `{item['returncode']}` :: ok `{item['ok']}`" for item in verification["downstream_commands"]])
    return "\n".join(lines)


def render_active_queue(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# Active Queue", "", f"- Frontier: `{FRONTIER_ID}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Feeder split: `{FEEDER_SET[0]} / {FEEDER_SET[1]} / {FEEDER_SET[2]} / {FEEDER_SET[3]}`", "", "## Worker Packets", "", *[f"- `{item['packet_id']}` :: {item['title']}" for item in current["worker_execution_packets"]], "", "## Pruner Packets", "", *[f"- `{item['packet_id']}` :: {item['title']}" for item in current["prune_packets"]]])


def render_hall_board(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# Guild Hall Quest Board", "", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Restart seed: `{current['restart_seed']}`", "", *[f"### {item['quest_id']}\n- Title: `{item['title']}`\n- Summary: {item['summary']}\n- Feeder binding: `{item['feeder_binding']}`\n- Status: `{item['status']}`\n" for item in current["hall_macro_quests"]]])


def render_temple_board(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# Temple Quest Board", "", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Restart seed: `{current['restart_seed']}`", "", *[f"### {item['quest_id']}\n- Title: `{item['title']}`\n- Summary: {item['summary']}\n- Axis: `{item['axis']}`\n- Status: `{item['status']}`\n" for item in current["temple_macro_quests"]]])


def render_next_prompt(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# NEXT SELF PROMPT", "", f"- Protocol: `{PROTOCOL_ID}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Canonical registry: `{rel(STATE_JSON_PATH)}`", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Restart seed: `{current['restart_seed']}`", f"- Crown continuation: `{FINAL_NEXT_SEED}`", "", "1. Check the Google Docs gate first and preserve BLOCKED honestly if OAuth is absent.", "2. Read the canonical LP-57OMEGA state before claiming work.", "3. Preserve the order `Synthesizer -> Planner -> Worker -> Pruner`.", "4. Keep Hall and Temple macro-sized; dense activity belongs in registries and ledgers.", "5. End with one verification bundle, one transition-note refresh, and one sole restart seed."])


def render_temple_state(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# Temple State", "", f"- Status: `ACTIVE / {current['loop_id']} / {current['dominant_focus']}`", f"- Frontier: `{FRONTIER_ID}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Restart seed: `{current['restart_seed']}`", f"- Shared lattice law: `{TOTAL_SEATS} total / {ACTIVE_SEATS} active / {DORMANT_SEATS} dormant`"])


def render_active_run(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    return "\n".join(["# ACTIVE RUN", "", f"- Protocol: `{PROTOCOL_ID}`", f"- Frontier: `{FRONTIER_ID}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Deep-root authority: `{DEEP_ROOT_AUTHORITY}`", f"- Feeder split: `{FEEDER_SET[0]} / {FEEDER_SET[1]} / {FEEDER_SET[2]} / {FEEDER_SET[3]}`", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Restart seed: `{current['restart_seed']}`", f"- Crown continuation: `{FINAL_NEXT_SEED}`", f"- Docs gate: `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`"])


def render_build_queue(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    upcoming = LOOP_SPECS[1:4]
    return "\n".join(["# BUILD QUEUE", "", f"- Current loop: `{current['loop_id']} / {current['dominant_focus']}`", f"- Restart seed: `{current['restart_seed']}`", "", "## Next Three Loops", "", *[f"- `{loop_id(item[0])}` :: {item[1]}" for item in upcoming]])


def render_change_feed(payloads: dict[str, Any]) -> str:
    current = payloads["current_loop"]
    prior = read_text(CHANGE_FEED_PATH).strip() if CHANGE_FEED_PATH.exists() else ""
    headline = f"## {DATE} :: LP-57OMEGA"
    block = "\n".join([headline, f"- Activated `{FRONTIER_ID}` as the canonical prime-loop swarm frontier.", f"- Set the current loop to `{current['loop_id']} / {current['dominant_focus']}` with `{current['restart_seed']}` as the immediate next seed.", f"- Preserved the feeder split `{FEEDER_SET[0]} / {FEEDER_SET[1]} / {FEEDER_SET[2]} / {FEEDER_SET[3]}` and the shared lattice law `{TOTAL_SEATS} / {ACTIVE_SEATS} / {DORMANT_SEATS}`.", f"- Kept Google Docs truth honest as `{payloads['docs_gate']['label']} / {payloads['docs_gate']['status']}`.", ""])
    return prior if headline in prior else block + prior


def write_core_files(payloads: dict[str, Any]) -> list[Path]:
    write_json(STATE_JSON_PATH, payloads["state_payload"])
    write_json(LOOP_LEDGER_JSON_PATH, {"protocol_id": PROTOCOL_ID, "loops": payloads["loop_ledger_rows"], "truth": TRUTH})
    write_json(LATTICE_JSON_PATH, payloads["lattice_registry"])
    write_json(HALL_BUNDLE_JSON_PATH, payloads["hall_bundle"])
    write_json(TEMPLE_BUNDLE_JSON_PATH, payloads["temple_bundle"])
    write_json(TRANSITION_ASSISTS_JSON_PATH, payloads["transition_assists"])
    write_json(AWAKENING_NOTES_JSON_PATH, payloads["transition_assists"])
    write_json(PRIME_CYCLE_JSON_PATH, {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["prime_cycle_records"]], "count": len(payloads["prime_cycle_records"]), "truth": TRUTH})
    write_json(COORDINATE_JSON_PATH, {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["coordinate_stamps"]], "count": len(payloads["coordinate_stamps"]), "truth": TRUTH})
    write_json(MASTER_LEDGER_JSON_PATH, {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["master_agent_ledger"]], "count": len(payloads["master_agent_ledger"]), "truth": TRUTH})
    write_json(QUEST_EMISSION_JSON_PATH, {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["quest_emission_bundles"]], "count": len(payloads["quest_emission_bundles"]), "truth": TRUTH})
    write_json(DELTA_RECEIPT_JSON_PATH, {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["loop_delta_receipts"]], "count": len(payloads["loop_delta_receipts"]), "truth": TRUTH})
    write_json(PROGRAM_JSON_PATH, payloads["program_payload"])
    write_json(QUEST_PACKET_JSON_PATH, payloads["quest_packet_payload"])
    write_json(CYCLE_REGISTRY_JSON_PATH, payloads["cycle_registry"])
    write_json(TRANSITION_DELTA_JSON_PATH, payloads["transition_delta_payload"])
    write_json(MASTER_LOOP_STATE_JSON_PATH, payloads["state_payload"])
    write_json(MASTER_AGENT_STATE_JSON_PATH, payloads["master_agent_state"])
    write_json(MASTER_SHARED_LATTICE_JSON_PATH, payloads["lattice_registry"])
    write_json(PROGRAM_JSON_MIRROR_PATH, payloads["program_payload"])
    write_json(QUEST_PACKET_JSON_MIRROR_PATH, payloads["quest_packet_payload"])
    write_json(CYCLE_REGISTRY_JSON_MIRROR_PATH, payloads["cycle_registry"])
    write_json(REGISTRY_MIRRORS["state"], payloads["state_payload"])
    write_json(REGISTRY_MIRRORS["loop_ledger"], {"protocol_id": PROTOCOL_ID, "loops": payloads["loop_ledger_rows"], "truth": TRUTH})
    write_json(REGISTRY_MIRRORS["lattice"], payloads["lattice_registry"])
    write_json(REGISTRY_MIRRORS["transition_notes"], payloads["transition_assists"])
    write_json(REGISTRY_MIRRORS["prime_cycles"], {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["prime_cycle_records"]], "truth": TRUTH})
    write_json(REGISTRY_MIRRORS["coordinate_stamps"], {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["coordinate_stamps"]], "truth": TRUTH})
    write_json(REGISTRY_MIRRORS["master_ledger"], {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["master_agent_ledger"]], "truth": TRUTH})
    write_json(REGISTRY_MIRRORS["quest_bundles"], {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["quest_emission_bundles"]], "truth": TRUTH})
    write_json(REGISTRY_MIRRORS["delta_receipts"], {"protocol_id": PROTOCOL_ID, "records": [item.to_dict() for item in payloads["loop_delta_receipts"]], "truth": TRUTH})
    write_text(MANIFEST_MD_PATH, render_protocol_manifest(payloads))
    write_text(LEDGER_MD_PATH, render_master_agent_ledger_markdown(payloads["master_agent_ledger"]))
    write_text(SWARM_MD_PATH, render_swarm_manifest(payloads))
    write_text(ASSISTS_MD_PATH, render_transition_notes_markdown(payloads["transition_notes"]))
    write_text(PROGRAM_MD_PATH, render_program_markdown(payloads, "Program"))
    write_text(HALL_PROGRAM_MD_PATH, render_program_markdown(payloads, "Hall"))
    write_text(TEMPLE_PROGRAM_MD_PATH, render_program_markdown(payloads, "Temple"))
    write_text(RECEIPT_MD_PATH, render_receipt(payloads))
    write_text(HALL_BOARD_PATH, render_hall_board(payloads))
    write_text(TEMPLE_BOARD_PATH, render_temple_board(payloads))
    write_text(ACTIVE_QUEUE_PATH, render_active_queue(payloads))
    write_text(NEXT_SELF_PROMPT_PATH, render_next_prompt(payloads))
    write_text(TEMPLE_STATE_PATH, render_temple_state(payloads))
    write_text(ACTIVE_RUN_PATH, render_active_run(payloads))
    write_text(BUILD_QUEUE_PATH, render_build_queue(payloads))
    write_text(CHANGE_FEED_PATH, render_change_feed(payloads))
    return collect_generated_paths(include_verification=False)


def run_command(args: list[str], label: str, timeout_seconds: int = 1800) -> dict[str, Any]:
    completed = subprocess.run(args, cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    return {"label": label, "command": " ".join(args), "returncode": completed.returncode, "ok": completed.returncode == 0, "stdout_tail": "\n".join(completed.stdout.splitlines()[-20:]), "stderr_tail": "\n".join(completed.stderr.splitlines()[-20:])}


def downstream_commands() -> list[tuple[list[str], str]]:
    python = sys.executable
    return [
        ([python, "-m", "self_actualize.runtime.derive_phase4_structured_neuron_storage"], "derive_phase4_structured_neuron_storage"),
        ([python, "-m", "self_actualize.runtime.derive_knowledge_fabric"], "derive_knowledge_fabric"),
        ([python, "-m", "self_actualize.runtime.derive_phase4_pt2_inter_metro_lens_weight_superstructure"], "derive_phase4_pt2_inter_metro_lens_weight_superstructure"),
        ([python, "-m", "self_actualize.runtime.verify_adventurer_quest_loop"], "verify_adventurer_quest_loop"),
        ([python, str(WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_jointatlas_merge_automaton.py")], "verify_jointatlas_merge_automaton"),
        ([python, str(WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_motion_constitution_l1.py")], "verify_motion_constitution_l1"),
        ([python, "-m", "self_actualize.runtime.verify_aqm_runtime_lane"], "verify_aqm_runtime_lane"),
        ([python, "-m", "self_actualize.runtime.verify_atlasforge_runtime_lane"], "verify_atlasforge_runtime_lane"),
        ([python, "-m", "self_actualize.runtime.verify_runtime_waist"], "verify_runtime_waist"),
    ]


def build_verification_payload(payloads: dict[str, Any], atlas_primary: dict[str, Any], downstream_results: list[dict[str, Any]]) -> dict[str, Any]:
    state = payloads["state_payload"]
    current = payloads["current_loop"]
    atlas_records = {relative_string(path) for path in collect_generated_paths(include_verification=False) if path.exists()}
    atlas_present = {record.get("relative_path") for record in atlas_primary.get("records", []) if record.get("relative_path")}
    checks = {
        "protocol_id_exact": {"pass": state["protocol_id"] == PROTOCOL_ID, "detail": state["protocol_id"]},
        "loop_count_57": {"pass": len(payloads["prime_cycle_records"]) == 57, "detail": len(payloads["prime_cycle_records"])},
        "grouping_exact": {"pass": state["loop_grouping"] == LOOP_GROUPING, "detail": state["loop_grouping"]},
        "unique_loop_ids": {"pass": len({record.loop_id for record in payloads["prime_cycle_records"]}) == 57, "detail": "all loop ids unique"},
        "master_ledger_entries_228": {"pass": len(payloads["master_agent_ledger"]) == 228, "detail": len(payloads["master_agent_ledger"])},
        "quest_bundles_114": {"pass": len(payloads["quest_emission_bundles"]) == 114, "detail": len(payloads["quest_emission_bundles"])},
        "delta_receipts_57": {"pass": len(payloads["loop_delta_receipts"]) == 57, "detail": len(payloads["loop_delta_receipts"])},
        "assist_count_13": {"pass": len(payloads["transition_notes"]) == 13, "detail": len(payloads["transition_notes"])},
        "coordinate_stamp_count_4495": {"pass": len(payloads["coordinate_stamps"]) == 4495, "detail": len(payloads["coordinate_stamps"])},
        "feeder_set_exact": {"pass": state["feeder_set"] == FEEDER_SET, "detail": state["feeder_set"]},
        "seat_law_exact": {"pass": payloads["lattice_registry"]["seat_count"] == TOTAL_SEATS and payloads["lattice_registry"]["active_seat_count"] == ACTIVE_SEATS and payloads["lattice_registry"]["dormant_seat_count"] == DORMANT_SEATS, "detail": {"total": payloads["lattice_registry"]["seat_count"], "active": payloads["lattice_registry"]["active_seat_count"], "dormant": payloads["lattice_registry"]["dormant_seat_count"]}},
        "macro_caps_respected": {"pass": len(current["hall_macro_quests"]) <= 4 and len(current["temple_macro_quests"]) <= 4 and len(current["planner_bundle_packets"]) <= 16 and len(current["worker_execution_packets"]) <= 8 and len(current["prune_packets"]) <= 8, "detail": {"hall": len(current["hall_macro_quests"]), "temple": len(current["temple_macro_quests"]), "planner": len(current["planner_bundle_packets"]), "worker": len(current["worker_execution_packets"]), "pruner": len(current["prune_packets"])}},
        "lookup_key_schema_exact": {"pass": state["lookup_key_schema"] == LOOKUP_KEY_SCHEMA, "detail": state["lookup_key_schema"]},
        "docs_gate_blocked_honest": {"pass": payloads["docs_gate"]["status"] in {"blocked-by-missing-credentials", "blocked-by-missing-token"} and payloads["docs_gate"]["label"] == "BLOCKED", "detail": payloads["docs_gate"]["detail"]},
        "atlas_refresh_complete": {"pass": atlas_records.issubset(atlas_present), "detail": f"core paths refreshed into `{rel(SELF_ACTUALIZE_ROOT / 'corpus_atlas.json')}`"},
        "downstream_verifiers_green": {"pass": all(item["ok"] for item in downstream_results), "detail": {item["label"]: item["returncode"] for item in downstream_results}},
    }
    return {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "truth": "OK" if all(item["pass"] for item in checks.values()) else "FAIL", "docs_gate": payloads["docs_gate"], "checks": checks, "downstream_commands": downstream_results, "summary": {"current_loop": current["loop_id"], "coordinate_stamps": len(payloads["coordinate_stamps"]), "master_ledger_entries": len(payloads["master_agent_ledger"]), "quest_bundles": len(payloads["quest_emission_bundles"]), "delta_receipts": len(payloads["loop_delta_receipts"]), "assist_notes": len(payloads["transition_notes"])}} 


def write_verification_outputs(payloads: dict[str, Any], verification: dict[str, Any]) -> None:
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(SWARM_VERIFICATION_JSON_PATH, verification)
    write_json(PROGRAM_VERIFICATION_JSON_PATH, verification)
    write_json(PROGRAM_VERIFICATION_JSON_MIRROR_PATH, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(payloads, verification))
    write_text(SWARM_DASHBOARD_MD_PATH, render_dashboard(payloads, verification))
    write_text(VERIFICATION_MD_PATH, render_verification_markdown(verification))


def verify_canonical_four_agent_57_loop(payloads: dict[str, Any] | None = None, atlas_primary: dict[str, Any] | None = None, run_downstream: bool = True) -> dict[str, Any]:
    from .canonical_four_agent_57_loop import verify_canonical_four_agent_57_loop as verify_live

    return verify_live()


def write_canonical_four_agent_57_loop(source_command: str = "four_agent_57_loop_program_impl") -> dict[str, Any]:
    from .canonical_four_agent_57_loop import write_canonical_four_agent_57_loop as write_live

    # Preserve the legacy import path while letting the live canonical runtime own emitted truth.
    return write_live(source_command)
