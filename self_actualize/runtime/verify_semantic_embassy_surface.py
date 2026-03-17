from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import swarm_board
from .derive_semantic_embassy_surface import (
    APPO_PATH,
    CURRENT_PACKET_PATH,
    DASHBOARD_PATH,
    FRONTIER_PATH,
    MANUSCRIPT_PATH,
    RENDER_POLICY_PATH,
    SURFACE_REGISTRY_PATH,
    VALIDATOR_REGISTRY_PATH,
    build_payloads,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_semantic_embassy_surface"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def verify_outputs_exist() -> dict[str, Any]:
    for path in [SURFACE_REGISTRY_PATH, VALIDATOR_REGISTRY_PATH, RENDER_POLICY_PATH, DASHBOARD_PATH]:
        ensure(path.exists(), f"missing registry output: {path}")
    return {"outputs": 4}


def verify_docs_gate_honesty() -> dict[str, Any]:
    docs_gate = swarm_board.docs_gate_status()
    policy = load_json(RENDER_POLICY_PATH)
    surface = load_json(SURFACE_REGISTRY_PATH)
    dashboard = load_json(DASHBOARD_PATH)
    ensure(policy["docs_gate_status"] == docs_gate["status"], "render policy docs gate drifted")
    ensure(surface["docs_gate_status"] == docs_gate["status"], "surface registry docs gate drifted")
    ensure(dashboard["docs_gate_status"] == docs_gate["status"], "dashboard docs gate drifted")
    ensure(docs_gate["status"] == "BLOCKED", "docs gate must remain BLOCKED in v1")
    return {"docs_gate_status": docs_gate["status"]}


def verify_manuscript_and_appo_alignment() -> dict[str, Any]:
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8", errors="ignore")
    appo = APPO_PATH.read_text(encoding="utf-8", errors="ignore")
    object_family = [
        "SemanticEmbassySurface",
        "ClaimSurface",
        "AudienceProfile",
        "RegisterProfile",
        "InterfaceContract",
        "MessageEnvelope",
        "TranslationSurface",
        "DomainPack",
        "ReleaseBundle",
        "SafeWordingBundle",
        "KairosAssessment",
        "RhetoricalPreview",
        "SemanticExportValidatorResult",
    ]
    policy_lines = [
        "explanatory -> minimal",
        "benchmark_safe -> minimal",
        "release_safe -> diplomatic",
        "public_claim -> diplomatic",
        "federation_claim -> diplomatic",
        "rhetorical -> preview_only",
    ]
    missing_manuscript = [token for token in object_family + policy_lines if token not in manuscript]
    missing_appo = [token for token in object_family + policy_lines if token not in appo]
    ensure(not missing_manuscript, f"manuscript is missing embassy terms: {missing_manuscript}")
    ensure(not missing_appo, f"AppO mirror is missing embassy terms: {missing_appo}")
    return {"object_family_count": len(object_family), "policy_line_count": len(policy_lines)}


def verify_replay_example() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_PATH)
    replay = dashboard["replay_example"]
    ensure(replay["validator_status"] == "PASS", "replay example did not pass validation")
    ensure(replay["audience_emit"] is True, "replay example did not produce an emitted audience bundle")
    ensure("RecertificationPack/ReleaseTrustPack" in replay["input_flow"], "replay flow is incomplete")
    return {"validator_status": replay["validator_status"]}


def verify_failure_cases() -> dict[str, Any]:
    validator = load_json(VALIDATOR_REGISTRY_PATH)
    failures = {record["label"]: record for record in validator["failure_cases"]}
    expected = {
        "rhetorical/public render requested in v1": "rhetorical",
        "public wording exceeds benchmark or release support": "wording exceeds allowed ceiling",
        "missing replay refs": "missing replay refs",
        "missing downgrade replacements": "missing downgrade replacements",
        "benchmark-facing surface with non-benchmark-safe names": "non-benchmark-safe names",
        "federation-facing surface with missing federation-safe terms": "missing federation-safe terms",
    }
    for label, needle in expected.items():
        ensure(label in failures, f"missing failure case: {label}")
        record = failures[label]
        ensure(record["status"] == "FAIL", f"failure case unexpectedly passed: {label}")
        joined = " | ".join(record["blocked_reasons"]).lower()
        ensure(needle.lower() in joined, f"failure case {label} missing expected reason: {needle}")
    return {"failure_cases": len(expected)}


def verify_render_policy_determinism() -> dict[str, Any]:
    existing = load_json(RENDER_POLICY_PATH)
    rebuilt = build_payloads()["policy"]
    ensure(normalize_json(existing) == normalize_json(rebuilt), "render policy serialization drifted")
    return {"policy_hash": existing["policy_hash"]}


def verify_frontier_registration() -> dict[str, Any]:
    current_packet = CURRENT_PACKET_PATH.read_text(encoding="utf-8", errors="ignore")
    frontier = FRONTIER_PATH.read_text(encoding="utf-8", errors="ignore")
    ensure(
        "After Release Notary / public-claim attestation, the next lawful public-language organ is the Semantic Embassy."
        in current_packet,
        "current packet is missing post-attestation Semantic Embassy registration",
    )
    ensure("TF-010" in frontier and "Semantic Embassy post-attestation audience reception surface" in frontier, "frontier ledger is missing TF-010")
    return {"frontier_row": "TF-010"}


def verify_surface_hash_determinism() -> dict[str, Any]:
    existing = load_json(SURFACE_REGISTRY_PATH)
    rebuilt = build_payloads()["surface"]
    ensure(existing["surface_hash"] == rebuilt["surface_hash"], "surface hash drifted across rebuild")
    return {"surface_hash": existing["surface_hash"]}


def main() -> None:
    checks = {
        "outputs_exist": verify_outputs_exist(),
        "docs_gate_honesty": verify_docs_gate_honesty(),
        "manuscript_and_appo_alignment": verify_manuscript_and_appo_alignment(),
        "replay_example": verify_replay_example(),
        "failure_cases": verify_failure_cases(),
        "render_policy_determinism": verify_render_policy_determinism(),
        "surface_hash_determinism": verify_surface_hash_determinism(),
        "frontier_registration": verify_frontier_registration(),
    }
    print(
        json.dumps(
            {
                "derivation_command": DERIVATION_COMMAND,
                "status": "OK",
                "checks": checks,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
