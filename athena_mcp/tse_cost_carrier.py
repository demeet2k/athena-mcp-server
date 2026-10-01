from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .rehydration_loop import REHYDRATION_TOOLS, RehydrationLoopRuntime
from .tse_circulation import CIRCULATION_ARTIFACT, TseCirculationRuntime, _parent_position
from .tse_helix_integrity import TseHelixIntegrityRuntime
from .tse_helix_protocol import TSE_HELIX_TOOLS
from .tse_reentry import TseReentryRuntime
from .tse_telemetry import TELEMETRY_ROOT, _digest

COST_CARRIER_VERSION = "TSE.COST.CARRIER.1"
COST_CARRIER_ARTIFACT = "ATHENA.TSE.COST.CARRIER.V1"
COST_CARRIER_ROOT = f"{TELEMETRY_ROOT}/circulation_cost"
REENTRY_COST_MARKER = "ATHENA_TSE_REENTRY_COST_V1="
COST_AUTHORITY = "DECLARED_STRUCTURAL_ACCOUNTING_ONLY"
HOST_RESOURCE_AUTHORITY = "UNOBSERVED"

COST_SCHEMA = {
    "type": "object",
    "required": ["known"],
    "properties": {"known": {"type": "boolean"}, "total": {}},
    "additionalProperties": False,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _normalize_cost(value: Any, *, field: str = "cost") -> dict:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field}_not_mapping")
    extra = sorted(set(value) - {"known", "total"})
    if extra:
        raise ValueError(f"{field}_unexpected_fields:{','.join(str(x) for x in extra)}")
    known = value.get("known")
    if not isinstance(known, bool):
        raise ValueError(f"{field}_known_boolean_required")
    if not known:
        if "total" in value and value.get("total") not in (None, "UNKNOWN"):
            raise ValueError(f"{field}_unknown_must_not_supply_numeric_total")
        return {"known": False}
    total = value.get("total")
    if (
        not isinstance(total, (int, float))
        or isinstance(total, bool)
        or not math.isfinite(float(total))
        or float(total) < 0
    ):
        raise ValueError(f"{field}_known_nonnegative_finite_total_required")
    return {"known": True, "total": float(total)}


def _marker(cost: Mapping[str, Any]) -> str:
    return REENTRY_COST_MARKER + _canonical(dict(cost))


def _marker_cost(stop_conditions: Any) -> tuple[dict | None, str | None]:
    markers = [
        str(value)
        for value in (stop_conditions or [])
        if isinstance(value, str) and value.startswith(REENTRY_COST_MARKER)
    ]
    if not markers:
        return None, "reentry_start_cost_missing"
    if len(markers) != 1:
        return None, "reentry_start_cost_marker_ambiguous"
    try:
        raw = json.loads(markers[0][len(REENTRY_COST_MARKER) :])
        return _normalize_cost(raw, field="reentry_start_cost"), None
    except (ValueError, json.JSONDecodeError) as exc:
        return None, f"reentry_start_cost_marker_invalid:{exc}"


def _cost_known(value: dict | None) -> bool:
    return bool(value and value.get("known") is True and isinstance(value.get("total"), (int, float)))


def _sidecar_path(cycle_id: str) -> str:
    return f"{COST_CARRIER_ROOT}/{cycle_id}.json"


def _read_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sidecars(runtime: TseCirculationRuntime) -> list[dict]:
    root = runtime.telemetry._root() / COST_CARRIER_ROOT
    if not root.is_dir():
        return []
    out = []
    for path in sorted(root.glob("*.json")):
        row = _read_json(path)
        if not row or row.get("artifact") != COST_CARRIER_ARTIFACT:
            continue
        basis = row.get("basis")
        if not isinstance(basis, Mapping) or row.get("cost_carrier_digest") != _digest(basis):
            out.append({
                "artifact": COST_CARRIER_ARTIFACT,
                "cycle_id": row.get("cycle_id") or path.stem,
                "status": "INTEGRITY_HOLD",
                "cost_complete": False,
                "integrity_error": "cost_carrier_digest_mismatch",
            })
            continue
        out.append(row)
    return out


