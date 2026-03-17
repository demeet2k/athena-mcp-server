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

QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_CAPABILITY_STACK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
QSHRINK_RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
QSHRINK_FLOWER_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
TRADING_BOT_CORRIDOR_PATH = SELF_ACTUALIZE_ROOT / "trading_bot_truth_corridor.json"
ORGIN_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "orgin_atlas.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"
OUTPUT_CONTRACT_PATH = QSHRINK_ECOSYSTEM_ROOT / "11_QSHRINK_CORE_CORRIDOR_CONTRACT.md"
OUTPUT_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "04_qshrink_core_corridor_contract.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_square"
ACTIVE_SUBFRONT = "QS64-17 Connectivity-Diagnose-Square"
RESTART_SEED = "QS64-18 Connectivity-Diagnose-Flower"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def atlas_metrics(atlas: dict, top_level: str) -> dict:
    summary = atlas.get("summary", {})
    top_counts = summary.get("by_top_level", {})
    records = [
        record for record in atlas.get("records", [])
        if record.get("top_level") == top_level
    ]
    return {
        "top_level": top_level,
        "record_count": top_counts.get(top_level, len(records)),
        "size_bytes": sum(int(record.get("size_bytes", 0)) for record in records),
    }


def gate_status(trading_corridor: dict) -> dict:
    gate_state = trading_corridor.get("gate_state", "BLOCKED")
    gate_detail = trading_corridor.get("gate_detail", "blocked-by-missing-credentials")
    gate_truth = trading_corridor.get("gate_truth", "FAIL")
    status = {
        "status": gate_state,
        "state": gate_state,
        "detail": gate_detail,
        "truth": gate_truth,
        "confirmed_by": str(LIVE_DOCS_GATE_PATH),
    }
    if LIVE_DOCS_GATE_PATH.exists():
        status["surface_excerpt"] = "\n".join(read_text(LIVE_DOCS_GATE_PATH).splitlines()[:12])
    return status


