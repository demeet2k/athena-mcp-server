from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Any, Dict, Iterable, Mapping, Optional

TSE_POPULATION_VERSION = "TSE.POPULATION.CIRCULATION.1"
TSE_HATCH_VERSION = "ATHENA.TSE.HATCH.V2"
TSE_RETURN_VERSION = "ATHENA.TSE.RETURN.V2"
TSE_HANDOFF_ARTIFACT = "ATHENA.TSE.HATCH.HANDOFF.V2"
TSE_POPULATION_RESOURCE_URI = "athena://tse-population/v1"

_ALLOWED_MATCH_TREATMENTS = {"NO_EXACT_COLLISION", "JOIN_OR_PARTITION_REQUIRED"}
_PUBLISH_OK = {"COHESION_NEED_PUBLISHED", "COHESION_REQUEST_ALREADY_PUBLISHED"}
_PRIVATE_KEYS = {"chain_of_thought", "private_chain_of_thought", "hidden_reasoning", "scratchpad"}
_RESET_TOKENS = {"token", "context", "quota", "usage", "platform", "counter", "runtime", "provider", "model"}
_ALLOWED_RESET_STATUS_KEY = "platform_counter_reset_claimed"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _short(value: Any, width: int = 24) -> str:
    return _digest(value).split(":", 1)[1][:width]


