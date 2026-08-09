from __future__ import annotations

"""Fast, bounded, non-authoritative inter-agent rendezvous plane.

The mesh is deliberately process-local and ephemeral. Material packets may be
explicitly compacted into Message Board/Cohesion; ordinary touches never mutate
Git. Routing priority is attention state, not evidence or truth.
"""

import hashlib
import json
import math
import threading
import time
from collections import defaultdict
from typing import Any, Iterable

from .liminal_beacon_mesh_protocol import LIMINAL_BEACON_TOOL_NAMES, RECEIPT_STAGES

VERSION = "LIMINAL.BEACON.MESH.1"
ARTIFACT = "ATHENA.LIMINAL.BEACON.MESH.V1.CANDIDATE"
CRITICAL_CLASSES = {"BLOCKER", "CORRECTION", "RETRACTION", "HANDOFF"}
BRIDGE_CLASSES = CRITICAL_CLASSES | {"NEED", "OFFER", "DISCOVERY", "RESULT"}

LAWS = [
    "L2_REMAINS_NAVIGATION_CORE",
    "COMMUNICATION_FIBRE != OBJECT_IDENTITY",
    "PRESENCE != WORKING",
    "AGENT_IDENTITY != PROCESS_INSTANCE",
    "BEACON != CLAIM",
    "ROUTE != DELIVERY != PRESENTATION != CONSUMPTION != INCORPORATION != PROPAGATION",
    "ROUTING_SCORE != TRUTH",
    "TOPOLOGICAL_NEIGHBOR != TRUST",
    "QUORUM_SIGNAL != EVIDENCE",
    "EPHEMERAL_LIVENESS != DURABLE_SEMANTIC_MEMORY",
    "RUNTIME_PULSE != GIT_COMMIT",
    "GIT_HISTORY_DOES_NOT_EVAPORATE_WITH_PHEROMONE_DECAY",
    "UNOBSERVED != ABSENT",
    "AUTOHOOK != HIDDEN_BACKGROUND_AGENT_EXECUTION",
]

_ROUTE_FIELDS = {
    "work_refs": "work",
    "object_refs": "object",
    "dependency_refs": "dep",
    "causal_refs": "causal",
    "semantic_tags": "sem",
    "kc_refs": "kc",
    "party_refs": "party",
}
_CAP_FIELDS = ("capabilities", "needs", "offers", "provides")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _names(values: Iterable[Any] | None) -> list[str]:
    out, seen = [], set()
    for raw in values or []:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return sorted(out)


