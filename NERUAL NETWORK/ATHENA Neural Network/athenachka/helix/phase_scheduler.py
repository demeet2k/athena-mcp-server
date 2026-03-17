from __future__ import annotations


FAST_PHASES = [
    "seed_unpack",
    "synthesis",
    "operator_build",
    "audit",
    "commit",
]

FULL_PHASES = [
    "2/16_seed_unpack",
    "3/16_corpus_split",
    "4/16_deep_synthesis",
    "5/16_residual_scan",
    "6/16_birth_mine",
    "7/16_operator_build",
    "8/16_registry_build",
    "9/16_meta_observe",
    "10/16_adversarial_audit",
    "11/16_dqi_improve",
    "12/16_prune",
    "13/16_compress",
    "14/16_lift_prepare",
]


def resolve_phase_plan(mode: str) -> list[str]:
    normalized = mode.lower().strip()
    if normalized == "full":
        return list(FULL_PHASES)
    return list(FAST_PHASES)
