from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from self_actualize.runtime.derive_corpus_weave_ranking import (
    OUTPUT_JSON_PATH as RANKING_JSON_PATH,
    main as derive_corpus_weave_ranking_main,
)
from self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism import (
    CORPUS_ATLAS_PATH,
    CORPUS_ATLAS_SUMMARY_PATH,
    PHASE5_DERIVATION_COMMAND,
    SEMANTIC_MASS_LEDGER_PATH,
    WITNESS_HIERARCHY_PATH,
    collect_phase5_promotable_paths,
    load_json as phase5_load_json,
    refresh_corpus_atlas,
    render_corpus_atlas_summary,
)
from self_actualize.runtime.derive_q42_canonical_bundle import (
    OUTPUT_JSON_PATH as Q42_BUNDLE_JSON_PATH,
    main as derive_q42_canonical_bundle_main,
    q42_allowed_touched_paths,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
REPORTS_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "90_LEDGERS" / "automations"
RUN_JSON_PATH = SELF_ACTUALIZE_ROOT / "corpus_weave_run.json"
QSHRINK_ACTIVE_FRONT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
ACTIVE_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "NEXT_SELF_PROMPT.md"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
ATHENA_OS_CORRIDOR_MEMBRANE_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "manifests" / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
)
ATHENA_FLEET_ROUTE_MAP_PATH = NERVOUS_SYSTEM_ROOT / "families" / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = NERVOUS_SYSTEM_ROOT / "families" / "FAMILY_orgin_route_map.md"
WAVE_STATE_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_wave_state.json"
ATLAS_REGEN_RECEIPT_PATH = MYCELIUM_ROOT / "receipts" / "corpus_weave_atlas_regen_receipt.md"

