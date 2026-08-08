from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Mapping, Sequence

ARTIFACT = "ATHENA.AQ001C.SEMANTIC_CONNECTION_CONTROL.V1"
DEFINED = "DEFINED"
UNKNOWN = "UNKNOWN"
ZERO_RESIDUE = "ZERO_RESIDUE"
NONZERO_RESIDUE = "NONZERO_RESIDUE"
UNKNOWN_RESIDUE = "UNKNOWN_RESIDUE"

# Raw connection behavior must never branch on post-hoc benchmark labels.
FORBIDDEN_RAW_KEYS = frozenset({
    "expected_class",
    "expected_label",
    "answer_key",
    "oracle_label",
})

_ALLOWED_OPS = frozenset({"IDENTITY", "SET", "ADD", "SCALE", "DELETE"})
_MISSING = {"$state": "MISSING"}
_IRREVERSIBLY_LOST = {"$state": "IRREVERSIBLY_LOST"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _deepcopy_json(value: Any) -> Any:
    # The V1 synthetic harness deliberately accepts JSON-like public state only.
    return json.loads(json.dumps(value, ensure_ascii=False))


@dataclass(frozen=True)
class SemanticState:
    """Typed transported semantic state in one explicit ambient feature basis.

    `provenance` is an audit/path ledger. It is intentionally excluded from the
    semantic residue so bookkeeping memory cannot manufacture holonomy.
    `irreversible_loss` is semantic state and therefore participates in residue.

    The feature basis is immutable across a defined connection. DELETE therefore
    writes a typed loss sentinel in-basis rather than changing the coordinate
    dimension; a later SET may restore the visible value while the irreversible
    loss ledger preserves the fact that identity was not transported losslessly.
    """

    coordinate: str
    values: Mapping[str, Any]
    feature_basis: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    irreversible_loss: frozenset[str] = frozenset()
    standing: str = "SYNTHETIC_CONTROL"

    def __post_init__(self) -> None:
        if not self.coordinate:
            raise ValueError("coordinate is required")
        values = _deepcopy_json(dict(self.values))
        basis = tuple(dict.fromkeys(str(x) for x in self.feature_basis)) or tuple(sorted(values))
        if not basis:
            raise ValueError("feature_basis is required")
        if len(basis) != len(set(basis)):
            raise ValueError("feature_basis contains duplicates")
        value_keys = set(values)
        basis_keys = set(basis)
        if value_keys != basis_keys:
            missing = sorted(basis_keys - value_keys)
            extra = sorted(value_keys - basis_keys)
            raise ValueError(f"values must exactly match feature_basis missing={missing} extra={extra}")
        irreversible = frozenset(str(x) for x in self.irreversible_loss)
        if not irreversible.issubset(basis_keys):
            extra_loss = sorted(irreversible - basis_keys)
            raise ValueError(f"irreversible_loss outside feature_basis: {extra_loss}")
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "feature_basis", basis)
        object.__setattr__(self, "provenance", tuple(str(x) for x in self.provenance))
        object.__setattr__(self, "irreversible_loss", irreversible)

    def public_semantics(self) -> dict[str, Any]:
        return {
            "coordinate": self.coordinate,
            "feature_basis": list(self.feature_basis),
            "values": _deepcopy_json(dict(self.values)),
            "irreversible_loss": sorted(self.irreversible_loss),
            "standing": self.standing,
        }

    def audit_view(self) -> dict[str, Any]:
        return {
            **self.public_semantics(),
            "provenance": list(self.provenance),
        }


@dataclass(frozen=True)
class FieldOperation:
    field: str
    op: str
    value: Any = None

    def __post_init__(self) -> None:
        op = str(self.op).upper()
        object.__setattr__(self, "op", op)
        if not self.field:
            raise ValueError("field is required")
        if op not in _ALLOWED_OPS:
            raise ValueError(f"unsupported field operation: {op}")
        if op in {"ADD", "SCALE"} and not isinstance(self.value, (int, float)):
            raise ValueError(f"{op} requires a numeric value")

    def to_dict(self) -> dict[str, Any]:
        return {"field": self.field, "op": self.op, "value": _deepcopy_json(self.value)}


