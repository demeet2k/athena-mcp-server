import math
import unittest

from athena_mcp.kc144_polyatlas import (
    gid_decompositions,
    kc27_address,
    kc27_from_ternary,
    kc27_shell_census,
    polyatlas_route,
    resolution_transport,
    rosetta_address,
    sphere_summary,
    validate,
)


class KC144PolyatlasTests(unittest.TestCase):
    def test_kc27_roundtrip_mirror_and_shells(self):
        for chapter in range(1, 28):
            address = kc27_address(chapter)
            self.assertEqual(kc27_from_ternary(address["ternary"]), chapter)
            self.assertEqual(kc27_address(address["mirror"])["mirror"], chapter)
            self.assertEqual(len(address["hamming_neighbors"]), 6)
        self.assertEqual(kc27_address(14)["ternary"], "111")
        self.assertTrue(kc27_address(14)["fixed_point"])
        self.assertEqual(kc27_shell_census()["counts"], {"0": 1, "1": 6, "2": 12, "3": 8})

    def test_all_kc144_decompositions_roundtrip(self):
        for gid in range(1, 145):
            coordinates = gid_decompositions(gid)
            self.assertEqual(coordinates["matrix_12x12"]["inverse"], gid)
            self.assertEqual(coordinates["sphere_6x3x8"]["inverse"], gid)
            self.assertEqual(coordinates["element_4x36"]["inverse"], gid)
            self.assertEqual(145 - coordinates["mirror_gid"], gid)

    def test_rosetta_center_and_exact_host_fibre(self):
        center = rosetta_address(14, 14)
        self.assertEqual(center["coordinates"]["C06"]["six_trit"], "111111")
        self.assertEqual(center["coordinates"]["C07"]["gid729"], 365)
        self.assertEqual(center["coordinates"]["C11"]["mirror_gid729"], 365)
        self.assertTrue(all(center["roundtrip"].values()))
        for chapter in range(1, 28):
            for shelf in range(1, 28):
                receipt = rosetta_address(chapter, shelf)
                c12 = receipt["coordinates"]["C12"]
                self.assertEqual(c12["reconstructed_gid729"], receipt["coordinates"]["C07"]["gid729"])

    def test_resolution_transport_is_exact(self):
        center = resolution_transport(27, 21, 14)
        self.assertEqual(center["exact_station"], 11)
        self.assertEqual(center["centered_xi"]["fraction"], "0/1")
        self.assertTrue(all(center["invariants"].values()))
        fractional = resolution_transport(27, 33, 2)
        self.assertIsNone(fractional["exact_station"])
        self.assertEqual(sum(item["weight"]["decimal"] for item in fractional["support"]), 1.0)
        self.assertTrue(all(fractional["invariants"].values()))

    def test_sphere_closes(self):
        summary = sphere_summary(radius=2.0)
        self.assertEqual(summary["cell_count"], 144)
        self.assertAlmostEqual(summary["observed"]["solid_angle"], 4.0 * math.pi, places=12)
        self.assertAlmostEqual(summary["observed"]["surface_area"], 16.0 * math.pi, places=11)
        self.assertAlmostEqual(summary["observed"]["wedge_volume"], 32.0 * math.pi / 3.0, places=11)

    def test_typed_route_and_full_validation(self):
        route = polyatlas_route(1, 144, layers=("matrix", "mirror"))
        self.assertTrue(route["found"])
        self.assertEqual(route["path"][0], 1)
        self.assertEqual(route["path"][-1], 144)
        self.assertTrue(all(edge["layers"] for edge in route["edges"]))
        receipt = validate()
        self.assertEqual(receipt["status"], "PASS", receipt)
        self.assertEqual(receipt["pass_count"], receipt["check_count"])


if __name__ == "__main__":
    unittest.main()
