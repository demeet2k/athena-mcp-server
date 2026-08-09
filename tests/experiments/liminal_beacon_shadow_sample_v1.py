from __future__ import annotations

"""Frozen actual-dispatch descriptive sample for Liminal Beacon Shadow V1.

Contract: public issue #339. This module is experiment-only and changes no
runtime behavior. Latency is descriptive in V1 and cannot change PASS/FAIL.
"""

import copy
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import time
from collections import Counter
from contextlib import contextmanager
from typing import Any

import athena_mcp  # noqa: F401 - install the exact candidate package composition
from athena_mcp import dispatch
from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.liminal_beacon_shadow import carrier_snapshot
from athena_mcp.server import Server

FIXTURE_PATH = pathlib.Path(__file__).with_name("liminal_beacon_shadow_sample_v1.fixture.json")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return round(ordered[0], 3)
    position = max(0.0, min(1.0, float(q))) * (len(ordered) - 1)
    lo = int(position)
    hi = min(len(ordered) - 1, lo + 1)
    weight = position - lo
    return round(ordered[lo] * (1.0 - weight) + ordered[hi] * weight, 3)


def _latency_packet(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "p50_us": _percentile(values, 0.50),
        "p95_us": _percentile(values, 0.95),
        "max_us": round(max(values), 3) if values else None,
        "values_us": [round(float(value), 3) for value in values],
    }


@contextmanager
def _arm(shadow: bool):
    old_shadow = os.environ.get("ATHENA_LIMINAL_SHADOW")
    old_auto = os.environ.get("ATHENA_LIMINAL_AUTOHOOK")
    try:
        if shadow:
            os.environ["ATHENA_LIMINAL_SHADOW"] = "1"
        else:
            os.environ.pop("ATHENA_LIMINAL_SHADOW", None)
        os.environ.pop("ATHENA_LIMINAL_AUTOHOOK", None)
        yield
    finally:
        if old_shadow is None:
            os.environ.pop("ATHENA_LIMINAL_SHADOW", None)
        else:
            os.environ["ATHENA_LIMINAL_SHADOW"] = old_shadow
        if old_auto is None:
            os.environ.pop("ATHENA_LIMINAL_AUTOHOOK", None)
        else:
            os.environ["ATHENA_LIMINAL_AUTOHOOK"] = old_auto


def _dispatch_call(server: Server, crossing: dict[str, Any], *, shadow: bool) -> tuple[dict[str, Any], float]:
    message = {
        "jsonrpc": "2.0",
        "id": int(crossing["id"]),
        "method": "tools/call",
        "params": {
            "name": crossing["tool"],
            "arguments": copy.deepcopy(crossing.get("arguments") or {}),
        },
    }
    with _arm(shadow):
        started = time.perf_counter_ns()
        result = dispatch.handle(server, message)
        elapsed_us = max(0.0, (time.perf_counter_ns() - started) / 1000.0)
    if not isinstance(result, dict) or "result" not in result:
        raise AssertionError(f"dispatch crossing did not return JSON-RPC result: {crossing['name']}")
    return result, elapsed_us


def _shadow_status(server: Server, *, include_records: bool = True) -> dict[str, Any]:
    runtime = getattr(server, "_liminal_beacon_shadow_runtime_v1", None)
    if runtime is None:
        raise AssertionError("shadow runtime missing after SHADOW crossing")
    return runtime.status(limit=200, include_records=include_records)


def _seed_shadow_source(server: Server, seed: dict[str, Any]) -> str:
    runtime = getattr(server, "_liminal_beacon_shadow_runtime_v1", None)
    if runtime is None:
        raise AssertionError("shadow runtime must exist before seed")
    source = runtime.source
    source.touch(
        seed["sender_id"],
        semantic_tags=list(seed["semantic_tags"]),
        focus="sample:bounded-seed",
        lease_seconds=30,
    )
    result = source.emit(
        seed["sender_id"],
        seed["message_class"],
        seed["summary"],
        semantic_tags=list(seed["semantic_tags"]),
        urgency=float(seed["urgency"]),
        novelty=float(seed["novelty"]),
        ttl_seconds=int(seed["ttl_seconds"]),
    )
    return str((result.get("packet") or {}).get("packet_id") or "")


def _structured(result: dict[str, Any]) -> Any:
    payload = result.get("result") or {}
    return payload.get("structuredContent") if isinstance(payload, dict) else None


