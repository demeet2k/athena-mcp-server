from __future__ import annotations

import json
from pathlib import Path
import re

from self_actualize.runtime.qshrink_refine_common import (
    ACTIVE_QUEUE_PATH,
    BLOCKED_EXTERNAL_FRONT,
    CHANGE_FEED_PATH,
    CURRENT_CARRIED_WITNESS,
    FRONT_ID,
    FRONT_TITLE,
    MYCELIUM_ROOT,
    NEXT_SELF_PROMPT_PATH,
    NEXT_TEMPLE_HANDOFF,
    PASS_IDS,
    QSHRINK_ACTIVE_FRONT_PATH,
    QSHRINK_AGENT_TASK_MATRIX_PATH,
    QSHRINK_LOOPED_PLAN_PATH,
    QSHRINK_NETWORK_INTEGRATION_PATH,
    QUEST_BOARD_PATH,
    RECEIPTS_ROOT,
    REQUESTS_BOARD_PATH,
    RESERVE_FRONTIER,
    SELF_ACTUALIZE_ROOT,
    TEMPLE_STATE_PATH,
    WORKSPACE_ROOT,
    docs_gate_payload,
    load_json,
    read_text,
    utc_now,
    write_json,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_refine_bundle_closure"
ACTIVE_LOCAL_SUBFRONT = PASS_IDS["fractal"]
NEXT_HALL_SEED = None
NEXT_HALL_SEED_DISPLAY = "none; do not invent QS64-25"
DRIFT_BASELINE_PATH = SELF_ACTUALIZE_ROOT / "q42_refine_bundle_drift_baseline.json"
DASHBOARD_PATH = SELF_ACTUALIZE_ROOT / "q42_refine_bundle_dashboard.json"
VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "q42_refine_bundle_verification.json"
CANONICAL_BUNDLE_PATH = SELF_ACTUALIZE_ROOT / "q42_canonical_bundle.json"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_q42_refine_bundle_closure.md"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
REGISTRY_DASHBOARD_PATH = REGISTRY_ROOT / "q42_refine_bundle_dashboard.json"
REGISTRY_VERIFICATION_PATH = REGISTRY_ROOT / "q42_refine_bundle_verification.json"


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_block(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"Start marker not found: {start_marker}")
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"End marker not found after {start_marker}: {end_marker}")
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


def surface_markers(text: str) -> dict[str, bool]:
    lower_text = text.lower()
    return {
        "qs64_20": CURRENT_CARRIED_WITNESS in text,
        "qs64_21": PASS_IDS["square"] in text,
        "qs64_22": PASS_IDS["flower"] in text,
        "qs64_23": PASS_IDS["cloud"] in text,
        "qs64_24": PASS_IDS["fractal"] in text,
        "tq04": NEXT_TEMPLE_HANDOFF in text,
        "q46": RESERVE_FRONTIER in text,
        "q02": BLOCKED_EXTERNAL_FRONT in text,
        "qs64_25_raw": "QS64-25" in text,
        "qs64_25_guard": "do not invent qs64-25" in lower_text,
    }


def collect_drift_baseline() -> dict:
    surfaces = {
        "quest_board": QUEST_BOARD_PATH,
        "active_queue": ACTIVE_QUEUE_PATH,
        "qshrink_active_front": QSHRINK_ACTIVE_FRONT_PATH,
        "looped_plan": QSHRINK_LOOPED_PLAN_PATH,
        "temple_state": TEMPLE_STATE_PATH,
        "next_self_prompt": NEXT_SELF_PROMPT_PATH,
    }
    states: dict[str, dict] = {}
    for name, path in surfaces.items():
        text = read_text(path)
        states[name] = {
            "path": relative_string(path),
            "markers": surface_markers(text),
            "excerpt": "\n".join(text.splitlines()[:24]),
        }

    mixed_state_sources = [
        name
        for name, state in states.items()
        if state["markers"]["qs64_21"] or state["markers"]["qs64_22"] or state["markers"]["qs64_23"]
    ]
    closed_bundle_sources = [
        name for name, state in states.items() if state["markers"]["qs64_24"] and state["markers"]["tq04"]
    ]
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate_payload(),
        "canonical_target": {
            "current_carried_witness": CURRENT_CARRIED_WITNESS,
            "active_local_subfront": ACTIVE_LOCAL_SUBFRONT,
            "next_hall_seed": NEXT_HALL_SEED,
            "next_hall_seed_display": NEXT_HALL_SEED_DISPLAY,
            "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        },
        "surface_states": states,
        "mixed_state_detected": bool(mixed_state_sources and closed_bundle_sources),
        "mixed_state_sources": mixed_state_sources,
        "closed_bundle_sources": closed_bundle_sources,
        "summary": "The March 13, 2026 drift is real when some live surfaces still present QS64-21..23 as current or next while other generator-owned surfaces already present QS64-24 as the closed Hall-local bundle.",
    }


