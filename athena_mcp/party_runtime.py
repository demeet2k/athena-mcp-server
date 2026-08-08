from __future__ import annotations

import json
import math
import time
from collections import Counter, defaultdict, deque
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

from .identity import digest, event_id
from .qhug_pareto_kernel import solve_kernel

VERSION = "PARTY.RUNTIME.1"
SUITE_VERSION = "BIG3.3x5x7x9.1"
MAX_PARTY_BONUS_RATE = 0.05

FAMILIES = ("MATCH", "BRAID", "PARETO")
VARIANTS = (
    ("FAST", {"fit": 0.58, "balance": 0.10, "communication": 0.12, "resilience": 0.20}),
    ("BALANCED", {"fit": 0.43, "balance": 0.30, "communication": 0.12, "resilience": 0.15}),
    ("COVERAGE", {"fit": 0.66, "balance": 0.16, "communication": 0.06, "resilience": 0.12}),
    ("COMMUNICATION", {"fit": 0.36, "balance": 0.14, "communication": 0.38, "resilience": 0.12}),
    ("RESILIENT", {"fit": 0.40, "balance": 0.14, "communication": 0.12, "resilience": 0.34}),
)
STAGES = (
    "HYDRATE_PARTY",
    "MAP_GOALS",
    "GENERATE_3x5",
    "BRAID_COMMUNICATION",
    "PARETO_ADJUDICATE",
    "VERIFY_GATES",
    "EMIT_CREDITABLE_SUCCESSOR",
)
OUTPUT_HEADS = (
    "party_state",
    "assignment",
    "communication_plan",
    "goal_vector",
    "overlap_risk",
    "synergy_score",
    "xp_multiplier",
    "evidence_requirements",
    "successor_packet",
)
MESSAGE_KINDS = frozenset({"CLAIM", "OFFER", "HANDOFF", "BLOCKER", "DECISION", "RESULT", "VERIFY"})
OBSERVED_STATUSES = frozenset({"OBSERVED", "VERIFIED"})

PARTY_SCHEMA = """
CREATE TABLE IF NOT EXISTS parties(
  party_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  leader TEXT NOT NULL,
  goals_json TEXT NOT NULL,
  channels_json TEXT NOT NULL,
  policy_json TEXT NOT NULL,
  status TEXT NOT NULL,
  version INTEGER NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS party_members(
  party_id TEXT NOT NULL,
  agent TEXT NOT NULL,
  capabilities_json TEXT NOT NULL,
  role TEXT NOT NULL,
  joined_at REAL NOT NULL,
  PRIMARY KEY(party_id,agent)
);
CREATE TABLE IF NOT EXISTS party_messages(
  message_id TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  author TEXT NOT NULL,
  target TEXT NOT NULL,
  kind TEXT NOT NULL,
  body TEXT NOT NULL,
  refs_json TEXT NOT NULL,
  eid TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_party_messages_party_created
  ON party_messages(party_id,created_at);
CREATE TABLE IF NOT EXISTS party_cycles(
  cycle_id TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  decision_digest TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_party_cycles_party_created
  ON party_cycles(party_id,created_at);
CREATE TABLE IF NOT EXISTS party_xp_awards(
  award_id TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  agent TEXT NOT NULL,
  source_xp_ref TEXT NOT NULL,
  base_xp REAL NOT NULL,
  bonus_rate REAL NOT NULL,
  bonus_xp REAL NOT NULL,
  witness_ref TEXT NOT NULL,
  outcome_refs_json TEXT NOT NULL,
  created_at REAL NOT NULL,
  UNIQUE(party_id,agent,source_xp_ref)
);
CREATE INDEX IF NOT EXISTS idx_party_xp_agent
  ON party_xp_awards(party_id,agent,created_at);
"""


