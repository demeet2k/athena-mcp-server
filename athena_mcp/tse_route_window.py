from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from typing import Any, Iterable, Mapping

from .tse_telemetry import (
    DECLARED_ONLY,
    HOLD_TRANSITION,
    SOURCE_BOUND,
    SUCCESS_TRANSITIONS,
    TELEMETRY_ROOT,
    _finite_nonnegative,
)

WINDOW_VERSION = "TSE.HELIX.ROUTE.WINDOW.1"
WINDOW_ARTIFACT = "ATHENA.TSE.HELIX.ROUTE.WINDOW.V1"
WINDOW_ROOT = f"{TELEMETRY_ROOT}/windows"
WINDOW_RESOURCE_URI = "athena://tse-route-window/v1"

STAGES = (
    "HATCH_CREATED",
    "HATCH_NEED_PUBLISHED",
    "MATCH_FOUND",
    "HANDOFF_ROUTED",
    "HANDOFF_CONSUMED",
    "CHILD_CLAIMED",
    "CHILD_VERIFIED_RETURN",
    "RETURN_APPLIED",
)
SEAMS = ("PUBLISH", "MATCH", "HANDOFF", "CONSUMPTION", "CLAIM", "RETURN", "APPLY")
SEAM_ALIASES = {
    "PUBLISH": "PUBLISH",
    "MATCH": "MATCH",
    "HANDOFF": "HANDOFF",
    "CONSUMPTION": "CONSUMPTION",
    "HANDOFF_CONSUMED": "CONSUMPTION",
    "CLAIM": "CLAIM",
    "CLAIM_STATE": "CLAIM",
    "RETURN": "RETURN",
    "RETURN_CHECK": "RETURN",
    "APPLY": "APPLY",
    "RETURN_APPLIED": "APPLY",
}