def render_quest_board_q42() -> str:
    targets = [
        "self_actualize/qshrink_connectivity_refine_square.json",
        "self_actualize/qshrink_connectivity_refine_flower.json",
        "self_actualize/qshrink_connectivity_refine_cloud.json",
        "self_actualize/qshrink_connectivity_refine_fractal.json",
        "self_actualize/qshrink_network_integration.json",
        "self_actualize/qshrink_agent_task_matrix.json",
        "self_actualize/q42_canonical_bundle.json",
        "self_actualize/q42_refine_bundle_dashboard.json",
        "self_actualize/q42_refine_bundle_verification.json",
        "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
        "self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md",
        "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md",
        "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
        "self_actualize/mycelium_brain/receipts/2026-03-13_q42_refine_bundle_closure.md",
    ]
    target_lines = "\n".join(f"  `{item}`" for item in targets)
    evidence = "\n".join(
        f"  `{item}`"
        for item in [
            "self_actualize/qshrink_connectivity_refine_fractal.json",
            "self_actualize/qshrink_network_integration.json",
            "self_actualize/qshrink_agent_task_matrix.json",
            "self_actualize/q42_canonical_bundle.json",
            "self_actualize/q42_refine_bundle_dashboard.json",
            "self_actualize/q42_refine_bundle_verification.json",
            "self_actualize/mycelium_brain/receipts/2026-03-13_q42_refine_bundle_closure.md",
        ]
    )
    return "\n".join(
        [
            "### Quest Q42: Activate The First QSHRINK Agent Sweep `[OPEN]`",
            "",
            "- Objective:",
            f"  keep `{CURRENT_CARRIED_WITNESS}` visible as the carried diagnose witness, preserve `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keep `{RESERVE_FRONTIER}` reserve-only, keep `{BLOCKED_EXTERNAL_FRONT}` external, and treat generated refine witnesses plus verification sidecars as the canonical current state",
            "- Why now:",
            "  the four-pass Hall-local refine rail is already landed in witness form, but Hall and Temple control surfaces still need one final precedence-safe closure sweep so no active surface reopens `QS64-21..23` or invents `QS64-25`",
            "- Current carried witness:",
            f"  `{CURRENT_CARRIED_WITNESS}`",
            "- Active local subfront:",
            f"  `{ACTIVE_LOCAL_SUBFRONT}`",
            "- Next Hall seed:",
            f"  `{NEXT_HALL_SEED_DISPLAY}`",
            "- Next Temple handoff:",
            f"  `{NEXT_TEMPLE_HANDOFF}`",
            "- Target surfaces:",
            target_lines,
            "- Witness needed:",
            "  one explicit mixed-state drift baseline, one precedence-safe closure sweep, one aligned Hall/Temple/queue/restart bundle, one receipt proving no Hall-local `QS64-25`, and one truthful carrythrough of landed `TQ04` plus external `Q02`",
            "- Writeback:",
            "  Hall quest board, active queue, active-front manifest, Hall looped plan, next-self prompt, Temple state, change feed, requests board, sidecar dashboards, and receipt",
            "- Restart seed:",
            f"  keep `Q42` open as the umbrella frontier, keep `{CURRENT_CARRIED_WITNESS}` visible as carried witness, keep `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local bundle, hand immediate deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keep `{RESERVE_FRONTIER}` reserve-only, emit no Hall-local `QS64-25`, and keep `{BLOCKED_EXTERNAL_FRONT}` blocked externally while Docs remains `BLOCKED`",
            "- Completion evidence:",
            evidence,
        ]
    )


