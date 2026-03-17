from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from self_actualize.runtime.qshrink_refine_common import (
    QSHRINK_NEXT4_STATE_PATH,
    load_next4_state,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
CAPSULE_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "50_CORPUS_CAPSULES" / "qshrink"
ATHENA_FLEET_ROOT = WORKSPACE_ROOT / "Athena FLEET"
QSHRINK_ECOSYSTEM_ROOT = ATHENA_FLEET_ROOT / "QSHRINK2_CORPUS_ECOSYSTEM"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"

QSHRINK_CLOUD_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
Q42_RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
Q42_SEED_PACKET_WITNESS_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

DEEP_ROOT = MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
DEEP_ROOT_README_PATH = DEEP_ROOT / "README.md"
DEEP_ROOT_MATRIX_INDEX_PATH = DEEP_ROOT / "05_MATRIX_16X16" / "00_INDEX.md"
DEEP_ROOT_LEVEL3_PATH = DEEP_ROOT / "07_METRO_STACK" / "02_level_3_deeper_neural_map.md"

ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_fractal.json"
OUTPUT_FRACTAL_PATH = QSHRINK_ECOSYSTEM_ROOT / "14_QSHRINK_CORE_CORRIDOR_FRACTAL.md"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "08_qshrink_core_corridor_fractal.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_qs64_20_core_corridor_fractal.md"
OUTPUT_README_PATH = QSHRINK_ECOSYSTEM_ROOT / "README.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_fractal"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_optional_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def docs_gate_detail(cloud: dict, next4_state: dict) -> dict:
    docs_gate = dict(cloud.get("docs_gate", {}))
    docs_gate.setdefault("status", next4_state["docs_gate_status"])
    docs_gate.setdefault("detail", "blocked-by-missing-credentials")
    docs_gate.setdefault("truth", "FAIL")
    docs_gate.setdefault("confirmed_by", str(LIVE_DOCS_GATE_PATH))
    if LIVE_DOCS_GATE_PATH.exists() and "surface_excerpt" not in docs_gate:
        docs_gate["surface_excerpt"] = "\n".join(read_text(LIVE_DOCS_GATE_PATH).splitlines()[:12])
    return docs_gate


def pressure_by_id(cloud: dict, pressure_id: str) -> dict:
    for pressure in cloud.get("ranked_pressures", []):
        if pressure.get("id") == pressure_id:
            return pressure
    return {}


def coerce_route_targets(cloud: dict) -> list[dict]:
    route_targets = list(cloud.get("route_targets", []))
    temple_target = {
        "body": "Temple",
        "target": "self_actualize/mycelium_brain/ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
    }
    if temple_target not in route_targets:
        route_targets.append(temple_target)
    return route_targets


def build_payload() -> dict:
    cloud = load_optional_json(QSHRINK_CLOUD_PATH, {"truth": "NEAR"})
    network = load_optional_json(QSHRINK_NETWORK_INTEGRATION_PATH, {"truth": "NEAR"})
    agent_matrix = load_optional_json(QSHRINK_AGENT_MATRIX_PATH, {"truth": "NEAR"})
    runtime_membrane = load_optional_json(Q42_RUNTIME_MEMBRANE_PATH, {"truth_state": "NEAR"})
    seed_packet = load_optional_json(Q42_SEED_PACKET_WITNESS_PATH, {"truth_state": "NEAR"})
    next4_state = load_next4_state()

    docs_gate = docs_gate_detail(cloud, next4_state)
    pinned_blocker = pressure_by_id(cloud, "P1")
    primary_pressure = pressure_by_id(cloud, "P2")
    secondary_pressure = pressure_by_id(cloud, "P3")
    qshrink_anchor = pressure_by_id(cloud, "P4")
    hall_anchor = pressure_by_id(cloud, "P5")

    recursive_crossings = [
        {
            "id": "X1",
            "name": "runtime-first recursive crossing",
            "body": primary_pressure.get("body", "Athena OS runtime"),
            "supporting_line": primary_pressure.get("supporting_line", "M3 runtime-rail"),
            "truth": runtime_membrane.get("truth_state", primary_pressure.get("truth", "NEAR")),
            "status": primary_pressure.get("selection_state", "PROMOTED_CURRENT"),
            "meaning": "Carry the Cloud-selected runtime pressure through Fractal without letting the witness redefine the operational current Hall step.",
            "evidence": relative_string(Q42_RUNTIME_MEMBRANE_PATH),
        },
        {
            "id": "X2",
            "name": "seed-mirror recursive crossing",
            "body": secondary_pressure.get("body", "ORGIN"),
            "supporting_line": secondary_pressure.get("supporting_line", "M5 seed-rail"),
            "truth": seed_packet.get("truth_state", secondary_pressure.get("truth", "NEAR")),
            "status": secondary_pressure.get("selection_state", "QUEUE_VISIBLE"),
            "meaning": "Preserve the ORGIN route as the secondary recursive follow-on behind the operational Hall lane.",
            "evidence": relative_string(Q42_SEED_PACKET_WITNESS_PATH),
        },
        {
            "id": "X3",
            "name": "governance overlay crossing",
            "body": pinned_blocker.get("body", "Trading Bot"),
            "supporting_line": pinned_blocker.get("supporting_line", "M2 governance-rail"),
            "truth": docs_gate.get("truth", "FAIL"),
            "status": pinned_blocker.get("selection_state", "PINNED_BLOCKER"),
            "meaning": "Keep the blocked Docs gate explicit as external truth while the operational current remains on `QS64-21`.",
            "evidence": relative_string(LIVE_DOCS_GATE_PATH),
        },
    ]

    crossing_hubs = [
        {
            "id": "H1",
            "name": "Athena FLEET ecosystem",
            "role": "corridor relay hub",
            "meaning": "Body-level relay where carried witness memory and dual-track writeback stay coupled.",
            "surfaces": [
                "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md",
                "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/14_QSHRINK_CORE_CORRIDOR_FRACTAL.md",
            ],
        },
        {
            "id": "H2",
            "name": "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE",
            "role": "primary recursive crossing hub",
            "meaning": "Runtime membrane that carries `P2` forward as the primary recursive pressure while `QS64-21` remains operational current.",
            "surfaces": [relative_string(Q42_RUNTIME_MEMBRANE_PATH)],
        },
        {
            "id": "H3",
            "name": "ORGIN seed packet witness",
            "role": "secondary recursive crossing hub",
            "meaning": "Packet-backed seed leg that stays visible behind the runtime-first carrythrough.",
            "surfaces": [relative_string(Q42_SEED_PACKET_WITNESS_PATH)],
        },
        {
            "id": "H4",
            "name": "Hall / queue / restart",
            "role": "public writeback hub",
            "meaning": "Public control surfaces that must agree on carried witness, operational current, next Hall seed, compiled bundle closure, deeper receiver, and blocked external front.",
            "surfaces": [
                "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
                "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
            ],
        },
        {
            "id": "H5",
            "name": "deeper integrated neural network",
            "role": "fractal synthesis hub",
            "meaning": "Deep-root metro stack that supplies the recursive-crossing lens without claiming the current Hall-side pass.",
            "surfaces": [
                relative_string(DEEP_ROOT_README_PATH),
                relative_string(DEEP_ROOT_MATRIX_INDEX_PATH),
                relative_string(DEEP_ROOT_LEVEL3_PATH),
            ],
        },
    ]

    stability_anchors = []
    if qshrink_anchor:
        stability_anchors.append(
            {
                "id": "M1",
                "body": qshrink_anchor.get("body", "QSHRINK"),
                "supporting_line": qshrink_anchor.get("supporting_line", "M1 contraction-rail"),
                "selection_state": qshrink_anchor.get("selection_state", "STABILITY_ANCHOR"),
                "meaning": "Contraction law keeps the recursive carrythrough grounded.",
            }
        )
    if hall_anchor:
        stability_anchors.append(
            {
                "id": "M4",
                "body": hall_anchor.get("body", "Athena FLEET / Hall"),
                "supporting_line": hall_anchor.get("supporting_line", "M4 hall-rail"),
                "selection_state": hall_anchor.get("selection_state", "STABILITY_ANCHOR"),
                "meaning": "Hall replay law keeps Fractal ownerable and restart-safe.",
            }
        )

    fractal_truth = (
        "OK"
        if runtime_membrane.get("truth_state") == "OK"
        and seed_packet.get("truth_state") == "OK"
        and bool(primary_pressure)
        and bool(secondary_pressure)
        else "NEAR"
    )

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": fractal_truth,
        "focus": "core-corridor-fractal-carrythrough",
        "front_id": next4_state["front_id"],
        "mode": next4_state["mode"],
        "witness_role": "carried_witness",
        "carried_witness": next4_state["carried_witness"],
        "operational_current": next4_state["operational_current"],
        "next_hall_seed": next4_state["next_hall_seed"],
        "compiled_bundle": next4_state["compiled_bundle"],
        "deeper_receiver": next4_state["deeper_receiver"],
        "reserve_frontier": next4_state["reserve_frontier"],
        "blocked_external_front": next4_state["blocked_external_front"],
        "docs_gate_status": next4_state["docs_gate_status"],
        "docs_gate": docs_gate,
        "route_targets": coerce_route_targets(cloud),
        "upstream_cloud": {
            "source_path": relative_string(QSHRINK_CLOUD_PATH),
            "truth": cloud.get("truth", "NEAR"),
            "promoted_pressure": {
                "id": primary_pressure.get("id", "P2"),
                "body": primary_pressure.get("body", "Athena OS runtime"),
                "selection_state": primary_pressure.get("selection_state", "PROMOTED_CURRENT"),
            },
            "queued_pressure": {
                "id": secondary_pressure.get("id", "P3"),
                "body": secondary_pressure.get("body", "ORGIN"),
                "selection_state": secondary_pressure.get("selection_state", "QUEUE_VISIBLE"),
            },
            "pinned_blocker": {
                "id": pinned_blocker.get("id", "P1"),
                "body": pinned_blocker.get("body", "Trading Bot"),
                "selection_state": pinned_blocker.get("selection_state", "PINNED_BLOCKER"),
            },
            "inheritance_rule": "Consume Cloud ranking as upstream truth and preserve Fractal as carried witness instead of using it to redefine the operational current step.",
        },
        "recursive_crossings": recursive_crossings,
        "crossing_hubs": crossing_hubs,
        "priority_carrythrough": {
            "pinned_blocker": {
                "id": pinned_blocker.get("id", "P1"),
                "body": pinned_blocker.get("body", "Trading Bot"),
                "supporting_line": pinned_blocker.get("supporting_line", "M2 governance-rail"),
                "truth": docs_gate.get("truth", "FAIL"),
                "status": pinned_blocker.get("selection_state", "PINNED_BLOCKER"),
            },
            "primary_recursive_pressure": {
                "id": primary_pressure.get("id", "P2"),
                "body": primary_pressure.get("body", "Athena OS runtime"),
                "supporting_line": primary_pressure.get("supporting_line", "M3 runtime-rail"),
                "truth": runtime_membrane.get("truth_state", primary_pressure.get("truth", "NEAR")),
                "status": primary_pressure.get("selection_state", "PROMOTED_CURRENT"),
            },
            "secondary_recursive_pressure": {
                "id": secondary_pressure.get("id", "P3"),
                "body": secondary_pressure.get("body", "ORGIN"),
                "supporting_line": secondary_pressure.get("supporting_line", "M5 seed-rail"),
                "truth": seed_packet.get("truth_state", secondary_pressure.get("truth", "NEAR")),
                "status": secondary_pressure.get("selection_state", "QUEUE_VISIBLE"),
            },
            "stability_anchors": stability_anchors,
        },
        "handoff_to_tq04": {
            "frontier": next4_state["deeper_receiver"],
            "state": "LANDED_DEEPER_RECEIVER",
            "why": "Fractal remains the carried witness, `QS64-21` stays operational current, `QS64-22` stays the next Hall seed, and `TQ04` remains the separate landed deeper receiver.",
            "public_writeback_targets": [
                "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
                "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
                "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
            ],
        },
        "source_paths": {
            "next4_state": str(QSHRINK_NEXT4_STATE_PATH),
            "qshrink_connectivity_cloud": str(QSHRINK_CLOUD_PATH),
            "qshrink_network_integration": str(QSHRINK_NETWORK_INTEGRATION_PATH),
            "qshrink_agent_task_matrix": str(QSHRINK_AGENT_MATRIX_PATH),
            "runtime_membrane": str(Q42_RUNTIME_MEMBRANE_PATH),
            "seed_packet_witness": str(Q42_SEED_PACKET_WITNESS_PATH),
        },
        "witness_basis": {
            "cloud_truth": cloud.get("truth", "NEAR"),
            "network_truth": network.get("truth", "NEAR"),
            "agent_matrix_truth": agent_matrix.get("truth", "NEAR"),
            "runtime_membrane_truth": runtime_membrane.get("truth_state", "NEAR"),
            "seed_packet_truth": seed_packet.get("truth_state", "NEAR"),
        },
        "active_basis_documents": [
            relative_string(QSHRINK_NEXT4_STATE_PATH),
            relative_string(QSHRINK_CLOUD_PATH),
            relative_string(Q42_RUNTIME_MEMBRANE_PATH),
            relative_string(Q42_SEED_PACKET_WITNESS_PATH),
            relative_string(DEEP_ROOT_README_PATH),
            relative_string(DEEP_ROOT_MATRIX_INDEX_PATH),
            relative_string(DEEP_ROOT_LEVEL3_PATH),
        ],
        "deprecated_fields": {
            "active_subfront": next4_state["carried_witness"],
            "next_seed": next4_state["next_hall_seed"],
            "reason": "Use carried_witness, operational_current, next_hall_seed, and compiled_bundle instead of letting the Fractal witness redefine the live pass.",
        },
    }


