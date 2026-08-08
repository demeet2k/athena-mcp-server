from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rehydration_loop import RehydrationLoopRuntime, _state_digest
from .rehydration_successor import SUCCESSOR_TOOLS
from .rehydration_terminal import evaluate_terminal_request

ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.PREVIEW.MEMBRANE.V1"


def _preview_hold(status: str, *, loop_id: str, remote_sync: dict, detail: dict | None = None) -> dict:
    return {
        "artifact": ARTIFACT,
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


def install_successor_preview_membrane(runtime_cls=RehydrationLoopRuntime, successor_tools=None) -> None:
    """Make standalone successor preview obey shared freshness and terminal closure law.

    The lower SuccessorCompiler intentionally remains a pure routing primitive. This
    membrane is the runtime-facing contract: it synchronizes shared Git before a
    preview, rejects stale state digests, and applies the same terminal closure gate
    used by mutating advance before delegating to the lower compiler.
    """

    if getattr(runtime_cls, "_athena_successor_preview_membrane_v1_registered", False):
        return

    original_call = runtime_cls.call_tool

    def call_tool_with_preview_membrane(self, name: str, a: dict):
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
        current_digest = state.get("state_digest")
        actual_digest = _state_digest(state)
        expected_digest = a["expected_state_digest"]
        if actual_digest != current_digest:
            return _preview_hold(
                "TAMPERED_SUCCESSOR_PREVIEW_STATE_HOLD",
                loop_id=loop_id,
                remote_sync=remote_sync,
                detail={
                    "expected_state_digest": expected_digest,
                    "stored_state_digest": current_digest,
                    "computed_state_digest": actual_digest,
                },
            )
        if expected_digest != current_digest:
            return _preview_hold(
                "STALE_SUCCESSOR_PREVIEW",
                loop_id=loop_id,
                remote_sync=remote_sync,
                detail={
                    "expected_state_digest": expected_digest,
                    "current_state_digest": current_digest,
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
        # Runtime-only membrane arguments are not part of the lower compiler API.
        forwarded.pop("remote", None)
        forwarded.pop("shared_remote_mode", None)
        result = original_call(self, name, forwarded)
        if not isinstance(result, dict):
            return result

        result["preview_membrane"] = ARTIFACT
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

    runtime_cls.call_tool = call_tool_with_preview_membrane
    runtime_cls._athena_successor_preview_membrane_v1_registered = True

    tools = SUCCESSOR_TOOLS if successor_tools is None else successor_tools
    for tool in tools:
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
