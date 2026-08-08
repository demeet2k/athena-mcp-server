from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rehydration_loop import REHYDRATION_TOOLS, RehydrationLoopRuntime, _state_digest

ARTIFACT = "ATHENA.REHYDRATION.TERMINAL.GATE.V1"
PREVIEW_ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.PREVIEW.MEMBRANE.V1"


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


def _preview_hold(status: str, *, loop_id: str, remote_sync: dict, detail: dict | None = None) -> dict:
    return {
        "artifact": PREVIEW_ARTIFACT,
        "status": status,
        "loop_id": loop_id,
        "selected": None,
        "candidates": [],
        "ties": [],
        "shared_frontier_verified": bool(remote_sync.get("shared_frontier_verified")),
        "remote_sync": remote_sync,
        "requires_rehydrate": True,
        "detail": dict(detail or {}),
        "laws": [
            "SUCCESSOR_PREVIEW != EXECUTION_AUTHORITY",
            "LOCAL_PREVIEW_STATE != SHARED_CURRENT_STATE",
            "STALE_PREVIEW => REHYDRATE_BEFORE_ROUTING",
            "TERMINAL_REQUEST != TERMINAL_VERDICT",
        ],
    }


def install_terminal_gate(runtime_cls=RehydrationLoopRuntime, tool_list=None) -> None:
    """Install fail-closed terminal gating and the standalone preview membrane."""

    if getattr(runtime_cls, "_athena_terminal_gate_v1_registered", False):
        return

    original_advance = runtime_cls.advance
    original_call = runtime_cls.call_tool

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

    def call_tool_with_terminal_preview_membrane(self, name: str, a: dict):
        if name != "athena_rehydration_successor_preview":
            return original_call(self, name, a)

        loop_id = a["loop_id"]
        remote = a.get("remote", "origin")
        mode = self._remote_mode(a.get("shared_remote_mode", "REQUIRED"))
        if mode == "DISABLED":
            remote_sync = {
                "status": "DISABLED",
                "remote": remote,
                "shared_frontier_verified": False,
            }
        else:
            remote_sync = self.remote_sync.sync(remote)
            if mode == "REQUIRED" and not remote_sync.get("shared_frontier_verified"):
                return _preview_hold(
                    "REHYDRATION_SUCCESSOR_PREVIEW_SHARED_FRONTIER_HOLD",
                    loop_id=loop_id,
                    remote_sync=remote_sync,
                    detail={"law": "LOCAL_PREVIEW_STATE != SHARED_CURRENT_STATE"},
                )

        state, paths = self._read_state(loop_id)
        stored_digest = state.get("state_digest")
        computed_digest = _state_digest(state)
        expected_digest = a["expected_state_digest"]
        if stored_digest != computed_digest:
            return _preview_hold(
                "TAMPERED_SUCCESSOR_PREVIEW_STATE_HOLD",
                loop_id=loop_id,
                remote_sync=remote_sync,
                detail={
                    "expected_state_digest": expected_digest,
                    "stored_state_digest": stored_digest,
                    "computed_state_digest": computed_digest,
                },
            )
        if expected_digest != stored_digest:
            return _preview_hold(
                "STALE_SUCCESSOR_PREVIEW",
                loop_id=loop_id,
                remote_sync=remote_sync,
                detail={
                    "expected_state_digest": expected_digest,
                    "current_state_digest": stored_digest,
                    "current_step_index": state.get("step_index"),
                    "checkpoint_head": self._path_last_commit(paths["state"]),
                },
            )

        completion = deepcopy(a.get("completion")) if isinstance(a.get("completion"), dict) else a.get("completion")
        terminal_gate = None
        if isinstance(completion, dict) and completion.get("terminal"):
            terminal_gate = evaluate_terminal_request(self, loop_id, completion)
            completion["terminal_gate"] = terminal_gate
            if terminal_gate["status"] != "ACCEPTED":
                completion["terminal"] = False
                completion["self_steer"] = True

        forwarded = dict(a)
        forwarded["completion"] = completion
        forwarded.pop("remote", None)
        forwarded.pop("shared_remote_mode", None)
        result = original_call(self, name, forwarded)
        if not isinstance(result, dict):
            return result

        result["preview_membrane"] = PREVIEW_ARTIFACT
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "SUCCESSOR_PREVIEW_SYNC_SHARED_GIT_BEFORE_ROUTING"
        result["closure_law"] = "SUCCESSOR_PREVIEW_APPLIES_TERMINAL_GATE_BEFORE_COMPILER"
        result["preview_verification"] = (
            "SHARED_CURRENT"
            if result["shared_frontier_verified"]
            else "LOCAL_ONLY_UNVERIFIED"
            if mode == "DISABLED"
            else "BEST_EFFORT_UNVERIFIED"
        )
        if terminal_gate is not None:
            result["terminal_gate"] = terminal_gate
            result["terminal_request_accepted"] = terminal_gate["status"] == "ACCEPTED"
        laws = list(result.get("laws") or [])
        for law in (
            "SUCCESSOR_PREVIEW != EXECUTION_AUTHORITY",
            "STALE_PREVIEW => REHYDRATE_BEFORE_ROUTING",
            "TERMINAL_REQUEST != TERMINAL_VERDICT",
        ):
            if law not in laws:
                laws.append(law)
        result["laws"] = laws
        return result

    runtime_cls.advance = advance_with_terminal_gate
    runtime_cls.call_tool = call_tool_with_terminal_preview_membrane
    runtime_cls._athena_terminal_gate_v1_registered = True
    runtime_cls._athena_successor_preview_membrane_v1_registered = True

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

    # Successor tools are registered after this extension is installed. Mutate the
    # additive preview schema in-place without introducing a second tool namespace.
    try:
        from .rehydration_successor import SUCCESSOR_TOOLS
    except ImportError:
        SUCCESSOR_TOOLS = []
    for tool in SUCCESSOR_TOOLS:
        if tool.get("name") != "athena_rehydration_successor_preview":
            continue
        tool["description"] = (
            "Fresh-sync shared Git, verify the exact current loop state digest, apply the same witnessed terminal-closure "
            "gate used by advance, then compile a replayable routing-only successor baton. Stale or unverified shared state "
            "fails closed by default; ties remain preserved."
        )
        schema = tool.setdefault("inputSchema", {"type": "object", "properties": {}})
        props = schema.setdefault("properties", {})
        props.setdefault("shared_remote_mode", {
            "type": "string",
            "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"],
            "description": "Default REQUIRED. DISABLED is local-only and never claims shared-current preview state.",
        })
        props.setdefault("remote", {"type": "string"})
        completion = props.setdefault("completion", {"type": ["object", "null"]})
        completion["description"] = (
            "Observed completion candidate. terminal=true is only a closure request; the runtime preview membrane applies "
            "the witnessed terminal gate before the lower successor compiler may return TERMINAL."
        )