def render_fractal(payload: dict) -> str:
    active_basis = "\n".join(f"- `{item}`" for item in payload["active_basis_documents"])
    route_targets = "\n".join(
        f"- `{target['body']}` -> `{target['target']}`" for target in payload["route_targets"]
    )
    crossings = []
    for crossing in payload["recursive_crossings"]:
        crossings.extend(
            [
                f"### {crossing['id']} `{crossing['name']}`",
                "",
                f"- Body: `{crossing['body']}`",
                f"- Supporting line: `{crossing['supporting_line']}`",
                f"- Truth: `{crossing['truth']}`",
                f"- Status: `{crossing['status']}`",
                f"- Meaning: {crossing['meaning']}",
                f"- Evidence: `{crossing['evidence']}`",
                "",
            ]
        )
    hubs = []
    for hub in payload["crossing_hubs"]:
        hubs.extend(
            [
                f"### {hub['id']} `{hub['name']}`",
                "",
                f"- Role: `{hub['role']}`",
                f"- Meaning: {hub['meaning']}",
                f"- Surfaces: {'; '.join(f'`{surface}`' for surface in hub['surfaces'])}",
                "",
            ]
        )
    anchors = "\n".join(
        f"- `{anchor['id']} {anchor['body']}` / `{anchor['selection_state']}` / `{anchor['supporting_line']}`"
        for anchor in payload["priority_carrythrough"]["stability_anchors"]
    ) or "- none"
    compiled_members = ", ".join(f"`{item}`" for item in payload["compiled_bundle"]["members"])
    return "\n".join(
        [
            "# QSHRINK Core Corridor Fractal",
            "",
            f"- Generated at: `{payload['generated_at']}`",
            f"- Truth: `{payload['truth']}`",
            f"- carried_witness: `{payload['carried_witness']}`",
            f"- operational_current: `{payload['operational_current']}`",
            f"- next_hall_seed: `{payload['next_hall_seed']}`",
            f"- compiled_bundle_terminal: `{payload['compiled_bundle']['terminal']}`",
            f"- docs_gate: `{payload['docs_gate']['detail']}`",
            "",
            "## Omega",
            "",
            "Fractal is now preserved as the carried upstream witness. It inherits the landed Cloud ranking, keeps the Docs blocker pinned externally, carries `P2` as the primary recursive crossing, preserves `P3` as the secondary crossing, keeps `QS64-21` as the operational current Hall pass, releases `QS64-22` only as the next Hall seed, and keeps `TQ04` separate as the landed deeper receiver.",
            "",
            "## Dual-Track Control",
            "",
            f"- carried_witness: `{payload['carried_witness']}`",
            f"- operational_current: `{payload['operational_current']}`",
            f"- next_hall_seed: `{payload['next_hall_seed']}`",
            f"- compiled_bundle_closed: `{payload['compiled_bundle']['closed']}`",
            f"- compiled_bundle_terminal: `{payload['compiled_bundle']['terminal']}`",
            f"- compiled_bundle_members: {compiled_members}",
            f"- deeper_receiver: `{payload['deeper_receiver']}`",
            f"- reserve_frontier: `{payload['reserve_frontier']}`",
            f"- blocked_external_front: `{payload['blocked_external_front']}`",
            "",
            "## Active Basis",
            "",
            active_basis,
            "",
            "## Upstream Cloud",
            "",
            f"- Source path: `{payload['upstream_cloud']['source_path']}`",
            f"- Inherited truth: `{payload['upstream_cloud']['truth']}`",
            f"- Promoted pressure: `{payload['upstream_cloud']['promoted_pressure']['id']} {payload['upstream_cloud']['promoted_pressure']['body']}` / `{payload['upstream_cloud']['promoted_pressure']['selection_state']}`",
            f"- Queued pressure: `{payload['upstream_cloud']['queued_pressure']['id']} {payload['upstream_cloud']['queued_pressure']['body']}` / `{payload['upstream_cloud']['queued_pressure']['selection_state']}`",
            f"- Pinned blocker: `{payload['upstream_cloud']['pinned_blocker']['id']} {payload['upstream_cloud']['pinned_blocker']['body']}` / `{payload['upstream_cloud']['pinned_blocker']['selection_state']}`",
            f"- Inheritance rule: {payload['upstream_cloud']['inheritance_rule']}",
            "",
            "## Recursive Crossings",
            "",
            *crossings,
            "## Crossing Hubs",
            "",
            *hubs,
            "## Priority Carrythrough",
            "",
            f"- Pinned blocker: `{payload['priority_carrythrough']['pinned_blocker']['id']} {payload['priority_carrythrough']['pinned_blocker']['body']}` / `{payload['priority_carrythrough']['pinned_blocker']['status']}`",
            f"- Primary recursive pressure: `{payload['priority_carrythrough']['primary_recursive_pressure']['id']} {payload['priority_carrythrough']['primary_recursive_pressure']['body']}` / `{payload['priority_carrythrough']['primary_recursive_pressure']['status']}`",
            f"- Secondary recursive pressure: `{payload['priority_carrythrough']['secondary_recursive_pressure']['id']} {payload['priority_carrythrough']['secondary_recursive_pressure']['body']}` / `{payload['priority_carrythrough']['secondary_recursive_pressure']['status']}`",
            "- Stability anchors:",
            anchors,
            "",
            "## Handoff To TQ04",
            "",
            f"- Frontier: `{payload['handoff_to_tq04']['frontier']}`",
            f"- State: `{payload['handoff_to_tq04']['state']}`",
            f"- Why: {payload['handoff_to_tq04']['why']}",
            f"- Public writeback targets: {'; '.join(f'`{target}`' for target in payload['handoff_to_tq04']['public_writeback_targets'])}",
            "",
            "## Route Targets",
            "",
            route_targets,
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    primary = payload["priority_carrythrough"]["primary_recursive_pressure"]
    secondary = payload["priority_carrythrough"]["secondary_recursive_pressure"]
    blocker = payload["priority_carrythrough"]["pinned_blocker"]
    return "\n".join(
        [
            "# QSHRINK Core Corridor Fractal",
            "",
            f"Truth class: `{payload['truth']}`",
            f"carried_witness: `{payload['carried_witness']}`",
            f"operational_current: `{payload['operational_current']}`",
            f"next_hall_seed: `{payload['next_hall_seed']}`",
            f"compiled_bundle_terminal: `{payload['compiled_bundle']['terminal']}`",
            f"Primary recursive pressure: `{primary['id']} {primary['body']}` / `{primary['status']}`",
            f"Secondary recursive pressure: `{secondary['id']} {secondary['body']}` / `{secondary['status']}`",
            f"Pinned blocker: `{blocker['id']} {blocker['body']}`",
            f"deeper_receiver: `{payload['deeper_receiver']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    primary = payload["priority_carrythrough"]["primary_recursive_pressure"]
    secondary = payload["priority_carrythrough"]["secondary_recursive_pressure"]
    blocker = payload["priority_carrythrough"]["pinned_blocker"]
    return f"""# QS64-20 Core Corridor Fractal Receipt

Date: `2026-03-13`
Truth: `{payload['truth']}`
Docs gate: `{payload['docs_gate']['detail']}`
carried_witness: `{payload['carried_witness']}`
operational_current: `{payload['operational_current']}`
next_hall_seed: `{payload['next_hall_seed']}`

## Objective

Preserve the landed Fractal corridor as upstream witness, keep the Docs blocker external, keep `P2` ahead of `P3`, keep `QS64-21` as the live Hall pass, keep `QS64-22` as next Hall seed only, and keep `TQ04` separate as the deeper receiver.

## Outcome

- inherited Cloud as upstream truth instead of rescoring the corridor from zero
- kept `{blocker['id']} {blocker['body']}` pinned as the external governance blocker
- carried `{primary['id']} {primary['body']}` as the primary recursive crossing
- carried `{secondary['id']} {secondary['body']}` as the secondary recursive crossing
- preserved `{payload['carried_witness']}` as carried witness instead of a reactivated live pass
- kept `{payload['operational_current']}` as the operational current Hall step
- kept `{payload['next_hall_seed']}` released only as the next Hall seed
- kept `{payload['deeper_receiver']}` separate as the deeper receiver

## Witness

- machine fractal witness: `{relative_string(OUTPUT_JSON_PATH)}`
- ecosystem witness: `{relative_string(OUTPUT_FRACTAL_PATH)}`
- capsule witness: `{relative_string(OUTPUT_CAPSULE_PATH)}`
- Fleet route witness: `{relative_string(ATHENA_FLEET_ROUTE_MAP_PATH)}`

## Separate Deeper Receiver

`{payload['deeper_receiver']}`
"""


def render_fleet_route_map(payload: dict) -> str:
    primary = payload["priority_carrythrough"]["primary_recursive_pressure"]
    secondary = payload["priority_carrythrough"]["secondary_recursive_pressure"]
    blocker = payload["priority_carrythrough"]["pinned_blocker"]
    compiled_members = " -> ".join(payload["compiled_bundle"]["members"])
    return f"""# FAMILY Athena FLEET Route Map

## Intake

- `Athena FLEET/MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`
- `Athena FLEET/FLEET_MYCELIUM_NETWORK/00_README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`
- `self_actualize/qshrink_next4_state.json`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/qshrink_connectivity_fractal.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Operational Track

`Q42 -> {payload['carried_witness']} (carried witness) -> {payload['operational_current']} (operational current) -> {payload['next_hall_seed']} (next Hall seed)`

## Compiled Bundle

`{compiled_members}` closes locally on `{payload['compiled_bundle']['terminal']}` without replacing the operational current pass.

## Law

- Cloud ranked the corridor pressures into `P1/P2/P3/P4/P5`
- Fractal remains the carried witness, keeps `P1` external, carries `{primary['id']}` first, preserves `{secondary['id']}` behind it, and does not overwrite the operational current Hall pass
- the blocked Docs gate must remain visible and must not collapse local closure
- `{payload['deeper_receiver']}` remains the landed deeper receiver and does not replace the Hall-side operational lane

## Current State

- carried_witness: `{payload['carried_witness']}`
- operational_current: `{payload['operational_current']}`
- next_hall_seed: `{payload['next_hall_seed']}`
- compiled_bundle_terminal: `{payload['compiled_bundle']['terminal']}`
- compiled_bundle_closed: `{payload['compiled_bundle']['closed']}`
- blocked_external_front: `{payload['blocked_external_front']}`
- docs_gate: `{payload['docs_gate']['status']}`
- primary_recursive_pressure: `{primary['id']} {primary['body']}` / `{primary['status']}`
- pinned_blocker: `{blocker['id']} {blocker['body']}` / `{blocker['status']}`
"""


def render_orgin_route_map(payload: dict) -> str:
    secondary = payload["priority_carrythrough"]["secondary_recursive_pressure"]
    return f"""# FAMILY ORGIN Route Map

## Intake

- `ORGIN/Fine Tuning Docs/`
- `self_actualize/orgin_atlas.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`
- `self_actualize/qshrink_next4_state.json`

## Main Transfer

`ORGIN -> seed packet witness -> {payload['carried_witness']} (carried witness) -> {payload['operational_current']} (operational current) -> {payload['next_hall_seed']} (next Hall seed)`

## Law

- Read `ORGIN` as origin memory and observer-seed matter.
- `{secondary['id']}` stays queue-visible and does not outrank the live `{payload['operational_current']}` pass.
- The compiled bundle still closes on `{payload['compiled_bundle']['terminal']}` without making that terminal marker the current Hall step.
- The blocked Docs gate remains external (`{payload['docs_gate']['status']}`).

## Next Route

`ORGIN -> {payload['next_hall_seed']} writeback -> {payload['deeper_receiver']}`
"""


def refresh_ecosystem_readme() -> None:
    if not OUTPUT_README_PATH.exists():
        return
    lines = OUTPUT_README_PATH.read_text(encoding="utf-8").splitlines()
    filtered_lines: list[str] = []
    seen_cloud = False
    for line in lines:
        if line.startswith("- `13_QSHRINK_CORE_CORRIDOR_CLOUD.md`"):
            if seen_cloud:
                continue
            seen_cloud = True
        if line.startswith("- `14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`"):
            continue
        filtered_lines.append(line)
    fractal_entry = "- `14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`: carried-witness Fractal law that preserves `QS64-20` upstream, keeps `QS64-21` operational, releases `QS64-22` only as next Hall seed, and keeps `TQ04` separate as the landed deeper receiver."
    insert_after = "- `13_QSHRINK_CORE_CORRIDOR_CLOUD.md`: cloud-law ranking witness that inherits local Flower closure, ranks corridor pressure honestly, and keeps Docs blocking explicit."
    if insert_after in filtered_lines:
        index = filtered_lines.index(insert_after) + 1
        filtered_lines.insert(index, fractal_entry)
    else:
        filtered_lines.append(fractal_entry)
    OUTPUT_README_PATH.write_text("\n".join(filtered_lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_FRACTAL_PATH.write_text(render_fractal(payload), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    ATHENA_FLEET_ROUTE_MAP_PATH.write_text(render_fleet_route_map(payload), encoding="utf-8")
    ORGIN_ROUTE_MAP_PATH.write_text(render_orgin_route_map(payload), encoding="utf-8")
    refresh_ecosystem_readme()
    print(f"Wrote qshrink connectivity fractal json: {OUTPUT_JSON_PATH}")
    print(f"Wrote qshrink corridor fractal: {OUTPUT_FRACTAL_PATH}")
    print(f"Wrote qshrink fractal capsule: {OUTPUT_CAPSULE_PATH}")
    print(f"Wrote fractal receipt: {OUTPUT_RECEIPT_PATH}")
    print(f"Wrote Athena FLEET route map: {ATHENA_FLEET_ROUTE_MAP_PATH}")
    print(f"Wrote ORGIN route map: {ORGIN_ROUTE_MAP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
