from __future__ import annotations

import hashlib
import json
import statistics
from typing import Any, Dict, Iterable, List, Optional

from .message_board import (
    BOARD_ROOT,
    MessageBoardRuntime,
    _iso,
    _jaccard,
    _json_text,
    _parse_time,
    _require_id,
    _utcnow,
)

COHESION_VERSION = "COHESION.MESH.MATCHMAKING.1"
REQUEST_ARTIFACT = "ATHENA.COHESION.REQUEST_OFFER.V1"
COALITION_ARTIFACT = "ATHENA.COHESION.COALITION.V1"
COMPARISON_ARTIFACT = "ATHENA.COHESION.SOLO_PARTY_COMPARE.V1"
REQUEST_EVENT = "COHESION_REQUEST_OFFER"
COALITION_EVENT = "COHESION_COALITION"
COMPARISON_EVENT = "COHESION_SOLO_PARTY_COMPARE"

MATCH_WEIGHTS = {
    "capability_fit": 0.50,
    "role_complement": 0.15,
    "dependency_unlock": 0.10,
    "capacity_fit": 0.10,
    "freshness": 0.10,
    "party_bridge": 0.05,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _names(values: Optional[Iterable[Any]]) -> List[str]:
    out, seen = [], set()
    for value in values or []:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return sorted(out)


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: List[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


class CohesionMeshRuntime:
    """First executable Cohesion Mesh vertical slice.

    The runtime projects Message Board state and typed Message Board events. It
    deliberately owns no presence, claim, assignment, party-membership, truth,
    scheduler, or XP authority.
    """

    def __init__(self, server):
        self.server = server

    def _board(self) -> MessageBoardRuntime:
        git = getattr(self.server, "git", None)
        if git is None or not git.enabled:
            raise ValueError("ATHENA_GIT_ROOT is required for Cohesion Mesh")
        return MessageBoardRuntime(git)

    @staticmethod
    def _payload(event: Dict[str, Any]) -> Dict[str, Any]:
        value = event.get("payload") or {}
        return value if isinstance(value, dict) else {}

    def _cohesion_events(self, board: MessageBoardRuntime, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = []
        for event in board._events():
            if kind is not None and event.get("kind") != kind:
                continue
            payload = self._payload(event)
            if payload.get("cohesion_version") != COHESION_VERSION:
                continue
            rows.append(event)
        return rows

    @staticmethod
    def _active_map(board: MessageBoardRuntime) -> Dict[str, Dict[str, Any]]:
        return {str(row.get("agent_id")): row for row in board._active()}

    @staticmethod
    def _expired(payload: Dict[str, Any]) -> bool:
        expires_at = payload.get("expires_at")
        if not expires_at:
            return False
        parsed = _parse_time(str(expires_at))
        return parsed is None or parsed <= _utcnow()

    def _request_by_id(self, board: MessageBoardRuntime, request_id: str) -> Optional[Dict[str, Any]]:
        for event in self._cohesion_events(board, REQUEST_EVENT):
            payload = self._payload(event)
            if str(payload.get("request_id")) == request_id:
                return {"event": event, "payload": payload}
        return None

    def _active_requests(self, board: MessageBoardRuntime, request_kind: Optional[str] = None) -> List[Dict[str, Any]]:
        active = self._active_map(board)
        rows = []
        for event in self._cohesion_events(board, REQUEST_EVENT):
            payload = self._payload(event)
            if request_kind and payload.get("request_kind") != request_kind:
                continue
            agent_id = str(payload.get("agent_id") or "")
            if agent_id not in active or self._expired(payload):
                continue
            rows.append({"event": event, "payload": payload, "presence": active[agent_id]})
        rows.sort(key=lambda row: (str(row["payload"].get("request_id")), str(row["event"].get("event_id"))))
        return rows

    def request_offer(
        self,
        request_id: str,
        agent_id: str,
        kind: str,
        capabilities: Iterable[str],
        goal_ref: str,
        role: str = "",
        work_key: Optional[str] = None,
        targets: Optional[Iterable[str]] = None,
        dependencies: Optional[Iterable[str]] = None,
        provides: Optional[Iterable[str]] = None,
        capacity_units: int = 1,
        needed_units: int = 1,
        constraints: Optional[Iterable[str]] = None,
        acceptance_criteria: Optional[Iterable[str]] = None,
        party_id: Optional[str] = None,
        quest_ref: Optional[str] = None,
        life_policy: Optional[str] = None,
        clear_condition_digest: Optional[str] = None,
        allow_collaboration: bool = False,
        expires_at: Optional[str] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        request_id = _require_id(request_id, "request_id")
        agent_id = _require_id(agent_id, "agent_id")
        kind = str(kind or "").upper()
        if kind not in {"NEED", "OFFER"}:
            raise ValueError("kind must be NEED or OFFER")
        capability_rows = _names(capabilities)
        if not capability_rows:
            raise ValueError("at least one capability is required")
        goal_ref = str(goal_ref or "").strip()
        if not goal_ref:
            raise ValueError("goal_ref must be non-empty")
        capacity_units = int(capacity_units)
        needed_units = int(needed_units)
        if not 1 <= capacity_units <= 64 or not 1 <= needed_units <= 64:
            raise ValueError("capacity_units and needed_units must be between 1 and 64")
        expiry = None
        if expires_at is not None:
            parsed = _parse_time(str(expires_at))
            if parsed is None:
                raise ValueError("expires_at must be an ISO-8601 timestamp")
            if parsed <= _utcnow():
                raise ValueError("expires_at must be in the future")
            expiry = parsed.isoformat()
        board = self._board()

        def build(base):
            existing = self._request_by_id(board, request_id)
            active = self._active_map(board)
            presence = active.get(agent_id)
            if not presence:
                return {
                    "return": {
                        "status": "COHESION_AGENT_NOT_PRESENT_HOLD",
                        "request_id": request_id,
                        "agent_id": agent_id,
                        "next": "athena_message_board present or join",
                        "assignment_authority": False,
                    }
                }
            effective_work_key = str(work_key or presence.get("work_key") or "").strip() or None
            effective_targets = _names(targets if targets is not None else (presence.get("targets") or []))
            payload_basis = {
                "cohesion_version": COHESION_VERSION,
                "cohesion_artifact": REQUEST_ARTIFACT,
                "request_id": request_id,
                "agent_id": agent_id,
                "request_kind": kind,
                "capabilities": capability_rows,
                "goal_ref": goal_ref,
                "role": str(role or "").strip() or None,
                "work_key": effective_work_key,
                "targets": effective_targets,
                "dependencies": _names(dependencies),
                "provides": _names(provides),
                "capacity_units": capacity_units,
                "needed_units": needed_units,
                "constraints": _names(constraints),
                "acceptance_criteria": _names(acceptance_criteria),
                "party_id": str(party_id).strip() if party_id else None,
                "quest_ref": str(quest_ref).strip() if quest_ref else None,
                "life_policy": str(life_policy).strip() if life_policy else None,
                "clear_condition_digest": str(clear_condition_digest).strip() if clear_condition_digest else None,
                "allow_collaboration": bool(allow_collaboration),
                "expires_at": expiry,
                "board_claim_id": presence.get("claim_id"),
                "board_claim_mode": presence.get("mode"),
                "published_from_git_head": base,
            }
            request_digest = _digest(payload_basis)
            payload = {**payload_basis, "request_digest": request_digest, "published_at": _iso()}
            if existing:
                old = existing["payload"]
                if old.get("request_digest") != request_digest:
                    raise ValueError(f"COHESION_REQUEST_ID_CONFLICT: {request_id}")
                return {
                    "return": {
                        "status": "COHESION_REQUEST_ALREADY_PUBLISHED",
                        "request": old,
                        "event": existing["event"],
                        "idempotent": True,
                        "assignment_authority": False,
                    }
                }
            event_rel, event = board._event(REQUEST_EVENT, agent_id, payload)
            return {
                "files": {event_rel: _json_text(event)},
                "message": f"cohesion {kind.lower()} {request_id}",
                "result": {
                    "status": f"COHESION_{kind}_PUBLISHED",
                    "request": payload,
                    "event": event,
                    "idempotent": False,
                    "assignment_authority": False,
                    "xp_authority": False,
                },
            }

        return board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    @staticmethod
    def _collision_packet(
        board: MessageBoardRuntime,
        need: Dict[str, Any],
        requester_presence: Dict[str, Any],
        offer_presence: Dict[str, Any],
    ) -> Dict[str, Any]:
        synthetic_need = {
            "task": need.get("goal_ref"),
            "work_key": need.get("work_key"),
            "targets": need.get("targets") or [],
        }
        hard = board._hard_overlap(synthetic_need, offer_presence)
        fuzzy, shared = _jaccard(need.get("goal_ref"), offer_presence.get("task"))
        intentional = board._intentional_pair(requester_presence, offer_presence)
        declared = intentional or str(offer_presence.get("mode")) in {"COLLABORATOR", "REPLICA"}
        allow = bool(need.get("allow_collaboration"))
        if hard and not (declared or allow):
            treatment = "DUPLICATE_COLLISION_HOLD"
            eligible_collision = False
        elif hard:
            treatment = "JOIN_OR_PARTITION_REQUIRED"
            eligible_collision = True
        else:
            treatment = "NO_EXACT_COLLISION"
            eligible_collision = True
        return {
            "hard_reasons": hard,
            "intentional_existing_relation": bool(intentional),
            "declared_collaboration_or_replica": bool(declared),
            "need_allows_collaboration": allow,
            "treatment": treatment,
            "eligible_collision": eligible_collision,
            "fuzzy_similarity": round(float(fuzzy), 6),
            "fuzzy_shared_tokens": int(shared),
            "fuzzy_warning": bool(fuzzy >= 0.65 and shared >= 3),
            "law": "FUZZY_SIMILARITY != DUPLICATE_PROOF",
        }

    def _rank_current(self, board: MessageBoardRuntime, need_id: str, shared_fresh: bool) -> Dict[str, Any]:
        need_row = self._request_by_id(board, need_id)
        if not need_row:
            return {"status": "COHESION_NEED_NOT_FOUND", "need_id": need_id, "candidates": []}
        need = need_row["payload"]
        if need.get("request_kind") != "NEED":
            return {"status": "COHESION_NOT_A_NEED", "need_id": need_id, "candidates": []}
        if self._expired(need):
            return {"status": "COHESION_NEED_EXPIRED", "need_id": need_id, "candidates": []}
        active = self._active_map(board)
        requester = active.get(str(need.get("agent_id")))
        if not requester:
            return {"status": "COHESION_NEED_OWNER_NOT_ACTIVE", "need_id": need_id, "candidates": []}
        required = set(_names(need.get("capabilities")))
        dependencies = set(_names(need.get("dependencies")))
        needed_units = max(1, int(need.get("needed_units") or 1))
        rows = []
        for offer_row in self._active_requests(board, "OFFER"):
            offer = offer_row["payload"]
            offer_agent = str(offer.get("agent_id"))
            if offer_agent == str(need.get("agent_id")):
                continue
            offered = set(_names(offer.get("capabilities")))
            fit = len(required & offered) / len(required) if required else 0.0
            need_role = str(need.get("role") or "")
            offer_role = str(offer.get("role") or "")
            role = 0.5 if not need_role else (1.0 if need_role == offer_role else 0.0)
            provided = set(_names(offer.get("provides")))
            unlock = len(dependencies & provided) / len(dependencies) if dependencies else 0.5
            capacity_units = max(0, int(offer.get("capacity_units") or 0))
            capacity = min(1.0, capacity_units / float(needed_units)) if capacity_units else 0.0
            freshness = 1.0 if shared_fresh else 0.5
            bridge = 1.0 if (
                need.get("party_id") and offer.get("party_id") and need.get("party_id") != offer.get("party_id")
            ) else 0.0
            collision = self._collision_packet(board, need, requester, offer_row["presence"])
            score = 100.0 * (
                MATCH_WEIGHTS["capability_fit"] * fit
                + MATCH_WEIGHTS["role_complement"] * role
                + MATCH_WEIGHTS["dependency_unlock"] * unlock
                + MATCH_WEIGHTS["capacity_fit"] * capacity
                + MATCH_WEIGHTS["freshness"] * freshness
                + MATCH_WEIGHTS["party_bridge"] * bridge
            )
            if collision["hard_reasons"]:
                score -= 18.0 if collision["eligible_collision"] else 60.0
            score = max(0.0, min(100.0, score))
            eligible = bool(fit > 0 and capacity > 0 and collision["eligible_collision"])
            reasons = []
            if fit == 1.0:
                reasons.append("FULL_CAPABILITY_FIT")
            elif fit > 0:
                reasons.append("PARTIAL_CAPABILITY_FIT")
            else:
                reasons.append("CAPABILITY_MISS")
            if unlock > 0 and dependencies:
                reasons.append("DEPENDENCY_UNLOCK")
            if bridge > 0:
                reasons.append("CROSS_PARTY_BRIDGE")
            if collision["fuzzy_warning"]:
                reasons.append("FUZZY_OVERLAP_WARNING_ONLY")
            if collision["hard_reasons"]:
                reasons.append(collision["treatment"])
            if not shared_fresh:
                reasons.append("SHARED_FRONTIER_UNVERIFIED")
            rows.append({
                "offer_id": offer.get("request_id"),
                "agent_id": offer_agent,
                "goal_ref": offer.get("goal_ref"),
                "party_id": offer.get("party_id"),
                "role": offer.get("role"),
                "capabilities": sorted(offered),
                "provides": sorted(provided),
                "capacity_units": capacity_units,
                "needed_units": needed_units,
                "score": round(score, 6),
                "eligible": eligible,
                "components": {
                    "capability_fit": round(fit, 6),
                    "role_complement": round(role, 6),
                    "dependency_unlock": round(unlock, 6),
                    "capacity_fit": round(capacity, 6),
                    "freshness": round(freshness, 6),
                    "party_bridge": round(bridge, 6),
                },
                "collision": collision,
                "reason_codes": reasons,
                "advisory_only": True,
            })
        rows.sort(key=lambda row: (not row["eligible"], -float(row["score"]), str(row["agent_id"]), str(row["offer_id"])))
        return {
            "status": "COHESION_MATCHES" if any(row["eligible"] for row in rows) else "COHESION_NO_ELIGIBLE_MATCH",
            "need": need,
            "candidates": rows,
            "weights": dict(MATCH_WEIGHTS),
            "shared_frontier_verified": bool(shared_fresh),
            "assignment_authority": False,
            "claim_authority": False,
            "law": "MATCH != ASSIGNMENT; EXISTING_MESSAGE_BOARD_CLAIMS_REMAIN_AUTHORITATIVE",
        }

    def matchmake(
        self,
        need_id: str,
        limit: int = 10,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        need_id = _require_id(need_id, "need_id")
        limit = max(1, min(50, int(limit)))
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=1)
        if shared_remote_mode == "REQUIRED" and not snapshot.get("shared_frontier_verified"):
            return {
                "status": "COHESION_SHARED_FRONTIER_HOLD",
                "need_id": need_id,
                "remote_sync": snapshot.get("remote_sync"),
                "candidates": [],
                "assignment_authority": False,
            }
        value = self._rank_current(board, need_id, bool(snapshot.get("shared_frontier_verified")))
        value["candidates"] = value.get("candidates", [])[:limit]
        value["git_head"] = snapshot.get("git_head")
        value["remote_sync"] = snapshot.get("remote_sync")
        return value

    def coalition(
        self,
        campaign_id: str,
        proposer_id: str,
        need_ids: Iterable[str],
        max_participants: int = 8,
        exit_criteria: Optional[Iterable[str]] = None,
        rendezvous_refs: Optional[Iterable[str]] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        campaign_id = _require_id(campaign_id, "campaign_id")
        proposer_id = _require_id(proposer_id, "proposer_id")
        needs = _names(need_ids)
        if len(needs) < 2:
            raise ValueError("coalition requires at least two distinct need_ids")
        max_participants = max(2, min(32, int(max_participants)))
        board = self._board()

        def build(base):
            active = self._active_map(board)
            if proposer_id not in active:
                return {
                    "return": {
                        "status": "COHESION_PROPOSER_NOT_PRESENT_HOLD",
                        "campaign_id": campaign_id,
                        "assignment_authority": False,
                    }
                }
            for event in self._cohesion_events(board, COALITION_EVENT):
                payload = self._payload(event)
                if str(payload.get("campaign_id")) == campaign_id:
                    return {
                        "return": {
                            "status": "COHESION_COALITION_ALREADY_PROPOSED",
                            "proposal": payload,
                            "event": event,
                            "idempotent": True,
                            "assignment_authority": False,
                        }
                    }
            ranked = {need_id: self._rank_current(board, need_id, True) for need_id in needs}
            constrained = sorted(
                needs,
                key=lambda need_id: (
                    sum(1 for row in ranked[need_id].get("candidates", []) if row.get("eligible")),
                    need_id,
                ),
            )
            remaining_by_offer: Dict[str, int] = {}
            participants = {proposer_id}
            assignments, unfilled = [], []
            for need_id in constrained:
                need = ranked[need_id].get("need") or {}
                needed_units = max(1, int(need.get("needed_units") or 1))
                selected = None
                for candidate in ranked[need_id].get("candidates", []):
                    if not candidate.get("eligible"):
                        continue
                    offer_id = str(candidate.get("offer_id"))
                    if offer_id not in remaining_by_offer:
                        remaining_by_offer[offer_id] = int(candidate.get("capacity_units") or 0)
                    agent_id = str(candidate.get("agent_id"))
                    prospective = participants | {str(need.get("agent_id")), agent_id}
                    if len(prospective) > max_participants:
                        continue
                    if remaining_by_offer[offer_id] < needed_units:
                        continue
                    selected = candidate
                    remaining_by_offer[offer_id] -= needed_units
                    participants = prospective
                    break
                if selected is None:
                    unfilled.append({
                        "need_id": need_id,
                        "owner": need.get("agent_id"),
                        "goal_ref": need.get("goal_ref"),
                        "reason": "NO_ELIGIBLE_CAPACITY_CONSTRAINED_MATCH",
                    })
                    continue
                assignments.append({
                    "need_id": need_id,
                    "need_owner": need.get("agent_id"),
                    "goal_ref": need.get("goal_ref"),
                    "offer_id": selected.get("offer_id"),
                    "assigned_candidate": selected.get("agent_id"),
                    "score": selected.get("score"),
                    "needed_units": needed_units,
                    "coordination_treatment": selected.get("collision", {}).get("treatment"),
                    "reason_codes": selected.get("reason_codes"),
                })
            if not assignments:
                return {
                    "return": {
                        "status": "COHESION_COALITION_NO_ASSIGNMENTS_HOLD",
                        "campaign_id": campaign_id,
                        "unfilled": unfilled,
                        "assignment_authority": False,
                    }
                }
            proposal_basis = {
                "cohesion_version": COHESION_VERSION,
                "cohesion_artifact": COALITION_ARTIFACT,
                "campaign_id": campaign_id,
                "proposer_id": proposer_id,
                "need_ids": needs,
                "assignments": sorted(assignments, key=lambda row: row["need_id"]),
                "unfilled": sorted(unfilled, key=lambda row: row["need_id"]),
                "participant_refs": sorted(participants),
                "max_participants": max_participants,
                "exit_criteria": _names(exit_criteria),
                "rendezvous_refs": _names(rendezvous_refs),
                "git_head": base,
                "assignment_authority": False,
                "party_membership_authority": False,
                "execution_authority": False,
            }
            proposal = {
                **proposal_basis,
                "proposal_digest": _digest(proposal_basis),
                "proposed_at": _iso(),
            }
            event_rel, event = board._event(COALITION_EVENT, proposer_id, proposal, recipients=sorted(participants - {proposer_id}))
            return {
                "files": {event_rel: _json_text(event)},
                "message": f"cohesion coalition {campaign_id}",
                "result": {
                    "status": "COHESION_COALITION_PROPOSED" if not unfilled else "COHESION_COALITION_PARTIAL_PROPOSAL",
                    "proposal": proposal,
                    "event": event,
                    "idempotent": False,
                    "assignment_authority": False,
                    "next": "commit actual ownership through existing Message Board/Party/MATA mechanisms",
                },
            }

        return board._mutate(agent_id=proposer_id, remote=remote, build_files=build)

    @staticmethod
    def _sample_map(samples: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        rows: Dict[str, List[Dict[str, Any]]] = {}
        for raw in samples:
            sample = dict(raw)
            key = str(sample.get("match_key") or "").strip()
            rows.setdefault(key, []).append(sample)
        return rows

    @staticmethod
    def _sample_primary(sample: Dict[str, Any]) -> float:
        cost = float(sample.get("cost") or 0.0)
        return float(sample.get("verified_delta") or 0.0) / cost if cost > 0 else 0.0

    def _compare_samples(
        self,
        solo_samples: Iterable[Dict[str, Any]],
        party_samples: Iterable[Dict[str, Any]],
        decision_rule: Dict[str, Any],
    ) -> Dict[str, Any]:
        solo = self._sample_map(solo_samples)
        party = self._sample_map(party_samples)
        common = sorted(set(solo) & set(party))
        ambiguous = sorted(key for key in common if len(solo[key]) != 1 or len(party[key]) != 1)
        pairs = []
        quality_reasons = []
        mission_ids = []
        for group in (solo, party):
            for samples in group.values():
                for sample in samples:
                    mission_ids.append(str(sample.get("mission_id") or ""))
                    if not sample.get("evidence_refs"):
                        quality_reasons.append(f"MISSING_EVIDENCE_REFS:{sample.get('mission_id')}")
        if len(mission_ids) != len(set(mission_ids)):
            quality_reasons.append("DUPLICATE_MISSION_ID")
        if ambiguous:
            quality_reasons.append("AMBIGUOUS_MATCH_KEYS")
        for key in common:
            if key in ambiguous:
                continue
            s = solo[key][0]
            p = party[key][0]
            diff = {
                "match_key": key,
                "solo_mission_id": s.get("mission_id"),
                "party_mission_id": p.get("mission_id"),
                "evidence_refs": sorted(set(_names(s.get("evidence_refs"))) | set(_names(p.get("evidence_refs")))),
                "verified_delta_per_cost": self._sample_primary(p) - self._sample_primary(s),
                "productive_transitions": float(p.get("productive_transition_count") or 0) - float(s.get("productive_transition_count") or 0),
                "duplicate_actions": float(p.get("duplicate_actions") or 0) - float(s.get("duplicate_actions") or 0),
                "stale_actions": float(p.get("stale_actions") or 0) - float(s.get("stale_actions") or 0),
                "human_interrupts": float(p.get("human_interrupts") or 0) - float(s.get("human_interrupts") or 0),
                "merge_debt": float(p.get("merge_debt") or 0) - float(s.get("merge_debt") or 0),
                "meta_overhead": float(p.get("meta_overhead") or 0) - float(s.get("meta_overhead") or 0),
                "closure": (1.0 if p.get("closure") else 0.0) - (1.0 if s.get("closure") else 0.0),
                "authority_evidence_violations": float(p.get("authority_evidence_violations") or 0) - float(s.get("authority_evidence_violations") or 0),
                "wasted_overrun": float(p.get("wasted_overrun") or 0) - float(s.get("wasted_overrun") or 0),
            }
            pairs.append(diff)
        min_pairs = int(decision_rule.get("min_pairs") or 0)
        if not bool(decision_rule.get("frozen_before_results")):
            quality_reasons.append("DECISION_RULE_NOT_DECLARED_FROZEN")
        if len(pairs) < min_pairs:
            quality_reasons.append("INSUFFICIENT_MATCHED_PAIRS")
        unmatched_solo = sorted(set(solo) - set(party))
        unmatched_party = sorted(set(party) - set(solo))
        metric_names = [
            "verified_delta_per_cost",
            "productive_transitions",
            "duplicate_actions",
            "stale_actions",
            "human_interrupts",
            "merge_debt",
            "meta_overhead",
            "closure",
            "authority_evidence_violations",
            "wasted_overrun",
        ]
        summary = {}
        for metric in metric_names:
            values = [float(pair[metric]) for pair in pairs]
            summary[metric] = {"mean_party_minus_solo": round(_mean(values), 9), "median_party_minus_solo": round(_median(values), 9)}
        if quality_reasons:
            decision = "UNKNOWN_INSUFFICIENT_EVIDENCE"
            rule_pass = None
        else:
            checks = {
                "primary_effect": summary["verified_delta_per_cost"]["mean_party_minus_solo"] >= float(decision_rule.get("min_primary_effect") or 0.0),
                "duplicate_nonregression": summary["duplicate_actions"]["mean_party_minus_solo"] <= float(decision_rule.get("max_duplicate_regression") or 0.0),
                "stale_nonregression": summary["stale_actions"]["mean_party_minus_solo"] <= float(decision_rule.get("max_stale_regression") or 0.0),
                "human_interrupt_nonregression": summary["human_interrupts"]["mean_party_minus_solo"] <= float(decision_rule.get("max_human_interrupt_regression") or 0.0),
                "meta_overhead_nonregression": summary["meta_overhead"]["mean_party_minus_solo"] <= float(decision_rule.get("max_meta_overhead_regression") or 0.0),
                "authority_evidence_nonregression": summary["authority_evidence_violations"]["mean_party_minus_solo"] <= 0.0,
            }
            rule_pass = all(checks.values())
            decision = "PARTY_RULE_PASS_DESCRIPTIVE" if rule_pass else "PARTY_RULE_NOT_PASS_DESCRIPTIVE"
        return {
            "decision": decision,
            "rule_pass": rule_pass,
            "decision_rule": dict(decision_rule),
            "decision_rule_digest": _digest(decision_rule),
            "matched_pair_count": len(pairs),
            "matched_pairs": pairs,
            "ambiguous_match_keys": ambiguous,
            "unmatched_solo_keys": unmatched_solo,
            "unmatched_party_keys": unmatched_party,
            "quality_reasons": sorted(set(quality_reasons)),
            "summary": summary,
            "standing": "MATCHED_DESCRIPTIVE_OBSERVATION" if not quality_reasons else "UNDERDETERMINED",
            "causal_effect": "UNKNOWN",
            "promotion_authority": False,
            "epistemic_boundary": (
                "Caller-supplied evidence refs and observed metrics are preserved as references; this comparator does not "
                "independently verify their world truth. Matched descriptive difference != causal treatment effect."
            ),
        }

    def solo_party_compare(
        self,
        comparison_id: str,
        observer_id: str,
        solo_samples: Iterable[Dict[str, Any]],
        party_samples: Iterable[Dict[str, Any]],
        decision_rule: Dict[str, Any],
        remote: str = "origin",
    ) -> Dict[str, Any]:
        comparison_id = _require_id(comparison_id, "comparison_id")
        observer_id = _require_id(observer_id, "observer_id")
        solo_rows = [dict(row) for row in solo_samples]
        party_rows = [dict(row) for row in party_samples]
        if not solo_rows or not party_rows:
            raise ValueError("both solo_samples and party_samples are required")
        request_basis = {
            "comparison_id": comparison_id,
            "observer_id": observer_id,
            "solo_samples": solo_rows,
            "party_samples": party_rows,
            "decision_rule": dict(decision_rule),
        }
        request_digest = _digest(request_basis)
        board = self._board()

        def build(base):
            active = self._active_map(board)
            if observer_id not in active:
                return {
                    "return": {
                        "status": "COHESION_OBSERVER_NOT_PRESENT_HOLD",
                        "comparison_id": comparison_id,
                        "promotion_authority": False,
                    }
                }
            for event in self._cohesion_events(board, COMPARISON_EVENT):
                payload = self._payload(event)
                if str(payload.get("comparison_id")) != comparison_id:
                    continue
                if payload.get("request_digest") != request_digest:
                    raise ValueError(f"COHESION_COMPARISON_ID_CONFLICT: {comparison_id}")
                replay = dict(payload)
                replay["idempotent"] = True
                return {"return": replay}
            comparison = self._compare_samples(solo_rows, party_rows, decision_rule)
            payload_basis = {
                "cohesion_version": COHESION_VERSION,
                "cohesion_artifact": COMPARISON_ARTIFACT,
                "comparison_id": comparison_id,
                "observer_id": observer_id,
                "request_digest": request_digest,
                "observed_at": _iso(),
                "observed_git_head": base,
                **comparison,
                "idempotent": False,
            }
            receipt_digest = _digest({key: value for key, value in payload_basis.items() if key != "idempotent"})
            payload = {**payload_basis, "receipt_digest": receipt_digest}
            event_rel, event = board._event(COMPARISON_EVENT, observer_id, payload)
            return {
                "files": {event_rel: _json_text(event)},
                "message": f"cohesion solo-party compare {comparison_id}",
                "result": payload,
            }

        return board._mutate(agent_id=observer_id, remote=remote, build_files=build)

    def benchmark(self) -> Dict[str, Any]:
        try:
            board = self._board()
        except ValueError:
            return {"cohesion_version": COHESION_VERSION, "cohesion_git_enabled": False}
        events = self._cohesion_events(board)
        kinds = {}
        for event in events:
            key = str(event.get("kind"))
            kinds[key] = kinds.get(key, 0) + 1
        return {
            "cohesion_version": COHESION_VERSION,
            "cohesion_git_enabled": True,
            "cohesion_event_count": len(events),
            "cohesion_event_kinds": kinds,
        }

    def resource(self) -> Dict[str, Any]:
        return {
            "version": COHESION_VERSION,
            "scope": "C0+C2 matchmaking/coalition vertical slice + C4 solo-party comparator",
            "parent_issue": "demeet2k/athena-mcp-server#147",
            "evaluation_contract": "demeet2k/Athena#192 GTC.V1 public telemetry",
            "transport": "ATHENA Message Board V1",
            "tools": [
                "athena_cohesion_request_offer",
                "athena_cohesion_matchmake",
                "athena_cohesion_coalition",
                "athena_cohesion_solo_party_compare",
            ],
            "match_weights": dict(MATCH_WEIGHTS),
            "laws": [
                "REQUEST_OR_OFFER != ASSIGNMENT",
                "MATCH != CLAIM != PARTY_MEMBERSHIP != EXECUTION_AUTHORITY",
                "Message Board remains sole presence/claim/message/ACK transport authority",
                "exact hard overlap without declared collaboration/replication/allow-collaboration treatment is ineligible",
                "FUZZY_SIMILARITY != DUPLICATE_PROOF",
                "coalition proposal creates no claims, presence, party membership, scheduler authority, or XP",
                "ROUTED != CONSUMED != COMPLIED != TRUE",
                "weak or ambiguous solo-party matching => UNKNOWN",
                "MATCHED_DESCRIPTIVE_DIFFERENCE != CAUSAL_TREATMENT_EFFECT",
                "self/caller supplied evidence refs are provenance references, not independent world-truth verification",
                "Cohesion Mesh is a projection/control membrane over existing substrates, not a second state universe",
            ],
            "residual": [
                "C1 common-ground tools 1-5",
                "remaining C2 partition/handoff tools 8-9",
                "C3 steering tools 11-15",
                "remaining C4 decision/outcome/health/pulse tools 16-17,19-20",
                "C5 organism scenario and matched field evaluation",
            ],
            "benchmark": self.benchmark(),
        }
