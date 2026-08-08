import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV4Tests(unittest.TestCase):
    def test_regime_and_contextual_bandit_learns_from_observation(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            regime=srv.call_tool('athena_regime_resolve', {'signals':{'uncertainty':.9,'volatility':.8,'divisibility':.8,'coupling':.2}})['regime']
            arms=[{'id':'A','features':{'novelty':.8}},{'id':'B','features':{'novelty':.2}}]
            before=srv.call_tool('athena_bandit_select', {'arms':arms,'context':{'risk':.2},'regime':regime})
            self.assertEqual(before['decision'],'EXPLORE_OR_EXPLOIT')
            for _ in range(5):
                srv.call_tool('athena_bandit_observe', {'arm_id':'A','reward':1,'features':{'risk':.2,'novelty':.8},'regime':regime})
                srv.call_tool('athena_bandit_observe', {'arm_id':'B','reward':0,'features':{'risk':.2,'novelty':.2},'regime':regime})
            after=srv.call_tool('athena_bandit_select', {'arms':arms,'context':{'risk':.2},'regime':regime,'exploration_alpha':.1})
            self.assertEqual(after['winner'],'A')
            a=next(x for x in after['ranked_arms'] if x['arm_id']=='A')
            b=next(x for x in after['ranked_arms'] if x['arm_id']=='B')
            self.assertGreater(a['mean_reward'],b['mean_reward'])
            srv.store.close()

    def test_credit_preserves_causal_confidence_and_residual(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            weak=srv.call_tool('athena_credit_assign', {
                'outcome_key':'o1','outcome_delta':.8,
                'interventions':[{'id':'x','evidence_weight':.5}],
            })
            self.assertEqual(weak['credits'][0]['status'],'ASSOCIATIONAL')
            self.assertNotEqual(weak['unattributed_residual'],0)
            strong=srv.call_tool('athena_credit_assign', {
                'outcome_key':'o2','outcome_delta':.8,
                'design':{'randomized':True,'control_group':True,'direct_measurement':1,'temporal_isolation':1,'replications':5},
                'interventions':[{'id':'x','counterfactual_without_delta':.2,'direct_measurement':1}],
            })
            self.assertEqual(strong['credits'][0]['status'],'CAUSAL_SUPPORTED')
            self.assertGreater(strong['credits'][0]['causal_confidence'], weak['credits'][0]['causal_confidence'])
            srv.store.close()

    def test_budget_schedule_uses_measured_worker_cost(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_worker_cost_observe', {'worker_id':'cheap','task_id':'past','resources':{'tokens':1},'budget':{'tokens':10},'useful_output':1})
            srv.call_tool('athena_worker_cost_observe', {'worker_id':'expensive','task_id':'past','resources':{'tokens':9},'budget':{'tokens':10},'useful_output':.3})
            out=srv.call_tool('athena_budget_schedule', {
                'tasks':[{'id':'critical','utility':1,'gap':1,'bridge_value':1,'required_capabilities':['math']}],
                'workers':[{'id':'cheap','capabilities':['math']},{'id':'expensive','capabilities':['math']}],
                'remaining_budget':{'tokens':5},
            })
            self.assertEqual(out['assignments'][0]['worker'],'cheap')
            self.assertEqual(out['assignments'][0]['cost_source'],'MEASURED_HISTORY')
            self.assertLess(out['remaining_budget']['tokens'],5)
            srv.store.close()

    def test_adaptive_diffusion_moves_from_prior_and_reinforces(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            prior=srv.collective_ecology.diffusion_coefficient('artifact','module')['coefficient']
            for _ in range(5):
                srv.call_tool('athena_diffusion_observe', {'source_scale':'artifact','target_scale':'module','transfer_utility':1,'evidence_weight':1,'causal_confidence':.5})
            learned=srv.collective_ecology.diffusion_coefficient('artifact','module')
            self.assertGreater(learned['coefficient'],prior)
            out=srv.call_tool('athena_pheromone_adaptive_reinforce', {
                'source_scale':'artifact','coordinates':{'artifact':'A','module':'M'},
                'observations':{'quality':1,'evidence':1,'reuse':1},'age':0,
            })
            self.assertEqual(len(out['updates']),2)
            self.assertGreater(out['updates'][0]['score'],0)
            srv.store.close()

    def test_antibody_executes_restricted_repository_witness(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            ab=srv.call_tool('athena_failure_antibody_register', {
                'signature':'stale expected vid write',
                'detector':{'keywords':['stale','expected','vid'],'min_keyword_hits':2},
                'repair':{'action':'rehydrate_then_retry'},
                'regression_refs':['tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex'],
            })
            out=srv.call_tool('athena_antibody_execute_regressions', {'antibody_id':ab['antibody_id'],'timeout_s':20})
            self.assertEqual(out['status'],'PASS')
            self.assertEqual(out['runs'][0]['status'],'PASS')
            self.assertEqual(out['antibody_update']['outcome'],'REGRESSION_PASS')
            srv.store.close()

    def test_rollout_is_uncertainty_banded_and_simulate_only(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_rollout_simulate', {
                'regime':'GLOBAL','initial_context':{'risk':.2},
                'trajectories':[
                    {'id':'lean','steps':[{'id':'s1','arm_id':'lean','configuration':{'workers':3,'avg_degree':2,'reserve_fraction':.2},'context_delta':{'risk':-.05}}, {'id':'s2','arm_id':'lean','configuration':{'workers':4,'avg_degree':2,'reserve_fraction':.2}}]},
                    {'id':'dense','steps':[{'id':'d1','arm_id':'dense','configuration':{'workers':12,'avg_degree':11,'reserve_fraction':.02},'risk':.5}]},
                ],
            })
            self.assertEqual(out['decision'],'SIMULATE_ONLY')
            self.assertTrue(out['ranked_trajectories'])
            for t in out['ranked_trajectories']:
                self.assertLessEqual(t['lower_return'],t['upper_return'])
            self.assertFalse(srv.collective_memory.topology_get('rollout')["exists"])
            srv.store.close()

    def test_projection_saga_semantic_only_and_stale_head_rejection(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_topology_apply', {'topology_id':'T','expected_version':0,'operation':'INIT','payload':{'state':{'modules':{'M':{'id':'M','active':True}},'bridges':[]}}})
            eid=srv.store.head('global')['eid']
            dry=srv.call_tool('athena_topology_project_jspace', {'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid,'dry_run':True})
            self.assertTrue(dry['dry_run'])
            out=srv.call_tool('athena_topology_project_jspace', {'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid})
            self.assertEqual(out['projection']['status'],'COMPLETED')
            self.assertEqual(out['authority'],'SEMANTIC_ONLY')
            self.assertFalse(out['atomic'])
            self.assertTrue(srv.store.one("SELECT edge_id FROM edges WHERE src='T' AND relation='HAS_ACTIVE_MODULE' AND dst='M'"))
            with self.assertRaises(ValueError):
                srv.call_tool('athena_topology_project_jspace', {'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid})
            srv.store.close()

    def test_mcp_surface_and_v4_resource(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_bandit_select','athena_credit_assign','athena_budget_schedule','athena_diffusion_observe','athena_antibody_execute_regressions','athena_rollout_simulate','athena_topology_project_jspace'):
                self.assertIn(name,names)
            resources=srv.handle({'jsonrpc':'2.0','id':2,'method':'resources/list'})['result']['resources']
            self.assertIn('athena://collective/v4',{x['uri'] for x in resources})
            read=srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://collective/v4'}})
            self.assertIn('result',read)
            self.assertEqual(read['result']['contents'][0]['mimeType'],'application/json')
            srv.store.close()


if __name__=='__main__': unittest.main()
