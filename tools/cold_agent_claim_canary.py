from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "demeet2k/athena-mcp-server")
TARGET_BRANCH = os.environ["TARGET_BRANCH"]
CANDIDATE_HEAD = os.environ["CANDIDATE_HEAD"]
TARGET_SEED_HEAD = os.environ["TARGET_SEED_HEAD"]
RUN_ID = os.environ.get("TARGET_RUN_ID", "run.cold-canary")
NODE_ID = os.environ.get("TARGET_NODE_ID", "build")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WITNESS_PATH = Path(os.environ.get("WITNESS_PATH", "cold-agent-claim-canary-witness.json"))
EXPECTED_CONTRACTS = {
    "orchestration/v3/reducer.py": "122802a3cec6f50b692d819b18024b50be39bab8",
    "orchestration/v3/ready.py": "975d61ab5ddf42e6e06c7304fc0fc330ca4b24d5",
    "orchestration/v3/claim.py": "4757f4eaf8180cf356dc0e940b9019177f1c0a8a",
    "orchestration/v3/journal.py": "d9a5674caef76b50a3ca6cb0e513389484ac640b",
    "orchestration/v3/claim_saga.py": "47a99a5b9461f613c7184650385b7d0804bc4553",
}

CHILD = r"""
import json
import os
import sys
import time
from pathlib import Path
from urllib import request as urlrequest

import athena_mcp.bootstrap  # noqa: F401 - installs production claim/provider membranes
from athena_mcp.frontier_claim import CLAIM_CONTRACT_BLOBS, FrontierClaimRuntime
from athena_mcp.frontier_runtime import FrontierRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime

root = Path(os.environ["ATHENA_TEST_BRAIN"])
target_branch = os.environ["TARGET_BRANCH"]
marker = Path(os.environ["READY_MARKER"])
barrier = Path(os.environ["RACE_BARRIER"])
run_id = os.environ["TARGET_RUN_ID"]
node_id = os.environ["TARGET_NODE_ID"]
operation_at = os.environ["OPERATION_AT"]
provider_marker = Path(os.environ["PROVIDER_READY_MARKER"])
provider_barrier = Path(os.environ["PROVIDER_RACE_BARRIER"])

_real_urlopen = urlrequest.urlopen

def _barrier_opener(req, timeout=20):
    method = str(getattr(req, "method", "") or "")
    url = str(getattr(req, "full_url", "") or "")
    if method == "PUT" and "/claims/" in url:
        provider_marker.write_text(
            json.dumps({"ready": True, "operation_at": operation_at}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        deadline = time.time() + 30
        while not provider_barrier.exists() and time.time() < deadline:
            time.sleep(0.01)
        if not provider_barrier.exists():
            raise TimeoutError("provider race barrier timeout")
    return _real_urlopen(req, timeout=timeout)

FrontierClaimRuntime._athena_claim_provider_opener = staticmethod(_barrier_opener)

git = GitBackend(root)
runtime = FrontierRuntime(git, PromptRuntime(git))

status = runtime.call_tool(
    "athena_frontier_provider_status",
    {"source_ref": target_branch, "remote": "origin", "fetch": True},
)
packet = runtime.hydrate(source_ref=target_branch, remote="origin", fetch=True)

claimable = [
    {
        "run_id": str(row.get("run_id")),
        "node_id": str(row.get("node_id")),
        "reducer_state": row.get("reducer_state"),
        "production_authority": row.get("production_authority"),
        "claim_path": row.get("claim_path"),
    }
    for row in (packet.get("claimable_work") or [])
]
contract_rows = (status.get("claim_contract") or {}).get("contracts") or {}
contract_map = {
    path: {
        "expected": row.get("expected_blob"),
        "actual": row.get("actual_blob"),
        "match": bool(row.get("match")),
    }
    for path, row in sorted(contract_rows.items())
}
address = {
    "source_head": packet.get("source_head"),
    "frontier_digest": packet.get("frontier_digest"),
    "prompt_stack_digest": packet.get("prompt_stack_digest"),
    "claim_contract_digest": (status.get("claim_contract") or {}).get("claim_contract_digest"),
}
same_address = (
    status.get("source_head") == address["source_head"]
    and status.get("frontier_digest") == address["frontier_digest"]
    and status.get("prompt_stack_digest") == address["prompt_stack_digest"]
)
expected_contracts = json.loads(os.environ["EXPECTED_CONTRACTS"])
contract_exact = (
    set(contract_map) == set(expected_contracts)
    and all(
        contract_map[path]["actual"] == expected_contracts[path]
        and contract_map[path]["expected"] == expected_contracts[path]
        and contract_map[path]["match"]
        for path in expected_contracts
    )
)
claimable_exact = claimable == [{
    "run_id": run_id,
    "node_id": node_id,
    "reducer_state": "READY",
    "production_authority": "HOLD",
    "claim_path": f"runtime/runs/{run_id}/claims/{node_id}.json",
}]
preflight_ok = bool(
    status.get("status") == "CLAIM_PROVIDER_READY"
    and status.get("write_ready") is True
    and (status.get("claim_contract") or {}).get("status") == "PASS"
    and same_address
    and contract_exact
    and claimable_exact
    and not any(
        str(row.get("run_id")) == run_id and str(row.get("node_id")) == node_id
        for row in (packet.get("routing_ready_work") or [])
    )
)

marker_payload = {
    "ok": preflight_ok,
    "provider_status": status.get("status"),
    "write_ready": status.get("write_ready"),
    "address": address,
    "contract_map": contract_map,
    "claimable": claimable,
}
marker.write_text(json.dumps(marker_payload, sort_keys=True) + "\n", encoding="utf-8")
if not preflight_ok:
    print(json.dumps({"phase": "preflight", **marker_payload}, sort_keys=True))
    raise SystemExit(2)

deadline = time.time() + 30
while not barrier.exists() and time.time() < deadline:
    time.sleep(0.01)
if not barrier.exists():
    print(json.dumps({"phase": "barrier", "status": "BARRIER_TIMEOUT"}, sort_keys=True))
    raise SystemExit(3)

args = {
    "expected_source_head": address["source_head"],
    "expected_frontier_digest": address["frontier_digest"],
    "expected_prompt_stack_digest": address["prompt_stack_digest"],
    "expected_claim_contract_digest": address["claim_contract_digest"],
    "run_id": run_id,
    "node_id": node_id,
    "worker_role": "builder",
    "lease_seconds": 900,
    "operation_at": operation_at,
    "source_ref": target_branch,
    "remote": "origin",
}
result = runtime.call_tool("athena_frontier_claim", args)

claim_provider = result.get("claim_provider") or result.get("provider") or {}
event_provider = result.get("event_provider") or {}
sanitized = {
    "phase": "claim",
    "status": result.get("status"),
    "run_id": result.get("run_id") or run_id,
    "node_id": result.get("node_id") or node_id,
    "claim_path": result.get("claim_path") or claim_provider.get("path"),
    "claim_provider": {
        "status": claim_provider.get("status"),
        "http_status": claim_provider.get("http_status"),
        "standing": claim_provider.get("provider_effect_standing"),
        "newly_created": claim_provider.get("provider_effect_newly_created"),
    },
    "event_provider": {
        "status": event_provider.get("status"),
        "http_status": event_provider.get("http_status"),
        "standing": event_provider.get("provider_effect_standing"),
        "newly_created": event_provider.get("provider_effect_newly_created"),
    },
    "observed": result.get("observed"),
}
print(json.dumps(sanitized, sort_keys=True))
"""


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr or p.stdout or f"command failed: {cmd}")
    return p


