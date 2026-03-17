from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import swarm_board
from .derive_corpus_integration_wave import (
    ACTIVE_RUN_PATH,
    AGENT_REGISTRY_PATH,
    APPP_PATH,
    CHANGE_FEED_PATH,
    CURRENT_PACKET_PATH,
    DASHBOARD_PATH,
    DEPLOYMENT_PATH,
    FRONTIER_PATH,
    GUIDE_PATH,
    LANE_POLICY_PATH,
    QUEUE_PATH,
    REQUESTS_PATH,
    SURFACE_REGISTRY_PATH,
    VALIDATION_PATH,
    build_payloads,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_corpus_integration_wave"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def verify_outputs_exist() -> dict[str, Any]:
    for path in [SURFACE_REGISTRY_PATH, AGENT_REGISTRY_PATH, LANE_POLICY_PATH, DASHBOARD_PATH]:
        ensure(path.exists(), f"missing registry output: {path}")
    return {"outputs": 4}


def verify_docs_gate_honesty() -> dict[str, Any]:
    docs_gate = swarm_board.docs_gate_status()
    surface = load_json(SURFACE_REGISTRY_PATH)
    agents = load_json(AGENT_REGISTRY_PATH)
    policy = load_json(LANE_POLICY_PATH)
    dashboard = load_json(DASHBOARD_PATH)
    ensure(docs_gate["status"] == "BLOCKED", "docs gate must remain BLOCKED")
    for payload in [surface, agents, policy, dashboard]:
        ensure(payload["docs_gate_status"] == docs_gate["status"], "docs gate drifted in generated payloads")
    return {"docs_gate_status": docs_gate["status"]}


def verify_manuscript_and_appp_alignment() -> dict[str, Any]:
    manuscript = DEPLOYMENT_PATH.read_text(encoding="utf-8", errors="ignore")
    appp = APPP_PATH.read_text(encoding="utf-8", errors="ignore")
    object_family = [
        "DeploymentMonitoringSurface",
        "DeploymentProfile",
        "RuntimeLane",
        "ActivationGate",
        "ObservabilitySurface",
        "MonitoringProbe",
        "AlertPolicy",
        "HealthWindow",
        "RollbackTrigger",
        "EscalationRoute",
        "ExecutionReceipt",
        "DeploymentMonitorResult",
        "CorpusIntegrationWave",
        "AwakeningAgentProfile",
        "TransitionSupportNote",
        "RegionLaneAssignment",
        "IntegrationMonitorResult",
    ]
    policy_lines = [
        "offline_replay = active",
        "internal_preview = active",
        "public_release = gated",
        "federation_release = gated",
        "live_autonomous = blocked",
    ]
    for token in object_family + policy_lines:
        ensure(token in manuscript, f"025 manuscript missing token: {token}")
        ensure(token in appp, f"AppP mirror missing token: {token}")
    return {"object_family_count": len(object_family), "policy_line_count": len(policy_lines)}


def verify_region_coverage() -> dict[str, Any]:
    policy = load_json(LANE_POLICY_PATH)
    regions = policy["region_assignments"]
    required = {
        "self_actualize",
        "DEEPER CRYSTALIZATION",
        "Voynich",
        "MATH",
        "Athena FLEET",
        "QSHRINK - ATHENA (internal use)",
        "Trading Bot",
        "ECOSYSTEM",
        "NERUAL NETWORK",
        "ORGIN",
        "CLEAN",
        "NERVOUS_SYSTEM",
    }
    seen = {record["region_name"] for record in regions}
    ensure(required.issubset(seen), f"missing region assignments: {sorted(required - seen)}")
    for record in regions:
        ensure(record["owner_profile_id"], f"owner missing for {record['region_name']}")
        ensure(record["runtime_lane"], f"lane missing for {record['region_name']}")
        ensure(record["receipt_class"], f"receipt class missing for {record['region_name']}")
    return {"region_count": len(regions)}


def verify_support_note_coverage() -> dict[str, Any]:
    agents = load_json(AGENT_REGISTRY_PATH)
    profiles = agents["agent_profiles"]
    notes = agents["transition_support_notes"]
    ensure(agents["profile_counts"]["total"] == 22, "combined agent registry should contain 22 profiles")
    note_profile_ids = {note["profile_id"] for note in notes}
    profile_ids = {profile["profile_id"] for profile in profiles}
    ensure(profile_ids == note_profile_ids, "every agent profile must have exactly one transition support note")
    return {"profile_count": len(profiles), "note_count": len(notes)}


def verify_public_grade_rule() -> dict[str, Any]:
    policy = load_json(LANE_POLICY_PATH)
    ensure(
        policy["public_grade_rule"] == "no route reaches public_grade without replay proof and Semantic Embassy validation",
        "public grade rule drifted",
    )
    failures = {record["label"]: record["result"] for record in policy["blocked_cases"]}
    bypass = failures["public-grade bypass"]
    joined = " | ".join(bypass["blocked_reasons"]).lower()
    ensure("missing replay proof" in joined, "public-grade bypass should fail replay proof")
    ensure("semantic embassy validation missing".lower() in joined, "public-grade bypass should fail semantic validation")
    return {"public_grade_rule": "verified"}


def verify_passing_example() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_PATH)
    passing = dashboard["passing_example"]
    ensure(passing["receipt"]["deployment_lane"] == "internal_preview", "passing example must target internal_preview")
    ensure(passing["integration_monitor_result"]["monitor_decision"] == "sustain", "passing example should sustain")
    ensure(
        passing["deployment_monitor_result"]["decision"] == "sustain",
        "deployment monitor result should sustain in the passing example",
    )
    return {"lane": passing["receipt"]["deployment_lane"]}


