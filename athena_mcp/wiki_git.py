"""Commit-bound access to the configured semantic Git Wiki compiler."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ARTIFACT = "ATHENA.MCP.GIT_WIKI.V1"
OPERATIONS = ("INIT", "INGEST", "QUERY", "REINDEX", "LINT")
MAX_REQUEST_BYTES = 1_000_000
MAX_RESPONSE_BYTES = 4_000_000
TIMEOUT_SECONDS = 180


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _run_bounded(command, *, input, cwd, timeout, max_output_bytes):
    """Run the fixed worker with a shared stdout/stderr byte budget.

    Drain both pipes concurrently so either stream can flood without deadlocking.
    Retained output never exceeds the budget; at most one 8 KiB read per pipe
    is in flight. Input writes also run off the supervising thread so a worker
    that never reads its request remains subject to the same deadline.
    """
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=cwd, bufsize=0)
    deadline = time.monotonic() + timeout
    outputs = [bytearray(), bytearray()]
    lock = threading.Lock()
    exceeded = threading.Event()
    failure = []
    total = 0

    def drain(pipe, index):
        nonlocal total
        try:
            while True:
                chunk = pipe.read(8192)
                if not chunk:
                    return
                with lock:
                    available = max_output_bytes - total
                    outputs[index].extend(chunk[:available])
                    total += min(len(chunk), available)
                    if len(chunk) > available:
                        exceeded.set()
                        return
        except (OSError, ValueError) as exc:
            failure.append(exc)

    def feed():
        try:
            view = memoryview(input)
            while view:
                written = process.stdin.write(view)
                if not written:
                    break
                view = view[written:]
        except BrokenPipeError:
            pass  # A normal worker failure is reported by its exit status.
        except (OSError, ValueError) as exc:
            failure.append(exc)
        finally:
            process.stdin.close()

    threads = [threading.Thread(target=drain, args=(process.stdout, 0), daemon=True),
               threading.Thread(target=drain, args=(process.stderr, 1), daemon=True),
               threading.Thread(target=feed, daemon=True)]
    for thread in threads:
        thread.start()
    try:
        while True:
            if exceeded.is_set():
                raise ValueError("GIT_WIKI_RESPONSE_TOO_LARGE")
            if process.poll() is not None and not any(t.is_alive() for t in threads):
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout)
            exceeded.wait(min(remaining, 0.01))
        if failure:
            raise ValueError("GIT_WIKI_WORKER_IO_FAILED") from failure[0]
        return subprocess.CompletedProcess(command, process.returncode,
                                           bytes(outputs[0]), bytes(outputs[1]))
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        # The direct worker is reaped before return, including on timeout/flood.
        for thread in threads:
            thread.join(timeout=0.1)
        for pipe in (process.stdin, process.stdout, process.stderr):
            pipe.close()


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
            process = _run_bounded(
                [sys.executable, "-I", "-B", str(worker), str(root), expected_git_head],
                input=raw, cwd=root, timeout=TIMEOUT_SECONDS,
                max_output_bytes=MAX_RESPONSE_BYTES,
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
