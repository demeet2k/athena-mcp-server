from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "manifests"
REGISTRY_PATH = ROOT / "framework" / "registry" / "folio_sequence.json"
MASTER_PLAN_PATH = ROOT / "framework" / "registry" / "autonomous_master_plan.json"
MACRO_STATE_PATH = MANIFESTS / "AUTONOMOUS_MACRO_STATE.json"
FOLIOS_DIR = ROOT / "folios"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the autonomous cursor, macro state, and active micro plan.")
    parser.add_argument("--completed", help="Completed folio id, e.g. F003R")
    parser.add_argument("--completed-step", help="Completed macro step id, e.g. MACRO_006_F003V")
    parser.add_argument("--sync-from-disk", action="store_true", help="Recover folio-step completion from *_FINAL_DRAFT.md files.")
    return parser.parse_args()


def load_registry() -> list[dict[str, object]]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return list(data["folios"])


def load_master_plan() -> dict[str, object]:
    if not MASTER_PLAN_PATH.exists():
        raise FileNotFoundError(f"Missing master plan at {MASTER_PLAN_PATH}. Run build_autonomous_master_plan.py first.")
    return json.loads(MASTER_PLAN_PATH.read_text(encoding="utf-8"))


def completed_from_disk() -> set[str]:
    pattern = re.compile(r"^(F\d{3}[RV])_FINAL_DRAFT\.md$")
    out: set[str] = set()
    for path in FOLIOS_DIR.glob("*_FINAL_DRAFT.md"):
        match = pattern.match(path.name)
        if match:
            out.add(match.group(1))
    return out


def ordered_completed_folios(registry: list[dict[str, object]], completed: set[str]) -> list[str]:
    return [str(entry["folio"]) for entry in registry if entry["folio"] in completed]


def load_macro_state(master_plan: dict[str, object]) -> set[str]:
    valid = {str(step["step_id"]) for step in master_plan["macro_steps"]}
    if not MACRO_STATE_PATH.exists():
        return set()
    data = json.loads(MACRO_STATE_PATH.read_text(encoding="utf-8"))
    return {step_id for step_id in data.get("completed_step_ids", []) if step_id in valid}


