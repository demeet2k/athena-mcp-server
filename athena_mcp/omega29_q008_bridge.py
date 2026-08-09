"""Fail-closed Ω29 V2 to Q008 continuation bridge.

The bridge recomputes Ω29 from its original packet and caller-supplied
contexts. It preserves the exact Q008 input state and cursor. It cannot execute
a transition, consume a packet, advance a cursor, admit evidence, close Q008,
or perform provider mutations.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from . import omega29_operate as omega

BRIDGE_SCHEMA = "ATHENA.OMEGA29.Q008.BRIDGE.V2"
TRANSITIONS = {"CONTINUE", "RETRY", "REBIND", "REPAIR", "ROLLBACK", "REPLAN", "HOLD", "ESCALATE", "COMPLETE"}
TERMINAL_INPUTS = {"CHECKPOINT_CONTINUE", "READY_TO_CLOSE", "REJECTED_EARLY_EXIT", "BLOCKED_EXTERNAL", "HOST_CUTOFF_PENDING"}
PACKETS = {
    "SOURCE_BINDING_MISMATCH": "P03", "OBSERVATION_STALE": "P03",
    "CLOCK_INVERSION": "P16", "RECEIPT_BINDING_MISMATCH": "P15",
    "RECEIPT_RESULT_MISMATCH": "P15", "RUNTIME_INCIDENT": "P16",
    "POSTCONDITION_FAILED": "P17", "PLAN_EXECUTION_DIVERGENCE": "P07",
    "EXECUTION_WORLD_DIVERGENCE": "P09", "PLAN_WORLD_DIVERGENCE": "P07",
    "NONE": "P21",
}
DECISION_KEYS = {
    "schema", "transition", "incident", "residuals", "reason",
    "source_binding_digest", "runtime_context_digest", "packet_digest",
    "source_freshness_claim", "claim_ceiling", "authority", "admission",
    "promotion", "external_effects", "decision_digest",
}
INCIDENT_TRANSITIONS = {
    "NONE": {"CONTINUE", "COMPLETE", "HOLD"},
    "SOURCE_BINDING_MISMATCH": {"REBIND", "HOLD"},
    "OBSERVATION_STALE": {"REBIND", "HOLD"},
    "CLOCK_INVERSION": {"HOLD"},
    "RECEIPT_BINDING_MISMATCH": {"REPAIR", "HOLD"},
    "RECEIPT_RESULT_MISMATCH": {"REPAIR", "HOLD"},
    "RUNTIME_INCIDENT": {"RETRY", "ESCALATE", "HOLD"},
    "POSTCONDITION_FAILED": {"ROLLBACK", "REPAIR", "HOLD"},
    "PLAN_EXECUTION_DIVERGENCE": {"REPLAN", "HOLD"},
    "EXECUTION_WORLD_DIVERGENCE": {"REPAIR", "HOLD"},
    "PLAN_WORLD_DIVERGENCE": {"REPLAN", "HOLD"},
}

class BridgeRejected(ValueError):
    pass

def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def _identifier(value: Any, name: str) -> str:
    if type(value) is not str or not value:
        raise BridgeRejected(f"{name} must be a non-empty string")
    return value

def bridge(
    *, omega_packet: dict[str, Any], source_binding: dict[str, Any],
    runtime_context: dict[str, Any], omega_decision: dict[str, Any],
    q008_terminal: str, terminal_attempt: bool, cursor: dict[str, Any],
    run_id: str, invocation_id: str,
) -> dict[str, Any]:
    run_id = _identifier(run_id, "run_id")
    invocation_id = _identifier(invocation_id, "invocation_id")
    if type(terminal_attempt) is not bool:
        raise BridgeRejected("terminal_attempt must be a boolean")
    if type(omega_decision) is not dict or set(omega_decision) != DECISION_KEYS:
        raise BridgeRejected("Omega29 decision shape is not closed")
    try:
        expected = omega.decide(omega_packet, source_binding=source_binding, runtime_context=runtime_context)
    except omega.OperateRejected as exc:
        raise BridgeRejected(f"Omega29 inputs rejected: {exc}") from exc
    if omega_decision != expected:
        raise BridgeRejected("Omega29 decision does not equal reducer recomputation")
    if source_binding.get("run_id") != run_id or source_binding.get("invocation_id") != invocation_id:
        raise BridgeRejected("source binding run/invocation mismatch")
    if runtime_context.get("run_id") != run_id or runtime_context.get("invocation_id") != invocation_id:
        raise BridgeRejected("runtime context run/invocation mismatch")
    if omega_packet.get("run_id") != run_id or omega_packet.get("invocation_id") != invocation_id:
        raise BridgeRejected("Omega29 packet run/invocation mismatch")

    transition = omega_decision["transition"]
    incident = omega_decision["incident"]
    residuals = omega_decision["residuals"]
    if transition not in TRANSITIONS or incident not in PACKETS or transition not in INCIDENT_TRANSITIONS[incident]:
        raise BridgeRejected("unknown or incompatible transition/incident")
    if q008_terminal not in TERMINAL_INPUTS:
        raise BridgeRejected("Q008 terminal input is not an admitted local state")
    if q008_terminal == "READY_TO_CLOSE" and not terminal_attempt:
        raise BridgeRejected("READY_TO_CLOSE requires an explicit terminal attempt")
    if type(cursor) is not dict or set(cursor) != {"invocation_index", "segment_index", "checkpoint_index"}:
        raise BridgeRejected("cursor must contain three exact axes")
    for key, value in cursor.items():
        if type(value) is not int or value < 0:
            raise BridgeRejected(f"cursor {key} must be a non-negative integer")
    if q008_terminal == "READY_TO_CLOSE" and (
        transition != "COMPLETE" or incident != "NONE" or any(residuals.values())
    ):
        raise BridgeRejected("Q008 cannot be ready without coherent Omega29 COMPLETE")

    operation_body = {
        "run_id": run_id, "invocation_id": invocation_id,
        "source_decision_digest": omega_decision["decision_digest"],
        "q008_input_state": q008_terminal, "terminal_attempt": terminal_attempt,
        "cursor": dict(cursor),
    }
    result = {
        "schema": BRIDGE_SCHEMA,
        "run_id": run_id, "invocation_id": invocation_id,
        "omega_transition": transition, "omega_incident": incident,
        "q008_input_state": q008_terminal, "q008_state": q008_terminal,
        "terminal_attempt": terminal_attempt, "cursor": dict(cursor),
        "ready_packet": PACKETS[incident],
        "consumption_state": "PENDING_IDEMPOTENT_CONSUMER",
        "consume_inside_same_invocation": False,
        "operation_id": digest(operation_body),
        "exit_permit": False, "success": False, "mass_orchestration": False,
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD",
        "external_mutations": 0,
        "source_binding_digest": omega_decision["source_binding_digest"],
        "runtime_context_digest": omega_decision["runtime_context_digest"],
        "source_packet_digest": omega_decision["packet_digest"],
        "source_decision_digest": omega_decision["decision_digest"],
    }
    result["bridge_digest"] = digest(result)
    return result
