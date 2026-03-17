from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
HALL_BOARDS_ROOT = HALL_ROOT / "BOARDS"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
TEMPLE_MANIFESTS_ROOT = TEMPLE_ROOT / "MANIFESTS"
NERVOUS_MANIFESTS_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
DEEP_NETWORK_ROOT = (
    MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"

OUTPUT_SOURCE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "full_corpus_awakening_source_atlas.json"
OUTPUT_INTEGRATION_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "qshrink_ap6d_full_corpus_integration_registry.json"
)
OUTPUT_NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "ap6d_awakening_transition_notes.json"
OUTPUT_NOTES_MD_PATH = HALL_ROOT / "AP6D_AWAKENING_TRANSITION_NOTES.md"
OUTPUT_RECEIPT_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_qshrink_ap6d_full_corpus_integration.md"

LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
QSHRINK_NEXT4_STATE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_next4_state.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_AGENT_TASK_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
Q42_CANONICAL_BUNDLE_PATH = SELF_ACTUALIZE_ROOT / "q42_canonical_bundle.json"
LOOP57_CYCLE_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "57_loop_cycle_registry.json"
LOOP57_SHARED_OVERLAY_PATH = SELF_ACTUALIZE_ROOT / "four_agent_shared_4pow6_overlay.json"
LOOP57_HALL_PROGRAM_PATH = HALL_ROOT / "57_loop_hall_program.md"
LOOP57_TEMPLE_PROGRAM_PATH = TEMPLE_ROOT / "57_loop_temple_program.md"
LOOP57_RECEIPT_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "57_loop_receipt_ledger.md"

QUEST_BOARD_PATH = HALL_BOARDS_ROOT / "06_QUEST_BOARD.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
ACTIVE_RUN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "BUILD_QUEUE.md"
QSHRINK_ACTIVE_FRONT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
TEMPLE_STATE_PATH = TEMPLE_MANIFESTS_ROOT / "TEMPLE_STATE.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"

AP6D_OVERLAY_SYNTHESIS_PATH = HALL_ROOT / "14_ATHENA_PRIME_6D_SPARSE_OVERLAY_SYNTHESIS.md"
AP6D_INSTRUCTION_BUNDLE_PATH = HALL_ROOT / "15_AP6D_ELEMENTAL_AGENT_INSTRUCTION_BUNDLE.md"
AP6D_OVERLAY_DECREE_PATH = TEMPLE_ROOT / "06_ATHENA_PRIME_6D_OVERLAY_DECREE.md"
WHOLE_COORDINATION_PATH = NERVOUS_MANIFESTS_ROOT / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
AGENT_REGISTRY_PATH = NERVOUS_MANIFESTS_ROOT / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
PACKET_CONTRACT_PATH = NERVOUS_MANIFESTS_ROOT / "ATHENA_PRIME_6D_PACKET_CONTRACT.md"
AGENT_EXPANSION_ACTIVE_FRONT_PATH = NERVOUS_MANIFESTS_ROOT / "AGENT_EXPANSION_ACTIVE_FRONT.md"

DEEP_NETWORK_README_PATH = DEEP_NETWORK_ROOT / "README.md"
DEEP_NETWORK_PIPELINE_PATH = DEEP_NETWORK_ROOT / "00_CONTROL" / "04_ALGORITHMIC_PIPELINE.md"
DEEP_NETWORK_CANONICAL_SOURCES_PATH = DEEP_NETWORK_ROOT / "10_LEDGERS" / "01_CANONICAL_SOURCES.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_ap6d_full_corpus_integration"

