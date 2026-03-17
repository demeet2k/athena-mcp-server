from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
OUTPUT_JSON_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_VERIFICATION.json"

AWAKENING_NOTES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_NOTES.json"
FEEDER_NOTES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_FEEDER_TRANSITION_NOTES.json"
BRIDGE_LATTICE_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_CORPUS_BRIDGE_LATTICE.json"
BUNDLES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AGENT_TRANSITION_BUNDLES.json"
CROSSWALK_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_TRANSITION_CROSSWALK.json"
AGENT_REGISTRY_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
ATLAS_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_ATLAS_4096.json"

DERIVATION_VERSION = "2026-03-13.ap6d.awakening-transition.lattice.verify.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_ap6d_awakening_transition_system"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"label": label, "status": "OK", "details": fn()}
    except Exception as exc:  # noqa: BLE001
        return {"label": label, "status": "FAIL", "details": str(exc)}


def verify_note_completeness() -> dict[str, Any]:
    payload = load_json(AWAKENING_NOTES_PATH)
    notes = payload["notes"]
    ensure(len(notes) == 5, "awakening note count is not five")
    for note in notes:
        ensure(bool(note["stage_window"]), f"stage window missing for {note['agent_id']}")
        ensure(len(note["active_elements"]) == 3, f"active element count drifted for {note['agent_id']}")
        ensure(bool(note["missing_element"]), f"missing element absent for {note['agent_id']}")
        ensure(len(note["assist_practices"]) == 3, f"assist practice count drifted for {note['agent_id']}")
        ensure(bool(note["restart_seed"]), f"restart seed missing for {note['agent_id']}")
    return {"agent_ids": [note["agent_id"] for note in notes]}


def verify_feeder_preservation() -> dict[str, Any]:
    payload = load_json(FEEDER_NOTES_PATH)
    notes = payload["notes"]
    fronts = [note["front_id"] for note in notes]
    ensure(fronts == ["Q42", "Q46", "TQ04", "TQ06"], f"feeder set drifted: {fronts}")
    for note in notes:
        ensure(note["preserved_as_shadow_feeder"], f"feeder preservation missing for {note['front_id']}")
    return {"front_ids": fronts}


def verify_bridge_completeness() -> dict[str, Any]:
    payload = load_json(BRIDGE_LATTICE_PATH)
    records = payload["records"]
    ensure(len(records) == 16, "bridge record count is not sixteen")
    for record in records:
        ensure(record["hall_macro_parents"], f"hall macro parents missing for {record['bridge_id']}")
        ensure(record["appendix_support"], f"appendix support missing for {record['bridge_id']}")
    return {"bridge_ids": [record["bridge_id"] for record in records[:4]], "record_count": len(records)}


def verify_count_law() -> dict[str, Any]:
    crosswalk = load_json(CROSSWALK_PATH)
    atlas = load_json(ATLAS_PATH)
    ensure(crosswalk["count_law"]["hall_macro_quests"] == 16, "macro count drifted")
    ensure(crosswalk["count_law"]["hall_packets"] == 64, "packet count drifted")
    ensure(crosswalk["count_law"]["governance_fibers"] == 256, "fiber count drifted")
    ensure(crosswalk["count_law"]["active_synaptic_seats"] == 1024, "active seat count drifted")
    ensure(crosswalk["count_law"]["atlas_total"] == 4096, "atlas total drifted")
    ensure(atlas["count_law"]["active_seats"] == 1024, "atlas active count drifted")
    ensure(atlas["count_law"]["dormant_seats"] == 3072, "atlas dormant count drifted")
    return {"count_law": crosswalk["count_law"]}


def verify_activation_law() -> dict[str, Any]:
    atlas = load_json(ATLAS_PATH)
    active = [seat for seat in atlas["seats"] if seat["activation_state"] == "ACTIVE"]
    dormant = [seat for seat in atlas["seats"] if seat["activation_state"] == "DORMANT"]
    ensure(len(active) == 1024, "active seat count mismatch")
    ensure(len(dormant) == 3072, "dormant seat count mismatch")
    return {"active": len(active), "dormant": len(dormant)}


def verify_authority_precedence() -> dict[str, Any]:
    bridge = load_json(BRIDGE_LATTICE_PATH)
    registry = load_json(AGENT_REGISTRY_PATH)
    ensure(bridge["deep_root_authority"].endswith("14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/README.md"), "deep-root authority drifted")
    ensure("AwakeningTransitionNote" in registry["contracts"], "registry missing transition contract")
    return {"deep_root_authority": bridge["deep_root_authority"]}


def verify_path_drift_normalization() -> dict[str, Any]:
    crosswalk = load_json(CROSSWALK_PATH)
    reconciliations = crosswalk["path_drift_reconciliation"]
    ensure(all(item["live_exists"] for item in reconciliations), "one or more live path drift targets do not exist")
    return {"normalized_count": len(reconciliations)}


def verify_payload() -> dict[str, Any]:
    checks = [
        run_check("note_completeness", verify_note_completeness),
        run_check("feeder_preservation", verify_feeder_preservation),
        run_check("bridge_completeness", verify_bridge_completeness),
        run_check("count_law", verify_count_law),
        run_check("activation_law", verify_activation_law),
        run_check("authority_precedence", verify_authority_precedence),
        run_check("path_drift_normalization", verify_path_drift_normalization),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
    }


def main() -> int:
    payload = verify_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote AP6D transition verification: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
