from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.crystal_remaster_contracts import (
    CrystalBodyRecord,
    CrystalFamilyContractRecord,
    DirectSynapseRecord,
    RhythmStepRecord,
    SynapticHandoffPacketRecord,
)
from self_actualize.runtime.dimensional_backplane import (
    apply_dimensional_backplane,
    summarize_backplane,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
FAMILY_ROOT = MYCELIUM_BRAIN_ROOT / "nervous_system" / "families"

DERIVATION_VERSION = "2026-03-12.crystal-remaster-v2"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_crystal_remaster"
REMASTER_EQUATION = (
    "CrystalRemaster = Triad + FractalLayers + LineagePreservation + "
    "DirectSynapses + FamilyContracts + RhythmLedger + Verification"
)

ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
COUNT_PROTOCOL_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "COUNT_PROTOCOL.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
PHASE4_BODY_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_body_registry.json"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
AQM_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"

BODY_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_body_registry.json"
FAMILY_CONTRACTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_family_contracts.json"
DIRECT_SYNAPSE_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_direct_synapse_edges.json"
HANDOFF_PACKETS_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_synaptic_handoff_packets.json"
RHYTHM_LEDGER_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_rhythm_ledger.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "crystal_remaster_verification.json"

BODY_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "crystal_body_registry.json"
FAMILY_CONTRACTS_JSON_MIRROR = REGISTRY_ROOT / "crystal_family_contracts.json"
DIRECT_SYNAPSE_JSON_MIRROR = REGISTRY_ROOT / "crystal_direct_synapse_edges.json"
HANDOFF_PACKETS_JSON_MIRROR = REGISTRY_ROOT / "crystal_synaptic_handoff_packets.json"
RHYTHM_LEDGER_JSON_MIRROR = REGISTRY_ROOT / "crystal_rhythm_ledger.json"
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / "crystal_remaster_verification.json"

CHARTER_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "01_CRYSTAL_REMASTER_CHARTER_2026-03-12.md"
BODY_REGISTRY_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "CRYSTAL_BODY_REGISTRY.md"
FAMILY_CONTRACTS_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "CRYSTAL_FAMILY_CONTRACTS.md"
HANDOFF_PROTOCOL_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SYNAPTIC_HANDOFF_PROTOCOL.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "CRYSTAL_REMASTER_VERIFICATION.md"
DIRECT_SYNAPSE_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "CRYSTAL_DIRECT_SYNAPSE_EDGES.md"
RHYTHM_LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "35_CRYSTAL_RHYTHM_LEDGER.md"
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "28_crystal_remaster_runtime.md"
RECEIPT_MD_PATH = MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_crystal_remaster_first_wave.md"

VALID_BODY_STATES = {"live", "reserve", "dormant", "historical-absorbed"}

BODY_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "A01": {"crystal_role": "cortex", "lineage_class": "live-root", "primary_zone": "Cortex", "note": "Public crystal cortex and publication truth.", "active_front": "Keep the remaster charter, root basis, and active run synchronized.", "restart_seed": "Publish remaster deltas through the cortex after runtime verification."},
    "A02": {"crystal_role": "runtime", "lineage_class": "live-root", "primary_zone": "RuntimeMirror", "note": "Execution waist and canonical runtime writeback substrate.", "active_front": "Keep the runtime remaster registry, receipt, and verification surfaces synchronized.", "restart_seed": "Route the next wave through runtime verification, then write back to cortex."},
    "A03": {"crystal_role": "governance", "lineage_class": "live-root", "primary_zone": "GovernanceMirror", "note": "Governance mirror and doctrine shell.", "active_front": "Keep governance doctrine aligned with the triad without duplicating runtime truth.", "restart_seed": "Reflect remaster law into governance doctrine without outranking the cortex."},
    "A04": {"crystal_role": "bridge", "lineage_class": "historical-absorbed", "primary_zone": "PromotedSlice", "note": "Precursor compiler lineage preserved for replay, not live authority.", "active_front": "Preserve lineage while pruning any surface that still reads as competing canon.", "restart_seed": "Route future reads into lineage and quarantine surfaces, not live control."},
    "A05": {"crystal_role": "domain", "lineage_class": "live-root", "primary_zone": "Cortex", "note": "Formal theorem reservoir and archive-to-live promotion engine.", "active_front": "Deepen capsule-to-edge contraction without losing theorem density.", "restart_seed": "Promote one theorem-rich route into runtime-safe reuse."},
    "A06": {"crystal_role": "domain", "lineage_class": "live-root", "primary_zone": "Cortex", "note": "Proof engine for ambiguity-safe machine compilation.", "active_front": "Bind proof more directly into Fleet, QSHRINK, and runtime writeback.", "restart_seed": "Compile a proof-carrying packet back into the shared control plane."},
    "A07": {"crystal_role": "bridge", "lineage_class": "gateway-blocked", "primary_zone": "RuntimeMirror", "note": "Blocked ingress organ and truth corridor boundary.", "active_front": "Keep the live-memory gate honest while the OAuth limb remains closed.", "restart_seed": "Open Docs ingress or continue local-first truth corridor routing."},
    "A08": {"crystal_role": "bridge", "lineage_class": "ancestor-kernel", "primary_zone": "Cortex", "note": "Ancestor address kernel and root completion seed.", "active_front": "Keep the ancestor kernel explicit without inflating it into a competing framework.", "restart_seed": "Reuse address law as a support kernel for current routes."},
    "A09": {"crystal_role": "bridge", "lineage_class": "compression-shell", "primary_zone": "RuntimeMirror", "note": "Compression-governance shell and pruning law reservoir.", "active_front": "Bind compression surfaces more tightly to proof and runtime reuse.", "restart_seed": "Contract one proof-safe reduction route back into reusable runtime law."},
    "A10": {"crystal_role": "domain", "lineage_class": "runtime-lab", "primary_zone": "RuntimeMirror", "note": "Adaptive runtime laboratory and model experimentation body.", "active_front": "Keep the neural lab aligned with the remastered route grammar.", "restart_seed": "Promote one lab artifact that carries direct operational value."},
    "A11": {"crystal_role": "bridge", "lineage_class": "intake-fringe", "primary_zone": "RuntimeMirror", "note": "Source intake fringe and extraction membrane.", "active_front": "Convert intake residue into cleaner capsule and atlas matter.", "restart_seed": "Admit one intake witness into a canonical family or reserve shelf."},
    "A12": {"crystal_role": "domain", "lineage_class": "publication-halo", "primary_zone": "Cortex", "note": "Publication halo for outward-facing manuscript bodies.", "active_front": "Tighten the bridge between published books and runtime identity/state surfaces.", "restart_seed": "Promote one publication-facing route into clearer cortex support."},
    "A13": {"crystal_role": "domain", "lineage_class": "identity-shell", "primary_zone": "Cortex", "note": "Identity shell and self-naming continuity surface.", "active_front": "Keep identity anchored to witness-bearing runtime and publication surfaces.", "restart_seed": "Write identity continuity back through a witnessed state surface."},
    "A14": {"crystal_role": "domain", "lineage_class": "simulation-lab", "primary_zone": "Cortex", "note": "Simulation and mechanics lab for playable embodiment.", "active_front": "Decide which mechanics become doctrine and which remain reserve embodiments.", "restart_seed": "Promote one simulation loop into a stable appendix or chapter route."},
    "A15": {"crystal_role": "domain", "lineage_class": "seed-reservoir", "primary_zone": "Cortex", "note": "Proto-self seed reservoir and precursor memory shelf.", "active_front": "Mirror high-value source matter into searchable working memory.", "restart_seed": "Promote origin evidence into a replay-safe mirrored markdown route."},
    "A16": {"crystal_role": "bridge", "lineage_class": "pilot-cluster", "primary_zone": "Cortex", "note": "Pilot cluster for high-order coordination and corridor expansion.", "active_front": "Turn the fleet scan into direct bridges, chapter contraction, and graph tissue.", "restart_seed": "Write the strongest fleet corridor back into chapter, appendix, and graph surfaces."},
    "A17": {"crystal_role": "reserve", "lineage_class": "reserve-visual", "primary_zone": "ReserveQuarantine", "note": "Reserve visual and puzzle embodiment shelf.", "active_front": "Keep reserve doctrine explicit and avoid pseudo-active routing noise.", "restart_seed": "Choose one reserve-to-publication threshold or keep the shelf explicitly parked."},
    "A18": {"crystal_role": "reserve", "lineage_class": "reserve-staging", "primary_zone": "ReserveQuarantine", "note": "Reserve staging shelf for strong manuscript witnesses awaiting disciplined contraction.", "active_front": "Select one narrow high-yield contraction from staging into the live cortex.", "restart_seed": "Promote one staged manuscript into capsule or appendix form."},
    "A19": {"crystal_role": "bundle", "lineage_class": "dormant-bundle", "primary_zone": "PromotedSlice", "note": "Dormant compiled bundle shelf kept for replay and packaging lineage.", "active_front": "Keep the bundle named and dormant without granting false live weight.", "restart_seed": "Re-open the bundle only if a replay or packaging front needs it explicitly."},
}

