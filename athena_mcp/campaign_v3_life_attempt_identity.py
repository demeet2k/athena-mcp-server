"""Pure attempt-identity envelope for Campaign V3 Life Loop packets.

This module does not own Life Loop state or classify play outcomes. It only binds a
validated life-aware quest packet to a host-observed execution-event identity so an
actual play can keep one stable attempt_id across transport retries.

The host-event identity membrane is deliberately weaker than canonical semantic
replay identity. Cross-repo semantic replay compatibility remains an explicit HOLD
until Athena's canonical Life/Quest Dispatch layer resolves alias replay,
play-vs-continuation settlement, and attempt-id forwarding.
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
    "standing": "MERGED_HARDENED_LIFE_LOOP_BASE",
    "exact_source_local_tests": "16/16 PASS",
    "github_actions_ci": False,
    "independent_witness": False,
}

ATTEMPT_REPLAY_EXTENSION = {
    "repo": "demeet2k/Athena",
    "pull_request": 291,
    "branch": "agent/life-loop-replay-hardening-v1",
    "observed_head": "f0d2efb9a0bdc999ae7aef93041cf8e69f4eb51e",
    "observed_against_athena_main": "9aeddf08bf3d73e35ba0a67107e4c420e83aa416",
    "candidate_base_sha": "60a7bc798412088977d7ab9adf16a0e7dca3a1c9",
    "status": "INTEGRATION_HOLD",
    "standing": "SEMANTIC_REPLAY_COMPATIBILITY_NOT_ESTABLISHED",
    "canonical_promotion": False,
    "semantic_replay_compatibility": False,
    "host_execution_identity_only": True,
    "candidate_diverged_from_current_main_at_observation": True,
    "quest_dispatch_attempt_id_abi": "BLOCKED",
    "semantic_alias_replay_safety": "UNRESOLVED",
    "continuation_settlement": "UNRESOLVED",
    "blockers": [
        "SEMANTIC_ALIAS_REPLAY_UNRESOLVED",
        "PLAY_SETTLEMENT_CONTINUATION_SETTLEMENT_UNRESOLVED",
        "QUEST_DISPATCH_ATTEMPT_ID_NOT_IN_ABI",
        "CANDIDATE_REBASE_ON_CURRENT_MAIN_REQUIRED",
    ],
    "historical_candidate_evidence": {
        "head": "6e96348ad5a8adfe7f111695d9ed6ec168f43bfb",
        "local_composed_tests": "20/20 PASS",
        "scope": "SUPERSEDED_CANDIDATE_SNAPSHOT_NOT_SEMANTIC_COMPATIBILITY_EVIDENCE",
    },
}

REQUIRED_REPLAY_BLOCKERS = frozenset(ATTEMPT_REPLAY_EXTENSION["blockers"])

IDENTITY_POLICY = {
    "attempt_id_required_at_play": True,
    "identity_source": "HOST_OBSERVED_EXECUTION_EVENT_ID",
    "stable_across_transport_retry": True,
    "delivery_id_participates_in_attempt_identity": False,
    "new_actual_play_requires_new_execution_event_id": True,
    "runtime_may_not_infer_new_play_from_delivery_retry": True,
    "host_event_identity_is_canonical_semantic_execution_identity": False,
    "semantic_alias_replay_safety_established": False,
    "continuation_retry_settlement_established": False,
    "quest_dispatch_attempt_id_abi_established": False,
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
    host-observed play must arrive with a distinct host `execution_event_id`.

    This does not establish canonical semantic-execution equivalence. The embedded
    replay standing remains fail-closed while Athena's semantic replay candidate is
    unresolved.
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
            "HOST_EVENT_IDENTITY != CANONICAL_SEMANTIC_EXECUTION_IDENTITY",
            "INTEGRATION_HOLD != SEMANTIC_REPLAY_SAFETY",
            "PLAY_SETTLEMENT != CONTINUATION_SETTLEMENT_COMPATIBILITY_PROOF",
            "ATTEMPT_ID != EXECUTION_AUTHORITY",
            "ATTEMPT_ID != REWARD_AUTHORITY",
            "ATTEMPT_ID != RESEED_AUTHORITY",
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

    policy = envelope.get("identity_policy")
    if not isinstance(policy, Mapping):
        errors.append("identity_policy")
    else:
        for key in (
            "host_event_identity_is_canonical_semantic_execution_identity",
            "semantic_alias_replay_safety_established",
            "continuation_retry_settlement_established",
            "quest_dispatch_attempt_id_abi_established",
        ):
            if policy.get(key) is not False:
                errors.append(f"identity_policy_{key}_must_be_false")

    extension = envelope.get("attempt_replay_extension")
    if not isinstance(extension, Mapping):
        errors.append("attempt_replay_extension")
    else:
        if extension.get("canonical_promotion") is not False:
            errors.append("candidate_extension_promotion_firewall")
        if extension.get("semantic_replay_compatibility") is not False:
            errors.append("semantic_replay_compatibility_must_be_false")
        if extension.get("status") != "INTEGRATION_HOLD":
            errors.append("semantic_replay_compatibility_hold")
        if extension.get("standing") != "SEMANTIC_REPLAY_COMPATIBILITY_NOT_ESTABLISHED":
            errors.append("semantic_replay_standing")
        blockers = extension.get("blockers")
        if not isinstance(blockers, list) or not REQUIRED_REPLAY_BLOCKERS.issubset(set(blockers)):
            errors.append("semantic_replay_blockers")

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
        "semantic_replay_compatibility": False,
        "execution_authority": False,
        "reward_authority": False,
        "reseed_authority": False,
        "platform_counter_reset_claimed": False,
    }
