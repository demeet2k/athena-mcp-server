from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from self_actualize.runtime.phase4_pt2_query_engine import (
    field as query_field,
    fire,
    interlock,
    lens,
    locate,
    project,
    promote,
    route,
)
from self_actualize.runtime.hemisphere_dense_65_shell_support import (
    DENSE_65_AUTHORITY_REFS,
    DENSE_65_SHELL_REGISTRY_PATH,
    DENSE_65_SIGMA_PATH,
)
from self_actualize.runtime.hemisphere_lp57omega_support import (
    LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH,
    LP57OMEGA_SEED_INVERSION_STANDARD_PATH,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
DEEP_ROOT = MYCELIUM_BRAIN_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"

DERIVATION_VERSION = "2026-03-12.phase4-pt2-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_phase4_pt2_inter_metro_lens_weight_superstructure"
PT2_EQUATION = "Phase4Pt2 = StructuredStorage + KnowledgeFabric + MetroInterlocks + LensWeightStack + FieldLayer + ProjectionSpaces"

DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
ADDRESSING_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "03_ADDRESSING_AND_ROUTING.md"
HIGHER_DIMENSIONAL_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "05_HIGHER_DIMENSIONAL_MAPPING.md"
DEEPER_SWARM_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "06_DEEPER_EMERGENT_NEURAL_SWARM.md"
GRAND_CENTRAL_OVERVIEW_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md"
AFFECTIVE_FIELD_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md"
PHASE4_STRUCTURED_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "18_PHASE4_STRUCTURED_NEURON_STORAGE.md"
KNOWLEDGE_FABRIC_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "18_PHASE4_KNOWLEDGE_FABRIC.md"
VIRTUAL_SWARM_SPEC_PATH = NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "08_VIRTUAL_SWARM_SPEC_16X16.md"
HD_SCT_PATH = WORKSPACE_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "02_CORPUS_CAPSULES" / "36_higher_d_square_circle_triangle.md"
HYBRID_LENS_PATH = WORKSPACE_ROOT / "Trading Bot" / "MANUSCRIPT_ELEMENTAL_NET_4X4" / "01_SOURCE_EXTRACTS" / "m02_holographic-reality-structure.md"

PHASE4_BODY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_body_registry.json"
PHASE4_NODE_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_node_registry.json"
PHASE4_PAIR_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_pair_registry.json"
PHASE4_WAVE_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_wave_registry.json"
PHASE4_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_structured_neuron_storage_dashboard.json"
KNOWLEDGE_FABRIC_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_dashboard.json"
WHOLE_CRYSTAL_BRIDGE_WITNESSES_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_bridge_witnesses.json"
BRIDGE_DENSIFICATION_FAMILIES_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_direct_bridge_families.json"

JSON_OUTPUTS = {
    "metro_system_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_system_registry.json",
    "metro_station_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_station_registry.json",
    "metro_interlock_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_interlock_registry.json",
    "holo_coordinate_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_holo_coordinate_registry.json",
    "carrier_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_carrier_registry.json",
    "rail_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_rail_registry.json",
    "arc_rotation_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_arc_rotation_registry.json",
    "carrier_transform_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_carrier_transform_registry.json",
    "lens_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_registry.json",
    "lens_hybrid_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_hybrid_registry.json",
    "lens_weight_profile_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_weight_profile_registry.json",
    "lens_state_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_state_registry.json",
    "field_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_field_registry.json",
    "z_point_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_z_point_registry.json",
    "aether_point_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_aether_point_registry.json",
    "projection_space_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_projection_space_registry.json",
    "projection_assignment_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_projection_assignment_registry.json",
    "shortcut_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_shortcut_registry.json",
    "query_registry": SELF_ACTUALIZE_ROOT / "phase4_pt2_query_presets.json",
    "system_crosswalk_edges": SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json",
    "dashboard": SELF_ACTUALIZE_ROOT / "phase4_pt2_dashboard.json",
    "registry_manifest": SELF_ACTUALIZE_ROOT / "phase4_pt2_registry_manifest.json",
}

OVERVIEW_MD_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "19_PHASE4_PT2_INTER_METRO_LENS_WEIGHT_SUPERSTRUCTURE.md"
SCHEMA_PRIMARY_MD_PATH = NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "15_PHASE4_PT2_INTER_METRO_LENS_WEIGHT_SCHEMA.md"
SCHEMA_QUERY_MD_PATH = NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "16_PHASE4_PT2_QUERY_AND_FIELD_SCHEMA.md"
LEDGER_MAIN_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "30_PHASE4_PT2_INTER_METRO_LENS_WEIGHT_LEDGER.md"
LEDGER_INTERLOCK_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "31_PHASE4_PT2_METRO_INTERLOCK_LEDGER.md"
LEDGER_LENS_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "32_PHASE4_PT2_LENS_WEIGHT_PROFILE_LEDGER.md"
LEDGER_FIELD_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "33_PHASE4_PT2_FIELD_AND_AETHER_LEDGER.md"
LEDGER_PROJECTION_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "34_PHASE4_PT2_PROJECTION_SPACE_LEDGER.md"
POINTERS_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_PT2_METRO_SYSTEM_POINTERS.md"
QUERY_PRESETS_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_PT2_QUERY_PRESETS.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_PT2_DASHBOARD.md"
EDGE_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "PHASE4_PT2_SYSTEM_CROSSWALK_EDGES.md"
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "27_phase4_pt2_inter_metro_lens_weight_runtime.md"
RECEIPT_MD_PATH = MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_phase4_pt2_inter_metro_lens_weight_superstructure.md"

APPENDIX_SUPPORT_SET = ["AppA", "AppC", "AppE", "AppF", "AppG", "AppI", "AppM", "AppP", "AppQ"]
QUERY_ORDER = ["body", "system", "coordinate", "lens", "pair", "wave", "field", "interlock", "writeback"]
LENS_ORDER = "SFCR"
BASE_CHANNEL_VECTOR = {"emotion": 0.0, "feeling": 0.0, "knowledge": 0.0, "desire": 0.0, "memory": 0.0, "boundary": 0.0, "repair": 0.0, "imagination": 0.0}
SINGLETON_CHANNELS = {
    "S": {**BASE_CHANNEL_VECTOR, "knowledge": 0.36, "boundary": 0.34, "repair": 0.30},
    "F": {**BASE_CHANNEL_VECTOR, "feeling": 0.35, "desire": 0.31, "imagination": 0.22, "emotion": 0.12},
    "C": {**BASE_CHANNEL_VECTOR, "emotion": 0.30, "feeling": 0.22, "imagination": 0.22, "boundary": 0.12, "knowledge": 0.14},
    "R": {**BASE_CHANNEL_VECTOR, "memory": 0.36, "repair": 0.31, "knowledge": 0.21, "feeling": 0.12},
}
SINGLETON_ROLES = {"S": "address/structure", "F": "resonance/orbit", "C": "field/Aether/ambiguity", "R": "memory/replay/regeneration"}
HYBRID_ROLES = {"SF": "spectral projection", "SC": "address-to-field permeability", "SR": "address-to-replay stabilization", "FC": "resonance-induced field motion", "FR": "harmonic regeneration", "CR": "field-memory renormalization", "SFC": "backbone spectral coherence", "SFR": "lift and defect-control gate", "SCR": "diffusion and coarse-grain corridor gate", "FCR": "heat-trace and global statistics gate", "SFCR": "mature-object certificate and unified Aether witness"}
SINGLETON_CARRIERS = {"S": ["Square", "Triangle", "Nervous"], "F": ["Flower", "Circle", "Neural"], "C": ["Cloud", "Aether", "Mycelium"], "R": ["Fractal", "Circle", "Mycelium"]}
SINGLETON_RAILS = {"S": ["Sa", "Me"], "F": ["Su"], "C": ["Me", "Su"], "R": ["Me", "Sa"]}
SINGLETON_APPENDICES = {"S": ["AppA", "AppC", "AppM"], "F": ["AppE", "AppF", "AppP"], "C": ["AppI", "AppG", "AppQ"], "R": ["AppM", "AppP", "AppQ"]}
SINGLETON_SHORTCUTS = {"S": ["SCPT2-01", "SCPT2-03", "SCPT2-13"], "F": ["SCPT2-02", "SCPT2-04", "SCPT2-07"], "C": ["SCPT2-05", "SCPT2-10", "SCPT2-11"], "R": ["SCPT2-06", "SCPT2-12", "SCPT2-13"]}
BODY_SYSTEM_OVERRIDES = {"A01": "CoreMetro", "A02": "GrandCentral", "A03": "EmergentSupermap", "A04": "CrossCorpusMycelial", "A05": "HDSCTMetro", "A06": "Mycelial4D", "A07": "CrossCorpusMycelial", "A08": "EmergentSupermap", "A09": "AppendixOnlyMetro", "A10": "L3Neural", "A11": "BrainStem64", "A12": "AppendixOnlyMetro", "A13": "L4Transcendent", "A14": "BrainStem64", "A15": "HDSCTMetro", "A16": "AthenaFleetMetro", "A17": "CrossCorpusMycelial", "A18": "AppendixOnlyMetro", "A19": "Mycelial4D"}
DIRECT_BRIDGE_WEIGHTS = {"CS-001": 0.96, "CS-002": 0.93, "CS-003": 0.91}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_direct_bridge_edges() -> List[Dict[str, Any]]:
    candidate_payloads: List[Tuple[Path, str]] = [
        (BRIDGE_DENSIFICATION_FAMILIES_JSON_PATH, "bridge_families"),
        (WHOLE_CRYSTAL_BRIDGE_WITNESSES_PATH, "edges"),
    ]
    for path, key in candidate_payloads:
        if not path.exists():
            continue
        payload = load_json(path)
        direct = [
            item
            for item in payload.get(key, [])
            if item.get("edge_id") in DIRECT_BRIDGE_WEIGHTS
        ]
        if direct:
            return direct
    return []


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    return match.group(1) if match else "UNKNOWN"


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def unique(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def base4(value: int, digits: int = 4) -> str:
    if value <= 0:
        return "0".rjust(digits, "0")
    out: List[str] = []
    current = value
    while current:
        out.append(str(current % 4))
        current //= 4
    return "".join(reversed(out)).rjust(digits, "0")


def stable_index(text: str, modulo: int) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16) % modulo


def surface_from_path(path: str) -> str:
    lowered = path.replace("/", "\\").lower()
    if "\\ecosystem\\nervous_system\\" in lowered:
        return "GovernanceMirror"
    if "\\nervous_system\\" in lowered:
        return "Cortex"
    if "\\athena fleet\\" in lowered:
        return "FleetRuntime"
    if "\\14_deeper_integrated_cross_synthesis_network\\" in lowered:
        return "DeepRoot"
    return "RuntimeHub"


def lens_label(lens_id: str) -> str:
    mapping = {"S": "Square", "F": "Flower", "C": "Cloud", "R": "Fractal"}
    return " + ".join(mapping[ch] for ch in lens_id)


def lens_role(lens_id: str) -> str:
    return SINGLETON_ROLES.get(lens_id) or HYBRID_ROLES.get(lens_id, "hybrid-lens bridge")


def combine_channels(members: Sequence[str]) -> Dict[str, float]:
    vector = {key: 0.0 for key in BASE_CHANNEL_VECTOR}
    for member in members:
        for key, value in SINGLETON_CHANNELS[member].items():
            vector[key] += value
    total = sum(vector.values()) or 1.0
    return {key: round(value / total, 3) for key, value in vector.items()}


def truth_from_body(body: Dict[str, Any]) -> str:
    if body.get("status") == "live" and body.get("authority") in {"canonical", "runtime"}:
        return "OK"
    if body.get("status") == "live":
        return "NEAR"
    return "AMBIG"


def truth_from_pair(pair: Dict[str, Any]) -> str:
    witness = float(pair.get("witness_floor", 0.0))
    if pair.get("status") == "ACTIVE" and witness >= 0.88:
        return "OK"
    if pair.get("status") == "ACTIVE" and witness >= 0.76:
        return "NEAR"
    return "AMBIG"


def truth_from_wave(wave: Dict[str, Any]) -> str:
    if wave.get("stop_condition") == "PROMOTE":
        return "OK"
    if wave.get("status") == "ACTIVE":
        return "NEAR"
    return "AMBIG"


def build_systems() -> List[Dict[str, Any]]:
    specs = [
        ("CoreMetro", "Core Metro", "cortex", "stations-and-transfer-hubs", "replay-safe", "live-root", "address", NERVOUS_SYSTEM_ROOT / "20_METRO" / "00_CORE_METRO_MAP.md"),
        ("EmergentSupermap", "Deeper Emergent Supermap", "cortex", "transfer-hub expansions", "replay-safe", "live-root", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "05_DEEPER_EMERGENT_METRO_SUPERMAP.md"),
        ("L2DeepEmergence", "Level 2 Deep Emergence", "cortex", "level-2 relays", "replay-safe", "live-root", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "06_LVL2_DEEP_EMERGENCE_METRO_MAP.md"),
        ("L3Neural", "Level 3 Neural", "cortex", "level-3 neural yards", "replay-safe", "live-root", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "07_LVL3_DEEPER_NEURAL_MAP.md"),
        ("L4Transcendent", "Level 4 Transcendent", "cortex", "level-4 lift hubs", "replay-partial", "live-root", "chamber", NERVOUS_SYSTEM_ROOT / "20_METRO" / "08_LVL4_TRANSCENDENT_METRO_MAP.md"),
        ("Mycelial4D", "4D Mycelial Organism", "cortex", "organism membranes", "replay-safe", "live-root", "chamber", NERVOUS_SYSTEM_ROOT / "20_METRO" / "13_4D_MYCELIAL_ORGANISM_METRO_MAP.md"),
        ("CrossCorpusMycelial", "4D Cross-Corpus Mycelial", "field", "cross-corpus departure lanes", "replay-partial", "reservoir-aware", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "14_4D_MYCELIAL_CROSS_CORPUS_METRO_MAP.md"),
        ("BrainStem64", "64x Brain Stem", "cortex", "brain-stem yards", "replay-safe", "live-root", "address", NERVOUS_SYSTEM_ROOT / "20_METRO" / "15_64X_BRAIN_STEM_FASCIA_METRO_MAP.md"),
        ("Plexus256", "256x Plexus", "cortex", "microfascia loops", "replay-safe", "live-root", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "16_256X_PLEXUS_MICROFASCIA_METRO_MAP.md"),
        ("Arbor1024", "1024x Synaptic Arbor", "cortex", "return-ring arbors", "replay-safe", "live-root", "replay", NERVOUS_SYSTEM_ROOT / "20_METRO" / "17_1024X_SYNAPTIC_ARBOR_METRO_MAP.md"),
        ("GrandCentral", "Grand Central", "runtime", "station-and-mezzanine complex", "replay-safe", "live-root", "replay", NERVOUS_SYSTEM_ROOT / "20_METRO" / "19_GRAND_CENTRAL_STATION_METRO_MAP.md"),
        ("DeepRootMetroStack", "Deep Root Metro Stack", "deep-root", "resolution stack", "replay-safe", "live-root", "relation", DEEP_ROOT / "07_METRO_STACK" / "02_level_3_deeper_neural_map.md"),
        ("AthenaFleetMetro", "Athena FLEET Metro", "fleet", "cluster interconnect yard", "replay-safe", "live-root", "relation", NERVOUS_SYSTEM_ROOT / "20_METRO" / "18_ATHENA_FLEET_256_POW_4_METRO_MAP.md"),
        ("AppendixOnlyMetro", "Appendix-Only Metro", "field", "appendix signature hubs", "replay-safe", "live-root", "address", DEEP_ROOT / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md"),
        ("HDSCTMetro", "HD-SCT Metro", "field", "carrier projection docks", "replay-partial", "live-witness", "chamber", HD_SCT_PATH),
    ]
    return [{"system_id": sid, "label": label, "authority_surface": str(LEDGER_INTERLOCK_MD_PATH), "category": category, "station_family": family, "replay_class": replay, "drift_status": drift, "primary_zone": zone, "entry_station_ids": [], "exit_station_ids": [], "default_return_path": [], "source_paths": [str(path)], "note": "Phase 4 Pt 2 metro system."} for sid, label, category, family, replay, drift, zone, path in specs]


def build_stations() -> List[Dict[str, Any]]:
    specs = [
        ("ST-T3", "T3 Base Transfer", ["CoreMetro"], "transfer_hub", ["Sa"], "Arc0/Sa"),
        ("ST-T8", "T8 Emergent Exchange", ["EmergentSupermap", "L2DeepEmergence"], "transfer_hub", ["Su"], "Arc2/Su"),
        ("ST-T9", "T9 Mycelial Junction", ["CoreMetro", "Mycelial4D"], "transfer_hub", ["Me"], "Arc2/Me"),
        ("ST-T10", "T10 Grand Central Concourse", ["CoreMetro", "GrandCentral", "L3Neural"], "grand_central_concourse", ["Su", "Me", "Sa"], "Arc3/All"),
        ("ST-GCW", "GCW Weight Mezzanine", ["GrandCentral", "BrainStem64", "Plexus256"], "mezzanine", ["Sa"], "Arc3/Sa"),
        ("ST-GCZ", "GCZ Z-Point Junction", ["GrandCentral", "DeepRootMetroStack"], "tunnel_junction", ["Me"], "Arc3/Me"),
        ("ST-GCP", "GCP Replay Concourse", ["GrandCentral", "Mycelial4D"], "replay_concourse", ["Me", "Sa"], "Arc3/Me"),
        ("ST-AppM", "AppM Certificate Dock", ["AppendixOnlyMetro", "HDSCTMetro"], "appendix_hub", ["Sa"], "Arc6/Sa"),
        ("ST-AppQ", "AppQ Appendix-Only Hub", ["AppendixOnlyMetro", "DeepRootMetroStack"], "appendix_hub", ["Me"], "Arc6/Me"),
        ("ST-Ch11", "Ch11 Restart Kernel", ["DeepRootMetroStack", "GrandCentral"], "restart_kernel", ["Me"], "Arc3/Me"),
        ("ST-FLEET", "Athena FLEET Convergence Hub", ["AthenaFleetMetro", "CrossCorpusMycelial"], "fleet_hub", ["Su", "Me"], "Arc4/Su"),
        ("ST-DeepRoot", "Deep Root Gateway", ["DeepRootMetroStack", "L3Neural", "L4Transcendent"], "deep_root_gate", ["Su", "Me"], "Arc4/Me"),
        ("ST-HDSCT", "HD-SCT Carrier Exchange", ["HDSCTMetro", "AppendixOnlyMetro"], "carrier_exchange", ["Sa", "Su"], "Arc5/Sa"),
        ("ST-B64", "B64 Brain Stem Yard", ["BrainStem64", "GrandCentral"], "yard", ["Sa"], "Arc4/Sa"),
        ("ST-P256", "P256 Plexus Field", ["Plexus256", "GrandCentral"], "yard", ["Su"], "Arc4/Su"),
        ("ST-A1024", "A1024 Arbor Return Ring", ["Arbor1024", "GrandCentral"], "return_ring", ["Me", "Sa"], "Arc5/Me"),
        ("ST-Mycelium", "4D Mycelial Chamber", ["Mycelial4D", "CrossCorpusMycelial"], "chamber", ["Me"], "Arc4/Me"),
        ("ST-L2", "Level 2 Emergence Yard", ["L2DeepEmergence", "EmergentSupermap"], "yard", ["Su"], "Arc2/Su"),
        ("ST-L3", "Level 3 Neural Yard", ["L3Neural", "DeepRootMetroStack"], "yard", ["Su", "Me"], "Arc3/Su"),
        ("ST-L4", "Level 4 Transcendent Lift", ["L4Transcendent", "HDSCTMetro"], "lift", ["Su", "Sa"], "Arc5/Su"),
    ]
    return [{"station_id": sid, "label": label, "system_ids": systems, "station_type": station_type, "authority_surface": str(LEDGER_INTERLOCK_MD_PATH), "lane_membership": lanes, "coordinate_hint": hint, "source_paths": [str(LEDGER_INTERLOCK_MD_PATH)], "note": "Station, hub, or dock used by Pt 2 interlocks."} for sid, label, systems, station_type, lanes, hint in specs]


def dispatch_score(transform_kind: str, route_via: Sequence[str], proof_state: str, note: str) -> float:
    base = {"same_station": 7.35, "hub_transfer": 7.75, "rail_lift": 7.48, "appendix_dock": 7.18, "tunnel_crossing": 7.82, "pair_projection": 7.28, "body_projection": 7.36, "field_projection": 7.21, "promotion_departure": 6.96}[transform_kind]
    if "ST-GCW" in route_via:
        base += 0.08
    if "ST-GCZ" in route_via or "ST-Ch11" in route_via:
        base += 0.12
    if "ST-HDSCT" in route_via:
        base += 0.05
    if proof_state == "NEAR":
        base -= 0.08
    if any(token in normalize(note) for token in ["historical", "trading bot"]):
        base -= 0.22
    return round(clamp(base, 5.7, 8.2), 3)


def build_interlocks() -> List[Dict[str, Any]]:
    basis = [str(GRAND_CENTRAL_OVERVIEW_PATH), str(ADDRESSING_PATH), str(HIGHER_DIMENSIONAL_PATH), str(HD_SCT_PATH), str(HYBRID_LENS_PATH)]
    specs = [
        ("IX-01", "CoreMetro", "ST-T3", "EmergentSupermap", "ST-T8", "same_station", "Core metro hands off into the deeper supermap through the existing transfer lattice.", ["ST-T3", "ST-T8"], ["ST-GCP"], "OK", ""),
        ("IX-02", "EmergentSupermap", "ST-T8", "L2DeepEmergence", "ST-L2", "rail_lift", "Emergent supermap lifts into Level 2 through the Su rail.", ["ST-T8", "ST-L2"], ["ST-T10", "ST-GCP"], "OK", ""),
        ("IX-03", "L2DeepEmergence", "ST-L2", "L3Neural", "ST-L3", "rail_lift", "Level 2 emergence hands off into Level 3 neural routing.", ["ST-L2", "ST-L3"], ["ST-T10", "ST-GCP"], "OK", ""),
        ("IX-04", "L3Neural", "ST-L3", "L4Transcendent", "ST-L4", "rail_lift", "Level 3 lifts into Level 4 only through the transcendent lift.", ["ST-L3", "ST-L4"], ["ST-T10", "ST-GCP"], "NEAR", ""),
        ("IX-05", "CoreMetro", "ST-T10", "GrandCentral", "ST-T10", "hub_transfer", "Grand Central is the default interlock yard for multi-system routing.", ["ST-T10"], ["ST-GCP"], "OK", ""),
        ("IX-06", "GrandCentral", "ST-GCW", "BrainStem64", "ST-B64", "rail_lift", "Weight mezzanine dispatches into the brain stem yard.", ["ST-GCW", "ST-B64"], ["ST-T10", "ST-GCP"], "OK", ""),
        ("IX-07", "BrainStem64", "ST-B64", "Plexus256", "ST-P256", "rail_lift", "Brain stem traffic expands into the 256x plexus.", ["ST-B64", "ST-P256"], ["ST-GCW", "ST-T10"], "OK", ""),
        ("IX-08", "Plexus256", "ST-P256", "Arbor1024", "ST-A1024", "rail_lift", "Plexus traffic deepens into the synaptic arbor return ring.", ["ST-P256", "ST-A1024"], ["ST-GCW", "ST-T10"], "OK", ""),
        ("IX-09", "GrandCentral", "ST-GCZ", "DeepRootMetroStack", "ST-DeepRoot", "tunnel_crossing", "GCZ and Ch11 form the lawful tunnel crossing into the live deep root.", ["ST-GCZ", "ST-Ch11", "ST-DeepRoot"], ["ST-GCP"], "OK", ""),
        ("IX-10", "DeepRootMetroStack", "ST-AppQ", "AppendixOnlyMetro", "ST-AppM", "appendix_dock", "Appendix-only certification docks into the deep-root appendix map.", ["ST-AppQ", "ST-AppM"], ["ST-GCZ", "ST-T10"], "OK", ""),
        ("IX-11", "AppendixOnlyMetro", "ST-AppM", "HDSCTMetro", "ST-HDSCT", "same_station", "HD-SCT uses Appendix M as a deterministic certificate dock.", ["ST-AppM", "ST-HDSCT"], ["ST-AppQ", "ST-GCZ"], "OK", ""),
        ("IX-12", "CoreMetro", "ST-T9", "Mycelial4D", "ST-Mycelium", "body_projection", "T9 projects cortical traffic into the 4D mycelial organism.", ["ST-T9", "ST-Mycelium"], ["ST-GCP"], "OK", ""),
        ("IX-13", "Mycelial4D", "ST-Mycelium", "CrossCorpusMycelial", "ST-FLEET", "field_projection", "Mycelial field projection opens the cross-corpus departure lane.", ["ST-Mycelium", "ST-FLEET"], ["ST-GCP", "ST-T10"], "NEAR", "Historical reservoirs remain visible and non-authoritative on this crossing."),
        ("IX-14", "GrandCentral", "ST-T10", "AthenaFleetMetro", "ST-FLEET", "body_projection", "Grand Central projects into the Athena FLEET cluster through the fleet hub.", ["ST-T10", "ST-FLEET"], ["ST-GCP"], "OK", ""),
        ("IX-15", "AthenaFleetMetro", "ST-FLEET", "CrossCorpusMycelial", "ST-FLEET", "promotion_departure", "Fleet promotion moves into the cross-corpus lane without dissolving the local cluster.", ["ST-FLEET", "ST-T10"], ["ST-GCP"], "OK", ""),
        ("IX-16", "CrossCorpusMycelial", "ST-FLEET", "GrandCentral", "ST-T10", "hub_transfer", "Cross-corpus traffic returns through Grand Central with blocked Trading Bot evidence kept visible.", ["ST-FLEET", "ST-T10"], ["ST-GCP"], "NEAR", "Trading Bot evidence reservoir is cited but cannot become authority while the Docs gate is blocked."),
        ("IX-17", "HDSCTMetro", "ST-HDSCT", "GrandCentral", "ST-T10", "field_projection", "HD-SCT carrier projections re-enter the main hall through Grand Central.", ["ST-HDSCT", "ST-GCW", "ST-T10"], ["ST-GCP"], "OK", ""),
        ("IX-18", "L3Neural", "ST-L3", "DeepRootMetroStack", "ST-DeepRoot", "pair_projection", "Level 3 neural routes resolve into the live deep-root pair store.", ["ST-L3", "ST-DeepRoot"], ["ST-GCZ"], "OK", ""),
        ("IX-19", "AppendixOnlyMetro", "ST-AppM", "CoreMetro", "ST-T3", "appendix_dock", "Appendix signatures can route back into the core metro when certification is complete.", ["ST-AppM", "ST-T3"], ["ST-T10", "ST-GCP"], "OK", ""),
        ("IX-20", "L4Transcendent", "ST-L4", "HDSCTMetro", "ST-HDSCT", "field_projection", "Transcendent lift hands off into HD-SCT carrier space.", ["ST-L4", "ST-HDSCT"], ["ST-T10", "ST-GCP"], "NEAR", ""),
        ("IX-21", "DeepRootMetroStack", "ST-Ch11", "GrandCentral", "ST-GCZ", "tunnel_crossing", "Ch11 restarts close back through GCZ and Grand Central.", ["ST-Ch11", "ST-GCZ", "ST-T10"], ["ST-GCP"], "OK", ""),
        ("IX-22", "GrandCentral", "ST-GCW", "Plexus256", "ST-P256", "hub_transfer", "Grand Central may jump straight to the plexus when the weight mezzanine is hot.", ["ST-GCW", "ST-P256"], ["ST-T10", "ST-GCP"], "OK", ""),
        ("IX-23", "GrandCentral", "ST-GCP", "Mycelial4D", "ST-Mycelium", "field_projection", "Replay concourse bridges into the mycelial chamber without bypassing return law.", ["ST-GCP", "ST-Mycelium"], ["ST-T10"], "OK", ""),
        ("IX-24", "EmergentSupermap", "ST-T8", "CrossCorpusMycelial", "ST-FLEET", "promotion_departure", "The deeper supermap can promote directly into the cross-corpus lane if Grand Central witness remains intact.", ["ST-T8", "ST-T10", "ST-FLEET"], ["ST-GCP"], "NEAR", "Shorter witnessed corridor declared through T8 -> T10 -> FLEET."),
    ]
    return [{"interlock_id": iid, "source_system": src_sys, "source_station": src_station, "target_system": dst_sys, "target_station": dst_station, "transform_kind": kind, "witness_basis": basis, "dispatch_rule": rule, "dispatch_score": dispatch_score(kind, route_via, proof, note), "return_path": ret, "route_via": route_via, "proof_state": proof, "status": "LIVE", "note": note} for iid, src_sys, src_station, dst_sys, dst_station, kind, rule, route_via, ret, proof, note in specs]


def apply_system_defaults(systems: List[Dict[str, Any]], stations: List[Dict[str, Any]], interlocks: List[Dict[str, Any]]) -> None:
    station_by_system: Dict[str, List[str]] = {}
    for station in stations:
        for system_id in station["system_ids"]:
            station_by_system.setdefault(system_id, []).append(station["station_id"])
    entries: Dict[str, List[str]] = {}
    exits: Dict[str, List[str]] = {}
    for interlock_record in interlocks:
        entries.setdefault(interlock_record["target_system"], []).append(interlock_record["target_station"])
        exits.setdefault(interlock_record["source_system"], []).append(interlock_record["source_station"])
    for system in systems:
        system["entry_station_ids"] = unique([*station_by_system.get(system["system_id"], []), *entries.get(system["system_id"], [])])[:4]
        system["exit_station_ids"] = unique([*exits.get(system["system_id"], []), *station_by_system.get(system["system_id"], [])])[:4]
        if system["system_id"] == "GrandCentral":
            system["default_return_path"] = ["ST-GCP", "ST-T10"]
        elif system["system_id"] == "DeepRootMetroStack":
            system["default_return_path"] = ["ST-Ch11", "ST-GCZ", "ST-T10"]
        elif system["system_id"] in {"CrossCorpusMycelial", "AthenaFleetMetro"}:
            system["default_return_path"] = ["ST-FLEET", "ST-T10", "ST-GCP"]
        elif system["system_id"] in {"AppendixOnlyMetro", "HDSCTMetro"}:
            system["default_return_path"] = ["ST-AppM", "ST-AppQ", "ST-GCZ", "ST-T10"]
        else:
            system["default_return_path"] = ["ST-T10", "ST-GCP"]


def build_simple_registry_specs() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    carriers = [{"carrier_id": cid, "label": cid, "role": role, "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "transform_neighbors": neighbors, "dominant_zone": zone, "note": "Carrier promoted into the Pt 2 machine layer."} for cid, role, zone, neighbors in [("Square", "addressable structure and indexing", "address", ["Triangle", "Flower", "Nervous"]), ("Circle", "phase and timing carrier", "phase", ["Flower", "Fractal", "Neural"]), ("Triangle", "legality and carry governor", "governance", ["Square", "Fractal", "Nervous"]), ("Flower", "resonance and orbit carrier", "resonance", ["Circle", "Cloud", "Neural"]), ("Cloud", "field and Aether carrier", "field", ["Flower", "Aether", "Mycelium"]), ("Fractal", "replay and regeneration carrier", "replay", ["Cloud", "Triangle", "Mycelium"]), ("Zero", "exact re-entry and recommitment", "zero", ["Aether", "Fractal"]), ("Aether", "integrated transport and high-coherence loading", "field", ["Cloud", "Zero", "Neural"]), ("Nervous", "cortical routing tissue", "organism", ["Square", "Triangle", "Mycelium"]), ("Mycelium", "cross-body membrane transport", "organism", ["Cloud", "Fractal", "Nervous"]), ("Neural", "wave and packet carrier", "runtime", ["Flower", "Circle", "Aether"])]]
    triad = ["Su", "Me", "Sa"]
    rails: List[Dict[str, Any]] = []
    for rid, purpose, kinds in [("Su", "synthesis, lift, and outbound transfer", ["same_station", "rail_lift", "promotion_departure"]), ("Me", "memory, restart, and replay closure", ["tunnel_crossing", "field_projection", "body_projection"]), ("Sa", "structure, legality, and certificate lock", ["hub_transfer", "appendix_dock", "pair_projection"])]:
        chapters = []
        for chapter in range(1, 22):
            omega = chapter - 1
            alpha = omega // 3
            lane = triad[(omega % 3 + alpha % 3) % 3]
            if lane == rid:
                chapters.append(f"Ch{chapter:02d}")
        rails.append({"rail_id": rid, "label": rid, "chapter_ids": chapters, "control_purpose": purpose, "allowed_transfer_kinds": kinds, "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": "Control rail overlay; not a standalone ontology."})
    arcs = [{"arc_id": f"Arc{alpha}", "omega_range": [alpha * 3, min(alpha * 3 + 2, 20)], "rho": alpha % 3, "rotated_triad": triad[alpha % 3 :] + triad[: alpha % 3], "chapter_assignments": [{"chapter_id": f"Ch{chapter:02d}", "lane": triad[((chapter - 1) % 3 + alpha % 3) % 3]} for chapter in range(alpha * 3 + 1, min(alpha * 3 + 4, 22))], "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": "Arc rotation record inherited from the address grammar."} for alpha in range(7)]
    transforms = [{"transform_id": tid, "source_carriers": src, "target_carriers": dst, "transform_law": law, "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": "Carrier transform law used by Pt 2 projections."} for tid, src, dst, law in [("CT-01", ["Square"], ["Flower"], "Square stabilizes address before resonance opens."), ("CT-02", ["Flower"], ["Cloud"], "Resonance sweeps phase into field permeability."), ("CT-03", ["Cloud"], ["Fractal"], "Cloud folds into replayable regeneration."), ("CT-04", ["Square", "Circle", "Triangle"], ["Flower", "Cloud", "Fractal"], "Base carriers project into higher-dimensional carrier families."), ("CT-05", ["Zero"], ["Aether"], "Zero becomes Aether only after exact recommitment and certificate closure.")]]
    singletons = [{"lens_id": lid, "label": lens_label(lid), "class_type": "singleton", "members": [lid], "role": lens_role(lid), "default_gate": lid, "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": f"{lid} acts as a singleton Pt 2 lens family."} for lid in LENS_ORDER]
    hybrids: List[Dict[str, Any]] = []
    profiles: List[Dict[str, Any]] = []
    for mask in range(1, 2 ** len(LENS_ORDER)):
        lid = "".join(LENS_ORDER[index] for index in range(len(LENS_ORDER)) if mask & (1 << index))
        members = list(lid)
        hybrids.append({"lens_id": lid, "label": lens_label(lid), "class_type": "singleton" if len(members) == 1 else "hybrid", "members": members, "role": lens_role(lid), "default_gate": lid, "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": "Full non-empty S/F/C/R closure lattice."})
        profiles.append({"lens_id": lid, "label": lens_label(lid), "members": members, "preferred_channels": [k for k, v in combine_channels(members).items() if v >= 0.15], "preferred_carriers": unique(c for m in members for c in SINGLETON_CARRIERS[m]), "preferred_rails": unique(r for m in members for r in SINGLETON_RAILS[m]), "appendix_support": unique([*(a for m in members for a in SINGLETON_APPENDICES[m]), *APPENDIX_SUPPORT_SET])[:9], "shortcut_chain": unique(s for m in members for s in SINGLETON_SHORTCUTS[m]), "stop_condition": "PROMOTE" if lid == "SFCR" else ("REPAIR" if "R" in lid else "ABSTAIN"), "writeback_targets": [str(LEDGER_LENS_MD_PATH), str(DASHBOARD_MD_PATH), str(EDGE_MD_PATH)], "channel_weights": combine_channels(members), "certificate_rule": lens_role(lid), "authority_surface": str(SCHEMA_PRIMARY_MD_PATH), "note": "Hybrid profile derived as a weighted merge of singleton channels plus a certificate check."})
    fields = [{"field_id": fid, "label": label, "carrier_binding": carriers, "role": role, "authority_surface": str(LEDGER_FIELD_MD_PATH), "thresholds": thresholds, "source_paths": [str(HIGHER_DIMENSIONAL_PATH), str(HD_SCT_PATH)], "note": "Field object elevated into the Pt 2 machine layer."} for fid, label, carriers, role, thresholds in [("Zero", "Zero", ["Zero", "Fractal"], "exact re-entry and recommitment", {"aether_floor": 0.35, "zero_floor": 0.72}), ("Aether", "Aether", ["Aether", "Cloud", "Neural"], "integrated transport and high-coherence loading", {"aether_floor": 0.78, "tunnel_cost_ceiling": 0.55}), ("CloudManifold", "Cloud Manifold", ["Cloud", "Aether", "Mycelium"], "field permeability and cloud transport", {"aether_floor": 0.65, "resonance_pressure_floor": 0.56}), ("TunnelGeodesic", "Tunnel Geodesic", ["Zero", "Aether", "Cloud"], "tunnel route minimization and lawful restarts", {"zero_floor": 0.61, "tunnel_cost_ceiling": 0.58}), ("RailHardeningBand", "Rail Hardening Band", ["Triangle", "Nervous", "Fractal"], "hardens control rails before promotion", {"rail_hardness_floor": 0.62}), ("ResonancePressureBand", "Resonance Pressure Band", ["Flower", "Circle", "Neural"], "tracks resonance intensity and heat traces", {"resonance_pressure_floor": 0.52})]]
    zpoints = [{"zpoint_id": zid, "label": label, "route_class": route_class, "restart_token": token, "binding_hubs": hubs, "proof_state": proof, "authority_surface": str(LEDGER_FIELD_MD_PATH), "source_paths": [str(GRAND_CENTRAL_OVERVIEW_PATH), str(LEDGER_FIELD_MD_PATH)], "note": "Z-point family bound to Grand Central and Ch11."} for zid, label, route_class, token, hubs, proof in [("Z0", "Intake Zero", "intake", "INTAKE-FIRST-WITNESS", ["ST-GCZ", "ST-T10"], "NEAR"), ("Z1", "Restart Zero", "restart", "CH11-RESTART-CONTINUITY", ["ST-Ch11", "ST-GCZ"], "OK"), ("Z2", "Contradiction Zero", "quarantine", "CONTRADICTION-PRESERVE-BOTH", ["ST-GCZ", "ST-GCP"], "NEAR"), ("Z3", "Carrier Zero", "carrier_lift", "HD-SCT-PROJECTION-LAW", ["ST-HDSCT", "ST-AppM"], "NEAR"), ("Z4", "Fleet Zero", "promotion", "FLEET-CLUSTER-RETURN", ["ST-FLEET", "ST-T10"], "NEAR"), ("Z5", "Aether Zero", "field_closure", "AETHER-CERTIFICATE-CLOSE", ["ST-GCW", "ST-HDSCT"], "OK")]]
    spaces = [{"space_id": sid, "label": label, "axes": axes, "carrier_focus": focus, "authority_surface": str(LEDGER_PROJECTION_MD_PATH), "crosswalk_rules": rules, "note": "3D projection surface for Pt 2."} for sid, label, axes, focus, rules in [("Transit3D", "Transit 3D", ["station", "hub", "yard"], ["Square", "Circle", "Triangle"], ["Transit routes crosswalk into Carrier3D through preferred carriers."]), ("Carrier3D", "Carrier 3D", ["carrier", "phase", "certificate"], ["Square", "Flower", "Cloud", "Fractal"], ["Carrier transforms bridge Carrier3D into Lens3D and Field3D."]), ("Lens3D", "Lens 3D", ["lens", "hybrid", "bias"], ["Square", "Flower", "Cloud", "Fractal"], ["Lens3D becomes Organism3D only when a body or node holds the carrier."]), ("Organism3D", "Organism 3D", ["body", "tract", "hemisphere"], ["Nervous", "Mycelium", "Neural"], ["Organism3D routes back into Transit3D through Grand Central and replay."]), ("Field3D", "Field 3D", ["aether", "zero", "tunnel"], ["Cloud", "Aether", "Zero"], ["Field3D crosses into Lens3D and Carrier3D only with replay closure."])]]
    shortcuts = [{"shortcut_id": sid, "label": label, "trigger": trig, "preferred_zones": zones, "preferred_surface_classes": classes, "ranking_stack": rank, "stop_condition": stop, "required_inputs": inputs, "authority_surface": str(SCHEMA_QUERY_MD_PATH), "note": "Phase 4 Pt 2 deterministic shortcut."} for sid, label, trig, zones, classes, rank, stop, inputs in [("SCPT2-01", "SquareAnchor", "address-first grounding", ["cortex", "appendix"], ["body_station", "body", "node"], ["authority", "witness", "system", "coordinate", "lens"], "REPAIR", ["seed surface", "body or node id"]), ("SCPT2-02", "CirclePhaseSync", "phase alignment", ["cortex", "deep-root"], ["pair", "wave"], ["authority", "witness", "system", "lens", "field"], "REPAIR", ["objective", "phase-bearing surface"]), ("SCPT2-03", "TriangleLegalityCheck", "carry legality", ["cortex", "field"], ["body", "pair", "route"], ["authority", "witness", "rail", "coordinate"], "ABSTAIN", ["candidate route", "rail context"]), ("SCPT2-04", "FlowerResonanceSweep", "resonance scan", ["runtime", "field"], ["wave", "pair"], ["authority", "witness", "lens", "field"], "REPAIR", ["objective"]), ("SCPT2-05", "CloudFieldProbe", "field-density scan", ["field", "deep-root"], ["wave", "projection"], ["authority", "witness", "field", "coordinate", "lens"], "ABSTAIN", ["field seed"]), ("SCPT2-06", "FractalReplayFold", "replay-first regeneration", ["runtime", "cortex"], ["wave", "body", "node"], ["authority", "witness", "field", "writeback"], "REPAIR", ["record id"]), ("SCPT2-07", "HybridFaceJump", "jump to nearest useful hybrid lens family", ["field", "deep-root"], ["pair", "wave", "projection"], ["authority", "witness", "system", "lens", "field"], "PROMOTE", ["objective", "dominant lens"]), ("SCPT2-08", "LensBalance", "rebalance over-fit lens stacks", ["cortex", "runtime"], ["body", "node", "wave"], ["authority", "witness", "lens", "field"], "REPAIR", ["record id"]), ("SCPT2-09", "MetroInterlockJump", "use explicit interlock instead of inferred hop", ["cortex", "runtime", "deep-root"], ["route", "interlock"], ["authority", "witness", "system", "interlock"], "PROMOTE", ["source", "target"]), ("SCPT2-10", "ZPointDive", "restart or tunnel dive through GCZ", ["deep-root", "field"], ["route", "wave"], ["authority", "witness", "field", "interlock"], "QUARANTINE", ["restart seed"]), ("SCPT2-11", "AetherBridge", "cross through Aether density rather than flat similarity", ["field", "runtime"], ["projection", "wave", "pair"], ["authority", "witness", "field", "lens"], "PROMOTE", ["field seed", "objective"]), ("SCPT2-12", "MycelialBackfill", "repair neglected membrane routes before outward lift", ["field", "cortex"], ["body", "pair", "projection"], ["authority", "witness", "field", "writeback"], "REPAIR", ["neglect signal"]), ("SCPT2-13", "HDSCTLift", "project through higher-dimensional carriers", ["field", "deep-root"], ["projection", "pair", "route"], ["authority", "witness", "system", "coordinate", "lens", "field"], "PROMOTE", ["projection seed"])]] 
    queries = [{"query_id": qid, "mode": mode, "scope": scope, "active_shortcuts": shortcuts_used, "stop_rule": stop, "default_exploration_order": QUERY_ORDER, "writeback_targets": targets, "authority_surface": str(QUERY_PRESETS_MD_PATH), "note": "Phase 4 Pt 2 query preset."} for qid, mode, scope, shortcuts_used, stop, targets in [("QPT2-01", "locate", "all active registries", ["SCPT2-01", "SCPT2-08", "SCPT2-13"], "ABSTAIN", [str(DASHBOARD_MD_PATH)]), ("QPT2-02", "route", "system and interlock graph", ["SCPT2-03", "SCPT2-09", "SCPT2-10"], "REPAIR", [str(LEDGER_INTERLOCK_MD_PATH), str(DASHBOARD_MD_PATH)]), ("QPT2-03", "fire", "lens states and field weights", ["SCPT2-04", "SCPT2-07", "SCPT2-11"], "PROMOTE", [str(LEDGER_LENS_MD_PATH), str(LEDGER_FIELD_MD_PATH)]), ("QPT2-04", "promote", "lawful promotion candidates", ["SCPT2-03", "SCPT2-09", "SCPT2-12"], "PROMOTE", [str(LEDGER_MAIN_MD_PATH), str(EDGE_MD_PATH)]), ("QPT2-05", "interlock", "metro interlock registry", ["SCPT2-09", "SCPT2-13"], "PROMOTE", [str(LEDGER_INTERLOCK_MD_PATH)]), ("QPT2-06", "lens", "lens profiles and lens states", ["SCPT2-07", "SCPT2-08"], "REPAIR", [str(LEDGER_LENS_MD_PATH)]), ("QPT2-07", "field", "field, z-point, and aether surfaces", ["SCPT2-05", "SCPT2-10", "SCPT2-11"], "ABSTAIN", [str(LEDGER_FIELD_MD_PATH)]), ("QPT2-08", "project", "projection spaces and assignments", ["SCPT2-07", "SCPT2-13"], "REPAIR", [str(LEDGER_PROJECTION_MD_PATH)])]]
    return carriers, rails, arcs, transforms, singletons, hybrids, profiles, fields, zpoints, spaces, shortcuts, queries


def build_state_registries(phase4_body: Dict[str, Any], phase4_node: Dict[str, Any], phase4_pair: Dict[str, Any], phase4_wave: Dict[str, Any], profiles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    profile_map = {profile["lens_id"]: profile for profile in profiles}
    pair_by_id = {pair["pair_id"]: pair for pair in phase4_pair["pairs"]}
    coordinates: List[Dict[str, Any]] = []
    lens_states: List[Dict[str, Any]] = []
    assignments: List[Dict[str, Any]] = []
    aether_points: List[Dict[str, Any]] = []

    def detect_members(record_type: str, record: Dict[str, Any], system_id: str, extra: Sequence[str]) -> List[str]:
        members: List[str] = []
        tract = normalize(str(record.get("tract", "")))
        dock = normalize(str(record.get("dock", "")))
        lines = [normalize(item) for item in record.get("line_ids", [])]
        appendix = [normalize(item) for item in record.get("appendix_support", [])]
        source = normalize(" ".join(record.get("source_paths", [])) + " " + " ".join(extra))
        if "address" in tract or "gcl" in dock or "gca" in dock or "crystal" in lines:
            members.append("S")
        if "relation" in tract or "gct" in dock or "transit" in lines:
            members.append("F")
        if "chamber" in tract or "gcz" in dock or "appi" in appendix or "appq" in appendix:
            members.append("C")
        if "replay" in tract or "gcp" in dock or "origin" in lines or "appm" in appendix:
            members.append("R")
        if system_id in {"GrandCentral", "DeepRootMetroStack"}:
            members.extend(["C", "R"])
        if system_id == "AthenaFleetMetro":
            members.extend(["S", "F"])
        if system_id == "HDSCTMetro" or "higher d square circle triangle" in source:
            members.extend(["S", "F", "C"])
        if record_type == "wave":
            members.extend(["F", "R"])
        return [member for member in LENS_ORDER if member in members] or ["S"]

    def pick_pair_system(pair: Dict[str, Any]) -> str:
        appendix = set(pair.get("appendix_support", []))
        lines = set(pair.get("line_ids", []))
        if "AppQ" in appendix:
            return "DeepRootMetroStack"
        if {"AppE", "AppF", "AppG"} & appendix and float(pair.get("charge_seed", {}).get("imagination", 0.0)) >= 0.33:
            return "HDSCTMetro"
        if "Origin" in lines:
            return "Mycelial4D"
        if "Transit" in lines and "Crystal" in lines:
            return "L3Neural"
        if "Transit" in lines:
            return ["BrainStem64", "Plexus256", "Arbor1024", "L3Neural"][stable_index(pair["pair_id"], 4)]
        if "Crystal" in lines:
            return "Plexus256"
        return "AppendixOnlyMetro"

    def pick_node_system(node: Dict[str, Any]) -> str:
        for tag in node.get("tags", []):
            if re.fullmatch(r"A\d{2}", tag):
                return BODY_SYSTEM_OVERRIDES.get(tag, "GrandCentral")
        if "gc" in normalize(str(node.get("dock", ""))):
            return "GrandCentral"
        return "CoreMetro"

    pair_systems: Dict[str, str] = {}
    rows: List[Tuple[str, str, Dict[str, Any], str, str, Sequence[str], Sequence[str], str, Sequence[str], str, str, Sequence[str]]] = []
    for body in phase4_body["bodies"]:
        rows.append((body["body_id"], "body", body, BODY_SYSTEM_OVERRIDES.get(body["body_id"], "GrandCentral"), truth_from_body(body), [], [], body.get("tract", ""), body.get("source_paths", []), body.get("authority_surface", str(POINTERS_MD_PATH)), body.get("replay_hint", ""), []))
    for node in phase4_node["nodes"]:
        rows.append((node["node_id"], "node", node, pick_node_system(node), "OK" if node.get("status") == "LIVE" else "NEAR", [], [], node.get("tract", ""), node.get("source_paths", []), node.get("authority_surface", str(POINTERS_MD_PATH)), node.get("replay_hint", ""), node.get("tags", [])))
    for pair in phase4_pair["pairs"]:
        pair_systems[pair["pair_id"]] = pick_pair_system(pair)
        rows.append((pair["pair_id"], "pair", pair, pair_systems[pair["pair_id"]], truth_from_pair(pair), pair.get("appendix_support", []), pair.get("line_ids", []), pair.get("tract", ""), pair.get("source_paths", []), pair.get("authority_surface", str(DEEP_ROOT / "05_MATRIX_16X16")), pair.get("replay_hint", ""), [pair.get("bridge_opportunity", "")]))
    for wave in phase4_wave["waves"]:
        pair = pair_by_id[wave["pair_id"]]
        system_id = "GrandCentral" if any(token in normalize(wave.get("objective", "")) for token in ["field", "cloud", "aether", "zero"]) else pair_systems[wave["pair_id"]]
        rows.append((wave["wave_id"], "wave", wave, system_id, truth_from_wave(wave), pair.get("appendix_support", []), pair.get("line_ids", []), pair.get("tract", ""), wave.get("evidence_paths", []), str(JSON_OUTPUTS["lens_state_registry"]), pair.get("replay_hint", ""), [wave.get("objective", ""), wave.get("stop_condition", "")]))

    for index, (record_id, record_type, record, system_id, truth, appendix_support, line_ids, tract, source_paths, authority_surface, replay_hint, extra) in enumerate(rows, start=1):
        seed_members = detect_members(record_type, record, system_id, extra)
        vector: Dict[str, float] = {}
        for lens_id, profile in profile_map.items():
            members = set(profile["members"])
            score = 0.48 * (len(set(seed_members) & members) / max(1, len(members))) + 0.22 * (len(set(seed_members) & members) / max(1, len(seed_members)))
            if record_type == "body" and "S" in members:
                score += 0.08
            if record_type == "wave" and {"F", "C"} & members:
                score += 0.09
            if "AppQ" in appendix_support and "C" in members:
                score += 0.08
            if system_id in {"DeepRootMetroStack", "HDSCTMetro"} and "C" in members:
                score += 0.06
            if system_id == "GrandCentral" and "R" in members:
                score += 0.05
            vector[lens_id] = round(clamp(score, 0.0, 1.0), 3)
        ranked = sorted(vector.items(), key=lambda item: (-item[1], item[0]))
        dominant = ranked[0][0]
        secondary = ranked[1][0] if len(ranked) > 1 else ""
        rail = profile_map[dominant]["preferred_rails"][0]
        field_vector = {
            "aether_density": round(clamp(0.46 + (0.20 if "C" in dominant else 0.0) + (0.05 if "F" in dominant else 0.0) + (0.09 if system_id == "HDSCTMetro" else 0.0), 0.0, 1.0), 3),
            "zero_proximity": round(clamp(0.28 + (0.18 if "R" in dominant else 0.0) + (0.08 if system_id in {"DeepRootMetroStack", "GrandCentral"} else 0.0), 0.0, 1.0), 3),
            "tunnel_cost": round(clamp(0.66 - (0.08 if "C" in dominant else 0.0) - (0.06 if "R" in dominant else 0.0) - (0.06 if system_id in {"DeepRootMetroStack", "GrandCentral"} else 0.0), 0.0, 1.0), 3),
            "rail_hardness": round(clamp({"Su": 0.57, "Me": 0.66, "Sa": 0.81}[rail] + (0.08 if "S" in dominant else 0.0), 0.0, 1.0), 3),
            "resonance_pressure": round(clamp(0.42 + (0.18 if "F" in dominant else 0.0) + (0.06 if "C" in dominant else 0.0) + (0.09 if record_type == "wave" else 0.0), 0.0, 1.0), 3),
            "repair_gain": round(clamp(0.39 + (0.16 if "R" in dominant else 0.0) + (0.05 if "S" in dominant else 0.0) + (0.06 if truth == "OK" else 0.0), 0.0, 1.0), 3),
        }
        supported = ["Organism3D", "Carrier3D", "Lens3D", "Transit3D"] if record_type == "body" else (["Transit3D", "Carrier3D", "Lens3D"] if record_type == "node" else (["Lens3D", "Carrier3D", "Transit3D"] if record_type == "pair" else ["Field3D", "Lens3D", "Carrier3D"]))
        if "C" in dominant or system_id in {"GrandCentral", "DeepRootMetroStack"}:
            supported.append("Field3D")
        if record_type == "wave" and system_id in {"GrandCentral", "Mycelial4D", "CrossCorpusMycelial"}:
            supported.append("Organism3D")
        supported = unique(supported)
        unsupported = [space for space in ["Transit3D", "Carrier3D", "Lens3D", "Organism3D", "Field3D"] if space not in supported]
        face = "Aether" if "C" in dominant and system_id in {"DeepRootMetroStack", "HDSCTMetro", "GrandCentral"} else ("Water" if "replay" in normalize(tract) else ("Air" if "relation" in normalize(tract) else ("Fire" if "chamber" in normalize(tract) or (record_type == "wave" and "F" in dominant) else "Earth")))
        coordinates.append({"coord_id": f"HC-{index:04d}", "record_id": record_id, "record_type": record_type, "addr4": (f"{record_id}<{base4(int(record_id[1:]) - 1)}>" if record_type == "body" else f"{record_id}<{base4(index % 256)}>"), "face6": face, "arc7": f"Arc{stable_index(record_id, 7)}", "rail3": rail, "depth5": {"body": "D1", "node": "D2", "pair": "D3", "wave": "D4"}[record_type], "lens15": dominant, "system_id": system_id, "truth": truth, "surface": surface_from_path(authority_surface), "authority_surface": str(JSON_OUTPUTS["holo_coordinate_registry"]), "source_paths": list(source_paths), "replay_hint": replay_hint})
        lens_states.append({"state_id": f"LS-{index:04d}", "record_id": record_id, "record_type": record_type, "dominant_lens_system": dominant, "secondary_lens_system": secondary, "lens_weight_vector": vector, "preferred_carriers": profile_map[dominant]["preferred_carriers"], "preferred_rails": profile_map[dominant]["preferred_rails"], "supported_projection_spaces": supported, "unsupported_projection_spaces": unsupported, "field_weight_vector": field_vector, "authority_surface": str(JSON_OUTPUTS["lens_state_registry"]), "source_paths": list(source_paths), "replay_hint": replay_hint})
        assignments.append({"assignment_id": f"PA-{index:04d}", "record_id": record_id, "record_type": record_type, "supported_spaces": supported, "unsupported_spaces": unsupported, "preferred_space": {"body": "Organism3D", "node": "Transit3D", "pair": "Lens3D", "wave": "Field3D"}[record_type], "authority_surface": str(JSON_OUTPUTS["projection_assignment_registry"]), "source_paths": list(source_paths), "note": "Projection-space assignment for Pt 2."})
        mode = "z-point tunnel" if field_vector["zero_proximity"] >= 0.64 else ("aether geodesic" if field_vector["aether_density"] >= 0.72 else "rail transit")
        aether_points.append({"point_id": f"AP-{index:04d}", "source_record_id": record_id, "source_record_type": record_type, "lens_system": dominant, "system_id": system_id, "aether_density": field_vector["aether_density"], "zero_proximity": field_vector["zero_proximity"], "tunnel_cost": field_vector["tunnel_cost"], "rail_hardness": field_vector["rail_hardness"], "resonance_pressure": field_vector["resonance_pressure"], "repair_gain": field_vector["repair_gain"], "geodesic_mode": mode, "authority_surface": str(JSON_OUTPUTS["aether_point_registry"]), "source_paths": list(source_paths), "note": "Aether point projected from the Pt 2 field-weight layer."})
    return coordinates, lens_states, assignments, aether_points


def wrap(list_key: str, items: Sequence[Any], authority_surface: Path, docs_gate: str, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "docs_gate": docs_gate, "authority_surface": str(authority_surface), list_key: list(items), "summary": {"count": len(items)}}
    if extra:
        payload.update(extra)
    return payload


def main() -> int:
    docs_gate = parse_docs_gate(DOCS_GATE_PATH.read_text(encoding="utf-8"))
    phase4_body = load_json(PHASE4_BODY_JSON_PATH)
    phase4_node = load_json(PHASE4_NODE_JSON_PATH)
    phase4_pair = load_json(PHASE4_PAIR_JSON_PATH)
    phase4_wave = load_json(PHASE4_WAVE_JSON_PATH)
    phase4_dashboard = load_json(PHASE4_DASHBOARD_JSON_PATH)
    knowledge_dashboard = load_json(KNOWLEDGE_FABRIC_DASHBOARD_JSON_PATH)
    systems = build_systems()
    stations = build_stations()
    interlocks = build_interlocks()
    apply_system_defaults(systems, stations, interlocks)
    carriers, rails, arcs, transforms, singletons, hybrids, profiles, fields, zpoints, spaces, shortcuts, queries = build_simple_registry_specs()
    coordinates, lens_states, assignments, aether_points = build_state_registries(phase4_body, phase4_node, phase4_pair, phase4_wave, profiles)
    edges = [{"edge_id": f"XW-{index:03d}", "source_id": item["source_system"], "target_id": item["target_system"], "edge_kind": "inter-metro", "bridge_reason": item["transform_kind"], "weight": round(item["dispatch_score"] / 10.0, 3), "witness_basis": item["witness_basis"], "note": item["dispatch_rule"]} for index, item in enumerate(interlocks, start=1)]
    edges.extend({"edge_id": f"XW-{len(edges)+i+1:03d}", "source_id": profile["lens_id"], "target_id": profile["preferred_carriers"][0], "edge_kind": "inter-lens", "bridge_reason": profile["certificate_rule"], "weight": round(max(profile["channel_weights"].values()), 3), "witness_basis": [profile["authority_surface"]], "note": "Lens profile resolves into its preferred carrier family."} for i, profile in enumerate(profiles))
    for item in load_direct_bridge_edges():
        edges.append(
            {
                "edge_id": item["edge_id"],
                "source_id": item.get("source_body_id", item.get("source_root", "")),
                "target_id": item.get("target_body_id", item.get("target_root", "")),
                "edge_kind": "direct-bridge-family",
                "bridge_reason": item.get("bridge_family_id", item["edge_id"]),
                "weight": DIRECT_BRIDGE_WEIGHTS.get(item["edge_id"], 0.9),
                "witness_basis": item.get("witness_basis", []),
                "note": item.get("note", "Direct bridge family carried into Phase 4 Pt 2."),
            }
        )
    payloads = {
        "metro_system_registry": wrap("systems", systems, LEDGER_INTERLOCK_MD_PATH, docs_gate, {"canonical_scope": "live 19-body organism + 16-kernel inner compiler", "active_basis": [str(ROOT_BASIS_PATH), str(ADDRESSING_PATH), str(HIGHER_DIMENSIONAL_PATH), str(DEEPER_SWARM_PATH), str(GRAND_CENTRAL_OVERVIEW_PATH), str(AFFECTIVE_FIELD_PATH), str(PHASE4_STRUCTURED_PATH), str(KNOWLEDGE_FABRIC_PATH), str(VIRTUAL_SWARM_SPEC_PATH), str(HD_SCT_PATH), str(HYBRID_LENS_PATH)], "appendix_support": APPENDIX_SUPPORT_SET}),
        "metro_station_registry": wrap("stations", stations, LEDGER_INTERLOCK_MD_PATH, docs_gate),
        "metro_interlock_registry": wrap("interlocks", interlocks, LEDGER_INTERLOCK_MD_PATH, docs_gate),
        "holo_coordinate_registry": wrap("coordinates", coordinates, LEDGER_MAIN_MD_PATH, docs_gate),
        "carrier_registry": wrap("carriers", carriers, LEDGER_MAIN_MD_PATH, docs_gate),
        "rail_registry": wrap("rails", rails, LEDGER_MAIN_MD_PATH, docs_gate),
        "arc_rotation_registry": wrap("arcs", arcs, LEDGER_MAIN_MD_PATH, docs_gate),
        "carrier_transform_registry": wrap("transforms", transforms, LEDGER_MAIN_MD_PATH, docs_gate),
        "lens_registry": wrap("lenses", singletons, LEDGER_LENS_MD_PATH, docs_gate),
        "lens_hybrid_registry": wrap("lenses", hybrids, LEDGER_LENS_MD_PATH, docs_gate),
        "lens_weight_profile_registry": wrap("profiles", profiles, LEDGER_LENS_MD_PATH, docs_gate),
        "lens_state_registry": wrap("lens_states", lens_states, LEDGER_LENS_MD_PATH, docs_gate),
        "field_registry": wrap("fields", fields, LEDGER_FIELD_MD_PATH, docs_gate),
        "z_point_registry": wrap("zpoints", zpoints, LEDGER_FIELD_MD_PATH, docs_gate),
        "aether_point_registry": wrap("aether_points", aether_points, LEDGER_FIELD_MD_PATH, docs_gate),
        "projection_space_registry": wrap("spaces", spaces, LEDGER_PROJECTION_MD_PATH, docs_gate),
        "projection_assignment_registry": wrap("assignments", assignments, LEDGER_PROJECTION_MD_PATH, docs_gate),
        "shortcut_registry": wrap("shortcuts", shortcuts, SCHEMA_QUERY_MD_PATH, docs_gate),
        "query_registry": wrap("queries", queries, QUERY_PRESETS_MD_PATH, docs_gate),
        "system_crosswalk_edges": wrap("edges", edges, EDGE_MD_PATH, docs_gate),
    }
    dashboard = {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "docs_gate": docs_gate, "canonical_scope": "live 19-body organism + 16-kernel inner compiler", "metro_system_count": len(systems), "station_count": len(stations), "interlock_count": len(interlocks), "coordinate_count": len(coordinates), "carrier_count": len(carriers), "rail_count": len(rails), "lens_count": len(hybrids), "lens_state_count": len(lens_states), "field_count": len(fields), "zpoint_count": len(zpoints), "aether_point_count": len(aether_points), "projection_space_count": len(spaces), "projection_assignment_count": len(assignments), "shortcut_count": len(shortcuts), "query_count": len(queries), "edge_count": len(edges), "dense_kernel_overlay": {"mode": "kernel_overlay", "shell_registry": str(DENSE_65_SHELL_REGISTRY_PATH), "sigma_path": list(DENSE_65_SIGMA_PATH), "rotation_authority": DENSE_65_AUTHORITY_REFS["rotation_authority"], "antispin_authority": DENSE_65_AUTHORITY_REFS["antispin_authority"]}, "validation": {"all_systems_have_interlocks": len({*[_["source_system"] for _ in interlocks], *[_["target_system"] for _ in interlocks]}) == len(systems), "coordinates_cover_active_records": len({item["record_id"] for item in coordinates}) == len(coordinates), "rails_are_su_me_sa": {item["rail_id"] for item in rails} == {"Su", "Me", "Sa"}, "all_15_lenses_materialized": len({item["lens_id"] for item in hybrids}) == 15, "docs_gate_preserved_blocked": docs_gate == "BLOCKED"}, "top_interlocks": [{"interlock_id": item["interlock_id"], "source_system": item["source_system"], "target_system": item["target_system"], "dispatch_score": item["dispatch_score"]} for item in sorted(interlocks, key=lambda row: (-row["dispatch_score"], row["interlock_id"]))[:10]], "top_lens_states": [{"record_id": item["record_id"], "record_type": item["record_type"], "dominant_lens_system": item["dominant_lens_system"], "score": item["lens_weight_vector"][item["dominant_lens_system"]]} for item in sorted(lens_states, key=lambda row: (-row["lens_weight_vector"][row["dominant_lens_system"]], row["record_id"]))[:10]], "top_aether_points": [{"point_id": item["point_id"], "source_record_id": item["source_record_id"], "aether_density": item["aether_density"], "geodesic_mode": item["geodesic_mode"]} for item in sorted(aether_points, key=lambda row: (-row["aether_density"], row["point_id"]))[:10]], "next_frontier": ["propagate lens and field weights into writeback-facing runtime receipts", "bind more pair and wave cells to explicit HD-SCT operator witnesses", "extend Phase 4 automation to emit interlock-aware neglected-area repairs", "keep Trading Bot and other evidence reservoirs visible without letting them outrank live authority while the Docs gate is blocked"], "phase4_dependency_counts": {"body_count": phase4_dashboard.get("body_count", 0), "pair_count": phase4_dashboard.get("pair_count", 0), "wave_count": phase4_dashboard.get("wave_count", 0), "knowledge_fabric_records": knowledge_dashboard.get("total_records", 0)}}
    payloads["dashboard"] = dashboard
    payloads["registry_manifest"] = {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "docs_gate": docs_gate, "registries": {key: str(path) for key, path in JSON_OUTPUTS.items()}, "counts": {"metro_systems": len(systems), "stations": len(stations), "interlocks": len(interlocks), "coordinates": len(coordinates), "lens_states": len(lens_states), "aether_points": len(aether_points), "projection_assignments": len(assignments), "edges": len(edges)}}
    runtime = {key: payloads[key] for key in payloads if key != "registry_manifest"}
    sample_queries = {"locate_top": locate("Grand Central", runtime, limit=1)["results"][0]["label"], "interlock_top": interlock("GCZ", runtime, limit=1)["results"][0]["interlock_id"], "lens_top": lens("SFCR", runtime, limit=1)["profiles"][0]["lens_id"], "field_top": query_field("Aether", runtime, limit=1)["fields"][0]["field_id"], "project_top": project("Field3D", runtime, limit=1)["spaces"][0]["space_id"], "route_outcome": route("CoreMetro", "HDSCTMetro", runtime)["outcome"], "fire_top": fire("cloud field repair", runtime, limit=1)["results"][0]["record_id"], "promote_outcome": promote("IX-16", runtime)["outcome"]}
    for key, path in JSON_OUTPUTS.items():
        write_json(path, payloads[key])
        write_json(REGISTRY_ROOT / path.name, payloads[key])
    write_text(OVERVIEW_MD_PATH, "# PHASE 4 PT 2 INTER-METRO LENS-WEIGHT SUPERSTRUCTURE\n\n" + f"Last compiled: `{dashboard['generated_at']}`\n\n```\n{PT2_EQUATION}\n```\n\n- Docs gate: `{docs_gate}`\n- Canonical scope: live `19`-body organism plus `16`-kernel inner compiler\n- Historical drift: resolved by keeping `14_DEEPER...` as the only live deep root\n- Appendix support: `" + "`, `".join(APPENDIX_SUPPORT_SET) + "`\n\n" + markdown_table(["Registry", "Count"], [["Metro systems", dashboard["metro_system_count"]], ["Stations", dashboard["station_count"]], ["Interlocks", dashboard["interlock_count"]], ["Coordinates", dashboard["coordinate_count"]], ["Lens systems", dashboard["lens_count"]], ["Lens states", dashboard["lens_state_count"]], ["Field objects", dashboard["field_count"]], ["Aether points", dashboard["aether_point_count"]]]))
    write_text(SCHEMA_PRIMARY_MD_PATH, "# PHASE 4 PT 2 INTER-METRO LENS-WEIGHT SCHEMA\n\n- `70_SCHEMAS`: contracts only\n- `90_LEDGERS`: canonical registries and scores\n- `95_MANIFESTS`: active query entrypoints and presets\n- `85_EDGES`: explicit inter-system crosswalks\n- `20_METRO`: human projections only\n\n```\nH = (Addr4, Face6, Arc7, Rail3, Depth5, Lens15, System, Truth, Surface)\n```")
    write_text(SCHEMA_QUERY_MD_PATH, "# PHASE 4 PT 2 QUERY AND FIELD SCHEMA\n\n```\nbody -> system -> coordinate -> lens -> pair -> wave -> field -> interlock -> writeback\n```\n\n```\n(aether_density, zero_proximity, tunnel_cost, rail_hardness, resonance_pressure, repair_gain)\n```\n\n" + markdown_table(["Mode", "Scope", "Stop Rule"], [[item["mode"], item["scope"], item["stop_rule"]] for item in queries]))
    write_text(LEDGER_MAIN_MD_PATH, "# PHASE 4 PT 2 INTER-METRO LENS-WEIGHT LEDGER\n\n" + markdown_table(["Check", "Pass"], [[key, "yes" if value else "no"] for key, value in dashboard["validation"].items()]))
    write_text(LEDGER_INTERLOCK_MD_PATH, "# PHASE 4 PT 2 METRO INTERLOCK LEDGER\n\n" + markdown_table(["Interlock", "Transform", "Route Via", "Score", "Proof"], [[item["interlock_id"], item["transform_kind"], " -> ".join(item["route_via"]), item["dispatch_score"], item["proof_state"]] for item in interlocks]))
    write_text(LEDGER_LENS_MD_PATH, "# PHASE 4 PT 2 LENS WEIGHT PROFILE LEDGER\n\n" + markdown_table(["Lens", "Role", "Carriers", "Rails", "Stop"], [[item["lens_id"], lens_role(item["lens_id"]), ", ".join(item["preferred_carriers"][:3]), ", ".join(item["preferred_rails"]), item["stop_condition"]] for item in profiles]))
    write_text(LEDGER_FIELD_MD_PATH, "# PHASE 4 PT 2 FIELD AND AETHER LEDGER\n\n" + markdown_table(["Field", "Role", "Bindings"], [[item["field_id"], item["role"], ", ".join(item["carrier_binding"])] for item in fields]) + "\n\n" + markdown_table(["Z", "Route", "Token", "Proof"], [[item["zpoint_id"], item["route_class"], item["restart_token"], item["proof_state"]] for item in zpoints]) + "\n\n## Dense Kernel Overlay\n\n- Dense shell: `" + str(DENSE_65_SHELL_REGISTRY_PATH) + "`\n- Transfer chain: `" + " -> ".join(DENSE_65_SIGMA_PATH) + "`\n- Rotation authority: `" + DENSE_65_AUTHORITY_REFS["rotation_authority"] + "`\n- Antispin authority: `" + DENSE_65_AUTHORITY_REFS["antispin_authority"] + "`\n- LP57 coordinate standard: `" + str(LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH) + "`\n- LP57 seed inversion standard: `" + str(LP57OMEGA_SEED_INVERSION_STANDARD_PATH) + "`")
    write_text(LEDGER_PROJECTION_MD_PATH, "# PHASE 4 PT 2 PROJECTION SPACE LEDGER\n\n" + markdown_table(["Space", "Axes", "Carriers"], [[item["space_id"], ", ".join(item["axes"]), ", ".join(item["carrier_focus"])] for item in spaces]))
    write_text(POINTERS_MD_PATH, "# PHASE 4 PT 2 METRO SYSTEM POINTERS\n\n" + markdown_table(["System", "Label", "Authority"], [[item["system_id"], item["label"], item["authority_surface"]] for item in systems] + [["DenseKernel65", "Dense 65 Kernel Overlay", str(DENSE_65_SHELL_REGISTRY_PATH)]]) + "\n\n## Dense Kernel Transit Law\n\n- Sigma path: `" + " -> ".join(DENSE_65_SIGMA_PATH) + "`\n- Order-4 rotation authority: `" + DENSE_65_AUTHORITY_REFS["rotation_authority"] + "`\n- Order-3 antispin authority: `" + DENSE_65_AUTHORITY_REFS["antispin_authority"] + "`")
    write_text(QUERY_PRESETS_MD_PATH, "# PHASE 4 PT 2 QUERY PRESETS\n\n" + markdown_table(["Mode", "Shortcuts", "Stop"], [[item["mode"], ", ".join(item["active_shortcuts"]), item["stop_rule"]] for item in queries]))
    write_text(DASHBOARD_MD_PATH, "# PHASE 4 PT 2 DASHBOARD\n\n- Dense kernel overlay: `DenseKernel65`\n- Transfer chain: `" + " -> ".join(DENSE_65_SIGMA_PATH) + "`\n- Rotation / antispin: `" + DENSE_65_AUTHORITY_REFS["rotation_authority"] + " / " + DENSE_65_AUTHORITY_REFS["antispin_authority"] + "`\n\n" + markdown_table(["Interlock", "Source", "Target", "Score"], [[item["interlock_id"], item["source_system"], item["target_system"], item["dispatch_score"]] for item in dashboard["top_interlocks"]]))
    write_text(EDGE_MD_PATH, "# PHASE 4 PT 2 SYSTEM CROSSWALK EDGES\n\n" + markdown_table(["Edge", "Kind", "Source", "Target", "Weight"], [[item["edge_id"], item["edge_kind"], item["source_id"], item["target_id"], item["weight"]] for item in edges]))
    write_text(RUNTIME_MD_PATH, f"# phase4_pt2_inter_metro_lens_weight_runtime\n\n- generated_at: `{dashboard['generated_at']}`\n- docs_gate: `{docs_gate}`\n- interlocks: `{dashboard['interlock_count']}`\n- coordinates: `{dashboard['coordinate_count']}`\n- lens_states: `{dashboard['lens_state_count']}`\n- aether_points: `{dashboard['aether_point_count']}`\n")
    write_text(RECEIPT_MD_PATH, "# 2026-03-12 phase4_pt2_inter_metro_lens_weight_superstructure\n\n" + f"- `locate('Grand Central')`: `{sample_queries['locate_top']}`\n- `interlock('GCZ')`: `{sample_queries['interlock_top']}`\n- `lens('SFCR')`: `{sample_queries['lens_top']}`\n- `field('Aether')`: `{sample_queries['field_top']}`\n- `project('Field3D')`: `{sample_queries['project_top']}`\n- `route(CoreMetro -> HDSCTMetro)`: `{sample_queries['route_outcome']}`\n- `fire('cloud field repair')`: `{sample_queries['fire_top']}`\n- `promote('IX-16')`: `{sample_queries['promote_outcome']}`\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
