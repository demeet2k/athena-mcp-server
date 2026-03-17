from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_crystal_remaster import (
    read_text,
    refresh_corpus_atlas,
    relative_string,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MANIFEST_ROOT = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS"
LEDGER_ROOT = NERVOUS_SYSTEM_ROOT / "90_LEDGERS"
RECEIPT_ROOT = MYCELIUM_ROOT / "receipts"

ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import (  # noqa: E402
    AgentProgressProfile,
    PhiEfficiencySnapshot,
    QuestOutcomeCredit,
    RewardTransform,
    RewardVector,
    RunOutcome,
)
from athenachka.runtime.reward_overlay import (  # noqa: E402
    build_mini_hive_charter,
    build_promotion_record,
    build_reward_steering_profile,
    distribute_credit,
    evaluate_reward_run,
    update_progress_profile,
)


DATE = "2026-03-13"
PROTOCOL_ID = "LP-57OMEGA"
FRONTIER_ID = "FRONT-NEXT-4-POW-6-57-CYCLE-SWARM"
TRUTH = "NEAR"
NEXT_SEED = "NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling"
REWARD_PROTOCOL_ID = "LP-57OMEGA-REWARD-V1"

STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_swarm_state.json"
MASTER_STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_loop_state_57.json"
MASTER_AGENT_STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_agent_state_57.json"
LATTICE_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_loop_shared_lattice_4096.json"
QUEST_JSON_PATH = SELF_ACTUALIZE_ROOT / "master_loop_public_quest_bundle_57.json"
NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "awakening_agent_transition_notes.json"
TRANSITION_ASSISTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_transition_assists.json"
LEGACY_REWARD_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "lp57_omega_run_reward_ledger.json"
LOOP_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "lp_57_prime_loop_cycle_records.json"
MASTER_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "lp_57_master_agent_ledger.json"
COORDINATE_STAMPS_PATH = SELF_ACTUALIZE_ROOT / "lp_57_liminal_coordinate_stamps.json"
QUEST_EMISSION_PATH = SELF_ACTUALIZE_ROOT / "lp_57_quest_emission_bundles.json"
DELTA_RECEIPT_PATH = SELF_ACTUALIZE_ROOT / "lp_57_loop_delta_receipts.json"
SWARM_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "four_agent_57_loop_verification.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
DOCS_CREDENTIALS_PATH = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
DOCS_TOKEN_PATH = WORKSPACE_ROOT / "Trading Bot" / "token.json"

AGENT_PROGRESS_PATH = SELF_ACTUALIZE_ROOT / "agent_progress_registry.json"
AGENT_REWARD_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "agent_reward_ledger.json"
PHI_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "phi_efficiency_ledger.json"
PROMOTION_QUEUE_PATH = SELF_ACTUALIZE_ROOT / "promotion_queue.json"
MINI_HIVE_CHARTERS_PATH = SELF_ACTUALIZE_ROOT / "mini_hive_charters.json"
RUN_EVALUATIONS_PATH = SELF_ACTUALIZE_ROOT / "reward_run_evaluations.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "lp57_reward_overlay_verification.json"

MANIFEST_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_REWARD_PROTOCOL.md"
DASHBOARD_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_REWARD_DASHBOARD.md"
PROMOTION_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PROMOTION_BOARD.md"
PHI_LEDGER_MD_PATH = LEDGER_ROOT / "LP_57_OMEGA_PHI_EFFICIENCY_LEDGER.md"
VERIFICATION_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_REWARD_VERIFICATION.md"
RECEIPT_MD_PATH = RECEIPT_ROOT / "2026-03-13_lp_57_omega_reward_overlay.md"
LP57_PROTOCOL_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
LP57_DASHBOARD_MD_PATH = MANIFEST_ROOT / "LP_57_OMEGA_PRIME_LOOP_DASHBOARD.md"

VERIFY_SCRIPT_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_lp57_reward_overlay.py"
MOTION_DERIVE_COMMAND = [sys.executable, "-m", "self_actualize.runtime.derive_motion_constitution_l1"]

REGISTRY_MIRRORS = {
    AGENT_PROGRESS_PATH: REGISTRY_ROOT / AGENT_PROGRESS_PATH.name,
    AGENT_REWARD_LEDGER_PATH: REGISTRY_ROOT / AGENT_REWARD_LEDGER_PATH.name,
    PHI_LEDGER_PATH: REGISTRY_ROOT / PHI_LEDGER_PATH.name,
    PROMOTION_QUEUE_PATH: REGISTRY_ROOT / PROMOTION_QUEUE_PATH.name,
    MINI_HIVE_CHARTERS_PATH: REGISTRY_ROOT / MINI_HIVE_CHARTERS_PATH.name,
    RUN_EVALUATIONS_PATH: REGISTRY_ROOT / RUN_EVALUATIONS_PATH.name,
    VERIFICATION_JSON_PATH: REGISTRY_ROOT / VERIFICATION_JSON_PATH.name,
}

ASSIST_BY_MASTER = {
    "A1": ["AP6D-WATER", "floating-agent-03"],
    "A2": ["AP6D-PRIME", "floating-agent-05"],
    "A3": ["AP6D-FIRE", "floating-agent-06"],
    "A4": ["AP6D-EARTH", "floating-agent-08"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(read_text(path))


def docs_gate_status() -> str:
    if not DOCS_CREDENTIALS_PATH.exists():
        return "blocked-by-missing-credentials"
    if not DOCS_TOKEN_PATH.exists():
        return "blocked-by-missing-token"
    return "open"


def coord_to_string(coord: dict[str, Any] | str) -> str:
    if isinstance(coord, str):
        return coord
    return "|".join(f"{key}={coord[key]}" for key in sorted(coord))


def reward_vector_from_legacy(row: dict[str, Any], docs_gate: str) -> RewardVector:
    deltas = row.get("metric_deltas", {})
    docs_honest = 1.0 if docs_gate.startswith("blocked") else 0.2
    return RewardVector(
        integration_gain=max(0.0, float(deltas.get("integration_delta", 0.0))),
        compression_gain=max(0.0, float(deltas.get("compression_delta", 0.0))),
        replay_gain=max(0.0, float(deltas.get("replay_delta", 0.0))),
        witness_gain=max(0.0, float(deltas.get("witness_delta", 0.0))),
        route_clarity_gain=max(0.0, float(deltas.get("route_clarity_delta", 0.0))),
        quest_closure_gain=1.0 if row.get("reward_status") == "APPLIED" else 0.0,
        blocker_honesty_gain=docs_honest,
        phi_efficiency_gain=max(0.0, min(1.0, float(row.get("net_gain", 0.0)))),
        regression_loss=max(0.0, -float(deltas.get("efficiency_delta", 0.0))),
        bloat_loss=max(0.0, -float(deltas.get("compression_delta", 0.0))),
        contradiction_increase=0.0,
        orphaned_node_loss=0.0,
        replay_break_loss=0.0 if row.get("replay_coverage_passed", False) else 1.0,
        control_surface_drift=0.0,
        unauthorized_activation_loss=0.0,
        docs_dishonesty_loss=0.0,
    )


def reward_transform_for_row(row: dict[str, Any]) -> RewardTransform:
    operator = row.get("reward_operator_id", "identity")
    if operator == "phi":
        return RewardTransform.PHI
    if operator == "double_phi":
        return RewardTransform.DOUBLE_PHI
    if operator == "phi_square":
        return RewardTransform.SQUARED
    return RewardTransform.BASE


def seed_profile(agent_id: str, parent_agent_id: str, master_agent_id: str, loop_origin: str, coordinate_stamp: str) -> AgentProgressProfile:
    return AgentProgressProfile(
        agent_id=agent_id,
        parent_agent_id=parent_agent_id,
        master_agent_id=master_agent_id,
        loop_origin=loop_origin,
        coordinate_stamp=coordinate_stamp,
    )


def ensure_profile(
    profiles: dict[str, AgentProgressProfile],
    *,
    agent_id: str,
    parent_agent_id: str,
    master_agent_id: str,
    loop_origin: str,
    coordinate_stamp: str,
) -> None:
    if agent_id in profiles:
        return
    profiles[agent_id] = seed_profile(agent_id, parent_agent_id, master_agent_id, loop_origin, coordinate_stamp)


def build_profile_registry() -> dict[str, AgentProgressProfile]:
    lattice = load_json(LATTICE_JSON_PATH)
    master_state = load_json(MASTER_AGENT_STATE_JSON_PATH)
    notes = load_json(NOTES_JSON_PATH).get("notes", [])
    profiles: dict[str, AgentProgressProfile] = {}

    for agent in master_state.get("agents", []):
        ensure_profile(
            profiles,
            agent_id=agent["master_agent_id"],
            parent_agent_id="",
            master_agent_id=agent["master_agent_id"],
            loop_origin="L01",
            coordinate_stamp=agent.get("active_front", "LP57"),
        )

    for note in notes:
        ensure_profile(
            profiles,
            agent_id=note["agent_id"],
            parent_agent_id="",
            master_agent_id="A2",
            loop_origin="L01",
            coordinate_stamp=note.get("coordinate_stamp", note["agent_id"]),
        )

    ensure_profile(
        profiles,
        agent_id="DOCS-GATE-01",
        parent_agent_id="",
        master_agent_id="A2",
        loop_origin="L01",
        coordinate_stamp="DOCS-GATE-BLOCKED",
    )

    for row in lattice.get("rows", []):
        stamp = coord_to_string(row.get("coordinate_stamp", {}))
        loop_origin = row.get("coordinate_stamp", {}).get("Ts", "L02")
        for master_id, binding in row.get("role_bindings", {}).items():
            ensure_profile(
                profiles,
                agent_id=binding["agent_tag"],
                parent_agent_id=master_id,
                master_agent_id=master_id,
                loop_origin=loop_origin,
                coordinate_stamp=stamp,
            )
    return profiles


def build_loop_bonus_evaluation(loop_id: str) -> RewardRunEvaluation:
    vector = RewardVector(
        integration_gain=0.22,
        compression_gain=0.18,
        replay_gain=0.2,
        witness_gain=0.18,
        route_clarity_gain=0.16,
        quest_closure_gain=0.5,
        blocker_honesty_gain=0.35,
        phi_efficiency_gain=0.24,
    )
    return evaluate_reward_run(
        run_id=f"RR::LOOP::{loop_id}",
        scope="loop",
        loop_id=loop_id,
        agent_ids=["A1", "A2", "A3", "A4"],
        baseline_snapshot_ref=f"SNAP::{loop_id}::loop::pre",
        post_snapshot_ref=f"SNAP::{loop_id}::loop::post",
        reward_vector=vector,
        reward_transform=RewardTransform.BASE,
        residuals=[],
        truth=TRUTH,
    )


def build_frontier_bonus_evaluation() -> RewardRunEvaluation:
    vector = RewardVector(
        integration_gain=0.28,
        compression_gain=0.12,
        replay_gain=0.24,
        witness_gain=0.24,
        route_clarity_gain=0.2,
        quest_closure_gain=0.16,
        blocker_honesty_gain=0.5,
        phi_efficiency_gain=0.3,
    )
    return evaluate_reward_run(
        run_id="RR::FRONTIER::LP57",
        scope="frontier",
        loop_id="L02",
        agent_ids=["A1", "A2", "A3", "A4", "AP6D-PRIME"],
        baseline_snapshot_ref="SNAP::LP57::frontier::pre",
        post_snapshot_ref="SNAP::LP57::frontier::post",
        reward_vector=vector,
        reward_transform=RewardTransform.PHI,
        residuals=[],
        truth=TRUTH,
    )


def build_snapshots(evaluation: Any, primary_agent_id: str, coordinate_stamp: str) -> list[PhiEfficiencySnapshot]:
    baseline = PhiEfficiencySnapshot(
        snapshot_id=evaluation.baseline_snapshot_ref,
        agent_id=primary_agent_id,
        scope=evaluation.scope,
        loop_id=evaluation.loop_id,
        frontier_id=FRONTIER_ID,
        pre_or_post="pre",
        reward_vector=RewardVector(),
        net_efficiency_score=0.0,
        truth=TRUTH,
        coordinate_stamp=coordinate_stamp,
    )
    post = PhiEfficiencySnapshot(
        snapshot_id=evaluation.post_snapshot_ref,
        agent_id=primary_agent_id,
        scope=evaluation.scope,
        loop_id=evaluation.loop_id,
        frontier_id=FRONTIER_ID,
        pre_or_post="post",
        reward_vector=evaluation.reward_vector,
        net_efficiency_score=evaluation.net_efficiency_score,
        truth=TRUTH,
        coordinate_stamp=coordinate_stamp,
    )
    return [baseline, post]


def apply_credit(
    profiles: dict[str, AgentProgressProfile],
    credit: QuestOutcomeCredit,
) -> None:
    for agent_id, xp_delta in credit.credit_shares.items():
        if agent_id not in profiles:
            ensure_profile(
                profiles,
                agent_id=agent_id,
                parent_agent_id="",
                master_agent_id=agent_id if agent_id.startswith("A") else "A2",
                loop_origin=credit.loop_id,
                coordinate_stamp=credit.quest_id,
            )
        profiles[agent_id] = update_progress_profile(
            profiles[agent_id],
            xp_delta=xp_delta,
            outcome=credit.outcome,
            linked_agents=credit.assist_agent_ids + credit.parent_chain_ids,
            quest_increment=1 if credit.outcome == RunOutcome.POSITIVE else 0,
        )


def distribute_direct_bonus(
    profiles: dict[str, AgentProgressProfile],
    *,
    evaluation: Any,
    target_agent_ids: list[str],
) -> dict[str, int]:
    if not target_agent_ids:
        return {}
    split = round(evaluation.xp_delta / len(target_agent_ids)) if evaluation.xp_delta else 0
    applied: dict[str, int] = {}
    for agent_id in target_agent_ids:
        if agent_id not in profiles:
            ensure_profile(
                profiles,
                agent_id=agent_id,
                parent_agent_id="",
                master_agent_id=agent_id if agent_id.startswith("A") else "A2",
                loop_origin=evaluation.loop_id,
                coordinate_stamp=evaluation.scope,
            )
        profiles[agent_id] = update_progress_profile(
            profiles[agent_id],
            xp_delta=split,
            outcome=evaluation.outcome,
            linked_agents=target_agent_ids,
            quest_increment=0,
        )
        applied[agent_id] = split
    return applied


def top_agents_from_profiles(profiles: dict[str, AgentProgressProfile], limit: int = 8) -> list[dict[str, Any]]:
    ranked = sorted(
        profiles.values(),
        key=lambda profile: (profile.xp_total, profile.level, profile.agent_id),
        reverse=True,
    )
    return [
        {
            "agent_id": profile.agent_id,
            "xp_total": profile.xp_total,
            "level": profile.level,
            "adventure_class": profile.adventure_class.value,
            "promotion_state": profile.promotion_state,
        }
        for profile in ranked[:limit]
    ]


def class_distribution(profiles: dict[str, AgentProgressProfile]) -> dict[str, int]:
    distribution = {name: 0 for name in ["F", "E", "D", "C", "B", "A", "S"]}
    for profile in profiles.values():
        distribution[profile.adventure_class.value] += 1
    return distribution


def patch_block(text_in: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    if start in text_in and end in text_in:
        before, _, tail = text_in.partition(start)
        _, _, after = tail.partition(end)
        return before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
    return text_in.rstrip() + "\n\n" + block + "\n"


def render_reward_summary(summary: dict[str, Any]) -> str:
    top_lines = "\n".join(
        f"- `{row['agent_id']}`: `{row['adventure_class']}` / level `{row['level']}` / xp `{row['xp_total']}`"
        for row in summary["top_agents"]
    ) or "- None"
    return (
        "## Reward Overlay\n\n"
        f"- Protocol: `{REWARD_PROTOCOL_ID}`\n"
        f"- Class distribution: `{summary['class_distribution']}`\n"
        f"- Top promoted candidates: `{summary['promotion_candidates']}`\n"
        f"- Recent organism delta: `+{summary['recent_positive_delta']} / {summary['recent_negative_delta']}`\n"
        f"- Reward pressure: {summary['reward_pressure_note']}\n\n"
        "### Top Agents\n\n"
        f"{top_lines}"
    )


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=WORKSPACE_ROOT, capture_output=True, text=True)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "ok": result.returncode == 0,
    }


def main() -> int:
    docs_gate = docs_gate_status()
    lattice = load_json(LATTICE_JSON_PATH)
    master_state = load_json(MASTER_AGENT_STATE_JSON_PATH)
    legacy_reward_ledger = load_json(LEGACY_REWARD_LEDGER_PATH, {"rows": []})
    verification = load_json(SWARM_VERIFICATION_PATH)

    profiles = build_profile_registry()
    run_evaluations: list[dict[str, Any]] = []
    quest_credits: list[dict[str, Any]] = []
    phi_snapshots: list[dict[str, Any]] = []

    for row in legacy_reward_ledger.get("rows", []):
        master_id = row["seat_id"].split("-")[1]
        transform = reward_transform_for_row(row)
        reward_vector = reward_vector_from_legacy(row, docs_gate)
        evaluation = evaluate_reward_run(
            run_id=row["run_id"],
            scope="quest",
            loop_id=row["loop_id"],
            agent_ids=[row["agent_tag"]],
            baseline_snapshot_ref=f"SNAP::{row['run_id']}::pre",
            post_snapshot_ref=f"SNAP::{row['run_id']}::post",
            reward_vector=reward_vector,
            reward_transform=transform,
            residuals=[],
            truth=TRUTH,
        )
        run_evaluations.append(evaluation.to_dict())
        phi_snapshots.extend(
            snapshot.to_dict()
            for snapshot in build_snapshots(
                evaluation,
                row["agent_tag"],
                row.get("linked_ledger_ref", row["agent_tag"]),
            )
        )
        credit = distribute_credit(
            quest_id=row["quest_packet_id"],
            loop_id=row["loop_id"],
            frontier_id=FRONTIER_ID,
            primary_agent_id=row["agent_tag"],
            assist_agent_ids=ASSIST_BY_MASTER.get(master_id, []),
            parent_chain_ids=[master_id],
            reward_transform=transform,
            base_xp_delta=round(evaluation.net_efficiency_score),
            final_xp_delta=evaluation.xp_delta,
            outcome=evaluation.outcome,
            truth=TRUTH,
        )
        quest_credits.append(credit.to_dict())
        apply_credit(profiles, credit)

    loop_bonus = build_loop_bonus_evaluation("L01")
    frontier_bonus = build_frontier_bonus_evaluation()
    loop_bonus_shares = distribute_direct_bonus(profiles, evaluation=loop_bonus, target_agent_ids=["A1", "A2", "A3", "A4"])
    frontier_bonus_shares = distribute_direct_bonus(profiles, evaluation=frontier_bonus, target_agent_ids=["A1", "A2", "A3", "A4", "AP6D-PRIME"])
    run_evaluations.extend([loop_bonus.to_dict(), frontier_bonus.to_dict()])
    phi_snapshots.extend(snapshot.to_dict() for snapshot in build_snapshots(loop_bonus, "A1", "LOOP-BONUS"))
    phi_snapshots.extend(snapshot.to_dict() for snapshot in build_snapshots(frontier_bonus, "AP6D-PRIME", "FRONTIER-BONUS"))

    promotion_records = []
    mini_hive_charters = []
    for profile in profiles.values():
        record = build_promotion_record(
            profile,
            merge_approved=False,
            no_replay_breach=True,
            no_docs_dishonesty=True,
            promotion_seed="MiniHive::Eligibility",
            truth=TRUTH,
        )
        if record.eligible:
            mini_hive_charters.append(
                build_mini_hive_charter(
                    agent_id=profile.agent_id,
                    promotion_ref=f"PROMOTION::{profile.agent_id}",
                    sub_hive_frontier_id=f"MINIHIVE::{profile.agent_id}",
                    seat_budget=64,
                    truth=TRUTH,
                ).to_dict()
            )
        promotion_records.append(record.to_dict())

    steering_profiles = {
        agent_id: build_reward_steering_profile(profile)
        for agent_id, profile in profiles.items()
        if agent_id in {"A1", "A2", "A3", "A4", "AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR", "floating-agent-01", "floating-agent-02", "floating-agent-05", "DOCS-GATE-01"} or profile.xp_total > 0
    }

    distribution = class_distribution(profiles)
    top_agents = top_agents_from_profiles(profiles)
    recent_positive_delta = sum(max(0, entry["xp_delta"]) for entry in run_evaluations)
    recent_negative_delta = sum(min(0, entry["xp_delta"]) for entry in run_evaluations)
    promotion_candidates = [row["agent_id"] for row in promotion_records if row["eligible"]][:8]
    reward_pressure_note = (
        "Positive pressure dominates; promotion remains governance-locked until level-100 agents satisfy replay and docs-honesty gates."
        if recent_positive_delta >= abs(recent_negative_delta)
        else "Negative pressure is dominant; replay and control-surface repair should outrank expansion."
    )

    progress_payload = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "reward_protocol_id": REWARD_PROTOCOL_ID,
        "docs_gate_status": docs_gate,
        "profile_count": len(profiles),
        "class_distribution": distribution,
        "top_agents": top_agents,
        "reward_steering_profiles": steering_profiles,
        "profiles": [profile.to_dict() for profile in sorted(profiles.values(), key=lambda row: row.agent_id)],
    }
    reward_ledger_payload = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "reward_protocol_id": REWARD_PROTOCOL_ID,
        "reward_hierarchy": {
            "state_reward": "diagnostic-only",
            "quest_reward": "primary-xp-source",
            "loop_reward": "4-agent completion bonus",
            "frontier_reward": "cross-loop stabilization bonus",
            "crown_reward": "reserved for rare canonization outcomes",
        },
        "quest_credits": quest_credits,
        "loop_rewards": [{"evaluation": loop_bonus.to_dict(), "credit_shares": loop_bonus_shares}],
        "frontier_rewards": [{"evaluation": frontier_bonus.to_dict(), "credit_shares": frontier_bonus_shares}],
        "crown_rewards": [],
        "recent_positive_delta": recent_positive_delta,
        "recent_negative_delta": recent_negative_delta,
        "reward_pressure_note": reward_pressure_note,
    }
    phi_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "reward_protocol_id": REWARD_PROTOCOL_ID, "snapshots": phi_snapshots}
    promotion_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "eligible_count": len(promotion_candidates), "records": promotion_records}
    mini_hive_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "count": len(mini_hive_charters), "charters": mini_hive_charters}
    evaluation_payload = {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "count": len(run_evaluations), "evaluations": run_evaluations}

    for path, payload in [
        (AGENT_PROGRESS_PATH, progress_payload),
        (AGENT_REWARD_LEDGER_PATH, reward_ledger_payload),
        (PHI_LEDGER_PATH, phi_payload),
        (PROMOTION_QUEUE_PATH, promotion_payload),
        (MINI_HIVE_CHARTERS_PATH, mini_hive_payload),
        (RUN_EVALUATIONS_PATH, evaluation_payload),
    ]:
        write_json(path, payload)
        write_json(REGISTRY_MIRRORS[path], payload)

    motion_result = run_command(MOTION_DERIVE_COMMAND)

    atlas = refresh_corpus_atlas(
        [
            AGENT_PROGRESS_PATH,
            AGENT_REWARD_LEDGER_PATH,
            PHI_LEDGER_PATH,
            PROMOTION_QUEUE_PATH,
            MINI_HIVE_CHARTERS_PATH,
            RUN_EVALUATIONS_PATH,
        ]
    )

    summary = {
        "class_distribution": distribution,
        "top_agents": top_agents,
        "promotion_candidates": promotion_candidates,
        "recent_positive_delta": recent_positive_delta,
        "recent_negative_delta": recent_negative_delta,
        "reward_pressure_note": reward_pressure_note,
    }

    state_payload = load_json(STATE_JSON_PATH)
    state_payload["reward_state_ref"] = relative_string(AGENT_PROGRESS_PATH)
    state_payload["class_distribution"] = distribution
    state_payload["promotion_queue_ref"] = relative_string(PROMOTION_QUEUE_PATH)
    state_payload["top_agents"] = top_agents[:5]
    state_payload["reward_pressure_ref"] = relative_string(AGENT_REWARD_LEDGER_PATH)
    write_json(STATE_JSON_PATH, state_payload)

    master_state_payload = load_json(MASTER_STATE_JSON_PATH)
    master_state_payload["reward_state_ref"] = relative_string(AGENT_PROGRESS_PATH)
    master_state_payload["class_distribution"] = distribution
    master_state_payload["promotion_queue_ref"] = relative_string(PROMOTION_QUEUE_PATH)
    master_state_payload["top_agents"] = top_agents[:5]
    master_state_payload["reward_pressure_ref"] = relative_string(AGENT_REWARD_LEDGER_PATH)
    write_json(MASTER_STATE_JSON_PATH, master_state_payload)

    master_agent_payload = load_json(MASTER_AGENT_STATE_JSON_PATH)
    master_agent_payload["reward_overlay_v1"] = {
        "state_ref": relative_string(AGENT_PROGRESS_PATH),
        "promotion_queue_ref": relative_string(PROMOTION_QUEUE_PATH),
        "class_distribution": distribution,
        "reward_pressure_note": reward_pressure_note,
    }
    write_json(MASTER_AGENT_STATE_JSON_PATH, master_agent_payload)

    manifest_text = (
        f"# LP-57OMEGA Reward Protocol\n\nGenerated: `{utc_now()}`\nDocs gate: `{docs_gate}`\n\n"
        "This overlay rewards measured organism improvement, not raw activity volume.\n\n"
        "## Locked Laws\n\n"
        "- Reward core: `vector + scalar`\n- Penalty law: `signed XP with floor`\n"
        "- Promotion: `level 100` unlocks governed mini-hive eligibility only\n"
        "- Persistence: all agents remain identity-persistent\n\n"
        f"## Summary\n\n{render_reward_summary(summary)}\n"
    )
    dashboard_text = (
        f"# LP-57OMEGA Reward Dashboard\n\nGenerated: `{utc_now()}`\n\n"
        f"- Profiles: `{len(profiles)}`\n- Positive delta: `+{recent_positive_delta}`\n"
        f"- Negative delta: `{recent_negative_delta}`\n- Promotion candidates: `{promotion_candidates}`\n\n"
        f"{render_reward_summary(summary)}\n"
    )
    promotion_text = "# LP-57OMEGA Promotion Board\n\n" + "\n".join(
        f"- `{row['agent_id']}`: eligible=`{row['eligible']}` failures=`{row['gating_failures']}`"
        for row in promotion_records[:24]
    )
    phi_text = "# LP-57OMEGA Phi Efficiency Ledger\n\n" + "\n".join(
        f"- `{row['snapshot_id']}` `{row['agent_id']}` `{row['pre_or_post']}` score=`{row['net_efficiency_score']}`"
        for row in phi_snapshots[:40]
    )

    verification_payload = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "reward_protocol_id": REWARD_PROTOCOL_ID,
        "truth": TRUTH,
        "docs_gate_status": docs_gate,
        "checks": {
            "profiles_exist": {"pass": len(profiles) >= 16384, "detail": len(profiles)},
            "seat_law_preserved": {"pass": load_json(SWARM_VERIFICATION_PATH)["checks"]["seat_law_exact"]["pass"], "detail": load_json(SWARM_VERIFICATION_PATH)["checks"]["seat_law_exact"]["detail"]},
            "feeder_set_preserved": {"pass": load_json(SWARM_VERIFICATION_PATH)["checks"]["feeder_set_exact"]["pass"], "detail": load_json(SWARM_VERIFICATION_PATH)["checks"]["feeder_set_exact"]["detail"]},
            "docs_gate_blocked_honest": {"pass": docs_gate.startswith("blocked"), "detail": docs_gate},
            "motion_refresh_ok": {"pass": motion_result["ok"], "detail": motion_result["returncode"]},
            "atlas_refresh_complete": {"pass": bool(atlas.get("record_count")), "detail": atlas.get("record_count", 0)},
            "promotion_locked_without_approval": {"pass": len(mini_hive_charters) == 0, "detail": len(mini_hive_charters)},
        },
    }
    write_json(VERIFICATION_JSON_PATH, verification_payload)
    write_json(REGISTRY_MIRRORS[VERIFICATION_JSON_PATH], verification_payload)
    verification_text = "# LP-57OMEGA Reward Verification\n\n" + "\n".join(
        f"- `{name}`: pass=`{payload['pass']}` detail=`{payload['detail']}`"
        for name, payload in verification_payload["checks"].items()
    )
    receipt_text = (
        f"# LP-57OMEGA Reward Overlay Receipt\n\nGenerated: `{utc_now()}`\n\n"
        f"- Progress registry: `{relative_string(AGENT_PROGRESS_PATH)}`\n"
        f"- Reward ledger: `{relative_string(AGENT_REWARD_LEDGER_PATH)}`\n"
        f"- Promotion queue: `{relative_string(PROMOTION_QUEUE_PATH)}`\n"
        f"- Motion refresh: `{motion_result['returncode']}`\n"
        f"- Next seed: `{NEXT_SEED}`\n"
    )

    for path, text in [
        (MANIFEST_MD_PATH, manifest_text),
        (DASHBOARD_MD_PATH, dashboard_text),
        (PROMOTION_MD_PATH, promotion_text),
        (PHI_LEDGER_MD_PATH, phi_text),
        (VERIFICATION_MD_PATH, verification_text),
        (RECEIPT_MD_PATH, receipt_text),
    ]:
        write_text(path, text)

    for path in [LP57_PROTOCOL_MD_PATH, LP57_DASHBOARD_MD_PATH]:
        existing = read_text(path)
        write_text(path, patch_block(existing, "LP57_REWARD_OVERLAY", render_reward_summary(summary)))

    refresh_corpus_atlas(
        [
            MANIFEST_MD_PATH,
            DASHBOARD_MD_PATH,
            PROMOTION_MD_PATH,
            PHI_LEDGER_MD_PATH,
            VERIFICATION_MD_PATH,
            RECEIPT_MD_PATH,
            LP57_PROTOCOL_MD_PATH,
            LP57_DASHBOARD_MD_PATH,
            STATE_JSON_PATH,
            MASTER_STATE_JSON_PATH,
            MASTER_AGENT_STATE_JSON_PATH,
            VERIFICATION_JSON_PATH,
        ]
    )
    print(json.dumps({"truth": TRUTH, "profiles": len(profiles), "positive_delta": recent_positive_delta, "negative_delta": recent_negative_delta}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
