from __future__ import annotations

import subprocess

from .git_backend import GitBackend, GitStateError


def _run(root, *args: str):
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)


class PromptRemoteSync:
    """Synchronize a prompt-brain checkout with its shared Git remote.

    This surface never creates a merge commit, never rewrites local history, and
    never equates local persistence with shared delivery. Pull-side synchronization
    may only fast-forward a clean current branch after a successful fresh fetch.
    Publish may only perform an ordinary non-force push after a successful fresh
    fetch proves the remote branch is an ancestor of exact local HEAD.
    """

    def __init__(self, git: GitBackend):
        self.git = git

    def _require(self):
        if not self.git.enabled:
            raise GitStateError("Git brain disabled")
        branch = self.git._git("branch", "--show-current")
        if not branch:
            raise GitStateError("DETACHED_GIT_HEAD: shared prompt sync requires a named branch")
        return branch

    def _remote_exists(self, remote: str) -> bool:
        p = _run(self.git.root, "remote", "get-url", remote)
        return p.returncode == 0 and bool(p.stdout.strip())

    def _is_ancestor(self, older: str, newer: str) -> bool:
        p = _run(self.git.root, "merge-base", "--is-ancestor", older, newer)
        if p.returncode not in (0, 1):
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.returncode == 0

    def status(self, remote: str = "origin", fetch: bool = False):
        branch = self._require()
        if not self._remote_exists(remote):
            return {
                "status": "REMOTE_UNAVAILABLE",
                "branch": branch,
                "remote": remote,
                "local_head": self.git.head(),
                "remote_head": None,
                "remote_checked": False,
                "shared_frontier_verified": False,
            }
        fetch_error = None
        remote_checked = False
        if fetch:
            p = _run(self.git.root, "fetch", "--prune", remote)
            if p.returncode:
                fetch_error = p.stderr.strip() or p.stdout.strip()
            else:
                remote_checked = True
        remote_ref = f"refs/remotes/{remote}/{branch}"
        p = _run(self.git.root, "rev-parse", remote_ref)
        if p.returncode:
            return {
                "status": "REMOTE_BRANCH_UNAVAILABLE" if not fetch_error else "REMOTE_SYNC_UNAVAILABLE",
                "branch": branch,
                "remote": remote,
                "local_head": self.git.head(),
                "remote_head": None,
                "remote_checked": remote_checked,
                "fetch_error": fetch_error,
                "shared_frontier_verified": False,
            }
        local = self.git.head()
        remote_head = p.stdout.strip()
        if local == remote_head:
            relation = "UP_TO_DATE"
        elif self._is_ancestor(local, remote_head):
            relation = "BEHIND_REMOTE"
        elif self._is_ancestor(remote_head, local):
            relation = "AHEAD_LOCAL"
        else:
            relation = "DIVERGED_HOLD"
        return {
            "status": relation,
            "branch": branch,
            "remote": remote,
            "remote_ref": remote_ref,
            "local_head": local,
            "remote_head": remote_head,
            "remote_checked": remote_checked,
            "fetch_error": fetch_error,
            "dirty": bool(self.git._git("status", "--porcelain")),
            "shared_frontier_verified": bool(remote_checked and relation == "UP_TO_DATE"),
            "law": "LOCAL_HEAD != SHARED_REMOTE_FRONTIER unless remote_checked=true and status=UP_TO_DATE",
        }

    @staticmethod
    def _fetch_hold(state: dict):
        return {
            **state,
            "status": "REMOTE_SYNC_UNAVAILABLE_HOLD",
            "shared_frontier_verified": False,
            "law": "STALE_REMOTE_TRACKING_REF != FRESH_REMOTE_WITNESS; no shared mutation without successful fetch",
        }

    def sync(self, remote: str = "origin"):
        branch = self._require()
        if self.git._git("status", "--porcelain"):
            return {
                "status": "DIRTY_WORKTREE_HOLD",
                "branch": branch,
                "remote": remote,
                "local_head": self.git.head(),
                "shared_frontier_verified": False,
                "law": "remote synchronization never absorbs uncommitted working-tree state",
            }
        state = self.status(remote=remote, fetch=True)
        if not state.get("remote_checked"):
            return self._fetch_hold(state)
        if state["status"] == "BEHIND_REMOTE":
            before = state["local_head"]
            p = _run(self.git.root, "merge", "--ff-only", state["remote_ref"])
            if p.returncode:
                return {
                    **state,
                    "status": "FAST_FORWARD_FAILED_HOLD",
                    "local_head_before": before,
                    "local_head_after": self.git.head(),
                    "shared_frontier_verified": False,
                    "error": p.stderr.strip() or p.stdout.strip(),
                }
            after = self.git.head()
            verified = self.status(remote=remote, fetch=False)
            return {
                **verified,
                "status": "FAST_FORWARDED",
                "local_head_before": before,
                "local_head_after": after,
                "shared_frontier_verified": after == state["remote_head"],
                "law": "shared prompt cognition advanced only by a clean fast-forward after a fresh fetch",
            }
        if state["status"] == "DIVERGED_HOLD":
            return {
                **state,
                "shared_frontier_verified": False,
                "law": "DIVERGENCE != AUTO_MERGE; rebase/merge/fork requires explicit conflict handling",
            }
        if state["status"] == "AHEAD_LOCAL":
            return {
                **state,
                "shared_frontier_verified": False,
                "law": "AHEAD_LOCAL != SHARED; push/PR is a distinct delivery transition",
            }
        return state

    def publish(self, expected_git_head: str, remote: str = "origin"):
        branch = self._require()
        if self.git._git("status", "--porcelain"):
            return {
                "status": "DIRTY_WORKTREE_HOLD",
                "branch": branch,
                "remote": remote,
                "local_head": self.git.head(),
                "shared_frontier_verified": False,
            }
        local = self.git.head()
        if local != expected_git_head:
            return {
                "status": "STALE_LOCAL_HEAD_HOLD",
                "branch": branch,
                "remote": remote,
                "expected_git_head": expected_git_head,
                "local_head": local,
                "shared_frontier_verified": False,
            }
        state = self.status(remote=remote, fetch=True)
        if not state.get("remote_checked"):
            return self._fetch_hold(state)
        if state["status"] == "UP_TO_DATE":
            return {**state, "status": "ALREADY_SHARED", "shared_frontier_verified": True}
        if state["status"] != "AHEAD_LOCAL":
            return {
                **state,
                "status": "PUBLISH_HOLD_" + state["status"],
                "shared_frontier_verified": False,
                "law": "publish requires remote ancestry of exact local HEAD; behind/diverged states do not push",
            }
        p = _run(self.git.root, "push", remote, f"HEAD:refs/heads/{branch}")
        if p.returncode:
            return {
                **state,
                "status": "PUSH_FAILED_HOLD",
                "shared_frontier_verified": False,
                "error": p.stderr.strip() or p.stdout.strip(),
            }
        verified = self.status(remote=remote, fetch=True)
        return {
            **verified,
            "status": "PUBLISHED_SHARED" if verified.get("remote_checked") and verified["status"] == "UP_TO_DATE" else "PUBLISH_VERIFY_HOLD",
            "shared_frontier_verified": bool(verified.get("remote_checked") and verified["status"] == "UP_TO_DATE"),
            "published_head": local,
            "law": "durable cross-agent return requires post-push fresh remote verification",
        }

    def call_tool(self, name: str, args: dict):
        if name == "athena_prompt_remote_status":
            return self.status(args.get("remote", "origin"), bool(args.get("fetch", False)))
        if name == "athena_prompt_sync":
            return self.sync(args.get("remote", "origin"))
        if name == "athena_prompt_publish":
            return self.publish(args["expected_git_head"], args.get("remote", "origin"))
        raise KeyError(name)


PROMPT_REMOTE_TOOLS = [
    {
        "name": "athena_prompt_remote_status",
        "description": "Compare the local prompt-brain checkout with its configured remote branch; optionally fetch before comparison. Never mutates local history.",
        "inputSchema": {
            "type": "object",
            "properties": {"remote": {"type": "string"}, "fetch": {"type": "boolean"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_sync",
        "description": "Fresh-fetch the shared prompt-brain remote and fast-forward a clean current branch only when local HEAD is an ancestor. Failed fetch, ahead, diverged or dirty states hold.",
        "inputSchema": {
            "type": "object",
            "properties": {"remote": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_publish",
        "description": "Fresh-fetch then publish an exact clean local prompt-brain HEAD by ordinary non-force push only when the remote branch is its ancestor; post-push fresh-fetch verifies equality.",
        "inputSchema": {
            "type": "object",
            "required": ["expected_git_head"],
            "properties": {"expected_git_head": {"type": "string"}, "remote": {"type": "string"}},
            "additionalProperties": False,
        },
    },
]
PROMPT_REMOTE_TOOL_NAMES = {x["name"] for x in PROMPT_REMOTE_TOOLS}
