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


class TseRouteWindowTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        a, b = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=a)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=b)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.seq = 0
        self.mission = "MISSION-WINDOW-1"
        self.window = "WINDOW-1"

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

    def event(
        self,
        server,
        route,
        transition,
        *,
        parent=None,
        ref=None,
        hold_class=None,
        seam=None,
        child=False,
        delta=None,
        cost=None,
    ):
        ref = ref or f"SRC-{route}-{transition}"
        runtime = TseHelixTelemetryRuntime(server)
        return runtime.record_source_bound(
            mission_id=self.mission,
            route_id=route,
            hatch_id=f"HATCH-{route}",
            transition=transition,
            actor_id="observer",
            witnesses=[f"source:{ref}"],
            cost=cost if cost is not None else {"known": True, "total": 1.0},
            source_kind=f"TEST_{transition}",
            source_ref=ref,
            source_payload={"route": route, "transition": transition, "ref": ref},
            source_git_head="SOURCE-HEAD-STABLE",
            source_authority="TEST_SOURCE",
            parent_event_id=parent,
            child_agent_id=f"child-{route}" if child else None,
            child_claim_id=f"claim-{route}" if child else None,
            verified_delta=delta,
            hold_class=hold_class,
            seam=seam,
            attempt_ref=ref,
        )

    def chain(self, route="R1", through="CHILD_VERIFIED_RETURN"):
        stages = [
            "HATCH_CREATED",
            "HATCH_NEED_PUBLISHED",
            "MATCH_FOUND",
            "HANDOFF_ROUTED",
            "CHILD_CLAIMED",
            "CHILD_VERIFIED_RETURN",
            "RETURN_APPLIED",
        ]
        stop = stages.index(through)
        parent = None
        events = {}
        for index, transition in enumerate(stages[: stop + 1]):
            server = self.a if index % 2 == 0 else self.b
            child = transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN", "RETURN_APPLIED"}
            delta = 5.0 if transition in {"CHILD_VERIFIED_RETURN", "RETURN_APPLIED"} else None
            out = self.event(
                server,
                route,
                transition,
                parent=parent,
                ref=f"SRC-{route}-{index}-{transition}",
                child=child,
                delta=delta,
            )
            self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", out["status"], out)
            parent = out["event"]["event_id"]
            events[transition] = out["event"]
        return events

    def open_window(self, route_ids=None):
        return self.tool(
            self.a,
            "athena_tse_route_window_open",
            {
                "window_id": self.window,
                "mission_id": self.mission,
                "actor_id": "observer",
                **({"route_ids": route_ids} if route_ids is not None else {}),
            },
        )

    def report(self):
        return self.tool(self.a, "athena_tse_route_window_report", {"window_id": self.window})

    def close(self, complete_seams, resolved_routes=None, route_ids=None):
        args = {
            "window_id": self.window,
            "mission_id": self.mission,
            "actor_id": "observer",
            "complete_seams": complete_seams,
        }
        if resolved_routes is not None:
            args["resolved_routes"] = resolved_routes
        if route_ids is not None:
            args["route_ids"] = route_ids
        return self.tool(self.b, "athena_tse_route_window_close", args)

    def test_tools_and_resource_registered(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in {
            "athena_tse_route_window_open",
            "athena_tse_route_window_close",
            "athena_tse_route_window_state",
            "athena_tse_route_window_report",
        }:
            self.assertIn(name, tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-route-window/v1", resources)

    def test_pending_route_is_not_silently_resolved_failure(self):
        events = self.chain("R1", through="HATCH_NEED_PUBLISHED")
        opened = self.open_window()
        self.assertEqual("TSE_ROUTE_WINDOW_OPENED", opened["status"])
        report = self.report()
        match = report["conversions"]["eta_match"]
        self.assertEqual(1, match["eligible_routes"])
        self.assertEqual(0, match["attained_routes"])
        self.assertEqual(1, match["pending_routes"])
        self.assertEqual("UNKNOWN", match["resolved_eta"])
        self.assertEqual(0.0, match["attainment_lower"])
        self.assertEqual(1.0, match["attainment_upper"])

    def test_complete_match_window_converts_pending_to_observed_zero(self):
        self.chain("R1", through="HATCH_NEED_PUBLISHED")
        self.open_window()
        closed = self.close(["MATCH"])
        self.assertEqual("TSE_ROUTE_WINDOW_CLOSED", closed["status"], closed)
        report = self.report()
        match = report["conversions"]["eta_match"]
        self.assertEqual(0, match["pending_routes"])
        self.assertEqual(1, match["mature_routes"])
        self.assertEqual(0.0, match["resolved_eta"])
        self.assertEqual(0.0, match["attainment_upper"])

    def test_retry_events_do_not_inflate_route_conversion(self):
        events = self.chain("R1", through="MATCH_FOUND")
        second = self.event(
            self.b,
            "R1",
            "MATCH_FOUND",
            parent=events["HATCH_NEED_PUBLISHED"]["event_id"],
            ref="SRC-R1-MATCH-RETRY",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", second["status"])
        self.open_window()
        report = self.report()
        self.assertEqual(1, report["stage_route_counts"]["MATCH_FOUND"])
        self.assertEqual(2, report["stage_attempt_counts"]["MATCH_FOUND"])
        self.assertEqual(1, report["retry_pressure"]["MATCH_FOUND"])
        self.assertEqual(1.0, report["conversions"]["eta_match"]["attainment_lower"])

    def test_hold_pressure_and_later_success_are_both_preserved(self):
        root = self.event(self.a, "R1", "HATCH_CREATED", ref="R1-HATCH")
        pub = self.event(self.b, "R1", "HATCH_NEED_PUBLISHED", parent=root["event"]["event_id"], ref="R1-PUB")
        held = self.event(
            self.a,
            "R1",
            "HELIX_HOLD",
            parent=pub["event"]["event_id"],
            ref="R1-MATCH-HOLD",
            hold_class="CAPABILITY_HOLD",
            seam="MATCH",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", held["status"])
        matched = self.event(self.b, "R1", "MATCH_FOUND", parent=pub["event"]["event_id"], ref="R1-MATCH-SUCCESS")
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", matched["status"])
        self.open_window()
        report = self.report()
        self.assertEqual(1, report["hold_pressure"]["MATCH"])
        self.assertEqual(1, report["stage_route_counts"]["MATCH_FOUND"])
        self.assertEqual(1.0, report["conversions"]["eta_match"]["resolved_eta"])

    def test_explicit_resolved_route_matures_without_global_seam_completion(self):
        self.chain("R1", through="HATCH_NEED_PUBLISHED")
        self.chain("R2", through="HATCH_NEED_PUBLISHED")
        self.open_window(route_ids=["R1", "R2"])
        self.close([], resolved_routes={"MATCH": ["R1"]})
        report = self.report()
        match = report["conversions"]["eta_match"]
        self.assertEqual(2, match["eligible_routes"])
        self.assertEqual(1, match["mature_routes"])
        self.assertEqual(1, match["pending_routes"])
        self.assertEqual(0.0, match["resolved_eta"])
        self.assertEqual(0.5, match["attainment_upper"])

    def test_optional_ack_is_side_channel_not_claim_precondition(self):
        events = self.chain("R1", through="CHILD_CLAIMED")
        self.open_window()
        report = self.report()
        self.assertEqual(1.0, report["conversions"]["eta_claim"]["attainment_lower"])
        self.assertEqual(1.0, report["conversions"]["eta_claim_from_handoff"]["attainment_lower"])
        consumption = report["conversions"]["eta_consumption"]
        self.assertEqual(1, consumption["eligible_routes"])
        self.assertEqual(0, consumption["attained_routes"])
        self.assertEqual(1, consumption["pending_routes"])
        self.assertEqual("UNKNOWN", consumption["resolved_eta"])

    def test_apply_absence_is_unknown_until_apply_seam_complete(self):
        self.chain("R1", through="CHILD_VERIFIED_RETURN")
        self.open_window()
        open_report = self.report()
        self.assertEqual("UNAVAILABLE_OR_INCOMPLETE", open_report["apply_channel_state"])
        self.assertEqual("UNKNOWN", open_report["conversions"]["eta_apply"]["resolved_eta"])
        self.close(["APPLY"])
        closed_report = self.report()
        self.assertEqual("COMPLETE_ZERO", closed_report["apply_channel_state"])
        self.assertEqual(0.0, closed_report["conversions"]["eta_apply"]["resolved_eta"])

    def test_applied_return_enables_route_level_eta_helix(self):
        self.chain("R1", through="RETURN_APPLIED")
        self.open_window()
        report = self.report()
        self.assertEqual("OBSERVED", report["apply_channel_state"])
        self.assertEqual(1.0, report["conversions"]["eta_apply"]["resolved_eta"])
        self.assertEqual(5.0, report["applied_verified_delta"])
        self.assertGreater(report["eta_helix"], 0.0)
        self.assertFalse(report["causal_promotion_authority"])
        self.assertEqual("UNKNOWN", report["behavioral_treatment_effect"])

    def test_declared_events_never_enter_route_projection(self):
        self.chain("R1", through="MATCH_FOUND")
        declared = self.tool(
            self.a,
            "athena_tse_telemetry_record",
            {
                "mission_id": self.mission,
                "route_id": "R-DECLARED",
                "hatch_id": "HATCH-DECLARED",
                "transition": "HATCH_CREATED",
                "actor_id": "observer",
                "witnesses": ["manual"],
                "cost": {"known": True, "total": 1.0},
                "attempt_ref": "declared-root",
            },
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_DECLARED", declared["status"])
        self.open_window()
        report = self.report()
        self.assertEqual(1, report["route_count"])
        self.assertEqual(1, report["declared_event_count"])

    def test_window_scope_freezes_at_close(self):
        self.chain("R1", through="MATCH_FOUND")
        self.open_window()
        closed = self.close(["MATCH"])
        self.assertEqual(["R1"], closed["window"]["route_ids"])
        self.chain("R2", through="MATCH_FOUND")
        report = self.report()
        self.assertEqual(1, report["route_count"])
        self.assertEqual(["R1"], [row["route_id"] for row in report["routes"]])

    def test_window_close_is_idempotent_and_scope_drift_conflicts(self):
        self.chain("R1", through="MATCH_FOUND")
        self.open_window(route_ids=["R1"])
        first = self.close(["MATCH"], route_ids=["R1"])
        self.assertEqual("TSE_ROUTE_WINDOW_CLOSED", first["status"])
        replay = self.close(["MATCH"], route_ids=["R1"])
        self.assertEqual("TSE_ROUTE_WINDOW_ALREADY_CLOSED", replay["status"])
        drift = self.close(["MATCH"], route_ids=["R2"])
        self.assertEqual("EVIDENCE_HOLD", drift["hold"])

    def test_unknown_cost_keeps_eta_helix_unknown(self):
        events = self.chain("R1", through="CHILD_VERIFIED_RETURN")
        applied = self.event(
            self.a,
            "R1",
            "RETURN_APPLIED",
            parent=events["CHILD_VERIFIED_RETURN"]["event_id"],
            ref="R1-APPLY-UNKNOWN-COST",
            child=True,
            delta=5.0,
            cost={"known": False},
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", applied["status"])
        self.open_window()
        report = self.report()
        self.assertFalse(report["all_costs_known"])
        self.assertEqual("UNKNOWN", report["eta_helix"])


if __name__ == "__main__":
    unittest.main()
