import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV5Tests(unittest.TestCase):
    def test_full_covariance_bayes_and_empirical_calibration(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            pre=srv.call_tool('athena_bayes_predict',{'features':{'x':.8,'y':.8},'regime':'R','arm_id':'A'})
            for _ in range(12):
                srv.call_tool('athena_bayes_observe',{'features':{'x':.8,'y':.8},'reward':.9,'regime':'R','arm_id':'A'})
                srv.call_tool('athena_bayes_observe',{'features':{'x':-.8,'y':-.8},'reward':.1,'regime':'R','arm_id':'A'})
            post=srv.call_tool('athena_bayes_predict',{'features':{'x':.8,'y':.8},'regime':'R','arm_id':'A'})
            self.assertGreater(post['n'],20)
            self.assertGreater(post['mean'],.5)
            self.assertLess(post['sigma'],pre['sigma'])
            self.assertNotEqual(post['posterior_covariance'][1][2],0)
            cal=srv.call_tool('athena_uncertainty_calibrate',{'regime':'R','arm_id':'A'})
            self.assertGreater(cal['n'],0)
            srv.store.close()

    def test_information_gain_experiment_design_and_ethics_gate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_experiment_design',{
                'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],
                'experiments':[
                    {'id':'diagnostic','positive_probability':{'H1':.95,'H2':.05},'cost':.1,'risk':.1,'ethical':True,'randomizable':True},
                    {'id':'uninformative','positive_probability':{'H1':.55,'H2':.45},'cost':.1,'risk':.1,'ethical':True},
                    {'id':'blocked','positive_probability':{'H1':1,'H2':0},'ethical':False},
                ],
                'sample_size':20,
            })
            self.assertEqual(out['decision'],'DESIGN_ONLY')
            self.assertEqual(out['winner'],'diagnostic')
            blocked=next(x for x in out['ranked_experiments'] if x['id']=='blocked')
            self.assertEqual(blocked['status'],'ETHICS_BLOCK')
            self.assertEqual(sum(out['ranked_experiments'][0]['allocation'].values()),20)
            srv.store.close()

    def test_interaction_and_delayed_credit(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            ex=[]
            for _ in range(3):
                ex += [
                    {'interventions':[],'outcome_delta':.1,'design_confidence':.9},
                    {'interventions':['A'],'outcome_delta':.2,'design_confidence':.9},
                    {'interventions':['B'],'outcome_delta':.2,'design_confidence':.9},
                    {'interventions':['A','B'],'outcome_delta':.8,'design_confidence':.9},
                ]
            out=srv.call_tool('athena_interaction_credit',{'analysis_key':'factorial','experiments':ex})
            pair=next(x for x in out['terms'] if x['term']=='A×B')
            self.assertAlmostEqual(pair['effect'],.5,places=6)
            self.assertEqual(pair['status'],'CAUSAL_SUPPORTED')
            near=srv.call_tool('athena_delayed_credit_record',{'action_id':'A','outcome_key':'near','outcome_delta':1,'delay_cycles':0,'causal_confidence':.8})
            far=srv.call_tool('athena_delayed_credit_record',{'action_id':'A','outcome_key':'far','outcome_delta':1,'delay_cycles':10,'causal_confidence':.8})
            self.assertGreater(near['credited_reward'],far['credited_reward'])
            srv.store.close()

    def test_learned_transition_and_rollout_remain_simulation(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for i in range(8):
                srv.call_tool('athena_transition_observe',{'action_id':'FOCUS','before':{'progress':.1,'risk':.4},'after':{'progress':.5,'risk':.3}})
            p=srv.call_tool('athena_transition_predict',{'action_id':'FOCUS','context':{'progress':.2,'risk':.4}})
            self.assertGreater(p['delta_mean']['progress'],0)
            self.assertLess(p['delta_mean']['risk'],0)
            out=srv.call_tool('athena_rollout_learned',{'initial_context':{'progress':.2,'risk':.4},'trajectories':[{'id':'focus2','steps':[{'action_id':'FOCUS','base_reward':.7},{'action_id':'FOCUS','base_reward':.7}]}]})
            self.assertEqual(out['decision'],'SIMULATE_ONLY')
            self.assertLessEqual(out['ranked_trajectories'][0]['lower_return'],out['ranked_trajectories'][0]['upper_return'])
            srv.store.close()

    def test_multiperiod_schedule_respects_dependencies_and_budget(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_schedule_multiperiod',{
                'tasks':[
                    {'id':'A','utility':1,'duration':2,'required_capabilities':['math'],'resource_cost':{'tokens':2}},
                    {'id':'B','utility':1,'duration':1,'dependencies':['A'],'required_capabilities':['math'],'resource_cost':{'tokens':2}},
                    {'id':'C','utility':.7,'duration':1,'required_capabilities':['code'],'resource_cost':{'tokens':2}},
                ],
                'workers':[{'id':'w1','capabilities':['math']},{'id':'w2','capabilities':['code']}],
                'horizon':6,'budget':{'tokens':6},'beam_width':64,
            })
            by={x['task']:x for x in out['schedule']}
            self.assertGreaterEqual(by['B']['start'],by['A']['finish'])
            self.assertGreaterEqual(out['remaining_budget']['tokens'],0)
            self.assertEqual(out['optimality'],'BOUNDED_BEAM_SEARCH_NO_GLOBAL_OPTIMALITY_PROOF')
            srv.store.close()

    def test_constrained_witness_cell_executes_known_test(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_witness_cell',{'regression_ref':'tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex','timeout_s':20})
            self.assertEqual(out['status'],'PASS')
            self.assertTrue(out['executed'])
            self.assertFalse(out['hermetic'])
            self.assertIn('sanitized_env',out['isolation'])
            srv.store.close()

    def test_learned_regime_geometry_and_pareto_frontier(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for _ in range(6):
                srv.call_tool('athena_regime_geometry_observe',{'signals':{'hardness':.9,'uncertainty':.8,'coupling':.2,'divisibility':.8,'volatility':.7},'reward':.9,'cluster_id':'explore-hard'})
            geo=srv.call_tool('athena_regime_geometry_resolve',{'signals':{'hardness':.88,'uncertainty':.82,'coupling':.2,'divisibility':.8,'volatility':.7}})
            self.assertEqual(geo['learned_neighbors'][0]['cluster_id'],'explore-hard')
            pf=srv.call_tool('athena_pareto_frontier',{
                'candidates':[
                    {'id':'A','metrics':{'quality':.9,'cost':.8}},
                    {'id':'B','metrics':{'quality':.8,'cost':.2}},
                    {'id':'C','metrics':{'quality':.7,'cost':.9}},
                ],
                'directions':{'quality':'max','cost':'min'},
            })
            self.assertEqual({x['id'] for x in pf['frontier']},{'A','B'})
            self.assertEqual(pf['dominated'][0]['id'],'C')
            srv.store.close()

    def test_projection_compensation_removes_only_projection_edges(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_topology_apply',{'topology_id':'T','expected_version':0,'operation':'INIT','payload':{'state':{'modules':{'M':{'id':'M','active':True}},'bridges':[]}}})
            eid=srv.store.head('global')['eid']
            projected=srv.call_tool('athena_topology_project_jspace',{'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid})
            pid=projected['projection']['projection_id']
            self.assertTrue(srv.store.one("SELECT edge_id FROM edges WHERE src='T' AND relation='HAS_ACTIVE_MODULE' AND dst='M'"))
            head=srv.store.head('global')['eid']
            comp=srv.call_tool('athena_projection_compensate',{'projection_id':pid,'expected_semantic_eid':head})
            self.assertEqual(comp['status'],'SEMANTIC_COMPENSATED')
            self.assertFalse(srv.store.one("SELECT edge_id FROM edges WHERE src='T' AND relation='HAS_ACTIVE_MODULE' AND dst='M'"))
            self.assertEqual(srv.call_tool('athena_projection_status',{'projection_id':pid})['status'],'COMPENSATED')
            srv.store.close()

    def test_mcp_v5_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_bayes_predict','athena_experiment_design','athena_interaction_credit','athena_transition_observe','athena_schedule_multiperiod','athena_witness_cell','athena_pareto_frontier','athena_projection_compensate'):
                self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
