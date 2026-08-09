from __future__ import annotations

import copy
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
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    (local / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    clone = base / "clone"
    proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(clone, "config", "user.name", "clone")
    _run(clone, "config", "user.email", "clone@example.invalid")
    return local, clone


def hatch():
    checkpoint = {
        "residual": ["implement bounded TSE subtask"],
        "acceptance": ["matched agent claim visible", "verified return"],
    }
    checkpoint["checkpoint_digest"] = _digest(checkpoint)
    value = {
        "schema_version": "ATHENA.TSE.HATCH.V2",
        "hatch_id": "HATCH.RUNTIME.1",
        "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
        "parent_checkpoint": checkpoint,
        "child_quest": {"id": "Q-TSE-RUNTIME-CHILD", "version": "1"},
        "status": "CHILD_ACTIVE",
        "platform_counter_reset_claimed": False,
    }
    value["hatch_digest"] = _digest(value)
    return value


class TsePopulationRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        local, clone = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=local)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=clone)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0

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

    def present(self, board, agent, task, work_key, targets=None):
        out = board.present(agent_id=agent, task=task, work_key=work_key, targets=targets or [])
        self.assertEqual("PRESENT", out["status"], out)
        return out

    def plan(self, server=None, hatch_value=None):
        return self.tool(
            server or self.a,
            "athena_tse_population_plan",
            {
                "hatch": hatch_value or hatch(),
                "parent_agent_id": "alpha",
                "capabilities": ["code", "tests"],
                "targets": ["child.py"],
                "dependencies": ["api.ready"],
                "role": "BUILDER",
                "needed_units": 1,
                "life_policy": "STAY_IN_GAME_LIFE_LOOP_V1",
                "clear_condition_digest": "sha256:criterion",
            },
        )

    def setup_parent_and_need(self):
        self.present(self.board_a, "alpha", "Parent TSE lane", "parent-tse", ["parent.py"])
        planned = self.plan(self.a)
        self.assertEqual("TSE_POPULATION_NEED_READY", planned["status"])
        published = self.tool(self.a, "athena_tse_population_publish", {"route": planned["route"]})
        self.assertEqual("TSE_POPULATION_NEED_PUBLISHED", published["status"])
        return published["route"]

    def setup_offer(self):
        presence = self.present(self.board_b, "beta", "Available TSE builder", "offer-beta", ["offer-beta.py"])
        offered = self.tool(
            self.b,
            "athena_cohesion_request_offer",
            {
                "request_id": "OFFER.TSE.BETA",
                "agent_id": "beta",
                "kind": "OFFER",
                "capabilities": ["code", "tests"],
                "goal_ref": "offer.tse",
                "role": "BUILDER",
                "provides": ["api.ready"],
                "capacity_units": 2,
            },
        )
        self.assertEqual("COHESION_OFFER_PUBLISHED", offered["status"])
        return presence

    def matched_route(self):
        route = self.setup_parent_and_need()
        self.setup_offer()
        matched = self.tool(self.a, "athena_tse_population_match", {"route": route, "min_score": 1})
        self.assertEqual("TSE_POPULATION_MATCHED_ADVISORY", matched["status"])
        self.assertEqual("beta", matched["route"]["selected_match"]["agent_id"])
        return matched["route"]

    def routed_route(self):
        route = self.matched_route()
        handed = self.tool(self.a, "athena_tse_population_handoff", {"route": route})
        self.assertEqual("TSE_POPULATION_HANDOFF_ROUTED", handed["status"])
        self.assertEqual("HANDOFF_ROUTED_NOT_CONSUMED", handed["route"]["status"])
        return handed["route"]

    def claimed_route(self):
        route = self.routed_route()
        before = self.tool(self.a, "athena_tse_population_claim_state", {"route": route})
        self.assertEqual("AUTHORITY_HOLD", before["hold"])

        snapshot = self.board_b.read(agent_id="beta", shared_remote_mode="REQUIRED")
        unread = [row for row in snapshot.get("unread_messages", []) if row.get("event_id") == route["handoff_message_id"]]
        self.assertEqual(1, len(unread), snapshot)
        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"])

        released = self.board_b.release(agent_id="beta", release_status="HANDOFF", outcome="accept TSE subtask")
        self.assertEqual("RELEASED", released["status"])
        claimed = self.board_b.present(
            agent_id="beta",
            task="Execute routed TSE subtask",
            work_key=route["child_work_key"],
            targets=["child.py"],
        )
        self.assertEqual("PRESENT", claimed["status"])

        observed = self.tool(self.a, "athena_tse_population_claim_state", {"route": route})
        self.assertEqual("TSE_POPULATION_SUBTASK_CLAIMED", observed["status"])
        self.assertEqual("EXACT_CHILD_WORK_KEY", observed["route"]["child_claim"]["binding"])
        return observed["route"]

    def valid_return(self, route):
        return {
            "schema_version": "ATHENA.TSE.RETURN.V2",
            "return_receipt_id": "RET.RUNTIME.1",
            "hatch_id": route["hatch_id"],
            "hatch_digest": route["hatch_digest"],
            "parent_checkpoint_digest": route["parent_checkpoint_digest"],
            "population_route_id": route["route_id"],
            "population_route_digest": route["route_digest"],
            "child_agent_id": route["child_claim"]["agent_id"],
            "child_claim_id": route["child_claim"]["claim_id"],
            "verified": True,
            "witnesses": ["test:return-witness"],
            "verified_delta": 4.0,
            "child_git_position": {
                "repo": "demeet2k/Athena",
                "ref": "refs/heads/child",
                "head": "b" * 40,
            },
            "platform_counter_reset_claimed": False,
        }

    def test_tools_and_resource_are_registered(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in {
            "athena_tse_population_plan", "athena_tse_population_publish", "athena_tse_population_match",
            "athena_tse_population_handoff", "athena_tse_population_claim_state", "athena_tse_population_return_check",
        }:
            self.assertIn(name, tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-population/v1", resources)

    def test_plan_is_pure_and_deterministic(self):
        one = self.plan(self.a)
        two = self.plan(self.a)
        self.assertEqual(one["route"]["route_id"], two["route"]["route_id"])
        self.assertEqual("NEED_READY_NOT_PUBLISHED", one["route"]["status"])
        self.assertFalse(one["assignment_authority"])
        self.assertFalse(one["claim_authority"])

    def test_tampered_hatch_digest_fails_closed(self):
        value = hatch()
        value["child_quest"]["version"] = "2"
        held = self.plan(self.a, hatch_value=value)
        self.assertEqual("EVIDENCE_HOLD", held["hold"])
        self.assertIn("hatch_digest_invalid", held["errors"])

    def test_publish_requires_parent_message_board_presence(self):
        planned = self.plan(self.a)
        held = self.tool(self.a, "athena_tse_population_publish", {"route": planned["route"]})
        self.assertEqual("TSE_POPULATION_PUBLISH_HOLD", held["status"])

    def test_tampered_route_semantics_fail_closed(self):
        planned = self.plan(self.a)
        route = copy.deepcopy(planned["route"])
        route["child_work_key"] = "TSE.CHILD.TAMPERED"
        held = self.tool(self.a, "athena_tse_population_publish", {"route": route})
        self.assertEqual("EVIDENCE_HOLD", held["hold"])
        self.assertIn("child_work_key_invalid", held["errors"])

    def test_match_is_advisory_and_preserves_offer_claim(self):
        route = self.setup_parent_and_need()
        offer_presence = self.setup_offer()
        claim_before = offer_presence["presence"]["claim_id"]
        matched = self.tool(self.a, "athena_tse_population_match", {"route": route})
        self.assertEqual("TSE_POPULATION_MATCHED_ADVISORY", matched["status"])
        snapshot = self.board_a.read(shared_remote_mode="REQUIRED")
        beta = next(row for row in snapshot["active"] if row["agent_id"] == "beta")
        self.assertEqual(claim_before, beta["claim_id"])
        self.assertFalse(matched["assignment_authority"])
        self.assertFalse(matched["claim_authority"])

    def test_handoff_route_does_not_activate_subtask(self):
        route = self.routed_route()
        observed = self.tool(self.a, "athena_tse_population_claim_state", {"route": route})
        self.assertEqual("AUTHORITY_HOLD", observed["hold"])
        self.assertEqual("match_or_ack_without_compatible_message_board_claim", observed["reason"])

    def test_unverified_claim_snapshot_fails_stale(self):
        route = self.routed_route()
        observed = self.tool(
            self.a,
            "athena_tse_population_claim_state",
            {"route": route, "shared_remote_mode": "DISABLED"},
        )
        self.assertEqual("STALE_STATE_HOLD", observed["hold"])

    def test_independent_matched_agent_claim_activates_subtask(self):
        route = self.claimed_route()
        self.assertEqual("SUBTASK_CLAIMED", route["status"])
        self.assertEqual("beta", route["child_claim"]["agent_id"])

    def test_return_check_binds_exact_hatch_route_agent_and_current_claim(self):
        route = self.claimed_route()
        ready = self.tool(
            self.a,
            "athena_tse_population_return_check",
            {"route": route, "child_return": self.valid_return(route)},
        )
        self.assertEqual("TSE_POPULATION_RETURN_CONSUMPTION_READY", ready["status"])
        self.assertTrue(ready["message_board_claim_reverified"])
        self.assertFalse(ready["return_applied"])
        self.assertFalse(ready["execution_authority"])

    def test_return_requires_claim_to_still_be_current(self):
        route = self.claimed_route()
        released = self.board_b.release(agent_id="beta", release_status="DONE", outcome="claim ended before return")
        self.assertEqual("RELEASED", released["status"])
        held = self.tool(
            self.a,
            "athena_tse_population_return_check",
            {"route": route, "child_return": self.valid_return(route)},
        )
        self.assertEqual("AUTHORITY_HOLD", held["hold"])
        self.assertEqual("matched_agent_claim_not_current_at_return", held["reason"])

    def test_wrong_child_claim_fails_authority(self):
        route = self.claimed_route()
        returned = self.valid_return(route)
        returned["child_claim_id"] = "OTHER"
        held = self.tool(self.a, "athena_tse_population_return_check", {"route": route, "child_return": returned})
        self.assertEqual("AUTHORITY_HOLD", held["hold"])

    def test_platform_reset_claim_fails_closed(self):
        route = self.claimed_route()
        returned = self.valid_return(route)
        returned["platform_counter_reset_claimed"] = True
        held = self.tool(self.a, "athena_tse_population_return_check", {"route": route, "child_return": returned})
        self.assertEqual("EVIDENCE_HOLD", held["hold"])

    def test_nested_platform_reset_claim_fails_closed(self):
        route = self.claimed_route()
        returned = self.valid_return(route)
        returned["nested"] = {"platform_counter_reset_claimed": True}
        held = self.tool(self.a, "athena_tse_population_return_check", {"route": route, "child_return": returned})
        self.assertEqual("EVIDENCE_HOLD", held["hold"])


if __name__ == "__main__":
    unittest.main()
