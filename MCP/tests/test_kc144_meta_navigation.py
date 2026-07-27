from __future__ import annotations

import json
import pathlib
import sys
import unittest

MCP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MCP))

from kc144_meta_navigation import register_kc144_meta_navigation
from kc144_meta_runtime import MAPS, compile_query, locate, route, station, validate


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator


class KC144NavigationTests(unittest.TestCase):
    def test_grid_bijection(self):
        self.assertEqual(len({station(gid)["grid"] for gid in range(1, 145)}), 144)

    def test_map_count(self):
        self.assertEqual(len(MAPS), 37)

    def test_locator(self):
        result = locate("find the mental compiler through the mycelium")
        self.assertTrue(result["found"])
        self.assertIn("compile", result["capabilities"])

    def test_route(self):
        result = route("H06", "M12")
        self.assertEqual(result["status"], "ROUTE_FOUND")
        self.assertEqual(result["nodes"][0]["station"], "H06")
        self.assertEqual(result["nodes"][-1]["station"], "M12")

    def test_compile(self):
        result = compile_query("quaternion lift proof search and auditable return")
        stations = {item["station"] for item in result["candidate_stations"]}
        self.assertIn("F06", stations)
        self.assertIn("I09", stations)

    def test_registration(self):
        fake = FakeMCP()
        register_kc144_meta_navigation(fake)
        self.assertEqual(set(fake.tools), {"locate_kc144", "use_kc144", "kc144_station", "kc144_route", "kc144_map", "kc144_status", "kc144_validate"})
        self.assertTrue(json.loads(fake.tools["locate_kc144"]("KC144"))["found"])

    def test_validate(self):
        self.assertEqual(validate()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
