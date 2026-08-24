from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.communication_plane_inventory import RESOURCE_URI, VERSION
from athena_mcp.dispatch import handle
from athena_mcp.server import Server
from athena_mcp.synapse_observer import SynapseObserverRuntime


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


class CommunicationPlaneInventoryTests(unittest.TestCase):
    def server(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local = _fixture(Path(td.name))
        server = Server(str(Path(td.name) / "athena.db"), git_root=local)
        self.addCleanup(server.store.close)
        return server

    def test_fast_plane_is_live_but_not_joined_into_board_liminal_agent_identity(self):
        server = self.server()
        fast = server.aor_development.ephemeral_coordination.runtime
        fast.present({
            "aid": "fast-only",
            "epoch": "e-fast",
            "ttl_ms": 10000,
            "capabilities": ["routing"],
            "need_offer_summary": {"need": ["review"]},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": "source:fast-only",
        })

        observed = SynapseObserverRuntime(server).observe(shared_remote_mode="BEST_EFFORT")
        inventory = observed["communication_plane_inventory"]
        self.assertEqual(inventory["version"], VERSION)
        self.assertEqual(inventory["fast_plane"]["fresh_presence_count"], 1)
        self.assertEqual(inventory["fast_plane"]["fresh_presence"][0]["aid"], "fast-only")
        self.assertEqual(inventory["identity_join_policy"], "NO_AUTOMATIC_CROSS_PLANE_IDENTITY_JOIN")
        self.assertNotIn("fast-only", [row["agent_id"] for row in observed["agents"]])

    def test_real_synapse_envelope_is_installed_while_optional_federation_and_escalation_are_unobserved(self):
        server = self.server()
        inventory = SynapseObserverRuntime(server).observe(shared_remote_mode="BEST_EFFORT")["communication_plane_inventory"]
        optional = inventory["optional_components"]
        self.assertTrue(optional["synapse_envelope"]["installed"])
        self.assertEqual(optional["synapse_envelope"]["schema"], "ATHENA.SYNAPSE.ENVELOPE.V1")
        self.assertFalse(optional["federation_ephemeral"]["installed"])
        self.assertFalse(optional["ephemeral_durable_escalation"]["installed"])
        edge_map = {(row["src"], row["dst"]): row for row in inventory["bridge_edges"]}
        self.assertEqual(edge_map[("LIMINAL_BEACON", "SYNAPSE_ENVELOPE")]["standing"], "INSTALLED_EXPLICIT_PROJECTION")
        self.assertEqual(edge_map[("FEDERATION_SOURCE_CURSOR", "EPHEMERAL_SQLITE")]["standing"], "OPTIONAL_BRIDGE_UNOBSERVED")
        self.assertEqual(edge_map[("EPHEMERAL_SQLITE", "MESSAGE_BOARD")]["standing"], "DECLARED_MATERIAL_ESCALATION_RESIDUAL_UNINSTALLED")

    def test_plane_resource_and_manifest_are_discoverable(self):
        server = self.server()
        listed = handle(server, {"jsonrpc": "2.0", "id": 1, "method": "resources/list"})
        self.assertIn(RESOURCE_URI, {row["uri"] for row in listed["result"]["resources"]})

        read = handle(server, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": RESOURCE_URI},
        })
        payload = json.loads(read["result"]["contents"][0]["text"])
        self.assertEqual(payload["version"], VERSION)
        self.assertEqual(payload["authority"], "READ_ONLY_NAVIGATION_OBSERVER")

        manifest = handle(server, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": "athena://manifest"},
        })
        manifest_payload = json.loads(manifest["result"]["contents"][0]["text"])
        self.assertEqual(manifest_payload["communication_plane_inventory"]["resource"], RESOURCE_URI)
        self.assertIn("COMMUNICATION_PLANE_INVENTORY_V1_READ_ONLY", manifest_payload["extensions"])

    def test_inventory_observation_mutates_no_durable_message_or_claim_state(self):
        server = self.server()
        before = server.git.head()
        observed = SynapseObserverRuntime(server).observe(shared_remote_mode="BEST_EFFORT")
        after = server.git.head()
        self.assertEqual(before, after)
        self.assertEqual(observed["communication_plane_inventory"]["authority"], "READ_ONLY_NAVIGATION_OBSERVER")
        self.assertEqual(observed["metrics"]["durable_active"], 0)


if __name__ == "__main__":
    unittest.main()
