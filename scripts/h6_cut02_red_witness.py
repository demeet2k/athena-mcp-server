from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEST_PATH = ROOT / "tests" / "red" / "test_h6_cut02_executable_red.py"
RECEIPT_PATH = ROOT / "h6_cut02_red_receipt.json"

CASES = [
    ("test_h6g01_identity_decision", "H6G01_IDENTITY_DECISION"),
    ("test_h6g02_projection_authority", "H6G02_PROJECTION_AUTHORITY"),
    ("test_h6g04_bridge_admission", "H6G04_BRIDGE_ADMISSION"),
    ("test_h6g05_evidence_graph", "H6G05_EVIDENCE_GRAPH"),
    ("test_h6g03_route_navrun_abi", "H6G03_ROUTE_NAVRUN_ABI"),
    ("test_h6g06_querybundle_root_facade", "H6G06_QUERYBUNDLE_ROOT_FACADE"),
]


def load_module():
    spec = importlib.util.spec_from_file_location("h6_cut02_red_tests", TEST_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load H6 CUT-02 RED module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()
    case_cls = module.H6Cut02ExecutableRed
    observations = []
    ok = True

    for method, gap_id in CASES:
        suite = unittest.TestSuite([case_cls(method)])
        result = unittest.TestResult()
        suite.run(result)
        failures = result.failures + result.errors
        detail = "\n".join(text for _, text in failures)
        observed_red = result.testsRun == 1 and len(failures) == 1 and gap_id in detail
        observations.append(
            {
                "method": method,
                "gap_id": gap_id,
                "tests_run": result.testsRun,
                "failure_count": len(result.failures),
                "error_count": len(result.errors),
                "observed_intended_red": observed_red,
                "detail_tail": detail[-1200:],
            }
        )
        ok = ok and observed_red

    receipt = {
        "artifact": "ATHENA.H6.EXECUTION.CUT02.RED.RECEIPT.V1",
        "runtime_parent": "429a480a80eeefb9e2bff1ea3015adf571d76b0e",
        "semantic_head": "f32eb817d48de73a0c591b0f7fb3561e4f08e7da",
        "treatment_code_present": False,
        "expected_red_count": len(CASES),
        "observed_intended_red_count": sum(1 for x in observations if x["observed_intended_red"]),
        "observations": observations,
        "status": "RED_WITNESS_CONFIRMED" if ok else "RED_WITNESS_HOLD",
        "laws": [
            "RED_WITNESS != TREATMENT",
            "PARENT_BEHAVIOR_FIRST",
            "OBSERVED_FAILURE != BENEFIT_OF_FUTURE_TREATMENT",
            "NO_GREEN_UNTIL_ALL_SIX_INTENDED_REDS_ARE_CONFIRMED",
        ],
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