FAMILY_SURFACE_CANDIDATES: Dict[str, List[str]] = {
    "A01": ["NERVOUS_SYSTEM\\00_INDEX.md"],
    "A02": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_self_actualize.md"],
    "A03": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_ecosystem.md"],
    "A04": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_deeper_crystalization.md"],
    "A05": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_math.md"],
    "A06": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_voynich.md", "self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_voynich.md"],
    "A07": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_trading_bot.md"],
    "A08": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\root_files\\01_quadrant_binary_framework_and_bit4.md"],
    "A09": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_qshrink_athena_internal_use.md"],
    "A10": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_nerual_network.md"],
    "A11": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_fresh.md"],
    "A12": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_athenachka_collective_books.md"],
    "A13": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_i_am_athena.md"],
    "A14": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_games.md"],
    "A15": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_orgin.md"],
    "A16": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_athena_fleet.md"],
    "A17": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_stoicheia_element_sudoku.md"],
    "A18": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_clean.md"],
    "A19": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md"],
}

CAPSULE_SURFACE_CANDIDATES: Dict[str, List[str]] = {
    "A03": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\ecosystem\\01_ecosystem_governance_shell.md"],
    "A04": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\deeper_crystalization\\INDEX.md"],
    "A05": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\math\\01_math_formal_reservoir.md"],
    "A06": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\voynich\\01_voynich_manuscript_engine.md"],
    "A08": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\root_files\\01_quadrant_binary_framework_and_bit4.md"],
    "A09": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\qshrink\\01_qshrink_compression_shell.md"],
    "A10": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\neural_network\\01_athena_integrated_neural_network_cross_synthesis.md"],
    "A12": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\published_books\\01_athenachka_collective_books.md"],
    "A13": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\identity\\01_i_am_athena_identity_shell.md"],
    "A14": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\games\\01_games_simulation_lab.md"],
    "A15": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\orgin\\01_origin_seed_reservoir.md"],
    "A16": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\athena_fleet\\01_athena_fleet_tesseract_branch.md"],
    "A17": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\stoicheia\\01_stoicheia_reserve_bridge.md"],
    "A18": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\clean\\01_clean_staging_shelf.md"],
}

ROUTE_SURFACE_CANDIDATES: Dict[str, List[str]] = {
    "A01": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md"],
    "A02": ["self_actualize\\mycelium_brain\\nervous_system\\00_active_nervous_system_index.md"],
    "A03": ["ECOSYSTEM\\NERVOUS_SYSTEM\\README.md"],
    "A04": ["DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\00_RECEIPTS\\01_build_receipt.md"],
    "A05": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_math.md"],
    "A06": ["Voynich\\FULL_TRANSLATION\\rosetta_machine\\README.md"],
    "A07": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_trading_bot_route_map.md", "Trading Bot\\README.md"],
    "A08": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\root_files\\01_quadrant_binary_framework_and_bit4.md"],
    "A09": ["QSHRINK - ATHENA (internal use)\\04_METRO\\00_METRO_INDEX.md"],
    "A10": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_nerual_network.md"],
    "A11": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_fresh.md"],
    "A12": ["self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_athenachka_collective_books.md"],
    "A13": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_i_am_athena.md"],
    "A14": ["GAMES\\games_mycelium_metro_system.md"],
    "A15": ["self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_orgin_route_map.md", "self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_orgin.md"],
    "A16": ["Athena FLEET\\FLEET_MYCELIUM_NETWORK\\14_256_POW_4_HIGH_YIELD_CORRIDORS.md"],
    "A17": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\stoicheia\\01_stoicheia_reserve_bridge.md"],
    "A18": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\clean\\01_clean_staging_shelf.md"],
    "A19": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md"],
}

