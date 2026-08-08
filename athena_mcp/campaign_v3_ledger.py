from __future__ import annotations

import hashlib
import json
import re
from typing import Any

LEDGER_ARTIFACT = "ATHENA.CAMPAIGN.V3.LEDGER.SOURCE.V1"
PULSE_ARTIFACT = "ATHENA.CAMPAIGN.V3.PULSE.COMPILATION.V1"
SOURCE_ISSUE = 177
VERIFICATION_ISSUE = 185
LEDGER_COMMENTS = 10
PULSE_COUNT = 100
ACTIONS_PER_PULSE = 10
HORIZON_COUNTS = {"I": 4, "M": 3, "L": 3}
ACTION_STATES = {"SATISFIED", "SUPERSEDED", "RESIDUAL", "HOLD"}

_STEP_RE = re.compile(r"(?m)^(\d{4})\s+`\[([IML])\]`\s+(.+?)\s*$")
_LEDGER_HEADER_RE = re.compile(r"LEDGER\s+(\d+)/10\s+[^\n]*?(\d{4})[–-](\d{4})", re.IGNORECASE)


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _comment_id(comment: dict) -> int:
    value = comment.get("id")
    if isinstance(value, int) and value > 0:
        return value
    url = str(comment.get("url") or "")
    match = re.search(r"issuecomment-(\d+)", url)
    if match:
        return int(match.group(1))
    raise ValueError("ledger comment requires a durable comment id")


def _expected_horizon(step: int) -> str:
    pos = ((int(step) - 1) % ACTIONS_PER_PULSE) + 1
    if pos <= 4:
        return "I"
    if pos <= 7:
        return "M"
    return "L"


def _parse_comment(comment: dict, ledger_index: int) -> dict:
    body = str(comment.get("body") or "")
    comment_id = _comment_id(comment)
    header = _LEDGER_HEADER_RE.search(body)
    expected_start = (ledger_index - 1) * 100 + 1
    expected_end = ledger_index * 100
    if not header:
        raise ValueError(f"ledger {ledger_index} header missing")
    if (int(header.group(1)), int(header.group(2)), int(header.group(3))) != (
        ledger_index,
        expected_start,
        expected_end,
    ):
        raise ValueError(f"ledger {ledger_index} header/range mismatch")

    actions: list[dict] = []
    for match in _STEP_RE.finditer(body):
        step = int(match.group(1))
        horizon = match.group(2)
        text = match.group(3).strip()
        if horizon != _expected_horizon(step):
            raise ValueError(f"step {step:04d} violates 4I/3M/3L grammar")
        actions.append({"step": step, "horizon": horizon, "text": text})

    expected_steps = list(range(expected_start, expected_end + 1))
    actual_steps = [row["step"] for row in actions]
    if actual_steps != expected_steps:
        raise ValueError(f"ledger {ledger_index} action sequence is not exact contiguous range")

    return {
        "ledger_index": ledger_index,
        "comment_id": comment_id,
        "url": comment.get("url"),
        "body_digest": _sha(body),
        "step_start": expected_start,
        "step_end": expected_end,
        "actions": actions,
    }


def compile_verified_ledger_source(
    ledger_comments: list[dict],
    verification_comment: dict,
    *,
    source_issue: int = SOURCE_ISSUE,
    verification_issue: int = VERIFICATION_ISSUE,
) -> dict:
    """Compile the verified #177 steering ledger into a source-bound curriculum object.

    The returned object is routing/curriculum state only. It cannot grant SCHED READY,
    claim ownership, provider authority, or execution permission.
    """
    if int(source_issue) != SOURCE_ISSUE or int(verification_issue) != VERIFICATION_ISSUE:
        raise ValueError("unexpected campaign ledger source identity")
    if len(ledger_comments) != LEDGER_COMMENTS:
        raise ValueError("exactly ten ledger comments are required")

    verification_body = str(verification_comment.get("body") or "")
    verification_id = _comment_id(verification_comment)
    if "LEDGER_VERIFIED=PASS" not in verification_body.replace(" ", ""):
        raise ValueError("verification receipt does not establish LEDGER_VERIFIED=PASS")
    if "LEDGER_EXECUTED" not in verification_body or "CAMPAIGN_SUCCESS" not in verification_body:
        raise ValueError("verification receipt must preserve execution/success distinction")

    parsed = [_parse_comment(comment, index) for index, comment in enumerate(ledger_comments, start=1)]
    all_actions = [action for block in parsed for action in block["actions"]]
    steps = [row["step"] for row in all_actions]
    if steps != list(range(1, 1001)):
        raise ValueError("ledger must be exactly contiguous from 0001 through 1000")

    pulses: list[dict] = []
    for pulse_index in range(1, PULSE_COUNT + 1):
        start = (pulse_index - 1) * ACTIONS_PER_PULSE + 1
        chunk = all_actions[start - 1 : start - 1 + ACTIONS_PER_PULSE]
        counts = {h: sum(1 for row in chunk if row["horizon"] == h) for h in HORIZON_COUNTS}
        if counts != HORIZON_COUNTS:
            raise ValueError(f"pulse {pulse_index} violates horizon coverage")
        pulses.append(
            {
                "pulse_index": pulse_index,
                "step_start": start,
                "step_end": start + 9,
                "horizon_coverage": counts,
                "actions": chunk,
            }
        )

    source = {
        "artifact": LEDGER_ARTIFACT,
        "source_issue": SOURCE_ISSUE,
        "verification_issue": VERIFICATION_ISSUE,
        "verification_comment_id": verification_id,
        "verification_body_digest": _sha(verification_body),
        "ledger_comment_ids": [row["comment_id"] for row in parsed],
        "ledger_comment_body_digests": [row["body_digest"] for row in parsed],
        "pulse_count": PULSE_COUNT,
        "actions_per_pulse": ACTIONS_PER_PULSE,
        "action_count": 1000,
        "horizon_totals": {"I": 400, "M": 300, "L": 300},
        "pulse_horizon_coverage": HORIZON_COUNTS,
        "pulses": pulses,
        "execution_authority": "NOT_DERIVED_FROM_LEDGER",
        "laws": [
            "LEDGER_VERIFIED != LEDGER_EXECUTED",
            "LEDGER_EXECUTED != CAMPAIGN_SUCCESS",
            "ISSUE_PRESSURE != SCHED_READY",
            "LEDGER_ACTION != EXECUTION_AUTHORIZATION",
            "PRIVATE_CHAIN_OF_THOUGHT != CAMPAIGN_TELEMETRY",
        ],
    }
    source["ledger_digest"] = _sha({k: v for k, v in source.items() if k != "ledger_digest"})
    return source


