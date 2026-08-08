from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from .common import KernelError, parse_time, require_exact_keys, require_nonempty_string, require_positive_int, require_safe_id

EVENT_KEYS = {
    "schema_version",
    "event_id",
    "sequence",
    "run_id",
    "event_type",
    "at",
    "node_id",
    "data",
}
EVENT_TYPES = {
    "RUN_CREATED",
    "RUN_ADMITTED",
    "NODE_READY",
    "CLAIM_ACQUIRED",
    "ACTION_ATTEMPTED",
    "CHECKPOINT_WRITTEN",
    "RECEIPT_WRITTEN",
    "NODE_SUCCEEDED",
    "NODE_FAILED",
    "NODE_HELD",
    "RUN_COMMITTED",
    "RUN_PARTIAL_HOLD",
    "RUN_BLOCKED",
    "RUN_ABORTED",
    "AUDIT_WRITTEN",
}
TERMINAL_RUN_STATES = {"COMMITTED", "PARTIAL_HOLD", "BLOCKED", "ABORTED"}


def validate_event(event: Mapping[str, Any]) -> dict[str, Any]:
    require_exact_keys(event, EVENT_KEYS, "event")
    if event["schema_version"] != "EVENT_V1":
        raise KernelError("event.schema_version: expected EVENT_V1")
    require_safe_id(event["event_id"], "event.event_id")
    require_positive_int(event["sequence"], "event.sequence")
    require_safe_id(event["run_id"], "event.run_id")
    if event["event_type"] not in EVENT_TYPES:
        raise KernelError("event.event_type: unsupported value")
    parse_time(event["at"], "event.at")
    if event["node_id"] is not None:
        require_safe_id(event["node_id"], "event.node_id")
    if not isinstance(event["data"], Mapping):
        raise KernelError("event.data: expected object")
    return deepcopy(dict(event))


