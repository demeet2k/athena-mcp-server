from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.communication_plane_inventory import build_plane_inventory
from athena_mcp.communication_route_planner import plan_route
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path) -> Path:
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
    return local


class CommunicationSupermeshTests(unittest.TestCase):
    def server(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local = _fixture(Path(td.name))
        server = Server(str(Path(td.name) / "athena.db"), git_root=local)
        self.addCleanup(server.store.close)
        return server

    @staticmethod
    def present_fast(runtime, aid="fast-a"):
        return runtime.present({
            "aid": aid,
            "epoch": "e1",
            "ttl_ms": 60000,
            "capabilities": ["federation-bridge", "durable-escalation"],
            "need_offer_summary": {},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": f"source:{aid}",
        })

    def test_federation_material_candidate_escalates_through_same_fast_runtime_to_message_board(self):
        server = self.server()
        development = server.aor_development
        fast = development.ephemeral_coordination.runtime
        federation = development.federation_ephemeral_bridge.bridge
        durable = development.ephemeral_durable_bridge.bridge

        self.assertIs(federation.runtime, fast)
        self.assertIs(durable.runtime, fast)

        board = MessageBoardRuntime(server.git)
        board.present(agent_id="board-a", task="supermesh durable actor", work_key="supermesh-a")
        board.present(agent_id="board-b", task="supermesh durable sink", work_key="supermesh-b")
        self.present_fast(fast, "fast-a")

        handoff = "sha256:" + "1" * 64
        cursor = "sha256:" + "2" * 64
        routed = federation.post({
            "sender_aid": "fast-a",
            "recipient_aids": ["fast-b"],
            "handoff_digest": handoff,
            "source_cursor_digest": cursor,
            "lamport": 2,
            "delivery_class": "MATERIAL_CANDIDATE",
            "salience": 0.8,
        })
        self.assertEqual(routed["transport"]["route_state"], "ROUTED")

        observed = federation.poll({
            "aid": "fast-b",
            "after_cursor": 0,
            "max_items": 10,
            "salience_budget": 5.0,
        })
        self.assertEqual(len(observed["handoffs"]), 1)
        handoff_row = observed["handoffs"][0]
        packet_id = handoff_row["packet_id"]
        self.assertEqual(handoff_row["handoff_digest"], handoff)
        self.assertEqual(handoff_row["source_cursor_digest"], cursor)
        self.assertFalse(handoff_row["source_currentness_proven"])

        before_plan_head = server.git.head()
        route_plan = plan_route(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
            "satisfied_preconditions": [
                "FEDERATION_HANDOFF_DIGEST_AVAILABLE",
                "FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE",
                "EPHEMERAL_SENDER_PRESENT",
                "MATERIAL_CANDIDATE",
                "EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF",
                "ACTIVE_MESSAGE_BOARD_ACTOR",
                "FRESH_SHARED_MESSAGE_BOARD_FRONTIER",
            ],
        })
        self.assertEqual(route_plan["status"], "SYNAPSE_ROUTE_STRUCTURALLY_AVAILABLE")
        self.assertEqual(
            [step["mechanism"] for step in route_plan["route"]["steps"]],
            ["athena_ephemeral_federation_post/poll", "athena_ephemeral_durable_escalate"],
        )
        self.assertEqual(route_plan["route"]["hop_count"], 2)
        self.assertEqual(route_plan["route"]["missing_preconditions"], [])
        self.assertFalse(route_plan["route"]["preconditions_verified"])
        self.assertFalse(route_plan["execution_authority"])
        self.assertEqual(server.git.head(), before_plan_head)

        escalated = durable.escalate({
            "packet_id": packet_id,
            "ephemeral_actor_aid": "fast-a",
            "actor_role": "SENDER",
            "actor_binding_ref": "binding:fast-a->board-a:opaque",
            "board_agent_id": "board-a",
            "board_recipients": ["board-b"],
            "minimum_receipt_stage": "ROUTED",
            "note": "supermesh federation handoff",
            "remote": "origin",
        })
        self.assertEqual(escalated["status"], "EPHEMERAL_MATERIAL_ESCALATED")
        self.assertTrue(escalated["durable_return"])
        self.assertEqual(escalated["delivery"], "DURABLY_ROUTED_NOT_CONSUMED")

        unread = board.read(agent_id="board-b")["unread_messages"]
        event_id = escalated["message_event"]["event_id"]
        event = next(row for row in unread if row["event_id"] == event_id)
        durable_packet = event["payload"]["ephemeral_durable_bridge"]
        projection = durable_packet["source_packet"]["federation_projection"]
        self.assertEqual(projection["handoff_digest"], handoff)
        self.assertEqual(projection["source_cursor_digest"], cursor)
        self.assertEqual(projection["loss_class"], "LOSSY_AUX")
        self.assertFalse(projection["source_currentness_proven"])
        self.assertFalse(durable_packet["source_currentness_proven"])
        self.assertFalse(durable_packet["identity_equivalence_proven"])
        self.assertFalse(durable_packet["claim_authority"])
        self.assertFalse(durable_packet["assignment_authority"])
        self.assertFalse(durable_packet["execution_authority"])
        self.assertEqual(event["law"], "MESSAGE_ROUTE != CONSUMPTION")

    def test_inventory_requires_live_organs_and_observes_shared_runtime_identity(self):
        server = self.server()
        inventory = build_plane_inventory(server, {}, limit=32)
        optional = inventory["optional_components"]
        federation = optional["federation_ephemeral"]
        durable = optional["ephemeral_durable_escalation"]
        envelope = optional["synapse_envelope"]

        self.assertTrue(federation["source_available"])
        self.assertTrue(federation["installed"])
        self.assertTrue(federation["runtime_present"])
        self.assertTrue(federation["shared_fast_runtime_identity"])
        self.assertEqual(federation["standing"], "FEDERATION_EPHEMERAL_PROJECTION_INSTALLED_SHARED_RUNTIME")

        self.assertTrue(durable["source_available"])
        self.assertTrue(durable["installed"])
        self.assertTrue(durable["runtime_present"])
        self.assertTrue(durable["shared_fast_runtime_identity"])
        self.assertEqual(durable["standing"], "EPHEMERAL_DURABLE_ESCALATION_INSTALLED_SHARED_RUNTIME")

        self.assertTrue(envelope["source_available"])
        self.assertTrue(envelope["installed"])
        self.assertEqual(envelope["schema"], "ATHENA.SYNAPSE.ENVELOPE.V1")

        edges = {(row["src"], row["dst"]): row for row in inventory["bridge_edges"]}
        self.assertEqual(edges[("FEDERATION_SOURCE_CURSOR", "EPHEMERAL_SQLITE")]["standing"], "INSTALLED_EXPLICIT_PROJECTION")
        self.assertEqual(edges[("EPHEMERAL_SQLITE", "MESSAGE_BOARD")]["standing"], "INSTALLED_EXPLICIT_ESCALATION")
        self.assertEqual(edges[("LIMINAL_BEACON", "SYNAPSE_ENVELOPE")]["standing"], "INSTALLED_EXPLICIT_PROJECTION")

    def test_route_planner_and_inventory_are_read_only_even_with_all_bridges_installed(self):
        server = self.server()
        before = server.git.head()
        inventory = build_plane_inventory(server, {}, limit=32)
        plan = plan_route(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
        })
        after = server.git.head()
        self.assertEqual(before, after)
        self.assertEqual(inventory["authority"], "READ_ONLY_NAVIGATION_OBSERVER")
        self.assertEqual(plan["status"], "SYNAPSE_ROUTE_PRECONDITION_HOLD")
        self.assertEqual(plan["route"]["hop_count"], 2)
        self.assertFalse(plan["execution_authority"])
        self.assertFalse(plan["mutation"])


if __name__ == "__main__":
    unittest.main()
