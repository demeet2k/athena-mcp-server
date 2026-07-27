"""Tests for W15 capsule-to-hardened-endpoint binding reconciliation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "MCP" / "data" / "w14_memory_digest_capsules.json"
RECEIPT = ROOT / ".athena" / "receipts" / "w15-endpoint-binding-reconciliation.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_live_binding_points_to_deep_hardened_activation_occurrence() -> None:
    data = _load(DATA)
    binding = data["endpoint_binding"]
    handoff = binding["canonical_activation_handoff"]
    assert handoff["head"] == "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
    assert handoff["deep_hardening_receipt_blob"] == "8a1c60bb994c049978fde7e9db35a8f9096db57a"
    assert binding["protected_secret_name"] == "ATHENA_MCP_BEARER_TOKEN"
    assert binding["deep_hardening_verdict"] == "READY_AWAITING_AUTHORIZED_TARGET"


def test_capsule_digest_is_unchanged_by_binding_metadata_repair() -> None:
    data = _load(DATA)
    receipt = _load(RECEIPT)
    expected = "sha256:9b4133f88aa397823eac35a143da9f12b38a09e38142a49ba48426687244c31f"
    assert data["capsule_set_digest"] == expected
    assert receipt["reconciled_live_binding"]["capsule_set_digest"] == expected
    assert receipt["reconciled_live_binding"]["capsule_set_digest_changed"] is False
    assert receipt["historical_w14"]["rewritten"] is False


def test_authority_boundary_remains_unresolved() -> None:
    authority = _load(RECEIPT)["authority"]
    assert authority["activation_packet"] == "UNRESOLVED"
    assert authority["authority_inputs_unresolved"] == 13
    assert authority["endpoint_contacted"] is False
    assert authority["persistent_witness_executed"] is False
    assert authority["secret_recorded"] is False
    assert authority["deployment_claimed"] is False
    assert authority["merge_claimed"] is False
    assert authority["promotion_claimed"] is False
