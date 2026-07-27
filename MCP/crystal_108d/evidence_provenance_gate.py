"""KC144.XNAV.W17 evidence-provenance witness and protected dispatch gate.

The public MCP surface is deliberately non-networked.  It can validate a
secret-free activation packet, matching provider evidence, and a provenance
envelope, but it cannot fetch the evidence URL or dispatch a live witness.

The CLI's ``fetch`` and ``authorize`` stages are intended only for the
workflow-dispatch job protected by the ``p10-persistent-host`` environment.
They bind a live, no-redirect evidence fetch to one exact GitHub run before a
run-scoped dispatch permit can be emitted.  No secret value is serialized.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from crystal_108d.replay_authority_ledger import (
    WITNESS_PLAN,
    _assert_secret_free,
    _canonical_bytes,
    _https_url,
    _validate_activation_packet,
    _validate_provider_evidence,
)


PHASE = "KC144.XNAV.W17"
ENVELOPE_SCHEMA = "athena.evidence-provenance-envelope/v1"
ENVELOPE_STATE = "DECLARED_FOR_PROTECTED_FETCH"
LIVE_WITNESS_SCHEMA = "athena.evidence-provenance-live-witness/v1"
LIVE_WITNESS_STATE = "PASS_LIVE_PROVENANCE_FETCH"
PERMIT_SCHEMA = "athena.protected-witness-dispatch-permit/v1"
RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
W16_HEAD = "97f7bdc917a29fe1f54192fdcd37e3704be736cd"
W16_PULL_REQUEST = 13
CONTROL_W16_HEAD = "33534798f458286d932706b57529a07776d15e15"
CONTROL_W16_PULL_REQUEST = 12
PROTECTED_ENVIRONMENT = "p10-persistent-host"
PROTECTED_SECRET_NAME = "ATHENA_MCP_BEARER_TOKEN"
MAXIMUM_BYTES = 65536
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")

ENVELOPE_FIELDS = {
    "schema",
    "state",
    "activation_packet_digest",
    "provider_evidence_digest",
    "evidence_url",
    "retrieval",
    "workflow_binding",
    "authority",
    "secret_material_recorded",
}
RETRIEVAL_FIELDS = {
    "mode",
    "maximum_bytes",
    "required_content_type",
    "redirects_allowed",
}
WORKFLOW_BINDING_FIELDS = {
    "repository",
    "ref",
    "sha",
    "protected_environment",
}
AUTHORITY_FIELDS = {
    "live_fetch_required",
    "explicit_dispatch_required",
    "runtime_can_promote",
    "promotion_claimed",
    "merge_claimed",
    "ic10_required",
}
LIVE_WITNESS_FIELDS = {
    "schema",
    "state",
    "activation_packet_digest",
    "provider_evidence_digest",
    "evidence_url",
    "fetched_at",
    "http_status",
    "content_type",
    "canonical_json_digest",
    "bytes_read",
    "redirect_count",
    "workflow",
    "secret_material_recorded",
}
LIVE_WORKFLOW_FIELDS = {
    "repository",
    "ref",
    "sha",
    "run_id",
    "run_attempt",
    "actor",
    "environment",
}


class EvidenceProvenanceGateError(RuntimeError):
    """Raised when a W17 provenance or dispatch contract fails closed."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _exact_object(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceProvenanceGateError(f"{path} must be an object")
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        raise EvidenceProvenanceGateError(
            f"{path} contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if missing:
        raise EvidenceProvenanceGateError(
            f"{path} is missing required fields: " + ", ".join(sorted(missing))
        )
    return value


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical_bytes(value)).hexdigest()


