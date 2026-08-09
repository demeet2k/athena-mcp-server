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

    def declared(self, server, transition, *, parent=None, attempt_ref=None, child=False, delta=None):
        args = {
            "mission_id": self.mission,
            "route_id": self.route,
            "hatch_id": self.hatch,
            "transition": transition,
            "actor_id": "observer",
            "witnesses": [f"declared:{transition}"],
            "cost": {"known": True, "total": 1.0},
        }
        if parent:
            args["parent_event_id"] = parent
        if attempt_ref:
            args["attempt_ref"] = attempt_ref
        if child:
            args["child_agent_id"] = "beta"
            args["child_claim_id"] = "CLAIM-BETA"
        if delta is not None:
            args["verified_delta"] = delta
        return self.tool(server, "athena_tse_telemetry_record", args)

    def source(self, server, transition, *, parent=None, ref=None, child=False, delta=None, cost=None):
        runtime = TseHelixTelemetryRuntime(server)
        ref = ref or f"SRC-{transition}"
        return runtime.record_source_bound(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition=transition,
            actor_id="observer",
            witnesses=[f"source:{transition}"],
            cost=cost if cost is not None else {"known": True, "total": 1.0},
            source_kind=f"TEST_{transition}",
            source_ref=ref,
            source_payload={"transition": transition, "ref": ref},
            source_git_head=server.git.head(),
            source_authority="TEST_SOURCE",
            parent_event_id=parent,
            child_agent_id="beta" if child else None,
            child_claim_id="CLAIM-BETA" if child else None,
            verified_delta=delta,
            attempt_ref=ref,
        )

    def test_tools_and_resource_registered(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        self.assertIn("athena_tse_telemetry_record", tools)
        self.assertIn("athena_tse_telemetry_report", tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-telemetry/v1", resources)

    def test_declared_success_is_audit_visible_but_not_primary_metric(self):
        root = self.declared(self.a, "HATCH_CREATED", attempt_ref="manual-root")
        self.assertEqual("TSE_TELEMETRY_RECORDED_DECLARED", root["status"])
        child = self.declared(
            self.b,
            "HATCH_NEED_PUBLISHED",
            parent=root["event"]["event_id"],
            attempt_ref="manual-publish",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_DECLARED", child["status"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(0, report["counts"]["HATCH_NEED_PUBLISHED"])
        self.assertEqual(1, report["declared_counts"]["HATCH_NEED_PUBLISHED"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_match"])
        self.assertEqual("PRIMARY_METRICS_SOURCE_BOUND_ONLY", report["measurement_standing"])

    def test_source_bound_child_cannot_parent_declared_event(self):
        root = self.declared(self.a, "HATCH_CREATED", attempt_ref="manual-root")
        held = self.source(
            self.b,
            "HATCH_NEED_PUBLISHED",
            parent=root["event"]["event_id"],
            ref="SRC-PUBLISH-1",
        )
        self.assertEqual("TSE_TELEMETRY_PARENT_HOLD", held["status"])
        self.assertEqual("source_bound_child_requires_source_bound_parent", held["reason"])

    def test_source_bound_cross_clone_chain_counts_primary_metrics(self):
        root = self.source(self.a, "HATCH_CREATED", ref="SRC-HATCH")
        published = self.source(
            self.b,
            "HATCH_NEED_PUBLISHED",
            parent=root["event"]["event_id"],
            ref="SRC-PUBLISH",
        )
        matched = self.source(
            self.a,
            "MATCH_FOUND",
            parent=published["event"]["event_id"],
            ref="SRC-MATCH",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", matched["status"])
        report = self.tool(self.b, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["counts"]["HATCH_NEED_PUBLISHED"])
        self.assertEqual(1, report["counts"]["MATCH_FOUND"])
        self.assertEqual(1.0, report["metrics"]["eta_match"])
        self.assertEqual(0, report["declared_event_count"])

    def test_full_source_bound_helix_reports_descriptive_efficiency(self):
        chain = [
            ("HATCH_CREATED", False, None),
            ("HATCH_NEED_PUBLISHED", False, None),
            ("MATCH_FOUND", False, None),
            ("HANDOFF_ROUTED", False, None),
            ("HANDOFF_CONSUMED", False, None),
            ("CHILD_CLAIMED", True, None),
            ("CHILD_VERIFIED_RETURN", True, 8.0),
            ("RETURN_APPLIED", True, 8.0),
        ]
        parent = None
        for index, (transition, child, delta) in enumerate(chain):
            server = self.a if index % 2 == 0 else self.b
            out = self.source(
                server,
                transition,
                parent=parent,
                ref=f"SRC-{index}-{transition}",
                child=child,
                delta=delta,
            )
            self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", out["status"], out)
            parent = out["event"]["event_id"]
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        for key in ("eta_match", "eta_claim", "eta_return", "eta_apply"):
            self.assertEqual(1.0, report["metrics"][key])
        self.assertEqual(1.0, report["metrics"]["eta_helix"])
        self.assertEqual("UNKNOWN", report["behavioral_treatment_effect"])
        self.assertFalse(report["causal_promotion_authority"])

    def test_unknown_source_bound_cost_keeps_eta_helix_unknown(self):
        root = self.source(self.a, "HATCH_CREATED", ref="S0")
        pub = self.source(self.b, "HATCH_NEED_PUBLISHED", parent=root["event"]["event_id"], ref="S1")
        match = self.source(self.a, "MATCH_FOUND", parent=pub["event"]["event_id"], ref="S2", cost={"known": False})
        route = self.source(self.b, "HANDOFF_ROUTED", parent=match["event"]["event_id"], ref="S3")
        consumed = self.source(self.a, "HANDOFF_CONSUMED", parent=route["event"]["event_id"], ref="S4")
        claim = self.source(self.b, "CHILD_CLAIMED", parent=consumed["event"]["event_id"], ref="S5", child=True)
        returned = self.source(self.a, "CHILD_VERIFIED_RETURN", parent=claim["event"]["event_id"], ref="S6", child=True, delta=4.0)
        self.source(self.b, "RETURN_APPLIED", parent=returned["event"]["event_id"], ref="S7", child=True, delta=4.0)
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertFalse(report["all_costs_known"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_helix"])

    def test_same_source_bound_identity_is_idempotent_changed_content_conflicts(self):
        first = self.source(self.a, "HATCH_CREATED", ref="SRC-IDEM")
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", first["status"])
        replay = self.source(self.b, "HATCH_CREATED", ref="SRC-IDEM")
        self.assertEqual("TSE_TELEMETRY_ALREADY_RECORDED", replay["status"])
        runtime = TseHelixTelemetryRuntime(self.a)
        changed = runtime.record_source_bound(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition="HATCH_CREATED",
            actor_id="observer",
            witnesses=["source:HATCH_CREATED"],
            cost={"known": True, "total": 2.0},
            source_kind="TEST_HATCH_CREATED",
            source_ref="SRC-IDEM",
            source_payload={"transition": "HATCH_CREATED", "ref": "SRC-IDEM"},
            source_git_head=self.a.git.head(),
            source_authority="TEST_SOURCE",
            attempt_ref="SRC-IDEM",
        )
        self.assertEqual("TSE_TELEMETRY_EVENT_CONFLICT_HOLD", changed["status"])

    def test_private_or_reset_source_payload_fails_closed(self):
        runtime = TseHelixTelemetryRuntime(self.a)
        private = runtime.record_source_bound(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition="HATCH_CREATED",
            actor_id="observer",
            witnesses=["w"],
            cost={"known": True, "total": 1.0},
            source_kind="TEST",
            source_ref="PRIVATE",
            source_payload={"chain_of_thought": "hidden"},
            source_git_head=self.a.git.head(),
            source_authority="TEST",
        )
        self.assertEqual("EVIDENCE_HOLD", private["hold"])
        reset = runtime.record_source_bound(
            mission_id=self.mission,
            route_id=self.route,
            hatch_id=self.hatch,
            transition="HATCH_CREATED",
            actor_id="observer",
            witnesses=["w"],
            cost={"known": True, "total": 1.0},
            source_kind="TEST",
            source_ref="RESET",
            source_payload={"nested": {"platform_counter_reset_claimed": True}},
            source_git_head=self.a.git.head(),
            source_authority="TEST",
        )
        self.assertEqual("EVIDENCE_HOLD", reset["hold"])

    def test_empty_mission_keeps_unknown_denominators(self):
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": "EMPTY-MISSION"})
        self.assertEqual("UNKNOWN", report["metrics"]["eta_match"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_helix"])

    def test_disabled_report_is_explicitly_unverified_and_noncausal(self):
        self.source(self.a, "HATCH_CREATED", ref="SRC-DISABLED")
        report = self.tool(
            self.a,
            "athena_tse_telemetry_report",
            {"mission_id": self.mission, "shared_remote_mode": "DISABLED"},
        )
        self.assertFalse(report["shared_frontier_verified"])
        self.assertFalse(report["causal_promotion_authority"])


if __name__ == "__main__":
    unittest.main()