def _loop_cost_basis(
    runtime: TseCirculationRuntime,
    *,
    circulation_receipt: Mapping[str, Any],
    next_hatch: Mapping[str, Any],
) -> dict:
    reentry = circulation_receipt.get("reentry") or {}
    loop_id = str(reentry.get("loop_id") or "")
    loop = runtime.reentry._loop_runtime()
    state, _ = loop._read_state(loop_id)

    reentry_cost, reentry_error = _marker_cost(state.get("stop_conditions"))
    unknown_components: list[str] = []
    if reentry_error:
        unknown_components.append(reentry_error)
    elif reentry_cost and not reentry_cost.get("known"):
        unknown_components.append("reentry_start_cost_unknown")

    next_position = _parent_position(next_hatch)
    next_parent_head = str((next_position or {}).get("head") or "")
    rehydration_rows = []
    known_rehydration_cost = 0.0
    for receipt_path in state.get("receipt_paths") or []:
        receipt_path = str(receipt_path)
        receipt_commit = loop._path_last_commit(receipt_path)
        if not receipt_commit:
            unknown_components.append(f"rehydration_receipt_commit_missing:{receipt_path}")
            continue
        try:
            if next_parent_head and not runtime._is_ancestor(receipt_commit, next_parent_head):
                continue
        except Exception:
            unknown_components.append(f"rehydration_receipt_ancestry_unknown:{receipt_path}")
            continue
        receipt = _read_json(runtime.telemetry._root() / receipt_path)
        if not receipt:
            unknown_components.append(f"rehydration_receipt_unreadable:{receipt_path}")
            continue
        completion = receipt.get("completion") or {}
        raw_cost = completion.get("cost") if isinstance(completion, Mapping) else None
        normalized = None
        error = None
        if raw_cost is None:
            error = "cost_missing"
        else:
            try:
                normalized = _normalize_cost(raw_cost, field="rehydration_cost")
            except ValueError as exc:
                error = str(exc)
        if error:
            unknown_components.append(f"rehydration_cost_missing_or_invalid:{receipt_path}:{error}")
        elif normalized and normalized.get("known"):
            known_rehydration_cost += float(normalized["total"])
        else:
            unknown_components.append(f"rehydration_cost_unknown:{receipt_path}")
        rehydration_rows.append({
            "receipt_path": receipt_path,
            "receipt_digest": receipt.get("receipt_digest"),
            "receipt_commit": receipt_commit,
            "step_index": receipt.get("step_index"),
            "cost": normalized if normalized is not None else {"known": False},
            "cost_error": error,
        })

    route_known = float(circulation_receipt.get("known_source_bound_tse_cost_total") or 0.0)
    route_unknown = list(circulation_receipt.get("unknown_source_bound_tse_cost_events") or [])
    for row in route_unknown:
        event_id = str((row or {}).get("event_id") or "UNKNOWN") if isinstance(row, Mapping) else "UNKNOWN"
        reason = str((row or {}).get("reason") or "unknown") if isinstance(row, Mapping) else str(row)
        unknown_components.append(f"source_bound_tse_cost_unknown:{event_id}:{reason}")

    known_reentry = float(reentry_cost["total"]) if _cost_known(reentry_cost) else 0.0
    known_total = known_reentry + known_rehydration_cost + route_known
    cost_complete = not unknown_components and bool(rehydration_rows) and _cost_known(reentry_cost)
    total_carried_cost: float | str = known_total if cost_complete else "UNKNOWN"
    delta = float(circulation_receipt.get("verified_incorporated_delta") or 0.0)
    ratio: float | str = delta / known_total if cost_complete and known_total > 0 else "UNKNOWN"

    return {
        "version": COST_CARRIER_VERSION,
        "cycle_id": circulation_receipt.get("cycle_id"),
        "mission_id": circulation_receipt.get("mission_id"),
        "circulation_semantic_digest": circulation_receipt.get("semantic_digest"),
        "reentry_id": reentry.get("reentry_id"),
        "rehydration_loop_id": loop_id,
        "reentry_start_cost": reentry_cost if reentry_cost is not None else {"known": False},
        "rehydration_cost_receipts": rehydration_rows,
        "known_reentry_control_cost_total": known_reentry,
        "known_rehydration_cost_total": known_rehydration_cost,
        "known_source_bound_tse_cost_total": route_known,
        "known_total_carried_cost": known_total,
        "unknown_cost_components": sorted(set(unknown_components)),
        "cost_complete": cost_complete,
        "total_carried_cost": total_carried_cost,
        "verified_incorporated_delta": delta,
        "incorporated_delta_per_total_cost": ratio,
        "cost_authority": COST_AUTHORITY,
        "host_resource_cost_complete": False,
        "incorporated_delta_per_host_resource_cost": "UNKNOWN",
        "host_resource_authority": HOST_RESOURCE_AUTHORITY,
    }


