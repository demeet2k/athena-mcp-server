from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from athena_mcp.mythic_connection_packet import (
    COMPILER_REVISION as PACKET_COMPILER_REVISION,
    SOURCE_EVIDENCE,
    compile_connection_packet,
)
from athena_mcp.semantic_connection_control_v1 import (
    ARTIFACT as SEMANTIC_CONTROL_ARTIFACT,
    SemanticState,
)

ARTIFACT = "ATHENA.MCK.EVALUATION.RECEIPT.V1"
VERSION = "MCK.EVALUATION.RECEIPT.V1"
REPLAY_ARTIFACT = "ATHENA.MCK.EVALUATION.REPLAY.V1"
REPLAY_VERSION = "MCK.EVALUATION.REPLAY.V1"
RECEIPT_STANDING = "SYNTHETIC_REPLAY_RECEIPT_NOT_SOURCE_EVIDENCE"
EVIDENCE_STANDING = "REPOSITORY_EXECUTED_SYNTHETIC_CONTROL"
HISTORICAL_MAPPING = "HOLD_EMPTY_V1_PROPOSAL"
AUTHORITY_DELTA = "NONE"
INDEPENDENT_WITNESS = False
CI_QUALIFICATION = "NOT_INFERRED_BY_RECEIPT"
RECEIPT_DIGEST_DOMAIN = "MCK.EVALUATION.RECEIPT.V1"
INPUT_DIGEST_DOMAIN = "MCK.EVALUATION.INPUT.V1"
RESULT_DIGEST_DOMAIN = "MCK.EVALUATION.RAW_RESULT.V1"

_RESERVED_CALLER_TRUST_KEYS = frozenset(
    {
        "ci_status",
        "ci_pass",
        "qualified",
        "qualification",
        "authority",
        "authority_delta",
        "source_verified",
        "source_evidence",
        "independent_witness",
        "promotion",
        "promoted",
        "expected_class",
        "expected",
        "expected_label",
        "answer_key",
        "oracle",
        "oracle_label",
        "benchmark_label",
        "game_score",
        "reward",
        "rarity",
    }
)

_REQUIRED_RECEIPT_KEYS = frozenset(
    {
        "artifact",
        "version",
        "status",
        "receipt_id",
        "receipt_standing",
        "evidence_standing",
        "source_evidence",
        "historical_mapping",
        "independent_witness",
        "authority_delta",
        "ci_qualification",
        "semantic_control_artifact",
        "packet_compiler_revision",
        "packet_semantic_digest",
        "operator_registry_digest",
        "initial_state",
        "edge_path",
        "evaluation_input_digest",
        "raw_result",
        "raw_result_digest",
        "receipt_digest",
    }
)


