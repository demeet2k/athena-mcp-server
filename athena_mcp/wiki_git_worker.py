"""Fresh-process adapter for the fixed semantic Wiki harness.

Executed as a file with Python -I -B. This is interpreter isolation, not an OS
sandbox: the operator must trust the explicitly configured Git repository.
Source documents are JSON data; no request can choose a module or entrypoint.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(sys.argv[1]).resolve()
    expected_head = sys.argv[2]

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args]).decode("utf-8").strip()

    def require_clean():
        if git("rev-parse", "HEAD") != expected_head:
            raise ValueError("GIT_WIKI_STALE_HEAD")
        if git("status", "--porcelain", "--untracked-files=all"):
            raise ValueError("GIT_WIKI_WORKTREE_NOT_CLEAN")

    raw = sys.stdin.buffer.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("GIT_WIKI_REQUEST_TOO_LARGE")
    request = json.loads(raw)
    require_clean()
    tree = git("rev-parse", "HEAD^{tree}")
    sys.path.insert(0, str(root))
    from scripts.scarlet_jspace_gate0_v1 import compile_gate0
    from scripts.entrance_admission_contract_v1 import validate_repository
    from TOOLS.KC144.GID039_R04C03_HARNESS_ALL_UPGRADES_SELFPLAY_ORCHESTRATOR_V1.repository_executor_v1 import RepositorySkillExecutor

    gate0 = compile_gate0(root)
    admission = validate_repository(root)
    if gate0.get("status") != "READY" or admission.get("status") != "READY":
        raise ValueError("GIT_WIKI_STATIC_BOOT_NOT_READY")
    if admission.get("host_execution_observed") is not False or admission.get("execution_authority_granted") is not False:
        raise ValueError("GIT_WIKI_ADMISSION_SCOPE_MISMATCH")
    executor = RepositorySkillExecutor(root)
    require_clean()
    receipt = executor.execute({"wiki_request": request}, harness_id="ATHENA.HARNESS.INTERNAL.WIKI.V1")
    require_clean()
    result = {
        "artifact": "ATHENA.MCP.GIT_WIKI.V1",
        "git_head": expected_head, "git_tree": tree,
        "request_sha256": hashlib.sha256(raw).hexdigest(),
        "operation": request["operation"], "standing": receipt["standing"],
        "wiki_standing": receipt["outputs"][0]["result"].get("standing") if len(receipt.get("outputs", [])) == 1 else "NOT_EXECUTED",
        "gate0": gate0, "static_admission": admission,
        "execution_receipt": receipt,
        "mutation_applied": False, "active_room_worker_admitted": False,
        "behavioral_gain": "UNKNOWN",
        "source_scope": "CONFIGURED_GIT_REPOSITORY_AT_EXPECTED_COMMIT",
    }
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(encoded) > 4_000_000:
        raise ValueError("GIT_WIKI_RESPONSE_TOO_LARGE")
    sys.stdout.buffer.write(encoded + b"\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.buffer.write((type(exc).__name__ + ":" + str(exc)[:1400]).encode("utf-8", errors="replace"))
        raise SystemExit(1)
