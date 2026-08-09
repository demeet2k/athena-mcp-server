from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Optional

from .cohesion_dependency_cone import dependency_cone
from .cohesion_mesh import COMPARISON_EVENT, COHESION_VERSION, _digest, _names
from .message_board import _iso, _json_text, _require_id

CUT02_VERSION = "ATHENA.COHESION.CLOSURE.CUT02.1"
CONSUMPTION_ARTIFACT = "ATHENA.COHESION.CONSUMPTION.V1"
CONSUMPTION_EVENT = "COHESION_CONSUMPTION"
OUTCOME_CREDIT_ARTIFACT = "ATHENA.COHESION.OUTCOME.CREDIT.V1"
PULSE_ARTIFACT = "ATHENA.COHESION.PULSE.CUT02.V1"

CONSUMPTION_DECISIONS = {
    "ACCEPTED_CHANGED",
    "ACCEPTED_NO_CHANGE",
    "REJECTED",
    "PARTIAL",
    "UNRESOLVED",
}

LAWS = [
    "ROUTED != ACKED != CONSUMED != COMPLIED != TRUE",
    "CONSUMPTION != EXECUTION_AUTHORITY",
    "CONSUMPTION != XP_AUTHORITY",
    "EXECUTION_CONTRIBUTION != COORDINATION_CONTRIBUTION != TRUTH_STANDING != CAUSAL_EFFECT",
    "DUPLICATE_EVIDENCE_ATTRIBUTION != INDEPENDENT_SUPPORT",
    "COHESION_PULSE != QUEST_PULSE",
    "COHESION_PULSE != SCHEDULER",
    "COHESION_SIGNAL != EXECUTION_AUTHORITY",
    "UNKNOWN != ZERO",
    "MATCHED_DESCRIPTIVE_DIFFERENCE != CAUSAL_TREATMENT_EFFECT",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _consumption_events(board) -> list[dict]:
    rows = []
    for event in board._events():
        if event.get("kind") != CONSUMPTION_EVENT:
            continue
        payload = event.get("payload") or {}
        if not isinstance(payload, Mapping):
            continue
        if payload.get("cohesion_version") != COHESION_VERSION:
            continue
        if payload.get("cohesion_artifact") != CONSUMPTION_ARTIFACT:
            continue
        rows.append(dict(event))
    return rows


def _consumption_by_id(board, consumption_id: str) -> Optional[dict]:
    for event in _consumption_events(board):
        payload = event.get("payload") or {}
        if str(payload.get("consumption_id")) == consumption_id:
            return event
    return None


def _consumption_by_event_id(board) -> dict[str, dict]:
    return {
        str(event.get("event_id")): event
        for event in _consumption_events(board)
        if event.get("event_id")
    }


def _route_acks(events: Iterable[Mapping[str, Any]], route_ref: str, recipient_id: str) -> list[str]:
    return sorted(
        str(event.get("event_id"))
        for event in events
        if event.get("kind") == "ACK"
        and str(event.get("agent_id")) == recipient_id
        and str((event.get("payload") or {}).get("message_id")) == route_ref
        and event.get("event_id")
    )


def consume(
    cohesion_runtime: Any,
    *,
    consumption_id: str,
    recipient_id: str,
    route_ref: str,
    decision: str,
    behavior_change: bool,
    behavior_change_ref: Optional[str] = None,
    reason: Optional[str] = None,
    evidence_refs: Optional[Iterable[str]] = None,
    expected_route_digest: Optional[str] = None,
    remote: str = "origin",
) -> dict:
    """Record explicit recipient uptake through Message Board; route/ACK are insufficient."""
    consumption_id = _require_id(consumption_id, "consumption_id")
    recipient_id = _require_id(recipient_id, "recipient_id")
    route_ref = _require_id(route_ref, "route_ref")
    decision = _text(decision).upper()
    if decision not in CONSUMPTION_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(CONSUMPTION_DECISIONS)}")
    if not isinstance(behavior_change, bool):
        raise ValueError("behavior_change must be boolean")
    behavior_change_ref = _text(behavior_change_ref) or None
    if behavior_change and not behavior_change_ref:
        raise ValueError("behavior_change_ref is required when behavior_change=true")
    if decision == "ACCEPTED_CHANGED" and not behavior_change:
        raise ValueError("ACCEPTED_CHANGED requires behavior_change=true")
    if decision in {"ACCEPTED_NO_CHANGE", "REJECTED", "UNRESOLVED"} and behavior_change:
        raise ValueError(f"{decision} requires behavior_change=false")
    evidence = _names(evidence_refs)
    expected_route_digest = _text(expected_route_digest) or None
    board = cohesion_runtime._board()

    def build(base):
        active = {str(row.get("agent_id")): row for row in board._active()}
        if recipient_id not in active:
            return {
                "return": {
                    "status": "COHESION_CONSUMPTION_RECIPIENT_NOT_ACTIVE_HOLD",
                    "consumption_id": consumption_id,
                    "recipient_id": recipient_id,
                    "consumption_established": False,
                    "execution_authority": False,
                }
            }
        events = board._events()
        route = next(
            (
                event
                for event in events
                if event.get("event_id") == route_ref and event.get("kind") == "MESSAGE"
            ),
            None,
        )
        if route is None:
            return {
                "return": {
                    "status": "COHESION_CONSUMPTION_STALE_ROUTE_HOLD",
                    "consumption_id": consumption_id,
                    "route_ref": route_ref,
                    "consumption_established": False,
                    "execution_authority": False,
                }
            }
        if not board._message_visible_to(route, recipient_id):
            return {
                "return": {
                    "status": "COHESION_CONSUMPTION_ROUTE_NOT_VISIBLE_HOLD",
                    "consumption_id": consumption_id,
                    "route_ref": route_ref,
                    "recipient_id": recipient_id,
                    "consumption_established": False,
                    "execution_authority": False,
                }
            }
        route_digest = _digest(route)
        if expected_route_digest and expected_route_digest != route_digest:
            return {
                "return": {
                    "status": "COHESION_CONSUMPTION_ROUTE_DIGEST_HOLD",
                    "consumption_id": consumption_id,
                    "route_ref": route_ref,
                    "expected_route_digest": expected_route_digest,
                    "observed_route_digest": route_digest,
                    "consumption_established": False,
                    "execution_authority": False,
                }
            }
        ack_refs = _route_acks(events, route_ref, recipient_id)
        identity_basis = {
            "cohesion_version": COHESION_VERSION,
            "cohesion_artifact": CONSUMPTION_ARTIFACT,
            "consumption_id": consumption_id,
            "recipient_id": recipient_id,
            "route_ref": route_ref,
            "route_digest": route_digest,
            "decision": decision,
            "behavior_change": behavior_change,
            "behavior_change_ref": behavior_change_ref,
            "reason": _text(reason) or None,
            "evidence_refs": evidence,
        }
        consumption_digest = _digest(identity_basis)
        existing = _consumption_by_id(board, consumption_id)
        if existing:
            old = existing.get("payload") or {}
            if old.get("consumption_digest") != consumption_digest:
                raise ValueError(f"COHESION_CONSUMPTION_ID_CONFLICT: {consumption_id}")
            return {
                "return": {
                    "status": "COHESION_CONSUMPTION_ALREADY_RECORDED",
                    "consumption": old,
                    "event": existing,
                    "idempotent": True,
                    "consumption_established": True,
                    "truth_authority": False,
                    "execution_authority": False,
                }
            }
        payload = {
            **identity_basis,
            "consumption_digest": consumption_digest,
            "ack_observed": bool(ack_refs),
            "ack_event_refs": ack_refs,
            "truth_authority": False,
            "compliance_authority": False,
            "execution_authority": False,
            "xp_authority": False,
            "consumed_at": _iso(),
            "consumed_from_git_head": base,
            "law": "ROUTED != ACKED != CONSUMED != COMPLIED != TRUE",
        }
        event_rel, event = board._event(
            CONSUMPTION_EVENT,
            recipient_id,
            payload,
            reply_to=route_ref,
        )
        return {
            "files": {event_rel: _json_text(event)},
            "message": f"cohesion consume {consumption_id}",
            "result": {
                "status": "COHESION_CONSUMPTION_RECORDED",
                "consumption": payload,
                "event": event,
                "idempotent": False,
                "consumption_established": True,
                "accepted": decision in {"ACCEPTED_CHANGED", "ACCEPTED_NO_CHANGE", "PARTIAL"},
                "behavior_changed": behavior_change,
                "truth_authority": False,
                "compliance_authority": False,
                "execution_authority": False,
                "xp_authority": False,
            },
        }

    return board._mutate(agent_id=recipient_id, remote=remote, build_files=build)


