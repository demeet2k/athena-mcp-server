from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from athena_mcp.server import Server


EXPECTED_EXISTING = {
    "athena_cohesion_request_offer",
    "athena_cohesion_matchmake",
    "athena_cohesion_coalition",
    "athena_cohesion_solo_party_compare",
    "athena_cohesion_duplicate_guard",
}

EXPECTED_MISSING = {
    "athena_cohesion_consume",
    "athena_cohesion_dependency_cone",
    "athena_cohesion_outcome_credit",
    "athena_cohesion_pulse",
}


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        server = Server(db.name)
        try:
            listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            names = {tool["name"] for tool in listed["result"]["tools"]}
            resource_response = server.handle({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/read",
                "params": {"uri": "athena://cohesion/v1"},
            })
            resource = json.loads(resource_response["result"]["contents"][0]["text"])
        finally:
            server.store.close()

    existing_missing = sorted(EXPECTED_EXISTING - names)
    unexpectedly_present = sorted(EXPECTED_MISSING & names)
    missing = sorted(EXPECTED_MISSING - names)

    evidence_ok = (
        resource.get("evidence_guard_version") == "COHESION.EVIDENCE.GUARD.1"
        and resource.get("duplicate_guard_version") == "COHESION.DUPLICATE.GUARD.1"
        and any(
            "PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE" in law
            for law in resource.get("laws", [])
        )
    )

    status = "RED_CONFIRMED"
    errors = []
    if existing_missing:
        errors.append(f"expected existing Cohesion surfaces missing: {existing_missing}")
    if unexpectedly_present:
        errors.append(
            "CUT-02 contract is stale because treatment surfaces already exist: "
            f"{unexpectedly_present}"
        )
    if set(missing) != EXPECTED_MISSING:
        errors.append(f"unexpected missing-set mismatch: {missing}")
    if not evidence_ok:
        errors.append("EvidenceCoverage/duplicate-guard substrate is not composed as expected")
    if errors:
        status = "RED_CONTRACT_DRIFT"

    receipt = {
        "schema": "ATHENA.CLOSURE.CUT02.RED.WITNESS.1",
        "status": status,
        "git_head": git_head(),
        "expected_existing": sorted(EXPECTED_EXISTING),
        "expected_missing": sorted(EXPECTED_MISSING),
        "observed_missing": missing,
        "unexpectedly_present": unexpectedly_present,
        "evidence_guard_version": resource.get("evidence_guard_version"),
        "duplicate_guard_version": resource.get("duplicate_guard_version"),
        "treatment_code_present": bool(unexpectedly_present),
        "errors": errors,
        "boundary": (
            "This is a pre-treatment surface-gap witness. It does not establish that the future "
            "operators are beneficial, correct, causally effective, promoted, or authorized."
        ),
    }
    out = Path("closure-cut02-red-witness.json")
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if status == "RED_CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
