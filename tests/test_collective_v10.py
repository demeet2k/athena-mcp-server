import math
import random
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV10Tests(unittest.TestCase):
    def test_gp_posterior_and_no_self_training(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_gp_register',{'context_key':'GP','features':['x'],'length_scale':.6,'signal_variance':1.0,'noise_variance':.01})
            prior=srv.call_tool('athena_gp_predict',{'context_key':'GP','features':{'x':1.0},'include_observation_noise':False})
            self.assertEqual(prior['observation_count'],0)
            for x,y in ((0.0,0.0),(1.0,1.0),(2.0,0.0)):
                srv.call_tool('athena_gp_observe',{'context_key':'GP','features':{'x':x},'target':y})
            post=srv.call_tool('athena_gp_predict',{'context_key':'GP','features':{'x':1.0},'include_observation_noise':False})
            self.assertEqual(post['status'],'GP_POSTERIOR_PREDICTION')
            self.assertGreater(post['mean'],.8)
            self.assertLess(post['latent_variance'],prior['latent_variance'])
            after=srv.call_tool('athena_gp_state',{'context_key':'GP'})
            self.assertEqual(after['observation_count'],3)
            srv.store.close()

    def test_pc_stable_collider(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rng=random.Random(7); rows=[]
            for _ in range(400):
                x=rng.gauss(0,1); y=rng.gauss(0,1); z=1.2*x+1.1*y+rng.gauss(0,.15)
                rows.append({'X':x,'Y':y,'Z':z})
            out=srv.call_tool('athena_pc_stable_discover',{'samples':rows,'variables':['X','Y','Z'],'alpha':.01,'max_conditioning':1})
            self.assertEqual(out['status'],'PC_STABLE_BOUNDED_PARTIAL_GRAPH')
            directed={(e['src'],e['dst']) for e in out['directed_edges']}
            self.assertIn(('X','Z'),directed)
            self.assertIn(('Y','Z'),directed)
            self.assertFalse(any(set((e['a'],e['b']))=={'X','Y'} for e in out['undirected_edges']))
            srv.store.close()

    def test_tmle_and_evalue(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rng=random.Random(13); rows=[]
            for i in range(1200):
                x=rng.uniform(-1,1)
                p_t=1/(1+math.exp(-(.8*x)))
                t=1 if rng.random()<p_t else 0
                p_y=max(.02,min(.98,.2+.45*t+.10*x))
                y=1 if rng.random()<p_y else 0
                rows.append({'T':t,'Y':y,'X':x})
            tm=srv.call_tool('athena_causal_tmle_binary',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X'],'propensity_clip':.05})
            self.assertEqual(tm['status'],'TMLE_BINARY_ESTIMATED_UNDER_ASSUMPTIONS')
            self.assertGreater(tm['estimate'],.25)
            self.assertLess(tm['estimate'],.65)
            self.assertGreater(tm['standard_error'],0)
            self.assertLess(tm['ci95'][0],tm['ci95'][1])
            ev=srv.call_tool('athena_sensitivity_evalue',{'risk_ratio':2.0,'ci_limit':1.5})
            self.assertAlmostEqual(ev['evalue_point'],2+math.sqrt(2),places=6)
            self.assertGreater(ev['evalue_ci_limit'],1)
            srv.store.close()

    def test_finite_pomdp_certificate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            states=['G','B']
            actions=[
                {'id':'act','reward_by_state':{'G':1.0,'B':0.0},
                 'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},
                 'observation':{'G':{'n':1.0},'B':{'n':1.0}}},
                {'id':'safe','reward_by_state':{'G':.4,'B':.4},
                 'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},
                 'observation':{'G':{'n':1.0},'B':{'n':1.0}}},
                {'id':'sense','reward_by_state':{'G':0.0,'B':0.0},
                 'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},
                 'observation':{'G':{'g':.9,'b':.1},'B':{'g':.1,'b':.9}}},
            ]
            out=srv.call_tool('athena_pomdp_solve',{'states':states,'initial_belief':{'G':.5,'B':.5},'actions':actions,'horizon':2,'discount':.95,'max_nodes':5000})
            self.assertEqual(out['status'],'FINITE_POMDP_EXACT_HORIZON_CERTIFIED')
            self.assertEqual(out['certificate'],'EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON')
            self.assertIn(out['selected'],{'act','safe','sense'})
            self.assertGreater(out['nodes_expanded'],0)
            srv.store.close()

    def test_dependence_calibration_and_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for i in range(60):
                same=1.0 if i%2 else 0.0
                method=1.0 if i%3 else 0.0
                label=1 if same==1.0 else 0
                srv.call_tool('athena_evidence_dependence_observe',{'scope':'R','features':{'same_dataset':same,'same_method':method},'label':label})
            fit=srv.call_tool('athena_evidence_dependence_fit',{'scope':'R','iterations':700})
            self.assertEqual(fit['status'],'EMPIRICAL_LOGISTIC_DEPENDENCE_MODEL')
            hi=srv.call_tool('athena_evidence_dependence_predict',{'scope':'R','features':{'same_dataset':1.0,'same_method':1.0}})
            lo=srv.call_tool('athena_evidence_dependence_predict',{'scope':'R','features':{'same_dataset':0.0,'same_method':0.0}})
            self.assertGreater(hi['probability'],lo['probability'])
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_sensitivity_evalue','athena_pomdp_solve','athena_evidence_dependence_fit'):
                self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
