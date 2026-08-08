
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .campaign_v3_ledger import PULSE_ARTIFACT, compile_current_pulse

ARTIFACT = "ATHENA.CAMPAIGN.V3.SIBLING.DISPOSITION.V1"
PULSE_BINDING_ARTIFACT = "ATHENA.CAMPAIGN.V3.SIBLING.PULSE.V1"
RELATION_TO_STATE = {"SATISFIES": "SATISFIED", "SUPERSEDES": "SUPERSEDED"}

LAWS = [
    "DELIVERY != CONSUMPTION",
    "CONSUMPTION != CAUSAL_INFLUENCE",
    "SIBLING_DELTA != SATISFIED_UNTIL_CURRENT_RECIPIENT_EFFECT_READBACK",
    "SATISFIED != EXECUTION_AUTHORITY",
    "SUPERSEDED != ERASED",
    "HISTORICAL_ACTION_TEXT_REMAINS_SOURCE_LINEAGE",
    "STALE_RECIPIENT_HEAD => HOLD",
    "SIBLING_EVIDENCE_BINDING != CLAIM",
]


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def bind_sibling_disposition(
    *,
    pulse_action: Mapping[str, Any],
    current_coordinates: Mapping[str, Any],
    sibling_delta: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind one explicit consumed+observed sibling effect to one historical action.

    No prose inference is performed. SATISFIED/SUPERSEDED is emitted only when
    the current recipient explicitly names the relation and provides current-head
    readback plus an observed-effect witness.
    """
    failures: list[str] = []
    step = _int(pulse_action.get("step"))
    horizon = _text(pulse_action.get("horizon")).upper()
    historical_text = _text(pulse_action.get("text"))
    if step <= 0:
        failures.append("PULSE_STEP_REQUIRED")
    if horizon not in {"I", "M", "L"}:
        failures.append("PULSE_HORIZON_REQUIRED")
    if not historical_text:
        failures.append("PULSE_TEXT_REQUIRED")

    current_head = _text(current_coordinates.get("git_head"))
    if not current_head:
        failures.append("CURRENT_GIT_HEAD_REQUIRED")
    if current_coordinates.get("shared_fresh") is not True:
        failures.append("SHARED_FRESHNESS_REQUIRED")

    relation = _text(sibling_delta.get("relation")).upper()
    if relation not in RELATION_TO_STATE:
        failures.append("RELATION_MUST_BE_SATISFIES_OR_SUPERSEDES")

    target_step = _int(sibling_delta.get("target_step"))
    if target_step != step:
        failures.append(f"TARGET_STEP_MISMATCH:{target_step}!={step}")

    source_ref = _text(sibling_delta.get("source_ref"))
    source_head = _text(sibling_delta.get("source_head"))
    recipient_head = _text(sibling_delta.get("recipient_head"))
    recipient_readback_ref = _text(sibling_delta.get("recipient_readback_ref"))
    recipient_effect_ref = _text(sibling_delta.get("recipient_effect_ref"))

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
    if sibling_delta.get("recipient_effect_observed") is not True:
        failures.append("RECIPIENT_EFFECT_OBSERVATION_REQUIRED")
    if not recipient_effect_ref:
        failures.append("RECIPIENT_EFFECT_REF_REQUIRED")

    reason = _text(sibling_delta.get("reason"))
    if not reason:
        failures.append("DISPOSITION_REASON_REQUIRED")

    evidence_refs = [
        _text(value)
        for value in (sibling_delta.get("evidence_refs") or [])
        if _text(value)
    ]
    for required_ref in (source_ref, recipient_readback_ref, recipient_effect_ref):
        if required_ref and required_ref not in evidence_refs:
            evidence_refs.append(required_ref)
    if not evidence_refs:
        failures.append("EVIDENCE_REFS_REQUIRED")

    expected_vid = sibling_delta.get("expected_vid")
    current_vid = sibling_delta.get("current_vid")
    if (expected_vid is None) != (current_vid is None):
        failures.append("VID_PAIR_REQUIRED")
    elif expected_vid is not None and str(expected_vid) != str(current_vid):
        failures.append(f"STALE_TARGET:{expected_vid}!={current_vid}")

    source_action = {"step": step, "horizon": horizon, "text": historical_text}
    base = {
        "artifact": ARTIFACT,
        "target_step": step,
        "source_action": source_action,
        "source_action_digest": _sha(source_action),
        "sibling": {
            "source_ref": source_ref or None,
            "source_head": source_head or None,
            "recipient_head": recipient_head or None,
            "recipient_readback_ref": recipient_readback_ref or None,
            "recipient_effect_ref": recipient_effect_ref or None,
            "consumed": sibling_delta.get("consumed") is True,
            "recipient_effect_observed": sibling_delta.get("recipient_effect_observed") is True,
        },
        "relation": relation or None,
        "reason": reason or None,
        "evidence_refs": evidence_refs,
        "failures": failures,
        "execution_authority": False,
        "laws": list(LAWS),
    }

    if failures:
        result = {
            **base,
            "status": "HOLD_INVALID_SIBLING_EVIDENCE",
            "current_state": None,
            "next": "REHYDRATE_OR_REPAIR_SIBLING_EVIDENCE",
            "standing": "NO_DISPOSITION_BOUND",
        }
    else:
        result = {
            **base,
            "status": "BOUND",
            "current_state": RELATION_TO_STATE[relation],
            "next": "PASS_STATE_TO_CURRENT_CAMPAIGN_V3_PULSE_COMPILER",
            "standing": "EVIDENCE_BOUND_DISPOSITION_NOT_EXECUTION_AUTHORITY",
        }
    result["receipt_digest"] = _sha(
        {key: value for key, value in result.items() if key != "receipt_digest"}
    )
    return result


def compile_pulse_with_sibling_dispositions(
    *,
    ledger_source: Mapping[str, Any],
    pulse_index: int,
    current_coordinates: Mapping[str, Any],
    sibling_deltas: Iterable[Mapping[str, Any]],
    operational_basis: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile a current Campaign V3 pulse after binding consumed sibling effects.

    Any invalid/conflicting sibling evidence holds the batch and returns no
    rewritten pulse. Valid dispositions are applied only through the integrated
    Campaign V3 compiler; unspecified actions remain RESIDUAL.
    """
    try:
        baseline = compile_current_pulse(
            dict(ledger_source),
            int(pulse_index),
            current_coordinates=dict(current_coordinates),
            action_states={},
            operational_basis=dict(operational_basis) if operational_basis is not None else None,
        )
    except Exception as exc:
        result = {
            "artifact": PULSE_BINDING_ARTIFACT,
            "status": "HOLD_INVALID_LEDGER_OR_PULSE_SOURCE",
            "pulse_index": int(pulse_index),
            "failures": [f"{type(exc).__name__}:{exc}"],
            "dispositions": [],
            "pulse": None,
            "execution_authority": False,
            "laws": list(LAWS),
        }
        result["binding_digest"] = _sha(
            {k: v for k, v in result.items() if k != "binding_digest"}
        )
        return result

    actions_by_step = {int(row["step"]): row for row in baseline.get("actions") or []}
    deltas = [dict(row) for row in sibling_deltas]
    receipts: list[dict[str, Any]] = []
    failures: list[str] = []
    action_states: dict[int, str] = {}
    seen: set[int] = set()

    for index, delta in enumerate(deltas):
        target_step = _int(delta.get("target_step"))
        if target_step in seen:
            failures.append(f"DUPLICATE_TARGET_STEP:{target_step}")
            continue
        seen.add(target_step)
        action = actions_by_step.get(target_step)
        if action is None:
            failures.append(f"TARGET_STEP_OUTSIDE_PULSE:{target_step}")
            continue
        receipt = bind_sibling_disposition(
            pulse_action=action,
            current_coordinates=current_coordinates,
            sibling_delta=delta,
        )
        receipts.append(receipt)
        if receipt["status"] != "BOUND":
            failures.extend(
                f"STEP_{target_step:04d}:{failure}"
                for failure in receipt.get("failures") or ["UNBOUND"]
            )
            continue
        action_states[target_step] = str(receipt["current_state"])

    if failures:
        result = {
            "artifact": PULSE_BINDING_ARTIFACT,
            "status": "HOLD_INVALID_SIBLING_EVIDENCE",
            "pulse_index": int(pulse_index),
            "ledger_digest": baseline.get("ledger_digest"),
            "current_coordinates": dict(current_coordinates),
            "failures": failures,
            "dispositions": receipts,
            "pulse": None,
            "execution_authority": False,
            "laws": list(LAWS),
        }
    else:
        pulse = compile_current_pulse(
            dict(ledger_source),
            int(pulse_index),
            current_coordinates=dict(current_coordinates),
            action_states=action_states,
            operational_basis=dict(operational_basis) if operational_basis is not None else None,
        )
        result = {
            "artifact": PULSE_BINDING_ARTIFACT,
            "status": "COMPILED",
            "pulse_index": int(pulse_index),
            "ledger_digest": pulse.get("ledger_digest"),
            "current_coordinates": dict(current_coordinates),
            "dispositions": receipts,
            "applied_states": {str(step): state for step, state in sorted(action_states.items())},
            "pulse": pulse,
            "execution_authority": False,
            "laws": list(LAWS) + [
                "SIBLING_DISPOSITION != PULSE_EXECUTION",
                "CURRENT_COMPILER_REMAINS_SINGLE_SOURCE_OF_PULSE_STATE",
            ],
        }
    result["binding_digest"] = _sha(
        {k: v for k, v in result.items() if k != "binding_digest"}
    )
    return result
