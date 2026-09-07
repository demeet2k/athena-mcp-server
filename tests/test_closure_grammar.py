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


class Trichotomy(unittest.TestCase):
    def test_e_chain_determinants(self):
        chain = cg.e_chain_trichotomy()
        self.assertEqual([chain[f"E{n}"]["det"] for n in range(6, 11)], [3, 2, 1, 0, -1])
        self.assertEqual([chain[f"E{n}"]["regime"] for n in (8, 9, 10)], ["finite", "affine", "indefinite"])
        self.assertLess(chain["E8"]["lambda_max"], 2.0)
        self.assertAlmostEqual(chain["E9"]["lambda_max"], 2.0, places=6)
        self.assertGreater(chain["E10"]["lambda_max"], 2.0)

    def test_affine_cycle_is_the_extra_node(self):
        # A_n is a chain of n nodes; its affine extension is the (n+1)-cycle and is exactly null
        for n in (2, 3, 5, 6, 11):
            self.assertGreater(cg.determinant(cg.dynkin_a(n)), 0)
            self.assertEqual(cg.determinant(cg.affine_a(n)), 0)
            self.assertEqual(len(cg.affine_a(n)), n + 1)

    def test_lambda_max_values_are_2cos(self):
        import math
        chain = cg.e_chain_trichotomy()
        for n, h in ((6, 12), (7, 18), (8, 30)):  # Coxeter numbers
            self.assertAlmostEqual(chain[f"E{n}"]["lambda_max"], 2 * math.cos(math.pi / h), places=5)


class Schema(unittest.TestCase):
    def test_registry_validates(self):
        from athena_mcp.closure_grammar_schema import validate_registry
        from scripts.closure_grammar_report import registry_dict

        self.assertEqual(validate_registry(registry_dict()), [])

    def test_validator_catches_untraceable_green_and_unmarked(self):
        from athena_mcp.closure_grammar_schema import validate_registry

        bad = {"version": "CLOSURE_GRAMMAR_REGISTRY_V1", "traditions": [{
            "id": "bad_one", "name": "x", "family": "x", "region": "x", "standing": "MODERN_RECONSTRUCTION",
            "sources": ["corpus: FILE"], "closures": [], "residues": [], "devices": {"record": [], "hull": []}, "ladder": [],
            "arithmetic": {"present": False, "what": ""}, "numbers": [{"n": 7, "role": "passage", "what": "x"}], "negatives": [], "notes": "",
            "crossings": [
                {"n": 6, "cross": 7, "seat": "extra", "what": "no locus", "grade": "🟢", "marked": True},
                {"n": 6, "cross": 8, "seat": "extra", "what": "wrong step", "grade": "🟡", "marked": True},
                {"n": 6, "cross": 7, "seat": "extra", "what": "unmarked", "grade": "🟡", "marked": False},
            ]}]}
        errs = validate_registry(bad)
        self.assertTrue(any("without traceable source" in e for e in errs))
        self.assertTrue(any("cross == n+1" in e for e in errs))
        self.assertTrue(any("unmarked adjacency" in e for e in errs))


class Census(unittest.TestCase):
    def test_null_model_is_deterministic_and_seven_separates(self):
        from athena_mcp.closure_grammar_report_core import build_report
        from scripts.closure_grammar_report import registry_dict

        a = build_report(registry_dict())["census"]
        b = build_report(registry_dict())["census"]
        self.assertEqual(a["null_model"], b["null_model"])
        self.assertGreater(a["ratio7_passage_over_order"], 1.0)
        self.assertLess(a["null_model"]["p7"]["p_value_one_sided"], 0.05)
        # the controls: 13 must not separate the roles
        self.assertGreater(a["null_model"]["p13"]["p_value_one_sided"], 0.05)

    def test_wilson(self):
        from athena_mcp.closure_grammar_report_core import wilson

        lo, hi = wilson(40, 141)
        self.assertLess(lo, 40 / 141)
        self.assertGreater(hi, 40 / 141)
        self.assertIsNone(wilson(0, 0))


class Resources(unittest.TestCase):
    def setUp(self):
        import tempfile

        from athena_mcp.server import Server

        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.seq += 1
        m = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            m["params"] = params
        return self.server.handle(m)

    def test_closure_grammar_resources_are_listed_and_readable(self):
        uris = {r["uri"] for r in self.rpc("resources/list")["result"]["resources"]}
        self.assertIn("athena://closure-grammar/registry", uris)
        self.assertIn("athena://closure-grammar/census", uris)
        reg = json.loads(self.rpc("resources/read", {"uri": "athena://closure-grammar/registry"})["result"]["contents"][0]["text"])
        self.assertEqual(reg["version"], "CLOSURE_GRAMMAR_REGISTRY_V1")
        self.assertGreaterEqual(len(reg["traditions"]), 80)
        self.assertIn("COMPATIBILITY != NECESSITY", reg["law_firewall"])
        cen = json.loads(self.rpc("resources/read", {"uri": "athena://closure-grammar/census"})["result"]["contents"][0]["text"])
        self.assertIn("null_model", cen["census"])
        self.assertNotIn("per_tradition_census", cen)
