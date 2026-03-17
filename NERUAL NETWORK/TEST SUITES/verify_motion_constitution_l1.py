from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATHENA_PACKAGE_ROOT = ROOT / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import MotionAction, MotionCandidatePacket, MotionScoreVector  # noqa: E402
from athenachka.runtime.motion_constitution import (  # noqa: E402
    MotionConstitutionL1,
    action_alphabet,
    accepted_source_kinds,
    bootstrap_motion_state,
    evaluate_candidate,
)


def build_score_vector(**overrides: float) -> MotionScoreVector:
    base = {
        "closure_gain": 1.2,
        "heart_need": 1.0,
        "replay_readiness": 1.0,
        "integration_yield": 1.1,
        "organ_adjacency": 1.0,
        "seed_value": 0.8,
        "cost": 0.4,
        "replay_cost": 0.2,
        "risk": 0.2,
        "failure_debt": 0.1,
        "branch_burden": 0.0,
        "contradiction_heat": 0.0,
        "pressure_gradient": 0.6,
        "truth_readiness": 1.0,
    }
    base.update(overrides)
    return MotionScoreVector(**base)


def build_candidate(
    candidate_id: str,
    *,
    source_kind: str = "quest_board",
    blockers: list[str] | None = None,
    dependencies: list[str] | None = None,
    witness_refs: list[str] | None = None,
    replay_refs: list[str] | None = None,
    committee_refs: list[str] | None = None,
    continuation_seed: str = "MotionConstitution_L1::Parameterization",
    current_family: str = "jointatlas",
    score_vector: MotionScoreVector | None = None,
) -> MotionCandidatePacket:
    return MotionCandidatePacket(
        candidate_id=candidate_id,
        source_kind=source_kind,
        source_ref=f"source::{candidate_id}",
        source_organ="GuildHall",
        target_organ="Runtime",
        current_family=current_family,
        truth_burden="NEAR",
        expected_packet_type="QuestPacket",
        continuation_seed=continuation_seed,
        dependencies=list(dependencies or []),
        blockers=list(blockers or []),
        witness_refs=list(witness_refs if witness_refs is not None else ["WIT-001"]),
        replay_refs=list(replay_refs if replay_refs is not None else ["RPL-001"]),
        committee_refs=list(committee_refs if committee_refs is not None else []),
        score_vector=score_vector or build_score_vector(),
    )


def assert_fixture_actions() -> dict[str, str]:
    state = bootstrap_motion_state(activation_threshold=1.1)
    fixtures = {
        "activate": build_candidate("activate-now"),
        "hold": build_candidate(
            "hold",
            score_vector=build_score_vector(
                closure_gain=0.1,
                heart_need=0.1,
                replay_readiness=0.8,
                integration_yield=0.1,
                organ_adjacency=0.1,
                seed_value=0.1,
                cost=1.8,
                replay_cost=1.0,
                risk=1.0,
                failure_debt=0.8,
                branch_burden=0.8,
                contradiction_heat=0.2,
                pressure_gradient=0.0,
            ),
        ),
        "request_witnesses": build_candidate("request-witnesses", witness_refs=[]),
        "request_help": build_candidate(
            "request-help",
            dependencies=["dep:missing"],
            blockers=["external_dependency"],
        ),
        "replay_first": build_candidate("replay-first", replay_refs=[]),
        "quarantine": build_candidate("quarantine", blockers=["policy_breach"]),
        "compress_to_seed": build_candidate(
            "compress-to-seed",
            blockers=["forward_circulation_blocked"],
        ),
        "escalate_to_committee": build_candidate(
            "escalate-to-committee",
            blockers=["committee_pending_conflict"],
            committee_refs=["pending:committee"],
        ),
        "refuse": build_candidate(
            "refuse",
            source_kind="inadmissible_source",
        ),
    }
    expected = {
        "activate": MotionAction.ACTIVATE_NOW,
        "hold": MotionAction.HOLD,
        "request_witnesses": MotionAction.REQUEST_WITNESSES,
        "request_help": MotionAction.REQUEST_HELP,
        "replay_first": MotionAction.REPLAY_FIRST,
        "quarantine": MotionAction.QUARANTINE,
        "compress_to_seed": MotionAction.COMPRESS_TO_SEED,
        "escalate_to_committee": MotionAction.ESCALATE_TO_COMMITTEE,
        "refuse": MotionAction.REFUSE_INADMISSIBLE,
    }

    results: dict[str, str] = {}
    for key, candidate in fixtures.items():
        decision, _, _ = evaluate_candidate(candidate, state, activation_threshold=1.1)
        assert decision.action == expected[key], f"{key} should map to {expected[key].value}"
        results[key] = decision.action.value
    return results


