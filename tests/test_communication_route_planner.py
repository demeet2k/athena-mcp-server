from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from athena_mcp import protocol
from athena_mcp import communication_route_planner as planner
from athena_mcp.communication_route_planner import (
    RESOURCE_URI,
    TOOL_NAME,
    VERSION,
    plan_route,
)
from athena_mcp.dispatch import handle
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


class CommunicationRoutePlannerTests(unittest.TestCase):
    def server(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local = _fixture(Path(td.name))
        server = Server(str(Path(td.name) / "athena.db"), git_root=local)
        self.addCleanup(server.store.close)
        return server

    def test_liminal_to_synapse_is_installed_but_preconditions_remain_unverified(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "LIMINAL_BEACON",
            "destination_plane": "SYNAPSE_ENVELOPE",
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_PRECONDITION_HOLD")
        self.assertEqual(result["route"]["hop_count"], 1)
        self.assertEqual(result["route"]["steps"][0]["mechanism"], "athena_synapse_liminal_export_packet / export_receipt")
        self.assertEqual(
            result["route"]["missing_preconditions"],
            ["EXPLICIT_SOURCE_REVISION", "LIVE_LIMINAL_PACKET_OR_RECEIPT"],
        )
        self.assertFalse(result["route"]["preconditions_verified"])
        self.assertTrue(result["route"]["roundtrip_route_installed"])
        self.assertEqual(result["route"]["roundtrip"]["steps"][0]["mechanism"], "athena_synapse_liminal_ingest")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["mutation"])

    def test_declaring_all_preconditions_changes_structural_status_not_verification(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "LIMINAL_BEACON",
            "destination_plane": "SYNAPSE_ENVELOPE",
            "satisfied_preconditions": [
                "live_liminal_packet_or_receipt",
                "explicit_source_revision",
            ],
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_STRUCTURALLY_AVAILABLE")
        self.assertEqual(result["route"]["missing_preconditions"], [])
        self.assertEqual(result["route"]["precondition_standing"], "CALLER_DECLARED_COMPLETE_NOT_VERIFIED")
        self.assertFalse(result["route"]["preconditions_verified"])
        self.assertFalse(result["execution_authority"])

    def test_federation_to_message_board_is_installed_two_hop_route_but_runtime_preconditions_hold(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "FEDERATION_SOURCE_CURSOR",
            "destination_plane": "MESSAGE_BOARD",
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_PRECONDITION_HOLD")
        route = result["route"]
        self.assertEqual(route["hop_count"], 2)
        self.assertEqual(
            [row["mechanism"] for row in route["steps"]],
            ["athena_ephemeral_federation_post/poll", "athena_ephemeral_durable_escalate"],
        )
        self.assertEqual(
            route["required_preconditions"],
            [
                "ACTIVE_MESSAGE_BOARD_ACTOR",
                "EPHEMERAL_SENDER_PRESENT",
                "EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF",
                "FEDERATION_HANDOFF_DIGEST_AVAILABLE",
                "FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE",
                "FRESH_SHARED_MESSAGE_BOARD_FRONTIER",
                "MATERIAL_CANDIDATE",
            ],
        )
        self.assertEqual(route["missing_preconditions"], route["required_preconditions"])
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["mutation"])

    def test_missing_bridge_candidate_behavior_remains_tested_with_synthetic_inventory(self):
        server = self.server()
        inventory = planner.build_plane_inventory(server, {}, limit=32)
        synthetic = json.loads(json.dumps(inventory))
        for edge in synthetic["bridge_edges"]:
            if (edge["src"], edge["dst"]) in {
                ("FEDERATION_SOURCE_CURSOR", "EPHEMERAL_SQLITE"),
                ("EPHEMERAL_SQLITE", "MESSAGE_BOARD"),
            }:
                edge["standing"] = "OPTIONAL_BRIDGE_UNOBSERVED"
                edge["authority"] = "NONE"
        with mock.patch.object(planner, "build_plane_inventory", return_value=synthetic):
            result = plan_route(server, {
                "source_plane": "FEDERATION_SOURCE_CURSOR",
                "destination_plane": "MESSAGE_BOARD",
            })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_BRIDGE_INSTALLATION_HOLD")
        self.assertEqual(result["candidate_route"]["hop_count"], 2)
        self.assertEqual(
            {(row["src"], row["dst"]) for row in result["missing_bridges"]},
            {
                ("FEDERATION_SOURCE_CURSOR", "EPHEMERAL_SQLITE"),
                ("EPHEMERAL_SQLITE", "MESSAGE_BOARD"),
            },
        )
        self.assertFalse(result["execution_authority"])

    def test_message_board_to_federation_has_no_invented_reverse_route(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "MESSAGE_BOARD",
            "destination_plane": "FEDERATION_SOURCE_CURSOR",
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_NOT_FOUND_HOLD")
        self.assertIsNone(result["candidate_route"])
        self.assertEqual(result["missing_bridges"], [])

    def test_identity_route_is_zero_hop_and_does_not_claim_transport(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "MESSAGE_BOARD",
            "destination_plane": "MESSAGE_BOARD",
            "max_hops": 0,
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_STRUCTURALLY_AVAILABLE")
        self.assertEqual(result["route"]["hop_count"], 0)
        self.assertEqual(result["route"]["loss_standing"], "IDENTITY_ROUTE")
        self.assertEqual(result["route"]["required_preconditions"], [])
        self.assertFalse(result["execution_authority"])

    def test_lossless_only_filter_refuses_current_lossy_projection(self):
        server = self.server()
        result = plan_route(server, {
            "source_plane": "LIMINAL_BEACON",
            "destination_plane": "SYNAPSE_ENVELOPE",
            "allow_lossy": False,
        })
        self.assertEqual(result["status"], "SYNAPSE_ROUTE_NOT_FOUND_HOLD")

    def test_mcp_tool_resource_manifest_and_no_git_mutation(self):
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
                    "source_plane": "LIMINAL_BEACON",
                    "destination_plane": "MESSAGE_BOARD",
                },
            },
        })
        self.assertFalse(called["result"]["isError"])
        self.assertEqual(called["result"]["structuredContent"]["version"], VERSION)
        self.assertEqual(before, server.git.head())

        listed = handle(server, {"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        self.assertIn(RESOURCE_URI, {row["uri"] for row in listed["result"]["resources"]})
        read = handle(server, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": RESOURCE_URI},
        })
        payload = json.loads(read["result"]["contents"][0]["text"])
        self.assertEqual(payload["version"], VERSION)
        self.assertEqual(payload["authority"], "READ_ONLY_ROUTE_PLANNING")

        manifest = handle(server, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {"uri": "athena://manifest"},
        })
        manifest_payload = json.loads(manifest["result"]["contents"][0]["text"])
        self.assertEqual(manifest_payload["communication_route_planner"]["tool"], TOOL_NAME)
        self.assertIn("COMMUNICATION_ROUTE_PLANNER_V1_READ_ONLY", manifest_payload["extensions"])
        self.assertEqual(before, server.git.head())


if __name__ == "__main__":
    unittest.main()
