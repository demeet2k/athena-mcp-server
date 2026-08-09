"""Campaign V3 route-selection / attempt observation identity bridge.

Preserves selected route context across the existing compiled-packet ->
attempt-identity -> Dispatch-bridge lineage. It does not prove semantic execution,
Life consumption, verifier success, or ASG-007 route-risk standing.
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

REQUIRED_ROUTE_CONTEXT_KEYS = (
    "selected_route_id", "route_family_id", "minigame", "objective_family_id",
    "task_family", "capability_profile_digest", "toolset_digest", "difficulty_band",
)


class CampaignV3RouteObservationError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + _sha(value)


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
        raise CampaignV3RouteObservationError("route_context missing required fields: " + ",".join(missing))
    for key in REQUIRED_ROUTE_CONTEXT_KEYS:
        out[key] = _nonblank(out.get(key), f"route_context.{key}")
    for key in ("capability_profile_digest", "toolset_digest"):
        if not out[key].startswith("sha256:"):
            raise CampaignV3RouteObservationError(f"{key} must be sha256-addressed")
    return out


def route_context_digest(value: Mapping[str, Any]) -> str:
    return _digest(normalize_route_context(value))


def _packet_identity(packet: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_campaign_v3_life_quest_packet(packet)
    if errors:
        raise CampaignV3RouteObservationError("invalid Campaign V3 Life quest packet: " + ";".join(errors))
    campaign = packet.get("campaign")
    quest = packet.get("quest")
    pulse = packet.get("pulse_binding")
    if not isinstance(campaign, Mapping) or not isinstance(quest, Mapping) or not isinstance(pulse, Mapping):
        raise CampaignV3RouteObservationError("campaign/quest/pulse identity missing")
    return {
        "packet_digest": _nonblank(packet.get("packet_digest"), "packet_digest"),
        "campaign_id": campaign.get("campaign_id"),
        "branch_id": campaign.get("branch_id"),
        "agent_id": campaign.get("agent_coordinate_name"),
        "residual_step": campaign.get("residual_step"),
        "quest_id": quest.get("quest_id"),
        "quest_version": quest.get("quest_version"),
        "pulse_index": pulse.get("pulse_index"),
        "pulse_digest": pulse.get("pulse_digest"),
        "git_head": pulse.get("git_head"),
    }


def bind_campaign_v3_route_selection(*, campaign_packet: Mapping[str, Any], selected_action_id: str,
                                     route_context: Mapping[str, Any], objective_digest: str,
                                     source_head: str) -> dict[str, Any]:
    identity = _packet_identity(campaign_packet)
    action_id = _nonblank(selected_action_id, "selected_action_id")
    objective = _nonblank(objective_digest, "objective_digest")
    if not objective.startswith("sha256:"):
        raise CampaignV3RouteObservationError("objective_digest must be sha256-addressed")
    head = _nonblank(source_head, "source_head")
    context = normalize_route_context(route_context)
    context_digest = _digest(context)
    selection_id = "ROUTE-SELECTION-" + _sha({
        "packet_digest": identity["packet_digest"],
        "selected_action_id": action_id,
        "objective_digest": objective,
        "route_context_digest": context_digest,
    })[:32]
    out = {
        "artifact": SELECTION_ARTIFACT, "status": "BOUND_SELECTION_IDENTITY", **identity,
        "selected_action_id": action_id, "objective_digest": objective,
        "route_context": context, "route_context_digest": context_digest,
        "route_selection_id": selection_id, "source_head": head,
        "semantic_execution_proven": False, "execution_authority": False,
        "life_consumption_authority": False, "reward_authority": False,
        "evidence_authority": False, "platform_counter_reset_claimed": False,
    }
    out["selection_digest"] = _digest({k: v for k, v in out.items() if k != "selection_digest"})
    return out


def validate_campaign_v3_route_selection(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping):
        return ["selection_not_object"]
    errors: list[str] = []
    if value.get("artifact") != SELECTION_ARTIFACT: errors.append("artifact")
    if value.get("status") != "BOUND_SELECTION_IDENTITY": errors.append("status")
    try:
        context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError:
        context = None; errors.append("route_context")
    if context is not None and value.get("route_context_digest") != _digest(context): errors.append("route_context_digest")
    if context is not None and all(isinstance(value.get(k), str) and value.get(k) for k in ("packet_digest","selected_action_id","objective_digest")):
        expected = "ROUTE-SELECTION-" + _sha({
            "packet_digest": value["packet_digest"], "selected_action_id": value["selected_action_id"],
            "objective_digest": value["objective_digest"], "route_context_digest": value["route_context_digest"],
        })[:32]
        if value.get("route_selection_id") != expected: errors.append("route_selection_id")
    else: errors.append("selection_identity")
    for key in ("semantic_execution_proven","execution_authority","life_consumption_authority","reward_authority","evidence_authority","platform_counter_reset_claimed"):
        if value.get(key) is not False: errors.append(f"{key}_must_be_false")
    if value.get("selection_digest") != _digest({k: v for k, v in value.items() if k != "selection_digest"}): errors.append("selection_digest")
    return errors


def bind_campaign_v3_route_attempt(*, route_selection: Mapping[str, Any], attempt_identity: Mapping[str, Any],
                                   existing_binding: Mapping[str, Any] | None = None) -> dict[str, Any]:
    selection_errors = validate_campaign_v3_route_selection(route_selection)
    if selection_errors: raise CampaignV3RouteObservationError("invalid route selection: " + ";".join(selection_errors))
    attempt_errors = validate_campaign_v3_life_attempt_identity(attempt_identity)
    if attempt_errors: raise CampaignV3RouteObservationError("invalid Life attempt identity: " + ";".join(attempt_errors))
    if attempt_identity.get("packet_digest") != route_selection.get("packet_digest"):
        raise CampaignV3RouteObservationError("attempt packet_digest does not match route selection")
    attempt_id = _nonblank(attempt_identity.get("attempt_id"), "attempt_id")
    event_id = _nonblank(attempt_identity.get("execution_event_id"), "execution_event_id")
    route_attempt_id = "ROUTE-ATTEMPT-" + _sha({
        "route_selection_id": route_selection["route_selection_id"], "attempt_id": attempt_id,
        "packet_digest": route_selection["packet_digest"],
    })[:32]
    if existing_binding is not None:
        existing_errors = validate_campaign_v3_route_attempt(existing_binding)
        if existing_errors: raise CampaignV3RouteObservationError("invalid existing binding: " + ";".join(existing_errors))
        if existing_binding.get("attempt_id") == attempt_id:
            if existing_binding.get("route_selection_id") != route_selection.get("route_selection_id"):
                raise CampaignV3RouteObservationError("attempt_id already bound to a conflicting route selection")
            return copy.deepcopy(dict(existing_binding))
    out = {
        "artifact": ATTEMPT_ARTIFACT, "status": "BOUND_ROUTE_ATTEMPT_IDENTITY",
        "route_selection_id": route_selection["route_selection_id"],
        "route_selection_digest": route_selection["selection_digest"],
        "route_attempt_id": route_attempt_id, "packet_digest": route_selection["packet_digest"],
        "attempt_id": attempt_id, "execution_event_id": event_id,
        "selected_action_id": route_selection["selected_action_id"],
        "objective_digest": route_selection["objective_digest"],
        "route_context": copy.deepcopy(route_selection["route_context"]),
        "route_context_digest": route_selection["route_context_digest"],
        **{k: route_selection.get(k) for k in ("campaign_id","branch_id","agent_id","residual_step","quest_id","quest_version","pulse_index","pulse_digest","git_head","source_head")},
        "semantic_execution_proven": False, "execution_authority": False,
        "life_consumption_authority": False, "reward_authority": False,
        "evidence_authority": False, "platform_counter_reset_claimed": False,
    }
    out["route_attempt_digest"] = _digest({k: v for k, v in out.items() if k != "route_attempt_digest"})
    return out


def validate_campaign_v3_route_attempt(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping): return ["route_attempt_not_object"]
    errors: list[str] = []
    if value.get("artifact") != ATTEMPT_ARTIFACT: errors.append("artifact")
    if value.get("status") != "BOUND_ROUTE_ATTEMPT_IDENTITY": errors.append("status")
    try: context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError: context = None; errors.append("route_context")
    if context is not None and value.get("route_context_digest") != _digest(context): errors.append("route_context_digest")
    if all(isinstance(value.get(k), str) and value.get(k) for k in ("route_selection_id","attempt_id","packet_digest")):
        expected = "ROUTE-ATTEMPT-" + _sha({"route_selection_id":value["route_selection_id"],"attempt_id":value["attempt_id"],"packet_digest":value["packet_digest"]})[:32]
        if value.get("route_attempt_id") != expected: errors.append("route_attempt_id")
    else: errors.append("route_attempt_identity")
    for key in ("semantic_execution_proven","execution_authority","life_consumption_authority","reward_authority","evidence_authority","platform_counter_reset_claimed"):
        if value.get(key) is not False: errors.append(f"{key}_must_be_false")
    if value.get("route_attempt_digest") != _digest({k:v for k,v in value.items() if k != "route_attempt_digest"}): errors.append("route_attempt_digest")
    return errors


def project_campaign_v3_route_observation(*, route_attempt: Mapping[str, Any], dispatch_bridge: Mapping[str, Any],
                                          execution_provenance: Mapping[str, Any], observed_at: int,
                                          routed_evidence_refs: Sequence[str] | None = None) -> dict[str, Any]:
    errors = validate_campaign_v3_route_attempt(route_attempt)
    if errors: raise CampaignV3RouteObservationError("invalid route-attempt binding: " + ";".join(errors))
    bridge_errors = validate_campaign_v3_life_dispatch_bridge(dispatch_bridge)
    if bridge_errors: raise CampaignV3RouteObservationError("invalid Dispatch bridge: " + ";".join(bridge_errors))
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
        if not isinstance(routed_evidence_refs, Sequence) or isinstance(routed_evidence_refs, (str,bytes)):
            raise CampaignV3RouteObservationError("routed_evidence_refs must be a list")
        refs = [_nonblank(item,"routed_evidence_ref") for item in routed_evidence_refs]
        if len(refs) != len(set(refs)): raise CampaignV3RouteObservationError("duplicate routed_evidence_ref")
    packet = dispatch_bridge.get("dispatch_packet")
    if not isinstance(packet, Mapping): raise CampaignV3RouteObservationError("Dispatch packet missing")
    result_class = packet.get("result_class")
    translated_executed = packet.get("executed") is True
    played_observed = translated_executed and result_class in {"CLEAR","FAIL_CLEAR"}
    semantic_proven = execution_provenance.get("semantic_execution_proven") is True
    eligibility = "NOT_ELIGIBLE_UNPROVEN_EXECUTION" if not semantic_proven else "NOT_ELIGIBLE_MISSING_AUTHORITATIVE_LIFE_RESULT"
    out = {
        "artifact": OBSERVATION_ARTIFACT, "status": "INSTRUMENTED_UNPROVEN", "observed_at": observed_at,
        **{k: route_attempt.get(k) for k in ("route_attempt_id","route_selection_id","packet_digest","attempt_id","execution_event_id","campaign_id","branch_id","agent_id","residual_step","quest_id","quest_version","pulse_index","pulse_digest","selected_action_id","objective_digest","route_context","route_context_digest","source_head")},
        "result_class": result_class, "dispatch_translated_executed": translated_executed,
        "played_observed_by_dispatch_translation": played_observed, "life_consumed": None,
        "semantic_execution_proven": semantic_proven, "execution_evidence_class": execution_provenance.get("evidence_class"),
        "routed_evidence_refs": refs, "routed_evidence_consumed": False,
        "verified": False, "self_scored": False, "asg007_eligible": False,
        "asg007_eligibility_status": eligibility, "asg007_candidate_receipt": None,
        "execution_authority": False, "life_consumption_authority": False,
        "reward_authority": False, "evidence_authority": False,
        "platform_counter_reset_claimed": False,
    }
    out["observation_digest"] = _digest({k:v for k,v in out.items() if k != "observation_digest"})
    return out


def validate_campaign_v3_route_observation(value: Mapping[str, Any]) -> list[str]:
    if not isinstance(value, Mapping): return ["observation_not_object"]
    errors: list[str] = []
    if value.get("artifact") != OBSERVATION_ARTIFACT: errors.append("artifact")
    if value.get("status") != "INSTRUMENTED_UNPROVEN": errors.append("status")
    try: context = normalize_route_context(value.get("route_context"))
    except CampaignV3RouteObservationError: context = None; errors.append("route_context")
    if context is not None and value.get("route_context_digest") != _digest(context): errors.append("route_context_digest")
    if value.get("life_consumed") is not None: errors.append("life_consumed_must_remain_unknown")
    if value.get("verified") is not False: errors.append("verified_must_be_false")
    if value.get("asg007_eligible") is not False or value.get("asg007_candidate_receipt") is not None: errors.append("asg007_must_remain_ineligible")
    if value.get("routed_evidence_consumed") is not False: errors.append("routed_evidence_consumed_must_be_false")
    for key in ("execution_authority","life_consumption_authority","reward_authority","evidence_authority","platform_counter_reset_claimed"):
        if value.get(key) is not False: errors.append(f"{key}_must_be_false")
    if value.get("observation_digest") != _digest({k:v for k,v in value.items() if k != "observation_digest"}): errors.append("observation_digest")
    return errors
