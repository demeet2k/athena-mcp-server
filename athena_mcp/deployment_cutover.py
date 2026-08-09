from __future__ import annotations

"""Pure CUTOVER_HOLD contracts layered on ATHENA.DEPLOYMENT.2.

The functions in this module bind an activation plan, a checksum-valid isolated
canary witness, a supplied single-writer quiescence observation, and an explicit
authority reference into a replayable hold packet.  They never contact a
registry, cluster, traffic plane, secret store, or state volume, and they never
turn a reference into verified execution authority.
"""

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from .deployment import (
    ACTIVATION_PLAN_VERSION,
    CANARY_ASSESSMENT_VERSION,
    validate_image_ref,
)

CUTOVER_HOLD_VERSION = "ATHENA.CUTOVER.HOLD.1"
CUTOVER_HOLD_VALIDATION_VERSION = "ATHENA.CUTOVER.HOLD.VALIDATION.1"
QUIESCENCE_OBSERVATION_VERSION = "ATHENA.SINGLE.WRITER.QUIESCENCE.OBSERVATION.1"
QUIESCENCE_ASSESSMENT_VERSION = "ATHENA.SINGLE.WRITER.QUIESCENCE.ASSESSMENT.1"
CANARY_WITNESS_VERSION = "ATHENA.ISOLATED.CANARY.WITNESS.1"
CANARY_OBSERVER_VERSION = "ATHENA.ISOLATED.CANARY.OBSERVER.1"
CANARY_COMPARISON_KIND = "REPLICATED_SAME_DIGEST_STATE_RESTART"

_SHA256 = re.compile(r"^(?:sha256:)?(?P<digest>[0-9a-f]{64})$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")

_REQUIRED_CANARY_GATES = {
    "readiness",
    "schema",
    "replay",
    "error_rate",
    "latency",
    "restarts",
    "sample_count",
    "observation_window",
}
_REQUIRED_STRUCTURAL_MATCHES = {
    "tool_inventory",
    "resource_inventory",
    "deployment_manifest",
    "state_restart_replay",
}
_FALSE_CANARY_AUTHORITY = {
    "cluster_apply_authorized": False,
    "cutover_authorized": False,
    "production_secret_provisioned": False,
    "production_state_contacted": False,
    "traffic_activation_authorized": False,
}
_FALSE_PACKET_AUTHORITY = {
    "cluster_apply_authorized": False,
    "cutover_authorized": False,
    "production_secret_provisioned": False,
    "production_state_contacted": False,
    "state_mutation_authorized": False,
    "traffic_activation_authorized": False,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _sha256(value: Any) -> str | None:
    match = _SHA256.fullmatch(_text(value).lower())
    return "sha256:" + match.group("digest") if match else None


def _git_sha(value: Any) -> str | None:
    text = _text(value).lower()
    return text if _GIT_SHA.fullmatch(text) else None


def _image_ref(value: Any) -> str | None:
    try:
        return validate_image_ref(_text(value), require_digest=True)["image_ref"]
    except (TypeError, ValueError, KeyError):
        return None


def _embedded_digest(data: Mapping[str, Any], field: str) -> tuple[str | None, str, bool]:
    value = dict(data)
    supplied = _sha256(value.pop(field, None))
    computed = _digest(value)
    return supplied, computed, supplied == computed


def _validation_result(
    *,
    version: str,
    checks: Mapping[str, bool],
    details: Mapping[str, Any],
    boundary: str,
) -> dict[str, Any]:
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "version": version,
        "status": "PASS" if not failed else "FAIL",
        "valid": not failed,
        "checks": {name: "PASS" if passed else "FAIL" for name, passed in checks.items()},
        "failed_checks": failed,
        **dict(details),
        "boundary": boundary,
    }
    result["validation_digest"] = _digest(result)
    return result


