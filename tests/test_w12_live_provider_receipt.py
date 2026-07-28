"""Contract tests for the KC144.XNAV.W12 live-provider witness receipt."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    REPO_ROOT / ".athena" / "receipts" / "w12-live-provider-return.json"
)


def _receipt() -> dict:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def test_w12_live_provider_return_is_exact_and_drift_free() -> None:
    receipt = _receipt()

    assert receipt["schema"] == "athena.live-provider-return-witness/v1"
    assert receipt["verdict"] == "PASS_LIVE_PROVIDER_RETURN_NO_DRIFT"
    assert receipt["aggregate"]["attempted_returns"] == 2
    assert receipt["aggregate"]["exact_returns"] == 2
    assert receipt["aggregate"]["stable_coordinate_drift_count"] == 0
    assert receipt["aggregate"]["digest_mismatch_count"] == 0
    assert receipt["aggregate"]["provider_result"] == "2_OF_2_EXACT"


def test_each_return_matches_all_stable_coordinates() -> None:
    receipt = _receipt()

    assert len(receipt["returns"]) == 2
    for result in receipt["returns"]:
        assert result["file_id_match"] is True
        assert result["drive_revision_match"] is True
        assert result["tab_match"] is True
        assert result["range_match"] is True
        assert result["literal_match"] is True
        assert result["digest_match"] is True
        assert result["return_grade"] == "R3-live-provider-witness"


def test_f07_revision_token_rotation_is_not_laundered_into_content_drift() -> None:
    f07 = next(
        result
        for result in _receipt()["returns"]
        if result["rid"] == "rid:kc144:gid050:f07:analytic-branch-cover"
    )

    assert f07["expected_drive_revision_id"] == "34"
    assert f07["current_drive_revision_id"] == "34"
    assert f07["docs_api_revision_token_rotated"] is True
    assert (
        f07["previous_docs_api_revision_token"]
        != f07["current_docs_api_revision_token"]
    )
    assert f07["expected_range"] == f07["current_range"]
    assert f07["literal_sha256"] == (
        "9ff39e3f43c43e077fff00ef05fb40da"
        "64440a4af49eeb83f63011cd10b15939"
    )


def test_m09_preserves_exact_occurrence_and_digest() -> None:
    m09 = next(
        result
        for result in _receipt()["returns"]
        if result["rid"] == "rid:kc144:gid141:m09:path-signature"
    )

    assert m09["expected_drive_revision_id"] == "92"
    assert m09["current_drive_revision_id"] == "92"
    assert m09["expected_range"] == {
        "start": 366356,
        "end": 366385,
        "interval": "half-open",
    }
    assert m09["current_range"] == m09["expected_range"]
    assert m09["matched_text"] == "A hidden hash is insufficient"
    assert m09["literal_sha256"] == (
        "b2dbee4215f51bcf76d251a49bbf150b"
        "fd6125f52b3e49c41303d7fb41e73b80"
    )


def test_w12_does_not_cross_deployment_or_internal_recall_boundaries() -> None:
    boundaries = _receipt()["boundaries"]

    assert boundaries["provider_check_executed_externally_to_runtime"] is True
    assert boundaries["runtime_network_read_added"] is False
    assert boundaries["raw_docs_body_committed"] is False
    assert boundaries["internal_cold_replay_claimed"] is False
    assert boundaries["persistent_https_endpoint_claimed"] is False
    assert boundaries["persistent_deployment_claimed"] is False
    assert boundaries["promotion_claimed"] is False
    assert boundaries["published_oci_changed"] is False
    assert boundaries["hidden_weights_inspected"] is False
