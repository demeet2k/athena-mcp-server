from __future__ import annotations

"""Deterministic held-out replication matrix for Liminal Beacon V1.1.

The matrix is frozen by issue #306 before results.  Each scenario receives a
fresh process-local runtime and returns a typed metric/criteria/trace packet.
This is deterministic fixture evidence only; it does not simulate independent
hidden processes or establish generalized causal effect.
"""

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "liminal_beacon_v11_heldout_matrix.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass
class Clock:
    value: float = 1000.0

    def __call__(self) -> float:
        return float(self.value)

    def tick(self, amount: float = 1.0) -> None:
        self.value += float(amount)


class DummyServer:
    git = None


def _fresh(start: float = 1000.0) -> tuple[LiminalBeaconMeshRuntime, Clock]:
    clock = Clock(start)
    return LiminalBeaconMeshRuntime(DummyServer(), clock=clock), clock


def _packet(view: dict[str, Any] | None, packet_id: str) -> dict[str, Any] | None:
    if not isinstance(view, dict):
        return None
    return next((row for row in (view.get("packets") or []) if row.get("packet_id") == packet_id), None)


def _all_packet_ids(view: dict[str, Any] | None) -> set[str]:
    if not isinstance(view, dict):
        return set()
    return {str(row.get("packet_id")) for row in (view.get("packets") or []) if row.get("packet_id")}


def _trace(rows: list[dict[str, Any]], clock: Clock, action: str, **details: Any) -> None:
    rows.append({"t": float(clock.value), "action": action, **details})


def _receipt_exists(mesh: LiminalBeaconMeshRuntime, agent_id: str, packet_id: str) -> bool:
    return bool(mesh._receipt_stage(agent_id, packet_id))


def _state_metrics(mesh: LiminalBeaconMeshRuntime) -> dict[str, Any]:
    return dict(mesh.state().get("metrics") or {})


def _common_metrics(
    mesh: LiminalBeaconMeshRuntime,
    views: list[dict[str, Any]],
    *,
    parent_ci_green: bool,
    false_presented_receipt_count: int = 0,
    full_result_leak_count: int = 0,
    evidence_ceiling_violation_count: int = 0,
    reverse_correction_reach: Any = "UNKNOWN",
) -> dict[str, Any]:
    state = mesh.state()
    raw = dict(state.get("metrics") or {})
    receipt_rows = state.get("receipts") or []
    consumed = sum(1 for row in receipt_rows if row.get("stage") != "PRESENTED")
    budgets = [int(view.get("context_budget") or 0) for view in views if int(view.get("context_budget") or 0) > 0]
    used = [int(view.get("context_used") or 0) for view in views]
    reserve = [int(view.get("critical_reserve_used") or 0) for view in views]
    return {
        "packets_emitted": int(raw.get("emitted", 0)),
        "packets_presented": int(raw.get("presented", 0)),
        "packets_consumed": consumed,
        "backpressure_filtered_count": int(raw.get("backpressure_filtered", 0)),
        "scope_filtered_count": int(raw.get("scope_filtered", 0)),
        "context_budget_filtered_count": int(raw.get("context_budget_filtered", 0)),
        "critical_reserve_used": max(reserve or [0]),
        "context_used_max": max(used or [0]),
        "context_budget_min": min(budgets or [0]),
        "hard_context_budget_preserved": all(
            int(view.get("context_used") or 0) <= int(view.get("context_budget") or 0)
            for view in views
            if int(view.get("context_budget") or 0) > 0
        ),
        "reverse_correction_reach": reverse_correction_reach,
        "false_presented_receipt_count": int(false_presented_receipt_count),
        "full_result_leak_count": int(full_result_leak_count),
        "evidence_ceiling_violation_count": int(evidence_ceiling_violation_count),
        "durable_coordination_git_write_count": int(raw.get("durable_bridges", 0)),
        "existing_tool_regression_count": 0 if parent_ci_green else "UNKNOWN",
        "hidden_process_count": state.get("hidden_process_count", "UNKNOWN"),
        "independent_process_count": state.get("independent_process_count", "UNKNOWN"),
    }


def _status(criteria: dict[str, Any]) -> str:
    known = [value for value in criteria.values() if value != "UNKNOWN"]
    if any(value is False for value in known):
        return "FAIL"
    if any(value == "UNKNOWN" for value in criteria.values()):
        return "UNKNOWN"
    return "PASS" if all(value is True for value in known) else "FAIL"