def _live_control(server: Server, fixture: dict[str, Any]) -> dict[str, Any]:
    control = fixture["live_control"]
    live = LiminalBeaconMeshRuntime(server)
    live.touch(control["agent_id"], work_refs=list(control["work_refs"]), lease_seconds=60)
    live.emit(
        control["agent_id"],
        "RESULT",
        control["summary"],
        work_refs=list(control["work_refs"]),
        ttl_seconds=900,
    )
    server._liminal_beacon_mesh_runtime_v1 = live
    before = carrier_snapshot(live)
    crossing = {"id": 105, "name": "live_isolation", "tool": "athena_hydrate", "arguments": {"agent": "SAMPLE-A"}}
    result, latency_us = _dispatch_call(server, crossing, shadow=True)
    after = carrier_snapshot(live)
    return {
        "before": before,
        "after": after,
        "equal": before == after,
        "latency_us": round(latency_us, 3),
        "domain_has_liminal_injection": isinstance(_structured(result), dict) and "_liminal_beacon" in _structured(result),
    }


def _restart_control() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="athena-lsh-restart-") as root:
        server = Server(str(pathlib.Path(root) / "state.db"), git_root=None)
        try:
            crossing = {
                "jsonrpc": "2.0",
                "id": 106,
                "method": "tools/call",
                "params": {"name": "athena_liminal_beacon_shadow_status", "arguments": {"include_records": True}},
            }
            with _arm(True):
                response = dispatch.handle(server, crossing)
            value = ((response or {}).get("result") or {}).get("structuredContent") or {}
            return {
                "crossing_count": int(value.get("crossing_count") or 0),
                "would_present_ledger_count": int(value.get("would_present_ledger_count") or 0),
                "hidden_process_count": value.get("hidden_process_count", "UNKNOWN"),
                "independent_process_count": value.get("independent_process_count", "UNKNOWN"),
                "reset": int(value.get("crossing_count") or 0) == 0 and int(value.get("would_present_ledger_count") or 0) == 0,
            }
        finally:
            server.store.close()


