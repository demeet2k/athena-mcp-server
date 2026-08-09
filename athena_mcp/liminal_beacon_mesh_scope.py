from __future__ import annotations

"""Fail-closed visibility treatment for Liminal Beacon Mesh V1.

V1 has one process-local colony plane. PUBLIC and COLONY therefore share the
same physical carrier today, while GUILD requires a shared party/guild route and
LOCAL requires explicit addressing. These rules are transport scope only; they
do not imply authorization, trust or evidence.
"""

import json


def _cost(value) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _party_keys(row) -> set[str]:
    return {str(key) for key in (row.get("_route_keys") or []) if str(key).startswith("party:")}


def _allowed(packet, receiver, agent_id: str) -> bool:
    recipients = {str(value) for value in (packet.get("recipients") or [])}
    if recipients:
        return agent_id in recipients
    visibility = str(packet.get("visibility") or "COLONY").upper()
    if visibility in {"PUBLIC", "COLONY"}:
        return True
    if visibility == "GUILD":
        return bool(_party_keys(packet) & _party_keys(receiver))
    if visibility == "LOCAL":
        return False
    return False


def _presence_allowed(other, receiver) -> bool:
    visibility = str(other.get("visibility") or "COLONY").upper()
    if visibility in {"PUBLIC", "COLONY"}:
        return True
    if visibility == "GUILD":
        return bool(_party_keys(other) & _party_keys(receiver))
    return False


def install_liminal_beacon_scope(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_liminal_scope_v1_registered", False):
        return

    previous_rendezvous = runtime_cls.rendezvous

    def rendezvous_with_scope(self, *args, **kwargs):
        result = previous_rendezvous(self, *args, **kwargs)
        agent_id = str(result.get("agent_id") or "")
        receiver = self._presence.get(agent_id) or {}
        allowed_packets = []
        filtered = []

        for capsule in result.get("packets") or []:
            packet_id = str(capsule.get("packet_id") or "")
            raw = self._packets.get(packet_id) or {}
            if _allowed(raw, receiver, agent_id):
                allowed_packets.append(capsule)
                continue
            filtered.append(packet_id)
            key = (agent_id, packet_id)
            receipt = self._receipts.get(key)
            if isinstance(receipt, dict) and receipt.get("stage") == "PRESENTED":
                self._receipts.pop(key, None)
                self._metrics["presented"] = max(0, int(self._metrics.get("presented", 0)) - 1)
            self._metrics["scope_filtered"] += 1

        allowed_neighbors = []
        for neighbor in result.get("neighbors") or []:
            other = self._presence.get(str(neighbor.get("agent_id") or "")) or {}
            if _presence_allowed(other, receiver):
                allowed_neighbors.append(neighbor)
            else:
                self._metrics["scope_filtered_neighbors"] += 1

        result["packets"] = allowed_packets
        result["neighbors"] = allowed_neighbors
        packet_used = sum(_cost(packet) for packet in allowed_packets)
        neighbor_used = sum(_cost(row) for row in allowed_neighbors)
        result["packet_context_used"] = packet_used
        result["neighbor_context_used"] = neighbor_used
        result["context_used"] = packet_used + neighbor_used
        result["scope_filtered"] = filtered
        result["scope_law"] = (
            "VISIBILITY != AUTHORITY; LOCAL_REQUIRES_EXPLICIT_RECIPIENT; "
            "GUILD_REQUIRES_SHARED_PARTY_ROUTE; COLONY_IS_CURRENT_PROCESS_LOCAL_CARRIER"
        )
        return result

    runtime_cls.rendezvous = rendezvous_with_scope
    runtime_cls._athena_liminal_scope_v1_registered = True


__all__ = ["install_liminal_beacon_scope"]