def _route_atom(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _route_keys(value: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for field, prefix in _ROUTE_FIELDS.items():
        for raw in value.get(field) or []:
            atom = _route_atom(raw)
            if atom:
                keys.add(f"{prefix}:{atom}")
    for field in _CAP_FIELDS:
        for raw in value.get(field) or []:
            atom = _route_atom(raw)
            if atom:
                # NEED and OFFER intentionally meet on one capability rendezvous key.
                keys.add(f"cap:{atom}")
    return keys


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _public_presence(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if not k.startswith("_")}


def _packet_capsule(row: dict[str, Any], score: float | None = None) -> dict[str, Any]:
    value = {
        key: row.get(key)
        for key in (
            "packet_id", "event_seq", "sender_id", "instance_id", "session_epoch",
            "sender_seq", "lamport", "message_class", "summary", "payload_ref", "goal_ref",
            "evidence_ceiling", "urgency", "novelty", "created_at", "expires_at", "visibility",
            "recipients", "changed_refs", "affected_refs", "correction_of", "retraction_of",
            "reply_to", "parent_ids", "semantic_digest",
        )
    }
    if score is not None:
        value["route_score"] = round(float(score), 6)
    return value


class LiminalBeaconMeshRuntime:
    def __init__(self, server: Any, clock=None):
        self.server = server
        self.clock = clock or time.time
        self._lock = threading.RLock()
        self._presence: dict[str, dict[str, Any]] = {}
        self._packets: dict[str, dict[str, Any]] = {}
        self._route_index: dict[str, set[str]] = defaultdict(set)
        self._receipts: dict[tuple[str, str], dict[str, Any]] = {}
        self._reverse_consumers: dict[str, set[str]] = defaultdict(set)
        self._sender_seq: dict[tuple[str, str], int] = defaultdict(int)
        self._event_seq = 0
        self._lamport = 0
        self._cursors: dict[str, int] = defaultdict(int)
        self._metrics = defaultdict(int)

    def _now(self) -> float:
        return float(self.clock())

    def _prune(self) -> None:
        now = self._now()
        for agent_id, row in list(self._presence.items()):
            if _finite(row.get("expires_at"), 0.0) <= now:
                row["liveness"] = "EXPIRED"
        for packet_id, row in list(self._packets.items()):
            if _finite(row.get("expires_at"), 0.0) > now:
                continue
            for key in row.get("_route_keys") or []:
                self._route_index[key].discard(packet_id)
                if not self._route_index[key]:
                    self._route_index.pop(key, None)
            self._packets.pop(packet_id, None)
            self._metrics["expired_packets"] += 1

    def manifest(self) -> dict[str, Any]:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "standing": "CANDIDATE_RUNTIME_NON_AUTHORITATIVE",
            "coordinate": "LCOM=<L2|BF,TF,IF,DF,AF,CF,RF,SF,MF,HF>",
            "persistence": {
                "presence": "PROCESS_LOCAL_EPHEMERAL",
                "packets": "PROCESS_LOCAL_EPHEMERAL_TTL",
                "receipts": "PROCESS_LOCAL_UNTIL_EXPLICIT_DURABLE_BRIDGE",
                "durable_bridge": ["MESSAGE_BOARD", "COHESION"],
                "git_default": "NO_GIT_WRITE_FOR_TOUCH_OR_RENDEZVOUS",
            },
            "autohook": {
                "installed": True,
                "activation": "ATHENA_LIMINAL_AUTOHOOK=1",
                "default": "DISABLED",
                "behavior": "touch + bounded metadata-only result beacon + rendezvous on exposed tool crossings",
                "background_execution": False,
            },
            "receipt_ladder": ["INDEXED", "ROUTED", "DELIVERED", *RECEIPT_STAGES],
            "laws": list(LAWS),
        }

    def touch(
        self,
        agent_id: str,
        *,
        instance_id: str | None = None,
        session_epoch: str | None = None,
        activity: str = "WORKING",
        focus: str | None = None,
        capacity: float | None = None,
        availability: float | None = None,
        work_refs=None,
        object_refs=None,
        dependency_refs=None,
        causal_refs=None,
        semantic_tags=None,
        kc_refs=None,
        party_refs=None,
        capabilities=None,
        needs=None,
        offers=None,
        blockers=None,
        provides=None,
        visibility: str = "COLONY",
        lease_seconds: int = 30,
    ) -> dict[str, Any]:
        agent_id = str(agent_id or "").strip()
        if not agent_id:
            raise ValueError("agent_id is required")
        lease_seconds = max(1, min(int(lease_seconds or 30), 3600))
        with self._lock:
            self._prune()
            now = self._now()
            previous = self._presence.get(agent_id) or {}
            effective_instance = str(instance_id).strip() if instance_id else str(previous.get("instance_id") or "UNKNOWN")
            effective_epoch = str(session_epoch).strip() if session_epoch else str(previous.get("session_epoch") or "UNKNOWN")
            same_epoch = (
                previous.get("liveness") == "ACTIVE"
                and previous.get("instance_id") == effective_instance
                and previous.get("session_epoch") == effective_epoch
            )
            heartbeat_seq = int(previous.get("heartbeat_seq") or 0) + 1 if same_epoch else 1
            payload = {
                "artifact": "ATHENA.LIMINAL.BEACON.PRESENCE.V1",
                "agent_id": agent_id,
                "instance_id": effective_instance,
                "session_epoch": effective_epoch,
                "lease_id": "LBLEASE." + _digest([agent_id, effective_instance, effective_epoch])[:24],
                "liveness": "ACTIVE",
                "activity": str(activity or "UNKNOWN").upper(),
                "heartbeat_seq": heartbeat_seq,
                "focus": str(focus).strip()[:512] if focus else None,
                "capacity": None if capacity is None else _clip(_finite(capacity)),
                "availability": None if availability is None else _clip(_finite(availability)),
                "work_refs": _names(work_refs),
                "object_refs": _names(object_refs),
                "dependency_refs": _names(dependency_refs),
                "causal_refs": _names(causal_refs),
                "semantic_tags": _names(semantic_tags),
                "kc_refs": _names(kc_refs),
                "party_refs": _names(party_refs),
                "capabilities": _names(capabilities),
                "needs": _names(needs),
                "offers": _names(offers),
                "blockers": _names(blockers),
                "provides": _names(provides),
                "visibility": str(visibility or "COLONY").upper(),
                "last_seen": now,
                "expires_at": now + lease_seconds,
                "lease_seconds": lease_seconds,
            }
            payload["_route_keys"] = sorted(_route_keys(payload))
            self._presence[agent_id] = payload
            self._metrics["touches"] += 1
            return {
                "status": "TOUCHED",
                "presence": _public_presence(payload),
                "route_key_count": len(payload["_route_keys"]),
                "durable_return": False,
                "law": "TOUCH != CLAIM != GIT_WRITE",
            }

    def _require_active(self, agent_id: str) -> dict[str, Any]:
        self._prune()
        row = self._presence.get(agent_id)
        if not row or row.get("liveness") != "ACTIVE":
            raise ValueError("LIMINAL_AGENT_NOT_PRESENT_HOLD: touch before emit/rendezvous")
        return row

    def emit(
        self,
        agent_id: str,
        message_class: str,
        summary: str,
        **kwargs,
    ) -> dict[str, Any]:
        agent_id = str(agent_id or "").strip()
        message_class = str(message_class or "").upper()
        summary = str(summary or "").strip()
        if not summary:
            raise ValueError("summary is required")
        with self._lock:
            sender = self._require_active(agent_id)
            now = self._now()
            sender_key = (agent_id, str(sender.get("session_epoch")))
            self._sender_seq[sender_key] += 1
            sender_seq = self._sender_seq[sender_key]
            parent_ids = _names(kwargs.get("parent_ids"))
            parent_lamports = [int((self._packets.get(pid) or {}).get("lamport") or 0) for pid in parent_ids]
            self._lamport = max([self._lamport, *parent_lamports], default=self._lamport) + 1
            ttl = max(1, min(int(kwargs.get("ttl_seconds") or 900), 86400))
            route_basis = {
                field: _names(kwargs.get(field)) or list(sender.get(field) or [])
                for field in _ROUTE_FIELDS
            }
            for field in _CAP_FIELDS:
                route_basis[field] = _names(kwargs.get(field)) or list(sender.get(field) or [])
            route_keys = sorted(_route_keys(route_basis))
            recipients = _names(kwargs.get("recipients"))
            correction_of = str(kwargs.get("correction_of") or "").strip() or None
            retraction_of = str(kwargs.get("retraction_of") or "").strip() or None
            reverse_targets = set(recipients)
            for origin in (correction_of, retraction_of):
                if origin:
                    reverse_targets.update(self._reverse_consumers.get(origin) or set())
            basis = {
                "version": VERSION,
                "sender_id": agent_id,
                "instance_id": sender.get("instance_id"),
                "session_epoch": sender.get("session_epoch"),
                "sender_seq": sender_seq,
                "lamport": self._lamport,
                "message_class": message_class,
                "summary": summary[:1200],
                "payload_ref": str(kwargs.get("payload_ref") or "").strip() or None,
                "goal_ref": str(kwargs.get("goal_ref") or "").strip() or None,
                "evidence_ceiling": str(kwargs.get("evidence_ceiling") or "").strip() or None,
                "route_keys": route_keys,
                "recipients": recipients,
                "visibility": str(kwargs.get("visibility") or sender.get("visibility") or "COLONY").upper(),
                "changed_refs": _names(kwargs.get("changed_refs")),
                "affected_refs": _names(kwargs.get("affected_refs")),
                "correction_of": correction_of,
                "retraction_of": retraction_of,
                "reply_to": str(kwargs.get("reply_to") or "").strip() or None,
                "parent_ids": parent_ids,
            }
            packet_id = "LBM." + _digest(basis)[:32]
            existing = self._packets.get(packet_id)
            if existing:
                return {"status": "ALREADY_EMITTED", "packet": _packet_capsule(existing), "idempotent": True}
            self._event_seq += 1
            packet = {
                "artifact": "ATHENA.LIMINAL.BEACON.PACKET.V1",
                "packet_id": packet_id,
                "event_seq": self._event_seq,
                "sender_id": agent_id,
                "instance_id": sender.get("instance_id"),
                "session_epoch": sender.get("session_epoch"),
                "sender_seq": sender_seq,
                "lamport": self._lamport,
                "message_class": message_class,
                "summary": summary[:1200],
                "payload_ref": basis["payload_ref"],
                "goal_ref": basis["goal_ref"],
                "evidence_ceiling": basis["evidence_ceiling"],
                "urgency": _clip(_finite(kwargs.get("urgency"), 0.5)),
                "novelty": _clip(_finite(kwargs.get("novelty"), 0.5)),
                "created_at": now,
                "expires_at": now + ttl,
                "ttl_seconds": ttl,
                "visibility": basis["visibility"],
                "recipients": recipients,
                "changed_refs": basis["changed_refs"],
                "affected_refs": basis["affected_refs"],
                "capabilities": _names(kwargs.get("capabilities")) or list(sender.get("capabilities") or []),
                "needs": _names(kwargs.get("needs")) or list(sender.get("needs") or []),
                "offers": _names(kwargs.get("offers")) or list(sender.get("offers") or []),
                "provides": _names(kwargs.get("provides")) or list(sender.get("provides") or []),
                "dependencies": _names(kwargs.get("dependencies")),
                "capacity_units": max(1, min(int(kwargs.get("capacity_units") or 1), 64)),
                "needed_units": max(1, min(int(kwargs.get("needed_units") or 1), 64)),
                "correction_of": correction_of,
                "retraction_of": retraction_of,
                "reply_to": basis["reply_to"],
                "parent_ids": parent_ids,
                "semantic_digest": _digest({k: basis[k] for k in basis if k not in {"sender_seq", "lamport"}}),
                "_route_keys": route_keys,
                "_reverse_targets": sorted(reverse_targets),
            }
            self._packets[packet_id] = packet
            for key in route_keys:
                self._route_index[key].add(packet_id)
            self._metrics["emitted"] += 1
            return {
                "status": "EMITTED",
                "packet": _packet_capsule(packet),
                "indexed_route_keys": len(route_keys),
                "reverse_targets": sorted(reverse_targets),
                "durable_return": False,
                "law": "EMIT != DELIVERY != CONSUMPTION",
            }

    @staticmethod
    def _visible(packet: dict[str, Any], agent_id: str) -> bool:
        recipients = set(packet.get("recipients") or [])
        return not recipients or agent_id in recipients

    def _receipt_stage(self, agent_id: str, packet_id: str) -> str | None:
        return (self._receipts.get((agent_id, packet_id)) or {}).get("stage")

    def _route_score(self, receiver: dict[str, Any], packet: dict[str, Any], reverse: bool = False) -> tuple[float, int]:
        receiver_keys = set(receiver.get("_route_keys") or [])
        packet_keys = set(packet.get("_route_keys") or [])
        intersection = receiver_keys & packet_keys
        denom = math.sqrt(max(1, len(receiver_keys)) * max(1, len(packet_keys)))
        match = len(intersection) / denom
        now = self._now()
        age = max(0.0, now - _finite(packet.get("created_at"), now))
        ttl = max(1.0, _finite(packet.get("ttl_seconds"), 900.0))
        freshness = math.exp(-age / max(1.0, ttl / 2.0))
        urgency = _clip(_finite(packet.get("urgency"), 0.5))
        novelty = _clip(_finite(packet.get("novelty"), 0.5))
        bridge = 1.0 if packet.get("message_class") in BRIDGE_CLASSES else 0.25
        score = 0.38 * match + 0.20 * urgency + 0.16 * freshness + 0.10 * novelty + 0.06 * bridge + 0.10 * (1.0 if reverse else 0.0)
        return _clip(score), len(intersection)

    def _neighbors(self, agent_id: str, receiver: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
        rkeys = set(receiver.get("_route_keys") or [])
        rows = []
        now = self._now()
        for other_id, other in self._presence.items():
            if other_id == agent_id or other.get("liveness") != "ACTIVE":
                continue
            overlap = rkeys & set(other.get("_route_keys") or [])
            if not overlap:
                continue
            rows.append({
                "agent_id": other_id,
                "instance_id": other.get("instance_id"),
                "activity": other.get("activity"),
                "focus": other.get("focus"),
                "capabilities": list(other.get("capabilities") or []),
                "needs": list(other.get("needs") or []),
                "offers": list(other.get("offers") or []),
                "route_overlap": len(overlap),
                "last_seen_age": max(0.0, now - _finite(other.get("last_seen"), now)),
            })
        rows.sort(key=lambda x: (-int(x["route_overlap"]), float(x["last_seen_age"]), str(x["agent_id"])))
        return rows[:limit]

    def rendezvous(
        self,
        agent_id: str,
        *,
        cursor: int | None = None,
        limit: int = 8,
        threshold: float = 0.35,
        context_budget: int = 4096,
        scout_quota: int = 1,
    ) -> dict[str, Any]:
        agent_id = str(agent_id or "").strip()
        with self._lock:
            receiver = self._require_active(agent_id)
            start_cursor = self._cursors[agent_id] if cursor is None else max(0, int(cursor))
            limit = max(1, min(int(limit or 8), 32))
            scout_quota = max(0, min(int(scout_quota or 0), 4))
            budget = max(256, min(int(context_budget or 4096), 16384))
            base_threshold = _clip(_finite(threshold, 0.35))
            rkeys = set(receiver.get("_route_keys") or [])
            candidate_ids: set[str] = set()
            for key in rkeys:
                candidate_ids.update(self._route_index.get(key) or set())
            for packet_id, packet in self._packets.items():
                if agent_id in set(packet.get("_reverse_targets") or []):
                    candidate_ids.add(packet_id)
            unseen = []
            for packet_id in candidate_ids:
                packet = self._packets.get(packet_id)
                if not packet or packet.get("sender_id") == agent_id or not self._visible(packet, agent_id):
                    continue
                if self._receipt_stage(agent_id, packet_id):
                    continue
                reverse = agent_id in set(packet.get("_reverse_targets") or [])
                score, overlap = self._route_score(receiver, packet, reverse=reverse)
                # Active topological signals remain encounterable after a receiver moves into
                # their neighborhood even if their event_seq predates the scan cursor.
                if not reverse and not overlap and int(packet.get("event_seq") or 0) <= start_cursor:
                    continue
                unseen.append((score, overlap, reverse, packet))
            queue_pressure = _clip(len(unseen) / 64.0)
            effective_threshold = _clip(base_threshold + 0.25 * queue_pressure, 0.0, 0.95)
            ranked = []
            for score, overlap, reverse, packet in unseen:
                local_threshold = max(0.0, effective_threshold - (0.18 if packet.get("message_class") in CRITICAL_CLASSES else 0.0))
                if reverse or overlap > 0 or score >= local_threshold:
                    ranked.append((score, overlap, reverse, packet))
            ranked.sort(key=lambda x: (-x[0], -x[1], int(x[3].get("event_seq") or 0), str(x[3].get("packet_id"))))

            if scout_quota:
                known = {row[3]["packet_id"] for row in ranked}
                scouts = []
                for packet in self._packets.values():
                    pid = packet["packet_id"]
                    if pid in known or packet.get("sender_id") == agent_id or not self._visible(packet, agent_id) or self._receipt_stage(agent_id, pid):
                        continue
                    age = max(0.0, self._now() - _finite(packet.get("created_at"), self._now()))
                    freshness = math.exp(-age / max(1.0, _finite(packet.get("ttl_seconds"), 900.0) / 2.0))
                    scout_score = 0.55 * _clip(_finite(packet.get("novelty"), 0.5)) + 0.30 * freshness + 0.15 * _clip(_finite(packet.get("urgency"), 0.5))
                    scouts.append((scout_score, 0, False, packet))
                scouts.sort(key=lambda x: (-x[0], int(x[3].get("event_seq") or 0)))
                ranked.extend(scouts[:scout_quota])

            selected, used = [], 0
            for score, overlap, reverse, packet in ranked:
                if len(selected) >= limit:
                    break
                capsule = _packet_capsule(packet, score)
                capsule["route_overlap"] = overlap
                capsule["reverse_route"] = reverse
                cost = len(json.dumps(capsule, ensure_ascii=False, sort_keys=True))
                if selected and used + cost > budget:
                    continue
                if cost > budget and not selected:
                    capsule = {
                        "packet_id": packet["packet_id"],
                        "event_seq": packet["event_seq"],
                        "sender_id": packet["sender_id"],
                        "message_class": packet["message_class"],
                        "summary": packet["summary"][:256],
                        "route_score": round(float(score), 6),
                        "truncated": True,
                    }
                    cost = len(json.dumps(capsule, ensure_ascii=False, sort_keys=True))
                selected.append(capsule)
                used += cost
                key = (agent_id, packet["packet_id"])
                self._receipts[key] = {
                    "agent_id": agent_id,
                    "packet_id": packet["packet_id"],
                    "stage": "PRESENTED",
                    "stage_index": RECEIPT_STAGES.index("PRESENTED"),
                    "updated_at": self._now(),
                    "disposition": None,
                    "consumer_ref": None,
                    "residual": None,
                    "propagation_refs": [],
                    "outcome_ref": None,
                }
                self._metrics["presented"] += 1
            self._cursors[agent_id] = max(start_cursor, self._event_seq)
            self._metrics["rendezvous_calls"] += 1
            return {
                "status": "RENDEZVOUS",
                "agent_id": agent_id,
                "neighbors": self._neighbors(agent_id, receiver),
                "packets": selected,
                "cursor_before": start_cursor,
                "next_cursor": self._cursors[agent_id],
                "queue_pressure": round(queue_pressure, 6),
                "effective_threshold": round(effective_threshold, 6),
                "context_budget": budget,
                "context_used": used,
                "receipt_standing": "PACKETS_PRESENTED_NOT_CONSUMED",
                "law": "PRESENTED != CONSUMED",
            }

    def receipt(
        self,
        agent_id: str,
        packet_id: str,
        stage: str,
        *,
        disposition: str | None = None,
        consumer_ref: str | None = None,
        residual: str | None = None,
        propagation_refs=None,
        outcome_ref: str | None = None,
    ) -> dict[str, Any]:
        stage = str(stage or "").upper()
        if stage not in RECEIPT_STAGES:
            raise ValueError("invalid receipt stage")
        with self._lock:
            if packet_id not in self._packets:
                raise ValueError("LIMINAL_PACKET_NOT_FOUND_HOLD")
            key = (agent_id, packet_id)
            previous = self._receipts.get(key)
            wanted = RECEIPT_STAGES.index(stage)
            if previous is None:
                if stage != "PRESENTED":
                    raise ValueError("RECEIPT_PREREQUISITE_HOLD: packet must be PRESENTED before later cognition can be claimed")
                previous_index = -1
            else:
                previous_index = int(previous.get("stage_index", -1))
                if wanted < previous_index:
                    raise ValueError("RECEIPT_REGRESSION_HOLD")
                if wanted > previous_index + 1:
                    raise ValueError("RECEIPT_STAGE_SKIP_HOLD")
                if wanted == previous_index:
                    return {"status": "RECEIPT_ALREADY_AT_STAGE", "receipt": dict(previous), "idempotent": True}
            row = dict(previous or {})
            row.update({
                "agent_id": agent_id,
                "packet_id": packet_id,
                "stage": stage,
                "stage_index": wanted,
                "updated_at": self._now(),
                "disposition": disposition,
                "consumer_ref": str(consumer_ref).strip() if consumer_ref else None,
                "residual": str(residual).strip() if residual else None,
                "propagation_refs": _names(propagation_refs),
                "outcome_ref": str(outcome_ref).strip() if outcome_ref else None,
            })
            self._receipts[key] = row
            if wanted >= RECEIPT_STAGES.index("CONSUMED"):
                self._reverse_consumers[packet_id].add(agent_id)
            self._metrics[stage.casefold()] += 1
            return {
                "status": "RECEIPT_ADVANCED",
                "receipt": dict(row),
                "reverse_route_registered": wanted >= RECEIPT_STAGES.index("CONSUMED"),
                "law": "RECEIPT_STAGE != OUTCOME_IMPROVEMENT",
            }

    def bridge(self, packet_id: str, bridge_kind: str = "AUTO", remote: str = "origin", allow_collaboration: bool = False, role: str | None = None) -> dict[str, Any]:
        with self._lock:
            packet = self._packets.get(packet_id)
            if not packet:
                raise ValueError("LIMINAL_PACKET_NOT_FOUND_HOLD")
            sender_id = str(packet.get("sender_id"))
            kind = str(bridge_kind or "AUTO").upper()
            if kind == "AUTO":
                kind = "COHESION" if packet.get("message_class") in {"NEED", "OFFER"} else "MESSAGE_BOARD"
            if kind == "MESSAGE_BOARD":
                from .message_board import MessageBoardRuntime

                kind_map = {
                    "BLOCKER": "BLOCKER", "DISCOVERY": "DISCOVERY", "QUESTION": "QUESTION",
                    "ANSWER": "ANSWER", "HANDOFF": "HANDOFF", "NEED": "HELP", "OFFER": "INFO",
                    "RESULT": "UPDATE", "CORRECTION": "UPDATE", "RETRACTION": "UPDATE",
                }
                text = packet["summary"]
                if packet.get("payload_ref"):
                    text += f"\nref={packet['payload_ref']}"
                result = MessageBoardRuntime(self.server.git).post(
                    agent_id=sender_id,
                    message=text,
                    message_kind=kind_map.get(str(packet.get("message_class")), "INFO"),
                    recipients=list(packet.get("recipients") or []),
                    reply_to=packet.get("reply_to"),
                    remote=remote,
                )
            elif kind == "COHESION":
                if packet.get("message_class") not in {"NEED", "OFFER"}:
                    raise ValueError("COHESION_BRIDGE_REQUIRES_NEED_OR_OFFER")
                from .cohesion_mesh import CohesionMeshRuntime

                capabilities = list(packet.get("capabilities") or packet.get("needs") or packet.get("offers") or [])
                if not capabilities:
                    raise ValueError("COHESION_BRIDGE_REQUIRES_CAPABILITIES")
                result = CohesionMeshRuntime(self.server).request_offer(
                    request_id="LBM-" + packet_id.split(".", 1)[-1],
                    agent_id=sender_id,
                    kind=str(packet.get("message_class")),
                    capabilities=capabilities,
                    goal_ref=str(packet.get("goal_ref") or packet.get("payload_ref") or packet.get("summary")),
                    role=str(role or ""),
                    dependencies=list(packet.get("dependencies") or []),
                    provides=list(packet.get("provides") or []),
                    capacity_units=int(packet.get("capacity_units") or 1),
                    needed_units=int(packet.get("needed_units") or 1),
                    allow_collaboration=bool(allow_collaboration),
                    remote=remote,
                )
            else:
                raise ValueError("bridge_kind must be AUTO, MESSAGE_BOARD, or COHESION")
            success = isinstance(result, dict) and not str(result.get("status") or "").endswith("HOLD")
            if success:
                self._metrics["durable_bridges"] += 1
            return {
                "status": "BRIDGED" if success else "BRIDGE_HOLD",
                "bridge_kind": kind,
                "packet_id": packet_id,
                "bridge_result": result,
                "law": "DURABLE_BRIDGE != TRUTH_OR_EXECUTION_AUTHORITY",
            }

    def state(self, agent_id: str | None = None, include_packets: bool = False, limit: int = 50) -> dict[str, Any]:
        with self._lock:
            self._prune()
            active = [_public_presence(v) for v in self._presence.values() if v.get("liveness") == "ACTIVE"]
            active.sort(key=lambda x: str(x.get("agent_id")))
            receipts = [dict(v) for v in self._receipts.values() if not agent_id or v.get("agent_id") == agent_id]
            receipts.sort(key=lambda x: (float(x.get("updated_at") or 0), str(x.get("packet_id"))), reverse=True)
            touches = int(self._metrics.get("touches", 0))
            bridges = int(self._metrics.get("durable_bridges", 0))
            result = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "status": "OK",
                "active_presence": active if not agent_id else [x for x in active if x.get("agent_id") == agent_id],
                "active_presence_count": len(active),
                "packet_count": len(self._packets),
                "receipt_count": len(self._receipts),
                "receipts": receipts[: max(1, min(int(limit or 50), 200))],
                "metrics": dict(sorted(self._metrics.items())),
                "git_write_amplification_proxy": round(bridges / max(1, touches), 8),
                "hidden_process_count": "UNKNOWN",
                "independent_process_count": "UNKNOWN",
                "durable_return_default": False,
                "laws": list(LAWS),
            }
            if include_packets:
                packets = sorted(self._packets.values(), key=lambda x: int(x.get("event_seq") or 0), reverse=True)
                result["packets"] = [_packet_capsule(row) for row in packets[: max(1, min(int(limit or 50), 200))]]
            return result

    @staticmethod
    def infer_agent_id(arguments: dict[str, Any]) -> str | None:
        for key in ("agent_id", "agent", "observer_id", "proposer_id", "worker_id"):
            raw = arguments.get(key)
            if isinstance(raw, str) and raw.strip():
                return raw.strip()[:128]
        actor = arguments.get("actor")
        if isinstance(actor, str) and actor.strip() and actor.strip().casefold() not in {"agent", "athena"}:
            return actor.strip()[:128]
        return None

    @staticmethod
    def _refs_from_call(arguments: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
        work, objects, deps = [], [], []
        for key in ("run_id", "loop_id", "claim_id", "work_key", "task", "request_id", "campaign_id"):
            if arguments.get(key) not in (None, ""):
                work.append(f"{key}:{arguments[key]}")
        for key in ("oid", "object_id", "target_oid", "topology_id", "subject_id"):
            if arguments.get(key) not in (None, ""):
                objects.append(f"{key}:{arguments[key]}")
        for key in ("source_ref", "expected_vid", "expected_git_head", "parent_id", "reply_to"):
            if arguments.get(key) not in (None, ""):
                deps.append(f"{key}:{arguments[key]}")
        return work, objects, deps

    def auto_before_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
        agent_id = self.infer_agent_id(arguments)
        if not agent_id:
            return None
        work, objects, deps = self._refs_from_call(arguments)
        focus = f"tool:{name}"
        task = arguments.get("task")
        if isinstance(task, str) and task.strip():
            focus += " " + task.strip()[:320]
        self.touch(
            agent_id,
            activity="WORKING",
            focus=focus,
            work_refs=work,
            object_refs=objects,
            dependency_refs=deps,
            semantic_tags=[f"tool:{name}"],
            lease_seconds=30,
        )
        return self.rendezvous(agent_id, limit=4, threshold=0.35, context_budget=2400, scout_quota=1)

    def auto_after_tool(self, name: str, arguments: dict[str, Any], value: Any) -> dict[str, Any] | None:
        agent_id = self.infer_agent_id(arguments)
        if not agent_id or not isinstance(value, dict):
            return None
        status = str(value.get("status") or value.get("pre_dispatch") or "").strip()
        if not status:
            return None
        work, objects, deps = self._refs_from_call(arguments)
        message_class = "BLOCKER" if any(token in status.upper() for token in ("HOLD", "BLOCK", "ERROR", "STALE")) else "RESULT"
        changed = []
        for key in ("event", "eid", "run_id", "claim_id", "head", "git_head", "routing_digest", "decision_digest"):
            if value.get(key) not in (None, ""):
                changed.append(f"{key}:{value[key]}")
        emitted = self.emit(
            agent_id,
            message_class,
            f"tool:{name} status:{status}",
            work_refs=work,
            object_refs=objects,
            dependency_refs=deps,
            semantic_tags=[f"tool:{name}", f"status:{status}"],
            changed_refs=changed,
            urgency=0.85 if message_class == "BLOCKER" else 0.45,
            novelty=0.35,
            ttl_seconds=300,
            evidence_ceiling="RUNTIME_METADATA_ONLY",
        )
        return {
            "emitted": emitted.get("packet"),
            "rendezvous": self.rendezvous(agent_id, limit=4, threshold=0.35, context_budget=2400, scout_quota=1),
            "law": "AUTO_METADATA_BEACON != FULL_TOOL_RESULT_SHARING",
        }

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in LIMINAL_BEACON_TOOL_NAMES:
            raise KeyError(name)
        if name == "athena_liminal_beacon_manifest":
            return self.manifest()
        if name == "athena_liminal_beacon_touch":
            return self.touch(**arguments)
        if name == "athena_liminal_beacon_emit":
            args = dict(arguments)
            args["message_class"] = args.pop("message_class")
            return self.emit(**args)
        if name == "athena_liminal_beacon_rendezvous":
            return self.rendezvous(**arguments)
        if name == "athena_liminal_beacon_receipt":
            return self.receipt(**arguments)
        if name == "athena_liminal_beacon_bridge":
            return self.bridge(**arguments)
        if name == "athena_liminal_beacon_state":
            return self.state(**arguments)
        raise KeyError(name)


__all__ = ["LiminalBeaconMeshRuntime", "VERSION", "ARTIFACT", "LAWS"]
