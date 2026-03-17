from __future__ import annotations


IMPROVEMENT_SECTIONS = [
    "missing_distinctions",
    "contradictions",
    "born_coordinate_candidates",
    "bridge_candidates",
    "operator_improvements",
    "representation_improvements",
    "registry_improvements",
    "verifier_improvements",
    "replay_improvements",
    "retrieval_improvements",
    "compression_opportunities",
    "pruning_targets",
    "transfer_opportunities",
    "process_improvements",
    "self_growth_improvements",
    "next_experiments",
]


def compile_improvement_ledger(
    trace: dict[str, object],
    contradictions: dict[str, object],
    born_coordinates: list[dict[str, object]],
    metric_tensor: dict[str, float],
    active_loops: list[str],
    active_fusions: list[str],
    phase_plan: list[str],
) -> dict[str, object]:
    candidate_count = len(trace["hypotheses"])
    pressure = float(contradictions.get("pressure", 0.0))
    active_flags = contradictions.get("flags", [])
    ledger = {
        "missing_distinctions": [
            f"candidate_count={candidate_count}",
            f"frontier_clarity={metric_tensor['frontier_clarity']:.4f}",
        ],
        "contradictions": list(active_flags),
        "born_coordinate_candidates": [item["name"] for item in born_coordinates],
        "bridge_candidates": [item.get("bridge_receipt", {}) for item in born_coordinates],
        "operator_improvements": [f"active_loops={','.join(active_loops) or 'none'}"],
        "representation_improvements": [f"active_fusions={','.join(active_fusions) or 'none'}"],
        "registry_improvements": [f"registry_completeness={metric_tensor['registry_completeness']:.4f}"],
        "verifier_improvements": [f"proof_density={metric_tensor['proof_density']:.4f}"],
        "replay_improvements": [f"replayability={metric_tensor['replayability']:.4f}"],
        "retrieval_improvements": [f"retrieval_quality={metric_tensor['retrieval_quality']:.4f}"],
        "compression_opportunities": [f"compression_ratio={metric_tensor['compression_ratio']:.4f}"],
        "pruning_targets": [f"contradiction_pressure={pressure:.4f}"],
        "transfer_opportunities": [f"cross_domain_transfer={metric_tensor['cross_domain_transfer']:.4f}"],
        "process_improvements": [f"phase_plan={' > '.join(phase_plan)}"],
        "self_growth_improvements": [f"self_growth_gain={metric_tensor['self_growth_gain']:.4f}"],
        "next_experiments": [
            "promote_born_coordinates_only_with_witness_bundle",
            "expand_pairwise_fusions_after_parity_holds",
        ],
    }
    return {
        "phase_terminal": "14/16_lift_prepare",
        "active_loops": list(active_loops),
        "sections": ledger,
        "required_sections": list(IMPROVEMENT_SECTIONS),
    }
