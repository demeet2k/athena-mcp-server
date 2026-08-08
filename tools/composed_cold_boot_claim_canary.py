from __future__ import annotations

import json
import os
import selectors
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "demeet2k/athena-mcp-server")
TARGET_BRANCH = os.environ["TARGET_BRANCH"]
TARGET_SEED_HEAD = os.environ["TARGET_SEED_HEAD"]
CANDIDATE_HEAD = os.environ["CANDIDATE_HEAD"]
RUN_ID = "run.composed-cold"
NODE_A = "build-a"
NODE_B = "build-b"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WITNESS_PATH = Path(os.environ.get("WITNESS_PATH", "composed-cold-boot-claim-witness.json"))
EXPECTED_CONTRACTS = {
    "orchestration/v3/reducer.py": "122802a3cec6f50b692d819b18024b50be39bab8",
    "orchestration/v3/ready.py": "975d61ab5ddf42e6e06c7304fc0fc330ca4b24d5",
    "orchestration/v3/claim.py": "4757f4eaf8180cf356dc0e940b9019177f1c0a8a",
    "orchestration/v3/journal.py": "d9a5674caef76b50a3ca6cb0e513389484ac640b",
    "orchestration/v3/claim_saga.py": "47a99a5b9461f613c7184650385b7d0804bc4553",
}


def run(cmd: list[str], *, cwd: Path | None = None) -> str:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-4000:])
    return p.stdout.strip()


def clone_target(base: Path, name: str) -> Path:
    dest = base / name
    run(["git", "clone", "--quiet", "--branch", TARGET_BRANCH, "--single-branch", f"https://github.com/{REPO}.git", str(dest)])
    run(["git", "config", "user.name", "athena-composed-cold-canary"], cwd=dest)
    run(["git", "config", "user.email", "athena-canary@example.invalid"], cwd=dest)
    return dest


class IssueHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.startswith("/repos/demeet2k/Athena/issues"):
            body = b"[]"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("ETag", '"composed-cold-issues-v1"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A003
        return


class IssueServer:
    def __init__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), IssueHandler)
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


class MCP:
    def __init__(self, git_root: Path, db_path: Path, issue_api_base: str):
        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"
        env["ATHENA_GITHUB_API_URL"] = issue_api_base
        env["GITHUB_TOKEN"] = TOKEN
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "athena_mcp", "--db", str(db_path), "--git-root", str(git_root)],
            cwd=str(Path(__file__).resolve().parents[1]),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.next_id = 1
        self.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "composed-cold-acceptance", "version": "1"},
            },
        )

    def request(self, method: str, params: dict):
        request_id = self.next_id
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self.proc.stdin.write(json.dumps(payload, sort_keys=True) + "\n")
        self.proc.stdin.flush()
        for _ in range(30):
            ready = self.selector.select(timeout=2)
            if not ready:
                if self.proc.poll() is not None:
                    raise RuntimeError(f"MCP exited {self.proc.returncode}")
                continue
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError(f"MCP stdout closed; exit={self.proc.poll()}")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(f"MCP {method} error: {message['error']}")
            return message.get("result")
        raise RuntimeError(f"timeout waiting for MCP {method}")

    def tool(self, name: str, arguments: dict) -> dict:
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if not isinstance(result, dict):
            raise RuntimeError(f"unexpected tool result for {name}")
        for item in result.get("content") or []:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text") or ""
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue
        structured = result.get("structuredContent")
        if isinstance(structured, dict):
            return structured
        return result

    def tool_names(self) -> set[str]:
        result = self.request("tools/list", {}) or {}
        return {str(x.get("name")) for x in result.get("tools") or []}

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


def safe_claims(packet: dict) -> list[dict]:
    out = []
    for claim in (packet.get("siblings") or {}).get("active_claims") or []:
        out.append({
            "run_id": claim.get("run_id"),
            "node_id": claim.get("node_id"),
            "worker_role": claim.get("worker_role"),
            "production_authority": claim.get("production_authority"),
        })
    return sorted(out, key=lambda x: (str(x.get("run_id")), str(x.get("node_id"))))


