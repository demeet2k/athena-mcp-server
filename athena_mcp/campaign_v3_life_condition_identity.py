"""Pre-play clear-condition identity membrane for Campaign V3 Life packets.

The merged Campaign compiler intentionally freezes public condition definitions but
not canonical criterion IDs. This additive layer binds explicit IDs to those frozen
definitions and to the immutable compiler packet digest before semantic dispatch.
It does not execute work, observe outcomes, or grant Life/reward/reseed authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from .campaign_v3_life_binding import validate_campaign_v3_life_quest_packet
from .campaign_v3_life_dispatch_bridge import translate_campaign_v3_life_dispatch_v1

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.CONDITION.IDENTITY.V1"
DISPATCH_ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.DISPATCH.IDENTITY.BRIDGE.V1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _ids(values: Any) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("criterion_ids must be a list")
    rows: list[str] = []
    for raw in values:
        value = str(raw or "").strip()
        if not value:
            raise ValueError("criterion_ids entries must be non-empty")
        if value in rows:
            raise ValueError(f"duplicate criterion_id: {value}")
        rows.append(value)
    if not rows:
        raise ValueError("criterion_ids must be non-empty")
    return rows


def freeze_campaign_v3_life_condition_identity(
    *,
    campaign_packet: Mapping[str, Any],
    criterion_ids: Sequence[Any],
    identity_ref: str,
) -> dict[str, Any]:
    """Freeze criterion IDs against an immutable, still-unplayed Campaign packet."""
    if not isinstance(campaign_packet, Mapping):
        raise ValueError("campaign_packet must be an object")
    packet_errors = validate_campaign_v3_life_quest_packet(campaign_packet)
    if packet_errors:
        raise ValueError("invalid campaign_packet: " + ",".join(packet_errors))
    if campaign_packet.get("CLEAR_RESULT_VECTOR") is not None:
        raise ValueError("identity freeze requires unobserved CLEAR_RESULT_VECTOR")
    if campaign_packet.get("work_executed") is not False:
        raise ValueError("identity freeze requires work_executed=false")

    identity_ref = str(identity_ref or "").strip()
    if not identity_ref:
        raise ValueError("identity_ref required")
    criterion_id_rows = _ids(criterion_ids)
    definitions = campaign_packet.get("CLEAR_CONDITIONS")
    if not isinstance(definitions, list) or not definitions:
        raise ValueError("campaign packet CLEAR_CONDITIONS invalid")
    if len(criterion_id_rows) != len(definitions):
        raise ValueError("criterion_ids length must equal CLEAR_CONDITIONS length")

    pairs = [
        {"id": criterion_id, "definition": str(definition)}
        for criterion_id, definition in zip(criterion_id_rows, definitions)
    ]
    pairs.sort(key=lambda row: row["id"])
    quest = campaign_packet.get("quest") or {}
    basis = {
        "packet_digest": str(campaign_packet.get("packet_digest") or ""),
        "quest_id": str(quest.get("quest_id") or ""),
        "quest_version": str(quest.get("quest_version") or ""),
        "identity_ref": identity_ref,
        "conditions": pairs,
    }
    envelope = {
        "artifact": ARTIFACT,
        "status": "FROZEN_PREPLAY_PACKET_BOUND",
        **basis,
        "condition_identity_digest": _sha(basis),
        "outcomes_observed": False,
        "temporal_creation_proof": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
        "standing": (
            "IDENTITY_BOUND_TO_UNPLAYED_PACKET_DIGEST; CALLER_DECLARED_IDENTITY_REF; "
            "CREATION_TIME_IS_NOT_INDEPENDENTLY_PROVEN"
        ),
        "laws": [
            "CONDITION_IDENTITY != CONDITION_OUTCOME",
            "PACKET_BOUND_IDENTITY != TEMPORAL_CREATION_PROOF",
            "IDENTITY_REF != EXTERNAL_AUTHORITY_PROOF",
            "IDENTITY_FREEZE != EXECUTION_AUTHORITY",
            "LOGICAL_RESEED != PLATFORM_COUNTER_RESET",
        ],
    }
    envelope["envelope_digest"] = _sha(
        {key: value for key, value in envelope.items() if key != "envelope_digest"}
    )
    return envelope


def validate_campaign_v3_life_condition_identity(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["identity_not_object"]
    errors: list[str] = []
    if value.get("artifact") != ARTIFACT:
        errors.append("artifact")
    if value.get("status") != "FROZEN_PREPLAY_PACKET_BOUND":
        errors.append("status")
    for key in ("packet_digest", "quest_id", "quest_version", "identity_ref"):
        if not isinstance(value.get(key), str) or not value.get(key):
            errors.append(key)

    conditions = value.get("conditions")
    ids_seen: set[str] = set()
    normalized_conditions: list[dict[str, str]] = []
    if not isinstance(conditions, list) or not conditions:
        errors.append("conditions")
    else:
        for row in conditions:
            if not isinstance(row, Mapping):
                errors.append("condition_not_object")
                continue
            criterion_id = row.get("id")
            definition = row.get("definition")
            valid_id = isinstance(criterion_id, str) and bool(criterion_id)
            valid_definition = isinstance(definition, str) and bool(definition)
            if not valid_id:
                errors.append("condition_id")
            elif criterion_id in ids_seen:
                errors.append("condition_id_duplicate")
            else:
                ids_seen.add(criterion_id)
            if not valid_definition:
                errors.append("condition_definition")
            if valid_id and valid_definition:
                normalized_conditions.append(
                    {"id": str(criterion_id), "definition": str(definition)}
                )
        if len(normalized_conditions) == len(conditions):
            canonical_conditions = sorted(
                normalized_conditions, key=lambda row: row["id"]
            )
            if normalized_conditions != canonical_conditions:
                errors.append("conditions_not_canonical_order")

    basis = {
        "packet_digest": value.get("packet_digest"),
        "quest_id": value.get("quest_id"),
        "quest_version": value.get("quest_version"),
        "identity_ref": value.get("identity_ref"),
        "conditions": conditions,
    }
    if value.get("condition_identity_digest") != _sha(basis):
        errors.append("condition_identity_digest")
    if value.get("outcomes_observed") is not False:
        errors.append("outcomes_observed_must_be_false")
    if value.get("temporal_creation_proof") is not False:
        errors.append("temporal_creation_proof_must_be_false")
    for key in (
        "execution_authority",
        "life_consumption_authority",
        "reward_issuance_authority",
        "reseed_anchor_consumption_authority",
        "platform_counter_reset_claimed",
    ):
        if value.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    expected_envelope_digest = _sha(
        {key: item for key, item in value.items() if key != "envelope_digest"}
    )
    if value.get("envelope_digest") != expected_envelope_digest:
        errors.append("envelope_digest")
    return errors


def verify_campaign_v3_life_condition_identity_against_packet(
    identity: Mapping[str, Any],
    campaign_packet: Mapping[str, Any],
) -> dict[str, Any]:
    errors = validate_campaign_v3_life_condition_identity(identity)
    if not isinstance(campaign_packet, Mapping):
        errors.append("campaign_packet_not_object")
    else:
        packet_errors = validate_campaign_v3_life_quest_packet(campaign_packet)
        errors.extend(f"campaign_packet:{item}" for item in packet_errors)
        if identity.get("packet_digest") != campaign_packet.get("packet_digest"):
            errors.append("packet_digest_binding")
        quest = campaign_packet.get("quest") or {}
        if identity.get("quest_id") != quest.get("quest_id"):
            errors.append("quest_id_binding")
        if identity.get("quest_version") != quest.get("quest_version"):
            errors.append("quest_version_binding")
        definitions = campaign_packet.get("CLEAR_CONDITIONS")
        identity_definitions = sorted(
            str(row.get("definition") or "")
            for row in (identity.get("conditions") or [])
            if isinstance(row, Mapping)
        )
        if not isinstance(definitions, list) or sorted(map(str, definitions)) != identity_definitions:
            errors.append("condition_definition_binding")
        if campaign_packet.get("CLEAR_RESULT_VECTOR") is not None:
            errors.append("packet_results_already_observed")
        if campaign_packet.get("work_executed") is not False:
            errors.append("packet_work_executed")
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.CONDITION.IDENTITY.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "errors": sorted(set(errors)),
        "packet_digest": identity.get("packet_digest") if isinstance(identity, Mapping) else None,
        "identity_digest": identity.get("condition_identity_digest") if isinstance(identity, Mapping) else None,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
    }


def _observations_match_identity(
    observations: Any,
    identity: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        return ["condition_observations_not_list"]
    expected = {
        str(row.get("id")): str(row.get("definition"))
        for row in (identity.get("conditions") or [])
        if isinstance(row, Mapping)
    }
    seen: dict[str, str] = {}
    for raw in observations:
        if not isinstance(raw, Mapping):
            errors.append("condition_observation_not_object")
            continue
        criterion_id = str(raw.get("id") or "")
        definition = str(raw.get("definition") or "")
        if criterion_id in seen:
            errors.append(f"duplicate_observation_id:{criterion_id}")
        seen[criterion_id] = definition
        if type(raw.get("satisfied")) is not bool:
            errors.append(f"observation_satisfied_not_bool:{criterion_id}")
    if seen != expected:
        errors.append("observation_identity_mismatch")
    return errors


def translate_campaign_v3_life_dispatch_with_frozen_identity_v1(
    *,
    campaign_packet: Mapping[str, Any],
    condition_identity: Mapping[str, Any],
    agent_id: str,
    condition_observations: Sequence[Mapping[str, Any]],
    result_class: str,
    executed: bool | None = None,
    hard_gate_status: str | None = None,
    witnesses: Sequence[Any] | None = None,
    current_git_positions: Sequence[Mapping[str, Any]] | None = None,
    extra_life_reward: Mapping[str, Any] | None = None,
    attempt_identity_envelope: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Strict identity-aware front door over the merged structural bridge."""
    identity_check = verify_campaign_v3_life_condition_identity_against_packet(
        condition_identity, campaign_packet
    )
    observation_errors = _observations_match_identity(
        condition_observations, condition_identity
    )
    if identity_check["status"] != "PASS" or observation_errors:
        value = {
            "artifact": DISPATCH_ARTIFACT,
            "status": "HOLD_CONDITION_IDENTITY",
            "identity_check": identity_check,
            "observation_errors": observation_errors,
            "dispatch_translation": None,
            "execution_authority": False,
            "life_consumption_authority": False,
            "reward_issuance_authority": False,
            "reseed_anchor_consumption_authority": False,
            "platform_counter_reset_claimed": False,
        }
        value["receipt_digest"] = _sha(
            {key: item for key, item in value.items() if key != "receipt_digest"}
        )
        return value

    translated = translate_campaign_v3_life_dispatch_v1(
        campaign_packet=campaign_packet,
        agent_id=agent_id,
        condition_observations=condition_observations,
        condition_identity_ref=str(condition_identity["identity_ref"]),
        result_class=result_class,
        executed=executed,
        hard_gate_status=hard_gate_status,
        witnesses=witnesses,
        current_git_positions=current_git_positions,
        extra_life_reward=extra_life_reward,
        attempt_identity_envelope=attempt_identity_envelope,
    )
    value = {
        "artifact": DISPATCH_ARTIFACT,
        "status": (
            "TRANSLATED_WITH_FROZEN_IDENTITY"
            if translated.get("status") == "TRANSLATED"
            else "HOLD_TRANSLATION"
        ),
        "identity_envelope_digest": condition_identity.get("envelope_digest"),
        "condition_identity_digest": condition_identity.get("condition_identity_digest"),
        "condition_identity_standing": (
            "FROZEN_AGAINST_UNPLAYED_COMPILER_PACKET_DIGEST; "
            "TEMPORAL_CREATION_AND_EXTERNAL_IDENTITY_AUTHORITY_NOT_INDEPENDENTLY_PROVEN"
        ),
        "dispatch_translation": copy.deepcopy(translated),
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "CONDITION_IDENTITY != CONDITION_OUTCOME",
            "FROZEN_PACKET_IDENTITY != TEMPORAL_CREATION_PROOF",
            "IDENTITY_REF != EXTERNAL_AUTHORITY_PROOF",
            "TRANSLATED_PACKET != EXECUTED_PLAY",
            "PACKET_COMPILER != IDENTITY_MEMBRANE != DISPATCH_TRANSLATOR != SEMANTIC_LIFE_REDUCER",
        ],
    }
    value["receipt_digest"] = _sha(
        {key: item for key, item in value.items() if key != "receipt_digest"}
    )
    return value
