from __future__ import annotations

from self_actualize.runtime.qshrink_refine_common import (
    CURRENT_CARRIED_WITNESS,
    FRONT_ID,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
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


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_refine_cloud"


def build_payload() -> dict:
    flower = load_json(refinement_output_path("flower"), {"truth": "NEAR"})
    ranked_pressures = [
        {
            "id": "P1",
            "title": "Docs blocker overlay",
            "body": "Trading Bot",
            "truth": "FAIL",
            "selection_state": "PINNED_BLOCKER",
            "meaning": "The Docs gate stays visible and outranks every local NEAR item until credentials exist and authenticate.",
        },
        {
            "id": "P2",
            "title": "Temple runner handoff gap",
            "body": "TQ04 binding gap",
            "truth": "NEAR",
            "selection_state": "PROMOTE_NEXT",
            "meaning": "Once local refinement law is stable, the runner-contract handoff is the highest unresolved non-blocker.",
        },
        {
            "id": "P3",
            "title": "control-surface drift",
            "body": "generator-owned QSHRINK / Hall / Temple disagreement",
            "truth": "NEAR",
            "selection_state": "QUEUE_VISIBLE",
            "meaning": "Surface agreement remains a visible pressure even after the structural and cadence passes land.",
        },
        {
            "id": "P4",
            "title": "ORGIN mirror deepening",
            "body": "ORGIN",
            "truth": "NEAR",
            "selection_state": "QUEUE_VISIBLE",
            "meaning": "ORGIN remains a real but lower-ranked local follow-on after TQ04 and control-surface agreement.",
        },
        {
            "id": "P5",
            "title": "stability anchors",
            "body": "QSHRINK plus Athena FLEET / Hall",
            "truth": "OK",
            "selection_state": "STABILITY_ANCHOR",
            "meaning": "The contraction root and Hall writeback stay present as anchors and never outrank active blockers or refine gaps.",
        },
    ]
    selection_discipline = [
        "Pinned Docs blocker always stays visible.",
        "TQ04 outranks ORGIN once local refinement law is stable.",
        "Stability anchors never outrank live blockers or active refinement gaps.",
        "No pass may claim authenticated Docs success while the gate is blocked.",
    ]
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "focus": "connectivity-refine-cloud",
        "front_id": FRONT_ID,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": PASS_IDS["cloud"],
        "next_hall_seed": PASS_IDS["fractal"],
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "docs_gate": docs_gate_payload(),
        "upstream_refine_flower": {
            "path": str(refinement_output_path("flower")),
            "truth": flower.get("truth", "NEAR"),
            "active_local_subfront": flower.get("active_local_subfront", PASS_IDS["flower"]),
        },
        "ranked_pressures": ranked_pressures,
        "selection_discipline": selection_discipline,
        "writeback_targets": route_targets(),
    }


def render_witness(payload: dict) -> str:
    ranked = "\n".join(
        f"- `{item['id']} {item['title']}`: `{item['body']}` / `{item['truth']}` / `{item['selection_state']}` / {item['meaning']}"
        for item in payload["ranked_pressures"]
    )
    rules = "\n".join(f"- {rule}" for rule in payload["selection_discipline"])
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Cloud",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Front: `{payload['front_id']}`",
            f"- Current carried witness: `{payload['current_carried_witness']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Next Hall seed: `{payload['next_hall_seed']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            f"- Docs gate: `{payload['docs_gate']['status']}` / `{payload['docs_gate']['detail']}`",
            "",
            "## Omega",
            "",
            "Cloud refinement reranks the corridor after structure and cadence are explicit, keeping the Docs blocker pinned, promoting the Temple runner handoff gap above local mirror deepening, and preserving QSHRINK plus Athena FLEET / Hall as stability anchors.",
            "",
            "## Ranked Pressures",
            "",
            ranked,
            "",
            "## Selection Discipline",
            "",
            rules,
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    top = payload["ranked_pressures"][0]
    next_item = payload["ranked_pressures"][1]
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Cloud",
            "",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Top blocker: `{top['id']} {top['body']}` / `{top['selection_state']}`",
            f"Next promotion target: `{next_item['id']} {next_item['body']}` / `{next_item['selection_state']}`",
            f"Next Hall seed: `{payload['next_hall_seed']}`",
            f"Next Temple handoff: `{payload['next_temple_handoff']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    top = payload["ranked_pressures"][0]
    return "\n".join(
        [
            "# QS64-23 Connectivity Refine Cloud Receipt",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Top ranked pressure: `{top['id']} {top['title']}`",
            f"- Next Hall seed: `{payload['next_hall_seed']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            "",
            "Cloud refinement landed as the ranked-pressure layer of the NEXT^4 bundle. The Docs blocker remains pinned, `TQ04` now outranks ORGIN once local law is stable, control-surface drift remains visible, and the final Hall-local pass advances to `QS64-24 Connectivity-Refine-Fractal`.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(refinement_output_path("cloud"), payload)
    ecosystem_output_path("cloud").write_text(render_witness(payload), encoding="utf-8")
    capsule_output_path("cloud").write_text(render_capsule(payload), encoding="utf-8")
    receipt_output_path("cloud").write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote {refinement_output_path('cloud')}")
    print(f"Wrote {ecosystem_output_path('cloud')}")
    print(f"Wrote {capsule_output_path('cloud')}")
    print(f"Wrote {receipt_output_path('cloud')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
