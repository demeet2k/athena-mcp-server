from __future__ import annotations

import os
import re
import subprocess
from typing import Any, Dict

from .git_backend import GitStaleHead
from .prompt_runtime_types import (
    PROMPT_RUNTIME_VERSION,
    PromptRuntimeError,
    canonical_json,
    nonempty as _nonempty,
)

_REMOTE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_REMOTE_TIMEOUT_SECONDS = 30


class PromptRuntimeRemoteMixin:
    """Explicit, fail-closed transport between one local prompt checkout and its remote.

    This mixin deliberately does not participate in hydrate/compile. Fetch,
    fast-forward, and push are separate tools because a read of repository policy
    must not silently mutate the checkout or publish local cognition.
    """

    @staticmethod
    def _remote_name(value: Any) -> str:
        remote = _nonempty(value or "origin", "remote")
        if not _REMOTE_NAME.fullmatch(remote):
            raise PromptRuntimeError(
                "remote must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
            )
        return remote

    def _remote_run(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_TERMINAL_PROMPT": "0",
                "GCM_INTERACTIVE": "Never",
            }
        )
        try:
            return subprocess.run(
                ["git", "-C", str(self._root()), *args],
                text=True,
                capture_output=True,
                env=env,
                timeout=_REMOTE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise PromptRuntimeError(
                canonical_json(
                    {
                        "status": "REMOTE_COMMAND_TIMEOUT",
                        "command": ["git", *args],
                        "timeout_seconds": _REMOTE_TIMEOUT_SECONDS,
                    }
                )
            ) from exc

    @staticmethod
    def _command_detail(process: subprocess.CompletedProcess[str]) -> str:
        return process.stderr.strip() or process.stdout.strip()

    def _named_branch(self) -> str:
        branch = self._branch()
        if not branch:
            raise PromptRuntimeError(
                "DETACHED_GIT_HEAD: shared prompt transport requires a named local branch"
            )
        return branch

    def _remote_exists(self, remote: str) -> bool:
        process = self._remote_run("remote", "get-url", remote)
        return process.returncode == 0 and bool(process.stdout.strip())

    def _remote_branch(self, remote: str, local_branch: str) -> str:
        configured_remote = self._remote_run(
            "config", "--get", f"branch.{local_branch}.remote"
        )
        configured_merge = self._remote_run(
            "config", "--get", f"branch.{local_branch}.merge"
        )
        if (
            configured_remote.returncode == 0
            and configured_remote.stdout.strip() == remote
            and configured_merge.returncode == 0
            and configured_merge.stdout.strip().startswith("refs/heads/")
        ):
            return configured_merge.stdout.strip()[len("refs/heads/") :]
        return local_branch

    def _is_ancestor(self, older: str, newer: str) -> bool:
        process = self._remote_run("merge-base", "--is-ancestor", older, newer)
        if process.returncode not in (0, 1):
            raise PromptRuntimeError(
                f"REMOTE_ANCESTRY_CHECK_FAILED: {self._command_detail(process)}"
            )
        return process.returncode == 0

    def _remote_state(self, remote: str, *, fetch: bool) -> Dict[str, Any]:
        branch = self._named_branch()
        local = self._head()
        if not self._remote_exists(remote):
            return {
                "version": PROMPT_RUNTIME_VERSION,
                "status": "REMOTE_UNAVAILABLE_HOLD",
                "remote": remote,
                "branch": branch,
                "remote_branch": None,
                "local_head": local,
                "remote_head": None,
                "remote_checked": False,
                "shared_frontier_verified": False,
                "dirty": bool(self._dirty_rows()),
            }

        remote_branch = self._remote_branch(remote, branch)
        fetch_error = None
        remote_checked = False
        if fetch:
            process = self._remote_run(
                "fetch", "--prune", "--no-tags", remote, remote_branch
            )
            if process.returncode:
                fetch_error = self._command_detail(process)
            else:
                remote_checked = True

        remote_ref = f"refs/remotes/{remote}/{remote_branch}"
        process = self._remote_run("rev-parse", "--verify", remote_ref)
        if process.returncode:
            return {
                "version": PROMPT_RUNTIME_VERSION,
                "status": (
                    "REMOTE_BRANCH_UNAVAILABLE_HOLD"
                    if fetch_error is None
                    else "REMOTE_SYNC_UNAVAILABLE_HOLD"
                ),
                "remote": remote,
                "branch": branch,
                "remote_branch": remote_branch,
                "remote_ref": remote_ref,
                "local_head": local,
                "remote_head": None,
                "remote_checked": remote_checked,
                "fetch_error": fetch_error,
                "shared_frontier_verified": False,
                "dirty": bool(self._dirty_rows()),
            }

        remote_head = process.stdout.strip()
        if local == remote_head:
            relation = "UP_TO_DATE"
        elif self._is_ancestor(local, remote_head):
            relation = "BEHIND_REMOTE"
        elif self._is_ancestor(remote_head, local):
            relation = "AHEAD_LOCAL"
        else:
            relation = "DIVERGED_HOLD"

        if fetch_error is not None:
            status = "REMOTE_SYNC_UNAVAILABLE_HOLD"
        else:
            status = relation
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": status,
            "relation": relation,
            "remote": remote,
            "branch": branch,
            "remote_branch": remote_branch,
            "remote_ref": remote_ref,
            "local_head": local,
            "remote_head": remote_head,
            "remote_checked": remote_checked,
            "fetch_error": fetch_error,
            "shared_frontier_verified": bool(
                remote_checked and fetch_error is None and relation == "UP_TO_DATE"
            ),
            "dirty": bool(self._dirty_rows()),
            "law": (
                "LOCAL_HEAD != SHARED_REMOTE_FRONTIER unless a fresh fetch succeeded and exact heads are equal"
            ),
        }

    def remote_status(
        self, *, remote: str = "origin", fetch: bool = False
    ) -> Dict[str, Any]:
        remote_name = self._remote_name(remote)
        if fetch:
            with self._write_lock():
                return self._remote_state(remote_name, fetch=True)
        return self._remote_state(remote_name, fetch=False)

    def remote_sync(
        self, *, expected_git_head: str, remote: str = "origin"
    ) -> Dict[str, Any]:
        remote_name = self._remote_name(remote)
        with self._write_lock():
            expected = self._cas(expected_git_head)
            self._require_clean()
            state = self._remote_state(remote_name, fetch=True)
            if not state.get("remote_checked"):
                return {
                    **state,
                    "status": "REMOTE_SYNC_UNAVAILABLE_HOLD",
                    "shared_frontier_verified": False,
                    "mutation_performed": False,
                }
            if self._head() != expected:
                raise GitStaleHead(
                    canonical_json(
                        {
                            "status": "STALE_GIT_HEAD_DURING_REMOTE_SYNC",
                            "expected": expected,
                            "current": self._head(),
                        }
                    )
                )
            relation = state.get("relation")
            if relation == "UP_TO_DATE":
                return {
                    **state,
                    "status": "ALREADY_SYNCHRONIZED",
                    "mutation_performed": False,
                }
            if relation != "BEHIND_REMOTE":
                return {
                    **state,
                    "status": f"SYNC_HOLD_{relation}",
                    "shared_frontier_verified": False,
                    "mutation_performed": False,
                    "law": (
                        "remote sync permits only a clean exact-head fast-forward; ahead/diverged states require an explicit integration lineage"
                    ),
                }

            process = self._remote_run("merge", "--ff-only", state["remote_ref"])
            if process.returncode:
                return {
                    **state,
                    "status": "FAST_FORWARD_FAILED_HOLD",
                    "error": self._command_detail(process),
                    "local_head_after": self._head(),
                    "shared_frontier_verified": False,
                    "mutation_performed": False,
                }
            after = self._head()
            verified = self._remote_state(remote_name, fetch=True)
            success = bool(
                verified.get("shared_frontier_verified")
                and verified.get("local_head") == after
            )
            return {
                **verified,
                "status": (
                    "FAST_FORWARDED_SHARED"
                    if success
                    else "FAST_FORWARD_VERIFY_HOLD"
                ),
                "local_head_before": expected,
                "local_head_after": after,
                "mutation_performed": True,
                "shared_frontier_verified": success,
                "law": (
                    "shared cognition advances locally only by exact-head clean fast-forward plus post-operation fresh remote verification"
                ),
            }

    def remote_publish(
        self, *, expected_git_head: str, remote: str = "origin"
    ) -> Dict[str, Any]:
        remote_name = self._remote_name(remote)
        with self._write_lock():
            expected = self._cas(expected_git_head)
            self._require_clean()
            state = self._remote_state(remote_name, fetch=True)
            if not state.get("remote_checked"):
                return {
                    **state,
                    "status": "REMOTE_SYNC_UNAVAILABLE_HOLD",
                    "shared_frontier_verified": False,
                    "push_performed": False,
                }
            if self._head() != expected:
                raise GitStaleHead(
                    canonical_json(
                        {
                            "status": "STALE_GIT_HEAD_DURING_REMOTE_PUBLISH",
                            "expected": expected,
                            "current": self._head(),
                        }
                    )
                )
            relation = state.get("relation")
            if relation == "UP_TO_DATE":
                return {
                    **state,
                    "status": "ALREADY_SHARED",
                    "push_performed": False,
                }
            if relation != "AHEAD_LOCAL":
                return {
                    **state,
                    "status": f"PUBLISH_HOLD_{relation}",
                    "shared_frontier_verified": False,
                    "push_performed": False,
                    "law": (
                        "publication requires the freshly fetched remote branch to be an ancestor of exact clean local HEAD; no force push or automatic merge"
                    ),
                }

            refspec = f"HEAD:refs/heads/{state['remote_branch']}"
            process = self._remote_run("push", "--porcelain", remote_name, refspec)
            if process.returncode:
                return {
                    **state,
                    "status": "PUSH_FAILED_HOLD",
                    "error": self._command_detail(process),
                    "shared_frontier_verified": False,
                    "push_performed": False,
                }
            verified = self._remote_state(remote_name, fetch=True)
            success = bool(
                verified.get("shared_frontier_verified")
                and verified.get("local_head") == expected
                and verified.get("remote_head") == expected
            )
            return {
                **verified,
                "status": "PUBLISHED_SHARED" if success else "PUBLISH_VERIFY_HOLD",
                "published_head": expected,
                "push_performed": True,
                "shared_frontier_verified": success,
                "law": (
                    "durable cross-agent return requires explicit non-force publication and post-push fresh-fetch equality"
                ),
            }
