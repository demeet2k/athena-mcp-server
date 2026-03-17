from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import swarm_board
from .derive_athena_fleet_bridge_registry import (
    CLUSTER_RECEIPT_PATH,
    OUTPUT_JSON_PATH as REGISTRY_PATH,
    WORKSPACE_ROOT,
)


SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "athena_fleet_bridge_verification.json"
GRAPH_CONTRACTION_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "50_CORPUS_CAPSULES" / "athena_fleet" / "04_athena_fleet_graph_contraction.md"
)
RECEIPT_PATH = (
    SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts" / "2026-03-13_front_int_athena_fleet_bridge_verification.md"
)

DERIVATION_VERSION = "2026-03-13.athena-fleet.bridge.verify.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_athena_fleet_bridge"
NEXT_SEED_SUCCESS = "Q35"
NEXT_SEED_FAIL = "FRONT-INT-ATHENA-FLEET-BRIDGE"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def load_record() -> dict[str, Any]:
    payload = load_registry()
    ensure(payload.get("records"), "bridge registry is empty")
    return payload["records"][0]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"label": label, "status": "OK", "details": fn()}
    except Exception as exc:  # noqa: BLE001
        return {"label": label, "status": "FAIL", "details": str(exc)}


def verify_root_basis() -> dict[str, Any]:
    record = load_record()
    root_basis = record["root_basis"]
    ensure(root_basis["exists"], "A16 is missing from ROOT_BASIS_MAP")
    ensure(root_basis["body_id"] == "A16", f"unexpected body id: {root_basis['body_id']}")
    return root_basis


def verify_family_route_surfaces() -> dict[str, Any]:
    record = load_record()
    family_surface = record["family_surface"]
    route_surface = record["route_surface"]
    route_map_surface = record["route_map_surface"]
    ensure(family_surface["exists"], "family surface is missing")
    ensure(route_surface["exists"], "route surface is missing")
    ensure(route_map_surface["exists"], "route-map surface is missing")
    return {
        "family_surface": family_surface["path"],
        "route_surface": route_surface["path"],
        "route_map_surface": route_map_surface["path"],
    }


def verify_direct_edges_match_bridge_routes() -> dict[str, Any]:
    record = load_record()
    edges = {item["edge_id"]: item for item in record["bridge_edges"]}
    bridge_routes = {item["bridge_family_id"]: item for item in record["bridge_routes"]}
    expected = {
        "BF-CS-001": ("CS-001", "A16 -> GCL+GCR -> GCZ -> A06"),
        "BF-CS-003": ("CS-003", "A16 -> GCL+GCR -> GCP -> A15"),
    }
    matched: dict[str, str] = {}
    for bridge_family_id, (edge_id, expected_route) in expected.items():
        ensure(edge_id in edges, f"missing direct edge {edge_id}")
        ensure(bridge_family_id in bridge_routes, f"missing bridge route {bridge_family_id}")
        ensure(edges[edge_id]["route"] == expected_route, f"{edge_id} direct route drifted")
        ensure(bridge_routes[bridge_family_id]["edge_id"] == edge_id, f"{bridge_family_id} edge id drifted")
        ensure(bridge_routes[bridge_family_id]["route"] == expected_route, f"{bridge_family_id} route drifted")
        matched[bridge_family_id] = expected_route
    return matched


def verify_bridge_ledger_authority() -> dict[str, Any]:
    record = load_record()
    entries = {item["bridge_family_id"]: item for item in record["bridge_ledger_entries"]}
    for bridge_family_id in ("BF-CS-001", "BF-CS-003"):
        ensure(bridge_family_id in entries, f"{bridge_family_id} missing from bridge ledger")
        ensure(entries[bridge_family_id]["authority"] == "authoritative", f"{bridge_family_id} is not authoritative")
    return {item["bridge_family_id"]: item["primary_writeback"] for item in entries.values()}


def verify_handoff_packets() -> dict[str, Any]:
    record = load_record()
    packets = {(item["source_body"], item["target_body"]): item for item in record["handoff_packets"]}
    ensure(("A16", "A06") in packets, "handoff packet A16 -> A06 is missing")
    ensure(("A16", "A15") in packets, "handoff packet A16 -> A15 is missing")
    return {
        "A16->A06": packets[("A16", "A06")]["route"],
        "A16->A15": packets[("A16", "A15")]["route"],
    }


def verify_cluster_receipt() -> dict[str, Any]:
    record = load_record()
    receipt = record["cluster_receipt"]
    ensure(receipt["exists"], "Athena FLEET cluster promotion receipt is missing")
    ensure(CLUSTER_RECEIPT_PATH.exists(), "Athena FLEET cluster promotion receipt path is missing on disk")
    return receipt


def verify_external_deficits() -> dict[str, Any]:
    record = load_record()
    deficits = {item["id"]: item for item in record["external_deficits"]}
    for deficit_id in ("LEG-C2", "LEG-C3", "LEG-C4"):
        ensure(deficit_id in deficits, f"missing external deficit {deficit_id}")
    return {deficit_id: deficits[deficit_id]["truth"] for deficit_id in sorted(deficits)}


def verify_docs_gate_honesty() -> dict[str, Any]:
    record = load_record()
    registry_status = record["docs_gate_status"]
    live_status = swarm_board.docs_gate_status()["status"]
    ensure(registry_status == live_status, f"docs gate drifted: registry={registry_status} live={live_status}")
    if live_status == "BLOCKED":
        creds = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
        token = WORKSPACE_ROOT / "Trading Bot" / "token.json"
        ensure(not (creds.exists() and token.exists()), "docs gate says blocked but OAuth files exist")
    return {"docs_gate_status": live_status}


