from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterable

from .tse_population import _position_errors, _public_errors, _validate_hatch, _validate_route
from .tse_telemetry import SOURCE_BOUND, TELEMETRY_ROOT, _digest, _finite_nonnegative, _require_id

CIRCULATION_VERSION = "TSE.CLOSED.HELIX.CIRCULATION.1"
CIRCULATION_ARTIFACT = "ATHENA.TSE.CLOSED.HELIX.CIRCULATION.V1"
CIRCULATION_ROOT = f"{TELEMETRY_ROOT}/circulation"
CIRCULATION_RESOURCE_URI = "athena://tse-circulation/v1"
_REENTRY_MARKER_RE = re.compile(r"^\[\[ATHENA_TSE_REENTRY_V1 id=([^ ]+) digest=([^\]]+)\]\]")


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _hold(reason: str, *, hold: str = "EVIDENCE_HOLD", **extra: Any) -> dict:
    return {
        "status": "TSE_CIRCULATION_HOLD",
        "hold": hold,
        "reason": reason,
        "closed_cycle": False,
        "execution_authority": False,
        "causal_effect": "UNKNOWN",
        **extra,
    }


def _parent_position(hatch: Mapping[str, Any]) -> Mapping[str, Any] | None:
    direct = hatch.get("parent_git_position")
    if isinstance(direct, Mapping):
        return direct
    checkpoint = hatch.get("parent_checkpoint")
    if isinstance(checkpoint, Mapping) and isinstance(checkpoint.get("git_position"), Mapping):
        return checkpoint["git_position"]
    return None


def _known_cost(cost: Any) -> tuple[float | None, str | None]:
    if not isinstance(cost, Mapping):
        return None, "cost_not_mapping"
    if cost.get("known") is not True:
        return None, "cost_unknown"
    total = cost.get("total")
    if not _finite_nonnegative(total):
        return None, "known_cost_total_invalid_or_missing"
    return float(total), None


