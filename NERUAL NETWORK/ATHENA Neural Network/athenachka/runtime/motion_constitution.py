from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any

from ..contracts import (
    MotionAction,
    MotionCandidatePacket,
    MotionConstitutionState,
    MotionDecision,
    MotionReceipt,
    MotionScoreVector,
    stable_hash,
)
from .reward_overlay import apply_reward_steering


ACCEPTED_SOURCE_KINDS = (
    "quest_board",
    "agent_registry",
    "committee_output",
    "immune_scheduler_output",
    "continuation_seed",
)

TRUTH_BURDEN_WITNESS_FLOOR = {
    "OK": 2,
    "NEAR": 1,
    "AMBIG": 1,
    "FAIL": 1,
}

REFUSAL_BLOCKERS = {"omega_denial", "scope_inadmissible"}
QUARANTINE_BLOCKERS = {
    "forbidden_contradiction",
    "hard_contradiction",
    "replay_divergence",
    "hazardous_failure",
    "policy_breach",
}
HELP_BLOCKERS = {"external_dependency", "owner_help_missing"}
COMMITTEE_BLOCKERS = {"committee_pending_conflict", "stewardship_gate", "branch_limit"}
FORWARD_BLOCKERS = {"forward_circulation_blocked"}
REPLAY_BLOCKERS = {"replay_missing"}


class MotionConstitutionError(ValueError):
    """Base error for the offline action chamber."""


class MotionCandidateError(MotionConstitutionError):
    """Raised when a candidate packet is structurally invalid."""


def accepted_source_kinds() -> tuple[str, ...]:
    return ACCEPTED_SOURCE_KINDS


def action_alphabet() -> tuple[str, ...]:
    return tuple(action.value for action in MotionAction)


def bootstrap_motion_state(
    *,
    docs_gate_status: str = "blocked-by-missing-credentials",
    activation_threshold: float = 1.0,
) -> MotionConstitutionState:
    return MotionConstitutionState(
        route_graph={
            "resolved_dependencies": [],
            "current_fronts": [],
            "active_targets": [],
        },
        pressure_field={
            "active_families": [],
            "recent_candidates": [],
            "committee_pending_families": [],
        },
        legality_projector={
            "sigma": ["AppA", "AppI", "AppM"],
            "admissible_source_kinds": list(ACCEPTED_SOURCE_KINDS),
            "activation_threshold": activation_threshold,
        },
        immune_state={
            "quarantined_candidates": [],
            "blocked_routes": ["Trading Bot"] if docs_gate_status.startswith("blocked") else [],
        },
        replay_memory={
            "recent_actions": [],
        },
        hysteresis_memory={},
        docs_gate_status=docs_gate_status,
    )


def constitutional_score(score_vector: MotionScoreVector) -> float:
    numerator = (
        score_vector.closure_gain
        + score_vector.heart_need
        + score_vector.replay_readiness
        + score_vector.integration_yield
        + score_vector.organ_adjacency
        + score_vector.seed_value
    )
    denominator = (
        1.0
        + score_vector.cost
        + score_vector.replay_cost
        + score_vector.risk
        + score_vector.failure_debt
        + score_vector.branch_burden
        + score_vector.contradiction_heat
    )
    pressure_factor = 1.0 + (0.5 * score_vector.pressure_gradient)
    return (numerator * pressure_factor) / denominator


def effective_score_vector(
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
) -> MotionScoreVector:
    return _effective_score_vector(candidate, state)


def evaluate_candidate(
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
    *,
    activation_threshold: float | None = None,
) -> tuple[MotionDecision, MotionReceipt, MotionConstitutionState]:
    _validate_candidate(candidate)
    trace = ["OBSERVE"]

    effective_vector = _effective_score_vector(candidate, state)
    score = constitutional_score(effective_vector)
    trace.append("SCORE")

    threshold = activation_threshold
    if threshold is None:
        threshold = float(state.legality_projector.get("activation_threshold", 1.0))

    action, legal, residuals, replay_obligations, note = _gate_candidate(
        candidate=candidate,
        state=state,
        effective_vector=effective_vector,
        score=score,
        activation_threshold=threshold,
    )
    trace.append("GATE")

    successor_seed = candidate.continuation_seed or "MotionConstitution_L1::Parameterization"
    next_state, replay_store_update = _store_replay(
        candidate=candidate,
        state=state,
        action=action,
        score=score,
        successor_seed=successor_seed,
    )

    trace.extend(["ACT/RECEIPT", "REPLAY_STORE", "SEED"])

    decision = MotionDecision(
        candidate_id=candidate.candidate_id,
        action=action,
        constitutional_score=score,
        legal=legal,
        residuals=list(residuals),
        replay_obligations=list(replay_obligations),
        successor_seed=successor_seed,
        note=note,
    )
    receipt = MotionReceipt(
        receipt_id=f"MCR-{candidate.candidate_id}",
        candidate_id=candidate.candidate_id,
        action=action,
        automaton_trace=trace,
        constitutional_score=score,
        replay_store_update=replay_store_update,
        successor_seed=successor_seed,
        residuals=list(residuals),
        note=note,
    )
    return decision, receipt, next_state