def outcome_credit(
    cohesion_runtime: Any,
    *,
    credit_id: str,
    observer_id: str,
    outcomes: Iterable[Mapping[str, Any]],
    remote: str = "origin",
    shared_remote_mode: str = "REQUIRED",
) -> dict:
    """Separate execution, coordination, truth and causal standing without scalar reward."""
    credit_id = _require_id(credit_id, "credit_id")
    observer_id = _require_id(observer_id, "observer_id")
    rows = [dict(row) for row in outcomes]
    if not rows:
        raise ValueError("outcomes are required")
    board = cohesion_runtime._board()
    snapshot = board.read(
        agent_id=observer_id,
        limit=500,
        include_stale=False,
        remote=remote,
        shared_remote_mode=shared_remote_mode,
    )
    shared_fresh = bool(snapshot.get("shared_frontier_verified"))
    if str(shared_remote_mode or "REQUIRED").upper() == "REQUIRED" and not shared_fresh:
        return {
            "artifact": OUTCOME_CREDIT_ARTIFACT,
            "version": CUT02_VERSION,
            "status": "COHESION_OUTCOME_CREDIT_SHARED_FRONTIER_HOLD",
            "credit_id": credit_id,
            "rows": [],
            "causal_effect": "UNKNOWN",
            "promotion_authority": False,
            "read_only": True,
            "execution_authority": False,
        }

    consumption_events = _consumption_by_event_id(board)
    evidence_usage: dict[str, set[str]] = defaultdict(set)
    consumption_usage: dict[str, set[str]] = defaultdict(set)
    normalized = []
    seen_outcomes: set[str] = set()
    for index, raw in enumerate(rows):
        outcome_id = _require_id(raw.get("outcome_id"), f"outcomes[{index}].outcome_id")
        if outcome_id in seen_outcomes:
            raise ValueError(f"duplicate outcome_id: {outcome_id}")
        seen_outcomes.add(outcome_id)
        evidence_refs = _names(raw.get("evidence_refs"))
        consumption_refs = _names(raw.get("consumption_refs"))
        for ref in evidence_refs:
            evidence_usage[ref].add(outcome_id)
        for ref in consumption_refs:
            consumption_usage[ref].add(outcome_id)
        valid_consumptions = []
        missing_consumptions = []
        for ref in consumption_refs:
            event = consumption_events.get(ref)
            if event is None:
                missing_consumptions.append(ref)
            else:
                payload = event.get("payload") or {}
                valid_consumptions.append({
                    "event_ref": ref,
                    "consumption_id": payload.get("consumption_id"),
                    "recipient_id": payload.get("recipient_id"),
                    "decision": payload.get("decision"),
                    "behavior_change": payload.get("behavior_change"),
                })
        execution_ref = _text(raw.get("execution_ref")) or None
        observation_ref = _text(raw.get("observation_ref")) or None
        verification_ref = _text(raw.get("verification_ref")) or None
        normalized.append({
            "outcome_id": outcome_id,
            "execution_ref": execution_ref,
            "observation_ref": observation_ref,
            "verification_ref": verification_ref,
            "evidence_refs": evidence_refs,
            "consumption_refs": consumption_refs,
            "valid_consumptions": valid_consumptions,
            "missing_consumption_refs": missing_consumptions,
            "execution_contribution": (
                "EXECUTION_REF_SUPPLIED_NOT_PROVIDER_VERIFIED"
                if execution_ref else "NOT_ESTABLISHED"
            ),
            "outcome_effect": (
                "OBSERVATION_REF_SUPPLIED_NOT_PROVIDER_VERIFIED"
                if observation_ref else "UNKNOWN"
            ),
            "truth_verification": (
                "VERIFICATION_REF_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED"
                if verification_ref else "UNKNOWN"
            ),
            "coordination_contribution": (
                "OBSERVED_CONSUMPTION_ASSOCIATION"
                if valid_consumptions else "NOT_ESTABLISHED"
            ),
            "causal_effect": "UNKNOWN",
        })

    reused_evidence = sorted(ref for ref, ids in evidence_usage.items() if len(ids) > 1)
    reused_consumptions = sorted(ref for ref, ids in consumption_usage.items() if len(ids) > 1)
    missing_consumptions = sorted({
        ref for row in normalized for ref in row["missing_consumption_refs"]
    })
    reasons = []
    if reused_evidence:
        reasons.append("DUPLICATE_EVIDENCE_ATTRIBUTION")
    if reused_consumptions:
        reasons.append("DUPLICATE_CONSUMPTION_ATTRIBUTION")
    if missing_consumptions:
        reasons.append("UNRESOLVED_CONSUMPTION_REF")
    if any(row["outcome_effect"] == "UNKNOWN" for row in normalized):
        reasons.append("UNOBSERVED_OUTCOME_EFFECT")

    decision = "UNKNOWN_INSUFFICIENT_EVIDENCE" if reasons else "DESCRIPTIVE_ATTRIBUTION_READY"
    standing = "UNDERDETERMINED" if reasons else "DESCRIPTIVE_OBSERVATION_ONLY"
    value = {
        "artifact": OUTCOME_CREDIT_ARTIFACT,
        "version": CUT02_VERSION,
        "status": "COHESION_OUTCOME_CREDIT_OK",
        "credit_id": credit_id,
        "observer_id": observer_id,
        "decision": decision,
        "standing": standing,
        "rows": normalized,
        "quality_reasons": sorted(reasons),
        "reused_evidence_refs": reused_evidence,
        "reused_consumption_refs": reused_consumptions,
        "missing_consumption_refs": missing_consumptions,
        "causal_effect": "UNKNOWN",
        "scalar_credit": None,
        "truth_authority": False,
        "promotion_authority": False,
        "execution_authority": False,
        "read_only": True,
        "shared_frontier_verified": shared_fresh,
        "git_head": board.git.head(),
        "laws": list(LAWS),
    }
    value["receipt_digest"] = _digest({
        "credit_id": credit_id,
        "observer_id": observer_id,
        "decision": decision,
        "standing": standing,
        "rows": normalized,
        "quality_reasons": value["quality_reasons"],
        "causal_effect": "UNKNOWN",
    })
    return value


