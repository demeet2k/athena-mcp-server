from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.lp57omega_b_prime_support import (  # noqa: E402
    B_PRIME_DOC_MIRROR,
    B_PRIME_DOC_PATH,
    B_PRIME_MANIFEST_REPORT_PATH,
    B_PRIME_REGISTRY_MIRROR,
    B_PRIME_REGISTRY_PATH,
    LP57OMEGA_MANIFEST_PATH,
    build_b_prime_registry,
    load_json,
    verify_b_prime_registry,
    write_json,
)
from self_actualize.runtime.hemisphere_brain_support import utc_now  # noqa: E402


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    expected = build_b_prime_registry()
    actual = load_json(B_PRIME_REGISTRY_PATH)
    mirror = load_json(B_PRIME_REGISTRY_MIRROR)
    manifest = load_json(LP57OMEGA_MANIFEST_PATH)
    doc_text = B_PRIME_DOC_PATH.read_text(encoding="utf-8")
    mirror_doc_text = B_PRIME_DOC_MIRROR.read_text(encoding="utf-8")

    actual_compare = dict(actual)
    expected_compare = dict(expected)
    actual_compare.pop("generated_at", None)
    expected_compare.pop("generated_at", None)
    ensure(
        actual_compare == expected_compare,
        "canonical B' registry drifted from generated expectation",
    )
    ensure(mirror == actual, "mirror B' registry drifted from canonical")
    ensure(doc_text == mirror_doc_text, "B' markdown mirror drifted")

    verification = verify_b_prime_registry(actual, doc_text)
    ensure(verification["truth"] == "OK", "B' verification failed")

    ensure(
        manifest["counts"].get("b_prime_dense_shell_rows") == 64,
        "manifest dense-shell count drifted",
    )
    ensure(
        manifest["counts"].get("b_prime_witness_rows") == 45,
        "manifest witness-row count drifted",
    )
    ensure(
        manifest["counts"].get("b_prime_pointer_expanded_rows") == 45,
        "manifest pointer-expanded count drifted",
    )
    ensure(
        manifest["counts"].get("b_prime_witness_seed_payloads") == 60,
        "manifest witness-seed payload count drifted",
    )
    ensure(
        manifest["counts"].get("b_prime_replay_seed_payloads") == 60,
        "manifest replay-seed payload count drifted",
    )
    ensure(
        manifest["outputs"].get("b_prime_witness_registry") == str(B_PRIME_REGISTRY_PATH),
        "manifest registry output drifted",
    )
    ensure(
        manifest["outputs"].get("b_prime_witness_doc") == str(B_PRIME_DOC_PATH),
        "manifest doc output drifted",
    )
    ensure(
        manifest["outputs"].get("b_prime_witness_verification")
        == str(B_PRIME_MANIFEST_REPORT_PATH),
        "manifest verification output drifted",
    )

    report = {
        "generated_at": utc_now(),
        "truth": "OK",
        "docs_gate_status": actual["docs_gate_status"],
        "dense_shell_rows": actual["counts"]["dense_shell_rows"],
        "witnessed_rows": actual["counts"]["witnessed_rows"],
        "pointer_expanded_rows": actual["payload_counts"]["pointer_expanded_rows"],
        "witness_seed_payloads": actual["payload_counts"]["witness_seed_payloads"],
        "replay_seed_payloads": actual["payload_counts"]["replay_seed_payloads"],
        "checks": verification["checks"],
    }
    write_json(B_PRIME_MANIFEST_REPORT_PATH, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