class MotionConstitutionL1:
    """Small stateful wrapper around the pure offline evaluator."""

    def __init__(
        self,
        state: MotionConstitutionState | None = None,
        *,
        activation_threshold: float = 1.0,
    ) -> None:
        self.state = state or bootstrap_motion_state(activation_threshold=activation_threshold)
        self.activation_threshold = activation_threshold

    def evaluate_candidate(
        self,
        candidate: MotionCandidatePacket,
    ) -> tuple[MotionDecision, MotionReceipt]:
        decision, receipt, next_state = evaluate_candidate(
            candidate,
            self.state,
            activation_threshold=self.activation_threshold,
        )
        self.state = next_state
        return decision, receipt


def _validate_candidate(candidate: MotionCandidatePacket) -> None:
    if not candidate.candidate_id:
        raise MotionCandidateError("candidate_id is required")
    if not candidate.source_kind:
        raise MotionCandidateError("source_kind is required")
    if not candidate.source_ref:
        raise MotionCandidateError("source_ref is required")
    if not candidate.target_organ:
        raise MotionCandidateError("target_organ is required")
    if not candidate.expected_packet_type:
        raise MotionCandidateError("expected_packet_type is required")


def _effective_score_vector(
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
) -> MotionScoreVector:
    branch_burden = candidate.score_vector.branch_burden + _duplicate_branch_penalty(candidate, state)
    adjusted = replace(candidate.score_vector, branch_burden=branch_burden)
    steering_profile = state.reward_profiles.get(candidate.agent_id, {}) if candidate.agent_id else {}
    adjusted, _ = apply_reward_steering(adjusted, steering_profile)
    return adjusted


def _duplicate_branch_penalty(
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
) -> float:
    active_families = set(state.pressure_field.get("active_families", []))
    recent_candidates = set(state.pressure_field.get("recent_candidates", []))
    if candidate.current_family in active_families or candidate.source_ref in recent_candidates:
        return 1.0
    return 0.0


def _gate_candidate(
    *,
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
    effective_vector: MotionScoreVector,
    score: float,
    activation_threshold: float,
) -> tuple[MotionAction, bool, list[str], list[str], str]:
    witness_signature = stable_hash(sorted(candidate.witness_refs))
    replay_signature = stable_hash(sorted(candidate.replay_refs))
    immune_signature = stable_hash(state.immune_state)
    previous = state.hysteresis_memory.get(candidate.candidate_id, {})

    if not _is_admissible(candidate, state):
        return (
            MotionAction.REFUSE_INADMISSIBLE,
            False,
            ["candidate is outside the legality projector"],
            [],
            "Omega denial or scope inadmissibility forced refusal.",
        )

    if previous.get("last_action") == MotionAction.REFUSE_INADMISSIBLE.value:
        if (
            previous.get("witness_signature") == witness_signature
            and previous.get("replay_signature") == replay_signature
        ):
            return (
                MotionAction.REFUSE_INADMISSIBLE,
                False,
                ["refusal hysteresis remains active until witness or replay changes"],
                [],
                "Refused candidates cannot reactivate until witness or replay evidence changes.",
            )

    if _requires_quarantine(candidate, state):
        return (
            MotionAction.QUARANTINE,
            False,
            ["hazardous contradiction or policy breach blocks circulation"],
            ["store quarantine replay witness"],
            "Forbidden contradiction or hazardous failure forced quarantine.",
        )

    if previous.get("last_action") == MotionAction.QUARANTINE.value:
        if (
            previous.get("immune_signature") == immune_signature
            and previous.get("replay_signature") == replay_signature
        ):
            return (
                MotionAction.QUARANTINE,
                False,
                ["quarantine hysteresis remains active until immune or replay state changes"],
                ["store quarantine replay witness"],
                "Quarantined candidates cannot reactivate until immune or replay state changes.",
            )

    if _has_replay_gap(candidate, effective_vector):
        return (
            MotionAction.REPLAY_FIRST,
            True,
            ["replay proof is the primary gap"],
            ["attach replay refs", "prove replay closure"],
            "Replay dependency outranks witness and help requests.",
        )

    if not _witness_burden_met(candidate, effective_vector):
        return (
            MotionAction.REQUEST_WITNESSES,
            True,
            ["truth burden has not been met"],
            [],
            "Witness burden is the primary blocker.",
        )

    if _requires_help(candidate, state):
        return (
            MotionAction.REQUEST_HELP,
            True,
            ["external dependency or owner help gap remains"],
            [],
            "Dependency pressure requires help before motion.",
        )

    if _requires_committee(candidate, state):
        return (
            MotionAction.ESCALATE_TO_COMMITTEE,
            True,
            ["stewardship, branch-limit, or committee-pending conflict suppresses activation"],
            [],
            "Committee escalation outranks seed compression when stewardship law fires.",
        )

    if _forward_blocked_but_seed_alive(candidate):
        return (
            MotionAction.COMPRESS_TO_SEED,
            True,
            ["forward circulation is blocked but continuation value remains alive"],
            [],
            "Seed compression wins when motion is blocked but continuation value remains.",
        )

    if score >= activation_threshold:
        return (
            MotionAction.ACTIVATE_NOW,
            True,
            [],
            ["store replay signature"],
            "Candidate cleared legality and threshold gates.",
        )

    return (
        MotionAction.HOLD,
        True,
        ["candidate is lawful but below the activation threshold"],
        [],
        "Low constitutional score keeps the candidate on hold.",
    )