def _finalize(
    scenario_id: str,
    cfg: dict[str, Any],
    shared: dict[str, Any],
    metrics: dict[str, Any],
    criteria: dict[str, Any],
    trace: list[dict[str, Any]],
    views: list[dict[str, Any]],
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "name": cfg["name"],
        "fixture_digest": _digest(cfg),
        "treatment_digest": _digest({"shared": shared, "scenario": scenario_id}),
        "metrics": {"scenario_id": scenario_id, **metrics},
        "criteria": criteria,
        "status": _status(criteria),
        "trace": trace,
        "rendezvous_accounting": [
            {
                "context_used": int(view.get("context_used") or 0),
                "context_budget": int(view.get("context_budget") or 0),
                "critical_reserve_used": int(view.get("critical_reserve_used") or 0),
                "critical_quota": int(view.get("critical_quota") or 0),
                "backpressure_filtered": list(view.get("backpressure_filtered") or []),
                "scope_filtered": list(view.get("scope_filtered") or []),
                "context_budget_filtered": list(view.get("context_budget_filtered") or []),
            }
            for view in views
        ],
        "details": details or {},
    }


def _h0(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1000)
    trace: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []
    mesh.touch("A", work_refs=[cfg["a_work"]], object_refs=[cfg["a_object"]])
    mesh.touch("B", work_refs=[cfg["b_work"]], object_refs=[cfg["b_object"]])
    result = {"status": "OK", "event": "H0", "domain_value": {"answer": 7}}
    before = copy.deepcopy(result)
    after = mesh.auto_after_tool("heldout_h0", {"agent_id": "A", "task": "alpha", "oid": "X"}, result)
    pid = str(((after or {}).get("emitted") or {}).get("packet_id") or "")
    clock.tick()
    view1 = mesh.rendezvous("B", threshold=0.35, scout_quota=0, critical_quota=1)
    clock.tick()
    view2 = mesh.rendezvous("B", threshold=0.35, scout_quota=0, critical_quota=1)
    views += [view1, view2]
    domain_preserved = result == before
    absent = pid not in _all_packet_ids(view1) | _all_packet_ids(view2)
    no_receipt = not _receipt_exists(mesh, "B", pid)
    _trace(trace, clock, "UNRELATED_NEGATIVE_CONTROL", packet_id=pid, absent=absent, domain_preserved=domain_preserved)
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green)
    criteria = {
        "unrelated_packet_absent": absent,
        "no_false_cognition_receipt": no_receipt,
        "domain_output_preserved": domain_preserved,
        "hard_context_budget": metrics["hard_context_budget_preserved"],
        "no_fast_git_writes": metrics["durable_coordination_git_write_count"] == 0,
    }
    return _finalize("H0", cfg, shared, metrics, criteria, trace, views, details={"packet_id": pid})


