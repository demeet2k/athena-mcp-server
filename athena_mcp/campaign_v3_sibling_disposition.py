from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .campaign_v3_ledger import ACTION_STATES, PULSE_ARTIFACT

ARTIFACT = "ATHENA.CAMPAIGN.V3.SIBLING.DISPOSITION.V1"
RELATION_TO_STATUS = {
    "SATISFIES": "SATISFIED",
    "SUPERSEDES": "SUPERSEDED",
}

LAWS = [
    "DELIVERY != CONSUMPTION",
    "CONSUMPTION != CAUSAL_INFLUENCE",
    "SIBLING_DELTA != SATISFIED_UNTIL_CURRENT_RECIPIENT_READBACK",
    "SATISFIED != EXECUTION_AUTHORITY",
    "SUPERSEDED != ERASED",
    "HISTORICAL_ACTION_TEXT_REMAINS_SOURCE_LINEAGE",
    "STALE_RECIPIENT_HEAD => HOLD",
    "SIBLING_EVIDENCE_BINDING != CLAIM",
]


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    return digest == _sha({k: v for k, v in pulse.items() if k != "pulse_digest"})


def _text(value: Any) -> str:
    return str(value or "").strip()


def _action(pulse: Mapping[str, Any], step: int) -> dict[str, Any] | None:
    for row in pulse.get("actions") or []:
        if int(row.get("step") or -1) == int(step):
            return dict(row)
    return None


