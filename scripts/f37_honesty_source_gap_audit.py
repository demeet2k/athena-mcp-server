from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F37_HONESTY_SOURCE_ADMISSION_V1.json"
F37_MANIFEST_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
ADMISSIONS_PATH = ROOT / "spec" / "F37_PRIMARY_SOURCE_ADMISSIONS_V1.json"
OUTPUT = Path("f37_honesty_source_gap_audit_v1.json")

REQUIRED_RECORD_FIELDS = {
    "source_id", "source_class", "locator", "revision", "claim_scope",
    "theorem_or_construction_locus", "independence_group",
    "supports_obligation", "project_mapping", "authority_ceiling",
}


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def valid_record(record: dict) -> tuple[bool, list[str]]:
    defects=[]
    for field in sorted(REQUIRED_RECORD_FIELDS):
        value=record.get(field)
        if value is None or value == "" or value == [] or value == {}:
            defects.append(f"missing_{field}")
    source_class=str(record.get("source_class") or "")
    if source_class not in {"PRIMARY_PAPER","PRIMARY_MONOGRAPH","FORMAL_ARTIFACT","EXTERNAL_OBSERVATION"}:
        defects.append("invalid_source_class")
    return not defects, defects


def main() -> int:
    contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37=json.loads(F37_MANIFEST_PATH.read_text(encoding="utf-8"))
    admissions={"records":[]}
    if ADMISSIONS_PATH.exists():
        admissions=json.loads(ADMISSIONS_PATH.read_text(encoding="utf-8"))
    records=list(admissions.get("records") or [])

    record_audit=[]
    valid_records=[]
    for record in records:
        valid, defects=valid_record(record)
        item={"record":record,"valid":valid,"defects":defects}
        record_audit.append(item)
        if valid:
            valid_records.append(record)

    cells={}
    all_parent_holds=True
    for gid_text, cell in contract["cells"].items():
        gid=int(gid_text)
        expected=cell["current_hold"]
        parent=f37["known_hold_by_gid"].get(str(gid))
        all_parent_holds = all_parent_holds and parent == expected
        required=list(cell["required_source_witnesses"])
        matches={slot:[] for slot in required}
        for record in valid_records:
            if str(record.get("gid")) not in {str(gid), ""} and record.get("gid") is not None:
                continue
            slot=str(record.get("supports_obligation") or "")
            if slot in matches:
                matches[slot].append(record)
        filled=sorted(slot for slot, rows in matches.items() if rows)
        missing=sorted(slot for slot in required if not matches[slot])
        cells[str(gid)]={
            "carrier":cell["carrier"],
            "parent_hold_expected":expected,
            "parent_hold_observed":parent,
            "required_slots":required,
            "filled_slots":filled,
            "missing_slots":missing,
            "admitted_records":matches,
            "source_admission_status":"SOURCE_ADMISSION_COMPLETE" if not missing else "SOURCE_ADMISSION_HOLD",
            "hold_discharge_allowed":not missing,
        }

    # Generic mechanism witnesses are deliberately not source records unless a
    # separately admitted source-record entry explicitly binds them to a primary source slot.
    generic_files=[
        "spec/F30_GRADED_MEMORY_WITNESS_V1.json",
        "spec/F34_MOTIVIC_ENVELOPE_WITNESS_V1.json",
        "spec/F35_HIGHER_COHERENCE_WITNESS_V1.json",
        "spec/F35_PROJECT_MAPPING_WITNESS_V1.json",
        "spec/F36_DERIVED_REPLAY_WITNESS_V1.json",
    ]
    generic_present=[path for path in generic_files if (ROOT/path).exists()]
    generic_not_counted=all(
        not any(str(row.get("locator") or "").endswith(path) for row in valid_records)
        for path in generic_present
    )

    checks={
        "all_four_parent_holds_match":all_parent_holds,
        "record_schema_valid_for_admitted_records":all(item["valid"] for item in record_audit),
        "generic_fixture_files_do_not_auto_fill_primary_source_slots":generic_not_counted,
        "all_cells_have_typed_source_admission_state":len(cells)==4 and all(row["source_admission_status"] in {"SOURCE_ADMISSION_COMPLETE","SOURCE_ADMISSION_HOLD"} for row in cells.values()),
    }
    # This audit may pass while source admission remains HOLD. Its job is to
    # classify the source frontier correctly, not force it green.
    audit_ok=all(checks.values())
    complete_gids=sorted(int(gid) for gid,row in cells.items() if row["hold_discharge_allowed"])
    held_gids=sorted(int(gid) for gid,row in cells.items() if not row["hold_discharge_allowed"])
    receipt={
        "artifact":contract["artifact"],
        "status":"F37_HONESTY_SOURCE_FRONTIER_CLASSIFIED" if audit_ok else "F37_HONESTY_SOURCE_AUDIT_DEFECT",
        "checkout_head":head(),
        "primary_source_admissions_path":str(ADMISSIONS_PATH.relative_to(ROOT)) if ADMISSIONS_PATH.exists() else None,
        "primary_source_record_count":len(records),
        "valid_primary_source_record_count":len(valid_records),
        "record_audit":record_audit,
        "generic_fixture_files_present":generic_present,
        "checks":checks,
        "cells":cells,
        "source_complete_gids":complete_gids,
        "source_hold_gids":held_gids,
        "cellclosure_evidence_hold_update_allowed":complete_gids,
        "evidence_ceiling":contract["firewalls"],
    }
    OUTPUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))
    return 0 if audit_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
