from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from typing import Any, Dict, Mapping, Sequence

from .identity import digest
from .party_board_bridge import PartyBoardBridge, VERSION as PARTY_BOARD_BRIDGE_VERSION
from .party_protocol import PARTY_RESOURCE, PARTY_TOOL_NAMES, PARTY_TOOLS
from .party_runtime import OBSERVED_STATUSES, PartyRuntime, party_bonus_rate


PARTY_SURFACE_VERSION = "PARTY.SURFACE.3"
PARTY_GUARD_SCHEMA = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_party_xp_source_global
  ON party_xp_awards(agent,source_xp_ref);
CREATE TABLE IF NOT EXISTS party_credit_outcomes(
  outcome_ref TEXT PRIMARY KEY,
  party_id TEXT NOT NULL,
  cycle_id TEXT NOT NULL,
  agent TEXT NOT NULL,
  goal_id TEXT NOT NULL,
  witness_ref TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_party_credit_outcomes_cycle
  ON party_credit_outcomes(party_id,cycle_id,created_at);
"""


def _text(value: Any, label: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{label} must be non-empty")
    return out


def _nonnegative(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric") from None
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    if out < 0:
        raise ValueError(f"{label} must be >= 0")
    return out


class PartySurface:
    """Native AOR surface for shared agent parties and bounded synergy credit.

    PartyRuntime owns local semantic/credit persistence. PartyBoardBridge binds
    presence, collaboration and message transport to canonical Message Board V1.
    XP eligibility therefore requires both current-cycle party semantics and a
    revalidated shared-Git Message Board event; local-only chat never qualifies.
    """

    def __init__(self, server: Any):
        self.server = server
        self.runtime = PartyRuntime(server)
        self.bridge = PartyBoardBridge(server, self.runtime)
        self.s = server.store
        with self.s.db:
            self.s.db.executescript(PARTY_GUARD_SCHEMA)

    def _decorate_state(self, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            return value
        rules = value.get("rules")
        if isinstance(rules, dict):
            rules["communication_scope"] = "CURRENT_CYCLE_SHARED_MESSAGE_BOARD_EVENTS_ONLY_FOR_XP"
            rules["replay_guard"] = "GLOBAL UNIQUE(agent,source_xp_ref) + UNIQUE(outcome_ref)"
            rules["shared_coordination"] = "MESSAGE_BOARD_V1_REQUIRED_FOR_PUBLIC_PARTY_IO"
        party_id = value.get("party_id")
        if party_id:
            try:
                party = self.runtime._party(str(party_id))
                policy = json.loads(party["policy_json"])
                value["message_board_binding"] = policy.get("message_board")
            except Exception:
                value.setdefault("message_board_binding", None)
        value.setdefault("shared_coordination", "MESSAGE_BOARD_V1")
        return value

    def _cycle_credit(
        self,
        party_id: str,
        cycle_id: str,
        outcomes: Sequence[Mapping[str, Any]],
        xp_receipts: Sequence[Mapping[str, Any]],
        actor: str = "agent",
        remote: str = "origin",
    ) -> Dict[str, Any]:
        party = self.runtime._party(party_id)
        cycle_id = _text(cycle_id, "cycle_id")
        cycle = self.s.one(
            "SELECT cycle_id,party_id FROM party_cycles WHERE cycle_id=?", (cycle_id,)
        )
        if not cycle or cycle["party_id"] != party_id:
            raise ValueError("cycle_id must reference a persisted steering cycle for this party")

        members = self.runtime._members(party_id)
        member_ids = [m["agent"] for m in members]
        member_set = set(member_ids)
        goal_ids = {str(g["id"]) for g in json.loads(party["goals_json"])}

        normalized: list[dict[str, Any]] = []
        seen_outcomes: set[str] = set()
        for raw in outcomes:
            row = dict(raw)
            outcome_ref = _text(row.get("outcome_ref"), "outcome_ref")
            if outcome_ref in seen_outcomes:
                raise ValueError(f"duplicate outcome_ref: {outcome_ref}")
            seen_outcomes.add(outcome_ref)
            agent = _text(row.get("agent"), "outcome.agent")
            goal_id = _text(row.get("goal_id"), "outcome.goal_id")
            witness_ref = _text(row.get("witness_ref"), "outcome.witness_ref")
            status = _text(row.get("status"), "outcome.status").upper()
            if status not in OBSERVED_STATUSES:
                raise ValueError(f"outcome.status must be one of {sorted(OBSERVED_STATUSES)}")
            if agent not in member_set:
                raise ValueError(f"outcome agent is not a party member: {agent}")
            if goal_id not in goal_ids:
                raise ValueError(f"outcome goal is not in party goal set: {goal_id}")
            normalized.append(
                {
                    "outcome_ref": outcome_ref,
                    "agent": agent,
                    "goal_id": goal_id,
                    "witness_ref": witness_ref,
                    "status": status,
                    "contribution_weight": _nonnegative(
                        row.get("contribution_weight", 1.0), "contribution_weight"
                    ),
                }
            )
        if not normalized:
            raise ValueError("outcomes must be non-empty")

        cycle_messages, board_receipt = self.bridge.verified_cycle_messages(
            party_id,
            cycle_id,
            remote=str(remote or "origin"),
        )
        credit = party_bonus_rate(member_ids, len(goal_ids), cycle_messages, normalized)
        credit["communication_scope"] = "CURRENT_CYCLE_SHARED_MESSAGE_BOARD_EVENTS_ONLY"
        credit["cycle_id"] = cycle_id
        credit["message_board"] = board_receipt
        if not credit["active"]:
            return {
                "party_id": party_id,
                "cycle_id": cycle_id,
                "status": "BONUS_LOCKED",
                "credit": credit,
                "awards": [],
                "law": "presence, historical/local-only chat, and planning do not mint XP; current-cycle Message Board-witnessed synergy must satisfy every gate",
            }

        contributors = {x["agent"] for x in normalized}
        outcome_refs_by_agent: dict[str, list[str]] = defaultdict(list)
        for row in normalized:
            outcome_refs_by_agent[row["agent"]].append(row["outcome_ref"])

        receipts: list[dict[str, Any]] = []
        seen_receipts: set[tuple[str, str]] = set()
        for raw in xp_receipts:
            agent = _text(raw.get("agent"), "xp_receipt.agent")
            source_xp_ref = _text(raw.get("source_xp_ref"), "source_xp_ref")
            witness_ref = _text(raw.get("witness_ref"), "xp_receipt.witness_ref")
            base_xp = _nonnegative(raw.get("base_xp"), "base_xp")
            key = (agent, source_xp_ref)
            if key in seen_receipts:
                raise ValueError(f"duplicate xp receipt: {key}")
            seen_receipts.add(key)
            if agent not in contributors:
                raise ValueError(f"XP receipt agent lacks a witnessed contribution: {agent}")
            existing = self.s.one(
                "SELECT award_id,party_id FROM party_xp_awards WHERE agent=? AND source_xp_ref=? LIMIT 1",
                (agent, source_xp_ref),
            )
            if existing:
                raise ValueError(
                    f"upstream XP receipt already received party credit: {agent}:{source_xp_ref}"
                )
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

        for row in normalized:
            existing = self.s.one(
                "SELECT party_id,cycle_id FROM party_credit_outcomes WHERE outcome_ref=?",
                (row["outcome_ref"],),
            )
            if existing:
                raise ValueError(
                    f"observed outcome already used for party credit: {row['outcome_ref']}"
                )

        rate = float(credit["bonus_rate"])
        awards: list[dict[str, Any]] = []
        now = time.time()
        with self.s.db:
            for row in normalized:
                self.s.db.execute(
                    "INSERT INTO party_credit_outcomes VALUES(?,?,?,?,?,?,?)",
                    (
                        row["outcome_ref"],
                        party_id,
                        cycle_id,
                        row["agent"],
                        row["goal_id"],
                        row["witness_ref"],
                        now,
                    ),
                )
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

        eid = self.runtime._emit(
            "PARTY_XP_CREDIT",
            str(actor),
            {
                "party_id": party_id,
                "cycle_id": cycle_id,
                "bonus_rate": rate,
                "communication_scope": "CURRENT_CYCLE_SHARED_MESSAGE_BOARD_EVENTS_ONLY",
                "message_board_git_head": board_receipt.get("message_board_git_head"),
                "award_ids": [x["award_id"] for x in awards],
                "source_xp_refs": [x["source_xp_ref"] for x in awards],
                "outcome_refs": sorted(seen_outcomes),
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
            "boundary": "only the incremental party bonus is stored; upstream quest XP is imported by reference and is never created, rewritten, or treated as evidence authority here",
        }

    def call_tool(self, name: str, args: Dict[str, Any]):
        if name not in PARTY_TOOL_NAMES:
            return False, None
        if name == "athena_party_form":
            return True, self._decorate_state(self.bridge.form(args))
        if name == "athena_party_join":
            return True, self._decorate_state(self.bridge.join(args))
        if name == "athena_party_message":
            return True, self.bridge.message(args)
        if name == "athena_party_steer":
            return True, self.runtime.steer(
                args["party_id"], args.get("actor", "agent"), args.get("persist", True)
            )
        if name == "athena_party_credit":
            return True, self._cycle_credit(
                args["party_id"],
                args["cycle_id"],
                args["outcomes"],
                args["xp_receipts"],
                args.get("actor", "agent"),
                args.get("remote", "origin"),
            )
        if name == "athena_party_state":
            return True, self._decorate_state(self.runtime.state(args["party_id"]))
        if name == "athena_party_list":
            return True, self.runtime.list(args.get("status"), args.get("limit", 100))
        raise KeyError(name)

    def read_resource(self, uri: str) -> Dict[str, Any]:
        if uri != PARTY_RESOURCE["uri"]:
            raise KeyError(uri)
        return {
            "version": PARTY_SURFACE_VERSION,
            "runtime": self.runtime.benchmark(),
            "parties": self.runtime.list(limit=100),
            "shared_coordination": {
                "substrate": "MESSAGE_BOARD_V1",
                "bridge_version": PARTY_BOARD_BRIDGE_VERSION,
                "available": self.bridge.available(),
                "law": "form/join/message use Message Board V1; XP accepts only cycle-scoped local messages whose shared board events revalidate after a fresh shared-Git sync",
            },
            "big3": {
                "shape": "3 strategy families x 5 variants x 7 stages x 9 output heads",
                "families": ["MATCH", "BRAID", "PARETO"],
                "pareto_kernel": "QHUG.PARETO-KERNEL.23.2",
            },
            "xp_law": {
                "formation_xp": 0,
                "join_presence_xp": 0,
                "message_xp": 0,
                "planning_xp": 0,
                "maximum_party_bonus_rate": 0.05,
                "minimum_contributors": 2,
                "minimum_observed_goals": 2,
                "communication_scope": "current-cycle shared Message Board events only",
                "source_receipt_replay_guard": "global per agent",
                "outcome_replay_guard": "global outcome_ref",
            },
            "boundary": "party state is coordination and bonus-ledger state; Message Board routing is not message consumption or truth; neither surface becomes Y1 evidence authority and neither replaces upstream quest XP accounting",
        }

    def benchmark(self) -> Dict[str, Any]:
        out = dict(self.runtime.benchmark())
        out["party_credit_outcomes"] = self.s.one(
            "SELECT COUNT(*) n FROM party_credit_outcomes"
        )["n"]
        out["party_surface"] = PARTY_SURFACE_VERSION
        out["party_message_board_bridge"] = PARTY_BOARD_BRIDGE_VERSION
        out["party_shared_board_available"] = self.bridge.available()
        return out


__all__ = [
    "PARTY_RESOURCE",
    "PARTY_TOOL_NAMES",
    "PARTY_TOOLS",
    "PartySurface",
]
