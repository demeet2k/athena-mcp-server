import json
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV13UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result'];self.assertFalse(r.get('isError'),r);return r['structuredContent']

    def _gp(self):
        self.tool('athena_gp_register',{'context_key':'G13U','features':['x'],'length_scale':.8,'signal_variance':1.0,'noise_variance':.04})
        for i,x in enumerate((-.9,-.6,-.3,0,.3,.6,.9)):self.tool('athena_gp_observe',{'context_key':'G13U','features':{'x':x},'target':x*x,'evidence_ref':f'test://{i}'})

    def test_v13_resource_names_bounded_runtime_and_trust_firewall(self):
        payload=self.rpc('resources/read',{'uri':'athena://collective/v13'})['result']['contents'][0]['text']
        self.assertIn('COLLECTIVE_RUNTIME_V13',payload)
        self.assertIn('Y1 authority',payload)
        self.assertIn('exact continuous Bayes',payload)
        self.assertIn('full FCI/RFCI',payload)
        self.assertIn('trusted promotion verification',payload)

    def test_v13_model_outputs_cannot_mutate_gp_y1_or_jspace(self):
        self._gp();self.tool('athena_claim_register',{'claim_id':'Y.V13','source_ref':'test://v13'})
        before_gp=self.tool('athena_gp_state',{'context_key':'G13U'});before_claim=self.tool('athena_claim_state',{'claim_id':'Y.V13'});before_edges=len(self.server.store.rows('SELECT * FROM edges'))
        self.tool('athena_gp_hyperqmc',{'context_key':'G13U','samples':40})
        self.tool('athena_gp_fitc_predict',{'context_key':'G13U','features':{'x':.2},'inducing_count':3})
        self.tool('athena_gp_joint_design',{'context_key':'G13U','actions':[{'id':'a','features':{'x':-.5}},{'id':'b','features':{'x':.5}}],'experiments':[{'id':'e','features':{'x':0}}],'hyper_samples':40,'mc_samples':80})
        rows=[]
        for i in range(80):rows.append({'X':i/80,'Y':((i*17)%79)/79,'Z':((i*31)%83)/83})
        self.tool('athena_fci_lite_discover',{'samples':rows,'variables':['X','Y','Z'],'max_conditioning':1})
        items=[{'id':'A','value':1,'resources':{'tokens':{'mean':1,'mean_uncertainty':.1}}}]
        self.tool('athena_dro_resource_select',{'candidates':items,'budgets':{'tokens':2},'covariances':{'tokens':[[.01]]},'ambiguity_radius':1})
        after_gp=self.tool('athena_gp_state',{'context_key':'G13U'});after_claim=self.tool('athena_claim_state',{'claim_id':'Y.V13'});after_edges=len(self.server.store.rows('SELECT * FROM edges'))
        self.assertEqual(before_gp['observation_count'],after_gp['observation_count']);self.assertEqual(before_gp['length_scale'],after_gp['length_scale'])
        self.assertEqual(before_edges,after_edges);self.assertEqual(before_claim['y'],after_claim['y']);self.assertEqual(before_claim['status'],after_claim['status']);self.assertEqual(after_claim['y'],'?')

    def test_surface_contract_requires_v13_and_promotion_schema_keeps_trusted_field_private(self):
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['collective_v13']['status'],'PASS',audit);self.assertTrue(audit['promotion_ready_locally'])
        tools={x['name']:x for x in self.rpc('tools/list')['result']['tools']}
        promo=tools['athena_promotion_evaluate']['inputSchema'];self.assertFalse(promo.get('additionalProperties',True));self.assertNotIn('trusted_external_verification',promo['properties'])
        self.assertIn('athena_gp_hyperqmc',tools);self.assertIn('athena_dro_resource_select',tools)


if __name__=='__main__':unittest.main()
