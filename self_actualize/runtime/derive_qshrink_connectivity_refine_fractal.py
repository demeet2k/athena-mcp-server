from __future__ import annotations

from self_actualize.runtime.qshrink_refine_common import (
    CURRENT_CARRIED_WITNESS,
    DEEP_NETWORK_ROOT,
    FRONT_ID,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
    QSHRINK_ECOSYSTEM_ROOT,
    RESERVE_FRONTIER,
    atlas_metrics,
    capsule_output_path,
    docs_gate_payload,
    ecosystem_output_path,
    load_json,
    receipt_output_path,
    refinement_output_path,
    render_qshrink_ecosystem_readme,
    route_targets,
    utc_now,
    write_json,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_refine_fractal"


def build_payload() -> dict:
    cloud = load_json(refinement_output_path("cloud"), {"truth": "NEAR"})
    loop_stack = [
        {
            "id": "F1",
            "name": "external blocker loop",
            "body": "Trading Bot / Docs gate",
            "meaning": "keeps the blocked live-memory limb visible at every scale and never treats it as locally closed",
        },
        {
            "id": "F2",
            "name": "local refinement loop",
            "body": "Q42 with QS64-21..24",
            "meaning": "carries the Hall-local refine bundle as one replay-safe recursion stack",
        },
        {
            "id": "F3",
            "name": "deeper contract loop",
            "body": NEXT_TEMPLE_HANDOFF,
            "meaning": "hands immediate deeper execution to the runner-contract frontier after the Hall-local bundle closes",
        },
        {
            "id": "F4",
            "name": "reserve execution loop",
            "body": RESERVE_FRONTIER,
            "meaning": "keeps the reserve wave visible without letting it pre-empt the Hall-local bundle or Temple handoff",
        },
    ]
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "focus": "connectivity-refine-fractal",
        "front_id": FRONT_ID,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": PASS_IDS["fractal"],
        "next_hall_seed": None,
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "docs_gate": docs_gate_payload(),
        "control_plane_precedence": {
            "canonical_state": "generated refine witnesses plus verification sidecars",
            "historical_state": "change feed entries plus receipts",
            "temple_contract_canon": "TQ04 manifest/json/verifier/receipt bundle",
        },
        "upstream_refine_cloud": {
            "path": str(refinement_output_path("cloud")),
            "truth": cloud.get("truth", "NEAR"),
            "active_local_subfront": cloud.get("active_local_subfront", PASS_IDS["cloud"]),
        },
        "loop_stack": loop_stack,
        "recursive_theorem": "The Hall-local NEXT^4 bundle is recursively stable when the carried diagnose witness stays visible, the blocker stays external, the Temple handoff stays separate, and no new Hall-local seed is emitted beyond QS64-24.",
        "deep_metro_companion": {
            "root": str(DEEP_NETWORK_ROOT),
            "resolution": "carry the bundle through the live 4-level metro stack without creating a fifth Hall-local refinement quest",
        },
        "hall_local_bundle_closed": True,
        "control_fields": {
            "current_carried_witness": CURRENT_CARRIED_WITNESS,
            "active_local_subfront": PASS_IDS["fractal"],
            "next_hall_seed": None,
            "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_external_front": "Q02",
        },
        "writeback_targets": route_targets(),
        "corpus_metrics": atlas_metrics(),
    }


def render_witness(payload: dict) -> str:
    loops = "\n".join(
        f"- `{item['id']} {item['name']}`: `{item['body']}` / {item['meaning']}" for item in payload["loop_stack"]
    )
    next_hall_seed = payload["next_hall_seed"] if payload["next_hall_seed"] else "none; do not invent QS64-25"
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Fractal",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Front: `{payload['front_id']}`",
            f"- Current carried witness: `{payload['current_carried_witness']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Hall seed: `{next_hall_seed}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            f"- Docs gate: `{payload['docs_gate']['status']}` / `{payload['docs_gate']['detail']}`",
            "",
            "## Omega",
            "",
            payload["recursive_theorem"],
            "",
            "## Control-Plane Precedence",
            "",
            f"- canonical state: {payload['control_plane_precedence']['canonical_state']}",
            f"- historical state: {payload['control_plane_precedence']['historical_state']}",
            f"- temple contract canon: {payload['control_plane_precedence']['temple_contract_canon']}",
            "",
            "## Loop Stack",
            "",
            loops,
            "",
            "## Control Fields",
            "",
            f"- current carried witness: `{payload['control_fields']['current_carried_witness']}`",
            f"- active local subfront: `{payload['control_fields']['active_local_subfront']}`",
            "- next Hall seed: `none; do not invent QS64-25`",
            f"- next Temple handoff: `{payload['control_fields']['next_temple_handoff']}`",
            f"- reserve frontier: `{payload['control_fields']['reserve_frontier']}`",
            f"- blocked external front: `{payload['control_fields']['blocked_external_front']}`",
            "",
            "## Deep Metro Companion",
            "",
            f"- Root: `{payload['deep_metro_companion']['root']}`",
            f"- Resolution: {payload['deep_metro_companion']['resolution']}",
            "",
            "## Bundle Status",
            "",
            f"- Hall-local bundle closed: `{payload['hall_local_bundle_closed']}`",
            f"- Files scanned: `{payload['corpus_metrics'].get('total_files', 0)}`",
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    next_hall_seed = payload["next_hall_seed"] if payload["next_hall_seed"] else "none"
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Fractal",
            "",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{next_hall_seed}`",
            f"Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Docs gate: `{payload['docs_gate']['status']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    return "\n".join(
        [
            "# QS64-24 Connectivity Refine Fractal Receipt",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            "- Next Hall seed: `none; do not invent QS64-25`",
            "",
            "Fractal refinement landed as the recursive theorem witness for the NEXT^4 bundle. The Hall-local bundle closes on `QS64-24`, `TQ04` becomes the immediate deeper execution receiver, `Q46` stays reserve-only, the Docs blocker remains external, and no new Hall-local seed is emitted.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(refinement_output_path("fractal"), payload)
    ecosystem_output_path("fractal").write_text(render_witness(payload), encoding="utf-8")
    capsule_output_path("fractal").write_text(render_capsule(payload), encoding="utf-8")
    receipt_output_path("fractal").write_text(render_receipt(payload), encoding="utf-8")
    (QSHRINK_ECOSYSTEM_ROOT / "README.md").write_text(render_qshrink_ecosystem_readme(), encoding="utf-8")
    print(f"Wrote {refinement_output_path('fractal')}")
    print(f"Wrote {ecosystem_output_path('fractal')}")
    print(f"Wrote {capsule_output_path('fractal')}")
    print(f"Wrote {receipt_output_path('fractal')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
