from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any, Dict, Optional

from .mythic_connection_packet import (
    COMPILER_REVISION,
    HISTORICAL_MAPPING_STATUS,
    IMPLEMENTATION_WITNESS,
    PACKET_ARTIFACT,
    PACKET_VERSION,
    SOURCE_EVIDENCE,
    compile_connection_packet,
    validate_connection_packet,
)
from .semantic_connection_control_v1 import (
    ARTIFACT as SEMANTIC_CONTROL_ARTIFACT,
    SemanticState,
)

RECEIPT_ARTIFACT = "ATHENA.MCK.CONNECTION.EVALUATION.RECEIPT.V1"
RECEIPT_VERSION = "MCK.CONNECTION.EVALUATION.RECEIPT.V1"
RECEIPT_REVISION = "SEMANTIC_CONTROL_FUSION_R1"
RECEIPT_STANDING = "SYNTHETIC_REPLAY_RECEIPT_NOT_EXTERNAL_IMPLEMENTATION_WITNESS"
REPLAY_STANDING = "REPLAY_MATCH_SYNTHETIC_CONTROL_ONLY"
HOLD_STANDING = "HOLD_NO_EXECUTION_RECEIPT"
SEMANTIC_STATE_STANDING = "SYNTHETIC_CONTROL"

STATE_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.STATE.V1"
PATH_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.PATH.V1"
SEMANTIC_RESULT_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.SEMANTIC_RESULT.V1"
RAW_RESULT_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.RAW_RESULT.V1"
RECEIPT_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.RECEIPT.V1"

SEMANTIC_RESULT_PROJECTION_BASIS = (
    "runtime_result minus executed_edges/audit/provenance; includes artifact, standing, "
    "classification, reason, initial/final public semantics, residue, residue_zero"
)

UNTRUSTED_IMPLEMENTATION_KEYS = frozenset(
    {
        "ci_status",
        "ci_run_id",
        "ci_run_number",
        "authority",
        "source_verified",
        "implementation_verified",
        "independent_witness",
        "repository_witness",
        "git_head",
        "repository",
    }
)

LAWS = (
    "PACKET_DIGEST != EVALUATION_RECEIPT",
    "OPERATOR_REGISTRY_DIGEST != PATH_EXECUTION_IDENTITY",
    "SELF_GENERATED_RECEIPT != REPOSITORY_CI_WITNESS",
    "REPLAY_MATCH != HISTORICAL_SOURCE_WITNESS",
    "CALLER_IMPLEMENTATION_CLAIM != EXTERNAL_IMPLEMENTATION_WITNESS",
    "UNKNOWN_RUNTIME_RESULT != ZERO_RESIDUE",
    "EXPECTED_CLASS != RECEIPT_INPUT",
    "AUDIT_TRACE_DIGEST != SEMANTIC_RESULT_DIGEST",
    "PATH_IDENTITY != SEMANTIC_RESIDUE",
    "DECLARED_TYPED_LOSS != EXECUTED_IRREVERSIBLE_LOSS",
)

_EMPTY_IMPLEMENTATION_BINDING = {
    "standing": IMPLEMENTATION_WITNESS,
    "repository": None,
    "git_head": None,
    "ci_workflow": None,
    "ci_run_id": None,
    "ci_run_number": None,
    "ci_conclusion": None,
}

_RAW_RESULT_KEYS = {
    "artifact",
    "standing",
    "classification",
    "reason",
    "initial_state",
    "final_state",
    "residue",
    "residue_zero",
    "executed_edges",
    "audit",
}

_RAW_STATE_KEYS = {
    "coordinate",
    "feature_basis",
    "values",
    "irreversible_loss",
    "standing",
    "provenance",
}


class EvaluationReceiptError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}" if detail else code)


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise EvaluationReceiptError(code, detail)


