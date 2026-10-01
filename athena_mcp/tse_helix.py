from __future__ import annotations

import copy
from typing import Any, Iterable, Mapping

from .tse_population import _validate_route
from .tse_telemetry import HOLD_CLASSES, _digest


HELIX_VERSION = "TSE.HELICAL.HANDOFF.COMPOSITION.2"
HELIX_RESOURCE_URI = "athena://tse-helix/v2"

_OPERATION_TRANSITION = {
    "PUBLISH": "HATCH_NEED_PUBLISHED",
    "MATCH": "MATCH_FOUND",
    "HANDOFF": "HANDOFF_ROUTED",
    "CLAIM_STATE": "CHILD_CLAIMED",
    "RETURN_CHECK": "CHILD_VERIFIED_RETURN",
}
_OPERATION_SUCCESS = {
    "PUBLISH": "TSE_POPULATION_NEED_PUBLISHED",
    "MATCH": "TSE_POPULATION_MATCHED_ADVISORY",
    "HANDOFF": "TSE_POPULATION_HANDOFF_ROUTED",
    "CLAIM_STATE": "TSE_POPULATION_SUBTASK_CLAIMED",
    "RETURN_CHECK": "TSE_POPULATION_RETURN_CONSUMPTION_READY",
}


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _short(value: Any, width: int = 24) -> str:
    return _digest(value).split(":", 1)[1][:width]


