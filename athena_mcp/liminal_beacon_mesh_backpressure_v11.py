from __future__ import annotations

"""Bounded receiver-owned critical reserve for Liminal Beacon Mesh V1.1.

This is the V1 backpressure law plus one finite reserve channel.  Critical class
labels do not become evidence, truth or authority and cannot create unbounded
attention bypass: at most ``critical_quota`` otherwise-filtered critical packets
already selected by the base routing pass may survive, with a hard cap of two.
"""

import json

CRITICAL_CLASSES = {"BLOCKER", "CORRECTION", "RETRACTION", "HANDOFF"}


def _cost(value) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _rollback_presented(self, agent_id: str, packet_id: str) -> None:
    key = (agent_id, packet_id)
    receipt = self._receipts.get(key)
    if isinstance(receipt, dict) and receipt.get("stage") == "PRESENTED":
        self._receipts.pop(key, None)
        self._metrics["presented"] = max(0, int(self._metrics.get("presented", 0)) - 1)


def install_liminal_beacon_backpressure_v11(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_liminal_backpressure_v11_registered", False):
        return

    previous_rendezvous = runtime_cls.rendezvous

    def rendezvous_with_backpressure_v11(self, *args, **kwargs):
        critical_quota = max(0, min(int(kwargs.pop("critical_quota", 1) or 0), 2))
        result = previous_rendezvous(self, *args, **kwargs)
        packets = list(result.get("packets") or [])
        threshold = float(result.get("effective_threshold") or 0.0)
        agent_id = str(result.get("agent_id") or "")
        kept = []
        filtered = []
        critical_used = 0

        for packet in packets:
            packet_id = str(packet.get("packet_id") or "")
            overlap = int(packet.get("route_overlap") or 0)
            raw_reverse = bool(packet.get("reverse_route"))
            correction = bool(packet.get("correction_of") or packet.get("retraction_of"))
            true_reverse = raw_reverse and correction
            recipients = {str(value) for value in (packet.get("recipients") or [])}
            direct = agent_id in recipients and not true_reverse
            message_class = str(packet.get("message_class") or "")
            critical = message_class in CRITICAL_CLASSES

            if true_reverse:
                packet["reverse_route"] = True
                packet["direct_route"] = False
                packet["critical_reserve"] = False
                kept.append(packet)
                continue

            # The existing bounded scout channel remains independent of the
            # critical reserve.  It cannot be multiplied by a critical label.
            if overlap == 0 and not direct:
                packet["reverse_route"] = False
                packet["direct_route"] = False
                packet["critical_reserve"] = False
                kept.append(packet)
                continue

            local_threshold = max(
                0.0,
                threshold
                - (0.18 if critical else 0.0)
                - (0.08 if direct else 0.0),
            )
            if float(packet.get("route_score") or 0.0) >= local_threshold:
                packet["reverse_route"] = False
                packet["direct_route"] = direct
                packet["critical_reserve"] = False
                kept.append(packet)
                continue

            # Reserve eligibility starts only after normal admission fails and
            # only for packets the base routing/context pass already selected.
            # Base ranking is descending by route score, so first eligible is
            # the highest-ranked reserve candidate under this rendezvous.
            if critical and critical_used < critical_quota:
                packet["reverse_route"] = False
                packet["direct_route"] = direct
                packet["critical_reserve"] = True
                kept.append(packet)
                critical_used += 1
                self._metrics["critical_reserve_presented"] += 1
                continue

            filtered.append(packet_id)
            _rollback_presented(self, agent_id, packet_id)
            self._metrics["backpressure_filtered"] += 1

        budget = int(result.get("context_budget") or 4096)
        packet_used = sum(_cost(packet) for packet in kept)
        remaining = max(0, budget - packet_used)
        bounded_neighbors = []
        neighbor_used = 0
        for row in result.get("neighbors") or []:
            compact = {
                "agent_id": row.get("agent_id"),
                "instance_id": row.get("instance_id"),
                "activity": row.get("activity"),
                "route_overlap": row.get("route_overlap"),
                "last_seen_age": row.get("last_seen_age"),
            }
            focus = str(row.get("focus") or "").strip()
            if focus:
                compact["focus"] = focus[:160]
            for field, cap in (("capabilities", 6), ("needs", 4), ("offers", 4)):
                values = [str(value) for value in (row.get(field) or [])[:cap]]
                if values:
                    compact[field] = values
            cost = _cost(compact)
            if cost <= remaining - neighbor_used:
                bounded_neighbors.append(compact)
                neighbor_used += cost
                continue
            minimal = {
                "agent_id": row.get("agent_id"),
                "activity": row.get("activity"),
                "route_overlap": row.get("route_overlap"),
            }
            cost = _cost(minimal)
            if cost <= remaining - neighbor_used:
                bounded_neighbors.append(minimal)
                neighbor_used += cost
            else:
                break

        result["packets"] = kept
        result["neighbors"] = bounded_neighbors
        result["packet_context_used"] = packet_used
        result["neighbor_context_used"] = neighbor_used
        result["context_used"] = packet_used + neighbor_used
        result["backpressure_filtered"] = filtered
        result["critical_quota"] = critical_quota
        result["critical_reserve_used"] = critical_used
        result["attention_law"] = (
            "TOPOLOGICAL_MATCH != ATTENTION_BYPASS; "
            "DIRECT_RECIPIENT != ATTENTION_BYPASS; "
            "CRITICAL_RESERVE != UNBOUNDED_BYPASS; "
            "CRITICAL_CLASS != AUTHORITY; "
            "PRESENCE_METADATA_COUNTS_AGAINST_CONTEXT_BUDGET"
        )
        return result

    runtime_cls.rendezvous = rendezvous_with_backpressure_v11
    runtime_cls._athena_liminal_backpressure_v11_registered = True


__all__ = ["install_liminal_beacon_backpressure_v11"]
