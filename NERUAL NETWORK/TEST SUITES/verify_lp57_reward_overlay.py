from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import (  # noqa: E402
    AdventureClass,
    AgentProgressProfile,
    MotionScoreVector,
    RewardTransform,
    RewardVector,
    RunOutcome,
)
from athenachka.runtime.reward_overlay import (  # noqa: E402
    apply_reward_steering,
    build_promotion_record,
    evaluate_reward_run,
    update_progress_profile,
)

SELF = WORKSPACE_ROOT / "self_actualize"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition: bool, detail) -> dict:
    return {"pass": bool(condition), "detail": detail}


def main() -> int:
    positive_eval = evaluate_reward_run(
        run_id="verify-positive",
        scope="quest",
        loop_id="L02",
        agent_ids=["A1"],
        baseline_snapshot_ref="pre",
        post_snapshot_ref="post",
        reward_vector=RewardVector(
            integration_gain=0.8,
            compression_gain=0.6,
            replay_gain=0.8,
            witness_gain=0.6,
            route_clarity_gain=0.5,
            quest_closure_gain=1.0,
            blocker_honesty_gain=0.8,
            phi_efficiency_gain=0.7,
        ),
        reward_transform=RewardTransform.PHI,
    )
    neutral_eval = evaluate_reward_run(
        run_id="verify-neutral",
        scope="quest",
        loop_id="L02",
        agent_ids=["A1"],
        baseline_snapshot_ref="pre",
        post_snapshot_ref="post",
        reward_vector=RewardVector(),
        reward_transform=RewardTransform.BASE,
    )
    negative_eval = evaluate_reward_run(
        run_id="verify-negative",
        scope="quest",
        loop_id="L02",
        agent_ids=["A1"],
        baseline_snapshot_ref="pre",
        post_snapshot_ref="post",
        reward_vector=RewardVector(
            regression_loss=0.8,
            bloat_loss=0.4,
            replay_break_loss=0.3,
        ),
        reward_transform=RewardTransform.BASE,
    )
    breach_eval = evaluate_reward_run(
        run_id="verify-breach",
        scope="quest",
        loop_id="L02",
        agent_ids=["A1"],
        baseline_snapshot_ref="pre",
        post_snapshot_ref="post",
        reward_vector=RewardVector(
            regression_loss=0.7,
            replay_break_loss=0.9,
            docs_dishonesty_loss=0.4,
        ),
        reward_transform=RewardTransform.PHI,
    )

    floor_profile = AgentProgressProfile(
        agent_id="P1",
        parent_agent_id="",
        master_agent_id="A1",
        loop_origin="L01",
        coordinate_stamp="floor",
        xp_total=4500,
        level=45,
        adventure_class=AdventureClass.C,
    )
    floor_profile = update_progress_profile(floor_profile, xp_delta=-400, outcome=RunOutcome.NEGATIVE)

    promotion_profile = AgentProgressProfile(
        agent_id="P2",
        parent_agent_id="",
        master_agent_id="A2",
        loop_origin="L01",
        coordinate_stamp="promotion",
        xp_total=10000,
        level=100,
        adventure_class=AdventureClass.S,
        recent_outcomes=["POSITIVE", "POSITIVE", "NEUTRAL", "POSITIVE", "POSITIVE"],
        promotion_state="ELIGIBLE",
    )
    promotion_record = build_promotion_record(
        promotion_profile,
        merge_approved=False,
        no_replay_breach=True,
        no_docs_dishonesty=True,
        promotion_seed="MiniHive::Eligibility",
    )

    boosted_vector, boosted_meta = apply_reward_steering(
        MotionScoreVector(
            closure_gain=1.0,
            heart_need=1.0,
            replay_readiness=0.5,
            integration_yield=0.5,
            organ_adjacency=1.0,
            seed_value=1.0,
            cost=0.1,
            replay_cost=0.1,
            risk=0.1,
            failure_debt=0.1,
            branch_burden=0.1,
            contradiction_heat=0.0,
            pressure_gradient=0.1,
            truth_readiness=0.9,
        ),
        {
            "adventure_class": "A",
            "recent_positive_runs": 5,
            "recent_net_losses": 0,
            "replay_breach_open": False,
            "docs_dishonesty_recent": False,
        },
    )

    progress = load_json(SELF / "agent_progress_registry.json")
    state = load_json(SELF / "next_4_pow_6_57_cycle_swarm_state.json")
    verification = load_json(SELF / "four_agent_57_loop_verification.json")

    checks = {
        "positive_run_positive": check(positive_eval.net_efficiency_score > 0 and positive_eval.xp_delta > 0, positive_eval.to_dict()),
        "neutral_run_zero": check(neutral_eval.xp_delta == 0 and neutral_eval.outcome == RunOutcome.NEUTRAL, neutral_eval.to_dict()),
        "negative_run_penalty": check(
            negative_eval.xp_delta < 0
            and (
                floor_profile.demotion_buffer > 0
                or floor_profile.adventure_class == AdventureClass.D
            ),
            {
                "xp_delta": negative_eval.xp_delta,
                "demotion_buffer": floor_profile.demotion_buffer,
                "adventure_class": floor_profile.adventure_class.value,
            },
        ),
        "breach_penalty_harsher": check(abs(breach_eval.xp_delta) > abs(negative_eval.xp_delta), {"breach": breach_eval.xp_delta, "ordinary": negative_eval.xp_delta}),
        "promotion_not_auto_spawn": check(not promotion_record.eligible and "merge or governance approval missing" in promotion_record.gating_failures, promotion_record.to_dict()),
        "steering_applies_exactly": check(boosted_meta["applied"] and boosted_vector.integration_yield == 0.65 and boosted_vector.replay_readiness == 0.6, boosted_meta),
        "persistent_agents_present": check(progress["profile_count"] >= 16384, progress["profile_count"]),
        "seat_law_preserved": check(state["class_distribution"] is not None and verification["checks"]["seat_law_exact"]["pass"], verification["checks"]["seat_law_exact"]["detail"]),
        "feeder_set_preserved": check(verification["checks"]["feeder_set_exact"]["pass"], verification["checks"]["feeder_set_exact"]["detail"]),
        "docs_gate_blocked": check(state["docs_gate"]["reason"] == "blocked-by-missing-credentials", state["docs_gate"]),
    }

    truth = "OK" if all(item["pass"] for item in checks.values()) else "FAIL"
    print(json.dumps({"truth": truth, "checks": checks}, indent=2))
    return 0 if truth == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
