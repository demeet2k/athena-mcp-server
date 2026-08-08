from __future__ import annotations

from typing import Any, Mapping, Sequence

from .claim import claim_path, make_claim, validate_claim
from .common import KernelError, require_nonempty_string, require_positive_int, require_safe_id
from .journal import (
    classify_event_provider_result,
    make_event,
    next_sequence,
    prepare_event_append,
    provider_create_packet,
    sha256_json,
    stream_digest,
)
from .reducer import reduce_events


def _node(run: Mapping[str, Any], node_id: str) -> Mapping[str, Any]:
    safe_node = require_safe_id(node_id, "claim_saga.node_id")
    for node in run.get("nodes", []):
        if node.get("node_id") == safe_node:
            return node
    raise KernelError(f"claim saga: unknown node {safe_node}")


def _claim_event_id(claim: Mapping[str, Any]) -> str:
    return f"claim-acquired-{sha256_json(claim)[:24]}"


def _matching_claim_events(events: Sequence[Mapping[str, Any]], *, node_id: str, path: str) -> list[Mapping[str, Any]]:
    return [
        event
        for event in events
        if event.get("event_type") == "CLAIM_ACQUIRED"
        and event.get("node_id") == node_id
        and (event.get("data") or {}).get("claim_path") == path
    ]


def prepare_claim_saga(
    *,
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    node_id: str,
    worker_role: str,
    attempt: int,
    policy_commit: str,
    claimed_at: str,
    lease_expires_at: str,
    input_snapshot_digest: str,
    production_authority: str = "HOLD",
) -> dict[str, Any]:
    """Prepare the provider-atomic exclusion effect for one replayably READY node."""

    projection = reduce_events(run, events)
    node = _node(run, node_id)
    state = projection["node_states"].get(node_id)
    if state != "READY":
        raise KernelError(f"claim saga: node {node_id} is {state}, not READY")
    if node.get("role_capability") != worker_role:
        raise KernelError(
            f"claim saga: worker role {worker_role!r} does not match node role {node.get('role_capability')!r}"
        )
    attempt = require_positive_int(attempt, "claim_saga.attempt")
    if attempt > int(node.get("max_attempts", 0)):
        raise KernelError("claim saga: attempt exceeds node max_attempts")
    require_nonempty_string(policy_commit, "claim_saga.policy_commit")

    claim = make_claim(
        run_id=run["run_id"],
        node_id=node_id,
        worker_role=worker_role,
        attempt=attempt,
        policy_commit=policy_commit,
        claimed_at=claimed_at,
        lease_expires_at=lease_expires_at,
        input_snapshot_digest=input_snapshot_digest,
        production_authority=production_authority,
    )
    path = claim_path(run["run_id"], node_id)
    return {
        "status": "CLAIM_EFFECT_PREPARED",
        "run_id": run["run_id"],
        "node_id": node_id,
        "worker_role": worker_role,
        "attempt": attempt,
        "claim_path": path,
        "claim_digest": sha256_json(claim),
        "basis_stream_digest": stream_digest(events),
        "projection_before": projection,
        "provider": provider_create_packet(path, claim, kind="CLAIM_V1"),
        "law": "CLAIM_EFFECT_PREPARED != CLAIM_ACQUIRED; fixed-path provider create-if-absent owns exclusion",
    }


