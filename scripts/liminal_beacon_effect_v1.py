from __future__ import annotations

"""Deterministic matched behavioral fixture for Liminal Beacon Mesh V1.

This runner is deliberately a simulated three-agent fixture. It can establish a
mechanism-level behavioral difference under the frozen scenario; it cannot prove
general causal gain or independently running agent multiplicity.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "liminal_beacon_effect_v1.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _bytes(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


@dataclass
class Clock:
    value: float = 0.0

    def __call__(self) -> float:
        return float(self.value)

    def set(self, value: float) -> None:
        self.value = float(value)


class DummyServer:
    git = None


class ManualBoardSurrogate:
    """Frozen baseline surrogate for deliberate durable message-board exchange.

    A publish counts as one expected durable coordination write because Message
    Board V1 material posts are Git-backed. The fixture does not claim these are
    actual Git executions; the standing is retained explicitly in arm output.
    """

    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self.writes = 0

    def publish(self, *, created_at: float, message_id: str, kind: str, summary: str, ref: str) -> dict[str, Any]:
        row = {
            "message_id": message_id,
            "created_at": float(created_at),
            "kind": kind,
            "summary": summary,
            "ref": ref,
            "delivery": "AVAILABLE_ON_EXPLICIT_POLL",
        }
        self.rows.append(row)
        self.writes += 1
        return row

    def poll(self, *, after: float = -1.0) -> list[dict[str, Any]]:
        return [dict(row) for row in self.rows if float(row["created_at"]) > float(after)]


def load_fixture(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_FIXTURE
    return json.loads(target.read_text(encoding="utf-8"))


def _trace(rows: list[dict[str, Any]], t: float, actor: str, action: str, **details: Any) -> None:
    rows.append({"t": float(t), "actor": actor, "action": action, **details})


def run_baseline(fixture: dict[str, Any], *, parent_ci_green: bool) -> dict[str, Any]:
    t = fixture["times"]
    board = ManualBoardSurrogate()
    trace: list[dict[str, Any]] = []

    d1 = board.publish(
        created_at=t["discovery"],
        message_id="D1",
        kind="DISCOVERY",
        summary="object X discovery",
        ref="event:D1",
    )
    _trace(trace, t["discovery"], "A", "PUBLISH_DISCOVERY", message=d1)

    _trace(trace, t["receiver_enters_object"], "B", "ENTER_OBJECT_X_WITHOUT_POLL")
    known_d1_at_decision = False
    duplicate_actions = 0 if known_d1_at_decision else 1
    missed = 0.0 if known_d1_at_decision else 1.0
    _trace(
        trace,
        t["duplicate_decision"],
        "B",
        "DUPLICATE_DECISION",
        knew_d1=known_d1_at_decision,
        duplicate_action=bool(duplicate_actions),
    )
    _trace(trace, t["receiver_leaves_object"], "B", "MOVE_TO_OBJECT_Z")

    c1 = board.publish(
        created_at=t["correction"],
        message_id="C1",
        kind="CORRECTION",
        summary="D1 partly wrong",
        ref="correction-of:D1",
    )
    _trace(trace, t["correction"], "A", "PUBLISH_CORRECTION", message=c1)

    polled = board.poll()
    context_bytes = sum(_bytes(row) for row in polled)
    seen_d1 = next((row for row in polled if row["message_id"] == "D1"), None)
    seen_c1 = next((row for row in polled if row["message_id"] == "C1"), None)
    _trace(trace, t["baseline_poll"], "B", "EXPLICIT_MANUAL_POLL", messages=polled)

    useful_consumed = int(seen_d1 is not None) + int(seen_c1 is not None)
    ratio = (context_bytes / useful_consumed) if useful_consumed else None
    metrics = {
        "missed_material_delta_rate": missed,
        "accidental_duplicate_action_count": duplicate_actions,
        "time_to_first_useful_sibling_discovery": (
            float(t["baseline_poll"] - t["discovery"]) if seen_d1 else None
        ),
        "presentation_latency": float(t["baseline_poll"] - t["discovery"]) if seen_d1 else None,
        "explicit_consumption_latency": float(t["baseline_poll"] - t["discovery"]) if seen_d1 else None,
        "context_bytes_presented": context_bytes,
        "useful_consumed_packet_count": useful_consumed,
        "context_bytes_per_useful_consumed_packet": ratio,
        "correction_reach": 1.0 if seen_c1 else 0.0,
        "stale_or_scope_invalid_presentation_count": 0,
        "fast_touch_count": 0,
        "durable_coordination_git_write_count": board.writes,
        "git_write_amplification": float(board.writes),
        "existing_tool_regression_count": 0 if parent_ci_green else "UNKNOWN",
        "preventable_human_steering_count": 1,
    }
    return {
        "arm": "B0_BASELINE",
        "standing": "SIMULATED_MANUAL_MESSAGE_BOARD_SURROGATE",
        "trace": trace,
        "metrics": metrics,
    }


def _matching_packet(view: dict[str, Any] | None, ref: str) -> dict[str, Any] | None:
    if not isinstance(view, dict):
        return None
    for row in view.get("packets") or []:
        if ref in (row.get("changed_refs") or []):
            return row
    return None


def run_challenger(fixture: dict[str, Any], *, parent_ci_green: bool) -> dict[str, Any]:
    t = fixture["times"]
    clock = Clock(float(t["initial_presence"]))
    mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=clock)
    trace: list[dict[str, Any]] = []
    context_bytes = 0

    # Initial positions are established through the same automatic crossing hook.
    a0 = mesh.auto_before_tool("fixture_work", {"agent_id": "A", "oid": "X"})
    b0 = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Y"})
    mesh.touch("C", object_refs=["oid:X"], focus="overloaded neighbor")
    _trace(trace, clock.value, "A", "AUTO_BEFORE_X", rendezvous=a0)
    _trace(trace, clock.value, "B", "AUTO_BEFORE_Y", rendezvous=b0)

    # A material tool result exposes only bounded metadata and event identity.
    clock.set(t["discovery"])
    d1_after = mesh.auto_after_tool(
        "fixture_work",
        {"agent_id": "A", "oid": "X"},
        {"status": "OK", "event": "D1", "discovery": "full payload intentionally not broadcast"},
    )
    d1_packet = dict((d1_after or {}).get("emitted") or {})
    d1_id = str(d1_packet.get("packet_id") or "")
    _trace(trace, clock.value, "A", "AUTO_AFTER_DISCOVERY", packet=d1_packet)

    # B enters X without sender identity or packet id. D1 must arrive topologically.
    clock.set(t["receiver_enters_object"])
    b_enter = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "X"})
    context_bytes += int((b_enter or {}).get("context_used") or 0)
    d1_seen = _matching_packet(b_enter, "event:D1")
    d1_consumed_at = None
    if d1_seen:
        d1_consumed_at = clock.value
        mesh.receipt("B", d1_seen["packet_id"], "CONSUMED", consumer_ref="fixture:B:D1")
        mesh.receipt("B", d1_seen["packet_id"], "INCORPORATED", disposition="ACCEPTED")
    _trace(trace, clock.value, "B", "AUTO_ENTER_X", saw_d1=bool(d1_seen), rendezvous=b_enter)

    clock.set(t["duplicate_decision"])
    duplicate_actions = 0 if d1_seen else 1
    missed = 0.0 if d1_seen else 1.0
    _trace(trace, clock.value, "B", "DUPLICATE_DECISION", knew_d1=bool(d1_seen), duplicate_action=bool(duplicate_actions))

    clock.set(t["receiver_leaves_object"])
    b_leave = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Z"})
    context_bytes += int((b_leave or {}).get("context_used") or 0)
    _trace(trace, clock.value, "B", "AUTO_MOVE_Z", rendezvous=b_leave)

    # Current V1 autohook receives correction-like result metadata but does not
    # infer correction_of lineage. The scored fixture intentionally observes that.
    clock.set(t["correction"])
    mesh.auto_before_tool("fixture_correct", {"agent_id": "A", "oid": "X"})
    c1_after = mesh.auto_after_tool(
        "fixture_correct",
        {"agent_id": "A", "oid": "X"},
        {"status": "STALE", "event": "C1", "correction_of": d1_id},
    )
    c1_packet = dict((c1_after or {}).get("emitted") or {})
    _trace(trace, clock.value, "A", "AUTO_AFTER_CORRECTION_LIKE_RESULT", packet=c1_packet)

    clock.set(t["receiver_next_crossing"])
    b_next = mesh.auto_before_tool("fixture_work", {"agent_id": "B", "oid": "Z"})
    context_bytes += int((b_next or {}).get("context_used") or 0)
    c1_seen = _matching_packet(b_next, "event:C1")
    correction_reverse = bool(c1_seen and c1_seen.get("reverse_route"))
    if c1_seen:
        # Presentation by scout is not credited as reverse correction reach.
        mesh.receipt("B", c1_seen["packet_id"], "CONSUMED", consumer_ref="fixture:B:C1")
        mesh.receipt("B", c1_seen["packet_id"], "INCORPORATED", disposition="PARTIAL")
    _trace(
        trace,
        clock.value,
        "B",
        "AUTO_NEXT_CROSSING_Z",
        saw_c1=bool(c1_seen),
        reverse_correction_route=correction_reverse,
        rendezvous=b_next,
    )

    # Refresh A/C at X before attention adversarial probes.
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
    c_low = mesh.rendezvous("C", threshold=0.95, scout_quota=0, context_budget=fixture["receiver_policy"]["context_budget"])
    context_bytes += int(c_low.get("context_used") or 0)
    low_presented = any(row.get("packet_id") == low_id for row in c_low.get("packets") or [])
    _trace(trace, clock.value, "C", "HIGH_THRESHOLD_LOW_DELTA", presented=low_presented, rendezvous=c_low)

    clock.set(t["critical_blocker"])
    blocker_after = mesh.auto_after_tool(
        "fixture_work",
        {"agent_id": "A", "oid": "X"},
        {"status": "HOLD", "event": "BLOCK"},
    )
    blocker_id = str(((blocker_after or {}).get("emitted") or {}).get("packet_id") or "")
    c_block = mesh.rendezvous("C", threshold=0.95, scout_quota=0, context_budget=fixture["receiver_policy"]["context_budget"])
    context_bytes += int(c_block.get("context_used") or 0)
    blocker_presented = any(row.get("packet_id") == blocker_id for row in c_block.get("packets") or [])
    _trace(trace, clock.value, "C", "HIGH_THRESHOLD_BLOCKER", presented=blocker_presented, rendezvous=c_block)

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
    c_direct = mesh.rendezvous("C", threshold=0.95, scout_quota=0, context_budget=fixture["receiver_policy"]["context_budget"])
    context_bytes += int(c_direct.get("context_used") or 0)
    direct_presented = any(row.get("packet_id") == direct["packet_id"] for row in c_direct.get("packets") or [])
    _trace(trace, clock.value, "C", "DIRECT_BACKPRESSURE_PROBE", presented=direct_presented, rendezvous=c_direct)

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
    c_guild = mesh.rendezvous("C", threshold=0.0, scout_quota=0)
    context_bytes += int(c_guild.get("context_used") or 0)
    guild_presented = any(row.get("packet_id") == guild["packet_id"] for row in c_guild.get("packets") or [])
    _trace(trace, clock.value, "C", "GUILD_SCOPE_PROBE", presented=guild_presented, rendezvous=c_guild)

    clock.set(t["restart_probe"])
    first_presence = mesh.touch("A", instance_id="worker-A", object_refs=["oid:X"])["presence"]
    first_marker = mesh.emit("A", "RESULT", "restart marker", object_refs=["oid:X"])["packet"]
    second_presence = mesh.touch("A", instance_id="worker-B", object_refs=["oid:X"])["presence"]
    second_marker = mesh.emit("A", "RESULT", "restart marker", object_refs=["oid:X"])["packet"]
    restart_rotated = (
        first_presence.get("session_epoch") != second_presence.get("session_epoch")
        and first_marker.get("packet_id") != second_marker.get("packet_id")
    )
    _trace(trace, clock.value, "A", "RESTART_PROBE", rotated=restart_rotated)

    state = mesh.state()
    useful_consumed = int(d1_seen is not None) + int(c1_seen is not None)
    ratio = (context_bytes / useful_consumed) if useful_consumed else None
    stale_or_scope_invalid = int(low_presented) + int(direct_presented) + int(guild_presented)
    metrics = {
        "missed_material_delta_rate": missed,
        "accidental_duplicate_action_count": duplicate_actions,
        "time_to_first_useful_sibling_discovery": (
            float(t["receiver_enters_object"] - t["discovery"]) if d1_seen else None
        ),
        "presentation_latency": float(t["receiver_enters_object"] - t["discovery"]) if d1_seen else None,
        "explicit_consumption_latency": (
            float(d1_consumed_at - t["discovery"]) if d1_consumed_at is not None else None
        ),
        "context_bytes_presented": context_bytes,
        "useful_consumed_packet_count": useful_consumed,
        "context_bytes_per_useful_consumed_packet": ratio,
        "correction_reach": 1.0 if correction_reverse else 0.0,
        "correction_was_presented_by_any_route": bool(c1_seen),
        "stale_or_scope_invalid_presentation_count": stale_or_scope_invalid,
        "low_salience_filtered": not low_presented,
        "critical_blocker_presented": blocker_presented,
        "direct_low_salience_filtered": not direct_presented,
        "guild_scope_isolated": not guild_presented,
        "restart_epoch_rotated": restart_rotated,
        "fast_touch_count": int((state.get("metrics") or {}).get("touches", 0)),
        "durable_coordination_git_write_count": int((state.get("metrics") or {}).get("durable_bridges", 0)),
        "git_write_amplification": float(state.get("git_write_amplification_proxy") or 0.0),
        "existing_tool_regression_count": 0 if parent_ci_green else "UNKNOWN",
        "preventable_human_steering_count": 0,
    }
    return {
        "arm": "B1_LIMINAL_AUTOHOOK",
        "standing": "SIMULATED_PROCESS_LOCAL_AUTOHOOK_FIXTURE",
        "trace": trace,
        "metrics": metrics,
        "state_summary": {
            "active_presence_count": state.get("active_presence_count"),
            "packet_count": state.get("packet_count"),
            "receipt_count": state.get("receipt_count"),
            "hidden_process_count": state.get("hidden_process_count"),
            "independent_process_count": state.get("independent_process_count"),
        },
    }


def compare(fixture: dict[str, Any], baseline: dict[str, Any], challenger: dict[str, Any]) -> dict[str, Any]:
    b = baseline["metrics"]
    c = challenger["metrics"]
    max_ratio = float(fixture["decision_rule"]["max_context_ratio_vs_baseline"])
    baseline_context = b.get("context_bytes_per_useful_consumed_packet")
    challenger_context = c.get("context_bytes_per_useful_consumed_packet")
    if baseline_context in (None, 0) or challenger_context is None:
        context_rule: bool | str = "UNKNOWN"
    else:
        context_rule = float(challenger_context) <= max_ratio * float(baseline_context)

    existing = c.get("existing_tool_regression_count")
    existing_rule: bool | str = "UNKNOWN" if existing == "UNKNOWN" else int(existing) == 0
    criteria: dict[str, bool | str] = {
        "missed_delta_non_regression": float(c["missed_material_delta_rate"]) <= float(b["missed_material_delta_rate"]),
        "duplicate_non_regression": int(c["accidental_duplicate_action_count"]) <= int(b["accidental_duplicate_action_count"]),
        "scripted_reverse_correction_reach": float(c["correction_reach"]) == 1.0,
        "no_stale_or_scope_invalid_presentations": int(c["stale_or_scope_invalid_presentation_count"]) == 0,
        "no_existing_tool_regression": existing_rule,
        "routine_fast_plane_zero_git_writes": int(c["durable_coordination_git_write_count"]) == 0,
        "bounded_context_ratio": context_rule,
        "strict_primary_improvement": (
            float(c["missed_material_delta_rate"]) < float(b["missed_material_delta_rate"])
            or int(c["accidental_duplicate_action_count"]) < int(b["accidental_duplicate_action_count"])
            or (
                c["time_to_first_useful_sibling_discovery"] is not None
                and b["time_to_first_useful_sibling_discovery"] is not None
                and float(c["time_to_first_useful_sibling_discovery"]) < float(b["time_to_first_useful_sibling_discovery"])
            )
        ),
    }
    if any(value is False for value in criteria.values()):
        status = "FAIL"
    elif any(value == "UNKNOWN" for value in criteria.values()):
        status = "PARTIAL_UNKNOWN"
    else:
        status = "PASS"
    return {
        "status": status,
        "criteria": criteria,
        "primary_deltas": {
            "missed_material_delta_rate": float(c["missed_material_delta_rate"]) - float(b["missed_material_delta_rate"]),
            "accidental_duplicate_action_count": int(c["accidental_duplicate_action_count"]) - int(b["accidental_duplicate_action_count"]),
            "discovery_latency": (
                None
                if c["time_to_first_useful_sibling_discovery"] is None or b["time_to_first_useful_sibling_discovery"] is None
                else float(c["time_to_first_useful_sibling_discovery"]) - float(b["time_to_first_useful_sibling_discovery"])
            ),
            "correction_reach": float(c["correction_reach"]) - float(b["correction_reach"]),
        },
        "interpretation_ceiling": "MATCHED_DETERMINISTIC_FIXTURE_DIFFERENCE_NOT_GENERAL_CAUSAL_EFFECT",
    }


def run_experiment(path: str | Path | None = None, *, parent_ci_green: bool = False) -> dict[str, Any]:
    fixture = load_fixture(path)
    fixture_digest = _digest(fixture)
    baseline = run_baseline(fixture, parent_ci_green=parent_ci_green)
    challenger = run_challenger(fixture, parent_ci_green=parent_ci_green)
    comparison = compare(fixture, baseline, challenger)
    return {
        "artifact": "ATHENA.LIMINAL.BEACON.EFFECT.EXPERIMENT.V1",
        "fixture_digest": fixture_digest,
        "parent_candidate_head": fixture["parent_candidate_head"],
        "parent_runtime_base": fixture["parent_runtime_base"],
        "parent_ci_green": bool(parent_ci_green),
        "baseline": baseline,
        "challenger": challenger,
        "comparison": comparison,
        "firewalls": list(fixture.get("firewalls") or []),
    }


def main() -> int:
    result = run_experiment(parent_ci_green=True)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