def _trial(fixture: dict[str, Any], trial_index: int) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    off_latencies: list[float] = []
    shadow_latencies: list[float] = []
    seed_packet_id = ""
    unknown_packet_delta = None

    with tempfile.TemporaryDirectory(prefix=f"athena-lsh-sample-{trial_index}-") as root:
        server = Server(str(pathlib.Path(root) / "state.db"), git_root=None)
        try:
            crossings = {row["name"]: row for row in fixture["paired_crossings"]}

            # A: same server, same state, same JSON-RPC id. Shadow cannot alter the
            # domain result; runtime-use metering is outside AthenaCore.hydrate().
            off_a, off_us = _dispatch_call(server, crossings["hydrate_a"], shadow=False)
            sh_a, sh_us = _dispatch_call(server, crossings["hydrate_a"], shadow=True)
            off_latencies.append(off_us); shadow_latencies.append(sh_us)
            pairs.append({
                "name": "hydrate_a",
                "off_digest": _digest(off_a),
                "shadow_digest": _digest(sh_a),
                "equal": _canonical(off_a) == _canonical(sh_a),
                "shadow_injection": isinstance(_structured(sh_a), dict) and "_liminal_beacon" in _structured(sh_a),
            })

            # B first: OFF observation occurs before the bounded shadow-only seed.
            # The seed cannot affect AthenaCore.hydrate output and exists only in
            # the isolated shadow carrier.
            off_b1, off_us = _dispatch_call(server, crossings["hydrate_b_first"], shadow=False)
            seed_packet_id = _seed_shadow_source(server, fixture["seed"])
            sh_b1, sh_us = _dispatch_call(server, crossings["hydrate_b_first"], shadow=True)
            off_latencies.append(off_us); shadow_latencies.append(sh_us)
            status_after_b1 = _shadow_status(server, include_records=True)
            b1_record = status_after_b1["records"][-1]
            pairs.append({
                "name": "hydrate_b_first",
                "off_digest": _digest(off_b1),
                "shadow_digest": _digest(sh_b1),
                "equal": _canonical(off_b1) == _canonical(sh_b1),
                "shadow_injection": isinstance(_structured(sh_b1), dict) and "_liminal_beacon" in _structured(sh_b1),
            })

            off_b2, off_us = _dispatch_call(server, crossings["hydrate_b_duplicate"], shadow=False)
            sh_b2, sh_us = _dispatch_call(server, crossings["hydrate_b_duplicate"], shadow=True)
            off_latencies.append(off_us); shadow_latencies.append(sh_us)
            status_after_b2 = _shadow_status(server, include_records=True)
            b2_record = status_after_b2["records"][-1]
            pairs.append({
                "name": "hydrate_b_duplicate",
                "off_digest": _digest(off_b2),
                "shadow_digest": _digest(sh_b2),
                "equal": _canonical(off_b2) == _canonical(sh_b2),
                "shadow_injection": isinstance(_structured(sh_b2), dict) and "_liminal_beacon" in _structured(sh_b2),
            })

            # Unknown-agent negative control: no identity may be invented and no
            # producer packet may appear merely because a tool boundary existed.
            off_git, off_us = _dispatch_call(server, crossings["unknown_agent_git_status"], shadow=False)
            source_before_unknown = len(server._liminal_beacon_shadow_runtime_v1.source._packets)
            sh_git, sh_us = _dispatch_call(server, crossings["unknown_agent_git_status"], shadow=True)
            source_after_unknown = len(server._liminal_beacon_shadow_runtime_v1.source._packets)
            unknown_packet_delta = source_after_unknown - source_before_unknown
            off_latencies.append(off_us); shadow_latencies.append(sh_us)
            unknown_record = _shadow_status(server, include_records=True)["records"][-1]
            pairs.append({
                "name": "unknown_agent_git_status",
                "off_digest": _digest(off_git),
                "shadow_digest": _digest(sh_git),
                "equal": _canonical(off_git) == _canonical(sh_git),
                "shadow_injection": isinstance(_structured(sh_git), dict) and "_liminal_beacon" in _structured(sh_git),
            })

            live = _live_control(server, fixture)
            status = _shadow_status(server, include_records=True)
            records = list(status.get("records") or [])
            record_key_leaks = sum(
                1
                for row in records
                if any(key in row for key in ("domain_result", "structuredContent", "content"))
            )
            authority_or_evidence_fields = sum(
                1
                for row in records
                if any(key.casefold() in {"authority", "evidence"} for key in row)
            )
            source = status.get("source_shadow") or {}
            source_runtime = server._liminal_beacon_shadow_runtime_v1.source
            durable_bridges = int(source_runtime._metrics.get("durable_bridges", 0))
            fast_write_intent = sum(int(row.get("fast_plane_git_write_intent_count") or 0) for row in records)
            would_classes = Counter()
            for row in records:
                for side in ("before", "after"):
                    for cls, count in ((row.get(side) or {}).get("would_present_classes") or {}).items():
                        would_classes[str(cls)] += int(count)

            criteria = {
                "paired_domain_outputs_equal": all(row["equal"] for row in pairs),
                "observer_output_mismatch_zero": int((status.get("metrics") or {}).get("output_mismatches", 0)) == 0,
                "source_shadow_receipts_zero": int(source.get("receipt_count") or 0) == 0,
                "source_shadow_cursors_zero": int(source.get("cursor_nonzero_count") or 0) == 0,
                "live_carrier_unchanged": bool(live["equal"]),
                "first_b_has_new_would": int((b1_record.get("before") or {}).get("new_would_presented") or 0) >= 1,
                "duplicate_b_has_zero_new_would": int((b2_record.get("before") or {}).get("new_would_presented") or 0) == 0,
                "unknown_agent_remains_unknown": str(unknown_record.get("agent_id")) == "UNKNOWN" and unknown_packet_delta == 0,
                "no_context_injection": not any(row["shadow_injection"] for row in pairs) and not live["domain_has_liminal_injection"],
                "no_full_result_leak": record_key_leaks == 0,
                "no_evidence_or_authority_fields": authority_or_evidence_fields == 0,
                "no_git_bridge_or_fast_write_intent": durable_bridges == 0 and fast_write_intent == 0,
                "real_autohook_disabled": "ATHENA_LIMINAL_AUTOHOOK" not in os.environ,
            }

            result = {
                "trial": trial_index,
                "pairs": pairs,
                "seed_packet_digest": hashlib.sha256(seed_packet_id.encode("utf-8")).hexdigest()[:16],
                "first_b_new_would": int((b1_record.get("before") or {}).get("new_would_presented") or 0),
                "duplicate_b_new_would": int((b2_record.get("before") or {}).get("new_would_presented") or 0),
                "unknown_agent": str(unknown_record.get("agent_id")),
                "unknown_packet_delta": int(unknown_packet_delta or 0),
                "off_wall_us": [round(value, 3) for value in off_latencies],
                "shadow_wall_us": [round(value, 3) for value in shadow_latencies],
                "overhead_delta_us": [round(shadow - off, 3) for off, shadow in zip(off_latencies, shadow_latencies)],
                "shadow_internal_latency_us": copy.deepcopy(status.get("latency_us") or {}),
                "would_present_packets": int((status.get("metrics") or {}).get("would_present_packets", 0)),
                "would_present_bytes": int((status.get("metrics") or {}).get("would_present_bytes", 0)),
                "would_present_classes": dict(sorted(would_classes.items())),
                "backpressure_filtered": int((status.get("metrics") or {}).get("backpressure_filtered", 0)),
                "scope_filtered": int((status.get("metrics") or {}).get("scope_filtered", 0)),
                "context_budget_filtered": int((status.get("metrics") or {}).get("context_budget_filtered", 0)),
                "critical_reserve_would_use": int((status.get("metrics") or {}).get("critical_reserve_would_use", 0)),
                "semantic_states": [str(row.get("semantic_state") or "UNKNOWN") for row in records],
                "source_shadow_receipt_count": int(source.get("receipt_count") or 0),
                "source_shadow_cursor_nonzero_count": int(source.get("cursor_nonzero_count") or 0),
                "live_control": live,
                "fast_plane_git_write_intent_count": fast_write_intent,
                "durable_bridge_count": durable_bridges,
                "full_result_leak_count": record_key_leaks,
                "evidence_or_authority_field_count": authority_or_evidence_fields,
                "criteria": criteria,
                "status": "PASS" if all(criteria.values()) else "FAIL",
            }
            return result
        finally:
            server.store.close()


