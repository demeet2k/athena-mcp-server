import unittest

from athena_mcp import kc144_topology as topo


class KC144TopologyTests(unittest.TestCase):
    def test_all_coordinate_roundtrips(self):
        self.assertEqual(len(topo.seats()), 144)
        for gid in range(1, 145):
            row, col = topo.grid_from_gid(gid)
            self.assertEqual(topo.gid_from_grid(row, col), gid)
            legacy = topo.legacy_factor(gid)
            self.assertEqual(topo.gid_from_legacy(legacy["s"], legacy["p"], legacy["q"]), gid)
            m12 = topo.m12_factor(gid)
            self.assertEqual(topo.gid_from_m12(m12["row_axis"], m12["row_phase"], m12["column_axis"], m12["column_phase"]), gid)
            self.assertEqual(topo.d4_image(topo.d4_image(gid, "R90"), "R270"), gid)
            self.assertEqual(145 - (145 - gid), gid)

    def test_exact_graph_cardinalities(self):
        for name, expected in topo.GRAPH_EXPECTED_COUNTS.items():
            self.assertEqual(len(topo.GRAPH_BUILDERS[name]()), expected, name)
        self.assertEqual(len(topo.graph("combined")["edges"]), sum(topo.GRAPH_EXPECTED_COUNTS.values()))

    def test_native_coordinates(self):
        self.assertEqual(topo.native_coordinate(7)["system"], "X16")
        self.assertEqual(topo.native_coordinate(23), {"system": "BR21", "stage": 1, "rail": "10", "index": 1})
        self.assertEqual(topo.native_coordinate(91)["mask"], "0001")
        self.assertEqual(topo.native_coordinate(106)["trits"], "000")
        self.assertEqual(topo.native_coordinate(132)["trits"], "222")
        self.assertEqual(topo.native_coordinate(144)["m12"], "T01")

    def test_routes_and_boundaries(self):
        route = topo.route(1, 144, ["physical_grid"])
        self.assertEqual(route["state"], "ROUTE_FOUND")
        self.assertEqual(route["hops"], 22)
        self.assertEqual(topo.route(23, 43, ["br21_native"])["state"], "ROUTE_FOUND")
        self.assertEqual(topo.route(1, 144, ["br21_native"])["state"], "UNREACHABLE")
        declared = topo.graph("compiler_declared")
        self.assertEqual(declared["edge_records"], 690)
        self.assertEqual(declared["edges"], [])

    def test_validation_and_digest_stability(self):
        first = topo.validate_topology()
        second = topo.validate_topology()
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        manifest = topo.manifest(include_edges=False)
        self.assertEqual(manifest["census_equation"], "6+16+21+37+10+15+27+12=144")
        self.assertFalse(manifest["readiness"]["athena_ready"])


if __name__ == "__main__":
    unittest.main()
