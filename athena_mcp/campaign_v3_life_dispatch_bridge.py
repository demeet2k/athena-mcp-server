"""Pure Campaign V3 -> canonical ATHENA.QUEST_LIFE_DISPATCH.V1 bridge.

Translate a validated Campaign V3 Life packet plus observed play-time fields into
the exact data contract consumed by the pinned semantic Athena dispatcher. This
module never executes Life Loop transitions, consumes lives or anchors, issues
rewards, or grants scheduler/provider/execution authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from .campaign_v3_life_attempt_identity import (
    ARTIFACT as ATTEMPT_IDENTITY_ARTIFACT,
    validate_campaign_v3_life_attempt_identity,
)
from .campaign_v3_life_binding import (
    ARTIFACT as CAMPAIGN_PACKET_ARTIFACT,
    validate_campaign_v3_life_quest_packet,
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

RESEED_REQUIRED_KEYS = {
    "schema_version",
    "anchor_id",
    "run_id",
    "agent_coordinate_name",
    "reseed_epoch",
    "pulse_age_before",
    "pulse_age_after",
    "git",
    "prompt_digest",
    "issue_pressure_digest",
    "target_versions",
    "durable_returns",
    "satisfied_work",
    "residuals",
    "holds",
    "continuation_value_class",
    "selected_successor",
    "stop_class",
    "reverse_route",
    "witnesses",
    "platform_counter_reset_claimed",
}
RESEED_OPTIONAL_KEYS = {"parent_anchor_id", "parent_reseed_epoch", "git_positions"}
RESEED_ALLOWED_KEYS = RESEED_REQUIRED_KEYS | RESEED_OPTIONAL_KEYS
RESEED_GIT_ALLOWED_KEYS = {
    "repo",
    "ref",
    "head_before",
    "head_after",
    "tree_after",
    "changed",
}
RESEED_STOP_CLASSES = {
    None,
    "CONTINUE_POSITIVE_FRONTIER",
    "SUCCESS_CLOSED",
    "NO_POSITIVE_FRONTIER",
    "BUDGET_EXHAUSTED",
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "STALE_STATE_HOLD",
    "CAPABILITY_HOLD",
    "HUMAN_VALUE_CHOICE",
    "META_OVERHEAD_COLLAPSE",
    "DUPLICATION_COLLAPSE",
}


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


def _nonempty_strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be a list")
    rows: list[str] = []
    for raw in value:
        text = str(raw or "").strip()
        if not text:
            raise ValueError(f"{field} entries must be non-empty strings")
        rows.append(text)
    if not rows:
        raise ValueError(f"{field} must be non-empty")
    return rows


def _schema_string_list(value: Any, field: str, *, min_items: int = 0) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{field} must contain at least {min_items} item(s)")
    for raw in value:
        if not isinstance(raw, str):
            raise ValueError(f"{field} entries must be strings")
        if min_items and not raw:
            raise ValueError(f"{field} entries must be non-empty strings")
    return list(value)


def _condition_observations(
    compiled_definitions: Any,
    observations: Any,
) -> list[dict[str, Any]]:
    """Bind explicit IDs and outcomes to exactly the compiler-frozen definitions."""
    compiled = _nonempty_strings(compiled_definitions, "compiled clear conditions")
    if len(compiled) != len(set(compiled)):
        raise ValueError("compiled clear condition definitions must be unique")
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise ValueError("condition_observations must be a list")
    if not observations:
        raise ValueError("condition_observations must be non-empty")

    ids: set[str] = set()
    definitions: set[str] = set()
    rows: list[dict[str, Any]] = []
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
            raise ValueError(f"duplicate condition observation definition: {definition}")
        if type(satisfied) is not bool:
            raise ValueError("condition observation satisfied must be boolean")
        ids.add(criterion_id)
        definitions.add(definition)
        rows.append({"id": criterion_id, "definition": definition, "satisfied": satisfied})

    compiled_set = set(compiled)
    if definitions != compiled_set or len(rows) != len(compiled):
        missing = sorted(compiled_set - definitions)
        extra = sorted(definitions - compiled_set)
        suffix: list[str] = []
        if missing:
            suffix.append("missing=" + ",".join(missing))
        if extra:
            suffix.append("extra=" + ",".join(extra))
        raise ValueError(
            "condition observations must bind exactly the compiled definitions"
            + (": " + ";".join(suffix) if suffix else "")
        )
    rows.sort(key=lambda row: row["id"])
    return rows


def compute_pinned_dispatch_clear_condition_digest(
    quest_id: str,
    quest_version: str,
    frozen_clear_conditions: Any,
) -> str:
    """Byte-compatible with Athena@9aeddf08 quest_life_dispatch_v1.py."""
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
        extra = sorted(set(raw) - {"id", "definition", "satisfied"})
        missing = sorted({"id", "definition", "satisfied"} - set(raw))
        if extra:
            raise ValueError("clear condition has unsupported fields: " + ",".join(extra))
        if missing:
            raise ValueError("clear condition missing fields: " + ",".join(missing))
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
    return DIGEST_PREFIX + _sha(
        {"quest_id": quest_id, "quest_version": quest_version, "conditions": conditions}
    )


def _git_positions(value: Any) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("current_git_positions must be a list")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ValueError("current_git_positions entries must be objects")
        allowed = {"repo", "ref", "head", "tree"}
        extra = sorted(set(raw) - allowed)
        missing = sorted({"repo", "ref", "head"} - set(raw))
        if extra:
            raise ValueError("current_git_positions has unsupported fields: " + ",".join(extra))
        if missing:
            raise ValueError("current_git_positions missing fields: " + ",".join(missing))
        repo = raw.get("repo")
        ref = raw.get("ref")
        head = raw.get("head")
        if not isinstance(repo, str) or not repo:
            raise ValueError("current_git_positions repo must be a non-empty string")
        if not isinstance(ref, str) or not ref:
            raise ValueError("current_git_positions ref must be a non-empty string")
        if not isinstance(head, str) or not head:
            raise ValueError("current_git_positions head must be a non-empty string")
        coordinate = f"{repo}::{ref}"
        if coordinate in seen:
            raise ValueError(f"duplicate current_git_position: {coordinate}")
        seen.add(coordinate)
        row: dict[str, Any] = {"repo": repo, "ref": ref, "head": head}
        if "tree" in raw:
            tree = raw.get("tree")
            if not isinstance(tree, str):
                raise ValueError("current_git_positions tree must be a string")
            row["tree"] = tree
        rows.append(row)
    if not rows:
        raise ValueError("current_git_positions must be non-empty")
    rows.sort(key=lambda row: (row["repo"], row["ref"]))
    return rows


def _reward(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("extra_life_reward must be an object")
    allowed = {"receipt_id", "delta", "verified", "self_scored", "witnesses"}
    extra = sorted(set(value) - allowed)
    missing = sorted(allowed - set(value))
    if extra:
        raise ValueError("extra_life_reward has unsupported fields: " + ",".join(extra))
    if missing:
        raise ValueError("extra_life_reward missing fields: " + ",".join(missing))
    receipt_id = value.get("receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id:
        raise ValueError("extra_life_reward receipt_id required")
    if value.get("delta") != 1 or type(value.get("delta")) is not int:
        raise ValueError("extra_life_reward delta must equal integer 1")
    if type(value.get("verified")) is not bool:
        raise ValueError("extra_life_reward verified must be boolean")
    if type(value.get("self_scored")) is not bool:
        raise ValueError("extra_life_reward self_scored must be boolean")
    witnesses = _schema_string_list(value.get("witnesses"), "extra_life_reward witnesses", min_items=1)
    return {
        "receipt_id": receipt_id,
        "delta": 1,
        "verified": value["verified"],
        "self_scored": value["self_scored"],
        "witnesses": witnesses,
    }


def _validate_reseed_anchor_shape(value: Any) -> list[str]:
    """Strict structural mirror of pinned ATHENA.RESEED_ANCHOR.V1."""
    if not isinstance(value, Mapping):
        return ["reseed_anchor_not_object"]
    errors: list[str] = []
    errors.extend(f"unknown:{key}" for key in sorted(set(value) - RESEED_ALLOWED_KEYS))
    errors.extend(f"missing:{key}" for key in sorted(RESEED_REQUIRED_KEYS - set(value)))
    if value.get("schema_version") != "ATHENA.RESEED_ANCHOR.V1":
        errors.append("schema_version")
    for key in ("anchor_id", "run_id", "agent_coordinate_name"):
        if not isinstance(value.get(key), str) or not value.get(key):
            errors.append(key)
    if "parent_anchor_id" in value and value.get("parent_anchor_id") is not None and not isinstance(value.get("parent_anchor_id"), str):
        errors.append("parent_anchor_id")
    for key in ("reseed_epoch", "pulse_age_before"):
        raw = value.get(key)
        if type(raw) is not int or raw < 0:
            errors.append(key)
    if "parent_reseed_epoch" in value:
        raw = value.get("parent_reseed_epoch")
        if raw is not None and (type(raw) is not int or raw < 0):
            errors.append("parent_reseed_epoch")
    if type(value.get("pulse_age_after")) is not int or value.get("pulse_age_after") != 0:
        errors.append("pulse_age_after")

    git = value.get("git")
    if not isinstance(git, Mapping):
        errors.append("git")
    else:
        extra = sorted(set(git) - RESEED_GIT_ALLOWED_KEYS)
        missing = sorted({"head_after", "changed"} - set(git))
        if extra:
            errors.append("git:unknown:" + ",".join(extra))
        if missing:
            errors.append("git:missing:" + ",".join(missing))
        for key in ("repo", "ref", "head_before", "tree_after"):
            if key in git and git.get(key) is not None and not isinstance(git.get(key), str):
                errors.append(f"git:{key}")
        if not isinstance(git.get("head_after"), str) or not git.get("head_after"):
            errors.append("git:head_after")
        if type(git.get("changed")) is not bool:
            errors.append("git:changed")

    if "git_positions" in value:
        positions = value.get("git_positions")
        if not isinstance(positions, list) or not positions:
            errors.append("git_positions")
        else:
            for index, raw in enumerate(positions):
                prefix = f"git_positions[{index}]"
                if not isinstance(raw, Mapping):
                    errors.append(prefix)
                    continue
                extra = sorted(set(raw) - {"repo", "ref", "head", "tree"})
                missing = sorted({"repo", "ref", "head"} - set(raw))
                if extra:
                    errors.append(prefix + ":unknown:" + ",".join(extra))
                if missing:
                    errors.append(prefix + ":missing:" + ",".join(missing))
                for key in ("repo", "ref", "head"):
                    if not isinstance(raw.get(key), str) or not raw.get(key):
                        errors.append(prefix + ":" + key)
                if "tree" in raw and raw.get("tree") is not None and not isinstance(raw.get("tree"), str):
                    errors.append(prefix + ":tree")

    for key in ("prompt_digest", "issue_pressure_digest"):
        raw = value.get(key)
        if raw is not None and not isinstance(raw, str):
            errors.append(key)

    target_versions = value.get("target_versions")
    if not isinstance(target_versions, list):
        errors.append("target_versions")
    else:
        for index, raw in enumerate(target_versions):
            prefix = f"target_versions[{index}]"
            if not isinstance(raw, Mapping):
                errors.append(prefix)
                continue
            extra = sorted(set(raw) - {"id", "version"})
            missing = sorted({"id", "version"} - set(raw))
            if extra:
                errors.append(prefix + ":unknown:" + ",".join(extra))
            if missing:
                errors.append(prefix + ":missing:" + ",".join(missing))
            for key in ("id", "version"):
                if not isinstance(raw.get(key), str) or not raw.get(key):
                    errors.append(prefix + ":" + key)

    for key, minimum in (
        ("durable_returns", 1),
        ("satisfied_work", 0),
        ("residuals", 0),
        ("holds", 0),
        ("reverse_route", 0),
        ("witnesses", 1),
    ):
        raw = value.get(key)
        if not isinstance(raw, list) or len(raw) < minimum or any(not isinstance(item, str) for item in raw):
            errors.append(key)

    if value.get("continuation_value_class") not in {"POSITIVE", "CONTINUE_POSITIVE_FRONTIER", "NONPOSITIVE"}:
        errors.append("continuation_value_class")
    if value.get("selected_successor") is not None and not isinstance(value.get("selected_successor"), str):
        errors.append("selected_successor")
    if value.get("stop_class") not in RESEED_STOP_CLASSES:
        errors.append("stop_class")
    if value.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed")
    return errors


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
    """Strict structural mirror of the pinned schema; it never executes the packet."""
    if not isinstance(packet, Mapping):
        return ["packet_not_object"]
    errors: list[str] = []
    errors.extend(f"unknown:{key}" for key in sorted(set(packet) - DISPATCH_ALLOWED_KEYS))
    errors.extend(f"missing:{key}" for key in sorted(DISPATCH_REQUIRED_KEYS - set(packet)))
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

    try:
        expected_digest = compute_pinned_dispatch_clear_condition_digest(
            str(packet.get("quest_id") or ""),
            str(packet.get("quest_version") or ""),
            packet.get("frozen_clear_conditions"),
        )
    except ValueError as exc:
        errors.append(f"frozen_clear_conditions:{exc}")
    else:
        if packet.get("clear_condition_digest") != expected_digest:
            errors.append("clear_condition_digest")

    if "executed" in packet and type(packet.get("executed")) is not bool:
        errors.append("executed")
    if "hard_gate_status" in packet and packet.get("hard_gate_status") not in {"PASS", "FAIL"}:
        errors.append("hard_gate_status")
    if "witnesses" in packet:
        try:
            _schema_string_list(packet.get("witnesses"), "witnesses", min_items=1)
        except ValueError as exc:
            errors.append(f"witnesses:{exc}")

    if packet.get("result_class") in PLAYED_CLASSES:
        if packet.get("executed") is not True:
            errors.append("executed")
        if packet.get("hard_gate_status") not in {"PASS", "FAIL"}:
            errors.append("hard_gate_status")
        if "witnesses" not in packet:
            errors.append("witnesses")

    reward = packet.get("extra_life_reward")
    if reward is not None:
        if packet.get("result_class") != "CLEAR":
            errors.append("extra_life_reward_requires_clear")
        if packet.get("extra_life_reward_eligibility") is not True:
            errors.append("extra_life_reward_not_eligible")
        try:
            if _reward(reward) != reward:
                errors.append("extra_life_reward_not_normalized")
        except ValueError as exc:
            errors.append(f"extra_life_reward:{exc}")

    if "reseed_anchor" in packet:
        errors.extend(
            f"reseed_anchor:{item}"
            for item in _validate_reseed_anchor_shape(packet.get("reseed_anchor"))
        )

    try:
        normalized_positions = _git_positions(packet.get("current_git_positions"))
        if "current_git_positions" in packet and normalized_positions != packet.get("current_git_positions"):
            errors.append("current_git_positions_not_normalized")
    except ValueError as exc:
        errors.append(f"current_git_positions:{exc}")
    return errors


def translate_campaign_v3_life_dispatch_v1(
    *,
    campaign_packet: Mapping[str, Any],
    agent_id: str,
    condition_observations: Sequence[Mapping[str, Any]],
    condition_identity_ref: str,
    result_class: str,
    executed: bool | None = None,
    hard_gate_status: str | None = None,
    witnesses: Sequence[Any] | None = None,
    current_git_positions: Sequence[Mapping[str, Any]] | None = None,
    extra_life_reward: Mapping[str, Any] | None = None,
    attempt_identity_envelope: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a canonical Dispatch V1 data packet or a typed HOLD."""
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

    campaign = campaign_packet.get("campaign")
    quest = campaign_packet.get("quest")
    if not isinstance(campaign, Mapping) or not isinstance(quest, Mapping):
        return _hold(
            "HOLD_INVALID_CAMPAIGN_PACKET",
            ["campaign_or_quest_missing"],
            source_packet_digest=source_packet_digest,
        )

    failures: list[str] = []
    normalized_agent = str(agent_id or "").strip()
    if not normalized_agent:
        failures.append("AGENT_ID_REQUIRED")
    elif normalized_agent != str(campaign.get("agent_coordinate_name") or ""):
        failures.append("AGENT_ID_CAMPAIGN_COORDINATE_MISMATCH")

    identity_ref = str(condition_identity_ref or "").strip()
    if not identity_ref:
        failures.append("CONDITION_IDENTITY_REF_REQUIRED")
    try:
        conditions = _condition_observations(
            campaign_packet.get("CLEAR_CONDITIONS"), condition_observations
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
            normalized_witnesses = _nonempty_strings(witnesses, "witnesses")
        except ValueError as exc:
            failures.append(f"WITNESSES_INVALID:{exc}")
    elif executed is True:
        executed = False

    try:
        positions = _git_positions(current_git_positions)
    except ValueError as exc:
        failures.append(f"CURRENT_GIT_POSITIONS_INVALID:{exc}")
        positions = None
    try:
        reward = _reward(extra_life_reward)
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
            str(source_packet_digest or ""), attempt_identity_envelope
        )
    except ValueError as exc:
        failures.append(f"ATTEMPT_IDENTITY_INVALID:{exc}")
        attempt_compat = {
            "status": "HOLD",
            "supported_by_pinned_dispatch": False,
            "attempt_id": None,
            "execution_authority": False,
        }

    raw_anchor = campaign_packet.get("RESEED_ANCHOR")
    if not isinstance(raw_anchor, Mapping):
        failures.append("RESEED_ANCHOR_INVALID")
        anchor = None
    else:
        anchor = copy.deepcopy(dict(raw_anchor))

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
            campaign_clear_condition_digest=campaign_packet.get("CLEAR_CONDITION_DIGEST"),
            canonical_clear_condition_digest=canonical_digest,
            campaign_reseed_anchor_digest=campaign_packet.get("RESEED_ANCHOR_DIGEST"),
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
        dispatch_packet.update(
            {
                "executed": True,
                "hard_gate_status": hard_gate_status,
                "witnesses": normalized_witnesses,
            }
        )
    elif executed is not None:
        dispatch_packet["executed"] = False
    if anchor is not None:
        dispatch_packet["reseed_anchor"] = anchor
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
            campaign_clear_condition_digest=campaign_packet.get("CLEAR_CONDITION_DIGEST"),
            canonical_clear_condition_digest=canonical_digest,
            campaign_reseed_anchor_digest=campaign_packet.get("RESEED_ANCHOR_DIGEST"),
            condition_identity_ref=identity_ref,
            attempt_compatibility=attempt_compat,
        )

    out = {
        "artifact": ARTIFACT,
        "status": "TRANSLATED",
        "source_packet_artifact": campaign_packet.get("artifact"),
        "source_packet_digest": source_packet_digest,
        "campaign_clear_condition_digest": campaign_packet.get("CLEAR_CONDITION_DIGEST"),
        "canonical_clear_condition_digest": canonical_digest,
        "campaign_reseed_anchor_digest": campaign_packet.get("RESEED_ANCHOR_DIGEST"),
        "condition_identity_ref": identity_ref,
        "condition_identity_standing": (
            "UNVERIFIED_EXTERNAL_CONTRACT_COORDINATE_BOUND_TO_COMPILER_DEFINITIONS; "
            "CRITERION_IDS_ARE_NOT_FROZEN_BY_THE_CURRENT_CAMPAIGN_COMPILER"
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
            "CAMPAIGN_RESEED_ANCHOR_DIGEST != RESEED_ANCHOR_PAYLOAD_FIELD",
            "CONDITION_IDENTITY_REF != PROVEN_CRITERION_IDENTITY",
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
    packet = value.get("dispatch_packet")
    if not isinstance(packet, Mapping):
        errors.append("dispatch_packet")
    else:
        errors.extend(
            f"dispatch_packet:{item}"
            for item in validate_pinned_dispatch_packet_shape(packet)
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
    expected = _sha({key: item for key, item in value.items() if key != "bridge_digest"})
    if not digest or digest != expected:
        errors.append("bridge_digest")
    return errors


def verify_campaign_v3_life_dispatch_bridge(value: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_dispatch_bridge(value)
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.DISPATCH.BRIDGE.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "errors": errors,
        "source_packet_digest": value.get("source_packet_digest") if isinstance(value, Mapping) else None,
        "canonical_clear_condition_digest": (
            value.get("canonical_clear_condition_digest") if isinstance(value, Mapping) else None
        ),
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
    }
