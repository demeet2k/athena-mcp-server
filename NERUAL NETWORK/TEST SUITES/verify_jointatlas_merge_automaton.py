from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATHENA_PACKAGE_ROOT = ROOT / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import (  # noqa: E402
    CommitteePack,
    ContinuationSeed,
    GovernanceApproval,
    MergeDestination,
    MergeState,
    ReplayPack,
    WitnessPack,
)
from athenachka.immune.merge_boundary import (  # noqa: E402
    MergeGuardError,
    MergeTransitionError,
    advance_merge_state,
    allowed_transitions,
    bootstrap_merge_attempt,
    build_merge_ledger_entry,
    destination_for_terminal_state,
)


def build_committee_pack(case_id: str, *, candidate_delta_refs: list[str] | None = None) -> CommitteePack:
    return CommitteePack(
        committee_pack_id=f"CP-{case_id}",
        candidate_delta_refs=candidate_delta_refs or [f"PKT-{case_id}-001", f"PKT-{case_id}-002"],
        dissent_refs=[],
        witness_refs=[f"WIT-{case_id}-001"],
        replay_refs=[f"RPL-{case_id}-001"],
        governance_profile={
            "committee": "JointAtlas",
            "quorum_model": "metadata-only-v0",
            "weighting_model": "metadata-only-v0",
        },
        continuation_seed_ref=f"SEED-{case_id}",
        route_witness_ref=f"ROUTE-{case_id}",
        replay_closure_ref=f"REPLAY-CLOSURE-{case_id}",
    )


def build_witness_pack(case_id: str, committee_pack_id: str) -> WitnessPack:
    return WitnessPack(
        witness_pack_id=f"WPK-{case_id}",
        committee_pack_id=committee_pack_id,
        witness_refs=[f"WIT-{case_id}-001", f"WIT-{case_id}-002"],
        route_witness_ref=f"ROUTE-{case_id}",
    )


def build_replay_pack(case_id: str, committee_pack_id: str) -> ReplayPack:
    return ReplayPack(
        replay_pack_id=f"RPK-{case_id}",
        committee_pack_id=committee_pack_id,
        replay_refs=[f"RPL-{case_id}-001", f"RPL-{case_id}-002"],
        replay_closure_ref=f"REPLAY-CLOSURE-{case_id}",
    )


def build_seed(case_id: str) -> ContinuationSeed:
    return ContinuationSeed(
        seed_id=f"SEED-{case_id}",
        next_seed="MotionConstitution_L1",
        objective="Replace boolean governance gating with typed motion scoring.",
    )


def build_approval(case_id: str, committee_pack_id: str, approved: bool) -> GovernanceApproval:
    return GovernanceApproval(
        approval_id=f"GOV-{case_id}",
        committee_pack_id=committee_pack_id,
        approved=approved,
        approver_refs=["council::01", "council::02"],
    )


def drive_to_verify_pending(case_id: str):
    committee_pack = build_committee_pack(case_id)
    attempt = bootstrap_merge_attempt(committee_pack)
    attempt, _ = advance_merge_state(attempt, MergeState.BUNDLED)
    attempt, _ = advance_merge_state(attempt, MergeState.DISSENT_SURFACED)
    witness_pack = build_witness_pack(case_id, committee_pack.committee_pack_id)
    replay_pack = build_replay_pack(case_id, committee_pack.committee_pack_id)
    attempt, _ = advance_merge_state(
        attempt,
        MergeState.VERIFY_PENDING,
        witness_pack=witness_pack,
        replay_pack=replay_pack,
    )
    return attempt, committee_pack, witness_pack, replay_pack


