from __future__ import annotations

"""Deterministic V1.1 replay of the frozen Liminal Beacon three-agent fixture.

This is a successor treatment replay, not a rescore of V1. It reuses the exact
V1 timing/policy fixture and changes only the two predeclared V1.1 treatment
coordinates: a strict typed correction envelope and receiver critical_quota=1.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_FIXTURE = ROOT / "tests" / "fixtures" / "liminal_beacon_effect_v1.json"
REPLAY_FIXTURE = ROOT / "tests" / "fixtures" / "liminal_beacon_effect_v11_replay.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass
class Clock:
    value: float = 0.0

    def __call__(self) -> float:
        return float(self.value)

    def set(self, value: float) -> None:
        self.value = float(value)


class DummyServer:
    git = None


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _trace(rows: list[dict[str, Any]], t: float, actor: str, action: str, **details: Any) -> None:
    rows.append({"t": float(t), "actor": actor, "action": action, **details})


def _matching_packet(view: dict[str, Any] | None, changed_ref: str) -> dict[str, Any] | None:
    if not isinstance(view, dict):
        return None
    for row in view.get("packets") or []:
        if changed_ref in (row.get("changed_refs") or []):
            return row
    return None


def _packet(view: dict[str, Any], packet_id: str) -> dict[str, Any] | None:
    return next((row for row in (view.get("packets") or []) if row.get("packet_id") == packet_id), None)


def _record_view(views: list[dict[str, Any]], label: str, view: dict[str, Any] | None) -> None:
    if not isinstance(view, dict):
        return
    views.append({
        "label": label,
        "context_used": int(view.get("context_used") or 0),
        "context_budget": int(view.get("context_budget") or 0),
        "critical_quota": int(view.get("critical_quota") or 0),
        "critical_reserve_used": int(view.get("critical_reserve_used") or 0),
        "critical_reserve_packet_ids": list(view.get("critical_reserve_packet_ids") or []),
        "backpressure_filtered": list(view.get("backpressure_filtered") or []),
        "context_budget_filtered": list(view.get("context_budget_filtered") or []),
        "scope_filtered": list(view.get("scope_filtered") or []),
    })


def run_replay(*, parent_ci_green: bool) -> dict[str, Any]:
    historical = _load(HISTORICAL_FIXTURE)
    replay = _load(REPLAY_FIXTURE)
    t = historical["times"]
    policy = historical["receiver_policy"]
    clock = Clock(float(t["initial_presence"]))
    mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=clock)
    trace: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []

    a0 = mesh.auto_before_tool("fixture_work", {"agent_id": "A", "oid": "X"})
    b0 = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Y"})
    mesh.auto_before_tool("fixture_work", {"agent_id": "C", "oid": "X"})
    _record_view(views, "A_INITIAL", a0)
    _record_view(views, "B_INITIAL", b0)
    _trace(trace, clock.value, "SYSTEM", "INITIAL_TOPOLOGY")

    clock.set(t["discovery"])
    d1_after = mesh.auto_after_tool(
        "fixture_work",
        {"agent_id": "A", "oid": "X"},
        {"status": "OK", "event": "D1", "discovery": "full payload intentionally not broadcast"},
    )
    d1_packet = dict((d1_after or {}).get("emitted") or {})
    d1_id = str(d1_packet.get("packet_id") or "")
    _record_view(views, "A_AFTER_D1", (d1_after or {}).get("rendezvous"))
    _trace(trace, clock.value, "A", "AUTO_AFTER_DISCOVERY", packet=d1_packet)

    clock.set(t["receiver_enters_object"])
    b_enter = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "X"})
    _record_view(views, "B_ENTER_X", b_enter)
    d1_seen = _matching_packet(b_enter, "event:D1")
    if d1_seen:
        mesh.receipt("B", d1_seen["packet_id"], "CONSUMED", consumer_ref="fixture-v11:B:D1")
        mesh.receipt("B", d1_seen["packet_id"], "INCORPORATED", disposition="ACCEPTED")
    _trace(trace, clock.value, "B", "ENTER_X", saw_d1=bool(d1_seen), rendezvous=b_enter)

    clock.set(t["duplicate_decision"])
    missed = 0.0 if d1_seen else 1.0
    duplicate_actions = 0 if d1_seen else 1
    _trace(trace, clock.value, "B", "DUPLICATE_DECISION", duplicate_action=bool(duplicate_actions))

    clock.set(t["receiver_leaves_object"])
    b_leave = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Z"})
    _record_view(views, "B_MOVE_Z", b_leave)
    _trace(trace, clock.value, "B", "MOVE_Z")

    # Frozen V1.1 treatment delta: explicit typed correction semantics only.
    clock.set(t["correction"])
    a_correct_before = mesh.auto_before_tool("fixture_correct", {"agent_id": "A", "oid": "X"})
    _record_view(views, "A_CORRECT_BEFORE", a_correct_before)
    c1_after = mesh.auto_after_tool(
        "fixture_correct",
        {"agent_id": "A", "oid": "X"},
        {
            "status": "STALE",
            "event": "C1",
            "secret_payload": "NEVER_BROADCAST_C1_FULL_RESULT",
            "_liminal_publish": {
                "message_class": "CORRECTION",
                "summary": "D1 partly wrong",
                "payload_ref": "event:C1",
                "changed_refs": ["event:C1"],
                "correction_of": d1_id,
            },
        },
    )
    c1_packet = dict((c1_after or {}).get("emitted") or {})
    _record_view(views, "A_AFTER_C1", (c1_after or {}).get("rendezvous"))
    _trace(trace, clock.value, "A", "TYPED_CORRECTION", packet=c1_packet)

    clock.set(t["receiver_next_crossing"])
    b_next = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Z"})
    _record_view(views, "B_NEXT_Z", b_next)
    c1_seen = _matching_packet(b_next, "event:C1")
    reverse_correction = bool(c1_seen and c1_seen.get("reverse_route"))
    if c1_seen:
        mesh.receipt("B", c1_seen["packet_id"], "CONSUMED", consumer_ref="fixture-v11:B:C1")
        mesh.receipt("B", c1_seen["packet_id"], "INCORPORATED", disposition="ACCEPTED")
    _trace(trace, clock.value, "B", "CORRECTION_RENDEZVOUS", saw_c1=bool(c1_seen), reverse_route=reverse_correction)

    # Re-establish A/C at X before overload probes.
    clock.set(t["low_salience_delta"] - 1)
    mesh.auto_before_tool("fixture_work", {"agent_id": "A", "oid": "X"})
    mesh.auto_before_tool("fixture_work", {"agent_id": "C", "oid": "X"})

    clock.set(t["low_salience_delta"])
    low_after = mesh.auto_after_tool(
        "fixture_work",
        {"agent_id": "A", "oid": "X"},
        {"status": "OK", "event": "LOW"},
    )
    low_id = str(((low_after or {}).get("emitted") or {}).get("packet_id") or "")
    c_low = mesh.rendezvous(
        "C",
        threshold=float(policy["overloaded_threshold"]),
        scout_quota=int(policy["scout_quota_adversarial"]),
        context_budget=int(policy["context_budget"]),
        critical_quota=1,
    )
    _record_view(views, "C_LOW", c_low)
    low_presented = _packet(c_low, low_id) is not None
    _trace(trace, clock.value, "C", "LOW_SALIENCE_PROBE", presented=low_presented)

    # Frozen V1.1 treatment delta: blocker remains generic; reserve must do work.
    clock.set(t["critical_blocker"])
    blocker_after = mesh.auto_after_tool(
        "fixture_work",
        {"agent_id": "A", "oid": "X"},
        {"status": "HOLD", "event": "BLOCK"},
    )
    blocker_id = str(((blocker_after or {}).get("emitted") or {}).get("packet_id") or "")
    c_block = mesh.rendezvous(
        "C",
        threshold=float(policy["overloaded_threshold"]),
        scout_quota=int(policy["scout_quota_adversarial"]),
        context_budget=int(policy["context_budget"]),
        critical_quota=1,
    )
    _record_view(views, "C_BLOCKER", c_block)
    blocker_capsule = _packet(c_block, blocker_id)
    blocker_presented = blocker_capsule is not None
    blocker_reserved = bool(blocker_capsule and blocker_capsule.get("critical_reserve"))
    _trace(trace, clock.value, "C", "CRITICAL_BLOCKER_PROBE", presented=blocker_presented, reserve=blocker_reserved)

    clock.set(t["direct_low_salience"])
    direct = mesh.emit(
        "A",
        "DELTA",
        "direct low salience",
        object_refs=["oid:X"],
        recipients=["C"],
        urgency=0.0,
        novelty=0.0,
    )["packet"]
    c_direct = mesh.rendezvous(
        "C",
        threshold=float(policy["overloaded_threshold"]),
        scout_quota=int(policy["scout_quota_adversarial"]),
        context_budget=int(policy["context_budget"]),
        critical_quota=1,
    )
    _record_view(views, "C_DIRECT", c_direct)
    direct_presented = _packet(c_direct, direct["packet_id"]) is not None
    _trace(trace, clock.value, "C", "DIRECT_LOW_PROBE", presented=direct_presented)

    clock.set(t["guild_scope_probe"])
    mesh.touch("A", object_refs=["oid:X"], party_refs=["guild:A"])
    mesh.touch("C", object_refs=["oid:X"], party_refs=["guild:B"])
    guild = mesh.emit(
        "A",
        "DELTA",
        "guild A only",
        object_refs=["oid:X"],
        party_refs=["guild:A"],
        visibility="GUILD",
        urgency=1.0,
        novelty=1.0,
    )["packet"]
    c_guild = mesh.rendezvous("C", threshold=0.0, scout_quota=0, critical_quota=1)
    _record_view(views, "C_GUILD", c_guild)
    guild_presented = _packet(c_guild, guild["packet_id"]) is not None
    _trace(trace, clock.value, "C", "GUILD_SCOPE_PROBE", presented=guild_presented)

    clock.set(t["restart_probe"])
    first_presence = mesh.touch("A", instance_id="worker-A", object_refs=["oid:X"])["presence"]
    first_marker = mesh.emit("A", "RESULT", "restart marker", object_refs=["oid:X"])["packet"]
    second_presence = mesh.touch("A", instance_id="worker-B", object_refs=["oid:X"])["presence"]
    second_marker = mesh.emit("A", "RESULT", "restart marker", object_refs=["oid:X"])["packet"]
    restart_rotated = (
        first_presence.get("session_epoch") != second_presence.get("session_epoch")
        and first_marker.get("packet_id") != second_marker.get("packet_id")
    )
    _trace(trace, clock.value, "A", "RESTART_REBIND", rotated=restart_rotated)

    context_hard_cap = all(
        int(row["context_used"]) <= int(row["context_budget"])
        for row in views
        if int(row["context_budget"]) > 0
    )
    max_reserve_used = max([int(row["critical_reserve_used"]) for row in views] or [0])
    full_result_absent = "NEVER_BROADCAST_C1_FULL_RESULT" not in json.dumps(c1_packet, sort_keys=True)
    correction_ceiling = c1_packet.get("evidence_ceiling")

    metrics = {
        "missed_material_delta_rate": missed,
        "accidental_duplicate_action_count": duplicate_actions,
        "time_to_first_useful_sibling_discovery": float(t["receiver_enters_object"] - t["discovery"]) if d1_seen else None,
        "correction_reach": 1.0 if reverse_correction else 0.0,
        "reverse_correction_route": reverse_correction,
        "critical_blocker_presented": blocker_presented,
        "critical_blocker_reserved": blocker_reserved,
        "max_critical_reserve_used": max_reserve_used,
        "low_salience_filtered": not low_presented,
        "direct_low_salience_filtered": not direct_presented,
        "guild_scope_isolated": not guild_presented,
        "restart_epoch_rotated": restart_rotated,
        "stale_or_scope_invalid_presentation_count": 0 if not guild_presented else 1,
        "existing_tool_regression_count": 0 if parent_ci_green else "UNKNOWN",
        "durable_coordination_git_write_count": 0,
        "hard_context_budget_preserved": context_hard_cap,
        "full_tool_result_absent_from_semantic_packet": full_result_absent,
        "semantic_evidence_ceiling": correction_ceiling,
    }

    rule = replay["success_rule"]
    criteria = {
        "missed_delta_zero": metrics["missed_material_delta_rate"] == float(rule["missed_material_delta_rate"]),
        "duplicate_zero": metrics["accidental_duplicate_action_count"] == int(rule["accidental_duplicate_action_count"]),
        "discovery_latency": metrics["time_to_first_useful_sibling_discovery"] is not None and metrics["time_to_first_useful_sibling_discovery"] <= float(rule["max_discovery_latency"]),
        "correction_reach": metrics["correction_reach"] == float(rule["correction_reach"]),
        "reverse_route": bool(metrics["reverse_correction_route"]),
        "critical_blocker": bool(metrics["critical_blocker_presented"]),
        "critical_reserve_bound": bool(metrics["critical_blocker_reserved"]) and int(metrics["max_critical_reserve_used"]) <= int(rule["max_critical_reserve_used_per_probe"]),
        "ordinary_filtered": bool(metrics["low_salience_filtered"]),
        "direct_filtered": bool(metrics["direct_low_salience_filtered"]),
        "guild_isolated": bool(metrics["guild_scope_isolated"]),
        "restart_rotated": bool(metrics["restart_epoch_rotated"]),
        "scope_stale_zero": int(metrics["stale_or_scope_invalid_presentation_count"]) <= int(rule["max_stale_or_scope_invalid_presentations"]),
        "existing_tools": (
            metrics["existing_tool_regression_count"] == int(rule["max_existing_tool_regressions"])
            if metrics["existing_tool_regression_count"] != "UNKNOWN"
            else "UNKNOWN"
        ),
        "no_fast_git_writes": int(metrics["durable_coordination_git_write_count"]) <= int(rule["max_routine_fast_plane_git_writes"]),
        "hard_context_budget": bool(metrics["hard_context_budget_preserved"]),
        "no_full_result_broadcast": bool(metrics["full_tool_result_absent_from_semantic_packet"]),
        "evidence_ceiling": metrics["semantic_evidence_ceiling"] == str(rule["semantic_evidence_ceiling"]),
    }
    known = [value for value in criteria.values() if value != "UNKNOWN"]
    status = "PASS" if all(value is True for value in known) and len(known) == len(criteria) else ("UNKNOWN" if "UNKNOWN" in criteria.values() and all(value is True for value in known) else "FAIL")

    return {
        "schema": replay["schema"],
        "standing": "MATCHED_DETERMINISTIC_REPLAY_NOT_GENERAL_CAUSAL_EFFECT",
        "historical_fixture_digest": _digest(historical),
        "replay_fixture_digest": _digest(replay),
        "treatment_delta_digest": _digest(replay["treatment_delta"]),
        "parent_candidate_head": replay["parent_candidate_head"],
        "parent_runtime_base": replay["parent_runtime_base"],
        "parent_ci_green": bool(parent_ci_green),
        "trace": trace,
        "rendezvous_accounting": views,
        "metrics": metrics,
        "criteria": criteria,
        "status": status,
        "historical_v1_challenger": replay["historical_v1_challenger"],
        "firewalls": replay["firewalls"],
    }


if __name__ == "__main__":
    print(json.dumps(run_replay(parent_ci_green=True), indent=2, sort_keys=True))
