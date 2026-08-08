from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

ARTIFACT = "ATHENA.STEERING.PULSE.COMPILATION.V1"
ASSESSMENT_STATES = {"SATISFIED", "SUPERSEDED", "DEFERRED", "RESIDUAL", "HOLD"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _operation_surface(execution_surface: Mapping[str, Any] | None) -> set[str]:
    surface = execution_surface or {}
    names: set[str] = set()
    for key in (
        "exposed_operations",
        "frontier_tools",
        "prompt_tools",
        "rehydration_tools",
        "agent_tools",
        "campaign_tools",
    ):
        for value in surface.get(key) or []:
            if value:
                names.add(str(value))
    if surface.get("claim_tool_exposed"):
        names.add("athena_frontier_claim")
    return names


def _normalize_metrics(raw: Mapping[str, Any] | None) -> dict[str, float]:
    defaults = {
        "utility": 0.0,
        "dependency_unblocking": 0.0,
        "uncertainty_reduction": 0.0,
        "novelty": 0.0,
        "risk": 0.0,
        "cost": 0.0,
        "repetition": 0.0,
    }
    for key, value in (raw or {}).items():
        if key in defaults:
            defaults[key] = float(value)
    return defaults


def _validate_assessment(step: int, assessment: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    status = str(assessment.get("status") or "").upper()
    if status not in ASSESSMENT_STATES:
        failures.append(f"ASSESSMENT_STATUS:{step}:{status or 'MISSING'}")
        return failures

    evidence = [str(value) for value in assessment.get("evidence_refs") or [] if str(value).strip()]
    reason = str(assessment.get("reason") or "").strip()

    if status in {"SATISFIED", "SUPERSEDED", "RESIDUAL", "HOLD"} and not evidence:
        failures.append(f"ASSESSMENT_EVIDENCE_REQUIRED:{step}:{status}")
    if status in {"SUPERSEDED", "DEFERRED", "HOLD"} and not reason:
        failures.append(f"ASSESSMENT_REASON_REQUIRED:{step}:{status}")
    if status == "RESIDUAL" and not str(assessment.get("task") or "").strip():
        failures.append(f"RESIDUAL_TASK_REQUIRED:{step}")
    if assessment.get("requires_execution_authority") and not str(assessment.get("required_operation") or "").strip():
        failures.append(f"EXECUTION_OPERATION_REQUIRED:{step}")

    expected_vid = assessment.get("expected_vid")
    current_vid = assessment.get("current_vid")
    if expected_vid is not None and current_vid is not None and str(expected_vid) != str(current_vid):
        failures.append(f"STALE_TARGET:{step}:{expected_vid}!={current_vid}")
    return failures


def compile_pulse(
    pulse: Mapping[str, Any],
    assessments: Iterable[Mapping[str, Any]],
    *,
    expected_source_body_digest: str,
    current_address: Mapping[str, Any],
    execution_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one verified ledger pulse into current-state campaign candidates.

    The function does not infer task completion from action prose. Every historical
    action must have an explicit evidence-bearing assessment. Only RESIDUAL actions
    whose required operation is actually exposed may become campaign candidates.
    The result is routing/coordination state, never execution authorization.
    """

    failures: list[str] = []
    holds: list[dict[str, Any]] = []
    actions = list(pulse.get("actions") or [])
    assessment_rows = [dict(row) for row in assessments]
    pulse_index = int(pulse.get("pulse_index") or 0)
    step_start = int(pulse.get("step_start") or 0)
    step_end = int(pulse.get("step_end") or 0)
    source_digest = str(pulse.get("source_body_digest") or "")

    expected_steps = list(range(step_start, step_end + 1)) if step_start and step_end else []
    observed_steps = [int(row.get("step") or 0) for row in actions]
    if len(actions) != 10 or observed_steps != expected_steps or len(expected_steps) != 10:
        failures.append("PULSE_SOURCE_SEQUENCE")
    if source_digest != str(expected_source_body_digest or ""):
        failures.append("STALE_PULSE_SOURCE_DIGEST")
    source_tags = [str(row.get("tag") or "") for row in actions]
    if source_tags != ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]:
        failures.append("PULSE_433_SOURCE_INVARIANT")

    git_head = str(current_address.get("git_head") or current_address.get("H") or "")
    if not git_head:
        failures.append("MISSING_CURRENT_GIT_HEAD")
    if current_address.get("shared_fresh") is False:
        failures.append("UNVERIFIED_SHARED_FRESHNESS")

    assessments_by_step: dict[int, Mapping[str, Any]] = {}
    for raw in assessment_rows:
        step = int(raw.get("step") or 0)
        if step in assessments_by_step:
            failures.append(f"DUPLICATE_ASSESSMENT:{step}")
        assessments_by_step[step] = raw
    missing_assessments = [step for step in expected_steps if step not in assessments_by_step]
    unexpected_assessments = sorted(set(assessments_by_step) - set(expected_steps))
    if missing_assessments:
        failures.append("MISSING_ASSESSMENTS:" + ",".join(map(str, missing_assessments)))
    if unexpected_assessments:
        failures.append("UNEXPECTED_ASSESSMENTS:" + ",".join(map(str, unexpected_assessments)))

    for step in expected_steps:
        assessment = assessments_by_step.get(step)
        if assessment is not None:
            failures.extend(_validate_assessment(step, assessment))

    exposed_operations = _operation_surface(execution_surface)
    action_records = []
    candidates = []
    status_counts = {state: {"I": 0, "M": 0, "L": 0, "total": 0} for state in sorted(ASSESSMENT_STATES)}

    source_by_step = {int(row.get("step") or 0): row for row in actions}
    if not failures:
        for step in expected_steps:
            source_action = source_by_step[step]
            assessment = assessments_by_step[step]
            status = str(assessment["status"]).upper()
            tag = str(source_action["tag"])
            status_counts[status][tag] += 1
            status_counts[status]["total"] += 1

            required_operation = str(assessment.get("required_operation") or "").strip() or None
            requires_execution = bool(assessment.get("requires_execution_authority", False))
            operation_exposed = required_operation in exposed_operations if required_operation else None
            record = {
                "step": step,
                "tag": tag,
                "source_text": str(source_action.get("text") or ""),
                "status": status,
                "reason": assessment.get("reason"),
                "evidence_refs": list(assessment.get("evidence_refs") or []),
                "required_capability_class": assessment.get("required_capability_class"),
                "required_operation": required_operation,
                "operation_exposed": operation_exposed,
                "requires_execution_authority": requires_execution,
            }

            if status == "HOLD":
                holds.append(
                    {
                        "step": step,
                        "kind": "ASSESSMENT_HOLD",
                        "reason": assessment.get("reason"),
                        "evidence_refs": list(assessment.get("evidence_refs") or []),
                    }
                )
            elif status == "RESIDUAL":
                if requires_execution and not required_operation:
                    holds.append(
                        {
                            "step": step,
                            "kind": "UNBOUND_EXECUTION_AUTHORITY",
                            "reason": "Residual requires execution authority but no exact operation was bound.",
                        }
                    )
                elif required_operation and not operation_exposed:
                    holds.append(
                        {
                            "step": step,
                            "kind": "UNEXPOSED_REQUIRED_OPERATION",
                            "required_operation": required_operation,
                            "reason": "Required operation is not present in the supplied current execution surface.",
                        }
                    )
                else:
                    candidate_id = f"ledger-p{pulse_index:03d}-s{step:04d}"
                    candidates.append(
                        {
                            "candidate_id": candidate_id,
                            "task": str(assessment["task"]).strip(),
                            "metrics": _normalize_metrics(assessment.get("routing_metrics")),
                            "source": {
                                "kind": "STEERING_LEDGER_RESIDUAL",
                                "pulse_index": pulse_index,
                                "step": step,
                                "tag": tag,
                                "comment_id": pulse.get("source_comment_id"),
                                "source_body_digest": source_digest,
                                "evidence_refs": list(assessment.get("evidence_refs") or []),
                            },
                            "required_capability_class": assessment.get("required_capability_class"),
                            "required_operation": required_operation,
                            "standing": "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY",
                        }
                    )
            action_records.append(record)

    coverage = {
        "source": {
            "I": sum(str(row.get("tag")) == "I" for row in actions),
            "M": sum(str(row.get("tag")) == "M" for row in actions),
            "L": sum(str(row.get("tag")) == "L" for row in actions),
        },
        "assessment_status": status_counts,
        "all_actions_accounted": bool(expected_steps) and not missing_assessments and not unexpected_assessments,
    }

    if failures:
        status = "HOLD_INVALID_COMPILATION_INPUT"
        can_advance = False
        next_action = "REHYDRATE_OR_REPAIR_INPUT"
    elif holds:
        status = "HOLD"
        can_advance = False
        next_action = "RESOLVE_TYPED_HOLDS"
    elif candidates:
        status = "RESIDUAL_CANDIDATES"
        can_advance = False
        next_action = "ROUTE_CAMPAIGN_CANDIDATES"
    else:
        status = "ACCOUNTED"
        can_advance = True
        next_action = "REHYDRATE_AND_RESEED_CURRENT_CUT" if pulse_index == 100 else "ADVANCE_TO_NEXT_PULSE"

    address_digest = _sha(dict(current_address)) if current_address else None
    compilation_basis = {
        "pulse_index": pulse_index,
        "source_body_digest": source_digest,
        "current_address_digest": address_digest,
        "exposed_operations": sorted(exposed_operations),
        "assessment_digest": _sha(
            [
                {
                    "step": int(row.get("step") or 0),
                    "status": str(row.get("status") or "").upper(),
                    "reason": row.get("reason"),
                    "evidence_refs": list(row.get("evidence_refs") or []),
                    "task": row.get("task"),
                    "required_capability_class": row.get("required_capability_class"),
                    "required_operation": row.get("required_operation"),
                    "requires_execution_authority": bool(row.get("requires_execution_authority", False)),
                    "expected_vid": row.get("expected_vid"),
                    "current_vid": row.get("current_vid"),
                    "routing_metrics": _normalize_metrics(row.get("routing_metrics")),
                }
                for row in sorted(assessment_rows, key=lambda item: int(item.get("step") or 0))
            ]
        ),
    }

    return {
        "artifact": ARTIFACT,
        "status": status,
        "pulse_index": pulse_index,
        "step_start": step_start,
        "step_end": step_end,
        "source_comment_id": pulse.get("source_comment_id"),
        "source_body_digest": source_digest,
        "current_address": dict(current_address),
        "current_address_digest": address_digest,
        "exposed_operations": sorted(exposed_operations),
        "failures": failures,
        "holds": holds,
        "coverage": coverage,
        "actions": action_records,
        "candidates": candidates,
        "can_advance_pulse": can_advance,
        "next": next_action,
        "compilation_digest": _sha(compilation_basis),
        "laws": [
            "LEDGER_ACTION != CURRENT_STATE_FACT",
            "ASSESSMENT_REQUIRES_PUBLIC_EVIDENCE",
            "CAMPAIGN_CANDIDATE != EXECUTION_AUTHORITY",
            "UNEXPOSED_REQUIRED_OPERATION => HOLD",
            "FEATURE_BRANCH != CURRENT_RUNTIME_EXPOSURE",
            "PULSE_433_COVERAGE_PRESERVED",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }
