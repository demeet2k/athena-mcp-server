from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any, Dict, Optional

from .mythic_connection_control import CONNECTION_VERSION, TransportState
from .mythic_connection_packet import (
    HISTORICAL_MAPPING_STATUS,
    IMPLEMENTATION_WITNESS,
    SOURCE_EVIDENCE,
    compile_connection_packet,
    validate_connection_packet,
)

RECEIPT_ARTIFACT = "ATHENA.MCK.CONNECTION.EVALUATION.RECEIPT.V1"
RECEIPT_VERSION = "MCK.CONNECTION.EVALUATION.RECEIPT.V1"
RECEIPT_STANDING = "SYNTHETIC_REPLAY_RECEIPT_NOT_EXTERNAL_IMPLEMENTATION_WITNESS"
REPLAY_STANDING = "REPLAY_MATCH_SYNTHETIC_CONTROL_ONLY"
HOLD_STANDING = "HOLD_NO_EXECUTION_RECEIPT"

STATE_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.STATE.V1"
PATH_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.PATH.V1"
RESULT_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.RESULT.V1"
RECEIPT_DIGEST_DOMAIN = "MCK.CONNECTION.EVALUATION.RECEIPT.V1"

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
)


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
    if isinstance(value, list):
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


def _domain_digest(domain: str, value: Any) -> str:
    payload = _canonical_json({"digest_domain": domain, "semantic_value": value}).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nonempty(value: Any, code: str, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), code, path)
    return value.strip()


def _normalize_string_list(value: Any, code: str, path: str, *, unique: bool = False) -> list[str]:
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


def _normalize_initial_state(value: Any, feature_basis: Sequence[str]) -> Dict[str, Any]:
    _require(isinstance(value, Mapping), "INITIAL_STATE_NOT_OBJECT")
    allowed = {"coordinate", "values", "irreversible_loss", "provenance"}
    extra = set(value) - allowed
    _require(not extra, "UNKNOWN_INITIAL_STATE_FIELD", ",".join(sorted(map(str, extra))))

    coordinate = _nonempty(value.get("coordinate"), "INVALID_INITIAL_COORDINATE", "$.initial_state.coordinate")
    values = value.get("values")
    _require(isinstance(values, Mapping), "INITIAL_VALUES_NOT_OBJECT")
    _require(all(isinstance(key, str) for key in values), "INITIAL_VALUES_NONSTRING_KEY")
    _require(set(values) == set(feature_basis), "INITIAL_STATE_FEATURE_BASIS_MISMATCH")
    canonical_values = {key: copy.deepcopy(values[key]) for key in sorted(values)}
    _finite_json(canonical_values, "$.initial_state.values")

    irreversible_loss = _normalize_string_list(
        value.get("irreversible_loss", []),
        "INVALID_INITIAL_IRREVERSIBLE_LOSS",
        "$.initial_state.irreversible_loss",
        unique=True,
    )
    _require(
        set(irreversible_loss).issubset(set(feature_basis)),
        "INITIAL_LOSS_FEATURE_OUTSIDE_BASIS",
    )
    provenance = _normalize_string_list(
        value.get("provenance", []),
        "INVALID_INITIAL_PROVENANCE",
        "$.initial_state.provenance",
    )

    return {
        "coordinate": coordinate,
        "values": canonical_values,
        "irreversible_loss": sorted(irreversible_loss),
        "provenance": provenance,
    }


def _normalize_path(value: Any) -> list[str]:
    path = _normalize_string_list(value, "INVALID_ORDERED_PATH", "$.ordered_path")
    _require(bool(path), "EMPTY_ORDERED_PATH")
    return path


def _hold(code: str, detail: str = "", *, packet_errors: Optional[list[dict[str, Any]]] = None) -> Dict[str, Any]:
    return {
        "status": "HOLD",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "standing": HOLD_STANDING,
        "evaluation_receipt_digest": None,
        "source_evidence": SOURCE_EVIDENCE,
        "implementation_witness": IMPLEMENTATION_WITNESS,
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "errors": ([{"code": code, "detail": detail}] if code else []) + list(packet_errors or []),
        "laws": list(LAWS),
    }


