from __future__ import annotations

from self_actualize.runtime.qshrink_refine_common import (
    AUTHORITATIVE_SQUARE_RECEIPT_FILE,
    BLOCKED_EXTERNAL_FRONT,
    CURRENT_CARRIED_WITNESS,
    FRONT_ID,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
    QSHRINK_CONNECTIVITY_CLOUD_PATH,
    QSHRINK_CONNECTIVITY_FRACTAL_PATH,
    QSHRINK_NETWORK_INTEGRATION_PATH,
    RECEIPTS_ROOT,
    RESERVE_FRONTIER,
    capsule_output_path,
    docs_gate_payload,
    ecosystem_output_path,
    load_json,
    receipt_output_path,
    refinement_output_path,
    route_targets,
    utc_now,
    write_json,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_refine_square"


def build_payload() -> dict:
    cloud = load_json(QSHRINK_CONNECTIVITY_CLOUD_PATH, {"truth": "NEAR"})
    fractal = load_json(QSHRINK_CONNECTIVITY_FRACTAL_PATH, {"truth": "NEAR"})
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "focus": "connectivity-refine-square",
        "front_id": FRONT_ID,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_subfront": PASS_IDS["square"],
        "active_local_subfront": PASS_IDS["square"],
        "next_seed": PASS_IDS["flower"],
        "next_hall_seed": PASS_IDS["flower"],
        "deeper_receiving_frontier": NEXT_TEMPLE_HANDOFF,
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "queued_follow_on": "P3 ORGIN",
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "authoritative_current_receipt": str(RECEIPTS_ROOT / AUTHORITATIVE_SQUARE_RECEIPT_FILE),
        "docs_gate": docs_gate_payload(),
        "upstream_witnesses": [
            {
                "id": "Cloud",
                "path": str(QSHRINK_CONNECTIVITY_CLOUD_PATH),
                "truth": cloud.get("truth", "NEAR"),
                "active_subfront": cloud.get("active_subfront", "QS64-19 Connectivity-Diagnose-Cloud"),
            },
            {
                "id": "Fractal",
                "path": str(QSHRINK_CONNECTIVITY_FRACTAL_PATH),
                "truth": fractal.get("truth", "NEAR"),
                "active_subfront": fractal.get("active_subfront", CURRENT_CARRIED_WITNESS),
            },
        ],
        "precedence_membrane": {
            "current_carried_witness": CURRENT_CARRIED_WITNESS,
            "active_owner_facing_pass": PASS_IDS["square"],
            "next_hall_seed_on_entry": PASS_IDS["square"],
            "next_hall_seed_after_writeback": PASS_IDS["flower"],
            "deeper_receiving_frontier": NEXT_TEMPLE_HANDOFF,
            "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
            "queued_follow_on": "P3 ORGIN",
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        },
        "structural_distinctions": [
            {
                "field": "current_carried_witness",
                "value": CURRENT_CARRIED_WITNESS,
                "meaning": "the landed diagnose witness carried into the NEXT^4 refine bundle",
            },
            {
                "field": "active_local_subfront",
                "value": PASS_IDS["square"],
                "meaning": "the current owner-facing Hall-local refinement pass",
            },
            {
                "field": "next_hall_seed",
                "value": PASS_IDS["flower"],
                "meaning": "the next Hall-local seed after square writeback lands",
            },
            {
                "field": "next_temple_handoff",
                "value": NEXT_TEMPLE_HANDOFF,
                "meaning": "the separate deeper Temple receiver that does not replace the Hall-local seed",
            },
            {
                "field": "queued_follow_on",
                "value": "P3 ORGIN",
                "meaning": "the queue-visible ORGIN follow-on that stays behind the next Hall seed",
            },
            {
                "field": "reserve_frontier",
                "value": RESERVE_FRONTIER,
                "meaning": "the reserve frontier kept behind the Hall-local refine bundle",
            },
            {
                "field": "blocked_external_front",
                "value": BLOCKED_EXTERNAL_FRONT,
                "meaning": "the external Docs front that remains blocked and separate",
            },
        ],
        "writeback_targets": route_targets(),
        "integration_refresh_target": str(QSHRINK_NETWORK_INTEGRATION_PATH),
    }


def render_witness(payload: dict) -> str:
    distinctions = "\n".join(
        f"- `{item['field']}` = `{item['value']}`: {item['meaning']}" for item in payload["structural_distinctions"]
    )
    routes = "\n".join(
        f"- `{item['body']}` -> `{item['target']}`" for item in payload["writeback_targets"]
    )
    witnesses = "\n".join(
        f"- `{item['id']}`: `{item['active_subfront']}` / `{item['truth']}` / `{item['path']}`"
        for item in payload["upstream_witnesses"]
    )
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Square",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Front: `{payload['front_id']}`",
            f"- Current carried witness: `{payload['current_carried_witness']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Hall seed: `{payload['next_hall_seed']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Queued follow-on: `{payload['queued_follow_on']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            f"- Docs gate: `{payload['docs_gate']['status']}` / `{payload['docs_gate']['detail']}`",
            "",
            "## Omega",
            "",
            "Square refinement separates the carried diagnose witness from the active Hall-local pass, the next Hall-local seed, the deeper Temple handoff, the reserve frontier, and the blocked external front so QSHRINK control surfaces stop collapsing them into one slot.",
            "",
            "## Precedence Membrane",
            "",
            distinctions,
            "",
            "## Upstream Witnesses",
            "",
            witnesses,
            "",
            "## Writeback Targets",
            "",
            routes,
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Square",
            "",
            f"Front: `{payload['front_id']}`",
            f"Carried witness: `{payload['current_carried_witness']}`",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{payload['next_hall_seed']}`",
            f"Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"Queued follow-on: `{payload['queued_follow_on']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Docs gate: `{payload['docs_gate']['status']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    return "\n".join(
        [
            "# QS64-21 Connectivity Refine Square Receipt",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Current carried witness: `{payload['current_carried_witness']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Hall seed after writeback: `{payload['next_hall_seed']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Queued follow-on: `{payload['queued_follow_on']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            f"- Blocked external front: `{payload['blocked_external_front']}`",
            "",
            "Square refinement landed as the structural precedence membrane for the NEXT^4 bundle. The carried diagnose witness stays `QS64-20`, the active owner-facing Hall pass becomes `QS64-21`, the next Hall-local seed becomes `QS64-22`, `TQ04` stays separate as the deeper receiver, `P3 ORGIN` stays queue-visible, `Q45` stays reserve-only, and the blocked Docs front stays external.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(refinement_output_path("square"), payload)
    ecosystem_output_path("square").write_text(render_witness(payload), encoding="utf-8")
    capsule_output_path("square").write_text(render_capsule(payload), encoding="utf-8")
    receipt_output_path("square").write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote {refinement_output_path('square')}")
    print(f"Wrote {ecosystem_output_path('square')}")
    print(f"Wrote {capsule_output_path('square')}")
    print(f"Wrote {receipt_output_path('square')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
