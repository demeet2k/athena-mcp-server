#!/usr/bin/env python3
"""Validate W24 return bundles without dispatching or contacting endpoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.execution_deployment_rollback_readback import (  # noqa: E402
    CANONICAL_RUNTIME_REF,
    CANONICAL_RUNTIME_REPOSITORY,
    FrozenExecutionDeploymentRollbackReadback,
    W23_HARDENING_HEAD,
    W24_HARDENED_CONTRACT,
    WORKFLOW_PATH,
)
from crystal_108d.independent_authority_return import (  # noqa: E402
    _commit,
    _strict_loads,
)


MAX_BUNDLE_BYTES = 1048576
BUNDLE_FIELDS = (
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
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-snapshot", action="store_true")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--verifier-repository")
    parser.add_argument("--verifier-ref")
    parser.add_argument("--verifier-head")
    parser.add_argument("--verifier-parent-head")
    parser.add_argument("--verifier-workflow")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w24-execution-deployment-rollback-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenExecutionDeploymentRollbackReadback.load()

    if arguments.check_snapshot:
        status = gate.status()
        required = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "execution_occurrence_count": 0,
            "execution_consumption_count": 0,
            "deployment_readback_count": 0,
            "previous_safe_deployment_count": 0,
            "rollback_occurrence_count": 0,
            "w23_image_published": False,
            "w23_execution_authorization_verified": False,
            "execution_occurrence_verified": False,
            "execution_consumption_verified": False,
            "execution_authorization_consumed_once": False,
            "fresh_execution_authority_issued": False,
            "fresh_execution_claimed": False,
            "promotion_observed": False,
            "deployment_readback_verified": False,
            "health_window_verified": False,
            "previous_safe_deployment_verified": False,
            "rollback_authorization_verified": False,
            "rollback_occurrence_verified": False,
            "rollback_observation_verified": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "deployment_claimed": False,
            "promotion_claimed": False,
        }
        mismatches = {
            key: status.get(key)
            for key, expected in required.items()
            if status.get(key) != expected
        }
        if mismatches:
            raise RuntimeError(f"W24 protected boundary mismatch: {mismatches}")
        print("PASS_W24_FROZEN_EMPTY_EXECUTION_DEPLOYMENT_ROLLBACK_RETURNS")
        return 0

    if arguments.bundle is None:
        parser.error("--bundle is required")
    data = arguments.bundle.read_bytes()
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError(f"bundle exceeds {MAX_BUNDLE_BYTES} bytes")
    bundle = _strict_loads(data.decode("utf-8"))
    if set(bundle) != set(BUNDLE_FIELDS):
        raise ValueError("bundle fields must exactly match W24 return topology")
    verifier_values = {
        "--verifier-repository": arguments.verifier_repository,
        "--verifier-ref": arguments.verifier_ref,
        "--verifier-head": arguments.verifier_head,
        "--verifier-parent-head": arguments.verifier_parent_head,
        "--verifier-workflow": arguments.verifier_workflow,
    }
    missing = [name for name, value in verifier_values.items() if value is None]
    if missing:
        raise ValueError(
            "bundle validation requires verifier coordinates: "
            + ", ".join(missing)
        )
    verifier_head = _commit(arguments.verifier_head, "verifier.head")
    verifier_parent_head = _commit(
        arguments.verifier_parent_head, "verifier.parent_head"
    )
    if (
        arguments.verifier_repository != CANONICAL_RUNTIME_REPOSITORY
        or arguments.verifier_ref != CANONICAL_RUNTIME_REF
        or arguments.verifier_workflow != WORKFLOW_PATH
        or verifier_parent_head != W23_HARDENING_HEAD
    ):
        raise ValueError("verifier runtime coordinate mismatch")
    records = [
        json.dumps(bundle[field], ensure_ascii=False, separators=(",", ":"))
        for field in BUNDLE_FIELDS
    ]
    result = gate.evaluate_closure(*records)
    result["verification_run"] = {
        "repository": arguments.verifier_repository,
        "ref": arguments.verifier_ref,
        "head": verifier_head,
        "parent_head": verifier_parent_head,
        "workflow": arguments.verifier_workflow,
        "contract_digest": W24_HARDENED_CONTRACT,
    }
    _write(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    verified = bool(result.get("rollback_observation_verified"))
    protected = (
        "runtime_mutated_registry",
        "runtime_issued_authority_signature",
        "workflow_dispatched",
        "endpoint_contacted",
        "merge_claimed",
        "deployment_claimed",
        "promotion_claimed",
    )
    return (
        0
        if verified and all(result.get(field) is False for field in protected)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
