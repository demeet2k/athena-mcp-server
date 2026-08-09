import unittest

from athena_mcp.ic10_runtime import IC10Compiler


class IC10InvariantEmptySemanticsTests(unittest.TestCase):
    def test_empty_violations_is_present_and_valid(self):
        witness = {
            "observed": True,
            "status": "PASS",
            "ref": "INV.EMPTY.VALID",
            "declared_invariants": ["IDENTITY", "TYPE"],
            "violations": [],
        }
        normalized = IC10Compiler._observed_witness(
            witness,
            required=("declared_invariants",),
        )
        defects = list(normalized["defects"])
        if "violations" not in normalized["packet"]:
            defects.append("missing_violations")
        violations = list(normalized["packet"].get("violations") or [])
        if violations:
            defects.append("invariant_violation")
        self.assertEqual(defects, [])

    def test_missing_violations_fails_closed(self):
        witness = {
            "observed": True,
            "status": "PASS",
            "ref": "INV.MISSING.INVALID",
            "declared_invariants": ["IDENTITY", "TYPE"],
        }
        normalized = IC10Compiler._observed_witness(
            witness,
            required=("declared_invariants",),
        )
        defects = list(normalized["defects"])
        if "violations" not in normalized["packet"]:
            defects.append("missing_violations")
        self.assertIn("missing_violations", defects)


if __name__ == "__main__":
    unittest.main()
