import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV2Tests(unittest.TestCase):
    def test_persistent_pheromone_survives_server_restart(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            first = srv.call_tool("athena_pheromone_reinforce", {
                "route_key": "route:A",
                "observations": {"quality": 1, "evidence": 1, "reuse": 1},
                "age": 0,
            })
            self.assertGreater(first["score"], 0)
            srv.store.close()

            srv2 = Server(f.name)
            field = srv2.call_tool("athena_pheromone_field", {"route_key": "route:A"})
            self.assertEqual(field["count"], 1)
            self.assertEqual(field["routes"][0]["version"], 1)
            srv2.store.close()

    def test_jspace_dependency_orientation(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            srv.store.put_edge("e1", "A", "DEPENDS_ON", "B", "eid", {"confidence": 1})
            srv.store.put_edge("e2", "C", "DEPENDS_ON", "A", "eid", {"confidence": 1})
            out = srv.call_tool("athena_jspace_alarm", {
                "seeds": [{"node": "B", "severity": 1}],
                "max_hops": 3,
            })
            nodes = [x["node"] for x in out["impacted"]]
            self.assertEqual(nodes, ["B", "A", "C"])
            self.assertEqual(out["source"], "JSPACE")
            srv.store.close()

    def test_rgo_observation_calibrates_prediction(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            for i, (pred, obs) in enumerate(((.4, .5), (.5, .6), (.6, .7), (.7, .8))):
                srv.call_tool("athena_rgo_observe", {
                    "plan_key": f"p{i}",
                    "predicted_rgo": pred,
                    "observed_rgo": obs,
                })
            out = srv.call_tool("athena_rgo_calibrate", {"predicted_rgo": .5})
            self.assertEqual(out["calibration"]["n"], 4)
            self.assertGreater(out["calibrated_rgo"], .5)
            srv.store.close()

    def test_topology_cas_fission_and_rollback(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            init = srv.call_tool("athena_topology_apply", {
                "topology_id": "T",
                "expected_version": 0,
                "operation": "INIT",
                "payload": {"state": {"modules": {"M": {"id": "M", "active": True}}, "bridges": []}},
            })
            self.assertEqual(init["version"], 1)
            fission = srv.call_tool("athena_topology_apply", {
                "topology_id": "T",
                "expected_version": 1,
                "operation": "FISSION",
                "payload": {"module_id": "M", "children": [{"id": "M1"}, {"id": "M2"}]},
            })
            self.assertFalse(fission["state"]["modules"]["M"]["active"])
            with self.assertRaises(ValueError):
                srv.call_tool("athena_topology_apply", {
                    "topology_id": "T", "expected_version": 1,
                    "operation": "PATCH_MODULE", "payload": {"module_id": "M1", "patch": {"x": 1}},
                })
            rollback = srv.call_tool("athena_topology_rollback", {
                "topology_id": "T",
                "txid": fission["txid"],
                "expected_version": 2,
            })
            self.assertEqual(rollback["version"], 3)
            self.assertTrue(rollback["state"]["modules"]["M"]["active"])
            self.assertNotIn("M1", rollback["state"]["modules"])
            srv.store.close()

    def test_failure_antibody_reuses_repair_and_regression(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            reg = srv.call_tool("athena_failure_antibody_register", {
                "signature": "stale expected vid write",
                "detector": {"keywords": ["stale", "expected", "vid"], "min_keyword_hits": 2},
                "repair": {"action": "rehydrate_then_retry"},
                "regression_refs": ["tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex"],
            })
            out = srv.call_tool("athena_failure_antibody_match", {
                "event": "write rejected because stale expected vid did not match current",
            })
            self.assertEqual(out["count"], 1)
            self.assertEqual(out["matches"][0]["antibody_id"], reg["antibody_id"])
            self.assertEqual(out["matches"][0]["repair"]["action"], "rehydrate_then_retry")
            self.assertTrue(out["matches"][0]["regression_refs"])
            srv.store.close()

    def test_mcp_discovery_and_resource(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            tools = srv.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
            names = {x["name"] for x in tools}
            for name in (
                "athena_pheromone_reinforce", "athena_jspace_alarm", "athena_rgo_observe",
                "athena_topology_apply", "athena_topology_rollback", "athena_failure_antibody_register",
            ):
                self.assertIn(name, names)
            resources = srv.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})["result"]["resources"]
            self.assertIn("athena://collective/v2", {x["uri"] for x in resources})
            read = srv.handle({"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "athena://collective/v2"}})
            self.assertEqual(read["result"]["contents"][0]["mimeType"], "application/json")
            srv.store.close()


if __name__ == "__main__":
    unittest.main()
