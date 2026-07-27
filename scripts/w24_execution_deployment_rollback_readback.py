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
    FrozenExecutionDeploymentRollbackReadback,
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
    "promotion",
    "deployment",
    "health",
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
            "deployment_readback_count": 0,
            "rollback_occurrence_count": 0,
            "w23_image_published": False,
            "w23_execution_authorization_verified": False,
            "execution_occurrence_verified": False,
            "promotion_observed": False,
            "deployment_readback_verified": False,
            "health_window_verified": False,
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
    bundle = json.loads(data.decode("utf-8"))
    if set(bundle) != set(BUNDLE_FIELDS):
        raise ValueError("bundle fields must exactly match W24 return topology")
    records = [
        json.dumps(bundle[field], ensure_ascii=False, separators=(",", ":"))
        for field in BUNDLE_FIELDS
    ]
    result = gate.evaluate_closure(*records)
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