def render_active_queue_q42() -> str:
    return "\n".join(
        [
            "### FRONT-Q42-QSHRINK-AGENT-SWEEP",
            "",
            "- Quest:",
            f"  `{FRONT_ID}: {FRONT_TITLE}`",
            "- State:",
            "  `OPEN`",
            "- Truth:",
            "  `OK`",
            "- Objective:",
            f"  keep `{CURRENT_CARRIED_WITNESS}` visible as the carried diagnose witness under `{FRONT_ID}`, preserve `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keep `{RESERVE_FRONTIER}` reserve-only, and keep the blocked Docs gate external as `{BLOCKED_EXTERNAL_FRONT}`",
            "- Why Now:",
            "  the local refine bundle is already landed, so the honest move is freshness repair and handoff clarity across Hall, queue, route, membrane, and Temple surfaces without inventing `QS64-25`",
            "- Current carried witness:",
            f"  `{CURRENT_CARRIED_WITNESS}`",
            "- Active local subfront:",
            f"  `{ACTIVE_LOCAL_SUBFRONT}`",
            "- Next Hall seed:",
            f"  `{NEXT_HALL_SEED_DISPLAY}`",
            "- Immediate deeper receiver:",
            f"  `{NEXT_TEMPLE_HANDOFF}`",
            "- Reserve frontier:",
            f"  `{RESERVE_FRONTIER}`",
            "- Blocked external front:",
            f"  `{BLOCKED_EXTERNAL_FRONT}`",
            "- Witness:",
            "  one explicit drift baseline, one aligned closure bundle, one receipt proving no Hall-local `QS64-25`, and one blocker-honest handoff to landed `TQ04`",
            "- Writeback:",
            "  quest board, temple state, change feed, active queue, next-self prompt, active-front manifest, and receipt",
            "- Next Seed:",
            f"  keep `{FRONT_ID}` open as the umbrella frontier, keep `{CURRENT_CARRIED_WITNESS}` visible as carried witness, keep `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local bundle, hand immediate deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keep `{RESERVE_FRONTIER}` reserve-only, emit no Hall-local `QS64-25`, and keep `{BLOCKED_EXTERNAL_FRONT}` blocked externally",
            "- Latest Witness:",
            f"  `{relative_string(RECEIPT_PATH)}` now keeps Hall, Temple, queue, route, and restart surfaces aligned on `{CURRENT_CARRIED_WITNESS}` as carried witness, `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local bundle, `{NEXT_TEMPLE_HANDOFF}` as the immediate deeper receiver, and `{RESERVE_FRONTIER}` as reserve-only while both OAuth files remain honestly missing",
        ]
    )


def render_next_prompt() -> str:
    return "\n".join(
        [
            "# Next Self Prompt",
            "",
            "## Current Restart Seed",
            "",
            f"keep `{FRONT_ID}` open as the umbrella frontier, keep `{CURRENT_CARRIED_WITNESS}` visible as carried diagnose witness, keep `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keep `{RESERVE_FRONTIER}` reserve-only, emit no Hall-local `QS64-25`, treat generated refine witnesses plus verification sidecars as canonical current state, and keep `{BLOCKED_EXTERNAL_FRONT}` externally blocked while Docs remains `BLOCKED`",
            "",
            "## Prompt",
            "",
            "```text",
            "You are continuing the Athena nervous-system build in recursive swarm mode.",
            "",
            "1. Check the live Docs gate first.",
            "2. If blocked, preserve the blocker exactly and pivot to the strongest local executable frontier.",
            f"3. Treat {CURRENT_CARRIED_WITNESS} as the carried diagnose witness, not as a fresh Hall-local seed.",
            f"4. Treat {ACTIVE_LOCAL_SUBFRONT} as the closed Hall-local NEXT^4 bundle marker.",
            f"5. Hand immediate deeper execution to {NEXT_TEMPLE_HANDOFF}.",
            f"6. Keep {RESERVE_FRONTIER} reserve-only and keep {BLOCKED_EXTERNAL_FRONT} external while Docs stays BLOCKED.",
            "7. Do not invent QS64-25.",
            "8. Keep the control fields separate: carried witness, active local subfront, next Hall seed, Temple handoff, reserve frontier, blocked external front.",
            "9. Treat generated refine witnesses plus verification sidecars as canonical state; treat change feed entries and receipts as witness history.",
            "10. Emit one artifact-backed move before ending the pass and refresh Hall, Temple, queue, and restart surfaces if state changes.",
            "```",
            "",
        ]
    )


