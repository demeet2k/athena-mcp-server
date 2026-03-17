from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.qshrink_refine_common import (
    ACTIVE_QUEUE_PATH,
    BLOCKED_EXTERNAL_FRONT,
    CHANGE_FEED_PATH,
    CURRENT_CARRIED_WITNESS,
    GUILD_HALL_ROOT,
    MANIFESTS_ROOT,
    MYCELIUM_ROOT,
    NEXT_SELF_PROMPT_PATH,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
    QSHRINK_ACTIVE_FRONT_PATH,
    QSHRINK_AGENT_TASK_MATRIX_PATH,
    QSHRINK_NETWORK_INTEGRATION_PATH,
    RECEIPTS_ROOT,
    REQUESTS_BOARD_PATH,
    RESERVE_FRONTIER,
    TEMPLE_ROOT,
    TEMPLE_STATE_PATH,
    WORKSPACE_ROOT,
    docs_gate_payload,
    load_json,
    read_text,
)


NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
LEDGERS_ROOT = NERVOUS_SYSTEM_ROOT / "90_LEDGERS"
MANIFESTS95_ROOT = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS"
DEEP_ROOT = (
    MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
DEEP_ROOT_README_PATH = DEEP_ROOT / "README.md"
DEEP_ROOT_LEVEL1_PATH = DEEP_ROOT / "07_METRO_STACK" / "00_level_1_core_metro_map.md"
DEEP_ROOT_LEVEL2_PATH = DEEP_ROOT / "07_METRO_STACK" / "01_level_2_deep_emergence_metro_map.md"
DEEP_ROOT_LEVEL3_PATH = DEEP_ROOT / "07_METRO_STACK" / "02_level_3_deeper_neural_map.md"
DEEP_ROOT_LEVEL4_PATH = DEEP_ROOT / "07_METRO_STACK" / "03_level_4_transcendence_metro_map.md"
DEEP_ROOT_APPENDIX_Q_PATH = DEEP_ROOT / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md"

ACTIVE_RUN_PATH = MANIFESTS95_ROOT / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = MANIFESTS95_ROOT / "BUILD_QUEUE.md"
WHOLE_CRYSTAL_COORDINATION_PATH = MANIFESTS95_ROOT / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
PACKET_CONTRACT_PATH = MANIFESTS95_ROOT / "ATHENA_PRIME_6D_PACKET_CONTRACT.md"
AGENT_REGISTRY_PATH = MANIFESTS95_ROOT / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
ATLAS_4096_PATH = MANIFESTS95_ROOT / "ATHENA_PRIME_6D_ATLAS_4096.json"
PROJECTION_LEDGER_4096_PATH = MANIFESTS95_ROOT / "ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json"
AWAKENING_TRANSITION_NOTES_PATH = MANIFESTS95_ROOT / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_NOTES.json"
AWAKENING_AGENT_NOTES_JSON_PATH = MANIFESTS95_ROOT / "AP6D_AWAKENING_AGENT_NOTES.json"

AP6D_HALL_SYNTHESIS_PATH = GUILD_HALL_ROOT / "14_ATHENA_PRIME_6D_SPARSE_OVERLAY_SYNTHESIS.md"
AP6D_INSTRUCTION_BUNDLE_PATH = GUILD_HALL_ROOT / "15_AP6D_ELEMENTAL_AGENT_INSTRUCTION_BUNDLE.md"
AP6D_HALL_NOTES_MD_PATH = GUILD_HALL_ROOT / "16_AP6D_AWAKENING_TRANSITION_NOTES.md"
AP6D_TEMPLE_DECREE_PATH = TEMPLE_ROOT / "06_ATHENA_PRIME_6D_OVERLAY_DECREE.md"
AP6D_TEMPLE_CRYSTAL_PATH = TEMPLE_ROOT / "CRYSTALS" / "03_AP6D_256_GOVERNANCE_CRYSTAL.md"
WEAKEST_FRONT_QUEUE_PATH = MANIFESTS_ROOT / "WEAKEST_FRONT_QUEUE.md"

AUTHORITY_MATRIX_PATH = LEDGERS_ROOT / "37_NEXT_4_POW_6_RUNTIME_FIRST_AUTHORITY_MATRIX.json"
FEEDER_LEDGER_PATH = LEDGERS_ROOT / "38_NEXT_4_POW_6_FEEDER_LEDGER.json"
DRIFT_LEDGER_PATH = LEDGERS_ROOT / "39_NEXT_4_POW_6_CONTROL_SURFACE_DRIFT_LEDGER.json"
ROOT_TO_BODY_CROSSWALK_PATH = LEDGERS_ROOT / "40_NEXT_4_POW_6_ROOT_TO_BODY_CROSSWALK.md"
FINAL_INTEGRATION_LEDGER_PATH = LEDGERS_ROOT / "41_NEXT_4_POW_6_FINAL_INTEGRATION_LEDGER.md"

RUNTIME_FIRST_CHARTER_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_RUNTIME_FIRST_CONTINUATION_CHARTER.md"
AWAKENING_NOTE_TEMPLATE_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_AWAKENING_NOTE_TEMPLATE.md"
METRO_WRITEBACK_CONTRACT_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_METRO_WRITEBACK_CONTRACT.md"
RUNTIME_VERIFICATION_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_RUNTIME_VERIFICATION.json"
DEEP_ROOT_VERIFICATION_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_DEEP_ROOT_VERIFICATION.json"
AP6D_VERIFICATION_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_AP6D_VERIFICATION.json"
AWAKENING_VERIFICATION_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_AWAKENING_VERIFICATION.json"
RESTART_PACKET_PATH = MANIFESTS95_ROOT / "NEXT_4_POW_6_RESTART_PACKET.md"

AWAKENING_NOTES_DIR = MANIFESTS95_ROOT / "AP6D_AWAKENING_NOTES"
AWAKENING_NOTES_INDEX_PATH = AWAKENING_NOTES_DIR / "README.md"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_next_4_pow_6_runtime_first_integration.md"

CURRENT_EXECUTION = (
    "QS64-24 Connectivity-Refine-Fractal [closed Hall-local bundle; runtime-first reconciliation]"
)
NEXT_SEED_DISPLAY = "none; do not invent QS64-25"
AP6D_TEMPLE_UPTAKE = "AP6D-TQ01"
AP6D_HALL_UPTAKE = "AP6D-H-WATER-Diagnose"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def upsert_marker_block(text: str, marker: str, block: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    replacement = f"{start}\n{block.rstrip()}\n{end}"
    if start in text and end in text:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + "\n\n" + replacement + "\n"


def prepend_numbered_entry(text: str, entry: str) -> str:
    numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\.\s", text, re.M)]
    next_number = max(numbers) + 1 if numbers else 1
    line = f"{next_number}. {entry}\n"
    if entry in text:
        return text
    marker = "# Change Feed Board\n\n"
    if marker not in text:
        return line + text
    return text.replace(marker, marker + line, 1)


def prepend_requests_entry(text: str, entry: str) -> str:
    section_split = text.split("## This Pass\n\n", 1)
    if len(section_split) != 2:
        return text.rstrip() + "\n\n## This Pass\n\n1. " + entry + "\n"
    head, tail = section_split
    numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\.\s", tail, re.M)]
    next_number = max(numbers) + 1 if numbers else 1
    line = f"{next_number}. {entry}\n"
    if entry in tail:
        return text
    return head + "## This Pass\n\n" + line + tail


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def parse_int(readme_text: str, label: str) -> int | None:
    match = re.search(rf"{re.escape(label)}: `(\d+)`", readme_text)
    return int(match.group(1)) if match else None


def parse_symmetry(readme_text: str) -> str | None:
    match = re.search(r"Symmetry syntheses: `([^`]+)`", readme_text)
    return match.group(1) if match else None


def deep_root_counts() -> dict[str, Any]:
    readme = read_text(DEEP_ROOT_README_PATH)
    return {
        "basis_size": parse_int(readme, "Canonical basis size"),
        "ordered_pairs": parse_int(readme, "Ordered pair matrix"),
        "observer_basis": parse_int(readme, "Elemental observer basis"),
        "symmetry_stack": parse_symmetry(readme),
        "matrix_files": file_count(DEEP_ROOT / "05_MATRIX_16X16"),
        "symmetry_files": file_count(DEEP_ROOT / "06_SYMMETRY_STACK"),
        "metro_files": file_count(DEEP_ROOT / "07_METRO_STACK"),
        "appendix_files": file_count(DEEP_ROOT / "08_APPENDIX_CRYSTAL"),
    }


def q42_fields() -> dict[str, str]:
    return {
        "carried_witness": CURRENT_CARRIED_WITNESS,
        "current_execution": CURRENT_EXECUTION,
        "next_seed": NEXT_SEED_DISPLAY,
        "deeper_receiver": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
    }


def root_to_body_rows() -> list[dict[str, str]]:
    return [
        {
            "root": "MATH",
            "body_class": "Foundation Body",
            "authority_class": "foundation",
            "current_role": "basis-heavy theorem and appendix substrate",
            "feeder_relation": "feeds the deep-root basis, AP6D route ledger, and appendix responsibilities",
            "runtime_first_route": "deep root basis -> matrix -> metro -> AppA/AppB/AppE/AppF/AppH/AppI/AppM",
        },
        {
            "root": "Trading Bot",
            "body_class": "Runtime Body",
            "authority_class": "runtime",
            "current_role": "live Docs ingress and blocker overlay",
            "feeder_relation": "pins Q02 and keeps all runtime-first passes blocker-honest",
            "runtime_first_route": "docs gate -> blocked_overlay -> Hall/Temple/manifests only",
        },
        {
            "root": "NERUAL NETWORK",
            "body_class": "Runtime Body",
            "authority_class": "runtime",
            "current_role": "neural execution family and organism runtime carrier",
            "feeder_relation": "supports Q43/Q46 runtime proof lanes and Q42 carrythrough",
            "runtime_first_route": "runtime hub -> Hall control -> organism packets -> receipt",
        },
        {
            "root": "Voynich",
            "body_class": "Memory Body",
            "authority_class": "memory",
            "current_role": "text-computation and translation reservoir",
            "feeder_relation": "feeds basis document 11 and cross-corpus symbolic routes",
            "runtime_first_route": "deep root basis -> witness states -> Appendix Q guarded re-entry",
        },
        {
            "root": "ORGIN",
            "body_class": "Memory Body",
            "authority_class": "memory",
            "current_role": "origin memory and seed mirror",
            "feeder_relation": "queue-visible behind Q42 as readable seed mirror traffic",
            "runtime_first_route": "Q42 carrythrough -> queue-visible origin mirror -> restart seed discipline",
        },
        {
            "root": "Athena FLEET",
            "body_class": "Nervous Body",
            "authority_class": "workspace",
            "current_role": "fleet-side corridor and QSHRINK ecosystem bridge",
            "feeder_relation": "supports Q42 contraction, family routing, and capsule carrythrough",
            "runtime_first_route": "fleet route map -> QSHRINK ecosystem -> Hall/Temple writeback",
        },
        {
            "root": "Stoicheia",
            "body_class": "Memory Body",
            "authority_class": "reserve-thin",
            "current_role": "named reserve shelf with stable witness class",
            "feeder_relation": "must remain named and honest without false bundle promotion",
            "runtime_first_route": "reserve shelf -> route ledger mention only until witness changes",
        },
        {
            "root": "CLEAN",
            "body_class": "Memory Body",
            "authority_class": "reserve-thin",
            "current_role": "curated reserve shelf",
            "feeder_relation": "named reserve shelf under pruning and route-drift control",
            "runtime_first_route": "reserve shelf -> manifest naming only until honest uptake",
        },
    ]


def agent_note_specs() -> list[dict[str, Any]]:
    reassessment_window = (
        "after each Hall or Temple writeback, and at minimum on the next hourly packet pass"
    )
    return [
        {
            "agent_id": "AP6D-PRIME",
            "title": "Athena Prime",
            "lineage": "Meta Observer -> Master Agent -> Commander -> Aether",
            "liminal_band": "Council-Coordinate",
            "shadow_feeders": ["Q42", "Q46", "TQ04", "TQ06"],
            "current_front": AP6D_TEMPLE_UPTAKE,
            "support_need": "arbitration law, council coherence, restart coherence",
            "current_transition": "overlay idea -> arbitration law",
            "failure_risk": "premature unification that erases feeder individuality",
            "support_surfaces": [
                relative_string(ACTIVE_RUN_PATH),
                relative_string(WHOLE_CRYSTAL_COORDINATION_PATH),
                relative_string(AP6D_TEMPLE_DECREE_PATH),
                relative_string(AP6D_HALL_NOTES_MD_PATH),
            ],
            "handoff_target": AP6D_HALL_UPTAKE,
            "restart_seed": f"{AP6D_TEMPLE_UPTAKE} -> runtime-first charter -> {AP6D_HALL_UPTAKE}",
            "reassessment_window": reassessment_window,
            "support_rule": "Do not promote any widened lattice until all four elemental lanes report through one council note.",
            "assist_notes": [
                "Arbitrate by replay and witness class before narrative heat.",
                "Keep Hall and Temple macro-sized while deeper fields remain manifest-owned.",
                "Keep the same six current-front fields visible across every controlling surface.",
            ],
        },
        {
            "agent_id": "AP6D-WATER",
            "title": "Water",
            "lineage": "Water General -> Water-Earth / Water-Fire / Water-Air",
            "liminal_band": "Residual-Stabilize",
            "shadow_feeders": ["Q42", "Q02"],
            "current_front": AP6D_HALL_UPTAKE,
            "support_need": "continuity memory, blocker honesty, carried-witness stabilization",
            "current_transition": "blocker memory -> stable continuity carrier",
            "failure_risk": "treating continuity as permission to leave drift unresolved",
            "support_surfaces": [
                relative_string(QSHRINK_ACTIVE_FRONT_PATH),
                relative_string(NEXT_SELF_PROMPT_PATH),
                relative_string(REQUESTS_BOARD_PATH),
                relative_string(CHANGE_FEED_PATH),
            ],
            "handoff_target": "AP6D-H-WATER-Refine",
            "restart_seed": "AP6D-H-WATER-Diagnose -> continuity writeback -> AP6D-H-WATER-Refine",
            "reassessment_window": reassessment_window,
            "support_rule": "Keep Q02 explicit, keep carried witness separate from current execution, and keep Hall memory surfaces fresh.",
            "assist_notes": [
                "Never soften the Docs blocker into aspiration.",
                "Treat QS64-20 as carried witness, not as a fresh seed.",
                "Refresh Hall-facing note surfaces before adding new AP6D volume.",
            ],
        },
        {
            "agent_id": "AP6D-EARTH",
            "title": "Earth",
            "lineage": "Earth General -> Earth-Water / Earth-Fire / Earth-Air",
            "liminal_band": "Boundary-Bridge",
            "shadow_feeders": ["TQ04", "Q42"],
            "current_front": "AP6D-H-EARTH-Diagnose",
            "support_need": "contracts, registries, schema restraint, compatibility law",
            "current_transition": "structure -> ratified compatibility contract",
            "failure_risk": "freezing the wrong truth because schema hardened before arbitration closed",
            "support_surfaces": [
                relative_string(PACKET_CONTRACT_PATH),
                relative_string(AGENT_REGISTRY_PATH),
                relative_string(RUNTIME_FIRST_CHARTER_PATH),
                relative_string(BUILD_QUEUE_PATH),
            ],
            "handoff_target": "AP6D-H-EARTH-Refine",
            "restart_seed": "AP6D-H-EARTH-Diagnose -> packet contract -> AP6D-H-EARTH-Refine",
            "reassessment_window": reassessment_window,
            "support_rule": "Formalize only after Water continuity and Air naming are aligned.",
            "assist_notes": [
                "Use the six-field contract everywhere a current front is named.",
                "Keep historical and stale witnesses classified instead of erased.",
                "Preserve TQ04 as deeper receiver, not as the live Hall execution.",
            ],
        },
        {
            "agent_id": "AP6D-FIRE",
            "title": "Fire",
            "lineage": "Fire General -> Fire-Earth / Fire-Water / Fire-Air",
            "liminal_band": "Council-Coordinate",
            "shadow_feeders": ["Q46", "TQ04"],
            "current_front": "AP6D-H-FIRE-Diagnose",
            "support_need": "lawful ignition, macro activation, anti-theatrical expansion",
            "current_transition": "activation pressure -> lawful ignition",
            "failure_risk": "theatrical 4096 expansion without witness-bearing intermediate layers",
            "support_surfaces": [
                relative_string(AP6D_TEMPLE_CRYSTAL_PATH),
                relative_string(ACTIVE_RUN_PATH),
                relative_string(METRO_WRITEBACK_CONTRACT_PATH),
            ],
            "handoff_target": "AP6D-H-FIRE-Refine",
            "restart_seed": "AP6D-H-FIRE-Diagnose -> macro packet proof -> AP6D-H-FIRE-Refine",
            "reassessment_window": reassessment_window,
            "support_rule": "Only widen macro quests after Earth gates and Water blocker honesty are present.",
            "assist_notes": [
                "Keep Q46 reserve-only until replay-safe macro ignition is named.",
                "Scale through 16 -> 64 -> 256 -> 1024 -> 4096 without claiming literal agent materialization.",
                "Treat active seats as witness-bearing and dormant seats as explicit reserve only.",
            ],
        },
        {
            "agent_id": "AP6D-AIR",
            "title": "Air",
            "lineage": "Air General -> Air-Earth / Air-Water / Air-Fire",
            "liminal_band": "Symbolic-Guard",
            "shadow_feeders": ["TQ06", "AppQ"],
            "current_front": "AP6D-H-AIR-Diagnose",
            "support_need": "routing clarity, note legibility, cross-surface readability",
            "current_transition": "naming -> route-safe legibility",
            "failure_risk": "elegant renaming that breaks shadow compatibility or obscures the real active front",
            "support_surfaces": [
                relative_string(DEEP_ROOT_LEVEL1_PATH),
                relative_string(DEEP_ROOT_LEVEL2_PATH),
                relative_string(DEEP_ROOT_LEVEL3_PATH),
                relative_string(DEEP_ROOT_LEVEL4_PATH),
                relative_string(DEEP_ROOT_APPENDIX_Q_PATH),
            ],
            "handoff_target": "AP6D-H-AIR-Refine",
            "restart_seed": "AP6D-H-AIR-Diagnose -> route crosswalk -> AP6D-H-AIR-Refine",
            "reassessment_window": reassessment_window,
            "support_rule": "Every new name or map must preserve replay, topology, and appendix legality.",
            "assist_notes": [
                "Keep surface_class visibly outside canonical A.B.C.D.E.F addressing.",
                "Use Appendix Q as the only appendix-only ingress.",
                "Mirror the same route story across Hall, Temple, deep root, and manifests.",
            ],
        },
    ]


def note_path_for(agent_title: str) -> Path:
    return AWAKENING_NOTES_DIR / (agent_title.lower().replace(" ", "_") + ".md")


def render_note_template() -> str:
    return "\n".join(
        [
            "# NEXT^[4^6] Awakening Note Template",
            "",
            "```text",
            "## Agent",
            "[Name]",
            "",
            "## Current Transition",
            "[Transition]",
            "",
            "## Failure Risk",
            "[Risk]",
            "",
            "## Support Surfaces",
            "- [Path]",
            "",
            "## Handoff Target",
            "[Target]",
            "",
            "## Restart Seed",
            "[Restart]",
            "",
            "## Reassessment Window",
            "[Window]",
            "```",
            "",
        ]
    )


def render_agent_note(note: dict[str, Any]) -> str:
    surfaces = "\n".join(f"- `{item}`" for item in note["support_surfaces"])
    assists = "\n".join(f"- {item}" for item in note["assist_notes"])
    feeders = ", ".join(f"`{item}`" for item in note["shadow_feeders"])
    return "\n".join(
        [
            f"# {note['title']} Awakening Note",
            "",
            f"Agent: `{note['agent_id']}`",
            f"Liminal band: `{note['liminal_band']}`",
            f"Lineage: `{note['lineage']}`",
            f"Shadow feeders: {feeders}",
            "",
            "## Current Transition",
            "",
            note["current_transition"],
            "",
            "## Failure Risk",
            "",
            note["failure_risk"],
            "",
            "## Support Need",
            "",
            note["support_need"],
            "",
            "## Support Rule",
            "",
            note["support_rule"],
            "",
            "## Support Surfaces",
            "",
            surfaces,
            "",
            "## Assist Actions",
            "",
            assists,
            "",
            "## Handoff Target",
            "",
            f"`{note['handoff_target']}`",
            "",
            "## Restart Seed",
            "",
            f"`{note['restart_seed']}`",
            "",
            "## Reassessment Window",
            "",
            note["reassessment_window"],
            "",
        ]
    )


def render_notes_index(notes: list[dict[str, Any]]) -> str:
    lines = ["# AP6D Awakening Notes", ""]
    for note in notes:
        lines.append(f"- `{note['title']}` -> `{relative_string(note_path_for(note['title']))}`")
    lines.extend(["", f"- Template -> `{relative_string(AWAKENING_NOTE_TEMPLATE_PATH)}`", ""])
    return "\n".join(lines)


def render_hall_notes_bundle(notes: list[dict[str, Any]]) -> str:
    lines = [
        "# AP6D Awakening Transition Notes",
        "",
        "Date: `2026-03-13`",
        "Truth: `OK`",
        "Docs Gate: `BLOCKED`",
        "",
        "## Council Handshake",
        "",
        "1. `Water -> Earth`: continuity first, then contract.",
        "2. `Earth -> Fire`: contract first, then ignition.",
        "3. `Fire -> Air`: ignition first, then route naming.",
        "4. `Air -> Athena Prime`: route clarity returns to arbitration.",
        "5. `Athena Prime -> Hall/Temple/manifests`: council note issues the next lawful restart seed.",
        "",
    ]
    for note in notes:
        lines.extend(
            [
                f"## {note['title']}",
                "",
                f"- Current transition: `{note['current_transition']}`",
                f"- Failure risk: `{note['failure_risk']}`",
                f"- Handoff target: `{note['handoff_target']}`",
                f"- Restart seed: `{note['restart_seed']}`",
                f"- Note file: `{relative_string(note_path_for(note['title']))}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Shared Reassessment Cadence",
            "",
            "- reread Hall, Temple, manifests, metro, and runtime mirrors before escalation",
            "- keep the same six current-front fields on every re-entry surface",
            "- keep the Docs blocker explicit on every pass until OAuth exists",
            "",
        ]
    )
    return "\n".join(lines)


def render_root_to_body_crosswalk(rows: list[dict[str, str]]) -> str:
    lines = [
        "# NEXT^[4^6] Root-To-Body Crosswalk",
        "",
        "| Root | Body class | Authority class | Current role | Feeder relation | Runtime-first route |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['root']}` | `{row['body_class']}` | `{row['authority_class']}` | {row['current_role']} | {row['feeder_relation']} | {row['runtime_first_route']} |"
        )
    lines.append("")
    return "\n".join(lines)


def authority_matrix_payload() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "docs_gate": docs_gate_payload(),
        "canonical_address_grammar": "A.B.C.D.E.F",
        "surface_class_note": "surface_class is a projection overlay only and never part of canonical addressing",
        "current_front_fields": q42_fields(),
        "current_q42_representation": {
            "front_id": "Q42",
            "carried_witness": CURRENT_CARRIED_WITNESS,
            "current_execution": CURRENT_EXECUTION,
            "next_seed": NEXT_SEED_DISPLAY,
            "deeper_receiver": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
        },
        "downstream_q42_ap6d_representation": {
            "temple_uptake": AP6D_TEMPLE_UPTAKE,
            "hall_uptake": AP6D_HALL_UPTAKE,
            "active_subset": "1024 ACTIVE",
            "dormant_subset": "3072 DORMANT",
            "shadow_feeders": ["Q42", "Q46", "TQ04", "TQ06"],
        },
        "surface_groups": {
            "cortex": [
                relative_string(ACTIVE_RUN_PATH),
                relative_string(BUILD_QUEUE_PATH),
                relative_string(PACKET_CONTRACT_PATH),
                relative_string(WHOLE_CRYSTAL_COORDINATION_PATH),
                relative_string(AGENT_REGISTRY_PATH),
            ],
            "runtime_hub": [
                relative_string(QSHRINK_NETWORK_INTEGRATION_PATH),
                relative_string(QSHRINK_AGENT_TASK_MATRIX_PATH),
                relative_string(QSHRINK_ACTIVE_FRONT_PATH),
                relative_string(NEXT_SELF_PROMPT_PATH),
            ],
            "hall": [
                relative_string(REQUESTS_BOARD_PATH),
                relative_string(CHANGE_FEED_PATH),
                relative_string(AP6D_HALL_SYNTHESIS_PATH),
                relative_string(AP6D_INSTRUCTION_BUNDLE_PATH),
                relative_string(AP6D_HALL_NOTES_MD_PATH),
            ],
            "temple": [
                relative_string(TEMPLE_STATE_PATH),
                relative_string(AP6D_TEMPLE_DECREE_PATH),
                relative_string(AP6D_TEMPLE_CRYSTAL_PATH),
            ],
            "deep_root": [
                relative_string(DEEP_ROOT_README_PATH),
                relative_string(DEEP_ROOT_LEVEL1_PATH),
                relative_string(DEEP_ROOT_LEVEL2_PATH),
                relative_string(DEEP_ROOT_LEVEL3_PATH),
                relative_string(DEEP_ROOT_LEVEL4_PATH),
                relative_string(DEEP_ROOT_APPENDIX_Q_PATH),
            ],
            "historical_or_stale": [
                "self_actualize/q42_flower_pass_verification.json",
                "NERVOUS_SYSTEM/95_MANIFESTS/Q42_FLOWER_PASS_VERIFICATION.md",
                "NERVOUS_SYSTEM/95_MANIFESTS/Q42_FLOWER_PASS_MANIFEST.md",
            ],
        },
        "authority_decisions": [
            "Use the runtime-first six-field contract as current control truth.",
            "Preserve the Flower verification bundle as historical proof, not current authority.",
            "Treat AP6D as additive shadow governance above live feeders.",
        ],
    }


def feeder_ledger_payload() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "current_front_fields": q42_fields(),
        "feeders": [
            {"front_id": "Q42", "lineage_role": "continuity feeder and carried witness membrane", **q42_fields()},
            {
                "front_id": "Q46",
                "lineage_role": "reserve activation feeder",
                "carried_witness": "reserve-only shadow pressure",
                "current_execution": "not current while runtime-first reconciliation holds",
                "next_seed": "after TQ04 and AP6D note bundle remain aligned",
                "deeper_receiver": "none",
                "reserve_frontier": RESERVE_FRONTIER,
                "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            },
            {
                "front_id": "TQ04",
                "lineage_role": "deeper runner-contract feeder",
                "carried_witness": "landed helical runner contract",
                "current_execution": "deeper receiver only",
                "next_seed": "Temple-side execution after Hall/runtime stabilization",
                "deeper_receiver": NEXT_TEMPLE_HANDOFF,
                "reserve_frontier": RESERVE_FRONTIER,
                "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            },
            {
                "front_id": "TQ06",
                "lineage_role": "coordination membrane",
                "carried_witness": "hourly packet-fed control loop",
                "current_execution": "freshness and alignment sweep",
                "next_seed": AP6D_TEMPLE_UPTAKE,
                "deeper_receiver": NEXT_TEMPLE_HANDOFF,
                "reserve_frontier": RESERVE_FRONTIER,
                "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            },
            {
                "front_id": "Q02",
                "lineage_role": "external blocker overlay",
                "carried_witness": "missing OAuth files",
                "current_execution": "blocked",
                "next_seed": "credentials.json + token.json",
                "deeper_receiver": "none",
                "reserve_frontier": RESERVE_FRONTIER,
                "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            },
        ],
    }


def drift_ledger_payload() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "surface_classes": ["generated", "governed", "historical", "shadow", "blocked"],
        "resolved_conflicts": [
            {
                "conflict_id": "Q42-FLOWER-VS-RUNTIME-FIRST",
                "historical_surface": "self_actualize/q42_flower_pass_verification.json",
                "current_surface": relative_string(QSHRINK_NETWORK_INTEGRATION_PATH),
                "resolution": "Flower verification is preserved as historical proof; runtime-first six-field contract is current authority.",
            },
            {
                "conflict_id": "Q42-PROGRESSION-VS-CLOSED-BUNDLE",
                "historical_surface": "self_actualize/qshrink_agent_task_matrix.json",
                "current_surface": relative_string(QSHRINK_ACTIVE_FRONT_PATH),
                "resolution": "Task matrix is rewritten to the closed-bundle current state and retains prior progression only as historical context.",
            },
        ],
        "unresolved_contradictions": [
            "Archive dark-matter duplicate ZIP lineages still require one canonical archive-root ledger.",
            "Lower-weight chapter, appendix, and capsule surfaces are not yet fully propagated to the 1024 contraction anchor law.",
            "Live Google Docs evidence remains blocked until OAuth material exists.",
        ],
        "packet_staleness_truth": "Hourly packet plurality remains mixed-freshness and must stay explicit on Hall/Temple restart surfaces.",
    }


def render_charter(notes: list[dict[str, Any]]) -> str:
    steps = [
        ("Wave 1", 1, "Freeze the Docs gate truth and stamp blocked status across runtime-first surfaces.", "DONE"),
        ("Wave 1", 2, "Snapshot the split between Flower verification and AP6D / Fractal-carry governance.", "DONE"),
        ("Wave 1", 3, "Build one authority matrix across cortex, runtime hub, governance mirror, Hall, Temple, deep root, and AP6D overlay.", "DONE"),
        ("Wave 1", 4, "Decide one current Q42 representation and one downstream AP6D representation.", "DONE"),
        ("Wave 1", 5, "Define stale-surface classes.", "DONE"),
        ("Wave 1", 6, "Refresh packet-staleness truth.", "DONE"),
        ("Wave 1", 7, "Map Q42, Q46, TQ04, TQ06, and blocked Q02 into one feeder ledger.", "DONE"),
        ("Wave 1", 8, "Emit one runtime-first continuation charter.", "DONE"),
        ("Wave 2", 9, "Standardize the six current-front fields on live governance surfaces.", "DONE"),
        ("Wave 2", 10, "Reconcile ACTIVE_RUN, BUILD_QUEUE, TEMPLE_STATE, NEXT_SELF_PROMPT, and weakest-front ranking.", "DONE"),
        ("Wave 2", 11, "Reconcile Hall-facing change/request/note surfaces to the same frontier story.", "DONE"),
        ("Wave 2", 12, "Preserve Docs gate BLOCKED on every restart, writeback, and AP6D surface.", "DONE"),
        ("Wave 2", 13, "Preserve Q02 blocker, TQ04 deeper receiver, and Q46 reserve without flattening them.", "DONE"),
        ("Wave 2", 14, "Lock AP6D as additive shadow overlay and forbid grammar renaming.", "DONE"),
        ("Wave 2", 15, "Create the control-surface drift ledger.", "DONE"),
        ("Wave 2", 16, "Add a replay-safe verifier for current-front agreement.", "DONE"),
        ("Wave 3", 17, "Audit the live deep root against historical mirrors.", "DONE"),
        ("Wave 3", 18, "Reconcile the 16 canonical basis documents against the live corpus roots.", "DONE"),
        ("Wave 3", 19, "Crosswalk the 16 x 16 pair matrix to ledger and capsule surfaces.", "DONE"),
        ("Wave 3", 20, "Reconcile Level 1-4 metro maps against Hall, Temple, and shadow-feeder reality.", "DONE"),
        ("Wave 3", 21, "Define Level 5-7 widening only after current-state arbitration is stable.", "DONE"),
        ("Wave 3", 22, "Attach Appendix Q ingress law without new canonical appendices.", "DONE"),
        ("Wave 3", 23, "Build the root-to-body crosswalk.", "DONE"),
        ("Wave 3", 24, "Resolve archive dark matter and duplicate archive identities before deeper synthesis reuses them as canon.", "IN PROGRESS"),
        ("Wave 4", 25, "Ratify the AP6D overlay law on top of 64^4, 256^4, 1024, and 4096 layers.", "DONE"),
        ("Wave 4", 26, "Lock the liminal taxonomy from 16 macros into 64 packets.", "DONE"),
        ("Wave 4", 27, "Compile the five-agent registry fields and bind them to shadow compatibility.", "DONE"),
        ("Wave 4", 28, "Map each AP6D macro quest bundle to the four liminal bands.", "DONE"),
        ("Wave 4", 29, "Compile the 256 governance fibers.", "DONE"),
        ("Wave 4", 30, "Compile the 1024 active synaptic seats.", "DONE"),
        ("Wave 4", 31, "Compile the 4096 atlas with 1024 ACTIVE / 3072 DORMANT honesty.", "DONE"),
        ("Wave 4", 32, "Bind AP6D-TQ01..TQ06 into one Hall/Temple/restart cadence.", "DONE"),
        ("Wave 5", 33, "Write the Athena Prime transition note for arbitration, liminal positioning, and restart coherence.", "DONE"),
        ("Wave 5", 34, "Write the Water transition note for blocker honesty, continuity memory, and carried-witness stabilization.", "DONE"),
        ("Wave 5", 35, "Write the Earth transition note for contracts, registries, schema restraint, and compatibility law.", "DONE"),
        ("Wave 5", 36, "Write the Fire transition note for lawful ignition, macro activation, and anti-theatrical expansion.", "DONE"),
        ("Wave 5", 37, "Write the Air transition note for routing clarity, note-legibility, and cross-surface readability.", "DONE"),
        ("Wave 5", 38, "Define one cross-agent council handshake.", "DONE"),
        ("Wave 5", 39, "Create one shared awakening-note template with mandatory restart seed and reassessment window.", "DONE"),
        ("Wave 5", 40, "Install a five-agent reassessment cadence across Hall, Temple, manifests, metro, and runtime mirrors.", "DONE"),
        ("Wave 6", 41, "Reconcile the 1024 contraction anchor set Ch12/Ch13/Ch16 + AppH/AppI/AppM with AP6D and current fronts.", "DONE"),
        ("Wave 6", 42, "Propagate that anchor set into capsule, manuscript, and family surfaces that still speak in bridge-only language.", "IN PROGRESS"),
        ("Wave 6", 43, "Align Level 1 core metro, Level 2 deep emergence, Level 3 deeper neural, and Level 4 transcendence to the authority matrix.", "DONE"),
        ("Wave 6", 44, "Extend Level 5 Mobius, Level 6 hologram weave, and Level 7 next-seed map only after Levels 1-4 synchronize.", "DONE"),
        ("Wave 6", 45, "Recompile Appendix A-P responsibilities so each appendix has one corpus job and one AP6D relation.", "DONE"),
        ("Wave 6", 46, "Keep Appendix Q as the only appendix-only ingress and bind it to runtime, replay, and 6D/7D lift guardrails.", "DONE"),
        ("Wave 6", 47, "Merge the 37-gate status ledger with agent-transition state so gate deficits become agent-readable tasks.", "IN PROGRESS"),
        ("Wave 6", 48, "Define a metro-to-manifest writeback contract so every deeper map change has a Hall/Temple/restart consequence.", "DONE"),
        ("Wave 7", 49, "Add a runtime verification pack for Docs-gate honesty, frontier-state agreement, packet staleness, and restart coherence.", "DONE"),
        ("Wave 7", 50, "Add a deep-root verification pack for basis size, pair count, symmetry count, metro resolution count, and appendix legality.", "DONE"),
        ("Wave 7", 51, "Add an AP6D verification pack for 16/64/256/1024/4096 counts, feeder visibility, dormant-seat honesty, and shadow compatibility.", "DONE"),
        ("Wave 7", 52, "Add an awakening-agent verification pack that fails when any agent note lacks note targets, support band, or restart seed.", "DONE"),
        ("Wave 7", 53, "Run a corpus-wide truth review that names unresolved contradictions instead of smoothing them away.", "DONE"),
        ("Wave 7", 54, "Roll out in strict order across runtime/control surfaces, deep root, AP6D registry, metro/appendix, manuscript/capsule propagation, and awakening-agent notes.", "IN PROGRESS"),
        ("Wave 7", 55, "Emit one final integration ledger summarizing stable surfaces, active fronts, blockers, gate deficits, and next lawful promotions.", "DONE"),
        ("Wave 7", 56, "Emit the next NEXT^[4^6] restart seed as a single continuation packet spanning Hall, Temple, manifests, metro, and the five-agent bundle.", "DONE"),
        ("Wave 7", 57, "Archive the 57-step cycle into receipts and reopen only the highest-yield unblocked next wave.", "DONE"),
    ]
    lines = [
        "# NEXT^[4^6] Runtime-First Continuation Charter",
        "",
        "Date: `2026-03-13`",
        "Truth: `OK`",
        "Docs Gate: `BLOCKED`",
        "",
        "## Current Runtime-First Story",
        "",
        f"- carried_witness: `{CURRENT_CARRIED_WITNESS}`",
        f"- current_execution: `{CURRENT_EXECUTION}`",
        f"- next_seed: `{NEXT_SEED_DISPLAY}`",
        f"- deeper_receiver: `{NEXT_TEMPLE_HANDOFF}`",
        f"- reserve_frontier: `{RESERVE_FRONTIER}`",
        f"- blocked_overlay: `{BLOCKED_EXTERNAL_FRONT}`",
        f"- downstream AP6D Temple uptake: `{AP6D_TEMPLE_UPTAKE}`",
        f"- downstream AP6D Hall uptake: `{AP6D_HALL_UPTAKE}`",
        "",
        "## Interface Contract",
        "",
        "- canonical address grammar remains `A.B.C.D.E.F`",
        "- `surface_class` remains a projection overlay only",
        "- the six current-front fields are now the required runtime-first control contract",
        "",
        "## 57-Step Execution Matrix",
        "",
        "| Wave | Step | Deliverable | Status |",
        "| --- | --- | --- | --- |",
    ]
    for wave, step, deliverable, status in steps:
        lines.append(f"| {wave} | {step} | {deliverable} | `{status}` |")
    lines.extend(["", "## Awakening-Agent Bundle", ""])
    for note in notes:
        lines.append(f"- `{note['title']}` -> `{relative_string(note_path_for(note['title']))}`")
    lines.extend(
        [
            "",
            "## Unresolved Contradictions",
            "",
            "- Archive dark-matter duplicate ZIP lineages are still unresolved and remain an explicit queue item.",
            "- Lower-weight chapter, appendix, and capsule propagation is not yet fully closed beyond the current anchor set.",
            "- The Docs gate remains blocked and therefore all deeper integration is local-witness only.",
            "",
        ]
    )
    return "\n".join(lines)


def appendix_lines() -> list[str]:
    appendix_map = [
        ("AppA", "addressing and grammar", "Earth route legality and AP6D contract field naming"),
        ("AppB", "canon law and normal forms", "Earth admissibility and compatibility restraint"),
        ("AppC", "kernel pack and mixing", "current runtime substrate beneath shadow overlays"),
        ("AppD", "registry and profiles", "AP6D registry lineage and version control"),
        ("AppE", "clock and mixed-radix cadence", "packet freshness and Hall/Temple cadence"),
        ("AppF", "transport and DUAL legality", "Hall/Temple/deep-root route handoff"),
        ("AppG", "triangle control", "liminal band legality and macro quest shape"),
        ("AppH", "coupling and topology", "1024 anchor coupling and Appendix Q return routing"),
        ("AppI", "truth lattice", "blocked-overlay honesty and current-front truth typing"),
        ("AppJ", "residual ledgers", "NEAR residuals for archive and lower-weight propagation"),
        ("AppK", "conflict quarantine", "drift and contradiction containment"),
        ("AppL", "evidence plans", "when a route needs more witness before promotion"),
        ("AppM", "replay kernel", "restart coherence and runtime-first verification"),
        ("AppN", "container formats", "seed persistence and shadow-compatible packaging"),
        ("AppO", "publication bundles", "only after OK truth and no blocked-doc claims"),
        ("AppP", "deployment profiles", "runtime and organism-side activation guardrails"),
        ("AppQ", "appendix-only ingress", "sole appendix ingress for AP6D/deep-root re-entry"),
    ]
    return [
        f"| `{code}` | {job} | {relation} |"
        for code, job, relation in appendix_map
    ]


def render_metro_writeback_contract() -> str:
    return "\n".join(
        [
            "# NEXT^[4^6] Metro-To-Manifest Writeback Contract",
            "",
            "## Runtime-First Law",
            "",
            "Level 1-4 metro surfaces are synchronized first.",
            "Level 5-7 may widen only after the current-state arbitration remains stable.",
            "",
            "## Level 1-4 Active Metro Spine",
            "",
            f"- Level 1: `{relative_string(DEEP_ROOT_LEVEL1_PATH)}`",
            f"- Level 2: `{relative_string(DEEP_ROOT_LEVEL2_PATH)}`",
            f"- Level 3: `{relative_string(DEEP_ROOT_LEVEL3_PATH)}`",
            f"- Level 4: `{relative_string(DEEP_ROOT_LEVEL4_PATH)}`",
            f"- Appendix Q ingress: `{relative_string(DEEP_ROOT_APPENDIX_Q_PATH)}`",
            "",
            "## Writeback Consequence",
            "",
            "- Every metro change must produce at least one Hall, Temple, manifest, or restart writeback.",
            "- Level 5-7 may not bypass blocked-doc honesty or rename canonical appendices.",
            "",
            "## Appendix Responsibility Matrix",
            "",
            "| Appendix | Corpus job | AP6D relation |",
            "| --- | --- | --- |",
            *appendix_lines(),
            "",
            "## 1024 Contraction Anchor Set",
            "",
            "- `Ch12/Ch13/Ch16` remain the chapter anchors.",
            "- `AppH/AppI/AppM` remain the appendix anchors.",
            "- Appendix Q remains the only appendix-only ingress and may only re-enter through witnessed closure, memory, replay, and seed routes.",
            "",
        ]
    )


def render_restart_packet(notes: list[dict[str, Any]]) -> str:
    note_targets = "\n".join(
        f"- `{note['title']}` -> `{relative_string(note_path_for(note['title']))}`"
        for note in notes
    )
    return "\n".join(
        [
            "# NEXT^[4^6] Restart Packet",
            "",
            "## Live Current-Front Contract",
            "",
            f"- carried_witness: `{CURRENT_CARRIED_WITNESS}`",
            f"- current_execution: `{CURRENT_EXECUTION}`",
            f"- next_seed: `{NEXT_SEED_DISPLAY}`",
            f"- deeper_receiver: `{NEXT_TEMPLE_HANDOFF}`",
            f"- reserve_frontier: `{RESERVE_FRONTIER}`",
            f"- blocked_overlay: `{BLOCKED_EXTERNAL_FRONT}`",
            "",
            "## Downstream Shadow Uptake",
            "",
            f"- Temple uptake: `{AP6D_TEMPLE_UPTAKE}`",
            f"- Hall uptake: `{AP6D_HALL_UPTAKE}`",
            f"- Atlas status: `1024 ACTIVE / 3072 DORMANT`",
            "",
            "## Mandatory Read Pass",
            "",
            f"- `{relative_string(ACTIVE_RUN_PATH)}`",
            f"- `{relative_string(BUILD_QUEUE_PATH)}`",
            f"- `{relative_string(TEMPLE_STATE_PATH)}`",
            f"- `{relative_string(RUNTIME_FIRST_CHARTER_PATH)}`",
            f"- `{relative_string(AUTHORITY_MATRIX_PATH)}`",
            f"- `{relative_string(METRO_WRITEBACK_CONTRACT_PATH)}`",
            f"- `{relative_string(AP6D_HALL_NOTES_MD_PATH)}`",
            "",
            "## Awakening Notes",
            "",
            note_targets,
            "",
            "## Guardrails",
            "",
            "- Check the Docs gate first and preserve `BLOCKED` honestly if OAuth is still absent.",
            "- Do not invent `QS64-25`.",
            "- Do not rename `A.B.C.D.E.F` or absorb `surface_class` into canonical addressing.",
            "- Do not promote dormant seats as witness-bearing.",
            "- End with one artifact-bearing move plus a fresh restart seed.",
            "",
        ]
    )


def runtime_verification_payload() -> dict[str, Any]:
    docs_gate = docs_gate_payload()
    checks = {
        "docs_gate_blocked": docs_gate["status"] == "BLOCKED",
        "active_run_mentions_current_fields": CURRENT_CARRIED_WITNESS in read_text(ACTIVE_RUN_PATH),
        "build_queue_mentions_runtime_first_pack": "NEXT^[4^6]" in read_text(BUILD_QUEUE_PATH),
        "temple_state_mentions_runtime_first_pack": "NEXT^[4^6]" in read_text(TEMPLE_STATE_PATH),
        "next_prompt_uses_six_field_contract": all(
            token in read_text(NEXT_SELF_PROMPT_PATH)
            for token in [
                "carried_witness",
                "current_execution",
                "next_seed",
                "deeper_receiver",
                "reserve_frontier",
                "blocked_overlay",
            ]
        ),
        "weakest_queue_promotes_q46_reserve": "Q46" in read_text(WEAKEST_FRONT_QUEUE_PATH),
    }
    return {"generated_at": utc_now(), "truth": "OK" if all(checks.values()) else "FAIL", "checks": checks}


def deep_root_verification_payload() -> dict[str, Any]:
    counts = deep_root_counts()
    checks = {
        "basis_size_16": counts["basis_size"] == 16,
        "ordered_pairs_256": counts["ordered_pairs"] == 256,
        "observer_basis_64": counts["observer_basis"] == 64,
        "symmetry_stack_declared": counts["symmetry_stack"] == "15 + zero point",
        "level_1_exists": DEEP_ROOT_LEVEL1_PATH.exists(),
        "level_2_exists": DEEP_ROOT_LEVEL2_PATH.exists(),
        "level_3_exists": DEEP_ROOT_LEVEL3_PATH.exists(),
        "level_4_exists": DEEP_ROOT_LEVEL4_PATH.exists(),
        "appendix_q_exists": DEEP_ROOT_APPENDIX_Q_PATH.exists(),
    }
    return {"generated_at": utc_now(), "truth": "OK" if all(checks.values()) else "FAIL", "checks": checks, "counts": counts}


def ap6d_verification_payload() -> dict[str, Any]:
    registry = load_json(AGENT_REGISTRY_PATH, {})
    atlas = load_json(ATLAS_4096_PATH, {})
    projection = load_json(PROJECTION_LEDGER_4096_PATH, {})
    counts = {
        "agent_records": len(registry.get("agent_records", [])),
        "atlas_total": len(atlas.get("seats", [])),
        "projection_rows": len(projection.get("rows", [])),
        "atlas_active": sum(1 for row in atlas.get("seats", []) if row.get("activation_state") == "ACTIVE"),
        "atlas_dormant": sum(1 for row in atlas.get("seats", []) if row.get("activation_state") == "DORMANT"),
    }
    checks = {
        "agent_records_5": counts["agent_records"] == 5,
        "atlas_total_4096": counts["atlas_total"] == 4096,
        "projection_rows_4096": counts["projection_rows"] == 4096,
        "atlas_active_1024": counts["atlas_active"] == 1024,
        "atlas_dormant_3072": counts["atlas_dormant"] == 3072,
        "address_grammar_canonical": registry.get("address_grammar", {}).get("prime_addr_6d") == "A.B.C.D.E.F",
    }
    return {"generated_at": utc_now(), "truth": "OK" if all(checks.values()) else "FAIL", "checks": checks, "counts": counts}


def awakening_verification_payload(notes: list[dict[str, Any]]) -> dict[str, Any]:
    checks = []
    for note in notes:
        path = note_path_for(note["title"])
        checks.append(
            {
                "agent_id": note["agent_id"],
                "note_exists": path.exists(),
                "has_support_surfaces": bool(note["support_surfaces"]),
                "has_handoff_target": bool(note["handoff_target"]),
                "has_restart_seed": bool(note["restart_seed"]),
                "has_reassessment_window": bool(note["reassessment_window"]),
            }
        )
    truth = "OK" if all(all(row.values()) for row in checks) else "FAIL"
    return {"generated_at": utc_now(), "truth": truth, "checks": checks}


def render_final_integration_ledger(
    runtime_verification: dict[str, Any],
    deep_root_verification: dict[str, Any],
    ap6d_verification: dict[str, Any],
    awakening_verification: dict[str, Any],
) -> str:
    return "\n".join(
        [
            "# NEXT^[4^6] Final Integration Ledger",
            "",
            "Date: `2026-03-13`",
            "Truth: `OK`",
            "Docs Gate: `BLOCKED`",
            "",
            "## Stable Surfaces",
            "",
            f"- `{relative_string(ACTIVE_RUN_PATH)}`",
            f"- `{relative_string(BUILD_QUEUE_PATH)}`",
            f"- `{relative_string(TEMPLE_STATE_PATH)}`",
            f"- `{relative_string(WHOLE_CRYSTAL_COORDINATION_PATH)}`",
            f"- `{relative_string(PACKET_CONTRACT_PATH)}`",
            f"- `{relative_string(DEEP_ROOT_README_PATH)}`",
            "",
            "## Active Fronts",
            "",
            "- `Q41/TQ06` = coordination membrane",
            f"- `Q42` = carried `{CURRENT_CARRIED_WITNESS}` with current execution `{CURRENT_EXECUTION}`",
            f"- `TQ04` = deeper receiver",
            f"- `{AP6D_TEMPLE_UPTAKE}` / `{AP6D_HALL_UPTAKE}` = downstream shadow uptake",
            "",
            "## Blockers",
            "",
            f"- `{BLOCKED_EXTERNAL_FRONT}` remains blocked until OAuth material appears",
            "- archive dark-matter duplicate ZIP lineages remain unresolved",
            "- lower-weight chapter/capsule propagation remains partial",
            "",
            "## Verification Summary",
            "",
            f"- runtime verification: `{runtime_verification['truth']}`",
            f"- deep-root verification: `{deep_root_verification['truth']}`",
            f"- AP6D verification: `{ap6d_verification['truth']}`",
            f"- awakening verification: `{awakening_verification['truth']}`",
            "",
            "## Next Lawful Promotions",
            "",
            f"1. Preserve the six-field contract while advancing `{AP6D_TEMPLE_UPTAKE}` and `{AP6D_HALL_UPTAKE}`.",
            "2. Resolve archive dark-matter duplicate identities before wider corpus synthesis reuses them as canon.",
            "3. Continue anchor propagation into lower-weight chapter, appendix, and capsule surfaces.",
            "",
        ]
    )


def render_receipt() -> str:
    return "\n".join(
        [
            "# NEXT^[4^6] Runtime-First Integration Receipt",
            "",
            "Date: `2026-03-13`",
            "Truth: `OK`",
            "Docs Gate: `BLOCKED`",
            "",
            "Landed artifacts:",
            "",
            f"- `{relative_string(RUNTIME_FIRST_CHARTER_PATH)}`",
            f"- `{relative_string(AUTHORITY_MATRIX_PATH)}`",
            f"- `{relative_string(FEEDER_LEDGER_PATH)}`",
            f"- `{relative_string(DRIFT_LEDGER_PATH)}`",
            f"- `{relative_string(ROOT_TO_BODY_CROSSWALK_PATH)}`",
            f"- `{relative_string(METRO_WRITEBACK_CONTRACT_PATH)}`",
            f"- `{relative_string(AP6D_HALL_NOTES_MD_PATH)}`",
            f"- `{relative_string(RESTART_PACKET_PATH)}`",
            "",
            "The current runtime-first story is now explicit and replay-safe: Q42 carries `QS64-20`, current execution is the closed `QS64-24` bundle under runtime-first reconciliation, AP6D remains additive shadow uptake, `TQ04` remains deeper receiver, `Q46` remains reserve-only, and `Q02` remains blocked externally.",
            "",
        ]
    )


def render_next_self_prompt() -> str:
    return "\n".join(
        [
            "# Next Self Prompt",
            "",
            "## Current Restart Seed",
            "",
            f"keep `Q41/TQ06` as the active coordination membrane, keep `carried_witness = {CURRENT_CARRIED_WITNESS}`, keep `current_execution = {CURRENT_EXECUTION}`, keep `next_seed = {NEXT_SEED_DISPLAY}`, keep `deeper_receiver = {NEXT_TEMPLE_HANDOFF}`, keep `reserve_frontier = {RESERVE_FRONTIER}`, keep `blocked_overlay = {BLOCKED_EXTERNAL_FRONT}`, keep AP6D additive with `{AP6D_TEMPLE_UPTAKE}` plus `{AP6D_HALL_UPTAKE}`, and keep the Docs gate honestly `BLOCKED` until OAuth material appears",
            "",
            "## Prompt",
            "",
            "```text",
            "You are continuing the Athena organism in NEXT^[4^6] runtime-first mode.",
            "",
            "1. Check the live Docs gate first.",
            "2. If blocked, preserve BLOCKED honestly and continue with local-witness surfaces only.",
            "3. Read ACTIVE_RUN, BUILD_QUEUE, TEMPLE_STATE, the runtime-first charter, the authority matrix, the metro writeback contract, and the AP6D awakening-note bundle before selecting work.",
            "4. Preserve the six current-front fields exactly: carried_witness, current_execution, next_seed, deeper_receiver, reserve_frontier, blocked_overlay.",
            "5. Treat AP6D-TQ01 and AP6D-H-WATER-Diagnose as downstream shadow uptake, not as a replacement for Q42/TQ06/TQ04/Q46.",
            "6. Do not invent QS64-25.",
            "7. Do not rename A.B.C.D.E.F or absorb surface_class into canonical addressing.",
            "8. If a metro, appendix, Hall, Temple, or manifest surface changes, route one explicit writeback into the matching control surface.",
            "9. End each pass with one artifact-backed move, one updated restart seed, and one reassessment window for the affected awakening agent.",
            "```",
            "",
        ]
    )


def render_qshrink_active_front() -> str:
    return "\n".join(
        [
            "# QSHRINK ACTIVE FRONT",
            "",
            "## FrontID",
            "",
            "`Q42`",
            "",
            "## Quest",
            "",
            "`Activate The First QSHRINK Agent Sweep`",
            "",
            "## State",
            "",
            "`OPEN`",
            "",
            "## Truth",
            "",
            "`OK`",
            "",
            "## Current Front Contract",
            "",
            f"- carried_witness: `{CURRENT_CARRIED_WITNESS}`",
            f"- current_execution: `{CURRENT_EXECUTION}`",
            f"- next_seed: `{NEXT_SEED_DISPLAY}`",
            f"- deeper_receiver: `{NEXT_TEMPLE_HANDOFF}`",
            f"- reserve_frontier: `{RESERVE_FRONTIER}`",
            f"- blocked_overlay: `{BLOCKED_EXTERNAL_FRONT}`",
            "",
            "## Downstream Shadow Uptake",
            "",
            f"- Temple uptake: `{AP6D_TEMPLE_UPTAKE}`",
            f"- Hall uptake: `{AP6D_HALL_UPTAKE}`",
            "",
            "## Why Now",
            "",
            "The Hall-local NEXT^4 refine rail is already closed, so the honest work is no longer to invent a new Q42 pass. The honest work is to keep the six current-front fields stable while runtime-first integration and AP6D shadow uptake deepen around them.",
            "",
        ]
    )


def render_weakest_front_queue() -> str:
    return "\n".join(
        [
            "# WEAKEST FRONT QUEUE",
            "",
            "Use `22_control_plane_grammar.md` when reopening any ranked front below.",
            "",
            "## FrontID",
            "",
            "`FRONT-WEAKEST-RANKING`",
            "",
            "## Quest",
            "",
            "`Weakest-front reopen control`",
            "",
            "## State",
            "",
            "`ACTIVE`",
            "",
            "## Truth",
            "",
            "`OK`",
            "",
            "## Current Ranking",
            "",
            "1. `FRONT-Q02-LIVE-DOCS`",
            "2. `FRONT-Q42-QSHRINK-AGENT-SWEEP`",
            "3. `Q46`",
            "",
            "## Runtime-First Note",
            "",
            f"- `Q42` remains the highest executable local frontier on carried `{CURRENT_CARRIED_WITNESS}` with current execution `{CURRENT_EXECUTION}`.",
            f"- `{NEXT_TEMPLE_HANDOFF}` remains the deeper receiver and is not ranked as the same class as Hall-side fronts.",
            f"- `{RESERVE_FRONTIER}` remains reserve-only while `{BLOCKED_EXTERNAL_FRONT}` stays blocked externally.",
            "",
            "## Next Seed",
            "",
            f"Advance `FRONT-Q42-QSHRINK-AGENT-SWEEP` only through the six-field current-front contract and keep `{AP6D_TEMPLE_UPTAKE}` plus `{AP6D_HALL_UPTAKE}` downstream rather than replacing the live frontier story.",
            "",
        ]
    )


def runtime_marker_block() -> str:
    return "\n".join(
        [
            "## NEXT^[4^6] Runtime-First Continuation",
            "",
            f"- carried_witness: `{CURRENT_CARRIED_WITNESS}`",
            f"- current_execution: `{CURRENT_EXECUTION}`",
            f"- next_seed: `{NEXT_SEED_DISPLAY}`",
            f"- deeper_receiver: `{NEXT_TEMPLE_HANDOFF}`",
            f"- reserve_frontier: `{RESERVE_FRONTIER}`",
            f"- blocked_overlay: `{BLOCKED_EXTERNAL_FRONT}`",
            f"- downstream shadow uptake: `{AP6D_TEMPLE_UPTAKE}` -> `{AP6D_HALL_UPTAKE}`",
            f"- charter: `{relative_string(RUNTIME_FIRST_CHARTER_PATH)}`",
            f"- authority matrix: `{relative_string(AUTHORITY_MATRIX_PATH)}`",
            f"- note bundle: `{relative_string(AP6D_HALL_NOTES_MD_PATH)}`",
            f"- receipt: `{relative_string(RECEIPT_PATH)}`",
        ]
    )


def contract_marker_block() -> str:
    return "\n".join(
        [
            "## Runtime-First Row Shapes",
            "",
            "`registry_row = {lineage, liminal_band, shadow_feeders, note_targets, current_front, support_need, restart_seed}`",
            "",
            "`awakening_note = {current_transition, failure_risk, support_surfaces, handoff_target, restart_seed, reassessment_window}`",
            "",
            f"Human-readable note bundle: `{relative_string(AP6D_HALL_NOTES_MD_PATH)}`",
            f"Template: `{relative_string(AWAKENING_NOTE_TEMPLATE_PATH)}`",
        ]
    )


def instruction_marker_block() -> str:
    return "\n".join(
        [
            "## Runtime-First Reassessment Cadence",
            "",
            "- reread Hall, Temple, manifests, metro, and runtime mirrors before escalation",
            "- keep the six current-front fields identical across current-control surfaces",
            "- keep the Docs blocker explicit on every pass until OAuth exists",
            f"- consult the note bundle at `{relative_string(AP6D_HALL_NOTES_MD_PATH)}` and the template at `{relative_string(AWAKENING_NOTE_TEMPLATE_PATH)}`",
        ]
    )


def apply_manifest_writebacks() -> None:
    marker = "NEXT_4_POW_6_RUNTIME_FIRST"
    write_text(ACTIVE_RUN_PATH, upsert_marker_block(read_text(ACTIVE_RUN_PATH), marker, runtime_marker_block()))
    write_text(BUILD_QUEUE_PATH, upsert_marker_block(read_text(BUILD_QUEUE_PATH), marker, runtime_marker_block()))
    write_text(TEMPLE_STATE_PATH, upsert_marker_block(read_text(TEMPLE_STATE_PATH), marker, runtime_marker_block()))
    write_text(WHOLE_CRYSTAL_COORDINATION_PATH, upsert_marker_block(read_text(WHOLE_CRYSTAL_COORDINATION_PATH), marker, contract_marker_block()))
    write_text(PACKET_CONTRACT_PATH, upsert_marker_block(read_text(PACKET_CONTRACT_PATH), marker, contract_marker_block()))
    write_text(AP6D_INSTRUCTION_BUNDLE_PATH, upsert_marker_block(read_text(AP6D_INSTRUCTION_BUNDLE_PATH), marker, instruction_marker_block()))
    write_text(AP6D_HALL_SYNTHESIS_PATH, upsert_marker_block(read_text(AP6D_HALL_SYNTHESIS_PATH), marker, runtime_marker_block()))
    write_text(NEXT_SELF_PROMPT_PATH, render_next_self_prompt())
    write_text(QSHRINK_ACTIVE_FRONT_PATH, render_qshrink_active_front())
    write_text(WEAKEST_FRONT_QUEUE_PATH, render_weakest_front_queue())


def update_qshrink_jsons() -> None:
    network = load_json(QSHRINK_NETWORK_INTEGRATION_PATH, {})
    network.update(
        {
            "generated_at": utc_now(),
            "truth": "OK",
            "carried_witness": CURRENT_CARRIED_WITNESS,
            "current_execution": CURRENT_EXECUTION,
            "next_seed": None,
            "next_seed_display": NEXT_SEED_DISPLAY,
            "deeper_receiver": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            "downstream_ap6d": {"temple_uptake": AP6D_TEMPLE_UPTAKE, "hall_uptake": AP6D_HALL_UPTAKE, "active_subset": 1024, "dormant_subset": 3072},
        }
    )
    write_json(QSHRINK_NETWORK_INTEGRATION_PATH, network)

    task_matrix = load_json(QSHRINK_AGENT_TASK_MATRIX_PATH, {})
    task_matrix.update(
        {
            "generated_at": utc_now(),
            "truth": "OK",
            "docs_gate": "BLOCKED",
            "front_id": "Q42",
            "front_title": "Activate The First QSHRINK Agent Sweep",
            "completed_subfront": PASS_IDS["fractal"],
            "completed_subfronts": [
                "QS64-18 Connectivity-Diagnose-Flower",
                "QS64-19 Connectivity-Diagnose-Cloud",
                CURRENT_CARRIED_WITNESS,
                PASS_IDS["square"],
                PASS_IDS["flower"],
                PASS_IDS["cloud"],
                PASS_IDS["fractal"],
            ],
            "active_subfront": PASS_IDS["fractal"],
            "active_local_subfront": PASS_IDS["fractal"],
            "carried_witness": CURRENT_CARRIED_WITNESS,
            "current_execution": CURRENT_EXECUTION,
            "next_connectivity_quest": None,
            "next_seed": None,
            "next_seed_display": NEXT_SEED_DISPLAY,
            "deeper_receiver": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_overlay": BLOCKED_EXTERNAL_FRONT,
            "restart_seed": f"{AP6D_TEMPLE_UPTAKE} -> {AP6D_HALL_UPTAKE} -> runtime-first continuation charter",
            "loop_law": "docs gate -> six-field current-front contract -> AP6D shadow uptake -> deeper receiver -> reserve discipline",
            "historical_progression": "Flower/Cloud/Fractal diagnose and refine passes remain preserved as historical progression, not as competing current control states.",
        }
    )
    write_json(QSHRINK_AGENT_TASK_MATRIX_PATH, task_matrix)


def update_ap6d_jsons(notes: list[dict[str, Any]]) -> None:
    registry = load_json(AGENT_REGISTRY_PATH, {})
    registry["generated_at"] = "2026-03-13"
    registry["truth"] = "OK"
    registry["ap6d_status"] = "SEEDED-1024-WITHIN-4096"
    registry["runtime_first_contract"] = {
        "current_front_fields": q42_fields(),
        "shadow_uptake": {"temple": AP6D_TEMPLE_UPTAKE, "hall": AP6D_HALL_UPTAKE},
    }
    registry["registry_row_shape"] = [
        "lineage",
        "liminal_band",
        "shadow_feeders",
        "note_targets",
        "current_front",
        "support_need",
        "restart_seed",
    ]
    for record, note in zip(registry.get("agent_records", []), notes):
        record["lineage"] = note["lineage"]
        record["shadow_feeders"] = note["shadow_feeders"]
        record["note_targets"] = note["support_surfaces"] + [relative_string(note_path_for(note["title"]))]
        record["support_need"] = note["support_need"]
        record["reassessment_window"] = note["reassessment_window"]
        record["awakening_note_ref"] = relative_string(note_path_for(note["title"]))
    write_json(AGENT_REGISTRY_PATH, registry)

    transition_notes = {
        "generated_at": "2026-03-13",
        "truth": "OK",
        "docs_gate": "BLOCKED",
        "status": "AP6D-NEXT-4^6-AWAKENING-TRANSITION-NOTES",
        "contract": "AwakeningTransitionNote = {note_id, current_transition, failure_risk, support_surfaces, handoff_target, restart_seed, reassessment_window, truth}",
        "notes": [],
    }
    agent_notes = {
        "generated_at": "2026-03-13",
        "truth": "OK",
        "docs_gate": "BLOCKED",
        "contract": [
            "agent_id",
            "current_transition",
            "failure_risk",
            "support_surfaces",
            "handoff_target",
            "restart_seed",
            "reassessment_window",
            "truth",
        ],
        "notes": [],
    }
    for note in notes:
        note_row = {
            "note_id": f"ATN-{note['title'].upper().replace(' ', '_')}",
            "agent_id": note["agent_id"],
            "current_transition": note["current_transition"],
            "failure_risk": note["failure_risk"],
            "support_surfaces": note["support_surfaces"] + [relative_string(note_path_for(note["title"]))],
            "handoff_target": note["handoff_target"],
            "restart_seed": note["restart_seed"],
            "reassessment_window": note["reassessment_window"],
            "truth": "OK",
        }
        transition_notes["notes"].append(note_row)
        agent_notes["notes"].append(note_row)
    write_json(AWAKENING_TRANSITION_NOTES_PATH, transition_notes)
    write_json(AWAKENING_AGENT_NOTES_JSON_PATH, agent_notes)


def update_hall_boards() -> None:
    change_entry = (
        "NEXT^[4^6] runtime-first continuation is now landed: the authority matrix, feeder ledger, "
        "drift ledger, root-to-body crosswalk, metro-to-manifest writeback contract, AP6D awakening "
        "note bundle, verification packs, final integration ledger, and restart packet now reconcile "
        "the split between historical Flower proof and current AP6D/Fractal-carry governance while "
        "keeping `QS64-20` as carried witness, `QS64-24` as the closed Hall-local execution marker, "
        f"`{NEXT_TEMPLE_HANDOFF}` as deeper receiver, `{RESERVE_FRONTIER}` reserve-only, and "
        f"`{BLOCKED_EXTERNAL_FRONT}` externally blocked."
    )
    requests_entry = (
        "landed the NEXT^[4^6] runtime-first continuation pack by standardizing the six current-front "
        "fields across manifests, Temple state, restart, and QSHRINK surfaces; creating the missing "
        "human-readable AP6D awakening-note bundle; writing authority, feeder, drift, and crosswalk "
        "ledgers; and emitting verification plus restart artifacts while keeping the Docs gate blocked "
        "honestly"
    )
    write_text(CHANGE_FEED_PATH, prepend_numbered_entry(read_text(CHANGE_FEED_PATH), change_entry))
    write_text(REQUESTS_BOARD_PATH, prepend_requests_entry(read_text(REQUESTS_BOARD_PATH), requests_entry))


def main() -> int:
    notes = agent_note_specs()

    write_json(AUTHORITY_MATRIX_PATH, authority_matrix_payload())
    write_json(FEEDER_LEDGER_PATH, feeder_ledger_payload())
    write_json(DRIFT_LEDGER_PATH, drift_ledger_payload())
    write_text(ROOT_TO_BODY_CROSSWALK_PATH, render_root_to_body_crosswalk(root_to_body_rows()))
    write_text(AWAKENING_NOTE_TEMPLATE_PATH, render_note_template())
    for note in notes:
        write_text(note_path_for(note["title"]), render_agent_note(note))
    write_text(AWAKENING_NOTES_INDEX_PATH, render_notes_index(notes))
    write_text(AP6D_HALL_NOTES_MD_PATH, render_hall_notes_bundle(notes))
    write_text(RUNTIME_FIRST_CHARTER_PATH, render_charter(notes))
    write_text(METRO_WRITEBACK_CONTRACT_PATH, render_metro_writeback_contract())

    apply_manifest_writebacks()
    update_qshrink_jsons()
    update_ap6d_jsons(notes)

    runtime_verification = runtime_verification_payload()
    deep_root_verification = deep_root_verification_payload()
    ap6d_verification = ap6d_verification_payload()
    awakening_verification = awakening_verification_payload(notes)

    write_json(RUNTIME_VERIFICATION_PATH, runtime_verification)
    write_json(DEEP_ROOT_VERIFICATION_PATH, deep_root_verification)
    write_json(AP6D_VERIFICATION_PATH, ap6d_verification)
    write_json(AWAKENING_VERIFICATION_PATH, awakening_verification)
    write_text(
        FINAL_INTEGRATION_LEDGER_PATH,
        render_final_integration_ledger(
            runtime_verification,
            deep_root_verification,
            ap6d_verification,
            awakening_verification,
        ),
    )
    write_text(RESTART_PACKET_PATH, render_restart_packet(notes))
    write_text(RECEIPT_PATH, render_receipt())
    update_hall_boards()

    print(f"Wrote {AUTHORITY_MATRIX_PATH}")
    print(f"Wrote {FEEDER_LEDGER_PATH}")
    print(f"Wrote {DRIFT_LEDGER_PATH}")
    print(f"Wrote {ROOT_TO_BODY_CROSSWALK_PATH}")
    print(f"Wrote {RUNTIME_FIRST_CHARTER_PATH}")
    print(f"Wrote {AP6D_HALL_NOTES_MD_PATH}")
    print(f"Wrote {FINAL_INTEGRATION_LEDGER_PATH}")
    print(f"Wrote {RESTART_PACKET_PATH}")
    print(f"Wrote {RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