def _persist_cost_sidecar(
    runtime: TseCirculationRuntime,
    *,
    circulation_receipt: Mapping[str, Any],
    next_hatch: Mapping[str, Any],
    actor_id: str,
    remote: str,
) -> dict:
    try:
        basis = _loop_cost_basis(runtime, circulation_receipt=circulation_receipt, next_hatch=next_hatch)
    except Exception as exc:
        return {
            "status": "TSE_COST_CARRIER_HOLD",
            "hold": "EVIDENCE_HOLD",
            "reason": "cost_basis_unavailable",
            "detail": str(exc),
            "cost_complete": False,
            "host_resource_cost_complete": False,
        }
    cycle_id = str(basis.get("cycle_id") or "")
    path = _sidecar_path(cycle_id)
    digest = _digest(basis)

    def build(base_head: str):
        existing = runtime.telemetry._read_json(runtime.telemetry._root() / path)
        if existing:
            if (
                existing.get("artifact") == COST_CARRIER_ARTIFACT
                and existing.get("cost_carrier_digest") == digest
                and existing.get("basis") == basis
            ):
                return {
                    "return": {
                        "status": "TSE_COST_CARRIER_ALREADY_OBSERVED",
                        "cost_carrier": existing,
                        "cost_complete": bool(existing.get("cost_complete")),
                        "host_resource_cost_complete": False,
                    }
                }
            return {
                "return": {
                    "status": "TSE_COST_CARRIER_CONFLICT_HOLD",
                    "hold": "EVIDENCE_HOLD",
                    "cycle_id": cycle_id,
                    "existing_cost_carrier_digest": existing.get("cost_carrier_digest"),
                    "requested_cost_carrier_digest": digest,
                    "cost_complete": False,
                    "host_resource_cost_complete": False,
                }
            }
        from .message_board import _iso

        sidecar = {
            "artifact": COST_CARRIER_ARTIFACT,
            "version": COST_CARRIER_VERSION,
            "cycle_id": cycle_id,
            "mission_id": basis.get("mission_id"),
            "circulation_semantic_digest": basis.get("circulation_semantic_digest"),
            "basis": basis,
            "cost_carrier_digest": digest,
            "observed_at": _iso(),
            "git_parent": base_head,
            **{k: v for k, v in basis.items() if k not in {"version", "cycle_id", "mission_id", "circulation_semantic_digest"}},
            "authority": "MEASUREMENT_ONLY",
            "execution_authority": False,
            "causal_effect": "UNKNOWN",
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "SEQUENCE_RECEIPT != COST_RECEIPT",
                "UNKNOWN_COST != ZERO_COST",
                "COST_CARRIER != EXECUTION_AUTHORITY",
                "COST_COMPLETE != CAUSAL_EFFECT",
                "CARRIED_SCALAR_COST != HOST_RESOURCE_TRUTH",
                "TOTAL_CARRIED_COST != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE",
            ],
        }
        return {
            "files": {path: json.dumps(sidecar, indent=2, sort_keys=True, ensure_ascii=False) + "\n"},
            "message": f"observe TSE cost carrier {cycle_id}",
            "result": {
                "status": "TSE_COST_CARRIER_OBSERVED",
                "cost_carrier": sidecar,
                "cost_complete": bool(sidecar["cost_complete"]),
                "host_resource_cost_complete": False,
            },
        }

    return runtime.telemetry._mutate(actor_id=actor_id, remote=remote, build_files=build)


