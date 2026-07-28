"""Fail-closed contract tests for KC144.XNAV.W16."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "MCP"))

from crystal_108d.capsule_index_repair import (  # noqa: E402
    CapsuleIndexRepairError,
    FrozenReplayLedger,
)


F07_CAPSULE = (
    "mcap:sha256:"
    "8797b945fb1ba77897f7b29076282c222a3e792122575d3562bb332a70c5fc3a"
)
M09_RID = "rid:kc144:gid141:m09:path-signature"
RECEIPT_PATH = (
    REPO_ROOT
    / ".athena"
    / "receipts"
    / "w16-capsule-index-repair-authorized-witness-ingress.json"
)


def test_replay_ledger_preserves_distinct_measurements() -> None:
    status = FrozenReplayLedger.load().status()
    events = {event["event_id"]: event for event in status["events"]}

    assert status["status"] == (
        "PASS_CAPSULE_INDEX_REPAIRED_REPLAY_LANES_TYPED_"
        "AUTHORITY_UNVERIFIED"
    )
    assert status["ledger_digest"] == (
        "sha256:5e95cfc3abc537b7108451c38c90cf9a"
        "4d99e39068e72c818343a4224fac2a35"
    )
    assert status["capsule_set_digest"] == (
        "sha256:9b4133f88aa397823eac35a143da9f12"
        "b38a09e38142a49ba48426687244c31f"
    )

    historical = events["W14-HISTORICAL-MEASUREMENT"]
    assert historical["conversation_memory_exact_fields"] == 10
    assert historical["persisted_file_memory_exact_fields"] == 12
    assert historical["external_capsule_exact_fields"] == 14
    assert historical["rewritten"] is False

    uncued = events["W15-UNCUED-CONTEXT-REPLAY"]
    assert uncued["conversation_memory_exact_fields"] == 0
    assert uncued["persisted_file_memory_exact_fields"] == 10
    assert uncued["external_capsule_exact_fields"] == 14
    assert uncued["verdict"] == "HOLD_UNCUED_FULL_PACKET_NOT_RECOVERED"
    assert uncued["rewritten"] is False

    opaque = events["W15-OPAQUE-CAPSULE-REPLAY"]
    assert opaque["input_fields"] == ["capsule_id"]
    assert opaque["challenge_count"] == 2
    assert opaque["passed"] == 2
    assert opaque["failed"] == 0
    assert opaque["internal_recall_claimed"] is False


def test_capsule_index_repairs_exact_packet_without_memory_inflation() -> None:
    result = FrozenReplayLedger.load().resolve(F07_CAPSULE)

    assert result["status"] == "PASS_W16_EXTERNAL_CAPSULE_INDEX_REPAIR"
    assert result["exact_packet_reconstructed"] is True
    assert result["index_entry"]["station"] == "F07"
    assert result["index_entry"]["rid"] == (
        "rid:kc144:gid050:f07:analytic-branch-cover"
    )
    assert result["index_entry"]["tab_id"] == "t.0"
    assert result["packet"]["source"]["range"] == {
        "start": 48973,
        "end": 48998,
        "interval": "half-open",
    }
    assert result["conversation_memory_measurement_rewritten"] is False
    assert result["persisted_file_memory_measurement_rewritten"] is False
    assert result["internal_recall_claimed"] is False
    assert result["live_provider_read"] is False


def test_reverse_exact_index_keys_route_to_same_capsule() -> None:
    registry = FrozenReplayLedger.load()
    by_rid = registry.resolve(M09_RID)
    by_station = registry.resolve("M09")
    by_aid = registry.resolve("KC144.V1::GID141::M09::PATH_SIGNATURE")

    for result in (by_rid, by_station, by_aid):
        assert result["status"] == "PASS_W16_EXTERNAL_CAPSULE_INDEX_REPAIR"
        assert result["index_entry"]["capsule_id"].endswith(
            "d89fbf78b35777cc55b1ad0e3518f186"
            "8cc2d4cce6ab78b62747b2291f9dfb0b"
        )
        assert result["packet"]["rid"] == M09_RID


def test_fuzzy_or_unknown_index_key_fails_closed() -> None:
    result = FrozenReplayLedger.load().resolve("M09-ish")

    assert result["status"] == "INVALID_W16_CAPSULE_INDEX_ADDRESS"
    assert result["fuzzy_substitution_used"] is False
    assert result["accepted_coordinate_classes"] == [
        "capsule_id",
        "station",
        "RID",
        "AID",
    ]


def test_index_repair_targets_only_the_four_missing_file_replay_fields() -> None:
    repair = FrozenReplayLedger.load().status()["index_repair"]

    assert repair["missing_fields_observed_in_w15_persisted_file_replay"] == [
        "F07.rid",
        "F07.tab_id",
        "M09.rid",
        "M09.tab_id",
    ]
    assert repair["exact_fields_reconstructed_total"] == 14
    assert repair["conversation_memory_measurement_rewritten"] is False
    assert repair["persisted_file_memory_measurement_rewritten"] is False
    assert repair["repair_is_internal_recall"] is False
    assert repair["repair_is_live_provider_read"] is False


def test_authorized_witness_ingress_remains_structural_only() -> None:
    status = FrozenReplayLedger.load().authority_status()

    assert status["status"] == (
        "READY_STRUCTURAL_INGRESS_AUTHORITY_UNVERIFIED"
    )
    assert status["canonical_activation_head"] == (
        "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
    )
    assert status["protected_environment"] == "p10-persistent-host"
    assert status["protected_secret_name"] == "ATHENA_MCP_BEARER_TOKEN"
    assert status["authority_inputs_unresolved"] == 13
    assert status["packet_storage"] == "NONE"
    assert status["network_capability"] == "NONE"
    assert status["dispatch_capability"] == "NONE"
    assert status["external_authority_verified"] is False
    assert status["endpoint_contacted"] is False
    assert status["persistent_witness_executed"] is False
    assert status["runtime_can_promote"] is False


def test_ledger_digest_tampering_is_rejected(tmp_path: Path) -> None:
    snapshot = deepcopy(FrozenReplayLedger.load().snapshot)
    snapshot["replay_ledger"][1]["conversation_memory_exact_fields"] = 14
    path = tmp_path / "tampered-ledger.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(CapsuleIndexRepairError):
        FrozenReplayLedger.load(path)


def test_w16_receipt_preserves_authority_and_lineage_boundaries() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    boundaries = receipt["boundaries"]

    assert receipt["verdict"] == (
        "PASS_CAPSULE_INDEX_REPAIRED__PASS_REPLAY_LANES_TYPED__"
        "READY_STRUCTURAL_INGRESS_AUTHORITY_UNVERIFIED"
    )
    assert receipt["measurements"]["w15_uncued"] == {
        "conversation_memory_exact_fields": 0,
        "persisted_file_memory_exact_fields": 10,
        "external_capsule_exact_fields": 14,
    }
    assert receipt["opaque_replay"]["passed"] == 2
    assert receipt["opaque_replay"]["failed"] == 0
    assert receipt["authority_ingress"]["authority_inputs_unresolved"] == 13
    assert receipt["authority_ingress"]["external_authority_verified"] is False
    assert boundaries["no_measurement_collapse"] is True
    assert boundaries["no_internal_recall_claim"] is True
    assert boundaries["no_endpoint_contact"] is True
    assert boundaries["no_merge"] is True
    assert boundaries["no_deployment"] is True
    assert boundaries["no_promotion"] is True
