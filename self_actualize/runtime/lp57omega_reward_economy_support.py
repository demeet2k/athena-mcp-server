from __future__ import annotations

from typing import Any


PHI = 1.61803398875
MAX_LEVEL = 100
MINI_HIVE_ROLE_IDS = ["A1", "A2", "A3", "A4"]
VIRTUAL_SEATS_PER_ROLE = 4**6
MINI_HIVE_TOTAL_SEATS = len(MINI_HIVE_ROLE_IDS) * VIRTUAL_SEATS_PER_ROLE
METRIC_NAMES = [
    "efficiency",
    "coherence",
    "integration",
    "compression",
    "witness",
    "replay",
    "route_clarity",
]
DELTA_NAMES = [f"{name}_delta" for name in METRIC_NAMES]
ALLOWED_TRUTH_CLASSES = {"OK", "NEAR"}
RANK_BANDS = [
    ("F", 0, 14),
    ("E", 15, 29),
    ("D", 30, 44),
    ("C", 45, 59),
    ("B", 60, 74),
    ("A", 75, 89),
    ("S", 90, 100),
]
REWARD_OPERATORS = {
    "identity": {
        "reward_operator_id": "identity",
        "reward_multiplier": 1.0,
        "risk_band": "standard",
        "reward_reason": "standard practical or governance quest",
    },
    "phi": {
        "reward_operator_id": "phi",
        "reward_multiplier": PHI,
        "risk_band": "integration",
        "reward_reason": "high-value integration or bridge quest",
    },
    "double_phi": {
        "reward_operator_id": "double_phi",
        "reward_multiplier": 2 * PHI,
        "risk_band": "frontier",
        "reward_reason": "boss or frontier quest promoted by the planner",
    },
    "phi_square": {
        "reward_operator_id": "phi_square",
        "reward_multiplier": 2.61803398875,
        "risk_band": "convergence",
        "reward_reason": "rare convergence, zero-point, or cross-family closure quest",
    },
    "zero": {
        "reward_operator_id": "zero",
        "reward_multiplier": 0.0,
        "risk_band": "bootstrap",
        "reward_reason": "spawn, init, or bootstrap task",
    },
}
ROLE_METRIC_BASE = {
    "A1": {
        "efficiency": 0.24,
        "coherence": 0.18,
        "integration": 0.72,
        "compression": 0.16,
        "witness": 0.68,
        "replay": 0.54,
        "route_clarity": 0.32,
    },
    "A2": {
        "efficiency": 0.28,
        "coherence": 0.72,
        "integration": 0.46,
        "compression": 0.22,
        "witness": 0.42,
        "replay": 0.48,
        "route_clarity": 0.74,
    },
    "A3": {
        "efficiency": 0.76,
        "coherence": 0.34,
        "integration": 0.66,
        "compression": 0.28,
        "witness": 0.52,
        "replay": 0.58,
        "route_clarity": 0.38,
    },
    "A4": {
        "efficiency": 0.42,
        "coherence": 0.52,
        "integration": 0.36,
        "compression": 0.82,
        "witness": 0.48,
        "replay": 0.44,
        "route_clarity": 0.62,
    },
}
ROLE_LANE_WEIGHTS = {
    "A1": {"integration": 1.0, "witness": 1.0, "route_clarity": 0.5},
    "A2": {"coherence": 1.0, "route_clarity": 1.0, "replay": 0.5},
    "A3": {"efficiency": 1.0, "replay": 1.0, "integration": 0.5},
    "A4": {"compression": 1.0, "coherence": 0.5, "route_clarity": 0.5},
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def zero_metrics() -> dict[str, float]:
    return {name: 0.0 for name in METRIC_NAMES}


def build_level_thresholds(max_level: int = MAX_LEVEL) -> list[int]:
    thresholds = [0]
    for n in range(max_level):
        thresholds.append(thresholds[-1] + round(100 * (PHI ** (n / 25))))
    return thresholds


LEVEL_THRESHOLDS = build_level_thresholds()


def level_for_xp(xp: int, thresholds: list[int] | None = None) -> int:
    ladder = thresholds or LEVEL_THRESHOLDS
    value = max(0, xp)
    level = 0
    for idx, threshold in enumerate(ladder):
        if threshold <= value:
            level = idx
        else:
            break
    return min(level, MAX_LEVEL)


def rank_for_level(level: int) -> str:
    for rank, lo, hi in RANK_BANDS:
        if lo <= level <= hi:
            return rank
    return "S"


def reward_operator_registry() -> dict[str, Any]:
    return {
        "model": "Hybrid Phi",
        "operators": list(REWARD_OPERATORS.values()),
        "rank_bands": [
            {"rank_class": rank, "level_min": lo, "level_max": hi}
            for rank, lo, hi in RANK_BANDS
        ],
        "level_thresholds": LEVEL_THRESHOLDS,
        "penalty_model": "Strict but Damped",
        "promotion_model": "Prestige Hive",
        "promotion_level": MAX_LEVEL,
        "mini_hive": {
            "role_count": len(MINI_HIVE_ROLE_IDS),
            "roles": list(MINI_HIVE_ROLE_IDS),
            "virtual_seats_per_role": VIRTUAL_SEATS_PER_ROLE,
            "total_virtual_seats": MINI_HIVE_TOTAL_SEATS,
        },
    }


def band_multipliers(loop_number: int) -> dict[str, float]:
    if loop_number <= 16:
        return {
            "efficiency": 0.92,
            "coherence": 1.08,
            "integration": 1.0,
            "compression": 0.88,
            "witness": 1.08,
            "replay": 0.96,
            "route_clarity": 1.02,
        }
    if loop_number <= 32:
        return {
            "efficiency": 1.0,
            "coherence": 1.0,
            "integration": 1.12,
            "compression": 0.95,
            "witness": 1.0,
            "replay": 1.0,
            "route_clarity": 1.08,
        }
    if loop_number <= 48:
        return {
            "efficiency": 1.08,
            "coherence": 0.98,
            "integration": 1.05,
            "compression": 1.08,
            "witness": 0.96,
            "replay": 1.05,
            "route_clarity": 1.0,
        }
    return {
        "efficiency": 0.96,
        "coherence": 1.05,
        "integration": 0.98,
        "compression": 1.12,
        "witness": 1.08,
        "replay": 1.1,
        "route_clarity": 1.02,
    }


def projected_end_state_metrics(loop_number: int, master_agent_id: str) -> dict[str, float]:
    base = ROLE_METRIC_BASE[master_agent_id]
    mods = band_multipliers(loop_number)
    role_index = int(master_agent_id[1:])
    metrics: dict[str, float] = {}
    for metric_index, metric_name in enumerate(METRIC_NAMES):
        jitter = (((loop_number * (role_index + 1) + metric_index) % 5) - 2) * 0.01
        value = base[metric_name] * mods[metric_name] + jitter
        metrics[metric_name] = round(clamp(value, -1.0, 1.0), 6)
    return metrics


def metric_deltas(
    start_state_metrics: dict[str, float], end_state_metrics: dict[str, float]
) -> dict[str, float]:
    return {
        f"{metric_name}_delta": round(
            end_state_metrics[metric_name] - start_state_metrics[metric_name], 6
        )
        for metric_name in METRIC_NAMES
    }


def net_gain(metric_delta_vector: dict[str, float]) -> float:
    return (
        0.25 * metric_delta_vector["efficiency_delta"]
        + 0.15 * metric_delta_vector["coherence_delta"]
        + 0.20 * metric_delta_vector["integration_delta"]
        + 0.15 * metric_delta_vector["compression_delta"]
        + 0.10 * metric_delta_vector["witness_delta"]
        + 0.10 * metric_delta_vector["replay_delta"]
        + 0.05 * metric_delta_vector["route_clarity_delta"]
    )


def positivity_score(metric_delta_vector: dict[str, float]) -> int:
    return int(clamp(round(100 * net_gain(metric_delta_vector)), -100, 100))


def xp_delta_from_score(
    positivity: int, reward_multiplier: float
) -> tuple[int, bool]:
    if positivity >= 0:
        return round(max(0, positivity) * reward_multiplier), False
    uncapped = round(abs(min(0, positivity)) * reward_multiplier * 0.8)
    capped = min(250, uncapped)
    return -capped, uncapped > 250


def metrics_are_contradictory(metric_delta_vector: dict[str, float]) -> bool:
    if set(metric_delta_vector.keys()) != set(DELTA_NAMES):
        return True
    return any(value < -1.0 or value > 1.0 for value in metric_delta_vector.values())


def lane_contribution_vector(metric_delta_vector: dict[str, float]) -> dict[str, float]:
    lane_scores: dict[str, float] = {}
    for lane_id, weights in ROLE_LANE_WEIGHTS.items():
        lane_scores[lane_id] = sum(
            abs(metric_delta_vector[f"{metric_name}_delta"]) * weight
            for metric_name, weight in weights.items()
        )
    total = sum(lane_scores.values())
    if total <= 0:
        return {lane_id: 0.0 for lane_id in ROLE_LANE_WEIGHTS}
    return {
        lane_id: round(score / total, 6) for lane_id, score in lane_scores.items()
    }


def reward_operator_for_loop(loop: dict[str, Any], master_agent_id: str) -> dict[str, Any]:
    loop_number = loop["loop_index"]
    focus_family = loop["focus_family"]
    frontier_type = loop["frontier_type"]

    if loop_number == 1 or frontier_type == "prime-lock":
        operator_id = "zero"
    elif loop_number in {53, 56, 57} or focus_family in {"canonicalization", "reseed"}:
        operator_id = "phi_square"
    elif loop_number in {16, 32, 48} or focus_family in {"gates", "replay"}:
        operator_id = "double_phi"
    elif (
        "bridge" in frontier_type
        or "integration" in frontier_type
        or focus_family
        in {
            "pair-matrix",
            "operators",
            "hybrid-equations",
            "algorithms",
            "knowledge-fabric",
            "grand-central",
            "pairwise-integration",
            "runtime-bridge",
            "identity-orgin",
            "voynich-math",
            "corridor",
            "kernel-weave",
            "parity",
        }
    ):
        operator_id = "phi"
    else:
        operator_id = "identity"

    operator = dict(REWARD_OPERATORS[operator_id])
    operator["master_agent_id"] = master_agent_id
    return operator


def projected_packet_reward(loop: dict[str, Any], master_agent_id: str) -> dict[str, Any]:
    operator = reward_operator_for_loop(loop, master_agent_id)
    start_state = zero_metrics()
    end_state = projected_end_state_metrics(loop["loop_index"], master_agent_id)
    deltas = metric_deltas(start_state, end_state)
    score = positivity_score(deltas)
    xp_delta, penalty_cap = xp_delta_from_score(score, operator["reward_multiplier"])
    return {
        "predicted_positivity_score": score,
        "predicted_xp_delta": xp_delta,
        "penalty_cap_applied": penalty_cap,
        "promotion_eligibility_hint": "eligible when admissible and cumulative local level reaches 100",
    }


def build_initial_progression(
    seat_row: dict[str, Any], lineage_id: str | None = None
) -> dict[str, Any]:
    return {
        "agent_tag": seat_row["agent_tag"],
        "seat_id": seat_row["seat_id"],
        "master_agent_id": seat_row["master_agent_id"],
        "lineage_id": lineage_id or f"{seat_row['seat_id']}::d0",
        "dimension_index": 0,
        "current_level": 0,
        "current_xp": 0,
        "lifetime_xp": 0,
        "rank_class": "F",
        "promotion_count": 0,
        "child_hive_id": None,
        "status": seat_row["binding_state"],
        "reward_operator_history": [],
        "reward_run_refs": [],
        "quarantined_run_refs": [],
        "last_positive_run_ref": None,
        "last_negative_run_ref": None,
    }


def build_child_hive_atlas(
    parent_agent_tag: str, parent_lineage_id: str, new_dimension_index: int
) -> dict[str, Any]:
    child_hive_id = (
        f"MINIHIVE::{parent_agent_tag}::d{new_dimension_index}"
    )
    child_namespace = (
        f"{parent_agent_tag}::dimension-{new_dimension_index}::mini-hive"
    )
    rows = []
    for role_id in MINI_HIVE_ROLE_IDS:
        for seat_index in range(VIRTUAL_SEATS_PER_ROLE):
            digits = []
            value = seat_index
            for _ in range(6):
                digits.append((value % 4) + 1)
                value //= 4
            digits.reverse()
            rows.append(
                {
                    "seat_id": f"{child_hive_id}::{role_id}::{seat_index:04d}",
                    "role_id": role_id,
                    "seat_index": seat_index,
                    "seat_addr_6d": ".".join(str(digit) for digit in digits),
                    "lineage_id": f"{parent_lineage_id}::d{new_dimension_index}",
                    "dimension_index": new_dimension_index,
                    "namespace": child_namespace,
                }
            )
    return {
        "child_hive_id": child_hive_id,
        "child_namespace": child_namespace,
        "child_role_ids": list(MINI_HIVE_ROLE_IDS),
        "virtual_seat_count": len(rows),
        "rows": rows,
    }


def build_run_reward_evaluation(
    *,
    run_id: str,
    agent_tag: str,
    seat_id: str,
    loop_id: str,
    quest_packet_id: str,
    truth_class: str,
    reward_operator_id: str,
    reward_multiplier: float,
    start_state_metrics: dict[str, float],
    end_state_metrics: dict[str, float],
    witness_coverage_passed: bool,
    replay_coverage_passed: bool,
    linked_ledger_ref: str,
    timestamp_internal: str,
) -> dict[str, Any]:
    delta_vector = metric_deltas(start_state_metrics, end_state_metrics)
    score = positivity_score(delta_vector)
    snapshots_present = bool(start_state_metrics) and bool(end_state_metrics)
    contradictory = metrics_are_contradictory(delta_vector)
    admissible = (
        truth_class in ALLOWED_TRUTH_CLASSES
        and witness_coverage_passed
        and replay_coverage_passed
        and snapshots_present
        and not contradictory
    )
    xp_delta, penalty_cap = xp_delta_from_score(score, reward_multiplier)
    quarantine_reason = None
    reward_status = "APPLIED"
    provisional_score = None
    if not admissible:
        reward_status = "QUARANTINED"
        quarantine_reason = (
            "truth-class"
            if truth_class not in ALLOWED_TRUTH_CLASSES
            else "witness-coverage"
            if not witness_coverage_passed
            else "replay-coverage"
            if not replay_coverage_passed
            else "snapshot-missing"
            if not snapshots_present
            else "metric-contradiction"
        )
        provisional_score = score
        xp_delta = 0
        penalty_cap = False

    return {
        "run_id": run_id,
        "agent_tag": agent_tag,
        "seat_id": seat_id,
        "loop_id": loop_id,
        "quest_packet_id": quest_packet_id,
        "truth_class": truth_class,
        "reward_status": reward_status,
        "start_state_metrics": start_state_metrics,
        "end_state_metrics": end_state_metrics,
        "metric_deltas": delta_vector,
        "net_gain": round(net_gain(delta_vector), 6),
        "positivity_score": score,
        "reward_operator_id": reward_operator_id,
        "reward_multiplier": reward_multiplier,
        "xp_delta": xp_delta,
        "penalty_cap_applied": penalty_cap,
        "quarantine_reason": quarantine_reason,
        "provisional_positivity_score": provisional_score,
        "witness_coverage_passed": witness_coverage_passed,
        "replay_coverage_passed": replay_coverage_passed,
        "lane_contribution_vector": lane_contribution_vector(delta_vector),
        "linked_ledger_ref": linked_ledger_ref,
        "timestamp_internal": timestamp_internal,
    }


def apply_evaluation_to_progression(
    progression: dict[str, Any], evaluation: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    progression["reward_operator_history"].append(evaluation["reward_operator_id"])

    if evaluation["reward_status"] == "QUARANTINED":
        progression["quarantined_run_refs"].append(evaluation["run_id"])
        return progression, None

    progression["reward_run_refs"].append(evaluation["run_id"])
    xp_delta = evaluation["xp_delta"]
    progression["current_xp"] = max(0, progression["current_xp"] + xp_delta)
    progression["lifetime_xp"] += max(0, xp_delta)
    if xp_delta > 0:
        progression["last_positive_run_ref"] = evaluation["run_id"]
    elif xp_delta < 0:
        progression["last_negative_run_ref"] = evaluation["run_id"]

    progression["current_level"] = level_for_xp(progression["current_xp"])
    progression["rank_class"] = rank_for_level(progression["current_level"])

    promotion_record = None
    if progression["current_level"] >= MAX_LEVEL:
        new_dimension_index = progression["dimension_index"] + 1
        child_hive = build_child_hive_atlas(
            progression["agent_tag"], progression["lineage_id"], new_dimension_index
        )
        promotion_id = (
            f"PROMOTE::{progression['seat_id']}::d{new_dimension_index}"
        )
        promotion_record = {
            "promotion_id": promotion_id,
            "parent_agent_tag": progression["agent_tag"],
            "parent_lineage_id": progression["lineage_id"],
            "new_dimension_index": new_dimension_index,
            "child_hive_id": child_hive["child_hive_id"],
            "child_namespace": child_hive["child_namespace"],
            "child_role_ids": list(MINI_HIVE_ROLE_IDS),
            "promotion_trigger_run_ref": evaluation["run_id"],
            "timestamp_internal": evaluation["timestamp_internal"],
            "child_hive_atlas": child_hive,
        }
        progression["promotion_count"] += 1
        progression["dimension_index"] = new_dimension_index
        progression["lineage_id"] = (
            f"{progression['seat_id']}::d{new_dimension_index}"
        )
        progression["child_hive_id"] = child_hive["child_hive_id"]
        progression["current_level"] = 0
        progression["current_xp"] = 0
        progression["rank_class"] = "F"
        progression["status"] = "PROMOTED"
    return progression, promotion_record