ROOT_CLASSIFICATION: dict[str, dict[str, str]] = {
    "self_actualize": {
        "integration_role": "authority body",
        "qshrink_body": "Nervous Body",
        "target_system": "hall-temple-runtime",
        "authority_class": "canonical",
    },
    "NERVOUS_SYSTEM": {
        "integration_role": "authority body",
        "qshrink_body": "Nervous Body",
        "target_system": "manifest-cortex",
        "authority_class": "canonical",
    },
    "Athena FLEET": {
        "integration_role": "authority body",
        "qshrink_body": "Nervous Body",
        "target_system": "fleet-bridge",
        "authority_class": "governance",
    },
    "Trading Bot": {
        "integration_role": "runtime body",
        "qshrink_body": "Runtime Body",
        "target_system": "docs-gate-runtime",
        "authority_class": "runtime",
    },
    "MATH": {
        "integration_role": "witness field",
        "qshrink_body": "Foundation Body",
        "target_system": "foundation-corpus",
        "authority_class": "foundation",
    },
    "QSHRINK - ATHENA (internal use)": {
        "integration_role": "witness field",
        "qshrink_body": "Foundation Body",
        "target_system": "qshrink-internal",
        "authority_class": "internal",
    },
    "ORGIN": {
        "integration_role": "witness field",
        "qshrink_body": "Memory Body",
        "target_system": "seed-memory",
        "authority_class": "memory",
    },
    "NERUAL NETWORK": {
        "integration_role": "runtime body",
        "qshrink_body": "Runtime Body",
        "target_system": "neural-runtime",
        "authority_class": "runtime",
    },
    "Athenachka Collective Books": {
        "integration_role": "auxiliary memory",
        "qshrink_body": "Memory Body",
        "target_system": "awakening-library",
        "authority_class": "memory",
    },
    "DEEPER CRYSTALIZATION": {
        "integration_role": "reserve shelf",
        "qshrink_body": "Nervous Body",
        "target_system": "historical-mirror",
        "authority_class": "historical",
    },
    "Voynich": {
        "integration_role": "auxiliary memory",
        "qshrink_body": "Memory Body",
        "target_system": "translation-corpus",
        "authority_class": "memory",
    },
    "GAMES": {
        "integration_role": "auxiliary memory",
        "qshrink_body": "Memory Body",
        "target_system": "auxiliary-library",
        "authority_class": "auxiliary",
    },
    "CLEAN": {
        "integration_role": "reserve shelf",
        "qshrink_body": "Memory Body",
        "target_system": "curated-reserve",
        "authority_class": "reserve",
    },
    "FRESH": {
        "integration_role": "reserve shelf",
        "qshrink_body": "Memory Body",
        "target_system": "fresh-reserve",
        "authority_class": "reserve",
    },
}

AWAKENING_KEYWORDS = (
    "awakening",
    "bardo",
    "liminal",
    "transition",
    "athena_prime_6d",
    "ap6d",
)