def validate_activation_plan_for_hold(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Replay the plan's intrinsic bindings before accepting it at CUTOVER_HOLD."""

    data = _mapping(plan)
    image = _mapping(data.get("image"))
    current = _mapping(data.get("expected_current_image"))
    cas = _mapping(data.get("compare_and_swap"))
    stages = data.get("stages") if isinstance(data.get("stages"), list) else []

    target_image = _image_ref(image.get("image_ref"))
    current_image = _image_ref(current.get("image_ref"))
    source_head = _git_sha(data.get("source_head"))
    snapshot_ref = _text(data.get("state_snapshot_ref")) or None
    snapshot_digest = _sha256(data.get("state_snapshot_digest"))
    plan_digest, computed_plan_digest, digest_match = _embedded_digest(data, "plan_digest")

    checks = {
        "version": data.get("version") == ACTIVATION_PLAN_VERSION,
        "status": data.get("status") == "PLAN_ONLY",
        "plan_digest": digest_match,
        "target_image_ref": target_image is not None,
        "source_head": source_head is not None,
        "expected_current_image_ref": current_image is not None,
        "state_snapshot_ref": snapshot_ref is not None,
        "state_snapshot_digest": snapshot_digest is not None,
        "token_secret_ref": bool(_text(data.get("token_secret_ref"))),
        "release_attestation_ref": bool(_text(data.get("release_attestation_ref"))),
        "sbom_ref": bool(_text(data.get("sbom_ref"))),
        "single_writer": isinstance(data.get("replicas"), int)
        and not isinstance(data.get("replicas"), bool)
        and data.get("replicas") == 1,
        "cas_current_image": current_image is not None
        and cas.get("expected_current_image_ref") == current_image,
        "cas_snapshot_ref": snapshot_ref is not None
        and cas.get("expected_state_snapshot_ref") == snapshot_ref,
        "cas_snapshot_digest": snapshot_digest is not None
        and _sha256(cas.get("expected_state_snapshot_digest")) == snapshot_digest,
        "cutover_hold_stage": any(
            isinstance(stage, Mapping) and stage.get("name") == "CUTOVER_HOLD"
            for stage in stages
        ),
    }
    return _validation_result(
        version=CUTOVER_HOLD_VALIDATION_VERSION,
        checks=checks,
        details={
            "plan_digest": plan_digest,
            "computed_plan_digest": computed_plan_digest,
            "target_image_ref": target_image,
            "source_head": source_head,
            "expected_current_image_ref": current_image,
            "state_snapshot_ref": snapshot_ref,
            "state_snapshot_digest": snapshot_digest,
        },
        boundary=(
            "PASS replays supplied plan bytes and internal CAS coordinates only. It does not prove that "
            "the current production image or state snapshot was independently observed."
        ),
    )


def validate_canary_witness(
    witness: Mapping[str, Any],
    *,
    expected_image_ref: str,
    expected_source_head: str,
) -> dict[str, Any]:
    """Verify a same-digest canary witness before it can feed CUTOVER_HOLD."""

    expected_image = _image_ref(expected_image_ref)
    expected_source = _git_sha(expected_source_head)
    if expected_image is None:
        raise ValueError("expected_image_ref must be digest pinned")
    if expected_source is None:
        raise ValueError("expected_source_head must be a full 40-character Git SHA")

    data = _mapping(witness)
    assessment = _mapping(data.get("assessment"))
    gates = _mapping(assessment.get("gates"))
    structural = _mapping(data.get("structural_match"))
    state = _mapping(data.get("state_witness"))
    authority = _mapping(data.get("authority"))
    observations = _mapping(assessment.get("observations"))

    witness_digest, computed_witness_digest, witness_digest_match = _embedded_digest(
        data, "witness_digest"
    )
    assessment_digest, computed_assessment_digest, assessment_digest_match = _embedded_digest(
        assessment, "assessment_digest"
    )
    sample_count = observations.get("sample_count")
    window = observations.get("observation_window_seconds")

    checks = {
        "schema": data.get("schema") == CANARY_WITNESS_VERSION,
        "observer": data.get("observer") == CANARY_OBSERVER_VERSION,
        "comparison_kind": data.get("comparison_kind") == CANARY_COMPARISON_KIND,
        "witness_digest": witness_digest_match,
        "image_ref": _image_ref(data.get("image_ref")) == expected_image,
        "source_head": _git_sha(data.get("source_head")) == expected_source,
        "release_coordinates": all(
            bool(_text(data.get(field)))
            for field in (
                "release_tag",
                "release_run_id",
                "oci_run_id",
                "workflow_run_id",
                "observed_at",
            )
        )
        and _git_sha(data.get("workflow_head")) is not None,
        "assessment_version": assessment.get("version") == CANARY_ASSESSMENT_VERSION,
        "assessment_digest": assessment_digest_match,
        "assessment_promote": assessment.get("decision") == "PROMOTE"
        and assessment.get("status") == "PASS"
        and assessment.get("failed_gates") == [],
        "assessment_gates": _REQUIRED_CANARY_GATES <= gates.keys()
        and all(gates.get(name) == "PASS" for name in _REQUIRED_CANARY_GATES)
        and all(value == "PASS" for value in gates.values()),
        "sample_count": isinstance(sample_count, int)
        and not isinstance(sample_count, bool)
        and sample_count >= 30,
        "observation_window": isinstance(window, int)
        and not isinstance(window, bool)
        and window >= 60,
        "structural_match": _REQUIRED_STRUCTURAL_MATCHES <= structural.keys()
        and all(structural.get(name) is True for name in _REQUIRED_STRUCTURAL_MATCHES)
        and not any(value is False for value in structural.values()),
        "state_restart_replay": state.get("registered") is True
        and state.get("matched") is True
        and bool(_text(state.get("oid"))),
        "authority_false": authority == _FALSE_CANARY_AUTHORITY,
    }
    return _validation_result(
        version=CUTOVER_HOLD_VALIDATION_VERSION,
        checks=checks,
        details={
            "witness_digest": witness_digest,
            "computed_witness_digest": computed_witness_digest,
            "assessment_digest": assessment_digest,
            "computed_assessment_digest": computed_assessment_digest,
            "workflow_run_id": _text(data.get("workflow_run_id")) or None,
            "workflow_head": _git_sha(data.get("workflow_head")),
            "state_oid": _text(state.get("oid")) or None,
        },
        boundary=(
            "PASS verifies checksum-bound same-digest canary evidence and its declared false authority bits. "
            "It does not establish production health, authorize cutover, or observe a production state volume."
        ),
    )


def assess_single_writer_quiescence(
    observation: Mapping[str, Any],
    *,
    expected_current_image_ref: str,
    expected_state_snapshot_ref: str,
    expected_state_snapshot_digest: str,
) -> dict[str, Any]:
    """Evaluate supplied quiescence evidence without contacting the production writer."""

    expected_image = _image_ref(expected_current_image_ref)
    expected_snapshot_ref = _text(expected_state_snapshot_ref)
    expected_snapshot_digest = _sha256(expected_state_snapshot_digest)
    if expected_image is None:
        raise ValueError("expected_current_image_ref must be digest pinned")
    if not expected_snapshot_ref:
        raise ValueError("expected_state_snapshot_ref is required")
    if expected_snapshot_digest is None:
        raise ValueError("expected_state_snapshot_digest must be a SHA-256 digest")

    data = _mapping(observation)
    observed_image_raw = _text(data.get("observed_current_image_ref"))
    observed_image = _image_ref(observed_image_raw)
    active_writers = data.get("active_writer_count")
    observed_snapshot_ref = _text(data.get("state_snapshot_ref"))
    observed_snapshot_digest = _sha256(data.get("state_snapshot_digest"))

    checks = {
        "schema": data.get("schema") == QUIESCENCE_OBSERVATION_VERSION,
        "current_image_ref_present": bool(observed_image_raw),
        "current_image_ref_valid": observed_image is not None,
        "current_image_match": observed_image == expected_image,
        "active_writer_count": isinstance(active_writers, int)
        and not isinstance(active_writers, bool)
        and active_writers == 0,
        "previous_writer_stopped": data.get("previous_writer_stopped") is True,
        "candidate_writer_not_started": data.get("candidate_writer_started") is False,
        "write_fence_active": data.get("write_fence_active") is True,
        "write_fence_ref": bool(_text(data.get("write_fence_ref"))),
        "snapshot_after_write_fence": data.get("snapshot_after_write_fence") is True,
        "state_snapshot_verified": data.get("state_snapshot_verified") is True,
        "state_snapshot_ref": observed_snapshot_ref == expected_snapshot_ref,
        "state_snapshot_digest": observed_snapshot_digest == expected_snapshot_digest,
        "observer_ref": bool(_text(data.get("observer_ref"))),
        "observed_at": bool(_text(data.get("observed_at"))),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "version": QUIESCENCE_ASSESSMENT_VERSION,
        "decision": "QUIESCENT" if not failed else "HOLD",
        "status": "PASS" if not failed else "FAIL",
        "checks": {name: "PASS" if passed else "FAIL" for name, passed in checks.items()},
        "failed_checks": failed,
        "expected": {
            "current_image_ref": expected_image,
            "state_snapshot_ref": expected_snapshot_ref,
            "state_snapshot_digest": expected_snapshot_digest,
        },
        "observed": {
            "current_image_ref": observed_image,
            "current_image_ref_raw": observed_image_raw or None,
            "active_writer_count": active_writers,
            "previous_writer_stopped": data.get("previous_writer_stopped"),
            "candidate_writer_started": data.get("candidate_writer_started"),
            "write_fence_active": data.get("write_fence_active"),
            "write_fence_ref": _text(data.get("write_fence_ref")) or None,
            "state_snapshot_ref": observed_snapshot_ref or None,
            "state_snapshot_digest": observed_snapshot_digest,
            "observer_ref": _text(data.get("observer_ref")) or None,
            "observed_at": _text(data.get("observed_at")) or None,
        },
        "observation_digest": _digest(data),
        "boundary": (
            "QUIESCENT means only that the supplied observation satisfies this single-writer contract. "
            "This function did not stop a writer, install a fence, verify a snapshot, or query production."
        ),
    }
    result["assessment_digest"] = _digest(result)
    return result


def _not_evaluated(kind: str, reason: str) -> dict[str, Any]:
    result = {
        "version": CUTOVER_HOLD_VALIDATION_VERSION,
        "status": "NOT_EVALUATED",
        "valid": False,
        "checks": {},
        "failed_checks": [reason],
        "kind": kind,
        "boundary": "Evaluation was skipped because an upstream binding was invalid.",
    }
    result["validation_digest"] = _digest(result)
    return result


def compile_cutover_hold(
    plan: Mapping[str, Any],
    canary_witness: Mapping[str, Any],
    quiescence_observation: Mapping[str, Any],
    *,
    cutover_authority_ref: str | None = None,
) -> dict[str, Any]:
    """Compile a replayable non-effectful CUTOVER_HOLD packet."""

    plan_validation = validate_activation_plan_for_hold(plan)
    authority_ref = _text(cutover_authority_ref) or None

    if plan_validation["valid"]:
        canary_validation = validate_canary_witness(
            canary_witness,
            expected_image_ref=plan_validation["target_image_ref"],
            expected_source_head=plan_validation["source_head"],
        )
        quiescence = assess_single_writer_quiescence(
            quiescence_observation,
            expected_current_image_ref=plan_validation["expected_current_image_ref"],
            expected_state_snapshot_ref=plan_validation["state_snapshot_ref"],
            expected_state_snapshot_digest=plan_validation["state_snapshot_digest"],
        )
    else:
        canary_validation = _not_evaluated("CANARY", "INVALID_ACTIVATION_PLAN")
        quiescence = _not_evaluated("QUIESCENCE", "INVALID_ACTIVATION_PLAN")

    hold_reasons: list[str] = []
    if not plan_validation["valid"]:
        hold_reasons.append("HOLD_ACTIVATION_PLAN_INVALID")
    else:
        if not canary_validation["valid"]:
            hold_reasons.append("HOLD_CANARY_WITNESS_INVALID")

        q_checks = quiescence.get("checks") or {}
        q_failed = set(quiescence.get("failed_checks") or [])
        if q_checks.get("current_image_ref_present") == "FAIL":
            hold_reasons.append("HOLD_MISSING_CURRENT_IMAGE_OBSERVATION")
        elif q_checks.get("current_image_ref_valid") == "FAIL":
            hold_reasons.append("HOLD_INVALID_CURRENT_IMAGE_OBSERVATION")
        elif q_checks.get("current_image_match") == "FAIL":
            hold_reasons.append("HOLD_STALE_ACTIVATION_BASE")

        non_current_failures = q_failed - {
            "current_image_ref_present",
            "current_image_ref_valid",
            "current_image_match",
        }
        if non_current_failures:
            hold_reasons.append("HOLD_SINGLE_WRITER_NOT_QUIESCENT")

    if authority_ref is None:
        hold_reasons.append("HOLD_MISSING_CUTOVER_AUTHORITY_REFERENCE")

    hold_reasons = list(dict.fromkeys(hold_reasons))
    binding_complete = not hold_reasons
    observed = _mapping(quiescence.get("observed"))
    q_checks = _mapping(quiescence.get("checks"))
    cas = {
        "current_image_match": q_checks.get("current_image_match") == "PASS",
        "state_snapshot_ref_match": q_checks.get("state_snapshot_ref") == "PASS",
        "state_snapshot_digest_match": q_checks.get("state_snapshot_digest") == "PASS",
        "failure": "HOLD_STALE_ACTIVATION_BASE",
    }

    packet: dict[str, Any] = {
        "version": CUTOVER_HOLD_VERSION,
        "status": "CUTOVER_HOLD" if binding_complete else "HOLD",
        "decision": "BOUND_AT_CUTOVER_HOLD" if binding_complete else hold_reasons[0],
        "binding_complete": binding_complete,
        "hold_reasons": hold_reasons,
        "plan": {
            "plan_digest": plan_validation.get("plan_digest"),
            "validation_digest": plan_validation.get("validation_digest"),
        },
        "target": {
            "image_ref": plan_validation.get("target_image_ref"),
            "source_head": plan_validation.get("source_head"),
        },
        "activation_base": {
            "expected_current_image_ref": plan_validation.get("expected_current_image_ref"),
            "observed_current_image_ref": observed.get("current_image_ref"),
            "state_snapshot_ref": plan_validation.get("state_snapshot_ref"),
            "state_snapshot_digest": plan_validation.get("state_snapshot_digest"),
        },
        "evidence": {
            "canary_witness_digest": canary_validation.get("witness_digest"),
            "canary_assessment_digest": canary_validation.get("assessment_digest"),
            "canary_validation_digest": canary_validation.get("validation_digest"),
            "canary_workflow_run_id": canary_validation.get("workflow_run_id"),
            "quiescence_observation_digest": quiescence.get("observation_digest"),
            "quiescence_assessment_digest": quiescence.get("assessment_digest"),
            "quiescence_observer_ref": observed.get("observer_ref"),
            "quiescence_observed_at": observed.get("observed_at"),
        },
        "cas": cas,
        "cutover_authority": {
            "ref": authority_ref,
            "reference_bound": authority_ref is not None,
            "independently_verified": False,
            "authorizes_this_packet": False,
        },
        "execution_authority": dict(_FALSE_PACKET_AUTHORITY),
        "next_transition": {
            "name": "SINGLE_WRITER_CUTOVER",
            "allowed_by_this_packet": False,
            "requires": [
                "independent verification of cutover authority",
                "fresh CAS re-observation of current image and snapshot",
                "fresh single-writer quiescence observation",
                "separately authorized effectful executor",
            ],
        },
        "rollback": _mapping(plan).get("rollback"),
        "validations": {
            "plan": plan_validation,
            "canary": canary_validation,
            "quiescence": quiescence,
        },
        "boundary": (
            "CUTOVER_HOLD is a checksum-bound coordination packet, not an activation receipt or execution grant. "
            "No image was started, no writer was stopped, no secret was resolved, no state was mounted, and no "
            "traffic was moved. A bound authority reference remains unverified data until a separate authorized "
            "executor independently replays every precondition."
        ),
    }
    packet["packet_digest"] = _digest(packet)
    return packet


def verify_cutover_hold(
    packet: Mapping[str, Any],
    *,
    expected_plan_digest: str,
    expected_image_ref: str,
    expected_source_head: str,
    expected_current_image_ref: str,
    expected_state_snapshot_ref: str,
    expected_state_snapshot_digest: str,
    expected_canary_witness_digest: str,
    expected_quiescence_assessment_digest: str,
    expected_cutover_authority_ref: str,
) -> dict[str, Any]:
    """Replay a complete hold packet without treating it as execution evidence."""

    expected = {
        "plan_digest": _sha256(expected_plan_digest),
        "image_ref": _image_ref(expected_image_ref),
        "source_head": _git_sha(expected_source_head),
        "current_image_ref": _image_ref(expected_current_image_ref),
        "state_snapshot_ref": _text(expected_state_snapshot_ref) or None,
        "state_snapshot_digest": _sha256(expected_state_snapshot_digest),
        "canary_witness_digest": _sha256(expected_canary_witness_digest),
        "quiescence_assessment_digest": _sha256(expected_quiescence_assessment_digest),
        "cutover_authority_ref": _text(expected_cutover_authority_ref) or None,
    }
    invalid_expected = [name for name, value in expected.items() if value is None]
    if invalid_expected:
        raise ValueError("invalid expected binding(s): " + ", ".join(sorted(invalid_expected)))

    data = _mapping(packet)
    plan = _mapping(data.get("plan"))
    target = _mapping(data.get("target"))
    base = _mapping(data.get("activation_base"))
    evidence = _mapping(data.get("evidence"))
    authority = _mapping(data.get("cutover_authority"))
    execution = _mapping(data.get("execution_authority"))
    cas = _mapping(data.get("cas"))
    transition = _mapping(data.get("next_transition"))
    packet_digest, computed_packet_digest, digest_match = _embedded_digest(data, "packet_digest")

    checks = {
        "version": data.get("version") == CUTOVER_HOLD_VERSION,
        "status": data.get("status") == "CUTOVER_HOLD",
        "decision": data.get("decision") == "BOUND_AT_CUTOVER_HOLD",
        "binding_complete": data.get("binding_complete") is True,
        "hold_reasons": data.get("hold_reasons") == [],
        "packet_digest": digest_match,
        "plan_digest": _sha256(plan.get("plan_digest")) == expected["plan_digest"],
        "image_ref": _image_ref(target.get("image_ref")) == expected["image_ref"],
        "source_head": _git_sha(target.get("source_head")) == expected["source_head"],
        "expected_current_image_ref": _image_ref(base.get("expected_current_image_ref"))
        == expected["current_image_ref"],
        "observed_current_image_ref": _image_ref(base.get("observed_current_image_ref"))
        == expected["current_image_ref"],
        "state_snapshot_ref": base.get("state_snapshot_ref") == expected["state_snapshot_ref"],
        "state_snapshot_digest": _sha256(base.get("state_snapshot_digest"))
        == expected["state_snapshot_digest"],
        "canary_witness_digest": _sha256(evidence.get("canary_witness_digest"))
        == expected["canary_witness_digest"],
        "quiescence_assessment_digest": _sha256(
            evidence.get("quiescence_assessment_digest")
        )
        == expected["quiescence_assessment_digest"],
        "cutover_authority_ref": authority.get("ref") == expected["cutover_authority_ref"],
        "authority_reference_only": authority.get("reference_bound") is True
        and authority.get("independently_verified") is False
        and authority.get("authorizes_this_packet") is False,
        "execution_authority_false": execution == _FALSE_PACKET_AUTHORITY,
        "cas": cas.get("current_image_match") is True
        and cas.get("state_snapshot_ref_match") is True
        and cas.get("state_snapshot_digest_match") is True,
        "transition_stopped": transition.get("name") == "SINGLE_WRITER_CUTOVER"
        and transition.get("allowed_by_this_packet") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "version": CUTOVER_HOLD_VALIDATION_VERSION,
        "status": "PASS" if not failed else "FAIL",
        "verified": not failed,
        "checks": {name: "PASS" if passed else "FAIL" for name, passed in checks.items()},
        "failed_checks": failed,
        "packet_digest": packet_digest,
        "computed_packet_digest": computed_packet_digest,
        "boundary": (
            "PASS verifies supplied CUTOVER_HOLD bytes and expected bindings only. It is not proof of current "
            "cluster state, authority validity, quiescence persistence, cutover execution, or traffic activation."
        ),
    }
    result["verification_digest"] = _digest(result)
    return result


def manifest() -> dict[str, Any]:
    value: dict[str, Any] = {
        "version": CUTOVER_HOLD_VERSION,
        "state": "NON_EFFECTFUL_CUTOVER_BINDING_GATE",
        "inputs": [
            ACTIVATION_PLAN_VERSION,
            CANARY_WITNESS_VERSION,
            QUIESCENCE_OBSERVATION_VERSION,
            "explicit cutover_authority_ref",
        ],
        "quiescence": {
            "active_writer_count": 0,
            "previous_writer_stopped": True,
            "candidate_writer_started": False,
            "write_fence_active": True,
            "snapshot_after_write_fence": True,
            "state_snapshot_verified": True,
        },
        "outcomes": {
            "complete": "CUTOVER_HOLD",
            "stale_base": "HOLD_STALE_ACTIVATION_BASE",
            "missing_authority": "HOLD_MISSING_CUTOVER_AUTHORITY_REFERENCE",
            "invalid_canary": "HOLD_CANARY_WITNESS_INVALID",
            "not_quiescent": "HOLD_SINGLE_WRITER_NOT_QUIESCENT",
        },
        "authority": dict(_FALSE_PACKET_AUTHORITY),
        "laws": [
            "CANARY_PROMOTE != CUTOVER_AUTHORITY",
            "AUTHORITY_REFERENCE_BOUND != AUTHORITY_VERIFIED",
            "QUIESCENCE_ASSESSMENT_PASS != WRITER_STOPPED_BY_THIS TOOL",
            "CUTOVER_HOLD != SINGLE_WRITER_CUTOVER",
            "PACKET_VERIFIED != ACTIVATION_RECEIPT",
            "ARTIFACT_CREATED != TRAFFIC_ACTIVATED",
        ],
        "boundary": (
            "This organ compiles and replays a hold packet only. It has no registry, secret, cluster, state, "
            "traffic, or executor adapter and cannot perform the next transition."
        ),
    }
    value["manifest_digest"] = _digest(value)
    return value


def benchmark() -> dict[str, Any]:
    return {
        "cutover_hold_version": CUTOVER_HOLD_VERSION,
        "quiescence_assessment_version": QUIESCENCE_ASSESSMENT_VERSION,
        "stale_base_fails_closed": True,
        "authority_reference_is_not_verification": True,
        "cutover_hold_replay": True,
        "cutover_execution_external": True,
    }


__all__ = [
    "CANARY_COMPARISON_KIND",
    "CANARY_OBSERVER_VERSION",
    "CANARY_WITNESS_VERSION",
    "CUTOVER_HOLD_VALIDATION_VERSION",
    "CUTOVER_HOLD_VERSION",
    "QUIESCENCE_ASSESSMENT_VERSION",
    "QUIESCENCE_OBSERVATION_VERSION",
    "assess_single_writer_quiescence",
    "benchmark",
    "compile_cutover_hold",
    "manifest",
    "validate_activation_plan_for_hold",
    "validate_canary_witness",
    "verify_cutover_hold",
]
