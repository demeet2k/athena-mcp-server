import unittest
from athena_mcp.collective_growth import CollectiveGrowthRuntime


class CollectiveGrowthTests(unittest.TestCase):
    def setUp(self):
        self.r = CollectiveGrowthRuntime()

    def test_demand_allocator_prefers_high_value_fit(self):
        x = self.r.demand_allocate([
            {'id':'critical','utility':1,'gap':1,'bridge_value':1,'urgency':1,'required_capabilities':['math']},
            {'id':'low','utility':.2,'gap':.2,'bridge_value':.2,'required_capabilities':['text']},
        ], [
            {'id':'m','capabilities':['math'],'load':0},
            {'id':'t','capabilities':['text'],'load':.2},
        ])
        self.assertEqual(x['assignments'][0]['task'], 'critical')
        self.assertEqual(x['assignments'][0]['worker'], 'm')

    def test_bridge_accounting(self):
        self.assertEqual(self.r.bridge_account({'expected_future_uses':10,'route_saving_per_use':2,'build_cost':5,'maintenance_cost':2,'locked_capacity_cost':1})['decision'], 'BUILD')
        self.assertEqual(self.r.bridge_account({'expected_future_uses':1,'route_saving_per_use':1,'build_cost':5})['decision'], 'DO_NOT_BUILD')

    def test_fission_and_fusion(self):
        self.assertEqual(self.r.restructure({'coordination_overhead':1,'contagion':1,'size_pressure':1,'internal_cohesion':0})['decision'], 'FISSION')
        self.assertEqual(self.r.restructure({'complementarity':1,'duplicate_work':1,'shared_dependencies':1,'interface_maturity':1,'identity_conflict':0})['decision'], 'FUSE')

    def test_dependency_alarm_is_scoped(self):
        x = self.r.dependency_alarm([{'node':'A','severity':1}], [
            {'src':'A','dst':'B','weight':1},
            {'src':'B','dst':'C','weight':.5},
            {'src':'X','dst':'Y','weight':1},
        ], max_hops=3)
        nodes = [i['node'] for i in x['impacted']]
        self.assertIn('C', nodes)
        self.assertNotIn('Y', nodes)

    def test_lifecycle_preserves_lineage(self):
        x = self.r.artifact_lifecycle([
            {'id':'old','reuse':0,'novelty':0,'age':1,'superseded':True},
            {'id':'root','critical_lineage':True},
            {'id':'weak','evidence':.1,'reuse':.5},
        ])
        d = {i['id']:i['decision'] for i in x['decisions']}
        self.assertEqual(d['old'], 'PRUNE_REFERENCE')
        self.assertEqual(d['root'], 'KEEP_REFERENCE')
        self.assertEqual(d['weak'], 'QUARANTINE')


if __name__ == '__main__':
    unittest.main()
