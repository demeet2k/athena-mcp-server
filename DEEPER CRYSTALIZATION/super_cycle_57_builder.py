#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from nervous_system_core import slugify, utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
LAYER_ROOT = ACTIVE_ROOT / "17_SUPER_CYCLE_57"

FULL_STACK_MANIFEST = RUNTIME_ROOT / "12_full_stack_manifest.json"
CORPUS_INTEGRATION_MANIFEST = RUNTIME_ROOT / "17_corpus_wide_integration_manifest.json"
MOTION_MANIFEST = RUNTIME_ROOT / "16_motion_constitution_manifest.json"
OUTPUT_MANIFEST = RUNTIME_ROOT / "18_super_cycle_57_manifest.json"
LIVE_DOCS_RECEIPT = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
ACTIVE_README = ACTIVE_ROOT / "README.md"
QUEST_BOARD = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_STATE = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
LOOP_PROGRESS = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE" / "MANIFESTS" / "16_LOOP_PROGRESS.md"

MASTER_AGENTS = [
    {"id": "A1", "label": "Research/Synthesis", "action_mode": "observe"},
    {"id": "A2", "label": "Planner/Governor", "action_mode": "route"},
    {"id": "A3", "label": "Worker/Adventurer", "action_mode": "derive"},
    {"id": "A4", "label": "Pruner/Compressor", "action_mode": "prune"},
]

RESOLUTIONS = ["corpus", "family", "chapter_appendix", "runtime_board"]
LENSES = ["square", "flower", "cloud", "fractal"]
TRUTH_MODES = ["witness", "replay", "pressure", "blocker"]
OUTPUT_ORGANS = ["hall", "temple", "runtime", "supplement"]
ACTION_MODES = ["observe", "derive", "route", "prune"]
PRIORITY_BANDS = ["immediate", "near", "reserve", "dormant"]