class TseCirculationRuntime:
    """Observe a closed TSE sequence from one incorporated Return to the next.

    This is measurement only. Git ancestry plus typed source lineage establishes a
    sequence witness, never causal treatment effect or execution authority.
    """

    def __init__(self, server, telemetry_runtime, reentry_runtime):
        self.server = server
        self.telemetry = telemetry_runtime
        self.reentry = reentry_runtime

    @property
    def git(self):
        return self.server.git

    def _root(self) -> Path:
        return self.telemetry._root()

    def _path(self, cycle_id: str) -> str:
        return f"{CIRCULATION_ROOT}/{_require_id(cycle_id, 'cycle_id')}.json"

    def _read(self, cycle_id: str) -> dict | None:
        return self.telemetry._read_json(self._root() / self._path(cycle_id))

    def _receipts(self) -> list[dict]:
        root = self._root() / CIRCULATION_ROOT
        if not root.is_dir():
            return []
        out = []
        for path in sorted(root.glob("*.json")):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(row, dict) and row.get("artifact") == CIRCULATION_ARTIFACT:
                out.append(row)
        return out

    def _is_ancestor(self, older: str, newer: str) -> bool:
        return self.reentry._is_ancestor(older, newer)

    def _event_commit(self, event_id: str) -> str | None:
        return self.reentry._event_commit(event_id)

    @staticmethod
    def _productive_receipt(receipt: Mapping[str, Any]) -> bool:
        completion = receipt.get("completion") or {}
        if not isinstance(completion, Mapping):
            return False
        try:
            progress_delta = float(completion.get("progress_delta") or 0.0)
        except (TypeError, ValueError):
            return False
        material = list(receipt.get("material_work_paths") or [])
        evidence = list(completion.get("evidence_refs") or [])
        return bool(
            completion.get("observed") is True
            and str(completion.get("status") or "").upper() in {"SUCCEEDED", "PARTIAL"}
            and math.isfinite(progress_delta)
            and progress_delta > 0
            and receipt.get("no_progress") is False
            and (material or evidence)
        )

    def _loop_evidence(self, loop_id: str, next_parent_head: str) -> dict:
        loop = self.reentry._loop_runtime()
        verification = loop.verify(loop_id)
        if verification.get("status") != "PASS":
            return _hold("rehydration_loop_integrity_hold", loop_verification=verification)
        try:
            state, paths = loop._read_state(loop_id)
        except Exception as exc:
            return _hold("rehydration_loop_state_unavailable", error=str(exc))

        goal = str(state.get("goal") or "")
        marker = _REENTRY_MARKER_RE.match(goal)
        if not marker:
            return _hold("rehydration_loop_missing_tse_reentry_marker")
        reentry_id, reentry_digest = marker.groups()
        base_head = str(state.get("base_head") or "")
        if not base_head:
            return _hold("rehydration_loop_base_head_missing")

        start_event_path = f"{paths['events']}/0000-start.json"
        start_commit = loop._path_last_commit(start_event_path)
        if not start_commit:
            return _hold("rehydration_loop_start_commit_missing")
        try:
            if not self._is_ancestor(base_head, start_commit):
                return _hold("rehydration_start_not_descendant_of_base", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(start_commit, next_parent_head):
                return _hold("next_hatch_parent_not_descendant_of_reentry_start", hold="STALE_STATE_HOLD")
        except Exception as exc:
            return _hold("rehydration_ancestry_check_failed", error=str(exc))

        rows = []
        productive = []
        no_progress_steps = 0
        material_paths = set()
        for receipt_path in state.get("receipt_paths") or []:
            path = self._root() / str(receipt_path)
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return _hold("rehydration_receipt_unreadable", receipt_path=receipt_path)
            receipt_commit = loop._path_last_commit(str(receipt_path))
            if not receipt_commit:
                return _hold("rehydration_receipt_commit_missing", receipt_path=receipt_path)
            try:
                before_next_hatch = self._is_ancestor(receipt_commit, next_parent_head)
            except Exception as exc:
                return _hold("receipt_ancestry_check_failed", receipt_path=receipt_path, error=str(exc))
            if not before_next_hatch:
                continue
            row = {
                "receipt_path": str(receipt_path),
                "receipt_digest": receipt.get("receipt_digest"),
                "receipt_commit": receipt_commit,
                "work_head": receipt.get("work_head"),
                "step_index": receipt.get("step_index"),
                "no_progress": bool(receipt.get("no_progress")),
                "completion_status": (receipt.get("completion") or {}).get("status"),
                "progress_delta": (receipt.get("completion") or {}).get("progress_delta"),
                "material_work_paths": sorted(set(receipt.get("material_work_paths") or [])),
                "evidence_refs": _names((receipt.get("completion") or {}).get("evidence_refs") or []),
                "productive": self._productive_receipt(receipt),
            }
            rows.append(row)
            if row["no_progress"]:
                no_progress_steps += 1
            material_paths.update(row["material_work_paths"])
            if row["productive"]:
                productive.append(row)

        if not rows:
            return _hold("no_observed_rehydration_receipt_before_next_hatch")
        if not productive:
            return _hold(
                "no_productive_rehydration_receipt_before_next_hatch",
                rehydration_steps_total=len(rows),
                no_progress_steps=no_progress_steps,
            )
        return {
            "status": "TSE_CIRCULATION_REHYDRATION_BOUND",
            "reentry_id": reentry_id,
            "reentry_digest": reentry_digest,
            "loop_id": loop_id,
            "loop_status": state.get("status"),
            "loop_state_digest": state.get("state_digest"),
            "loop_chain_digest": state.get("chain_digest"),
            "loop_base_head": base_head,
            "loop_start_commit": start_commit,
            "rehydration_steps_total": len(rows),
            "productive_rehydration_steps": len(productive),
            "no_progress_steps": no_progress_steps,
            "material_work_paths_unique": sorted(material_paths),
            "receipts_before_next_hatch": rows,
            "productive_receipts": productive,
            "loop_verification": verification,
        }

    def _route_cost(self, mission_id: str, route_id: str, hatch_id: str, through_commit: str) -> dict:
        known = 0.0
        known_events = []
        unknown = []
        for event in self.telemetry._events():
            if (
                event.get("mission_id") != mission_id
                or event.get("route_id") != route_id
                or event.get("hatch_id") != hatch_id
            ):
                continue
            event_commit = self._event_commit(str(event.get("event_id") or ""))
            if not event_commit:
                unknown.append({"event_id": event.get("event_id"), "reason": "event_commit_missing"})
                continue
            try:
                if not self._is_ancestor(event_commit, through_commit):
                    continue
            except Exception:
                unknown.append({"event_id": event.get("event_id"), "reason": "event_commit_ancestry_unknown"})
                continue
            if (event.get("source") or {}).get("verification") != SOURCE_BOUND:
                # Declared-only observations are attempt metadata, not primary source cost.
                continue
            value, reason = _known_cost(event.get("cost"))
            if reason:
                unknown.append({"event_id": event.get("event_id"), "reason": reason})
                continue
            known += float(value)
            known_events.append(str(event.get("event_id")))
        return {
            "known_source_bound_tse_cost_total": known,
            "known_cost_event_ids": known_events,
            "unknown_source_bound_tse_cost_events": unknown,
        }

    def observe(
        self,
        *,
        cycle_id: str,
        mission_id: str,
        origin_route: Mapping[str, Any],
        origin_hatch: Mapping[str, Any],
        origin_return_applied_event_id: str,
        reentry_id: str,
        rehydration_loop_id: str,
        next_route: Mapping[str, Any],
        next_hatch: Mapping[str, Any],
        next_return_applied_event_id: str,
        actor_id: str,
        witnesses: Iterable[str],
        remote: str = "origin",
    ) -> dict:
        public = {
            "origin_route": origin_route,
            "origin_hatch": origin_hatch,
            "next_route": next_route,
            "next_hatch": next_hatch,
            "platform_counter_reset_claimed": False,
        }
        errors = _public_errors(public)
        if errors:
            return _hold("public_payload_invalid", errors=errors)
        try:
            cycle_id = _require_id(cycle_id, "cycle_id")
            mission_id = _require_id(mission_id, "mission_id")
            reentry_id = _require_id(reentry_id, "reentry_id")
            rehydration_loop_id = _require_id(rehydration_loop_id, "rehydration_loop_id")
            origin_return_applied_event_id = _require_id(origin_return_applied_event_id, "origin_return_applied_event_id")
            next_return_applied_event_id = _require_id(next_return_applied_event_id, "next_return_applied_event_id")
            actor_id = _require_id(actor_id, "actor_id")
        except ValueError as exc:
            return _hold("invalid_identity", errors=[str(exc)])
        witness_list = _names(witnesses)
        if not witness_list:
            return _hold("witnesses_required")
        if origin_return_applied_event_id == next_return_applied_event_id:
            return _hold("origin_and_next_return_applied_events_must_differ")

        origin_errors = _validate_route(origin_route) + _validate_hatch(origin_hatch)
        next_errors = _validate_route(next_route) + _validate_hatch(next_hatch)
        if origin_errors or next_errors:
            return _hold("invalid_route_or_hatch", errors=sorted(set(origin_errors + next_errors)))
        if origin_route.get("hatch_id") == next_route.get("hatch_id"):
            return _hold("origin_and_next_hatch_must_differ")

        origin = self.reentry._validate_applied(
            mission_id=mission_id,
            route=origin_route,
            hatch=origin_hatch,
            return_applied_event_id=origin_return_applied_event_id,
            remote=remote,
        )
        if origin.get("status") != "TSE_REENTRY_APPLIED_BOUND":
            return _hold("origin_return_applied_not_bound", origin=origin)
        nxt = self.reentry._validate_applied(
            mission_id=mission_id,
            route=next_route,
            hatch=next_hatch,
            return_applied_event_id=next_return_applied_event_id,
            remote=remote,
        )
        if nxt.get("status") != "TSE_REENTRY_APPLIED_BOUND":
            return _hold("next_return_applied_not_bound", next=nxt)

        next_parent = _parent_position(next_hatch)
        position_errors = _position_errors(next_parent)
        if position_errors:
            return _hold("next_hatch_parent_position_required", errors=position_errors)
        next_parent_head = str(next_parent.get("head"))
        try:
            if not self._is_ancestor(origin["applied_semantic_head"], next_parent_head):
                return _hold("next_hatch_parent_not_descendant_of_origin_applied_state", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(origin["return_applied_observation_commit"], next_parent_head):
                return _hold("next_hatch_parent_not_descendant_of_origin_s7_observation", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(next_parent_head, nxt["applied_semantic_head"]):
                return _hold("next_hatch_parent_not_contained_in_next_applied_state", hold="STALE_STATE_HOLD")
        except Exception as exc:
            return _hold("cycle_git_ancestry_check_failed", error=str(exc))

        loop_evidence = self._loop_evidence(rehydration_loop_id, next_parent_head)
        if loop_evidence.get("status") != "TSE_CIRCULATION_REHYDRATION_BOUND":
            return loop_evidence
        if loop_evidence.get("reentry_id") != reentry_id:
            return _hold("reentry_id_loop_marker_mismatch")
        try:
            if not self._is_ancestor(origin["applied_semantic_head"], loop_evidence["loop_base_head"]):
                return _hold("reentry_loop_base_missing_origin_applied_state", hold="STALE_STATE_HOLD")
            if not self._is_ancestor(origin["return_applied_observation_commit"], loop_evidence["loop_base_head"]):
                return _hold("reentry_loop_base_missing_origin_s7_observation", hold="STALE_STATE_HOLD")
        except Exception as exc:
            return _hold("origin_to_reentry_ancestry_check_failed", error=str(exc))

        origin_event = origin["return_applied_event"]
        next_event = nxt["return_applied_event"]
        cost = self._route_cost(
            mission_id,
            str(next_route.get("route_id")),
            str(next_route.get("hatch_id")),
            nxt["return_applied_observation_commit"],
        )
        unknown_components = [
            "reentry_start_control_cost_not_persisted",
            "rehydration_execution_cost_not_persisted",
        ]
        if cost["unknown_source_bound_tse_cost_events"]:
            unknown_components.append("one_or_more_source_bound_tse_event_costs_unknown")
        known_cost = float(cost["known_source_bound_tse_cost_total"])
        incorporated_delta = float(next_event["verified_delta"])
        per_known = incorporated_delta / known_cost if known_cost > 0 else "UNKNOWN"

        productive_basis = [
            {
                "receipt_path": row["receipt_path"],
                "receipt_digest": row["receipt_digest"],
                "receipt_commit": row["receipt_commit"],
                "work_head": row["work_head"],
            }
            for row in loop_evidence["productive_receipts"]
        ]
        basis = {
            "version": CIRCULATION_VERSION,
            "cycle_id": cycle_id,
            "mission_id": mission_id,
            "origin": {
                "route_id": origin_route.get("route_id"),
                "route_digest": origin_route.get("route_digest"),
                "hatch_id": origin_hatch.get("hatch_id"),
                "hatch_digest": origin_hatch.get("hatch_digest"),
                "return_applied_event_id": origin_return_applied_event_id,
                "semantic_digest": origin_event.get("semantic_digest"),
                "source_digest": (origin_event.get("source") or {}).get("digest"),
                "applied_semantic_head": origin["applied_semantic_head"],
                "s7_observation_commit": origin["return_applied_observation_commit"],
            },
            "reentry": {
                "reentry_id": reentry_id,
                "reentry_digest": loop_evidence["reentry_digest"],
                "loop_id": rehydration_loop_id,
                "loop_base_head": loop_evidence["loop_base_head"],
                "loop_start_commit": loop_evidence["loop_start_commit"],
                "productive_receipts": productive_basis,
            },
            "next": {
                "route_id": next_route.get("route_id"),
                "route_digest": next_route.get("route_digest"),
                "hatch_id": next_hatch.get("hatch_id"),
                "hatch_digest": next_hatch.get("hatch_digest"),
                "next_hatch_parent_head": next_parent_head,
                "return_applied_event_id": next_return_applied_event_id,
                "semantic_digest": next_event.get("semantic_digest"),
                "source_digest": (next_event.get("source") or {}).get("digest"),
                "applied_semantic_head": nxt["applied_semantic_head"],
                "s7_observation_commit": nxt["return_applied_observation_commit"],
                "verified_incorporated_delta": incorporated_delta,
            },
            "authority": "SEQUENCE_OBSERVATION_ONLY",
        }
        semantic_digest = _digest(basis)
        path = self._path(cycle_id)

        def build(base_head: str):
            existing = self._read(cycle_id)
            if existing:
                if existing.get("semantic_digest") == semantic_digest:
                    return {
                        "return": {
                            "status": "TSE_CIRCULATION_ALREADY_OBSERVED",
                            "receipt": existing,
                            "closed_cycle": True,
                            "current_shared_frontier_revalidated": False,
                            "causal_effect": "UNKNOWN",
                        }
                    }
                return {
                    "return": {
                        "status": "TSE_CIRCULATION_ID_CONFLICT_HOLD",
                        "hold": "EVIDENCE_HOLD",
                        "cycle_id": cycle_id,
                        "existing_semantic_digest": existing.get("semantic_digest"),
                        "requested_semantic_digest": semantic_digest,
                        "closed_cycle": False,
                        "causal_effect": "UNKNOWN",
                    }
                }

            from .message_board import _iso

            receipt = {
                "artifact": CIRCULATION_ARTIFACT,
                **basis,
                "semantic_digest": semantic_digest,
                "status": "CLOSED_SEQUENCE_BOUND",
                "observed_at": _iso(),
                "git_parent": base_head,
                "current_shared_frontier_at_observation": nxt["continuation_shared_head"],
                "productive_rehydration_steps": loop_evidence["productive_rehydration_steps"],
                "rehydration_steps_total": loop_evidence["rehydration_steps_total"],
                "no_progress_steps": loop_evidence["no_progress_steps"],
                "material_work_paths_unique": loop_evidence["material_work_paths_unique"],
                "verified_incorporated_delta": incorporated_delta,
                **cost,
                "unknown_cost_components": unknown_components,
                "cost_complete": False,
                "incorporated_delta_per_known_source_bound_tse_cost": per_known,
                "incorporated_delta_per_total_cost": "UNKNOWN",
                "witnesses": witness_list,
                "execution_authority": False,
                "causal_effect": "UNKNOWN",
                "behavioral_treatment_effect": "UNKNOWN",
                "laws": [
                    "SEQUENCE_BOUND != CAUSAL_EFFECT",
                    "GIT_ANCESTRY != SEMANTIC_CAUSALITY",
                    "PRODUCTIVE_REHYDRATION_STEP != WALL_TIME",
                    "KNOWN_COST != TOTAL_COST",
                    "UNKNOWN_COST != ZERO_COST",
                    "CLOSED_CYCLE != RUN_FOREVER",
                ],
            }
            return {
                "files": {path: _json_text(receipt)},
                "message": f"observe closed TSE circulation cycle {cycle_id}",
                "result": {
                    "status": "TSE_CIRCULATION_OBSERVED",
                    "receipt": receipt,
                    "closed_cycle": True,
                    "current_shared_frontier_revalidated": True,
                    "execution_authority": False,
                    "causal_effect": "UNKNOWN",
                },
            }

        return self.telemetry._mutate(actor_id=actor_id, remote=remote, build_files=build)

    def report(self, *, mission_id: str | None = None, remote: str = "origin", shared_remote_mode: str = "REQUIRED") -> dict:
        if mission_id is not None:
            try:
                mission_id = _require_id(mission_id, "mission_id")
            except ValueError as exc:
                return _hold("invalid_mission_id", errors=[str(exc)])
        mode = str(shared_remote_mode or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            return _hold("invalid_shared_remote_mode")
        sync = self.telemetry._sync(remote, mode)
        if mode == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return _hold("shared_frontier_unverified", hold="STALE_STATE_HOLD", remote_sync=sync)

        rows = [row for row in self._receipts() if mission_id is None or row.get("mission_id") == mission_id]
        rows = sorted(rows, key=lambda row: str(row.get("cycle_id") or ""))
        delta = sum(float(row.get("verified_incorporated_delta") or 0.0) for row in rows)
        productive_steps = sum(int(row.get("productive_rehydration_steps") or 0) for row in rows)
        no_progress_steps = sum(int(row.get("no_progress_steps") or 0) for row in rows)
        known_cost = sum(float(row.get("known_source_bound_tse_cost_total") or 0.0) for row in rows)
        per_known = delta / known_cost if known_cost > 0 else "UNKNOWN"
        return {
            "status": "TSE_CIRCULATION_REPORT",
            "version": CIRCULATION_VERSION,
            "mission_id": mission_id,
            "closed_cycles": len(rows),
            "cycle_ids": [row.get("cycle_id") for row in rows],
            "verified_incorporated_delta_total": delta,
            "productive_rehydration_steps_total": productive_steps,
            "no_progress_steps_total": no_progress_steps,
            "known_source_bound_tse_cost_total": known_cost,
            "incorporated_delta_per_known_source_bound_tse_cost": per_known,
            "incorporated_delta_per_total_cost": "UNKNOWN",
            "cost_complete": bool(rows) and all(bool(row.get("cost_complete")) for row in rows),
            "pending_cycles": "UNKNOWN",
            "closure_rate": "UNKNOWN",
            "observation_model": "CLOSED_RECEIPTS_ONLY_NO_OPEN_WINDOW_MUTATION",
            "remote_sync": sync,
            "execution_authority": False,
            "causal_effect": "UNKNOWN",
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "CLOSED_RECEIPT_COUNT != TOTAL_STARTED_CYCLE_COUNT",
                "PENDING != FAILURE",
                "UNKNOWN_DENOMINATOR => CLOSURE_RATE_UNKNOWN",
                "SEQUENCE_BOUND != CAUSAL_EFFECT",
                "UNKNOWN_COST != ZERO_COST",
            ],
        }

    def resource(self) -> dict:
        return {
            "version": CIRCULATION_VERSION,
            "artifact": CIRCULATION_ARTIFACT,
            "resource_uri": CIRCULATION_RESOURCE_URI,
            "stored_receipts": len(self._receipts()),
            "observation_model": "CLOSED_RECEIPTS_ONLY_NO_OPEN_WINDOW_MUTATION",
            "authority": "MEASUREMENT_ONLY",
            "causal_effect": "UNKNOWN",
            "laws": [
                "SEQUENCE_BOUND != CAUSAL_EFFECT",
                "PRODUCTIVE_STEP != WALL_TIME",
                "KNOWN_COST != TOTAL_COST",
                "UNKNOWN_COST != ZERO_COST",
                "CYCLE_RECEIPT != EXECUTION_AUTHORITY",
            ],
        }
