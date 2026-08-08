from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from athena_mcp.frontier_claim import FrontierClaimRuntime, _provider_packet
from athena_mcp.frontier_claim_provider import GitHubContentsCreateProvider
from athena_mcp.frontier_claim_provider_guard import install_frontier_claim_provider_guard
from athena_mcp.frontier_claim_provider_readback import install_frontier_claim_provider_readback


class RuntimeEnvelope:
    def __init__(self):
        self.environ = dict(os.environ)


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    target_branch = os.environ["TARGET_BRANCH"]
    run_id = os.environ["TARGET_RUN_ID"]
    token = os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        raise SystemExit("GITHUB_TOKEN missing")

    install_frontier_claim_provider_guard(FrontierClaimRuntime)
    install_frontier_claim_provider_readback(FrontierClaimRuntime)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    claimed_at = now.isoformat().replace("+00:00", "Z")
    lease_expires_at = (now + timedelta(minutes=10)).isoformat().replace("+00:00", "Z")
    input_digest = hashlib.sha256(f"{repo}:{target_branch}:{run_id}".encode()).hexdigest()
    path = f"runtime/runs/{run_id}/claims/contend.json"

    def packet(worker: str):
        content = {
            "schema_version": "CLAIM_V1",
            "run_id": run_id,
            "node_id": "contend",
            "worker_role": worker,
            "attempt": 1,
            "policy_commit": os.environ["GITHUB_SHA"],
            "claimed_at": claimed_at,
            "lease_expires_at": lease_expires_at,
            "input_snapshot_digest": input_digest,
            "production_authority": "HOLD",
        }
        return _provider_packet(path, content, kind="CLAIM_V1")

    provider = GitHubContentsCreateProvider(RuntimeEnvelope())
    first = provider.create(repo=repo, branch=target_branch, packet=packet("canary-a"))
    second = provider.create(repo=repo, branch=target_branch, packet=packet("canary-a"))
    third = provider.create(repo=repo, branch=target_branch, packet=packet("canary-b"))

    assert first.get("status") == "CREATED", first
    assert first.get("provider_effect_standing") == "CREATED_NEW", first
    assert first.get("provider_effect_newly_created") is True, first

    assert second.get("status") == "CREATED", second
    assert second.get("provider_effect_standing") == "CREATE_EFFECT_OBSERVED", second
    assert second.get("provider_effect_newly_created") is False, second

    assert third.get("status") == "EXISTS", third
    assert third.get("provider_effect_standing") == "CREATE_COLLISION", third
    assert third.get("provider_effect_newly_created") is False, third

    witness = {
        "artifact": "ATHENA.FRONTIER.CLAIM.LIVE.PROVIDER.CANARY.V1",
        "repo": repo,
        "runner_branch": os.environ.get("GITHUB_REF_NAME"),
        "runner_sha": os.environ["GITHUB_SHA"],
        "target_branch": target_branch,
        "run_id": run_id,
        "fixed_claim_path": path,
        "production_authority": "HOLD",
        "results": {"first": first, "second": second, "third": third},
        "verdict": "PASS",
        "standing": "PUBLIC_LIVE_PROVIDER_MEMBRANE_CANARY_ONLY",
        "laws": [
            "LIVE_PUBLIC_PROVIDER_CANARY != PRIVATE_SCHEDULER_SAGA_ACCEPTANCE",
            "CREATE_EFFECT_OBSERVED != NEW_PROVIDER_CREATE",
            "CREATE_COLLISION != CLAIM_SUCCESS",
            "PROVIDER_CREDENTIAL != AUTHORITY_BYPASS",
        ],
    }
    rendered = json.dumps(witness, sort_keys=True, indent=2)
    if token in rendered:
        raise AssertionError("provider credential leaked into witness")
    Path("live-provider-canary-witness.json").write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
