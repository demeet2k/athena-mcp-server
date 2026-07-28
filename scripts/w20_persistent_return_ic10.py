#!/usr/bin/env python3
"""Validate the W20 persistent-return and IC10 evidence chain.

This command accepts only bounded, secret-free records.  It can validate and
compile a ledger candidate, but it cannot mutate the frozen ledger or reviewer
registry, dispatch work, contact an endpoint, or authorize promotion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.persistent_return_ic10 import (  # noqa: E402
    FrozenPersistentReturnIC10Gate,
)


LEGAL_CLOSURE_STATUS = (
    "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_AND_IC10_REVIEW__"
    "LEDGER_COMMIT_AND_PROMOTION_OPEN"
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
    activation_packet: Path,
    provider_evidence: Path,
    provenance_witness: Path,
    provider_admission: Path,
    provider_return: Path,
    execution_authorization: Path,
    persistent_witness: Path,
    control_admission: Path,
    review_packet: Path,
    ic10_decision: Path,
) -> dict[str, Any]:
    """Evaluate all ten W17-W20 records against commit-pinned registries."""
    gate = FrozenPersistentReturnIC10Gate.load()
    return gate.evaluate_closure(
        _read(activation_packet),
        _read(provider_evidence),
        _read(provenance_witness),
        _read(provider_admission),
        _read(provider_return),
        _read(execution_authorization),
        _read(persistent_witness),
        _read(control_admission),
        _read(review_packet),
        _read(ic10_decision),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-snapshot", action="store_true")
    parser.add_argument("--activation-packet", type=Path)
    parser.add_argument("--provider-evidence", type=Path)
    parser.add_argument("--provenance-witness", type=Path)
    parser.add_argument("--provider-admission", type=Path)
    parser.add_argument("--provider-return", type=Path)
    parser.add_argument("--execution-authorization", type=Path)
    parser.add_argument("--persistent-witness", type=Path)
    parser.add_argument("--control-admission", type=Path)
    parser.add_argument("--review-packet", type=Path)
    parser.add_argument("--ic10-decision", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w20-return-ic10-preflight.json"),
    )
    arguments = parser.parse_args()

    gate = FrozenPersistentReturnIC10Gate.load()
    if arguments.check_snapshot:
        status = gate.status()
        if status["production_control_authority_count"] != 0:
            raise RuntimeError(
                "checked-in W20 control authority registry must remain empty"
            )
        if status["production_ic10_reviewer_count"] != 0:
            raise RuntimeError(
                "checked-in W20 IC10 reviewer registry must remain empty"
            )
        if status["ledger_entry_count"] != 0:
            raise RuntimeError(
                "checked-in W20 persistent-return ledger must remain empty"
            )
        if (
            status["runtime_can_mutate_ledger"] is not False
            or status["runtime_can_promote"] is not False
        ):
            raise RuntimeError("W20 snapshot crosses a protected boundary")
        print("PASS_W20_FROZEN_EMPTY_AUTHORITY_REVIEWER_AND_LEDGER_STATE")
        return 0

    required = {
        "--activation-packet": arguments.activation_packet,
        "--provider-evidence": arguments.provider_evidence,
        "--provenance-witness": arguments.provenance_witness,
        "--provider-admission": arguments.provider_admission,
        "--provider-return": arguments.provider_return,
        "--execution-authorization": arguments.execution_authorization,
        "--persistent-witness": arguments.persistent_witness,
        "--control-admission": arguments.control_admission,
        "--review-packet": arguments.review_packet,
        "--ic10-decision": arguments.ic10_decision,
    }
    missing = [flag for flag, value in required.items() if value is None]
    if missing:
        parser.error("required arguments: " + ", ".join(missing))

    result = evaluate_files(
        activation_packet=arguments.activation_packet,
        provider_evidence=arguments.provider_evidence,
        provenance_witness=arguments.provenance_witness,
        provider_admission=arguments.provider_admission,
        provider_return=arguments.provider_return,
        execution_authorization=arguments.execution_authorization,
        persistent_witness=arguments.persistent_witness,
        control_admission=arguments.control_admission,
        review_packet=arguments.review_packet,
        ic10_decision=arguments.ic10_decision,
    )
    _write_json(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") != LEGAL_CLOSURE_STATUS:
        return 1
    if (
        result.get("persistent_witness_validated") is not True
        or result.get("external_persistence_attestation_verified") is not True
        or result.get("control_plane_witness_admitted") is not True
        or result.get("ic10_review_recorded") is not True
        or result.get("ledger_entry_committed") is not False
        or result.get("promotion_authorized") is not False
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
