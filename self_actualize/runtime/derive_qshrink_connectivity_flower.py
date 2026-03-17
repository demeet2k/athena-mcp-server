from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
CAPSULE_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "50_CORPUS_CAPSULES" / "qshrink"
ATHENA_FLEET_ROOT = WORKSPACE_ROOT / "Athena FLEET"
QSHRINK_ECOSYSTEM_ROOT = ATHENA_FLEET_ROOT / "QSHRINK2_CORPUS_ECOSYSTEM"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
PACKETS_ROOT = MYCELIUM_ROOT / "nervous_system" / "packets"

QSHRINK_SQUARE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
QSHRINK_CAPABILITY_STACK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
TRADING_BOT_CORRIDOR_PATH = SELF_ACTUALIZE_ROOT / "trading_bot_truth_corridor.json"
ORGIN_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "orgin_atlas.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
Q42_RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
Q42_SEED_PACKET_WITNESS_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"

QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
TRADING_BOT_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_trading_bot_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
ORGIN_PACKET_PATH = PACKETS_ROOT / "PKT_2026-03-13_q42_orgin_seed_packet_witness.md"
RUNTIME_MEMBRANE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
OUTPUT_METRO_PATH = QSHRINK_ECOSYSTEM_ROOT / "12_QSHRINK_CORE_CORRIDOR_METRO.md"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "05_qshrink_core_corridor_metro.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_qs64_18_core_corridor_metro.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_flower"
ACTIVE_SUBFRONT = "QS64-18 Connectivity-Diagnose-Flower"
RESTART_SEED = "QS64-19 Connectivity-Diagnose-Cloud"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return load_json(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{value} B"


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def docs_gate_payload(square: dict) -> dict:
    docs_gate = dict(square.get("docs_gate", {}))
    docs_gate.setdefault("status", "BLOCKED")
    docs_gate.setdefault("state", docs_gate["status"])
    docs_gate.setdefault("detail", "blocked-by-missing-credentials")
    docs_gate.setdefault("truth", "FAIL")
    docs_gate.setdefault("confirmed_by", str(LIVE_DOCS_GATE_PATH))
    if LIVE_DOCS_GATE_PATH.exists() and "surface_excerpt" not in docs_gate:
        docs_gate["surface_excerpt"] = "\n".join(read_text(LIVE_DOCS_GATE_PATH).splitlines()[:12])
    return docs_gate


def line_ok(line: dict) -> bool:
    return line.get("truth") == "OK"


def build_payload() -> dict:
    square = load_json(QSHRINK_SQUARE_PATH)
    network = load_optional_json(QSHRINK_NETWORK_INTEGRATION_PATH, {"truth": "NEAR"})
    agent_matrix = load_optional_json(QSHRINK_AGENT_MATRIX_PATH, {"truth": "NEAR"})
    runtime = load_optional_json(QSHRINK_RUNTIME_VERIFICATION_PATH, {"truth": "NEAR"})
    capability = load_optional_json(QSHRINK_CAPABILITY_STACK_PATH, {"truth": "NEAR"})
    trading_corridor = load_optional_json(TRADING_BOT_CORRIDOR_PATH, {"truth": "NEAR"})
    orgin_atlas = load_optional_json(ORGIN_ATLAS_PATH, {"record_count": 0})
    runtime_membrane = load_optional_json(Q42_RUNTIME_MEMBRANE_PATH, {"truth_state": "NEAR"})
    seed_packet = load_optional_json(Q42_SEED_PACKET_WITNESS_PATH, {"truth_state": "NEAR"})

    athena_fleet_route_map_text = read_text(ATHENA_FLEET_ROUTE_MAP_PATH)
    trading_bot_route_map_text = read_text(TRADING_BOT_ROUTE_MAP_PATH)
    orgin_route_map_text = read_text(ORGIN_ROUTE_MAP_PATH)

    docs_gate = docs_gate_payload(square)
    runtime_membrane_truth = runtime_membrane.get("truth_state", "NEAR")
    seed_packet_truth = seed_packet.get("truth_state", "NEAR")

    metro_lines = [
        {
            "id": "M1",
            "name": "contraction-rail",
            "truth": "OK",
            "status": "witnessed",
            "scope": "flower-core",
            "closure_role": "required-for-flower-ok",
            "blocker_scope": "local",
            "cadence_class": "per-corridor-pass",
            "route": "QSHRINK internal root -> Athena FLEET ecosystem -> qshrink family route map",
            "meaning": "Carries contraction law from the internal QSHRINK doctrine root into the Fleet-facing ecosystem and back into the routed family membrane.",
            "surfaces": [
                "QSHRINK - ATHENA (internal use)/README.md",
                "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/01_FULL_FRAMEWORK_SYNTHESIS.md",
                relative_string(QSHRINK_ROUTE_MAP_PATH),
            ],
        },
        {
            "id": "M2",
            "name": "governance-rail",
            "truth": "NEAR",
            "status": docs_gate["detail"],
            "scope": "external-gate-overlay",
            "closure_role": "truthful-blocker-only",
            "blocker_scope": "external",
            "cadence_class": "gate-bound",
            "route": "Athena FLEET ecosystem -> Trading Bot truth corridor -> live_docs_gate_status -> Hall truth writeback",
            "meaning": "Keeps the blocked Docs gate explicit as an external governance blocker without letting it falsify local Flower closure.",
            "surfaces": [
                relative_string(OUTPUT_METRO_PATH),
                relative_string(TRADING_BOT_CORRIDOR_PATH),
                relative_string(LIVE_DOCS_GATE_PATH),
                relative_string(TRADING_BOT_ROUTE_MAP_PATH),
            ],
        },
        {
            "id": "M3",
            "name": "runtime-rail",
            "truth": "OK" if runtime_membrane_truth == "OK" else "NEAR",
            "status": runtime_membrane_truth.lower(),
            "scope": "flower-core",
            "closure_role": "required-for-flower-ok",
            "blocker_scope": "local",
            "cadence_class": "verification-bound",
            "route": "Athena FLEET ecosystem -> Athena OS qshrink runtime corridor membrane -> runtime verification -> QSHRINK active front",
            "meaning": "Binds Athena OS into the corridor through an explicit runtime membrane instead of leaving the rail as a free-floating verifier.",
            "surfaces": [
                relative_string(RUNTIME_MEMBRANE_MD_PATH),
                relative_string(Q42_RUNTIME_MEMBRANE_PATH),
                relative_string(QSHRINK_RUNTIME_VERIFICATION_PATH),
                relative_string(QSHRINK_ACTIVE_FRONT_PATH),
            ],
        },
        {
            "id": "M4",
            "name": "hall-rail",
            "truth": "OK",
            "status": "witnessed",
            "scope": "flower-core",
            "closure_role": "required-for-flower-ok",
            "blocker_scope": "local",
            "cadence_class": "every-landed-pass",
            "route": "Athena FLEET ecosystem -> Quest Board -> active queue -> receipt -> restart seed",
            "meaning": "Closes the replay loop that makes corridor work ownerable, visible, and restart-safe.",
            "surfaces": [
                "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
                relative_string(OUTPUT_RECEIPT_PATH),
                "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
            ],
        },
        {
            "id": "M5",
            "name": "seed-rail",
            "truth": "OK" if seed_packet_truth == "OK" else "NEAR",
            "status": seed_packet_truth.lower(),
            "scope": "flower-core",
            "closure_role": "required-for-flower-ok",
            "blocker_scope": "local",
            "cadence_class": "packet-bound",
            "route": "Athena FLEET ecosystem -> ORGIN mirror bundle -> seed packet witness -> ORGIN route map",
            "meaning": "Turns ORGIN from a visible backlog leg into a replayable packet witness that can participate in local Flower closure.",
            "surfaces": [
                relative_string(Q42_SEED_PACKET_WITNESS_PATH),
                relative_string(ORGIN_PACKET_PATH),
                relative_string(ORGIN_ROUTE_MAP_PATH),
                relative_string(ORGIN_ATLAS_PATH),
            ],
        },
    ]

    flower_core_status = "OK" if all(line_ok(line) for line in metro_lines if line["scope"] == "flower-core") else "NEAR"
    external_gate_overlay_status = docs_gate["detail"] if docs_gate["detail"] != "open" else "OK"
    flower_activation_status = "OK" if flower_core_status == "OK" else "NEAR"

    flow_deficits = []
    if external_gate_overlay_status != "OK":
        flow_deficits.append(
            {
                "body": "Trading Bot",
                "truth": docs_gate.get("truth", "FAIL"),
                "status": "external-blocker",
                "deficit": "Google Docs ingress is still blocked and remains an explicit external governance overlay.",
                "resolution_target": "Reopen Google Docs lawfully or preserve the blocker unchanged.",
            }
        )
    if runtime_membrane_truth != "OK":
        flow_deficits.append(
            {
                "body": "Athena OS runtime",
                "truth": "NEAR",
                "status": "missing-local-witness",
                "deficit": "The runtime rail still lacks its corridor membrane witness.",
                "resolution_target": "Land the Athena OS corridor membrane.",
            }
        )
    if seed_packet_truth != "OK":
        flow_deficits.append(
            {
                "body": "ORGIN",
                "truth": "NEAR",
                "status": "missing-local-witness",
                "deficit": "The seed rail still lacks its packet-backed mirror witness.",
                "resolution_target": "Land the ORGIN seed packet witness.",
            }
        )

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": flower_activation_status,
        "focus": "core-corridor-flower-activation",
        "active_subfront": ACTIVE_SUBFRONT,
        "upstream_square_contract": relative_string(QSHRINK_SQUARE_PATH),
        "docs_gate": docs_gate,
        "flower_core_status": flower_core_status,
        "external_gate_overlay_status": external_gate_overlay_status,
        "flower_activation_status": flower_activation_status,
        "corridor_bodies": {
            "primary_bodies": square.get("primary_bodies", []),
            "secondary_bodies": square.get("secondary_bodies", []),
        },
        "metro_lines": metro_lines,
        "transfer_hubs": [
            {
                "id": "H1",
                "name": "Athena FLEET ecosystem",
                "truth": "OK",
                "role": "body-level transfer hub",
                "meaning": "Athena FLEET remains the body-level transfer hub where the Flower core actually closes.",
                "connected_lines": ["M1", "M2", "M3", "M4", "M5"],
                "surfaces": [
                    "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/",
                    "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md",
                    relative_string(OUTPUT_METRO_PATH),
                ],
            },
            {
                "id": "H2",
                "name": "FAMILY_athena_fleet_route_map.md",
                "truth": "OK",
                "role": "witness-level routing hub",
                "meaning": "The Fleet route map is the witness membrane where Flower-core closure and the external gate overlay are named together.",
                "connected_lines": ["M1", "M2", "M3", "M4", "M5"],
                "surfaces": [
                    relative_string(ATHENA_FLEET_ROUTE_MAP_PATH),
                    relative_string(OUTPUT_JSON_PATH),
                ],
            },
            {
                "id": "H3",
                "name": "Quest Board / active queue",
                "truth": "OK",
                "role": "replay-and-restart hub",
                "meaning": "The Hall loop closes the Flower pass and emits Cloud as the next lawful restart.",
                "connected_lines": ["M2", "M4"],
                "surfaces": [
                    "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                    "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
                    relative_string(OUTPUT_RECEIPT_PATH),
                ],
            },
        ],
        "zero_point_hub": {
            "body": "Athena FLEET",
            "witness": relative_string(ATHENA_FLEET_ROUTE_MAP_PATH),
            "meaning": "Athena FLEET is the Flower pass zero-point hub.",
        },
        "global_topology": "cylinder",
        "topology_rationale": "The Hall loop closes locally through M1, M3, M4, and M5 while M2 stays an explicitly external governance overlay.",
        "flow_deficits": flow_deficits,
        "route_targets": [
            {"body": "QSHRINK", "target": relative_string(QSHRINK_ROUTE_MAP_PATH)},
            {"body": "Athena FLEET", "target": relative_string(ATHENA_FLEET_ROUTE_MAP_PATH)},
            {"body": "Trading Bot", "target": relative_string(TRADING_BOT_ROUTE_MAP_PATH)},
            {"body": "Athena OS runtime", "target": relative_string(RUNTIME_MEMBRANE_MD_PATH)},
            {"body": "ORGIN", "target": relative_string(ORGIN_ROUTE_MAP_PATH)},
            {"body": "Queue", "target": "self_actualize/mycelium_brain/nervous_system/06_active_queue.md"},
        ],
        "next_seed": RESTART_SEED,
        "source_paths": {
            "qshrink_connectivity_square": str(QSHRINK_SQUARE_PATH),
            "qshrink_network_integration": str(QSHRINK_NETWORK_INTEGRATION_PATH),
            "qshrink_agent_task_matrix": str(QSHRINK_AGENT_MATRIX_PATH),
            "qshrink_runtime_verification": str(QSHRINK_RUNTIME_VERIFICATION_PATH),
            "qshrink_capability_stack": str(QSHRINK_CAPABILITY_STACK_PATH),
            "trading_bot_truth_corridor": str(TRADING_BOT_CORRIDOR_PATH),
            "orgin_atlas": str(ORGIN_ATLAS_PATH),
            "runtime_membrane": str(Q42_RUNTIME_MEMBRANE_PATH),
            "seed_packet_witness": str(Q42_SEED_PACKET_WITNESS_PATH),
        },
        "witness_basis": {
            "square_truth": square.get("truth", "NEAR"),
            "network_truth": network.get("truth", "NEAR"),
            "agent_matrix_truth": agent_matrix.get("truth", "NEAR"),
            "runtime_truth": runtime.get("truth", "NEAR"),
            "capability_truth": capability.get("truth", "NEAR"),
            "trading_bot_truth": trading_corridor.get("truth", "NEAR"),
            "orgin_records": orgin_atlas.get("record_count", 0),
            "route_map_bytes": {
                "athena_fleet": len(athena_fleet_route_map_text.encode("utf-8")),
                "trading_bot": len(trading_bot_route_map_text.encode("utf-8")),
                "orgin": len(orgin_route_map_text.encode("utf-8")),
            },
        },
    }