def render_temple_state() -> str:
    return "\n".join(
        [
            "# Temple State",
            "",
            "Date: `2026-03-13`",
            "Last Run Stamp: `2026-03-13 America/Los_Angeles`",
            "Temple Status: `ONLINE`",
            "",
            "## FrontID",
            "",
            "`TQ06-GUILDMASTER-HOURLY-PACKET-COUPLING`",
            "",
            "## Quest",
            "",
            "`TQ06: Install The Packet-Fed Guildmaster Coupling Loop`",
            "",
            "## State",
            "",
            "`ACTIVE`",
            "",
            "## Truth",
            "",
            "`OK`",
            "",
            "## Active Lens",
            "",
            "- Packet vote: `Q41 / TQ06 x3`",
            "- Contraction minority: `Q42 x2`",
            "- NEXT^4 scope: `Q42 Hall-local refine bundle closed`",
            "- Mode: `hourly packet-fed control loop`",
            f"- Current carried Hall witness: `Q42 -> {CURRENT_CARRIED_WITNESS}`",
            f"- Active Hall-side local bundle marker: `Q42 -> {ACTIVE_LOCAL_SUBFRONT}`",
            f"- Next Hall restart seed: `{NEXT_HALL_SEED_DISPLAY}`",
            f"- Immediate deeper receiver: `{NEXT_TEMPLE_HANDOFF} [LANDED 2026-03-13]`",
            f"- Reserve frontier: `{RESERVE_FRONTIER}`",
            f"- External blocker: `{BLOCKED_EXTERNAL_FRONT}`",
            "- Legacy note: `T14` remains the founding short-cadence drift-closure law, and `T16` remains the active cadence-binding law",
            "",
            "## Objective",
            "",
            "Bind the High Priest totality pressure to a recurring hourly packet-fed Guildmaster loop that:",
            "",
            "1. rereads the whole organism",
            "2. keeps the carried Hall-side QSHRINK diagnose witness truthful",
            "3. preserves the closed Hall-local refine bundle without reopening earlier local passes",
            "4. preserves the landed Temple runner contract as the immediate deeper receiver",
            "5. keeps reserve and blocker fronts separate",
            "",
            "## Why Now",
            "",
            f"The TQ04 proof set exists on disk and the Hall-local refine rail is now closed on `{ACTIVE_LOCAL_SUBFRONT}`. The honest followthrough is no longer to release another Hall-local seed; the honest followthrough is to preserve `{CURRENT_CARRIED_WITNESS}` as carried witness, keep `{NEXT_TEMPLE_HANDOFF}` as the immediate deeper receiver, and prevent Hall, Temple, queue, and restart surfaces from reintroducing `QS64-21..23` as current or inventing `QS64-25`.",
            "",
            "## Witness",
            "",
            f"`TQ04` remains the landed contract witness through `self_actualize/helical_runner_contract.json`, while `{relative_string(RECEIPT_PATH)}` now proves the closure sweep that keeps Hall, Temple, queue, and restart surfaces on the same final Q42 control state.",
            "",
            "- the paired verifier exists at `self_actualize/helical_runner_contract_verification.json`",
            "- the human-readable contract surface now lives at `NERVOUS_SYSTEM/95_MANIFESTS/TQ04_HELICAL_RUNNER_CONTRACT.md`",
            f"- the current lane witness lives at `{relative_string(RECEIPT_PATH)}`",
            "",
            "## Current Blockers",
            "",
            "- live Google Docs gate still blocked by missing OAuth files",
            f"- `{BLOCKED_EXTERNAL_FRONT}` remains external and unresolved",
            f"- `{RESERVE_FRONTIER}` remains reserve-only and outside the immediate Temple receiver lane",
            "",
            "## Carried Fronts",
            "",
            "- `TQ05` remains the totality umbrella and its active contradiction band is externalized through `Q39`",
            "- `TQ06` remains the active hourly packet-fed coupling frontier",
            f"- `TQ04` remains the landed contract witness and immediate deeper receiver after `{ACTIVE_LOCAL_SUBFRONT}`",
            f"- `Q42` remains the Hall-side feeder on carried `{CURRENT_CARRIED_WITNESS}` plus closed `{ACTIVE_LOCAL_SUBFRONT}`",
            "",
            "## Hall Coupling Delta",
            "",
            "The Hall and Temple now share one live control story:",
            "",
            "- `Q41` remains the promoted synchronization membrane",
            "- `TQ06` remains active as the packet-fed coupling frontier",
            f"- `{CURRENT_CARRIED_WITNESS}` remains visible as the carried Hall diagnose witness",
            f"- `{ACTIVE_LOCAL_SUBFRONT}` remains the closed Hall-local NEXT^4 bundle",
            f"- `{NEXT_TEMPLE_HANDOFF}` remains the immediate deeper receiver",
            f"- `{RESERVE_FRONTIER}` remains reserve-only",
            f"- `{BLOCKED_EXTERNAL_FRONT}` remains externally blocked",
            f"- no Hall-local `QS64-25` is emitted",
            "",
            "## Restart Seed",
            "",
            f"`Keep TQ06 active as the hourly packet-fed coupling frontier, keep Q42 open as the umbrella Hall frontier, preserve {CURRENT_CARRIED_WITNESS} as carried witness, preserve {ACTIVE_LOCAL_SUBFRONT} as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to {NEXT_TEMPLE_HANDOFF}, keep {RESERVE_FRONTIER} reserve-only, emit no Hall-local QS64-25, and keep {BLOCKED_EXTERNAL_FRONT} externally blocked while the Docs gate remains BLOCKED.`",
            "",
        ]
    )


