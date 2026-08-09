from __future__ import annotations

import json
from collections.abc import Mapping

from .tse_helix import TseHelixRuntime
from .tse_knot_apply import TseKnotApplyRuntime
from .tse_population import TSE_HANDOFF_ARTIFACT, _validate_route
from .tse_reentry import REENTRY_PACKET_VERSION, TseReentryRuntime

INTEGRITY_VERSION = "TSE.HELICAL.HANDOFF.INTEGRITY.3"


class TseHelixIntegrityRuntime(TseHelixRuntime):
    """Strict handoff integrity, shared-Git apply, and explicit re-entry."""

    def __init__(self, server, population_runtime, telemetry_runtime, cohesion_runtime):
        super().__init__(server, population_runtime, telemetry_runtime, cohesion_runtime)
        self.knot_apply = TseKnotApplyRuntime(server, telemetry_runtime)
        self.reentry = TseReentryRuntime(server, telemetry_runtime)

    @staticmethod
    def _expected_handoff(route: Mapping[str, object]) -> dict:
        selected = route.get("selected_match") or {}
        need = route.get("need_args") or {}
        return {
            "artifact": TSE_HANDOFF_ARTIFACT,
            "route_id": route.get("route_id"),
            "route_digest": route.get("route_digest"),
            "hatch_id": route.get("hatch_id"),
            "hatch_digest": route.get("hatch_digest"),
            "parent_checkpoint_digest": route.get("parent_checkpoint_digest"),
            "parent_agent_id": route.get("parent_agent_id"),
            "candidate_agent_id": selected.get("agent_id") if isinstance(selected, Mapping) else None,
            "cohesion_need_id": need.get("request_id") if isinstance(need, Mapping) else None,
            "cohesion_offer_id": selected.get("offer_id") if isinstance(selected, Mapping) else None,
            "child_quest": route.get("child_quest"),
            "child_work_key": route.get("child_work_key"),
            "coordination_treatment": selected.get("coordination_treatment") if isinstance(selected, Mapping) else None,
            "assignment_authority": False,
            "claim_authority": False,
        }

    def _handoff_envelope_check(
        self,
        route: Mapping[str, object],
        *,
        remote: str,
        shared_remote_mode: str,
    ) -> dict:
        errors = _validate_route(route)
        if errors or not route.get("handoff_message_id") or not route.get("selected_match"):
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "errors": errors or ["routed_handoff_required"],
            }

        board = self.cohesion._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=500)
        if not snapshot.get("shared_frontier_verified"):
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "STALE_STATE_HOLD",
                "reason": "shared_frontier_unverified",
                "message_board": snapshot,
            }

        message_id = str(route["handoff_message_id"])
        message = next(
            (
                event
                for event in board._events()
                if event.get("event_id") == message_id and event.get("kind") == "MESSAGE"
            ),
            None,
        )
        if not message:
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_message_missing",
            }

        payload = message.get("payload") or {}
        if not isinstance(payload, Mapping) or str(payload.get("message_kind") or "") != "HANDOFF":
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_message_kind_mismatch",
            }

        raw = payload.get("message")
        if not isinstance(raw, str) or not raw.strip():
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_envelope_missing",
            }
        try:
            envelope = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_envelope_invalid_json",
            }
        if not isinstance(envelope, Mapping):
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_envelope_not_object",
            }

        expected = self._expected_handoff(route)
        mismatches = [key for key, value in expected.items() if envelope.get(key) != value]
        if mismatches:
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_envelope_binding_mismatch",
                "mismatches": sorted(mismatches),
                "message_id": message_id,
            }

        parent = str(route.get("parent_agent_id") or "")
        candidate = str((route.get("selected_match") or {}).get("agent_id") or "")
        if str(message.get("agent_id") or "") != parent:
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_sender_mismatch",
            }
        if candidate not in [str(value) for value in (message.get("recipients") or [])]:
            return {
                "status": "TSE_HELIX_HANDOFF_ENVELOPE_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "handoff_recipient_mismatch",
            }

        return {
            "status": "TSE_HELIX_HANDOFF_ENVELOPE_BOUND",
            "message_id": message_id,
            "envelope": dict(envelope),
            "message_board_git_head": snapshot.get("git_head"),
            "authority": "INTEGRITY_ONLY",
            "law": "HANDOFF_ENVELOPE_BINDING != CONSUMPTION != CLAIM",
        }

    @staticmethod
    def _reentry_packet(child_return: Mapping[str, object] | None) -> tuple[Mapping[str, object] | None, Mapping[str, object] | None, dict | None]:
        if not isinstance(child_return, Mapping):
            return None, None, {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "reentry_packet_required_in_child_return_field",
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        hatch = child_return.get("hatch")
        packet = child_return.get("reentry")
        if not isinstance(hatch, Mapping) or not isinstance(packet, Mapping):
            return None, None, {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "reentry_packet_requires_hatch_and_reentry",
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        if packet.get("schema_version") != REENTRY_PACKET_VERSION:
            return None, None, {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "reentry_packet_schema",
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        if packet.get("platform_counter_reset_claimed") is not False:
            return None, None, {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "platform_counter_reset_claimed_must_be_false",
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        return hatch, packet, None

    def advance(
        self,
        *,
        mission_id: str,
        operation: str,
        route: Mapping[str, object],
        parent_event_id: str,
        actor_id: str,
        witnesses,
        cost: Mapping[str, object],
        child_return: Mapping[str, object] | None = None,
        min_score: float = 0.0,
        limit: int = 10,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        operation = str(operation or "").upper()
        if operation == "APPLY":
            if not isinstance(child_return, Mapping):
                return {
                    "status": "TSE_KNOT_APPLY_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "apply_packet_required_in_child_return_field",
                    "return_applied": False,
                    "merge_authority": False,
                    "execution_authority": False,
                }
            hatch = child_return.get("hatch")
            apply_receipt = child_return.get("apply_receipt")
            if not isinstance(hatch, Mapping) or not isinstance(apply_receipt, Mapping):
                return {
                    "status": "TSE_KNOT_APPLY_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "reason": "apply_packet_requires_hatch_and_apply_receipt",
                    "return_applied": False,
                    "merge_authority": False,
                    "execution_authority": False,
                }
            return self.knot_apply.observe_apply(
                mission_id=mission_id,
                route=route,
                hatch=hatch,
                child_return_event_id=parent_event_id,
                apply_receipt=apply_receipt,
                actor_id=actor_id,
                witnesses=witnesses,
                cost=cost,
                remote=remote,
            )
        if operation in {"REENTRY_PREVIEW", "REENTRY_START"}:
            if str(shared_remote_mode or "REQUIRED").upper() != "REQUIRED":
                return {
                    "status": "TSE_REENTRY_HOLD",
                    "hold": "STALE_STATE_HOLD",
                    "reason": "reentry_requires_shared_remote_mode_required",
                    "reentry_started": False,
                    "background_execution": False,
                    "execution_authority": False,
                }
            hatch, packet, error = self._reentry_packet(child_return)
            if error:
                return error
            common = dict(
                mission_id=mission_id,
                route=route,
                hatch=hatch,
                return_applied_event_id=parent_event_id,
                reentry_id=packet.get("reentry_id"),
                goal=packet.get("goal", ""),
                successor_candidates=packet.get("successor_candidates"),
                successor_policy=packet.get("successor_policy"),
                profile=packet.get("profile"),
                source_ref=packet.get("source_ref", "athena-runtime-v3-candidate"),
                use_frontier=packet.get("use_frontier", True),
                fetch=packet.get("fetch", True),
                allow_parent_residual_fallback=packet.get("allow_parent_residual_fallback", False),
                terminal_request=packet.get("terminal_request", False),
                terminal_witnesses=packet.get("terminal_witnesses"),
                remote=remote,
            )
            if operation == "REENTRY_PREVIEW":
                return self.reentry.preview(**common)
            return self.reentry.start(
                **common,
                actor_id=actor_id,
                allow_ambiguity_resolution=packet.get("allow_ambiguity_resolution", False),
                max_steps=packet.get("max_steps", 64),
                max_no_progress=packet.get("max_no_progress", 3),
                max_prompt_chars=packet.get("max_prompt_chars", 32000),
                depth_mode=packet.get("depth_mode", "deep"),
                required_passes=packet.get("required_passes"),
                stop_conditions=packet.get("stop_conditions"),
            )
        return super().advance(
            mission_id=mission_id,
            operation=operation,
            route=route,
            parent_event_id=parent_event_id,
            actor_id=actor_id,
            witnesses=witnesses,
            cost=cost,
            child_return=child_return,
            min_score=min_score,
            limit=limit,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )

    def observe_consumption(
        self,
        *,
        mission_id: str,
        route: Mapping[str, object],
        parent_event_id: str,
        actor_id: str,
        witnesses,
        cost: Mapping[str, object],
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        binding = self._handoff_envelope_check(
            route,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        if binding.get("status") != "TSE_HELIX_HANDOFF_ENVELOPE_BOUND":
            return binding
        result = super().observe_consumption(
            mission_id=mission_id,
            route=route,
            parent_event_id=parent_event_id,
            actor_id=actor_id,
            witnesses=witnesses,
            cost=cost,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        if result.get("status") == "TSE_HELIX_HANDOFF_CONSUMED":
            result["handoff_envelope_bound"] = True
            result["integrity_version"] = INTEGRITY_VERSION
            result["law"] = "EXACT_HANDOFF_ENVELOPE + ACK -> CONSUMPTION_OBSERVED; ACK != CLAIM"
        return result