def clone_agent(base: Path, name: str) -> Path:
    target = base / name
    url = f"https://github.com/{REPO}.git"
    run(["git", "clone", "--quiet", "--branch", TARGET_BRANCH, "--single-branch", url, str(target)])
    return target


def child_env(brain: Path, marker: Path, barrier: Path, provider_marker: Path, provider_barrier: Path, operation_at: str) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "ATHENA_TEST_BRAIN": str(brain),
        "ATHENA_GITHUB_TOKEN": TOKEN,
        "TARGET_BRANCH": TARGET_BRANCH,
        "TARGET_RUN_ID": RUN_ID,
        "TARGET_NODE_ID": NODE_ID,
        "READY_MARKER": str(marker),
        "RACE_BARRIER": str(barrier),
        "PROVIDER_READY_MARKER": str(provider_marker),
        "PROVIDER_RACE_BARRIER": str(provider_barrier),
        "OPERATION_AT": operation_at,
        "EXPECTED_CONTRACTS": json.dumps(EXPECTED_CONTRACTS, sort_keys=True),
    })
    return env


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_result(actor: str, payload: dict, returncode: int) -> dict:
    return {
        "actor": actor,
        "returncode": returncode,
        "status": payload.get("status"),
        "claim_path": payload.get("claim_path"),
        "claim_provider": payload.get("claim_provider") or {},
        "event_provider": payload.get("event_provider") or {},
        "observed": payload.get("observed"),
    }