def render_receipt() -> str:
    return "\n".join(
        [
            "# Q42 Refine Bundle Closure Receipt",
            "",
            "Date: `2026-03-13`",
            "Truth: `OK`",
            "Docs gate: `BLOCKED`",
            "",
            "The Q42 Hall-local refine rail is now lawfully closed across live owner-facing surfaces.",
            "",
            f"- carried witness: `{CURRENT_CARRIED_WITNESS}`",
            f"- closed Hall-local bundle: `{ACTIVE_LOCAL_SUBFRONT}`",
            f"- next Hall seed: `{NEXT_HALL_SEED_DISPLAY}`",
            f"- immediate deeper receiver: `{NEXT_TEMPLE_HANDOFF}`",
            f"- reserve frontier: `{RESERVE_FRONTIER}`",
            f"- blocked external front: `{BLOCKED_EXTERNAL_FRONT}`",
            "",
            "Generated refine witnesses plus verification sidecars now outrank change feed and receipt prose as canonical current state. Change feed entries and receipts remain witness history only.",
            "",
        ]
    )


def build_dashboard(baseline: dict) -> dict:
    task_matrix = load_json(QSHRINK_AGENT_TASK_MATRIX_PATH, {})
    network = load_json(QSHRINK_NETWORK_INTEGRATION_PATH, {})
    canonical_bundle = load_json(CANONICAL_BUNDLE_PATH, {})
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "front_id": FRONT_ID,
        "front_title": FRONT_TITLE,
        "docs_gate": docs_gate_payload(),
        "control_plane_precedence": {
            "canonical_state": "generated refine witnesses plus verification sidecars",
            "historical_state": "change feed entries plus receipts",
            "temple_contract_canon": "TQ04 manifest/json/verifier/receipt bundle",
        },
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "active_local_subfront": ACTIVE_LOCAL_SUBFRONT,
        "next_hall_seed": NEXT_HALL_SEED,
        "next_hall_seed_display": NEXT_HALL_SEED_DISPLAY,
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "hall_local_bundle_closed": True,
        "source_paths": {
            "task_matrix": relative_string(QSHRINK_AGENT_TASK_MATRIX_PATH),
            "network_integration": relative_string(QSHRINK_NETWORK_INTEGRATION_PATH),
            "canonical_bundle": relative_string(CANONICAL_BUNDLE_PATH),
            "quest_board": relative_string(QUEST_BOARD_PATH),
            "active_queue": relative_string(ACTIVE_QUEUE_PATH),
            "active_front": relative_string(QSHRINK_ACTIVE_FRONT_PATH),
            "looped_plan": relative_string(QSHRINK_LOOPED_PLAN_PATH),
            "temple_state": relative_string(TEMPLE_STATE_PATH),
            "next_self_prompt": relative_string(NEXT_SELF_PROMPT_PATH),
            "drift_baseline": relative_string(DRIFT_BASELINE_PATH),
            "receipt": relative_string(RECEIPT_PATH),
        },
        "baseline_summary": {
            "mixed_state_detected": baseline["mixed_state_detected"],
            "mixed_state_sources": baseline["mixed_state_sources"],
            "closed_bundle_sources": baseline["closed_bundle_sources"],
        },
        "task_matrix_truth": task_matrix.get("truth", "NEAR"),
        "network_truth": network.get("truth", "NEAR"),
        "canonical_bundle_truth": canonical_bundle.get("truth", task_matrix.get("truth", "NEAR")),
    }


