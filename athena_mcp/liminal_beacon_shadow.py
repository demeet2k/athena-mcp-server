from __future__ import annotations

"""Reversible no-injection operational observer for Liminal Beacon V1.1.

The observer owns an isolated process-local Beacon carrier. For each observed MCP
crossing it executes the *installed* V1.1 autohook on a disposable projection,
then copies back producer-side shadow state only. Projection PRESENTED receipts
and cursors are translated into a separate WOULD_PRESENT ledger and are never
copied into the source shadow carrier or the live/manual Beacon carrier.

Nothing in this module grants delivery, cognition, evidence, truth, assignment,
Git, deployment, or canonical authority.
"""

import copy
import hashlib
import json
import threading
import time
from collections import Counter, defaultdict, deque
from typing import Any

from .liminal_beacon_mesh import LiminalBeaconMeshRuntime

VERSION = "LIMINAL.BEACON.SHADOW.1"
ARTIFACT = "ATHENA.LIMINAL.BEACON.SHADOW.V1.CANDIDATE"
PARENT_INTEGRATION = "df74f7388cdb43c36cfdeeff684724b73fdfc117"
PARENT_MASTER = "d8bb4cc6e2e6861eeb7141dc52a2efcea252ff36"

LAWS = [
    "SHADOW != DELIVERY",
    "SHADOW != PRESENTED",
    "WOULD_PRESENT != PRESENTED",
    "SHADOW != CONSUMED",
    "SHADOW != INCORPORATED",
    "SHADOW != AUTHORITY",
    "SHADOW != EVIDENCE",
    "SHADOW_PACKET != DOMAIN_OUTPUT",
    "SHADOW_CARRIER != LIVE_BEACON_CARRIER",
    "SHADOW_STATE != HIDDEN_PROCESS_PROOF",
    "SHADOW_PASS != DEFAULT_ACTIVATION",
    "SHADOW_PASS != CANONICAL_PROMOTION",
    "UNKNOWN != ZERO",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def output_digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _packet_cost(value: dict[str, Any]) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    q = max(0.0, min(1.0, float(quantile)))
    if len(ordered) == 1:
        return round(ordered[0], 3)
    position = q * (len(ordered) - 1)
    lo = int(position)
    hi = min(len(ordered) - 1, lo + 1)
    weight = position - lo
    return round(ordered[lo] * (1.0 - weight) + ordered[hi] * weight, 3)


def carrier_snapshot(runtime: LiminalBeaconMeshRuntime | None) -> dict[str, Any]:
    if runtime is None:
        return {
            "present": False,
            "digest": None,
            "packet_count": 0,
            "receipt_count": 0,
            "cursor_nonzero_count": 0,
        }
    with runtime._lock:
        value = {
            "presence": copy.deepcopy(runtime._presence),
            "packets": copy.deepcopy(runtime._packets),
            "route_index": [
                [str(key), sorted(str(item) for item in values)]
                for key, values in sorted(runtime._route_index.items())
            ],
            "receipts": [
                [str(agent_id), str(packet_id), copy.deepcopy(row)]
                for (agent_id, packet_id), row in sorted(runtime._receipts.items())
            ],
            "reverse_consumers": [
                [str(key), sorted(str(item) for item in values)]
                for key, values in sorted(runtime._reverse_consumers.items())
            ],
            "sender_seq": [
                [str(agent_id), str(epoch), int(seq)]
                for (agent_id, epoch), seq in sorted(runtime._sender_seq.items())
            ],
            "event_seq": int(runtime._event_seq),
            "lamport": int(runtime._lamport),
            "cursors": [[str(key), int(value)] for key, value in sorted(runtime._cursors.items())],
            "runtime_epoch": str(getattr(runtime, "_liminal_runtime_epoch", "UNKNOWN")),
        }
        return {
            "present": True,
            "digest": output_digest(value),
            "packet_count": len(runtime._packets),
            "receipt_count": len(runtime._receipts),
            "cursor_nonzero_count": sum(1 for value in runtime._cursors.values() if int(value) != 0),
        }


class LiminalBeaconShadowRuntime:
    def __init__(self, server: Any, *, clock=None, perf_counter_ns=None, record_limit: int = 200):
        self.server = server
        self.clock = clock or time.time
        self.perf_counter_ns = perf_counter_ns or time.perf_counter_ns
        self._lock = threading.RLock()
        self.source = LiminalBeaconMeshRuntime(server, clock=self.clock)
        self._would_presented: set[tuple[str, str]] = set()
        self._would_cursors: dict[str, int] = defaultdict(int)
        self._records = deque(maxlen=max(16, min(int(record_limit or 200), 2000)))
        self._metrics: dict[str, int] = defaultdict(int)
        self._holds = deque(maxlen=64)

    def manifest(self) -> dict[str, Any]:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "standing": "SHADOW_OBSERVATION_ONLY",
            "parent_integration": PARENT_INTEGRATION,
            "parent_master": PARENT_MASTER,
            "coordinate": "LSH=<PARENT,MODE,PROJECTION,WPR,WCR,OUT,OVERHEAD,FILTER,RESERVE,SEMANTIC,ISOLATION,STANDING>",
            "activation": "ATHENA_LIMINAL_SHADOW=1",
            "default": "DISABLED",
            "background_execution": False,
            "delivery": False,
            "context_injection": False,
            "cognition_receipts": False,
            "durable_git_write_intent": False,
            "laws": list(LAWS),
        }

    def _live_carrier(self) -> LiminalBeaconMeshRuntime | None:
        value = getattr(self.server, "_liminal_beacon_mesh_runtime_v1", None)
        return value if isinstance(value, LiminalBeaconMeshRuntime) else None

    def _projection(self) -> LiminalBeaconMeshRuntime:
        projection = LiminalBeaconMeshRuntime(self.server, clock=self.source.clock)
        with self.source._lock:
            projection._presence = copy.deepcopy(self.source._presence)
            projection._packets = copy.deepcopy(self.source._packets)
            projection._route_index = defaultdict(
                set,
                {key: set(values) for key, values in self.source._route_index.items()},
            )
            projection._receipts = {}
            projection._reverse_consumers = defaultdict(
                set,
                {key: set(values) for key, values in self.source._reverse_consumers.items()},
            )
            projection._sender_seq = defaultdict(int, dict(self.source._sender_seq))
            projection._event_seq = int(self.source._event_seq)
            projection._lamport = int(self.source._lamport)
            projection._cursors = defaultdict(int)
            projection._metrics = defaultdict(int)
            if hasattr(self.source, "_liminal_runtime_epoch"):
                projection._liminal_runtime_epoch = self.source._liminal_runtime_epoch

        now = float(projection.clock())
        for agent_id, packet_id in sorted(self._would_presented):
            if packet_id not in projection._packets:
                continue
            projection._receipts[(agent_id, packet_id)] = {
                "agent_id": agent_id,
                "packet_id": packet_id,
                "stage": "PRESENTED",
                "stage_index": 0,
                "updated_at": now,
                "disposition": None,
                "consumer_ref": None,
                "residual": None,
                "propagation_refs": [],
                "outcome_ref": None,
            }
        for agent_id, cursor in self._would_cursors.items():
            projection._cursors[agent_id] = int(cursor)
        return projection

    def _merge_producer_state(self, projection: LiminalBeaconMeshRuntime) -> None:
        with projection._lock:
            presence = copy.deepcopy(projection._presence)
            packets = copy.deepcopy(projection._packets)
            route_index = {key: set(values) for key, values in projection._route_index.items()}
            reverse_consumers = {key: set(values) for key, values in projection._reverse_consumers.items()}
            sender_seq = dict(projection._sender_seq)
            event_seq = int(projection._event_seq)
            lamport = int(projection._lamport)
            runtime_epoch = getattr(projection, "_liminal_runtime_epoch", None)

        with self.source._lock:
            self.source._presence = presence
            self.source._packets = packets
            self.source._route_index = defaultdict(set, route_index)
            self.source._reverse_consumers = defaultdict(set, reverse_consumers)
            self.source._sender_seq = defaultdict(int, sender_seq)
            self.source._event_seq = event_seq
            self.source._lamport = lamport
            if runtime_epoch is not None:
                self.source._liminal_runtime_epoch = runtime_epoch
            # Shadow source cognition state is structurally forbidden.
            self.source._receipts.clear()
            self.source._cursors.clear()

    def _adopt_would_state(self, projection: LiminalBeaconMeshRuntime) -> int:
        before = len(self._would_presented)
        with projection._lock:
            for (agent_id, packet_id), row in projection._receipts.items():
                if str(row.get("stage") or "").upper() == "PRESENTED":
                    self._would_presented.add((str(agent_id), str(packet_id)))
            for agent_id, cursor in projection._cursors.items():
                self._would_cursors[str(agent_id)] = max(
                    int(self._would_cursors.get(str(agent_id), 0)),
                    int(cursor),
                )
        return len(self._would_presented) - before

    @staticmethod
    def _rendezvous(value: Any) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            return None
        if value.get("status") == "RENDEZVOUS":
            return value
        nested = value.get("rendezvous")
        return nested if isinstance(nested, dict) else None

    @staticmethod
    def _semantic_state(structured: Any, after_value: Any) -> str:
        if not isinstance(structured, dict):
            return "UNKNOWN"
        if "_liminal_publish" not in structured:
            return "ABSENT"
        if isinstance(after_value, dict) and after_value.get("semantic_envelope"):
            return "VALID"
        if isinstance(after_value, dict) and after_value.get("semantic_error"):
            return "HOLD"
        return "UNKNOWN"

    @staticmethod
    def _rdv_summary(value: Any) -> dict[str, Any]:
        rendezvous = LiminalBeaconShadowRuntime._rendezvous(value)
        if not rendezvous:
            return {
                "would_present_count": 0,
                "would_present_bytes": 0,
                "would_present_classes": {},
                "backpressure_filtered_count": 0,
                "scope_filtered_count": 0,
                "context_budget_filtered_count": 0,
                "critical_reserve_would_use": 0,
                "context_budget": None,
                "context_used": 0,
                "queue_pressure": None,
            }
        packets = list(rendezvous.get("packets") or [])
        classes = Counter(str(packet.get("message_class") or "UNKNOWN") for packet in packets)
        return {
            "would_present_count": len(packets),
            "would_present_bytes": sum(_packet_cost(packet) for packet in packets),
            "would_present_classes": dict(sorted(classes.items())),
            "would_packet_digests": [
                hashlib.sha256(str(packet.get("packet_id") or "").encode("utf-8")).hexdigest()[:16]
                for packet in packets
            ],
            "backpressure_filtered_count": len(rendezvous.get("backpressure_filtered") or []),
            "scope_filtered_count": len(rendezvous.get("scope_filtered") or []),
            "context_budget_filtered_count": len(rendezvous.get("context_budget_filtered") or []),
            "critical_reserve_would_use": int(rendezvous.get("critical_reserve_used") or 0),
            "context_budget": rendezvous.get("context_budget"),
            "context_used": int(rendezvous.get("context_used") or 0),
            "queue_pressure": rendezvous.get("queue_pressure"),
        }

    def preview_rendezvous(self, agent_id: str, **kwargs) -> dict[str, Any]:
        """Run the installed V1.1 rendezvous on a projection and retain only WOULD state."""
        with self._lock:
            projection = self._projection()
            result = projection.rendezvous(agent_id, **kwargs)
            self._merge_producer_state(projection)
            new_would = self._adopt_would_state(projection)
            summary = self._rdv_summary(result)
            summary["new_would_presented"] = new_would
            summary["source_receipt_count"] = len(self.source._receipts)
            summary["source_cursor_nonzero_count"] = sum(
                1 for value in self.source._cursors.values() if int(value) != 0
            )
            summary["standing"] = "WOULD_PRESENT_ONLY"
            return summary

    def begin_crossing(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            live_before = carrier_snapshot(self._live_carrier())
            started = self.perf_counter_ns()
            projection = self._projection()
            value = projection.auto_before_tool(str(tool_name), dict(arguments or {}))
            self._merge_producer_state(projection)
            new_would = self._adopt_would_state(projection)
            elapsed_us = max(0.0, (self.perf_counter_ns() - started) / 1000.0)
            summary = self._rdv_summary(value)
            summary["new_would_presented"] = new_would
            return {
                "tool_name": str(tool_name)[:160],
                "tool_digest": hashlib.sha256(str(tool_name).encode("utf-8")).hexdigest()[:16],
                "agent_id": self.source.infer_agent_id(arguments or {}) or "UNKNOWN",
                "pre_shadow_us": round(elapsed_us, 3),
                "before": summary,
                "live_before": live_before,
            }

    def end_crossing(
        self,
        token: dict[str, Any],
        tool_name: str,
        arguments: dict[str, Any],
        structured: Any,
        domain_result: Any,
        *,
        successful: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
            output_before = output_digest(domain_result)
            after_value = None
            started = self.perf_counter_ns()
            if successful and isinstance(structured, dict):
                projection = self._projection()
                after_value = projection.auto_after_tool(str(tool_name), dict(arguments or {}), structured)
                self._merge_producer_state(projection)
                new_would = self._adopt_would_state(projection)
            else:
                new_would = 0
            elapsed_us = max(0.0, (self.perf_counter_ns() - started) / 1000.0)
            output_after = output_digest(domain_result)
            live_after = carrier_snapshot(self._live_carrier())
            source_state = carrier_snapshot(self.source)
            before_summary = dict(token.get("before") or {})
            after_summary = self._rdv_summary(after_value)
            after_summary["new_would_presented"] = new_would

            live_unchanged = token.get("live_before") == live_after
            output_preserved = output_before == output_after
            source_receipts_zero = source_state["receipt_count"] == 0
            source_cursors_zero = source_state["cursor_nonzero_count"] == 0
            record = {
                "schema": "ATHENA.LIMINAL.BEACON.SHADOW.CROSSING.1",
                "tool_name": str(token.get("tool_name") or tool_name)[:160],
                "tool_digest": str(token.get("tool_digest") or ""),
                "agent_id": str(token.get("agent_id") or "UNKNOWN")[:128],
                "output_digest_before": output_before,
                "output_digest_after": output_after,
                "output_preserved": output_preserved,
                "pre_shadow_us": float(token.get("pre_shadow_us") or 0.0),
                "post_shadow_us": round(elapsed_us, 3),
                "total_shadow_us": round(float(token.get("pre_shadow_us") or 0.0) + elapsed_us, 3),
                "before": before_summary,
                "after": after_summary,
                "would_present_count": int(before_summary.get("would_present_count") or 0)
                + int(after_summary.get("would_present_count") or 0),
                "would_present_bytes": int(before_summary.get("would_present_bytes") or 0)
                + int(after_summary.get("would_present_bytes") or 0),
                "backpressure_filtered_count": int(before_summary.get("backpressure_filtered_count") or 0)
                + int(after_summary.get("backpressure_filtered_count") or 0),
                "scope_filtered_count": int(before_summary.get("scope_filtered_count") or 0)
                + int(after_summary.get("scope_filtered_count") or 0),
                "context_budget_filtered_count": int(before_summary.get("context_budget_filtered_count") or 0)
                + int(after_summary.get("context_budget_filtered_count") or 0),
                "critical_reserve_would_use": int(before_summary.get("critical_reserve_would_use") or 0)
                + int(after_summary.get("critical_reserve_would_use") or 0),
                "semantic_state": self._semantic_state(structured, after_value),
                "source_shadow_receipt_count": int(source_state["receipt_count"]),
                "source_shadow_cursor_nonzero_count": int(source_state["cursor_nonzero_count"]),
                "live_carrier_unchanged": live_unchanged,
                "fast_plane_git_write_intent_count": 0,
                "hidden_process_count": "UNKNOWN",
                "independent_process_count": "UNKNOWN",
                "standing": (
                    "SHADOW_OBSERVED"
                    if output_preserved and live_unchanged and source_receipts_zero and source_cursors_zero
                    else "SHADOW_INVARIANT_HOLD"
                ),
            }
            self._records.append(record)
            self._metrics["crossings"] += 1
            self._metrics["output_mismatches"] += 0 if output_preserved else 1
            self._metrics["live_carrier_mutations"] += 0 if live_unchanged else 1
            self._metrics["source_receipt_violations"] += 0 if source_receipts_zero else 1
            self._metrics["source_cursor_violations"] += 0 if source_cursors_zero else 1
            self._metrics["would_present_packets"] += record["would_present_count"]
            self._metrics["would_present_bytes"] += record["would_present_bytes"]
            self._metrics["backpressure_filtered"] += record["backpressure_filtered_count"]
            self._metrics["scope_filtered"] += record["scope_filtered_count"]
            self._metrics["context_budget_filtered"] += record["context_budget_filtered_count"]
            self._metrics["critical_reserve_would_use"] += record["critical_reserve_would_use"]
            self._metrics["semantic_holds"] += 1 if record["semantic_state"] == "HOLD" else 0
            return copy.deepcopy(record)

    def record_hold(self, reason: str, *, tool_name: str | None = None) -> dict[str, Any]:
        with self._lock:
            row = {
                "schema": "ATHENA.LIMINAL.BEACON.SHADOW.HOLD.1",
                "standing": "SHADOW_HOLD",
                "reason": str(reason)[:256],
                "tool_name": str(tool_name or "")[:160] or None,
                "at": float(self.clock()),
            }
            self._holds.append(row)
            self._metrics["holds"] += 1
            return copy.deepcopy(row)

    def record_error(self, stage: str, exc: Exception, *, tool_name: str | None = None) -> dict[str, Any]:
        return self.record_hold(
            f"{str(stage).upper()}_ERROR:{type(exc).__name__}:{exc}",
            tool_name=tool_name,
        )

    def status(self, *, limit: int = 20, include_records: bool = False) -> dict[str, Any]:
        with self._lock:
            records = list(self._records)
            latencies = [float(row.get("total_shadow_us") or 0.0) for row in records]
            crossings = int(self._metrics.get("crossings", 0))
            source = carrier_snapshot(self.source)
            result = {
                **self.manifest(),
                "status": "OK",
                "crossing_count": crossings,
                "would_present_ledger_count": len(self._would_presented),
                "would_cursor_agent_count": len(self._would_cursors),
                "source_shadow": source,
                "metrics": dict(sorted(self._metrics.items())),
                "latency_us": {
                    "p50": _percentile(latencies, 0.50),
                    "p95": _percentile(latencies, 0.95),
                    "max": round(max(latencies), 3) if latencies else None,
                },
                "rates": {
                    "would_present_packets_per_crossing": round(
                        int(self._metrics.get("would_present_packets", 0)) / max(1, crossings), 6
                    ),
                    "would_present_bytes_per_crossing": round(
                        int(self._metrics.get("would_present_bytes", 0)) / max(1, crossings), 6
                    ),
                    "semantic_hold_rate": round(
                        int(self._metrics.get("semantic_holds", 0)) / max(1, crossings), 6
                    ),
                },
                "holds": list(self._holds)[-10:],
                "hidden_process_count": "UNKNOWN",
                "independent_process_count": "UNKNOWN",
            }
            if include_records:
                bounded = max(1, min(int(limit or 20), 200))
                result["records"] = copy.deepcopy(records[-bounded:])
            return result


__all__ = [
    "LiminalBeaconShadowRuntime",
    "carrier_snapshot",
    "output_digest",
    "VERSION",
    "ARTIFACT",
    "LAWS",
]
