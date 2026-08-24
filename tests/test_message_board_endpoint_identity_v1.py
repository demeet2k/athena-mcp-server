from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import AGENT_ROOT, MESSAGE_BOARD_TOOLS, MessageBoardRuntime
from athena_mcp.message_board_endpoint_identity import (
    IDENTITY_ARTIFACT,
    endpoint_identity_digest,
    normalize_endpoint_identity,
)
from athena_mcp.synapse_mcp_contract import SYNAPSE_MCP_CONTRACT_DIGEST


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
    )
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _clone(remote: Path, dest: Path) -> None:
    proc = subprocess.run(
        ["git", "clone", str(remote), str(dest)],
        text=True,
        capture_output=True,
    )
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(dest, "config", "user.name", "test")
    _run(dest, "config", "user.email", "test@example.invalid")


def _identity(organ_id: str, oid: str) -> dict:
    return {
        "artifact": IDENTITY_ARTIFACT,
        "organ_id": organ_id,
        "oid": oid,
        "fingerprint": ["schema:v1", f"organ:{organ_id}"],
        "lineage": f"{organ_id}@test",
    }


class MessageBoardEndpointIdentityTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        remote = base / "shared.git"
        subprocess.run(
            ["git", "init", "--bare", str(remote)],
            check=True,
            capture_output=True,
        )
        seed = base / "seed"
        seed.mkdir()
        _run(seed, "init", "-b", "master")
        _run(seed, "config", "user.name", "test")
        _run(seed, "config", "user.email", "test@example.invalid")
        (seed / "seed.txt").write_text("seed\n", encoding="utf-8")
        _run(seed, "add", ".")
        _run(seed, "commit", "-m", "seed")
        _run(seed, "remote", "add", "origin", str(remote))
        _run(seed, "push", "-u", "origin", "master")
        subprocess.run(
            [
                "git",
                "--git-dir",
                str(remote),
                "symbolic-ref",
                "HEAD",
                "refs/heads/master",
            ],
            check=True,
        )
        a, b, legacy = base / "a", base / "b", base / "legacy"
        _clone(remote, a)
        _clone(remote, b)
        _clone(remote, legacy)
        return a, b, legacy

    @staticmethod
    def _runtime(root: Path) -> MessageBoardRuntime:
        return MessageBoardRuntime(GitBackend(root))

    def test_tool_schema_exposes_optional_exact_endpoint_identity(self):
        schema = MESSAGE_BOARD_TOOLS[0]["inputSchema"]
        self.assertIn("endpoint_identity", schema["properties"])
        identity_schema = schema["properties"]["endpoint_identity"]
        self.assertFalse(identity_schema["additionalProperties"])
        self.assertEqual(identity_schema["properties"]["artifact"]["const"], IDENTITY_ARTIFACT)

    def test_contract_digest_is_canonical_sha256(self):
        self.assertRegex(SYNAPSE_MCP_CONTRACT_DIGEST, r"^sha256:[0-9a-f]{64}$")

    def test_identity_digest_is_order_invariant_for_fingerprint(self):
        left = _identity("coord.synapse", "OID:coord.synapse")
        right = dict(left)
        right["fingerprint"] = list(reversed(left["fingerprint"]))
        self.assertEqual(endpoint_identity_digest(left), endpoint_identity_digest(right))
        self.assertEqual(
            normalize_endpoint_identity(right)["fingerprint"],
            sorted(left["fingerprint"]),
        )

    def test_invalid_or_ambiguous_identity_is_rejected(self):
        value = _identity("coord.synapse", "OID:coord.synapse")
        value["fingerprint"] = ["duplicate", "duplicate"]
        with self.assertRaisesRegex(ValueError, "unique"):
            normalize_endpoint_identity(value)
        value = _identity("coord.synapse", "OID:coord.synapse")
        value["extra"] = "authority"
        with self.assertRaisesRegex(ValueError, "fields must match"):
            normalize_endpoint_identity(value)

    def test_presence_message_and_ack_preserve_target_identity_and_contract_digest(self):
        a, b, _ = self._fixture()
        runtime_a = self._runtime(a)
        runtime_b = self._runtime(b)
        source_identity = _identity("coord.synapse", "OID:coord.synapse")
        target_identity = _identity("transport.mcp", "OID:transport.mcp")
        source_digest = endpoint_identity_digest(source_identity)
        target_digest = endpoint_identity_digest(target_identity)

        present_a = runtime_a.call_tool(
            "athena_message_board",
            {
                "action": "present",
                "agent_id": "synapse-agent",
                "task": "route typed synapse packet",
                "work_key": "SYNAPSE:ROUTE",
                "endpoint_identity": source_identity,
            },
        )
        self.assertEqual(present_a["status"], "PRESENT", present_a)
        self.assertEqual(present_a["presence"]["endpoint_identity_digest"], source_digest)
        self.assertEqual(present_a["presence"]["synapse_contract_digest"], SYNAPSE_MCP_CONTRACT_DIGEST)

        present_b = runtime_b.call_tool(
            "athena_message_board",
            {
                "action": "present",
                "agent_id": "mcp-agent",
                "task": "consume typed synapse packet",
                "work_key": "MCP:CONSUME",
                "endpoint_identity": target_identity,
            },
        )
        self.assertEqual(present_b["status"], "PRESENT", present_b)
        self.assertEqual(present_b["presence"]["endpoint_identity_digest"], target_digest)
        self.assertEqual(present_b["presence"]["synapse_contract_digest"], SYNAPSE_MCP_CONTRACT_DIGEST)

        post = runtime_a.call_tool(
            "athena_message_board",
            {
                "action": "post",
                "agent_id": "synapse-agent",
                "message": "typed-envelope",
                "message_kind": "HANDOFF",
                "recipients": ["mcp-agent"],
            },
        )
        self.assertEqual(post["status"], "POSTED", post)
        self.assertTrue(post["durable_return"], post)
        payload = post["message_event"]["payload"]
        self.assertEqual(payload["actor_endpoint_identity_digest"], source_digest)
        self.assertEqual(payload["synapse_contract_digest"], SYNAPSE_MCP_CONTRACT_DIGEST)
        self.assertEqual(
            payload["recipient_endpoint_identity_digests"],
            {"mcp-agent": target_digest},
        )

        ack = runtime_b.call_tool(
            "athena_message_board",
            {
                "action": "ack",
                "agent_id": "mcp-agent",
                "message_id": post["message_event"]["event_id"],
            },
        )
        self.assertEqual(ack["status"], "ACKED", ack)
        self.assertTrue(ack["durable_return"], ack)
        self.assertEqual(
            ack["ack_event"]["payload"]["actor_endpoint_identity_digest"],
            target_digest,
        )
        self.assertEqual(
            ack["ack_event"]["payload"]["synapse_contract_digest"],
            SYNAPSE_MCP_CONTRACT_DIGEST,
        )
        self.assertEqual(
            ack["ack_event"]["payload"]["message_id"],
            post["message_event"]["event_id"],
        )

    def test_stale_presence_contract_cannot_be_projected_as_current_binding(self):
        a, b, _ = self._fixture()
        runtime_a = self._runtime(a)
        runtime_b = self._runtime(b)
        source_identity = _identity("coord.synapse", "OID:coord.synapse")
        target_identity = _identity("transport.mcp", "OID:transport.mcp")
        self.assertEqual(
            runtime_a.present(
                agent_id="synapse-agent",
                task="route typed synapse packet",
                endpoint_identity=source_identity,
            )["status"],
            "PRESENT",
        )
        self.assertEqual(
            runtime_b.present(
                agent_id="mcp-agent",
                task="consume typed synapse packet",
                endpoint_identity=target_identity,
            )["status"],
            "PRESENT",
        )

        presence_path = b / AGENT_ROOT / "mcp-agent.json"
        value = json.loads(presence_path.read_text(encoding="utf-8"))
        value["synapse_contract_digest"] = "sha256:" + "0" * 64
        presence_path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _run(b, "add", str(Path(AGENT_ROOT) / "mcp-agent.json"))
        _run(b, "commit", "-m", "test stale endpoint contract")
        _run(b, "push", "origin", "master")

        post = runtime_a.post(
            agent_id="synapse-agent",
            message="typed-envelope",
            message_kind="HANDOFF",
            recipients=["mcp-agent"],
        )
        self.assertEqual(post["status"], "POSTED", post)
        payload = post["message_event"]["payload"]
        self.assertEqual(payload["recipient_endpoint_identity_digests"], {})
        self.assertEqual(payload["stale_endpoint_contract_recipients"], ["mcp-agent"])
        self.assertEqual(payload["synapse_contract_digest"], SYNAPSE_MCP_CONTRACT_DIGEST)

        ack = runtime_b.ack(
            agent_id="mcp-agent",
            message_id=post["message_event"]["event_id"],
        )
        self.assertEqual(ack["status"], "ACKED", ack)
        self.assertNotIn("actor_endpoint_identity_digest", ack["ack_event"]["payload"])
        self.assertEqual(
            ack["ack_event"]["payload"]["synapse_contract_digest"],
            SYNAPSE_MCP_CONTRACT_DIGEST,
        )

    def test_existing_presence_cannot_silently_change_endpoint_identity(self):
        a, _, _ = self._fixture()
        runtime = self._runtime(a)
        first = runtime.present(
            agent_id="agent-a",
            task="stable task",
            work_key="WK:STABLE",
            endpoint_identity=_identity("coord.synapse", "OID:coord.synapse"),
        )
        self.assertEqual(first["status"], "PRESENT", first)
        switched = runtime.present(
            agent_id="agent-a",
            task="stable task",
            work_key="WK:STABLE",
            endpoint_identity=_identity("transport.mcp", "OID:transport.mcp"),
        )
        self.assertEqual(switched["status"], "ENDPOINT_IDENTITY_MISMATCH_HOLD", switched)
        self.assertNotEqual(
            switched["requested_endpoint_identity_digest"],
            switched["existing_endpoint_identity_digest"],
        )

    def test_legacy_presence_cannot_retroactively_claim_endpoint_identity(self):
        _, _, legacy = self._fixture()
        runtime = self._runtime(legacy)
        first = runtime.present(
            agent_id="legacy-agent",
            task="legacy task",
            work_key="WK:LEGACY",
        )
        self.assertEqual(first["status"], "PRESENT", first)
        claimed = runtime.present(
            agent_id="legacy-agent",
            task="legacy task",
            work_key="WK:LEGACY",
            endpoint_identity=_identity("coord.synapse", "OID:coord.synapse"),
        )
        self.assertEqual(claimed["status"], "ENDPOINT_IDENTITY_MISSING_HOLD", claimed)
        self.assertIsNone(claimed["existing_endpoint_identity_digest"])

    def test_legacy_presence_and_message_flow_remain_valid_without_identity(self):
        _, _, legacy = self._fixture()
        runtime = self._runtime(legacy)
        present = runtime.present(agent_id="legacy-agent", task="legacy task")
        self.assertEqual(present["status"], "PRESENT", present)
        self.assertNotIn("endpoint_identity", present["presence"])
        self.assertNotIn("synapse_contract_digest", present["presence"])
        post = runtime.post(agent_id="legacy-agent", message="legacy message")
        self.assertEqual(post["status"], "POSTED", post)
        self.assertEqual(
            post["message_event"]["payload"]["recipient_endpoint_identity_digests"],
            {},
        )
        self.assertEqual(
            post["message_event"]["payload"]["synapse_contract_digest"],
            SYNAPSE_MCP_CONTRACT_DIGEST,
        )
        self.assertNotIn(
            "actor_endpoint_identity_digest",
            post["message_event"]["payload"],
        )


if __name__ == "__main__":
    unittest.main()