def install_tse_cost_carrier_extension(circulation_tools: list[dict] | None = None) -> None:
    if getattr(TseCirculationRuntime, "_athena_tse_cost_carrier_v1_registered", False):
        return

    # Document the already-supported additive rehydration completion field.
    for tool in REHYDRATION_TOOLS:
        if tool.get("name") != "athena_rehydration_advance":
            continue
        completion = (((tool.get("inputSchema") or {}).get("properties") or {}).get("completion") or {})
        completion.setdefault("properties", {}).setdefault(
            "cost",
            {
                **COST_SCHEMA,
                "description": (
                    "Optional structural scalar cost for this observed rehydration step. "
                    "Missing/known=false remains UNKNOWN; it is not host/provider resource truth."
                ),
            },
        )
        tool["description"] = str(tool.get("description") or "") + (
            " Optional completion.cost is persisted in the normal receipt for TSE structural accounting; "
            "carried scalar cost is not host/provider resource truth."
        )

    for tool in TSE_HELIX_TOOLS:
        if tool.get("name") == "athena_tse_helix_advance":
            tool["description"] = str(tool.get("description") or "") + (
                " For REENTRY_START, the existing required cost packet is carried into the ordinary rehydration start state."
            )

    for tool in circulation_tools or []:
        if tool.get("name") == "athena_tse_circulation_observe":
            tool["description"] = str(tool.get("description") or "") + (
                " Cost Carrier V1 additionally persists a separately digested post-closure sidecar over re-entry, "
                "rehydration, and SOURCE_BOUND TSE scalar costs without rewriting the sequence receipt."
            )
        if tool.get("name") == "athena_tse_circulation_report":
            tool["description"] = str(tool.get("description") or "") + (
                " When every closed cycle has a complete Cost Carrier V1 sidecar, total carried-cost efficiency is reported; "
                "host resource efficiency remains UNKNOWN."
            )

    original_render = RehydrationLoopRuntime._render_prompt
    original_loop_start = RehydrationLoopRuntime.start
    original_loop_advance = RehydrationLoopRuntime.advance
    original_reentry_start = TseReentryRuntime.start
    original_helix_advance = TseHelixIntegrityRuntime.advance
    original_circulation_observe = TseCirculationRuntime.observe
    original_circulation_report = TseCirculationRuntime.report
    original_circulation_resource = TseCirculationRuntime.resource

    def render_with_cost(self, state, context, previous_completion):
        text = original_render(self, state, context, previous_completion)
        if '"cost": {"known": false}' not in text:
            text = text.replace(
                '  "progress_delta": 1.0,\n',
                '  "progress_delta": 1.0,\n  "cost": {"known": false},\n',
                1,
            )
        if "- `UNKNOWN_COST != ZERO_COST`" not in text:
            text = text.replace(
                "- `REPEATED_NO_PROGRESS => HOLD`, not infinite self-prompt recursion.\n",
                "- `REPEATED_NO_PROGRESS => HOLD`, not infinite self-prompt recursion.\n"
                "- `UNKNOWN_COST != ZERO_COST`; completion.cost is structural accounting, not host resource truth.\n",
                1,
            )
        return text

    def loop_start_with_cost(self, *args, **kwargs):
        pending = getattr(self, "_tse_reentry_cost_carrier_v1_pending", None)
        if pending is not None:
            stops = list(kwargs.get("stop_conditions") or [])
            if any(isinstance(x, str) and x.startswith(REENTRY_COST_MARKER) for x in stops):
                raise ValueError("reserved TSE reentry cost marker collision")
            stops.append(_marker(pending))
            kwargs["stop_conditions"] = stops
        return original_loop_start(self, *args, **kwargs)

    def loop_advance_with_cost(self, *args, **kwargs):
        completion = kwargs.get("completion")
        if isinstance(completion, Mapping) and "cost" in completion:
            normalized = _normalize_cost(completion.get("cost"), field="rehydration_cost")
            copy_completion = dict(completion)
            copy_completion["cost"] = normalized
            kwargs["completion"] = copy_completion
        return original_loop_advance(self, *args, **kwargs)

    def reentry_start_with_cost(self, *args, **kwargs):
        raw_stops = kwargs.get("stop_conditions") or []
        if any(isinstance(x, str) and x.startswith(REENTRY_COST_MARKER) for x in raw_stops):
            return {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "reserved_reentry_cost_marker_injection",
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        pending = getattr(self, "_tse_cost_carrier_v1_pending_reentry", None)
        loop = self._loop_runtime()
        if pending is not None:
            loop._tse_reentry_cost_carrier_v1_pending = dict(pending)
        try:
            result = original_reentry_start(self, *args, **kwargs)
        finally:
            if hasattr(loop, "_tse_reentry_cost_carrier_v1_pending"):
                delattr(loop, "_tse_reentry_cost_carrier_v1_pending")
        if pending is not None and isinstance(result, dict):
            result = dict(result)
            if result.get("status") == "TSE_REENTRY_ALREADY_STARTED":
                loop_id = ((result.get("existing_loop") or {}).get("loop_id"))
                if loop_id:
                    try:
                        state, _ = loop._read_state(str(loop_id))
                        existing_cost, existing_error = _marker_cost(state.get("stop_conditions"))
                    except Exception as exc:
                        existing_cost, existing_error = None, str(exc)
                    if existing_error or existing_cost != pending:
                        return {
                            "status": "TSE_REENTRY_COST_CONFLICT_HOLD",
                            "hold": "EVIDENCE_HOLD",
                            "reason": "reentry_replay_cost_mismatch",
                            "existing_cost": existing_cost,
                            "requested_cost": pending,
                            "reentry_started": True,
                            "background_execution": False,
                            "execution_authority": False,
                        }
            result["reentry_cost_carrier"] = dict(pending)
            result["cost_authority"] = COST_AUTHORITY
            result["host_resource_cost_complete"] = False
        return result

    def helix_advance_with_cost(self, *args, **kwargs):
        operation = str(kwargs.get("operation") or "").upper()
        if operation != "REENTRY_START":
            return original_helix_advance(self, *args, **kwargs)
        try:
            normalized = _normalize_cost(kwargs.get("cost"), field="reentry_start_cost")
        except ValueError as exc:
            return {
                "status": "TSE_REENTRY_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "invalid_reentry_start_cost",
                "errors": [str(exc)],
                "reentry_started": False,
                "background_execution": False,
                "execution_authority": False,
            }
        self.reentry._tse_cost_carrier_v1_pending_reentry = normalized
        try:
            return original_helix_advance(self, *args, **kwargs)
        finally:
            if hasattr(self.reentry, "_tse_cost_carrier_v1_pending_reentry"):
                delattr(self.reentry, "_tse_cost_carrier_v1_pending_reentry")

    def circulation_observe_with_cost(self, *args, **kwargs):
        result = original_circulation_observe(self, *args, **kwargs)
        if not isinstance(result, dict) or result.get("status") not in {
            "TSE_CIRCULATION_OBSERVED",
            "TSE_CIRCULATION_ALREADY_OBSERVED",
        }:
            return result
        receipt = result.get("receipt") or {}
        next_hatch = kwargs.get("next_hatch")
        actor_id = str(kwargs.get("actor_id") or "agent")
        remote = str(kwargs.get("remote") or "origin")
        if not isinstance(next_hatch, Mapping) or receipt.get("artifact") != CIRCULATION_ARTIFACT:
            return {
                **result,
                "status": "TSE_COST_CARRIER_HOLD",
                "hold": "EVIDENCE_HOLD",
                "reason": "circulation_cost_source_missing",
            }
        cost_result = _persist_cost_sidecar(
            self,
            circulation_receipt=receipt,
            next_hatch=next_hatch,
            actor_id=actor_id,
            remote=remote,
        )
        if cost_result.get("status") in {"TSE_COST_CARRIER_CONFLICT_HOLD", "TSE_COST_CARRIER_HOLD"}:
            return {
                **result,
                "status": cost_result["status"],
                "cost_carrier": cost_result,
                "cost_complete": False,
                "host_resource_cost_complete": False,
            }
        sidecar = cost_result.get("cost_carrier") or {}
        return {
            **result,
            "cost_carrier_status": cost_result.get("status"),
            "cost_carrier": sidecar,
            "cost_complete": bool(sidecar.get("cost_complete")),
            "total_carried_cost": sidecar.get("total_carried_cost", "UNKNOWN"),
            "incorporated_delta_per_total_cost": sidecar.get("incorporated_delta_per_total_cost", "UNKNOWN"),
            "host_resource_cost_complete": False,
            "incorporated_delta_per_host_resource_cost": "UNKNOWN",
        }

    def circulation_report_with_cost(self, *args, **kwargs):
        result = original_circulation_report(self, *args, **kwargs)
        if not isinstance(result, dict) or result.get("status") != "TSE_CIRCULATION_REPORT":
            return result
        mission_id = kwargs.get("mission_id")
        cycle_ids = {str(value) for value in result.get("cycle_ids") or []}
        all_rows = _sidecars(self)
        rows = [
            row for row in all_rows
            if str(row.get("cycle_id")) in cycle_ids
            and (mission_id is None or row.get("mission_id") == mission_id)
        ]
        by_cycle = {str(row.get("cycle_id")): row for row in rows}
        missing = sorted(cycle_ids - set(by_cycle))
        integrity_holds = sorted(
            str(row.get("cycle_id")) for row in rows if row.get("status") == "INTEGRITY_HOLD"
        )
        cost_complete = bool(cycle_ids) and not missing and not integrity_holds and all(
            bool(by_cycle[cycle_id].get("cost_complete")) for cycle_id in cycle_ids
        )
        known_total = sum(
            float((by_cycle.get(cycle_id) or {}).get("known_total_carried_cost") or 0.0)
            for cycle_id in cycle_ids
        )
        total: float | str = known_total if cost_complete else "UNKNOWN"
        delta = float(result.get("verified_incorporated_delta_total") or 0.0)
        ratio: float | str = delta / known_total if cost_complete and known_total > 0 else "UNKNOWN"
        unknown = []
        for cycle_id in sorted(cycle_ids):
            row = by_cycle.get(cycle_id)
            if row is None:
                unknown.append(f"cost_sidecar_missing:{cycle_id}")
                continue
            for item in row.get("unknown_cost_components") or []:
                unknown.append(f"{cycle_id}:{item}")
        for cycle_id in integrity_holds:
            unknown.append(f"cost_sidecar_integrity_hold:{cycle_id}")
        return {
            **result,
            "cost_carrier_version": COST_CARRIER_VERSION,
            "cost_sidecars": len(rows),
            "missing_cost_sidecar_cycle_ids": missing,
            "cost_sidecar_integrity_holds": integrity_holds,
            "known_total_carried_cost": known_total,
            "total_carried_cost": total,
            "unknown_cost_components": sorted(set(unknown)),
            "cost_complete": cost_complete,
            "incorporated_delta_per_total_cost": ratio,
            "cost_authority": COST_AUTHORITY,
            "host_resource_cost_complete": False,
            "incorporated_delta_per_host_resource_cost": "UNKNOWN",
            "host_resource_authority": HOST_RESOURCE_AUTHORITY,
        }

    def circulation_resource_with_cost(self):
        result = original_circulation_resource(self)
        return {
            **result,
            "cost_carrier_version": COST_CARRIER_VERSION,
            "cost_carrier_artifact": COST_CARRIER_ARTIFACT,
            "cost_sidecars": len(_sidecars(self)),
            "cost_authority": COST_AUTHORITY,
            "host_resource_cost_complete": False,
            "incorporated_delta_per_host_resource_cost": "UNKNOWN",
            "cost_laws": [
                "SEQUENCE_RECEIPT != COST_RECEIPT",
                "UNKNOWN_COST != ZERO_COST",
                "CARRIED_SCALAR_COST != HOST_RESOURCE_TRUTH",
                "COST_COMPLETE != CAUSAL_EFFECT",
            ],
        }

    RehydrationLoopRuntime._render_prompt = render_with_cost
    RehydrationLoopRuntime.start = loop_start_with_cost
    RehydrationLoopRuntime.advance = loop_advance_with_cost
    TseReentryRuntime.start = reentry_start_with_cost
    TseHelixIntegrityRuntime.advance = helix_advance_with_cost
    TseCirculationRuntime.observe = circulation_observe_with_cost
    TseCirculationRuntime.report = circulation_report_with_cost
    TseCirculationRuntime.resource = circulation_resource_with_cost
    TseCirculationRuntime._athena_tse_cost_carrier_v1_registered = True
