from __future__ import annotations

import copy
from collections.abc import Mapping

from .tse_telemetry import TseHelixTelemetryRuntime


class TseHelixTelemetryProxy:
    """Late-bind TSE telemetry and stabilize authoritative source coordinates.

    Server constructs the AOR development surface before assigning `server.git`,
    so the concrete telemetry runtime is created lazily. The proxy also strips
    observer-side Git drift from source kinds whose stable identity already
    lives in an authoritative Hatch/Message-Board/claim/Return receipt.

    This does not weaken freshness checks performed by the wrapped source. It
    only prevents telemetry's own Git commits from changing the identity of an
    otherwise identical source observation.
    """

    def __init__(self, server):
        self.server = server
        self._runtime = None

    def _get(self):
        runtime = self._runtime
        if runtime is None:
            if not hasattr(self.server, "git"):
                raise RuntimeError("TSE_TELEMETRY_GIT_NOT_READY")
            runtime = TseHelixTelemetryRuntime(self.server)
            self._runtime = runtime
        return runtime

    @staticmethod
    def _stable_source_kwargs(kwargs):
        out = dict(kwargs)
        kind = str(out.get("source_kind") or "")
        payload = copy.deepcopy(out.get("source_payload"))
        if not isinstance(payload, Mapping):
            return out
        payload = dict(payload)

        if kind == "TSE_HATCH_V2":
            # Hatch digest + parent checkpoint digest are the frozen source
            # identity. The observer HEAD is downstream telemetry state.
            out["source_git_head"] = None

        elif kind == "COHESION_NEED_PUBLICATION":
            event = payload.get("event") or payload.get("message_event") or {}
            if not isinstance(event, Mapping):
                event = {}
            out["source_git_head"] = event.get("git_parent")

        elif kind == "COHESION_ADVISORY_MATCH":
            # Cohesion already verified the shared frontier before producing the
            # advisory match. A later telemetry commit must not manufacture a
            # new match identity solely by moving Git HEAD.
            selected = payload.get("selected_match") or {}
            if isinstance(selected, Mapping):
                selected = dict(selected)
                selected.pop("match_git_head", None)
                payload["selected_match"] = selected
            payload.pop("match_git_head", None)
            out["source_git_head"] = None

        elif kind == "MESSAGE_BOARD_HANDOFF_ROUTE":
            event = payload.get("message_event") or {}
            if not isinstance(event, Mapping):
                event = {}
            out["source_git_head"] = event.get("git_parent")

        elif kind == "MESSAGE_BOARD_CHILD_CLAIM":
            claim = payload.get("child_claim") or {}
            if not isinstance(claim, Mapping):
                claim = {}
            payload.pop("message_board_git_head", None)
            out["source_git_head"] = claim.get("claim_base_head")

        elif kind == "TSE_RETURN_CHECK":
            returned = payload.get("return_payload") or {}
            position = returned.get("child_git_position") if isinstance(returned, Mapping) else None
            if not isinstance(position, Mapping):
                position = {}
            out["source_git_head"] = position.get("head")

        elif kind == "MESSAGE_BOARD_HANDOFF_ACK":
            ack = payload.get("ack_event") or {}
            if not isinstance(ack, Mapping):
                ack = {}
            out["source_git_head"] = ack.get("git_parent")

        out["source_payload"] = payload
        return out

    def record_source_bound(self, **kwargs):
        return self._get().record_source_bound(**self._stable_source_kwargs(kwargs))

    def __getattr__(self, name):
        return getattr(self._get(), name)
