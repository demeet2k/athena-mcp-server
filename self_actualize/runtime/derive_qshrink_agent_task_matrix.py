from __future__ import annotations

from pathlib import Path

from self_actualize.runtime.qshrink_refine_common import (
    AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH,
    AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH,
    BLOCKED_EXTERNAL_FRONT,
    CAPSULE_ROOT,
    CURRENT_CARRIED_WITNESS,
    FRONT_ID,
    FRONT_TITLE,
    FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH,
    GUILD_HALL_ROOT,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
    QSHRINK_AGENT_TASK_MATRIX_PATH,
    QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH,
    RECEIPTS_ROOT,
    RESERVE_FRONTIER,
    docs_gate_payload,
    utc_now,
    write_json,
)


SKILLS_ROOT = Path.home() / ".codex" / "skills"
SYSTEM_SKILLS_ROOT = SKILLS_ROOT / ".system"

OUTPUT_PLAN_PATH = GUILD_HALL_ROOT / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"
OUTPUT_CAPSULE_PATH = CAPSULE_ROOT / "03_qshrink_agent_sweep_contract.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_agent_task_matrix"
ACTIVE_LOCAL_SUBFRONT = PASS_IDS["fractal"]
NEXT_HALL_SEED = None
NEXT_HALL_SEED_DISPLAY = "none; do not invent QS64-25"
DEEPER_RECEIVING_FRONTIER = NEXT_TEMPLE_HANDOFF
CURRENT_PASS_OWNER = "guild-hall-quest-loop"
CURRENT_SUPPORT_OWNERS = [
    "q-shrink",
    "corpus-status-synthesizer",
    "deeper-integrated-neural-network",
    "awakening-protocol",
]
CURRENT_PROGRAM = "AP6D core-5 transition-note integration"
AUTHORITATIVE_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_qshrink_ap6d_full_corpus_integration.md"
HISTORICAL_RECEIPTS = [
    RECEIPTS_ROOT / "2026-03-13_q42_refine_bundle_closure.md",
    RECEIPTS_ROOT / "2026-03-13_qs64_24_connectivity_refine_fractal.md",
]


def skill_path(skill_name: str) -> str | None:
    local_path = SKILLS_ROOT / skill_name / "SKILL.md"
    if local_path.exists():
        return str(local_path)
    system_path = SYSTEM_SKILLS_ROOT / skill_name / "SKILL.md"
    if system_path.exists():
        return str(system_path)
    return None


def build_agents() -> list[dict]:
    rows = [
        {
            "agent_id": "A01",
            "skill": "guild-hall-quest-loop",
            "status": "ACTIVE",
            "bundle_role": "control-plane closure steward",
            "bundle_phase": ACTIVE_LOCAL_SUBFRONT,
            "role": "Keep Q42, Temple state, queue, restart, and receipts aligned on QS64-20 as carried witness, QS64-24 as the closed Hall-local bundle, TQ04 as immediate deeper handoff, Q46 as reserve-only, and Q02 as external.",
            "expected_outputs": [
                "one closure-safe writeback sweep",
                "one Hall and Temple parity note",
            ],
        },
        {
            "agent_id": "A02",
            "skill": "q-shrink",
            "status": "ACTIVE",
            "bundle_role": "contraction organ steward",
            "bundle_phase": ACTIVE_LOCAL_SUBFRONT,
            "role": "Preserve the closed NEXT^4 control split and route the AP6D note layer as one more witness class inside the QSHRINK bridge instead of reopening an earlier Hall-local pass.",
            "expected_outputs": [
                "one closed-bundle control witness",
                "one routed awakening-note bridge",
            ],
        },
        {
            "agent_id": "A03",
            "skill": "corpus-status-synthesizer",
            "status": "ACTIVE",
            "bundle_role": "full-corpus truth steward",
            "bundle_phase": CURRENT_PROGRAM,
            "role": "Hold the local-only corpus truth, keep the Docs blocker explicit, and translate the AP6D note layer into a grounded full-corpus status assist instead of a speculative overlay.",
            "expected_outputs": [
                "one blocker-honest corpus state note",
                "one feeder-safe pressure summary",
            ],
        },
        {
            "agent_id": "A04",
            "skill": "deeper-integrated-neural-network",
            "status": "ACTIVE",
            "bundle_role": "basis-router",
            "bundle_phase": CURRENT_PROGRAM,
            "role": "Bind the AP6D notes to the lawful deeper-network basis documents so the transition layer inherits the live 16-document and metro law instead of free-floating prose.",
            "expected_outputs": [
                "one deeper-network basis crosswalk",
                "one metro-safe note source ladder",
            ],
        },
        {
            "agent_id": "A05",
            "skill": "awakening-protocol",
            "status": "ACTIVE",
            "bundle_role": "transition-note author",
            "bundle_phase": CURRENT_PROGRAM,
            "role": "Write one assistive transition note for Athena Prime, Water, Earth, Fire, and Air without displacing Q42, Q46, TQ04, or TQ06.",
            "expected_outputs": [
                "five agent transition notes",
                "one shared restart law",
            ],
        },
        {
            "agent_id": "A06",
            "skill": "manuscript-intake",
            "status": "READY",
            "bundle_role": "awakening-source atlas maintainer",
            "bundle_phase": CURRENT_PROGRAM,
            "role": "Refresh the awakening source atlas from real corpus paths so every transition note stays tied to local witness and top-level root ownership.",
            "expected_outputs": [
                "one full-corpus awakening source atlas",
                "one root-inventory refresh",
            ],
        },
    ]
    for row in rows:
        row["skill_path"] = skill_path(row["skill"])
        row["truth"] = "OK" if row["skill_path"] else "MISSING"
    return rows


