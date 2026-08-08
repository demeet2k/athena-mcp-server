import json
import tempfile
import unittest

from athena_mcp.gap_server import GapServer

POLICY={'traversable_relations':['derive','support','bridge','implement'],'max_depth':4,'require_witness':True,'allowed_statuses':['ACTIVE']}

def edge(eid,src,dst,relation='derive',verified=True):return {'id':eid,'src':src,'dst':dst,'relation':relation,'verified':verified,'witness_ref':f'w:{eid}','status':'ACTIVE'}
def target(ident,node,sev=1,lev=1,ig=1,cost=1):return {'id':ident,'node':node,'severity':sev,'leverage':lev,'information_gain':ig,'cost':cost}

class GapServerTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=GapServer(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});self.assertFalse(r['result'].get('isError'),r);return r['result']['structuredContent']

    def test_gap_surface_preserves_all_prior_organs(self):
        names=[x['name'] for x in self.rpc('tools/list')['result']['tools']]
        for required in ['athena_gap_compile','athena_gap_replay','athena_hug_register','athena_retrieval_compile','athena_extraction_plan','athena_equivalence_snapshot','athena_claim_register','athena_branch_observe','athena_orchestrate','athena_apply_transform','athena_finalize_output']:
            self.assertIn(required,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for uri in ['athena://gap','athena://hug','athena://retrieval','athena://extraction','athena://equivalence','athena://authority','athena://branches','athena://transforms','athena://emissions']:
            self.assertIn(uri,uris)

    def test_explicit_SHBC_groups_close_targets_and_surface_residual(self):
        sources={'S':['s0'],'H':['h0'],'B':['b0'],'C':['c0']}
        edges=[edge('s1','s0','x'),edge('h1','h0','y','support'),edge('b1','b0','z','bridge'),edge('c1','c0','w','implement')]
        run=self.tool('athena_gap_compile',{'task_ref':'task://shbc','sources':sources,'edges':edges,'targets':[target('tx','x'),target('ty','y'),target('tz','z'),target('tw','w'),target('missing','m',2,3,4,2)],'policy':POLICY})
        self.assertEqual(run['covered_target_ids'],['tx','ty','tz','tw']);self.assertEqual(run['gap_target_ids'],['missing']);self.assertEqual(run['grow']['id'],'missing');self.assertEqual(run['grow']['residual_score']['value'],12)
        self.assertEqual(run['closure_paths']['z']['origin_groups'],['B']);self.assertTrue(run['run_id'].startswith('GAPRUN.'))

    def test_unverified_graph_edge_is_rejected_and_replay_freezes_decision(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://frozen','sources':{'S':['a']},'edges':[edge('ab','a','b',verified=False)],'targets':[target('b','b')],'policy':POLICY})
        self.assertEqual(run['gap_target_ids'],['b']);self.assertEqual(run['rejected_edges'][0]['id'],'ab');self.assertIn('edge_not_verified',run['rejected_edges'][0]['defects'])
        replay=self.tool('athena_gap_replay',{'run_id':run['run_id']});self.assertTrue(replay['match']);self.assertEqual(replay['stored_gap'],['b']);self.assertEqual(replay['recomputed_gap'],['b'])

    def test_reachability_is_not_presented_as_logical_proof(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://boundary','sources':{'S':['a']},'edges':[edge('ab','a','b')],'targets':[target('b','b')],'policy':POLICY,'persist':False})
        self.assertEqual(run['closure_kind'],'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF');self.assertIn('logical/causal entailment',run['epistemic_boundary'])

    def test_unknown_residual_metrics_route_to_measurement(self):
        t={'id':'u','node':'u','severity':1,'leverage':2,'cost':1}
        run=self.tool('athena_gap_compile',{'task_ref':'task://unknown','sources':{'S':['a']},'edges':[],'targets':[t],'policy':POLICY,'persist':False})
        self.assertIsNone(run['grow']);self.assertEqual(run['measurement_plan'][0]['target'],'u');self.assertEqual(run['gap'][0]['residual_score']['status'],'UNKNOWN')

    def test_resource_benchmark_and_prompt(self):
        self.tool('athena_gap_compile',{'task_ref':'task://r','sources':{'S':['a']},'edges':[],'targets':[target('b','b')],'policy':POLICY})
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://gap'})['result']['contents'][0]['text']);self.assertEqual(payload['benchmark']['gap_runs'],1);self.assertIn('reachability != logical/causal proof',payload['law']['boundary'])
        bench=self.tool('athena_benchmark',{});self.assertEqual(bench['gap_runs'],1);self.assertIn('hug_implementations',bench);self.assertIn('retrieval_runs',bench)
        prompt=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})['result']['messages'][0]['content']['text'];self.assertIn('18 GAP/CLOSURE:',prompt);self.assertIn('Do not call reachability proof',prompt)

if __name__=='__main__':unittest.main()
