from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server
from athena_mcp.tse_population import _digest


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


def hatch():
    checkpoint = {
        "residual": ["execute bounded helical child"],
        "acceptance": ["source-bound claim", "verified child return"],
    }
    checkpoint["checkpoint_digest"] = _digest(checkpoint)
    value = {
        "schema_version": "ATHENA.TSE.HATCH.V2",
        "hatch_id": "HATCH.HELIX.1",
        "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
        "parent_checkpoint": checkpoint,
        "child_quest": {"id": "Q-HELIX-CHILD", "version": "1"},
        "status": "CHILD_ACTIVE",
        "platform_counter_reset_claimed": False,
    }
    value["hatch_digest"] = _digest(value)
    return value


class TseHelixCompositionTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        a, b = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=a)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=b)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0
        self.mission = "MISSION-HELIX-SOURCE-1"

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

    def cost(self):
        return {"known": True, "total": 1.0}

    def open(self):
        return self.tool(
            self.a,
            "athena_tse_helix_open",
            {
                "mission_id": self.mission,
                "hatch": hatch(),
                "parent_agent_id": "alpha",
                "capabilities": ["code", "tests"],
                "actor_id": "observer",
                "witnesses": ["test:hatch"],
                "cost": self.cost(),
                "targets": ["child.py"],
                "dependencies": ["api.ready"],
                "role": "BUILDER",
                "life_policy": "STAY_IN_GAME_LIFE_LOOP_V1",
                "clear_condition_digest": "sha256:criterion",
            },
        )

    def advance(self, server, operation, route, parent, **extra):
        args = {
            "mission_id": self.mission,
            "operation": operation,
            "route": route,
            "parent_event_id": parent,
            "actor_id": "observer",
            "witnesses": [f"test:{operation}"],
            "cost": self.cost(),
        }
        args.update(extra)
        return self.tool(server, "athena_tse_helix_advance", args)

    def present_parent(self):
        out = self.board_a.present(
            agent_id="alpha",
            task="Parent TSE helix",
            work_key="parent-helix",
            targets=["parent.py"],
        )
        self.assertEqual("PRESENT", out["status"], out)

    def offer_beta(self):
        present = self.board_b.present(
            agent_id="beta",
            task="Available helical builder",
            work_key="offer-beta",
            targets=["offer.py"],
        )
        self.assertEqual("PRESENT", present["status"], present)
        offer = self.tool(
            self.b,
            "athena_cohesion_request_offer",
            {
                "request_id": "OFFER.HELIX.BETA",
                "agent_id": "beta",
                "kind": "OFFER",
                "capabilities": ["code", "tests"],
                "goal_ref": "offer.helix",
                "role": "BUILDER",
                "provides": ["api.ready"],
                "capacity_units": 2,
            },
        )
        self.assertEqual("COHESION_OFFER_PUBLISHED", offer["status"], offer)

    def full_to_handoff(self):
        root = self.open()
        self.assertEqual("TSE_HELIX_OPEN", root["status"], root)
        self.present_parent()
        published = self.advance(self.a, "PUBLISH", root["route"], root["root_event_id"])
        self.assertEqual("TSE_HELIX_ADVANCED", published["status"], published)
        self.offer_beta()
        matched = self.advance(self.a, "MATCH", published["route"], published["event_id"], min_score=1)
        self.assertEqual("TSE_HELIX_ADVANCED", matched["status"], matched)
        handed = self.advance(self.a, "HANDOFF", matched["route"], matched["event_id"])
        self.assertEqual("TSE_HELIX_ADVANCED", handed["status"], handed)
        return handed

    def valid_return(self, route):
        return {
            "schema_version": "ATHENA.TSE.RETURN.V2",
            "return_receipt_id": "RET.HELIX.1",
            "hatch_id": route["hatch_id"],
            "hatch_digest": route["hatch_digest"],
            "parent_checkpoint_digest": route["parent_checkpoint_digest"],
            "population_route_id": route["route_id"],
            "population_route_digest": route["route_digest"],
            "child_agent_id": route["child_claim"]["agent_id"],
            "child_claim_id": route["child_claim"]["claim_id"],
            "verified": True,
            "witnesses": ["test:return"],
            "verified_delta": 5.0,
            "child_git_position": {
                "repo": "demeet2k/Athena",
                "ref": "refs/heads/child",
                "head": "b" * 40,
            },
            "platform_counter_reset_claimed": False,
        }

    def test_helix_tools_and_resource_registered(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in {
            "athena_tse_helix_open",
            "athena_tse_helix_advance",
            "athena_tse_helix_observe_consumption",
            "athena_tse_helix_reconcile",
        }:
            self.assertIn(name, tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-helix/v2", resources)

    def test_open_binds_valid_hatch_to_source_bound_root(self):
        opened = self.open()
        self.assertEqual("TSE_HELIX_OPEN", opened["status"])
        self.assertEqual("SOURCE_BOUND", opened["telemetry"]["event"]["source"]["verification"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["counts"]["HATCH_CREATED"])
        self.assertEqual(0, report["declared_event_count"])

    def test_population_hold_becomes_source_bound_residual_not_fake_progress(self):
        opened = self.open()
        held = self.advance(self.a, "PUBLISH", opened["route"], opened["root_event_id"])
        self.assertEqual("TSE_HELIX_POPULATION_HOLD", held["status"])
        self.assertEqual("AUTHORITY_HOLD", held["hold"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["residuals"]["AUTHORITY_HOLD"])
        self.assertEqual(0, report["counts"]["HATCH_NEED_PUBLISHED"])

    def test_real_population_actions_emit_source_bound_success_chain(self):
        handed = self.full_to_handoff()
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["counts"]["HATCH_NEED_PUBLISHED"])
        self.assertEqual(1, report["counts"]["MATCH_FOUND"])
        self.assertEqual(1, report["counts"]["HANDOFF_ROUTED"])
        self.assertEqual(1.0, report["metrics"]["eta_match"])
        self.assertEqual("SOURCE_BOUND", handed["telemetry"]["event"]["source"]["verification"])

    def test_handoff_consumption_requires_actual_matched_agent_ack(self):
        handed = self.full_to_handoff()
        route = handed["route"]
        pending = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:consume"],
                "cost": self.cost(),
            },
        )
        self.assertEqual("TSE_HELIX_CONSUMPTION_PENDING", pending["status"])
        self.assertEqual("ROUTED_NOT_CONSUMED", pending["hold"])

        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"], ack)
        consumed = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:consume"],
                "cost": self.cost(),
            },
        )
        self.assertEqual("TSE_HELIX_HANDOFF_CONSUMED", consumed["status"], consumed)
        self.assertFalse(consumed["claim_authority"])

        claim_before = self.advance(self.a, "CLAIM_STATE", consumed["route"], consumed["event_id"])
        self.assertEqual("TSE_HELIX_POPULATION_HOLD", claim_before["status"])
        self.assertEqual("AUTHORITY_HOLD", claim_before["hold"])

    def test_independent_claim_then_return_check_complete_operational_helix(self):
        handed = self.full_to_handoff()
        route = handed["route"]
        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"])
        consumed = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:consume"],
                "cost": self.cost(),
            },
        )
        self.board_b.release(agent_id="beta", release_status="HANDOFF", outcome="accept child")
        claimed = self.board_b.present(
            agent_id="beta",
            task="Execute helical child",
            work_key=route["child_work_key"],
            targets=["child.py"],
        )
        self.assertEqual("PRESENT", claimed["status"], claimed)

        claim_event = self.advance(self.a, "CLAIM_STATE", consumed["route"], consumed["event_id"])
        self.assertEqual("TSE_HELIX_ADVANCED", claim_event["status"], claim_event)
        returned = self.advance(
            self.a,
            "RETURN_CHECK",
            claim_event["route"],
            claim_event["event_id"],
            child_return=self.valid_return(claim_event["route"]),
        )
        self.assertEqual("TSE_HELIX_ADVANCED", returned["status"], returned)
        self.assertEqual("CHILD_VERIFIED_RETURN", returned["transition"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1.0, report["metrics"]["eta_claim"])
        self.assertEqual(1.0, report["metrics"]["eta_return"])
        self.assertEqual(0.0, report["metrics"]["eta_apply"])
        resource = self.rpc(self.a, "resources/read", {"uri": "athena://tse-helix/v2"})["result"]
        self.assertIn("NOT_AVAILABLE_IN_THIS_OPERATIONAL_SURFACE", str(resource))

    def test_reconcile_recovers_missing_publish_telemetry_without_replaying_publish(self):
        opened = self.open()
        self.present_parent()
        low = self.tool(
            self.a,
            "athena_tse_population_publish",
            {"route": opened["route"]},
        )
        self.assertEqual("TSE_POPULATION_NEED_PUBLISHED", low["status"])
        reconciled = self.tool(
            self.a,
            "athena_tse_helix_reconcile",
            {
                "mission_id": self.mission,
                "operation": "PUBLISH",
                "route": low["route"],
                "parent_event_id": opened["root_event_id"],
                "actor_id": "observer",
                "witnesses": ["test:reconcile"],
                "cost": self.cost(),
            },
        )
        self.assertEqual("TSE_HELIX_RECONCILED", reconciled["status"], reconciled)
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(1, report["counts"]["HATCH_NEED_PUBLISHED"])

    def test_declared_success_cannot_inflate_source_bound_chain(self):
        opened = self.open()
        declared = self.tool(
            self.a,
            "athena_tse_telemetry_record",
            {
                "mission_id": self.mission,
                "route_id": opened["route"]["route_id"],
                "hatch_id": opened["route"]["hatch_id"],
                "transition": "RETURN_APPLIED",
                "actor_id": "observer",
                "witnesses": ["fake:apply"],
                "cost": self.cost(),
                "parent_event_id": opened["root_event_id"],
                "child_agent_id": "beta",
                "child_claim_id": "fake-claim",
                "verified_delta": 999.0,
                "attempt_ref": "fake-apply",
            },
        )
        self.assertEqual("TSE_TELEMETRY_PARENT_HOLD", declared["status"])
        report = self.tool(self.a, "athena_tse_telemetry_report", {"mission_id": self.mission})
        self.assertEqual(0, report["counts"]["RETURN_APPLIED"])
        self.assertEqual("UNKNOWN", report["metrics"]["eta_helix"])


if __name__ == "__main__":
    unittest.main()
