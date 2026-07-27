"""Contract tests for KC144.XNAV.W15 replay and authority ingress."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "MCP"))

from crystal_108d.capsule_replay_ingress import (  # noqa: E402
    AUTHORIZED_STATE,
    FrozenCapsuleReplayIngress,
)


F07_CAPSULE = (
    "mcap:sha256:"
    "8797b945fb1ba77897f7b29076282c222a3e792122575d3562bb332a70c5fc3a"
)
M09_CAPSULE = (
    "mcap:sha256:"
    "d89fbf78b35777cc55b1ad0e3518f1868cc2d4cce6ab78b62747b2291f9dfb0b"
)
RECEIPT_PATH = (
    REPO_ROOT
    / ".athena"
    / "receipts"
    / "w15-capsule-blind-replay-authority-ingress.json"
)


def _unresolved_packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "UNRESOLVED",
        "canonical_hardening_head": (
            "b4e24de38788ecdf30f43514ece279d1270b998b"
        ),
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": (
            "ghcr.io/demeet2k/athena-mcp-server@sha256:"
            "31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
        ),
        "provider": {
            "id": None,
            "account_scope": None,
            "deployment_id": None,
            "deployment_observed_at": None,
            "evidence_url": None,
        },
        "target": {
            "id": None,
            "endpoint": None,
            "persistence_class": None,
            "secret_store_ref": None,
        },
        "authorization": {
            "ref": None,
            "actor": None,
            "authorized_at": None,
        },
        "witness": {
            "environment": "p10-persistent-host",
            "secret_name": "ATHENA_P10_BEARER_TOKEN",
            "sample_count": 3,
            "interval_seconds": 20,
            "minimum_span_seconds": 40,
        },
        "authority": {
            "live_witness_authorized": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "secret_material_recorded": False,
    }


def _authorized_packet() -> dict:
    packet = _unresolved_packet()
    packet["state"] = AUTHORIZED_STATE
    packet["provider"] = {
        "id": "authorized-provider",
        "account_scope": "logical-account-scope",
        "deployment_id": "deployment-123",
        "deployment_observed_at": "2026-07-27T07:30:00Z",
        "evidence_url": "https://provider.example/deployments/deployment-123",
    }
    packet["target"] = {
        "id": "athena-p10-production",
        "endpoint": "https://athena.example/mcp",
        "persistence_class": "managed-service",
        "secret_store_ref": "provider://secrets/athena-p10-bearer",
    }
    packet["authorization"] = {
        "ref": "change-control:approved-123",
        "actor": "authorized-operator",
        "authorized_at": "2026-07-27T07:29:00Z",
    }
    packet["authority"]["live_witness_authorized"] = True
    return packet


def test_frozen_challenges_pass_from_opaque_capsule_ids_only() -> None:
    status = FrozenCapsuleReplayIngress.load().replay_status()

    assert status["status"] == "PASS_ALL_OPAQUE_CAPSULE_REPLAYS"
    assert status["challenge_count"] == 2
    assert status["passed"] == 2
    assert status["failed"] == 0
    assert status["input_fields"] == ["capsule_id"]
    assert status["internal_recall_claimed"] is False
    assert status["live_provider_read"] is False
    assert all(
        result["exact_packet_reconstructed"] is True
        for result in status["results"]
    )


def test_f07_opaque_replay_reconstructs_exact_full_packet() -> None:
    result = FrozenCapsuleReplayIngress.load().replay(F07_CAPSULE)
    packet = result["packet"]

    assert result["status"] == "PASS_OPAQUE_CAPSULE_BLIND_REPLAY"
    assert result["input"] == {"capsule_id": F07_CAPSULE}
    assert result["packet_digest"] == "sha256:" + F07_CAPSULE.split(":")[-1]
    assert packet["station"] == "F07"
    assert packet["rid"] == "rid:kc144:gid050:f07:analytic-branch-cover"
    assert packet["source"]["revision_id"] == "34"
    assert packet["source"]["range"] == {
        "start": 48973,
        "end": 48998,
        "interval": "half-open",
    }
    assert packet["source"]["literal_sha256"] == (
        "9ff39e3f43c43e077fff00ef05fb40da"
        "64440a4af49eeb83f63011cd10b15939"
    )


def test_m09_opaque_replay_reconstructs_exact_full_packet() -> None:
    result = FrozenCapsuleReplayIngress.load().replay(M09_CAPSULE)

    assert result["status"] == "PASS_OPAQUE_CAPSULE_BLIND_REPLAY"
    assert result["packet_digest"] == "sha256:" + M09_CAPSULE.split(":")[-1]
    assert result["packet"]["station"] == "M09"
    assert result["packet"]["rid"] == "rid:kc144:gid141:m09:path-signature"
    assert result["packet"]["source"]["literal"] == (
        "A hidden hash is insufficient"
    )


def test_blind_replay_rejects_station_rid_and_fuzzy_inputs() -> None:
    registry = FrozenCapsuleReplayIngress.load()

    for identifier in (
        "F07",
        "rid:kc144:gid050:f07:analytic-branch-cover",
        "F07-ish",
    ):
        result = registry.replay(identifier)
        assert result["status"] == "INVALID_BLIND_REPLAY_ADDRESS"
        assert result["accepted_coordinate_classes"] == ["capsule_id"]
        assert result["fuzzy_substitution_used"] is False


def test_tampered_challenge_packet_digest_fails_closed(tmp_path: Path) -> None:
    snapshot = deepcopy(FrozenCapsuleReplayIngress.load().snapshot)
    snapshot["blind_replay"]["challenges"][0][
        "expected_packet_digest"
    ] = "sha256:" + "0" * 64
    path = tmp_path / "tampered-w15.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(
        RuntimeError,
        match="challenge packet digest must equal",
    ):
        FrozenCapsuleReplayIngress.load(path)


def test_unresolved_template_is_structurally_valid_but_held() -> None:
    result = FrozenCapsuleReplayIngress.load().inspect_authority_packet(
        json.dumps(_unresolved_packet())
    )

    assert result["status"] == "HOLD_AUTHORITY_INPUTS_UNRESOLVED"
    assert result["packet_state"] == "UNRESOLVED"
    assert result["structurally_valid"] is True
    assert len(result["unresolved_authority_inputs"]) == 13
    assert result["external_authority_verified"] is False
    assert result["secret_value_accepted"] is False
    assert result["endpoint_contacted"] is False
    assert result["dispatch_allowed"] is False


def test_authorized_claim_packet_is_only_structurally_admitted() -> None:
    result = FrozenCapsuleReplayIngress.load().inspect_authority_packet(
        json.dumps(_authorized_packet())
    )

    assert result["status"] == (
        "PASS_STRUCTURAL_AUTHORITY_PACKET_INGRESS_NOT_DISPATCHED"
    )
    assert result["packet_state"] == AUTHORIZED_STATE
    assert result["structurally_valid"] is True
    assert result["authority_claims_present"] is True
    assert result["external_authority_verified"] is False
    assert result["provider_evidence_fetched"] is False
    assert result["submitted_packet_persisted"] is False
    assert result["secret_value_accepted"] is False
    assert result["endpoint_contacted"] is False
    assert result["dispatch_allowed"] is False
    assert result["runtime_can_promote"] is False
    assert len(result["remaining_external_gates"]) == 7


def test_unknown_secret_bearing_field_is_rejected() -> None:
    packet = _authorized_packet()
    packet["token"] = "must-never-enter-ingress"
    result = FrozenCapsuleReplayIngress.load().inspect_authority_packet(
        json.dumps(packet)
    )

    assert result["status"] == "REJECTED_AUTHORITY_PACKET"
    assert "forbidden or unknown fields" in result["reason"]
    assert result["secret_material_recorded"] is False
    assert result["dispatch_allowed"] is False


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://athena.example/mcp",
        "https://athena.example/not-mcp",
        "https://user:password@athena.example/mcp",
        "https://athena.example/mcp?token=forbidden",
    ],
)
def test_noncanonical_or_secret_bearing_endpoint_is_rejected(endpoint: str) -> None:
    packet = _authorized_packet()
    packet["target"]["endpoint"] = endpoint
    result = FrozenCapsuleReplayIngress.load().inspect_authority_packet(
        json.dumps(packet)
    )

    assert result["status"] == "REJECTED_AUTHORITY_PACKET"
    assert result["endpoint_contacted"] is False
    assert result["dispatch_allowed"] is False


def test_lineage_and_witness_plan_cannot_be_weakened() -> None:
    registry = FrozenCapsuleReplayIngress.load()

    bad_lineage = _authorized_packet()
    bad_lineage["runtime_p09_head"] = "0" * 40
    assert registry.inspect_authority_packet(json.dumps(bad_lineage))["status"] == (
        "REJECTED_AUTHORITY_PACKET"
    )

    bad_plan = _authorized_packet()
    bad_plan["witness"]["minimum_span_seconds"] = 39
    assert registry.inspect_authority_packet(json.dumps(bad_plan))["status"] == (
        "REJECTED_AUTHORITY_PACKET"
    )


def test_w15_receipt_preserves_replay_and_ingress_boundaries() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    replay = receipt["capsule_blind_replay"]
    ingress = receipt["authority_packet_ingress"]
    boundaries = receipt["boundaries"]

    assert receipt["verdict"] == (
        "PASS_OPAQUE_CAPSULE_REPLAY_2_OF_2__"
        "PASS_STRUCTURAL_INGRESS_AUTHORITY_UNVERIFIED"
    )
    assert replay["passed"] == 2
    assert replay["failed"] == 0
    assert replay["input_fields"] == ["capsule_id"]
    assert replay["internal_recall_claimed"] is False
    assert ingress["submitted_packets_persisted"] is False
    assert ingress["external_authority_verified"] is False
    assert ingress["secret_value_accepted"] is False
    assert ingress["endpoint_contacted"] is False
    assert ingress["dispatch_allowed"] is False
    assert boundaries["no_secret_material_recorded"] is True
    assert boundaries["no_external_endpoint_contact"] is True
    assert boundaries["no_merge"] is True
    assert boundaries["no_deployment"] is True
    assert boundaries["no_promotion"] is True
