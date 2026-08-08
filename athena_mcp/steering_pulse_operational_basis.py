from __future__ import annotations

from typing import Any, Iterable, Mapping

from .steering_pulse import ARTIFACT, compile_pulse

BASIS_ARTIFACT = "OPERATIONAL_BASIS_V1"
BASIS_READY = "OPERATIONAL_BASIS_READY"

INTEGRATION_LAWS = [
    "OPERATIONAL_BASIS_DIGEST_MATCH_REQUIRED",
    "CURRENT_EXPOSURE_DESCRIPTOR_REQUIRED",
    "FEATURE_BRANCH != CURRENT_RUNTIME_EXPOSURE",
    "DESCRIPTOR != EXECUTION_AUTHORITY",
    "UNREADY_OPERATIONAL_BASIS => HOLD",
]


def _project_current_operations(
    current_address: Mapping[str, Any],
    operational_basis: Mapping[str, Any] | None,
) -> tuple[list[str], dict[str, Any], list[str]]:
    basis = dict(operational_basis or {})
    failures: list[str] = []

    if basis.get("artifact") != BASIS_ARTIFACT:
        failures.append("OPERATIONAL_BASIS_ARTIFACT_MISMATCH")
    if basis.get("status") != BASIS_READY:
        failures.append("OPERATIONAL_BASIS_NOT_READY")

    basis_digest = str(basis.get("basis_digest") or "")
    address_digest = str(current_address.get("operational_basis_digest") or "")
    if not basis_digest:
        failures.append("MISSING_OPERATIONAL_BASIS_DIGEST")
    if not address_digest:
        failures.append("MISSING_CURRENT_OPERATIONAL_BASIS_DIGEST")
    if basis_digest and address_digest and basis_digest != address_digest:
        failures.append(
            f"STALE_OPERATIONAL_BASIS_DIGEST:{address_digest}!={basis_digest}"
        )

    descriptors = basis.get("descriptors")
    if not isinstance(descriptors, list):
        failures.append("OPERATIONAL_BASIS_DESCRIPTORS_REQUIRED")
        descriptors = []

    operations: set[str] = set()
    for row in descriptors:
        if not isinstance(row, Mapping):
            failures.append("INVALID_OPERATIONAL_BASIS_DESCRIPTOR")
            continue
        operation = str(row.get("operation") or "").strip()
        if row.get("current_exposure") is True and operation:
            operations.add(operation)

    metadata = {
        "artifact": basis.get("artifact"),
        "status": basis.get("status"),
        "basis_digest": basis_digest or None,
        "address_basis_digest": address_digest or None,
        "source_witness": basis.get("source_witness"),
        "projected_current_operations": sorted(operations),
        "standing": "CURRENT_REGISTERED_SURFACE_PROJECTION_NOT_EXECUTION_AUTHORITY",
    }
    return sorted(operations), metadata, failures


def compile_pulse_with_operational_basis(
    pulse: Mapping[str, Any],
    assessments: Iterable[Mapping[str, Any]],
    *,
    expected_source_body_digest: str,
    current_address: Mapping[str, Any],
    operational_basis: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind Campaign V3 pulse compilation to the canonical current runtime basis.

    The operational-basis packet is an exposure witness, not permission.  Its
    digest must match the current bootstrap/address coordinate before any
    historical RESIDUAL can become a routing candidate.
    """

    exposed, basis_meta, basis_failures = _project_current_operations(
        current_address, operational_basis
    )
    if basis_failures:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_INVALID_COMPILATION_INPUT",
            "pulse_index": int(pulse.get("pulse_index") or 0),
            "step_start": int(pulse.get("step_start") or 0),
            "step_end": int(pulse.get("step_end") or 0),
            "source_comment_id": pulse.get("source_comment_id"),
            "source_body_digest": pulse.get("source_body_digest"),
            "current_address": dict(current_address),
            "operational_basis": basis_meta,
            "exposed_operations": exposed,
            "failures": basis_failures,
            "holds": [],
            "coverage": None,
            "actions": [],
            "candidates": [],
            "can_advance_pulse": False,
            "next": "REHYDRATE_OPERATIONAL_BASIS",
            "compilation_digest": None,
            "laws": list(INTEGRATION_LAWS),
        }

    result = compile_pulse(
        pulse,
        assessments,
        expected_source_body_digest=expected_source_body_digest,
        current_address=current_address,
        execution_surface={"exposed_operations": exposed},
    )
    result["operational_basis"] = basis_meta
    result["laws"] = list(result.get("laws") or []) + [
        law for law in INTEGRATION_LAWS if law not in (result.get("laws") or [])
    ]
    return result
