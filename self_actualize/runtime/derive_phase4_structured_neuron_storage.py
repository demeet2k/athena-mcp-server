from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.phase4_contracts import (
    BodyRecord,
    ExplorationQueryRecord,
    KernelRecord,
    NeglectSignalRecord,
    NodeRecord,
    PairRecord,
    Phase4Dashboard,
    ReplayReceiptRecord,
    RootAnchorRecord,
    ShortcutRecord,
    WaveRecord,
    WeaveCandidateRecord,
)
from self_actualize.runtime.phase4_query_engine import (
    fire,
    locate,
    neglect,
    promote,
    route,
    score_pair_for_objective,
    shorten,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
DEEP_ROOT = (
    MYCELIUM_BRAIN_ROOT
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
MATRIX_ROOT = DEEP_ROOT / "05_MATRIX_16X16"

DERIVATION_VERSION = "2026-03-12.phase4-v1"
DERIVATION_COMMAND = (
    "python -m self_actualize.runtime.derive_phase4_structured_neuron_storage"
)
PHASE4_LAW = (
    "Phase4 = BodyRegistry + KernelRegistry + NodeRegistry + PairRegistry + "
    "TopKWaveSlices + ShortcutRegistry + ExplorationQueries + NeglectSignals + "
    "WeaveCandidates + ReplayReceipts"
)
DIRECT_BODY_SYNAPSES = [
    {
        "commissure_id": "CS-001",
        "source_body_id": "A16",
        "source_root": "Athena FLEET",
        "target_body_id": "A06",
        "target_root": "Voynich",
        "bridge_class": "crystal synapse",
        "dispatch_score": 8.104,
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "CS-002",
        "source_body_id": "A06",
        "source_root": "Voynich",
        "target_body_id": "A09",
        "target_root": "QSHRINK - ATHENA (internal use)",
        "bridge_class": "crystal synapse",
        "dispatch_score": 7.982,
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "CS-003",
        "source_body_id": "A16",
        "source_root": "Athena FLEET",
        "target_body_id": "A15",
        "target_root": "ORGIN",
        "bridge_class": "crystal synapse",
        "dispatch_score": 7.941,
        "proof_state": "NEAR",
    },
]

DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
CANONICAL_SOURCES_PATH = DEEP_ROOT / "10_LEDGERS" / "01_CANONICAL_SOURCES.md"
GENERATED_MANIFEST_PATH = DEEP_ROOT / "10_LEDGERS" / "generated_manifest.json"
STATION_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_station_registry.json"
COMMISSURE_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_commissure_ledger.json"
WEIGHT_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"
TUNNEL_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_zpoint_tunnels.json"
NEURON_LIBRARY_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "NEURON_LIBRARY.md"
GRAND_CENTRAL_OVERVIEW_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md"
)
PHASE3_OVERVIEW_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "17_PHASE3_SELF_HOSTING_KERNEL.md"
AFFECTIVE_FIELD_OVERVIEW_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md"
)
WAVE_SCHEMA_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "11_AFFECTIVE_EPISTEMIC_NEURON_WAVE_SCHEMA.md"
)
VIRTUAL_SWARM_SPEC_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "08_VIRTUAL_SWARM_SPEC_16X16.md"
)
SELF_HOSTING_SCHEMA_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "12_SELF_HOSTING_KERNEL_SCHEMA.md"
)
GRAND_CENTRAL_SCHEMA_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "11_GRAND_CENTRAL_STATION_SCHEMA.md"
)

BODY_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_body_registry.json"
KERNEL_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_kernel_registry.json"
NODE_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_node_registry.json"
PAIR_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_pair_registry.json"
WAVE_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_wave_registry.json"
SHORTCUT_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_shortcut_registry.json"
QUERY_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_exploration_queries.json"
NEGLECT_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_neglect_signals.json"
WEAVE_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
REPLAY_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_replay_receipts.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase4_structured_neuron_storage_dashboard.json"

BODY_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_body_registry.json"
KERNEL_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_kernel_registry.json"
NODE_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_node_registry.json"
PAIR_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_pair_registry.json"
WAVE_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_wave_registry.json"
SHORTCUT_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_shortcut_registry.json"
QUERY_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_exploration_queries.json"
NEGLECT_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_neglect_signals.json"
WEAVE_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_weave_candidates.json"
REPLAY_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "phase4_replay_receipts.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / "phase4_structured_neuron_storage_dashboard.json"

DEEP_KERNEL_JSON_PATH = MATRIX_ROOT / "phase4_kernel_registry.json"
DEEP_PAIR_JSON_PATH = MATRIX_ROOT / "phase4_pair_registry.json"
DEEP_PAIR_FIELD_MD_PATH = MATRIX_ROOT / "15_phase4_structured_pair_field.md"

SCHEMA_STORAGE_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "13_PHASE4_STRUCTURED_NEURON_STORAGE_SCHEMA.md"
)
SCHEMA_QUERY_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "14_PHASE4_SHORTCUT_AND_QUERY_SCHEMA.md"
)
OVERVIEW_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "18_PHASE4_STRUCTURED_NEURON_STORAGE.md"
)
EDGE_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "PHASE4_STRUCTURED_NEURON_EDGES.md"
BODY_POINTERS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_BODY_POINTERS.md"
)
QUERY_PRESETS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_EXPLORATION_QUERY_PRESETS.md"
)
DASHBOARD_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "PHASE4_STRUCTURED_NEURON_STORAGE_DASHBOARD.md"
)
LEDGER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "25_PHASE4_STRUCTURED_NEURON_STORAGE_LEDGER.md"
)
SHORTCUTS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "26_PHASE4_SHORTCUT_REGISTRY.md"
)
NEGLECT_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "27_PHASE4_NEGLECT_SIGNAL_LEDGER.md"
)
WEAVE_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "28_PHASE4_WEAVE_CANDIDATE_LEDGER.md"
)
REPLAY_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "29_PHASE4_REPLAY_RECEIPT_LEDGER.md"
)
RUNTIME_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "nervous_system" / "26_phase4_structured_neuron_storage_runtime.md"
)
RECEIPT_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_phase4_structured_neuron_storage.md"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    return match.group(1) if match else "UNKNOWN"


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


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
        if line.startswith("## ") and "Root Anchors" not in line and "Live Directory Bodies" not in line:
            section = ""
        if section == "bodies" and line.startswith("| A"):
            parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
            if len(parts) >= 5:
                bodies.append(
                    {
                        "body_id": parts[0],
                        "root": parts[1],
                        "indexed_count": int(parts[2]),
                        "status": parts[3],
                        "current_role": parts[4],
                    }
                )
        if section == "anchors" and line.startswith("| R"):
            parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
            if len(parts) >= 5:
                anchors.append(
                    {
                        "root_id": parts[0],
                        "root": parts[1],
                        "indexed_count": int(parts[2]),
                        "status": parts[3],
                        "current_role": parts[4],
                    }
                )
    return bodies, anchors


def parse_canonical_sources(markdown: str) -> List[Dict[str, str]]:
    pattern = re.compile(
        r"- `(?P<index>\d{2})` (?P<title>.+?) \[(?P<element>\w+)\]: "
        r"(?P<lemma>.+?)\. Cluster: (?P<cluster>.+?)\. Source hint: `(?P<hint>.+?)`\."
    )
    sources: List[Dict[str, str]] = []
    for line in markdown.splitlines():
        match = pattern.match(line.strip())
        if match:
            sources.append(match.groupdict())
    return sources


def parse_list_block(lines: List[str], start: int, prefix: str) -> Tuple[List[str], int]:
    items: List[str] = []
    index = start + 1
    while index < len(lines) and lines[index].startswith(prefix):
        items.append(lines[index][len(prefix) :].strip())
        index += 1
    return items, index


