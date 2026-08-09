"""Campaign V3 route-selection / attempt observation identity bridge.

ASG-008 fills one narrow instrumentation gap: preserve the selected route/context
cell across the existing compiled-packet -> attempt-identity -> Dispatch-bridge
lineage. It does NOT prove semantic execution, verifier success, Life consumption,
or route-risk standing.

The pinned Campaign/Dispatch schemas are never mutated. Route metadata is sibling
public identity/provenance only.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from .campaign_v3_life_attempt_identity import validate_campaign_v3_life_attempt_identity
from .campaign_v3_life_binding import validate_campaign_v3_life_quest_packet
from .campaign_v3_life_dispatch_bridge import validate_campaign_v3_life_dispatch_bridge
from .campaign_v3_life_execution_provenance import ARTIFACT as EXECUTION_PROVENANCE_ARTIFACT

SELECTION_ARTIFACT = "ATHENA.CAMPAIGN.V3.ROUTE.SELECTION.V1"
ATTEMPT_ARTIFACT = "ATHENA.CAMPAIGN.V3.ROUTE.ATTEMPT.V1"
OBSERVATION_ARTIFACT = "ATHENA.CAMPAIGN.V3.ROUTE.OBSERVATION.V1"
DIGEST_PREFIX = "sha256:"

REQUIRED_ROUTE_CONTEXT_KEYS = (
    "selected_route_id",
    "route_family_id",
    "minigame",
    "objective_family_id",
    "task_family",
    "capability_profile_digest",
    "toolset_digest",
    "difficulty_band",
)


class CampaignV3RouteObservationError(ValueError):
    pass


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _digest(value: Any) -> str:
    return DIGEST_PREFIX + _sha(value)


def _nonblank(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CampaignV3RouteObservationError(f"{name} must be a non-empty string")
    return value.strip()


def normalize_route_context(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CampaignV3RouteObservationError("route_context must be an object")
    out = copy.deepcopy(dict(value))
    missing = [key for key in REQUIRED_ROUTE_CONTEXT_KEYS if key not in out]
    if missing:
        raise CampaignV3RouteObservationError(
            "route_context missing required fields: " + ",".join(missing)
        )
    for key in REQUIRED_ROUTE_CONTEXT_KEYS:
        out[key] = _nonblank(out.get(key), f"route_context.{key}")
    if not out["capability_profile_digest"].startswith("sha256:"):
        raise CampaignV3RouteObservationError("capability_profile_digest must be sha256-addressed")
    if not out["toolset_digest"].startswith("sha256:"):
        raise CampaignV3RouteObservationError("toolset_digest must be sha256-addressed")
    return out


def route_context_digest(value: Mapping[str, Any]) -> str:
    return _digest(normalize_route_context(value))


def _packet_identity(packet: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_quest_packet(packet)
    if errors:
        raise CampaignV3RouteObservationError(
            "invalid Campaign V3 Life quest packet: " + ";".join(errors)
        )
    packet_digest = _nonblank(packet.get("packet_digest"), "packet_digest")
    campaign = packet.get("campaign")
    quest = packet.get("quest")
    pulse = packet.get("pulse")
    if not isinstance(campaign, Mapping) or not isinstance(quest, Mapping):
        raise CampaignV3RouteObservationError("campaign/quest identity missing")
    if not isinstance(pulse, Mapping):
        pulse = {}
    return {
        "packet_digest": packet_digest,
        "campaign_id": campaign.get("campaign_id"),
        "branch_id": campaign.get("branch_id"),
        "agent_id": campaign.get("agent_coordinate_name"),
        "quest_id": quest.get("quest_id"),
        "quest_version": quest.get("quest_version"),
        "stage_id": quest.get("stage_id"),
        "step_id": quest.get("step_id"),
        "residual_step_id": quest.get("residual_step_id"),
        "pulse_index": pulse.get("pulse_index"),
    }


def bind_campaign_v3_route_selection(
    *,
    campaign_packet: Mapping[str, Any],
    selected_action_id: str,
    route_context: Mapping[str, Any],
    objective_digest: str,
    source_head: str,
) -> dict[str, Any]:
    """Freeze route identity against an already compiled packet; do not execute it."""
    identity = _packet_identity(campaign_packet)
    action_id = _nonblank(selected_action_id, "selected_action_id")
    objective = _nonblank(objective_digest, "objective_digest")
    if not objective.startswith("sha256:"):
        raise CampaignV3RouteObservationError("objective_digest must be sha256-addressed")
    head = _nonblank(source_head, "source_head")
    context = normalize_route_context(route_context)
    context_digest = _digest(context)
    selection_payload = {
        "packet_digest": identity["packet_digest"],
        "selected_action_id": action_id,
        "objective_digest": objective,
        "route_context_digest": context_digest,
    }
    out = {
        "artifact": SELECTION_ARTIFACT,
        "status": "BOUND_SELECTION_IDENTITY",
        **identity,
        "selected_action_id": action_id,
        "objective_digest": objective,
        "route_context": context,
        "route_context_digest": context_digest,
        "route_selection_id": "ROUTE-SELECTION-" + _sha(selection_payload)[:32],
        "source_head": head,
        "semantic_execution_proven": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_authority": False,
        "evidence_authority": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "ROUTE_SELECTION_ID != ATTEMPT_ID != LIFE_EVENT_ID",
            "ROUTE_CONTEXT != EXECUTION_PROOF",
            "ROUTE_BINDING != QUEST_ADMISSION_AUTHORITY",
            "SELECTION_REPLAY != NEW_PLAY",
        ],
    }
    out["selection_digest"] = _digest(
        {key: value for key, value in out.items() if key != "selection_digest"}
    )
    return out


def validate_campaign_v3_route_selection(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["selection_not_object"]
    errors: list[str] = []
    if value.get("artifact") != SELECTION_ARTIFACT:
        errors.append("artifact")
    if value.get("status") != "BOUND_SELECTION_IDENTITY":
        errors.append("status")
    try:
        context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError as exc:
        errors.append(f"route_context:{exc}")
        context = None
    if context is not None and value.get("route_context_digest") != _digest(context):
        errors.append("route_context_digest")
    for key in ("packet_digest", "selected_action_id", "objective_digest", "route_selection_id", "source_head"):
        if not isinstance(value.get(key), str) or not value.get(key):
            errors.append(key)
    expected_selection_id = None
    if context is not None and isinstance(value.get("packet_digest"), str):
        expected_selection_id = "ROUTE-SELECTION-" + _sha(
            {
                "packet_digest": value.get("packet_digest"),
                "selected_action_id": value.get("selected_action_id"),
                "objective_digest": value.get("objective_digest"),
                "route_context_digest": value.get("route_context_digest"),
            }
        )[:32]
    if expected_selection_id and value.get("route_selection_id") != expected_selection_id:
        errors.append("route_selection_id")
    for key in (
        "semantic_execution_proven",
        "execution_authority",
        "life_consumption_authority",
        "reward_authority",
        "evidence_authority",
        "platform_counter_reset_claimed",
    ):
        if value.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    digest = value.get("selection_digest")
    if digest != _digest({key: item for key, item in value.items() if key != "selection_digest"}):
        errors.append("selection_digest")
    return errors


def bind_campaign_v3_route_attempt(
    *,
    route_selection: Mapping[str, Any],
    attempt_identity: Mapping[str, Any],
    existing_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Join one host-attempt identity to the frozen route selection."""
    selection_errors = validate_campaign_v3_route_selection(route_selection)
    if selection_errors:
        raise CampaignV3RouteObservationError(
            "invalid route selection: " + ";".join(selection_errors)
        )
    attempt_errors = validate_campaign_v3_life_attempt_identity(attempt_identity)
    if attempt_errors:
        raise CampaignV3RouteObservationError(
            "invalid Life attempt identity: " + ";".join(attempt_errors)
        )
    if attempt_identity.get("packet_digest") != route_selection.get("packet_digest"):
        raise CampaignV3RouteObservationError("attempt packet_digest does not match route selection")
    attempt_id = _nonblank(attempt_identity.get("attempt_id"), "attempt_id")
    execution_event_id = _nonblank(attempt_identity.get("execution_event_id"), "execution_event_id")
    attempt_payload = {
        "route_selection_id": route_selection["route_selection_id"],
        "attempt_id": attempt_id,
        "packet_digest": route_selection["packet_digest"],
    }
    route_attempt_id = "ROUTE-ATTEMPT-" + _sha(attempt_payload)[:32]

    if existing_binding is not None:
        existing_errors = validate_campaign_v3_route_attempt(existing_binding)
        if existing_errors:
            raise CampaignV3RouteObservationError(
                "invalid existing route-attempt binding: " + ";".join(existing_errors)
            )
        if existing_binding.get("attempt_id") == attempt_id:
            if existing_binding.get("route_selection_id") != route_selection.get("route_selection_id"):
                raise CampaignV3RouteObservationError(
                    "attempt_id already bound to a conflicting route selection"
                )
            return copy.deepcopy(dict(existing_binding))

    out = {
        "artifact": ATTEMPT_ARTIFACT,
        "status": "BOUND_ROUTE_ATTEMPT_IDENTITY",
        "route_selection_id": route_selection["route_selection_id"],
        "route_selection_digest": route_selection["selection_digest"],
        "route_attempt_id": route_attempt_id,
        "packet_digest": route_selection["packet_digest"],
        "attempt_id": attempt_id,
        "execution_event_id": execution_event_id,
        "selected_action_id": route_selection["selected_action_id"],
        "objective_digest": route_selection["objective_digest"],
        "route_context": copy.deepcopy(route_selection["route_context"]),
        "route_context_digest": route_selection["route_context_digest"],
        "campaign_id": route_selection.get("campaign_id"),
        "branch_id": route_selection.get("branch_id"),
        "agent_id": route_selection.get("agent_id"),
        "quest_id": route_selection.get("quest_id"),
        "quest_version": route_selection.get("quest_version"),
        "stage_id": route_selection.get("stage_id"),
        "step_id": route_selection.get("step_id"),
        "residual_step_id": route_selection.get("residual_step_id"),
        "pulse_index": route_selection.get("pulse_index"),
        "source_head": route_selection.get("source_head"),
        "semantic_execution_proven": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_authority": False,
        "evidence_authority": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "PACKET_DIGEST != ROUTE_SELECTION_ID != ATTEMPT_ID != ROUTE_ATTEMPT_ID != LIFE_EVENT_ID",
            "ATTEMPT_ID != SEMANTIC_EXECUTION_PROOF",
            "ROUTE_ATTEMPT_IDENTITY != PLAY_SETTLEMENT_AUTHORITY",
        ],
    }
    out["route_attempt_digest"] = _digest(
        {key: value for key, value in out.items() if key != "route_attempt_digest"}
    )
    return out


