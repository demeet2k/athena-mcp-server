#!/usr/bin/env python3
"""Validate W26 control-ledger return/review-open bundles without side effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.control_ledger_ic10_review import (  # noqa: E402
    FrozenControlLedgerIC10Review,
    W26_CONTRACT,
)
from crystal_108d.independent_authority_return import (  # noqa: E402
    _addressed,
    _commit,
    _digest,
    _strict_loads,
)


MAX_BUNDLE_BYTES = 1572864
W25_FIELDS = (
    "challenge",
    "publication",
    "publication_observation",
    "policy_a",
    "policy_b",
    "execution_authorization",
    "execution",
    "execution_consumption",
    "promotion",
    "deployment",
    "health",
    "previous_safe_deployment",
    "rollback_authorization",
    "rollback_occurrence",
    "rollback_observation",
    "persistence_proof",
    "persistence_observation",
    "promotion_settlement",
    "settlement_observation",
)
W26_FIELDS = (
    "commit_authorization",
    "commit_occurrence",
    "ledger_observation",
    "review_request",
    "review_request_observation",
)
BUNDLE_FIELDS = W25_FIELDS + W26_FIELDS
CANONICAL_VERIFIER_REF = (
    "refs/heads/agent/w15-reconcile-capsule-deep-hardening"
)


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-snapshot", action="store_true")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--verifier-head")
    parser.add_argument("--verifier-tree")
    parser.add_argument("--verifier-ref")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w26-control-ledger-ic10-review-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenControlLedgerIC10Review.load()

    if arguments.check_snapshot:
        status = gate.status()
        required = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "commit_authorization_count": 0,
            "commit_occurrence_count": 0,
            "ledger_observation_count": 0,
            "review_request_count": 0,
            "review_request_observation_count": 0,
            "ic10_decision_count": 0,
            "w25_settlement_verified": False,
            "control_ledger_authorization_verified": False,
            "control_ledger_commit_verified": False,
            "control_ledger_readback_verified": False,
            "ic10_review_request_verified": False,
            "ic10_review_request_observed": False,
            "ic10_review_open": False,
            "ic10_decision_recorded": False,
            "runtime_mutated_registry": False,
            "runtime_mutated_control_ledger": False,
            "runtime_sent_review_request": False,
            "runtime_issued_ic10_decision": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "merge_claimed": False,
            "deployment_claimed": False,
            "promotion_claimed": False,
        }
        mismatches = {
            key: status.get(key)
            for key, expected in required.items()
            if status.get(key) != expected
        }
        if mismatches:
            raise RuntimeError(f"W26 protected boundary mismatch: {mismatches}")
        print("PASS_W26_FROZEN_EMPTY_CONTROL_RETURN_AND_IC10_REVIEW")
        return 0

    if arguments.bundle is None:
        parser.error("--bundle is required")
    data = arguments.bundle.read_bytes()
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError(f"bundle exceeds {MAX_BUNDLE_BYTES} bytes")
    bundle = _strict_loads(data.decode("utf-8"))
    if set(bundle) != set(BUNDLE_FIELDS):
        raise ValueError("bundle fields must exactly match W26 return topology")
    if not all(
        (
            arguments.verifier_head,
            arguments.verifier_tree,
            arguments.verifier_ref,
        )
    ):
        raise ValueError(
            "verifier head, tree, and ref are required for bundle validation"
        )
    verifier_head = _commit(arguments.verifier_head, "verifier_head")
    verifier_tree = _commit(arguments.verifier_tree, "verifier_tree")
    if (
        arguments.verifier_ref != CANONICAL_VERIFIER_REF
        or verifier_head != _git("rev-parse", "HEAD")
        or verifier_tree != _git("rev-parse", "HEAD^{tree}")
    ):
        raise ValueError("verifier coordinates do not bind checked-out canonical ref")
    records = tuple(
        json.dumps(bundle[field], ensure_ascii=False, separators=(",", ":"))
        for field in BUNDLE_FIELDS
    )
    result = gate.evaluate_closure(*records)
    envelope = {
        "schema": "athena.w26-control-ledger-ic10-review-preflight/v1",
        "verifier": {
            "repository": "demeet2k/athena-mcp-server",
            "ref": arguments.verifier_ref,
            "head": verifier_head,
            "tree": verifier_tree,
            "contract_digest": W26_CONTRACT,
        },
        "closure": result,
    }
    envelope["preflight_digest"] = _digest(
        _addressed(envelope, "preflight_digest")
    )
    _write(arguments.output, envelope)
    print(json.dumps(envelope, indent=2, sort_keys=True))
    protected = (
        "runtime_mutated_registry",
        "runtime_mutated_control_ledger",
        "runtime_sent_review_request",
        "runtime_issued_ic10_decision",
        "workflow_dispatched",
        "endpoint_contacted",
        "merge_claimed",
        "deployment_claimed",
        "promotion_claimed",
    )
    return (
        0
        if result.get("ic10_review_open")
        and result.get("ic10_decision_recorded") is False
        and all(result.get(field) is False for field in protected)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