def verify_text_surface(path: Path) -> dict:
    text = read_text(path)
    markers = surface_markers(text)
    return {
        "path": relative_string(path),
        "markers": markers,
        "ok": (
            markers["qs64_20"]
            and markers["qs64_24"]
            and markers["tq04"]
            and markers["q46"]
            and markers["q02"]
            and (not markers["qs64_25_raw"] or markers["qs64_25_guard"])
        ),
    }


def build_verification() -> dict:
    task_matrix = load_json(QSHRINK_AGENT_TASK_MATRIX_PATH, {})
    network = load_json(QSHRINK_NETWORK_INTEGRATION_PATH, {})
    canonical_bundle = load_json(CANONICAL_BUNDLE_PATH, {})
    surfaces = {
        "quest_board": verify_text_surface(QUEST_BOARD_PATH),
        "active_queue": verify_text_surface(ACTIVE_QUEUE_PATH),
        "active_front": verify_text_surface(QSHRINK_ACTIVE_FRONT_PATH),
        "looped_plan": verify_text_surface(QSHRINK_LOOPED_PLAN_PATH),
        "temple_state": verify_text_surface(TEMPLE_STATE_PATH),
        "next_self_prompt": verify_text_surface(NEXT_SELF_PROMPT_PATH),
    }
    checks = {
        "docs_gate_blocked": docs_gate_payload()["status"] == "BLOCKED",
        "task_matrix_active_qs64_24": task_matrix.get("active_local_subfront") == ACTIVE_LOCAL_SUBFRONT,
        "task_matrix_next_seed_null": task_matrix.get("next_hall_seed") is None,
        "network_active_qs64_24": network.get("active_local_subfront") == ACTIVE_LOCAL_SUBFRONT,
        "network_next_seed_null": network.get("next_hall_seed") is None,
        "canonical_bundle_active_qs64_24": canonical_bundle.get("active_subfront") == ACTIVE_LOCAL_SUBFRONT,
        "canonical_bundle_next_seed_null": canonical_bundle.get("next_seed") is None,
        "surfaces_aligned": all(item["ok"] for item in surfaces.values()),
        "no_hall_local_qs64_25": all(
            (not item["markers"]["qs64_25_raw"]) or item["markers"]["qs64_25_guard"]
            for item in surfaces.values()
        ),
        "tq04_immediate_receiver_visible": all(item["markers"]["tq04"] for item in surfaces.values()),
        "q46_reserve_visible": all(item["markers"]["q46"] for item in surfaces.values()),
        "q02_external_visible": all(item["markers"]["q02"] for item in surfaces.values()),
    }
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if all(checks.values()) else "FAIL",
        "checks": checks,
        "surface_checks": surfaces,
        "expected_state": {
            "current_carried_witness": CURRENT_CARRIED_WITNESS,
            "active_local_subfront": ACTIVE_LOCAL_SUBFRONT,
            "next_hall_seed": NEXT_HALL_SEED,
            "next_hall_seed_display": NEXT_HALL_SEED_DISPLAY,
            "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
            "reserve_frontier": RESERVE_FRONTIER,
            "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        },
    }


def prepend_change_feed_entry(text: str, entry: str) -> str:
    match = re.search(r"^\s*(\d+)\.\s", text, re.M)
    next_number = int(match.group(1)) + 1 if match else 1
    block = f"{next_number}. {entry}\n"
    marker = "## Recent Structural Changes\n\n"
    if block in text:
        return text
    if marker not in text:
        raise ValueError("Change feed marker not found")
    return text.replace(marker, marker + block, 1)


