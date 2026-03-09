from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "framework" / "registry" / "folio_sequence.json"
MASTER_JSON_PATH = ROOT / "framework" / "registry" / "autonomous_master_plan.json"
MASTER_MD_PATH = ROOT / "manifests" / "AUTONOMOUS_MASTER_PLAN.md"
TERMINATION_MD_PATH = ROOT / "manifests" / "AUTONOMOUS_TERMINATION_CONTRACT.md"

FOLIO_PHASES = [
    "Phase 1: Intake",
    "Phase 2: Scaffold",
    "Phase 3: Direct Evidence",
    "Phase 4: Visual Pass",
    "Phase 5: Multilens Rendering",
    "Phase 6: Formal Compilation",
    "Phase 7: Synthesis",
    "Phase 8: Audit",
    "Phase 9: Corpus Roll-Up",
    "Phase 10: Autonomous Self-Handoff",
]

SECTION_PHASES = [
    "Phase S1: Section Synthesis Consolidation",
    "Phase S2: Crystal Completion",
    "Phase S3: Section Metro Map",
    "Phase S4: Emergent Metro Map",
    "Phase S5: Full-Crystal Propagation",
    "Phase S6: Autonomous Self-Handoff",
]

TERMINAL_PHASES = [
    "Phase T1: Final Section Sweep",
    "Phase T2: Full Crystal Completion",
    "Phase T3: Authorial Final Line",
    "Phase T4: Master Manuscript Finalization",
    "Phase T5: Giant Manuscript Packaging",
    "Phase T6: Terminal State Write",
]

FOLIO_OUTPUTS = [
    "folios/{folio}_FINAL_DRAFT.md",
    "folios/{folio}.md",
    "unified/VOYNICH_FULL_TRANSLATION.md",
    "{section}",
    "{crystal}",
    "metro/VOYNICH_METRO_MAP_WORKING.md",
    "manifests/CORPUS_BUILD_STATUS.md",
    "unified/VOYNICH_MASTER_MANUSCRIPT.md",
    "manifests/AUTONOMOUS_CURSOR.md",
    "manifests/AUTONOMOUS_QUEUE.md",
    "manifests/NEXT_FOLIO_SELF_PROMPT.md",
    "manifests/ACTIVE_MICRO_PLAN.md",
    "manifests/ACTIVE_RUN_TASK_LIST.md",
    "manifests/PARALLEL_AGENT_QUEUE.md",
]

SECTION_OUTPUTS = [
    "{section}",
    "{crystal}",
    "crystals/VOYNICH_FULL_CRYSTAL.md",
    "metro/VOYNICH_METRO_MAP_WORKING.md",
    "manifests/CORPUS_BUILD_STATUS.md",
    "unified/VOYNICH_MASTER_MANUSCRIPT.md",
    "manifests/AUTONOMOUS_CURSOR.md",
    "manifests/AUTONOMOUS_QUEUE.md",
    "manifests/NEXT_FOLIO_SELF_PROMPT.md",
    "manifests/ACTIVE_MICRO_PLAN.md",
    "manifests/ACTIVE_RUN_TASK_LIST.md",
    "manifests/PARALLEL_AGENT_QUEUE.md",
]

TERMINAL_OUTPUTS = [
    "sections/FULL_PLANT.md",
    "sections/FULL_ASTROLOGY.md",
    "sections/FULL_BATH.md",
    "sections/PHARMACEUTICAL_1_FULL.md",
    "sections/PHARMACEUTICAL_1_SYNTHESIS.md",
    "sections/PHARMACEUTICAL_2_FULL.md",
    "sections/PHARMACEUTICAL_2_SYNTHESIS.md",
    "sections/PHARMACEUTICAL_1_2_SYNTHESIS.md",
    "crystals/PLANT_CRYSTAL.md",
    "crystals/ASTROLOGY_CRYSTAL.md",
    "crystals/BATH_CRYSTAL.md",
    "crystals/PHARMACEUTICAL_1_CRYSTAL.md",
    "crystals/PHARMACEUTICAL_2_CRYSTAL.md",
    "crystals/VOYNICH_FULL_CRYSTAL.md",
    "unified/VOYNICH_MASTER_MANUSCRIPT.md",
    "unified/VOYNICH_GIANT_MANUSCRIPT.md",
    "manifests/ACTIVE_MICRO_PLAN.md",
]

FINAL_TERMINAL_ACTIONS = [
    "finalize every section synthesis crystal with synthesis, metro map, and emergent metro map",
    "finalize crystals/VOYNICH_FULL_CRYSTAL.md",
    "append the author's final line after 116r",
    "finalize unified/VOYNICH_MASTER_MANUSCRIPT.md",
    "finalize unified/VOYNICH_GIANT_MANUSCRIPT.md",
    "write terminal completion state into manifests/ACTIVE_MICRO_PLAN.md",
    "stop the agent when no master-plan steps remain",
]


