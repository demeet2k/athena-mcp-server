from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
FAMILY_SURFACE_PATH = (
    SELF_ACTUALIZE_ROOT / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_athena_fleet.md"
)
ROUTE_MAP_PATH = (
    SELF_ACTUALIZE_ROOT / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_athena_fleet_route_map.md"
)
ROUTE_SURFACE_PATH = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "nervous_system"
    / "routes"
    / "whole_crystal"
    / "ROUTE_athena_fleet.md"
)
BRIDGE_ROUTE_PATHS = {
    "BF-CS-001": (
        SELF_ACTUALIZE_ROOT
        / "mycelium_brain"
        / "nervous_system"
        / "routes"
        / "whole_crystal"
        / "bridge_families"
        / "ROUTE_bf_cs_001.md"
    ),
    "BF-CS-003": (
        SELF_ACTUALIZE_ROOT
        / "mycelium_brain"
        / "nervous_system"
        / "routes"
        / "whole_crystal"
        / "bridge_families"
        / "ROUTE_bf_cs_003.md"
    ),
}
DIRECT_EDGES_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "CRYSTAL_DIRECT_SYNAPSE_EDGES.md"
BRIDGE_LEDGER_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "WHOLE_CRYSTAL_BRIDGE_LEDGER.md"
HANDOFF_PROTOCOL_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SYNAPTIC_HANDOFF_PROTOCOL.md"
CLUSTER_RECEIPT_PATH = (
    SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts" / "2026-03-12_athena_fleet_cluster_promotion.md"
)
QSHRINK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
CAPSULE_WITNESS_PATHS = [
    NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "athena_fleet" / "01_athena_fleet_tesseract_branch.md",
    NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "athena_fleet" / "02_athena_fleet.md",
    NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "athena_fleet" / "03_athena_fleet.md",
]
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "athena_fleet_bridge_registry.json"

DERIVATION_VERSION = "2026-03-13.athena-fleet.bridge.registry.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_athena_fleet_bridge_registry"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def truth_value(text: str, default: str = "AMBIG") -> str:
    match = re.search(r"Truth:\s*`([^`]+)`", text)
    return match.group(1) if match else default


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"## {re.escape(heading)}\s*(.*?)(?=\n## |\Z)", text, re.S)
    return match.group(1).strip() if match else ""


