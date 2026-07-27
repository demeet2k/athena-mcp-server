"""Fail-closed tests for KC144.XNAV.W17."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.evidence_provenance_gate import (  # noqa: E402
    ENVELOPE_SCHEMA,
    LIVE_WITNESS_SCHEMA,
    LIVE_WITNESS_STATE,
    authorize_dispatch,
    gate_status,
    inspect_provenance,
    validate_unresolved_template,
    _digest,
)
from crystal_108d.replay_authority_ledger import (  # noqa: E402
    _validate_activation_packet,
    _validate_provider_evidence,
)


RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w17-evidence-provenance-dispatch-gate.json"
)
TEMPLATE = ROOT / "deploy" / "w17" / "evidence-provenance.example.json"
W17_SHA = "1" * 40


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": (
            "b4e24de38788ecdf30f43514ece279d1270b998b"
        ),
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": (
            "ghcr.io/demeet2k/athena-mcp-server@"
            "sha256:31458783d4aeb28e0a4036cb4fab39a2"
            "f2bc1f4ef6e3025d126c78a865162ad2"
        ),
        "provider": {
            "id": "provider-alpha",
            "account_scope": "account-alpha",
            "deployment_id": "deployment-alpha",
            "deployment_observed_at": "2026-07-27T08:45:00-07:00",
            "evidence_url": (
                "https://evidence.provider.example.org/deploy/alpha.json"
            ),
        },
        "target": {
            "id": "athena-alpha",
            "endpoint": "https://athena.provider.example.org/mcp",
            "persistence_class": "managed-service",
            "secret_store_ref": "provider://account-alpha/athena-token",
        },
        "authorization": {
            "ref": "authorization-alpha",
            "actor": "authorized-operator",
            "authorized_at": "2026-07-27T08:40:00-07:00",
        },
        "witness": {
            "environment": "p10-persistent-host",
            "secret_name": "ATHENA_MCP_BEARER_TOKEN",
            "sample_count": 3,
            "interval_seconds": 20,
            "minimum_span_seconds": 40,
        },
        "authority": {
            "live_witness_authorized": True,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "secret_material_recorded": False,
    }


def _evidence() -> dict:
    packet = _packet()
    return {
        "schema": "athena.provider-deployment-evidence/v1",
        "provider_id": packet["provider"]["id"],
        "provider_account_scope": packet["provider"]["account_scope"],
        "deployment_id": packet["provider"]["deployment_id"],
        "target_id": packet["target"]["id"],
        "authorization_ref": packet["authorization"]["ref"],
        "deployed_image": packet["image"],
        "image_digest": packet["image"].split("@", 1)[1],
        "source_commit": packet["source_commit"],
        "runtime_p09_head": packet["runtime_p09_head"],
        "endpoint": packet["target"]["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": packet["provider"][
            "deployment_observed_at"
        ],
        "secret_store_ref": packet["target"]["secret_store_ref"],
        "secret_material_recorded": False,
        "evidence_url": packet["provider"]["evidence_url"],
    }


def _envelope() -> dict:
    packet = _validate_activation_packet(_packet())
    evidence = _validate_provider_evidence(_evidence(), packet)
    return {
        "schema": ENVELOPE_SCHEMA,
        "state": "DECLARED_FOR_PROTECTED_FETCH",
        "activation_packet_digest": _digest(packet),
        "provider_evidence_digest": _digest(evidence),
        "evidence_url": evidence["evidence_url"],
        "retrieval": {
            "mode": "protected-live-fetch",
            "maximum_bytes": 65536,
            "required_content_type": "application/json",
            "redirects_allowed": False,
        },
        "workflow_binding": {
            "repository": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/agent/w17-evidence-provenance-dispatch-gate",
            "sha": W17_SHA,
            "protected_environment": "p10-persistent-host",
        },
        "authority": {
            "live_fetch_required": True,
            "explicit_dispatch_required": True,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "secret_material_recorded": False,
    }


def _live_witness() -> dict:
    packet = _validate_activation_packet(_packet())
    evidence = _validate_provider_evidence(_evidence(), packet)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "schema": LIVE_WITNESS_SCHEMA,
        "state": LIVE_WITNESS_STATE,
        "activation_packet_digest": _digest(packet),
        "provider_evidence_digest": _digest(evidence),
        "evidence_url": evidence["evidence_url"],
        "fetched_at": now,
        "http_status": 200,
        "content_type": "application/json",
        "canonical_json_digest": _digest(evidence),
        "bytes_read": 1024,
        "redirect_count": 0,
        "workflow": {
            "repository": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/agent/w17-evidence-provenance-dispatch-gate",
            "sha": W17_SHA,
            "run_id": 12345,
            "run_attempt": 1,
            "actor": "authorized-operator",
            "environment": "p10-persistent-host",
        },
        "secret_material_recorded": False,
    }


def _json(value: dict) -> str:
    return json.dumps(value)


def test_unresolved_template_is_explicitly_nondispatching() -> None:
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert validate_unresolved_template(template) == template
    assert template["activation_packet_digest"] is None
    assert template["provider_evidence_digest"] is None
    assert template["evidence_url"] is None
    assert template["retrieval"]["redirects_allowed"] is False


def test_structural_provenance_does_not_become_live_evidence() -> None:
    result = inspect_provenance(
        _json(_packet()), _json(_evidence()), _json(_envelope())
    )
    assert result["status"] == (
        "PASS_STRUCTURAL_PROVENANCE_ENVELOPE_NOT_LIVE_FETCHED"
    )
    assert result["live_fetch_executed"] is False
    assert result["external_evidence_verified"] is False
    assert result["protected_environment_admitted"] is False
    assert result["bearer_secret_available"] is False
    assert result["endpoint_contacted"] is False
    assert result["persistent_witness_executed"] is False
    assert result["dispatch_allowed"] is False
    assert result["runtime_can_promote"] is False


def test_digest_tamper_redirects_and_secrets_fail_closed() -> None:
    tampered = deepcopy(_envelope())
    tampered["provider_evidence_digest"] = "sha256:" + "0" * 64
    result = inspect_provenance(
        _json(_packet()), _json(_evidence()), _json(tampered)
    )
    assert result["status"] == "HOLD_EVIDENCE_PROVENANCE_REJECTED"
    assert result["dispatch_allowed"] is False

    redirects = deepcopy(_envelope())
    redirects["retrieval"]["redirects_allowed"] = True
    result = inspect_provenance(
        _json(_packet()), _json(_evidence()), _json(redirects)
    )
    assert result["status"] == "HOLD_EVIDENCE_PROVENANCE_REJECTED"
    assert result["dispatch_allowed"] is False

    secret = deepcopy(_packet())
    secret["bearer_token"] = "Bearer never-admitted"
    result = inspect_provenance(
        _json(secret), _json(_evidence()), _json(_envelope())
    )
    assert result["status"] == "HOLD_EVIDENCE_PROVENANCE_REJECTED"
    assert result["secret_material_accepted"] is False


def test_dispatch_requires_exact_protected_workflow_context_and_secret() -> None:
    empty = authorize_dispatch(
        _json(_packet()),
        _json(_evidence()),
        _json(_envelope()),
        _json(_live_witness()),
    )
    assert empty["verdict"] == "HOLD_PROTECTED_DISPATCH_GATE"
    assert empty["dispatch_allowed"] is False
    assert empty["endpoint_contacted"] is False

    environment = {
        "GITHUB_REPOSITORY": "demeet2k/athena-mcp-server",
        "GITHUB_REF": (
            "refs/heads/agent/w17-evidence-provenance-dispatch-gate"
        ),
        "GITHUB_SHA": W17_SHA,
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_ACTOR": "authorized-operator",
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "ATHENA_W17_PROTECTED_ENVIRONMENT": "p10-persistent-host",
        "ATHENA_W17_EXECUTE_LIVE_WITNESS": "true",
        "ATHENA_MCP_BEARER_TOKEN": "x" * 32,
    }
    with mock.patch.dict(os.environ, environment, clear=True):
        permit = authorize_dispatch(
            _json(_packet()),
            _json(_evidence()),
            _json(_envelope()),
            _json(_live_witness()),
        )
    assert permit["verdict"] == (
        "PASS_PROTECTED_DISPATCH_GATE_LIVE_WITNESS_NOT_YET_EXECUTED"
    )
    assert permit["external_evidence_verified"] is True
    assert permit["protected_environment_admitted"] is True
    assert permit["bearer_secret_available"] is True
    assert permit["secret_material_recorded"] is False
    assert permit["dispatch_allowed"] is True
    assert permit["endpoint_contacted"] is False
    assert permit["persistent_witness_executed"] is False
    assert permit["runtime_can_promote"] is False


def test_static_gate_and_receipt_preserve_w16_and_authority_holds() -> None:
    status = gate_status()
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    assert status["lineage"]["runtime_w16_head"] == (
        "97f7bdc917a29fe1f54192fdcd37e3704be736cd"
    )
    assert status["lineage"]["control_w16_head"] == (
        "33534798f458286d932706b57529a07776d15e15"
    )
    assert status["authority_inputs_unresolved"] == 13
    assert status["external_evidence_verified"] is False
    assert status["dispatch_allowed"] is False
    assert status["endpoint_contacted"] is False
    assert status["promotion_claimed"] is False

    assert receipt["w16_boundary_preserved"][
        "submitted_evidence_class"
    ] == "UNVERIFIED_EXTERNAL_ASSERTION"
    assert receipt["replay_measurements_preserved"]["w15_uncued"] == {
        "conversation_memory_exact_fields": 0,
        "persisted_file_memory_exact_fields": 10,
        "external_capsule_exact_fields": 14,
    }
    assert receipt["replay_measurements_preserved"]["w14_historical"] == {
        "conversation_memory_exact_fields": 10,
        "persisted_file_memory_exact_fields": 12,
        "external_capsule_exact_fields": 14,
        "rewritten": False,
    }
    assert receipt["protected_dispatch"]["dispatch_permit_emitted"] is False
    assert receipt["authority"]["deployment_claimed"] is False
    assert receipt["authority"]["merge_claimed"] is False
    assert receipt["authority"]["promotion_claimed"] is False