def load_registry() -> list[dict[str, object]]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return list(data["folios"])


def group_books(folios: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for entry in folios:
        if current is None or entry["book"] != current["book"]:
            if current is not None:
                groups.append(current)
            current = {
                "book": entry["book"],
                "start": entry["folio"],
                "end": entry["folio"],
                "section": entry["section"],
                "crystal": entry["crystal"],
                "folios": [entry["folio"]],
            }
        else:
            current["end"] = entry["folio"]
            current["folios"].append(entry["folio"])
    if current is not None:
        groups.append(current)
    return groups


def build_gap_windows(folios: list[dict[str, object]]) -> list[dict[str, object]]:
    ids = [entry["folio"] for entry in folios]
    gaps: list[dict[str, object]] = []
    if "F084V" in ids and "F087R" in ids:
        gaps.append(
            {
                "label": "Reserved Book IV / Cosmology gap in current canonical registry",
                "after": "F084V",
                "before": "F087R",
                "missing_window": ["F085R", "F085V", "F086R", "F086V"],
                "rule": "Do not invent absent folios. Hold the gap explicitly until a canonical local witness is added.",
            }
        )
    return gaps


def format_outputs(templates: list[str], folio: str | None, section: str | None, crystal: str | None) -> list[str]:
    out = []
    for template in templates:
        out.append(template.format(folio=folio or "", section=section or "", crystal=crystal or ""))
    return out


def make_folio_step(entry: dict[str, object]) -> dict[str, object]:
    folio = str(entry["folio"])
    return {
        "kind": "folio",
        "folio": folio,
        "title": f"{folio} final draft",
        "book": entry["book"],
        "section": entry["section"],
        "crystal": entry["crystal"],
        "phases": FOLIO_PHASES,
        "outputs": format_outputs(FOLIO_OUTPUTS, folio, str(entry["section"]), str(entry["crystal"])),
    }


def make_section_step(group: dict[str, object]) -> dict[str, object]:
    suffix = str(group["end"])
    return {
        "kind": "section_completion",
        "folio": None,
        "title": f"{group['book']} synthesis and crystal completion",
        "book": group["book"],
        "section": group["section"],
        "crystal": group["crystal"],
        "trigger_after": suffix,
        "phases": SECTION_PHASES,
        "outputs": format_outputs(SECTION_OUTPUTS, None, str(group["section"]), str(group["crystal"])),
        "actions": [
            f"finalize {group['section']}",
            f"finalize {group['crystal']}",
            f"write section synthesis, metro map, and emergent metro map into {group['crystal']}",
            "propagate the section-level delta into crystals/VOYNICH_FULL_CRYSTAL.md",
        ],
    }


def make_terminal_step(last_folio: str) -> dict[str, object]:
    return {
        "kind": "terminal_completion",
        "folio": None,
        "title": "Manuscript terminal completion",
        "book": "Manuscript Complete",
        "section": "unified/VOYNICH_FULL_TRANSLATION.md",
        "crystal": "crystals/VOYNICH_FULL_CRYSTAL.md",
        "trigger_after": last_folio,
        "phases": TERMINAL_PHASES,
        "outputs": TERMINAL_OUTPUTS,
        "actions": FINAL_TERMINAL_ACTIONS,
    }


def finalize_steps(raw_steps: list[dict[str, object]]) -> list[dict[str, object]]:
    steps: list[dict[str, object]] = []
    total = len(raw_steps)
    for index, step in enumerate(raw_steps, start=1):
        step_id = f"MACRO_{index:03d}"
        if step["kind"] == "folio":
            step_id += f"_{step['folio']}"
        elif step["kind"] == "section_completion":
            step_id += "_SECTION_SYNTHESIS"
        else:
            step_id += "_MANUSCRIPT_TERMINUS"

        current = dict(step)
        current["step_number"] = index
        current["step_id"] = step_id
        current["previous_step_id"] = steps[-1]["step_id"] if steps else None
        current["next_step_id"] = None
        current["macro_step_count"] = total
        steps.append(current)

    for left, right in zip(steps, steps[1:]):
        left["next_step_id"] = right["step_id"]
    return steps


def build_steps(folios: list[dict[str, object]], books: list[dict[str, object]]) -> list[dict[str, object]]:
    last_by_book = {group["end"]: group for group in books}
    raw_steps: list[dict[str, object]] = []
    for entry in folios:
        raw_steps.append(make_folio_step(entry))
        if entry["folio"] in last_by_book:
            raw_steps.append(make_section_step(last_by_book[entry["folio"]]))
    raw_steps.append(make_terminal_step(str(folios[-1]["folio"])))
    return finalize_steps(raw_steps)


def build_master_plan() -> dict[str, object]:
    folios = load_registry()
    books = group_books(folios)
    macro_steps = build_steps(folios, books)
    folio_steps = [step for step in macro_steps if step["kind"] == "folio"]
    milestone_steps = [step for step in macro_steps if step["kind"] != "folio"]
    return {
        "version": "2.0.0",
        "source_registry": str(REGISTRY_PATH),
        "folio_count": len(folios),
        "macro_step_count": len(macro_steps),
        "books": books,
        "gap_windows": build_gap_windows(folios),
        "folio_phases": FOLIO_PHASES,
        "macro_steps": macro_steps,
        "work_items": folio_steps,
        "milestones": milestone_steps,
        "terminal_actions": FINAL_TERMINAL_ACTIONS,
    }


def render_master_markdown(plan: dict[str, object]) -> str:
    lines: list[str] = [
        "# Autonomous Master Plan",
        "",
        "## Control Architecture",
        "",
        "This is the canonical macro plan for the full no-stop Voynich manuscript build.",
        "",
        f"- folio work items: `{plan['folio_count']}`",
        f"- macro steps total: `{plan['macro_step_count']}`",
        "",
        "Control law:",
        "",
        "1. the macro plan owns the full manuscript-order step ledger",
        "2. the runtime emits one active micro plan from the active macro step",
        "3. the penultimate micro step hands off to the next macro step",
        "4. the final micro step performs successor intake and must not be interpreted as completion",
        "5. every active macro step also emits a five-task run list whose fifth task reboots the cycle by reading the rewritten successor list",
        "6. every active macro step also emits a parallel lane queue so the current folio, immediate successor, and preheated follow-on lane remain staged together",
        "7. when no macro steps remain, the runtime emits the terminal completion micro plan and stops only because no successor step exists",
        "",
        "## Canonical Runtime Files",
        "",
        "- `framework/registry/autonomous_master_plan.json`",
        "- `manifests/AUTONOMOUS_MASTER_PLAN.md`",
        "- `manifests/ACTIVE_MICRO_PLAN.md`",
        "- `manifests/ACTIVE_RUN_TASK_LIST.md`",
        "- `manifests/PARALLEL_AGENT_QUEUE.md`",
        "- `manifests/AUTONOMOUS_CURSOR.md`",
        "- `manifests/AUTONOMOUS_QUEUE.md`",
        "- `manifests/NEXT_FOLIO_SELF_PROMPT.md`",
        "- `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md`",
        "",
        "## Book Spans",
        "",
        "| Book | Start | End | Section | Crystal |",
        "| --- | --- | --- | --- | --- |",
    ]
    for group in plan["books"]:
        lines.append(f"| {group['book']} | `{group['start']}` | `{group['end']}` | `{group['section']}` | `{group['crystal']}` |")

    if plan["gap_windows"]:
        lines += ["", "## Reserved Gap Windows", ""]
        for gap in plan["gap_windows"]:
            missing = ", ".join(f"`{folio}`" for folio in gap["missing_window"])
            lines += [
                f"### {gap['label']}",
                "",
                f"- gap window: {missing}",
                f"- placement: after `{gap['after']}` and before `{gap['before']}`",
                f"- rule: {gap['rule']}",
                "",
            ]

    lines += ["## Macro Step Ledger", ""]
    for step in plan["macro_steps"]:
        target = step["folio"] or step["title"]
        lines.append(
            f"{step['step_number']}. `{step['step_id']}` | kind: `{step['kind']}` | target: `{target}` | next: `{step['next_step_id'] or 'STOP'}`"
        )

    return "\n".join(lines).rstrip() + "\n"


def render_termination_markdown(plan: dict[str, object]) -> str:
    lines = [
        "# Autonomous Termination Contract",
        "",
        "The autonomous manuscript runtime terminates only when both conditions are true:",
        "",
        "1. there is no remaining macro step in `framework/registry/autonomous_master_plan.json`",
        "2. every terminal completion action below is complete",
        "",
        "## Terminal Completion Actions",
        "",
    ]
    for action in plan["terminal_actions"]:
        lines.append(f"- {action}")
    lines += [
        "",
        "## Stop Rule",
        "",
        "The terminal micro plan must hand off into terminal-complete state on its penultimate step, then the final micro step reads that terminal state and stops only because no successor macro step exists.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    plan = build_master_plan()
    MASTER_JSON_PATH.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    MASTER_MD_PATH.write_text(render_master_markdown(plan), encoding="utf-8")
    TERMINATION_MD_PATH.write_text(render_termination_markdown(plan), encoding="utf-8")


if __name__ == "__main__":
    main()
