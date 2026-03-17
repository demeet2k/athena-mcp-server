from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"
QUEST_PACKETS_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_quest_packets.json"
WAVE_STATE_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_wave_state.json"
HALL_DOC_PATH = HALL_ROOT / "13_ATHENACHKA_ORGANISM_V0_QUEST_CRYSTAL_256.md"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_bootstrap.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.runtime.questing import build_macro_quest_bundle  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _current_wave_view(wave_state: dict[str, object]) -> dict[str, object]:
    if "current_wave" in wave_state:
        return dict(wave_state["current_wave"])
    return {
        "quest_front": wave_state.get("wave_activation", {}).get("quest_front", "Q44"),
        "wave_id": wave_state.get("wave_activation", {}).get("wave_id", "Q44-wave1"),
        "wave_activation": wave_state.get("wave_activation", {}),
        "owner_proof": wave_state.get("owner_proof", {}),
        "packet_results": wave_state.get("packet_results", []),
        "replay_summary": wave_state.get("replay_summary", {}),
        "parity_summary": wave_state.get("parity_summary", {}),
        "crystal_summary": wave_state.get("crystal_summary", {}),
        "verdict": wave_state.get("verdict", "UNKNOWN"),
        "exact_failing_gate": wave_state.get("exact_failing_gate", ""),
        "restart_seed": wave_state.get("restart_seed", ""),
    }


def render_assignment_lines(wave_state: dict[str, object]) -> list[str]:
    current_wave = _current_wave_view(wave_state)
    packet_results = {
        item["quest_id"]: item
        for item in current_wave.get("packet_results", [])
    }
    lines = []
    for packet in current_wave.get("wave_activation", {}).get("assignments", []):
        result = packet_results.get(packet["quest_id"], {})
        status = result.get("wave_status", packet.get("wave_status", "ASSIGNED"))
        lines.append(
            f"- `{packet['quest_id']}` :: `{packet['owner_id']}` :: `{packet['execution_contract']}` :: witness=`{packet['witness_target']}` :: status=`{status}`"
        )
    return lines


def render_wave_history_lines(wave_state: dict[str, object]) -> list[str]:
    history = wave_state.get("wave_history", {})
    if not history:
        return []

    lines = ["## Archived Wave History", ""]
    for wave_id, entry in sorted(history.items()):
        lines.append(
            f"- `{wave_id}` :: quest=`{entry.get('quest_front', '')}` :: verdict=`{entry.get('verdict', 'UNKNOWN')}` :: restart_seed=`{entry.get('restart_seed', '')}`"
        )
    lines.append("")
    return lines