def boot_args(agent_id: str) -> dict:
    return {
        "agent_id": agent_id,
        "task": "prove composed cold bootstrap claim sibling refresh acceptance",
        "profile": "BUILD",
        "source_ref": TARGET_BRANCH,
        "remote": "origin",
        "fetch": True,
        "issue_repo": "demeet2k/Athena",
        "issue_limit": 5,
        "shared_remote_mode": "REQUIRED",
        "continuation_shared_remote_mode": "DISABLED",
    }


def assert_boot(packet: dict, agent: str) -> None:
    if packet.get("status") != "BOOTSTRAPPED":
        raise AssertionError(f"{agent} bootstrap status={packet.get('status')}")
    if packet.get("shared_frontier_verified") is not True:
        raise AssertionError(f"{agent} shared frontier not verified")
    surface = packet.get("execution_surface") or {}
    if surface.get("claim_tool_exposed") is not True or surface.get("standing") != "OBSERVED_TOOL_SURFACE":
        raise AssertionError(f"{agent} claim execution surface not observed")
    if (packet.get("frontier") or {}).get("status") != "HYDRATED":
        raise AssertionError(f"{agent} frontier not hydrated")


def provider_status(mcp: MCP, address: dict) -> dict:
    status = mcp.tool(
        "athena_frontier_provider_status",
        {"task": "composed cold acceptance", "profile": "BUILD", "source_ref": TARGET_BRANCH, "remote": "origin", "fetch": True},
    )
    if status.get("status") != "CLAIM_PROVIDER_READY" or status.get("write_ready") is not True:
        raise AssertionError(f"provider not ready: {status.get('status')}")
    if status.get("source_head") != address.get("frontier_source_head"):
        raise AssertionError("provider source_head does not match composite address")
    if status.get("frontier_digest") != address.get("frontier_digest"):
        raise AssertionError("provider frontier_digest does not match composite address")
    if status.get("prompt_stack_digest") != address.get("prompt_stack_digest"):
        raise AssertionError("provider prompt_stack_digest does not match composite address")
    contract = status.get("claim_contract") or {}
    if contract.get("status") != "PASS":
        raise AssertionError("five-blob claim contract is not PASS")
    rows = contract.get("contracts") or {}
    actual = {path: (row or {}).get("actual_blob") for path, row in rows.items()}
    if actual != EXPECTED_CONTRACTS:
        raise AssertionError(f"claim contract blob identity mismatch: {actual}")
    return status


def claim_args(address: dict, status: dict, node_id: str, operation_at: str) -> dict:
    return {
        "expected_source_head": address["frontier_source_head"],
        "expected_frontier_digest": address["frontier_digest"],
        "expected_prompt_stack_digest": address["prompt_stack_digest"],
        "expected_claim_contract_digest": status["claim_contract"]["claim_contract_digest"],
        "run_id": RUN_ID,
        "node_id": node_id,
        "worker_role": "builder",
        "lease_seconds": 900,
        "operation_at": operation_at,
        "task": "composed cold acceptance",
        "profile": "BUILD",
        "source_ref": TARGET_BRANCH,
        "remote": "origin",
    }