def _h1(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1100)
    trace: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []
    mesh.touch("A", dependency_refs=[cfg["dependency_shared"]])
    mesh.touch("B", dependency_refs=[cfg["dependency_initial"]])
    d1 = mesh.emit("A", "DISCOVERY", "heldout dependency D1", dependency_refs=[cfg["dependency_shared"]], changed_refs=["event:H1-D1"], urgency=0.6, novelty=0.7)["packet"]
    clock.tick(5)
    mesh.touch("B", dependency_refs=[cfg["dependency_shared"]])
    discover = mesh.rendezvous("B", scout_quota=0, critical_quota=1)
    views.append(discover)
    d1_seen = _packet(discover, d1["packet_id"])
    if d1_seen:
        mesh.receipt("B", d1["packet_id"], "CONSUMED", consumer_ref="H1:B:D1")
        mesh.receipt("B", d1["packet_id"], "INCORPORATED", disposition="ACCEPTED")
    mesh.touch("B", dependency_refs=[cfg["dependency_after"]])
    clock.tick(5)
    value = {
        "status": "STALE",
        "event": "H1-C1",
        "secret_body": "H1_FULL_RESULT_MUST_NOT_LEAK",
        "_liminal_publish": {
            "message_class": "CORRECTION",
            "summary": "heldout dependency D1 correction",
            "payload_ref": "event:H1-C1",
            "changed_refs": ["event:H1-C1"],
            "correction_of": d1["packet_id"],
        },
    }
    correction = mesh.auto_after_tool("heldout_h1_fix", {"agent_id": "A", "source_ref": cfg["dependency_shared"]}, value)
    c1 = dict((correction or {}).get("emitted") or {})
    clock.tick()
    reverse_view = mesh.rendezvous("B", threshold=0.95, scout_quota=0, critical_quota=1)
    views.append(reverse_view)
    c1_seen = _packet(reverse_view, str(c1.get("packet_id") or ""))
    reverse = bool(c1_seen and c1_seen.get("reverse_route"))
    if c1_seen:
        mesh.receipt("B", c1["packet_id"], "CONSUMED", consumer_ref="H1:B:C1")
    full_leak = int("H1_FULL_RESULT_MUST_NOT_LEAK" in json.dumps(c1, sort_keys=True))
    ceiling_violation = int(c1.get("evidence_ceiling") != shared["semantic_evidence_ceiling"])
    _trace(trace, clock, "DEPENDENCY_LATE_DISCOVERY", d1_seen=bool(d1_seen), c1_reverse=reverse)
    metrics = _common_metrics(
        mesh,
        views,
        parent_ci_green=parent_ci_green,
        full_result_leak_count=full_leak,
        evidence_ceiling_violation_count=ceiling_violation,
        reverse_correction_reach=1.0 if reverse else 0.0,
    )
    criteria = {
        "late_dependency_discovery": bool(d1_seen),
        "explicit_consumption_required": bool(d1_seen and mesh._reverse_consumers.get(d1["packet_id"]) == {"B"}),
        "reverse_correction_after_departure": reverse,
        "correction_reach_one": metrics["reverse_correction_reach"] == 1.0,
        "no_full_result_leak": full_leak == 0,
        "evidence_ceiling_fixed": ceiling_violation == 0,
        "hard_context_budget": metrics["hard_context_budget_preserved"],
    }
    return _finalize("H1", cfg, shared, metrics, criteria, trace, views, details={"d1": d1["packet_id"], "c1": c1.get("packet_id")})


def _h2(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1200)
    trace: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []
    mesh.touch("A", work_refs=[cfg["work_shared"]], semantic_tags=[cfg["semantic_shared"]], party_refs=[cfg["guild_a"]])
    mesh.touch("B", work_refs=["work:other"], semantic_tags=["semantic:other"], party_refs=[cfg["guild_b"]])
    mesh.touch("X", work_refs=[cfg["work_shared"]], semantic_tags=[cfg["semantic_shared"]], party_refs=[cfg["guild_a"]])
    d1 = mesh.emit("A", "DISCOVERY", "heldout multiplex D1", work_refs=[cfg["work_shared"]], semantic_tags=[cfg["semantic_shared"]], changed_refs=["event:H2-D1"], urgency=0.5, novelty=0.7)["packet"]
    guild = mesh.emit("X", "RESULT", "guild-only noise", work_refs=[cfg["work_shared"]], semantic_tags=[cfg["semantic_shared"]], party_refs=[cfg["guild_a"]], visibility="GUILD", urgency=0.9, novelty=0.9)["packet"]
    clock.tick(3)
    mesh.touch("B", work_refs=[cfg["work_shared"]], semantic_tags=[cfg["semantic_shared"]], party_refs=[cfg["guild_b"]])
    first = mesh.rendezvous("B", scout_quota=0, critical_quota=1)
    views.append(first)
    clock.tick()
    second = mesh.rendezvous("B", scout_quota=0, critical_quota=1)
    views.append(second)
    d1_first = _packet(first, d1["packet_id"])
    d1_second = _packet(second, d1["packet_id"])
    guild_leak = _packet(first, guild["packet_id"]) or _packet(second, guild["packet_id"])
    scope_filtered = guild["packet_id"] in set(first.get("scope_filtered") or []) | set(second.get("scope_filtered") or [])
    false_receipts = int(_receipt_exists(mesh, "B", guild["packet_id"]))
    _trace(trace, clock, "MULTIPLEX_LATE_DISCOVERY", first=bool(d1_first), repeated=bool(d1_second), guild_leak=bool(guild_leak))
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green, false_presented_receipt_count=false_receipts)
    criteria = {
        "late_multiplex_discovery": bool(d1_first),
        "no_duplicate_presentation": d1_second is None,
        "guild_packet_did_not_leak": guild_leak is None,
        "guild_packet_scope_filtered": scope_filtered,
        "no_false_scope_receipt": false_receipts == 0,
        "hard_context_budget": metrics["hard_context_budget_preserved"],
    }
    return _finalize("H2", cfg, shared, metrics, criteria, trace, views, details={"d1": d1["packet_id"], "guild": guild["packet_id"]})


