import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV12UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result'];self.assertFalse(r.get('isError'),r);return r['structuredContent']

    def test_v12_resource_is_joint_runtime_and_keeps_y1_firewall(self):
        payload=self.rpc('resources/read',{'uri':'athena://collective/v12'})['result']['contents'][0]['text']
        self.assertIn('COLLECTIVE_RUNTIME_V12',payload)
        self.assertIn('Y1 authority',payload)
        self.assertIn('bounded PAG candidate',payload)

    def test_v12_model_outputs_cannot_mutate_y1_or_jspace(self):
        claim=self.tool('athena_claim_register',{'claim_id':'Y.V12','source_ref':'test://v12'})
        before_claim=self.tool('athena_claim_state',{'claim_id':'Y.V12'})
        before_edges=len(self.server.store.rows('SELECT * FROM edges'))
        rows=[]
        for i in range(60):rows.append({'X':i/60,'Y':((i*11)%59)/59,'Z':((i*17)%61)/61})
        self.tool('athena_pag_candidate_discover',{'samples':rows,'variables':['X','Y','Z'],'max_conditioning':1})
        self.tool('athena_chance_resource_select',{'candidates':[{'id':'A','value':1,'resources':{'tokens':{'mean':1,'std':.1}}}],'budgets':{'tokens':2}})
        after_edges=len(self.server.store.rows('SELECT * FROM edges'))
        after_claim=self.tool('athena_claim_state',{'claim_id':'Y.V12'})
        self.assertEqual(before_edges,after_edges)
        self.assertEqual(before_claim['stage'],after_claim['stage'])
        self.assertEqual(before_claim['claim_id'],after_claim['claim_id'])

    def test_surface_contract_requires_v12(self):
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        self.assertEqual(audit['groups']['collective_v12']['status'],'PASS',audit)
        self.assertTrue(audit['promotion_ready_locally'])


if __name__=='__main__':unittest.main()
