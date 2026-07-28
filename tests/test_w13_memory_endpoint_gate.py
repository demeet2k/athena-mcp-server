"""Contract tests for KC144.XNAV.W13 memory and endpoint gate."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    REPO_ROOT
    / ".athena"
    / "receipts"
    / "w13-blind-memory-and-endpoint-gate.json"
)


def _receipt() -> dict:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def test_blind_probe_preserves_partial_result_without_overclaim() -> None:
    probe = _receipt()["global_memory_probe"]
    result = probe["conversation_memory_result"]

    assert probe["probe_id"] == "W13-Q0-FRAMEWORK-ONLY"
    assert probe["probe_current_conversation_access"] is False
    assert probe["target_station_labels_supplied"] is False
    assert probe["target_rids_supplied"] is False
    assert probe["target_provider_coordinates_supplied"] is False
    assert probe["target_literals_supplied"] is False
    assert probe["target_digests_supplied"] is False
    assert result["exact_field_count"] == 10
    assert result["possible_field_count"] == 14
    assert result["exact_recovery_ratio"] == 0.7142857143
    assert result["verdict"] == "PARTIAL_PACKET_RECOVERED"
    assert result["live_source_substitution_used"] is False


def test_cue_control_distinguishes_conversation_and_file_memory() -> None:
    control = _receipt()["global_memory_probe"]["cue_assisted_control"]

    assert control["supplied_cues"] == ["F07", "M09"]
    assert control["conversation_only_exact_field_count"] == 10
    assert control["conversation_only_cue_gain_fields"] == 0
    assert control["conversation_only_cue_gain_ratio"] == 0.0
    assert control["persisted_file_memory_exact_field_count"] == 12
    assert control["persisted_file_memory_gain_fields"] == 2
    assert control["persisted_file_memory_gain_ratio"] == 0.1428571428
    assert control["remaining_incomplete_fields"] == [
        "F07.full_sha256",
        "M09.full_sha256",
    ]


def test_collision_audit_rejects_unrelated_historical_coordinates() -> None:
    audit = _receipt()["global_memory_probe"]["collision_audit"]

    assert audit["unrelated_historical_coordinates_returned"] is True
    assert audit["false_leads_admitted"] is False
    assert "GID043.P10.QS1" in audit["examples"]


def test_probe_is_not_hidden_weight_or_unassisted_model_recall() -> None:
    classification = _receipt()["global_memory_probe"]["classification"]

    assert classification["cross_conversation_retrieval_demonstrated"] is True
    assert classification["exact_full_packet_reconstruction_demonstrated"] is False
    assert classification["cue_gain_in_conversation_memory_demonstrated"] is False
    assert classification["persisted_memory_augmentation_demonstrated"] is True
    assert classification["hidden_weight_recall_tested"] is False
    assert classification["hidden_weights_inspected"] is False
    assert classification["unassisted_model_cold_recall_claimed"] is False


def test_endpoint_gate_is_ready_but_authority_remains_unbound() -> None:
    gate = _receipt()["endpoint_authorization_gate"]

    assert gate["state"] == "PASS_ACTIVATION_HANDOFF_READY_AUTHORITY_PENDING"
    assert gate["canonical_runtime_pull_request"] == 11
    assert gate["head"] == "7e7df38602834e88150450ed5bdbe24b8822c2ac"
    assert gate["activation_packet_compilable_now"] is False
    assert gate["endpoint_contacted"] is False
    assert gate["persistent_witness_executed"] is False
    assert gate["persistent_deployment_claimed"] is False
    assert gate["promotion_claimed"] is False
    assert gate["ic10_required"] is True
    assert len(gate["unresolved_authority_inputs"]) == 13


def test_endpoint_plan_cannot_be_laundered_into_deployment() -> None:
    receipt = _receipt()
    plan = receipt["endpoint_authorization_gate"]["witness_plan"]
    boundaries = receipt["boundaries"]

    assert plan["protected_environment"] == "p10-persistent-host"
    assert plan["protected_secret_name"] == "ATHENA_P10_BEARER_TOKEN"
    assert plan["samples"] == 3
    assert plan["interval_seconds"] == 20
    assert plan["minimum_span_seconds"] == 40
    assert plan["execute_live_witness_default"] is False
    assert boundaries["no_secret_material_recorded"] is True
    assert boundaries["no_external_endpoint_contact"] is True
    assert boundaries["no_merge"] is True
    assert boundaries["no_deployment"] is True
    assert boundaries["no_promotion"] is True
