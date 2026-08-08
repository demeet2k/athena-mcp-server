from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from typing import Any, Dict, List, Mapping, Sequence, Tuple

CONNECTION_VERSION = "MCK.HOLONOMY.CONNECTION.RUNTIME.V1"
PACKET_ARTIFACT = "ATHENA.MYTHIC.HOLONOMY.CONNECTION.V1"
PACKET_VERSION = "MCK.HOLONOMY.CONNECTION.V1"
OPERATOR_STANDING = "PREDECLARED_TYPED_CONNECTION_V1"

CONNECTION_RESOURCE = {
    "uri": "athena://symbolic/computation/mck/holonomy/connection/v1",
    "name": "ATHENA MCK Typed Connection / Closed Holonomy V1",
    "description": (
        "Read-only discrete affine-connection evaluator. It computes a true closed-loop "
        "state-space residual only when every traversed edge has an explicit predeclared "
        "typed operator and the full return path is executed. Missing or oracle-coupled "
        "operators fail closed. Computation is not source truth, practitioner validation, "
        "metaphysical evidence, or MCK.V2 promotion."
    ),
}

CONNECTION_TOOLS = [{
    "name": "athena_mck_closed_holonomy_evaluate",
    "description": (
        "Compose an explicit finite-dimensional affine connection around a closed loop. "
        "Returns the full transport trajectory, composed operator, and h_gamma=T_gamma(x0)-x0. "
        "No operator is inferred from expected labels, endpoint identity, prose loss metadata, "
        "or V0 representation-drift proxies."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["packet"],
        "properties": {"packet": {"type": "object"}},
        "additionalProperties": False,
    },
}]
CONNECTION_TOOL_NAMES = {x["name"] for x in CONNECTION_TOOLS}
CONNECTION_RESOURCES = [CONNECTION_RESOURCE]
CONNECTION_RESOURCE_URIS = {CONNECTION_RESOURCE["uri"]}

LAWS = [
    "PREDECLARED_CONNECTION != SOURCE_TRUTH",
    "OPERATOR_COMPLETENESS_REQUIRED_FOR_CLOSED_LOOP",
    "ANSWER_KEY != CONNECTION_OPERATOR",
    "ENDPOINT_IDENTITY != ZERO_HOLONOMY",
    "CONNECTION_COMPOSITION_ORDER_MATTERS",
    "CLOSED_LOOP_HOLONOMY != METAPHYSICAL_QUANTITY",
    "COMPUTED_OPERATOR_WITNESS != INDEPENDENT_WITNESS",
    "COMPUTED_OPERATOR_WITNESS != MCK_V2_PROMOTION",
    "V0_OPEN_PATH_PROXY != V1_CLOSED_LOOP_OPERATOR_WITNESS",
]

_ALLOWED_TOP = {"artifact", "version", "packet_id", "state_space", "connections", "loop", "comparison_loop", "source_refs"}
_ALLOWED_STATE = {"basis_id", "dimension", "initial_state", "state_semantics"}
_ALLOWED_CONNECTION = {
    "connection_id", "source_layer", "target_layer", "matrix", "offset",
    "operator_standing", "operator_source_ref", "provenance", "declared_loss",
}
_ALLOWED_LOOP = {"loop_id", "start_layer", "connection_ids"}
_FORBIDDEN_ORACLE_KEYS = {
    "expected_class", "expected_label", "expected_result", "answer_key", "oracle",
    "desired_result", "target_holonomy", "expected_holonomy", "holonomy_answer",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _walk_keys(value: Any):
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _has_oracle_key(packet: Mapping[str, Any]) -> bool:
    for key in _walk_keys(packet):
        normalized = key.strip().lower().replace("-", "_")
        if normalized in _FORBIDDEN_ORACLE_KEYS:
            return True
        if "answer_key" in normalized or normalized.startswith("oracle_"):
            return True
    return False


def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("non_numeric")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non_finite")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("non_numeric") from None
    if not d.is_finite():
        raise ValueError("non_finite")
    return d


def _public_number(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _public_vector(values: Sequence[Decimal]) -> List[int | float]:
    return [_public_number(v) for v in values]


def _public_matrix(values: Sequence[Sequence[Decimal]]) -> List[List[int | float]]:
    return [_public_vector(row) for row in values]


def _identity(n: int) -> List[List[Decimal]]:
    return [[Decimal(1 if i == j else 0) for j in range(n)] for i in range(n)]


def _zero(n: int) -> List[Decimal]:
    return [Decimal(0) for _ in range(n)]


def _mat_vec(matrix: Sequence[Sequence[Decimal]], vector: Sequence[Decimal]) -> List[Decimal]:
    return [sum((row[j] * vector[j] for j in range(len(vector))), Decimal(0)) for row in matrix]


def _mat_mul(left: Sequence[Sequence[Decimal]], right: Sequence[Sequence[Decimal]]) -> List[List[Decimal]]:
    n = len(left)
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(n)), Decimal(0))
            for j in range(n)
        ]
        for i in range(n)
    ]


