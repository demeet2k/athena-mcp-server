from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "spec" / "KC15_INTERPRETATION_REVIEW_V1.json").read_text(encoding="utf-8"))
OUTPUT = Path("kc15_interpretation_review_v1.json")

SAFE_STRUCTURAL_RUNTIME_PATHS = {
    "athena_mcp/inner_constitution.py": "ACTIVE_EPOCH_CONSTITUTION_DECLARATION",
    "athena_mcp/kc144.py": "KC144_BAND_RANGE_DECLARATION",
}


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def grep_kc15() -> list[dict]:
    p = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-n", "-I", "KC15", "--", "*.py", "*.json", "*.md"],
        text=True,
        capture_output=True,
    )
    if p.returncode not in (0, 1):
        raise RuntimeError(p.stderr.strip() or "git grep failed")
    rows=[]
    for line in p.stdout.splitlines():
        path, lineno, text = line.split(":",2)
        rows.append({"path":path,"line":int(lineno),"text":text})
    return rows


def structural_review(row: dict) -> dict:
    path=row["path"]
    classification=SAFE_STRUCTURAL_RUNTIME_PATHS.get(path)
    safe=False
    reason=None
    if path == "athena_mcp/inner_constitution.py":
        safe = "KC15" in row["text"] and any(token in row["text"] for token in ("KC15_MASKS", "91", "105"))
        reason = "defines active constitutional KC15 masks/block membership; does not derive truth/evidence/probability/authority"
    elif path == "athena_mcp/kc144.py":
        safe = "('KC15',91,105)" in row["text"].replace(" ", "")
        reason = "declares only KC144 band range GID091-105; no mask support semantics or decision authority"
    return {**row,"classification":classification,"safe":safe,"reason":reason}


def main() -> int:
    rows=grep_kc15()
    runtime_rows=[r for r in rows if r["path"].startswith("athena_mcp/")]
    structural_rows=[]
    unreviewed_consumers=[]
    for row in runtime_rows:
        if row["path"] in SAFE_STRUCTURAL_RUNTIME_PATHS:
            reviewed=structural_review(row)
            structural_rows.append(reviewed)
            if not reviewed["safe"]:
                unreviewed_consumers.append(reviewed)
        else:
            unreviewed_consumers.append({**row,"classification":"UNREVIEWED_EXECUTABLE_REFERENCE","safe":False})

    checks={
        "kc15_references_enumerated": bool(rows),
        "constitution_reference_present": any(r["path"] == "athena_mcp/inner_constitution.py" for r in runtime_rows),
        "band_topology_reference_present": any(r["path"] == "athena_mcp/kc144.py" for r in runtime_rows),
        "all_structural_runtime_references_reviewed_safe": bool(structural_rows) and all(r["safe"] for r in structural_rows),
        "no_unreviewed_executable_runtime_consumer": len(unreviewed_consumers) == 0,
        "execution_not_upgraded": CONTRACT["expected_runtime_state"]["execution"] == "PARTIAL",
        "evidence_stays_hold_until_ic10": CONTRACT["expected_runtime_state"]["evidence"] == "HOLD_UNTIL_IC10_ADMISSION",
        "promotion_authority_false": CONTRACT["expected_runtime_state"]["promotion_authority"] is False,
    }
    ok=all(checks.values())
    receipt={
        "artifact":CONTRACT["artifact"],
        "status":"KC15_INTERPRETATION_REVIEW_PASS" if ok else "KC15_INTERPRETATION_REVIEW_HOLD",
        "checkout_head":head(),
        "checks":checks,
        "all_kc15_references":rows,
        "runtime_references":runtime_rows,
        "safe_structural_runtime_references":structural_rows,
        "unreviewed_executable_runtime_consumers":unreviewed_consumers,
        "interpretation_standing":"NO_FORBIDDEN_RUNTIME_SEMANTIC_CAST_OBSERVED" if ok else "CONSUMER_SPECIFIC_REVIEW_REQUIRED",
        "execution":"PARTIAL",
        "evidence":"HOLD",
        "admission_authority":"HOLD",
        "promotion_authority":False,
        "next_obligation":"KC15_IC10_ADMISSION_AUTHORITY" if ok else "REVIEW_KC15_RUNTIME_CONSUMERS",
        "evidence_ceiling":[
            "SAFE_TOPOLOGY_DECLARATION != KC15_EXECUTION_QUALIFIED",
            "NO_FORBIDDEN_CAST_OBSERVED != UNIVERSAL_FUTURE_SAFETY",
            "INTERPRETATION_REVIEW != CLAIM_TRUTH",
            "INTERPRETATION_REVIEW != IC10_ADMISSION",
            "KC15_EVIDENCE_REMAINS_HOLD_UNTIL_IC10_ADMISSION",
        ],
    }
    OUTPUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k not in {"all_kc15_references","runtime_references"}},indent=2,sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