def _timestamp(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise EvidenceProvenanceGateError(f"{path} must be bounded ISO-8601 text")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise EvidenceProvenanceGateError(f"{path} must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise EvidenceProvenanceGateError(f"{path} must include a timezone")
    return value


def _parse_json(value: str, path: str) -> dict[str, Any]:
    if not isinstance(value, str) or len(value) > MAXIMUM_BYTES:
        raise EvidenceProvenanceGateError(
            f"{path} must be a bounded JSON object string"
        )
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as error:
        raise EvidenceProvenanceGateError(f"{path} is invalid JSON") from error
    if not isinstance(decoded, dict):
        raise EvidenceProvenanceGateError(f"{path} must contain an object")
    return decoded


def _normalized_inputs(
    activation_packet_json: str,
    provider_evidence_json: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    packet_raw = _parse_json(activation_packet_json, "activation_packet")
    evidence_raw = _parse_json(provider_evidence_json, "provider_evidence")
    _assert_secret_free(packet_raw, "activation_packet")
    _assert_secret_free(evidence_raw, "provider_evidence")
    try:
        packet = _validate_activation_packet(packet_raw)
        evidence = _validate_provider_evidence(evidence_raw, packet)
    except ValueError as error:
        raise EvidenceProvenanceGateError(str(error)) from error
    return packet, evidence


def validate_unresolved_template(value: Any) -> dict[str, Any]:
    envelope = _exact_object(value, ENVELOPE_FIELDS, "provenance envelope")
    if (
        envelope.get("schema") != ENVELOPE_SCHEMA
        or envelope.get("state") != "UNRESOLVED"
    ):
        raise EvidenceProvenanceGateError(
            "unresolved provenance template has the wrong schema or state"
        )
    for field in (
        "activation_packet_digest",
        "provider_evidence_digest",
        "evidence_url",
    ):
        if envelope.get(field) is not None:
            raise EvidenceProvenanceGateError(
                f"unresolved provenance template {field} must remain null"
            )
    retrieval = _exact_object(
        envelope.get("retrieval"), RETRIEVAL_FIELDS, "retrieval"
    )
    if retrieval != {
        "mode": "protected-live-fetch",
        "maximum_bytes": MAXIMUM_BYTES,
        "required_content_type": "application/json",
        "redirects_allowed": False,
    }:
        raise EvidenceProvenanceGateError(
            "unresolved template must preserve the exact retrieval contract"
        )
    binding = _exact_object(
        envelope.get("workflow_binding"),
        WORKFLOW_BINDING_FIELDS,
        "workflow_binding",
    )
    if binding != {
        "repository": RUNTIME_REPOSITORY,
        "ref": None,
        "sha": None,
        "protected_environment": PROTECTED_ENVIRONMENT,
    }:
        raise EvidenceProvenanceGateError(
            "unresolved template must preserve the protected workflow binding"
        )
    _validate_authority(envelope.get("authority"))
    if envelope.get("secret_material_recorded") is not False:
        raise EvidenceProvenanceGateError(
            "provenance template must not record secret material"
        )
    return envelope


def _validate_authority(value: Any) -> dict[str, Any]:
    authority = _exact_object(value, AUTHORITY_FIELDS, "authority")
    expected = {
        "live_fetch_required": True,
        "explicit_dispatch_required": True,
        "runtime_can_promote": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "ic10_required": True,
    }
    if authority != expected:
        raise EvidenceProvenanceGateError(
            "provenance envelope crosses the nonpromotion authority boundary"
        )
    return authority


def _validate_envelope(
    value: Any,
    packet: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    _assert_secret_free(value, "provenance_envelope")
    envelope = _exact_object(value, ENVELOPE_FIELDS, "provenance envelope")
    if (
        envelope.get("schema") != ENVELOPE_SCHEMA
        or envelope.get("state") != ENVELOPE_STATE
    ):
        raise EvidenceProvenanceGateError(
            "provenance envelope has the wrong schema or state"
        )
    packet_digest = _digest(packet)
    evidence_digest = _digest(evidence)
    if envelope.get("activation_packet_digest") != packet_digest:
        raise EvidenceProvenanceGateError("activation packet digest mismatch")
    if envelope.get("provider_evidence_digest") != evidence_digest:
        raise EvidenceProvenanceGateError("provider evidence digest mismatch")
    try:
        evidence_url = _https_url(
            envelope.get("evidence_url"), "evidence_url"
        )
    except ValueError as error:
        raise EvidenceProvenanceGateError(str(error)) from error
    if evidence_url != evidence["evidence_url"]:
        raise EvidenceProvenanceGateError(
            "provenance evidence_url must equal provider evidence"
        )
    retrieval = _exact_object(
        envelope.get("retrieval"), RETRIEVAL_FIELDS, "retrieval"
    )
    if retrieval != {
        "mode": "protected-live-fetch",
        "maximum_bytes": MAXIMUM_BYTES,
        "required_content_type": "application/json",
        "redirects_allowed": False,
    }:
        raise EvidenceProvenanceGateError(
            "provenance envelope must require bounded no-redirect JSON fetch"
        )
    binding = _exact_object(
        envelope.get("workflow_binding"),
        WORKFLOW_BINDING_FIELDS,
        "workflow_binding",
    )
    if binding.get("repository") != RUNTIME_REPOSITORY:
        raise EvidenceProvenanceGateError("workflow repository mismatch")
    ref = binding.get("ref")
    if not isinstance(ref, str) or not ref.startswith("refs/heads/"):
        raise EvidenceProvenanceGateError(
            "workflow ref must name an exact branch ref"
        )
    sha = binding.get("sha")
    if not isinstance(sha, str) or not GIT_SHA.fullmatch(sha):
        raise EvidenceProvenanceGateError(
            "workflow sha must be a full lowercase Git commit"
        )
    if binding.get("protected_environment") != PROTECTED_ENVIRONMENT:
        raise EvidenceProvenanceGateError("protected environment mismatch")
    _validate_authority(envelope.get("authority"))
    if envelope.get("secret_material_recorded") is not False:
        raise EvidenceProvenanceGateError(
            "provenance envelope must not record secret material"
        )
    return {
        **envelope,
        "activation_packet_digest": packet_digest,
        "provider_evidence_digest": evidence_digest,
        "evidence_url": evidence_url,
    }


def inspect_provenance(
    activation_packet_json: str,
    provider_evidence_json: str,
    provenance_envelope_json: str,
) -> dict[str, Any]:
    try:
        packet, evidence = _normalized_inputs(
            activation_packet_json, provider_evidence_json
        )
        envelope = _validate_envelope(
            _parse_json(provenance_envelope_json, "provenance_envelope"),
            packet,
            evidence,
        )
        return {
            "status": (
                "PASS_STRUCTURAL_PROVENANCE_ENVELOPE_NOT_LIVE_FETCHED"
            ),
            "phase": PHASE,
            "activation_packet_digest": envelope["activation_packet_digest"],
            "provider_evidence_digest": envelope[
                "provider_evidence_digest"
            ],
            "evidence_url": envelope["evidence_url"],
            "workflow_binding": envelope["workflow_binding"],
            "live_fetch_executed": False,
            "external_evidence_verified": False,
            "protected_environment_admitted": False,
            "bearer_secret_available": False,
            "secret_material_accepted": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
        }
    except (EvidenceProvenanceGateError, ValueError) as error:
        return {
            "status": "HOLD_EVIDENCE_PROVENANCE_REJECTED",
            "phase": PHASE,
            "error": str(error),
            "live_fetch_executed": False,
            "external_evidence_verified": False,
            "protected_environment_admitted": False,
            "bearer_secret_available": False,
            "secret_material_accepted": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
        }


def _workflow_context() -> dict[str, Any]:
    required = {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "ref": os.environ.get("GITHUB_REF"),
        "sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "actor": os.environ.get("GITHUB_ACTOR"),
        "environment": os.environ.get("ATHENA_W17_PROTECTED_ENVIRONMENT"),
    }
    if any(value is None or value == "" for value in required.values()):
        raise EvidenceProvenanceGateError(
            "protected workflow context is incomplete"
        )
    try:
        required["run_id"] = int(str(required["run_id"]))
        required["run_attempt"] = int(str(required["run_attempt"]))
    except ValueError as error:
        raise EvidenceProvenanceGateError(
            "workflow run identifiers must be integers"
        ) from error
    if required["run_id"] <= 0 or required["run_attempt"] <= 0:
        raise EvidenceProvenanceGateError(
            "workflow run identifiers must be positive"
        )
    return required


def _fetch_json(
    evidence_url: str,
    timeout: int,
) -> tuple[dict[str, Any], int, str, int]:
    opener = build_opener(_NoRedirect)
    request = Request(
        evidence_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "athena-w17-provenance-witness/1",
        },
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            status = int(response.status)
            content_type = response.headers.get_content_type()
            body = response.read(MAXIMUM_BYTES + 1)
    except HTTPError as error:
        raise EvidenceProvenanceGateError(
            f"evidence fetch failed closed with HTTP {error.code}"
        ) from error
    if status != 200:
        raise EvidenceProvenanceGateError(
            f"evidence fetch requires HTTP 200, received {status}"
        )
    if content_type != "application/json":
        raise EvidenceProvenanceGateError(
            "evidence fetch requires application/json"
        )
    if len(body) > MAXIMUM_BYTES:
        raise EvidenceProvenanceGateError(
            "evidence response exceeds the maximum byte budget"
        )
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceProvenanceGateError(
            "evidence response is not UTF-8 JSON"
        ) from error
    if not isinstance(decoded, dict):
        raise EvidenceProvenanceGateError(
            "evidence response must contain a JSON object"
        )
    return decoded, status, content_type, len(body)


def fetch_live_provenance(
    activation_packet_json: str,
    provider_evidence_json: str,
    provenance_envelope_json: str,
    *,
    timeout: int = 30,
) -> dict[str, Any]:
    packet, evidence = _normalized_inputs(
        activation_packet_json, provider_evidence_json
    )
    envelope = _validate_envelope(
        _parse_json(provenance_envelope_json, "provenance_envelope"),
        packet,
        evidence,
    )
    workflow = _workflow_context()
    binding = envelope["workflow_binding"]
    for field in ("repository", "ref", "sha"):
        if workflow[field] != binding[field]:
            raise EvidenceProvenanceGateError(
                f"live workflow {field} does not match provenance binding"
            )
    if workflow["environment"] != PROTECTED_ENVIRONMENT:
        raise EvidenceProvenanceGateError(
            "live fetch requires the protected environment"
        )
    fetched, status, content_type, bytes_read = _fetch_json(
        envelope["evidence_url"], timeout
    )
    try:
        normalized_fetched = _validate_provider_evidence(fetched, packet)
    except ValueError as error:
        raise EvidenceProvenanceGateError(str(error)) from error
    if _canonical_bytes(normalized_fetched) != _canonical_bytes(evidence):
        raise EvidenceProvenanceGateError(
            "live-fetched provider evidence does not equal admitted evidence"
        )
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if now.endswith("+00:00"):
        now = now[:-6] + "Z"
    return {
        "schema": LIVE_WITNESS_SCHEMA,
        "state": LIVE_WITNESS_STATE,
        "activation_packet_digest": _digest(packet),
        "provider_evidence_digest": _digest(evidence),
        "evidence_url": envelope["evidence_url"],
        "fetched_at": now,
        "http_status": status,
        "content_type": content_type,
        "canonical_json_digest": _digest(normalized_fetched),
        "bytes_read": bytes_read,
        "redirect_count": 0,
        "workflow": workflow,
        "secret_material_recorded": False,
    }


def _validate_live_witness(
    value: Any,
    envelope: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    _assert_secret_free(value, "live_provenance_witness")
    witness = _exact_object(
        value, LIVE_WITNESS_FIELDS, "live provenance witness"
    )
    if (
        witness.get("schema") != LIVE_WITNESS_SCHEMA
        or witness.get("state") != LIVE_WITNESS_STATE
    ):
        raise EvidenceProvenanceGateError(
            "live provenance witness has the wrong schema or state"
        )
    expected_digest = _digest(evidence)
    expected = {
        "activation_packet_digest": envelope["activation_packet_digest"],
        "provider_evidence_digest": expected_digest,
        "evidence_url": envelope["evidence_url"],
        "http_status": 200,
        "content_type": "application/json",
        "canonical_json_digest": expected_digest,
        "redirect_count": 0,
        "secret_material_recorded": False,
    }
    mismatches = [
        field
        for field, expected_value in expected.items()
        if witness.get(field) != expected_value
    ]
    if mismatches:
        raise EvidenceProvenanceGateError(
            "live provenance witness mismatch: " + ", ".join(mismatches)
        )
    _timestamp(witness.get("fetched_at"), "fetched_at")
    bytes_read = witness.get("bytes_read")
    if not isinstance(bytes_read, int) or not 0 < bytes_read <= MAXIMUM_BYTES:
        raise EvidenceProvenanceGateError(
            "live provenance bytes_read is outside the admitted budget"
        )
    workflow = _exact_object(
        witness.get("workflow"), LIVE_WORKFLOW_FIELDS, "workflow"
    )
    binding = envelope["workflow_binding"]
    for field in ("repository", "ref", "sha"):
        if workflow.get(field) != binding[field]:
            raise EvidenceProvenanceGateError(
                f"witness workflow {field} does not match envelope"
            )
    if workflow.get("environment") != PROTECTED_ENVIRONMENT:
        raise EvidenceProvenanceGateError(
            "witness workflow did not enter the protected environment"
        )
    if (
        not isinstance(workflow.get("run_id"), int)
        or workflow["run_id"] <= 0
        or not isinstance(workflow.get("run_attempt"), int)
        or workflow["run_attempt"] <= 0
    ):
        raise EvidenceProvenanceGateError(
            "witness workflow run identity is invalid"
        )
    actor = workflow.get("actor")
    if not isinstance(actor, str) or not actor or len(actor) > 128:
        raise EvidenceProvenanceGateError("witness actor is invalid")
    return witness


def authorize_dispatch(
    activation_packet_json: str,
    provider_evidence_json: str,
    provenance_envelope_json: str,
    live_witness_json: str,
) -> dict[str, Any]:
    try:
        packet, evidence = _normalized_inputs(
            activation_packet_json, provider_evidence_json
        )
        envelope = _validate_envelope(
            _parse_json(provenance_envelope_json, "provenance_envelope"),
            packet,
            evidence,
        )
        witness = _validate_live_witness(
            _parse_json(live_witness_json, "live_provenance_witness"),
            envelope,
            evidence,
        )
        workflow = _workflow_context()
        if workflow != witness["workflow"]:
            raise EvidenceProvenanceGateError(
                "current workflow does not equal live provenance witness"
            )
        if os.environ.get("GITHUB_ACTIONS") != "true":
            raise EvidenceProvenanceGateError(
                "dispatch permits are emitted only inside GitHub Actions"
            )
        if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch":
            raise EvidenceProvenanceGateError(
                "dispatch permits require workflow_dispatch"
            )
        if os.environ.get("ATHENA_W17_EXECUTE_LIVE_WITNESS") != "true":
            raise EvidenceProvenanceGateError(
                "explicit live-witness dispatch intent is absent"
            )
        bearer = os.environ.get(PROTECTED_SECRET_NAME)
        if not isinstance(bearer, str) or len(bearer) < 32:
            raise EvidenceProvenanceGateError(
                "protected bearer secret is unavailable or too short"
            )
        body = {
            "schema": PERMIT_SCHEMA,
            "phase": PHASE,
            "verdict": (
                "PASS_PROTECTED_DISPATCH_GATE_LIVE_WITNESS_NOT_YET_EXECUTED"
            ),
            "activation_packet_digest": envelope[
                "activation_packet_digest"
            ],
            "provider_evidence_digest": envelope[
                "provider_evidence_digest"
            ],
            "live_provenance_witness_digest": _digest(witness),
            "target": {
                "endpoint": packet["target"]["endpoint"],
                "deployment_id": packet["provider"]["deployment_id"],
                "image": packet["image"],
            },
            "workflow": workflow,
            "witness_plan": WITNESS_PLAN,
            "external_evidence_verified": True,
            "protected_environment_admitted": True,
            "bearer_secret_available": True,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": True,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        }
        return {
            "permit_id": "w17-dispatch:" + _digest(body).split(":", 1)[1],
            **body,
        }
    except (EvidenceProvenanceGateError, ValueError) as error:
        return {
            "schema": PERMIT_SCHEMA,
            "phase": PHASE,
            "verdict": "HOLD_PROTECTED_DISPATCH_GATE",
            "error": str(error),
            "external_evidence_verified": False,
            "protected_environment_admitted": False,
            "bearer_secret_available": False,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        }


def gate_status() -> dict[str, Any]:
    return {
        "status": "READY_EVIDENCE_PROVENANCE_GATE_AUTHORITY_INPUTS_UNRESOLVED",
        "phase": PHASE,
        "lineage": {
            "runtime_w16_pull_request": W16_PULL_REQUEST,
            "runtime_w16_head": W16_HEAD,
            "control_w16_pull_request": CONTROL_W16_PULL_REQUEST,
            "control_w16_head": CONTROL_W16_HEAD,
        },
        "required_inputs": {
            "activation_packet": False,
            "provider_evidence": False,
            "provenance_envelope": False,
            "protected_bearer": False,
        },
        "retrieval_contract": {
            "mode": "protected-live-fetch",
            "maximum_bytes": MAXIMUM_BYTES,
            "required_content_type": "application/json",
            "redirects_allowed": False,
        },
        "protected_environment": PROTECTED_ENVIRONMENT,
        "protected_secret_name": PROTECTED_SECRET_NAME,
        "authority_inputs_unresolved": 13,
        "live_fetch_executed": False,
        "external_evidence_verified": False,
        "dispatch_allowed": False,
        "endpoint_contacted": False,
        "persistent_witness_executed": False,
        "secret_material_recorded": False,
        "runtime_can_promote": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "ic10_required": True,
        "successor": (
            "KC144.XNAV.W18::AUTHORIZED-PROVENANCE-FETCH-AND-"
            "PERSISTENT-ENDPOINT-WITNESS"
        ),
    }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_evidence_provenance_gate(mcp: Any) -> None:
    """Register non-networked W17 inspection and status surfaces."""

    @mcp.tool()
    def athena_w17_evidence_provenance_gate_status() -> str:
        """Report the W17 gate and unresolved external authority boundary."""
        return _render(gate_status())

    @mcp.tool()
    def inspect_athena_w17_evidence_provenance(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_envelope_json: str,
    ) -> str:
        """Structurally inspect W17 inputs without fetching or dispatching."""
        return _render(
            inspect_provenance(
                activation_packet_json,
                provider_evidence_json,
                provenance_envelope_json,
            )
        )

    @mcp.resource("athena://w17/evidence-provenance-dispatch-gate")
    def evidence_provenance_dispatch_gate_resource() -> str:
        """Expose the non-networked W17 gate state."""
        return _render(gate_status())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("check-template")
    template.add_argument("envelope", type=Path)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("packet", type=Path)
    preflight.add_argument("evidence", type=Path)
    preflight.add_argument("envelope", type=Path)
    preflight.add_argument("--output", type=Path, required=True)

    fetch = subparsers.add_parser("fetch")
    fetch.add_argument("packet", type=Path)
    fetch.add_argument("evidence", type=Path)
    fetch.add_argument("envelope", type=Path)
    fetch.add_argument("--output", type=Path, required=True)
    fetch.add_argument("--timeout", type=int, default=30)

    authorize = subparsers.add_parser("authorize")
    authorize.add_argument("packet", type=Path)
    authorize.add_argument("evidence", type=Path)
    authorize.add_argument("envelope", type=Path)
    authorize.add_argument("live_witness", type=Path)
    authorize.add_argument("--output", type=Path, required=True)

    arguments = parser.parse_args()
    if arguments.command == "check-template":
        value = json.loads(arguments.envelope.read_text(encoding="utf-8"))
        validate_unresolved_template(value)
        print("PASS_UNRESOLVED_W17_PROVENANCE_TEMPLATE")
        return 0
    if arguments.command == "preflight":
        result = inspect_provenance(
            _read(arguments.packet),
            _read(arguments.evidence),
            _read(arguments.envelope),
        )
        _write_json(arguments.output, result)
        print(_render(result))
        return 0 if result["status"].startswith("PASS_") else 1
    if arguments.command == "fetch":
        result = fetch_live_provenance(
            _read(arguments.packet),
            _read(arguments.evidence),
            _read(arguments.envelope),
            timeout=arguments.timeout,
        )
        _write_json(arguments.output, result)
        print(_render(result))
        return 0
    result = authorize_dispatch(
        _read(arguments.packet),
        _read(arguments.evidence),
        _read(arguments.envelope),
        _read(arguments.live_witness),
    )
    _write_json(arguments.output, result)
    print(_render(result))
    return 0 if result["dispatch_allowed"] is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
