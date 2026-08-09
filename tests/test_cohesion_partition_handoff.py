from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.cohesion_partition_handoff import CohesionPartitionHandoffRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


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


class CohesionPartitionHandoffTests(unittest.TestCase):
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
        self.runtime_a = CohesionPartitionHandoffRuntime(self.a)
        self.runtime_b = CohesionPartitionHandoffRuntime(self.b)

    def present(self, board, agent, task, work_key, targets):
        result = board.present(
            agent_id=agent,
            task=task,
            work_key=work_key,
            targets=targets,
        )
        self.assertEqual(result["status"], "PRESENT", result)
        return result

    @staticmethod
    def packet(
        packet_id,
        work_key,
        targets,
        *,
        dependencies=None,
        shared_sinks=None,
        integration_order=0,
        exact_refs=None,
    ):
        return {
            "packet_id": packet_id,
            "work_key": work_key,
            "targets": list(targets),
            "dependencies": list(dependencies or []),
            "shared_sinks": list(shared_sinks or []),
            "integration_order": integration_order,
            "merge_strategy": "deterministic-merge",
            "exact_refs": list(exact_refs or []),
            "verification_requirements": [f"verify:{packet_id}"],
            "handoff_conditions": [f"handoff:{packet_id}"],
            "acceptance_criteria": [f"accept:{packet_id}"],
        }

    def test_disjoint_partition_builds_parallel_group_without_mutating_claims(self):
        self.present(self.board_a, "planner", "Partition goal", "goal-root", ["plan.md"])
        before = {row["agent_id"]: row["claim_id"] for row in self.board_a.read()["active"]}
        result = self.runtime_a.partition(
            "PART.1",
            "planner",
            "goal.partition",
            [
                self.packet("A", "work.a", ["src/a.py#f"], integration_order=0),
                self.packet("B", "work.b", ["src/b.py#g"], integration_order=0),
            ],
        )
        self.assertEqual(result["status"], "COHESION_PARTITION_PROPOSED")
        proof = result["partition"]["proof"]
        self.assertEqual(proof["parallel_groups"], [["A", "B"]])
        self.assertEqual(proof["serialization_edges"], [])
        self.assertFalse(result["assignment_authority"])
        after = {row["agent_id"]: row["claim_id"] for row in self.board_a.read()["active"]}
        self.assertEqual(before, after)

    def test_duplicate_work_key_and_unsafe_owned_target_hold(self):
        self.present(self.board_a, "planner", "Partition goal", "goal-root", ["plan.md"])
        duplicate = self.runtime_a.partition(
            "PART.DUP",
            "planner",
            "goal.partition",
            [
                self.packet("A", "same", ["src/a.py#f"]),
                self.packet("B", "same", ["src/b.py#g"]),
            ],
        )
        self.assertEqual(duplicate["status"], "COHESION_PARTITION_HOLD")
        self.assertTrue(any(reason.startswith("DUPLICATE_WORK_KEY:") for reason in duplicate["errors"]))

        collision = self.runtime_a.partition(
            "PART.COLLIDE",
            "planner",
            "goal.partition",
            [
                self.packet("A", "work.a", ["src/shared.py#f"]),
                self.packet("B", "work.b", ["src/shared.py#f"]),
            ],
        )
        self.assertEqual(collision["status"], "COHESION_PARTITION_HOLD")
        self.assertTrue(any(reason.startswith("OWNED_TARGET_COLLISION:") for reason in collision["errors"]))

    def test_declared_shared_sink_is_serialized_by_integration_order(self):
        self.present(self.board_a, "planner", "Partition shared sink", "goal-root", ["plan.md"])
        shared = "src/index.py#registry"
        result = self.runtime_a.partition(
            "PART.SINK",
            "planner",
            "goal.partition",
            [
                self.packet(
                    "A", "work.a", ["src/a.py#f", shared], shared_sinks=[shared], integration_order=10
                ),
                self.packet(
                    "B", "work.b", ["src/b.py#g", shared], shared_sinks=[shared], integration_order=20
                ),
            ],
        )
        self.assertEqual(result["status"], "COHESION_PARTITION_PROPOSED")
        proof = result["partition"]["proof"]
        self.assertEqual(proof["parallel_groups"], [["A"], ["B"]])
        self.assertEqual(proof["serialization_edges"][0]["from"], "A")
        self.assertEqual(proof["serialization_edges"][0]["to"], "B")
        self.assertEqual(proof["serialization_edges"][0]["shared_sinks"], [shared])

        same_order = self.runtime_a.partition(
            "PART.SINK.BAD",
            "planner",
            "goal.partition",
            [
                self.packet("A", "x.a", [shared], shared_sinks=[shared], integration_order=10),
                self.packet("B", "x.b", [shared], shared_sinks=[shared], integration_order=10),
            ],
        )
        self.assertEqual(same_order["status"], "COHESION_PARTITION_HOLD")
        self.assertTrue(any(reason.startswith("SHARED_SINK_ORDER_REQUIRED:") for reason in same_order["errors"]))

    def test_dependency_cycle_holds_and_valid_dependency_layers(self):
        self.present(self.board_a, "planner", "Partition dependencies", "goal-root", ["plan.md"])
        cycle = self.runtime_a.partition(
            "PART.CYCLE",
            "planner",
            "goal.partition",
            [
                self.packet("A", "work.a", ["a"], dependencies=["B"]),
                self.packet("B", "work.b", ["b"], dependencies=["A"]),
            ],
        )
        self.assertEqual(cycle["status"], "COHESION_PARTITION_HOLD")
        self.assertIn("PARTITION_DEPENDENCY_OR_SERIALIZATION_CYCLE", cycle["errors"])

        valid = self.runtime_a.partition(
            "PART.DAG",
            "planner",
            "goal.partition",
            [
                self.packet("A", "work.a2", ["a2"]),
                self.packet("B", "work.b2", ["b2"], dependencies=["A"]),
                self.packet("C", "work.c2", ["c2"], dependencies=["A"]),
            ],
        )
        self.assertEqual(valid["partition"]["proof"]["parallel_groups"], [["A"], ["B", "C"]])

    def test_partition_replay_is_cross_clone_idempotent_and_changed_id_conflicts(self):
        self.present(self.board_a, "planner", "Partition goal", "goal-root", ["plan.md"])
        packets = [
            self.packet("A", "work.a", ["a"], exact_refs=["ref://a"]),
            self.packet("B", "work.b", ["b"], exact_refs=["ref://b"]),
        ]
        first = self.runtime_a.partition("PART.REPLAY", "planner", "goal.partition", packets)
        self.assertEqual(first["status"], "COHESION_PARTITION_PROPOSED")
        replay = self.runtime_b.partition("PART.REPLAY", "planner", "goal.partition", list(reversed(packets)))
        self.assertEqual(replay["status"], "COHESION_PARTITION_ALREADY_PROPOSED")
        self.assertTrue(replay["idempotent"])
        self.assertEqual(
            replay["partition"]["partition_proof_digest"], first["partition"]["partition_proof_digest"]
        )
        changed = [
            self.packet("A", "work.a.changed", ["a"], exact_refs=["ref://a"]),
            packets[1],
        ]
        with self.assertRaisesRegex(ValueError, "COHESION_PARTITION_ID_CONFLICT"):
            self.runtime_a.partition("PART.REPLAY", "planner", "goal.partition", changed)

    def test_handoff_waits_for_receiver_ack_and_never_releases_claim(self):
        sender = self.present(self.board_a, "sender", "Build sender lane", "sender-work", ["sender.py"])
        self.present(self.board_b, "receiver", "Receive next lane", "receiver-work", ["receiver.py"])
        result = self.runtime_a.handoff(
            "HAND.1",
            "sender",
            "receiver",
            ["git://head", "test://suite"],
            "implemented packet A",
            "packet B remains",
            ["authority unchanged"],
            ["test://suite"],
            [],
            "receiver verifies packet B",
            "MESSAGE_ACK",
        )
        self.assertEqual(result["status"], "COHESION_HANDOFF_AWAITING_RECEIPT")
        self.assertFalse(result["claim_release_allowed"])
        self.assertTrue(result["claim_still_active"])
        self.assertFalse(result["claim_release_performed"])
        message_id = result["message_id"]

        acked = self.board_b.ack(agent_id="receiver", message_id=message_id)
        self.assertEqual(acked["status"], "ACKED")
        replay = self.runtime_a.handoff(
            "HAND.1",
            "sender",
            "receiver",
            ["git://head", "test://suite"],
            "implemented packet A",
            "packet B remains",
            ["authority unchanged"],
            ["test://suite"],
            [],
            "receiver verifies packet B",
            "MESSAGE_ACK",
        )
        self.assertEqual(replay["status"], "COHESION_HANDOFF_ACKNOWLEDGED")
        self.assertTrue(replay["receiver_acknowledged"])
        self.assertTrue(replay["claim_release_allowed"])
        self.assertFalse(replay["claim_release_performed"])
        active = {row["agent_id"]: row for row in self.board_a.read()["active"]}
        self.assertEqual(active["sender"]["claim_id"], sender["presence"]["claim_id"])

    def test_handoff_detects_sender_release_before_required_ack(self):
        self.present(self.board_a, "sender", "Build sender lane", "sender-work", ["sender.py"])
        self.present(self.board_b, "receiver", "Receive next lane", "receiver-work", ["receiver.py"])
        routed = self.runtime_a.handoff(
            "HAND.EARLY",
            "sender",
            "receiver",
            ["ref://delta"],
            "delta done",
            "residual remains",
            ["invariant"],
            ["test://one"],
            [],
            "continue",
            "MESSAGE_ACK",
        )
        self.assertFalse(routed["claim_release_allowed"])
        released = self.board_a.release(agent_id="sender", release_status="DONE", outcome="released too early")
        self.assertEqual(released["status"], "RELEASED")
        self.board_b.ack(agent_id="receiver", message_id=routed["message_id"])
        replay = self.runtime_b.handoff(
            "HAND.EARLY",
            "sender",
            "receiver",
            ["ref://delta"],
            "delta done",
            "residual remains",
            ["invariant"],
            ["test://one"],
            [],
            "continue",
            "MESSAGE_ACK",
        )
        self.assertEqual(replay["status"], "COHESION_HANDOFF_EARLY_RELEASE_OBSERVED")
        self.assertTrue(replay["early_release_observed"])
        self.assertTrue(replay["receiver_acknowledged"])
        self.assertTrue(replay["claim_release_allowed"])
        self.assertFalse(replay["claim_still_active"])

    def test_partition_linked_handoff_requires_partition_exact_refs(self):
        self.present(self.board_a, "sender", "Partition sender", "root", ["plan.md"])
        self.present(self.board_b, "receiver", "Receiver", "receiver", ["receiver.md"])
        self.runtime_a.partition(
            "PART.HAND",
            "sender",
            "goal.partition",
            [
                self.packet("A", "packet.a", ["a"], exact_refs=["ref://a-required"]),
                self.packet("B", "packet.b", ["b"]),
            ],
        )
        with self.assertRaisesRegex(ValueError, "COHESION_HANDOFF_MISSING_PARTITION_REFS"):
            self.runtime_a.handoff(
                "HAND.MISSING",
                "sender",
                "receiver",
                ["ref://other"],
                "done",
                "residual",
                ["invariant"],
                ["test://one"],
                [],
                "next",
                "MESSAGE_ACK",
                partition_id="PART.HAND",
                packet_id="A",
                work_key="packet.a",
            )

        good = self.runtime_a.handoff(
            "HAND.GOOD",
            "sender",
            "receiver",
            ["ref://a-required", "ref://other"],
            "done",
            "residual",
            ["invariant"],
            ["test://one"],
            [],
            "next",
            "MESSAGE_ACK",
            partition_id="PART.HAND",
            packet_id="A",
            work_key="packet.a",
        )
        self.assertEqual(good["handoff"]["partition_id"], "PART.HAND")
        self.assertEqual(good["handoff"]["packet_id"], "A")
        self.assertIsNotNone(good["handoff"]["partition_packet_digest"])


if __name__ == "__main__":
    unittest.main()
