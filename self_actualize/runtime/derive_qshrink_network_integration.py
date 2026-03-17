from __future__ import annotations

from typing import Any

from self_actualize.runtime.qshrink_refine_common import (
    AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH,
    AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH,
    BLOCKED_EXTERNAL_FRONT,
    CAPSULE_ROOT,
    CURRENT_CARRIED_WITNESS,
    FRONT_ID,
    FRONT_TITLE,
    FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH,
    NEXT_TEMPLE_HANDOFF,
    QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH,
    QSHRINK_ACTIVE_FRONT_PATH,
    QSHRINK_AGENT_TASK_MATRIX_PATH,
    QSHRINK_CAPABILITY_STACK_PATH,
    QSHRINK_FAMILY_PATH,
    QSHRINK_NETWORK_INTEGRATION_PATH,
    QSHRINK_REFINEMENT_CLOUD_PATH,
    QSHRINK_REFINEMENT_FLOWER_PATH,
    QSHRINK_REFINEMENT_FRACTAL_PATH,
    QSHRINK_REFINEMENT_SQUARE_PATH,
    QSHRINK_ROUTE_MAP_PATH,
    QSHRINK_RUNTIME_VERIFICATION_PATH,
    RESERVE_FRONTIER,
    atlas_metrics,
    docs_gate_payload,
    load_json,
    relative_string,
    route_targets,
    utc_now,
    write_json,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_network_integration"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "02_qshrink_shiva_corpus_ecosystem.md"
ACTIVE_LOCAL_SUBFRONT = "QS64-24 Connectivity-Refine-Fractal"
NEXT_HALL_SEED = None
NEXT_HALL_SEED_DISPLAY = "none; do not invent QS64-25"


def build_payload() -> dict[str, Any]:
    refine_square = load_json(QSHRINK_REFINEMENT_SQUARE_PATH, {"truth": "NEAR"})
    refine_flower = load_json(QSHRINK_REFINEMENT_FLOWER_PATH, {"truth": "NEAR"})
    refine_cloud = load_json(QSHRINK_REFINEMENT_CLOUD_PATH, {"truth": "NEAR"})
    refine_fractal = load_json(QSHRINK_REFINEMENT_FRACTAL_PATH, {"truth": "NEAR"})
    runtime_verification = load_json(QSHRINK_RUNTIME_VERIFICATION_PATH, {"truth": "NEAR"})
    capability_stack = load_json(QSHRINK_CAPABILITY_STACK_PATH, {"truth": "NEAR"})
    full_corpus_registry = load_json(QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH, {"truth": "NEAR"})
    four_agent_meta_loop = full_corpus_registry.get("four_agent_meta_loop", {})

    ranked_pressures = refine_cloud.get("ranked_pressures", [])
    loop_stack = refine_fractal.get("loop_stack", [])
    hall_local_bundle_closed = bool(refine_fractal.get("hall_local_bundle_closed", False))

    payload: dict[str, Any] = {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": refine_fractal.get("truth", "NEAR"),
        "front_id": FRONT_ID,
        "front_title": FRONT_TITLE,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": ACTIVE_LOCAL_SUBFRONT,
        "active_subfront": ACTIVE_LOCAL_SUBFRONT,
        "next_hall_seed": NEXT_HALL_SEED,
        "next_seed": NEXT_HALL_SEED,
        "next_hall_seed_display": NEXT_HALL_SEED_DISPLAY,
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "docs_gate": docs_gate_payload(),
        "control_plane_precedence": {
            "canonical_state": "generated refine witnesses plus verification sidecars",
            "historical_state": "change feed entries plus receipts",
            "temple_contract_canon": "TQ04 manifest/json/verifier/receipt bundle",
        },
        "runtime_verification_truth": runtime_verification.get("truth", "NEAR"),
        "capability_stack_truth": capability_stack.get("truth", "NEAR"),
        "connectivity_refine_square_truth": refine_square.get("truth", "NEAR"),
        "connectivity_refine_flower_truth": refine_flower.get("truth", "NEAR"),
        "connectivity_refine_cloud_truth": refine_cloud.get("truth", "NEAR"),
        "connectivity_refine_fractal_truth": refine_fractal.get("truth", "NEAR"),
        "cadence_rails": refine_flower.get("cadence_rails", []),
        "ranked_pressures": ranked_pressures,
        "top_priority_pressure": ranked_pressures[0] if ranked_pressures else {},
        "selection_discipline": refine_cloud.get("selection_discipline", []),
        "loop_stack": loop_stack,
        "recursive_theorem": refine_fractal.get("recursive_theorem", ""),
        "hall_local_bundle_closed": hall_local_bundle_closed,
        "immediate_deeper_receiver": NEXT_TEMPLE_HANDOFF,
        "route_targets": route_targets(),
        "full_corpus_integration_truth": full_corpus_registry.get("truth", "NEAR"),
        "awakening_transition_note_layer": full_corpus_registry.get("ap6d_transition_note_layer", {}),
        "awakening_source_atlas": full_corpus_registry.get("awakening_source_atlas", {}),
        "ap6d_core_agents": full_corpus_registry.get("ap6d_core_agents", []),
        "feeder_fronts": full_corpus_registry.get("feeder_fronts", []),
        "four_agent_meta_loop_truth": four_agent_meta_loop.get("truth", "NEAR"),
        "four_agent_meta_loop": four_agent_meta_loop,
        "corpus_metrics": atlas_metrics(),
        "receipt_chain": [
            str(path)
            for path in [
                QSHRINK_REFINEMENT_SQUARE_PATH,
                QSHRINK_REFINEMENT_FLOWER_PATH,
                QSHRINK_REFINEMENT_CLOUD_PATH,
                QSHRINK_REFINEMENT_FRACTAL_PATH,
                QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH,
                FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH,
                AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH,
            ]
        ],
        "source_paths": {
            "runtime_verification": str(QSHRINK_RUNTIME_VERIFICATION_PATH),
            "capability_stack": str(QSHRINK_CAPABILITY_STACK_PATH),
            "refine_square": str(QSHRINK_REFINEMENT_SQUARE_PATH),
            "refine_flower": str(QSHRINK_REFINEMENT_FLOWER_PATH),
            "refine_cloud": str(QSHRINK_REFINEMENT_CLOUD_PATH),
            "refine_fractal": str(QSHRINK_REFINEMENT_FRACTAL_PATH),
            "agent_task_matrix": str(QSHRINK_AGENT_TASK_MATRIX_PATH),
            "full_corpus_integration_registry": str(QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH),
            "awakening_source_atlas": str(FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH),
            "awakening_transition_notes_json": str(AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH),
            "awakening_transition_notes_markdown": str(AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH),
        },
    }
    return payload


def render_family(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# FAMILY QSHRINK Internal Use",
            "",
            f"Date: `{payload['generated_at'][:10]}`",
            f"Truth: `{payload['truth']}`",
            "",
            "## Role",
            "",
            "QSHRINK remains Athena's contraction organ. The live control story now keeps the diagnose witness visible as carried memory, closes the Hall-local NEXT^4 refine bundle on `QS64-24`, and hands immediate deeper execution to `TQ04` without inventing `QS64-25`.",
            "",
            "## Control Plane",
            "",
            f"- Front ID: `{payload['front_id']}`",
            f"- Current carried witness: `{payload['current_carried_witness']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Hall seed: `{payload['next_hall_seed_display']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            f"- Blocked external front: `{payload['blocked_external_front']}`",
            f"- Docs gate: `{payload['docs_gate']['status']}` / `{payload['docs_gate']['detail']}`",
            "",
            "## Bundle Closure",
            "",
            f"- Square truth: `{payload['connectivity_refine_square_truth']}`",
            f"- Flower truth: `{payload['connectivity_refine_flower_truth']}`",
            f"- Cloud truth: `{payload['connectivity_refine_cloud_truth']}`",
            f"- Fractal truth: `{payload['connectivity_refine_fractal_truth']}`",
            f"- Hall-local bundle closed: `{payload['hall_local_bundle_closed']}`",
            f"- Immediate deeper receiver: `{payload['immediate_deeper_receiver']}`",
            "",
            "## AP6D Integration Layer",
            "",
            f"- full-corpus integration truth: `{payload['full_corpus_integration_truth']}`",
            f"- transition note layer: `{payload['awakening_transition_note_layer'].get('status', 'missing')}`",
            f"- awakening source atlas: `{payload['awakening_source_atlas'].get('path', relative_string(FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH))}`",
            f"- transition note markdown: `{relative_string(AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH)}`",
            f"- feeder fronts preserved: `{', '.join(item['front_id'] for item in payload['feeder_fronts'])}`",
            "",
            "## Control-Plane Precedence",
            "",
            f"- canonical state: {payload['control_plane_precedence']['canonical_state']}",
            f"- historical state: {payload['control_plane_precedence']['historical_state']}",
            f"- temple contract canon: {payload['control_plane_precedence']['temple_contract_canon']}",
            "",
        ]
    ) + "\n"


