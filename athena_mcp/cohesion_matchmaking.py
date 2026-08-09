from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from .cohesion_mesh import (
    COALITION_ARTIFACT,
    COALITION_EVENT,
    COHESION_VERSION,
    REQUEST_ARTIFACT,
    REQUEST_EVENT,
    CohesionMeshRuntime,
    _digest,
    _names,
)
from .message_board import _iso, _json_text, _parse_time, _require_id, _utcnow


class CohesionMatchmakingRuntime(CohesionMeshRuntime):
    """Mutation-identity hardening for the Cohesion matchmaking vertical slice.

    The base module owns projection/scoring/comparison mechanics. This class makes
    mutation identities semantic rather than incidental: publication Git heads do
    not poison request idempotency, campaign IDs bind a frozen proposal request,
    and comparison sample order is canonicalized before receipt identity is built.
    """

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
            semantic_basis = {
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
            }
            request_digest = _digest(semantic_basis)
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
            payload = {
                **semantic_basis,
                "request_digest": request_digest,
                "published_from_git_head": base,
                "published_at": _iso(),
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
        exits = _names(exit_criteria)
        rendezvous = _names(rendezvous_refs)
        request_basis = {
            "campaign_id": campaign_id,
            "proposer_id": proposer_id,
            "need_ids": needs,
            "max_participants": max_participants,
            "exit_criteria": exits,
            "rendezvous_refs": rendezvous,
        }
        proposal_request_digest = _digest(request_basis)
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
                if str(payload.get("campaign_id")) != campaign_id:
                    continue
                if payload.get("proposal_request_digest") != proposal_request_digest:
                    raise ValueError(f"COHESION_CAMPAIGN_ID_CONFLICT: {campaign_id}")
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
                "proposal_request_digest": proposal_request_digest,
                "need_ids": needs,
                "assignments": sorted(assignments, key=lambda row: row["need_id"]),
                "unfilled": sorted(unfilled, key=lambda row: row["need_id"]),
                "participant_refs": sorted(participants),
                "max_participants": max_participants,
                "exit_criteria": exits,
                "rendezvous_refs": rendezvous,
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
            event_rel, event = board._event(
                COALITION_EVENT,
                proposer_id,
                proposal,
                recipients=sorted(participants - {proposer_id}),
            )
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

    def solo_party_compare(
        self,
        comparison_id: str,
        observer_id: str,
        solo_samples: Iterable[Dict[str, Any]],
        party_samples: Iterable[Dict[str, Any]],
        decision_rule: Dict[str, Any],
        remote: str = "origin",
    ) -> Dict[str, Any]:
        def canonical_samples(rows: Iterable[Dict[str, Any]]):
            out = []
            for raw in rows:
                row = dict(raw)
                row["evidence_refs"] = _names(row.get("evidence_refs"))
                out.append(row)
            return sorted(out, key=lambda row: (str(row.get("mission_id")), str(row.get("match_key"))))

        return super().solo_party_compare(
            comparison_id,
            observer_id,
            canonical_samples(solo_samples),
            canonical_samples(party_samples),
            dict(decision_rule),
            remote,
        )