def after_claim_provider(
    *,
    run: Mapping[str, Any],
    current_events: Sequence[Mapping[str, Any]],
    prepared: Mapping[str, Any],
    provider_status: str,
) -> dict[str, Any]:
    """Translate the provider claim result into either lost-race or journal work."""

    status = require_nonempty_string(provider_status, "claim_saga.provider_status").upper()
    if status in {"EXISTS", "ALREADY_EXISTS", "CONFLICT"}:
        return {
            "status": "CLAIM_LOST_RACE",
            "run_id": prepared["run_id"],
            "node_id": prepared["node_id"],
            "claim_path": prepared["claim_path"],
            "law": "existing fixed claim path is a lost race, not retryable success",
        }
    if status not in {"CREATED", "SUCCESS", "COMMITTED"}:
        return {
            "status": "CLAIM_PROVIDER_HOLD",
            "provider_status": status,
            "run_id": prepared["run_id"],
            "node_id": prepared["node_id"],
            "claim_path": prepared["claim_path"],
        }

    claim = validate_claim(prepared["provider"]["content"])
    try:
        projection = reduce_events(run, current_events)
        state = projection["node_states"].get(claim["node_id"])
        if _matching_claim_events(current_events, node_id=claim["node_id"], path=prepared["claim_path"]):
            return {
                "status": "CLAIM_ALREADY_JOURNALED",
                "run_id": claim["run_id"],
                "node_id": claim["node_id"],
                "claim_path": prepared["claim_path"],
            }
        if state != "READY":
            return {
                "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
                "run_id": claim["run_id"],
                "node_id": claim["node_id"],
                "claim_path": prepared["claim_path"],
                "reducer_state": state,
                "reason": "provider claim exists but current replay state cannot lawfully accept CLAIM_ACQUIRED",
                "law": "provider effect is preserved; contradiction requires reconciliation, not fabricated rollback",
            }
        event = make_event(
            event_id=_claim_event_id(claim),
            sequence=next_sequence(current_events),
            run_id=claim["run_id"],
            event_type="CLAIM_ACQUIRED",
            at=claim["claimed_at"],
            node_id=claim["node_id"],
            data={
                "claim_path": prepared["claim_path"],
                "claim_digest": sha256_json(claim),
                "attempt": claim["attempt"],
            },
        )
        event_append = prepare_event_append(run=run, events=current_events, event=event)
    except Exception as exc:
        return {
            "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
            "run_id": claim["run_id"],
            "node_id": claim["node_id"],
            "claim_path": prepared["claim_path"],
            "reason": str(exc),
            "law": "claim provider effect remains real even when journal preparation fails",
        }

    return {
        "status": "CLAIM_EFFECT_CREATED_JOURNAL_PENDING",
        "run_id": claim["run_id"],
        "node_id": claim["node_id"],
        "claim_path": prepared["claim_path"],
        "claim_digest": sha256_json(claim),
        "event_append": event_append,
        "law": "claim creation and event append are separate provider effects; this state is not yet reducer-visible CLAIMED",
    }


def after_claim_event_provider(
    *,
    saga_state: Mapping[str, Any],
    provider_status: str,
) -> dict[str, Any]:
    if saga_state.get("status") != "CLAIM_EFFECT_CREATED_JOURNAL_PENDING":
        raise KernelError("claim saga: journal result requires CLAIM_EFFECT_CREATED_JOURNAL_PENDING")
    event_result = classify_event_provider_result(saga_state["event_append"], provider_status)
    if event_result["status"] == "EVENT_PERSISTED":
        return {
            "status": "CLAIM_JOURNALED",
            "run_id": saga_state["run_id"],
            "node_id": saga_state["node_id"],
            "claim_path": saga_state["claim_path"],
            "claim_digest": saga_state["claim_digest"],
            "event": event_result,
            "law": "claim is reducer-visible only after immutable CLAIM_ACQUIRED event persistence",
        }
    return {
        "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
        "run_id": saga_state["run_id"],
        "node_id": saga_state["node_id"],
        "claim_path": saga_state["claim_path"],
        "claim_digest": saga_state["claim_digest"],
        "event": event_result,
        "law": "event collision/failure does not erase the already-created claim provider effect",
    }


def reconcile_claim_effect(
    *,
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    claim_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Recover an existing provider claim that lacks its causal journal event."""

    claim = validate_claim(claim_record)
    path = claim_path(claim["run_id"], claim["node_id"])
    matches = _matching_claim_events(events, node_id=claim["node_id"], path=path)
    if len(matches) > 1:
        return {
            "status": "CLAIM_JOURNAL_CONTRADICTION_HOLD",
            "claim_path": path,
            "reason": "multiple CLAIM_ACQUIRED events reference one fixed claim path",
        }
    if len(matches) == 1:
        return {
            "status": "CLAIM_ALREADY_JOURNALED",
            "claim_path": path,
            "event_id": matches[0]["event_id"],
            "sequence": matches[0]["sequence"],
        }

    projection = reduce_events(run, events)
    state = projection["node_states"].get(claim["node_id"])
    if state != "READY":
        return {
            "status": "CLAIM_JOURNAL_CONTRADICTION_HOLD",
            "claim_path": path,
            "reducer_state": state,
            "reason": "unjournaled provider claim exists but replay state is not READY",
            "law": "do not synthesize or delete state to force convergence",
        }

    event = make_event(
        event_id=_claim_event_id(claim),
        sequence=next_sequence(events),
        run_id=claim["run_id"],
        event_type="CLAIM_ACQUIRED",
        at=claim["claimed_at"],
        node_id=claim["node_id"],
        data={"claim_path": path, "claim_digest": sha256_json(claim), "attempt": claim["attempt"]},
    )
    append = prepare_event_append(run=run, events=events, event=event)
    return {
        "status": "CLAIM_RECONCILIATION_APPEND_PREPARED",
        "claim_path": path,
        "claim_digest": sha256_json(claim),
        "event_append": append,
        "law": "reconciliation journals the observed provider effect; it does not invent a new claim",
    }