def run_sample() -> dict[str, Any]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    trials = [_trial(fixture, index + 1) for index in range(int(fixture["trial_count"]))]
    restart = _restart_control()
    off_lat = [value for trial in trials for value in trial["off_wall_us"]]
    shadow_lat = [value for trial in trials for value in trial["shadow_wall_us"]]
    overhead = [value for trial in trials for value in trial["overhead_delta_us"]]
    shadow_internal = []
    for trial in trials:
        # Per-trial observer already reports percentile summaries rather than raw
        # internal values; retain those summaries as measured telemetry.
        value = trial.get("shadow_internal_latency_us") or {}
        if value.get("p50") is not None:
            shadow_internal.append(float(value["p50"]))

    aggregate_criteria = {
        "all_trials_pass": all(trial["status"] == "PASS" for trial in trials),
        "restart_reset": bool(restart["reset"]),
        "restart_hidden_process_unknown": restart["hidden_process_count"] == "UNKNOWN",
        "restart_independent_process_unknown": restart["independent_process_count"] == "UNKNOWN",
    }
    checkout_head = "UNKNOWN_LOCAL"
    try:
        checkout_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        pass

    result = {
        "schema": "ATHENA.LIMINAL.BEACON.SHADOW.SAMPLE.RESULT.1",
        "standing": "SCOPED_ACTUAL_DISPATCH_SHADOW_OBSERVATION",
        "fixture_digest": _digest(fixture),
        "fixture": {
            "contract_issue": fixture["contract_issue"],
            "shadow_parent_head": fixture["shadow_parent_head"],
            "integration_parent_head": fixture["integration_parent_head"],
            "master_ancestry": fixture["master_ancestry"],
            "trial_count": fixture["trial_count"],
        },
        "checkout_head_observed": checkout_head,
        "github_sha": os.getenv("GITHUB_SHA") or "UNKNOWN_LOCAL",
        "trials": trials,
        "latency": {
            "off_wall": _latency_packet(off_lat),
            "shadow_wall": _latency_packet(shadow_lat),
            "overhead_delta": _latency_packet(overhead),
            "shadow_internal_trial_p50": _latency_packet(shadow_internal),
            "rule": "MEASUREMENT_ONLY_NO_PASS_THRESHOLD",
        },
        "restart": restart,
        "aggregate_criteria": aggregate_criteria,
        "hidden_process_count": "UNKNOWN",
        "independent_process_count": "UNKNOWN",
        "firewalls": list(fixture["firewalls"]),
        "status": "PASS" if all(aggregate_criteria.values()) else "FAIL",
    }
    return result


if __name__ == "__main__":
    packet = run_sample()
    print("LIMINAL_BEACON_SHADOW_SAMPLE_RESULT=" + json.dumps(packet, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if packet["status"] == "PASS" else 1)