def assert_transition_graph() -> dict[str, object]:
    graph = allowed_transitions()
    assert graph[MergeState.PROPOSED] == (MergeState.BUNDLED,)
    assert graph[MergeState.BUNDLED] == (MergeState.DISSENT_SURFACED,)
    assert graph[MergeState.DISSENT_SURFACED] == (MergeState.VERIFY_PENDING,)
    assert graph[MergeState.VERIFY_PENDING] == (
        MergeState.GOVERNANCE_PENDING,
        MergeState.DECIDED_DEFER_NEAR,
        MergeState.DECIDED_DEFER_AMBIG,
        MergeState.DECIDED_QUARANTINE,
    )
    assert graph[MergeState.GOVERNANCE_PENDING] == (
        MergeState.DECIDED_COMMIT,
        MergeState.DECIDED_REFUSE,
    )
    assert all(not graph[state] for state in (
        MergeState.DECIDED_COMMIT,
        MergeState.DECIDED_DEFER_NEAR,
        MergeState.DECIDED_DEFER_AMBIG,
        MergeState.DECIDED_REFUSE,
        MergeState.DECIDED_QUARANTINE,
    ))
    return {"graph_state_count": len(graph)}


def assert_terminal_destinations() -> dict[str, object]:
    mapping = {
        state.value: destination_for_terminal_state(state).value
        for state in (
            MergeState.DECIDED_COMMIT,
            MergeState.DECIDED_DEFER_NEAR,
            MergeState.DECIDED_DEFER_AMBIG,
            MergeState.DECIDED_REFUSE,
            MergeState.DECIDED_QUARANTINE,
        )
    }
    assert mapping == {
        "DECIDED_COMMIT": "COMMIT",
        "DECIDED_DEFER_NEAR": "DEFER_NEAR",
        "DECIDED_DEFER_AMBIG": "DEFER_AMBIG",
        "DECIDED_REFUSE": "REFUSE",
        "DECIDED_QUARANTINE": "QUARANTINE_FAIL",
    }
    return {"terminal_destinations": mapping}


def assert_commit_path() -> dict[str, object]:
    attempt, committee_pack, witness_pack, replay_pack = drive_to_verify_pending("COMMIT")
    attempt, _ = advance_merge_state(attempt, MergeState.GOVERNANCE_PENDING)
    seed = build_seed("COMMIT")
    approval = build_approval("COMMIT", committee_pack.committee_pack_id, True)
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.DECIDED_COMMIT,
        governance_approval=approval,
        continuation_seed=seed,
        ledger_appendable=True,
    )
    ledger = build_merge_ledger_entry(
        decision=decision,
        committee_pack=committee_pack,
        continuation_seed=seed,
        entry_index=1,
        witness_pack=witness_pack,
        replay_pack=replay_pack,
        governance_approval=approval,
    )
    assert decision.chosen_destination == MergeDestination.COMMIT
    assert "MergeLedgerEntry" in decision.required_artifacts
    assert ledger.chosen_destination == MergeDestination.COMMIT
    return {
        "final_state": attempt.current_state.value,
        "destination": decision.chosen_destination.value,
        "ledger_entry": ledger.entry_id,
    }


def assert_defer_near_path() -> dict[str, object]:
    attempt, _, _, _ = drive_to_verify_pending("DEFER-NEAR")
    seed = build_seed("DEFER-NEAR")
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.DECIDED_DEFER_NEAR,
        continuation_seed=seed,
        bounded_residual=True,
    )
    assert attempt.current_state == MergeState.DECIDED_DEFER_NEAR
    assert decision.chosen_destination == MergeDestination.DEFER_NEAR
    return {"destination": decision.chosen_destination.value}


def assert_defer_ambig_path() -> dict[str, object]:
    attempt, _, _, _ = drive_to_verify_pending("DEFER-AMBIG")
    seed = build_seed("DEFER-AMBIG")
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.DECIDED_DEFER_AMBIG,
        continuation_seed=seed,
        underdetermined_conflict=True,
    )
    assert attempt.current_state == MergeState.DECIDED_DEFER_AMBIG
    assert decision.chosen_destination == MergeDestination.DEFER_AMBIG
    return {"destination": decision.chosen_destination.value}