def _finite_json(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        _require(math.isfinite(value), "NONFINITE_JSON_NUMBER", path)
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _require(isinstance(key, str), "NONSTRING_JSON_KEY", f"{path}.{key}")
            _finite_json(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _finite_json(child, f"{path}[{index}]")
        return
    raise EvaluationReceiptError("NON_JSON_VALUE", path)


def _canonical_json(value: Any) -> str:
    _finite_json(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _clone_json(value: Any) -> Any:
    return json.loads(_canonical_json(value))


def _domain_digest(domain: str, value: Any) -> str:
    payload = _canonical_json(
        {"digest_domain": domain, "semantic_value": value}
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nonempty(value: Any, code: str, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), code, path)
    return value.strip()


def _normalize_string_list(
    value: Any,
    code: str,
    path: str,
    *,
    unique: bool = False,
) -> list[str]:
    _require(isinstance(value, list), code, path)
    out: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item = _nonempty(item, code, f"{path}[{index}]")
        if unique:
            _require(item not in seen, f"DUPLICATE_{code}", item)
            seen.add(item)
        out.append(item)
    return out


def _normalize_initial_state(
    value: Any,
    feature_basis: Sequence[str],
) -> Dict[str, Any]:
    _require(isinstance(value, Mapping), "INITIAL_STATE_NOT_OBJECT")
    allowed = {"coordinate", "values", "irreversible_loss", "provenance"}
    extra = set(value) - allowed
    _require(
        not extra,
        "UNKNOWN_INITIAL_STATE_FIELD",
        ",".join(sorted(map(str, extra))),
    )

    coordinate = _nonempty(
        value.get("coordinate"),
        "INVALID_INITIAL_COORDINATE",
        "$.initial_state.coordinate",
    )
    basis = [str(item) for item in feature_basis]
    _require(bool(basis), "EMPTY_PACKET_FEATURE_BASIS")
    _require(len(basis) == len(set(basis)), "DUPLICATE_PACKET_FEATURE_BASIS")
    _require(all(bool(item) for item in basis), "EMPTY_PACKET_FEATURE_ID")

    values = value.get("values")
    _require(isinstance(values, Mapping), "INITIAL_VALUES_NOT_OBJECT")
    _require(
        all(isinstance(key, str) and bool(key) for key in values),
        "INITIAL_VALUES_INVALID_KEY",
    )
    _require(
        set(values) == set(basis),
        "INITIAL_STATE_FEATURE_BASIS_MISMATCH",
    )
    canonical_values = _clone_json({key: values[key] for key in sorted(values)})

    irreversible_loss = _normalize_string_list(
        value.get("irreversible_loss", []),
        "INVALID_INITIAL_IRREVERSIBLE_LOSS",
        "$.initial_state.irreversible_loss",
        unique=True,
    )
    _require(
        set(irreversible_loss).issubset(set(basis)),
        "INITIAL_LOSS_FEATURE_OUTSIDE_BASIS",
    )
    provenance = _normalize_string_list(
        value.get("provenance", []),
        "INVALID_INITIAL_PROVENANCE",
        "$.initial_state.provenance",
    )

    return {
        "coordinate": coordinate,
        "feature_basis": list(basis),
        "values": canonical_values,
        "irreversible_loss": sorted(irreversible_loss),
        "standing": SEMANTIC_STATE_STANDING,
        "provenance": provenance,
    }


def _normalize_path(value: Any) -> list[str]:
    path = _normalize_string_list(
        value,
        "INVALID_ORDERED_PATH",
        "$.ordered_path",
    )
    _require(bool(path), "EMPTY_ORDERED_PATH")
    return path


def _normalize_replay_initial_state(
    value: Any,
    feature_basis: Sequence[str],
) -> Dict[str, Any]:
    """Validate the persisted receipt state before any replay dereference.

    Receipt replay is an adversarial verifier boundary. A caller may recompute the
    outer self-digest after changing fields, so self-consistency alone is not shape
    validity. The stored state must be the canonical state that E itself would emit.
    """

    _require(isinstance(value, Mapping), "RECEIPT_INITIAL_STATE_NOT_OBJECT")
    _require(
        set(value) == _RAW_STATE_KEYS,
        "RECEIPT_INITIAL_STATE_SCHEMA_DRIFT",
        ",".join(sorted(set(value) ^ _RAW_STATE_KEYS)),
    )
    expected_basis = [str(item) for item in feature_basis]
    stored_basis = _normalize_string_list(
        value.get("feature_basis"),
        "RECEIPT_INITIAL_FEATURE_BASIS",
        "$.receipt.initial_state.feature_basis",
        unique=True,
    )
    _require(
        stored_basis == expected_basis,
        "RECEIPT_INITIAL_FEATURE_BASIS_MISMATCH",
    )
    standing = _nonempty(
        value.get("standing"),
        "RECEIPT_INITIAL_STATE_STANDING",
        "$.receipt.initial_state.standing",
    )
    _require(
        standing == SEMANTIC_STATE_STANDING,
        "RECEIPT_INITIAL_STATE_STANDING_MISMATCH",
        standing,
    )
    normalized = _normalize_initial_state(
        {
            "coordinate": value.get("coordinate"),
            "values": value.get("values"),
            "irreversible_loss": value.get("irreversible_loss"),
            "provenance": value.get("provenance"),
        },
        expected_basis,
    )
    _require(
        normalized == _clone_json(dict(value)),
        "RECEIPT_INITIAL_STATE_CANONICAL_MISMATCH",
    )
    return normalized


def _semantic_state_projection(value: Any, path: str) -> Any:
    if value is None:
        return None
    _require(isinstance(value, Mapping), "RUNTIME_STATE_NOT_OBJECT", path)
    _require(
        set(value) == _RAW_STATE_KEYS,
        "RUNTIME_STATE_SCHEMA_DRIFT",
        path,
    )
    coordinate = _nonempty(value.get("coordinate"), "RUNTIME_STATE_COORDINATE", path)
    basis = _normalize_string_list(
        value.get("feature_basis"),
        "RUNTIME_STATE_FEATURE_BASIS",
        f"{path}.feature_basis",
        unique=True,
    )
    values = value.get("values")
    _require(isinstance(values, Mapping), "RUNTIME_STATE_VALUES", path)
    _require(set(values) == set(basis), "RUNTIME_STATE_FEATURE_BASIS_MISMATCH", path)
    irreversible_loss = _normalize_string_list(
        value.get("irreversible_loss"),
        "RUNTIME_STATE_IRREVERSIBLE_LOSS",
        f"{path}.irreversible_loss",
        unique=True,
    )
    _require(
        set(irreversible_loss).issubset(set(basis)),
        "RUNTIME_STATE_LOSS_OUTSIDE_BASIS",
        path,
    )
    standing = _nonempty(value.get("standing"), "RUNTIME_STATE_STANDING", path)
    _require(standing == SEMANTIC_STATE_STANDING, "RUNTIME_STATE_STANDING_DRIFT", standing)
    return {
        "coordinate": coordinate,
        "feature_basis": basis,
        "values": _clone_json(dict(values)),
        "irreversible_loss": sorted(irreversible_loss),
        "standing": standing,
    }


def _semantic_result_projection(raw_result: Any) -> Dict[str, Any]:
    _require(isinstance(raw_result, Mapping), "RUNTIME_RESULT_NOT_OBJECT")
    _require(
        set(raw_result) == _RAW_RESULT_KEYS,
        "RUNTIME_RESULT_SCHEMA_DRIFT",
        ",".join(sorted(set(raw_result) ^ _RAW_RESULT_KEYS)),
    )
    _require(
        raw_result.get("artifact") == SEMANTIC_CONTROL_ARTIFACT,
        "RUNTIME_RESULT_ARTIFACT_DRIFT",
        str(raw_result.get("artifact")),
    )
    standing = _nonempty(
        raw_result.get("standing"),
        "RUNTIME_RESULT_STANDING",
        "$.raw_result.standing",
    )
    classification = _nonempty(
        raw_result.get("classification"),
        "RUNTIME_RESULT_CLASSIFICATION",
        "$.raw_result.classification",
    )
    reason = _nonempty(
        raw_result.get("reason"),
        "RUNTIME_RESULT_REASON",
        "$.raw_result.reason",
    )
    residue = raw_result.get("residue")
    _require(
        residue is None or isinstance(residue, Mapping),
        "RUNTIME_RESULT_RESIDUE_SHAPE",
    )
    residue_zero = raw_result.get("residue_zero")
    _require(
        residue_zero is None or isinstance(residue_zero, bool),
        "RUNTIME_RESULT_RESIDUE_ZERO_SHAPE",
    )
    _require(
        isinstance(raw_result.get("executed_edges"), list),
        "RUNTIME_EXECUTED_EDGES_SHAPE",
    )
    _require(isinstance(raw_result.get("audit"), Mapping), "RUNTIME_AUDIT_SHAPE")
    _finite_json(raw_result, "$.raw_result")

    return {
        "artifact": SEMANTIC_CONTROL_ARTIFACT,
        "standing": standing,
        "classification": classification,
        "reason": reason,
        "initial_state": _semantic_state_projection(
            raw_result.get("initial_state"),
            "$.raw_result.initial_state",
        ),
        "final_state": _semantic_state_projection(
            raw_result.get("final_state"),
            "$.raw_result.final_state",
        ),
        "residue": _clone_json(residue) if residue is not None else None,
        "residue_zero": residue_zero,
    }


def _hold(
    code: str,
    detail: str = "",
    *,
    packet_errors: Optional[list[dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "status": "HOLD",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "revision": RECEIPT_REVISION,
        "standing": HOLD_STANDING,
        "evaluation_receipt_digest": None,
        "source_evidence": SOURCE_EVIDENCE,
        "implementation_witness": IMPLEMENTATION_WITNESS,
        "historical_mapping": {
            "status": HISTORICAL_MAPPING_STATUS,
            "edges": [],
        },
        "errors": (
            ([{"code": code, "detail": detail}] if code else [])
            + list(packet_errors or [])
        ),
        "laws": list(LAWS),
    }


def create_evaluation_receipt(
    packet: Any,
    initial_state: Any,
    ordered_path: Any,
    *,
    caller_claims: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute one validated synthetic connection packet and freeze replay identity.

    The receipt is deliberately self-generated mechanism evidence only. External
    Git/CI/source/authority attestation is a distinct successor artifact and cannot
    be embedded into this self-digested object.
    """

    if caller_claims:
        keys = sorted(str(key) for key in caller_claims)
        forbidden = sorted(set(keys) & set(UNTRUSTED_IMPLEMENTATION_KEYS))
        detail = ",".join(forbidden or keys)
        return _hold("UNTRUSTED_IMPLEMENTATION_CLAIM", detail)

    validation = validate_connection_packet(packet)
    if validation.get("status") != "VALID":
        return _hold(
            "INVALID_CONNECTION_PACKET",
            packet_errors=list(validation.get("errors") or []),
        )
    if validation.get("compiler_revision") != COMPILER_REVISION:
        return _hold(
            "PACKET_COMPILER_REVISION_DRIFT",
            str(validation.get("compiler_revision")),
        )

    try:
        semantic = validation["canonical_semantics"]
        state = _normalize_initial_state(initial_state, semantic["feature_basis"])
        path = _normalize_path(ordered_path)
    except EvaluationReceiptError as exc:
        return _hold(exc.code, exc.detail)
    except (TypeError, ValueError) as exc:
        return _hold("INITIAL_STATE_NORMALIZATION_ERROR", str(exc))

    compilation, runtime = compile_connection_packet(packet)
    if compilation.get("status") != "VALID" or runtime is None:
        return _hold(
            "CONNECTION_PACKET_COMPILE_HOLD",
            packet_errors=list(compilation.get("errors") or []),
        )

    try:
        semantic_state = SemanticState(
            coordinate=state["coordinate"],
            values=_clone_json(state["values"]),
            feature_basis=tuple(state["feature_basis"]),
            provenance=tuple(state["provenance"]),
            irreversible_loss=frozenset(state["irreversible_loss"]),
            standing=state["standing"],
        )
        raw_result = runtime.evaluate_closed_loop(semantic_state, path)
        raw_result = _clone_json(raw_result)
        semantic_result = _semantic_result_projection(raw_result)
    except EvaluationReceiptError as exc:
        return _hold(exc.code, exc.detail)
    except (TypeError, ValueError) as exc:
        return _hold("RUNTIME_EXECUTION_NORMALIZATION_ERROR", str(exc))

    initial_state_digest = _domain_digest(STATE_DIGEST_DOMAIN, state)
    ordered_path_digest = _domain_digest(PATH_DIGEST_DOMAIN, path)
    semantic_result_digest = _domain_digest(
        SEMANTIC_RESULT_DIGEST_DOMAIN,
        semantic_result,
    )
    raw_result_digest = _domain_digest(RAW_RESULT_DIGEST_DOMAIN, raw_result)

    receipt: Dict[str, Any] = {
        "status": "EVALUATED",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "revision": RECEIPT_REVISION,
        "standing": RECEIPT_STANDING,
        "packet_artifact": validation["artifact"],
        "packet_version": validation["version"],
        "packet_compiler_revision": validation["compiler_revision"],
        "packet_semantic_digest": validation["packet_semantic_digest"],
        "operator_registry_digest": validation["operator_registry_digest"],
        "semantic_control_artifact": SEMANTIC_CONTROL_ARTIFACT,
        "initial_state": state,
        "initial_state_digest": initial_state_digest,
        "ordered_path": list(path),
        "ordered_path_digest": ordered_path_digest,
        "raw_result": raw_result,
        "raw_result_digest": raw_result_digest,
        "semantic_result": semantic_result,
        "semantic_result_digest": semantic_result_digest,
        "semantic_result_projection_basis": SEMANTIC_RESULT_PROJECTION_BASIS,
        "source_evidence": SOURCE_EVIDENCE,
        "historical_mapping": {
            "status": HISTORICAL_MAPPING_STATUS,
            "edges": [],
        },
        "implementation_binding": copy.deepcopy(_EMPTY_IMPLEMENTATION_BINDING),
        "expected_class_used": False,
        "laws": list(LAWS),
    }
    receipt["evaluation_receipt_digest"] = _domain_digest(
        RECEIPT_DIGEST_DOMAIN,
        receipt,
    )
    return _clone_json(receipt)


def _receipt_digest_without_self(receipt: Mapping[str, Any]) -> str:
    payload = {
        key: _clone_json(value)
        for key, value in receipt.items()
        if key != "evaluation_receipt_digest"
    }
    return _domain_digest(RECEIPT_DIGEST_DOMAIN, payload)


def _receipt_static_contract_is_valid(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    if receipt.get("revision") != RECEIPT_REVISION:
        return False, "RECEIPT_REVISION_MISMATCH"
    if receipt.get("packet_artifact") != PACKET_ARTIFACT:
        return False, "RECEIPT_PACKET_ARTIFACT_MISMATCH"
    if receipt.get("packet_version") != PACKET_VERSION:
        return False, "RECEIPT_PACKET_VERSION_MISMATCH"
    if receipt.get("packet_compiler_revision") != COMPILER_REVISION:
        return False, "RECEIPT_PACKET_COMPILER_REVISION_MISMATCH"
    if receipt.get("semantic_control_artifact") != SEMANTIC_CONTROL_ARTIFACT:
        return False, "RECEIPT_SEMANTIC_CONTROL_ARTIFACT_MISMATCH"
    if receipt.get("source_evidence") != SOURCE_EVIDENCE:
        return False, "RECEIPT_SOURCE_EVIDENCE_MISMATCH"
    if receipt.get("historical_mapping") != {
        "status": HISTORICAL_MAPPING_STATUS,
        "edges": [],
    }:
        return False, "RECEIPT_HISTORICAL_MAPPING_MISMATCH"
    if receipt.get("implementation_binding") != _EMPTY_IMPLEMENTATION_BINDING:
        return False, "RECEIPT_IMPLEMENTATION_BINDING_INVALID"
    if receipt.get("expected_class_used") is not False:
        return False, "RECEIPT_EXPECTED_CLASS_USED_INVALID"
    if receipt.get("laws") != list(LAWS):
        return False, "RECEIPT_LAWS_MISMATCH"
    if receipt.get("semantic_result_projection_basis") != SEMANTIC_RESULT_PROJECTION_BASIS:
        return False, "RECEIPT_SEMANTIC_PROJECTION_BASIS_MISMATCH"
    return True, ""


def replay_evaluation_receipt(packet: Any, receipt: Any) -> Dict[str, Any]:
    """Re-execute a receipt and require exact state/path/semantic/audit identity."""

    if not isinstance(receipt, Mapping):
        return _hold("RECEIPT_NOT_OBJECT")
    if receipt.get("status") != "EVALUATED":
        return _hold("RECEIPT_NOT_EXECUTION")
    if receipt.get("artifact") != RECEIPT_ARTIFACT or receipt.get("version") != RECEIPT_VERSION:
        return _hold("RECEIPT_IDENTITY_MISMATCH")
    if receipt.get("standing") != RECEIPT_STANDING:
        return _hold("RECEIPT_STANDING_MISMATCH")

    static_ok, static_code = _receipt_static_contract_is_valid(receipt)
    if not static_ok:
        return _hold(static_code)

    supplied_digest = receipt.get("evaluation_receipt_digest")
    if not isinstance(supplied_digest, str) or len(supplied_digest) != 64:
        return _hold("INVALID_EVALUATION_RECEIPT_DIGEST")
    try:
        recomputed_self = _receipt_digest_without_self(receipt)
    except (EvaluationReceiptError, TypeError, ValueError) as exc:
        return _hold("RECEIPT_SELF_DIGEST_RECOMPUTE_ERROR", str(exc))
    if supplied_digest != recomputed_self:
        return _hold("EVALUATION_RECEIPT_SELF_DIGEST_MISMATCH")

    validation = validate_connection_packet(packet)
    if validation.get("status") != "VALID":
        return _hold(
            "REPLAY_PACKET_INVALID",
            packet_errors=list(validation.get("errors") or []),
        )
    if validation.get("compiler_revision") != COMPILER_REVISION:
        return _hold(
            "REPLAY_PACKET_COMPILER_REVISION_DRIFT",
            str(validation.get("compiler_revision")),
        )
    if receipt.get("packet_semantic_digest") != validation.get("packet_semantic_digest"):
        return _hold("REPLAY_PACKET_SEMANTIC_DIGEST_MISMATCH")
    if receipt.get("operator_registry_digest") != validation.get("operator_registry_digest"):
        return _hold("REPLAY_OPERATOR_REGISTRY_DIGEST_MISMATCH")

    try:
        stored_state = _normalize_replay_initial_state(
            receipt.get("initial_state"),
            validation["canonical_semantics"]["feature_basis"],
        )
        stored_path = _normalize_path(receipt.get("ordered_path"))
        stored_state_digest = _domain_digest(STATE_DIGEST_DOMAIN, stored_state)
        stored_path_digest = _domain_digest(PATH_DIGEST_DOMAIN, stored_path)
    except EvaluationReceiptError as exc:
        return _hold(exc.code, exc.detail)
    except (TypeError, ValueError, KeyError) as exc:
        return _hold("RECEIPT_REPLAY_INPUT_NORMALIZATION_ERROR", str(exc))

    if receipt.get("initial_state_digest") != stored_state_digest:
        return _hold("RECEIPT_INITIAL_STATE_DIGEST_MISMATCH")
    if receipt.get("ordered_path_digest") != stored_path_digest:
        return _hold("RECEIPT_ORDERED_PATH_DIGEST_MISMATCH")

    regenerated = create_evaluation_receipt(
        packet,
        {
            "coordinate": stored_state["coordinate"],
            "values": copy.deepcopy(stored_state["values"]),
            "irreversible_loss": copy.deepcopy(stored_state["irreversible_loss"]),
            "provenance": copy.deepcopy(stored_state["provenance"]),
        },
        copy.deepcopy(stored_path),
    )
    if regenerated.get("status") != "EVALUATED":
        return _hold(
            "REPLAY_REEXECUTION_HOLD",
            packet_errors=list(regenerated.get("errors") or []),
        )

    checks = {
        "initial_state_digest": regenerated["initial_state_digest"]
        == receipt.get("initial_state_digest"),
        "ordered_path_digest": regenerated["ordered_path_digest"]
        == receipt.get("ordered_path_digest"),
        "semantic_result_digest": regenerated["semantic_result_digest"]
        == receipt.get("semantic_result_digest"),
        "raw_result_digest": regenerated["raw_result_digest"]
        == receipt.get("raw_result_digest"),
        "evaluation_receipt_digest": regenerated["evaluation_receipt_digest"]
        == supplied_digest,
        "raw_result": regenerated["raw_result"] == receipt.get("raw_result"),
        "semantic_result": regenerated["semantic_result"]
        == receipt.get("semantic_result"),
    }
    if not all(checks.values()):
        return {
            **_hold("REPLAY_MISMATCH"),
            "checks": checks,
            "regenerated_evaluation_receipt_digest": regenerated.get(
                "evaluation_receipt_digest"
            ),
        }

    return {
        "status": "REPLAY_MATCH",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "revision": RECEIPT_REVISION,
        "standing": REPLAY_STANDING,
        "evaluation_receipt_digest": supplied_digest,
        "checks": checks,
        "source_evidence": SOURCE_EVIDENCE,
        "implementation_witness": IMPLEMENTATION_WITNESS,
        "historical_mapping": {
            "status": HISTORICAL_MAPPING_STATUS,
            "edges": [],
        },
        "authority_delta": "NONE",
        "laws": list(LAWS),
    }
