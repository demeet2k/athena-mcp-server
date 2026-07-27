#!/usr/bin/env python3
"""Validate or materialize a P10 host contract without exposing secrets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

try:
    from scripts.p10_contract import (
        PREPARED_OUTCOME,
        TOKEN_ENV,
        canonical_bytes,
        content_addressed_receipt,
        content_digest,
        environment_target_fields,
        load_contract,
        materialize_authorized_contract,
        secret_free,
        validate_contract,
        validate_token_from_environment,
    )
except ModuleNotFoundError:
    from p10_contract import (
        PREPARED_OUTCOME,
        TOKEN_ENV,
        canonical_bytes,
        content_addressed_receipt,
        content_digest,
        environment_target_fields,
        load_contract,
        materialize_authorized_contract,
        secret_free,
        validate_contract,
        validate_token_from_environment,
    )


def _write_json(path: Path | None, value: dict) -> None:
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path is None:
        print(content, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def prepared_receipt(contract: dict) -> dict:
    body = {
        "schema": "athena.p10-deployment-preflight/v1",
        "phase": "P10",
        "verdict": PREPARED_OUTCOME,
        "contract_digest": content_digest(contract),
        "authorized_target_selected": False,
        "endpoint": None,
        "bearer_secret_provisioned": False,
        "persistent_witness": None,
        "deployment_claimed": False,
        "promotion_ready": False,
        "promotion_claimed": False,
    }
    return content_addressed_receipt("p10-preflight", body)


def authorized_receipt(contract: dict, token: str) -> dict:
    body = {
        "schema": "athena.p10-deployment-preflight/v1",
        "phase": "P10",
        "verdict": "READY_TO_PROBE_AUTHORIZED_TARGET",
        "contract_digest": content_digest(contract),
        "target": contract["target"],
        "endpoint": contract["network"]["external_mcp_endpoint"],
        "image_reference": contract["image"]["reference"],
        "source_commit": contract["source_commit"],
        "authentication": {
            "environment": TOKEN_ENV,
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": contract["authentication"]["secret_store_ref"],
        },
        "persistent_witness": None,
        "deployment_claimed": False,
        "promotion_ready": False,
        "promotion_claimed": False,
    }
    if not secret_free(body, token):
        raise RuntimeError("preflight receipt failed the secret-free boundary")
    return content_addressed_receipt("p10-preflight", body)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("contract", type=Path)
    validate_parser.add_argument(
        "--mode", choices=("prepared", "authorized"), required=True
    )
    validate_parser.add_argument("--output", type=Path)

    materialize_parser = subparsers.add_parser("materialize-authorized")
    materialize_parser.add_argument("prepared_contract", type=Path)
    materialize_parser.add_argument("--output", required=True, type=Path)

    arguments = parser.parse_args()
    if arguments.command == "materialize-authorized":
        token = os.environ.get(TOKEN_ENV)
        validate_token_from_environment(token, argv=sys.argv[1:])
        prepared = load_contract(arguments.prepared_contract)
        target = materialize_authorized_contract(
            prepared, **environment_target_fields()
        )
        validate_contract(
            target,
            require_authorized_target=True,
            token=token,
            argv=sys.argv[1:],
        )
        if not secret_free(target, token):
            raise RuntimeError("authorized target contract contains bearer secret material")
        _write_json(arguments.output, target)
        return 0

    contract = load_contract(arguments.contract)
    if arguments.mode == "prepared":
        validate_contract(contract, require_authorized_target=False)
        receipt = prepared_receipt(contract)
    else:
        token = os.environ.get(TOKEN_ENV)
        validate_token_from_environment(token, argv=sys.argv[1:])
        validate_contract(
            contract,
            require_authorized_target=True,
            token=token,
            argv=sys.argv[1:],
        )
        receipt = authorized_receipt(contract, token)
    _write_json(arguments.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
