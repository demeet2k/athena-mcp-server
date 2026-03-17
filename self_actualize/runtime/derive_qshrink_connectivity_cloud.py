from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
CAPSULE_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "50_CORPUS_CAPSULES" / "qshrink"
ATHENA_FLEET_ROOT = WORKSPACE_ROOT / "Athena FLEET"
QSHRINK_ECOSYSTEM_ROOT = ATHENA_FLEET_ROOT / "QSHRINK2_CORPUS_ECOSYSTEM"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

QSHRINK_FLOWER_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
Q42_RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
Q42_RUNTIME_CARRIER_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_carrier_contract.json"
Q42_SEED_PACKET_WITNESS_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
OUTPUT_CLOUD_PATH = QSHRINK_ECOSYSTEM_ROOT / "13_QSHRINK_CORE_CORRIDOR_CLOUD.md"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "06_qshrink_core_corridor_cloud.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_qs64_19_core_corridor_cloud.md"
OUTPUT_README_PATH = QSHRINK_ECOSYSTEM_ROOT / "README.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_cloud"
ACTIVE_SUBFRONT = "QS64-19 Connectivity-Diagnose-Cloud"
RESTART_SEED = "QS64-20 Connectivity-Diagnose-Fractal"


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


def docs_gate_detail(flower: dict) -> dict:
    docs_gate = dict(flower.get("docs_gate", {}))
    docs_gate.setdefault("status", "BLOCKED")
    docs_gate.setdefault("detail", "blocked-by-missing-credentials")
    docs_gate.setdefault("truth", "FAIL")
    docs_gate.setdefault("confirmed_by", str(LIVE_DOCS_GATE_PATH))
    if LIVE_DOCS_GATE_PATH.exists() and "surface_excerpt" not in docs_gate:
        docs_gate["surface_excerpt"] = "\n".join(read_text(LIVE_DOCS_GATE_PATH).splitlines()[:12])
    return docs_gate


def build_ranked_pressures(runtime_carrier_status: str) -> list[dict]:
    runtime_promoted = runtime_carrier_status == "OK"
    return [
        {
            "id": "P1",
            "title": "governance blocker",
            "body": "Trading Bot",
            "supporting_line": "M2 governance-rail",
            "truth": "FAIL",
            "witness_burden": "HEAVY",
            "uncertainty": "LOW",
            "leverage": "HIGH",
            "selection_state": "PINNED_BLOCKER",
            "meaning": "The Docs gate is still blocked and must remain explicit while Cloud work advances locally.",
            "resolution_target": "Restore Google Docs lawfully or keep the blocker unchanged.",
        },
        {
            "id": "P2",
            "title": "runtime carrier hardening",
            "body": "Athena OS runtime",
            "supporting_line": "M3 runtime-rail",
            "truth": "OK" if runtime_promoted else "NEAR",
            "witness_burden": "MEDIUM",
            "uncertainty": "LOW" if runtime_promoted else "MEDIUM",
            "leverage": "HIGH",
            "selection_state": "PROMOTED_CURRENT" if runtime_promoted else "PROMOTE_NEXT",
            "meaning": (
                "The runtime rail is now promoted from a witnessed membrane into the active Cloud carrier contract."
                if runtime_promoted
                else "The Flower membrane is landed, but runtime carrier hardening still needs stronger replay-safe contract and verifier depth."
            ),
            "resolution_target": (
                "Retain as the current promoted Cloud carrier and keep it replay-safe."
                if runtime_promoted
                else "Extend the new corridor membrane into a stronger runtime carrier contract."
            ),
        },
        {
            "id": "P3",
            "title": "seed mirror deepening",
            "body": "ORGIN",
            "supporting_line": "M5 seed-rail",
            "truth": "NEAR",
            "witness_burden": "MEDIUM",
            "uncertainty": "MEDIUM",
            "leverage": "MEDIUM",
            "selection_state": "QUEUE_VISIBLE",
            "meaning": "The seed packet witness is landed, but ORGIN still needs a deeper searchable mirror mesh beyond the first packet.",
            "resolution_target": "Turn the packet-backed mirror witness into a denser mirror/packet lattice.",
        },
        {
            "id": "P4",
            "title": "contraction anchor",
            "body": "QSHRINK",
            "supporting_line": "M1 contraction-rail",
            "truth": "OK",
            "witness_burden": "LIGHT",
            "uncertainty": "LOW",
            "leverage": "LOW",
            "selection_state": "STABILITY_ANCHOR",
            "meaning": "The contraction rail keeps the corridor grounded while Cloud work ranks the remaining live deficits.",
            "resolution_target": "Retain as a stability anchor.",
        },
        {
            "id": "P5",
            "title": "hall anchor",
            "body": "Athena FLEET / Hall",
            "supporting_line": "M4 hall-rail",
            "truth": "OK",
            "witness_burden": "LIGHT",
            "uncertainty": "LOW",
            "leverage": "LOW",
            "selection_state": "STABILITY_ANCHOR",
            "meaning": "The Hall loop remains the replay anchor that makes Cloud results ownerable.",
            "resolution_target": "Retain as a stability anchor.",
        },
    ]