def render_route_map(payload: dict[str, Any]) -> str:
    rails = "\n".join(
        f"- `{item['id']} {item['name']}`: `{item['route']}` / `{item['cadence_class']}`"
        for item in payload["cadence_rails"]
    )
    loops = "\n".join(
        f"- `{item['id']} {item['name']}`: `{item['body']}`" for item in payload["loop_stack"]
    )
    ranked = "\n".join(
        f"- `{item['id']} {item['title']}`: `{item['selection_state']}` / `{item['truth']}`"
        for item in payload["ranked_pressures"]
    )
    return "\n".join(
        [
            "# FAMILY QSHRINK Athena Internal Use Route Map",
            "",
            "## Current Route",
            "",
            f"`Q42 -> {payload['current_carried_witness']} (carried witness) -> QS64-21..24 (closed Hall-local bundle) -> {payload['next_temple_handoff']} -> {payload['reserve_frontier']} (reserve only)`",
            "",
            "## Control Fields",
            "",
            f"- current carried witness: `{payload['current_carried_witness']}`",
            f"- active local subfront: `{payload['active_local_subfront']}`",
            f"- next Hall seed: `{payload['next_hall_seed_display']}`",
            f"- next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- reserve frontier: `{payload['reserve_frontier']}`",
            f"- blocked external front: `{payload['blocked_external_front']}`",
            f"- docs gate: `{payload['docs_gate']['status']}`",
            "",
            "## Cadence Law",
            "",
            rails,
            "",
            "## Cloud Ranking",
            "",
            ranked,
            "",
            "## Recursive Law",
            "",
            loops,
            "",
            "## Awakening Note Layer",
            "",
            f"- transition note layer: `{payload['awakening_transition_note_layer'].get('status', 'missing')}`",
            f"- source atlas path: `{payload['awakening_source_atlas'].get('path', relative_string(FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH))}`",
            f"- note bundle path: `{relative_string(AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH)}`",
            "",
            ]
    ) + "\n"


