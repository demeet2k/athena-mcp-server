#!/usr/bin/env python3
"""Validate W25 persistence/settlement bundles without side effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.persistent_promotion_settlement import (  # noqa: E402
    FrozenPersistentPromotionSettlement,
    W25_CONTRACT,
)
from crystal_108d.independent_authority_return import (  # noqa: E402
    _addressed,
    _commit,
    _digest,
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
    "persistence_proof",
    "persistence_observation",
    "promotion_settlement",
    "settlement_observation",
)
CANONICAL_VERIFIER_REF = (
    "refs/heads/agent/w15-reconcile-capsule-deep-hardening"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


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
        default=Path("w25-persistent-promotion-settlement-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenPersistentPromotionSettlement.load()

    if arguments.check_snapshot:
        status = gate.status()
        required = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "persistence_proof_count": 0,
            "persistence_observation_count": 0,
            "promotion_settlement_count": 0,
            "settlement_observation_count": 0,
            "w24_image_published": False,
            "w24_return_bundle_verified": False,
            "return_persistence_proved": False,
            "return_persistence_observed": False,
            "promotion_settlement_verified": False,
            "settlement_observation_verified": False,
            "settlement_replay_guard_verified": False,
            "settlement_closure_is_idempotent": False,
            "settlement_disposition": None,
            "runtime_persisted_return": False,
            "runtime_issued_settlement": False,
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
            raise RuntimeError(f"W25 protected boundary mismatch: {mismatches}")
        print("PASS_W25_FROZEN_EMPTY_PERSISTENCE_AND_SETTLEMENT")
        return 0

    if arguments.bundle is None:
        parser.error("--bundle is required")
    data = arguments.bundle.read_bytes()
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError(f"bundle exceeds {MAX_BUNDLE_BYTES} bytes")
    bundle = _strict_loads(data.decode("utf-8"))
    if set(bundle) != set(BUNDLE_FIELDS):
        raise ValueError("bundle fields must exactly match W25 settlement topology")
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
    records = [
        json.dumps(bundle[field], ensure_ascii=False, separators=(",", ":"))
        for field in BUNDLE_FIELDS
    ]
    result = gate.evaluate_closure(*records)
    envelope = {
        "schema": "athena.w25-persistent-settlement-preflight/v1",
        "verifier": {
            "repository": "demeet2k/athena-mcp-server",
            "ref": arguments.verifier_ref,
            "head": verifier_head,
            "tree": verifier_tree,
            "contract_digest": W25_CONTRACT,
        },
        "closure": result,
    }
    envelope["preflight_digest"] = _digest(
        _addressed(envelope, "preflight_digest")
    )
    _write(arguments.output, envelope)
    print(json.dumps(envelope, indent=2, sort_keys=True))
    verified = bool(result.get("settlement_observation_verified"))
    protected = (
        "runtime_mutated_registry",
        "runtime_issued_authority_signature",
        "runtime_persisted_return",
        "runtime_issued_settlement",
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