def bind_sibling_disposition(
    *,
    pulse: Mapping[str, Any],
    sibling_delta: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind current, consumed sibling evidence to one canonical Campaign V3 action.

    No prose inference is performed. A caller must explicitly declare SATISFIES or
    SUPERSEDES and provide recipient readback at the pulse's current shared head.
    """
    failures: list[str] = []
    if pulse.get("artifact") != PULSE_ARTIFACT:
        failures.append("PULSE_ARTIFACT_INVALID")
    if not _pulse_integrity(pulse):
        failures.append("PULSE_DIGEST_INVALID")
    if pulse.get("execution_authorized") is not False:
        failures.append("PULSE_AUTHORITY_FIREWALL_MISSING")

    address = pulse.get("current_coordinates") or {}
    current_head = _text(address.get("git_head"))
    if not current_head:
        failures.append("CURRENT_GIT_HEAD_REQUIRED")
    if address.get("shared_fresh") is not True:
        failures.append("SHARED_FRESHNESS_REQUIRED")

    target_step = int(sibling_delta.get("target_step") or 0)
    action = _action(pulse, target_step)
    if action is None:
        failures.append("TARGET_STEP_NOT_IN_PULSE")
        source_action = {"step": target_step, "horizon": None, "text": None}
    else:
        source_action = {
            "step": int(action["step"]),
            "horizon": _text(action.get("horizon")),
            "text": _text(action.get("text")),
        }
        if source_action["horizon"] not in {"I", "M", "L"}:
            failures.append("PULSE_HORIZON_INVALID")
        if not source_action["text"]:
            failures.append("PULSE_TEXT_REQUIRED")
        if str(action.get("current_state") or "").upper() not in ACTION_STATES:
            failures.append("PULSE_CURRENT_STATE_INVALID")

    relation = _text(sibling_delta.get("relation")).upper()
    if relation not in RELATION_TO_STATUS:
        failures.append("RELATION_MUST_BE_SATISFIES_OR_SUPERSEDES")

    source_ref = _text(sibling_delta.get("source_ref"))
    source_head = _text(sibling_delta.get("source_head"))
    recipient_head = _text(sibling_delta.get("recipient_head"))
    recipient_readback_ref = _text(sibling_delta.get("recipient_readback_ref"))
    reason = _text(sibling_delta.get("reason"))
    if not source_ref:
        failures.append("SIBLING_SOURCE_REF_REQUIRED")
    if not source_head:
        failures.append("SIBLING_SOURCE_HEAD_REQUIRED")
    if not recipient_head:
        failures.append("RECIPIENT_HEAD_REQUIRED")
    elif current_head and recipient_head != current_head:
        failures.append(f"STALE_RECIPIENT_HEAD:{recipient_head}!={current_head}")
    if sibling_delta.get("consumed") is not True:
        failures.append("RECIPIENT_CONSUMPTION_READBACK_REQUIRED")
    if not recipient_readback_ref:
        failures.append("RECIPIENT_READBACK_REF_REQUIRED")
    if not reason:
        failures.append("DISPOSITION_REASON_REQUIRED")

    evidence_refs = [
        _text(value)
        for value in (sibling_delta.get("evidence_refs") or [])
        if _text(value)
    ]
    if source_ref and source_ref not in evidence_refs:
        evidence_refs.append(source_ref)
    if recipient_readback_ref and recipient_readback_ref not in evidence_refs:
        evidence_refs.append(recipient_readback_ref)
    if not evidence_refs:
        failures.append("EVIDENCE_REFS_REQUIRED")

    expected_vid = sibling_delta.get("expected_vid")
    current_vid = sibling_delta.get("current_vid")
    if expected_vid is not None and current_vid is not None and str(expected_vid) != str(current_vid):
        failures.append(f"STALE_TARGET:{expected_vid}!={current_vid}")

    base = {
        "artifact": ARTIFACT,
        "pulse_digest": pulse.get("pulse_digest"),
        "target_step": target_step,
        "source_action": source_action,
        "relation": relation or None,
        "sibling": {
            "source_ref": source_ref or None,
            "source_head": source_head or None,
            "recipient_head": recipient_head or None,
            "recipient_readback_ref": recipient_readback_ref or None,
            "consumed": sibling_delta.get("consumed") is True,
        },
        "failures": failures,
        "execution_authority": False,
        "laws": list(LAWS),
    }
    if failures:
        return {
            **base,
            "status": "HOLD_INVALID_SIBLING_EVIDENCE",
            "assessment": None,
            "standing": "NO_DISPOSITION_BOUND",
            "next": "REHYDRATE_OR_REPAIR_SIBLING_EVIDENCE",
        }

    assessment = {
        "step": target_step,
        "status": RELATION_TO_STATUS[relation],
        "reason": reason,
        "evidence_refs": evidence_refs,
    }
    if expected_vid is not None:
        assessment["expected_vid"] = str(expected_vid)
    if current_vid is not None:
        assessment["current_vid"] = str(current_vid)
    receipt = {
        **base,
        "status": "BOUND",
        "assessment": assessment,
        "standing": "EVIDENCE_BOUND_ASSESSMENT_NOT_EXECUTION_AUTHORITY",
        "next": "APPLY_DISPOSITION_AND_RESEAL_CURRENT_PULSE",
    }
    receipt["receipt_digest"] = _sha(receipt)
    return receipt


def apply_sibling_disposition(
    pulse: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply one verified sibling disposition and re-seal the canonical pulse."""
    if pulse.get("artifact") != PULSE_ARTIFACT or not _pulse_integrity(pulse):
        raise ValueError("invalid or tampered pulse")
    if receipt.get("artifact") != ARTIFACT or receipt.get("status") != "BOUND":
        raise ValueError("receipt is not a bound sibling disposition")
    receipt_digest = str(receipt.get("receipt_digest") or "")
    if not receipt_digest or receipt_digest != _sha({k: v for k, v in receipt.items() if k != "receipt_digest"}):
        raise ValueError("invalid sibling disposition receipt digest")
    if receipt.get("execution_authority") is not False:
        raise ValueError("sibling disposition cannot grant execution authority")
    if receipt.get("pulse_digest") != pulse.get("pulse_digest"):
        raise ValueError("receipt was bound to a different pulse")

    step = int(receipt.get("target_step") or 0)
    source = receipt.get("source_action") or {}
    current = _action(pulse, step)
    if current is None:
        raise ValueError("target step is not in pulse")
    if {
        "step": int(current.get("step") or 0),
        "horizon": _text(current.get("horizon")),
        "text": _text(current.get("text")),
    } != {
        "step": int(source.get("step") or 0),
        "horizon": _text(source.get("horizon")),
        "text": _text(source.get("text")),
    }:
        raise ValueError("historical source action drift")

    assessment = receipt.get("assessment") or {}
    new_state = _text(assessment.get("status")).upper()
    if new_state not in {"SATISFIED", "SUPERSEDED"}:
        raise ValueError("receipt assessment is not a selective-satisfaction state")

    updated = json.loads(json.dumps(pulse))
    for row in updated["actions"]:
        if int(row.get("step") or -1) == step:
            row["current_state"] = new_state
            row["history_preserved"] = True
            row["sibling_disposition"] = {
                "receipt_digest": receipt_digest,
                "relation": receipt.get("relation"),
                "reason": assessment.get("reason"),
                "evidence_refs": list(assessment.get("evidence_refs") or []),
            }
            break

    status_counts = {
        horizon: {state: 0 for state in ACTION_STATES}
        for horizon in ("I", "M", "L")
    }
    for row in updated["actions"]:
        status_counts[str(row["horizon"])][str(row["current_state"])] += 1
    updated["current_status_counts"] = status_counts
    updated["residual_steps"] = [int(row["step"]) for row in updated["actions"] if row["current_state"] == "RESIDUAL"]
    updated["hold_steps"] = [int(row["step"]) for row in updated["actions"] if row["current_state"] == "HOLD"]
    updated["authority_resolution_required"] = bool(updated["residual_steps"])
    updated["execution_authorized"] = False

    holds = [
        value for value in (updated.get("holds") or [])
        if value not in {"OPERATIONAL_BASIS_UNAVAILABLE_HOLD", "PULSE_ACTION_HOLD"}
    ]
    if updated["residual_steps"] and updated.get("operational_basis_status") == "UNAVAILABLE":
        holds.append("OPERATIONAL_BASIS_UNAVAILABLE_HOLD")
    if updated["hold_steps"]:
        holds.append("PULSE_ACTION_HOLD")
    updated["holds"] = holds
    updated.setdefault("sibling_disposition_receipts", []).append(receipt_digest)
    for law in LAWS:
        if law not in updated.setdefault("laws", []):
            updated["laws"].append(law)
    updated.pop("pulse_digest", None)
    updated["pulse_digest"] = _sha(updated)
    return updated