CONVERSION_EDGES = {
    "eta_publish": {"from": "HATCH_CREATED", "to": "HATCH_NEED_PUBLISHED", "seam": "PUBLISH"},
    "eta_match": {"from": "HATCH_NEED_PUBLISHED", "to": "MATCH_FOUND", "seam": "MATCH"},
    "eta_handoff": {"from": "MATCH_FOUND", "to": "HANDOFF_ROUTED", "seam": "HANDOFF"},
    "eta_consumption": {"from": "HANDOFF_ROUTED", "to": "HANDOFF_CONSUMED", "seam": "CONSUMPTION"},
    # Preserve the original evaluation contract: claim conversion is measured from match.
    "eta_claim": {"from": "MATCH_FOUND", "to": "CHILD_CLAIMED", "seam": "CLAIM"},
    # Also expose the narrower route-to-claim conversion for diagnosis.
    "eta_claim_from_handoff": {"from": "HANDOFF_ROUTED", "to": "CHILD_CLAIMED", "seam": "CLAIM"},
    "eta_return": {"from": "CHILD_CLAIMED", "to": "CHILD_VERIFIED_RETURN", "seam": "RETURN"},
    "eta_apply": {"from": "CHILD_VERIFIED_RETURN", "to": "RETURN_APPLIED", "seam": "APPLY"},
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _require_id(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text or len(text) > 192 or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.:-" for char in text):
        raise ValueError(f"invalid {field}")
    return text


def _canonical_seam(value: Any) -> str:
    seam = str(value or "").strip().upper()
    if seam not in SEAM_ALIASES:
        raise ValueError(f"unknown seam: {value}")
    return SEAM_ALIASES[seam]


def _ratio(numerator: int, denominator: int):
    if denominator <= 0:
        return "UNKNOWN"
    return numerator / denominator


def _normalized_resolved_routes(value: Any) -> dict[str, list[str]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("resolved_routes must be an object")
    out: dict[str, list[str]] = {}
    for raw_seam, route_ids in value.items():
        seam = _canonical_seam(raw_seam)
        if not isinstance(route_ids, list):
            raise ValueError(f"resolved_routes[{raw_seam}] must be an array")
        out[seam] = _names(route_ids)
    return dict(sorted(out.items()))


class TseRouteWindowRuntime:
    """Observation-window and route-level projection for TSE Helix telemetry.

    Event volume remains an attempt/friction signal. Conversion is computed over
    unique source-bound routes and explicit observation maturity. Window state is
    observation scope only; it creates no execution, claim, life, stop or Return
    authority.
    """

    def __init__(self, server, telemetry_runtime):
        self.server = server
        self.telemetry = telemetry_runtime

    def _root(self):
        return self.telemetry._root()

    def _window_path(self, window_id: str) -> str:
        return f"{WINDOW_ROOT}/{_require_id(window_id, 'window_id')}.json"

    def _read_window(self, window_id: str) -> dict | None:
        return self.telemetry._read_json(self._root() / self._window_path(window_id))

    def _source_events(self, mission_id: str) -> list[dict]:
        return [
            row
            for row in self.telemetry._events()
            if row.get("mission_id") == mission_id
            and (row.get("source") or {}).get("verification") == SOURCE_BOUND
        ]

    def _declared_events(self, mission_id: str) -> list[dict]:
        return [
            row
            for row in self.telemetry._events()
            if row.get("mission_id") == mission_id
            and (row.get("source") or {}).get("verification") != SOURCE_BOUND
        ]

    def open(
        self,
        *,
        window_id: str,
        mission_id: str,
        actor_id: str,
        route_ids: Iterable[str] | None = None,
        source_refs: Iterable[str] | None = None,
        remote: str = "origin",
    ) -> dict:
        try:
            window_id = _require_id(window_id, "window_id")
            mission_id = _require_id(mission_id, "mission_id")
            actor_id = _require_id(actor_id, "actor_id")
            routes = [_require_id(value, "route_id") for value in _names(route_ids)]
        except ValueError as exc:
            return {"status": "TSE_ROUTE_WINDOW_OPEN_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}
        sources = _names(source_refs)
        basis = {
            "version": WINDOW_VERSION,
            "window_id": window_id,
            "mission_id": mission_id,
            "route_ids": routes,
            "route_scope": "EXPLICIT" if routes else "MISSION_DYNAMIC_UNTIL_CLOSE",
            "source_refs": sources,
            "authority": "OBSERVATION_SCOPE_ONLY",
        }
        request_digest = _digest(basis)
        path = self._window_path(window_id)

        def build(base_head: str):
            existing = self._read_window(window_id)
            if existing:
                if existing.get("open_request_digest") == request_digest:
                    return {"return": {"status": "TSE_ROUTE_WINDOW_ALREADY_OPEN", "window": existing}}
                return {
                    "return": {
                        "status": "TSE_ROUTE_WINDOW_ID_CONFLICT_HOLD",
                        "hold": "EVIDENCE_HOLD",
                        "window": existing,
                    }
                }
            window = {
                "artifact": WINDOW_ARTIFACT,
                **basis,
                "status": "OPEN",
                "opened_at": self.telemetry._events()[-1].get("created_at") if self.telemetry._events() else None,
                "open_git_parent": base_head,
                "open_request_digest": request_digest,
                "closed_at": None,
                "close_git_parent": None,
                "complete_seams": [],
                "resolved_routes": {},
                "close_source_refs": [],
                "close_request_digest": None,
                "behavioral_treatment_effect": "UNKNOWN",
            }
            # Wall-clock timestamp is metadata only and is deliberately excluded
            # from idempotent request identity.
            from .message_board import _iso
            window["opened_at"] = _iso()
            return {
                "files": {path: _json_text(window)},
                "message": f"open TSE route window {window_id}",
                "result": {"status": "TSE_ROUTE_WINDOW_OPENED", "window": window},
            }

        return self.telemetry._mutate(actor_id=actor_id, remote=remote, build_files=build)

    def close(
        self,
        *,
        window_id: str,
        mission_id: str,
        actor_id: str,
        complete_seams: Iterable[str],
        resolved_routes: Mapping[str, list[str]] | None = None,
        route_ids: Iterable[str] | None = None,
        source_refs: Iterable[str] | None = None,
        remote: str = "origin",
    ) -> dict:
        try:
            window_id = _require_id(window_id, "window_id")
            mission_id = _require_id(mission_id, "mission_id")
            actor_id = _require_id(actor_id, "actor_id")
            seams = sorted({_canonical_seam(value) for value in complete_seams})
            resolved = _normalized_resolved_routes(resolved_routes)
            requested_routes = [_require_id(value, "route_id") for value in _names(route_ids)]
        except ValueError as exc:
            return {"status": "TSE_ROUTE_WINDOW_CLOSE_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}
        close_sources = _names(source_refs)

        def build(base_head: str):
            existing = self._read_window(window_id)
            if not existing:
                return {"return": {"status": "TSE_ROUTE_WINDOW_CLOSE_HOLD", "hold": "EVIDENCE_HOLD", "reason": "window_not_found"}}
            if existing.get("mission_id") != mission_id:
                return {"return": {"status": "TSE_ROUTE_WINDOW_CLOSE_HOLD", "hold": "EVIDENCE_HOLD", "reason": "mission_mismatch"}}

            open_routes = _names(existing.get("route_ids"))
            discovered = _names(row.get("route_id") for row in self._source_events(mission_id))
            if open_routes:
                if requested_routes and requested_routes != open_routes:
                    return {"return": {"status": "TSE_ROUTE_WINDOW_CLOSE_HOLD", "hold": "EVIDENCE_HOLD", "reason": "explicit_route_scope_drift"}}
                frozen_routes = open_routes
            else:
                frozen_routes = requested_routes or discovered

            route_set = set(frozen_routes)
            for seam, rows in resolved.items():
                unknown = sorted(set(rows) - route_set)
                if unknown:
                    return {
                        "return": {
                            "status": "TSE_ROUTE_WINDOW_CLOSE_HOLD",
                            "hold": "EVIDENCE_HOLD",
                            "reason": "resolved_route_outside_window",
                            "seam": seam,
                            "route_ids": unknown,
                        }
                    }

            close_basis = {
                "window_id": window_id,
                "mission_id": mission_id,
                "route_ids": frozen_routes,
                "complete_seams": seams,
                "resolved_routes": resolved,
                "source_refs": close_sources,
            }
            close_digest = _digest(close_basis)
            if existing.get("status") == "CLOSED":
                if existing.get("close_request_digest") == close_digest:
                    return {"return": {"status": "TSE_ROUTE_WINDOW_ALREADY_CLOSED", "window": existing}}
                return {
                    "return": {
                        "status": "TSE_ROUTE_WINDOW_CLOSE_CONFLICT_HOLD",
                        "hold": "EVIDENCE_HOLD",
                        "window": existing,
                    }
                }

            from .message_board import _iso
            updated = copy.deepcopy(existing)
            updated.update(
                {
                    "status": "CLOSED",
                    "route_ids": frozen_routes,
                    "route_scope": "FROZEN_AT_CLOSE",
                    "closed_at": _iso(),
                    "close_git_parent": base_head,
                    "complete_seams": seams,
                    "resolved_routes": resolved,
                    "close_source_refs": close_sources,
                    "close_request_digest": close_digest,
                }
            )
            return {
                "files": {self._window_path(window_id): _json_text(updated)},
                "message": f"close TSE route window {window_id}",
                "result": {"status": "TSE_ROUTE_WINDOW_CLOSED", "window": updated},
            }

        return self.telemetry._mutate(actor_id=actor_id, remote=remote, build_files=build)

    def state(
        self,
        *,
        window_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        try:
            window_id = _require_id(window_id, "window_id")
        except ValueError as exc:
            return {"status": "TSE_ROUTE_WINDOW_STATE_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}
        sync = self.telemetry._sync(remote, shared_remote_mode)
        window = self._read_window(window_id)
        if str(shared_remote_mode).upper() == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return {"status": "TSE_ROUTE_WINDOW_STATE_HOLD", "hold": "STALE_STATE_HOLD", "remote_sync": sync, "window": window}
        if not window:
            return {"status": "TSE_ROUTE_WINDOW_STATE_HOLD", "hold": "EVIDENCE_HOLD", "reason": "window_not_found", "remote_sync": sync}
        return {
            "status": "TSE_ROUTE_WINDOW_STATE",
            "window": window,
            "remote_sync": sync,
            "shared_frontier_verified": bool(sync.get("shared_frontier_verified")),
            "authority": "OBSERVATION_SCOPE_ONLY",
        }

    @staticmethod
    def _route_projection(events: list[dict]) -> tuple[dict[str, dict], list[dict]]:
        hatch_by_route: dict[str, set[str]] = defaultdict(set)
        for event in events:
            route_id = str(event.get("route_id") or "")
            hatch_by_route[route_id].add(str(event.get("hatch_id") or ""))
        conflicts = [
            {"route_id": route_id, "hatch_ids": sorted(hatches)}
            for route_id, hatches in sorted(hatch_by_route.items())
            if len(hatches) != 1
        ]
        projection: dict[str, dict] = {}
        for event in events:
            route_id = str(event.get("route_id") or "")
            row = projection.setdefault(
                route_id,
                {
                    "route_id": route_id,
                    "hatch_id": str(event.get("hatch_id") or ""),
                    "attained": set(),
                    "success_attempts": defaultdict(int),
                    "hold_attempts": defaultdict(int),
                    "events": [],
                    "last_event": None,
                },
            )
            transition = str(event.get("transition") or "")
            row["events"].append(str(event.get("event_id") or ""))
            row["last_event"] = str(event.get("event_id") or "")
            if transition in SUCCESS_TRANSITIONS:
                row["attained"].add(transition)
                row["success_attempts"][transition] += 1
            elif transition == HOLD_TRANSITION:
                try:
                    seam = _canonical_seam(event.get("seam"))
                except ValueError:
                    seam = str(event.get("seam") or "UNKNOWN").upper()
                row["hold_attempts"][seam] += 1
        return projection, conflicts

    @staticmethod
    def _edge_report(
        projection: Mapping[str, Mapping[str, Any]],
        *,
        from_stage: str,
        to_stage: str,
        seam: str,
        complete_seams: set[str],
        resolved_routes: Mapping[str, list[str]],
    ) -> dict:
        eligible = {route_id for route_id, row in projection.items() if from_stage in row["attained"]}
        attained = {route_id for route_id in eligible if to_stage in projection[route_id]["attained"]}
        explicit_resolved = set(resolved_routes.get(seam) or []) & eligible
        if seam in complete_seams:
            mature = set(eligible)
            maturity_source = "WINDOW_COMPLETE_SEAM"
        else:
            mature = attained | explicit_resolved
            maturity_source = "SUCCESS_OR_EXPLICIT_RESOLVED_ROUTE"
        pending = eligible - mature
        failures = mature - attained
        lower = _ratio(len(attained), len(eligible))
        upper = (
            "UNKNOWN"
            if not eligible
            else (len(attained) + len(pending)) / len(eligible)
        )
        return {
            "from_stage": from_stage,
            "to_stage": to_stage,
            "seam": seam,
            "eligible_routes": len(eligible),
            "attained_routes": len(attained),
            "mature_routes": len(mature),
            "failed_mature_routes": len(failures),
            "pending_routes": len(pending),
            "resolved_eta": _ratio(len(attained), len(mature)),
            "attainment_lower": lower,
            "attainment_upper": upper,
            "maturity_source": maturity_source,
            "pending_route_ids": sorted(pending),
            "failed_mature_route_ids": sorted(failures),
        }

    def report(
        self,
        *,
        window_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        state = self.state(window_id=window_id, remote=remote, shared_remote_mode=shared_remote_mode)
        if state.get("status") != "TSE_ROUTE_WINDOW_STATE":
            return {"status": "TSE_ROUTE_WINDOW_REPORT_HOLD", **{key: value for key, value in state.items() if key != "status"}}
        window = state["window"]
        mission_id = str(window["mission_id"])
        source_events = self._source_events(mission_id)
        declared_events = self._declared_events(mission_id)

        scoped_ids = set(_names(window.get("route_ids")))
        if scoped_ids:
            source_events = [row for row in source_events if str(row.get("route_id")) in scoped_ids]
            declared_events = [row for row in declared_events if str(row.get("route_id")) in scoped_ids]
        elif window.get("status") == "OPEN":
            scoped_ids = {str(row.get("route_id")) for row in source_events}

        projection, conflicts = self._route_projection(source_events)
        if conflicts:
            return {
                "status": "TSE_ROUTE_WINDOW_REPORT_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "route_id_hatch_identity_conflict",
                "conflicts": conflicts,
                "window": window,
            }

        complete_seams = set(_names(window.get("complete_seams")))
        resolved_routes = window.get("resolved_routes") or {}
        edges = {
            name: self._edge_report(
                projection,
                from_stage=spec["from"],
                to_stage=spec["to"],
                seam=spec["seam"],
                complete_seams=complete_seams,
                resolved_routes=resolved_routes,
            )
            for name, spec in CONVERSION_EDGES.items()
        }

        stage_route_counts = {
            stage: sum(1 for row in projection.values() if stage in row["attained"])
            for stage in STAGES
        }
        stage_attempt_counts = {
            stage: sum(int(row["success_attempts"].get(stage, 0)) for row in projection.values())
            for stage in STAGES
        }
        retry_pressure = {
            stage: stage_attempt_counts[stage] - stage_route_counts[stage]
            for stage in STAGES
        }
        hold_pressure: dict[str, int] = {seam: 0 for seam in SEAMS}
        for row in projection.values():
            for seam, count in row["hold_attempts"].items():
                hold_pressure[seam] = hold_pressure.get(seam, 0) + int(count)

        known_cost_total = 0.0
        all_costs_known = True
        for event in source_events:
            cost = event.get("cost") or {}
            if cost.get("known") is True and _finite_nonnegative(cost.get("total")):
                known_cost_total += float(cost["total"])
            else:
                all_costs_known = False

        apply_events_by_route: dict[str, list[dict]] = defaultdict(list)
        for event in source_events:
            if event.get("transition") == "RETURN_APPLIED":
                apply_events_by_route[str(event.get("route_id"))].append(event)
        apply_multiplicity = {
            route_id: [str(row.get("event_id")) for row in rows]
            for route_id, rows in apply_events_by_route.items()
            if len(rows) > 1
        }
        if apply_multiplicity:
            applied_delta: Any = "UNKNOWN"
            eta_helix: Any = "UNKNOWN"
        else:
            applied_delta = sum(
                float(rows[0].get("verified_delta"))
                for rows in apply_events_by_route.values()
                if rows and _finite_nonnegative(rows[0].get("verified_delta"))
            )
            eta_helix = (
                applied_delta / known_cost_total
                if apply_events_by_route and all_costs_known and known_cost_total > 0
                else "UNKNOWN"
            )

        apply_channel_state = (
            "OBSERVED"
            if apply_events_by_route
            else "COMPLETE_ZERO" if "APPLY" in complete_seams else "UNAVAILABLE_OR_INCOMPLETE"
        )
        if apply_channel_state == "UNAVAILABLE_OR_INCOMPLETE":
            edges["eta_apply"]["resolved_eta"] = "UNKNOWN"
            edges["eta_apply"]["maturity_source"] = "APPLY_OBSERVATION_INCOMPLETE"

        route_rows = []
        for route_id, row in sorted(projection.items()):
            attained = [stage for stage in STAGES if stage in row["attained"]]
            route_rows.append(
                {
                    "route_id": route_id,
                    "hatch_id": row["hatch_id"],
                    "highest_stage": attained[-1] if attained else None,
                    "attained_stages": attained,
                    "success_attempts": {stage: int(row["success_attempts"].get(stage, 0)) for stage in STAGES if row["success_attempts"].get(stage, 0)},
                    "hold_attempts": dict(sorted((key, int(value)) for key, value in row["hold_attempts"].items())),
                    "last_event": row["last_event"],
                }
            )

        report_basis = {
            "window_id": window["window_id"],
            "mission_id": mission_id,
            "window_status": window["status"],
            "route_count": len(projection),
            "stage_route_counts": stage_route_counts,
            "stage_attempt_counts": stage_attempt_counts,
            "retry_pressure": retry_pressure,
            "hold_pressure": hold_pressure,
            "conversions": edges,
            "apply_channel_state": apply_channel_state,
            "known_cost_total": known_cost_total,
            "all_costs_known": all_costs_known,
            "applied_verified_delta": applied_delta,
            "eta_helix": eta_helix,
            "declared_event_count": len(declared_events),
            "source_bound_event_count": len(source_events),
            "apply_multiplicity_conflicts": apply_multiplicity,
        }
        return {
            "status": "TSE_ROUTE_WINDOW_REPORT",
            **report_basis,
            "routes": route_rows,
            "report_digest": _digest(report_basis),
            "window": window,
            "remote_sync": state.get("remote_sync"),
            "shared_frontier_verified": state.get("shared_frontier_verified"),
            "authority": "OBSERVATION_PROJECTION_ONLY",
            "causal_promotion_authority": False,
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "EVENT_COUNT != ROUTE_COUNT",
                "RETRY_COUNT != CONVERSION",
                "PENDING != FAILURE",
                "ABSENCE_OF_APPLY_EVENT != ZERO_APPLY_RATE_WITHOUT_COMPLETE_APPLY_WINDOW",
                "ACK_CONSUMPTION_IS_OPTIONAL_SIDE_CHANNEL_NOT_CLAIM_PREDECESSOR",
                "WINDOW_SCOPE != EXECUTION_AUTHORITY",
                "ROUTE_ATTAINMENT != CAUSAL_TREATMENT_EFFECT",
            ],
        }

    @staticmethod
    def resource() -> dict:
        return {
            "version": WINDOW_VERSION,
            "artifact": WINDOW_ARTIFACT,
            "stages": list(STAGES),
            "seams": list(SEAMS),
            "conversion_edges": copy.deepcopy(CONVERSION_EDGES),
            "window_states": ["OPEN", "CLOSED"],
            "authority": "OBSERVATION_SCOPE_ONLY",
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "EVENT_COUNT != ROUTE_COUNT",
                "RETRY_COUNT != CONVERSION",
                "PENDING != FAILURE",
                "ZERO_MATURE_DENOMINATOR => UNKNOWN",
                "ABSENCE_OF_APPLY_EVENT != ZERO_APPLY_RATE_WITHOUT_COMPLETE_APPLY_WINDOW",
                "WINDOW_SCOPE != SOURCE_OR_EXECUTION_AUTHORITY",
            ],
        }