def bullet_value(text: str, prefix: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip("`")
    return ""


def parse_root_basis() -> dict[str, Any]:
    text = read_text(ROOT_BASIS_PATH)
    match = re.search(
        r"\|\s*(A16)\s*\|\s*`Athena FLEET`\s*\|\s*`?([^|`]+?)`?\s*\|\s*`?([^|`]+?)`?\s*\|\s*([^|]+?)\s*\|",
        text,
    )
    return {
        "path": rel(ROOT_BASIS_PATH),
        "exists": bool(match),
        "body_id": match.group(1) if match else "",
        "indexed_count": match.group(2).strip() if match else "",
        "status": match.group(3).strip() if match else "",
        "role": match.group(4).strip() if match else "",
    }


def parse_direct_edges(edge_ids: set[str]) -> list[dict[str, Any]]:
    text = read_text(DIRECT_EDGES_PATH)
    edges: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\|\s*(CS-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|?\s*$"
    )
    for raw_line in text.splitlines():
        match = pattern.match(raw_line.strip())
        if not match or match.group(1) not in edge_ids:
            continue
        edges.append(
            {
                "edge_id": match.group(1),
                "source": match.group(2).strip(),
                "target": match.group(3).strip(),
                "relation": match.group(4).strip(),
                "weight": match.group(5).strip(),
                "route": match.group(6).strip(),
                "path": rel(DIRECT_EDGES_PATH),
            }
        )
    return sorted(edges, key=lambda item: item["edge_id"])


def parse_bridge_ledger_entries(family_ids: set[str]) -> list[dict[str, Any]]:
    text = read_text(BRIDGE_LEDGER_PATH)
    entries: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\|\s*(BF-CS-\d+)\s*\|\s*(CS-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|?\s*$"
    )
    for raw_line in text.splitlines():
        match = pattern.match(raw_line.strip())
        if not match or match.group(1) not in family_ids:
            continue
        entries.append(
            {
                "bridge_family_id": match.group(1),
                "edge_id": match.group(2),
                "source": match.group(3).strip(),
                "target": match.group(4).strip(),
                "authority": match.group(5).strip(),
                "primary_writeback": match.group(6).strip().replace("\\", "/"),
                "path": rel(BRIDGE_LEDGER_PATH),
            }
        )
    return sorted(entries, key=lambda item: item["bridge_family_id"])


def parse_bridge_route(path: Path, bridge_family_id: str) -> dict[str, Any]:
    text = read_text(path)
    return {
        "bridge_family_id": bridge_family_id,
        "path": rel(path),
        "exists": path.exists(),
        "truth": truth_value(text),
        "edge_id": bullet_value(markdown_section(text, "Bridge"), "- edge id: "),
        "primary_writeback_target": bullet_value(markdown_section(text, "Bridge"), "- primary writeback target: "),
        "route": re.search(r"## Route\s*`([^`]+)`", text, re.S).group(1)
        if re.search(r"## Route\s*`([^`]+)`", text, re.S)
        else "",
    }


def parse_handoff_packets(packet_ids: set[str]) -> list[dict[str, Any]]:
    text = read_text(HANDOFF_PROTOCOL_PATH)
    packets: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\|\s*(SHP-\d+)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*(A\d+)\s*\|\s*(A\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|?\s*$"
    )
    for raw_line in text.splitlines():
        match = pattern.match(raw_line.strip())
        if not match or match.group(1) not in packet_ids:
            continue
        packets.append(
            {
                "packet_id": match.group(1),
                "source_agent": match.group(4).strip(),
                "target_agent": match.group(5).strip(),
                "source_body": match.group(6).strip(),
                "target_body": match.group(7).strip(),
                "trigger": match.group(8).strip(),
                "route": match.group(9).strip(),
                "path": rel(HANDOFF_PROTOCOL_PATH),
            }
        )
    return sorted(packets, key=lambda item: item["packet_id"])


def parse_external_deficits() -> list[dict[str, Any]]:
    payload = json.loads(QSHRINK_INTEGRATION_PATH.read_text(encoding="utf-8"))
    deficits = []
    for leg in payload.get("corridor_legs", []):
        if leg.get("id") not in {"LEG-C2", "LEG-C3", "LEG-C4"}:
            continue
        deficits.append(
            {
                "id": leg.get("id", ""),
                "name": leg.get("name", ""),
                "truth": leg.get("truth", ""),
                "meaning": leg.get("meaning", ""),
                "surfaces": leg.get("surfaces", []),
            }
        )
    return sorted(deficits, key=lambda item: item["id"])


def parse_route_surface() -> dict[str, Any]:
    text = read_text(ROUTE_SURFACE_PATH)
    law_lines = [line.strip()[2:] for line in markdown_section(text, "Law").splitlines() if line.strip().startswith("- ")]
    authority_state = ""
    route_state = ""
    for line in law_lines:
        if line.startswith("authority"):
            authority_state = line.split("`")[1] if "`" in line else line
        if line.lower().startswith("route"):
            route_state = line
    return {
        "path": rel(ROUTE_SURFACE_PATH),
        "exists": ROUTE_SURFACE_PATH.exists(),
        "authority_state": authority_state,
        "route_state": route_state,
        "law": law_lines,
        "main_transfer": re.search(r"## Main transfer\s*`([^`]+)`", text, re.S).group(1)
        if re.search(r"## Main transfer\s*`([^`]+)`", text, re.S)
        else "",
    }


def parse_cluster_receipt() -> dict[str, Any]:
    text = read_text(CLUSTER_RECEIPT_PATH)
    status = bullet_value(text, "- status: ")
    return {
        "path": rel(CLUSTER_RECEIPT_PATH),
        "exists": CLUSTER_RECEIPT_PATH.exists(),
        "status": status,
        "docs_gate": bullet_value(text, "- docs_gate: "),
    }


def capsule_witnesses() -> list[dict[str, Any]]:
    return [{"path": rel(path), "exists": path.exists()} for path in CAPSULE_WITNESS_PATHS]


def build_record() -> dict[str, Any]:
    family_text = read_text(FAMILY_SURFACE_PATH)
    route_map_text = read_text(ROUTE_MAP_PATH)
    route_surface = parse_route_surface()
    bridge_routes = [
        parse_bridge_route(path=path, bridge_family_id=bridge_family_id)
        for bridge_family_id, path in sorted(BRIDGE_ROUTE_PATHS.items())
    ]
    bridge_edges = parse_direct_edges(edge_ids={"CS-001", "CS-003"})
    bridge_ledger_entries = parse_bridge_ledger_entries(family_ids={"BF-CS-001", "BF-CS-003"})
    handoff_packets = parse_handoff_packets(packet_ids={"SHP-002", "SHP-004"})
    cluster_receipt = parse_cluster_receipt()
    docs_gate_status = swarm_board.docs_gate_status()["status"]
    return {
        "body_id": "A16",
        "truth": truth_value(family_text, "NEAR"),
        "authority_state": route_surface["authority_state"] or truth_value(family_text, "NEAR"),
        "route_state": route_surface["route_state"] or "local-first and atlas-indexed",
        "proof_target": "graph-first",
        "promotion_bar": "A16_local_closure",
        "root_basis": parse_root_basis(),
        "family_surface": {
            "path": rel(FAMILY_SURFACE_PATH),
            "exists": FAMILY_SURFACE_PATH.exists(),
            "truth": truth_value(family_text, "NEAR"),
        },
        "route_map_surface": {
            "path": rel(ROUTE_MAP_PATH),
            "exists": ROUTE_MAP_PATH.exists(),
            "next_route": markdown_section(route_map_text, "Next route").replace("`", "").strip(),
        },
        "route_surface": route_surface,
        "capsule_witnesses": capsule_witnesses(),
        "bridge_edges": bridge_edges,
        "bridge_routes": bridge_routes,
        "bridge_ledger_entries": bridge_ledger_entries,
        "handoff_packets": handoff_packets,
        "cluster_receipt": cluster_receipt,
        "external_deficits": parse_external_deficits(),
        "docs_gate_status": docs_gate_status,
    }


def build_payload() -> dict[str, Any]:
    record = build_record()
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "records": [record],
        "summary": {
            "record_count": 1,
            "body_ids": [record["body_id"]],
            "docs_gate_status": record["docs_gate_status"],
            "external_deficit_count": len(record["external_deficits"]),
        },
    }


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    print(f"Wrote Athena FLEET bridge registry: {OUTPUT_JSON_PATH}")
    print(f"Body ids: {', '.join(payload['summary']['body_ids'])}")
    print(f"Docs gate: {payload['summary']['docs_gate_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
