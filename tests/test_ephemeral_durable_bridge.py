from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp import protocol
from athena_mcp.dispatch import handle
from athena_mcp.ephemeral_durable_bridge import VERSION
from athena_mcp.ephemeral_durable_bridge_protocol import (
    EPHEMERAL_DURABLE_RESOURCE,
    EPHEMERAL_DURABLE_TOOL_NAMES,
)
from athena_mcp.federation_ephemeral_bridge import encode_handoff_ref
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path) -> tuple[Path, Path]:
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
    return local, origin


class EphemeralDurableBridgeTests(unittest.TestCase):
    def runtime(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, _ = _fixture(Path(td.name))
        server = Server(str(Path(td.name) / "athena.db"), git_root=local)
        self.addCleanup(server.store.close)
        now = [1000.0]
        fast = server.aor_development.ephemeral_coordination.runtime
        fast.clock = lambda: now[0]
        bridge = server.aor_development.ephemeral_durable_bridge.bridge
        board = MessageBoardRuntime(server.git)
        return server, fast, bridge, board, now

    @staticmethod
    def present_fast(runtime, aid: str):
        return runtime.present({
            "aid": aid,
            "epoch": "e1",
            "ttl_ms": 10000,
            "capabilities": ["coordination"],
            "need_offer_summary": {},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": f"source:{aid}",
        })

    @staticmethod
    def material(runtime, sender="fast-a", recipient="fast-b", ref="source:material", ttl_ms=10000):
        return runtime.post({
            "sender_aid": sender,
            "recipient_selector": {"aids": [recipient]},
            "delivery_class": "MATERIAL_CANDIDATE",
            "salience": 0.7,
            "ttl_ms": ttl_ms,
            "packet_digest_or_ref": ref,
            "lamport": 2,
            "causal_parents": [],
        })

    @staticmethod
    def args(packet_id: str, **overrides):
        value = {
            "packet_id": packet_id,
            "ephemeral_actor_aid": "fast-a",
            "actor_role": "SENDER",
            "actor_binding_ref": "binding:fast-a->board-a:opaque",
            "board_agent_id": "board-a",
            "board_recipients": ["board-b"],
            "minimum_receipt_stage": "ROUTED",
            "note": "preserve material candidate",
            "remote": "origin",
        }
        value.update(overrides)
        return value

    def test_surface_is_registered_and_reuses_existing_fast_runtime(self):
        server, fast, bridge, _, _ = self.runtime()
        names = {row["name"] for row in protocol.TOOLS}
        self.assertTrue(EPHEMERAL_DURABLE_TOOL_NAMES <= names)
        self.assertIs(server.aor_development.ephemeral_durable_bridge.bridge.runtime, fast)
        self.assertEqual(bridge.describe()["version"], VERSION)
        listed = handle(server, {"jsonrpc": "2.0", "id": 1, "method": "resources/list"})
        uris = {row["uri"] for row in listed["result"]["resources"]}
        self.assertIn(EPHEMERAL_DURABLE_RESOURCE["uri"], uris)
        resource = handle(server, {
            "jsonrpc": "2.0", "id": 2, "method": "resources/read",
            "params": {"uri": EPHEMERAL_DURABLE_RESOURCE["uri"]},
        })
        self.assertEqual(resource["result"]["contents"][0]["uri"], EPHEMERAL_DURABLE_RESOURCE["uri"])

    def test_plan_and_escalate_create_one_durable_message_without_identity_laundering(self):
        _, fast, bridge, board, _ = self.runtime()
        board.present(agent_id="board-a", task="durable actor", work_key="board-a")
        self.present_fast(fast, "fast-a")
        packet = self.material(fast)
        args = self.args(packet["packet_id"])

        plan = bridge.plan(args)
        self.assertEqual(plan["status"], "EPHEMERAL_DURABLE_PLAN_READY")
        self.assertTrue(plan["shared_frontier_verified"])
        self.assertFalse(plan["identity_binding_proven"])
        self.assertEqual(plan["plan"]["ephemeral_actor"]["aid"], "fast-a")
        self.assertEqual(plan["plan"]["durable_route"]["board_agent_id"], "board-a")
        self.assertFalse(plan["plan"]["identity_equivalence_proven"])

        escalated = bridge.escalate(args)
        self.assertEqual(escalated["status"], "EPHEMERAL_MATERIAL_ESCALATED")
        self.assertTrue(escalated["durable_return"])
        self.assertEqual(escalated["delivery"], "DURABLY_ROUTED_NOT_CONSUMED")
        event_id = escalated["message_event"]["event_id"]

        unread = board.read(agent_id="board-b")["unread_messages"]
        event = next(row for row in unread if row["event_id"] == event_id)
        packet_payload = event["payload"]["ephemeral_durable_bridge"]
        self.assertEqual(packet_payload["source_packet"]["packet_id"], packet["packet_id"])
        self.assertEqual(packet_payload["ephemeral_actor"]["binding_standing"], "CALLER_SUPPLIED_OPAQUE_REFERENCE_NOT_IDENTITY_PROOF")
        self.assertFalse(packet_payload["claim_authority"])
        self.assertFalse(packet_payload["assignment_authority"])
        self.assertFalse(packet_payload["execution_authority"])
        self.assertEqual(event["law"], "MESSAGE_ROUTE != CONSUMPTION")

        replay = bridge.escalate(args)
        self.assertEqual(replay["status"], "EPHEMERAL_MATERIAL_ALREADY_ESCALATED")
        self.assertTrue(replay["idempotent"])
        self.assertEqual(replay["message_event"]["event_id"], event_id)
        matches = [
            row for row in board.read()["recent_events"]
            if (row.get("payload") or {}).get("ephemeral_escalation_id") == escalated["ephemeral_escalation_id"]
        ]
        self.assertEqual(len(matches), 1)

    def test_durable_replay_survives_source_ttl_expiry_after_first_escalation(self):
        _, fast, bridge, board, now = self.runtime()
        board.present(agent_id="board-a", task="durable actor", work_key="board-a")
        self.present_fast(fast, "fast-a")
        packet = self.material(fast, ttl_ms=1000)
        args = self.args(packet["packet_id"])
        first = bridge.escalate(args)
        self.assertEqual(first["status"], "EPHEMERAL_MATERIAL_ESCALATED")
        now[0] += 2.0
        replay = bridge.escalate(args)
        self.assertEqual(replay["status"], "EPHEMERAL_MATERIAL_ALREADY_ESCALATED")
        self.assertEqual(replay["message_event"]["event_id"], first["message_event"]["event_id"])

    def test_non_material_source_is_rejected_without_durable_write(self):
        _, fast, bridge, board, _ = self.runtime()
        board.present(agent_id="board-a", task="durable actor", work_key="board-a")
        self.present_fast(fast, "fast-a")
        packet = fast.post({
            "sender_aid": "fast-a",
            "recipient_selector": {"aids": ["fast-b"]},
            "delivery_class": "NUDGE",
            "salience": 0.2,
            "ttl_ms": 10000,
            "packet_digest_or_ref": "source:nudge",
            "lamport": 2,
            "causal_parents": [],
        })
        result = bridge.escalate(self.args(packet["packet_id"]))
        self.assertEqual(result["status"], "EPHEMERAL_DURABLE_ESCALATION_HOLD")
        self.assertIn("NOT_MATERIAL_CANDIDATE", result["reason"])
        self.assertFalse(result["durable_return"])

    def test_recipient_can_require_consumption_before_escalation(self):
        _, fast, bridge, board, _ = self.runtime()
        board.present(agent_id="board-a", task="durable actor", work_key="board-a")
        self.present_fast(fast, "fast-a")
        packet = self.material(fast)
        args = self.args(
            packet["packet_id"],
            ephemeral_actor_aid="fast-b",
            actor_role="RECIPIENT",
            actor_binding_ref="binding:fast-b->board-a:opaque",
            minimum_receipt_stage="CONSUMED",
        )
        before = bridge.plan(args)
        self.assertEqual(before["status"], "EPHEMERAL_DURABLE_PLAN_HOLD")
        self.assertIn("EPHEMERAL_RECEIPT_STAGE_HOLD", before["reason"])

        fast.receipt({"packet_id": packet["packet_id"], "aid": "fast-b", "stage": "DELIVERED"})
        fast.receipt({"packet_id": packet["packet_id"], "aid": "fast-b", "stage": "PRESENTED"})
        fast.receipt({
            "packet_id": packet["packet_id"], "aid": "fast-b", "stage": "CONSUMED",
            "witness": {"consumer_ref": "fast-b:decision"},
        })
        ready = bridge.plan(args)
        self.assertEqual(ready["status"], "EPHEMERAL_DURABLE_PLAN_READY")
        self.assertEqual(ready["plan"]["source_packet"]["actor_observed_receipt_stage"], "CONSUMED")

    def test_federation_projection_is_preserved_without_source_currentness_promotion(self):
        _, fast, bridge, board, _ = self.runtime()
        board.present(agent_id="board-a", task="durable actor", work_key="board-a")
        self.present_fast(fast, "fast-a")
        handoff = "sha256:" + "1" * 64
        cursor = "sha256:" + "2" * 64
        packet = self.material(fast, ref=encode_handoff_ref(handoff, cursor))
        plan = bridge.plan(self.args(packet["packet_id"]))
        projection = plan["plan"]["source_packet"]["federation_projection"]
        self.assertEqual(projection["handoff_digest"], handoff)
        self.assertEqual(projection["source_cursor_digest"], cursor)
        self.assertEqual(projection["loss_class"], "LOSSY_AUX")
        self.assertFalse(projection["source_currentness_proven"])
        self.assertFalse(plan["plan"]["source_currentness_proven"])

    def test_inactive_board_actor_holds_instead_of_creating_claim(self):
        _, fast, bridge, board, _ = self.runtime()
        self.present_fast(fast, "fast-a")
        packet = self.material(fast)
        result = bridge.escalate(self.args(packet["packet_id"]))
        self.assertEqual(result["status"], "EPHEMERAL_DURABLE_BOARD_AGENT_NOT_ACTIVE_HOLD")
        self.assertFalse(result["durable_return"])
        self.assertEqual(board.read()["active"], [])


if __name__ == "__main__":
    unittest.main()