@dataclass(frozen=True)
class EdgeOperator:
    edge_id: str
    source: str
    target: str
    operations: tuple[FieldOperation, ...] = ()
    inverse_edge_id: str | None = None
    typed_loss: frozenset[str] = frozenset()
    provenance: tuple[str, ...] = ()
    standing: str = "SYNTHETIC_CONTROL"
    typed: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.edge_id or not self.source or not self.target:
            raise ValueError("edge_id, source and target are required")
        object.__setattr__(self, "operations", tuple(self.operations))
        object.__setattr__(self, "typed_loss", frozenset(str(x) for x in self.typed_loss))
        object.__setattr__(self, "provenance", tuple(str(x) for x in self.provenance))
        object.__setattr__(self, "metadata", _deepcopy_json(dict(self.metadata)))

    def raw_spec(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "operations": [op.to_dict() for op in self.operations],
            "inverse_edge_id": self.inverse_edge_id,
            "typed_loss": sorted(self.typed_loss),
            "provenance": list(self.provenance),
            "standing": self.standing,
            "typed": self.typed,
            "metadata": _deepcopy_json(dict(self.metadata)),
        }


@dataclass(frozen=True)
class ConnectionResult:
    standing: str
    classification: str
    reason: str
    initial_state: SemanticState
    final_state: SemanticState | None
    residue: Mapping[str, Any] | None
    executed_edges: tuple[str, ...]
    audit: Mapping[str, Any]

    @property
    def residue_zero(self) -> bool | None:
        if self.standing != DEFINED or self.residue is None:
            return None
        return not bool(self.residue)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact": ARTIFACT,
            "standing": self.standing,
            "classification": self.classification,
            "reason": self.reason,
            "initial_state": self.initial_state.audit_view(),
            "final_state": self.final_state.audit_view() if self.final_state else None,
            "residue": _deepcopy_json(dict(self.residue)) if self.residue is not None else None,
            "residue_zero": self.residue_zero,
            "executed_edges": list(self.executed_edges),
            "audit": _deepcopy_json(dict(self.audit)),
        }


def _unknown(
    initial: SemanticState,
    reason: str,
    *,
    executed_edges: Iterable[str] = (),
    final_state: SemanticState | None = None,
    audit: Mapping[str, Any] | None = None,
) -> ConnectionResult:
    return ConnectionResult(
        standing=UNKNOWN,
        classification=UNKNOWN_RESIDUE,
        reason=reason,
        initial_state=initial,
        final_state=final_state,
        residue=None,
        executed_edges=tuple(executed_edges),
        audit=dict(audit or {}),
    )


def _metadata_is_oracle_free(edge: EdgeOperator) -> bool:
    return not bool(FORBIDDEN_RAW_KEYS.intersection(edge.metadata))


def _apply_field_operation(values: dict[str, Any], operation: FieldOperation) -> tuple[bool, str | None]:
    field_name = operation.field
    op = operation.op
    if field_name not in values:
        return False, f"FIELD_OUTSIDE_BASIS:{field_name}"
    if op == "IDENTITY":
        return True, None
    if op == "SET":
        values[field_name] = _deepcopy_json(operation.value)
        return True, None
    if op == "DELETE":
        values[field_name] = _deepcopy_json(_IRREVERSIBLY_LOST)
        return True, None

    current = values.get(field_name, _MISSING)
    if current in (_MISSING, _IRREVERSIBLY_LOST):
        return False, f"MISSING_NUMERIC_FIELD:{field_name}"
    if not isinstance(current, (int, float)):
        return False, f"NON_NUMERIC_FIELD:{field_name}"
    if op == "ADD":
        values[field_name] = current + operation.value
        return True, None
    if op == "SCALE":
        values[field_name] = current * operation.value
        return True, None
    return False, f"UNSUPPORTED_OPERATION:{op}"


