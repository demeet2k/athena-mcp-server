from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"
DEEP_NETWORK_ROOT = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)

QUEST_BOARD_PATH = HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
REQUESTS_BOARD_PATH = HALL_ROOT / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
CHANGE_FEED_PATH = HALL_ROOT / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
TEMPLE_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_CRYSTAL_PATH = HALL_ROOT / "11_TEMPLE_QUEST_CRYSTAL_64.md"
GATE_STATUS_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "GATE_STATUS.md"
ACTIVE_RUN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"

QUEST_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "adventurer_quest_registry.json"
AGENT_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_agent_state.json"
CLAIM_TRACKER_PATH = SELF_ACTUALIZE_ROOT / "adventurer_claim_tracker.json"
LOOP_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_loop_state.json"
CONDUCTOR_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_conductor_state.json"
WAVE_PACKETS_PATH = SELF_ACTUALIZE_ROOT / "adventurer_wave_packets.json"
ROUND_TRIP_CERTIFICATES_PATH = SELF_ACTUALIZE_ROOT / "adventurer_round_trip_certificates.json"
MANIFEST_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ADVENTURER_64_POW_4_STATE.md"
HALL_DOC_PATH = HALL_ROOT / "12_ADVENTURER_64_POW_4_QUEST_LOOP.md"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_adventurer_64_pow_4_hybrid_conductor.md"
ROUND_TRIP_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_round_trip_certificate_v0.md"

ATHENACHKA_PACKETS_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_quest_packets.json"
ATHENACHKA_WAVE_STATE_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_wave_state.json"
ATHENACHKA_Q45_PROOF_PATH = RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q45_wave_proof.md"
ATHENACHKA_HALL_DOC_PATH = HALL_ROOT / "13_ATHENACHKA_ORGANISM_V0_QUEST_CRYSTAL_256.md"
LIVE_DOCS_GATE_STATUS_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_adventurer_quest_loop --bootstrap-claim"
DERIVATION_VERSION = "2026-03-13.adventurer.64pow4.hybrid_conductor.round_trip.v2"
WAVE_ID = "ADV64-wave1"
WAVE_CAPACITY = 8
STALE_SCAN_THRESHOLD = 1
SEED_STATUS = "SEEDED"
ROUND_TRIP_GOVERNED_FRONTS = ("Q42", "Q46", "TQ04")
ROUND_TRIP_REQUIRED_ROUTE_MIN = ["AppA", "AppI", "AppM"]
ROUND_TRIP_ILLEGAL_LOSS_TESTS = [
    {
        "test_id": "route_min_sigma_loss",
        "description": "Fail if AppA, AppI, or AppM drop out of the route minimum during conversion.",
    },
    {
        "test_id": "ambig_without_evidence_plan",
        "description": "Fail if AMBIG survives conversion without an EvidencePlan debt.",
    },
    {
        "test_id": "near_without_residual_ledger",
        "description": "Fail if NEAR survives conversion without a ResidualLedger debt.",
    },
    {
        "test_id": "ok_without_replay_or_witness",
        "description": "Fail if OK is claimed without replay and witness receipts.",
    },
    {
        "test_id": "publish_without_parity_or_appo",
        "description": "Fail if publish-class output lacks parity or AppO attestation.",
    },
    {
        "test_id": "semantic_change_without_migrate",
        "description": "Fail if semantic drift is declared without MIGRATE receipts.",
    },
    {
        "test_id": "corridor_widening_without_attestation",
        "description": "Fail if corridor widening occurs without attestation.",
    },
]
ROUND_TRIP_TRANSFORM_SPECS = {
    "myth_to_sigil": {
        "allowed_classes": ["law_equivalent"],
        "required_invariants": ["gate", "terminal_type", "overlay_debt"],
        "residual_requirements": ["preserve gate, terminal type, and overlay debt"],
        "obligations": ["no silent remap", "no erased ambiguity debt"],
    },
    "sigil_to_schema": {
        "allowed_classes": ["exact", "law_equivalent"],
        "required_invariants": ["gate", "route_min", "truth", "overlay_debt", "terminal_type", "receipt_debt"],
        "residual_requirements": ["expand defaults deterministically if needed"],
        "obligations": ["preserve route minimum", "preserve proof bundle obligations"],
    },
    "schema_to_automaton": {
        "allowed_classes": ["exact"],
        "required_invariants": ["gate", "route_min", "truth", "overlay_debt", "terminal_type", "receipt_debt"],
        "residual_requirements": ["no residual loss allowed"],
        "obligations": ["no selected-to-published jump", "no gated-to-executing jump without normalization"],
    },
    "automaton_to_wall_chart": {
        "allowed_classes": ["law_equivalent"],
        "required_invariants": ["gate", "route_min", "truth", "overlay_debt", "terminal_type", "receipt_debt"],
        "residual_requirements": ["wall chart may change shape but not law"],
        "obligations": ["preserve truth layer", "preserve terminal class"],
    },
    "pocket_card_or_poster": {
        "allowed_classes": ["residualized"],
        "required_invariants": ["gate", "route_min", "truth", "overlay_debt", "terminal_type", "receipt_debt"],
        "residual_requirements": ["name dropped detail in ResidualLedger or EvidencePlan"],
        "obligations": ["do not fake exactness", "declare compression loss explicitly"],
    },
}
ROUND_TRIP_FRONT_CONTEXT = {
    "Q42": {
        "transform_family": "automaton_to_wall_chart",
        "source_representation": "automaton",
        "transformed_representation": "wall_chart",
        "recovered_representation": "automaton_normalized",
        "source_extra": {"corridor_state": "runtime", "layout_mode": "owner_control"},
        "transformed_extra": {"corridor_state": "wall_chart", "layout_mode": "hall_projection"},
        "recovered_extra": {"corridor_state": "runtime", "layout_mode": "canonical_projection"},
        "allowed_loss": [],
        "proof_note": "Q42 carries runtime corridor state into Hall-facing chart and manifest surfaces without weakening Sigma.",
    },
    "Q46": {
        "transform_family": "sigil_to_schema",
        "source_representation": "sigil_packet",
        "transformed_representation": "schema_contract",
        "recovered_representation": "sigil_packet_normalized",
        "source_extra": {"notation_density": "sigil_packed", "carrier": "athenachka_wave"},
        "transformed_extra": {"notation_density": "schema_expanded", "carrier": "helix_contracts"},
        "recovered_extra": {"notation_density": "schema_recovered", "carrier": "athenachka_wave"},
        "allowed_loss": [],
        "proof_note": "Q46 expands the proved crystal packet into the first Helix::Contracts slice while preserving the same law bundle.",
    },
    "TQ04": {
        "transform_family": "schema_to_automaton",
        "source_representation": "schema_pack",
        "transformed_representation": "runner_contract",
        "recovered_representation": "schema_pack",
        "source_extra": {"runner_mode": "helical_contract", "pack_scope": "loop_phase_swarm_lift"},
        "transformed_extra": {"runner_mode": "helical_contract", "pack_scope": "loop_phase_swarm_lift"},
        "recovered_extra": {"runner_mode": "helical_contract", "pack_scope": "loop_phase_swarm_lift"},
        "allowed_loss": [],
        "proof_note": "TQ04 is the exact schema-to-runner bridge that anchors the membrane before wider Hall execution.",
    },
}

DOMAINS = ["Self", "Guild", "Source", "Stack"]
MOVES = ["Diagnose", "Refine", "Synthesize", "Scale"]
LENSES = ["Square", "Flower", "Cloud", "Fractal"]
WITNESS_CLASSES = ["direct", "derived", "blocked", "archive"]
SURFACES = ["Hall", "Temple", "Runtime", "Family"]
LANES = ["Sa", "Me", "Su", "Bridge"]
SCOPES = ["file", "folder", "family", "organism"]
METHODS = ["derive", "verify", "reconcile", "compress"]
ARTIFACTS = ["script", "ledger", "manifest", "mirror"]
VERIFY_TYPES = ["test", "receipt", "proof", "abstain"]
WRITEBACK_TYPES = ["questboard", "queue", "manifest", "family"]
RESTART_TYPES = ["same_lane", "cross_lane", "hall_seed", "temple_seed"]

FLOATING_AGENTS = [f"floating-agent-{index:02d}" for index in range(1, WAVE_CAPACITY + 1)]
CURRENT_FIRST_WAVE = ["Q42", "Q46", "TQ03", "TQ04", "TQ05", "TQ06", "ADV64-S01", "ADV64-S02"]
CONDUCTOR_PRIORITY = {
    "Q42": 100.0,
    "Q46": 96.0,
    "TQ03": 90.0,
    "TQ04": 89.0,
    "TQ05": 88.0,
    "TQ06": 87.0,
    "ADV64-S01": 84.0,
    "ADV64-S02": 83.0,
}
SEED_PAIR_SPECS = [
    ("ADV64-S01", ("Q42",), ("TQ04",), "Hall-to-runner bridge for the QSHRINK Fractal carrythrough"),
    ("ADV64-S02", ("Q46", "Q45"), ("TQ06", "TQ05"), "Athenachka proof carrythrough into the packet-fed restart loop"),
]
DEEP_NETWORK_SURFACES = [
    DEEP_NETWORK_ROOT / "README.md",
    DEEP_NETWORK_ROOT / "00_CONTROL" / "04_ALGORITHMIC_PIPELINE.md",
    DEEP_NETWORK_ROOT / "05_MATRIX_16X16" / "00_INDEX.md",
    DEEP_NETWORK_ROOT / "07_METRO_STACK" / "00_level_1_core_metro_map.md",
    DEEP_NETWORK_ROOT / "07_METRO_STACK" / "03_level_4_transcendence_metro_map.md",
    DEEP_NETWORK_ROOT / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md",
]

