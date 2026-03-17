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


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_connectivity_refine_flower"


def build_payload() -> dict:
    square = load_json(refinement_output_path("square"), {"truth": "NEAR"})
    cadence_rails = [
        {
            "id": "R1",
            "name": "local-refinement rail",
            "route": "Q42 -> QS64-21 Connectivity-Refine-Square -> QS64-22 Connectivity-Refine-Flower -> QS64-23 Connectivity-Refine-Cloud -> QS64-24 Connectivity-Refine-Fractal",
            "cadence_class": "hall-local-refine-loop",
            "meaning": "keeps the four-pass NEXT^4 bundle ordered as one Hall-local refinement rail",
        },
        {
            "id": "R2",
            "name": "deeper-handoff rail",
            "route": "Q42 writeback -> TQ04: Bind The Helical Schema Pack To A Runner Contract",
            "cadence_class": "temple-receiver",
            "meaning": "hands deeper execution to TQ04 without letting Temple pressure overwrite the Hall-local seed",
        },
        {
            "id": "R3",
            "name": "reserve-growth rail",
            "route": "Q42 / TQ04 stable -> Q46",
            "cadence_class": "reserve-only",
            "meaning": "keeps Q46 visible as a reserve frontier without promoting it into the NEXT^4 bundle",
        },
        {
            "id": "R4",
            "name": "blocker-overlay rail",
            "route": "Trading Bot -> live_docs_gate_status -> Hall truth",
            "cadence_class": "external-blocker-overlay",
            "meaning": "pins the blocked Docs limb as an external truth overlay across every local refinement pass",
        },
    ]
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "focus": "connectivity-refine-flower",
        "front_id": FRONT_ID,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": PASS_IDS["flower"],
        "next_hall_seed": PASS_IDS["cloud"],
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "docs_gate": docs_gate_payload(),
        "upstream_refine_square": {
            "path": str(refinement_output_path("square")),
            "truth": square.get("truth", "NEAR"),
            "active_local_subfront": square.get("active_local_subfront", PASS_IDS["square"]),
        },
        "cadence_rails": cadence_rails,
        "writeback_targets": route_targets(),
    }


def render_witness(payload: dict) -> str:
    rails = "\n".join(
        f"- `{item['id']} {item['name']}`: `{item['route']}` / `{item['cadence_class']}` / {item['meaning']}"
        for item in payload["cadence_rails"]
    )
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Flower",
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
            "Flower refinement fixes one cadence law across local Hall refinement, deeper Temple handoff, reserve growth, and blocker overlay so all QSHRINK control surfaces share the same rail grammar before cloud reranking begins.",
            "",
            "## Fixed Rails",
            "",
            rails,
            "",
            "## Upstream Refine Square",
            "",
            f"- `{payload['upstream_refine_square']['active_local_subfront']}` / `{payload['upstream_refine_square']['truth']}` / `{payload['upstream_refine_square']['path']}`",
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    return "\n".join(
        [
            "# QSHRINK Connectivity Refine Flower",
            "",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{payload['next_hall_seed']}`",
            f"Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Docs gate: `{payload['docs_gate']['status']}`",
            "",
        ]
    )


def render_receipt(payload: dict) -> str:
    rails = ", ".join(item["id"] for item in payload["cadence_rails"])
    return "\n".join(
        [
            "# QS64-22 Connectivity Refine Flower Receipt",
            "",
            f"- Truth: `{payload['truth']}`",
            f"- Active local subfront: `{payload['active_local_subfront']}`",
            f"- Fixed rails: `{rails}`",
            f"- Next Hall seed: `{payload['next_hall_seed']}`",
            f"- Next Temple handoff: `{payload['next_temple_handoff']}`",
            f"- Reserve frontier: `{payload['reserve_frontier']}`",
            "",
            "Flower refinement landed as the cadence-law layer of the NEXT^4 bundle. The Hall-local refine loop, Temple receiver, reserve frontier, and external blocker overlay now each have a fixed rail so the Cloud pass can rank pressure without reopening cadence ambiguity.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(refinement_output_path("flower"), payload)
    ecosystem_output_path("flower").write_text(render_witness(payload), encoding="utf-8")
    capsule_output_path("flower").write_text(render_capsule(payload), encoding="utf-8")
    receipt_output_path("flower").write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote {refinement_output_path('flower')}")
    print(f"Wrote {ecosystem_output_path('flower')}")
    print(f"Wrote {capsule_output_path('flower')}")
    print(f"Wrote {receipt_output_path('flower')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