def _apply_edge(state: SemanticState, edge: EdgeOperator) -> tuple[SemanticState | None, str | None]:
    if not edge.typed:
        return None, f"UNTYPED_EDGE:{edge.edge_id}"
    if not _metadata_is_oracle_free(edge):
        return None, f"ORACLE_METADATA_FORBIDDEN:{edge.edge_id}"
    if state.coordinate != edge.source:
        return None, f"SOURCE_MISMATCH:{edge.edge_id}:{state.coordinate}!={edge.source}"

    basis = set(state.feature_basis)
    operation_fields = {op.field for op in edge.operations}
    outside_basis = sorted(operation_fields - basis)
    if outside_basis:
        return None, f"FIELD_OUTSIDE_BASIS:{edge.edge_id}:{','.join(outside_basis)}"

    delete_fields = {op.field for op in edge.operations if op.op == "DELETE"}
    typed_loss = set(edge.typed_loss)
    loss_outside_basis = sorted(typed_loss - basis)
    if loss_outside_basis:
        return None, f"LOSS_OUTSIDE_BASIS:{edge.edge_id}:{','.join(loss_outside_basis)}"
    if not delete_fields.issubset(typed_loss):
        missing = sorted(delete_fields - typed_loss)
        return None, f"UNTYPED_DELETE:{edge.edge_id}:{','.join(missing)}"
    phantom_loss = sorted(typed_loss - delete_fields)
    if phantom_loss:
        return None, f"UNEXECUTED_TYPED_LOSS:{edge.edge_id}:{','.join(phantom_loss)}"
    unavailable_loss_source = sorted(
        field_name
        for field_name in delete_fields
        if state.values.get(field_name, _MISSING) in (_MISSING, _IRREVERSIBLY_LOST)
    )
    if unavailable_loss_source:
        return None, f"LOSS_SOURCE_MISSING:{edge.edge_id}:{','.join(unavailable_loss_source)}"

    values = _deepcopy_json(dict(state.values))
    for operation in edge.operations:
        ok, reason = _apply_field_operation(values, operation)
        if not ok:
            return None, f"{reason}:{edge.edge_id}"

    # V1 irreversible loss is deletion-backed: every loss marker corresponds to a
    # feature that existed in the fixed ambient basis and was actually erased on
    # this execution. The marker survives even if a later edge restores the same
    # syntactic value. Representation/audit fields never enter semantic residue.
    irreversible = frozenset(set(state.irreversible_loss) | typed_loss)
    provenance = state.provenance + (f"EDGE::{edge.edge_id}",) + edge.provenance
    return (
        SemanticState(
            coordinate=edge.target,
            values=values,
            feature_basis=state.feature_basis,
            provenance=provenance,
            irreversible_loss=irreversible,
            standing=state.standing,
        ),
        None,
    )


def semantic_residue(initial: SemanticState, final: SemanticState) -> dict[str, Any]:
    """Return a typed semantic residue; `{}` is exact zero.

    Path/provenance bookkeeping is intentionally absent. Both states must be in
    the same fixed ambient feature basis; route closure is checked by the caller.
    """

    if initial.feature_basis != final.feature_basis:
        raise ValueError("semantic residue requires identical feature_basis")

    residue: dict[str, Any] = {}
    for key in initial.feature_basis:
        before = initial.values[key]
        after = final.values[key]
        if before != after:
            residue[key] = {
                "before": _deepcopy_json(before),
                "after": _deepcopy_json(after),
            }

    if initial.irreversible_loss != final.irreversible_loss:
        residue["__irreversible_loss__"] = {
            "before": sorted(initial.irreversible_loss),
            "after": sorted(final.irreversible_loss),
        }
    if initial.standing != final.standing:
        residue["__standing__"] = {"before": initial.standing, "after": final.standing}
    return residue


