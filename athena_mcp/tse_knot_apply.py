from __future__ import annotations

import copy
import subprocess
from collections.abc import Mapping
from typing import Any, Iterable

from .tse_population import (
    _finite_nonnegative,
    _position_errors,
    _public_errors,
    _validate_hatch,
    _validate_route,
)
from .tse_telemetry import SOURCE_BOUND, _digest

KNOT_APPLY_VERSION = "TSE.SELF.TIGHTENING.KNOT.APPLY.1"
KNOT_APPLY_RECEIPT = "ATHENA.TSE.KNOT.APPLY.RECEIPT.V1"
KNOT_RESOURCE_URI = "athena://tse-knot-apply/v1"


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _hold(reason: str, *, hold: str = "EVIDENCE_HOLD", **extra: Any) -> dict:
    return {
        "status": "TSE_KNOT_APPLY_HOLD",
        "hold": hold,
        "reason": reason,
        "return_applied": False,
        "merge_authority": False,
        "execution_authority": False,
        **extra,
    }


class TseKnotApplyRuntime:
    """Observe a real shared Git adoption and close TSE stage S7.

    This runtime never performs merge/rebase/cherry-pick/push. It proves that an
    externally completed Git adoption is already the current freshly verified
    shared frontier and that both the frozen parent and verified child commits
    are ancestors of that applied frontier. Only then may telemetry observe
    RETURN_APPLIED.
    """

    def __init__(self, server, telemetry_runtime):
        self.server = server
        self.telemetry = telemetry_runtime

    @property
    def git(self):
        return self.server.git

    @staticmethod
    def _parent_position(hatch: Mapping[str, Any]) -> Mapping[str, Any] | None:
        direct = hatch.get("parent_git_position")
        if isinstance(direct, Mapping):
            return direct
        checkpoint = hatch.get("parent_checkpoint")
        if isinstance(checkpoint, Mapping) and isinstance(checkpoint.get("git_position"), Mapping):
            return checkpoint["git_position"]
        return None

    def _commit_exists(self, sha: str) -> bool:
        proc = subprocess.run(
            ["git", "-C", str(self.git.root), "cat-file", "-e", f"{sha}^{{commit}}"],
            text=True,
            capture_output=True,
        )
        return proc.returncode == 0

    def _is_ancestor(self, older: str, newer: str) -> bool:
        proc = subprocess.run(
            ["git", "-C", str(self.git.root), "merge-base", "--is-ancestor", older, newer],
            text=True,
            capture_output=True,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git ancestry check failed")
        return proc.returncode == 0

    def _return_event(self, event_id: str) -> dict | None:
        return next(
            (row for row in self.telemetry._events() if str(row.get("event_id")) == str(event_id)),
            None,
        )

    @staticmethod
    def _stable_apply_payload(
        *,
        apply_id: str,
        parent_head: str,
        child_head: str,
        applied_head: str,
        child_return_event: Mapping[str, Any],
        route: Mapping[str, Any],
        hatch: Mapping[str, Any],
        apply_witnesses: Iterable[str],
    ) -> dict:
        source = child_return_event.get("source") or {}
        claim = route.get("child_claim") or {}
        return {
            "apply_id": apply_id,
            "mode": "ANCESTRY_ADOPTION",
            "parent_head": parent_head,
            "child_head": child_head,
            "applied_head": applied_head,
            "child_return_event_id": child_return_event.get("event_id"),
            "child_return_source_ref": source.get("ref"),
            "route_id": route.get("route_id"),
            "route_digest": route.get("route_digest"),
            "hatch_id": hatch.get("hatch_id"),
            "hatch_digest": hatch.get("hatch_digest"),
            "parent_checkpoint_digest": hatch.get("parent_checkpoint_digest"),
            "child_agent_id": claim.get("agent_id"),
            "child_claim_id": claim.get("claim_id"),
            "verified_delta": child_return_event.get("verified_delta"),
            "apply_witnesses": _names(apply_witnesses),
            "platform_counter_reset_claimed": False,
        }

    def _existing_apply_event(
        self,
        *,
        mission_id: str,
        route_id: str,
        hatch_id: str,
        apply_id: str,
    ) -> dict | None:
        for event in self.telemetry._events():
            source = event.get("source") or {}
            if (
                event.get("transition") == "RETURN_APPLIED"
                and event.get("mission_id") == mission_id
                and event.get("route_id") == route_id
                and event.get("hatch_id") == hatch_id
                and source.get("verification") == SOURCE_BOUND
                and source.get("kind") == "TSE_SHARED_GIT_ADOPTION"
                and source.get("ref") == apply_id
            ):
                return event
        return None

    def observe_apply(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        hatch: Mapping[str, Any],
        child_return_event_id: str,
        apply_receipt: Mapping[str, Any],
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        remote: str = "origin",
    ) -> dict:
        errors = _validate_route(route) + _validate_hatch(hatch) + _public_errors(apply_receipt)
        if errors:
            return _hold("invalid_route_hatch_or_apply_receipt", errors=sorted(set(errors)))
        if not isinstance(apply_receipt, Mapping):
            return _hold("apply_receipt_not_mapping")
        if apply_receipt.get("schema_version") != KNOT_APPLY_RECEIPT:
            return _hold("apply_receipt_schema")
        if apply_receipt.get("mode") != "ANCESTRY_ADOPTION":
            return _hold("unsupported_apply_mode")
        if apply_receipt.get("platform_counter_reset_claimed") is not False:
            return _hold("platform_counter_reset_claimed_must_be_false")

        required = ("apply_id", "parent_head", "child_head", "applied_head", "apply_witnesses")
        missing = [key for key in required if not apply_receipt.get(key)]
        if missing:
            return _hold("apply_receipt_missing_fields", missing=missing)
        if not isinstance(apply_receipt.get("apply_witnesses"), list) or not apply_receipt["apply_witnesses"]:
            return _hold("apply_witnesses_required")

        apply_id = str(apply_receipt["apply_id"])
        parent_head = str(apply_receipt["parent_head"])
        child_head = str(apply_receipt["child_head"])
        applied_head = str(apply_receipt["applied_head"])
        if child_head == parent_head:
            return _hold("child_head_equals_parent_head")

        for key, expected in (
            ("hatch_id", route.get("hatch_id")),
            ("hatch_digest", route.get("hatch_digest")),
            ("parent_checkpoint_digest", route.get("parent_checkpoint_digest")),
        ):
            if hatch.get(key) != expected:
                return _hold(f"hatch_route_{key}_mismatch")

        parent_position = self._parent_position(hatch)
        position_errors = _position_errors(parent_position)
        if position_errors:
            return _hold("parent_git_position_required", errors=position_errors)
        if str(parent_position.get("head")) != parent_head:
            return _hold("parent_head_mismatch")

        child_event = self._return_event(child_return_event_id)
        if not child_event:
            return _hold("child_return_event_not_found")
        source = child_event.get("source") or {}
        claim = route.get("child_claim") or {}
        event_checks = {
            "mission_id": mission_id,
            "route_id": route.get("route_id"),
            "hatch_id": route.get("hatch_id"),
            "transition": "CHILD_VERIFIED_RETURN",
            "child_agent_id": claim.get("agent_id"),
            "child_claim_id": claim.get("claim_id"),
        }
        for key, expected in event_checks.items():
            if child_event.get(key) != expected:
                return _hold(f"child_return_event_{key}_mismatch")
        if source.get("verification") != SOURCE_BOUND or source.get("kind") != "TSE_RETURN_CHECK":
            return _hold("child_return_event_not_source_bound_return_check")
        if str(source.get("git_head") or "") != child_head:
            return _hold("child_head_mismatch")
        if not _finite_nonnegative(child_event.get("verified_delta")) or float(child_event["verified_delta"]) <= 0:
            return _hold("child_return_event_positive_delta_required")

        stable_payload = self._stable_apply_payload(
            apply_id=apply_id,
            parent_head=parent_head,
            child_head=child_head,
            applied_head=applied_head,
            child_return_event=child_event,
            route=route,
            hatch=hatch,
            apply_witnesses=apply_receipt["apply_witnesses"],
        )
        expected_digest = _digest(stable_payload)
        existing = self._existing_apply_event(
            mission_id=mission_id,
            route_id=str(route["route_id"]),
            hatch_id=str(route["hatch_id"]),
            apply_id=apply_id,
        )
        if existing:
            existing_source = existing.get("source") or {}
            if (
                existing_source.get("digest") != expected_digest
                or existing.get("parent_event_id") != child_return_event_id
                or existing.get("child_agent_id") != claim.get("agent_id")
                or existing.get("child_claim_id") != claim.get("claim_id")
            ):
                return _hold(
                    "changed_same_apply_id_conflict",
                    existing_event_id=existing.get("event_id"),
                    existing_source_digest=existing_source.get("digest"),
                    requested_source_digest=expected_digest,
                )
            return {
                "status": "TSE_KNOT_APPLY_ALREADY_OBSERVED",
                "knot_status": "TIGHTENED_SHARED_GIT_HISTORICAL_REPLAY",
                "return_applied": True,
                "return_applied_event_id": existing.get("event_id"),
                "parent_head": parent_head,
                "child_head": child_head,
                "applied_head": applied_head,
                "child_return_event_id": child_return_event_id,
                "return_receipt_ref": source.get("ref"),
                "verified_delta": float(child_event["verified_delta"]),
                "current_shared_frontier_revalidated": False,
                "merge_authority": False,
                "execution_authority": False,
                "authority": "HISTORICAL_OBSERVATION_REPLAY_ONLY",
                "law": "IDEMPOTENT_REPLAY != CLAIM_THAT_APPLIED_HEAD_IS_STILL_CURRENT",
            }

        if not self.git.enabled:
            return _hold("git_disabled")
        if self.git._git("status", "--porcelain"):
            return _hold("dirty_worktree", hold="STALE_STATE_HOLD")

        sync = self.telemetry._sync(remote, "REQUIRED")
        if not sync.get("shared_frontier_verified"):
            return _hold("shared_frontier_unverified", hold="STALE_STATE_HOLD", remote_sync=sync)
        current_head = self.git.head()
        if current_head != applied_head or sync.get("remote_head") != applied_head:
            return _hold(
                "applied_head_not_current_shared_frontier",
                hold="STALE_STATE_HOLD",
                current_head=current_head,
                remote_head=sync.get("remote_head"),
                applied_head=applied_head,
            )

        for name, sha in (("parent", parent_head), ("child", child_head), ("applied", applied_head)):
            if not self._commit_exists(sha):
                return _hold(f"{name}_head_not_commit")
        try:
            if not self._is_ancestor(parent_head, applied_head):
                return _hold("parent_not_ancestor_of_applied", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(child_head, applied_head):
                return _hold("child_not_ancestor_of_applied", hold="STALE_STATE_HOLD")
            if self._is_ancestor(child_head, parent_head):
                return _hold("child_already_contained_in_frozen_parent")
        except RuntimeError as exc:
            return _hold("git_ancestry_check_failed", error=str(exc))

        telemetry = self.telemetry.record_source_bound(
            mission_id=mission_id,
            route_id=str(route["route_id"]),
            hatch_id=str(route["hatch_id"]),
            transition="RETURN_APPLIED",
            actor_id=actor_id,
            witnesses=_names(witnesses),
            cost=cost,
            source_kind="TSE_SHARED_GIT_ADOPTION",
            source_ref=apply_id,
            source_payload=stable_payload,
            source_git_head=applied_head,
            source_authority="FRESH_SHARED_GIT_ANCESTRY_ADOPTION",
            parent_event_id=child_return_event_id,
            child_agent_id=claim.get("agent_id"),
            child_claim_id=claim.get("claim_id"),
            verified_delta=float(child_event["verified_delta"]),
            attempt_ref=apply_id,
            remote=remote,
        )
        if telemetry.get("status") not in {
            "TSE_TELEMETRY_RECORDED_SOURCE_BOUND",
            "TSE_TELEMETRY_ALREADY_RECORDED",
        }:
            return _hold(
                "shared_adoption_valid_telemetry_append_failed",
                hold="EVIDENCE_HOLD",
                adoption_verified=True,
                telemetry=telemetry,
                recovery={
                    "apply_id": apply_id,
                    "child_return_event_id": child_return_event_id,
                    "source_digest": expected_digest,
                },
            )

        return {
            "status": "TSE_KNOT_APPLY_OBSERVED",
            "knot_status": "TIGHTENED_SHARED_GIT",
            "return_applied": True,
            "return_applied_event_id": telemetry["event"]["event_id"],
            "parent_head": parent_head,
            "child_head": child_head,
            "applied_head": applied_head,
            "child_return_event_id": child_return_event_id,
            "return_receipt_ref": source.get("ref"),
            "verified_delta": float(child_event["verified_delta"]),
            "current_shared_frontier_revalidated": True,
            "remote_sync": sync,
            "next_parent_git_position": {
                **dict(parent_position),
                "head": applied_head,
            },
            "merge_authority": False,
            "execution_authority": False,
            "authority": "OBSERVATION_OF_SHARED_ADOPTION_ONLY",
            "behavioral_treatment_effect": "UNKNOWN",
            "law": "SHARED_GIT_ADOPTION + SOURCE_BOUND_RETURN -> RETURN_APPLIED; KNOT_OBSERVATION != MERGE_AUTHORITY",
        }

    @staticmethod
    def resource() -> dict:
        return {
            "version": KNOT_APPLY_VERSION,
            "artifact": "ATHENA.TSE.SELF.TIGHTENING.KNOT.APPLY.V1",
            "mode": "OBSERVE_EXTERNAL_ANCESTRY_ADOPTION_ONLY",
            "transition": "CHILD_VERIFIED_RETURN -> RETURN_APPLIED",
            "source_kind": "TSE_SHARED_GIT_ADOPTION",
            "authority": "OBSERVATION_ONLY",
            "merge_authority": False,
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "RETURN_READY != RETURN_APPLIED",
                "CHILD_VERIFIED_RETURN != SHARED_ADOPTION",
                "LOCAL_COMMIT != SHARED_RETURN",
                "KNOT_OBSERVATION != MERGE_AUTHORITY",
                "PARENT_AND_CHILD_MUST_BOTH_BE_ANCESTORS_OF_CURRENT_SHARED_APPLIED_HEAD",
                "GIT_ANCESTRY_PROOF != CAUSAL_PERFORMANCE_PROOF",
                "RESEED != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE_RESET",
            ],
        }