QUEST_OVERRIDES: dict[str, dict[str, str]] = {
    "Q02": {"domain": "Source", "move": "Diagnose", "lens": "Cloud", "witness_class": "blocked", "surface": "Hall", "lane": "Bridge", "scope": "organism", "method": "reconcile", "artifact": "manifest", "verify": "abstain", "writeback": "manifest", "restart": "hall_seed"},
    "FRONT-INT-SKILL-COHESION": {"domain": "Stack", "move": "Refine", "lens": "Square", "witness_class": "derived", "surface": "Hall", "lane": "Me", "scope": "family", "method": "reconcile", "artifact": "ledger", "verify": "receipt", "writeback": "manifest", "restart": "hall_seed"},
    "FRONT-INT-ATHENA-FLEET-BRIDGE": {"domain": "Source", "move": "Synthesize", "lens": "Flower", "witness_class": "derived", "surface": "Hall", "lane": "Bridge", "scope": "family", "method": "derive", "artifact": "manifest", "verify": "receipt", "writeback": "family", "restart": "hall_seed"},
    "FRONT-INT-QSHRINK-CANONICAL-FAMILY": {"domain": "Source", "move": "Refine", "lens": "Square", "witness_class": "derived", "surface": "Hall", "lane": "Me", "scope": "family", "method": "compress", "artifact": "manifest", "verify": "receipt", "writeback": "family", "restart": "hall_seed"},
    "Q35": {"domain": "Source", "move": "Synthesize", "lens": "Flower", "witness_class": "direct", "surface": "Hall", "lane": "Sa", "scope": "folder", "method": "derive", "artifact": "mirror", "verify": "receipt", "writeback": "family", "restart": "hall_seed"},
    "Q39": {"domain": "Stack", "move": "Synthesize", "lens": "Cloud", "witness_class": "derived", "surface": "Hall", "lane": "Bridge", "scope": "organism", "method": "reconcile", "artifact": "ledger", "verify": "proof", "writeback": "queue", "restart": "temple_seed"},
    "Q10": {"domain": "Guild", "move": "Scale", "lens": "Square", "witness_class": "derived", "surface": "Hall", "lane": "Sa", "scope": "family", "method": "derive", "artifact": "ledger", "verify": "receipt", "writeback": "family", "restart": "hall_seed"},
    "Q40": {"domain": "Source", "move": "Diagnose", "lens": "Square", "witness_class": "direct", "surface": "Hall", "lane": "Me", "scope": "organism", "method": "reconcile", "artifact": "ledger", "verify": "proof", "writeback": "manifest", "restart": "hall_seed"},
    "Q45": {"domain": "Guild", "move": "Refine", "lens": "Flower", "witness_class": "derived", "surface": "Hall", "lane": "Bridge", "scope": "organism", "method": "compress", "artifact": "manifest", "verify": "proof", "writeback": "manifest", "restart": "hall_seed"},
    "Q46": {"domain": "Guild", "move": "Refine", "lens": "Flower", "witness_class": "derived", "surface": "Hall", "lane": "Bridge", "scope": "organism", "method": "compress", "artifact": "manifest", "verify": "proof", "writeback": "manifest", "restart": "hall_seed"},
    "TQ03": {"domain": "Source", "move": "Scale", "lens": "Square", "witness_class": "archive", "surface": "Temple", "lane": "Bridge", "scope": "organism", "method": "derive", "artifact": "ledger", "verify": "proof", "writeback": "questboard", "restart": "hall_seed"},
    "TQ04": {"domain": "Stack", "move": "Refine", "lens": "Fractal", "witness_class": "derived", "surface": "Temple", "lane": "Su", "scope": "organism", "method": "verify", "artifact": "manifest", "verify": "proof", "writeback": "manifest", "restart": "temple_seed"},
    "TQ05": {"domain": "Stack", "move": "Synthesize", "lens": "Fractal", "witness_class": "derived", "surface": "Temple", "lane": "Bridge", "scope": "organism", "method": "derive", "artifact": "ledger", "verify": "proof", "writeback": "questboard", "restart": "temple_seed"},
    "TQ06": {"domain": "Guild", "move": "Refine", "lens": "Fractal", "witness_class": "derived", "surface": "Temple", "lane": "Bridge", "scope": "organism", "method": "derive", "artifact": "manifest", "verify": "receipt", "writeback": "queue", "restart": "hall_seed"},
}


@dataclass
class QuestRecord:
    quest_id: str
    quest_address: str
    parent_address: str
    title: str
    objective: str
    why_now: str
    target_surfaces: list[str]
    best_lane: str
    witness_needed: str
    writeback: str
    restart_seed: str
    status: str
    owner: str
    blockers: list[str] = field(default_factory=list)
    completion_evidence: list[str] = field(default_factory=list)
    source_board: str = ""
    address_components: dict[str, Any] = field(default_factory=dict)
    registration_kind: str = "board"
    frontier_seed: str = ""
    source_fronts: list[str] = field(default_factory=list)
    priority_score: float = 0.0
    success_gate: dict[str, Any] = field(default_factory=dict)
    round_trip_required: bool = False
    round_trip_certificate_id: str = ""
    round_trip_class: str = ""


@dataclass
class WavePacket:
    packet_id: str
    wave_id: str
    frontier_seed: str
    address_slice: list[str]
    priority_score: float
    max_parallel_claims: int
    docs_gate_status: str
    evidence_surfaces: list[str]
    success_gate: dict[str, Any]
    assigned_owner: str
    source_front: str
    source_fronts: list[str]
    status: str
    priority_reason: str
    round_trip_certificate_id: str = ""
    round_trip_class: str = ""


@dataclass
class InvariantBundle:
    gate: str
    route_min: list[str]
    truth: str
    overlay_debt: dict[str, str]
    terminal_type: str
    receipt_debt: list[str]


@dataclass
class TransformLaw:
    transform_family: str
    allowed_classes: list[str]
    required_invariants: list[str]
    residual_requirements: list[str]
    obligations: list[str]