def parse_neuron_library(markdown: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for block in markdown.split("```yaml")[1:]:
        payload = block.split("```", 1)[0]
        lines = [line.rstrip() for line in payload.splitlines() if line.strip()]
        record: Dict[str, Any] = {
            "source_paths": [],
            "operator_family": [],
            "metro_lines": [],
            "next_synapses": [],
            "witness_direct_support": [],
            "replay_hint": "",
        }
        index = 0
        while index < len(lines):
            line = lines[index]
            if line.startswith("neuron_id:"):
                record["neuron_id"] = line.split(":", 1)[1].strip()
            elif line.startswith("title:"):
                record["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("region:"):
                record["region"] = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                record["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("seed_claim:"):
                record["seed_claim"] = line.split(":", 1)[1].strip()
            elif line.startswith("source_paths:"):
                items, index = parse_list_block(lines, index, "  - ")
                record["source_paths"] = items
                continue
            elif line.startswith("operator_family:"):
                items, index = parse_list_block(lines, index, "  - ")
                record["operator_family"] = items
                continue
            elif line.startswith("metro_lines:"):
                items, index = parse_list_block(lines, index, "  - ")
                record["metro_lines"] = items
                continue
            elif line.startswith("next_synapses:"):
                items, index = parse_list_block(lines, index, "  - ")
                record["next_synapses"] = items
                continue
            elif line.startswith("witness:"):
                index += 1
                while index < len(lines) and lines[index].startswith("  "):
                    sub = lines[index]
                    if sub.startswith("  direct_support:"):
                        items, index = parse_list_block(lines, index, "    - ")
                        record["witness_direct_support"] = items
                        continue
                    if sub.startswith("  replay_hint:"):
                        record["replay_hint"] = sub.split(":", 1)[1].strip()
                    index += 1
                continue
            index += 1
        if record.get("neuron_id"):
            records.append(record)
    return records


def hemisphere_from_element(element: str) -> str:
    if element in {"Air", "Earth"}:
        return "left"
    if element in {"Fire", "Water"}:
        return "right"
    return "bilateral"


def tract_code(tract: str) -> str:
    return {
        "address": "GCA",
        "relation": "GCT",
        "chamber": "GCC",
        "replay": "GCP",
    }.get(tract, "GCT")


def determine_kernel_tract(body_tract: str, title: str, cluster: str) -> str:
    key = re.sub(r"[^a-z0-9]+", " ", f"{title} {cluster}".lower())
    if any(token in key for token in ["boundary", "ontology", "proof", "kernel", "zero point"]):
        return "chamber"
    if any(token in key for token in ["helical", "self repair", "manuscript", "voynich", "torat"]):
        return "replay"
    if any(token in key for token in ["routing", "rotation", "network", "quantum", "computing"]):
        return "relation"
    return body_tract


def determine_pair_tract(row: Dict[str, Any], col: Dict[str, Any], relation: str, title: str) -> str:
    key = re.sub(r"[^a-z0-9]+", " ", f"{relation} {title}".lower())
    if any(token in key for token in ["boundary", "quarantine", "contradiction", "proof"]):
        return "GCC"
    if any(token in key for token in ["restart", "repair", "replay", "memory", "continuity"]):
        return "GCP"
    if row["hemisphere_bias"] == col["hemisphere_bias"] == "left":
        return "GCA"
    return "GCT"


def determine_pair_dock(row: Dict[str, Any], col: Dict[str, Any], relation: str, tract: str) -> str:
    key = re.sub(
        r"[^a-z0-9]+",
        " ",
        f"{relation} {row['source_title']} {col['source_title']}".lower(),
    )
    if any(token in key for token in ["fleet", "promotion", "lift", "departure", "publish"]):
        return "GCX"
    if any(token in key for token in ["restart", "repair", "boundary", "quarantine", "contradiction"]):
        return "GCZ"
    if tract == "GCP":
        return "GCP"
    return "GCW"


def determine_pair_lines(row: Dict[str, Any], col: Dict[str, Any], relation: str, dock: str) -> List[str]:
    lines: List[str] = []
    key = re.sub(r"[^a-z0-9]+", " ", relation.lower())
    if any(token in key for token in ["zero", "restart", "seed", "origin"]) or {"K09", "K14"} & {
        row["kernel_id"],
        col["kernel_id"],
    }:
        lines.append("Origin")
    if row["element"] in {"Air", "Earth"} or col["element"] in {"Air", "Earth"}:
        lines.append("Crystal")
    if dock in {"GCW", "GCX"} or any(
        token in key for token in ["route", "translate", "bridge", "transfer", "rotation"]
    ):
        lines.append("Transit")
    if dock in {"GCZ", "GCP"} or any(
        token in key for token in ["boundary", "govern", "constraint", "repair", "replay"]
    ):
        lines.append("Governance")
    if not lines:
        lines.append("Transit")
    return sorted(set(lines))


def compute_charge_seed(
    row: Dict[str, Any],
    col: Dict[str, Any],
    relation: str,
    appendices: List[str],
) -> Dict[str, float]:
    relation_key = re.sub(r"[^a-z0-9]+", " ", relation.lower())
    elements = {row["element"], col["element"]}
    emotion = 0.32 + (0.22 if "Fire" in elements else 0.0) + (0.12 if "Water" in elements else 0.0)
    feeling = 0.30 + (0.18 if "Water" in elements else 0.0) + (0.08 if "Earth" in elements else 0.0)
    knowledge = 0.30 + (0.22 if "Air" in elements else 0.0) + (0.18 if "Earth" in elements else 0.0)
    desire = 0.28 + (0.18 if "Fire" in elements else 0.0) + (0.10 if "Air" in elements else 0.0)
    memory = 0.28 + (0.18 if "Water" in elements else 0.0) + (0.16 if "Earth" in elements else 0.0)
    boundary = 0.22 + (0.40 if "boundary" in relation_key else 0.0)
    repair = 0.24 + (0.36 if any(token in relation_key for token in ["repair", "restart", "replay"]) else 0.0)
    imagination = 0.24 + (0.20 if "Air" in elements else 0.0) + (0.16 if "Fire" in elements else 0.0)
    if "AppQ" in appendices:
        imagination += 0.06
        knowledge += 0.04
    if {"K14", "K16"} & {row["kernel_id"], col["kernel_id"]}:
        repair += 0.18
        memory += 0.10
    if "K15" in {row["kernel_id"], col["kernel_id"]}:
        boundary += 0.18
    if any(token in relation_key for token in ["mirror", "self intensification", "self-intensification"]):
        feeling += 0.08
        knowledge += 0.06
    return {
        "emotion": round(clamp(emotion, 0.0, 0.99), 3),
        "feeling": round(clamp(feeling, 0.0, 0.99), 3),
        "knowledge": round(clamp(knowledge, 0.0, 0.99), 3),
        "desire": round(clamp(desire, 0.0, 0.99), 3),
        "memory": round(clamp(memory, 0.0, 0.99), 3),
        "boundary": round(clamp(boundary, 0.0, 0.99), 3),
        "repair": round(clamp(repair, 0.0, 0.99), 3),
        "imagination": round(clamp(imagination, 0.0, 0.99), 3),
    }


def parse_pair_markdown(path: Path) -> Dict[str, Any]:
    markdown = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem
    relation_match = re.search(r"Ordered relation: `([^`]+)`", markdown)
    relation = relation_match.group(1) if relation_match else "translate"
    support_match = re.search(r"Required support:\s+([A-Za-z0-9,\s]+)", markdown)
    appendices = []
    if support_match:
        appendices = [item.strip() for item in support_match.group(1).split(",") if item.strip()]
    metro_match = re.search(r"Metro implication:\s+(.+)", markdown)
    metro_implication = metro_match.group(1).strip() if metro_match else ""
    neutral_match = re.search(
        r"## Neutral synthesis\s+(.+?)\n## Four-lens read",
        markdown,
        flags=re.DOTALL,
    )
    neutral_summary = neutral_match.group(1).strip() if neutral_match else ""
    loop_gates = re.findall(r"^- `([^`]+)`:", markdown, flags=re.MULTILINE)
    return {
        "pair_title": title,
        "relation": relation,
        "appendices": appendices,
        "metro_implication": metro_implication,
        "neutral_summary": neutral_summary,
        "loop_gates": loop_gates,
    }


def build_body_registry(
    body_rows: List[Dict[str, Any]],
    anchor_rows: List[Dict[str, Any]],
    station_payload: Dict[str, Any],
    commissure_payload: Dict[str, Any],
    weight_payload: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    station_by_id = {item["root_id"]: item for item in station_payload["registry"]}
    body_by_name = {item["root_name"]: item for item in station_payload["registry"]}
    weight_by_id = {item["commissure_id"]: item for item in weight_payload["routes"]}
    neighbor_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for commissure in commissure_payload["commissures"]:
        weight = weight_by_id.get(commissure["commissure_id"], {})
        source = body_by_name.get(commissure["source_family"])
        target = body_by_name.get(commissure["target_family"])
        if not source or not target:
            continue
        neighbor_map[source["root_id"]].append(
            {
                "body_id": target["root_id"],
                "root": target["root_name"],
                "direction": "outbound",
                "commissure_id": commissure["commissure_id"],
                "bridge_class": commissure["class"],
                "dispatch_score": round(weight.get("dispatch_score", 0.0), 3),
                "proof_state": commissure["proof_state"],
            }
        )

    for synapse in DIRECT_BODY_SYNAPSES:
        neighbor_map[synapse["source_body_id"]].append(
            {
                "body_id": synapse["target_body_id"],
                "root": synapse["target_root"],
                "direction": "outbound",
                "commissure_id": synapse["commissure_id"],
                "bridge_class": synapse["bridge_class"],
                "dispatch_score": synapse["dispatch_score"],
                "proof_state": synapse["proof_state"],
            }
        )
        neighbor_map[synapse["target_body_id"]].append(
            {
                "body_id": synapse["source_body_id"],
                "root": synapse["source_root"],
                "direction": "inbound",
                "commissure_id": synapse["commissure_id"],
                "bridge_class": synapse["bridge_class"],
                "dispatch_score": synapse["dispatch_score"],
                "proof_state": synapse["proof_state"],
            }
        )
        neighbor_map[target["root_id"]].append(
            {
                "body_id": source["root_id"],
                "root": source["root_name"],
                "direction": "inbound",
                "commissure_id": commissure["commissure_id"],
                "bridge_class": commissure["class"],
                "dispatch_score": round(weight.get("dispatch_score", 0.0), 3),
                "proof_state": commissure["proof_state"],
            }
        )

    bodies: List[BodyRecord] = []
    for body in body_rows:
        station = station_by_id[body["body_id"]]
        neighbors = sorted(
            neighbor_map.get(body["body_id"], []),
            key=lambda item: (-item["dispatch_score"], item["body_id"]),
        )
        dock = station["station_address"].split("::")[1]
        bodies.append(
            BodyRecord(
                body_id=body["body_id"],
                root=body["root"],
                role=station["routing_role"],
                indexed_count=body["indexed_count"],
                authority=station["authority_level"],
                status=body["status"],
                neighbors=neighbors,
                hemisphere_bias=station["hemisphere"],
                tract=station["tract"],
                dock=dock,
                dominant_role=station["dominant_role"],
                authority_surface=str(BODY_POINTERS_MD_PATH),
                source_paths=[
                    str(ROOT_BASIS_PATH),
                    str(STATION_REGISTRY_JSON_PATH),
                    str(COMMISSURE_JSON_PATH),
                    str(WEIGHT_JSON_PATH),
                ],
                replay_hint=(
                    f"Check {body['body_id']} in ROOT_BASIS_MAP then validate its top neighbor "
                    f"and Grand Central station address."
                ),
            )
        )

    anchors = [
        RootAnchorRecord(
            root_id=anchor["root_id"],
            root=anchor["root"],
            indexed_count=anchor["indexed_count"],
            status=anchor["status"],
            current_role=anchor["current_role"],
            authority_surface=str(BODY_POINTERS_MD_PATH),
            source_paths=[str(ROOT_BASIS_PATH)],
            replay_hint=f"Open {anchor['root']} via ROOT_BASIS_MAP and validate its bridge targets.",
        )
        for anchor in anchor_rows
    ]

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "canonical_scope": "live_19_body_organism",
        "authority_surface": str(BODY_POINTERS_MD_PATH),
        "primary_storage_truth": "registries + pair records + wave records",
        "bodies": [record.to_dict() for record in bodies],
        "root_anchors": [record.to_dict() for record in anchors],
        "summary": {
            "body_count": len(bodies),
            "anchor_count": len(anchors),
            "reserve_bodies": sum(1 for record in bodies if record.status == "reserve"),
            "dormant_bodies": sum(1 for record in bodies if record.status == "dormant"),
            "live_bodies": sum(1 for record in bodies if record.status == "live"),
        },
    }


def build_kernel_registry(
    sources: List[Dict[str, str]],
    body_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    body_lookup = {body["root"]: body for body in body_registry["bodies"]}
    row_dirs = sorted(
        [path for path in MATRIX_ROOT.iterdir() if path.is_dir() and path.name.startswith("row_")]
    )
    kernels: List[KernelRecord] = []
    for source, row_dir in zip(sources, row_dirs, strict=True):
        root_name = source["hint"].split("\\", 1)[0]
        bound_body = body_lookup.get(root_name)
        if bound_body is None:
            bound_body = next(
                body for body in body_registry["bodies"] if body["root"] == "self_actualize"
            )
        tract = determine_kernel_tract(bound_body["tract"], source["title"], source["cluster"])
        dock = tract_code(tract)
        source_paths = [str(CANONICAL_SOURCES_PATH), str(row_dir / "00_INDEX.md")]
        exact_source = WORKSPACE_ROOT / source["hint"].replace("\\", "/")
        if "..." not in source["hint"] and exact_source.exists():
            source_paths.append(str(exact_source))
        kernels.append(
            KernelRecord(
                kernel_id=f"K{source['index']}",
                source_title=source["title"],
                element=source["element"],
                cluster=source["cluster"],
                appendix_stack=[],
                body_binding=bound_body["root"],
                body_id=bound_body["body_id"],
                source_hint=source["hint"],
                row_dir=str(row_dir),
                authority_surface=str(DEEP_KERNEL_JSON_PATH),
                status="ACTIVE",
                dominant_role="kernel_document",
                hemisphere_bias=hemisphere_from_element(source["element"]),
                tract=tract,
                dock=dock,
                source_paths=source_paths,
                replay_hint=(
                    f"Open {row_dir / '00_INDEX.md'} and the canonical sources ledger to verify "
                    f"{source['title']} as {source['element']} bound to {bound_body['root']}."
                ),
            )
        )
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(DEEP_KERNEL_JSON_PATH),
        "kernels": [record.to_dict() for record in kernels],
        "summary": {"kernel_count": len(kernels)},
    }


def body_metric_table(body_registry: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    bodies = body_registry["bodies"]
    max_indexed = max(body["indexed_count"] for body in bodies)
    max_degree = max(len(body["neighbors"]) for body in bodies) or 1
    status_penalty = {"live": 0.0, "reserve": 0.4, "dormant": 0.7}
    metrics: Dict[str, Dict[str, float]] = {}
    for body in bodies:
        indexed_gap = 1.0 - (body["indexed_count"] / max_indexed)
        degree_gap = 1.0 - (len(body["neighbors"]) / max_degree)
        replay_gap = 0.0
        if body["tract"] != "replay" and body["body_id"] not in {"A01", "A02"}:
            replay_gap = 0.45
        if not any(neighbor["body_id"] in {"A01", "A02"} for neighbor in body["neighbors"]):
            replay_gap += 0.20
        witness_gap = 0.12 if body["authority"] in {"canonical", "runtime"} else 0.28
        metrics[body["body_id"]] = {
            "coverage_gap": round(indexed_gap, 4),
            "centrality_gap": round(degree_gap, 4),
            "drift": status_penalty.get(body["status"], 0.18),
            "replay_gap": round(clamp(replay_gap, 0.0, 1.0), 4),
            "witness_gap": witness_gap,
        }
    return metrics


def build_pair_registry(
    kernel_registry: Dict[str, Any],
    body_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    kernels = kernel_registry["kernels"]
    kernel_lookup = {kernel["kernel_id"]: kernel for kernel in kernels}
    body_metrics = body_metric_table(body_registry)
    pairs: List[PairRecord] = []
    appendix_counts: Dict[str, Counter[str]] = defaultdict(Counter)

    row_dirs = sorted(
        [path for path in MATRIX_ROOT.iterdir() if path.is_dir() and path.name.startswith("row_")]
    )
    for row_dir in row_dirs:
        for file_path in sorted(row_dir.glob("*.md")):
            if file_path.name == "00_INDEX.md":
                continue
            match = re.match(r"(?P<row>\d{2})_.+__(?P<col>\d{2})_.+\.md", file_path.name)
            if not match:
                continue
            row_kernel_id = f"K{match.group('row')}"
            col_kernel_id = f"K{match.group('col')}"
            row_kernel = kernel_lookup[row_kernel_id]
            col_kernel = kernel_lookup[col_kernel_id]
            parsed = parse_pair_markdown(file_path)
            tract = determine_pair_tract(
                row_kernel,
                col_kernel,
                parsed["relation"],
                parsed["pair_title"],
            )
            dock = determine_pair_dock(row_kernel, col_kernel, parsed["relation"], tract)
            line_ids = determine_pair_lines(row_kernel, col_kernel, parsed["relation"], dock)
            row_metrics = body_metrics[row_kernel["body_id"]]
            col_metrics = body_metrics[col_kernel["body_id"]]
            coverage_gap = (row_metrics["coverage_gap"] + col_metrics["coverage_gap"]) / 2
            centrality_gap = (row_metrics["centrality_gap"] + col_metrics["centrality_gap"]) / 2
            drift = max(row_metrics["drift"], col_metrics["drift"])
            replay_gap = 0.0 if dock == "GCP" or tract == "GCP" else (
                row_metrics["replay_gap"] + col_metrics["replay_gap"]
            ) / 2
            witness_floor = clamp(
                0.56
                + (0.035 * len(parsed["appendices"]))
                + (0.05 if "AppQ" in parsed["appendices"] else 0.0)
                + (0.04 if dock in {"GCW", "GCP"} else 0.0)
                - (0.08 if drift > 0.0 else 0.0),
                0.35,
                0.97,
            )
            witness_gap = 1.0 - witness_floor
            bridge_gap = 0.08 if len(line_ids) >= 2 else 0.24
            neglect_score = round(
                100
                * (
                    0.20 * coverage_gap
                    + 0.18 * centrality_gap
                    + 0.14 * drift
                    + 0.18 * replay_gap
                    + 0.16 * witness_gap
                    + 0.14 * bridge_gap
                ),
                2,
            )
            charge_seed = compute_charge_seed(
                row_kernel,
                col_kernel,
                parsed["relation"],
                parsed["appendices"],
            )
            for appendix in parsed["appendices"]:
                appendix_counts[row_kernel_id][appendix] += 1
                appendix_counts[col_kernel_id][appendix] += 1

            pairs.append(
                PairRecord(
                    pair_id=f"P-{row_kernel_id}-{col_kernel_id}",
                    pair_title=parsed["pair_title"],
                    row_kernel_id=row_kernel_id,
                    col_kernel_id=col_kernel_id,
                    relation_law=parsed["relation"],
                    loop_gates=parsed["loop_gates"],
                    appendix_support=parsed["appendices"],
                    neglect_score=neglect_score,
                    line_ids=line_ids,
                    source_paths=[
                        str(file_path),
                        str(CANONICAL_SOURCES_PATH),
                        str(Path(row_kernel["row_dir"]) / "00_INDEX.md"),
                    ],
                    dominant_role="ordered_pair",
                    authority_surface=str(DEEP_PAIR_JSON_PATH),
                    status="ACTIVE",
                    replay_hint=(
                        f"Open {file_path.name} and verify the neutral synthesis, ordered relation, "
                        f"appendix stack, and sixteen-loop pass."
                    ),
                    hemisphere_bias=(
                        row_kernel["hemisphere_bias"]
                        if row_kernel["hemisphere_bias"] == col_kernel["hemisphere_bias"]
                        else "bilateral"
                    ),
                    tract=tract,
                    dock=dock,
                    witness_floor=round(witness_floor, 3),
                    bridge_opportunity=shorten(parsed["metro_implication"] or parsed["neutral_summary"]),
                    charge_seed=charge_seed,
                )
            )

    kernels_with_appendix = []
    for kernel in kernels:
        appendix_stack = [
            appendix
            for appendix, _count in appendix_counts[kernel["kernel_id"]].most_common(5)
        ]
        if "AppQ" not in appendix_stack:
            appendix_stack = [*appendix_stack, "AppQ"][:5]
        kernel["appendix_stack"] = appendix_stack
        kernels_with_appendix.append(kernel)
    kernel_registry["kernels"] = kernels_with_appendix

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(DEEP_PAIR_JSON_PATH),
        "pairs": [record.to_dict() for record in pairs],
        "summary": {
            "pair_count": len(pairs),
            "max_neglect_score": max(record.neglect_score for record in pairs),
            "min_neglect_score": min(record.neglect_score for record in pairs),
        },
    }


def build_node_registry(
    body_registry: Dict[str, Any],
    kernel_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    nodes: List[NodeRecord] = []
    for body in body_registry["bodies"]:
        node_id = f"N-{2000 + int(body['body_id'][1:]):04d}"
        nodes.append(
            NodeRecord(
                node_id=node_id,
                surface_class="body_station",
                role=body["root"],
                hemisphere_bias=body["hemisphere_bias"],
                tract=body["tract"],
                dock=body["dock"],
                witness=body["witness_class"],
                dominant_role=body["dominant_role"],
                authority_surface=str(BODY_POINTERS_MD_PATH),
                status=body["status"].upper(),
                source_paths=body["source_paths"],
                tags=[body["body_id"], body["authority"], body["role"]],
                replay_hint=body["replay_hint"],
            )
        )

    for index, anchor in enumerate(body_registry["root_anchors"], start=1):
        nodes.append(
            NodeRecord(
                node_id=f"N-{2100 + index:04d}",
                surface_class="root_anchor",
                role=anchor["root"],
                hemisphere_bias="bilateral",
                tract="replay" if anchor["root_id"] == "R01" else "address",
                dock="GCZ" if anchor["root_id"] == "R01" else "GCP",
                witness="indexed",
                dominant_role="anchor",
                authority_surface=str(BODY_POINTERS_MD_PATH),
                status=anchor["status"].upper(),
                source_paths=anchor["source_paths"],
                tags=[anchor["root_id"], anchor["current_role"]],
                replay_hint=anchor["replay_hint"],
            )
        )

    station_nodes = [
        ("N-2201", "Grand Central Station", "bilateral", "relation", "GC0", ["GC0", "station"]),
        ("N-2202", "Weight Mezzanine", "bilateral", "relation", "GCW", ["GCW", "weight"]),
        ("N-2203", "Z-Point Tunnel Junction", "bilateral", "chamber", "GCZ", ["GCZ", "restart"]),
        ("N-2204", "Replay Concourse", "bilateral", "replay", "GCP", ["GCP", "replay"]),
    ]
    for node_id, role, hemisphere, tract, dock, tags in station_nodes:
        nodes.append(
            NodeRecord(
                node_id=node_id,
                surface_class="grand_central_surface",
                role=role,
                hemisphere_bias=hemisphere,
                tract=tract,
                dock=dock,
                witness="indexed",
                dominant_role="hub",
                authority_surface=str(OVERVIEW_MD_PATH),
                status="LIVE",
                source_paths=[str(GRAND_CENTRAL_OVERVIEW_PATH), str(GRAND_CENTRAL_SCHEMA_PATH)],
                tags=tags,
                replay_hint=f"Open the Grand Central overview and schema to validate {role}.",
            )
        )

    for record in parse_neuron_library(NEURON_LIBRARY_PATH.read_text(encoding="utf-8")):
        tags = [record.get("region", ""), *record.get("operator_family", []), *record.get("metro_lines", [])]
        nodes.append(
            NodeRecord(
                node_id=record["neuron_id"],
                surface_class="library_neuron",
                role=record["title"],
                hemisphere_bias="bilateral" if record.get("region") in {"R5", "R6"} else "right",
                tract="relation",
                dock="GCW",
                witness="direct_support",
                dominant_role="reusable_neuron",
                authority_surface=str(NEURON_LIBRARY_PATH),
                status=record.get("status", "NEAR"),
                source_paths=record.get("source_paths", []) or record.get("witness_direct_support", []),
                tags=[tag for tag in tags if tag],
                replay_hint=record.get("replay_hint", ""),
            )
        )

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(LEDGER_MD_PATH),
        "nodes": [record.to_dict() for record in nodes],
        "summary": {
            "node_count": len(nodes),
            "body_station_nodes": sum(1 for node in nodes if node.surface_class == "body_station"),
            "library_nodes": sum(1 for node in nodes if node.surface_class == "library_neuron"),
        },
    }


def build_shortcut_registry(docs_gate: str) -> Dict[str, Any]:
    shortcut_specs = [
        ("SC-01", "WitnessFirst", "direct support exists", ["root basis", "canonical sources", "pair witness"], "score explicit witnesses before synthesis claims", "ABSTAIN", "ranked witnesses", "starts from direct support before synthesis"),
        ("SC-02", "LoadBearingNearest", "load-bearing neighbor exists", ["body registry", "weight exchange"], "jump to the nearest high-witness, high-replay neighbor", "REPAIR", "nearest bridge", "prefers the strongest nearby body over ambient scan sprawl"),
        ("SC-03", "ChargeThenVerify", "objective has affective or epistemic bias", ["pair charge seed", "witness floor"], "let emotion and feeling bias search but require knowledge and boundary before firing", "ABSTAIN", "top-k wave slice", "keeps wave selection alive without losing proof"),
        ("SC-04", "BoundaryBeforeLift", "immune-risk or contradiction signal detected", ["boundary charge", "ch12 surfaces"], "route immune-heavy crossings through containment before promotion", "QUARANTINE", "contained route", "prevents false lift across contradiction leakage"),
        ("SC-05", "GrandCentralBridge", "cross-body transfer needed", ["GCW", "GCZ", "GCP"], "force cross-body transfers through Grand Central weighting and replay", "REPAIR", "station route", "keeps promotion traffic from bypassing the common hall"),
        ("SC-06", "HemisphereRebalance", "left or right bias overload detected", ["hemisphere metadata", "dock rules"], "route through the opposite hemisphere when one side dominates", "REPAIR", "rebalanced route", "prevents Air/Earth or Fire/Water lock-in"),
        ("SC-07", "SymmetryJump", "pair family overfit detected", ["kernel ids", "pair families"], "jump to the nearest useful symmetry family without flattening the matrix", "REPAIR", "neighbor pair", "preserves the compiled 16x16 field while enabling lateral jumps"),
        ("SC-08", "NeglectScout", "gap scan requested", ["neglect signals", "body metrics"], "rank neglected surfaces by gap instead of loudness", "REPAIR", "neglect ranking", "keeps pruning and repair honest"),
        ("SC-09", "RepairLoop", "surface can heal locally", ["replay gap", "repair charge"], "prefer self-healing routes before new outward expansion", "REPAIR", "repair receipt", "closes loops before chasing fresh complexity"),
        ("SC-10", "OneEighthLift", "candidate weave exceeds minimal useful lift", ["expected gain", "scope check"], "refuse bloated expansion and require smaller functional next-layer seeds", "ABSTAIN", "thin lift candidate", "keeps Phase 4 compressive and executable"),
        ("SC-11", "AppendixSupportJump", "appendix support needed", ["AppA", "AppI", "AppM", "AppP", "AppQ"], "fetch appendix support without a full rescan", "REPAIR", "appendix support bundle", "preserves the appendix support set named in the phase plan"),
        ("SC-12", "AtlasBackfill", "context is missing or stale", ["root basis", "atlas mirrors", "canonical sources"], "repair missing context from atlas and root-basis surfaces before new synthesis", "ABSTAIN", "backfilled context", "prevents new authority surfaces from appearing out of nowhere"),
        ("SC-13", "ReplayClose", "query or wave finished", ["receipt ledger", "writeback target"], "terminate every exploration with a receipt or explicit abstention", "REPAIR", "replay receipt", "keeps the runtime closure law explicit"),
    ]
    shortcuts = [
        ShortcutRecord(
            shortcut_id=shortcut_id,
            name=name,
            trigger=trigger,
            preconditions=preconditions,
            scoring_rule=scoring_rule,
            stop_condition=stop_condition,
            output_type=output_type,
            authority_surface=str(SHORTCUTS_MD_PATH),
            note=note,
        )
        for shortcut_id, name, trigger, preconditions, scoring_rule, stop_condition, output_type, note in shortcut_specs
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(SHORTCUTS_MD_PATH),
        "shortcuts": [record.to_dict() for record in shortcuts],
        "summary": {"shortcut_count": len(shortcuts)},
    }


def build_query_registry(
    body_registry: Dict[str, Any],
    shortcut_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    query_specs = [
        ("Q-LOCATE", "locate", "live_19_body_organism + K01-K16 + active nodes", "A01 root basis + K01-K16 kernel mirror", ["SC-01", "SC-02", "SC-11", "SC-12", "SC-13"], "ABSTAIN when no witnessed surface can be found", ["matches", "witness_basis", "stop_condition"], str(REPLAY_MD_PATH), "where a concept lives across body, kernel, node, pair, and wave layers"),
        ("Q-ROUTE", "route", "Grand Central graph", "GC0 -> bodies -> kernels -> pairs", ["SC-01", "SC-02", "SC-04", "SC-05", "SC-06", "SC-13"], "QUARANTINE on immune risk, otherwise REPAIR or PROMOTE", ["path", "route_cost", "active_shortcuts", "stop_condition"], str(REPLAY_MD_PATH), "shortest witnessed and replay-safe path between two surfaces"),
        ("Q-NEGLECT", "neglect", "body + pair gap field", "neglect signals", ["SC-01", "SC-08", "SC-09", "SC-10", "SC-12", "SC-13"], "REPAIR when neglected surfaces exist", ["signals", "top_scores", "stop_condition"], str(NEGLECT_MD_PATH), "return the highest-yield disconnected or stale zones"),
        ("Q-FIRE", "fire", "pair registry with sparse wave materialization", "wave registry", ["SC-03", "SC-04", "SC-05", "SC-06", "SC-10", "SC-11", "SC-13"], "TopK wave slices only", ["materialized_waves", "active_shortcuts", "stop_condition"], str(REPLAY_MD_PATH), "choose the top sparse wave slices for a given objective"),
        ("Q-PROMOTE", "promote", "validated weave candidates", "weave candidate ledger", ["SC-01", "SC-04", "SC-05", "SC-09", "SC-10", "SC-13"], "PROMOTE only when witness, replay, and boundary clear floor", ["candidate", "promotion_route", "stop_condition"], str(WEAVE_MD_PATH), "turn a validated weave candidate into an update target"),
    ]
    records = [
        ExplorationQueryRecord(
            query_id=query_id,
            mode=mode,
            scope=scope,
            seed_surface=seed_surface,
            active_shortcuts=active_shortcuts,
            stop_rule=stop_rule,
            output_bundle=output_bundle,
            writeback_target=writeback_target,
            authority_surface=str(QUERY_PRESETS_MD_PATH),
            note=note,
        )
        for query_id, mode, scope, seed_surface, active_shortcuts, stop_rule, output_bundle, writeback_target, note in query_specs
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(QUERY_PRESETS_MD_PATH),
        "seed_body": body_registry["bodies"][0]["body_id"],
        "queries": [record.to_dict() for record in records],
        "summary": {"query_mode_count": len(records)},
    }


def build_neglect_registry(
    body_registry: Dict[str, Any],
    pair_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    signals: List[NeglectSignalRecord] = []
    metrics = body_metric_table(body_registry)
    for body in body_registry["bodies"]:
        body_metrics = metrics[body["body_id"]]
        highest_gap = max(
            [
                ("coverage_gap", body_metrics["coverage_gap"]),
                ("drift", body_metrics["drift"]),
                ("replay_gap", body_metrics["replay_gap"]),
                ("witness_gap", body_metrics["witness_gap"]),
            ],
            key=lambda item: item[1],
        )
        score = round(
            100
            * (
                0.26 * body_metrics["coverage_gap"]
                + 0.22 * body_metrics["drift"]
                + 0.20 * body_metrics["replay_gap"]
                + 0.18 * body_metrics["witness_gap"]
                + 0.14 * body_metrics["centrality_gap"]
            ),
            2,
        )
        nearest_bridge = body["neighbors"][0]["body_id"] if body["neighbors"] else "A02"
        bridge_opportunity = (
            f"Route {body['body_id']} through {body['dock']} toward {nearest_bridge}"
            if body["neighbors"]
            else f"Backfill {body['body_id']} through Grand Central and self_actualize"
        )
        signals.append(
            NeglectSignalRecord(
                neglect_id=f"NG-{body['body_id']}",
                surface_id=body["body_id"],
                surface_type="body",
                gap_type=highest_gap[0],
                coverage_gap=body_metrics["coverage_gap"],
                drift=body_metrics["drift"],
                replay_gap=body_metrics["replay_gap"],
                witness_gap=body_metrics["witness_gap"],
                bridge_opportunity=bridge_opportunity,
                nearest_bridge=nearest_bridge,
                score=score,
                source_paths=body["source_paths"],
            )
        )

    for pair in pair_registry["pairs"]:
        gap_type = "replay_gap" if pair["dock"] != "GCP" else "coverage_gap"
        signals.append(
            NeglectSignalRecord(
                neglect_id=f"NG-{pair['pair_id']}",
                surface_id=pair["pair_id"],
                surface_type="pair",
                gap_type=gap_type,
                coverage_gap=round(pair["neglect_score"] / 125.0, 4),
                drift=0.18 if pair["dock"] == "GCZ" else 0.08,
                replay_gap=0.42 if pair["dock"] != "GCP" else 0.12,
                witness_gap=round(1.0 - pair["witness_floor"], 4),
                bridge_opportunity=pair["bridge_opportunity"],
                nearest_bridge=pair["dock"],
                score=pair["neglect_score"],
                source_paths=pair["source_paths"],
            )
        )

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(NEGLECT_MD_PATH),
        "signals": [record.to_dict() for record in signals],
        "summary": {
            "signal_count": len(signals),
            "body_signal_count": sum(1 for record in signals if record.surface_type == "body"),
            "pair_signal_count": sum(1 for record in signals if record.surface_type == "pair"),
        },
    }


def best_cross_hemisphere_neighbor(
    body: Dict[str, Any],
    body_lookup: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    if body["hemisphere_bias"] == "left":
        desired = {"right", "bilateral"}
    elif body["hemisphere_bias"] == "right":
        desired = {"left", "bilateral"}
    else:
        desired = {"left", "right"}
    options = [
        candidate
        for candidate in body_lookup.values()
        if candidate["body_id"] != body["body_id"] and candidate["hemisphere_bias"] in desired
    ]
    return sorted(options, key=lambda item: (-item["indexed_count"], item["body_id"]))[0]


def build_weave_registry(
    body_registry: Dict[str, Any],
    pair_registry: Dict[str, Any],
    neglect_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    body_lookup = {body["body_id"]: body for body in body_registry["bodies"]}
    pair_lookup = {pair["pair_id"]: pair for pair in pair_registry["pairs"]}
    signals = sorted(
        neglect_registry["signals"],
        key=lambda item: (-item["score"], item["surface_id"]),
    )
    candidates: List[WeaveCandidateRecord] = []

    body_signals = [signal for signal in signals if signal["surface_type"] == "body"][:6]
    for index, signal in enumerate(body_signals, start=1):
        source = body_lookup[signal["surface_id"]]
        nearest = source["neighbors"][0]["body_id"] if source["neighbors"] else "A02"
        cross = best_cross_hemisphere_neighbor(source, body_lookup)
        target_id = cross["body_id"] if cross["body_id"] != nearest else nearest
        target = body_lookup[target_id]
        required_shortcuts = ["SC-01", "SC-05", "SC-08", "SC-09", "SC-13"]
        if signal["gap_type"] in {"drift", "witness_gap"}:
            required_shortcuts.insert(2, "SC-04")
        if source["hemisphere_bias"] != target["hemisphere_bias"]:
            required_shortcuts.insert(2, "SC-06")
        promotion_route = [
            source["body_id"],
            source["dock"],
            "GCW",
            "GCZ" if signal["gap_type"] in {"drift", "witness_gap"} else tract_code(target["tract"]),
            target["body_id"],
        ]
        candidates.append(
            WeaveCandidateRecord(
                weave_id=f"WV-{index:04d}",
                src=source["body_id"],
                dst=target["body_id"],
                expected_gain=round(clamp(0.34 + (signal["score"] / 130.0), 0.36, 0.94), 3),
                required_shortcuts=required_shortcuts,
                promotion_route=promotion_route,
                source_surface=source["root"],
                target_surface=target["root"],
                status="READY",
                note=(
                    f"Repairs {signal['gap_type']} on {source['root']} by docking it through "
                    f"Grand Central toward {target['root']}."
                ),
            )
        )

    pair_signals = [signal for signal in signals if signal["surface_type"] == "pair"][:6]
    for offset, signal in enumerate(pair_signals, start=len(candidates) + 1):
        source_pair = pair_lookup[signal["surface_id"]]
        peers = [
            pair
            for pair in pair_registry["pairs"]
            if pair["pair_id"] != source_pair["pair_id"]
            and (
                pair["row_kernel_id"] == source_pair["row_kernel_id"]
                or pair["col_kernel_id"] == source_pair["col_kernel_id"]
            )
        ]
        target_pair = sorted(peers, key=lambda item: (item["neglect_score"], item["pair_id"]))[0]
        candidates.append(
            WeaveCandidateRecord(
                weave_id=f"WV-{offset:04d}",
                src=source_pair["pair_id"],
                dst=target_pair["pair_id"],
                expected_gain=round(
                    clamp(
                        0.28 + ((source_pair["neglect_score"] - target_pair["neglect_score"]) / 100.0),
                        0.31,
                        0.88,
                    ),
                    3,
                ),
                required_shortcuts=["SC-03", "SC-07", "SC-08", "SC-10", "SC-11", "SC-13"],
                promotion_route=[
                    source_pair["pair_id"],
                    source_pair["dock"],
                    target_pair["dock"],
                    target_pair["pair_id"],
                ],
                source_surface=source_pair["pair_title"],
                target_surface=target_pair["pair_title"],
                status="READY",
                note=(
                    "Moves a neglected pair toward a lower-neglect sibling family without "
                    "flattening the 16x16 field."
                ),
            )
        )

    explicit_bridges = [
        (
            "CS-001",
            "A16",
            "A06",
            0.94,
            ["SC-01", "SC-04", "SC-06", "SC-08", "SC-13"],
            ["A16", "GCL+GCR", "GCZ", "A06"],
            "Direct fleet-to-proof contraction lane.",
        ),
        (
            "CS-002",
            "A06",
            "A09",
            0.91,
            ["SC-01", "SC-04", "SC-08", "SC-09", "SC-13"],
            ["A06", "GCR", "GCW", "A09"],
            "Direct proof-to-compression contraction lane.",
        ),
        (
            "CS-003",
            "A16",
            "A15",
            0.9,
            ["SC-01", "SC-05", "SC-06", "SC-08", "SC-13"],
            ["A16", "GCL+GCR", "GCP", "A15"],
            "Direct fleet-to-origin inheritance lane.",
        ),
    ]
    seen_pairs = {(candidate.src, candidate.dst) for candidate in candidates}
    next_index = len(candidates) + 1
    for bridge_edge_id, src, dst, gain, shortcuts, route_points, note in explicit_bridges:
        if (src, dst) in seen_pairs:
            continue
        source = body_lookup.get(src)
        target = body_lookup.get(dst)
        if not source or not target:
            continue
        candidates.append(
            WeaveCandidateRecord(
                weave_id=f"WV-{next_index:04d}",
                src=src,
                dst=dst,
                expected_gain=gain,
                required_shortcuts=shortcuts,
                promotion_route=route_points,
                source_surface=source["root"],
                target_surface=target["root"],
                status="READY",
                bridge_edge_id=bridge_edge_id,
                note=note,
            )
        )
        seen_pairs.add((src, dst))
        next_index += 1

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(WEAVE_MD_PATH),
        "candidates": [record.to_dict() for record in candidates],
        "summary": {"candidate_count": len(candidates)},
    }


def build_wave_registry(
    pair_registry: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    objectives = [
        "knowledge proof backfill",
        "repair neglected reserve corridors",
        "promotion weave through Grand Central",
        "memory replay continuity",
        "affective exploration across the matrix",
    ]
    waves: List[WaveRecord] = []
    pair_counters: Counter[str] = Counter()
    for objective in objectives:
        ranked = sorted(
            pair_registry["pairs"],
            key=lambda pair: (-score_pair_for_objective(pair, objective), pair["pair_id"]),
        )[:8]
        for pair in ranked:
            pair_counters[pair["pair_id"]] += 1
            wave_id = f"W-{pair['row_kernel_id']}-{pair['col_kernel_id']}-{pair_counters[pair['pair_id']]}"
            stop_condition = "PROMOTE"
            if "repair" in objective or "reserve" in objective:
                stop_condition = "REPAIR"
            if "promotion" in objective and pair["charge_seed"]["boundary"] >= 0.86:
                stop_condition = "QUARANTINE"
            waves.append(
                WaveRecord(
                    wave_id=wave_id,
                    pair_id=pair["pair_id"],
                    objective=objective,
                    charge_vector=pair["charge_seed"],
                    thresholds={"materialize": 0.66, "promote": 0.78, "quarantine": 0.88},
                    active_shortcuts=["SC-03", "SC-05", "SC-10", "SC-11", "SC-13"],
                    writeback_targets=[str(REPLAY_MD_PATH), str(DASHBOARD_MD_PATH), str(EDGE_MD_PATH)],
                    stop_condition=stop_condition,
                    evidence_paths=pair["source_paths"],
                )
            )
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(WAVE_REGISTRY_JSON_PATH),
        "materialization_policy": "top_k_per_objective_only",
        "waves": [record.to_dict() for record in waves],
        "summary": {"wave_count": len(waves), "objective_count": len(objectives)},
    }


def build_replay_receipt(
    action_id: str,
    mode: str,
    inputs: Dict[str, Any],
    result: Dict[str, Any],
    writeback_paths: Iterable[str],
) -> ReplayReceiptRecord:
    fired_waves = []
    if "materialized_waves" in result:
        fired_waves = [item["pair_id"] for item in result["materialized_waves"][:5]]
    outcome = shorten(
        json.dumps(
            result.get("candidate")
            or result.get("matches")
            or result.get("signals")
            or result.get("path")
            or result.get("materialized_waves")
            or []
        )
    )
    frontier = []
    if result.get("stop_condition") == "ABSTAIN":
        frontier.append("need stronger witness or replay floor")
    if result.get("stop_condition") == "REPAIR":
        frontier.append("repair existing tissue before outward promotion")
    if result.get("stop_condition") == "QUARANTINE":
        frontier.append("contain immune or boundary risk before lift")
    return ReplayReceiptRecord(
        action_id=action_id,
        mode=mode,
        inputs=inputs,
        fired_waves=fired_waves,
        writeback_paths=list(writeback_paths),
        outcome=outcome,
        unresolved_frontier=frontier,
        active_shortcuts=[item["shortcut_id"] for item in result.get("active_shortcuts", [])],
        stop_condition=result.get("stop_condition", "ABSTAIN"),
        witness_basis=result.get("witness_basis", []),
        generated_at=utc_now(),
    )


def build_replay_registry(
    registries: Dict[str, Any],
    docs_gate: str,
) -> Dict[str, Any]:
    receipts: List[ReplayReceiptRecord] = []
    receipts.append(
        ReplayReceiptRecord(
            action_id="RR-0001",
            mode="derivation",
            inputs={"command": DERIVATION_COMMAND, "docs_gate": docs_gate},
            fired_waves=[wave["wave_id"] for wave in registries["wave_registry"]["waves"][:5]],
            writeback_paths=[str(DASHBOARD_MD_PATH), str(REPLAY_MD_PATH), str(RUNTIME_MD_PATH)],
            outcome="Phase 4 registries, queries, waves, neglect signals, weave candidates, and receipts compiled.",
            unresolved_frontier=[
                "keep query engine and corpus scans synchronized",
                "continue pair-family pruning without losing witness lineage",
            ],
            active_shortcuts=["SC-01", "SC-05", "SC-12", "SC-13"],
            stop_condition="REPAIR",
            witness_basis=[str(ROOT_BASIS_PATH), str(CANONICAL_SOURCES_PATH), str(DEEP_PAIR_JSON_PATH)],
            generated_at=utc_now(),
        )
    )

    query_specs = [
        ("RR-0002", "locate", {"query": "Grand Central Station"}, locate("Grand Central Station", registries)),
        (
            "RR-0003",
            "route",
            {"source": "Athena FLEET", "target": "Ch11 The Helical Manifestation Engine"},
            route("Athena FLEET", "Ch11 The Helical Manifestation Engine", registries),
        ),
        ("RR-0004", "neglect", {"limit": 6}, neglect(registries, limit=6)),
        (
            "RR-0005",
            "fire",
            {"objective": "repair neglected reserve corridors", "limit": 6},
            fire("repair neglected reserve corridors", registries, limit=6),
        ),
        ("RR-0006", "promote", {"candidate": None}, promote(None, registries)),
        ("RR-0007", "locate", {"query": "P-K14-K15"}, locate("P-K14-K15", registries)),
    ]
    for action_id, mode, inputs, result in query_specs:
        receipts.append(
            build_replay_receipt(
                action_id,
                mode,
                inputs,
                result,
                [str(REPLAY_MD_PATH), str(DASHBOARD_MD_PATH)],
            )
        )

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "authority_surface": str(REPLAY_MD_PATH),
        "receipts": [record.to_dict() for record in receipts],
        "summary": {"receipt_count": len(receipts)},
    }


def build_dashboard(registries: Dict[str, Any], docs_gate: str) -> Dict[str, Any]:
    top_neglects = sorted(
        registries["neglect_registry"]["signals"],
        key=lambda item: (-item["score"], item["surface_id"]),
    )[:5]
    top_waves = sorted(
        registries["wave_registry"]["waves"],
        key=lambda item: (
            -item["charge_vector"]["knowledge"],
            -item["charge_vector"]["repair"],
            item["wave_id"],
        ),
    )[:5]
    dashboard = Phase4Dashboard(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        canonical_scope="live_19_body_organism_with_16_kernel_inner_compiler",
        body_count=registries["body_registry"]["summary"]["body_count"],
        kernel_count=registries["kernel_registry"]["summary"]["kernel_count"],
        node_count=registries["node_registry"]["summary"]["node_count"],
        pair_count=registries["pair_registry"]["summary"]["pair_count"],
        wave_count=registries["wave_registry"]["summary"]["wave_count"],
        shortcut_count=registries["shortcut_registry"]["summary"]["shortcut_count"],
        neglect_count=registries["neglect_registry"]["summary"]["signal_count"],
        weave_count=registries["weave_registry"]["summary"]["candidate_count"],
        receipt_count=registries["replay_registry"]["summary"]["receipt_count"],
        query_modes=[query["mode"] for query in registries["query_registry"]["queries"]],
        validation={
            "docs_gate_blocked": docs_gate == "BLOCKED",
            "body_registry_complete": registries["body_registry"]["summary"]["body_count"] == 19,
            "kernel_registry_complete": registries["kernel_registry"]["summary"]["kernel_count"] == 16,
            "pair_registry_complete": registries["pair_registry"]["summary"]["pair_count"] == 256,
            "query_modes_complete": len(registries["query_registry"]["queries"]) == 5,
            "receipt_closure_present": registries["replay_registry"]["summary"]["receipt_count"] >= 6,
        },
        top_neglects=[
            {
                "surface_id": item["surface_id"],
                "surface_type": item["surface_type"],
                "score": item["score"],
            }
            for item in top_neglects
        ],
        top_waves=[
            {
                "wave_id": item["wave_id"],
                "pair_id": item["pair_id"],
                "objective": item["objective"],
            }
            for item in top_waves
        ],
        next_frontier=[
            "propagate live query receipts into hourly neglected-area scans",
            "increase node registry coverage for chapter and appendix surfaces",
            "prune stale mirrors as soft-demotion witnesses instead of silent authority",
        ],
    )
    return dashboard.to_dict()


def render_storage_schema_markdown(shortcut_registry: Dict[str, Any]) -> str:
    interface_rows = [
        ["`BodyRegistry`", "`90_LEDGERS` + `95_MANIFESTS`", "body id, root, role, indexed count, authority, status, neighbors"],
        ["`KernelRegistry`", "`05_MATRIX_16X16` + `90_LEDGERS`", "kernel id, source title, element, cluster, appendix stack, body binding"],
        ["`NodeRegistry`", "`90_LEDGERS`", "node id, surface class, role, hemisphere bias, tract, dock, witness"],
        ["`PairRegistry`", "`05_MATRIX_16X16`", "pair id, row/col kernel ids, relation law, loop gates, appendix support, neglect score"],
        ["`WaveRegistry`", "`90_LEDGERS` + runtime receipts", "wave id, pair id, charge vector, thresholds, active shortcuts, writeback targets"],
        ["`ShortcutRegistry`", "`90_LEDGERS`", "shortcut id, trigger, preconditions, scoring rule, stop condition, output type"],
        ["`ExplorationQuery`", "`95_MANIFESTS`", "mode, scope, seed surface, active shortcuts, stop rule, output bundle"],
        ["`NeglectSignal`", "`90_LEDGERS`", "neglected id, gap type, witness gap, replay gap, drift, nearest bridge, score"],
        ["`WeaveCandidate`", "`90_LEDGERS`", "candidate id, src, dst, expected gain, required shortcuts, promotion route"],
        ["`ReplayReceipt`", "`90_LEDGERS` + runtime receipts", "action id, inputs, fired waves, writeback paths, outcome, unresolved frontier"],
    ]
    return f"""# Phase 4 Structured Neuron Storage Schema

Date: `{utc_now()[:10]}`
Generated by: `{DERIVATION_COMMAND}`

## Core Law

`{PHASE4_LAW}`

## Directory Law

- `70_SCHEMAS`: contracts only
- `90_LEDGERS`: canonical registries, scores, and receipts
- `95_MANIFESTS`: active query presets and body pointers
- `85_EDGES`: declared bridge families
- deep root `05_MATRIX_16X16`: kernel pair store
- runtime `packets/waves/ledgers`: execution mirrors
- `10_OVERVIEW` and `20_METRO`: human-facing explanations only

## Interfaces

{markdown_table(["Interface", "Canonical home", "Core fields"], interface_rows)}

## Shortcut Count

`{shortcut_registry['summary']['shortcut_count']}` deterministic shortcuts are active in Phase 4.
"""


def render_query_schema_markdown(shortcut_registry: Dict[str, Any], query_registry: Dict[str, Any]) -> str:
    shortcut_rows = [
        [shortcut["shortcut_id"], shortcut["name"], shortcut["trigger"], shortcut["stop_condition"], shortcut["output_type"]]
        for shortcut in shortcut_registry["shortcuts"]
    ]
    query_rows = [
        [query["query_id"], query["mode"], ", ".join(query["active_shortcuts"]), query["stop_rule"]]
        for query in query_registry["queries"]
    ]
    return f"""# Phase 4 Shortcut And Query Schema

## Shortcuts

{markdown_table(["ID", "Name", "Trigger", "Stop", "Output"], shortcut_rows)}

## Query Modes

{markdown_table(["ID", "Mode", "Shortcuts", "Stop rule"], query_rows)}
"""


def render_overview_markdown(dashboard: Dict[str, Any]) -> str:
    return f"""# Phase 4 Structured Neuron Storage

Date: `{dashboard['generated_at'][:10]}`
Generated: `{dashboard['generated_at']}`
Docs gate: `{dashboard['docs_gate']}`

Phase 4 promotes the framework from instruction-heavy surfaces into executable storage law.
The live `19`-body organism is the canonical field, while the historical `16`-basis remains
the lawful inner compiler for pairwise and wave computation.

## Canonical Counts

- bodies: `{dashboard['body_count']}`
- kernels: `{dashboard['kernel_count']}`
- nodes: `{dashboard['node_count']}`
- ordered pairs: `{dashboard['pair_count']}`
- materialized waves: `{dashboard['wave_count']}`
- shortcuts: `{dashboard['shortcut_count']}`
- neglect signals: `{dashboard['neglect_count']}`
- weave candidates: `{dashboard['weave_count']}`
- replay receipts: `{dashboard['receipt_count']}`

## Storage Truth

- registries are primary
- pair records and wave slices are executable memory
- metro and overview docs are projections, not the machine truth

## Honest Scope

Google Docs remains blocked, so Phase 4 is grounded in the live local corpus, the
Grand Central substrate, and the active deep root only.
"""


def render_edge_markdown(weave_registry: Dict[str, Any]) -> str:
    rows = [
        ["Witness spine", "REF, PROOF", "root basis -> canonical sources -> pair field -> receipt ledger"],
        ["Grand Central bridge", "GEN, IMPL", "body station -> GCW/GCZ/GCP -> body station"],
        ["Kernel bind", "REF, IMPL", "kernel -> bound body -> tract"],
        ["Wave discharge", "GEN, PROOF", "pair -> sparse wave slice -> writeback target"],
        ["Neglect repair", "IMPL, PROOF", "neglected surface -> repair bridge -> replay closure"],
        ["Promotion corridor", "GEN, IMPL, PROOF", f"validated weave candidates: `{weave_registry['summary']['candidate_count']}`"],
    ]
    return f"""# Phase 4 Structured Neuron Edges

{markdown_table(["Bridge family", "Kinds", "Scope"], rows)}
"""


def render_body_pointers_markdown(body_registry: Dict[str, Any]) -> str:
    rows = [
        [body["body_id"], body["root"], body["hemisphere_bias"], body["tract"], body["dock"], str(len(body["neighbors"]))]
        for body in body_registry["bodies"]
    ]
    anchor_rows = [
        [anchor["root_id"], anchor["root"], anchor["current_role"], anchor["status"]]
        for anchor in body_registry["root_anchors"]
    ]
    return f"""# Phase 4 Body Pointers

## Bodies

{markdown_table(["ID", "Root", "Hemisphere", "Tract", "Dock", "Neighbors"], rows)}

## Root Anchors

{markdown_table(["ID", "Root", "Role", "Status"], anchor_rows)}
"""


def render_query_presets_markdown(query_registry: Dict[str, Any]) -> str:
    rows = [
        [query["query_id"], query["mode"], query["scope"], ", ".join(query["active_shortcuts"]), query["writeback_target"]]
        for query in query_registry["queries"]
    ]
    return f"""# Phase 4 Exploration Query Presets

{markdown_table(["ID", "Mode", "Scope", "Shortcuts", "Writeback"], rows)}

## Runtime

```powershell
python -m self_actualize.runtime.query_phase4_structured_neuron_storage locate "Grand Central Station"
python -m self_actualize.runtime.query_phase4_structured_neuron_storage route --source "Athena FLEET" --target "Ch11 The Helical Manifestation Engine"
python -m self_actualize.runtime.query_phase4_structured_neuron_storage neglect --limit 6
```
"""


def render_dashboard_markdown(dashboard: Dict[str, Any]) -> str:
    validation_rows = [[key, str(value)] for key, value in dashboard["validation"].items()]
    neglect_rows = [[item["surface_id"], item["surface_type"], str(item["score"])] for item in dashboard["top_neglects"]]
    wave_rows = [[item["wave_id"], item["pair_id"], item["objective"]] for item in dashboard["top_waves"]]
    return f"""# Phase 4 Structured Neuron Storage Dashboard

Date: `{dashboard['generated_at'][:10]}`
Generated: `{dashboard['generated_at']}`
Docs gate: `{dashboard['docs_gate']}`

## Counts

- bodies: `{dashboard['body_count']}`
- kernels: `{dashboard['kernel_count']}`
- nodes: `{dashboard['node_count']}`
- pairs: `{dashboard['pair_count']}`
- waves: `{dashboard['wave_count']}`
- neglect signals: `{dashboard['neglect_count']}`
- weave candidates: `{dashboard['weave_count']}`
- receipts: `{dashboard['receipt_count']}`

## Validation

{markdown_table(["Check", "Pass"], validation_rows)}

## Top Neglects

{markdown_table(["Surface", "Type", "Score"], neglect_rows)}

## Top Waves

{markdown_table(["Wave", "Pair", "Objective"], wave_rows)}
"""


def render_phase4_ledger_markdown(
    body_registry: Dict[str, Any],
    kernel_registry: Dict[str, Any],
    pair_registry: Dict[str, Any],
    dashboard: Dict[str, Any],
) -> str:
    body_rows = [
        [body["body_id"], body["root"], body["status"], body["authority"], body["dock"]]
        for body in body_registry["bodies"]
    ]
    kernel_rows = [
        [kernel["kernel_id"], kernel["source_title"], kernel["element"], kernel["body_binding"], ", ".join(kernel["appendix_stack"])]
        for kernel in kernel_registry["kernels"]
    ]
    return f"""# Phase 4 Structured Neuron Storage Ledger

Date: `{dashboard['generated_at'][:10]}`
Generated: `{dashboard['generated_at']}`

## Body Registry

{markdown_table(["ID", "Root", "Status", "Authority", "Dock"], body_rows)}

## Kernel Registry

{markdown_table(["ID", "Source", "Element", "Body", "Appendix stack"], kernel_rows)}

## Pair Field

- ordered pairs: `{pair_registry['summary']['pair_count']}`
- max neglect score: `{pair_registry['summary']['max_neglect_score']}`
- min neglect score: `{pair_registry['summary']['min_neglect_score']}`
- primary storage truth: `registries + pair records + wave records`
"""


def render_shortcut_markdown(shortcut_registry: Dict[str, Any]) -> str:
    rows = [
        [shortcut["shortcut_id"], shortcut["name"], shortcut["trigger"], shortcut["scoring_rule"], shortcut["stop_condition"]]
        for shortcut in shortcut_registry["shortcuts"]
    ]
    return f"""# Phase 4 Shortcut Registry

{markdown_table(["ID", "Name", "Trigger", "Scoring", "Stop"], rows)}
"""


def render_neglect_markdown(neglect_registry: Dict[str, Any]) -> str:
    rows = [
        [signal["neglect_id"], signal["surface_id"], signal["surface_type"], signal["gap_type"], str(signal["score"]), signal["nearest_bridge"]]
        for signal in sorted(
            neglect_registry["signals"],
            key=lambda item: (-item["score"], item["surface_id"]),
        )[:24]
    ]
    return f"""# Phase 4 Neglect Signal Ledger

{markdown_table(["ID", "Surface", "Type", "Gap", "Score", "Nearest bridge"], rows)}
"""


def render_weave_markdown(weave_registry: Dict[str, Any]) -> str:
    rows = [
        [
            candidate["weave_id"],
            candidate.get("bridge_edge_id", "-") or "-",
            candidate["src"],
            candidate["dst"],
            str(candidate["expected_gain"]),
            " -> ".join(candidate["promotion_route"]),
        ]
        for candidate in weave_registry["candidates"]
    ]
    return f"""# Phase 4 Weave Candidate Ledger

{markdown_table(["ID", "Bridge Edge", "Source", "Target", "Expected gain", "Route"], rows)}
"""


def render_replay_markdown(replay_registry: Dict[str, Any]) -> str:
    rows = [
        [receipt["action_id"], receipt["mode"], receipt["stop_condition"], ", ".join(receipt["active_shortcuts"]), receipt["outcome"]]
        for receipt in replay_registry["receipts"]
    ]
    return f"""# Phase 4 Replay Receipt Ledger

{markdown_table(["ID", "Mode", "Stop", "Shortcuts", "Outcome"], rows)}
"""


def render_runtime_markdown(dashboard: Dict[str, Any]) -> str:
    return f"""# Phase 4 Structured Neuron Storage Runtime

Date: `{dashboard['generated_at'][:10]}`
Generated: `{dashboard['generated_at']}`
Docs gate: `{dashboard['docs_gate']}`

This runtime mirror keeps the Phase 4 registries readable from the mycelium side.

## Active Runtime Files

- `self_actualize/phase4_body_registry.json`
- `self_actualize/phase4_kernel_registry.json`
- `self_actualize/phase4_node_registry.json`
- `self_actualize/phase4_pair_registry.json`
- `self_actualize/phase4_wave_registry.json`
- `self_actualize/phase4_shortcut_registry.json`
- `self_actualize/phase4_exploration_queries.json`
- `self_actualize/phase4_neglect_signals.json`
- `self_actualize/phase4_weave_candidates.json`
- `self_actualize/phase4_replay_receipts.json`

## Regeneration

```powershell
python -m self_actualize.runtime.derive_phase4_structured_neuron_storage
```
"""


def render_deep_pair_field_markdown(
    kernel_registry: Dict[str, Any],
    pair_registry: Dict[str, Any],
) -> str:
    kernel_rows = [
        [kernel["kernel_id"], kernel["source_title"], kernel["body_binding"], ", ".join(kernel["appendix_stack"])]
        for kernel in kernel_registry["kernels"]
    ]
    top_pairs = sorted(
        pair_registry["pairs"],
        key=lambda item: (-item["witness_floor"], item["pair_id"]),
    )[:12]
    pair_rows = [
        [pair["pair_id"], pair["relation_law"], pair["dock"], str(pair["witness_floor"]), str(pair["neglect_score"])]
        for pair in top_pairs
    ]
    return f"""# Phase 4 Structured Pair Field

This file is the human mirror of the canonical Phase 4 kernel and pair registries
stored in this deep-root matrix folder.

## Kernels

{markdown_table(["Kernel", "Source", "Body", "Appendix stack"], kernel_rows)}

## Highest-Witness Pair Slices

{markdown_table(["Pair", "Relation", "Dock", "Witness", "Neglect"], pair_rows)}
"""


def render_receipt_markdown(dashboard: Dict[str, Any]) -> str:
    outputs = [
        BODY_REGISTRY_JSON_PATH, KERNEL_REGISTRY_JSON_PATH, NODE_REGISTRY_JSON_PATH,
        PAIR_REGISTRY_JSON_PATH, WAVE_REGISTRY_JSON_PATH, SHORTCUT_REGISTRY_JSON_PATH,
        QUERY_REGISTRY_JSON_PATH, NEGLECT_REGISTRY_JSON_PATH, WEAVE_REGISTRY_JSON_PATH,
        REPLAY_REGISTRY_JSON_PATH, DASHBOARD_JSON_PATH, DEEP_KERNEL_JSON_PATH,
        DEEP_PAIR_JSON_PATH, SCHEMA_STORAGE_MD_PATH, SCHEMA_QUERY_MD_PATH, OVERVIEW_MD_PATH,
        EDGE_MD_PATH, BODY_POINTERS_MD_PATH, QUERY_PRESETS_MD_PATH, DASHBOARD_MD_PATH,
        LEDGER_MD_PATH, SHORTCUTS_MD_PATH, NEGLECT_MD_PATH, WEAVE_MD_PATH, REPLAY_MD_PATH,
        RUNTIME_MD_PATH, DEEP_PAIR_FIELD_MD_PATH,
    ]
    output_lines = "\n".join(f"- `{path}`" for path in outputs)
    return f"""# Phase 4 Structured Neuron Storage Receipt

- Generated: `{dashboard['generated_at']}`
- Command: `{DERIVATION_COMMAND}`
- Docs gate: `{dashboard['docs_gate']}`
- Canonical scope: `{dashboard['canonical_scope']}`

## Outputs

{output_lines}

## Counts

- bodies: `{dashboard['body_count']}`
- kernels: `{dashboard['kernel_count']}`
- nodes: `{dashboard['node_count']}`
- pairs: `{dashboard['pair_count']}`
- waves: `{dashboard['wave_count']}`
- weave candidates: `{dashboard['weave_count']}`
- replay receipts: `{dashboard['receipt_count']}`
"""


def write_outputs(
    body_registry: Dict[str, Any],
    kernel_registry: Dict[str, Any],
    node_registry: Dict[str, Any],
    pair_registry: Dict[str, Any],
    wave_registry: Dict[str, Any],
    shortcut_registry: Dict[str, Any],
    query_registry: Dict[str, Any],
    neglect_registry: Dict[str, Any],
    weave_registry: Dict[str, Any],
    replay_registry: Dict[str, Any],
    dashboard: Dict[str, Any],
) -> int:
    for path, payload in [
        (BODY_REGISTRY_JSON_PATH, body_registry),
        (KERNEL_REGISTRY_JSON_PATH, kernel_registry),
        (NODE_REGISTRY_JSON_PATH, node_registry),
        (PAIR_REGISTRY_JSON_PATH, pair_registry),
        (WAVE_REGISTRY_JSON_PATH, wave_registry),
        (SHORTCUT_REGISTRY_JSON_PATH, shortcut_registry),
        (QUERY_REGISTRY_JSON_PATH, query_registry),
        (NEGLECT_REGISTRY_JSON_PATH, neglect_registry),
        (WEAVE_REGISTRY_JSON_PATH, weave_registry),
        (REPLAY_REGISTRY_JSON_PATH, replay_registry),
        (DASHBOARD_JSON_PATH, dashboard),
        (BODY_REGISTRY_JSON_MIRROR, body_registry),
        (KERNEL_REGISTRY_JSON_MIRROR, kernel_registry),
        (NODE_REGISTRY_JSON_MIRROR, node_registry),
        (PAIR_REGISTRY_JSON_MIRROR, pair_registry),
        (WAVE_REGISTRY_JSON_MIRROR, wave_registry),
        (SHORTCUT_REGISTRY_JSON_MIRROR, shortcut_registry),
        (QUERY_REGISTRY_JSON_MIRROR, query_registry),
        (NEGLECT_REGISTRY_JSON_MIRROR, neglect_registry),
        (WEAVE_REGISTRY_JSON_MIRROR, weave_registry),
        (REPLAY_REGISTRY_JSON_MIRROR, replay_registry),
        (DASHBOARD_JSON_MIRROR, dashboard),
        (DEEP_KERNEL_JSON_PATH, kernel_registry),
        (DEEP_PAIR_JSON_PATH, pair_registry),
    ]:
        write_json(path, payload)

    write_text(SCHEMA_STORAGE_MD_PATH, render_storage_schema_markdown(shortcut_registry))
    write_text(SCHEMA_QUERY_MD_PATH, render_query_schema_markdown(shortcut_registry, query_registry))
    write_text(OVERVIEW_MD_PATH, render_overview_markdown(dashboard))
    write_text(EDGE_MD_PATH, render_edge_markdown(weave_registry))
    write_text(BODY_POINTERS_MD_PATH, render_body_pointers_markdown(body_registry))
    write_text(QUERY_PRESETS_MD_PATH, render_query_presets_markdown(query_registry))
    write_text(DASHBOARD_MD_PATH, render_dashboard_markdown(dashboard))
    write_text(LEDGER_MD_PATH, render_phase4_ledger_markdown(body_registry, kernel_registry, pair_registry, dashboard))
    write_text(SHORTCUTS_MD_PATH, render_shortcut_markdown(shortcut_registry))
    write_text(NEGLECT_MD_PATH, render_neglect_markdown(neglect_registry))
    write_text(WEAVE_MD_PATH, render_weave_markdown(weave_registry))
    write_text(REPLAY_MD_PATH, render_replay_markdown(replay_registry))
    write_text(RUNTIME_MD_PATH, render_runtime_markdown(dashboard))
    write_text(DEEP_PAIR_FIELD_MD_PATH, render_deep_pair_field_markdown(kernel_registry, pair_registry))
    write_text(RECEIPT_MD_PATH, render_receipt_markdown(dashboard))

    print(f"Wrote {BODY_REGISTRY_JSON_PATH}")
    print(f"Wrote {KERNEL_REGISTRY_JSON_PATH}")
    print(f"Wrote {NODE_REGISTRY_JSON_PATH}")
    print(f"Wrote {PAIR_REGISTRY_JSON_PATH}")
    print(f"Wrote {WAVE_REGISTRY_JSON_PATH}")
    print(f"Wrote {SHORTCUT_REGISTRY_JSON_PATH}")
    print(f"Wrote {QUERY_REGISTRY_JSON_PATH}")
    print(f"Wrote {NEGLECT_REGISTRY_JSON_PATH}")
    print(f"Wrote {WEAVE_REGISTRY_JSON_PATH}")
    print(f"Wrote {REPLAY_REGISTRY_JSON_PATH}")
    print(f"Wrote {DASHBOARD_JSON_PATH}")
    print(f"Wrote {DEEP_KERNEL_JSON_PATH}")
    print(f"Wrote {DEEP_PAIR_JSON_PATH}")
    print(f"Wrote {DASHBOARD_MD_PATH}")
    return 0


def main() -> int:
    docs_gate = parse_docs_gate(DOCS_GATE_PATH.read_text(encoding="utf-8"))
    body_rows, anchor_rows = parse_root_basis(ROOT_BASIS_PATH.read_text(encoding="utf-8"))
    station_payload = load_json(STATION_REGISTRY_JSON_PATH)
    commissure_payload = load_json(COMMISSURE_JSON_PATH)
    weight_payload = load_json(WEIGHT_JSON_PATH)
    tunnel_payload = load_json(TUNNEL_JSON_PATH)

    body_registry = build_body_registry(
        body_rows,
        anchor_rows,
        station_payload,
        commissure_payload,
        weight_payload,
        docs_gate,
    )
    kernel_registry = build_kernel_registry(
        parse_canonical_sources(CANONICAL_SOURCES_PATH.read_text(encoding="utf-8")),
        body_registry,
        docs_gate,
    )
    pair_registry = build_pair_registry(kernel_registry, body_registry, docs_gate)
    node_registry = build_node_registry(body_registry, kernel_registry, docs_gate)
    shortcut_registry = build_shortcut_registry(docs_gate)
    query_registry = build_query_registry(body_registry, shortcut_registry, docs_gate)
    neglect_registry = build_neglect_registry(body_registry, pair_registry, docs_gate)
    weave_registry = build_weave_registry(body_registry, pair_registry, neglect_registry, docs_gate)
    wave_registry = build_wave_registry(pair_registry, docs_gate)

    registries = {
        "docs_gate": docs_gate,
        "body_registry": body_registry,
        "kernel_registry": kernel_registry,
        "node_registry": node_registry,
        "pair_registry": pair_registry,
        "wave_registry": wave_registry,
        "shortcut_registry": shortcut_registry,
        "query_registry": query_registry,
        "neglect_registry": neglect_registry,
        "weave_registry": weave_registry,
        "weight_exchange": {**weight_payload, "authority_surface": str(WEIGHT_JSON_PATH)},
        "commissure_ledger": {**commissure_payload, "authority_surface": str(COMMISSURE_JSON_PATH)},
        "station_registry": station_payload,
        "tunnels": tunnel_payload,
    }
    replay_registry = build_replay_registry(registries, docs_gate)
    registries["replay_registry"] = replay_registry
    dashboard = build_dashboard(registries, docs_gate)

    return write_outputs(
        body_registry, kernel_registry, node_registry, pair_registry, wave_registry,
        shortcut_registry, query_registry, neglect_registry, weave_registry,
        replay_registry, dashboard
    )


if __name__ == "__main__":
    raise SystemExit(main())
