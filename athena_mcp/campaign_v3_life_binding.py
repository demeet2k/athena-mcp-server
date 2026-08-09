"""Campaign V3 life-aware quest packet compiler.

Pure contract composition only: compilation never executes work, consumes a life or
reseed anchor, issues a reward, grants authority, or promotes Life Loop V1.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .campaign_v3_ledger import PULSE_ARTIFACT
from .campaign_v3_reseed_anchor import SCHEMA_VERSION as RESEED_SCHEMA_VERSION
from .campaign_v3_reseed_anchor import validate_campaign_v3_reseed_anchor

ARTIFACT = "ATHENA.CAMPAIGN.V3.LIFE.QUEST.PACKET.V1"
LIFE_LOOP_ARTIFACT = "ATHENA.STAY_IN_GAME.LIFE_LOOP.V1"
LIFE_LOOP_SOURCE_REPO = "demeet2k/Athena"
LIFE_LOOP_SOURCE_COMMIT = "60a7bc798412088977d7ab9adf16a0e7dca3a1c9"
LIFE_LOOP_REPAIR_HEAD = "18ffcbc21601d71811ae2d81069dbf8e21a82b5b"
LIFE_LOOP_TEST_BLOB = "a6ce3ac0bd94eee62764b2daa22ae0679fdc32d5"
LIFE_LOOP_SCRIPT_BLOB = "c6f35cf39d9f25333ee0c748b5e4bacedbb544a1"
LIFE_LOOP_SCHEMA_BLOB = "93212c61e341ec474332c4daa36e776f735d2491"
LIFE_LOOP_REGISTRY_BLOB = "375c51fa362a110100568a1e0e8d47a279c1b928"
LIFE_LOOP_SOURCE_PR = 284
LIFE_LOOP_SOURCE_ISSUE = 278

BASE_LIVES = 3
MAX_EXTRA_LIVES = 9
EXTRA_LIFE_DELTA = 1

HOLD_CLASSES = (
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "STALE_STATE_HOLD",
    "CAPABILITY_HOLD",
    "HUMAN_VALUE_CHOICE",
    "BUDGET_EXHAUSTED",
    "META_OVERHEAD_COLLAPSE",
    "DUPLICATION_COLLAPSE",
)

PINNED_LIFE_POLICY = {
    "artifact": LIFE_LOOP_ARTIFACT,
    "source": {
        "repo": LIFE_LOOP_SOURCE_REPO,
        "commit": LIFE_LOOP_SOURCE_COMMIT,
        "repair_head": LIFE_LOOP_REPAIR_HEAD,
        "script_blob": LIFE_LOOP_SCRIPT_BLOB,
        "schema_blob": LIFE_LOOP_SCHEMA_BLOB,
        "test_blob": LIFE_LOOP_TEST_BLOB,
        "registry_blob": LIFE_LOOP_REGISTRY_BLOB,
        "pull_request": LIFE_LOOP_SOURCE_PR,
        "issue": LIFE_LOOP_SOURCE_ISSUE,
        "standing": "CANDIDATE_HARDENED_EXACT_SOURCE_TESTED",
        "exact_source_local_tests": "16/16 PASS",
        "github_actions_ci": False,
        "independent_witness": False,
        "canonical_promotion": False,
    },
    "base_lives_per_agent": BASE_LIVES,
    "max_extra_lives": MAX_EXTRA_LIVES,
    "extra_life_delta": EXTRA_LIFE_DELTA,
    "played_result_classes": ["CLEAR", "FAIL_CLEAR"],
    "hold_classes": list(HOLD_CLASSES),
    "extra_life_requires_result": "CLEAR",
    "extra_life_requires_verified_receipt": True,
    "extra_life_requires_witnesses": True,
    "extra_life_self_scored_allowed": False,
    "reseed_schema_version": RESEED_SCHEMA_VERSION,
    "reseed_anchor_replay_guard_required": True,
    "reseed_anchor_agent_binding_required": True,
    "reseed_anchor_quest_binding_required": True,
    "current_git_positions_match_required_at_play": True,
    "platform_counter_reset_claimed": False,
}

FORBIDDEN_CANDIDATE_KEYS = {
    "authority",
    "execution_authority",
    "scheduler_ready",
    "provider_authority",
    "verified",
    "reward_issued",
    "extra_life_issued",
    "extra_lives_minted",
    "platform_counter_reset_claimed",
    "token_counter_reset",
    "context_counter_reset",
    "quota_reset",
    "campaign_success",
    "canonical_promotion",
}
ALLOWED_CANDIDATE_KEYS = {"requested", "candidate_id", "evidence_refs"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    basis = {k: v for k, v in pulse.items() if k != "pulse_digest"}
    return digest == _sha(basis)


def _residual_action(pulse: Mapping[str, Any], residual_step: int) -> Mapping[str, Any] | None:
    for action in pulse.get("actions") or []:
        try:
            step = int(action.get("step"))
        except (TypeError, ValueError):
            continue
        if step == int(residual_step):
            return action
    return None


def _normalize_clear_conditions(clear_conditions: Sequence[Any]) -> list[str]:
    """Freeze ordered public clear-condition definitions.

    Life Loop execution later receives one observed boolean per frozen condition.
    This packet compiler never converts those future outcomes into pre-play facts.
    """
    if not isinstance(clear_conditions, Sequence) or isinstance(clear_conditions, (str, bytes)):
        raise ValueError("clear_conditions must be a non-empty ordered list")
    if not clear_conditions:
        raise ValueError("clear_conditions must be a non-empty ordered list")
    out: list[str] = []
    for raw_value in clear_conditions:
        if isinstance(raw_value, bool):
            raise ValueError("clear_conditions must declare conditions, not observed booleans")
        value = str(raw_value or "").strip()
        if not value:
            raise ValueError("clear condition definitions must be non-empty")
        if value in out:
            raise ValueError(f"duplicate clear condition: {value}")
        out.append(value)
    return out


def _clear_condition_digest(*, quest_id: str, quest_version: str, clear_conditions: Sequence[str]) -> str:
    return _sha(
        {
            "quest_id": quest_id,
            "quest_version": quest_version,
            "hard_gate_required": True,
            "ordered_clear_condition_contract": list(clear_conditions),
            "observed_clear_results_bound_later": True,
        }
    )

def _life_policy() -> dict[str, Any]:
    policy = deepcopy(PINNED_LIFE_POLICY)
    policy["policy_digest"] = _sha(PINNED_LIFE_POLICY)
    return policy


def _target_version_map(anchor: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in anchor.get("target_versions") or []:
        if not isinstance(row, Mapping):
            continue
        target_id = str(row.get("id") or "").strip()
        version = str(row.get("version") or "").strip()
        if target_id and version:
            if target_id in result:
                raise ValueError(f"duplicate reseed target version: {target_id}")
            result[target_id] = version
    return result


def _anchor_digest(anchor: Mapping[str, Any]) -> str:
    return _sha(anchor)


def _normalize_reward_candidate(candidate: Mapping[str, Any] | None) -> dict[str, Any]:
    if candidate is None:
        candidate = {}
    if not isinstance(candidate, Mapping):
        raise ValueError("extra_life_reward_candidate must be an object")
    unknown = sorted(set(candidate) - ALLOWED_CANDIDATE_KEYS)
    forbidden = sorted(set(candidate) & FORBIDDEN_CANDIDATE_KEYS)
    if forbidden:
        raise ValueError("forbidden reward/authority fields: " + ",".join(forbidden))
    if unknown:
        raise ValueError("unknown extra-life candidate fields: " + ",".join(unknown))

    requested = candidate.get("requested", False)
    if not isinstance(requested, bool):
        raise ValueError("extra-life requested must be boolean")

    candidate_id = str(candidate.get("candidate_id") or "").strip() or None
    raw_refs = candidate.get("evidence_refs") or []
    if not isinstance(raw_refs, Sequence) or isinstance(raw_refs, (str, bytes)):
        raise ValueError("extra-life evidence_refs must be a list")
    refs: list[str] = []
    for raw in raw_refs:
        ref = str(raw or "").strip()
        if ref and ref not in refs:
            refs.append(ref)

    eligible = bool(requested and candidate_id and refs)
    standing = "CANDIDATE_ELIGIBLE_NOT_ISSUED" if eligible else "NOT_ELIGIBLE"
    reasons: list[str] = []
    if requested and not candidate_id:
        reasons.append("CANDIDATE_ID_REQUIRED")
    if requested and not refs:
        reasons.append("EVIDENCE_REFERENCE_REQUIRED")

    return {
        "eligible": eligible,
        "eligibility_scope": "PRE_CLEAR_CANDIDATE_SIGNAL_ONLY",
        "issuance_eligible": False,
        "standing": standing,
        "candidate_id": candidate_id,
        "evidence_refs": refs,
        "requires_result": "CLEAR",
        "verified_receipt_required": True,
        "witnesses_required": True,
        "self_scored_allowed": False,
        "reward_delta_if_independently_issued": EXTRA_LIFE_DELTA,
        "reward_issued": False,
        "reasons": reasons,
    }


def _hold(
    *,
    status: str,
    quest_id: str | None,
    quest_version: str | None,
    failures: Sequence[str],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "status": status,
        "quest_id": quest_id,
        "quest_version": quest_version,
        "failures": list(failures),
        "execution_authority": False,
        "scheduler_ready": False,
        "provider_authority": False,
        "campaign_success_claim_allowed": False,
        "platform_counter_reset_claimed": False,
        "life_loop_canonical_promotion": False,
        "reseed_anchor_consumption_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "work_executed": False,
        **extra,
    }


def compile_campaign_v3_life_quest_packet(
    *,
    pulse: Mapping[str, Any],
    residual_step: int,
    campaign_id: str,
    branch_id: str,
    agent_coordinate_name: str,
    quest_id: str,
    quest_version: str,
    clear_conditions: Sequence[Any],
    reseed_anchor: Mapping[str, Any],
    extra_life_reward_candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one life-aware Campaign V3 quest packet.

    This function is pure. It does not claim, execute, reseed, consume an
    anchor/life, issue an extra life, grant scheduler/provider authority, or
    promote the semantic Life Loop candidate.
    """
    campaign_id = str(campaign_id or "").strip()
    branch_id = str(branch_id or "").strip()
    agent_coordinate_name = str(agent_coordinate_name or "").strip()
    quest_id = str(quest_id or "").strip()
    quest_version = str(quest_version or "").strip()
    if not isinstance(pulse, Mapping):
        return _hold(
            status="HOLD_INVALID_PACKET_INPUT",
            quest_id=quest_id or None,
            quest_version=quest_version or None,
            failures=["PULSE_REQUIRED"],
            campaign_id=campaign_id or None,
            branch_id=branch_id or None,
            agent_coordinate_name=agent_coordinate_name or None,
        )
    try:
        residual_step = int(residual_step)
    except (TypeError, ValueError):
        return _hold(
            status="HOLD_INVALID_PACKET_INPUT",
            quest_id=quest_id or None,
            quest_version=quest_version or None,
            failures=["RESIDUAL_STEP_INVALID"],
        )

    failures: list[str] = []
    if not campaign_id:
        failures.append("CAMPAIGN_ID_REQUIRED")
    if not branch_id:
        failures.append("BRANCH_ID_REQUIRED")
    if not agent_coordinate_name:
        failures.append("AGENT_COORDINATE_NAME_REQUIRED")
    if not quest_id:
        failures.append("QUEST_ID_REQUIRED")
    if not quest_version:
        failures.append("QUEST_VERSION_REQUIRED")
    if pulse.get("artifact") != PULSE_ARTIFACT:
        failures.append("PULSE_ARTIFACT_INVALID")
    if not _pulse_integrity(pulse):
        failures.append("PULSE_DIGEST_INVALID")
    if pulse.get("execution_authorized") is not False:
        failures.append("PULSE_AUTHORITY_FIREWALL_MISSING")
    coordinates = pulse.get("current_coordinates")
    if not isinstance(coordinates, Mapping) or not str(coordinates.get("git_head") or "").strip():
        failures.append("PULSE_GIT_HEAD_REQUIRED")

    residual_set: set[int] = set()
    for raw in pulse.get("residual_steps") or []:
        try:
            residual_set.add(int(raw))
        except (TypeError, ValueError):
            failures.append("PULSE_RESIDUAL_STEPS_INVALID")
            break
    action = _residual_action(pulse, residual_step)
    if residual_step not in residual_set:
        failures.append("STEP_NOT_RESIDUAL")
    if action is None:
        failures.append("RESIDUAL_ACTION_MISSING")
    elif str(action.get("current_state") or "").upper() != "RESIDUAL":
        failures.append("ACTION_NOT_RESIDUAL")

    try:
        normalized_clear = _normalize_clear_conditions(clear_conditions)
    except ValueError as exc:
        failures.append(f"CLEAR_CONDITIONS_INVALID:{exc}")
        normalized_clear = []

    if not isinstance(reseed_anchor, Mapping):
        failures.append("RESEED_ANCHOR_REQUIRED")
        anchor_errors = ["anchor_not_object"]
    else:
        try:
            anchor_errors = list(validate_campaign_v3_reseed_anchor(reseed_anchor))
        except Exception as exc:  # fail closed at the adapter membrane
            anchor_errors = [f"validator_exception:{type(exc).__name__}"]
        if reseed_anchor.get("platform_counter_reset_claimed") is not False:
            anchor_errors = list(anchor_errors) + ["platform_counter_reset_claimed_must_be_false"]

    if anchor_errors:
        failures.extend(f"RESEED_ANCHOR_INVALID:{error}" for error in anchor_errors)

    target_versions: dict[str, str] = {}
    if isinstance(reseed_anchor, Mapping) and not anchor_errors:
        try:
            target_versions = _target_version_map(reseed_anchor)
        except ValueError as exc:
            failures.append(f"RESEED_ANCHOR_INVALID:{exc}")
    if isinstance(reseed_anchor, Mapping) and not anchor_errors:
        expected_pulse = str(pulse.get("pulse_digest") or "")
        if target_versions.get("campaign_v3.pulse_digest") != expected_pulse:
            failures.append("RESEED_ANCHOR_PULSE_BINDING_MISMATCH")
        if target_versions.get("campaign_v3.campaign_id") != campaign_id:
            failures.append("RESEED_ANCHOR_CAMPAIGN_BINDING_MISMATCH")
        if target_versions.get(quest_id) != quest_version:
            failures.append("RESEED_ANCHOR_QUEST_BINDING_MISMATCH")
        if str(reseed_anchor.get("agent_coordinate_name") or "") != agent_coordinate_name:
            failures.append("RESEED_ANCHOR_AGENT_BINDING_MISMATCH")

    try:
        reward_eligibility = _normalize_reward_candidate(extra_life_reward_candidate)
    except ValueError as exc:
        failures.append(f"EXTRA_LIFE_CANDIDATE_INVALID:{exc}")
        reward_eligibility = _normalize_reward_candidate(None)

    if failures:
        status = (
            "HOLD_INVALID_RESEED_ANCHOR"
            if any(item.startswith("RESEED_ANCHOR") for item in failures)
            else "HOLD_INVALID_PACKET_INPUT"
        )
        return _hold(
            status=status,
            quest_id=quest_id or None,
            quest_version=quest_version or None,
            failures=failures,
            campaign_id=campaign_id or None,
            branch_id=branch_id or None,
            agent_coordinate_name=agent_coordinate_name or None,
            residual_step=residual_step,
            EXTRA_LIFE_REWARD_ELIGIBILITY=reward_eligibility,
        )

    clear_digest = _clear_condition_digest(
        quest_id=quest_id,
        quest_version=quest_version,
        clear_conditions=normalized_clear,
    )
    policy = _life_policy()
    anchor_copy = deepcopy(dict(reseed_anchor))
    anchor_copy["anchor_digest"] = _anchor_digest(reseed_anchor)

    packet = {
        "artifact": ARTIFACT,
        "status": "COMPILED",
        "campaign": {
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "agent_coordinate_name": agent_coordinate_name,
            "residual_step": residual_step,
        },
        "quest": {
            "quest_id": quest_id,
            "quest_version": quest_version,
            "historical_action_text": str((action or {}).get("text") or ""),
            "historical_action_horizon": str((action or {}).get("horizon") or ""),
        },
        "pulse_binding": {
            "artifact": PULSE_ARTIFACT,
            "pulse_digest": str(pulse["pulse_digest"]),
            "ledger_digest": str(pulse.get("ledger_digest") or ""),
            "pulse_index": int(pulse.get("pulse_index") or 0),
            "git_head": str(coordinates.get("git_head")),
        },
        "CLEAR_CONDITIONS": normalized_clear,
        "CLEAR_CONDITION_DIGEST": clear_digest,
        "CLEAR_RESULT_VECTOR": None,
        "LIFE_POLICY": policy,
        "RESEED_ANCHOR": anchor_copy,
        "EXTRA_LIFE_REWARD_ELIGIBILITY": reward_eligibility,
        "execution_authority": False,
        "scheduler_ready": False,
        "provider_authority": False,
        "campaign_success_claim_allowed": False,
        "platform_counter_reset_claimed": False,
        "life_loop_canonical_promotion": False,
        "reseed_anchor_consumption_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "work_executed": False,
        "laws": [
            "QUEST_PACKET != EXECUTION_AUTHORITY",
            "LIFE_POLICY != CANONICAL_PROMOTION",
            "RESEED_ANCHOR != PLATFORM_COUNTER_RESET",
            "PACKET_COMPILE != RESEED_ANCHOR_CONSUMPTION",
            "PACKET_COMPILE != LIFE_CONSUMPTION",
            "ANCHOR_REPLAY_FRESHNESS_VERIFIED_AT_PLAY != PACKET_COMPILE",
            "EXTRA_LIFE_REWARD_ELIGIBILITY != EXTRA_LIFE_ISSUED",
            "CLEAR_CONDITION_DIGEST != CLEAR_WITNESS",
            "COMPILED_PACKET != PLAYED_ATTEMPT",
            "PLAYED_ATTEMPT != VERIFIED_CLEAR",
        ],
    }
    packet["packet_digest"] = _sha({k: v for k, v in packet.items() if k != "packet_digest"})
    return packet