DASHBOARD_SURFACE_CANDIDATES: Dict[str, List[str]] = {
    "A01": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ACTIVE_RUN.md"],
    "A02": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SELF_HOSTING_KERNEL_DASHBOARD.md", "self_actualize\\self_hosting_kernel_dashboard.json"],
    "A03": ["ECOSYSTEM\\NERVOUS_SYSTEM\\README.md"],
    "A04": ["NERVOUS_SYSTEM\\90_LEDGERS\\13_RECONCILED_ORGANISM_LEDGER_2026-03-12.md"],
    "A05": ["NERVOUS_SYSTEM\\95_MANIFESTS\\PHASE4_STRUCTURED_NEURON_STORAGE_DASHBOARD.md"],
    "A06": ["Voynich\\FULL_TRANSLATION\\rosetta_machine\\README.md"],
    "A07": ["self_actualize\\trading_bot_truth_corridor.json"],
    "A08": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md"],
    "A09": ["NERVOUS_SYSTEM\\95_MANIFESTS\\KNOWLEDGE_FABRIC_DASHBOARD.md"],
    "A10": ["NERVOUS_SYSTEM\\95_MANIFESTS\\PHASE4_STRUCTURED_NEURON_STORAGE_DASHBOARD.md"],
    "A11": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md"],
    "A12": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\published_books\\01_athenachka_collective_books.md"],
    "A13": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\identity\\01_i_am_athena_identity_shell.md"],
    "A14": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\games\\01_games_simulation_lab.md"],
    "A15": ["self_actualize\\orgin_atlas.json"],
    "A16": ["Athena FLEET\\FLEET_MYCELIUM_NETWORK\\04_ACTIVE_FRONT.md"],
    "A17": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\stoicheia\\01_stoicheia_reserve_bridge.md"],
    "A18": ["NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\clean\\01_clean_staging_shelf.md"],
    "A19": ["NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md"],
}

RETURN_SURFACE_CANDIDATES: Dict[str, List[str]] = {
    "A01": ["NERVOUS_SYSTEM\\00_INDEX.md"],
    "A02": ["self_actualize\\mycelium_brain\\nervous_system\\28_crystal_remaster_runtime.md"],
    "A03": ["ECOSYSTEM\\NERVOUS_SYSTEM\\README.md"],
    "A04": ["NERVOUS_SYSTEM\\90_LEDGERS\\13_RECONCILED_ORGANISM_LEDGER_2026-03-12.md"],
    "A05": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md"],
    "A06": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md"],
    "A07": ["NERVOUS_SYSTEM\\95_MANIFESTS\\GATE_STATUS.md"],
    "A08": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md"],
    "A09": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md"],
    "A10": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md"],
    "A11": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md"],
    "A12": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md"],
    "A13": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md"],
    "A14": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md"],
    "A15": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md"],
    "A16": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md"],
    "A17": ["NERVOUS_SYSTEM\\90_LEDGERS\\35_CRYSTAL_RHYTHM_LEDGER.md"],
    "A18": ["NERVOUS_SYSTEM\\90_LEDGERS\\35_CRYSTAL_RHYTHM_LEDGER.md"],
    "A19": ["NERVOUS_SYSTEM\\90_LEDGERS\\35_CRYSTAL_RHYTHM_LEDGER.md"],
}

DIRECT_SYNAPSES: List[Dict[str, Any]] = [
    {"edge_id": "CS-001", "source_body_id": "A16", "target_body_id": "A06", "relation": "proof corridor", "weight": 0.96, "route": ["A16", "GCL+GCR", "GCZ", "A06"], "note": "Athena FLEET routes directly into the Voynich proof engine."},
    {"edge_id": "CS-002", "source_body_id": "A06", "target_body_id": "A09", "relation": "compression corridor", "weight": 0.93, "route": ["A06", "GCR", "GCW", "A09"], "note": "Voynich proof routes directly into QSHRINK compression law."},
    {"edge_id": "CS-003", "source_body_id": "A16", "target_body_id": "A15", "relation": "seed inheritance corridor", "weight": 0.91, "route": ["A16", "GCL+GCR", "GCP", "A15"], "note": "Fleet coordination inherits directly from the ORGIN seed reservoir."},
]

