"""Contract tests for KC144.XNAV.W14 memory digest capsules."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "MCP"))

from crystal_108d.memory_digest_capsules import (  # noqa: E402
    FrozenMemoryDigestCapsules,
    MemoryDigestCapsuleError,
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
    / "w14-memory-digest-capsule-endpoint-binding.json"
)


def test_capsule_status_preserves_measured_memory_boundary() -> None:
    status = FrozenMemoryDigestCapsules.load().status()
    measurement = status["memory_measurement"]

    assert status["status"] == (
        "READY_CAPSULE_ASSISTED_PACKET_COMPLETE_ENDPOINT_AUTHORITY_PENDING"
    )
    assert status["capsule_count"] == 2
    assert status["stations"] == ["F07", "M09"]
    assert status["capsule_set_digest"] == (
        "sha256:9b4133f88aa397823eac35a143da9f12"
        "b38a09e38142a49ba48426687244c31f"
    )
    assert measurement["conversation_memory_exact_field_count"] == 10
    assert measurement["persisted_file_memory_exact_field_count"] == 12
    assert measurement["capsule_assisted_exact_field_count"] == 14
    assert measurement["capsule_assisted_exact_recovery_ratio"] == 1.0
    assert measurement["capsule_assisted_is_internal_recall"] is False
    assert measurement["capsule_assisted_is_live_provider_read"] is False


def test_f07_capsule_resolves_complete_exact_coordinate() -> None:
    resolved = FrozenMemoryDigestCapsules.load().resolve("F07")
    source = resolved["source"]

    assert resolved["status"] == "RESOLVED_EXTERNAL_MEMORY_DIGEST_CAPSULE"
    assert resolved["capsule_id"] == F07_CAPSULE
    assert resolved["rid"] == "rid:kc144:gid050:f07:analytic-branch-cover"
    assert source["file_id"] == (
        "1fWBHqWuFXHucyHxnTobngr3vmaWkRmlP-zyn7jOm3_w"
    )
    assert source["revision_id"] == "34"
    assert source["tab_id"] == "t.0"
    assert source["range"] == {
        "start": 48973,
        "end": 48998,
        "interval": "half-open",
    }
    assert source["literal"] == "FORWARD_ADDR::⟨0,s₂,[β₁]⟩"
    assert source["literal_sha256"] == (
        "9ff39e3f43c43e077fff00ef05fb40da"
        "64440a4af49eeb83f63011cd10b15939"
    )
    assert resolved["packet_fields_completed"] == 14
    assert resolved["capsule_assisted_is_internal_recall"] is False


def test_m09_capsule_resolves_complete_exact_coordinate() -> None:
    registry = FrozenMemoryDigestCapsules.load()
    resolved = registry.resolve("KC144.V1::GID141::M09::PATH_SIGNATURE")

    assert resolved["capsule_id"] == M09_CAPSULE
    assert resolved["rid"] == "rid:kc144:gid141:m09:path-signature"
    assert resolved["source"]["revision_id"] == "92"
    assert resolved["source"]["range"] == {
        "start": 366356,
        "end": 366385,
        "interval": "half-open",
    }
    assert resolved["source"]["literal"] == "A hidden hash is insufficient"
    assert resolved["source"]["literal_sha256"] == (
        "b2dbee4215f51bcf76d251a49bbf150b"
        "fd6125f52b3e49c41303d7fb41e73b80"
    )


def test_each_capsule_recomputes_literal_capsule_and_set_digests() -> None:
    registry = FrozenMemoryDigestCapsules.load()

    for capsule_id in (F07_CAPSULE, M09_CAPSULE):
        result = registry.verify(capsule_id)
        assert result["status"] == "PASS_CAPSULE_VERIFIED"
        assert result["literal_digest_verified"] is True
        assert result["capsule_digest_verified"] is True
        assert result["capsule_set_digest_verified"] is True
        assert result["verified"] is True
        assert result["internal_recall_claimed"] is False
        assert result["live_provider_checked"] is False


def test_literal_tampering_is_rejected(tmp_path: Path) -> None:
    snapshot = deepcopy(FrozenMemoryDigestCapsules.load().snapshot)
    snapshot["capsules"][0]["source"]["literal"] += "!"
    path = tmp_path / "tampered-literal.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(MemoryDigestCapsuleError, match="literal digest mismatch"):
        FrozenMemoryDigestCapsules.load(path)


def test_capsule_id_tampering_is_rejected(tmp_path: Path) -> None:
    snapshot = deepcopy(FrozenMemoryDigestCapsules.load().snapshot)
    snapshot["capsules"][1]["capsule_id"] = "mcap:sha256:" + "0" * 64
    path = tmp_path / "tampered-capsule.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(MemoryDigestCapsuleError, match="capsule digest mismatch"):
        FrozenMemoryDigestCapsules.load(path)


def test_endpoint_binding_is_ready_but_strictly_fail_closed() -> None:
    binding = FrozenMemoryDigestCapsules.load().endpoint_binding_status()

    assert binding["status"] == "ENDPOINT_BINDING_AUTHORITY_PENDING"
    assert binding["state"] == "AUTHORITY_PENDING"
    assert binding["binding_ready"] is True
    assert binding["binding_complete"] is False
    assert binding["authority_packet_digest"] is None
    assert binding["authorized_endpoint"] is None
    assert len(binding["unresolved_authority_inputs"]) == 13
    assert binding["activation_packet_compilable_now"] is False
    assert binding["dispatch_allowed"] is False
    assert binding["endpoint_contacted"] is False
    assert binding["persistent_witness_executed"] is False
    assert binding["secret_material_embedded"] is False
    assert binding["persistent_deployment_claimed"] is False
    assert binding["promotion_claimed"] is False
    assert binding["witness_plan"] == {
        "samples": 3,
        "interval_seconds": 20,
        "minimum_span_seconds": 40,
        "execute_live_witness_default": False,
    }


def test_w14_receipt_preserves_capsule_and_authority_boundaries() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    capsule = receipt["memory_digest_capsule"]
    binding = receipt["endpoint_binding"]
    boundaries = receipt["boundaries"]

    assert receipt["verdict"] == (
        "PASS_MEMORY_DIGEST_CAPSULE_COMPLETE__"
        "ENDPOINT_BINDING_READY_AUTHORITY_PENDING"
    )
    assert capsule["capsule_assisted_exact_field_count"] == 14
    assert capsule["capsule_assisted_is_internal_recall"] is False
    assert capsule["capsule_assisted_is_live_provider_read"] is False
    assert binding["authority_packet_digest"] is None
    assert binding["authorized_endpoint"] is None
    assert binding["dispatch_allowed"] is False
    assert boundaries["no_hidden_weight_claim"] is True
    assert boundaries["no_secret_material_recorded"] is True
    assert boundaries["no_external_endpoint_contact"] is True
    assert boundaries["no_merge"] is True
    assert boundaries["no_deployment"] is True
    assert boundaries["no_promotion"] is True