def assert_gate_precedence() -> dict[str, str]:
    state = bootstrap_motion_state(activation_threshold=1.1)
    refusal = build_candidate(
        "precedence-refusal",
        source_kind="inadmissible_source",
        blockers=["policy_breach"],
    )
    decision, _, _ = evaluate_candidate(refusal, state, activation_threshold=1.1)
    assert decision.action == MotionAction.REFUSE_INADMISSIBLE

    quarantine = build_candidate(
        "precedence-quarantine",
        blockers=["policy_breach", "external_dependency"],
        replay_refs=[],
        witness_refs=[],
    )
    decision, _, _ = evaluate_candidate(quarantine, state, activation_threshold=1.1)
    assert decision.action == MotionAction.QUARANTINE

    replay = build_candidate(
        "precedence-replay",
        blockers=["external_dependency"],
        replay_refs=[],
        witness_refs=[],
    )
    decision, _, _ = evaluate_candidate(replay, state, activation_threshold=1.1)
    assert decision.action == MotionAction.REPLAY_FIRST

    committee = build_candidate(
        "precedence-committee",
        blockers=["committee_pending_conflict", "forward_circulation_blocked"],
        committee_refs=["pending:committee"],
    )
    decision, _, _ = evaluate_candidate(committee, state, activation_threshold=1.1)
    assert decision.action == MotionAction.ESCALATE_TO_COMMITTEE

    witness = build_candidate(
        "precedence-witness",
        witness_refs=[],
        score_vector=build_score_vector(closure_gain=2.0, integration_yield=2.0),
    )
    decision, _, _ = evaluate_candidate(witness, state, activation_threshold=1.1)
    assert decision.action == MotionAction.REQUEST_WITNESSES

    return {
        "refusal_beats_quarantine": MotionAction.REFUSE_INADMISSIBLE.value,
        "quarantine_beats_replay": MotionAction.QUARANTINE.value,
        "replay_beats_help_and_witness": MotionAction.REPLAY_FIRST.value,
        "committee_beats_seed_compression": MotionAction.ESCALATE_TO_COMMITTEE.value,
        "activation_never_bypasses_witness": MotionAction.REQUEST_WITNESSES.value,
    }


def assert_hysteresis() -> dict[str, str]:
    engine = MotionConstitutionL1(bootstrap_motion_state(activation_threshold=1.1), activation_threshold=1.1)

    refused_candidate = build_candidate(
        "hysteresis-refuse",
        source_kind="inadmissible_source",
        witness_refs=["WIT-HR-001"],
        replay_refs=["RPL-HR-001"],
    )
    decision, _ = engine.evaluate_candidate(refused_candidate)
    assert decision.action == MotionAction.REFUSE_INADMISSIBLE

    reattempt = build_candidate(
        "hysteresis-refuse",
        source_kind="quest_board",
        witness_refs=["WIT-HR-001"],
        replay_refs=["RPL-HR-001"],
    )
    decision, _ = engine.evaluate_candidate(reattempt)
    assert decision.action == MotionAction.REFUSE_INADMISSIBLE

    released = build_candidate(
        "hysteresis-refuse",
        source_kind="quest_board",
        witness_refs=["WIT-HR-002"],
        replay_refs=["RPL-HR-001"],
    )
    decision, _ = engine.evaluate_candidate(released)
    assert decision.action == MotionAction.ACTIVATE_NOW

    quarantined_candidate = build_candidate(
        "hysteresis-quarantine",
        blockers=["policy_breach"],
        replay_refs=["RPL-HQ-001"],
    )
    decision, _ = engine.evaluate_candidate(quarantined_candidate)
    assert decision.action == MotionAction.QUARANTINE

    reattempt = build_candidate(
        "hysteresis-quarantine",
        blockers=[],
        replay_refs=["RPL-HQ-001"],
    )
    decision, _ = engine.evaluate_candidate(reattempt)
    assert decision.action == MotionAction.QUARANTINE

    released = build_candidate(
        "hysteresis-quarantine",
        blockers=[],
        replay_refs=["RPL-HQ-002"],
    )
    decision, _ = engine.evaluate_candidate(released)
    assert decision.action == MotionAction.ACTIVATE_NOW

    return {
        "refusal_requires_new_witness_or_replay": "OK",
        "quarantine_requires_new_immune_or_replay_state": "OK",
    }


def assert_public_contracts() -> dict[str, object]:
    alphabet = action_alphabet()
    sources = accepted_source_kinds()
    assert len(alphabet) == 9
    assert len(sources) == 5
    return {
        "action_count": len(alphabet),
        "source_kind_count": len(sources),
        "actions": list(alphabet),
        "source_kinds": list(sources),
    }


def main() -> int:
    report = {
        "public_contracts": assert_public_contracts(),
        "fixture_actions": assert_fixture_actions(),
        "gate_precedence": assert_gate_precedence(),
        "hysteresis": assert_hysteresis(),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
