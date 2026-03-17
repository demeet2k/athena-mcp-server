from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.canonical_four_agent_57_loop import (  # noqa: E402
    AGENT_PROGRESSION_JSON,
    PHI_EFFICIENCY_LEDGER_JSON,
    PROGRAM_VERIFY_JSON,
    PROMOTION_LINEAGE_JSON,
    PROGRAM_JSON,
    REWARD_OPERATORS_JSON,
    RUN_REWARD_LEDGER_JSON,
    SEATS_JSON,
    STATE_JSON,
    verify_canonical_four_agent_57_loop,
)
from self_actualize.runtime.lp57omega_reward_economy_support import (  # noqa: E402
    LEVEL_THRESHOLDS,
    MAX_LEVEL,
    MINI_HIVE_ROLE_IDS,
    MINI_HIVE_TOTAL_SEATS,
    apply_evaluation_to_progression,
    build_initial_progression,
    build_run_reward_evaluation,
    level_for_xp,
    rank_for_level,
    zero_metrics,
)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    canonical = verify_canonical_four_agent_57_loop()
    ensure(canonical["truth"] == "OK", "canonical LP57Omega verification failed")

    state = load_json(STATE_JSON)
    if "reward_economy" not in state:
        state = load_json(PROGRAM_JSON)
    seats = load_json(SEATS_JSON)
    operators = load_json(REWARD_OPERATORS_JSON)
    run_rewards = load_json(RUN_REWARD_LEDGER_JSON)
    progression = load_json(AGENT_PROGRESSION_JSON)
    promotions = load_json(PROMOTION_LINEAGE_JSON)
    phi_eff = load_json(PHI_EFFICIENCY_LEDGER_JSON)
    program_verify = load_json(PROGRAM_VERIFY_JSON)

    sample_seat = seats["rows"][0]
    baseline = build_initial_progression(sample_seat)
    ensure(baseline["current_xp"] == 0, "spawn baseline XP drifted")
    ensure(baseline["current_level"] == 0, "spawn baseline level drifted")
    ensure(baseline["dimension_index"] == 0, "spawn baseline dimension drifted")

    positive = build_run_reward_evaluation(
        run_id="TEST::POSITIVE",
        agent_tag=baseline["agent_tag"],
        seat_id=baseline["seat_id"],
        loop_id="LTEST",
        quest_packet_id="QP::POSITIVE",
        truth_class="OK",
        reward_operator_id="phi",
        reward_multiplier=operators["operators"][1]["reward_multiplier"],
        start_state_metrics=zero_metrics(),
        end_state_metrics={
            "efficiency": 0.6,
            "coherence": 0.5,
            "integration": 0.7,
            "compression": 0.4,
            "witness": 0.6,
            "replay": 0.5,
            "route_clarity": 0.4,
        },
        witness_coverage_passed=True,
        replay_coverage_passed=True,
        linked_ledger_ref="LEDGER::POSITIVE",
        timestamp_internal="2026-03-13T00:00:00Z",
    )
    ensure(positive["reward_status"] == "APPLIED", "positive run failed to apply")
    ensure(positive["xp_delta"] > 0, "positive run did not gain XP")

    negative = build_run_reward_evaluation(
        run_id="TEST::NEGATIVE",
        agent_tag=baseline["agent_tag"],
        seat_id=baseline["seat_id"],
        loop_id="LTEST",
        quest_packet_id="QP::NEGATIVE",
        truth_class="NEAR",
        reward_operator_id="double_phi",
        reward_multiplier=3.2360679775,
        start_state_metrics=zero_metrics(),
        end_state_metrics={
            "efficiency": -1.0,
            "coherence": -1.0,
            "integration": -1.0,
            "compression": -1.0,
            "witness": -1.0,
            "replay": -1.0,
            "route_clarity": -1.0,
        },
        witness_coverage_passed=True,
        replay_coverage_passed=True,
        linked_ledger_ref="LEDGER::NEGATIVE",
        timestamp_internal="2026-03-13T00:00:00Z",
    )
    ensure(negative["reward_status"] == "APPLIED", "negative run failed to apply")
    ensure(negative["xp_delta"] < 0, "negative run did not lose XP")
    ensure(abs(negative["xp_delta"]) <= 250, "negative run exceeded damped penalty cap")
    ensure(negative["penalty_cap_applied"], "negative cap flag did not trip")

    quarantined = build_run_reward_evaluation(
        run_id="TEST::QUARANTINE",
        agent_tag=baseline["agent_tag"],
        seat_id=baseline["seat_id"],
        loop_id="LTEST",
        quest_packet_id="QP::QUARANTINE",
        truth_class="FAIL",
        reward_operator_id="identity",
        reward_multiplier=1.0,
        start_state_metrics=zero_metrics(),
        end_state_metrics={
            "efficiency": 0.2,
            "coherence": 0.2,
            "integration": 0.2,
            "compression": 0.2,
            "witness": 0.2,
            "replay": 0.2,
            "route_clarity": 0.2,
        },
        witness_coverage_passed=True,
        replay_coverage_passed=True,
        linked_ledger_ref="LEDGER::QUARANTINE",
        timestamp_internal="2026-03-13T00:00:00Z",
    )
    ensure(
        quarantined["reward_status"] == "QUARANTINED",
        "quarantine gate failed on FAIL truth class",
    )
    ensure(quarantined["xp_delta"] == 0, "quarantined run mutated XP")

    for level, rank in [
        (14, "F"),
        (15, "E"),
        (29, "E"),
        (30, "D"),
        (44, "D"),
        (45, "C"),
        (59, "C"),
        (60, "B"),
        (74, "B"),
        (75, "A"),
        (89, "A"),
        (90, "S"),
        (100, "S"),
    ]:
        ensure(rank_for_level(level) == rank, f"rank drift at level {level}")

    ensure(
        all(LEVEL_THRESHOLDS[idx] <= LEVEL_THRESHOLDS[idx + 1] for idx in range(len(LEVEL_THRESHOLDS) - 1)),
        "level thresholds are not monotonic",
    )
    for xp in [0, LEVEL_THRESHOLDS[1], LEVEL_THRESHOLDS[15], LEVEL_THRESHOLDS[100]]:
        level = level_for_xp(xp)
        ensure(0 <= level <= MAX_LEVEL, f"invalid level {level} for XP {xp}")

    promotion_progression = build_initial_progression(sample_seat)
    promotion_progression["current_xp"] = LEVEL_THRESHOLDS[100] - 1
    promotion_progression["current_level"] = level_for_xp(promotion_progression["current_xp"])
    promotion_progression["rank_class"] = rank_for_level(promotion_progression["current_level"])
    trigger = build_run_reward_evaluation(
        run_id="TEST::PROMOTION",
        agent_tag=promotion_progression["agent_tag"],
        seat_id=promotion_progression["seat_id"],
        loop_id="LTEST",
        quest_packet_id="QP::PROMOTION",
        truth_class="OK",
        reward_operator_id="identity",
        reward_multiplier=1.0,
        start_state_metrics=zero_metrics(),
        end_state_metrics={
            "efficiency": 0.04,
            "coherence": 0.0,
            "integration": 0.0,
            "compression": 0.0,
            "witness": 0.0,
            "replay": 0.0,
            "route_clarity": 0.0,
        },
        witness_coverage_passed=True,
        replay_coverage_passed=True,
        linked_ledger_ref="LEDGER::PROMOTION",
        timestamp_internal="2026-03-13T00:00:00Z",
    )
    promoted, promotion_record = apply_evaluation_to_progression(
        promotion_progression, trigger
    )
    ensure(promotion_record is not None, "promotion did not trigger at level 100")
    ensure(promoted["dimension_index"] == 1, "promotion did not increment dimension")
    ensure(promoted["current_level"] == 0, "promotion did not reset local level")
    ensure(promoted["current_xp"] == 0, "promotion did not reset local XP")
    ensure(promoted["lifetime_xp"] >= 1, "promotion did not preserve lifetime XP")
    ensure(
        promotion_record["child_hive_atlas"]["virtual_seat_count"] == MINI_HIVE_TOTAL_SEATS,
        "promotion did not create a full child hive atlas",
    )
    ensure(
        promotion_record["child_role_ids"] == MINI_HIVE_ROLE_IDS,
        "promotion child role ids drifted",
    )

    ensure(len(operators["operators"]) == 5, "reward operator registry drifted")
    ensure(
        progression["row_count"] == seats["row_count"],
        "progression registry lost seat alignment",
    )
    ensure(
        run_rewards["row_count"] == run_rewards["applied_count"] + run_rewards["quarantined_count"],
        "run reward ledger counts drifted",
    )
    ensure(
        set(phi_eff["aggregate"]["rank_distribution"].keys())
        == {"F", "E", "D", "C", "B", "A", "S"},
        "phi efficiency rank distribution drifted",
    )
    ensure(
        "reward_economy" in state and state["reward_economy"]["model"] == "Hybrid Phi",
        "state reward economy summary drifted",
    )
    ensure(program_verify["truth"] == "OK", "program verification drifted")
    ensure(state["docs_gate"]["state"] == "BLOCKED", "docs gate honesty drifted")

    report = {
        "truth": "OK",
        "docs_gate_status": state["docs_gate"]["state"],
        "reward_operators": len(operators["operators"]),
        "run_reward_rows": run_rewards["row_count"],
        "progression_rows": progression["row_count"],
        "promotion_rows": promotions["promotion_count"],
        "phi_efficiency_rows": phi_eff["row_count"],
        "checks": canonical["checks"],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
