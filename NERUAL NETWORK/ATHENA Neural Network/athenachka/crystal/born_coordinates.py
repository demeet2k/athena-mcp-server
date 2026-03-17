from __future__ import annotations

import numpy as np

from ..contracts import BornCoordinate


def propose_born_coordinates(
    trace: dict[str, object],
    symmetry_state: dict[str, object],
    state,
    max_candidates: int = 3,
) -> list[BornCoordinate]:
    """Generate witness-backed born-coordinate candidates from residual ambiguity."""
    hypotheses: list[dict[str, object]] = list(trace["hypotheses"])
    if len(hypotheses) < 2:
        return []

    probs = np.asarray(trace["legacy_probs"])
    top_probs = np.sort(probs)[-2:]
    margin = float(top_probs[-1] - top_probs[-2])
    if margin >= 0.2:
        return []

    results: list[BornCoordinate] = []
    sorted_hypotheses = sorted(hypotheses, key=lambda item: float(item["confidence"]), reverse=True)
    for idx, hypothesis in enumerate(sorted_hypotheses[:max_candidates]):
        residual_norm = float((1.0 - margin) * (0.5 + float(hypothesis["disagreement"])))
        support = [
            f"candidate_threshold={hypothesis['tau']:.2f}",
            f"candidate_confidence={float(hypothesis['confidence']):.4f}",
            f"candidate_disagreement={float(hypothesis['disagreement']):.4f}",
            f"active_fusions={','.join(symmetry_state['active_fusions'].keys()) or 'none'}",
        ]
        bridge_receipt = {
            "source_phase": "6/16_birth_mine",
            "target_phase": "7/16_operator_build",
            "residual_norm": residual_norm,
            "checkpoint_id": state.checkpoint_id,
        }
        results.append(
            BornCoordinate(
                name=f"born_coord_{idx + 1}",
                residual_norm=residual_norm,
                support=support,
                bridge_receipt=bridge_receipt,
                promoted=False,
            )
        )
    return results