def _is_admissible(candidate: MotionCandidatePacket, state: MotionConstitutionState) -> bool:
    admissible_source_kinds = set(
        state.legality_projector.get("admissible_source_kinds", ACCEPTED_SOURCE_KINDS)
    )
    blockers = set(candidate.blockers)
    if candidate.source_kind not in admissible_source_kinds:
        return False
    if blockers & REFUSAL_BLOCKERS:
        return False
    return True


def _requires_quarantine(
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
) -> bool:
    blockers = set(candidate.blockers)
    _ = state
    return bool(blockers & QUARANTINE_BLOCKERS)


def _has_replay_gap(candidate: MotionCandidatePacket, score_vector: MotionScoreVector) -> bool:
    blockers = set(candidate.blockers)
    if blockers & REPLAY_BLOCKERS:
        return True
    if not candidate.replay_refs:
        return True
    return score_vector.replay_readiness < 0.5


def _witness_burden_met(candidate: MotionCandidatePacket, score_vector: MotionScoreVector) -> bool:
    required_witnesses = TRUTH_BURDEN_WITNESS_FLOOR.get(candidate.truth_burden.upper(), 1)
    return len(candidate.witness_refs) >= required_witnesses and score_vector.truth_readiness >= 0.5


def _requires_help(candidate: MotionCandidatePacket, state: MotionConstitutionState) -> bool:
    blockers = set(candidate.blockers)
    if blockers & HELP_BLOCKERS:
        return True
    resolved = set(state.route_graph.get("resolved_dependencies", []))
    return any(dependency not in resolved for dependency in candidate.dependencies)


def _requires_committee(candidate: MotionCandidatePacket, state: MotionConstitutionState) -> bool:
    blockers = set(candidate.blockers)
    if blockers & COMMITTEE_BLOCKERS:
        return True
    pending_families = set(state.pressure_field.get("committee_pending_families", []))
    if candidate.current_family in pending_families:
        return True
    return any(reference.startswith("pending:") for reference in candidate.committee_refs)


def _forward_blocked_but_seed_alive(candidate: MotionCandidatePacket) -> bool:
    blockers = set(candidate.blockers)
    return bool(
        blockers & FORWARD_BLOCKERS
        and candidate.continuation_seed
        and candidate.score_vector.seed_value > 0.0
    )


def _store_replay(
    *,
    candidate: MotionCandidatePacket,
    state: MotionConstitutionState,
    action: MotionAction,
    score: float,
    successor_seed: str,
) -> tuple[MotionConstitutionState, dict[str, Any]]:
    next_state = deepcopy(state)
    witness_signature = stable_hash(sorted(candidate.witness_refs))
    replay_signature = stable_hash(sorted(candidate.replay_refs))

    quarantined = list(next_state.immune_state.get("quarantined_candidates", []))
    if action == MotionAction.QUARANTINE and candidate.candidate_id not in quarantined:
        quarantined.append(candidate.candidate_id)
    if action != MotionAction.QUARANTINE and candidate.candidate_id in quarantined:
        quarantined.remove(candidate.candidate_id)
    next_state.immune_state["quarantined_candidates"] = quarantined

    immune_signature = stable_hash(next_state.immune_state)

    update = {
        "candidate_id": candidate.candidate_id,
        "action": action.value,
        "constitutional_score": round(score, 6),
        "witness_signature": witness_signature,
        "replay_signature": replay_signature,
        "immune_signature": immune_signature,
        "successor_seed": successor_seed,
    }

    next_state.hysteresis_memory[candidate.candidate_id] = {
        "last_action": action.value,
        "witness_signature": witness_signature,
        "replay_signature": replay_signature,
        "immune_signature": immune_signature,
    }

    recent_actions = list(next_state.replay_memory.get("recent_actions", []))
    recent_actions.append(update)
    next_state.replay_memory["recent_actions"] = recent_actions[-32:]

    recent_candidates = list(next_state.pressure_field.get("recent_candidates", []))
    if candidate.source_ref not in recent_candidates:
        recent_candidates.append(candidate.source_ref)
    next_state.pressure_field["recent_candidates"] = recent_candidates[-32:]

    active_families = list(next_state.pressure_field.get("active_families", []))
    if action == MotionAction.ACTIVATE_NOW and candidate.current_family not in active_families:
        active_families.append(candidate.current_family)
    next_state.pressure_field["active_families"] = active_families

    return next_state, update