def _h3(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1300)
    trace: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []
    obj = cfg["object"]
    mesh.touch("A", object_refs=[obj])
    mesh.touch("B", object_refs=[obj])
    ordinary = mesh.emit("A", "RESULT", "ordinary low", object_refs=[obj], urgency=0.0, novelty=0.0)["packet"]
    blockers = []
    for index, (urgency, novelty) in enumerate(zip(cfg["blocker_urgencies"], cfg["blocker_novelties"]), start=1):
        blockers.append(mesh.emit("A", "BLOCKER", f"blocker-{index}", object_refs=[obj], urgency=urgency, novelty=novelty)["packet"])
    direct = mesh.emit("A", "RESULT", "direct ordinary", object_refs=[obj], recipients=["B"], urgency=0.0, novelty=0.0)["packet"]
    first = mesh.rendezvous("B", threshold=shared["overloaded_threshold"], scout_quota=0, critical_quota=1, context_budget=shared["context_budget"], limit=16)
    views.append(first)
    first_ids = _all_packet_ids(first)
    reserve_ids = list(first.get("critical_reserve_packet_ids") or [])
    admitted = reserve_ids[0] if reserve_ids else None
    expected = blockers[0]["packet_id"]
    filtered = set(first.get("backpressure_filtered") or [])
    false_receipts = sum(int(_receipt_exists(mesh, "B", pid)) for pid in filtered)
    clock.tick()
    second = mesh.rendezvous("B", threshold=shared["overloaded_threshold"], scout_quota=0, critical_quota=1, context_budget=shared["context_budget"], limit=16)
    views.append(second)
    repeated_first = expected in _all_packet_ids(second)
    _trace(trace, clock, "CRITICAL_BURST", admitted=admitted, expected=expected, repeated_first=repeated_first)
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green, false_presented_receipt_count=false_receipts)
    criteria = {
        "reserve_used_exactly_one_first_view": int(first.get("critical_reserve_used") or 0) == 1,
        "highest_ranked_blocker_reserved": admitted == expected,
        "ordinary_low_filtered": ordinary["packet_id"] in filtered,
        "direct_low_filtered": direct["packet_id"] in filtered,
        "excess_blockers_filtered": all(row["packet_id"] in filtered for row in blockers[1:]),
        "no_duplicate_first_reserve": not repeated_first,
        "no_false_filtered_receipts": false_receipts == 0,
        "reserve_never_exceeds_quota": all(int(view.get("critical_reserve_used") or 0) <= 1 for view in views),
        "hard_context_budget": metrics["hard_context_budget_preserved"],
    }
    return _finalize("H3", cfg, shared, metrics, criteria, trace, views, details={"first_presented": sorted(first_ids), "reserve_ids": reserve_ids})


def _h4(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1400)
    trace: list[dict[str, Any]] = []
    obj = cfg["object"]
    mesh.touch("A", object_refs=[obj])
    mesh.touch("B", object_refs=[obj])
    blocker = mesh.emit("A", "BLOCKER", "X" * int(cfg["summary_size"]), object_refs=[obj], urgency=0.0, novelty=0.0)["packet"]
    view = mesh.rendezvous("B", threshold=shared["overloaded_threshold"], scout_quota=0, critical_quota=1, context_budget=int(cfg["context_budget"]), limit=8)
    views = [view]
    present = _packet(view, blocker["packet_id"])
    budget_filtered = blocker["packet_id"] in set(view.get("context_budget_filtered") or [])
    false_receipts = int(_receipt_exists(mesh, "B", blocker["packet_id"]))
    _trace(trace, clock, "TINY_CONTEXT", presented=bool(present), budget_filtered=budget_filtered)
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green, false_presented_receipt_count=false_receipts)
    criteria = {
        "hard_budget": metrics["hard_context_budget_preserved"],
        "oversized_critical_absent": present is None,
        "typed_context_budget_filter": budget_filtered,
        "no_false_presented_receipt": false_receipts == 0,
        "reserve_counts_only_survivors": int(view.get("critical_reserve_used") or 0) == 0,
    }
    return _finalize("H4", cfg, shared, metrics, criteria, trace, views, details={"blocker": blocker["packet_id"]})


