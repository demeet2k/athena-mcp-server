"""Pure attempt-identity envelope for Campaign V3 Life Loop packets.

This module does not own Life Loop state or classify play outcomes. It only binds a
validated life-aware quest packet to a host-observed execution-event identity so an
actual play can keep one stable attempt_id across transport retries.

The canonical merged semantic base and any newer unmerged semantic-replay candidate
are recorded separately. Runtime identity metadata never promotes a candidate Life
reducer and never substitutes for external semantic Life resolution.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from .campaign_v3_life_binding import (
    ARTIFACT as QUEST_PACKET_ARTIFACT,
    validate_campaign_v3_life_quest_packet,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.ATTEMPT.IDENTITY.V1"

SEMANTIC_BASE = {
    "repo": "demeet2k/Athena",
    "commit": "60a7bc798412088977d7ab9adf16a0e7dca3a1c9",
    "script_blob": "c6f35cf39d9f25333ee0c748b5e4bacedbb544a1",
    "schema_blob": "93212c61e341ec474332c4daa36e776f735d2491",
    "registry_blob": "375c51fa362a110100568a1e0e8d47a279c1b928",
    "standing": "CANDIDATE_HARDENED_EXACT_SOURCE_TESTED",
    "exact_source_local_tests": "16/16 PASS",
    "github_actions_ci": False,
    "independent_witness": False,
}

# Compatibility name retained for existing consumers. The object now records the
# successor semantic-execution replay candidate rather than the superseded #291
# attempt-alias-only candidate.
ATTEMPT_REPLAY_EXTENSION = {
    "kind": "SEMANTIC_EXECUTION_REPLAY_V2",
    "repo": "demeet2k/Athena",
    "pull_request": 315,
    "supersedes_pull_request": 291,
    "branch": "agent/life-loop-semantic-replay-v2",
    "branch_head_at_binding": "97ebac3d47b607a43eb31fda372afbe10a0ddfdc",
    "base_head": "9aeddf08bf3d73e35ba0a67107e4c420e83aa416",
    "canonical_reseed_blob": "8eb274cc8d7f966e8778da5677fa0207233ae39b",
    "life_script_blob": "0e07e4e5a3cdf4be05fa189909c95c54f32aece4",
    "life_schema_blob": "585a08c57ca1f20cd301d32d8fa9dd6c5eee77b7",
    "life_test_blob": "88c408ba294158bf548337a677e6f471b6c56814",
    "dispatch_script_blob": "8ec6b38f2c441efce21ea636db15ce3b78fcbdab",
    "dispatch_schema_blob": "b1736e7e157e23daf2ae9919efe4bebf8e35f10d",
    "dispatch_test_blob": "69e8e92788d366b9071aa2360bc77bbbc021986c",
    "standing": "CANDIDATE_SEMANTIC_REPLAY_EXACT_SOURCE_TESTED",
    "life_exact_source_local_tests": "23/23 PASS",
    "dispatch_exact_source_local_tests": "23/23 PASS",
    "combined_exact_source_local_tests": "46/46 PASS",
    "github_actions_ci": False,
    "independent_witness": False,
    "performance_effect": "UNKNOWN",
    "canonical_promotion": False,
    "semantic_base_commit_remains_canonical": True,
}

IDENTITY_POLICY = {
    "attempt_id_required_at_play": True,
    "identity_source": "HOST_OBSERVED_EXECUTION_EVENT_ID",
    "stable_across_transport_retry": True,
    "delivery_id_participates_in_attempt_identity": False,
    "new_actual_play_requires_new_execution_event_id": True,
    "runtime_may_not_infer_new_play_from_delivery_retry": True,
    "execution_event_id_forwarded_unchanged_to_semantic_reducer": True,
    "attempt_id_is_settlement_identity": True,
    "semantic_replay_decision_owned_by_runtime": False,
    "attempt_id_grants_execution_authority": False,
    "attempt_id_grants_reward_authority": False,
    "attempt_id_grants_reseed_authority": False,
    "platform_counter_reset_claimed": False,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def derive_attempt_id(*, packet_digest: str, execution_event_id: str) -> str:
    packet_digest = str(packet_digest or "").strip()
    execution_event_id = str(execution_event_id or "").strip()
    if not packet_digest:
        raise ValueError("packet_digest required")
    if not execution_event_id:
        raise ValueError("execution_event_id required")
    return "LIFE-ATTEMPT-" + _sha(
        {
            "artifact": ARTIFACT,
            "packet_digest": packet_digest,
            "execution_event_id": execution_event_id,
        }
    )


def bind_campaign_v3_life_attempt_identity(
    *,
    packet: Mapping[str, Any],
    execution_event_id: str,
    delivery_id: str | None = None,
) -> dict[str, Any]:
    """Bind one validated quest packet to a host execution-event identity.

    `delivery_id` is transport metadata only. Multiple deliveries of the same host
    execution event intentionally produce the same `attempt_id`; a genuinely new
    played attempt must arrive with a distinct host `execution_event_id`.
    """
    packet_errors = validate_campaign_v3_life_quest_packet(packet)
    if packet_errors:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_INVALID_LIFE_QUEST_PACKET",
            "errors": list(packet_errors),
            "attempt_id": None,
            "execution_authority": False,
            "reward_authority": False,
            "reseed_authority": False,
            "platform_counter_reset_claimed": False,
        }

    event_id = str(execution_event_id or "").strip()
    if not event_id:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_EXECUTION_EVENT_ID_REQUIRED",
            "errors": ["execution_event_id_required"],
            "packet_digest": packet.get("packet_digest"),
            "attempt_id": None,
            "execution_authority": False,
            "reward_authority": False,
            "reseed_authority": False,
            "platform_counter_reset_claimed": False,
        }

    packet_digest = str(packet.get("packet_digest") or "")
    attempt_id = derive_attempt_id(
        packet_digest=packet_digest,
        execution_event_id=event_id,
    )
    normalized_delivery = str(delivery_id or "").strip() or None
    envelope: dict[str, Any] = {
        "artifact": ARTIFACT,
        "status": "BOUND_ATTEMPT_IDENTITY",
        "quest_packet_artifact": QUEST_PACKET_ARTIFACT,
        "packet_digest": packet_digest,
        "attempt_id": attempt_id,
        "execution_event_id": event_id,
        "delivery_id": normalized_delivery,
        "identity_policy": deepcopy(IDENTITY_POLICY),
        "semantic_base": deepcopy(SEMANTIC_BASE),
        "attempt_replay_extension": deepcopy(ATTEMPT_REPLAY_EXTENSION),
        "work_executed": False,
        "execution_authority": False,
        "reward_authority": False,
        "reseed_authority": False,
        "platform_counter_reset_claimed": False,
        "firewalls": [
            "DELIVERY_ID != ATTEMPT_ID",
            "RETRY_DELIVERY != NEW_PLAY",
            "ATTEMPT_ID != EXECUTION_EVENT_ID",
            "ATTEMPT_ID != EXECUTION_AUTHORITY",
            "ATTEMPT_ID != REWARD_AUTHORITY",
            "ATTEMPT_ID != RESEED_AUTHORITY",
            "RUNTIME_IDENTITY != SEMANTIC_REPLAY_DECISION",
            "CANDIDATE_EXTENSION != CANONICAL_PROMOTION",
        ],
    }
    envelope["envelope_digest"] = _sha(
        {key: value for key, value in envelope.items() if key != "envelope_digest"}
    )
    return envelope


def validate_campaign_v3_life_attempt_identity(envelope: Mapping[str, Any]) -> list[str]:
    if not isinstance(envelope, Mapping):
        return ["envelope_not_object"]
    errors: list[str] = []
    if envelope.get("artifact") != ARTIFACT:
        errors.append("artifact")
    if envelope.get("status") != "BOUND_ATTEMPT_IDENTITY":
        errors.append("status")
    packet_digest = str(envelope.get("packet_digest") or "")
    event_id = str(envelope.get("execution_event_id") or "")
    if not packet_digest:
        errors.append("packet_digest")
    if not event_id:
        errors.append("execution_event_id")
    if packet_digest and event_id:
        expected_attempt_id = derive_attempt_id(
            packet_digest=packet_digest,
            execution_event_id=event_id,
        )
        if envelope.get("attempt_id") != expected_attempt_id:
            errors.append("attempt_id")
    for key in ("work_executed", "execution_authority", "reward_authority", "reseed_authority"):
        if envelope.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    if envelope.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed_must_be_false")

    base = envelope.get("semantic_base")
    if not isinstance(base, Mapping) or base.get("commit") != SEMANTIC_BASE["commit"]:
        errors.append("semantic_base")

    extension = envelope.get("attempt_replay_extension")
    if not isinstance(extension, Mapping):
        errors.append("semantic_replay_extension")
    else:
        if extension.get("kind") != "SEMANTIC_EXECUTION_REPLAY_V2":
            errors.append("semantic_replay_extension_kind")
        if extension.get("pull_request") != 315:
            errors.append("semantic_replay_extension_stale_pr")
        if extension.get("branch_head_at_binding") != ATTEMPT_REPLAY_EXTENSION["branch_head_at_binding"]:
            errors.append("semantic_replay_extension_head")
        if extension.get("canonical_promotion") is not False:
            errors.append("candidate_extension_promotion_firewall")
        if extension.get("semantic_base_commit_remains_canonical") is not True:
            errors.append("semantic_base_promotion_firewall")

    policy = envelope.get("identity_policy")
    if not isinstance(policy, Mapping):
        errors.append("identity_policy")
    else:
        if policy.get("execution_event_id_forwarded_unchanged_to_semantic_reducer") is not True:
            errors.append("execution_event_forwarding_firewall")
        if policy.get("semantic_replay_decision_owned_by_runtime") is not False:
            errors.append("semantic_replay_ownership_firewall")

    digest = str(envelope.get("envelope_digest") or "")
    expected_digest = _sha(
        {key: value for key, value in envelope.items() if key != "envelope_digest"}
    )
    if not digest or digest != expected_digest:
        errors.append("envelope_digest")
    return errors


def verify_campaign_v3_life_attempt_identity(envelope: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_attempt_identity(envelope)
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.ATTEMPT.IDENTITY.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "attempt_id": envelope.get("attempt_id") if isinstance(envelope, Mapping) else None,
        "errors": errors,
        "execution_authority": False,
        "reward_authority": False,
        "reseed_authority": False,
        "platform_counter_reset_claimed": False,
    }