def assert_claimed(result: dict, node_id: str) -> dict:
    if result.get("status") != "CLAIM_JOURNALED":
        raise AssertionError(f"{node_id} claim status={result.get('status')}")
    observed = result.get("observed") or {}
    if observed.get("reducer_state") != "CLAIMED" or observed.get("claim_visible") is not True:
        raise AssertionError(f"{node_id} claim postcondition not observed")
    if observed.get("still_claimable") is not False:
        raise AssertionError(f"{node_id} remains claimable")
    claim_provider = result.get("claim_provider") or result.get("provider") or {}
    event_provider = result.get("event_provider") or {}
    if claim_provider.get("http_status") != 201:
        raise AssertionError(f"{node_id} claim provider was not HTTP 201")
    if event_provider.get("http_status") != 201:
        raise AssertionError(f"{node_id} event provider was not HTTP 201")
    return {
        "status": result.get("status"),
        "claim_path": result.get("claim_path") or claim_provider.get("path"),
        "claim_provider": {
            "http_status": claim_provider.get("http_status"),
            "standing": claim_provider.get("provider_effect_standing"),
            "newly_created": claim_provider.get("provider_effect_newly_created"),
        },
        "event_provider": {
            "http_status": event_provider.get("http_status"),
            "standing": event_provider.get("provider_effect_standing"),
            "newly_created": event_provider.get("provider_effect_newly_created"),
        },
        "observed": {
            "reducer_state": observed.get("reducer_state"),
            "claim_visible": observed.get("claim_visible"),
            "still_claimable": observed.get("still_claimable"),
        },
    }


