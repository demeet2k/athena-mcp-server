from __future__ import annotations

from ..contracts import LoopActivation


LOOP_HEADS = {
    "L1_CorpusMap": ("coverage", "coherence", "retrieval_quality"),
    "L2_OntologyLattice": ("coherence", "born_coordinate_discovery_rate", "novelty_gain"),
    "L3_ResidualPressure": ("contradiction_pressure", "frontier_clarity", "born_coordinate_discovery_rate"),
    "L4_BridgeMiner": ("born_coordinate_discovery_rate", "cross_domain_transfer", "frontier_clarity"),
    "L5_OperatorExtraction": ("operator_closure", "proof_density", "novelty_gain"),
    "L6_RepresentationTheory": ("operator_closure", "registry_completeness", "cross_domain_transfer"),
    "L7_RegistrySchemas": ("registry_completeness", "replayability", "proof_density"),
    "L8_VerifierReplay": ("proof_density", "replayability", "coherence"),
    "L9_MetaProcess": ("meta_process_quality", "coherence", "pruning_efficiency"),
    "L10_JourneyGrowth": ("self_growth_gain", "meta_process_quality", "cross_domain_transfer"),
    "L11_PathologyLab": ("contradiction_pressure", "proof_density", "replayability"),
    "L12_PruneOptimizer": ("pruning_efficiency", "compression_ratio", "coherence"),
    "L13_CrossDomainTransfer": ("cross_domain_transfer", "novelty_gain", "frontier_clarity"),
    "L14_NovelGenerator": ("novelty_gain", "born_coordinate_discovery_rate", "operator_closure"),
    "L15_Distillation": ("compression_ratio", "operator_closure", "proof_density"),
    "L16_DimensionLift": ("compression_ratio", "meta_process_quality", "self_growth_gain"),
}


def _loop_score(metric_tensor: dict[str, float], metric_ids: tuple[str, str, str], elemental_bias: float) -> float:
    base = sum(float(metric_tensor.get(metric, 0.0)) for metric in metric_ids) / len(metric_ids)
    return float(base * 0.8 + elemental_bias * 0.2)


def select_loops(
    metric_tensor: dict[str, float],
    elemental_state: dict[str, dict[str, object]],
    mode: str,
    phase_budget: int,
) -> list[LoopActivation]:
    top_k = 8 if mode == "full" else 4
    fire = float(elemental_state["fire"]["score"])
    water = float(elemental_state["water"]["score"])
    air = float(elemental_state["air"]["score"])
    earth = float(elemental_state["earth"]["score"])
    elemental_biases = {
        "L1_CorpusMap": air,
        "L2_OntologyLattice": air,
        "L3_ResidualPressure": fire,
        "L4_BridgeMiner": water,
        "L5_OperatorExtraction": fire,
        "L6_RepresentationTheory": air,
        "L7_RegistrySchemas": earth,
        "L8_VerifierReplay": earth,
        "L9_MetaProcess": water,
        "L10_JourneyGrowth": water,
        "L11_PathologyLab": fire,
        "L12_PruneOptimizer": earth,
        "L13_CrossDomainTransfer": air,
        "L14_NovelGenerator": fire,
        "L15_Distillation": earth,
        "L16_DimensionLift": water,
    }

    scored: list[LoopActivation] = []
    for loop_id, metric_ids in LOOP_HEADS.items():
        score = _loop_score(metric_tensor, metric_ids, elemental_biases[loop_id])
        scored.append(
            LoopActivation(
                loop_id=loop_id,
                score=score,
                phase_budget=phase_budget,
                corridor_budget=float(metric_tensor.get("coherence", 0.5)),
                activation_reason=f"dominant_metrics={','.join(metric_ids)}",
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]
