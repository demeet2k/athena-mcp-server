from __future__ import annotations

import numpy as np

from ..appendix import appendix_bundle
from ..appendix.app_l_replay_validation import build_replay_signature
from ..contracts import AthenaResult, stable_hash
from ..crystal.born_coordinates import propose_born_coordinates
from ..crystal.elemental_lanes import project_elemental_state
from ..crystal.symmetry_fusions import compute_symmetry_state
from ..helix import (
    build_initial_state,
    build_metric_tensor,
    compile_improvement_ledger,
    prepare_lift_seed,
    resolve_phase_plan,
    select_loops,
)
from ..immune import (
    build_witness_bundle,
    capture_checkpoint,
    classify_truth,
    detect_contradictions,
    evaluate_self_contract,
    resolve_corridor,
    trim_candidate_set,
    verify_boundary,
)
from ..core.kernel import AthenaKernel

CORE_RUNTIME_FINGERPRINT = [
    "rank_encoder",
    "attention_field",
    "hypothesis_compiler",
    "carrier_stack",
    "mdl_prior",
    "classifier",
    "fusion",
]


def _candidate_set_from_trace(trace: dict[str, object]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for item in trace["hypotheses"]:
        candidates.append(
            {
                "threshold": float(item["tau"]),
                "predicted_class": int(item["predicted_class"]),
                "confidence": float(item["confidence"]),
                "quality": float(item["quality"]),
                "disagreement": float(item["disagreement"]),
                "edge_agreement": float(item["edge_agreement"]),
                "probabilities": np.asarray(item["fused_probs"], dtype=float).tolist(),
                "mask_mass": float(item["mask_mass"]),
            }
        )
    if not candidates:
        candidates.append(
            {
                "threshold": 0.0,
                "predicted_class": int(trace["legacy_prediction"]),
                "confidence": float(trace["legacy_confidence"]),
                "quality": 0.0,
                "disagreement": 0.0,
                "edge_agreement": 0.0,
                "probabilities": np.asarray(trace["legacy_probs"], dtype=float).tolist(),
                "mask_mass": 0.0,
            }
        )
    return candidates


class AthenachkaOrganismV0:
    """Organism-first wrapper around the preserved Athena kernel."""

    def __init__(self, kernel: AthenaKernel | None = None, docs_gate_status: str = "BLOCKED"):
        self.kernel = kernel or AthenaKernel()
        self.docs_gate_status = docs_gate_status
        self.last_state = build_initial_state(mode="fast", docs_gate_status=docs_gate_status)

    def train(self, X_train, Y_train, **kwargs) -> None:
        self.kernel.train(X_train, Y_train, **kwargs)

    def forward_legacy(self, img: np.ndarray) -> tuple[int, np.ndarray, float]:
        return self.kernel.forward(img)

    def forward(
        self,
        img: np.ndarray,
        mode: str = "fast",
        state=None,
        promote_born_coordinates: bool = False,
    ) -> AthenaResult:
        corridor_profile = resolve_corridor(mode)
        phase_plan = resolve_phase_plan(mode)
        state = state or build_initial_state(mode=mode, docs_gate_status=self.docs_gate_status)
        state.phase_index = phase_plan[0]
        state.process["phase_history"] = list(phase_plan)
        state.process["core_runtime_fingerprint"] = list(CORE_RUNTIME_FINGERPRINT)
        state.replay["phase_trace"] = list(phase_plan)
        state.replay["core_runtime_fingerprint"] = list(CORE_RUNTIME_FINGERPRINT)

        checkpoint = None
        if mode == "full":
            checkpoint = capture_checkpoint(state)

        trace = self.kernel.forward_trace(img, max_hypotheses=int(corridor_profile["max_hypotheses"]))
        candidate_set = trim_candidate_set(_candidate_set_from_trace(trace), corridor_profile)
        elemental_state = project_elemental_state(trace, state, mode=mode)
        symmetry_state = compute_symmetry_state(
            elemental_state,
            top_k=int(corridor_profile["max_pairwise_fusions"]),
        )
        state.active_fusions = list(symmetry_state["active_fusions"].keys())

        contradictions = detect_contradictions(candidate_set, trace, symmetry_state, corridor_profile)
        self_contract = evaluate_self_contract(state, promote_born_coordinates, mode)
        boundary_state = verify_boundary(contradictions, state)
        state.process["contradictions"] = dict(contradictions)
        state.process["self_contract"] = dict(self_contract)
        state.process["boundary_state"] = dict(boundary_state)

        appendix_state = appendix_bundle(mode, phase_plan, trace)
        provisional_witness = {
            "strength": 0.5,
            "replay_score": 0.5,
        }
        metric_tensor = build_metric_tensor(
            trace=trace,
            elemental_state=elemental_state,
            symmetry_state=symmetry_state,
            born_coordinates=[],
            contradictions=contradictions,
            witness_bundle=provisional_witness,
            mode=mode,
        )
        active_loop_objects = select_loops(metric_tensor, elemental_state, mode=mode, phase_budget=len(phase_plan))
        state.active_loops = [item.loop_id for item in active_loop_objects]

        witness_bundle = build_witness_bundle(
            state=state,
            phase_plan=phase_plan,
            candidate_set=candidate_set,
            contradictions=contradictions,
            corridor_profile=corridor_profile,
            active_loops=state.active_loops,
            appendix_bundle=appendix_state,
            boundary_state=boundary_state,
        )
        metric_tensor = build_metric_tensor(
            trace=trace,
            elemental_state=elemental_state,
            symmetry_state=symmetry_state,
            born_coordinates=[],
            contradictions=contradictions,
            witness_bundle=witness_bundle,
            mode=mode,
        )
        state.metrics = dict(metric_tensor)

        born_coordinates: list[dict[str, object]] = []
        if mode == "full":
            for item in propose_born_coordinates(trace, symmetry_state, state):
                promoted = (
                    promote_born_coordinates
                    and bool(self_contract["legal"])
                    and len(item.support) > 0
                    and bool(item.bridge_receipt)
                )
                item.promoted = promoted
                born_coordinates.append(
                    {
                        "name": item.name,
                        "residual_norm": float(item.residual_norm),
                        "support": list(item.support),
                        "bridge_receipt": dict(item.bridge_receipt),
                        "promoted": bool(item.promoted),
                    }
                )
            state.bridges["candidate_receipts"] = [item["bridge_receipt"] for item in born_coordinates]
            if promote_born_coordinates:
                state.bridges["promoted_receipts"] = [
                    item["bridge_receipt"] for item in born_coordinates if item["promoted"]
                ]

        improvement_ledger = compile_improvement_ledger(
            trace=trace,
            contradictions=contradictions,
            born_coordinates=born_coordinates,
            metric_tensor=metric_tensor,
            active_loops=state.active_loops,
            active_fusions=state.active_fusions,
            phase_plan=phase_plan,
        )
        state.process["improvement_ledger"] = improvement_ledger

        lineage_delta = {
            "phase_plan": phase_plan,
            "active_loops": state.active_loops,
            "active_fusions": state.active_fusions,
            "born_coordinate_count": len(born_coordinates),
            "checkpoint_id": state.checkpoint_id,
        }

        if mode == "full":
            seed = prepare_lift_seed(
                state=state,
                metric_tensor=metric_tensor,
                witness_bundle=witness_bundle,
                improvement_ledger=improvement_ledger,
                symmetry_state=symmetry_state,
            )
            state.replay["lift_seed"] = seed
        elif checkpoint is not None:
            state.replay["last_checkpoint"] = checkpoint["id"]

        truth_type = classify_truth(
            trace=trace,
            contradictions=contradictions,
            witness_bundle=witness_bundle,
            corridor_profile=corridor_profile,
            self_contract=self_contract,
        )

        replay_payload = {
            "prediction": int(trace["legacy_prediction"]),
            "truth_type": truth_type,
            "active_loops": state.active_loops,
            "active_fusions": state.active_fusions,
            "checkpoint_id": state.checkpoint_id,
            "witness_signature": witness_bundle["signature"],
        }
        replay_signature = build_replay_signature(replay_payload)
        state.replay["last_signature"] = replay_signature
        state.replay.setdefault("phase_replay", []).append(replay_payload)
        self.last_state = state

        return AthenaResult(
            prediction=int(trace["legacy_prediction"]),
            truth_type=truth_type,
            confidence=float(trace["legacy_confidence"]),
            candidate_set=candidate_set,
            elemental_state=elemental_state,
            symmetry_state=symmetry_state,
            born_coordinates=born_coordinates,
            witness_bundle=witness_bundle,
            corridor_profile=corridor_profile,
            metric_tensor=metric_tensor,
            replay_signature=replay_signature,
            lineage_delta=lineage_delta,
        )

    def predict(self, X: np.ndarray, mode: str = "fast") -> np.ndarray:
        predictions = []
        for i in range(len(X)):
            result = self.forward(X[i].reshape(28, 28), mode=mode)
            predictions.append(int(result.prediction))
        return np.array(predictions)

    def evaluate(self, X_test: np.ndarray, Y_test: np.ndarray, mode: str = "fast", verbose: bool = True) -> float:
        correct = 0
        total = len(X_test)
        for i in range(total):
            result = self.forward(X_test[i].reshape(28, 28), mode=mode)
            if int(result.prediction) == int(Y_test[i].argmax()):
                correct += 1
        accuracy = correct / max(1, total)
        if verbose:
            print(f"  Organism {mode} accuracy: {accuracy * 100:.1f}%")
        return accuracy

    def checkpoint_id(self) -> str:
        return self.last_state.checkpoint_id or stable_hash(self.last_state.to_dict())
