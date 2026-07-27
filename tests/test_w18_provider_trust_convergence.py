"""Append-only convergence tests for both KC144.XNAV.W18 siblings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / ".athena" / "receipts" / "w18-provider-trust-convergence.json"
STATUS = ROOT / ".athena" / "status.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_both_w18_sibling_occurrences_are_preserved_in_parent_order() -> None:
    receipt = _load(RECEIPT)
    lineage = receipt["lineage"]
    assert lineage["merge_parent_order"] == [
        "49f2449e159fdef82b60722f35f302290934a468",
        "5eece82829abb7eba87943548e89b6c04179ef40",
    ]
    assert lineage["common_w17_parent"] == (
        "9ac6f97f1065280d027d13a43d8c9d68770184bd"
    )
    assert lineage["append_only"] is True
    assert lineage["sibling_rewritten"] is False
    assert receipt["sibling_hosted_evidence"]["structural_return"][
        "tests_passed"
    ] == 108
    assert receipt["sibling_hosted_evidence"]["pinned_crypto"][
        "tests_passed"
    ] == 106


def test_convergence_exposes_both_topology_and_real_crypto_without_trust_inflation() -> None:
    receipt = _load(RECEIPT)
    contract = receipt["combined_contract"]
    status = _load(STATUS)
    assert contract["structural_return_topology_ready"] is True
    assert contract["detached_signature_verifier_ready"] is True
    assert contract["production_adapter_count"] == 0
    assert contract["production_trust_anchor_count"] == 0
    assert contract["self_supplied_trust_anchors_allowed"] is False
    assert status["w18_provider_trust_convergence"][
        "structural_return_topology_ready"
    ] is True
    assert status["w18_provider_trust_convergence"][
        "detached_signature_verifier_ready"
    ] is True
    assert status["w18_provider_trust_convergence"][
        "provider_return_signature_verified"
    ] is False


def test_convergence_receipt_is_content_addressed_and_nonpromotional() -> None:
    receipt = _load(RECEIPT)
    receipt_id = receipt.pop("receipt_id")
    digest = hashlib.sha256(
        json.dumps(
            receipt,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert receipt_id == f"w18-convergence:sha256:{digest}"
    assert receipt["validation"]["registered_tools"] == 207
    assert receipt["validation"]["registered_resources"] == 37
    assert receipt["boundaries"]["production_provider_adapter_admitted"] is False
    assert receipt["boundaries"]["provider_return_signature_verified"] is False
    assert receipt["boundaries"]["workflow_dispatched"] is False
    assert receipt["boundaries"]["persistent_witness_executed"] is False
    assert receipt["boundaries"]["deployment_claimed"] is False
    assert receipt["boundaries"]["merge_claimed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
