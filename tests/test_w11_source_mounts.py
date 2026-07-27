"""Contract tests for KC144.XNAV.W11 frozen source-mount consumption."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "MCP"))

from crystal_108d.source_mounts import FrozenSourceMounts  # noqa: E402


F07_RID = "rid:kc144:gid050:f07:analytic-branch-cover"
M09_RID = "rid:kc144:gid141:m09:path-signature"


def test_snapshot_is_ready_but_not_live_verified() -> None:
    status = FrozenSourceMounts.load().status()

    assert status["status"] == "READY_FROZEN_NOT_LIVE_VERIFIED"
    assert status["mount_count"] == 2
    assert status["rids"] == [F07_RID, M09_RID]
    assert status["control"]["commit"] == (
        "bb611ff94134dd630e3471a0eff29dd6d79b3288"
    )
    assert status["runtime_base"]["commit"] == (
        "9731b24c5963b75821b381b4562aa51baa55196c"
    )
    assert status["runtime_base"]["published_oci_changed"] is False


def test_each_literal_matches_its_declared_digest() -> None:
    registry = FrozenSourceMounts.load()

    for mount in registry.by_rid.values():
        source = mount["source"]
        actual = sha256(source["literal"].encode("utf-8")).hexdigest()
        assert actual == source["literal_sha256"]


def test_f07_resolves_exact_git_and_docs_coordinates() -> None:
    registry = FrozenSourceMounts.load()
    resolved = registry.resolve(
        "KC144.V1::GID050::F07::ANALYTIC_BRANCH_COVER"
    )
    returned = registry.return_to_source(F07_RID)

    assert resolved["status"] == "RESOLVED_FROZEN_SOURCE_MOUNT"
    assert resolved["rid"] == F07_RID
    assert resolved["control_object"]["blob_sha"] == (
        "d1c79fb80bda9a5343be8c5593ae5f6d3fbb0630"
    )
    assert returned["status"] == "SOURCE_OCCURRENCE_RESOLVED"
    assert returned["revision_id"] == "34"
    assert returned["tab_id"] == "t.0"
    assert returned["range"] == {
        "start": 48973,
        "end": 48998,
        "interval": "half-open",
    }
    assert returned["literal"] == "FORWARD_ADDR::⟨0,s₂,[β₁]⟩"
    assert returned["return_grade"] == "R3-protocol"
    assert returned["live_provider_checked"] is False


def test_m09_preserves_semantic_equivalence_without_route_collapse() -> None:
    resolved = FrozenSourceMounts.load().resolve(M09_RID)
    route = resolved["route_identity"]

    assert route["semantic_equivalence"] is True
    assert route["route_equivalence"] is False
    assert route["exact_trace_replay"] is False
    assert route["return_mode"] == "candidate-set"
    assert route["return_unique"] is False
    assert route["route_fingerprints"]["W02"] != route["route_fingerprints"]["W03"]


def test_unknown_coordinate_is_rejected_without_fuzzy_substitution() -> None:
    registry = FrozenSourceMounts.load()

    assert registry.resolve("F07-ish") == {
        "status": "INVALID_ADDRESS",
        "identifier": "F07-ish",
        "accepted_coordinate_classes": ["RID", "AID"],
    }
    assert registry.return_to_source("M09-ish")["status"] == "INVALID_ADDRESS"


def test_claim_boundaries_remain_closed() -> None:
    boundaries = FrozenSourceMounts.load().status()["boundaries"]

    assert boundaries["raw_docs_body_committed"] is False
    assert boundaries["live_provider_checked_by_runtime"] is False
    assert boundaries["internal_cold_replay_claimed"] is False
    assert boundaries["persistent_deployment_claimed"] is False
    assert boundaries["promotion_claimed"] is False
    assert boundaries["hidden_weights_inspected"] is False
