from __future__ import annotations

import copy
import json
import time
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from .nexus4d_types import (
    VERSION, SCHEMA, RESOURCE_URI, PRESSURE_CHANNELS, EVIDENCE_DIMENSIONS,
    LIFECYCLE, EVENT_TYPES, _DB_SCHEMA, _canonical, _clean_id, _digest,
    normalize_spec,
)
from .nexus4d_planner import _new_snapshot, _terminal, derive, plan_snapshot
from .nexus4d_events import _apply_event, _snapshot_digest
from .nexus4d_planner import _validate_event_envelope

class Nexus4dRuntime:
    """Durable NEXUS-4D control-plane runtime over the canonical Store connection."""

    def __init__(self, store, authority_ledger=None):
        self.store = store
        self.authority_ledger = authority_ledger
        with self.store.db:
            self.store.db.executescript(_DB_SCHEMA)

    def _authority_snapshot_for_requirements(self, requirements: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        claim_ids = {item["claim_id"] for item in requirements}
        result: Dict[str, Dict[str, Any]] = {}
        for claim_id in sorted(claim_ids):
            state = self.authority_ledger.state(claim_id) if self.authority_ledger is not None else None
            if state:
                result[claim_id] = {
                    "claim_id": claim_id,
                    "y": state.get("y"),
                    "status": state.get("status"),
                    "last_eid": state.get("last_eid"),
                    "canonical_ref": state.get("canonical_ref"),
                    "source_ref": state.get("source_ref"),
                }
        return result

    def _authority_requirements(self, spec: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        requirements: List[Mapping[str, Any]] = [
            item
            for node in spec["nodes"]
            for item in node.get("required_authority_claims", [])
        ]
        requirements.extend(spec.get("topology_authority_claims", []))
        return requirements

    def _authority_snapshot(self, spec: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        return self._authority_snapshot_for_requirements(self._authority_requirements(spec))

    def _event_authority_snapshot(
        self,
        spec: Mapping[str, Any],
        snapshot: Mapping[str, Any],
        event_type: str,
        payload: Mapping[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        requirements = list(self._authority_requirements(spec))
        if event_type in {"TOPOLOGY_PROMOTED", "TOPOLOGY_ROLLED_BACK"}:
            change_id = payload.get("change_id")
            record = (snapshot.get("topology_candidates") or {}).get(change_id) if change_id else None
            if record:
                counterpart_key = "replacement_spec" if event_type == "TOPOLOGY_PROMOTED" else "base_spec"
                counterpart = record.get(counterpart_key) or {}
                requirements.extend(counterpart.get("topology_authority_claims", []))
        return self._authority_snapshot_for_requirements(requirements)

    def _row(self, machine_id: str) -> Dict[str, Any]:
        row = self.store.one("SELECT * FROM nexus4d_machines WHERE machine_id=?", (machine_id,))
        if not row:
            raise KeyError(f"unknown NEXUS machine {machine_id}")
        return row

    def _load(self, machine_id: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        row = self._row(machine_id)
        return row, json.loads(row["spec_json"]), json.loads(row["snapshot_json"])

    def compile(self, spec: Mapping[str, Any], machine_id: str | None = None, actor: str = "agent") -> Dict[str, Any]:
        normalized = normalize_spec(spec)
        spec_digest = _digest("NXSPEC", normalized)
        resolved_id = _clean_id(machine_id, "machine_id") if machine_id else _digest("NXM", normalized)
        existing = self.store.one("SELECT * FROM nexus4d_machines WHERE machine_id=?", (resolved_id,))
        if existing:
            existing_spec = json.loads(existing["spec_json"])
            if _canonical(existing_spec) != _canonical(normalized):
                raise ValueError("machine_id already exists with a different specification")
            result = self.state(resolved_id)
            result["idempotent_reuse"] = True
            return result
        snapshot = _new_snapshot(normalized)
        authority_states = self._authority_snapshot(normalized)
        derived = derive(normalized, snapshot, authority_states)
        terminal = _terminal(normalized, snapshot, derived)
        snapshot_digest = _snapshot_digest(snapshot)
        now = time.time()
        with self.store._lock, self.store.db:
            self.store.db.execute(
                "INSERT INTO nexus4d_machines VALUES(?,?,?,?,?,?,?,?,?)",
                (resolved_id, SCHEMA, 0, _canonical(normalized), _canonical(normalized), _canonical(snapshot), snapshot_digest, now, now),
            )
        return {
            "version": VERSION,
            "status": "COMPILED",
            "machine_id": resolved_id,
            "revision": 0,
            "spec_digest": spec_digest,
            "snapshot_digest": snapshot_digest,
            "terminal": terminal,
            "plan": plan_snapshot(normalized, snapshot, authority_states=authority_states),
            "idempotent_reuse": False,
            "authority": "CONTROL_PLANE_ONLY",
            "execution_authority": False,
            "promotion_authority": False,
            "actor": actor,
        }

    def state(self, machine_id: str) -> Dict[str, Any]:
        row, spec, snapshot = self._load(machine_id)
        authority_states = self._authority_snapshot(spec)
        derived = derive(spec, snapshot, authority_states)
        terminal = _terminal(spec, snapshot, derived)
        return {
            "version": VERSION,
            "status": terminal["status"],
            "machine_id": machine_id,
            "revision": int(row["revision"]),
            "topology_epoch": snapshot["topology_epoch"],
            "spec_digest": _digest("NXSPEC", spec),
            "snapshot_digest": row["snapshot_digest"],
            "snapshot": snapshot,
            "authority_observations": authority_states,
            "derived": derived,
            "terminal": terminal,
            "authority": "CONTROL_PLANE_ONLY",
            "execution_authority": False,
            "promotion_authority": False,
        }

    def plan(self, machine_id: str, expected_revision: int | None = None, max_nodes: int | None = None, max_cost: float | None = None) -> Dict[str, Any]:
        row, spec, snapshot = self._load(machine_id)
        revision = int(row["revision"])
        if expected_revision is not None and int(expected_revision) != revision:
            raise ValueError(f"STALE_NEXUS_REVISION expected={expected_revision} current={revision}")
        authority_states = self._authority_snapshot(spec)
        result = plan_snapshot(spec, snapshot, max_nodes=max_nodes, max_cost=max_cost, authority_states=authority_states)
        result.update({"version": VERSION, "machine_id": machine_id, "snapshot_digest": row["snapshot_digest"], "execution_authority": False})
        return result

    def advance(self, machine_id: str, expected_revision: int, events: Sequence[Mapping[str, Any]], actor: str = "agent") -> Dict[str, Any]:
        if not isinstance(events, Sequence) or isinstance(events, (str, bytes)) or not events:
            raise ValueError("events must be a non-empty array")
        with self.store._lock:
            row, spec, snapshot = self._load(machine_id)
            current_revision = int(row["revision"])
            if int(expected_revision) != current_revision:
                raise ValueError(f"STALE_NEXUS_REVISION expected={expected_revision} current={current_revision}")
            working = copy.deepcopy(snapshot)
            prepared = []
            next_seq = current_revision
            seen_idempotency: Dict[str, str] = {}
            batch_event_ids: set[str] = set()
            batch_idempotency: set[str] = set()
            for raw in events:
                event_type, payload, supplied_event_id, idempotency_key = _validate_event_envelope(raw)
                payload.pop("_authority_receipts", None)
                if event_type in {"CLAIMED", "COMMITTED", "TOPOLOGY_PROMOTED", "TOPOLOGY_ROLLED_BACK"}:
                    payload["_authority_receipts"] = self._event_authority_snapshot(spec, working, event_type, payload)
                if supplied_event_id:
                    if supplied_event_id in batch_event_ids:
                        raise ValueError("duplicate event_id in batch")
                    existing_event = self.store.one("SELECT * FROM nexus4d_events WHERE machine_id=? AND event_id=?", (machine_id, supplied_event_id))
                    if existing_event:
                        raise ValueError("event_id already exists")
                    batch_event_ids.add(supplied_event_id)
                if idempotency_key:
                    if idempotency_key in batch_idempotency:
                        raise ValueError("duplicate idempotency_key in batch")
                    batch_idempotency.add(idempotency_key)
                    existing = self.store.one("SELECT * FROM nexus4d_events WHERE machine_id=? AND idempotency_key=?", (machine_id, idempotency_key))
                    if existing:
                        incoming_basis = {"machine_id": machine_id, "type": event_type, "payload": payload, "actor": actor, "idempotency_key": idempotency_key}
                        incoming_digest = _digest("NXEVENT", incoming_basis)
                        if incoming_digest != existing["event_digest"]:
                            raise ValueError("idempotency key already exists with different event content")
                        seen_idempotency[idempotency_key] = existing["event_id"]
                        continue
                next_seq += 1
                basis = {"machine_id": machine_id, "seq": next_seq, "type": event_type, "payload": payload, "actor": actor, "idempotency_key": idempotency_key}
                event_id = supplied_event_id or _digest("NXE", basis)
                event_digest = _digest("NXEVENT", {"machine_id": machine_id, "type": event_type, "payload": payload, "actor": actor, "idempotency_key": idempotency_key})
                _apply_event(spec, working, event_type, payload, next_seq, payload.get("_authority_receipts") or self._authority_snapshot(spec))
                working["revision"] = next_seq
                working["last_event_id"] = event_id
                prepared.append((next_seq, event_id, idempotency_key, event_type, payload, event_digest))
            if not prepared:
                result = self.state(machine_id)
                result["status"] = "IDEMPOTENT_REPLAY"
                result["idempotent_events"] = seen_idempotency
                return result
            authority_states = self._authority_snapshot(spec)
            derived = derive(spec, working, authority_states)
            terminal = _terminal(spec, working, derived)
            snapshot_digest = _snapshot_digest(working)
            now = time.time()
            with self.store.db:
                fresh = self.store.one("SELECT revision FROM nexus4d_machines WHERE machine_id=?", (machine_id,))
                if not fresh or int(fresh["revision"]) != current_revision:
                    raise ValueError("STALE_NEXUS_REVISION concurrent update detected")
                for seq, event_id, idempotency_key, event_type, payload, event_digest in prepared:
                    self.store.db.execute(
                        "INSERT INTO nexus4d_events VALUES(?,?,?,?,?,?,?,?,?)",
                        (machine_id, seq, event_id, idempotency_key, event_type, actor, _canonical(payload), event_digest, now),
                    )
                self.store.db.execute(
                    "UPDATE nexus4d_machines SET revision=?,spec_json=?,snapshot_json=?,snapshot_digest=?,updated_at=? WHERE machine_id=? AND revision=?",
                    (next_seq, _canonical(spec), _canonical(working), snapshot_digest, now, machine_id, current_revision),
                )
            return {
                "version": VERSION,
                "status": terminal["status"],
                "machine_id": machine_id,
                "previous_revision": current_revision,
                "revision": next_seq,
                "applied_event_ids": [item[1] for item in prepared],
                "idempotent_events": seen_idempotency,
                "snapshot_digest": snapshot_digest,
                "terminal": terminal,
                "plan": plan_snapshot(spec, working, authority_states=authority_states),
                "authority": "CONTROL_PLANE_ONLY",
                "execution_authority": False,
                "promotion_authority": False,
            }

    def replay(self, machine_id: str) -> Dict[str, Any]:
        row, active_spec, current = self._load(machine_id)
        spec = json.loads(row["genesis_spec_json"])
        replayed = _new_snapshot(spec)
        events = self.store.rows("SELECT * FROM nexus4d_events WHERE machine_id=? ORDER BY seq", (machine_id,))
        expected_seq = 1
        for event in events:
            if int(event["seq"]) != expected_seq:
                return {"version": VERSION, "status": "REPLAY_FAIL", "machine_id": machine_id, "reason": "NON_CONTIGUOUS_EVENT_SEQUENCE", "expected_seq": expected_seq, "observed_seq": event["seq"]}
            payload = json.loads(event["payload_json"])
            recomputed = _digest("NXEVENT", {"machine_id": machine_id, "type": event["event_type"], "payload": payload, "actor": event["actor"], "idempotency_key": event["idempotency_key"]})
            if recomputed != event["event_digest"]:
                return {"version": VERSION, "status": "REPLAY_FAIL", "machine_id": machine_id, "reason": "EVENT_DIGEST_MISMATCH", "seq": expected_seq}
            _apply_event(spec, replayed, event["event_type"], payload, expected_seq, payload.get("_authority_receipts") or {})
            replayed["revision"] = expected_seq
            replayed["last_event_id"] = event["event_id"]
            expected_seq += 1
        replay_digest = _snapshot_digest(replayed)
        stored_digest = row["snapshot_digest"]
        spec_match = _canonical(spec) == _canonical(active_spec)
        match = replay_digest == stored_digest and _canonical(replayed) == _canonical(current) and spec_match
        return {
            "version": VERSION,
            "status": "REPLAY_MATCH" if match else "REPLAY_FAIL",
            "machine_id": machine_id,
            "revision": int(row["revision"]),
            "event_count": len(events),
            "stored_snapshot_digest": stored_digest,
            "replayed_snapshot_digest": replay_digest,
            "match": match,
            "active_spec_match": spec_match,
            "active_spec_digest": _digest("NXSPEC", active_spec),
            "replayed_spec_digest": _digest("NXSPEC", spec),
            "authority": "INTEGRITY_ONLY",
            "truth_authority": False,
            "causal_authority": False,
        }

    def terminal(self, machine_id: str) -> Dict[str, Any]:
        row, spec, snapshot = self._load(machine_id)
        authority_states = self._authority_snapshot(spec)
        return {"version": VERSION, "machine_id": machine_id, **_terminal(spec, snapshot, derive(spec, snapshot, authority_states)), "snapshot_digest": row["snapshot_digest"], "authority_observations": authority_states}

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        limit = int(limit)
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be in [1,1000]")
        rows = self.store.rows("SELECT machine_id,revision,snapshot_digest,created_at,updated_at FROM nexus4d_machines ORDER BY updated_at DESC LIMIT ?", (limit,))
        for row in rows:
            row["terminal"] = self.terminal(row["machine_id"])
        return rows

    def benchmark(self) -> Dict[str, Any]:
        machines = self.store.one("SELECT COUNT(*) AS n FROM nexus4d_machines")["n"]
        events = self.store.one("SELECT COUNT(*) AS n FROM nexus4d_events")["n"]
        open_obligations = 0
        actionable = 0
        terminal = 0
        for row in self.store.rows("SELECT spec_json,snapshot_json FROM nexus4d_machines"):
            spec = json.loads(row["spec_json"])
            snapshot = json.loads(row["snapshot_json"])
            derived = derive(spec, snapshot, self._authority_snapshot(spec))
            open_obligations += sum(1 for item in derived["obligations"] if item["status"] != "CLOSED")
            actionable += sum(1 for item in derived["readiness"].values() if item["ready"])
            terminal += int(_terminal(spec, snapshot, derived)["terminal"])
        return {
            "nexus4d_version": VERSION,
            "nexus4d_machines": int(machines),
            "nexus4d_events": int(events),
            "nexus4d_open_obligations": int(open_obligations),
            "nexus4d_actionable_nodes": int(actionable),
            "nexus4d_terminal_machines": int(terminal),
        }

    def describe(self) -> Dict[str, Any]:
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "resource": RESOURCE_URI,
            "pressure_channels": list(PRESSURE_CHANNELS),
            "evidence_dimensions": list(EVIDENCE_DIMENSIONS),
            "lifecycle": list(LIFECYCLE),
            "event_types": sorted(EVENT_TYPES),
            "benchmark": self.benchmark(),
            "laws": [
                "PRESSURE_IS_DERIVED_NOT_SELF_REPORTED",
                "PRESSURE_DOES_NOT_GRANT_AUTHORITY",
                "STATE_AND_EVIDENCE_MOVE_FORWARD",
                "OBLIGATION_AND_REPAIR_DEMAND_MOVE_BACKWARD",
                "UNKNOWN_IS_A_LIVE_RESIDUAL_NOT_ZERO",
                "CANDIDATE_NE_VERIFIED_NE_COMMITTED_NE_CONSUMED_NE_OBSERVED",
                "PRODUCERS_CANNOT_SELF_CLOSE_ROOT_GOALS",
                "TOPOLOGY_PROMOTION_REQUIRES_POSITIVE_OBSERVED_GAIN_ZERO_INVARIANT_REGRESSIONS_AND_ROLLBACK",
            ],
            "authority": {
                "execution": False,
                "promotion": False,
                "merge": False,
                "external_action": False,
                "scope": "durable control-plane planning, obligation accounting, lifecycle admission and replay",
            },
        }