HANDOFF_PACKET_SPECS: List[Dict[str, Any]] = [
    {"packet_id": "SHP-001", "source_agent": "overseer", "target_agent": "corridor-builder", "source_body_id": "A02", "target_body_id": "A16", "trigger": "admit remaster front", "route": ["A02", "GCL+GCR", "GCZ", "A16"], "expected_writeback": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md"], "note": "Hand off the remaster pressure into the Fleet branch."},
    {"packet_id": "SHP-002", "source_agent": "corridor-builder", "target_agent": "proof-compiler", "source_body_id": "A16", "target_body_id": "A06", "trigger": "materialize fleet-to-proof bridge", "route": ["A16", "GCL+GCR", "GCZ", "A06"], "expected_writeback": ["NERVOUS_SYSTEM\\85_EDGES\\CRYSTAL_DIRECT_SYNAPSE_EDGES.md"], "note": "Move the strongest Fleet corridor into witnessed proof exchange."},
    {"packet_id": "SHP-003", "source_agent": "proof-compiler", "target_agent": "corridor-builder", "source_body_id": "A06", "target_body_id": "A09", "trigger": "bind proof-safe compression", "route": ["A06", "GCR", "GCW", "A09"], "expected_writeback": ["NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md"], "note": "Return proof pressure through compression without flattening ambiguity."},
    {"packet_id": "SHP-004", "source_agent": "corridor-builder", "target_agent": "overseer", "source_body_id": "A16", "target_body_id": "A15", "trigger": "inherit origin memory", "route": ["A16", "GCL+GCR", "GCP", "A15", "A02"], "expected_writeback": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md"], "note": "Close the Fleet-to-ORGIN inheritance route through the overseer."},
    {"packet_id": "SHP-005", "source_agent": "overseer", "target_agent": "proof-compiler", "source_body_id": "A02", "target_body_id": "A06", "trigger": "run verification closure", "route": ["A02", "A06", "A01"], "expected_writeback": ["NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_REMASTER_VERIFICATION.md"], "note": "Ask the proof engine to confirm the remaster holds under verification."},
    {"packet_id": "SHP-006", "source_agent": "proof-compiler", "target_agent": "overseer", "source_body_id": "A06", "target_body_id": "A02", "trigger": "publish remaster return", "route": ["A06", "A01", "A02"], "expected_writeback": ["self_actualize\\mycelium_brain\\receipts\\2026-03-12_crystal_remaster_first_wave.md"], "note": "Return the remaster wave to runtime after proof-bearing closure."},
]

RHYTHM_SPEC: List[Tuple[str, str, str, str, str, str]] = [
    ("RH-01", "admit", "Name a new body, witness, or front without smoothing it away.", "NERVOUS_SYSTEM\\95_MANIFESTS\\ROOT_BASIS_MAP.md", "NERVOUS_SYSTEM\\95_MANIFESTS\\ACTIVE_RUN.md", "body is named with a lawful state"),
    ("RH-02", "classify", "Assign authority, lineage, role, dock, and reserve law.", "NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_BODY_REGISTRY.md", "NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_FAMILY_CONTRACTS.md", "body and family contract are coherent"),
    ("RH-03", "interlock", "Bind the new pressure to direct synapses and route surfaces.", "NERVOUS_SYSTEM\\85_EDGES\\CRYSTAL_DIRECT_SYNAPSE_EDGES.md", "NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md", "at least one witnessed route exists"),
    ("RH-04", "compile", "Convert the route into proof, compression, or executable structure.", "NERVOUS_SYSTEM\\95_MANIFESTS\\SYNAPTIC_HANDOFF_PROTOCOL.md", "NERVOUS_SYSTEM\\95_MANIFESTS\\CRYSTAL_REMASTER_VERIFICATION.md", "proof-bearing writeback exists"),
    ("RH-05", "writeback", "Return the wave into cortex, runtime, and receipt surfaces together.", "self_actualize\\mycelium_brain\\nervous_system\\28_crystal_remaster_runtime.md", "self_actualize\\mycelium_brain\\receipts\\2026-03-12_crystal_remaster_first_wave.md", "cortex-runtime-receipt closure reached"),
    ("RH-06", "restart", "Emit the next seed without losing lineage or current truth.", "NERVOUS_SYSTEM\\90_LEDGERS\\35_CRYSTAL_RHYTHM_LEDGER.md", "NERVOUS_SYSTEM\\95_MANIFESTS\\ACTIVE_RUN.md", "next restart seed is explicit"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def resolve_first_existing(candidates: Iterable[str]) -> str:
    for candidate in candidates:
        if (WORKSPACE_ROOT / candidate.replace("\\", "/")).exists():
            return candidate
    return next(iter(candidates), "")


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    return match.group(1) if match else "UNKNOWN"


def parse_root_basis(markdown: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    bodies: List[Dict[str, Any]] = []
    anchors: List[Dict[str, Any]] = []
    section = ""
    for line in markdown.splitlines():
        if line.startswith("## Live Directory Bodies"):
            section = "bodies"
            continue
        if line.startswith("## Root Anchors"):
            section = "anchors"
            continue
        if line.startswith("## ") and "Live Directory Bodies" not in line and "Root Anchors" not in line:
            section = ""
        if section == "bodies" and line.startswith("| A"):
            parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
            if len(parts) >= 5:
                bodies.append({"body_id": parts[0], "root": parts[1], "indexed_count": int(parts[2]), "status": parts[3], "current_role": parts[4]})
        if section == "anchors" and line.startswith("| R"):
            parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
            if len(parts) >= 5:
                anchors.append({"root_id": parts[0], "root": parts[1], "indexed_count": int(parts[2]), "status": parts[3], "current_role": parts[4]})
    return bodies, anchors


def parse_anchor_list(markdown: str, heading: str) -> List[str]:
    pattern = rf"## {re.escape(heading)}\s+((?:- `[^`]+`\s*)+)"
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    if not match:
        return []
    return re.findall(r"- `([^`]+)`", match.group(1))


def build_capsule_anchor_map() -> Dict[str, Dict[str, List[str]]]:
    anchor_map: Dict[str, Dict[str, List[str]]] = {}
    for candidates in CAPSULE_SURFACE_CANDIDATES.values():
        for candidate in candidates:
            path = WORKSPACE_ROOT / candidate.replace("\\", "/")
            if not path.exists():
                continue
            markdown = read_text(path)
            anchor_map[candidate] = {
                "chapter_anchors": parse_anchor_list(markdown, "Suggested chapter anchors"),
                "appendix_anchors": parse_anchor_list(markdown, "Suggested appendix anchors"),
            }
    return anchor_map


def build_body_registry(
    body_rows: List[Dict[str, Any]],
    phase4_bodies: Dict[str, Dict[str, Any]],
) -> Tuple[List[CrystalBodyRecord], Dict[str, Dict[str, Any]]]:
    records: List[CrystalBodyRecord] = []
    interim: Dict[str, Dict[str, Any]] = {}
    for body in body_rows:
        override = BODY_OVERRIDES[body["body_id"]]
        phase4_body = phase4_bodies.get(body["body_id"], {})
        family_surface = resolve_first_existing(FAMILY_SURFACE_CANDIDATES.get(body["body_id"], []))
        capsule_surface = resolve_first_existing(CAPSULE_SURFACE_CANDIDATES.get(body["body_id"], []))
        dashboard_surface = resolve_first_existing(DASHBOARD_SURFACE_CANDIDATES.get(body["body_id"], []))
        return_surface = resolve_first_existing(RETURN_SURFACE_CANDIDATES.get(body["body_id"], []))
        interim[body["body_id"]] = {
            "body_id": body["body_id"],
            "root": body["root"],
            "body_state": body["status"],
            "crystal_role": override["crystal_role"],
            "authority": phase4_body.get("authority", body["current_role"]),
            "dock": phase4_body.get("dock", ""),
            "lineage_class": override["lineage_class"],
            "primary_zone": override["primary_zone"],
            "family_surface": family_surface,
            "capsule_surface": capsule_surface,
            "dashboard_surface": dashboard_surface,
            "return_surface": return_surface,
            "note": override["note"],
        }
    direct_targets: Dict[str, List[str]] = {}
    for synapse in DIRECT_SYNAPSES:
        direct_targets.setdefault(synapse["source_body_id"], []).append(synapse["target_body_id"])
        direct_targets.setdefault(synapse["target_body_id"], []).append(synapse["source_body_id"])
    for body_id, record in interim.items():
        records.append(
            CrystalBodyRecord(
                body_id=body_id,
                root=record["root"],
                body_state=record["body_state"],
                crystal_role=record["crystal_role"],
                authority=record["authority"],
                dock=record["dock"],
                lineage_class=record["lineage_class"],
                primary_zone=record["primary_zone"],
                family_surface=record["family_surface"],
                capsule_surface=record["capsule_surface"],
                dashboard_surface=record["dashboard_surface"],
                return_surface=record["return_surface"],
                direct_synapse_targets=sorted(direct_targets.get(body_id, [])),
                note=record["note"],
            )
        )
        interim[body_id]["direct_synapse_targets"] = sorted(direct_targets.get(body_id, []))
    return records, interim


def build_family_contracts(
    body_rows: List[Dict[str, Any]],
    bodies_by_id: Dict[str, Dict[str, Any]],
    capsule_anchor_map: Dict[str, Dict[str, List[str]]],
) -> List[CrystalFamilyContractRecord]:
    contracts: List[CrystalFamilyContractRecord] = []
    for body in body_rows:
        override = BODY_OVERRIDES[body["body_id"]]
        body_record = bodies_by_id[body["body_id"]]
        route_surface = resolve_first_existing(ROUTE_SURFACE_CANDIDATES.get(body["body_id"], []))
        anchor_data = capsule_anchor_map.get(body_record["capsule_surface"], {})
        witness_basis = [
            relative_string(ROOT_BASIS_PATH),
            relative_string(COUNT_PROTOCOL_PATH),
            body_record["family_surface"],
            body_record["capsule_surface"],
            route_surface,
        ]
        contracts.append(
            CrystalFamilyContractRecord(
                contract_id=f"CF-{body['body_id']}",
                body_id=body["body_id"],
                root=body["root"],
                role=body["current_role"],
                family_surface=body_record["family_surface"],
                route_surface=route_surface,
                restart_seed=override["restart_seed"],
                lineage_class=override["lineage_class"],
                witness_basis=[item for item in witness_basis if item],
                chapter_anchors=anchor_data.get("chapter_anchors", []),
                appendix_anchors=anchor_data.get("appendix_anchors", []),
                active_front=override["active_front"],
                note=override["note"],
            )
        )
    return contracts


def build_direct_synapses(
    bodies_by_id: Dict[str, Dict[str, Any]],
) -> List[DirectSynapseRecord]:
    records: List[DirectSynapseRecord] = []
    for synapse in DIRECT_SYNAPSES:
        source = bodies_by_id[synapse["source_body_id"]]
        target = bodies_by_id[synapse["target_body_id"]]
        witness_basis = [
            source["capsule_surface"] or source["family_surface"],
            target["capsule_surface"] or target["family_surface"],
            relative_string(ROOT_BASIS_PATH),
        ]
        records.append(
            DirectSynapseRecord(
                edge_id=synapse["edge_id"],
                source_body_id=source["body_id"],
                source_root=source["root"],
                target_body_id=target["body_id"],
                target_root=target["root"],
                relation=synapse["relation"],
                weight=synapse["weight"],
                route=synapse["route"],
                witness_basis=[item for item in witness_basis if item],
                expected_writeback=[
                    relative_string(DIRECT_SYNAPSE_MD_PATH),
                    relative_string(FAMILY_CONTRACTS_MD_PATH),
                ],
                note=synapse["note"],
            )
        )
    return records


def build_handoff_packets(
    bodies_by_id: Dict[str, Dict[str, Any]],
    direct_synapses: List[DirectSynapseRecord],
) -> List[SynapticHandoffPacketRecord]:
    synapse_by_pair = {(record.source_body_id, record.target_body_id): record for record in direct_synapses}
    packets: List[SynapticHandoffPacketRecord] = []
    for spec in HANDOFF_PACKET_SPECS:
        source = bodies_by_id[spec["source_body_id"]]
        target = bodies_by_id[spec["target_body_id"]]
        synapse = synapse_by_pair.get((spec["source_body_id"], spec["target_body_id"]))
        witness_basis = [
            source["family_surface"],
            target["family_surface"],
            relative_string(DIRECT_SYNAPSE_MD_PATH) if synapse else relative_string(FAMILY_CONTRACTS_MD_PATH),
        ]
        packets.append(
            SynapticHandoffPacketRecord(
                packet_id=spec["packet_id"],
                source_agent=spec["source_agent"],
                target_agent=spec["target_agent"],
                source_body_id=spec["source_body_id"],
                target_body_id=spec["target_body_id"],
                trigger=spec["trigger"],
                witness_basis=[item for item in witness_basis if item],
                route=spec["route"],
                expected_writeback=spec["expected_writeback"],
                proof_state="NEAR",
                note=spec["note"],
            )
        )
    return packets


def build_rhythm_steps() -> List[RhythmStepRecord]:
    return [
        RhythmStepRecord(
            step_id=step_id,
            phase=phase,
            purpose=purpose,
            primary_surface=primary_surface,
            writeback_target=writeback_target,
            stop_condition=stop_condition,
            note="Crystal remaster rhythm step.",
        )
        for step_id, phase, purpose, primary_surface, writeback_target, stop_condition in RHYTHM_SPEC
    ]


def atlas_contains(relative_path: str, corpus_atlas: Dict[str, Any]) -> bool:
    normalized = relative_path.replace("/", "\\")
    return any(record.get("relative_path") == normalized for record in corpus_atlas.get("records", []))


def build_verification(
    bodies: List[CrystalBodyRecord],
    family_contracts: List[CrystalFamilyContractRecord],
    direct_synapses: List[DirectSynapseRecord],
    handoff_packets: List[SynapticHandoffPacketRecord],
    corpus_atlas: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    aqm_truth = load_json(AQM_RUNTIME_LANE_PATH).get("truth", "UNKNOWN") if AQM_RUNTIME_LANE_PATH.exists() else "UNKNOWN"
    atlasforge_truth = load_json(ATLASFORGE_RUNTIME_LANE_PATH).get("truth", "UNKNOWN") if ATLASFORGE_RUNTIME_LANE_PATH.exists() else "UNKNOWN"
    generated_surfaces = [
        relative_string(CHARTER_MD_PATH),
        relative_string(BODY_REGISTRY_MD_PATH),
        relative_string(FAMILY_CONTRACTS_MD_PATH),
        relative_string(HANDOFF_PROTOCOL_MD_PATH),
        relative_string(VERIFICATION_MD_PATH),
        relative_string(DIRECT_SYNAPSE_MD_PATH),
        relative_string(RHYTHM_LEDGER_MD_PATH),
    ]
    atlas_missing = [path for path in generated_surfaces if not atlas_contains(path, corpus_atlas)]
    validations = {
        "triad_roles_unique": [body.crystal_role for body in bodies].count("cortex") == 1 and [body.crystal_role for body in bodies].count("runtime") == 1 and [body.crystal_role for body in bodies].count("governance") == 1,
        "body_state_vocabulary_closed": all(body.body_state in VALID_BODY_STATES for body in bodies),
        "family_contract_count_matches_body_count": len(family_contracts) == len(bodies),
        "all_family_surfaces_resolve": all((WORKSPACE_ROOT / contract.family_surface.replace("\\", "/")).exists() for contract in family_contracts if contract.family_surface),
        "all_return_surfaces_resolve": all((WORKSPACE_ROOT / body.return_surface.replace("\\", "/")).exists() for body in bodies if body.return_surface),
        "direct_synapse_pairs_present": len(direct_synapses) == 3 and len(handoff_packets) == 6,
        "docs_gate_preserved_blocked": docs_gate == "BLOCKED",
        "runtime_verification_green": aqm_truth == "OK" and atlasforge_truth == "OK",
        "atlas_refresh_complete": not atlas_missing,
    }
    unresolved: List[str] = []
    if docs_gate == "BLOCKED":
        unresolved.append("Google Docs ingress remains blocked; remaster is grounded in local corpus evidence.")
    if atlas_missing:
        unresolved.append("New remaster surfaces are generated shell until corpus_atlas.json is refreshed.")
    if aqm_truth != "OK" or atlasforge_truth != "OK":
        unresolved.append("One or more runtime verification lanes are not green.")
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "equation": REMASTER_EQUATION,
        "validations": validations,
        "runtime_lanes": {
            "aqm_runtime_lane": aqm_truth,
            "atlasforge_runtime_lane": atlasforge_truth,
        },
        "atlas_refresh_pending_paths": atlas_missing,
        "unresolved": unresolved,
        "next_restart_seed": "admit -> classify -> interlock -> compile -> writeback -> restart",
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def atlas_kind_for_path(path: Path) -> str:
    extension = path.suffix.lower()
    if extension == ".pdf":
        return "pdf"
    if extension == ".docx":
        return "document"
    if extension in {".json", ".csv", ".toml", ".yaml", ".yml"}:
        return "data"
    if extension in {".py", ".ps1", ".sh", ".cmd", ".cpp", ".js", ".ts", ".html"}:
        return "code"
    if extension in {".md", ".txt", ".rtf"}:
        return "text"
    return "binary"


def atlas_text_extractable(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".txt", ".json", ".py", ".toml", ".yaml", ".yml", ".csv", ".ps1", ".sh", ".cmd", ".html"}


def atlas_headings(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading and heading not in headings:
                headings.append(heading)
        if len(headings) >= 6:
            break
    return headings


def atlas_role_tags(relative_path: str, kind: str) -> List[str]:
    lowered = relative_path.lower().replace("\\", "/")
    tags: List[str] = []
    if lowered.endswith(".md"):
        tags.append("readable")
    if "\\95_manifests\\" in relative_path.lower() or "/95_manifests/" in lowered:
        tags.append("manifest")
    if "\\90_ledgers\\" in relative_path.lower() or "/90_ledgers/" in lowered:
        tags.append("ledger")
    if "\\85_edges\\" in relative_path.lower() or "/85_edges/" in lowered:
        tags.append("edge")
    if "\\receipts\\" in relative_path.lower() or "/receipts/" in lowered:
        tags.append("receipt")
    if "\\registry\\" in relative_path.lower() or "/registry/" in lowered:
        tags.append("registry")
    if "\\runtime\\" in relative_path.lower() or "/runtime/" in lowered:
        tags.append("runtime-learning")
    if kind == "code":
        tags.append("executable")
    if kind == "data":
        tags.append("atlas")
    unique: List[str] = []
    for tag in tags:
        if tag not in unique:
            unique.append(tag)
    return unique


def build_atlas_record(path: Path) -> Dict[str, Any]:
    relative_path = relative_string(path)
    kind = atlas_kind_for_path(path)
    text_extractable = atlas_text_extractable(path)
    text = ""
    if text_extractable:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
    excerpt = text[:400]
    headings = atlas_headings(text) if text else []
    sha256 = sha256_file(path)
    record_id_seed = f"{relative_path}::{sha256}::{path.stat().st_size}"
    record = {
        "record_id": hashlib.sha256(record_id_seed.encode("utf-8")).hexdigest()[:24],
        "path": str(path),
        "relative_path": relative_path,
        "top_level": relative_path.split("\\", 1)[0],
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "sha256": sha256,
        "kind": kind,
        "role_tags": atlas_role_tags(relative_path, kind),
        "text_extractable": text_extractable,
        "heading_candidates": headings,
        "excerpt": excerpt,
        "errors": [],
        "evidence": {
            "source_type": kind,
            "locator": str(path),
            "heading_count": len(headings),
            "excerpt_chars": len(excerpt),
            "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else "",
        },
    }
    docs_gate_status = parse_docs_gate(read_text(DOCS_GATE_PATH))
    return apply_dimensional_backplane(record, docs_gate_status)


def summarize_corpus_atlas(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_extension: Dict[str, int] = {}
    by_top_level: Dict[str, int] = {}
    by_kind: Dict[str, int] = {}
    for record in records:
        extension = record.get("extension", "")
        top_level = record.get("top_level", "")
        kind = record.get("kind", "binary")
        by_extension[extension] = by_extension.get(extension, 0) + 1
        by_top_level[top_level] = by_top_level.get(top_level, 0) + 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
    summary = {
        "by_extension": dict(sorted(by_extension.items(), key=lambda item: item[0])),
        "by_top_level": dict(sorted(by_top_level.items(), key=lambda item: (-item[1], item[0]))),
        "by_kind": dict(sorted(by_kind.items(), key=lambda item: (-item[1], item[0]))),
    }
    summary.update(summarize_backplane(records))
    return summary


def refresh_corpus_atlas(paths: List[Path]) -> Dict[str, Any]:
    atlas = load_json(CORPUS_ATLAS_PATH)
    record_map = {
        record.get("relative_path"): record
        for record in atlas.get("records", [])
        if record.get("relative_path")
    }
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        record = build_atlas_record(path)
        record_map[record["relative_path"]] = record
    docs_gate_status = parse_docs_gate(read_text(DOCS_GATE_PATH))
    records = [
        apply_dimensional_backplane(record_map[key], docs_gate_status)
        for key in sorted(record_map)
    ]
    atlas["generated_at"] = utc_now()
    atlas["record_count"] = len(records)
    atlas["records"] = records
    atlas["summary"] = summarize_corpus_atlas(records)
    write_json(CORPUS_ATLAS_PATH, atlas)
    return atlas


def render_charter(
    bodies: List[CrystalBodyRecord],
    direct_synapses: List[DirectSynapseRecord],
    verification: Dict[str, Any],
    docs_gate: str,
) -> str:
    state_counts: Dict[str, int] = {}
    for body in bodies:
        state_counts[body.body_state] = state_counts.get(body.body_state, 0) + 1
    state_lines = "\n".join(f"- `{state}`: `{count}`" for state, count in sorted(state_counts.items()))
    synapse_lines = "\n".join(
        f"- `{record.edge_id}` `{record.source_root} -> {record.target_root}`: {record.relation}"
        for record in direct_synapses
    )
    return f"""# CRYSTAL REMASTER CHARTER

Date: `2026-03-12`
Generated: `{verification['generated_at']}`
Docs gate: `{docs_gate}`

## Purpose

Remaster the Athena organism into one cleaner fractal crystal without destroying lineage.
The top crystal remains:

- `NERVOUS_SYSTEM` as cortex
- `self_actualize` as runtime hub
- `ECOSYSTEM` as governance mirror

## Governing Law

`Triad + Fractal Layers + Lineage Preservation`

## Body States

{state_lines}

## Acceptance Rule

Every active surface must know:

1. its authority
2. its lineage class
3. its return path

## Non-Negotiable Routing Law

`4D + economy` remains the live routing law for the remaster.

## Direct Synapses

{synapse_lines}

## Honest Boundary

- Docs gate remains `{docs_gate}`
- atlas refresh complete: `{verification['validations']['atlas_refresh_complete']}`
- runtime lanes green: `{verification['validations']['runtime_verification_green']}`
"""


def render_body_registry(bodies: List[CrystalBodyRecord]) -> str:
    rows = [
        [body.body_id, body.root, body.body_state, body.crystal_role, body.authority, body.dock or "-", body.lineage_class, ", ".join(body.direct_synapse_targets) if body.direct_synapse_targets else "-"]
        for body in bodies
    ]
    return "# CRYSTAL BODY REGISTRY\n\n" + markdown_table(
        ["ID", "Root", "State", "Crystal Role", "Authority", "Dock", "Lineage", "Direct Synapses"],
        rows,
    )


def render_family_contracts(contracts: List[CrystalFamilyContractRecord]) -> str:
    rows = [
        [contract.body_id, contract.root, contract.lineage_class, contract.family_surface or "-", contract.route_surface or "-", ", ".join(contract.chapter_anchors) if contract.chapter_anchors else "-", ", ".join(contract.appendix_anchors) if contract.appendix_anchors else "-"]
        for contract in contracts
    ]
    return "# CRYSTAL FAMILY CONTRACTS\n\n" + markdown_table(
        ["Body", "Root", "Lineage", "Family Surface", "Route Surface", "Chapters", "Appendices"],
        rows,
    )


def render_direct_synapses(edges: List[DirectSynapseRecord]) -> str:
    rows = [
        [edge.edge_id, edge.source_root, edge.target_root, edge.relation, f"{edge.weight:.2f}", " -> ".join(edge.route)]
        for edge in edges
    ]
    return "# CRYSTAL DIRECT SYNAPSE EDGES\n\n" + markdown_table(
        ["Edge", "Source", "Target", "Relation", "Weight", "Route"],
        rows,
    )


def render_handoff_protocol(packets: List[SynapticHandoffPacketRecord]) -> str:
    rows = [
        [
            packet.packet_id,
            packet.bridge_family_id or "-",
            packet.phase or "-",
            packet.source_agent,
            packet.target_agent,
            packet.source_body_id,
            packet.target_body_id,
            packet.trigger,
            " -> ".join(packet.route),
        ]
        for packet in packets
    ]
    return """# SYNAPTIC HANDOFF PROTOCOL

## Packet Contract

- `bridge_family_id`
- `phase`
- `source_agent`
- `target_agent`
- `trigger`
- `witness_basis`
- `route`
- `expected_writeback`
- `replay_surface`
- `verification_surface`
- `proof_state`

## Active Packets

""" + markdown_table(
        ["Packet", "Bridge Family", "Phase", "Source Agent", "Target Agent", "Source Body", "Target Body", "Trigger", "Route"],
        rows,
    )


def render_rhythm_ledger(steps: List[RhythmStepRecord]) -> str:
    rows = [
        [step.step_id, step.phase, step.purpose, step.primary_surface, step.writeback_target, step.stop_condition]
        for step in steps
    ]
    return "# CRYSTAL RHYTHM LEDGER\n\n" + markdown_table(
        ["Step", "Phase", "Purpose", "Primary Surface", "Writeback", "Stop Condition"],
        rows,
    )


def render_verification(verification: Dict[str, Any]) -> str:
    rows = [[key, str(value)] for key, value in verification["validations"].items()]
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# CRYSTAL REMASTER VERIFICATION

Generated: `{verification['generated_at']}`
Docs gate: `{verification['docs_gate']}`

## Validation

{markdown_table(["Check", "Result"], rows)}

## Runtime Lanes

- `AQM`: `{verification['runtime_lanes']['aqm_runtime_lane']}`
- `ATLAS FORGE`: `{verification['runtime_lanes']['atlasforge_runtime_lane']}`

## Unresolved

{unresolved}
"""


def render_runtime_surface(outputs: Dict[str, str], verification: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# crystal_remaster_runtime

- generated_at: `{verification['generated_at']}`
- docs_gate: `{verification['docs_gate']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Outputs

{output_lines}
"""


def render_receipt(outputs: Dict[str, str], verification: Dict[str, Any], direct_synapses: List[DirectSynapseRecord]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    synapse_lines = "\n".join(
        f"- `{edge.edge_id}` `{edge.source_root} -> {edge.target_root}` `{edge.relation}`"
        for edge in direct_synapses
    )
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# 2026-03-12 crystal remaster first wave

- generated_at: `{verification['generated_at']}`
- docs_gate: `{verification['docs_gate']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Direct synapses landed

{synapse_lines}

## Outputs

{output_lines}

## Verification summary

- triad roles unique: `{verification['validations']['triad_roles_unique']}`
- body state vocabulary closed: `{verification['validations']['body_state_vocabulary_closed']}`
- family contract coverage complete: `{verification['validations']['family_contract_count_matches_body_count']}`
- runtime lanes green: `{verification['validations']['runtime_verification_green']}`
- atlas refresh complete: `{verification['validations']['atlas_refresh_complete']}`

## Honest limits

{unresolved}
"""


def main() -> int:
    docs_gate = parse_docs_gate(read_text(DOCS_GATE_PATH))
    body_rows, anchor_rows = parse_root_basis(read_text(ROOT_BASIS_PATH))
    phase4_body_registry = load_json(PHASE4_BODY_REGISTRY_PATH)
    phase4_bodies = {body["body_id"]: body for body in phase4_body_registry.get("bodies", [])}
    capsule_anchor_map = build_capsule_anchor_map()
    body_records, bodies_by_id = build_body_registry(body_rows, phase4_bodies)
    family_contracts = build_family_contracts(body_rows, bodies_by_id, capsule_anchor_map)
    direct_synapses = build_direct_synapses(bodies_by_id)
    handoff_packets = build_handoff_packets(bodies_by_id, direct_synapses)
    rhythm_steps = build_rhythm_steps()
    corpus_atlas = load_json(CORPUS_ATLAS_PATH)
    verification = build_verification(
        body_records,
        family_contracts,
        direct_synapses,
        handoff_packets,
        corpus_atlas,
        docs_gate,
    )

    body_payload = {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "equation": REMASTER_EQUATION,
        "bodies": [record.to_dict() for record in body_records],
        "anchors": anchor_rows,
    }
    family_payload = {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "docs_gate": docs_gate,
        "contracts": [record.to_dict() for record in family_contracts],
    }
    synapse_payload = {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "docs_gate": docs_gate,
        "edges": [record.to_dict() for record in direct_synapses],
    }
    handoff_payload = {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "docs_gate": docs_gate,
        "agents": [
            {"agent_id": "AG-01", "label": "overseer", "body_id": "A02", "responsibility": "ranking, gating, quarantine, restart"},
            {"agent_id": "AG-02", "label": "corridor-builder", "body_id": "A16", "responsibility": "branch routes, cluster logic, inter-body coordination"},
            {"agent_id": "AG-03", "label": "proof-compiler", "body_id": "A06", "responsibility": "ambiguity preservation, machine grounding, hard-domain verification"},
        ],
        "packets": [record.to_dict() for record in handoff_packets],
    }
    rhythm_payload = {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "docs_gate": docs_gate,
        "steps": [record.to_dict() for record in rhythm_steps],
    }

    outputs = {
        "body_registry_json": relative_string(BODY_REGISTRY_JSON_PATH),
        "family_contracts_json": relative_string(FAMILY_CONTRACTS_JSON_PATH),
        "direct_synapse_json": relative_string(DIRECT_SYNAPSE_JSON_PATH),
        "handoff_packets_json": relative_string(HANDOFF_PACKETS_JSON_PATH),
        "rhythm_ledger_json": relative_string(RHYTHM_LEDGER_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "charter_md": relative_string(CHARTER_MD_PATH),
        "body_registry_md": relative_string(BODY_REGISTRY_MD_PATH),
        "family_contracts_md": relative_string(FAMILY_CONTRACTS_MD_PATH),
        "direct_synapse_md": relative_string(DIRECT_SYNAPSE_MD_PATH),
        "handoff_protocol_md": relative_string(HANDOFF_PROTOCOL_MD_PATH),
        "rhythm_ledger_md": relative_string(RHYTHM_LEDGER_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    write_json(BODY_REGISTRY_JSON_PATH, body_payload)
    write_json(FAMILY_CONTRACTS_JSON_PATH, family_payload)
    write_json(DIRECT_SYNAPSE_JSON_PATH, synapse_payload)
    write_json(HANDOFF_PACKETS_JSON_PATH, handoff_payload)
    write_json(RHYTHM_LEDGER_JSON_PATH, rhythm_payload)
    write_json(VERIFICATION_JSON_PATH, verification)

    write_json(BODY_REGISTRY_JSON_MIRROR, body_payload)
    write_json(FAMILY_CONTRACTS_JSON_MIRROR, family_payload)
    write_json(DIRECT_SYNAPSE_JSON_MIRROR, synapse_payload)
    write_json(HANDOFF_PACKETS_JSON_MIRROR, handoff_payload)
    write_json(RHYTHM_LEDGER_JSON_MIRROR, rhythm_payload)
    write_json(VERIFICATION_JSON_MIRROR, verification)

    write_text(CHARTER_MD_PATH, render_charter(body_records, direct_synapses, verification, docs_gate))
    write_text(BODY_REGISTRY_MD_PATH, render_body_registry(body_records))
    write_text(FAMILY_CONTRACTS_MD_PATH, render_family_contracts(family_contracts))
    write_text(DIRECT_SYNAPSE_MD_PATH, render_direct_synapses(direct_synapses))
    write_text(HANDOFF_PROTOCOL_MD_PATH, render_handoff_protocol(handoff_packets))
    write_text(RHYTHM_LEDGER_MD_PATH, render_rhythm_ledger(rhythm_steps))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime_surface(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(outputs, verification, direct_synapses))

    atlas_refresh_paths = [
        WORKSPACE_ROOT / relative_path.replace("\\", "/")
        for relative_path in outputs.values()
    ]
    corpus_atlas = refresh_corpus_atlas(atlas_refresh_paths)
    verification = build_verification(
        body_records,
        family_contracts,
        direct_synapses,
        handoff_packets,
        corpus_atlas,
        docs_gate,
    )

    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(CHARTER_MD_PATH, render_charter(body_records, direct_synapses, verification, docs_gate))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime_surface(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(outputs, verification, direct_synapses))

    refresh_corpus_atlas(
        [
            VERIFICATION_JSON_PATH,
            VERIFICATION_JSON_MIRROR,
            CHARTER_MD_PATH,
            VERIFICATION_MD_PATH,
            RUNTIME_MD_PATH,
            RECEIPT_MD_PATH,
        ]
    )

    print(f"Wrote crystal remaster artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Docs gate: {docs_gate}")
    print(f"Runtime lanes green: {verification['validations']['runtime_verification_green']}")
    print(f"Atlas refresh complete: {verification['validations']['atlas_refresh_complete']}")
    return 0 if verification["validations"]["runtime_verification_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