def build_payload() -> dict:
    flower = load_optional_json(QSHRINK_FLOWER_PATH, {"truth": "NEAR", "corridor_bodies": {}})
    network = load_optional_json(QSHRINK_NETWORK_INTEGRATION_PATH, {"truth": "NEAR"})
    agent_matrix = load_optional_json(QSHRINK_AGENT_MATRIX_PATH, {"truth": "NEAR"})
    runtime_membrane = load_optional_json(Q42_RUNTIME_MEMBRANE_PATH, {"truth_state": "NEAR"})
    runtime_carrier = load_optional_json(Q42_RUNTIME_CARRIER_PATH, {"truth_state": "NEAR"})
    seed_packet = load_optional_json(Q42_SEED_PACKET_WITNESS_PATH, {"truth_state": "NEAR"})

    docs_gate = docs_gate_detail(flower)
    runtime_carrier_status = runtime_carrier.get("truth_state", "NEAR")
    cloud_sync_status = "OK" if flower.get("flower_activation_status") == "OK" and runtime_carrier_status == "OK" else "NEAR"
    ranked_pressures = build_ranked_pressures(runtime_carrier_status)
    promoted_pressure = next((pressure for pressure in ranked_pressures if pressure["id"] == "P2"), {})
    queue_visible_pressures = [pressure for pressure in ranked_pressures if pressure["selection_state"] == "QUEUE_VISIBLE"]

    truth_cloud = {
        "stable_anchors": [
            {"id": "P4", "body": "QSHRINK", "supporting_line": "M1 contraction-rail"},
            {"id": "P5", "body": "Athena FLEET / Hall", "supporting_line": "M4 hall-rail"},
        ],
        "open_pressures": [
            {"id": "P3", "body": "ORGIN", "supporting_line": "M5 seed-rail"},
        ],
        "hard_blockers": [
            {"id": "P1", "body": "Trading Bot", "supporting_line": "M2 governance-rail"},
        ],
        "promotion_ready": [] if runtime_carrier_status == "OK" else [{"id": "P2", "body": "Athena OS runtime", "supporting_line": "M3 runtime-rail"}],
        "promoted_pressures": [] if runtime_carrier_status != "OK" else [{"id": "P2", "body": "Athena OS runtime", "supporting_line": "M3 runtime-rail"}],
    }
    uncertainty_register = [
        {
            "body": "Trading Bot",
            "uncertainty": "LOW",
            "why": "The blocker is explicit and confirmed by the live Docs gate witness.",
            "pinned_by": [
                "self_actualize/live_docs_gate_status.md",
                "self_actualize/trading_bot_truth_corridor.json",
            ],
            "next_evidence": "Provide valid Google Docs credentials or preserve the blocker unchanged.",
        },
        {
            "body": "Athena OS runtime",
            "uncertainty": "LOW" if runtime_carrier_status == "OK" else "MEDIUM",
            "why": (
                "The runtime carrier contract now binds the membrane, verifier, and replay return into one Cloud-selected witness."
                if runtime_carrier_status == "OK"
                else "The local membrane exists, but Cloud work still needs stronger runtime carrier hardening."
            ),
            "pinned_by": [
                "self_actualize/q42_runtime_corridor_membrane.json",
                "self_actualize/q42_runtime_carrier_contract.json",
                "self_actualize/qshrink_runtime_verification.json",
            ],
            "next_evidence": "Keep the runtime carrier contract replay-safe while the corridor moves into Fractal.",
        },
        {
            "body": "ORGIN",
            "uncertainty": "MEDIUM",
            "why": "The first packet witness exists, but the mirror mesh remains thin.",
            "pinned_by": [
                "self_actualize/q42_orgin_seed_packet_witness.json",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md",
            ],
            "next_evidence": "Add denser mirrored packet coverage after the runtime carrier promotion is stable.",
        },
    ]
    selection_discipline = {
        "rules": [
            "FAIL plus LOW uncertainty always outranks every NEAR item.",
            "Cloud promotes the highest-leverage local NEAR item before queue-visible follow-ons.",
            "OK items remain stability anchors and never outrank live blockers.",
            "Flower closure must remain upstream truth for every Cloud claim.",
            "Cloud may rank the next frontier, but it may not pre-claim Docs access.",
        ],
        "restart_rule": RESTART_SEED,
        "current_priority_logic": "Keep the Docs blocker pinned, retain P2 as the promoted Cloud carrier, and hold P3 queue-visible behind it.",
    }
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if cloud_sync_status == "OK" else "NEAR",
        "focus": "core-corridor-cloud",
        "active_subfront": ACTIVE_SUBFRONT,
        "docs_gate": docs_gate,
        "inherited_flower_status": flower.get("flower_activation_status", flower.get("truth", "NEAR")),
        "inherited_flower_next_seed": flower.get("next_seed", ACTIVE_SUBFRONT),
        "cloud_sync_status": cloud_sync_status,
        "promoted_pressure": {
            "id": promoted_pressure.get("id", "P2"),
            "body": promoted_pressure.get("body", "Athena OS runtime"),
            "selection_state": promoted_pressure.get("selection_state", "PROMOTED_CURRENT"),
        },
        "runtime_carrier_status": runtime_carrier_status,
        "queue_visible_pressures": [
            {"id": pressure["id"], "body": pressure["body"], "selection_state": pressure["selection_state"]}
            for pressure in queue_visible_pressures
        ],
        "corridor_bodies": flower.get("corridor_bodies", {}),
        "truth_cloud": truth_cloud,
        "ranked_pressures": ranked_pressures,
        "uncertainty_register": uncertainty_register,
        "selection_discipline": selection_discipline,
        "route_targets": flower.get("route_targets", []),
        "next_seed": RESTART_SEED,
        "next_restart_seed": RESTART_SEED,
        "source_paths": {
            "qshrink_connectivity_flower": str(QSHRINK_FLOWER_PATH),
            "qshrink_network_integration": str(QSHRINK_NETWORK_INTEGRATION_PATH),
            "qshrink_agent_task_matrix": str(QSHRINK_AGENT_MATRIX_PATH),
            "runtime_membrane": str(Q42_RUNTIME_MEMBRANE_PATH),
            "runtime_carrier": str(Q42_RUNTIME_CARRIER_PATH),
            "seed_packet_witness": str(Q42_SEED_PACKET_WITNESS_PATH),
        },
        "witness_basis": {
            "flower_truth": flower.get("truth", "NEAR"),
            "network_truth": network.get("truth", "NEAR"),
            "agent_matrix_truth": agent_matrix.get("truth", "NEAR"),
            "runtime_membrane_truth": runtime_membrane.get("truth_state", "NEAR"),
            "runtime_carrier_truth": runtime_carrier_status,
            "seed_packet_truth": seed_packet.get("truth_state", "NEAR"),
        },
    }