def _clean(value: Any, label: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{label} must be non-empty")
    return out


def _finite(value: Any, label: str, minimum: float | None = None) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric") from None
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    if minimum is not None and out < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return out


def _caps(values: Iterable[Any] | None) -> tuple[str, ...]:
    return tuple(sorted({_clean(x, "capability").upper() for x in (values or [])}))


def _goal_rows(goals: Sequence[Any]) -> list[dict[str, Any]]:
    if not goals:
        raise ValueError("goals must be non-empty")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in goals:
        if isinstance(raw, Mapping):
            gid = _clean(raw.get("id"), "goal.id")
            row = {
                "id": gid,
                "weight": _finite(raw.get("weight", 1.0), f"goal[{gid}].weight", 0.0),
                "required_capabilities": list(_caps(raw.get("required_capabilities") or [])),
                "description": str(raw.get("description") or "").strip(),
            }
        else:
            gid = _clean(raw, "goal")
            row = {"id": gid, "weight": 1.0, "required_capabilities": [], "description": ""}
        if gid in seen:
            raise ValueError(f"duplicate goal id: {gid}")
        seen.add(gid)
        out.append(row)
    return out


def _channel_rows(channels: Sequence[Any]) -> list[dict[str, str]]:
    if not channels:
        raise ValueError("channels must be non-empty")
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in channels:
        if isinstance(raw, Mapping):
            cid = _clean(raw.get("id"), "channel.id")
            mode = str(raw.get("mode") or "PARTY_SHARED").strip().upper()
        else:
            cid = _clean(raw, "channel")
            mode = "PARTY_SHARED"
        if cid in seen:
            raise ValueError(f"duplicate channel id: {cid}")
        seen.add(cid)
        out.append({"id": cid, "mode": mode})
    return out


def _fit(required: Sequence[str], capabilities: Sequence[str]) -> float:
    req = set(map(str.upper, required))
    if not req:
        return 1.0
    caps = set(map(str.upper, capabilities))
    return len(req & caps) / len(req)


def _connected(nodes: set[str], edges: set[tuple[str, str]]) -> bool:
    if len(nodes) < 2:
        return False
    adj: dict[str, set[str]] = {n: set() for n in nodes}
    for a, b in edges:
        if a in nodes and b in nodes and a != b:
            adj[a].add(b)
            adj[b].add(a)
    start = min(nodes)
    seen = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in adj[node]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen == nodes


def communication_metrics(
    members: Sequence[str],
    messages: Sequence[Mapping[str, Any]],
    contributors: Iterable[str] | None = None,
) -> dict[str, Any]:
    member_set = set(map(str, members))
    nodes = set(map(str, contributors)) if contributors is not None else set(member_set)
    nodes &= member_set
    directed: set[tuple[str, str]] = set()
    useful = 0
    authored: set[str] = set()
    targeted: set[str] = set()
    kind_counts: Counter[str] = Counter()
    for raw in messages:
        author = str(raw.get("author") or "")
        target = str(raw.get("target") or "")
        kind = str(raw.get("kind") or "").upper()
        if author not in member_set or kind not in MESSAGE_KINDS:
            continue
        useful += 1
        kind_counts[kind] += 1
        authored.add(author)
        if target == "*":
            for other in member_set - {author}:
                directed.add((author, other))
                targeted.add(other)
        elif target in member_set and target != author:
            directed.add((author, target))
            targeted.add(target)
    undirected = {tuple(sorted((a, b))) for a, b in directed if a != b}
    possible_pairs = max(1, len(nodes) * (len(nodes) - 1) // 2)
    reciprocal = 0
    for a, b in combinations(sorted(nodes), 2):
        if (a, b) in directed and (b, a) in directed:
            reciprocal += 1
    reciprocity = reciprocal / possible_pairs
    coverage = len((authored & targeted) & nodes) / max(1, len(nodes))
    connected = _connected(nodes, undirected)
    structured = min(1.0, useful / max(1, 2 * len(nodes)))
    quality = max(0.0, min(1.0, 0.35 * reciprocity + 0.30 * coverage + 0.20 * float(connected) + 0.15 * structured))
    has_coordination_act = any(kind_counts[k] for k in ("HANDOFF", "DECISION", "VERIFY", "RESULT"))
    proper = len(nodes) >= 2 and connected and nodes <= authored and nodes <= targeted and has_coordination_act
    degree = Counter()
    for a, b in undirected:
        if a in member_set and b in member_set:
            degree[a] += 1
            degree[b] += 1
    denom = max(1, len(member_set) - 1)
    centrality = {m: min(1.0, degree[m] / denom) for m in member_set}
    return {
        "proper": proper,
        "quality": quality,
        "connected": connected,
        "reciprocity": reciprocity,
        "coverage": coverage,
        "useful_message_count": useful,
        "kind_counts": dict(sorted(kind_counts.items())),
        "centrality": dict(sorted(centrality.items())),
        "boundary": "communication structure is evidence of coordination traffic, not evidence that message content or downstream claims are true",
    }


def _family_weights(family: str, base: Mapping[str, float]) -> dict[str, float]:
    w = dict(base)
    if family == "MATCH":
        w["fit"] *= 1.25
    elif family == "BRAID":
        w["communication"] *= 1.55
        w["balance"] *= 1.10
    elif family == "PARETO":
        w["balance"] *= 1.25
        w["resilience"] *= 1.35
    total = sum(w.values()) or 1.0
    return {k: v / total for k, v in w.items()}


def _candidate(
    family: str,
    variant: str,
    weights: Mapping[str, float],
    goals: Sequence[Mapping[str, Any]],
    members: Sequence[Mapping[str, Any]],
    comm: Mapping[str, Any],
) -> dict[str, Any]:
    loads: Counter[str] = Counter()
    assignment: dict[str, str] = {}
    fit_values: list[tuple[float, float]] = []
    backup_values: list[tuple[float, float]] = []
    member_count = len(members)
    goal_count = len(goals)
    cap_breadth = max(1, max((len(m["capabilities"]) for m in members), default=1))
    for goal in sorted(goals, key=lambda g: (-float(g["weight"]), str(g["id"]))):
        req = list(goal.get("required_capabilities") or [])
        ranked: list[tuple[float, str, float]] = []
        for member in members:
            agent = str(member["agent"])
            fit = _fit(req, member["capabilities"])
            load_score = 1.0 - min(1.0, loads[agent] / max(1, math.ceil(goal_count / member_count)))
            communication = float((comm.get("centrality") or {}).get(agent, 0.0))
            resilience = min(1.0, len(member["capabilities"]) / cap_breadth) if req else 1.0
            score = (
                weights["fit"] * fit
                + weights["balance"] * load_score
                + weights["communication"] * communication
                + weights["resilience"] * resilience
            )
            ranked.append((score, agent, fit))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        _, winner, winner_fit = ranked[0]
        assignment[str(goal["id"])] = winner
        loads[winner] += 1
        fit_values.append((float(goal["weight"]), winner_fit))
        backup_fit = ranked[1][2] if len(ranked) > 1 else 0.0
        backup_values.append((float(goal["weight"]), backup_fit))
    total_weight = sum(w for w, _ in fit_values) or 1.0
    coverage = sum(w * v for w, v in fit_values) / total_weight
    resilience = sum(w * v for w, v in backup_values) / total_weight
    load_vector = [loads[str(m["agent"])] for m in members]
    load_balance = 1.0 - ((max(load_vector) - min(load_vector)) / max(1, goal_count))
    used = sum(1 for x in load_vector if x > 0)
    parallelism = used / max(1, min(member_count, goal_count))
    comm_alignment = sum(float((comm.get("centrality") or {}).get(a, 0.0)) for a in assignment.values()) / max(1, goal_count)
    overlap_risk = 1.0 - parallelism
    utility = max(
        0.0,
        min(
            1.0,
            0.40 * coverage
            + 0.20 * load_balance
            + 0.15 * comm_alignment
            + 0.15 * parallelism
            + 0.10 * resilience,
        ),
    )
    cid = f"{family}.{variant}"
    return {
        "id": cid,
        "family": family,
        "variant": variant,
        "weights": dict(weights),
        "assignment": dict(sorted(assignment.items())),
        "metrics": {
            "coverage": coverage,
            "load_balance": load_balance,
            "communication_alignment": comm_alignment,
            "parallelism": parallelism,
            "resilience": resilience,
            "overlap_risk": overlap_risk,
            "utility": utility,
        },
    }


def compile_big3_suite(
    goals: Sequence[Mapping[str, Any]],
    members: Sequence[Mapping[str, Any]],
    messages: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(members) < 2:
        raise ValueError("party steering requires at least 2 members")
    if len(goals) < 2:
        raise ValueError("party steering requires at least 2 simultaneous goals")
    member_ids = [str(m["agent"]) for m in members]
    comm = communication_metrics(member_ids, messages)
    candidates: list[dict[str, Any]] = []
    for family in FAMILIES:
        for variant, base in VARIANTS:
            candidates.append(_candidate(family, variant, _family_weights(family, base), goals, members, comm))
    patches = []
    ids = [c["id"] for c in candidates]
    for c in candidates:
        m = c["metrics"]
        patches.append(
            {
                "id": c["id"],
                "value": 10.0 * float(m["utility"]) + 0.001,
                "proof_cost": float(m["overlap_risk"]) + (1.0 - float(m["communication_alignment"])),
                "governance": 1.0 - float(m["load_balance"]),
            }
        )
    kernel = solve_kernel(
        {
            "patches": patches,
            "conflicts": [list(x) for x in combinations(ids, 2)],
            "policy": {"lambda_patch": 0.0, "mu_proof_cost": 0.35, "nu_governance": 0.20},
            "max_component_size": 20,
        }
    )
    tie_ids: set[str] = set()
    optimum = kernel.get("optimum") or {}
    for profile in optimum.get("profiles") or []:
        for witness in profile.get("witness") or []:
            tie_ids.add(str(witness))
    by_id = {c["id"]: c for c in candidates}
    if tie_ids:
        selected_id = sorted(tie_ids)[0]
        fallback = False
    else:
        selected_id = sorted(candidates, key=lambda c: (-float(c["metrics"]["utility"]), c["id"]))[0]["id"]
        fallback = True
    selected = by_id[selected_id]
    synergy_prior = max(
        0.0,
        min(
            1.0,
            0.40 * float(selected["metrics"]["parallelism"])
            + 0.30 * float(selected["metrics"]["load_balance"])
            + 0.30 * float(comm["quality"]),
        ),
    )
    heads = {
        "party_state": {
            "member_count": len(members),
            "goal_count": len(goals),
            "communication_ready": bool(comm["proper"]),
        },
        "assignment": selected["assignment"],
        "communication_plan": {
            "metrics": comm,
            "required_next": [] if comm["proper"] else ["reciprocal cross-agent message", "HANDOFF|DECISION|VERIFY|RESULT coordination act"],
        },
        "goal_vector": [{"id": g["id"], "weight": g["weight"]} for g in goals],
        "overlap_risk": selected["metrics"]["overlap_risk"],
        "synergy_score": {"value": synergy_prior, "status": "PLAN_PRIOR", "causal_claim": False},
        "xp_multiplier": {"status": "LOCKED_UNTIL_OBSERVED_OUTCOMES", "value": 1.0, "maximum": 1.0 + MAX_PARTY_BONUS_RATE},
        "evidence_requirements": [
            ">=2 distinct contributing agents",
            ">=2 distinct observed/verified goals",
            "witness_ref for every credited outcome and imported base-XP receipt",
            "connected reciprocal party communication with a coordination act",
            "unique source_xp_ref to prevent replay/double credit",
        ],
        "successor_packet": {
            "selected_candidate": selected_id,
            "next": "execute assignments -> communicate/handoff -> observe outcomes -> athena_party_credit",
            "durable_return": False,
        },
    }
    assert tuple(heads) == OUTPUT_HEADS
    return {
        "version": VERSION,
        "suite": {
            "version": SUITE_VERSION,
            "shape": {"families": 3, "variants_per_family": 5, "stages": 7, "output_heads": 9},
            "families": list(FAMILIES),
            "variants": [name for name, _ in VARIANTS],
            "stages": list(STAGES),
        },
        "candidate_count": len(candidates),
        "candidates": candidates,
        "pareto": {
            "kernel_version": kernel["version"],
            "selected": selected_id,
            "ties": sorted(tie_ids),
            "fallback": fallback,
            "model_count": kernel["model_count"],
            "assignment_work": kernel["assignment_work"],
        },
        "heads": heads,
        "boundary": "planning synergy is a prior for allocation only; XP remains locked until witnessed outcomes satisfy credit gates",
    }


def _credit_balance(outcomes: Sequence[Mapping[str, Any]]) -> float:
    weights: Counter[str] = Counter()
    for row in outcomes:
        weights[str(row["agent"])] += float(row.get("contribution_weight", 1.0))
    total = sum(weights.values())
    if len(weights) < 2 or total <= 0:
        return 0.0
    shares = [v / total for v in weights.values()]
    hhi = sum(x * x for x in shares)
    n = len(shares)
    lo = 1.0 / n
    return max(0.0, min(1.0, (1.0 - hhi) / max(1e-12, 1.0 - lo)))


def party_bonus_rate(
    member_ids: Sequence[str],
    goal_count: int,
    messages: Sequence[Mapping[str, Any]],
    outcomes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    valid = [
        dict(row)
        for row in outcomes
        if str(row.get("status") or "").upper() in OBSERVED_STATUSES
        and str(row.get("witness_ref") or "").strip()
    ]
    contributors = {str(x.get("agent")) for x in valid}
    observed_goals = {str(x.get("goal_id")) for x in valid}
    comm = communication_metrics(member_ids, messages, contributors)
    gates = {
        "party_size": len(set(member_ids)) >= 2,
        "distinct_contributors": len(contributors) >= 2,
        "multi_goal_observation": len(observed_goals) >= 2,
        "communication": bool(comm["proper"]),
        "witnessed": len(valid) == len(outcomes) and bool(valid),
    }
    active = all(gates.values())
    goal_factor = min(1.0, len(observed_goals) / max(2, min(3, goal_count)))
    balance = _credit_balance(valid)
    synergy = max(0.0, min(1.0, 0.45 * float(comm["quality"]) + 0.30 * goal_factor + 0.25 * balance))
    rate = min(MAX_PARTY_BONUS_RATE, 0.01 + 0.04 * synergy) if active else 0.0
    return {
        "active": active,
        "gates": gates,
        "synergy_score": synergy if active else 0.0,
        "bonus_rate": rate,
        "xp_multiplier": 1.0 + rate,
        "communication": comm,
        "observed_goal_count": len(observed_goals),
        "contributor_count": len(contributors),
        "law": "presence never earns XP; only witnessed, multi-goal, multi-agent, properly communicated contribution unlocks the capped party bonus",
    }


class PartyRuntime:
    def __init__(self, server: Any):
        self.server = server
        self.core = server.core
        self.s = server.store
        with self.s.db:
            self.s.db.executescript(PARTY_SCHEMA)
        self.core.register(
            "TOOL",
            "COLLECTIVE",
            "COORDINATE",
            "PARTY",
            "BIG3_3x5x7x9",
            {"party": "members+goals+channels+messages+witnessed outcomes"},
            {"party_state": "durable", "plan": "3x5x7x9", "xp_bonus": "witness-gated <=5%"},
            constraints={
                "minimum_members_for_bonus": 2,
                "minimum_observed_goals_for_bonus": 2,
                "authority": "NONE",
                "presence_bonus": 0,
                "max_bonus_rate": MAX_PARTY_BONUS_RATE,
            },
            actor="GENESIS.PARTY.1",
            status="CANONICAL",
        )

    def _party(self, party_id: str) -> dict[str, Any]:
        row = self.s.one("SELECT * FROM parties WHERE party_id=?", (_clean(party_id, "party_id"),))
        if not row:
            raise KeyError("unknown party")
        return row

    def _members(self, party_id: str) -> list[dict[str, Any]]:
        rows = self.s.rows(
            "SELECT agent,capabilities_json,role,joined_at FROM party_members WHERE party_id=? ORDER BY joined_at,agent",
            (party_id,),
        )
        return [
            {
                "agent": r["agent"],
                "capabilities": json.loads(r["capabilities_json"]),
                "role": r["role"],
                "joined_at": r["joined_at"],
            }
            for r in rows
        ]

    def _messages(self, party_id: str) -> list[dict[str, Any]]:
        rows = self.s.rows(
            "SELECT message_id,channel,author,target,kind,body,refs_json,eid,created_at FROM party_messages WHERE party_id=? ORDER BY created_at,message_id",
            (party_id,),
        )
        return [{**r, "refs": json.loads(r.pop("refs_json"))} for r in rows]

    def _emit(self, event_type: str, actor: str, payload: Mapping[str, Any]) -> str:
        parent = self.s.head("global")
        pe = parent["eid"] if parent else None
        eid = event_id(event_type, actor, pe, payload)
        ed = digest(payload, 32)
        self.s.put_event(eid, event_type, actor, pe, dict(payload), ed)
        self.s.set_head("global", None, None, eid, ed)
        return eid

    def form(
        self,
        leader: str,
        goals: Sequence[Any],
        channels: Sequence[Any],
        capabilities: Sequence[Any] | None = None,
        name: str | None = None,
        policy: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        leader = _clean(leader, "leader")
        goal_rows = _goal_rows(goals)
        channel_rows = _channel_rows(channels)
        now = time.time()
        party_id = "PARTY." + digest(
            {"leader": leader, "goals": goal_rows, "channels": channel_rows, "nonce": f"{now:.9f}"}, 24
        )
        display_name = str(name or party_id).strip()
        pol = dict(policy or {})
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO parties VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    party_id,
                    display_name,
                    leader,
                    json.dumps(goal_rows, sort_keys=True),
                    json.dumps(channel_rows, sort_keys=True),
                    json.dumps(pol, sort_keys=True),
                    "FORMING",
                    1,
                    now,
                    now,
                ),
            )
            self.s.db.execute(
                "INSERT INTO party_members VALUES(?,?,?,?,?)",
                (party_id, leader, json.dumps(list(_caps(capabilities)), sort_keys=True), "LEADER", now),
            )
        eid = self._emit(
            "PARTY_FORM",
            leader,
            {
                "party_id": party_id,
                "leader": leader,
                "goal_ids": [g["id"] for g in goal_rows],
                "channels": [c["id"] for c in channel_rows],
                "presence_xp": 0,
            },
        )
        return {**self.state(party_id), "event": eid, "bonus_locked": True}

    def join(
        self,
        party_id: str,
        agent: str,
        capabilities: Sequence[Any] | None = None,
        role: str = "MEMBER",
    ) -> dict[str, Any]:
        party = self._party(party_id)
        if party["status"] == "CLOSED":
            raise ValueError("party is closed")
        agent = _clean(agent, "agent")
        now = time.time()
        existing = self.s.one(
            "SELECT agent FROM party_members WHERE party_id=? AND agent=?", (party_id, agent)
        )
        if existing:
            return {**self.state(party_id), "action": "REUSE_MEMBER", "presence_xp": 0}
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO party_members VALUES(?,?,?,?,?)",
                (party_id, agent, json.dumps(list(_caps(capabilities)), sort_keys=True), str(role).upper(), now),
            )
            self.s.db.execute(
                "UPDATE parties SET status='ACTIVE',version=version+1,updated_at=? WHERE party_id=?",
                (now, party_id),
            )
        eid = self._emit(
            "PARTY_JOIN",
            agent,
            {"party_id": party_id, "agent": agent, "role": str(role).upper(), "presence_xp": 0},
        )
        return {**self.state(party_id), "action": "JOINED", "event": eid, "presence_xp": 0}

    def message(
        self,
        party_id: str,
        author: str,
        channel: str,
        target: str,
        kind: str,
        body: str,
        refs: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        party = self._party(party_id)
        author = _clean(author, "author")
        target = _clean(target, "target")
        channel = _clean(channel, "channel")
        kind = _clean(kind, "kind").upper()
        body = _clean(body, "body")
        members = {m["agent"] for m in self._members(party_id)}
        if author not in members:
            raise ValueError("author must be a party member")
        if target != "*" and target not in members:
            raise ValueError("target must be another party member or '*'")
        if target == author:
            raise ValueError("self-targeted message does not count as party communication")
        channels = {c["id"] for c in json.loads(party["channels_json"])}
        if channel not in channels:
            raise ValueError("message channel is not declared by this party")
        if kind not in MESSAGE_KINDS:
            raise ValueError(f"kind must be one of {sorted(MESSAGE_KINDS)}")
        refs = sorted({_clean(x, "ref") for x in (refs or [])})
        payload = {
            "party_id": party_id,
            "channel": channel,
            "author": author,
            "target": target,
            "kind": kind,
            "body_digest": digest(body, 32),
            "refs": refs,
        }
        eid = self._emit("PARTY_MESSAGE", author, payload)
        message_id = "PARTYMSG." + digest({"eid": eid, **payload}, 24)
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO party_messages VALUES(?,?,?,?,?,?,?,?,?,?)",
                (message_id, party_id, channel, author, target, kind, body, json.dumps(refs), eid, time.time()),
            )
        return {
            "message_id": message_id,
            "eid": eid,
            "party_id": party_id,
            "channel": channel,
            "kind": kind,
            "communication": communication_metrics(sorted(members), self._messages(party_id)),
            "xp_delta": 0.0,
            "law": "communication unlocks eligibility but never earns XP by itself",
        }

    def steer(self, party_id: str, actor: str = "agent", persist: bool = True) -> dict[str, Any]:
        party = self._party(party_id)
        members = self._members(party_id)
        goals = json.loads(party["goals_json"])
        messages = self._messages(party_id)
        plan = compile_big3_suite(goals, members, messages)
        plan["party_id"] = party_id
        plan["party_version"] = int(party["version"])
        if not persist:
            return {**plan, "persisted": False}
        frozen = {
            "party_id": party_id,
            "party_version": int(party["version"]),
            "member_ids": [m["agent"] for m in members],
            "goal_ids": [g["id"] for g in goals],
            "selected": plan["pareto"]["selected"],
            "heads": plan["heads"],
        }
        decision_digest = digest(frozen, 32)
        cycle_id = "PARTYCYCLE." + digest({"party": party_id, "decision": decision_digest}, 24)
        existing = self.s.one("SELECT cycle_id FROM party_cycles WHERE cycle_id=?", (cycle_id,))
        if not existing:
            with self.s.db:
                self.s.db.execute(
                    "INSERT INTO party_cycles VALUES(?,?,?,?,?,?)",
                    (
                        cycle_id,
                        party_id,
                        str(actor),
                        json.dumps(plan, sort_keys=True),
                        decision_digest,
                        time.time(),
                    ),
                )
            eid = self._emit(
                "PARTY_STEER",
                str(actor),
                {"party_id": party_id, "cycle_id": cycle_id, "decision_digest": decision_digest},
            )
        else:
            eid = None
        return {
            **plan,
            "persisted": True,
            "cycle_id": cycle_id,
            "decision_digest": decision_digest,
            "event": eid,
        }

    def credit(
        self,
        party_id: str,
        cycle_id: str,
        outcomes: Sequence[Mapping[str, Any]],
        xp_receipts: Sequence[Mapping[str, Any]],
        actor: str = "agent",
    ) -> dict[str, Any]:
        party = self._party(party_id)
        cycle = self.s.one(
            "SELECT cycle_id,party_id FROM party_cycles WHERE cycle_id=?", (_clean(cycle_id, "cycle_id"),)
        )
        if not cycle or cycle["party_id"] != party_id:
            raise ValueError("cycle_id must reference a persisted steering cycle for this party")
        members = self._members(party_id)
        member_ids = [m["agent"] for m in members]
        member_set = set(member_ids)
        goal_ids = {str(g["id"]) for g in json.loads(party["goals_json"])}
        normalized: list[dict[str, Any]] = []
        seen_outcome_refs: set[str] = set()
        for raw in outcomes:
            row = dict(raw)
            outcome_ref = _clean(row.get("outcome_ref"), "outcome_ref")
            if outcome_ref in seen_outcome_refs:
                raise ValueError(f"duplicate outcome_ref: {outcome_ref}")
            seen_outcome_refs.add(outcome_ref)
            agent = _clean(row.get("agent"), "outcome.agent")
            goal_id = _clean(row.get("goal_id"), "outcome.goal_id")
            witness_ref = _clean(row.get("witness_ref"), "outcome.witness_ref")
            status = _clean(row.get("status"), "outcome.status").upper()
            if agent not in member_set:
                raise ValueError(f"outcome agent is not a party member: {agent}")
            if goal_id not in goal_ids:
                raise ValueError(f"outcome goal is not in party goal set: {goal_id}")
            weight = _finite(row.get("contribution_weight", 1.0), "contribution_weight", 0.0)
            normalized.append(
                {
                    "outcome_ref": outcome_ref,
                    "agent": agent,
                    "goal_id": goal_id,
                    "witness_ref": witness_ref,
                    "status": status,
                    "contribution_weight": weight,
                }
            )
        if not normalized:
            raise ValueError("outcomes must be non-empty")
        credit = party_bonus_rate(member_ids, len(goal_ids), self._messages(party_id), normalized)
        if not credit["active"]:
            return {
                "party_id": party_id,
                "cycle_id": cycle_id,
                "status": "BONUS_LOCKED",
                "credit": credit,
                "awards": [],
                "law": "failed gates never mint party XP",
            }
        contributors = {x["agent"] for x in normalized if x["status"] in OBSERVED_STATUSES}
        outcome_refs_by_agent: dict[str, list[str]] = defaultdict(list)
        for row in normalized:
            if row["status"] in OBSERVED_STATUSES:
                outcome_refs_by_agent[row["agent"]].append(row["outcome_ref"])
        receipts: list[dict[str, Any]] = []
        seen_receipts: set[tuple[str, str]] = set()
        for raw in xp_receipts:
            agent = _clean(raw.get("agent"), "xp_receipt.agent")
            source_xp_ref = _clean(raw.get("source_xp_ref"), "source_xp_ref")
            witness_ref = _clean(raw.get("witness_ref"), "xp_receipt.witness_ref")
            base_xp = _finite(raw.get("base_xp"), "base_xp", 0.0)
            key = (agent, source_xp_ref)
            if key in seen_receipts:
                raise ValueError(f"duplicate xp receipt: {key}")
            seen_receipts.add(key)
            if agent not in contributors:
                raise ValueError(f"XP receipt agent lacks a witnessed contribution: {agent}")
            existing = self.s.one(
                "SELECT award_id FROM party_xp_awards WHERE party_id=? AND agent=? AND source_xp_ref=?",
                (party_id, agent, source_xp_ref),
            )
            if existing:
                raise ValueError(f"party XP source already credited: {agent}:{source_xp_ref}")
            receipts.append(
                {
                    "agent": agent,
                    "source_xp_ref": source_xp_ref,
                    "witness_ref": witness_ref,
                    "base_xp": base_xp,
                }
            )
        if not receipts:
            raise ValueError("xp_receipts must be non-empty")
        rate = float(credit["bonus_rate"])
        awards = []
        now = time.time()
        with self.s.db:
            for rec in receipts:
                bonus = round(rec["base_xp"] * rate, 6)
                outcome_refs = sorted(outcome_refs_by_agent[rec["agent"]])
                award_id = "PARTYXP." + digest(
                    {
                        "party": party_id,
                        "agent": rec["agent"],
                        "source_xp_ref": rec["source_xp_ref"],
                        "cycle": cycle_id,
                    },
                    24,
                )
                self.s.db.execute(
                    "INSERT INTO party_xp_awards VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        award_id,
                        party_id,
                        rec["agent"],
                        rec["source_xp_ref"],
                        rec["base_xp"],
                        rate,
                        bonus,
                        rec["witness_ref"],
                        json.dumps(outcome_refs),
                        now,
                    ),
                )
                awards.append(
                    {
                        "award_id": award_id,
                        "agent": rec["agent"],
                        "source_xp_ref": rec["source_xp_ref"],
                        "base_xp": rec["base_xp"],
                        "bonus_rate": rate,
                        "bonus_xp": bonus,
                        "xp_after_party_bonus": round(rec["base_xp"] + bonus, 6),
                        "outcome_refs": outcome_refs,
                    }
                )
        eid = self._emit(
            "PARTY_XP_CREDIT",
            str(actor),
            {
                "party_id": party_id,
                "cycle_id": cycle_id,
                "bonus_rate": rate,
                "award_ids": [x["award_id"] for x in awards],
                "source_xp_refs": [x["source_xp_ref"] for x in awards],
            },
        )
        return {
            "party_id": party_id,
            "cycle_id": cycle_id,
            "status": "BONUS_CREDITED",
            "credit": credit,
            "awards": awards,
            "event": eid,
            "authority": "PARTY_BONUS_LEDGER_ONLY",
            "boundary": "this ledger records only the incremental party bonus over witnessed imported base XP; it does not create or modify the upstream quest XP source",
        }

    def state(self, party_id: str) -> dict[str, Any]:
        party = self._party(party_id)
        members = self._members(party_id)
        messages = self._messages(party_id)
        goals = json.loads(party["goals_json"])
        channels = json.loads(party["channels_json"])
        awards = self.s.rows(
            "SELECT agent,COALESCE(SUM(bonus_xp),0) bonus_xp,COUNT(*) award_count FROM party_xp_awards WHERE party_id=? GROUP BY agent ORDER BY agent",
            (party_id,),
        )
        latest = self.s.one(
            "SELECT cycle_id,decision_digest,created_at FROM party_cycles WHERE party_id=? ORDER BY created_at DESC LIMIT 1",
            (party_id,),
        )
        return {
            "version": VERSION,
            "party_id": party_id,
            "name": party["name"],
            "leader": party["leader"],
            "status": party["status"],
            "party_version": int(party["version"]),
            "goals": goals,
            "channels": channels,
            "members": members,
            "communication": communication_metrics([m["agent"] for m in members], messages),
            "latest_cycle": latest,
            "party_bonus_totals": awards,
            "rules": {
                "presence_xp": 0,
                "minimum_bonus_members": 2,
                "minimum_observed_goals": 2,
                "max_bonus_rate": MAX_PARTY_BONUS_RATE,
                "requires_proper_communication": True,
                "requires_witnessed_contribution": True,
                "replay_guard": "UNIQUE(party_id,agent,source_xp_ref)",
            },
        }

    def list(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        if status:
            rows = self.s.rows(
                "SELECT party_id,name,leader,status,version,created_at,updated_at FROM parties WHERE status=? ORDER BY updated_at DESC LIMIT ?",
                (str(status).upper(), limit),
            )
        else:
            rows = self.s.rows(
                "SELECT party_id,name,leader,status,version,created_at,updated_at FROM parties ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        return rows

    def benchmark(self) -> dict[str, Any]:
        q = lambda table: self.s.one(f"SELECT COUNT(*) n FROM {table}")["n"]
        return {
            "version": VERSION,
            "parties": q("parties"),
            "party_members": q("party_members"),
            "party_messages": q("party_messages"),
            "party_cycles": q("party_cycles"),
            "party_xp_awards": q("party_xp_awards"),
            "suite": SUITE_VERSION,
        }