def verify_failure_cases() -> dict[str, Any]:
    policy = load_json(LANE_POLICY_PATH)
    failures = {record["label"]: record["result"] for record in policy["blocked_cases"]}
    expected = {
        "docs-gate breach": "docs gate remains blocked",
        "public-grade bypass": "missing replay proof",
        "missing probe": "missing monitoring probe",
        "missing rollback": "missing rollback trigger",
        "ownerless region assignment": "ownerless region assignment",
        "live autonomous deployment request": "live autonomous deployment is blocked in v1",
    }
    for label, needle in expected.items():
        ensure(label in failures, f"missing failure case: {label}")
        joined = " | ".join(failures[label]["blocked_reasons"]).lower()
        ensure(needle in joined, f"failure case {label} missing expected reason: {needle}")
    return {"failure_cases": len(expected)}


def verify_determinism() -> dict[str, Any]:
    existing = {
        "surface": load_json(SURFACE_REGISTRY_PATH),
        "agents": load_json(AGENT_REGISTRY_PATH),
        "policy": load_json(LANE_POLICY_PATH),
        "dashboard": load_json(DASHBOARD_PATH),
    }
    rebuilt = build_payloads()
    ensure(normalize_json(existing["surface"]) == normalize_json(rebuilt["surface"]), "surface registry drifted")
    ensure(normalize_json(existing["agents"]) == normalize_json(rebuilt["agents"]), "agent registry drifted")
    ensure(normalize_json(existing["policy"]) == normalize_json(rebuilt["policy"]), "lane policy drifted")
    ensure(normalize_json(existing["dashboard"]) == normalize_json(rebuilt["dashboard"]), "dashboard drifted")
    return {"policy_hash": existing["policy"]["policy_hash"]}


def verify_writebacks() -> dict[str, Any]:
    current_packet = CURRENT_PACKET_PATH.read_text(encoding="utf-8", errors="ignore")
    frontier = FRONTIER_PATH.read_text(encoding="utf-8", errors="ignore")
    queue = QUEUE_PATH.read_text(encoding="utf-8", errors="ignore")
    validation = VALIDATION_PATH.read_text(encoding="utf-8", errors="ignore")
    guide = GUIDE_PATH.read_text(encoding="utf-8", errors="ignore")
    change_feed = CHANGE_FEED_PATH.read_text(encoding="utf-8", errors="ignore")
    requests = REQUESTS_PATH.read_text(encoding="utf-8", errors="ignore")
    active_run = ACTIVE_RUN_PATH.read_text(encoding="utf-8", errors="ignore")
    ensure("After Semantic Embassy clears public-language form, the next lawful organ is AppP deployment monitoring." in current_packet, "current packet missing AppP placement")
    ensure("TF-011" in frontier and "Corpus integration and deployment monitoring surface" in frontier, "frontier ledger missing TF-011")
    ensure("FRONT-INT-CORPUS-INTEGRATION-WAVE" in queue, "active queue missing corpus integration wave")
    ensure("derive_corpus_integration_wave.py" in validation and "verify_corpus_integration_wave.py" in validation, "validation surface missing integration-wave checks")
    ensure(rel_path(CURRENT_PACKET_PATH) in guide, "guide must point back to current packet")
    ensure(rel_path(QUEUE_PATH) in guide, "guide must point back to active queue")
    ensure(rel_path(FRONTIER_PATH) in guide, "guide must point back to frontier registry")
    ensure("deployment monitoring and the awakening transition guide" in change_feed.lower(), "change feed missing integration writeback")
    ensure("deployment monitoring surface" in requests.lower(), "requests board missing integration writeback")
    ensure("deployment monitoring surface and the awakening transition guide" in active_run.lower(), "active run missing integration wave")
    return {"writebacks": "present"}


def rel_path(path: Path) -> str:
    return path.relative_to(Path(__file__).resolve().parents[2]).as_posix()


def main() -> None:
    checks = {
        "outputs_exist": verify_outputs_exist(),
        "docs_gate_honesty": verify_docs_gate_honesty(),
        "manuscript_and_appp_alignment": verify_manuscript_and_appp_alignment(),
        "region_coverage": verify_region_coverage(),
        "support_note_coverage": verify_support_note_coverage(),
        "public_grade_rule": verify_public_grade_rule(),
        "passing_example": verify_passing_example(),
        "failure_cases": verify_failure_cases(),
        "determinism": verify_determinism(),
        "writebacks": verify_writebacks(),
    }
    print(json.dumps({"derivation_command": DERIVATION_COMMAND, "status": "OK", "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