def render_active_front(payload: dict[str, Any]) -> str:
    top_pressure = payload["top_priority_pressure"]
    top_pressure_label = top_pressure.get("title", "Docs blocker overlay")
    return "\n".join(
        [
            "# QSHRINK ACTIVE FRONT",
            "",
            "## FrontID",
            "",
            f"`{payload['front_id']}`",
            "",
            "## Quest",
            "",
            payload["front_title"],
            "",
            "## State",
            "",
            "`OPEN`",
            "",
            "## Truth",
            "",
            f"`{payload['truth']}`",
            "",
            "## Objective",
            "",
            f"keep `{payload['current_carried_witness']}` visible as the carried diagnose witness under `Q42`, preserve `{payload['active_local_subfront']}` as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to `{payload['next_temple_handoff']}`, keep `{payload['reserve_frontier']}` reserve-only, and keep the blocked Docs gate external as `{payload['blocked_external_front']}`",
            "",
            "## Why Now",
            "",
            "the local refine bundle is already landed, so the honest move is control-plane freshness and handoff clarity rather than inventing a new Hall-local `QS64-25` or collapsing Temple, reserve, and blocker fronts into one seed field",
            "",
            "## Current Carried Witness",
            "",
            f"`{payload['current_carried_witness']}`",
            "",
            "## Active Local Subfront",
            "",
            f"`{payload['active_local_subfront']}`",
            "",
            "## Next Hall Seed",
            "",
            f"`{payload['next_hall_seed_display']}`",
            "",
            "## Immediate Deeper Receiver",
            "",
            f"`{payload['next_temple_handoff']}`",
            "",
            "## Reserve Frontier",
            "",
            f"`{payload['reserve_frontier']}`",
            "",
            "## Blocked External Front",
            "",
            f"`{payload['blocked_external_front']}`",
            "",
            "## Pressure Order",
            "",
            f"- pinned blocker: `{top_pressure_label}`",
            "- promoted non-blocker receiver: `TQ04 runner handoff`",
            "- reserve-only frontier: `Q46`",
            "- blocked external overlay: `Q02 / Docs gate`",
            "",
            "## Precedence",
            "",
            f"- canonical state: {payload['control_plane_precedence']['canonical_state']}",
            f"- historical state: {payload['control_plane_precedence']['historical_state']}",
            "",
            "## Awakening Layer",
            "",
            f"- transition note layer: `{payload['awakening_transition_note_layer'].get('status', 'missing')}`",
            f"- core agents: `{', '.join(item['agent_id'] for item in payload['ap6d_core_agents'])}`",
            f"- note bundle: `{relative_string(AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH)}`",
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# QSHRINK Shiva Corpus Ecosystem",
            "",
            f"Truth class: `{payload['truth']}`",
            f"Current carried witness: `{payload['current_carried_witness']}`",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{payload['next_hall_seed_display']}`",
            f"Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Blocked external front: `{payload['blocked_external_front']}`",
            f"Docs gate: `{payload['docs_gate']['status']}`",
            f"AP6D note layer: `{payload['awakening_transition_note_layer'].get('status', 'missing')}`",
            "",
            "Q42 stays open as the umbrella frontier, the Hall-local NEXT^4 bundle is closed on `QS64-24`, and immediate deeper execution now routes to `TQ04` without creating `QS64-25`.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(QSHRINK_NETWORK_INTEGRATION_PATH, payload)
    QSHRINK_FAMILY_PATH.write_text(render_family(payload), encoding="utf-8")
    QSHRINK_ROUTE_MAP_PATH.write_text(render_route_map(payload), encoding="utf-8")
    QSHRINK_ACTIVE_FRONT_PATH.write_text(render_active_front(payload), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    print(f"Wrote {QSHRINK_NETWORK_INTEGRATION_PATH}")
    print(f"Wrote {QSHRINK_FAMILY_PATH}")
    print(f"Wrote {QSHRINK_ROUTE_MAP_PATH}")
    print(f"Wrote {QSHRINK_ACTIVE_FRONT_PATH}")
    print(f"Wrote {OUTPUT_CAPSULE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
