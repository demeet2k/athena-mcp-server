from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple

from athena_mcp.mythic_connection_control import (
    CONTROL_STANDING,
    VERIFIED_TYPED_LOSS,
    EdgeOperator,
    FeatureTransform,
    SyntheticConnectionRuntime,
)

PACKET_ARTIFACT = "ATHENA.MCK.CONNECTION.OPERATOR_PACKET.V1"
PACKET_VERSION = "MCK.CONNECTION.PACKET.V1"
PACKET_STANDING = "SYNTHETIC_CONTROL_PACKET_NOT_SOURCE_EVIDENCE"
HISTORICAL_MAPPING_STATUS = "HOLD_EMPTY_V1_PROPOSAL"
PACKET_LOSS_STANDING = "SCHEMA_TYPED_CONTROL_DECLARATION"
SOURCE_EVIDENCE = "NONE_SYNTHETIC_CONTROL"
IMPLEMENTATION_WITNESS = "EXTERNAL_BINDING_REQUIRED"
PACKET_DIGEST_DOMAIN = "MCK.CONNECTION.PACKET.SEMANTIC.V1"
REGISTRY_DIGEST_DOMAIN = "MCK.CONNECTION.OPERATOR.REGISTRY.V1"

ALLOWED_TRANSFORMS = frozenset({"IDENTITY", "SET", "ADD", "MUL"})
RESERVED_ORACLE_KEYS = frozenset(
    {"expected_class", "expected", "answer_key", "oracle", "benchmark_label"}
)

MANDATORY_FIREWALLS = frozenset(
    {
        "EXPECTED_CLASS != CONNECTION_DEFINITION",
        "SYNTHETIC_CONTROL_PACKET != HISTORICAL_SOURCE_EVIDENCE",
        "PACKET_DIGEST != INTERPRETER_IMPLEMENTATION_WITNESS",
    }
)