def build_payload() -> dict[str, Any]:
    checks = [
        run_check("root_basis", verify_root_basis),
        run_check("family_route_surfaces", verify_family_route_surfaces),
        run_check("direct_edges_match_bridge_routes", verify_direct_edges_match_bridge_routes),
        run_check("bridge_ledger_authority", verify_bridge_ledger_authority),
        run_check("handoff_packets", verify_handoff_packets),
        run_check("cluster_receipt", verify_cluster_receipt),
        run_check("external_deficits", verify_external_deficits),
        run_check("docs_gate_honesty", verify_docs_gate_honesty),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    truth = "OK" if not failed else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "promotion_bar": "A16_local_closure",
        "proof_target": "graph-first",
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
        "eligible_for_promotion": truth == "OK",
        "next_seed": NEXT_SEED_SUCCESS if truth == "OK" else NEXT_SEED_FAIL,
    }


def render_graph_contraction(record: dict[str, Any], verification: dict[str, Any]) -> str:
    truth = verification["truth"]
    lines = [
        "# Athena FLEET Graph Contraction",
        "",
        "Date: `2026-03-13`",
        f"Truth: `{truth}`",
        "Body: `A16`",
        "Promotion bar: `A16 local closure only`",
        f"Docs gate: `{record['docs_gate_status']}`",
        "",
        "## Family",
        "",
        f"- family_surface: `{record['family_surface']['path']}`",
        f"- family_truth: `{record['family_surface']['truth']}`",
        "",
        "## Route",
        "",
        f"- route_surface: `{record['route_surface']['path']}`",
        f"- authority_state: `{record['authority_state']}`",
        f"- route_state: `{record['route_state']}`",
        "",
        "## Direct Edges",
        "",
    ]
    for edge in record["bridge_edges"]:
        lines.append(
            f"- `{edge['edge_id']}` `{edge['source']} -> {edge['target']}` :: `{edge['route']}` :: weight=`{edge['weight']}`"
        )
    lines.extend(["", "## Bridge-Family Routes", ""])
    for route in record["bridge_routes"]:
        lines.append(
            f"- `{route['bridge_family_id']}` :: edge=`{route['edge_id']}` :: truth=`{route['truth']}` :: route=`{route['route']}`"
        )
    lines.extend(["", "## Handoff Packets", ""])
    for packet in record["handoff_packets"]:
        lines.append(
            f"- `{packet['packet_id']}` :: `{packet['source_body']} -> {packet['target_body']}` :: `{packet['route']}`"
        )
    lines.extend(["", "## Remaining External Deficits", ""])
    for deficit in record["external_deficits"]:
        lines.append(f"- `{deficit['id']}` `{deficit['name']}` :: truth=`{deficit['truth']}` :: {deficit['meaning']}")
    lines.extend(
        [
            "",
            "## Law",
            "",
            "- `A16` is now treated as locally closed when the family surface, route surface, direct edges, bridge-family routes, and handoff packets agree.",
            "- `LEG-C2`, `LEG-C3`, and `LEG-C4` remain explicit downstream deficits and do not invalidate local `A16` closure.",
            f"- next_seed: `{verification['next_seed']}`",
        ]
    )
    return "\n".join(lines)


def render_receipt(record: dict[str, Any], verification: dict[str, Any]) -> str:
    truth = verification["truth"]
    lines = [
        "# 2026-03-13 FRONT-INT-ATHENA-FLEET-BRIDGE Verification",
        "",
        "## Outcome",
        "",
        f"- truth: `{truth}`",
        f"- registry_path: `{REGISTRY_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        f"- verification_path: `{OUTPUT_JSON_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        f"- graph_contraction_path: `{GRAPH_CONTRACTION_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        f"- cluster_receipt: `{record['cluster_receipt']['path']}`",
        "",
        "## Local Closure Bundle",
        "",
        f"- root_basis: `{record['root_basis']['path']}`",
        f"- family_surface: `{record['family_surface']['path']}`",
        f"- route_surface: `{record['route_surface']['path']}`",
        f"- route_map_surface: `{record['route_map_surface']['path']}`",
        f"- direct_edges: `{', '.join(edge['edge_id'] for edge in record['bridge_edges'])}`",
        f"- bridge_routes: `{', '.join(route['bridge_family_id'] for route in record['bridge_routes'])}`",
        f"- handoff_packets: `{', '.join(packet['packet_id'] for packet in record['handoff_packets'])}`",
        "",
        "## Remaining External Deficits",
        "",
    ]
    for deficit in record["external_deficits"]:
        lines.append(f"- `{deficit['id']}` `{deficit['truth']}` :: {deficit['meaning']}")
    lines.extend(
        [
            "",
            "## Next Seed",
            "",
            f"- `{verification['next_seed']}`",
            "- macro note: `Q41` may remain the macro synchronization front while `FRONT-INT-ATHENA-FLEET-BRIDGE` closes as the local floating-agent frontier",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    record = load_record()
    payload = build_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    write_text(GRAPH_CONTRACTION_PATH, render_graph_contraction(record, payload))
    write_text(RECEIPT_PATH, render_receipt(record, payload))
    print(f"Wrote Athena FLEET bridge verification: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