def _comparison_payload(cohesion_runtime: Any, board, comparison_id: Optional[str]) -> Optional[dict]:
    rows = []
    for event in cohesion_runtime._cohesion_events(board, COMPARISON_EVENT):
        payload = dict(cohesion_runtime._payload(event))
        if comparison_id and str(payload.get("comparison_id")) != comparison_id:
            continue
        rows.append((str(event.get("created_at") or ""), str(event.get("event_id") or ""), payload))
    if not rows:
        return None
    return sorted(rows)[-1][2]


def _unconsumed_routes(board, events: list[dict], consumption_events: list[dict]) -> list[dict]:
    consumed = {
        (str((event.get("payload") or {}).get("route_ref")), str((event.get("payload") or {}).get("recipient_id")))
        for event in consumption_events
    }
    rows = []
    for event in events:
        if event.get("kind") != "MESSAGE":
            continue
        route_ref = str(event.get("event_id") or "")
        if not route_ref:
            continue
        message_kind = str((event.get("payload") or {}).get("message_kind") or "INFO")
        for recipient in sorted({str(x) for x in (event.get("recipients") or []) if str(x)}):
            if (route_ref, recipient) in consumed:
                continue
            rows.append({
                "route_ref": route_ref,
                "recipient_id": recipient,
                "message_kind": message_kind,
                "created_at": event.get("created_at"),
                "standing": "ROUTED_NOT_CONSUMED",
            })
    return rows