def _h5(cfg, shared, parent_ci_green):
    trace: list[dict[str, Any]] = []
    case_results = []
    full_leaks = 0
    ceiling_violations = 0
    packet_emissions = 0
    for name, envelope in (
        ("unknown_key", {"message_class": "RESULT", "summary": "x", "unexpected": "reject"}),
        ("missing_correction", {"message_class": "CORRECTION", "summary": "x"}),
        ("evidence_escalation", {"message_class": "RESULT", "summary": "x", "evidence_ceiling": "VERIFIED_TRUTH"}),
    ):
        mesh, clock = _fresh(1500 + len(case_results) * 10)
        mesh.touch("A", object_refs=[cfg["object"]])
        value = {"status": "OK", "event": f"H5:{name}", "domain_value": name, "_liminal_publish": envelope}
        before = copy.deepcopy(value)
        result = mesh.auto_after_tool("heldout_h5", {"agent_id": "A", "oid": "semantic-guard"}, value)
        state = mesh.state(include_packets=True)
        emitted = (result or {}).get("emitted")
        packet_emissions += int(state.get("packet_count") or 0)
        text = json.dumps(state, sort_keys=True)
        full_leaks += int("VERIFIED_TRUTH" in text)
        ceiling_violations += sum(int((row.get("evidence_ceiling") or "") not in {"", shared["semantic_evidence_ceiling"]}) for row in (state.get("packets") or []))
        ok = (
            emitted is None
            and "SEMANTIC_ENVELOPE_HOLD" in str((result or {}).get("semantic_error") or "")
            and value == before
            and int(state.get("packet_count") or 0) == 0
        )
        case_results.append({"case": name, "ok": ok, "semantic_error": (result or {}).get("semantic_error")})
        _trace(trace, clock, "MALFORMED_SEMANTIC", case=name, ok=ok)
    metrics = {
        "packets_emitted": packet_emissions,
        "packets_presented": 0,
        "packets_consumed": 0,
        "backpressure_filtered_count": 0,
        "scope_filtered_count": 0,
        "context_budget_filtered_count": 0,
        "critical_reserve_used": 0,
        "context_used_max": 0,
        "context_budget_min": 0,
        "hard_context_budget_preserved": True,
        "reverse_correction_reach": "UNKNOWN",
        "false_presented_receipt_count": 0,
        "full_result_leak_count": full_leaks,
        "evidence_ceiling_violation_count": ceiling_violations,
        "durable_coordination_git_write_count": 0,
        "existing_tool_regression_count": 0 if parent_ci_green else "UNKNOWN",
        "hidden_process_count": "UNKNOWN",
        "independent_process_count": "UNKNOWN",
    }
    criteria = {
        "all_malformed_cases_hold": all(row["ok"] for row in case_results),
        "no_fallback_generic_packet": packet_emissions == 0,
        "no_evidence_escalation": ceiling_violations == 0 and full_leaks == 0,
        "underlying_results_preserved": all(row["ok"] for row in case_results),
    }
    return _finalize("H5", cfg, shared, metrics, criteria, trace, [], details={"cases": case_results})


def _h6(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1600)
    trace: list[dict[str, Any]] = []
    obj = cfg["object"]
    mesh.touch("A", object_refs=[obj], party_refs=[cfg["guild_a"]], visibility="COLONY")
    mesh.touch("B", object_refs=[obj], party_refs=[cfg["guild_b"]], visibility="COLONY")
    packet = mesh.emit("A", "RESULT", "guild-only", object_refs=[obj], party_refs=[cfg["guild_a"]], visibility="GUILD", urgency=1.0, novelty=1.0)["packet"]
    view = mesh.rendezvous("B", threshold=0.0, scout_quota=0, critical_quota=1)
    views = [view]
    packet_absent = _packet(view, packet["packet_id"]) is None
    scope_filtered = packet["packet_id"] in set(view.get("scope_filtered") or [])
    neighbor_present = any(row.get("agent_id") == "A" for row in (view.get("neighbors") or []))
    false_receipts = int(_receipt_exists(mesh, "B", packet["packet_id"]))
    _trace(trace, clock, "GUILD_ISOLATION", packet_absent=packet_absent, neighbor_present=neighbor_present)
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green, false_presented_receipt_count=false_receipts)
    criteria = {
        "guild_packet_absent": packet_absent,
        "guild_packet_scope_filtered": scope_filtered,
        "colony_presence_visible": neighbor_present,
        "no_false_scope_receipt": false_receipts == 0,
        "hard_context_budget": metrics["hard_context_budget_preserved"],
    }
    return _finalize("H6", cfg, shared, metrics, criteria, trace, views, details={"packet": packet["packet_id"]})


