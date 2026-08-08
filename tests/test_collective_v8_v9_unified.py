import json
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV8V9UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']
    def resource(self,uri):return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])

    def test_v8_v9_tools_resources_and_surface_are_advertised(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']};uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']}
        for n in ('athena_belief_register','athena_decision_evi','athena_evidence_spectral','athena_gaussian_belief_register','athena_decision_evpi','athena_decision_evsi','athena_causal_aipw','athena_structure_partial','athena_evidence_dependence_probability'):
            self.assertIn(n,names)
        self.assertIn('athena://collective/v8',uris);self.assertIn('athena://collective/v9',uris)
        self.assertEqual(self.resource('athena://collective/v8')['runtime']['version'],'COLLECTIVE_RUNTIME_V8')
        self.assertEqual(self.resource('athena://collective/v9')['runtime']['version'],'COLLECTIVE_RUNTIME_V9')
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['collective_v8']['status'],'PASS');self.assertEqual(audit['groups']['collective_v9']['status'],'PASS')

    def test_v8_design_and_v9_value_reads_do_not_self_update_beliefs(self):
        self.tool('athena_belief_register',{'context_key':'B','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]})
        before=self.tool('athena_belief_state',{'context_key':'B'})
        actions=[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}]
        exp={'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}
        self.tool('athena_decision_evi',{'context_key':'B','actions':actions,'experiments':[exp]})
        self.tool('athena_contingent_policy',{'context_key':'B','actions':actions,'experiment':exp})
        after=self.tool('athena_belief_state',{'context_key':'B'});self.assertEqual(before['models'],after['models'])
        self.tool('athena_gaussian_belief_register',{'context_key':'G','parameters':['theta'],'prior_variance':2.0,'noise_variance':.5})
        gbefore=self.tool('athena_gaussian_belief_state',{'context_key':'G'});ga=[{'id':'p','utility_linear':{'theta':1}},{'id':'m','utility_linear':{'theta':-1}}]
        self.tool('athena_decision_evpi',{'context_key':'G','actions':ga,'samples':60,'seed':1})
        self.tool('athena_decision_evsi',{'context_key':'G','actions':ga,'experiments':[{'id':'e','design':{'theta':1},'noise_variance':.2}],'samples':60,'seed':1,'cost_weight':0,'risk_weight':0})
        gafter=self.tool('athena_gaussian_belief_state',{'context_key':'G'});self.assertEqual(gbefore['observation_count'],gafter['observation_count']);self.assertEqual(gbefore['mean'],gafter['mean'])

    def test_v8_v9_evidence_geometry_is_shadow_only_and_y1_is_unchanged(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.Y1.V89','source_ref':'source://canonical'})
        shadow=self.tool('athena_discovery_claim_register',{'claim_key':'shadow:v89','statement':'replication target'})
        for k,d in (('r1','D1'),('r2','D1'),('r3','D2')):
            self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k,'confidence':.9,'evidence':{'dataset':d,'implementation':'same','method':'same'}})
        spectral=self.tool('athena_evidence_spectral',{'claim_id':shadow['claim_id']});self.assertGreaterEqual(spectral['effective_n'],1.0);self.assertIn('spectral_participation_ratio',spectral)
        dep=self.tool('athena_evidence_dependence_probability',{'claim_id':shadow['claim_id'],'coefficients':{'bias':-1,'match':1.5,'different':-.5}});self.assertEqual(dep['status'],'DECLARED_METADATA_DEPENDENCE_MODEL')
        y1=self.tool('athena_claim_state',{'claim_id':'CLAIM.Y1.V89'});self.assertEqual(y1['y'],'?');self.assertEqual(y1['status'],'ACTIVE')

    def test_v8_v9_graph_and_causal_surfaces_fail_closed_without_canonical_mutation(self):
        before=len(self.server.core.s.rows('SELECT * FROM edges'))
        rows=[{'X':i/35,'Y':2*i/35+((i%3)-1)*.01,'Z':((i*11)%17)/17} for i in range(35)]
        pg=self.tool('athena_structure_partial',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.4,'resamples':10,'support_threshold':.5,'seed':4})
        self.assertEqual(pg['status'],'HEURISTIC_PARTIAL_GRAPH');self.assertEqual(before,len(self.server.core.s.rows('SELECT * FROM edges')))
        causal=[{'T':i%2,'Y':2*(i%2)+.1*i,'Z':i/30} for i in range(30)]
        blocked=self.tool('athena_causal_aipw',{'samples':causal,'treatment':'T','outcome':'Y','adjustment':['Z'],'assumptions':{'latent_confounding_possible':True}})
        self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')


if __name__=='__main__':unittest.main()