class PacketValidationError(ValueError):
    """Fail-closed validation error for MCK synthetic connection packets."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}" if detail else code)


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise PacketValidationError(code, detail)


def _is_sequence(value: Any) -> bool:
    return isinstance(value, list)


def _scan_reserved_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in RESERVED_ORACLE_KEYS:
                raise PacketValidationError("RESERVED_ORACLE_FIELD", f"{path}.{key}")
            _scan_reserved_keys(child, f"{path}.{key}")
    elif _is_sequence(value):
        for index, child in enumerate(value):
            _scan_reserved_keys(child, f"{path}[{index}]")


def _require_finite_json(value: Any, path: str) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return
    if isinstance(value, float):
        _require(math.isfinite(value), "NONFINITE_JSON_NUMBER", path)
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _require(isinstance(key, str), "NONSTRING_JSON_KEY", f"{path}.{key}")
            _require_finite_json(child, f"{path}.{key}")
        return
    if _is_sequence(value):
        for index, child in enumerate(value):
            _require_finite_json(child, f"{path}[{index}]")
        return
    raise PacketValidationError("NON_JSON_VALUE", path)


def _nonempty_string(value: Any, code: str, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), code, path)
    return value.strip()


def _unique_strings(value: Any, code: str, path: str, *, nonempty: bool = True) -> Tuple[str, ...]:
    _require(_is_sequence(value), code, path)
    out = []
    seen = set()
    for index, item in enumerate(value):
        if nonempty:
            item = _nonempty_string(item, code, f"{path}[{index}]")
        else:
            _require(isinstance(item, str), code, f"{path}[{index}]")
        _require(item not in seen, f"DUPLICATE_{code}", item)
        seen.add(item)
        out.append(item)
    return tuple(out)


def _validate_transform(transform: Any, path: str) -> Dict[str, Any]:
    _require(isinstance(transform, Mapping), "INVALID_TRANSFORM_OBJECT", path)
    allowed_keys = {"op", "operand"}
    extra = set(transform) - allowed_keys
    _require(not extra, "UNKNOWN_TRANSFORM_FIELD", f"{path}:{','.join(sorted(map(str, extra)))}")

    op = _nonempty_string(transform.get("op"), "INVALID_TRANSFORM_OP", f"{path}.op")
    _require(op in ALLOWED_TRANSFORMS, "UNSUPPORTED_TRANSFORM", f"{path}:{op}")

    has_operand = "operand" in transform
    operand = transform.get("operand")
    if op == "IDENTITY":
        _require(not has_operand or operand is None, "IDENTITY_OPERAND_FORBIDDEN", path)
    elif op in {"ADD", "MUL"}:
        _require(
            isinstance(operand, (int, float)) and not isinstance(operand, bool),
            "NUMERIC_OPERAND_REQUIRED",
            path,
        )
        _require_finite_json(operand, f"{path}.operand")
    else:  # SET
        _require(has_operand, "SET_OPERAND_REQUIRED", path)
        _require_finite_json(operand, f"{path}.operand")

    canonical: Dict[str, Any] = {"op": op}
    if has_operand:
        canonical["operand"] = copy.deepcopy(operand)
    return canonical


def _validate_operator(operator: Any, feature_set: frozenset[str], index: int) -> Dict[str, Any]:
    path = f"$.operators[{index}]"
    _require(isinstance(operator, Mapping), "INVALID_OPERATOR_OBJECT", path)
    allowed_keys = {
        "edge_id",
        "source_coordinate",
        "target_coordinate",
        "transforms",
        "typed_loss",
        "loss_standing",
        "inverse_edge_id",
        "provenance",
        "standing",
    }
    extra = set(operator) - allowed_keys
    _require(not extra, "UNKNOWN_OPERATOR_FIELD", f"{path}:{','.join(sorted(map(str, extra)))}")

    edge_id = _nonempty_string(operator.get("edge_id"), "INVALID_EDGE_ID", f"{path}.edge_id")
    source = _nonempty_string(
        operator.get("source_coordinate"), "INVALID_SOURCE_COORDINATE", f"{path}.source_coordinate"
    )
    target = _nonempty_string(
        operator.get("target_coordinate"), "INVALID_TARGET_COORDINATE", f"{path}.target_coordinate"
    )
    _require(operator.get("standing") == PACKET_STANDING, "INVALID_OPERATOR_STANDING", edge_id)

    transforms = operator.get("transforms")
    _require(isinstance(transforms, Mapping), "INVALID_TRANSFORMS", edge_id)
    canonical_transforms: Dict[str, Any] = {}
    for feature, transform in transforms.items():
        _require(isinstance(feature, str) and feature in feature_set, "TRANSFORM_FEATURE_OUTSIDE_BASIS", str(feature))
        _require(feature.strip().lower() not in RESERVED_ORACLE_KEYS, "RESERVED_ORACLE_FEATURE_ID", feature)
        canonical_transforms[feature] = _validate_transform(transform, f"{path}.transforms.{feature}")

    typed_loss = _unique_strings(operator.get("typed_loss"), "TYPED_LOSS", f"{path}.typed_loss")
    for feature in typed_loss:
        _require(feature in feature_set, "LOSS_FEATURE_OUTSIDE_BASIS", feature)
    _require(operator.get("loss_standing") == PACKET_LOSS_STANDING, "INVALID_LOSS_STANDING", edge_id)

    inverse = operator.get("inverse_edge_id")
    if inverse is not None:
        inverse = _nonempty_string(inverse, "INVALID_INVERSE_EDGE_ID", f"{path}.inverse_edge_id")

    provenance = _unique_strings(operator.get("provenance"), "PROVENANCE", f"{path}.provenance")
    _require(bool(provenance), "EMPTY_PROVENANCE", edge_id)

    return {
        "edge_id": edge_id,
        "source_coordinate": source,
        "target_coordinate": target,
        "transforms": {key: canonical_transforms[key] for key in sorted(canonical_transforms)},
        "typed_loss": sorted(typed_loss),
        "loss_standing": PACKET_LOSS_STANDING,
        "inverse_edge_id": inverse,
        "provenance": list(provenance),
        "standing": PACKET_STANDING,
    }


def _canonical_semantics(packet: Mapping[str, Any]) -> Dict[str, Any]:
    feature_basis = _unique_strings(packet.get("feature_basis"), "FEATURE_ID", "$.feature_basis")
    _require(bool(feature_basis), "EMPTY_FEATURE_BASIS")
    for feature in feature_basis:
        _require(feature.strip().lower() not in RESERVED_ORACLE_KEYS, "RESERVED_ORACLE_FEATURE_ID", feature)
    feature_set = frozenset(feature_basis)

    operators_raw = packet.get("operators")
    _require(_is_sequence(operators_raw) and bool(operators_raw), "EMPTY_OPERATOR_REGISTRY")
    operators = [_validate_operator(operator, feature_set, index) for index, operator in enumerate(operators_raw)]
    by_id: Dict[str, Dict[str, Any]] = {}
    for operator in operators:
        edge_id = operator["edge_id"]
        _require(edge_id not in by_id, "DUPLICATE_EDGE_ID", edge_id)
        by_id[edge_id] = operator

    for edge_id, operator in by_id.items():
        inverse_id = operator["inverse_edge_id"]
        if inverse_id is None:
            continue
        _require(inverse_id in by_id, "MISSING_DECLARED_INVERSE", f"{edge_id}:{inverse_id}")
        inverse = by_id[inverse_id]
        _require(
            inverse["source_coordinate"] == operator["target_coordinate"]
            and inverse["target_coordinate"] == operator["source_coordinate"],
            "INVERSE_COORDINATE_MISMATCH",
            f"{edge_id}:{inverse_id}",
        )
        _require(inverse["inverse_edge_id"] == edge_id, "INVERSE_NOT_MUTUAL", f"{edge_id}:{inverse_id}")

    historical = packet.get("historical_mapping")
    _require(isinstance(historical, Mapping), "INVALID_HISTORICAL_MAPPING")
    _require(set(historical) == {"status", "edges"}, "INVALID_HISTORICAL_MAPPING_SHAPE")
    _require(historical.get("status") == HISTORICAL_MAPPING_STATUS, "HISTORICAL_MAPPING_STATUS_INVALID")
    _require(_is_sequence(historical.get("edges")) and len(historical.get("edges")) == 0, "HISTORICAL_MAPPING_MUST_BE_EMPTY")

    firewalls = _unique_strings(packet.get("firewalls"), "FIREWALL", "$.firewalls")
    _require(MANDATORY_FIREWALLS.issubset(set(firewalls)), "MANDATORY_FIREWALL_MISSING")

    return {
        "artifact": PACKET_ARTIFACT,
        "version": PACKET_VERSION,
        "standing": PACKET_STANDING,
        "feature_basis": sorted(feature_basis),
        "operators": [by_id[edge_id] for edge_id in sorted(by_id)],
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "firewalls": sorted(firewalls),
    }


def _domain_digest(domain: str, semantic_value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        {"digest_domain": domain, "semantic_value": semantic_value},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def semantic_digest(semantic_packet: Mapping[str, Any]) -> str:
    return _domain_digest(PACKET_DIGEST_DOMAIN, semantic_packet)


def operator_registry_digest(semantic_packet: Mapping[str, Any]) -> str:
    registry = {
        "feature_basis": semantic_packet["feature_basis"],
        "operators": semantic_packet["operators"],
    }
    return _domain_digest(REGISTRY_DIGEST_DOMAIN, registry)


def validate_connection_packet(packet: Any) -> Dict[str, Any]:
    """Validate and canonically digest one synthetic MCK connection packet.

    The return is a public mechanism receipt only. It cannot self-assert repository
    CI, historical/source authority, or implementation verification.
    """

    try:
        _require(isinstance(packet, Mapping), "PACKET_NOT_OBJECT")
        _scan_reserved_keys(packet)
        allowed_packet_keys = {
            "artifact",
            "version",
            "standing",
            "feature_basis",
            "operators",
            "historical_mapping",
            "firewalls",
            "packet_semantic_digest",
            "operator_registry_digest",
        }
        extra_packet_keys = set(packet) - allowed_packet_keys
        _require(
            not extra_packet_keys,
            "UNKNOWN_PACKET_FIELD",
            ",".join(sorted(map(str, extra_packet_keys))),
        )
        _require(packet.get("artifact") == PACKET_ARTIFACT, "INVALID_ARTIFACT")
        _require(packet.get("version") == PACKET_VERSION, "INVALID_PACKET_VERSION")
        _require(packet.get("standing") == PACKET_STANDING, "INVALID_PACKET_STANDING")
        _require_finite_json(packet, "$")

        semantic = _canonical_semantics(packet)
        digest = semantic_digest(semantic)
        registry_digest = operator_registry_digest(semantic)
        supplied = packet.get("packet_semantic_digest")
        if supplied is not None:
            _require(
                isinstance(supplied, str) and supplied == digest,
                "PACKET_SEMANTIC_DIGEST_MISMATCH",
                str(supplied),
            )
        supplied_registry = packet.get("operator_registry_digest")
        if supplied_registry is not None:
            _require(
                isinstance(supplied_registry, str) and supplied_registry == registry_digest,
                "OPERATOR_REGISTRY_DIGEST_MISMATCH",
                str(supplied_registry),
            )

        return {
            "status": "VALID",
            "artifact": PACKET_ARTIFACT,
            "version": PACKET_VERSION,
            "standing": PACKET_STANDING,
            "packet_semantic_digest": digest,
            "operator_registry_digest": registry_digest,
            "canonical_semantics": semantic,
            "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
            "source_evidence": SOURCE_EVIDENCE,
            "implementation_witness": IMPLEMENTATION_WITNESS,
            "errors": [],
        }
    except PacketValidationError as exc:
        return {
            "status": "HOLD",
            "artifact": PACKET_ARTIFACT,
            "version": PACKET_VERSION,
            "standing": PACKET_STANDING,
            "packet_semantic_digest": None,
            "operator_registry_digest": None,
            "canonical_semantics": None,
            "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
            "source_evidence": SOURCE_EVIDENCE,
            "implementation_witness": IMPLEMENTATION_WITNESS,
            "errors": [{"code": exc.code, "detail": exc.detail}],
        }


def compile_connection_packet(packet: Any) -> Tuple[Dict[str, Any], Optional[SyntheticConnectionRuntime]]:
    """Translate a VALID packet into the existing synthetic control runtime.

    Packet standing is intentionally mapped *down* to the runtime's synthetic
    control standing and typed-loss declaration standing. No historical/source
    evidence is emitted by this translation.
    """

    validation = validate_connection_packet(packet)
    if validation["status"] != "VALID":
        return validation, None

    semantic = validation["canonical_semantics"]
    operators = []
    for source in semantic["operators"]:
        transforms = {
            feature: FeatureTransform(spec["op"], spec.get("operand"))
            for feature, spec in source["transforms"].items()
        }
        operators.append(
            EdgeOperator(
                edge_id=source["edge_id"],
                source_coordinate=source["source_coordinate"],
                target_coordinate=source["target_coordinate"],
                transforms=transforms,
                typed_loss=frozenset(source["typed_loss"]),
                loss_standing=VERIFIED_TYPED_LOSS,
                inverse_edge_id=source["inverse_edge_id"],
                provenance=tuple(source["provenance"]),
                standing=CONTROL_STANDING,
            )
        )

    runtime = SyntheticConnectionRuntime(semantic["feature_basis"], operators)
    if runtime.registry_errors:
        receipt = dict(validation)
        receipt["status"] = "HOLD"
        receipt["errors"] = [
            {"code": "RUNTIME_REGISTRY_REJECTED", "detail": error}
            for error in runtime.registry_errors
        ]
        return receipt, None

    receipt = dict(validation)
    receipt.update(
        {
            "runtime_translation": {
                "control_standing": CONTROL_STANDING,
                "typed_loss_standing": VERIFIED_TYPED_LOSS,
                "source_evidence": SOURCE_EVIDENCE,
                "historical_mapping_applied": False,
                "public_mcp_registration": False,
            }
        }
    )
    return receipt, runtime