def validate_campaign_v3_life_quest_packet(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet_not_object"]
    if packet.get("artifact") != ARTIFACT:
        errors.append("artifact")
    if packet.get("status") != "COMPILED":
        errors.append("status")

    for key in (
        "execution_authority",
        "scheduler_ready",
        "provider_authority",
        "campaign_success_claim_allowed",
        "platform_counter_reset_claimed",
        "life_loop_canonical_promotion",
        "reseed_anchor_consumption_authority",
        "life_consumption_authority",
        "reward_issuance_authority",
        "work_executed",
    ):
        if packet.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    campaign = packet.get("campaign")
    if not isinstance(campaign, Mapping):
        errors.append("campaign")
    else:
        if not str(campaign.get("campaign_id") or ""):
            errors.append("campaign_id")
        if not str(campaign.get("branch_id") or ""):
            errors.append("branch_id")
        if not str(campaign.get("agent_coordinate_name") or ""):
            errors.append("agent_coordinate_name")
        try:
            if int(campaign.get("residual_step")) <= 0:
                errors.append("residual_step")
        except (TypeError, ValueError):
            errors.append("residual_step")

    quest = packet.get("quest")
    conditions = packet.get("CLEAR_CONDITIONS")
    if not isinstance(quest, Mapping) or not quest.get("quest_id") or not quest.get("quest_version"):
        errors.append("quest")
    else:
        try:
            normalized = _normalize_clear_conditions(conditions)
            expected_clear_digest = _clear_condition_digest(
                quest_id=str(quest["quest_id"]),
                quest_version=str(quest["quest_version"]),
                clear_conditions=normalized,
            )
            if packet.get("CLEAR_CONDITION_DIGEST") != expected_clear_digest:
                errors.append("clear_condition_digest")
        except ValueError:
            errors.append("clear_conditions")

    if packet.get("CLEAR_RESULT_VECTOR") is not None:
        errors.append("clear_result_vector_must_be_unobserved")

    policy = packet.get("LIFE_POLICY")
    expected_policy = _life_policy()
    if policy != expected_policy:
        errors.append("life_policy")

    anchor = packet.get("RESEED_ANCHOR")
    if not isinstance(anchor, Mapping):
        errors.append("reseed_anchor")
    else:
        anchor_basis = {k: v for k, v in anchor.items() if k != "anchor_digest"}
        if anchor.get("anchor_digest") != _anchor_digest(anchor_basis):
            errors.append("reseed_anchor_digest")
        try:
            anchor_errors = list(validate_campaign_v3_reseed_anchor(anchor_basis))
        except Exception as exc:
            anchor_errors = [f"validator_exception:{type(exc).__name__}"]
        if anchor_errors:
            errors.extend(f"reseed_anchor:{item}" for item in anchor_errors)
        pulse_binding = packet.get("pulse_binding")
        if isinstance(campaign, Mapping) and isinstance(pulse_binding, Mapping):
            try:
                targets = _target_version_map(anchor_basis)
            except ValueError as exc:
                errors.append(f"reseed_anchor:{exc}")
                targets = {}
            if targets.get("campaign_v3.pulse_digest") != str(pulse_binding.get("pulse_digest") or ""):
                errors.append("reseed_anchor_pulse_binding")
            if targets.get("campaign_v3.campaign_id") != str(campaign.get("campaign_id") or ""):
                errors.append("reseed_anchor_campaign_binding")
            if isinstance(quest, Mapping):
                if targets.get(str(quest.get("quest_id") or "")) != str(quest.get("quest_version") or ""):
                    errors.append("reseed_anchor_quest_binding")
            if str(anchor_basis.get("agent_coordinate_name") or "") != str(campaign.get("agent_coordinate_name") or ""):
                errors.append("reseed_anchor_agent_binding")

    eligibility = packet.get("EXTRA_LIFE_REWARD_ELIGIBILITY")
    if not isinstance(eligibility, Mapping):
        errors.append("extra_life_reward_eligibility")
    else:
        if eligibility.get("reward_issued") is not False:
            errors.append("reward_issued_must_be_false")
        if eligibility.get("issuance_eligible") is not False:
            errors.append("issuance_eligible_must_be_false_before_clear")
        if eligibility.get("eligibility_scope") != "PRE_CLEAR_CANDIDATE_SIGNAL_ONLY":
            errors.append("eligibility_scope")
        if eligibility.get("self_scored_allowed") is not False:
            errors.append("self_scored_allowed_must_be_false")
        if eligibility.get("verified_receipt_required") is not True:
            errors.append("verified_receipt_required_must_be_true")
        if eligibility.get("witnesses_required") is not True:
            errors.append("witnesses_required_must_be_true")
        if eligibility.get("eligible") is True:
            if not eligibility.get("candidate_id") or not eligibility.get("evidence_refs"):
                errors.append("eligible_candidate_requires_identity_and_evidence_refs")
            if eligibility.get("standing") != "CANDIDATE_ELIGIBLE_NOT_ISSUED":
                errors.append("eligible_candidate_standing")

    pulse_binding = packet.get("pulse_binding")
    if not isinstance(pulse_binding, Mapping):
        errors.append("pulse_binding")
    else:
        if pulse_binding.get("artifact") != PULSE_ARTIFACT:
            errors.append("pulse_binding_artifact")
        if not pulse_binding.get("pulse_digest") or not pulse_binding.get("git_head"):
            errors.append("pulse_binding_identity")

    digest = str(packet.get("packet_digest") or "")
    expected_digest = _sha({k: v for k, v in packet.items() if k != "packet_digest"})
    if not digest or digest != expected_digest:
        errors.append("packet_digest")

    return errors


def verify_campaign_v3_life_quest_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_quest_packet(packet)
    return {
        "artifact": "ATHENA.CAMPAIGN.V3.LIFE.QUEST.PACKET.VERIFY.V1",
        "status": "PASS" if not errors else "HOLD",
        "packet_digest": packet.get("packet_digest") if isinstance(packet, Mapping) else None,
        "errors": errors,
        "execution_authority": False,
        "reward_authority": False,
        "platform_counter_reset_claimed": False,
    }
