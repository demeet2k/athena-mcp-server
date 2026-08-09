from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MESSAGE_BOARD_TOOL_NAMES, MessageBoardRuntime


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture(base: Path, clone_names=("b",)):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    _write(local, "seed.txt", "seed\n")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    clones = []
    for name in clone_names:
        clone = base / name
        proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
        if proc.returncode:
            raise AssertionError(proc.stderr or proc.stdout)
        _run(clone, "config", "user.name", name)
        _run(clone, "config", "user.email", f"{name}@example.invalid")
        clones.append(clone)
    return local, clones


class MessageBoardTests(unittest.TestCase):
    def _boards(self, count=2):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, clones = _fixture(Path(td.name), tuple(f"c{i}" for i in range(count - 1)))
        roots = [local, *clones]
        return [MessageBoardRuntime(GitBackend(root)) for root in roots], roots

    def test_present_publishes_and_read_sees_shared_presence(self):
        boards, _ = self._boards()
        result = boards[0].present(agent_id="builder", task="Build message board", work_key="message-board-v1", targets=["athena_mcp/message_board.py"])
        self.assertEqual(result["status"], "PRESENT")
        self.assertTrue(result["durable_return"])
        snapshot = boards[1].read(agent_id="reader")
        self.assertEqual(snapshot["status"], "OK")
        self.assertTrue(snapshot["shared_frontier_verified"])
        self.assertEqual([row["agent_id"] for row in snapshot["active"]], ["builder"])

    def test_exact_task_or_target_collision_holds_instead_of_duplicate_build(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Build the message board")
        duplicate = boards[1].present(agent_id="b", task="  BUILD the   message board ")
        self.assertEqual(duplicate["status"], "DUPLICATE_WORK_HOLD")
        self.assertIn("EXACT_TASK", duplicate["conflicts"][0]["reasons"])

    def test_join_allows_declared_collaboration_on_same_lane(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Build message board", work_key="board", targets=["athena_mcp/message_board.py"])
        joined = boards[1].join(agent_id="b", join_agent_id="a", details="Taking tests")
        self.assertEqual(joined["status"], "JOINED")
        self.assertEqual(joined["presence"]["mode"], "COLLABORATOR")
        overlaps = boards[0].read()["exact_overlaps"]
        self.assertTrue(overlaps)
        self.assertTrue(all(edge["intentional"] for edge in overlaps))

    def test_replica_requires_explicit_reason_but_can_overlap(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Benchmark solver", work_key="solver")
        with self.assertRaises(ValueError):
            boards[1].present(agent_id="b", task="Benchmark solver", work_key="solver", mode="REPLICA")
        replica = boards[1].present(agent_id="b", task="Benchmark solver", work_key="solver", mode="REPLICA", replication_reason="independent reproducibility witness")
        self.assertEqual(replica["status"], "PRESENT")
        self.assertTrue(replica["hard_overlap_override"])

    def test_message_ack_and_release_preserve_communication_history(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Build A", work_key="a")
        boards[1].present(agent_id="b", task="Build B", work_key="b")
        posted = boards[1].post(agent_id="b", recipients=["a"], message_kind="BLOCKER", message="Need the schema contract.")
        message_id = posted["message_event"]["event_id"]
        unread = boards[0].read(agent_id="a")["unread_messages"]
        self.assertEqual(unread[-1]["event_id"], message_id)
        acked = boards[0].ack(agent_id="a", message_id=message_id)
        self.assertEqual(acked["status"], "ACKED")
        self.assertEqual(boards[0].read(agent_id="a")["unread_messages"], [])
        claim_id = next(row["claim_id"] for row in boards[1].read()["active"] if row["agent_id"] == "b")
        released = boards[1].release(
            agent_id="b",
            expected_claim_id=claim_id,
            release_status="DONE",
            outcome="build complete",
            completion_receipt={
                "claim_id": claim_id,
                "agent_id": "b",
                "result_refs": ["git:result"],
                "owned_delta_targets": [],
                "verification": {
                    "executed": 1,
                    "passed": 1,
                    "failed": 0,
                    "skipped": 0,
                    "provider_ref": "local:test_message_board",
                    "witness_digest": "a" * 64,
                },
            },
        )
        self.assertEqual(released["status"], "RELEASED")
        history = boards[0].read(include_stale=True)
        self.assertEqual([row["agent_id"] for row in history["active"]], ["a"])
        self.assertIn(("b", "RELEASED"), [(row["agent_id"], row["lease_state"]) for row in history["inactive"]])
        self.assertTrue(any(event["event_id"] == message_id for event in history["recent_events"]))

    def test_heartbeat_renews_active_lease(self):
        boards, _ = self._boards()
        present = boards[0].present(agent_id="a", task="Build A", work_key="a", lease_seconds=60)
        before = present["presence"]["expires_at"]
        heartbeat = boards[0].heartbeat(agent_id="a", expected_claim_id=present["presence"]["claim_id"], lease_seconds=3600, note="still working")
        self.assertEqual(heartbeat["status"], "HEARTBEAT")
        self.assertGreater(heartbeat["presence"]["expires_at"], before)

    def test_fuzzy_overlap_warns_but_is_not_duplicate_proof(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Implement durable message board API for agents")
        result = boards[1].present(agent_id="b", task="Implement durable message board API for worker agents")
        self.assertEqual(result["status"], "PRESENT")
        self.assertTrue(result["potential_overlaps"])

    def test_publish_race_rehydrates_and_loser_observes_winner_claim(self):
        boards, roots = self._boards(count=2)
        loser, winner = boards[0], boards[1]
        original_publish = loser.remote_sync.publish
        injected = {"done": False}

        def racing_publish(expected_git_head, remote="origin"):
            if not injected["done"]:
                injected["done"] = True
                won = winner.present(agent_id="winner", task="Build X", work_key="x", targets=["x.py"])
                self.assertEqual(won["status"], "PRESENT")
            return original_publish(expected_git_head, remote)

        loser.remote_sync.publish = racing_publish
        result = loser.present(agent_id="loser", task="Build X", work_key="x", targets=["x.py"])
        self.assertEqual(result["status"], "DUPLICATE_WORK_HOLD")
        self.assertEqual(result["conflicts"][0]["agent"]["agent_id"], "winner")
        self.assertEqual(_run(roots[0], "rev-parse", "HEAD"), _run(roots[1], "rev-parse", "HEAD"))

    def test_tool_surface_is_one_message_board_tool(self):
        self.assertEqual(MESSAGE_BOARD_TOOL_NAMES, {"athena_message_board"})

    def test_nfkc_and_dot_segment_aliases_collide(self):
        boards, _ = self._boards()
        boards[0].present(agent_id="a", task="Build A", work_key="ＲＵＮＴＩＭＥ", targets=["Src/./A/../Core.py"])
        duplicate = boards[1].present(agent_id="b", task="Build B", work_key="runtime", targets=["src/core.py"])
        self.assertEqual(duplicate["status"], "DUPLICATE_WORK_HOLD")
        reasons = duplicate["conflicts"][0]["reasons"]
        self.assertIn("EXACT_WORK_KEY", reasons)
        self.assertIn("TARGET:src/core.py", reasons)

    def test_old_claim_cannot_heartbeat_or_release_new_same_agent_claim(self):
        boards, _ = self._boards(count=1)
        first = boards[0].present(agent_id="a", task="First", work_key="first")
        first_id = first["presence"]["claim_id"]
        boards[0].release(agent_id="a", expected_claim_id=first_id, release_status="PAUSED", outcome="switch")
        second = boards[0].present(agent_id="a", task="Second", work_key="second")
        second_id = second["presence"]["claim_id"]
        self.assertNotEqual(first_id, second_id)
        heartbeat = boards[0].heartbeat(agent_id="a", expected_claim_id=first_id)
        release = boards[0].release(agent_id="a", expected_claim_id=first_id, release_status="PAUSED")
        self.assertEqual(heartbeat["status"], "STALE_CLAIM_HOLD")
        self.assertEqual(release["status"], "STALE_CLAIM_HOLD")
        self.assertEqual(boards[0].read()["active"][0]["claim_id"], second_id)

    def test_done_without_structured_nonempty_verification_is_held(self):
        boards, _ = self._boards(count=1)
        present = boards[0].present(agent_id="a", task="Build", work_key="build", targets=["x.py"])
        claim_id = present["presence"]["claim_id"]
        missing = boards[0].release(agent_id="a", expected_claim_id=claim_id, release_status="DONE", outcome="trust me")
        self.assertEqual(missing["status"], "COMPLETION_GATE_HOLD")
        zero = boards[0].release(
            agent_id="a",
            expected_claim_id=claim_id,
            release_status="DONE",
            completion_receipt={
                "claim_id": claim_id,
                "agent_id": "a",
                "result_refs": ["git:x"],
                "owned_delta_targets": ["x.py"],
                "verification": {
                    "executed": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "provider_ref": "provider",
                    "witness_digest": "a" * 64,
                },
            },
        )
        self.assertEqual(zero["status"], "COMPLETION_GATE_HOLD")
        self.assertEqual(zero["reason"], "COMPLETION_VERIFICATION_NOT_NONEMPTY_CLEAN_PASS")

    def test_structural_completion_receipt_never_grants_task_authority(self):
        boards, _ = self._boards(count=1)
        present = boards[0].present(agent_id="a", task="Build", work_key="build", targets=["x.py"])
        claim_id = present["presence"]["claim_id"]
        result = boards[0].release(
            agent_id="a",
            expected_claim_id=claim_id,
            release_status="DONE",
            completion_receipt={
                "claim_id": claim_id,
                "agent_id": "a",
                "result_refs": ["git:x"],
                "owned_delta_targets": ["x.py"],
                "verification": {
                    "executed": 3,
                    "passed": 3,
                    "failed": 0,
                    "skipped": 0,
                    "provider_ref": "provider:run/1",
                    "witness_digest": "b" * 64,
                },
            },
        )
        self.assertEqual(result["status"], "RELEASED")
        self.assertFalse(result["completion_authority"])
        self.assertEqual(result["presence"]["completion_standing"], "STRUCTURALLY_VALID_PROVIDER_REF_UNVERIFIED")

    def test_inactive_agent_cannot_ack_message(self):
        boards, _ = self._boards(count=2)
        boards[0].present(agent_id="a", task="A", work_key="a")
        posted = boards[0].post(agent_id="a", message="hello")
        ack = boards[1].ack(agent_id="inactive", message_id=posted["message_event"]["event_id"])
        self.assertEqual(ack["status"], "NOT_PRESENT_HOLD")


if __name__ == "__main__":
    unittest.main()