def _strict_copy(value: Any) -> Any:
    return json.loads(
        json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _domain_digest(domain: str, value: Any) -> str:
    payload = {"digest_domain": domain, "value": value}
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _contains_reserved_caller_key(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in _RESERVED_CALLER_TRUST_KEYS:
                return normalized
            nested = _contains_reserved_caller_key(child)
            if nested is not None:
                return nested
        return None
    if isinstance(value, (list, tuple)):
        for child in value:
            nested = _contains_reserved_caller_key(child)
            if nested is not None:
                return nested
    return None


def _hold(reason: str, *, packet_validation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "HOLD",
        "reason": reason,
        "receipt_id": None,
        "receipt_standing": RECEIPT_STANDING,
        "evidence_standing": EVIDENCE_STANDING,
        "source_evidence": SOURCE_EVIDENCE,
        "historical_mapping": HISTORICAL_MAPPING,
        "independent_witness": INDEPENDENT_WITNESS,
        "authority_delta": AUTHORITY_DELTA,
        "ci_qualification": CI_QUALIFICATION,
        "execution_identity": None,
        "packet_validation": _strict_copy(dict(packet_validation or {})),
    }


def _normalize_path(edge_path: Sequence[str]) -> list[str]:
    if isinstance(edge_path, (str, bytes)):
        raise ValueError("edge_path must be a sequence of edge IDs")
    path: list[str] = []
    for index, edge_id in enumerate(edge_path):
        if not isinstance(edge_id, str) or not edge_id.strip():
            raise ValueError(f"edge_path[{index}] must be a non-empty string")
        path.append(edge_id.strip())
    return path


def _evaluation_input_payload(
    *,
    packet_semantic_digest: str,
    operator_registry_digest: str,
    initial_state: Mapping[str, Any],
    edge_path: Sequence[str],
) -> dict[str, Any]:
    return {
        "packet_semantic_digest": packet_semantic_digest,
        "operator_registry_digest": operator_registry_digest,
        "semantic_control_artifact": SEMANTIC_CONTROL_ARTIFACT,
        "packet_compiler_revision": PACKET_COMPILER_REVISION,
        "initial_state": _strict_copy(dict(initial_state)),
        "edge_path": list(edge_path),
    }


def _receipt_identity_payload(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact": receipt["artifact"],
        "version": receipt["version"],
        "receipt_standing": receipt["receipt_standing"],
        "evidence_standing": receipt["evidence_standing"],
        "source_evidence": receipt["source_evidence"],
        "historical_mapping": receipt["historical_mapping"],
        "independent_witness": receipt["independent_witness"],
        "authority_delta": receipt["authority_delta"],
        "ci_qualification": receipt["ci_qualification"],
        "semantic_control_artifact": receipt["semantic_control_artifact"],
        "packet_compiler_revision": receipt["packet_compiler_revision"],
        "packet_semantic_digest": receipt["packet_semantic_digest"],
        "operator_registry_digest": receipt["operator_registry_digest"],
        "evaluation_input_digest": receipt["evaluation_input_digest"],
        "raw_result_digest": receipt["raw_result_digest"],
    }


def build_evaluation_receipt(
    packet: Mapping[str, Any],
    initial_state: SemanticState,
    edge_path: Sequence[str],
    *,
    caller_claims: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute one packet-defined route and freeze a deterministic replay receipt.

    Caller trust claims are not admitted into V1. Repository CI, source standing,
    independent witness, authority, benchmark labels, game metadata, or promotion
    state must be bound by a separate evidence surface rather than self-minted by
    this receipt constructor.
    """

    if caller_claims:
        reserved = _contains_reserved_caller_key(caller_claims)
        if reserved is not None:
            return _hold(f"CALLER_TRUST_CLAIM_FORBIDDEN:{reserved}")
        return _hold("CALLER_CONTEXT_NOT_ADMITTED_V1")

    if not isinstance(initial_state, SemanticState):
        return _hold("INITIAL_STATE_MUST_BE_SEMANTIC_STATE")

    try:
        path = _normalize_path(edge_path)
        initial_audit = _strict_copy(initial_state.audit_view())
    except (TypeError, ValueError) as exc:
        return _hold(f"INVALID_EVALUATION_INPUT:{type(exc).__name__}:{exc}")

    packet_validation, compiled = compile_connection_packet(packet)
    if compiled is None or packet_validation.get("status") != "VALID":
        return _hold("PACKET_VALIDATION_HOLD", packet_validation=packet_validation)

    input_payload = _evaluation_input_payload(
        packet_semantic_digest=packet_validation["packet_semantic_digest"],
        operator_registry_digest=packet_validation["operator_registry_digest"],
        initial_state=initial_audit,
        edge_path=path,
    )
    evaluation_input_digest = _domain_digest(INPUT_DIGEST_DOMAIN, input_payload)

    raw_result = _strict_copy(compiled.evaluate_closed_loop(initial_state, path))
    raw_result_digest = _domain_digest(RESULT_DIGEST_DOMAIN, raw_result)

    receipt: dict[str, Any] = {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "RECORDED",
        "receipt_id": "",
        "receipt_standing": RECEIPT_STANDING,
        "evidence_standing": EVIDENCE_STANDING,
        "source_evidence": SOURCE_EVIDENCE,
        "historical_mapping": HISTORICAL_MAPPING,
        "independent_witness": INDEPENDENT_WITNESS,
        "authority_delta": AUTHORITY_DELTA,
        "ci_qualification": CI_QUALIFICATION,
        "semantic_control_artifact": SEMANTIC_CONTROL_ARTIFACT,
        "packet_compiler_revision": PACKET_COMPILER_REVISION,
        "packet_semantic_digest": packet_validation["packet_semantic_digest"],
        "operator_registry_digest": packet_validation["operator_registry_digest"],
        "initial_state": input_payload["initial_state"],
        "edge_path": path,
        "evaluation_input_digest": evaluation_input_digest,
        "raw_result": raw_result,
        "raw_result_digest": raw_result_digest,
        "receipt_digest": "",
    }
    receipt_digest = _domain_digest(
        RECEIPT_DIGEST_DOMAIN, _receipt_identity_payload(receipt)
    )
    receipt["receipt_digest"] = receipt_digest
    receipt["receipt_id"] = f"MCK-EVAL-{receipt_digest[:24]}"
    return _strict_copy(receipt)


def validate_evaluation_receipt(receipt: Any) -> dict[str, Any]:
    try:
        if not isinstance(receipt, Mapping):
            raise ValueError("RECEIPT_NOT_OBJECT")
        if set(receipt) != set(_REQUIRED_RECEIPT_KEYS):
            missing = sorted(_REQUIRED_RECEIPT_KEYS - set(receipt))
            extra = sorted(set(receipt) - _REQUIRED_RECEIPT_KEYS)
            raise ValueError(f"RECEIPT_SHAPE_MISMATCH:missing={missing}:extra={extra}")

        strict = _strict_copy(dict(receipt))
        if strict["artifact"] != ARTIFACT or strict["version"] != VERSION:
            raise ValueError("RECEIPT_IDENTITY_MISMATCH")
        if strict["status"] != "RECORDED":
            raise ValueError("RECEIPT_STATUS_INVALID")
        if strict["receipt_standing"] != RECEIPT_STANDING:
            raise ValueError("RECEIPT_STANDING_INVALID")
        if strict["evidence_standing"] != EVIDENCE_STANDING:
            raise ValueError("EVIDENCE_STANDING_INVALID")
        if strict["source_evidence"] != SOURCE_EVIDENCE:
            raise ValueError("SOURCE_EVIDENCE_INVALID")
        if strict["historical_mapping"] != HISTORICAL_MAPPING:
            raise ValueError("HISTORICAL_MAPPING_INVALID")
        if strict["independent_witness"] is not False:
            raise ValueError("INDEPENDENT_WITNESS_MUST_BE_FALSE")
        if strict["authority_delta"] != AUTHORITY_DELTA:
            raise ValueError("AUTHORITY_DELTA_INVALID")
        if strict["ci_qualification"] != CI_QUALIFICATION:
            raise ValueError("CI_QUALIFICATION_SELF_MINT_FORBIDDEN")
        if strict["semantic_control_artifact"] != SEMANTIC_CONTROL_ARTIFACT:
            raise ValueError("SEMANTIC_CONTROL_ARTIFACT_MISMATCH")
        if strict["packet_compiler_revision"] != PACKET_COMPILER_REVISION:
            raise ValueError("PACKET_COMPILER_REVISION_MISMATCH")

        normalized_path = _normalize_path(strict["edge_path"])
        input_payload = _evaluation_input_payload(
            packet_semantic_digest=strict["packet_semantic_digest"],
            operator_registry_digest=strict["operator_registry_digest"],
            initial_state=strict["initial_state"],
            edge_path=normalized_path,
        )
        expected_input_digest = _domain_digest(INPUT_DIGEST_DOMAIN, input_payload)
        if strict["evaluation_input_digest"] != expected_input_digest:
            raise ValueError("EVALUATION_INPUT_DIGEST_MISMATCH")

        expected_raw_digest = _domain_digest(
            RESULT_DIGEST_DOMAIN, strict["raw_result"]
        )
        if strict["raw_result_digest"] != expected_raw_digest:
            raise ValueError("RAW_RESULT_DIGEST_MISMATCH")

        expected_receipt_digest = _domain_digest(
            RECEIPT_DIGEST_DOMAIN, _receipt_identity_payload(strict)
        )
        if strict["receipt_digest"] != expected_receipt_digest:
            raise ValueError("RECEIPT_DIGEST_MISMATCH")
        if strict["receipt_id"] != f"MCK-EVAL-{expected_receipt_digest[:24]}":
            raise ValueError("RECEIPT_ID_MISMATCH")

        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "VALID",
            "receipt_id": strict["receipt_id"],
            "receipt_digest": strict["receipt_digest"],
            "errors": [],
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "HOLD",
            "receipt_id": None,
            "receipt_digest": None,
            "errors": [f"{type(exc).__name__}:{exc}"],
        }


def replay_evaluation_receipt(
    stored_receipt: Mapping[str, Any],
    packet: Mapping[str, Any],
    initial_state: SemanticState,
    edge_path: Sequence[str],
) -> dict[str, Any]:
    stored_validation = validate_evaluation_receipt(stored_receipt)
    if stored_validation["status"] != "VALID":
        return {
            "artifact": REPLAY_ARTIFACT,
            "version": REPLAY_VERSION,
            "status": "HOLD",
            "reason": "STORED_RECEIPT_INVALID",
            "stored_validation": stored_validation,
            "mismatches": [],
        }

    replay = build_evaluation_receipt(packet, initial_state, edge_path)
    if replay.get("status") != "RECORDED":
        return {
            "artifact": REPLAY_ARTIFACT,
            "version": REPLAY_VERSION,
            "status": "HOLD",
            "reason": "REPLAY_EXECUTION_HOLD",
            "replay_hold": replay,
            "mismatches": [],
        }

    comparison_fields = (
        "packet_semantic_digest",
        "operator_registry_digest",
        "semantic_control_artifact",
        "packet_compiler_revision",
        "evaluation_input_digest",
        "raw_result_digest",
        "receipt_digest",
    )
    mismatches = [
        field_name
        for field_name in comparison_fields
        if stored_receipt.get(field_name) != replay.get(field_name)
    ]
    if _strict_copy(stored_receipt.get("raw_result")) != replay.get("raw_result"):
        mismatches.append("raw_result")

    return {
        "artifact": REPLAY_ARTIFACT,
        "version": REPLAY_VERSION,
        "status": "MATCH" if not mismatches else "MISMATCH",
        "reason": "EXACT_REPLAY_MATCH" if not mismatches else "REPLAY_IDENTITY_CHANGED",
        "stored_receipt_id": stored_receipt["receipt_id"],
        "replay_receipt_id": replay["receipt_id"],
        "mismatches": sorted(set(mismatches)),
        "source_evidence": SOURCE_EVIDENCE,
        "independent_witness": False,
        "authority_delta": AUTHORITY_DELTA,
    }
