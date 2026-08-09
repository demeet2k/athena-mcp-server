from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .message_board import _iso, _json_text, _require_id
from .party_coordination import PARTY_ARTIFACT, PARTY_ROOT, _digest, _names
from .party_coordination_v2 import PartyCoordinationRuntimeV2

PARTY_REWARD_VERSION = "PARTY.REWARD.PROVENANCE.3"
PARTY_RESULT_ARTIFACT = "ATHENA.PARTY.RESULT.V3"
PARTY_RESULT_KINDS = frozenset({"RESULT", "VERIFY"})
_RESULT_MESSAGE_KIND = {"RESULT": "DISCOVERY", "VERIFY": "ANSWER"}


class PartyCoordinationRuntimeV3(PartyCoordinationRuntimeV2):
    """Reward-provenance hardening over Party Channel V2.

    V2 decides which communication can count. V3 decides which current work and
    upstream XP source can be credited. Result events remain Message Board V1
    messages; this layer does not create another transport or truth authority.
    """

    @staticmethod
    def _root_work_id(member: Dict[str, Any]) -> str:
        work_key = str(member.get("work_key") or "").strip()
        if work_key:
            return "WORK:" + work_key
        join_of = str(member.get("join_of") or "").strip()
        mode = str(member.get("claim_mode") or "").upper()
        if mode == "COLLABORATOR" and join_of:
            return "CLAIM:" + join_of
        return "CLAIM:" + str(member.get("claim_id") or "")

    @staticmethod
    def _decode_result_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("kind") != "MESSAGE":
            return None
        raw = (event.get("payload") or {}).get("message")
        if not isinstance(raw, str):
            return None
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(packet, dict) or packet.get("artifact") != PARTY_RESULT_ARTIFACT:
            return None
        return packet

    @staticmethod
    def _event_acknowledgers(events: Iterable[Dict[str, Any]], message_id: str) -> set[str]:
        return {
            str(event.get("agent_id") or "")
            for event in events
            if event.get("kind") == "ACK"
            and str((event.get("payload") or {}).get("message_id") or "") == message_id
        }

    def _source_xp_award(self, board, source_xp_ref: str) -> Optional[Dict[str, Any]]:
        """Find the first awarded use of one upstream XP identity across parties."""
        root: Path = board._root() / PARTY_ROOT
        if not root.exists():
            return None
        for path in sorted(root.glob("*.json")):
            party = board._read_json(path)
            if not party or party.get("artifact") != PARTY_ARTIFACT:
                continue
            for observation in party.get("observations") or []:
                if (
                    observation.get("status") == "AWARDED"
                    and str(observation.get("source_xp_ref") or "") == source_xp_ref
                ):
                    return {
                        "party_id": party.get("party_id"),
                        "observation_id": observation.get("observation_id"),
                        "receipt_digest": observation.get("receipt_digest"),
                    }
        return None

    def result(
        self,
        party_id: str,
        sender: str,
        recipients: Iterable[str],
        goal_id: str,
        result_ref: str,
        witness_ref: str,
        evidence_kind: str = "RESULT",
        remote: str = "origin",
    ) -> Dict[str, Any]:
        """Post one provenance-bearing party result through Message Board V1.

        This proves an attributable shared event was routed; it does not prove the
        result content is true and it never earns XP by itself.
        """
        party_id = _require_id(party_id, "party_id")
        sender = _require_id(sender, "sender")
        recipients = sorted({_require_id(str(value), "recipient") for value in (recipients or [])})
        goal_id = str(goal_id or "").strip()
        result_ref = str(result_ref or "").strip()
        witness_ref = str(witness_ref or "").strip()
        kind = str(evidence_kind or "RESULT").upper()
        if not recipients:
            raise ValueError("PARTY_RESULT_RECIPIENT_REQUIRED")
        if sender in recipients:
            raise ValueError("PARTY_RESULT_SELF_ROUTE_HOLD")
        if not goal_id or not result_ref or not witness_ref:
            raise ValueError("party result requires goal_id, result_ref, and witness_ref")
        if kind not in PARTY_RESULT_KINDS:
            raise ValueError(f"evidence_kind must be one of {sorted(PARTY_RESULT_KINDS)}")

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
                "status": "PARTY_RESULT_SHARED_FRONTIER_HOLD",
                "party_id": party_id,
                "durable_return": False,
                "xp_bonus": 0,
                "board": snapshot,
            }
        party = self._read_party(board, party_id)
        if not party:
            return {"status": "PARTY_NOT_FOUND_HOLD", "party_id": party_id, "durable_return": True, "xp_bonus": 0}
        members = self._members(party)
        member = members.get(sender)
        if not member:
            raise ValueError(f"PARTY_RESULT_SENDER_NOT_MEMBER:{sender}")
        if goal_id not in set(member.get("goal_refs") or []):
            raise ValueError(f"PARTY_RESULT_GOAL_NOT_ASSIGNED:{sender}:{goal_id}")
        unknown_recipients = sorted(set(recipients) - set(members))
        if unknown_recipients:
            raise ValueError("PARTY_RESULT_RECIPIENT_NOT_MEMBER:" + ",".join(unknown_recipients))

        active = {
            str(row.get("agent_id") or ""): row
            for row in (snapshot.get("active") or [])
        }
        presence = active.get(sender)
        if not presence:
            return {
                "status": "PARTY_RESULT_SENDER_NOT_ACTIVE_HOLD",
                "party_id": party_id,
                "sender": sender,
                "durable_return": True,
                "xp_bonus": 0,
            }
        if str(presence.get("claim_id") or "") != str(member.get("claim_id") or ""):
            return {
                "status": "PARTY_RESULT_STALE_CLAIM_HOLD",
                "party_id": party_id,
                "sender": sender,
                "frozen_claim_id": member.get("claim_id"),
                "current_claim_id": presence.get("claim_id"),
                "durable_return": True,
                "xp_bonus": 0,
            }
        inactive = sorted(set(recipients) - set(active))
        if inactive:
            return {
                "status": "PARTY_RESULT_RECIPIENT_NOT_ACTIVE_HOLD",
                "party_id": party_id,
                "inactive_recipients": inactive,
                "durable_return": True,
                "xp_bonus": 0,
            }

        packet = {
            "artifact": PARTY_RESULT_ARTIFACT,
            "version": PARTY_REWARD_VERSION,
            "party_id": party_id,
            "goal_id": goal_id,
            "agent_id": sender,
            "claim_id": member.get("claim_id"),
            "root_work_id": self._root_work_id(member),
            "evidence_kind": kind,
            "result_ref": result_ref,
            "witness_ref": witness_ref,
            "recipients": recipients,
            "law": "RESULT_EVENT_ROUTE != RESULT_TRUTH; PARTY_RESULT_EVENT != XP_AUTHORITY",
        }
        value = board.post(
            agent_id=sender,
            message=json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            message_kind=_RESULT_MESSAGE_KIND[kind],
            recipients=recipients,
            remote=remote,
        )
        value.update(
            {
                "party_reward_version": PARTY_REWARD_VERSION,
                "party_id": party_id,
                "goal_id": goal_id,
                "evidence_kind": kind,
                "result_ref": result_ref,
                "witness_ref": witness_ref,
                "xp_bonus": 0,
                "execution_authority": False,
                "xp_authority": False,
                "epistemic_boundary": "shared attributable result provenance is not independent verification of result truth",
            }
        )
        return value

    def _validate_result_provenance(
        self,
        *,
        events: list[Dict[str, Any]],
        event_map: Dict[str, Dict[str, Any]],
        party: Dict[str, Any],
        member: Dict[str, Any],
        current_presence: Dict[str, Any],
        result: Dict[str, Any],
        reward_window_start: Optional[str],
    ) -> tuple[Optional[Dict[str, Any]], list[str]]:
        reasons: list[str] = []
        event_ref = str(result.get("result_event_ref") or "").strip()
        agent_id = str(result.get("agent_id") or "")
        goal_id = str(result.get("goal_id") or "")
        witness_ref = str(result.get("witness_ref") or "")
        if not event_ref:
            return None, [f"RESULT_EVENT_REF_REQUIRED:{agent_id}:{goal_id}"]
        event = event_map.get(event_ref)
        if not event:
            return None, [f"RESULT_EVENT_NOT_FOUND:{event_ref}"]
        packet = self._decode_result_event(event)
        if not packet:
            return None, [f"RESULT_EVENT_CONTRACT_MISMATCH:{event_ref}"]

        members = self._members(party)
        recipients = {str(value) for value in (event.get("recipients") or [])}
        packet_recipients = {str(value) for value in (packet.get("recipients") or [])}
        if str(event.get("agent_id") or "") != agent_id:
            reasons.append(f"RESULT_EVENT_AUTHOR_MISMATCH:{event_ref}")
        if str(packet.get("agent_id") or "") != agent_id:
            reasons.append(f"RESULT_PACKET_AGENT_MISMATCH:{event_ref}")
        if str(packet.get("party_id") or "") != str(party.get("party_id") or ""):
            reasons.append(f"RESULT_EVENT_PARTY_MISMATCH:{event_ref}")
        if str(packet.get("goal_id") or "") != goal_id:
            reasons.append(f"RESULT_EVENT_GOAL_MISMATCH:{event_ref}")
        if str(packet.get("witness_ref") or "") != witness_ref:
            reasons.append(f"RESULT_EVENT_WITNESS_MISMATCH:{event_ref}")
        if not str(packet.get("result_ref") or "").strip():
            reasons.append(f"RESULT_REF_MISSING:{event_ref}")
        frozen_claim = str(member.get("claim_id") or "")
        current_claim = str(current_presence.get("claim_id") or "")
        if str((event.get("payload") or {}).get("claim_id") or "") != frozen_claim:
            reasons.append(f"RESULT_EVENT_CLAIM_MISMATCH:{event_ref}")
        if str(packet.get("claim_id") or "") != frozen_claim:
            reasons.append(f"RESULT_PACKET_CLAIM_MISMATCH:{event_ref}")
        if current_claim != frozen_claim:
            reasons.append(f"RESULT_AGENT_STALE_CLAIM_HOLD:{agent_id}")
        if str(packet.get("root_work_id") or "") != self._root_work_id(member):
            reasons.append(f"RESULT_ROOT_WORK_MISMATCH:{event_ref}")
        if not recipients or recipients != packet_recipients or not recipients.issubset(set(members)):
            reasons.append(f"RESULT_EVENT_RECIPIENT_SCOPE_MISMATCH:{event_ref}")
        if agent_id in recipients:
            reasons.append(f"RESULT_EVENT_SELF_ROUTE:{event_ref}")
        if reward_window_start and str(event.get("created_at") or "") <= reward_window_start:
            reasons.append(f"RESULT_EVENT_OUTSIDE_REWARD_WINDOW:{event_ref}")
        if str(event.get("created_at") or "") < str(member.get("joined_at") or ""):
            reasons.append(f"RESULT_EVENT_PREDATES_MEMBERSHIP:{event_ref}")
        evidence_kind = str(packet.get("evidence_kind") or "")
        if evidence_kind not in PARTY_RESULT_KINDS:
            reasons.append(f"RESULT_EVENT_KIND_INVALID:{event_ref}")

        ackers = self._event_acknowledgers(events, event_ref) & recipients & set(members)
        if not ackers:
            reasons.append(f"RESULT_EVENT_UNACKNOWLEDGED:{event_ref}")
        if reasons:
            return None, reasons
        return {
            "result_event_ref": event_ref,
            "evidence_kind": evidence_kind,
            "result_ref": packet.get("result_ref"),
            "witness_ref": witness_ref,
            "agent_id": agent_id,
            "goal_id": goal_id,
            "claim_id": frozen_claim,
            "root_work_id": self._root_work_id(member),
            "acknowledged_by": sorted(ackers),
            "event_created_at": event.get("created_at"),
            "provenance_validated": True,
            "truth_verified": False,
        }, []

    def observe(
        self,
        observation_id: str,
        party_id: str,
        observer: str,
        base_xp: float,
        results: Iterable[Dict[str, Any]],
        witness_ref: str,
        source_xp_ref: Optional[str] = None,
        source_xp_witness_ref: Optional[str] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        observation_id = _require_id(observation_id, "observation_id")
        party_id = _require_id(party_id, "party_id")
        observer = _require_id(observer, "observer")
        witness_ref = str(witness_ref or "").strip()
        source_xp_ref = str(source_xp_ref or "").strip()
        source_xp_witness_ref = str(source_xp_witness_ref or "").strip()
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
            result_event_ref = str(raw.get("result_event_ref") or "").strip()
            if not goal_id or not result_witness:
                raise ValueError("every result requires goal_id and witness_ref")
            if goal_id in seen_goals:
                raise ValueError(f"duplicate result goal_id: {goal_id}")
            seen_goals.add(goal_id)
            result_rows.append(
                {
                    "goal_id": goal_id,
                    "agent_id": agent_id,
                    "witness_ref": result_witness,
                    "result_event_ref": result_event_ref or None,
                }
            )
        result_rows.sort(key=lambda row: row["goal_id"])
        if len(result_rows) < 2:
            raise ValueError("PARTY_MULTI_GOAL_OBSERVATION_REQUIRED: at least two distinct goal results")

        request = {
            "observation_id": observation_id,
            "party_id": party_id,
            "observer": observer,
            "base_xp": base_xp,
            "source_xp_ref": source_xp_ref or None,
            "source_xp_witness_ref": source_xp_witness_ref or None,
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
                    replay = dict(stored)
                    replay["idempotent"] = True
                    replay["durable_return"] = True
                    return {"return": replay}

            members = self._members(party)
            goal_ids = self._goal_ids(party)
            active = {str(row.get("agent_id") or ""): row for row in board._active()}
            events = board._events()
            event_map = {str(event.get("event_id") or ""): event for event in events if event.get("event_id")}
            reward_window_start = self._reward_window_start(party)
            reasons: list[str] = []
            result_agents: set[str] = set()
            root_work_ids: set[str] = set()
            provenance_rows: list[Dict[str, Any]] = []

            if len(members) < 2:
                reasons.append("NEED_TWO_MEMBERS")
            if not source_xp_ref:
                reasons.append("SOURCE_XP_REF_REQUIRED")
            if not source_xp_witness_ref:
                reasons.append("SOURCE_XP_WITNESS_REQUIRED")
            if source_xp_ref:
                prior_source = self._source_xp_award(board, source_xp_ref)
                if prior_source:
                    reasons.append("SOURCE_XP_ALREADY_PARTY_CREDITED_HOLD")

            for result_row in result_rows:
                goal_id = str(result_row["goal_id"])
                agent_id = str(result_row["agent_id"])
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
                presence = active.get(agent_id)
                if not presence:
                    reasons.append(f"RESULT_AGENT_NOT_ACTIVE_HOLD:{agent_id}")
                    continue
                if str(presence.get("claim_id") or "") != str(member.get("claim_id") or ""):
                    reasons.append(f"RESULT_AGENT_STALE_CLAIM_HOLD:{agent_id}")
                    continue
                result_agents.add(agent_id)
                root_work_ids.add(self._root_work_id(member))
                provenance, provenance_reasons = self._validate_result_provenance(
                    events=events,
                    event_map=event_map,
                    party=party,
                    member=member,
                    current_presence=presence,
                    result=result_row,
                    reward_window_start=reward_window_start,
                )
                reasons.extend(provenance_reasons)
                if provenance:
                    provenance_rows.append(provenance)

            if len(result_agents) < 2:
                reasons.append("NEED_TWO_RESULT_AGENTS")
            if len(root_work_ids) < 2:
                reasons.append("DUPLICATE_ONLY_PARTY_HOLD")
            if len(provenance_rows) != len(result_rows):
                reasons.append("RESULT_PROVENANCE_INCOMPLETE_HOLD")

            communication = self._communication(board, party)
            if communication.get("participant_count", 0) < 2:
                reasons.append("NEED_ACKNOWLEDGED_PARTY_COMMUNICATION")
            prior_witness = next(
                (
                    stored
                    for stored in observations
                    if stored.get("status") == "AWARDED"
                    and stored.get("witness_ref") == witness_ref
                ),
                None,
            )
            if prior_witness:
                reasons.append("WITNESS_ALREADY_REWARDED")

            score = self._score(party, communication, seen_goals, True)
            if score["synergy"] < 0.35:
                reasons.append("LOW_SYNERGY")
            if base_xp == 0:
                reasons.append("BASE_XP_ZERO")

            unique_reasons = sorted(set(reasons))
            if unique_reasons:
                status, bonus_rate, bonus_xp = "HOLD", 0.0, 0.0
            else:
                status = "AWARDED"
                bonus_rate = min(0.05, 0.01 + 0.04 * float(score["synergy"]))
                bonus_xp = round(base_xp * bonus_rate, 6)

            observation = {
                "version": PARTY_REWARD_VERSION,
                "observation_id": observation_id,
                "party_id": party_id,
                "observer": observer,
                "base_xp": base_xp,
                "source_xp_ref": source_xp_ref or None,
                "source_xp_witness_ref": source_xp_witness_ref or None,
                "source_xp_binding_digest": _digest(
                    {
                        "source_xp_ref": source_xp_ref or None,
                        "source_xp_witness_ref": source_xp_witness_ref or None,
                        "base_xp": base_xp,
                    }
                ),
                "results": result_rows,
                "result_provenance": provenance_rows,
                "result_provenance_complete": len(provenance_rows) == len(result_rows),
                "result_truth_verified": False,
                "witness_ref": witness_ref,
                "status": status,
                "hold_reasons": unique_reasons,
                "communication": communication,
                "score": score,
                "root_work_ids": sorted(root_work_ids),
                "root_work_diversity": len(root_work_ids),
                "coordination_bonus_rate": round(bonus_rate, 9),
                "coordination_bonus_xp": bonus_xp,
                "xp_patch": {
                    "base_xp_observed": base_xp,
                    "source_xp_ref": source_xp_ref or None,
                    "coordination_bonus_xp": bonus_xp,
                    "apply_to_global_xp": False,
                },
                "request_digest": request_digest,
                "observed_at": _iso(),
                "observed_git_head": base,
                "idempotent": False,
                "execution_authority": False,
                "xp_authority": False,
                "source_xp_external_verification": False,
                "independent_result_verification": False,
                "reward_law": (
                    "bonus requires fresh scoped communication, current frozen claims, ACKed result-provenance events, "
                    "at least two root work identities, and a globally unused source_xp_ref; bonus <= 5%"
                ),
                "epistemic_boundary": (
                    "result/source witness refs and ACKed shared events establish provenance, not independent truth; "
                    "Party records only an incremental bonus candidate and never creates or rewrites upstream XP"
                ),
            }
            observation["receipt_digest"] = _digest(
                {key: value for key, value in observation.items() if key != "idempotent"}
            )
            updated = dict(party)
            updated["observations"] = observations + [observation]
            updated["updated_at"] = _iso()
            updated["revision"] = int(updated.get("revision") or 0) + 1
            event_rel, event = board._event(
                "PARTY_OBSERVE",
                observer,
                {
                    "party_id": party_id,
                    "observation_id": observation_id,
                    "status": status,
                    "bonus_xp": bonus_xp,
                    "source_xp_ref": source_xp_ref or None,
                    "witness_ref": witness_ref,
                },
            )
            return {
                "files": {
                    self._party_rel(party_id): _json_text(updated),
                    event_rel: _json_text(event),
                },
                "message": f"party reward provenance observe {party_id} {observation_id}",
                "result": observation,
            }

        return board._mutate(agent_id=observer, remote=remote, build_files=build)

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        value["version"] = PARTY_REWARD_VERSION
        tools = list(value.get("tools") or [])
        for tool in ("athena_party_message", "athena_party_result"):
            if tool not in tools:
                tools.append(tool)
        value["tools"] = tools
        value["reward_provenance"] = {
            "result_artifact": PARTY_RESULT_ARTIFACT,
            "result_transport": "ATHENA Message Board V1",
            "result_consumption": "Message Board ACK by addressed party member",
            "current_claim_required": True,
            "source_xp_ref_required_for_award": True,
            "source_xp_global_reuse": False,
            "root_work_diversity_required": 2,
            "truth_authority": False,
        }
        value["xp"]["double_count_guard"] = "global awarded source_xp_ref + party observation idempotency"
        value["xp"]["source_xp_external_verification"] = False
        value["laws"] = list(value.get("laws") or []) + [
            "party member at join time is not current work proof; credited result agents must still hold the frozen Message Board claim",
            "result witness text is insufficient; award provenance requires an ACKed typed shared result event",
            "claim-id diversity is not root-work diversity; duplicate-only work roots cannot unlock a party bonus",
            "source_xp_ref identifies imported upstream XP and may receive at most one awarded Party bonus across parties",
            "result events and source XP witness refs establish provenance only, not independent truth or global XP authority",
        ]
        return value

    def benchmark(self) -> Dict[str, Any]:
        value = dict(super().benchmark())
        value["party_reward_version"] = PARTY_REWARD_VERSION
        value["party_result_artifact"] = PARTY_RESULT_ARTIFACT
        return value