AUTOMATION_ID = "corpus-weave"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")
TEXT_NORMALIZED_SUFFIXES = {
    ".json",
    ".md",
    ".py",
    ".text",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_now() -> datetime:
    return datetime.now(LOCAL_TIMEZONE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_text = normalize_text_for_comparison(text)
    existing = load_text(path) if path.exists() else None
    if existing is not None and normalize_text_for_comparison(existing) == normalized_text:
        return False
    path.write_text(normalized_text, encoding="utf-8")
    return True


def normalize_text_for_comparison(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n")).rstrip("\n")
    return f"{normalized}\n"


def relative_posix(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def absolute_from_relative(relative_path: str) -> Path:
    return WORKSPACE_ROOT / Path(relative_path.replace("\\", "/"))


def display_path(path_value: str) -> str:
    candidate = Path(path_value)
    if candidate.is_absolute():
        try:
            return relative_posix(candidate)
        except ValueError:
            return path_value.replace("\\", "/")
    return path_value.replace("\\", "/")


def surface_is_textual(path: Path) -> bool:
    return path.suffix.lower() in TEXT_NORMALIZED_SUFFIXES


def surface_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    if surface_is_textual(path):
        payload = normalize_text_for_comparison(load_text(path)).encode("utf-8")
    else:
        payload = path.read_bytes()
    return hashlib.sha256(payload).hexdigest()


def snapshot_surface_hashes(relative_paths: list[str]) -> dict[str, str | None]:
    return {
        path: surface_hash(absolute_from_relative(path))
        for path in sorted(set(relative_paths))
    }


def controlled_surface_paths() -> list[str]:
    return sorted(
        {
            *q42_allowed_touched_paths(),
            relative_posix(CORPUS_ATLAS_PATH),
            relative_posix(CORPUS_ATLAS_SUMMARY_PATH),
            relative_posix(ATLAS_REGEN_RECEIPT_PATH),
            relative_posix(WAVE_STATE_PATH),
        }
    )


def compute_actual_touched_paths(
    pre_run_hashes: dict[str, str | None],
    final_hashes: dict[str, str | None],
) -> list[str]:
    return sorted(
        path
        for path in final_hashes
        if final_hashes.get(path) != pre_run_hashes.get(path)
    )


def compute_transient_touched_paths(
    pre_run_hashes: dict[str, str | None],
    intermediate_hashes: list[dict[str, str | None]],
    final_hashes: dict[str, str | None],
) -> list[str]:
    transient: list[str] = []
    for path in final_hashes:
        baseline = pre_run_hashes.get(path)
        if final_hashes.get(path) != baseline:
            continue
        if any(snapshot.get(path) != baseline for snapshot in intermediate_hashes):
            transient.append(path)
    return sorted(transient)


def extract_block(text: str, header: str) -> str:
    pattern = re.compile(rf"(?ms)^{re.escape(header)}\n(?P<body>.*?)(?=^### |\Z)")
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Could not locate block: {header}")
    return match.group("body").rstrip()


def replace_block(text: str, header: str, body: str) -> str:
    pattern = re.compile(rf"(?ms)^{re.escape(header)}\n.*?(?=^### |\Z)")
    replacement = f"{header}\n{body.rstrip()}\n"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace block: {header}")
    return updated


def replace_header_block(
    text: str,
    header_pattern: str,
    header_line: str,
    body: str,
) -> str:
    pattern = re.compile(rf"(?ms)^(?:{header_pattern})\n.*?(?=^### |\Z)")
    replacement = f"{header_line}\n{body.rstrip()}\n"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace block matching: {header_pattern}")
    return updated


def render_backticked_lines(values: list[str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}`{value}`" for value in values)


def render_q42_quest_block(bundle: dict[str, Any]) -> str:
    hall = bundle["hall_contract"]
    return "\n".join(
        [
            "",
            "- Objective:",
            f"  {hall['objective']}",
            "- Why now:",
            f"  {hall['why_now']}",
            "- Active subfront:",
            f"  `{bundle['active_subfront']}`",
            "- Target surfaces:",
            render_backticked_lines(hall["target_surfaces"]),
            "- Witness needed:",
            f"  {hall['witness_needed']}",
            "- Writeback:",
            f"  {hall['writeback']}",
            "- Restart seed:",
            f"  {hall['restart_seed']}",
            "- Completion evidence:",
            render_backticked_lines(hall["completion_evidence"]),
            "",
        ]
    )


def render_q42_active_queue_block(bundle: dict[str, Any]) -> str:
    hall = bundle["hall_contract"]
    return "\n".join(
        [
            "",
            "- Quest:",
            f"  `Q42: {bundle['front_title']}`",
            "- State:",
            f"  `{hall['state']}`",
            "- Truth:",
            f"  `{hall['truth']}`",
            "- Objective:",
            f"  {hall['objective']}",
            "- Why Now:",
            f"  {hall['why_now']}",
            "- Active subfront:",
            f"  `{bundle['active_subfront']}`",
            "- Targets:",
            render_backticked_lines(hall["target_surfaces"]),
            "- Writeback:",
            f"  {hall['writeback']}",
            "- Next Seed:",
            f"  {hall['restart_seed']}",
            "",
        ]
    )


def render_q42_active_front(bundle: dict[str, Any]) -> str:
    hall = bundle["hall_contract"]
    selected = bundle["selected_pressure"]
    queued = bundle["queued_follow_on"]
    blocker = bundle["pinned_blocker"]
    return "\n".join(
        [
            "# QSHRINK ACTIVE FRONT",
            "",
            "## FrontID",
            "",
            f"`{bundle['front_id']}`",
            "",
            "## Quest",
            "",
            bundle["front_title"],
            "",
            "## State",
            "",
            f"`{hall['state']}`",
            "",
            "## Truth",
            "",
            f"`{hall['truth']}`",
            "",
            "## Objective",
            "",
            hall["objective"],
            "",
            "## Why Now",
            "",
            hall["why_now"],
            "",
            "## Active Subfront",
            "",
            f"`{bundle['active_subfront']}`",
            "",
            "## Next Seed",
            "",
            f"`{bundle['next_seed']}`",
            "",
            "## Contract Gate",
            "",
            f"`{bundle['deeper_receiving_frontier']}`",
            "",
            "## Pressure Order",
            "",
            f"- current: `{selected['id']} {selected['body']}` / `{selected['selection_state']}`",
            f"- queue-visible: `{queued['id']} {queued['body']}` / `{queued['selection_state']}`",
            f"- external blocker: `{blocker['id']} {blocker['body']}` / `{blocker['selection_state']}`",
            "",
        ]
    )


def render_q42_next_self_prompt(bundle: dict[str, Any]) -> str:
    hall = bundle["hall_contract"]
    selected = bundle["selected_pressure"]
    queued = bundle["queued_follow_on"]
    blocker = bundle["pinned_blocker"]
    docs_gate = bundle["docs_gate_status"]
    return "\n".join(
        [
            "# Next Self Prompt",
            "",
            "## Current Restart Seed",
            "",
            hall["restart_seed"],
            "",
            "## Prompt",
            "",
            "```text",
            "You are continuing the Athena nervous-system build in recursive swarm mode.",
            "",
            "1. Check the live Docs gate first.",
            f"2. If the gate is `{docs_gate['state']}`, preserve the blocker exactly and pivot to the strongest local executable frontier.",
            f"3. Treat `Q42 -> {bundle['active_subfront']}` as the current Hall-side corridor pass.",
            f"4. Treat `{bundle['next_seed']}` as the next Hall seed only, not the live pass.",
            f"5. Keep `{bundle['deeper_receiving_frontier']}` separate as the deeper receiving frontier.",
            f"6. Preserve `{selected['id']} {selected['body']}` as `{selected['selection_state']}`.",
            f"7. Preserve `{queued['id']} {queued['body']}` as `{queued['selection_state']}` behind the runtime-first law.",
            f"8. Keep `{blocker['id']} {blocker['body']}` external while Docs stays `{docs_gate['state']}`.",
            "9. Emit one artifact-backed move before ending the pass.",
            "10. If state changes, refresh the canonical Q42 corridor bundle before reporting the pass.",
            "```",
            "",
        ]
    )


def render_q42_corridor_membrane(bundle: dict[str, Any]) -> str:
    runtime_rail = bundle["runtime_rail"]
    return "\n".join(
        [
            "# ATHENA OS QSHRINK CORRIDOR MEMBRANE",
            "",
            f"Truth: `{runtime_rail['truth_state']}`",
            "",
            "## Corridor",
            "",
            f"- corridor id: `{runtime_rail['corridor_id']}`",
            f"- source body id: `{runtime_rail['source_body_id']}`",
            f"- current owner-facing subfront: `{runtime_rail['current_owner_facing_subfront']}`",
            f"- selected pressure: `{runtime_rail['selected_pressure']['id']} {runtime_rail['selected_pressure']['body']}`",
            f"- target runtime surface: `{runtime_rail['target_runtime_surface']}`",
            f"- writeback surface: `{runtime_rail['writeback_surface']}`",
            f"- next seed: `{runtime_rail['next_seed']}`",
            f"- deeper receiving frontier: `{runtime_rail['deeper_receiving_frontier']}`",
            "",
            "## Witness basis",
            "",
            render_backticked_lines(runtime_rail["witness_basis"], indent="- "),
            "",
            "## Note",
            "",
            runtime_rail["note"],
            "",
        ]
    )


def render_q42_athena_fleet_route_map(bundle: dict[str, Any]) -> str:
    route = bundle["route_contract"]["athena_fleet"]
    return "\n".join(
        [
            "# FAMILY Athena FLEET Route Map",
            "",
            "## Intake",
            "",
            render_backticked_lines(route["intake"], indent="- "),
            "",
            "## Main transfer",
            "",
            f"`{route['main_transfer']}`",
            "",
            "Governance overlay:",
            "",
            f"`{route['governance_overlay']}`",
            "",
            "## Law",
            "",
            *[f"- {line}" for line in route["law"]],
            "",
            "## Next route",
            "",
            f"`{route['next_route']}`",
            "",
            "## Separate Deeper Frontier",
            "",
            f"`{route['separate_deeper_frontier']}`",
            "",
        ]
    )


def render_q42_orgin_route_map(bundle: dict[str, Any]) -> str:
    route = bundle["route_contract"]["orgin"]
    return "\n".join(
        [
            "# FAMILY ORGIN Route Map",
            "",
            "## Intake",
            "",
            render_backticked_lines(route["intake"], indent="- "),
            "",
            "## Main transfer",
            "",
            f"`{route['main_transfer']}`",
            "",
            "## Law",
            "",
            *[f"- {line}" for line in route["law"]],
            "",
            "## Next route",
            "",
            f"`{route['next_route']}`",
            "",
        ]
    )


def render_q42_receipt(bundle: dict[str, Any]) -> str:
    hall = bundle["hall_contract"]
    docs_gate = bundle["docs_gate_status"]
    receipt_stem = Path(bundle["receipt_path"]).stem.replace("_", " ")
    missing_files = docs_gate.get("missing_files", [])
    docs_block = ["none"] if not missing_files else [f"`{path}`: `MISSING`" for path in missing_files]
    return "\n".join(
        [
            f"# {receipt_stem}",
            "",
            "- truth: `OK`",
            f"- docs gate: `{docs_gate['state']}`",
            f"- hall frontier: `{bundle['front_id']}`",
            f"- active subfront: `{bundle['active_subfront']}`",
            f"- next seed: `{bundle['next_seed']}`",
            f"- deeper frontier: `{bundle['deeper_receiving_frontier']}`",
            "",
            "## Docs gate truth",
            "",
            *[f"- {line}" for line in docs_block],
            *(
                ["- live Docs access remains blocked, so this pass is local-only and does not claim Google Docs witness"]
                if docs_gate["state"] == "BLOCKED"
                else ["- live Docs access is open"]
            ),
            "",
            "## Authoritative witness basis",
            "",
            f"- `{relative_posix(Q42_BUNDLE_JSON_PATH)}`",
            f"- `{display_path(bundle['source_paths']['qshrink_task_matrix'])}`",
            f"- `{display_path(bundle['source_paths']['q42_runtime_corridor_membrane'])}`",
            f"- `{display_path(bundle['source_paths']['q42_orgin_seed_packet_witness'])}`",
            "",
            "## Canonical post-pass state",
            "",
            f"- `{bundle['active_subfront']}` is the current owner-facing `Q42` subfront",
            f"- `{bundle['next_seed']}` is the next Hall seed and not the live pass",
            f"- `{bundle['selected_pressure']['id']} {bundle['selected_pressure']['body']}` remains PROMOTED_CURRENT",
            f"- `{bundle['queued_follow_on']['id']} {bundle['queued_follow_on']['body']}` remains QUEUE_VISIBLE",
            f"- `{bundle['deeper_receiving_frontier']}` remains the deeper receiving frontier",
            "",
            "## Corridor bundle",
            "",
            *[f"- `{path}`" for path in bundle["allowed_touched_paths"]],
            "",
            "## Honest residual",
            "",
            f"- Docs gate remains `{docs_gate['state']}` until OAuth material exists",
            "- raw witness JSONs stayed read-only in this pass",
            f"- `{bundle['deeper_receiving_frontier']}` remains separate and was not executed here",
            "",
            "## Restart seed",
            "",
            hall["restart_seed"],
            "",
        ]
    )


def load_q42_bundle() -> dict[str, Any]:
    derive_q42_canonical_bundle_main()
    return load_json(Q42_BUNDLE_JSON_PATH)


def sync_q42_quest_board(bundle: dict[str, Any]) -> bool:
    text = load_text(QUEST_BOARD_PATH)
    updated = replace_header_block(
        text,
        r"### Quest Q42: .+? `\[(?:OPEN|BLOCKED|PROMOTED(?: [^\]]+)?)\]`",
        bundle["hall_contract"]["front_header"],
        render_q42_quest_block(bundle),
    )
    return write_if_changed(QUEST_BOARD_PATH, updated)


def sync_q42_active_queue(bundle: dict[str, Any]) -> bool:
    text = load_text(ACTIVE_QUEUE_PATH)
    rendered_block = render_q42_active_queue_block(bundle).rstrip()
    current_block = extract_block(text, bundle["hall_contract"]["active_queue_header"])
    if normalize_text_for_comparison(current_block) == normalize_text_for_comparison(rendered_block):
        return False
    updated = replace_block(
        text,
        bundle["hall_contract"]["active_queue_header"],
        rendered_block,
    )
    return write_if_changed(ACTIVE_QUEUE_PATH, updated)


def sync_q42_active_front(bundle: dict[str, Any]) -> bool:
    return write_if_changed(QSHRINK_ACTIVE_FRONT_PATH, render_q42_active_front(bundle))


def sync_q42_next_self_prompt(bundle: dict[str, Any]) -> bool:
    rendered = render_q42_next_self_prompt(bundle)
    current = load_text(NEXT_SELF_PROMPT_PATH) if NEXT_SELF_PROMPT_PATH.exists() else ""
    if normalize_text_for_comparison(current) == normalize_text_for_comparison(rendered):
        return False
    return write_if_changed(NEXT_SELF_PROMPT_PATH, rendered)


def sync_q42_corridor_membrane(bundle: dict[str, Any]) -> bool:
    return write_if_changed(
        ATHENA_OS_CORRIDOR_MEMBRANE_MD_PATH,
        render_q42_corridor_membrane(bundle),
    )


def sync_q42_athena_fleet_route_map(bundle: dict[str, Any]) -> bool:
    return write_if_changed(
        ATHENA_FLEET_ROUTE_MAP_PATH,
        render_q42_athena_fleet_route_map(bundle),
    )


def sync_q42_orgin_route_map(bundle: dict[str, Any]) -> bool:
    return write_if_changed(ORGIN_ROUTE_MAP_PATH, render_q42_orgin_route_map(bundle))


def sync_q42_receipt(bundle: dict[str, Any]) -> bool:
    receipt_path = absolute_from_relative(bundle["receipt_path"])
    return write_if_changed(receipt_path, render_q42_receipt(bundle))


def handle_q42_sync(_: dict[str, Any]) -> tuple[str, list[str]]:
    bundle = load_q42_bundle()
    changed: list[str] = []
    writers: list[tuple[Path, Callable[[dict[str, Any]], bool]]] = [
        (QUEST_BOARD_PATH, sync_q42_quest_board),
        (ACTIVE_QUEUE_PATH, sync_q42_active_queue),
        (QSHRINK_ACTIVE_FRONT_PATH, sync_q42_active_front),
        (NEXT_SELF_PROMPT_PATH, sync_q42_next_self_prompt),
        (ATHENA_OS_CORRIDOR_MEMBRANE_MD_PATH, sync_q42_corridor_membrane),
        (ATHENA_FLEET_ROUTE_MAP_PATH, sync_q42_athena_fleet_route_map),
        (ORGIN_ROUTE_MAP_PATH, sync_q42_orgin_route_map),
    ]
    for path, writer in writers:
        if writer(bundle):
            changed.append(relative_posix(path))
    receipt_path = absolute_from_relative(bundle["receipt_path"])
    if sync_q42_receipt(bundle):
        changed.append(relative_posix(receipt_path))
    return "q42_sync", changed


def render_atlas_regen_receipt(
    ranking_payload: dict[str, Any],
    refresh_payload: dict[str, Any],
) -> str:
    winning_move = ranking_payload["winning_move"]
    promoted_count = len(refresh_payload.get("promoted_paths", []))
    updated_count = len(refresh_payload.get("updated_paths", []))
    promoted_sample = "\n".join(
        f"- `{path}`" for path in refresh_payload.get("promoted_paths", [])[:12]
    ) or "- none"
    return f"""# Corpus Weave Atlas Regen Receipt

- Generated: `{utc_now()}`
- Automation: `{AUTOMATION_ID}`
- Winning move: `{winning_move['id']} {winning_move['title']}`
- Report: `{ranking_payload['selected_report_path']}`
- Command: `{PHASE5_DERIVATION_COMMAND}` (refresh primitives only)

## Atlas Delta

- promoted paths: `{promoted_count}`
- updated paths: `{updated_count}`

## Promotion Sample

{promoted_sample}
"""


def handle_front_full_atlas_regen(ranking_payload: dict[str, Any]) -> tuple[str, list[str]]:
    before_atlas = load_text(CORPUS_ATLAS_PATH)
    before_summary = load_text(CORPUS_ATLAS_SUMMARY_PATH) if CORPUS_ATLAS_SUMMARY_PATH.exists() else ""
    before_receipt = load_text(ATLAS_REGEN_RECEIPT_PATH) if ATLAS_REGEN_RECEIPT_PATH.exists() else ""

    refresh_payload = refresh_corpus_atlas(
        collect_phase5_promotable_paths(include_phase5_outputs=False)
    )

    atlas = phase5_load_json(CORPUS_ATLAS_PATH)
    witness = (
        phase5_load_json(WITNESS_HIERARCHY_PATH)
        if WITNESS_HIERARCHY_PATH.exists()
        else {"witnesses": {}}
    )
    semantic = phase5_load_json(SEMANTIC_MASS_LEDGER_PATH) if SEMANTIC_MASS_LEDGER_PATH.exists() else {}
    witness_payload = copy.deepcopy(witness)
    witness_payload.setdefault("witnesses", {}).setdefault("indexed", {})["value"] = atlas.get(
        "record_count",
        0,
    )
    summary_text = render_corpus_atlas_summary(atlas, witness_payload, semantic)
    write_if_changed(CORPUS_ATLAS_SUMMARY_PATH, summary_text)
    write_if_changed(
        ATLAS_REGEN_RECEIPT_PATH,
        render_atlas_regen_receipt(ranking_payload, refresh_payload),
    )

    changed: list[str] = []
    if load_text(CORPUS_ATLAS_PATH) != before_atlas:
        changed.append(relative_posix(CORPUS_ATLAS_PATH))
    if load_text(CORPUS_ATLAS_SUMMARY_PATH) != before_summary:
        changed.append(relative_posix(CORPUS_ATLAS_SUMMARY_PATH))
    if load_text(ATLAS_REGEN_RECEIPT_PATH) != before_receipt:
        changed.append(relative_posix(ATLAS_REGEN_RECEIPT_PATH))
    return "front_full_atlas_regen", changed


def handle_q50_wave_handoff(ranking_payload: dict[str, Any]) -> tuple[str, list[str]]:
    payload = load_json(WAVE_STATE_PATH)
    desired = {
        "quest_front": "Q50",
        "wave_id": "Q50-wave7",
        "generated_at": utc_now(),
        "restart_seed": (
            "Q51 -> Wave8/ImmuneAppendix.Runtime.Fire.Diagnose"
            if ranking_payload["winning_move"]["title"].startswith(
                "Run The First Athenachka Helix Runtime Wave"
            )
            else ranking_payload["restart_seed"]
        ),
        "source_wave_id": payload.get("current_wave", {}).get("wave_id", ""),
        "target_surface": "ATHENA Neural Network/athenachka/helix/",
        "reason": ranking_payload["winning_move"]["rationale"],
    }
    existing = payload.get("next_wave_handoff")
    if existing == desired:
        return "q50_wave_handoff", []
    payload["next_wave_handoff"] = desired
    write_json(WAVE_STATE_PATH, payload)
    return "q50_wave_handoff", [relative_posix(WAVE_STATE_PATH)]


HANDLER_REGISTRY: dict[str, Callable[[dict[str, Any]], tuple[str, list[str]]]] = {
    "Q42": handle_q42_sync,
    "FRONT-FULL-ATLAS-REGEN": handle_front_full_atlas_regen,
    "Q50": handle_q50_wave_handoff,
}


def apply_writeback_handler(ranking_payload: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    winner = ranking_payload["winning_move"]
    allowed = set(ranking_payload.get("touched_paths_allowed", []))
    handler = HANDLER_REGISTRY.get(winner["id"])
    if handler is None:
        return "report_only", [], []
    try:
        handler_name, attempted_paths = handler(ranking_payload)
    except Exception as exc:
        return "report_only", [], [f"Handler `{winner['id']}` failed: {exc}"]
    unexpected = [path for path in attempted_paths if path not in allowed]
    if unexpected:
        return (
            "report_only",
            [],
            [
                "Handler "
                f"`{winner['id']}` touched paths outside the ranking allowlist: {', '.join(unexpected)}"
            ],
      )
    return handler_name, sorted(set(attempted_paths)), []


def render_docs_gate_section(docs_gate_status: dict[str, Any]) -> str:
    state = docs_gate_status.get("state", "UNKNOWN")
    lines = [f"`{state}`"]
    detail = docs_gate_status.get("detail", "")
    if state == "BLOCKED" and detail:
        lines.extend(["", "```text", detail, "```"])
    return "\n".join(lines)


def render_neglected_areas(entries: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"{entry['rank']}. `{entry['body']}` via `{entry['representative_candidate_id']}` (score `{entry['final_score']}`): {entry['rationale']}"
        for entry in entries
    )


def render_missing_bridges(entries: list[dict[str, Any]]) -> str:
    lines = []
    for entry in entries:
        lines.append(
            f"{entry['rank']}. `{entry['id']}` `{entry['title']}` on `{entry['anchor_body']}` "
            f"(score `{entry['final_score']}`, readiness `{entry['score_breakdown']['execution_readiness']}`): {entry['rationale']}"
        )
    return "\n".join(lines)


def render_winning_move(run_payload: dict[str, Any]) -> str:
    winner = run_payload["winning_move"]
    lines = [
        f"- `{winner['id']}` `{winner['title']}` on `{winner['anchor_body']}`",
        f"- score: `{winner['final_score']}`",
        f"- handler: `{run_payload['applied_handler']}`",
        f"- mode: `{'report-only' if run_payload['report_only'] else 'writeback'}`",
        f"- rationale: {winner['rationale']}",
    ]
    return "\n".join(lines)


def render_touched_paths(run_payload: dict[str, Any]) -> str:
    if not run_payload["actual_touched_paths"]:
        return "none"
    return "\n".join(f"- `{path}`" for path in run_payload["actual_touched_paths"])


def render_blockers(blockers: list[str]) -> str:
    if not blockers:
        return "none"
    return "\n".join(f"- {blocker}" for blocker in blockers)


def render_report_markdown(run_payload: dict[str, Any], title: str) -> str:
    timestamp = local_now().strftime("%Y-%m-%d %H:%M:%S %z")
    return "\n".join(
        [
            title,
            "",
            f"Date: `{timestamp}`",
            f"Automation id: `{AUTOMATION_ID}`",
            "",
            "## docs gate status",
            "",
            render_docs_gate_section(run_payload["docs_gate_status"]),
            "",
            "## neglected areas",
            "",
            render_neglected_areas(run_payload["neglected_areas"]),
            "",
            "## highest-yield missing bridges",
            "",
            render_missing_bridges(run_payload["missing_bridges"]),
            "",
            "## one concrete interconnection move",
            "",
            render_winning_move(run_payload),
            "",
            "## touched paths",
            "",
            render_touched_paths(run_payload),
            "",
            "## blockers",
            "",
            render_blockers(run_payload["blockers"]),
            "",
            "## restart seed",
            "",
            run_payload["restart_seed"],
            "",
        ]
    )


def build_run_payload(
    ranking_payload: dict[str, Any],
    applied_handler: str,
    actual_touched_paths: list[str],
    handler_blockers: list[str],
    surface_write_audit: dict[str, Any],
) -> dict[str, Any]:
    blockers = list(ranking_payload.get("blockers", [])) + handler_blockers
    report_only = not actual_touched_paths

    run_payload = {
        "generated_at": utc_now(),
        "ranking_path": relative_posix(RANKING_JSON_PATH),
        "selected_report_path": ranking_payload["selected_report_path"],
        "docs_gate_status": ranking_payload["docs_gate_status"],
        "neglected_areas": ranking_payload["neglected_areas"],
        "missing_bridges": ranking_payload["missing_bridges"],
        "winning_move": ranking_payload["winning_move"],
        "report_only": report_only,
        "allowed_touched_paths": ranking_payload.get("touched_paths_allowed", []),
        "actual_touched_paths": actual_touched_paths,
        "applied_handler": applied_handler,
        "blockers": blockers,
        "restart_seed": ranking_payload["restart_seed"],
        "surface_write_audit": surface_write_audit,
    }
    run_payload["report_markdown"] = render_report_markdown(
        run_payload,
        "# Corpus Weave Vishnu Report",
    )
    run_payload["inbox_markdown"] = render_report_markdown(
        run_payload,
        "# Corpus Weave Inbox",
    )
    return run_payload


def write_report(run_payload: dict[str, Any]) -> None:
    report_path = absolute_from_relative(run_payload["selected_report_path"])
    write_if_changed(report_path, run_payload["report_markdown"])


def execute_corpus_weave_run() -> dict[str, Any]:
    pre_all_hashes = snapshot_surface_hashes(controlled_surface_paths())
    derive_corpus_weave_ranking_main()
    ranking_payload = load_json(RANKING_JSON_PATH)
    allowed_paths = list(ranking_payload.get("touched_paths_allowed", []))
    pre_run_hashes = {path: pre_all_hashes.get(path) for path in allowed_paths}
    post_ranking_hashes = snapshot_surface_hashes(allowed_paths)
    applied_handler, attempted_paths, handler_blockers = apply_writeback_handler(ranking_payload)
    post_handler_hashes = snapshot_surface_hashes(allowed_paths)
    final_hashes = snapshot_surface_hashes(allowed_paths)
    actual_touched_paths = compute_actual_touched_paths(pre_run_hashes, final_hashes)
    transient_touched_paths = compute_transient_touched_paths(
        pre_run_hashes,
        [post_ranking_hashes, post_handler_hashes],
        final_hashes,
    )
    surface_write_audit = {
        "allowed_paths": sorted(set(allowed_paths)),
        "pre_run_hashes": pre_run_hashes,
        "post_ranking_hashes": post_ranking_hashes,
        "post_handler_hashes": post_handler_hashes,
        "final_hashes": final_hashes,
        "transient_touched_paths": transient_touched_paths,
    }
    run_payload = build_run_payload(
        ranking_payload,
        applied_handler,
        actual_touched_paths,
        handler_blockers,
        surface_write_audit,
    )
    write_report(run_payload)
    write_json(RUN_JSON_PATH, run_payload)
    return run_payload


def main() -> int:
    execute_corpus_weave_run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