def scrub(value):
    if isinstance(value, str):
        return value.replace(TOKEN, "<REDACTED>") if TOKEN else value
    if isinstance(value, dict):
        return {str(k): scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def fail_witness(reason: str, extra: dict | None = None) -> None:
    witness = {
        "schema_version": "ATHENA.PUBLIC.COLD_AGENT.CLAIM_CANARY.V1",
        "result": "FAIL",
        "reason": reason,
        "candidate_head": CANDIDATE_HEAD,
        "target_branch": TARGET_BRANCH,
        "laws": [
            "PUBLIC_COLD_AGENT_PROVIDER != PRIVATE_SCHEDULER_ACCEPTANCE",
            "PROVIDER_CREDENTIAL != AUTHORITY_BYPASS",
            "CREATE_IF_ABSENT != ATOMIC_MULTIWRITE_TRANSACTION",
        ],
    }
    if extra:
        witness["evidence"] = scrub(extra)
    rendered = json.dumps(witness, sort_keys=True, indent=2)
    if TOKEN and TOKEN in rendered:
        raise RuntimeError("token leak detected while rendering failure witness")
    WITNESS_PATH.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(1)


def main() -> None:
    if not TOKEN:
        fail_witness("GITHUB_TOKEN unavailable before canary")
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        agent_a = clone_agent(base, "agent-a")
        agent_b = clone_agent(base, "agent-b")
        barrier = base / "race-go"
        provider_barrier = base / "provider-race-go"
        marker_a = base / "agent-a.ready.json"
        marker_b = base / "agent-b.ready.json"
        provider_marker_a = base / "agent-a.provider-ready.json"
        provider_marker_b = base / "agent-b.provider-ready.json"

        procs = []
        for actor, brain, marker, provider_marker, operation_at in (
            ("agent-a", agent_a, marker_a, provider_marker_a, "2026-08-08T21:40:00Z"),
            ("agent-b", agent_b, marker_b, provider_marker_b, "2026-08-08T21:40:01Z"),
        ):
            p = subprocess.Popen(
                [sys.executable, "-c", CHILD],
                cwd=brain,
                env=child_env(brain, marker, barrier, provider_marker, provider_barrier, operation_at),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            procs.append((actor, p))

        deadline = time.time() + 30
        while time.time() < deadline:
            if marker_a.exists() and marker_b.exists():
                break
            if any(p.poll() is not None for _, p in procs):
                break
            time.sleep(0.05)

        markers = {}
        if marker_a.exists():
            markers["agent-a"] = read_json(marker_a)
        if marker_b.exists():
            markers["agent-b"] = read_json(marker_b)
        if set(markers) != {"agent-a", "agent-b"}:
            outputs = {}
            for actor, p in procs:
                if p.poll() is None:
                    p.terminate()
                out, err = p.communicate(timeout=10)
                outputs[actor] = scrub({"returncode": p.returncode, "stdout": out[-4000:], "stderr": err[-4000:]})
            fail_witness("both cold-agent preflight markers were not produced", {"markers": markers, "outputs": outputs})

        if not all(markers[a].get("ok") for a in markers):
            for _, p in procs:
                if p.poll() is None:
                    p.terminate()
                    p.communicate(timeout=10)
            fail_witness("cold-agent preflight failed closed", {"markers": markers})

        address_a = markers["agent-a"]["address"]
        address_b = markers["agent-b"]["address"]
        if address_a != address_b:
            for _, p in procs:
                if p.poll() is None:
                    p.terminate()
                    p.communicate(timeout=10)
            fail_witness("cold agents disagreed on initial freshness address", {"markers": markers})
        if address_a.get("source_head") != TARGET_SEED_HEAD:
            for _, p in procs:
                if p.poll() is None:
                    p.terminate()
                    p.communicate(timeout=10)
            fail_witness("target branch moved before race release", {"initial_address": address_a})

        barrier.write_text("go\n", encoding="utf-8")

        provider_deadline = time.time() + 30
        while time.time() < provider_deadline:
            if provider_marker_a.exists() and provider_marker_b.exists():
                break
            if any(p.poll() is not None for _, p in procs):
                break
            time.sleep(0.05)
        if not (provider_marker_a.exists() and provider_marker_b.exists()):
            outputs = {}
            for actor, p in procs:
                if p.poll() is None:
                    p.terminate()
                out, err = p.communicate(timeout=10)
                outputs[actor] = scrub({"returncode": p.returncode, "stdout": out[-4000:], "stderr": err[-4000:]})
            fail_witness(
                "both cold agents did not reach the fixed-claim provider PUT before mutation",
                {"markers": markers, "outputs": outputs},
            )

        provider_barrier.write_text("go\n", encoding="utf-8")

        results = {}
        raw_outputs = {}
        for actor, p in procs:
            out, err = p.communicate(timeout=60)
            raw_outputs[actor] = scrub({"returncode": p.returncode, "stdout": out[-4000:], "stderr": err[-4000:]})
            lines = [line for line in out.splitlines() if line.strip()]
            try:
                results[actor] = json.loads(lines[-1]) if lines else {}
            except json.JSONDecodeError:
                results[actor] = {}

        winner_rows = [
            (actor, payload)
            for actor, payload in results.items()
            if payload.get("status") == "CLAIM_JOURNALED"
        ]
        loser_rows = [
            (actor, payload)
            for actor, payload in results.items()
            if payload.get("status") == "CLAIM_LOST_RACE"
        ]
        if len(winner_rows) != 1 or len(loser_rows) != 1:
            fail_witness(
                "expected exactly one CLAIM_JOURNALED winner and one CLAIM_LOST_RACE loser",
                {"markers": markers, "results": results, "raw_outputs": raw_outputs},
            )

        winner_actor, winner = winner_rows[0]
        loser_actor, loser = loser_rows[0]
        winner_claim = winner.get("claim_provider") or {}
        loser_claim = loser.get("claim_provider") or {}
        if winner_claim.get("standing") != "CREATED_NEW" or winner_claim.get("newly_created") is not True:
            fail_witness("winner did not prove a newly-created fixed claim effect", {"results": results})
        if loser_claim.get("status") != "EXISTS" or loser_claim.get("standing") not in {
            "CREATE_COLLISION",
            "CREATE_COLLISION_UNREADABLE",
        }:
            fail_witness("loser did not prove fixed-path provider exclusion", {"results": results})

        observer = clone_agent(base, "observer")
        observer_code = r"""
import json
import os
from pathlib import Path
import athena_mcp.bootstrap  # noqa: F401
from athena_mcp.frontier_runtime import FrontierRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime

root = Path(os.environ["ATHENA_TEST_BRAIN"])
git = GitBackend(root)
runtime = FrontierRuntime(git, PromptRuntime(git))
packet = runtime.hydrate(source_ref=os.environ["TARGET_BRANCH"], remote="origin", fetch=True)
run_id = os.environ["TARGET_RUN_ID"]
node_id = os.environ["TARGET_NODE_ID"]
entry = next(row for row in packet.get("runs") or [] if str(row.get("run_id")) == run_id)
state = ((entry.get("projection") or {}).get("node_states") or {}).get(node_id)
out = {
    "status": packet.get("status"),
    "source_head": packet.get("source_head"),
    "frontier_digest": packet.get("frontier_digest"),
    "prompt_stack_digest": packet.get("prompt_stack_digest"),
    "sched_contract_status": (packet.get("sched_contract") or {}).get("status"),
    "node_state": state,
    "claim_visible": any(
        str(row.get("run_id")) == run_id and str(row.get("node_id")) == node_id
        for row in packet.get("claims") or []
    ),
    "still_claimable": any(
        str(row.get("run_id")) == run_id and str(row.get("node_id")) == node_id
        for row in packet.get("claimable_work") or []
    ),
    "still_routing_ready": any(
        str(row.get("run_id")) == run_id and str(row.get("node_id")) == node_id
        for row in packet.get("routing_ready_work") or []
    ),
    "production_authority": entry.get("production_authority"),
}
print(json.dumps(out, sort_keys=True))
"""
        observer_env = dict(os.environ)
        observer_env.update({
            "ATHENA_TEST_BRAIN": str(observer),
            "TARGET_BRANCH": TARGET_BRANCH,
            "TARGET_RUN_ID": RUN_ID,
            "TARGET_NODE_ID": NODE_ID,
        })
        obs_proc = subprocess.run(
            [sys.executable, "-c", observer_code],
            cwd=observer,
            env=observer_env,
            text=True,
            capture_output=True,
        )
        try:
            observer_payload = json.loads([line for line in obs_proc.stdout.splitlines() if line.strip()][-1])
        except Exception:
            fail_witness("observer output was not valid JSON", {"stdout": obs_proc.stdout[-4000:], "stderr": obs_proc.stderr[-4000:]})

        observer_ok = bool(
            obs_proc.returncode == 0
            and observer_payload.get("status") == "HYDRATED"
            and observer_payload.get("sched_contract_status") == "PASS"
            and observer_payload.get("node_state") == "CLAIMED"
            and observer_payload.get("claim_visible") is True
            and observer_payload.get("still_claimable") is False
            and observer_payload.get("still_routing_ready") is False
            and observer_payload.get("production_authority") == "HOLD"
            and observer_payload.get("source_head") != address_a.get("source_head")
        )
        if not observer_ok:
            fail_witness("fresh observer did not reconstruct the claimed postcondition", {"observer": observer_payload, "results": results})

        witness = {
            "schema_version": "ATHENA.PUBLIC.COLD_AGENT.CLAIM_CANARY.V1",
            "result": "PASS",
            "candidate_head": CANDIDATE_HEAD,
            "target_branch": TARGET_BRANCH,
            "target_seed_head": TARGET_SEED_HEAD,
            "initial_address": address_a,
            "contract_blobs": EXPECTED_CONTRACTS,
            "agents": [
                compact_result("agent-a", results["agent-a"], raw_outputs["agent-a"]["returncode"]),
                compact_result("agent-b", results["agent-b"], raw_outputs["agent-b"]["returncode"]),
            ],
            "winner": winner_actor,
            "loser": loser_actor,
            "winner_count": len(winner_rows),
            "loser_count": len(loser_rows),
            "observer": observer_payload,
            "laws": [
                "PUBLIC_COLD_AGENT_PROVIDER != PRIVATE_SCHEDULER_ACCEPTANCE",
                "PROVIDER_CREDENTIAL != AUTHORITY_BYPASS",
                "CREATE_IF_ABSENT != ATOMIC_MULTIWRITE_TRANSACTION",
                "EXACTLY_ONE_CLAIM_WINNER",
                "CLAIM_CREATED + EVENT_FAILED => CLAIM_EFFECT_UNJOURNALED_HOLD",
            ],
        }
        rendered = json.dumps(witness, sort_keys=True, indent=2)
        if TOKEN in rendered:
            raise RuntimeError("token leak detected while rendering witness")
        WITNESS_PATH.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)


if __name__ == "__main__":
    main()