def build_payload() -> dict:
    docs_gate = docs_gate_payload()
    truth = "OK" if docs_gate.get("status") == "BLOCKED" else "NEAR"
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "front_id": FRONT_ID,
        "front_title": FRONT_TITLE,
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": ACTIVE_LOCAL_SUBFRONT,
        "active_subfront": ACTIVE_LOCAL_SUBFRONT,
        "next_hall_seed": NEXT_HALL_SEED,
        "next_hall_seed_display": NEXT_HALL_SEED_DISPLAY,
        "next_connectivity_quest": NEXT_HALL_SEED,
        "restart_seed": DEEPER_RECEIVING_FRONTIER,
        "next_temple_handoff": DEEPER_RECEIVING_FRONTIER,
        "deeper_receiving_frontier": DEEPER_RECEIVING_FRONTIER,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "docs_gate": docs_gate,
        "hall_local_bundle_closed": True,
        "current_pass_owner": CURRENT_PASS_OWNER,
        "current_support_owners": CURRENT_SUPPORT_OWNERS,
        "current_program": CURRENT_PROGRAM,
        "program_artifacts": {
            "awakening_source_atlas": str(FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH),
            "integration_registry": str(QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH),
            "transition_notes_json": str(AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH),
            "transition_notes_markdown": str(AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH),
        },
        "bundle_status": [
            {
                "pass": CURRENT_CARRIED_WITNESS,
                "truth": "OK",
                "status": "CARRIED_WITNESS",
            },
            {
                "pass": ACTIVE_LOCAL_SUBFRONT,
                "truth": "OK",
                "status": "CLOSED_HALL_LOCAL_BUNDLE",
            },
            {
                "pass": DEEPER_RECEIVING_FRONTIER,
                "truth": "OK",
                "status": "IMMEDIATE_DEEPER_RECEIVER",
            },
            {
                "pass": RESERVE_FRONTIER,
                "truth": "NEAR",
                "status": "RESERVE_ONLY",
            },
            {
                "pass": BLOCKED_EXTERNAL_FRONT,
                "truth": "FAIL",
                "status": "EXTERNAL_BLOCKER",
            },
            {
                "pass": CURRENT_PROGRAM,
                "truth": "NEAR",
                "status": "ACTIVE_INTEGRATION_LAYER",
            },
        ],
        "loop_law": "preserve QS64-20 as carried witness -> preserve QS64-24 as the closed Hall-local bundle -> keep TQ04 as immediate deeper handoff -> keep Q46 reserve-only -> keep Q02 external -> route the AP6D core-5 note layer through local witness only",
        "authoritative_current_receipt": str(AUTHORITATIVE_RECEIPT_PATH),
        "historical_receipts": [str(path) for path in HISTORICAL_RECEIPTS],
        "field_separation_law": {
            "front_id": "the umbrella Q42 frontier that stays open above the closed Hall-local bundle",
            "current_carried_witness": "the carried diagnose witness that remains visible after local refinement closes",
            "active_local_subfront": "the closed Hall-local NEXT^4 bundle marker rather than an active earlier Square pass",
            "next_hall_seed": "no new Hall-local seed is lawful; do not invent QS64-25",
            "next_temple_handoff": "the immediate deeper receiver that stays separate from Hall-local state",
            "reserve_frontier": "the reserve-only frontier outside the live QSHRINK closure lane",
            "blocked_external_front": "the still-blocked external Docs front that must remain explicit",
        },
        "agents": build_agents(),
    }


