#!/usr/bin/env python3
"""Validate the secret-free W19 provider-admission execution envelope.

This command is the workflow boundary for KC144.XNAV.W19.  It never accepts
private keys or bearer material, never mutates the frozen authority registry,
and never dispatches a workflow.  A zero exit status means only that the
commit-pinned control signatures authorize the protected workflow to proceed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.provider_admission_execution import (  # noqa: E402
    FrozenProviderAdmissionExecutionGate,
)


LEGAL_EXECUTION_STATUS = (
    "PASS_CONTROL_SIGNED_PROTECTED_EXECUTION_AUTHORIZATION__NOT_DISPATCHED"
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
) -> dict[str, Any]:
    """Evaluate all six secret-free W19 records against the frozen registry."""
    gate = FrozenProviderAdmissionExecutionGate.load()
    return gate.evaluate_execution(
        _read(activation_packet),
        _read(provider_evidence),
        _read(provenance_witness),
        _read(provider_admission),
        _read(provider_return),
        _read(execution_authorization),
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
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("w19-execution-preflight.json"),
    )
    arguments = parser.parse_args()

    gate = FrozenProviderAdmissionExecutionGate.load()
    if arguments.check_snapshot:
        status = gate.status()
        if status["production_control_authority_count"] != 0:
            raise RuntimeError(
                "checked-in W19 production authority registry must remain empty"
            )
        if status["boundaries"]["workflow_dispatched"] is not False:
            raise RuntimeError("W19 snapshot crosses the dispatch boundary")
        print("PASS_W19_FROZEN_EMPTY_AUTHORITY_REGISTRY")
        return 0

    required = {
        "--activation-packet": arguments.activation_packet,
        "--provider-evidence": arguments.provider_evidence,
        "--provenance-witness": arguments.provenance_witness,
        "--provider-admission": arguments.provider_admission,
        "--provider-return": arguments.provider_return,
        "--execution-authorization": arguments.execution_authorization,
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
    )
    _write_json(arguments.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") != LEGAL_EXECUTION_STATUS:
        return 1
    if (
        result.get("execution_authorization_verified") is not True
        or result.get("dispatch_eligible_in_protected_workflow") is not True
        or result.get("workflow_dispatched") is not False
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
