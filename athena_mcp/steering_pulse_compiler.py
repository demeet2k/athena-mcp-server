from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

PULSE_ARTIFACT = "ATHENA.STEERING.LEDGER.PULSE.V1"
COMPILED_ARTIFACT = "ATHENA.STEERING.PULSE.COMPILED.V1"
COORDINATE_ARTIFACT = "ATHENA.LIMINAL.OPERATIONAL.COORDINATE.V1"
DELTA_ARTIFACT = "ATHENA.LIMINAL.OPERATIONAL.DELTA.V1"
PARENT_LIMINAL_SCHEMA = "ATHENA.LIMINAL.RUNTIME.v1"
CAMPAIGN_PROJECTION = "CAMPAIGN_V3_LOSSY_PROJECTION"

DISPOSITIONS = {"SATISFIED", "SUPERSEDED", "DEFERRED", "RESIDUAL", "HOLD"}
EXPECTED_TAGS = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
COORDINATE_AXES = (
    "git_head",
    "prompt_digest",
    "frontier_digest",
    "operational_basis_digest",
    "issue_pressure_digest",
    "source_bundle_digest",
    "pulse_index",
    "phase",
    "authority",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _nonempty(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def make_liminal_coordinate(
    *,
    navigator_id: str,
    git_head: str,
    prompt_digest: str,
    frontier_digest: str,
    operational_basis_digest: str,
    issue_pressure_digest: str,
    source_bundle_digest: str,
    pulse_index: int,
    phase: str,
    authority: str,
) -> dict[str, Any]:
    """Build public operational telemetry for a campaign position.

    This coordinate is intentionally categorical. It reports only observable,
    caller-supplied state identities. It is not physical location, hidden model
    state, or private reasoning telemetry.
    """
    axes = {
        "git_head": _nonempty(git_head, "git_head"),
        "prompt_digest": _nonempty(prompt_digest, "prompt_digest"),
        "frontier_digest": _nonempty(frontier_digest, "frontier_digest"),
        "operational_basis_digest": _nonempty(
            operational_basis_digest, "operational_basis_digest"
        ),
        "issue_pressure_digest": _nonempty(
            issue_pressure_digest, "issue_pressure_digest"
        ),
        "source_bundle_digest": _nonempty(
            source_bundle_digest, "source_bundle_digest"
        ),
        "pulse_index": int(pulse_index),
        "phase": _nonempty(phase, "phase").upper(),
        "authority": _nonempty(authority, "authority").upper(),
    }
    if not 1 <= axes["pulse_index"] <= 100:
        raise ValueError("pulse_index must be in 1..100")

    coordinate_digest = _sha(axes)
    return {
        "artifact": COORDINATE_ARTIFACT,
        "coordinate_id": "LC-" + coordinate_digest[:20],
        "coordinate_digest": coordinate_digest,
        "navigator_id": _nonempty(navigator_id, "navigator_id"),
        "axes": axes,
        "metric": "CATEGORICAL_HAMMING",
        "parent_chart": {
            "schema": PARENT_LIMINAL_SCHEMA,
            "relationship": CAMPAIGN_PROJECTION,
        },
        "standing": "PUBLIC_OPERATIONAL_TELEMETRY_ONLY",
        "laws": [
            "COORDINATE != PRIVATE_REASONING",
            "MOVEMENT != PHYSICAL_LOCATION",
            "DIGEST_IDENTITY != AUTHORITY",
            "ROUTING_COORDINATE != EXECUTION_AUTHORITY",
            "GIT_STATE != WORLD_TRUTH",
            "UNKNOWN != ZERO",
            "CAMPAIGN_COORDINATE != FULL_PARENT_LIMINAL_TUPLE",
            "PROJECTION_LOSS_MUST_REMAIN_EXPLICIT",
        ],
    }


def liminal_delta(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    """Measure exact categorical movement between two public coordinates."""
    if previous.get("artifact") != COORDINATE_ARTIFACT:
        raise ValueError("previous is not a liminal coordinate")
    if current.get("artifact") != COORDINATE_ARTIFACT:
        raise ValueError("current is not a liminal coordinate")

    before = previous.get("axes") or {}
    after = current.get("axes") or {}
    changed = [
        axis for axis in COORDINATE_AXES if before.get(axis) != after.get(axis)
    ]
    return {
        "artifact": DELTA_ARTIFACT,
        "from_coordinate_id": previous.get("coordinate_id"),
        "to_coordinate_id": current.get("coordinate_id"),
        "changed_axes": changed,
        "hamming_distance": len(changed),
        "stationary": not changed,
        "standing": "OBSERVED_PUBLIC_AXIS_DELTA",
        "laws": [
            "NO_AXIS_CHANGE => NO_LIMINAL_MOVEMENT",
            "NAVIGATOR_LABEL_CHANGE_ALONE != POSITION_CHANGE",
        ],
    }


def _validate_pulse_bundle(pulse: Mapping[str, Any]) -> list[dict[str, Any]]:
    if pulse.get("artifact") != PULSE_ARTIFACT:
        raise ValueError("pulse artifact mismatch")
    actions = list(pulse.get("actions") or [])
    if len(actions) != 10:
        raise ValueError("pulse must contain exactly 10 actions")

    start = int(pulse.get("step_start") or actions[0].get("step") or 0)
    expected_steps = list(range(start, start + 10))
    steps = [int(row.get("step") or 0) for row in actions]
    tags = [str(row.get("tag") or "") for row in actions]
    if steps != expected_steps:
        raise ValueError("pulse action sequence is not contiguous")
    if tags != EXPECTED_TAGS:
        raise ValueError("pulse horizon pattern must be exactly 4I/3M/3L")
    if not all(str(row.get("text") or "").strip() for row in actions):
        raise ValueError("pulse action text must be non-empty")
    if int(pulse.get("step_end") or 0) != expected_steps[-1]:
        raise ValueError("pulse step_end mismatch")
    return actions


def _assessment_map(
    assessments: Iterable[Mapping[str, Any]], expected_steps: set[int]
) -> dict[int, Mapping[str, Any]]:
    out: dict[int, Mapping[str, Any]] = {}
    for row in assessments:
        step = int(row.get("step") or 0)
        if step in out:
            raise ValueError(f"duplicate assessment for step {step}")
        out[step] = row
    missing = sorted(expected_steps - set(out))
    unexpected = sorted(set(out) - expected_steps)
    if missing:
        raise ValueError("missing assessments: " + ",".join(map(str, missing)))
    if unexpected:
        raise ValueError("unexpected assessments: " + ",".join(map(str, unexpected)))
    return out


def compile_current_pulse(
    *,
    pulse: Mapping[str, Any],
    assessments: Iterable[Mapping[str, Any]],
    navigator_id: str,
    git_head: str,
    prompt_digest: str,
    frontier_digest: str,
    operational_basis_digest: str,
    issue_pressure_digest: str,
    source_bundle_digest: str,
    authority: str = "ROUTING_ONLY",
) -> dict[str, Any]:
    """Compile historical steering pressure into current-state routing state.

    The caller must independently assess every historical action against current
    evidence. This compiler never infers SCHED READY, ownership, claim state, or
    execution authority from ledger prose.
    """
    actions = _validate_pulse_bundle(pulse)
    pulse_index = int(pulse.get("pulse_index") or 0)
    expected_steps = {int(row["step"]) for row in actions}
    by_step = _assessment_map(assessments, expected_steps)

    compiled_actions: list[dict[str, Any]] = []
    horizon = {
        tag: {
            "total": 0,
            "SATISFIED": 0,
            "SUPERSEDED": 0,
            "DEFERRED": 0,
            "RESIDUAL": 0,
            "HOLD": 0,
        }
        for tag in ("I", "M", "L")
    }

    for action in actions:
        step = int(action["step"])
        tag = str(action["tag"])
        assessment = by_step[step]
        disposition = str(assessment.get("disposition") or "").upper()
        if disposition not in DISPOSITIONS:
            raise ValueError(
                f"invalid disposition for step {step}: {disposition or '<empty>'}"
            )
        reason = _nonempty(assessment.get("reason"), f"assessment[{step}].reason")
        evidence_refs = [
            _nonempty(ref, f"assessment[{step}].evidence_ref")
            for ref in (assessment.get("evidence_refs") or [])
        ]
        current_target = assessment.get("current_target")
        if current_target is not None:
            current_target = _nonempty(
                current_target, f"assessment[{step}].current_target"
            )

        horizon[tag]["total"] += 1
        horizon[tag][disposition] += 1
        compiled_actions.append(
            {
                "step": step,
                "horizon": tag,
                "historical_text": str(action["text"]),
                "disposition": disposition,
                "reason": reason,
                "evidence_refs": evidence_refs,
                "current_target": current_target,
            }
        )

    holds = [row for row in compiled_actions if row["disposition"] == "HOLD"]
    residuals = [
        {
            "step": row["step"],
            "horizon": row["horizon"],
            "current_target": row["current_target"],
            "reason": row["reason"],
            "evidence_refs": row["evidence_refs"],
            "status": "CANDIDATE_ONLY",
            "execution_authority": "HOLD_UNLESS_SEPARATELY_ESTABLISHED_BY_CURRENT_RUNTIME",
        }
        for row in compiled_actions
        if row["disposition"] == "RESIDUAL"
    ]

    coordinate = make_liminal_coordinate(
        navigator_id=navigator_id,
        git_head=git_head,
        prompt_digest=prompt_digest,
        frontier_digest=frontier_digest,
        operational_basis_digest=operational_basis_digest,
        issue_pressure_digest=issue_pressure_digest,
        source_bundle_digest=source_bundle_digest,
        pulse_index=pulse_index,
        phase="CURRENT_STATE_COMPILED",
        authority=authority,
    )

    if holds:
        status = "COMPILED_WITH_HOLDS"
    elif residuals:
        status = "RESIDUALS_IDENTIFIED"
    else:
        status = "NO_CURRENT_RESIDUAL_IN_THIS_PULSE"

    packet = {
        "artifact": COMPILED_ARTIFACT,
        "status": status,
        "pulse_index": pulse_index,
        "step_start": int(pulse["step_start"]),
        "step_end": int(pulse["step_end"]),
        "source_comment_id": int(pulse["source_comment_id"]),
        "source_body_digest": _nonempty(
            pulse.get("source_body_digest"), "source_body_digest"
        ),
        "source_bundle_digest": _nonempty(
            source_bundle_digest, "source_bundle_digest"
        ),
        "compiled_actions": compiled_actions,
        "horizon_accounting": horizon,
        "residual_candidates": residuals,
        "holds": [
            {
                "step": row["step"],
                "reason": row["reason"],
                "evidence_refs": row["evidence_refs"],
            }
            for row in holds
        ],
        "liminal_coordinate": coordinate,
        "standing": "CURRENT_STATE_ROUTING_PACKET_NOT_EXECUTION_AUTHORITY",
        "laws": [
            "HISTORICAL_ACTION != CURRENT_WORK",
            "CURRENT_ASSESSMENT_REQUIRED_FOR_EVERY_ACTION",
            "PULSE_COMPILATION != SCHED_READY",
            "RESIDUAL != CLAIM",
            "ISSUE_PRESSURE != EXECUTION_AUTHORITY",
            "COORDINATE != PRIVATE_REASONING",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }
    packet["packet_digest"] = _sha(packet)
    return packet
