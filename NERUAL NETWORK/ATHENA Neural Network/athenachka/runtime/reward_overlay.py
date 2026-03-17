from __future__ import annotations

from dataclasses import replace
from typing import Any

from ..contracts import (
    AdventureClass,
    AgentProgressProfile,
    MiniHiveCharter,
    MotionScoreVector,
    PhiEfficiencySnapshot,
    PromotionEligibilityRecord,
    QuestOutcomeCredit,
    RewardRunEvaluation,
    RewardTransform,
    RewardVector,
    RunOutcome,
)


POSITIVE_WEIGHTS = {
    "integration_gain": 5,
    "compression_gain": 4,
    "replay_gain": 5,
    "witness_gain": 4,
    "route_clarity_gain": 3,
    "quest_closure_gain": 3,
    "blocker_honesty_gain": 4,
    "phi_efficiency_gain": 5,
}

NEGATIVE_WEIGHTS = {
    "regression_loss": 6,
    "bloat_loss": 3,
    "contradiction_increase": 4,
    "orphaned_node_loss": 5,
    "replay_break_loss": 6,
    "control_surface_drift": 4,
    "unauthorized_activation_loss": 6,
    "docs_dishonesty_loss": 8,
}

POSITIVE_DENOMINATOR = 33
NEGATIVE_DENOMINATOR = 42
POSITIVE_OUTCOMES = {RunOutcome.POSITIVE.value, RunOutcome.POSITIVE}
NON_NEGATIVE_OUTCOMES = {
    RunOutcome.POSITIVE.value,
    RunOutcome.POSITIVE,
    RunOutcome.NEUTRAL.value,
    RunOutcome.NEUTRAL,
}

CLASS_ORDER = [
    AdventureClass.F,
    AdventureClass.E,
    AdventureClass.D,
    AdventureClass.C,
    AdventureClass.B,
    AdventureClass.A,
    AdventureClass.S,
]


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalize_reward_vector(vector: RewardVector) -> RewardVector:
    return RewardVector(
        integration_gain=clamp01(vector.integration_gain),
        compression_gain=clamp01(vector.compression_gain),
        replay_gain=clamp01(vector.replay_gain),
        witness_gain=clamp01(vector.witness_gain),
        route_clarity_gain=clamp01(vector.route_clarity_gain),
        quest_closure_gain=clamp01(vector.quest_closure_gain),
        blocker_honesty_gain=clamp01(vector.blocker_honesty_gain),
        phi_efficiency_gain=clamp01(vector.phi_efficiency_gain),
        regression_loss=clamp01(vector.regression_loss),
        bloat_loss=clamp01(vector.bloat_loss),
        contradiction_increase=clamp01(vector.contradiction_increase),
        orphaned_node_loss=clamp01(vector.orphaned_node_loss),
        replay_break_loss=clamp01(vector.replay_break_loss),
        control_surface_drift=clamp01(vector.control_surface_drift),
        unauthorized_activation_loss=clamp01(vector.unauthorized_activation_loss),
        docs_dishonesty_loss=clamp01(vector.docs_dishonesty_loss),
    )


def positive_score(vector: RewardVector) -> float:
    normalized = normalize_reward_vector(vector)
    weighted = sum(getattr(normalized, key) * weight for key, weight in POSITIVE_WEIGHTS.items())
    return round(weighted / POSITIVE_DENOMINATOR, 6)


def negative_score(vector: RewardVector) -> float:
    normalized = normalize_reward_vector(vector)
    weighted = sum(getattr(normalized, key) * weight for key, weight in NEGATIVE_WEIGHTS.items())
    return round(weighted / NEGATIVE_DENOMINATOR, 6)


def net_efficiency_score(vector: RewardVector) -> float:
    return round(100.0 * (positive_score(vector) - negative_score(vector)), 2)


def base_xp_delta(vector: RewardVector) -> int:
    return round(net_efficiency_score(vector))