def build_payload() -> dict:
    network = load_json(QSHRINK_NETWORK_INTEGRATION_PATH)
    capability = load_json(QSHRINK_CAPABILITY_STACK_PATH)
    runtime = load_json(QSHRINK_RUNTIME_VERIFICATION_PATH)
    corpus_atlas = load_json(CORPUS_ATLAS_PATH)
    trading_corridor = load_json(TRADING_BOT_CORRIDOR_PATH)
    orgin_atlas = load_json(ORGIN_ATLAS_PATH)

    qshrink_surface = network["surface_metrics"]["qshrink_internal"]
    fleet_surface = network["surface_metrics"]["fleet_cluster"]
    trading_surface = network["surface_metrics"]["trading_bot"]
    athena_os_surface = network["surface_metrics"]["athena_os_runtime"]

    qshrink_atlas = atlas_metrics(corpus_atlas, "QSHRINK - ATHENA (internal use)")
    fleet_atlas = atlas_metrics(corpus_atlas, "Athena FLEET")
    trading_atlas = atlas_metrics(corpus_atlas, "Trading Bot")
    orgin_metrics = {
        "top_level": "ORGIN",
        "record_count": orgin_atlas.get("record_count", 0),
        "size_bytes": sum(int(record.get("size_bytes", 0)) for record in orgin_atlas.get("records", [])),
    }

    docs_gate = gate_status(trading_corridor)

    primary_bodies = [
        {
            "body": "QSHRINK",
            "truth": "OK",
            "role": "Shiva compression organ and corridor origin",
            "atlas_records": qshrink_atlas["record_count"],
            "surface_files": qshrink_surface.get("file_count", 0),
            "size_bytes": qshrink_surface.get("size_bytes", 0),
            "route_surface": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md",
        },
        {
            "body": "Athena FLEET",
            "truth": "OK",
            "role": "fleet-side corridor membrane and ecosystem shell",
            "atlas_records": fleet_atlas["record_count"],
            "surface_files": fleet_surface.get("file_count", 0),
            "size_bytes": fleet_surface.get("size_bytes", 0),
            "route_surface": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md",
        },
        {
            "body": "Trading Bot",
            "truth": trading_corridor.get("truth", "NEAR"),
            "role": "truth corridor and blocked live-memory governance limb",
            "atlas_records": trading_atlas["record_count"],
            "surface_files": trading_surface.get("file_count", 0),
            "size_bytes": trading_surface.get("size_bytes", 0),
            "route_surface": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_trading_bot_route_map.md",
        },
        {
            "body": "Athena OS runtime",
            "truth": "OK" if runtime.get("truth") == "OK" else "NEAR",
            "role": "verified qshrink runtime-compute leg",
            "atlas_records": 0,
            "surface_files": athena_os_surface.get("file_count", 0),
            "size_bytes": athena_os_surface.get("size_bytes", 0),
            "route_surface": "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS/athena_os/qshrink/",
        },
    ]

    secondary_bodies = [
        {
            "body": "ORGIN",
            "truth": "NEAR",
            "role": "secondary seed leg and origin-memory reservoir",
            "atlas_records": orgin_metrics["record_count"],
            "size_bytes": orgin_metrics["size_bytes"],
            "route_surface": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md",
        }
    ]

    corridor_legs = [
        {
            "id": "LEG-C1",
            "name": "qshrink-to-athena-fleet",
            "truth": "OK",
            "meaning": "The QSHRINK fleet ecosystem and the new Athena FLEET route map now form one canonical square membrane.",
            "surfaces": [
                "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md",
            ],
        },
        {
            "id": "LEG-C2",
            "name": "athena-fleet-to-trading-bot",
            "truth": trading_corridor.get("truth", "NEAR"),
            "meaning": "Fleet can route into the Trading Bot truth corridor, but live Docs ingress remains blocker-bound and must stay explicit.",
            "surfaces": [
                "self_actualize/trading_bot_truth_corridor.json",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_trading_bot_route_map.md",
                "self_actualize/live_docs_gate_status.md",
            ],
        },
        {
            "id": "LEG-C3",
            "name": "athena-fleet-to-athena-os-runtime",
            "truth": "NEAR",
            "meaning": "Athena OS participates as a verified runtime leg, but it still lacks a separate family membrane inside the core corridor.",
            "surfaces": [
                "self_actualize/qshrink_runtime_verification.json",
                "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS/athena_os/qshrink/",
                "self_actualize/qshrink_network_integration.json",
            ],
        },
        {
            "id": "LEG-C4",
            "name": "athena-fleet-to-orgin-seed",
            "truth": "NEAR",
            "meaning": "ORGIN is routed as a secondary seed leg through its atlas and route map, but mirrored markdown packets are not landed yet.",
            "surfaces": [
                "self_actualize/orgin_atlas.json",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md",
                "ORGIN/Fine Tuning Docs/",
            ],
        },
    ]

    square_deficits = [
        {
            "id": "SQD-01",
            "body": "Athena FLEET",
            "truth": "OK",
            "status": "resolved-this-pass",
            "deficit": "Athena FLEET lacked a canonical route map inside the QSHRINK core corridor.",
            "resolution": "FAMILY_athena_fleet_route_map.md now binds Fleet to QSHRINK, Trading Bot, Athena OS runtime, and ORGIN.",
        },
        {
            "id": "SQD-02",
            "body": "Trading Bot",
            "truth": docs_gate["truth"],
            "status": "open-deficit",
            "deficit": "Live Docs ingress remains blocker-bound at the truth corridor.",
            "resolution_target": "Either authenticate the Docs gate or keep local-first governance routing explicit.",
        },
        {
            "id": "SQD-03",
            "body": "Athena OS runtime",
            "truth": "NEAR",
            "status": "open-deficit",
            "deficit": "Athena OS is present as a runtime leg but does not yet have a separate family membrane for this corridor.",
            "resolution_target": "Promote a corridor-facing runtime family or equivalent manifest membrane after QS64-18/QS64-42.",
        },
        {
            "id": "SQD-04",
            "body": "ORGIN",
            "truth": "NEAR",
            "status": "open-deficit",
            "deficit": "ORGIN remains accessible only through atlas and route-map witness, not through mirrored markdown packets.",
            "resolution_target": "Land a mirrored markdown bundle or seed-packet index for everyday contraction and search.",
        },
    ]

    route_targets = [
        {
            "body": "QSHRINK",
            "target": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md",
        },
        {
            "body": "Athena FLEET",
            "target": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md",
        },
        {
            "body": "Trading Bot",
            "target": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_trading_bot_route_map.md",
        },
        {
            "body": "ORGIN",
            "target": "self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md",
        },
        {
            "body": "Hall",
            "target": "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        },
    ]

    promotion_thresholds = {
        "fleet_square_ready": "The Fleet route map exists, is cited by the corridor contract, and is referenced by qshrink_network_integration.json.",
        "trading_bot_gate_honesty": "Trading Bot either authenticates the Docs gate or continues to publish explicit BLOCKED local-first truth surfaces.",
        "athena_os_runtime_membrane": "Athena OS runtime is reused by a corridor-facing family, manifest, or capsule surface beyond the verifier alone.",
        "orgin_seed_accessibility": "ORGIN gains mirrored markdown packets or a packet index that makes the seed leg searchable without reopening raw archives.",
        "next_promotion": RESTART_SEED,
    }

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "NEAR",
        "focus": "core-corridor",
        "docs_gate": docs_gate,
        "primary_bodies": primary_bodies,
        "secondary_bodies": secondary_bodies,
        "corridor_legs": corridor_legs,
        "square_deficits": square_deficits,
        "atlas_slice": {
            "qshrink": qshrink_atlas,
            "athena_fleet": fleet_atlas,
            "trading_bot": trading_atlas,
            "orgin": orgin_metrics,
            "athena_os_runtime": {
                "record_count": 0,
                "surface_files": athena_os_surface.get("file_count", 0),
                "size_bytes": athena_os_surface.get("size_bytes", 0),
            },
        },
        "route_targets": route_targets,
        "promotion_thresholds": promotion_thresholds,
        "active_subfront": ACTIVE_SUBFRONT,
        "next_seed": RESTART_SEED,
        "source_paths": {
            "qshrink_network_integration": str(QSHRINK_NETWORK_INTEGRATION_PATH),
            "qshrink_capability_stack": str(QSHRINK_CAPABILITY_STACK_PATH),
            "qshrink_runtime_verification": str(QSHRINK_RUNTIME_VERIFICATION_PATH),
            "corpus_atlas": str(CORPUS_ATLAS_PATH),
            "trading_bot_truth_corridor": str(TRADING_BOT_CORRIDOR_PATH),
            "orgin_atlas": str(ORGIN_ATLAS_PATH),
            "live_docs_gate_status": str(LIVE_DOCS_GATE_PATH),
        },
        "witness_basis": {
            "network_truth": network.get("truth", "NEAR"),
            "capability_truth": capability.get("truth", "NEAR"),
            "runtime_truth": runtime.get("truth", "NEAR"),
            "trading_bot_truth": trading_corridor.get("truth", "NEAR"),
        },
    }