def _names(values: Optional[Iterable[Any]]) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _finite_nonnegative(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and float(value) >= 0


def _walk_items(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item
            yield from _walk_items(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_items(item)


def _public_errors(value: Any) -> list[str]:
    errors: list[str] = []
    for key, item in _walk_items(value):
        normalized = key.lower().replace("-", "_")
        if normalized in _PRIVATE_KEYS:
            errors.append(f"forbidden_private_key:{key}")
        if normalized == _ALLOWED_RESET_STATUS_KEY:
            if item not in (None, False):
                errors.append("platform_counter_reset_claimed_must_be_false")
            continue
        if "reset" in normalized and any(token in normalized for token in _RESET_TOKENS):
            errors.append(f"forbidden_reset_key:{key}")
    return sorted(set(errors))


def _validate_hatch(hatch: Any) -> list[str]:
    if not isinstance(hatch, Mapping):
        return ["hatch_not_mapping"]
    errors = _public_errors(hatch)
    if hatch.get("schema_version") != TSE_HATCH_VERSION:
        errors.append("hatch_schema_version")
    if hatch.get("status") != "CHILD_ACTIVE":
        errors.append("hatch_not_child_active")
    for key in ("hatch_id", "hatch_digest", "parent_checkpoint_digest", "parent_checkpoint", "child_quest"):
        if not hatch.get(key):
            errors.append(f"hatch_missing:{key}")
    child = hatch.get("child_quest") or {}
    if not isinstance(child, Mapping) or not child.get("id") or not child.get("version"):
        errors.append("child_quest")
    checkpoint = hatch.get("parent_checkpoint") or {}
    if not isinstance(checkpoint, Mapping):
        errors.append("parent_checkpoint")
    else:
        checkpoint_digest = checkpoint.get("checkpoint_digest")
        if checkpoint_digest != hatch.get("parent_checkpoint_digest"):
            errors.append("parent_checkpoint_digest_mismatch")
        if checkpoint_digest:
            checkpoint_body = {key: value for key, value in checkpoint.items() if key != "checkpoint_digest"}
            if _digest(checkpoint_body) != checkpoint_digest:
                errors.append("parent_checkpoint_digest_invalid")
        if not checkpoint.get("residual"):
            errors.append("parent_residual_required")
        if not checkpoint.get("acceptance"):
            errors.append("parent_acceptance_required")
    if hatch.get("hatch_digest"):
        hatch_body = {key: value for key, value in hatch.items() if key != "hatch_digest"}
        if _digest(hatch_body) != hatch.get("hatch_digest"):
            errors.append("hatch_digest_invalid")
    return sorted(set(errors))


def _route_basis(route: Mapping[str, Any]) -> Dict[str, Any]:
    need = route.get("need_args") if isinstance(route.get("need_args"), Mapping) else {}
    return {
        "version": TSE_POPULATION_VERSION,
        "hatch_id": route.get("hatch_id"),
        "hatch_digest": route.get("hatch_digest"),
        "parent_checkpoint_digest": route.get("parent_checkpoint_digest"),
        "parent_agent_id": route.get("parent_agent_id"),
        "child_quest": copy.deepcopy(route.get("child_quest")),
        "capabilities": _names(need.get("capabilities")),
        "targets": _names(need.get("targets")),
        "dependencies": _names(need.get("dependencies")),
        "role": str(need.get("role") or "").strip() or None,
        "needed_units": need.get("needed_units"),
        "constraints": _names(need.get("constraints")),
        "life_policy": str(need.get("life_policy")).strip() if need.get("life_policy") else None,
        "clear_condition_digest": str(need.get("clear_condition_digest")).strip() if need.get("clear_condition_digest") else None,
    }


def _validate_route(route: Any) -> list[str]:
    if not isinstance(route, Mapping):
        return ["route_not_mapping"]
    errors = _public_errors(route)
    if route.get("schema_version") != TSE_POPULATION_VERSION:
        errors.append("route_schema_version")
    for key in (
        "route_id", "route_digest", "hatch_id", "hatch_digest", "parent_checkpoint_digest",
        "parent_agent_id", "child_quest", "child_work_key", "need_args",
    ):
        if not route.get(key):
            errors.append(f"route_missing:{key}")
    if errors:
        return sorted(set(errors))
    basis = _route_basis(route)
    expected_route_id = f"TSE.ROUTE.{_short(basis)}"
    if route.get("route_digest") != _digest(basis):
        errors.append("route_digest_invalid")
    if route.get("route_id") != expected_route_id:
        errors.append("route_id_invalid")
    child = route.get("child_quest") or {}
    expected_request_id = f"TSE.NEED.{_short({**basis, 'route_id': expected_route_id})}"
    expected_child_work_key = f"TSE.CHILD.{_short({'route_id': expected_route_id, 'child': child})}"
    expected_goal_ref = f"TSE-HATCH:{route.get('hatch_id')}:{child.get('id')}@{child.get('version')}"
    need = route.get("need_args") or {}
    checks = {
        "request_id": expected_request_id,
        "agent_id": route.get("parent_agent_id"),
        "kind": "NEED",
        "goal_ref": expected_goal_ref,
        "work_key": expected_child_work_key,
        "quest_ref": f"{child.get('id')}@{child.get('version')}",
    }
    for key, expected in checks.items():
        if need.get(key) != expected:
            errors.append(f"need_args_{key}_invalid")
    if route.get("child_work_key") != expected_child_work_key:
        errors.append("child_work_key_invalid")
    if _names(route.get("acceptance")) != _names(need.get("acceptance_criteria")):
        errors.append("acceptance_contract_mismatch")
    return sorted(set(errors))


def _position_errors(position: Any) -> list[str]:
    if not isinstance(position, Mapping):
        return ["git_position_not_mapping"]
    return [f"git_position_missing:{key}" for key in ("repo", "ref", "head") if not position.get(key)]


class TsePopulationRuntime:
    """Operational projection over Cohesion + Message Board authority.

    Route packets are caller-carried deterministic state, but their immutable
    semantic coordinates are digest-verified on every hop. No second claim
    universe is created. This runtime never presents/joins on behalf of a
    matched agent. Cohesion stays advisory; Message Board stays claim truth.
    """

    def __init__(self, cohesion_runtime):
        self.cohesion = cohesion_runtime

    @staticmethod
    def plan(
        hatch: Mapping[str, Any],
        parent_agent_id: str,
        capabilities: Iterable[str],
        targets: Optional[Iterable[str]] = None,
        dependencies: Optional[Iterable[str]] = None,
        role: str = "",
        needed_units: int = 1,
        constraints: Optional[Iterable[str]] = None,
        life_policy: Optional[str] = None,
        clear_condition_digest: Optional[str] = None,
    ) -> Dict[str, Any]:
        errors = _validate_hatch(hatch)
        if errors:
            return {"status": "TSE_POPULATION_PLAN_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors}
        parent_agent_id = str(parent_agent_id or "").strip()
        capabilities = _names(capabilities)
        if not parent_agent_id or not capabilities:
            return {"status": "TSE_POPULATION_PLAN_HOLD", "hold": "EVIDENCE_HOLD", "errors": ["parent_agent_id_and_capabilities_required"]}
        try:
            needed_units = int(needed_units)
        except (TypeError, ValueError):
            needed_units = 0
        if not 1 <= needed_units <= 64:
            return {"status": "TSE_POPULATION_PLAN_HOLD", "hold": "EVIDENCE_HOLD", "errors": ["needed_units"]}

        child = dict(hatch["child_quest"])
        checkpoint = dict(hatch["parent_checkpoint"])
        basis = {
            "version": TSE_POPULATION_VERSION,
            "hatch_id": hatch["hatch_id"],
            "hatch_digest": hatch["hatch_digest"],
            "parent_checkpoint_digest": hatch["parent_checkpoint_digest"],
            "parent_agent_id": parent_agent_id,
            "child_quest": child,
            "capabilities": capabilities,
            "targets": _names(targets),
            "dependencies": _names(dependencies),
            "role": str(role or "").strip() or None,
            "needed_units": needed_units,
            "constraints": _names(constraints),
            "life_policy": str(life_policy).strip() if life_policy else None,
            "clear_condition_digest": str(clear_condition_digest).strip() if clear_condition_digest else None,
        }
        route_id = f"TSE.ROUTE.{_short(basis)}"
        request_id = f"TSE.NEED.{_short({**basis, 'route_id': route_id})}"
        child_work_key = f"TSE.CHILD.{_short({'route_id': route_id, 'child': child})}"
        goal_ref = f"TSE-HATCH:{hatch['hatch_id']}:{child['id']}@{child['version']}"
        need_args = {
            "request_id": request_id,
            "agent_id": parent_agent_id,
            "kind": "NEED",
            "capabilities": capabilities,
            "goal_ref": goal_ref,
            "role": basis["role"] or "",
            "work_key": child_work_key,
            "targets": basis["targets"],
            "dependencies": basis["dependencies"],
            "provides": [],
            "capacity_units": 1,
            "needed_units": needed_units,
            "constraints": basis["constraints"],
            "acceptance_criteria": _names(checkpoint.get("acceptance")),
            "party_id": None,
            "quest_ref": f"{child['id']}@{child['version']}",
            "life_policy": basis["life_policy"],
            "clear_condition_digest": basis["clear_condition_digest"],
            "allow_collaboration": False,
            "expires_at": None,
        }
        route = {
            "schema_version": TSE_POPULATION_VERSION,
            "route_id": route_id,
            "route_digest": _digest(basis),
            "status": "NEED_READY_NOT_PUBLISHED",
            "hatch_id": hatch["hatch_id"],
            "hatch_digest": hatch["hatch_digest"],
            "parent_checkpoint_digest": hatch["parent_checkpoint_digest"],
            "parent_agent_id": parent_agent_id,
            "child_quest": child,
            "child_work_key": child_work_key,
            "parent_residual": _names(checkpoint.get("residual")),
            "acceptance": _names(checkpoint.get("acceptance")),
            "need_args": need_args,
            "cohesion_request_digest": None,
            "parent_board_claim_id": None,
            "selected_match": None,
            "handoff_message_id": None,
            "child_claim": None,
            "platform_counter_reset_claimed": False,
        }
        return {
            "status": "TSE_POPULATION_NEED_READY",
            "route": route,
            "assignment_authority": False,
            "claim_authority": False,
            "law": "PLAN != PUBLICATION != MATCH != CLAIM",
        }

    def publish(self, route: Mapping[str, Any], remote: str = "origin") -> Dict[str, Any]:
        errors = _validate_route(route)
        if errors:
            return {"status": "TSE_POPULATION_PUBLISH_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors, "route": copy.deepcopy(route)}
        if route.get("status") != "NEED_READY_NOT_PUBLISHED":
            return {"status": "TSE_POPULATION_PUBLISH_HOLD", "hold": "EVIDENCE_HOLD", "reason": "route_not_need_ready", "route": copy.deepcopy(route)}
        args = dict(route["need_args"])
        result = self.cohesion.request_offer(
            args["request_id"], args["agent_id"], args["kind"], args["capabilities"], args["goal_ref"],
            args.get("role", ""), args.get("work_key"), args.get("targets"), args.get("dependencies"),
            args.get("provides"), args.get("capacity_units", 1), args.get("needed_units", 1),
            args.get("constraints"), args.get("acceptance_criteria"), args.get("party_id"),
            args.get("quest_ref"), args.get("life_policy"), args.get("clear_condition_digest"),
            args.get("allow_collaboration", False), args.get("expires_at"), remote,
        )
        if result.get("status") not in _PUBLISH_OK:
            return {
                "status": "TSE_POPULATION_PUBLISH_HOLD",
                "hold": "AUTHORITY_HOLD" if "NOT_PRESENT" in str(result.get("status")) else "EVIDENCE_HOLD",
                "reason": result.get("status"),
                "route": copy.deepcopy(route),
                "cohesion": result,
            }
        request = result.get("request") or {}
        if request.get("request_id") != args["request_id"] or request.get("agent_id") != args["agent_id"] or request.get("request_kind") != "NEED":
            return {"status": "TSE_POPULATION_PUBLISH_HOLD", "hold": "EVIDENCE_HOLD", "reason": "publication_identity_mismatch", "route": copy.deepcopy(route), "cohesion": result}
        if request.get("work_key") != args["work_key"] or request.get("quest_ref") != args["quest_ref"]:
            return {"status": "TSE_POPULATION_PUBLISH_HOLD", "hold": "EVIDENCE_HOLD", "reason": "publication_contract_mismatch", "route": copy.deepcopy(route), "cohesion": result}
        if not request.get("request_digest") or not request.get("board_claim_id"):
            return {"status": "TSE_POPULATION_PUBLISH_HOLD", "hold": "EVIDENCE_HOLD", "reason": "publication_digest_or_claim_missing", "route": copy.deepcopy(route), "cohesion": result}
        out = copy.deepcopy(route)
        out["cohesion_request_digest"] = str(request["request_digest"])
        out["parent_board_claim_id"] = str(request["board_claim_id"])
        out["status"] = "NEED_PUBLISHED"
        return {"status": "TSE_POPULATION_NEED_PUBLISHED", "route": out, "cohesion": result, "assignment_authority": False, "claim_authority": False}

    def match(
        self,
        route: Mapping[str, Any],
        min_score: float = 0.0,
        limit: int = 10,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        errors = _validate_route(route)
        if errors or route.get("status") != "NEED_PUBLISHED":
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors or ["need_not_published"], "route": copy.deepcopy(route)}
        if not _finite_nonnegative(min_score):
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "EVIDENCE_HOLD", "errors": ["min_score"], "route": copy.deepcopy(route)}
        result = self.cohesion.matchmake(route["need_args"]["request_id"], limit, remote, shared_remote_mode)
        if result.get("status") == "COHESION_SHARED_FRONTIER_HOLD" or not result.get("shared_frontier_verified"):
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "STALE_STATE_HOLD", "reason": "shared_frontier_unverified", "route": copy.deepcopy(route), "cohesion": result}
        if result.get("assignment_authority") is not False or result.get("claim_authority") not in (None, False):
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "AUTHORITY_HOLD", "reason": "cohesion_authority_boundary", "route": copy.deepcopy(route), "cohesion": result}
        if result.get("status") != "COHESION_MATCHES":
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "CAPABILITY_HOLD", "reason": result.get("status"), "route": copy.deepcopy(route), "cohesion": result}
        need = result.get("need") or {}
        if need.get("request_id") != route["need_args"]["request_id"]:
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "EVIDENCE_HOLD", "reason": "need_identity_mismatch", "route": copy.deepcopy(route), "cohesion": result}
        candidates = []
        for raw in result.get("candidates") or []:
            if not isinstance(raw, Mapping) or raw.get("eligible") is not True or raw.get("advisory_only") is not True:
                continue
            if not _finite_nonnegative(raw.get("score")) or float(raw["score"]) < float(min_score):
                continue
            treatment = str((raw.get("collision") or {}).get("treatment") or "")
            if treatment not in _ALLOWED_MATCH_TREATMENTS:
                continue
            if str(raw.get("agent_id") or "") == str(route["parent_agent_id"]):
                continue
            candidates.append(dict(raw))
        if not candidates:
            return {"status": "TSE_POPULATION_MATCH_HOLD", "hold": "CAPABILITY_HOLD", "reason": "no_eligible_candidate_after_tse_gates", "route": copy.deepcopy(route), "cohesion": result}
        candidates.sort(key=lambda row: (-float(row["score"]), str(row.get("agent_id")), str(row.get("offer_id"))))
        chosen = candidates[0]
        treatment = str((chosen.get("collision") or {}).get("treatment"))
        out = copy.deepcopy(route)
        out["selected_match"] = {
            "agent_id": str(chosen["agent_id"]),
            "offer_id": str(chosen.get("offer_id") or ""),
            "score": float(chosen["score"]),
            "coordination_treatment": treatment,
            "reason_codes": _names(chosen.get("reason_codes")),
            "match_git_head": result.get("git_head"),
        }
        out["status"] = "MATCHED_ADVISORY_COORDINATION_REQUIRED" if treatment == "JOIN_OR_PARTITION_REQUIRED" else "MATCHED_ADVISORY"
        return {"status": "TSE_POPULATION_MATCHED_ADVISORY", "route": out, "cohesion": result, "assignment_authority": False, "claim_authority": False, "law": "MATCH != CLAIM"}

    def handoff(self, route: Mapping[str, Any], remote: str = "origin") -> Dict[str, Any]:
        errors = _validate_route(route)
        if errors or route.get("status") not in {"MATCHED_ADVISORY", "MATCHED_ADVISORY_COORDINATION_REQUIRED"}:
            return {"status": "TSE_POPULATION_HANDOFF_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors or ["matched_route_required"], "route": copy.deepcopy(route)}
        selected = route.get("selected_match") or {}
        candidate = str(selected.get("agent_id") or "")
        if not candidate:
            return {"status": "TSE_POPULATION_HANDOFF_HOLD", "hold": "EVIDENCE_HOLD", "errors": ["candidate_agent_id"], "route": copy.deepcopy(route)}
        envelope = {
            "artifact": TSE_HANDOFF_ARTIFACT,
            "route_id": route["route_id"],
            "route_digest": route["route_digest"],
            "hatch_id": route["hatch_id"],
            "hatch_digest": route["hatch_digest"],
            "parent_checkpoint_digest": route["parent_checkpoint_digest"],
            "parent_agent_id": route["parent_agent_id"],
            "candidate_agent_id": candidate,
            "cohesion_need_id": route["need_args"]["request_id"],
            "cohesion_offer_id": selected.get("offer_id"),
            "child_quest": route["child_quest"],
            "child_work_key": route["child_work_key"],
            "residual": route.get("parent_residual") or [],
            "acceptance": route.get("acceptance") or [],
            "coordination_treatment": selected.get("coordination_treatment"),
            "assignment_authority": False,
            "claim_authority": False,
            "law": "MATCH != CLAIM; MESSAGE_ROUTE != CONSUMPTION",
        }
        board = self.cohesion._board()
        result = board.post(
            agent_id=route["parent_agent_id"],
            message=_canonical(envelope),
            message_kind="HANDOFF",
            recipients=[candidate],
            remote=remote,
        )
        if result.get("status") != "POSTED":
            return {"status": "TSE_POPULATION_HANDOFF_HOLD", "hold": "AUTHORITY_HOLD", "reason": result.get("status"), "route": copy.deepcopy(route), "message_board": result}
        event = result.get("message_event") or {}
        if candidate not in [str(value) for value in (event.get("recipients") or [])]:
            return {"status": "TSE_POPULATION_HANDOFF_HOLD", "hold": "EVIDENCE_HOLD", "reason": "handoff_recipient_mismatch", "route": copy.deepcopy(route), "message_board": result}
        out = copy.deepcopy(route)
        out["handoff_message_id"] = str(event.get("event_id") or "")
        if not out["handoff_message_id"]:
            return {"status": "TSE_POPULATION_HANDOFF_HOLD", "hold": "EVIDENCE_HOLD", "reason": "handoff_event_id_missing", "route": copy.deepcopy(route), "message_board": result}
        out["status"] = "HANDOFF_ROUTED_NOT_CONSUMED"
        return {"status": "TSE_POPULATION_HANDOFF_ROUTED", "route": out, "message_board": result, "law": "MESSAGE_ROUTE != CONSUMPTION; ACK != CLAIM"}

    def claim_state(
        self,
        route: Mapping[str, Any],
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        errors = _validate_route(route)
        if errors or not route.get("selected_match") or not route.get("handoff_message_id"):
            return {"status": "TSE_POPULATION_CLAIM_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors or ["routed_handoff_required"], "route": copy.deepcopy(route)}
        board = self.cohesion._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=50)
        if not snapshot.get("shared_frontier_verified"):
            return {"status": "TSE_POPULATION_CLAIM_HOLD", "hold": "STALE_STATE_HOLD", "reason": "shared_frontier_unverified", "route": copy.deepcopy(route), "message_board": snapshot}
        child_agent = str(route["selected_match"]["agent_id"])
        rows = [row for row in (snapshot.get("active") or []) if str(row.get("agent_id")) == child_agent]
        if len(rows) != 1:
            return {"status": "TSE_POPULATION_CLAIM_HOLD", "hold": "CAPABILITY_HOLD", "reason": "matched_agent_not_uniquely_active", "route": copy.deepcopy(route), "message_board": snapshot}
        presence = dict(rows[0])
        if not presence.get("claim_id"):
            return {"status": "TSE_POPULATION_CLAIM_HOLD", "hold": "EVIDENCE_HOLD", "reason": "claim_id_missing", "route": copy.deepcopy(route), "message_board": snapshot}
        exact = str(presence.get("work_key") or "") == str(route["child_work_key"])
        treatment = str(route["selected_match"].get("coordination_treatment") or "")
        collaborator = (
            treatment == "JOIN_OR_PARTITION_REQUIRED"
            and str(presence.get("mode") or "") == "COLLABORATOR"
            and str(presence.get("join_of") or "") == str(route.get("parent_board_claim_id") or "")
        )
        if not (exact or collaborator):
            return {
                "status": "TSE_POPULATION_CLAIM_HOLD", "hold": "AUTHORITY_HOLD",
                "reason": "match_or_ack_without_compatible_message_board_claim",
                "route": copy.deepcopy(route), "message_board": snapshot,
                "law": "MATCH != CLAIM; ACK != CLAIM",
            }
        out = copy.deepcopy(route)
        out["child_claim"] = {
            "agent_id": child_agent,
            "claim_id": str(presence["claim_id"]),
            "work_key": presence.get("work_key"),
            "mode": presence.get("mode"),
            "join_of": presence.get("join_of"),
            "claim_base_head": presence.get("claim_base_head"),
            "binding": "EXACT_CHILD_WORK_KEY" if exact else "COLLABORATOR_JOIN_OF_PARENT",
        }
        out["status"] = "SUBTASK_CLAIMED"
        return {"status": "TSE_POPULATION_SUBTASK_CLAIMED", "route": out, "message_board": snapshot, "execution_authority": False, "law": "CLAIM_IS_OBSERVED_NOT_MINTED_BY_TSE"}

    def return_check(
        self,
        route: Mapping[str, Any],
        child_return: Mapping[str, Any],
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        errors = _validate_route(route) + _public_errors(child_return)
        if errors:
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors}
        if route.get("status") != "SUBTASK_CLAIMED" or not route.get("child_claim"):
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "AUTHORITY_HOLD", "reason": "compatible_matched_agent_claim_required"}

        board = self.cohesion._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=50)
        if not snapshot.get("shared_frontier_verified"):
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "STALE_STATE_HOLD", "reason": "shared_frontier_unverified_at_return", "message_board": snapshot}
        claim = route["child_claim"]
        active = [
            row for row in (snapshot.get("active") or [])
            if str(row.get("agent_id")) == str(claim.get("agent_id"))
            and str(row.get("claim_id")) == str(claim.get("claim_id"))
        ]
        if len(active) != 1:
            return {
                "status": "TSE_POPULATION_RETURN_HOLD", "hold": "AUTHORITY_HOLD",
                "reason": "matched_agent_claim_not_current_at_return", "message_board": snapshot,
            }
        current_claim = active[0]
        if claim.get("binding") == "EXACT_CHILD_WORK_KEY":
            if str(current_claim.get("work_key") or "") != str(route.get("child_work_key") or ""):
                return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "AUTHORITY_HOLD", "reason": "child_work_key_claim_drift"}
        elif claim.get("binding") == "COLLABORATOR_JOIN_OF_PARENT":
            if str(current_claim.get("mode") or "") != "COLLABORATOR" or str(current_claim.get("join_of") or "") != str(route.get("parent_board_claim_id") or ""):
                return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "AUTHORITY_HOLD", "reason": "collaborator_claim_drift"}
        else:
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "AUTHORITY_HOLD", "reason": "unknown_claim_binding"}

        if child_return.get("schema_version") != TSE_RETURN_VERSION:
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "reason": "return_schema_version"}
        for key, expected in (
            ("hatch_id", route["hatch_id"]),
            ("hatch_digest", route["hatch_digest"]),
            ("parent_checkpoint_digest", route["parent_checkpoint_digest"]),
            ("population_route_id", route["route_id"]),
            ("population_route_digest", route["route_digest"]),
            ("child_agent_id", route["child_claim"]["agent_id"]),
            ("child_claim_id", route["child_claim"]["claim_id"]),
        ):
            if child_return.get(key) != expected:
                hold = "AUTHORITY_HOLD" if key in {"child_agent_id", "child_claim_id"} else "EVIDENCE_HOLD"
                return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": hold, "reason": f"{key}_mismatch"}
        if not child_return.get("return_receipt_id"):
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "reason": "return_receipt_id"}
        if child_return.get("verified") is not True or not isinstance(child_return.get("witnesses"), list) or not child_return.get("witnesses"):
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "reason": "verified_witnessed_return_required"}
        if not _finite_nonnegative(child_return.get("verified_delta")) or float(child_return["verified_delta"]) <= 0:
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "reason": "positive_verified_delta_required"}
        position_errors = _position_errors(child_return.get("child_git_position"))
        if position_errors:
            return {"status": "TSE_POPULATION_RETURN_HOLD", "hold": "EVIDENCE_HOLD", "errors": position_errors}
        return {
            "status": "TSE_POPULATION_RETURN_CONSUMPTION_READY",
            "return_payload": copy.deepcopy(child_return),
            "return_applied": False,
            "execution_authority": False,
            "message_board_claim_reverified": True,
            "law": "RETURN_READY != RETURN_APPLIED; TSE_CORE_REMAINS_RETURN_APPLICATION_AUTHORITY",
        }

    @staticmethod
    def resource() -> Dict[str, Any]:
        return {
            "version": TSE_POPULATION_VERSION,
            "artifact": "ATHENA.TSE.POPULATION.OPERATIONAL.V1",
            "flow": [
                "HATCH", "COHESION_NEED", "NEED_PUBLICATION", "MATCH_ADVISORY", "HANDOFF_ROUTE",
                "OPTIONAL_ACK", "MATCHED_AGENT_MESSAGE_BOARD_CLAIM", "SUBTASK_ACTIVE", "VERIFIED_RETURN",
                "RETURN_CONSUMPTION_READY",
            ],
            "laws": [
                "MATCH != CLAIM",
                "MESSAGE_ROUTE != CONSUMPTION",
                "ACK != CLAIM",
                "PARENT_CANNOT_CLAIM_FOR_MATCHED_AGENT",
                "COHESION_SIGNAL != EXECUTION_AUTHORITY",
                "MESSAGE_BOARD_CLAIM_REMAINS_AUTHORITATIVE",
                "CALLER_CARRIED_ROUTE_REQUIRES_DIGEST_VALIDATION",
                "RETURN_REQUIRES_CURRENT_SHARED_CLAIM_REVERIFICATION",
                "RETURN_READY != RETURN_APPLIED",
                "RESEED != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE_RESET",
            ],
            "performance_standing": "UNKNOWN",
            "behavioral_treatment_effect": "UNKNOWN",
        }
