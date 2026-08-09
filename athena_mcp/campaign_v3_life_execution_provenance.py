"""Fail-closed execution provenance membrane for Campaign V3 Life.

Identity compatibility is not proof that semantic work occurred. This module
classifies the provenance of a Campaign Life execution-event identifier without
executing work, mutating Life state, or granting execution/reward/reseed authority.

No executor is trusted by default. A future executor may become recognized only by
an explicit code-reviewed registry change plus its own receipt validator/tests.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from .campaign_v3_life_attempt_identity import (
    validate_campaign_v3_life_attempt_identity,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.EXECUTION.PROVENANCE.V1"
RECEIPT_ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.EXECUTOR.RECEIPT.V1"

SUPPLIED_UNPROVEN = "SUPPLIED_UNPROVEN"
PROVENANCE_HOLD = "PROVENANCE_HOLD"
HOST_ATTESTED = "HOST_ATTESTED"

# Intentionally empty at V1. Adding an entry is a security/evidence change, not a
# configuration convenience. It requires a real executor integration and tests.
RECOGNIZED_EXECUTOR_PROFILES: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def provenance_digest(payload: Mapping[str, Any]) -> str:
    return _sha(payload)


def _base_result(*, execution_event_id: str, evidence_class: str, status: str) -> dict[str, Any]:
    out = {
        "artifact": ARTIFACT,
        "status": status,
        "execution_event_id": execution_event_id,
        "evidence_class": evidence_class,
        "semantic_execution_proven": False,
        "work_executed_by_this_module": False,
        "execution_authority": False,
        "reward_authority": False,
        "reseed_authority": False,
        "platform_counter_reset_claimed": False,
        "firewalls": [
            "SUPPLIED_EXECUTION_EVENT_ID != PROVEN_SEMANTIC_EXECUTION_ID",
            "REQUEST_RECEIPT != EXECUTION_RECEIPT",
            "TRANSPORT_RECEIPT != EXECUTION_EVIDENCE",
            "LEDGERED_EVENT != EXECUTION_EVIDENCE",
            "SELF_ASSERTED_HOST_ATTESTATION != RECOGNIZED_EXECUTOR_ATTESTATION",
            "EXECUTION_RECEIPT != EXECUTION_AUTHORITY",
            "RETRY_DELIVERY != NEW_PLAY",
        ],
    }
    return out


def classify_execution_provenance(
    *,
    execution_event_id: str,
    attempt_identity_envelope: Mapping[str, Any] | None = None,
    executor_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify evidence behind an execution-event identifier.

    V1 has no recognized executor profile. Consequently a plain identifier is
    `SUPPLIED_UNPROVEN`, and even a syntactically host-looking receipt cannot become
    `HOST_ATTESTED`. This is intentional fail-closed behavior.
    """
    event_id = str(execution_event_id or "").strip()
    if not event_id:
        return {
            **_base_result(execution_event_id="", evidence_class=PROVENANCE_HOLD, status="HOLD_EXECUTION_EVENT_ID_REQUIRED"),
            "errors": ["execution_event_id_required"],
        }

    if attempt_identity_envelope is not None:
        identity_errors = validate_campaign_v3_life_attempt_identity(attempt_identity_envelope)
        if identity_errors:
            return {
                **_base_result(execution_event_id=event_id, evidence_class=PROVENANCE_HOLD, status="HOLD_INVALID_ATTEMPT_IDENTITY"),
                "errors": list(identity_errors),
            }
        if str(attempt_identity_envelope.get("execution_event_id") or "") != event_id:
            return {
                **_base_result(execution_event_id=event_id, evidence_class=PROVENANCE_HOLD, status="HOLD_EXECUTION_EVENT_ID_MISMATCH"),
                "errors": ["execution_event_id_mismatch"],
            }

    if executor_receipt is None:
        basis = {
            "artifact": ARTIFACT,
            "execution_event_id": event_id,
            "evidence_class": SUPPLIED_UNPROVEN,
            "identity_envelope_digest": (
                attempt_identity_envelope.get("envelope_digest")
                if isinstance(attempt_identity_envelope, Mapping)
                else None
            ),
        }
        out = _base_result(
            execution_event_id=event_id,
            evidence_class=SUPPLIED_UNPROVEN,
            status="SUPPLIED_EXECUTION_EVENT_UNPROVEN",
        )
        out["provenance_digest"] = provenance_digest(basis)
        out["recognized_executor_profile"] = None
        return out

    if not isinstance(executor_receipt, Mapping):
        return {
            **_base_result(execution_event_id=event_id, evidence_class=PROVENANCE_HOLD, status="HOLD_INVALID_EXECUTOR_RECEIPT"),
            "errors": ["executor_receipt_not_object"],
        }

    receipt = deepcopy(dict(executor_receipt))
    errors: list[str] = []
    if receipt.get("artifact") != RECEIPT_ARTIFACT:
        errors.append("executor_receipt_artifact")
    executor_id = str(receipt.get("executor_id") or "").strip()
    if not executor_id:
        errors.append("executor_id_required")
    if str(receipt.get("execution_event_id") or "") != event_id:
        errors.append("executor_receipt_execution_event_id_mismatch")
    if receipt.get("work_executed") is not True:
        errors.append("work_executed_attestation_required")
    if receipt.get("observed_execution") is not True:
        errors.append("observed_execution_attestation_required")
    receipt_digest = str(receipt.get("receipt_digest") or "")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    if not receipt_digest or receipt_digest != _sha(unsigned):
        errors.append("executor_receipt_digest")

    profile = RECOGNIZED_EXECUTOR_PROFILES.get(executor_id)
    if profile is None:
        errors.append("unrecognized_executor_profile")

    if errors:
        out = _base_result(
            execution_event_id=event_id,
            evidence_class=PROVENANCE_HOLD,
            status="HOLD_UNPROVEN_EXECUTOR_ATTESTATION",
        )
        out["errors"] = errors
        out["recognized_executor_profile"] = executor_id if profile is not None else None
        out["receipt_digest"] = receipt_digest or None
        return out

    # This branch is unreachable in V1 because the recognized registry is empty.
    # It is present only to make the future promotion contract explicit.
    out = _base_result(
        execution_event_id=event_id,
        evidence_class=HOST_ATTESTED,
        status="HOST_EXECUTION_ATTESTED",
    )
    out["semantic_execution_proven"] = True
    out["recognized_executor_profile"] = executor_id
    out["receipt_digest"] = receipt_digest
    out["provenance_digest"] = provenance_digest(
        {
            "artifact": ARTIFACT,
            "execution_event_id": event_id,
            "executor_id": executor_id,
            "receipt_digest": receipt_digest,
            "profile": profile,
        }
    )
    return out


def make_untrusted_receipt_shape(
    *,
    executor_id: str,
    execution_event_id: str,
    evidence_ref: str,
) -> dict[str, Any]:
    """Test/integration helper that creates a self-consistent *untrusted* shape.

    Digest correctness is intentionally insufficient for recognition.
    """
    body = {
        "artifact": RECEIPT_ARTIFACT,
        "executor_id": str(executor_id),
        "execution_event_id": str(execution_event_id),
        "evidence_ref": str(evidence_ref),
        "work_executed": True,
        "observed_execution": True,
        "execution_authority": False,
        "reward_authority": False,
        "reseed_authority": False,
        "platform_counter_reset_claimed": False,
    }
    return {**body, "receipt_digest": _sha(body)}
