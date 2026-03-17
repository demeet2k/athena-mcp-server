from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.hemisphere_dense_65_shell_support import (  # noqa: E402
    DENSE_65_CANONICAL_SEED_TABLE,
    DENSE_65_ROUTE_KEYS,
)


PROTOCOL_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "18_LP_57OMEGA_PROTOCOL"
)
TRANSFER_REGISTRY_PATH = PROTOCOL_ROOT / "14_rqt_transfer_signature_registry.json"
TRANSFER_WITNESS_PATH = PROTOCOL_ROOT / "15_rqt_transfer_signature_and_metro_witness.md"
POINTER_REGISTRY_PATH = PROTOCOL_ROOT / "16_aether_witness_replay_pointer_registry.json"

VERIFICATION_JSON_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.json"
)
VERIFICATION_MD_PATH = (
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.md"
)

AE_PATTERN = re.compile(
    r"^AE=\((?P<lens>[^,]+),(?P<phase>[^,]+),(?P<bundle>B\d{2})(:h=(?P<hidden>[^;]+))?;(?P<slot>[^)]+)\)$"
)
WITNESS_PTR_FIELDS = {"Type", "Location", "Hash", "Scope", "Timestamp", "Collector", "VersionPins"}
REPLAY_PTR_FIELDS = {"Inputs", "Steps", "ExpectedOutputs", "Checks", "EnvPin", "Hash"}
REPLAY_CHECKS = {"Sigma", "Hub<=6", "ZMatch"}
REPRESENTATIVE_EXPECTATIONS = {
    "R01": [("plus", "AE=(Flower,R+,B01;Core)"), ("minus", "AE=(Flower,R-,B01;Core)")],
    "Q03": [("q4", "AE=(Flower,Q4,B03;Core)")],
    "T11": [("t3", "AE=(Flower,T3,B11:h=B;Residual)")],
    "T33": [("t3", "AE=(Flower,T3,B33:h=A;Residual)")],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_ae(location: str) -> dict[str, str | None]:
    match = AE_PATTERN.match(location)
    if not match:
        raise ValueError(f"Invalid AE location: {location}")
    return match.groupdict()


def append_check(results: list[dict[str, Any]], name: str, result: bool, detail: str | None = None) -> None:
    entry: dict[str, Any] = {"name": name, "result": result}
    if detail:
        entry["detail"] = detail
    results.append(entry)


def verify_registry() -> dict[str, Any]:
    transfer_registry = load_json(TRANSFER_REGISTRY_PATH)
    pointer_registry = load_json(POINTER_REGISTRY_PATH)
    transfer_witness = TRANSFER_WITNESS_PATH.read_text(encoding="utf-8")

    checks: list[dict[str, Any]] = []

    append_check(
        checks,
        "transfer_record_count",
        transfer_registry.get("enriched_transfer_record_count") == 45 and len(transfer_registry.get("records", [])) == 45,
        f"count={len(transfer_registry.get('records', []))}",
    )
    append_check(
        checks,
        "phase_binding_count",
        transfer_registry.get("phase_binding_count") == 60,
        f"count={transfer_registry.get('phase_binding_count')}",
    )
    append_check(
        checks,
        "pointer_registry_counts",
        pointer_registry.get("record_count") == 45 and pointer_registry.get("concrete_pointer_count") == 60,
        f"records={pointer_registry.get('record_count')} pointers={pointer_registry.get('concrete_pointer_count')}",
    )
    append_check(
        checks,
        "markdown_explicit_payloads",
        "AE[" not in transfer_witness and "WitnessPtr" in transfer_witness and "ReplayPtr" in transfer_witness,
        "Markdown should render explicit AE / WitnessPtr / ReplayPtr payloads.",
    )

    pointer_records = {record["record_id"]: record for record in pointer_registry["records"]}
    total_phase_bindings = 0

    for record in transfer_registry["records"]:
        record_id = record["record_id"]
        spec = DENSE_65_CANONICAL_SEED_TABLE[record_id]
        bindings = record["orientation_bindings"]
        total_phase_bindings += len(bindings)

        append_check(
            checks,
            f"{record_id}_summary_fields",
            all(
                key in record
                for key in ("z_transfer_signature", "aether_transfer_signature", "prior_metro_route_witness")
            ),
        )
        append_check(
            checks,
            f"{record_id}_route_binding",
            record["route_key"] == spec["route_key"]
            and record["check_key"] == spec["check_key"]
            and record["z_binding"] == spec["z_binding"],
            f"route={record['route_key']} check={record['check_key']} z={record['z_binding']}",
        )

        expected_binding_count = 2 if record["record_type"] == "R" else 1
        append_check(
            checks,
            f"{record_id}_binding_count",
            len(bindings) == expected_binding_count and record["phase_binding_count"] == expected_binding_count,
            f"bindings={len(bindings)}",
        )

        if record["record_type"] == "R":
            expected_binding_keys = {"plus", "minus"}
        elif record["record_type"] == "Q":
            expected_binding_keys = {"q4"}
        else:
            expected_binding_keys = {"t3"}
        append_check(
            checks,
            f"{record_id}_binding_keys",
            {binding["binding_key"] for binding in bindings} == expected_binding_keys,
            ",".join(binding["binding_key"] for binding in bindings),
        )

        for binding in bindings:
            ae_parts = parse_ae(binding["Location"])
            expected_slot = "Residual" if record["record_type"] == "T" else "Core"
            expected_hidden = spec["hidden_pole"] if record["record_type"] == "T" else None
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_ae_round_trip",
                binding["AE"]["Lens"] == "Flower"
                and ae_parts["lens"] == "Flower"
                and binding["AE"]["Phase"] == ae_parts["phase"]
                and binding["AE"]["Bundle"] == ae_parts["bundle"]
                and binding["AE"]["Slot"] == ae_parts["slot"],
                binding["Location"],
            )
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_slot_law",
                binding["slot"] == expected_slot
                and binding["AE"]["Slot"] == expected_slot
                and ae_parts["slot"] == expected_slot,
            )
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_hidden_pole",
                (
                    expected_hidden is None
                    and binding.get("hidden_pole") is None
                    and "HiddenPole" not in binding["AE"]
                    and ae_parts["hidden"] is None
                )
                or (
                    expected_hidden is not None
                    and binding.get("hidden_pole") == expected_hidden
                    and binding["AE"].get("HiddenPole") == expected_hidden
                    and ae_parts["hidden"] == expected_hidden
                ),
                str(binding.get("hidden_pole")),
            )
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_ptr_fields",
                WITNESS_PTR_FIELDS.issubset(binding["WitnessPtr"].keys())
                and REPLAY_PTR_FIELDS.issubset(binding["ReplayPtr"].keys()),
            )
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_replay_checks",
                REPLAY_CHECKS.issubset(set(binding["ReplayPtr"]["Checks"])),
                ",".join(binding["ReplayPtr"]["Checks"]),
            )
            append_check(
                checks,
                f"{record_id}_{binding['binding_key']}_route_payload",
                binding["route_id"] == spec["route_key"]
                and binding["route_path"] == DENSE_65_ROUTE_KEYS[spec["route_key"]]
                and binding["checkpoint"] == spec["check_key"]
                and binding["z"] == spec["z_binding"],
            )

        pointer_record = pointer_records.get(record_id)
        append_check(
            checks,
            f"{record_id}_pointer_registry_match",
            pointer_record is not None and len(pointer_record["pointers"]) == len(bindings),
        )

    append_check(
        checks,
        "phase_binding_total_recomputed",
        total_phase_bindings == 60,
        f"total={total_phase_bindings}",
    )

    for record_id, expectation in REPRESENTATIVE_EXPECTATIONS.items():
        record = next(item for item in transfer_registry["records"] if item["record_id"] == record_id)
        actual = [(binding["binding_key"], binding["Location"]) for binding in record["orientation_bindings"]]
        append_check(checks, f"{record_id}_representative", actual == expectation, f"actual={actual}")

    truth = "OK" if all(check["result"] for check in checks) else "FAIL"
    return {
        "generated_at": date.today().isoformat(),
        "protocol_id": "LP-57OMEGA",
        "truth": truth,
        "checks": checks,
    }


def write_reports(report: dict[str, Any]) -> None:
    VERIFICATION_JSON_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# LP-57OMEGA Prime Loop Verification",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Truth: `{report['truth']}`",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        status = "PASS" if check["result"] else "FAIL"
        line = f"- `{status}` `{check['name']}`"
        if check.get("detail"):
            line += f" :: {check['detail']}"
        lines.append(line)
    lines.append("")
    VERIFICATION_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = verify_registry()
    write_reports(report)
    print(json.dumps({"truth": report["truth"], "check_count": len(report["checks"])}, indent=2))
    return 0 if report["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
