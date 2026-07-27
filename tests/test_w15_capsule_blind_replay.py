"""Fail-closed tests for KC144.XNAV.W15 blind replay and ingress."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / ".athena" / "receipts" / "w15-capsule-blind-replay-ingress.json"


def _receipt() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_blind_replay_records_observed_failure_without_overclaim() -> None:
    replay = _receipt()["blind_replay"]
    assert replay["current_conversation_access"] is False
    assert replay["current_google_drive_search_used"] is False
    assert replay["current_github_search_used"] is False
    assert replay["possible_fields"] == 14
    assert replay["conversation_memory"]["exact_packet_fields"] == 0
    assert replay["persisted_file_memory"]["exact_packet_fields"] == 10
    assert replay["persisted_file_memory"]["missing_fields"] == [
        "F07.rid", "F07.tab_id", "M09.rid", "M09.tab_id"
    ]
    assert replay["full_packet_verdict"] == "HOLD_UNCUED_FULL_PACKET_NOT_RECOVERED"
    assert replay["hidden_weight_recall_claimed"] is False


def test_external_capsule_truth_is_distinct_from_memory_replay() -> None:
    capsule = _receipt()["external_capsule_ground_truth"]
    assert capsule["source_head"] == "deab5f44f2942326b415a50daa722ce565210540"
    assert capsule["explicit_external_packet_fields"] == 14
    assert capsule["external_packet_complete"] is True
    assert capsule["internal_recall"] is False
    assert capsule["live_provider_read_during_blind_probe"] is False


def test_both_parent_lineages_are_preserved_append_only() -> None:
    parents = _receipt()["parent_reconciliation"]
    assert parents["activation_hardening_head"] == "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
    assert parents["executable_capsule_head"] == "deab5f44f2942326b415a50daa722ce565210540"
    assert parents["prior_return_closure_head"] == "9a36bf46600f64b519c24252ec32fa078211b614"
    assert parents["deep_activation_hardening_preserved"] is True
    assert parents["source_mount_runtime_preserved"] is True
    assert parents["executable_digest_capsule_preserved"] is True
    assert parents["old_pr12_history_rewritten"] is False


def test_authorized_witness_remains_fail_closed() -> None:
    receipt = _receipt()
    endpoint = receipt["endpoint_authority"]
    authority = receipt["authority"]
    assert endpoint["verdict"] == "READY_AWAITING_AUTHORIZED_TARGET"
    assert endpoint["activation_packet"] == "UNRESOLVED"
    assert endpoint["protected_secret_name"] == "ATHENA_MCP_BEARER_TOKEN"
    assert endpoint["authority_inputs_unresolved"] == 13
    assert endpoint["persistent_witness_executed"] is False
    assert authority["secret_recorded"] is False
    assert authority["merge_claimed"] is False
    assert authority["deployment_claimed"] is False
    assert authority["promotion_claimed"] is False