def render_cloud(payload: dict) -> str:
    rows = []
    for pressure in payload["ranked_pressures"]:
        rows.extend(
            [
                f"### {pressure['id']} `{pressure['title']}`",
                "",
                f"- Body: `{pressure['body']}`",
                f"- Supporting line: `{pressure['supporting_line']}`",
                f"- Truth: `{pressure['truth']}`",
                f"- Selection state: `{pressure['selection_state']}`",
                f"- Meaning: {pressure['meaning']}",
                f"- Resolution target: {pressure['resolution_target']}",
                "",
            ]
        )
    queue_lines = "\n".join(
        f"- `{pressure['id']}`: `{pressure['body']}` / `{pressure['selection_state']}`"
        for pressure in payload["queue_visible_pressures"]
    ) or "- none"
    return "\n".join(
        [
            "# QSHRINK Core Corridor Cloud",
            "",
            f"- Generated at: `{payload['generated_at']}`",
            f"- Truth: `{payload['truth']}`",
            f"- Active subfront: `{payload['active_subfront']}`",
            f"- Inherited Flower status: `{payload['inherited_flower_status']}`",
            f"- Cloud sync status: `{payload['cloud_sync_status']}`",
            f"- Runtime carrier status: `{payload['runtime_carrier_status']}`",
            f"- Promoted pressure: `{payload['promoted_pressure']['id']}` / `{payload['promoted_pressure']['selection_state']}`",
            f"- Docs gate: `{payload['docs_gate']['detail']}`",
            "",
            "## Omega",
            "",
            "Cloud is now the canonical ranking layer for the core corridor and keeps P2 promoted while P3 stays queue-visible.",
            "",
            "## Queue-visible follow-on",
            "",
            queue_lines,
            "",
            "## Ranked Pressures",
            "",
            *rows,
            "## Restart Seed",
            "",
            f"`{payload['next_restart_seed']}`",
            "",
        ]
    )


