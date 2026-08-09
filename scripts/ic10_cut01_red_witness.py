from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "red" / "test_ic10_gate_chain_red.py"
OUTPUT = ROOT / "ic10_cut01_red_receipt.json"
GAP_ID = "IC10G01_ORDERED_GATE_CHAIN"


def main() -> int:
    spec = importlib.util.spec_from_file_location("ic10_red", TEST)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load IC10 RED test")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.TestSuite([module.IC10GateChainRed("test_promotion2_qualifies_runtime_contract_without_full_ic10_vector")])
    result = unittest.TestResult()
    suite.run(result)
    failures = result.failures + result.errors
    detail = "\n".join(text for _, text in failures)
    intended = result.testsRun == 1 and len(failures) == 1 and GAP_ID in detail
    receipt = {
        "artifact": "ATHENA.IC10.EXECUTION.CUT01.RED.RECEIPT.V1",
        "gap_id": GAP_ID,
        "tests_run": result.testsRun,
        "failure_count": len(result.failures),
        "error_count": len(result.errors),
        "observed_intended_red": intended,
        "status": "RED_WITNESS_CONFIRMED" if intended else "RED_WITNESS_HOLD",
        "detail_tail": detail[-1600:],
        "laws": [
            "PROMOTION2_QUALIFIED != FULL_IC10_GATE_VECTOR",
            "IC10_RED != TREATMENT",
            "IC10_MUST_COMPOSE_EXISTING_PROMOTION_AUTHORITY_NOT_REPLACE_IT",
        ],
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if intended else 1


if __name__ == "__main__":
    raise SystemExit(main())
