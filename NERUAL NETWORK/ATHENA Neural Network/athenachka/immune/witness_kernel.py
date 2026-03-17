from __future__ import annotations

from ..contracts import stable_hash


def build_witness_bundle(
    state,
    phase_plan: list[str],
    candidate_set: list[dict[str, object]],
    contradictions: dict[str, object],
    corridor_profile: dict[str, object],
    active_loops: list[str],
    appendix_bundle: dict[str, object],
    boundary_state: dict[str, object],
) -> dict[str, object]:
    contradiction_penalty = 0.12 * len(contradictions.get("flags", []))
    replay_score = min(1.0, 0.4 + 0.15 * len(state.replay.get("seed_history", [])) + 0.15 * bool(state.checkpoint_id))
    strength = max(
        0.0,
        min(
            1.0,
            0.35
            + 0.06 * len(candidate_set)
            + 0.05 * len(active_loops)
            + 0.12 * replay_score
            - contradiction_penalty,
        ),
    )
    bundle = {
        "phase_plan": list(phase_plan),
        "candidate_count": len(candidate_set),
        "active_loops": list(active_loops),
        "corridor_profile": dict(corridor_profile),
        "contradictions": list(contradictions.get("flags", [])),
        "boundary_state": dict(boundary_state),
        "appendix_bundle": appendix_bundle,
        "replay_score": float(replay_score),
        "strength": float(strength),
    }
    bundle["signature"] = stable_hash(bundle)
    return bundle