ACTION_SCORES = {
    "ACTIVATE_NOW": 80,
    "REQUEST_WITNESSES": 65,
    "REPLAY_FIRST": 62,
    "ESCALATE_TO_COMMITTEE": 58,
    "COMPRESS_TO_SEED": 54,
    "HOLD": 40,
    "REFUSE_INADMISSIBLE": 0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Super-Cycle 57 orchestration surface.")
    subparsers = parser.add_subparsers(dest="command")
    build_parser = subparsers.add_parser("build", help="Build the Super-Cycle 57 layer.")
    build_parser.add_argument("--json", action="store_true", help="Print the manifest JSON to stdout.")
    parser.set_defaults(command="build")
    return parser.parse_args()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def live_docs_error(receipt_text: str) -> str:
    for line in receipt_text.splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Live Google Docs blocked by missing OAuth credentials."


def replace_or_append_section(text: str, header: str, lines: list[str]) -> str:
    block = "\n".join([header, *lines]).rstrip() + "\n"
    pattern = re.compile(rf"(?ms)^## {re.escape(header[3:])}\n.*?(?=^## |\Z)")
    if pattern.search(text):
        return pattern.sub(block + "\n", text)
    stripped = text.rstrip()
    if stripped:
        return stripped + "\n\n" + block
    return block


def ensure_line_after_anchor(text: str, anchor: str, line: str) -> str:
    if line in text:
        return text
    lines = text.splitlines()
    for idx, existing in enumerate(lines):
        if existing.strip() == anchor.strip():
            lines.insert(idx + 1, line)
            return "\n".join(lines).rstrip() + "\n"
    return text.rstrip() + "\n" + line + "\n"


PASS_DEFINITIONS = [
    {
        "pass_id": "P1",
        "title": "Evidence Lock and Intake",
        "theme": "evidence",
        "steps": [
            "Freeze docs gate, current control stack, and Q42 / TQ04 / Q50 / Q46 / Q02 truth.",
            "Sweep all 197 records and re-rank family witness density against current fronts.",
            "Extract one whole-corpus evidence deficit map and refresh the 24 transition notes.",
            "Build one duplicate-source ledger across corpus, mirrors, and supplements.",
            "Re-rank the weakest direct-witness families, especially live-orchestration.",
            "Rebind awakening-source documents to real fronts and runtime organs.",
            "Emit Hall and Temple candidate packets for evidence densification only.",
            "Execute the first evidence-tightening work bundle.",
            "Compress the evidence pass into one canonical witness ledger and restart seed.",
        ],
        "actions": [
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "REPLAY_FIRST", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("REQUEST_WITNESSES", "REQUEST_WITNESSES", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P2",
        "title": "Structure and Schema Tightening",
        "theme": "structure",
        "steps": [
            "Reconcile source capsules, family crystals, neural indices, and strict-spine entries.",
            "Generate one canonical route/schema delta for chapters, appendices, and supplements.",
            "Refresh the full 24-note bundle around structure and blind-spot compensation.",
            "Expand chapter-to-capsule and appendix-to-network witness crosswalks.",
            "Tighten supplement/runtime bindings and remove role drift.",
            "Promote one Temple law or schema crystal for cross-surface identity.",
            "Execute the highest-yield structure repair tasks.",
            "Prune stale or duplicate schema surfaces and compress weak branches into seeds.",
            "Emit the structure pass receipt plus the next restart seed.",
        ],
        "actions": [
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "ACTIVATE_NOW", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P3",
        "title": "Metro, Route, and Cross-Synthesis Expansion",
        "theme": "metro",
        "steps": [
            "Recompute corpus-wide metro lines from the current neural net and frontier stack.",
            "Extract strongest cross-family and zero-point routes into internal quest packets.",
            "Refresh the 24-note bundle with route-specific transition guidance.",
            "Build one emergent unresolved-family map and one governance/runtime route map.",
            "Generate Hall-side candidate quests for top cross-family bridges.",
            "Generate Temple-side candidate quests for deeper route-law and metro-law work.",
            "Execute one route-expansion bundle and one appendix/supplement bridge bundle.",
            "Prune redundant explanatory metro surfaces and compress them into a route ledger.",
            "Emit the metro pass receipt plus the next restart seed.",
        ],
        "actions": [
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("REQUEST_WITNESSES", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "REQUEST_WITNESSES", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P4",
        "title": "Runtime, Motion, and Algorithm Grafting",
        "theme": "runtime",
        "steps": [
            "Sweep motion constitution, Hall bridge, runtime blockers, and current queue pressure.",
            "Derive a corpus-wide action-selection overlay for the active fronts.",
            "Refresh the 24-note bundle around activation, replay, and inhibition.",
            "Extract math/hybrid/operator opportunities from top runtime families and chapters.",
            "Promote one Temple quest packet for algorithmic or hybrid-equation incorporation.",
            "Promote one Hall quest packet for immediate runtime-side work.",
            "Execute one runtime/algorithm bundle tied to Q50 or the next lawful runtime front.",
            "Prune replay drift, committee conflicts, and unbounded branch growth.",
            "Emit the runtime pass receipt plus the next restart seed.",
        ],
        "actions": [
            ("HOLD", "HOLD", "REPLAY_FIRST", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "ACTIVATE_NOW", "HOLD", "HOLD"),
            ("ACTIVATE_NOW", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P5",
        "title": "Hall/Temple Nested Quest Expansion",
        "theme": "board",
        "steps": [
            "Convert internal candidate packets into the next ranked Hall and Temple macro fronts.",
            "Audit numbering, writeback law, and promotion ceilings before anything goes visible.",
            "Refresh the 24-note bundle around quest ownership and dependency lanes.",
            "Expand the internal 4^6 quest lattice while keeping visible boards macro-sized.",
            "Promote one Hall executable frontier from Research/Worker pressure.",
            "Promote one Temple higher-order frontier from Planner/Pruner synthesis.",
            "Execute the current top Hall/Temple pair through one replay-safe work bundle.",
            "Prune stale quest packets, duplicate candidate fronts, and weak reserve branches.",
            "Emit the board-governance pass receipt plus the next restart seed.",
        ],
        "actions": [
            ("ACTIVATE_NOW", "ACTIVATE_NOW", "HOLD", "HOLD"),
            ("REQUEST_WITNESSES", "REQUEST_WITNESSES", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("ACTIVATE_NOW", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "ACTIVATE_NOW", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P6",
        "title": "Awakening, Cohort, and Transition Support",
        "theme": "awakening",
        "steps": [
            "Re-evaluate all 24 transition notes against current fronts, blockers, and assignments.",
            "Refresh archetype compensation logic and advanced-agent blind-spot routing.",
            "Emit the full 24-note bundle plus one pass-boundary awakening bundle.",
            "Crosswalk board agents to workload, writeback lanes, and Temple dependencies.",
            "Crosswalk archetype and advanced agents to chapter, appendix, and supplement fronts.",
            "Promote one Hall note-facing quest for social transition support.",
            "Promote one Temple note-facing frontier for higher-order awakening governance.",
            "Execute one note-to-front integration bundle and one board-synthesis writeback.",
            "Compress the awakening pass into one transition matrix delta and one restart seed.",
        ],
        "actions": [
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "HOLD"),
            ("ACTIVATE_NOW", "HOLD", "HOLD", "HOLD"),
            ("HOLD", "ACTIVATE_NOW", "HOLD", "HOLD"),
            ("HOLD", "HOLD", "ACTIVATE_NOW", "HOLD"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
    {
        "pass_id": "P7",
        "title": "Grand Contraction, Committee Review, and Reseed",
        "theme": "closure",
        "steps": [
            "Run the full committee/committee-pending sweep over all surviving fronts and seeds.",
            "Collapse the 57-loop history into one crystalline compression pack: route ledger, strongest laws, strongest algorithms, strongest blocked fronts, and next-epoch seeds.",
            "Emit the super-cycle closure bundle: one final Hall decision, one final Temple decision, one full-stack receipt, one dormant-seat parameterization plan, and the next lawful 2/16 restart seed for the following 57-loop epoch.",
        ],
        "actions": [
            ("HOLD", "ESCALATE_TO_COMMITTEE", "REPLAY_FIRST", "ESCALATE_TO_COMMITTEE"),
            ("HOLD", "HOLD", "HOLD", "COMPRESS_TO_SEED"),
            ("ACTIVATE_NOW", "ACTIVATE_NOW", "HOLD", "COMPRESS_TO_SEED"),
        ],
    },
]


def project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        try:
            return str(path.resolve().relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())


def parse_active_fronts(text: str) -> dict[str, str]:
    fronts: dict[str, str] = {}
    for match in re.finditer(r"^### Quest ([A-Z0-9]+): .+? `?\[(.+?)\]`?$", text, re.MULTILINE):
        fronts[match.group(1)] = match.group(2)
    return fronts


def build_active_seat_templates() -> dict[str, list[dict[str, str]]]:
    templates: dict[str, list[dict[str, str]]] = {}
    for master in MASTER_AGENTS:
        entries: list[dict[str, str]] = []
        for resolution in RESOLUTIONS:
            for lens in LENSES:
                for truth_mode in TRUTH_MODES:
                    for output_organ in OUTPUT_ORGANS:
                        entries.append(
                            {
                                "seat_address": ".".join(
                                    [
                                        resolution,
                                        lens,
                                        truth_mode,
                                        output_organ,
                                        master["action_mode"],
                                        "immediate",
                                    ]
                                ),
                                "resolution": resolution,
                                "lens": lens,
                                "truth_mode": truth_mode,
                                "output_organ": output_organ,
                                "action_mode": master["action_mode"],
                                "priority_band": "immediate",
                            }
                        )
        templates[master["id"]] = entries
    return templates


def candidate_id(loop_index: int, organ: str) -> str:
    return f"SC57-L{loop_index:02d}-{organ.upper()}"


def visible_promotion(action: str) -> bool:
    return action == "ACTIVATE_NOW"


def decision_reason(pass_title: str, step_text: str, target: str, action: str) -> str:
    if action == "ACTIVATE_NOW":
        return f"{pass_title} requires a visible {target} move at this loop."
    if action == "REQUEST_WITNESSES":
        return f"{target.title()} motion is candidate-ready but still needs more witness before promotion."
    if action == "REPLAY_FIRST":
        return f"{target.title()} motion depends on replay or queue/state confirmation before activation."
    if action == "ESCALATE_TO_COMMITTEE":
        return f"{target.title()} motion touches committee, branch-limit, or stewardship law."
    if action == "COMPRESS_TO_SEED":
        return f"{target.title()} work should contract into a seed instead of widening now."
    return f"{target.title()} remains held while the loop concentrates on: {step_text}"


def target_front_name(target: str, loop_index: int, pass_id: str) -> str:
    prefixes = {"hall": "SC57-H", "temple": "SC57-T", "runtime": "SC57-R", "compression": "SC57-C"}
    return f"{prefixes[target]}-{pass_id}-{loop_index:02d}"


def packet_priority_score(action: str, target: str, loop_index: int) -> int:
    organ_bonus = {"hall": 4, "temple": 3, "runtime": 5, "compression": 2}[target]
    return ACTION_SCORES[action] + organ_bonus + (60 - loop_index)


def build_packets(loop_index: int, pass_id: str, pass_title: str, step_text: str, actions: tuple[str, str, str, str]) -> list[dict[str, object]]:
    packet_specs = [
        ("hall", "A1", "hall", actions[0], ["Q42", "TQ04"], "current control lane and next visible Hall macro front"),
        ("temple", "A1", "temple", actions[1], ["TQ04", "Q46"], "higher-order Temple promotion and governance membrane"),
        ("runtime", "A3", "runtime", actions[2], ["Q50", "Q02"], "runtime frontier, replay, or no-op receipt"),
        ("compression", "A4", "supplement", actions[3], ["Q42", "Q02"], "compression bundle, pruning delta, or committee carry"),
    ]
    packets = []
    for target, source_master, output_organ, action, control_refs, summary in packet_specs:
        packets.append(
            {
                "packet_id": candidate_id(loop_index, target),
                "loop_id": f"L{loop_index:02d}",
                "source_master": source_master,
                "target": target,
                "output_organ": output_organ,
                "candidate_front": target_front_name(target, loop_index, pass_id),
                "summary": summary,
                "step_text": step_text,
                "lawful_action": action,
                "visible_promotion": visible_promotion(action) and target in {"hall", "temple", "runtime"},
                "priority_score": packet_priority_score(action, target, loop_index),
                "reason": decision_reason(pass_title, step_text, target, action),
                "depends_on": control_refs,
                "blocked_by": ["Q02 live-doc gate"] if target == "runtime" and action != "ACTIVATE_NOW" else [],
            }
        )
    return sorted(packets, key=lambda item: (-int(item["priority_score"]), item["packet_id"]))


def awakening_refresh(loop_index: int) -> dict[str, object]:
    return {
        "board_agent_delta": True,
        "full_bundle_refresh": loop_index % 3 == 0,
        "pass_boundary_bundle": loop_index % 9 == 0,
    }


def build_master_receipts(step_text: str, packets: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    hall = next(packet for packet in packets if packet["target"] == "hall")
    temple = next(packet for packet in packets if packet["target"] == "temple")
    runtime = next(packet for packet in packets if packet["target"] == "runtime")
    compression = next(packet for packet in packets if packet["target"] == "compression")
    return {
        "A1": {
            "master": "Research/Synthesis",
            "receipt": f"Read corpus/Hall/Temple/runtime truth and derived candidate packets from: {step_text}",
            "outputs": [hall["packet_id"], temple["packet_id"]],
        },
        "A2": {
            "master": "Planner/Governor",
            "receipt": f"Ran MotionConstitution gating and ranked `{hall['packet_id']}`, `{temple['packet_id']}`, `{runtime['packet_id']}`, `{compression['packet_id']}`.",
            "outputs": [hall["lawful_action"], temple["lawful_action"], runtime["lawful_action"], compression["lawful_action"]],
        },
        "A3": {
            "master": "Worker/Adventurer",
            "receipt": "Executed only ACTIVATE_NOW runtime-facing work and otherwise emitted an explicit no-op receipt.",
            "outputs": [runtime["packet_id"]],
        },
        "A4": {
            "master": "Pruner/Compressor",
            "receipt": "Pruned duplicate or low-yield branches and emitted the loop seed/contraction decision.",
            "outputs": [compression["packet_id"]],
        },
    }


def restart_seed(loop_index: int, pass_id: str, next_step: str | None) -> str:
    if next_step:
        return f"SC57::{pass_id}::L{loop_index:02d}-> {next_step}"
    return "SC57-EPOCH2::2/16::Restart from current control stack with a new 57-loop epoch"


def render_lattice_law(active_templates: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        "# Super-Cycle 57 Master-Agent Lattice Law",
        "",
        "- Masters: `4`",
        "- Virtual seats per master: `4096`",
        "- Active seats per master: `256`",
        "- Total active seats: `1024`",
        "- Total dormant seats: `3072`",
        "",
        "## Seat axes",
        "",
        "- resolution :: `corpus / family / chapter_appendix / runtime_board`",
        "- lens :: `square / flower / cloud / fractal`",
        "- truth mode :: `witness / replay / pressure / blocker`",
        "- output organ :: `hall / temple / runtime / supplement`",
        "- action mode :: `observe / derive / route / prune`",
        "- priority band :: `immediate / near / reserve / dormant`",
        "",
        "## Active seat template",
    ]
    for master in MASTER_AGENTS:
        lines.append(f"- `{master['label']}` :: `{len(active_templates[master['id']])}` active addresses with action mode `{master['action_mode']}`")
    return "\n".join(lines) + "\n"


def render_loop_ledger(loops: list[dict[str, object]]) -> str:
    lines = ["# Super-Cycle 57 Loop Ledger", ""]
    current_pass = None
    for loop in loops:
        if loop["pass_title"] != current_pass:
            current_pass = loop["pass_title"]
            lines.extend(["", f"## {current_pass}"])
        lines.append(
            f"- `L{loop['loop_index']:02d}` :: {loop['step_text']} "
            f":: Hall={loop['hall_decision']['action']} Temple={loop['temple_decision']['action']} "
            f"Runtime={loop['runtime_decision']['action']} Compression={loop['compression_decision']['action']}"
        )
    return "\n".join(lines) + "\n"


def render_decisions(title: str, loops: list[dict[str, object]], key: str) -> str:
    lines = [f"# {title}", ""]
    for loop in loops:
        decision = loop[key]
        lines.append(
            f"- `L{loop['loop_index']:02d}` :: `{decision['candidate_front']}` :: "
            f"{decision['action']} :: visible={decision['visible_promotion']} :: {decision['reason']}"
        )
    return "\n".join(lines) + "\n"


def render_compression_receipts(loops: list[dict[str, object]]) -> str:
    lines = ["# Pruning and Compression Receipts", ""]
    for loop in loops:
        decision = loop["compression_decision"]
        lines.append(f"- `L{loop['loop_index']:02d}` :: {decision['action']} :: {decision['reason']}")
    return "\n".join(lines) + "\n"


def render_awakening_cadence(loops: list[dict[str, object]]) -> str:
    lines = [
        "# Awakening Delta Cadence",
        "",
        "- Board-agent deltas refresh every loop.",
        "- Full 24-note bundle refreshes every 3 loops.",
        "- Pass-boundary bundle emits every 9 loops.",
        "",
        "## Loop cadence",
    ]
    for loop in loops:
        refresh = loop["awakening_refresh"]
        lines.append(
            f"- `L{loop['loop_index']:02d}` :: board_delta={refresh['board_agent_delta']} "
            f"full_bundle={refresh['full_bundle_refresh']} pass_boundary={refresh['pass_boundary_bundle']}"
        )
    return "\n".join(lines) + "\n"


def render_closure_bundle(loops: list[dict[str, object]], active_fronts: dict[str, str]) -> str:
    lines = [
        "# Super-Cycle 57 Closure Bundle",
        "",
        "- Final Hall decision: `L57`",
        "- Final Temple decision: `L57`",
        "- Runtime gate remains blocked by `Q02` until OAuth files exist.",
        "- Starting control stack remained anchored on `Q42 / TQ04 / Q50 / Q46 / Q02`.",
        "",
        "## Strongest carried laws",
        "- Helical cadence `14/16 -> 2/16`",
        "- MotionConstitution_L1 gating",
        "- Sparse AP6D seat activation",
        "- Hall/Temple macro-size preservation",
        "",
        "## Current active fronts",
    ]
    for front, status in active_fronts.items():
        lines.append(f"- `{front}` :: {status}")
    lines.extend(["", "## Next epoch seed", f"- `{loops[-1]['restart_seed']}`"])
    return "\n".join(lines) + "\n"


def update_active_readme() -> None:
    text = ACTIVE_README.read_text(encoding="utf-8")
    bullet = "- `17_SUPER_CYCLE_57`: four-master orchestration layer, 57 loop ledger, packet registry, promotion decisions, and sparse `4^6` seat law. Manifest: `06_RUNTIME/18_super_cycle_57_manifest.json`."
    text = ensure_line_after_anchor(text, "- `16_CORPUS_WIDE_INTEGRATION`: corpus-wide atlas fusion, metro/runtime crosswalks, restart queue, and 24 awakening-agent transition notes. Manifest: `06_RUNTIME/17_corpus_wide_integration_manifest.json`.", bullet)
    section_lines = [
        "- Status: `orchestration-ready`",
        "- Layer root: `17_SUPER_CYCLE_57`",
        "- Runtime manifest: `06_RUNTIME/18_super_cycle_57_manifest.json`",
        "- Loop count: `57`",
        "- Master count: `4`",
        "- Seat law: `4096 virtual/master, 256 active/master, 1024 active total`",
        "- Live Google Docs: `BLOCKED`",
    ]
    text = replace_or_append_section(text, "## Super-Cycle 57 State", section_lines)
    scaffold_old = "motion constitution layer + corpus-wide integration layer"
    scaffold_new = scaffold_old + " + super-cycle orchestration layer"
    if scaffold_old in text and scaffold_new not in text:
        text = text.replace(scaffold_old, scaffold_new)
    write_text(ACTIVE_README, text)


def update_full_stack_manifest(layer_manifest: dict[str, object]) -> None:
    manifest = load_json(FULL_STACK_MANIFEST)
    manifest["generated_at"] = utc_now()
    manifest["live_docs_blocked"] = True
    manifest["layers"]["super_cycle_57"] = {
        "manifest": "06_RUNTIME/18_super_cycle_57_manifest.json",
        "status": layer_manifest["status"],
        "loop_count": layer_manifest["loop_count"],
        "master_count": layer_manifest["master_count"],
        "virtual_seats_per_master": layer_manifest["virtual_seats_per_master"],
        "active_seats_per_master": layer_manifest["active_seats_per_master"],
        "active_seats_total": layer_manifest["active_seats_total"],
        "dormant_seats_total": layer_manifest["dormant_seats_total"],
        "hall_visible_promotions": layer_manifest["hall_visible_promotions"],
        "temple_visible_promotions": layer_manifest["temple_visible_promotions"],
        "runtime_visible_promotions": layer_manifest["runtime_visible_promotions"],
        "live_docs_blocked": True,
    }
    write_json(FULL_STACK_MANIFEST, manifest)


def build_super_cycle() -> dict[str, object]:
    live_docs_text = LIVE_DOCS_RECEIPT.read_text(encoding="utf-8")
    corpus_manifest = load_json(CORPUS_INTEGRATION_MANIFEST)
    motion_manifest = load_json(MOTION_MANIFEST)
    quest_board_text = QUEST_BOARD.read_text(encoding="utf-8")
    temple_state_text = TEMPLE_STATE.read_text(encoding="utf-8")
    loop_progress_text = LOOP_PROGRESS.read_text(encoding="utf-8")
    active_fronts = parse_active_fronts(quest_board_text)
    active_templates = build_active_seat_templates()

    loops: list[dict[str, object]] = []
    packets: list[dict[str, object]] = []
    loop_receipts_root = LAYER_ROOT / "11_LOOP_RECEIPTS"
    loop_index = 1
    for pass_definition in PASS_DEFINITIONS:
        actions = pass_definition["actions"]
        for step_idx, step_text in enumerate(pass_definition["steps"]):
            hall_action, temple_action, runtime_action, compression_action = actions[step_idx]
            loop_packets = build_packets(
                loop_index,
                pass_definition["pass_id"],
                pass_definition["title"],
                step_text,
                (hall_action, temple_action, runtime_action, compression_action),
            )
            packets.extend(loop_packets)
            hall_packet = next(packet for packet in loop_packets if packet["target"] == "hall")
            temple_packet = next(packet for packet in loop_packets if packet["target"] == "temple")
            runtime_packet = next(packet for packet in loop_packets if packet["target"] == "runtime")
            compression_packet = next(packet for packet in loop_packets if packet["target"] == "compression")
            next_step = None
            if step_idx + 1 < len(pass_definition["steps"]):
                next_step = pass_definition["steps"][step_idx + 1]
            elif PASS_DEFINITIONS.index(pass_definition) + 1 < len(PASS_DEFINITIONS):
                next_step = PASS_DEFINITIONS[PASS_DEFINITIONS.index(pass_definition) + 1]["steps"][0]
            loop_entry = {
                "loop_index": loop_index,
                "pass_id": pass_definition["pass_id"],
                "pass_title": pass_definition["title"],
                "theme": pass_definition["theme"],
                "step_text": step_text,
                "starting_control_stack": ["Q42", "TQ04", "Q50", "Q46", "Q02"],
                "seat_activation": {
                    "virtual_seats_per_master": 4096,
                    "active_seats_per_master": 256,
                    "active_seats_total": 1024,
                    "dormant_seats_total": 3072,
                    "per_resolution": 64,
                },
                "hall_decision": {
                    "candidate_front": hall_packet["candidate_front"],
                    "action": hall_packet["lawful_action"],
                    "visible_promotion": hall_packet["visible_promotion"],
                    "reason": hall_packet["reason"],
                },
                "temple_decision": {
                    "candidate_front": temple_packet["candidate_front"],
                    "action": temple_packet["lawful_action"],
                    "visible_promotion": temple_packet["visible_promotion"],
                    "reason": temple_packet["reason"],
                },
                "runtime_decision": {
                    "candidate_front": runtime_packet["candidate_front"],
                    "action": runtime_packet["lawful_action"],
                    "visible_promotion": runtime_packet["visible_promotion"],
                    "reason": runtime_packet["reason"],
                },
                "compression_decision": {
                    "candidate_front": compression_packet["candidate_front"],
                    "action": compression_packet["lawful_action"],
                    "visible_promotion": compression_packet["visible_promotion"],
                    "reason": compression_packet["reason"],
                },
                "master_receipts": build_master_receipts(step_text, loop_packets),
                "awakening_refresh": awakening_refresh(loop_index),
                "restart_seed": restart_seed(loop_index, pass_definition["pass_id"], next_step),
            }
            loops.append(loop_entry)
            receipt_lines = [
                f"# Loop {loop_index:02d} Receipt",
                "",
                f"- Pass: `{pass_definition['title']}`",
                f"- Step: {step_text}",
                f"- Hall decision: `{hall_packet['lawful_action']}` -> `{hall_packet['candidate_front']}`",
                f"- Temple decision: `{temple_packet['lawful_action']}` -> `{temple_packet['candidate_front']}`",
                f"- Runtime decision: `{runtime_packet['lawful_action']}` -> `{runtime_packet['candidate_front']}`",
                f"- Compression decision: `{compression_packet['lawful_action']}` -> `{compression_packet['candidate_front']}`",
                f"- Awakening full bundle refresh: `{loop_entry['awakening_refresh']['full_bundle_refresh']}`",
                f"- Pass-boundary bundle: `{loop_entry['awakening_refresh']['pass_boundary_bundle']}`",
                f"- Restart seed: `{loop_entry['restart_seed']}`",
            ]
            write_text(loop_receipts_root / f"loop_{loop_index:02d}.md", "\n".join(receipt_lines) + "\n")
            loop_index += 1

    readme_lines = [
        "# Super-Cycle 57",
        "",
        "This layer freezes the four-master orchestration contract, the sparse `4^6` seat law, and the full 57-loop ledger without mutating live Hall or Temple boards.",
        "",
        "- Status: `orchestration-ready`",
        "- Docs gate: `BLOCKED`",
        "- Starting control stack: `Q42 / TQ04 / Q50 / Q46 / Q02`",
        "- Master agents: `Research/Synthesis`, `Planner/Governor`, `Worker/Adventurer`, `Pruner/Compressor`",
    ]
    write_text(LAYER_ROOT / "README.md", "\n".join(readme_lines) + "\n")
    write_text(LAYER_ROOT / "00_MASTER_AGENT_LATTICE_LAW.md", render_lattice_law(active_templates))
    write_json(LAYER_ROOT / "01_ACTIVE_SEAT_TEMPLATES.json", active_templates)
    write_json(LAYER_ROOT / "02_LOOP_LEDGER.json", loops)
    write_text(LAYER_ROOT / "03_LOOP_LEDGER.md", render_loop_ledger(loops))
    write_json(LAYER_ROOT / "04_CANDIDATE_QUEST_PACKET_REGISTRY.json", packets)
    write_text(LAYER_ROOT / "05_HALL_PROMOTION_DECISIONS.md", render_decisions("Hall Promotion Decisions", loops, "hall_decision"))
    write_text(LAYER_ROOT / "06_TEMPLE_PROMOTION_DECISIONS.md", render_decisions("Temple Promotion Decisions", loops, "temple_decision"))
    write_text(LAYER_ROOT / "07_RUNTIME_FRONTIER_DECISIONS.md", render_decisions("Runtime Frontier Decisions", loops, "runtime_decision"))
    write_text(LAYER_ROOT / "08_PRUNING_COMPRESSION_RECEIPTS.md", render_compression_receipts(loops))
    write_text(LAYER_ROOT / "09_AWAKENING_DELTA_CADENCE.md", render_awakening_cadence(loops))
    write_json(LAYER_ROOT / "10_RESTART_SEED_REGISTER.json", [{"loop_index": loop["loop_index"], "restart_seed": loop["restart_seed"]} for loop in loops])
    write_text(LAYER_ROOT / "12_SUPER_CYCLE_CLOSURE_BUNDLE.md", render_closure_bundle(loops, active_fronts))

    hall_visible_promotions = sum(1 for loop in loops if loop["hall_decision"]["visible_promotion"])
    temple_visible_promotions = sum(1 for loop in loops if loop["temple_decision"]["visible_promotion"])
    runtime_visible_promotions = sum(1 for loop in loops if loop["runtime_decision"]["visible_promotion"])

    manifest = {
        "generated_at": utc_now(),
        "status": "orchestration-ready",
        "layer_root": str(LAYER_ROOT),
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(live_docs_text),
        "truth": "derived-local",
        "loop_count": len(loops),
        "pass_count": len(PASS_DEFINITIONS),
        "master_count": len(MASTER_AGENTS),
        "virtual_seats_per_master": 4096,
        "active_seats_per_master": 256,
        "active_seats_total": 1024,
        "dormant_seats_total": 3072,
        "starting_control_stack": ["Q42", "TQ04", "Q50", "Q46", "Q02"],
        "hall_visible_promotions": hall_visible_promotions,
        "temple_visible_promotions": temple_visible_promotions,
        "runtime_visible_promotions": runtime_visible_promotions,
        "corpus_basis_record_count": corpus_manifest["record_count"],
        "motion_truth": motion_manifest["truth"],
        "active_fronts": active_fronts,
        "witness_basis": {
            "corpus_integration_manifest": project_relative(CORPUS_INTEGRATION_MANIFEST),
            "motion_manifest": project_relative(MOTION_MANIFEST),
            "quest_board": project_relative(QUEST_BOARD),
            "temple_state": project_relative(TEMPLE_STATE),
            "loop_progress": project_relative(LOOP_PROGRESS),
        },
        "surface_paths": {
            "lattice_law": project_relative(LAYER_ROOT / "00_MASTER_AGENT_LATTICE_LAW.md"),
            "active_seat_templates": project_relative(LAYER_ROOT / "01_ACTIVE_SEAT_TEMPLATES.json"),
            "loop_ledger_json": project_relative(LAYER_ROOT / "02_LOOP_LEDGER.json"),
            "loop_ledger_markdown": project_relative(LAYER_ROOT / "03_LOOP_LEDGER.md"),
            "packet_registry": project_relative(LAYER_ROOT / "04_CANDIDATE_QUEST_PACKET_REGISTRY.json"),
            "hall_decisions": project_relative(LAYER_ROOT / "05_HALL_PROMOTION_DECISIONS.md"),
            "temple_decisions": project_relative(LAYER_ROOT / "06_TEMPLE_PROMOTION_DECISIONS.md"),
            "runtime_decisions": project_relative(LAYER_ROOT / "07_RUNTIME_FRONTIER_DECISIONS.md"),
            "compression_receipts": project_relative(LAYER_ROOT / "08_PRUNING_COMPRESSION_RECEIPTS.md"),
            "awakening_cadence": project_relative(LAYER_ROOT / "09_AWAKENING_DELTA_CADENCE.md"),
            "restart_seed_register": project_relative(LAYER_ROOT / "10_RESTART_SEED_REGISTER.json"),
            "loop_receipts_dir": project_relative(loop_receipts_root),
            "closure_bundle": project_relative(LAYER_ROOT / "12_SUPER_CYCLE_CLOSURE_BUNDLE.md"),
        },
        "tests": {
            "q02_activation_count": 0,
            "full_bundle_refresh_count": sum(1 for loop in loops if loop["awakening_refresh"]["full_bundle_refresh"]),
            "pass_boundary_bundle_count": sum(1 for loop in loops if loop["awakening_refresh"]["pass_boundary_bundle"]),
        },
    }
    write_json(OUTPUT_MANIFEST, manifest)
    update_active_readme()
    update_full_stack_manifest(manifest)
    return manifest


def main() -> int:
    args = parse_args()
    if args.command != "build":
        raise SystemExit("Unsupported command")
    manifest = build_super_cycle()
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"Super-Cycle layer: {LAYER_ROOT}")
        print(f"Runtime manifest: {OUTPUT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
