from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_remote import PromptRemoteSync, PROMPT_REMOTE_TOOL_NAMES


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _remote_fixture(base: Path):
    local = base / "local"
    local.mkdir()
    _run(local, "init")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    _write(local, "prompts/PROMPT.manifest.json", '{"artifact":"ATHENA.PROMPT.RUNTIME.V1"}\n')
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    p = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "HEAD:master")

    sibling = base / "sibling"
    p = subprocess.run(["git", "clone", str(origin), str(sibling)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(sibling, "config", "user.name", "sibling")
    _run(sibling, "config", "user.email", "sibling@example.invalid")
    return local, sibling


class PromptRemoteTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, sibling = _remote_fixture(Path(td.name))
        return PromptRemoteSync(GitBackend(local)), local, sibling

    def test_remote_status_and_fast_forward_make_sibling_delta_visible(self):
        remote, local, sibling = self._fixture()
        initial = remote.status(fetch=True)
        self.assertEqual(initial["status"], "UP_TO_DATE")
        self.assertTrue(initial["shared_frontier_verified"])

        _write(sibling, "prompts/sibling-learning.md", "learned delta\n")
        _run(sibling, "add", ".")
        _run(sibling, "commit", "-m", "sibling learning")
        _run(sibling, "push", "origin", "master")

        synced = remote.sync()
        self.assertEqual(synced["status"], "FAST_FORWARDED")
        self.assertTrue(synced["shared_frontier_verified"])
        self.assertEqual(_run(local, "rev-parse", "HEAD"), _run(sibling, "rev-parse", "HEAD"))
        self.assertEqual((local / "prompts" / "sibling-learning.md").read_text(), "learned delta\n")

    def test_ahead_local_is_not_mislabeled_shared(self):
        remote, local, _ = self._fixture()
        _write(local, "prompts/local-only.md", "local\n")
        _run(local, "add", ".")
        _run(local, "commit", "-m", "local only")
        state = remote.sync()
        self.assertEqual(state["status"], "AHEAD_LOCAL")
        self.assertFalse(state["shared_frontier_verified"])

    def test_divergence_fails_closed_without_auto_merge(self):
        remote, local, sibling = self._fixture()
        _write(local, "prompts/local.md", "local\n")
        _run(local, "add", ".")
        _run(local, "commit", "-m", "local branch")
        local_head = _run(local, "rev-parse", "HEAD")

        _write(sibling, "prompts/sibling.md", "sibling\n")
        _run(sibling, "add", ".")
        _run(sibling, "commit", "-m", "sibling branch")
        _run(sibling, "push", "origin", "master")

        state = remote.sync()
        self.assertEqual(state["status"], "DIVERGED_HOLD")
        self.assertFalse(state["shared_frontier_verified"])
        self.assertEqual(_run(local, "rev-parse", "HEAD"), local_head)

    def test_dirty_worktree_holds_before_fetch_or_merge(self):
        remote, local, _ = self._fixture()
        _write(local, "prompts/dirty.md", "dirty\n")
        state = remote.sync()
        self.assertEqual(state["status"], "DIRTY_WORKTREE_HOLD")
        self.assertFalse(state["shared_frontier_verified"])

    def test_remote_tool_surface_is_explicit(self):
        self.assertEqual(PROMPT_REMOTE_TOOL_NAMES, {"athena_prompt_remote_status", "athena_prompt_sync"})


if __name__ == "__main__":
    unittest.main()
