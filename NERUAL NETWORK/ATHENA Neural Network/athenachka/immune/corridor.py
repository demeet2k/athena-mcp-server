from __future__ import annotations


FAST_PROFILE = {
    "mode": "fast",
    "max_hypotheses": 6,
    "max_pairwise_fusions": 3,
    "max_loops": 4,
    "ok_confidence": 0.9,
    "near_confidence": 0.7,
    "ambiguity_margin": 0.12,
}

FULL_PROFILE = {
    "mode": "full",
    "max_hypotheses": 12,
    "max_pairwise_fusions": 6,
    "max_loops": 8,
    "ok_confidence": 0.85,
    "near_confidence": 0.65,
    "ambiguity_margin": 0.15,
}


def resolve_corridor(mode: str) -> dict[str, object]:
    return dict(FULL_PROFILE if mode.lower().strip() == "full" else FAST_PROFILE)


def trim_candidate_set(candidate_set: list[dict[str, object]], corridor_profile: dict[str, object]) -> list[dict[str, object]]:
    limit = int(corridor_profile["max_hypotheses"])
    return list(candidate_set)[:limit]
