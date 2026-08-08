from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from .identity import digest
from .message_board import MessageBoardRuntime
from .party_runtime import MESSAGE_KINDS, PartyRuntime, _channel_rows, _goal_rows


VERSION = "PARTY.MESSAGE-BOARD-BRIDGE.1"
PARTY_MESSAGE_ARTIFACT = "ATHENA.PARTY.MESSAGE.V1"

_KIND_MAP = {
    "CLAIM": "UPDATE",
    "OFFER": "HELP",
    "HANDOFF": "HANDOFF",
    "BLOCKER": "BLOCKER",
    "DECISION": "UPDATE",
    "RESULT": "DISCOVERY",
    "VERIFY": "ANSWER",
}


class PartyBoardBridge:
    """Map party coordination onto the canonical shared Message Board V1.

    The board is the inter-agent presence/transport substrate. The party SQLite
    tables are a local semantic/credit projection. A local party message never
    becomes XP-eligible unless it carries a Message Board event id that can be
    revalidated after a fresh shared-remote synchronization.
    """

    def __init__(self, server: Any, runtime: PartyRuntime):
        self.server = server
        self.runtime = runtime
        self._board_runtime: MessageBoardRuntime | None = None

    def available(self) -> bool:
        git = getattr(self.server, "git", None)
        return bool(git is not None and git.enabled)

    def board(self) -> MessageBoardRuntime:
        if not self.available():
            raise ValueError("ATHENA_GIT_ROOT is required for shared party coordination")
        if self._board_runtime is None:
            self._board_runtime = MessageBoardRuntime(self.server.git)
        return self._board_runtime

    @staticmethod
    def _board_success(value: Mapping[str, Any], *statuses: str) -> bool:
        return str(value.get("status") or "") in set(statuses) and bool(value.get("durable_return", True))

    @staticmethod
    def _goal_targets(goals: Sequence[Mapping[str, Any]]) -> list[str]:
        return [f"party-goal:{str(row['id'])}" for row in goals]

    @staticmethod
    def _task_text(name: str | None, goals: Sequence[Mapping[str, Any]]) -> str:
        goal_ids = ", ".join(str(row["id"]) for row in goals)
        prefix = str(name or "Agent party").strip() or "Agent party"
        return f"{prefix} :: synergistically steer goals [{goal_ids}]"

    @staticmethod
    def _work_key(name: str | None, goals: Sequence[Mapping[str, Any]]) -> str:
        semantic = {
            "name": str(name or "").strip(),
            "goals": [
                {
                    "id": str(row["id"]),
                    "weight": float(row["weight"]),
                    "required_capabilities": list(row.get("required_capabilities") or []),
                }
                for row in goals
            ],
        }
        return "party:" + digest(semantic, 24)

    def _existing_party_for_work(self, leader: str, work_key: str) -> dict[str, Any] | None:
        rows = self.runtime.s.rows(
            "SELECT party_id,leader,policy_json,status FROM parties WHERE leader=? AND status<>'CLOSED' ORDER BY created_at DESC",
            (leader,),
        )
        for row in rows:
            try:
                policy = json.loads(row["policy_json"])
            except Exception:
                continue
            board = policy.get("message_board") or {}
            if str(board.get("work_key") or "") == work_key:
                return self.runtime.state(row["party_id"])
        return None

    def form(self, args: Mapping[str, Any]) -> dict[str, Any]:
        leader = str(args["leader"]).strip()
        goals = _goal_rows(args["goals"])
        channels = _channel_rows(args["channels"])
        name = args.get("name")
        remote = str(args.get("remote") or "origin")
        work_key = self._work_key(name, goals)
        existing = self._existing_party_for_work(leader, work_key)
        if existing:
            return {
                **existing,
                "action": "REUSE_PARTY",
                "presence_xp": 0,
                "shared_coordination": "MESSAGE_BOARD_V1",
            }
        if not self.available():
            return {
                "status": "PARTY_SHARED_BOARD_HOLD",
                "reason": "ATHENA_GIT_ROOT is required before forming a shared agent party",
                "presence_xp": 0,
                "durable_return": False,
                "shared_coordination": "MESSAGE_BOARD_V1_REQUIRED",
            }

        task = self._task_text(name, goals)
        board_result = self.board().present(
            agent_id=leader,
            task=task,
            work_key=work_key,
            targets=self._goal_targets(goals),
            details="Forming ATHENA party; party formation itself grants zero XP.",
            remote=remote,
        )
        if not self._board_success(board_result, "PRESENT", "ALREADY_PRESENT"):
            return {
                "status": "PARTY_FORM_BOARD_HOLD",
                "presence_xp": 0,
                "shared_message_board": board_result,
                "durable_return": False,
                "next": board_result.get("next") or "resolve Message Board hold before party formation",
            }

        presence = board_result.get("presence") or {}
        policy = dict(args.get("policy") or {})
        policy["message_board"] = {
            "version": VERSION,
            "required": True,
            "leader": leader,
            "root_claim_id": presence.get("claim_id"),
            "work_key": work_key,
            "task": task,
            "remote": remote,
        }
        try:
            formed = self.runtime.form(
                leader,
                goals,
                channels,
                args.get("capabilities"),
                name,
                policy,
            )
        except Exception:
            try:
                self.board().release(
                    agent_id=leader,
                    release_status="ABANDONED",
                    outcome="party formation failed after board claim",
                    remote=remote,
                )
            except Exception:
                pass
            raise
        formed["status"] = "PARTY_FORMED"
        formed["shared_coordination"] = "MESSAGE_BOARD_V1"
        formed["shared_message_board"] = board_result
        formed["durable_return"] = bool(board_result.get("durable_return"))
        formed["presence_xp"] = 0
        return formed

    def _board_policy(self, party_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        party = self.runtime._party(party_id)
        try:
            policy = json.loads(party["policy_json"])
        except Exception:
            policy = {}
        board = dict(policy.get("message_board") or {})
        if not board.get("required"):
            raise ValueError("party is not bound to Message Board V1")
        return party, board

    def join(self, args: Mapping[str, Any]) -> dict[str, Any]:
        party_id = str(args["party_id"])
        agent = str(args["agent"]).strip()
        party, board_policy = self._board_policy(party_id)
        leader = str(party["leader"])
        remote = str(args.get("remote") or board_policy.get("remote") or "origin")
        if not self.available():
            return {
                "status": "PARTY_SHARED_BOARD_HOLD",
                "party_id": party_id,
                "agent": agent,
                "presence_xp": 0,
                "durable_return": False,
            }

        joined = self.board().join(
            agent_id=agent,
            join_agent_id=leader,
            task=f"Join {party.get('name') or party_id} as synergistic collaborator",
            details=f"party_id={party_id}; role={str(args.get('role') or 'MEMBER').upper()}",
            remote=remote,
        )
        board_ok = self._board_success(joined, "JOINED")
        if not board_ok and str(joined.get("status")) == "AGENT_ALREADY_PRESENT_HOLD":
            presence = joined.get("presence") or {}
            board_ok = bool(
                str(presence.get("mode")) == "COLLABORATOR"
                and str(presence.get("join_of") or "") == str(board_policy.get("root_claim_id") or "")
            )
        if not board_ok:
            return {
                "status": "PARTY_JOIN_BOARD_HOLD",
                "party_id": party_id,
                "agent": agent,
                "presence_xp": 0,
                "shared_message_board": joined,
                "durable_return": False,
                "next": joined.get("next") or "resolve Message Board presence before joining party",
            }

        result = self.runtime.join(
            party_id,
            agent,
            args.get("capabilities"),
            args.get("role", "MEMBER"),
        )
        result["shared_coordination"] = "MESSAGE_BOARD_V1"
        result["shared_message_board"] = joined
        result["durable_return"] = bool(joined.get("durable_return", True))
        result["presence_xp"] = 0
        return result

    def _validate_message(self, args: Mapping[str, Any]) -> tuple[dict[str, Any], list[str], str]:
        party_id = str(args["party_id"])
        party, board_policy = self._board_policy(party_id)
        author = str(args["author"]).strip()
        target = str(args["target"]).strip()
        channel = str(args["channel"]).strip()
        kind = str(args["kind"]).upper().strip()
        body = str(args["body"]).strip()
        members = {row["agent"] for row in self.runtime._members(party_id)}
        if author not in members:
            raise ValueError("author must be a party member")
        if target != "*" and target not in members:
            raise ValueError("target must be another party member or '*'")
        if target == author:
            raise ValueError("self-targeted message does not count as party communication")
        channels = {row["id"] for row in json.loads(party["channels_json"])}
        if channel not in channels:
            raise ValueError("message channel is not declared by this party")
        if kind not in MESSAGE_KINDS:
            raise ValueError(f"kind must be one of {sorted(MESSAGE_KINDS)}")
        if not body:
            raise ValueError("body must be non-empty")
        refs = sorted({str(x).strip() for x in (args.get("refs") or []) if str(x).strip()})
        return board_policy, refs, body

    def message(self, args: Mapping[str, Any]) -> dict[str, Any]:
        party_id = str(args["party_id"])
        author = str(args["author"]).strip()
        target = str(args["target"]).strip()
        channel = str(args["channel"]).strip()
        kind = str(args["kind"]).upper().strip()
        board_policy, refs, body = self._validate_message(args)
        remote = str(args.get("remote") or board_policy.get("remote") or "origin")
        if not self.available():
            return {
                "status": "PARTY_SHARED_BOARD_HOLD",
                "party_id": party_id,
                "xp_delta": 0.0,
                "durable_return": False,
            }

        snapshot = self.board().read(
            agent_id=author,
            limit=100,
            include_stale=False,
            remote=remote,
            shared_remote_mode="REQUIRED",
        )
        if snapshot.get("status") != "OK" or not snapshot.get("shared_frontier_verified"):
            return {
                "status": "PARTY_MESSAGE_BOARD_FRESHNESS_HOLD",
                "party_id": party_id,
                "xp_delta": 0.0,
                "shared_message_board": snapshot,
                "durable_return": False,
            }
        active = {str(row.get("agent_id")) for row in snapshot.get("active") or []}
        if author not in active:
            return {
                "status": "PARTY_AUTHOR_NOT_PRESENT_HOLD",
                "party_id": party_id,
                "author": author,
                "xp_delta": 0.0,
                "durable_return": False,
            }
        if target != "*" and target not in active:
            return {
                "status": "PARTY_RECIPIENT_NOT_PRESENT_HOLD",
                "party_id": party_id,
                "target": target,
                "xp_delta": 0.0,
                "durable_return": False,
            }

        packet = {
            "artifact": PARTY_MESSAGE_ARTIFACT,
            "party_id": party_id,
            "channel": channel,
            "kind": kind,
            "author": author,
            "target": target,
            "body": body,
            "body_digest": digest(body, 32),
            "refs": refs,
            "xp_delta": 0,
        }
        board_result = self.board().post(
            agent_id=author,
            message=json.dumps(packet, sort_keys=True, ensure_ascii=False),
            message_kind=_KIND_MAP[kind],
            recipients=[] if target == "*" else [target],
            remote=remote,
        )
        if not self._board_success(board_result, "POSTED"):
            return {
                "status": "PARTY_MESSAGE_BOARD_HOLD",
                "party_id": party_id,
                "xp_delta": 0.0,
                "shared_message_board": board_result,
                "durable_return": False,
            }
        event = board_result.get("message_event") or {}
        board_event_id = str(event.get("event_id") or "")
        if not board_event_id:
            raise ValueError("Message Board POSTED result missing message event id")
        result = self.runtime.message(
            party_id,
            author,
            channel,
            target,
            kind,
            body,
            refs=[*refs, board_event_id],
        )
        result["status"] = "PARTY_MESSAGE_POSTED"
        result["shared_coordination"] = "MESSAGE_BOARD_V1"
        result["shared_message_board"] = board_result
        result["message_board_event_id"] = board_event_id
        result["durable_return"] = bool(board_result.get("durable_return"))
        result["xp_delta"] = 0.0
        return result

    @staticmethod
    def _event_packet(event: Mapping[str, Any]) -> dict[str, Any] | None:
        if str(event.get("kind") or "") != "MESSAGE":
            return None
        payload = event.get("payload") or {}
        raw = payload.get("message")
        if not isinstance(raw, str):
            return None
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return packet if isinstance(packet, dict) else None

    def verified_cycle_messages(
        self,
        party_id: str,
        cycle_id: str,
        remote: str = "origin",
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if not self.available():
            return [], {
                "status": "PARTY_SHARED_BOARD_HOLD",
                "shared_frontier_verified": False,
                "verified_party_messages": 0,
            }
        snapshot = self.board().read(
            limit=500,
            include_stale=True,
            remote=remote,
            shared_remote_mode="REQUIRED",
        )
        if snapshot.get("status") != "OK" or not snapshot.get("shared_frontier_verified"):
            return [], {
                "status": "PARTY_MESSAGE_BOARD_FRESHNESS_HOLD",
                "shared_frontier_verified": False,
                "snapshot": snapshot,
                "verified_party_messages": 0,
            }
        events = {str(row.get("event_id")): row for row in self.board()._events()}
        verified: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for local in self.runtime._messages(party_id):
            refs = [str(x) for x in (local.get("refs") or [])]
            if cycle_id not in refs:
                continue
            board_ids = [ref for ref in refs if ref.startswith("MBE-")]
            accepted = False
            for event_id in board_ids:
                event = events.get(event_id)
                packet = self._event_packet(event or {})
                if not packet:
                    continue
                expected_recipients = [] if str(local.get("target")) == "*" else [str(local.get("target"))]
                recipients = [str(x) for x in (event.get("recipients") or [])]
                if (
                    packet.get("artifact") == PARTY_MESSAGE_ARTIFACT
                    and str(packet.get("party_id")) == party_id
                    and str(packet.get("channel")) == str(local.get("channel"))
                    and str(packet.get("kind")) == str(local.get("kind"))
                    and str(packet.get("author")) == str(local.get("author"))
                    and str(packet.get("target")) == str(local.get("target"))
                    and str(packet.get("body")) == str(local.get("body"))
                    and str(packet.get("body_digest")) == digest(str(local.get("body")), 32)
                    and cycle_id in [str(x) for x in (packet.get("refs") or [])]
                    and str(event.get("agent_id")) == str(local.get("author"))
                    and recipients == expected_recipients
                ):
                    accepted = True
                    break
            if accepted:
                verified.append(local)
            else:
                rejected.append({"message_id": local.get("message_id"), "reason": "NO_MATCHING_SHARED_BOARD_EVENT"})
        return verified, {
            "status": "VERIFIED_SHARED_PARTY_MESSAGES",
            "shared_frontier_verified": True,
            "verified_party_messages": len(verified),
            "rejected_cycle_messages": rejected,
            "message_board_git_head": snapshot.get("git_head"),
            "law": "LOCAL_PARTY_MESSAGE != SHARED_COMMUNICATION_WITNESS; XP uses only cycle-scoped messages revalidated against Message Board V1 after shared-fresh sync",
        }