def level_from_xp(xp_total: int) -> int:
    return max(0, min(100, int(xp_total) // 100))


def adventure_class_for_level(level: int) -> AdventureClass:
    if level >= 90:
        return AdventureClass.S
    if level >= 75:
        return AdventureClass.A
    if level >= 60:
        return AdventureClass.B
    if level >= 45:
        return AdventureClass.C
    if level >= 30:
        return AdventureClass.D
    if level >= 15:
        return AdventureClass.E
    return AdventureClass.F


def class_floor_xp(adventure_class: AdventureClass) -> int:
    floors = {
        AdventureClass.F: 0,
        AdventureClass.E: 1500,
        AdventureClass.D: 3000,
        AdventureClass.C: 4500,
        AdventureClass.B: 6000,
        AdventureClass.A: 7500,
        AdventureClass.S: 9000,
    }
    return floors[adventure_class]


def class_from_xp(xp_total: int) -> AdventureClass:
    return adventure_class_for_level(level_from_xp(xp_total))


def previous_class(adventure_class: AdventureClass) -> AdventureClass:
    index = CLASS_ORDER.index(adventure_class)
    if index == 0:
        return AdventureClass.F
    return CLASS_ORDER[index - 1]


def apply_reward_transform(
    base_delta: int,
    reward_transform: RewardTransform,
    outcome: RunOutcome,
) -> int:
    if outcome == RunOutcome.NEUTRAL:
        return 0
    if outcome == RunOutcome.NEGATIVE:
        if reward_transform == RewardTransform.PHI:
            return round(base_delta * 1.618)
        return base_delta
    if reward_transform == RewardTransform.BASE:
        return base_delta
    if reward_transform == RewardTransform.PHI:
        return round(base_delta * 1.618)
    if reward_transform == RewardTransform.DOUBLE_PHI:
        return round(base_delta * 3.236)
    if reward_transform == RewardTransform.SQUARED:
        return round(min((base_delta**2) / 100, 500))
    return base_delta


def select_reward_transform(
    *,
    cross_family: bool = False,
    clean_compression: bool = False,
    whole_front: bool = False,
    multi_surface: bool = False,
    crown_scale: bool = False,
    downstream_verifiers_green: bool = False,
    no_high_severity_residuals: bool = False,
) -> RewardTransform:
    if crown_scale and downstream_verifiers_green and no_high_severity_residuals:
        return RewardTransform.SQUARED
    if whole_front or multi_surface:
        return RewardTransform.DOUBLE_PHI
    if cross_family or clean_compression:
        return RewardTransform.PHI
    return RewardTransform.BASE


def outcome_from_vector(vector: RewardVector) -> RunOutcome:
    delta = net_efficiency_score(vector)
    if delta > 0:
        return RunOutcome.POSITIVE
    if delta < 0:
        return RunOutcome.NEGATIVE
    return RunOutcome.NEUTRAL


def evaluate_reward_run(
    *,
    run_id: str,
    scope: str,
    loop_id: str,
    agent_ids: list[str],
    baseline_snapshot_ref: str,
    post_snapshot_ref: str,
    reward_vector: RewardVector,
    reward_transform: RewardTransform = RewardTransform.BASE,
    residuals: list[str] | None = None,
    truth: str = "NEAR",
) -> RewardRunEvaluation:
    normalized = normalize_reward_vector(reward_vector)
    outcome = outcome_from_vector(normalized)
    xp_delta = base_xp_delta(normalized)
    if outcome == RunOutcome.POSITIVE:
        xp_delta = apply_reward_transform(xp_delta, reward_transform, outcome)
    else:
        xp_delta = apply_reward_transform(xp_delta, reward_transform, outcome)
    return RewardRunEvaluation(
        run_id=run_id,
        scope=scope,
        loop_id=loop_id,
        agent_ids=list(agent_ids),
        baseline_snapshot_ref=baseline_snapshot_ref,
        post_snapshot_ref=post_snapshot_ref,
        reward_vector=normalized,
        positive_score=positive_score(normalized),
        negative_score=negative_score(normalized),
        net_efficiency_score=net_efficiency_score(normalized),
        reward_transform=reward_transform,
        xp_delta=xp_delta,
        outcome=outcome,
        residuals=list(residuals or []),
        truth=truth,
    )


def apply_signed_xp(profile: AgentProgressProfile, xp_delta: int) -> AgentProgressProfile:
    xp_total = max(0, int(profile.xp_total))
    current_class = profile.adventure_class
    demotion_buffer = int(profile.demotion_buffer)

    if xp_delta >= 0:
        xp_total += int(xp_delta)
    else:
        floor = class_floor_xp(current_class)
        target = xp_total + int(xp_delta)
        if target >= floor:
            xp_total = target
        else:
            overflow = floor - max(target, 0)
            xp_total = floor
            demotion_buffer += overflow
            if demotion_buffer >= 200 and current_class != AdventureClass.F:
                current_class = previous_class(current_class)
                xp_total = class_floor_xp(current_class)
                demotion_buffer = 0

    level = level_from_xp(xp_total)
    derived_class = adventure_class_for_level(level)
    if xp_delta >= 0:
        current_class = derived_class
    else:
        current_class = current_class if current_class != AdventureClass.F or derived_class == AdventureClass.F else derived_class
        level = max(level, class_floor_xp(current_class) // 100)

    return replace(
        profile,
        xp_total=max(0, xp_total),
        level=level,
        adventure_class=current_class,
        demotion_buffer=demotion_buffer,
    )


def update_progress_profile(
    profile: AgentProgressProfile,
    *,
    xp_delta: int,
    outcome: RunOutcome,
    linked_agents: list[str] | None = None,
    quest_increment: int = 0,
) -> AgentProgressProfile:
    updated = apply_signed_xp(profile, xp_delta)
    recent = list(updated.recent_outcomes)
    recent.append(outcome.value)
    recent = recent[-5:]
    success_count = updated.success_count + (1 if outcome == RunOutcome.POSITIVE else 0)
    net_positive_count = updated.net_positive_count + (1 if outcome == RunOutcome.POSITIVE else 0)
    promotion_state = updated.promotion_state
    if updated.level >= 100:
        promotion_state = "ELIGIBLE"
    return replace(
        updated,
        run_count=updated.run_count + 1,
        quest_count=updated.quest_count + quest_increment,
        success_count=success_count,
        net_positive_count=net_positive_count,
        recent_outcomes=recent,
        promotion_state=promotion_state,
        linked_agents=sorted(set(updated.linked_agents + list(linked_agents or []))),
    )


def distribute_credit(
    *,
    quest_id: str,
    loop_id: str,
    frontier_id: str,
    primary_agent_id: str,
    assist_agent_ids: list[str],
    parent_chain_ids: list[str],
    reward_transform: RewardTransform,
    base_xp_delta: int,
    final_xp_delta: int,
    outcome: RunOutcome,
    truth: str = "NEAR",
) -> QuestOutcomeCredit:
    credit_shares: dict[str, int] = {}
    primary_share = round(final_xp_delta * 0.7)
    parent_share_total = round(final_xp_delta * 0.2)
    assist_share_total = final_xp_delta - primary_share - parent_share_total

    credit_shares[primary_agent_id] = primary_share

    parent_targets = list(parent_chain_ids)
    assist_targets = list(assist_agent_ids)
    if not assist_targets:
        parent_share_total += assist_share_total
        assist_share_total = 0

    if parent_targets and parent_share_total:
        split = round(parent_share_total / len(parent_targets))
        for agent_id in parent_targets:
            credit_shares[agent_id] = credit_shares.get(agent_id, 0) + split
    elif parent_share_total:
        credit_shares[primary_agent_id] += parent_share_total

    if assist_targets and assist_share_total:
        split = round(assist_share_total / len(assist_targets))
        for agent_id in assist_targets:
            credit_shares[agent_id] = credit_shares.get(agent_id, 0) + split

    return QuestOutcomeCredit(
        quest_id=quest_id,
        loop_id=loop_id,
        frontier_id=frontier_id,
        primary_agent_id=primary_agent_id,
        assist_agent_ids=list(assist_targets),
        parent_chain_ids=list(parent_targets),
        reward_transform=reward_transform,
        base_xp_delta=base_xp_delta,
        final_xp_delta=final_xp_delta,
        outcome=outcome,
        credit_shares=credit_shares,
        truth=truth,
    )


def promotion_requirements_met(
    profile: AgentProgressProfile,
    *,
    merge_approved: bool,
    no_replay_breach: bool,
    no_docs_dishonesty: bool,
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if profile.level < 100:
        failures.append("level below 100")
    if len(profile.recent_outcomes) < 5:
        failures.append("fewer than 5 recent outcomes")
    if any(item not in NON_NEGATIVE_OUTCOMES for item in profile.recent_outcomes[-5:]):
        failures.append("last 5 outcomes not all non-negative")
    if not no_replay_breach:
        failures.append("unresolved replay breach")
    if not no_docs_dishonesty:
        failures.append("docs dishonesty in promotion window")
    if not merge_approved:
        failures.append("merge or governance approval missing")
    return not failures, failures


def build_promotion_record(
    profile: AgentProgressProfile,
    *,
    merge_approved: bool,
    no_replay_breach: bool,
    no_docs_dishonesty: bool,
    promotion_seed: str,
    truth: str = "NEAR",
) -> PromotionEligibilityRecord:
    eligible, failures = promotion_requirements_met(
        profile,
        merge_approved=merge_approved,
        no_replay_breach=no_replay_breach,
        no_docs_dishonesty=no_docs_dishonesty,
    )
    requirements = [
        "level 100",
        "last 5 run outcomes non-negative",
        "no unresolved replay breach",
        "no docs dishonesty loss in promotion window",
        "merge/governance approval",
    ]
    return PromotionEligibilityRecord(
        agent_id=profile.agent_id,
        level=profile.level,
        adventure_class=profile.adventure_class,
        eligible=eligible,
        requirements=requirements,
        gating_failures=failures,
        promotion_seed=promotion_seed,
        truth=truth,
    )


def build_mini_hive_charter(
    *,
    agent_id: str,
    promotion_ref: str,
    sub_hive_frontier_id: str,
    seat_budget: int,
    truth: str = "NEAR",
) -> MiniHiveCharter:
    return MiniHiveCharter(
        charter_id=f"MINIHIVE-{agent_id}",
        agent_id=agent_id,
        promotion_ref=promotion_ref,
        sub_hive_frontier_id=sub_hive_frontier_id,
        seat_budget=seat_budget,
        governance_required=True,
        merge_required=True,
        activation_state="LOCKED",
        truth=truth,
    )


def build_reward_steering_profile(
    profile: AgentProgressProfile,
    *,
    replay_breach_open: bool = False,
    docs_dishonesty_recent: bool = False,
) -> dict[str, Any]:
    recent = profile.recent_outcomes[-5:]
    recent_positive_runs = sum(1 for item in recent if item == RunOutcome.POSITIVE.value)
    recent_net_losses = sum(1 for item in recent if item == RunOutcome.NEGATIVE.value)
    return {
        "agent_id": profile.agent_id,
        "adventure_class": profile.adventure_class.value,
        "recent_outcomes": recent,
        "recent_positive_runs": recent_positive_runs,
        "recent_net_losses": recent_net_losses,
        "replay_breach_open": replay_breach_open,
        "docs_dishonesty_recent": docs_dishonesty_recent,
    }


def apply_reward_steering(
    score_vector: MotionScoreVector,
    steering_profile: dict[str, Any] | None,
) -> tuple[MotionScoreVector, dict[str, Any]]:
    if not steering_profile:
        return score_vector, {"applied": False, "reason": "no steering profile"}

    adjusted = score_vector
    applied_rules: list[str] = []
    adventure_class = steering_profile.get("adventure_class", AdventureClass.F.value)
    recent_positive_runs = int(steering_profile.get("recent_positive_runs", 0))
    recent_net_losses = int(steering_profile.get("recent_net_losses", 0))
    replay_breach_open = bool(steering_profile.get("replay_breach_open", False))
    docs_dishonesty_recent = bool(steering_profile.get("docs_dishonesty_recent", False))

    if adventure_class in {AdventureClass.S.value, AdventureClass.A.value} and recent_positive_runs >= 5 and not replay_breach_open:
        adjusted = replace(
            adjusted,
            integration_yield=round(adjusted.integration_yield + 0.15, 6),
            replay_readiness=round(adjusted.replay_readiness + 0.10, 6),
        )
        applied_rules.append("high-rank-positive-boost")

    if adventure_class in {AdventureClass.D.value, AdventureClass.E.value, AdventureClass.F.value} and recent_net_losses > 0:
        adjusted = replace(
            adjusted,
            branch_burden=round(adjusted.branch_burden + 0.15, 6),
            risk=round(adjusted.risk + 0.10, 6),
        )
        applied_rules.append("low-rank-loss-penalty")

    if replay_breach_open or docs_dishonesty_recent:
        adjusted = replace(
            adjusted,
            risk=round(adjusted.risk + 0.30, 6),
            truth_readiness=round(adjusted.truth_readiness - 0.25, 6),
        )
        applied_rules.append("breach-penalty")

    return adjusted, {
        "applied": bool(applied_rules),
        "rules": applied_rules,
        "profile": steering_profile,
    }
