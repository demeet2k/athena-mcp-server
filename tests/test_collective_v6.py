import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV6Tests(unittest.TestCase):
    def test_nonlinear_ood_and_observation(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            regime='REGIME/TEST'
            no_ref=srv.call_tool('athena_ood_score',{'features':{'x':.1},'regime':regime})
            self.assertEqual(no_ref['status'],'NO_REFERENCE_DISTRIBUTION')
            for x in (-.2,-.1,0,.1,.2):
                srv.call_tool('athena_nonlinear_observe',{'features':{'x':x},'reward':x*x,'regime':regime,'arm_id':'A'})
            near=srv.call_tool('athena_ood_score',{'features':{'x':.1},'regime':regime})
            far=srv.call_tool('athena_ood_score',{'features':{'x':1.0},'regime':regime})
            self.assertLess(near['ood_score'],far['ood_score'])
            pred=srv.call_tool('athena_nonlinear_predict',{'features':{'x':.15},'regime':regime,'arm_id':'A'})
            self.assertEqual(pred['basis'],'POLYNOMIAL_DEGREE_2')
            self.assertIn('ood',pred)
            srv.store.close()

    def test_generated_experiment_and_backdoor_identification(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_experiment_generate',{
                'hypotheses':[
                    {'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},
                    {'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}},
                ],
                'factors':[{'name':'dose','levels':['low','high']}],
            })
            self.assertEqual(out['decision'],'DESIGN_ONLY')
            self.assertEqual(out['generated_count'],2)
            self.assertTrue(out['ranked_experiments'])
            ci=srv.call_tool('athena_causal_identify',{
                'treatment':'T','outcome':'Y',
                'edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],
                'observed_nodes':['T','Y','Z'],
            })
            self.assertEqual(ci['status'],'IDENTIFIED_BACKDOOR')
            self.assertIn(['Z'],ci['minimal_adjustment_sets'])
            srv.store.close()

    def test_higher_order_interaction(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[]
            for a in (0,1):
                for b in (0,1):
                    for c in (0,1):
                        active=[x for x,v in [('A',a),('B',b),('C',c)] if v]
                        rows.append({'interventions':active,'outcome':.1*a+.2*b+.3*c+.5*a*b*c})
            out=srv.call_tool('athena_interaction_higher_order',{'experiments':rows,'max_order':3,'design_confidence':1})
            term=next(x for x in out['interactions'] if x['term']=='A*B*C')
            self.assertAlmostEqual(term['effect'],.5,places=6)
            srv.store.close()

    def test_stochastic_transition_and_mpc_are_observation_bounded(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for before,after in [({'progress':0,'risk':.5},{'progress':.2,'risk':.4}),({'progress':.2,'risk':.4},{'progress':.5,'risk':.32})]:
                srv.call_tool('athena_transition_observe',{'action_id':'PACK','before':before,'after':after})
            dist=srv.call_tool('athena_transition_distribution',{'action_id':'PACK','context':{'progress':.5,'risk':.32}})
            self.assertEqual(dist['status'],'MODELED')
            self.assertIn('progress',dist['covariance'])
            before_n=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            plan=srv.call_tool('athena_mpc_plan',{'initial_context':{'progress':.5,'risk':.32},'actions':[{'id':'PACK','base_reward':.8},{'id':'UNSEEN','base_reward':.9}],'horizon':2})
            self.assertEqual(plan['decision'],'PLAN_ONLY')
            after_n=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            self.assertEqual(before_n,after_n)
            srv.store.close()

    def test_certified_schedule_and_capsule_boundary(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_schedule_certified',{
                'tasks':[{'id':'A','duration':1,'utility':1,'resource_cost':{'tokens':1},'required_capabilities':['x']},{'id':'B','duration':1,'utility':1,'dependencies':['A'],'resource_cost':{'tokens':1},'required_capabilities':['x']}],
                'workers':[{'id':'W','capabilities':['x']}],
                'budget':{'tokens':2},'horizon':3,
            })
            self.assertEqual(out['certificate'],'EXACT_ENUMERATION_CERTIFIED')
            self.assertEqual([x['task'] for x in out['schedule']],['A','B'])
            cap=srv.call_tool('athena_witness_capsule',{'regression_ref':'tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex'})
            self.assertIn(cap['status'],{'HERMETIC_UNAVAILABLE','PASS','FAIL','TIMEOUT'})
            if cap['status']=='HERMETIC_UNAVAILABLE': self.assertFalse(cap['executed'])
            if cap.get('executed'): self.assertTrue(cap['hermetic'])
            srv.store.close()

    def test_pareto_experiment_and_replication_graph(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_pareto_bandit_select',{'candidates':[
                {'id':'safe','metrics':{'quality':{'mean':.8,'sigma':.02},'cost':{'mean':.5,'sigma':.01}}},
                {'id':'uncertain','metrics':{'quality':{'mean':.82,'sigma':.2},'cost':{'mean':.45,'sigma':.1}}},
            ],'directions':{'quality':'max','cost':'min'}})
            self.assertEqual(out['decision'],'EXPERIMENT_SELECTION_ONLY')
            self.assertIn(out['selected'],out['possible_frontier'])
            claim=srv.call_tool('athena_claim_register',{'claim_key':'C1','statement':'A improves verified output'})
            for key in ('rep1','rep2'):
                srv.call_tool('athena_claim_witness',{'claim_id':claim['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':key})
            state=srv.call_tool('athena_claim_state',{'claim_id':claim['claim_id']})
            self.assertEqual(state['status'],'REPLICATED_SUPPORT')
            srv.call_tool('athena_claim_witness',{'claim_id':claim['claim_id'],'kind':'FALSIFIER','result':'FALSIFIES','independence_key':'redteam'})
            self.assertEqual(srv.call_tool('athena_claim_state',{'claim_id':claim['claim_id']})['status'],'CONTESTED')
            srv.store.close()

    def test_v6_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_ood_score','athena_experiment_generate','athena_causal_identify','athena_mpc_plan','athena_schedule_certified','athena_claim_state'):
                self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
