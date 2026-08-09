from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .campaign_v3_binding import ARTIFACT as BINDING_ARTIFACT
from .campaign_v3_life_binding import (
    ARTIFACT as LIFE_PACKET_ARTIFACT,
    validate_campaign_v3_life_quest_packet,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.BOUND.IDENTITY.V1"

_REQUIRED_BOUND_LAWS = {
    "PULSE_DIGEST_VERIFIED_BEFORE_LEASE",
    "BOUND_RECEIPT_RETAINS_VERIFIED_PULSE_DIGEST",
    "CAMPAIGN_BINDING != WORK_EXECUTION",
    "BOUND_LOOP != OBSERVED_SUCCESS",
}
_OUTPUT_KEYS = {
    "artifact",
    "status",
    "failures",
    "identity",
    "bound_receipt_digest",
    "life_packet_digest",
    "structural_alignment",
    "receipt_provenance_proven",
    "execution_authority",
    "work_executed",
    "life_dispatch_executed",
    "platform_counter_reset_claimed",
    "laws",
    "alignment_digest",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _validate_bound_receipt(bound_receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if bound_receipt.get("artifact") != BINDING_ARTIFACT:
        errors.append("bound_artifact")
    if bound_receipt.get("status") != "BOUND":
        errors.append("bound_status")
    if bound_receipt.get("standing") != "BOUND_LOOP_NOT_WORK_EXECUTED":
        errors.append("bound_standing")
    if bound_receipt.get("execution_authority_granted") is not False:
        errors.append("bound_execution_authority_must_be_false")
    if bound_receipt.get("work_executed") is not False:
        errors.append("bound_work_executed_must_be_false")
    if bound_receipt.get("failures") != []:
        errors.append("bound_failures_must_be_empty")
    if bound_receipt.get("holds") != []:
        errors.append("bound_holds_must_be_empty")
    if not _text(bound_receipt.get("task")):
        errors.append("bound_task_required")
    if bound_receipt.get("next") != "RESUME_EXPLICIT_LOOP_AND_EXECUTE_ONE_LAWFUL_CYCLE":
        errors.append("bound_next")

    for key in ("campaign_id", "branch_id", "pulse_digest", "loop_id"):
        if not _text(bound_receipt.get(key)):
            errors.append(f"bound_{key}_required")
    if _positive_int(bound_receipt.get("residual_step")) is None:
        errors.append("bound_residual_step")

    laws = bound_receipt.get("laws")
    if not isinstance(laws, list):
        errors.append("bound_laws")
    else:
        normalized = {_text(value) for value in laws if _text(value)}
        missing = sorted(_REQUIRED_BOUND_LAWS - normalized)
        errors.extend(f"bound_law_missing:{law}" for law in missing)

    for key in (
        "loop_state_digest",
        "campaign_state_digest",
        "pre_lease_head",
        "post_lease_head",
        "post_loop_start_head",
        "post_bind_head",
    ):
        if not _text(bound_receipt.get(key)):
            errors.append(f"bound_{key}_required")

    pre_lease = _text(bound_receipt.get("pre_lease_head"))
    post_lease = _text(bound_receipt.get("post_lease_head"))
    post_loop = _text(bound_receipt.get("post_loop_start_head"))
    post_bind = _text(bound_receipt.get("post_bind_head"))
    if pre_lease and post_lease and pre_lease == post_lease:
        errors.append("bound_lease_head_not_advanced")
    if post_loop and post_bind and post_loop == post_bind:
        errors.append("bound_bind_head_not_advanced")

    return errors


def _identity_from_bound(bound_receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": _text(bound_receipt.get("campaign_id")),
        "branch_id": _text(bound_receipt.get("branch_id")),
        "residual_step": _positive_int(bound_receipt.get("residual_step")),
        "pulse_digest": _text(bound_receipt.get("pulse_digest")),
        "loop_id": _text(bound_receipt.get("loop_id")),
    }


def _hold(
    *,
    status: str,
    failures: list[str],
    bound_receipt: Mapping[str, Any] | None,
    life_packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    result = {
        "artifact": ARTIFACT,
        "status": status,
        "failures": list(failures),
        "identity": None,
        "bound_receipt_digest": _sha(bound_receipt) if isinstance(bound_receipt, Mapping) else None,
        "life_packet_digest": (
            _text(life_packet.get("packet_digest")) if isinstance(life_packet, Mapping) else None
        ),
        "structural_alignment": False,
        "receipt_provenance_proven": False,
        "execution_authority": False,
        "work_executed": False,
        "life_dispatch_executed": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "STRUCTURAL_ALIGNMENT != RECEIPT_PROVENANCE",
            "IDENTITY_ALIGNMENT != EXECUTION_AUTHORITY",
            "BOUND != WORK_EXECUTED",
            "LIFE_PACKET != PLAYED_ATTEMPT",
            "LOGICAL_RESEED != PLATFORM_RESET",
        ],
    }
    result["alignment_digest"] = _sha(result)
    return result


def align_campaign_v3_bound_life_packet(
    *,
    bound_receipt: Mapping[str, Any],
    life_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Prove structural identity agreement between one BOUND loop receipt and Life packet.

    The inputs remain caller-supplied public objects. A PASS proves deterministic
    structural agreement only; it does not independently prove that the BOUND
    receipt was produced by a real runtime mutation or that any work was executed.
    """
    if not isinstance(bound_receipt, Mapping):
        return _hold(
            status="HOLD_INVALID_BOUND_RECEIPT",
            failures=["bound_receipt_not_object"],
            bound_receipt=None,
            life_packet=life_packet if isinstance(life_packet, Mapping) else None,
        )
    if not isinstance(life_packet, Mapping):
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=["life_packet_not_object"],
            bound_receipt=bound_receipt,
            life_packet=None,
        )

    bound_errors = _validate_bound_receipt(bound_receipt)
    if bound_errors:
        return _hold(
            status="HOLD_INVALID_BOUND_RECEIPT",
            failures=bound_errors,
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )

    life_errors = list(validate_campaign_v3_life_quest_packet(life_packet))
    if life_errors:
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=[f"life_packet:{error}" for error in life_errors],
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )
    if life_packet.get("artifact") != LIFE_PACKET_ARTIFACT:
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=["life_packet_artifact"],
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )
    if life_packet.get("execution_authority") is not False:
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=["life_execution_authority_must_be_false"],
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )
    if life_packet.get("work_executed") is not False:
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=["life_work_executed_must_be_false"],
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )

    campaign = life_packet.get("campaign")
    pulse_binding = life_packet.get("pulse_binding")
    if not isinstance(campaign, Mapping) or not isinstance(pulse_binding, Mapping):
        return _hold(
            status="HOLD_INVALID_LIFE_PACKET",
            failures=["life_identity_surface_missing"],
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )

    expected = _identity_from_bound(bound_receipt)
    observed = {
        "campaign_id": _text(campaign.get("campaign_id")),
        "branch_id": _text(campaign.get("branch_id")),
        "residual_step": _positive_int(campaign.get("residual_step")),
        "pulse_digest": _text(pulse_binding.get("pulse_digest")),
        "loop_id": expected["loop_id"],
    }

    failures: list[str] = []
    for key in ("campaign_id", "branch_id", "residual_step", "pulse_digest"):
        if expected[key] != observed[key]:
            failures.append(f"identity_mismatch:{key}")
    if failures:
        return _hold(
            status="HOLD_IDENTITY_MISMATCH",
            failures=failures,
            bound_receipt=bound_receipt,
            life_packet=life_packet,
        )

    result = {
        "artifact": ARTIFACT,
        "status": "ALIGNED",
        "failures": [],
        "identity": expected,
        "bound_receipt_digest": _sha(bound_receipt),
        "life_packet_digest": _text(life_packet.get("packet_digest")),
        "structural_alignment": True,
        "receipt_provenance_proven": False,
        "execution_authority": False,
        "work_executed": False,
        "life_dispatch_executed": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "STRUCTURAL_ALIGNMENT != RECEIPT_PROVENANCE",
            "IDENTITY_ALIGNMENT != EXECUTION_AUTHORITY",
            "BOUND != WORK_EXECUTED",
            "LIFE_PACKET != PLAYED_ATTEMPT",
            "BOUND_PULSE_DIGEST == LIFE_PACKET_PULSE_DIGEST",
            "DISPATCH_TRANSLATOR_OWNERSHIP_UNCHANGED",
            "LOGICAL_RESEED != PLATFORM_RESET",
        ],
    }
    result["alignment_digest"] = _sha(result)
    return result


def validate_campaign_v3_life_bound_identity(receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, Mapping):
        return ["receipt_not_object"]

    extra = sorted(set(receipt) - _OUTPUT_KEYS)
    errors.extend(f"unknown:{key}" for key in extra)
    missing = sorted(_OUTPUT_KEYS - set(receipt))
    errors.extend(f"missing:{key}" for key in missing)

    if receipt.get("artifact") != ARTIFACT:
        errors.append("artifact")
    status = receipt.get("status")
    if status not in {
        "ALIGNED",
        "HOLD_INVALID_BOUND_RECEIPT",
        "HOLD_INVALID_LIFE_PACKET",
        "HOLD_IDENTITY_MISMATCH",
    }:
        errors.append("status")

    for key in (
        "receipt_provenance_proven",
        "execution_authority",
        "work_executed",
        "life_dispatch_executed",
        "platform_counter_reset_claimed",
    ):
        if receipt.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    aligned = receipt.get("structural_alignment")
    if status == "ALIGNED":
        if aligned is not True:
            errors.append("aligned_status_requires_structural_alignment")
        if receipt.get("failures") != []:
            errors.append("aligned_status_requires_empty_failures")
        identity = receipt.get("identity")
        if not isinstance(identity, Mapping):
            errors.append("identity")
        else:
            if set(identity) != {"campaign_id", "branch_id", "residual_step", "pulse_digest", "loop_id"}:
                errors.append("identity_keys")
            for key in ("campaign_id", "branch_id", "pulse_digest", "loop_id"):
                if not _text(identity.get(key)):
                    errors.append(f"identity_{key}")
            if _positive_int(identity.get("residual_step")) is None:
                errors.append("identity_residual_step")
        if not _text(receipt.get("bound_receipt_digest")):
            errors.append("bound_receipt_digest")
        if not _text(receipt.get("life_packet_digest")):
            errors.append("life_packet_digest")
    else:
        if aligned is not False:
            errors.append("hold_status_requires_no_alignment")
        if not isinstance(receipt.get("failures"), list) or not receipt.get("failures"):
            errors.append("hold_status_requires_failures")
        if receipt.get("identity") is not None:
            errors.append("hold_identity_must_be_null")

    laws = receipt.get("laws")
    if not isinstance(laws, list) or "STRUCTURAL_ALIGNMENT != RECEIPT_PROVENANCE" not in laws:
        errors.append("laws")

    digest = _text(receipt.get("alignment_digest"))
    basis = {key: value for key, value in receipt.items() if key != "alignment_digest"}
    if not digest or digest != _sha(basis):
        errors.append("alignment_digest")
    return errors


def verify_campaign_v3_life_bound_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_bound_identity(receipt)
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.BOUND.IDENTITY.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "alignment_digest": receipt.get("alignment_digest") if isinstance(receipt, Mapping) else None,
        "errors": errors,
        "receipt_provenance_proven": False,
        "execution_authority": False,
        "platform_counter_reset_claimed": False,
    }
