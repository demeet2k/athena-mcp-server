#!/usr/bin/env python3
"""Validate W21 ledger-commit and promotion-authority returns.

The command accepts bounded, secret-free records.  It verifies signed
external returns but cannot mutate a ledger, dispatch work, contact an
endpoint, deploy, merge, or execute promotion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.ledger_commit_promotion_handoff import (  # noqa: E402
    FrozenLedgerCommitPromotionHandoff,
)


LEGAL_CLOSURE_STATUS = (
    "PASS_W21_LEDGER_COMMIT_AND_PROMOTION_DECISION_CLOSED__"
    "PROMOTION_EXECUTION_RECEIPT_OPEN"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def evaluate_files(
    *,
    transaction: Path,
    authorization: Path,
    commit_receipt: Path,
    promotion_packet: Path,
    promotion_decision: Path,
) -> dict[str, Any]:
    """Evaluate the five W21 records against commit-pinned registries."""
    gate = FrozenLedgerCommitPromotionHandoff.load()
    return gate.evaluate_closure(
        _read(transaction),
        _read(authorization),
        _read(commit_receipt),
        _read(promotion_packet),
        _read(promotion_decision),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-snapshot", action="store_true")
    parser.add_argument("--transaction", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--commit-receipt", type=Path)
    parser.add_argument("--promotion-packet", type=Path)
    parser.add_argument("--promotion-decision", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w21-commit-promotion-preflight.json"),
    )
    arguments = parser.parse_args()

    gate = FrozenLedgerCommitPromotionHandoff.load()
    if arguments.check_snapshot:
        status = gate.status()
        if status["w20_control_protocol_admission_observed"] is not True:
            raise RuntimeError("exact W20 control protocol receipt is not pinned")
        if status["w20_control_receipt_grants_production_authority"] is not False:
            raise RuntimeError("W20 protocol observation cannot grant authority")
        if status["production_commit_authority_count"] != 0:
            raise RuntimeError(
                "checked-in W21 commit authority registry must remain empty"
            )
        if status["production_promotion_authority_count"] != 0:
            raise RuntimeError(
                "checked-in W21 promotion authority registry must remain empty"
            )
        if status["committed_ledger_entry_count"] != 0:
            raise RuntimeError(
                "checked-in W21 committed ledger must remain empty"
            )
        if (
            status["runtime_can_mutate_ledger"] is not False
            or status["runtime_can_promote"] is not False
        ):
            raise RuntimeError("W21 snapshot crosses a protected boundary")
        print("PASS_W21_FROZEN_EMPTY_COMMIT_PROMOTION_AUTHORITY_AND_LEDGER_STATE")
        return 0

    required = {
        "--transaction": arguments.transaction,
        "--authorization": arguments.authorization,
        "--commit-receipt": arguments.commit_receipt,
        "--promotion-packet": arguments.promotion_packet,
        "--promotion-decision": arguments.promotion_decision,
    }
    missing = [flag for flag, value in required.items() if value is None]
    if missing:
        parser.error("required arguments: " + ", ".join(missing))

    result = evaluate_files(
        transaction=arguments.transaction,
        authorization=arguments.authorization,
        commit_receipt=arguments.commit_receipt,
        promotion_packet=arguments.promotion_packet,
        promotion_decision=arguments.promotion_decision,
    )
    _write_json(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") != LEGAL_CLOSURE_STATUS:
        return 1
    if (
        result.get("ledger_entry_committed") is not True
        or result.get("promotion_authorized") is not True
        or result.get("promotion_executed") is not False
        or result.get("promotion_claimed") is not False
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
