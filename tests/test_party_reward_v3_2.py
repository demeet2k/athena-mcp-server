from __future__ import annotations

import math
import unittest
from unittest.mock import patch

from athena_mcp.aor_collective_transport_surface import AorCollectiveTransportSurface
from athena_mcp.party_coordination_v3_1 import PartyCoordinationRuntimeV31
from athena_mcp.party_coordination_v3_2 import (
    PARTY_REWARD_NUMERIC_VERSION,
    PartyCoordinationRuntimeV32,
    _finite_nonnegative_xp,
)


class PartyRewardV32NumericTests(unittest.TestCase):
    def test_v32_is_strict_subclass_of_v31(self):
        self.assertTrue(issubclass(PartyCoordinationRuntimeV32, PartyCoordinationRuntimeV31))
        self.assertEqual(PARTY_REWARD_NUMERIC_VERSION, "PARTY.REWARD.PROVENANCE.3.2")

    def test_finite_positive_and_zero_are_normalized(self):
        self.assertEqual(_finite_nonnegative_xp(12), 12.0)
        self.assertEqual(_finite_nonnegative_xp(12.5), 12.5)
        self.assertEqual(_finite_nonnegative_xp(0), 0.0)
        self.assertTrue(math.isfinite(_finite_nonnegative_xp(12.5)))

    def test_finite_numeric_string_compatibility_is_preserved(self):
        self.assertEqual(_finite_nonnegative_xp("12.5"), 12.5)
        self.assertEqual(_finite_nonnegative_xp("0"), 0.0)

    def test_negative_finite_rejects(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            _finite_nonnegative_xp(-0.01)

    def test_nan_and_infinities_reject(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite"):
                    _finite_nonnegative_xp(value)

    def test_boolean_rejects_before_numeric_coercion(self):
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "non-boolean"):
                    _finite_nonnegative_xp(value)

    def test_non_numeric_rejects(self):
        for value in (None, "not-a-number", object()):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "numeric"):
                    _finite_nonnegative_xp(value)

    def test_invalid_value_never_enters_v31_observe(self):
        runtime = object.__new__(PartyCoordinationRuntimeV32)
        with patch.object(PartyCoordinationRuntimeV31, "observe", autospec=True) as parent:
            for value in (float("nan"), float("inf"), float("-inf"), True, False):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        runtime.observe(
                            "OBS.TEST",
                            "PARTY.TEST",
                            "meta",
                            value,
                            [],
                            "witness://obs",
                            "xp://source",
                            "xp-witness://source",
                        )
            parent.assert_not_called()

    def test_finite_value_delegates_as_normalized_float(self):
        runtime = object.__new__(PartyCoordinationRuntimeV32)
        expected = {"status": "DELEGATED"}
        with patch.object(PartyCoordinationRuntimeV31, "observe", autospec=True, return_value=expected) as parent:
            result = runtime.observe(
                "OBS.TEST",
                "PARTY.TEST",
                "meta",
                "42.5",
                [],
                "witness://obs",
                "xp://source",
                "xp-witness://source",
            )
        self.assertEqual(result, expected)
        args = parent.call_args.args
        self.assertIs(args[0], runtime)
        self.assertEqual(args[4], 42.5)
        self.assertIsInstance(args[4], float)
        self.assertTrue(math.isfinite(args[4]))

    def test_public_aor_constructor_selects_v32_runtime(self):
        self.assertIn("PartyCoordinationRuntimeV32", AorCollectiveTransportSurface.__init__.__code__.co_names)
        self.assertNotIn("PartyCoordinationRuntimeV31", AorCollectiveTransportSurface.__init__.__code__.co_names)

    def test_finite_preflight_does_not_claim_upstream_verification(self):
        # The helper validates representation only; it returns a bare finite float,
        # not an evidence/authority wrapper or receipt.
        value = _finite_nonnegative_xp("7.25")
        self.assertEqual(value, 7.25)
        self.assertIs(type(value), float)


if __name__ == "__main__":
    unittest.main()
