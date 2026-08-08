from __future__ import annotations

from typing import Any, Mapping

ARTIFACT = "ATHENA.STEERING.SIBLING.DISPOSITION.V1"
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


def _text(value: Any) -> str:
    return str(value or "").strip()


def bind_sibling_disposition(
    *,
    pulse_action: Mapping[str, Any],
    current_address: Mapping[str, Any],
    sibling_delta: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind an explicitly consumed sibling delta to one historical pulse action.

    The function performs no semantic inference from prose. The caller must state
    an explicit SATISFIES or SUPERSEDES relation and provide current-head recipient
    readback/evidence. The original historical action is preserved verbatim in the
    returned receipt and remains the source text used by the pulse compiler.
    """

    failures: list[str] = []
    step = int(pulse_action.get("step") or 0)
    tag = _text(pulse_action.get("tag"))
    historical_text = _text(pulse_action.get("text"))
    if step <= 0:
        failures.append("PULSE_STEP_REQUIRED")
    if tag not in {"I", "M", "L"}:
        failures.append("PULSE_TAG_REQUIRED")
    if not historical_text:
        failures.append("PULSE_TEXT_REQUIRED")

    current_head = _text(current_address.get("git_head") or current_address.get("H"))
    if not current_head:
        failures.append("CURRENT_GIT_HEAD_REQUIRED")
    if current_address.get("shared_fresh") is not True:
        failures.append("SHARED_FRESHNESS_REQUIRED")

    relation = _text(sibling_delta.get("relation")).upper()
    if relation not in RELATION_TO_STATUS:
        failures.append("RELATION_MUST_BE_SATISFIES_OR_SUPERSEDES")

    target_step = int(sibling_delta.get("target_step") or 0)
    if target_step != step:
        failures.append(f"TARGET_STEP_MISMATCH:{target_step}!={step}")

    source_ref = _text(sibling_delta.get("source_ref"))
    source_head = _text(sibling_delta.get("source_head"))
    recipient_head = _text(sibling_delta.get("recipient_head"))
    recipient_readback_ref = _text(sibling_delta.get("recipient_readback_ref"))
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

    reason = _text(sibling_delta.get("reason"))
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
    if (
        expected_vid is not None
        and current_vid is not None
        and str(expected_vid) != str(current_vid)
    ):
        failures.append(f"STALE_TARGET:{expected_vid}!={current_vid}")

    base = {
        "artifact": ARTIFACT,
        "target_step": step,
        "source_action": {
            "step": step,
            "tag": tag,
            "text": historical_text,
        },
        "sibling": {
            "source_ref": source_ref or None,
            "source_head": source_head or None,
            "recipient_head": recipient_head or None,
            "recipient_readback_ref": recipient_readback_ref or None,
            "consumed": sibling_delta.get("consumed") is True,
        },
        "relation": relation or None,
        "failures": failures,
        "execution_authority": False,
        "laws": list(LAWS),
    }

    if failures:
        return {
            **base,
            "status": "HOLD_INVALID_SIBLING_EVIDENCE",
            "assessment": None,
            "next": "REHYDRATE_OR_REPAIR_SIBLING_EVIDENCE",
            "standing": "NO_DISPOSITION_BOUND",
        }

    assessment = {
        "step": step,
        "status": RELATION_TO_STATUS[relation],
        "reason": reason,
        "evidence_refs": evidence_refs,
    }
    if expected_vid is not None:
        assessment["expected_vid"] = str(expected_vid)
    if current_vid is not None:
        assessment["current_vid"] = str(current_vid)

    return {
        **base,
        "status": "BOUND",
        "assessment": assessment,
        "next": "PASS_ASSESSMENT_TO_CURRENT_STATE_PULSE_COMPILER",
        "standing": "EVIDENCE_BOUND_ASSESSMENT_NOT_EXECUTION_AUTHORITY",
    }