def compose_closed_route(
    initial: SemanticState,
    edge_ids: Sequence[str],
    operators: Mapping[str, EdgeOperator],
) -> ConnectionResult:
    """Execute an explicitly typed closed route in one ambient feature basis.

    Missing/untyped/ill-typed edges and open routes are UNKNOWN. A result is
    DEFINED only after every declared edge executes and the final coordinate is
    the initial coordinate without changing the feature basis.
    """

    if not edge_ids:
        return ConnectionResult(
            standing=DEFINED,
            classification=ZERO_RESIDUE,
            reason="EMPTY_IDENTITY_ROUTE",
            initial_state=initial,
            final_state=initial,
            residue={},
            executed_edges=(),
            audit={"route": [], "connection_defined": True, "feature_basis": list(initial.feature_basis)},
        )

    current = initial
    executed: list[str] = []
    edge_digests: list[str] = []
    for edge_id in edge_ids:
        edge = operators.get(edge_id)
        if edge is None:
            return _unknown(
                initial,
                f"MISSING_EDGE_OPERATOR:{edge_id}",
                executed_edges=executed,
                final_state=current,
                audit={"route": list(edge_ids), "connection_defined": False},
            )
        next_state, reason = _apply_edge(current, edge)
        if next_state is None:
            return _unknown(
                initial,
                reason or f"EDGE_UNDEFINED:{edge_id}",
                executed_edges=executed,
                final_state=current,
                audit={"route": list(edge_ids), "failed_edge": edge_id, "connection_defined": False},
            )
        current = next_state
        executed.append(edge_id)
        edge_digests.append(digest(edge.raw_spec()))

    if current.coordinate != initial.coordinate:
        return _unknown(
            initial,
            f"OPEN_PATH_NO_RETURN:{current.coordinate}!={initial.coordinate}",
            executed_edges=executed,
            final_state=current,
            audit={"route": list(edge_ids), "connection_defined": False, "edge_digests": edge_digests},
        )
    if current.feature_basis != initial.feature_basis:
        return _unknown(
            initial,
            "AMBIENT_BASIS_CHANGED",
            executed_edges=executed,
            final_state=current,
            audit={"route": list(edge_ids), "connection_defined": False, "edge_digests": edge_digests},
        )

    residue = semantic_residue(initial, current)
    classification = ZERO_RESIDUE if not residue else NONZERO_RESIDUE
    return ConnectionResult(
        standing=DEFINED,
        classification=classification,
        reason="CLOSED_TYPED_CONNECTION_EXECUTED",
        initial_state=initial,
        final_state=current,
        residue=residue,
        executed_edges=tuple(executed),
        audit={
            "route": list(edge_ids),
            "edge_digests": edge_digests,
            "connection_defined": True,
            "feature_basis": list(initial.feature_basis),
            "provenance_excluded_from_residue": True,
            "final_provenance": list(current.provenance),
        },
    )


def declared_round_trip(
    initial: SemanticState,
    forward_edge_id: str,
    operators: Mapping[str, EdgeOperator],
) -> ConnectionResult:
    """Execute one edge and its explicitly declared inverse.

    The helper intentionally refuses to guess a return edge. Missing inverse
    declaration or implementation is UNKNOWN. Inverse metadata does not prove
    reversibility: the operators are still executed and residue is measured.
    """

    forward = operators.get(forward_edge_id)
    if forward is None:
        return _unknown(initial, f"MISSING_EDGE_OPERATOR:{forward_edge_id}")
    if not forward.typed:
        return _unknown(initial, f"UNTYPED_EDGE:{forward_edge_id}")
    if not forward.inverse_edge_id:
        return _unknown(initial, f"MISSING_DECLARED_INVERSE:{forward_edge_id}")
    inverse = operators.get(forward.inverse_edge_id)
    if inverse is None:
        return _unknown(initial, f"MISSING_INVERSE_OPERATOR:{forward.inverse_edge_id}")
    if inverse.inverse_edge_id not in (None, forward.edge_id):
        return _unknown(initial, f"INVERSE_DECLARATION_CONFLICT:{inverse.edge_id}")
    if inverse.source != forward.target or inverse.target != forward.source:
        return _unknown(initial, f"INVERSE_ENDPOINT_MISMATCH:{inverse.edge_id}")
    return compose_closed_route(initial, [forward.edge_id, inverse.edge_id], operators)


def raw_behavior_with_expected_label(
    initial: SemanticState,
    edge_ids: Sequence[str],
    operators: Mapping[str, EdgeOperator],
    *,
    expected_class: str | None = None,
) -> ConnectionResult:
    """Compatibility fixture proving expected labels are post-hoc only.

    `expected_class` is accepted to make mutation tests explicit and deliberately
    not read by the raw connection engine.
    """

    del expected_class
    return compose_closed_route(initial, edge_ids, operators)


def with_metadata(edge: EdgeOperator, **metadata: Any) -> EdgeOperator:
    merged = dict(edge.metadata)
    merged.update(metadata)
    return replace(edge, metadata=merged)