def validate_campaign_v3_route_attempt(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["route_attempt_not_object"]
    errors: list[str] = []
    if value.get("artifact") != ATTEMPT_ARTIFACT:
        errors.append("artifact")
    if value.get("status") != "BOUND_ROUTE_ATTEMPT_IDENTITY":
        errors.append("status")
    try:
        context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError as exc:
        errors.append(f"route_context:{exc}")
        context = None
    if context is not None and value.get("route_context_digest") != _digest(context):
        errors.append("route_context_digest")
    for key in ("route_selection_id", "route_attempt_id", "packet_digest", "attempt_id", "execution_event_id"):
        if not isinstance(value.get(key), str) or not value.get(key):
            errors.append(key)
    expected = None
    if all(isinstance(value.get(key), str) and value.get(key) for key in ("route_selection_id", "attempt_id", "packet_digest")):
        expected = "ROUTE-ATTEMPT-" + _sha(
            {
                "route_selection_id": value["route_selection_id"],
                "attempt_id": value["attempt_id"],
                "packet_digest": value["packet_digest"],
            }
        )[:32]
    if expected and value.get("route_attempt_id") != expected:
        errors.append("route_attempt_id")
    for key in (
        "semantic_execution_proven",
        "execution_authority",
        "life_consumption_authority",
        "reward_authority",
        "evidence_authority",
        "platform_counter_reset_claimed",
    ):
        if value.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    digest = value.get("route_attempt_digest")
    if digest != _digest({key: item for key, item in value.items() if key != "route_attempt_digest"}):
        errors.append("route_attempt_digest")
    return errors


def project_campaign_v3_route_observation(
    *,
    route_attempt: Mapping[str, Any],
    dispatch_bridge: Mapping[str, Any],
    execution_provenance: Mapping[str, Any],
    observed_at: int,
    routed_evidence_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Project correlated route/result telemetry without fabricating ASG-007 standing."""
    attempt_errors = validate_campaign_v3_route_attempt(route_attempt)
    if attempt_errors:
        raise CampaignV3RouteObservationError(
            "invalid route-attempt binding: " + ";".join(attempt_errors)
        )
    dispatch_errors = validate_campaign_v3_life_dispatch_bridge(dispatch_bridge)
    if dispatch_errors:
        raise CampaignV3RouteObservationError(
            "invalid Dispatch bridge: " + ";".join(dispatch_errors)
        )
    if dispatch_bridge.get("source_packet_digest") != route_attempt.get("packet_digest"):
        raise CampaignV3RouteObservationError("Dispatch source packet does not match route attempt")
    compat = dispatch_bridge.get("attempt_compatibility")
    if not isinstance(compat, Mapping) or compat.get("attempt_id") != route_attempt.get("attempt_id"):
        raise CampaignV3RouteObservationError("Dispatch attempt metadata does not match route attempt")
    if not isinstance(execution_provenance, Mapping) or execution_provenance.get("artifact") != EXECUTION_PROVENANCE_ARTIFACT:
        raise CampaignV3RouteObservationError("execution_provenance artifact mismatch")
    if execution_provenance.get("execution_event_id") != route_attempt.get("execution_event_id"):
        raise CampaignV3RouteObservationError("execution provenance event does not match route attempt")
    if execution_provenance.get("platform_counter_reset_claimed") is not False:
        raise CampaignV3RouteObservationError("execution provenance platform-reset claim forbidden")
    if not isinstance(observed_at, int) or isinstance(observed_at, bool) or observed_at < 0:
        raise CampaignV3RouteObservationError("observed_at must be a nonnegative integer")

    refs: list[str] = []
    if routed_evidence_refs is not None:
        if not isinstance(routed_evidence_refs, Sequence) or isinstance(routed_evidence_refs, (str, bytes)):
            raise CampaignV3RouteObservationError("routed_evidence_refs must be a list")
        for raw in routed_evidence_refs:
            refs.append(_nonblank(raw, "routed_evidence_ref"))
        if len(refs) != len(set(refs)):
            raise CampaignV3RouteObservationError("duplicate routed_evidence_ref")

    dispatch_packet = dispatch_bridge.get("dispatch_packet")
    if not isinstance(dispatch_packet, Mapping):
        raise CampaignV3RouteObservationError("Dispatch packet missing")
    result_class = dispatch_packet.get("result_class")
    translated_executed = dispatch_packet.get("executed") is True
    played_observed = translated_executed and result_class in {"CLEAR", "FAIL_CLEAR"}
    semantic_execution_proven = execution_provenance.get("semantic_execution_proven") is True

    # V1 intentionally cannot promote to ASG-007 eligibility. Even if a future caller
    # supplies routed witnesses, current execution provenance has no trusted executor
    # profile and this projection has no authoritative Life-reducer result.
    if not semantic_execution_proven:
        eligibility = "NOT_ELIGIBLE_UNPROVEN_EXECUTION"
    else:
        eligibility = "NOT_ELIGIBLE_MISSING_AUTHORITATIVE_LIFE_RESULT"

    out = {
        "artifact": OBSERVATION_ARTIFACT,
        "status": "INSTRUMENTED_UNPROVEN",
        "observed_at": observed_at,
        "route_attempt_id": route_attempt["route_attempt_id"],
        "route_selection_id": route_attempt["route_selection_id"],
        "packet_digest": route_attempt["packet_digest"],
        "attempt_id": route_attempt["attempt_id"],
        "execution_event_id": route_attempt["execution_event_id"],
        "campaign_id": route_attempt.get("campaign_id"),
        "branch_id": route_attempt.get("branch_id"),
        "agent_id": route_attempt.get("agent_id"),
        "quest_id": route_attempt.get("quest_id"),
        "quest_version": route_attempt.get("quest_version"),
        "residual_step_id": route_attempt.get("residual_step_id"),
        "pulse_index": route_attempt.get("pulse_index"),
        "selected_action_id": route_attempt["selected_action_id"],
        "objective_digest": route_attempt["objective_digest"],
        "route_context": copy.deepcopy(route_attempt["route_context"]),
        "route_context_digest": route_attempt["route_context_digest"],
        "result_class": result_class,
        "dispatch_translated_executed": translated_executed,
        "played_observed_by_dispatch_translation": played_observed,
        "life_consumed": None,
        "semantic_execution_proven": semantic_execution_proven,
        "execution_evidence_class": execution_provenance.get("evidence_class"),
        "routed_evidence_refs": refs,
        "routed_evidence_consumed": False,
        "verified": False,
        "self_scored": False,
        "asg007_eligible": False,
        "asg007_eligibility_status": eligibility,
        "asg007_candidate_receipt": None,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_authority": False,
        "evidence_authority": False,
        "platform_counter_reset_claimed": False,
        "laws": [
            "ROUTE_INSTRUMENTATION != EXECUTION_PROOF",
            "DISPATCH_TRANSLATION != EXECUTED_PLAY_SETTLEMENT",
            "ROUTED_EVIDENCE != CONSUMED_EVIDENCE",
            "ATTEMPT_ID != SEMANTIC_EXECUTION_PROOF",
            "RESULT_CLASS != LIFE_CONSUMPTION_RECEIPT",
            "ASG007_ELIGIBILITY_REQUIRES_INDEPENDENT_EXECUTION_AND_LIFE_EVIDENCE",
        ],
    }
    out["observation_digest"] = _digest(
        {key: value for key, value in out.items() if key != "observation_digest"}
    )
    return out


def validate_campaign_v3_route_observation(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["observation_not_object"]
    errors: list[str] = []
    if value.get("artifact") != OBSERVATION_ARTIFACT:
        errors.append("artifact")
    if value.get("status") != "INSTRUMENTED_UNPROVEN":
        errors.append("status")
    try:
        context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError as exc:
        errors.append(f"route_context:{exc}")
        context = None
    if context is not None and value.get("route_context_digest") != _digest(context):
        errors.append("route_context_digest")
    if value.get("life_consumed") is not None:
        errors.append("life_consumed_must_remain_unknown")
    if value.get("verified") is not False:
        errors.append("verified_must_be_false")
    if value.get("asg007_eligible") is not False or value.get("asg007_candidate_receipt") is not None:
        errors.append("asg007_must_remain_ineligible")
    if value.get("routed_evidence_consumed") is not False:
        errors.append("routed_evidence_consumed_must_be_false")
    for key in (
        "execution_authority",
        "life_consumption_authority",
        "reward_authority",
        "evidence_authority",
        "platform_counter_reset_claimed",
    ):
        if value.get(key) is not False:
            errors.append(f"{key}_must_be_false")
    digest = value.get("observation_digest")
    if digest != _digest({key: item for key, item in value.items() if key != "observation_digest"}):
        errors.append("observation_digest")
    return errors