def _h7(cfg, shared, parent_ci_green):
    mesh, clock = _fresh(1700)
    trace: list[dict[str, Any]] = []
    obj = cfg["object"]
    mesh.touch("A", object_refs=[obj])
    mesh.touch("B", object_refs=[obj])
    unaddressed = mesh.emit("A", "RESULT", "unaddressed local", object_refs=[obj], visibility="LOCAL", urgency=cfg["unaddressed_urgency"], novelty=cfg["unaddressed_novelty"])["packet"]
    addressed = mesh.emit("A", "RESULT", "addressed local low", object_refs=[obj], visibility="LOCAL", recipients=["B"], urgency=cfg["addressed_urgency"], novelty=cfg["addressed_novelty"])["packet"]
    view = mesh.rendezvous("B", threshold=float(cfg["attention_threshold"]), scout_quota=0, critical_quota=1, context_budget=shared["context_budget"], limit=8)
    views = [view]
    scope_filtered = set(view.get("scope_filtered") or [])
    bp_filtered = set(view.get("backpressure_filtered") or [])
    false_receipts = sum(int(_receipt_exists(mesh, "B", pid)) for pid in (unaddressed["packet_id"], addressed["packet_id"]))
    _trace(trace, clock, "LOCAL_SPAM_CONTROL", scope_filtered=sorted(scope_filtered), backpressure_filtered=sorted(bp_filtered))
    metrics = _common_metrics(mesh, views, parent_ci_green=parent_ci_green, false_presented_receipt_count=false_receipts)
    criteria = {
        "unaddressed_local_scope_filtered": unaddressed["packet_id"] in scope_filtered,
        "addressed_local_attention_filtered": addressed["packet_id"] in bp_filtered,
        "no_local_packet_presented": not (_packet(view, unaddressed["packet_id"]) or _packet(view, addressed["packet_id"])),
        "ordinary_direct_did_not_use_reserve": int(view.get("critical_reserve_used") or 0) == 0,
        "no_false_filtered_receipts": false_receipts == 0,
        "hard_context_budget": metrics["hard_context_budget_preserved"],
    }
    return _finalize("H7", cfg, shared, metrics, criteria, trace, views, details={"unaddressed": unaddressed["packet_id"], "addressed": addressed["packet_id"]})


def _explicit_packet(cfg: dict[str, Any]) -> str:
    mesh, _clock = _fresh(1800)
    mesh.touch("A", instance_id="fixture", session_epoch=cfg["explicit_epoch"], object_refs=[cfg["object"]])
    return mesh.emit("A", "RESULT", "explicit deterministic replay", object_refs=[cfg["object"]], urgency=0.5, novelty=0.5)["packet"]["packet_id"]


def _h8(cfg, shared, parent_ci_green):
    trace: list[dict[str, Any]] = []
    pid1 = _explicit_packet(cfg)
    pid2 = _explicit_packet(cfg)
    mesh, clock = _fresh(1810)
    first = mesh.touch("A", instance_id=cfg["instance_a"], object_refs=[cfg["object"]])["presence"]
    marker1 = mesh.emit("A", "RESULT", "implicit restart marker", object_refs=[cfg["object"]])["packet"]
    second = mesh.touch("A", instance_id=cfg["instance_b"], object_refs=[cfg["object"]])["presence"]
    marker2 = mesh.emit("A", "RESULT", "implicit restart marker", object_refs=[cfg["object"]])["packet"]
    state = mesh.state()
    explicit_equal = pid1 == pid2
    implicit_rotated = first.get("session_epoch") != second.get("session_epoch") and marker1.get("packet_id") != marker2.get("packet_id")
    no_semantic_correction = all(not row.get("correction_of") and not row.get("retraction_of") for row in mesh._packets.values())
    _trace(trace, clock, "RESTART_REPLAY", explicit_equal=explicit_equal, implicit_rotated=implicit_rotated)
    metrics = _common_metrics(mesh, [], parent_ci_green=parent_ci_green)
    criteria = {
        "explicit_identity_deterministic": explicit_equal,
        "implicit_epoch_rotated": implicit_rotated,
        "hidden_process_count_unknown": state.get("hidden_process_count") == "UNKNOWN",
        "independent_process_count_unknown": state.get("independent_process_count") == "UNKNOWN",
        "restart_did_not_invent_correction": no_semantic_correction,
        "no_fast_git_writes": metrics["durable_coordination_git_write_count"] == 0,
    }
    return _finalize("H8", cfg, shared, metrics, criteria, trace, [], details={"explicit_packet_1": pid1, "explicit_packet_2": pid2})


