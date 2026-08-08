from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

CONNECTION_VERSION = "MCK.SYNTHETIC.CONNECTION.CONTROL.V1"

CONTROL_STANDING = "SYNTHETIC_CONTROL_ONLY_NOT_SOURCE_EVIDENCE"
VERIFIED_TYPED_LOSS = "VERIFIED_TYPED_CONTROL"
DEFINED_STANDING = "DEFINED_SYNTHETIC_TYPED_CONNECTION"

UNKNOWN_UNTYPED_LOSS = "UNKNOWN_UNVERIFIED_TYPED_LOSS"
UNKNOWN_MISSING_OPERATOR = "UNKNOWN_MISSING_OPERATOR"
UNKNOWN_PATH_DISCONTINUITY = "UNKNOWN_PATH_DISCONTINUITY"
UNKNOWN_NOT_CLOSED = "UNKNOWN_NOT_CLOSED_LOOP"
UNKNOWN_INVALID_OPERATOR = "UNKNOWN_INVALID_OPERATOR"
UNKNOWN_TRANSFORM = "UNKNOWN_TRANSFORM"

ALLOWED_TRANSFORMS = frozenset({"IDENTITY", "SET", "ADD", "MUL"})

LAWS = (
    "EXPECTED_CLASS != CONNECTION_DEFINITION",
    "UNTYPED_PROSE_LOSS != COMPUTABLE_TYPED_IRREVERSIBILITY",
    "ENDPOINT_EQUALITY != ZERO_RESIDUE_WHEN_VERIFIED_IRREVERSIBLE_LOSS_EXISTS",
    "NONZERO_RESIDUE_REQUIRES_TYPED_STATE_TRANSITION_OR_TYPED_IRREVERSIBILITY",
    "UNSUPPORTED_CONNECTION -> UNKNOWN",
    "SYNTHETIC_CONTROL != HISTORICAL_SOURCE_WITNESS",
    "DECLARED_INVERSE_METADATA != PROOF_OF_ZERO_RESIDUE",
)


@dataclass(frozen=True)
class FeatureTransform:
    op: str
    operand: Any = None

    def normalized_op(self) -> str:
        return str(self.op).upper()


@dataclass(frozen=True)
class EdgeOperator:
    edge_id: str
    source_coordinate: str
    target_coordinate: str
    transforms: Mapping[str, FeatureTransform] = field(default_factory=dict)
    typed_loss: Optional[frozenset[str]] = frozenset()
    loss_standing: str = VERIFIED_TYPED_LOSS
    inverse_edge_id: Optional[str] = None
    provenance: Tuple[str, ...] = ()
    standing: str = CONTROL_STANDING


@dataclass
class TransportState:
    coordinate: str
    values: Dict[str, Any]
    irreversible_loss: set[str] = field(default_factory=set)
    provenance: list[str] = field(default_factory=list)

    def clone(self) -> "TransportState":
        return TransportState(
            coordinate=self.coordinate,
            values=dict(self.values),
            irreversible_loss=set(self.irreversible_loss),
            provenance=list(self.provenance),
        )