def assert_quarantine_path() -> dict[str, object]:
    attempt, _, _, _ = drive_to_verify_pending("QUARANTINE")
    seed = build_seed("QUARANTINE")
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.DECIDED_QUARANTINE,
        continuation_seed=seed,
        policy_breach=True,
    )
    assert attempt.current_state == MergeState.DECIDED_QUARANTINE
    assert decision.chosen_destination == MergeDestination.QUARANTINE_FAIL
    return {"destination": decision.chosen_destination.value}


def assert_refuse_path() -> dict[str, object]:
    attempt, committee_pack, _, _ = drive_to_verify_pending("REFUSE")
    attempt, _ = advance_merge_state(attempt, MergeState.GOVERNANCE_PENDING)
    seed = build_seed("REFUSE")
    denial = build_approval("REFUSE", committee_pack.committee_pack_id, False)
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.DECIDED_REFUSE,
        governance_approval=denial,
        continuation_seed=seed,
    )
    assert attempt.current_state == MergeState.DECIDED_REFUSE
    assert decision.chosen_destination == MergeDestination.REFUSE
    return {"destination": decision.chosen_destination.value}


def assert_forbidden_bypasses() -> dict[str, object]:
    attempt = bootstrap_merge_attempt(build_committee_pack("BYPASS"))
    try:
        advance_merge_state(attempt, MergeState.VERIFY_PENDING)
        raise AssertionError("PROPOSED -> VERIFY_PENDING should fail")
    except MergeTransitionError:
        pass

    attempt, _, _, _ = drive_to_verify_pending("BYPASS-2")
    try:
        advance_merge_state(attempt, MergeState.DECIDED_COMMIT, ledger_appendable=True)
        raise AssertionError("VERIFY_PENDING -> DECIDED_COMMIT should fail")
    except MergeTransitionError:
        pass
    return {"forbidden_bypasses_checked": 2}


def assert_guard_failures() -> dict[str, object]:
    invalid_attempt = bootstrap_merge_attempt(
        build_committee_pack("BAD-ID", candidate_delta_refs=["bad packet id"])
    )
    try:
        advance_merge_state(invalid_attempt, MergeState.BUNDLED)
        raise AssertionError("invalid packet id should block bundling")
    except MergeGuardError:
        pass

    missing_witness_attempt = bootstrap_merge_attempt(build_committee_pack("MISSING-WIT"))
    missing_witness_attempt, _ = advance_merge_state(missing_witness_attempt, MergeState.BUNDLED)
    missing_witness_attempt, _ = advance_merge_state(missing_witness_attempt, MergeState.DISSENT_SURFACED)
    try:
        advance_merge_state(missing_witness_attempt, MergeState.VERIFY_PENDING)
        raise AssertionError("missing witness/replay should block verification")
    except MergeGuardError:
        pass

    attempt, committee_pack, _, _ = drive_to_verify_pending("DENIAL")
    attempt, _ = advance_merge_state(attempt, MergeState.GOVERNANCE_PENDING)
    try:
        advance_merge_state(
            attempt,
            MergeState.DECIDED_COMMIT,
            governance_approval=build_approval("DENIAL", committee_pack.committee_pack_id, False),
            continuation_seed=build_seed("DENIAL"),
            ledger_appendable=True,
        )
        raise AssertionError("governance denial cannot commit")
    except MergeGuardError:
        pass
    return {"guard_failures_checked": 3}


def main() -> int:
    report = {
        "transition_graph": assert_transition_graph(),
        "terminal_destinations": assert_terminal_destinations(),
        "commit_path": assert_commit_path(),
        "defer_near_path": assert_defer_near_path(),
        "defer_ambig_path": assert_defer_ambig_path(),
        "quarantine_path": assert_quarantine_path(),
        "refuse_path": assert_refuse_path(),
        "forbidden_bypasses": assert_forbidden_bypasses(),
        "guard_failures": assert_guard_failures(),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