def write_witness(payload: dict, *, passed: bool) -> None:
    payload = dict(payload)
    payload["schema_version"] = "ATHENA.PUBLIC.COMPOSED.COLD.BOOT.CLAIM.V1"
    payload["result"] = "PASS" if passed else "FAIL"
    payload["candidate_head"] = CANDIDATE_HEAD
    payload["target_branch"] = TARGET_BRANCH
    payload["target_seed_head"] = TARGET_SEED_HEAD
    payload["contract_blobs"] = EXPECTED_CONTRACTS
    payload["laws"] = [
        "PUBLIC_COMPOSED_COLD_ACCEPTANCE != PRIVATE_SCHEDULER_ACCEPTANCE",
        "BOOT_PACKET != EXECUTION_AUTHORITY",
        "NO_HUMAN_PACKET_TRANSPORT",
        "PROVIDER_CREDENTIAL != AUTHORITY_BYPASS",
        "CLAIM_DEPENDENCY_FEATURE != CANONICAL_MERGE",
    ]
    rendered = json.dumps(payload, sort_keys=True, indent=2)
    if TOKEN and TOKEN in rendered:
        raise RuntimeError("token leak detected in canary witness")
    WITNESS_PATH.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def main() -> None:
    if not TOKEN:
        write_witness({"reason": "GITHUB_TOKEN unavailable"}, passed=False)
        raise SystemExit(1)
    try:
        with tempfile.TemporaryDirectory() as td, IssueServer() as issue_server:
            base = Path(td)
            a = clone_target(base, "cold-a")
            b = clone_target(base, "cold-b")
            with MCP(a, base / "a.sqlite", issue_server.api_base) as mcp_a, MCP(b, base / "b.sqlite", issue_server.api_base) as mcp_b:
                required = {"athena_agent_bootstrap", "athena_agent_refresh", "athena_frontier_provider_status", "athena_frontier_claim"}
                for agent, names in (("cold-a", mcp_a.tool_names()), ("cold-b", mcp_b.tool_names())):
                    missing = sorted(required - names)
                    if missing:
                        raise AssertionError(f"{agent} missing tools: {missing}")

                boot_a = mcp_a.tool("athena_agent_bootstrap", boot_args("cold-a"))
                boot_b = mcp_b.tool("athena_agent_bootstrap", boot_args("cold-b"))
                assert_boot(boot_a, "cold-a")
                assert_boot(boot_b, "cold-b")
                if boot_a["address"] != boot_b["address"]:
                    raise AssertionError("independent cold boot addresses differ before any write")
                if boot_a["address"]["frontier_source_head"] != TARGET_SEED_HEAD:
                    raise AssertionError("target moved before initial cold bootstrap acceptance")
                if safe_claims(boot_a) or safe_claims(boot_b):
                    raise AssertionError("claims unexpectedly visible before first claim")

                status_a = provider_status(mcp_a, boot_a["address"])
                claim_a_raw = mcp_a.tool(
                    "athena_frontier_claim",
                    claim_args(boot_a["address"], status_a, NODE_A, "2026-08-08T22:05:00Z"),
                )
                claim_a = assert_claimed(claim_a_raw, NODE_A)

                # B receives no A packet. It refreshes only its own in-process boot session.
                refresh_b = mcp_b.tool(
                    "athena_agent_refresh",
                    {
                        "session_id": boot_b["session_id"],
                        "shared_remote_mode": "REQUIRED",
                        "continuation_shared_remote_mode": "DISABLED",
                    },
                )
                assert_boot(refresh_b, "cold-b-refresh")
                refresh_meta = refresh_b.get("refresh") or {}
                if "scheduler_frontier" not in (refresh_meta.get("affected_dependency_cone") or []):
                    raise AssertionError("B refresh did not observe scheduler frontier change")
                if not (refresh_meta.get("changed") or {}).get("frontier_source_head"):
                    raise AssertionError("B refresh did not observe source-head movement")
                claims_after_a = safe_claims(refresh_b)
                if not any(x.get("run_id") == RUN_ID and x.get("node_id") == NODE_A for x in claims_after_a):
                    raise AssertionError("B refresh did not observe A claim through sibling state")
                if any(x.get("production_authority") != "HOLD" for x in claims_after_a):
                    raise AssertionError("A claim widened production authority")

                status_b = provider_status(mcp_b, refresh_b["address"])
                claim_b_raw = mcp_b.tool(
                    "athena_frontier_claim",
                    claim_args(refresh_b["address"], status_b, NODE_B, "2026-08-08T22:05:01Z"),
                )
                claim_b = assert_claimed(claim_b_raw, NODE_B)
                refreshed_b_address = dict(refresh_b["address"])
                b_refresh_evidence = {
                    "arguments_transported": ["session_id", "shared_remote_mode", "continuation_shared_remote_mode"],
                    "changed_coordinates": refresh_meta.get("changed_coordinates") or [],
                    "affected_dependency_cone": refresh_meta.get("affected_dependency_cone") or [],
                    "observed_claims": claims_after_a,
                    "address": refreshed_b_address,
                }

            c = clone_target(base, "cold-c")
            with MCP(c, base / "c.sqlite", issue_server.api_base) as mcp_c:
                boot_c = mcp_c.tool("athena_agent_bootstrap", boot_args("cold-c"))
                assert_boot(boot_c, "cold-c")
                claims_c = safe_claims(boot_c)
                visible_nodes = {x.get("node_id") for x in claims_c if x.get("run_id") == RUN_ID}
                if visible_nodes != {NODE_A, NODE_B}:
                    raise AssertionError(f"cold-C did not reconstruct both claims: {visible_nodes}")
                if any(x.get("production_authority") != "HOLD" for x in claims_c):
                    raise AssertionError("cold-C observed widened production authority")
                status_c = provider_status(mcp_c, boot_c["address"])
                if status_c.get("claimable_work_count") != 0:
                    raise AssertionError("cold-C still sees claimable work after both claims")
                if boot_c["address"]["frontier_source_head"] == TARGET_SEED_HEAD:
                    raise AssertionError("cold-C failed to observe evolved provider branch")

            write_witness(
                {
                    "initial_address": boot_a["address"],
                    "boot": {
                        "cold_a_session": bool(boot_a.get("session_id")),
                        "cold_b_session": bool(boot_b.get("session_id")),
                        "same_initial_address": boot_a["address"] == boot_b["address"],
                        "claim_tool_exposed": True,
                        "shared_frontier_verified": True,
                    },
                    "claim_a": claim_a,
                    "cold_b_refresh": b_refresh_evidence,
                    "claim_b": claim_b,
                    "cold_c": {
                        "address": boot_c["address"],
                        "claims": claims_c,
                        "provider_claimable_work_count": status_c.get("claimable_work_count"),
                        "shared_frontier_verified": boot_c.get("shared_frontier_verified"),
                    },
                    "no_human_packet_transport": True,
                    "production_authority": "HOLD",
                },
                passed=True,
            )
    except Exception as exc:
        write_witness({"reason": f"{type(exc).__name__}: {exc}"}, passed=False)
        raise


if __name__ == "__main__":
    main()