def reduce_events(run: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Reduce append-only events into one deterministic run projection."""

    if not events:
        raise KernelError("events: empty stream")
    node_specs = {str(node["node_id"]): node for node in run["nodes"]}
    node_states = {node_id: "PENDING" for node_id in node_specs}
    attempts = {node_id: 0 for node_id in node_specs}
    receipts = {node_id: False for node_id in node_specs}
    checkpoints = {node_id: 0 for node_id in node_specs}
    claims: dict[str, str] = {}
    event_ids: set[str] = set()
    run_state = "ABSENT"
    audited = False
    last_time = None

    for expected_sequence, raw_event in enumerate(events, start=1):
        event = validate_event(raw_event)
        if event["sequence"] != expected_sequence:
            raise KernelError(
                f"event.sequence: expected contiguous {expected_sequence}, got {event['sequence']}"
            )
        if event["event_id"] in event_ids:
            raise KernelError(f"event.event_id: duplicate {event['event_id']}")
        event_ids.add(event["event_id"])
        if event["run_id"] != run["run_id"]:
            raise KernelError("event.run_id: run identity mismatch")
        event_time = parse_time(event["at"], "event.at")
        if last_time is not None and event_time < last_time:
            raise KernelError("event.at: timestamps must be nondecreasing")
        last_time = event_time
        event_type = event["event_type"]
        node_id = event["node_id"]
        data = event["data"]

        if run_state in TERMINAL_RUN_STATES and event_type != "AUDIT_WRITTEN":
            raise KernelError("events: non-audit event after terminal run state")

        if event_type == "RUN_CREATED":
            if expected_sequence != 1 or run_state != "ABSENT" or node_id is not None:
                raise KernelError("RUN_CREATED: must be first and run-scoped")
            run_state = "QUEUED"
            continue

        if event_type == "RUN_ADMITTED":
            if run_state != "QUEUED" or node_id is not None:
                raise KernelError("RUN_ADMITTED: requires QUEUED run")
            if data.get("verdict") != "PASS":
                raise KernelError("RUN_ADMITTED: verdict must be PASS")
            run_state = "ADMITTED"
            continue

        if event_type in {
            "NODE_READY",
            "CLAIM_ACQUIRED",
            "ACTION_ATTEMPTED",
            "CHECKPOINT_WRITTEN",
            "RECEIPT_WRITTEN",
            "NODE_SUCCEEDED",
            "NODE_FAILED",
            "NODE_HELD",
        }:
            if run_state not in {"ADMITTED", "RUNNING", "VERIFYING", "READY_TO_COMMIT"}:
                raise KernelError(f"{event_type}: run is not active")
            if node_id not in node_specs:
                raise KernelError(f"{event_type}: unknown node {node_id}")
            current = node_states[str(node_id)]
            node = node_specs[str(node_id)]

            if event_type == "NODE_READY":
                if current != "PENDING":
                    raise KernelError("NODE_READY: node must be PENDING")
                missing = [
                    dependency
                    for dependency in node["depends_on"]
                    if node_states[str(dependency)] != "SUCCEEDED"
                ]
                if missing:
                    raise KernelError(f"NODE_READY: unsatisfied dependencies {missing}")
                node_states[str(node_id)] = "READY"
                run_state = "RUNNING"

            elif event_type == "CLAIM_ACQUIRED":
                if current != "READY":
                    raise KernelError("CLAIM_ACQUIRED: node must be READY")
                expected_path = node["claim_path"]
                if data.get("claim_path") != expected_path:
                    raise KernelError("CLAIM_ACQUIRED: claim path mismatch")
                if expected_path in claims.values():
                    raise KernelError("CLAIM_ACQUIRED: duplicate claim path")
                claims[str(node_id)] = expected_path
                node_states[str(node_id)] = "CLAIMED"

            elif event_type == "ACTION_ATTEMPTED":
                if current not in {"CLAIMED", "CHECKPOINTED"}:
                    raise KernelError("ACTION_ATTEMPTED: node must be CLAIMED or CHECKPOINTED")
                attempts[str(node_id)] += 1
                if attempts[str(node_id)] > int(node["max_attempts"]):
                    raise KernelError("ACTION_ATTEMPTED: node attempt ceiling exceeded")
                node_states[str(node_id)] = "RUNNING"

            elif event_type == "CHECKPOINT_WRITTEN":
                if current != "RUNNING":
                    raise KernelError("CHECKPOINT_WRITTEN: node must be RUNNING")
                require_nonempty_string(data.get("checkpoint_ref"), "event.data.checkpoint_ref")
                checkpoints[str(node_id)] += 1
                node_states[str(node_id)] = "CHECKPOINTED"

            elif event_type == "RECEIPT_WRITTEN":
                if current not in {"RUNNING", "CHECKPOINTED"}:
                    raise KernelError("RECEIPT_WRITTEN: node must be RUNNING or CHECKPOINTED")
                if receipts[str(node_id)]:
                    raise KernelError("RECEIPT_WRITTEN: duplicate node receipt")
                require_nonempty_string(data.get("receipt_ref"), "event.data.receipt_ref")
                receipts[str(node_id)] = True

            elif event_type == "NODE_SUCCEEDED":
                if current not in {"RUNNING", "CHECKPOINTED"}:
                    raise KernelError("NODE_SUCCEEDED: node must be RUNNING or CHECKPOINTED")
                if not receipts[str(node_id)]:
                    raise KernelError("NODE_SUCCEEDED: receipt required before success")
                node_states[str(node_id)] = "SUCCEEDED"

            elif event_type == "NODE_FAILED":
                if current not in {"CLAIMED", "RUNNING", "CHECKPOINTED"}:
                    raise KernelError("NODE_FAILED: invalid source state")
                node_states[str(node_id)] = "FAILED"

            elif event_type == "NODE_HELD":
                if current not in {"READY", "CLAIMED", "RUNNING", "CHECKPOINTED"}:
                    raise KernelError("NODE_HELD: invalid source state")
                node_states[str(node_id)] = "HELD"

            if all(state == "SUCCEEDED" for state in node_states.values()):
                run_state = "READY_TO_COMMIT"
            elif any(
                node_specs[item]["role_capability"] in {"verifier", "adversary", "committer", "auditor"}
                and state in {"READY", "CLAIMED", "RUNNING", "CHECKPOINTED", "SUCCEEDED"}
                for item, state in node_states.items()
            ):
                run_state = "VERIFYING"
            continue

        if event_type == "RUN_COMMITTED":
            if node_id is not None or run_state != "READY_TO_COMMIT":
                raise KernelError("RUN_COMMITTED: all nodes must have succeeded")
            require_nonempty_string(data.get("artifact_ref"), "event.data.artifact_ref")
            require_nonempty_string(data.get("artifact_sha256"), "event.data.artifact_sha256")
            run_state = "COMMITTED"
            continue

        if event_type == "RUN_PARTIAL_HOLD":
            if node_id is not None or run_state not in {"ADMITTED", "RUNNING", "VERIFYING"}:
                raise KernelError("RUN_PARTIAL_HOLD: invalid source state")
            require_nonempty_string(data.get("first_divergence"), "event.data.first_divergence")
            run_state = "PARTIAL_HOLD"
            continue

        if event_type == "RUN_BLOCKED":
            if node_id is not None or run_state not in {"ADMITTED", "RUNNING", "VERIFYING"}:
                raise KernelError("RUN_BLOCKED: invalid source state")
            require_nonempty_string(data.get("first_divergence"), "event.data.first_divergence")
            run_state = "BLOCKED"
            continue

        if event_type == "RUN_ABORTED":
            if node_id is not None or run_state not in {"QUEUED", "ADMITTED", "RUNNING", "VERIFYING"}:
                raise KernelError("RUN_ABORTED: invalid source state")
            run_state = "ABORTED"
            continue

        if event_type == "AUDIT_WRITTEN":
            if node_id is not None or run_state not in TERMINAL_RUN_STATES or audited:
                raise KernelError("AUDIT_WRITTEN: requires one unaudited terminal run")
            require_nonempty_string(data.get("audit_ref"), "event.data.audit_ref")
            audited = True
            continue

    return {
        "run_id": run["run_id"],
        "run_state": run_state,
        "audited": audited,
        "node_states": node_states,
        "attempts": attempts,
        "receipt_written": receipts,
        "checkpoint_counts": checkpoints,
        "claim_paths": claims,
        "event_count": len(events),
        "last_event_id": events[-1]["event_id"],
    }
