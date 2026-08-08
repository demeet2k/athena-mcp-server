import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV6AdversarialTests(unittest.TestCase):
    def test_ood_does_not_train_and_unseen_features_raise_pressure(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for _ in range(4): srv.call_tool('athena_ood_observe',{'features':{'x':0},'regime':'R'})
            before=srv.store.one("SELECT n FROM collective_v6_ood_models WHERE scope='global' AND regime='R'")['n']
            out=srv.call_tool('athena_ood_score',{'features':{'x':0,'novel':1},'regime':'R'})
            after=srv.store.one("SELECT n FROM collective_v6_ood_models WHERE scope='global' AND regime='R'")['n']
            self.assertEqual(before,after)
            self.assertIn('novel',out['unseen_features'])
            self.assertGreater(out['ood_score'],0)
            srv.store.close()

    def test_generated_experiments_respect_forbidden_levels(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_experiment_generate',{
                'hypotheses':[{'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},{'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}}],
                'factors':[{'name':'dose','levels':['low','high'],'forbidden_levels':['high']}],
            })
            blocked=[x for x in out['ranked_experiments'] if x['id'].endswith('dose=high')]
            self.assertTrue(blocked)
            self.assertEqual(blocked[0]['status'],'ETHICS_BLOCK')
            srv.store.close()

    def test_causal_identification_fails_closed_on_latent_confounding_flag(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'T','dst':'Y'}],'assumptions':{'latent_confounding_possible':True}})
            self.assertEqual(out['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            self.assertEqual(out['minimal_adjustment_sets'],[])
            srv.store.close()

    def test_missing_higher_order_cell_remains_unidentified(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[]
            for a in (0,1):
                for b in (0,1):
                    for c in (0,1):
                        if (a,b,c)==(1,1,1): continue
                        rows.append({'interventions':[x for x,v in [('A',a),('B',b),('C',c)] if v],'outcome':a+b+c})
            out=srv.call_tool('athena_interaction_higher_order',{'experiments':rows,'max_order':3})
            term=next(x for x in out['interactions'] if x['term']=='A*B*C')
            self.assertEqual(term['status'],'UNIDENTIFIED')
            self.assertIsNone(term['effect'])
            srv.store.close()

    def test_unseen_transition_mpc_does_not_fabricate_or_train(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            dist=srv.call_tool('athena_transition_distribution',{'action_id':'NEVER','context':{'x':1}})
            self.assertEqual(dist['status'],'UNSEEN_ACTION')
            self.assertEqual(dist['mean_delta'],{})
            before=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            for _ in range(3): srv.call_tool('athena_mpc_plan',{'initial_context':{'x':1},'actions':[{'id':'NEVER','base_reward':.9}],'horizon':3})
            after=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            self.assertEqual(before,after)
            srv.store.close()

    def test_certified_scheduler_does_not_certify_large_search(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            tasks=[{'id':f'T{i}','duration':1,'utility':1} for i in range(9)]
            out=srv.call_tool('athena_schedule_certified',{'tasks':tasks,'workers':[{'id':'W'}],'exact_task_limit':8})
            self.assertEqual(out['certificate'],'NONE')
            srv.store.close()

    def test_witness_capsule_never_silently_falls_back(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            bad=srv.call_tool('athena_witness_capsule',{'regression_ref':'../../escape.py::X::test_y'})
            self.assertIn(bad['status'],{'HERMETIC_UNAVAILABLE','INVALID_REF'})
            if bad['status']=='HERMETIC_UNAVAILABLE': self.assertFalse(bad['executed'])
            srv.store.close()

    def test_claim_falsifier_never_changes_canonical_registry(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            before=srv.store.one('SELECT COUNT(*) AS n FROM objects')['n']
            claim=srv.call_tool('athena_claim_register',{'claim_key':'shadow','statement':'shadow claim'})
            srv.call_tool('athena_claim_witness',{'claim_id':claim['claim_id'],'kind':'FALSIFIER','result':'FALSIFIES','independence_key':'r1'})
            state=srv.call_tool('athena_claim_state',{'claim_id':claim['claim_id']})
            after=srv.store.one('SELECT COUNT(*) AS n FROM objects')['n']
            self.assertEqual(state['status'],'FALSIFICATION_SIGNAL')
            self.assertEqual(before,after)
            srv.store.close()


if __name__=='__main__': unittest.main()