class TseHelixRuntime:
    """Source-bound composition over TSE population actions and telemetry.

    The composition layer does not replace the authority of the wrapped source:
    population actions remain authoritative for their own state, Message Board
    remains claim truth, and telemetry is a post-action observation saga.
    """

    def __init__(self, server, population_runtime, telemetry_runtime, cohesion_runtime):
        self.server = server
        self.population = population_runtime
        self.telemetry = telemetry_runtime
        self.cohesion = cohesion_runtime

    @staticmethod
    def _route_identity(route: Mapping[str, Any]) -> dict:
        return {
            "route_id": route.get("route_id"),
            "route_digest": route.get("route_digest"),
            "hatch_id": route.get("hatch_id"),
            "hatch_digest": route.get("hatch_digest"),
            "parent_checkpoint_digest": route.get("parent_checkpoint_digest"),
        }

    @staticmethod
    def _hold_class(result: Mapping[str, Any]) -> str:
        value = str(result.get("hold") or "").upper()
        return value if value in HOLD_CLASSES else "EVIDENCE_HOLD"

    @staticmethod
    def _result_route(result: Mapping[str, Any], fallback: Mapping[str, Any]) -> dict:
        value = result.get("route")
        return copy.deepcopy(value if isinstance(value, Mapping) else fallback)

    def _record_hold(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        operation: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        parent_event_id: str,
        result: Mapping[str, Any],
        remote: str,
    ) -> dict:
        payload = {
            "operation": operation,
            "status": result.get("status"),
            "hold": result.get("hold"),
            "reason": result.get("reason"),
            "errors": result.get("errors"),
            "route": self._route_identity(route),
            "git_head": self.server.git.head() if self.server.git.enabled else None,
        }
        source_ref = f"HOLD-{_short(payload)}"
        return self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=str(route["route_id"]),
            hatch_id=str(route["hatch_id"]),
            transition="HELIX_HOLD",
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind=f"TSE_POPULATION_{operation}_RESULT",
            source_ref=source_ref,
            source_payload=payload,
            source_git_head=self.server.git.head() if self.server.git.enabled else None,
            source_authority="WRAPPED_SOURCE_RESULT",
            parent_event_id=parent_event_id,
            hold_class=self._hold_class(result),
            seam=operation,
            attempt_ref=source_ref,
            remote=remote,
        )

    def _source_from_result(self, operation: str, route: Mapping[str, Any], result: Mapping[str, Any]) -> dict:
        if operation == "PUBLISH":
            cohesion = result.get("cohesion") or {}
            request = cohesion.get("request") or {}
            event = cohesion.get("event") or {}
            source_ref = str(event.get("event_id") or f"NEED-{_short(request)}")
            payload = {
                "request": request,
                "event_id": event.get("event_id"),
                "route": self._route_identity(route),
            }
            return {
                "kind": "COHESION_NEED_PUBLICATION",
                "ref": source_ref,
                "payload": payload,
                "git_head": (cohesion.get("git") or {}).get("head") or self.server.git.head(),
                "authority": "COHESION_PUBLICATION_STATE",
            }

        if operation == "MATCH":
            cohesion = result.get("cohesion") or {}
            selected = route.get("selected_match") or {}
            payload = {
                "selected_match": selected,
                "need_id": (route.get("need_args") or {}).get("request_id"),
                "match_git_head": selected.get("match_git_head") or cohesion.get("git_head"),
                "route": self._route_identity(route),
            }
            return {
                "kind": "COHESION_ADVISORY_MATCH",
                "ref": f"MATCH-{_short(payload)}",
                "payload": payload,
                "git_head": selected.get("match_git_head") or cohesion.get("git_head") or self.server.git.head(),
                "authority": "COHESION_ADVISORY_MATCH_STATE",
            }

        if operation == "HANDOFF":
            board = result.get("message_board") or {}
            event = board.get("message_event") or {}
            payload = {
                "message_event": event,
                "route": self._route_identity(route),
            }
            return {
                "kind": "MESSAGE_BOARD_HANDOFF_ROUTE",
                "ref": str(event.get("event_id") or f"HANDOFF-{_short(payload)}"),
                "payload": payload,
                "git_head": (board.get("git") or {}).get("head") or self.server.git.head(),
                "authority": "MESSAGE_BOARD_ROUTE_STATE",
            }

        if operation == "CLAIM_STATE":
            board = result.get("message_board") or {}
            claim = route.get("child_claim") or {}
            payload = {
                "child_claim": claim,
                "message_board_git_head": board.get("git_head"),
                "route": self._route_identity(route),
            }
            return {
                "kind": "MESSAGE_BOARD_CHILD_CLAIM",
                "ref": str(claim.get("claim_id") or f"CLAIM-{_short(payload)}"),
                "payload": payload,
                "git_head": board.get("git_head") or self.server.git.head(),
                "authority": "MESSAGE_BOARD_CLAIM_STATE",
            }

        if operation == "RETURN_CHECK":
            returned = result.get("return_payload") or {}
            claim = route.get("child_claim") or {}
            payload = {
                "return_receipt_id": returned.get("return_receipt_id"),
                "return_payload": returned,
                "child_claim": claim,
                "message_board_claim_reverified": result.get("message_board_claim_reverified"),
                "route": self._route_identity(route),
            }
            return {
                "kind": "TSE_RETURN_CHECK",
                "ref": str(returned.get("return_receipt_id") or f"RETURN-{_short(payload)}"),
                "payload": payload,
                "git_head": self.server.git.head(),
                "authority": "TSE_RETURN_CHECK_WITH_CURRENT_MESSAGE_BOARD_CLAIM",
            }

        raise ValueError(f"unsupported operation: {operation}")

    def open(
        self,
        *,
        mission_id: str,
        hatch: Mapping[str, Any],
        parent_agent_id: str,
        capabilities: Iterable[str],
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        targets: Iterable[str] | None = None,
        dependencies: Iterable[str] | None = None,
        role: str = "",
        needed_units: int = 1,
        constraints: Iterable[str] | None = None,
        life_policy: str | None = None,
        clear_condition_digest: str | None = None,
        remote: str = "origin",
    ) -> dict:
        planned = self.population.plan(
            hatch,
            parent_agent_id,
            capabilities,
            targets,
            dependencies,
            role,
            needed_units,
            constraints,
            life_policy,
            clear_condition_digest,
        )
        if planned.get("status") != "TSE_POPULATION_NEED_READY":
            return {
                "status": "TSE_HELIX_OPEN_HOLD",
                "population": planned,
                "telemetry": None,
                "law": "INVALID_HATCH_OR_PLAN != HELIX_ROOT",
            }
        route = planned["route"]
        source_payload = {
            "hatch_id": hatch.get("hatch_id"),
            "hatch_digest": hatch.get("hatch_digest"),
            "parent_checkpoint_digest": hatch.get("parent_checkpoint_digest"),
            "child_quest": hatch.get("child_quest"),
            "route": self._route_identity(route),
        }
        source_ref = str(hatch.get("hatch_digest") or f"HATCH-{_short(source_payload)}")
        telemetry = self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=route["route_id"],
            hatch_id=route["hatch_id"],
            transition="HATCH_CREATED",
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind="TSE_HATCH_V2",
            source_ref=source_ref,
            source_payload=source_payload,
            source_git_head=self.server.git.head() if self.server.git.enabled else None,
            source_authority="TSE_HATCH_DIGEST_INTEGRITY",
            parent_event_id=None,
            attempt_ref=source_ref,
            remote=remote,
        )
        if telemetry.get("status") not in {
            "TSE_TELEMETRY_RECORDED_SOURCE_BOUND",
            "TSE_TELEMETRY_ALREADY_RECORDED",
        }:
            return {
                "status": "TSE_HELIX_OPEN_TELEMETRY_HOLD",
                "population": planned,
                "route": route,
                "telemetry": telemetry,
                "population_result_valid": True,
                "law": "TELEMETRY_FAILURE != PLAN_INVALIDATION",
            }
        return {
            "status": "TSE_HELIX_OPEN",
            "route": route,
            "root_event_id": telemetry["event"]["event_id"],
            "population": planned,
            "telemetry": telemetry,
            "authority": "COMPOSITION_ONLY",
            "law": "HATCH_INTEGRITY -> SOURCE_BOUND_ROOT; TELEMETRY != AUTHORITY",
        }

    def _execute_population(
        self,
        operation: str,
        route: Mapping[str, Any],
        *,
        child_return: Mapping[str, Any] | None,
        min_score: float,
        limit: int,
        remote: str,
        shared_remote_mode: str,
    ) -> dict:
        if operation == "PUBLISH":
            return self.population.publish(route, remote)
        if operation == "MATCH":
            return self.population.match(route, min_score, limit, remote, shared_remote_mode)
        if operation == "HANDOFF":
            return self.population.handoff(route, remote)
        if operation == "CLAIM_STATE":
            return self.population.claim_state(route, remote, shared_remote_mode)
        if operation == "RETURN_CHECK":
            if not isinstance(child_return, Mapping):
                return {
                    "status": "TSE_POPULATION_RETURN_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "child_return_required",
                    "route": copy.deepcopy(route),
                }
            return self.population.return_check(route, child_return, remote, shared_remote_mode)
        raise ValueError(f"unsupported operation: {operation}")

    def advance(
        self,
        *,
        mission_id: str,
        operation: str,
        route: Mapping[str, Any],
        parent_event_id: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        child_return: Mapping[str, Any] | None = None,
        min_score: float = 0.0,
        limit: int = 10,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        operation = str(operation or "").upper()
        if operation not in _OPERATION_TRANSITION:
            return {
                "status": "TSE_HELIX_ADVANCE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "unsupported_operation",
            }
        errors = _validate_route(route)
        if errors:
            return {
                "status": "TSE_HELIX_ADVANCE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "errors": errors,
            }

        result = self._execute_population(
            operation,
            route,
            child_return=child_return,
            min_score=min_score,
            limit=limit,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        out_route = self._result_route(result, route)
        expected = _OPERATION_SUCCESS[operation]
        if result.get("status") != expected:
            telemetry = self._record_hold(
                mission_id=mission_id,
                route=out_route,
                operation=operation,
                actor_id=actor_id,
                witnesses=witnesses,
                cost=cost,
                parent_event_id=parent_event_id,
                result=result,
                remote=remote,
            )
            return {
                "status": "TSE_HELIX_POPULATION_HOLD",
                "hold": result.get("hold") or "EVIDENCE_HOLD",
                "population": result,
                "route": out_route,
                "telemetry": telemetry,
                "population_result_valid": True,
                "law": "SOURCE_HOLD_REMAINS_SOURCE_HOLD; TELEMETRY != AUTHORITY",
            }

        source = self._source_from_result(operation, out_route, result)
        transition = _OPERATION_TRANSITION[operation]
        child_agent_id = None
        child_claim_id = None
        verified_delta = None
        if transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN"}:
            claim = out_route.get("child_claim") or {}
            child_agent_id = claim.get("agent_id")
            child_claim_id = claim.get("claim_id")
        if transition == "CHILD_VERIFIED_RETURN":
            returned = result.get("return_payload") or {}
            verified_delta = returned.get("verified_delta")

        telemetry = self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=out_route["route_id"],
            hatch_id=out_route["hatch_id"],
            transition=transition,
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind=source["kind"],
            source_ref=source["ref"],
            source_payload=source["payload"],
            source_git_head=source["git_head"],
            source_authority=source["authority"],
            parent_event_id=parent_event_id,
            child_agent_id=child_agent_id,
            child_claim_id=child_claim_id,
            verified_delta=verified_delta,
            attempt_ref=source["ref"],
            remote=remote,
        )
        if telemetry.get("status") not in {
            "TSE_TELEMETRY_RECORDED_SOURCE_BOUND",
            "TSE_TELEMETRY_ALREADY_RECORDED",
        }:
            return {
                "status": "TSE_HELIX_ACTION_VALID_TELEMETRY_HOLD",
                "population": result,
                "route": out_route,
                "telemetry": telemetry,
                "population_result_valid": True,
                "authoritative_mutation_may_already_be_durable": operation in {"PUBLISH", "HANDOFF"},
                "recovery": {
                    "operation": operation,
                    "parent_event_id": parent_event_id,
                    "source_ref": source["ref"],
                },
                "law": "TELEMETRY_FAILURE != ROLLBACK_OF_SOURCE_AUTHORITY",
            }
        return {
            "status": "TSE_HELIX_ADVANCED",
            "operation": operation,
            "transition": transition,
            "route": out_route,
            "event_id": telemetry["event"]["event_id"],
            "population": result,
            "telemetry": telemetry,
            "authority": "COMPOSITION_ONLY",
            "law": "SOURCE_ACTION -> SOURCE_BOUND_OBSERVATION; OBSERVATION != AUTHORITY",
        }

    def observe_consumption(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        parent_event_id: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        errors = _validate_route(route)
        if errors or not route.get("handoff_message_id") or not route.get("selected_match"):
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "EVIDENCE_HOLD",
                "errors": errors or ["routed_handoff_required"],
            }
        board = self.cohesion._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=500)
        if not snapshot.get("shared_frontier_verified"):
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "STALE_STATE_HOLD",
                "reason": "shared_frontier_unverified",
                "message_board": snapshot,
            }

        message_id = str(route["handoff_message_id"])
        child_agent = str((route.get("selected_match") or {}).get("agent_id") or "")
        events = board._events()
        message = next(
            (
                event
                for event in events
                if event.get("event_id") == message_id
                and event.get("kind") == "MESSAGE"
            ),
            None,
        )
        if not message:
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_message_missing",
            }
        if str(message.get("agent_id") or "") != str(route.get("parent_agent_id") or ""):
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_sender_mismatch",
            }
        if child_agent not in [str(value) for value in (message.get("recipients") or [])]:
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_recipient_mismatch",
            }
        payload = message.get("payload") or {}
        if str(payload.get("message_kind") or "") != "HANDOFF":
            return {
                "status": "TSE_HELIX_CONSUMPTION_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_message_kind_mismatch",
            }

        ack = next(
            (
                event
                for event in events
                if event.get("kind") == "ACK"
                and str(event.get("agent_id") or "") == child_agent
                and str((event.get("payload") or {}).get("message_id") or "") == message_id
            ),
            None,
        )
        if not ack:
            return {
                "status": "TSE_HELIX_CONSUMPTION_PENDING",
                "hold": "ROUTED_NOT_CONSUMED",
                "route": copy.deepcopy(route),
                "message_board": snapshot,
                "telemetry": None,
                "law": "ROUTE != CONSUMPTION; ABSENT_ACK != CLAIM_FAILURE",
            }

        source_payload = {
            "handoff_message_id": message_id,
            "message_event": message,
            "ack_event": ack,
            "route": self._route_identity(route),
        }
        source_ref = str(ack.get("event_id") or f"ACK-{_short(source_payload)}")
        telemetry = self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=route["route_id"],
            hatch_id=route["hatch_id"],
            transition="HANDOFF_CONSUMED",
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind="MESSAGE_BOARD_HANDOFF_ACK",
            source_ref=source_ref,
            source_payload=source_payload,
            source_git_head=snapshot.get("git_head") or self.server.git.head(),
            source_authority="MESSAGE_BOARD_ACK_STATE",
            parent_event_id=parent_event_id,
            attempt_ref=source_ref,
            remote=remote,
        )
        if telemetry.get("status") not in {
            "TSE_TELEMETRY_RECORDED_SOURCE_BOUND",
            "TSE_TELEMETRY_ALREADY_RECORDED",
        }:
            return {
                "status": "TSE_HELIX_CONSUMPTION_TELEMETRY_HOLD",
                "route": copy.deepcopy(route),
                "telemetry": telemetry,
                "consumption_observed": True,
                "law": "TELEMETRY_FAILURE != ACK_INVALIDATION",
            }
        out = copy.deepcopy(route)
        out["handoff_ack_event_id"] = source_ref
        out["status"] = "HANDOFF_CONSUMED_NOT_CLAIMED"
        return {
            "status": "TSE_HELIX_HANDOFF_CONSUMED",
            "route": out,
            "event_id": telemetry["event"]["event_id"],
            "telemetry": telemetry,
            "consumption_observed": True,
            "claim_authority": False,
            "law": "ACK -> CONSUMPTION_OBSERVED; ACK != CLAIM",
        }

    def reconcile(
        self,
        *,
        mission_id: str,
        operation: str,
        route: Mapping[str, Any],
        parent_event_id: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        child_return: Mapping[str, Any] | None = None,
        min_score: float = 0.0,
        limit: int = 10,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        """Re-derive a missing source-bound event without replaying source mutation."""
        operation = str(operation or "").upper()
        errors = _validate_route(route)
        if errors or operation not in _OPERATION_TRANSITION:
            return {
                "status": "TSE_HELIX_RECONCILE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "errors": errors or ["unsupported_operation"],
            }

        probe_route = copy.deepcopy(route)
        if operation == "PUBLISH":
            board = self.cohesion._board()
            snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=500)
            if not snapshot.get("shared_frontier_verified"):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "STALE_STATE_HOLD",
                    "reason": "shared_frontier_unverified",
                }
            row = self.cohesion._request_by_id(board, route["need_args"]["request_id"])
            if not row:
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "published_need_not_found",
                }
            request = row["payload"]
            if (
                request.get("request_digest") != route.get("cohesion_request_digest")
                or request.get("board_claim_id") != route.get("parent_board_claim_id")
            ):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "published_need_binding_mismatch",
                }
            result = {
                "status": _OPERATION_SUCCESS[operation],
                "route": copy.deepcopy(route),
                "cohesion": {"request": request, "event": row["event"], "git_head": snapshot.get("git_head")},
            }

        elif operation == "MATCH":
            probe_route["status"] = "NEED_PUBLISHED"
            result = self.population.match(probe_route, min_score, limit, remote, shared_remote_mode)
            if result.get("status") != _OPERATION_SUCCESS[operation]:
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": result.get("hold") or "EVIDENCE_HOLD",
                    "reason": "current_match_cannot_reproduce_historical_match",
                    "probe": result,
                }
            current = (result.get("route") or {}).get("selected_match") or {}
            expected = route.get("selected_match") or {}
            keys = ("agent_id", "offer_id", "coordination_treatment")
            if any(str(current.get(key)) != str(expected.get(key)) for key in keys):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "STALE_STATE_HOLD",
                    "reason": "current_match_differs_from_route_match",
                }
            result["route"] = copy.deepcopy(route)

        elif operation == "HANDOFF":
            board = self.cohesion._board()
            snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=500)
            if not snapshot.get("shared_frontier_verified"):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "STALE_STATE_HOLD",
                    "reason": "shared_frontier_unverified",
                }
            event = next(
                (
                    event
                    for event in board._events()
                    if event.get("event_id") == route.get("handoff_message_id")
                    and event.get("kind") == "MESSAGE"
                ),
                None,
            )
            if not event:
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "handoff_message_missing",
                }
            result = {
                "status": _OPERATION_SUCCESS[operation],
                "route": copy.deepcopy(route),
                "message_board": {"message_event": event, "git_head": snapshot.get("git_head")},
            }

        elif operation == "CLAIM_STATE":
            result = self.population.claim_state(route, remote, shared_remote_mode)
            if result.get("status") != _OPERATION_SUCCESS[operation]:
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": result.get("hold") or "EVIDENCE_HOLD",
                    "reason": "current_claim_cannot_reproduce_route_claim",
                    "probe": result,
                }
            current = (result.get("route") or {}).get("child_claim") or {}
            expected = route.get("child_claim") or {}
            if current.get("claim_id") != expected.get("claim_id"):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "AUTHORITY_HOLD",
                    "reason": "current_claim_differs_from_route_claim",
                }
            result["route"] = copy.deepcopy(route)

        elif operation == "RETURN_CHECK":
            if not isinstance(child_return, Mapping):
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "child_return_required",
                }
            result = self.population.return_check(route, child_return, remote, shared_remote_mode)
            if result.get("status") != _OPERATION_SUCCESS[operation]:
                return {
                    "status": "TSE_HELIX_RECONCILE_HOLD",
                    "hold": result.get("hold") or "EVIDENCE_HOLD",
                    "reason": "return_check_no_longer_valid",
                    "probe": result,
                }
            result["route"] = copy.deepcopy(route)

        else:
            raise AssertionError(operation)

        out_route = self._result_route(result, route)
        source = self._source_from_result(operation, out_route, result)
        transition = _OPERATION_TRANSITION[operation]
        claim = out_route.get("child_claim") or {}
        returned = result.get("return_payload") or {}
        telemetry = self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=out_route["route_id"],
            hatch_id=out_route["hatch_id"],
            transition=transition,
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind=source["kind"],
            source_ref=source["ref"],
            source_payload=source["payload"],
            source_git_head=source["git_head"],
            source_authority=source["authority"],
            parent_event_id=parent_event_id,
            child_agent_id=claim.get("agent_id") if transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN"} else None,
            child_claim_id=claim.get("claim_id") if transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN"} else None,
            verified_delta=returned.get("verified_delta") if transition == "CHILD_VERIFIED_RETURN" else None,
            attempt_ref=source["ref"],
            remote=remote,
        )
        if telemetry.get("status") not in {
            "TSE_TELEMETRY_RECORDED_SOURCE_BOUND",
            "TSE_TELEMETRY_ALREADY_RECORDED",
        }:
            return {
                "status": "TSE_HELIX_RECONCILE_TELEMETRY_HOLD",
                "telemetry": telemetry,
                "source_reverified": True,
            }
        return {
            "status": "TSE_HELIX_RECONCILED",
            "operation": operation,
            "transition": transition,
            "event_id": telemetry["event"]["event_id"],
            "telemetry": telemetry,
            "source_reverified": True,
            "law": "RECONCILIATION RE-DERIVES SOURCE; IT DOES NOT REPLAY SOURCE MUTATION",
        }

    @staticmethod
    def resource() -> dict:
        return {
            "version": HELIX_VERSION,
            "artifact": "ATHENA.TSE.HELICAL.HANDOFF.COMPOSITION.V2",
            "flow": [
                "HATCH_SOURCE_BOUND_ROOT",
                "POPULATION_PUBLISH",
                "POPULATION_MATCH",
                "MESSAGE_BOARD_HANDOFF",
                "OPTIONAL_HANDOFF_ACK_OBSERVATION",
                "MESSAGE_BOARD_CHILD_CLAIM",
                "TSE_CHILD_RETURN_CHECK",
                "EXTERNAL_RETURN_APPLICATION_PENDING",
            ],
            "source_bound_operations": sorted(_OPERATION_TRANSITION),
            "return_applied_source": "NOT_AVAILABLE_IN_THIS_OPERATIONAL_SURFACE",
            "authority": "COMPOSITION_ONLY",
            "laws": [
                "SOURCE_ACTION != TELEMETRY",
                "TELEMETRY != SOURCE_AUTHORITY",
                "TELEMETRY_FAILURE != SOURCE_ROLLBACK",
                "DECLARED_EVENT != SOURCE_BOUND_EVENT",
                "ROUTE != CONSUMPTION",
                "ACK != CLAIM",
                "MATCH != CLAIM",
                "RETURN_READY != RETURN_APPLIED",
                "RETURN_APPLIED_REQUIRES_EXTERNAL_OPERATIONAL_SOURCE_ADAPTER",
            ],
        }
