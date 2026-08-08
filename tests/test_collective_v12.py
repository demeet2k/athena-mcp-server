import math
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV12Tests(unittest.TestCase):
    def _gp(self,srv):
        srv.call_tool('athena_gp_register',{'context_key':'G12','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.03})
        for i,x in enumerate((-1.0,-.7,-.3,0.0,.3,.7,1.0)):
            srv.call_tool('athena_gp_observe',{'context_key':'G12','features':{'x':x},'target':x*x+.05*math.sin(i),'evidence_ref':f'test://{i}'})

    def test_gp_hyperposterior_bma_and_sparse(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._gp(srv)
            hp=srv.call_tool('athena_gp_hyperposterior',{'context_key':'G12','candidates':[
                {'length_scale':.35,'signal_variance':1.0,'noise_variance':.03,'prior':1.0},
                {'length_scale':.7,'signal_variance':1.0,'noise_variance':.03,'prior':1.0},
                {'length_scale':1.4,'signal_variance':1.0,'noise_variance':.03,'prior':1.0},
            ]})
            self.assertEqual(hp['status'],'FINITE_GRID_GP_HYPERPOSTERIOR')
            self.assertAlmostEqual(sum(x['posterior_weight'] for x in hp['posterior']),1.0,places=8)
            self.assertGreaterEqual(hp['effective_model_count'],1.0)
            bma=srv.call_tool('athena_gp_bma_predict',{'context_key':'G12','features':{'x':.5},'candidates':hp['posterior']})
            self.assertEqual(bma['status'],'FINITE_GRID_GP_BAYESIAN_MODEL_AVERAGE')
            self.assertGreaterEqual(bma['predictive_variance'],bma['within_model_variance'])
            sp=srv.call_tool('athena_gp_sparse_predict',{'context_key':'G12','features':{'x':.5},'inducing_count':3})
            self.assertEqual(sp['status'],'SUBSET_OF_DATA_GP_APPROXIMATION')
            self.assertEqual(sp['inducing_count'],3)
            self.assertGreaterEqual(sp['exact_reference']['absolute_mean_error'],0.0)
            srv.store.close()

    def test_bma_gp_evsi_is_decision_valued(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._gp(srv)
            before=srv.call_tool('athena_gp_state',{'context_key':'G12'})['observation_count']
            out=srv.call_tool('athena_gp_bma_decision_evsi',{
                'context_key':'G12',
                'actions':[{'id':'left','features':{'x':-.9},'utility_scale':1},{'id':'right','features':{'x':.9},'utility_scale':1}],
                'experiments':[{'id':'center','features':{'x':0.0},'noise_variance':.02},{'id':'edge','features':{'x':.8},'noise_variance':.02}],
                'samples':80,'seed':11,'cost_weight':0,'risk_weight':0,
            })
            self.assertEqual(out['decision'],'FINITE_GRID_BMA_GP_EVSI_DESIGN_ONLY')
            self.assertIn(out['winner'],{'center','edge'})
            self.assertEqual(before,srv.call_tool('athena_gp_state',{'context_key':'G12'})['observation_count'])
            srv.store.close()

    def test_pag_candidate_marks_collider(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rows=[]
            for i in range(240):
                x=((i*17)%101)/50.0-1.0; y=((i*43)%103)/51.0-1.0; noise=((i*29)%17-8)/500.0
                rows.append({'X':x,'Y':y,'Z':1.1*x-.9*y+noise})
            out=srv.call_tool('athena_pag_candidate_discover',{'samples':rows,'variables':['X','Y','Z'],'alpha':.01,'max_conditioning':1})
            self.assertEqual(out['status'],'BOUNDED_PAG_CANDIDATE')
            self.assertTrue(any(c['middle']=='Z' for c in out['collider_candidates']))
            self.assertTrue(any(e['endpoint_b']=='arrowhead' or e['endpoint_a']=='arrowhead' for e in out['edges']))
            srv.store.close()

    def test_longitudinal_gformula_orders_regimes(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rows=[]
            for i in range(240):
                x=((i*13)%101)/100.0-.5; a1=i%2
                pl=max(.05,min(.95,.25+.35*a1+.2*x)); l1=1 if ((i*37)%100)/100.0<pl else 0
                a2=1 if (i%4 in (1,2)) else 0
                py=max(.03,min(.97,.08+.12*a1+.18*l1+.42*a2+.08*x)); y=1 if ((i*53)%100)/100.0<py else 0
                rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
            out=srv.call_tool('athena_longitudinal_gformula',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']})
            self.assertEqual(out['status'],'TWO_TIMEPOINT_PARAMETRIC_GFORMULA_ESTIMATED_UNDER_ASSUMPTIONS')
            risks={(r['a1'],r['a2']):r['estimated_risk'] for r in out['regimes']}
            self.assertGreater(risks[(1,1)],risks[(0,0)])
            self.assertGreater(out['risk_contrast'],0)
            srv.store.close()

    def test_exact_chance_resource_certificate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_chance_resource_select',{'candidates':[
                {'id':'A','value':5,'resources':{'tokens':{'mean':4,'std':.2}}},
                {'id':'B','value':4,'resources':{'tokens':{'mean':3,'std':.2}}},
                {'id':'C','value':2,'resources':{'tokens':{'mean':2,'std':.1}}},
            ],'budgets':{'tokens':8},'alpha':.05})
            self.assertEqual(out['status'],'CHANCE_CONSTRAINED_EXACT_ENUMERATION_CERTIFIED')
            self.assertEqual(out['certificate'],'EXACT_ENUMERATION_UNDER_DECLARED_INDEPENDENT_GAUSSIAN_RESOURCE_MODEL')
            self.assertEqual(set(out['selected']),{'A','B'})
            srv.store.close()

    def test_v12_tools_are_exposed(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for n in ('athena_gp_hyperposterior','athena_gp_bma_predict','athena_gp_sparse_predict','athena_gp_bma_decision_evsi','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_chance_resource_select'):
                self.assertIn(n,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