@dataclass
class RoundTripCertificate:
    certificate_id: str
    quest_id: str
    transform_family: str
    source_repr: dict[str, Any]
    forward_transform: str
    transformed_repr: dict[str, Any]
    inverse_transform: str
    recovered_repr: dict[str, Any]
    allowed_loss: list[str]
    proof_bundle: dict[str, Any]
    invariant_before: dict[str, Any]
    invariant_after: dict[str, Any]
    round_trip_class: str
    loss_findings: list[str]
    docs_gate_status: str
    lawful: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relpath(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_line(value: str) -> str:
    return value.strip().strip("`").strip()


def normalize_status(raw_status: str) -> str:
    return raw_status.split()[0].upper()


def unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = item.replace("\\", "/").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def path_like_items(items: list[str]) -> list[str]:
    results = []
    for item in items:
        normalized = item.replace("\\", "/")
        if "/" in normalized or normalized.endswith((".md", ".py", ".json", ".txt", ".docx")):
            results.append(normalized)
    return results


def path_exists(relative_or_absolute: str) -> bool:
    candidate = Path(relative_or_absolute)
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate
    return candidate.exists()


def parse_markdown_quests(path: Path, source_board: str) -> list[dict[str, Any]]:
    text = read_text(path)
    lines = text.splitlines()
    quests: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_field: str | None = None
    header_patterns = [
        re.compile(r"^### Quest (?P<head>.+?) `?\[(?P<status>[^\]]+)\]`?$"),
        re.compile(r"^### (?P<head>TQ\d+:.+?) `?\[(?P<status>[^\]]+)\]`?$"),
    ]

    def flush() -> None:
        nonlocal current, current_field
        if current is not None:
            quests.append(current)
        current = None
        current_field = None

    for raw_line in lines:
        stripped = raw_line.strip()
        matched = None
        for pattern in header_patterns:
            matched = pattern.match(stripped)
            if matched:
                break
        if matched:
            flush()
            head = matched.group("head")
            if ":" in head:
                quest_id, title = head.split(":", 1)
            else:
                quest_id, title = head, head
            current = {
                "quest_id": quest_id.strip(),
                "title": title.strip(),
                "status": normalize_status(matched.group("status").strip()),
                "source_board": source_board,
                "target_surfaces": [],
                "completion_evidence": [],
            }
            continue
        if current is None:
            continue
        label_only = re.match(r"^- ([A-Za-z][A-Za-z0-9 _/-]+):\s*$", stripped)
        if label_only:
            current_field = label_only.group(1).lower().replace(" ", "_").replace("/", "_")
            if current_field not in current:
                current[current_field] = ""
            continue
        label_value = re.match(r"^- ([A-Za-z][A-Za-z0-9 _/-]+):\s*(.+)$", stripped)
        if label_value:
            current_field = label_value.group(1).lower().replace(" ", "_").replace("/", "_")
            value = clean_line(label_value.group(2))
            if current_field in {"target_surfaces", "completion_evidence"}:
                current.setdefault(current_field, []).append(value)
            else:
                current[current_field] = value
            continue
        if current_field in {"target_surfaces", "completion_evidence"} and stripped:
            if stripped.startswith("- "):
                current.setdefault(current_field, []).append(clean_line(stripped[2:]))
            else:
                current.setdefault(current_field, []).append(clean_line(stripped))
            continue
        if current_field and stripped:
            previous = current.get(current_field, "")
            current[current_field] = f"{previous} {clean_line(stripped)}".strip()

    flush()
    return quests


def detect_gate_blocked() -> bool:
    return "Status: **BLOCKED**" in read_text(GATE_STATUS_PATH)


def load_change_feed_signals() -> list[str]:
    signals = []
    for raw_line in read_text(CHANGE_FEED_PATH).splitlines():
        stripped = raw_line.strip()
        if re.match(r"^\d+\.\s", stripped):
            signals.append(stripped)
    return signals[-10:]


def load_existing_claims() -> list[dict[str, Any]]:
    return swarm_board.load_board_claims()


def load_existing_notes() -> list[dict[str, Any]]:
    return swarm_board.load_notes()


def match_owner(quest_id: str, quest_title: str, claims: list[dict[str, Any]]) -> str:
    for claim in claims:
        frontier = (claim.get("frontier") or "").strip()
        if frontier == quest_id or frontier == quest_title:
            return claim.get("owner", "")
        if quest_id and quest_id in frontier:
            return claim.get("owner", "")
    return ""


def infer_domain(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("domain"):
        return override["domain"]
    low = f"{record['title']} {record.get('objective', '')} {' '.join(record.get('target_surfaces', []))}".lower()
    if "self_actualize" in low and "guild" not in low and "temple" not in low:
        return "Self"
    if any(item in low for item in ["guild hall", "guild", "hall"]):
        return "Guild"
    if any(item in low for item in ["athena temple", "temple", "helical", "whole-corpus", "runner contract"]):
        return "Stack"
    if any(item in low for item in ["athena fleet", "qshrink", "origin", "trading bot", "math", "voynich", "family"]):
        return "Source"
    return "Guild" if record["source_board"] == "hall" else "Stack"


def infer_move(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("move"):
        return override["move"]
    low = f"{record['title']} {record.get('objective', '')}".lower()
    if any(token in low for token in ["audit", "diagnose", "sweep", "find", "identify"]):
        return "Diagnose"
    if any(token in low for token in ["prune", "reconcile", "repair", "harden", "bind", "refine", "unlock"]):
        return "Refine"
    if any(token in low for token in ["mirror", "externalize", "promote", "create", "emit", "synthesize", "turn"]):
        return "Synthesize"
    return "Scale" if any(token in low for token in ["scale", "densify", "couple", "expand", "rank"]) else "Refine"


def infer_lens(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("lens"):
        return override["lens"]
    low = f"{record['title']} {record.get('objective', '')} {record.get('why_now', '')}".lower()
    if any(token in low for token in ["loop", "helical", "fractal", "restart", "cadence"]):
        return "Fractal"
    if any(token in low for token in ["truth", "contradiction", "cloud", "uncertainty", "theorem"]):
        return "Cloud"
    if any(token in low for token in ["bridge", "mirror", "bind", "route", "corridor"]):
        return "Flower"
    return "Square"


def infer_witness_class(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("witness_class"):
        return override["witness_class"]
    if record["status"] == "BLOCKED":
        return "blocked"
    low = " ".join(record.get("target_surfaces", [])).lower()
    if "archive" in low or "zip" in low:
        return "archive"
    return "direct" if any(token in low for token in ["origin", "source", "docx", "direct"]) else "derived"


def infer_surface(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("surface"):
        return override["surface"]
    low = " ".join(record.get("target_surfaces", [])).lower()
    if "athena temple" in low:
        return "Temple"
    if "runtime" in low or "95_manifests" in low:
        return "Runtime"
    if "families/" in low or "family_" in low:
        return "Family"
    return "Hall"


def infer_lane(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("lane"):
        return override["lane"]
    low = f"{record['title']} {' '.join(record.get('target_surfaces', []))}".lower()
    if any(token in low for token in ["bridge", "corridor", "cross"]):
        return "Bridge"
    if any(token in low for token in ["runtime", "verify", "test", "execute"]):
        return "Su"
    if any(token in low for token in ["origin", "family", "mirror", "source"]):
        return "Sa"
    return "Me"


def infer_scope(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("scope"):
        return override["scope"]
    surfaces = record.get("target_surfaces", [])
    if len(surfaces) >= 4 or any("whole-corpus" in item.lower() for item in surfaces):
        return "organism"
    if any("families/" in item.lower() or "family_" in item.lower() for item in surfaces):
        return "family"
    if len(surfaces) > 1:
        return "folder"
    return "file"


def infer_method(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("method"):
        return override["method"]
    low = f"{record['title']} {record.get('objective', '')}".lower()
    if any(token in low for token in ["verify", "test", "runtime lane"]):
        return "verify"
    if any(token in low for token in ["reconcile", "repair", "sweep", "prune"]):
        return "reconcile"
    if any(token in low for token in ["compress", "qshrink"]):
        return "compress"
    return "derive"


def infer_artifact(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("artifact"):
        return override["artifact"]
    low = " ".join(record.get("target_surfaces", [])).lower()
    if "runtime/" in low or ".py" in low:
        return "script"
    if "manifest" in low:
        return "manifest"
    if "mirror" in low:
        return "mirror"
    return "ledger"


def infer_verify(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("verify"):
        return override["verify"]
    low = f"{record.get('witness_needed', '')} {record.get('objective', '')}".lower()
    if record["status"] == "BLOCKED":
        return "abstain"
    if "test" in low or "verify" in low:
        return "test"
    if "theorem" in low or "proof" in low or "contract" in low:
        return "proof"
    return "receipt"


def infer_writeback(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("writeback"):
        return override["writeback"]
    low = f"{record.get('writeback', '')} {' '.join(record.get('target_surfaces', []))}".lower()
    if "family" in low:
        return "family"
    if "queue" in low:
        return "queue"
    if "manifest" in low:
        return "manifest"
    return "questboard"


def infer_restart(record: dict[str, Any]) -> str:
    override = QUEST_OVERRIDES.get(record["quest_id"], {})
    if override.get("restart"):
        return override["restart"]
    low = f"{record.get('restart_seed', '')} {record.get('why_now', '')}".lower()
    if "temple" in low or record["source_board"] == "temple":
        return "temple_seed"
    if "cross" in low or "bridge" in low:
        return "cross_lane"
    if "same lane" in low:
        return "same_lane"
    return "hall_seed"


def encode_index(a: str, b: str, c: str, values_a: list[str], values_b: list[str], values_c: list[str]) -> int:
    return values_a.index(a) * 16 + values_b.index(b) * 4 + values_c.index(c) + 1


def build_address_components(record: dict[str, Any]) -> dict[str, Any]:
    domain = infer_domain(record)
    move = infer_move(record)
    lens = infer_lens(record)
    witness_class = infer_witness_class(record)
    surface = infer_surface(record)
    lane = infer_lane(record)
    scope = infer_scope(record)
    method = infer_method(record)
    artifact = infer_artifact(record)
    verify = infer_verify(record)
    writeback = infer_writeback(record)
    restart = infer_restart(record)
    return {
        "intent64": {"index": encode_index(domain, move, lens, DOMAINS, MOVES, LENSES), "domain": domain, "move": move, "lens": lens},
        "witness64": {"index": encode_index(witness_class, surface, lane, WITNESS_CLASSES, SURFACES, LANES), "witness_class": witness_class, "surface": surface, "lane": lane},
        "execution64": {"index": encode_index(scope, method, artifact, SCOPES, METHODS, ARTIFACTS), "scope": scope, "method": method, "artifact": artifact},
        "return64": {"index": encode_index(verify, writeback, restart, VERIFY_TYPES, WRITEBACK_TYPES, RESTART_TYPES), "verify": verify, "writeback": writeback, "restart": restart},
    }


def quest_address_from_components(components: dict[str, Any]) -> str:
    return f"A{components['intent64']['index']:02d}.B{components['witness64']['index']:02d}.C{components['execution64']['index']:02d}.D{components['return64']['index']:02d}"


def should_exclude_for_gate(record: QuestRecord, gate_blocked: bool) -> bool:
    if not gate_blocked:
        return False
    low = " ".join(record.target_surfaces).lower()
    return record.quest_id == "Q02" or "trading bot/docs_search.py" in low


def round_trip_required(record: QuestRecord) -> bool:
    return record.quest_id in ROUND_TRIP_GOVERNED_FRONTS


def canonicalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonicalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        normalized = [canonicalize_value(item) for item in value]
        if all(isinstance(item, (str, int, float, bool)) or item is None for item in normalized):
            return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True))
        return normalized
    return value


def canonicalize_invariant_bundle(bundle: InvariantBundle | dict[str, Any]) -> dict[str, Any]:
    payload = asdict(bundle) if isinstance(bundle, InvariantBundle) else deepcopy(bundle)
    payload["route_min"] = sorted(set(payload.get("route_min", [])))
    payload["receipt_debt"] = sorted(set(payload.get("receipt_debt", [])))
    payload["overlay_debt"] = {
        key: payload.get("overlay_debt", {}).get(key, "")
        for key in sorted(payload.get("overlay_debt", {}))
    }
    return canonicalize_value(payload)


def canonicalize_representation(payload: dict[str, Any]) -> dict[str, Any]:
    return canonicalize_value(payload)


def truth_for_record(record: QuestRecord) -> str:
    if record.status == "PROMOTED":
        return "OK"
    if record.status == "BLOCKED":
        return "AMBIG"
    if record.status == "SUPERSEDED":
        return "FAIL"
    return "NEAR"


def overlay_debt_for_record(record: QuestRecord) -> dict[str, str]:
    truth = truth_for_record(record)
    if truth == "AMBIG":
        return {"L": f"EvidencePlan::{relpath(GATE_STATUS_PATH)}"}
    if truth == "NEAR":
        return {"J": f"ResidualLedger::{relpath(ROUND_TRIP_RECEIPT_PATH)}::{record.quest_id}"}
    if truth == "FAIL":
        return {"K": f"QuarantineReceipt::{relpath(GATE_STATUS_PATH)}::{record.quest_id}"}
    return {}


def receipt_debt_for_record(record: QuestRecord) -> list[str]:
    receipts: list[str] = []
    evidence_pointer = next(iter(record.completion_evidence), "")
    target_pointer = next(iter(record.target_surfaces), "")
    if evidence_pointer:
        receipts.append(f"ReplayPtr::{evidence_pointer}")
        receipts.append(f"WitnessPtr::{evidence_pointer}")
    elif target_pointer:
        receipts.append(f"ReplayPtr::{target_pointer}")
        receipts.append(f"WitnessPtr::{target_pointer}")
    if record.status == "PROMOTED":
        receipts.append(f"ParityPtr::{relpath(RECEIPT_PATH)}")
    return unique_list(receipts)


def terminal_type_for_record(record: QuestRecord) -> str:
    if record.status == "PROMOTED":
        return "checkpoint"
    if record.status == "BLOCKED":
        return "fail"
    if record.status == "SUPERSEDED":
        return "return"
    return "transit"


def invariant_bundle_for_record(record: QuestRecord) -> InvariantBundle:
    return InvariantBundle(
        gate=record.quest_id,
        route_min=list(ROUND_TRIP_REQUIRED_ROUTE_MIN),
        truth=truth_for_record(record),
        overlay_debt=overlay_debt_for_record(record),
        terminal_type=terminal_type_for_record(record),
        receipt_debt=receipt_debt_for_record(record),
    )


def build_transform_law(transform_family: str) -> TransformLaw:
    spec = ROUND_TRIP_TRANSFORM_SPECS[transform_family]
    residual_requirements = spec.get("residual_requirements", [])
    if isinstance(residual_requirements, str):
        residual_requirements = [residual_requirements]
    return TransformLaw(
        transform_family=transform_family,
        allowed_classes=list(spec["allowed_classes"]),
        required_invariants=list(spec["required_invariants"]),
        residual_requirements=list(residual_requirements),
        obligations=list(spec["obligations"]),
    )


def representation_payload(
    record: QuestRecord,
    representation: str,
    bundle: InvariantBundle,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "quest_id": record.quest_id,
        "quest_address": record.quest_address,
        "source_board": record.source_board,
        "representation": representation,
        "surface_hint": next(iter(record.target_surfaces), ""),
        "invariant_bundle": canonicalize_invariant_bundle(bundle),
    }
    if extra:
        payload.update(deepcopy(extra))
    return canonicalize_representation(payload)


def retag_representation(
    target_representation: str,
    extra: dict[str, Any] | None = None,
    drop_fields: list[str] | None = None,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def apply(payload: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(payload)
        result["representation"] = target_representation
        if drop_fields:
            for field_name in drop_fields:
                result.pop(field_name, None)
        if extra:
            for key, value in extra.items():
                result[key] = deepcopy(value)
        return canonicalize_representation(result)

    return apply


def payload_loss_findings(source_payload: dict[str, Any], recovered_payload: dict[str, Any]) -> list[str]:
    protected_keys = {"invariant_bundle", "quest_id", "quest_address", "source_board", "surface_hint", "representation"}
    losses: list[str] = []
    for key in sorted(set(source_payload) | set(recovered_payload)):
        if key in protected_keys:
            continue
        if source_payload.get(key) != recovered_payload.get(key):
            losses.append(key)
    return losses


def illegal_loss_findings(
    invariant_before: dict[str, Any],
    invariant_after: dict[str, Any],
    proof_bundle: dict[str, Any],
) -> list[str]:
    findings: list[str] = []
    route_min_after = set(invariant_after.get("route_min", []))
    if any(required not in route_min_after for required in ROUND_TRIP_REQUIRED_ROUTE_MIN):
        findings.append("route_min_sigma_loss")
    if invariant_after.get("truth") == "AMBIG" and "L" not in invariant_after.get("overlay_debt", {}):
        findings.append("ambig_without_evidence_plan")
    if invariant_after.get("truth") == "NEAR" and "J" not in invariant_after.get("overlay_debt", {}):
        findings.append("near_without_residual_ledger")
    if invariant_after.get("truth") == "OK":
        receipt_debt = set(invariant_after.get("receipt_debt", []))
        if not any(item.startswith("ReplayPtr::") for item in receipt_debt) or not any(
            item.startswith("WitnessPtr::") for item in receipt_debt
        ):
            findings.append("ok_without_replay_or_witness")
    if invariant_after.get("terminal_type") == "publish":
        receipt_debt = set(invariant_after.get("receipt_debt", []))
        if "AppO" not in route_min_after or not any(item.startswith("ParityPtr::") for item in receipt_debt):
            findings.append("publish_without_parity_or_appo")
    if proof_bundle.get("semantic_change") and "MIGRATE" not in set(proof_bundle.get("receipt_obligations", [])):
        findings.append("semantic_change_without_migrate")
    if proof_bundle.get("corridor_widening") and "ATTEST" not in set(proof_bundle.get("receipt_obligations", [])):
        findings.append("corridor_widening_without_attestation")
    return findings


def round_trip_certify(
    source_repr: dict[str, Any],
    forward: Callable[[dict[str, Any]], dict[str, Any]],
    inverse: Callable[[dict[str, Any]], dict[str, Any]],
    context: dict[str, Any],
) -> RoundTripCertificate:
    source0 = canonicalize_representation(deepcopy(source_repr))
    transformed = canonicalize_representation(forward(deepcopy(source0)))
    recovered = canonicalize_representation(inverse(deepcopy(transformed)))
    invariant_before = canonicalize_invariant_bundle(source0["invariant_bundle"])
    invariant_after = canonicalize_invariant_bundle(recovered["invariant_bundle"])
    law = build_transform_law(context["transform_family"])
    declared_loss = list(context.get("allowed_loss", []))
    payload_losses = payload_loss_findings(source0, recovered)
    illegal_findings = illegal_loss_findings(invariant_before, invariant_after, context["proof_bundle"])
    loss_findings = illegal_findings + [f"declared::{item}" for item in payload_losses if item in declared_loss]
    if illegal_findings:
        round_trip_class = "illegal"
    elif source0 == recovered:
        round_trip_class = "exact"
    elif payload_losses and set(payload_losses).issubset(set(declared_loss)) and invariant_before == invariant_after:
        round_trip_class = "residualized"
    elif invariant_before == invariant_after:
        round_trip_class = "law_equivalent"
    else:
        round_trip_class = "illegal"
    lawful = round_trip_class != "illegal" and round_trip_class in set(law.allowed_classes)
    if round_trip_class == "illegal" and "illegal_unclassified_loss" not in loss_findings:
        loss_findings.append("illegal_unclassified_loss")
    return RoundTripCertificate(
        certificate_id=context["certificate_id"],
        quest_id=context["quest_id"],
        transform_family=context["transform_family"],
        source_repr=source0,
        forward_transform=context["forward_transform"],
        transformed_repr=transformed,
        inverse_transform=context["inverse_transform"],
        recovered_repr=recovered,
        allowed_loss=declared_loss,
        proof_bundle=context["proof_bundle"],
        invariant_before=invariant_before,
        invariant_after=invariant_after,
        round_trip_class=round_trip_class,
        loss_findings=loss_findings,
        docs_gate_status=context["docs_gate_status"],
        lawful=lawful,
    )


def build_governed_round_trip_certificate(record: QuestRecord) -> RoundTripCertificate | None:
    spec = ROUND_TRIP_FRONT_CONTEXT.get(record.quest_id)
    if spec is None:
        return None
    bundle = invariant_bundle_for_record(record)
    source_repr = representation_payload(
        record,
        spec["source_representation"],
        bundle,
        extra=spec.get("source_extra"),
    )
    evidence_surfaces = unique_list(
        path_like_items(record.target_surfaces)
        + path_like_items(record.completion_evidence)
        + [relpath(GATE_STATUS_PATH), relpath(ACTIVE_RUN_PATH), relpath(ROUND_TRIP_RECEIPT_PATH)]
    )[:16]
    proof_bundle = {
        "law_id": spec["transform_family"],
        "allowed_classes": ROUND_TRIP_TRANSFORM_SPECS[spec["transform_family"]]["allowed_classes"],
        "evidence_surfaces": evidence_surfaces,
        "proof_note": spec["proof_note"],
        "receipt_obligations": ["ReplayPtr", "WitnessPtr"],
        "semantic_change": False,
        "corridor_widening": False,
    }
    return round_trip_certify(
        source_repr,
        retag_representation(
            spec["transformed_representation"],
            extra=spec.get("transformed_extra"),
        ),
        retag_representation(
            spec["recovered_representation"],
            extra=spec.get("recovered_extra"),
        ),
        {
            "certificate_id": f"RTC-v0-{record.quest_id}",
            "quest_id": record.quest_id,
            "transform_family": spec["transform_family"],
            "allowed_loss": spec.get("allowed_loss", []),
            "proof_bundle": proof_bundle,
            "docs_gate_status": "BLOCKED" if detect_gate_blocked() else "READY",
            "forward_transform": f"{spec['source_representation']}->{spec['transformed_representation']}",
            "inverse_transform": f"{spec['transformed_representation']}->{spec['recovered_representation']}",
        },
    )


def build_reference_round_trip_examples() -> list[RoundTripCertificate]:
    example_record = QuestRecord(
        quest_id="RTC-REF",
        quest_address="A00.B00.C00.D00",
        parent_address="",
        title="Round trip reference",
        objective="Reference example only.",
        why_now="Verifier coverage for residualized and illegal branches.",
        target_surfaces=[],
        best_lane="",
        witness_needed="",
        writeback="",
        restart_seed="reference only",
        status="OPEN",
        owner="",
    )
    base_bundle = InvariantBundle(
        gate="RTC-REF",
        route_min=list(ROUND_TRIP_REQUIRED_ROUTE_MIN),
        truth="NEAR",
        overlay_debt={"J": "ResidualLedger::reference"},
        terminal_type="transit",
        receipt_debt=["ReplayPtr::reference", "WitnessPtr::reference"],
    )
    residual_source = representation_payload(
        example_record,
        "dense_schema",
        base_bundle,
        extra={"annotations": "full", "display_density": "dense"},
    )
    residual = round_trip_certify(
        residual_source,
        retag_representation("poster_card", extra={"display_density": "thin"}, drop_fields=["annotations"]),
        retag_representation("poster_card", extra={"display_density": "thin"}, drop_fields=["annotations"]),
        {
            "certificate_id": "RTC-v0-reference-residualized",
            "quest_id": "RTC-REF-RESIDUAL",
            "transform_family": "pocket_card_or_poster",
            "allowed_loss": ["annotations", "display_density"],
            "proof_bundle": {
                "law_id": "pocket_card_or_poster",
                "allowed_classes": ["residualized"],
                "evidence_surfaces": [relpath(ROUND_TRIP_RECEIPT_PATH)],
                "proof_note": "Reference residualized transform for card/poster compression.",
                "receipt_obligations": ["ReplayPtr", "WitnessPtr"],
                "semantic_change": False,
                "corridor_widening": False,
            },
            "docs_gate_status": "BLOCKED" if detect_gate_blocked() else "READY",
            "forward_transform": "dense_schema->poster_card",
            "inverse_transform": "poster_card->poster_card",
        },
    )
    illegal_bundle = InvariantBundle(
        gate="RTC-REF-ILLEGAL",
        route_min=list(ROUND_TRIP_REQUIRED_ROUTE_MIN),
        truth="OK",
        overlay_debt={},
        terminal_type="publish",
        receipt_debt=["WitnessPtr::reference"],
    )
    illegal_source = {
        "quest_id": "RTC-REF-ILLEGAL",
        "quest_address": "A00.B00.C00.D01",
        "source_board": "conductor",
        "representation": "schema_pack",
        "surface_hint": relpath(ROUND_TRIP_RECEIPT_PATH),
        "invariant_bundle": canonicalize_invariant_bundle(illegal_bundle),
    }
    illegal = round_trip_certify(
        illegal_source,
        retag_representation(
            "published_bundle",
            extra={
                "invariant_bundle": canonicalize_invariant_bundle(
                    {
                        "gate": "RTC-REF-ILLEGAL",
                        "route_min": ["AppA", "AppM"],
                        "truth": "OK",
                        "overlay_debt": {},
                        "terminal_type": "publish",
                        "receipt_debt": ["WitnessPtr::reference"],
                    }
                )
            },
        ),
        retag_representation(
            "published_bundle",
            extra={
                "invariant_bundle": canonicalize_invariant_bundle(
                    {
                        "gate": "RTC-REF-ILLEGAL",
                        "route_min": ["AppA", "AppM"],
                        "truth": "OK",
                        "overlay_debt": {},
                        "terminal_type": "publish",
                        "receipt_debt": ["WitnessPtr::reference"],
                    }
                )
            },
        ),
        {
            "certificate_id": "RTC-v0-reference-illegal",
            "quest_id": "RTC-REF-ILLEGAL",
            "transform_family": "schema_to_automaton",
            "allowed_loss": [],
            "proof_bundle": {
                "law_id": "schema_to_automaton",
                "allowed_classes": ["exact"],
                "evidence_surfaces": [relpath(ROUND_TRIP_RECEIPT_PATH)],
                "proof_note": "Reference illegal transform proving the loss linter fires.",
                "receipt_obligations": [],
                "semantic_change": True,
                "corridor_widening": True,
            },
            "docs_gate_status": "BLOCKED" if detect_gate_blocked() else "READY",
            "forward_transform": "schema_pack->published_bundle",
            "inverse_transform": "published_bundle->published_bundle",
        },
    )
    return [residual, illegal]


def apply_round_trip_certificate(record: QuestRecord, certificate: RoundTripCertificate) -> None:
    record.round_trip_required = True
    record.round_trip_certificate_id = certificate.certificate_id
    record.round_trip_class = certificate.round_trip_class
    record.success_gate.setdefault("completion_receipt", {})
    record.success_gate["round_trip_required"] = True
    record.success_gate["round_trip_lawful"] = certificate.lawful
    record.success_gate["round_trip_certificate_id"] = certificate.certificate_id
    record.success_gate["round_trip_class"] = certificate.round_trip_class
    record.success_gate["round_trip_registry_path"] = relpath(ROUND_TRIP_CERTIFICATES_PATH)
    record.success_gate["completion_receipt"]["round_trip_required"] = True
    record.success_gate["completion_receipt"]["round_trip_certificate_id"] = certificate.certificate_id
    record.success_gate["completion_receipt"]["round_trip_class"] = certificate.round_trip_class
    record.success_gate["completion_receipt"]["round_trip_lawful"] = certificate.lawful


def build_round_trip_registry(records_by_id: dict[str, QuestRecord]) -> dict[str, Any]:
    governed_certificates: list[RoundTripCertificate] = []
    for quest_id in ROUND_TRIP_GOVERNED_FRONTS:
        record = records_by_id.get(quest_id)
        if record is None:
            continue
        certificate = build_governed_round_trip_certificate(record)
        if certificate is None:
            continue
        apply_round_trip_certificate(record, certificate)
        governed_certificates.append(certificate)
    reference_examples = build_reference_round_trip_examples()
    transform_laws = [asdict(build_transform_law(name)) for name in ROUND_TRIP_TRANSFORM_SPECS]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "docs_gate_status": "BLOCKED" if detect_gate_blocked() else "READY",
        "registry_path": relpath(ROUND_TRIP_CERTIFICATES_PATH),
        "governed_fronts": [certificate.quest_id for certificate in governed_certificates],
        "protected_invariant_bundle": ["gate", "route_min", "truth", "overlay_debt", "terminal_type", "receipt_debt"],
        "required_route_min": list(ROUND_TRIP_REQUIRED_ROUTE_MIN),
        "transform_laws": transform_laws,
        "illegal_loss_tests": list(ROUND_TRIP_ILLEGAL_LOSS_TESTS),
        "governed_certificates": [asdict(certificate) for certificate in governed_certificates],
        "reference_examples": [asdict(certificate) for certificate in reference_examples],
    }


def completion_receipt_for_record(record: QuestRecord) -> dict[str, Any]:
    terminal_statuses = {"PROMOTED", "BLOCKED", "SUPERSEDED"}
    artifact_landed = any(path_exists(item) for item in record.completion_evidence)
    board_update_landed = record.registration_kind == "board" and record.status in terminal_statuses
    writeback_landed = bool(record.writeback.strip()) or any(
        token in item.lower()
        for item in record.completion_evidence
        for token in ("manifest", "family", "queue", "quest_board", "guild_hall", "hall", "temple_state")
    )
    restart_seed = record.restart_seed.strip()
    docs_gate_status = "BLOCKED" if detect_gate_blocked() else "READY"
    if record.registration_kind == "seeded":
        replay_notes = "Seeded adjacent bridge address; completion remains pending until the four-witness contract lands."
    elif board_update_landed:
        replay_notes = "Board-backed quest; terminal status came from the live Hall or Temple surface."
    else:
        replay_notes = "Active frontier; completion is still pending."
    return {
        "artifact_landed": artifact_landed,
        "board_update_landed": board_update_landed,
        "writeback_landed": writeback_landed,
        "restart_seed": restart_seed,
        "docs_gate_status": docs_gate_status,
        "replay_notes": replay_notes,
        "round_trip_required": record.round_trip_required,
        "round_trip_certificate_id": record.round_trip_certificate_id,
        "round_trip_class": record.round_trip_class,
    }


def success_gate_for_record(record: QuestRecord) -> dict[str, Any]:
    receipt = completion_receipt_for_record(record)
    ready = bool(
        receipt["artifact_landed"]
        and receipt["board_update_landed"]
        and receipt["writeback_landed"]
        and receipt["restart_seed"]
    )
    return {
        "requires_all": ["artifact_landed", "board_update_landed", "writeback_landed", "restart_seed"],
        "ready": ready,
        "completion_receipt": receipt,
        "round_trip_required": record.round_trip_required,
        "round_trip_lawful": not record.round_trip_required,
        "round_trip_certificate_id": record.round_trip_certificate_id,
        "round_trip_class": record.round_trip_class,
    }


def normalize_record(raw: dict[str, Any], claims: list[dict[str, Any]]) -> QuestRecord:
    components = build_address_components(raw)
    blockers = []
    if raw["status"] == "BLOCKED" and detect_gate_blocked():
        blockers.append("docs_gate_blocked")
    record = QuestRecord(
        quest_id=raw["quest_id"],
        quest_address=quest_address_from_components(components),
        parent_address="",
        title=raw["title"],
        objective=raw.get("objective", ""),
        why_now=raw.get("why_now", ""),
        target_surfaces=raw.get("target_surfaces", []),
        best_lane=raw.get("best_lane", ""),
        witness_needed=raw.get("witness_needed", ""),
        writeback=raw.get("writeback", ""),
        restart_seed=raw.get("restart_seed", ""),
        status=raw["status"],
        owner=match_owner(raw["quest_id"], raw["title"], claims),
        blockers=blockers,
        completion_evidence=raw.get("completion_evidence", []),
        source_board=raw["source_board"],
        address_components=components,
        registration_kind="board",
        frontier_seed=raw["quest_id"],
        source_fronts=[raw["quest_id"]],
    )
    record.success_gate = success_gate_for_record(record)
    return record


def load_previous_tracker() -> dict[str, Any]:
    payload = load_json(CLAIM_TRACKER_PATH, {})
    return payload.get("claims", payload)


def load_previous_loop_state() -> dict[str, Any]:
    return load_json(LOOP_STATE_PATH, {})


def select_next_frontier(records: list[QuestRecord], gate_blocked: bool) -> str:
    hall_open = [
        record
        for record in records
        if record.source_board == "hall" and record.status == "OPEN" and not should_exclude_for_gate(record, gate_blocked)
    ]
    ordered = {quest_id: index for index, quest_id in enumerate(CURRENT_FIRST_WAVE)}
    hall_open.sort(key=lambda item: ordered.get(item.quest_id, 999))
    if hall_open:
        return hall_open[0].quest_id
    temple_candidates = [
        record
        for record in records
        if record.source_board == "temple" and record.status in {"OPEN", "ACTIVE"} and not should_exclude_for_gate(record, gate_blocked)
    ]
    temple_candidates.sort(key=lambda item: ordered.get(item.quest_id, 999))
    if temple_candidates:
        return temple_candidates[0].quest_id
    blocked = [record for record in records if record.status == "BLOCKED"]
    return blocked[0].quest_id if blocked else "NONE"


def sort_records(records: list[QuestRecord]) -> list[QuestRecord]:
    board_order = {"hall": 0, "temple": 1, "conductor": 2}
    preferred = {quest_id: index for index, quest_id in enumerate(CURRENT_FIRST_WAVE)}
    return sorted(
        records,
        key=lambda item: (
            board_order.get(item.source_board, 9),
            preferred.get(item.quest_id, 999),
            item.priority_score * -1,
            item.quest_id,
        ),
    )


def build_records() -> list[QuestRecord]:
    claims = load_existing_claims()
    hall = [normalize_record(item, claims) for item in parse_markdown_quests(QUEST_BOARD_PATH, "hall")]
    temple = [normalize_record(item, claims) for item in parse_markdown_quests(TEMPLE_BOARD_PATH, "temple")]
    return sort_records(hall + temple)


def priority_score_for_record(record: QuestRecord, records_by_id: dict[str, QuestRecord]) -> float:
    base = CONDUCTOR_PRIORITY.get(record.quest_id, 50.0)
    if record.quest_id == "Q42":
        if "FRONT-INT-QSHRINK-CANONICAL-FAMILY" in records_by_id:
            base += 1.5
        if "FRONT-INT-ATHENA-FLEET-BRIDGE" in records_by_id:
            base += 1.0
    if record.quest_id == "Q46" and "Q45" in records_by_id:
        base += 1.25
    return base


def resolve_first_present(records_by_id: dict[str, QuestRecord], candidates: tuple[str, ...]) -> QuestRecord | None:
    for quest_id in candidates:
        record = records_by_id.get(quest_id)
        if record is not None:
            return record
    return None


def merge_components(
    intent_source: QuestRecord,
    witness_source: QuestRecord,
    execution_source: QuestRecord,
    return_source: QuestRecord,
) -> dict[str, Any]:
    return {
        "intent64": dict(intent_source.address_components["intent64"]),
        "witness64": dict(witness_source.address_components["witness64"]),
        "execution64": dict(execution_source.address_components["execution64"]),
        "return64": dict(return_source.address_components["return64"]),
    }


def build_seeded_record(
    seed_id: str,
    hall_record: QuestRecord,
    temple_record: QuestRecord,
    label: str,
    used_addresses: set[str],
) -> QuestRecord:
    candidate_components = [
        merge_components(hall_record, hall_record, temple_record, temple_record),
        merge_components(hall_record, temple_record, hall_record, temple_record),
        merge_components(hall_record, hall_record, temple_record, hall_record),
    ]
    selected_components = None
    selected_address = ""
    for components in candidate_components:
        address = quest_address_from_components(components)
        if address not in used_addresses:
            selected_components = components
            selected_address = address
            break
    if selected_components is None:
        selected_components = candidate_components[0]
        selected_address = quest_address_from_components(selected_components)
    used_addresses.add(selected_address)
    target_surfaces = unique_list(
        path_like_items(hall_record.target_surfaces)
        + path_like_items(temple_record.target_surfaces)
        + [relpath(path) for path in DEEP_NETWORK_SURFACES[:2]]
    )[:12]
    record = QuestRecord(
        quest_id=seed_id,
        quest_address=selected_address,
        parent_address=f"{hall_record.quest_address} + {temple_record.quest_address}",
        title=label,
        objective=(
            f"Bridge `{hall_record.quest_id}` into `{temple_record.quest_id}` through one seeded adjacent address so "
            "the conductor can widen the live frontier without pretending to exhaust the full 64^4 lattice."
        ),
        why_now=(
            f"`{hall_record.quest_id}` is the live Hall-side frontier while `{temple_record.quest_id}` carries active Temple pressure, "
            "so one bridge packet yields more than broad unranked seeding."
        ),
        target_surfaces=target_surfaces,
        best_lane="bridge -> runtime -> replay -> restart",
        witness_needed=(
            "one seeded bridge packet, one active claim overlay, one receipt-bearing replay witness, and one restart seed "
            "back into the Hall or Temple front"
        ),
        writeback="manifest + queue",
        restart_seed=f"{hall_record.quest_id} -> {temple_record.quest_id} -> next seeded conductor bridge",
        status=SEED_STATUS,
        owner="",
        blockers=["docs_gate_blocked"] if detect_gate_blocked() else [],
        completion_evidence=[],
        source_board="conductor",
        address_components=selected_components,
        registration_kind="seeded",
        frontier_seed=f"{hall_record.quest_id}+{temple_record.quest_id}",
        source_fronts=[hall_record.quest_id, temple_record.quest_id],
        priority_score=CONDUCTOR_PRIORITY.get(seed_id, 80.0),
    )
    record.success_gate = success_gate_for_record(record)
    return record


def build_seeded_records(records_by_id: dict[str, QuestRecord]) -> list[QuestRecord]:
    used_addresses = {record.quest_address for record in records_by_id.values()}
    seeded: list[QuestRecord] = []
    for seed_id, hall_candidates, temple_candidates, label in SEED_PAIR_SPECS:
        hall_record = resolve_first_present(records_by_id, hall_candidates)
        temple_record = resolve_first_present(records_by_id, temple_candidates)
        if hall_record is None or temple_record is None:
            continue
        seeded.append(build_seeded_record(seed_id, hall_record, temple_record, label, used_addresses))
    return seeded


def active_front_records(records_by_id: dict[str, QuestRecord], gate_blocked: bool) -> list[QuestRecord]:
    selected: list[QuestRecord] = []
    for quest_id in ["Q42", "Q46", "TQ03", "TQ04", "TQ05", "TQ06"]:
        record = records_by_id.get(quest_id)
        if record is None:
            continue
        if record.status not in {"OPEN", "ACTIVE"}:
            continue
        if should_exclude_for_gate(record, gate_blocked):
            continue
        record.priority_score = priority_score_for_record(record, records_by_id)
        selected.append(record)
    return selected


def evidence_surfaces_for_record(record: QuestRecord, records_by_id: dict[str, QuestRecord]) -> list[str]:
    surfaces: list[str] = [relpath(GATE_STATUS_PATH), relpath(ACTIVE_RUN_PATH)]
    surfaces.extend(relpath(path) for path in DEEP_NETWORK_SURFACES)
    surfaces.extend(path_like_items(record.target_surfaces))
    if round_trip_required(record):
        surfaces.extend([relpath(ROUND_TRIP_CERTIFICATES_PATH), relpath(ROUND_TRIP_RECEIPT_PATH)])
    if record.quest_id == "Q42":
        for anchor_id in ["FRONT-INT-QSHRINK-CANONICAL-FAMILY", "FRONT-INT-ATHENA-FLEET-BRIDGE"]:
            anchor = records_by_id.get(anchor_id)
            if anchor:
                surfaces.extend(anchor.completion_evidence[:4])
    if record.quest_id in {"Q46", "ADV64-S02"}:
        surfaces.extend(
            [
                relpath(ATHENACHKA_PACKETS_PATH),
                relpath(ATHENACHKA_WAVE_STATE_PATH),
                relpath(ATHENACHKA_Q45_PROOF_PATH),
                relpath(ATHENACHKA_HALL_DOC_PATH),
            ]
        )
    if record.quest_id.startswith("TQ"):
        surfaces.append(relpath(TEMPLE_CRYSTAL_PATH))
    if record.registration_kind == "seeded":
        surfaces.extend(path_like_items(record.target_surfaces))
    return unique_list(surfaces)[:16]


def priority_reason_for_record(record: QuestRecord) -> str:
    if record.quest_id == "Q42":
        return "Highest Hall-side live frontier; QSHRINK Fractal carrythrough remains the first lawful active contraction."
    if record.quest_id == "Q46":
        return "Current Athenachka execution front, carried forward from the promoted Q45 proof anchor at the same 64^4 address."
    if record.quest_id.startswith("TQ"):
        return "Active Temple pressure that can emit Hall-facing writeback into the same conductor cycle."
    return "Seeded adjacent bridge packet widening the live frontier without bulk-filling the lattice."


def build_wave_packets(
    live_fronts: list[QuestRecord],
    seeded_records: list[QuestRecord],
    records_by_id: dict[str, QuestRecord],
) -> list[WavePacket]:
    gate_status = "BLOCKED" if detect_gate_blocked() else "READY"
    packets: list[WavePacket] = []
    for index, record in enumerate(live_fronts + seeded_records, start=1):
        record.priority_score = record.priority_score or CONDUCTOR_PRIORITY.get(record.quest_id, 50.0)
        record.frontier_seed = record.frontier_seed or record.quest_id
        record.success_gate = success_gate_for_record(record)
        packets.append(
            WavePacket(
                packet_id=f"ADV64-{index:02d}",
                wave_id=WAVE_ID,
                frontier_seed=record.frontier_seed,
                address_slice=[record.quest_address],
                priority_score=record.priority_score,
                max_parallel_claims=WAVE_CAPACITY,
                docs_gate_status=gate_status,
                evidence_surfaces=evidence_surfaces_for_record(record, records_by_id),
                success_gate=record.success_gate,
                assigned_owner=FLOATING_AGENTS[index - 1],
                source_front=record.quest_id,
                source_fronts=record.source_fronts or [record.quest_id],
                status="ACTIVE" if index <= WAVE_CAPACITY else "QUEUED",
                priority_reason=priority_reason_for_record(record),
                round_trip_certificate_id=record.round_trip_certificate_id,
                round_trip_class=record.round_trip_class,
            )
        )
    return packets


def close_non_wave_claims(active_packets: list[WavePacket]) -> list[str]:
    active_front_by_owner = {packet.assigned_owner: packet.source_front for packet in active_packets}
    released: list[str] = []
    for claim in swarm_board.load_board_claims():
        owner = claim.get("owner", "")
        if owner not in active_front_by_owner:
            continue
        if claim.get("status") != "active":
            continue
        if claim.get("frontier") == active_front_by_owner[owner]:
            continue
        swarm_board.create_or_update_claim(
            agent=owner,
            front=claim.get("frontier", ""),
            level=claim.get("level", ""),
            output_target=claim.get("output_target", ""),
            receipt=claim.get("receipt", ""),
            status="closed",
            message=(
                f"Closed during `{WAVE_ID}` synchronization because `{active_front_by_owner[owner]}` became the "
                "authoritative active claim for this agent."
            ),
            paths=claim.get("paths", []),
            claim_id=claim.get("claim_id"),
        )
        released.append(claim.get("claim_id", ""))
    return released


def claim_paths_for_packet(packet: WavePacket, records_by_id: dict[str, QuestRecord]) -> list[str]:
    record = records_by_id.get(packet.source_front)
    paths = []
    if record is not None:
        paths.extend(path_like_items(record.target_surfaces))
    paths.extend(packet.evidence_surfaces)
    paths.extend([relpath(CONDUCTOR_STATE_PATH), relpath(WAVE_PACKETS_PATH), relpath(MANIFEST_PATH)])
    return unique_list(paths)[:16]


def ensure_wave_claims(active_packets: list[WavePacket], records_by_id: dict[str, QuestRecord]) -> list[str]:
    receipt_relative = relpath(RECEIPT_PATH)
    close_non_wave_claims(active_packets)
    board_claims = swarm_board.load_board_claims()
    notes = swarm_board.load_notes()
    updated_fronts: list[str] = []
    for packet in active_packets:
        claim_paths = claim_paths_for_packet(packet, records_by_id)
        existing_claim = next(
            (
                claim
                for claim in board_claims
                if claim.get("owner") == packet.assigned_owner and claim.get("frontier") == packet.source_front
            ),
            None,
        )
        swarm_board.create_or_update_claim(
            agent=packet.assigned_owner,
            front=packet.source_front,
            level="framework",
            output_target="; ".join(claim_paths),
            receipt=receipt_relative,
            status="active",
            message=(
                f"Synchronized `{packet.source_front}` onto `{packet.assigned_owner}` for `{packet.wave_id}` at "
                f"`{packet.address_slice[0]}` with priority `{packet.priority_score:.2f}` while Docs gate is "
                f"`{packet.docs_gate_status}`."
            ),
            paths=claim_paths,
            claim_id=existing_claim.get("claim_id") if existing_claim else None,
        )
        existing_note = next(
            (
                note
                for note in notes
                if note.get("agent") == packet.assigned_owner
                and note.get("front") == packet.source_front
                and note.get("status") == "active"
            ),
            None,
        )
        if existing_note is None:
            swarm_board.create_note(
                agent=packet.assigned_owner,
                front=packet.source_front,
                status="active",
                message=(
                    f"Claimed `{packet.source_front}` as slot `{packet.packet_id}` in `{packet.wave_id}` and bound it "
                    f"to `{packet.address_slice[0]}`."
                ),
                paths=claim_paths[:8],
            )
        updated_fronts.append(packet.source_front)
    return updated_fronts


def update_claim_tracker(
    claims: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    records_by_front: dict[str, QuestRecord],
    cycle_index: int,
) -> dict[str, Any]:
    previous = load_previous_tracker()
    notes_by_front: dict[str, list[dict[str, Any]]] = {}
    for note in notes:
        notes_by_front.setdefault(note.get("front", ""), []).append(note)
    tracker: dict[str, Any] = {}
    for claim in claims:
        claim_id = claim["claim_id"]
        frontier = claim.get("frontier", "")
        note_hits = notes_by_front.get(frontier, [])
        receipt_text = (claim.get("receipt") or "").strip().replace("\\", "/")
        receipt_exists = bool(receipt_text) and (WORKSPACE_ROOT / receipt_text).exists()
        prior = previous.get(claim_id, {})
        last_claim_update = claim.get("updated_at", "")
        last_note_count = len(note_hits)
        note_count_changed = last_note_count != prior.get("last_note_count", 0)
        claim_update_changed = last_claim_update != prior.get("last_claim_update", "")
        receipt_changed = receipt_exists != prior.get("receipt_exists", False)
        inactive_cycles = 0 if (note_count_changed or claim_update_changed or receipt_changed) else prior.get("inactive_cycles", 0) + 1
        record = records_by_front.get(frontier)
        tracker[claim_id] = {
            "claim_id": claim_id,
            "frontier": frontier,
            "address": record.quest_address if record else "",
            "owner": claim.get("owner", ""),
            "source_front": frontier,
            "status": claim.get("status", ""),
            "claimed_at": claim.get("created_at", ""),
            "stale_after": f"cycle-{cycle_index + 1}",
            "receipt_pointer": receipt_text,
            "note_count": len(note_hits),
            "last_note_count": len(note_hits),
            "receipt_exists": receipt_exists,
            "last_claim_update": last_claim_update,
            "artifact_delta": False,
            "inactive_cycles": inactive_cycles,
            "stale": inactive_cycles >= STALE_SCAN_THRESHOLD and claim.get("status") == "active",
        }
    return tracker


def maybe_release_stale_claims(claim_tracker: dict[str, Any]) -> list[str]:
    board_claims = {claim["claim_id"]: claim for claim in swarm_board.load_board_claims()}
    released = []
    for claim_id, tracked in claim_tracker.items():
        if not tracked.get("stale"):
            continue
        claim = board_claims.get(claim_id)
        if not claim or claim.get("status") != "active":
            continue
        swarm_board.create_or_update_claim(
            agent=claim.get("owner", ""),
            front=claim.get("frontier", ""),
            level=claim.get("level", ""),
            output_target=claim.get("output_target", ""),
            receipt=claim.get("receipt", ""),
            status="open",
            message=claim.get("note", ""),
            paths=claim.get("paths", []),
            claim_id=claim_id,
        )
        released.append(claim_id)
    return released


def build_agent_state(next_frontier: str, records: list[QuestRecord], packets: list[WavePacket]) -> dict[str, Any]:
    terminal_statuses = {"PROMOTED", "BLOCKED", "SUPERSEDED"}
    answered = [record for record in records if record.status in terminal_statuses]
    promoted = [record for record in records if record.status == "PROMOTED"]
    blocked = [record for record in records if record.status == "BLOCKED"]
    superseded = [record for record in records if record.status == "SUPERSEDED"]
    board_claims = swarm_board.load_board_claims()
    packet_by_owner = {packet.assigned_owner: packet for packet in packets}
    active_claim_by_owner = {agent: "" for agent in FLOATING_AGENTS}
    for claim in board_claims:
        if claim.get("owner") in active_claim_by_owner and claim.get("status") == "active":
            active_claim_by_owner[claim["owner"]] = claim.get("frontier", "")
    agents = []
    for agent_id in FLOATING_AGENTS:
        packet = packet_by_owner.get(agent_id)
        agents.append(
            {
                "agent_id": agent_id,
                "active_claim": active_claim_by_owner.get(agent_id, ""),
                "assigned_packet_id": packet.packet_id if packet else "",
                "assigned_frontier_seed": packet.frontier_seed if packet else "",
                "assigned_address": packet.address_slice[0] if packet else "",
                "loop_count": 1 if packet else 0,
                "answered_count": len(answered),
                "promoted_count": len(promoted),
                "blocked_count": len(blocked),
                "superseded_count": len(superseded),
                "last_receipt": relpath(RECEIPT_PATH) if packet else "",
                "last_restart_seed": next_frontier if packet else "",
            }
        )
    return {
        "generated_at": utc_now(),
        "wave_id": WAVE_ID,
        "max_parallel_claims": WAVE_CAPACITY,
        "agents": agents,
    }


def build_loop_state(
    records: list[QuestRecord],
    next_frontier: str,
    claim_tracker: dict[str, Any],
    cycle_index: int,
    seeded_records: list[QuestRecord],
) -> dict[str, Any]:
    terminal_statuses = {"PROMOTED", "BLOCKED", "SUPERSEDED"}
    answered = [record for record in records if record.status in terminal_statuses]
    promoted = [record for record in records if record.status == "PROMOTED"]
    blocked = [record for record in records if record.status == "BLOCKED"]
    superseded = [record for record in records if record.status == "SUPERSEDED"]
    open_records = [record for record in records if record.status == "OPEN"]
    active_records = [record for record in records if record.status == "ACTIVE"]
    active_claim_count = sum(1 for tracked in claim_tracker.values() if tracked.get("status") == "active")
    return {
        "generated_at": utc_now(),
        "cycle_index": cycle_index,
        "answer_space": 64**4,
        "registered_quest_count": len(records),
        "answered_count": len(answered),
        "promoted_count": len(promoted),
        "blocked_count": len(blocked),
        "superseded_count": len(superseded),
        "open_count": len(open_records),
        "active_front_count": len(active_records),
        "seeded_count": len(seeded_records),
        "active_claim_count": active_claim_count,
        "docs_gate_blocked": detect_gate_blocked(),
        "next_frontier": next_frontier,
        "wave_id": WAVE_ID,
        "wave_capacity": WAVE_CAPACITY,
        "stale_release_after_inactive_cycles": STALE_SCAN_THRESHOLD,
        "round_trip_governed_front_count": sum(1 for record in records if record.round_trip_required),
    }


def build_conductor_state(
    packets: list[WavePacket],
    records_by_id: dict[str, QuestRecord],
    seeded_records: list[QuestRecord],
    next_frontier: str,
    cycle_index: int,
) -> dict[str, Any]:
    ranking = [
        {
            "packet_id": packet.packet_id,
            "source_front": packet.source_front,
            "frontier_seed": packet.frontier_seed,
            "priority_score": packet.priority_score,
            "assigned_owner": packet.assigned_owner,
            "address": packet.address_slice[0],
            "priority_reason": packet.priority_reason,
        }
        for packet in packets
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "wave_id": WAVE_ID,
        "cycle_index": cycle_index,
        "docs_gate_status": "BLOCKED" if detect_gate_blocked() else "READY",
        "next_frontier": next_frontier,
        "max_parallel_claims": WAVE_CAPACITY,
        "stale_release_after_inactive_cycles": STALE_SCAN_THRESHOLD,
        "proof_anchors": {
            "q42_bundle_pair": ["FRONT-INT-QSHRINK-CANONICAL-FAMILY", "FRONT-INT-ATHENA-FLEET-BRIDGE"],
            "athenachka_carrythrough": ["Q45", "Q46"],
        },
        "round_trip_registry_path": relpath(ROUND_TRIP_CERTIFICATES_PATH),
        "round_trip_receipt_path": relpath(ROUND_TRIP_RECEIPT_PATH),
        "round_trip_governed_fronts": list(ROUND_TRIP_GOVERNED_FRONTS),
        "round_trip_transform_laws": list(ROUND_TRIP_TRANSFORM_SPECS),
        "deep_network_surfaces": [relpath(path) for path in DEEP_NETWORK_SURFACES],
        "seeded_registration_ids": [record.quest_id for record in seeded_records],
        "wave_ranking": ranking,
        "packets": [asdict(packet) for packet in packets],
        "shared_address_proof_anchor": {
            "proof_front": "Q45" if "Q45" in records_by_id else "",
            "execution_front": "Q46" if "Q46" in records_by_id else "",
            "shared_address": records_by_id["Q46"].quest_address if "Q46" in records_by_id else "",
        },
    }


def render_manifest(
    loop_state: dict[str, Any],
    records: list[QuestRecord],
    seeded_records: list[QuestRecord],
    packets: list[WavePacket],
    next_frontier: str,
    released_claims: list[str],
) -> str:
    hall_open = [record for record in records if record.source_board == "hall" and record.status == "OPEN"]
    temple_pressure = [record for record in records if record.source_board == "temple" and record.status in {"OPEN", "ACTIVE"}]
    stale_claims = [claim_id for claim_id, tracked in load_previous_tracker().items() if tracked.get("stale")]
    gate_status = "BLOCKED" if loop_state["docs_gate_blocked"] else "READY"
    lines = [
        "# ADVENTURER 64^4 STATE",
        "",
        f"generated_at: {loop_state['generated_at']}",
        f"derivation_version: {DERIVATION_VERSION}",
        f"docs_gate: {gate_status}",
        f"answer_space: {loop_state['answer_space']}",
        f"registered_quests: {loop_state['registered_quest_count']}",
        f"answered_count: {loop_state['answered_count']}",
        f"promoted_count: {loop_state['promoted_count']}",
        f"blocked_count: {loop_state['blocked_count']}",
        f"superseded_count: {loop_state['superseded_count']}",
        f"open_count: {loop_state['open_count']}",
        f"active_front_count: {loop_state['active_front_count']}",
        f"seeded_count: {loop_state['seeded_count']}",
        f"active_claim_count: {loop_state['active_claim_count']}",
        f"cycle_index: {loop_state['cycle_index']}",
        f"wave_id: {loop_state['wave_id']}",
        f"wave_capacity: {loop_state['wave_capacity']}",
        f"round_trip_governed_front_count: {loop_state['round_trip_governed_front_count']}",
        f"next_frontier: {next_frontier}",
        "",
        "## Current Conductor Wave",
        "",
    ]
    for index, packet in enumerate(packets, start=1):
        lines.append(
            f"{index}. `{packet.source_front}` :: `{packet.address_slice[0]}` :: owner=`{packet.assigned_owner}` :: "
            f"score=`{packet.priority_score:.2f}` :: round_trip=`{packet.round_trip_class or 'n/a'}`"
        )
    lines.extend(["", "## Open Hall Quests", ""])
    for record in hall_open[:12]:
        owner = record.owner or "unclaimed"
        lines.append(f"- `{record.quest_id}` :: {record.title} :: `{record.quest_address}` :: owner=`{owner}`")
    lines.extend(["", "## Active Temple Pressure", ""])
    for record in temple_pressure[:12]:
        lines.append(f"- `{record.quest_id}` :: {record.title} :: `{record.status}` :: `{record.quest_address}`")
    lines.extend(["", "## Seeded Adjacent Registrations", ""])
    for record in seeded_records:
        lines.append(
            f"- `{record.quest_id}` :: `{record.quest_address}` :: parents=`{', '.join(record.source_fronts)}` :: "
            f"lane=`{record.best_lane}`"
        )
    lines.extend(
        [
            "",
            "## Claim Staleness",
            "",
            f"- release_after_inactive_cycles: `{STALE_SCAN_THRESHOLD}`",
            f"- released_this_pass: {', '.join(f'`{item}`' for item in released_claims) if released_claims else 'none'}",
            f"- stale_claims_prior_state: {', '.join(f'`{item}`' for item in stale_claims) if stale_claims else 'none'}",
            "",
            "## Loop Law",
            "",
            "- Anchor: read gate, Hall, Temple, active run, change-feed, and deeper-network control surfaces.",
            "- Detect: prioritize `Q42`, then the `Q45 -> Q46` Athenachka carrythrough, then Hall-emitting Temple fronts, then seeded adjacents.",
            "- Validate: reject blocked Docs work while local lawful fronts remain.",
            "- Encode: keep every registered quest or seeded bridge on one lazy `A.B.C.D` address.",
            "- Round trip: a conversion is valid only if it preserves law or explicitly names the loss through `RoundTripCertificate_v0`.",
            "- Undertake: only mark a slice complete when artifact, board update, writeback, and restart seed all land.",
            "- Restart: reopen stale claims after one inactive scheduler cycle and rescan Hall plus Temple after every terminal answer state.",
        ]
    )
    return "\n".join(lines)


def render_hall_doc(
    loop_state: dict[str, Any],
    records: list[QuestRecord],
    seeded_records: list[QuestRecord],
    packets: list[WavePacket],
    next_frontier: str,
) -> str:
    gate_status = "BLOCKED" if loop_state["docs_gate_blocked"] else "READY"
    registered_slice = sort_records(records)
    lines = [
        "# Adventurer 64^4 Quest Loop",
        "",
        "This document defines the hybrid-conductor Adventurer loop for the live 64^4 lattice.",
        "It widens the frontier lazily, assigns up to eight floating-agent claims, and keeps the Google Docs gate honest.",
        "",
        "## Canonical Surfaces",
        "",
        f"- Hall quest board: `{relpath(QUEST_BOARD_PATH)}`",
        f"- Hall requests board: `{relpath(REQUESTS_BOARD_PATH)}`",
        f"- Hall change feed: `{relpath(CHANGE_FEED_PATH)}`",
        f"- Temple quest board: `{relpath(TEMPLE_BOARD_PATH)}`",
        f"- Temple 64 crystal: `{relpath(TEMPLE_CRYSTAL_PATH)}`",
        f"- Gate status: `{relpath(GATE_STATUS_PATH)}`",
        f"- Active run: `{relpath(ACTIVE_RUN_PATH)}`",
        f"- Conductor state: `{relpath(CONDUCTOR_STATE_PATH)}`",
        f"- Wave packets: `{relpath(WAVE_PACKETS_PATH)}`",
        f"- Round-trip registry: `{relpath(ROUND_TRIP_CERTIFICATES_PATH)}`",
        "",
        "## Address Contract",
        "",
        "- `QuestAddress = A.B.C.D`",
        "- `A = Intent64 = Domain x Move x Lens`",
        "- `B = Witness64 = WitnessClass x Surface x Lane`",
        "- `C = Execution64 = Scope x Method x Artifact`",
        "- `D = Return64 = Verify x Writeback x Restart`",
        "",
        "## Agent Law",
        "",
        f"- shared floating agents: `{', '.join(FLOATING_AGENTS)}`",
        f"- one active claim per address and up to `{WAVE_CAPACITY}` active claims in `{WAVE_ID}`",
        f"- stale claims reopen after `{STALE_SCAN_THRESHOLD}` inactive scheduler cycle",
        "- terminal answer states are `PROMOTED`, `BLOCKED`, and `SUPERSEDED`",
        f"- docs gate on this pass: `{gate_status}`",
        "",
        "## Current Conductor Wave",
        "",
    ]
    for packet in packets:
        lines.append(
            f"- `{packet.packet_id}` :: `{packet.source_front}` :: `{packet.address_slice[0]}` :: "
            f"owner=`{packet.assigned_owner}` :: score=`{packet.priority_score:.2f}` :: "
            f"round_trip=`{packet.round_trip_class or 'n/a'}`"
        )
    lines.extend(
        [
            "",
            "## Registered Quest Slice",
            "",
            "| Quest | Address | Board | Status | Owner | Kind |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in registered_slice[:24]:
        lines.append(
            f"| `{record.quest_id}` | `{record.quest_address}` | `{record.source_board}` | `{record.status}` | "
            f"`{record.owner or 'unclaimed'}` | `{record.registration_kind}` |"
        )
    for record in seeded_records:
        lines.append(
            f"| `{record.quest_id}` | `{record.quest_address}` | `{record.source_board}` | `{record.status}` | "
            f"`{record.owner or 'unclaimed'}` | `{record.registration_kind}` |"
        )
    lines.extend(
        [
            "",
            "## Proof Anchors",
            "",
            "- `Q42` routes through the atlas-backed `qshrink` and `athena_fleet` bundle pair before widening laterally.",
            "- `Q45` remains the promoted proof anchor that hands the shared `A22.B27.C49.D43` coordinate forward to live `Q46` execution.",
            "- `RoundTripCertificate_v0` governs the first conversion membrane across `Q42`, `Q46`, and `TQ04` without replacing the Hall four-witness completion law.",
            "",
            "## Round-Trip Membrane",
            "",
            f"- governed fronts: `{', '.join(ROUND_TRIP_GOVERNED_FRONTS)}`",
            f"- registry: `{relpath(ROUND_TRIP_CERTIFICATES_PATH)}`",
            f"- receipt: `{relpath(ROUND_TRIP_RECEIPT_PATH)}`",
            "",
            "## Seeded Adjacent Slice",
            "",
        ]
    )
    for record in seeded_records:
        lines.append(
            f"- `{record.quest_id}` :: `{record.quest_address}` :: parents=`{', '.join(record.source_fronts)}` :: restart=`{record.restart_seed}`"
        )
    lines.extend(
        [
            "",
            "## Restart Seed",
            "",
            f"- current lawful frontier: `{next_frontier}`",
            f"- current wave: `{WAVE_ID}`",
            "- keep `Q02` suppressed while the Docs gate stays blocked and local lawful work remains",
            "- if the Hall runs out of feasible open work, emit a new seeded bridge before idling instead of pretending the full 64^4 field has been traversed",
        ]
    )
    return "\n".join(lines)


def render_receipt(
    next_frontier: str,
    packets: list[WavePacket],
    seeded_records: list[QuestRecord],
    synced_fronts: list[str],
    round_trip_registry: dict[str, Any],
) -> str:
    lines = [
        "# 2026-03-13 Adventurer 64^4 Hybrid Conductor",
        "",
        "## Outcome",
        "",
        "Installed the first hybrid-conductor Adventurer layer over the live 64^4 quest lattice.",
        "",
        "## Machine Artifacts",
        "",
        f"- `{relpath(QUEST_REGISTRY_PATH)}`",
        f"- `{relpath(AGENT_STATE_PATH)}`",
        f"- `{relpath(CLAIM_TRACKER_PATH)}`",
        f"- `{relpath(LOOP_STATE_PATH)}`",
        f"- `{relpath(CONDUCTOR_STATE_PATH)}`",
        f"- `{relpath(WAVE_PACKETS_PATH)}`",
        f"- `{relpath(ROUND_TRIP_CERTIFICATES_PATH)}`",
        f"- `{relpath(ROUND_TRIP_RECEIPT_PATH)}`",
        f"- `{relpath(MANIFEST_PATH)}`",
        f"- `{relpath(HALL_DOC_PATH)}`",
        "",
        "## Wave Contract",
        "",
        f"- wave_id: `{WAVE_ID}`",
        f"- max_parallel_claims: `{WAVE_CAPACITY}`",
        f"- synced_front_count: `{len(synced_fronts)}`",
        f"- next_frontier: `{next_frontier}`",
        f"- seeded_adjacent_count: `{len(seeded_records)}`",
        "",
        "## Active Claim Overlay",
        "",
    ]
    for packet in packets:
        lines.append(
            f"- `{packet.source_front}` :: owner=`{packet.assigned_owner}` :: address=`{packet.address_slice[0]}` :: "
            f"status=`{packet.status}`"
        )
    lines.extend(
        [
            "",
            "## Gate Honesty",
            "",
            "- Live Google Docs remain blocked until OAuth files exist.",
            f"- blocker surface: `{relpath(LIVE_DOCS_GATE_STATUS_PATH)}`",
            "",
            "## Hall Completion Law",
            "",
            "- one witness-bearing artifact",
            "- one board or queue update",
            "- one writeback into a manifest, queue, or family surface",
            "- one restart seed",
            "",
            "## Round-Trip Membrane",
            "",
            f"- governed fronts: `{', '.join(round_trip_registry['governed_fronts'])}`",
            f"- transform laws: `{', '.join(item['transform_family'] for item in round_trip_registry['transform_laws'])}`",
            "- law: conversions must preserve the protected invariant bundle or explicitly name the loss",
        ]
    )
    return "\n".join(lines)


def render_round_trip_receipt(round_trip_registry: dict[str, Any]) -> str:
    lines = [
        "# 2026-03-13 RoundTripCertificate v0",
        "",
        "## Constitutional Law",
        "",
        "A conversion is valid only if it preserves law or explicitly names the loss.",
        "",
        "## Protected Invariant Bundle",
        "",
        f"- `{', '.join(round_trip_registry['protected_invariant_bundle'])}`",
        f"- required route minimum: `{', '.join(round_trip_registry['required_route_min'])}`",
        "",
        "## Governed Fronts",
        "",
    ]
    for certificate in round_trip_registry["governed_certificates"]:
        lines.append(
            f"- `{certificate['quest_id']}` :: class=`{certificate['round_trip_class']}` :: "
            f"lawful=`{certificate['lawful']}` :: transform=`{certificate['transform_family']}`"
        )
    lines.extend(
        [
            "",
            "## Transform Laws",
            "",
        ]
    )
    for transform_law in round_trip_registry["transform_laws"]:
        lines.append(
            f"- `{transform_law['transform_family']}` :: allowed=`{', '.join(transform_law['allowed_classes'])}`"
        )
    lines.extend(
        [
            "",
            "## Illegal Loss Tests",
            "",
        ]
    )
    for loss_test in round_trip_registry["illegal_loss_tests"]:
        lines.append(f"- `{loss_test['test_id']}` :: {loss_test['description']}")
    lines.extend(
        [
            "",
            "## Gate Honesty",
            "",
            f"- docs gate: `{round_trip_registry['docs_gate_status']}`",
            "- local evidence only while OAuth files remain missing",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive the Adventurer 64^4 hybrid conductor state.")
    parser.add_argument("--agent-id", default=FLOATING_AGENTS[0])
    parser.add_argument("--bootstrap-claim", action="store_true")
    parser.add_argument("--sync-wave-claims", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    previous_loop = load_previous_loop_state()
    cycle_index = int(previous_loop.get("cycle_index", 0)) + 1

    base_records = build_records()
    base_records_by_front = {record.quest_id: record for record in base_records}
    claim_tracker = update_claim_tracker(
        claims=load_existing_claims(),
        notes=load_existing_notes(),
        records_by_front=base_records_by_front,
        cycle_index=cycle_index,
    )
    released_claims = maybe_release_stale_claims(claim_tracker)
    if released_claims:
        base_records = build_records()
        base_records_by_front = {record.quest_id: record for record in base_records}
        claim_tracker = update_claim_tracker(
            claims=load_existing_claims(),
            notes=load_existing_notes(),
            records_by_front=base_records_by_front,
            cycle_index=cycle_index,
        )

    gate_blocked = detect_gate_blocked()
    records_by_id = {record.quest_id: record for record in base_records}
    round_trip_registry = build_round_trip_registry(records_by_id)
    live_fronts = active_front_records(records_by_id, gate_blocked)
    seeded_records = build_seeded_records(records_by_id)
    records_by_id.update({record.quest_id: record for record in seeded_records})
    packets = build_wave_packets(live_fronts, seeded_records, records_by_id)

    synced_fronts: list[str] = []
    if args.bootstrap_claim or args.sync_wave_claims:
        synced_fronts = ensure_wave_claims(packets, records_by_id)
        base_records = build_records()
        records_by_id = {record.quest_id: record for record in base_records}
        round_trip_registry = build_round_trip_registry(records_by_id)
        seeded_records = build_seeded_records(records_by_id)
        records_by_id.update({record.quest_id: record for record in seeded_records})
        live_fronts = active_front_records(records_by_id, gate_blocked)
        packets = build_wave_packets(live_fronts, seeded_records, records_by_id)
        claim_tracker = update_claim_tracker(
            claims=load_existing_claims(),
            notes=load_existing_notes(),
            records_by_front=records_by_id,
            cycle_index=cycle_index,
        )

    all_records = sort_records(base_records + seeded_records)
    next_frontier = select_next_frontier(base_records, gate_blocked)
    agent_state = build_agent_state(next_frontier=next_frontier, records=all_records, packets=packets)
    loop_state = build_loop_state(
        records=all_records,
        next_frontier=next_frontier,
        claim_tracker=claim_tracker,
        cycle_index=cycle_index,
        seeded_records=seeded_records,
    )
    conductor_state = build_conductor_state(
        packets=packets,
        records_by_id=records_by_id,
        seeded_records=seeded_records,
        next_frontier=next_frontier,
        cycle_index=cycle_index,
    )
    payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "gate_status_path": relpath(GATE_STATUS_PATH),
        "active_run_path": relpath(ACTIVE_RUN_PATH),
        "requests_board_path": relpath(REQUESTS_BOARD_PATH),
        "temple_crystal_path": relpath(TEMPLE_CRYSTAL_PATH),
        "conductor_state_path": relpath(CONDUCTOR_STATE_PATH),
        "wave_packets_path": relpath(WAVE_PACKETS_PATH),
        "round_trip_certificates_path": relpath(ROUND_TRIP_CERTIFICATES_PATH),
        "change_feed_signals": load_change_feed_signals(),
        "next_frontier": next_frontier,
        "current_first_wave": CURRENT_FIRST_WAVE,
        "quest_records": [asdict(record) for record in all_records],
    }
    write_json(QUEST_REGISTRY_PATH, payload)
    write_json(AGENT_STATE_PATH, agent_state)
    write_json(LOOP_STATE_PATH, loop_state)
    write_json(CONDUCTOR_STATE_PATH, conductor_state)
    write_json(ROUND_TRIP_CERTIFICATES_PATH, round_trip_registry)
    write_json(
        WAVE_PACKETS_PATH,
        {
            "generated_at": utc_now(),
            "wave_id": WAVE_ID,
            "docs_gate_status": "BLOCKED" if gate_blocked else "READY",
            "packets": [asdict(packet) for packet in packets],
        },
    )
    write_text(MANIFEST_PATH, render_manifest(loop_state, base_records, seeded_records, packets, next_frontier, released_claims))
    write_text(HALL_DOC_PATH, render_hall_doc(loop_state, base_records, seeded_records, packets, next_frontier))
    write_text(RECEIPT_PATH, render_receipt(next_frontier, packets, seeded_records, synced_fronts, round_trip_registry))
    write_text(ROUND_TRIP_RECEIPT_PATH, render_round_trip_receipt(round_trip_registry))
    claim_tracker = update_claim_tracker(
        claims=load_existing_claims(),
        notes=load_existing_notes(),
        records_by_front=records_by_id,
        cycle_index=cycle_index,
    )
    tracker_payload = {
        "generated_at": utc_now(),
        "wave_id": WAVE_ID,
        "release_after_inactive_cycles": STALE_SCAN_THRESHOLD,
        "claims": claim_tracker,
        "released_claims": released_claims,
    }
    write_json(CLAIM_TRACKER_PATH, tracker_payload)
    print(f"Wrote quest registry: {QUEST_REGISTRY_PATH}")
    print(f"Wrote conductor state: {CONDUCTOR_STATE_PATH}")
    print(f"Wrote wave packets: {WAVE_PACKETS_PATH}")
    print(f"Wrote round-trip registry: {ROUND_TRIP_CERTIFICATES_PATH}")
    print(f"Next frontier: {next_frontier}")
    print(f"Synced fronts: {', '.join(synced_fronts) if synced_fronts else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
