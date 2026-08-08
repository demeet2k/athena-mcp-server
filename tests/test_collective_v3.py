import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV3Tests(unittest.TestCase):
    def test_budget_and_automatic_runtime_meter(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            b = srv.call_tool("athena_budget_record", {
                "run_key": "r1",
                "resources": {"tokens": 100, "wall_time_s": 2},
                "budget": {"tokens": 200, "wall_time_s": 4},
                "outcome": {"useful_output": .8},
            })
            self.assertEqual(b["budget_pressure"], .5)
            self.assertFalse(b["over_budget"])
            srv.handle({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"athena_policy_state","arguments":{}}})
            s = srv.call_tool("athena_budget_summary", {})
            self.assertGreaterEqual(s["runtime_usage_events"], 1)
            self.assertIn("athena_policy_state", s["tool_wall_time_s"])
            srv.store.close()

    def test_policy_is_versioned_bounded_and_rollbackable(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            before = srv.call_tool("athena_policy_state", {})
            self.assertEqual(before["version"], 0)
            up = srv.call_tool("athena_policy_update", {
                "expected_version": 0,
                "features": {"uncertainty": .8, "reserve_fraction": .2},
                "observed_reward": .95,
            })
            self.assertEqual(up["version"], 1)
            self.assertGreater(up["state"]["reliability"], 0)
            with self.assertRaises(ValueError):
                srv.call_tool("athena_policy_update", {
                    "expected_version": 0, "features": {"x": 1}, "observed_reward": .5,
                })
            rb = srv.call_tool("athena_policy_rollback", {
                "txid": up["txid"], "expected_version": 1,
            })
            self.assertEqual(rb["version"], 2)
            self.assertEqual(rb["state"]["n"], 0)
            self.assertEqual(rb["state"]["weights"], {})
            srv.store.close()

    def test_counterfactual_never_commits(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            out = srv.call_tool("athena_counterfactual_simulate", {
                "candidates": [
                    {"id":"small","configuration":{"workers":3,"avg_degree":2,"reserve_fraction":.2}},
                    {"id":"dense","configuration":{"workers":12,"avg_degree":11,"reserve_fraction":.02},"risk":.4},
                ],
                "context": {"risk": .2},
            })
            self.assertEqual(out["decision"], "SIMULATE_ONLY")
            self.assertEqual(len(out["ranked_candidates"]), 2)
            self.assertFalse(srv.collective_memory.topology_get("counterfactual")["exists"])
            srv.store.close()

    def test_elder_authority_is_empirical_not_age(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            for _ in range(6):
                srv.call_tool("athena_elder_observe", {
                    "entity_id":"good",
                    "outcomes":{"reuse_success":1,"prediction_success":1,"repair_success":1,"regression_success":1,"generalization_success":1},
                })
                srv.call_tool("athena_elder_observe", {
                    "entity_id":"bad",
                    "outcomes":{"reuse_success":0,"prediction_success":0,"repair_success":0,"regression_success":0,"generalization_success":0,"contradiction":1},
                })
            ranked = srv.call_tool("athena_elder_rank", {})
            self.assertEqual(ranked["elders"][0]["entity_id"], "good")
            self.assertGreater(ranked["elders"][0]["authority"], ranked["elders"][-1]["authority"])
            srv.store.close()

    def test_antibody_evolution_and_variant_selection(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            base = srv.call_tool("athena_failure_antibody_register", {
                "signature":"stale expected vid write",
                "detector":{"keywords":["stale","expected","vid"],"min_keyword_hits":2},
                "repair":{"action":"rehydrate"},
                "regression_refs":["tests/test_runtime.py"],
            })
            for _ in range(3):
                srv.call_tool("athena_antibody_record_outcome", {"antibody_id":base["antibody_id"],"outcome":"SUCCESS"})
            child = srv.call_tool("athena_antibody_evolve", {
                "parent_id":base["antibody_id"],
                "signature":"stale expected topology vid write",
                "detector":{"keywords":["stale","topology","vid"],"min_keyword_hits":2},
                "repair":{"action":"rehydrate_topology"},
                "ttl_hours":24,
            })
            self.assertEqual(child["parent_id"], base["antibody_id"])
            selected = srv.call_tool("athena_antibody_select", {"event":"stale expected vid write rejected"})
            self.assertTrue(selected["matches"])
            self.assertEqual(selected["matches"][0]["antibody_id"], base["antibody_id"])
            srv.store.close()

    def test_multiscale_pheromone_attenuates(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            out = srv.call_tool("athena_pheromone_multiscale_reinforce", {
                "source_scale":"artifact",
                "coordinates":{"artifact":"A","module":"M","domain":"D","system":"S"},
                "observations":{"quality":1,"evidence":1,"reuse":1},
                "age":0,
            })
            scores = {x["scale"]:x["score"] for x in out["updates"]}
            self.assertGreater(scores["artifact"], scores["module"])
            self.assertGreater(scores["module"], scores["domain"])
            field = srv.call_tool("athena_pheromone_multiscale_field", {})
            self.assertGreaterEqual(field["count"], 4)
            srv.store.close()

    def test_mcp_discovery_and_v3_resource(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            names = {x["name"] for x in srv.handle({"jsonrpc":"2.0","id":1,"method":"tools/list"})["result"]["tools"]}
            for name in (
                "athena_budget_record","athena_policy_update","athena_counterfactual_simulate",
                "athena_elder_observe","athena_antibody_evolve","athena_pheromone_multiscale_reinforce",
            ):
                self.assertIn(name, names)
            resources = srv.handle({"jsonrpc":"2.0","id":2,"method":"resources/list"})["result"]["resources"]
            self.assertIn("athena://collective/v3", {x["uri"] for x in resources})
            read = srv.handle({"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"athena://collective/v3"}})
            self.assertEqual(read["result"]["contents"][0]["mimeType"], "application/json")
            srv.store.close()


if __name__ == "__main__":
    unittest.main()
