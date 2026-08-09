from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .cohesion_evidence_guard import CohesionEvidenceGuardRuntime
from .cohesion_mesh import COHESION_VERSION, _digest, _names
from .message_board import (
    _iso,
    _json_text,
    _norm_target,
    _parse_time,
    _require_id,
)
from .party_coordination_v2 import PartyCoordinationRuntimeV2

PARTITION_EVENT = "COHESION_PARTITION"
PARTITION_ARTIFACT = "ATHENA.COHESION.PARTITION.V1"
HANDOFF_ARTIFACT = "ATHENA.COHESION.HANDOFF.V1"
PARTITION_HANDOFF_VERSION = "COHESION.PARTITION.HANDOFF.1"


class CohesionPartitionHandoffRuntime(CohesionEvidenceGuardRuntime):
    """Ring-II partition proof + typed baton handoff over canonical Message Board.

    Partition validates explicit caller-supplied boundaries; it does not invent
    code ownership or assignments. Handoff is a Message Board route plus receipt
    projection. Cohesion never releases claims itself.
    """

    @staticmethod
    def _normalize_targets(values: Optional[Iterable[Any]]) -> List[str]:
        return sorted({_norm_target(str(value)) for value in (values or []) if _norm_target(str(value))})

    @staticmethod
    def _normalize_ids(values: Optional[Iterable[Any]], field: str) -> List[str]:
        rows = []
        seen = set()
        for value in values or []:
            item = _require_id(str(value), field)
            if item not in seen:
                seen.add(item)
                rows.append(item)
        return sorted(rows)

    def _normalize_packet(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        packet_id = _require_id(str(raw.get("packet_id") or ""), "packet_id")
        work_key = str(raw.get("work_key") or "").strip()
        if not work_key:
            raise ValueError(f"PARTITION_WORK_KEY_REQUIRED:{packet_id}")
        targets = self._normalize_targets(raw.get("targets"))
        if not targets:
            raise ValueError(f"PARTITION_TARGET_REQUIRED:{packet_id}")
        shared_sinks = self._normalize_targets(raw.get("shared_sinks"))
        unknown_shared = sorted(set(shared_sinks) - set(targets))
        if unknown_shared:
            raise ValueError(
                f"PARTITION_SHARED_SINK_NOT_TARGET:{packet_id}:" + ",".join(unknown_shared)
            )
        dependencies = self._normalize_ids(raw.get("dependencies"), "dependency packet_id")
        integration_order = int(raw.get("integration_order", 0))
        if integration_order < 0:
            raise ValueError(f"PARTITION_INTEGRATION_ORDER_NEGATIVE:{packet_id}")
        merge_strategy = str(raw.get("merge_strategy") or "").strip()
        if not merge_strategy:
            raise ValueError(f"PARTITION_MERGE_STRATEGY_REQUIRED:{packet_id}")
        verification = _names(raw.get("verification_requirements"))
        handoff_conditions = _names(raw.get("handoff_conditions"))
        if not verification:
            raise ValueError(f"PARTITION_VERIFICATION_REQUIRED:{packet_id}")
        if not handoff_conditions:
            raise ValueError(f"PARTITION_HANDOFF_CONDITION_REQUIRED:{packet_id}")
        assignee_hint = str(raw.get("assignee_hint") or "").strip() or None
        if assignee_hint is not None:
            assignee_hint = _require_id(assignee_hint, "assignee_hint")
        row = {
            "packet_id": packet_id,
            "work_key": work_key,
            "targets": targets,
            "dependencies": dependencies,
            "shared_sinks": shared_sinks,
            "integration_order": integration_order,
            "merge_strategy": merge_strategy,
            "exact_refs": _names(raw.get("exact_refs")),
            "verification_requirements": verification,
            "handoff_conditions": handoff_conditions,
            "acceptance_criteria": _names(raw.get("acceptance_criteria")),
            "assignee_hint": assignee_hint,
        }
        row["packet_digest"] = _digest(row)
        return row

    def _partition_by_id(self, board, partition_id: str) -> Optional[Dict[str, Any]]:
        for event in self._cohesion_events(board, PARTITION_EVENT):
            payload = self._payload(event)
            if str(payload.get("partition_id") or "") == partition_id:
                return {"event": event, "payload": payload}
        return None

    @staticmethod
    def _topological_layers(
        node_ids: Iterable[str], edges: Iterable[Tuple[str, str]]
    ) -> Optional[List[List[str]]]:
        nodes = sorted(set(node_ids))
        adjacency = {node: set() for node in nodes}
        indegree = {node: 0 for node in nodes}
        for src, dst in sorted(set(edges)):
            if src not in adjacency or dst not in adjacency:
                return None
            if dst in adjacency[src]:
                continue
            adjacency[src].add(dst)
            indegree[dst] += 1
        layers: List[List[str]] = []
        remaining = set(nodes)
        while remaining:
            ready = sorted(node for node in remaining if indegree[node] == 0)
            if not ready:
                return None
            layers.append(ready)
            for node in ready:
                remaining.remove(node)
                for dst in adjacency[node]:
                    indegree[dst] -= 1
        return layers

    def _validate_party_context(
        self,
        board,
        party_id: Optional[str],
        actors: Iterable[str],
        goal_refs: Optional[Iterable[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not party_id:
            return None
        party_id = _require_id(str(party_id), "party_id")
        runtime = PartyCoordinationRuntimeV2(self.server)
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

    def partition(
        self,
        partition_id: str,
        proposer_id: str,
        goal_ref: str,
        packets: Iterable[Dict[str, Any]],
        party_id: Optional[str] = None,
        quest_ref: Optional[str] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        partition_id = _require_id(partition_id, "partition_id")
        proposer_id = _require_id(proposer_id, "proposer_id")
        goal_ref = str(goal_ref or "").strip()
        if not goal_ref:
            raise ValueError("PARTITION_GOAL_REF_REQUIRED")
        packet_rows = [self._normalize_packet(dict(raw)) for raw in packets]
        if len(packet_rows) < 2:
            raise ValueError("PARTITION_REQUIRES_AT_LEAST_TWO_PACKETS")
        packet_rows.sort(key=lambda row: row["packet_id"])
        semantic_basis = {
            "partition_id": partition_id,
            "proposer_id": proposer_id,
            "goal_ref": goal_ref,
            "packets": packet_rows,
            "party_id": str(party_id).strip() if party_id else None,
            "quest_ref": str(quest_ref).strip() if quest_ref else None,
        }
        request_digest = _digest(semantic_basis)
        board = self._board()

        def build(base):
            existing = self._partition_by_id(board, partition_id)
            if existing:
                old = existing["payload"]
                if old.get("request_digest") != request_digest:
                    raise ValueError(f"COHESION_PARTITION_ID_CONFLICT:{partition_id}")
                return {
                    "return": {
                        "status": "COHESION_PARTITION_ALREADY_PROPOSED",
                        "partition": old,
                        "event": existing["event"],
                        "idempotent": True,
                        "assignment_authority": False,
                        "claim_authority": False,
                    }
                }

            active = self._active_map(board)
            if proposer_id not in active:
                return {
                    "return": {
                        "status": "COHESION_PARTITION_PROPOSER_NOT_PRESENT_HOLD",
                        "partition_id": partition_id,
                        "assignment_authority": False,
                    }
                }
            self._validate_party_context(board, party_id, [proposer_id], [goal_ref] if party_id else None)

            errors: List[str] = []
            packet_map = {row["packet_id"]: row for row in packet_rows}
            if len(packet_map) != len(packet_rows):
                errors.append("DUPLICATE_PACKET_ID")

            by_work_key: Dict[str, List[str]] = {}
            for row in packet_rows:
                by_work_key.setdefault(row["work_key"], []).append(row["packet_id"])
            for work_key, ids in sorted(by_work_key.items()):
                if len(ids) > 1:
                    errors.append("DUPLICATE_WORK_KEY:" + work_key + ":" + ",".join(sorted(ids)))

            dependency_edges: List[Dict[str, Any]] = []
            edge_pairs: List[Tuple[str, str]] = []
            for row in packet_rows:
                for dependency in row["dependencies"]:
                    if dependency == row["packet_id"]:
                        errors.append(f"SELF_DEPENDENCY:{row['packet_id']}")
                        continue
                    if dependency not in packet_map:
                        errors.append(f"UNKNOWN_DEPENDENCY:{row['packet_id']}:{dependency}")
                        continue
                    dependency_edges.append({"from": dependency, "to": row["packet_id"]})
                    edge_pairs.append((dependency, row["packet_id"]))

            serialization_edges: List[Dict[str, Any]] = []
            for index, left in enumerate(packet_rows):
                left_targets = set(left["targets"])
                left_sinks = set(left["shared_sinks"])
                for right in packet_rows[index + 1 :]:
                    overlap = sorted(left_targets & set(right["targets"]))
                    if not overlap:
                        continue
                    declared_shared = sorted(set(overlap) & left_sinks & set(right["shared_sinks"]))
                    unsafe = sorted(set(overlap) - set(declared_shared))
                    if unsafe:
                        errors.append(
                            f"OWNED_TARGET_COLLISION:{left['packet_id']}:{right['packet_id']}:"
                            + ",".join(unsafe)
                        )
                    if declared_shared:
                        if left["integration_order"] == right["integration_order"]:
                            errors.append(
                                f"SHARED_SINK_ORDER_REQUIRED:{left['packet_id']}:{right['packet_id']}:"
                                + ",".join(declared_shared)
                            )
                        else:
                            first, second = (
                                (left, right)
                                if left["integration_order"] < right["integration_order"]
                                else (right, left)
                            )
                            serialization_edges.append(
                                {
                                    "from": first["packet_id"],
                                    "to": second["packet_id"],
                                    "shared_sinks": declared_shared,
                                    "law": "SHARED_SINK => SERIALIZE_UNLESS_PROVEN_DISJOINT",
                                }
                            )
                            edge_pairs.append((first["packet_id"], second["packet_id"]))

            layers = self._topological_layers(packet_map, edge_pairs)
            if layers is None:
                errors.append("PARTITION_DEPENDENCY_OR_SERIALIZATION_CYCLE")

            if errors:
                return {
                    "return": {
                        "status": "COHESION_PARTITION_HOLD",
                        "partition_id": partition_id,
                        "errors": sorted(set(errors)),
                        "assignment_authority": False,
                        "claim_authority": False,
                        "execution_authority": False,
                        "law": "INVALID_OR_AMBIGUOUS_PARTITION != PARALLEL_EXECUTION_AUTHORITY",
                    }
                }

            proof_basis = {
                "packet_ids": sorted(packet_map),
                "work_keys": sorted(row["work_key"] for row in packet_rows),
                "dependency_edges": sorted(dependency_edges, key=lambda row: (row["from"], row["to"])),
                "serialization_edges": sorted(
                    serialization_edges, key=lambda row: (row["from"], row["to"], row["shared_sinks"])
                ),
                "parallel_groups": layers,
                "unsafe_target_collisions": [],
                "all_work_keys_unique": True,
                "acyclic": True,
            }
            partition = {
                "cohesion_version": COHESION_VERSION,
                "cohesion_artifact": PARTITION_ARTIFACT,
                "partition_handoff_version": PARTITION_HANDOFF_VERSION,
                **semantic_basis,
                "request_digest": request_digest,
                "proof": proof_basis,
                "partition_proof_digest": _digest(proof_basis),
                "proposed_from_git_head": base,
                "proposed_at": _iso(),
                "assignment_authority": False,
                "claim_authority": False,
                "scheduler_authority": False,
                "execution_authority": False,
                "law": "PARTITION_PROPOSAL != ASSIGNMENT; PARALLEL_GROUPS_ARE_PROOF_SCOPED_ONLY",
            }
            event_rel, event = board._event(PARTITION_EVENT, proposer_id, partition)
            return {
                "files": {event_rel: _json_text(event)},
                "message": f"cohesion partition {partition_id}",
                "result": {
                    "status": "COHESION_PARTITION_PROPOSED",
                    "partition": partition,
                    "event": event,
                    "idempotent": False,
                    "assignment_authority": False,
                    "claim_authority": False,
                },
            }

        return board._mutate(agent_id=proposer_id, remote=remote, build_files=build)

    @staticmethod
    def _decode_handoff(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("kind") != "MESSAGE":
            return None
        raw = (event.get("payload") or {}).get("message")
        if not isinstance(raw, str):
            return None
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(packet, dict) or packet.get("artifact") != HANDOFF_ARTIFACT:
            return None
        return packet

    def _handoff_by_id(self, board, handoff_id: str) -> Optional[Dict[str, Any]]:
        for event in board._events():
            packet = self._decode_handoff(event)
            if packet and str(packet.get("handoff_id") or "") == handoff_id:
                return {"event": event, "packet": packet}
        return None

    @staticmethod
    def _event_time(event: Optional[Dict[str, Any]]):
        if not event:
            return None
        return _parse_time(str(event.get("created_at") or ""))

    def _handoff_state(self, board, event: Dict[str, Any], packet: Dict[str, Any]) -> Dict[str, Any]:
        message_id = str(event.get("event_id") or "")
        receiver = str(packet.get("receiver") or "")
        sender = str(packet.get("sender") or "")
        sender_claim_id = str(packet.get("sender_claim_id") or "")
        route_time = self._event_time(event)
        ack_events = [
            row
            for row in board._events()
            if row.get("kind") == "ACK"
            and str(row.get("agent_id") or "") == receiver
            and str((row.get("payload") or {}).get("message_id") or "") == message_id
        ]
        ack_events.sort(key=lambda row: str(row.get("created_at") or ""))
        ack_event = ack_events[0] if ack_events else None
        ack_time = self._event_time(ack_event)

        release_events = []
        for row in board._events():
            if row.get("kind") not in {"RELEASE", "HANDOFF"}:
                continue
            if str(row.get("agent_id") or "") != sender:
                continue
            if str((row.get("payload") or {}).get("claim_id") or "") != sender_claim_id:
                continue
            row_time = self._event_time(row)
            if route_time is None or row_time is None or row_time >= route_time:
                release_events.append(row)
        release_events.sort(key=lambda row: str(row.get("created_at") or ""))
        release_event = release_events[0] if release_events else None
        release_time = self._event_time(release_event)

        receipt_required = packet.get("required_receipt") == "MESSAGE_ACK"
        acknowledged = ack_event is not None
        early_release = bool(
            receipt_required
            and release_event is not None
            and (ack_time is None or release_time is None or release_time < ack_time)
        )
        active = self._active_map(board)
        sender_presence = active.get(sender)
        claim_still_active = bool(
            sender_presence and str(sender_presence.get("claim_id") or "") == sender_claim_id
        )
        claim_release_allowed = bool(not receipt_required or acknowledged)
        if early_release:
            status = "COHESION_HANDOFF_EARLY_RELEASE_OBSERVED"
        elif acknowledged:
            status = "COHESION_HANDOFF_ACKNOWLEDGED"
        else:
            status = "COHESION_HANDOFF_AWAITING_RECEIPT"
        return {
            "status": status,
            "handoff_id": packet.get("handoff_id"),
            "message_id": message_id,
            "sender": sender,
            "receiver": receiver,
            "sender_claim_id": sender_claim_id,
            "required_receipt": packet.get("required_receipt"),
            "receiver_acknowledged": acknowledged,
            "ack_event_id": ack_event.get("event_id") if ack_event else None,
            "claim_release_allowed": claim_release_allowed,
            "claim_release_performed": False,
            "claim_still_active": claim_still_active,
            "early_release_observed": early_release,
            "release_event_id": release_event.get("event_id") if release_event else None,
            "execution_authority": False,
            "claim_authority": False,
            "law": (
                "HANDOFF_ROUTE != CONSUMPTION; ACK_CONTROLS_COHESION_RELEASE_READINESS_ONLY; "
                "COHESION_NEVER_RELEASES_MESSAGE_BOARD_CLAIMS"
            ),
        }

    def handoff(
        self,
        handoff_id: str,
        sender: str,
        receiver: str,
        exact_refs: Iterable[str],
        completed_delta: str,
        residual: str,
        invariants: Iterable[str],
        tests: Iterable[str],
        blockers: Iterable[str],
        next_edge: str,
        required_receipt: str,
        partition_id: Optional[str] = None,
        packet_id: Optional[str] = None,
        work_key: Optional[str] = None,
        party_id: Optional[str] = None,
        goal_refs: Optional[Iterable[str]] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        handoff_id = _require_id(handoff_id, "handoff_id")
        sender = _require_id(sender, "sender")
        receiver = _require_id(receiver, "receiver")
        if sender == receiver:
            raise ValueError("COHESION_HANDOFF_SELF_ROUTE_HOLD")
        refs = _names(exact_refs)
        if not refs:
            raise ValueError("COHESION_HANDOFF_EXACT_REF_REQUIRED")
        completed_delta = str(completed_delta or "").strip()
        residual = str(residual or "").strip()
        next_edge = str(next_edge or "").strip()
        invariant_rows = _names(invariants)
        test_rows = _names(tests)
        if not completed_delta or not residual or not next_edge or not invariant_rows or not test_rows:
            raise ValueError("COHESION_HANDOFF_REQUIRED_FIELD_EMPTY")
        required_receipt = str(required_receipt or "").upper()
        if required_receipt not in {"MESSAGE_ACK", "NONE"}:
            raise ValueError("COHESION_HANDOFF_RECEIPT_INVALID")
        if bool(partition_id) != bool(packet_id):
            raise ValueError("COHESION_HANDOFF_PARTITION_AND_PACKET_REQUIRED_TOGETHER")
        goals = _names(goal_refs)
        semantic_basis = {
            "handoff_id": handoff_id,
            "sender": sender,
            "receiver": receiver,
            "exact_refs": refs,
            "completed_delta": completed_delta,
            "residual": residual,
            "invariants": invariant_rows,
            "tests": test_rows,
            "blockers": _names(blockers),
            "next_edge": next_edge,
            "required_receipt": required_receipt,
            "partition_id": str(partition_id).strip() if partition_id else None,
            "packet_id": str(packet_id).strip() if packet_id else None,
            "work_key": str(work_key).strip() if work_key else None,
            "party_id": str(party_id).strip() if party_id else None,
            "goal_refs": goals,
        }
        request_digest = _digest(semantic_basis)
        board = self._board()
        snapshot = board.read(
            agent_id=sender,
            limit=500,
            include_stale=True,
            remote=remote,
            shared_remote_mode="REQUIRED",
        )
        if snapshot.get("status") != "OK" or not snapshot.get("shared_frontier_verified"):
            return {
                "status": "COHESION_HANDOFF_SHARED_FRONTIER_HOLD",
                "handoff_id": handoff_id,
                "durable_return": False,
                "claim_authority": False,
            }

        existing = self._handoff_by_id(board, handoff_id)
        if existing:
            packet = existing["packet"]
            if packet.get("request_digest") != request_digest:
                raise ValueError(f"COHESION_HANDOFF_ID_CONFLICT:{handoff_id}")
            value = self._handoff_state(board, existing["event"], packet)
            value["handoff"] = packet
            value["idempotent"] = True
            value["durable_return"] = True
            return value

        active = {str(row.get("agent_id")): row for row in snapshot.get("active") or []}
        sender_presence = active.get(sender)
        receiver_presence = active.get(receiver)
        if not sender_presence:
            return {
                "status": "COHESION_HANDOFF_SENDER_NOT_ACTIVE_HOLD",
                "handoff_id": handoff_id,
                "claim_authority": False,
            }
        if not receiver_presence:
            return {
                "status": "COHESION_HANDOFF_RECEIVER_NOT_ACTIVE_HOLD",
                "handoff_id": handoff_id,
                "claim_authority": False,
            }

        self._validate_party_context(board, party_id, [sender, receiver], goals if party_id else None)

        partition_packet = None
        if partition_id:
            partition_id = _require_id(str(partition_id), "partition_id")
            packet_id = _require_id(str(packet_id), "packet_id")
            partition_row = self._partition_by_id(board, partition_id)
            if not partition_row:
                raise ValueError(f"COHESION_HANDOFF_PARTITION_NOT_FOUND:{partition_id}")
            partition_packet = next(
                (
                    row
                    for row in (partition_row["payload"].get("packets") or [])
                    if str(row.get("packet_id") or "") == packet_id
                ),
                None,
            )
            if not partition_packet:
                raise ValueError(f"COHESION_HANDOFF_PACKET_NOT_FOUND:{partition_id}:{packet_id}")
            if work_key and str(partition_packet.get("work_key") or "") != str(work_key):
                raise ValueError("COHESION_HANDOFF_WORK_KEY_MISMATCH")
            missing_refs = sorted(set(partition_packet.get("exact_refs") or []) - set(refs))
            if missing_refs:
                raise ValueError("COHESION_HANDOFF_MISSING_PARTITION_REFS:" + ",".join(missing_refs))

        packet = {
            "artifact": HANDOFF_ARTIFACT,
            "version": PARTITION_HANDOFF_VERSION,
            "cohesion_version": COHESION_VERSION,
            **semantic_basis,
            "request_digest": request_digest,
            "sender_claim_id": sender_presence.get("claim_id"),
            "sender_claim_work_key": sender_presence.get("work_key"),
            "receiver_claim_id": receiver_presence.get("claim_id"),
            "partition_packet_digest": partition_packet.get("packet_digest") if partition_packet else None,
            "routed_from_git_head": snapshot.get("git_head"),
            "routed_at": _iso(),
            "claim_release_authority": False,
            "execution_authority": False,
            "law": (
                "HANDOFF_ROUTE != CONSUMPTION; REQUIRED_ACK_PRECEDES_COHESION_RELEASE_READINESS; "
                "COHESION_DOES_NOT_RELEASE_CLAIMS"
            ),
        }
        posted = board.post(
            agent_id=sender,
            message=json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            message_kind="HANDOFF",
            recipients=[receiver],
            remote=remote,
        )
        event = posted.get("message_event")
        if not isinstance(event, dict):
            return {
                **posted,
                "status": "COHESION_HANDOFF_ROUTE_HOLD",
                "handoff_id": handoff_id,
                "claim_authority": False,
            }
        value = self._handoff_state(board, event, packet)
        value["handoff"] = packet
        value["idempotent"] = False
        value["durable_return"] = bool(posted.get("durable_return"))
        value["message_board"] = posted
        return value

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        tools = list(value.get("tools") or [])
        for name in ["athena_cohesion_partition", "athena_cohesion_handoff"]:
            if name not in tools:
                tools.append(name)
        value["tools"] = tools
        value["partition_handoff"] = {
            "version": PARTITION_HANDOFF_VERSION,
            "partition": {
                "input": "explicit caller-supplied packets",
                "parallelism": "unique work keys + disjoint owned targets + acyclic dependency/serialization graph",
                "shared_sink": "must be declared by both packets and serialized by distinct integration order",
                "authority": "advisory proof only",
            },
            "handoff": {
                "transport": "Message Board V1 HANDOFF message",
                "consumption": "addressed receiver Message Board ACK",
                "release": "readiness projection only; no claim mutation",
                "early_release": "observed from Message Board RELEASE/HANDOFF chronology",
            },
        }
        value["laws"] = list(value.get("laws") or []) + [
            "PARTITION_PROPOSAL != ASSIGNMENT",
            "SHARED_SINK => SERIALIZE_UNLESS_PROVEN_DISJOINT",
            "HANDOFF_ROUTE != CONSUMPTION",
            "ACK != OUTCOME_PROOF",
            "COHESION_RELEASE_READINESS != MESSAGE_BOARD_CLAIM_RELEASE",
        ]
        residual = [
            item
            for item in (value.get("residual") or [])
            if "partition/handoff" not in str(item).lower() and "tools 8-9" not in str(item).lower()
        ]
        value["residual"] = residual
        return value