def render_proof_section(wave_state: dict[str, object]) -> list[str]:
    current_wave = _current_wave_view(wave_state)
    parity_summary = current_wave.get("parity_summary")
    replay_summary = current_wave.get("replay_summary")
    owner_summary = current_wave.get("wave_activation", {}).get("owner_summary")
    crystal_summary = current_wave.get("crystal_summary")
    layer_summary = current_wave.get("layer_summary")
    if not parity_summary and not replay_summary and not owner_summary and not crystal_summary:
        return []

    lines = [
        "## Current Wave Proof",
        "",
        f"- quest_front: `{current_wave.get('quest_front', '')}`",
        f"- wave_id: `{current_wave.get('wave_id', '')}`",
        f"- wave_title: `{current_wave.get('wave_activation', {}).get('wave_title', '')}`",
        f"- verdict: `{current_wave.get('verdict', 'UNKNOWN')}`",
    ]
    exact_failing_gate = current_wave.get("exact_failing_gate")
    if exact_failing_gate:
        lines.append(f"- exact_failing_gate: `{exact_failing_gate}`")
    if owner_summary:
        lines.extend(
            [
                f"- guildmaster_active_claims: `{owner_summary['guildmaster']['active_claims']}`",
                f"- elemental_pod_leads: `{owner_summary['elemental_pod_leads']['active_claims']}`",
                f"- controller_auditors: `{owner_summary['controller_auditors']['active_claims']}`",
                f"- verification_replay_stewards: `{owner_summary['verification_replay_stewards']['active_claims']}`",
                f"- appendix_service_stewards: `{owner_summary['appendix_service_stewards']['active_claims']}`",
            ]
        )
    if replay_summary:
        lines.extend(
            [
                f"- diagnose_packets_passed: `{replay_summary.get('diagnose_packets_passed', 0)}`",
                f"- refine_packets_stable: `{replay_summary.get('refine_packets_stable', 0)}`",
                f"- synthesize_packets_passed: `{replay_summary.get('synthesize_packets_passed', 0)}`",
                f"- truth_gate_passed: `{replay_summary.get('truth_gate_passed', False)}`",
            ]
        )
    if crystal_summary:
        whole_wave = crystal_summary.get("whole_wave", {})
        lines.extend(
            [
                f"- omega_mean: `{whole_wave.get('omega_mean', 0.0):.3f}`",
                f"- contradiction_count: `{whole_wave.get('contradiction_count', 0)}`",
                f"- born_coordinate_candidate_count: `{whole_wave.get('born_coordinate_candidate_count', 0)}`",
            ]
        )
    if layer_summary:
        lines.append(f"- layer_summary_kind: `{layer_summary.get('kind', 'unknown')}`")
        if layer_summary.get("kind") == "helix":
            lines.append(f"- loop_frequency_histogram: `{layer_summary.get('loop_frequency_histogram', {})}`")
            lines.append(f"- phase_coverage_summary: `{layer_summary.get('phase_coverage_summary', {})}`")
        elif layer_summary.get("kind") == "immune_appendix":
            lines.append(f"- truth_type_histogram: `{layer_summary.get('truth_type_histogram', {})}`")
            lines.append(f"- quarantine_count: `{layer_summary.get('quarantine_count', 0)}`")
        elif layer_summary.get("kind") == "core_runtime":
            lines.append(f"- module_invocation_fingerprint: `{layer_summary.get('module_invocation_fingerprint', [])}`")
            lines.append(f"- hypothesis_count_distribution: `{layer_summary.get('hypothesis_count_distribution', {})}`")
    if parity_summary:
        lines.extend(
            [
                f"- kernel_import_ok: `{parity_summary.get('kernel_import_ok', False)}`",
                f"- organism_import_ok: `{parity_summary.get('organism_import_ok', False)}`",
                f"- average_absolute_delta: `{parity_summary.get('average_absolute_delta', 0.0):.3f}`",
                f"- max_fast_hypotheses: `{parity_summary.get('max_fast_hypotheses', 0)}`",
                f"- max_full_hypotheses: `{parity_summary.get('max_full_hypotheses', 0)}`",
            ]
        )
        for benchmark_name, benchmark in parity_summary.get("benchmarks", {}).items():
            lines.append(
                f"- `{benchmark_name}` :: kernel=`{benchmark['kernel_accuracy']:.3f}` organism=`{benchmark['organism_accuracy']:.3f}` delta=`{benchmark['absolute_delta']:.3f}`"
            )
    lines.append("")
    return lines


def render_hall_doc(bundle: dict[str, object], wave_state: dict[str, object]) -> str:
    current_wave = _current_wave_view(wave_state)
    active_lines = []
    for packet in bundle["active_packets"][:16]:
        active_lines.append(
            f"- `{packet['quest_id']}` :: `{packet['address_a256_b256_c256_d256']}` :: `{packet['objective']}` :: axis_owner_class=`{packet['owner_class']}`"
        )
    assignment_lines = render_assignment_lines(wave_state)
    parked_lines = []
    for packet in bundle["parked_packets"][:16]:
        parked_lines.append(f"- `{packet['quest_id']}` :: `{packet['address_a256_b256_c256_d256']}`")

    return "\n".join(
        [
            "# Athenachka Organism v0 Quest Crystal 256",
            "",
            "This Hall surface binds the organism build to a sparse `256^4` quest-address membrane without pretending to materialize every agent.",
            "",
            "## Macro Quest",
            "",
            f"- QuestId: `{bundle['macro_quest']['quest_id']}`",
            f"- Title: {bundle['macro_quest']['title']}",
            f"- Objective: {bundle['macro_quest']['objective']}",
            "",
            "## Wave Stack",
            "",
            *[f"- `{wave}` :: {goal}" for wave, goal in bundle["macro_quest"]["waves"].items()],
            "",
            "## Sparse Agent Law",
            "",
            *[f"- `{key}` = `{value}`" for key, value in bundle["agent_policy"].items()],
            "",
            "## Current Live Wave",
            "",
            f"- quest_front: `{current_wave.get('quest_front', '')}`",
            f"- wave_id: `{current_wave.get('wave_id', '')}`",
            f"- wave_title: `{current_wave.get('wave_activation', {}).get('wave_title', '')}`",
            "",
            "## Active Slice",
            "",
            *active_lines,
            "",
            f"## {current_wave.get('wave_id', 'current-wave')} Assignment Overlay",
            "",
            *assignment_lines,
            "",
            "## Parked Frontier Slice",
            "",
            *parked_lines,
            "",
            *render_wave_history_lines(wave_state),
            "## Runtime State",
            "",
            f"- docs_gate_blocked: `{wave_state['docs_gate_blocked']}`",
            f"- active_packet_count: `{wave_state['active_packet_count']}`",
            f"- parked_packet_count: `{wave_state['parked_packet_count']}`",
            f"- queued_packet_count: `{wave_state['queued_packet_count']}`",
            f"- verdict: `{current_wave.get('verdict', 'UNKNOWN')}`",
            f"- restart_seed: `{current_wave.get('restart_seed', '')}`",
            "",
            *render_proof_section(wave_state),
        ]
    )