def render_capsule(payload: dict) -> str:
    top_blocker = payload["ranked_pressures"][0]
    next_target = payload["promoted_pressure"]
    queued = ", ".join(pressure["id"] for pressure in payload["queue_visible_pressures"]) or "none"
    return "\n".join(
        [
            "# QSHRINK Core Corridor Cloud",
            "",
            f"Truth class: `{payload['truth']}`",
            f"Active subfront: `{payload['active_subfront']}`",
            f"Inherited Flower status: `{payload['inherited_flower_status']}`",
            f"Cloud sync status: `{payload['cloud_sync_status']}`",
            f"Top blocker: `{top_blocker['body']}` / `{top_blocker['selection_state']}`",
            f"Promoted pressure: `{next_target['body']}` / `{next_target['selection_state']}`",
            f"Queue-visible follow-on: `{queued}`",
            "",
            "## Next Seed",
            "",
            f"`{payload['next_restart_seed']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    pressure_lines = "\n".join(
        f"- `{pressure['id']} {pressure['title']}`: `{pressure['body']}` / `{pressure['selection_state']}`"
        for pressure in payload["ranked_pressures"]
    )
    queue_lines = "\n".join(
        f"- `{pressure['id']}`: `{pressure['body']}`"
        for pressure in payload["queue_visible_pressures"]
    ) or "- none"
    return f"""# QS64-19 Core Corridor Cloud Receipt

Date: `2026-03-13`
Truth: `{payload['truth']}`
Docs gate: `{payload['docs_gate']['detail']}`
Inherited Flower status: `{payload['inherited_flower_status']}`
Cloud sync status: `{payload['cloud_sync_status']}`
Runtime carrier status: `{payload['runtime_carrier_status']}`

## Objective

Hold Cloud as the canonical core-corridor ranking layer, promote `P2` into the active runtime carrier contract, and keep `P3` visible without bundling it into the same pass.

## Ranked Pressures

{pressure_lines}

## Queue-visible follow-on

{queue_lines}

## Restart Seed

`{payload['next_restart_seed']}`
"""


def refresh_ecosystem_readme() -> None:
    if not OUTPUT_README_PATH.exists():
        return
    readme_text = OUTPUT_README_PATH.read_text(encoding="utf-8")
    entry = "- `13_QSHRINK_CORE_CORRIDOR_CLOUD.md`: cloud-law ranking witness that inherits local Flower closure, promotes the runtime carrier, and keeps Docs blocking explicit."
    if entry in readme_text:
        return
    marker = "- `12_QSHRINK_CORE_CORRIDOR_METRO.md`: flower-law cadence and handoff metro across QSHRINK, Athena FLEET, Trading Bot, Athena OS runtime, Hall, and the secondary ORGIN seed leg."
    if marker in readme_text:
        readme_text = readme_text.replace(marker, marker + "\n" + entry)
    else:
        readme_text = readme_text.rstrip() + "\n" + entry + "\n"
    OUTPUT_README_PATH.write_text(readme_text, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_CLOUD_PATH.write_text(render_cloud(payload), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    refresh_ecosystem_readme()
    print(f"Wrote qshrink connectivity cloud json: {OUTPUT_JSON_PATH}")
    print(f"Wrote qshrink corridor cloud: {OUTPUT_CLOUD_PATH}")
    print(f"Wrote qshrink cloud capsule: {OUTPUT_CAPSULE_PATH}")
    print(f"Wrote cloud receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
