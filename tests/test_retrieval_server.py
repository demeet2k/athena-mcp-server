import json
import tempfile
import unittest

from athena_mcp.retrieval_server import RetrievalServer
from athena_mcp.orchestration_equivalence import REQUIRED_SAMENESS

SAME={name:True for name in REQUIRED_SAMENESS}

def meas(rel=1):
    return {
        'relevance':{'value':rel,'method':'semantic','witness_ref':'m:r'},
        'source_authority':{'value':1,'method':'provenance','witness_ref':'m:a'},
        'cross_value':{'value':1,'method':'cross','witness_ref':'m:c'},
        'decision_relevance':{'value':1,'method':'decision','witness_ref':'m:d'},
    }

def cand(ident,rel=1,roles=None,facets=None):
    return {'id':ident,'source_ref':f'source://{ident}','measurements':meas(rel),'source_time':900,'cost':1,'roles':roles or [],'facets':facets or []}

QUERY={'as_of':1000,'freshness_half_life':100,'budget':2,'max_items':2}

class RetrievalServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=RetrievalServer(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});self.assertFalse(r['result'].get('isError'),r);return r['result']['structuredContent']

    def test_retrieval_surface_composes_with_all_prior_organs(self):
        names=[x['name'] for x in self.rpc('tools/list')['result']['tools']]
        for required in ['athena_retrieval_compile','athena_retrieval_replay','athena_extraction_plan','athena_equivalence_observe','athena_claim_register','athena_branch_observe','athena_orchestrate','athena_apply_transform','athena_finalize_output']:
            self.assertIn(required,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for uri in ['athena://retrieval','athena://extraction','athena://equivalence','athena://authority','athena://branches','athena://transforms','athena://emissions']:
            self.assertIn(uri,uris)

    def test_equivalence_context_is_snapshotted_before_retrieval(self):
        self.tool('athena_equivalence_observe',{'context_id':'RAG.EQ','left_id':'a','right_id':'b','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq:ab'},'same':SAME})
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://1','query':QUERY,'candidates':[cand('a',0.2),cand('b',1.0),cand('c',0.8)],'equivalence_context':'RAG.EQ','actor':'A1','task':'retrieve'})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('RAGRUN.'))
        self.assertIn('a',run['equivalence']['suppressed']);self.assertIn('b',run['selected_ids'])
        stored=self.tool('athena_retrieval_get',{'run_id':run['run_id']});self.assertIsNotNone(stored['input']['eq_snapshot'])
        replay=self.tool('athena_retrieval_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'])

    def test_later_equivalence_conflict_does_not_rewrite_old_ragrun(self):
        self.tool('athena_equivalence_observe',{'context_id':'RAG.FROZEN','left_id':'a','right_id':'b','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq:ab'},'same':SAME})
        old=self.tool('athena_retrieval_compile',{'query_ref':'q://frozen','query':QUERY,'candidates':[cand('a',0.2),cand('b',1.0)],'equivalence_context':'RAG.FROZEN'})
        self.assertEqual(old['equivalence']['suppressed'],['a'])
        self.tool('athena_equivalence_observe',{'context_id':'RAG.FROZEN','left_id':'a','right_id':'b','relation':'DISTINCT','witness':{'verified':True,'ref':'d:ab'},'different':['lineage']})
        current=self.tool('athena_retrieval_compile',{'query_ref':'q://current','query':QUERY,'candidates':[cand('a',0.2),cand('b',1.0)],'equivalence_context':'RAG.FROZEN','persist':False})
        self.assertEqual(current['equivalence']['suppressed'],[]);self.assertEqual(len(current['equivalence']['pair_conflicts']),1)
        replay=self.tool('athena_retrieval_replay',{'run_id':old['run_id']});self.assertTrue(replay['match']);self.assertEqual(replay['stored_equivalence']['suppressed'],['a']);self.assertEqual(replay['recomputed_equivalence']['suppressed'],['a'])

    def test_required_contradiction_role_changes_selection_under_one_item_budget(self):
        q={**QUERY,'budget':1,'max_items':1,'required_roles':['contradiction'],'role_coverage_weight':3}
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://contra','query':q,'candidates':[cand('direct',1,['direct']),cand('contra',0.2,['contradiction'])],'persist':False})
        self.assertEqual(run['selected_ids'],['contra']);self.assertEqual(run['coverage']['missing_roles'],[])

    def test_unknown_retrieval_measurement_surfaces_plan_not_zero_score(self):
        bad=cand('bad');del bad['measurements']['cross_value']
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://unknown','query':QUERY,'candidates':[bad,cand('known',0.1)],'persist':False})
        self.assertEqual(run['selected_ids'],['known']);self.assertEqual(run['measurement_plan'][0]['candidate'],'bad')

    def test_retrieval_resource_benchmark_and_prompt(self):
        self.tool('athena_retrieval_compile',{'query_ref':'q://r','query':QUERY,'candidates':[cand('a')]})
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://retrieval'})['result']['contents'][0]['text'])
        self.assertEqual(payload['benchmark']['retrieval_runs'],1);self.assertEqual(payload['law']['version'],'RAG.1')
        bench=self.tool('athena_benchmark',{});self.assertEqual(bench['retrieval_runs'],1);self.assertIn('extraction_runs',bench);self.assertIn('authority_claims',bench)
        prompt=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})['result']['messages'][0]['content']['text']
        self.assertIn('16 RETRIEVAL/RAG.1:',prompt);self.assertIn('source_authority is retrieval provenance quality, not Y claim authority',prompt)

if __name__=='__main__':unittest.main()
