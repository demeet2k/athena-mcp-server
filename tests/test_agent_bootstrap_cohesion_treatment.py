from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.agent_bootstrap import AgentBootstrapRuntime
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
    _run(destination, "config", "user.name", "boot-c3-test")
    _run(destination, "config", "user.email", "boot-c3-test@example.invalid")


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
    a, b, c = base / "a", base / "b", base / "c"
    _clone(remote, a)
    _clone(remote, b)
    _clone(remote, c)
    return remote, a, b, c


def _board_digest(root: Path) -> str:
    board = root / "runtime" / "message_board" / "v1"
    if not board.exists():
        return "ABSENT"
    rows = []
    for path in sorted(p for p in board.rglob("*") if p.is_file()):
        rows.append((str(path.relative_to(root)), path.read_text(encoding="utf-8")))
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


class _Prompt:
    available = True

    def __init__(self, git):
        self.git = git

    def compile(self, task="", profile=None, include_text=False):
        return {
            "profile": profile or "BUILD",
            "selected_modules": ["core"],
            "selected_overlays": [],
            "git_head": self.git.head(),
            "prompt_stack_digest": "p" * 64,
            "ancestry": {"policy": "test"},
        }

    def _safe_rel(self, rel: str) -> Path:
        return self.git.root / rel


class _Frontier:
    def hydrate(self, **kwargs):
        return {
            "status": "HYDRATED",
            "source_ref": kwargs.get("source_ref"),
            "resolved_ref": kwargs.get("source_ref"),
            "source_head": "s" * 40,
            "frontier_digest": "f" * 64,
            "ready_work": [],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {"event_reduced_runs": 1},
            "sched_contract": {"status": "PASS", "contracts": {"reducer": "ok"}},
            "remote_checked": True,
            "fetch_error": None,
        }

    def select(self, **kwargs):
        return {"status": "NO_REPLAYABLE_READY_WORK", "selected": None, "pareto_front": []}


class _Issues:
    def snapshot(self, **kwargs):
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": "demeet2k/Athena",
            "relevant": [],
            "digest": "i" * 64,
            "witness": {"provider": "test", "http_status": 200},
        }


class AgentBootstrapCohesionTreatmentTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        _, self.a, self.b, self.c = _fixture(Path(self._td.name))

    @staticmethod
    def runtime(root: Path):
        git = GitBackend(root)
        return AgentBootstrapRuntime(git, _Prompt(git), _Frontier(), _Issues())

    @staticmethod
    def boot(runtime, agent_id, task, **kwargs):
        kwargs.setdefault("coordination_mode", "AUTO")
        return runtime.bootstrap(
            agent_id=agent_id,
            task=task,
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
            **kwargs,
        )

    def present(self, root: Path, agent_id: str, task: str, work_key=None, targets=None):
        result = MessageBoardRuntime(GitBackend(root)).present(
            agent_id=agent_id,
            task=task,
            work_key=work_key,
            targets=targets,
        )
        self.assertTrue(result.get("durable_return"), result)
        return result

    def test_exact_duplicate_hold_gets_c3_treatments_without_override(self):
        self.present(self.a, "worker-a", "build parser", work_key="WK:PARSER")
        runtime = self.runtime(self.b)
        packet = self.boot(runtime, "worker-b", "build parser", work_key="WK:PARSER")
        self.assertEqual(packet["coordination"]["status"], "DUPLICATE_WORK_HOLD", packet)
        self.assertEqual(packet["coordination"]["pre_dispatch"], "HOLD")
        self.assertEqual(packet["status"], "BOOTSTRAP_HOLD")
        projection = packet["coordination"]["treatment_projection"]
        self.assertEqual(projection["classification"], "EXACT_DUPLICATE_HOLD", projection)
        self.assertTrue(projection["hard_hold"])
        actions = {row["action"]: row for row in projection["treatments"]}
        self.assertTrue(actions["JOIN"]["eligible"])
        self.assertTrue(actions["PIVOT"]["eligible"])
        self.assertTrue(actions["REPLICA"]["eligible"])
        self.assertFalse(actions["PROCEED"]["eligible"])
        self.assertTrue(all(not row["execution_authority"] for row in actions.values()))
        self.assertFalse(projection["hold_override"])
        self.assertFalse(projection["claim_authority"])
        self.assertFalse(projection["execution_authority"])
        self.assertEqual(projection["mata"]["semantic_relation"], "UNAVAILABLE_NOT_IN_RUNTIME")

    def test_self_active_incompatible_hold_gets_self_conflict_projection(self):
        runtime = self.runtime(self.b)
        first = self.boot(runtime, "worker-b", "build parser", work_key="WK:PARSER")
        self.assertEqual(first["coordination"]["pre_dispatch"], "ALLOW", first)
        packet = self.boot(runtime, "worker-b", "build renderer", work_key="WK:RENDERER")
        self.assertEqual(packet["coordination"]["status"], "AGENT_ALREADY_PRESENT_HOLD")
        projection = packet["coordination"]["treatment_projection"]
        self.assertEqual(projection["classification"], "SELF_ACTIVE_CLAIM_CONFLICT", projection)
        self.assertTrue(projection["hard_hold"])
        actions = {row["action"]: row for row in projection["treatments"]}
        self.assertTrue(actions["PIVOT"]["eligible"])
        self.assertFalse(actions["JOIN"]["eligible"])

    def test_projection_stage_does_not_write_candidate_presence_or_board_events(self):
        self.present(self.a, "worker-a", "build parser", work_key="WK:PARSER")
        runtime = self.runtime(self.b)
        # First held boot may fast-forward b to the board claim. That is read-side sync.
        first = self.boot(runtime, "worker-b", "build parser", work_key="WK:PARSER")
        self.assertEqual(first["coordination"]["pre_dispatch"], "HOLD")
        head = _run(self.b, "rev-parse", "HEAD")
        before = _board_digest(self.b)
        second = self.boot(runtime, "worker-b", "build parser", work_key="WK:PARSER")
        self.assertEqual(second["coordination"]["pre_dispatch"], "HOLD")
        self.assertEqual(_run(self.b, "rev-parse", "HEAD"), head)
        self.assertEqual(_board_digest(self.b), before)
        self.assertFalse((self.b / "runtime/message_board/v1/agents/worker-b.json").exists())
        self.assertFalse(second["coordination"]["treatment_projection"]["board_write_performed"])

    def test_allow_read_only_and_disabled_paths_have_no_projection(self):
        allowed = self.boot(self.runtime(self.a), "worker-a", "build parser", work_key="WK:PARSER")
        self.assertEqual(allowed["coordination"]["pre_dispatch"], "ALLOW", allowed)
        self.assertNotIn("treatment_projection", allowed["coordination"])

        observed = self.runtime(self.b).bootstrap(
            agent_id="observer-b",
            task="inspect parser",
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
            coordination_mode="READ_ONLY",
        )
        self.assertEqual(observed["coordination"]["pre_dispatch"], "ADVISORY_ONLY")
        self.assertNotIn("treatment_projection", observed["coordination"])

        disabled = self.runtime(self.c).bootstrap(
            agent_id="library-c",
            task="offline inspect",
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(disabled["coordination"]["pre_dispatch"], "DISABLED")
        self.assertNotIn("treatment_projection", disabled["coordination"])

    def test_generic_shared_frontier_hold_does_not_invent_treatment(self):
        _run(self.b, "remote", "set-url", "origin", str(self.b.parent / "missing.git"))
        packet = self.boot(self.runtime(self.b), "worker-b", "build parser", work_key="WK:PARSER")
        self.assertEqual(packet["coordination"]["pre_dispatch"], "HOLD", packet)
        self.assertNotIn(packet["coordination"]["status"], {"DUPLICATE_WORK_HOLD", "AGENT_ALREADY_PRESENT_HOLD"})
        self.assertNotIn("treatment_projection", packet["coordination"])

    def test_explicit_replica_remains_message_board_governed_and_unprojected(self):
        self.present(self.a, "worker-a", "benchmark kernel", work_key="WK:KERNEL")
        packet = self.boot(
            self.runtime(self.b),
            "worker-b",
            "benchmark kernel",
            work_key="WK:KERNEL",
            coordination_claim_mode="REPLICA",
            replication_reason="independent implementation attempt",
        )
        self.assertEqual(packet["coordination"]["pre_dispatch"], "ALLOW", packet)
        self.assertEqual(packet["coordination"]["presence"]["mode"], "REPLICA")
        self.assertNotIn("treatment_projection", packet["coordination"])

    def test_repeated_held_refresh_has_stable_treatment_digest_and_no_board_write(self):
        self.present(self.a, "worker-a", "build parser", work_key="WK:PARSER")
        runtime = self.runtime(self.b)
        first = self.boot(runtime, "worker-b", "build parser", work_key="WK:PARSER")
        digest = first["coordination"]["treatment_projection"]["decision_digest"]
        head = _run(self.b, "rev-parse", "HEAD")
        before = _board_digest(self.b)
        refreshed = runtime.refresh(
            session_id=first["session_id"],
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(refreshed["coordination"]["pre_dispatch"], "HOLD", refreshed)
        self.assertEqual(refreshed["coordination"]["treatment_projection"]["decision_digest"], digest)
        self.assertEqual(_run(self.b, "rev-parse", "HEAD"), head)
        self.assertEqual(_board_digest(self.b), before)
        self.assertFalse(refreshed["coordination"]["treatment_projection"]["board_write_performed"])

    def test_extension_registration_and_contract_are_present(self):
        self.assertTrue(getattr(AgentBootstrapRuntime, "_athena_boot_cohesion_treatment_v1_registered", False))
        spec_path = Path(__file__).resolve().parents[1] / "spec" / "AGENT_BOOT_COHESION_TREATMENT_V1.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        self.assertEqual(spec["artifact"], "ATHENA.AGENT.BOOT.COHESION.TREATMENT.V1")
        self.assertIn("DUPLICATE_WORK_HOLD", spec["activation"]["projectable_holds"])
        self.assertFalse(spec["authority"]["execution"])
        self.assertFalse(spec["authority"]["claim_mutation"])


if __name__ == "__main__":
    unittest.main()
