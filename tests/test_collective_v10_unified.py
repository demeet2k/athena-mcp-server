import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV10UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_v10_tools_resource_and_surface_are_advertised(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']};uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']}
        for n in ('athena_gp_register','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_sensitivity_evalue','athena_pomdp_solve','athena_evidence_dependence_observe','athena_evidence_dependence_fit','athena_evidence_dependence_predict'):
            self.assertIn(n,names)
        self.assertIn('athena://collective/v10',uris)
        payload=self.rpc('resources/read',{'uri':'athena://collective/v10'})['result']['contents'][0]['text']
        self.assertIn('COLLECTIVE_RUNTIME_V10',payload);self.assertIn('model/assumption scoped',payload)
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['collective_v10']['status'],'PASS')

    def test_gp_prediction_and_pc_discovery_do_not_self_mutate(self):
        self.tool('athena_gp_register',{'context_key':'G','features':['x']})
        for _ in range(4):self.tool('athena_gp_predict',{'context_key':'G','features':{'x':.2}})
        self.assertEqual(self.tool('athena_gp_state',{'context_key':'G'})['observation_count'],0)
        rows=[{'X':i/40,'Y':2*i/40,'Z':((i*13)%17)/17} for i in range(40)]
        before=len(self.server.store.rows('SELECT * FROM edges'))
        graph=self.tool('athena_pc_stable_discover',{'samples':rows,'variables':['X','Y','Z'],'alpha':.05,'max_conditioning':1})
        self.assertEqual(graph['status'],'PC_STABLE_BOUNDED_PARTIAL_GRAPH');self.assertEqual(before,len(self.server.store.rows('SELECT * FROM edges')))

    def test_tmle_and_pomdp_keep_assumption_and_execution_boundaries(self):
        rows=[{'T':i%2,'Y':(i//2)%2,'X':i/80} for i in range(80)]
        blocked=self.tool('athena_causal_tmle_binary',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X'],'assumptions':{'latent_confounding_possible':True}})
        self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
        states=['G','B'];actions=[{'id':'safe','reward_by_state':{'G':.4,'B':.4},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'n':1.0},'B':{'n':1.0}}}]
        plan=self.tool('athena_pomdp_solve',{'states':states,'initial_belief':{'G':.5,'B':.5},'actions':actions,'horizon':2,'max_nodes':5000})
        self.assertEqual(plan['certificate'],'EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON');self.assertIn('supplied finite model',plan['law'])

    def test_dependence_calibration_is_model_state_not_y1_authority(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.Y1.V10','source_ref':'source://canonical'})
        for i in range(30):self.tool('athena_evidence_dependence_observe',{'scope':'S','features':{'same_dataset':float(i%2)},'label':i%2})
        fit=self.tool('athena_evidence_dependence_fit',{'scope':'S','iterations':500});self.assertEqual(fit['status'],'EMPIRICAL_LOGISTIC_DEPENDENCE_MODEL')
        pred=self.tool('athena_evidence_dependence_predict',{'scope':'S','features':{'same_dataset':1.0}});self.assertIn('probability',pred)
        y1=self.tool('athena_claim_state',{'claim_id':'CLAIM.Y1.V10'});self.assertEqual(y1['y'],'?');self.assertEqual(y1['status'],'ACTIVE')


if __name__=='__main__':unittest.main()
