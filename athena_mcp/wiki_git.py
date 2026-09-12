"""Commit-bound access to the configured semantic Git Wiki compiler."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ARTIFACT = "ATHENA.MCP.GIT_WIKI.V1"
OPERATIONS = ("INIT", "INGEST", "QUERY", "REINDEX", "LINT")
MAX_REQUEST_BYTES = 1_000_000
MAX_RESPONSE_BYTES = 4_000_000
TIMEOUT_SECONDS = 180


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


class GitWikiCompiler:
    def __init__(self, git):
        self.git = git

    def compile(self, *, expected_git_head, request):
        if type(expected_git_head) is not str or not re.fullmatch(r"[0-9a-f]{40}", expected_git_head):
            raise ValueError("GIT_WIKI_EXACT_COMMIT_REQUIRED")
        if type(request) is not dict or request.get("operation") not in OPERATIONS:
            raise ValueError("GIT_WIKI_OPERATION_UNSUPPORTED")
        raw = canonical(request)
        if len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("GIT_WIKI_REQUEST_TOO_LARGE")
        if not self.git.enabled:
            raise ValueError("GIT_WIKI_ROOT_NOT_CONFIGURED")
        root = self.git.root
        before = self.git.status()
        if before["head"] != expected_git_head:
            raise ValueError("GIT_WIKI_STALE_HEAD")
        if before["dirty"]:
            raise ValueError("GIT_WIKI_WORKTREE_NOT_CLEAN")
        worker = Path(__file__).with_name("wiki_git_worker.py")
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-B", str(worker), str(root), expected_git_head],
                input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=root, timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError("GIT_WIKI_EXECUTION_TIMEOUT") from exc
        after = self.git.status()
        if after["head"] != expected_git_head or after["dirty"]:
            raise ValueError("GIT_WIKI_STATE_CHANGED_DURING_EXECUTION")
        if process.returncode:
            raise ValueError("GIT_WIKI_WORKER_FAILED:" + process.stderr.decode("utf-8", errors="replace")[-1500:])
        if len(process.stdout) > MAX_RESPONSE_BYTES:
            raise ValueError("GIT_WIKI_RESPONSE_TOO_LARGE")
        try:
            result = json.loads(process.stdout)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("GIT_WIKI_INVALID_WORKER_RESPONSE") from exc
        expected_digest = hashlib.sha256(raw).hexdigest()
        if (type(result) is not dict or result.get("artifact") != ARTIFACT
                or result.get("git_head") != expected_git_head
                or result.get("request_sha256") != expected_digest
                or result.get("operation") != request["operation"]
                or result.get("mutation_applied") is not False):
            raise ValueError("GIT_WIKI_RESPONSE_BINDING_MISMATCH")
        return result
