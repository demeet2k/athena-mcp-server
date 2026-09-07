import json
import os
import unittest
from fractions import Fraction

from athena_mcp import closure_grammar as cg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "spec", "CLOSURE_GRAMMAR_REGISTRY_V1.json")


class ClosureArithmetic(unittest.TestCase):
    def test_self_test_passes(self):
        out = cg.self_test()
        self.assertEqual(out["mckay"], {"E6": 24, "E7": 48, "E8": 120})

    def test_closing_triples_and_carrier(self):
        trip = cg.closing_triples()
        self.assertEqual(len(trip), 6)
        self.assertEqual(max(max(t) for t in trip), 6)
        self.assertEqual(cg.lcm_range(1, 6), 60)
        self.assertEqual(cg.lcm_range(1, 10, exclude=(7,)), 360)
        self.assertEqual(cg.lcm_range(1, 10), 2520)
        self.assertEqual(cg.triple_excess(2, 3, 7), Fraction(-1, 42))

    def test_sixtieths(self):
        self.assertEqual([int(cg.in_sixtieths(*t)) for t in [(2, 3, 3), (2, 3, 4), (2, 3, 5)]], [70, 65, 62])
        self.assertTrue(all(cg.in_sixtieths(*t) == 60 for t in [(2, 3, 6), (2, 4, 4), (3, 3, 3)]))
        self.assertFalse(cg.in_sixtieths(2, 3, 7).denominator == 1)

    def test_regular_numbers(self):
        self.assertEqual(cg.first_non_smooth(), 7)
        self.assertTrue(cg.reciprocal_terminates(15, 60))
        self.assertFalse(cg.reciprocal_terminates(7, 60))
        self.assertFalse(cg.reciprocal_terminates(7, 10))
        self.assertFalse(cg.reciprocal_terminates(7, 20))
        self.assertFalse(cg.is_regular(14))
        self.assertTrue(all(cg.is_regular(x) for x in (60, 50, 40, 30, 20, 15, 10)))

    def test_shcn_ladder(self):
        self.assertEqual(cg.superior_highly_composite(6000), [2, 6, 12, 60, 120, 360, 2520, 5040])
        hc = cg.highly_composite(2000)
        self.assertEqual(min(x for x in hc if x % 7 == 0), 840)
        self.assertEqual(cg.tau(5040), 60)

    def test_divisor_charts_of_360(self):
        pairs = cg.divisor_pairs(360)
        self.assertEqual(len(pairs), 12)
        self.assertEqual(cg.most_square_pair(360), (18, 20))
        self.assertIn((9, 40), pairs)

    def test_egyptian_fractions(self):
        self.assertEqual(cg.unit_fraction_partitions_of_one(3), [(2, 3, 6), (2, 4, 4), (3, 3, 3)])
        self.assertEqual(cg.sylvester_sequence(4), [2, 3, 7, 43])
        self.assertEqual(cg.greedy_egyptian(Fraction(1)), [1])
        self.assertEqual(cg.greedy_egyptian(Fraction(41, 42)), [2, 3, 7])

    def test_pantheon_partitions(self):
        gods = {"An": 60, "Enlil": 50, "Enki": 40, "Nanna": 30, "Utu": 20, "Ishtar": 15, "Adad": 10, "Nergal": 14}
        hits = cg.subset_sums(gods, 60, 2, 4)
        self.assertIn(("Nanna", "Utu", "Adad"), hits)
        self.assertIn(("Enlil", "Adad"), hits)
        self.assertIn(("Enki", "Utu"), hits)
        self.assertTrue(all(cg.is_regular(v) for k, v in gods.items() if k != "Nergal"))
        self.assertFalse(cg.is_regular(gods["Nergal"]))

    def test_oracle_symmetry(self):
        hexa = cg.v4_census(6)
        self.assertEqual((hexa["reversal_classes"], hexa["v4_orbits"]), (36, 20))
        odu = cg.v4_census(4)
        self.assertEqual(odu["v4_orbits"], 6)
        self.assertEqual(cg.v4_orbit_sizes(4), {2: 4, 4: 2})
        self.assertEqual(cg.yarrow_line_probabilities(), {6: Fraction(1, 16), 7: Fraction(5, 16), 8: Fraction(7, 16), 9: Fraction(3, 16)})

    def test_geomantic_judge_parity(self):
        out = cg.geomantic_judge_theorem()
        self.assertTrue(out["holds"])
        self.assertEqual(out["possible_judges"], 8)

    def test_triangular_and_tori(self):
        self.assertEqual(cg.triangular(36), 666)
        self.assertEqual(cg.triangular(17), 153)
        self.assertEqual(cg.triangular(12), 78)
        self.assertEqual(cg.is_triangular(28), 7)
        self.assertEqual(cg.torus(13, 20)["orbit"], 260)
        self.assertEqual(cg.torus(10, 12), {"orbit": 60, "orbits": 2, "points": 120})
        self.assertEqual(cg.torus(260, 365)["orbit"], 18980)

    def test_fifth_closures(self):
        self.assertEqual([k for k, _ in cg.best_fifth_closures(60)], [1, 2, 5, 12, 41, 53])

    def test_calendar_constants(self):
        self.assertEqual(cg.metonic_intercalation()["intercalary"], 7)
        self.assertAlmostEqual(cg.lunar_quarter(), 7.38, places=1)


class Registry(unittest.TestCase):
    def setUp(self):
        with open(REGISTRY, encoding="utf-8") as fh:
            self.reg = json.load(fh)

    def test_every_crossing_is_n_plus_one_or_typed_exception(self):
        for t in self.reg["traditions"]:
            for c in t.get("crossings", []):
                if c.get("seat") in ("extra", "return", "centre", "withdrawn"):
                    self.assertEqual(c["cross"], c["n"] + 1, f"{t['id']}: {c}")
                elif c.get("seat") in ("residue", "extension"):
                    self.assertGreater(c["cross"], c["n"], f"{t['id']}: {c}")
                self.assertIn(c["grade"], ("🟢", "🟡", "🟠"), f"{t['id']}: {c}")

    def test_numbers_factor_as_stated(self):
        for t in self.reg["traditions"]:
            for num in t.get("numbers", []):
                if "factors" in num:
                    self.assertEqual(cg.factor_string(num["n"]), num["factors"], f"{t['id']}: {num}")

    def test_registry_json_in_sync_with_module(self):
        from scripts.closure_grammar_report import check_json

        self.assertTrue(check_json(), "run `python -m scripts.closure_grammar_report` to re-export the registry")

    def test_gate_convention(self):
        # n == 0 marks an unquantified crossing: the gate before any count (extra), a whole-cycle
        # return with no specific count (return), a single withheld unit (withdrawn), or a lost unit (residue).
        for t in self.reg["traditions"]:
            for c in t.get("crossings", []):
                if c["n"] == 0:
                    self.assertIn(c["seat"], ("extra", "return", "withdrawn", "residue"), f"{t['id']}: {c}")

    def test_registry_report_runs(self):
        from scripts.closure_grammar_report import build_report

        rep = build_report(self.reg)
        self.assertGreaterEqual(rep["tradition_count"], 40)
        self.assertIn("seat_counts", rep)


if __name__ == "__main__":
    unittest.main()
