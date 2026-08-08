from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .common import KernelError, parse_time, require_nonempty_string, require_positive_int, require_safe_id
from .reducer import reduce_events

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


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def event_path(run_id: str, sequence: int) -> str:
    """Return the provider-atomic journal key for one event sequence.

    Sequence owns the fixed path.  `event_id` intentionally does not participate
    in the path because `events/<sequence>-<event_id>.json` permits two different
    writers to create different files carrying the same sequence.
    """

    safe_run = require_safe_id(run_id, "event.run_id")
    seq = require_positive_int(sequence, "event.sequence")
    return f"runtime/runs/{safe_run}/events/{seq:08d}.json"


def validate_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if set(event) != EVENT_KEYS:
        missing = sorted(EVENT_KEYS - set(event))
        extra = sorted(set(event) - EVENT_KEYS)
        raise KernelError(f"event: exact keys required; missing={missing}; extra={extra}")
    if event["schema_version"] != "EVENT_V1":
        raise KernelError("event.schema_version: expected EVENT_V1")
    require_nonempty_string(event["event_id"], "event.event_id")
    require_positive_int(event["sequence"], "event.sequence")
    require_safe_id(event["run_id"], "event.run_id")
    if event["event_type"] not in EVENT_TYPES:
        raise KernelError(f"event.event_type: unsupported value {event['event_type']!r}")
    parse_time(event["at"], "event.at")
    if event["node_id"] is not None:
        require_safe_id(event["node_id"], "event.node_id")
    if not isinstance(event["data"], Mapping):
        raise KernelError("event.data: expected object")
    return {
        "schema_version": "EVENT_V1",
        "event_id": event["event_id"],
        "sequence": event["sequence"],
        "run_id": event["run_id"],
        "event_type": event["event_type"],
        "at": event["at"],
        "node_id": event["node_id"],
        "data": dict(event["data"]),
    }


def make_event(
    *,
    event_id: str,
    sequence: int,
    run_id: str,
    event_type: str,
    at: str,
    node_id: str | None = None,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "schema_version": "EVENT_V1",
        "event_id": event_id,
        "sequence": sequence,
        "run_id": run_id,
        "event_type": event_type,
        "at": at,
        "node_id": node_id,
        "data": dict(data or {}),
    }
    return validate_event(event)


def ordered_events(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    validated = [validate_event(event) for event in events]
    validated.sort(key=lambda event: event["sequence"])
    seen_sequences: set[int] = set()
    seen_ids: set[str] = set()
    for expected, event in enumerate(validated, start=1):
        sequence = event["sequence"]
        if sequence in seen_sequences:
            raise KernelError(f"event stream: duplicate sequence {sequence}")
        if event["event_id"] in seen_ids:
            raise KernelError(f"event stream: duplicate event_id {event['event_id']!r}")
        if sequence != expected:
            raise KernelError(f"event stream: expected sequence {expected}, found {sequence}")
        seen_sequences.add(sequence)
        seen_ids.add(event["event_id"])
    return validated


def next_sequence(events: Iterable[Mapping[str, Any]]) -> int:
    return len(ordered_events(events)) + 1


def stream_digest(events: Iterable[Mapping[str, Any]]) -> str:
    return sha256_json(ordered_events(events))


def provider_create_packet(path: str, content: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    return {
        "provider_operation": "CREATE_FILE_IF_ABSENT",
        "kind": kind,
        "path": path,
        "content": dict(content),
        "content_text": json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
    }


def prepare_event_append(
    *,
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate an append by replaying the existing reducer before provider write."""

    current = ordered_events(events)
    candidate = validate_event(event)
    if candidate["run_id"] != run.get("run_id"):
        raise KernelError("event append: run_id mismatch")
    expected_sequence = len(current) + 1
    if candidate["sequence"] != expected_sequence:
        raise KernelError(
            f"event append: stale sequence; expected {expected_sequence}, found {candidate['sequence']}"
        )
    if any(existing["event_id"] == candidate["event_id"] for existing in current):
        raise KernelError(f"event append: event_id already exists: {candidate['event_id']}")

    before = reduce_events(run, current) if current else None
    after = reduce_events(run, [*current, candidate])
    path = event_path(candidate["run_id"], candidate["sequence"])
    return {
        "status": "EVENT_APPEND_PREPARED",
        "run_id": candidate["run_id"],
        "sequence": candidate["sequence"],
        "event_id": candidate["event_id"],
        "event_type": candidate["event_type"],
        "basis_stream_digest": stream_digest(current),
        "result_stream_digest": stream_digest([*current, candidate]),
        "projection_before": before,
        "projection_after": after,
        "provider": provider_create_packet(path, candidate, kind="EVENT_V1"),
        "law": "EVENT_APPEND_PREPARED != EVENT_PERSISTED; provider create-if-absent owns the sequence-CAS boundary",
    }


def classify_event_provider_result(prepared: Mapping[str, Any], provider_status: str) -> dict[str, Any]:
    status = require_nonempty_string(provider_status, "event.provider_status").upper()
    if status in {"CREATED", "SUCCESS", "COMMITTED"}:
        return {
            "status": "EVENT_PERSISTED",
            "event_id": prepared["event_id"],
            "sequence": prepared["sequence"],
            "path": prepared["provider"]["path"],
            "result_stream_digest": prepared["result_stream_digest"],
        }
    if status in {"EXISTS", "ALREADY_EXISTS", "CONFLICT"}:
        return {
            "status": "EVENT_SEQUENCE_COLLISION_REHYDRATE",
            "event_id": prepared["event_id"],
            "sequence": prepared["sequence"],
            "path": prepared["provider"]["path"],
            "law": "sequence path collision is not success; rehydrate and recompute the next lawful event",
        }
    return {
        "status": "EVENT_PROVIDER_HOLD",
        "provider_status": status,
        "event_id": prepared["event_id"],
        "sequence": prepared["sequence"],
        "path": prepared["provider"]["path"],
    }
