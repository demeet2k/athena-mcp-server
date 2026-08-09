"""Pure Q008 invocation-identity closure compiler.

This candidate binds one downstream Q008 consumer transition to a fresh consumer
invocation without consuming the Ω29 bridge inside its source invocation. It
constructs digest-bound cursor, event, terminal receipt, abort-set, optional
provider-observation receipt, and a closure receipt. It performs no external
I/O, provider calls, admission, promotion, scheduling, or canonical mutation.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

BRIDGE_SCHEMA = "ATHENA.OMEGA29.Q008.BRIDGE.V2"
ENVELOPE_SCHEMA = "ATHENA.Q008.CONSUMER.ENVELOPE.V1"
CURSOR_SCHEMA = "ATHENA.Q008.CURSOR.V3"
EVENT_SCHEMA = "ATHENA.Q008.EVENT.V2"
RECEIPT_SCHEMA = "ATHENA.Q008.RECEIPT.V2"
ABORT_SET_SCHEMA = "ATHENA.Q008.ABORT_SET.V2"
PROVIDER_RECEIPT_SCHEMA = "ATHENA.Q008.PROVIDER_RECEIPT.V2"
CLOSURE_SCHEMA = "ATHENA.Q008.IDENTITY.CLOSURE.RECEIPT.V1"

BRIDGE_KEYS = {
    "schema", "run_id", "invocation_id", "omega_transition", "omega_incident",
    "q008_input_state", "q008_state", "terminal_attempt", "cursor",
    "ready_packet", "consumption_state", "consume_inside_same_invocation",
    "operation_id", "exit_permit", "success", "mass_orchestration",
    "authority", "admission", "promotion", "external_mutations",
    "source_binding_digest", "runtime_context_digest", "source_packet_digest",
    "source_decision_digest", "bridge_digest",
}
CURSOR_AXES = {"invocation_index", "segment_index", "checkpoint_index"}
CURSOR_MOVES = {"NONE", "CHECKPOINT", "SEGMENT"}
DECISIONS = {"CONTINUE", "HOLD", "ABORT", "COMPLETE_CANDIDATE", "PROVIDER_OBSERVED"}
EVENT_TYPES = {
    "CONSUMER_OPEN", "CHECKPOINT_RECORDED", "SEGMENT_ADVANCED",
    "ABORT_RECORDED", "PROVIDER_OBSERVED", "TERMINAL_CANDIDATE",
}
PROVIDER_STANDING = "CALLER_SUPPLIED_PROVIDER_OBSERVATION_UNVERIFIED_BY_Q008"
CLAIM_STANDING = ("NONE", "UNADMITTED", "HOLD", 0)

class Q008IdentityRejected(ValueError):
    pass

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def _obj(value: Any, name: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise Q008IdentityRejected(f"{name} must be an object")
    return dict(value)

def _str(value: Any, name: str) -> str:
    if type(value) is not str or not value:
        raise Q008IdentityRejected(f"{name} must be a non-empty string")
    return value

def _int(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise Q008IdentityRejected(f"{name} must be a non-negative integer")
    return value

def _zero(value: Any, name: str) -> int:
    if type(value) is not int or value != 0:
        raise Q008IdentityRejected(f"{name} must be exact integer zero")
    return value

def _bool(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise Q008IdentityRejected(f"{name} must be a boolean")
    return value

def _sha(value: Any, name: str) -> str:
    value = _str(value, name)
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise Q008IdentityRejected(f"{name} must be lowercase SHA-256")
    return value

def _closed(value: Mapping[str, Any], keys: set[str], name: str) -> None:
    if set(value) != keys:
        raise Q008IdentityRejected(f"{name} shape is not closed")

def _claim_ceiling(value: Mapping[str, Any], prefix: str) -> None:
    if (value.get("authority"), value.get("admission"), value.get("promotion")) != CLAIM_STANDING[:3]:
        raise Q008IdentityRejected(f"{prefix} expanded authority/admission/promotion")
    _zero(value.get("external_mutations"), f"{prefix}.external_mutations")

def _cursor_axes(value: Any, name: str) -> dict[str, int]:
    value = _obj(value, name)
    _closed(value, CURSOR_AXES, name)
    return {key: _int(value[key], f"{name}.{key}") for key in sorted(CURSOR_AXES)}

def validate_bridge(value: Any) -> dict[str, Any]:
    bridge = _obj(value, "bridge")
    _closed(bridge, BRIDGE_KEYS, "bridge")
    if bridge["schema"] != BRIDGE_SCHEMA:
        raise Q008IdentityRejected("bridge schema mismatch")
    body = dict(bridge); claimed = _sha(body.pop("bridge_digest"), "bridge.bridge_digest")
    if digest(body) != claimed:
        raise Q008IdentityRejected("bridge digest mismatch")
    _str(bridge["run_id"], "bridge.run_id")
    _str(bridge["invocation_id"], "bridge.invocation_id")
    _sha(bridge["operation_id"], "bridge.operation_id")
    _cursor_axes(bridge["cursor"], "bridge.cursor")
    if bridge["consumption_state"] != "PENDING_IDEMPOTENT_CONSUMER":
        raise Q008IdentityRejected("bridge is not pending consumer")
    if _bool(bridge["consume_inside_same_invocation"], "bridge.consume_inside_same_invocation"):
        raise Q008IdentityRejected("bridge illegally permits same-invocation consumption")
    for key in ("exit_permit", "success", "mass_orchestration"):
        if _bool(bridge[key], f"bridge.{key}"):
            raise Q008IdentityRejected(f"bridge {key} must remain false")
    _claim_ceiling(bridge, "bridge")
    for key in ("source_binding_digest", "runtime_context_digest", "source_packet_digest", "source_decision_digest"):
        _sha(bridge[key], f"bridge.{key}")
    return bridge

def _source_cursor_digest(bridge: Mapping[str, Any]) -> str:
    return digest({"run_id": bridge["run_id"], "invocation_id": bridge["invocation_id"], "operation_id": bridge["operation_id"], "cursor": bridge["cursor"]})

def open_consumer(bridge: Any, *, consumer_invocation_id: str) -> dict[str, Any]:
    bridge = validate_bridge(bridge)
    consumer_invocation_id = _str(consumer_invocation_id, "consumer_invocation_id")
    if consumer_invocation_id == bridge["invocation_id"]:
        raise Q008IdentityRejected("consumer invocation must differ from source bridge invocation")
    source_cursor = _cursor_axes(bridge["cursor"], "bridge.cursor")
    invocation_index = source_cursor["invocation_index"] + 1
    operation_body = {
        "source_bridge_digest": bridge["bridge_digest"], "source_operation_id": bridge["operation_id"],
        "source_invocation_id": bridge["invocation_id"], "run_id": bridge["run_id"],
        "invocation_id": consumer_invocation_id, "source_cursor_digest": _source_cursor_digest(bridge),
        "ready_packet": bridge["ready_packet"],
    }
    operation_id = digest(operation_body)
    cursor_body = {
        "schema": CURSOR_SCHEMA, "run_id": bridge["run_id"], "invocation_id": consumer_invocation_id,
        "operation_id": operation_id, "source_bridge_digest": bridge["bridge_digest"],
        "prior_cursor_digest": operation_body["source_cursor_digest"], "invocation_index": invocation_index,
        "segment_index": source_cursor["segment_index"], "checkpoint_index": source_cursor["checkpoint_index"],
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_mutations": 0,
    }
    cursor = {**cursor_body, "cursor_digest": digest(cursor_body)}
    envelope_body = {
        "schema": ENVELOPE_SCHEMA, "run_id": bridge["run_id"], "invocation_id": consumer_invocation_id,
        "operation_id": operation_id, "source_invocation_id": bridge["invocation_id"],
        "source_operation_id": bridge["operation_id"], "source_bridge_digest": bridge["bridge_digest"],
        "source_cursor_digest": operation_body["source_cursor_digest"], "initial_cursor_digest": cursor["cursor_digest"],
        "ready_packet": bridge["ready_packet"], "standing": "LOCAL_IDEMPOTENT_CONSUMER_CANDIDATE",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_mutations": 0,
    }
    return {**envelope_body, "envelope_digest": digest(envelope_body), "initial_cursor": cursor}

def _validate_envelope(value: Any) -> dict[str, Any]:
    envelope = _obj(value, "consumer_envelope")
    keys = {
        "schema", "run_id", "invocation_id", "operation_id", "source_invocation_id", "source_operation_id",
        "source_bridge_digest", "source_cursor_digest", "initial_cursor_digest", "ready_packet", "standing",
        "authority", "admission", "promotion", "external_mutations", "envelope_digest", "initial_cursor",
    }
    _closed(envelope, keys, "consumer_envelope")
    if envelope["schema"] != ENVELOPE_SCHEMA or envelope["standing"] != "LOCAL_IDEMPOTENT_CONSUMER_CANDIDATE":
        raise Q008IdentityRejected("consumer envelope schema/standing mismatch")
    for key in ("run_id", "invocation_id", "operation_id", "source_invocation_id", "source_operation_id", "ready_packet"):
        _str(envelope[key], f"consumer_envelope.{key}")
    for key in ("source_bridge_digest", "source_cursor_digest", "initial_cursor_digest"):
        _sha(envelope[key], f"consumer_envelope.{key}")
    if envelope["invocation_id"] == envelope["source_invocation_id"]:
        raise Q008IdentityRejected("consumer/source invocation alias")
    _claim_ceiling(envelope, "consumer_envelope")
    body = {k: envelope[k] for k in keys - {"envelope_digest", "initial_cursor"}}
    if envelope["envelope_digest"] != digest(body):
        raise Q008IdentityRejected("consumer envelope digest mismatch")
    cursor = validate_cursor(envelope["initial_cursor"], envelope=envelope)
    if cursor["cursor_digest"] != envelope["initial_cursor_digest"]:
        raise Q008IdentityRejected("initial cursor digest mismatch")
    return envelope

def validate_cursor(value: Any, *, envelope: Mapping[str, Any]) -> dict[str, Any]:
    cursor = _obj(value, "cursor")
    keys = {
        "schema", "run_id", "invocation_id", "operation_id", "source_bridge_digest", "prior_cursor_digest",
        "invocation_index", "segment_index", "checkpoint_index", "authority", "admission", "promotion",
        "external_mutations", "cursor_digest",
    }
    _closed(cursor, keys, "cursor")
    if cursor["schema"] != CURSOR_SCHEMA:
        raise Q008IdentityRejected("cursor schema mismatch")
    for key in ("run_id", "invocation_id", "operation_id"):
        if cursor[key] != envelope[key]:
            raise Q008IdentityRejected(f"cursor {key} mismatch")
    if cursor["invocation_index"] != envelope["initial_cursor"]["invocation_index"]:
        raise Q008IdentityRejected("cursor invocation index escaped consumer invocation")
    if cursor["segment_index"] < envelope["initial_cursor"]["segment_index"] or cursor["checkpoint_index"] < envelope["initial_cursor"]["checkpoint_index"]:
        raise Q008IdentityRejected("cursor regressed below consumer-open coordinates")
    if cursor["source_bridge_digest"] != envelope["source_bridge_digest"]:
        raise Q008IdentityRejected("cursor source bridge mismatch")
    _sha(cursor["prior_cursor_digest"], "cursor.prior_cursor_digest")
    for key in CURSOR_AXES:
        _int(cursor[key], f"cursor.{key}")
    _claim_ceiling(cursor, "cursor")
    body = {k: cursor[k] for k in keys - {"cursor_digest"}}
    if cursor["cursor_digest"] != digest(body):
        raise Q008IdentityRejected("cursor digest mismatch")
    return cursor

def advance_cursor(envelope: Any, cursor: Any, *, move: str) -> dict[str, Any]:
    envelope = _validate_envelope(envelope); cursor = validate_cursor(cursor, envelope=envelope)
    if move not in CURSOR_MOVES:
        raise Q008IdentityRejected("unknown cursor move")
    body = {k: deepcopy(cursor[k]) for k in cursor if k != "cursor_digest"}
    body["prior_cursor_digest"] = cursor["cursor_digest"]
    if move == "CHECKPOINT": body["checkpoint_index"] += 1
    elif move == "SEGMENT": body["segment_index"] += 1
    body["invocation_index"] = envelope["initial_cursor"]["invocation_index"]
    return {**body, "cursor_digest": digest(body)}

def make_event(envelope: Any, *, cursor_before: Any, cursor_after: Any, event_index: int, event_type: str, payload_digest: str) -> dict[str, Any]:
    envelope = _validate_envelope(envelope); before = validate_cursor(cursor_before, envelope=envelope); after = validate_cursor(cursor_after, envelope=envelope)
    event_index = _int(event_index, "event_index")
    if event_type not in EVENT_TYPES: raise Q008IdentityRejected("unknown event type")
    payload_digest = _sha(payload_digest, "payload_digest")
    if after["prior_cursor_digest"] != before["cursor_digest"]: raise Q008IdentityRejected("cursor transition does not chain")
    deltas = {"invocation": after["invocation_index"] - before["invocation_index"], "segment": after["segment_index"] - before["segment_index"], "checkpoint": after["checkpoint_index"] - before["checkpoint_index"]}
    if deltas["invocation"] != 0 or deltas["segment"] not in {0, 1} or deltas["checkpoint"] not in {0, 1}:
        raise Q008IdentityRejected("cursor transition is not bounded")
    if deltas["segment"] + deltas["checkpoint"] > 1: raise Q008IdentityRejected("cursor cannot advance segment and checkpoint together")
    event_body = {
        "schema": EVENT_SCHEMA, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"],
        "operation_id": envelope["operation_id"], "source_bridge_digest": envelope["source_bridge_digest"],
        "event_index": event_index, "event_type": event_type, "cursor_before_digest": before["cursor_digest"],
        "cursor_after_digest": after["cursor_digest"], "payload_digest": payload_digest,
        "standing": "LOCAL_Q008_EVENT_UNADMITTED", "authority": "NONE", "admission": "UNADMITTED",
        "promotion": "HOLD", "external_mutations": 0,
    }
    return {**event_body, "event_digest": digest(event_body)}

def validate_event(value: Any, *, envelope: Mapping[str, Any]) -> dict[str, Any]:
    event = _obj(value, "event")
    keys = {
        "schema", "run_id", "invocation_id", "operation_id", "source_bridge_digest", "event_index", "event_type",
        "cursor_before_digest", "cursor_after_digest", "payload_digest", "standing", "authority", "admission",
        "promotion", "external_mutations", "event_digest",
    }
    _closed(event, keys, "event")
    if event["schema"] != EVENT_SCHEMA or event["standing"] != "LOCAL_Q008_EVENT_UNADMITTED": raise Q008IdentityRejected("event schema/standing mismatch")
    for key in ("run_id", "invocation_id", "operation_id"):
        if event[key] != envelope[key]: raise Q008IdentityRejected(f"event {key} mismatch")
    if event["source_bridge_digest"] != envelope["source_bridge_digest"]: raise Q008IdentityRejected("event source bridge mismatch")
    _int(event["event_index"], "event.event_index")
    if event["event_type"] not in EVENT_TYPES: raise Q008IdentityRejected("unknown event type")
    for key in ("cursor_before_digest", "cursor_after_digest", "payload_digest"): _sha(event[key], f"event.{key}")
    _claim_ceiling(event, "event")
    body = {k: event[k] for k in keys - {"event_digest"}}
    if event["event_digest"] != digest(body): raise Q008IdentityRejected("event digest mismatch")
    return event

def make_receipt(envelope: Any, *, event: Any, cursor: Any, decision: str) -> dict[str, Any]:
    envelope = _validate_envelope(envelope); event = validate_event(event, envelope=envelope); cursor = validate_cursor(cursor, envelope=envelope)
    if decision not in DECISIONS: raise Q008IdentityRejected("unknown decision")
    if event["cursor_after_digest"] != cursor["cursor_digest"]: raise Q008IdentityRejected("receipt cursor is not event output")
    body = {
        "schema": RECEIPT_SCHEMA, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"],
        "operation_id": envelope["operation_id"], "source_bridge_digest": envelope["source_bridge_digest"],
        "event_digest": event["event_digest"], "cursor_digest": cursor["cursor_digest"], "decision": decision,
        "standing": "LOCAL_Q008_RECEIPT_UNADMITTED", "q008_completion_claim": "NOT_ESTABLISHED",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_mutations": 0,
    }
    return {**body, "receipt_digest": digest(body)}

def validate_receipt(value: Any, *, envelope: Mapping[str, Any]) -> dict[str, Any]:
    receipt = _obj(value, "receipt")
    keys = {
        "schema", "run_id", "invocation_id", "operation_id", "source_bridge_digest", "event_digest", "cursor_digest",
        "decision", "standing", "q008_completion_claim", "authority", "admission", "promotion", "external_mutations", "receipt_digest",
    }
    _closed(receipt, keys, "receipt")
    if receipt["schema"] != RECEIPT_SCHEMA or receipt["standing"] != "LOCAL_Q008_RECEIPT_UNADMITTED": raise Q008IdentityRejected("receipt schema/standing mismatch")
    if receipt["q008_completion_claim"] != "NOT_ESTABLISHED": raise Q008IdentityRejected("receipt fabricated completion claim")
    for key in ("run_id", "invocation_id", "operation_id"):
        if receipt[key] != envelope[key]: raise Q008IdentityRejected(f"receipt {key} mismatch")
    if receipt["source_bridge_digest"] != envelope["source_bridge_digest"]: raise Q008IdentityRejected("receipt source bridge mismatch")
    for key in ("event_digest", "cursor_digest"): _sha(receipt[key], f"receipt.{key}")
    if receipt["decision"] not in DECISIONS: raise Q008IdentityRejected("unknown receipt decision")
    _claim_ceiling(receipt, "receipt")
    body = {k: receipt[k] for k in keys - {"receipt_digest"}}
    if receipt["receipt_digest"] != digest(body): raise Q008IdentityRejected("receipt digest mismatch")
    return receipt

def make_abort_set(envelope: Any, aborts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    envelope = _validate_envelope(envelope)
    if type(aborts) not in (list, tuple): raise Q008IdentityRejected("aborts must be a sequence")
    rows=[]; seen=set()
    for index, raw in enumerate(aborts):
        item=_obj(raw, f"aborts[{index}]"); _closed(item, {"abort_id", "reason_code", "event_digest", "cursor_digest"}, f"aborts[{index}]")
        abort_id=_str(item["abort_id"], f"aborts[{index}].abort_id")
        if abort_id in seen: raise Q008IdentityRejected("duplicate abort_id")
        seen.add(abort_id)
        rows.append({
            "abort_id": abort_id, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"],
            "operation_id": envelope["operation_id"], "source_bridge_digest": envelope["source_bridge_digest"],
            "reason_code": _str(item["reason_code"], f"aborts[{index}].reason_code"),
            "event_digest": _sha(item["event_digest"], f"aborts[{index}].event_digest"),
            "cursor_digest": _sha(item["cursor_digest"], f"aborts[{index}].cursor_digest"),
        })
    rows=sorted(rows, key=lambda row: row["abort_id"])
    body={
        "schema": ABORT_SET_SCHEMA, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"],
        "operation_id": envelope["operation_id"], "source_bridge_digest": envelope["source_bridge_digest"],
        "aborts": rows, "standing": "LOCAL_ABORT_SET_UNADMITTED", "authority": "NONE", "admission": "UNADMITTED",
        "promotion": "HOLD", "external_mutations": 0,
    }
    return {**body, "abort_set_digest": digest(body)}

def validate_abort_set(value: Any, *, envelope: Mapping[str, Any]) -> dict[str, Any]:
    abort_set=_obj(value, "abort_set")
    keys={"schema","run_id","invocation_id","operation_id","source_bridge_digest","aborts","standing","authority","admission","promotion","external_mutations","abort_set_digest"}
    _closed(abort_set, keys, "abort_set")
    if abort_set["schema"] != ABORT_SET_SCHEMA or abort_set["standing"] != "LOCAL_ABORT_SET_UNADMITTED": raise Q008IdentityRejected("abort set schema/standing mismatch")
    for key in ("run_id","invocation_id","operation_id"):
        if abort_set[key] != envelope[key]: raise Q008IdentityRejected(f"abort set {key} mismatch")
    if abort_set["source_bridge_digest"] != envelope["source_bridge_digest"]: raise Q008IdentityRejected("abort set source bridge mismatch")
    if type(abort_set["aborts"]) is not list: raise Q008IdentityRejected("abort set rows must be list")
    ids=[]
    for i,row in enumerate(abort_set["aborts"]):
        row=_obj(row,f"abort_set.aborts[{i}]"); _closed(row,{"abort_id","run_id","invocation_id","operation_id","source_bridge_digest","reason_code","event_digest","cursor_digest"},f"abort row {i}")
        for key in ("run_id","invocation_id","operation_id"):
            if row[key] != envelope[key]: raise Q008IdentityRejected(f"abort row {key} mismatch")
        if row["source_bridge_digest"] != envelope["source_bridge_digest"]: raise Q008IdentityRejected("abort row source bridge mismatch")
        ids.append(_str(row["abort_id"],"abort_id")); _str(row["reason_code"],"reason_code"); _sha(row["event_digest"],"abort.event_digest"); _sha(row["cursor_digest"],"abort.cursor_digest")
    if ids != sorted(set(ids)): raise Q008IdentityRejected("abort rows not canonical unique order")
    _claim_ceiling(abort_set,"abort_set"); body={k:abort_set[k] for k in keys-{"abort_set_digest"}}
    if abort_set["abort_set_digest"] != digest(body): raise Q008IdentityRejected("abort set digest mismatch")
    return abort_set

def make_provider_receipt(envelope: Any, observation: Mapping[str, Any], *, event: Any, cursor: Any) -> dict[str, Any]:
    envelope=_validate_envelope(envelope); event=validate_event(event,envelope=envelope); cursor=validate_cursor(cursor,envelope=envelope)
    if event["cursor_after_digest"] != cursor["cursor_digest"]: raise Q008IdentityRejected("provider receipt cursor is not event output")
    observation=_obj(observation,"provider_observation"); _closed(observation,{"provider","provider_operation_id","observation_id","request_digest","observation_digest","observed_state"},"provider_observation")
    body={
        "schema": PROVIDER_RECEIPT_SCHEMA, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"],
        "operation_id": envelope["operation_id"], "source_bridge_digest": envelope["source_bridge_digest"],
        "event_digest": event["event_digest"], "cursor_digest": cursor["cursor_digest"],
        "provider": _str(observation["provider"],"provider"), "provider_operation_id": _str(observation["provider_operation_id"],"provider_operation_id"),
        "observation_id": _str(observation["observation_id"],"observation_id"), "request_digest": _sha(observation["request_digest"],"request_digest"),
        "observation_digest": _sha(observation["observation_digest"],"observation_digest"), "observed_state": _str(observation["observed_state"],"observed_state"),
        "standing": PROVIDER_STANDING, "provider_effect_claim": "NOT_ESTABLISHED_BY_Q008_IDENTITY_COMPILER",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_mutations": 0,
    }
    return {**body, "provider_receipt_digest": digest(body)}

def validate_provider_receipt(value: Any, *, envelope: Mapping[str, Any]) -> dict[str, Any]:
    receipt=_obj(value,"provider_receipt")
    keys={"schema","run_id","invocation_id","operation_id","source_bridge_digest","event_digest","cursor_digest","provider","provider_operation_id","observation_id","request_digest","observation_digest","observed_state","standing","provider_effect_claim","authority","admission","promotion","external_mutations","provider_receipt_digest"}
    _closed(receipt,keys,"provider_receipt")
    if receipt["schema"] != PROVIDER_RECEIPT_SCHEMA or receipt["standing"] != PROVIDER_STANDING: raise Q008IdentityRejected("provider receipt schema/standing mismatch")
    if receipt["provider_effect_claim"] != "NOT_ESTABLISHED_BY_Q008_IDENTITY_COMPILER": raise Q008IdentityRejected("provider receipt fabricated effect claim")
    for key in ("run_id","invocation_id","operation_id"):
        if receipt[key] != envelope[key]: raise Q008IdentityRejected(f"provider receipt {key} mismatch")
    if receipt["source_bridge_digest"] != envelope["source_bridge_digest"]: raise Q008IdentityRejected("provider receipt source bridge mismatch")
    for key in ("provider","provider_operation_id","observation_id","observed_state"): _str(receipt[key],f"provider_receipt.{key}")
    for key in ("event_digest","cursor_digest","request_digest","observation_digest"): _sha(receipt[key],f"provider_receipt.{key}")
    _claim_ceiling(receipt,"provider_receipt"); body={k:receipt[k] for k in keys-{"provider_receipt_digest"}}
    if receipt["provider_receipt_digest"] != digest(body): raise Q008IdentityRejected("provider receipt digest mismatch")
    return receipt

def validate_closure(*, envelope: Any, cursor: Any, event: Any, receipt: Any, abort_set: Any, provider_receipt: Any | None = None) -> dict[str, Any]:
    envelope=_validate_envelope(envelope); cursor=validate_cursor(cursor,envelope=envelope); event=validate_event(event,envelope=envelope); receipt=validate_receipt(receipt,envelope=envelope); abort_set=validate_abort_set(abort_set,envelope=envelope)
    provider=validate_provider_receipt(provider_receipt,envelope=envelope) if provider_receipt is not None else None
    if event["cursor_after_digest"] != cursor["cursor_digest"]: raise Q008IdentityRejected("closure cursor/event mismatch")
    if receipt["event_digest"] != event["event_digest"] or receipt["cursor_digest"] != cursor["cursor_digest"]: raise Q008IdentityRejected("closure receipt mismatch")
    for row in abort_set["aborts"]:
        if row["event_digest"] != event["event_digest"] or row["cursor_digest"] != cursor["cursor_digest"]: raise Q008IdentityRejected("abort row is not bound to closure event/cursor")
    if provider is not None and (provider["event_digest"] != event["event_digest"] or provider["cursor_digest"] != cursor["cursor_digest"]): raise Q008IdentityRejected("provider receipt is not bound to closure event/cursor")
    body={
        "schema": CLOSURE_SCHEMA, "run_id": envelope["run_id"], "invocation_id": envelope["invocation_id"], "operation_id": envelope["operation_id"],
        "source_invocation_id": envelope["source_invocation_id"], "source_bridge_digest": envelope["source_bridge_digest"], "envelope_digest": envelope["envelope_digest"],
        "cursor_digest": cursor["cursor_digest"], "event_digest": event["event_digest"], "receipt_digest": receipt["receipt_digest"], "abort_set_digest": abort_set["abort_set_digest"],
        "provider_receipt_digest": provider["provider_receipt_digest"] if provider else None, "identity_closed": True,
        "standing": "LOCAL_IDENTITY_CLOSURE_CANDIDATE", "q008_execution_claim": "NOT_ESTABLISHED", "provider_effect_claim": "NOT_ESTABLISHED",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_mutations": 0,
    }
    return {**body, "closure_digest": digest(body)}

def compile_transition(bridge: Any, *, consumer_invocation_id: str, move: str, event_index: int, event_type: str, payload_digest: str, decision: str, abort_reasons: Sequence[str] = (), provider_observation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    envelope=open_consumer(bridge,consumer_invocation_id=consumer_invocation_id); before=envelope["initial_cursor"]; after=advance_cursor(envelope,before,move=move)
    event=make_event(envelope,cursor_before=before,cursor_after=after,event_index=event_index,event_type=event_type,payload_digest=payload_digest); receipt=make_receipt(envelope,event=event,cursor=after,decision=decision)
    abort_rows=[{"abort_id":f"abort-{index:04d}","reason_code":_str(reason,f"abort_reasons[{index}]"),"event_digest":event["event_digest"],"cursor_digest":after["cursor_digest"]} for index,reason in enumerate(abort_reasons)]
    abort_set=make_abort_set(envelope,abort_rows); provider_receipt=make_provider_receipt(envelope,provider_observation,event=event,cursor=after) if provider_observation is not None else None
    closure=validate_closure(envelope=envelope,cursor=after,event=event,receipt=receipt,abort_set=abort_set,provider_receipt=provider_receipt)
    return {"schema":"ATHENA.Q008.IDENTITY.TRANSITION.BUNDLE.V1","envelope":envelope,"cursor_before":before,"cursor_after":after,"event":event,"receipt":receipt,"abort_set":abort_set,"provider_receipt":provider_receipt,"closure":closure}