def pulse(
    cohesion_runtime: Any,
    party_runtime: Any,
    *,
    observer_id: str,
    comparison_id: Optional[str] = None,
    change: Optional[Mapping[str, Any]] = None,
    caller_edges: Optional[Iterable[Mapping[str, Any]]] = None,
    remote: str = "origin",
    shared_remote_mode: str = "REQUIRED",
) -> dict:
    """Read-only advisory collective steering front door; never dispatches work."""
    observer_id = _require_id(observer_id, "observer_id")
    board = cohesion_runtime._board()
    snapshot = board.read(
        agent_id=observer_id,
        limit=500,
        include_stale=False,
        remote=remote,
        shared_remote_mode=shared_remote_mode,
    )
    shared_fresh = bool(snapshot.get("shared_frontier_verified"))
    if str(shared_remote_mode or "REQUIRED").upper() == "REQUIRED" and not shared_fresh:
        return {
            "artifact": PULSE_ARTIFACT,
            "version": CUT02_VERSION,
            "status": "COHESION_PULSE_SHARED_FRONTIER_HOLD",
            "observer_id": observer_id,
            "ranked_interventions": [{"intervention": "HOLD", "reason_codes": ["SHARED_FRONTIER_UNVERIFIED"]}],
            "unknown_pressures": [],
            "execution_authority": False,
            "scheduler_authority": False,
            "read_only": True,
        }

    events = board._events()
    consumptions = _consumption_events(board)
    unconsumed = _unconsumed_routes(board, events, consumptions)
    exact_unintentional = [
        dict(row)
        for row in (snapshot.get("exact_overlaps") or [])
        if not bool(row.get("intentional"))
    ]
    comparison = _comparison_payload(cohesion_runtime, board, comparison_id)
    dependency = None
    if change is not None:
        dependency = dependency_cone(
            cohesion_runtime,
            party_runtime,
            change=change,
            caller_edges=caller_edges,
            remote=remote,
            shared_remote_mode="DISABLED",
        )

    unknown_pressures = []
    pressures = []
    interventions = []

    if exact_unintentional:
        pressures.append({"pressure": "duplicate_collision", "value": len(exact_unintentional), "standing": "OBSERVED_MESSAGE_BOARD"})
        interventions.append({
            "intervention": "PARTITION_OR_SEQUENCE",
            "priority": 90,
            "reason_codes": ["EXACT_UNDECLARED_OVERLAP"],
            "expected_receipts": ["claim/partition/coordination receipt"],
            "execution_authority": False,
        })
    else:
        pressures.append({"pressure": "duplicate_collision", "value": 0, "standing": "OBSERVED_MESSAGE_BOARD"})

    if unconsumed:
        pressures.append({"pressure": "unconsumed_routes", "value": len(unconsumed), "standing": "OBSERVED_MESSAGE_BOARD_MINUS_CONSUMPTION"})
        interventions.append({
            "intervention": "CONSUME_REVIEW",
            "priority": 80,
            "reason_codes": ["ROUTED_NOT_CONSUMED"],
            "expected_receipts": ["COHESION_CONSUMPTION"],
            "execution_authority": False,
        })
    else:
        pressures.append({"pressure": "unconsumed_routes", "value": 0, "standing": "OBSERVED_MESSAGE_BOARD_MINUS_CONSUMPTION"})

    if comparison is None:
        unknown_pressures.append("comparative_evidence")
    else:
        decision = str(comparison.get("decision") or "")
        reasons = list(comparison.get("quality_reasons") or [])
        if decision == "UNKNOWN_INSUFFICIENT_EVIDENCE" or reasons:
            pressures.append({"pressure": "comparative_evidence", "value": "HOLD", "standing": "OBSERVED_COHESION_COMPARISON", "reason_codes": reasons})
            interventions.append({
                "intervention": "EVIDENCE_REQUIRED",
                "priority": 100,
                "reason_codes": sorted(set(reasons or ["COMPARISON_UNDERDETERMINED"])),
                "expected_receipts": ["complete unique-evidence comparison receipt"],
                "execution_authority": False,
            })
        else:
            pressures.append({"pressure": "comparative_evidence", "value": decision, "standing": "MATCHED_DESCRIPTIVE_ONLY"})

    if dependency is None:
        unknown_pressures.append("dependency_change")
    else:
        affected = list(dependency.get("directly_affected") or []) + list(dependency.get("transitively_affected") or [])
        if dependency.get("classification") in {"GIT_REF_HOLD", "SHARED_FRONTIER_HOLD", "UNKNOWN_IMPACT_TRUNCATED"}:
            interventions.append({
                "intervention": "HOLD",
                "priority": 100,
                "reason_codes": [str(dependency.get("classification"))],
                "expected_receipts": ["fresh dependency-cone receipt"],
                "execution_authority": False,
            })
        elif affected:
            pressures.append({"pressure": "dependency_invalidation", "value": len(affected), "standing": "EXPLICIT_EDGE_CONE"})
            interventions.append({
                "intervention": "TARGETED_REHYDRATE_RECHECK",
                "priority": 85,
                "reason_codes": ["DEPENDENCY_CONE_AFFECTED_LANES"],
                "affected_agent_ids": sorted({str(row.get("agent_id")) for row in affected}),
                "expected_receipts": ["rehydrate/recheck receipts for affected lanes"],
                "execution_authority": False,
            })
        else:
            pressures.append({"pressure": "dependency_invalidation", "value": 0, "standing": str(dependency.get("classification"))})

    if not interventions:
        interventions.append({
            "intervention": "CONTINUE_OR_STOP_REQUIRES_GTC",
            "priority": 10,
            "reason_codes": ["NO_COHESION_HARD_PRESSURE_OBSERVED"],
            "expected_receipts": ["fresh GTC continuation/stop receipt"],
            "execution_authority": False,
        })
    interventions = sorted(
        interventions,
        key=lambda row: (-int(row.get("priority") or 0), str(row.get("intervention"))),
    )

    state_basis = {
        "git_head": board.git.head(),
        "observer_id": observer_id,
        "exact_unintentional_overlaps": exact_unintentional,
        "unconsumed_routes": unconsumed,
        "comparison_id": comparison.get("comparison_id") if comparison else None,
        "comparison_decision": comparison.get("decision") if comparison else None,
        "dependency_digest": dependency.get("decision_digest") if dependency else None,
        "pressures": pressures,
        "unknown_pressures": sorted(set(unknown_pressures)),
        "ranked_interventions": interventions,
    }
    return {
        "artifact": PULSE_ARTIFACT,
        "version": CUT02_VERSION,
        "status": "COHESION_PULSE_OK",
        **state_basis,
        "state_digest": _digest(state_basis),
        "shared_frontier_verified": shared_fresh,
        "stop_established": False,
        "stop_condition": "requires fresh external GTC NO_POSITIVE_FRONTIER/legitimate stop receipt",
        "escalation_conditions": [
            "authority hold",
            "unresolved shared-frontier hold",
            "unresolved evidence hold",
            "unresolved coordination conflict",
        ],
        "execution_authority": False,
        "scheduler_authority": False,
        "claim_authority": False,
        "truth_authority": False,
        "read_only": True,
        "laws": list(LAWS),
    }


