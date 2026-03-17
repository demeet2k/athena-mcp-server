from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import re

from ..contracts import (
    CommitteePack,
    ContinuationSeed,
    GovernanceApproval,
    MergeAttempt,
    MergeDecision,
    MergeDestination,
    MergeLedgerEntry,
    MergeState,
    ReplayPack,
    WitnessPack,
    stable_hash,
)


TERMINAL_DESTINATIONS = {
    MergeState.DECIDED_COMMIT: MergeDestination.COMMIT,
    MergeState.DECIDED_DEFER_NEAR: MergeDestination.DEFER_NEAR,
    MergeState.DECIDED_DEFER_AMBIG: MergeDestination.DEFER_AMBIG,
    MergeState.DECIDED_REFUSE: MergeDestination.REFUSE,
    MergeState.DECIDED_QUARANTINE: MergeDestination.QUARANTINE_FAIL,
}

TRANSITIONS: dict[MergeState, tuple[MergeState, ...]] = {
    MergeState.PROPOSED: (MergeState.BUNDLED,),
    MergeState.BUNDLED: (MergeState.DISSENT_SURFACED,),
    MergeState.DISSENT_SURFACED: (MergeState.VERIFY_PENDING,),
    MergeState.VERIFY_PENDING: (
        MergeState.GOVERNANCE_PENDING,
        MergeState.DECIDED_DEFER_NEAR,
        MergeState.DECIDED_DEFER_AMBIG,
        MergeState.DECIDED_QUARANTINE,
    ),
    MergeState.GOVERNANCE_PENDING: (
        MergeState.DECIDED_COMMIT,
        MergeState.DECIDED_REFUSE,
    ),
    MergeState.DECIDED_COMMIT: (),
    MergeState.DECIDED_DEFER_NEAR: (),
    MergeState.DECIDED_DEFER_AMBIG: (),
    MergeState.DECIDED_REFUSE: (),
    MergeState.DECIDED_QUARANTINE: (),
}

ARTIFACT_REQUIREMENTS: dict[MergeState, list[str]] = {
    MergeState.PROPOSED: ["CommitteePack"],
    MergeState.BUNDLED: ["CommitteePack"],
    MergeState.DISSENT_SURFACED: ["CommitteePack", "DissentPacket"],
    MergeState.VERIFY_PENDING: ["CommitteePack", "WitnessPack", "ReplayPack"],
    MergeState.GOVERNANCE_PENDING: ["CommitteePack", "GovernanceApproval"],
    MergeState.DECIDED_COMMIT: ["CommitteePack", "DeltaPacket", "MergeLedgerEntry", "ContinuationSeed"],
    MergeState.DECIDED_DEFER_NEAR: ["CommitteePack", "NearPack", "MergeLedgerEntry", "ContinuationSeed"],
    MergeState.DECIDED_DEFER_AMBIG: ["CommitteePack", "AmbigPack", "MergeLedgerEntry", "ContinuationSeed"],
    MergeState.DECIDED_REFUSE: ["CommitteePack", "FailPack", "MergeLedgerEntry", "ContinuationSeed"],
    MergeState.DECIDED_QUARANTINE: ["CommitteePack", "FailPack", "ConflictPacket", "MergeLedgerEntry", "ContinuationSeed"],
}

PACKET_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


class MergeBoundaryError(ValueError):
    """Base error for merge boundary failures."""


class MergeTransitionError(MergeBoundaryError):
    """Raised when a transition bypasses the lawful graph."""


