"""Fail-closed tests for KC144.XNAV.W16."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.replay_authority_ledger import (  # noqa: E402
    FrozenReplayAuthorityLedger,
    ReplayAuthorityLedgerError,
)


DATA = ROOT / "MCP" / "data" / "w16_replay_authority_ledger.json"
CAPSULES = ROOT / "MCP" / "data" / "w14_memory_digest_capsules.json"


def _registry() -> FrozenReplayAuthorityLedger:
    return FrozenReplayAuthorityLedger.load(DATA, CAPSULES)


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": "b4e24de38788ecdf30f43514ece279d1270b998b",
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": "ghcr.io/demeet2k/athena-mcp-server@sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2",
        "provider": {
            "id": "synthetic-provider",
            "account_scope": "synthetic-account",
            "deployment_id": "synthetic-deployment",
            "deployment_observed_at": "2026-07-27T08:05:00-07:00",
            "evidence_url": "https://evidence.invalid-domain.example.net/deploy/1",
        },
        "target": {
            "id": "synthetic-target",
            "endpoint": "https://athena.invalid-domain.example.net/mcp",
            "persistence_class": "managed-service",
            "secret_store_ref": "provider://synthetic/secret-reference",
        },
        "authorization": {
            "ref": "synthetic-authorization",
            "actor": "synthetic-authority",
            "authorized_at": "2026-07-27T08:00:00-07:00",
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
    provider = packet["provider"]
    target = packet["target"]
    return {
        "schema": "athena.provider-deployment-evidence/v1",
        "provider_id": provider["id"],
        "provider_account_scope": provider["account_scope"],
        "deployment_id": provider["deployment_id"],
        "target_id": target["id"],
        "authorization_ref": packet["authorization"]["ref"],
        "deployed_image": packet["image"],
        "image_digest": "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2",
        "source_commit": packet["source_commit"],
        "runtime_p09_head": packet["runtime_p09_head"],
        "endpoint": target["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": provider["deployment_observed_at"],
        "secret_store_ref": target["secret_store_ref"],
        "secret_material_recorded": False,
        "evidence_url": provider["evidence_url"],
    }


def test_frozen_ledger_verifies_two_append_only_rows() -> None:
    result = _registry().verify()
    assert result["status"] == "PASS_APPEND_ONLY_REPLAY_LEDGER_2_OF_2"
    assert result["row_count"] == 2
    assert result["ledger_root"] == (
        "sha256:4ae7fe2b2f390c876ca333cf5719b977"
        "97175d369997ce77f3329c47df0f316a"
    )
    assert result["internal_recall_claimed"] is False
    assert result["live_provider_read"] is False


def test_tampered_chain_and_alias_index_fail_closed() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    capsules = json.loads(CAPSULES.read_text(encoding="utf-8"))
    tampered = deepcopy(snapshot)
    tampered["replay_ledger"]["rows"][1]["prev_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ReplayAuthorityLedgerError, match="chain"):
        FrozenReplayAuthorityLedger.from_snapshots(tampered, capsules)

    aliased = deepcopy(snapshot)
    aliased["capsule_index"]["entries"]["F07"] = 1
    with pytest.raises(ReplayAuthorityLedgerError, match="exact-ID-only"):
        FrozenReplayAuthorityLedger.from_snapshots(aliased, capsules)


def test_opaque_replay_reconstructs_packet_and_rejects_station() -> None:
    registry = _registry()
    capsule_id = (
        "mcap:sha256:8797b945fb1ba77897f7b29076282c222"
        "a3e792122575d3562bb332a70c5fc3a"
    )
    result = registry.replay(capsule_id)
    assert result["status"] == (
        "PASS_LEDGER_BOUND_OPAQUE_EXTERNAL_CAPSULE_REPLAY"
    )
    assert result["reconstructed_packet"]["station"] == "F07"
    assert result["reconstructed_packet"]["source"]["revision_id"] == "34"
    assert result["current_conversation_queried"] is False
    assert result["internal_recall_claimed"] is False
    assert result["live_google_docs_read"] is False
    assert registry.replay("F07")["status"] == "REJECT_NON_OPAQUE_CAPSULE_ID"


def test_structural_packet_evidence_adjunction_is_not_live_authority() -> None:
    result = _registry().inspect_authority_evidence_adjunction(
        json.dumps(_packet()), json.dumps(_evidence())
    )
    assert result["status"] == (
        "PASS_STRUCTURAL_PACKET_EVIDENCE_ADJUNCTION_NOT_EXTERNALLY_WITNESSED"
    )
    assert result["packet_evidence_fields_match"] is True
    assert result["submitted_evidence_class"] == "UNVERIFIED_EXTERNAL_ASSERTION"
    assert result["submitted_inputs_persisted"] is False
    assert result["provider_evidence_fetched"] is False
    assert result["external_evidence_verified"] is False
    assert result["authorization_externally_verified"] is False
    assert result["secret_material_accepted"] is False
    assert result["endpoint_contacted"] is False
    assert result["persistent_witness_executed"] is False
    assert result["dispatch_allowed"] is False
    assert result["deployment_claimed"] is False
    assert result["promotion_claimed"] is False


def test_evidence_mismatch_and_secret_payload_are_rejected() -> None:
    mismatch = _evidence()
    mismatch["deployment_id"] = "different-deployment"
    result = _registry().inspect_authority_evidence_adjunction(
        json.dumps(_packet()), json.dumps(mismatch)
    )
    assert result["status"] == "HOLD_AUTHORITY_EVIDENCE_ADJUNCTION_REJECTED"
    assert result["dispatch_allowed"] is False

    packet = _packet()
    packet["bearer_token"] = "Bearer definitely-not-accepted"
    result = _registry().inspect_authority_evidence_adjunction(
        json.dumps(packet), json.dumps(_evidence())
    )
    assert result["status"] == "HOLD_AUTHORITY_EVIDENCE_ADJUNCTION_REJECTED"
    assert "forbidden secret material" in result["error"]
    assert result["secret_material_accepted"] is False


def test_authority_status_remains_unresolved_and_nondispatching() -> None:
    status = _registry().authority_status()
    assert status["status"] == (
        "AUTHORITY_EVIDENCE_ADJUNCTION_READY_INPUTS_UNRESOLVED"
    )
    assert status["unresolved_authority_input_count"] == 13
    assert status["activation_packet_present"] is False
    assert status["provider_evidence_present"] is False
    assert status["external_evidence_verified"] is False
    assert status["dispatch_allowed"] is False
    assert status["endpoint_contacted"] is False
