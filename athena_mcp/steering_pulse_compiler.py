from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

ARTIFACT = "ATHENA.STEERING.CAMPAIGN.CURRENT_STATE.PULSE.V1"
WORK_ORDER_ARTIFACT = "ATHENA.STEERING.CAMPAIGN.ROUTING.WORK_ORDER.V1"

REQUIRED_CURRENT_STATE = (
    "git_head",
    "prompt_stack_digest",
    "frontier_digest",
    "operational_basis_digest",
    "issue_pressure_digest",
)

DISPOSITIONS = {
    "SATISFIED",
    "SUPERSEDED",
    "RESIDUAL",
    "DEFERRED",
    "HOLD",
}

EXPECTED_TAGS = ("I", "I", "I", "I", "M", "M", "M", "L", "L", "L")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _assessment_map(assessments: Iterable[Mapping[str, Any]]) -> tuple[dict[int, Mapping[str, Any]], list[str]]:
    failures: list[str] = []
    out: dict[int, Mapping[str, Any]] = {}
    for assessment in assessments:
        try:
            step = int(assessment.get("step"))
        except (TypeError, ValueError):
            failures.append("ASSESSMENT_STEP_INVALID")
            continue
        if step in out:
            failures.append(f"ASSESSMENT_DUPLICATE:{step}")
            continue
        out[step] = assessment
    return out, failures


