import math
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV11Tests(unittest.TestCase):
    def test_gp_hyperfit_apply_and_decision_evsi(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_gp_register',{'context_key':'G11','features':['x'],'length_scale':4.0,'signal_variance':.25,'noise_variance':.2})
            for x,y in [(-1.0,1.0),(-.5,.25),(0.0,0.0),(.5,.25),(1.0,1.0)]:
                srv.call_tool('athena_gp_observe',{'context_key':'G11','features':{'x':x},'target':y})
            before=srv.call_tool('athena_gp_state',{'context_key':'G11'})
            fit=srv.call_tool('athena_gp_hyperfit',{'context_key':'G11','length_scales':[.25,.5,1.0,2.0],'signal_variances':[.25,1.0,2.0],'noise_variances':[.01,.05,.2]})
            self.assertEqual(fit['status'],'GP_HYPERPARAMETER_DESIGN_ONLY')
            self.assertEqual(srv.call_tool('athena_gp_state',{'context_key':'G11'})['length_scale'],before['length_scale'])
            applied=srv.call_tool('athena_gp_hyperfit',{'context_key':'G11','length_scales':[.25,.5,1.0,2.0],'signal_variances':[.25,1.0,2.0],'noise_variances':[.01,.05,.2],'apply':True,'expected_observation_count':5})
            self.assertEqual(applied['status'],'GP_HYPERPARAMETERS_APPLIED')
            st=srv.call_tool('athena_gp_state',{'context_key':'G11'})
            self.assertAlmostEqual(st['length_scale'],applied['best']['length_scale'])
            evsi=srv.call_tool('athena_gp_decision_evsi',{
                'context_key':'G11',
                'actions':[{'id':'left','features':{'x':-.8}},{'id':'right','features':{'x':.8}}],
                'experiments':[{'id':'center','features':{'x':0.0},'noise_variance':.01},{'id':'edge','features':{'x':.8},'noise_variance':.01}],
                'samples':100,'seed':11,'cost_weight':0,'risk_weight':0,
            })
            self.assertEqual(evsi['decision'],'GP_DECISION_EVSI_DESIGN_ONLY')
            self.assertEqual(len(evsi['ranked']),2)
            self.assertTrue(all(r['evsi']>=0 for r in evsi['ranked']))
            srv.store.close()

    def test_latent_projection_admg(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_latent_project_admg',{
                'edges':[{'src':'U','dst':'X'},{'src':'U','dst':'Y'},{'src':'X','dst':'Z'}],
                'latent_nodes':['U'], 'observed_nodes':['X','Y','Z'],
            })
            self.assertEqual(out['status'],'RESTRICTED_LATENT_PROJECTION_ADMG')
            self.assertTrue(any(e['a']=='X' and e['b']=='Y' for e in out['bidirected_edges']))
            self.assertTrue(any(e['src']=='X' and e['dst']=='Z' for e in out['directed_edges']))
            srv.store.close()

    def test_stacked_tmle_and_rr_sensitivity_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[]
            for i in range(160):
                x=(i%20)/19.0; t=i%2; u=((i*7)%17)/17.0
                p=min(.95,max(.05,.12+.48*t+.22*x*x))
                y=1 if u<p else 0
                rows.append({'T':t,'Y':y,'X':x})
            tmle=srv.call_tool('athena_causal_tmle_ensemble',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X']})
            self.assertEqual(tmle['status'],'TMLE_STACKED_ENSEMBLE_ESTIMATED_UNDER_ASSUMPTIONS')
            self.assertTrue(math.isfinite(tmle['estimate']))
            self.assertGreater(tmle['estimate'],0.05)
            self.assertEqual(len(tmle['libraries']),2)
            sens=srv.call_tool('athena_sensitivity_rr_surface',{'observed_rr':2.0,'exposure_confounder_rrs':[1.0,2.0,3.5],'outcome_confounder_rrs':[1.0,2.0,3.5]})
            self.assertEqual(sens['status'],'RR_BIAS_FACTOR_SENSITIVITY_SURFACE')
            self.assertEqual(sens['pair_count'],9)
            self.assertIsNotNone(sens['minimum_grid_explain_away'])
            srv.store.close()

    def test_exact_finite_model_bapomdp_prefers_information(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            def acts(model):
                if model=='M1':
                    probe={'x':.9,'y':.1}; left=.6; right=0.0
                else:
                    probe={'x':.1,'y':.9}; left=0.0; right=.6
                return [
                    {'id':'left','reward_by_state':{'S':left},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
                    {'id':'right','reward_by_state':{'S':right},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
                    {'id':'probe','reward_by_state':{'S':0.0},'transition':{'S':{'S':1.0}},'observation':{'S':probe}},
                ]
            out=srv.call_tool('athena_bapomdp_solve',{
                'states':['S'],'initial_state_belief':{'S':1.0},
                'models':[{'id':'M1','prior':.5,'actions':acts('M1')},{'id':'M2','prior':.5,'actions':acts('M2')}],
                'horizon':3,'discount':.95,'max_nodes':100000,
            })
            self.assertEqual(out['status'],'FINITE_MODEL_BAYES_ADAPTIVE_POMDP_EXACT_HORIZON_CERTIFIED')
            self.assertEqual(out['certificate'],'EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON')
            self.assertEqual(out['selected'],'probe')
            srv.store.close()

    def test_dependence_interval_and_mcp_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for i in range(40):
                same=float(i%2); other=float((i//2)%2); label=1 if same==1.0 else 0
                srv.call_tool('athena_evidence_dependence_observe',{'scope':'V11D','features':{'same':same,'other':other},'label':label})
            srv.call_tool('athena_evidence_dependence_fit',{'scope':'V11D'})
            ci=srv.call_tool('athena_evidence_dependence_interval',{'scope':'V11D','features':{'same':1.0,'other':0.0}})
            self.assertEqual(ci['status'],'LOGISTIC_DEPENDENCE_LAPLACE_INTERVAL')
            self.assertLessEqual(ci['interval'][0],ci['probability'])
            self.assertGreaterEqual(ci['interval'][1],ci['probability'])
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_gp_hyperfit','athena_gp_decision_evsi','athena_latent_project_admg','athena_causal_tmle_ensemble','athena_sensitivity_rr_surface','athena_bapomdp_solve','athena_evidence_dependence_interval'):
                self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
