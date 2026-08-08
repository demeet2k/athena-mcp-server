from __future__ import annotations

import json
import math
from typing import Any, Dict, Iterable, Optional

from .message_board import _MESSAGE_KINDS, _require_id
from .party_coordination import PartyCoordinationRuntime, _names

PARTY_CHANNEL_VERSION = "PARTY.COORDINATION.CHANNEL.2"
PARTY_MESSAGE_ARTIFACT = "ATHENA.PARTY.MESSAGE.V2"


class PartyCoordinationRuntimeV2(PartyCoordinationRuntime):
    """Party Coordination V2 channel gate over canonical Message Board V1.

    Message Board remains the only message transport. This layer merely emits a
    structured party envelope and, for reward scoring, ignores ambient board
    traffic that is not explicitly scoped to the party. After an awarded
    observation, the communication reward window resets so old acknowledged
    messages cannot be recycled into a new coordination bonus.
    """

    @staticmethod
    def _decode_party_message(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("kind") != "MESSAGE":
            return None
        raw = (event.get("payload") or {}).get("message")
        if not isinstance(raw, str):
            return None
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(packet, dict) or packet.get("artifact") != PARTY_MESSAGE_ARTIFACT:
            return None
        return packet

    @staticmethod
    def _reward_window_start(party: Dict[str, Any]) -> Optional[str]:
        awarded = [
            str(row.get("observed_at") or "")
            for row in (party.get("observations") or [])
            if row.get("status") == "AWARDED" and row.get("observed_at")
        ]
        return max(awarded) if awarded else None

    def message(
        self,
        party_id: str,
        sender: str,
        recipients: Iterable[str],
        goal_refs: Iterable[str],
        message: str,
        message_kind: str = "INFO",
        reply_to: Optional[str] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        party_id = _require_id(party_id, "party_id")
        sender = _require_id(sender, "sender")
        recipient_rows = [_require_id(str(value), "recipient") for value in (recipients or [])]
        recipient_rows = sorted(set(recipient_rows))
        if not recipient_rows:
            raise ValueError("PARTY_MESSAGE_RECIPIENT_REQUIRED")
        if sender in recipient_rows:
            raise ValueError("PARTY_MESSAGE_SELF_ROUTE_HOLD")
        goals = _names(goal_refs)
        if not goals:
            raise ValueError("PARTY_MESSAGE_GOAL_REF_REQUIRED")
        text = str(message or "").strip()
        if not text:
            raise ValueError("party message must be non-empty")
        kind = str(message_kind or "INFO").upper()
        if kind not in _MESSAGE_KINDS:
            raise ValueError(f"message_kind must be one of {sorted(_MESSAGE_KINDS)}")

        board = self._board()
        snapshot = board.read(
            agent_id=sender,
            limit=500,
            include_stale=False,
            remote=remote,
            shared_remote_mode="REQUIRED",
        )
        if snapshot.get("status") != "OK" or not snapshot.get("shared_frontier_verified"):
            return {
                "status": "PARTY_SHARED_FRONTIER_HOLD",
                "party_id": party_id,
                "durable_return": False,
                "board": snapshot,
            }
        party = self._read_party(board, party_id)
        if not party:
            return {"status": "PARTY_NOT_FOUND_HOLD", "party_id": party_id, "durable_return": True}
        members = self._members(party)
        if sender not in members:
            raise ValueError(f"PARTY_MESSAGE_SENDER_NOT_MEMBER:{sender}")
        unknown_recipients = sorted(set(recipient_rows) - set(members))
        if unknown_recipients:
            raise ValueError("PARTY_MESSAGE_RECIPIENT_NOT_MEMBER:" + ",".join(unknown_recipients))
        goal_ids = self._goal_ids(party)
        unknown_goals = sorted(set(goals) - goal_ids)
        if unknown_goals:
            raise ValueError("PARTY_MESSAGE_UNKNOWN_GOAL:" + ",".join(unknown_goals))
        active = {str(row.get("agent_id")) for row in (snapshot.get("active") or [])}
        if sender not in active:
            return {
                "status": "PARTY_MESSAGE_SENDER_NOT_ACTIVE_HOLD",
                "party_id": party_id,
                "sender": sender,
                "durable_return": True,
            }
        inactive = sorted(set(recipient_rows) - active)
        if inactive:
            return {
                "status": "PARTY_MESSAGE_RECIPIENT_NOT_ACTIVE_HOLD",
                "party_id": party_id,
                "inactive_recipients": inactive,
                "durable_return": True,
            }

        packet = {
            "artifact": PARTY_MESSAGE_ARTIFACT,
            "version": PARTY_CHANNEL_VERSION,
            "party_id": party_id,
            "channel": f"party:{party_id}",
            "sender": sender,
            "recipients": recipient_rows,
            "goal_refs": goals,
            "message_kind": kind,
            "message": text,
            "law": "PARTY_MESSAGE_ROUTE != CONSUMPTION != OUTCOME_PROOF != XP_AUTHORITY",
        }
        result = board.post(
            agent_id=sender,
            message=json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            message_kind=kind,
            recipients=recipient_rows,
            reply_to=reply_to,
            remote=remote,
        )
        result["party_channel_version"] = PARTY_CHANNEL_VERSION
        result["party_id"] = party_id
        result["party_channel"] = f"party:{party_id}"
        result["party_goal_refs"] = goals
        result["xp_bonus"] = 0
        result["execution_authority"] = False
        result["xp_authority"] = False
        return result

    def _communication(self, board, party: Dict[str, Any]) -> Dict[str, Any]:
        party_id = str(party.get("party_id") or "")
        members = set(self._members(party))
        goal_ids = self._goal_ids(party)
        events = board._events()
        cutoff = self._reward_window_start(party)

        all_party_messages: Dict[str, Dict[str, Any]] = {}
        eligible_messages: Dict[str, Dict[str, Any]] = {}
        packets: Dict[str, Dict[str, Any]] = {}
        for event in events:
            sender = str(event.get("agent_id") or "")
            if sender not in members:
                continue
            packet = self._decode_party_message(event)
            if not packet or str(packet.get("party_id") or "") != party_id:
                continue
            recipients = {str(value) for value in (event.get("recipients") or [])}
            packet_recipients = {str(value) for value in (packet.get("recipients") or [])}
            packet_goals = {str(value) for value in (packet.get("goal_refs") or [])}
            if (
                not recipients
                or recipients != packet_recipients
                or not recipients.issubset(members)
                or not packet_goals
                or not packet_goals.issubset(goal_ids)
            ):
                continue
            message_id = str(event.get("event_id") or "")
            if not message_id:
                continue
            all_party_messages[message_id] = event
            packets[message_id] = packet
            if cutoff is None or str(event.get("created_at") or "") > cutoff:
                eligible_messages[message_id] = event

        acknowledgements: Dict[str, list[str]] = {}
        for event in events:
            if event.get("kind") != "ACK":
                continue
            acknowledger = str(event.get("agent_id") or "")
            if acknowledger not in members:
                continue
            message_id = str((event.get("payload") or {}).get("message_id") or "")
            message = eligible_messages.get(message_id)
            if not message:
                continue
            recipients = {str(value) for value in (message.get("recipients") or [])}
            if acknowledger in recipients:
                acknowledgements.setdefault(message_id, []).append(acknowledger)

        edges = []
        participants = set()
        acknowledged_goals = set()
        for message_id, ackers in sorted(acknowledgements.items()):
            sender = str(eligible_messages[message_id].get("agent_id") or "")
            goals = {str(value) for value in (packets[message_id].get("goal_refs") or [])}
            for receiver in sorted(set(ackers)):
                edges.append(
                    {
                        "message_id": message_id,
                        "sender": sender,
                        "acknowledger": receiver,
                        "goal_refs": sorted(goals),
                    }
                )
                participants.update((sender, receiver))
                acknowledged_goals.update(goals)

        raw_participant_count = len(participants)
        multi_goal_channel = len(acknowledged_goals) >= 2
        reward_ready = raw_participant_count >= 2 and multi_goal_channel
        goal_coverage = len(acknowledged_goals & goal_ids) / len(goal_ids) if goal_ids else 0.0
        return {
            "channel_version": PARTY_CHANNEL_VERSION,
            "party_channel": f"party:{party_id}",
            "reward_window_start": cutoff,
            "party_scoped_message_count_total": len(all_party_messages),
            "message_count": len(eligible_messages),
            "acknowledged_message_count": len(acknowledgements),
            "acknowledged_edges": edges,
            "participants": sorted(participants),
            "raw_participant_count": raw_participant_count,
            "participant_count": raw_participant_count if reward_ready else 0,
            "acknowledged_goal_refs": sorted(acknowledged_goals),
            "acknowledged_goal_count": len(acknowledged_goals),
            "goal_coverage": round(goal_coverage, 9),
            "multi_goal_channel": multi_goal_channel,
            "reward_ready": reward_ready,
            "law": (
                "ONLY PARTY-TAGGED ACKNOWLEDGED MESSAGE-BOARD EVENTS IN THE CURRENT REWARD WINDOW COUNT; "
                "MESSAGE_ROUTE != CONSUMPTION; ACKNOWLEDGED_COMMUNICATION != OUTCOME_PROOF"
            ),
        }

    def _score(
        self,
        party: Dict[str, Any],
        communication: Dict[str, Any],
        result_goal_ids: Optional[Iterable[str]] = None,
        shared_frontier_verified: bool = False,
    ) -> Dict[str, Any]:
        score = super()._score(party, communication, result_goal_ids, shared_frontier_verified)
        members = self._members(party)
        raw_participants = float(communication.get("raw_participant_count") or 0)
        participant_fraction = min(1.0, raw_participants / max(1.0, float(len(members))))
        communication_goal_coverage = float(communication.get("goal_coverage") or 0.0)

        # Q-SEAR is the multi-objective steering layer: retain the canonical
        # assignment/capability/load score and explicitly add communication-to-goal coverage.
        qsear = max(0.0, min(1.0, 0.85 * float(score["qsear"]) + 0.15 * communication_goal_coverage))

        # Q-ARSI recursive refinement now requires both member participation and
        # goal-linked channel coverage, so generic ambient chat cannot raise the phase.
        phases = dict(score["qarsi_phases"])
        phases["recursive"] = math.sqrt(max(0.0, participant_fraction * communication_goal_coverage))
        qarsi = sum(float(phases[key]) for key in score["qarsi_phase_order"]) / len(score["qarsi_phase_order"])
        qlearn = float(score["qlearn"])
        synergy = (qlearn * qsear * qarsi) ** (1.0 / 3.0) if qlearn > 0 and qsear > 0 and qarsi > 0 else 0.0

        score.update(
            {
                "big3_version": "PARTY.BIG3.BOARD.CHANNEL.2",
                "qsear": round(qsear, 9),
                "qarsi": round(qarsi, 9),
                "qarsi_phases": {key: round(float(value), 9) for key, value in phases.items()},
                "synergy": round(synergy, 9),
            }
        )
        diagnostics = dict(score.get("diagnostics") or {})
        diagnostics.update(
            {
                "party_channel_version": PARTY_CHANNEL_VERSION,
                "party_scoped_communication": True,
                "communication_goal_coverage": round(communication_goal_coverage, 9),
                "communication_reward_ready": bool(communication.get("reward_ready")),
                "reward_window_start": communication.get("reward_window_start"),
            }
        )
        score["diagnostics"] = diagnostics
        score["big3_loop_law"] = (
            "Q-LEARN retains/refines observed coordination patterns -> Q-SEAR steers multi-goal synergy/concurrency -> "
            "Q-ARSI refines symphony/recursive/ultra_fine/hyper_fine -> observed deltas return to Q-LEARN"
        )
        return score

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        value["version"] = PARTY_CHANNEL_VERSION
        value["channel"] = {
            "tool": "athena_party_message",
            "artifact": PARTY_MESSAGE_ARTIFACT,
            "transport": "ATHENA Message Board V1",
            "scope": "party_id + explicit goal_refs + party-member recipients",
            "consumption": "Message Board ACK",
            "reward_window": "resets after each AWARDED observation",
            "minimum_goal_refs_for_reward_window": 2,
        }
        value["big3"]["version"] = "PARTY.BIG3.BOARD.CHANNEL.2"
        value["big3"]["reiterative_loop"] = ["Q-LEARN", "Q-SEAR", "Q-ARSI", "Q-LEARN"]
        value["xp"]["communication_reuse"] = False
        value["xp"]["ambient_board_chat_eligible"] = False
        value["laws"] = list(value.get("laws") or []) + [
            "party bonus communication must be party-tagged, acknowledged, goal-linked, and fresh since the previous award",
            "ambient or historical Message Board chat cannot unlock party XP",
        ]
        return value

    def benchmark(self) -> Dict[str, Any]:
        value = dict(super().benchmark())
        value["party_channel_version"] = PARTY_CHANNEL_VERSION
        value["party_message_artifact"] = PARTY_MESSAGE_ARTIFACT
        return value