def render_metro(payload: dict) -> str:
    lines = [
        "# QSHRINK Core Corridor Metro",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Truth: `{payload['truth']}`",
        f"- Active subfront: `{payload['active_subfront']}`",
        f"- Flower core status: `{payload['flower_core_status']}`",
        f"- External gate overlay: `{payload['external_gate_overlay_status']}`",
        f"- Flower activation: `{payload['flower_activation_status']}`",
        "",
        "## Omega",
        "",
        "The Flower pass is closed locally when M1, M3, M4, and M5 are all witnessed. M2 remains visible as an external blocker and does not silently govern local closure.",
        "",
        "## Metro Lines",
        "",
    ]
    for line in payload["metro_lines"]:
        lines.extend(
            [
                f"### {line['id']} `{line['name']}`",
                "",
                f"- Truth: `{line['truth']}`",
                f"- Status: `{line['status']}`",
                f"- Scope: `{line['scope']}`",
                f"- Closure role: `{line['closure_role']}`",
                f"- Blocker scope: `{line['blocker_scope']}`",
                f"- Route: `{line['route']}`",
                f"- Meaning: {line['meaning']}",
                f"- Surfaces: {'; '.join(f'`{surface}`' for surface in line['surfaces'])}",
                "",
            ]
        )

    lines.extend(["## Transfer Hubs", ""])
    for hub in payload["transfer_hubs"]:
        lines.extend(
            [
                f"### {hub['id']} `{hub['name']}`",
                "",
                f"- Truth: `{hub['truth']}`",
                f"- Role: `{hub['role']}`",
                f"- Meaning: {hub['meaning']}",
                f"- Connected lines: {', '.join(f'`{line}`' for line in hub['connected_lines'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Flow Deficits",
            "",
        ]
    )
    if payload["flow_deficits"]:
        for deficit in payload["flow_deficits"]:
            lines.extend(
                [
                    f"### `{deficit['body']}`",
                    "",
                    f"- Truth: `{deficit['truth']}`",
                    f"- Status: `{deficit['status']}`",
                    f"- Deficit: {deficit['deficit']}",
                    f"- Resolution target: {deficit['resolution_target']}",
                    "",
                ]
            )
    else:
        lines.extend(["- none", ""])

    lines.extend(["## Restart Seed", "", f"`{payload['next_seed']}`"])
    return "\n".join(lines) + "\n"


