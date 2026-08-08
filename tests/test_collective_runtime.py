import unittest
from athena_mcp.collective_runtime import CollectiveRuntime


class CollectiveRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.r = CollectiveRuntime()

    def test_form_selection_and_role_conservation(self):
        cases = [
            ("HIVE", dict(hardness=.4, uncertainty=.2, divisibility=.9, coupling=.3, volatility=.1, repetition=.9, reuse=.8)),
            ("SWARM", dict(hardness=.5, uncertainty=.95, divisibility=.8, coupling=.1, volatility=.9, innovation=.9)),
            ("PACK", dict(hardness=.95, uncertainty=.4, divisibility=.1, coupling=.95, risk=.8, evidence_sensitivity=.9)),
            ("HERD", dict(migration=1.0, risk=.8, coupling=.6, reuse=.8)),
        ]
        for expected, signals in cases:
            p = self.r.plan(signals, max_workers=12)
            self.assertEqual(p["form"], expected)
            self.assertEqual(sum(p["roles"].values()), p["active_workers"])
            self.assertEqual(p["active_workers"] + p["reserve_workers"], 12)
            self.assertGreaterEqual(p["reserve_workers"], p["protected_reserve"])

    def test_sparse_topology_beats_dense_when_coupling_is_high(self):
        dense = self.r.evaluate({"workers":12, "avg_degree":11, "coupling":.9})
        sparse = self.r.evaluate({"workers":12, "avg_degree":4, "coupling":.9})
        self.assertGreater(sparse["return_on_group_organization"], dense["return_on_group_organization"])

    def test_quorum_requires_evidence_and_survives_inhibition(self):
        good = self.r.quorum([
            {"id":"A", "support":.95, "evidence_quality":.95, "inhibition":.05},
            {"id":"B", "support":.60, "evidence_quality":.70, "inhibition":.10},
        ], risk=.5, evidence_sensitivity=.8)
        self.assertEqual(good["decision"], "COMMIT")
        blocked = self.r.quorum([
            {"id":"A", "support":.98, "evidence_quality":.30, "inhibition":.50, "contradiction":.70},
            {"id":"B", "support":.55, "evidence_quality":.55, "inhibition":.10},
        ], risk=.8, evidence_sensitivity=.9)
        self.assertEqual(blocked["decision"], "EXPLORE")

    def test_stigmergy_evaporates_stale_contradicted_routes(self):
        bad = self.r.stigmergy_update(.8, {"quality":.1,"evidence":.1,"staleness":1,"contradiction":.5}, age=5)
        good = self.r.stigmergy_update(.2, {"quality":1,"novelty":.8,"evidence":1,"reuse":1,"bridge_value":.8,"downstream_gain":1}, age=.1)
        self.assertLess(bad["updated_score"], .8)
        self.assertGreater(good["updated_score"], .2)

    def test_homeostasis_can_throttle_growth(self):
        h = self.r.health({"context_saturation":.95,"error_rate":.5,"reserve_fraction":.01,"evidence_quality":.3})
        self.assertEqual(h["status"], "RED")
        self.assertGreaterEqual(h["critical_count"], 2)


if __name__ == "__main__":
    unittest.main()
