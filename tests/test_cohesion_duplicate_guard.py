from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from athena_mcp.aor_collective_transport_surface import AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES
from athena_mcp.cohesion_duplicate_guard import augment_cohesion_resource, duplicate_guard
from athena_mcp.cohesion_duplicate_guard_protocol import DUPLICATE_GUARD_TOOL_NAMES
from athena_mcp.cohesion_matchmaking import CohesionMatchmakingRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _clone(remote: Path, destination: Path) -> None:
    proc = subprocess.run(["git", "clone", str(remote), str(destination)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(destination, "config", "user.name", "cohesion-test")
    _run(destination, "config", "user.email", "cohesion-test@example.invalid")


def _fixture(base: Path):
    remote = base / "origin.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    seed = base / "seed"
    seed.mkdir()
    _run(seed, "init", "-b", "master")
    _run(seed, "config", "user.name", "seed")
    _run(seed, "config", "user.email", "seed@example.invalid")
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _run(seed, "add", ".")
    _run(seed, "commit", "-m", "seed")
    _run(seed, "remote", "add", "origin", str(remote))
    _run(seed, "push", "-u", "origin", "master")
    subprocess.run(
        ["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/master"],
        check=True,
        capture_output=True,
    )
    local = base / "local"
    _clone(remote, local)
    return remote, local


def _board_digest(root: Path) -> str:
    board = root / "runtime" / "message_board" / "v1"
    if not board.exists():
        return "ABSENT"
    rows = []
    for path in sorted(p for p in board.rglob("*") if p.is_file()):
        rows.append((str(path.relative_to(root)), path.read_text(encoding="utf-8")))
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


class CohesionDuplicateGuardTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        _, self.root = _fixture(Path(self._td.name))
        self.git = GitBackend(self.root)
        self.board = MessageBoardRuntime(self.git)
        self.runtime = CohesionMatchmakingRuntime(SimpleNamespace(git=self.git))

    def present(self, agent_id: str, task: str, work_key=None, targets=None, mode="PRIMARY", replication_reason=None):
        value = self.board.present(
            agent_id=agent_id,
            task=task,
            work_key=work_key,
            targets=targets,
            mode=mode,
            replication_reason=replication_reason,
        )
        self.assertTrue(value.get("durable_return"), value)
        return value

    def guard(self, **kwargs):
        args = {
            "agent_id": "candidate",
            "task": "build renderer",
            "work_key": None,
            "targets": [],
            "intended_mode": "PRIMARY",
            "shared_remote_mode": "REQUIRED",
        }
        args.update(kwargs)
        return duplicate_guard(self.runtime, **args)

    def test_shared_frontier_required_failure_holds(self):
        _run(self.root, "remote", "set-url", "origin", str(self.root.parent / "missing.git"))
        result = self.guard(task="build parser")
        self.assertEqual(result["classification"], "SHARED_FRONTIER_HOLD")
        self.assertEqual(result["standing"], "HOLD")
        self.assertTrue(result["hard_hold"])
        self.assertFalse(result["claim_authority"])

    def test_clear_lane_allows_proceed_advisory_only(self):
        self.present("worker-a", "build parser", work_key="WK:PARSER")
        result = self.guard(task="build renderer", work_key="WK:RENDERER")
        self.assertEqual(result["classification"], "CLEAR", result)
        proceed = next(row for row in result["treatments"] if row["action"] == "PROCEED")
        self.assertTrue(proceed["eligible"])
        self.assertFalse(proceed["execution_authority"])
        self.assertFalse(result["hard_hold"])

    def test_fuzzy_similarity_is_warning_not_duplicate_proof(self):
        self.present("worker-a", "build agent bootstrap message board gate")
        result = self.guard(task="build agent bootstrap message board integration")
        self.assertEqual(result["classification"], "FUZZY_WARNING_ONLY", result)
        self.assertTrue(result["fuzzy_warnings"])
        self.assertFalse(result["hard_hold"])

    def test_exact_work_key_primary_collision_holds(self):
        self.present("worker-a", "build parser", work_key="WK:PARSER")
        result = self.guard(task="different prose", work_key="WK:PARSER")
        self.assertEqual(result["classification"], "EXACT_DUPLICATE_HOLD", result)
        self.assertIn("EXACT_WORK_KEY", result["conflicts"][0]["reasons"])
        self.assertTrue(result["hard_hold"])
        actions = {row["action"]: row for row in result["treatments"]}
        self.assertTrue(actions["JOIN"]["eligible"])
        self.assertTrue(actions["PIVOT"]["eligible"])
        self.assertTrue(actions["REPLICA"]["eligible"])
        self.assertFalse(actions["PROCEED"]["eligible"])

    def test_exact_task_primary_collision_holds(self):
        self.present("worker-a", "build parser")
        result = self.guard(task="build parser")
        self.assertEqual(result["classification"], "EXACT_DUPLICATE_HOLD", result)
        self.assertIn("EXACT_TASK", result["conflicts"][0]["reasons"])

    def test_target_only_collision_requires_partition_or_other_treatment(self):
        self.present("worker-a", "build parser", targets=["src/shared.py"])
        result = self.guard(task="build renderer", targets=["src/shared.py"])
        self.assertEqual(result["classification"], "SHARED_SINK_HOLD", result)
        self.assertEqual(result["conflicts"][0]["target_overlap"], ["src/shared.py"])
        partition = next(row for row in result["treatments"] if row["action"] == "PARTITION")
        self.assertTrue(partition["eligible"])
        self.assertFalse(result["partition"]["provided"])

    def test_partition_assertion_without_evidence_does_not_clear(self):
        self.present("worker-a", "build parser", targets=["src/shared.py"])
        result = self.guard(
            task="build renderer",
            targets=["src/shared.py"],
            partition_proof={
                "proof_id": "P1",
                "shared_sinks": ["src/shared.py"],
                "disjoint_targets": ["src/a.py", "src/b.py"],
                "evidence_refs": [],
            },
        )
        self.assertEqual(result["classification"], "PARTITION_PROOF_REQUIRED", result)
        self.assertIn("PARTITION_EVIDENCE_REFS_REQUIRED", result["partition"]["reason_codes"])
        self.assertTrue(result["hard_hold"])

    def test_valid_target_only_partition_evidence_returns_option_not_execution(self):
        self.present("worker-a", "build parser", targets=["src/shared.py"])
        result = self.guard(
            task="build renderer",
            targets=["src/shared.py"],
            partition_proof={
                "proof_id": "P2",
                "shared_sinks": ["src/shared.py"],
                "disjoint_targets": ["src/parser-part.py", "src/render-part.py"],
                "evidence_refs": ["spec://partition/P2"],
            },
        )
        self.assertEqual(result["classification"], "PARTITION_CLEARS_TARGET_ONLY", result)
        self.assertEqual(result["standing"], "HOLD_UNTIL_PARTITION_COMMITTED")
        self.assertTrue(result["partition"]["eligible_for_target_partition"])
        self.assertFalse(result["partition"]["independently_verified"])
        self.assertTrue(result["hard_hold"])

    def test_partition_never_erases_exact_work_identity(self):
        self.present("worker-a", "build parser", work_key="WK:PARSER", targets=["src/shared.py"])
        result = self.guard(
            task="different prose",
            work_key="WK:PARSER",
            targets=["src/shared.py"],
            partition_proof={
                "proof_id": "P3",
                "shared_sinks": ["src/shared.py"],
                "disjoint_targets": ["src/a.py", "src/b.py"],
                "evidence_refs": ["spec://partition/P3"],
            },
        )
        self.assertEqual(result["classification"], "EXACT_DUPLICATE_HOLD", result)
        self.assertTrue(result["partition"]["eligible_for_target_partition"])
        partition = next(row for row in result["treatments"] if row["action"] == "PARTITION")
        self.assertFalse(partition["eligible"])

    def test_replica_requires_reason_and_remains_non_evidentiary(self):
        self.present("worker-a", "benchmark kernel", work_key="WK:KERNEL")
        with self.assertRaisesRegex(ValueError, "REPLICA requires replication_reason"):
            self.guard(task="benchmark kernel", work_key="WK:KERNEL", intended_mode="REPLICA")
        result = self.guard(
            task="benchmark kernel",
            work_key="WK:KERNEL",
            intended_mode="REPLICA",
            replication_reason="independent implementation attempt",
        )
        self.assertEqual(result["classification"], "INTENTIONAL_REPLICA", result)
        self.assertFalse(result["hard_hold"])
        self.assertFalse(result["independent_verification"])

    def test_declared_join_must_target_relevant_conflict_and_never_mutates(self):
        first = self.present("worker-a", "build parser", work_key="WK:PARSER")
        head = _run(self.root, "rev-parse", "HEAD")
        before = _board_digest(self.root)
        result = self.guard(task="build parser", work_key="WK:PARSER", join_agent_id="worker-a")
        self.assertEqual(result["classification"], "DECLARED_JOIN", result)
        self.assertEqual(result["standing"], "HOLD_UNTIL_JOIN_EXECUTED")
        self.assertTrue(result["hard_hold"])
        self.assertFalse(result["board_write_performed"])
        self.assertEqual(_run(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual(_board_digest(self.root), before)
        self.assertEqual(first["presence"]["claim_id"], result["conflicts"][0]["presence"]["claim_id"])

        invalid = self.guard(task="build parser", work_key="WK:PARSER", join_agent_id="worker-z")
        self.assertEqual(invalid["classification"], "DECLARED_JOIN_TARGET_INVALID")

    def test_self_active_incompatible_claim_is_distinct(self):
        self.present("candidate", "build parser", work_key="WK:PARSER")
        result = self.guard(task="build renderer", work_key="WK:RENDERER")
        self.assertEqual(result["classification"], "SELF_ACTIVE_CLAIM_CONFLICT", result)
        self.assertIn("TASK", result["self_relation"]["differences"])
        self.assertTrue(result["hard_hold"])

    def test_guard_does_not_write_board_or_advance_head_when_already_fresh(self):
        self.present("worker-a", "build parser", work_key="WK:PARSER")
        head = _run(self.root, "rev-parse", "HEAD")
        before = _board_digest(self.root)
        result = self.guard(task="build renderer", work_key="WK:RENDERER")
        self.assertEqual(result["head_before_sync"], head)
        self.assertEqual(result["head_after_sync"], head)
        self.assertEqual(_run(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual(_board_digest(self.root), before)
        self.assertFalse(result["board_write_performed"])

    def test_mata_semantics_are_not_fabricated(self):
        result = self.guard(task="build parser")
        self.assertFalse(result["mata"]["runtime_available"])
        self.assertEqual(result["mata"]["semantic_relation"], "UNAVAILABLE_NOT_IN_RUNTIME")
        self.assertFalse(result["assignment_authority"])
        self.assertFalse(result["claim_authority"])
        self.assertFalse(result["execution_authority"])

    def test_registration_and_resource_projection_are_additive(self):
        self.assertEqual(DUPLICATE_GUARD_TOOL_NAMES, {"athena_cohesion_duplicate_guard"})
        self.assertIn("athena_cohesion_duplicate_guard", AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES)
        resource = augment_cohesion_resource(self.runtime.resource())
        self.assertIn("athena_cohesion_duplicate_guard", resource["tools"])
        self.assertIn("remaining C3 steering tools 12-15", resource["residual"])
        self.assertEqual(resource["mata_duplicate_adapter"], "UNAVAILABLE_NOT_IN_RUNTIME")


if __name__ == "__main__":
    unittest.main()