def compile_current_pulse(
    ledger_source: dict,
    pulse_index: int,
    *,
    current_coordinates: dict,
    action_states: dict[int | str, str] | None = None,
    operational_basis: dict | None = None,
) -> dict:
    """Project one historical pulse into current routing state without granting authority."""
    if ledger_source.get("artifact") != LEDGER_ARTIFACT:
        raise ValueError("invalid ledger source artifact")
    expected_digest = _sha({k: v for k, v in ledger_source.items() if k != "ledger_digest"})
    if ledger_source.get("ledger_digest") != expected_digest:
        raise ValueError("stale or tampered ledger source")
    pulse_index = int(pulse_index)
    if not 1 <= pulse_index <= PULSE_COUNT:
        raise ValueError("pulse_index must be 1..100")
    if not isinstance(current_coordinates, dict) or not current_coordinates.get("git_head"):
        raise ValueError("current git_head coordinate is required")

    source_pulse = ledger_source["pulses"][pulse_index - 1]
    states = action_states or {}
    actions: list[dict] = []
    status_counts = {h: {state: 0 for state in ACTION_STATES} for h in HORIZON_COUNTS}
    for historical in source_pulse["actions"]:
        raw_state = states.get(historical["step"], states.get(str(historical["step"]), "RESIDUAL"))
        state = str(raw_state).upper()
        if state not in ACTION_STATES:
            raise ValueError(f"invalid action state for step {historical['step']:04d}")
        row = dict(historical)
        row["current_state"] = state
        row["history_preserved"] = True
        actions.append(row)
        status_counts[row["horizon"]][state] += 1

    residual_steps = [row["step"] for row in actions if row["current_state"] == "RESIDUAL"]
    hold_steps = [row["step"] for row in actions if row["current_state"] == "HOLD"]
    basis_status = "UNAVAILABLE"
    basis_digest = None
    if isinstance(operational_basis, dict):
        basis_status = str(operational_basis.get("status") or "PRESENT")
        basis_digest = operational_basis.get("basis_digest")

    holds: list[str] = []
    if residual_steps and operational_basis is None:
        holds.append("OPERATIONAL_BASIS_UNAVAILABLE_HOLD")
    if hold_steps:
        holds.append("PULSE_ACTION_HOLD")

    result = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": ledger_source["ledger_digest"],
        "source_issue": ledger_source["source_issue"],
        "verification_issue": ledger_source["verification_issue"],
        "pulse_index": pulse_index,
        "step_start": source_pulse["step_start"],
        "step_end": source_pulse["step_end"],
        "historical_horizon_coverage": dict(source_pulse["horizon_coverage"]),
        "current_status_counts": status_counts,
        "actions": actions,
        "residual_steps": residual_steps,
        "hold_steps": hold_steps,
        "current_coordinates": dict(current_coordinates),
        "operational_basis_status": basis_status,
        "operational_basis_digest": basis_digest,
        "execution_authorized": False,
        "authority_resolution_required": bool(residual_steps),
        "holds": holds,
        "must_reseed_from_then_current_state": pulse_index == 100,
        "mission_complete_claim_allowed": False,
        "laws": [
            "HISTORICAL_ACTION != CURRENT_READY_WORK",
            "SATISFIED/SUPERSEDED != ERASED_HISTORY",
            "OPERATIONAL_BASIS != EXECUTION_AUTHORITY",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }
    result["pulse_digest"] = _sha({k: v for k, v in result.items() if k != "pulse_digest"})
    return result
