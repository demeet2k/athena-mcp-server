from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp import protocol
from athena_mcp.communication_route_readiness import (
    RESOURCE_URI,
    TOOL_NAME,
    VERSION,
    verify_route_readiness,
)
from athena_mcp.dispatch import handle
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server
from athena_mcp.synapse_liminal_adapter import liminal_capsule_to_synapse


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


class CommunicationRouteReadinessTests(unittest.TestCase):
    def server(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local = _fixture(Path(td.name))
        server = Server(str(Path(td.name) / "athena.db"), git_root=local)
        self.addCleanup(server.store.close)
        return server

    @staticmethod
    def present_fast(server, aid="fast-a"):
        return server.aor_development.ephemeral_coordination.runtime.present({
            "aid": aid,
            "epoch": "e1",
            "ttl_ms": 60000,
            "capabilities": ["federation-bridge"],
            "need_offer_summary": {},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": f"source:{aid}",
        })

    @staticmethod
    def statuses(result):
        return {row["condition"]: row for row in result["readiness"]}

    def test_pre_hop_federation_route_can_be_ready_with_observed_runtime_and_declared_source_coordinates(self):
        server = self.server()
        board = MessageBoardRuntime(server.git)
        board.present(agent_id="board-a", task="readiness actor", work_key="readiness-a")
        self.present_fast(server, "fast-a")
        fast = server.aor_development.ephemeral_coordination.runtime
        with fast._lock:
            before_packets = fast.db.execute("SELECT COUNT(*) FROM ephemeral_packets").fetchone()[0]
        before_head = server.git.head()

        result = verify_route_readiness(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
            "ephemeral_actor_aid": "fast-a",
            "board_agent_id": "board-a",
            "actor_binding_ref": "binding:fast-a->board-a:opaque",
            "delivery_class": "MATERIAL_CANDIDATE",
            "handoff_digest": "sha256:" + "1" * 64,
            "source_cursor_digest": "sha256:" + "2" * 64,
            "fresh_remote_check": True,
        })
        rows = self.statuses(result)
        self.assertTrue(result["ready"])
        self.assertEqual(result["status"], "ROUTE_READINESS_READY_OBSERVED_WITH_DECLARED_COORDINATES")
        self.assertEqual(rows["EPHEMERAL_SENDER_PRESENT"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["ACTIVE_MESSAGE_BOARD_ACTOR"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["FRESH_SHARED_MESSAGE_BOARD_FRONTIER"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["FEDERATION_HANDOFF_DIGEST_AVAILABLE"]["status"], "DECLARED_REQUIRED_PASS")
        self.assertEqual(rows["FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE"]["status"], "DECLARED_REQUIRED_PASS")
        self.assertEqual(rows["MATERIAL_CANDIDATE"]["status"], "DECLARED_REQUIRED_PASS")
        self.assertEqual(rows["EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF"]["status"], "DECLARED_REQUIRED_PASS")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["bridge_execution_performed"])
        self.assertEqual(result["frontier_observation"]["local_head_before"], before_head)
        self.assertEqual(result["frontier_observation"]["local_head_after"], before_head)
        with fast._lock:
            after_packets = fast.db.execute("SELECT COUNT(*) FROM ephemeral_packets").fetchone()[0]
        self.assertEqual(before_packets, after_packets)

    def test_without_fresh_fetch_shared_frontier_remains_unknown(self):
        server = self.server()
        MessageBoardRuntime(server.git).present(agent_id="board-a", task="readiness actor", work_key="readiness-a")
        self.present_fast(server, "fast-a")
        result = verify_route_readiness(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
            "ephemeral_actor_aid": "fast-a",
            "board_agent_id": "board-a",
            "actor_binding_ref": "binding:opaque",
            "delivery_class": "MATERIAL_CANDIDATE",
            "handoff_digest": "sha256:" + "1" * 64,
            "source_cursor_digest": "sha256:" + "2" * 64,
            "fresh_remote_check": False,
        })
        rows = self.statuses(result)
        self.assertFalse(result["ready"])
        self.assertEqual(result["status"], "ROUTE_READINESS_HOLD")
        self.assertEqual(rows["FRESH_SHARED_MESSAGE_BOARD_FRONTIER"]["status"], "UNKNOWN")
        self.assertFalse(result["frontier_observation"]["fresh_fetch_performed"])

    def test_after_federation_first_hop_packet_proves_projection_and_material_state(self):
        server = self.server()
        MessageBoardRuntime(server.git).present(agent_id="board-a", task="readiness actor", work_key="readiness-a")
        self.present_fast(server, "fast-a")
        handoff = "sha256:" + "3" * 64
        cursor = "sha256:" + "4" * 64
        federation = server.aor_development.federation_ephemeral_bridge.bridge
        routed = federation.post({
            "sender_aid": "fast-a",
            "recipient_aids": ["fast-b"],
            "handoff_digest": handoff,
            "source_cursor_digest": cursor,
            "lamport": 2,
            "delivery_class": "MATERIAL_CANDIDATE",
        })
        packet_id = routed["transport"]["packet_id"]

        result = verify_route_readiness(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
            "packet_id": packet_id,
            "ephemeral_actor_aid": "fast-a",
            "board_agent_id": "board-a",
            "actor_binding_ref": "binding:opaque",
            "handoff_digest": handoff,
            "source_cursor_digest": cursor,
            "fresh_remote_check": True,
        })
        rows = self.statuses(result)
        self.assertTrue(result["ready"])
        self.assertEqual(rows["FEDERATION_HANDOFF_DIGEST_AVAILABLE"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["MATERIAL_CANDIDATE"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF"]["status"], "DECLARED_REQUIRED_PASS")

        mismatch = verify_route_readiness(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
            "packet_id": packet_id,
            "ephemeral_actor_aid": "fast-a",
            "board_agent_id": "board-a",
            "actor_binding_ref": "binding:opaque",
            "handoff_digest": "sha256:" + "9" * 64,
            "source_cursor_digest": cursor,
            "fresh_remote_check": True,
        })
        self.assertFalse(mismatch["ready"])
        self.assertEqual(self.statuses(mismatch)["FEDERATION_HANDOFF_DIGEST_AVAILABLE"]["status"], "OBSERVED_HOLD")

    def test_liminal_to_message_board_readiness_observes_live_packet_sender_claim_and_frontier(self):
        server = self.server()
        board = MessageBoardRuntime(server.git)
        board.present(agent_id="alpha", task="liminal durable actor", work_key="liminal-alpha")
        server.call_tool("athena_liminal_beacon_touch", {
            "agent_id": "alpha",
            "object_refs": ["oid:shared"],
        })
        emitted = server.call_tool("athena_liminal_beacon_emit", {
            "agent_id": "alpha",
            "message_class": "RESULT",
            "summary": "ready",
            "object_refs": ["oid:shared"],
        })
        packet_id = emitted["packet"]["packet_id"]

        result = verify_route_readiness(server, {
            "source_plane": "LIMINAL_BEACON",
            "destination_plane": "MESSAGE_BOARD",
            "packet_id": packet_id,
            "fresh_remote_check": True,
        })
        rows = self.statuses(result)
        self.assertTrue(result["ready"])
        self.assertEqual(result["status"], "ROUTE_READINESS_READY_OBSERVED")
        self.assertEqual(rows["LIVE_LIMINAL_PACKET"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["LIMINAL_SENDER_HAS_ACTIVE_MESSAGE_BOARD_PRESENCE"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["FRESH_SHARED_MESSAGE_BOARD_FRONTIER"]["status"], "OBSERVED_PASS")

    def test_liminal_synapse_and_synapse_liminal_readiness_validate_existing_adapter_without_ingest(self):
        server = self.server()
        server.call_tool("athena_liminal_beacon_touch", {
            "agent_id": "alpha",
            "object_refs": ["oid:shared"],
        })
        server.call_tool("athena_liminal_beacon_touch", {
            "agent_id": "beta",
            "object_refs": ["oid:shared"],
        })
        emitted = server.call_tool("athena_liminal_beacon_emit", {
            "agent_id": "alpha",
            "message_class": "RESULT",
            "summary": "ready",
            "object_refs": ["oid:shared"],
        })
        packet = emitted["packet"]
        packet_id = packet["packet_id"]
        outward = verify_route_readiness(server, {
            "source_plane": "LIMINAL_BEACON",
            "destination_plane": "SYNAPSE_ENVELOPE",
            "packet_id": packet_id,
            "source_revision": "source-rev-explicit",
        })
        self.assertTrue(outward["ready"])
        self.assertEqual(outward["status"], "ROUTE_READINESS_READY_OBSERVED_WITH_DECLARED_COORDINATES")
        self.assertEqual(self.statuses(outward)["LIVE_LIMINAL_PACKET_OR_RECEIPT"]["status"], "OBSERVED_PASS")
        self.assertEqual(self.statuses(outward)["EXPLICIT_SOURCE_REVISION"]["status"], "DECLARED_REQUIRED_PASS")

        envelope = liminal_capsule_to_synapse(
            packet,
            source_revision="source-rev-explicit",
            bridge_observed_at="2026-08-24T16:30:00Z",
        )
        before_packets = len(server._liminal_beacon_mesh_runtime_v1._packets)
        inward = verify_route_readiness(server, {
            "source_plane": "SYNAPSE_ENVELOPE",
            "destination_plane": "LIMINAL_BEACON",
            "target_liminal_agent_id": "beta",
            "synapse_envelope": envelope,
        })
        self.assertTrue(inward["ready"])
        self.assertEqual(inward["status"], "ROUTE_READINESS_READY_OBSERVED")
        rows = self.statuses(inward)
        self.assertEqual(rows["VALID_SYNAPSE_ENVELOPE"]["status"], "OBSERVED_PASS")
        self.assertEqual(rows["TARGET_LIMINAL_AGENT_PRESENT"]["status"], "OBSERVED_PASS")
        self.assertEqual(len(server._liminal_beacon_mesh_runtime_v1._packets), before_packets)

    def test_tool_resource_manifest_and_invalid_target_hold(self):
        server = self.server()
        self.assertIn(TOOL_NAME, {row["name"] for row in protocol.TOOLS})
        before = server.git.head()
        called = handle(server, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": TOOL_NAME,
                "arguments": {
                    "source_plane": "SYNAPSE_ENVELOPE",
                    "destination_plane": "LIMINAL_BEACON",
                    "target_liminal_agent_id": "missing",
                    "synapse_envelope": {},
                },
            },
        })
        self.assertFalse(called["result"]["isError"])
        payload = called["result"]["structuredContent"]
        self.assertEqual(payload["version"], VERSION)
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["status"], "ROUTE_READINESS_HOLD")
        self.assertEqual(server.git.head(), before)

        listed = handle(server, {"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        self.assertIn(RESOURCE_URI, {row["uri"] for row in listed["result"]["resources"]})
        read = handle(server, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": RESOURCE_URI},
        })
        resource = json.loads(read["result"]["contents"][0]["text"])
        self.assertEqual(resource["version"], VERSION)
        self.assertEqual(resource["authority"], "READ_ONLY_PRECONDITION_VERIFICATION")

        manifest = handle(server, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {"uri": "athena://manifest"},
        })
        manifest_payload = json.loads(manifest["result"]["contents"][0]["text"])
        self.assertEqual(manifest_payload["communication_route_readiness"]["tool"], TOOL_NAME)
        self.assertIn("COMMUNICATION_ROUTE_READINESS_V1_READ_ONLY", manifest_payload["extensions"])


if __name__ == "__main__":
    unittest.main()
