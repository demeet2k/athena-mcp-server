"""Pure Campaign V3 -> canonical ATHENA.QUEST_LIFE_DISPATCH.V1 bridge.

This module translates a validated Campaign V3 life-aware compile packet into the
field/digest contract consumed by the semantic Athena quest-life dispatcher.
It never executes Life Loop transitions, consumes lives/anchors, issues rewards,
or grants scheduler/provider/execution authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from .campaign_v3_life_binding import (
    ARTIFACT as CAMPAIGN_PACKET_ARTIFACT,
    validate_campaign_v3_life_quest_packet,
)
from .campaign_v3_life_attempt_identity import (
    ARTIFACT as ATTEMPT_IDENTITY_ARTIFACT,
    validate_campaign_v3_life_attempt_identity,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.DISPATCH.BRIDGE.V1"
DISPATCH_SCHEMA_VERSION = "ATHENA.QUEST_LIFE_DISPATCH.V1"
LIFE_POLICY = "STAY_IN_GAME_LIFE_LOOP_V1"
DIGEST_PREFIX = "sha256:"

SEMANTIC_DISPATCH_SOURCE = {
    "repo": "demeet2k/Athena",
    "commit": "9aeddf08bf3d73e35ba0a67107e4c420e83aa416",
    "script_path": "scripts/quest_life_dispatch_v1.py",
    "script_blob": "08624386100fd56178dc99ee2ede27009427cca7",
    "schema_path": "schemas/quest_life_dispatch_v1.schema.json",
    "schema_blob": "5f9435dea0cb1e74bdf0143714417a33a8fa502a",
    "mechanism_evidence": "16/16 parent + 23/23 adapter = 39/39 exact-source local PASS",
    "github_actions_ci": False,
    "independent_witness": False,
    "performance_effect": "UNKNOWN",
}

PLAYED_CLASSES = {"CLEAR", "FAIL_CLEAR"}
HOLD_CLASSES = {
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "STALE_STATE_HOLD",
    "CAPABILITY_HOLD",
    "HUMAN_VALUE_CHOICE",
    "BUDGET_EXHAUSTED",
    "META_OVERHEAD_COLLAPSE",
    "DUPLICATION_COLLAPSE",
}
RESULT_CLASSES = PLAYED_CLASSES | HOLD_CLASSES

DISPATCH_REQUIRED_KEYS = {
    "dispatch_schema_version",
    "agent_id",
    "quest_id",
    "quest_version",
    "life_policy",
    "frozen_clear_conditions",
    "clear_condition_digest",
    "result_class",
    "extra_life_reward_eligibility",
    "platform_counter_reset_claimed",
}
DISPATCH_OPTIONAL_KEYS = {
    "executed",
    "hard_gate_status",
    "witnesses",
    "reseed_anchor",
    "current_git_positions",
    "extra_life_reward",
}
DISPATCH_ALLOWED_KEYS = DISPATCH_REQUIRED_KEYS | DISPATCH_OPTIONAL_KEYS


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hold(
    status: str,
    failures: Sequence[str],
    *,
    source_packet_digest: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    out = {
        "artifact": ARTIFACT,
        "status": status,
        "failures": list(failures),
        "source_packet_digest": source_packet_digest,
        "dispatch_packet": None,
        "semantic_dispatch_source": copy.deepcopy(SEMANTIC_DISPATCH_SOURCE),
        "work_executed": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
        **extra,
    }
    out["bridge_digest"] = _sha(
        {key: value for key, value in out.items() if key != "bridge_digest"}
    )
    return out


def _normalize_nonempty_strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be a list")
    out: list[str] = []
    for raw in value:
        text = str(raw or "").strip()
        if not text:
            raise ValueError(f"{field} entries must be non-empty strings")
        out.append(text)
    if not out:
        raise ValueError(f"{field} must be non-empty")
    return out


def _normalize_condition_observations(
    compiled_definitions: Any,
    observations: Any,
) -> list[dict[str, Any]]:
    """Bind explicit criterion IDs to compiler-frozen definitions and outcomes.

    The parent compiler currently freezes only ordered definitions, whereas the
    canonical dispatcher freezes ``{id, definition}`` identity. Criterion IDs
    are therefore explicit bridge input; definitions may not be substituted,
    omitted, duplicated, or invented here.
    """
    compiled = _normalize_nonempty_strings(
        compiled_definitions, "compiled clear conditions"
    )
    if len(compiled) != len(set(compiled)):
        raise ValueError("compiled clear condition definitions must be unique")
    if not isinstance(observations, Sequence) or isinstance(
        observations, (str, bytes)
    ):
        raise ValueError("condition_observations must be a list")
    if not observations:
        raise ValueError("condition_observations must be non-empty")

    rows: list[dict[str, Any]] = []
    ids: set[str] = set()
    definitions: set[str] = set()
    for raw in observations:
        if not isinstance(raw, Mapping):
            raise ValueError("condition observation must be an object")
        criterion_id = str(raw.get("id") or "").strip()
        definition = str(raw.get("definition") or "").strip()
        satisfied = raw.get("satisfied")
        if not criterion_id:
            raise ValueError("condition observation id required")
        if criterion_id in ids:
            raise ValueError(f"duplicate condition observation id: {criterion_id}")
        if not definition:
            raise ValueError("condition observation definition required")
        if definition in definitions:
            raise ValueError(
                f"duplicate condition observation definition: {definition}"
            )
        if type(satisfied) is not bool:
            raise ValueError("condition observation satisfied must be boolean")
        ids.add(criterion_id)
        definitions.add(definition)
        rows.append(
            {
                "id": criterion_id,
                "definition": definition,
                "satisfied": satisfied,
            }
        )

    if definitions != set(compiled) or len(rows) != len(compiled):
        missing = sorted(set(compiled) - definitions)
        extra = sorted(definitions - set(compiled))
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise ValueError(
            "condition observations must bind exactly the compiled definitions"
            + (": " + ";".join(details) if details else "")
        )

    rows.sort(key=lambda row: row["id"])
    return rows


def compute_pinned_dispatch_clear_condition_digest(
    quest_id: str,
    quest_version: str,
    frozen_clear_conditions: Any,
) -> str:
    """Byte-compatible digest with Athena@9aeddf08 quest_life_dispatch_v1.py."""
    quest_id = str(quest_id or "").strip()
    quest_version = str(quest_version or "").strip()
    if not quest_id:
        raise ValueError("quest_id required")
    if not quest_version:
        raise ValueError("quest_version required")
    if not isinstance(frozen_clear_conditions, list) or not frozen_clear_conditions:
        raise ValueError("frozen_clear_conditions must be a nonempty list")

    ids: set[str] = set()
    conditions: list[dict[str, str]] = []
    for raw in frozen_clear_conditions:
        if not isinstance(raw, Mapping):
            raise ValueError("clear condition must be a mapping")
        criterion_id = raw.get("id")
        definition = raw.get("definition")
        satisfied = raw.get("satisfied")
        if not isinstance(criterion_id, str) or not criterion_id:
            raise ValueError("clear condition id required")
        if criterion_id in ids:
            raise ValueError("duplicate clear condition id")
        ids.add(criterion_id)
        if not isinstance(definition, str) or not definition:
            raise ValueError("clear condition definition required")
        if type(satisfied) is not bool:
            raise ValueError("clear condition satisfied must be boolean")
        conditions.append({"id": criterion_id, "definition": definition})

    conditions.sort(key=lambda row: row["id"])
    basis = {
        "quest_id": quest_id,
        "quest_version": quest_version,
        "conditions": conditions,
    }
    return DIGEST_PREFIX + _sha(basis)


def _normalize_git_positions(value: Any) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("current_git_positions must be a list")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ValueError("current_git_positions entries must be objects")
        repo = str(raw.get("repo") or "").strip()
        ref = str(raw.get("ref") or "").strip()
        head = str(raw.get("head") or "").strip()
        tree_value = raw.get("tree")
        if not repo or not ref or not head:
            raise ValueError("current_git_positions requires repo/ref/head")
        coordinate = f"{repo}::{ref}"
        if coordinate in seen:
            raise ValueError(f"duplicate current_git_position: {coordinate}")
        seen.add(coordinate)
        row: dict[str, Any] = {"repo": repo, "ref": ref, "head": head}
        if tree_value is not None:
            if not isinstance(tree_value, str):
                raise ValueError("current_git_positions tree must be a string")
            row["tree"] = tree_value
        rows.append(row)
    if not rows:
        raise ValueError("current_git_positions must be non-empty")
    rows.sort(key=lambda row: (row["repo"], row["ref"]))
    return rows


def _raw_reseed_anchor(packet: Mapping[str, Any]) -> dict[str, Any] | None:
    anchor = packet.get("RESEED_ANCHOR")
    if anchor is None:
        return None
    if not isinstance(anchor, Mapping):
        raise ValueError("RESEED_ANCHOR must be an object")
    # Campaign compilation adds `anchor_digest` metadata, but the pinned semantic
    # RESEED_ANCHOR_V1 schema is strict and does not admit that compiler-only key.
    return copy.deepcopy(
        {key: value for key, value in anchor.items() if key != "anchor_digest"}
    )


def _normalize_reward(reward: Any) -> dict[str, Any] | None:
    if reward is None:
        return None
    if not isinstance(reward, Mapping):
        raise ValueError("extra_life_reward must be an object")
    allowed = {"receipt_id", "delta", "verified", "self_scored", "witnesses"}
    extra = sorted(set(reward) - allowed)
    if extra:
        raise ValueError("extra_life_reward has unsupported fields: " + ",".join(extra))
    receipt_id = str(reward.get("receipt_id") or "").strip()
    if not receipt_id:
        raise ValueError("extra_life_reward receipt_id required")
    if reward.get("delta") != 1:
        raise ValueError("extra_life_reward delta must equal 1")
    if type(reward.get("verified")) is not bool:
        raise ValueError("extra_life_reward verified must be boolean")
    if type(reward.get("self_scored")) is not bool:
        raise ValueError("extra_life_reward self_scored must be boolean")
    witnesses = _normalize_nonempty_strings(
        reward.get("witnesses"), "extra_life_reward witnesses"
    )
    return {
        "receipt_id": receipt_id,
        "delta": 1,
        "verified": reward["verified"],
        "self_scored": reward["self_scored"],
        "witnesses": witnesses,
    }


def _attempt_compatibility(
    source_packet_digest: str,
    attempt_identity_envelope: Any,
) -> dict[str, Any]:
    """Preserve candidate identity metadata without injecting it into Dispatch V1."""
    if attempt_identity_envelope is None:
        return {
            "status": "NOT_SUPPLIED",
            "supported_by_pinned_dispatch": False,
            "attempt_id": None,
            "standing": "PINNED_DISPATCH_V1_HAS_NO_ATTEMPT_ID_FIELD",
            "execution_authority": False,
        }
    if not isinstance(attempt_identity_envelope, Mapping):
        raise ValueError("attempt_identity_envelope must be an object")
    errors = validate_campaign_v3_life_attempt_identity(attempt_identity_envelope)
    if errors:
        raise ValueError("invalid attempt_identity_envelope: " + ",".join(errors))
    if attempt_identity_envelope.get("packet_digest") != source_packet_digest:
        raise ValueError("attempt_identity_envelope packet_digest mismatch")
    return {
        "status": "PRESERVED_OUT_OF_BAND",
        "supported_by_pinned_dispatch": False,
        "artifact": ATTEMPT_IDENTITY_ARTIFACT,
        "attempt_id": attempt_identity_envelope.get("attempt_id"),
        "execution_event_id": attempt_identity_envelope.get("execution_event_id"),
        "standing": (
            "CANDIDATE_METADATA_ONLY; PINNED ATHENA.QUEST_LIFE_DISPATCH.V1 "
            "DOES_NOT_ACCEPT ATTEMPT_ID"
        ),
        "execution_authority": False,
    }


def validate_pinned_dispatch_packet_shape(packet: Mapping[str, Any]) -> list[str]:
    """Structural validator mirrored from the pinned schema, without execution."""
    if not isinstance(packet, Mapping):
        return ["packet_not_object"]
    errors: list[str] = []
    extra = sorted(set(packet) - DISPATCH_ALLOWED_KEYS)
    missing = sorted(DISPATCH_REQUIRED_KEYS - set(packet))
    errors.extend(f"unknown:{key}" for key in extra)
    errors.extend(f"missing:{key}" for key in missing)

    if packet.get("dispatch_schema_version") != DISPATCH_SCHEMA_VERSION:
        errors.append("dispatch_schema_version")
    if packet.get("life_policy") != LIFE_POLICY:
        errors.append("life_policy")
    if packet.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed")
    for key in ("agent_id", "quest_id", "quest_version"):
        if not isinstance(packet.get(key), str) or not packet.get(key):
            errors.append(key)
    if packet.get("result_class") not in RESULT_CLASSES:
        errors.append("result_class")
    if type(packet.get("extra_life_reward_eligibility")) is not bool:
        errors.append("extra_life_reward_eligibility")

    conditions = packet.get("frozen_clear_conditions")
    try:
        digest = compute_pinned_dispatch_clear_condition_digest(
            str(packet.get("quest_id") or ""),
            str(packet.get("quest_version") or ""),
            conditions,
        )
    except ValueError as exc:
        errors.append(f"frozen_clear_conditions:{exc}")
    else:
        if packet.get("clear_condition_digest") != digest:
            errors.append("clear_condition_digest")

    result_class = packet.get("result_class")
    if result_class in PLAYED_CLASSES:
        if packet.get("executed") is not True:
            errors.append("executed")
        if packet.get("hard_gate_status") not in {"PASS", "FAIL"}:
            errors.append("hard_gate_status")
        witnesses = packet.get("witnesses")
        if not isinstance(witnesses, list) or not witnesses:
            errors.append("witnesses")

    reward = packet.get("extra_life_reward")
    if reward is not None:
        if result_class != "CLEAR":
            errors.append("extra_life_reward_requires_clear")
        if packet.get("extra_life_reward_eligibility") is not True:
            errors.append("extra_life_reward_not_eligible")
        try:
            normalized_reward = _normalize_reward(reward)
        except ValueError as exc:
            errors.append(f"extra_life_reward:{exc}")
        else:
            if normalized_reward != reward:
                errors.append("extra_life_reward_not_normalized")

    try:
        _normalize_git_positions(packet.get("current_git_positions"))
    except ValueError as exc:
        errors.append(f"current_git_positions:{exc}")

    anchor = packet.get("reseed_anchor")
    if anchor is not None:
        if not isinstance(anchor, Mapping):
            errors.append("reseed_anchor")
        elif "anchor_digest" in anchor:
            errors.append("reseed_anchor_contains_campaign_metadata")
    return errors


def translate_campaign_v3_life_dispatch_v1(
    *,
    campaign_packet: Mapping[str, Any],
    agent_id: str,
    condition_observations: Sequence[Mapping[str, Any]],
    result_class: str,
    executed: bool | None = None,
    hard_gate_status: str | None = None,
    witnesses: Sequence[Any] | None = None,
    current_git_positions: Sequence[Mapping[str, Any]] | None = None,
    extra_life_reward: Mapping[str, Any] | None = None,
    attempt_identity_envelope: Mapping[str, Any] | None = None,
    condition_identity_ref: str | None = None,
) -> dict[str, Any]:
    """Translate a validated Campaign compile packet into canonical Dispatch V1.

    The returned ``dispatch_packet`` is data only. Callers must send it to the
    semantic Athena dispatcher separately; this bridge has zero transition
    authority.
    """
    if not isinstance(campaign_packet, Mapping):
        return _hold("HOLD_INVALID_CAMPAIGN_PACKET", ["campaign_packet_not_object"])
    source_packet_digest = str(campaign_packet.get("packet_digest") or "").strip() or None
    packet_errors = validate_campaign_v3_life_quest_packet(campaign_packet)
    if packet_errors:
        return _hold(
            "HOLD_INVALID_CAMPAIGN_PACKET",
            packet_errors,
            source_packet_digest=source_packet_digest,
        )
    if campaign_packet.get("artifact") != CAMPAIGN_PACKET_ARTIFACT:
        return _hold(
            "HOLD_INVALID_CAMPAIGN_PACKET",
            ["campaign_packet_artifact"],
            source_packet_digest=source_packet_digest,
        )

    failures: list[str] = []
    campaign = campaign_packet.get("campaign")
    quest = campaign_packet.get("quest")
    if not isinstance(campaign, Mapping) or not isinstance(quest, Mapping):
        return _hold(
            "HOLD_INVALID_CAMPAIGN_PACKET",
            ["campaign_or_quest_missing"],
            source_packet_digest=source_packet_digest,
        )

    normalized_agent = str(agent_id or "").strip()
    if not normalized_agent:
        failures.append("AGENT_ID_REQUIRED")
    elif normalized_agent != str(campaign.get("agent_coordinate_name") or ""):
        failures.append("AGENT_ID_CAMPAIGN_COORDINATE_MISMATCH")

    identity_ref = str(condition_identity_ref or "").strip()
    if not identity_ref:
        failures.append("CONDITION_IDENTITY_REF_REQUIRED")

    try:
        conditions = _normalize_condition_observations(
            campaign_packet.get("CLEAR_CONDITIONS"),
            condition_observations,
        )
    except ValueError as exc:
        failures.append(f"CONDITION_OBSERVATIONS_INVALID:{exc}")
        conditions = []

    normalized_result = str(result_class or "").strip().upper()
    if normalized_result not in RESULT_CLASSES:
        failures.append("RESULT_CLASS_INVALID")

    normalized_witnesses: list[str] | None = None
    if normalized_result in PLAYED_CLASSES:
        if executed is not True:
            failures.append("PLAYED_RESULT_REQUIRES_EXECUTED_TRUE")
        if hard_gate_status not in {"PASS", "FAIL"}:
            failures.append("PLAYED_RESULT_REQUIRES_HARD_GATE_STATUS")
        try:
            normalized_witnesses = _normalize_nonempty_strings(
                witnesses, "witnesses"
            )
        except ValueError as exc:
            failures.append(f"WITNESSES_INVALID:{exc}")
    else:
        if executed is True:
            # HOLD is not a played life-consuming attempt in the semantic reducer.
            executed = False

    try:
        positions = _normalize_git_positions(current_git_positions)
    except ValueError as exc:
        failures.append(f"CURRENT_GIT_POSITIONS_INVALID:{exc}")
        positions = None

    try:
        reward = _normalize_reward(extra_life_reward)
    except ValueError as exc:
        failures.append(f"EXTRA_LIFE_REWARD_INVALID:{exc}")
        reward = None

    eligibility_obj = campaign_packet.get("EXTRA_LIFE_REWARD_ELIGIBILITY")
    if not isinstance(eligibility_obj, Mapping):
        failures.append("CAMPAIGN_REWARD_ELIGIBILITY_INVALID")
        eligibility = False
    else:
        eligibility = bool(eligibility_obj.get("eligible", False))

    if reward is not None and not eligibility:
        failures.append("EXTRA_LIFE_REWARD_NOT_ELIGIBLE")
    if reward is not None and normalized_result != "CLEAR":
        failures.append("EXTRA_LIFE_REWARD_REQUIRES_CLEAR")

    try:
        attempt_compat = _attempt_compatibility(
            str(source_packet_digest or ""),
            attempt_identity_envelope,
        )
    except ValueError as exc:
        failures.append(f"ATTEMPT_IDENTITY_INVALID:{exc}")
        attempt_compat = {
            "status": "HOLD",
            "supported_by_pinned_dispatch": False,
            "attempt_id": None,
            "execution_authority": False,
        }

    try:
        raw_anchor = _raw_reseed_anchor(campaign_packet)
    except ValueError as exc:
        failures.append(f"RESEED_ANCHOR_INVALID:{exc}")
        raw_anchor = None

    quest_id = str(quest.get("quest_id") or "")
    quest_version = str(quest.get("quest_version") or "")
    canonical_digest: str | None = None
    if conditions:
        try:
            canonical_digest = compute_pinned_dispatch_clear_condition_digest(
                quest_id, quest_version, conditions
            )
        except ValueError as exc:
            failures.append(f"CANONICAL_DIGEST_INVALID:{exc}")

    if failures:
        return _hold(
            "HOLD_DISPATCH_TRANSLATION",
            failures,
            source_packet_digest=source_packet_digest,
            campaign_clear_condition_digest=campaign_packet.get(
                "CLEAR_CONDITION_DIGEST"
            ),
            canonical_clear_condition_digest=canonical_digest,
            condition_identity_ref=identity_ref or None,
            attempt_compatibility=attempt_compat,
        )

    dispatch_packet: dict[str, Any] = {
        "dispatch_schema_version": DISPATCH_SCHEMA_VERSION,
        "agent_id": normalized_agent,
        "quest_id": quest_id,
        "quest_version": quest_version,
        "life_policy": LIFE_POLICY,
        "frozen_clear_conditions": conditions,
        "clear_condition_digest": canonical_digest,
        "result_class": normalized_result,
        "extra_life_reward_eligibility": eligibility,
        "platform_counter_reset_claimed": False,
    }
    if normalized_result in PLAYED_CLASSES:
        dispatch_packet["executed"] = True
        dispatch_packet["hard_gate_status"] = hard_gate_status
        dispatch_packet["witnesses"] = normalized_witnesses
    elif executed is not None:
        dispatch_packet["executed"] = False

    if raw_anchor is not None:
        dispatch_packet["reseed_anchor"] = raw_anchor
    if positions is not None:
        dispatch_packet["current_git_positions"] = positions
    if reward is not None:
        dispatch_packet["extra_life_reward"] = reward

    shape_errors = validate_pinned_dispatch_packet_shape(dispatch_packet)
    if shape_errors:
        return _hold(
            "HOLD_PINNED_DISPATCH_SHAPE",
            shape_errors,
            source_packet_digest=source_packet_digest,
            campaign_clear_condition_digest=campaign_packet.get(
                "CLEAR_CONDITION_DIGEST"
            ),
            canonical_clear_condition_digest=canonical_digest,
            condition_identity_ref=identity_ref,
            attempt_compatibility=attempt_compat,
        )

    out = {
        "artifact": ARTIFACT,
        "status": "TRANSLATED",
        "source_packet_artifact": campaign_packet.get("artifact"),
        "source_packet_digest": source_packet_digest,
        "campaign_clear_condition_digest": campaign_packet.get(
            "CLEAR_CONDITION_DIGEST"
        ),
        "canonical_clear_condition_digest": canonical_digest,
        "condition_identity_ref": identity_ref,
        "condition_identity_standing": (
            "EXPLICIT_BRIDGE_INPUT_BOUND_TO_COMPILER_DEFINITIONS; "
            "IDENTIFIERS_ARE_NOT_INFERRED_BY_THE_CAMPAIGN_COMPILER"
        ),
        "dispatch_packet": dispatch_packet,
        "semantic_dispatch_source": copy.deepcopy(SEMANTIC_DISPATCH_SOURCE),
        "attempt_compatibility": attempt_compat,
        "work_executed": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "PACKET_COMPILER != DISPATCH_TRANSLATOR != SEMANTIC_LIFE_REDUCER",
            "CAMPAIGN_CLEAR_CONDITION_DIGEST != CANONICAL_CLEAR_CONDITION_DIGEST",
            "CONDITION_IDENTITY_IS_EXPLICIT_NOT_INFERRED",
            "TRANSLATED_PACKET != EXECUTED_PLAY",
            "ELIGIBILITY != REWARD_ISSUANCE",
            "RESEED_ANCHOR != RESEED_AUTHORITY",
            "ATTEMPT_METADATA != PLAY_SETTLEMENT_AUTHORITY",
            "LOGICAL_RESEED != PLATFORM_COUNTER_RESET",
        ],
    }
    out["bridge_digest"] = _sha(
        {key: value for key, value in out.items() if key != "bridge_digest"}
    )
    return out


def validate_campaign_v3_life_dispatch_bridge(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["bridge_not_object"]
    errors: list[str] = []
    if value.get("artifact") != ARTIFACT:
        errors.append("artifact")
    if value.get("status") != "TRANSLATED":
        errors.append("status")
    dispatch_packet = value.get("dispatch_packet")
    if not isinstance(dispatch_packet, Mapping):
        errors.append("dispatch_packet")
    else:
        errors.extend(
            f"dispatch_packet:{item}"
            for item in validate_pinned_dispatch_packet_shape(dispatch_packet)
        )
    if value.get("semantic_dispatch_source") != SEMANTIC_DISPATCH_SOURCE:
        errors.append("semantic_dispatch_source")
    for key in (
        "work_executed",
        "execution_authority",
        "life_consumption_authority",
        "reward_issuance_authority",
        "reseed_anchor_consumption_authority",
        "platform_counter_reset_claimed",
    ):
        if value.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    digest = str(value.get("bridge_digest") or "")
    expected = _sha(
        {key: item for key, item in value.items() if key != "bridge_digest"}
    )
    if not digest or digest != expected:
        errors.append("bridge_digest")
    return errors


def verify_campaign_v3_life_dispatch_bridge(value: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_dispatch_bridge(value)
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.DISPATCH.BRIDGE.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "errors": errors,
        "source_packet_digest": (
            value.get("source_packet_digest") if isinstance(value, Mapping) else None
        ),
        "canonical_clear_condition_digest": (
            value.get("canonical_clear_condition_digest")
            if isinstance(value, Mapping)
            else None
        ),
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
    }