def render_capsule(payload: dict) -> str:
    return "\n".join(
        [
            "# QSHRINK Core Corridor Metro",
            "",
            f"Truth class: `{payload['truth']}`",
            f"Active subfront: `{payload['active_subfront']}`",
            f"Flower core status: `{payload['flower_core_status']}`",
            f"External gate overlay: `{payload['external_gate_overlay_status']}`",
            f"Restart seed: `{payload['next_seed']}`",
            "",
        ]
    )


def render_fleet_route_map(payload: dict) -> str:
    line_status = "\n".join(
        f"- `{line['id']} {line['name']}`: `{line['truth']}` / `{line['scope']}` / `{line['status']}`"
        for line in payload["metro_lines"]
    )
    return f"""# FAMILY Athena FLEET Route Map

## Intake

- `Athena FLEET/MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`
- `Athena FLEET/FLEET_MYCELIUM_NETWORK/00_README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `self_actualize/qshrink_connectivity_square.json`
- `self_actualize/qshrink_connectivity_flower.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Main transfer

`QSHRINK -> Athena FLEET ecosystem -> Athena OS corridor membrane -> ORGIN seed packet witness -> Hall writeback`

Governance overlay:

`Athena FLEET -> Trading Bot truth corridor -> blocked Docs gate`

## Law

- `M1`, `M3`, `M4`, and `M5` close the Flower core locally
- `M2` remains an external governance overlay while Docs is blocked
- the blocked Docs gate must remain visible and must not collapse local corridor closure

## Flower status

- Flower core: `{payload['flower_core_status']}`
- External gate overlay: `{payload['external_gate_overlay_status']}`
- Flower activation: `{payload['flower_activation_status']}`

## Fixed metro lines

{line_status}

## Next route

`{payload['next_seed']}`
"""