def create_evaluation_receipt(
    packet: Any,
    initial_state: Any,
    ordered_path: Any,
    *,
    caller_claims: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute one validated synthetic connection packet and freeze a replay receipt.

    This is an execution-identity receipt only. It deliberately cannot self-bind a
    Git head, CI run, authority, historical source standing, or independent witness.
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

    try:
        semantic = validation["canonical_semantics"]
        state = _normalize_initial_state(initial_state, semantic["feature_basis"])
        path = _normalize_path(ordered_path)
    except EvaluationReceiptError as exc:
        return _hold(exc.code, exc.detail)

    compilation, runtime = compile_connection_packet(packet)
    if compilation.get("status") != "VALID" or runtime is None:
        return _hold(
            "CONNECTION_PACKET_COMPILE_HOLD",
            packet_errors=list(compilation.get("errors") or []),
        )

    transport = TransportState(
        coordinate=state["coordinate"],
        values=copy.deepcopy(state["values"]),
        irreversible_loss=set(state["irreversible_loss"]),
        provenance=list(state["provenance"]),
    )
    raw_result = runtime.evaluate_closed_loop(transport, path)
    raw_result = copy.deepcopy(raw_result)
    _finite_json(raw_result, "$.raw_result")

    initial_state_digest = _domain_digest(STATE_DIGEST_DOMAIN, state)
    ordered_path_digest = _domain_digest(PATH_DIGEST_DOMAIN, path)
    result_semantic_digest = _domain_digest(RESULT_DIGEST_DOMAIN, raw_result)

    receipt: Dict[str, Any] = {
        "status": "EVALUATED",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "standing": RECEIPT_STANDING,
        "packet_artifact": validation["artifact"],
        "packet_version": validation["version"],
        "packet_semantic_digest": validation["packet_semantic_digest"],
        "operator_registry_digest": validation["operator_registry_digest"],
        "runtime_contract_version": CONNECTION_VERSION,
        "initial_state": state,
        "initial_state_digest": initial_state_digest,
        "ordered_path": path,
        "ordered_path_digest": ordered_path_digest,
        "raw_result": raw_result,
        "result_semantic_digest": result_semantic_digest,
        "source_evidence": SOURCE_EVIDENCE,
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "implementation_binding": {
            "standing": IMPLEMENTATION_WITNESS,
            "repository": None,
            "git_head": None,
            "ci_workflow": None,
            "ci_run_id": None,
            "ci_run_number": None,
            "ci_conclusion": None,
        },
        "expected_class_used": False,
        "laws": list(LAWS),
    }
    receipt["evaluation_receipt_digest"] = _domain_digest(RECEIPT_DIGEST_DOMAIN, receipt)
    return copy.deepcopy(receipt)


def _receipt_digest_without_self(receipt: Mapping[str, Any]) -> str:
    payload = {key: copy.deepcopy(value) for key, value in receipt.items() if key != "evaluation_receipt_digest"}
    return _domain_digest(RECEIPT_DIGEST_DOMAIN, payload)


def replay_evaluation_receipt(packet: Any, receipt: Any) -> Dict[str, Any]:
    """Replay a receipt against a supplied packet and compare exact execution identity."""

    if not isinstance(receipt, Mapping):
        return _hold("RECEIPT_NOT_OBJECT")
    if receipt.get("status") != "EVALUATED":
        return _hold("RECEIPT_NOT_EXECUTION")
    if receipt.get("artifact") != RECEIPT_ARTIFACT or receipt.get("version") != RECEIPT_VERSION:
        return _hold("RECEIPT_IDENTITY_MISMATCH")
    if receipt.get("standing") != RECEIPT_STANDING:
        return _hold("RECEIPT_STANDING_MISMATCH")

    supplied_digest = receipt.get("evaluation_receipt_digest")
    if not isinstance(supplied_digest, str) or len(supplied_digest) != 64:
        return _hold("INVALID_EVALUATION_RECEIPT_DIGEST")
    try:
        recomputed_self = _receipt_digest_without_self(receipt)
    except EvaluationReceiptError as exc:
        return _hold(exc.code, exc.detail)
    if supplied_digest != recomputed_self:
        return _hold("EVALUATION_RECEIPT_SELF_DIGEST_MISMATCH")

    validation = validate_connection_packet(packet)
    if validation.get("status") != "VALID":
        return _hold("REPLAY_PACKET_INVALID", packet_errors=list(validation.get("errors") or []))
    if receipt.get("packet_semantic_digest") != validation.get("packet_semantic_digest"):
        return _hold("REPLAY_PACKET_SEMANTIC_DIGEST_MISMATCH")
    if receipt.get("operator_registry_digest") != validation.get("operator_registry_digest"):
        return _hold("REPLAY_OPERATOR_REGISTRY_DIGEST_MISMATCH")

    regenerated = create_evaluation_receipt(
        packet,
        copy.deepcopy(receipt.get("initial_state")),
        copy.deepcopy(receipt.get("ordered_path")),
    )
    if regenerated.get("status") != "EVALUATED":
        return _hold("REPLAY_REEXECUTION_HOLD", packet_errors=list(regenerated.get("errors") or []))

    checks = {
        "initial_state_digest": regenerated["initial_state_digest"] == receipt.get("initial_state_digest"),
        "ordered_path_digest": regenerated["ordered_path_digest"] == receipt.get("ordered_path_digest"),
        "result_semantic_digest": regenerated["result_semantic_digest"] == receipt.get("result_semantic_digest"),
        "evaluation_receipt_digest": regenerated["evaluation_receipt_digest"] == supplied_digest,
        "raw_result": regenerated["raw_result"] == receipt.get("raw_result"),
    }
    if not all(checks.values()):
        return {
            **_hold("REPLAY_MISMATCH"),
            "checks": checks,
            "regenerated_evaluation_receipt_digest": regenerated.get("evaluation_receipt_digest"),
        }

    return {
        "status": "REPLAY_MATCH",
        "artifact": RECEIPT_ARTIFACT,
        "version": RECEIPT_VERSION,
        "standing": REPLAY_STANDING,
        "evaluation_receipt_digest": supplied_digest,
        "checks": checks,
        "source_evidence": SOURCE_EVIDENCE,
        "implementation_witness": IMPLEMENTATION_WITNESS,
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "authority_delta": "NONE",
        "laws": list(LAWS),
    }
