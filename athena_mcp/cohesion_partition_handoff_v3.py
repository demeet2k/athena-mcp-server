from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from .cohesion_partition_handoff import CohesionPartitionHandoffRuntime
from .party_coordination_v3 import PartyCoordinationRuntimeV3

RING2_V3_VERSION = "COHESION.PARTITION.HANDOFF.V3BRIDGE.1"


class CohesionPartitionHandoffRuntimeV3(CohesionPartitionHandoffRuntime):
    """Current-frontier Ring-II bridge.

    The underlying Ring-II mechanics remain authority-neutral. This wrapper binds
    party-context validation to Party Reward Provenance V3 and projects successful
    shared-sink partitions into the C3 duplicate-guard proof dialect. The adapter
    is structural only and never asserts independent verification.
    """

    def _validate_party_context(
        self,
        board,
        party_id: Optional[str],
        actors: Iterable[str],
        goal_refs: Optional[Iterable[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not party_id:
            return None
        from .message_board import _require_id
        from .party_coordination import _names

        party_id = _require_id(str(party_id), "party_id")
        runtime = PartyCoordinationRuntimeV3(self.server)
        party = runtime._read_party(board, party_id)
        if not party:
            raise ValueError(f"COHESION_PARTY_NOT_FOUND:{party_id}")
        members = runtime._members(party)
        missing = sorted(set(actors) - set(members))
        if missing:
            raise ValueError("COHESION_PARTY_ACTOR_NOT_MEMBER:" + ",".join(missing))
        goals = _names(goal_refs)
        if goals:
            unknown = sorted(set(goals) - runtime._goal_ids(party))
            if unknown:
                raise ValueError("COHESION_PARTY_UNKNOWN_GOAL:" + ",".join(unknown))
        return party

    @staticmethod
    def _c3_adapters(partition: Dict[str, Any]) -> list[Dict[str, Any]]:
        packets = {
            str(row.get("packet_id")): row
            for row in (partition.get("packets") or [])
            if row.get("packet_id")
        }
        proof = partition.get("proof") or {}
        adapters = []
        for edge in proof.get("serialization_edges") or []:
            left = packets.get(str(edge.get("from")))
            right = packets.get(str(edge.get("to")))
            if not left or not right:
                continue
            sinks = sorted(set(edge.get("shared_sinks") or []))
            owned = sorted(
                (set(left.get("targets") or []) | set(right.get("targets") or [])) - set(sinks)
            )
            evidence = sorted(
                set(left.get("exact_refs") or []) | set(right.get("exact_refs") or [])
            )
            reasons = []
            if len(owned) < 2:
                reasons.append("C3_ADAPTER_REQUIRES_TWO_DISJOINT_TARGETS")
            if not sinks:
                reasons.append("C3_ADAPTER_REQUIRES_SHARED_SINK")
            if not evidence:
                reasons.append("C3_ADAPTER_REQUIRES_EVIDENCE_REFS")
            structural = {
                "proof_id": (
                    f"{partition.get('partition_id')}."
                    f"{left.get('packet_id')}.{right.get('packet_id')}"
                ),
                "disjoint_targets": owned,
                "shared_sinks": sinks,
                "evidence_refs": evidence,
            }
            adapters.append(
                {
                    "packet_ids": [left.get("packet_id"), right.get("packet_id")],
                    "eligible": not reasons,
                    "reason_codes": reasons,
                    "partition_proof": structural,
                    "independently_verified": False,
                    "standing": "COHESION_STRUCTURAL_ADAPTER_FOR_C3_DUPLICATE_GUARD",
                    "law": "PARTITION_PROOF != CLEAR_EXACT_WORK_IDENTITY",
                }
            )
        return adapters

    def partition(self, *args, **kwargs) -> Dict[str, Any]:
        result = super().partition(*args, **kwargs)
        partition = result.get("partition")
        if isinstance(partition, dict):
            result["c3_duplicate_guard_adapters"] = self._c3_adapters(partition)
        return result

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        value["partition_handoff_v3_bridge"] = {
            "version": RING2_V3_VERSION,
            "party_context": "PartyCoordinationRuntimeV3 / PARTY.REWARD.PROVENANCE.3",
            "c3_adapter": (
                "shared-sink structural adapter only; independently_verified=false; "
                "never clears exact work-key/task identity"
            ),
        }
        return value
