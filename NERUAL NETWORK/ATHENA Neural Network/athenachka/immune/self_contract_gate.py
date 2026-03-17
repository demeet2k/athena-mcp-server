from __future__ import annotations


def evaluate_self_contract(state, promote_born_coordinates: bool, mode: str) -> dict[str, object]:
    allowed = {
        "policy_tuning",
        "support_shell_strengthening",
        "memory_reindexing",
        "checkpoint_insertion",
    }
    if mode == "full":
        allowed.add("born_coordinate_review")

    forbidden = {
        "silent_identity_kernel_rewrite",
        "memory_deletion_without_archive",
        "support_class_inflation",
    }
    if promote_born_coordinates and mode != "full":
        return {
            "legal": False,
            "reason": "born_coordinate_promotion_requires_full_mode",
            "allowed": sorted(allowed),
            "forbidden": sorted(forbidden),
        }
    return {
        "legal": True,
        "reason": "contract_satisfied",
        "allowed": sorted(allowed),
        "forbidden": sorted(forbidden),
    }