def prepend_requests_this_pass(text: str, entry: str) -> str:
    section_split = text.split("## This Pass\n\n", 1)
    if len(section_split) != 2:
        raise ValueError("Requests board This Pass marker not found")
    head, tail = section_split
    numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\.\s", tail, re.M)]
    next_number = max(numbers) + 1 if numbers else 1
    line = f"{next_number}. {entry}\n"
    if line in tail:
        return text
    return head + "## This Pass\n\n" + line + tail


def main() -> int:
    baseline = collect_drift_baseline()
    write_json(DRIFT_BASELINE_PATH, baseline)

    quest_board_text = read_text(QUEST_BOARD_PATH)
    quest_board_text = replace_block(
        quest_board_text,
        "### Quest Q42: Activate The First QSHRINK Agent Sweep `[OPEN]`",
        "### Quest Q46: Run The First Athenachka Helix Contracts Wave `[OPEN]`",
        render_quest_board_q42(),
    )
    write_text(QUEST_BOARD_PATH, quest_board_text)

    active_queue_text = read_text(ACTIVE_QUEUE_PATH)
    active_queue_text = replace_block(
        active_queue_text,
        "### FRONT-Q42-QSHRINK-AGENT-SWEEP",
        "### FRONT-Q02-LIVE-DOCS",
        render_active_queue_q42(),
    )
    write_text(ACTIVE_QUEUE_PATH, active_queue_text)

    write_text(NEXT_SELF_PROMPT_PATH, render_next_prompt())
    write_text(TEMPLE_STATE_PATH, render_temple_state())

    change_feed_entry = (
        "Q42 refine-rail closure is now the canonical current state: generated refine witnesses plus "
        "verification sidecars now outrank change feed entries and receipts as active truth, Hall and "
        f"Temple surfaces now agree that `{CURRENT_CARRIED_WITNESS}` is carried witness, "
        f"`{ACTIVE_LOCAL_SUBFRONT}` is the closed Hall-local NEXT^4 bundle, `{NEXT_TEMPLE_HANDOFF}` "
        f"is the immediate deeper receiver, `{RESERVE_FRONTIER}` remains reserve-only, `{BLOCKED_EXTERNAL_FRONT}` "
        "remains external, and no Hall-local `QS64-25` is emitted."
    )
    write_text(CHANGE_FEED_PATH, prepend_change_feed_entry(read_text(CHANGE_FEED_PATH), change_feed_entry))

    requests_entry = (
        f"closed the Hall-local `Q42` NEXT^4 refine bundle by capturing the mixed-state drift baseline, "
        f"aligning Hall, Temple, queue, restart, and canonical bundle surfaces on `{CURRENT_CARRIED_WITNESS}` "
        f"as carried witness plus `{ACTIVE_LOCAL_SUBFRONT}` as the closed Hall-local bundle, handing immediate "
        f"deeper execution to `{NEXT_TEMPLE_HANDOFF}`, keeping `{RESERVE_FRONTIER}` reserve-only, and "
        f"explicitly forbidding Hall-local `QS64-25` while Docs remains blocked"
    )
    write_text(REQUESTS_BOARD_PATH, prepend_requests_this_pass(read_text(REQUESTS_BOARD_PATH), requests_entry))

    write_text(RECEIPT_PATH, render_receipt())

    dashboard = build_dashboard(baseline)
    verification = build_verification()
    write_json(DASHBOARD_PATH, dashboard)
    write_json(VERIFICATION_PATH, verification)
    write_json(REGISTRY_DASHBOARD_PATH, dashboard)
    write_json(REGISTRY_VERIFICATION_PATH, verification)

    print(f"Wrote {DRIFT_BASELINE_PATH}")
    print(f"Wrote {QUEST_BOARD_PATH}")
    print(f"Wrote {ACTIVE_QUEUE_PATH}")
    print(f"Wrote {NEXT_SELF_PROMPT_PATH}")
    print(f"Wrote {TEMPLE_STATE_PATH}")
    print(f"Wrote {CHANGE_FEED_PATH}")
    print(f"Wrote {REQUESTS_BOARD_PATH}")
    print(f"Wrote {RECEIPT_PATH}")
    print(f"Wrote {DASHBOARD_PATH}")
    print(f"Wrote {VERIFICATION_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