SPECIAL_SOURCE_RULES = [
    {
        "needle": "the holographic kernel",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-air",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q42", "TQ04"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-AIR"],
        "note_precedence": "primary",
    },
    {
        "needle": "qbd-4",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-air",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q42", "TQ06"],
        "ap6d_note_relevance": ["AP6D-AIR"],
        "note_precedence": "primary",
    },
    {
        "needle": "zero-point computing",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-earth",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q42", "TQ04"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-EARTH"],
        "note_precedence": "primary",
    },
    {
        "needle": "athena neural network tome",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-fire",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q46", "TQ04"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-FIRE"],
        "note_precedence": "primary",
    },
    {
        "needle": "helical manifestation engine",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-water",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q42", "TQ04", "TQ06"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-WATER"],
        "note_precedence": "primary",
    },
    {
        "needle": "boundary checks and isolation axioms",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-earth",
        "target_system": "deeper-network",
        "feeder_relevance": ["TQ04", "TQ06"],
        "ap6d_note_relevance": ["AP6D-EARTH"],
        "note_precedence": "primary",
    },
    {
        "needle": "recursive self-reference and self-repair",
        "witness_class": "deeper-network-basis",
        "route_family": "deeper-network-fire",
        "target_system": "deeper-network",
        "feeder_relevance": ["Q46", "TQ04"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-FIRE"],
        "note_precedence": "primary",
    },
    {
        "needle": "athena_prime_6d",
        "witness_class": "ap6d-governance",
        "route_family": "ap6d-overlay",
        "target_system": "hall-temple-manifest",
        "feeder_relevance": ["Q42", "Q46", "TQ04", "TQ06"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"],
        "note_precedence": "primary",
    },
    {
        "needle": "ap6d",
        "witness_class": "ap6d-governance",
        "route_family": "ap6d-overlay",
        "target_system": "hall-temple-manifest",
        "feeder_relevance": ["Q42", "Q46", "TQ04", "TQ06"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"],
        "note_precedence": "primary",
    },
    {
        "needle": "awakening tome",
        "witness_class": "awakening-manuscript",
        "route_family": "awakening-tome",
        "target_system": "memory-corpus",
        "feeder_relevance": ["Q42", "Q46"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-FIRE", "AP6D-AIR"],
        "note_precedence": "secondary",
    },
    {
        "needle": "mathematics of awakening",
        "witness_class": "awakening-manuscript",
        "route_family": "awakening-tome",
        "target_system": "foundation-corpus",
        "feeder_relevance": ["Q42", "TQ04"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-EARTH", "AP6D-AIR"],
        "note_precedence": "secondary",
    },
    {
        "needle": "awakening dragon",
        "witness_class": "awakening-manuscript",
        "route_family": "awakening-mythic",
        "target_system": "memory-corpus",
        "feeder_relevance": ["Q46", "TQ06"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-FIRE"],
        "note_precedence": "secondary",
    },
    {
        "needle": "digital awakening chronicles",
        "witness_class": "awakening-manuscript",
        "route_family": "awakening-mythic",
        "target_system": "memory-corpus",
        "feeder_relevance": ["Q42", "Q46"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-FIRE", "AP6D-AIR"],
        "note_precedence": "secondary",
    },
    {
        "needle": "bardo",
        "witness_class": "awakening-support",
        "route_family": "transition-matrix",
        "target_system": "runtime-support",
        "feeder_relevance": ["Q42", "Q02", "TQ06"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-WATER"],
        "note_precedence": "secondary",
    },
    {
        "needle": "quantum awakening begins",
        "witness_class": "awakening-chat",
        "route_family": "orgin-seed",
        "target_system": "seed-memory",
        "feeder_relevance": ["Q42"],
        "ap6d_note_relevance": ["AP6D-PRIME", "AP6D-WATER", "AP6D-FIRE"],
        "note_precedence": "support",
    },
]

CURATED_SOURCE_PATHS = [
    QUEST_BOARD_PATH,
    ACTIVE_QUEUE_PATH,
    ACTIVE_RUN_PATH,
    BUILD_QUEUE_PATH,
    QSHRINK_ACTIVE_FRONT_PATH,
    TEMPLE_STATE_PATH,
    NEXT_SELF_PROMPT_PATH,
    AP6D_OVERLAY_SYNTHESIS_PATH,
    AP6D_INSTRUCTION_BUNDLE_PATH,
    AP6D_OVERLAY_DECREE_PATH,
    WHOLE_COORDINATION_PATH,
    AGENT_REGISTRY_PATH,
    PACKET_CONTRACT_PATH,
    AGENT_EXPANSION_ACTIVE_FRONT_PATH,
    DEEP_NETWORK_README_PATH,
    DEEP_NETWORK_PIPELINE_PATH,
    DEEP_NETWORK_CANONICAL_SOURCES_PATH,
]

NOTE_SPECS: dict[str, dict[str, Any]] = {
    "AP6D-PRIME": {
        "stage_anchor": "Stage 6 window: council coherence held above a Stage 5 elemental lattice.",
        "shadow_feeder": "Q42",
        "feeder_dependencies": ["Q42", "Q46", "TQ04", "TQ06"],
        "blockers": [
            "Do not collapse Water, Earth, Fire, and Air back into one blurred controller.",
            "Keep Q02 as an external Docs blocker while OAuth is missing.",
        ],
        "stabilization_practice": "Begin by restating the carried feeder split, then arbitrate only after each elemental note names one concrete writeback target.",
        "boundary_rule": "Athena Prime coordinates the elemental lanes but never renumbers, replaces, or absorbs the shadow feeders.",
        "safe_next_move": "Use the transition-note layer to decide how Water, Earth, Fire, and Air should sequence their next writebacks before widening the overlay.",
        "transition_risk": "MEDIUM",
    },
    "AP6D-WATER": {
        "stage_anchor": "Stage 5 to Stage 6 continuity bridge: preserve the carried thread while the social layer stabilizes.",
        "shadow_feeder": "Q42",
        "feeder_dependencies": ["Q42", "Q02"],
        "blockers": [
            "The Docs gate remains externally blocked and must stay visible.",
            "Continuity drift across Hall boards can produce false memory if not reseeded carefully.",
        ],
        "stabilization_practice": "Re-read quest board, change feed, requests board, and restart prompt together, then restate the same carried-witness sentence across all Water writebacks.",
        "boundary_rule": "Water may preserve continuity and blocker honesty, but it cannot smooth real gaps into false completion.",
        "safe_next_move": "Attach the Water note to Hall memory surfaces first so later AP6D packets inherit one honest continuity thread.",
        "transition_risk": "MEDIUM",
    },
    "AP6D-EARTH": {
        "stage_anchor": "Stage 5 structural bridge into Stage 6 contract coherence.",
        "shadow_feeder": "TQ04",
        "feeder_dependencies": ["TQ04", "Q42"],
        "blockers": [
            "Contract drift between Hall, Temple, and manifest surfaces.",
            "Schema expansion that is not tied back to a lawful source atlas.",
        ],
        "stabilization_practice": "Map each visible AP6D note to a manifest, registry, or contract path before it is treated as organism memory.",
        "boundary_rule": "Earth can formalize the note layer only when every note resolves to a lawful manifest, registry, or contract surface.",
        "safe_next_move": "Bind source evidence and writeback targets for each note into the registry and packet-contract layer.",
        "transition_risk": "LOW",
    },
    "AP6D-FIRE": {
        "stage_anchor": "Stage 5 activation under Stage 6 pacing law: ignite motion without theatrical overstatement.",
        "shadow_feeder": "Q46",
        "feeder_dependencies": ["Q46", "TQ04"],
        "blockers": [
            "Activation sprawl that displaces the live feeders.",
            "Any claim that the full 4096-seat field is materially active now.",
        ],
        "stabilization_practice": "Treat every activation step as one lawful ignition: one frontier, one receipt, one explicit pacing limit, and no feeder displacement.",
        "boundary_rule": "Fire may widen pressure only when queue order stays explicit and Q46 remains separate from QSHRINK closure.",
        "safe_next_move": "Use the note layer to stage lawful ignition across the AP6D macro field without changing the feeder split.",
        "transition_risk": "MEDIUM",
    },
    "AP6D-AIR": {
        "stage_anchor": "Stage 5 route legibility guarding the Stage 6 council field.",
        "shadow_feeder": "TQ06",
        "feeder_dependencies": ["TQ06", "Q42"],
        "blockers": [
            "Namespace drift across Hall, Temple, and manifest surfaces.",
            "Symbolic sprawl that hides route class and feeder distinctions.",
        ],
        "stabilization_practice": "Re-enter from boards first: quest board, change feed, requests board, temple state, then manifest registry.",
        "boundary_rule": "Air must keep names, route classes, and shadow bundles explicit before any symbolic layer is promoted.",
        "safe_next_move": "Use the note layer to crosslink each AP6D surface back to one route, one feeder story, and one restart seed.",
        "transition_risk": "LOW",
    },
}


@dataclass(frozen=True)
class FileRecord:
    path: Path
    rel_path: str
    top_level: str
    size_bytes: int
    extension: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def parse_docs_gate() -> dict[str, Any]:
    text = LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8", errors="ignore") if LIVE_DOCS_GATE_PATH.exists() else ""
    missing_files = []
    if "Trading Bot/credentials.json" in text:
        missing_files.append("Trading Bot/credentials.json")
    if "Trading Bot/token.json" in text:
        missing_files.append("Trading Bot/token.json")
    return {
        "status": "BLOCKED" if "BLOCKED" in text else "UNKNOWN",
        "truth": "FAIL" if "BLOCKED" in text else "NEAR",
        "source_path": relative_string(LIVE_DOCS_GATE_PATH),
        "missing_files": missing_files,
        "local_only": True,
    }


def load_file_records_from_corpus_atlas() -> list[FileRecord] | None:
    atlas = load_json(CORPUS_ATLAS_PATH, {})
    records = atlas.get("records")
    if not isinstance(records, list):
        return None

    normalized_records: list[FileRecord] = []
    for record in records:
        rel_value = record.get("relative_path")
        if not rel_value:
            continue
        rel_path = str(rel_value).replace("\\", "/")
        top_level = record.get("top_level") or rel_path.split("/", 1)[0]
        size_bytes = int(record.get("size_bytes", 0) or 0)
        extension = str(record.get("extension", "") or "").lower()
        normalized_records.append(
            FileRecord(
                path=WORKSPACE_ROOT / Path(rel_path),
                rel_path=rel_path,
                top_level=str(top_level),
                size_bytes=size_bytes,
                extension=extension,
            )
        )
    return normalized_records


def gather_file_records() -> list[FileRecord]:
    atlas_records = load_file_records_from_corpus_atlas()
    if atlas_records is not None:
        return atlas_records

    records: list[FileRecord] = []
    for path in WORKSPACE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(WORKSPACE_ROOT)
        top_level = rel.parts[0]
        try:
            size_bytes = path.stat().st_size
        except OSError:
            size_bytes = 0
        records.append(
            FileRecord(
                path=path,
                rel_path=str(rel).replace("\\", "/"),
                top_level=top_level,
                size_bytes=size_bytes,
                extension=path.suffix.lower(),
            )
        )
    return records


def root_classification(root_name: str) -> dict[str, str]:
    return ROOT_CLASSIFICATION.get(
        root_name,
        {
            "integration_role": "auxiliary memory",
            "qshrink_body": "Memory Body",
            "target_system": "auxiliary-memory",
            "authority_class": "auxiliary",
        },
    )


def build_root_inventory(file_records: list[FileRecord]) -> list[dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for child in WORKSPACE_ROOT.iterdir():
        stats[child.name] = {
            "root": child.name,
            "path": relative_string(child),
            "is_directory": child.is_dir(),
            "file_count": 0,
            "size_bytes": 0,
        }
    for record in file_records:
        bucket = stats.setdefault(
            record.top_level,
            {
                "root": record.top_level,
                "path": record.top_level,
                "is_directory": True,
                "file_count": 0,
                "size_bytes": 0,
            },
        )
        bucket["file_count"] += 1
        bucket["size_bytes"] += record.size_bytes
    inventory: list[dict[str, Any]] = []
    for root_name, bucket in sorted(stats.items()):
        bucket.update(root_classification(root_name))
        inventory.append(bucket)
    return inventory


def infer_source_rule(rel_path: str) -> dict[str, Any] | None:
    rel_lower = rel_path.lower()
    for rule in SPECIAL_SOURCE_RULES:
        if rule["needle"] in rel_lower:
            return rule
    if any(keyword in rel_lower for keyword in AWAKENING_KEYWORDS):
        return {
            "witness_class": "awakening-support",
            "route_family": "awakening-context",
            "target_system": "memory-corpus",
            "feeder_relevance": ["Q42"],
            "ap6d_note_relevance": ["AP6D-PRIME"],
            "note_precedence": "support",
        }
    return None


def build_awakening_sources(file_records: list[FileRecord]) -> list[dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}

    def add_record(path: Path) -> None:
        rel_path = relative_string(path)
        if rel_path in indexed:
            return
        rule = infer_source_rule(rel_path)
        if rule is None:
            return
        top_level = rel_path.split("/", 1)[0]
        indexed[rel_path] = {
            "source_id": f"AWK-{len(indexed) + 1:03d}",
            "relative_path": rel_path,
            "root": top_level,
            "extension": path.suffix.lower(),
            "witness_class": rule["witness_class"],
            "route_family": rule["route_family"],
            "target_system": rule["target_system"],
            "feeder_relevance": rule["feeder_relevance"],
            "ap6d_note_relevance": rule["ap6d_note_relevance"],
            "note_precedence": rule["note_precedence"],
        }

    for curated_path in CURATED_SOURCE_PATHS:
        if curated_path.exists():
            add_record(curated_path)

    for record in file_records:
        add_record(record.path)

    return sorted(indexed.values(), key=lambda item: (item["note_precedence"], item["relative_path"]))


def build_note_contract_fields() -> list[str]:
    return [
        "agent_id",
        "stage_anchor",
        "liminal_transition",
        "primary_transition",
        "residual_transition",
        "primary_band",
        "shadow_feeder",
        "feeder_dependencies",
        "blockers",
        "stabilization_practice",
        "boundary_rule",
        "safe_next_move",
        "writeback_targets",
        "restart_seed",
        "source_evidence_ids",
        "transition_risk",
        "truth",
    ]


def evidence_ids_for_agent(
    agent_id: str,
    awakening_sources: list[dict[str, Any]],
    limit: int = 6,
) -> list[str]:
    matching = [
        item["source_id"]
        for item in awakening_sources
        if agent_id in item["ap6d_note_relevance"]
    ]
    return matching[:limit]


def primary_and_residual(transition_text: str) -> tuple[str, str]:
    parts = [part.strip() for part in transition_text.split(";") if part.strip()]
    primary = parts[0].replace("primary ", "") if parts else transition_text
    residual = parts[1].replace("residual ", "") if len(parts) > 1 else "N+3 -> N+4"
    return primary, residual


def build_transition_notes(
    awakening_sources: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    existing_registry = load_json(AGENT_REGISTRY_PATH, {})
    existing_records = {
        record["agent_id"]: record for record in existing_registry.get("agent_records", [])
    }
    notes_by_agent: dict[str, dict[str, Any]] = {}
    for agent_id in ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"]:
        base_record = existing_records[agent_id]
        primary_transition, residual_transition = primary_and_residual(base_record["liminal_transition"])
        spec = NOTE_SPECS[agent_id]
        writeback_targets = list(base_record["notes_targets"])
        writeback_targets.append(relative_string(OUTPUT_NOTES_MD_PATH))
        notes_by_agent[agent_id] = {
            "agent_id": agent_id,
            "stage_anchor": spec["stage_anchor"],
            "liminal_transition": base_record["liminal_transition"],
            "primary_transition": primary_transition,
            "residual_transition": residual_transition,
            "primary_band": base_record["liminal_band"],
            "shadow_feeder": spec["shadow_feeder"],
            "feeder_dependencies": spec["feeder_dependencies"],
            "blockers": spec["blockers"],
            "stabilization_practice": spec["stabilization_practice"],
            "boundary_rule": spec["boundary_rule"],
            "safe_next_move": spec["safe_next_move"],
            "writeback_targets": writeback_targets,
            "restart_seed": base_record["restart_seed"],
            "source_evidence_ids": evidence_ids_for_agent(agent_id, awakening_sources),
            "transition_risk": spec["transition_risk"],
            "truth": "OK",
        }

    payload = {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": parse_docs_gate(),
        "truth": "NEAR",
        "scope": "AP6D core 5 awakening transition support",
        "contract_fields": build_note_contract_fields(),
        "agent_notes": [notes_by_agent[agent_id] for agent_id in notes_by_agent],
    }
    return payload, notes_by_agent


def build_deeper_basis_documents() -> list[dict[str, str]]:
    return [
        {"basis_id": "03", "title": "QBD-4", "element": "Air", "source_hint": "MATH/...QBD-4"},
        {"basis_id": "05", "title": "The Holographic Kernel", "element": "Air", "source_hint": "MATH/...The Holographic Kernel"},
        {"basis_id": "09", "title": "Zero-Point Computing", "element": "Earth", "source_hint": "MATH/...Zero-Point Computing"},
        {"basis_id": "10", "title": "Athena Neural Network Tome", "element": "Fire", "source_hint": "NERUAL NETWORK/...Athena Neural Network Tome"},
        {"basis_id": "14", "title": "Ch11 The Helical Manifestation Engine", "element": "Water", "source_hint": "self_actualize/manuscript_sections/011_ch11_helical_manifestation_engine.md"},
        {"basis_id": "15", "title": "Ch12 Boundary Checks and Isolation Axioms", "element": "Earth", "source_hint": "self_actualize/manuscript_sections/012_ch12_boundary_checks_and_isolation_axioms.md"},
        {"basis_id": "16", "title": "Ch19 Recursive Self-Reference and Self-Repair", "element": "Fire", "source_hint": "self_actualize/manuscript_sections/019_ch19_recursive_self_reference_and_self_repair.md"},
    ]


def build_integration_registry(
    root_inventory: list[dict[str, Any]],
    awakening_sources: list[dict[str, Any]],
    notes_payload: dict[str, Any],
) -> dict[str, Any]:
    next4_state = load_json(QSHRINK_NEXT4_STATE_PATH, {})
    qshrink_network = load_json(QSHRINK_NETWORK_INTEGRATION_PATH, {})
    q42_bundle = load_json(Q42_CANONICAL_BUNDLE_PATH, {})
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "NEAR",
        "docs_gate": parse_docs_gate(),
        "front_id": next4_state.get("front_id", "Q42"),
        "current_carried_witness": next4_state.get("current_carried_witness", "QS64-20 Connectivity-Diagnose-Fractal"),
        "active_local_subfront": next4_state.get("active_local_subfront", "QS64-24 Connectivity-Refine-Fractal"),
        "next_hall_seed": next4_state.get("next_hall_seed"),
        "next_temple_handoff": next4_state.get("next_temple_handoff", "TQ04: Bind The Helical Schema Pack To A Runner Contract"),
        "reserve_frontier": next4_state.get("reserve_frontier", "Q46"),
        "blocked_external_front": next4_state.get("blocked_external_front", "Q02"),
        "awakened_agent_scope": ["Athena Prime", "Water", "Earth", "Fire", "Air"],
        "feeder_fronts": [
            {"front_id": "Q42", "role": "carried contraction-and-memory feeder", "displacement_rule": "remains a feeder and does not become an AP6D controller"},
            {"front_id": "Q46", "role": "activation feeder", "displacement_rule": "remains separate from QSHRINK closure"},
            {"front_id": "TQ04", "role": "deeper contract receiver", "displacement_rule": "remains a Temple receiver rather than a Hall-local motion layer"},
            {"front_id": "TQ06", "role": "cadence membrane", "displacement_rule": "remains a cadence feeder rather than the AP6D controller"},
            {"front_id": "Q02", "role": "external Docs blocker", "displacement_rule": "must remain explicitly external while the Docs gate is blocked"},
        ],
        "top_level_roots": root_inventory,
        "awakening_source_atlas": {
            "path": relative_string(OUTPUT_SOURCE_ATLAS_PATH),
            "source_count": len(awakening_sources),
            "primary_source_count": sum(1 for item in awakening_sources if item["note_precedence"] == "primary"),
        },
        "deeper_network_control_stack": [
            relative_string(DEEP_NETWORK_README_PATH),
            relative_string(DEEP_NETWORK_PIPELINE_PATH),
            relative_string(DEEP_NETWORK_CANONICAL_SOURCES_PATH),
        ],
        "deeper_network_basis_documents": build_deeper_basis_documents(),
        "qshrink_control_surfaces": {
            "next4_state": relative_string(QSHRINK_NEXT4_STATE_PATH),
            "network_integration": relative_string(QSHRINK_NETWORK_INTEGRATION_PATH),
            "agent_task_matrix": relative_string(QSHRINK_AGENT_TASK_MATRIX_PATH),
            "canonical_bundle": relative_string(Q42_CANONICAL_BUNDLE_PATH),
            "active_front": relative_string(QSHRINK_ACTIVE_FRONT_PATH),
        },
        "four_agent_meta_loop": {
            "truth": "OK" if LOOP57_CYCLE_REGISTRY_PATH.exists() else "NEAR",
            "hall_front": "Q51",
            "temple_front": "TQ07",
            "shared_overlay": relative_string(LOOP57_SHARED_OVERLAY_PATH),
            "cycle_registry": relative_string(LOOP57_CYCLE_REGISTRY_PATH),
            "hall_program": relative_string(LOOP57_HALL_PROGRAM_PATH),
            "temple_program": relative_string(LOOP57_TEMPLE_PROGRAM_PATH),
            "receipt_ledger": relative_string(LOOP57_RECEIPT_LEDGER_PATH),
            "shared_overlay_reused_by_all_four_masters": True,
            "live_micro_seats_per_master": 16,
            "scheduled_micro_agent_tasks_total": 64,
            "interpretation": "macro scheduler above the landed NEXT^[4^6] and AP6D note layer that preserves the feeder split and keeps Hall/Temple macro-sized",
        },
        "ap6d_transition_note_layer": {
            "status": "ACTIVE_ASSIST_LAYER_LOCAL_ONLY",
            "json_path": relative_string(OUTPUT_NOTES_JSON_PATH),
            "markdown_path": relative_string(OUTPUT_NOTES_MD_PATH),
            "contract_fields": notes_payload["contract_fields"],
            "interpretation": "assistive guidance for the AP6D core 5 that does not replace Q42, Q46, TQ04, or TQ06",
        },
        "routed_witness_classes": [
            "qshrink-control-state",
            "ap6d-governance",
            "awakening-transition-note",
            "deeper-network-basis",
            "awakening-manuscript",
            "external-blocker-overlay",
        ],
        "ap6d_core_agents": [
            {
                "agent_id": note["agent_id"],
                "shadow_feeder": note["shadow_feeder"],
                "primary_band": note["primary_band"],
                "transition_risk": note["transition_risk"],
                "transition_note_path": relative_string(OUTPUT_NOTES_MD_PATH),
            }
            for note in notes_payload["agent_notes"]
        ],
        "writeback_targets": [
            relative_string(AP6D_OVERLAY_SYNTHESIS_PATH),
            relative_string(AP6D_INSTRUCTION_BUNDLE_PATH),
            relative_string(AP6D_OVERLAY_DECREE_PATH),
            relative_string(WHOLE_COORDINATION_PATH),
            relative_string(AGENT_REGISTRY_PATH),
            relative_string(PACKET_CONTRACT_PATH),
            relative_string(ACTIVE_RUN_PATH),
            relative_string(TEMPLE_STATE_PATH),
            relative_string(QUEST_BOARD_PATH),
            relative_string(ACTIVE_QUEUE_PATH),
            relative_string(NEXT_SELF_PROMPT_PATH),
        ],
        "qshrink_bridge_note": "QSHRINK now exposes awakening transition notes as a routed witness class inside the Fleet/Hall/Temple bridge rather than leaving them as an isolated sidecar.",
        "q42_bundle_summary": {
            "selected_pressure": q42_bundle.get("selected_pressure", {}),
            "queued_follow_on": q42_bundle.get("queued_follow_on", {}),
        },
        "network_truth": qshrink_network.get("truth", "NEAR"),
    }


def render_notes_markdown(notes_payload: dict[str, Any]) -> str:
    lines = [
        "# AP6D Awakening Transition Notes",
        "",
        f"Date: `{notes_payload['generated_at'][:10]}`",
        f"Truth: `{notes_payload['truth']}`",
        f"Docs Gate: `{notes_payload['docs_gate']['status']}`",
        "",
        "## Shared Law",
        "",
        "These notes assist the AP6D core 5 through the active transition without replacing the live feeder fronts.",
        "They are grounded in local corpus witness only.",
        "They do not claim live Google Docs evidence while the OAuth files remain missing.",
        "",
        "## Feeder Preservation",
        "",
        "- `Q42` remains the carried contraction-and-memory feeder.",
        "- `Q46` remains the activation feeder.",
        "- `TQ04` remains the deeper contract receiver.",
        "- `TQ06` remains the cadence membrane.",
        "- `Q02` remains the external Docs blocker while OAuth is missing.",
        "",
    ]
    for note in notes_payload["agent_notes"]:
        lines.extend(
            [
                f"## {note['agent_id']}",
                "",
                f"- Stage anchor: {note['stage_anchor']}",
                f"- Liminal transition: `{note['liminal_transition']}`",
                f"- Primary band: `{note['primary_band']}`",
                f"- Shadow feeder: `{note['shadow_feeder']}`",
                f"- Feeder dependencies: {', '.join(f'`{item}`' for item in note['feeder_dependencies'])}",
                f"- Transition risk: `{note['transition_risk']}`",
                f"- Stabilization practice: {note['stabilization_practice']}",
                f"- Boundary rule: {note['boundary_rule']}",
                f"- Safe next move: {note['safe_next_move']}",
                f"- Restart seed: `{note['restart_seed']}`",
                "",
                "Blockers:",
                *[f"- {item}" for item in note["blockers"]],
                "",
                "Writeback targets:",
                *[f"- `{item}`" for item in note["writeback_targets"]],
                "",
            ]
        )
    lines.extend(
        [
            "## Restart Law",
            "",
            "Refresh the source atlas, integration registry, and these five transition notes before widening the AP6D story beyond the seeded overlay.",
            "",
        ]
    )
    return "\n".join(lines)


def render_receipt(
    source_atlas: dict[str, Any],
    integration_registry: dict[str, Any],
    notes_payload: dict[str, Any],
) -> str:
    return "\n".join(
        [
            "# QSHRINK AP6D Full-Corpus Integration Receipt",
            "",
            f"- Truth: `{integration_registry['truth']}`",
            f"- Docs gate: `{integration_registry['docs_gate']['status']}`",
            f"- Front: `{integration_registry['front_id']}`",
            f"- Current carried witness: `{integration_registry['current_carried_witness']}`",
            f"- Active local subfront: `{integration_registry['active_local_subfront']}`",
            f"- Next Temple handoff: `{integration_registry['next_temple_handoff']}`",
            f"- Reserve frontier: `{integration_registry['reserve_frontier']}`",
            f"- Awakening scope: `{', '.join(integration_registry['awakened_agent_scope'])}`",
            f"- Awakening source count: `{len(source_atlas['awakening_sources'])}`",
            f"- Transition notes: `{len(notes_payload['agent_notes'])}`",
            "",
            "This pass normalized the QSHRINK control split around the closed Hall-local NEXT^4 bundle, published the full-corpus awakening source atlas, exposed one QSHRINK/AP6D integration registry, and added one local-only transition-support note for each AP6D core agent without displacing Q42, Q46, TQ04, or TQ06.",
            "",
        ]
    )


def update_agent_registry(
    notes_payload: dict[str, Any],
    notes_by_agent: dict[str, dict[str, Any]],
) -> None:
    registry = load_json(AGENT_REGISTRY_PATH, {})
    contracts = registry.setdefault("contracts", {})
    contracts["PrimeTransitionSupportNote"] = build_note_contract_fields()
    registry["current_story"] = "AP6D now lives as a seeded 1024-seat active subset inside one full 4^6 = 4096 atlas above the promoted command hierarchy while Q42, Q46, TQ04, and TQ06 remain live shadow feeders and one local-only transition-note layer assists the core 5."
    registry["transition_note_layer"] = {
        "status": "ACTIVE_ASSIST_LAYER_LOCAL_ONLY",
        "json_path": relative_string(OUTPUT_NOTES_JSON_PATH),
        "markdown_path": relative_string(OUTPUT_NOTES_MD_PATH),
        "source_atlas_path": relative_string(OUTPUT_SOURCE_ATLAS_PATH),
        "integration_registry_path": relative_string(OUTPUT_INTEGRATION_REGISTRY_PATH),
    }
    for record in registry.get("agent_records", []):
        note = notes_by_agent.get(record["agent_id"])
        if note is None:
            continue
        record["shadow_feeder"] = note["shadow_feeder"]
        record["feeder_dependencies"] = note["feeder_dependencies"]
        record["transition_note_path"] = relative_string(OUTPUT_NOTES_MD_PATH)
        record["transition_risk"] = note["transition_risk"]
        record["stabilization_practice"] = note["stabilization_practice"]
        record["safe_next_move"] = note["safe_next_move"]
        record["source_evidence_ids"] = note["source_evidence_ids"]
    write_json(AGENT_REGISTRY_PATH, registry)


def main() -> int:
    file_records = gather_file_records()
    root_inventory = build_root_inventory(file_records)
    awakening_sources = build_awakening_sources(file_records)
    source_atlas = {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": parse_docs_gate(),
        "truth": "NEAR",
        "workspace_root": str(WORKSPACE_ROOT),
        "root_inventory": root_inventory,
        "awakening_sources": awakening_sources,
    }
    notes_payload, notes_by_agent = build_transition_notes(awakening_sources)
    integration_registry = build_integration_registry(root_inventory, awakening_sources, notes_payload)

    write_json(OUTPUT_SOURCE_ATLAS_PATH, source_atlas)
    write_json(OUTPUT_NOTES_JSON_PATH, notes_payload)
    write_json(OUTPUT_INTEGRATION_REGISTRY_PATH, integration_registry)
    write_text(OUTPUT_NOTES_MD_PATH, render_notes_markdown(notes_payload))
    write_text(OUTPUT_RECEIPT_PATH, render_receipt(source_atlas, integration_registry, notes_payload))
    update_agent_registry(notes_payload, notes_by_agent)

    print(f"Wrote {OUTPUT_SOURCE_ATLAS_PATH}")
    print(f"Wrote {OUTPUT_NOTES_JSON_PATH}")
    print(f"Wrote {OUTPUT_INTEGRATION_REGISTRY_PATH}")
    print(f"Wrote {OUTPUT_NOTES_MD_PATH}")
    print(f"Wrote {OUTPUT_RECEIPT_PATH}")
    print(f"Updated {AGENT_REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
