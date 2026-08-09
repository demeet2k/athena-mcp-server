from __future__ import annotations

import copy
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server
from athena_mcp.tse_population import _digest
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
    parent = _run(a, "rev-parse", "HEAD")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(a, "remote", "add", "origin", str(origin))
    _run(a, "push", "-u", "origin", "master")

    _run(a, "checkout", "-b", "child")
    (a / "child.txt").write_text("verified child delta\n", encoding="utf-8")
    _run(a, "add", "child.txt")
    _run(a, "commit", "-m", "child work")
    child = _run(a, "rev-parse", "HEAD")
    _run(a, "checkout", "master")

    b = base / "b"
    proc = subprocess.run(["git", "clone", str(origin), str(b)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(b, "config", "user.name", "b")
    _run(b, "config", "user.email", "b@example.invalid")
    return a, b, parent, child


class TseSelfTighteningKnotApplyTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        a, b, self.parent_head, self.child_head = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=a)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=b)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.seq = 0
        self.mission = "MISSION-KNOT-1"
        self.hatch = self.make_hatch()
        self.route = self.make_route()
        self.return_event = self.make_return_chain()

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

    def make_hatch(self):
        gp = {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": self.parent_head,
        }
        checkpoint = {
            "residual": ["adopt verified child into shared parent"],
            "acceptance": ["child and parent are ancestors of applied shared HEAD"],
            "git_position": gp,
        }
        checkpoint["checkpoint_digest"] = _digest(checkpoint)
        hatch = {
            "schema_version": "ATHENA.TSE.HATCH.V2",
            "hatch_id": "HATCH.KNOT.1",
            "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
            "parent_checkpoint": checkpoint,
            "parent_git_position": gp,
            "child_quest": {"id": "Q-KNOT-CHILD", "version": "1"},
            "status": "CHILD_ACTIVE",
            "platform_counter_reset_claimed": False,
        }
        hatch["hatch_digest"] = _digest(hatch)
        return hatch

    def make_route(self):
        planned = self.tool(
            self.a,
            "athena_tse_population_plan",
            {
                "hatch": self.hatch,
                "parent_agent_id": "alpha",
                "capabilities": ["code", "tests"],
                "targets": ["child.txt"],
                "role": "BUILDER",
            },
        )
        self.assertEqual("TSE_POPULATION_NEED_READY", planned["status"], planned)
        route = copy.deepcopy(planned["route"])
        route["status"] = "SUBTASK_CLAIMED"
        route["child_claim"] = {
            "agent_id": "beta",
            "claim_id": "CLAIM.KNOT.BETA",
            "work_key": route["child_work_key"],
            "mode": "PRIMARY",
            "join_of": None,
            "claim_base_head": self.parent_head,
            "binding": "EXACT_CHILD_WORK_KEY",
        }
        return route

    def source_event(
        self,
        transition,
        *,
        parent=None,
        ref=None,
        child=False,
        source_kind=None,
        source_git_head=None,
        delta=None,
    ):
        runtime = TseHelixTelemetryRuntime(self.a)
        ref = ref or f"SRC-{transition}"
        out = runtime.record_source_bound(
            mission_id=self.mission,
            route_id=self.route["route_id"],
            hatch_id=self.route["hatch_id"],
            transition=transition,
            actor_id="observer",
            witnesses=[f"witness:{transition}"],
            cost={"known": True, "total": 0.1},
            source_kind=source_kind or f"TEST_{transition}",
            source_ref=ref,
            source_payload={"transition": transition, "ref": ref, "route_id": self.route["route_id"]},
            source_git_head=source_git_head,
            source_authority="TEST_SOURCE",
            parent_event_id=parent,
            child_agent_id="beta" if child else None,
            child_claim_id="CLAIM.KNOT.BETA" if child else None,
            verified_delta=delta,
            attempt_ref=ref,
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", out["status"], out)
        return out["event"]

    def make_return_chain(self):
        root = self.source_event("HATCH_CREATED", ref="K0")
        published = self.source_event("HATCH_NEED_PUBLISHED", parent=root["event_id"], ref="K1")
        matched = self.source_event("MATCH_FOUND", parent=published["event_id"], ref="K2")
        routed = self.source_event("HANDOFF_ROUTED", parent=matched["event_id"], ref="K3")
        claimed = self.source_event("CHILD_CLAIMED", parent=routed["event_id"], ref="K4", child=True)
        returned = self.source_event(
            "CHILD_VERIFIED_RETURN",
            parent=claimed["event_id"],
            ref="RETURN.KNOT.1",
            child=True,
            source_kind="TSE_RETURN_CHECK",
            source_git_head=self.child_head,
            delta=5.0,
        )
        return returned

    def merge_child_and_push(self):
        root = Path(self.a.git.root)
        _run(root, "merge", "--no-ff", "child", "-m", "apply verified child")
        applied = _run(root, "rev-parse", "HEAD")
        _run(root, "push", "origin", "master")
        return applied

    def apply_packet(self, applied_head, *, apply_id="APPLY.KNOT.1", child_head=None, parent_head=None):
        return {
            "hatch": copy.deepcopy(self.hatch),
            "apply_receipt": {
                "schema_version": "ATHENA.TSE.KNOT.APPLY.RECEIPT.V1",
                "apply_id": apply_id,
                "mode": "ANCESTRY_ADOPTION",
                "parent_head": parent_head or self.parent_head,
                "child_head": child_head or self.child_head,
                "applied_head": applied_head,
                "apply_witnesses": ["git:shared-adoption", "test:child-pass"],
                "platform_counter_reset_claimed": False,
            },
        }

    def observe_apply(self, packet):
        return self.tool(
            self.a,
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": "APPLY",
                "route": self.route,
                "parent_event_id": self.return_event["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:knot-observe"],
                "cost": {"known": True, "total": 1.0},
                "child_return": packet,
            },
        )

    def test_apply_operation_is_registered_on_existing_helix_tool(self):
        tools = {row["name"]: row for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        schema = tools["athena_tse_helix_advance"]["inputSchema"]
        self.assertIn("APPLY", schema["properties"]["operation"]["enum"])

    def test_shared_merge_closes_return_applied_stage(self):
        applied = self.merge_child_and_push()
        result = self.observe_apply(self.apply_packet(applied))
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", result["status"], result)
        self.assertEqual("TIGHTENED_SHARED_GIT", result["knot_status"])
        self.assertTrue(result["return_applied"])
        self.assertFalse(result["merge_authority"])
        self.assertFalse(result["execution_authority"])
        self.assertEqual(applied, result["applied_head"])
        self.assertEqual(applied, result["next_parent_git_position"]["head"])

        event = next(
            row
            for row in self.a.aor_development.transport.tse_telemetry._events()
            if row.get("event_id") == result["return_applied_event_id"]
        )
        self.assertEqual("RETURN_APPLIED", event["transition"])
        self.assertEqual("SOURCE_BOUND", event["source"]["verification"])
        self.assertEqual("TSE_SHARED_GIT_ADOPTION", event["source"]["kind"])
        self.assertEqual(self.return_event["event_id"], event["parent_event_id"])
        self.assertEqual(5.0, event["verified_delta"])

    def test_exact_replay_is_historical_idempotency_after_telemetry_advances_head(self):
        applied = self.merge_child_and_push()
        first = self.observe_apply(self.apply_packet(applied))
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", first["status"], first)
        replay = self.observe_apply(self.apply_packet(applied))
        self.assertEqual("TSE_KNOT_APPLY_ALREADY_OBSERVED", replay["status"], replay)
        self.assertFalse(replay["current_shared_frontier_revalidated"])
        self.assertEqual(first["return_applied_event_id"], replay["return_applied_event_id"])

    def test_changed_same_apply_id_conflicts(self):
        applied = self.merge_child_and_push()
        first = self.observe_apply(self.apply_packet(applied))
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", first["status"], first)
        changed = self.apply_packet(applied)
        changed["apply_receipt"]["apply_witnesses"] = ["changed:witness"]
        held = self.observe_apply(changed)
        self.assertEqual("TSE_KNOT_APPLY_HOLD", held["status"], held)
        self.assertEqual("changed_same_apply_id_conflict", held["reason"])

    def test_new_stale_apply_receipt_cannot_masquerade_as_current_after_frontier_advances(self):
        applied = self.merge_child_and_push()
        first = self.observe_apply(self.apply_packet(applied, apply_id="APPLY.KNOT.1"))
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", first["status"])
        stale = self.observe_apply(self.apply_packet(applied, apply_id="APPLY.KNOT.2"))
        self.assertEqual("TSE_KNOT_APPLY_HOLD", stale["status"], stale)
        self.assertEqual("STALE_STATE_HOLD", stale["hold"])
        self.assertEqual("applied_head_not_current_shared_frontier", stale["reason"])

    def test_current_head_without_child_ancestry_fails(self):
        current = _run(Path(self.a.git.root), "rev-parse", "HEAD")
        held = self.observe_apply(self.apply_packet(current, apply_id="APPLY.NO.CHILD"))
        self.assertEqual("TSE_KNOT_APPLY_HOLD", held["status"], held)
        self.assertEqual("STALE_STATE_HOLD", held["hold"])
        self.assertEqual("child_not_ancestor_of_applied", held["reason"])

    def test_wrong_child_head_fails_before_git_adoption_claim(self):
        applied = self.merge_child_and_push()
        held = self.observe_apply(
            self.apply_packet(applied, apply_id="APPLY.WRONG.CHILD", child_head=self.parent_head)
        )
        self.assertEqual("TSE_KNOT_APPLY_HOLD", held["status"], held)
        self.assertIn(held["reason"], {"child_head_equals_parent_head", "child_head_mismatch"})

    def test_wrong_parent_head_fails_hatch_binding(self):
        applied = self.merge_child_and_push()
        held = self.observe_apply(
            self.apply_packet(applied, apply_id="APPLY.WRONG.PARENT", parent_head=self.child_head)
        )
        self.assertEqual("TSE_KNOT_APPLY_HOLD", held["status"], held)
        self.assertEqual("parent_head_mismatch", held["reason"])

    def test_reset_claim_fails_closed(self):
        applied = self.merge_child_and_push()
        packet = self.apply_packet(applied, apply_id="APPLY.RESET")
        packet["apply_receipt"]["platform_counter_reset_claimed"] = True
        # Protocol validation may reject before runtime; invoke runtime surface directly
        result = self.a.aor_development.transport.tse_helix.advance(
            mission_id=self.mission,
            operation="APPLY",
            route=self.route,
            parent_event_id=self.return_event["event_id"],
            actor_id="observer",
            witnesses=["test:reset"],
            cost={"known": True, "total": 1.0},
            child_return=packet,
        )
        self.assertEqual("TSE_KNOT_APPLY_HOLD", result["status"], result)
        self.assertEqual("EVIDENCE_HOLD", result["hold"])


if __name__ == "__main__":
    unittest.main()
