#!/usr/bin/env python3
"""Validate W22 independent authority returns without mutating any registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.independent_authority_return import (  # noqa: E402
    FrozenIndependentAuthorityReturn,
)


def _read(path: Path) -> str:
    data = path.read_bytes()
    if len(data) > 262144:
        raise ValueError(f"{path} exceeds 262144 bytes")
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
        choices=("commit", "promotion", "closure"),
        default="closure",
    )
    parser.add_argument("--commit-return", type=Path)
    parser.add_argument("--git-observation", type=Path)
    parser.add_argument("--promotion-return", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w22-independent-authority-return-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenIndependentAuthorityReturn.load()

    if arguments.check_snapshot:
        status = gate.status()
        required = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "admitted_return_count": 0,
            "w21_custody_grants_authority": False,
            "w21_control_observation_grants_authority": False,
            "ledger_entry_committed": False,
            "promotion_authorized": False,
            "promotion_execution_authorized": False,
            "promotion_executed": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
        }
        mismatches = {
            key: status.get(key)
            for key, expected in required.items()
            if status.get(key) != expected
        }
        if mismatches:
            raise RuntimeError(f"W22 protected boundary mismatch: {mismatches}")
        print(
            "PASS_W22_FROZEN_EMPTY_SOURCE_REVISION_OCCURRENCE_AND_RETURN_LEDGER"
        )
        return 0

    if arguments.commit_return is None or arguments.git_observation is None:
        parser.error("--commit-return and --git-observation are required")
    commit_return = _read(arguments.commit_return)
    observation = _read(arguments.git_observation)
    if arguments.mode == "commit":
        result = gate.inspect_ledger_commit_return(commit_return, observation)
        legal = bool(result.get("ledger_entry_committed"))
    else:
        if arguments.promotion_return is None:
            parser.error("--promotion-return is required for promotion/closure")
        promotion = _read(arguments.promotion_return)
        result = gate.evaluate_closure(commit_return, observation, promotion)
        legal = bool(result.get("promotion_decision_return_verified"))
    _write(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not legal:
        return 1
    protected = (
        "runtime_mutated_registry",
        "runtime_mutated_return_ledger",
        "workflow_dispatched",
        "endpoint_contacted",
        "promotion_execution_authorized",
        "promotion_executed",
        "deployment_claimed",
        "merge_claimed",
        "promotion_claimed",
    )
    return 0 if all(result.get(field) is False for field in protected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