def render_plan(payload: dict) -> str:
    bundle_lines: list[str] = []
    for item in payload["bundle_status"]:
        bundle_lines.extend(
            [
                f"### `{item['pass']}`",
                "",
                f"- Status: `{item['status']}`",
                f"- Truth: `{item['truth']}`",
                "",
            ]
        )

    agent_lines: list[str] = []
    for agent in payload["agents"]:
        outputs = "; ".join(agent["expected_outputs"])
        agent_lines.extend(
            [
                f"### {agent['agent_id']} `{agent['skill']}`",
                "",
                f"- Status: `{agent['status']}`",
                f"- Bundle phase: `{agent['bundle_phase']}`",
                f"- Bundle role: `{agent['bundle_role']}`",
                f"- Skill truth: `{agent['truth']}`",
                f"- Role: {agent['role']}",
                f"- Expected outputs: {outputs}",
                "",
            ]
        )

    return "\n".join(
        [
            "# QSHRINK Looped Agentic Plan",
            "",
            "Date: `2026-03-13`",
            f"Truth: `{payload['truth']}`",
            f"Front ID: `{payload['front_id']}`",
            f"Hall frontier: `{payload['front_title']}`",
            f"Current carried witness: `{payload['current_carried_witness']}`",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{payload['next_hall_seed_display']}`",
            f"Deeper receiving frontier: `{payload['deeper_receiving_frontier']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Blocked external front: `{payload['blocked_external_front']}`",
            f"Current program: `{payload['current_program']}`",
            "Live Docs Gate: `BLOCKED` because `Trading Bot/credentials.json` and `Trading Bot/token.json` are missing.",
            "",
            "## Current Order",
            "",
            f"- `Q42` stays open while `{payload['current_carried_witness']}` remains the carried witness and `{payload['active_local_subfront']}` remains the closed Hall-local NEXT^4 bundle marker.",
            f"- `{payload['deeper_receiving_frontier']}` remains the immediate deeper receiver.",
            f"- `{payload['reserve_frontier']}` stays reserve-only and `{payload['blocked_external_front']}` stays externally blocked.",
            f"- `{payload['current_program']}` is the active integration layer above the closed bundle, not a replacement Hall-local seed.",
            "",
            "## Program Artifacts",
            "",
            f"- awakening source atlas: `{payload['program_artifacts']['awakening_source_atlas']}`",
            f"- integration registry: `{payload['program_artifacts']['integration_registry']}`",
            f"- transition notes json: `{payload['program_artifacts']['transition_notes_json']}`",
            f"- transition notes markdown: `{payload['program_artifacts']['transition_notes_markdown']}`",
            "",
            "## Bundle Status",
            "",
            *bundle_lines,
            "## Agent Matrix",
            "",
            *agent_lines,
            "## Authoritative Current Receipt",
            "",
            f"- `{payload['authoritative_current_receipt']}`",
            "",
            "## Historical Receipts",
            "",
            *[f"- `{path}`" for path in payload["historical_receipts"]],
            "",
            "## Field Separation Law",
            "",
            *[f"- {name.replace('_', ' ')}: {meaning}" for name, meaning in payload["field_separation_law"].items()],
            "",
        ]
    ) + "\n"


def render_capsule(payload: dict) -> str:
    return "\n".join(
        [
            "# QSHRINK Agent Sweep Contract",
            "",
            "Date: `2026-03-13`",
            f"Truth class: `{payload['truth']}`",
            f"Front ID: `{payload['front_id']}`",
            f"Current carried witness: `{payload['current_carried_witness']}`",
            f"Active local subfront: `{payload['active_local_subfront']}`",
            f"Next Hall seed: `{payload['next_hall_seed_display']}`",
            f"Deeper receiving frontier: `{payload['deeper_receiving_frontier']}`",
            f"Reserve frontier: `{payload['reserve_frontier']}`",
            f"Blocked external front: `{payload['blocked_external_front']}`",
            f"Current program: `{payload['current_program']}`",
            f"Docs gate: `{payload['docs_gate']['status']}`",
            "",
            "Q42 stays open as the umbrella frontier, QS64-20 remains the carried witness, QS64-24 remains the closed Hall-local bundle, TQ04 remains the immediate deeper receiver, Q46 stays reserve-only, Q02 stays blocked, and the AP6D core-5 transition-note layer rides above that split as a local-only assistive witness class.",
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(QSHRINK_AGENT_TASK_MATRIX_PATH, payload)
    OUTPUT_PLAN_PATH.write_text(render_plan(payload), encoding="utf-8")
    OUTPUT_CAPSULE_PATH.write_text(render_capsule(payload), encoding="utf-8")
    print(f"Wrote {QSHRINK_AGENT_TASK_MATRIX_PATH}")
    print(f"Wrote {OUTPUT_PLAN_PATH}")
    print(f"Wrote {OUTPUT_CAPSULE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