def folio_step_map(master_plan: dict[str, object]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for step in master_plan["macro_steps"]:
        if step["kind"] == "folio":
            mapping[str(step["folio"])] = str(step["step_id"])
    return mapping


def save_macro_state(completed_step_ids: set[str], active_step: dict[str, object] | None, master_plan: dict[str, object]) -> None:
    payload = {
        "version": "1.0.0",
        "macro_step_count": len(master_plan["macro_steps"]),
        "completed_step_ids": sorted(completed_step_ids),
        "completed_step_count": len(completed_step_ids),
        "active_step_id": active_step["step_id"] if active_step else None,
    }
    MACRO_STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def active_step_from_state(master_plan: dict[str, object], completed_step_ids: set[str]) -> dict[str, object] | None:
    for step in master_plan["macro_steps"]:
        if step["step_id"] not in completed_step_ids:
            return step
    return None


def resolve_state(args: argparse.Namespace, registry: list[dict[str, object]], master_plan: dict[str, object]) -> dict[str, object]:
    completed_folios_set = completed_from_disk()
    completed_folios = ordered_completed_folios(registry, completed_folios_set)
    last_completed_folio = completed_folios[-1] if completed_folios else None

    completed_step_ids = load_macro_state(master_plan)
    folio_to_step = folio_step_map(master_plan)

    if args.sync_from_disk:
        for folio in completed_folios_set:
            step_id = folio_to_step.get(folio)
            if step_id:
                completed_step_ids.add(step_id)

    if args.completed:
        folio = args.completed.upper()
        step_id = folio_to_step.get(folio)
        if step_id:
            completed_step_ids.add(step_id)
        last_completed_folio = folio

    if args.completed_step:
        completed_step_ids.add(args.completed_step)

    active_step = active_step_from_state(master_plan, completed_step_ids)
    save_macro_state(completed_step_ids, active_step, master_plan)

    if active_step is None:
        return {
            "completed_folios": completed_folios,
            "last_completed_folio": last_completed_folio or "F116V",
            "active_step": None,
            "next_folio": None,
            "next_macro_step_id": None,
            "completed_step_ids": completed_step_ids,
            "macro_step_count": len(master_plan["macro_steps"]),
        }

    next_folio = str(active_step["folio"]) if active_step["kind"] == "folio" else None
    return {
        "completed_folios": completed_folios,
        "last_completed_folio": last_completed_folio or "NONE",
        "active_step": active_step,
        "next_folio": next_folio,
        "next_macro_step_id": active_step["step_id"],
        "completed_step_ids": completed_step_ids,
        "macro_step_count": len(master_plan["macro_steps"]),
    }


def write_cursor(state: dict[str, object]) -> None:
    active = state["active_step"]
    active_step_id = active["step_id"] if active else "NONE - macro plan complete"
    active_kind = active["kind"] if active else "terminal-complete"
    next_folio = state["next_folio"] or "NONE - execute non-folio macro step or stop"
    book = active["book"] if active else "Manuscript Complete"
    section = active["section"] if active else "unified/VOYNICH_FULL_TRANSLATION.md"
    crystal = active["crystal"] if active else "crystals/VOYNICH_FULL_CRYSTAL.md"

    text = f"""# Autonomous Cursor

## Mode

- Execution mode: `no-stop recursive continuation`
- Persistence law: `completion exhaust becomes next-step intake`
- Hard-stop rule: stop only for an honest blocker or explicit user redirect

## Current Cursor

- Last authoritative folio: `{state["last_completed_folio"]}`
- Active macro step: `{active_step_id}`
- Active macro kind: `{active_kind}`
- Next authoritative folio: `{next_folio}`
- Current book: `{book}`
- Active section synthesis: `{section}`
- Active crystal: `{crystal}`
- Macro progress: `{len(state["completed_step_ids"])}` / `{state["macro_step_count"]}` completed
- Master control plan: `manifests/AUTONOMOUS_MASTER_PLAN.md`
- Active micro plan: `manifests/ACTIVE_MICRO_PLAN.md`
- Active run task list: `manifests/ACTIVE_RUN_TASK_LIST.md`
- Parallel agent queue: `manifests/PARALLEL_AGENT_QUEUE.md`
- Termination contract: `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md`
"""
    (MANIFESTS / "AUTONOMOUS_CURSOR.md").write_text(text, encoding="utf-8")


def write_prompt(state: dict[str, object]) -> None:
    active = state["active_step"]
    if active is None:
        text = """# Next Folio Self Prompt

No macro step remains.

Execute the terminal-complete closeout in `manifests/ACTIVE_MICRO_PLAN.md` and stop.
"""
    elif active["kind"] == "folio":
        folio = active["folio"]
        text = f"""# Next Folio Self Prompt

Current cursor is now past `{state["last_completed_folio"]}`.

Begin macro step `{active["step_id"]}` for `{folio}` immediately.

## Required Outputs

1. `folios/{folio}_FINAL_DRAFT.md`
2. pointer file `folios/{folio}.md`
3. unified corpus update
4. section synthesis update for `{active["section"]}`
5. crystal update for `{active["crystal"]}`
6. metro update
7. build-status update
8. master-manuscript append in `unified/VOYNICH_MASTER_MANUSCRIPT.md`
9. regenerate `manifests/ACTIVE_MICRO_PLAN.md`, `manifests/ACTIVE_RUN_TASK_LIST.md`, and `manifests/PARALLEL_AGENT_QUEUE.md` from the next macro step
10. immediately read the emitted successor run task list and the parallel-agent queue and treat them as the next intake state
"""
    else:
        text = f"""# Next Folio Self Prompt

Current cursor is now past `{state["last_completed_folio"]}`.

Execute non-folio macro step `{active["step_id"]}` immediately.

## Target

- kind: `{active["kind"]}`
- title: `{active["title"]}`
- section: `{active["section"]}`
- crystal: `{active["crystal"]}`
- parallel queue: `manifests/PARALLEL_AGENT_QUEUE.md`
"""
    (MANIFESTS / "NEXT_FOLIO_SELF_PROMPT.md").write_text(text, encoding="utf-8")


def write_queue(state: dict[str, object], master_plan: dict[str, object]) -> None:
    completed = set(state["completed_step_ids"])
    recent_steps = [step for step in master_plan["macro_steps"] if step["step_id"] in completed][-5:]
    upcoming_steps = [step for step in master_plan["macro_steps"] if step["step_id"] not in completed][:10]

    text = f"""# Autonomous Queue

## Queue State

- Macro step count: `{state["macro_step_count"]}`
- Completed macro steps: `{len(completed)}`
- Remaining macro steps: `{state["macro_step_count"] - len(completed)}`
- Last authoritative folio: `{state["last_completed_folio"]}`
- Active macro step: `{state["active_step"]["step_id"] if state["active_step"] else "NONE - macro plan complete"}`
- Active macro kind: `{state["active_step"]["kind"] if state["active_step"] else "terminal-complete"}`

## Recent Completed Macro Steps
"""
    if recent_steps:
        for step in recent_steps:
            text += f"- `{step['step_id']}` - {step['title']}\n"
    else:
        text += "- none yet\n"

    text += "\n## Upcoming Macro Steps\n"
    if upcoming_steps:
        for step in upcoming_steps:
            text += f"- `{step['step_id']}` - {step['title']}\n"
    else:
        text += "- macro plan exhausted\n"

    text += """

## Plan Handoff

- master plan: `manifests/AUTONOMOUS_MASTER_PLAN.md`
- active micro plan: `manifests/ACTIVE_MICRO_PLAN.md`
- active run task list: `manifests/ACTIVE_RUN_TASK_LIST.md`
- termination contract: `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md`
"""
    (MANIFESTS / "AUTONOMOUS_QUEUE.md").write_text(text, encoding="utf-8")


def write_parallel_agent_queue(state: dict[str, object], master_plan: dict[str, object]) -> None:
    pending_folio_steps = [
        step
        for step in master_plan["macro_steps"]
        if step["kind"] == "folio" and step["step_id"] not in state["completed_step_ids"]
    ]
    lanes = []
    lane_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"]
    lane_roles = [
        "primary build lane",
        "shadow successor lane",
        "preheated follow-on lane",
        "buffer lane after the follow-on",
        "mid-horizon reserve lane",
        "extended reserve lane",
        "far-horizon reserve lane",
        "deep queue stabilization lane",
    ]
    for idx, step in enumerate(pending_folio_steps[:8]):
        lanes.append((lane_names[idx], lane_roles[idx], step))

    lines = [
        "# Parallel Agent Queue",
        "",
        "## Control Law",
        "",
        "The runtime should never hold only one live folio in mind.",
        "Lane Alpha is the active authoritative build.",
        "Lane Beta is the immediate successor shadow lane.",
        "Lane Gamma is the preheated follow-on lane after that.",
        "Lane Delta is the buffered lane after Gamma.",
        "Lane Epsilon extends the queue past the first local buffer.",
        "Lane Zeta keeps the mid-horizon successor already warm.",
        "Lane Eta keeps the far-horizon successor visible.",
        "Lane Theta preserves one more deep reserve so the queue does not collapse back to a short horizon.",
        "",
        "## Live Lanes",
        "",
    ]
    if lanes:
        for name, role, step in lanes:
            lines += [
                f"### Lane {name}",
                "",
                f"- role: `{role}`",
                f"- macro step: `{step['step_id']}`",
                f"- folio: `{step['folio']}`",
                f"- book: `{step['book']}`",
                f"- section: `{step['section']}`",
                f"- crystal: `{step['crystal']}`",
                f"- next after handoff: `{step['next_step_id'] or 'NONE'}`",
                "",
            ]
    else:
        lines += ["- no pending folio lanes remain", ""]

    lines += [
        "## Lane Rule",
        "",
        "When Lane Alpha hands off, every remaining lane slides forward by one position, and the deepest available successor repopulates the last open lane. This file must be rewritten on every handoff so eight successor lanes already exist before Alpha is finished.",
        "",
    ]
    (MANIFESTS / "PARALLEL_AGENT_QUEUE.md").write_text("\n".join(lines), encoding="utf-8")


def folio_micro_steps(step: dict[str, object]) -> list[str]:
    return [
        "Step 1. Intake the folio witness set and normalize the EVA line inventory.",
        "Step 2. Scaffold or refresh the authoritative final-draft folio file and pointer file.",
        "Step 3. Fill the direct evidence layer: source stack, reading contract, zero claim, and direct ledger.",
        "Step 4. Complete the visual/codicological pass or explicitly mark the folio as text-only.",
        "Step 5. Render all formal and mythic lenses with real equations in every formal-math lens.",
        "Step 6. Compile the formal overlay: line operators, paragraph compositions, invariants, transport laws, and folio theorem.",
        "Step 7. Write the synthesis layer: direct operational meaning, mathematical extraction, mythic extraction, zero point, and dense compression.",
        "Step 8. Audit honesty, completeness, uncertainty, and page-specific signatures.",
        "Step 9. Roll the folio into unified corpus, section synthesis, crystal, metro, build status, and master manuscript.",
        f"Step 10. Handoff: run `python \"{ROOT / 'framework' / 'scripts' / 'update_autonomous_cursor.py'}\" --completed-step {step['step_id']}` so the macro plan advances to `{step['next_step_id'] or 'STOP'}` and emits the next micro plan.",
        "Step 11. Immediately read the emitted successor micro plan and treat it as the live intake state. Do not interpret Step 10 as completion.",
    ]


def section_micro_steps(step: dict[str, object]) -> list[str]:
    actions = list(step.get("actions", []))
    lines = [
        "Step 1. Consolidate the completed folios of this section inside the section synthesis file.",
        "Step 2. Finish the section crystal synthesis layer.",
        "Step 3. Write or refresh the section metro map.",
        "Step 4. Write or refresh the section emergent metro map.",
    ]
    for idx, action in enumerate(actions, start=5):
        lines.append(f"Step {idx}. {action[0].upper() + action[1:]}.")
    handoff_index = len(lines) + 1
    lines.append(
        f"Step {handoff_index}. Handoff: run `python \"{ROOT / 'framework' / 'scripts' / 'update_autonomous_cursor.py'}\" --completed-step {step['step_id']}` so the macro plan advances to `{step['next_step_id'] or 'STOP'}` and emits the next micro plan."
    )
    lines.append(f"Step {handoff_index + 1}. Immediately read the emitted successor micro plan and treat it as the live intake state. Do not interpret the handoff as completion.")
    return lines


def terminal_micro_steps(step: dict[str, object]) -> list[str]:
    lines = []
    for idx, action in enumerate(step.get("actions", []), start=1):
        lines.append(f"Step {idx}. {action[0].upper() + action[1:]}.")
    handoff_index = len(lines) + 1
    lines.append(
        f"Step {handoff_index}. Handoff: run `python \"{ROOT / 'framework' / 'scripts' / 'update_autonomous_cursor.py'}\" --completed-step {step['step_id']}` so the macro plan emits terminal-complete state."
    )
    lines.append(f"Step {handoff_index + 1}. Read the emitted terminal-complete state and stop only because no successor macro step exists.")
    return lines


def write_micro_plan(state: dict[str, object]) -> None:
    active = state["active_step"]
    path = MANIFESTS / "ACTIVE_MICRO_PLAN.md"

    if active is None:
        path.write_text(
            "# Active Micro Plan\n\n## Status\n\n- state: `terminal-complete`\n- note: no remaining macro step exists\n",
            encoding="utf-8",
        )
        return

    if active["kind"] == "folio":
        steps = folio_micro_steps(active)
    elif active["kind"] == "section_completion":
        steps = section_micro_steps(active)
    else:
        steps = terminal_micro_steps(active)

    lines = [
        "# Active Micro Plan",
        "",
        "## Status",
        "",
        "- state: `active`",
        f"- macro step id: `{active['step_id']}`",
        f"- macro step number: `{active['step_number']}` of `{state['macro_step_count']}`",
        f"- macro kind: `{active['kind']}`",
        f"- title: `{active['title']}`",
        f"- previous authoritative folio: `{state['last_completed_folio']}`",
        f"- next macro step after handoff: `{active['next_step_id'] or 'NONE - terminal complete'}`",
        "",
        "## Required Outputs",
        "",
    ]
    for output in active.get("outputs", []):
        lines.append(f"- `{output}`")

    lines += ["", "## Micro Steps", ""]
    lines.extend(f"- {step}" for step in steps)
    lines += ["", "## Stop Rule", "", "The penultimate micro step must hand off to the next macro step. The final micro step is successor intake, not completion. The successor intake must read both the rewritten run task list and the rewritten parallel lane queue. Stopping is only valid when the emitted successor state is terminal-complete.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_run_tasks(state: dict[str, object]) -> list[str]:
    active = state["active_step"]
    if active is None:
        return [
            "Task 1. Confirm that no remaining macro step exists.",
            "Task 2. Finalize terminal packaging artifacts only if any terminal action remains incomplete.",
            "Task 3. Emit terminal-complete state into the runtime manifests.",
            "Task 4. Re-read the emitted terminal state and confirm that no successor step was generated.",
            "Task 5. Stop only because the macro plan is exhausted; no ouroboros reboot remains available.",
        ]

    if active["kind"] == "folio":
        folio = active["folio"]
        next_step = active["next_step_id"] or "terminal-complete"
        next_folio = next_step.split("_", 2)[-1] if next_step.startswith("MACRO_") else "terminal-complete"
        return [
            f"Task 1. Intake and normalize the full witness set for `{folio}`.",
            f"Task 2. Build the authoritative folio outputs for `{folio}`: final draft, pointer file, direct ledger, and full multilens math/myth stack.",
            "Task 3. Roll the finished folio into unified corpus, section synthesis, crystal, metro, build status, and master manuscript, then refresh the shadow folio lanes.",
            f"Task 4. Advance the macro state with `update_autonomous_cursor.py --completed-step {active['step_id']}` so the runtime rewrites itself to `{next_step}`.",
            f"Task 5. Reboot the cycle by reading the newly emitted `manifests/ACTIVE_RUN_TASK_LIST.md` and `manifests/PARALLEL_AGENT_QUEUE.md` for `{next_folio}` and treating those rewritten lane files as the next live intake instead of completion.",
        ]

    if active["kind"] == "section_completion":
        next_step = active["next_step_id"] or "terminal-complete"
        return [
            f"Task 1. Consolidate the completed folios inside `{active['section']}`.",
            f"Task 2. Complete the section crystal work in `{active['crystal']}`.",
            "Task 3. Finish the section metro and emergent metro rollups, update corpus/master packaging, and refresh the parallel lane queue.",
            f"Task 4. Advance the macro state with `update_autonomous_cursor.py --completed-step {active['step_id']}` so the runtime rewrites itself to `{next_step}`.",
            "Task 5. Reboot the cycle by reading the newly emitted `manifests/ACTIVE_RUN_TASK_LIST.md` and `manifests/PARALLEL_AGENT_QUEUE.md` and treating those successor lane files as the next live intake.",
        ]

    return [
        "Task 1. Execute the remaining terminal completion actions.",
        "Task 2. Finalize the full crystal, master manuscript, and giant manuscript package.",
        "Task 3. Emit terminal-complete state into the runtime manifests.",
        f"Task 4. Advance the macro state with `update_autonomous_cursor.py --completed-step {active['step_id']}` so the runtime rewrites itself into terminal-complete state.",
        "Task 5. Re-read the emitted terminal state and parallel queue and stop only because no successor folio lane was generated.",
    ]


def write_run_task_list(state: dict[str, object]) -> None:
    active = state["active_step"]
    tasks = build_run_tasks(state)
    path = MANIFESTS / "ACTIVE_RUN_TASK_LIST.md"

    lines = [
        "# Active Run Task List",
        "",
        "## Control Law",
        "",
        "This is the run-level ouroboros list.",
        "Task 5 must reboot the cycle by reading the newly emitted successor task list and parallel lane queue before completion can be interpreted.",
        "",
        "## Status",
        "",
        f"- macro step: `{active['step_id'] if active else 'NONE - terminal complete'}`",
        f"- title: `{active['title'] if active else 'terminal complete'}`",
        f"- previous authoritative folio: `{state['last_completed_folio']}`",
        f"- next macro step after handoff: `{active['next_step_id'] if active else 'NONE'}`",
        "",
        "## Five Tasks",
        "",
    ]
    lines.extend(f"{idx}. {task[8:] if task.startswith('Task ') else task}" for idx, task in enumerate(tasks, start=1))
    lines += [
        "",
        "## Ouroboros Rule",
        "",
        "The list is not allowed to bottom out at Task 4. Task 4 must rewrite this file and the parallel lane queue to the successor step, and Task 5 must read those rewritten lane files as the next live intake.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    registry = load_registry()
    master_plan = load_master_plan()
    state = resolve_state(args, registry, master_plan)
    write_cursor(state)
    write_prompt(state)
    write_queue(state, master_plan)
    write_parallel_agent_queue(state, master_plan)
    write_micro_plan(state)
    write_run_task_list(state)


if __name__ == "__main__":
    main()
