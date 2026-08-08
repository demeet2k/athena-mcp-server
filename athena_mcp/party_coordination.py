from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Dict, Iterable, List, Optional

PARTY_VERSION = "PARTY.COORDINATION.1"
TASK_RELATIONS = {
    "IDENTICAL",
    "INDEPENDENT",
    "COMMUTATIVE",
    "ORDERED",
    "CONDITIONAL",
    "CONFLICT",
    "INCOMPARABLE",
}
POST_KINDS = {"WORKING_ON", "NEED", "OFFER", "DECISION", "BLOCKER", "RESULT"}
COORDINATION_MODES = {"PARALLEL_COMPLEMENT", "INDEPENDENT_VERIFY"}
QARSI_PHASES = ("symphony", "recursive", "ultra_fine", "hyper_fine")

SCHEMA = """
CREATE TABLE IF NOT EXISTS party_coordination_parties(
  party_id TEXT PRIMARY KEY,
  task_ref TEXT NOT NULL,
  purpose TEXT NOT NULL,
  status TEXT NOT NULL,
  leader TEXT NOT NULL,
  capacity INTEGER NOT NULL,
  goals_json TEXT NOT NULL,
  channels_json TEXT NOT NULL,
  config_digest TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL,
  version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS party_coordination_members(
  party_id TEXT NOT NULL,
  agent TEXT NOT NULL,
  role TEXT NOT NULL,
  capabilities_json TEXT NOT NULL,
  claim_refs_json TEXT NOT NULL,
  channel_ref TEXT NOT NULL,
  task_relation TEXT NOT NULL,
  coordination_mode TEXT NOT NULL,
  profile_digest TEXT NOT NULL,
  joined_at REAL NOT NULL,
  PRIMARY KEY(party_id,agent),
  FOREIGN KEY(party_id) REFERENCES party_coordination_parties(party_id)
);
CREATE TABLE IF NOT EXISTS party_coordination_posts(
  post_id TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  agent TEXT NOT NULL,
  kind TEXT NOT NULL,
  channel_ref TEXT NOT NULL,
  body TEXT NOT NULL,
  goal_refs_json TEXT NOT NULL,
  claim_refs_json TEXT NOT NULL,
  witness_ref TEXT,
  request_digest TEXT NOT NULL,
  created_at REAL NOT NULL,
  FOREIGN KEY(party_id) REFERENCES party_coordination_parties(party_id)
);
CREATE TABLE IF NOT EXISTS party_coordination_observations(
  observation_id TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  observer TEXT NOT NULL,
  base_xp REAL NOT NULL,
  advanced_goal_ids_json TEXT NOT NULL,
  witness_ref TEXT NOT NULL,
  status TEXT NOT NULL,
  bonus_rate REAL NOT NULL,
  bonus_xp REAL NOT NULL,
  request_digest TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at REAL NOT NULL,
  FOREIGN KEY(party_id) REFERENCES party_coordination_parties(party_id)
);
CREATE INDEX IF NOT EXISTS idx_party_members_party ON party_coordination_members(party_id);
CREATE INDEX IF NOT EXISTS idx_party_posts_party ON party_coordination_posts(party_id,created_at);
CREATE INDEX IF NOT EXISTS idx_party_observations_party ON party_coordination_observations(party_id,created_at);
CREATE INDEX IF NOT EXISTS idx_party_observations_witness ON party_coordination_observations(party_id,witness_ref);
"""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _names(values: Optional[Iterable[Any]]) -> List[str]:
    out = []
    seen = set()
    for value in values or []:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return sorted(out)