def augment_cut02_resource(resource: Mapping[str, Any]) -> dict:
    value = dict(resource or {})
    tools = list(value.get("tools") or [])
    for name in (
        "athena_cohesion_consume",
        "athena_cohesion_outcome_credit",
        "athena_cohesion_pulse",
    ):
        if name not in tools:
            tools.append(name)
    value["tools"] = tools
    laws = list(value.get("laws") or [])
    for law in LAWS:
        if law not in laws:
            laws.append(law)
    value["laws"] = laws
    value["closure_cut02_version"] = CUT02_VERSION
    value["closure_cut02"] = {
        "consume": "MESSAGE_BOARD_EVENT_MUTATION_ONLY",
        "outcome_credit": "READ_ONLY_DESCRIPTIVE_ATTRIBUTION",
        "pulse": "READ_ONLY_ADVISORY_STEERING",
        "execution_authority": False,
        "scheduler_authority": False,
    }
    residual = []
    for item in value.get("residual") or []:
        text = str(item)
        if text == "C1 common-ground tools 1-5":
            residual.append("remaining C1 common-ground tools 1-3,5")
        elif text == "remaining C4 decision/outcome/health/pulse tools 16-17,19-20":
            residual.append("remaining C4 decision/health tools 16,19")
        else:
            residual.append(item)
    value["residual"] = residual
    return value