def render_receipt(payload: dict) -> str:
    lines = [
        "# QS64-18 Core Corridor Metro Receipt",
        "",
        "Date: `2026-03-13`",
        f"Truth: `{payload['truth']}`",
        f"Flower core status: `{payload['flower_core_status']}`",
        f"External gate overlay: `{payload['external_gate_overlay_status']}`",
        "Hall frontier: `Q42`",
        f"Active subfront: `{payload['active_subfront']}`",
        "",
        "## Objective",
        "",
        "Close the Flower pass honestly by witnessing the Athena OS runtime membrane and the ORGIN seed packet while keeping the blocked Docs gate explicit and external.",
        "",
        "## Witness",
        "",
        f"- machine metro witness: `{relative_string(OUTPUT_JSON_PATH)}`",
        f"- markdown metro witness: `{relative_string(OUTPUT_METRO_PATH)}`",
        f"- capsule witness: `{relative_string(OUTPUT_CAPSULE_PATH)}`",
        f"- runtime membrane: `{relative_string(Q42_RUNTIME_MEMBRANE_PATH)}`",
        f"- seed packet witness: `{relative_string(Q42_SEED_PACKET_WITNESS_PATH)}`",
        "",
        "## Guardrails Preserved",
        "",
        "- Google Docs remained honestly blocked because `Trading Bot/credentials.json` and `Trading Bot/token.json` are still absent",
        "- Flower closure was computed from local corridor witnesses only",
        "- Cloud remains the next frontier instead of being treated as already closed",
        "",
        "## Restart Seed",
        "",
        f"`{payload['next_seed']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_METRO_PATH.write_text(render_metro(payload), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    ATHENA_FLEET_ROUTE_MAP_PATH.write_text(render_fleet_route_map(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote qshrink connectivity flower json: {OUTPUT_JSON_PATH}")
    print(f"Wrote qshrink corridor metro: {OUTPUT_METRO_PATH}")
    print(f"Wrote qshrink metro capsule: {OUTPUT_CAPSULE_PATH}")
    print(f"Wrote Athena FLEET route map: {ATHENA_FLEET_ROUTE_MAP_PATH}")
    print(f"Wrote metro receipt: {OUTPUT_RECEIPT_PATH}")
    return 0 if payload["truth"] in {"OK", "NEAR"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
