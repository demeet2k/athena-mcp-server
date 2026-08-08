import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV11UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_v11_tools_resource_and_surface_are_advertised(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']};uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']}
        for n in ('athena_gp_hyperfit','athena_gp_decision_evsi','athena_latent_project_admg','athena_causal_tmle_ensemble','athena_sensitivity_rr_surface','athena_bapomdp_solve','athena_evidence_dependence_interval'):
            self.assertIn(n,names)
        self.assertIn('athena://collective/v11',uris)
        payload=self.rpc('resources/read',{'uri':'athena://collective/v11'})['result']['contents'][0]['text']
        self.assertIn('COLLECTIVE_RUNTIME_V11',payload);self.assertIn('Y1 authority',payload)
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['collective_v11']['status'],'PASS')

    def test_gp_hyperfit_and_evsi_are_design_reads_unless_explicit_cas_apply(self):
        self.tool('athena_gp_register',{'context_key':'G11','features':['x'],'length_scale':1.0,'signal_variance':1.0,'noise_variance':.05})
        for x,y in ((0.0,0.0),(0.5,.4),(1.0,1.0)):self.tool('athena_gp_observe',{'context_key':'G11','features':{'x':x},'target':y})
        before=self.tool('athena_gp_state',{'context_key':'G11'})
        fit=self.tool('athena_gp_hyperfit',{'context_key':'G11','length_scales':[.4,1.0],'signal_variances':[.7,1.0],'noise_variances':[.02,.05],'apply':False})
        self.assertEqual(fit['status'],'GP_HYPERPARAMETER_DESIGN_ONLY')
        after_fit=self.tool('athena_gp_state',{'context_key':'G11'});self.assertEqual(before,after_fit)
        evsi=self.tool('athena_gp_decision_evsi',{'context_key':'G11','actions':[{'id':'a','features':{'x':0.0}},{'id':'b','features':{'x':1.0}}],'experiments':[{'id':'e','features':{'x':.5},'noise_variance':.03}],'samples':60,'seed':2,'cost_weight':0,'risk_weight':0})
        self.assertEqual(evsi['decision'],'GP_DECISION_EVSI_DESIGN_ONLY');self.assertEqual(before['observation_count'],self.tool('athena_gp_state',{'context_key':'G11'})['observation_count'])

    def test_latent_projection_and_bapomdp_do_not_mutate_canonical_state(self):
        before_edges=len(self.server.store.rows('SELECT * FROM edges'))
        proj=self.tool('athena_latent_project_admg',{'edges':[{'src':'L','dst':'X'},{'src':'L','dst':'Y'},{'src':'X','dst':'Y'}],'latent_nodes':['L'],'observed_nodes':['X','Y']})
        self.assertEqual(proj['status'],'RESTRICTED_LATENT_PROJECTION_ADMG');self.assertEqual(before_edges,len(self.server.store.rows('SELECT * FROM edges')))
        def acts(model):
            probe={'x':.9,'y':.1} if model=='M1' else {'x':.1,'y':.9};left=.6 if model=='M1' else 0.0;right=0.0 if model=='M1' else .6
            return [
                {'id':'left','reward_by_state':{'S':left},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
                {'id':'right','reward_by_state':{'S':right},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
                {'id':'probe','reward_by_state':{'S':0.0},'transition':{'S':{'S':1.0}},'observation':{'S':probe}},
            ]
        plan=self.tool('athena_bapomdp_solve',{'states':['S'],'initial_state_belief':{'S':1.0},'models':[{'id':'M1','prior':.5,'actions':acts('M1')},{'id':'M2','prior':.5,'actions':acts('M2')}],'horizon':2,'max_nodes':10000})
        self.assertEqual(plan['status'],'FINITE_MODEL_BAYES_ADAPTIVE_POMDP_EXACT_HORIZON_CERTIFIED')
        self.assertEqual(plan['certificate'],'EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON')

    def test_v11_dependence_interval_and_causal_read_do_not_change_y1(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.Y1.V11','source_ref':'source://canonical'})
        for i in range(40):self.tool('athena_evidence_dependence_observe',{'scope':'V11','features':{'same_dataset':float(i%2)},'label':i%2})
        self.tool('athena_evidence_dependence_fit',{'scope':'V11','iterations':500})
        before=self.server.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_observations WHERE scope='V11'")['n']
        interval=self.tool('athena_evidence_dependence_interval',{'scope':'V11','features':{'same_dataset':1.0}});self.assertEqual(interval['status'],'LOGISTIC_DEPENDENCE_LAPLACE_INTERVAL')
        after=self.server.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_observations WHERE scope='V11'")['n'];self.assertEqual(before,after)
        rows=[{'T':i%2,'Y':(i//2)%2,'X':i/80} for i in range(80)]
        blocked=self.tool('athena_causal_tmle_ensemble',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X'],'assumptions':{'latent_confounding_possible':True}});self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
        y1=self.tool('athena_claim_state',{'claim_id':'CLAIM.Y1.V11'});self.assertEqual(y1['y'],'?');self.assertEqual(y1['status'],'ACTIVE')


if __name__=='__main__':unittest.main()
