from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .message_board import BOARD_ROOT, MessageBoardRuntime, _iso, _json_text, _require_id

PARTY_VERSION = "PARTY.COORDINATION.BOARD.1"
PARTY_ARTIFACT = "ATHENA.PARTY.COORDINATION.V1"
PARTY_ROOT = f"{BOARD_ROOT}/parties"
TASK_RELATIONS = {
    "INDEPENDENT", "COMMUTATIVE", "ORDERED", "CONDITIONAL",
    "IDENTICAL", "INCOMPARABLE", "CONFLICT",
}
QARSI_PHASES = ("symphony", "recursive", "ultra_fine", "hyper_fine")


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
        seen.add(item);out.append(item)
    return sorted(out)


def _goals(values: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows, seen = [], set()
    for raw in values:
        goal_id = str(raw.get("goal_id") or "").strip()
        if not goal_id:
            raise ValueError("goal_id must be non-empty")
        if goal_id in seen:
            raise ValueError(f"duplicate goal_id: {goal_id}")
        seen.add(goal_id)
        rows.append({
            "goal_id": goal_id,
            "required_capabilities": _names(raw.get("required_capabilities")),
        })
    if len(rows) < 2:
        raise ValueError("PARTY_MULTI_GOAL_REQUIRED: at least two goals are required")
    return sorted(rows, key=lambda row: row["goal_id"])


def _relation_weight(value: str) -> float:
    return {
        "COMMUTATIVE": 1.0,
        "ORDERED": 0.92,
        "INDEPENDENT": 0.86,
        "CONDITIONAL": 0.76,
        "IDENTICAL": 0.68,
        "INCOMPARABLE": 0.60,
        "CONFLICT": 0.0,
    }.get(value, 0.0)


class PartyCoordinationRuntime:
    """Git-shared multi-goal party layer over Message Board V1.

    Party identity and reward receipts are written under the Message Board Git root
    using its fresh-remote CAS/publish path. Message Board V1 remains the sole
    presence/claim/message transport; this layer does not duplicate that subsystem.
    """

    def __init__(self, server):
        self.server = server

    def _board(self) -> MessageBoardRuntime:
        git = getattr(self.server, "git", None)
        if git is None or not git.enabled:
            raise ValueError("ATHENA_GIT_ROOT is required for party coordination")
        return MessageBoardRuntime(git)

    @staticmethod
    def _party_rel(party_id: str) -> str:
        return f"{PARTY_ROOT}/{_require_id(party_id, 'party_id')}.json"

    def _party_path(self, board: MessageBoardRuntime, party_id: str) -> Path:
        return board._root() / self._party_rel(party_id)

    def _read_party(self, board: MessageBoardRuntime, party_id: str) -> Dict[str, Any] | None:
        value = board._read_json(self._party_path(board, party_id))
        if value and value.get("artifact") == PARTY_ARTIFACT:
            return value
        return None

    @staticmethod
    def _presence(board: MessageBoardRuntime, agent_id: str) -> Dict[str, Any] | None:
        return next((row for row in board._active() if row.get("agent_id") == agent_id), None)

    @staticmethod
    def _goal_ids(party: Dict[str, Any]) -> set[str]:
        return {str(goal["goal_id"]) for goal in party.get("goals") or []}

    @staticmethod
    def _members(party: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        value = party.get("members") or {}
        return value if isinstance(value, dict) else {}

    def _communication(self, board: MessageBoardRuntime, party: Dict[str, Any]) -> Dict[str, Any]:
        members = set(self._members(party))
        events = board._events()
        messages = {
            str(event.get("event_id")): event
            for event in events
            if event.get("kind") == "MESSAGE"
            and str(event.get("agent_id")) in members
            and any(str(recipient) in members for recipient in (event.get("recipients") or []))
        }
        acks: Dict[str, List[str]] = {}
        for event in events:
            if event.get("kind") != "ACK" or str(event.get("agent_id")) not in members:
                continue
            message_id = str((event.get("payload") or {}).get("message_id") or "")
            if message_id in messages:
                message = messages[message_id]
                recipients = {str(x) for x in (message.get("recipients") or [])}
                if str(event.get("agent_id")) in recipients:
                    acks.setdefault(message_id, []).append(str(event.get("agent_id")))
        edges, participants = [], set()
        for message_id, ackers in sorted(acks.items()):
            sender = str(messages[message_id].get("agent_id"))
            for receiver in sorted(set(ackers)):
                edges.append({"message_id": message_id, "sender": sender, "acknowledger": receiver})
                participants.update((sender, receiver))
        return {
            "message_count": len(messages),
            "acknowledged_message_count": len(acks),
            "acknowledged_edges": edges,
            "participants": sorted(participants),
            "participant_count": len(participants),
            "law": "MESSAGE_ROUTE != CONSUMPTION; acknowledged routing is coordination evidence, not outcome proof",
        }

    def _score(
        self,
        party: Dict[str, Any],
        communication: Dict[str, Any],
        result_goal_ids: Optional[Iterable[str]] = None,
        shared_frontier_verified: bool = False,
    ) -> Dict[str, Any]:
        members = list(self._members(party).values())
        goals = party.get("goals") or []
        goal_ids = {str(goal["goal_id"]) for goal in goals}

        relation_quality = (
            sum(_relation_weight(str(member.get("task_relation"))) for member in members) / len(members)
            if members else 0.0
        )
        claims = [str(member.get("claim_id") or "") for member in members if member.get("claim_id")]
        claim_diversity = len(set(claims)) / len(claims) if claims else 0.0
        capabilities = [
            capability
            for member in members
            for capability in (member.get("capabilities") or [])
        ]
        capability_novelty = (
            len(set(capabilities)) / len(capabilities) if capabilities else 0.5
        )
        qlearn = 0.45 * relation_quality + 0.35 * claim_diversity + 0.20 * capability_novelty

        assigned = {
            goal
            for member in members
            for goal in (member.get("goal_refs") or [])
            if goal in goal_ids
        }
        goal_coverage = len(assigned) / len(goal_ids) if goal_ids else 0.0
        required = [
            capability
            for goal in goals
            for capability in (goal.get("required_capabilities") or [])
        ]
        available = set(capabilities)
        capability_coverage = (
            sum(1 for capability in required if capability in available) / len(required)
            if required else 1.0
        )
        loads = [len(member.get("goal_refs") or []) for member in members]
        if not loads or max(loads) == 0:
            load_balance = 0.5
        else:
            load_balance = 1.0 - (max(loads) - min(loads)) / max(1.0, float(max(loads)))
        qsear = 0.50 * goal_coverage + 0.30 * capability_coverage + 0.20 * load_balance

        result_set = set(_names(result_goal_ids)) & goal_ids
        advanced_count = len(set(_names(result_goal_ids)))
        symphony = goal_coverage
        recursive = min(1.0, communication.get("participant_count", 0) / max(1.0, float(len(members))))
        ultra_fine = len(result_set) / advanced_count if advanced_count else 0.0
        hyper_fine = 1.0 if (
            advanced_count >= 2
            and len(result_set) == advanced_count
            and communication.get("participant_count", 0) >= 2
            and shared_frontier_verified
        ) else 0.0
        phases = {
            "symphony": symphony,
            "recursive": recursive,
            "ultra_fine": ultra_fine,
            "hyper_fine": hyper_fine,
        }
        qarsi = sum(phases.values()) / 4.0
        synergy = (
            (qlearn * qsear * qarsi) ** (1.0 / 3.0)
            if qlearn > 0 and qsear > 0 and qarsi > 0 else 0.0
        )
        return {
            "big3_version": "PARTY.BIG3.BOARD.BRIDGE.1",
            "big3_cycle": ["Q-LEARN", "Q-SEAR", "Q-ARSI", "Q-LEARN"],
            "qlearn": round(qlearn, 9),
            "qsear": round(qsear, 9),
            "qarsi": round(qarsi, 9),
            "qarsi_phases": {key: round(value, 9) for key, value in phases.items()},
            "qarsi_phase_order": list(QARSI_PHASES),
            "synergy": round(synergy, 9),
            "diagnostics": {
                "relation_quality": round(relation_quality, 9),
                "claim_diversity": round(claim_diversity, 9),
                "capability_novelty": round(capability_novelty, 9),
                "goal_coverage": round(goal_coverage, 9),
                "capability_coverage": round(capability_coverage, 9),
                "load_balance": round(load_balance, 9),
                "communication_participants": communication.get("participant_count", 0),
                "acknowledged_messages": communication.get("acknowledged_message_count", 0),
                "shared_frontier_verified": bool(shared_frontier_verified),
            },
            "epistemic_boundary": (
                "Operational proxy over explicit party and Message Board evidence; not quantum execution, "
                "proof of optimality, outcome proof, or XP authority."
            ),
        }

    def _public_state(
        self,
        board: MessageBoardRuntime,
        party: Dict[str, Any],
        board_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        communication = self._communication(board, party)
        active = {str(row.get("agent_id")): row for row in board_snapshot.get("active") or []}
        member_rows = []
        for agent_id, member in sorted(self._members(party).items()):
            member_rows.append({
                **member,
                "board_presence": active.get(agent_id),
                "board_active": agent_id in active,
            })
        last_results = []
        observations = party.get("observations") or []
        if observations:
            last_results = [result["goal_id"] for result in observations[-1].get("results") or []]
        score = self._score(
            party,
            communication,
            last_results,
            bool(board_snapshot.get("shared_frontier_verified")),
        )
        value = {
            "version": PARTY_VERSION,
            "party": {key: value for key, value in party.items() if key not in {"members", "observations"}},
            "members": member_rows,
            "observations": observations,
            "communication": communication,
            "score": score,
            "board": {
                "status": board_snapshot.get("status"),
                "git_head": board_snapshot.get("git_head"),
                "shared_frontier_verified": bool(board_snapshot.get("shared_frontier_verified")),
            },
            "execution_authority": False,
            "xp_authority": False,
            "law": "PARTY_COORDINATION != EXECUTION_AUTHORITY != XP_AUTHORITY",
        }
        value["state_digest"] = _digest(value)
        return value

    def form(
        self,
        party_id: str,
        leader: str,
        goals: Iterable[Dict[str, Any]],
        leader_goal_refs: Iterable[str],
        purpose: str = "",
        role: str = "LEAD",
        capabilities: Optional[Iterable[str]] = None,
        capacity: int = 4,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        party_id = _require_id(party_id, "party_id")
        leader = _require_id(leader, "leader")
        goal_rows = _goals(goals)
        goal_ids = {row["goal_id"] for row in goal_rows}
        leader_goals = _names(leader_goal_refs)
        if not leader_goals or not set(leader_goals).issubset(goal_ids):
            raise ValueError("leader_goal_refs must be a non-empty subset of party goals")
        capacity = int(capacity)
        if capacity < 2 or capacity > 16:
            raise ValueError("capacity must be between 2 and 16")
        config = {
            "party_id": party_id,
            "leader": leader,
            "purpose": str(purpose or ""),
            "goals": goal_rows,
            "capacity": capacity,
            "leader_goal_refs": leader_goals,
            "role": str(role or "LEAD"),
            "capabilities": _names(capabilities),
        }
        formation_digest = _digest(config)
        board = self._board()

        def build(base):
            existing = self._read_party(board, party_id)
            if existing:
                if existing.get("formation_digest") != formation_digest:
                    raise ValueError(f"PARTY_ID_CONFLICT: {party_id}")
                return {"return": {"status": "ALREADY_FORMED", "party": existing, "idempotent": True}}
            presence = self._presence(board, leader)
            if not presence:
                return {"return": {"status": "LEADER_NOT_PRESENT_HOLD", "party_id": party_id, "leader": leader, "next": "athena_message_board present"}}
            now = _iso()
            member = {
                "agent_id": leader,
                "role": str(role or "LEAD"),
                "goal_refs": leader_goals,
                "capabilities": _names(capabilities),
                "task_relation": "INDEPENDENT",
                "claim_id": presence.get("claim_id"),
                "claim_mode": presence.get("mode"),
                "join_of": presence.get("join_of"),
                "board_task": presence.get("task"),
                "work_key": presence.get("work_key"),
                "joined_at": now,
            }
            party = {
                "artifact": PARTY_ARTIFACT,
                "version": PARTY_VERSION,
                "party_id": party_id,
                "status": "OPEN",
                "leader": leader,
                "purpose": str(purpose or ""),
                "goals": goal_rows,
                "capacity": capacity,
                "members": {leader: member},
                "observations": [],
                "formation_digest": formation_digest,
                "created_at": now,
                "updated_at": now,
                "revision": 1,
                "created_from_git_head": base,
                "message_board_contract": "ATHENA.MESSAGE.BOARD.PRESENCE.V1",
                "law": "PARTY_MEMBERSHIP_COORDINATES_EXISTING_BOARD_CLAIMS; IT DOES_NOT_CREATE_EXECUTION_AUTHORITY",
            }
            event_rel, event = board._event(
                "PARTY_FORM", leader,
                {"party_id": party_id, "goal_ids": sorted(goal_ids), "claim_id": presence.get("claim_id")},
            )
            return {
                "files": {self._party_rel(party_id): _json_text(party), event_rel: _json_text(event)},
                "message": f"party form {party_id}",
                "result": {"status": "PARTY_FORMED", "party": party, "event": event, "idempotent": False},
            }

        result = board._mutate(agent_id=leader, remote=remote, build_files=build)
        result["execution_authority"] = False
        result["xp_bonus"] = 0
        return result

    def join(
        self,
        party_id: str,
        agent: str,
        goal_refs: Iterable[str],
        task_relation: str,
        role: str = "MEMBER",
        capabilities: Optional[Iterable[str]] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        party_id = _require_id(party_id, "party_id")
        agent = _require_id(agent, "agent")
        goals = _names(goal_refs)
        relation = str(task_relation or "").upper()
        if relation not in TASK_RELATIONS:
            raise ValueError(f"invalid task_relation: {relation}")
        if relation == "CONFLICT":
            raise ValueError("PARTY_RELATION_CONFLICT_HOLD")
        board = self._board()

        def build(base):
            party = self._read_party(board, party_id)
            if not party:
                return {"return": {"status": "PARTY_NOT_FOUND_HOLD", "party_id": party_id}}
            if party.get("status") != "OPEN":
                return {"return": {"status": "PARTY_NOT_OPEN_HOLD", "party_id": party_id}}
            goal_ids = self._goal_ids(party)
            if not goals or not set(goals).issubset(goal_ids):
                raise ValueError("goal_refs must be a non-empty subset of party goals")
            members = self._members(party)
            presence = self._presence(board, agent)
            if not presence:
                return {"return": {"status": "AGENT_NOT_PRESENT_HOLD", "agent": agent, "next": "athena_message_board present or join"}}
            profile = {
                "agent_id": agent,
                "role": str(role or "MEMBER"),
                "goal_refs": goals,
                "capabilities": _names(capabilities),
                "task_relation": relation,
                "claim_id": presence.get("claim_id"),
                "claim_mode": presence.get("mode"),
                "join_of": presence.get("join_of"),
                "board_task": presence.get("task"),
                "work_key": presence.get("work_key"),
            }
            profile_digest = _digest(profile)
            if agent in members:
                existing = members[agent]
                if existing.get("profile_digest") != profile_digest:
                    raise ValueError(f"PARTY_MEMBER_PROFILE_CONFLICT: {party_id}/{agent}")
                return {"return": {"status": "ALREADY_JOINED", "party": party, "idempotent": True}}
            if len(members) >= int(party.get("capacity") or 0):
                return {"return": {"status": "PARTY_FULL_HOLD", "party_id": party_id}}
            claims = {str(member.get("claim_id")) for member in members.values()}
            if str(presence.get("claim_id")) in claims:
                raise ValueError("DUPLICATE_PARTY_CLAIM_HOLD")
            if relation == "IDENTICAL" and str(presence.get("mode")) not in {"COLLABORATOR", "REPLICA"}:
                raise ValueError("IDENTICAL_RELATION_REQUIRES_DECLARED_BOARD_COLLABORATION_OR_REPLICA")
            now = _iso()
            profile["joined_at"] = now
            profile["profile_digest"] = profile_digest
            updated = dict(party)
            updated_members = dict(members);updated_members[agent] = profile
            updated["members"] = updated_members
            updated["updated_at"] = now
            updated["revision"] = int(updated.get("revision") or 0) + 1
            event_rel, event = board._event(
                "PARTY_JOIN", agent,
                {"party_id": party_id, "goal_refs": goals, "claim_id": presence.get("claim_id"), "task_relation": relation},
                recipients=[str(party.get("leader"))],
            )
            return {
                "files": {self._party_rel(party_id): _json_text(updated), event_rel: _json_text(event)},
                "message": f"party join {party_id} {agent}",
                "result": {"status": "PARTY_JOINED", "party": updated, "event": event, "idempotent": False},
            }

        result = board._mutate(agent_id=agent, remote=remote, build_files=build)
        result["execution_authority"] = False
        result["xp_bonus"] = 0
        return result

    def state(
        self,
        party_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        party_id = _require_id(party_id, "party_id")
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, include_stale=True, limit=500)
        party = self._read_party(board, party_id)
        if not party:
            raise ValueError(f"PARTY_NOT_FOUND: {party_id}")
        value = self._public_state(board, party, snapshot)
        if shared_remote_mode == "REQUIRED" and not snapshot.get("shared_frontier_verified"):
            value["status"] = "PARTY_SHARED_FRONTIER_HOLD"
        else:
            value["status"] = "OK"
        return value

    def list(
        self,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
        limit: int = 50,
    ) -> Dict[str, Any]:
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=1)
        root = board._root() / PARTY_ROOT
        rows = []
        if root.exists():
            for path in sorted(root.glob("*.json")):
                value = board._read_json(path)
                if value and value.get("artifact") == PARTY_ARTIFACT:
                    rows.append({
                        "party_id": value.get("party_id"),
                        "status": value.get("status"),
                        "leader": value.get("leader"),
                        "purpose": value.get("purpose"),
                        "goal_count": len(value.get("goals") or []),
                        "member_count": len(self._members(value)),
                        "observation_count": len(value.get("observations") or []),
                        "revision": value.get("revision"),
                        "updated_at": value.get("updated_at"),
                    })
        rows.sort(key=lambda row: (str(row.get("updated_at")), str(row.get("party_id"))), reverse=True)
        limit = max(1, min(500, int(limit)))
        return {
            "version": PARTY_VERSION,
            "status": "OK" if snapshot.get("shared_frontier_verified") or shared_remote_mode != "REQUIRED" else "PARTY_SHARED_FRONTIER_HOLD",
            "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
            "parties": rows[:limit],
        }

    def observe(
        self,
        observation_id: str,
        party_id: str,
        observer: str,
        base_xp: float,
        results: Iterable[Dict[str, Any]],
        witness_ref: str,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        observation_id = _require_id(observation_id, "observation_id")
        party_id = _require_id(party_id, "party_id")
        observer = _require_id(observer, "observer")
        witness_ref = str(witness_ref or "").strip()
        if not witness_ref:
            raise ValueError("witness_ref must be non-empty")
        base_xp = float(base_xp)
        if base_xp < 0:
            raise ValueError("base_xp must be non-negative")
        result_rows = []
        seen_goals = set()
        for raw in results:
            goal_id = str(raw.get("goal_id") or "").strip()
            agent_id = _require_id(str(raw.get("agent_id") or ""), "result agent_id")
            result_witness = str(raw.get("witness_ref") or "").strip()
            if not goal_id or not result_witness:
                raise ValueError("every result requires goal_id and witness_ref")
            if goal_id in seen_goals:
                raise ValueError(f"duplicate result goal_id: {goal_id}")
            seen_goals.add(goal_id)
            result_rows.append({"goal_id": goal_id, "agent_id": agent_id, "witness_ref": result_witness})
        result_rows.sort(key=lambda row: row["goal_id"])
        if len(result_rows) < 2:
            raise ValueError("PARTY_MULTI_GOAL_OBSERVATION_REQUIRED: at least two distinct goal results")
        request = {
            "observation_id": observation_id,
            "party_id": party_id,
            "observer": observer,
            "base_xp": base_xp,
            "results": result_rows,
            "witness_ref": witness_ref,
        }
        request_digest = _digest(request)
        board = self._board()

        def build(base):
            party = self._read_party(board, party_id)
            if not party:
                return {"return": {"status": "PARTY_NOT_FOUND_HOLD", "party_id": party_id}}
            observations = list(party.get("observations") or [])
            for stored in observations:
                if stored.get("observation_id") == observation_id:
                    if stored.get("request_digest") != request_digest:
                        raise ValueError(f"PARTY_OBSERVATION_ID_CONFLICT: {observation_id}")
                    replay = dict(stored);replay["idempotent"] = True;replay["durable_return"] = True
                    return {"return": replay}
            goal_ids = self._goal_ids(party)
            members = self._members(party)
            reasons = []
            if len(members) < 2:
                reasons.append("NEED_TWO_MEMBERS")
            result_agents = set()
            for result in result_rows:
                goal_id, agent_id = result["goal_id"], result["agent_id"]
                if goal_id not in goal_ids:
                    reasons.append(f"UNKNOWN_GOAL:{goal_id}")
                    continue
                member = members.get(agent_id)
                if not member:
                    reasons.append(f"RESULT_AGENT_NOT_MEMBER:{agent_id}")
                    continue
                if goal_id not in set(member.get("goal_refs") or []):
                    reasons.append(f"RESULT_GOAL_NOT_ASSIGNED:{agent_id}:{goal_id}")
                    continue
                result_agents.add(agent_id)
            if len(result_agents) < 2:
                reasons.append("NEED_TWO_RESULT_AGENTS")
            communication = self._communication(board, party)
            if communication.get("participant_count", 0) < 2:
                reasons.append("NEED_ACKNOWLEDGED_PARTY_COMMUNICATION")
            prior = next((stored for stored in observations if stored.get("status") == "AWARDED" and stored.get("witness_ref") == witness_ref), None)
            if prior:
                reasons.append("WITNESS_ALREADY_REWARDED")
            score = self._score(party, communication, seen_goals, True)
            if score["synergy"] < 0.35:
                reasons.append("LOW_SYNERGY")
            if base_xp == 0:
                reasons.append("BASE_XP_ZERO")
            if reasons:
                status, bonus_rate, bonus_xp = "HOLD", 0.0, 0.0
            else:
                status = "AWARDED"
                bonus_rate = min(0.05, 0.01 + 0.04 * float(score["synergy"]))
                bonus_xp = round(base_xp * bonus_rate, 6)
            observation = {
                "version": PARTY_VERSION,
                "observation_id": observation_id,
                "party_id": party_id,
                "observer": observer,
                "base_xp": base_xp,
                "results": result_rows,
                "witness_ref": witness_ref,
                "status": status,
                "hold_reasons": sorted(set(reasons)),
                "communication": communication,
                "score": score,
                "coordination_bonus_rate": round(bonus_rate, 9),
                "coordination_bonus_xp": bonus_xp,
                "xp_patch": {
                    "base_xp_observed": base_xp,
                    "coordination_bonus_xp": bonus_xp,
                    "apply_to_global_xp": False,
                },
                "request_digest": request_digest,
                "observed_at": _iso(),
                "observed_git_head": base,
                "idempotent": False,
                "execution_authority": False,
                "xp_authority": False,
                "reward_law": (
                    "bonus requires at least two party members, two assigned goal results by at least two agents, "
                    "and acknowledged Message Board communication; membership alone earns zero XP; bonus <= 5%"
                ),
                "epistemic_boundary": (
                    "witness refs are recorded observations, not independently verified outcome truth; "
                    "this receipt is not global XP authority"
                ),
            }
            observation["receipt_digest"] = _digest({key: value for key, value in observation.items() if key != "idempotent"})
            updated = dict(party)
            updated["observations"] = observations + [observation]
            updated["updated_at"] = _iso()
            updated["revision"] = int(updated.get("revision") or 0) + 1
            event_rel, event = board._event(
                "PARTY_OBSERVE", observer,
                {"party_id": party_id, "observation_id": observation_id, "status": status, "bonus_xp": bonus_xp, "witness_ref": witness_ref},
            )
            return {
                "files": {self._party_rel(party_id): _json_text(updated), event_rel: _json_text(event)},
                "message": f"party observe {party_id} {observation_id}",
                "result": observation,
            }

        return board._mutate(agent_id=observer, remote=remote, build_files=build)

    def benchmark(self) -> Dict[str, Any]:
        try:
            board = self._board()
        except ValueError:
            return {"party_coordination_version": PARTY_VERSION, "party_git_enabled": False}
        root = board._root() / PARTY_ROOT
        parties, observations, awarded, bonus = 0, 0, 0, 0.0
        if root.exists():
            for path in root.glob("*.json"):
                party = board._read_json(path)
                if not party or party.get("artifact") != PARTY_ARTIFACT:
                    continue
                parties += 1
                rows = party.get("observations") or []
                observations += len(rows)
                awarded_rows = [row for row in rows if row.get("status") == "AWARDED"]
                awarded += len(awarded_rows)
                bonus += sum(float(row.get("coordination_bonus_xp") or 0.0) for row in awarded_rows)
        return {
            "party_coordination_version": PARTY_VERSION,
            "party_git_enabled": True,
            "party_count": parties,
            "party_observation_count": observations,
            "party_award_count": awarded,
            "party_coordination_bonus_xp": round(bonus, 6),
        }

    def resource(self) -> Dict[str, Any]:
        return {
            "version": PARTY_VERSION,
            "storage": PARTY_ROOT,
            "transport": "ATHENA Message Board V1",
            "tools": [
                "athena_party_form", "athena_party_join", "athena_party_state",
                "athena_party_list", "athena_party_observe",
            ],
            "big3": {
                "cycle": ["Q-LEARN", "Q-SEAR", "Q-ARSI", "Q-LEARN"],
                "Q-LEARN": "relation, claim, and capability complementarity",
                "Q-SEAR": "multi-goal coverage, capability coverage, and load balance",
                "Q-ARSI": {"phases": list(QARSI_PHASES), "meaning": "assignment -> communication -> results -> shared-frontier closure"},
            },
            "xp": {
                "membership_bonus": 0,
                "max_bonus_rate": 0.05,
                "global_xp_mutation": False,
                "double_count_guard": "same party+witness can receive at most one AWARDED receipt",
            },
            "laws": [
                "Message Board V1 remains the sole presence/claim/message transport",
                "party records are shared Git state written through the Message Board fresh-frontier CAS/publish path",
                "CONFLICT relation is held; IDENTICAL requires board-declared COLLABORATOR or REPLICA state",
                "acknowledged communication is coordination evidence, not outcome proof",
                "party membership grants no execution or claim authority",
                "party reward receipts never directly mutate global XP authority",
                "Big-3 scores are operational proxies, not claims of quantum execution",
            ],
            "benchmark": self.benchmark(),
        }
