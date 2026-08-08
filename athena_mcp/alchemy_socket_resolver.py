from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

ARTIFACT = "ATHENA.ALCHEMY.SOCKET.RECIPE.V1"
BASIS_ARTIFACT = "OPERATIONAL_BASIS_V1"

LAWS = [
    "SOCKET_RESOLUTION != TOOL_INVOCATION",
    "RECIPE != EXECUTION_AUTHORITY",
    "DESCRIPTOR != PERMISSION",
    "CURRENT_EXPOSURE != AUTO_SELECTION",
    "AUTO_SOCKET => READ_ONLY_AND_AUTO_SELECT",
    "GATED_PLAN != EXECUTION_READY",
    "OPERATIONAL_BASIS_HOLD => FORGE_HOLD",
    "BASIS_DIGEST_DRIFT => REHYDRATE",
    "TOOL_SCHEMA_DRIFT => RECOMPILE_SOCKET",
    "MISSING_OR_UNCLASSIFIED_SOCKET => HOLD",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _hold(code: str, detail: str, *, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "detail": detail}
    if request is not None:
        result["socket_id"] = str(request.get("socket_id") or request.get("operation") or "")
        result["operation"] = str(request.get("operation") or "")
    return result


def _normalize_requests(requests: Sequence[Mapping[str, Any] | str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    normalized: list[dict[str, Any]] = []
    holds: list[dict[str, Any]] = []
    seen: set[str] = set()

    for raw in requests:
        if isinstance(raw, str):
            request: dict[str, Any] = {"operation": raw, "mode": "AUTO"}
        elif isinstance(raw, Mapping):
            request = dict(raw)
            request.setdefault("mode", "AUTO")
        else:
            holds.append(_hold("INVALID_REQUEST", f"unsupported request type: {type(raw).__name__}"))
            continue

        operation = str(request.get("operation") or "").strip()
        request["operation"] = operation
        request["socket_id"] = str(request.get("socket_id") or operation)
        request["mode"] = str(request.get("mode") or "AUTO").upper()

        if not operation:
            holds.append(_hold("MISSING_OPERATION", "socket request has no operation", request=request))
            continue
        if operation in seen:
            holds.append(_hold("DUPLICATE_OPERATION", "same operation requested more than once", request=request))
            continue
        seen.add(operation)
        normalized.append(request)

    return normalized, holds


def compile_socket_recipe(
    requests: Sequence[Mapping[str, Any] | str],
    operational_basis: Mapping[str, Any],
    *,
    expected_basis_digest: str,
) -> dict[str, Any]:
    """Resolve candidate Crystal-Rod sockets against a frozen operational basis.

    The function is deliberately pure. It does not register, call, authorize, or
    execute operations. AUTO requests may seat only descriptors that the basis
    itself marks as current, READ_ONLY, and auto_select=true. PLAN requests may
    preserve a known write/gated descriptor as plan metadata, but never become
    execution-ready.
    """

    basis = dict(operational_basis)
    holds: list[dict[str, Any]] = []
    sockets: list[dict[str, Any]] = []

    if basis.get("artifact") != BASIS_ARTIFACT:
        holds.append(_hold("BASIS_ARTIFACT_MISMATCH", f"expected {BASIS_ARTIFACT}"))

    actual_digest = str(basis.get("basis_digest") or "")
    if not expected_basis_digest or actual_digest != expected_basis_digest:
        holds.append(
            _hold(
                "BASIS_DIGEST_DRIFT",
                f"expected={expected_basis_digest or '<missing>'};actual={actual_digest or '<missing>'}",
            )
        )

    if basis.get("status") != "OPERATIONAL_BASIS_READY":
        holds.append(_hold("OPERATIONAL_BASIS_HOLD", f"status={basis.get('status')}"))

    source_witness = basis.get("source_witness")
    if not isinstance(source_witness, Mapping) or source_witness.get("surface") != "PROTOCOL_TOOLS_CONTROL_FILTER":
        holds.append(_hold("BASIS_WITNESS_MISSING", "current registration-surface witness is absent or malformed"))

    normalized, request_holds = _normalize_requests(requests)
    holds.extend(request_holds)
    if not normalized:
        holds.append(_hold("EMPTY_SOCKET_SET", "at least one socket request is required"))

    descriptors = basis.get("descriptors")
    if not isinstance(descriptors, list):
        descriptors = []
        holds.append(_hold("DESCRIPTOR_SET_MISSING", "operational basis has no descriptor list"))

    by_operation = {
        str(row.get("operation")): row
        for row in descriptors
        if isinstance(row, Mapping) and str(row.get("operation") or "")
    }

    for request in normalized:
        operation = request["operation"]
        descriptor = by_operation.get(operation)
        if not isinstance(descriptor, Mapping):
            holds.append(_hold("SOCKET_NOT_EXPOSED", "operation not present in current basis", request=request))
            continue
        if descriptor.get("current_exposure") is not True:
            holds.append(_hold("SOCKET_NOT_CURRENT", "descriptor is not marked current_exposure=true", request=request))
            continue

        capability_class = str(descriptor.get("capability_class") or "")
        effect = str(descriptor.get("effect") or "")
        authority = str(descriptor.get("authority_class") or "")
        auto_select = descriptor.get("auto_select") is True
        descriptor_witness = descriptor.get("source_witness")
        tool_schema_digest = (
            str(descriptor_witness.get("tool_schema_digest") or "")
            if isinstance(descriptor_witness, Mapping)
            else ""
        )

        if capability_class == "UNCLASSIFIED" or effect in {"", "UNKNOWN"} or authority.endswith("HOLD"):
            holds.append(_hold("SOCKET_UNCLASSIFIED", "operation semantics are not safe to compose automatically", request=request))
            continue

        expected_effect = request.get("expected_effect")
        if expected_effect is not None and str(expected_effect) != effect:
            holds.append(
                _hold(
                    "SOCKET_EFFECT_DRIFT",
                    f"expected={expected_effect};actual={effect}",
                    request=request,
                )
            )
            continue

        expected_authority = request.get("expected_authority_class")
        if expected_authority is not None and str(expected_authority) != authority:
            holds.append(
                _hold(
                    "SOCKET_AUTHORITY_DRIFT",
                    f"expected={expected_authority};actual={authority}",
                    request=request,
                )
            )
            continue

        expected_schema_digest = request.get("expected_tool_schema_digest")
        if expected_schema_digest is not None and str(expected_schema_digest) != tool_schema_digest:
            holds.append(
                _hold(
                    "TOOL_SCHEMA_DRIFT",
                    f"expected={expected_schema_digest};actual={tool_schema_digest}",
                    request=request,
                )
            )
            continue

        mode = request["mode"]
        if mode == "AUTO":
            if effect != "READ_ONLY" or not auto_select:
                holds.append(
                    _hold(
                        "AUTHORITY_GATE_REQUIRED",
                        f"AUTO requires READ_ONLY+auto_select; effect={effect};auto_select={auto_select}",
                        request=request,
                    )
                )
                continue
            socket_state = "AUTO_READ_ONLY"
            execution_ready = True
        elif mode == "PLAN":
            socket_state = "AUTO_READ_ONLY" if effect == "READ_ONLY" and auto_select else "GATED_PLAN_ONLY"
            execution_ready = socket_state == "AUTO_READ_ONLY"
        else:
            holds.append(_hold("INVALID_SOCKET_MODE", f"mode={mode};allowed=AUTO|PLAN", request=request))
            continue

        sockets.append(
            {
                "socket_id": request["socket_id"],
                "operation": operation,
                "mode": mode,
                "socket_state": socket_state,
                "execution_ready": execution_ready,
                "current_exposure": True,
                "capability_class": capability_class,
                "component": descriptor.get("component"),
                "effect": effect,
                "authority_class": authority,
                "auto_select": auto_select,
                "freshness_dependencies": list(descriptor.get("freshness_dependencies") or []),
                "preconditions": list(descriptor.get("preconditions") or []),
                "replayability": bool(descriptor.get("replayability")),
                "rollback_or_compensation": descriptor.get("rollback_or_compensation"),
                "source_witness": dict(descriptor_witness) if isinstance(descriptor_witness, Mapping) else {},
            }
        )

    status = "RECIPE" if not holds and len(sockets) == len(normalized) and sockets else "HOLD"
    auto_executable = status == "RECIPE" and all(row["execution_ready"] for row in sockets)
    recipe_basis = {
        "artifact": ARTIFACT,
        "status": status,
        "basis_digest": actual_digest,
        "requested": normalized,
        "sockets": sockets,
        "holds": holds,
        "execution_authority": False,
        "invocation_performed": False,
        "auto_executable": auto_executable,
        "laws": LAWS,
    }

    return {
        **recipe_basis,
        "recipe_digest": _sha(recipe_basis),
        "next": (
            "EXECUTOR_MUST_RECHECK_BASIS_AND_OPERATION_PRECONDITIONS"
            if status == "RECIPE"
            else "REHYDRATE_OR_REVISE_SOCKET_REQUEST"
        ),
    }
