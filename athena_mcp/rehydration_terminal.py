from __future__ import annotations

from typing import Any

from .rehydration_loop import REHYDRATION_TOOLS, RehydrationLoopRuntime

ARTIFACT = "ATHENA.REHYDRATION.TERMINAL.GATE.V1"


def _nonempty_text(value: Any) -> str:
    return str(value or "").strip()


def _nonempty_list(value: Any) -> list:
    return list(value) if isinstance(value, list) else []


def evaluate_terminal_request(runtime: RehydrationLoopRuntime, loop_id: str, completion: dict) -> dict:
    """Evaluate a terminal request as a closure claim, never as self-authenticating truth."""

    state, _ = runtime._read_state(loop_id)
    reasons: list[str] = []

    if str(completion.get("status") or "").upper() != "SUCCEEDED":
        reasons.append("TERMINAL_STATUS_NOT_SUCCEEDED")
    if completion.get("hard_hold"):
        reasons.append("HARD_HOLD_IS_NOT_SUCCESSFUL_CLOSURE")

    residuals = [row for row in _nonempty_list(completion.get("residuals")) if _nonempty_text(row)]
    if residuals:
        reasons.append("KNOWN_RESIDUAL_WORK_REMAINS")
    if _nonempty_text(completion.get("next_task")):
        reasons.append("NEXT_TASK_DECLARED")
    if _nonempty_list(completion.get("successor_candidates")):
        reasons.append("SUCCESSOR_CANDIDATES_REMAIN")

    tests = _nonempty_list(completion.get("tests"))
    if not tests:
        reasons.append("NO_TERMINAL_TEST_WITNESS")
    else:
        nonpass = [
            str(row.get("name") or "unnamed")
            for row in tests
            if not isinstance(row, dict) or str(row.get("status") or "").upper() != "PASS"
        ]
        if nonpass:
            reasons.append("NONPASS_TERMINAL_TESTS:" + ",".join(nonpass))

    evidence = completion.get("terminal_evidence")
    if not isinstance(evidence, dict):
        reasons.append("TERMINAL_EVIDENCE_MISSING")
        evidence = {}
    else:
        if evidence.get("goal_satisfied") is not True:
            reasons.append("GOAL_SATISFACTION_NOT_WITNESSED")
        if evidence.get("remaining_material_work") is not False:
            reasons.append("NO_REMAINING_WORK_NOT_WITNESSED")
        if not _nonempty_text(evidence.get("reason")):
            reasons.append("TERMINAL_REASON_MISSING")
        refs = [x for x in _nonempty_list(evidence.get("evidence_refs")) if _nonempty_text(x)]
        if not refs:
            reasons.append("TERMINAL_EVIDENCE_REFS_MISSING")

    stop_conditions = [_nonempty_text(x) for x in _nonempty_list(state.get("stop_conditions")) if _nonempty_text(x)]
    stop_results = _nonempty_list(completion.get("stop_results"))
    result_by_condition: dict[str, dict] = {}
    malformed = False
    for row in stop_results:
        if not isinstance(row, dict):
            malformed = True
            continue
        condition = _nonempty_text(row.get("condition"))
        if not condition or condition in result_by_condition:
            malformed = True
            continue
        result_by_condition[condition] = row
    if malformed:
        reasons.append("STOP_RESULTS_MALFORMED_OR_DUPLICATED")

    if stop_conditions:
        missing = [condition for condition in stop_conditions if condition not in result_by_condition]
        unexpected = [condition for condition in result_by_condition if condition not in stop_conditions]
        failed = [
            condition
            for condition in stop_conditions
            if condition in result_by_condition
            and (
                str(result_by_condition[condition].get("status") or "").upper() != "PASS"
                or not _nonempty_text(result_by_condition[condition].get("evidence_ref"))
            )
        ]
        if missing:
            reasons.append("STOP_CONDITIONS_UNWITNESSED:" + "|".join(missing))
        if unexpected:
            reasons.append("UNDECLARED_STOP_RESULTS:" + "|".join(unexpected))
        if failed:
            reasons.append("STOP_CONDITIONS_NOT_PASSED:" + "|".join(failed))
    elif stop_results:
        reasons.append("STOP_RESULTS_WITHOUT_DECLARED_CONDITIONS")

    accepted = not reasons
    return {
        "artifact": ARTIFACT,
        "status": "ACCEPTED" if accepted else "REJECTED_CONTINUE",
        "requested_terminal": True,
        "reasons": reasons,
        "declared_stop_conditions": stop_conditions,
        "observed_stop_results": stop_results,
        "terminal_evidence": evidence,
        "laws": [
            "TERMINAL_REQUEST != TERMINAL_VERDICT",
            "KNOWN_RESIDUAL => CONTINUE",
            "STOP_CONDITION_TEXT != OBSERVED_STOP_WITNESS",
            "REJECTED_TERMINAL => SELF_STEER_SUCCESSOR_NOT_HUMAN_REENTRY",
        ],
    }


def install_terminal_gate(runtime_cls=RehydrationLoopRuntime, tool_list=None) -> None:
    """Install fail-closed terminal gating around the already-composed advance path."""

    if getattr(runtime_cls, "_athena_terminal_gate_v1_registered", False):
        return

    original_advance = runtime_cls.advance

    def advance_with_terminal_gate(self, *args, **kwargs):
        completion = dict(kwargs.get("completion") or {})
        loop_id = kwargs.get("loop_id") if "loop_id" in kwargs else args[0] if args else None
        gate = None
        if completion.get("terminal"):
            if not loop_id:
                raise ValueError("loop_id is required for terminal closure evaluation")
            gate = evaluate_terminal_request(self, loop_id, completion)
            completion["terminal_gate"] = gate
            if gate["status"] != "ACCEPTED":
                # Demote the kill request into a continuation request before the
                # successor compiler sees it. This preserves residual candidates
                # and eliminates human re-entry caused solely by premature stop.
                completion["terminal"] = False
                completion["self_steer"] = True
            kwargs["completion"] = completion

        result = original_advance(self, *args, **kwargs)
        if gate is not None:
            result["terminal_gate"] = gate
            result["terminal_request_accepted"] = gate["status"] == "ACCEPTED"
        return result

    runtime_cls.advance = advance_with_terminal_gate
    runtime_cls._athena_terminal_gate_v1_registered = True

    tools = REHYDRATION_TOOLS if tool_list is None else tool_list
    for tool in tools:
        if tool.get("name") != "athena_rehydration_advance":
            continue
        completion = (((tool.get("inputSchema") or {}).get("properties") or {}).get("completion") or {})
        props = completion.setdefault("properties", {})
        props.setdefault("terminal_evidence", {
            "type": "object",
            "description": "Required when terminal=true: witnessed goal satisfaction, no remaining material work, reason, and evidence refs.",
        })
        props.setdefault("stop_results", {
            "type": "array",
            "items": {"type": "object"},
            "description": "When the loop declares stop_conditions, terminal=true requires one PASS result with evidence_ref for each exact condition.",
        })
        if "terminal" in props:
            props["terminal"]["description"] = (
                "Closure request only. COMPLETE is granted only by the witnessed terminal gate; known residuals, next tasks, "
                "successor candidates, non-PASS tests, missing terminal evidence, or unwitnessed stop conditions force continuation."
            )
