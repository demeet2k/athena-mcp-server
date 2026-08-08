from __future__ import annotations

import json
import os
import selectors
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sched_v3"
EXPECTED_BLOBS = {
    "orchestration/v3/reducer.py": "122802a3cec6f50b692d819b18024b50be39bab8",
    "orchestration/v3/ready.py": "975d61ab5ddf42e6e06c7304fc0fc330ca4b24d5",
    "orchestration/v3/claim.py": "4757f4eaf8180cf356dc0e940b9019177f1c0a8a",
}


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _clone(remote: Path, dest: Path) -> None:
    p = subprocess.run(["git", "clone", str(remote), str(dest)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(dest, "config", "user.name", "cold-process-test")
    _run(dest, "config", "user.email", "cold-process@example.invalid")


def _write_json(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_shared_brain(base: Path) -> Path:
    remote = base / "shared.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    seed = base / "seed"
    seed.mkdir()
    _run(seed, "init", "-b", "master")
    _run(seed, "config", "user.name", "cold-process-test")
    _run(seed, "config", "user.email", "cold-process@example.invalid")

    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "BUILD",
        "profiles": {"BUILD": ["core"], "MAXDEV": ["core"]},
        "modules": {
            "core": {
                "path": "prompts/ORCHESTRATION_CORE.md",
                "order": 0,
                "mandatory": True,
                "selectors": [],
                "depends_on": [],
            }
        },
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "BUILD",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write_json(seed, "prompts/PROMPT.manifest.json", manifest)
    _write_json(seed, "prompts/state/ACTIVE.json", active)
    (seed / "policies").mkdir(parents=True, exist_ok=True)
    (seed / "policies/PROMPT_RUNTIME.md").write_text("PROMPT RUNTIME POLICY\n", encoding="utf-8")
    (seed / "prompts/ORCHESTRATION_CORE.md").write_text("ORCHESTRATION CORE V1\n", encoding="utf-8")

    contract_dir = seed / "orchestration" / "v3"
    contract_dir.mkdir(parents=True, exist_ok=True)
    for name in ("reducer.py", "ready.py", "claim.py"):
        shutil.copyfile(FIXTURE / name, contract_dir / name)

    _run(seed, "add", ".")
    _run(seed, "commit", "-m", "seed shared cognitive brain")
    for rel, expected in EXPECTED_BLOBS.items():
        actual = _run(seed, "hash-object", rel)
        if actual != expected:
            raise AssertionError(f"fixture blob mismatch for {rel}: {actual} != {expected}")

    _run(seed, "branch", "athena-runtime-v3-candidate")
    _run(seed, "remote", "add", "origin", str(remote))
    _run(seed, "push", "-u", "origin", "master")
    _run(seed, "push", "origin", "athena-runtime-v3-candidate")
    subprocess.run(
        ["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/master"],
        check=True,
        capture_output=True,
    )
    return remote


class _IssueHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.startswith("/repos/demeet2k/Athena/issues"):
            body = b"[]"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("ETag", '"cold-process-issues-v1"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A003
        return


class _IssueServer:
    def __init__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _IssueHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def api_base(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class _MCP:
    def __init__(self, git_root: Path, db_path: Path, api_base: str):
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["ATHENA_GITHUB_API_URL"] = api_base
        env.pop("ATHENA_GITHUB_TOKEN", None)
        self.proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "athena_mcp",
                "--db",
                str(db_path),
                "--git-root",
                str(git_root),
            ],
            cwd=str(ROOT),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.next_id = 1
        self.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "cold-process-acceptance", "version": "1"},
            },
        )

    def _failure_detail(self) -> str:
        code = self.proc.poll()
        if code is None:
            return "process still running"
        try:
            _, err = self.proc.communicate(timeout=1)
        except Exception:
            err = ""
        return f"process exited {code}: {err[-4000:]}"

    def request(self, method: str, params: dict):
        request_id = self.next_id
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self.proc.stdin.write(json.dumps(payload, sort_keys=True) + "\n")
        self.proc.stdin.flush()
        deadline_reads = 0
        while deadline_reads < 20:
            ready = self.selector.select(timeout=2)
            if not ready:
                deadline_reads += 1
                if self.proc.poll() is not None:
                    raise AssertionError(self._failure_detail())
                continue
            line = self.proc.stdout.readline()
            if not line:
                raise AssertionError(self._failure_detail())
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise AssertionError(f"MCP {method} error: {message['error']}")
            return message.get("result")
        raise AssertionError(f"timeout waiting for MCP {method}; {self._failure_detail()}")

    def tool(self, name: str, arguments: dict):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if not isinstance(result, dict):
            raise AssertionError(f"unexpected tool result: {result!r}")
        content = result.get("content") or []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text") or ""
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"text": text}
        if "structuredContent" in result:
            return result["structuredContent"]
        return result

    def tool_names(self) -> set[str]:
        result = self.request("tools/list", {})
        return {str(item.get("name")) for item in (result or {}).get("tools") or []}

    def close(self):
        try:
            self.selector.close()
        except Exception:
            pass
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def _passes():
    return [
        {"kind": kind, "summary": f"{kind} pass", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _completion(summary: str, next_task: str, residual: str):
    return {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": False,
        "hard_hold": False,
        "summary": summary,
        "progress_delta": 1.0,
        "passes": _passes(),
        "tests": [{"name": "cold-process-test", "status": "PASS", "evidence_ref": "test://cold-process"}],
        "evidence_refs": ["test://cold-process"],
        "residuals": [residual],
        "next_task": next_task,
        "handoff_to": "cold-successor",
    }


class AgentBootstrapColdProcessContinuationTests(unittest.TestCase):
    def test_two_cold_mcp_sessions_reconstruct_and_refresh_shared_continuation(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        remote = _seed_shared_brain(base)

        with _IssueServer() as issue_server:
            # Preparation process creates exactly one durable transition, then exits.
            prep = base / "prep"
            _clone(remote, prep)
            with _MCP(prep, base / "prep.sqlite", issue_server.api_base) as mcp:
                names = mcp.tool_names()
                self.assertIn("athena_rehydration_start", names)
                self.assertIn("athena_rehydration_advance", names)
                self.assertIn("athena_prompt_publish", names)
                start = mcp.tool(
                    "athena_rehydration_start",
                    {
                        "goal": "prove cold-process continuation without chat-memory transport",
                        "task": "create first verified durable transition",
                        "expected_git_head": _run(prep, "rev-parse", "HEAD"),
                        "actor": "prep",
                        "profile": "BUILD",
                        "source_ref": "athena-runtime-v3-candidate",
                        "remote": "origin",
                        "fetch": True,
                        "use_frontier": True,
                        "shared_remote_mode": "DISABLED",
                        "max_steps": 8,
                        "depth_mode": "deep",
                    },
                )
                self.assertIn("loop_id", start, start)
                loop_id = start["loop_id"]
                (prep / "transition-1.txt").write_text("transition one\n", encoding="utf-8")
                _run(prep, "add", ".")
                _run(prep, "commit", "-m", "verified transition one")
                first = mcp.tool(
                    "athena_rehydration_advance",
                    {
                        "loop_id": loop_id,
                        "expected_checkpoint_head": start["checkpoint_head"],
                        "expected_state_digest": start["state_digest"],
                        "expected_prompt_digest": start["prompt_digest"],
                        "completion": _completion(
                            "verified transition one complete",
                            "create second verified durable transition",
                            "second transition remains",
                        ),
                        "actor": "prep",
                        "shared_remote_mode": "DISABLED",
                    },
                )
                first_checkpoint = first["checkpoint_head"]
                published = mcp.tool(
                    "athena_prompt_publish",
                    {"expected_git_head": first_checkpoint, "remote": "origin"},
                )
                self.assertTrue(published.get("shared_frontier_verified"), published)

            # Two independent clones/processes start only after transition one is shared.
            a = base / "cold-a"
            b = base / "cold-b"
            _clone(remote, a)
            _clone(remote, b)
            with _MCP(a, base / "a.sqlite", issue_server.api_base) as mcp_a, _MCP(
                b, base / "b.sqlite", issue_server.api_base
            ) as mcp_b:
                for names in (mcp_a.tool_names(), mcp_b.tool_names()):
                    self.assertIn("athena_agent_bootstrap", names)
                    self.assertIn("athena_agent_refresh", names)
                    self.assertIn("athena_rehydration_handoff_delta", names)

                boot_args = {
                    "task": "continue cold-process acceptance",
                    "profile": "BUILD",
                    "source_ref": "athena-runtime-v3-candidate",
                    "remote": "origin",
                    "fetch": True,
                    "issue_repo": "demeet2k/Athena",
                    "issue_limit": 5,
                    "shared_remote_mode": "REQUIRED",
                    "continuation_shared_remote_mode": "REQUIRED",
                }
                boot_a = mcp_a.tool("athena_agent_bootstrap", {"agent_id": "cold-a", **boot_args})
                boot_b = mcp_b.tool("athena_agent_bootstrap", {"agent_id": "cold-b", **boot_args})
                self.assertEqual(boot_a["status"], "BOOTSTRAPPED", boot_a)
                self.assertEqual(boot_b["status"], "BOOTSTRAPPED", boot_b)
                self.assertTrue(boot_a["shared_frontier_verified"])
                self.assertTrue(boot_b["shared_frontier_verified"])
                self.assertEqual(boot_a["address"], boot_b["address"])
                self.assertEqual(boot_a["continuation"]["selected_loop_id"], loop_id)
                self.assertEqual(boot_b["continuation"]["selected_loop_id"], loop_id)
                self.assertEqual(
                    boot_a["continuation"]["handoff_digest"],
                    boot_b["continuation"]["handoff_digest"],
                )
                first_handoff = boot_b["address"]["rehydration_continuation_digest"]

                # A publishes transition two using only its own cold reconstructed continuation state.
                handoff_body = boot_a["continuation"]["handoff"]["handoff"]
                successor = handoff_body["successor"]
                (a / "transition-2.txt").write_text("transition two\n", encoding="utf-8")
                _run(a, "add", ".")
                _run(a, "commit", "-m", "verified transition two")
                second = mcp_a.tool(
                    "athena_rehydration_advance",
                    {
                        "loop_id": loop_id,
                        "expected_checkpoint_head": successor["checkpoint_head"],
                        "expected_state_digest": successor["state_digest"],
                        "expected_prompt_digest": successor["prompt_digest"],
                        "completion": _completion(
                            "verified transition two complete",
                            "continue after observed sibling refresh",
                            "acceptance observation remains",
                        ),
                        "actor": "cold-a",
                        "shared_remote_mode": "DISABLED",
                    },
                )
                second_checkpoint = second["checkpoint_head"]
                published_second = mcp_a.tool(
                    "athena_prompt_publish",
                    {"expected_git_head": second_checkpoint, "remote": "origin"},
                )
                self.assertTrue(published_second.get("shared_frontier_verified"), published_second)

                # B receives no A packet. It refreshes only its own session against shared Git.
                refreshed_b = mcp_b.tool(
                    "athena_agent_refresh",
                    {
                        "session_id": boot_b["session_id"],
                        "shared_remote_mode": "REQUIRED",
                        "continuation_shared_remote_mode": "REQUIRED",
                    },
                )
                refresh = refreshed_b["refresh"]
                self.assertTrue(refresh["changed"]["rehydration_continuation_digest"], refresh)
                self.assertIn("rehydration_handoff", refresh["affected_dependency_cone"])
                self.assertNotEqual(
                    first_handoff,
                    refreshed_b["address"]["rehydration_continuation_digest"],
                )
                self.assertEqual(refreshed_b["address"]["git_head"], second_checkpoint)
                self.assertEqual(refreshed_b["continuation"]["selected_loop_id"], loop_id)

                refreshed_address = dict(refreshed_b["address"])
                refreshed_handoff = refreshed_b["continuation"]["handoff_digest"]

            # A third brand-new process independently reconstructs the exact refreshed address.
            c = base / "cold-c"
            _clone(remote, c)
            with _MCP(c, base / "c.sqlite", issue_server.api_base) as mcp_c:
                boot_c = mcp_c.tool(
                    "athena_agent_bootstrap",
                    {
                        "agent_id": "cold-c",
                        "task": "continue cold-process acceptance",
                        "profile": "BUILD",
                        "source_ref": "athena-runtime-v3-candidate",
                        "remote": "origin",
                        "fetch": True,
                        "issue_repo": "demeet2k/Athena",
                        "issue_limit": 5,
                        "shared_remote_mode": "REQUIRED",
                        "continuation_shared_remote_mode": "REQUIRED",
                    },
                )
                self.assertEqual(boot_c["status"], "BOOTSTRAPPED", boot_c)
                self.assertEqual(boot_c["address"], refreshed_address)
                self.assertEqual(boot_c["continuation"]["handoff_digest"], refreshed_handoff)
                self.assertEqual(boot_c["address"]["git_head"], second_checkpoint)


if __name__ == "__main__":
    unittest.main()