def render_receipt(bundle: dict[str, object], wave_state: dict[str, object], claim_id: str) -> str:
    current_wave = _current_wave_view(wave_state)
    return "\n".join(
        [
            "# 2026-03-13 Athenachka Organism v0 Bootstrap",
            "",
            "## Outcome",
            "",
            "Bootstrapped the first executable Athenachka Organism v0 through the preserved Athena kernel, the new organism package, and the live Guild Hall quest membrane.",
            "",
            "## Gate Honesty",
            "",
            "- Live Google Docs remained blocked because OAuth files are still missing.",
            f"- blocker surface: `{DOCS_GATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            "",
            "## Witness Artifacts",
            "",
            f"- `{QUEST_PACKETS_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            f"- `{WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            f"- `{HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            "",
            "## Sparse Agent Contract",
            "",
            f"- macro_quest: `{bundle['macro_quest']['quest_id']}`",
            f"- current_wave: `{current_wave.get('wave_id', '')}`",
            f"- active_claim_count: `{wave_state['active_packet_count']}`",
            f"- parked_frontier_count: `{wave_state['parked_packet_count']}`",
            f"- bootstrap_claim_id: `{claim_id}`",
            f"- verdict: `{current_wave.get('verdict', 'UNKNOWN')}`",
            f"- restart_seed: `{current_wave.get('restart_seed', '')}`",
        ]
    )


def main() -> int:
    bundle = build_macro_quest_bundle()
    current_wave = {
        "quest_front": bundle["wave_activation"]["quest_front"],
        "wave_id": bundle["wave_activation"]["wave_id"],
        "wave_activation": bundle["wave_activation"],
        "verdict": "READY",
        "restart_seed": bundle["wave_activation"]["restart_seed_on_success"],
    }
    wave_state = {
        "generated_at": utc_now(),
        "docs_gate_blocked": True,
        "active_packet_count": len(bundle["active_packets"]),
        "parked_packet_count": len(bundle["parked_packets"]),
        "queued_packet_count": len(bundle["queued_packets"]),
        "current_wave": current_wave,
        "wave_history": {},
    }

    write_json(QUEST_PACKETS_PATH, bundle)
    write_json(WAVE_STATE_PATH, wave_state)
    write_text(HALL_DOC_PATH, render_hall_doc(bundle, wave_state))

    claim = swarm_board.create_or_update_claim(
        agent="guildmaster",
        front="Q43",
        level="framework",
        output_target="; ".join(
            [
                QUEST_PACKETS_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
                WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
                HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            ]
        ),
        receipt=RECEIPT_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        status="active",
        message="Bootstrapped Athenachka Organism v0 into the Hall with sparse 256^4 quest addressing and replay-bearing writebacks.",
        paths=[
            QUEST_PACKETS_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        ],
    )
    swarm_board.create_note(
        agent="guildmaster",
        front="Q43",
        status="active",
        message="Organism v0 is now routed as a Hall quest membrane with 16 live claims, 64 parked packets, and blocked Docs gate honesty preserved.",
        paths=[
            QUEST_PACKETS_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        ],
    )
    swarm_board.refresh_board()
    write_text(RECEIPT_PATH, render_receipt(bundle, wave_state, claim.get("claim_id", "")))
    print(f"Wrote quest packets: {QUEST_PACKETS_PATH}")
    print(f"Wrote wave state: {WAVE_STATE_PATH}")
    print(f"Wrote hall doc: {HALL_DOC_PATH}")
    print(f"Wrote receipt: {RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
