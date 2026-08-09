from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server
from athena_mcp.tse_telemetry import TseHelixTelemetryRuntime


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path):
    a = base / "a"
    a.mkdir()
    _run(a, "init", "-b", "master")
    _run(a, "config", "user.name", "a")
    _run(a, "config", "user.email", "a@example.invalid")
    (a / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(a, "add", ".")
    _run(a, "commit", "-m", "seed")
    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(a, "remote", "add", "origin", str(origin))
    _run(a, "push", "-u", "origin", "master")
    b = base / "b"
    proc = subprocess.run(["git", "clone", str(origin), str(b)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(b, "config", "user.name", "b")
    _run(b, "config", "user.email", "b@example.invalid")
    return a, b


class TseHelixTelemetryTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        a, b = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=a)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=b)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.seq = 0
        self.mission = "MISSION-HELIX-1"
        self.route = "TSE.ROUTE.TEST1"
        self.hatch = "HATCH-TEST1"

    def rpc(self, server, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server, name, args):
        response = self.rpc(server, "tools/call", {"name": name, "arguments": args})
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def record(self, server, transition, *, parent=None, cost=None, delta=None, child=False, attempt_ref=None, hold_class=None, seam=None, witnesses=None):
        args = {
            "mission_id": self.mission,
            "route_id": self.route,
            "hatch_id": self.hatch,
            "transition": transition,
            "actor_id": "observer",
            "witnesses": witnesses or [f"witness:{transition}"],
            "cost": cost if cost is not None else {"known": True, "total": 1.0},
        }
        if parent is not None:
            args["parent_event_id"] = parent
        if delta is not None:
            args["verified_delta"] = delta
        if child:
            args["child_agent_id"] = "beta"
            args["child_claim_id"] = "CLAIM-BETA"
        if attempt_ref is not None:
            args["attempt_ref"] = attempt_ref
        if hold_class is not None:
            args["hold_class"] = hold_class
        if seam is not None:
            args["seam"] = seam
        return self.tool(server, "athena_tse_telemetry_record", args)

    def chain(self, unknown_cost_at=None):
        transitions = [
            "HATCH_CREATED", "HATCH_NEED_PUBLISHED", "MATCH_FOUND", "HANDOFF_ROUTED",
            "HANDOFF_CONSUMED", "CHILD_CLAIMED", "CHILD_VERIFIED_RETURN", "RETURN_APPLIED",
        ]
        parent = None
        events = []
        for index, transition in enumerate(transitions):
            server = self.a if index % 2 == 0 else self.b
            cost = {"known": False} if transition == unknown_cost_at else {"known": True, "total": 1.0}
            out = self.record(
                server,
                transition,
                parent=parent,
                cost=cost,
                delta=8.0 if transition in {"CHILD_VERIFIED_RETURN", "RETURN_APPLIED"} else None,
                child=transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN", "RETURN_APPLIED"},
            )
            self.assertEqual("TSE_TELEMETRY_RECORDED", out["status"], out)
            parent = out["event"]["event_id"]
            events.append(out["event"])
        return events

    def test_tools_and_resource_registered(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        self.assertIn("athena_tse_telemetry_record", tools)
        self.assertIn("athena_tse_telemetry_report", tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-telemetry/v1", resources)

    def test_cross_clone_parent_lineage_and_exact_replay(self):
        first = self.record(self.a, "HATCH_CREATED")
        second = self.record(self.b, "HATCH_NEED_PUBLISHED", parent=first["event"]["event_id"])
        self.assertEqual("TSE_TELEMETRY_RECORDED", second["status"])
        replay = self.record(self.a, "HATCH_CREATED")
        self.assertEqual("TSE_TELEMETRY_ALREADY_RECORDED", replay["status"])

    def test_changed_same_event_identity_conflicts(self):
        first = self.record(self.a, "HATCH_CREATED")
        self.assertEqual("TSE_TELEMETRY_RECORDED", first["status"])
        changed = self.record(self.b, "HATCH_CREATED", cost={"known": True, "total": 2.0})
        self.assertEqual("TSE_TELEMETRY_EVENT_CONFLICT_HOLD", changed["status"])

    def test_missing_parent_fails_closed(self):
        held = self.record(self.a, "MATCH_FOUND", parent="TSETELEM-MISSING")
        self.assertEqual("TSE_TELEMETRY_PARENT_HOLD", held["status"])
        self.assertEqual("parent_event_missing", held["reason"])

    def test_invalid_parent_transition_fails_closed(self):
        first = self.record(self.a, "HATCH_CREATED")
        held = self.record(self.b, "MATCH_FOUND", parent=first["event"]["event_id"])
        self.assertEqual("parent_transition_invalid", held["reason"])

    def test_partial_funnel_preserves_unknown_denominators(self):
        first = self.record(self.a, "HATCH_CREATED")
        self.record(self.b, "HATCH_NEED_PUBLISHED", parent=first["event"]["event_id"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(0.0, report["metrics"]["eta_match"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_claim"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_return"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_apply"])

    def test_empty_mission_is_unknown_not_zero_efficiency(self):
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": "EMPTY-MISSION"})
        self.assertEqual("UNKNOWN", report["metrics"]["eta_match"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_helix"])

    def test_full_helix_reports_conversion_and_value_efficiency(self):
        self.chain()
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        for key in ("eta_match", "eta_claim", "eta_return", "eta_apply"):
            self.assertEqual(1.0, report["metrics"][key])
        self.assertEqual(1.0, report["metrics"]["eta_helix"])
        self.assertEqual(8.0, report["applied_verified_delta"])
        self.assertEqual(8.0, report["known_cost_total"])
        self.assertFalse(report["causal_promotion_authority"])
        self.assertEqual("UNKNOWN", report["behavioral_treatment_effect"])

    def test_unknown_cost_keeps_eta_helix_unknown(self):
        self.chain(unknown_cost_at="MATCH_FOUND")
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertFalse(report["all_costs_known"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_helix"])

    def test_hold_residual_is_typed_not_counted_as_success(self):
        first = self.record(self.a, "HATCH_CREATED")
        held = self.record(
            self.b,
            "HELIX_HOLD",
            parent=first["event"]["event_id"],
            attempt_ref="attempt-1",
            hold_class="CAPABILITY_HOLD",
            seam="MATCH",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED", held["status"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["residuals"]["CAPABILITY_HOLD"])
        self.assertEqual(0, report["counts"]["MATCH_FOUND"])

    def test_direct_runtime_rejects_private_or_reset_payloads(self):
        runtime = TseHelixTelemetryRuntime(self.a)
        private = runtime.record(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition="HATCH_CREATED",
            actor_id="observer",
            witnesses=["w"],
            cost={"known": True, "total": 1.0, "metadata": {"chain_of_thought": "hidden"}},
        )
        self.assertEqual("EVIDENCE_HOLD", private["hold"])
        reset = runtime.record(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition="HATCH_CREATED",
            actor_id="observer",
            witnesses=["w"],
            cost={"known": True, "total": 1.0, "metadata": {"platform_counter_reset_claimed": True}},
        )
        self.assertEqual("EVIDENCE_HOLD", reset["hold"])

    def test_report_disabled_sync_marks_view_unverified_and_noncausal(self):
        first = self.record(self.a, "HATCH_CREATED")
        self.assertEqual("TSE_TELEMETRY_RECORDED", first["status"])
        report = self.tool(
            self.a,
            "athena_tse_telemetry_report",
            {"mission_id": self.mission, "shared_remote_mode": "DISABLED"},
        )
        self.assertFalse(report["shared_frontier_verified"])
        self.assertFalse(report["causal_promotion_authority"])


if __name__ == "__main__":
    unittest.main()