def _source_validation_for_pulse(
    pulse: Mapping[str, Any],
    source_validation: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    if source_validation.get("status") != "PASS":
        failures.append("SOURCE_VALIDATION_NOT_PASS")
        return failures

    source_comment_id = int(pulse.get("source_comment_id") or 0)
    source_body_digest = str(pulse.get("source_body_digest") or "")
    matching = [
        block
        for block in source_validation.get("blocks", [])
        if int(block.get("comment_id") or 0) == source_comment_id
    ]
    if len(matching) != 1:
        failures.append("SOURCE_VALIDATION_BLOCK_MISSING")
    elif str(matching[0].get("body_digest") or "") != source_body_digest:
        failures.append("PULSE_SOURCE_DIGEST_MISMATCH")

    if not _nonempty(source_validation.get("source_bundle_digest")):
        failures.append("SOURCE_BUNDLE_DIGEST_MISSING")
    return failures


def compile_current_state_pulse(
    pulse: Mapping[str, Any],
    source_validation: Mapping[str, Any],
    current_state: Mapping[str, Any],
    assessments: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compile one verified historical pulse against supplied current observations.

    This function does not inspect Git, claim work, mutate scheduler state, or execute
    any source action. The caller must supply a fresh source-validation receipt and a
    fresh current-state observation packet. Output candidates are routing-only.
    """
    failures = _source_validation_for_pulse(pulse, source_validation)

    pulse_index = int(pulse.get("pulse_index") or 0)
    actions = [dict(row) for row in pulse.get("actions", [])]
    steps = [int(row.get("step") or 0) for row in actions]
    tags = [str(row.get("tag") or "") for row in actions]
    expected_start = (pulse_index - 1) * 10 + 1 if pulse_index else 0
    expected_steps = list(range(expected_start, expected_start + 10)) if pulse_index else []

    if not 1 <= pulse_index <= 100:
        failures.append("PULSE_INDEX_INVALID")
    if len(actions) != 10:
        failures.append(f"PULSE_ACTION_COUNT:{len(actions)}")
    if steps != expected_steps:
        failures.append("PULSE_SEQUENCE_INVALID")
    if tuple(tags) != EXPECTED_TAGS:
        failures.append("PULSE_TAG_PATTERN_INVALID")
    if pulse.get("standing") != "CURRICULUM_BUNDLE_NOT_EXECUTION_AUTHORITY":
        failures.append("PULSE_STANDING_INVALID")

    missing_state = [key for key in REQUIRED_CURRENT_STATE if not _nonempty(current_state.get(key))]
    failures.extend(f"CURRENT_STATE_MISSING:{key}" for key in missing_state)

    assessment_by_step, assessment_failures = _assessment_map(assessments)
    failures.extend(assessment_failures)
    expected_step_set = set(expected_steps)
    observed_step_set = set(assessment_by_step)
    for step in sorted(expected_step_set - observed_step_set):
        failures.append(f"ASSESSMENT_MISSING:{step}")
    for step in sorted(observed_step_set - expected_step_set):
        failures.append(f"ASSESSMENT_UNEXPECTED:{step}")

    rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    disposition_counts = {name: 0 for name in sorted(DISPOSITIONS)}
    by_horizon = {
        tag: {name: 0 for name in sorted(DISPOSITIONS)}
        for tag in ("I", "M", "L")
    }

    action_by_step = {int(row.get("step") or 0): row for row in actions}
    for step in expected_steps:
        action = action_by_step.get(step, {})
        assessment = assessment_by_step.get(step, {})
        horizon = str(action.get("tag") or "")
        disposition = str(assessment.get("disposition") or "").upper()
        evidence_refs = [
            str(ref).strip()
            for ref in assessment.get("evidence_refs", [])
            if str(ref).strip()
        ]
        reason = str(assessment.get("reason") or "").strip() or None
        current_task = str(assessment.get("current_task") or "").strip() or None

        if disposition not in DISPOSITIONS:
            failures.append(f"DISPOSITION_INVALID:{step}:{disposition or 'EMPTY'}")
        else:
            disposition_counts[disposition] += 1
            if horizon in by_horizon:
                by_horizon[horizon][disposition] += 1

        if disposition in {"SATISFIED", "SUPERSEDED"} and not evidence_refs:
            failures.append(f"EVIDENCE_REQUIRED:{step}:{disposition}")
        if disposition == "RESIDUAL" and not current_task:
            failures.append(f"CURRENT_TASK_REQUIRED:{step}")
        if disposition == "HOLD" and not (reason or evidence_refs):
            failures.append(f"HOLD_REASON_REQUIRED:{step}")

        row = {
            "step": step,
            "horizon": horizon,
            "source_text": str(action.get("text") or ""),
            "disposition": disposition or None,
            "evidence_refs": evidence_refs,
            "reason": reason,
            "current_task": current_task,
        }
        rows.append(row)

        if disposition == "RESIDUAL" and current_task:
            candidates.append(
                {
                    "source_step": step,
                    "horizon": horizon,
                    "task": current_task,
                    "evidence_refs": evidence_refs,
                    "standing": "ROUTING_CANDIDATE_NOT_SCHED_READY",
                    "claim_authority": False,
                    "execution_authority": False,
                }
            )

    source_horizon_counts = {
        tag: sum(1 for value in tags if value == tag)
        for tag in ("I", "M", "L")
    }
    classified_horizon_counts = {
        tag: sum(by_horizon[tag].values())
        for tag in ("I", "M", "L")
    }
    if source_horizon_counts != {"I": 4, "M": 3, "L": 3}:
        failures.append("SOURCE_433_COVERAGE_INVALID")
    if classified_horizon_counts != source_horizon_counts:
        failures.append("CLASSIFICATION_433_COVERAGE_INVALID")

    hold_steps = [row["step"] for row in rows if row["disposition"] == "HOLD"]
    current_state_digest = _digest(dict(current_state))
    source_bundle_digest = str(source_validation.get("source_bundle_digest") or "")

    if failures or hold_steps:
        status = "HOLD"
        next_mode = "REHYDRATE_OR_RESOLVE_HOLD"
        next_pulse = None
    elif pulse_index == 100:
        status = "RESEED_REQUIRED"
        next_mode = "REHYDRATE_NEWEST_GIT_AND_RESEED"
        next_pulse = None
    elif candidates:
        status = "COMPILED"
        next_mode = "ROUTE_CURRENT_RESIDUALS"
        next_pulse = pulse_index
    elif disposition_counts["DEFERRED"]:
        status = "PULSE_DEFERRED"
        next_mode = "ADVANCE_PULSE_WITH_RESERVE"
        next_pulse = pulse_index + 1
    else:
        status = "PULSE_SATISFIED"
        next_mode = "ADVANCE_PULSE"
        next_pulse = pulse_index + 1

    work_order = {
        "artifact": WORK_ORDER_ARTIFACT,
        "status": status,
        "pulse_index": pulse_index,
        "source_bundle_digest": source_bundle_digest,
        "current_state_digest": current_state_digest,
        "candidates": candidates,
        "candidate_count": len(candidates),
        "authority": {
            "standing": "ROUTING_ONLY",
            "sched_ready": False,
            "claim_authority": False,
            "execution_authority": False,
        },
    }

    result = {
        "artifact": ARTIFACT,
        "status": status,
        "failures": failures,
        "pulse_index": pulse_index,
        "step_start": expected_start or None,
        "step_end": expected_start + 9 if expected_start else None,
        "source_bundle_digest": source_bundle_digest,
        "current_state": {
            key: current_state.get(key)
            for key in REQUIRED_CURRENT_STATE
        },
        "current_state_digest": current_state_digest,
        "assessments": rows,
        "coverage": {
            "source_horizon_counts": source_horizon_counts,
            "classified_horizon_counts": classified_horizon_counts,
            "disposition_counts": disposition_counts,
            "by_horizon": by_horizon,
        },
        "hold_steps": hold_steps,
        "work_order": work_order,
        "mission_complete": False,
        "next": {
            "mode": next_mode,
            "pulse_index": next_pulse,
            "rehydrate_before_consequential_action": True,
        },
        "laws": [
            "HISTORICAL_PULSE != CURRENT_EXECUTABLE_QUEUE",
            "ASSESSMENT != EXECUTION_AUTHORITY",
            "ROUTING_CANDIDATE != SCHED_READY",
            "SOURCE_DIGEST_MUST_MATCH_FRESH_VALIDATION",
            "SATISFIED_OR_SUPERSEDED_REQUIRES_EVIDENCE",
            "ALL_4I_3M_3L_POSITIONS_REQUIRE_ACCOUNTING",
            "PULSE_100 != MISSION_COMPLETE",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }
    result["compilation_digest"] = _digest(
        {key: value for key, value in result.items() if key != "compilation_digest"}
    )
    return result