SCENARIOS: dict[str, Callable[[dict[str, Any], dict[str, Any], bool], dict[str, Any]]] = {
    "H0": _h0,
    "H1": _h1,
    "H2": _h2,
    "H3": _h3,
    "H4": _h4,
    "H5": _h5,
    "H6": _h6,
    "H7": _h7,
    "H8": _h8,
}


def run_matrix(*, parent_ci_green: bool) -> dict[str, Any]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    shared = fixture["shared"]
    results = {
        scenario_id: SCENARIOS[scenario_id](fixture["scenarios"][scenario_id], shared, parent_ci_green)
        for scenario_id in fixture["aggregate_rule"]["required_scenarios"]
    }
    metrics = [row["metrics"] for row in results.values()]
    any_fail = any(row["status"] == "FAIL" for row in results.values())
    any_unknown = any(row["status"] == "UNKNOWN" for row in results.values())
    full_leaks = sum(int(row["full_result_leak_count"]) for row in metrics)
    evidence_violations = sum(int(row["evidence_ceiling_violation_count"]) for row in metrics)
    false_receipts = sum(int(row["false_presented_receipt_count"]) for row in metrics)
    git_writes = sum(int(row["durable_coordination_git_write_count"]) for row in metrics)
    max_reserve = max(int(row["critical_reserve_used"]) for row in metrics)
    hard_budget = all(bool(row["hard_context_budget_preserved"]) for row in metrics)
    existing = 0 if parent_ci_green else "UNKNOWN"
    rule = fixture["aggregate_rule"]
    aggregate_criteria = {
        "all_required_scenarios_pass": not any_fail and not any_unknown,
        "zero_full_result_leaks": full_leaks <= int(rule["max_full_result_leaks"]),
        "zero_evidence_ceiling_violations": evidence_violations <= int(rule["max_evidence_ceiling_violations"]),
        "zero_false_presented_receipts": false_receipts <= int(rule["max_false_presented_receipts"]),
        "existing_tool_regressions": existing == int(rule["max_existing_tool_regressions"]) if existing != "UNKNOWN" else "UNKNOWN",
        "zero_fast_git_writes": git_writes <= int(rule["max_routine_fast_plane_git_writes"]),
        "hard_context_budget_everywhere": hard_budget,
        "critical_reserve_bounded": max_reserve <= int(rule["max_critical_reserve_used"]),
    }
    aggregate_status = _status(aggregate_criteria)
    return {
        "schema": fixture["schema"],
        "standing": fixture["evidence_ceiling_after_pass"],
        "fixture_digest": _digest(fixture),
        "parent_candidate_head": fixture["parent_candidate_head"],
        "parent_runtime_base": fixture["parent_runtime_base"],
        "parent_ci_green": bool(parent_ci_green),
        "scenarios": results,
        "aggregate": {
            "status": aggregate_status,
            "criteria": aggregate_criteria,
            "full_result_leak_count": full_leaks,
            "evidence_ceiling_violation_count": evidence_violations,
            "false_presented_receipt_count": false_receipts,
            "durable_coordination_git_write_count": git_writes,
            "existing_tool_regression_count": existing,
            "max_critical_reserve_used": max_reserve,
            "hard_context_budget_preserved": hard_budget,
        },
        "firewalls": fixture["firewalls"],
    }


if __name__ == "__main__":
    print(json.dumps(run_matrix(parent_ci_green=True), indent=2, sort_keys=True))