def _goal_rows(goals: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    seen = set()
    for raw in goals:
        goal_id = str(raw.get("goal_id") or "").strip()
        if not goal_id:
            raise ValueError("goal_id must be non-empty")
        if goal_id in seen:
            raise ValueError(f"duplicate goal_id: {goal_id}")
        seen.add(goal_id)
        rows.append(
            {
                "goal_id": goal_id,
                "required_capabilities": _names(raw.get("required_capabilities")),
            }
        )
    if len(rows) < 2:
        raise ValueError("PARTY_MULTI_GOAL_REQUIRED: form_party requires at least two goals")
    return sorted(rows, key=lambda row: row["goal_id"])


class PartyCoordinationRuntime:
    """Persistent, authority-neutral party/message-board coordination.

    The Big-3 score is an operational bridge over explicit party evidence:
    Q-LEARN -> pattern/complementarity score,
    Q-SEAR  -> multi-goal capability/allocation score,
    Q-ARSI  -> four-phase refinement score.

    It is deliberately not represented as quantum execution or proof of outcome.
    XP is issued only as a persisted coordination-bonus receipt after an observed
    outcome witness; this runtime does not mutate any global XP authority.
    """

    def __init__(self, server):
        self.server = server
        self.store = server.store
        self.db = self.store.db
        self._lock = self.store._lock
        with self._lock, self.db:
            self.db.executescript(SCHEMA)

    def _one(self, sql: str, args=()):
        row = self.db.execute(sql, args).fetchone()
        return dict(row) if row else None

    def _rows(self, sql: str, args=()):
        return [dict(row) for row in self.db.execute(sql, args).fetchall()]

    def _party(self, party_id: str) -> Dict[str, Any]:
        row = self._one(
            "SELECT * FROM party_coordination_parties WHERE party_id=?",
            (party_id,),
        )
        if row is None:
            raise ValueError(f"PARTY_NOT_FOUND: {party_id}")
        return row

    @staticmethod
    def _loads(value: str):
        return json.loads(value)

    def _members(self, party_id: str) -> List[Dict[str, Any]]:
        rows = self._rows(
            "SELECT * FROM party_coordination_members WHERE party_id=? ORDER BY joined_at,agent",
            (party_id,),
        )
        for row in rows:
            row["capabilities"] = self._loads(row.pop("capabilities_json"))
            row["claim_refs"] = self._loads(row.pop("claim_refs_json"))
        return rows

    def _posts(self, party_id: str) -> List[Dict[str, Any]]:
        rows = self._rows(
            "SELECT * FROM party_coordination_posts WHERE party_id=? ORDER BY created_at,post_id",
            (party_id,),
        )
        for row in rows:
            row["goal_refs"] = self._loads(row.pop("goal_refs_json"))
            row["claim_refs"] = self._loads(row.pop("claim_refs_json"))
        return rows

    def _observations(self, party_id: str) -> List[Dict[str, Any]]:
        rows = self._rows(
            "SELECT payload_json FROM party_coordination_observations WHERE party_id=? ORDER BY created_at,observation_id",
            (party_id,),
        )
        return [self._loads(row["payload_json"]) for row in rows]

    @staticmethod
    def _relation_weight(relation: str, mode: str) -> float:
        if relation == "COMMUTATIVE":
            return 1.0
        if relation == "ORDERED":
            return 0.92
        if relation == "INDEPENDENT":
            return 0.86
        if relation == "CONDITIONAL":
            return 0.76
        if relation == "INCOMPARABLE":
            return 0.62
        if relation == "IDENTICAL" and mode == "INDEPENDENT_VERIFY":
            return 0.66
        return 0.0

    def _score(
        self,
        party: Dict[str, Any],
        members: List[Dict[str, Any]],
        posts: List[Dict[str, Any]],
        advanced_goal_ids: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        goals = self._loads(party["goals_json"])
        channels = set(self._loads(party["channels_json"]))
        goal_ids = {goal["goal_id"] for goal in goals}

        relations = [
            self._relation_weight(member["task_relation"], member["coordination_mode"])
            for member in members
        ]
        relation_quality = sum(relations) / len(relations) if relations else 0.0

        all_claims = [claim for member in members for claim in member["claim_refs"]]
        unique_claims = len(set(all_claims))
        claim_complementarity = (
            unique_claims / len(all_claims) if all_claims else 0.5
        )

        all_capabilities = [
            capability for member in members for capability in member["capabilities"]
        ]
        capability_novelty = (
            len(set(all_capabilities)) / len(all_capabilities)
            if all_capabilities
            else 0.5
        )
        qlearn = (
            0.45 * relation_quality
            + 0.35 * claim_complementarity
            + 0.20 * capability_novelty
        )

        available_capabilities = set(all_capabilities)
        required = [
            capability
            for goal in goals
            for capability in goal.get("required_capabilities", [])
        ]
        capability_coverage = (
            sum(1 for capability in required if capability in available_capabilities)
            / len(required)
            if required
            else 1.0
        )

        active_goal_ids = {
            goal_ref
            for post in posts
            if post["kind"] in {"WORKING_ON", "NEED", "OFFER", "DECISION", "RESULT"}
            for goal_ref in post["goal_refs"]
            if goal_ref in goal_ids
        }
        goal_activity_coverage = (
            len(active_goal_ids) / len(goal_ids) if goal_ids else 0.0
        )

        work_load = {member["agent"]: len(member["claim_refs"]) for member in members}
        for post in posts:
            if post["kind"] == "WORKING_ON" and post["agent"] in work_load:
                work_load[post["agent"]] += max(1, len(post["goal_refs"]))
        loads = list(work_load.values())
        if not loads or max(loads) == 0:
            load_balance = 0.5
        else:
            load_balance = 1.0 - (max(loads) - min(loads)) / max(1.0, float(max(loads)))
        qsear = (
            0.50 * capability_coverage
            + 0.30 * goal_activity_coverage
            + 0.20 * load_balance
        )

        active_posters = {
            post["agent"]
            for post in posts
            if post["kind"] in {"WORKING_ON", "NEED", "OFFER", "DECISION", "RESULT"}
        }
        witnessed_decision_or_result = any(
            post["kind"] in {"DECISION", "RESULT"} and post.get("witness_ref")
            for post in posts
        )
        witnessed_results = [
            post
            for post in posts
            if post["kind"] == "RESULT" and post.get("witness_ref")
        ]
        advanced = set(_names(advanced_goal_ids))
        symphony = min(1.0, len(active_goal_ids) / max(1.0, float(len(goal_ids))))
        recursive = min(1.0, len(active_posters) / max(1.0, float(len(members))))
        ultra_fine = 1.0 if witnessed_decision_or_result else 0.0
        hyper_fine = (
            min(1.0, len(advanced & goal_ids) / max(1.0, float(len(goal_ids))))
            if witnessed_results and advanced
            else 0.0
        )
        phases = {
            "symphony": symphony,
            "recursive": recursive,
            "ultra_fine": ultra_fine,
            "hyper_fine": hyper_fine,
        }
        qarsi = sum(phases.values()) / 4.0

        synergy = (
            (max(0.0, qlearn) * max(0.0, qsear) * max(0.0, qarsi)) ** (1.0 / 3.0)
            if qlearn > 0 and qsear > 0 and qarsi > 0
            else 0.0
        )

        member_channels_valid = all(
            member["channel_ref"] in channels for member in members
        )
        board_channels_valid = all(post["channel_ref"] in channels for post in posts)
        joiners = [member for member in members if member["agent"] != party["leader"]]
        duplicate_only = bool(joiners) and all(
            member["task_relation"] == "IDENTICAL" for member in joiners
        )

        return {
            "big3_version": "PARTY.BIG3.BRIDGE.1",
            "big3_cycle": ["Q-LEARN", "Q-SEAR", "Q-ARSI", "Q-LEARN"],
            "qlearn": round(qlearn, 9),
            "qsear": round(qsear, 9),
            "qarsi": round(qarsi, 9),
            "qarsi_phases": {k: round(v, 9) for k, v in phases.items()},
            "qarsi_phase_order": list(QARSI_PHASES),
            "synergy": round(synergy, 9),
            "diagnostics": {
                "relation_quality": round(relation_quality, 9),
                "claim_complementarity": round(claim_complementarity, 9),
                "capability_novelty": round(capability_novelty, 9),
                "capability_coverage": round(capability_coverage, 9),
                "goal_activity_coverage": round(goal_activity_coverage, 9),
                "load_balance": round(load_balance, 9),
                "active_posters": len(active_posters),
                "active_goals": len(active_goal_ids),
                "witnessed_results": len(witnessed_results),
                "member_channels_valid": member_channels_valid,
                "board_channels_valid": board_channels_valid,
                "duplicate_only": duplicate_only,
            },
            "epistemic_boundary": (
                "Operational evidence score inspired by the registered Big-3 semantics; "
                "it is not quantum execution, proof of optimality, or outcome authority."
            ),
        }

    def _state(self, party_id: str) -> Dict[str, Any]:
        party = self._party(party_id)
        members = self._members(party_id)
        posts = self._posts(party_id)
        observations = self._observations(party_id)
        last_advanced = observations[-1]["advanced_goal_ids"] if observations else []
        score = self._score(party, members, posts, last_advanced)
        public_party = {
            "party_id": party["party_id"],
            "task_ref": party["task_ref"],
            "purpose": party["purpose"],
            "status": party["status"],
            "leader": party["leader"],
            "capacity": party["capacity"],
            "goals": self._loads(party["goals_json"]),
            "channels": self._loads(party["channels_json"]),
            "created_at": party["created_at"],
            "updated_at": party["updated_at"],
            "version": party["version"],
        }
        state = {
            "version": PARTY_VERSION,
            "party": public_party,
            "members": members,
            "posts": posts,
            "observations": observations,
            "score": score,
            "execution_authority": False,
            "claim_authority": False,
            "law": (
                "party membership coordinates explicit claims and communication only; "
                "it never authorizes execution or mutates another agent's claim"
            ),
        }
        state["state_digest"] = _digest(state)
        return state

    def form(
        self,
        party_id: str,
        task_ref: str,
        leader: str,
        goals: Iterable[Dict[str, Any]],
        channels: Iterable[str],
        purpose: str = "",
        capacity: int = 4,
        role: str = "LEAD",
        capabilities: Optional[Iterable[str]] = None,
        claim_refs: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        party_id = str(party_id).strip()
        task_ref = str(task_ref).strip()
        leader = str(leader).strip()
        if not party_id or not task_ref or not leader:
            raise ValueError("party_id, task_ref, and leader must be non-empty")
        capacity = int(capacity)
        if capacity < 2 or capacity > 16:
            raise ValueError("capacity must be between 2 and 16")
        goal_rows = _goal_rows(goals)
        channel_rows = _names(channels)
        if not channel_rows:
            raise ValueError("PARTY_CHANNEL_REQUIRED: at least one communication channel is required")
        leader_profile = {
            "agent": leader,
            "role": str(role or "LEAD").strip() or "LEAD",
            "capabilities": _names(capabilities),
            "claim_refs": _names(claim_refs),
            "channel_ref": channel_rows[0],
            "task_relation": "INDEPENDENT",
            "coordination_mode": "PARALLEL_COMPLEMENT",
        }
        config = {
            "party_id": party_id,
            "task_ref": task_ref,
            "purpose": str(purpose or ""),
            "leader": leader,
            "capacity": capacity,
            "goals": goal_rows,
            "channels": channel_rows,
            "leader_profile": leader_profile,
        }
        config_digest = _digest(config)
        now = time.time()
        with self._lock, self.db:
            existing = self._one(
                "SELECT config_digest FROM party_coordination_parties WHERE party_id=?",
                (party_id,),
            )
            if existing:
                if existing["config_digest"] != config_digest:
                    raise ValueError(f"PARTY_ID_CONFLICT: {party_id}")
                result = self._state(party_id)
                result["idempotent"] = True
                return result
            self.db.execute(
                """INSERT INTO party_coordination_parties
                   (party_id,task_ref,purpose,status,leader,capacity,goals_json,channels_json,
                    config_digest,created_at,updated_at,version)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    party_id,
                    task_ref,
                    str(purpose or ""),
                    "OPEN",
                    leader,
                    capacity,
                    _canonical(goal_rows),
                    _canonical(channel_rows),
                    config_digest,
                    now,
                    now,
                    1,
                ),
            )
            self.db.execute(
                """INSERT INTO party_coordination_members
                   (party_id,agent,role,capabilities_json,claim_refs_json,channel_ref,
                    task_relation,coordination_mode,profile_digest,joined_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    party_id,
                    leader,
                    leader_profile["role"],
                    _canonical(leader_profile["capabilities"]),
                    _canonical(leader_profile["claim_refs"]),
                    leader_profile["channel_ref"],
                    leader_profile["task_relation"],
                    leader_profile["coordination_mode"],
                    _digest(leader_profile),
                    now,
                ),
            )
        result = self._state(party_id)
        result["idempotent"] = False
        result["event"] = "PARTY_FORMED"
        return result

    def join(
        self,
        party_id: str,
        agent: str,
        channel_ref: str,
        task_relation: str,
        role: str = "MEMBER",
        capabilities: Optional[Iterable[str]] = None,
        claim_refs: Optional[Iterable[str]] = None,
        coordination_mode: str = "PARALLEL_COMPLEMENT",
    ) -> Dict[str, Any]:
        party_id = str(party_id).strip()
        agent = str(agent).strip()
        channel_ref = str(channel_ref).strip()
        task_relation = str(task_relation).strip().upper()
        coordination_mode = str(coordination_mode).strip().upper()
        if not party_id or not agent or not channel_ref:
            raise ValueError("party_id, agent, and channel_ref must be non-empty")
        if task_relation not in TASK_RELATIONS:
            raise ValueError(f"invalid task_relation: {task_relation}")
        if coordination_mode not in COORDINATION_MODES:
            raise ValueError(f"invalid coordination_mode: {coordination_mode}")
        if task_relation == "CONFLICT":
            raise ValueError("PARTY_RELATION_CONFLICT_HOLD: conflicting work must be resolved before joining")
        if task_relation == "IDENTICAL" and coordination_mode != "INDEPENDENT_VERIFY":
            raise ValueError(
                "DUPLICATE_WORK_HOLD: IDENTICAL work may join only as explicit INDEPENDENT_VERIFY"
            )
        profile = {
            "agent": agent,
            "role": str(role or "MEMBER").strip() or "MEMBER",
            "capabilities": _names(capabilities),
            "claim_refs": _names(claim_refs),
            "channel_ref": channel_ref,
            "task_relation": task_relation,
            "coordination_mode": coordination_mode,
        }
        profile_digest = _digest(profile)
        now = time.time()
        with self._lock, self.db:
            party = self._party(party_id)
            if party["status"] != "OPEN":
                raise ValueError(f"PARTY_NOT_OPEN: {party_id}")
            channels = set(self._loads(party["channels_json"]))
            if channel_ref not in channels:
                raise ValueError(
                    f"PARTY_CHANNEL_MISMATCH: {channel_ref} is not a registered party channel"
                )
            existing = self._one(
                "SELECT profile_digest FROM party_coordination_members WHERE party_id=? AND agent=?",
                (party_id, agent),
            )
            if existing:
                if existing["profile_digest"] != profile_digest:
                    raise ValueError(
                        f"PARTY_MEMBER_PROFILE_CONFLICT: {party_id}/{agent}"
                    )
                result = self._state(party_id)
                result["idempotent"] = True
                return result
            count = self._one(
                "SELECT COUNT(*) AS n FROM party_coordination_members WHERE party_id=?",
                (party_id,),
            )["n"]
            if int(count) >= int(party["capacity"]):
                raise ValueError(f"PARTY_FULL: {party_id}")
            incoming_claims = set(profile["claim_refs"])
            if incoming_claims:
                for member in self._members(party_id):
                    overlap = incoming_claims & set(member["claim_refs"])
                    if (
                        overlap
                        and coordination_mode != "INDEPENDENT_VERIFY"
                        and task_relation != "ORDERED"
                    ):
                        raise ValueError(
                            "DUPLICATE_CLAIM_HOLD: overlapping claims "
                            + ",".join(sorted(overlap))
                        )
            self.db.execute(
                """INSERT INTO party_coordination_members
                   (party_id,agent,role,capabilities_json,claim_refs_json,channel_ref,
                    task_relation,coordination_mode,profile_digest,joined_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    party_id,
                    agent,
                    profile["role"],
                    _canonical(profile["capabilities"]),
                    _canonical(profile["claim_refs"]),
                    channel_ref,
                    task_relation,
                    coordination_mode,
                    profile_digest,
                    now,
                ),
            )
            self.db.execute(
                "UPDATE party_coordination_parties SET updated_at=?,version=version+1 WHERE party_id=?",
                (now, party_id),
            )
        result = self._state(party_id)
        result["idempotent"] = False
        result["event"] = "PARTY_JOINED"
        return result

    def board_post(
        self,
        post_id: str,
        party_id: str,
        agent: str,
        kind: str,
        channel_ref: str,
        body: str,
        goal_refs: Optional[Iterable[str]] = None,
        claim_refs: Optional[Iterable[str]] = None,
        witness_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        post_id = str(post_id).strip()
        party_id = str(party_id).strip()
        agent = str(agent).strip()
        kind = str(kind).strip().upper()
        channel_ref = str(channel_ref).strip()
        body = str(body).strip()
        if not post_id or not body:
            raise ValueError("post_id and body must be non-empty")
        if kind not in POST_KINDS:
            raise ValueError(f"invalid post kind: {kind}")
        goals = _names(goal_refs)
        claims = _names(claim_refs)
        witness = str(witness_ref).strip() if witness_ref is not None else None
        if kind in {"DECISION", "RESULT"} and not witness:
            raise ValueError(f"{kind}_WITNESS_REQUIRED")
        request = {
            "post_id": post_id,
            "party_id": party_id,
            "agent": agent,
            "kind": kind,
            "channel_ref": channel_ref,
            "body": body,
            "goal_refs": goals,
            "claim_refs": claims,
            "witness_ref": witness,
        }
        request_digest = _digest(request)
        now = time.time()
        with self._lock, self.db:
            party = self._party(party_id)
            member = self._one(
                "SELECT agent FROM party_coordination_members WHERE party_id=? AND agent=?",
                (party_id, agent),
            )
            if member is None:
                raise ValueError(f"PARTY_MEMBERSHIP_REQUIRED: {agent}")
            channels = set(self._loads(party["channels_json"]))
            if channel_ref not in channels:
                raise ValueError(f"PARTY_CHANNEL_MISMATCH: {channel_ref}")
            goal_ids = {goal["goal_id"] for goal in self._loads(party["goals_json"])}
            unknown_goals = set(goals) - goal_ids
            if unknown_goals:
                raise ValueError(
                    "UNKNOWN_PARTY_GOAL: " + ",".join(sorted(unknown_goals))
                )
            existing = self._one(
                "SELECT request_digest FROM party_coordination_posts WHERE post_id=?",
                (post_id,),
            )
            if existing:
                if existing["request_digest"] != request_digest:
                    raise ValueError(f"PARTY_POST_ID_CONFLICT: {post_id}")
                result = self._state(party_id)
                result["idempotent"] = True
                return result
            self.db.execute(
                """INSERT INTO party_coordination_posts
                   (post_id,party_id,agent,kind,channel_ref,body,goal_refs_json,
                    claim_refs_json,witness_ref,request_digest,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    post_id,
                    party_id,
                    agent,
                    kind,
                    channel_ref,
                    body,
                    _canonical(goals),
                    _canonical(claims),
                    witness,
                    request_digest,
                    now,
                ),
            )
            self.db.execute(
                "UPDATE party_coordination_parties SET updated_at=?,version=version+1 WHERE party_id=?",
                (now, party_id),
            )
        result = self._state(party_id)
        result["idempotent"] = False
        result["event"] = "PARTY_BOARD_POSTED"
        result["post_id"] = post_id
        return result

    def observe(
        self,
        observation_id: str,
        party_id: str,
        observer: str,
        base_xp: float,
        advanced_goal_ids: Iterable[str],
        witness_ref: str,
    ) -> Dict[str, Any]:
        observation_id = str(observation_id).strip()
        party_id = str(party_id).strip()
        observer = str(observer).strip()
        witness_ref = str(witness_ref).strip()
        advanced = _names(advanced_goal_ids)
        base_xp = float(base_xp)
        if not observation_id or not observer or not witness_ref:
            raise ValueError("observation_id, observer, and witness_ref must be non-empty")
        if base_xp < 0:
            raise ValueError("base_xp must be non-negative")
        if len(advanced) < 2:
            raise ValueError("PARTY_MULTI_GOAL_OBSERVATION_REQUIRED: at least two advanced goals")
        request = {
            "observation_id": observation_id,
            "party_id": party_id,
            "observer": observer,
            "base_xp": base_xp,
            "advanced_goal_ids": advanced,
            "witness_ref": witness_ref,
        }
        request_digest = _digest(request)
        now = time.time()
        with self._lock, self.db:
            existing = self._one(
                "SELECT request_digest,payload_json FROM party_coordination_observations WHERE observation_id=?",
                (observation_id,),
            )
            if existing:
                if existing["request_digest"] != request_digest:
                    raise ValueError(
                        f"PARTY_OBSERVATION_ID_CONFLICT: {observation_id}"
                    )
                result = self._loads(existing["payload_json"])
                result["idempotent"] = True
                return result

            party = self._party(party_id)
            members = self._members(party_id)
            posts = self._posts(party_id)
            goal_ids = {goal["goal_id"] for goal in self._loads(party["goals_json"])}
            unknown = set(advanced) - goal_ids
            if unknown:
                raise ValueError("UNKNOWN_PARTY_GOAL: " + ",".join(sorted(unknown)))

            score = self._score(party, members, posts, advanced)
            d = score["diagnostics"]
            reasons: List[str] = []
            if len(members) < 2:
                reasons.append("NEED_TWO_MEMBERS")
            if len(goal_ids) < 2:
                reasons.append("NEED_MULTIPLE_GOALS")
            if d["active_posters"] < 2:
                reasons.append("NEED_TWO_COMMUNICATING_MEMBERS")
            if d["witnessed_results"] < 1:
                reasons.append("NEED_WITNESSED_RESULT_POST")
            if not d["member_channels_valid"] or not d["board_channels_valid"]:
                reasons.append("COMMUNICATION_CHANNEL_INVALID")
            if d["duplicate_only"]:
                reasons.append("DUPLICATE_ONLY_PARTY")
            if score["synergy"] < 0.35:
                reasons.append("LOW_SYNERGY")
            if base_xp == 0:
                reasons.append("BASE_XP_ZERO")

            prior_witness = self._one(
                """SELECT observation_id FROM party_coordination_observations
                   WHERE party_id=? AND witness_ref=? AND status='AWARDED' LIMIT 1""",
                (party_id, witness_ref),
            )
            if prior_witness:
                reasons.append("WITNESS_ALREADY_REWARDED")

            if reasons:
                status = "HOLD"
                bonus_rate = 0.0
                bonus_xp = 0.0
            else:
                status = "AWARDED"
                bonus_rate = min(0.05, 0.01 + 0.04 * float(score["synergy"]))
                bonus_xp = round(base_xp * bonus_rate, 6)

            payload = {
                "version": PARTY_VERSION,
                "observation_id": observation_id,
                "party_id": party_id,
                "observer": observer,
                "advanced_goal_ids": advanced,
                "witness_ref": witness_ref,
                "status": status,
                "hold_reasons": reasons,
                "score": score,
                "base_xp": base_xp,
                "coordination_bonus_rate": round(bonus_rate, 9),
                "coordination_bonus_xp": bonus_xp,
                "xp_patch": {
                    "base_xp_observed": base_xp,
                    "coordination_bonus_xp": bonus_xp,
                    "apply_to_global_xp": False,
                },
                "reward_law": (
                    "bonus requires observed multi-goal progress, two-way party communication, "
                    "and a witnessed result; membership alone earns no XP; bonus is capped at 5%"
                ),
                "execution_authority": False,
                "idempotent": False,
            }
            payload["receipt_digest"] = _digest(payload)
            self.db.execute(
                """INSERT INTO party_coordination_observations
                   (observation_id,party_id,observer,base_xp,advanced_goal_ids_json,witness_ref,
                    status,bonus_rate,bonus_xp,request_digest,payload_json,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    observation_id,
                    party_id,
                    observer,
                    base_xp,
                    _canonical(advanced),
                    witness_ref,
                    status,
                    bonus_rate,
                    bonus_xp,
                    request_digest,
                    _canonical(payload),
                    now,
                ),
            )
            self.db.execute(
                "UPDATE party_coordination_parties SET updated_at=?,version=version+1 WHERE party_id=?",
                (now, party_id),
            )
        return payload

    def state(self, party_id: str) -> Dict[str, Any]:
        return self._state(str(party_id).strip())

    def list(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        args: List[Any] = []
        where = ""
        if status:
            where = "WHERE status=?"
            args.append(str(status).upper())
        args.append(limit)
        rows = self._rows(
            f"""SELECT party_id,task_ref,purpose,status,leader,capacity,updated_at,version
                FROM party_coordination_parties {where}
                ORDER BY updated_at DESC,party_id LIMIT ?""",
            tuple(args),
        )
        for row in rows:
            counts = self._one(
                """SELECT
                   (SELECT COUNT(*) FROM party_coordination_members WHERE party_id=?) AS members,
                   (SELECT COUNT(*) FROM party_coordination_posts WHERE party_id=?) AS posts,
                   (SELECT COUNT(*) FROM party_coordination_observations WHERE party_id=? AND status='AWARDED') AS awards""",
                (row["party_id"], row["party_id"], row["party_id"]),
            )
            row.update(counts)
        return rows

    def benchmark(self) -> Dict[str, Any]:
        def count(table: str) -> int:
            return int(self._one(f"SELECT COUNT(*) AS n FROM {table}")["n"])

        award = self._one(
            """SELECT COUNT(*) AS n,COALESCE(SUM(bonus_xp),0) AS xp
               FROM party_coordination_observations WHERE status='AWARDED'"""
        )
        return {
            "party_coordination_version": PARTY_VERSION,
            "party_count": count("party_coordination_parties"),
            "party_member_count": count("party_coordination_members"),
            "party_board_post_count": count("party_coordination_posts"),
            "party_observation_count": count("party_coordination_observations"),
            "party_award_count": int(award["n"]),
            "party_coordination_bonus_xp": float(award["xp"]),
        }

    def resource(self) -> Dict[str, Any]:
        return {
            "version": PARTY_VERSION,
            "tools": [
                "athena_party_form",
                "athena_party_join",
                "athena_party_board_post",
                "athena_party_state",
                "athena_party_list",
                "athena_party_observe",
            ],
            "task_relations": sorted(TASK_RELATIONS),
            "coordination_modes": sorted(COORDINATION_MODES),
            "post_kinds": sorted(POST_KINDS),
            "big3": {
                "cycle": ["Q-LEARN", "Q-SEAR", "Q-ARSI", "Q-LEARN"],
                "Q-LEARN": "pattern/claim/capability complementarity from explicit party state",
                "Q-SEAR": "multi-goal capability coverage, activity coverage, and load balance",
                "Q-ARSI": {
                    "phases": list(QARSI_PHASES),
                    "meaning": "progressive evidence refinement from exploration to witnessed result",
                },
            },
            "xp": {
                "award_trigger": "athena_party_observe",
                "membership_bonus": 0,
                "max_bonus_rate": 0.05,
                "global_xp_mutation": False,
                "double_count_guard": "same party+witness cannot receive a second awarded coordination bonus",
            },
            "laws": [
                "party is a coordination primitive, not an authority grant",
                "CONFLICT work is held; IDENTICAL work requires explicit INDEPENDENT_VERIFY",
                "overlapping claims are held unless ordered or explicit independent verification",
                "messages must use a registered party channel and RESULT/DECISION require witnesses",
                "XP is receipt-gated by observed multi-goal progress and witnessed communication/results",
                "Big-3 scores are operational proxies over observed party evidence, not claims of quantum execution",
            ],
            "benchmark": self.benchmark(),
        }
