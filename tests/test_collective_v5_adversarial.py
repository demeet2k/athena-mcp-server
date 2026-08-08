import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV5AdversarialTests(unittest.TestCase):
    def test_prediction_and_design_do_not_self_train(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for _ in range(5):
                srv.call_tool('athena_bayes_predict',{'features':{'x':1},'regime':'R','arm_id':'A'})
            science=srv.collective_ecology.s.one("SELECT COUNT(*) AS n FROM collective_v5_bayes_observations")
            self.assertEqual(science['n'],0)
            design=srv.call_tool('athena_experiment_design',{
                'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],
                'experiments':[{'id':'missing','positive_probability':{'H1':.9}}, {'id':'unsafe','positive_probability':{'H1':1,'H2':0},'ethical':False}],
            })
            self.assertIsNone(design['winner'])
            self.assertEqual(next(x for x in design['ranked_experiments'] if x['id']=='missing')['status'],'INCOMPLETE_PREDICTIONS')
            self.assertEqual(next(x for x in design['ranked_experiments'] if x['id']=='unsafe')['status'],'ETHICS_BLOCK')
            srv.store.close()

    def test_missing_factorial_cell_stays_unidentified(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            ex=[
                {'interventions':[],'outcome_delta':.1,'design_confidence':1},
                {'interventions':['A'],'outcome_delta':.2,'design_confidence':1},
                {'interventions':['B'],'outcome_delta':.2,'design_confidence':1},
            ]
            out=srv.call_tool('athena_interaction_credit',{'analysis_key':'missing11','experiments':ex})
            pair=next(x for x in out['terms'] if x['term']=='A×B')
            self.assertIsNone(pair['effect'])
            self.assertEqual(pair['status'],'UNIDENTIFIED')
            srv.store.close()

    def test_zero_confidence_delayed_credit_is_zero(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_delayed_credit_record',{'action_id':'A','outcome_key':'o','outcome_delta':1,'delay_cycles':0,'causal_confidence':0})
            self.assertEqual(out['credited_reward'],0)
            srv.store.close()

    def test_unseen_transition_does_not_invent_deltas_or_train_on_rollout(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            pre=srv.call_tool('athena_transition_predict',{'action_id':'NEVER','context':{'risk':.5}})
            self.assertEqual(pre['delta_mean'],{})
            self.assertEqual(pre['next_context_mean']['risk'],.5)
            for _ in range(3):
                srv.call_tool('athena_rollout_learned',{'initial_context':{'risk':.5},'trajectories':[{'id':'x','steps':[{'action_id':'NEVER','base_reward':.5}]}]})
            n=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            self.assertEqual(n,0)
            srv.store.close()

    def test_scheduler_unknown_cost_is_penalized_and_cycles_not_fabricated(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_worker_cost_observe',{'worker_id':'known','task_id':'past','resources':{'tokens':1},'budget':{'tokens':10},'useful_output':1})
            out=srv.call_tool('athena_schedule_multiperiod',{
                'tasks':[{'id':'t','utility':1,'duration':1,'required_capabilities':['x']}],
                'workers':[{'id':'known','capabilities':['x']},{'id':'unknown','capabilities':['x']}],
                'horizon':2,'budget':{'tokens':5},'beam_width':16,
            })
            self.assertEqual(out['schedule'][0]['worker'],'known')
            cyc=srv.call_tool('athena_schedule_multiperiod',{
                'tasks':[{'id':'A','dependencies':['B'],'duration':1},{'id':'B','dependencies':['A'],'duration':1}],
                'workers':[{'id':'w','capabilities':[]}], 'horizon':4,
            })
            self.assertEqual(cyc['scheduled_count'],0)
            self.assertEqual(set(cyc['unscheduled']),{'A','B'})
            srv.store.close()

    def test_witness_cell_rejects_escape_and_does_not_claim_hermetic(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            bad=srv.call_tool('athena_witness_cell',{'regression_ref':'tests/test_runtime.py;echo pwn::RuntimeTests::test_registry_stale_text_simplex'})
            self.assertEqual(bad['status'],'INVALID_REF')
            self.assertFalse(bad['executed'])
            good=srv.call_tool('athena_witness_cell',{'regression_ref':'tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex'})
            self.assertFalse(good['hermetic'])
            srv.store.close()

    def test_robust_pareto_requires_interval_worst_case_dominance(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            pf=srv.call_tool('athena_pareto_frontier',{
                'candidates':[
                    {'id':'uncertain','metrics':{'quality':.9,'cost':.2},'intervals':{'quality':[.5,1.0],'cost':[.1,.4]}},
                    {'id':'stable','metrics':{'quality':.8,'cost':.25},'intervals':{'quality':[.78,.82],'cost':[.24,.26]}},
                ], 'directions':{'quality':'max','cost':'min'}, 'robust':True,
            })
            self.assertEqual({x['id'] for x in pf['frontier']},{'uncertain','stable'})
            srv.store.close()

    def test_compensation_stale_head_and_edge_ownership(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            unrelated=srv.call_tool('athena_add_edge',{'src':'X','relation':'KEEP','dst':'Y'})
            srv.call_tool('athena_topology_apply',{'topology_id':'T','expected_version':0,'operation':'INIT','payload':{'state':{'modules':{'M':{'id':'M','active':True}},'bridges':[]}}})
            eid=srv.store.head('global')['eid']
            p=srv.call_tool('athena_topology_project_jspace',{'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid})
            pid=p['projection']['projection_id']; stale=eid
            with self.assertRaises(ValueError):
                srv.call_tool('athena_projection_compensate',{'projection_id':pid,'expected_semantic_eid':stale})
            head=srv.store.head('global')['eid']
            srv.call_tool('athena_projection_compensate',{'projection_id':pid,'expected_semantic_eid':head})
            self.assertTrue(srv.store.one('SELECT edge_id FROM edges WHERE edge_id=?',(unrelated['edge_id'],)))
            srv.store.close()


if __name__=='__main__': unittest.main()