class SyntheticConnectionRuntime:
    """Synthetic connection-control harness.

    Intentionally not wired into the public MCK tool/resource surface. It is a
    mathematical control harness, not historical/source evidence, and it has no
    expected-label input.
    """

    def __init__(self, feature_basis: Iterable[str], operators: Iterable[EdgeOperator]):
        self.feature_basis = tuple(dict.fromkeys(str(x) for x in feature_basis))
        self.feature_set = frozenset(self.feature_basis)
        self.operators: Dict[str, EdgeOperator] = {}
        self.registry_errors: list[str] = []

        if not self.feature_basis:
            self.registry_errors.append("EMPTY_FEATURE_BASIS")

        for edge in operators:
            if not edge.edge_id:
                self.registry_errors.append("EMPTY_EDGE_ID")
                continue
            if edge.edge_id in self.operators:
                self.registry_errors.append(f"DUPLICATE_EDGE_ID:{edge.edge_id}")
                continue
            self.operators[edge.edge_id] = edge

        for edge in self.operators.values():
            self.registry_errors.extend(self._validate_operator(edge))

    def _validate_operator(self, edge: EdgeOperator) -> list[str]:
        errors: list[str] = []
        if not edge.source_coordinate or not edge.target_coordinate:
            errors.append(f"INVALID_COORDINATE:{edge.edge_id}")
        if edge.standing != CONTROL_STANDING:
            errors.append(f"INVALID_OPERATOR_STANDING:{edge.edge_id}")
        for feature, transform in edge.transforms.items():
            if feature not in self.feature_set:
                errors.append(f"TRANSFORM_FEATURE_OUTSIDE_BASIS:{edge.edge_id}:{feature}")
            if not isinstance(transform, FeatureTransform):
                errors.append(f"INVALID_TRANSFORM_OBJECT:{edge.edge_id}:{feature}")
                continue
            if transform.normalized_op() not in ALLOWED_TRANSFORMS:
                errors.append(f"UNSUPPORTED_TRANSFORM:{edge.edge_id}:{feature}:{transform.op}")
        if edge.typed_loss is not None:
            extra = set(edge.typed_loss) - set(self.feature_set)
            for feature in sorted(extra):
                errors.append(f"LOSS_FEATURE_OUTSIDE_BASIS:{edge.edge_id}:{feature}")
            if edge.loss_standing != VERIFIED_TYPED_LOSS:
                errors.append(f"UNVERIFIED_TYPED_LOSS_STANDING:{edge.edge_id}")
        if edge.inverse_edge_id is not None:
            inverse = self.operators.get(edge.inverse_edge_id)
            if inverse is None:
                errors.append(f"MISSING_DECLARED_INVERSE:{edge.edge_id}:{edge.inverse_edge_id}")
            else:
                if inverse.source_coordinate != edge.target_coordinate or inverse.target_coordinate != edge.source_coordinate:
                    errors.append(f"INVERSE_COORDINATE_MISMATCH:{edge.edge_id}:{edge.inverse_edge_id}")
                if inverse.inverse_edge_id != edge.edge_id:
                    errors.append(f"INVERSE_NOT_MUTUAL:{edge.edge_id}:{edge.inverse_edge_id}")
        return errors

    def _unknown(
        self,
        standing: str,
        *,
        reason: str,
        initial: TransportState,
        executed: Sequence[str] = (),
        final: Optional[TransportState] = None,
        errors: Sequence[str] = (),
    ) -> Dict[str, Any]:
        state = final or initial
        return {
            "version": CONNECTION_VERSION,
            "status": "UNKNOWN",
            "standing": standing,
            "reason": reason,
            "control_standing": CONTROL_STANDING,
            "connection_defined": False,
            "projection_back_executed": False,
            "projection_back_operator": None,
            "initial_coordinate": initial.coordinate,
            "final_coordinate": state.coordinate,
            "executed_edge_ids": list(executed),
            "closed_loop_residue": None,
            "errors": list(errors),
            "laws": list(LAWS),
        }

    @staticmethod
    def _apply_transform(value: Any, transform: FeatureTransform) -> Any:
        op = transform.normalized_op()
        if op == "IDENTITY":
            return value
        if op == "SET":
            return transform.operand
        if op == "ADD":
            return value + transform.operand
        if op == "MUL":
            return value * transform.operand
        raise ValueError(f"unsupported transform: {transform.op}")

    def _apply_edge(self, state: TransportState, edge: EdgeOperator) -> tuple[TransportState, Optional[str]]:
        if state.coordinate != edge.source_coordinate:
            return state, f"EDGE_SOURCE_MISMATCH:{edge.edge_id}:{state.coordinate}!={edge.source_coordinate}"

        out = state.clone()
        for feature, transform in edge.transforms.items():
            if feature not in out.values:
                return state, f"MISSING_STATE_FEATURE:{edge.edge_id}:{feature}"
            try:
                out.values[feature] = self._apply_transform(out.values[feature], transform)
            except Exception as exc:
                return state, f"TRANSFORM_ERROR:{edge.edge_id}:{feature}:{type(exc).__name__}"

        if edge.typed_loss is not None:
            out.irreversible_loss.update(edge.typed_loss)
        out.provenance.extend(edge.provenance)
        out.provenance.append(f"EDGE::{edge.edge_id}")
        out.coordinate = edge.target_coordinate
        return out, None

    def evaluate_closed_loop(self, initial: TransportState, edge_ids: Sequence[str]) -> Dict[str, Any]:
        if self.registry_errors:
            return self._unknown(
                UNKNOWN_INVALID_OPERATOR,
                reason="OPERATOR_REGISTRY_INVALID",
                initial=initial,
                errors=self.registry_errors,
            )

        if set(initial.values) != set(self.feature_set):
            missing = sorted(self.feature_set - set(initial.values))
            extra = sorted(set(initial.values) - self.feature_set)
            return self._unknown(
                UNKNOWN_INVALID_OPERATOR,
                reason="INITIAL_STATE_FEATURE_BASIS_MISMATCH",
                initial=initial,
                errors=[f"MISSING:{','.join(missing)}", f"EXTRA:{','.join(extra)}"],
            )

        if not edge_ids:
            return self._unknown(
                UNKNOWN_NOT_CLOSED,
                reason="EMPTY_EDGE_SEQUENCE_HAS_NO_EXECUTED_RETURN_OPERATOR",
                initial=initial,
            )

        state = initial.clone()
        executed: list[str] = []
        unverified_loss_edges: list[str] = []

        for edge_id in edge_ids:
            edge = self.operators.get(edge_id)
            if edge is None:
                return self._unknown(
                    UNKNOWN_MISSING_OPERATOR,
                    reason=f"MISSING_OPERATOR:{edge_id}",
                    initial=initial,
                    executed=executed,
                    final=state,
                )
            if edge.typed_loss is None or edge.loss_standing != VERIFIED_TYPED_LOSS:
                unverified_loss_edges.append(edge.edge_id)

            next_state, error = self._apply_edge(state, edge)
            if error is not None:
                return self._unknown(
                    UNKNOWN_PATH_DISCONTINUITY if error.startswith("EDGE_SOURCE_MISMATCH") else UNKNOWN_TRANSFORM,
                    reason=error,
                    initial=initial,
                    executed=executed,
                    final=state,
                )
            state = next_state
            executed.append(edge.edge_id)

        if state.coordinate != initial.coordinate:
            return self._unknown(
                UNKNOWN_NOT_CLOSED,
                reason=f"FINAL_COORDINATE_NOT_INITIAL:{state.coordinate}!={initial.coordinate}",
                initial=initial,
                executed=executed,
                final=state,
            )

        if unverified_loss_edges:
            return self._unknown(
                UNKNOWN_UNTYPED_LOSS,
                reason="LOOP_CONTAINS_EDGE_WITHOUT_VERIFIED_TYPED_LOSS_STANDING",
                initial=initial,
                executed=executed,
                final=state,
                errors=[f"UNVERIFIED_LOSS_EDGE:{x}" for x in unverified_loss_edges],
            )

        mismatches = {
            feature: {"initial": initial.values[feature], "final": state.values[feature]}
            for feature in self.feature_basis
            if state.values[feature] != initial.values[feature]
        }
        lost = sorted(state.irreversible_loss - initial.irreversible_loss)
        residue = {
            "value_mismatches": mismatches,
            "value_mismatch_count": len(mismatches),
            "irreversible_loss_features": lost,
            "irreversible_loss_count": len(lost),
        }
        nonzero = bool(mismatches or lost)

        declared_inverse_pairs = []
        for edge_id in executed:
            edge = self.operators[edge_id]
            if edge.inverse_edge_id and edge.inverse_edge_id in executed:
                pair = tuple(sorted((edge.edge_id, edge.inverse_edge_id)))
                if pair not in declared_inverse_pairs:
                    declared_inverse_pairs.append(pair)

        return {
            "version": CONNECTION_VERSION,
            "status": "DEFINED",
            "standing": DEFINED_STANDING,
            "control_standing": CONTROL_STANDING,
            "connection_defined": True,
            "projection_back_executed": True,
            "projection_back_operator": executed[-1],
            "initial_coordinate": initial.coordinate,
            "final_coordinate": state.coordinate,
            "initial_values": dict(initial.values),
            "final_values": dict(state.values),
            "executed_edge_ids": executed,
            "executed_edge_count": len(executed),
            "closed_loop_residue": residue,
            "closed_loop_residue_nonzero": nonzero,
            "declared_inverse_pairs_observed": [list(x) for x in declared_inverse_pairs],
            "final_irreversible_loss": sorted(state.irreversible_loss),
            "provenance_ledger": list(state.provenance),
            "source_evidence": "NONE_SYNTHETIC_CONTROL",
            "expected_class_used": False,
            "laws": list(LAWS),
        }