def render_contract(payload: dict) -> str:
    lines = [
        "# QSHRINK Core Corridor Contract",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Truth: `{payload['truth']}`",
        f"- Focus: `{payload['focus']}`",
        f"- Active subfront: `{payload['active_subfront']}`",
        f"- Docs gate: `{payload['docs_gate']['state']}` / `{payload['docs_gate']['detail']}`",
        "",
        "## Omega",
        "",
        "QSHRINK's first core corridor is now formalized as a square-law contract: QSHRINK compresses, Athena FLEET routes, Trading Bot preserves truth-boundary law, Athena OS computes, and ORGIN remains the secondary seed reservoir.",
        "",
        "## Primary Bodies",
        "",
    ]

    for body in payload["primary_bodies"]:
        lines.extend(
            [
                f"### `{body['body']}`",
                "",
                f"- Truth: `{body['truth']}`",
                f"- Role: {body['role']}",
                f"- Atlas records: `{body['atlas_records']}`",
                f"- Surface files: `{body['surface_files']}`",
                f"- Size: `{human_bytes(body['size_bytes'])}`",
                f"- Route surface: `{body['route_surface']}`",
                "",
            ]
        )

    lines.extend(["## Secondary Body", ""])
    for body in payload["secondary_bodies"]:
        lines.extend(
            [
                f"### `{body['body']}`",
                "",
                f"- Truth: `{body['truth']}`",
                f"- Role: {body['role']}",
                f"- Atlas records: `{body['atlas_records']}`",
                f"- Size: `{human_bytes(body['size_bytes'])}`",
                f"- Route surface: `{body['route_surface']}`",
                "",
            ]
        )

    lines.extend(["## Corridor Legs", ""])
    for leg in payload["corridor_legs"]:
        lines.extend(
            [
                f"### {leg['id']} `{leg['name']}`",
                "",
                f"- Truth: `{leg['truth']}`",
                f"- Meaning: {leg['meaning']}",
                f"- Surfaces: {'; '.join(f'`{surface}`' for surface in leg['surfaces'])}",
                "",
            ]
        )

    lines.extend(["## Square Deficits", ""])
    for deficit in payload["square_deficits"]:
        resolution = deficit.get("resolution") or deficit.get("resolution_target", "")
        lines.extend(
            [
                f"### {deficit['id']} `{deficit['body']}`",
                "",
                f"- Truth: `{deficit['truth']}`",
                f"- Status: `{deficit['status']}`",
                f"- Deficit: {deficit['deficit']}",
                f"- Resolution: {resolution}",
                "",
            ]
        )

    lines.extend(["## Route Targets", ""])
    for target in payload["route_targets"]:
        lines.append(f"- `{target['body']}` -> `{target['target']}`")

    lines.extend(["", "## Promotion Thresholds", ""])
    for key, value in payload["promotion_thresholds"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(
        [
            "",
            "## Restart Seed",
            "",
            f"`{payload['next_seed']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_fleet_route_map(payload: dict, flower: dict | None = None) -> str:
    flower_intake = ""
    cadence_law = ""
    next_route = payload["next_seed"]
    if flower:
        flower_intake = (
            "- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`\n"
            "- `self_actualize/qshrink_connectivity_flower.json`\n"
        )
        line_names = "; ".join(f"`{line['id']} {line['name']}`" for line in flower.get("metro_lines", []))
        cadence_law = f"""
## Cadence law

The flower witness at `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
is now the cadence membrane for this route map.

Fixed metro lines:

- {line_names}

Zero-point hub:

- body: `Athena FLEET`
- witness: `FAMILY_athena_fleet_route_map.md`
"""
        next_route = flower.get("next_seed", next_route)

    return f"""# FAMILY Athena FLEET Route Map

## Intake

- `Athena FLEET/MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`
- `Athena FLEET/FLEET_MYCELIUM_NETWORK/00_README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
{flower_intake}- `self_actualize/qshrink_connectivity_square.json`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md`

## Main transfer

`QSHRINK -> Athena FLEET ecosystem -> Trading Bot truth corridor -> Athena OS qshrink runtime`

Secondary seed line:

`QSHRINK -> Athena FLEET ecosystem -> ORGIN seed leg`

## Law

- `QSHRINK -> Athena FLEET ecosystem`
- `Athena FLEET -> Trading Bot truth corridor`
- `Athena FLEET -> Athena OS qshrink runtime`
- `Athena FLEET -> ORGIN seed leg`
- blocked live Docs remain explicit truth and do not collapse into fake open-memory claims
{cadence_law}

## Next route

`{next_route}`
"""


def render_capsule(payload: dict) -> str:
    lines = [
        "# QSHRINK Core Corridor Contract",
        "",
        f"Truth class: `{payload['truth']}`",
        f"Active subfront: `{payload['active_subfront']}`",
        f"Docs gate: `{payload['docs_gate']['state']}` / `{payload['docs_gate']['detail']}`",
        "",
        "## Corridor Bodies",
        "",
    ]
    for body in payload["primary_bodies"]:
        lines.append(f"- `{body['body']}`: `{body['truth']}`")
    for body in payload["secondary_bodies"]:
        lines.append(f"- `{body['body']}`: `{body['truth']}`")

    lines.extend(["", "## Square Deficits", ""])
    for deficit in payload["square_deficits"]:
        lines.append(f"- `{deficit['body']}`: `{deficit['status']}`")

    lines.extend(["", "## Next Seed", "", f"`{payload['next_seed']}`"])
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()
    flower = load_json(QSHRINK_FLOWER_PATH) if QSHRINK_FLOWER_PATH.exists() else None
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_CONTRACT_PATH.write_text(render_contract(payload), encoding="utf-8")
    OUTPUT_FLEET_ROUTE_MAP_PATH.write_text(render_fleet_route_map(payload, flower), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    print(f"Wrote qshrink connectivity square json: {OUTPUT_JSON_PATH}")
    print(f"Wrote qshrink corridor contract: {OUTPUT_CONTRACT_PATH}")
    print(f"Wrote Athena FLEET route map: {OUTPUT_FLEET_ROUTE_MAP_PATH}")
    print(f"Wrote qshrink core corridor capsule: {OUTPUT_CAPSULE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