class MergeGuardError(MergeBoundaryError):
    """Raised when a transition guard is not satisfied."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def allowed_transitions(state: MergeState | None = None) -> dict[MergeState, tuple[MergeState, ...]] | tuple[MergeState, ...]:
    if state is None:
        return dict(TRANSITIONS)
    return TRANSITIONS[state]


def destination_for_terminal_state(state: MergeState) -> MergeDestination | None:
    return TERMINAL_DESTINATIONS.get(state)


def emit_required_artifacts(state: MergeState) -> list[str]:
    return list(ARTIFACT_REQUIREMENTS[state])


def bootstrap_merge_attempt(committee_pack: CommitteePack, merge_id: str | None = None) -> MergeAttempt:
    if not committee_pack.committee_pack_id:
        raise MergeGuardError("committee_pack_id is required")
    derived_id = merge_id or stable_hash(
        {
            "committee_pack_id": committee_pack.committee_pack_id,
            "candidate_delta_refs": committee_pack.candidate_delta_refs,
        }
    )[:16]
    return MergeAttempt(
        merge_id=f"merge-{derived_id}",
        committee_pack=committee_pack,
        current_state=MergeState.PROPOSED,
    )


def advance_merge_state(
    attempt: MergeAttempt,
    target_state: MergeState,
    *,
    witness_pack: WitnessPack | None = None,
    replay_pack: ReplayPack | None = None,
    governance_approval: GovernanceApproval | None = None,
    continuation_seed: ContinuationSeed | None = None,
    bounded_residual: bool = False,
    underdetermined_conflict: bool = False,
    hard_contradiction: bool = False,
    replay_divergence: bool = False,
    policy_breach: bool = False,
    ledger_appendable: bool = False,
) -> tuple[MergeAttempt, MergeDecision]:
    current_state = attempt.current_state
    if target_state not in TRANSITIONS[current_state]:
        raise MergeTransitionError(
            f"illegal merge transition: {current_state.value} -> {target_state.value}"
        )

    residuals: list[str] = []
    _validate_transition(
        attempt=attempt,
        target_state=target_state,
        witness_pack=witness_pack,
        replay_pack=replay_pack,
        governance_approval=governance_approval,
        continuation_seed=continuation_seed,
        bounded_residual=bounded_residual,
        underdetermined_conflict=underdetermined_conflict,
        hard_contradiction=hard_contradiction,
        replay_divergence=replay_divergence,
        policy_breach=policy_breach,
        ledger_appendable=ledger_appendable,
        residuals=residuals,
    )

    next_attempt = replace(
        attempt,
        current_state=target_state,
        witness_pack=witness_pack or attempt.witness_pack,
        replay_pack=replay_pack or attempt.replay_pack,
        governance_approval=governance_approval or attempt.governance_approval,
        continuation_seed=continuation_seed or attempt.continuation_seed,
        residuals=list(residuals),
    )
    decision = MergeDecision(
        merge_id=attempt.merge_id,
        current_state=target_state,
        chosen_destination=destination_for_terminal_state(target_state),
        required_artifacts=emit_required_artifacts(target_state),
        residuals=list(residuals),
        next_seed=(continuation_seed.next_seed if continuation_seed else ""),
    )
    return next_attempt, decision


def build_merge_ledger_entry(
    *,
    decision: MergeDecision,
    committee_pack: CommitteePack,
    continuation_seed: ContinuationSeed,
    entry_index: int,
    witness_pack: WitnessPack | None = None,
    replay_pack: ReplayPack | None = None,
    governance_approval: GovernanceApproval | None = None,
    timestamp: str | None = None,
) -> MergeLedgerEntry:
    if decision.chosen_destination is None:
        raise MergeGuardError("only terminal merge decisions may be written to the ledger")
    if entry_index < 1:
        raise MergeGuardError("entry_index must be positive and monotonic")
    return MergeLedgerEntry(
        entry_id=f"MLE-{entry_index:04d}",
        committee_pack_ref=committee_pack.committee_pack_id,
        chosen_destination=decision.chosen_destination,
        supporting_witnesses=list(witness_pack.witness_refs) if witness_pack else list(committee_pack.witness_refs),
        replay_bundle_ref=replay_pack.replay_pack_id if replay_pack else None,
        governance_approval_ref=governance_approval.approval_id if governance_approval else None,
        dissent_refs=list(committee_pack.dissent_refs),
        continuation_seed_ref=continuation_seed.seed_id,
        timestamp=timestamp or utc_now(),
    )


def _validate_transition(
    *,
    attempt: MergeAttempt,
    target_state: MergeState,
    witness_pack: WitnessPack | None,
    replay_pack: ReplayPack | None,
    governance_approval: GovernanceApproval | None,
    continuation_seed: ContinuationSeed | None,
    bounded_residual: bool,
    underdetermined_conflict: bool,
    hard_contradiction: bool,
    replay_divergence: bool,
    policy_breach: bool,
    ledger_appendable: bool,
    residuals: list[str],
) -> None:
    committee_pack = attempt.committee_pack

    if target_state == MergeState.BUNDLED:
        if not committee_pack.candidate_delta_refs:
            raise MergeGuardError("candidate deltas are required before bundling")
        if not all(_is_valid_packet_id(item) for item in committee_pack.candidate_delta_refs):
            raise MergeGuardError("all candidate delta refs must be valid packet ids")
        return

    if target_state == MergeState.DISSENT_SURFACED:
        if committee_pack.dissent_refs is None:
            raise MergeGuardError("dissent slots must be materialized before review")
        return

    if target_state == MergeState.VERIFY_PENDING:
        if witness_pack is None or not witness_pack.witness_refs:
            raise MergeGuardError("witness refs are required before verification")
        if replay_pack is None or not replay_pack.replay_refs:
            raise MergeGuardError("replay refs are required before verification")
        if witness_pack.committee_pack_id != committee_pack.committee_pack_id:
            raise MergeGuardError("witness pack must target the same committee pack")
        if replay_pack.committee_pack_id != committee_pack.committee_pack_id:
            raise MergeGuardError("replay pack must target the same committee pack")
        return

    if target_state == MergeState.GOVERNANCE_PENDING:
        witness_ok = bool((witness_pack or attempt.witness_pack) and (witness_pack or attempt.witness_pack).route_witness_ref)
        replay_ok = bool((replay_pack or attempt.replay_pack) and (replay_pack or attempt.replay_pack).replay_closure_ref)
        if not witness_ok:
            raise MergeGuardError("route witness must be sufficient before governance")
        if not replay_ok:
            raise MergeGuardError("replay closure must be sufficient before governance")
        return

    if target_state == MergeState.DECIDED_DEFER_NEAR:
        if not bounded_residual:
            raise MergeGuardError("bounded residual is required for DEFER_NEAR")
        if continuation_seed is None or not continuation_seed.next_seed:
            raise MergeGuardError("continuation seed is required for DEFER_NEAR")
        residuals.append("bounded residual remains with a lawful closure path")
        return

    if target_state == MergeState.DECIDED_DEFER_AMBIG:
        if not underdetermined_conflict:
            raise MergeGuardError("underdetermined conflict is required for DEFER_AMBIG")
        if continuation_seed is None or not continuation_seed.next_seed:
            raise MergeGuardError("continuation seed is required for DEFER_AMBIG")
        residuals.append("candidate conflict remains underdetermined")
        return

    if target_state == MergeState.DECIDED_QUARANTINE:
        if not any([hard_contradiction, replay_divergence, policy_breach]):
            raise MergeGuardError("a hard contradiction, replay divergence, or policy breach is required for quarantine")
        if continuation_seed is None or not continuation_seed.next_seed:
            raise MergeGuardError("continuation seed is required for quarantine")
        if hard_contradiction:
            residuals.append("hard contradiction blocks circulation")
        if replay_divergence:
            residuals.append("replay divergence blocks circulation")
        if policy_breach:
            residuals.append("policy breach blocks circulation")
        return

    if target_state == MergeState.DECIDED_COMMIT:
        if governance_approval is None or not governance_approval.approved:
            raise MergeGuardError("explicit governance approval is required for commit")
        if governance_approval.committee_pack_id != committee_pack.committee_pack_id:
            raise MergeGuardError("governance approval must target the same committee pack")
        if not ledger_appendable:
            raise MergeGuardError("append-only ledger must be writable before commit")
        if continuation_seed is None or not continuation_seed.next_seed:
            raise MergeGuardError("continuation seed is required for commit")
        return

    if target_state == MergeState.DECIDED_REFUSE:
        if governance_approval is None or governance_approval.approved:
            raise MergeGuardError("explicit governance denial is required for refuse")
        if governance_approval.committee_pack_id != committee_pack.committee_pack_id:
            raise MergeGuardError("governance approval must target the same committee pack")
        if continuation_seed is None or not continuation_seed.next_seed:
            raise MergeGuardError("continuation seed is required for refuse")
        residuals.append("governance denied the claimed scope")
        return

    raise MergeTransitionError(f"unsupported target state: {target_state.value}")


def _is_valid_packet_id(value: str) -> bool:
    return bool(value and PACKET_ID_PATTERN.match(value))
