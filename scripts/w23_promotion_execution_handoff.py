#!/usr/bin/env python3
"""Validate W23 promotion/execution handoffs without executing them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.promotion_execution_handoff import (  # noqa: E402
    FrozenPromotionExecutionHandoff,
)


MAX_RECORD_BYTES = 262144


def _read(path: Path) -> str:
    data = path.read_bytes()
    if len(data) > MAX_RECORD_BYTES:
        raise ValueError(f"{path} exceeds {MAX_RECORD_BYTES} bytes")
    return data.decode("utf-8")


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-snapshot", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("quorum", "handoff", "closure"),
        default="closure",
    )
    parser.add_argument("--challenge", type=Path)
    parser.add_argument("--publication", type=Path)
    parser.add_argument("--observation", type=Path)
    parser.add_argument("--policy-a", type=Path)
    parser.add_argument("--policy-b", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w23-promotion-execution-handoff-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenPromotionExecutionHandoff.load()

    if arguments.check_snapshot:
        status = gate.status()
        required = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "freshness_challenge_count": 0,
            "publication_proof_count": 0,
            "execution_authorization_count": 0,
            "artifact_publication_observed": False,
            "promotion_policy_a_verified": False,
            "promotion_policy_b_verified": False,
            "w22_image_published": False,
            "promotion_quorum_satisfied": False,
            "execution_authorized": False,
            "promotion_executed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
        }
        mismatches = {
            key: status.get(key)
            for key, expected in required.items()
            if status.get(key) != expected
        }
        if mismatches:
            raise RuntimeError(f"W23 protected boundary mismatch: {mismatches}")
        print("PASS_W23_FROZEN_EMPTY_SIX_ROLE_PROMOTION_EXECUTION_HANDOFF")
        return 0

    paths = {
        "challenge": arguments.challenge,
        "publication": arguments.publication,
        "observation": arguments.observation,
        "policy_a": arguments.policy_a,
        "policy_b": arguments.policy_b,
    }
    missing = [name for name, path in paths.items() if path is None]
    if missing:
        parser.error("required inputs missing: " + ", ".join(missing))
    records = {name: _read(path) for name, path in paths.items() if path}

    if arguments.mode == "quorum":
        result = gate.evaluate_quorum(
            records["challenge"],
            records["publication"],
            records["observation"],
            records["policy_a"],
            records["policy_b"],
        )
        legal = bool(result.get("promotion_quorum_satisfied"))
    else:
        if arguments.authorization is None:
            parser.error("--authorization is required for handoff/closure")
        result = gate.inspect_execution_authorization(
            records["challenge"],
            records["publication"],
            records["observation"],
            records["policy_a"],
            records["policy_b"],
            _read(arguments.authorization),
        )
        legal = bool(result.get("execution_authorized"))

    _write(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    protected = (
        "runtime_mutated_registry",
        "workflow_dispatched",
        "endpoint_contacted",
        "promotion_executed",
        "deployment_claimed",
        "merge_claimed",
        "promotion_claimed",
        "execution_receipt_observed",
    )
    return (
        0
        if legal and all(result.get(field) is False for field in protected)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
