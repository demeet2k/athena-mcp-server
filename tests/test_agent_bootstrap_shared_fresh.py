from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.agent_bootstrap import AgentBootstrapRuntime
from athena_mcp.git_backend import GitBackend


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _clone(remote: Path, dest: Path) -> None:
    p = subprocess.run(["git", "clone", str(remote), str(dest)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(dest, "config", "user.name", "test")
    _run(dest, "config", "user.email", "test@example.invalid")


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


class BootstrapSharedFreshTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        remote = base / "shared.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
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
        subprocess.run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/master"], check=True)
        a = base / "a"
        b = base / "b"
        _clone(remote, a)
        _clone(remote, b)
        return a, b

    @staticmethod
    def _runtime(root: Path):
        git = GitBackend(root)
        return AgentBootstrapRuntime(git, _Prompt(git), _Frontier(), _Issues())

    def test_required_boot_fast_forwards_before_address_is_computed(self):
        a, b = self._fixture()
        (a / "sibling.txt").write_text("shared change\n", encoding="utf-8")
        _run(a, "add", ".")
        _run(a, "commit", "-m", "sibling advance")
        new_head = _run(a, "rev-parse", "HEAD")
        _run(a, "push", "origin", "master")
        self.assertNotEqual(_run(b, "rev-parse", "HEAD"), new_head)

        runtime = self._runtime(b)
        packet = runtime.bootstrap(
            agent_id="cold-b",
            task="continue",
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(packet["status"], "BOOTSTRAPPED", packet)
        self.assertEqual(_run(b, "rev-parse", "HEAD"), new_head)
        self.assertEqual(packet["address"]["git_head"], new_head)
        self.assertTrue(packet["shared_frontier_verified"])
        self.assertTrue(packet["witnesses"]["shared_git"]["shared_frontier_verified"])
        self.assertEqual(packet["boot_freshness_law"], "BOOT_SYNC_SHARED_GIT_BEFORE_COMPOSITE_SNAPSHOT")

    def test_required_dirty_boot_holds_instead_of_claiming_freshness(self):
        _, b = self._fixture()
        (b / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        runtime = self._runtime(b)
        packet = runtime.bootstrap(
            agent_id="cold-b",
            task="continue",
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(packet["status"], "BOOTSTRAP_HOLD", packet)
        self.assertIn("BOOTSTRAP_SHARED_FRONTIER_HOLD", packet["holds"])
        self.assertFalse(packet["shared_frontier_verified"])
        self.assertEqual(packet["witnesses"]["shared_git"]["status"], "DIRTY_WORKTREE_HOLD")


if __name__ == "__main__":
    unittest.main()