def _vec_add(left: Sequence[Decimal], right: Sequence[Decimal]) -> List[Decimal]:
    return [a + b for a, b in zip(left, right)]


def _vec_sub(left: Sequence[Decimal], right: Sequence[Decimal]) -> List[Decimal]:
    return [a - b for a, b in zip(left, right)]


def _matrix_equal(a: Sequence[Sequence[Decimal]], b: Sequence[Sequence[Decimal]]) -> bool:
    return all(x == y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def _vector_equal(a: Sequence[Decimal], b: Sequence[Decimal]) -> bool:
    return all(x == y for x, y in zip(a, b))


def _error(status: str, errors: Sequence[str]) -> Dict[str, Any]:
    return {
        "version": CONNECTION_VERSION,
        "status": status,
        "errors": list(dict.fromkeys(errors)),
        "projection_back_executed": False,
        "closed_loop_holonomy": "UNKNOWN",
        "closed_loop_holonomy_standing": "HOLD_NO_COMPLETE_TYPED_CONNECTION_WITNESS",
        "authority": "NONE",
        "mck_v2_promotion": False,
        "laws": list(LAWS),
    }


class ClosedHolonomyConnectionRuntime:
    def _validate_packet(self, packet: Mapping[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        errors: List[str] = []
        parsed: Dict[str, Any] = {}

        unknown_top = sorted(set(packet) - _ALLOWED_TOP)
        if unknown_top:
            errors.extend(f"unknown_top_level:{key}" for key in unknown_top)
        if _has_oracle_key(packet):
            errors.append("oracle_coupled_packet")
        if packet.get("artifact") != PACKET_ARTIFACT:
            errors.append("artifact")
        if packet.get("version") != PACKET_VERSION:
            errors.append("version")

        state = packet.get("state_space")
        if not isinstance(state, Mapping):
            errors.append("state_space")
            state = {}
        else:
            unknown_state = sorted(set(state) - _ALLOWED_STATE)
            errors.extend(f"unknown_state_space:{key}" for key in unknown_state)

        dimension = state.get("dimension")
        if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1 or dimension > 32:
            errors.append("dimension")
            dimension = 0
        basis_id = state.get("basis_id")
        if not isinstance(basis_id, str) or not basis_id:
            errors.append("basis_id")

        initial_raw = state.get("initial_state")
        initial: List[Decimal] = []
        if not isinstance(initial_raw, list) or len(initial_raw) != dimension:
            errors.append("initial_state_dimension")
        else:
            for i, value in enumerate(initial_raw):
                try:
                    initial.append(_decimal(value))
                except ValueError as exc:
                    errors.append(f"initial_state[{i}]:{exc}")

        semantics = state.get("state_semantics")
        if semantics is not None and (
            not isinstance(semantics, list)
            or len(semantics) != dimension
            or not all(isinstance(x, str) and x for x in semantics)
        ):
            errors.append("state_semantics_dimension")

        raw_connections = packet.get("connections")
        if not isinstance(raw_connections, list) or not raw_connections:
            errors.append("connections")
            raw_connections = []

        connections: Dict[str, Dict[str, Any]] = {}
        for idx, raw in enumerate(raw_connections):
            if not isinstance(raw, Mapping):
                errors.append(f"connection[{idx}]")
                continue
            unknown = sorted(set(raw) - _ALLOWED_CONNECTION)
            errors.extend(f"connection[{idx}].unknown:{key}" for key in unknown)
            cid = raw.get("connection_id")
            if not isinstance(cid, str) or not cid:
                errors.append(f"connection[{idx}].connection_id")
                continue
            if cid in connections:
                errors.append(f"duplicate_connection_id:{cid}")
                continue

            source = raw.get("source_layer")
            target = raw.get("target_layer")
            if not isinstance(source, str) or not source:
                errors.append(f"connection[{idx}].source_layer")
            if not isinstance(target, str) or not target:
                errors.append(f"connection[{idx}].target_layer")
            if raw.get("operator_standing") != OPERATOR_STANDING:
                errors.append(f"connection[{idx}].operator_standing")
            source_ref = raw.get("operator_source_ref")
            if not isinstance(source_ref, str) or not source_ref:
                errors.append(f"connection[{idx}].operator_source_ref")
            provenance = raw.get("provenance")
            if not isinstance(provenance, list) or not provenance or not all(isinstance(x, str) and x for x in provenance):
                errors.append(f"connection[{idx}].provenance")
            declared_loss = raw.get("declared_loss")
            if not isinstance(declared_loss, list) or not all(isinstance(x, str) for x in declared_loss):
                errors.append(f"connection[{idx}].declared_loss")

            raw_matrix = raw.get("matrix")
            matrix: List[List[Decimal]] = []
            if (
                not isinstance(raw_matrix, list)
                or len(raw_matrix) != dimension
                or any(not isinstance(row, list) or len(row) != dimension for row in raw_matrix)
            ):
                errors.append(f"connection[{idx}].matrix_dimension")
            else:
                for i, row in enumerate(raw_matrix):
                    out_row: List[Decimal] = []
                    for j, value in enumerate(row):
                        try:
                            out_row.append(_decimal(value))
                        except ValueError as exc:
                            errors.append(f"connection[{idx}].matrix[{i}][{j}]:{exc}")
                    matrix.append(out_row)

            raw_offset = raw.get("offset")
            offset: List[Decimal] = []
            if not isinstance(raw_offset, list) or len(raw_offset) != dimension:
                errors.append(f"connection[{idx}].offset_dimension")
            else:
                for i, value in enumerate(raw_offset):
                    try:
                        offset.append(_decimal(value))
                    except ValueError as exc:
                        errors.append(f"connection[{idx}].offset[{i}]:{exc}")

            connections[cid] = {
                "connection_id": cid,
                "source_layer": source,
                "target_layer": target,
                "matrix": matrix,
                "offset": offset,
                "operator_standing": raw.get("operator_standing"),
                "operator_source_ref": source_ref,
                "provenance": list(provenance or []),
                "declared_loss": list(declared_loss or []),
            }

        loop_ok, loop_errors, loop = self._validate_loop(packet.get("loop"), "loop", connections)
        errors.extend(loop_errors)

        comparison = None
        if "comparison_loop" in packet:
            comp_ok, comp_errors, comparison = self._validate_loop(
                packet.get("comparison_loop"), "comparison_loop", connections
            )
            errors.extend(comp_errors)
            if loop_ok and comp_ok and loop and comparison and loop["start_layer"] != comparison["start_layer"]:
                errors.append("comparison_loop.start_layer_mismatch")

        parsed.update({
            "dimension": dimension,
            "basis_id": basis_id,
            "initial_state": initial,
            "state_semantics": list(semantics or []),
            "connections": connections,
            "loop": loop,
            "comparison_loop": comparison,
        })
        return not errors, errors, parsed

    def _validate_loop(
        self,
        raw_loop: Any,
        label: str,
        connections: Mapping[str, Mapping[str, Any]],
    ) -> Tuple[bool, List[str], Dict[str, Any] | None]:
        errors: List[str] = []
        if not isinstance(raw_loop, Mapping):
            return False, [label], None
        unknown = sorted(set(raw_loop) - _ALLOWED_LOOP)
        errors.extend(f"{label}.unknown:{key}" for key in unknown)
        loop_id = raw_loop.get("loop_id")
        if not isinstance(loop_id, str) or not loop_id:
            errors.append(f"{label}.loop_id")
        start = raw_loop.get("start_layer")
        if not isinstance(start, str) or not start:
            errors.append(f"{label}.start_layer")
        ids = raw_loop.get("connection_ids")
        if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x for x in ids):
            errors.append(f"{label}.connection_ids")
            ids = []

        current = start
        for i, cid in enumerate(ids):
            edge = connections.get(cid)
            if edge is None:
                errors.append(f"{label}.missing_connection:{cid}")
                continue
            if current != edge.get("source_layer"):
                errors.append(f"{label}.discontinuous_edge:{i}:{cid}")
            current = edge.get("target_layer")
        if ids and current != start:
            errors.append(f"{label}.not_closed")

        return not errors, errors, {
            "loop_id": loop_id,
            "start_layer": start,
            "connection_ids": list(ids),
        }

    def _execute_loop(
        self,
        loop: Mapping[str, Any],
        initial: Sequence[Decimal],
        connections: Mapping[str, Mapping[str, Any]],
        dimension: int,
    ) -> Dict[str, Any]:
        state = list(initial)
        composite_matrix = _identity(dimension)
        composite_offset = _zero(dimension)
        receipts: List[Dict[str, Any]] = []
        route = [loop["start_layer"]]

        for index, cid in enumerate(loop["connection_ids"]):
            edge = connections[cid]
            before = list(state)
            after = _vec_add(_mat_vec(edge["matrix"], before), edge["offset"])
            composite_matrix = _mat_mul(edge["matrix"], composite_matrix)
            composite_offset = _vec_add(_mat_vec(edge["matrix"], composite_offset), edge["offset"])
            state = after
            route.append(edge["target_layer"])
            receipts.append({
                "step": index,
                "connection_id": cid,
                "source_layer": edge["source_layer"],
                "target_layer": edge["target_layer"],
                "state_before": _public_vector(before),
                "state_after": _public_vector(after),
                "operator_standing": edge["operator_standing"],
                "operator_source_ref": edge["operator_source_ref"],
                "provenance": list(edge["provenance"]),
                "declared_loss": list(edge["declared_loss"]),
            })

        residual = _vec_sub(state, initial)
        identity = _identity(dimension)
        zero = _zero(dimension)
        operator_nonidentity = (
            not _matrix_equal(composite_matrix, identity)
            or not _vector_equal(composite_offset, zero)
        )
        state_nonzero = not _vector_equal(residual, zero)
        operator_packet = {
            "matrix": _public_matrix(composite_matrix),
            "offset": _public_vector(composite_offset),
        }
        return {
            "loop_id": loop["loop_id"],
            "start_layer": loop["start_layer"],
            "layer_route": route,
            "connection_ids": list(loop["connection_ids"]),
            "all_edges_executed": True,
            "return_edge_executed": True,
            "projection_back_executed": True,
            "initial_state": _public_vector(initial),
            "final_state": _public_vector(state),
            "transport_receipts": receipts,
            "composed_operator": operator_packet,
            "composed_operator_sha256": _digest(operator_packet),
            "closed_loop_holonomy_vector": _public_vector(residual),
            "closed_loop_holonomy_nonzero": state_nonzero,
            "operator_holonomy_nonidentity": operator_nonidentity,
            "_matrix_decimal": composite_matrix,
            "_offset_decimal": composite_offset,
            "_final_decimal": state,
        }

    def evaluate(self, packet: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(packet, Mapping):
            return _error("HOLD_INVALID_CONNECTION_PACKET", ["packet"])
        valid, errors, parsed = self._validate_packet(packet)
        if not valid:
            status = (
                "HOLD_ORACLE_COUPLED_PACKET"
                if "oracle_coupled_packet" in errors
                else "HOLD_INVALID_CONNECTION_PACKET"
            )
            return _error(status, errors)

        primary = self._execute_loop(
            parsed["loop"],
            parsed["initial_state"],
            parsed["connections"],
            parsed["dimension"],
        )

        comparison_public = None
        path_order_sensitive: bool | str = "NOT_EVALUATED"
        initial_state_difference: bool | str = "NOT_EVALUATED"
        if parsed["comparison_loop"] is not None:
            comparison = self._execute_loop(
                parsed["comparison_loop"],
                parsed["initial_state"],
                parsed["connections"],
                parsed["dimension"],
            )
            path_order_sensitive = (
                not _matrix_equal(primary["_matrix_decimal"], comparison["_matrix_decimal"])
                or not _vector_equal(primary["_offset_decimal"], comparison["_offset_decimal"])
            )
            initial_state_difference = not _vector_equal(
                primary["_final_decimal"], comparison["_final_decimal"]
            )
            comparison_public = {
                k: v for k, v in comparison.items() if not k.startswith("_")
            }

        primary_public = {k: v for k, v in primary.items() if not k.startswith("_")}
        operator_manifest = {
            "basis_id": parsed["basis_id"],
            "dimension": parsed["dimension"],
            "initial_state": _public_vector(parsed["initial_state"]),
            "connections": [
                {
                    "connection_id": edge["connection_id"],
                    "source_layer": edge["source_layer"],
                    "target_layer": edge["target_layer"],
                    "matrix": _public_matrix(edge["matrix"]),
                    "offset": _public_vector(edge["offset"]),
                    "operator_standing": edge["operator_standing"],
                    "operator_source_ref": edge["operator_source_ref"],
                    "provenance": list(edge["provenance"]),
                    "declared_loss": list(edge["declared_loss"]),
                }
                for edge in (parsed["connections"][cid] for cid in sorted(parsed["connections"]))
            ],
            "loop": dict(parsed["loop"]),
            "comparison_loop": (
                dict(parsed["comparison_loop"]) if parsed["comparison_loop"] is not None else None
            ),
        }

        return {
            "version": CONNECTION_VERSION,
            "status": "CLOSED_LOOP_HOLONOMY_COMPUTED_V1",
            "packet_identity": {
                "artifact": packet.get("artifact"),
                "version": packet.get("version"),
                "packet_id": packet.get("packet_id"),
            },
            "basis_id": parsed["basis_id"],
            "dimension": parsed["dimension"],
            "state_semantics": parsed["state_semantics"],
            "operator_manifest_sha256": _digest(operator_manifest),
            "operator_standing": OPERATOR_STANDING,
            "primary_loop": primary_public,
            "comparison_loop": comparison_public,
            "path_order_sensitive": path_order_sensitive,
            "path_order_effect_observed_on_initial_state": initial_state_difference,
            "projection_back_executed": True,
            "closed_loop_holonomy": primary_public["closed_loop_holonomy_vector"],
            "closed_loop_holonomy_standing": (
                "COMPUTED_DISCRETE_AFFINE_CONNECTION_V1_CALLER_PREDECLARED_OPERATORS"
            ),
            "source_validation": "NOT_PERFORMED",
            "practitioner_review": "HOLD_EXTERNAL_REVIEW",
            "independent_witness": False,
            "mck_v2_promotion": False,
            "authority": "READ_ONLY_COMPUTATIONAL_CONNECTION_WITNESS_ONLY",
            "laws": list(LAWS),
        }


def connection_resource_payload() -> Dict[str, Any]:
    return {
        "version": CONNECTION_VERSION,
        "packet_artifact": PACKET_ARTIFACT,
        "packet_version": PACKET_VERSION,
        "operator_model": "x_next = A_edge * x + b_edge",
        "closed_loop_operator": "T_gamma = T_en o ... o T_e1",
        "state_holonomy": "h_gamma(x0) = T_gamma(x0) - x0",
        "operator_holonomy": "T_gamma != identity_affine_operator",
        "operator_standing_required": OPERATOR_STANDING,
        "projection_back_executed": "ONLY_AFTER_EVERY_CONNECTION_ID_IN_CLOSED_LOOP_EXECUTES",
        "missing_connection_behavior": "HOLD",
        "oracle_coupling_behavior": "HOLD",
        "scalarization": "DISABLED_V1",
        "source_validation": "NOT_PERFORMED",
        "practitioner_review": "HOLD_EXTERNAL_REVIEW",
        "mck_v2_promotion": False,
        "authority": "READ_ONLY_COMPUTATIONAL_CONNECTION_WITNESS_ONLY",
        "laws": list(LAWS),
    }
