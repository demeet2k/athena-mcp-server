"""Contract tests for the W14 cross-repository return closure."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / ".athena" / "receipts" / "w14-control-return-closure.json"


def _receipt() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_return_closure_pins_both_immutable_occurrences() -> None:
    receipt = _receipt()
    runtime = receipt["runtime_content_occurrence"]
    control = receipt["control_admission_occurrence"]

    assert runtime["content_head"] == "43d80149b16f9354ba295e09130a83aaeda85203"
    assert runtime["capsule_blob_sha"] == "e69f789cb185305961ff845b6bbcedaabf936b6b"
    assert control["head"] == "59176453d005e32888b399ce61048e3c44a1dd28"
    assert control["receipt_blob_sha"] == "f1a20a7c76d1b9985f56220d7ccf7145b0121a20"


def test_closure_is_append_only_not_a_false_fixed_point() -> None:
    route = _receipt()["route"]

    assert route["runtime_content_rewritten"] is False
    assert route["control_admission_rewritten"] is False
    assert route["final_mutual_commit_fixed_point_claimed"] is False
    assert route["no_self_referential_commit_claim"] is True


def test_all_unwitnessed_boundaries_remain_held() -> None:
    receipt = _receipt()
    unresolved = receipt["unresolved"]
    authority = receipt["authority"]

    assert unresolved["runtime_exact_head_hosted_runs_observed"] is False
    assert unresolved["control_exact_head_hosted_runs_observed"] is False
    assert unresolved["endpoint_authority_inputs_unresolved"] == 13
    assert unresolved["activation_packet"] == "UNRESOLVED"
    assert unresolved["endpoint_contacted"] is False
    assert unresolved["persistent_witness_executed"] is False
    assert authority["secret_recorded"] is False
    assert authority["merge_claimed"] is False
    assert authority["deployment_claimed"] is False
    assert authority["promotion_claimed"] is False
