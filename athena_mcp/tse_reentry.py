from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterable

from .frontier_runtime import DEFAULT_SOURCE_REF
from .prompt_runtime import PromptRuntime
from .rehydration_loop import LOOP_ROOT, RehydrationLoopRuntime
from .rehydration_successor import SuccessorCompiler, _dominates
from .tse_population import _public_errors, _validate_hatch, _validate_route
from .tse_telemetry import SOURCE_BOUND, _digest, _finite_nonnegative, _require_id

REENTRY_VERSION = "TSE.REENTRY.SUCCESSION.1"
REENTRY_PACKET_VERSION = "ATHENA.TSE.REENTRY.PACKET.V1"
REENTRY_MARKER = "ATHENA_TSE_REENTRY_V1"
_MARKER_RE = re.compile(r"^\[\[ATHENA_TSE_REENTRY_V1 id=([^ ]+) digest=([^\]]+)\]\]")


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _hold(reason: str, *, hold: str = "EVIDENCE_HOLD", **extra: Any) -> dict:
    return {
        "status": "TSE_REENTRY_HOLD",
        "hold": hold,
        "reason": reason,
        "reentry_started": False,
        "execution_authority": False,
        "background_execution": False,
        **extra,
    }


class TseReentryRuntime:
    """Bind SOURCE_BOUND RETURN_APPLIED to the next explicit rehydration cycle.

    Re-entry does not execute a task and does not decide world truth. PREVIEW is
    read-only with respect to semantic Git history. START delegates to the
    existing RehydrationLoopRuntime, preserving one continuation control plane.
    """

    def __init__(self, server, telemetry_runtime):
        self.server = server
        self.telemetry = telemetry_runtime

    @property
    def git(self):
        return self.server.git

    def _loop_runtime(self) -> RehydrationLoopRuntime:
        prompt = getattr(self.server, "prompt_runtime", None)
        if prompt is None:
            prompt = PromptRuntime(self.git)
            self.server.prompt_runtime = prompt
        runtime = getattr(prompt, "_rehydration_loop_runtime_v1", None)
        if runtime is None:
            runtime = RehydrationLoopRuntime(self.git, prompt)
            prompt._rehydration_loop_runtime_v1 = runtime
        return runtime

    def _is_ancestor(self, older: str, newer: str) -> bool:
        proc = subprocess.run(
            ["git", "-C", str(self.git.root), "merge-base", "--is-ancestor", older, newer],
            text=True,
            capture_output=True,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git ancestry check failed")
        return proc.returncode == 0

    def _event_commit(self, event_id: str) -> str | None:
        rel = self.telemetry._event_path(event_id)
        proc = subprocess.run(
            ["git", "-C", str(self.git.root), "log", "-n", "1", "--format=%H", "--", rel],
            text=True,
            capture_output=True,
        )
        if proc.returncode:
            return None
        return proc.stdout.strip() or None

    def _event(self, event_id: str) -> dict | None:
        return next((row for row in self.telemetry._events() if row.get("event_id") == event_id), None)

    @staticmethod
    def _goal_marker(reentry_id: str, reentry_digest: str) -> str:
        return f"[[{REENTRY_MARKER} id={reentry_id} digest={reentry_digest}]]"

    def _existing_loop(self, reentry_id: str, reentry_digest: str) -> dict | None:
        root = Path(self.git.root) / LOOP_ROOT
        if not root.is_dir():
            return None
        expected_prefix = f"[[{REENTRY_MARKER} id={reentry_id} digest="
        for path in sorted(root.glob("*/state.json")):
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            goal = str(state.get("goal") or "")
            if not goal.startswith(expected_prefix):
                continue
            match = _MARKER_RE.match(goal)
            if not match:
                continue
            existing_digest = match.group(2)
            return {
                "loop_id": state.get("loop_id"),
                "loop_status": state.get("status"),
                "step_index": state.get("step_index"),
                "task": state.get("task"),
                "state_digest": state.get("state_digest"),
                "chain_digest": state.get("chain_digest"),
                "checkpoint_parent_head": state.get("checkpoint_parent_head"),
                "reentry_digest": existing_digest,
                "digest_match": existing_digest == reentry_digest,
            }
        return None

    def _validate_applied(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        hatch: Mapping[str, Any],
        return_applied_event_id: str,
        remote: str,
    ) -> dict:
        errors = _validate_route(route) + _validate_hatch(hatch)
        if errors:
            return _hold("invalid_route_or_hatch", errors=sorted(set(errors)))
        try:
            mission_id = _require_id(mission_id, "mission_id")
            return_applied_event_id = _require_id(return_applied_event_id, "return_applied_event_id")
        except ValueError as exc:
            return _hold("invalid_identity", errors=[str(exc)])

        for key in ("hatch_id", "hatch_digest", "parent_checkpoint_digest"):
            if hatch.get(key) != route.get(key):
                return _hold(f"hatch_route_{key}_mismatch")

        event = self._event(return_applied_event_id)
        if not event:
            return _hold("return_applied_event_not_found")
        source = event.get("source") or {}
        claim = route.get("child_claim") or {}
        checks = {
            "mission_id": mission_id,
            "route_id": route.get("route_id"),
            "hatch_id": route.get("hatch_id"),
            "transition": "RETURN_APPLIED",
            "child_agent_id": claim.get("agent_id"),
            "child_claim_id": claim.get("claim_id"),
        }
        for key, expected in checks.items():
            if event.get(key) != expected:
                return _hold(f"return_applied_event_{key}_mismatch")
        if (
            source.get("verification") != SOURCE_BOUND
            or source.get("kind") != "TSE_SHARED_GIT_ADOPTION"
            or source.get("authority") != "FRESH_SHARED_GIT_ANCESTRY_ADOPTION"
        ):
            return _hold("return_applied_event_not_source_bound_shared_adoption")
        if not _finite_nonnegative(event.get("verified_delta")) or float(event["verified_delta"]) <= 0:
            return _hold("return_applied_positive_delta_required")

        parent_id = str(event.get("parent_event_id") or "")
        parent = self._event(parent_id)
        if not parent:
            return _hold("child_verified_return_parent_missing")
        parent_source = parent.get("source") or {}
        parent_checks = {
            "mission_id": mission_id,
            "route_id": route.get("route_id"),
            "hatch_id": route.get("hatch_id"),
            "transition": "CHILD_VERIFIED_RETURN",
            "child_agent_id": claim.get("agent_id"),
            "child_claim_id": claim.get("claim_id"),
        }
        for key, expected in parent_checks.items():
            if parent.get(key) != expected:
                return _hold(f"child_verified_return_{key}_mismatch")
        if parent_source.get("verification") != SOURCE_BOUND or parent_source.get("kind") != "TSE_RETURN_CHECK":
            return _hold("child_verified_return_not_source_bound_return_check")
        if float(parent.get("verified_delta") or 0) != float(event["verified_delta"]):
            return _hold("return_delta_lineage_mismatch")

        applied_semantic_head = str(source.get("git_head") or "")
        if not applied_semantic_head:
            return _hold("applied_semantic_head_missing")
        if str(event.get("git_parent") or "") != applied_semantic_head:
            return _hold("return_applied_git_parent_not_semantic_applied_head")

        sync = self.telemetry._sync(remote, "REQUIRED")
        if not sync.get("shared_frontier_verified"):
            return _hold("shared_frontier_unverified", hold="STALE_STATE_HOLD", remote_sync=sync)
        current_head = self.git.head()
        if sync.get("remote_head") != current_head:
            return _hold(
                "local_remote_phase_mismatch",
                hold="STALE_STATE_HOLD",
                current_head=current_head,
                remote_head=sync.get("remote_head"),
            )

        observation_commit = self._event_commit(return_applied_event_id)
        if not observation_commit:
            return _hold("return_applied_observation_commit_missing")
        try:
            if not self._is_ancestor(applied_semantic_head, current_head):
                return _hold("applied_semantic_head_not_in_current_shared_frontier", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(observation_commit, current_head):
                return _hold("return_applied_observation_not_in_current_shared_frontier", hold="STALE_STATE_HOLD")
        except RuntimeError as exc:
            return _hold("git_ancestry_check_failed", error=str(exc))

        return {
            "status": "TSE_REENTRY_APPLIED_BOUND",
            "mission_id": mission_id,
            "route_id": route.get("route_id"),
            "route_digest": route.get("route_digest"),
            "hatch_id": route.get("hatch_id"),
            "hatch_digest": route.get("hatch_digest"),
            "parent_checkpoint_digest": route.get("parent_checkpoint_digest"),
            "return_applied_event": event,
            "child_verified_return_event": parent,
            "applied_semantic_head": applied_semantic_head,
            "return_applied_observation_commit": observation_commit,
            "continuation_shared_head": current_head,
            "verified_delta": float(event["verified_delta"]),
            "remote_sync": sync,
        }

    @staticmethod
    def _routing(
        *,
        frontier: Mapping[str, Any],
        explicit_candidates: list[Any],
        parent_residuals: list[Any],
        policy: Mapping[str, Any] | None,
        allow_parent_residual_fallback: bool,
    ) -> dict:
        route_policy = SuccessorCompiler._policy(dict(policy or {}))
        rows: list[dict] = []
        ordinal = 0

        selected = frontier.get("selected")
        if selected:
            row = SuccessorCompiler._candidate(selected, "AGENT_NEXT_TASK", ordinal)
            ordinal += 1
            if row:
                rows.append(row)
        for raw in frontier.get("pareto_front") or []:
            row = SuccessorCompiler._candidate(raw, "AGENT_NEXT_TASK", ordinal)
            ordinal += 1
            if row:
                rows.append(row)
        for raw in frontier.get("residuals") or []:
            row = SuccessorCompiler._candidate(raw, "COMPLETION_RESIDUAL", ordinal)
            ordinal += 1
            if row:
                rows.append(row)
        for raw in explicit_candidates:
            row = SuccessorCompiler._candidate(raw, "EXPLICIT_CANDIDATE", ordinal)
            ordinal += 1
            if row:
                rows.append(row)
        if not rows and allow_parent_residual_fallback:
            for raw in parent_residuals:
                row = SuccessorCompiler._candidate(raw, "CURRENT_TASK_CONTINUATION", ordinal)
                ordinal += 1
                if row:
                    rows.append(row)

        rows = SuccessorCompiler._dedupe(rows)
        for row in rows:
            row["routing_score"] = SuccessorCompiler._score(row, route_policy)
        pareto = [row for row in rows if not any(_dominates(other, row) for other in rows if other is not row)]
        pareto = sorted(pareto, key=lambda x: (-x["routing_score"], x["task"].lower(), x["candidate_id"]))
        ties: list[dict] = []
        selected_row = None
        status = "NO_SUCCESSOR"
        if pareto:
            best = pareto[0]["routing_score"]
            ties = [row for row in pareto if abs(row["routing_score"] - best) <= route_policy["tie_epsilon"]]
            if len(ties) == 1:
                status = "SELECTED"
                selected_row = ties[0]
            else:
                status = "AMBIGUOUS"
        return {
            "status": status,
            "policy": route_policy,
            "candidates": rows,
            "pareto_candidate_ids": [row["candidate_id"] for row in pareto],
            "selected": selected_row,
            "ties": ties,
            "authority": "ROUTING_ONLY",
            "laws": [
                "SUCCESSOR_SCORE != EVIDENCE",
                "SUCCESSOR_SCORE != AUTHORITY",
                "AMBIGUITY != FAILURE",
                "TIE => PRESERVE",
            ],
        }

    def preview(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        hatch: Mapping[str, Any],
        return_applied_event_id: str,
        reentry_id: str,
        goal: str = "",
        successor_candidates: list[Any] | None = None,
        successor_policy: Mapping[str, Any] | None = None,
        profile: str | None = None,
        source_ref: str = DEFAULT_SOURCE_REF,
        use_frontier: bool = True,
        fetch: bool = True,
        allow_parent_residual_fallback: bool = False,
        terminal_request: bool = False,
        terminal_witnesses: Iterable[str] | None = None,
        remote: str = "origin",
    ) -> dict:
        packet_public = {
            "hatch": hatch,
            "successor_candidates": successor_candidates or [],
            "successor_policy": successor_policy or {},
            "platform_counter_reset_claimed": False,
        }
        errors = _public_errors(packet_public)
        if errors:
            return _hold("public_payload_invalid", errors=errors)
        try:
            reentry_id = _require_id(reentry_id, "reentry_id")
        except ValueError as exc:
            return _hold("invalid_reentry_id", errors=[str(exc)])
        if successor_candidates is not None and not isinstance(successor_candidates, list):
            return _hold("successor_candidates_must_be_array")
        if successor_policy is not None and not isinstance(successor_policy, Mapping):
            return _hold("successor_policy_must_be_object")

        bound = self._validate_applied(
            mission_id=mission_id,
            route=route,
            hatch=hatch,
            return_applied_event_id=return_applied_event_id,
            remote=remote,
        )
        if bound.get("status") != "TSE_REENTRY_APPLIED_BOUND":
            return bound

        human_goal = str(goal or "").strip() or f"Continue mission {mission_id} after verified shared TSE Return {return_applied_event_id}"
        semantic_basis = {
            "version": REENTRY_PACKET_VERSION,
            "reentry_id": reentry_id,
            "mission_id": mission_id,
            "route_id": route.get("route_id"),
            "route_digest": route.get("route_digest"),
            "hatch_id": hatch.get("hatch_id"),
            "hatch_digest": hatch.get("hatch_digest"),
            "parent_checkpoint_digest": hatch.get("parent_checkpoint_digest"),
            "return_applied_event_id": return_applied_event_id,
            "return_applied_semantic_digest": (bound["return_applied_event"].get("semantic_digest")),
            "return_applied_source_digest": ((bound["return_applied_event"].get("source") or {}).get("digest")),
            "applied_semantic_head": bound["applied_semantic_head"],
            "verified_delta": bound["verified_delta"],
            "goal": human_goal,
            "successor_candidates": successor_candidates or [],
            "successor_policy": dict(successor_policy or {}),
            "allow_parent_residual_fallback": bool(allow_parent_residual_fallback),
            "terminal_request": bool(terminal_request),
        }
        reentry_digest = _digest(semantic_basis)
        existing = self._existing_loop(reentry_id, reentry_digest)
        if existing:
            if not existing["digest_match"]:
                return _hold(
                    "changed_same_reentry_id_conflict",
                    existing_reentry_digest=existing["reentry_digest"],
                    requested_reentry_digest=reentry_digest,
                    existing_loop_id=existing.get("loop_id"),
                )
            return {
                "status": "TSE_REENTRY_ALREADY_STARTED",
                "reentry_id": reentry_id,
                "reentry_digest": reentry_digest,
                "existing_loop": existing,
                "applied_semantic_head": bound["applied_semantic_head"],
                "continuation_shared_head": bound["continuation_shared_head"],
                "reentry_started": True,
                "background_execution": False,
                "execution_authority": False,
                "law": "IDEMPOTENT_REENTRY_ID != BACKGROUND_EXECUTION",
            }

        terminal_witness_list = _names(terminal_witnesses)
        if terminal_request:
            if not terminal_witness_list:
                return _hold("terminal_request_requires_public_witness")
            return {
                "status": "TSE_REENTRY_STOP_REQUESTED",
                "reentry_id": reentry_id,
                "reentry_digest": reentry_digest,
                "terminal_witnesses": terminal_witness_list,
                "applied_semantic_head": bound["applied_semantic_head"],
                "continuation_shared_head": bound["continuation_shared_head"],
                "verified_delta": bound["verified_delta"],
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
                "authority": "CALLER_POLICY_REQUEST_ONLY",
                "law": "TERMINAL_REQUEST != VERIFIED_GLOBAL_TERMINALITY; START_BLOCKED",
            }

        loop = self._loop_runtime()
        frontier = loop._frontier_snapshot(
            task=human_goal,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
            use_frontier=use_frontier,
        )
        frontier_status = str(frontier.get("status") or "")
        if use_frontier and ("HOLD" in frontier_status or "ERROR" in frontier_status):
            return _hold(
                "frontier_unavailable_for_requested_reentry",
                hold="STALE_STATE_HOLD" if "STALE" in frontier_status else "EVIDENCE_HOLD",
                frontier=frontier,
                reentry_id=reentry_id,
                reentry_digest=reentry_digest,
            )

        checkpoint = hatch.get("parent_checkpoint") or {}
        parent_residuals = list(checkpoint.get("residual") or []) if isinstance(checkpoint, Mapping) else []
        routing = self._routing(
            frontier=frontier,
            explicit_candidates=list(successor_candidates or []),
            parent_residuals=parent_residuals,
            policy=successor_policy,
            allow_parent_residual_fallback=allow_parent_residual_fallback,
        )
        if routing["status"] == "NO_SUCCESSOR":
            return _hold(
                "no_successor_observed",
                hold="EVIDENCE_HOLD",
                reentry_id=reentry_id,
                reentry_digest=reentry_digest,
                applied_semantic_head=bound["applied_semantic_head"],
                continuation_shared_head=bound["continuation_shared_head"],
                frontier=frontier,
                routing=routing,
                law="NO_SUCCESSOR_OBSERVED != GLOBAL_TERMINALITY",
            )

        status = "TSE_REENTRY_READY" if routing["status"] == "SELECTED" else "TSE_REENTRY_AMBIGUOUS"
        preview_basis = {
            "reentry_digest": reentry_digest,
            "continuation_shared_head": bound["continuation_shared_head"],
            "return_applied_observation_commit": bound["return_applied_observation_commit"],
            "frontier_digest": frontier.get("frontier_digest"),
            "routing_status": routing["status"],
            "selected": (routing.get("selected") or {}).get("candidate_id"),
            "ties": [row.get("candidate_id") for row in routing.get("ties") or []],
        }
        return {
            "status": status,
            "version": REENTRY_VERSION,
            "reentry_id": reentry_id,
            "reentry_digest": reentry_digest,
            "preview_digest": _digest(preview_basis),
            "goal": human_goal,
            "applied_semantic_head": bound["applied_semantic_head"],
            "return_applied_observation_commit": bound["return_applied_observation_commit"],
            "continuation_shared_head": bound["continuation_shared_head"],
            "return_applied_event_id": return_applied_event_id,
            "child_verified_return_event_id": bound["child_verified_return_event"].get("event_id"),
            "verified_delta": bound["verified_delta"],
            "frontier": frontier,
            "routing": routing,
            "reentry_started": False,
            "background_execution": False,
            "execution_authority": False,
            "authority": "ROUTING_AND_FRESHNESS_ONLY",
            "laws": [
                "RETURN_APPLIED != NEXT_TASK_TRUTH",
                "RETURN_APPLIED != EXECUTION_AUTHORITY",
                "REENTRY_PREVIEW != BACKGROUND_EXECUTION",
                "APPLIED_SEMANTIC_HEAD != CONTINUATION_SHARED_HEAD",
                "SUCCESSOR_SCORE != EVIDENCE",
            ],
        }

    def start(
        self,
        *,
        mission_id: str,
        route: Mapping[str, Any],
        hatch: Mapping[str, Any],
        return_applied_event_id: str,
        reentry_id: str,
        actor_id: str,
        goal: str = "",
        successor_candidates: list[Any] | None = None,
        successor_policy: Mapping[str, Any] | None = None,
        profile: str | None = None,
        source_ref: str = DEFAULT_SOURCE_REF,
        use_frontier: bool = True,
        fetch: bool = True,
        allow_parent_residual_fallback: bool = False,
        allow_ambiguity_resolution: bool = False,
        terminal_request: bool = False,
        terminal_witnesses: Iterable[str] | None = None,
        max_steps: int = 64,
        max_no_progress: int = 3,
        max_prompt_chars: int = 32000,
        depth_mode: str = "deep",
        required_passes: list[str] | None = None,
        stop_conditions: list[str] | None = None,
        remote: str = "origin",
    ) -> dict:
        preview = self.preview(
            mission_id=mission_id,
            route=route,
            hatch=hatch,
            return_applied_event_id=return_applied_event_id,
            reentry_id=reentry_id,
            goal=goal,
            successor_candidates=successor_candidates,
            successor_policy=successor_policy,
            profile=profile,
            source_ref=source_ref,
            use_frontier=use_frontier,
            fetch=fetch,
            allow_parent_residual_fallback=allow_parent_residual_fallback,
            terminal_request=terminal_request,
            terminal_witnesses=terminal_witnesses,
            remote=remote,
        )
        if preview.get("status") == "TSE_REENTRY_ALREADY_STARTED":
            return preview
        if preview.get("status") == "TSE_REENTRY_STOP_REQUESTED":
            return preview
        if preview.get("status") not in {"TSE_REENTRY_READY", "TSE_REENTRY_AMBIGUOUS"}:
            return preview

        routing = preview["routing"]
        if preview["status"] == "TSE_REENTRY_READY":
            task = routing["selected"]["task"]
        else:
            if not allow_ambiguity_resolution:
                return _hold(
                    "successor_ambiguity_requires_explicit_resolution_permission",
                    reentry_id=preview["reentry_id"],
                    reentry_digest=preview["reentry_digest"],
                    routing=routing,
                    applied_semantic_head=preview["applied_semantic_head"],
                    continuation_shared_head=preview["continuation_shared_head"],
                )
            tasks = [row["task"] for row in routing.get("ties") or []]
            task = "Resolve successor ambiguity without silent scalarization among: " + " | ".join(tasks)

        marker = self._goal_marker(preview["reentry_id"], preview["reentry_digest"])
        marked_goal = marker + "\n" + preview["goal"]
        loop = self._loop_runtime()
        started = loop.start(
            goal=marked_goal,
            task=task,
            expected_git_head=preview["continuation_shared_head"],
            actor=actor_id,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
            use_frontier=use_frontier,
            shared_remote_mode="REQUIRED",
            max_steps=max_steps,
            max_no_progress=max_no_progress,
            max_prompt_chars=max_prompt_chars,
            depth_mode=depth_mode,
            required_passes=required_passes,
            stop_conditions=list(stop_conditions or []) + [
                f"Preserve TSE re-entry lineage {preview['reentry_id']}",
                "Do not claim background execution or platform/provider counter reset",
            ],
        )
        if started.get("status") != "STARTED":
            return {
                "status": "TSE_REENTRY_START_HOLD",
                "reentry_id": preview["reentry_id"],
                "reentry_digest": preview["reentry_digest"],
                "rehydration": started,
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
                "law": "REHYDRATION_START_HOLD != REENTRY_SUCCESS",
            }
        return {
            "status": "TSE_REENTRY_STARTED",
            "version": REENTRY_VERSION,
            "reentry_id": preview["reentry_id"],
            "reentry_digest": preview["reentry_digest"],
            "preview_digest": preview["preview_digest"],
            "applied_semantic_head": preview["applied_semantic_head"],
            "continuation_shared_head_before_start": preview["continuation_shared_head"],
            "return_applied_observation_commit": preview["return_applied_observation_commit"],
            "return_applied_event_id": preview["return_applied_event_id"],
            "verified_delta": preview["verified_delta"],
            "selected_task": task,
            "routing": routing,
            "rehydration": started,
            "reentry_started": True,
            "background_execution": False,
            "execution_authority": False,
            "authority": "EXPLICIT_REHYDRATION_START_ONLY",
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "RETURN_APPLIED -> REENTRY_READY != BACKGROUND_EXECUTION",
                "REHYDRATION_STARTED != TASK_EXECUTED",
                "SUCCESSOR_SCORE != EVIDENCE",
                "SUCCESSOR_SCORE != AUTHORITY",
                "REENTRY != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE_RESET",
            ],
        }
