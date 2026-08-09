from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .party_coordination_v3 import (
    PARTY_RESULT_ARTIFACT,
    PARTY_RESULT_KINDS,
    PARTY_REWARD_VERSION,
    PartyCoordinationRuntimeV3,
    _RESULT_MESSAGE_KIND,
)

PARTY_REWARD_ENVELOPE_VERSION = "PARTY.REWARD.PROVENANCE.3.1"


class PartyCoordinationRuntimeV31(PartyCoordinationRuntimeV3):
    """Exact envelope-coherence hardening over Reward Provenance V3.

    V3 establishes attribution/current-work/source-XP provenance. V3.1 adds no
    new reward channel or authority. It merely requires the shared Message Board
    envelope to agree with the inner result packet on the exact protocol version
    and RESULT/VERIFY semantic role before V3 provenance validation can proceed.
    """

    @staticmethod
    def _raw_result_packet(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
    def _decode_result_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        packet = PartyCoordinationRuntimeV31._raw_result_packet(event)
        if not packet:
            return None
        if str(packet.get("version") or "") != PARTY_REWARD_VERSION:
            return None
        evidence_kind = str(packet.get("evidence_kind") or "")
        if evidence_kind not in PARTY_RESULT_KINDS:
            return None
        outer_kind = str((event.get("payload") or {}).get("message_kind") or "")
        if outer_kind != _RESULT_MESSAGE_KIND[evidence_kind]:
            return None
        return packet

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
    ):
        event_ref = str(result.get("result_event_ref") or "").strip()
        if not event_ref:
            return super()._validate_result_provenance(
                events=events,
                event_map=event_map,
                party=party,
                member=member,
                current_presence=current_presence,
                result=result,
                reward_window_start=reward_window_start,
            )
        event = event_map.get(event_ref)
        if not event:
            return super()._validate_result_provenance(
                events=events,
                event_map=event_map,
                party=party,
                member=member,
                current_presence=current_presence,
                result=result,
                reward_window_start=reward_window_start,
            )

        packet = self._raw_result_packet(event)
        if not packet:
            return None, [f"RESULT_EVENT_CONTRACT_MISMATCH:{event_ref}"]

        packet_version = str(packet.get("version") or "")
        if packet_version != PARTY_REWARD_VERSION:
            return None, [
                f"RESULT_EVENT_VERSION_MISMATCH:{event_ref}:{packet_version or 'MISSING'}"
            ]

        evidence_kind = str(packet.get("evidence_kind") or "")
        if evidence_kind not in PARTY_RESULT_KINDS:
            return None, [f"RESULT_EVENT_KIND_INVALID:{event_ref}:{evidence_kind or 'MISSING'}"]

        outer_kind = str((event.get("payload") or {}).get("message_kind") or "")
        expected_outer = _RESULT_MESSAGE_KIND[evidence_kind]
        if outer_kind != expected_outer:
            return None, [
                f"RESULT_EVENT_ROLE_MISMATCH:{event_ref}:{evidence_kind}:{outer_kind or 'MISSING'}:{expected_outer}"
            ]

        return super()._validate_result_provenance(
            events=events,
            event_map=event_map,
            party=party,
            member=member,
            current_presence=current_presence,
            result=result,
            reward_window_start=reward_window_start,
        )

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        reward = dict(value.get("reward_provenance") or {})
        reward.update(
            {
                "envelope_hardening_version": PARTY_REWARD_ENVELOPE_VERSION,
                "result_packet_exact_version_required": PARTY_REWARD_VERSION,
                "outer_role_binding": {
                    "RESULT": "DISCOVERY",
                    "VERIFY": "ANSWER",
                },
                "role_or_version_coherence_is_truth_authority": False,
            }
        )
        value["reward_provenance"] = reward
        value["laws"] = list(value.get("laws") or []) + [
            "result artifact identity is insufficient: result packet version must exactly match the V3 protocol",
            "inner RESULT/VERIFY role must exactly agree with the outer Message Board message_kind",
            "version/role coherence establishes envelope provenance only, not result truth or independent verification",
        ]
        return value

    def benchmark(self) -> Dict[str, Any]:
        value = dict(super().benchmark())
        value["party_reward_envelope_hardening_version"] = PARTY_REWARD_ENVELOPE_VERSION
        return value


__all__ = ["PARTY_REWARD_ENVELOPE_VERSION", "PartyCoordinationRuntimeV31"]
