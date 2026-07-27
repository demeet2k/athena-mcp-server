#!/usr/bin/env python3
"""Validate W27-W31 five-wave bundles without production side effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.five_wave_review_closure import (  # noqa: E402
    FrozenFiveWaveReviewClosure,
    W27_W31_CONTRACT,
)
from crystal_108d.independent_authority_return import (  # noqa: E402
    _addressed,
    _commit,
    _digest,
    _strict_loads,
)


MAX_BUNDLE_BYTES = 1572864
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
        default=Path("w27-w31-five-wave-preflight.json"),
    )
    arguments = parser.parse_args()
    gate = FrozenFiveWaveReviewClosure.load()

    if arguments.check_snapshot:
        status = gate.status()
        required_zero = {
            "authority_source_count": 0,
            "authority_revision_count": 0,
            "record_count": 0,
        }
        mismatches = {
            key: status.get(key)
            for key, expected in required_zero.items()
            if status.get(key) != expected
        }
        protected = (
            "runtime_mutated_authority_registry",
            "runtime_mutated_control_ledger",
            "runtime_issued_decision_or_disposition",
            "runtime_published_artifact",
            "runtime_activated_endpoint",
            "workflow_dispatched",
            "endpoint_contacted",
            "image_published",
            "merged",
            "deployed",
            "promoted",
            "production_effect_claimed",
        )
        mismatches.update(
            {
                key: status.get(key)
                for key in protected
                if status.get(key) is not False
            }
        )
        if mismatches:
            raise RuntimeError(
                f"W27-W31 protected boundary mismatch: {mismatches}"
            )
        print("PASS_W27_W31_FROZEN_EMPTY_FIVE_WAVE_PROTOCOL")
        return 0

    if arguments.bundle is None:
        parser.error("--bundle is required")
    data = arguments.bundle.read_bytes()
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError(f"bundle exceeds {MAX_BUNDLE_BYTES} bytes")
    bundle = _strict_loads(data.decode("utf-8"))
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
        raise ValueError(
            "verifier coordinates do not bind checked-out canonical ref"
        )
    result = gate.verify_bundle(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    )
    envelope = {
        "schema": "athena.w27-w31-five-wave-preflight/v1",
        "verifier": {
            "repository": "demeet2k/athena-mcp-server",
            "ref": arguments.verifier_ref,
            "head": verifier_head,
            "tree": verifier_tree,
            "contract_digest": W27_W31_CONTRACT,
        },
        "closure": result,
        "preflight_digest": "",
    }
    envelope["preflight_digest"] = _digest(
        _addressed(envelope, "preflight_digest")
    )
    _write(arguments.output, envelope)
    print(json.dumps(envelope, indent=2, sort_keys=True))
    return (
        0
        if result.get("status")
        == (
            "PASS_W27_W31_COMPLETE_SIGNED_EVIDENCE_BUNDLE__"
            "VERIFIER_REMAINS_NON_EFFECTING"
        )
        and result.get("production_effect_claimed") is False
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
